##
# Makefile for ARGOS development and evaluation
#
# Targets:
#  dev-up: build and start services via docker-compose
#  dev-down: tear down docker-compose services
#  demo: run scripted queries against the seed corpus
#  eval-nightly: compute metrics and write nightly report

COMPOSE_FILE=ops/docker-compose.yaml
PYTHON=python3

.PHONY: dev-up dev-down demo eval-nightly

## Build images and start all services locally via docker-compose.
dev-up:
	docker-compose -f $(COMPOSE_FILE) up --build -d

## Stop all services and remove containers, networks, and volumes.
dev-down:
	docker-compose -f $(COMPOSE_FILE) down -v

## Run the demo script to issue a sequence of queries against the answer API.
demo:
	@echo "Running demo queries..."
	$(PYTHON) eval/demo.py

## Compute metrics on recent logs and generate a nightly HTML report.
eval-nightly:
	$(PYTHON) eval/nightly_report.py --logs ./logs --output ./eval/report.html
	@echo "Nightly report generated at eval/report.html"