---
id: android-087
title: Test Coverage Quality Metrics / Метрики покрытия и качества тестов
aliases: [Test Coverage Quality Metrics, Метрики покрытия и качества тестов]
topic: android
subtopics:
  - testing-instrumented
  - testing-unit
question_kind: theory
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-testing
  - q-dagger-build-time-optimization--android--medium
  - q-jank-detection-frame-metrics--android--medium
  - q-test-doubles-dependency-injection--android--medium
  - q-what-is-diffutil-for--android--medium
created: 2025-10-13
updated: 2025-11-10
tags: [android/testing-instrumented, android/testing-unit, coverage, difficulty/medium, jacoco, metrics]

date created: Saturday, November 1st 2025, 12:47:05 pm
date modified: Tuesday, November 25th 2025, 8:53:56 pm
---
# Вопрос (RU)
> Метрики покрытия и качества тестов

# Question (EN)
> Test Coverage Quality Metrics

---

## Ответ (RU)

Метрики покрытия тестами помогают найти непротестированный код, но высокий процент не гарантирует качество. Важно понимать типы метрик, правильно настраивать инструменты (например, JaCoCo) и следить за тем, чтобы тесты реально проверяли поведение.

Ниже приведены примеры и шаблоны конфигурации. Они могут отличаться в зависимости от версии Android Gradle Plugin (AGP), Gradle и JaCoCo. Не воспринимайте их как готовое решение «из коробки» — проверяйте задачи и пути под свой проект.

### Настройка JaCoCo (Android пример)

Пример (упрощённый) конфигурации JaCoCo для Android; конкретные пути и задачи зависят от версии Android Gradle Plugin и структуры проекта:

```gradle
// build.gradle (app module)
plugins {
    id 'com.android.application'
    id 'jacoco'
}

android {
    buildTypes {
        debug {
            // Для инструментального покрытия в старых версиях AGP; в новых может быть недоступно/удалено
            testCoverageEnabled true
        }
    }
}

// Отчёт по unit-тестам (+ опционально инструментальным тестам)
// Шаблон: проверьте, что задачи и директории соответствуют вашей версии AGP/Gradle.
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

// Сводный отчёт по unit + инструментальным тестам (эскиз, задачи версии-зависимы)
tasks.register('jacocoFullReport', JacocoReport) {
    dependsOn 'testDebugUnitTest'
    dependsOn 'createDebugCoverageReport' // убедитесь, что задача существует в вашем проекте

    // sourceDirectories, classDirectories, executionData настраиваются аналогично jacocoTestReport
}

// Проверка минимального покрытия (пример; конфигурация плагина/типа задачи может отличаться)

tasks.register('jacocoVerification', JacocoCoverageVerification) {
    dependsOn 'jacocoTestReport'

    violationRules {
        rule {
            limit {
                minimum = 0.80 // пример: минимум 80% общего покрытия
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

Примечание: используйте это как шаблон; точная интеграция (task names, директории, поддержка `testCoverageEnabled`) зависит от версии AGP и используемого Gradle-плагина JaCoCo.

### Понимание Метрик Покрытия (с примером)

- Line Coverage: доля выполненных строк кода.
- Branch Coverage: доля выполненных ветвей (if/else, switch и т.п.).
- Method Coverage: доля вызванных методов.
- Class Coverage: доля классов, где выполнен хотя бы один метод.

```kotlin
// Пример для иллюстрации метрик (валидный Kotlin-код)
class Calculator {
    fun divide(a: Int, b: Int): Int {  // Влияет на line и branch coverage
        if (b == 0) {                  // Две ветви для branch coverage
            throw IllegalArgumentException("Division by zero")
        }
        return a / b
    }

    fun add(a: Int, b: Int): Int {
        return a + b
    }

    fun isPositive(n: Int): Boolean {  // Для method coverage
        return n > 0
    }
}

class CalculatorTest {
    @Test
    fun divide_validInput() {
        assertEquals(5, Calculator().divide(10, 2))
        // Покрыт: divide() happy-path (ветка else)
        // Не покрыт: ветка деления на ноль
    }

    @Test
    fun add_addsNumbers() {
        assertEquals(3, Calculator().add(1, 2))
    }

    @Test
    fun isPositive_true() {
        assertTrue(Calculator().isPositive(5))
    }

