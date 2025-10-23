# Obsidian Vault Automation Pipeline - User Guide

**Version**: 1.0
**Date**: 2025-10-23
**Status**: Ready for Use

---

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install pyyaml rich flask
```

### 2. Run Pipeline

```bash
# Full pipeline execution
python pipeline/orchestrator.py run

# Dry run first (recommended)
python pipeline/orchestrator.py run --dry-run
```

### 3. Review Results

```bash
# Check created work packages
ls pipeline/batches/

# Check automation results
ls pipeline/results/

# Check review tasks for Claude Code
ls pipeline/review_queue/
```

---

## Pipeline Overview

The pipeline consists of **3 main stages**:

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  ANALYSIS   │ → │  AUTOMATION  │ → │   REVIEW    │
│  (Python)   │    │  (Python +   │    │  (Claude    │
│             │    │   Parallel)  │    │   Code)     │
└─────────────┘    └──────────────┘    └─────────────┘
```

### Stage 1: Analysis
- **Purpose**: Scan vault for issues and create work packages
- **Output**: JSON work packages in `pipeline/batches/`
- **Duration**: ~5 minutes
- **Automated**: Yes

### Stage 2: Automation
- **Purpose**: Execute Python scripts for automated fixes
- **Output**: Results in `pipeline/results/`
- **Duration**: 1-2 hours depending on vault size
- **Automated**: Yes (with validation gates)

### Stage 3: Review
- **Purpose**: Claude Code reviews changes and handles complex cases
- **Output**: Review tasks in `pipeline/review_queue/`
- **Duration**: Variable (manual review)
- **Automated**: No (requires human/Claude Code interaction)

---

## Configuration

### Main Config File: `pipeline/config.yaml`

Key settings you can adjust:

```yaml
execution:
  max_parallel_workers: 4  # Number of parallel processes
  checkpoint_frequency: 10  # Save progress every N files
  auto_rollback: true  # Auto-rollback on errors
  dry_run_first: true  # Always preview before applying

quality:
  min_pass_rate: 0.95  # 95% files must pass validation
  max_error_rate: 0.05  # Max 5% errors per batch
  max_regressions: 0  # Zero tolerance for making things worse

  require_manual_review:
    - content-generation  # Always review generated content
    - complex-refactoring
    - translation
```

---

## Work Package System

### What is a Work Package?

A work package is a JSON file defining a batch of work:

```json
{
  "id": "difficulty-tags",
  "type": "python_script",
  "priority": 100,
  "file_count": 101,
  "files": ["40-Android/q-example--android--medium.md", "..."],
  "script": "restore_difficulty_tags.py",
  "description": "Restore missing difficulty tags",
  "can_parallel": false,
  "requires_review": false
}
```

### Types of Work Packages

**1. Python Script Packages**
- Automated fixes via Python scripts
- Fast, bulk operations
- Examples: tag restoration, whitespace cleanup, YAML fixes

**2. Claude Code Review Packages**
- Manual review and refinement
- Complex operations requiring judgment
- Examples: content generation, translation, concept linking

### Package Priority

Packages execute in priority order (higher = first):

- **100**: Critical fixes (difficulty tags, YAML structure)
- **90**: High priority (whitespace, formatting)
- **80**: Medium priority (concept links)
- **70**: Low priority (content generation)

---

## Parallel Execution

### How It Works

The pipeline can run multiple batches in parallel:

```
Worker 1: [whitespace-clean]    (21 files)  ▓▓▓▓▓▓▓▓▓▓░░░░░░  60%
Worker 2: [concept-links-1]     (20 files)  ▓▓▓▓▓▓░░░░░░░░░░  40%
Worker 3: [concept-links-2]     (20 files)  ▓▓▓▓▓▓░░░░░░░░░░  40%
Worker 4: Idle
```

### Configuring Parallelism

