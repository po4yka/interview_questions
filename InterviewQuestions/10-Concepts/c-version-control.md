---
id: concept-version-control
title: "Version Control Systems / Системы контроля версий"
type: concept
tags: [concept, vcs, git, version-control, collaboration]
created: 2025-10-12
updated: 2025-10-12
---

# Version Control Systems

## Overview

Version Control Systems (VCS) track changes to files over time, enabling collaboration, history tracking, and rollback capabilities.

---

## Types of VCS

### Centralized (CVCS)
- Single central repository
- Examples: SVN, Perforce
- Requires network for most operations

### Distributed (DVCS)
- Every developer has full repository copy
- Examples: Git, Mercurial
- Offline work possible
- Better branching/merging

---

## Core Concepts

### Commit
Snapshot of changes at a point in time.

### Branch
Independent line of development.

### Merge
Combine changes from different branches.

### Conflict
When same code is modified in different ways.

### Tag
Named reference to specific commit (releases).

---

## Benefits

- History tracking
- Collaboration
- Branching strategies
- Code review
- Rollback capability
- Backup
- Audit trail

---

## Related Questions

- [[q-git-pull-vs-fetch--tools--easy]]

## Related Concepts

- [[c-git]]

## MOC Links

- [[moc-tools]]
