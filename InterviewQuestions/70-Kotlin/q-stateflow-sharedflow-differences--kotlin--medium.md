---
id: 20251005-235001
title: "StateFlow and SharedFlow / StateFlow и SharedFlow"
aliases: []

# Classification
topic: kotlin
subtopics: [stateflow, sharedflow, flow, hot-flows, coroutines]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-flow-basics--kotlin--medium, q-kotlin-coroutines-introduction--kotlin--medium, q-stateflow-sharedflow-android--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-10-18

tags: [kotlin, stateflow, sharedflow, flow, hot-flows, coroutines, difficulty/medium]
---
# Question (EN)
> What are StateFlow and SharedFlow in Kotlin? What are the differences between them?
# Вопрос (RU)
> Что такое StateFlow и SharedFlow в Kotlin? В чем их отличия?

---

## Answer (EN)

`StateFlow` and `SharedFlow` are Flow APIs that enable flows to optimally emit state updates and emit values to multiple consumers. They are **hot flows**, meaning they are active and can emit values even when there are no collectors.

### StateFlow

`StateFlow` is a state-holder observable flow that emits the current and new state updates to its collectors. The current state value can also be read through its `value` property.

#### Key Characteristics

1. **Always has a value** - Requires an initial state to be passed to the constructor
2. **State holder** - Always represents the current state
3. **Conflates values** - Only emits distinct values, skips duplicate consecutive values
4. **Hot flow** - Active and in memory even without collectors
5. **Thread-safe** - Can be safely updated from any thread

#### Example Usage

```kotlin
class LatestNewsViewModel(
    private val newsRepository: NewsRepository
) : ViewModel() {
    // Backing property to avoid state updates from other classes
    private val _uiState = MutableStateFlow(LatestNewsUiState.Success(emptyList()))
    // The UI collects from this StateFlow to get its state updates
    val uiState: StateFlow<LatestNewsUiState> = _uiState

    init {
        viewModelScope.launch {
            newsRepository.favoriteLatestNews
                // Update View with the latest favorite news
                .collect { favoriteNews ->
                    _uiState.value = LatestNewsUiState.Success(favoriteNews)
                }
        }
    }
}

// Represents different states for the LatestNews screen
sealed class LatestNewsUiState {
    data class Success(val news: List<ArticleHeadline>): LatestNewsUiState()
    data class Error(val exception: Throwable): LatestNewsUiState()
}
```

#### StateFlow vs LiveData

Both are observable data holder classes with similar patterns:

| Feature | StateFlow | LiveData |
|---------|-----------|----------|
| **Initial value** | Required | Not required |
| **Lifecycle awareness** | Manual (collect in lifecycle scope) | Automatic (observe) |
| **Thread safety** | Built-in | Built-in |
| **Transformation** | Flow operators | LiveData transformations |
| **Backpressure** | Conflation | N/A |

**Key Difference**: `LiveData.observe()` automatically unregisters when view goes to STOPPED state, whereas collecting from StateFlow doesn't stop automatically - you need to collect in a lifecycle-aware scope like `lifecycleScope.launch { repeatOnLifecycle(STARTED) { ... } }`.

### SharedFlow

The `shareIn` function returns a `SharedFlow`, a hot flow that emits values to all consumers that collect from it. A `SharedFlow` is a highly-configurable generalization of `StateFlow`.

#### Key Characteristics

1. **No initial value required** - Can start without any value
2. **Broadcasts events** - All collectors receive the same emissions
3. **Configurable replay cache** - Can replay N previous values to new subscribers
4. **Configurable buffer** - Control overflow behavior
5. **More flexible** - Can represent events, not just state

#### Configuration Options

```kotlin
private val _tickFlow = MutableSharedFlow<Unit>(
    replay = 0,                          // How many values to replay to new collectors
    extraBufferCapacity = 0,             // Extra buffer beyond replay
    onBufferOverflow = BufferOverflow.SUSPEND  // What to do when buffer is full
)
```

