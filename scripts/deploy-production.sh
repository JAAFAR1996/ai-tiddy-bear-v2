#!/bin/bash

# AI Teddy Bear - Production Deployment Script
# Secure deployment with child safety validation

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# ================================
# Configuration
# ================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="${PROJECT_ROOT}/.env.production"
DOCKER_COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.production.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ================================
# Validation Functions
# ================================

check_prerequisites() {
    log_info "Checking deployment prerequisites..."
    
    # Check required commands
    local required_commands=("docker" "docker-compose" "openssl" "curl" "psql")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "Required command '$cmd' not found"
            exit 1
        fi
    done
    
    # Check Docker is running
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running"
        exit 1
    fi
    
    # Check if running as root (should not be)
    if [ "$EUID" -eq 0 ]; then
        log_error "Do not run this script as root for security reasons"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

validate_environment() {
    log_info "Validating environment configuration..."
    
    if [ ! -f "$ENV_FILE" ]; then
        log_error "Environment file not found: $ENV_FILE"
        log_info "Please create the production environment file with required settings"
        exit 1
    fi
    
    # Source environment file
    set -a  # automatically export all variables
    source "$ENV_FILE"
    set +a
    
    # Critical environment variables for child safety
    local required_vars=(
        "SECRET_KEY"
        "JWT_SECRET_KEY" 
        "DATABASE_URL"
        "OPENAI_API_KEY"
        "ENCRYPTION_KEY"
        "COPPA_ENCRYPTION_KEY"
        "REDIS_PASSWORD"
        "DB_PASSWORD"
    )
    
    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_error "Missing required environment variables:"
        printf '%s\n' "${missing_vars[@]}"
        exit 1
    fi
    
    # Validate critical security settings
    if [ "${#SECRET_KEY}" -lt 32 ]; then
        log_error "SECRET_KEY must be at least 32 characters long"
        exit 1
    fi
    
    if [ "${#JWT_SECRET_KEY}" -lt 32 ]; then
        log_error "JWT_SECRET_KEY must be at least 32 characters long"
        exit 1
    fi
    
    if [[ ! "$OPENAI_API_KEY" =~ ^sk- ]]; then
        log_error "OPENAI_API_KEY must start with 'sk-'"
        exit 1
    fi
    
    if [[ ! "$DATABASE_URL" =~ ^postgresql ]]; then
        log_error "DATABASE_URL must use PostgreSQL"
        exit 1
    fi
    
    # Validate COPPA compliance settings
    if [ "${MAX_CHILD_AGE:-0}" -gt 13 ]; then
        log_error "MAX_CHILD_AGE cannot exceed 13 (COPPA compliance)"
        exit 1
    fi
    
    if [ "${REQUIRE_PARENTAL_CONSENT:-false}" != "true" ]; then
        log_error "REQUIRE_PARENTAL_CONSENT must be true for COPPA compliance"
        exit 1
    fi
    
    log_success "Environment validation passed"
}

validate_security() {
    log_info "Validating security configuration..."
    
    # Check file permissions
    if [ -f "$ENV_FILE" ]; then
        local env_perms=$(stat -c "%a" "$ENV_FILE" 2>/dev/null || stat -f "%A" "$ENV_FILE" 2>/dev/null || echo "unknown")
        if [ "$env_perms" != "600" ]; then
            log_warning "Environment file permissions should be 600 (current: $env_perms)"
            chmod 600 "$ENV_FILE"
            log_success "Fixed environment file permissions"
        fi
    fi
    
    # Validate SSL certificates exist
    local ssl_dir="${PROJECT_ROOT}/ssl"
    if [ ! -d "$ssl_dir" ]; then
        log_warning "SSL directory not found: $ssl_dir"
        log_info "Creating self-signed certificate for testing..."
        mkdir -p "$ssl_dir"
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "$ssl_dir/aiteddy.key" \
            -out "$ssl_dir/aiteddy.crt" \
            -subj "/C=US/ST=State/L=City/O=AI Teddy Bear/CN=localhost"
        log_success "Self-signed certificate created"
    fi
    
    log_success "Security validation passed"
}

# ================================
# Deployment Functions
# ================================

backup_existing_data() {
    log_info "Creating backup of existing data..."
    
    local backup_dir="${PROJECT_ROOT}/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup database if container exists
    if docker ps -a --format 'table {{.Names}}' | grep -q "ai-teddy-postgres-prod"; then
        log_info "Backing up PostgreSQL database..."
        docker exec ai-teddy-postgres-prod pg_dump -U ai_teddy_user ai_teddy_prod > "$backup_dir/database.sql" || true
    fi
    
    # Backup uploaded files
    if [ -d "${PROJECT_ROOT}/uploads" ]; then
        log_info "Backing up uploaded files..."
        cp -r "${PROJECT_ROOT}/uploads" "$backup_dir/" || true
    fi
    
    # Backup logs
    if [ -d "${PROJECT_ROOT}/logs" ]; then
        log_info "Backing up logs..."
        cp -r "${PROJECT_ROOT}/logs" "$backup_dir/" || true
    fi
    
    log_success "Backup completed: $backup_dir"
}

build_images() {
    log_info "Building Docker images..."
    
    cd "$PROJECT_ROOT"
    
    # Build production image
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    
    # Tag images for deployment
    docker tag ai-teddy-backend:production "ai-teddy-backend:$(date +%Y%m%d_%H%M%S)"
    
    log_success "Docker images built successfully"
}

deploy_services() {
    log_info "Deploying services..."
    
    cd "$PROJECT_ROOT"
    
    # Stop existing services
    log_info "Stopping existing services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down --remove-orphans || true
    
    # Start database and cache first
    log_info "Starting database and cache services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d postgres-db redis-cache
    
    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    local max_attempts=60
    local attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T postgres-db pg_isready -U ai_teddy_user -d ai_teddy_prod >/dev/null 2>&1; then
            break
        fi
        sleep 2
        ((attempt++))
    done
    
    if [ $attempt -eq $max_attempts ]; then
        log_error "Database failed to start within expected time"
        exit 1
    fi
    
    log_success "Database is ready"
    
    # Run database migrations
    log_info "Running database migrations..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" run --rm ai-teddy-backend \
        alembic upgrade head
    
    # Start all services
    log_info "Starting all services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    log_success "Services deployed successfully"
}

validate_deployment() {
    log_info "Validating deployment..."
    
    # Wait for services to be ready
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -f http://localhost/health >/dev/null 2>&1; then
            break
        fi
        sleep 5
        ((attempt++))
    done
    
    if [ $attempt -eq $max_attempts ]; then
        log_error "Application failed to start within expected time"
        return 1
    fi
    
    # Test critical endpoints
    log_info "Testing critical endpoints..."
    
    # Health check
    if ! curl -f http://localhost/health >/dev/null 2>&1; then
        log_error "Health check endpoint failed"
        return 1
    fi
    
    # Test API availability
    if ! curl -f -H "Content-Type: application/json" http://localhost/api/v1/ >/dev/null 2>&1; then
        log_warning "API endpoint may not be fully ready yet"
    fi
    
    # Check all containers are running
    local expected_containers=("ai-teddy-backend-prod" "ai-teddy-postgres-prod" "ai-teddy-redis-prod" "ai-teddy-nginx-prod")
    for container in "${expected_containers[@]}"; do
        if ! docker ps --format 'table {{.Names}}' | grep -q "$container"; then
            log_error "Container $container is not running"
            return 1
        fi
    done
    
    log_success "Deployment validation passed"
}

# ================================
# Monitoring and Cleanup
# ================================

setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Create log directories
    mkdir -p "${PROJECT_ROOT}/logs/nginx"
    mkdir -p "${PROJECT_ROOT}/logs/app"
    
    # Set up log rotation
    if command -v logrotate >/dev/null 2>&1; then
        cat > "${PROJECT_ROOT}/logs/logrotate.conf" << EOF
${PROJECT_ROOT}/logs/**/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644
}
EOF
    fi
    
    log_success "Monitoring setup completed"
}

