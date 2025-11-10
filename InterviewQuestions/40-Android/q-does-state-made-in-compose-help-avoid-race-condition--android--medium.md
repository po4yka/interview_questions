---
id: android-444
title: Does State in Compose Help Avoid Race Conditions / Помогает ли State в Compose избежать состояния гонки
aliases:
- Compose State Thread Safety
- Does State Made In Compose Help Avoid Race Condition
- Thread Safety в Compose State
- Помогает ли State в Compose избежать состояния гонки
topic: android
subtopics:
- ui-compose
- ui-state
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-compose-state
- c-jetpack-compose
- q-derived-state-snapshot-system--android--hard
created: 2025-10-20
updated: 2025-11-10
tags:
- android/ui-compose
- android/ui-state
- difficulty/medium
sources:
- "https://developer.android.com/jetpack/compose/state"

---

# Вопрос (RU)
> Помогает ли State в Compose избежать состояния гонки?

# Question (EN)
> Does State Made In Compose Help Avoid Race Condition?

---

## Ответ (RU)

**Нет**, `MutableState` в `Compose` сам по себе не гарантирует отсутствия race condition и не является универсальным thread-safe примитивом. Он построен на системе snapshot-состояния, которая обеспечивает согласованность чтения/записи внутри своих правил, но **не защищает** от одновременных небезопасных изменений из разных потоков без использования правильных механизмов (main thread, snapshot API или других средств синхронизации). При некорректном параллельном доступе возможно неконсистентное состояние UI, потеря обновлений и ошибки.

### Основные Проблемы

**1. MutableState не является общим thread-safe примитивом**

**Проблема:**

`MutableState` не предназначен как обычный thread-safe контейнер наподобие `Atomic*`. Он интегрирован с snapshot-системой Compose, которая ожидает, что изменения UI-состояния будут происходить согласованно (обычно — на главном потоке или через корректные snapshot-операции). Если одновременно изменять одно и то же состояние из разных потоков без координации, можно получить:
- **Потерю обновлений** — одно из изменений перезапишет другое
- **Некорректное состояние** — разные части UI могут наблюдать разные значения
- Потенциальные ошибки работы snapshot-системы

Важно: это не «магически защищённый» от гонок тип. Отвечает разработчик — как организованы потоки и точки записи.

**Решение:**

- Обновлять UI-состояние (`MutableState`) из одного, предсказуемого контекста (как правило, main thread), либо
- Использовать официальные snapshot-утилиты и/или дополнительные примитивы синхронизации при межпоточных изменениях.

Практический и рекомендуемый путь для UI:
- Выполнять работу в фоновых потоках
- Публиковать результат обратно в UI через main dispatcher или слой, гарантирующий согласованные обновления (`ViewModel` + `Flow`/`StateFlow`)

```kotlin
// ❌ ПЛОХО - изменение состояния из "сырых" фоновых потоков без координации
@Composable
fun UnsafeCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        Thread {
            // ⚠️ Риск: запись в snapshot-состояние из произвольного потока без соблюдения правил
            count++
        }.start()
    }) { Text("Increment: $count") }
}

// ✅ ХОРОШО - все изменения происходят в UI-потоке
@Composable
fun SafeCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        count++
    }) { Text("Increment: $count") }
}

// ✅ ХОРОШО - асинхронная работа в фоне, публикация результата в UI-потоке
@Composable
fun SafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    val scope = rememberCoroutineScope()
    Button(onClick = {
        scope.launch {
            val result = withContext(Dispatchers.IO) {
                heavyCalculation()
            }
            // Главное: обновление snapshot-состояния из согласованного (обычно main) контекста
            count = result
        }
    }) { Text("Count: $count") }
}
```

**2. Доступ из background потоков**

**Проблема:**

Прямое изменение `MutableState` из фоновых потоков (IO, Default и т.п.) без соблюдения правил snapshot-системы может приводить к неконсистентности и трудноотлавливаемым багам. На практике это выглядит как:
- пропущенные или странно упорядоченные recomposition,
- логически некорректное состояние,
- сложные для отладки эффекты при одновременных записях.