**BufferOverflow Options**:
- `SUSPEND` (default) - Suspends the caller when buffer is full
- `DROP_LATEST` - Drops the latest value when buffer is full
- `DROP_OLDEST` - Drops the oldest value when buffer is full

#### Example Usage

```kotlin
// Class that centralizes when the content of the app needs to be refreshed
class TickHandler(
    private val externalScope: CoroutineScope,
    private val tickIntervalMs: Long = 5000
) {
    // Backing property to avoid flow emissions from other classes
    private val _tickFlow = MutableSharedFlow<Unit>(replay = 0)
    val tickFlow: SharedFlow<Unit> = _tickFlow

    init {
        externalScope.launch {
            while(true) {
                _tickFlow.emit(Unit)
                delay(tickIntervalMs)
            }
        }
    }
}

class NewsRepository(
    private val tickHandler: TickHandler,
    private val externalScope: CoroutineScope
) {
    init {
        externalScope.launch {
            // Listen for tick updates
            tickHandler.tickFlow.collect {
                refreshLatestNews()
            }
        }
    }

    suspend fun refreshLatestNews() { /* ... */ }
}
```

### StateFlow vs SharedFlow Comparison

| Feature | StateFlow | SharedFlow |
|---------|-----------|------------|
| **Initial value** | Required | Optional |
| **Always has value** | Yes | No |
| **Use case** | UI state | Events/signals |
| **Conflation** | Yes (always) | Configurable |
| **Replay** | 1 (always) | Configurable (0...∞) |
| **subscriptionCount** | Available | Available |

### When to Use Each

**Use StateFlow when**:
- You need to represent current state (e.g., UI state, loading state)
- You want automatic conflation of values
- New subscribers should immediately receive the latest value
- You're migrating from LiveData

**Use SharedFlow when**:
- You need to represent events (e.g., navigation events, one-time messages)
- You need configurable replay behavior
- You want to broadcast to multiple collectors
- You need control over buffer overflow behavior

### Example: Counter with StateFlow

```kotlin
class CounterModel {
    private val _counter = MutableStateFlow(0) // private mutable state flow
    val counter = _counter.asStateFlow() // publicly exposed as read-only state flow

    fun inc() {
        _counter.value++
    }
}

// Usage
val aModel = CounterModel()
val bModel = CounterModel()
val sumFlow: Flow<Int> = aModel.counter.combine(bModel.counter) { a, b -> a + b }
```

### Additional MutableSharedFlow Features

```kotlin
val sharedFlow = MutableSharedFlow<String>(replay = 3)

// Check number of active collectors
val collectorCount: Int = sharedFlow.subscriptionCount.value

// Reset replay cache if needed
sharedFlow.resetReplayCache()
```

**English Summary**: StateFlow is a state-holder hot flow that always has a current value and conflates updates. SharedFlow is a more general hot flow for broadcasting events with configurable replay and buffer behavior. Use StateFlow for UI state, SharedFlow for events.

## Ответ (RU)

`StateFlow` и `SharedFlow` — это API для Flow, которые позволяют эффективно передавать обновления состояния и значения нескольким подписчикам. Это **горячие потоки** (hot flows), то есть они активны и могут испускать значения даже без подписчиков.

### StateFlow

`StateFlow` — это наблюдаемый поток-держатель состояния, который испускает текущее состояние и новые обновления состояния своим подписчикам. Текущее значение состояния также доступно через свойство `value`.

#### Ключевые характеристики

1. **Всегда имеет значение** - Требует начальное состояние при создании
2. **Держатель состояния** - Всегда представляет текущее состояние
3. **Объединяет значения** - Испускает только отличающиеся значения, пропускает дубликаты
4. **Горячий поток** - Активен и в памяти даже без подписчиков
5. **Потокобезопасный** - Можно безопасно обновлять из любого потока

#### Пример использования

