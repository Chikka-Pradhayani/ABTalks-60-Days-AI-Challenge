# ==============================================================================
# AURONIX Production Backend Container
# Day 53 Production Dockerfile with Multi-Stage Build & Non-Root Security
# ==============================================================================

# Stage 1: Build & Dependencies
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final Production Runner
FROM python:3.12-slim AS runner

WORKDIR /app

# Install curl for Docker healthcheck and ca-certificates
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root application user (UID 10001) for SOC2 compliance
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser

# Copy installed python dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application source code
COPY --chown=appuser:appgroup . /app

# Ensure persistent data directories exist with write permissions
RUN mkdir -p /app/data/production /app/data/staging && \
    chown -R appuser:appgroup /app/data

# Environment configuration
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app:/app/day-53/backend \
    PORT=8001 \
    HOST=0.0.0.0 \
    ENVIRONMENT=production

# Switch to non-root user
USER appuser

# Expose production port
EXPOSE 8001

# Production container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8001}/health || exit 1

# Start production server using uvicorn
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8001}"]
