#!/bin/bash
# Credit Guardian Docker Deployment Script (Linux/Mac)
# =====================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${CYAN}========================================"
    echo -e "  $1"
    echo -e "========================================${NC}\n"
}

print_step() {
    echo -e "${YELLOW}➡️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running! Please start Docker first."
    exit 1
fi

print_header "Credit Guardian Docker Deployment"

# Parse arguments
GPU=false
BUILD=false
DOWN=false
LOGS=false
STATUS=false
SERVICE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --gpu)
            GPU=true
            shift
            ;;
        --build)
            BUILD=true
            shift
            ;;
        --down)
            DOWN=true
            shift
            ;;
        --logs)
            LOGS=true
            shift
            ;;
        --status)
            STATUS=true
            shift
            ;;
        --service)
            SERVICE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--gpu] [--build] [--down] [--logs] [--status] [--service NAME]"
            exit 1
            ;;
    esac
done

# Determine compose file
if [ "$GPU" = true ]; then
    COMPOSE_FILE="docker-compose.yml"
    echo -e "Mode: ${CYAN}GPU-accelerated${NC}"
else
    COMPOSE_FILE="docker-compose.cpu.yml"
    echo -e "Mode: ${CYAN}CPU-only${NC}"
fi

# Handle commands
if [ "$DOWN" = true ]; then
    print_step "Stopping all containers..."
    docker-compose -f $COMPOSE_FILE down
    print_success "All containers stopped"
    exit 0
fi

if [ "$LOGS" = true ]; then
    if [ -n "$SERVICE" ]; then
        docker-compose -f $COMPOSE_FILE logs -f $SERVICE
    else
        docker-compose -f $COMPOSE_FILE logs -f
    fi
    exit 0
fi

if [ "$STATUS" = true ]; then
    print_header "Container Status"
    docker-compose -f $COMPOSE_FILE ps
    
    echo -e "\n${YELLOW}📊 Resource Usage:${NC}"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    exit 0
fi

# Main deployment
print_step "Using compose file: $COMPOSE_FILE"

if [ "$BUILD" = true ]; then
    print_step "Building images..."
    docker-compose -f $COMPOSE_FILE build --no-cache
fi

print_step "Starting services..."
docker-compose -f $COMPOSE_FILE up -d

print_step "Waiting for services to be healthy..."
sleep 10

# Check service health
for svc in cg_postgres cg_ollama cg_api cg_frontend; do
    status=$(docker inspect --format='{{.State.Status}}' $svc 2>/dev/null || echo "not found")
    if [ "$status" = "running" ]; then
        print_success "$svc is running"
    else
        print_error "$svc is not running (status: $status)"
    fi
done

# Wait for Ollama model
print_step "Checking Ollama model (this may take a few minutes on first run)..."
attempts=0
max_attempts=30
while [ $attempts -lt $max_attempts ]; do
    if docker exec cg_ollama ollama list 2>/dev/null | grep -q "llama3.2"; then
        print_success "Ollama model llama3.2 is ready!"
        break
    fi
    attempts=$((attempts + 1))
    echo "  Waiting for model... ($attempts/$max_attempts)"
    sleep 10
done

if [ $attempts -eq $max_attempts ]; then
    echo -e "${YELLOW}⚠️  Model still pulling. Check with: docker logs cg_ollama_pull${NC}"
fi

print_header "Deployment Complete!"

echo -e "${CYAN}
🌐 Access Points:
   Frontend:  http://localhost:3000
   API:       http://localhost:8080
   API Docs:  http://localhost:8080/docs
   Ollama:    http://localhost:11434

📋 Useful Commands:
   View logs:     ./deploy.sh --logs
   View API logs: ./deploy.sh --logs --service api
   Status:        ./deploy.sh --status
   Stop all:      ./deploy.sh --down
   Rebuild:       ./deploy.sh --build

🧪 Test Ollama:
   docker exec cg_ollama ollama list
   docker exec cg_ollama ollama run llama3.2 \"Здравей!\"
${NC}"

