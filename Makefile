# Premiere Suites Scraper Makefile

.PHONY: help setup install test run clean lint format

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
