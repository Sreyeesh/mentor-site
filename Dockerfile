FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    PYTHONPATH=/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc nginx curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -c "from app import app, db; app.app_context().push(); db.create_all()" \
    && python freeze.py && ls -la build/

RUN mkdir -p /var/cache/nginx /var/log/nginx /var/lib/nginx /run/nginx

RUN echo 'events { worker_connections 1024; } \
http { \
    include /etc/nginx/mime.types; \
    default_type application/octet-stream; \
    access_log /var/log/nginx/access.log; \
    error_log /var/log/nginx/error.log warn; \
    sendfile on; tcp_nopush on; tcp_nodelay on; keepalive_timeout 65; \
    gzip on; gzip_vary on; gzip_min_length 10240; \
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json; \
    server { \
        listen 80; server_name localhost; root /app/build; index index.html; \
        location /static/ { expires 1y; add_header Cache-Control "public, immutable"; } \
        location / { try_files $uri $uri/ /index.html; autoindex off; } \
        location /health { access_log off; return 200 "healthy"; add_header Content-Type text/plain; } \
    } \
}' > /etc/nginx/nginx.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
