---
id: 20251012-160009
title: "StandardTestDispatcher vs UnconfinedTestDispatcher / StandardTestDispatcher vs UnconfinedTestDispatcher"
slug: test-dispatcher-types-kotlin-medium
topic: kotlin
subtopics:
  - coroutines
  - testing
  - test-dispatcher
  - runtest
status: draft
difficulty: medium
moc: moc-kotlin
date_created: 2025-10-12
date_updated: 2025-10-12
related_questions:
  - q-debugging-coroutines-techniques--kotlin--medium
  - q-common-coroutine-mistakes--kotlin--medium
  - q-channelflow-callbackflow-flow--kotlin--medium
tags:
  - kotlin
  - coroutines
  - testing
  - test-dispatcher
  - runtest
---

# StandardTestDispatcher vs UnconfinedTestDispatcher

## English Version

### Problem Statement

Testing coroutines requires special test dispatchers that control time and execution order. Kotlin provides `StandardTestDispatcher` and `UnconfinedTestDispatcher`, each with different behavior. Choosing the wrong one can lead to flaky tests, timing issues, or incorrect test results.

**The Question:** What's the difference between StandardTestDispatcher and UnconfinedTestDispatcher? When should you use each?

### Detailed Answer

#### Overview of Test Dispatchers

| Feature | StandardTestDispatcher | UnconfinedTestDispatcher |
|---------|------------------------|--------------------------|
| **Execution** | Queues coroutines | Executes immediately |
| **Control** | Manual advancement | Auto-advances |
| **Virtual time** | Full control | Limited control |
| **Default in runTest** | ✅ Yes (since 1.6) | ❌ No |
| **Use case** | Most tests | Tests needing immediate execution |

#### StandardTestDispatcher Behavior

**Key characteristics:**
- **Queues coroutines**: Doesn't execute until explicitly advanced
- **Controlled timing**: Full control over virtual time
- **Predictable**: Execution order is deterministic

**Basic example:**

```kotlin
@Test
fun testStandardDispatcher() = runTest {
    // runTest uses StandardTestDispatcher by default
    var value = 0

    launch {
        value = 1
        println("Launch executed: value = $value")
    }

    // Coroutine NOT executed yet (queued)
    println("After launch: value = $value") // value = 0

    // Advance virtual time to execute queued coroutines
    advanceUntilIdle()

    println("After advanceUntilIdle: value = $value") // value = 1
}

// Output:
// After launch: value = 0
// Launch executed: value = 1
// After advanceUntilIdle: value = 1
```

#### UnconfinedTestDispatcher Behavior

**Key characteristics:**
- **Executes immediately**: Coroutines run until first suspension
- **Less control**: Auto-advances after suspensions
- **Eager execution**: Runs code before returning to caller

**Basic example:**

```kotlin
@Test
fun testUnconfinedDispatcher() = runTest(UnconfinedTestDispatcher()) {
    var value = 0

    launch {
        value = 1 // Executes immediately
        println("Launch executed: value = $value")
    }

    // Coroutine already executed!
    println("After launch: value = $value") // value = 1
}

// Output:
// Launch executed: value = 1
// After launch: value = 1
```

#### runTest Default Behavior

**runTest uses StandardTestDispatcher by default (since kotlinx.coroutines 1.6):**

```kotlin
@Test
fun defaultRunTest() = runTest {
    // Uses StandardTestDispatcher
    // Need to call advanceUntilIdle() to execute queued coroutines
}

// Equivalent to:
@Test
fun explicitStandardDispatcher() = runTest(StandardTestDispatcher()) {
    // ...
}
```

#### advanceUntilIdle with StandardTestDispatcher

**advanceUntilIdle():** Executes all pending coroutines and advances time until nothing left to run.

```kotlin
@Test
fun testAdvanceUntilIdle() = runTest {
    var step = 0

    launch {
        step = 1
        delay(100)
        step = 2
        delay(200)
        step = 3
    }

    println("Before: step = $step") // 0

    advanceUntilIdle() // Runs all delays and code

    println("After: step = $step") // 3
    println("Virtual time: ${currentTime}ms") // 300ms
}
```

#### advanceTimeBy - Precise Time Control

**advanceTimeBy(millis):** Advances virtual time by specific amount.

```kotlin
@Test
fun testAdvanceTimeBy() = runTest {
    var value = "start"

    launch {
        delay(100)
        value = "after 100ms"
        delay(100)
        value = "after 200ms"
    }

    println("0ms: $value") // "start"

    advanceTimeBy(100)
    println("100ms: $value") // "after 100ms"

    advanceTimeBy(100)
    println("200ms: $value") // "after 200ms"
}
```

#### TestScope and Virtual Time

