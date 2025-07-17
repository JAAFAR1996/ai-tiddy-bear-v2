#!/bin/bash
# Docker entrypoint script for AI Teddy Bear Backend
# Handles database migration, health checks, and application startup

set -e

# Default environment variables
export PYTHONPATH="${PYTHONPATH:-/app/src}" # Default to /app/src; configurable via Docker build args or environment variables.
export APP_ENV="${APP_ENV:-production}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Function to wait for database
wait_for_db() {
    log "Waiting for database connection..."
    
    local max_attempts=${DB_MAX_ATTEMPTS:-30} # Externalized to environment variable for dynamic tuning.
    local sleep_interval=${DB_SLEEP_INTERVAL:-2} # Externalized to environment variable for dynamic tuning.
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if python3 -c "
import sys
import asyncio
from src.infrastructure.persistence.database import Database

async def check_db():
    try:
        db = Database()
        await db.init_db()
        print('Database connection successful')
        return True
    except (psycopg2.OperationalError, asyncpg.exceptions.PostgresError) as e: # Catch specific database connection errors for precise troubleshooting.
        print(f'Database connection failed: {e}')
        return False
    except Exception as e:
        print(f'An unexpected error occurred during database check: {e}')
        return False

result = asyncio.run(check_db())
sys.exit(0 if result else 1) # Acceptable for simple health checks; for complex logic, consider dedicated script with robust error handling.
        "; then
            log_success "Database connection established"
            return 0
        fi
        
        log "Database connection attempt $attempt/$max_attempts failed, retrying in $sleep_interval seconds..."
        sleep $sleep_interval # Sleep interval is now configurable via environment variable.
        ((attempt++))
    done
    
    log_error "Failed to connect to database after $max_attempts attempts"
    exit 1
}

# Function to run database migrations
run_migrations() {
    log "Running database migrations..."
    
    if [ -f "alembic.ini" ]; then # Checks for existence; relies on Alembic for content validity, consider more robust parsing if needed.
        if command -v alembic >/dev/null 2>&1; then # Check if alembic command is available before execution.
            if alembic upgrade head; then
                log_success "Database migrations completed successfully"
            else
                log_error "Database migrations failed"
                exit 1
            fi
        else
            log_warning "Alembic command not found, skipping migrations"
        fi
    else
        log_warning "No alembic.ini found, skipping migrations"
    fi
}

