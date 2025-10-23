# Obsidian Vault Automation Pipeline Design

**Version**: 1.0
**Date**: 2025-10-23
**Status**: Design Document

---

## Overview

A comprehensive automation pipeline combining Python scripts (automated processing) and Claude Code (manual review/refactoring) with progress tracking, parallel execution, and quality assurance.

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE ORCHESTRATOR                        │
│  - Task scheduling                                              │
│  - Progress tracking                                            │
│  - Quality gates                                                │
│  - Rollback capability                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ├──────────────┬──────────────┐
                              ▼              ▼              ▼
┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐
│   STAGE 1:      │  │   STAGE 2:      │  │   STAGE 3:      │
│   ANALYZE       │  │   AUTOMATE      │  │   REVIEW        │
└─────────────────┘  └─────────────────┘  └──────────────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
       ┌────────────┐  ┌───────────┐  ┌──────────┐
       │  Python    │  │  Parallel │  │  Claude  │
       │  Scripts   │  │  Workers  │  │   Code   │
       └────────────┘  └───────────┘  └──────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │  QUALITY VALIDATION  │
                   │  - Pre-checks        │
                   │  - Post-checks       │
                   │  - Diff analysis     │
                   └──────────────────────┘
```

---

## Pipeline Stages

### Stage 1: Analysis & Planning

**Purpose**: Identify work to be done and create execution plan

**Components**:
1. **Vault Scanner**
   - Scan all notes for issues
   - Categorize by severity (CRITICAL, ERROR, WARNING, INFO)
   - Group by fix type (automated vs manual)

2. **Work Classifier**
   - Determine which issues can be automated
   - Flag which need manual review
   - Estimate effort for each category

3. **Batch Creator**
   - Split work into parallelizable batches
   - Create work packages (JSON files)
   - Set dependencies between batches

**Output**: Work packages in `pipeline/batches/`

---

### Stage 2: Automated Processing

**Purpose**: Apply Python scripts for bulk automated fixes

**Components**:
1. **Pre-validation**
   - Check current state
   - Verify prerequisites
   - Create backup/checkpoint

2. **Script Execution**
   - Run Python scripts in defined order
   - Handle errors gracefully
   - Log all changes

3. **Parallel Workers**
   - Execute independent batches simultaneously
   - Track progress per worker
   - Aggregate results

4. **Post-validation**
   - Verify changes applied correctly
   - Check for new issues introduced
   - Generate diff reports

**Output**:
- Modified files
- Change logs in `pipeline/logs/`
- Validation reports

---

### Stage 3: Manual Review & Refactoring

**Purpose**: Claude Code reviews automated changes and handles complex cases

**Components**:
1. **Review Queues**
   - Files flagged for review
   - Priority-sorted tasks
   - Context-rich work items

2. **Interactive Refinement**
   - Claude Code reviews changes
   - Makes manual corrections
   - Handles edge cases

3. **Quality Enhancement**
   - Content improvement
   - Consistency checks
   - Best practice application

**Output**:
- Refined files
- Review notes
- Quality reports

---

## Progress Tracking System

### Database Schema

```json
{
  "pipeline_run": {
    "id": "run-20251023-001",
    "started": "2025-10-23T10:00:00Z",
    "status": "in_progress",
    "total_files": 500,
    "stages": {
      "analysis": { "status": "completed", "duration": 120 },
      "automation": { "status": "in_progress", "duration": null },
      "review": { "status": "pending", "duration": null }
    }
  },
  "batches": [
    {
      "id": "batch-001",
      "type": "difficulty-tags",
      "files": 101,
      "status": "completed",
      "worker": "python-script",
      "started": "2025-10-23T10:05:00Z",
      "completed": "2025-10-23T10:06:30Z",
      "success_count": 101,
      "error_count": 0
    }
  ],
  "files": {
    "q-example--android--medium.md": {
      "status": "completed",
      "batches_applied": ["batch-001", "batch-003"],
      "issues_found": 3,
      "issues_fixed": 3,
      "needs_review": false,
      "last_modified": "2025-10-23T10:06:00Z"
    }
  }
}
```

### Progress Dashboard

**Real-time metrics**:
- Overall completion percentage
- Stage-by-stage progress
- Files processed / remaining
- Issues fixed / remaining
- Estimated time to completion
- Worker utilization
- Error rate

**Visualization**:
```
PIPELINE PROGRESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stage 1: Analysis        ████████████████████ 100% (Complete)
Stage 2: Automation      ████████████▒▒▒▒▒▒▒▒  60% (In Progress)
Stage 3: Review          ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒   0% (Pending)