**TestScope:** Provides `currentTime` property to check virtual time.

```kotlin
@Test
fun testVirtualTime() = runTest {
    println("Start: ${currentTime}ms") // 0ms

    delay(1000)
    println("After 1s: ${currentTime}ms") // 1000ms

    delay(5000)
    println("After 6s: ${currentTime}ms") // 6000ms

    // Total real time: < 1ms (virtual time!)
}
```

#### Testing Delays and Timeouts

**Test long delays instantly:**

```kotlin
@Test
fun testLongDelay() = runTest {
    var completed = false

    launch {
        delay(1.hours.inWholeMilliseconds) // 1 hour!
        completed = true
    }

    advanceTimeBy(1.hours.inWholeMilliseconds)

    assertTrue(completed)
    // Test completes instantly (virtual time)
}

val Long.hours: Duration
    get() = Duration.parse("${this}h")
```

**Test timeout:**

```kotlin
@Test
fun testTimeout() = runTest {
    assertFailsWith<TimeoutCancellationException> {
        withTimeout(1000) {
            delay(2000) // Exceeds timeout
        }
    }
}
```

#### Testing Immediate Execution with UnconfinedTestDispatcher

**Use case: Test code that must execute before suspension**

```kotlin
class UserViewModel {
    private val _state = MutableStateFlow<State>(State.Idle)
    val state: StateFlow<State> = _state

    fun loadUser() {
        viewModelScope.launch {
            _state.value = State.Loading // Must be immediate
            delay(100)
            _state.value = State.Success
        }
    }
}

@Test
fun testImmediateStateUpdate() = runTest(UnconfinedTestDispatcher()) {
    val viewModel = UserViewModel()

    viewModel.loadUser()

    // With UnconfinedTestDispatcher: Loading state is set immediately
    assertEquals(State.Loading, viewModel.state.value)

    advanceUntilIdle()

    assertEquals(State.Success, viewModel.state.value)
}

// With StandardTestDispatcher, this test would FAIL:
@Test
fun testWithStandardDispatcher() = runTest {
    val viewModel = UserViewModel()

    viewModel.loadUser()

    // Loading state NOT set yet (coroutine queued)
    assertEquals(State.Idle, viewModel.state.value) // State is still Idle!

    advanceUntilIdle()

    assertEquals(State.Success, viewModel.state.value)
}
```

#### Common Testing Patterns

**Pattern 1: Test StateFlow updates**

```kotlin
@Test
fun testStateFlowUpdates() = runTest {
    val viewModel = UserViewModel()
    val states = mutableListOf<State>()

    backgroundScope.launch {
        viewModel.state.collect {
            states.add(it)
        }
    }

    viewModel.loadUser()

    advanceUntilIdle()

    assertEquals(
        listOf(State.Idle, State.Loading, State.Success),
        states
    )
}
```

**Pattern 2: Test multiple coroutines**

```kotlin
@Test
fun testMultipleCoroutines() = runTest {
    var result1 = 0
    var result2 = 0

    launch {
        delay(100)
        result1 = 1
    }

    launch {
        delay(200)
        result2 = 2
    }

    advanceTimeBy(100)
    assertEquals(1, result1)
    assertEquals(0, result2) // Not executed yet

    advanceTimeBy(100)
    assertEquals(1, result1)
    assertEquals(2, result2) // Now executed
}
```

**Pattern 3: Test cancellation**

```kotlin
@Test
fun testCancellation() = runTest {
    var executed = false

    val job = launch {
        delay(1000)
        executed = true
    }

    advanceTimeBy(500)
    job.cancel()

    advanceUntilIdle()

    assertFalse(executed) // Cancelled before execution
}
```

#### Mixing Dispatchers in Tests

**Background work with StandardTestDispatcher:**

```kotlin
@Test
fun testBackgroundWork() = runTest {
    val result = async(StandardTestDispatcher(testScheduler)) {
        delay(1000)
        "Result"
    }

    advanceTimeBy(1000)

    assertEquals("Result", result.await())
}
```

**Using UnconfinedTestDispatcher for specific coroutine:**

```kotlin
@Test
fun testMixedDispatchers() = runTest {
    // Test scope uses StandardTestDispatcher
    var standardValue = 0
    var unconfinedValue = 0

    launch {
        standardValue = 1 // Queued
    }

    launch(UnconfinedTestDispatcher(testScheduler)) {
        unconfinedValue = 1 // Immediate
    }

    assertEquals(0, standardValue) // Not executed yet
    assertEquals(1, unconfinedValue) // Already executed

    advanceUntilIdle()

    assertEquals(1, standardValue) // Now executed
}
```

#### Real ViewModel Testing Examples

