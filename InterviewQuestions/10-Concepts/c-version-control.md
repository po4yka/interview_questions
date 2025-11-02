---
id: "20251012-000000"
title: "Version Control Systems / Системы контроля версий"
aliases: []
summary: ""
topic: "cs"
subtopics: ["git", "vcs", "version-control"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-cs"
related: []
created: "2025-10-12"
updated: "2025-10-12"
tags: ["collaboration", "concept", "difficulty/medium", "git", "vcs", "version-control"]
date created: Sunday, October 12th 2025, 2:37:10 pm
date modified: Saturday, November 1st 2025, 5:43:38 pm
---

# Summary (EN)

Version Control Systems (VCS) track changes to files over time, enabling collaboration, history tracking, and rollback capabilities. There are two main types: Centralized (CVCS) with a single repository like SVN, and Distributed (DVCS) where every developer has a full copy like Git. VCS provides essential features for team collaboration, code review, and change management.

# Сводка (RU)

Системы контроля версий (VCS) отслеживают изменения в файлах с течением времени, обеспечивая совместную работу, отслеживание истории и возможность отката. Существуют два основных типа: Централизованные (CVCS) с единым репозиторием, такие как SVN, и Распределенные (DVCS), где каждый разработчик имеет полную копию, такие как Git. VCS предоставляют необходимые функции для командной работы, проверки кода и управления изменениями.

## Use Cases / Trade-offs

**Use Cases:**
- Source code management
- Team collaboration
- Change tracking and history
- Code review workflows
- Release management
- Backup and disaster recovery

**Trade-offs:**
- **CVCS vs DVCS:** Simple central control vs. offline work and distributed workflows
- **Branching:** Flexibility vs. merge complexity
- **History:** Complete audit trail vs. repository size growth
- **Learning Curve:** Simple workflows vs. advanced features complexity

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

## References

- [Git Documentation](https://git-scm.com/doc)
- [Version Control with Git](https://www.atlassian.com/git/tutorials/what-is-version-control)
- "Version Control with Git" by Jon Loeliger and Matthew McCullough
- [Pro Git Book](https://git-scm.com/book/en/v2)

## MOC Links

- [[moc-tools]]
