# Stage 1: Build & dependencies
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Final lightweight runtime container
FROM python:3.11-slim as runner

WORKDIR /app

# Create non-root system user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy installed wheels/packages from builder
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application code
COPY ./app ./app

# Set ownership
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Container Healthcheck for Orchestration / Kubernetes
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
