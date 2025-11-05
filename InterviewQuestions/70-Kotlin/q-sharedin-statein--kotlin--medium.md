---
id: kotlin-094
title: "shareIn and stateIn Operators / Операторы shareIn и stateIn"
aliases: ["shareIn and stateIn Operators, Операторы shareIn и stateIn"]

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
related: [q-desugaring-android-java--kotlin--medium, q-kotlin-java-type-differences--programming-languages--medium, q-what-is-coroutine--kotlin--easy]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [coroutines, difficulty/medium, kotlin]
date created: Sunday, October 12th 2025, 3:39:19 pm
date modified: Saturday, November 1st 2025, 5:43:23 pm
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

### Ключевые Отличия

| Функция | shareIn | stateIn |
|---------|---------|---------|
| Тип возврата | SharedFlow | StateFlow |
| Начальное значение | Нет | Требуется |
| Replay | Настраиваемый | Всегда 1 |
| Применение | События | Состояние |

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
