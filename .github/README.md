# GitHub Actions CI/CD System

**Comprehensive automation for the Obsidian Interview Questions vault**

This directory contains GitHub Actions workflows that automate vault validation, health reporting, and maintenance tasks using the [automation package](../automation/).

---

## Overview

The CI/CD system provides:

1. **Automated Note Validation** - Validate notes on every PR
2. **Vault Health Reporting** - Daily health checks with detailed reports
3. **Concept Normalization** - On-demand frontmatter standardization
4. **Graph Exports** - Weekly vault graph exports for analysis

All workflows leverage the [obsidian-vault automation package](../automation/) (v0.8.0) which provides comprehensive validation, graph analytics, and reporting capabilities.

---

## Workflows

### 1. Validate Notes (PR Checks)

**File**: [`validate-notes.yml`](./workflows/validate-notes.yml)

**Triggers**:
- Pull requests that modify `InterviewQuestions/**/*.md`
- Push to `main` branch

**Purpose**: Ensure all new and modified notes meet quality standards before merging.

**What it does**:
1. Detects changed Markdown files in PRs
2. Validates each changed file using the automation package
3. Runs comprehensive validators:
   - YAML frontmatter structure
   - Bilingual (EN/RU) content
   - Link integrity
   - Filename and folder conventions
   - Code formatting
   - Android-specific rules (if applicable)
   - System design patterns (if applicable)
4. Generates validation report
5. Comments on PR with validation results
6. Uploads validation report as artifact

**Exit behavior**:
- **Fails** if any CRITICAL issues are found
- **Passes** with warnings/info messages if no critical issues

**Example comment**:
```
## Validation Results

### File: InterviewQuestions/70-Kotlin/q-coroutine-context--kotlin--medium.md

PASSED (12 checks):
+ YAML frontmatter complete
+ Both EN and RU content present
+ All links resolve correctly
+ Filename follows convention
+ Folder placement correct

WARNING (1 issue):
- Consider adding 1-2 more related links (currently 2, recommended 3-5)
```

---

### 2. Vault Health Report (Scheduled)

**File**: [`vault-health-report.yml`](./workflows/vault-health-report.yml)

**Triggers**:
- Daily at 00:00 UTC (cron schedule)
- Manual trigger via `workflow_dispatch`
- Push to `main` that modifies the workflow file

**Purpose**: Generate comprehensive vault health reports and track repository quality over time.

**What it does**:
1. Generates comprehensive health reports:
   - Link health analysis
   - Network statistics (nodes, edges, density)
   - Orphaned notes (no links)
   - Broken links (links to non-existent notes)
   - Missing translations
   - Full vault validation
2. Uploads reports as artifacts (90-day retention)
3. Commits reports to `reports` branch
4. Creates GitHub issue if critical problems are found (broken links, orphans)

**Reports generated**:
- `VAULT-HEALTH-SUMMARY.md` - Executive summary
- `link-health-report.md` - Comprehensive link analysis
- `validation-report.md` - Full vault validation results
- `graph-stats.txt` - Network statistics
- `orphaned-notes.txt` - List of orphaned notes
- `broken-links.txt` - List of broken links
- `missing-translations.txt` - Notes missing EN or RU

**Branch**: Reports are committed to the `reports` branch for historical tracking.

**Issue creation**: Automatically creates or updates a GitHub issue labeled `vault-health` when critical problems are detected.

---

### 3. Normalize Concepts (Manual)

**File**: [`normalize-concepts.yml`](./workflows/normalize-concepts.yml)

**Triggers**:
- Manual trigger only (`workflow_dispatch`)

**Purpose**: Standardize concept note frontmatter across the vault.

**Inputs**:
- `dry_run` (boolean, default: true) - Preview changes without applying

**What it does**:
1. Runs frontmatter normalization on all concept notes (`10-Concepts/c-*.md`)
2. Normalizes:
   - YAML field ordering
   - Missing field inference from tags
   - MOC reference correction
   - Date formatting
3. In dry-run mode: Shows preview of changes without modifying files
4. In apply mode: Creates a Pull Request with normalized changes

**Safety**:
- Default is dry-run mode to prevent accidental changes
- Always creates a PR for review before merging
- Labels PR as `automated` and `normalization`

**Example usage**:
1. Go to Actions > Normalize Concepts
2. Click "Run workflow"
3. Select dry_run: false
4. Review the generated PR
5. Merge if changes look good

