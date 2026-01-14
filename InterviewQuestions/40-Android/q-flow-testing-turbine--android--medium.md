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
status: draft
moc: moc-android
related:
- c-flow
- q-compose-testing--android--medium
- q-testing-coroutines-flow--android--hard
- q-testing-viewmodels-turbine--android--medium
- q-unit-testing-coroutines-flow--android--medium
created: 2025-10-12
updated: 2025-11-10
tags:
- android/coroutines
- android/flow
- android/testing-unit
- difficulty/medium
- turbine
- testing-unit
anki_cards:
- slug: android-066-0-en
  language: en
  anki_id: 1768367161107
  synced_at: '2026-01-14T09:17:53.521987'
- slug: android-066-0-ru
  language: ru
  anki_id: 1768367161130
  synced_at: '2026-01-14T09:17:53.525708'
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
Turbine — библиотека для тестирования Kotlin `Flow` от Cash App, предоставляющая декларативный API для проверки асинхронных эмиссий. Упрощает верификацию последовательности событий и уменьшает недетерминизм `Flow`-тестов за счет явного ожидания элементов, завершения и ошибок.

**Ключевые возможности:**
- Декларативные методы для проверки эмиссий (`awaitItem`, `awaitComplete`, `awaitError`)
- Интеграция с `kotlinx-coroutines-test` для контроля виртуального времени
- Поддержка `StateFlow`, `SharedFlow` и холодных `Flow`
- Автоматическая очистка ресурсов и корректная обработка отмены внутри `test {}` / `testIn()`

**Основной API:**

```kotlin
// ✅ Базовый паттерн тестирования Flow
@Test
fun `test flow emissions`() = runTest {
    val flow = flowOf(1, 2, 3)

    flow.test {
        assertEquals(1, awaitItem())  // ждём первую эмиссию
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

// ✅ Проверка отложенной эмиссии с виртуальным временем (всё в одном тест-блоке)
@Test
fun `test delayed emission`() = runTest {
    val flow = flow {
        delay(100)
        emit(42)
        emit(43)
    }

    flow.test {
        expectNoEvents()              // на старте нет эмиссий

        advanceTimeBy(100)            // управление виртуальным временем в runTest

        assertEquals(42, awaitItem())
        assertEquals(43, awaitItem())
        awaitComplete()
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
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)
    try {
        val viewModel = CounterViewModel()

        viewModel.count.test {
            assertEquals(0, awaitItem())  // ✅ StateFlow всегда имеет начальное значение

            viewModel.increment()
            // при необходимости продвигаем виртуальное время:
            advanceUntilIdle()

            assertEquals(1, awaitItem())

            cancelAndIgnoreRemainingEvents()  // ✅ завершаем тест без ожидания
        }
    } finally {
        Dispatchers.resetMain()
    }
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
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)
    try {
        val mockRepo = mockk<Repository>()
        coEvery { mockRepo.getData() } returns flowOf("result")

        val viewModel = DataViewModel(mockRepo)

        viewModel.state.test {
            // начальное состояние
            assertTrue(awaitItem() is UiState.Loading)

            viewModel.load()
            advanceUntilIdle()  // ✅ пропускаем виртуальное время до завершения корутин

            val final = awaitItem()
            assertTrue(final is UiState.Success)
            assertEquals("result", (final as UiState.Success).data)

            cancelAndIgnoreRemainingEvents()
        }
    } finally {
        Dispatchers.resetMain()
    }
}
```

**Частые ошибки:**

```kotlin
// ❌ Забыли awaitComplete/cancelAndIgnoreRemainingEvents
flow.test {
    assertEquals(1, awaitItem())
    // тест зависнет, ожидая завершения Flow или дополнительных элементов
}

// ✅ Всегда явно завершайте ожидание
flow.test {
    assertEquals(1, awaitItem())
    awaitComplete()  // или cancelAndIgnoreRemainingEvents()
}

// ❌ Не учли начальное значение StateFlow
stateFlow.test {
    viewModel.update()
    assertEquals(newValue, awaitItem())  // пропустили начальное!
}

// ✅ Обрабатывайте начальную эмиссию
stateFlow.test {
    awaitItem()  // пропускаем начальное
    viewModel.update()
    assertEquals(newValue, awaitItem())
}
```

## Answer (EN)

**What is Turbine:**
Turbine is a Kotlin `Flow` testing library by Cash App that provides a declarative API for verifying asynchronous emissions. It simplifies event sequence verification and reduces test non-determinism through explicit waiting for items, completion, and errors.

**Key capabilities:**
- Declarative methods for emission verification (`awaitItem`, `awaitComplete`, `awaitError`)
- Integration with `kotlinx-coroutines-test` for virtual time control
- Support for `StateFlow`, `SharedFlow`, and cold Flows
- Automatic resource cleanup and proper cancellation handling inside `test {}` / `testIn()`

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

