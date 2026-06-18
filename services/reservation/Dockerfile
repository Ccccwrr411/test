# syntax=docker/dockerfile:1.6

# ===== Stage 1: Build Dependencies =====
FROM python:3.12-slim AS build
WORKDIR /app

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy source
COPY . .

# ===== Stage 2: Production Runtime =====
FROM python:3.12-slim AS runtime

# Security: Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup -m appuser

# Install runtime system deps only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python packages from build stage
COPY --from=build /root/.local /home/appuser/.local

# Copy application code
COPY --from=build /app/src ./src
COPY --from=build /app/tests ./tests

# Set PATH
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Change ownership
RUN chown -R appuser:appgroup /app /home/appuser/.local

USER appuser

EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/healthz || exit 1

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
