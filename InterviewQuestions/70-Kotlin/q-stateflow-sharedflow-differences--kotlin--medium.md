---
anki_cards:
- slug: q-stateflow-sharedflow-differences--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-stateflow-sharedflow-differences--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
# Question (EN)
> What are `StateFlow` and `SharedFlow` in Kotlin? What are the differences between them?

## Ответ (RU)

`StateFlow` и `SharedFlow` — это API для `Flow`, которые позволяют эффективно передавать обновления состояния и значения нескольким подписчикам. Это **горячие потоки** (hot flows), то есть они существуют независимо от подписчиков и могут принимать/испускать значения, даже когда подписчиков нет (с учётом конфигурации буфера и возможной приостановки эмиттера). См. также [[c-concurrency]].

### StateFlow

`StateFlow` — это наблюдаемый поток-держатель состояния, который испускает текущее состояние и новые обновления состояния своим подписчикам. Текущее значение состояния также доступно через свойство `value`.

#### Ключевые Характеристики

1. **Всегда имеет значение** — требуется начальное состояние при создании.
2. **Держатель состояния** — всегда представляет актуальное состояние.
3. **Объединяет значения** — испускает только отличающиеся подряд значения (поведение аналогично `distinctUntilChanged`).
4. **Горячий поток** — активен независимо от наличия подписчиков.
5. **Потокобезопасный** — можно безопасно обновлять из любого потока.

#### Пример Использования

