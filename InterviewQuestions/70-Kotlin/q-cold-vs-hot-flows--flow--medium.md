---
id: kotlin-flow-002
title: Cold vs Hot Flows / Холодные и горячие Flow
aliases:
- Cold vs Hot Flows
- Cold Flow Hot Flow
- Холодные горячие потоки
topic: kotlin
subtopics:
- coroutines
- flow
question_kind: comparison
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
- q-stateflow-vs-sharedflow--flow--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- coroutines
- difficulty/medium
- flow
- kotlin
anki_cards:
- slug: kotlin-flow-002-0-en
  language: en
  anki_id: 1769344141365
  synced_at: '2026-01-25T16:29:01.417019'
- slug: kotlin-flow-002-0-ru
  language: ru
  anki_id: 1769344141415
  synced_at: '2026-01-25T16:29:01.420038'
---
# Vopros (RU)
> Чем отличаются холодные и горячие Flow? Приведите примеры каждого типа.

---

# Question (EN)
> What is the difference between cold and hot flows? Give examples of each type.

## Otvet (RU)

### Холодные Flow

**Холодный Flow** начинает выполнение только при появлении подписчика (collector). Каждый подписчик получает свою независимую последовательность значений.

```kotlin
// Холодный Flow - создается через flow { } builder
val coldFlow = flow {
    println("Flow started")
    emit(1)
    delay(100)
    emit(2)
    delay(100)
    emit(3)
}

// Первый подписчик
launch {
    coldFlow.collect { println("Collector 1: $it") }
}
// Flow started
// Collector 1: 1
// Collector 1: 2
// Collector 1: 3

// Второй подписчик - получает ВСЕ значения заново
launch {
    coldFlow.collect { println("Collector 2: $it") }
}
// Flow started  <-- блок выполняется заново!
// Collector 2: 1
// Collector 2: 2
// Collector 2: 3
```

**Характеристики холодного Flow:**
- Ленивый: не производит значения без `collect()`
- Per-collector: каждый подписчик запускает выполнение заново
- Значения вычисляются по требованию
- Примеры: `flow { }`, `flowOf()`, `.asFlow()`, Room DAO flows

```kotlin
// Примеры холодных Flow
val flow1 = flowOf(1, 2, 3)
val flow2 = listOf(1, 2, 3).asFlow()
val flow3 = (1..10).asFlow()

// Room DAO - холодный Flow
@Query("SELECT * FROM users")
fun getAllUsers(): Flow<List<User>>
```

### Горячие Flow

**Горячий Flow** производит значения независимо от наличия подписчиков. Подписчики получают только те значения, которые были эмитированы после подписки (плюс replay cache, если настроен).

```kotlin
// SharedFlow - горячий
val sharedFlow = MutableSharedFlow<Int>()

// StateFlow - горячий
val stateFlow = MutableStateFlow(0)

// Эмиссия происходит независимо от подписчиков
launch {
    repeat(5) {
        sharedFlow.emit(it)
        delay(100)
    }
}

// Подписчик подключается позже
delay(250)
sharedFlow.collect { println("Received: $it") }
// Received: 3  <-- пропустил 0, 1, 2
// Received: 4
```

**Характеристики горячего Flow:**
- Активный: производит значения независимо от подписчиков
- Shared: все подписчики получают одни и те же значения
- Состояние существует независимо от коллекции
- Примеры: `StateFlow`, `SharedFlow`

### Сравнение

| Аспект | Холодный Flow | Горячий Flow |
|--------|---------------|--------------|
| Старт | При `collect()` | Сразу при создании |
| Подписчики | Независимые потоки | Общий поток данных |
| Пропуск значений | Нет | Возможен |
| Жизненный цикл | Привязан к collector | Независимый |
| Память | По требованию | Постоянно хранит состояние |

### Преобразование Cold в Hot

```kotlin
// shareIn - преобразует Flow в SharedFlow
val sharedFlow = coldFlow.shareIn(
    scope = viewModelScope,
    started = SharingStarted.WhileSubscribed(5000),
    replay = 1
)

// stateIn - преобразует Flow в StateFlow
val stateFlow = coldFlow.stateIn(
    scope = viewModelScope,
    started = SharingStarted.WhileSubscribed(5000),
    initialValue = InitialState
)
```

### Стратегии SharingStarted

```kotlin
// Eagerly - запускается сразу
SharingStarted.Eagerly

// Lazily - запускается при первом подписчике, никогда не останавливается
SharingStarted.Lazily

// WhileSubscribed - активен пока есть подписчики
SharingStarted.WhileSubscribed(
    stopTimeoutMillis = 5000,  // Задержка перед остановкой
    replayExpirationMillis = 0 // Когда очищать replay cache
)
```

### Практический Пример

```kotlin
class UserRepository(private val api: UserApi) {
    // Холодный Flow - каждый вызов делает новый запрос
    fun getUser(id: String): Flow<User> = flow {
        emit(api.fetchUser(id))
    }
}

class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    // Преобразование в горячий для UI
    val user: StateFlow<UiState<User>> = repository
        .getUser("123")
        .map { UiState.Success(it) }
        .catch { emit(UiState.Error(it.message)) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = UiState.Loading
        )
}
```

---

## Answer (EN)

### Cold Flows

**Cold Flow** starts execution only when a collector appears. Each collector receives its own independent sequence of values.

