---
anki_cards:
- slug: q-hot-vs-cold-flows--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-hot-vs-cold-flows--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---\
id: lang-016
title: "Hot Vs Cold Flows / Горячие и холодные потоки"
aliases: [Hot Vs Cold Flows, Горячие и холодные потоки]
topic: kotlin
subtopics: [coroutines, flow, reactive-programming]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-flow, c-kotlin]
created: 2025-10-15
updated: 2025-11-09
tags: [coroutines, difficulty/medium, flow, kotlin, reactive]
---\
# Вопрос (RU)
> В чем разница между Hot и Cold Flows?

---

# Question (EN)
> What is the difference between Hot and Cold Flows?

## Ответ (RU)

Холодные потоки (cold) начинают генерировать данные только после подписки (ленивые) — выполнение запускается для каждого нового коллектора.
Примеры: `Flow` (`kotlinx.coroutines.flow.Flow`).

Горячие потоки (hot) существуют независимо от подписчиков — источник данных активен в своем жизненном цикле и эмитит значения независимо от того, есть ли текущие коллекторы.
Примеры: `SharedFlow`, `StateFlow`, `LiveData`, широковещательные источники (Broadcast-like).

### Характеристики Холодных Потоков

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Cold Flow: Starts only when collected
fun coldFlowExample(): Flow<Int> = flow {
    println("Flow started")  // Печатается при вызове collect()
    repeat(3) { i ->
        delay(100)
        emit(i)
    }
}

fun main() = runBlocking {
    val coldFlow = coldFlowExample()
    println("Flow created")

    delay(1000)
    println("Starting collection")

    coldFlow.collect { value ->
        println("Received: $value")
    }
}

// Возможный вывод:
// Flow created
// (1 second delay)
// Starting collection
// Flow started  <- Запуск только в момент collect()
// Received: 0
// Received: 1
// Received: 2
```

### Характеристики Горячих Потоков

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Hot Flow: Producer emits regardless of current subscribers
fun hotFlowExample() = runBlocking {
    val hotFlow = MutableSharedFlow<Int>() // replay = 0 по умолчанию

    // Начинаем эмитить (подписчиков еще нет)
    launch {
        repeat(5) { i ->
            println("Emitting $i")
            hotFlow.emit(i)
            delay(100)
        }
    }

    delay(250)  // Ждем перед подпиской

    // Поздний подписчик — пропускает значения до момента подписки
    launch {
        hotFlow.collect { value ->
            println("Subscriber 1: $value")
        }
    }

    delay(500)
}

// Возможный результат при replay = 0 (зависит от планировщика и таймингов):
// Emitting 0  <- До появления подписчика
// Emitting 1  <- До появления подписчика
// Emitting 2
// Subscriber 1: 2  <- Поздний подписчик получает первое значение после своей подписки
// Emitting 3
// Subscriber 1: 3
// Emitting 4
// Subscriber 1: 4
```

### Холодный Поток — Отдельное Выполнение На Коллектора

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun multipleColdCollectors() = runBlocking {
    val coldFlow = flow {
        println("Flow started for ${'$'}{Thread.currentThread().name}")
        repeat(3) { emit(it) }
    }

    // Коллектор 1
    launch {
        coldFlow.collect { println("Collector 1: ${'$'}it") }
    }

    // Коллектор 2
    launch {
        coldFlow.collect { println("Collector 2: ${'$'}it") }
    }
}

