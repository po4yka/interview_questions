# Makefile Quick Reference

**Location**: `automation/Makefile`

Simplified development workflow for the Obsidian Vault Automation package.

---

## Quick Start

```bash
cd automation

# Setup development environment (one-time)
make install-dev

# Daily development workflow
make quick-check    # Format, lint, and test
make full-check     # Complete check before commit
```

---

## Common Commands

### Setup

```bash
make install           # Install package only
make install-dev       # Install with dev tools + pre-commit hooks
make check-deps        # Check for outdated dependencies
```

### Testing

```bash
make test              # Run all tests
make test-cov          # Run tests with coverage report
make test-fast         # Run tests without coverage (faster)
make test-failed       # Re-run only failed tests
```

### Code Quality

```bash
make lint              # Check code style
make lint-fix          # Check and auto-fix issues
make format            # Format code with ruff
make type-check        # Run mypy type checking
make security          # Run bandit security checks
make check-all         # Run all quality checks
```

### Vault Operations

```bash
make validate          # Validate all vault notes
make validate-android  # Validate Android notes only
make validate-kotlin   # Validate Kotlin notes only
make graph-stats       # Show vault graph statistics
make orphans           # Find orphaned notes
make broken-links      # Find broken links
make link-report       # Generate comprehensive link report
make normalize         # Normalize concepts (dry-run)
make normalize-apply   # Normalize concepts (apply changes)
```

### Cleaning

```bash
make clean             # Remove cache, coverage, etc.
make clean-logs        # Remove log files
```

### Pre-commit

```bash
make pre-commit        # Run all pre-commit hooks
make pre-commit-update # Update hooks to latest versions
```

---

## Development Workflows

### First-Time Setup

```bash
cd automation
make install-dev       # Installs package + dev deps + pre-commit hooks
```

This sets up:

- ✅ Python package and dependencies
- ✅ Development tools (pytest, ruff, mypy, bandit)
- ✅ Pre-commit hooks in `.git/hooks/`

### Daily Development

**Option 1: Quick iteration**

```bash
# Edit code
vim src/obsidian_vault/cli.py

# Quick check (format + lint + fast test)
make quick-check

# Commit
git add .
git commit -m "feat: add feature"
```

**Option 2: Full quality check**

```bash
# Edit code
vim src/obsidian_vault/validators/yaml_validator.py

# Full check (format + lint + type-check + security + coverage)
make full-check

# Commit
git add .
git commit -m "feat: improve validator"
```

**Option 3: Test-driven development**

```bash
# Write test first
vim tests/test_validators.py

# Run tests continuously
make test-watch    # Or make test-fast in a loop

# Implement feature
vim src/obsidian_vault/validators/yaml_validator.py

# Final check
make test-cov
```

### Before Committing

**Minimal check** (2-3 seconds):

```bash
make quick-check
```

**Recommended check** (10-20 seconds):

```bash
make full-check
```

**Complete CI simulation** (30-60 seconds):

```bash
make ci
```

### Working on Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run only failed tests (after fixing)
make test-failed

# Run tests in watch mode (continuous)
make test-watch
```

### Working on Documentation

```bash
# Check docstring style
make docstyle

# View current documentation structure
make docs
```

### Vault Maintenance

**Quick health check**:

```bash
make graph-stats
make orphans
make broken-links
```

**Full validation**:

```bash
# Validate everything (slow)
make validate

# Validate in parallel (faster)
make validate-parallel

# Validate specific folder
make validate-android
make validate-kotlin
```

**Generate reports**:

```bash
make link-report       # Comprehensive link health report
make check-translations # Find missing EN/RU translations
```

**Normalize concepts**:

```bash
# Preview changes
make normalize

# Apply changes
make normalize-apply
```

---

## CI/CD Simulation

Simulate what GitHub Actions will run:

```bash
# Full CI pipeline
make ci

# Fast CI check (no coverage)
make ci-fast
```

This ensures your code will pass CI checks before pushing.

---

## Troubleshooting

### "make: command not found"

**Solution**: Install `make`

```bash
# macOS
xcode-select --install

# Ubuntu/Debian
sudo apt install build-essential

# Fedora
sudo dnf install make

# Windows (WSL)
sudo apt install build-essential
```

### "uv: command not found"

**Solution**: Install `uv`

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Tests fail with import errors

**Solution**: Reinstall dependencies

```bash
make clean
make install-dev
```

### Pre-commit hooks not running

**Solution**: Reinstall hooks

```bash
cd ..  # Go to repo root
uv run --project automation pre-commit install
```

### Makefile doesn't work on Windows

**Solution**: Use WSL (Windows Subsystem for Linux) or install make for Windows

```powershell
# Using Chocolatey
choco install make