// ✅ Verifying delayed emission with virtual time (single test block)
@Test
fun `test delayed emission`() = runTest {
    val flow = flow {
        delay(100)
        emit(42)
        emit(43)
    }

    flow.test {
        expectNoEvents()              // no emissions at the beginning

        advanceTimeBy(100)            // virtual time control in runTest

        assertEquals(42, awaitItem())
        assertEquals(43, awaitItem())
        awaitComplete()
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
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)
    try {
        val viewModel = CounterViewModel()

        viewModel.count.test {
            assertEquals(0, awaitItem())  // ✅ StateFlow always has initial value

            viewModel.increment()
            // advance virtual time if needed
            advanceUntilIdle()

            assertEquals(1, awaitItem())

            cancelAndIgnoreRemainingEvents()  // ✅ finish test without waiting
        }
    } finally {
        Dispatchers.resetMain()
    }
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
    val dispatcher = StandardTestDispatcher(testScheduler)
    Dispatchers.setMain(dispatcher)
    try {
        val mockRepo = mockk<Repository>()
        coEvery { mockRepo.getData() } returns flowOf("result")

        val viewModel = DataViewModel(mockRepo)

        viewModel.state.test {
            // initial state
            assertTrue(awaitItem() is UiState.Loading)

            viewModel.load()
            advanceUntilIdle()  // ✅ advance virtual time until coroutines complete

            val final = awaitItem()
            assertTrue(final is UiState.Success)
            assertEquals("result", (final as UiState.Success).data)

            cancelAndIgnoreRemainingEvents()
        }
    } finally {
        Dispatchers.resetMain()
    }
}
```

**Common mistakes:**

```kotlin
// ❌ Forgot awaitComplete/cancelAndIgnoreRemainingEvents
flow.test {
    assertEquals(1, awaitItem())
    // test will hang waiting for Flow completion or further items
}

// ✅ Always explicitly finish waiting
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

## Дополнительные Вопросы (RU)

- Как Turbine ведёт себя при тестировании высокочастотных эмиссий и буферизации событий (учитывая, что backpressure в терминах `Flow` реализуется самим Flow/операторами)?
- В чем разница между методами `test()` и `testIn()`, и когда какой использовать?
- Как тестировать холодные и горячие Flows с помощью Turbine?
- Когда использовать `expectNoEvents()` vs `expectMostRecentItem()`?
- Как тестировать Flows с несколькими коллекторами с помощью Turbine?
- Как Turbine интегрируется с управлением виртуальным временем `TestScope`?

## Follow-ups

- How does Turbine behave when testing high-frequency emissions and event buffering (given that backpressure semantics are defined by Flows/operators themselves)?
- What's the difference between `test()` and `testIn()` methods, and when to use each?
- How to test cold vs hot Flows with Turbine?
- When should you use `expectNoEvents()` vs `expectMostRecentItem()`?
- How to test Flows with multiple collectors using Turbine?
- How does Turbine integrate with TestScope's virtual time control?

## Ссылки (RU)

- Официальная документация Turbine: https://github.com/cashapp/turbine
- Руководство по `kotlinx-coroutines-test`: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/
- [[c-flow]] — основы `Flow` и операторов

## References

- Official Turbine documentation: https://github.com/cashapp/turbine
- kotlinx-coroutines-test guide: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/
- [[c-flow]] — `Flow` basics and operators

## Похожие Вопросы (RU)

### Предпосылки / Концепты

- [[c-flow]] — концепты и операторы `Flow`

### Связанные
- [[q-unit-testing-coroutines-flow--android--medium]] - Тестирование корутин и `Flow`
- [[q-compose-testing--android--medium]] - Тестирование `ViewModel` с `Flow`
- [[q-compose-testing--android--medium]] - Тестирование Compose UI с состоянием на `Flow`

### Продвинутое
- Тестирование различий и практик между `SharedFlow` и `StateFlow`
- Продвинутое тестирование операторов `Flow` (debounce, combine, flatMapLatest)
- Тестирование `Flow` с кастомным `CoroutineContext` и диспетчерами

## Related Questions

### Prerequisites / Concepts

- [[c-flow]] - `Flow` concepts and operators

### Related
- [[q-unit-testing-coroutines-flow--android--medium]] - Testing coroutines and Flows
- [[q-compose-testing--android--medium]] - Testing ViewModels with Flows
- [[q-compose-testing--android--medium]] - Testing Compose UI with state Flows

### Advanced
- Testing `SharedFlow` vs `StateFlow` differences and best practices
- Advanced `Flow` operators testing (debounce, combine, flatMapLatest)
- Testing `Flow` with custom CoroutineContext and dispatchers
