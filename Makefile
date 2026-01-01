.PHONY: help setup install test lint format type-check clean infra-up infra-down run deploy generate monitor list-s3 list-s3-raw list-s3-dlq list-s3-aggregated kafka-list-topics kafka-consume-events flink-list-jobs flink-submit-job flink-cancel-job
export DOCKER_CONFIG := $(HOME)/.docker
export AWS_ACCESS_KEY_ID := test
export AWS_SECRET_ACCESS_KEY := test
export AWS_DEFAULT_REGION := us-east-1
export AWS_ENDPOINT_URL := http://localhost:4566
export PYFLINK_JOB ?= flink-app/src/main.py

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Initial project setup
	@echo "Setting up project..."
	poetry install
	cp -n .env.example .env || true
	mkdir -p localstack-data
	@echo "Setup complete! Edit .env if needed."

install: ## Install dependencies
	poetry install

test: ## Run all tests with Nox
	poetry run nox -rs test

lint: ## Run linters with Nox
	poetry run nox -rs lint

format: ## Format code with Nox
	poetry run nox -rs format

type-check: ## Run type checking with Nox
	poetry run nox -rs type_check

clean: ## Clean generated files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache
	rm -rf infrastructure/.terraform infrastructure/terraform.tfstate* infrastructure/.terraform.lock.hcl infrastructure/.terraform.tfstate.d

verify-deps: ## Check presence of required tools
	@command -v docker >/dev/null 2>&1 || { echo "Docker is not installed"; exit 1; }
	@command -v terraform >/dev/null 2>&1 || { echo "Terraform is not installed"; exit 1; }
	@echo "Dependencies verified"

docker-up: verify-deps ## Start Docker services
	docker-compose up -d --build
	@echo "Waiting for services to stabilize..."
	@sleep 5

docker-down: ## Stop Docker services
	docker-compose down

docker-restart: ## Restart Docker services
	docker-compose stop
	docker-compose up -d

docker-clean: ## Deep clean of Docker and LocalStack resources
	@echo "Performing deep clean..."
	docker-compose down -v --remove-orphans
	rm -rf localstack-data
	# Note: grafana-data is a named volume, docker-compose down -v handles it
	@echo "Cleanup complete."

infra-up: docker-up ## Provision infrastructure
	@echo "Initializing Terraform..."
	cd infrastructure && terraform init
	@echo "Selecting 'local' workspace..."
	cd infrastructure && (terraform workspace new local || terraform workspace select local)
	@echo "Applying Terraform..."
	cd infrastructure && terraform apply -auto-approve

infra-down: ## Destroy infrastructure
	@echo "Selecting 'local' workspace..."
	cd infrastructure && terraform workspace select local || true
	@echo "Destroying resources..."
	cd infrastructure && terraform destroy -auto-approve
	$(MAKE) docker-down

run: infra-up ## Run end-to-end pipeline (Up -> Submit -> Logs)
	@echo "Infrastructure ready. Submitting Flink job..."
	$(MAKE) flink-submit-job
	@echo "Pipeline started! Following generator logs..."
	$(MAKE) generate

generate: ## Watch data generator logs
	docker-compose logs -f data-generator

list-s3: ## List S3 buckets in LocalStack
	aws --endpoint-url=$(AWS_ENDPOINT_URL) s3 ls

list-s3-raw: ## List objects in raw events S3 bucket
	aws --endpoint-url=$(AWS_ENDPOINT_URL) s3 ls s3://pageview-pipeline-local-raw-events/

list-s3-dlq: ## List objects in DLQ S3 bucket
	aws --endpoint-url=$(AWS_ENDPOINT_URL) s3 ls s3://pageview-pipeline-local-dlq/

list-s3-aggregated: ## List objects in aggregated S3 bucket
	aws --endpoint-url=$(AWS_ENDPOINT_URL) s3 ls s3://pageview-pipeline-local-aggregated/

kafka-list-topics: ## List Kafka topics
	docker exec pageview-kafka kafka-topics --bootstrap-server localhost:9092 --list

kafka-consume-events: ## Consume events from Kafka (isolated consumer group)
	@echo "Note: Using independent consumer group; will not affect Flink offsets"
	docker exec pageview-kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic pageview-events

flink-list-jobs: ## List Flink jobs
	docker exec pageview-flink-jobmanager flink list

flink-submit-job: ## Submit PyFlink job (usage: make flink-submit-job script=path/to/script.py)
	docker exec pageview-flink-jobmanager flink run -py /opt/project/$(PYFLINK_JOB)

flink-cancel-job: ## Cancel Flink job (usage: make flink-cancel-job id=<JOB_ID>)
	docker exec pageview-flink-jobmanager flink cancel $(id)

all: ## Run all checks via Nox
	poetry run nox -rs
