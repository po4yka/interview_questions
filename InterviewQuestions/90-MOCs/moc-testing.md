---
id: ivm-20251012-204200
title: Testing — MOC
kind: moc
created: 2025-10-12
updated: 2025-10-18
tags: [moc, topic/testing]
---

# Testing — Map of Content

## Overview
This MOC covers software testing practices, unit testing, integration testing, UI testing, test-driven development (TDD), testing frameworks, mocking, and testing strategies across different platforms.

## Study Paths

### Beginner Path

Start with testing fundamentals and basic unit testing:

1. **Testing Fundamentals**
   - Understand the testing pyramid concept
   - Learn Given-When-Then pattern
   - Basic test structure and organization
   - [[q-android-testing-strategies--android--medium]] - Overview of testing methods

2. **Unit Testing Basics**
   - Writing your first unit test with JUnit
   - Assertions and test structure
   - Test isolation and independence
   - [[q-fakes-vs-mocks-testing--testing--medium]] - Understanding test doubles

3. **Test Doubles Introduction**
   - Stubs vs Mocks vs Fakes
   - When to use each type
   - Simple mock frameworks (Mockito/MockK)
   - [[q-test-doubles-dependency-injection--testing--medium]] - Test doubles and DI

### Intermediate Path

Build on fundamentals with framework-specific testing:

1. **Mocking Frameworks**
   - Advanced MockK features
   - Verification and stubbing patterns
   - [[q-mockk-advanced-features--testing--medium]] - MockK advanced usage

2. **Testing Async Code**
   - Testing coroutines with runTest
   - TestDispatcher and virtual time
   - [[q-unit-testing-coroutines-flow--android--medium]] - Coroutines/Flow testing basics
   - [[q-testing-coroutines-runtest--kotlin--medium]] - runTest deep dive
   - [[q-testing-stateflow-sharedflow--kotlin--medium]] - Testing StateFlow/SharedFlow

3. **UI Testing**
   - Espresso basics
   - Compose testing fundamentals
   - [[q-compose-testing--android--medium]] - Compose UI testing
   - [[q-testing-compose-ui--android--medium]] - Compose testing strategies
   - [[q-robolectric-vs-instrumented--testing--medium]] - Choosing test type

4. **Integration Testing**
   - Testing module interactions
   - Database testing (Room)
   - [[q-integration-testing-strategies--testing--medium]] - Integration approaches

### Advanced Path

Master complex testing scenarios and strategies:

1. **Advanced Testing Patterns**
   - TDD/BDD methodologies
   - Testing architecture patterns (MVVM, MVI)
   - [[q-testing-viewmodels-turbine--testing--medium]] - ViewModel testing with Turbine
   - [[q-testing-coroutine-cancellation--kotlin--medium]] - Testing cancellation
   - [[q-testing-flow-operators--kotlin--hard]] - Advanced Flow testing

2. **UI Testing Mastery**
   - Advanced Compose testing patterns
   - Custom matchers and assertions
   - [[q-compose-ui-testing-advanced--testing--hard]] - Advanced Compose UI testing
   - [[q-espresso-advanced-patterns--testing--medium]] - Advanced Espresso patterns
   - [[q-screenshot-snapshot-testing--testing--medium]] - Snapshot testing

3. **Test Quality & Maintenance**
   - Preventing flaky tests
   - Test coverage metrics
   - [[q-flaky-test-prevention--testing--medium]] - Flaky test strategies
   - [[q-test-coverage-quality-metrics--testing--medium]] - Coverage and metrics

4. **Performance & Specialized Testing**
   - Performance testing techniques
   - Accessibility testing
   - [[q-accessibility-testing--accessibility--medium]] - Accessibility testing
   - [[q-testing-coroutines-flow--testing--hard]] - Advanced coroutines/Flow testing

5. **CI/CD Integration**
   - Automated testing in pipelines
   - Test reporting and analytics
   - [[q-cicd-automated-testing--devops--medium]] - CI/CD testing strategies

