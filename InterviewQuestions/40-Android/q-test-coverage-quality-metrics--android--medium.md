---
id: android-087
title: "Test Coverage Quality Metrics / Метрики покрытия и качества тестов"
aliases: [Test Coverage Quality Metrics, Метрики покрытия и качества тестов]
topic: android
subtopics: [testing-instrumented, testing-unit]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-junit, c-testing, q-what-is-diffutil-for--android--medium]
created: 2025-10-13
updated: 2025-10-31
tags: [android/testing-instrumented, android/testing-unit, coverage, difficulty/medium, jacoco, metrics]
date created: Saturday, November 1st 2025, 12:47:05 pm
date modified: Saturday, November 1st 2025, 5:43:29 pm
---

# Test Coverage and Quality Metrics

**English**: Measure and improve test coverage. Configure JaCoCo, analyze coverage reports, identify gaps. Balance coverage vs quality.

**Russian**: Измеряйте и улучшайте покрытие тестами. Настройте JaCoCo, анализируйте отчеты покрытия, выявляйте пробелы. Баланс между покрытием и качеством.

## Answer (EN)

Test coverage metrics help identify untested code, but high coverage doesn't guarantee quality. Understanding metrics and balancing coverage with meaningful tests is crucial.

### JaCoCo Setup

```gradle
// build.gradle (project level)
buildscript {
    dependencies {
        classpath "org.jacoco:org.jacoco.core:0.8.10"
    }
}

// build.gradle (app level)
plugins {
    id 'com.android.application'
    id 'jacoco'
}

android {
    buildTypes {
        debug {
            testCoverageEnabled true
        }
    }
}

tasks.register('jacocoTestReport', JacocoReport) {
    dependsOn 'testDebugUnitTest'

    reports {
        xml.required = true
        html.required = true
        csv.required = false
    }

    def fileFilter = [
        '**/R.class',
        '**/R$*.class',
        '**/BuildConfig.*',
        '**/Manifest*.*',
        '**/*Test*.*',
        'android/**/*.*',
        '**/*_Factory.*',
        '**/*_MembersInjector.*',
        '**/*Module.*',
        '**/*Dagger*.*',
        '**/*Hilt*.*'
    ]

    def debugTree = fileTree(
        dir: "$buildDir/intermediates/javac/debug",
        excludes: fileFilter
    )
    def mainSrc = "$projectDir/src/main/java"

    sourceDirectories.setFrom(files([mainSrc]))
    classDirectories.setFrom(files([debugTree]))
    executionData.setFrom(fileTree(
        dir: buildDir,
        includes: [
            'jacoco/testDebugUnitTest.exec',
            'outputs/code_coverage/debugAndroidTest/connected/*coverage.ec'
        ]
    ))
}

// Combined report for unit + instrumentation tests
tasks.register('jacocoFullReport', JacocoReport) {
    dependsOn 'testDebugUnitTest'
    dependsOn 'createDebugCoverageReport'

    // Same configuration as above
}

// Coverage verification
tasks.register('jacocoVerification', JacocoCoverageVerification) {
    dependsOn 'jacocoTestReport'

    violationRules {
        rule {
            limit {
                minimum = 0.80 // 80% coverage minimum
            }
        }

        rule {
            enabled = true
            element = 'CLASS'
            limit {
                counter = 'LINE'
                value = 'COVEREDRATIO'
                minimum = 0.70
            }
            excludes = [
                '*.BuildConfig',
                '*.di.*',
                '*.ui.theme.*'
            ]
        }
    }
}
```

### Understanding Coverage Metrics

**Line Coverage**: Percentage of executed lines
**Branch Coverage**: Percentage of executed branches (if/else, switch)
**Method Coverage**: Percentage of executed methods
**Class Coverage**: Percentage of classes with at least one executed method

