#!/bin/bash
# Security Validation Script for AI Teddy Bear Docker Infrastructure
# Validates all security controls are properly implemented

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
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

# Validation counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Function to increment check counters
increment_check() {
    ((TOTAL_CHECKS++))
    if [[ $1 == "pass" ]]; then
        ((PASSED_CHECKS++))
    else
        ((FAILED_CHECKS++))
    fi
}

# Function to validate Docker image security
validate_docker_images() {
    log_info "Validating Docker image security..."

    # Check if Dockerfiles exist
    local dockerfiles=("Dockerfile" "Dockerfile.production")
    for dockerfile in "${dockerfiles[@]}"; do
        if [[ -f "$dockerfile" ]]; then
            log_success "Found $dockerfile"
            increment_check "pass"

            # Check for pinned base images (no latest tags)
            if grep -q "FROM.*:latest" "$dockerfile"; then
                log_error "$dockerfile uses latest tag - security violation"
                increment_check "fail"
            else
                log_success "$dockerfile uses pinned base image tags"
                increment_check "pass"
            fi

            # Check for non-root user
            if grep -q "USER.*[^0]" "$dockerfile"; then
                log_success "$dockerfile runs as non-root user"
                increment_check "pass"
            else
                log_error "$dockerfile missing non-root user directive"
                increment_check "fail"
            fi

            # Check for security labels
            if grep -q "security\." "$dockerfile"; then
                log_success "$dockerfile has security labels"
                increment_check "pass"
            else
                log_warning "$dockerfile missing security labels"
                increment_check "fail"
            fi

            # Check for multi-stage builds
            if grep -c "FROM.*as.*" "$dockerfile" | grep -q "[2-9]"; then
                log_success "$dockerfile uses multi-stage builds"
                increment_check "pass"
            else
                log_warning "$dockerfile should use multi-stage builds"
                increment_check "fail"
            fi

        else
            log_error "$dockerfile not found"
            increment_check "fail"
        fi
    done
}

# Function to validate Docker Compose security
validate_docker_compose() {
    log_info "Validating Docker Compose security configurations..."

    local compose_files=("docker-compose.prod.yml" "docker-compose.production.yml")
    for compose_file in "${compose_files[@]}"; do
        if [[ -f "$compose_file" ]]; then
            log_success "Found $compose_file"
            increment_check "pass"

            # Check for non-root users
            if grep -q "user:.*[^:]0" "$compose_file"; then
                log_success "$compose_file configures non-root users"
                increment_check "pass"
            else
                log_error "$compose_file missing non-root user configurations"
                increment_check "fail"
            fi

            # Check for security options
            if grep -q "security_opt:" "$compose_file" && grep -q "no-new-privileges:true" "$compose_file"; then
                log_success "$compose_file has security options configured"
                increment_check "pass"
            else
                log_error "$compose_file missing security options"
                increment_check "fail"
            fi

            # Check for capability dropping
            if grep -q "cap_drop:" "$compose_file" && grep -q "ALL" "$compose_file"; then
                log_success "$compose_file drops all capabilities"
                increment_check "pass"
            else
                log_error "$compose_file missing capability restrictions"
                increment_check "fail"
            fi

            # Check for read-only containers
            if grep -q "read_only: true" "$compose_file"; then
                log_success "$compose_file configures read-only containers"
                increment_check "pass"
            else
                log_warning "$compose_file missing read-only container configurations"
                increment_check "fail"
            fi

            # Check for resource limits
            if grep -q "resources:" "$compose_file" && grep -q "limits:" "$compose_file"; then
                log_success "$compose_file has resource limits"
                increment_check "pass"
            else
                log_warning "$compose_file missing resource limits"
                increment_check "fail"
            fi

            # Check for localhost-only port bindings
            if grep -q "127.0.0.1:" "$compose_file"; then
                log_success "$compose_file binds sensitive ports to localhost only"
                increment_check "pass"
            else
                log_warning "$compose_file may expose ports to all interfaces"
                increment_check "fail"
            fi

        else
            log_error "$compose_file not found"
            increment_check "fail"
        fi
    done
}

