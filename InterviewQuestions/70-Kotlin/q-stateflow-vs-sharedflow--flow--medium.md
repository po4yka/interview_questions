---
id: kotlin-flow-001
title: StateFlow vs SharedFlow Differences / Различия StateFlow и SharedFlow
aliases:
  - StateFlow vs SharedFlow
  - SharedFlow vs StateFlow
  - Hot Flows Comparison
topic: kotlin
subtopics:
  - coroutines
  - flow
  - state-management
question_kind: comparison
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-kotlin
related:
  - c-flow
  - c-kotlin
  - q-hot-cold-flows--kotlin--medium
  - q-stateflow-purpose--kotlin--medium
created: 2026-01-23
updated: 2026-01-23
tags:
  - kotlin_flow
  - difficulty::medium
  - stateflow
  - sharedflow
  - hot-flows
---
# Question (EN)
> What are the key differences between `StateFlow` and `SharedFlow`? When should you use each one?

# Vopros (RU)
> Каковы основные различия между `StateFlow` и `SharedFlow`? Когда следует использовать каждый из них?

## Answer (EN)

`StateFlow` and `SharedFlow` are both **hot flows** in Kotlin Coroutines, but they serve different purposes and have distinct characteristics.

### Key Differences

| Feature | StateFlow | SharedFlow |
|---------|-----------|------------|
| **Initial value** | Required | Not required |
| **Current value** | Always accessible via `.value` | No `.value` property |
| **Replay** | Always 1 (latest value) | Configurable (0 to N) |
| **Equality check** | Conflates equal values | Emits all values |
| **Buffer overflow** | Not configurable | Configurable |
| **Use case** | State holder | Events/signals |

### StateFlow Characteristics

```kotlin
// StateFlow ALWAYS requires an initial value
private val _uiState = MutableStateFlow(UiState.Loading)
val uiState: StateFlow<UiState> = _uiState.asStateFlow()

// Key properties:
// 1. Always has a value - can read .value anytime
val currentState = _uiState.value

// 2. Conflates equal values - won't emit if value unchanged
_uiState.value = UiState.Loading // No emission if already Loading

// 3. New collectors immediately get current value (replay = 1)
```

### SharedFlow Characteristics

```kotlin
// SharedFlow does NOT require initial value
private val _events = MutableSharedFlow<UiEvent>(
    replay = 0,              // No replay by default
    extraBufferCapacity = 1, // Buffer for non-suspending emit
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)
val events: SharedFlow<UiEvent> = _events.asSharedFlow()

// Key properties:
// 1. No .value property - cannot read current value
// 2. Emits ALL values, even duplicates
// 3. Configurable replay, buffer, and overflow behavior
```

### When to Use StateFlow

Use `StateFlow` for **state** that:
- Always has a meaningful current value
- Observers need the latest state immediately
- Duplicate consecutive values should be ignored

```kotlin
class SearchViewModel : ViewModel() {
    // UI State - always has a value, observers need latest
    private val _searchState = MutableStateFlow(SearchState())
    val searchState: StateFlow<SearchState> = _searchState.asStateFlow()

    fun updateQuery(query: String) {
        _searchState.update { it.copy(query = query) }
    }
}

data class SearchState(
    val query: String = "",
    val results: List<Item> = emptyList(),
    val isLoading: Boolean = false
)
```

### When to Use SharedFlow

Use `SharedFlow` for **events** that:
- Should not be replayed to new collectors
- Should be delivered even if duplicates
- May have no value initially

```kotlin
class NavigationViewModel : ViewModel() {
    // Navigation events - fire-and-forget, no replay needed
    private val _navigationEvents = MutableSharedFlow<NavigationEvent>()
    val navigationEvents: SharedFlow<NavigationEvent> = _navigationEvents.asSharedFlow()

    fun navigateToDetails(id: String) {
        viewModelScope.launch {
            _navigationEvents.emit(NavigationEvent.ToDetails(id))
        }
    }
}

sealed class NavigationEvent {
    data class ToDetails(val id: String) : NavigationEvent()
    data object Back : NavigationEvent()
}
```

### StateFlow is a Specialized SharedFlow

Internally, `StateFlow` is implemented as a `SharedFlow` with specific configuration:

```kotlin
// StateFlow is conceptually equivalent to:
MutableSharedFlow<T>(
    replay = 1,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
).apply {
    // Plus: distinctUntilChanged behavior
    // Plus: always has initial value
    // Plus: .value property for synchronous access
}
```

### Common Patterns

**Converting Flow to StateFlow/SharedFlow:**

```kotlin
// Cold Flow to StateFlow
val userState: StateFlow<User?> = userRepository.observeUser()
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = null
    )

// Cold Flow to SharedFlow
val notifications: SharedFlow<Notification> = notificationSource.stream()
    .shareIn(
        scope = viewModelScope,
        started = SharingStarted.Lazily,
        replay = 0
    )
```

### Decision Guide

```
Is it state (always has a meaningful value)?
  YES -> StateFlow
  NO -> Is it an event/signal?
    YES -> SharedFlow (replay = 0)
    NO -> Do new subscribers need history?
      YES -> SharedFlow (replay > 0)
      NO -> SharedFlow (replay = 0)
```

## Otvet (RU)

