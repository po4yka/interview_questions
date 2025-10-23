# Autonomous Review System Design

**Version**: 2.0
**Purpose**: Fully autonomous review orchestration with unlimited runtime
**User Command**: "Start review" → Complete automation

---

## Overview

A self-managing system where Claude Code (the coordinator) launches and manages sub-agents to complete all vault work autonomously. The user only needs to initiate and monitor progress.

### Key Principles

1. **One-Command Start**: User says "start review" → system runs to completion
2. **Fully Autonomous**: No user intervention required during execution
3. **Unlimited Runtime**: Can run for hours/days with progress persistence
4. **Self-Managing**: Coordinator spawns, monitors, validates, and corrects sub-agents
5. **Resume Capability**: Can pause/resume at any checkpoint
6. **Quality Assurance**: Self-validates and auto-corrects issues

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  CLAUDE CODE (COORDINATOR)                      │
│  - Task planning                                                │
│  - Sub-agent spawning                                           │
│  - Progress tracking                                            │
│  - Quality validation                                           │
│  - Error recovery                                               │
│  - Result aggregation                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Spawns & manages
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SUB-AGENT POOL (1-10)                       │
│                                                                 │
│  Agent-1: [concept-links-1]    Files 1-20   [RUNNING]          │
│  Agent-2: [concept-links-2]    Files 21-40  [RUNNING]          │
│  Agent-3: [content-gen-1]      Files 1-10   [QUEUED]           │
│  Agent-4: [content-gen-2]      Files 11-20  [QUEUED]           │
│  Agent-5: [validation]         All files    [PENDING]          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Results
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROGRESS DATABASE                            │
│  - Task status tracking                                         │
│  - File-level progress                                          │
│  - Quality metrics                                              │
│  - Error logs                                                   │
│  - Checkpoints                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Coordinator (Claude Code) Responsibilities

### 1. Task Planning

**Input**: Current vault state
**Process**:
1. Analyze all files needing work
2. Categorize by issue type
3. Determine dependencies
4. Create execution plan with priorities
5. Split work into parallelizable batches

**Output**: Task graph with sub-agent assignments

### 2. Sub-Agent Spawning

**Strategy**: Launch optimal number of sub-agents based on:
- Work volume
- Task complexity
- Dependencies
- Available resources

```python
# Coordinator spawns sub-agents
coordinator.spawn_agents([
    {
        'agent_id': 'concepts-1',
        'task_type': 'add_concept_links',
        'files': ['file1.md', 'file2.md', ...],
        'count': 20,
        'priority': 80
    },
    {
        'agent_id': 'concepts-2',
        'task_type': 'add_concept_links',
        'files': ['file21.md', 'file22.md', ...],
        'count': 20,
        'priority': 80
    },
    # ... up to 10 agents
])
```

### 3. Progress Monitoring

**Real-time tracking**:
- Monitor each sub-agent's progress
- Track files processed/remaining
- Record quality metrics
- Log errors and warnings
- Update progress database

**Dashboard view**:
```
AUTONOMOUS REVIEW SYSTEM - RUNNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Started: 2025-10-23 10:00:00
Runtime: 2h 34m
Status: IN PROGRESS

PHASE 1: CONCEPT LINKS (COMPLETE)
  ✓ concepts-1: 20/20 files [100%] - 2 concepts/file avg
  ✓ concepts-2: 20/20 files [100%] - 2 concepts/file avg
  ✓ concepts-3: 20/20 files [100%] - 3 concepts/file avg
  ✓ concepts-4: 20/20 files [100%] - 2 concepts/file avg
  ✓ concepts-5: 20/20 files [100%] - 2 concepts/file avg
  ✓ concepts-6: 24/24 files [100%] - 2 concepts/file avg

PHASE 2: CONTENT GENERATION (IN PROGRESS)
  ⟳ content-gen-1: 7/12 files [58%] - Generating Russian translations
  ⟳ content-gen-2: 5/12 files [42%] - Generating questions
  ⟳ content-gen-3: 4/12 files [33%] - Generating complete content
  ⏳ content-gen-4: 0/11 files [0%] - Queued

PHASE 3: QUALITY VALIDATION (PENDING)
  ⏳ validation-1: 0/66 files [0%] - Final validation pass

OVERALL PROGRESS
  Files processed: 114/175 (65%)
  Quality score: 87.3% → 94.1% (+6.8%)
  Critical issues: 52 → 8 (-85%)
  Estimated completion: 45 minutes

RECENT ACTIVITY
  10:34:12 - concepts-6 completed batch (24 files)
  10:34:15 - content-gen-1 processing q-example--android--medium.md
  10:34:20 - content-gen-2 processing q-another--android--hard.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4. Quality Validation

**After each sub-agent completes**:
```python
def validate_sub_agent_results(agent_id: str, results: Dict):
    """Validate sub-agent output and auto-correct if needed."""

    validation = {
        'yaml_integrity': check_yaml_valid(results.files),
        'required_fields': check_fields_present(results.files),
        'content_quality': assess_content(results.files),
        'improvements': measure_improvements(results.files),
        'regressions': detect_regressions(results.files)
    }

    if validation['regressions'] > 0:
        # Auto-correction: spawn repair agent
        coordinator.spawn_repair_agent(agent_id, validation['issues'])

    if validation['yaml_integrity'] < 1.0:
        # Auto-correction: fix YAML
        coordinator.spawn_yaml_fixer(results.files)

    return validation