// Возможный вывод (порядок зависит от планировщика):
// Flow started for ...  <- Запуск для коллектора 1
// Collector 1: 0
// Flow started for ...  <- Отдельный запуск для коллектора 2
// Collector 1: 1
// Collector 2: 0
// ...
// Каждый коллектор получает независимое выполнение upstream-а
```

### Горячий Поток — Общее Выполнение

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun multipleHotCollectors() = runBlocking {
    val hotFlow = MutableSharedFlow<Int>() // replay = 0

    // Один общий источник эмиссий
    launch {
        repeat(5) { i ->
            hotFlow.emit(i)
            delay(100)
        }
    }

    // Коллектор 1 подписывается сразу
    launch {
        hotFlow.collect { println("Collector 1: ${'$'}it") }
    }

    delay(150)

    // Коллектор 2 подписывается позже и видит только последующие значения
    launch {
        hotFlow.collect { println("Collector 2: ${'$'}it") }
    }

    delay(500)
}

// Возможный результат при replay = 0 (зависит от таймингов):
// Collector 1: 0
// Collector 1: 1
// Collector 2: 2  <- Поздний подписчик не видит 0 и 1
// Collector 1: 2
// Collector 1: 3
// Collector 2: 3
// Collector 1: 4
// Collector 2: 4
// Один продюсер, несколько коллекторов разделяют его эмиссии; поздние подписчики пропускают прошлые значения без replay
```

### Конвертация Холодного Потока В Горячий

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// shareIn: превращает холодный upstream в разделяемый горячий поток
fun coldToHot() = runBlocking {
    val coldFlow = flow {
        println("Flow started")
        repeat(5) { i ->
            delay(100)
            emit(i)
        }
    }

    // Делаем общий горячий поток в данном scope
    val hotFlow = coldFlow.shareIn(
        scope = this,
        started = SharingStarted.Eagerly,
        replay = 0
    )

    delay(250)

    // Подписчик получает значения от уже запущенного общего upstream-а
    hotFlow.collect { println("Received: ${'$'}it") }
}
```

### Использование Горячего Потока (общий источник)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun hotFlowUsage() = runBlocking {
    val sharedFlow = MutableSharedFlow<Int>()

    // Каждый collect подписывается на один и тот же горячий источник
    launch {
        sharedFlow.collect { println("A: ${'$'}it") }
    }

    launch {
        sharedFlow.collect { println("B: ${'$'}it") }
    }

    // Оба коллектора получают одни и те же значения
    sharedFlow.emit(1)
    sharedFlow.emit(2)
}
```

### StateFlow — Горячий Поток С Состоянием

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun stateFlowExample() = runBlocking {
    val stateFlow = MutableStateFlow(0)

    // `StateFlow` горячий — всегда имеет текущее значение в своем scope
    println("Initial value: ${'$'}{stateFlow.value}")  // 0

    // Продюсер, обновляющий состояние
    launch {
        repeat(5) { i ->
            delay(100)
            stateFlow.value = i + 1
        }
    }

    delay(250)

    // Поздний подписчик сразу получает актуальное значение и дальнейшие обновления
    launch {
        stateFlow.collect { println("Subscriber: ${'$'}it") }
    }

    delay(500)
}

// Возможный результат (зависит от таймингов):
// Initial value: 0
// Subscriber: 3  <- Поздний подписчик сразу получает текущее значение на момент подписки
// Subscriber: 4
// Subscriber: 5
```

### Практические Примеры

```kotlin
// Cold Flow: API вызовы (каждый collect запускает свой запрос)
class Repository(private val api: Api) {
    fun getUsers(): Flow<List<User>> = flow {
        val users = api.fetchUsers()  // Новый запрос на каждый collect()
        emit(users)
    }
}

// Hot Flow: обновления локации (один источник, несколько наблюдателей)
class LocationService(private val locationProvider: LocationProvider) {
    private val _location = MutableSharedFlow<Location>(replay = 0)
    val location: SharedFlow<Location> = _location

    init {
        // Запуск обновлений независимо от наличия подписчиков
        locationProvider.startUpdates { newLocation ->
            _location.tryEmit(newLocation)
        }
    }
}