**Example 1: Testing loading states**

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Idle)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val user = repository.getUser(userId)
                _uiState.value = UiState.Success(user)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message)
            }
        }
    }
}

sealed class UiState {
    object Idle : UiState()
    object Loading : UiState()
    data class Success(val user: User) : UiState()
    data class Error(val message: String?) : UiState()
}

@Test
fun `test user loading success`() = runTest {
    val repository = FakeUserRepository()
    val viewModel = UserViewModel(repository)

    // Collect states
    val states = mutableListOf<UiState>()
    backgroundScope.launch {
        viewModel.uiState.collect { states.add(it) }
    }

    // Trigger load
    viewModel.loadUser("123")

    // Advance to execute coroutine
    advanceUntilIdle()

    // Verify states
    assertEquals(3, states.size)
    assertTrue(states[0] is UiState.Idle)
    assertTrue(states[1] is UiState.Loading)
    assertTrue(states[2] is UiState.Success)
}
```

**Example 2: Testing debounce/throttle**

```kotlin
class SearchViewModel : ViewModel() {
    private val _query = MutableStateFlow("")
    val query: StateFlow<String> = _query

    private val _results = MutableStateFlow<List<String>>(emptyList())
    val results: StateFlow<List<String>> = _results

    init {
        viewModelScope.launch {
            query
                .debounce(300) // Wait 300ms after last input
                .collect { query ->
                    if (query.isNotEmpty()) {
                        _results.value = searchRepository.search(query)
                    }
                }
        }
    }

    fun setQuery(newQuery: String) {
        _query.value = newQuery
    }
}

@Test
fun `test search debounce`() = runTest {
    val viewModel = SearchViewModel(FakeSearchRepository())

    viewModel.setQuery("a")
    advanceTimeBy(100)

    viewModel.setQuery("ab")
    advanceTimeBy(100)

    viewModel.setQuery("abc")
    advanceTimeBy(100)

    // No search yet (debounce period not elapsed)
    assertEquals(emptyList(), viewModel.results.value)

    // Wait for debounce
    advanceTimeBy(300)

    // Now search executed
    assertTrue(viewModel.results.value.isNotEmpty())
}
```

#### Migration from Old Test API

**Old API (deprecated):**

```kotlin
// Old: TestCoroutineDispatcher
@Test
fun oldTest() = runBlockingTest { // Deprecated
    // Test code
}
```

**New API:**

```kotlin
// New: StandardTestDispatcher/UnconfinedTestDispatcher
@Test
fun newTest() = runTest {
    // Test code
}
```

**Key changes:**
- `runBlockingTest` → `runTest`
- `TestCoroutineDispatcher` → `StandardTestDispatcher`/`UnconfinedTestDispatcher`
- Auto-advancement → Manual with `advanceUntilIdle()`
- More explicit control over execution

#### Best Practices

**1. Use StandardTestDispatcher by default:**

```kotlin
@Test
fun normalTest() = runTest {
    // StandardTestDispatcher gives full control
}
```

**2. Use UnconfinedTestDispatcher when testing immediate execution:**

```kotlin
@Test
fun immediateExecutionTest() = runTest(UnconfinedTestDispatcher()) {
    // When you need eager execution
}
```

**3. Always call advanceUntilIdle():**

```kotlin
@Test
fun goodTest() = runTest {
    viewModel.loadData()

    advanceUntilIdle() // Execute all pending coroutines

    assertEquals(expected, viewModel.state.value)
}
```

**4. Collect StateFlow in backgroundScope:**

```kotlin
@Test
fun collectStateFlow() = runTest {
    val states = mutableListOf<State>()

    // Use backgroundScope, not launch
    backgroundScope.launch {
        viewModel.state.collect { states.add(it) }
    }

    // Test actions
    viewModel.doSomething()

    advanceUntilIdle()

    // Verify states
}
```

**5. Test virtual time, not real time:**

```kotlin
// ❌ BAD: Real delays
@Test
fun badTest() = runBlocking {
    delay(1000) // Actually waits 1 second!
}

// ✅ GOOD: Virtual time
@Test
fun goodTest() = runTest {
    delay(1000) // Instant (virtual time)
}
```

#### Common Mistakes

**Mistake 1: Forgetting advanceUntilIdle()**

```kotlin
// ❌ WRONG: Coroutine not executed
@Test
fun badTest() = runTest {
    var value = 0
    launch { value = 1 }

    assertEquals(1, value) // FAILS: value is still 0
}

// ✅ CORRECT
@Test
fun goodTest() = runTest {
    var value = 0
    launch { value = 1 }

    advanceUntilIdle()

    assertEquals(1, value) // PASSES
}
```

**Mistake 2: Using runBlocking in tests:**

```kotlin
// ❌ WRONG: Real time delays
@Test
fun badTest() = runBlocking {
    delay(1000) // Blocks thread for 1 second
}

