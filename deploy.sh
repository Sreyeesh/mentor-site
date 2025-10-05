#!/bin/bash

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Paths & configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTAINER_NAME="mentor-site-prod"
IMAGE_NAME="mentor-site"
HOST_PORT="5000"
CONTAINER_PORT="80"

AUTHORING_ENABLED=0
AUTHORING_CONTAINER_NAME="mentor-site-authoring"
AUTHORING_IMAGE_NAME="mentor-site-authoring"
AUTHORING_CONTAINER_PORT="5000"
AUTHORING_HOST_PORT="5001"
AUTHORING_DOCKERFILE="Dockerfile.dev"
AUTHORING_SECRET_KEY_DEFAULT="authoring-dev-secret"

usage() {
    cat <<USAGE
Usage: ./deploy.sh [options]

Options:
  --with-authoring        Launch the blog authoring tool alongside the static site (default port 5001)
  --authoring-port PORT   Override the host port used for the authoring tool (implies --with-authoring)
  -h, --help              Show this help message
USAGE
}

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

ensure_port_available() {
    local port=$1
    local label=$2

    local containers_on_port
    containers_on_port=$(find_containers_on_port "$port")
    if [ -n "$containers_on_port" ]; then
        print_warning "Found containers using port $port ($label):"
        echo "$containers_on_port"
        print_status "Stopping containers using port $port..."
        echo "$containers_on_port" | while read -r container; do
            if [ -n "$container" ]; then
                cleanup_container "$container"
            fi
        done
    fi

    if check_port "$port"; then
        print_warning "Port $port is still in use after cleanup"
        print_status "Checking what's using port $port..."

        if command -v lsof >/dev/null 2>&1; then
            lsof -i :$port || true
        elif command -v netstat >/dev/null 2>&1; then
            netstat -tlnp | grep ":$port " || true
        fi

        echo ""
        print_error "Please free port $port before continuing."
        echo "You can:"
        echo "  1. Kill processes using the port: sudo lsof -ti:$port | xargs kill -9"
        echo "  2. Or modify this script to use a different port"
        exit 1
    else
        print_success "Port $port is available"
    fi
}

# Parse CLI arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --with-authoring)
            AUTHORING_ENABLED=1
            shift
            ;;
        --authoring-port)
            AUTHORING_ENABLED=1
            shift
            if [[ $# -eq 0 ]]; then
                print_error "Missing value for --authoring-port"
                usage
                exit 1
            fi
            AUTHORING_HOST_PORT="$1"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

AUTHORING_SECRET_KEY="${AUTHORING_SECRET_KEY:-$AUTHORING_SECRET_KEY_DEFAULT}"

print_status "Starting deployment process..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Clean up existing containers
cleanup_container "$CONTAINER_NAME"
if [ "$AUTHORING_ENABLED" -eq 1 ]; then
    cleanup_container "$AUTHORING_CONTAINER_NAME"
fi

# Ensure ports are free
ensure_port_available "$HOST_PORT" "static site"
if [ "$AUTHORING_ENABLED" -eq 1 ]; then
    ensure_port_available "$AUTHORING_HOST_PORT" "authoring tool"
fi

print_status "Building Docker image for static site..."
if docker build --no-cache -t "$IMAGE_NAME" .; then
    print_success "Docker image built successfully"
else
    print_error "Docker build failed!"
    exit 1
fi

if [ "$AUTHORING_ENABLED" -eq 1 ]; then
    print_status "Building Docker image for authoring tool (using $AUTHORING_DOCKERFILE)..."
    if docker build --no-cache -t "$AUTHORING_IMAGE_NAME" -f "$AUTHORING_DOCKERFILE" .; then
        print_success "Authoring tool image built successfully"
    else
        print_error "Authoring tool build failed!"
        exit 1
    fi
fi

print_status "Starting new container..."
CONTAINER_ID=$(docker run -d \
    --name "$CONTAINER_NAME" \
    -p "$HOST_PORT:$CONTAINER_PORT" \
    --restart unless-stopped \
    "$IMAGE_NAME" 2>/dev/null)

if [ $? -eq 0 ] && [ -n "$CONTAINER_ID" ]; then
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

if [ "$AUTHORING_ENABLED" -eq 1 ]; then
    print_status "Starting authoring tool container..."
    AUTHORING_CONTAINER_ID=$(docker run -d \
        --name "$AUTHORING_CONTAINER_NAME" \
        -p "$AUTHORING_HOST_PORT:$AUTHORING_CONTAINER_PORT" \
        -v "$PROJECT_ROOT/content:/app/content" \
        --env AUTHORING_CONTENT_DIR=/app/content/posts \
        --env AUTHORING_SECRET_KEY="$AUTHORING_SECRET_KEY" \
        --restart unless-stopped \
        "$AUTHORING_IMAGE_NAME" \
        python author_app.py 2>/dev/null)

    if [ $? -eq 0 ] && [ -n "$AUTHORING_CONTAINER_ID" ]; then
        print_success "Authoring tool is running!"
        echo "Container ID: ${AUTHORING_CONTAINER_ID:0:12}"
        echo "Access it at: http://localhost:$AUTHORING_HOST_PORT/authoring/"
    else
        print_error "Failed to start authoring container!"
        docker logs "$AUTHORING_CONTAINER_NAME" 2>/dev/null || true
        exit 1
    fi
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
if [ "$AUTHORING_ENABLED" -eq 1 ]; then
    echo "  Authoring logs:     docker logs $AUTHORING_CONTAINER_NAME -f"
    echo "  Stop authoring:     docker stop $AUTHORING_CONTAINER_NAME"
    echo "  Remove authoring:   docker rm $AUTHORING_CONTAINER_NAME"
fi
echo ""
print_success "🚀 Local deployment completed successfully! 🎉"
echo ""
print_status "📝 Next steps for GitHub Pages deployment:"
echo "  1. Extract static files: docker cp $CONTAINER_NAME:/app/build ./github-pages-deploy"
echo "  2. Copy contents to your GitHub Pages repository"
echo "  3. Push to GitHub to deploy to toucan.ee"