Overall: ████████▒▒▒▒▒▒▒▒▒▒▒▒  40% Complete

BATCHES (6 total)
✓ batch-001: difficulty-tags       (101/101 files) [DONE]
✓ batch-002: whitespace-clean      ( 21/ 21 files) [DONE]
⟳ batch-003: concept-links         ( 45/124 files) [IN PROGRESS]
⏳ batch-004: content-generation    (  0/ 47 files) [QUEUED]
⏳ batch-005: wikilink-cleanup      (  0/ 10 files) [QUEUED]
⏳ batch-006: final-validation      (  0/500 files) [QUEUED]

WORKERS (3 active)
Worker-1: Processing batch-003 (concept-links) - 36% done
Worker-2: Idle
Worker-3: Idle

QUALITY METRICS
✓ Pass rate: 15.2% → 45.7% (+30.5%)
✓ Critical issues: 115 → 52 (-55%)
✓ Files validated: 245/500
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Parallel Execution Framework

### Worker Pool

```python
class WorkerPool:
    """Manages parallel execution of batches."""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.workers = []
        self.queue = []

    def submit_batch(self, batch: Batch, priority: int = 0):
        """Add batch to execution queue."""
        self.queue.append((priority, batch))

    def execute(self):
        """Execute batches in parallel."""
        # Sort by priority
        self.queue.sort(key=lambda x: x[0], reverse=True)

        # Execute with max_workers parallelism
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for priority, batch in self.queue:
                if batch.can_run():  # Check dependencies
                    future = executor.submit(self._execute_batch, batch)
                    futures.append((batch.id, future))

            # Wait and collect results
            for batch_id, future in futures:
                result = future.result()
                self._update_progress(batch_id, result)
```

### Dependency Management

```yaml
# pipeline/dependencies.yaml
batches:
  difficulty-tags:
    depends_on: []
    can_parallel: true

  whitespace-clean:
    depends_on: []
    can_parallel: true

  concept-links:
    depends_on: [difficulty-tags]  # Needs clean YAML first
    can_parallel: true
    split_into: 6  # Can split into 6 parallel workers

  content-generation:
    depends_on: [concept-links]
    can_parallel: false  # Sequential due to LLM rate limits

  final-validation:
    depends_on: [difficulty-tags, whitespace-clean, concept-links, content-generation]
    can_parallel: true
```

### Execution Graph

```
START
  │
  ├─→ [difficulty-tags] ────┐
  │                          │
  ├─→ [whitespace-clean] ───┼─→ [concept-links] ─→ [content-generation]
  │                          │         │                    │
  └──────────────────────────┘         └────────────────────┴─→ [final-validation] → END
```

---

## Quality Assurance Layers

### Layer 1: Pre-execution Validation

**Before any script runs**:
```python
def pre_validate(batch: Batch) -> ValidationResult:
    """Validate before executing batch."""
    checks = [
        check_files_exist(batch.files),
        check_yaml_parseable(batch.files),
        check_no_locks(batch.files),
        check_dependencies_met(batch),
        check_disk_space(),
    ]
    return ValidationResult(checks)
```

### Layer 2: Execution Monitoring

**During script execution**:
- Track changes to each file
- Log all operations
- Detect anomalies (e.g., file size changes >50%)
- Auto-rollback on critical errors

### Layer 3: Post-execution Validation