**Важно:** snapshot-система поддерживает работу с несколькими потоками через свои API, но это уже продвинутый сценарий. Для типичного UI-кода рекомендуется модель: фон → main → обновление состояния.

**Решение (рекомендуемый путь для UI-кода):**

Использовать `rememberCoroutineScope()` или `ViewModel` scope и переключаться на `Dispatchers.IO` только для фоновой работы, возвращая результат в UI через основной контекст.

```kotlin
// ❌ ПЛОХО - прямое изменение state в IO scope
@Composable
fun UnsafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        CoroutineScope(Dispatchers.IO).launch {
            // ⚠️ Неконтролируемая запись в snapshot-состояние из фонового потока
            count = heavyCalculation()
        }
    }) { Text("Calculate: $count") }
}

// ✅ ХОРОШО - работа в фоне, публикация из согласованного контекста
@Composable
fun SafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    val scope = rememberCoroutineScope()
    Button(onClick = {
        scope.launch {
            val result = withContext(Dispatchers.IO) {
                heavyCalculation()
            }
            count = result
        }
    }) { Text("Calculate: $count") }
}

// ✅ ХОРОШО - альтернатива с LaunchedEffect
@Composable
fun SafeAsyncCounterWithEffect() {
    var count by remember { mutableStateOf(0) }
    var trigger by remember { mutableStateOf(0) }

    LaunchedEffect(trigger) {
        val result = withContext(Dispatchers.IO) {
            heavyCalculation()
        }
        count = result
    }

    Button(onClick = { trigger++ }) {
        Text("Calculate: $count")
    }
}
```

**3. Shared state между компонентами**

**Проблема:**

Когда несколько `@Composable` напрямую изменяют один и тот же `MutableState`, возникают проблемы архитектуры и согласованности:
- **Нарушение Single Source of Truth** — непонятно, где находится главный источник данных
- **Сложность отладки** — трудно отследить, кто изменил состояние
- **Отсутствие жизненного цикла** — `remember { mutableStateOf() }` не переживает конфигурационные изменения
- При одновременном доступе из разных потоков — классические race conditions

Важно: два обработчика кликов в одном потоке, последовательно меняющих одно значение, сами по себе не создают data race. Проблема возникает, когда появляются конкурентные записи или плохо спроектированное разделение ответственности.

**Решение:**

Использовать `ViewModel` с `StateFlow`/`MutableStateFlow` или другим четко определённым слоем состояния для shared state. `StateFlow` предоставляет потокобезопасные обновления и интеграцию с жизненным циклом.

```kotlin
// ❌ ПЛОХО - общий mutable state в UI-слое
@Composable
fun ParentComponent() {
    var sharedState by remember { mutableStateOf(0) }

    ChildComponent1(sharedState) {
        sharedState++
    }
    ChildComponent2(sharedState) {
        sharedState++
    }
}

// ✅ ХОРОШО - ViewModel как единый источник истины
@Composable
fun ParentComponent(viewModel: SharedViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsState()
    ChildComponent1(state) { viewModel.increment() }
    ChildComponent2(state) { viewModel.increment() }
}

class SharedViewModel : ViewModel() {
    private val _state = MutableStateFlow(0)
    val state: StateFlow<Int> = _state.asStateFlow()

    fun increment() {
        _state.update { it + 1 } // Потокобезопасное инкрементирование
    }
}

// ✅ ХОРОШО - пример с Flow-источником
@Composable
fun ParentComponentWithFlow(viewModel: SharedViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsState()
    ChildComponent1(state) { viewModel.increment() }
    ChildComponent2(state) { viewModel.increment() }
}
```

### Решения и паттерны потокобезопасности

**1. Корутины с согласованным контекстом (обычно Main)**

Рекомендуется выполнять фоновые операции в соответствующих диспетчерах и обновлять UI-состояние из одного согласованного контекста (как правило, main):

