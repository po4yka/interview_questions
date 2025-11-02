---
id: ivm-20251012-140500
title: Tools — MOC
kind: moc
created: 2025-10-12
updated: 2025-10-18
tags: [moc, topic/tools]
date created: Saturday, October 18th 2025, 2:46:09 pm
date modified: Saturday, November 1st 2025, 5:43:22 pm
---

# Tools — Map of Content

## Overview
This MOC covers development tools including version control (Git), build systems, CI/CD, IDEs, command-line tools, debugging tools, profiling tools, and other essential developer productivity tools.

## Study Paths

### Beginner Path: Git Fundamentals
Essential Git commands and workflows for daily development.

1. **Basic Operations**
   - [[q-git-pull-vs-fetch--tools--easy]] - Understanding pull vs fetch
   - Learn: git status, git add, git commit
   - Learn: git push, git pull basics

2. **Branching Basics**
   - Learn: git branch, git checkout
   - Learn: Creating and switching branches
   - Learn: Merging simple changes

3. **Remote Operations**
   - [[q-git-pull-vs-fetch--tools--easy]] - Fetching and pulling changes
   - Learn: git remote, git clone
   - Learn: Pushing to remote repositories

### Intermediate Path: Merge Strategies & Workflows
Advanced branching, conflict resolution, and team workflows.

1. **Merge vs Rebase**
   - [[q-git-merge-vs-rebase--tools--medium]] - Comprehensive merge vs rebase guide
   - [[q-git-squash-commits--tools--medium]] - Squashing commits with interactive rebase
   - Learn: When to use merge vs rebase
   - Learn: Fast-forward merges

2. **Conflict Resolution**
   - Learn: Resolving merge conflicts
   - Learn: Using merge tools
   - Learn: Conflict resolution during rebase

3. **Branch Management**
   - Learn: Feature branch workflow
   - Learn: Git flow and other workflows
   - Learn: Branch naming conventions

4. **History Management**
   - [[q-git-squash-commits--tools--medium]] - Combining commits
   - Learn: git reset (soft, mixed, hard)
   - Learn: git revert vs reset

### Advanced Path: Git Internals & Complex Workflows
Deep understanding of Git internals and advanced techniques.

1. **Git Internals**
   - Learn: Git object model (blobs, trees, commits)
   - Learn: How Git stores data
   - Learn: Understanding refs and HEAD

2. **Advanced Rebase**
   - [[q-git-squash-commits--tools--medium]] - Interactive rebase techniques
   - Learn: git rebase -i advanced options (pick, squash, fixup, reword, edit)
   - Learn: Rewriting history safely
   - Learn: Recovering from rebase mistakes

3. **Complex Workflows**
   - Learn: git reflog for recovery
   - Learn: git bisect for debugging
   - Learn: git cherry-pick
   - Learn: Submodules and subtrees
   - Learn: Git hooks and automation

4. **Team Collaboration**
   - [[q-git-merge-vs-rebase--tools--medium]] - Best practices for team workflows
   - Learn: Pull request workflows
   - Learn: Code review with Git
   - Learn: Handling force pushes safely

## Git Workflow Diagrams

### Feature Branch Workflow with Merge
```
main:     A --- B --- C --- D --- M --- F
                       \         /
feature:                E -----

Timeline:
1. Branch from main at C
2. Work on feature (commit E)
3. Main advances (commit D)
4. Merge feature into main (commit M)
5. Continue main development (commit F)
```

### Feature Branch Workflow with Rebase
```
Before rebase:
main:     A --- B --- C --- D
                       \
feature:                E --- F

After rebase:
main:     A --- B --- C --- D
                             \
feature:                      E' --- F'

Timeline:
1. Branch from main at C
2. Work on feature (commits E, F)
3. Main advances (commit D)
4. Rebase feature onto main (creates E', F')
5. Fast-forward merge into main
```

### Interactive Rebase for Cleanup
```
Before interactive rebase:
feature:  A --- B --- C --- D --- E
               WIP   Fix   WIP  Feature

After squashing:
feature:  A --- F
              Combined feature

Commands:
git rebase -i HEAD~4
pick B
squash C
squash D
squash E
```

## Common Git Commands Reference

### Daily Operations
```bash
git status                    # Check working directory status
git add <file>                # Stage file for commit
git add .                     # Stage all changes
git commit -m "message"       # Commit with message
git push                      # Push to remote
git pull                      # Fetch and merge from remote
```

### Branching
```bash
git branch                    # List branches
git branch <name>             # Create new branch
git checkout <branch>         # Switch to branch
git checkout -b <branch>      # Create and switch
git merge <branch>            # Merge branch into current
git branch -d <branch>        # Delete merged branch
git branch -D <branch>        # Force delete branch
```

