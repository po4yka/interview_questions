---
id: android-237
title: CI/CD Automated Testing / Автоматизированное тестирование в CI/CD
aliases:
- CI/CD Automated Testing
- Автоматизированное тестирование в CI/CD
topic: android
subtopics:
- ci-cd
- gradle
- testing-instrumented
- testing-unit
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- c-gradle-build-cache
- c-test-sharding
created: 2025-10-15
updated: 2025-10-29
sources: []
tags:
- android/ci-cd
- android/gradle
- android/testing-instrumented
- android/testing-unit
- ci-cd
- difficulty/medium
- testing
date created: Thursday, October 30th 2025, 11:10:59 am
date modified: Sunday, November 2nd 2025, 1:29:32 pm
---

# Вопрос (RU)
> Как организовать автоматизированное тестирование Android-приложения в CI/CD пайплайне?

# Question (EN)
> How to organize automated testing for Android applications in a CI/CD pipeline?

---

## Ответ (RU)

### Архитектура Пайплайна

**Pre-merge (быстрая обратная связь < 10 мин)**:
- Статический анализ (lint/detekt)
- Юнит-тесты (JVM)
- Критические UI-тесты (sharded)
- Генерация отчетов и артефактов

**Post-merge/nightly (полное покрытие)**:
- Все инструментальные тесты
- Регрессионные проверки
- Device farm на разных API/размерах
- Производительность и метрики

### Стратегии Тестирования

```kotlin
// ✅ Unit-тесты: быстрые, изолированные, мокируем Android API
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
// ✅ Инструментальные: реальное устройство, проверка UI
@RunWith(AndroidJUnit4::class)
class LoginFlowTest {
    @get:Rule val composeRule = createComposeRule()

    @Test
    fun loginWithValidCredentials_navigatesToHome() {
        composeRule.setContent { LoginScreen() }
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

// CI: запуск шардов параллельно
./gradlew connectedDebugAndroidTest -Pandroid.testInstrumentationRunnerArguments.numShards=4 \
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

// CI: автоматический retry
./gradlew test --rerun-tasks --max-parallel-forks=4 \
  -Pandroid.testInstrumentationRunnerArguments.numAttempts=3
```

### Отчетность И Артефакты

**Что сохранять**:
- JUnit XML (для CI-системы)
- HTML отчеты (lint, test results)
- Jacoco покрытие (объединенное: unit + instrumented)
- APK/AAB для QA

**Визуализация**:
- Inline-аннотации для провалов
- Дашборд с трендами (coverage, flakiness)
- Ссылки на device farm результаты

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
```

## Answer (EN)

### Pipeline Architecture

**Pre-merge (fast feedback < 10 min)**:
- Static analysis (lint/detekt)
- Unit tests (JVM)
- Critical UI tests (sharded)
- Generate reports and artifacts

**Post-merge/nightly (full coverage)**:
- All instrumented tests
- Regression checks
- Device farm across API levels/screen sizes
- Performance metrics

### Testing Strategies

```kotlin
// ✅ Unit tests: fast, isolated, mock Android APIs
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
// ✅ Instrumented: real device, UI verification
@RunWith(AndroidJUnit4::class)
class LoginFlowTest {
    @get:Rule val composeRule = createComposeRule()

    @Test
    fun loginWithValidCredentials_navigatesToHome() {
        composeRule.setContent { LoginScreen() }
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

// CI: run shards in parallel
./gradlew connectedDebugAndroidTest -Pandroid.testInstrumentationRunnerArguments.numShards=4 \
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

// CI: automatic retry
./gradlew test --rerun-tasks --max-parallel-forks=4 \
  -Pandroid.testInstrumentationRunnerArguments.numAttempts=3
```

### Reporting and Artifacts

**What to save**:
- JUnit XML (for CI system)
- HTML reports (lint, test results)
- Jacoco coverage (merged: unit + instrumented)
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
```

## Follow-ups

- How to maintain a flaky test quarantine process and track deflake metrics over time?
- What criteria determine pre-merge vs nightly test scope for optimal cost/signal ratio?
- How to effectively shard instrumented tests across devices and retry only failed shards?
- What combination of local, remote, and configuration caching gives best CI performance?
- How to integrate code coverage requirements without adding significant overhead to PR checks?

## References

- https://docs.gradle.org/current/userguide/build_cache.html - Gradle build cache
- https://developer.android.com/studio/test - Android testing fundamentals
- https://docs.github.com/actions - GitHub Actions documentation

## Related Questions

### Prerequisites / Concepts

- [[c-gradle-build-cache]]
- [[c-test-sharding]]


### Prerequisites (Easier)
- [[q-android-testing-strategies--android--medium]] - Testing strategies overview
- [[q-gradle-basics--android--easy]] - Gradle build system fundamentals

### Related (Same Level)
- [[q-android-lint-tool--android--medium]] - Static analysis with Android Lint
- [[q-build-optimization-gradle--android--medium]] - Gradle build optimization