    // Нет теста для divide с b = 0 => для этой точки ветвления branch coverage = 50%.
}
```

### Анализ Отчётов Покрытия

```bash
# Генерация отчёта
./gradlew jacocoTestReport

# Просмотр отчёта (macOS)
open app/build/reports/jacoco/jacocoTestReport/html/index.html
```

Пример интерпретации отчёта:

```text
Package: com.example.data
 Class: UserRepository (85% coverage)
   getUser()    - 100%
   updateUser() - 90%  (пропущена ветка обработки ошибки)
   deleteUser() - 0%   (не тестируется)
```

### Поиск «дыр» В Покрытии (пример)

```kotlin
// Оригинальный код
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState = _uiState.asStateFlow()

    fun loadUser(id: String) {
        viewModelScope.launch {
            try {
                val user = repository.getUser(id)  // Строка 1
                _uiState.value = UiState.Success(user)  // Строка 2
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message)  // Строка 3 - изначально не покрыта
            }
        }
    }

    fun refresh(currentUserId: String) {  // Изначально не покрыт тестами
        loadUser(currentUserId)
    }
}

// Отчёт до добавления тестов (примерная оценка):
// loadUser: ~66% (строки 1 и 2 покрыты, строка 3 нет)
// refresh: 0% (никогда не вызывается в тестах)

// Добавляем недостающие тесты (эскиз, псевдокод поведения double/mocking опущен)
@Test
fun loadUser_error() = runTest {
    repository.shouldReturnError = true
    viewModel.loadUser("1")
    assertTrue(viewModel.uiState.value is UiState.Error)  // Теперь покрыта строка 3
}

@Test
fun refresh_reloadsUser() = runTest {
    viewModel.refresh("1")  // Теперь покрыт refresh()
    // Дополнительные проверки...
}
```

### Покрытие По Слоям (пример целей)

```kotlin
val coverageTargets = mapOf(
    "ViewModel" to 85,       // Пример целевых значений
    "Repository" to 80,
    "UseCase" to 90,
    "UI/Composables" to 50,
    "DataSource" to 75,
    "Mapper" to 95,
    "Utility" to 90
)
```

Значения выше — ориентиры, а не жёсткий стандарт; выбирайте под контекст проекта.

### Баланс Качества И Процента Покрытия

Высокое покрытие само по себе не гарантирует хорошие тесты.

```kotlin
// ПЛОХО: 100% покрытия, но тест бесполезен
@Test
fun badTest() {
    val calculator = Calculator()
    calculator.add(1, 2)  // Код выполняется, но ничего не проверяется
    // Покрытие есть, уверенности нет
}

// ХОРОШО: то же покрытие, но с проверкой поведения
@Test
fun goodTest() {
    val calculator = Calculator()
    val result = calculator.add(1, 2)
    assertEquals(3, result)  // Проверяется корректность результата
}
```

### Mutation Testing (для Оценки Качества тестов)

Пример для JVM-модулей (для Android app-модулей потребуется дополнительная настройка; конфигурация может меняться с версиями плагина):

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

### Исключения Из Покрытия

```kotlin
// Пример: исключаем сгенерированный код (аннотация условна; используйте реальную @Generated из нужного пакета)
@Generated
class User_Impl : User

// Пример: исключаем только отладочный код (аннотация DebugOnly условна, может быть кастомной)
@DebugOnly
fun debugPrint(message: String) {
    Log.d("DEBUG", message)
}
```

```gradle
// Эскиз конфигурации JaCoCo: исключаем сгенерированный/инфраструктурный код
jacocoTestReport {
    classDirectories.setFrom(files(classDirectories.files.collect {
        fileTree(dir: it, excludes: [
            '**/*_Impl.*',          // Сгенерированные реализации
            '**/*DebugOnly*.*',     // Отладочные утилиты
            '**/*Module*.class',    // DI-модули (по необходимости)
            '**/*Component*.class'  // DI-компоненты (по необходимости)
            // Не исключайте всё подряд, чтобы не скрыть реальную логику
        ])
    }))
}
```

### Интеграция С CI/CD

```yaml
# GitHub Actions (пример)
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

### Пример Дашборда Покрытия

