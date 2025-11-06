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
updated: 2025-10-28
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

**1. TestDispatchers**
- `StandardTestDispatcher` — требует явного `advanceTimeBy()`/`runCurrent()`
- `UnconfinedTestDispatcher` — выполняет корутины немедленно
- `runTest { }` — корутинный scope с виртуальным временем

**2. Turbine**
- Удобный API для тестирования `Flow`
- `awaitItem()`, `awaitComplete()`, `awaitError()`
- Автоматическая отмена коллекции

**3. MockK**
- `coEvery { }` для suspend функций
- `coVerify { }` для проверки вызовов

### Основные Паттерны

**Тестирование suspend функций**

```kotlin
// ViewModel
class UserViewModel(private val repo: UserRepository) : ViewModel() {
 private val _user = MutableStateFlow<User?>(null)
 val user: StateFlow<User?> = _user.asStateFlow()

 suspend fun loadUser(id: String) {
 _user.value = repo.getUser(id) // ✅ Simple state update
 }
}

// Test
@get:Rule
val mainDispatcherRule = MainDispatcherRule()

@Test
fun `loadUser updates state`() = runTest {
 coEvery { repo.getUser("1") } returns User("1", "John")

 viewModel.loadUser("1")

 assertEquals(User("1", "John"), viewModel.user.value) // ✅ Direct assertion
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
 assertEquals(articles1, awaitItem()) // ✅ First emission

 testScheduler.advanceTimeBy(5000)
 assertEquals(articles2, awaitItem()) // ✅ After delay

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
 .filter { it.length >= 2 } // ✅ Skip short queries
 .flatMapLatest { repo.search(it) }
 .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

 fun onQueryChanged(q: String) { _query.value = q }
}

// Test
@Test
fun `debounce prevents excessive calls`() = runTest {
 coEvery { repo.search(any()) } returns flowOf(emptyList())

 viewModel.onQueryChanged("t") // ❌ Too short
 testScheduler.advanceTimeBy(100)

 viewModel.onQueryChanged("test") // ✅ Valid
 testScheduler.advanceTimeBy(400) // ✅ Past debounce

 coVerify(exactly = 1) { repo.search("test") } // ✅ Only final query
 coVerify(exactly = 0) { repo.search("t") } // ✅ Filtered out
}
```

### MainDispatcherRule

```kotlin
// Test rule для замены Dispatchers.Main
class MainDispatcherRule(
 private val dispatcher: TestDispatcher = UnconfinedTestDispatcher()
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
- Используйте `runTest { }` вместо `runBlocking`
- Инжектируйте `CoroutineDispatcher` для тестируемости
- Управляйте виртуальным временем через `testScheduler`
- Используйте Turbine для `Flow` тестов
- Проверяйте error cases и cancellation

**❌ Избегайте:**
- `Thread.sleep()` — ломает виртуальное время
- Забывать `advanceTimeBy()` для delay
- Не закрывать infinite `Flow` (используйте `take()` или Turbine)
- Не тестировать cancellation
- Использовать реальные Dispatchers

### Распространённые Ошибки

```kotlin
// ❌ WRONG: Реальный Main dispatcher
@Test
fun test() = runBlocking { ... }

// ✅ CORRECT: TestDispatcher
@Test
fun test() = runTest { ... }

// ❌ WRONG: Тест завершается до выполнения корутины
@Test
fun test() = runTest {
 launch { delay(1000); doWork() }
 verify { doWork() } // ❌ Ещё не выполнилось
}

// ✅ CORRECT: Продвигаем время
@Test
fun test() = runTest {
 launch { delay(1000); doWork() }
 testScheduler.advanceUntilIdle() // ✅ Выполняем все задачи
 verify { doWork() }
}

// ❌ WRONG: Infinite Flow висит
@Test
fun test() = runTest {
 flow.collect { ... } // ❌ Никогда не завершится
}

// ✅ CORRECT: Ограничиваем коллекцию
@Test
fun test() = runTest {
 flow.take(3).test { ... } // ✅ Завершится после 3 элементов
}
```

---

## Answer (EN)

Testing coroutines and `Flow` requires specialized tools: test dispatchers, virtual time control, and proper async handling.

### Key Tools

**1. TestDispatchers**
- `StandardTestDispatcher` — requires explicit `advanceTimeBy()`/`runCurrent()`
- `UnconfinedTestDispatcher` — executes coroutines immediately
- `runTest { }` — coroutine scope with virtual time

**2. Turbine**
- Convenient API for `Flow` testing
- `awaitItem()`, `awaitComplete()`, `awaitError()`
- Automatic collection cancellation

**3. MockK**
- `coEvery { }` for suspend functions
- `coVerify { }` for call verification

### Core Patterns

**Testing suspend functions**

```kotlin
// ViewModel
class UserViewModel(private val repo: UserRepository) : ViewModel() {
 private val _user = MutableStateFlow<User?>(null)
 val user: StateFlow<User?> = _user.asStateFlow()