```kotlin
@Composable
fun SafeAsyncComponent() {
    var state by remember { mutableStateOf(initialValue) }
    val scope = rememberCoroutineScope()

    Button(onClick = {
        scope.launch {
            val result = withContext(Dispatchers.IO) {
                performBackgroundWork()
            }
            state = result
        }
    }) {
        Text("Update")
    }
}
```

**2. `ViewModel` с `StateFlow` для shared state**

`StateFlow` и `MutableStateFlow` обеспечивают потокобезопасные обновления состояния.

```kotlin
class MyViewModel<T>(initialValue: T) : ViewModel() {
    private val _state = MutableStateFlow(initialValue)
    val state: StateFlow<T> = _state.asStateFlow()

    fun updateState(newValue: T) {
        _state.value = newValue
    }

    fun incrementInt(by: Int = 1) {
        // Только для Int-состояний; пример использования update для атомарности
        (_state as? MutableStateFlow<Int>)?.update { it + by }
    }
}

@Composable
fun MyScreen(viewModel: MyViewModel<SomeType> = hiltViewModel()) {
    val state by viewModel.state.collectAsState()
    // Безопасное использование shared state
}
```

**3. SnapshotFlow для интеграции со `Flow`**

Для наблюдения за snapshot-состоянием в корутинах используйте `snapshotFlow`:

```kotlin
@Composable
fun ComponentWithSnapshotFlow() {
    var count by remember { mutableStateOf(0) }

    LaunchedEffect(Unit) {
        snapshotFlow { count }
            .filter { it > 10 }
            .collect { value ->
                performAction(value)
            }
    }
}
```

**4. Классическая синхронизация (Mutex/Channel) для сложных случаев**

Для сложных сценариев с множественными конкурентными обновлениями используйте примитивы синхронизации на уровне бизнес-логики:

```kotlin
class ThreadSafeCounter {
    private val mutex = Mutex()
    private var _count = 0

    suspend fun increment() {
        mutex.withLock {
            _count++
        }
    }

    suspend fun getCount(): Int = mutex.withLock { _count }
}

@Composable
fun ComponentWithMutex(viewModel: ThreadSafeCounterViewModel = hiltViewModel()) {
    val scope = rememberCoroutineScope()
    Button(onClick = {
        scope.launch {
            viewModel.increment()
        }
    }) {
        Text("Increment")
    }
}
```

### Лучшие практики и рекомендации

**Архитектурные решения:**

- Использовать `MutableState` для локального UI-состояния и обновлять его из одного согласованного контекста
- Для разделяемого состояния использовать `ViewModel` + `StateFlow`/`Flow`
- Не писать в `MutableState` из произвольных фоновых потоков без понимания snapshot-системы и/или доп. синхронизации
- Использовать `rememberCoroutineScope()` и `ViewModel` scope для корректного управления корутинами

**Оптимизация производительности:**

- Минимизировать количество обновлений состояния, по возможности объединять
- Использовать `derivedStateOf` для производных значений, чтобы снизить количество recomposition
- Следить за временем выполнения в main dispatcher; тяжёлую работу выносить в фон

**Когда использовать что:**

- `MutableState`: локальное состояние одного composable / небольшого дерева
- `StateFlow` в `ViewModel`: разделяемое состояние между несколькими экранами/компонентами
- `Flow` + `collectAsState()`: реактивные источники (сеть, БД и т.п.)
- `snapshotFlow`: мост между snapshot-состоянием и `Flow`

### Типичные ошибки

**Проблема 1: Изменение state в LaunchedEffect только в фоновом контексте**

```kotlin
// ❌ ПЛОХО
LaunchedEffect(Unit) {
    withContext(Dispatchers.IO) {
        state = fetchData() // Запись в snapshot-состояние из фонового контекста
    }
}

// ✅ ХОРОШО
LaunchedEffect(Unit) {
    val data = withContext(Dispatchers.IO) {
        fetchData()
    }
    state = data
}
```

**Проблема 2: Нескоординированные записи в shared state**