### Remote Operations
```bash
git remote -v                 # List remotes
git fetch origin              # Download from remote
git pull origin main          # Fetch and merge
git push origin <branch>      # Push branch to remote
git push -u origin <branch>   # Push and set upstream
```

### History & Inspection
```bash
git log                       # View commit history
git log --oneline             # Compact log view
git log --graph --oneline     # Visual branch history
git diff                      # Show unstaged changes
git diff --staged             # Show staged changes
git show <commit>             # Show commit details
```

### Undoing Changes
```bash
git restore <file>            # Discard working changes
git restore --staged <file>   # Unstage file
git reset HEAD~1              # Undo last commit (keep changes)
git reset --hard HEAD~1       # Undo last commit (discard changes)
git revert <commit>           # Create new commit undoing changes
```

### Advanced Operations
```bash
git rebase main               # Rebase current branch on main
git rebase -i HEAD~3          # Interactive rebase last 3 commits
git cherry-pick <commit>      # Apply commit to current branch
git stash                     # Temporarily save changes
git stash pop                 # Restore stashed changes
git reflog                    # View reference log (recovery)
```

## By Difficulty

### Easy
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "80-Tools"
WHERE difficulty = "easy"
SORT file.name ASC
LIMIT 50
```

### Medium
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "80-Tools"
WHERE difficulty = "medium"
SORT file.name ASC
LIMIT 50
```