```kotlin
class LatestNewsViewModel(
    private val newsRepository: NewsRepository
) : ViewModel() {
    // Приватное свойство для предотвращения обновлений извне
    private val _uiState = MutableStateFlow(LatestNewsUiState.Success(emptyList()))
    // UI подписывается на этот StateFlow для получения обновлений состояния
    val uiState: StateFlow<LatestNewsUiState> = _uiState

    init {
        viewModelScope.launch {
            newsRepository.favoriteLatestNews
                // Обновляем View последними избранными новостями
                .collect { favoriteNews ->
                    _uiState.value = LatestNewsUiState.Success(favoriteNews)
                }
        }
    }
}

// Представляет разные состояния экрана LatestNews
sealed class LatestNewsUiState {
    data class Success(val news: List<ArticleHeadline>): LatestNewsUiState()
    data class Error(val exception: Throwable): LatestNewsUiState()
}
```

#### StateFlow vs LiveData

| Функция | StateFlow | LiveData |
|---------|-----------|----------|
| **Начальное значение** | Обязательно | Необязательно |
| **Lifecycle awareness** | Вручную (collect в lifecycle scope) | Автоматически (observe) |
| **Потокобезопасность** | Встроенная | Встроенная |
| **Трансформации** | Flow операторы | LiveData трансформации |

**Ключевое отличие**: `LiveData.observe()` автоматически отписывается когда view переходит в состояние STOPPED, тогда как сбор из StateFlow не останавливается автоматически - нужно собирать в lifecycle-aware scope.

### SharedFlow

`SharedFlow` — это горячий поток, который испускает значения всем подписчикам. Это высоко настраиваемое обобщение StateFlow.

#### Опции конфигурации

```kotlin
private val _tickFlow = MutableSharedFlow<Unit>(
    replay = 0,                          // Сколько значений повторить новым подписчикам
    extraBufferCapacity = 0,             // Дополнительный буфер сверх replay
    onBufferOverflow = BufferOverflow.SUSPEND  // Что делать при переполнении буфера
)
```

**Варианты BufferOverflow**:
- `SUSPEND` (по умолчанию) - Приостанавливает вызывающего при переполнении
- `DROP_LATEST` - Отбрасывает последнее значение при переполнении
- `DROP_OLDEST` - Отбрасывает самое старое значение при переполнении

### Сравнение StateFlow vs SharedFlow

| Функция | StateFlow | SharedFlow |
|---------|-----------|------------|
| **Начальное значение** | Обязательно | Опционально |
| **Всегда имеет значение** | Да | Нет |
| **Случай использования** | UI состояние | События/сигналы |
| **Объединение** | Да (всегда) | Настраиваемое |
| **Повтор** | 1 (всегда) | Настраиваемый (0...∞) |

### Когда что использовать

**Используйте StateFlow когда**:
- Нужно представить текущее состояние (например, UI состояние, состояние загрузки)
- Нужно автоматическое объединение значений
- Новые подписчики должны сразу получить последнее значение
- Мигрируете с LiveData

**Используйте SharedFlow когда**:
- Нужно представить события (например, навигационные события, одноразовые сообщения)
- Нужно настраиваемое поведение повтора
- Нужно транслировать нескольким подписчикам
- Нужен контроль над переполнением буфера

**Краткое содержание**: StateFlow — это горячий поток-держатель состояния с обязательным текущим значением и объединением обновлений. SharedFlow — более общий горячий поток для трансляции событий с настраиваемым повтором и буферизацией. Используйте StateFlow для UI состояния, SharedFlow для событий.

---

## References
- [StateFlow and SharedFlow - Android Developers](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)
- [Flow - Kotlin Documentation](https://kotlinlang.org/docs/reference/coroutines/flow.html)
- [Introducing StateFlow and SharedFlow - JetBrains Blog](https://blog.jetbrains.com/kotlin/2020/10/kotlinx-coroutines-1-4-0-introducing-stateflow-and-sharedflow/)

## Related Questions

### Related (Medium)
- [[q-testing-stateflow-sharedflow--kotlin--medium]] - Coroutines
- [[q-stateflow-sharedflow-android--kotlin--medium]] - Coroutines
- [[q-sharedflow-stateflow--kotlin--medium]] - Flow
- [[q-sharedflow-replay-buffer-config--kotlin--medium]] - Coroutines

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

