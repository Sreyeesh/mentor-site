#!/bin/bash
echo "🔄 Quick rebuild script for toucan-ee"
echo "Stopping containers..."
docker-compose down

echo "Rebuilding image..."
docker-compose build toucan-ee

echo "Starting container..."
docker-compose up -d toucan-ee

echo "✅ Rebuild complete! Site available at localhost:3000"
