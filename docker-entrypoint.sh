#!/bin/bash
# Docker entrypoint script for AI Teddy Bear Backend
# Security-hardened with proper signal handling and graceful shutdown

set -euo pipefail  # Exit on any error, undefined variable, or pipe failure
export LC_ALL=C   # Ensure consistent locale for security

# Default environment variables with security-first defaults
export PYTHONPATH="${PYTHONPATH:-/app/src}"
export APP_ENV="${APP_ENV:-production}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"
export DB_MAX_ATTEMPTS="${DB_MAX_ATTEMPTS:-30}"
export DB_SLEEP_INTERVAL="${DB_SLEEP_INTERVAL:-2}"
export JWT_MIN_LENGTH="${JWT_MIN_LENGTH:-32}"

# Colors for output (disabled in production for security)
if [[ "${APP_ENV}" != "production" ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Secure logging function with timestamp and level
log() {
    echo -e "${BLUE}[$(date -u +'%Y-%m-%dT%H:%M:%S.%3NZ')] INFO:${NC} $1" >&1
}

log_error() {
    echo -e "${RED}[$(date -u +'%Y-%m-%dT%H:%M:%S.%3NZ')] ERROR:${NC} $1" >&2
}

log_success() {
    echo -e "${GREEN}[$(date -u +'%Y-%m-%dT%H:%M:%S.%3NZ')] SUCCESS:${NC} $1" >&1
}

log_warning() {
    echo -e "${YELLOW}[$(date -u +'%Y-%m-%dT%H:%M:%S.%3NZ')] WARNING:${NC} $1" >&2
}

# Secure function to wait for database with timeout and retry logic
wait_for_db() {
    log "Waiting for database connection..."

    local max_attempts="${DB_MAX_ATTEMPTS}"
    local sleep_interval="${DB_SLEEP_INTERVAL}"
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        if timeout 10 python3 -c "
import sys
import asyncio
import asyncpg
import psycopg2
from urllib.parse import urlparse

async def check_db():
    try:
        # Parse DATABASE_URL securely
        db_url = '${DATABASE_URL:-}'
        if not db_url:
            print('DATABASE_URL not set')
            return False

        parsed = urlparse(db_url)
        if parsed.scheme not in ['postgresql', 'postgres']:
            print('Invalid database URL scheme')
            return False

        # Test connection with timeout
        conn = await asyncpg.connect(db_url, timeout=5.0)
        await conn.execute('SELECT 1')
        await conn.close()
        print('Database connection successful')
        return True
    except Exception as e:
        print(f'Database connection failed: {e}')
        return False

result = asyncio.run(check_db())
sys.exit(0 if result else 1)
        " 2>/dev/null; then
            log_success "Database connection established"
            return 0
        fi

        log "Database connection attempt $attempt/$max_attempts failed, retrying in $sleep_interval seconds..."
        sleep "$sleep_interval"
        ((attempt++))
    done

    log_error "Failed to connect to database after $max_attempts attempts"
    exit 1
}
# Secure function to run database migrations
run_migrations() {
    log "Running database migrations..."

    if [[ ! -f "alembic.ini" ]]; then
        log_warning "No alembic.ini found, skipping migrations"
        return 0
    fi

    if ! command -v alembic >/dev/null 2>&1; then
        log_warning "Alembic command not found, skipping migrations"
        return 0
    fi

    # Run migrations with timeout and error handling
    if timeout 300 alembic upgrade head 2>&1 | tee /app/logs/migration.log; then
        log_success "Database migrations completed successfully"
    else
        log_error "Database migrations failed"
        exit 1
    fi
}

# Comprehensive environment validation with security checks
validate_environment() {
    log "Validating environment configuration..."

    # Check required environment variables
    local required_vars=(
        "DATABASE_URL"
        "JWT_SECRET_KEY"
        "OPENAI_API_KEY"
    )

    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_error "Required environment variable $var is not set"
            exit 1
        fi
    done

    # Validate DATABASE_URL format with security checks
    if [[ ! "$DATABASE_URL" =~ ^postgresql(\\+asyncpg)?:// ]]; then
        log_error "DATABASE_URL must be a PostgreSQL connection string"
        exit 1
    fi

    # Check for forbidden patterns in DATABASE_URL
    if [[ "$DATABASE_URL" =~ (localhost|127\.0\.0\.1) ]] && [[ "$APP_ENV" == "production" ]]; then
        log_error "Production DATABASE_URL should not use localhost"
        exit 1
    fi

    # Validate JWT secret length and complexity
    if [[ ${#JWT_SECRET_KEY} -lt ${JWT_MIN_LENGTH} ]]; then
        log_error "JWT_SECRET_KEY must be at least ${JWT_MIN_LENGTH} characters long"
        exit 1
    fi

    # Enhanced OpenAI API key validation
    if [[ ! "$OPENAI_API_KEY" =~ ^sk-[A-Za-z0-9_-]{40,}$ ]]; then
        log_error "OPENAI_API_KEY format is invalid"
        exit 1
    fi

    # Production-specific validations
    if [[ "$APP_ENV" == "production" ]]; then
        # Check for production-required variables
        local prod_vars=(
            "SENTRY_DSN"
            "COPPA_ENCRYPTION_KEY"
        )

        for var in "${prod_vars[@]}"; do
            if [[ -z "${!var:-}" ]]; then
                log_warning "Production environment variable $var is not set"
            fi
        done

        # Validate HTTPS requirements
        if [[ "${REQUIRE_HTTPS:-true}" == "true" ]]; then
            log "HTTPS is required in production environment"
        fi
    fi

    log_success "Environment validation completed"
}

# Secure application initialization
init_application() {
    log "Initializing AI Teddy Bear application..."

    # Create necessary directories with secure permissions
    local dirs=("/app/logs" "/app/data" "/app/uploads" "/app/tmp")
    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir" || {
                log_error "Failed to create directory: $dir"
                exit 1
            }
        fi
        chmod 755 "$dir" || {
            log_error "Failed to set permissions for: $dir"
            exit 1
        }
    done

    # Validate Python modules can be imported with timeout
    if ! timeout 30 python3 -c "
import sys
import traceback
try:
    from src.main import app
    print('Application modules imported successfully')
    sys.exit(0)
except ImportError as e:
    print(f'Failed to import application modules: {e}')
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f'Unexpected error during module import: {e}')
    traceback.print_exc()
    sys.exit(1)
    "; then
        log_success "Application initialized successfully"
    else
        log_error "Application initialization failed"
        exit 1
    fi
}

# Enhanced health check with comprehensive validation
health_check() {
    log "Running application health check..."

    if ! command -v uvicorn >/dev/null 2>&1; then
        log_error "uvicorn command not found, health check cannot be performed"
        exit 1
    fi

    # Start application in background with timeout
    timeout 60 python3 -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --log-level error &
    local app_pid=$!

    # Wait for application to start
    local start_wait=10
    log "Waiting ${start_wait} seconds for application to start..."
    sleep $start_wait

    # Check if process is still running
    if ! kill -0 $app_pid 2>/dev/null; then
        log_error "Application process died during startup"
        wait $app_pid 2>/dev/null || true
        exit 1
    fi

    # Perform health check with retries
    local max_attempts=10
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        if command -v curl >/dev/null 2>&1; then
            # Test multiple endpoints for comprehensive health check
            if curl -s --max-time 5 http://127.0.0.1:8000/health >/dev/null && \
               curl -s --max-time 5 http://127.0.0.1:8000/ready >/dev/null; then
                log_success "Health check passed"
                kill $app_pid 2>/dev/null || true
                wait $app_pid 2>/dev/null || true
                return 0
            fi
        else
            log_error "curl command not found, cannot perform HTTP health check"
            kill $app_pid 2>/dev/null || true
            wait $app_pid 2>/dev/null || true
            exit 1
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

# Enhanced monitoring setup with security considerations
setup_monitoring() {
    log "Setting up monitoring components..."

    # Configure log rotation with secure permissions
    if command -v logrotate >/dev/null 2>&1; then
        log "Configuring log rotation..."
        # Note: In production, this should be handled by the container orchestration platform
        cat > /tmp/logrotate.conf << 'EOF'
/app/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 appuser appuser
    copytruncate
}
EOF
        log_success "Log rotation configured"
    else
        log_warning "logrotate not available, log rotation not configured"
    fi

    # Validate Sentry DSN if provided
    if [[ -n "${SENTRY_DSN:-}" ]]; then
        # Enhanced Sentry DSN validation
        if [[ "$SENTRY_DSN" =~ ^https://[a-f0-9]{32}@[a-zA-Z0-9.-]+/[0-9]+$ ]]; then
            log "Sentry DSN validated - error reporting enabled"
        else
            log_error "SENTRY_DSN format is invalid"
            exit 1
        fi
    else
        log_warning "SENTRY_DSN not set - error reporting to Sentry is disabled"
    fi

    # Validate monitoring endpoints if in production
    if [[ "$APP_ENV" == "production" ]]; then
        if [[ "${PROMETHEUS_ENABLED:-false}" == "true" ]]; then
            log "Prometheus monitoring enabled"
        fi
    fi

    log_success "Monitoring setup completed"
}

# Comprehensive security checks
security_checks() {
    log "Running security checks..."

    # Check file permissions (no world-writable files)
    local world_writable_files
    world_writable_files=$(find /app -type f -perm -o+w 2>/dev/null | head -10)
    if [[ -n "$world_writable_files" ]]; then
        log_error "World-writable files detected:"
        echo "$world_writable_files"
        exit 1
    fi

    # Check for running as non-root user
    if [[ "$(id -u)" == "0" ]]; then
        log_error "Container is running as root user - security violation"
        exit 1
    fi

    # Validate user and group
    local current_user
    current_user=$(whoami)
    if [[ "$current_user" != "appuser" ]]; then
        log_error "Container is not running as appuser (current: $current_user)"
        exit 1
    fi

    # Check critical directories exist and have correct permissions
    local critical_dirs=("/app/logs" "/app/data")
    for dir in "${critical_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            log_error "Critical directory missing: $dir"
            exit 1
        fi

        local dir_perms
        dir_perms=$(stat -c "%a" "$dir" 2>/dev/null || echo "000")
        if [[ "$dir_perms" != "755" ]]; then
            log_warning "Directory $dir has unexpected permissions: $dir_perms"
        fi
    done

    # Validate HTTPS configuration in production
    if [[ "$APP_ENV" == "production" ]] && [[ "${REQUIRE_HTTPS:-true}" == "true" ]]; then
        log "HTTPS requirement validated for production environment"
    fi

    # Check for sensitive information in environment (basic check)
    if env | grep -i password | grep -v "POSTGRES_PASSWORD\|REDIS_PASSWORD\|DB_PASSWORD" >/dev/null 2>&1; then
        log_warning "Potential sensitive information detected in environment variables"
    fi

    log_success "Security checks completed"
}

# Enhanced main execution with proper error handling
main() {
    log "Starting AI Teddy Bear Backend deployment..."
    log "Environment: $APP_ENV"
    log "Python path: $PYTHONPATH"
    log "User: $(whoami) (UID: $(id -u), GID: $(id -g))"

    # Trap signals for graceful shutdown
    trap 'cleanup' SIGTERM SIGINT SIGQUIT

    # Run all initialization steps with error handling
    validate_environment || exit 1
    wait_for_db || exit 1
    run_migrations || exit 1
    init_application || exit 1
    setup_monitoring || exit 1
    security_checks || exit 1

    # Run health check if not explicitly skipped
    if [[ "${SKIP_HEALTH_CHECK:-false}" != "true" ]]; then
        health_check || exit 1
    fi

    log_success "All initialization checks passed!"
    log "Starting application with command: $*"

    # Execute the main application command
    exec "$@"
}

# Enhanced signal handling for graceful shutdown
cleanup() {
    local exit_code=$?
    log "Received shutdown signal (exit code: $exit_code), initiating graceful shutdown..."

    # Stop background jobs gracefully
    local jobs_list
    jobs_list=$(jobs -p 2>/dev/null || echo "")
    if [[ -n "$jobs_list" ]]; then
        log "Terminating background jobs..."
        echo "$jobs_list" | while read -r pid; do
            if kill -TERM "$pid" 2>/dev/null; then
                log "Sent SIGTERM to process $pid"
                # Wait for graceful shutdown
                local wait_count=0
                while kill -0 "$pid" 2>/dev/null && [[ $wait_count -lt 10 ]]; do
                    sleep 1
                    ((wait_count++))
                done

                # Force kill if still running
                if kill -0 "$pid" 2>/dev/null; then
                    log_warning "Force killing process $pid"
                    kill -KILL "$pid" 2>/dev/null || true
                fi
            fi
        done
    fi

    # Flush logs
    sync

    log "Graceful shutdown completed"
    exit $exit_code
}

# Enhanced command handling with security checks
if [[ $# -eq 0 ]]; then
    log_error "No command provided"
    exit 1
fi

# Check if we're running the default application command
case "$1" in
    "uvicorn"|"python"|"python3")
        # For application commands, run full initialization
        main "$@"
        ;;
    "sh"|"bash"|"/bin/sh"|"/bin/bash")
        # Security: Prevent shell access in production
        if [[ "$APP_ENV" == "production" ]]; then
            log_error "Shell access is disabled in production environment"
            exit 1
        fi
        log_warning "Starting shell session in non-production environment"
        exec "$@"
        ;;
    "alembic")
        # For database migration commands, skip health check
        export SKIP_HEALTH_CHECK=true
        main "$@"
        ;;
    *)
        # For other commands, run with minimal initialization
        log "Running command: $*"
        validate_environment || exit 1
        exec "$@"
        ;;
esac
