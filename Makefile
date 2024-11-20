#!/usr/bin/make -f

.DEFAULT_GOAL := up

.PHONY: up
up:
	@docker-compose up -d --build

.PHONY: down
down:
	@docker-compose down --remove-orphans