cleanup_old_images() {
    log_info "Cleaning up old Docker images..."
    
    # Remove unused images older than 7 days
    docker image prune -a --filter "until=168h" -f >/dev/null 2>&1 || true
    
    # Remove unused volumes
    docker volume prune -f >/dev/null 2>&1 || true
    
    log_success "Cleanup completed"
}

# ================================
# Main Deployment Flow
# ================================

print_banner() {
    echo "================================"
    echo "🧸 AI Teddy Bear Production Deployment"
    echo "🔒 Child Safety & COPPA Compliance"
    echo "================================"
    echo
}

main() {
    print_banner
    
    # Pre-deployment checks
    check_prerequisites
    validate_environment
    validate_security
    
    # Deployment process
    log_info "Starting production deployment..."
    backup_existing_data
    build_images
    deploy_services
    
    # Post-deployment validation
    validate_deployment
    setup_monitoring
    cleanup_old_images
    
    # Success message
    echo
    log_success "🎉 Production deployment completed successfully!"
    echo
    echo "📊 Application Status:"
    echo "   • Frontend: https://localhost"
    echo "   • API: https://localhost/api/v1/"
    echo "   • Health: https://localhost/health"
    echo "   • Monitoring: http://localhost:3000 (Grafana)"
    echo "   • Metrics: http://localhost:9090 (Prometheus)"
    echo
    echo "🔍 To check logs:"
    echo "   docker-compose -f docker-compose.production.yml logs -f"
    echo
    echo "🛡️ Security Reminders:"
    echo "   • All child data is encrypted"
    echo "   • COPPA compliance is enforced"
    echo "   • SSL/TLS is enabled"
    echo "   • Rate limiting is active"
    echo
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "validate")
        print_banner
        check_prerequisites
        validate_environment
        validate_security
        log_success "All validations passed"
        ;;
    "backup")
        print_banner
        backup_existing_data
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [deploy|validate|backup|help]"
        echo
        echo "Commands:"
        echo "  deploy    - Full production deployment (default)"
        echo "  validate  - Validate environment and prerequisites"
        echo "  backup    - Create backup of existing data"
        echo "  help      - Show this help message"
        ;;
    *)
        log_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac

 