### Hard
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "80-Tools"
WHERE difficulty = "hard"
SORT file.name ASC
LIMIT 50
```

## By Subtopic

### Git & Version Control

**Key Questions** (Curated Learning Path):

#### Fundamentals (Easy)
- [[q-git-pull-vs-fetch--tools--easy]] - Understanding the difference between pull and fetch
- Learn: Basic git workflow (clone, add, commit, push)
- Learn: Git configuration and setup
- Learn: Understanding the staging area

#### Branching & Merging (Medium)
- [[q-git-merge-vs-rebase--tools--medium]] - Comprehensive guide to merge vs rebase strategies
- [[q-git-squash-commits--tools--medium]] - How to squash commits using interactive rebase
- Learn: Branch management and naming conventions
- Learn: Resolving merge conflicts
- Learn: Fast-forward vs non-fast-forward merges

#### Advanced Workflows (Hard)
- Learn: Git internals (objects, refs, HEAD)
- Learn: Advanced rebase techniques and conflict resolution
- Learn: git reflog and recovery strategies
- Learn: git bisect for debugging
- Learn: Submodules and subtrees

**Best Practices**:
- Use `git fetch` to review changes before merging
- Rebase local branches, merge for shared/public branches
- Never rebase public history
- Use interactive rebase to clean up commit history before PR
- Write meaningful commit messages

**All Git Questions:**
```dataview
TABLE difficulty, status
FROM "80-Tools"
WHERE contains(tags, "git") OR contains(tags, "version-control") OR contains(subtopics, "git") OR contains(file.name, "git")
SORT difficulty ASC, file.name ASC
```

### Build Systems

**Key Questions** (Curated Learning Path):

#### Gradle Fundamentals (Easy)
- Learn: What is Gradle and build automation
- Learn: build.gradle vs build.gradle.kts
- Learn: Gradle project structure
- Learn: Basic Gradle tasks (clean, build, assemble)

#### Gradle Configuration (Medium)
- Learn: Dependencies management (implementation, api, compileOnly)
- Learn: Build variants and flavors (Android)
- Learn: Custom Gradle tasks
- Learn: Build configuration and settings.gradle
- Learn: Gradle plugins and repositories

#### Advanced Build Optimization (Hard)
- Learn: Gradle build cache and optimization
- Learn: Multi-module projects
- Learn: Custom plugins development
- Learn: Build performance tuning
- Learn: Gradle version catalogs

**Best Practices**:
- Use version catalogs for dependency management
- Enable Gradle build cache for faster builds
- Separate build logic with buildSrc or convention plugins
- Use implementation over api when possible
- Keep Gradle and plugin versions up to date

**All Build System Questions:**
```dataview
TABLE difficulty, status
FROM "80-Tools"
WHERE contains(tags, "gradle") OR contains(tags, "maven") OR contains(tags, "build-systems") OR contains(tags, "build-tools")
SORT difficulty ASC, file.name ASC
```

### CI/CD

**Key Questions** (Curated Learning Path):

#### CI/CD Basics (Easy)
- Learn: What is Continuous Integration
- Learn: What is Continuous Deployment vs Delivery
- Learn: CI/CD pipeline concepts
- Learn: Common CI/CD tools (GitHub Actions, GitLab CI, Jenkins)

#### Pipeline Configuration (Medium)
- Learn: Writing CI/CD pipeline configurations
- Learn: Automated testing in pipelines
- Learn: Build and deployment automation
- Learn: Environment management (dev, staging, production)
- Learn: Secrets and credentials management

#### Advanced CI/CD (Hard)
- Learn: Blue-green deployments
- Learn: Canary deployments and rollback strategies
- Learn: Infrastructure as Code (IaC)
- Learn: Container orchestration in CI/CD
- Learn: Monitoring and observability

**Best Practices**:
- Run tests on every commit
- Keep pipelines fast (parallel execution, caching)
- Fail fast - run quick tests first
- Use matrix builds for multi-platform testing
- Automate versioning and changelog generation

**All CI/CD Questions:**
```dataview
TABLE difficulty, status
FROM "80-Tools"
WHERE contains(tags, "ci-cd") OR contains(tags, "continuous-integration") OR contains(tags, "deployment")
SORT difficulty ASC, file.name ASC
```

### IDEs & Editors

**Essential Skills**:

#### Android Studio / IntelliJ IDEA
- Learn: Navigation and keyboard shortcuts
- Learn: Code completion and refactoring tools
- Learn: Debugging with breakpoints and watches
- Learn: Profiling tools (CPU, memory, network)
- Learn: Version control integration
- Learn: Live templates and custom templates
- Learn: Plugin ecosystem and customization

**Productivity Tips**:
- Master keyboard shortcuts (search everywhere, go to definition, refactor)
- Use live templates for common code patterns
- Configure code style and formatting
- Use structural search and replace for complex refactoring
- Enable Git integration for inline blame and history

**All IDE Questions:**
```dataview
TABLE difficulty, status
FROM "80-Tools"
WHERE contains(tags, "ide") OR contains(tags, "android-studio") OR contains(tags, "intellij")
SORT difficulty ASC, file.name ASC
```

### Command-Line Tools

**Essential CLI Skills**:

#### Basic Commands
- Learn: Navigation (cd, ls, pwd)
- Learn: File operations (cp, mv, rm, mkdir)
- Learn: Text processing (grep, sed, awk, cat)
- Learn: Process management (ps, top, kill)

#### Advanced CLI
- Learn: Pipe and redirection (|, >, >>, <)
- Learn: Environment variables and PATH
- Learn: Shell scripting basics (bash, zsh)
- Learn: Package managers (apt, brew, npm)
- Learn: SSH and remote operations

**All CLI Questions:**
```dataview
TABLE difficulty, status
FROM "80-Tools"
WHERE contains(tags, "cli") OR contains(tags, "command-line") OR contains(tags, "terminal")
SORT difficulty ASC, file.name ASC
```

### Debugging & Profiling

**Key Debugging Skills**:

#### Debugging Fundamentals
- Learn: Breakpoints (line, conditional, exception)
- Learn: Step execution (step over, into, out)
- Learn: Watch expressions and evaluate
- Learn: Call stack navigation
- Learn: Thread debugging

#### Profiling
- Learn: CPU profiling and flame graphs
- Learn: Memory profiling and leak detection
- Learn: Network profiling and monitoring
- Learn: Android-specific tools (Layout Inspector, Profiler)

**All Debugging/Profiling Questions:**
```dataview
TABLE difficulty, status
FROM "80-Tools"
WHERE contains(tags, "debugging") OR contains(tags, "profiling") OR contains(tags, "performance-tools")
SORT difficulty ASC, file.name ASC
```

### Testing Tools

**Testing Tool Categories**:

#### Unit Testing
- Learn: JUnit, TestNG frameworks
- Learn: Mocking with Mockito, MockK
- Learn: Assertion libraries

#### Android Testing
- Learn: Espresso for UI testing
- Learn: Robolectric for unit testing
- Learn: AndroidX Test framework

#### Other Tools
- Learn: Test coverage tools (JaCoCo)
- Learn: Performance testing tools
- Learn: Screenshot testing

**All Testing Tool Questions:**
```dataview
TABLE difficulty, status
FROM "80-Tools"
WHERE contains(tags, "testing-tools") OR contains(tags, "test-frameworks")
SORT difficulty ASC, file.name ASC
```

## All Questions
```dataview
TABLE difficulty, subtopics, status, tags
FROM "80-Tools"
SORT difficulty ASC, file.name ASC
```

## Statistics
```dataview
TABLE length(rows) as "Count"
FROM "80-Tools"
GROUP BY difficulty
SORT difficulty ASC
```

## Related MOCs
- [[moc-android]]
- [[moc-backend]]
- [[moc-kotlin]]
