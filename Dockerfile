# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set BASE_PATH environment variable for subdirectory deployment
ENV BASE_PATH=/mentor-site

# Generate static site for production
RUN python freeze.py

# Install nginx for serving static files
RUN apt-get update && apt-get install -y nginx curl && rm -rf /var/lib/apt/lists/*

# Create non-root user for security first
RUN adduser --disabled-password --gecos '' appuser

# Create directories and set permissions for nginx to run as non-root
RUN mkdir -p /var/cache/nginx /var/log/nginx /var/lib/nginx /run/nginx \
    && chown -R appuser:appuser /var/cache/nginx /var/log/nginx /var/lib/nginx /run/nginx /etc/nginx \
    && chown -R appuser:appuser /app

# Create nginx configuration for serving static files
RUN echo 'user appuser; \
worker_processes auto; \
pid /run/nginx/nginx.pid; \
error_log /var/log/nginx/error.log warn; \
\
events { \
    worker_connections 1024; \
} \
\
http { \
    include /etc/nginx/mime.types; \
    default_type application/octet-stream; \
    \
    access_log /var/log/nginx/access.log; \
    \
    sendfile on; \
    tcp_nopush on; \
    tcp_nodelay on; \
    keepalive_timeout 65; \
    \
    server { \
        listen 5000; \
        server_name localhost; \
        root /app/build; \
        index index.html; \
        \
        # Serve static files directly \
        location /mentor-site/static/ { \
            alias /app/build/static/; \
            expires 1y; \
            add_header Cache-Control "public, immutable"; \
        } \
        \
        # Serve main page \
        location /mentor-site/ { \
            try_files $uri $uri/ /index.html; \
        } \
        \
        # Redirect root to mentor-site \
        location = / { \
            return 301 /mentor-site/; \
        } \
        \
        # Health check endpoint \
        location /health { \
            access_log off; \
            return 200 "healthy"; \
            add_header Content-Type text/plain; \
        } \
    } \
}' > /etc/nginx/nginx.conf

USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run nginx
CMD ["nginx", "-g", "daemon off;"]
