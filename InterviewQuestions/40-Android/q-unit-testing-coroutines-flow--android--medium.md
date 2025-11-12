---
id: android-425
title: "Unit Testing Coroutines and Flow / Юнит-тестирование корутин и Flow"
aliases: ["Unit Testing Coroutines Flow", "Юнит-тестирование корутин и Flow"]
topic: android
subtopics: [coroutines, flow, testing-unit]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-coroutines, c-flow, c-testing]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/coroutines, android/flow, android/testing-unit, difficulty/medium, mockk, testing, turbine, unit-testing]

---

# Вопрос (RU)

> Как писать юнит-тесты для Kotlin Coroutines и `Flow`? Какие есть best practices и распространённые ошибки?

# Question (EN)

> How do you write unit tests for Kotlin Coroutines and `Flow`? What are the best practices and common pitfalls?

---

## Ответ (RU)

Тестирование корутин и `Flow` требует специального подхода: тестовые диспетчеры, управление виртуальным временем, правильная обработка асинхронности.

### Ключевые Инструменты

**1. TestDispatchers и runTest**
- `runTest { }` — корутинный scope с виртуальным временем и встроенным `TestCoroutineScheduler`. Используйте его как основной entrypoint для тестов корутин.
- `StandardTestDispatcher` — планирует выполнение задач; требует явного `advanceTimeBy()`/`runCurrent()`/`advanceUntilIdle()` через `testScheduler`.
- `UnconfinedTestDispatcher` — выполняет корутины немедленно в текущем потоке; менее детерминирован, обычно не используется как дефолтный для сложных тестов.

**2. Turbine**
- Удобный API для тестирования `Flow`.
- `awaitItem()`, `awaitComplete()`, `awaitError()`.
- Автоматическая отмена коллекции в конце блока `test { ... }`.

**3. MockK**
- `coEvery { }` для suspend-функций.
- `coVerify { }` для проверки вызовов.

### Основные Паттерны

**Тестирование suspend-функций**

```kotlin
// ViewModel
class UserViewModel(private val repo: UserRepository) : ViewModel() {
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    suspend fun loadUser(id: String) {
        _user.value = repo.getUser(id)  // ✅ Simple state update
    }
}

// Test
@get:Rule
val mainDispatcherRule = MainDispatcherRule()

@Test
fun `loadUser updates state`() = runTest {
    coEvery { repo.getUser("1") } returns User("1", "John")

    viewModel.loadUser("1")

    assertEquals(User("1", "John"), viewModel.user.value)  // ✅ Direct assertion
}
```

**Тестирование `Flow` с Turbine**

```kotlin
// Repository
fun observeArticles(): Flow<List<Article>> = flow {
    while (currentCoroutineContext().isActive) {
        emit(api.getArticles())
        delay(5000)
    }
}

// Test
@Test
fun `observeArticles emits periodically`() = runTest {
    val articles1 = listOf(Article("1", "First"))
    val articles2 = listOf(Article("2", "Second"))

    coEvery { api.getArticles() } returnsMany listOf(articles1, articles2)

    repo.observeArticles().test {
        assertEquals(articles1, awaitItem())  // ✅ First emission

        testScheduler.advanceTimeBy(5000)     // ✅ Используем scheduler из runTest
        assertEquals(articles2, awaitItem())  // ✅ After delay

        cancelAndIgnoreRemainingEvents()
    }
}
```

**Тестирование `StateFlow` с debounce**

```kotlin
// ViewModel
class SearchViewModel(private val repo: SearchRepository) : ViewModel() {
    private val _query = MutableStateFlow("")
    val results = _query
        .debounce(300)
        .filter { it.length >= 2 }  // ✅ Skip short queries before вызова search
        .flatMapLatest { query -> repo.search(query) }
        .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

    fun onQueryChanged(q: String) { _query.value = q }
}

// Test
@Test
fun `debounce prevents excessive calls`() = runTest {
    coEvery { repo.search(any()) } returns flowOf(emptyList())

    viewModel.onQueryChanged("t")   // ❌ Too short
    testScheduler.advanceTimeBy(100)

    viewModel.onQueryChanged("test")  // ✅ Valid
    testScheduler.advanceTimeBy(400)   // ✅ Past debounce

    coVerify(exactly = 1) { repo.search("test") }  // ✅ Only final query
    coVerify(exactly = 0) { repo.search("t") }     // ✅ Filtered out by length
}
```

### MainDispatcherRule