## The Testing Pyramid

The testing pyramid is a fundamental concept in software testing that guides how to distribute testing effort across different types of tests.

```
        /\
       /  \
      / UI \       10%  - Slow, brittle, expensive
     /______\            End-to-end user flows
    /        \
   /  Integ.  \    20%  - Medium speed, moderate cost
  /____________\          Module interactions
 /              \
/  Unit Tests    \  70%  - Fast, reliable, cheap
/__________________\     Business logic, utilities
```

### Pyramid Principles

1. **Unit Tests (70%)** - Foundation
   - Test individual components in isolation
   - Fast execution (milliseconds)
   - Easy to write and maintain
   - High confidence in business logic
   - Examples: ViewModels, repositories, utility functions

2. **Integration Tests (20%)** - Middle layer
   - Test module interactions
   - Moderate execution time
   - Test data flow between components
   - Examples: Database + DAO, Repository + API, ViewModel + Repository

3. **UI Tests (10%)** - Top layer
   - Test critical user flows end-to-end
   - Slow execution (seconds to minutes)
   - More brittle, harder to maintain
   - Examples: Login flow, checkout process, main user journey

### Why This Distribution?

**Speed**: Unit tests run in milliseconds, integration tests in seconds, UI tests in minutes. Running 1000 unit tests is faster than 10 UI tests.

**Reliability**: Unit tests are deterministic and stable. UI tests can be flaky due to timing, animations, and external dependencies.

**Maintenance**: Unit tests are simple to update. UI tests break with every UI change, even if functionality is correct.

**Debugging**: Unit test failures pinpoint exact issues. UI test failures require investigation to find root cause.

**Cost**: Writing and maintaining UI tests is 10x more expensive than unit tests.

### Practical Example

Testing a login feature following the pyramid:

**Unit Tests (70%)**:
- Email validation logic
- Password strength checker
- Login request formatting
- Error message selection
- State management in ViewModel

**Integration Tests (20%)**:
- Repository calling API service
- ViewModel + Repository interaction
- Database caching after login
- Token storage

**UI Tests (10%)**:
- Complete login flow: enter credentials, tap login, navigate to home screen
- Error message display for invalid credentials

### Anti-Pattern: Ice Cream Cone

```
        /\
       /  \
      /    \
     / UI   \      70%  - WRONG! Too many UI tests
    /________\
   /          \
  / Integ.     \   20%
 /______________\
/                \
/  Unit   Tests   \ 10%  - WRONG! Too few unit tests
/____________________\
```

This leads to:
- Slow test suites (hours instead of minutes)
- Flaky, unreliable tests
- High maintenance burden
- Poor developer experience
- Delayed feedback

## Testing Frameworks & Tools

### Unit Testing Frameworks

**JUnit 4/5**
- Industry standard for Java/Kotlin unit testing
- Annotations: @Test, @Before, @After, @BeforeClass, @AfterClass
- Assertions: assertEquals, assertTrue, assertThrows
- Parameterized tests, test suites

**Kotlin Test**
- Kotlin-specific testing utilities
- kotlin.test library with DSL-style assertions

### Mocking Frameworks

**MockK**
- Kotlin-first mocking library
- Better Kotlin support than Mockito (suspend functions, extension functions)
- Relaxed mocks, spies, object mocks
- [[q-mockk-advanced-features--testing--medium]] - Advanced MockK patterns
- [[q-fakes-vs-mocks-testing--testing--medium]] - Mocks vs Fakes vs Stubs

**Mockito**
- Classic Java mocking framework
- verify(), when(), thenReturn() patterns
- Argument matchers and captor

### Coroutine Testing

**kotlinx-coroutines-test**
- runTest for coroutine testing
- TestDispatcher (Standard, Unconfined)
- Virtual time control (advanceUntilIdle, advanceTimeBy)
- [[q-testing-coroutines-runtest--kotlin--medium]] - Complete runTest guide
- [[q-unit-testing-coroutines-flow--android--medium]] - Coroutines/Flow testing

