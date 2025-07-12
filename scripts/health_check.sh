#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Service endpoints for health checks
declare -A SERVICES=(
  ["product-service"]="http://localhost:8000/health"
  ["payment-service"]="http://localhost:8001/health"
  ["coupon-service"]="http://localhost:8002/health"
  ["order-service"]="http://localhost:8003/health"
)

# Function to check health of a service
check_service_health() {
  local service=$1
  local endpoint=${SERVICES[$service]}
  
  echo -e "${YELLOW}Checking health of $service at $endpoint...${NC}"
  
  # Check if service is running using docker-compose
  if ! docker-compose ps | grep -q "$service.*Up"; then
    echo -e "${RED}✘ $service is not running${NC}"
    return 1
  fi
  
  # Check health endpoint
  local response=$(curl -s -o /dev/null -w "%{http_code}" $endpoint)
  
  if [ "$response" == "200" ]; then
    echo -e "${GREEN}✓ $service is healthy${NC}"
    return 0
  else
    echo -e "${RED}✘ $service returned HTTP $response${NC}"
    return 1
  fi
}

# Function to open health dashboard
open_dashboard() {
  echo -e "${YELLOW}Opening health dashboard...${NC}"
  
  # Determine the correct command to open a browser based on OS
  if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open "file://$(pwd)/scripts/health_dashboard.html" 2>/dev/null || \
    echo -e "${YELLOW}Please open the dashboard manually at: file://$(pwd)/scripts/health_dashboard.html${NC}"
  elif [[ "$OSTYPE" == "darwin"* ]]; then
    open "file://$(pwd)/scripts/health_dashboard.html" 2>/dev/null || \
    echo -e "${YELLOW}Please open the dashboard manually at: file://$(pwd)/scripts/health_dashboard.html${NC}"
  elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    start "file://$(pwd)/scripts/health_dashboard.html" 2>/dev/null || \
    echo -e "${YELLOW}Please open the dashboard manually at: file://$(pwd)/scripts/health_dashboard.html${NC}"
  else
    echo -e "${YELLOW}Please open the dashboard manually at: file://$(pwd)/scripts/health_dashboard.html${NC}"
  fi
}

# Main function
main() {
  local specific_service=$1
  local dashboard_flag=$2
  local exit_code=0
  
  echo "E-Store Microservices Health Check"
  echo "=================================="
  
  if [ "$specific_service" == "--dashboard" ] || [ "$dashboard_flag" == "--dashboard" ]; then
    open_dashboard
    return 0
  fi
  
  if [ -n "$specific_service" ]; then
    # Check specific service
    if [[ -v SERVICES[$specific_service] ]]; then
      check_service_health "$specific_service" || exit_code=1
    else
      echo -e "${RED}Error: Unknown service '$specific_service'${NC}"
      echo "Available services: ${!SERVICES[@]}"
      exit_code=1
    fi
  else
    # Check all services
    for service in "${!SERVICES[@]}"; do
      check_service_health "$service" || exit_code=1
      echo ""
    done
  fi
  
  if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}All services are healthy!${NC}"
  else
    echo -e "${RED}Some services are not healthy!${NC}"
  fi
  
  # Suggest opening the dashboard
  echo -e "${YELLOW}For a visual dashboard, run: make health dashboard=true${NC}"
  
  return $exit_code
}

# Run the main function
main "$@"