// StateFlow: состояние UI (всегда отдает последнее состояние)
class ViewModel {
    private val _uiState = MutableStateFlow(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState

    // Поздние подписчики сразу получают текущее состояние
}
```

### Сводная Таблица

| Характеристика | Холодный поток | Горячий поток |
|----------------|----------------|---------------|
| Старт | Запускается при collect (ленивый) | Продюсер активен по своему жизненному циклу, не на collect |
| Выполнение | Новое выполнение для каждого коллектора | Общее выполнение для всех коллектора |
| Поздние подписчики | Получают значения с момента начала своего collect | Могут пропускать прошлые значения (если нет replay/буфера) |
| Примеры | `Flow` | `SharedFlow`, `StateFlow`, `LiveData` |
| Use case | API-вызовы, преобразования | События, состояние, сенсоры, broadcast-источники |
| Ресурсы | Возможное дублирование работы на коллектора | Один продюсер переиспользуется коллекторами |

## Answer (EN)

Cold flows start producing data only when they are collected (lazy) — a new execution is started for each collector.
Examples: `Flow` (`kotlinx.coroutines.flow.Flow`).

Hot flows have an active producer that exists independently of individual subscribers — emissions are driven by the producer's lifecycle, not by each collector.
Examples: `SharedFlow`, `StateFlow`, `LiveData`, broadcast-like sources.

### Cold Flow Characteristics

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Cold Flow: Starts only when collected
fun coldFlowExample(): Flow<Int> = flow {
    println("Flow started")  // Printed when collect() is called
    repeat(3) { i ->
        delay(100)
        emit(i)
    }
}

fun main() = runBlocking {
    val coldFlow = coldFlowExample()
    println("Flow created")

    delay(1000)
    println("Starting collection")

    coldFlow.collect { value ->
        println("Received: $value")
    }
}

// Possible output:
// Flow created
// (1 second delay)
// Starting collection
// Flow started  <- Only starts when collect() is called
// Received: 0
// Received: 1
// Received: 2
```

### Hot Flow Characteristics

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Hot Flow: Producer emits regardless of current subscribers
fun hotFlowExample() = runBlocking {
    val hotFlow = MutableSharedFlow<Int>() // replay = 0 by default

    // Start emitting (no subscribers yet)
    launch {
        repeat(5) { i ->
            println("Emitting $i")
            hotFlow.emit(i)
            delay(100)
        }
    }

    delay(250)  // Wait before subscribing

    // Subscribe late - will miss values emitted before subscription
    launch {
        hotFlow.collect { value ->
            println("Subscriber 1: $value")
        }
    }

    delay(500)
}

// Possible outcome with replay = 0 (timing-dependent):
// Emitting 0  <- Emitted before any subscriber
// Emitting 1  <- Emitted before any subscriber
// Emitting 2
// Subscriber 1: 2  <- Late subscriber starts from the first emission after subscription
// Emitting 3
// Subscriber 1: 3
// Emitting 4
// Subscriber 1: 4
```

### Cold Flow - Each Collector Gets Own Execution

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun multipleColdCollectors() = runBlocking {
    val coldFlow = flow {
        println("Flow started for ${'$'}{Thread.currentThread().name}")
        repeat(3) { emit(it) }
    }

    // Collector 1
    launch {
        coldFlow.collect { println("Collector 1: ${'$'}it") }
    }

    // Collector 2
    launch {
        coldFlow.collect { println("Collector 2: ${'$'}it") }
    }
}

// Possible output (order depends on scheduling):
// Flow started for ...  <- Started for collector 1
// Collector 1: 0
// Flow started for ...  <- Started again for collector 2
// Collector 1: 1
// Collector 2: 0
// ...
// (Each collector gets an independent execution of the upstream)
```

### Hot Flow - Shared Execution

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun multipleHotCollectors() = runBlocking {
    val hotFlow = MutableSharedFlow<Int>() // replay = 0

    // Start emitting from a single shared source
    launch {
        repeat(5) { i ->
            hotFlow.emit(i)
            delay(100)
        }
    }

    // Collector 1 subscribes immediately
    launch {
        hotFlow.collect { println("Collector 1: ${'$'}it") }
    }

    delay(150)

    // Collector 2 joins later; will only see emissions from this point on
    launch {
        hotFlow.collect { println("Collector 2: ${'$'}it") }
    }

    delay(500)
}

// Possible outcome with replay = 0 (timing-dependent):
// Collector 1: 0
// Collector 1: 1
// Collector 2: 2  <- Joins later; does not receive 0 or 1
// Collector 1: 2
// Collector 1: 3
// Collector 2: 3
// Collector 1: 4
// Collector 2: 4
// (A single producer; multiple collectors share its emissions, late collectors miss past values without replay)
```

### Converting Cold to Hot

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// shareIn: Convert a cold upstream into a shared hot flow
fun coldToHot() = runBlocking {
    val coldFlow = flow {
        println("Flow started")
        repeat(5) { i ->
            delay(100)
            emit(i)
        }
    }

    // Convert to hot shared flow in this scope
    val hotFlow = coldFlow.shareIn(
        scope = this,
        started = SharingStarted.Eagerly,
        replay = 0
    )

    delay(250)

    // Subscriber gets values from the already running shared upstream
    hotFlow.collect { println("Received: ${'$'}it") }
}
```

### Hot Flow Usage (Shared Source)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun hotFlowUsage() = runBlocking {
    val sharedFlow = MutableSharedFlow<Int>()

