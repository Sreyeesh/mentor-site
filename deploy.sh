#!/bin/bash

echo "🚀 Starting deployment process..."

# Stop and remove existing containers using port 5000
echo "🧹 Cleaning up existing containers..."
docker stop mentor-site-prod 2>/dev/null || true
docker rm mentor-site-prod 2>/dev/null || true

# Also check for any other containers using port 5000
EXISTING_CONTAINER=$(docker ps --filter "publish=5000" --format "{{.Names}}" | head -1)
if [ ! -z "$EXISTING_CONTAINER" ]; then
    echo "⚠️  Found container '$EXISTING_CONTAINER' using port 5000, stopping it..."
    docker stop $EXISTING_CONTAINER
fi

# Kill any processes using port 5000 (optional, be careful)
# echo "🔍 Checking for processes on port 5000..."
# lsof -ti:5000 | xargs kill -9 2>/dev/null || true

echo "📦 Building Docker image..."
docker build -t mentor-site .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo "🌐 Starting new container..."
docker run -d \
    --name mentor-site-prod \
    -p 5000:80 \
    --restart unless-stopped \
    mentor-site

if [ $? -eq 0 ]; then
    echo "✅ Container started successfully!"
    echo "🌍 Site should be available at: http://localhost:5000/mentor-site/"
    echo "📊 Container status:"
    docker ps --filter "name=mentor-site-prod" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo ""
    echo "🔧 Useful commands:"
    echo "  View logs: docker logs mentor-site-prod -f"
    echo "  Stop container: docker stop mentor-site-prod"
    echo "  Remove container: docker rm mentor-site-prod"
    echo "  Check build files: docker exec mentor-site-prod ls -la /app/build/"
else
    echo "❌ Failed to start container!"
    docker logs mentor-site-prod 2>/dev/null || true
    exit 1
fi