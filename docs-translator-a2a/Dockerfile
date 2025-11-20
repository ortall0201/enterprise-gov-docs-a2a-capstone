# Lightweight Dockerfile for Render deployment
# Optimized for fast builds and minimal dependencies

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy only requirements first (for Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
# Using --no-deps to avoid pulling unnecessary transitive dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application source
COPY src/ ./src/
COPY .env.example ./.env.example

# Expose A2A service port
EXPOSE 8001

# Health check (simple HTTP check without requests library)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=2 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1

# Run the A2A server
CMD ["python", "src/a2a_server.py"]