# Function to validate entrypoint script security
validate_entrypoint_script() {
    log_info "Validating docker-entrypoint.sh security..."

    local entrypoint="docker-entrypoint.sh"
    if [[ -f "$entrypoint" ]]; then
        log_success "Found $entrypoint"
        increment_check "pass"

        # Check for set -euo pipefail
        if grep -q "set -euo pipefail" "$entrypoint"; then
            log_success "$entrypoint uses strict error handling"
            increment_check "pass"
        else
            log_error "$entrypoint missing strict error handling"
            increment_check "fail"
        fi

        # Check for signal handling
        if grep -q "trap.*cleanup" "$entrypoint" && grep -q "SIGTERM\|SIGINT" "$entrypoint"; then
            log_success "$entrypoint has proper signal handling"
            increment_check "pass"
        else
            log_error "$entrypoint missing signal handling"
            increment_check "fail"
        fi

        # Check for input validation
        if grep -q "validate_environment" "$entrypoint"; then
            log_success "$entrypoint validates environment variables"
            increment_check "pass"
        else
            log_error "$entrypoint missing environment validation"
            increment_check "fail"
        fi

        # Check for security checks
        if grep -q "security_checks" "$entrypoint"; then
            log_success "$entrypoint includes security checks"
            increment_check "pass"
        else
            log_error "$entrypoint missing security checks"
            increment_check "fail"
        fi

        # Check file permissions
        local perms
        perms=$(stat -c "%a" "$entrypoint" 2>/dev/null || echo "000")
        if [[ "$perms" == "755" ]]; then
            log_success "$entrypoint has correct permissions (755)"
            increment_check "pass"
        else
            log_error "$entrypoint has incorrect permissions ($perms)"
            increment_check "fail"
        fi

    else
        log_error "$entrypoint not found"
        increment_check "fail"
    fi
}

# Function to validate base image security
validate_base_images() {
    log_info "Validating base image security..."

    local dockerfiles=("Dockerfile" "Dockerfile.production")
    for dockerfile in "${dockerfiles[@]}"; do
        if [[ -f "$dockerfile" ]]; then
            # Extract base images
            local base_images
            base_images=$(grep "^FROM" "$dockerfile" | awk '{print $2}' | cut -d'@' -f1)

            for image in $base_images; do
                # Check if image has SHA256 digest
                if grep "FROM.*$image@sha256:" "$dockerfile" >/dev/null; then
                    log_success "Base image $image is pinned with SHA256 digest"
                    increment_check "pass"
                else
                    log_error "Base image $image is not pinned with SHA256 digest"
                    increment_check "fail"
                fi
            done
        fi
    done
}

# Function to validate security scanning integration
validate_security_scanning() {
    log_info "Validating security scanning integration..."

    local dockerfiles=("Dockerfile" "Dockerfile.production")
    for dockerfile in "${dockerfiles[@]}"; do
        if [[ -f "$dockerfile" ]]; then
            # Check for Trivy integration
            if grep -q "trivy" "$dockerfile"; then
                log_success "$dockerfile includes Trivy security scanning"
                increment_check "pass"
            else
                log_error "$dockerfile missing Trivy security scanning"
                increment_check "fail"
            fi

            # Check for security scanning stage
            if grep -q "security-scanner" "$dockerfile"; then
                log_success "$dockerfile has dedicated security scanning stage"
                increment_check "pass"
            else
                log_error "$dockerfile missing security scanning stage"
                increment_check "fail"
            fi
        fi
    done
}

# Function to validate file permissions
validate_file_permissions() {
    log_info "Validating file permissions..."

    # Check for world-writable files
    local world_writable
    world_writable=$(find . -type f -perm -o+w 2>/dev/null | grep -v ".git" | head -5)
    if [[ -z "$world_writable" ]]; then
        log_success "No world-writable files found"
        increment_check "pass"
    else
        log_error "World-writable files detected: $world_writable"
        increment_check "fail"
    fi

    # Check for executable scripts
    local scripts=("docker-entrypoint.sh" "scripts/validate_security.sh")
    for script in "${scripts[@]}"; do
        if [[ -f "$script" ]]; then
            local perms
            perms=$(stat -c "%a" "$script" 2>/dev/null || echo "000")
            if [[ "$perms" == "755" ]]; then
                log_success "$script has correct permissions (755)"
                increment_check "pass"
            else
                log_warning "$script has permissions: $perms"
                increment_check "fail"
            fi
        fi
    done
}

# Function to check for hardcoded secrets
check_hardcoded_secrets() {
    log_info "Checking for hardcoded secrets..."

    # Patterns that might indicate hardcoded secrets
    local secret_patterns=(
        "password.*=.*['\"][^'\"]*['\"]"
        "secret.*=.*['\"][^'\"]*['\"]"
        "key.*=.*['\"][^'\"]*['\"]"
        "token.*=.*['\"][^'\"]*['\"]"
        "api_key.*=.*['\"][^'\"]*['\"]"
    )

    local files_to_check=("Dockerfile" "Dockerfile.production" "docker-compose.prod.yml" "docker-compose.production.yml" "docker-entrypoint.sh")
    local secrets_found=false

    for file in "${files_to_check[@]}"; do
        if [[ -f "$file" ]]; then
            for pattern in "${secret_patterns[@]}"; do
                if grep -i -E "$pattern" "$file" | grep -v "{\$" | grep -v "example" | grep -v "#" >/dev/null; then
                    log_error "Potential hardcoded secret found in $file"
                    secrets_found=true
                fi
            done
        fi
    done

    if [[ "$secrets_found" == "false" ]]; then
        log_success "No hardcoded secrets detected"
        increment_check "pass"
    else
        increment_check "fail"
    fi
}

