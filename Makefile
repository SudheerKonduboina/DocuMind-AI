.PHONY: setup run test lint format clean docker-build docker-up docker-down help

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup     - Install dependencies"
	@echo "  make run       - Run development server"
	@echo "  make test      - Run tests"
	@echo "  make lint      - Run linting (black, isort, mypy)"
	@echo "  make format    - Format code with black and isort"
	@echo "  make clean     - Clean cache and build artifacts"
	@echo "  make docker-build - Build Docker containers"
	@echo "  make docker-up   - Start Docker containers"
	@echo "  make docker-down - Stop Docker containers"

# Install dependencies
setup:
	pip install -r backend/requirements.txt
	pip install black isort mypy pytest pytest-cov

# Run development server
run:
	cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	cd backend && pytest -v --cov=. --cov-report=html

# Lint code
lint:
	black --check backend/
	isort --check-only backend/
	mypy backend/

# Format code
format:
	black backend/
	isort backend/

# Clean cache and artifacts
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

# Docker commands
docker-build:
	docker compose build

docker-up:
	docker compose up --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f
