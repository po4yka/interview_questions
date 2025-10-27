---
id: 20251012-122711
title: "Testing ViewModels with Turbine / Тестирование ViewModels с Turbine"
aliases: [Testing ViewModels Turbine, Тестирование ViewModels Turbine, Turbine Flow Testing, StateFlow Testing, SharedFlow Testing]
topic: android
subtopics: [testing-unit, coroutines, architecture-mvvm]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-viewmodel, q-mvvm-pattern--android--medium, q-what-is-viewmodel--android--medium]
created: 2025-10-15
updated: 2025-10-27
sources: [https://github.com/cashapp/turbine, https://developer.android.com/topic/libraries/architecture/viewmodel]
tags: [android/testing-unit, android/coroutines, android/architecture-mvvm, viewmodel, flow, turbine, state-management, difficulty/medium]
---
# Вопрос (RU)

> Как тестировать эмиссии StateFlow и SharedFlow в ViewModels используя библиотеку Turbine?

# Question (EN)

> How do you test StateFlow and SharedFlow emissions in ViewModels using the Turbine library?

---

## Ответ (RU)

**Turbine** — библиотека для тестирования Flow с чистым API для проверки эмиссий, обработки таймаутов и управления множественными потоками.

### Установка

```gradle
testImplementation("app.cash.turbine:turbine:1.0.0")
```

### Базовое тестирование StateFlow

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Initial)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser(id: Int) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading // ✅ Эмиссия Loading
            try {
                val user = repository.getUser(id)
                _uiState.value = UiState.Success(user) // ✅ Эмиссия Success
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message) // ❌ Эмиссия Error
            }
        }
    }
}

@Test
fun `loadUser успешно эмитит Loading затем Success`() = runTest {
    val user = User(1, "John")
    coEvery { repository.getUser(1) } returns user

    viewModel.uiState.test {
        assertEquals(UiState.Initial, awaitItem()) // ✅ Начальное состояние

        viewModel.loadUser(1)

        assertEquals(UiState.Loading, awaitItem()) // ✅ Loading

        val successState = awaitItem() as UiState.Success
        assertEquals("John", successState.user.name) // ✅ Success

        cancelAndIgnoreRemainingEvents() // ✅ Завершение теста
    }
}
```

**Ключевые API:**
- `test {}` — блок для тестирования Flow
- `awaitItem()` — ждёт следующую эмиссию
- `cancelAndIgnoreRemainingEvents()` — завершает тест

### Тестирование SharedFlow (события)

```kotlin
private val _events = MutableSharedFlow<Event>()
val events: SharedFlow<Event> = _events.asSharedFlow()