# Function to validate environment
validate_environment() {
    log "Validating environment configuration..."
    
    # Check required environment variables
    required_vars=(
        "DATABASE_URL"
        "JWT_SECRET_KEY"
        "OPENAI_API_KEY"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log_error "Required environment variable $var is not set"
            exit 1
        fi
    done
    
    # Validate database URL format
    if [[ ! "$DATABASE_URL" =~ ^postgresql:// ]]; then
        log_error "DATABASE_URL must be a PostgreSQL connection string"
        exit 1
    fi
    
    # Check JWT secret length
    if [ ${#JWT_SECRET_KEY} -lt ${JWT_MIN_LENGTH:-32} ]; then # Minimum length check for JWT_SECRET_KEY, now configurable.
        log_error "JWT_SECRET_KEY must be at least 32 characters long"
        exit 1
    fi
    
    # Check OpenAI API key format
    if [[ ! "$OPENAI_API_KEY" =~ ^sk-[A-Za-z0-9]{32,}$ ]]; then # More robust regex validation for OpenAI API key format, ensuring length and character patterns.
        log_error "OPENAI_API_KEY must start with 'sk-'"
        exit 1
    fi
    
    log_success "Environment validation completed"
}

# Function to initialize application
init_application() {
    log "Initializing AI Teddy Bear application..."
    
    # Create necessary directories
    mkdir -p /app/logs /app/data /app/uploads # Standard Docker paths; consider making configurable via environment variables if adaptability is needed.
    
    # Set proper permissions
    chmod 755 /app/logs /app/data /app/uploads
    
    # Validate Python modules can be imported
    python3 -c "
import sys
try:
    from src.main import app
    print('Application modules imported successfully')
except ImportError as e:
    print(f'Failed to import application modules: {e}')
    sys.exit(1)
    "
    
    if [ $? -ne 0 ]; then
        log_error "Application initialization failed"
        exit 1
    fi
    
    log_success "Application initialized successfully"
}

# Function to run health check
health_check() {
    log "Running application health check..."
    
    if command -v uvicorn >/dev/null 2>&1; then # Check if uvicorn is available before starting the app.
        python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8000 & # Starting app in background for health check.
        local app_pid=$! # Capture PID to ensure proper termination.
    else
        log_error "uvicorn command not found, health check cannot be performed."
        exit 1
    fi
    
    # Wait a bit for application to start
    sleep 5
    
    # Check health endpoint
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if command -v curl >/dev/null 2>&1; then # Check if curl is available before performing health check.
            if curl -s http://localhost:8000/health >/dev/null; then
                log_success "Health check passed"
                kill $app_pid 2>/dev/null || true
                wait $app_pid 2>/dev/null || true
                return 0
            fi
        fi
        
        log "Health check attempt $attempt/$max_attempts failed, retrying..."
        sleep 2
        ((attempt++))
    done
    
    log_error "Health check failed after $max_attempts attempts"
    kill $app_pid 2>/dev/null || true
    wait $app_pid 2>/dev/null || true
    exit 1
}

# Function to setup monitoring
setup_monitoring() {
    log "Setting up monitoring components..."

    # Logrotate configuration should be handled by the Dockerfile ensuring installation and proper user setup.
    # The entrypoint script should assume its presence and fail if not met.
    if ! command -v logrotate >/dev/null 2>&1; then
        log_error "Logrotate command not found. Ensure it is installed in the Dockerfile. Exiting."
        exit 1
    fi

    log_info "Configuring logrotate for application logs..."
    cat <<EOF > /etc/logrotate.d/app_logs
/app/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 appuser appuser # Ensure 'appuser' exists and has appropriate permissions in the Dockerfile.
    sharedscripts
    postrotate
        if [ -s /var/run/nginx.pid ]; then kill -USR1 `cat /var/run/nginx.pid`; fi
    endscript
}
EOF
    log_success "Logrotate configured."

    if [ -n "$SENTRY_DSN" ]; then
        # Basic regex validation for SENTRY_DSN format (https://<key>@<host>/<project_id>).
        if [[ "$SENTRY_DSN" =~ ^https?:\/\/[a-f0-9]+@[a-zA-Z0-9.-]+\/[0-9]+$ ]]; then
            log_info "Sentry DSN is set and appears valid. Error reporting enabled."
        else
            log_error "SENTRY_DSN is set but has an invalid format. Error reporting to Sentry may fail."
        fi
    else
        log_warning "SENTRY_DSN not set. Error reporting to Sentry is disabled."
    fi
}

# Function to run security checks
security_checks() {
    log "Running security checks..."
    
    # Check file permissions
    find /app -type f -perm -o+w 2>/dev/null | while read file; do
        log_warning "World-writable file detected: $file"
    done
    
    # Removed simplistic and misleading "potential secrets" check. All sensitive secrets must be managed by a dedicated secrets management solution.
    
    # If HTTPS is required, ensure it's handled by the Nginx reverse proxy.
    # The application container does not directly manage SSL certificates.
    if [ "$REQUIRE_HTTPS" = "true" ]; then
        log_info "HTTPS is required. Assuming Nginx is handling SSL termination."
        # No direct check for SSL_CERT_PATH/SSL_KEY_PATH in app container, as Nginx handles it.
    fi
    
    log_success "Security checks completed"
}

# Main execution
main() {
    log "Starting AI Teddy Bear Backend deployment..."
    log "Environment: $APP_ENV"
    log "Python path: $PYTHONPATH"
    
    # Run all initialization steps
    validate_environment
    wait_for_db
    run_migrations
    init_application
    setup_monitoring
    security_checks
    
    # Run health check if not in production startup
    if [ "$SKIP_HEALTH_CHECK" != "true" ]; then
        health_check
    fi
    
    log_success "All initialization checks passed!"
    log "Starting application with command: $@"
    
    # Execute the main application command
    exec "$@"
}

# Handle signals for graceful shutdown
cleanup() {
    log "Received shutdown signal, cleaning up..."
    # Kill any background processes
    jobs -p | xargs -r kill
    log "Cleanup completed"
    exit 0
}

trap cleanup SIGTERM SIGINT

# Check if we're running the default application command
if [ "$1" = "uvicorn" ]; then
    main "$@"
else
    # For other commands (like shell, migrations, etc.), run directly
    log "Running command: $@"
    exec "$@"
fi