---
id: concept-git
title: "Git Fundamentals / Основы Git"
type: concept
tags: [concept, git, version-control, branching, merging, rebasing]
created: 2025-10-12
updated: 2025-10-12
---

# Git Fundamentals

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

## MOC Links

- [[moc-tools]]