```kotlin
// Test rule для замены Dispatchers.Main под тестовым диспетчером
class MainDispatcherRule(
    private val dispatcher: TestDispatcher = StandardTestDispatcher()
) : TestWatcher() {
    override fun starting(description: Description) {
        Dispatchers.setMain(dispatcher)
    }
    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

### Best Practices

**✅ Правильно:**
- Используйте `runTest { }` вместо `runBlocking` для тестов корутин.
- Инжектируйте `CoroutineDispatcher` для тестируемости (`Dispatchers.Main`, IO и т.п.).
- Управляйте виртуальным временем через `testScheduler` из `runTest` или связанного `TestDispatcher`.
- Используйте Turbine для тестирования `Flow`.
- Тестируйте error cases и cancellation.

**❌ Избегайте:**
- `Thread.sleep()` — ломает виртуальное время.
- Забывать `advanceTimeBy()`/`advanceUntilIdle()` для `delay` и отложенных задач.
- Не ограничивать infinite `Flow` (используйте `take()` или правильную отмену/Turbine).
- Не тестировать cancellation.
- Использовать реальные `Dispatchers` (`Dispatchers.Main`, `Dispatchers.IO`) в unit-тестах.

### Распространённые Ошибки

```kotlin
// ❌ WRONG: Реальный Main dispatcher и блокирующий runBlocking
@Test
fun test() = runBlocking { /* ... */ }

// ✅ CORRECT: Используем runTest с тестовым диспетчером
@Test
fun test() = runTest { /* ... */ }

// ❌ WRONG: Тест завершается до выполнения корутины
@Test
fun test() = runTest {
    launch { delay(1000); doWork() }
    verify { doWork() }  // ❌ Ещё не выполнилось
}

// ✅ CORRECT: Продвигаем виртуальное время
@Test
fun test() = runTest {
    launch { delay(1000); doWork() }
    testScheduler.advanceUntilIdle()  // ✅ Выполняем все отложенные задачи
    verify { doWork() }
}

// ❌ WRONG: Infinite Flow висит
@Test
fun test() = runTest {
    flow.collect { /* ... */ }  // ❌ Никогда не завершится
}

// ✅ CORRECT: Ограничиваем коллекцию или явно отменяем
@Test
fun test() = runTest {
    flow.take(3).test { /* ... */ }  // ✅ Завершится после 3 элементов
}
```

---

## Answer (EN)

Testing coroutines and `Flow` requires specialized tools: test dispatchers, virtual time control, and proper async handling.

### Key Tools

**1. TestDispatchers and runTest**
- `runTest { }` — coroutine scope with virtual time and an internal `TestCoroutineScheduler`. Use it as the primary entrypoint for coroutine unit tests.
- `StandardTestDispatcher` — schedules execution; requires explicit `advanceTimeBy()`/`runCurrent()`/`advanceUntilIdle()` via `testScheduler`.
- `UnconfinedTestDispatcher` — executes coroutines immediately in the current call stack; less deterministic, usually not the default choice for complex tests.

**2. Turbine**
- Convenient API for `Flow` testing.
- `awaitItem()`, `awaitComplete()`, `awaitError()`.
- Automatically cancels collection when leaving the `test { ... }` block.

**3. MockK**
- `coEvery { }` for suspend functions.
- `coVerify { }` for call verification.

### Core Patterns

**Testing suspend functions**

```kotlin
// ViewModel
class UserViewModel(private val repo: UserRepository) : ViewModel() {
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    suspend fun loadUser(id: String) {
        _user.value = repo.getUser(id)  // ✅ Simple state update
    }
}

// Test
@get:Rule
val mainDispatcherRule = MainDispatcherRule()

@Test
fun `loadUser updates state`() = runTest {
    coEvery { repo.getUser("1") } returns User("1", "John")

    viewModel.loadUser("1")

    assertEquals(User("1", "John"), viewModel.user.value)  // ✅ Direct assertion
}
```

**Testing `Flow` with Turbine**

```kotlin
// Repository
fun observeArticles(): Flow<List<Article>> = flow {
    while (currentCoroutineContext().isActive) {
        emit(api.getArticles())
        delay(5000)
    }
}

// Test
@Test
fun `observeArticles emits periodically`() = runTest {
    val articles1 = listOf(Article("1", "First"))
    val articles2 = listOf(Article("2", "Second"))

    coEvery { api.getArticles() } returnsMany listOf(articles1, articles2)

    repo.observeArticles().test {
        assertEquals(articles1, awaitItem())  // ✅ First emission

        testScheduler.advanceTimeBy(5000)     // ✅ Use scheduler from runTest
        assertEquals(articles2, awaitItem())  // ✅ After delay

        cancelAndIgnoreRemainingEvents()
    }
}
```

**Testing `StateFlow` with debounce**

```kotlin
// ViewModel
class SearchViewModel(private val repo: SearchRepository) : ViewModel() {
    private val _query = MutableStateFlow("")
    val results = _query
        .debounce(300)
        .filter { it.length >= 2 }  // ✅ Skip short queries before calling search
        .flatMapLatest { query -> repo.search(query) }
        .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

    fun onQueryChanged(q: String) { _query.value = q }
}

