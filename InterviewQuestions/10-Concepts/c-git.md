---
id: "20251012-000000"
title: "Git Fundamentals / Основы Git"
aliases: []
summary: ""
topic: "cs"
subtopics: ["branching", "git", "version-control"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-cs"
related: [c-version-control, c-ci-cd]
created: "2025-10-12"
updated: "2025-10-12"
tags: ["branching", "concept", "difficulty/medium", "git", "merging", "rebasing", "version-control"]
date created: Sunday, October 12th 2025, 2:37:10 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

Git is a distributed version control system for tracking changes in source code during software development. It provides powerful branching and merging capabilities, supports distributed workflows, and maintains complete history of all changes.

# Сводка (RU)

Git - это распределенная система контроля версий для отслеживания изменений в исходном коде во время разработки программного обеспечения. Она предоставляет мощные возможности ветвления и слияния, поддерживает распределенные рабочие процессы и сохраняет полную историю всех изменений.

## Use Cases / Trade-offs

**Use Cases:**
- Source code version control
- Collaborative development
- Feature branch workflows
- Code review processes
- Release management

**Trade-offs:**
- **Pros:** Distributed architecture, powerful branching, offline work, fast operations
- **Cons:** Steep learning curve, complex conflict resolution, large binary files handling

## Overview

Git is a distributed version control system for tracking changes in source code during software development.

---

## Core Concepts

### Repository
```bash
# Initialize repository
git init

# Clone repository
git clone https://github.com/user/repo.git
```

### Commits
```bash
# Stage changes
git add file.txt
git add .

# Commit
git commit -m "Add feature X"

# Amend last commit
git commit --amend -m "Updated message"
```

### Branches
```bash
# Create branch
git branch feature/new-feature

# Switch branch
git checkout feature/new-feature
# or
git switch feature/new-feature

# Create and switch
git checkout -b feature/new-feature
```

### Merging
```bash
# Merge branch into current
git merge feature/new-feature

# Merge with --no-ff (preserve branch history)
git merge --no-ff feature/new-feature
```

### Rebasing
```bash
# Rebase current branch onto main
git rebase main

# Interactive rebase (squash, edit, reorder commits)
git rebase -i HEAD~3
```

---

## Branching Strategies

### GitFlow
- main: production-ready code
- develop: integration branch
- feature/*: new features
- release/*: release preparation
- hotfix/*: production fixes

### GitHub Flow
- main: always deployable
- feature branches: pull requests
- merge to main: immediate deploy

---

## Related Questions

- [[q-git-pull-vs-fetch--tools--easy]]
- [[q-git-squash-commits--tools--medium]]
- [[q-git-merge-vs-rebase--tools--medium]]

## Related Concepts

- [[c-version-control]]

## References

- [Pro Git Book](https://git-scm.com/book/en/v2)
- [Git Documentation](https://git-scm.com/doc)
- [Atlassian Git Tutorials](https://www.atlassian.com/git/tutorials)

## MOC Links

- [[moc-tools]]
