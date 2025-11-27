---
id: android-237
title: CI/CD Automated Testing / Автоматизированное тестирование в CI/CD
aliases: [CI/CD Automated Testing, Автоматизированное тестирование в CI/CD]
topic: android
subtopics:
  - ci-cd
  - testing-instrumented
  - testing-unit
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-gradle
  - q-accessibility-testing--android--medium
  - q-android-release-pipeline-cicd--android--hard
  - q-android-testing-strategies--android--medium
  - q-integration-testing-strategies--android--medium
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/ci-cd, android/testing-instrumented, android/testing-unit, ci-cd, difficulty/medium, testing]
date created: Saturday, November 1st 2025, 1:05:16 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---
# Вопрос (RU)
> Как организовать автоматизированное тестирование Android-приложения в CI/CD пайплайне?

# Question (EN)
> How to organize automated testing for Android applications in a CI/CD pipeline?

---

## Ответ (RU)

### Архитектура Пайплайна

**Pre-merge (быстрая обратная связь < 10 мин)**:
- Статический анализ (`lint`/`detekt`)
- Юнит-тесты (JVM)
- Критические/смоук UI-тесты (при необходимости, можно шардингом, но ограниченно по времени)
- Генерация отчетов и артефактов

**Post-merge/nightly (полное покрытие)**:
- Все релевантные инструментальные тесты
- Регрессионные проверки
- Device farm на разных API/размерах
- Тесты производительности и сбор метрик

### Стратегии Тестирования

```kotlin
// ✅ Unit-тесты: быстрые, изолированные, мокируем Android API
// Для корутин используем runTest + TestDispatcher (опущено для краткости)
class ViewModelTest {
    @Test
    fun `loadData updates state correctly`() = runTest {
        val repo = FakeRepository()
        val viewModel = MyViewModel(repo)

        viewModel.loadData()

        assertEquals(Success(data), viewModel.state.value)
    }
}
```

```kotlin
// ✅ Инструментальные: реальное устройство, проверка UI (Compose)
// На CI рекомендуется отключать анимации для стабильности
@RunWith(AndroidJUnit4::class)
class LoginFlowTest {
    @get:Rule
    val composeRule = createAndroidComposeRule<MainActivity>()

    @Test
    fun loginWithValidCredentials_navigatesToHome() {
        composeRule.onNodeWithTag("email").performTextInput("test@test.com")
        composeRule.onNodeWithTag("submit").performClick()
        composeRule.onNodeWithTag("home").assertIsDisplayed()
    }
}
```

```kotlin
// ❌ Не используйте сеть напрямую в тестах
@Test
fun loadData() {
    val data = api.fetchData() // Нестабильно!
}

// ✅ Используйте MockWebServer
@Test
fun loadData() {
    mockWebServer.enqueue(MockResponse().setBody("""{"id":1}"""))
    val data = api.fetchData()
    assertEquals(1, data.id)
}
```

### Оптимизация Скорости

```yaml
# ✅ GitHub Actions с кэшированием
name: Android CI
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 17
      # Для надёжности в Android CI обычно явно настраивают SDK/NDK при необходимости
      - uses: gradle/gradle-build-action@v2
        with:
          cache-read-only: false

      - name: Unit tests
        run: ./gradlew testDebugUnitTest --parallel --configuration-cache

      - name: Lint
        run: ./gradlew lintDebug --parallel

      - name: Upload reports
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: test-reports
          path: '**/build/reports/**'
```

```kotlin
// ✅ Шардинг для параллельного выполнения
// build.gradle.kts
android {
    testOptions {
        execution = "ANDROIDX_TEST_ORCHESTRATOR"
        animationsDisabled = true
    }
}

// CI: запуск нескольких шардов параллельно разными job'ами
// Пример одного шарда (shardIndex меняется от 0 до numShards-1)
./gradlew connectedDebugAndroidTest \
  -Pandroid.testInstrumentationRunnerArguments.numShards=4 \
  -Pandroid.testInstrumentationRunnerArguments.shardIndex=0
```

