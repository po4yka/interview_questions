---
id: kotlin-094
title: "shareIn and stateIn Operators / Операторы shareIn и stateIn"
aliases: ["shareIn and stateIn Operators", "Операторы shareIn и stateIn"]

# Classification
topic: kotlin
subtopics: [coroutines, flow, hot-flows]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Guide - Question 140019

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-kotlin, c-flow, q-statein-sharein-flow--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [coroutines, difficulty/medium, kotlin]
---
# Вопрос (RU)
> Продвинутая тема корутин Kotlin 140019

---

# Question (EN)
> Kotlin Coroutines advanced topic 140019

## Ответ (RU)

Операторы `shareIn` и `stateIn` обычно используются для преобразования холодных `Flow` в горячие `Flow`, которые можно разделять между несколькими коллекторами (а также могут применяться к уже горячим `Flow`).

### shareIn

Делит `Flow` между несколькими коллекторами и создает `SharedFlow`:
```kotlin
val sharedFlow = flow {
    repeat(5) {
        emit(it)
        delay(100)
    }
}.shareIn(
    scope = viewModelScope,
    started = SharingStarted.WhileSubscribed(),
    replay = 0
)
```

**Стратегии SharingStarted**:
- `Eagerly` — запуск немедленно при создании, без ожидания подписчиков.
- `Lazily` — запуск при первом подписчике.
- `WhileSubscribed(stopTimeoutMillis, replayExpirationMillis)` — запуск при наличии подписчиков и остановка (отмена upstream) после отсутствия подписчиков с учетом тайм-аутов; без аргументов использует значения по умолчанию.

### stateIn

Создает `StateFlow`, представляющий состояние поверх исходного `Flow`:
```kotlin
val stateFlow = dataFlow
    .map { it.toUiModel() }
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = UiState.Loading
    )
```

### Ключевые Отличия

| Функция | shareIn | stateIn |
|---------|---------|---------|
| Тип возврата | `SharedFlow` | `StateFlow` |
| Начальное значение | Параметр `initialValue` отсутствует; при `replay > 0` первым значением становится первое эмитированное значение | Требуется `initialValue` при создании |
| Replay буфер | Настраиваемый `replay` (0..N) | Эффективно всегда 1: всегда хранит и переигрывает только последнее состояние |
| Основное применение | Общие события, потоки значений | Представление текущего состояния |

### Практический Пример
```kotlin
class ViewModel : ViewModel() {
    // Состояние - используйте stateIn
    val uiState = repository.getData()
        .map { UiState.Success(it) }
        .stateIn(
            viewModelScope,
            SharingStarted.WhileSubscribed(5000),
            UiState.Loading
        )
    
    // События - используйте shareIn
    val events = eventFlow.shareIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(),
        replay = 0
    )
}
```

---

## Answer (EN)

The `shareIn` and `stateIn` operators are commonly used to convert cold `Flow`s into hot `Flow`s that can be shared among multiple collectors (and can also be applied to already hot `Flow`s).

### shareIn

Shares a `Flow` among multiple collectors and creates a `SharedFlow`:
```kotlin
val sharedFlow = flow {
    repeat(5) {
        emit(it)
        delay(100)
    }
}.shareIn(
    scope = viewModelScope,
    started = SharingStarted.WhileSubscribed(),
    replay = 0
)
```

**SharingStarted strategies**:
- `Eagerly` - Start immediately when created, without waiting for subscribers.
- `Lazily` - Start on the first subscriber.
- `WhileSubscribed(stopTimeoutMillis, replayExpirationMillis)` - Start when there is at least one subscriber and stop (cancel upstream) after there are no subscribers, respecting the configured timeouts; when called without arguments it uses default values.

### stateIn

Creates a `StateFlow` that represents state on top of the upstream `Flow`:
```kotlin
val stateFlow = dataFlow
    .map { it.toUiModel() }
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = UiState.Loading
    )
```

### Key Differences

| Feature | shareIn | stateIn |
|---------|---------|---------|
| Return type | `SharedFlow` | `StateFlow` |
| Initial value | No `initialValue` parameter; if `replay > 0`, the first emitted item becomes the first replayed value | Requires an `initialValue` at creation |
| Replay buffer | Configurable `replay` (0..N) | Effectively always 1: it always stores and replays only the latest state |
| Primary use case | Events / shared emissions | State representation |

### Practical Example
```kotlin
class ViewModel : ViewModel() {
    // State - use stateIn
    val uiState = repository.getData()
        .map { UiState.Success(it) }
        .stateIn(
            viewModelScope,
            SharingStarted.WhileSubscribed(5000),
            UiState.Loading
        )
    
    // Events - use shareIn
    val events = eventFlow.shareIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(),
        replay = 0
    )
}
```

---

## Follow-ups

1. How do `SharedFlow` and `StateFlow` differ from `Channel` for one-off events and backpressure handling?
2. In which scenarios would you choose `SharingStarted.Eagerly` vs `SharingStarted.WhileSubscribed`, and how does this impact resource usage?
3. How would you migrate an existing `LiveData`-based API to use `StateFlow` with `stateIn` in a `ViewModel`?
4. What pitfalls can occur when using `shareIn` with `replay > 0` for UI events, and how can you avoid them?
5. How do `shareIn`/`stateIn` interact with structured concurrency and the lifecycle of a `ViewModel` or other coroutine scopes?

---

## References

- [Kotlin Coroutines Documentation](https://kotlinlang.org/docs/coroutines-overview.html)
- [[c-kotlin]]
- [[c-flow]]

---

## Related Questions

### Prerequisites (Easier)
- [[q-flow-basics--kotlin--easy]] - Flow

### Related (Medium)
- [[q-statein-sharein-flow--kotlin--medium]] - Flow
- [[q-catch-operator-flow--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-hot-cold-flows--kotlin--medium]] - Coroutines

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
