# GitHub Workflows Quick Reference

**Fast lookup for the Obsidian Interview Questions vault CI/CD system**

---

## Quick Commands

### Trigger Workflows Manually

```bash
# Go to Actions tab → Select workflow → Run workflow button
```

**Or use GitHub CLI**:

```bash
# Normalize concepts (dry-run)
gh workflow run normalize-concepts.yml -f dry_run=true

# Normalize concepts (apply changes)
gh workflow run normalize-concepts.yml -f dry_run=false

# Generate health report now
gh workflow run vault-health-report.yml

# Export graphs (all formats)
gh workflow run graph-export.yml -f format=all

# Export graphs (specific format)
gh workflow run graph-export.yml -f format=json
```

---

## Workflows at a Glance

| Workflow                | Trigger          | Purpose                 | Runtime   |
| ----------------------- | ---------------- | ----------------------- | --------- |
| **Validate Notes**      | PR, push to main | Validate changed notes  | ~2-5 min  |
| **Vault Health Report** | Daily 00:00 UTC  | Generate health reports | ~5-10 min |
| **Normalize Concepts**  | Manual only      | Standardize frontmatter | ~1-3 min  |
| **Graph Export**        | Weekly Sunday    | Export vault graph      | ~2-4 min  |

---

## Common Tasks

### Review Validation Errors in PR

1. Open the PR
2. Check the "Validate Notes" workflow status
3. Click "Details" to see workflow run
4. Review the PR comment with validation results
5. Download "validation-report" artifact for detailed analysis

### Check Vault Health

**Option 1: Latest report (fastest)**

```bash
# View in browser
open https://github.com/YOUR_ORG/YOUR_REPO/tree/reports/vault-reports
```

**Option 2: Trigger new report**

1. Go to Actions > Vault Health Report
2. Click "Run workflow"
3. Wait ~5-10 minutes
4. Check `reports` branch for results

**Option 3: Download artifact**

1. Go to Actions > Vault Health Report
2. Click latest run
3. Download "vault-health-reports" artifact

### Fix Validation Errors

Common fixes:

```yaml
# Missing required YAML field
# Add to frontmatter:
topic: kotlin
difficulty: medium
status: draft

# Missing bilingual content
# Add section:
## Ответ (RU)

[Russian translation here]

# Broken link
# Fix wikilink:
[[c-coroutines]]  # correct
[[c-coroutine]]   # wrong (note doesn't exist)
```

### Normalize Concept Notes

**Step 1: Preview changes**

1. Go to Actions > Normalize Concepts
2. Click "Run workflow"
3. Keep `dry_run` as `true`
4. Click "Run workflow"
5. Wait ~1 minute
6. Review the step summary

**Step 2: Apply if good**

1. Run workflow again
2. Set `dry_run` to `false`
3. Review the created PR
4. Merge PR if changes look good

### Export Vault Graph

**For Gephi visualization**:

1. Go to Actions > Graph Export
2. Run workflow with format: `gexf`
3. Download artifact
4. Open `.gexf` file in Gephi

**For programmatic analysis**:

1. Run workflow with format: `json`
2. Download artifact
3. Parse JSON with your tool

**All formats at once**:

- Scheduled: Runs every Sunday automatically
- Manual: Run with format: `all`

---

## Checking Workflow Status

### In GitHub UI

```
Repository → Actions tab → Select workflow
```

### Using GitHub CLI

```bash
# List workflow runs
gh run list --workflow=validate-notes.yml

# View specific run
gh run view RUN_ID

# Download artifacts
gh run download RUN_ID
```

### Check latest status

```bash
# All workflows
gh run list --limit 5

# Specific workflow
gh workflow view vault-health-report.yml
```

---

## Understanding Validation Results

### Severity Levels

| Severity     | Meaning           | Action                      |
| ------------ | ----------------- | --------------------------- |
| **CRITICAL** | Structural issues | **Must fix** before merge   |
| **ERROR**    | Serious problems  | **Should fix** before merge |
| **WARNING**  | Issues to address | Fix when possible           |
| **INFO**     | Recommendations   | Optional improvements       |

### Common Validation Issues

