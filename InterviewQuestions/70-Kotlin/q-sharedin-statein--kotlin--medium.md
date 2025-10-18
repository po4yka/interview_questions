---
id: 20251012-140019
title: "shareIn and stateIn Operators / Операторы shareIn и stateIn"
aliases: []

# Classification
topic: kotlin
subtopics: [coroutines, flow, sharedin, statein, hot-flows]
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
related: [q-kotlin-java-type-differences--programming-languages--medium, q-what-is-coroutine--kotlin--easy, q-desugaring-android-java--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [kotlin, coroutines, difficulty/medium]
---
# Question (EN)
> Kotlin Coroutines advanced topic 140019

# Вопрос (RU)
> Продвинутая тема корутин Kotlin 140019

---

## Answer (EN)


The `shareIn` and `stateIn` operators convert cold Flows into hot Flows that can be shared among multiple collectors.

### shareIn

Shares a Flow among multiple collectors:
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
- `Eagerly` - Start immediately
- `Lazily` - Start on first subscriber
- `WhileSubscribed()` - Start/stop based on subscribers

### stateIn

Creates a StateFlow that represents state:
```kotlin
val state Flow = dataFlow
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
| Return type | SharedFlow | StateFlow |
| Initial value | No | Required |
| Replay | Configurable | Always 1 |
| Use case | Events | State |

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
---

## Ответ (RU)


Операторы `shareIn` и `stateIn` преобразуют холодные Flow в горячие Flow, которые можно разделять между несколькими коллекторами.

### shareIn

Делит Flow между несколькими коллекторами:
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
- `Eagerly` - Запуск немедленно
- `Lazily` - Запуск при первом подписчике
- `WhileSubscribed()` - Запуск/остановка на основе подписчиков

### stateIn

Создает StateFlow представляющий состояние:
```kotlin
val stateFlow = dataFlow
    .map { it.toUiModel() }
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = UiState.Loading
    )
```

### Ключевые отличия

| Функция | shareIn | stateIn |
|---------|---------|---------|
| Тип возврата | SharedFlow | StateFlow |
| Начальное значение | Нет | Требуется |
| Replay | Настраиваемый | Всегда 1 |
| Применение | События | Состояние |

### Практический пример
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
---

## Follow-ups

1. **Follow-up question 1**
2. **Follow-up question 2**

---

## References

- [Kotlin Coroutines Documentation](https://kotlinlang.org/docs/coroutines-overview.html)

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
