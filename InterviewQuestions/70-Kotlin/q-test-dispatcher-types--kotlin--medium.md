---
---
---\
id: kotlin-067
title: "StandardTestDispatcher vs UnconfinedTestDispatcher / StandardTestDispatcher против UnconfinedTestDispatcher"
aliases: ["StandardTestDispatcher vs UnconfinedTestDispatcher", "StandardTestDispatcher против UnconfinedTestDispatcher"]
topic: kotlin
question_kind: coding
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-12
updated: 2025-11-09
tags: [coroutines, difficulty/medium, kotlin, runtest, test-dispatcher, testing]
moc: moc-kotlin
related: [c-coroutines, q-common-coroutine-mistakes--kotlin--medium, q-debugging-coroutines-techniques--kotlin--medium, q-suspend-functions-deep-dive--kotlin--medium]
subtopics: [coroutines, runtest, testing]
---\
# Вопрос (RU)
> В чем разница между StandardTestDispatcher и UnconfinedTestDispatcher? Когда следует использовать каждый?

---

# Question (EN)
> What's the difference between StandardTestDispatcher and UnconfinedTestDispatcher? When should you use each?

## Ответ (RU)

Тестирование корутин требует специальных тестовых диспетчеров и планировщика, которые позволяют контролировать виртуальное время и порядок выполнения. В `kotlinx-coroutines-test` есть `StandardTestDispatcher` и `UnconfinedTestDispatcher`, которые работают поверх общего `TestCoroutineScheduler`, но ведут себя по-разному. Неправильный выбор или неверные ожидания их поведения могут привести к нестабильным тестам, тайм-аутам или некорректным результатам. См. также [[c-coroutines]].

### Обзор Тестовых Диспетчеров

Ключевая идея: оба диспетчера используют виртуальное время `TestCoroutineScheduler` и не продвигают его «магическим образом» — время сдвигается `runTest` и/или явными вызовами `advanceTimeBy` / `advanceUntilIdle`.

- `StandardTestDispatcher` — ставит задачи в очередь и выполняет их детерминированно под контролем планировщика. Он является значением по умолчанию в `runTest` и подходит для большинства тестов.
- `UnconfinedTestDispatcher` — выполняет код немедленно до первой приостановки, после чего возобновление также планируется через тот же `TestCoroutineScheduler`. Не привязан к конкретному потоку и полезен, когда важны немедленные эффекты до первой приостановки.

### Поведение StandardTestDispatcher

Основные свойства:
- Все корутины ставятся в очередь и управляются `TestCoroutineScheduler`.
- Детерминированный порядок выполнения.
- Предпочитаемый диспетчер по умолчанию для юнит-тестов.

Пример (нужно «сотрудничать» с планировщиком):

```kotlin
@Test
fun testStandardDispatcher() = runTest {
    var value = 0

    val job = launch {
        value = 1
    }

    // На этом этапе корутина запланирована, но может ещё не выполниться.
    // Синхронизируемся через join или advanceUntilIdle.
    job.join() // или advanceUntilIdle()

    assertEquals(1, value)
}
```

### Поведение UnconfinedTestDispatcher

Основные свойства:
- Выполняет тело корутины немедленно в текущем стеке до первой приостановки.
- После приостановки возобновление планируется `TestCoroutineScheduler`.
- Не привязан к конкретному потоку.
- Полезен, когда требуется явно проверить немедленные эффекты до первой приостановки.

Пример:

```kotlin
@Test
fun testUnconfinedDispatcher() = runTest(UnconfinedTestDispatcher(testScheduler)) {
    var value = 0

    launch {
        value = 1 // Выполнится сразу до первой приостановки
    }

    // На этом шаге тело до первой приостановки уже выполнено
    assertEquals(1, value)
}
```

### Поведение runTest По Умолчанию

`runTest` по умолчанию использует `StandardTestDispatcher` с общим `TestCoroutineScheduler`:

```kotlin
@Test
fun defaultRunTest() = runTest {
    // Внутри используется StandardTestDispatcher(testScheduler).
}

@Test
fun explicitStandardDispatcher() = runTest(StandardTestDispatcher(testScheduler)) {
    // Эквивалентная явная конфигурация.
}
```

Особенности `runTest`:
- Интегрирован с виртуальным временем.
- Автоматически выполняет задачи, необходимые для завершения тела теста.
- Требует явного ожидания (`join`/`await`) или продвижения времени, когда вы тестируете отложенное/асинхронное поведение.

### advanceUntilIdle С StandardTestDispatcher

`advanceUntilIdle()` выполняет все задачи, запланированные в `TestCoroutineScheduler`, включая те, что следуют за задержками, пока не останется работы.

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

    assertEquals(0, step)

    advanceUntilIdle()

    assertEquals(3, step)
    assertEquals(300, currentTime)
}
```

### advanceTimeBy — Точный Контроль Времени

`advanceTimeBy(millis)` сдвигает виртуальное время и выполняет задачи, запланированные до этого момента:

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

    assertEquals("start", value)

    advanceTimeBy(100)
    assertEquals("after 100ms", value)

    advanceTimeBy(100)
    assertEquals("after 200ms", value)
}
```

### TestScope И Виртуальное Время

`runTest` предоставляет `TestScope` с:
- `currentTime` для проверки виртуального времени;
- доступом к `testScheduler` (в новых API) для создания тестовых диспетчеров.

```kotlin
@Test
fun testVirtualTime() = runTest {
    assertEquals(0, currentTime)

    delay(1000)
    assertEquals(1000, currentTime)

    delay(5000)
    assertEquals(6000, currentTime)
}
```

### Тестирование Задержек И Таймаутов

Длинные задержки выполняются мгновенно за счет виртуального времени:

```kotlin
import kotlin.time.Duration.Companion.hours

@Test
fun testLongDelay() = runTest {
    var completed = false

    launch {
        delay(1.hours) // Виртуальный 1 час
        completed = true
    }

    advanceTimeBy(1.hours.inWholeMilliseconds)

    assertTrue(completed)
}
```

Пример таймаута:

```kotlin
@Test
fun testTimeout() = runTest {
    assertFailsWith<TimeoutCancellationException> {
        withTimeout(1000) {
            delay(2000)
        }
    }
}
```

### Тестирование Немедленного Выполнения С UnconfinedTestDispatcher

`UnconfinedTestDispatcher` полезен, когда нужно проверить побочные эффекты, происходящие до первой приостановки.

Пример с `ViewModel`, использующей внедренный диспетчер:

```kotlin
class UserViewModel(
    private val dispatcher: CoroutineDispatcher,
    private val repository: UserRepository
) : ViewModel() {
    private val _state = MutableStateFlow<State>(State.Idle)
    val state: StateFlow<State> = _state

    fun loadUser() {
        viewModelScope.launch(dispatcher) {
            _state.value = State.Loading // Немедленно на UnconfinedTestDispatcher до первой приостановки
            delay(100)
            _state.value = State.Success
        }
    }
}

@Test
fun testImmediateStateUpdate() = runTest {
    val dispatcher = UnconfinedTestDispatcher(testScheduler)
    val viewModel = UserViewModel(dispatcher, FakeUserRepository())

    viewModel.loadUser()

    assertEquals(State.Loading, viewModel.state.value)

    advanceUntilIdle()

    assertEquals(State.Success, viewModel.state.value)
}

@Test
fun testWithStandardDispatcher() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    val viewModel = UserViewModel(dispatcher, FakeUserRepository())

    viewModel.loadUser()

    // Эффект запланирован; продвигаем время/очередь, чтобы его увидеть
    advanceUntilIdle()

    assertEquals(State.Success, viewModel.state.value)
}
```

### Типичные Паттерны Тестирования

Паттерн 1: тестирование обновлений `StateFlow` с `backgroundScope`:

```kotlin
@Test
fun testStateFlowUpdates() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    val viewModel = UserViewModel(dispatcher, FakeUserRepository())
    val states = mutableListOf<State>()

    backgroundScope.launch {
        viewModel.state.collect { states.add(it) }
    }

    viewModel.loadUser()

    advanceUntilIdle()

    assertEquals(listOf(State.Idle, State.Loading, State.Success), states)
}
```

Паттерн 2: тестирование нескольких корутин:

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
    assertEquals(0, result2)

    advanceTimeBy(100)
    assertEquals(2, result2)
}
```

Паттерн 3: тестирование отмены:

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

    assertFalse(executed)
}
```

### Смешивание Диспетчеров В Тестах

Используйте экземпляры диспетчеров, привязанные к одному `testScheduler`, для согласованного виртуального времени.

```kotlin
@Test
fun testBackgroundWork() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)

    val result = async(dispatcher) {
        delay(1000)
        "Result"
    }

    advanceTimeBy(1000)

    assertEquals("Result", result.await())
}
```

```kotlin
@Test
fun testMixedDispatchers() = runTest {
    var standardValue = 0
    var unconfinedValue = 0

    launch(StandardTestDispatcher(testScheduler)) {
        standardValue = 1
    }

    launch(UnconfinedTestDispatcher(testScheduler)) {
        unconfinedValue = 1 // Немедленное выполнение до первой приостановки
    }

    assertEquals(0, standardValue)
    assertEquals(1, unconfinedValue)

    advanceUntilIdle()

    assertEquals(1, standardValue)
}
```

### Примеры Тестирования Реальных `ViewModel`

Пример: тестирование состояний загрузки с внедренным диспетчером:

```kotlin
class UserViewModel(
    private val dispatcher: CoroutineDispatcher,
    private val repository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Idle)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch(dispatcher) {
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
```

```kotlin
@Test
fun `test user loading success`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    val repository = FakeUserRepository()
    val viewModel = UserViewModel(dispatcher, repository)

    val states = mutableListOf<UiState>()
    backgroundScope.launch {
        viewModel.uiState.collect { states.add(it) }
    }

    viewModel.loadUser("123")

    advanceUntilIdle()

    assertEquals(3, states.size)
    assertTrue(states[0] is UiState.Idle)
    assertTrue(states[1] is UiState.Loading)
    assertTrue(states[2] is UiState.Success)
}
```

Пример: тестирование debounce:

```kotlin
class SearchViewModel(
    private val dispatcher: CoroutineDispatcher,
    private val searchRepository: SearchRepository
) : ViewModel() {
    private val _query = MutableStateFlow("")
    val query: StateFlow<String> = _query

    private val _results = MutableStateFlow<List<String>>(emptyList())
    val results: StateFlow<List<String>> = _results

    init {
        viewModelScope.launch(dispatcher) {
            query
                .debounce(300)
                .collect { q ->
                    if (q.isNotEmpty()) {
                        _results.value = searchRepository.search(q)
                    }
                }
        }
    }

    fun setQuery(newQuery: String) {
        _query.value = newQuery
    }
}
```

```kotlin
@Test
fun `test search debounce`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    val viewModel = SearchViewModel(dispatcher, FakeSearchRepository())

    viewModel.setQuery("a")
    advanceTimeBy(100)

    viewModel.setQuery("ab")
    advanceTimeBy(100)

    viewModel.setQuery("abc")
    advanceTimeBy(100)

    // Окно debounce ещё не завершено
    assertEquals(emptyList<String>(), viewModel.results.value)

    advanceTimeBy(300)

    assertTrue(viewModel.results.value.isNotEmpty())
}
```

### Миграция Со Старого Тестового API

Старый (устаревший) подход:

```kotlin
// Устарело: runBlockingTest, TestCoroutineDispatcher, TestCoroutineScope
@Test
fun oldTest() = runBlockingTest {
    // Test code
}
```

