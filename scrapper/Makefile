include .env
export

SHELL := /bin/bash

.DEFAULT_GOAL := up
.PHONY: up
up: create-network down
	@docker compose up --build -d

.PHONY: down
down:
	@docker compose down --rmi local

.PHONY: stop
stop:
	@docker compose stop

.PHONY: logs
logs:
	@docker compose logs -f

.PHONY: create-network
create-network:
	@if ! docker network inspect kaleid-network > /dev/null 2>&1; then \
		echo "Criando rede 'kaleid-network'..."; \
		docker network create kaleid-network; \
		else \
		echo "Rede 'kaleid-network' já existe..."; \
	fi


# Limpeza
.PHONY: clean
clean: ## Remove containers, volumes e artifacts
	$(COMPOSE_DEV) down -v
	$(COMPOSE_PROD) down -v
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +



	# Testes e Qualidade
.PHONY: test
test: ## Roda os testes
	$(COMPOSE_DEV) run --rm collector pytest

.PHONY: lint
lint: ## Roda black, flake8 e mypy
	$(COMPOSE_DEV) run --rm collector black .
	$(COMPOSE_DEV) run --rm collector flake8
	$(COMPOSE_DEV) run --rm collector mypy .

.PHONY: format
format: ## Formata o código com black
	$(COMPOSE_DEV) run --rm collector black .