### Управление Нестабильными Тестами

```kotlin
// ✅ Стратегия карантина для flaky тестов
@FlakyTest(bugId = "ISSUE-123")
@Test
fun animationTest() {
    // Тест в карантине, не блокирует PR
}

// CI: автоматический retry (пример для инструментальных тестов)
./gradlew connectedDebugAndroidTest \
  -Pandroid.testInstrumentationRunnerArguments.numAttempts=3
```

### Отчетность И Артефакты

**Что сохранять**:
- JUnit XML (для CI-системы)
- HTML отчеты (lint, результаты тестов)
- Отчет покрытия (например, Jacoco), при необходимости объединённый для unit + instrumented (требует доп. конфигурации)
- APK/AAB для QA

**Визуализация**:
- Inline-аннотации для падений
- Дашборд с трендами (coverage, flakiness)
- Ссылки на результаты device farm

### Безопасность В CI

```yaml
# ✅ Подписание APK в защищенной среде
- name: Sign APK
  env:
    KEYSTORE_BASE64: ${{ secrets.KEYSTORE_BASE64 }}
    KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
  run: |
    echo "$KEYSTORE_BASE64" | base64 -d > keystore.jks
    ./gradlew assembleRelease \
      -Pandroid.injected.signing.store.file=keystore.jks \
      -Pandroid.injected.signing.store.password="$KEY_PASSWORD"
    rm keystore.jks

# ✅ Проверка зависимостей (supply-chain security)
- name: Verify checksums
  run: ./gradlew --write-verification-metadata sha256
  # Обычно метаданные коммитятся и далее используется --verify-configuration
```

## Answer (EN)

### Pipeline Architecture

**Pre-merge (fast feedback < 10 min)**:
- Static analysis (`lint`/`detekt`)
- Unit tests (JVM)
- Critical/smoke UI tests (optionally, sharded; keep time-bounded)
- Generate reports and artifacts

**Post-merge/nightly (full coverage)**:
- All relevant instrumented tests
- Regression checks
- Device farm across API levels/screen sizes
- Performance tests and metrics collection

### Testing Strategies

```kotlin
// ✅ Unit tests: fast, isolated, mock Android APIs
// For coroutines use runTest + proper TestDispatcher setup (omitted for brevity)
class ViewModelTest {
    @Test
    fun `loadData updates state correctly`() = runTest {
        val repo = FakeRepository()
        val viewModel = MyViewModel(repo)

        viewModel.loadData()

        assertEquals(Success(data), viewModel.state.value)
    }
}
```

```kotlin
// ✅ Instrumented: real device, UI verification (Compose)
// On CI it's recommended to disable animations for stability
@RunWith(AndroidJUnit4::class)
class LoginFlowTest {
    @get:Rule
    val composeRule = createAndroidComposeRule<MainActivity>()

    @Test
    fun loginWithValidCredentials_navigatesToHome() {
        composeRule.onNodeWithTag("email").performTextInput("test@test.com")
        composeRule.onNodeWithTag("submit").performClick()
        composeRule.onNodeWithTag("home").assertIsDisplayed()
    }
}
```

```kotlin
// ❌ Don't use network directly in tests
@Test
fun loadData() {
    val data = api.fetchData() // Flaky!
}

// ✅ Use MockWebServer
@Test
fun loadData() {
    mockWebServer.enqueue(MockResponse().setBody("""{"id":1}"""))
    val data = api.fetchData()
    assertEquals(1, data.id)
}
```

### Speed Optimization

```yaml
# ✅ GitHub Actions with caching
name: Android CI
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 17
      # In Android CI it's usually safer to configure SDK/NDK explicitly if needed
      - uses: gradle/gradle-build-action@v2
        with:
          cache-read-only: false

      - name: Unit tests
        run: ./gradlew testDebugUnitTest --parallel --configuration-cache

      - name: Lint
        run: ./gradlew lintDebug --parallel

      - name: Upload reports
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: test-reports
          path: '**/build/reports/**'
```