# Function to validate environment variable usage
validate_environment_variables() {
    log_info "Validating environment variable usage..."

    local compose_files=("docker-compose.prod.yml" "docker-compose.production.yml")
    for compose_file in "${compose_files[@]}"; do
        if [[ -f "$compose_file" ]]; then
            # Check that sensitive values use environment variables
            local sensitive_keys=("PASSWORD" "SECRET" "KEY" "TOKEN")
            local env_var_usage=true

            for key in "${sensitive_keys[@]}"; do
                if grep -i "$key" "$compose_file" | grep -v "{\$" | grep ":" >/dev/null; then
                    log_warning "$compose_file may have hardcoded sensitive values for $key"
                    env_var_usage=false
                fi
            done

            if [[ "$env_var_usage" == "true" ]]; then
                log_success "$compose_file uses environment variables for sensitive data"
                increment_check "pass"
            else
                increment_check "fail"
            fi
        fi
    done
}

# Function to run comprehensive security scan if tools are available
run_security_scan() {
    log_info "Running security scan if tools are available..."

    # Check if Trivy is available
    if command -v trivy >/dev/null 2>&1; then
        log_info "Running Trivy filesystem scan..."
        if trivy fs --exit-code 0 --severity HIGH,CRITICAL . >/dev/null 2>&1; then
            log_success "Trivy scan completed successfully"
            increment_check "pass"
        else
            log_warning "Trivy scan found vulnerabilities"
            increment_check "fail"
        fi
    else
        log_warning "Trivy not available for security scanning"
        increment_check "fail"
    fi

    # Check if hadolint is available for Dockerfile linting
    if command -v hadolint >/dev/null 2>&1; then
        local dockerfiles=("Dockerfile" "Dockerfile.production")
        for dockerfile in "${dockerfiles[@]}"; do
            if [[ -f "$dockerfile" ]]; then
                if hadolint "$dockerfile" >/dev/null 2>&1; then
                    log_success "Hadolint scan passed for $dockerfile"
                    increment_check "pass"
                else
                    log_warning "Hadolint found issues in $dockerfile"
                    increment_check "fail"
                fi
            fi
        done
    else
        log_warning "Hadolint not available for Dockerfile linting"
        increment_check "fail"
    fi
}

# Main validation function
main() {
    echo "========================================"
    echo "AI Teddy Bear Security Validation Report"
    echo "========================================"
    echo "Date: $(date)"
    echo "Validating Docker infrastructure security..."
    echo ""

    # Run all validation checks
    validate_docker_images
    validate_docker_compose
    validate_entrypoint_script
    validate_base_images
    validate_security_scanning
    validate_file_permissions
    check_hardcoded_secrets
    validate_environment_variables
    run_security_scan

    echo ""
    echo "========================================"
    echo "SECURITY VALIDATION SUMMARY"
    echo "========================================"
    echo "Total checks: $TOTAL_CHECKS"
    echo "Passed: $PASSED_CHECKS"
    echo "Failed: $FAILED_CHECKS"

    local pass_percentage=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
    echo "Pass rate: ${pass_percentage}%"

    if [[ $FAILED_CHECKS -eq 0 ]]; then
        log_success "ALL SECURITY CHECKS PASSED! 🎉"
        echo ""
        echo "✅ Container runs as non-root user"
        echo "✅ All base images are pinned to exact versions"
        echo "✅ Security scanning is integrated"
        echo "✅ Proper signal handling implemented"
        echo "✅ No hardcoded secrets detected"
        echo "✅ File permissions are secure"
        echo "✅ Security options are configured"
        exit 0
    elif [[ $pass_percentage -ge 80 ]]; then
        log_warning "SECURITY VALIDATION PASSED WITH WARNINGS"
        echo "Some non-critical security issues were found but overall security posture is good."
        exit 1
    else
        log_error "SECURITY VALIDATION FAILED"
        echo "Critical security issues were found that must be addressed."
        exit 2
    fi
}

# Run the main validation
main "$@"