```kotlin
// ❌ ПЛОХО
var counter by remember { mutableStateOf(0) }
Button1 { counter++ }
Button2 { counter++ }
// В одном потоке это не data race, но сложно масштабировать и контролировать ответственность

// ✅ ХОРОШО
val viewModel: CounterViewModel = hiltViewModel()
val counter by viewModel.counter.collectAsState()
Button1 { viewModel.increment() }
Button2 { viewModel.increment() }
```

---

## Answer (EN)

**No**, `MutableState` in Compose does not by itself prevent race conditions and is not a general-purpose thread-safe primitive. It is built on the snapshot state system, which ensures consistency under its own rules, but it does **not** protect you from unsafe concurrent modifications from multiple threads without proper coordination (main thread confinement, snapshot APIs, or additional synchronization). Incorrect concurrent access can lead to inconsistent UI state, lost updates, and hard-to-debug issues.

### Main Issues

**1. MutableState is not a general-purpose thread-safe primitive**

**Problem:**

`MutableState` is not meant to be used like `Atomic*` types. It is integrated with Compose's snapshot system, which assumes that UI state changes are performed in a coordinated manner (typically on the main thread or via proper snapshot operations). If you update the same state concurrently from multiple threads without coordination, you can get:
- **Lost updates** — one write overwrites another
- **Inconsistent state** — different parts of UI may observe different values
- Snapshot-related anomalies

It is not "magically" race-free; you remain responsible for designing safe access patterns.

**Solution:**

- Update UI `MutableState` from a single, predictable context (commonly the main thread), or
- Use official snapshot utilities and/or synchronization primitives when doing cross-thread updates.

A practical recommended pattern for UI:
- Do heavy work on background threads
- Publish results to UI via a confined context (main dispatcher, `ViewModel` with `Flow`/`StateFlow`, etc.)

```kotlin
// ❌ BAD - raw background thread writes into snapshot state
@Composable
fun UnsafeCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        Thread {
            // ⚠️ Risky: writing snapshot state from an arbitrary thread without proper rules
            count++
        }.start()
    }) { Text("Increment: $count") }
}

// ✅ GOOD - all updates happen in UI context
@Composable
fun SafeCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        count++
    }) { Text("Increment: $count") }
}

// ✅ GOOD - background work, result applied from a coordinated context
@Composable
fun SafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    val scope = rememberCoroutineScope()
    Button(onClick = {
        scope.launch {
            val result = withContext(Dispatchers.IO) {
                heavyCalculation()
            }
            count = result
        }
    }) { Text("Count: $count") }
}
```

**2. Background thread access**

**Problem:**

Directly modifying `MutableState` from background dispatchers (IO, Default, etc.) without respecting snapshot rules can result in:
- logically inconsistent state,
- surprising recomposition behavior,
- snapshot system issues when multiple writes interleave.

**Note:** The snapshot system itself supports multi-threaded usage via its APIs, but that is an advanced use case. For regular app code, prefer the simple pattern: background work → UI context → state update.

**Solution (recommended for typical UI code):**

Use `rememberCoroutineScope()` or `ViewModel` scope, switch to `Dispatchers.IO` only for heavy work, and apply state changes from a consistent context.

```kotlin
// ❌ BAD - writing snapshot state directly in IO scope
@Composable
fun UnsafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        CoroutineScope(Dispatchers.IO).launch {
            // ⚠️ Risky cross-thread write
            count = heavyCalculation()
        }
    }) { Text("Calculate: $count") }
}

// ✅ GOOD - compute in background, update from coordinated context
@Composable
fun SafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    val scope = rememberCoroutineScope()
    Button(onClick = {
        scope.launch {
            val result = withContext(Dispatchers.IO) {
                heavyCalculation()
            }
            count = result
        }
    }) { Text("Calculate: $count") }
}

// ✅ GOOD - alternative with LaunchedEffect
@Composable
fun SafeAsyncCounterWithEffect() {
    var count by remember { mutableStateOf(0) }
    var trigger by remember { mutableStateOf(0) }

    LaunchedEffect(trigger) {
        val result = withContext(Dispatchers.IO) {
            heavyCalculation()
        }
        count = result
    }

    Button(onClick = { trigger++ }) {
        Text("Calculate: $count")
    }
}
```