```yaml
# config.yaml
execution:
  max_parallel_workers: 4  # Adjust based on CPU cores

# Work package
{
  "can_parallel": true,
  "split_into": 6  # Split into 6 parallel sub-tasks
}
```

### Dependencies

Some packages must wait for others:

```yaml
# pipeline/dependencies.yaml
batches:
  concept-links:
    depends_on: [difficulty-tags]  # Must run after difficulty-tags
```

---

## Quality Gates

### Pre-execution Validation

Before each batch runs:
- ✓ All files exist and are readable
- ✓ YAML is parseable
- ✓ No file locks
- ✓ Dependencies met
- ✓ Sufficient disk space

### Post-execution Validation

After each batch completes:
- ✓ All files still parseable
- ✓ No required fields lost
- ✓ Improvements detected (not regressions)
- ✓ Sample validation (10 random files)

### Quality Metrics

```
Pass Rate:    95/100 files ✓ (>95% required)
Error Rate:   2/100 files  ✓ (<5% allowed)
Regressions:  0 issues     ✓ (0 tolerance)
```

If any metric fails, the batch is **rejected** and **rolled back**.

---

## Rollback & Recovery

### Automatic Rollback

The pipeline creates checkpoints before each batch:

```
pipeline/checkpoints/
  difficulty-tags/
    40-Android/
      q-example--android--medium.md  (backup)
      q-another--android--easy.md    (backup)
```

If a batch fails quality gates, files are automatically restored.

### Manual Rollback

```bash
# List available checkpoints
ls pipeline/checkpoints/

# Restore specific batch
python pipeline/orchestrator.py rollback --batch-id=concept-links

# Restore entire run
python pipeline/orchestrator.py rollback --run-id=run-20251023-001
```

---

## Progress Tracking

### Real-time Progress

The pipeline tracks progress in SQLite database (`pipeline/progress.db`):

```sql
-- Current progress
SELECT
  batch_id,
  status,
  files_processed,
  files_total,
  (files_processed * 100.0 / files_total) as percent
FROM batches
WHERE run_id = 'run-20251023-001';
```

### Progress Dashboard (Optional)

```bash
# Start web dashboard
python pipeline/dashboard.py

# Open in browser
http://localhost:8080
```

Shows:
- Overall pipeline progress
- Per-batch progress
- Worker status
- Quality metrics
- Recent errors

---

## Claude Code Integration

### Review Queue System

After automation, review tasks are created in `pipeline/review_queue/`:

```json
{
  "review_id": "review-001",
  "priority": "high",
  "assigned_to": "claude_code",
  "files": [
    {
      "path": "40-Android/q-example--android--medium.md",
      "issues": [
        {
          "type": "missing_content",
          "severity": "critical",
          "description": "Missing Russian question section"
        }
      ]
    }
  ],
  "instructions": "Generate missing Russian translations"
}
```

### How to Process Review Tasks

1. **Find review task**:
   ```bash
   ls pipeline/review_queue/
   ```

2. **Read the task**:
   ```bash
   cat pipeline/review_queue/review-001.json
   ```

3. **Process files** (as Claude Code):
   - Open each file listed
   - Address the issues described
   - Follow the instructions
   - Make improvements

4. **Mark complete**:
   ```bash
   mv pipeline/review_queue/review-001.json pipeline/review_reports/review-001-complete.json
   ```

---

## Common Workflows

### Workflow 1: Fix Simple Issues

For simple automated fixes (tags, whitespace, formatting):

```bash
# 1. Analyze
python pipeline/orchestrator.py stage analysis

# 2. Review work packages
cat pipeline/batches/*.json

# 3. Run automation
python pipeline/orchestrator.py stage automation

# 4. Verify results
python validate_note.py --sample=10
```

### Workflow 2: Content Generation

For complex tasks requiring Claude Code:

```bash
# 1. Create work package manually
cat > pipeline/batches/custom-content.json <<EOF
{
  "id": "custom-content",
  "type": "claude_code_review",
  "files": ["40-Android/q-missing-content--android--medium.md"],
  "instructions": "Generate missing Russian translation"
}
EOF

# 2. Create review task
python pipeline/orchestrator.py stage review

# 3. Process with Claude Code
cat pipeline/review_queue/review-custom-content.json
# ... work on files ...

# 4. Mark complete
mv pipeline/review_queue/review-custom-content.json \\
   pipeline/review_reports/review-custom-content-complete.json
```

### Workflow 3: Incremental Pipeline

Process vault in stages with validation between:

```bash
# Stage 1: Quick wins (automated)
python pipeline/orchestrator.py run --batches=difficulty-tags,whitespace-clean

# Validate
python analyze_reviewed.py

# Stage 2: Concept links (parallel Claude Code)
python pipeline/orchestrator.py run --batches=concept-links

# Validate
python analyze_reviewed.py

# Stage 3: Content generation (sequential Claude Code)
python pipeline/orchestrator.py run --batches=content-generation

# Final validation
python analyze_reviewed.py
```

---

## Monitoring & Debugging

### Log Files

**Main pipeline log**: `pipeline/logs/pipeline.log`
```
2025-10-23 10:00:00 INFO Pipeline started: run-20251023-001
2025-10-23 10:00:05 INFO Stage 1 (analysis) completed: 6 work packages created
2025-10-23 10:00:10 INFO Batch difficulty-tags started: 101 files
2025-10-23 10:01:30 INFO Batch difficulty-tags completed: 101/101 succeeded
2025-10-23 10:01:35 ERROR Batch concept-links failed: quality gate failure
2025-10-23 10:01:36 INFO Rolling back batch concept-links
```

**Per-batch logs**: `pipeline/logs/batch-{batch-id}.log`

### Error Handling

When errors occur:

1. **Check logs**: `tail -f pipeline/logs/pipeline.log`
2. **Inspect results**: `cat pipeline/results/{batch-id}-result.json`
3. **Review checkpoint**: `ls pipeline/checkpoints/{batch-id}/`
4. **Decide**:
   - Fix issue and re-run batch
   - Rollback and investigate
   - Skip batch and continue

### Common Issues

**Issue**: "YAML parsing error"
```bash
# Solution: Validate YAML before running pipeline
python scripts/validate_yaml.py 40-Android/
```

**Issue**: "File locked"
```bash
# Solution: Close Obsidian or use --force flag
python pipeline/orchestrator.py run --force
```

**Issue**: "Quality gate failed"
```bash
# Solution: Review what changed
cat pipeline/results/{batch-id}-result.json
diff pipeline/checkpoints/{batch-id}/file.md 40-Android/file.md
```

---

## Best Practices

### 1. Always Dry Run First

```bash
python pipeline/orchestrator.py run --dry-run
```

Review what would happen before applying changes.

### 2. Small Batches

Start with small batches to validate:

```bash
# Test on 10 files first
python pipeline/orchestrator.py run --limit=10
```

### 3. Checkpoint Frequently

```yaml
# config.yaml
execution:
  checkpoint_frequency: 10  # Save every 10 files
```

### 4. Monitor Progress

```bash
# Watch progress in real-time
watch -n 5 'cat pipeline/progress.db | sqlite3 -column "SELECT * FROM batches"'
```

### 5. Version Control

```bash
# Commit before running pipeline
git add -A
git commit -m "Pre-pipeline checkpoint"

# Run pipeline
python pipeline/orchestrator.py run

# Review changes
git diff

# Commit or rollback
git commit -am "Pipeline changes"
# OR
git reset --hard HEAD
```

### 6. Review Samples

Even for automated batches, spot-check samples:

```bash
# Review 5 random files from batch
python -c "import random, json
files = json.load(open('pipeline/results/difficulty-tags-result.json'))['changes']
for f in random.sample(files, 5):
    print(f['file'])"
```