```kotlin
// Концептуальный пример кастомного репортера покрытия (псевдокод для иллюстрации идей)
class CoverageReporter {
    fun generateReport(jacocoReport: File): CoverageReport {
        val doc = parseXml(jacocoReport) // предположим, что есть утилита для парсинга XML

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

### Best Practices (RU)

1. Устанавливайте реалистичные цели покрытия (часто 70–85%+ для ключевой логики) по слоям — как ориентир, а не жёсткое требование.
2. Фокусируйтесь на критичных путях и обработке ошибок, а не только на общей цифре.
3. Исключайте из метрик сгенерированный/фреймворк/boilerplate-код, чтобы не искажать картину.
4. Следите за branch coverage для сложных условий.
5. Дополняйте метрики покрытием с помощью mutation testing и похожих техник.
6. Отслеживайте тренд покрытия по модулям/слоям во времени.
7. Просматривайте отчёты покрытия на code review.
8. Не жертвуйте качеством и скоростью тестов ради красивого процента.
9. Покрывайте edge cases, null/error-флоу, конкурентные сценарии (если актуально).
10. Встраивайте проверки покрытия в CI/CD, чтобы не допускать регрессии.

---

## Answer (EN)

Test coverage metrics help identify untested code, but high coverage doesn't guarantee quality. Understanding metrics and balancing coverage with meaningful tests is crucial.

The snippets below are examples/templates. Exact configuration depends on your Android Gradle Plugin (AGP), Gradle, and JaCoCo versions. Verify task names and paths in your project instead of assuming they exist as-is.

### JaCoCo Setup

Example JaCoCo configuration for Android (simplified; exact paths depend on AGP version and project setup):

```gradle
// build.gradle (app module)
plugins {
    id 'com.android.application'
    id 'jacoco'
}

android {
    buildTypes {
        debug {
            // For Android instrumented coverage with older AGP; may be removed or unsupported in newer versions
            testCoverageEnabled true
        }
    }
}

// Unit test + (optionally) instrumentation coverage report
// Template: ensure tasks/directories match your AGP/Gradle setup.
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

// Combined report for unit + instrumentation tests (sketch; version-dependent tasks)
tasks.register('jacocoFullReport', JacocoReport) {
    dependsOn 'testDebugUnitTest'
    dependsOn 'createDebugCoverageReport' // ensure this task exists in your project

    // Configure sourceDirectories, classDirectories, executionData similar to jacocoTestReport
}

// Coverage verification (example; exact configuration depends on the JaCoCo Gradle plugin setup)