```kotlin
class LatestNewsViewModel(
    private val newsRepository: NewsRepository
) : ViewModel() {
    // Приватное свойство для предотвращения обновлений извне
    private val _uiState = MutableStateFlow(LatestNewsUiState.Success(emptyList()))
    // UI подписывается на этот `StateFlow` для получения обновлений состояния
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

#### StateFlow Vs `LiveData`

| Функция | `StateFlow` | `LiveData` |
|---------|------------|-----------|
| **Начальное значение** | Обязательно | Необязательно |
| **`Lifecycle` awareness** | Нет, нужно собирать в lifecycle scope вручную | Да, автоматическое управление подпиской |
| **Потокобезопасность** | Встроенная | Встроенная |
| **Трансформации** | Операторы `Flow` | Трансформации `LiveData` |

**Ключевое отличие**: `LiveData.observe()` автоматически отписывается, когда `LifecycleOwner` переходит в состояние ниже STARTED, тогда как сбор из `StateFlow` сам по себе не останавливается — нужно собирать его в lifecycle-aware scope (например, `lifecycleScope.launch { repeatOnLifecycle(STARTED) { ... } }`).

### SharedFlow

`SharedFlow` — это горячий поток, который испускает значения всем подписчикам. Это высоко настраиваемое обобщение `StateFlow` (сам `StateFlow` реализован поверх `SharedFlow`). Значения `SharedFlow` могут производиться из разных источников, включая `MutableSharedFlow`, `shareIn` и `stateIn`.

#### Ключевые Характеристики

1. **Начальное значение не требуется** — может быть создан без стартового значения.
2. **Широковещательная рассылка нескольким коллекторам** — все активные коллектора получают одинаковые эмиссии.
3. **Настраиваемый кэш replay** — можно повторять N предыдущих значений новым коллекторам.
4. **Настраиваемый буфер** — управление переполнением через `replay`, `extraBufferCapacity` и `onBufferOverflow`.
5. **Гибкая семантика** — может представлять события, общие потоки или даже состояние при соответствующей конфигурации.

#### Опции Конфигурации

```kotlin
private val _tickFlow = MutableSharedFlow<Unit>(
    replay = 0,                          // Сколько значений повторить новым подписчикам
    extraBufferCapacity = 0,             // Дополнительный буфер сверх replay
    onBufferOverflow = BufferOverflow.SUSPEND  // Что делать при переполнении буфера
)
```

**Варианты BufferOverflow**:
- `SUSPEND` (по умолчанию) — приостанавливает вызывающего при переполнении.
- `DROP_LATEST` — отбрасывает последнее новое значение при переполнении.
- `DROP_OLDEST` — отбрасывает самое старое значение при переполнении.

#### Пример Использования

```kotlin
// Класс, который централизует моменты, когда нужно обновить контент приложения
class TickHandler(
    private val externalScope: CoroutineScope,
    private val tickIntervalMs: Long = 5000
) {
    // Приватное свойство для предотвращения внешних эмиссий
    private val _tickFlow = MutableSharedFlow<Unit>(replay = 0)
    val tickFlow: SharedFlow<Unit> = _tickFlow

    init {
        externalScope.launch {
            while (true) {
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
            // Слушаем "тики" для обновления новостей
            tickHandler.tickFlow.collect {
                refreshLatestNews()
            }
        }
    }

    suspend fun refreshLatestNews() { /* ... */ }
}
```

### Сравнение `StateFlow` Vs `SharedFlow`

| Функция | `StateFlow` | `SharedFlow` |
|---------|------------|-------------|
| **Начальное значение** | Обязательно | Опционально |
| **Всегда имеет значение** | Да | Нет |
| **Случай использования** | UI-состояние / держатель состояния | События/сигналы, общие потоки событий или настраиваемое общее состояние |
| **Объединение** | Да (для подряд идущих одинаковых значений) | Настраивается через буфер/replay и логику эмиссий |
| **Повтор (replay)** | 1 (последнее значение) | Настраиваемый (0...∞) |
| **subscriptionCount** | Доступен | Доступен |

### Когда Что Использовать

**Используйте `StateFlow`, когда**:
- Нужно представить текущее состояние (например, UI-состояние, состояние загрузки).
- Нужна автоматическая конденсация подряд идущих одинаковых значений.
- Новые подписчики должны сразу получать последнее значение.
- Мигрируете с `LiveData`.

**Используйте `SharedFlow`, когда**:
- Нужно представить события (например, навигационные события, одноразовые сообщения).
- Нужен настраиваемый `replay`.
- Нужно транслировать значения нескольким коллекторам.
- Нужен контроль над переполнением буфера или более гибкие неконфлюирующие семантики.

### Пример: Счетчик С Использованием `StateFlow`

```kotlin
class CounterModel {
    private val _counter = MutableStateFlow(0) // приватный изменяемый `StateFlow`
    val counter = _counter.asStateFlow() // публично только для чтения

    fun inc() {
        _counter.value++
    }
}

// Использование
val aModel = CounterModel()
val bModel = CounterModel()
val sumFlow: Flow<Int> = aModel.counter.combine(bModel.counter) { a, b -> a + b }
```

### Дополнительные Возможности `MutableSharedFlow`

```kotlin
val sharedFlow = MutableSharedFlow<String>(replay = 3)

// Количество активных коллекторов
val collectorCount: Int = sharedFlow.subscriptionCount.value

// Сбросить кэш replay при необходимости
sharedFlow.resetReplayCache()
```

**Краткое резюме (RU)**: `StateFlow` — это горячий поток-держатель состояния с обязательным текущим значением и объединением подряд идущих одинаковых обновлений. `SharedFlow` — более общий горячий поток для трансляции состояний и/или событий с настраиваемым `replay` и буферизацией. Используйте `StateFlow` для UI-состояния, `SharedFlow` — для событий и широковещательных сценариев.

## Answer (EN)

`StateFlow` and `SharedFlow` are `Flow` APIs that enable flows to efficiently emit state updates and values to multiple collectors. They are **hot flows**, meaning they exist independently of collectors and can be emitted to even when there are no active collectors (subject to buffer configuration and possible suspension of emitters). See also [[c-concurrency]].

### StateFlow

`StateFlow` is a state-holder observable flow that emits the current and new state updates to its collectors. The current state value can also be read through its `value` property.

#### Key Characteristics

1. **Always has a value** - Requires an initial state value when created.
2. **State holder** - Always represents the latest state.
3. **Conflates values** - Only emits distinct consecutive values (behavior similar to `distinctUntilChanged`).
4. **Hot flow** - Active regardless of the presence of collectors.
5. **`Thread`-safe** - Can be safely updated from any thread.

#### Example Usage

```kotlin
class LatestNewsViewModel(
    private val newsRepository: NewsRepository
) : ViewModel() {
    // Backing property to avoid state updates from other classes
    private val _uiState = MutableStateFlow(LatestNewsUiState.Success(emptyList()))
    // The UI collects from this `StateFlow` to get its state updates
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

#### `StateFlow` Vs `LiveData`

Both are observable data holder classes with similar patterns:

| Feature | `StateFlow` | `LiveData` |
|---------|------------|-----------|
| **Initial value** | Required | Not required |
| **`Lifecycle` awareness** | Not lifecycle-aware by itself; must collect in lifecycle-aware scope | Built-in lifecycle awareness |
| **`Thread` safety** | Built-in | Built-in |
| **Transformation** | `Flow` operators | `LiveData` transformations |

**Key Difference**: `LiveData.observe()` automatically unregisters when the `LifecycleOwner` goes below the STARTED state, whereas collecting from `StateFlow` does not stop automatically — you must collect it in a lifecycle-aware scope such as `lifecycleScope.launch { repeatOnLifecycle(STARTED) { ... } }`.

### SharedFlow

`SharedFlow` is a hot flow that emits values to all collectors. It is a highly-configurable generalization of `StateFlow` (and `StateFlow` is implemented on top of `SharedFlow`). `SharedFlow` values can be produced by many sources, including `MutableSharedFlow`, `shareIn`, and `stateIn`.

#### Key Characteristics

1. **No initial value required** - Can start without any value.
2. **Broadcasts to multiple collectors** - All active collectors receive the same emissions.
3. **Configurable replay cache** - Can replay N previous values to new collectors.
4. **Configurable buffer** - Control overflow behavior via `replay`, `extraBufferCapacity`, and `onBufferOverflow`.
5. **Flexible semantics** - Can represent events, shared streams, or even state when configured appropriately.

#### Configuration Options

```kotlin
private val _tickFlow = MutableSharedFlow<Unit>(
    replay = 0,                          // How many values to replay to new collectors
    extraBufferCapacity = 0,             // Extra buffer beyond replay
    onBufferOverflow = BufferOverflow.SUSPEND  // What to do when buffer is full
)
```

**BufferOverflow Options**:
- `SUSPEND` (default) - Suspends the caller when buffer is full.
- `DROP_LATEST` - Drops the latest new value when buffer is full.
- `DROP_OLDEST` - Drops the oldest value when buffer is full.

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
            while (true) {
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

### `StateFlow` Vs `SharedFlow` Comparison

| Feature | `StateFlow` | `SharedFlow` |
|---------|------------|------------|
| **Initial value** | Required | Optional |
| **Always has value** | Yes | No |
| **Use case** | UI state / state holder | Events/signals, shared event streams, or configurable shared state |
| **Conflation** | Yes (for consecutive equal values) | Configurable via buffer/replay setup and emission logic |
| **Replay** | 1 (last value) | Configurable (0...∞) |
| **subscriptionCount** | Available | Available |

### When to Use Each

**Use `StateFlow` when**:
- You need to represent current state (e.g., UI state, loading state).
- You want automatic conflation of consecutive equal values.
- New subscribers should immediately receive the latest value.
- You're migrating from `LiveData`.

**Use `SharedFlow` when**:
- You need to represent events (e.g., navigation events, one-time messages).
- You need configurable replay behavior.
- You want to broadcast to multiple collectors.
- You need control over buffer overflow behavior or non-conflated semantics.

### Example: Counter with `StateFlow`

```kotlin
class CounterModel {
    private val _counter = MutableStateFlow(0) // private mutable `StateFlow`
    val counter = _counter.asStateFlow() // publicly exposed as read-only `StateFlow`

    fun inc() {
        _counter.value++
    }
}

// Usage
val aModel = CounterModel()
val bModel = CounterModel()
val sumFlow: Flow<Int> = aModel.counter.combine(bModel.counter) { a, b -> a + b }
```

### Additional `MutableSharedFlow` Features

```kotlin
val sharedFlow = MutableSharedFlow<String>(replay = 3)

// Check number of active collectors
val collectorCount: Int = sharedFlow.subscriptionCount.value

// Reset replay cache if needed
sharedFlow.resetReplayCache()
```

**English Summary**: `StateFlow` is a state-holder hot flow that always has a current value and conflates consecutive equal updates. `SharedFlow` is a more general hot flow for broadcasting events or shared streams with configurable replay and buffer behavior. Use `StateFlow` for UI state, `SharedFlow` for events and broadcast-style sharing.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [`StateFlow` and `SharedFlow` - Android Developers](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)
- [`Flow` - Kotlin Documentation](https://kotlinlang.org/docs/reference/coroutines/flow.html)
- [Introducing `StateFlow` and `SharedFlow` - JetBrains Blog](https://blog.jetbrains.com/kotlin/2020/10/kotlinx-coroutines-1-4-0-introducing-stateflow-and-sharedflow/)

## Related Questions

### Related (Medium)
- [[q-testing-stateflow-sharedflow--kotlin--medium]] - Coroutines
- [[q-stateflow-sharedflow-android--kotlin--medium]] - Coroutines
- [[q-sharedflow-stateflow--kotlin--medium]] - `Flow`
- [[q-sharedflow-replay-buffer-config--kotlin--medium]] - Coroutines

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive `Flow` introduction