// Test
@Test
fun `debounce prevents excessive calls`() = runTest {
    coEvery { repo.search(any()) } returns flowOf(emptyList())

    viewModel.onQueryChanged("t")   // ❌ Too short
    testScheduler.advanceTimeBy(100)

    viewModel.onQueryChanged("test")  // ✅ Valid
    testScheduler.advanceTimeBy(400)   // ✅ Past debounce

    coVerify(exactly = 1) { repo.search("test") }  // ✅ Only final query
    coVerify(exactly = 0) { repo.search("t") }     // ✅ Filtered out by length
}
```

### MainDispatcherRule

```kotlin
// Test rule to replace Dispatchers.Main with a TestDispatcher
class MainDispatcherRule(
    private val dispatcher: TestDispatcher = StandardTestDispatcher()
) : TestWatcher() {
    override fun starting(description: Description) {
        Dispatchers.setMain(dispatcher)
    }
    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

### Best Practices

**✅ Do:**
- Use `runTest { }` instead of `runBlocking` for coroutine tests.
- Inject `CoroutineDispatcher` for testability (`Dispatchers.Main`, IO, etc.).
- Control virtual time via the `testScheduler` from `runTest` or the associated `TestDispatcher`.
- Use Turbine for `Flow` tests.
- Cover error paths and cancellation behavior.

**❌ Avoid:**
- `Thread.sleep()` — breaks virtual time.
- Forgetting `advanceTimeBy()`/`advanceUntilIdle()` for `delay` and scheduled work.
- Leaving infinite Flows unbounded (use `take()` or proper cancellation/Turbine helpers).
- Skipping cancellation tests.
- Using real `Dispatchers` (`Dispatchers.Main`, `Dispatchers.IO`) in unit tests.

### Common Pitfalls

```kotlin
// ❌ WRONG: Real Main dispatcher and blocking runBlocking
@Test
fun test() = runBlocking { /* ... */ }

// ✅ CORRECT: Use runTest with a TestDispatcher
@Test
fun test() = runTest { /* ... */ }

// ❌ WRONG: Test finishes before coroutine executes
@Test
fun test() = runTest {
    launch { delay(1000); doWork() }
    verify { doWork() }  // ❌ Not executed yet
}

// ✅ CORRECT: Advance virtual time
@Test
fun test() = runTest {
    launch { delay(1000); doWork() }
    testScheduler.advanceUntilIdle()  // ✅ Execute all scheduled tasks
    verify { doWork() }
}

// ❌ WRONG: Infinite Flow hangs
@Test
fun test() = runTest {
    flow.collect { /* ... */ }  // ❌ Never completes
}

// ✅ CORRECT: Limit collection or cancel explicitly
@Test
fun test() = runTest {
    flow.take(3).test { /* ... */ }  // ✅ Completes after 3 items
}
```

---

## Дополнительные вопросы (RU)

1. Как протестировать поведение `SharedFlow` с `replay` буфером и различными подписчиками?
2. В чём практическая разница между `StandardTestDispatcher` и `UnconfinedTestDispatcher` при написании тестов?
3. Как корректно тестировать отмену корутин и использование `ensureActive()`?
4. Как тестировать сложные `Flow`-цепочки с операторами `combine()`, `zip()` и `merge()`?
5. Как протестировать поведение с таймаутами при использовании `withTimeout()` и `withTimeoutOrNull()`?

## Follow-ups

1. How do you test `SharedFlow` with replay buffer behavior and multiple subscribers?
2. What are the practical differences between `StandardTestDispatcher` and `UnconfinedTestDispatcher` in coroutine tests?
3. How do you properly test coroutine cancellation and `ensureActive()` checks?
4. How do you test complex `Flow` chains using operators like `combine()`, `zip()`, and `merge()`?
5. How do you test timeout behavior when using `withTimeout()` or `withTimeoutOrNull()`?

---

## Ссылки (RU)

- [[c-coroutines]] — основы корутин в Kotlin
- [[c-flow]] — основы и операторы `Flow`
- [[c-testing]] — общие подходы к тестированию
- [Kotlin Coroutines Test Guide](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
- [Turbine Documentation](https://github.com/cashapp/turbine)
- [Testing Coroutines on Android](https://developer.android.com/kotlin/coroutines/test)

## References

- [[c-coroutines]] — Kotlin coroutines fundamentals
- [[c-flow]] — `Flow` basics and operators
- [[c-testing]] — General testing approaches
- [Kotlin Coroutines Test Guide](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
- [Turbine Documentation](https://github.com/cashapp/turbine)
- [Testing Coroutines on Android](https://developer.android.com/kotlin/coroutines/test)

---

## Связанные вопросы (RU)

### Базовые (проще)
- [[q-what-is-coroutine--kotlin--easy]] — основы `Coroutine`

### Связанные (средний уровень)
- [[q-testing-compose-ui--android--medium]] — тестирование Compose UI
- [[q-coroutine-dispatchers--kotlin--medium]] — типы диспетчеров и их использование

### Продвинутые (сложнее)
- [[q-structured-concurrency--kotlin--hard]] — сложные иерархии корутин

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-coroutine--kotlin--easy]] — `Coroutine` basics

### Related (Same Level)
- [[q-testing-compose-ui--android--medium]] — Compose UI testing
- [[q-coroutine-dispatchers--kotlin--medium]] — Dispatcher types and usage

### Advanced (Harder)
- [[q-structured-concurrency--kotlin--hard]] — Complex coroutine hierarchies
``