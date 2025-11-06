---
id: android-066
title: Flow Testing with Turbine / Тестирование Flow с Turbine
aliases:
- Flow Testing with Turbine
- Тестирование Flow с Turbine
topic: android
subtopics:
- coroutines
- flow
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
- q-compose-testing--android--medium
- q-unit-testing-coroutines-flow--android--medium
created: 2025-10-12
updated: 2025-10-28
tags:
- android/coroutines
- android/flow
- android/testing-unit
- difficulty/medium
- turbine
- unit-testing
sources:
- https://github.com/cashapp/turbine

---

# Вопрос (RU)
> Что такое Turbine? Как тестировать Flows с Turbine?

# Question (EN)
> What is Turbine? How do you test Flows with Turbine?

---

## Ответ (RU)

**Что такое Turbine:**
Turbine — библиотека для тестирования Kotlin `Flow` от Cash App, предоставляющая декларативный API для проверки асинхронных эмиссий. Решает проблему недетерминированности `Flow`-тестов и упрощает верификацию последовательности событий.

**Ключевые возможности:**
- Декларативные методы для проверки эмиссий (`awaitItem`, `awaitComplete`, `awaitError`)
- Интеграция с `kotlinx-coroutines-test` для контроля виртуального времени
- Поддержка `StateFlow`, `SharedFlow` и холодных `Flow`
- Автоматическая очистка ресурсов и обработка отмены

**Основной API:**

```kotlin
// ✅ Базовый паттерн тестирования Flow
@Test
fun `test flow emissions`() = runTest {
    val flow = flowOf(1, 2, 3)

    flow.test {
        assertEquals(1, awaitItem())  // ждем первую эмиссию
        assertEquals(2, awaitItem())
        assertEquals(3, awaitItem())
        awaitComplete()               // проверяем завершение
    }
}

// ✅ Тестирование ошибок
@Test
fun `test flow error`() = runTest {
    val flow = flow {
        emit("data")
        throw IOException("Network error")
    }

    flow.test {
        assertEquals("data", awaitItem())
        val error = awaitError()
        assertTrue(error is IOException)
    }
}

// ✅ Проверка отсутствия событий
@Test
fun `test delayed emission`() = runTest {
    val flow = flow {
        delay(100)
        emit(42)
    }

    flow.test {
        expectNoEvents()           // нет эмиссий до истечения delay
        advanceTimeBy(100)
        assertEquals(42, awaitItem())
    }
}
```

**Тестирование `StateFlow` в `ViewModel`:**

```kotlin
class CounterViewModel : ViewModel() {
    private val _count = MutableStateFlow(0)
    val count = _count.asStateFlow()

    fun increment() { _count.value++ }
}

@Test
fun `increment updates state correctly`() = runTest {
    Dispatchers.setMain(StandardTestDispatcher())
    val viewModel = CounterViewModel()

    viewModel.count.test {
        assertEquals(0, awaitItem())  // ✅ StateFlow всегда имеет начальное значение

        viewModel.increment()
        assertEquals(1, awaitItem())

        cancelAndIgnoreRemainingEvents()  // ✅ завершаем тест без ожидания
    }

    Dispatchers.resetMain()
}
```

**Тестирование UI State паттерна:**

```kotlin
sealed interface UiState {
    data object Loading : UiState
    data class Success(val data: String) : UiState
    data class Error(val msg: String) : UiState
}

class DataViewModel(private val repo: Repository) : ViewModel() {
    private val _state = MutableStateFlow<UiState>(UiState.Loading)
    val state = _state.asStateFlow()

    fun load() {
        viewModelScope.launch {
            repo.getData()
                .onStart { _state.value = UiState.Loading }
                .catch { _state.value = UiState.Error(it.message ?: "Unknown") }
                .collect { _state.value = UiState.Success(it) }
        }
    }
}

@Test
fun `load transitions through states correctly`() = runTest {
    val mockRepo = mockk<Repository>()
    coEvery { mockRepo.getData() } returns flowOf("result")

    val viewModel = DataViewModel(mockRepo)

    viewModel.state.test {
        assertTrue(awaitItem() is UiState.Loading)  // начальное

        viewModel.load()
        advanceUntilIdle()  // ✅ пропускаем виртуальное время до завершения корутин

        // ❌ НЕ используйте skipItems() без понимания, сколько эмиссий пропустить
        val final = awaitItem()
        assertTrue(final is UiState.Success)
        assertEquals("result", (final as UiState.Success).data)

        cancelAndIgnoreRemainingEvents()
    }
}
```

**Частые ошибки:**

```kotlin
// ❌ Забыли awaitComplete/cancelAndIgnoreRemainingEvents
flow.test {
    assertEquals(1, awaitItem())
    // тест зависнет, ожидая завершения Flow
}

// ✅ Всегда явно завершайте
flow.test {
    assertEquals(1, awaitItem())
    awaitComplete()  // или cancelAndIgnoreRemainingEvents()
}

// ❌ Не учли начальное значение StateFlow
stateFlow.test {
    viewModel.update()
    assertEquals(newValue, awaitItem())  // пропустили начальное!
}

// ✅ Обрабатываем начальную эмиссию
stateFlow.test {
    awaitItem()  // пропускаем начальное
    viewModel.update()
    assertEquals(newValue, awaitItem())
}
```