**Turbine**
- Flow testing library
- Simple, expressive API for testing Flow emissions
- awaitItem(), awaitComplete(), awaitError()
- [[q-testing-viewmodels-turbine--testing--medium]] - Turbine usage
- [[q-flow-testing-turbine--testing--medium]] - Flow testing with Turbine

### Android UI Testing

**Espresso**
- Android UI testing framework
- onView(), perform(), check() API
- ViewMatchers, ViewActions, ViewAssertions
- [[q-espresso-advanced-patterns--testing--medium]] - Advanced Espresso patterns

**Compose Testing**
- Jetpack Compose UI testing
- composeTestRule, onNodeWithTag(), onNodeWithText()
- Semantics tree interaction
- [[q-compose-testing--android--medium]] - Compose testing basics
- [[q-compose-ui-testing-advanced--testing--hard]] - Advanced Compose testing
- [[q-testing-compose-ui--android--medium]] - Compose testing strategies

**UI Automator**
- Cross-app UI testing
- System UI interaction
- Testing beyond app boundaries

**Robolectric**
- JVM-based Android testing
- Faster than instrumented tests
- [[q-robolectric-vs-instrumented--testing--medium]] - Robolectric vs Instrumented

### Test Utilities

**AndroidX Test**
- Unified testing API for JVM and device
- ActivityScenario, FragmentScenario
- Test rules and helpers

**Truth**
- Google's fluent assertion library
- assertThat(x).isEqualTo(y)
- More readable assertions

**Faker Libraries**
- Generate realistic test data
- JavaFaker, kotlin-faker
- Avoid hardcoded test data

### Screenshot/Snapshot Testing

**Paparazzi**
- JVM-based screenshot testing
- No emulator required
- Fast snapshot tests

**Shot**
- Screenshot testing framework
- Android device-based
- [[q-screenshot-snapshot-testing--testing--medium]] - Snapshot testing strategies

### Performance Testing

**Android Profiler**
- CPU, memory, network profiling
- Performance monitoring during tests

**Benchmark Library**
- Jetpack Benchmark
- Micro-benchmarking for performance-critical code

**LeakCanary**
- Memory leak detection
- Automatic in debug builds

### CI/CD Testing Tools

**Gradle Test Retry Plugin**
- Retry flaky tests automatically
- [[q-flaky-test-prevention--testing--medium]] - Flaky test strategies

**JaCoCo**
- Code coverage reporting
- [[q-test-coverage-quality-metrics--testing--medium]] - Coverage metrics

**Detekt/Lint**
- Static analysis
- Code quality checks

## Testing Best Practices

### Test Structure

**Use Given-When-Then Pattern**
```kotlin
@Test
fun `user login with valid credentials succeeds`() {
    // Given (Arrange) - Setup test data and state
    val email = "user@example.com"
    val password = "password123"
    val expectedUser = User(1, "User", email)

    // When (Act) - Execute the operation
    viewModel.login(email, password)

    // Then (Assert) - Verify the result
    assertEquals(expectedUser, viewModel.currentUser.value)
    assertFalse(viewModel.isLoading.value)
}
```

**Name Tests Descriptively**
- Use backticks for readable test names in Kotlin
- Describe behavior, not implementation
- Good: `user login with invalid credentials shows error`
- Bad: `testLogin()`, `test1()`

### Test Independence

**Each Test Should Be Isolated**
- No shared mutable state between tests
- Use @Before/@After for setup/cleanup
- Tests should pass in any order
- [[q-flaky-test-prevention--testing--medium]] - Test isolation strategies

**Clean Up Resources**
```kotlin
@After
fun tearDown() {
    database.close()
    tempFile.delete()
}
```

### What to Test