```

### 5. Error Recovery

**Automatic handling**:
- **Sub-agent timeout**: Respawn with smaller batch
- **Sub-agent error**: Log, checkpoint, spawn repair agent
- **Quality gate failure**: Rollback and retry with corrections
- **File corruption**: Restore from checkpoint

**Recovery strategies**:
```python
class ErrorRecovery:
    """Autonomous error recovery."""

    def handle_agent_failure(self, agent_id: str, error: Exception):
        """Handle sub-agent failure."""
        # Log error
        self.log_error(agent_id, error)

        # Determine recovery strategy
        if isinstance(error, TimeoutError):
            # Split batch and retry
            smaller_batches = self.split_batch(agent_id, factor=2)
            for batch in smaller_batches:
                self.spawn_agent(batch)

        elif isinstance(error, YAMLError):
            # Spawn YAML repair agent
            self.spawn_repair_agent('yaml-fixer', agent_id)

        else:
            # Generic retry with backoff
            self.retry_agent(agent_id, delay=60)
```

### 6. Result Aggregation

**Final steps**:
1. Collect all sub-agent results
2. Aggregate statistics
3. Generate comprehensive report
4. Present to user

---

## Sub-Agent Specifications

### Agent Template

Each sub-agent receives:

```json
{
  "agent_id": "concepts-1",
  "task_type": "add_concept_links",
  "work_package": {
    "files": [
      {
        "path": "40-Android/q-example--android--medium.md",
        "issues": ["missing_concept_links"],
        "context": {
          "title": "Example Question",
          "difficulty": "medium",
          "en_answer_preview": "This is about..."
        }
      }
    ]
  },
  "instructions": "Add 1-3 relevant concept links to each note's answer sections (EN and RU)",
  "quality_requirements": {
    "min_concepts_per_file": 1,
    "max_concepts_per_file": 3,
    "validate_links_exist": false,
    "preserve_all_content": true
  },
  "timeout": 1800,
  "checkpoint_file": "progress/concepts-1.checkpoint"
}
```

### Agent Types

**1. Concept Link Agents** (parallelizable)
- Task: Add 1-3 `[[c-concept-name]]` links
- Batch size: 20 files
- Parallel agents: 6
- Duration: 15-20 minutes each

**2. Content Generation Agents** (parallelizable with rate limits)
- Task: Generate missing questions/translations
- Batch size: 12 files
- Parallel agents: 4
- Duration: 30-45 minutes each

**3. Validation Agents** (sequential)
- Task: Final quality check
- Batch size: 66 files
- Parallel agents: 1
- Duration: 10-15 minutes

**4. Repair Agents** (on-demand)
- Task: Fix issues found by validation
- Spawned automatically when needed
- Duration: Variable

---

## Progress Persistence

### SQLite Database Schema

```sql
-- Main review session
CREATE TABLE review_sessions (
    session_id TEXT PRIMARY KEY,
    started_at TIMESTAMP,
    status TEXT, -- running, paused, completed, failed
    total_files INTEGER,
    completed_files INTEGER,
    current_phase TEXT
);

