---
id: test-001
title: "Flaky Test Prevention / Предотвращение нестабильных тестов"
aliases: ["Flaky Test Prevention", "Предотвращение нестабильных тестов"]
topic: cs
subtopics: [testing, best-practices]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-testing, q-robolectric-vs-instrumented--android--medium, q-testing-compose-ui--android--medium]
created: 2025-10-15
updated: 2025-11-11
sources: []
tags: [difficulty/medium, stability, testing/best-practices, testing/flaky-tests]

---
# Вопрос (RU)

> Как выявлять и исправлять flaky тесты? Обрабатывайте проблемы с таймингом, изоляцию тестов, очистку ресурсов.

# Question (EN)

> How to identify and fix flaky tests? Handle timing issues, test isolation, and resource cleanup.

---

## Ответ (RU)

Flaky тесты — тесты, которые периодически падают без изменений в коде. Они подрывают доверие к тестовому покрытию и тратят время разработчиков на расследование ложных срабатываний.

### Основные Причины

**1. Проблемы с таймингом**

```kotlin
@Test
fun flakyTest() {
    viewModel.loadData()
    Thread.sleep(100)  // ❌ Ненадежно: нет гарантии, что данные загрузились
    assertEquals("Data", viewModel.data.value)
}

@Test
fun stableTest() = runTest {
    viewModel.loadData()
    advanceUntilIdle()  // ✅ Корректная синхронизация с тестовым диспетчером
    assertEquals("Data", viewModel.data.value)
}
```

**2. Разделяемое состояние**

```kotlin
class FlakyTest {
    companion object {
        var counter = 0  // ❌ Общее состояние между тестами
    }

    @Test
    fun test1() {
        counter++
        assertEquals(1, counter)  // Падает, если test2 выполнился первым
    }
}

class StableTest {
    private var counter = 0  // ✅ Изолированное состояние

    @Test
    fun test1() {
        counter++
        assertEquals(1, counter)
    }
}
```

**3. Недетерминированные данные**

```kotlin
@Test
fun flakyTest() {
    val value = Random.nextInt()  // ❌ Непредсказуемый результат
    assertTrue(value > 0)
}

@Test
fun stableTest() {
    val random = Random(seed = 12345)  // ✅ Воспроизводимая последовательность
    val value = random.nextInt(100)
    assertTrue(value >= 0)  // Проверка согласована с диапазоном nextInt(100)
}
```

**4. Внешние зависимости**

```kotlin
@Test
fun flakyTest() {
    val response = apiService.getUser("123")  // ❌ Реальная сеть делает тест нестабильным
    assertEquals("John", response.name)
}

@Test
fun stableTest() {
    val mockApi = mockk<ApiService>()
    coEvery { mockApi.getUser("123") } returns User("John")  // ✅ Мок внешнего сервиса
    assertEquals("John", mockApi.getUser("123").name)
}
```

### Исправление Проблем

**Синхронизация UI в Compose**

```kotlin
@Test
fun waitForUpdate() {
    composeTestRule.setContent { MyScreen() }
    composeTestRule.onNodeWithTag("button").performClick()

    composeTestRule.waitUntil(timeoutMillis = 5000) {  // ✅ Явное ожидание, завязанное на условие
        composeTestRule.onAllNodesWithText("Updated")
            .fetchSemanticsNodes()
            .isNotEmpty()
    }
}
```

**Очистка ресурсов**

```kotlin
class ProperCleanupTest {
    private lateinit var database: AppDatabase

    @Before
    fun setup() {
        // Получите корректный context (например, через ApplicationProvider или инструментальные API)
        database = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java).build()
    }

    @After
    fun tearDown() {
        database.close()  // ✅ Всегда корректно освобождайте ресурсы
    }
}
```

### Обнаружение И Мониторинг

**Запуск тестов многократно:**

```bash
for i in {1..100}; do
  ./gradlew test --tests "*.FlakyTest" || echo "Failed on $i"
done
```

**Gradle Test Retry Plugin (для выявления нестабильности, а не маскировки проблем):**

```gradle
plugins {
    id 'org.gradle.test-retry'
}

tasks.withType(Test) {
    retry {
        maxRetries = 3
        maxFailures = 5
    }
}
```

### Лучшие Практики

1. Используйте `runTest` и управляемые тестовые диспетчеры (например, `advanceUntilIdle()`) для корутин.
2. Избегайте `Thread.sleep()` — используйте `waitUntil`, `IdlingResource` и другие механизмы синхронизации.
3. Мокируйте внешние зависимости (сеть, БД, файлы).
4. Очищайте состояние и ресурсы в `@Before` и `@After`.
5. Используйте фиксированный seed для `Random`.
6. Делайте тесты независимыми от порядка выполнения.
7. Используйте in-memory БД вместо реальных, когда это возможно.
8. Контролируйте время через тестовые диспетчеры и тестовые часы (например, `TestDispatcher`, `mainClock`).
9. Применяйте retry только как последнюю меру и инструмент диагностики, а не для сокрытия flaky-тестов.

## Answer (EN)

Flaky tests are tests that intermittently fail without code changes. They undermine confidence in test suites and waste developer time on investigating false failures.

### Common Causes

**1. Timing issues**