**Test Behavior, Not Implementation**
- Focus on inputs and outputs
- Don't test private methods directly
- Test public API contract

**Test Edge Cases**
- Empty collections
- Null values (in Java)
- Boundary conditions
- Error scenarios

**Don't Test Framework Code**
- Don't test Android SDK behavior
- Don't test third-party libraries
- Focus on your business logic

### Mock vs Fake

**Use Fakes for Complex Dependencies**
- Stateful components (repositories, databases)
- [[q-fakes-vs-mocks-testing--testing--medium]] - Detailed comparison

**Use Mocks for Verification**
- Verify specific interactions
- External APIs, analytics, logging

**Prefer Fakes Over Mocks**
- More realistic behavior
- Less brittle tests
- Reusable across tests

### Async Testing

**Use Proper Async Handling**
- runTest for coroutines
- TestDispatcher for virtual time
- [[q-testing-coroutines-runtest--kotlin--medium]] - Coroutine testing patterns

**Avoid Thread.sleep()**
```kotlin
// WRONG
@Test
fun badTest() {
    viewModel.loadData()
    Thread.sleep(1000)  // Flaky and slow!
    assertEquals(expected, viewModel.data.value)
}

// CORRECT
@Test
fun goodTest() = runTest {
    viewModel.loadData()
    advanceUntilIdle()  // Virtual time control
    assertEquals(expected, viewModel.data.value)
}
```

### Test Coverage

**Aim for Meaningful Coverage**
- 70-80% coverage for unit tests is a good target
- 100% coverage doesn't mean bug-free
- Focus on critical paths and business logic
- [[q-test-coverage-quality-metrics--testing--medium]] - Coverage metrics

**Don't Chase Metrics Blindly**
- Quality over quantity
- Test important behavior, not lines of code
- Some code doesn't need tests (simple getters, generated code)

### Flaky Test Prevention

**Common Causes of Flakiness**
- Race conditions and timing issues
- Shared state between tests
- Non-deterministic data (Random without seed)
- External dependencies (network, file system)
- [[q-flaky-test-prevention--testing--medium]] - Comprehensive flaky test guide

**Fix Flaky Tests Immediately**
- Don't ignore or disable flaky tests
- They erode trust in test suite
- Debug and fix root cause

### TDD/BDD Practices

**Test-Driven Development (TDD)**
1. Write failing test
2. Write minimal code to pass
3. Refactor while keeping tests green
4. Repeat

**Benefits**:
- Better test coverage
- Simpler, more testable design
- Living documentation

**Behavior-Driven Development (BDD)**
- Focus on business behavior
- Given-When-Then format
- Collaboration between developers and stakeholders

### Performance Considerations

**Keep Tests Fast**
- Unit tests should run in milliseconds
- Slow tests won't be run frequently
- Use in-memory databases
- Mock expensive operations

**Parallelize When Possible**
- Run tests in parallel
- Gradle: `maxParallelForks = Runtime.runtime.availableProcessors()`
- Ensure tests are truly independent

### Documentation

**Tests as Documentation**
- Well-written tests explain how code should be used
- Test names describe expected behavior
- Examples for new developers

**Document Known Issues**
- Comment tests that are temporarily disabled
- Link to issue tracker
- Explain why test is skipped

### Continuous Integration

**Run Tests in CI/CD**
- Every pull request
- Before merging to main
- [[q-cicd-automated-testing--devops--medium]] - CI/CD testing strategies

**Test Different Configurations**
- Multiple API levels
- Different screen sizes
- Various locales

**Monitor Test Metrics**
- Track test execution time
- Monitor flakiness rate
- Coverage trends over time

### Code Review for Tests

**Review Test Code Too**
- Tests are production code
- Apply same quality standards
- Check for proper assertions
- Verify test isolation

**Look For**:
- Clear test names
- Proper setup/teardown
- No test interdependencies
- Appropriate test doubles
- Good coverage of edge cases

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
- [[moc-cs]]
