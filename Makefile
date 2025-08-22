# Premiere Suites Scraper Makefile

.PHONY: help setup install test run clean lint format faq-workflow deploy-faq test-faq

# Default target
help:
	@echo "Available commands:"
	@echo "  setup    - Set up the project (virtual env, dependencies, etc.)"
	@echo "  install  - Install dependencies"
	@echo "  test     - Run tests"
	@echo "  run      - Run the main scraper"
	@echo "  clean    - Clean up generated files"
	@echo "  lint     - Run linting"
	@echo "  format   - Format code"
	@echo ""
	@echo "FAQ Workflow Commands:"
	@echo "  faq-workflow - Create FAQ to Qdrant n8n workflow"
	@echo "  deploy-faq   - Deploy FAQ workflow to n8n"
	@echo "  test-faq     - Test FAQ workflow"
	@echo "  faq-setup    - Complete FAQ workflow setup (create + deploy + test)"

# Set up the project
setup:
	@echo "Setting up Premiere Suites Scraper..."
	python3 scripts/setup.py

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

# Run tests
test:
	@echo "Running tests..."
	python -m pytest tests/ -v

# Run the main scraper
run:
	@echo "Running Premiere Suites Scraper..."
	python main.py

# Clean up generated files
clean:
	@echo "Cleaning up..."
	rm -rf __pycache__
	rm -rf src/**/__pycache__
	rm -rf tests/__pycache__
	rm -rf .pytest_cache
	rm -rf data/processed/premiere_suites_*
	@echo "Cleanup completed"

# Run linting (if flake8 is installed)
lint:
	@echo "Running linting..."
	flake8 src/ tests/ --max-line-length=100 --ignore=E501,W503

# Format code (if black is installed)
format:
	@echo "Formatting code..."
	black src/ tests/ --line-length=100

# Quick start (setup + run)
quickstart: setup run

# FAQ to Qdrant Workflow
faq-workflow:
	@echo "Creating FAQ to Qdrant n8n workflow..."
	python src/n8n_integration/faq_to_qdrant_workflow.py

# Deploy FAQ workflow to n8n
deploy-faq:
	@echo "Deploying FAQ workflow to n8n..."
	python src/n8n_integration/deploy_faq_workflow.py

# Test FAQ workflow
test-faq:
	@echo "Testing FAQ workflow..."
	python src/n8n_integration/test_faq_workflow.py

# Complete FAQ workflow setup (create + deploy + test)
faq-setup: faq-workflow deploy-faq test-faq