-- Sub-agent tracking
CREATE TABLE sub_agents (
    agent_id TEXT PRIMARY KEY,
    session_id TEXT,
    task_type TEXT,
    status TEXT, -- queued, running, completed, failed
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    files_assigned INTEGER,
    files_completed INTEGER,
    quality_score REAL,
    FOREIGN KEY (session_id) REFERENCES review_sessions(session_id)
);

-- File-level progress
CREATE TABLE file_progress (
    file_path TEXT PRIMARY KEY,
    session_id TEXT,
    agent_id TEXT,
    status TEXT, -- pending, processing, completed, failed
    issues_before INTEGER,
    issues_after INTEGER,
    last_modified TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES review_sessions(session_id),
    FOREIGN KEY (agent_id) REFERENCES sub_agents(agent_id)
);

-- Checkpoints
CREATE TABLE checkpoints (
    checkpoint_id TEXT PRIMARY KEY,
    session_id TEXT,
    created_at TIMESTAMP,
    files_backed_up INTEGER,
    backup_path TEXT,
    FOREIGN KEY (session_id) REFERENCES review_sessions(session_id)
);

-- Quality metrics
CREATE TABLE quality_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    timestamp TIMESTAMP,
    pass_rate REAL,
    critical_issues INTEGER,
    errors INTEGER,
    warnings INTEGER,
    FOREIGN KEY (session_id) REFERENCES review_sessions(session_id)
);
```

### Resume Capability

```python
def resume_review(session_id: str):
    """Resume interrupted review session."""

    # Load session state
    session = db.get_session(session_id)

    # Determine what's incomplete
    incomplete_agents = db.get_incomplete_agents(session_id)
    incomplete_files = db.get_incomplete_files(session_id)

    # Respawn incomplete agents
    for agent in incomplete_agents:
        if agent.status == 'running':
            # Check if actually still running
            if not is_agent_alive(agent.agent_id):
                # Respawn
                coordinator.spawn_agent(agent.work_package)
        elif agent.status == 'failed':
            # Retry with error recovery
            coordinator.retry_agent(agent.agent_id)

    # Continue monitoring
    coordinator.monitor_until_complete()
```

---

## User Interface

### Command Interface

```bash
# Start autonomous review
./review start

# Or with specific scope
./review start --files=missing_content
./review start --priority=critical

# Check status
./review status

# Pause
./review pause

# Resume
./review resume

# Stop (with checkpoint)
./review stop
```

### Monitoring Dashboard

**Terminal UI** (using `rich` library):

```python
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

def create_dashboard():
    """Create real-time dashboard."""

    table = Table(title="Autonomous Review System")
    table.add_column("Phase", style="cyan")
    table.add_column("Agent", style="magenta")
    table.add_column("Progress", style="green")
    table.add_column("Status", style="yellow")

    # Add rows for each agent
    for agent in coordinator.get_active_agents():
        table.add_row(
            agent.phase,
            agent.agent_id,
            f"{agent.progress}%",
            agent.status
        )

    # Overall progress
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%")
    )

    overall_task = progress.add_task("Overall", total=coordinator.total_files)
    progress.update(overall_task, completed=coordinator.completed_files)

    return Panel.fit(table), progress
```

**Web Dashboard** (optional):

```
http://localhost:8080/review

AUTONOMOUS REVIEW SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Session: review-20251023-001
Status: IN PROGRESS
Runtime: 2h 34m
Overall: ████████████████▒▒▒▒ 65% (114/175 files)

[REAL-TIME LOGS]
10:34:45 - concepts-6: Completed batch (24 files)
10:34:46 - content-gen-1: Processing q-example--android--medium.md
10:34:47 - content-gen-1: Added Russian translation
10:34:48 - content-gen-2: Processing q-another--android--hard.md

[QUALITY METRICS]
Pass Rate: 87.3% → 94.1% (+6.8%)
Critical Issues: 52 → 8 (-85%)
Errors: 76 → 12 (-84%)

[CONTROLS]
[Pause] [Stop] [View Logs] [Export Report]
```

---

## Execution Flow

### Phase 1: Initialization

```python
# User command
$ ./review start

# Coordinator initializes
coordinator = AutonomousCoordinator()
coordinator.analyze_vault()
coordinator.create_task_graph()
coordinator.create_checkpoint()
coordinator.start_session()
```

### Phase 2: Execution

```python
# Spawn initial agents
for task in coordinator.get_initial_tasks():
    coordinator.spawn_agent(task)