Новый API:

```kotlin
@Test
fun newTest() = runTest {
    // Используем runTest с TestScope и тестовыми диспетчерами
}
```

Ключевые изменения:
- `runBlockingTest` → `runTest`.
- `TestCoroutineDispatcher` / `TestCoroutineScope` → `StandardTestDispatcher` / `UnconfinedTestDispatcher` + `TestScope`.
- Виртуальное время управляется `runTest` и `TestCoroutineScheduler`; при необходимости вы явно продвигаете его.

### Лучшие Практики

1. Используйте `StandardTestDispatcher` по умолчанию.
2. Применяйте `UnconfinedTestDispatcher` только когда осознанно полагаетесь на его нетерпеливое, незафиксированное поведение.
3. Для асинхронной работы:
   - Явно ожидайте задачи (`join`, `await`), или
   - Используйте `advanceTimeBy` / `advanceUntilIdle` при тестировании задержек и таймингов.
4. Собирайте `Flow` / `StateFlow` в `backgroundScope`, чтобы не блокировать основной поток теста.
5. Предпочитайте виртуальное время (`runTest`) реальным задержкам (`runBlocking`, `Thread.sleep`).

### Распространенные Ошибки

Ошибка 1: отсутствие кооперации с планировщиком:

```kotlin
@Test
fun badTest() = runTest {
    var value = 0
    launch { value = 1 }

    // Нет join / advance; возможна преждевременная проверка
    assertEquals(1, value) // Нестабильно / неверно
}

@Test
fun goodTest() = runTest {
    var value = 0
    val job = launch { value = 1 }

    job.join() // или advanceUntilIdle()

    assertEquals(1, value)
}
```

Ошибка 2: использование `runBlocking` с реальным временем:

```kotlin
@Test
fun badTest() = runBlocking {
    delay(1000) // Реальная секунда
}

@Test
fun goodTest() = runTest {
    delay(1000) // Виртуальное время
}
```

Ошибка 3: collect в основном scope теста без `backgroundScope`:

```kotlin
@Test
fun badTest() = runTest {
    // Этот collect не завершится и заблокирует тест
    collectFlow().collect { }
}

@Test
fun goodTest() = runTest {
    backgroundScope.launch {
        collectFlow().collect { }
    }

    advanceUntilIdle()
}
```

Ошибка 4: смешивание реального и виртуального времени:

```kotlin
@Test
fun badTest() = runTest {
    launch {
        Thread.sleep(1000) // Реальное время, не управляется планировщиком
    }
    advanceTimeBy(1000) // Не влияет на Thread.sleep
}

@Test
fun goodTest() = runTest {
    launch {
        delay(1000) // Виртуальное время
    }
    advanceTimeBy(1000)
}
```

### Когда Использовать Каждый Диспетчер

Используйте `StandardTestDispatcher`, когда:
- Нужна детерминированность и полный контроль порядка выполнения.
- Тестируете задержки, debounce, таймауты, отмены.
- Пишете большинство unit-тестов корутин.

Используйте `UnconfinedTestDispatcher`, когда:
- Важно немедленное выполнение до первой приостановки.
- Осознанно зависите от его поведения и понимаете последствия.

### Ключевые Выводы

1. `StandardTestDispatcher` (по умолчанию в `runTest`) — детерминированное, управляемое выполнение.
2. `UnconfinedTestDispatcher` — нетерпеливое выполнение до первой приостановки, далее под управлением того же планировщика.
3. Ни один не продвигает виртуальное время автоматически; используйте `advanceTimeBy` / `advanceUntilIdle` и корректное ожидание.
4. Предпочитайте `runTest` и виртуальное время вместо `runBlocking` / `runBlockingTest`.
5. Используйте `backgroundScope` для долгоживущих коллекций.
6. Выбирайте диспетчер по требуемой семантике: контроль против немедленных эффектов.

---

## Answer (EN)

