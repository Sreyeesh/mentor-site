#!/bin/bash
echo "🔄 Quick rebuild script for mentor-site"
echo "Stopping containers..."
docker-compose down

echo "Rebuilding image..."
docker-compose build mentor-site

echo "Starting container..."
docker-compose up -d mentor-site

echo "✅ Rebuild complete! Site available at localhost:3000"