tasks.register('jacocoVerification', JacocoCoverageVerification) {
    dependsOn 'jacocoTestReport'

    violationRules {
        rule {
            limit {
                minimum = 0.80 // example: 80% minimum overall coverage
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

Note: Treat this as an illustrative template. Actual task names, directories, and `testCoverageEnabled` availability vary with AGP/Gradle versions.

### Understanding Coverage Metrics

- Line Coverage: percentage of executed lines.
- Branch Coverage: percentage of executed branches (if/else, switch, etc.).
- Method Coverage: percentage of executed methods.
- Class Coverage: percentage of classes with at least one executed method.

```kotlin
// Example with coverage analysis (valid Kotlin code)
class Calculator {
    fun divide(a: Int, b: Int): Int {  // Affects line and branch coverage
        if (b == 0) {                  // Branch coverage - 2 branches
            throw IllegalArgumentException("Division by zero")
        }
        return a / b
    }

    fun add(a: Int, b: Int): Int {
        return a + b
    }

    fun isPositive(n: Int): Boolean {  // Method coverage example
        return n > 0
    }
}

class CalculatorTest {
    @Test
    fun divide_validInput() {
        assertEquals(5, Calculator().divide(10, 2))
        // Covers: divide() happy path (else branch)
        // Missing: division-by-zero branch
    }

    @Test
    fun add_addsNumbers() {
        assertEquals(3, Calculator().add(1, 2))
    }

    @Test
    fun isPositive_true() {
        assertTrue(Calculator().isPositive(5))
    }

    // Missing test for divide-by-zero => for that branch point, branch coverage is 50%.
}
```

### Analyzing Coverage Reports

```bash
# Generate report
./gradlew jacocoTestReport

# View report (macOS)
open app/build/reports/jacoco/jacocoTestReport/html/index.html
```

Coverage Report Interpretation (example):

```text
Package: com.example.data
 Class: UserRepository (85% coverage)
   getUser()    - 100%
   updateUser() - 90%  (missing error branch)
   deleteUser() - 0%   (not tested)
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
                _uiState.value = UiState.Error(e.message)  // Line 3 - initially NOT COVERED
            }
        }
    }

    fun refresh(currentUserId: String) {  // initially NOT COVERED
        loadUser(currentUserId)
    }
}

// Coverage report (before extra tests, approximate illustration):
// loadUser: ~66% (Lines 1,2 covered, Line 3 not covered)
// refresh: 0% (never called in tests)

// Add missing tests (sketch; mocking/dispatcher details omitted)
@Test
fun loadUser_error() = runTest {
    repository.shouldReturnError = true
    viewModel.loadUser("1")
    assertTrue(viewModel.uiState.value is UiState.Error)  // Now covers Line 3
}

@Test
fun refresh_reloadsUser() = runTest {
    viewModel.refresh("1")  // Now covers refresh()
    // assertions...
}
```

### Coverage by Layer (Example Targets)

```kotlin
val coverageTargets = mapOf(
    "ViewModel" to 85,       // Example target values
    "Repository" to 80,
    "UseCase" to 90,
    "UI/Composables" to 50,
    "DataSource" to 75,
    "Mapper" to 95,
    "Utility" to 90
)
```

These numbers are guidelines, not strict rules; adjust to your project's context.

### Quality Vs Coverage Balance

High coverage alone doesn't mean tests are good.

```kotlin
// BAD: 100% coverage but meaningless test
@Test
fun badTest() {
    val calculator = Calculator()
    calculator.add(1, 2)  // Executes code but doesn't assert anything
    // Coverage: lines executed, but behavior not verified
}

// GOOD: Same coverage but meaningful assertion
@Test
fun goodTest() {
    val calculator = Calculator()
    val result = calculator.add(1, 2)
    assertEquals(3, result)  // Verifies behavior
}
```

### Mutation Testing (for Quality)

Example (for JVM modules; Android app modules may require extra setup; plugin versions may change):

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
// Exclude generated code (annotation is illustrative; use the appropriate @Generated import for your toolchain)
@Generated
class User_Impl : User

// Exclude debug-only code (DebugOnly is illustrative; could be a custom annotation)
@DebugOnly
fun debugPrint(message: String) {
    Log.d("DEBUG", message)
}
```

```gradle
// JaCoCo configuration sketch: exclude generated/infra code; adjust patterns carefully
jacocoTestReport {
    classDirectories.setFrom(files(classDirectories.files.collect {
        fileTree(dir: it, excludes: [
            '**/*_Impl.*',          // Generated implementations
            '**/*DebugOnly*.*',     // Debug utilities
            '**/*Module*.class',    // DI modules (if appropriate)
            '**/*Component*.class'  // DI components (if appropriate)
            // Avoid blanket exclusion of all inner/anonymous classes unless intentional
        ])
    }))
}
```

### CI/CD Integration

```yaml
# GitHub Actions (example)
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
// Custom coverage reporter (conceptual; uses pseudo-APIs for brevity)
class CoverageReporter {
    fun generateReport(jacocoReport: File): CoverageReport {
        val doc = parseXml(jacocoReport) // assume a helper for XML parsing exists

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

1. Set realistic coverage goals (commonly 70–85%+ for core logic) per layer; treat them as guidance, not dogma.
2. Focus on critical paths and error handling, not just the headline percentage.
3. Exclude generated/framework/boilerplate code where appropriate to avoid skewing metrics.
4. Pay attention to branch coverage for complex conditionals.
5. Combine coverage metrics with mutation testing or similar techniques.
6. Track coverage trends over time per module/layer.
7. Review coverage reports during code reviews.
8. Do not sacrifice test quality or speed for coverage numbers.
9. Include edge cases, null/error flows, and concurrency scenarios where relevant.
10. Integrate coverage checks into the CI/CD pipeline to catch regressions.

---

## Follow-ups

- [[c-testing]]
- [[q-what-is-diffutil-for--android--medium]]

## References

- [Local Unit Tests](https://developer.android.com/training/testing/local-tests)
- [Android Documentation](https://developer.android.com/docs)

## Related Questions

### Related (Medium)
- [[q-testing-viewmodels-turbine--android--medium]] - Testing
- [[q-testing-compose-ui--android--medium]] - Testing
- [[q-compose-testing--android--medium]] - Testing
- [[q-robolectric-vs-instrumented--android--medium]] - Testing
- [[q-screenshot-snapshot-testing--android--medium]] - Testing

### Advanced (Harder)
- [[q-testing-coroutines-flow--android--hard]] - Testing