Testing coroutines requires dedicated test dispatchers and a scheduler that control virtual time and execution order. The kotlinx.coroutines-test module provides `StandardTestDispatcher` and `UnconfinedTestDispatcher`, both backed by a shared `TestCoroutineScheduler` but with different scheduling behavior. Misunderstanding their behavior can lead to flaky tests, timeouts, or incorrect expectations.

### Overview of Test Dispatchers

| Feature | StandardTestDispatcher | UnconfinedTestDispatcher |
|---------|------------------------|--------------------------|
| Execution start | Enqueues tasks; executes via scheduler | Runs immediately until first suspension |
| `Thread` confinement | Confined to the scheduler's execution | Unconfined (may resume in different contexts) |
| Control | Deterministic, queued | Eager before first suspension, then scheduled |
| Virtual time | Uses TestCoroutineScheduler | Uses same TestCoroutineScheduler |
| Default in runTest | Yes (since 1.6) | No |
| Typical use | Default for most tests | When immediate pre-suspension execution semantics are needed |

Note: Neither dispatcher "auto-advances" time on its own. Virtual time is advanced by `runTest` and/or by explicit calls to `advanceTimeBy` / `advanceUntilIdle`.

### StandardTestDispatcher Behavior

Key characteristics:
- Queues coroutines and runs them under control of `TestCoroutineScheduler`.
- Deterministic execution order.
- Ideal default for unit tests.

Basic example (demonstrating need to cooperate with scheduler):

```kotlin
@Test
fun testStandardDispatcher() = runTest {
    var value = 0

    val job = launch {
        value = 1
    }

    // At this point, the coroutine is scheduled but may not have run yet.
    // Cooperate with the scheduler by awaiting or advancing.
    job.join() // or advanceUntilIdle()

    assertEquals(1, value)
}
```

### UnconfinedTestDispatcher Behavior

Key characteristics:
- Executes coroutine code immediately in the current call stack until the first suspension.
- After suspension, resumption is scheduled by the same `TestCoroutineScheduler`.
- Not bound to a particular thread.
- Useful when you specifically want eager behavior before the first suspension.

Basic example:

```kotlin
@Test
fun testUnconfinedDispatcher() = runTest(UnconfinedTestDispatcher(testScheduler)) {
    var value = 0

    launch {
        value = 1 // Executes immediately until first suspension
    }

    // Coroutine body up to first suspension has already run
    assertEquals(1, value)
}
```

### runTest Default Behavior

`runTest` uses `StandardTestDispatcher` with an underlying `TestCoroutineScheduler` by default:

```kotlin
@Test
fun defaultRunTest() = runTest {
    // Uses StandardTestDispatcher(testScheduler) internally.
}

@Test
fun explicitStandardDispatcher() = runTest(StandardTestDispatcher(testScheduler)) {
    // Equivalent explicit configuration.
}
```

`runTest`:
- Integrates with virtual time.
- Automatically runs scheduled tasks needed to complete the test body.
- Still requires you to either await launched coroutines (e.g., via `join`/`await`) or advance virtual time when testing delayed/async behavior.

### advanceUntilIdle with StandardTestDispatcher

`advanceUntilIdle()` executes all tasks scheduled on `TestCoroutineScheduler` (including those after delays) until there is nothing left to run.

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

    assertEquals(0, step)

    advanceUntilIdle()

    assertEquals(3, step)
    assertEquals(300, currentTime)
}
```

### advanceTimeBy - Precise Time Control

`advanceTimeBy(millis)` advances virtual time and runs tasks scheduled up to that time.

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

    assertEquals("start", value)

    advanceTimeBy(100)
    assertEquals("after 100ms", value)

    advanceTimeBy(100)
    assertEquals("after 200ms", value)
}
```

### TestScope and Virtual Time

`runTest` provides a `TestScope` with:
- `currentTime` to inspect virtual time.
- Access to `testScheduler` (in newer APIs) for creating dispatchers.

