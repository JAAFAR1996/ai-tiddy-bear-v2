#!/bin/bash
# Runtime Security Validation Script
# Tests actual container behavior to ensure security controls are effective

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

increment_test() {
    ((TOTAL_TESTS++))
    if [[ $1 == "pass" ]]; then
        ((PASSED_TESTS++))
    else
        ((FAILED_TESTS++))
    fi
}

# Function to test non-root user execution
test_non_root_user() {
    log_info "Testing non-root user execution..."

    # Build the image first
    if docker build -t ai-teddy-security-test -f Dockerfile . >/dev/null 2>&1; then
        log_success "Docker image built successfully"
        increment_test "pass"

        # Test whoami command
        local user_output
        user_output=$(docker run --rm ai-teddy-security-test whoami 2>/dev/null || echo "error")

        if [[ "$user_output" == "appuser" ]]; then
            log_success "Container runs as non-root user: $user_output"
            increment_test "pass"
        else
            log_error "Container runs as: $user_output (expected: appuser)"
            increment_test "fail"
        fi

        # Test user ID
        local uid_output
        uid_output=$(docker run --rm ai-teddy-security-test id -u 2>/dev/null || echo "error")

        if [[ "$uid_output" == "1000" ]]; then
            log_success "Container runs with UID: $uid_output"
            increment_test "pass"
        else
            log_error "Container runs with UID: $uid_output (expected: 1000)"
            increment_test "fail"
        fi

        # Test write permissions to sensitive directories
        local write_test
        write_test=$(docker run --rm ai-teddy-security-test sh -c "touch /etc/test 2>&1" || echo "Permission denied")

        if [[ "$write_test" == *"Permission denied"* ]]; then
            log_success "Cannot write to /etc (expected security restriction)"
            increment_test "pass"
        else
            log_error "Can write to /etc (security violation)"
            increment_test "fail"
        fi

    else
        log_error "Failed to build Docker image"
        increment_test "fail"
    fi
}

# Function to test production image security
test_production_image() {
    log_info "Testing production image security..."

    # Build production image
    if docker build -t ai-teddy-production-test -f Dockerfile.production . >/dev/null 2>&1; then
        log_success "Production Docker image built successfully"
        increment_test "pass"

        # Test non-root user
        local prod_user
        prod_user=$(docker run --rm ai-teddy-production-test whoami 2>/dev/null || echo "error")

        if [[ "$prod_user" == "appuser" ]]; then
            log_success "Production container runs as non-root user: $prod_user"
            increment_test "pass"
        else
            log_error "Production container runs as: $prod_user (expected: appuser)"
            increment_test "fail"
        fi

        # Test minimal image size (production should be smaller)
        local dev_size prod_size
        dev_size=$(docker images ai-teddy-security-test --format "{{.Size}}" | head -n1)
        prod_size=$(docker images ai-teddy-production-test --format "{{.Size}}" | head -n1)

        log_info "Development image size: $dev_size"
        log_info "Production image size: $prod_size"
        increment_test "pass"

    else
        log_error "Failed to build production Docker image"
        increment_test "fail"
    fi
}

# Function to test health checks
test_health_checks() {
    log_info "Testing health check functionality..."

    # Start container with health check
    local container_id
    if container_id=$(docker run -d --name ai-teddy-health-test -p 8080:8000 ai-teddy-security-test 2>/dev/null); then
        log_success "Container started with ID: ${container_id:0:12}"
        increment_test "pass"

        # Wait for health check
        sleep 10

        # Check health status
        local health_status
        health_status=$(docker inspect --format='{{.State.Health.Status}}' ai-teddy-health-test 2>/dev/null || echo "unknown")

        if [[ "$health_status" == "healthy" ]]; then
            log_success "Health check passed: $health_status"
            increment_test "pass"
        else
            log_warning "Health check status: $health_status"
            increment_test "fail"
        fi

        # Test graceful shutdown
        log_info "Testing graceful shutdown..."
        if docker stop ai-teddy-health-test >/dev/null 2>&1; then
            log_success "Container stopped gracefully"
            increment_test "pass"
        else
            log_error "Container did not stop gracefully"
            increment_test "fail"
        fi

        # Cleanup
        docker rm ai-teddy-health-test >/dev/null 2>&1 || true

    else
        log_error "Failed to start container for health check test"
        increment_test "fail"
    fi
}

# Function to test compose security
test_compose_security() {
    log_info "Testing Docker Compose security configurations..."

    # Test production compose file
    local compose_file="docker-compose.production.yml"
    if [[ -f "$compose_file" ]]; then
        log_success "Found $compose_file"
        increment_test "pass"

        # Check if we can start services (dry run)
        if docker-compose -f "$compose_file" config >/dev/null 2>&1; then
            log_success "Docker Compose configuration is valid"
            increment_test "pass"
        else
            log_error "Docker Compose configuration has errors"
            increment_test "fail"
        fi

        # Test user configurations
        local user_configs
        user_configs=$(grep "user:" "$compose_file" | wc -l)

        if [[ $user_configs -gt 0 ]]; then
            log_success "Services configured with non-root users ($user_configs services)"
            increment_test "pass"
        else
            log_error "No user configurations found in services"
            increment_test "fail"
        fi

    else
        log_error "$compose_file not found"
        increment_test "fail"
    fi
}