    // Each collect call subscribes to the same hot shared source
    launch {
        sharedFlow.collect { println("A: ${'$'}it") }
    }

    launch {
        sharedFlow.collect { println("B: ${'$'}it") }
    }

    // Both collectors receive the same emitted values from the shared source
    sharedFlow.emit(1)
    sharedFlow.emit(2)
}
```

### StateFlow - Hot Flow with State

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun stateFlowExample() = runBlocking {
    val stateFlow = MutableStateFlow(0)

    // `StateFlow` is hot - it always has a value and is active within its scope
    println("Initial value: ${'$'}{stateFlow.value}")  // 0

    // Start updating in a producer coroutine
    launch {
        repeat(5) { i ->
            delay(100)
            stateFlow.value = i + 1
        }
    }

    delay(250)

    // Late subscriber gets the current value immediately, then subsequent updates
    launch {
        stateFlow.collect { println("Subscriber: ${'$'}it") }
    }

    delay(500)
}

// Possible outcome (timing-dependent):
// Initial value: 0
// Subscriber: 3  <- Late subscriber immediately gets current value at time of subscription
// Subscriber: 4
// Subscriber: 5
```

### Real-World Examples

```kotlin
// Cold Flow: API calls (each collector triggers its own request)
class Repository(private val api: Api) {
    fun getUsers(): Flow<List<User>> = flow {
        val users = api.fetchUsers()  // New request for each collect()
        emit(users)
    }
}

// Hot Flow: Location updates (single source, multiple observers sharing updates)
class LocationService(private val locationProvider: LocationProvider) {
    private val _location = MutableSharedFlow<Location>(replay = 0)
    val location: SharedFlow<Location> = _location

    init {
        // Start receiving and emitting updates independently of collectors
        locationProvider.startUpdates { newLocation ->
            _location.tryEmit(newLocation)
        }
    }
}

// StateFlow: UI state (always exposes the latest state to collectors)
class ViewModel {
    private val _uiState = MutableStateFlow(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState

    // Late subscribers immediately receive the current state
}
```

### Summary Table

| Feature | Cold `Flow` | Hot `Flow` |
|---------|-----------|----------|
| Start behavior | Starts on collection (lazy) | Producer active based on its own scope/lifecycle, not per collector |
| Execution | New execution per collector | Shared execution for all collectors |
| Late subscribers | Receive values from the moment their collection starts | May miss values emitted before subscription (unless replay/buffering is used) |
| Examples | `Flow` | `SharedFlow`, `StateFlow`, `LiveData` |
| Use case | API calls, transformations | Events, state, sensors, broadcasts |
| Resource usage | Potentially repeated work per collector | Single producer reused across collectors |

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия по сравнению с Java-подходами к реактивности?
- Когда на практике стоит использовать `hot` vs `cold` потоки?
- Каковы типичные ошибки при работе с hot/cold потоками?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [[c-flow]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## References

- [[c-kotlin]]
- [[c-flow]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-how-suspend-function-detects-suspension--kotlin--hard]]
- [[q-inheritance-vs-composition--cs--medium]]
## Related Questions

- [[q-how-suspend-function-detects-suspension--kotlin--hard]]
- [[q-inheritance-vs-composition--cs--medium]]