`StateFlow` и `SharedFlow` - оба являются **горячими потоками** в Kotlin Coroutines, но служат разным целям и имеют различные характеристики.

### Основные различия

| Характеристика | StateFlow | SharedFlow |
|----------------|-----------|------------|
| **Начальное значение** | Обязательно | Не требуется |
| **Текущее значение** | Всегда доступно через `.value` | Нет свойства `.value` |
| **Replay** | Всегда 1 (последнее значение) | Настраивается (от 0 до N) |
| **Проверка равенства** | Игнорирует одинаковые значения | Эмитит все значения |
| **Переполнение буфера** | Не настраивается | Настраивается |
| **Применение** | Хранение состояния | События/сигналы |

### Характеристики StateFlow

```kotlin
// StateFlow ВСЕГДА требует начальное значение
private val _uiState = MutableStateFlow(UiState.Loading)
val uiState: StateFlow<UiState> = _uiState.asStateFlow()

// Ключевые свойства:
// 1. Всегда имеет значение - можно читать .value в любой момент
val currentState = _uiState.value

// 2. Игнорирует одинаковые значения - не эмитит если значение не изменилось
_uiState.value = UiState.Loading // Нет эмиссии если уже Loading

// 3. Новые подписчики сразу получают текущее значение (replay = 1)
```

### Характеристики SharedFlow

```kotlin
// SharedFlow НЕ требует начального значения
private val _events = MutableSharedFlow<UiEvent>(
    replay = 0,              // Без replay по умолчанию
    extraBufferCapacity = 1, // Буфер для неприостанавливающего emit
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)
val events: SharedFlow<UiEvent> = _events.asSharedFlow()

// Ключевые свойства:
// 1. Нет свойства .value - нельзя прочитать текущее значение
// 2. Эмитит ВСЕ значения, даже дубликаты
// 3. Настраиваемые replay, буфер и поведение при переполнении
```

### Когда использовать StateFlow

Используйте `StateFlow` для **состояния**, которое:
- Всегда имеет осмысленное текущее значение
- Подписчикам нужно последнее состояние немедленно
- Повторяющиеся одинаковые значения следует игнорировать

```kotlin
class SearchViewModel : ViewModel() {
    // UI State - всегда имеет значение, подписчикам нужно последнее
    private val _searchState = MutableStateFlow(SearchState())
    val searchState: StateFlow<SearchState> = _searchState.asStateFlow()

    fun updateQuery(query: String) {
        _searchState.update { it.copy(query = query) }
    }
}

data class SearchState(
    val query: String = "",
    val results: List<Item> = emptyList(),
    val isLoading: Boolean = false
)
```

### Когда использовать SharedFlow

Используйте `SharedFlow` для **событий**, которые:
- Не должны повторяться новым подписчикам
- Должны доставляться даже если это дубликаты
- Могут не иметь значения изначально

```kotlin
class NavigationViewModel : ViewModel() {
    // События навигации - отправил и забыл, replay не нужен
    private val _navigationEvents = MutableSharedFlow<NavigationEvent>()
    val navigationEvents: SharedFlow<NavigationEvent> = _navigationEvents.asSharedFlow()

    fun navigateToDetails(id: String) {
        viewModelScope.launch {
            _navigationEvents.emit(NavigationEvent.ToDetails(id))
        }
    }
}

sealed class NavigationEvent {
    data class ToDetails(val id: String) : NavigationEvent()
    data object Back : NavigationEvent()
}
```

### StateFlow - это специализированный SharedFlow

Внутренне `StateFlow` реализован как `SharedFlow` со специфичной конфигурацией:

```kotlin
// StateFlow концептуально эквивалентен:
MutableSharedFlow<T>(
    replay = 1,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
).apply {
    // Плюс: поведение distinctUntilChanged
    // Плюс: всегда имеет начальное значение
    // Плюс: свойство .value для синхронного доступа
}
```

### Руководство по выбору

```
Это состояние (всегда имеет осмысленное значение)?
  ДА -> StateFlow
  НЕТ -> Это событие/сигнал?
    ДА -> SharedFlow (replay = 0)
    НЕТ -> Нужна ли новым подписчикам история?
      ДА -> SharedFlow (replay > 0)
      НЕТ -> SharedFlow (replay = 0)
```

## Follow-ups

1. How does `StateFlow`'s conflation affect UI updates with rapidly changing data?
2. What happens if you emit to a `SharedFlow` with `replay = 0` and no active collectors?
3. How do you handle events with `SharedFlow` to ensure they're not lost during configuration changes?
4. When would you use `SharedFlow` with `replay > 0` instead of `StateFlow`?
5. How do `stateIn` and `shareIn` differ in their caching behavior?

## References

- [StateFlow and SharedFlow - Kotlin Documentation](https://kotlinlang.org/docs/flow.html#stateflow-and-sharedflow)
- [StateFlow and SharedFlow - Android Developers](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)
- [[c-flow]]
- [[c-kotlin]]

## Related Questions

- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold Flows
- [[q-stateflow-purpose--kotlin--medium]] - StateFlow Purpose
- [[q-sharedflow-replay-buffer-config--kotlin--medium]] - SharedFlow Configuration
- [[q-stateflow-sharedflow-differences--kotlin--medium]] - StateFlow SharedFlow Differences
