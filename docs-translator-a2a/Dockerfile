# Docs Translator A2A VaaS Service Dockerfile

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src/ ./src/

# Expose A2A service port
EXPOSE 8001

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV A2A_SERVICE_HOST=0.0.0.0
ENV A2A_SERVICE_PORT=8001

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/health')"

# Run the A2A server
CMD ["python", "src/a2a_server.py"]