```kotlin
@Test
fun testVirtualTime() = runTest {
    assertEquals(0, currentTime)

    delay(1000)
    assertEquals(1000, currentTime)

    delay(5000)
    assertEquals(6000, currentTime)
}
```

### Testing Delays and Timeouts

`Long` delays are executed instantly via virtual time:

```kotlin
import kotlin.time.Duration.Companion.hours

@Test
fun testLongDelay() = runTest {
    var completed = false

    launch {
        delay(1.hours) // Virtual 1 hour
        completed = true
    }

    advanceTimeBy(1.hours.inWholeMilliseconds)

    assertTrue(completed)
}
```

Timeout example:

```kotlin
@Test
fun testTimeout() = runTest {
    assertFailsWith<TimeoutCancellationException> {
        withTimeout(1000) {
            delay(2000)
        }
    }
}
```

### Testing Immediate Execution with UnconfinedTestDispatcher

Use `UnconfinedTestDispatcher` when you want to assert side effects that must happen before the first suspension.

Example with a `ViewModel` using an injected dispatcher (simplified for correctness):

```kotlin
class UserViewModel(
    private val dispatcher: CoroutineDispatcher,
    private val repository: UserRepository
) : ViewModel() {
    private val _state = MutableStateFlow<State>(State.Idle)
    val state: StateFlow<State> = _state

    fun loadUser() {
        viewModelScope.launch(dispatcher) {
            _state.value = State.Loading // Immediate on UnconfinedTestDispatcher until first suspension
            delay(100)
            _state.value = State.Success
        }
    }
}
```

```kotlin
@Test
fun testImmediateStateUpdate() = runTest {
    val dispatcher = UnconfinedTestDispatcher(testScheduler)
    val viewModel = UserViewModel(dispatcher, FakeUserRepository())

    viewModel.loadUser()

    assertEquals(State.Loading, viewModel.state.value)

    advanceUntilIdle()

    assertEquals(State.Success, viewModel.state.value)
}
```

```kotlin
@Test
fun testWithStandardDispatcher() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    val viewModel = UserViewModel(dispatcher, FakeUserRepository())

    viewModel.loadUser()

    // The effect is scheduled; advance to observe it
    advanceUntilIdle()

    assertEquals(State.Success, viewModel.state.value)
}
```

### Common Testing Patterns

Pattern 1: Test `StateFlow` updates with `backgroundScope`

```kotlin
@Test
fun testStateFlowUpdates() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    val viewModel = UserViewModel(dispatcher, FakeUserRepository())
    val states = mutableListOf<State>()

    backgroundScope.launch {
        viewModel.state.collect { states.add(it) }
    }

    viewModel.loadUser()

    advanceUntilIdle()

    assertEquals(listOf(State.Idle, State.Loading, State.Success), states)
}
```

Pattern 2: Test multiple coroutines

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
    assertEquals(0, result2)

    advanceTimeBy(100)
    assertEquals(2, result2)
}
```

Pattern 3: Test cancellation

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

    assertFalse(executed)
}
```

### Mixing Dispatchers in Tests

Using dispatcher instances tied to the same `testScheduler` ensures consistent virtual time.

```kotlin
@Test
fun testBackgroundWork() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)

    val result = async(dispatcher) {
        delay(1000)
        "Result"
    }

    advanceTimeBy(1000)

    assertEquals("Result", result.await())
}
```

```kotlin
@Test
fun testMixedDispatchers() = runTest {
    var standardValue = 0
    var unconfinedValue = 0

    launch(StandardTestDispatcher(testScheduler)) {
        standardValue = 1
    }

    launch(UnconfinedTestDispatcher(testScheduler)) {
        unconfinedValue = 1 // Eager before first suspension
    }

    assertEquals(0, standardValue)
    assertEquals(1, unconfinedValue)

    advanceUntilIdle()

    assertEquals(1, standardValue)
}
```

### Real `ViewModel` Testing Examples

