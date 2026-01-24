---
id: kotlin-flow-007
title: "Testing Flows with Turbine / Тестирование Flow с Turbine"
aliases:
  - Testing Flows Turbine
  - Flow Testing
  - Turbine Library
topic: kotlin
subtopics:
  - coroutines
  - flow
  - testing
question_kind: theory
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
source: internal
status: draft
moc: moc-kotlin
related:
  - c-kotlin
  - c-flow
  - q-testing-stateflow-sharedflow--kotlin--medium
created: 2026-01-23
updated: 2026-01-23
tags:
  - coroutines
  - difficulty/medium
  - flow
  - kotlin
  - testing
  - turbine
---
# Vopros (RU)
> Как тестировать Flow с библиотекой Turbine? Какие есть методы и паттерны?

---

# Question (EN)
> How to test Flows with the Turbine library? What methods and patterns are available?

## Otvet (RU)

### Turbine Overview

Turbine - библиотека от Cash App для тестирования Kotlin Flow. Предоставляет DSL для детерминированного тестирования эмиссий.

```gradle
testImplementation("app.cash.turbine:turbine:1.0.0")
```

### Базовое Использование

```kotlin
import app.cash.turbine.test

@Test
fun `basic flow test`() = runTest {
    flowOf(1, 2, 3).test {
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        assertEquals(3, awaitItem())
        awaitComplete()
    }
}
```

### Основные Методы

```kotlin
flow.test {
    // Получить следующий элемент (ждёт эмиссии)
    val item = awaitItem()

    // Получить ошибку
    val error = awaitError()

    // Ожидать завершения Flow
    awaitComplete()

    // Проверить что нет событий
    expectNoEvents()

    // Отменить и игнорировать оставшиеся события
    cancelAndIgnoreRemainingEvents()

    // Отменить и проверить что нет оставшихся событий
    cancelAndConsumeRemainingEvents()

    // Пропустить N элементов
    skipItems(count = 3)
}
```

### Тестирование StateFlow

```kotlin
class CounterViewModel {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() { _count.value++ }
    fun decrement() { _count.value-- }
}

@Test
fun `counter increments correctly`() = runTest {
    val viewModel = CounterViewModel()

    viewModel.count.test {
        // StateFlow всегда эмитирует начальное значение
        assertEquals(0, awaitItem())

        viewModel.increment()
        assertEquals(1, awaitItem())

        viewModel.increment()
        assertEquals(2, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}

@Test
fun `StateFlow skips duplicate values`() = runTest {
    val viewModel = CounterViewModel()

    viewModel.count.test {
        assertEquals(0, awaitItem())

        viewModel.increment()  // 0 -> 1
        assertEquals(1, awaitItem())

        // Установка того же значения - эмиссии не будет
        // Ничего не делаем, ожидаем отсутствие событий
        expectNoEvents()

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Тестирование SharedFlow

```kotlin
class EventViewModel {
    private val _events = MutableSharedFlow<UiEvent>()
    val events: SharedFlow<UiEvent> = _events.asSharedFlow()

    suspend fun sendEvent(event: UiEvent) {
        _events.emit(event)
    }
}

sealed class UiEvent {
    data class ShowMessage(val text: String) : UiEvent()
    object NavigateBack : UiEvent()
}