# Monitor loop
while not coordinator.is_complete():
    # Check agent statuses
    for agent in coordinator.active_agents:
        if agent.is_complete():
            # Validate results
            validation = coordinator.validate_agent(agent)

            if validation.passed:
                coordinator.mark_complete(agent)
                coordinator.spawn_next_agents()
            else:
                coordinator.spawn_repair_agent(agent, validation.issues)

        elif agent.is_failed():
            coordinator.handle_failure(agent)

        elif agent.is_timeout():
            coordinator.handle_timeout(agent)

    # Update progress
    coordinator.update_progress()

    # Sleep
    time.sleep(5)
```

### Phase 3: Completion

```python
# All agents complete
coordinator.generate_final_report()
coordinator.notify_user()
coordinator.cleanup()
```

---

## Self-Correction System

### Validation Loops

**After each agent**:
1. Run validation on agent's output
2. If issues found → spawn repair agent
3. Repair agent fixes issues
4. Re-validate
5. Repeat until clean

**Example**:
```
Agent concepts-1 completes
  → Validation finds 2 broken YAML files
  → Spawn repair-yaml-1 to fix
  → Repair-yaml-1 fixes files
  → Re-validate
  → All clean ✓
  → Mark concepts-1 as complete
```

### Quality Thresholds

```python
class QualityThresholds:
    """Minimum quality requirements."""

    # Per-agent thresholds
    AGENT_MIN_PASS_RATE = 0.90  # 90% files must pass
    AGENT_MAX_ERROR_RATE = 0.10  # Max 10% errors

    # Overall thresholds
    OVERALL_MIN_PASS_RATE = 0.95  # 95% after all agents
    MAX_REGRESSIONS = 0  # Zero new issues

    # Content quality
    MIN_CONCEPTS_PER_FILE = 1
    MAX_MISSING_TRANSLATIONS = 0
```

### Auto-Correction Rules

```python
CORRECTION_RULES = {
    'broken_yaml': {
        'action': 'spawn_yaml_repair_agent',
        'priority': 'critical',
        'max_retries': 3
    },
    'missing_content': {
        'action': 'spawn_content_generator',
        'priority': 'high',
        'max_retries': 2
    },
    'low_quality_concepts': {
        'action': 'respawn_with_better_prompt',
        'priority': 'medium',
        'max_retries': 1
    }
}
```

---

## Implementation

### Coordinator Script

**File**: `review_coordinator.py`

```python
#!/usr/bin/env python3
"""
Autonomous Review Coordinator.
Fully autonomous review system - just run and wait for completion.

Usage:
    python review_coordinator.py start
    python review_coordinator.py status
    python review_coordinator.py resume
"""

import argparse
import asyncio
import json
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console
from rich.live import Live
from rich.table import Table

console = Console()