```kotlin
// Cold Flow - created via flow { } builder
val coldFlow = flow {
    println("Flow started")
    emit(1)
    delay(100)
    emit(2)
    delay(100)
    emit(3)
}

// First collector
launch {
    coldFlow.collect { println("Collector 1: $it") }
}
// Flow started
// Collector 1: 1
// Collector 1: 2
// Collector 1: 3

// Second collector - receives ALL values from the start
launch {
    coldFlow.collect { println("Collector 2: $it") }
}
// Flow started  <-- block executes again!
// Collector 2: 1
// Collector 2: 2
// Collector 2: 3
```

**Cold Flow characteristics:**
- Lazy: does not produce values without `collect()`
- Per-collector: each subscriber triggers fresh execution
- Values computed on demand
- Examples: `flow { }`, `flowOf()`, `.asFlow()`, Room DAO flows

```kotlin
// Cold Flow examples
val flow1 = flowOf(1, 2, 3)
val flow2 = listOf(1, 2, 3).asFlow()
val flow3 = (1..10).asFlow()

// Room DAO - cold Flow
@Query("SELECT * FROM users")
fun getAllUsers(): Flow<List<User>>
```

### Hot Flows

**Hot Flow** produces values regardless of collectors. Collectors receive only values emitted after subscription (plus replay cache if configured).

```kotlin
// SharedFlow - hot
val sharedFlow = MutableSharedFlow<Int>()

// StateFlow - hot
val stateFlow = MutableStateFlow(0)

// Emission happens regardless of collectors
launch {
    repeat(5) {
        sharedFlow.emit(it)
        delay(100)
    }
}

// Collector joins later
delay(250)
sharedFlow.collect { println("Received: $it") }
// Received: 3  <-- missed 0, 1, 2
// Received: 4
```

**Hot Flow characteristics:**
- Active: produces values regardless of collectors
- Shared: all collectors receive the same values
- State exists independently of collection
- Examples: `StateFlow`, `SharedFlow`

### Comparison

| Aspect | Cold Flow | Hot Flow |
|--------|-----------|----------|
| Start | On `collect()` | Immediately on creation |
| Collectors | Independent streams | Shared stream |
| Value loss | No | Possible |
| Lifecycle | Tied to collector | Independent |
| Memory | On demand | Always holds state |

### Converting Cold to Hot

```kotlin
// shareIn - converts Flow to SharedFlow
val sharedFlow = coldFlow.shareIn(
    scope = viewModelScope,
    started = SharingStarted.WhileSubscribed(5000),
    replay = 1
)

// stateIn - converts Flow to StateFlow
val stateFlow = coldFlow.stateIn(
    scope = viewModelScope,
    started = SharingStarted.WhileSubscribed(5000),
    initialValue = InitialState
)
```

### SharingStarted Strategies

```kotlin
// Eagerly - starts immediately
SharingStarted.Eagerly

// Lazily - starts on first subscriber, never stops
SharingStarted.Lazily

// WhileSubscribed - active while there are subscribers
SharingStarted.WhileSubscribed(
    stopTimeoutMillis = 5000,  // Delay before stopping
    replayExpirationMillis = 0 // When to clear replay cache
)
```

### Practical Example

```kotlin
class UserRepository(private val api: UserApi) {
    // Cold Flow - each call makes a new request
    fun getUser(id: String): Flow<User> = flow {
        emit(api.fetchUser(id))
    }
}

class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    // Convert to hot for UI
    val user: StateFlow<UiState<User>> = repository
        .getUser("123")
        .map { UiState.Success(it) }
        .catch { emit(UiState.Error(it.message)) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = UiState.Loading
        )
}
```

---

## Dopolnitelnye Voprosy (RU)

1. Почему Room DAO возвращает холодный Flow, а не горячий?
2. Как выбрать между `shareIn` и `stateIn`?
3. Что произойдет, если использовать `SharingStarted.Eagerly` в ViewModel?
4. Как избежать повторных запросов при повороте экрана?
5. Можно ли преобразовать горячий Flow обратно в холодный?

---

## Follow-ups

1. Why does Room DAO return a cold Flow instead of a hot one?
2. How to choose between `shareIn` and `stateIn`?
3. What happens if you use `SharingStarted.Eagerly` in a ViewModel?
4. How to avoid repeated requests on screen rotation?
5. Can you convert a hot Flow back to a cold one?

---

## Ssylki (RU)

- [[c-kotlin]]
- [[c-flow]]
- [Kotlin Flow Documentation](https://kotlinlang.org/docs/flow.html)
- [StateIn and ShareIn](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/share-in.html)

---

## References

- [[c-kotlin]]
- [[c-flow]]
- [Kotlin Flow Documentation](https://kotlinlang.org/docs/flow.html)
- [StateIn and ShareIn](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/share-in.html)

---

## Svyazannye Voprosy (RU)

### Sredniy Uroven
- [[q-stateflow-vs-sharedflow--flow--medium]]
- [[q-hot-cold-flows--kotlin--medium]]
- [[q-flow-lifecycle-collection--flow--medium]]

---

## Related Questions

### Related (Medium)
- [[q-stateflow-vs-sharedflow--flow--medium]] - StateFlow vs SharedFlow
- [[q-hot-cold-flows--kotlin--medium]] - Hot and Cold Flows detailed
- [[q-flow-lifecycle-collection--flow--medium]] - Lifecycle-aware collection