```kotlin
@Test
fun flakyTest() {
    viewModel.loadData()
    Thread.sleep(100)  // ❌ Unreliable: no guarantee data is loaded
    assertEquals("Data", viewModel.data.value)
}

@Test
fun stableTest() = runTest {
    viewModel.loadData()
    advanceUntilIdle()  // ✅ Proper synchronization with the test dispatcher
    assertEquals("Data", viewModel.data.value)
}
```

**2. Shared state**

```kotlin
class FlakyTest {
    companion object {
        var counter = 0  // ❌ Shared across tests
    }

    @Test
    fun test1() {
        counter++
        assertEquals(1, counter)  // Fails if test2 ran first
    }
}

class StableTest {
    private var counter = 0  // ✅ Isolated state

    @Test
    fun test1() {
        counter++
        assertEquals(1, counter)
    }
}
```

**3. Non-deterministic data**

```kotlin
@Test
fun flakyTest() {
    val value = Random.nextInt()  // ❌ Unpredictable
    assertTrue(value > 0)
}

@Test
fun stableTest() {
    val random = Random(seed = 12345)  // ✅ Reproducible sequence
    val value = random.nextInt(100)
    assertTrue(value >= 0)  // Check aligned with nextInt(100) range
}
```

**4. External dependencies**

```kotlin
@Test
fun flakyTest() {
    val response = apiService.getUser("123")  // ❌ Real network makes test flaky
    assertEquals("John", response.name)
}

@Test
fun stableTest() {
    val mockApi = mockk<ApiService>()
    coEvery { mockApi.getUser("123") } returns User("John")  // ✅ Mock external service
    assertEquals("John", mockApi.getUser("123").name)
}
```

### Fixing Issues

**UI synchronization in Compose**

```kotlin
@Test
fun waitForUpdate() {
    composeTestRule.setContent { MyScreen() }
    composeTestRule.onNodeWithTag("button").performClick()

    composeTestRule.waitUntil(timeoutMillis = 5000) {  // ✅ Explicit, condition-based wait
        composeTestRule.onAllNodesWithText("Updated")
            .fetchSemanticsNodes()
            .isNotEmpty()
    }
}
```

**Resource cleanup**

```kotlin
class ProperCleanupTest {
    private lateinit var database: AppDatabase

    @Before
    fun setup() {
        // Obtain a valid context (e.g., via ApplicationProvider or instrumentation APIs)
        database = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java).build()
    }

    @After
    fun tearDown() {
        database.close()  // ✅ Always release resources properly
    }
}
```

### Detection and Monitoring

**Run tests multiple times:**

```bash
for i in {1..100}; do
  ./gradlew test --tests "*.FlakyTest" || echo "Failed on $i"
done
```

**Gradle Test Retry Plugin (for detecting flakiness, not hiding it):**

```gradle
plugins {
    id 'org.gradle.test-retry'
}

tasks.withType(Test) {
    retry {
        maxRetries = 3
        maxFailures = 5
    }
}
```

### Best Practices

1. Use `runTest` and controlled test dispatchers (e.g., `advanceUntilIdle()`) for coroutines.
2. Avoid `Thread.sleep()` — use `waitUntil`, `IdlingResource`, and proper synchronization.
3. Mock external dependencies (network, DB, files).
4. Clean up state and resources in `@Before` and `@After`.
5. Use a fixed seed for `Random`.
6. Make tests independent of execution order.
7. Prefer in-memory databases over real ones where appropriate.
8. Control time via test dispatchers and test clocks (e.g., `TestDispatcher`, `mainClock`).
9. Apply retries only as a last resort and as a diagnostic tool, not to mask flaky tests.

---

## Дополнительные Вопросы (RU)

- Как вы бы реализовали собственный инструмент выявления нестабильных тестов в CI/CD?
- Какие метрики вы бы отслеживали для измерения стабильности тестового набора со временем?
- Как вы балансируете стратегии повторных запусков и исправление корневых причин?
- Какую роль играют `IdlingResource` в стабильности тестов Espresso?
- Как вы будете отлаживать тест, который проходит локально, но падает в CI?

## Follow-ups

- How would you implement a custom flakiness detection tool in CI/CD?
- What metrics would you track to measure test suite stability over time?
- How do you balance retry strategies vs fixing root causes?
- What role do IdlingResources play in Espresso test stability?
- How would you debug a test that passes locally but fails in CI?

## Ссылки (RU)

- [[c-testing]] — основы тестирования
- Gradle Test Retry Plugin documentation
- JUnit TestRule и Extension документация

## References

- [[c-testing]] - Testing fundamentals
- Gradle Test Retry Plugin documentation
- JUnit TestRule and Extension documentation

## Связанные Вопросы (RU)

### Предварительные (Prerequisites)

- [[q-testing-compose-ui--android--medium]] - основы UI-тестирования

### Связанные (Related)

- [[q-testing-viewmodels-turbine--android--medium]] - тестирование `ViewModel`
- [[q-robolectric-vs-instrumented--android--medium]] - типы тестов

### Продвинутые (Advanced)

- [[q-testing-coroutines-flow--android--hard]] - паттерны тестирования асинхронного кода

## Related Questions

### Prerequisites

- [[q-testing-compose-ui--android--medium]] - UI testing basics

### Related

- [[q-testing-viewmodels-turbine--android--medium]] - `ViewModel` testing
- [[q-robolectric-vs-instrumented--android--medium]] - Test types

### Advanced

- [[q-testing-coroutines-flow--android--hard]] - Async testing patterns