Example: Testing loading states with injected dispatcher

```kotlin
class UserViewModel(
    private val dispatcher: CoroutineDispatcher,
    private val repository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Idle)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch(dispatcher) {
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
```

```kotlin
@Test
fun `test user loading success`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    val repository = FakeUserRepository()
    val viewModel = UserViewModel(dispatcher, repository)

    val states = mutableListOf<UiState>()
    backgroundScope.launch {
        viewModel.uiState.collect { states.add(it) }
    }

    viewModel.loadUser("123")

    advanceUntilIdle()

    assertEquals(3, states.size)
    assertTrue(states[0] is UiState.Idle)
    assertTrue(states[1] is UiState.Loading)
    assertTrue(states[2] is UiState.Success)
}
```

Example: Testing debounce

```kotlin
class SearchViewModel(
    private val dispatcher: CoroutineDispatcher,
    private val searchRepository: SearchRepository
) : ViewModel() {
    private val _query = MutableStateFlow("")
    val query: StateFlow<String> = _query

    private val _results = MutableStateFlow<List<String>>(emptyList())
    val results: StateFlow<List<String>> = _results

    init {
        viewModelScope.launch(dispatcher) {
            query
                .debounce(300)
                .collect { q ->
                    if (q.isNotEmpty()) {
                        _results.value = searchRepository.search(q)
                    }
                }
        }
    }

    fun setQuery(newQuery: String) {
        _query.value = newQuery
    }
}
```

```kotlin
@Test
fun `test search debounce`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    val viewModel = SearchViewModel(dispatcher, FakeSearchRepository())

    viewModel.setQuery("a")
    advanceTimeBy(100)

    viewModel.setQuery("ab")
    advanceTimeBy(100)

    viewModel.setQuery("abc")
    advanceTimeBy(100)

    // Debounce window not completed yet
    assertEquals(emptyList<String>(), viewModel.results.value)

    advanceTimeBy(300)

    assertTrue(viewModel.results.value.isNotEmpty())
}
```

### Migration from Old Test API

Old (deprecated):

```kotlin
// Deprecated: runBlockingTest, TestCoroutineDispatcher, TestCoroutineScope
@Test
fun oldTest() = runBlockingTest {
    // Test code
}
```

New API:

```kotlin
@Test
fun newTest() = runTest {
    // Use runTest with TestScope and test dispatchers
}
```

Key changes:
- `runBlockingTest` → `runTest`.
- `TestCoroutineDispatcher` / `TestCoroutineScope` → `StandardTestDispatcher` / `UnconfinedTestDispatcher` with `TestScope`.
- Virtual time is managed by `runTest` and `TestCoroutineScheduler`; you explicitly advance it when needed.

### Best Practices

1. Use `StandardTestDispatcher` as the default in tests.
2. Use `UnconfinedTestDispatcher` only when you intentionally rely on its eager, unconfined behavior.
3. For async work, either:
   - Await jobs (`join`, `await`), or
   - Use `advanceTimeBy` / `advanceUntilIdle` when testing delays and timing.
4. Collect `Flow` / `StateFlow` in `backgroundScope` to avoid blocking the main test body.
5. Prefer virtual time (`runTest`) over real delays (`runBlocking`, `Thread.sleep`).

### Common Mistakes

Mistake 1: Forgetting to cooperate with the scheduler

```kotlin
@Test
fun badTest() = runTest {
    var value = 0
    launch { value = 1 }

    // No join / no advance; may assert too early
    assertEquals(1, value) // Flaky / incorrect
}

@Test
fun goodTest() = runTest {
    var value = 0
    val job = launch { value = 1 }

    job.join() // or advanceUntilIdle()

    assertEquals(1, value)
}
```

Mistake 2: Using `runBlocking` with real time

```kotlin
@Test
fun badTest() = runBlocking {
    delay(1000) // Real 1 second
}

@Test
fun goodTest() = runTest {
    delay(1000) // Virtual
}
```

