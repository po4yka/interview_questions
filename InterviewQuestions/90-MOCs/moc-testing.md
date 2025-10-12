---
id: ivm-20251012-204200
title: Testing — MOC
kind: moc
created: 2025-10-12
updated: 2025-10-12
tags: [moc, topic/testing]
---

# Testing — Map of Content

## Overview
This MOC covers software testing practices, unit testing, integration testing, UI testing, test-driven development (TDD), testing frameworks, mocking, and testing strategies across different platforms.

## By Difficulty

### Easy
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM ""
WHERE difficulty = "easy" AND (contains(tags, "testing") OR topic = "testing")
SORT file.name ASC
LIMIT 50
```

### Medium
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM ""
WHERE difficulty = "medium" AND (contains(tags, "testing") OR topic = "testing")
SORT file.name ASC
LIMIT 50
```

### Hard
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM ""
WHERE difficulty = "hard" AND (contains(tags, "testing") OR topic = "testing")
SORT file.name ASC
LIMIT 50
```

## By Subtopic

### Testing Strategies

**Key Questions**:

#### General Testing
- [[q-android-testing-strategies--android--medium]] - Android testing strategies overview
- [[q-integration-testing-strategies--testing--medium]] - Integration testing approaches
- [[q-test-coverage-quality-metrics--testing--medium]] - Test coverage and quality metrics

**All Testing Strategy Questions:**
```dataview
TABLE difficulty, status
FROM ""
WHERE (contains(tags, "testing") OR topic = "testing") AND (contains(file.name, "strateg") OR contains(tags, "test-strategy"))
SORT difficulty ASC, file.name ASC
```

### Unit Testing

**Key Questions**:

#### Unit Testing Fundamentals
- [[q-fakes-vs-mocks-testing--testing--medium]] - Fakes vs Mocks
- [[q-test-doubles-dependency-injection--testing--medium]] - Test doubles and dependency injection
- [[q-mockk-advanced-features--testing--medium]] - MockK advanced features

#### Coroutines & Flow Testing
- [[q-unit-testing-coroutines-flow--android--medium]] - Testing coroutines and Flow basics
- [[q-testing-coroutines-flow--testing--hard]] - Advanced coroutines/Flow testing
- [[q-testing-viewmodels-turbine--testing--medium]] - Testing ViewModels with Turbine

**All Unit Testing Questions:**
```dataview
TABLE difficulty, status
FROM ""
WHERE (contains(tags, "testing") OR topic = "testing") AND (contains(tags, "unit-testing") OR contains(file.name, "unit-test"))
SORT difficulty ASC, file.name ASC
```

### UI Testing

**Key Questions**:

#### Android UI Testing
- [[q-compose-testing--android--medium]] - Compose UI testing basics
- [[q-compose-ui-testing-advanced--testing--hard]] - Advanced Compose UI testing
- [[q-testing-compose-ui--android--medium]] - Compose UI testing strategies
- [[q-espresso-advanced-patterns--testing--medium]] - Advanced Espresso patterns

#### Testing Approaches
- [[q-robolectric-vs-instrumented--testing--medium]] - Robolectric vs Instrumented tests
- [[q-screenshot-snapshot-testing--testing--medium]] - Screenshot/snapshot testing
- [[q-accessibility-testing--accessibility--medium]] - Accessibility testing

**All UI Testing Questions:**
```dataview
TABLE difficulty, status
FROM ""
WHERE (contains(tags, "testing") OR topic = "testing") AND (contains(tags, "ui-testing") OR contains(file.name, "ui-test") OR contains(file.name, "espresso"))
SORT difficulty ASC, file.name ASC
```

### Integration Testing

**Key Questions**:

#### Integration Testing
- [[q-integration-testing-strategies--testing--medium]] - Integration testing strategies
- [[q-kmm-testing--multiplatform--medium]] - KMM integration testing

**All Integration Testing Questions:**
```dataview
TABLE difficulty, status
FROM ""
WHERE (contains(tags, "testing") OR topic = "testing") AND (contains(tags, "integration-testing") OR contains(file.name, "integration"))
SORT difficulty ASC, file.name ASC
```

### Test Quality & Maintenance

**Key Questions**:

#### Test Quality
- [[q-flaky-test-prevention--testing--medium]] - Preventing flaky tests
- [[q-test-coverage-quality-metrics--testing--medium]] - Test coverage metrics

**All Test Quality Questions:**
```dataview
TABLE difficulty, status
FROM ""
WHERE (contains(tags, "testing") OR topic = "testing") AND (contains(file.name, "flaky") OR contains(file.name, "coverage") OR contains(file.name, "quality"))
SORT difficulty ASC, file.name ASC
```

### CI/CD & Automation

**Key Questions**:

#### Continuous Integration
- [[q-cicd-automated-testing--devops--medium]] - CI/CD automated testing

**All CI/CD Testing Questions:**
```dataview
TABLE difficulty, status
FROM ""
WHERE (contains(tags, "testing") OR topic = "testing") AND (contains(tags, "cicd") OR contains(tags, "devops") OR contains(file.name, "cicd"))
SORT difficulty ASC, file.name ASC
```

## All Questions
```dataview
TABLE difficulty, subtopics, status, tags
FROM ""
WHERE contains(tags, "testing") OR topic = "testing"
SORT difficulty ASC, file.name ASC
```

## Statistics
```dataview
TABLE length(rows) as "Count"
FROM ""
WHERE contains(tags, "testing") OR topic = "testing"
GROUP BY difficulty
SORT difficulty ASC
```

## Related MOCs
- [[moc-android]]
- [[moc-kotlin]]
- [[moc-compSci]]