**After script completes**:
```python
def post_validate(batch: Batch, results: BatchResult) -> ValidationReport:
    """Validate results after batch execution."""
    report = ValidationReport(batch.id)

    # Check all files still parseable
    report.add_check("yaml_integrity", validate_yaml_integrity(results.files))

    # Check no required fields lost
    report.add_check("field_preservation", check_fields_preserved(results.files))

    # Check improvements vs regressions
    before = analyze_files(results.files, results.backup)
    after = analyze_files(results.files)
    report.add_metric("improvement", calculate_improvement(before, after))

    # Run full validation on sample
    sample = random.sample(results.files, min(10, len(results.files)))
    report.add_check("full_validation", run_full_validation(sample))

    return report
```

### Layer 4: Manual Review Gate

**Before finalizing**:
- Claude Code reviews sample of changes
- Flags suspicious changes
- Approves or rejects batch
- Provides improvement suggestions

### Layer 5: Diff Analysis

**Change comparison**:
```python
def analyze_diffs(before: str, after: str) -> DiffAnalysis:
    """Analyze what changed and why."""
    diff = unified_diff(before.split('\n'), after.split('\n'))

    return DiffAnalysis(
        lines_added=count_additions(diff),
        lines_removed=count_removals(diff),
        yaml_changes=analyze_yaml_changes(before, after),
        content_changes=analyze_content_changes(before, after),
        risk_level=assess_risk(before, after),
        requires_review=should_review(before, after)
    )
```

---

## Pipeline Configuration

### Main Config (`pipeline/config.yaml`)

```yaml
pipeline:
  name: "Obsidian Vault Automation"
  version: "1.0"

  execution:
    max_parallel_workers: 4
    checkpoint_frequency: 10  # Save progress every 10 files
    auto_rollback: true
    dry_run_first: true

  quality:
    min_pass_rate: 0.95  # 95% files must pass validation
    max_error_rate: 0.05  # Max 5% errors allowed
    require_manual_review:
      - content-generation  # Always review generated content
      - complex-refactoring
    sample_size_for_review: 10  # Review 10 random files per batch

  stages:
    analysis:
      enabled: true
      timeout: 300  # 5 minutes

    automation:
      enabled: true
      timeout: 3600  # 1 hour
      scripts_dir: "scripts"

    review:
      enabled: true
      timeout: 7200  # 2 hours
      claude_code_integration: true

  logging:
    level: "INFO"
    file: "pipeline/logs/pipeline.log"
    console: true

  progress_tracking:
    database: "pipeline/progress.db"
    update_interval: 5  # Update progress every 5 seconds
    dashboard_port: 8080  # Web dashboard

  rollback:
    create_backups: true
    backup_dir: "pipeline/backups"
    max_backups: 5
```

### Batch Templates

**Python Script Batch** (`pipeline/batch_templates/python_script.yaml`):
```yaml
type: python_script
executor: python
timeout: 600

pre_checks:
  - yaml_parseable
  - files_exist
  - no_file_locks

execution:
  script: "scripts/{script_name}.py"
  args:
    - "--status=reviewed"
    - "--output=pipeline/results/{batch_id}.json"

post_checks:
  - yaml_still_parseable
  - no_data_loss
  - improvements_detected

on_error:
  action: rollback
  notify: true
```

**Claude Code Review Batch** (`pipeline/batch_templates/claude_review.yaml`):
```yaml
type: claude_code_review
executor: claude_code
timeout: 7200

inputs:
  work_package: "pipeline/review_queue/{batch_id}.json"
  context_files:
    - "TAXONOMY.md"
    - "AGENTS.md"
    - "CLAUDE.md"

task_description: |
  Review the files in the work package and:
  1. Verify automated changes are correct
  2. Fix any issues found
  3. Improve content quality where needed
  4. Add missing translations if required
  5. Report completion with summary

output:
  report: "pipeline/review_reports/{batch_id}.md"
  changes_log: "pipeline/review_reports/{batch_id}-changes.json"

quality_gates:
  min_files_reviewed: 0.9  # Must review 90%+ of assigned files
  require_summary: true
```

---

## Implementation Components

### 1. Pipeline Orchestrator

**File**: `pipeline/orchestrator.py`