```kotlin
// Example with coverage analysis
class Calculator {
    fun divide(a: Int, b: Int): Int {  // Line coverage
        if (b == 0) {                   // Branch coverage - 2 branches
            throw IllegalArgumentException("Division by zero")
        }
        return a / b
    }

    fun isPositive(n: Int): Boolean {  // Method coverage
        return n > 0
    }
}

// Test with 75% branch coverage
class CalculatorTest {
    @Test
    fun divide_validInput() {
        assertEquals(5, Calculator().divide(10, 2))
        // Covers: line with divide call, else branch
        // Missing: if branch (division by zero)
    }

    @Test
    fun isPositive_true() {
        assertTrue(Calculator().isPositive(5))
        // Covers: isPositive method
    }

    // Missing test for divide by zero = 75% branch coverage
}
```

### Analyzing Coverage Reports

```bash
# Generate report
./gradlew jacocoTestReport

# View report
open app/build/reports/jacoco/jacocoTestReport/html/index.html
```

**Coverage Report Interpretation**:

```
Package: com.example.data
 Class: UserRepository (85% coverage)
   getUser() - 100%
   updateUser() - 90%  (missing error branch)
   deleteUser() - 0%  (not tested)
```

### Identifying Coverage Gaps

```kotlin
// Original code
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState = _uiState.asStateFlow()

    fun loadUser(id: String) {
        viewModelScope.launch {
            try {
                val user = repository.getUser(id)  // Line 1
                _uiState.value = UiState.Success(user)  // Line 2
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message)  // Line 3 - NOT COVERED
            }
        }
    }

    fun refresh() {  // NOT COVERED
        loadUser(currentUserId)
    }
}

// Coverage report shows:
// loadUser: 66% (Lines 1,2 covered, Line 3 not covered)
// refresh: 0% (never called in tests)

// Add missing tests
@Test
fun loadUser_error() = runTest {
    repository.shouldReturnError = true
    viewModel.loadUser("1")
    assertTrue(viewModel.uiState.value is UiState.Error)  // Now covers Line 3
}

@Test
fun refresh_reloadsUser() = runTest {
    viewModel.refresh()  // Now covers refresh method
    // assertions...
}
```

### Coverage by Layer

```kotlin
// Typical coverage targets
val coverageTargets = mapOf(
    "ViewModel" to 85,        // High coverage for business logic
    "Repository" to 80,       // Most paths tested
    "UseCase" to 90,          // Critical business logic
    "UI/Composables" to 50,   // Lower priority for pure UI
    "DataSource" to 75,       // Important for data integrity
    "Mapper" to 95,           // Simple, easy to test fully
    "Utility" to 90           // Reusable code should be well-tested
)
```

### Quality Vs Coverage Balance

**High coverage doesn't mean high quality**:

```kotlin
// BAD: 100% coverage but meaningless test
@Test
fun badTest() {
    val calculator = Calculator()
    calculator.add(1, 2)  // Executes code but doesn't assert anything
    // Coverage: 100%, Quality: 0%
}

// GOOD: Lower coverage but meaningful
@Test
fun goodTest() {
    val calculator = Calculator()
    val result = calculator.add(1, 2)
    assertEquals(3, result)  // Verifies behavior
    // Coverage: same, Quality: high
}
```

**Mutation Testing** for quality:

```gradle
plugins {
    id 'info.solidsoft.pitest' version '1.9.11'
}

pitest {
    targetClasses = ['com.example.*']
    pitestVersion = '1.14.2'
    threads = 4
    outputFormats = ['HTML', 'XML']
    timestampedReports = false
}
```

### Coverage Exclusions

```kotlin
// Exclude generated code
@Generated
class User_Impl : User

// Exclude debug-only code
@DebugOnly
fun debugPrint(message: String) {
    Log.d("DEBUG", message)
}

// JaCoCo configuration
jacocoTestReport {
    classDirectories.setFrom(files(classDirectories.files.collect {
        fileTree(dir: it, excludes: [
            '**/*_Impl.*',           // Generated implementations
            '**/*DebugOnly*.*',      // Debug utilities
            '**/*$*.class',          // Inner classes (if not tested)
            '**/*Module*.class',     // DI modules
            '**/*Component*.class'   // DI components
        ])
    }))
}
```

### CI/CD Integration