 suspend fun loadUser(id: String) {
 _user.value = repo.getUser(id) // ✅ Simple state update
 }
}

// Test
@get:Rule
val mainDispatcherRule = MainDispatcherRule()

@Test
fun `loadUser updates state`() = runTest {
 coEvery { repo.getUser("1") } returns User("1", "John")

 viewModel.loadUser("1")

 assertEquals(User("1", "John"), viewModel.user.value) // ✅ Direct assertion
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
 assertEquals(articles1, awaitItem()) // ✅ First emission

 testScheduler.advanceTimeBy(5000)
 assertEquals(articles2, awaitItem()) // ✅ After delay

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
 .filter { it.length >= 2 } // ✅ Skip short queries
 .flatMapLatest { repo.search(it) }
 .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

 fun onQueryChanged(q: String) { _query.value = q }
}

// Test
@Test
fun `debounce prevents excessive calls`() = runTest {
 coEvery { repo.search(any()) } returns flowOf(emptyList())

 viewModel.onQueryChanged("t") // ❌ Too short
 testScheduler.advanceTimeBy(100)

 viewModel.onQueryChanged("test") // ✅ Valid
 testScheduler.advanceTimeBy(400) // ✅ Past debounce

 coVerify(exactly = 1) { repo.search("test") } // ✅ Only final query
 coVerify(exactly = 0) { repo.search("t") } // ✅ Filtered out
}
```

### MainDispatcherRule

```kotlin
// Test rule to replace Dispatchers.Main
class MainDispatcherRule(
 private val dispatcher: TestDispatcher = UnconfinedTestDispatcher()
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
- Use `runTest { }` instead of `runBlocking`
- Inject `CoroutineDispatcher` for testability
- Control virtual time via `testScheduler`
- Use Turbine for `Flow` tests
- Test error cases and cancellation

**❌ Avoid:**
- `Thread.sleep()` — breaks virtual time
- Forgetting `advanceTimeBy()` for delays
- Not closing infinite Flows (use `take()` or Turbine)
- Not testing cancellation
- Using real Dispatchers

### Common Pitfalls

```kotlin
// ❌ WRONG: Real Main dispatcher
@Test
fun test() = runBlocking { ... }

// ✅ CORRECT: TestDispatcher
@Test
fun test() = runTest { ... }

// ❌ WRONG: Test finishes before coroutine executes
@Test
fun test() = runTest {
 launch { delay(1000); doWork() }
 verify { doWork() } // ❌ Not executed yet
}

// ✅ CORRECT: Advance time
@Test
fun test() = runTest {
 launch { delay(1000); doWork() }
 testScheduler.advanceUntilIdle() // ✅ Execute all tasks
 verify { doWork() }
}

// ❌ WRONG: Infinite Flow hangs
@Test
fun test() = runTest {
 flow.collect { ... } // ❌ Never completes
}

// ✅ CORRECT: Limit collection
@Test
fun test() = runTest {
 flow.take(3).test { ... } // ✅ Completes after 3 items
}
```

---

## Follow-ups

1. How do you test `SharedFlow` with replay buffer behavior?
2. What's the difference between `StandardTestDispatcher` and `UnconfinedTestDispatcher` in practice?
3. How to test coroutine cancellation and `ensureActive()` calls?
4. How do you test `Flow` operators like `combine()`, `zip()`, and `merge()`?
5. How to test timeout behavior with `withTimeout()`?

---

## References

- [[c-coroutines]] — Kotlin coroutines fundamentals
- [[c-flow]] — `Flow` basics and operators
- — General testing approaches
- [Kotlin Coroutines Test Guide](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
- [Turbine Documentation](https://github.com/cashapp/turbine)
- [Testing Coroutines on Android](https://developer.android.com/kotlin/coroutines/test)

---

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-coroutine--kotlin--easy]] — `Coroutine` basics
- — `Flow` fundamentals
- — Unit testing intro

### Related (Same Level)
- [[q-testing-viewmodels-turbine--android--medium]] — `ViewModel` testing patterns
- [[q-testing-compose-ui--android--medium]] — Compose UI testing
- [[q-coroutine-dispatchers--kotlin--medium]] — Dispatcher types and usage

### Advanced (Harder)
- — Concurrency edge cases
- [[q-structured-concurrency--kotlin--hard]] — Complex coroutine hierarchies