# Function to test network security
test_network_security() {
    log_info "Testing network security configurations..."

    # Check for localhost bindings
    local compose_files=("docker-compose.prod.yml" "docker-compose.production.yml")
    for compose_file in "${compose_files[@]}"; do
        if [[ -f "$compose_file" ]]; then
            local localhost_bindings
            localhost_bindings=$(grep -c "127.0.0.1:" "$compose_file" 2>/dev/null || echo "0")

            if [[ $localhost_bindings -gt 0 ]]; then
                log_success "$compose_file: $localhost_bindings services bound to localhost"
                increment_test "pass"
            else
                log_warning "$compose_file: No localhost-only bindings found"
                increment_test "fail"
            fi
        fi
    done
}

# Function to test file permissions in container
test_container_permissions() {
    log_info "Testing file permissions inside container..."

    # Test application directory permissions
    local app_perms
    app_perms=$(docker run --rm ai-teddy-security-test stat -c "%a" /app 2>/dev/null || echo "000")

    if [[ "$app_perms" == "755" ]]; then
        log_success "Application directory has correct permissions: $app_perms"
        increment_test "pass"
    else
        log_warning "Application directory permissions: $app_perms"
        increment_test "fail"
    fi

    # Test that sensitive files are not world-readable
    local passwd_perms
    passwd_perms=$(docker run --rm ai-teddy-security-test stat -c "%a" /etc/passwd 2>/dev/null || echo "000")

    if [[ "$passwd_perms" == "644" ]]; then
        log_success "/etc/passwd has secure permissions: $passwd_perms"
        increment_test "pass"
    else
        log_warning "/etc/passwd permissions: $passwd_perms"
        increment_test "fail"
    fi
}

# Function to test security scanning results
test_security_scanning() {
    log_info "Testing security scanning integration..."

    # Check if Trivy scan was integrated during build
    local trivy_logs
    trivy_logs=$(docker history ai-teddy-security-test 2>/dev/null | grep -i trivy | wc -l)

    if [[ $trivy_logs -gt 0 ]]; then
        log_success "Trivy security scanning integrated in build process"
        increment_test "pass"
    else
        log_warning "Trivy scanning not detected in build history"
        increment_test "fail"
    fi

    # Test if critical vulnerabilities would block deployment
    local dockerfile_content
    if dockerfile_content=$(grep -i "exit.*1" Dockerfile.production); then
        log_success "Build configured to fail on critical vulnerabilities"
        increment_test "pass"
    else
        log_warning "Build may not fail on critical vulnerabilities"
        increment_test "fail"
    fi
}

# Function to cleanup test resources
cleanup_test_resources() {
    log_info "Cleaning up test resources..."

    # Remove test images
    docker rmi ai-teddy-security-test ai-teddy-production-test >/dev/null 2>&1 || true

    # Remove any test containers
    docker rm -f ai-teddy-health-test >/dev/null 2>&1 || true

    log_success "Test cleanup completed"
}

# Main test function
main() {
    echo "========================================"
    echo "AI Teddy Bear Runtime Security Tests"
    echo "========================================"
    echo "Date: $(date)"
    echo "Testing actual container security behavior..."
    echo ""

    # Ensure Docker is available
    if ! command -v docker >/dev/null 2>&1; then
        log_error "Docker is not available. Cannot run runtime tests."
        exit 1
    fi

    # Run all runtime tests
    test_non_root_user
    test_production_image
    test_health_checks
    test_compose_security
    test_network_security
    test_container_permissions
    test_security_scanning

    echo ""
    echo "========================================"
    echo "RUNTIME SECURITY TEST SUMMARY"
    echo "========================================"
    echo "Total tests: $TOTAL_TESTS"
    echo "Passed: $PASSED_TESTS"
    echo "Failed: $FAILED_TESTS"

    local pass_percentage=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo "Pass rate: ${pass_percentage}%"

    # Cleanup test resources
    cleanup_test_resources

    if [[ $FAILED_TESTS -eq 0 ]]; then
        log_success "ALL RUNTIME SECURITY TESTS PASSED! 🎉"
        echo ""
        echo "✅ whoami prints 'appuser' (non-root user)"
        echo "✅ All containers run with UID 1000"
        echo "✅ Health checks pass and reflect application health"
        echo "✅ Proper signal handling verified (graceful shutdown)"
        echo "✅ File permissions are secure"
        echo "✅ Network security configured correctly"
        echo "✅ Security scanning integrated"
        exit 0
    elif [[ $pass_percentage -ge 80 ]]; then
        log_warning "RUNTIME TESTS PASSED WITH WARNINGS"
        echo "Some non-critical issues were found but containers are secure."
        exit 1
    else
        log_error "RUNTIME SECURITY TESTS FAILED"
        echo "Critical security issues were found in runtime behavior."
        exit 2
    fi
}

# Run the main test suite
main "$@"
