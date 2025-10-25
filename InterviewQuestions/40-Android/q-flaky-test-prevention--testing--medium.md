---
id: 20251012-1227139
title: "Flaky Test Prevention / Предотвращение нестабильных тестов"
topic: testing
difficulty: medium
status: draft
moc: moc-android
related: [q-16kb-dex-page-size--android--medium, q-compose-navigation-advanced--jetpack-compose--medium, q-how-to-create-animations-in-android--android--medium]
created: 2025-10-15
tags: [best-practices, difficulty/medium, flaky-tests, stability]
date created: Saturday, October 25th 2025, 1:26:29 pm
date modified: Saturday, October 25th 2025, 4:51:58 pm
---

# Question (EN)

> Identify and fix flaky tests. Handle timing issues, test isolation, resource cleanup. Implement retry strategies.

# Вопрос (RU)

> Выявляйте и исправляйте flaky тесты. Обрабатывайте проблемы с таймингом, изоляцию тестов, очистку ресурсов. Реализуйте стратегии повторных попыток.

---

## Answer (EN)

Flaky tests are tests that sometimes pass and sometimes fail without code changes. They reduce confidence in test suites and waste development time.

### Common Causes of Flaky Tests

**1. Timing Issues**

```kotlin
// FLAKY: Race condition
@Test
fun flakyTest_raceCondition() {
    viewModel.loadData()
    Thread.sleep(100)  //  Unreliable timing
    assertEquals("Data", viewModel.data.value)
}

// STABLE: Proper async handling
@Test
fun stableTest_properAsync() = runTest {
    viewModel.loadData()
    advanceUntilIdle()  //  Wait for coroutines to complete
    assertEquals("Data", viewModel.data.value)
}
```

**2. Shared State Between Tests**

```kotlin
// FLAKY: Shared mutable state
class FlakyTest {
    companion object {
        var counter = 0  //  Shared across tests
    }

    @Test
    fun test1() {
        counter++
        assertEquals(1, counter)  // Fails if test2 ran first
    }

    @Test
    fun test2() {
        counter++
        assertEquals(1, counter)  // Fails if test1 ran first
    }
}

// STABLE: Isolated state
class StableTest {
    private var counter = 0  //  Fresh instance per test

    @Test
    fun test1() {
        counter++
        assertEquals(1, counter)
    }

    @Test
    fun test2() {
        counter++
        assertEquals(1, counter)
    }
}
```

**3. Non-Deterministic Data**

```kotlin
// FLAKY: Random data
@Test
fun flakyTest_randomData() {
    val value = Random.nextInt()
    assertTrue(value > 0)  //  Fails ~50% of time
}

// STABLE: Deterministic data
@Test
fun stableTest_fixedData() {
    val value = 42
    assertTrue(value > 0)  //  Always passes
}

// Or use seeded random for controlled randomness
@Test
fun stableTest_seededRandom() {
    val random = Random(12345)  //  Same sequence every run
    val value = random.nextInt(100)
    assertTrue(value >= 0)
}
```

**4. External Dependencies**

```kotlin
// FLAKY: Real network call
@Test
fun flakyTest_realNetwork() {
    val response = apiService.getUser("123")  //  Can timeout, fail
    assertEquals("John", response.name)
}

// STABLE: Mocked dependency
@Test
fun stableTest_mockedNetwork() = runTest {
    val mockApi = mockk<ApiService>()
    coEvery { mockApi.getUser("123") } returns User("123", "John")

    val response = mockApi.getUser("123")  //  Always returns same data
    assertEquals("John", response.name)
}
```

**5. Test Order Dependencies**

```kotlin
// FLAKY: Depends on test order
class OrderDependentTests {
    @Test
    fun test1_createUser() {
        database.insert(User("1", "John"))
    }

    @Test
    fun test2_getUser() {
        //  Assumes test1 ran first
        val user = database.getUser("1")
        assertEquals("John", user?.name)
    }
}

// STABLE: Each test self-contained
class IndependentTests {
    @Before
    fun setup() {
        database.clearAllTables()
    }

    @Test
    fun test1_createUser() {
        database.insert(User("1", "John"))
        val user = database.getUser("1")
        assertEquals("John", user?.name)
    }

    @Test
    fun test2_getUser() {
        //  Setup own data
        database.insert(User("2", "Jane"))
        val user = database.getUser("2")
        assertEquals("Jane", user?.name)
    }
}
```

### Fixing Timing Issues

**Problem: UI Not Updated**

