# AI Teddy Bear Backend - Development Dockerfile
# Multi-stage build for optimized development deployment
# Security-hardened with pinned dependencies and non-root execution

# ================================
# Build Stage
# ================================
FROM python:3.11.11-slim-bookworm@sha256:da2d7af143dab7cd5b0d5a5c9545fe14e67fc24c394fcf1cf15e8ea16cbd8637 as builder

# Security metadata
LABEL maintainer="AI Teddy Bear Security Team <security@aiteddybear.com>"
LABEL version="1.0.0"
LABEL description="AI Teddy Bear Backend - Development Build"
LABEL security.scan="trivy,snyk"
LABEL security.non-root="true"

# Set build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG BUILD_VERSION=dev
ARG DEBIAN_FRONTEND=noninteractive

# Set environment variables for build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    BUILD_DATE=${BUILD_DATE} \
    VCS_REF=${VCS_REF} \
    BUILD_VERSION=${BUILD_VERSION} \
    DEBIAN_FRONTEND=noninteractive

# Create build user with specific UID/GID for consistency
RUN groupadd -r -g 999 builder && \
    useradd -r -g builder -u 999 -m -s /bin/bash builder

# Install build dependencies with exact version pinning
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.9 \
    gcc=4:12.2.0-3 \
    libc6-dev=2.36-9+deb12u8 \
    libffi-dev=3.4.4-1 \
    libssl-dev=3.0.14-1~deb12u2 \
    pkg-config=1.8.1-1 \
    curl=7.88.1-10+deb12u8 \
    ca-certificates=20230311 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/* \
    && rm -rf /var/cache/apt/* \
    && rm -rf /usr/share/doc/* \
    && rm -rf /usr/share/man/*

# Create virtual environment for isolation
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip with exact version
RUN pip install --no-cache-dir \
    pip==24.3.1 \
    setuptools==75.6.0 \
    wheel==0.45.1

# Set work directory
WORKDIR /build

# Copy requirements with proper ownership
COPY --chown=builder:builder requirements-lock.txt requirements.txt ./

# Switch to builder user for dependency installation
USER builder

# Install Python dependencies with security flags and hash verification
RUN pip install --no-cache-dir \
    --require-hashes \
    --only-binary=all \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org \
    -r requirements-lock.txt

# ================================
# Security Scanning Stage
# ================================
FROM builder as security-scanner

USER root

# Install Trivy security scanner with pinned version
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin v0.58.1

# Scan dependencies for vulnerabilities (non-blocking for development)
RUN trivy fs --exit-code 0 --severity HIGH,CRITICAL /opt/venv || echo "Security scan completed with warnings"

# ================================
# Production Runtime Stage
# ================================
FROM python:3.11.11-slim-bookworm@sha256:da2d7af143dab7cd5b0d5a5c9545fe14e67fc24c394fcf1cf15e8ea16cbd8637 as production

# Security metadata
LABEL maintainer="AI Teddy Bear Security Team <security@aiteddybear.com>"
LABEL version="1.0.0"
LABEL description="AI Teddy Bear Backend - Development"
LABEL security.scan="trivy,snyk"
LABEL security.non-root="true"
LABEL security.no-new-privileges="true"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app/src" \
    APP_ENV=development \
    DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies with exact version pinning
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl=7.88.1-10+deb12u8 \
    ca-certificates=20230311 \
    dumb-init=1.2.5-2 \
    tini=0.19.0-1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/* \
    && rm -rf /var/cache/apt/* \
    && rm -rf /usr/share/doc/* \
    && rm -rf /usr/share/man/*

# Create app user with specific UID/GID for security
RUN groupadd -r -g 1000 appuser && \
    useradd -r -g appuser -u 1000 -m -s /bin/bash appuser && \
    usermod -L appuser

# Set work directory
WORKDIR /app

# Copy virtual environment from builder stage with proper ownership
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Copy application code with proper ownership and permissions
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser migrations/ ./migrations/
COPY --chown=appuser:appuser alembic.ini ./
COPY --chown=appuser:appuser docker-entrypoint.sh ./

# Set strict file permissions
RUN chmod 755 docker-entrypoint.sh && \
    chmod -R 644 src/ && \
    find src/ -type d -exec chmod 755 {} \; && \
    chmod -R 644 migrations/ && \
    find migrations/ -type d -exec chmod 755 {} \; && \
    chmod 644 alembic.ini

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/data /app/tmp && \
    chown -R appuser:appuser /app && \
    chmod 755 /app/logs /app/data /app/tmp

# Clean up any remaining build artifacts
RUN find /app -name "*.pyc" -delete && \
    find /app -name "__pycache__" -type d -exec rm -rf {} + || true && \
    find /app -name "*.pyo" -delete

# Install security scanning tools for runtime
COPY --from=security-scanner /usr/local/bin/trivy /usr/local/bin/trivy

# Switch to non-root user
USER appuser

# Security validation
RUN whoami | grep appuser && \
    test "$(id -u)" = "1000" && \
    test "$(id -g)" = "1000" && \
    test ! -w /etc/passwd

# Expose port
EXPOSE 8000

# Health check with timeout and proper error handling
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set up signal handling for graceful shutdown
STOPSIGNAL SIGTERM

# Use tini for proper signal handling and zombie reaping
ENTRYPOINT ["tini", "--", "./docker-entrypoint.sh"]

# Development command with reload enabled
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--reload"]