```
CRITICAL: Missing required heading "# Question (EN)"
→ Add the heading to your note

ERROR: Broken link to [[c-unknown-note]]
→ Create the note or fix the link

ERROR: File in wrong folder (kotlin note in android folder)
→ Move file to correct folder

WARNING: Only 1 related link (recommended: 3-5)
→ Add more cross-references

INFO: Consider adding more detailed explanation
→ Expand the answer section
```

---

## Accessing Reports

### Latest Health Report

**Branch**: `reports`

```bash
# Clone reports branch
git fetch origin reports:reports
git checkout reports

# View reports
cat vault-reports/VAULT-HEALTH-SUMMARY.md
cat vault-reports/link-health-report.md
```

**Or in browser**:

```
https://github.com/YOUR_ORG/YOUR_REPO/tree/reports/vault-reports
```

### Latest Graph Export

**Branch**: `graph-exports`

```bash
# Clone exports branch
git fetch origin graph-exports:graph-exports
git checkout graph-exports

# Latest exports
ls exports/
```

### Artifacts (90-day retention)

1. Go to Actions > Select workflow run
2. Scroll to "Artifacts" section
3. Click to download

---

## Troubleshooting

### Workflow Failed

**Step 1**: Check logs

```
Actions → Failed run → Click failed job → View logs
```

**Step 2**: Common fixes

```bash
# Python dependency issues
# → Workflow re-runs usually fix this (temporary GitHub issues)

# Validation errors
# → Fix the errors in your notes and push again

# Permission errors
# → Check repository settings → Actions → Permissions
```

### Validation Passes Locally but Fails in CI

**Possible causes**:

1. Different Python version (CI uses 3.12)
2. Different automation package version
3. Missing files in git

**Fix**:

```bash
# Use same Python version
python --version  # should be 3.12

# Install same dependencies
cd automation
uv sync

# Validate locally
uv run vault validate InterviewQuestions/YOUR_FILE.md
```

### Health Report Not Updated

**Check**:

1. Workflow succeeded? (Actions tab)
2. Reports committed to `reports` branch?
3. GitHub Pages enabled? (Settings → Pages)

**Force update**:

```bash
# Manually trigger workflow
gh workflow run vault-health-report.yml
```

---

## Best Practices

### Before Creating PR

```bash
# Validate your changes locally
cd automation
uv run vault validate InterviewQuestions/YOUR_CHANGES

# Fix any errors
# Push when validation passes
```

### After PR Validation Fails

1. **Don't** close PR and create new one
2. **Do** fix errors in the same PR
3. Push fixes → workflow re-runs automatically

### Regular Maintenance

**Weekly**:

- Review health report issues
- Fix broken links
- Link orphaned notes

**Monthly**:

- Review graph exports for trends
- Check missing translations
- Normalize concept notes

---

## Workflow Files

| File                      | Lines | Purpose                   |
| ------------------------- | ----- | ------------------------- |
| `validate-notes.yml`      | ~180  | PR validation             |
| `vault-health-report.yml` | ~250  | Health reporting          |
| `normalize-concepts.yml`  | ~90   | Frontmatter normalization |
| `graph-export.yml`        | ~120  | Graph exports             |

**Total**: ~640 lines of workflow automation

---

## Integration with Automation Package

All workflows use the [automation package](../automation/):

```bash
# Commands used in workflows
uv run vault validate        # Note validation
uv run vault normalize       # Frontmatter normalization
uv run vault check-translations  # Missing translations
uv run vault graph-stats     # Network statistics
uv run vault orphans         # Orphaned notes
uv run vault broken-links    # Broken links
uv run vault link-report     # Health report
uv run vault graph-export    # Graph export
```

**See**: [automation/README.md](../automation/README.md) for CLI documentation

---

## Monitoring Schedule

```
Daily 00:00 UTC     → Vault Health Report
Weekly Sun 00:00    → Graph Export
On every PR         → Note Validation
Manual as needed    → Concept Normalization
```

---

## Emergency: Disable Workflows

**Temporarily disable**:

```
Repository → Actions → Select workflow → "..." → Disable workflow
```

**Re-enable**:

```
Repository → Actions → Select workflow → "..." → Enable workflow
```

**Remove entirely**:

```bash
git rm .github/workflows/WORKFLOW_NAME.yml
git commit -m "Remove workflow"
git push
```

---

**Last Updated**: 2025-11-08
**See Also**: [.github/README.md](.github/README.md) for comprehensive documentation
