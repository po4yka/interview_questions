---
id: ivm-20251018-140300
title: DevOps & CI/CD — MOC
kind: moc
created: 2025-10-18
updated: 2025-10-18
tags: [moc, topic/devops-ci-cd]
---

# DevOps & CI/CD — Map of Content

## Overview
This MOC covers DevOps practices and CI/CD (Continuous Integration/Continuous Deployment) pipelines, including automation, build systems, deployment strategies, containerization, infrastructure as code, monitoring, and testing automation.

## By Difficulty

### Easy
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM ""
WHERE difficulty = "easy" AND (topic = "devops-ci-cd" OR contains(tags, "ci-cd") OR contains(tags, "devops"))
SORT file.name ASC
LIMIT 50
```

### Medium
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM ""
WHERE difficulty = "medium" AND (topic = "devops-ci-cd" OR contains(tags, "ci-cd") OR contains(tags, "devops"))
SORT file.name ASC
LIMIT 50
```

### Hard
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM ""
WHERE difficulty = "hard" AND (topic = "devops-ci-cd" OR contains(tags, "ci-cd") OR contains(tags, "devops"))
SORT file.name ASC
LIMIT 50
```

## By Subtopic

### CI/CD Pipelines

**Key Questions**:

#### Pipeline Setup & Configuration
- [[q-cicd-pipeline-setup--devops--medium]] - Setting up CI/CD pipeline for Android (GitHub Actions, GitLab CI, Jenkins)
- [[q-cicd-pipeline-android--android--medium]] - Android CI/CD pipeline overview

#### Testing Automation
- [[q-cicd-automated-testing--devops--medium]] - Running automated tests in CI/CD (unit, instrumented, UI)

#### Deployment Automation
- [[q-cicd-deployment-automation--devops--medium]] - Automating deployment to Play Store (signing, versioning, release tracks)

#### Multi-Module Optimization
- [[q-cicd-multi-module--devops--medium]] - Optimizing CI/CD for multi-module projects (affected module detection)

**All CI/CD Pipeline Questions:**
```dataview
TABLE difficulty, status
FROM ""
WHERE (topic = "devops-ci-cd" OR contains(tags, "ci-cd")) AND (contains(file.name, "pipeline") OR contains(tags, "pipeline"))
SORT difficulty ASC, file.name ASC
```

### Build & Deployment

**Key Questions**:

#### Build Optimization
- [[q-gradle-build-optimization--build--medium]] - Gradle build optimization techniques

#### Deployment Strategies
- [[q-cicd-deployment-automation--devops--medium]] - Deployment to Play Store
- [[q-app-bundle-optimization--distribution--medium]] - App bundle optimization

**All Build & Deployment Questions:**
```dataview
TABLE difficulty, status
FROM ""
WHERE (topic = "devops-ci-cd" OR contains(tags, "ci-cd")) AND (contains(tags, "build") OR contains(tags, "deployment") OR contains(tags, "gradle"))
SORT difficulty ASC, file.name ASC
```

### Containerization & Orchestration

**Key Questions**:

#### Docker
- Docker for consistent builds
- Docker in CI/CD pipelines

#### Kubernetes
- Container orchestration
- Kubernetes deployment strategies

**All Containerization Questions:**
```dataview
TABLE difficulty, status
FROM ""
WHERE (topic = "devops-ci-cd" OR contains(tags, "ci-cd")) AND (contains(tags, "docker") OR contains(tags, "kubernetes") OR contains(tags, "container"))
SORT difficulty ASC, file.name ASC
```

### Infrastructure as Code

**Key Questions**:

#### Infrastructure Automation
- Terraform
- Ansible
- CloudFormation

**All IaC Questions:**
```dataview
TABLE difficulty, status
FROM ""
WHERE (topic = "devops-ci-cd" OR contains(tags, "ci-cd")) AND (contains(tags, "iac") OR contains(tags, "terraform") OR contains(tags, "ansible"))
SORT difficulty ASC, file.name ASC
```

### Monitoring & Logging

**Key Questions**:

#### Application Monitoring
- Performance monitoring
- Crash reporting
- Analytics integration

#### Build Monitoring
- Build time tracking
- Test flakiness detection
- Pipeline metrics

**All Monitoring Questions:**
```dataview
TABLE difficulty, status
FROM ""
WHERE (topic = "devops-ci-cd" OR contains(tags, "ci-cd")) AND (contains(tags, "monitoring") OR contains(tags, "logging") OR contains(tags, "analytics"))
SORT difficulty ASC, file.name ASC
```

### Testing Automation

**Key Questions**:

#### Test Automation in CI
- [[q-cicd-automated-testing--devops--medium]] - Automated testing in CI/CD
- [[q-screenshot-snapshot-testing--testing--medium]] - Screenshot testing in pipelines

#### Test Optimization
- Test sharding
- Test filtering
- Parallel test execution

**All Test Automation Questions:**
```dataview
TABLE difficulty, status
FROM ""
WHERE (topic = "devops-ci-cd" OR contains(tags, "ci-cd")) AND (contains(tags, "testing") OR contains(tags, "automation"))
SORT difficulty ASC, file.name ASC
```

## Study Paths

### Beginner Path
Start with basic CI/CD concepts and pipeline setup:

1. **CI/CD Fundamentals**
   - [[q-cicd-pipeline-android--android--medium]] - Understand CI/CD basics
   - [[q-cicd-pipeline-setup--devops--medium]] - Learn pipeline setup

2. **Basic Automation**
   - Unit test automation
   - Build automation with Gradle

3. **Version Control**
   - Git workflows
   - Branching strategies

### Intermediate Path
Build on fundamentals with advanced pipeline features:

1. **Advanced Pipelines**
   - [[q-cicd-automated-testing--devops--medium]] - Automated testing strategies
   - [[q-cicd-multi-module--devops--medium]] - Multi-module optimization

2. **Deployment Automation**
   - [[q-cicd-deployment-automation--devops--medium]] - Deployment strategies
   - Release management

3. **Build Optimization**
   - Gradle caching
   - Parallel builds
   - Incremental builds

### Advanced Path
Master complex DevOps practices and enterprise patterns:

1. **Enterprise CI/CD**
   - Multi-environment deployments
   - Canary releases
   - Blue-green deployments

2. **Infrastructure**
   - Docker containerization
   - Kubernetes orchestration
   - Infrastructure as Code

3. **Monitoring & Observability**
   - Build metrics
   - Performance monitoring
   - Logging aggregation
   - Alerting systems

4. **Security & Compliance**
   - Secrets management
   - Code signing automation
   - Security scanning
   - Compliance checks

## All Questions
```dataview
TABLE difficulty, subtopics, status, tags
FROM ""
WHERE topic = "devops-ci-cd" OR contains(tags, "ci-cd") OR contains(tags, "devops")
SORT difficulty ASC, file.name ASC
```

## Statistics
```dataview
TABLE length(rows) as "Count"
FROM ""
WHERE topic = "devops-ci-cd" OR contains(tags, "ci-cd") OR contains(tags, "devops")
GROUP BY difficulty
SORT difficulty ASC
```

## Related MOCs
- [[moc-tools]] - Development tools, Git, build systems
- [[moc-testing]] - Testing strategies and frameworks
- [[moc-android]] - Android-specific CI/CD
- [[moc-backend]] - Backend deployment and infrastructure

## Key Concepts

### CI/CD Pipeline Stages
```
1. Source → 2. Build → 3. Test → 4. Deploy → 5. Monitor
    ↓         ↓         ↓         ↓          ↓
  Git SCM   Compile   Unit/UI   Staging   Metrics
            Lint      E2E       Prod      Alerts
```

### Essential Practices
- Automate everything possible
- Fail fast with quick feedback
- Test in production-like environments
- Monitor and measure continuously
- Iterate based on metrics

### Common Tools & Platforms
- **CI/CD**: GitHub Actions, GitLab CI, Jenkins, CircleCI, Bitrise
- **Build**: Gradle, Maven, Fastlane
- **Testing**: JUnit, Espresso, Robolectric, Firebase Test Lab
- **Deployment**: Play Store, Firebase App Distribution
- **Monitoring**: Firebase Crashlytics, Sentry, Datadog
- **Containerization**: Docker, Kubernetes
- **IaC**: Terraform, Ansible, CloudFormation
