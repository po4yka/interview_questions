# Pre-commit Hooks Setup Guide

This repository uses [pre-commit](https://pre-commit.com/) to automatically run code quality checks before commits.

## What Gets Checked?

The pre-commit hooks will automatically:

1. **Standard Checks** (all files)

   - Remove trailing whitespace
   - Fix end-of-file issues
   - Validate YAML, TOML, JSON syntax
   - Check for large files (>1MB)
   - Detect merge conflicts
   - Detect private keys

2. **Python Code** (automation/)

   - **Ruff**: Auto-format and lint Python code
   - **Mypy**: Static type checking
   - **Bandit**: Security vulnerability scanning
   - **Pydocstyle**: Docstring style checking

3. **Documentation**

   - **Prettier**: Format Markdown, YAML, JSON
   - **Markdownlint**: Markdown style consistency

4. **Shell Scripts**
   - **Shellcheck**: Shell script linting

---

## Installation

### 1. Install pre-commit

**Option A: Using pip**

```bash
pip install pre-commit
```

**Option B: Using uv (recommended for this project)**

```bash
cd automation
uv sync --extra dev
```

**Option C: Using system package manager**

```bash
# macOS
brew install pre-commit

# Ubuntu/Debian
sudo apt install pre-commit

# Fedora
sudo dnf install pre-commit
```

### 2. Install the Git Hooks

From the repository root:

```bash
pre-commit install
```

This installs the hooks into `.git/hooks/pre-commit`.

---

## Usage

### Automatic (Recommended)

Once installed, hooks run automatically on `git commit`:

```bash
git add .
git commit -m "your commit message"

# Hooks run automatically:
# - If all checks pass ✓ → commit succeeds
# - If checks fail ✗ → commit is blocked, files are auto-fixed
# - Review changes and commit again
```

### Manual Execution

Run hooks without committing:

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Run specific hook
pre-commit run ruff --all-files
pre-commit run mypy --all-files
```

### Bypassing Hooks (Use with Caution)

In rare cases, you may need to bypass hooks:

```bash
git commit --no-verify -m "emergency fix"
```

**Warning**: Only use `--no-verify` for emergencies. Always fix issues properly.

---

## What Each Hook Does

### Ruff (Python Linting & Formatting)

**Purpose**: Fast Python linter and formatter (replaces black, isort, flake8)

**What it fixes**:

- Code formatting (PEP 8 compliance)
- Import sorting
- Unused imports/variables
- Simple code improvements

**Example**:

```python
# Before
import sys
import os
from pathlib import Path

def foo( x,y ):
    return x+y

# After (auto-fixed by ruff)
import os
import sys
from pathlib import Path

def foo(x, y):
    return x + y
```

### Mypy (Type Checking)

**Purpose**: Static type analysis for Python

**What it checks**:

- Type annotations correctness
- Type consistency
- Potential runtime type errors

**Example**:

```python
# This will fail mypy
def add(x: int, y: int) -> int:
    return x + y

result: str = add(1, 2)  # ✗ Type error: int assigned to str

# Fix
result: int = add(1, 2)  # ✓ Correct
```

### Bandit (Security)

**Purpose**: Find common security issues in Python code

**What it detects**:

- SQL injection vulnerabilities
- Hardcoded passwords
- Unsafe YAML loading
- Shell injection risks
- Weak cryptography

**Example**:

```python
# ✗ Security issue detected
password = "hardcoded_password"  # B105: Hardcoded password

# ✓ Correct approach
password = os.getenv("PASSWORD")
```

### Pydocstyle (Docstrings)

**Purpose**: Ensure consistent docstring style (Google convention)

**What it checks**:

- Docstring presence
- Docstring formatting
- Parameter documentation

**Example**:

```python
# ✗ Missing docstring
def calculate_total(items):
    return sum(items)

# ✓ Proper docstring
def calculate_total(items):
    """Calculate the total sum of items.

    Args:
        items: List of numeric values to sum.

    Returns:
        The sum of all items.
    """
    return sum(items)
```

### Prettier (Markdown/YAML/JSON)

**Purpose**: Auto-format documentation files

**What it fixes**:

- Consistent indentation
- Line wrapping
- Quote style
- Trailing commas

### Markdownlint

**Purpose**: Markdown style consistency

**What it checks**:

- Heading style
- List formatting
- Code block fencing
- Link formatting

---

## Configuration Files

Pre-commit uses these configuration files:

| File                        | Purpose                                              |
| --------------------------- | ---------------------------------------------------- |
| `.pre-commit-config.yaml`   | Pre-commit hook definitions                          |
| `.prettierrc`               | Prettier formatting rules                            |
| `.markdownlint.json`        | Markdown linting rules                               |
| `automation/pyproject.toml` | Python tool configs (ruff, mypy, bandit, pydocstyle) |

---

## Troubleshooting

### Hook fails with "command not found"

**Problem**: Pre-commit can't find a required tool

**Solution**: Update pre-commit environments

```bash
pre-commit clean
pre-commit install
pre-commit run --all-files
```

### Mypy fails with import errors

**Problem**: Missing type stubs for dependencies

**Solution**: Install additional type stubs

```bash
cd automation
uv sync --extra dev  # Installs types-pyyaml and others
```

### Ruff changes conflict with manual edits

**Problem**: Ruff formatting differs from your style

**Solution**: Update ruff config in `automation/pyproject.toml`

```toml
[tool.ruff]
line-length = 120  # Change from 100
```

### Hooks are too slow

**Problem**: Running hooks on many files takes time

**Solution**: Run only on changed files

```bash
# Instead of --all-files
pre-commit run
```

### Want to skip specific hooks

**Problem**: Need to temporarily disable a hook

**Solution**: Set SKIP environment variable

```bash
SKIP=mypy git commit -m "WIP: incomplete types"
```

---

## Updating Hooks

Pre-commit hooks can become outdated. Update them periodically:

```bash
# Update to latest versions
pre-commit autoupdate

# Test the updates
pre-commit run --all-files

# Commit the updates
git add .pre-commit-config.yaml
git commit -m "chore: update pre-commit hooks"
```

---

## CI Integration

Pre-commit runs automatically in GitHub Actions via the **Code Quality** workflow.

**File**: `.github/workflows/code-quality.yml`

If hooks fail in CI but pass locally, ensure:

1. You have the latest `.pre-commit-config.yaml`
2. Your Python version matches CI (3.11+)
3. All dev dependencies are installed

---

## Best Practices

### 1. Run Before Committing

```bash
# Good workflow
pre-commit run --all-files
git add .
git commit -m "your message"
```

### 2. Fix Issues Properly

Don't bypass hooks unless absolutely necessary. If a hook fails:

1. Read the error message
2. Fix the underlying issue
3. Stage the changes
4. Commit again

### 3. Keep Hooks Updated

Update hooks monthly:

```bash
pre-commit autoupdate
```

### 4. Use in Development

Run hooks during development, not just at commit time:

```bash
# Watch mode (requires entr or similar)
find automation/src -name "*.py" | entr -c pre-commit run ruff
```

---

## Customization

### Disable a Hook Permanently

Edit `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.13.0
  hooks:
    - id: mypy
      # Add this line to disable
      # stages: [manual]
```

### Add a Custom Hook

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: custom-check
      name: Custom validation
      entry: python automation/scripts/custom_check.py
      language: system
      files: '\.md$'
```

### Change Hook Configuration

Edit tool-specific configs:

- **Ruff**: `automation/pyproject.toml` → `[tool.ruff]`
- **Mypy**: `automation/pyproject.toml` → `[tool.mypy]`
- **Bandit**: `automation/pyproject.toml` → `[tool.bandit]`
- **Prettier**: `.prettierrc`
- **Markdownlint**: `.markdownlint.json`

---

## FAQ

### Q: Do hooks run on untracked files?

**A:** No, only on staged files (`git add`).

### Q: Can I run hooks on specific files?

**A:** Yes:

```bash
pre-commit run --files automation/src/obsidian_vault/cli.py
```

### Q: Do hooks modify files?

**A:** Some do (ruff, prettier). Always review changes before committing.

### Q: What happens if I skip hooks?

**A:** CI will catch issues, but it's slower. Better to fix locally.

### Q: Can I use pre-commit with other tools?

**A:** Yes! Pre-commit works alongside:

- GitHub Actions (CI checks)
- IDE linters (VS Code, PyCharm)
- Manual tool runs

---

## Related Documentation

- [Pre-commit Official Docs](https://pre-commit.com/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Automation README](automation/README.md)
- [AUTOMATION_ANALYSIS.md](AUTOMATION_ANALYSIS.md) - Full analysis with recommendations

---

## Quick Reference

```bash
# Setup
pre-commit install

# Run on all files
pre-commit run --all-files

# Run on staged files
pre-commit run

# Update hooks
pre-commit autoupdate

# Bypass hooks (emergency only)
git commit --no-verify

# Run specific hook
pre-commit run ruff --all-files

# Skip specific hook
SKIP=mypy git commit -m "message"

# Uninstall hooks
pre-commit uninstall
```

---

**Last Updated**: 2025-11-08
**Pre-commit Version**: 3.5.0+