**3. Shared state between components**

**Problem:**

When multiple composables directly mutate the same `MutableState`, you run into architectural and consistency issues:
- **Single Source of Truth violation**
- **Debugging difficulties**
- No configuration-change survival for `remember` state
- If those writes become concurrent (e.g., from different threads) — actual race conditions

Note: Two click handlers on the same thread incrementing the same variable are not, by themselves, a data race; problems arise from poor separation of concerns or true concurrency.

**Solution:**

Use a `ViewModel` with `StateFlow` / `MutableStateFlow` (or similar) as the single source of truth for shared state. `StateFlow` provides thread-safe updates and integrates well with Compose.

```kotlin
// ❌ BAD - shared mutable state purely in UI layer
@Composable
fun ParentComponent() {
    var sharedState by remember { mutableStateOf(0) }

    ChildComponent1(sharedState) {
        sharedState++
    }
    ChildComponent2(sharedState) {
        sharedState++
    }
}

// ✅ GOOD - ViewModel provides centralized shared state
@Composable
fun ParentComponent(viewModel: SharedViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsState()
    ChildComponent1(state) { viewModel.increment() }
    ChildComponent2(state) { viewModel.increment() }
}

class SharedViewModel : ViewModel() {
    private val _state = MutableStateFlow(0)
    val state: StateFlow<Int> = _state.asStateFlow()

    fun increment() {
        _state.update { it + 1 }
    }
}

// ✅ GOOD - Flow-based reactive updates (same state property)
@Composable
fun ParentComponentWithFlow(viewModel: SharedViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsState()
    ChildComponent1(state) { viewModel.increment() }
    ChildComponent2(state) { viewModel.increment() }
}
```

### Thread Safety Solutions and Patterns

**1. Coroutines with a consistent context (usually Main)**

Use background dispatchers for heavy work, and apply UI state updates from a single coordinated context (commonly Main):

```kotlin
@Composable
fun SafeAsyncComponent() {
    var state by remember { mutableStateOf(initialValue) }
    val scope = rememberCoroutineScope()

    Button(onClick = {
        scope.launch {
            val result = withContext(Dispatchers.IO) {
                performBackgroundWork()
            }
            state = result
        }
    }) {
        Text("Update")
    }
}
```

**2. `ViewModel` with `StateFlow` for shared state**

`StateFlow` / `MutableStateFlow` provide thread-safe, observable state.

```kotlin
class MyViewModel<T>(initialValue: T) : ViewModel() {
    private val _state = MutableStateFlow(initialValue)
    val state: StateFlow<T> = _state.asStateFlow()

    fun updateState(newValue: T) {
        _state.value = newValue
    }

    fun incrementInt(by: Int = 1) {
        (_state as? MutableStateFlow<Int>)?.update { it + by }
    }
}

@Composable
fun MyScreen(viewModel: MyViewModel<SomeType> = hiltViewModel()) {
    val state by viewModel.state.collectAsState()
    // Safe usage of shared state
}
```

**3. SnapshotFlow for integrating snapshot state with `Flow`**

Use `snapshotFlow` to observe snapshot state changes in coroutines:

```kotlin
@Composable
fun ComponentWithSnapshotFlow() {
    var count by remember { mutableStateOf(0) }

    LaunchedEffect(Unit) {
        snapshotFlow { count }
            .filter { it > 10 }
            .collect { value ->
                performAction(value)
            }
    }
}
```

**4. Mutex / Channels for complex concurrency**

For complex scenarios with real concurrent writers, use explicit synchronization in your domain layer:

```kotlin
class ThreadSafeCounter {
    private val mutex = Mutex()
    private var _count = 0

    suspend fun increment() {
        mutex.withLock {
            _count++
        }
    }

    suspend fun getCount(): Int = mutex.withLock { _count }
}

@Composable
fun ComponentWithMutex(viewModel: ThreadSafeCounterViewModel = hiltViewModel()) {
    val scope = rememberCoroutineScope()
    Button(onClick = {
        scope.launch {
            viewModel.increment()
        }
    }) {
        Text("Increment")
    }
}
```

