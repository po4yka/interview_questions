# Makefile for Obsidian Vault Automation
# Run 'make help' to see all available targets

.PHONY: help install install-dev test test-cov test-watch lint format type-check security clean pre-commit validate graph docs run-cli

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
RESET := \033[0m

#=============================================================================
# Help
#=============================================================================

help: ## Show this help message
	@echo "$(BLUE)Obsidian Vault Automation - Available Commands$(RESET)"
	@echo ""
	@echo "$(GREEN)Setup:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; /^(install|install-dev)/ {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Testing:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; /^(test|test-)/ {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Code Quality:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; /^(lint|format|type-check|security|pre-commit)/ {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Vault Operations:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; /^(validate|graph|normalize)/ {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Utilities:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; /^(clean|docs|run-cli|check-deps)/ {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'

#=============================================================================
# Setup
#=============================================================================

install: ## Install package and runtime dependencies
	@echo "$(BLUE)Installing package...$(RESET)"
	uv sync
	@echo "$(GREEN)✓ Installation complete$(RESET)"

install-dev: ## Install package with development dependencies
	@echo "$(BLUE)Installing package with dev dependencies...$(RESET)"
	uv sync --extra dev
	@echo "$(BLUE)Installing pre-commit hooks...$(RESET)"
	cd .. && uv run --project automation pre-commit install
	@echo "$(GREEN)✓ Development setup complete$(RESET)"

check-deps: ## Check for outdated dependencies
	@echo "$(BLUE)Checking for outdated dependencies...$(RESET)"
	uv pip list --outdated

#=============================================================================
# Testing
#=============================================================================

test: ## Run all tests
	@echo "$(BLUE)Running tests...$(RESET)"
	uv run pytest tests/ -v

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	uv run pytest tests/ -v --cov=obsidian_vault --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)✓ Coverage report generated at htmlcov/index.html$(RESET)"

test-watch: ## Run tests in watch mode (requires pytest-watch)
	@echo "$(BLUE)Running tests in watch mode...$(RESET)"
	@echo "$(YELLOW)Note: Install pytest-watch if not available: pip install pytest-watch$(RESET)"
	uv run ptw tests/ -- -v

test-fast: ## Run tests without coverage (faster)
	@echo "$(BLUE)Running tests (fast mode)...$(RESET)"
	uv run pytest tests/ -v -x --no-cov

test-failed: ## Re-run only failed tests
	@echo "$(BLUE)Re-running failed tests...$(RESET)"
	uv run pytest tests/ -v --lf

test-verbose: ## Run tests with maximum verbosity
	@echo "$(BLUE)Running tests (verbose)...$(RESET)"
	uv run pytest tests/ -vv -s

#=============================================================================
# Code Quality
#=============================================================================

lint: ## Run linter (ruff check)
	@echo "$(BLUE)Running linter...$(RESET)"
	uv run ruff check src/

lint-fix: ## Run linter and auto-fix issues
	@echo "$(BLUE)Running linter with auto-fix...$(RESET)"
	uv run ruff check src/ --fix

format: ## Format code with ruff
	@echo "$(BLUE)Formatting code...$(RESET)"
	uv run ruff format src/
	@echo "$(GREEN)✓ Code formatted$(RESET)"

format-check: ## Check if code is formatted
	@echo "$(BLUE)Checking code formatting...$(RESET)"
	uv run ruff format src/ --check

type-check: ## Run type checker (mypy)
	@echo "$(BLUE)Running type checker...$(RESET)"
	uv run mypy src/

security: ## Run security checks (bandit)
	@echo "$(BLUE)Running security checks...$(RESET)"
	uv run bandit -r src/ -c pyproject.toml

docstyle: ## Check docstring style (pydocstyle)
	@echo "$(BLUE)Checking docstring style...$(RESET)"
	uv run pydocstyle src/

check-all: lint type-check security docstyle ## Run all code quality checks
	@echo "$(GREEN)✓ All checks passed$(RESET)"

#=============================================================================
# Pre-commit
#=============================================================================

pre-commit: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(RESET)"
	cd .. && uv run --project automation pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks to latest versions
	@echo "$(BLUE)Updating pre-commit hooks...$(RESET)"
	cd .. && uv run --project automation pre-commit autoupdate

#=============================================================================
# Vault Operations
#=============================================================================

validate: ## Validate all vault notes
	@echo "$(BLUE)Validating vault notes...$(RESET)"
	uv run vault validate --all

validate-android: ## Validate Android notes only
	@echo "$(BLUE)Validating Android notes...$(RESET)"
	uv run vault validate ../InterviewQuestions/40-Android

validate-kotlin: ## Validate Kotlin notes only
	@echo "$(BLUE)Validating Kotlin notes...$(RESET)"
	uv run vault validate ../InterviewQuestions/70-Kotlin

validate-parallel: ## Validate vault notes in parallel (faster)
	@echo "$(BLUE)Validating vault notes (parallel)...$(RESET)"
	uv run vault validate --all --parallel --workers 8

graph-stats: ## Show vault graph statistics
	@echo "$(BLUE)Analyzing vault graph...$(RESET)"
	uv run vault-app graph-stats --hubs 10 --authorities 10

orphans: ## Find orphaned notes (no links)
	@echo "$(BLUE)Finding orphaned notes...$(RESET)"
	uv run vault-app orphans