## Answer (EN)

**What is Turbine:**
Turbine is a `Flow` testing library by Cash App that provides a declarative API for verifying asynchronous emissions. It solves the non-determinism problem in `Flow` tests and simplifies event sequence verification.

**Key capabilities:**
- Declarative methods for emission verification (`awaitItem`, `awaitComplete`, `awaitError`)
- Integration with `kotlinx-coroutines-test` for virtual time control
- Support for `StateFlow`, `SharedFlow`, and cold Flows
- Automatic resource cleanup and cancellation handling

**Core API:**

```kotlin
// ✅ Basic Flow testing pattern
@Test
fun `test flow emissions`() = runTest {
    val flow = flowOf(1, 2, 3)

    flow.test {
        assertEquals(1, awaitItem())  // wait for first emission
        assertEquals(2, awaitItem())
        assertEquals(3, awaitItem())
        awaitComplete()               // verify completion
    }
}

// ✅ Testing errors
@Test
fun `test flow error`() = runTest {
    val flow = flow {
        emit("data")
        throw IOException("Network error")
    }

    flow.test {
        assertEquals("data", awaitItem())
        val error = awaitError()
        assertTrue(error is IOException)
    }
}

// ✅ Verifying no events
@Test
fun `test delayed emission`() = runTest {
    val flow = flow {
        delay(100)
        emit(42)
    }

    flow.test {
        expectNoEvents()           // no emissions before delay expires
        advanceTimeBy(100)
        assertEquals(42, awaitItem())
    }
}
```

**Testing `StateFlow` in `ViewModel`:**

```kotlin
class CounterViewModel : ViewModel() {
    private val _count = MutableStateFlow(0)
    val count = _count.asStateFlow()

    fun increment() { _count.value++ }
}

@Test
fun `increment updates state correctly`() = runTest {
    Dispatchers.setMain(StandardTestDispatcher())
    val viewModel = CounterViewModel()

    viewModel.count.test {
        assertEquals(0, awaitItem())  // ✅ StateFlow always has initial value

        viewModel.increment()
        assertEquals(1, awaitItem())

        cancelAndIgnoreRemainingEvents()  // ✅ finish test without waiting
    }

    Dispatchers.resetMain()
}
```

**Testing UI State pattern:**

```kotlin
sealed interface UiState {
    data object Loading : UiState
    data class Success(val data: String) : UiState
    data class Error(val msg: String) : UiState
}

class DataViewModel(private val repo: Repository) : ViewModel() {
    private val _state = MutableStateFlow<UiState>(UiState.Loading)
    val state = _state.asStateFlow()

    fun load() {
        viewModelScope.launch {
            repo.getData()
                .onStart { _state.value = UiState.Loading }
                .catch { _state.value = UiState.Error(it.message ?: "Unknown") }
                .collect { _state.value = UiState.Success(it) }
        }
    }
}

@Test
fun `load transitions through states correctly`() = runTest {
    val mockRepo = mockk<Repository>()
    coEvery { mockRepo.getData() } returns flowOf("result")

    val viewModel = DataViewModel(mockRepo)

    viewModel.state.test {
        assertTrue(awaitItem() is UiState.Loading)  // initial state

        viewModel.load()
        advanceUntilIdle()  // ✅ skip virtual time until coroutines complete

        // ❌ DON'T use skipItems() without knowing how many emissions to skip
        val final = awaitItem()
        assertTrue(final is UiState.Success)
        assertEquals("result", (final as UiState.Success).data)

        cancelAndIgnoreRemainingEvents()
    }
}
```

**Common mistakes:**

```kotlin
// ❌ Forgot awaitComplete/cancelAndIgnoreRemainingEvents
flow.test {
    assertEquals(1, awaitItem())
    // test will hang waiting for Flow completion
}

// ✅ Always explicitly finish
flow.test {
    assertEquals(1, awaitItem())
    awaitComplete()  // or cancelAndIgnoreRemainingEvents()
}

// ❌ Didn't account for StateFlow initial value
stateFlow.test {
    viewModel.update()
    assertEquals(newValue, awaitItem())  // missed initial!
}

// ✅ Handle initial emission
stateFlow.test {
    awaitItem()  // skip initial
    viewModel.update()
    assertEquals(newValue, awaitItem())
}
```

---

## Follow-ups

- How does Turbine handle backpressure when testing high-frequency emissions?
- What's the difference between `test()` and `testIn()` methods, and when to use each?
- How to test cold vs hot Flows with Turbine?
- When should you use `expectNoEvents()` vs `expectMostRecentItem()`?
- How to test Flows with multiple collectors using Turbine?
- How does Turbine integrate with TestScope's virtual time control?

## References

- Official Turbine documentation: https://github.com/cashapp/turbine
- kotlinx-coroutines-test guide: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/

## Related Questions

### Prerequisites / Concepts

- 


### Related
- [[q-unit-testing-coroutines-flow--android--medium]] - Testing coroutines and Flows
- [[q-compose-testing--android--medium]] - Testing ViewModels with Flows
- [[q-compose-testing--android--medium]] - Testing Compose UI with state Flows

### Advanced
- Testing `SharedFlow` vs `StateFlow` differences and best practices
- Advanced `Flow` operators testing (debounce, combine, flatMapLatest)
- Testing `Flow` with custom CoroutineContext and dispatchers
