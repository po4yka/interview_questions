---
id: android-087
title: Test Coverage Quality Metrics / Метрики покрытия и качества тестов
aliases:
- Test Coverage Quality Metrics
- Метрики покрытия и качества тестов
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
- q-what-is-diffutil-for--android--medium
created: 2025-10-13
updated: 2025-11-10
tags:
- android/testing-instrumented
- android/testing-unit
- coverage
- difficulty/medium
- jacoco
- metrics

---

# Вопрос (RU)
> Метрики покрытия и качества тестов

# Question (EN)
> Test Coverage Quality Metrics

---

## Ответ (RU)

Метрики покрытия тестами помогают найти непротестированный код, но высокий процент не гарантирует качество. Важно понимать типы метрик, правильно настраивать инструменты (например, JaCoCo) и следить за тем, чтобы тесты реально проверяли поведение.

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
            // Для инструментального покрытия в старых версиях AGP; в новых может быть недоступно
            testCoverageEnabled true
        }
    }
}

// Отчёт по unit-тестам (+ опционально инструментальным тестам)
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

// Сводный отчёт по unit + инструментальным тестам (эскиз)
tasks.register('jacocoFullReport', JacocoReport) {
    dependsOn 'testDebugUnitTest'
    dependsOn 'createDebugCoverageReport'

    // sourceDirectories, classDirectories, executionData настраиваются аналогично jacocoTestReport
}

// Проверка минимального покрытия

tasks.register('jacocoVerification', JacocoCoverageVerification) {
    dependsOn 'jacocoTestReport'

    violationRules {
        rule {
            limit {
                minimum = 0.80 // минимум 80% общего покрытия
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

Примечание: используйте это как шаблон; точная интеграция зависит от версии AGP.

### Понимание метрик покрытия (с примером)

- Line Coverage: доля выполненных строк кода.
- Branch Coverage: доля выполненных ветвей (if/else, switch и т.п.).
- Method Coverage: доля вызванных методов.
- Class Coverage: доля классов, где выполнен хотя бы один метод.

```kotlin
// Пример для иллюстрации метрик
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

### Анализ отчётов покрытия

```bash
# Генерация отчёта
./gradlew jacocoTestReport

# Просмотр отчёта (macOS)
open app/build/reports/jacoco/jacocoTestReport/html/index.html
```

Пример интерпретации отчёта:

```
Package: com.example.data
 Class: UserRepository (85% coverage)
   getUser()    - 100%
   updateUser() - 90%  (пропущена ветка обработки ошибки)
   deleteUser() - 0%   (не тестируется)
```

### Поиск «дыр» в покрытии (пример)

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

// Отчёт до добавления тестов:
// loadUser: ~66% (строки 1 и 2 покрыты, строка 3 нет)
// refresh: 0% (никогда не вызывается в тестах)

// Добавляем недостающие тесты (эскиз)
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

### Покрытие по слоям (пример целей)

```kotlin
val coverageTargets = mapOf(
    "ViewModel" to 85,       // Высокое покрытие презентационной/бизнес-логики
    "Repository" to 80,      // Большинство путей покрыто
    "UseCase" to 90,         // Критичная бизнес-логика
    "UI/Composables" to 50,  // Ниже приоритет для чистого UI
    "DataSource" to 75,      // Важно для целостности данных
    "Mapper" to 95,          // Простая логика — почти полностью покрыта
    "Utility" to 90          // Общие утилиты должны быть хорошо протестированы
)
```

### Баланс качества и процента покрытия

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

### Mutation testing (для оценки качества тестов)

Пример для JVM-модулей (для Android app-модулей потребуется дополнительная настройка):

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

### Исключения из покрытия

```kotlin
// Пример: исключаем сгенерированный код
@Generated
class User_Impl : User

// Пример: исключаем только отладочный код
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
            '**/*Module*.class',    // DI-модули
            '**/*Component*.class'  // DI-компоненты
            // Не исключайте всё подряд, чтобы не скрыть реальную логику
        ])
    }))
}
```

### Интеграция с CI/CD

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

### Пример дашборда покрытия

```kotlin
// Концептуальный пример кастомного репортера покрытия
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