---

## Performance Tuning

### Optimize for Speed

```yaml
execution:
  max_parallel_workers: 8  # Use more workers
  checkpoint_frequency: 50  # Checkpoint less often

quality:
  sample_size_for_review: 5  # Review fewer samples
```

### Optimize for Safety

```yaml
execution:
  max_parallel_workers: 1  # Sequential execution
  checkpoint_frequency: 1  # Checkpoint every file

quality:
  sample_size_for_review: 20  # Review more samples
  full_validation_sample: 50
```

---

## Extending the Pipeline

### Add Custom Batch Type

1. **Create work package template**:
   ```json
   {
     "id": "my-custom-fix",
     "type": "python_script",
     "script": "my_script.py",
     "files": ["..."],
     "custom_config": {
       "option1": "value1"
     }
   }
   ```

2. **Write script** (`scripts/my_script.py`):
   ```python
   #!/usr/bin/env python3
   import argparse
   import json

   def main():
       parser = argparse.ArgumentParser()
       parser.add_argument('--work-package', required=True)
       parser.add_argument('--output', required=True)
       args = parser.parse_args()

       # Load work package
       with open(args.work_package) as f:
           pkg = json.load(f)

       # Process files
       results = process_files(pkg['files'], pkg['custom_config'])

       # Save results
       with open(args.output, 'w') as f:
           json.dump(results, f, indent=2)

   if __name__ == '__main__':
       main()
   ```

3. **Add to pipeline config**:
   ```yaml
   # config.yaml
   stages:
     automation:
       custom_scripts:
         - my_script.py
   ```

---

## Troubleshooting

### Pipeline Won't Start

```bash
# Check Python version
python3 --version  # Must be 3.8+

# Check dependencies
pip list | grep -E "(pyyaml|rich|flask)"

# Check config
python -c "import yaml; yaml.safe_load(open('pipeline/config.yaml'))"
```

### Batch Stuck

```bash
# Check process
ps aux | grep python | grep pipeline

# Kill if needed
pkill -f "pipeline/orchestrator"

# Resume from checkpoint
python pipeline/orchestrator.py resume --run-id=run-20251023-001
```

### Out of Memory

```yaml
# Reduce parallelism
execution:
  max_parallel_workers: 2

# Process fewer files per batch
  batch_size: 20
```

---

## FAQ

**Q: Can I run the pipeline on a subset of files?**

A: Yes, modify the work package to include only specific files:
```json
{
  "files": ["40-Android/q-specific-file--android--medium.md"]
}
```

**Q: How do I skip a batch?**

A: Remove it from `pipeline/batches/` or set priority to 0.

**Q: Can I pause the pipeline?**

A: Yes, press Ctrl+C. Resume with:
```bash
python pipeline/orchestrator.py resume --run-id=<run-id>
```

**Q: What if I want to review ALL changes, not samples?**

A: Set in config:
```yaml
quality:
  require_manual_review: ["*"]  # All batches require review
```

**Q: How do I see what changed?**

A: Check the diff in results:
```bash
cat pipeline/results/{batch-id}-result.json | jq '.changes'
```

---

## Summary

The pipeline provides:

✓ **Automated processing** for bulk fixes
✓ **Parallel execution** for speed
✓ **Quality gates** to prevent regressions
✓ **Progress tracking** for visibility
✓ **Rollback capability** for safety
✓ **Claude Code integration** for complex tasks

**Recommended workflow**:
1. Run analysis stage
2. Review work packages
3. Run automation (dry-run first)
4. Validate results
5. Process review tasks with Claude Code
6. Final validation

---

**For More Information**:
- Design: `PIPELINE-DESIGN.md`
- Config: `pipeline/config.yaml`
- Examples: `pipeline/templates/`
- Logs: `pipeline/logs/`

**Status**: Ready for production use
