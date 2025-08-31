#!/bin/bash

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="mentor-site-prod"
IMAGE_NAME="mentor-site"
HOST_PORT="5000"
CONTAINER_PORT="80"

# Function to print colored output
print_status() {
    echo -e "${BLUE}🚀${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC}  $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if command -v lsof >/dev/null 2>&1; then
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            return 0  # Port is in use
        fi
    elif command -v netstat >/dev/null 2>&1; then
        if netstat -ln | grep ":$port " >/dev/null 2>&1; then
            return 0  # Port is in use
        fi
    fi
    return 1  # Port is available
}

# Function to stop and remove container
cleanup_container() {
    local container_name=$1
    
    if docker ps -q -f name="$container_name" | grep -q .; then
        print_status "Stopping existing container: $container_name"
        docker stop "$container_name" || true
    fi
    
    if docker ps -aq -f name="$container_name" | grep -q .; then
        print_status "Removing existing container: $container_name"
        docker rm "$container_name" || true
    fi
}

# Function to find containers using the port
find_containers_on_port() {
    local port=$1
    docker ps --filter "publish=$port" --format "{{.Names}}" 2>/dev/null || true
}

print_status "Starting deployment process..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Clean up existing container with same name
cleanup_container "$CONTAINER_NAME"

# Check for other containers using the port
CONTAINERS_ON_PORT=$(find_containers_on_port "$HOST_PORT")
if [ ! -z "$CONTAINERS_ON_PORT" ]; then
    print_warning "Found containers using port $HOST_PORT:"
    echo "$CONTAINERS_ON_PORT"
    print_status "Stopping containers using port $HOST_PORT..."
    echo "$CONTAINERS_ON_PORT" | while read container; do
        if [ ! -z "$container" ]; then
            cleanup_container "$container"
        fi
    done
fi

# Final port check
if check_port "$HOST_PORT"; then
    print_warning "Port $HOST_PORT is still in use after cleanup"
    print_status "Checking what's using port $HOST_PORT..."
    
    if command -v lsof >/dev/null 2>&1; then
        lsof -i :$HOST_PORT || true
    elif command -v netstat >/dev/null 2>&1; then
        netstat -tlnp | grep ":$HOST_PORT " || true
    fi
    
    echo ""
    print_error "Please free port $HOST_PORT before continuing."
    echo "You can:"
    echo "  1. Kill processes using the port: sudo lsof -ti:$HOST_PORT | xargs kill -9"
    echo "  2. Or modify this script to use a different port"
    exit 1
else
    print_success "Port $HOST_PORT is available"
fi

print_status "Building Docker image..."
if docker build --no-cache -t "$IMAGE_NAME" .; then
    print_success "Docker image built successfully"
else
    print_error "Docker build failed!"
    exit 1
fi

print_status "Starting new container..."
CONTAINER_ID=$(docker run -d \
    --name "$CONTAINER_NAME" \
    -p "$HOST_PORT:$CONTAINER_PORT" \
    --restart unless-stopped \
    "$IMAGE_NAME" 2>/dev/null)

if [ $? -eq 0 ] && [ ! -z "$CONTAINER_ID" ]; then
    print_success "Container started successfully!"
    echo "Container ID: ${CONTAINER_ID:0:12}"
    
    # Wait a moment for container to fully start
    sleep 3
    
    # Check container status
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        print_success "Container is running"
        
        # Display container info
        echo ""
        print_status "Container status:"
        docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        
        echo ""
        print_success "🌍 Site should be available at:"
        echo "   http://localhost:$HOST_PORT/mentor-site/"
        echo "   http://127.0.0.1:$HOST_PORT/mentor-site/"
        
        # Test if the site is responding
        print_status "Testing site availability..."
        sleep 3
        
        if command -v curl >/dev/null 2>&1; then
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$HOST_PORT/mentor-site/" || echo "000")
            if [[ "$HTTP_CODE" =~ ^[23] ]]; then
                print_success "Site is responding! (HTTP $HTTP_CODE)"
                
                # Test static files
                print_status "Testing static file access..."
                CSS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$HOST_PORT/mentor-site/static/css/style.css" || echo "000")
                JS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$HOST_PORT/mentor-site/static/js/script.js" || echo "000")
                
                if [[ "$CSS_CODE" =~ ^[23] ]]; then
                    print_success "CSS file accessible! (HTTP $CSS_CODE)"
                else
                    print_warning "CSS file not accessible (HTTP $CSS_CODE)"
                fi
                
                if [[ "$JS_CODE" =~ ^[23] ]]; then
                    print_success "JS file accessible! (HTTP $JS_CODE)"
                else
                    print_warning "JS file not accessible (HTTP $JS_CODE)"
                fi
                
            else
                print_warning "Site returned HTTP $HTTP_CODE - check logs if needed"
                print_status "Checking container logs..."
                docker logs "$CONTAINER_NAME" --tail 10
            fi
        else
            print_warning "curl not available - please test the site manually"
        fi
        
    else
        print_error "Container started but is not running. Checking logs..."
        docker logs "$CONTAINER_NAME" 2>/dev/null || true
        exit 1
    fi
    
else
    print_error "Failed to start container!"
    docker logs "$CONTAINER_NAME" 2>/dev/null || true
    exit 1
fi

echo ""
print_status "🔧 Useful commands:"
echo "  View logs:          docker logs $CONTAINER_NAME -f"
echo "  Stop container:     docker stop $CONTAINER_NAME"
echo "  Remove container:   docker rm $CONTAINER_NAME"
echo "  Shell access:       docker exec -it $CONTAINER_NAME sh"
echo "  Check build files:  docker exec $CONTAINER_NAME ls -la /app/build/"
echo "  Test nginx config:  docker exec $CONTAINER_NAME nginx -t"
echo "  Restart nginx:      docker exec $CONTAINER_NAME nginx -s reload"
echo ""
print_success "🚀 Local deployment completed successfully! 🎉"
echo ""
print_status "📝 Next steps for GitHub Pages deployment:"
echo "  1. Extract static files: docker cp $CONTAINER_NAME:/app/build ./github-pages-deploy"
echo "  2. Copy contents to your GitHub Pages repository"
echo "  3. Push to GitHub to deploy to toucan.ee"