```kotlin
// ✅ Sharding for parallel execution
// build.gradle.kts
android {
    testOptions {
        execution = "ANDROIDX_TEST_ORCHESTRATOR"
        animationsDisabled = true
    }
}

// CI: run multiple shards in parallel via separate jobs
// Example for one shard (shardIndex varies from 0 to numShards-1)
./gradlew connectedDebugAndroidTest \
  -Pandroid.testInstrumentationRunnerArguments.numShards=4 \
  -Pandroid.testInstrumentationRunnerArguments.shardIndex=0
```

### Managing Flaky Tests

```kotlin
// ✅ Quarantine strategy for flaky tests
@FlakyTest(bugId = "ISSUE-123")
@Test
fun animationTest() {
    // Test in quarantine, doesn't block PRs
}

// CI: automatic retry (example for instrumented tests)
./gradlew connectedDebugAndroidTest \
  -Pandroid.testInstrumentationRunnerArguments.numAttempts=3
```

### Reporting and Artifacts

**What to save**:
- JUnit XML (for CI system)
- HTML reports (lint, test results)
- Coverage report (e.g., Jacoco); merged unit + instrumented coverage is possible with extra configuration
- APK/AAB for QA

**Visualization**:
- Inline annotations for failures
- Dashboard with trends (coverage, flakiness)
- Links to device farm results

### Security in CI

```yaml
# ✅ Sign APK in secure environment
- name: Sign APK
  env:
    KEYSTORE_BASE64: ${{ secrets.KEYSTORE_BASE64 }}
    KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
  run: |
    echo "$KEYSTORE_BASE64" | base64 -d > keystore.jks
    ./gradlew assembleRelease \
      -Pandroid.injected.signing.store.file=keystore.jks \
      -Pandroid.injected.signing.store.password="$KEY_PASSWORD"
    rm keystore.jks

# ✅ Verify dependencies (supply-chain security)
- name: Verify checksums
  run: ./gradlew --write-verification-metadata sha256
  # Typically the metadata is committed and then enforced via --verify-configuration
```

## Дополнительные Вопросы (RU)

- Как поддерживать процесс карантина нестабильных тестов и отслеживать метрики снижения flaky-тестов со временем?
- Какие критерии определяют состав pre-merge и nightly-наборов тестов для оптимального баланса стоимости и качества сигнала?
- Как эффективно шардировать инструментальные тесты по девайсам и ретраить только упавшие шарды?
- Какая комбинация локального, удаленного и конфигурационного кэширования даёт лучшую производительность CI?
- Как интегрировать требования по покрытию кода без значительного увеличения времени проверки PR?

## Follow-ups

- How to maintain a flaky test quarantine process and track deflake metrics over time?
- What criteria determine pre-merge vs nightly test scope for optimal cost/signal ratio?
- How to effectively shard instrumented tests across devices and retry only failed shards?
- What combination of local, remote, and configuration caching gives best CI performance?
- How to integrate code coverage requirements without adding significant overhead to PR checks?

## Ссылки (RU)

- https://docs.gradle.org/current/userguide/build_cache.html - Gradle build cache
- https://developer.android.com/studio/test - Основы тестирования Android
- https://docs.github.com/actions - Документация GitHub Actions

## References

- https://docs.gradle.org/current/userguide/build_cache.html - Gradle build cache
- https://developer.android.com/studio/test - Android testing fundamentals
- https://docs.github.com/actions - GitHub Actions documentation

## Related Questions

### Prerequisites / Concepts

- [[c-gradle]]

### Prerequisites (Easier)
- [[q-android-testing-strategies--android--medium]] - Testing strategies overview
- [[q-gradle-basics--android--easy]] - Gradle build system fundamentals

### Related (Same Level)
- [[q-android-lint-tool--android--medium]] - Static analysis with Android Lint
- [[q-build-optimization-gradle--android--medium]] - Gradle build optimization