class AutonomousCoordinator:
    """Coordinates autonomous review with sub-agents."""

    def __init__(self, config_path: str = "pipeline/config.yaml"):
        self.config = self.load_config(config_path)
        self.session_id = None
        self.db = sqlite3.connect("pipeline/progress.db")
        self.init_db()
        self.active_agents = []
        self.task_queue = []

    def init_db(self):
        """Initialize progress database."""
        # Create tables (schema from above)
        pass

    def start(self):
        """Start autonomous review."""
        console.print("[bold green]Starting Autonomous Review System[/bold green]")

        # Create session
        self.session_id = f"review-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Analyze vault
        console.print("📊 Analyzing vault...")
        work_packages = self.analyze_vault()

        # Create task graph
        console.print("📋 Creating execution plan...")
        task_graph = self.create_task_graph(work_packages)

        # Create checkpoint
        console.print("💾 Creating checkpoint...")
        self.create_checkpoint()

        # Start execution
        console.print("[bold]🚀 Launching sub-agents...[/bold]")
        asyncio.run(self.execute(task_graph))

    async def execute(self, task_graph: Dict):
        """Execute task graph with sub-agents."""
        # Spawn initial agents
        initial_tasks = task_graph['initial']
        for task in initial_tasks:
            await self.spawn_agent(task)

        # Monitor loop
        with Live(self.create_dashboard(), refresh_per_second=1) as live:
            while not self.is_complete():
                # Check agent statuses
                await self.check_agents()

                # Update dashboard
                live.update(self.create_dashboard())

                # Sleep
                await asyncio.sleep(5)

        # Generate report
        self.generate_report()

    async def spawn_agent(self, task: Dict):
        """Spawn a sub-agent using Task tool."""
        agent_id = task['agent_id']

        # Save work package
        pkg_file = Path(f"pipeline/batches/{agent_id}.json")
        with open(pkg_file, 'w') as f:
            json.dump(task, f, indent=2)

        # Spawn using Task tool
        # (This would be done by Claude Code coordinator)
        console.print(f"  → Spawning {agent_id} ({task['file_count']} files)")

        # Track agent
        self.active_agents.append({
            'agent_id': agent_id,
            'task': task,
            'status': 'running',
            'started': datetime.now()
        })

    async def check_agents(self):
        """Check status of active agents."""
        for agent in self.active_agents:
            # Check if agent completed
            result_file = Path(f"pipeline/results/{agent['agent_id']}-result.json")
            if result_file.exists():
                # Load results
                with open(result_file) as f:
                    results = json.load(f)

                # Validate
                validation = self.validate_results(results)

                if validation['passed']:
                    agent['status'] = 'completed'
                    # Spawn next agents
                    await self.spawn_next_agents(agent)
                else:
                    # Spawn repair agent
                    await self.spawn_repair_agent(agent, validation)

    def create_dashboard(self):
        """Create real-time dashboard."""
        table = Table(title=f"Autonomous Review - {self.session_id}")
        table.add_column("Agent", style="cyan")
        table.add_column("Files", justify="right", style="magenta")
        table.add_column("Progress", style="green")
        table.add_column("Status", style="yellow")

        for agent in self.active_agents:
            progress = agent.get('progress', 0)
            table.add_row(
                agent['agent_id'],
                str(agent['task']['file_count']),
                f"{progress}%",
                agent['status']
            )

        return table


def main():
    parser = argparse.ArgumentParser(description="Autonomous Review Coordinator")
    parser.add_argument('command', choices=['start', 'status', 'pause', 'resume', 'stop'])
    args = parser.parse_args()

    coordinator = AutonomousCoordinator()

    if args.command == 'start':
        coordinator.start()
    elif args.command == 'status':
        coordinator.show_status()
    elif args.command == 'resume':
        coordinator.resume()
    # ... etc


if __name__ == '__main__':
    main()
```

---

## Usage Example

### Complete Autonomous Flow

```bash
# User starts review
$ python review_coordinator.py start

# System runs autonomously
Starting Autonomous Review System
📊 Analyzing vault...
  Found 175 files needing work
  - 66 files: missing concept links
  - 47 files: missing content
  - 10 files: broken wikilinks

📋 Creating execution plan...
  Phase 1: Concept links (6 parallel agents)
  Phase 2: Content generation (4 parallel agents)
  Phase 3: Validation (1 agent)

💾 Creating checkpoint...
  Backed up 175 files

🚀 Launching sub-agents...
  → Spawning concepts-1 (20 files)
  → Spawning concepts-2 (20 files)
  → Spawning concepts-3 (20 files)
  → Spawning concepts-4 (20 files)
  → Spawning concepts-5 (20 files)
  → Spawning concepts-6 (24 files)

[REAL-TIME DASHBOARD APPEARS]

... 2 hours later ...

✓ All phases complete
📊 Generating final report...

REVIEW COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session: review-20251023-001
Duration: 2h 34m
Files processed: 175/175 (100%)

RESULTS
  Concept links added: 124 files (avg 2.3 concepts/file)
  Content generated: 47 files
  Wikilinks fixed: 10 files

QUALITY IMPROVEMENT
  Pass rate: 0.0% → 98.3% (+98.3%)
  Critical issues: 52 → 0 (-100%)
  Errors: 76 → 3 (-96%)
  Warnings: 226 → 12 (-95%)

Report: pipeline/reports/review-20251023-001.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Summary

With this system, you simply say **"start review"** and:

1. **System analyzes** vault automatically
2. **Spawns sub-agents** in optimal configuration
3. **Monitors progress** in real-time
4. **Validates quality** after each agent
5. **Self-corrects** issues automatically
6. **Runs to completion** without intervention
7. **Generates report** when done

**No user action required** - fully autonomous with unlimited runtime!

---

**Status**: DESIGN COMPLETE
**Next**: Implement coordinator with Task tool integration