# Or use WSL (recommended)
wsl --install
```

---

## Customization

### Add Custom Targets

Edit `automation/Makefile`:

```makefile
my-custom-task: ## Description of my task
	@echo "Running my task..."
	uv run python scripts/my_script.py
```

Then run:

```bash
make my-custom-task
```

### Override Variables

```bash
# Use different number of workers
WORKERS=16 make validate-parallel

# Use different Python version
PYTHON=python3.12 make test
```

---

## Tips & Tricks

### 1. Tab Completion

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Bash
complete -W "$(make -qp | awk -F':' '/^[a-zA-Z0-9][^$#\/\t=]*:([^=]|$)/ {split($1,A,/ /);for(i in A)print A[i]}')" make

# Zsh (built-in)
# Just use: make <TAB>
```

### 2. Quick Aliases

Add to your shell config:

```bash
# Bash/Zsh
alias m='make'
alias mt='make test'
alias mtc='make test-cov'
alias mf='make format'
alias ml='make lint-fix'
alias mqc='make quick-check'
alias mfc='make full-check'
```

Then use:

```bash
m test       # Instead of: make test
mqc          # Instead of: make quick-check
```

### 3. Watch for Changes

Use `entr` for continuous testing:

```bash
# Install entr
brew install entr  # macOS
sudo apt install entr  # Ubuntu

# Watch Python files and run tests
find src -name "*.py" | entr -c make test-fast
```

### 4. Parallel Execution

Some tasks support parallel execution:

```bash
# Validate with more workers
make validate-parallel WORKERS=16

# Run multiple make targets in parallel (advanced)
make -j4 lint type-check security docstyle
```

### 5. Verbose Output

See what's happening:

```bash
# Show all commands being executed
make test VERBOSE=1

# Or use built-in make flag
make -n test  # Dry-run (show commands without executing)
```

---

## Integration with IDEs

### VS Code

Add to `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "make test",
      "type": "shell",
      "command": "make test",
      "group": "test",
      "presentation": {
        "reveal": "always"
      }
    },
    {
      "label": "make quick-check",
      "type": "shell",
      "command": "make quick-check",
      "group": "build"
    }
  ]
}
```

Then: `Cmd+Shift+P` → "Run Task" → "make test"

### PyCharm

1. Settings → Tools → External Tools
2. Add new tool:
   - Name: `Make Test`
   - Program: `make`
   - Arguments: `test`
   - Working directory: `$ProjectFileDir$/automation`
3. Assign keyboard shortcut (optional)

### Vim/Neovim

Add to `.vimrc` or `init.vim`:

```vim
" Run make test
nnoremap <leader>mt :!make test<CR>

" Run make quick-check
nnoremap <leader>mq :!make quick-check<CR>
```

---

## Comparison with Direct Commands

| Makefile                 | Direct Command                                                                   | Time Saved  |
| ------------------------ | -------------------------------------------------------------------------------- | ----------- |
| `make test`              | `uv run pytest tests/ -v`                                                        | ~50% typing |
| `make install-dev`       | `uv sync --extra dev && cd .. && uv run --project automation pre-commit install` | ~80% typing |
| `make full-check`        | `uv run ruff format src/ && uv run ruff check src/ && uv run mypy src/ && ...`   | ~90% typing |
| `make validate-parallel` | `uv run vault validate --all --parallel --workers 8`                             | ~70% typing |

**Average time saved**: 2-3 minutes per command → **10-20 minutes per day**

---

## Advanced Usage

### Chaining Commands

```bash
# Run multiple commands in sequence
make clean && make install-dev && make test-cov

# Stop on first failure
make lint && make type-check && make test
```

### Conditional Execution

```bash
# Run tests only if lint passes
make lint && make test || echo "Fix lint errors first"
```

### Background Execution

```bash
# Run tests in background
make test &

# Run multiple tasks in parallel
make lint & make type-check & make security & wait
```

---

## Reference: All Targets

Run `make help` for a categorized list of all available targets.

**Categories**:

- **Setup**: `install`, `install-dev`, `check-deps`
- **Testing**: `test`, `test-cov`, `test-fast`, `test-failed`, `test-watch`
- **Code Quality**: `lint`, `format`, `type-check`, `security`, `check-all`
- **Vault Operations**: `validate`, `graph-stats`, `orphans`, `broken-links`, `normalize`
- **Utilities**: `clean`, `docs`, `run-cli`, `version`, `info`
- **CI/CD**: `ci`, `ci-fast`, `pre-commit`

---

## See Also

- [Automation README](README.md) - Full automation documentation
- [PRE_COMMIT_SETUP.md](../PRE_COMMIT_SETUP.md) - Pre-commit hooks guide
- [AUTOMATION_ANALYSIS.md](../AUTOMATION_ANALYSIS.md) - Analysis and recommendations

---

**Last Updated**: 2025-11-08
**Makefile Version**: 1.0
