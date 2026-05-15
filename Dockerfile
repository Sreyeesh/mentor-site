# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Allow overriding the URL base path (useful for GitHub Pages)
ARG BASE_PATH=/mentor-site

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV BASE_PATH=${BASE_PATH}
ENV GITHUB_PAGES_BASE_PATH=${BASE_PATH}

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

COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80 (nginx listens on this port inside container)
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Run nginx as root (simpler and more reliable)
CMD ["nginx", "-g", "daemon off;"]