### Best Practices (RU)

1. Устанавливайте реалистичные цели покрытия (часто 70–85%+ для ключевой логики) по слоям.
2. Фокусируйтесь на критичных путях и обработке ошибок, а не только на общей цифре.
3. Исключайте из метрик сгенерированный/фреймворк/boilerplate-код, чтобы не искажать картину.
4. Следите за branch coverage для сложных условий.
5. Дополняйте метрики покрытием с помощью mutation testing и похожих техник.
6. Отслеживайте тренд покрытия по модулям/слоям во времени.
7. Просматривайте отчёты покрытия на code review.
8. Не жертвуйте качеством и скоростью тестов ради красивого процента.
9. Покрывайте edge cases, null/error-флоу, конкуррентные сценарии (если актуально).
10. Встраивайте проверки покрытия в CI/CD, чтобы не допускать регрессии.

---

## Answer (EN)

Test coverage metrics help identify untested code, but high coverage doesn't guarantee quality. Understanding metrics and balancing coverage with meaningful tests is crucial.

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
            // For Android instrumented coverage with older AGP; may be deprecated in newer versions
            testCoverageEnabled true
        }
    }
}

// Unit test + (optionally) instrumentation coverage report
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

// Combined report for unit + instrumentation tests (sketch)
tasks.register('jacocoFullReport', JacocoReport) {
    dependsOn 'testDebugUnitTest'
    dependsOn 'createDebugCoverageReport'

    // Configure sourceDirectories, classDirectories, executionData similar to jacocoTestReport
}

// Coverage verification

tasks.register('jacocoVerification', JacocoCoverageVerification) {
    dependsOn 'jacocoTestReport'

    violationRules {
        rule {
            limit {
                minimum = 0.80 // 80% coverage minimum overall
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

Note: Exact integration (task names, directories, testCoverageEnabled support) depends on the Android Gradle Plugin version; treat this as an illustrative template.

### Understanding Coverage Metrics

- Line Coverage: percentage of executed lines.
- Branch Coverage: percentage of executed branches (if/else, switch, etc.).
- Method Coverage: percentage of executed methods.
- Class Coverage: percentage of classes with at least one executed method.

```kotlin
// Example with coverage analysis
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

    fun isPositive(n: Int): Boolean {  // Method coverage
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

```
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

// Coverage report shows (before extra tests):
// loadUser: ~66% (Lines 1,2 covered, Line 3 not covered)
// refresh: 0% (never called in tests)

// Add missing tests (sketch)
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
    "ViewModel" to 85,       // High coverage for presentation/business logic
    "Repository" to 80,      // Most paths tested
    "UseCase" to 90,         // Critical business logic
    "UI/Composables" to 50,  // Lower priority for pure UI rendering
    "DataSource" to 75,      // Data integrity important
    "Mapper" to 95,          // Simple, should be almost fully covered
    "Utility" to 90          // Reusable helpers should be well-tested
)
```

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

Example (for JVM modules; Android app modules may require extra setup):

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
```

```gradle
// JaCoCo configuration sketch: exclude generated/infra code; adjust patterns carefully
jacocoTestReport {
    classDirectories.setFrom(files(classDirectories.files.collect {
        fileTree(dir: it, excludes: [
            '**/*_Impl.*',          // Generated implementations
            '**/*DebugOnly*.*',     // Debug utilities
            '**/*Module*.class',    // DI modules
            '**/*Component*.class'  // DI components
            // Avoid blanket exclusion of all inner classes unless intentional
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
// Custom coverage reporter (conceptual example)
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

1. `Set` realistic coverage goals (commonly 70–85%+ for core logic).
2. Focus on critical paths and error handling, not just the percentage.
3. Exclude generated/framework/boilerplate code where appropriate.
4. Pay attention to branch coverage for complex conditions.
5. Combine coverage with mutation testing or similar techniques.
6. Track coverage trends over time per module/layer.
7. Review coverage reports during code reviews.
8. Do not sacrifice test quality or speed for coverage numbers.
9. Include edge cases, null/error flows, and concurrency where relevant.
10. Integrate coverage checks into the CI/CD pipeline.

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