```python
class PipelineOrchestrator:
    """Main pipeline orchestrator."""

    def __init__(self, config_path: str):
        self.config = load_config(config_path)
        self.progress = ProgressTracker(self.config.progress_tracking.database)
        self.worker_pool = WorkerPool(self.config.execution.max_parallel_workers)
        self.quality_gate = QualityGate(self.config.quality)

    def run(self):
        """Execute the pipeline."""
        run_id = self.progress.start_run()

        try:
            # Stage 1: Analysis
            work_packages = self.stage_analysis()

            # Stage 2: Automation
            automation_results = self.stage_automation(work_packages)

            # Stage 3: Review
            review_results = self.stage_review(automation_results)

            # Final validation
            final_report = self.final_validation(review_results)

            self.progress.complete_run(run_id, final_report)

        except Exception as e:
            self.handle_error(run_id, e)
            if self.config.execution.auto_rollback:
                self.rollback(run_id)
```

### 2. Progress Tracker

**File**: `pipeline/progress_tracker.py`

```python
class ProgressTracker:
    """Tracks pipeline execution progress."""

    def __init__(self, db_path: str):
        self.db = sqlite3.connect(db_path)
        self.init_schema()

    def start_batch(self, batch_id: str, total_files: int):
        """Start tracking a batch."""

    def update_file(self, batch_id: str, filepath: str, status: str):
        """Update status of a single file."""

    def get_progress(self) -> ProgressSnapshot:
        """Get current progress snapshot."""
        return ProgressSnapshot(
            overall_percent=self.calculate_overall_progress(),
            stage_progress=self.get_stage_progress(),
            batch_progress=self.get_batch_progress(),
            worker_status=self.get_worker_status(),
            quality_metrics=self.get_quality_metrics()
        )
```

### 3. Quality Gate

**File**: `pipeline/quality_gate.py`

```python
class QualityGate:
    """Enforces quality standards."""

    def check_batch_results(self, batch: Batch, results: BatchResult) -> GateDecision:
        """Determine if batch results meet quality standards."""

        decision = GateDecision()

        # Check pass rate
        if results.success_rate < self.config.min_pass_rate:
            decision.reject(f"Pass rate {results.success_rate} < {self.config.min_pass_rate}")

        # Check error rate
        if results.error_rate > self.config.max_error_rate:
            decision.reject(f"Error rate {results.error_rate} > {self.config.max_error_rate}")

        # Check for regressions
        if results.regressions > 0:
            decision.warn(f"Introduced {results.regressions} regressions")

        return decision
```

### 4. Dashboard Server

**File**: `pipeline/dashboard.py`

```python
from flask import Flask, render_template, jsonify

app = Flask(__name__)
tracker = None

@app.route('/')
def dashboard():
    """Render main dashboard."""
    return render_template('dashboard.html')

@app.route('/api/progress')
def get_progress():
    """API endpoint for current progress."""
    return jsonify(tracker.get_progress())

@app.route('/api/batches')
def get_batches():
    """API endpoint for batch status."""
    return jsonify(tracker.get_all_batches())

def start_dashboard(progress_tracker: ProgressTracker, port: int = 8080):
    """Start the web dashboard."""
    global tracker
    tracker = progress_tracker
    app.run(port=port, debug=False)
```

---

## Usage Examples

### Example 1: Run Full Pipeline

```bash
# Run complete pipeline with default config
python pipeline/orchestrator.py run

# Run with custom config
python pipeline/orchestrator.py run --config=pipeline/custom_config.yaml

# Dry run first
python pipeline/orchestrator.py run --dry-run

# Resume from checkpoint
python pipeline/orchestrator.py resume --run-id=run-20251023-001
```

### Example 2: Run Specific Stage

```bash
# Run only analysis stage
python pipeline/orchestrator.py stage analysis

# Run only automation stage
python pipeline/orchestrator.py stage automation --batches=batch-001,batch-002

# Run only review stage
python pipeline/orchestrator.py stage review
```

### Example 3: Monitor Progress

```bash
# Start dashboard server
python pipeline/dashboard.py --port=8080

# View in browser: http://localhost:8080

# CLI progress monitor
python pipeline/monitor.py --watch
```

### Example 4: Create Custom Batch