```kotlin
// FLAKY
@Test
fun flakyTest_uiUpdate() {
    composeTestRule.setContent { MyScreen() }
    composeTestRule.onNodeWithTag("button").performClick()
    composeTestRule.onNodeWithText("Updated").assertExists()  //  May not update yet
}

// STABLE: Wait for condition
@Test
fun stableTest_waitForUpdate() {
    composeTestRule.setContent { MyScreen() }
    composeTestRule.onNodeWithTag("button").performClick()

    composeTestRule.waitUntil(timeoutMillis = 5000) {
        composeTestRule
            .onAllNodesWithText("Updated")
            .fetchSemanticsNodes()
            .isNotEmpty()
    }

    composeTestRule.onNodeWithText("Updated").assertExists()  //  Waits for condition
}
```

**Problem: Coroutine Not Complete**

```kotlin
// FLAKY
@Test
fun flakyTest_coroutineNotComplete() = runTest {
    viewModel.loadData()
    assertEquals(LoadState.Success, viewModel.state.value)  //  May still be loading
}

// STABLE: Advance time
@Test
fun stableTest_coroutineComplete() = runTest {
    viewModel.loadData()
    advanceUntilIdle()  //  Wait for all coroutines
    assertEquals(LoadState.Success, viewModel.state.value)
}
```

**Problem: Animation Not Finished**

```kotlin
// FLAKY
@Test
fun flakyTest_animationRunning() {
    composeTestRule.setContent { AnimatedScreen() }
    composeTestRule.onNodeWithTag("animated").assertExists()
    //  Animation may still be running
}

// STABLE: Control time
@Test
fun stableTest_animationControlled() {
    composeTestRule.mainClock.autoAdvance = false
    composeTestRule.setContent { AnimatedScreen() }

    composeTestRule.mainClock.advanceTimeBy(500)  //  Control animation timing
    composeTestRule.waitForIdle()

    composeTestRule.onNodeWithTag("animated").assertExists()
}
```

### Resource Cleanup

```kotlin
class ProperCleanupTest {
    private lateinit var database: AppDatabase
    private lateinit var tempFile: File

    @Before
    fun setup() {
        // Create resources
        database = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java).build()
        tempFile = File.createTempFile("test", ".tmp")
    }

    @After
    fun tearDown() {
        //  Always cleanup
        database.close()
        tempFile.delete()
    }

    @Test
    fun test() {
        // Test code
    }
}

// For JUnit 5
class ModernCleanupTest {
    @RegisterExtension
    val database = DatabaseExtension()

    @Test
    fun test() {
        // Extension handles cleanup
    }
}
```

### Test Isolation Strategies

**1. Fresh State Per Test**

```kotlin
@RunWith(AndroidJUnit4::class)
class IsolatedTests {
    //  New instance per test method
    private val repository = TestRepository()

    @Before
    fun resetState() {
        repository.clear()  //  Clean slate
    }

    @Test
    fun test1() {
        repository.addItem("A")
        assertEquals(1, repository.count())
    }

    @Test
    fun test2() {
        repository.addItem("B")
        assertEquals(1, repository.count())  // Always 1, not 2
    }
}
```

**2. Separate Test Instances**

```kotlin
// Use @TestInstance for JUnit 5
@TestInstance(TestInstance.Lifecycle.PER_METHOD)  // Default
class PerMethodTests {
    // New instance created for each test
}

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class PerClassTests {
    // Single instance shared across tests
    // Requires manual cleanup!

    @AfterEach
    fun cleanup() {
        // Reset state
    }
}
```

### Retry Strategies

**Gradle Test Retry Plugin**

```gradle
plugins {
    id 'org.gradle.test-retry' version '1.5.4'
}

tasks.withType(Test) {
    retry {
        maxRetries = 3
        maxFailures = 5
        failOnPassedAfterRetry = false
    }
}
```

**Custom Retry Rule (JUnit 4)**

```kotlin
class RetryRule(private val retryCount: Int = 3) : TestRule {
    override fun apply(base: Statement, description: Description): Statement {
        return object : Statement() {
            override fun evaluate() {
                var lastThrowable: Throwable? = null

                for (i in 0 until retryCount) {
                    try {
                        base.evaluate()
                        return  // Success
                    } catch (t: Throwable) {
                        lastThrowable = t
                        println("Test ${description.methodName} failed (attempt ${i + 1}/$retryCount)")
                    }
                }

                throw lastThrowable!!
            }
        }
    }
}

class FlakyTest {
    @get:Rule
    val retryRule = RetryRule(retryCount = 3)

    @Test
    fun sometimesFails() {
        // Flaky test that might need retries
    }
}
```

**Conditional Retry**