@Test
fun `events are emitted correctly`() = runTest {
    val viewModel = EventViewModel()

    viewModel.events.test {
        // SharedFlow без replay не имеет начального значения
        expectNoEvents()

        viewModel.sendEvent(UiEvent.ShowMessage("Hello"))
        assertEquals(UiEvent.ShowMessage("Hello"), awaitItem())

        viewModel.sendEvent(UiEvent.NavigateBack)
        assertEquals(UiEvent.NavigateBack, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Тестирование Операторов

```kotlin
@Test
fun `map operator transforms values`() = runTest {
    flowOf(1, 2, 3)
        .map { it * 2 }
        .test {
            assertEquals(2, awaitItem())
            assertEquals(4, awaitItem())
            assertEquals(6, awaitItem())
            awaitComplete()
        }
}

@Test
fun `filter operator filters values`() = runTest {
    flowOf(1, 2, 3, 4, 5)
        .filter { it % 2 == 0 }
        .test {
            assertEquals(2, awaitItem())
            assertEquals(4, awaitItem())
            awaitComplete()
        }
}

@Test
fun `debounce delays emissions`() = runTest {
    flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
        delay(500)
    }
    .debounce(300)
    .test {
        // Только 3 пройдёт debounce
        assertEquals(3, awaitItem())
        awaitComplete()
    }
}
```

### Тестирование Ошибок

```kotlin
@Test
fun `flow emits error`() = runTest {
    flow {
        emit(1)
        throw IOException("Network error")
    }.test {
        assertEquals(1, awaitItem())

        val error = awaitError()
        assertTrue(error is IOException)
        assertEquals("Network error", error.message)
    }
}

@Test
fun `catch operator handles error`() = runTest {
    flow {
        emit(1)
        throw IOException("Error")
    }
    .catch { emit(-1) }
    .test {
        assertEquals(1, awaitItem())
        assertEquals(-1, awaitItem())
        awaitComplete()
    }
}
```

### Тестирование с Timeout

```kotlin
@Test
fun `test with custom timeout`() = runTest {
    flow {
        delay(5000)
        emit(1)
    }.test(timeout = 10.seconds) {
        assertEquals(1, awaitItem())
        awaitComplete()
    }
}
```

### Тестирование ViewModel с Flow

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var repository: FakeUserRepository
    private lateinit var viewModel: UserViewModel

    @Before
    fun setup() {
        repository = FakeUserRepository()
        viewModel = UserViewModel(repository)
    }

    @Test
    fun `loadUser success flow`() = runTest {
        val user = User(id = "1", name = "John")
        repository.setUser(user)

        viewModel.uiState.test {
            // Начальное состояние
            assertEquals(UiState.Idle, awaitItem())

            // Запускаем загрузку
            viewModel.loadUser("1")

            // Loading
            assertEquals(UiState.Loading, awaitItem())

            // Success
            val successState = awaitItem()
            assertTrue(successState is UiState.Success)
            assertEquals(user, (successState as UiState.Success).user)

            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `loadUser error flow`() = runTest {
        repository.setError(IOException("Network error"))

        viewModel.uiState.test {
            assertEquals(UiState.Idle, awaitItem())

            viewModel.loadUser("1")

            assertEquals(UiState.Loading, awaitItem())

            val errorState = awaitItem()
            assertTrue(errorState is UiState.Error)
            assertEquals("Network error", (errorState as UiState.Error).message)

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

### Параллельное Тестирование Flow

```kotlin
@Test
fun `test multiple flows in parallel`() = runTest {
    val flow1 = flowOf(1, 2, 3)
    val flow2 = flowOf("a", "b", "c")

    turbineScope {
        val turbine1 = flow1.testIn(backgroundScope)
        val turbine2 = flow2.testIn(backgroundScope)

        assertEquals(1, turbine1.awaitItem())
        assertEquals("a", turbine2.awaitItem())

        assertEquals(2, turbine1.awaitItem())
        assertEquals("b", turbine2.awaitItem())

        assertEquals(3, turbine1.awaitItem())
        assertEquals("c", turbine2.awaitItem())

        turbine1.awaitComplete()
        turbine2.awaitComplete()
    }
}
```

### Полезные Паттерны

```kotlin
// Проверка всех элементов за раз
@Test
fun `collect all items`() = runTest {
    flowOf(1, 2, 3).test {
        val items = cancelAndConsumeRemainingEvents()
            .filterIsInstance<Event.Item<Int>>()
            .map { it.value }

        assertEquals(listOf(1, 2, 3), items)
    }
}

// Пропуск начального значения StateFlow
@Test
fun `skip initial state`() = runTest {
    val stateFlow = MutableStateFlow(0)

    stateFlow.test {
        skipItems(1)  // Пропустить начальное значение

        stateFlow.value = 1
        assertEquals(1, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

---

## Answer (EN)

### Turbine Overview

Turbine is a library from Cash App for testing Kotlin Flow. It provides a DSL for deterministic emission testing.

```gradle
testImplementation("app.cash.turbine:turbine:1.0.0")
```

### Basic Usage

```kotlin
import app.cash.turbine.test

@Test
fun `basic flow test`() = runTest {
    flowOf(1, 2, 3).test {
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        assertEquals(3, awaitItem())
        awaitComplete()
    }
}
```

### Main Methods

```kotlin
flow.test {
    // Get next item (waits for emission)
    val item = awaitItem()

    // Get error
    val error = awaitError()

    // Wait for Flow completion
    awaitComplete()

    // Verify no events
    expectNoEvents()

    // Cancel and ignore remaining events
    cancelAndIgnoreRemainingEvents()

    // Cancel and verify no remaining events
    cancelAndConsumeRemainingEvents()

    // Skip N items
    skipItems(count = 3)
}
```

### Testing StateFlow

```kotlin
class CounterViewModel {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() { _count.value++ }
    fun decrement() { _count.value-- }
}

@Test
fun `counter increments correctly`() = runTest {
    val viewModel = CounterViewModel()

    viewModel.count.test {
        // StateFlow always emits initial value
        assertEquals(0, awaitItem())

        viewModel.increment()
        assertEquals(1, awaitItem())

        viewModel.increment()
        assertEquals(2, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}

@Test
fun `StateFlow skips duplicate values`() = runTest {
    val viewModel = CounterViewModel()

    viewModel.count.test {
        assertEquals(0, awaitItem())

        viewModel.increment()  // 0 -> 1
        assertEquals(1, awaitItem())

        // Setting same value - no emission
        // Do nothing, expect no events
        expectNoEvents()

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Testing SharedFlow

```kotlin
class EventViewModel {
    private val _events = MutableSharedFlow<UiEvent>()
    val events: SharedFlow<UiEvent> = _events.asSharedFlow()

    suspend fun sendEvent(event: UiEvent) {
        _events.emit(event)
    }
}

sealed class UiEvent {
    data class ShowMessage(val text: String) : UiEvent()
    object NavigateBack : UiEvent()
}

@Test
fun `events are emitted correctly`() = runTest {
    val viewModel = EventViewModel()

    viewModel.events.test {
        // SharedFlow without replay has no initial value
        expectNoEvents()

        viewModel.sendEvent(UiEvent.ShowMessage("Hello"))
        assertEquals(UiEvent.ShowMessage("Hello"), awaitItem())

        viewModel.sendEvent(UiEvent.NavigateBack)
        assertEquals(UiEvent.NavigateBack, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Testing Operators

```kotlin
@Test
fun `map operator transforms values`() = runTest {
    flowOf(1, 2, 3)
        .map { it * 2 }
        .test {
            assertEquals(2, awaitItem())
            assertEquals(4, awaitItem())
            assertEquals(6, awaitItem())
            awaitComplete()
        }
}

@Test
fun `filter operator filters values`() = runTest {
    flowOf(1, 2, 3, 4, 5)
        .filter { it % 2 == 0 }
        .test {
            assertEquals(2, awaitItem())
            assertEquals(4, awaitItem())
            awaitComplete()
        }
}

@Test
fun `debounce delays emissions`() = runTest {
    flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
        delay(500)
    }
    .debounce(300)
    .test {
        // Only 3 passes debounce
        assertEquals(3, awaitItem())
        awaitComplete()
    }
}
```

### Testing Errors

```kotlin
@Test
fun `flow emits error`() = runTest {
    flow {
        emit(1)
        throw IOException("Network error")
    }.test {
        assertEquals(1, awaitItem())

        val error = awaitError()
        assertTrue(error is IOException)
        assertEquals("Network error", error.message)
    }
}

@Test
fun `catch operator handles error`() = runTest {
    flow {
        emit(1)
        throw IOException("Error")
    }
    .catch { emit(-1) }
    .test {
        assertEquals(1, awaitItem())
        assertEquals(-1, awaitItem())
        awaitComplete()
    }
}
```

### Testing with Timeout

```kotlin
@Test
fun `test with custom timeout`() = runTest {
    flow {
        delay(5000)
        emit(1)
    }.test(timeout = 10.seconds) {
        assertEquals(1, awaitItem())
        awaitComplete()
    }
}
```

### Testing ViewModel with Flow

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var repository: FakeUserRepository
    private lateinit var viewModel: UserViewModel

    @Before
    fun setup() {
        repository = FakeUserRepository()
        viewModel = UserViewModel(repository)
    }

    @Test
    fun `loadUser success flow`() = runTest {
        val user = User(id = "1", name = "John")
        repository.setUser(user)

        viewModel.uiState.test {
            // Initial state
            assertEquals(UiState.Idle, awaitItem())

            // Start loading
            viewModel.loadUser("1")

            // Loading
            assertEquals(UiState.Loading, awaitItem())

            // Success
            val successState = awaitItem()
            assertTrue(successState is UiState.Success)
            assertEquals(user, (successState as UiState.Success).user)

            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `loadUser error flow`() = runTest {
        repository.setError(IOException("Network error"))

        viewModel.uiState.test {
            assertEquals(UiState.Idle, awaitItem())

            viewModel.loadUser("1")

            assertEquals(UiState.Loading, awaitItem())

            val errorState = awaitItem()
            assertTrue(errorState is UiState.Error)
            assertEquals("Network error", (errorState as UiState.Error).message)

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

### Parallel Flow Testing

```kotlin
@Test
fun `test multiple flows in parallel`() = runTest {
    val flow1 = flowOf(1, 2, 3)
    val flow2 = flowOf("a", "b", "c")

    turbineScope {
        val turbine1 = flow1.testIn(backgroundScope)
        val turbine2 = flow2.testIn(backgroundScope)

        assertEquals(1, turbine1.awaitItem())
        assertEquals("a", turbine2.awaitItem())

        assertEquals(2, turbine1.awaitItem())
        assertEquals("b", turbine2.awaitItem())

        assertEquals(3, turbine1.awaitItem())
        assertEquals("c", turbine2.awaitItem())

        turbine1.awaitComplete()
        turbine2.awaitComplete()
    }
}
```

### Useful Patterns

```kotlin
// Check all items at once
@Test
fun `collect all items`() = runTest {
    flowOf(1, 2, 3).test {
        val items = cancelAndConsumeRemainingEvents()
            .filterIsInstance<Event.Item<Int>>()
            .map { it.value }

        assertEquals(listOf(1, 2, 3), items)
    }
}

// Skip StateFlow initial value
@Test
fun `skip initial state`() = runTest {
    val stateFlow = MutableStateFlow(0)

    stateFlow.test {
        skipItems(1)  // Skip initial value

        stateFlow.value = 1
        assertEquals(1, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

---

## Dopolnitelnye Voprosy (RU)

1. Как тестировать Flow с debounce без реального ожидания?
2. Чем Turbine лучше ручного тестирования через `toList()`?
3. Как тестировать бесконечные Flow?
4. Как организовать тесты для сложных цепочек операторов?
5. Как работает `turbineScope` и когда его использовать?

---

## Follow-ups

1. How to test Flow with debounce without actual waiting?
2. Why is Turbine better than manual testing via `toList()`?
3. How to test infinite Flows?
4. How to organize tests for complex operator chains?
5. How does `turbineScope` work and when to use it?

---

## Ssylki (RU)

- [[c-kotlin]]
- [[c-flow]]
- [Turbine GitHub](https://github.com/cashapp/turbine)
- [Testing Flows on Android](https://developer.android.com/kotlin/flow/test)

---

## References

- [[c-kotlin]]
- [[c-flow]]
- [Turbine GitHub](https://github.com/cashapp/turbine)
- [Testing Flows on Android](https://developer.android.com/kotlin/flow/test)

---

## Svyazannye Voprosy (RU)

### Sredniy Uroven
- [[q-testing-stateflow-sharedflow--kotlin--medium]]
- [[q-testing-viewmodel-coroutines--kotlin--medium]]
- [[q-test-dispatcher-types--kotlin--medium]]

---

## Related Questions

### Related (Medium)
- [[q-testing-stateflow-sharedflow--kotlin--medium]] - Testing StateFlow and SharedFlow
- [[q-testing-viewmodel-coroutines--kotlin--medium]] - Testing ViewModel coroutines
- [[q-test-dispatcher-types--kotlin--medium]] - Test dispatcher types