---

### 4. Graph Export (Weekly)

**File**: [`graph-export.yml`](./workflows/graph-export.yml)

**Triggers**:
- Weekly on Sundays at 00:00 UTC
- Manual trigger with format selection

**Purpose**: Export vault link graph for external analysis and visualization.

**Inputs** (manual trigger):
- `format` (choice: all, gexf, graphml, json, csv) - Export format

**What it does**:
1. Exports vault graph to multiple formats:
   - **GEXF** - For Gephi visualization
   - **GraphML** - For yEd, Cytoscape
   - **JSON** - Node-link data format
   - **CSV** - Simple edge list
2. Creates timestamped exports
3. Maintains "latest" versions for easy access
4. Commits exports to `graph-exports` branch
5. Uploads as artifacts (90-day retention)

**Use cases**:
- Visualize vault structure in Gephi
- Analyze link patterns programmatically
- Track graph evolution over time
- Import into graph analysis tools

---

## Branch Strategy

The CI/CD system uses separate branches for different types of outputs:

- **`main`** - Production vault content
- **`reports`** - Daily health reports (auto-updated)
- **`graph-exports`** - Weekly graph exports (auto-updated)
- **`automated/*`** - Automated PR branches (e.g., `automated/normalize-concepts`)

**Note**: The `reports` and `graph-exports` branches are commit-only and not merged back to `main`.

---

## Setup

### Prerequisites

