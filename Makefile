.PHONY: build up down restart logs ps clean prune help health

# Default target
.DEFAULT_GOAL := help

# Variables
DOCKER_COMPOSE = docker-compose

# Colors for terminal output
GREEN = \033[0;32m
NC = \033[0m # No Color

help: ## Show this help message
	@echo "E-Store Microservices Docker Commands"
	@echo "----------------------------------"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

build: ## Build all services or a specific service: make build [service]
	@if [ -z "$(service)" ]; then \
		echo "Building all services..."; \
		$(DOCKER_COMPOSE) build; \
	else \
		echo "Building service: $(service)..."; \
		$(DOCKER_COMPOSE) build $(service); \
	fi

up: ## Start all services or a specific service: make up [service]
	@if [ -z "$(service)" ]; then \
		echo "Starting all services..."; \
		$(DOCKER_COMPOSE) up -d; \
	else \
		echo "Starting service: $(service)..."; \
		$(DOCKER_COMPOSE) up -d $(service); \
	fi

down: ## Stop all services
	@echo "Stopping all services..."
	@$(DOCKER_COMPOSE) down

restart: ## Restart all services or a specific service: make restart [service]
	@if [ -z "$(service)" ]; then \
		echo "Restarting all services..."; \
		$(DOCKER_COMPOSE) restart; \
	else \
		echo "Restarting service: $(service)..."; \
		$(DOCKER_COMPOSE) restart $(service); \
	fi

logs: ## View logs of all services or a specific service: make logs [service]
	@if [ -z "$(service)" ]; then \
		echo "Showing logs for all services..."; \
		$(DOCKER_COMPOSE) logs -f; \
	else \
		echo "Showing logs for service: $(service)..."; \
		$(DOCKER_COMPOSE) logs -f $(service); \
	fi

ps: ## List all running services
	@echo "Listing all services..."
	@$(DOCKER_COMPOSE) ps

clean: ## Remove all containers, networks, and volumes
	@echo "Removing all containers, networks, and volumes..."
	@$(DOCKER_COMPOSE) down -v

prune: ## Remove all unused containers, networks, and images
	@echo "Removing all unused containers, networks, and images..."
	@docker system prune -a

shell: ## Open a shell in a specific service: make shell service=service_name
	@if [ -z "$(service)" ]; then \
		echo "Please specify a service: make shell service=service_name"; \
	else \
		echo "Opening shell in service: $(service)..."; \
		$(DOCKER_COMPOSE) exec $(service) sh || $(DOCKER_COMPOSE) exec $(service) bash; \
	fi

test: ## Run tests for a specific service: make test service=service_name
	@if [ -z "$(service)" ]; then \
		echo "Please specify a service: make test service=service_name"; \
	else \
		echo "Running tests for service: $(service)..."; \
		$(DOCKER_COMPOSE) run --rm $(service) pytest; \
	fi

db-migrate: ## Run database migrations for a specific service: make db-migrate service=service_name
	@if [ -z "$(service)" ]; then \
		echo "Please specify a service: make db-migrate service=service_name"; \
	else \
		echo "Running database migrations for service: $(service)..."; \
		$(DOCKER_COMPOSE) run --rm $(service) alembic upgrade head; \
	fi

db-rollback: ## Rollback database migrations for a specific service: make db-rollback service=service_name
	@if [ -z "$(service)" ]; then \
		echo "Please specify a service: make db-rollback service=service_name"; \
	else \
		echo "Rolling back database migrations for service: $(service)..."; \
		$(DOCKER_COMPOSE) run --rm $(service) alembic downgrade -1; \
	fi

health: ## Check health status of all services or a specific service: make health [service] [dashboard=true]
	@if [ -n "$(dashboard)" ] && [ "$(dashboard)" = "true" ]; then \
		echo "Opening health dashboard..."; \
		./scripts/health_check.sh --dashboard; \
	elif [ -z "$(service)" ]; then \
		echo "Checking health of all services..."; \
		./scripts/health_check.sh; \
	else \
		echo "Checking health of service: $(service)..."; \
		./scripts/health_check.sh $(service); \
	fi