Mistake 3: Collecting in the main test scope without `backgroundScope`

```kotlin
@Test
fun badTest() = runTest {
    // This collect never completes and blocks the test
    collectFlow().collect { }
}

@Test
fun goodTest() = runTest {
    backgroundScope.launch {
        collectFlow().collect { }
    }

    advanceUntilIdle()
}
```

Mistake 4: Mixing real and virtual time

```kotlin
@Test
fun badTest() = runTest {
    launch {
        Thread.sleep(1000) // Real time: not controlled by scheduler
    }
    advanceTimeBy(1000) // Has no effect on Thread.sleep
}

@Test
fun goodTest() = runTest {
    launch {
        delay(1000) // Virtual
    }
    advanceTimeBy(1000)
}
```

### When to Use Each Dispatcher

Use `StandardTestDispatcher` when:
- You want deterministic, controllable execution.
- Testing delays, debounces, timeouts, and cancellations.
- Writing most coroutine unit tests.

Use `UnconfinedTestDispatcher` when:
- You need immediate execution before the first suspension.
- You explicitly depend on unconfined behavior (e.g., verifying synchronous side effects) and understand its implications.

### Key Takeaways

1. `StandardTestDispatcher` (default in `runTest`) — deterministic, queued execution.
2. `UnconfinedTestDispatcher` — eager until first suspension, then scheduled by the same test scheduler.
3. Neither dispatcher advances time magically; use `advanceTimeBy` / `advanceUntilIdle` and proper awaiting.
4. Prefer `runTest` + virtual time over `runBlocking` / `runBlockingTest`.
5. Use `backgroundScope` for long-running collectors.
6. Pick the dispatcher based on the required semantics: control vs eager pre-suspension execution.

---

## Дополнительные Вопросы (RU)

1. Как тестировать код, использующий несколько диспетчеров (`IO`, `Main`, `Default`)?
2. Как связаны `TestScope` и тестовые диспетчеры (`StandardTestDispatcher` / `UnconfinedTestDispatcher`)?
3. Как тестировать `Flow`, которые постоянно эмитят значения?
4. Как работает виртуальное время внутренне в `kotlinx-coroutines-test`?
5. Как тестировать код, где реальные задержки смешиваются с `delay` корутин?
6. Что произойдет, если не координироваться с планировщиком в тестах?
7. Как тестировать корутины, использующие `withContext` для переключения диспетчеров?

## Follow-ups

1. How do you test code that uses multiple dispatchers (`IO`, `Main`, `Default`)?
2. What's the relationship between `TestScope` and test dispatchers (`StandardTestDispatcher` / `UnconfinedTestDispatcher`)?
3. How do you test `Flow`s that emit values continuously?
4. Can you explain how virtual time works internally in `kotlinx-coroutines-test`?
5. How do you test code with real delays mixed with coroutine `delay`?
6. What happens if you don't coordinate with the scheduler in tests?
7. How do you test coroutines that use `withContext` to switch dispatchers?

## Ссылки (RU)

- https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/
- https://developer.android.com/kotlin/coroutines/test
- https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/kotlinx.coroutines.test/-test-dispatcher.html

## References

- https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/
- https://developer.android.com/kotlin/coroutines/test
- https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/kotlinx.coroutines.test/-test-dispatcher.html

## Связанные Вопросы (RU)

- [[q-debugging-coroutines-techniques--kotlin--medium|Отладка корутин]]
- [[q-common-coroutine-mistakes--kotlin--medium|Типичные ошибки при работе с корутинами]]
- [[q-channelflow-callbackflow-flow--kotlin--medium|Построители `Flow`]]

## Related Questions

- [[q-debugging-coroutines-techniques--kotlin--medium|Debugging coroutines]]
- [[q-common-coroutine-mistakes--kotlin--medium|Common coroutine mistakes]]
- [[q-channelflow-callbackflow-flow--kotlin--medium|`Flow` builders]]