@Test
fun `loadUser успешно эмитит UserLoaded событие`() = runTest {
    val user = User(1, "John")
    coEvery { repository.getUser(1) } returns user

    viewModel.events.test {
        viewModel.loadUser(1)

        assertEquals(Event.UserLoaded, awaitItem()) // ✅ Ждём событие

        cancelAndIgnoreRemainingEvents()
    }
}
```

**Важно:** SharedFlow не имеет начального значения, поэтому начинайте слушать до эмиссии.

### Множественные эмиссии

```kotlin
@Test
fun `поиск эмитит множественные результаты`() = runTest {
    viewModel.searchResults.test {
        assertEquals(emptyList(), awaitItem()) // ✅ Начальный

        viewModel.search("a")
        assertEquals(listOf(Item("Apple")), awaitItem()) // ✅ Первый

        viewModel.search("ab")
        assertEquals(listOf(Item("Abacus")), awaitItem()) // ✅ Второй

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Таймауты и ожидание

```kotlin
@Test
fun `тест с таймаутом`() = runTest {
    viewModel.events.test(timeout = 5.seconds) { // ✅ Ждём до 5 секунд
        viewModel.loadUser(1)
        assertEquals(Event.UserLoaded, awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
}

@Test
fun `expectNoEvents проверяет тишину`() = runTest {
    viewModel.events.test {
        expectNoEvents() // ✅ Не должно быть эмиссий
        viewModel.loadUser(1)
        awaitItem() // ✅ Теперь ожидаем событие
        cancelAndIgnoreRemainingEvents()
    }
}
```

### Пропуск элементов

```kotlin
@Test
fun `skipItems пропускает эмиссии`() = runTest {
    viewModel.uiState.test {
        awaitItem() // Initial
        viewModel.loadUser(1)
        skipItems(1) // ✅ Пропускаем Loading
        val state = awaitItem() as UiState.Success // ✅ Прыгаем к Success
        assertEquals("John", state.user.name)
        cancelAndIgnoreRemainingEvents()
    }
}

@Test
fun `expectMostRecentItem получает последний`() = runTest {
    viewModel.uiState.test {
        awaitItem()
        repeat(5) { viewModel.refresh() } // Множественные обновления
        val latestState = expectMostRecentItem() // ✅ Игнорируем промежуточные
        cancelAndIgnoreRemainingEvents()
    }
}
```

### Тестирование множественных Flow

```kotlin
@Test
fun `тест состояния и событий вместе`() = runTest {
    val user = User(1, "John")
    coEvery { repository.getUser(1) } returns user

    // ✅ Запускаем оба коллектора параллельно
    launch {
        viewModel.uiState.test {
            assertEquals(UiState.Initial, awaitItem())
            assertEquals(UiState.Loading, awaitItem())
            val successState = awaitItem() as UiState.Success
            assertEquals("John", successState.user.name)
            cancelAndIgnoreRemainingEvents()
        }
    }

    launch {
        viewModel.events.test {
            assertEquals(Event.UserLoaded, awaitItem())
            cancelAndIgnoreRemainingEvents()
        }
    }

    viewModel.loadUser(1) // Триггерим действие
}
```

### Лучшие практики

**1. Всегда ожидайте начальную эмиссию для StateFlow:**

```kotlin
// ✅ ПРАВИЛЬНО
viewModel.uiState.test {
    assertEquals(UiState.Initial, awaitItem()) // Начальное значение
    // ... тестовая логика
}

// ❌ НЕПРАВИЛЬНО (пропустит начальное значение)
viewModel.uiState.test {
    viewModel.load()
    assertEquals(UiState.Loading, awaitItem()) // Пропускает Initial!
}
```

**2. Используйте cancelAndIgnoreRemainingEvents:**

```kotlin
// ✅ ПРАВИЛЬНО
test {
    assertEquals(expected, awaitItem())
    cancelAndIgnoreRemainingEvents() // Завершаем тест
}

// ❌ НЕПРАВИЛЬНО (тест зависнет)
test {
    assertEquals(expected, awaitItem())
    // Нет cancel - тест ждёт бесконечно
}
```

**3. Тестируйте состояние и события отдельно или вместе:**

```kotlin
// ✅ ХОРОШО: Отдельные тесты
@Test fun testState()
@Test fun testEvents()

// ✅ ТОЖЕ ХОРОШО: Вместе когда связаны
@Test fun testStateAndEvents()
```

---

## Answer (EN)

**Turbine** is a testing library that simplifies Flow testing with a clean API for asserting emissions, handling timeouts, and managing multiple flows.

### Setup

```gradle
testImplementation("app.cash.turbine:turbine:1.0.0")
```

### Basic StateFlow Testing

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Initial)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser(id: Int) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading // ✅ Emit Loading
            try {
                val user = repository.getUser(id)
                _uiState.value = UiState.Success(user) // ✅ Emit Success
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message) // ❌ Emit Error
            }
        }
    }
}

@Test
fun `loadUser success emits Loading then Success`() = runTest {
    val user = User(1, "John")
    coEvery { repository.getUser(1) } returns user

    viewModel.uiState.test {
        assertEquals(UiState.Initial, awaitItem()) // ✅ Initial state

        viewModel.loadUser(1)

        assertEquals(UiState.Loading, awaitItem()) // ✅ Loading

        val successState = awaitItem() as UiState.Success
        assertEquals("John", successState.user.name) // ✅ Success

        cancelAndIgnoreRemainingEvents() // ✅ Finish test
    }
}
```

**Key APIs:**
- `test {}` — block for testing Flow
- `awaitItem()` — waits for next emission
- `cancelAndIgnoreRemainingEvents()` — finishes test

### Testing SharedFlow (Events)

```kotlin
private val _events = MutableSharedFlow<Event>()
val events: SharedFlow<Event> = _events.asSharedFlow()