// ✅ CORRECT: Virtual time
@Test
fun goodTest() = runTest {
    delay(1000) // Instant
}
```

**Mistake 3: Not using backgroundScope for collectors:**

```kotlin
// ❌ WRONG: Collection blocks test
@Test
fun badTest() = runTest {
    launch {
        flow.collect { } // Blocks forever
    }

    // This never executes
    advanceUntilIdle()
}

// ✅ CORRECT: Use backgroundScope
@Test
fun goodTest() = runTest {
    backgroundScope.launch {
        flow.collect { }
    }

    advanceUntilIdle() // Executes
}
```

**Mistake 4: Mixing real and virtual time:**

```kotlin
// ❌ WRONG: Thread.sleep is real time
@Test
fun badTest() = runTest {
    launch {
        Thread.sleep(1000) // Real delay!
    }
    advanceTimeBy(1000) // Doesn't help
}

// ✅ CORRECT: Use delay
@Test
fun goodTest() = runTest {
    launch {
        delay(1000) // Virtual delay
    }
    advanceTimeBy(1000) // Works
}
```

#### When to Use Each Dispatcher

**Use StandardTestDispatcher when:**
- Default choice for most tests
- Need full control over execution order
- Testing timing-dependent code
- Testing delays and timeouts
- Testing cancellation

**Use UnconfinedTestDispatcher when:**
- Need immediate execution before suspension
- Testing StateFlow immediate updates
- Testing code that must run before async operations
- Specific test requirements for eager execution

### Key Takeaways

1. **StandardTestDispatcher is default** - Queues coroutines
2. **UnconfinedTestDispatcher executes immediately** - Until first suspension
3. **advanceUntilIdle() is essential** - With StandardTestDispatcher
4. **Virtual time** - Tests run instantly
5. **runTest** - Preferred over runBlocking for tests
6. **backgroundScope** - For collectors that shouldn't block
7. **Control execution order** - StandardTestDispatcher gives full control
8. **Test StateFlow updates** - Collect in backgroundScope
9. **Migration** - Old API deprecated, use new test dispatchers
10. **Choose based on needs** - Standard for control, Unconfined for immediacy

---

## Русская версия

### Формулировка проблемы

Тестирование корутин требует специальных тестовых диспетчеров, которые контролируют время и порядок выполнения. Kotlin предоставляет `StandardTestDispatcher` и `UnconfinedTestDispatcher`, каждый с разным поведением. Выбор неправильного может привести к нестабильным тестам, проблемам с временем или неверным результатам тестов.

**Вопрос:** В чем разница между StandardTestDispatcher и UnconfinedTestDispatcher? Когда следует использовать каждый?

### Подробный ответ

[Полный русский перевод следует той же структуре]

### Ключевые выводы

1. **StandardTestDispatcher по умолчанию** - Ставит корутины в очередь
2. **UnconfinedTestDispatcher выполняется немедленно** - До первой приостановки
3. **advanceUntilIdle() критичен** - С StandardTestDispatcher
4. **Виртуальное время** - Тесты выполняются мгновенно
5. **runTest** - Предпочтительнее runBlocking для тестов
6. **backgroundScope** - Для коллекторов которые не должны блокировать
7. **Контроль порядка выполнения** - StandardTestDispatcher дает полный контроль
8. **Тестирование обновлений StateFlow** - Собирайте в backgroundScope
9. **Миграция** - Старый API устарел, используйте новые тестовые диспетчеры
10. **Выбирайте по потребностям** - Standard для контроля, Unconfined для немедленности

---

## Follow-ups

1. How do you test code that uses multiple dispatchers (IO, Main, Default)?
2. What's the relationship between TestScope and TestDispatcher?
3. How do you test flows that emit values continuously?
4. Can you explain how virtual time works internally?
5. How do you test code with real delays mixed with coroutine delays?
6. What happens if you don't call advanceUntilIdle() in tests?
7. How do you test coroutines that use `withContext` to switch dispatchers?

## References

- [Testing Kotlin Coroutines](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
- [Testing Coroutines on Android](https://developer.android.com/kotlin/coroutines/test)
- [TestDispatchers Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/kotlinx.coroutines.test/-test-dispatcher.html)

## Related Questions

- [[q-debugging-coroutines-techniques--kotlin--medium|Debugging coroutines]]
- [[q-common-coroutine-mistakes--kotlin--medium|Common coroutine mistakes]]
- [[q-channelflow-callbackflow-flow--kotlin--medium|Flow builders]]
