---
id: test-001
title: "Flaky Test Prevention / Предотвращение нестабильных тестов"
aliases: ["Flaky Test Prevention", "Предотвращение нестабильных тестов"]
topic: testing
subtopics: [best-practices, test-stability, test-isolation]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [q-testing-viewmodels-turbine--android--medium, q-testing-compose-ui--android--medium, q-robolectric-vs-instrumented--android--medium]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [testing, best-practices, difficulty/medium, flaky-tests, stability]
date created: Monday, October 27th 2025, 3:58:21 pm
date modified: Thursday, October 30th 2025, 12:47:51 pm
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
    Thread.sleep(100)  // ❌ Ненадежно
    assertEquals("Data", viewModel.data.value)
}

@Test
fun stableTest() = runTest {
    viewModel.loadData()
    advanceUntilIdle()  // ✅ Корректная синхронизация
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
    assertTrue(value >= 0)
}
```

**4. Внешние зависимости**

```kotlin
@Test
fun flakyTest() {
    val response = apiService.getUser("123")  // ❌ Реальная сеть
    assertEquals("John", response.name)
}

@Test
fun stableTest() = runTest {
    val mockApi = mockk<ApiService>()
    coEvery { mockApi.getUser("123") } returns User("John")  // ✅ Мок
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

    composeTestRule.waitUntil(timeoutMillis = 5000) {  // ✅ Явное ожидание
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
        database = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java).build()
    }

    @After
    fun tearDown() {
        database.close()  // ✅ Всегда очищать
    }
}
```

### Обнаружение и Мониторинг

**Запуск тестов многократно:**

```bash
for i in {1..100}; do
  ./gradlew test --tests "*.FlakyTest" || echo "Failed on $i"
done
```

**Gradle Test Retry Plugin:**

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

1. Используйте `runTest` и `advanceUntilIdle()` для корутин
2. Избегайте `Thread.sleep()` — используйте `waitUntil`, `IdlingResource`
3. Мокируйте внешние зависимости (сеть, БД, файлы)
4. Очищайте состояние в `@Before` и `@After`
5. Используйте seed для `Random`
6. Делайте тесты независимыми от порядка выполнения
7. Используйте in-memory БД вместо реальных
8. Контролируйте время через `TestDispatcher`, `mainClock`
9. Применяйте retry только как последнюю меру

## Answer (EN)

Flaky tests are tests that intermittently fail without code changes. They undermine confidence in test suites and waste developer time on false positives.

### Common Causes

**1. Timing issues**

```kotlin
@Test
fun flakyTest() {
    viewModel.loadData()
    Thread.sleep(100)  // ❌ Unreliable
    assertEquals("Data", viewModel.data.value)
}

@Test
fun stableTest() = runTest {
    viewModel.loadData()
    advanceUntilIdle()  // ✅ Proper synchronization
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
    val random = Random(seed = 12345)  // ✅ Reproducible
    val value = random.nextInt(100)
    assertTrue(value >= 0)
}
```

**4. External dependencies**

```kotlin
@Test
fun flakyTest() {
    val response = apiService.getUser("123")  // ❌ Real network
    assertEquals("John", response.name)
}

@Test
fun stableTest() = runTest {
    val mockApi = mockk<ApiService>()
    coEvery { mockApi.getUser("123") } returns User("John")  // ✅ Mock
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

    composeTestRule.waitUntil(timeoutMillis = 5000) {  // ✅ Explicit wait
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
        database = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java).build()
    }

    @After
    fun tearDown() {
        database.close()  // ✅ Always cleanup
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

**Gradle Test Retry Plugin:**

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

1. Use `runTest` and `advanceUntilIdle()` for coroutines
2. Avoid `Thread.sleep()` — use `waitUntil`, `IdlingResource`
3. Mock external dependencies (network, DB, files)
4. Clean state in `@Before` and `@After`
5. Use seeded `Random`
6. Make tests independent of execution order
7. Use in-memory databases instead of real ones
8. Control time via `TestDispatcher`, `mainClock`
9. Apply retry only as last resort

---

## Follow-ups

- How would you implement a custom flakiness detection tool in CI/CD?
- What metrics would you track to measure test suite stability over time?
- How do you balance retry strategies vs fixing root causes?
- What role do IdlingResources play in Espresso test stability?
- How would you debug a test that passes locally but fails in CI?

## References

- [[c-unit-testing]] - Testing fundamentals
- Gradle Test Retry Plugin documentation
- JUnit TestRule and Extension documentation

## Related Questions

### Prerequisites

- [[q-testing-compose-ui--android--medium]] - UI testing basics

### Related

- [[q-testing-viewmodels-turbine--android--medium]] - ViewModel testing
- [[q-robolectric-vs-instrumented--android--medium]] - Test types

### Advanced

- [[q-testing-coroutines-flow--android--hard]] - Async testing patterns