The workflows require:
- Python 3.12
- [uv](https://github.com/astral-sh/uv) package installer
- [automation](../automation/) package dependencies

All dependencies are automatically installed by the workflows.

### Permissions

Workflows require the following permissions:
- `contents: write` - To commit reports and exports to branches
- `issues: write` - To create health issues
- `pull-requests: write` - To comment on PRs

These are configured in each workflow file.

### Secrets

No secrets are required. Workflows use the default `GITHUB_TOKEN` which is automatically provided by GitHub Actions.

---

## Automation Package Integration

All workflows use the [automation package](../automation/) which provides:

**CLI Commands**:
- `vault validate` - Comprehensive note validation
- `vault normalize` - Concept frontmatter normalization
- `vault check-translations` - Find missing translations
- `vault graph-stats` - Network statistics
- `vault orphans` - Find orphaned notes
- `vault broken-links` - Find broken links
- `vault link-report` - Generate health report
- `vault graph-export` - Export graph data

**Validators** (7 total):
- YAMLValidator - Frontmatter structure
- ContentValidator - Bilingual content
- LinkValidator - Link integrity
- FormatValidator - File naming
- CodeFormatValidator - Code formatting
- AndroidValidator - Android-specific rules
- SystemDesignValidator - System design patterns

**See**: [automation/README.md](../automation/README.md) for complete documentation.

---

## Monitoring

### Workflow Status

Check workflow status:
- [Actions tab](../../actions) - All workflow runs
- [Validate Notes runs](../../actions/workflows/validate-notes.yml)
- [Vault Health Report runs](../../actions/workflows/vault-health-report.yml)

### Reports

Access generated reports:
- **Latest reports**: [reports branch](../../tree/reports/vault-reports)
- **Latest exports**: [graph-exports branch](../../tree/graph-exports/exports)
- **Artifacts**: Available in workflow run pages (90-day retention)

### Issues

Health issues are automatically created:
- Label: `vault-health`
- Updated daily if problems persist
- Auto-closed when problems are resolved

---

## Customization

### Adjusting Schedules

Edit cron expressions in workflow files:

```yaml
# Daily at 02:00 UTC instead of 00:00
schedule:
  - cron: '0 2 * * *'

# Weekly on Mondays instead of Sundays
schedule:
  - cron: '0 0 * * 1'
```

### Adding Validation Rules

Add new validators to the [automation package](../automation/src/obsidian_vault/validators/):

1. Create new validator file
2. Extend `BaseValidator`
3. Register with `@ValidatorRegistry.register`
4. Validators are auto-discovered, no workflow changes needed

**See**: [automation/src/obsidian_vault/validators/README.md](../automation/src/obsidian_vault/validators/README.md)

### Custom Reports

Modify report generation in workflows or add new CLI commands to the automation package.

---

## Troubleshooting

### Workflow Fails on PR

1. Check the workflow run logs in Actions tab
2. Review the validation report artifact
3. Fix validation errors in your notes
4. Push fixes to the PR

### Health Report Not Generated

1. Check if `vault-health-report.yml` workflow succeeded
2. Review workflow logs for errors
3. Check `reports` branch for latest reports
4. Verify automation package dependencies installed correctly

### Graph Export Fails

1. Ensure vault has at least one note with links
2. Check obsidiantools compatibility
3. Review workflow logs for specific errors

### Manual Workflow Trigger

Go to [Actions tab](../../actions), select the workflow, and click "Run workflow" button.

---

## Development

### Testing Workflows Locally

Use [act](https://github.com/nektos/act) to test workflows locally:

```bash
# Install act
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run validation workflow
act pull_request -W .github/workflows/validate-notes.yml

# Run health report workflow
act schedule -W .github/workflows/vault-health-report.yml
```

### Debugging

Add debug output to workflows:

```yaml
- name: Debug step
  run: |
    echo "Debug information"
    ls -la
    env
```

Enable debug logging:
- Repository Settings > Secrets > New repository secret
- Name: `ACTIONS_STEP_DEBUG`, Value: `true`

---

## Best Practices

1. **Always dry-run first**: Use `workflow_dispatch` with dry_run=true before applying changes
2. **Review PR comments**: Check validation results before merging
3. **Monitor health issues**: Address vault health issues promptly
4. **Keep automation updated**: Update automation package when new validators are added
5. **Check reports regularly**: Review weekly/monthly trends in vault quality

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Actions                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ triggers
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Workflows                                │
├─────────────────────────────────────────────────────────────┤
│  • validate-notes.yml       (PR validation)                 │
│  • vault-health-report.yml  (scheduled reporting)           │
│  • normalize-concepts.yml   (manual normalization)          │
│  • graph-export.yml         (weekly exports)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ uses
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Automation Package (v0.8.0)                    │
├─────────────────────────────────────────────────────────────┤
│  CLI:                                                       │
│    • vault validate                                         │
│    • vault normalize                                        │
│    • vault check-translations                               │
│    • vault graph-stats                                      │
│    • vault orphans                                          │
│    • vault broken-links                                     │
│    • vault link-report                                      │
│    • vault graph-export                                     │
│                                                             │
│  Validators:                                                │
│    • YAMLValidator                                          │
│    • ContentValidator                                       │
│    • LinkValidator                                          │
│    • FormatValidator                                        │
│    • CodeFormatValidator                                    │
│    • AndroidValidator                                       │
│    • SystemDesignValidator                                  │
│                                                             │
│  Utils:                                                     │
│    • Graph analytics (obsidiantools)                        │
│    • Frontmatter handling (python-frontmatter)              │
│    • Markdown parsing (marko)                               │
│    • Logging (loguru)                                       │
│    • Reporting                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ operates on
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Obsidian Vault                                 │
├─────────────────────────────────────────────────────────────┤
│  InterviewQuestions/                                        │
│    ├── 10-Concepts/        (93 notes)                       │
│    ├── 20-Algorithms/                                       │
│    ├── 30-System-Design/                                    │
│    ├── 40-Android/                                          │
│    ├── 50-Backend/                                          │
│    ├── 60-CompSci/                                          │
│    ├── 70-Kotlin/                                           │
│    ├── 80-Tools/                                            │
│    └── 90-MOCs/                                             │
│                                                             │
│  Total: 976 question notes + 93 concept notes               │
└─────────────────────────────────────────────────────────────┘
```

---

## Version History

### v1.0.0 (2025-11-08)

Initial CI/CD system implementation:

- Automated note validation on PR
- Daily vault health reporting
- Manual concept normalization
- Weekly graph exports
- Integration with automation package v0.8.0
- Comprehensive documentation

---

## Related Documentation

- [Automation Package README](../automation/README.md) - Complete automation documentation
- [Validators README](../automation/src/obsidian_vault/validators/README.md) - Validator details
- [CLAUDE.md](../CLAUDE.md) - Claude Code agent guide
- [AGENTS.md](../AGENTS.md) - AI agent instructions

---

## Support

For issues or questions:
1. Check workflow logs in [Actions tab](../../actions)
2. Review [automation package documentation](../automation/README.md)
3. Create an issue with the `ci-cd` label

---

**Last Updated**: 2025-11-08
**Version**: 1.0.0
**Maintained by**: GitHub Actions + automation package v0.8.0