### Best Practices and Recommendations

**Architectural decisions:**

- Use `MutableState` for local UI state and mutate it from a single coordinated context
- Use `ViewModel` + `StateFlow`/`Flow` for shared or long-lived state
- Do not write into `MutableState` from arbitrary background threads without understanding snapshot rules or using extra synchronization
- Use `rememberCoroutineScope()` and `ViewModel` scopes to manage coroutine lifecycles

**Performance optimization:**

- Minimize state write frequency; batch updates where reasonable
- Use `derivedStateOf` for computed values to avoid unnecessary recompositions
- Keep heavy work off the main thread; only apply results on the coordinated/UI context

**When to use what:**

- `MutableState`: local state within a single composable or small tree
- `StateFlow` in `ViewModel`: shared state between screens/components
- `Flow` + `collectAsState()`: reactive external sources (network, DB, etc.)
- `snapshotFlow`: convert snapshot state to `Flow` for use in coroutine/`Flow` pipelines

### Common Pitfalls

**Problem 1: Updating state only from a background context in LaunchedEffect**

```kotlin
// ❌ BAD
LaunchedEffect(Unit) {
    withContext(Dispatchers.IO) {
        state = fetchData() // Writing into snapshot state from background context
    }
}

// ✅ GOOD
LaunchedEffect(Unit) {
    val data = withContext(Dispatchers.IO) {
        fetchData()
    }
    state = data
}
```

**Problem 2: Uncoordinated writers to shared state**

```kotlin
// ❌ BAD
var counter by remember { mutableStateOf(0) }
Button1 { counter++ }
Button2 { counter++ }
// On its own this is single-threaded, but scales poorly and blurs responsibilities

// ✅ GOOD
val viewModel: CounterViewModel = hiltViewModel()
val counter by viewModel.counter.collectAsState()
Button1 { viewModel.increment() }
Button2 { viewModel.increment() }
```

---

## Дополнительные вопросы (RU)

- Когда использовать `StateFlow` vs `MutableState` в архитектуре на основе Compose?
- Как snapshot-система в Compose концептуально обрабатывает конкурентные изменения?
- Как правильно обновлять состояние Compose из фоновых корутин, не нарушая правила snapshot-системы?
- Как выстроить разделяемое состояние с `ViewModel` и `StateFlow`, чтобы избежать гонок?
- Как отлаживать и обнаруживать race condition, связанные с обновлениями состояния в Compose?

## Follow-ups

- When to use `StateFlow` vs `MutableState` in Compose-based architecture?
- How does the snapshot system in Compose handle concurrent modifications conceptually?
- How to correctly update Compose state from background coroutines without violating snapshot rules?
- How to structure shared state with `ViewModel` and `StateFlow` to avoid race conditions?
- How to debug and detect race conditions related to Compose state updates?

## Ссылки (RU)

- [Документация по состоянию в Compose](https://developer.android.com/jetpack/compose/state)
- [`StateFlow` и `SharedFlow`](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)
- [Hoisting состояния в Compose](https://developer.android.com/jetpack/compose/state-hoisting)
- [Потокобезопасность в Kotlin](https://kotlinlang.org/docs/thread-safety.html)
- [Диспетчеры корутин](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)

## References

- [Compose State Documentation](https://developer.android.com/jetpack/compose/state)
- [`StateFlow` and `SharedFlow`](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)
- [Compose State Hoisting](https://developer.android.com/jetpack/compose/state-hoisting)
- [Thread Safety in Kotlin](https://kotlinlang.org/docs/thread-safety.html)
- [Coroutines Dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)

## Связанные вопросы (RU)

### Предпосылки / Концепты

- [[c-compose-state]]
- [[c-jetpack-compose]]

### Связанные (того же уровня)

- [[q-derived-state-snapshot-system--android--hard]]

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]
- [[c-jetpack-compose]]

### Related (Same Level)

- [[q-derived-state-snapshot-system--android--hard]]