```yaml
# GitHub Actions
name: Test Coverage

on: [push, pull_request]

jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up JDK
        uses: actions/setup-java@v3
        with:
          java-version: '17'

      - name: Run tests with coverage
        run: ./gradlew jacocoTestReport

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./app/build/reports/jacoco/jacocoTestReport/jacocoTestReport.xml
          fail_ci_if_error: true

      - name: Verify coverage
        run: ./gradlew jacocoVerification

      - name: Comment PR with coverage
        uses: madrapps/jacoco-report@v1.3
        with:
          paths: ${{ github.workspace }}/app/build/reports/jacoco/jacocoTestReport/jacocoTestReport.xml
          token: ${{ secrets.GITHUB_TOKEN }}
          min-coverage-overall: 80
          min-coverage-changed-files: 80
```

### Coverage Dashboard Example

```kotlin
// Custom coverage reporter
class CoverageReporter {
    fun generateReport(jacocoReport: File): CoverageReport {
        val doc = parseXml(jacocoReport)

        val packages = doc.selectNodes("//package").map { pkg ->
            val name = pkg.getAttribute("name")
            val lineCoverage = pkg.selectSingleNode("counter[@type='LINE']")
            val branchCoverage = pkg.selectSingleNode("counter[@type='BRANCH']")

            PackageCoverage(
                name = name,
                linesCovered = lineCoverage.getAttribute("covered").toInt(),
                linesTotal = lineCoverage.getAttribute("missed").toInt() +
                            lineCoverage.getAttribute("covered").toInt(),
                branchesCovered = branchCoverage.getAttribute("covered").toInt(),
                branchesTotal = branchCoverage.getAttribute("missed").toInt() +
                               branchCoverage.getAttribute("covered").toInt()
            )
        }

        return CoverageReport(packages)
    }
}
```

### Best Practices

1. **Set realistic coverage goals** (70-85% is often sufficient)
2. **Focus on critical paths** over arbitrary coverage numbers
3. **Exclude generated and framework code**
4. **Use branch coverage** as primary metric
5. **Combine with mutation testing** for quality assurance
6. **Track coverage trends** over time
7. **Review coverage reports** in code reviews
8. **Don't sacrifice test quality** for coverage percentage
9. **Test edge cases and errors**, not just happy paths
10. **Integrate into CI/CD pipeline**

## Ответ (RU)

Метрики покрытия тестами помогают идентифицировать непротестированный код, но высокое покрытие не гарантирует качество.

### Типы Покрытия

- **Line Coverage**: процент выполненных строк
- **Branch Coverage**: процент выполненных ветвей
- **Method Coverage**: процент выполненных методов
- **Class Coverage**: процент классов с хотя бы одним выполненным методом

[Полные примеры настройки JaCoCo, анализа отчетов и CI/CD интеграции приведены в английском разделе]

### Лучшие Практики

1. **Устанавливайте реалистичные цели покрытия** (70-85%)
2. **Фокусируйтесь на критичных путях**
3. **Исключайте сгенерированный код**
4. **Используйте branch coverage** как основную метрику
5. **Комбинируйте с mutation testing**
6. **Отслеживайте тренды покрытия**
7. **Проверяйте отчеты в code reviews**
8. **Не жертвуйте качеством ради процентов**
9. **Тестируйте edge cases и ошибки**
10. **Интегрируйте в CI/CD**

---


## Follow-ups

- [[c-junit]]
- [[c-testing]]
- [[q-what-is-diffutil-for--android--medium]]


## References

- https://developer.android.com/training/testing/local-tests
- https://developer.android.com/docs


## Related Questions

### Related (Medium)
- [[q-testing-viewmodels-turbine--android--medium]] - Testing
- [[q-testing-compose-ui--android--medium]] - Testing
- [[q-compose-testing--android--medium]] - Testing
- [[q-robolectric-vs-instrumented--android--medium]] - Testing
- [[q-screenshot-snapshot-testing--android--medium]] - Testing

### Advanced (Harder)
- [[q-testing-coroutines-flow--android--hard]] - Testing