```kotlin
class ConditionalRetryRule : TestRule {
    override fun apply(base: Statement, description: Description): Statement {
        return object : Statement() {
            override fun evaluate() {
                try {
                    base.evaluate()
                } catch (e: Throwable) {
                    // Only retry on specific exceptions
                    if (e is TimeoutException || e is NetworkException) {
                        println("Retrying due to: ${e::class.simpleName}")
                        Thread.sleep(1000)  // Backoff
                        base.evaluate()
                    } else {
                        throw e
                    }
                }
            }
        }
    }
}
```

### Detecting Flaky Tests

**1. Run Tests Multiple Times**

```bash
# Run same test 100 times
./gradlew test --tests "*.FlakyTest" --rerun-tasks

# Or use repeat
for i in {1..100}; do
    ./gradlew test --tests "*.FlakyTest" || echo "Failed on iteration $i"
done
```

**2. CI/CD Detection**

```yaml
# GitHub Actions
- name: Run tests multiple times
  run: |
      for i in {1..10}; do
        ./gradlew test || exit 1
      done
```

**3. Flakiness Score**

```kotlin
data class TestResult(
    val name: String,
    val passed: Boolean,
    val duration: Long
)

class FlakinessAnalyzer {
    fun analyzeFlakiness(results: List<TestResult>): Map<String, Double> {
        return results.groupBy { it.name }
            .mapValues { (_, runs) ->
                val failures = runs.count { !it.passed }
                failures.toDouble() / runs.size
            }
            .filter { it.value > 0.0 }  // Only flaky tests
            .toList()
            .sortedByDescending { it.second }
            .toMap()
    }
}

// Output: "UserTest.login" -> 0.15 (15% failure rate)
```

### Best Practices

1. **Use proper async handling** (runTest, waitUntil)
2. **Clean state between tests** (@Before, @After)
3. **Avoid Thread.sleep()** - use proper synchronization
4. **Mock external dependencies** (network, file system)
5. **Use deterministic test data** (no Random without seed)
6. **Make tests independent** - no order dependencies
7. **Set proper timeouts** - not too short, not too long
8. **Use IdlingResources** for Espresso tests
9. **Clean up resources** in @After or try-finally
10. **Monitor flakiness metrics** in CI/CD
11. **Fix flaky tests immediately** - don't ignore
12. **Use retries sparingly** - last resort, not solution
13. **Test in isolation** - use in-memory databases
14. **Control time** with TestDispatcher, mainClock
15. **Document known flakiness** if can't fix immediately

### Quick Checklist for Flaky Tests

When you encounter a flaky test, check:

-   [ ] Does it use Thread.sleep()? Replace with proper waiting
-   [ ] Does it share state with other tests? Isolate
-   [ ] Does it depend on test order? Make independent
-   [ ] Does it use real network/database? Mock it
-   [ ] Does it use Random? Use seeded Random
-   [ ] Does it wait for async operations? Add proper waiting
-   [ ] Does it clean up resources? Add @After cleanup
-   [ ] Does it have hardcoded timeouts? Make configurable
-   [ ] Does it test animations? Control test clock
-   [ ] Does it run reliably 100 times? Test it

## Ответ (RU)

Flaky тесты — это тесты, которые иногда проходят, а иногда падают без изменений в коде. Они снижают доверие к тестовым наборам и тратят время разработчиков.


### Основные Причины

1. **Проблемы с таймингом**: race conditions, async операции
2. **Общее состояние между тестами**: статические переменные
3. **Недетерминированные данные**: Random без seed
4. **Внешние зависимости**: реальная сеть, файловая система
5. **Зависимость от порядка тестов**: тесты зависят друг от друга

[Полные примеры исправлений, стратегий retry и обнаружения flaky тестов приведены в английском разделе]

### Лучшие Практики

1. **Используйте правильную async обработку**
2. **Очищайте состояние между тестами**
3. **Избегайте Thread.sleep()**
4. **Мокируйте внешние зависимости**
5. **Используйте детерминированные данные**
6. **Делайте тесты независимыми**
7. **Устанавливайте правильные timeouts**
8. **Очищайте ресурсы**
9. **Мониторьте метрики flakiness**
10. **Исправляйте flaky тесты немедленно**
11. **Используйте retries осторожно**
12. **Тестируйте в изоляции**
13. **Контролируйте время** с TestDispatcher
14. **Документируйте известный flakiness**
15. **Тестируйте многократно** для выявления

---

## Related Questions

### Related (Medium)

-   [[q-testing-viewmodels-turbine--android--medium]] - Testing
-   [[q-testing-compose-ui--android--medium]] - Testing
-   [[q-compose-testing--android--medium]] - Testing
-   [[q-robolectric-vs-instrumented--android--medium]] - Testing
-   [[q-screenshot-snapshot-testing--android--medium]] - Testing

### Advanced (Harder)

-   [[q-testing-coroutines-flow--android--hard]] - Testing