broken-links: ## Find broken links
	@echo "$(BLUE)Finding broken links...$(RESET)"
	uv run vault-app broken-links

link-report: ## Generate link health report
	@echo "$(BLUE)Generating link health report...$(RESET)"
	uv run vault-app link-report --output ../reports/link-health-report.md
	@echo "$(GREEN)✓ Report saved to ../reports/link-health-report.md$(RESET)"

graph-export: ## Export vault graph to JSON
	@echo "$(BLUE)Exporting vault graph...$(RESET)"
	uv run vault graph-export ../exports/vault-graph.json
	@echo "$(GREEN)✓ Graph exported to ../exports/vault-graph.json$(RESET)"

normalize: ## Normalize concept frontmatter (dry-run)
	@echo "$(BLUE)Normalizing concepts (dry-run)...$(RESET)"
	uv run vault normalize --dry-run

normalize-apply: ## Normalize concept frontmatter (apply changes)
	@echo "$(YELLOW)⚠ This will modify files!$(RESET)"
	@echo "$(BLUE)Normalizing concepts...$(RESET)"
	uv run vault normalize

check-translations: ## Find notes missing translations
	@echo "$(BLUE)Checking for missing translations...$(RESET)"
	uv run vault check-translations

#=============================================================================
# Cleaning
#=============================================================================

clean: ## Remove all generated files (cache, coverage, etc.)
	@echo "$(BLUE)Cleaning generated files...$(RESET)"
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*.egg-info' -exec rm -r {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov/ dist/ build/
	@echo "$(GREEN)✓ Cleanup complete$(RESET)"

clean-logs: ## Remove log files
	@echo "$(BLUE)Cleaning log files...$(RESET)"
	rm -f ~/.cache/obsidian-vault/vault.log*
	@echo "$(GREEN)✓ Logs cleaned$(RESET)"

#=============================================================================
# Documentation
#=============================================================================

docs: ## Generate documentation (if sphinx is set up)
	@echo "$(YELLOW)Documentation generation not yet configured$(RESET)"
	@echo "$(BLUE)To set up documentation:$(RESET)"
	@echo "  pip install sphinx sphinx-rtd-theme"
	@echo "  sphinx-quickstart docs/"

#=============================================================================
# Utilities
#=============================================================================

run-cli: ## Run the vault CLI (interactive)
	@echo "$(BLUE)Running vault CLI...$(RESET)"
	uv run vault --help

run-cli-app: ## Run the modern CLI (interactive)
	@echo "$(BLUE)Running vault-app CLI...$(RESET)"
	uv run vault-app --help

version: ## Show package version
	@echo "$(BLUE)Package version:$(RESET)"
	@uv run python -c "import tomli; print(tomli.load(open('pyproject.toml', 'rb'))['project']['version'])" 2>/dev/null || echo "0.8.0"

info: ## Show development environment info
	@echo "$(BLUE)Development Environment Info$(RESET)"
	@echo ""
	@echo "Python version:"
	@uv run python --version
	@echo ""
	@echo "UV version:"
	@uv --version
	@echo ""
	@echo "Package version:"
	@make version
	@echo ""
	@echo "Installed packages:"
	@uv pip list | head -20

shell: ## Start a Python shell with package loaded
	@echo "$(BLUE)Starting Python shell...$(RESET)"
	uv run python

#=============================================================================
# CI/CD Simulation
#=============================================================================

ci: check-all test-cov ## Run all checks like CI/CD pipeline
	@echo "$(GREEN)✓ All CI checks passed$(RESET)"

ci-fast: lint type-check test-fast ## Run fast CI checks (no coverage)
	@echo "$(GREEN)✓ Fast CI checks passed$(RESET)"

#=============================================================================
# Development Workflow Helpers
#=============================================================================

dev-setup: install-dev ## Alias for install-dev
	@echo "$(GREEN)✓ Development environment ready$(RESET)"

quick-check: lint-fix format test-fast ## Quick development check (fix, format, test)
	@echo "$(GREEN)✓ Quick check passed$(RESET)"

full-check: format lint type-check security test-cov ## Full check before commit
	@echo "$(GREEN)✓ Full check passed - ready to commit$(RESET)"

watch: ## Watch for file changes and run tests
	@echo "$(BLUE)Watching for changes...$(RESET)"
	@echo "$(YELLOW)Note: Requires 'entr' or 'watchdog'$(RESET)"
	@echo "$(BLUE)Alternative: Use 'make test-watch' with pytest-watch$(RESET)"

#=============================================================================
# Benchmarking (future)
#=============================================================================

benchmark: ## Run performance benchmarks
	@echo "$(YELLOW)Benchmarks not yet implemented$(RESET)"
	@echo "$(BLUE)To set up benchmarks:$(RESET)"
	@echo "  pip install pytest-benchmark"
	@echo "  Create tests/benchmarks/ directory"

#=============================================================================
# Release Helpers (future)
#=============================================================================

build: ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(RESET)"
	uv build
	@echo "$(GREEN)✓ Build complete - see dist/$(RESET)"

build-check: build ## Build and verify packages
	@echo "$(BLUE)Checking built packages...$(RESET)"
	uv run twine check dist/*
	@echo "$(GREEN)✓ Package check complete$(RESET)"