@Test
fun `loadUser success emits UserLoaded event`() = runTest {
    val user = User(1, "John")
    coEvery { repository.getUser(1) } returns user

    viewModel.events.test {
        viewModel.loadUser(1)

        assertEquals(Event.UserLoaded, awaitItem()) // ✅ Wait for event

        cancelAndIgnoreRemainingEvents()
    }
}
```

**Important:** SharedFlow has no initial value, so start listening before emission.

### Multiple Emissions

```kotlin
@Test
fun `search emits multiple results`() = runTest {
    viewModel.searchResults.test {
        assertEquals(emptyList(), awaitItem()) // ✅ Initial

        viewModel.search("a")
        assertEquals(listOf(Item("Apple")), awaitItem()) // ✅ First

        viewModel.search("ab")
        assertEquals(listOf(Item("Abacus")), awaitItem()) // ✅ Second

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Timeouts and Waiting

```kotlin
@Test
fun `test with timeout`() = runTest {
    viewModel.events.test(timeout = 5.seconds) { // ✅ Wait up to 5 seconds
        viewModel.loadUser(1)
        assertEquals(Event.UserLoaded, awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
}

@Test
fun `expectNoEvents verifies silence`() = runTest {
    viewModel.events.test {
        expectNoEvents() // ✅ Should not emit anything
        viewModel.loadUser(1)
        awaitItem() // ✅ Now expect an event
        cancelAndIgnoreRemainingEvents()
    }
}
```

### Skip Items

```kotlin
@Test
fun `skipItems skips emissions`() = runTest {
    viewModel.uiState.test {
        awaitItem() // Initial
        viewModel.loadUser(1)
        skipItems(1) // ✅ Skip Loading state
        val state = awaitItem() as UiState.Success // ✅ Jump to Success
        assertEquals("John", state.user.name)
        cancelAndIgnoreRemainingEvents()
    }
}

@Test
fun `expectMostRecentItem gets latest`() = runTest {
    viewModel.uiState.test {
        awaitItem()
        repeat(5) { viewModel.refresh() } // Multiple updates
        val latestState = expectMostRecentItem() // ✅ Ignore intermediate
        cancelAndIgnoreRemainingEvents()
    }
}
```

### Testing Multiple Flows

```kotlin
@Test
fun `test state and events together`() = runTest {
    val user = User(1, "John")
    coEvery { repository.getUser(1) } returns user

    // ✅ Launch both collectors in parallel
    launch {
        viewModel.uiState.test {
            assertEquals(UiState.Initial, awaitItem())
            assertEquals(UiState.Loading, awaitItem())
            val successState = awaitItem() as UiState.Success
            assertEquals("John", successState.user.name)
            cancelAndIgnoreRemainingEvents()
        }
    }

    launch {
        viewModel.events.test {
            assertEquals(Event.UserLoaded, awaitItem())
            cancelAndIgnoreRemainingEvents()
        }
    }

    viewModel.loadUser(1) // Trigger action
}
```

### Best Practices

**1. Always await initial emission for StateFlow:**

```kotlin
// ✅ CORRECT
viewModel.uiState.test {
    assertEquals(UiState.Initial, awaitItem()) // Initial value
    // ... test logic
}

// ❌ WRONG (will miss initial value)
viewModel.uiState.test {
    viewModel.load()
    assertEquals(UiState.Loading, awaitItem()) // Misses Initial!
}
```

**2. Use cancelAndIgnoreRemainingEvents:**

```kotlin
// ✅ CORRECT
test {
    assertEquals(expected, awaitItem())
    cancelAndIgnoreRemainingEvents() // Finish test
}

// ❌ WRONG (test will hang)
test {
    assertEquals(expected, awaitItem())
    // Missing cancel - test waits forever
}
```

**3. Test state and events separately or together:**

```kotlin
// ✅ GOOD: Separate tests
@Test fun testState()
@Test fun testEvents()

// ✅ ALSO GOOD: Together when related
@Test fun testStateAndEvents()
```

---

## Follow-ups

- How do you test ViewModels that emit both StateFlow and SharedFlow simultaneously?
- What are the best practices for handling timeout scenarios in Flow testing?
- How can you mock dependencies in ViewModel tests while using Turbine?
- How to test hot flows vs cold flows differently?
- What's the difference between `awaitItem()` and `expectMostRecentItem()`?

## References

- [[c-viewmodel]] - ViewModel concept
- https://github.com/cashapp/turbine - Turbine library
- https://developer.android.com/topic/libraries/architecture/viewmodel - ViewModel testing guide
- https://kotlinlang.org/docs/flow.html - Kotlin Flow documentation

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-viewmodel--android--medium]] - ViewModel basics

### Related (Same Level)
- [[q-mvvm-pattern--android--medium]] - MVVM pattern
- [[q-why-is-viewmodel-needed-and-what-happens-in-it--android--medium]] - ViewModel internals

### Advanced (Harder)
- [[q-mvi-architecture--android--hard]] - MVI architecture
- [[q-testing-coroutines-flow--android--hard]] - Advanced Flow testing
