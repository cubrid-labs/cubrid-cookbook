.PHONY: help up down status clean

DOCKER_COMPOSE := docker compose

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Start CUBRID database
	$(DOCKER_COMPOSE) up -d
	@echo "Waiting for CUBRID to be ready..."
	@until $(DOCKER_COMPOSE) exec -T cubrid csql -u dba testdb -c "SELECT 1" > /dev/null 2>&1; do \
		sleep 2; \
	done
	@echo "✓ CUBRID is ready at localhost:33000"

down: ## Stop CUBRID database
	$(DOCKER_COMPOSE) down

status: ## Show container status
	$(DOCKER_COMPOSE) ps

clean: ## Stop and remove all data
	$(DOCKER_COMPOSE) down -v
	@echo "✓ Cleaned up all containers and volumes"
