# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Allow overriding the URL base path (useful for GitHub Pages)
ARG BASE_PATH=/mentor-site

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    PYTHONPATH=/app \
    BASE_PATH=${BASE_PATH} \
    GITHUB_PAGES_BASE_PATH=${BASE_PATH} \
    SITE_CALENDLY_LINK=https://calendly.com/toucan-sg/consulting-link \
    STRIPE_SECRET_KEY= \
    STRIPE_PUBLISHABLE_KEY= \
    STRIPE_PRICE_ID= \
    STRIPE_SUCCESS_URL= \
    STRIPE_CANCEL_URL= \
    STRIPE_ENDPOINT_SECRET=

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        nginx \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Generate static site for production and verify it worked
RUN python freeze.py && ls -la build/

# Create directories for nginx
RUN mkdir -p /var/cache/nginx /var/log/nginx /var/lib/nginx /run/nginx

# Create nginx configuration for serving static files
RUN echo 'events { \
    worker_connections 1024; \
} \
\
http { \
    include /etc/nginx/mime.types; \
    default_type application/octet-stream; \
    \
    access_log /var/log/nginx/access.log; \
    error_log /var/log/nginx/error.log warn; \
    \
    sendfile on; \
    tcp_nopush on; \
    tcp_nodelay on; \
    keepalive_timeout 65; \
    \
    gzip on; \
    gzip_vary on; \
    gzip_min_length 10240; \
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json; \
    \
    server { \
        listen 80; \
        server_name localhost; \
        root /app/build; \
        index index.html; \
        \
        # Serve static files directly \
        location /static/ { \
            expires 1y; \
            add_header Cache-Control "public, immutable"; \
            add_header Access-Control-Allow-Origin "*"; \
        } \
        \
        # Serve all other files \
        location / { \
            try_files $uri $uri/ /index.html; \
            autoindex off; \
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

# Expose port 80 (nginx listens on this port inside container)
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Run nginx as root (simpler and more reliable)
CMD ["nginx", "-g", "daemon off;"]