```yaml
# pipeline/batches/custom_batch.yaml
id: custom-subtopic-fix
type: python_script
priority: 10

files:
  - query: "status:reviewed AND topic:android"
    max_count: 50

execution:
  script: scripts/fix_subtopics.py
  parallel: true
  workers: 3

quality:
  post_validate: true
  require_review: false
```

---

## Rollback & Recovery

### Automatic Rollback

```python
class RollbackManager:
    """Manages rollback of failed batches."""

    def create_checkpoint(self, batch_id: str, files: List[str]):
        """Create backup before batch execution."""
        checkpoint_dir = f"pipeline/checkpoints/{batch_id}"
        for file in files:
            backup_path = checkpoint_dir / file
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, backup_path)

    def rollback(self, batch_id: str):
        """Restore files from checkpoint."""
        checkpoint_dir = f"pipeline/checkpoints/{batch_id}"
        for backup_file in checkpoint_dir.rglob('*.md'):
            original_path = get_original_path(backup_file)
            shutil.copy2(backup_file, original_path)
            logger.info(f"Restored {original_path}")
```

### Manual Recovery

```bash
# List available checkpoints
python pipeline/orchestrator.py checkpoints list

# Restore specific checkpoint
python pipeline/orchestrator.py checkpoints restore --batch-id=batch-003

# Restore entire run
python pipeline/orchestrator.py checkpoints restore --run-id=run-20251023-001
```

---

## Integration Points

### Claude Code Integration

**Work Package Format** (`pipeline/review_queue/review-001.json`):
```json
{
  "review_id": "review-001",
  "created": "2025-10-23T12:00:00Z",
  "priority": "high",
  "assigned_to": "claude_code",
  "files": [
    {
      "path": "40-Android/q-example--android--medium.md",
      "issues": [
        {
          "type": "missing_content",
          "severity": "critical",
          "description": "Missing Russian question section",
          "suggested_action": "Generate Russian translation of English question"
        }
      ],
      "context": {
        "title": "Example Android Question",
        "difficulty": "medium",
        "has_en_answer": true,
        "has_ru_answer": false
      }
    }
  ],
  "instructions": "Generate missing Russian translations for all files",
  "deadline": "2025-10-23T18:00:00Z"
}
```

### Python Script Integration

**Script Requirements**:
```python
#!/usr/bin/env python3
"""
Pipeline-compatible script template.
Must implement:
- JSON work package input
- Progress reporting
- Error handling
- Result output
"""

import argparse
import json
from pathlib import Path

def process_batch(work_package: dict) -> dict:
    """Process the work package."""
    results = {
        "batch_id": work_package["batch_id"],
        "files_processed": 0,
        "files_succeeded": 0,
        "files_failed": 0,
        "errors": [],
        "changes": []
    }

    for file_info in work_package["files"]:
        try:
            # Process file
            result = process_file(file_info)
            results["files_processed"] += 1
            if result.success:
                results["files_succeeded"] += 1
            else:
                results["files_failed"] += 1
                results["errors"].append(result.error)
            results["changes"].append(result.changes)
        except Exception as e:
            results["files_failed"] += 1
            results["errors"].append(str(e))

    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-package", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    # Load work package
    with open(args.work_package) as f:
        work_package = json.load(f)

    # Process
    results = process_batch(work_package)

    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)

    # Exit with appropriate code
    sys.exit(0 if results["files_failed"] == 0 else 1)

if __name__ == '__main__':
    main()
```

---

## Next Steps

1. **Implement Core Components**
   - Pipeline orchestrator
   - Progress tracker
   - Quality gate
   - Dashboard

2. **Create Batch Definitions**
   - Define all required batches
   - Set dependencies
   - Configure quality thresholds

3. **Integrate Existing Scripts**
   - Adapt scripts to pipeline format
   - Add progress reporting
   - Standardize error handling

4. **Test Pipeline**
   - Dry run on sample data
   - Validate rollback mechanism
   - Verify quality gates

5. **Deploy & Monitor**
   - Run on full vault
   - Monitor dashboard
   - Collect metrics

---

**Status**: DESIGN COMPLETE - READY FOR IMPLEMENTATION
