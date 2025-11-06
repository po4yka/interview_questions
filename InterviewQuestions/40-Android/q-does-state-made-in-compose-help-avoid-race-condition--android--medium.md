---
id: android-444
title: Does State Made In Compose Help Avoid Race Condition / Помогает ли State в
  Compose избежать состояния гонки
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
status: reviewed
moc: moc-android
related:
- c-compose-state
- c-jetpack-compose
- c-viewmodel
- q-derived-state-snapshot-system--android--hard
created: 2025-10-20
updated: 2025-11-02
tags:
- android/ui-compose
- android/ui-state
- compose
- concurrency
- difficulty/medium
- state
- thread-safety
sources:
- https://developer.android.com/jetpack/compose/state
---

# Вопрос (RU)
> Помогает ли State в Compose избежать состояния гонки?

# Question (EN)
> Does State Made In Compose Help Avoid Race Condition?

---

## Ответ (RU)

**Нет**, `MutableState` в `Compose` не гарантирует thread safety. `MutableState` — это обертка над простым значением, которая не содержит внутренних механизмов синхронизации потоков. При одновременном изменении состояния несколькими потоками возникают race conditions, которые могут привести к потере обновлений, некорректному состоянию UI, и даже к крашам приложения. Понимание механизмов thread safety в `Compose` критично для написания корректного асинхронного кода.

### Основные Проблемы

**1. MutableState не thread-safe**

**Проблема:**

`MutableState` не является thread-safe типом. Внутренне `MutableState` хранит значение в обычной переменной (`var value: T`), без использования синхронизации (`synchronized`, `volatile`, атомарных операций). Это означает:
- **Потеря обновлений** — при одновременной записи из разных потоков одно из обновлений может быть потеряно
- **Некорректное чтение** — чтение из фонового потока может вернуть устаревшее значение
- **Undefined behavior** — доступ из фоновых потоков к `MutableState` может привести к непредсказуемому поведению

**Решение:**

Использовать `MutableState` только на главном потоке (Main thread), где выполняются все операции UI. Для обновлений из фоновых потоков использовать `withContext(Dispatchers.Main)` или `Dispatchers.Main.immediate`.

```kotlin
// ❌ ПЛОХО - race condition при одновременном доступе
@Composable
fun UnsafeCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        // ⚠️ ОПАСНО: изменение state из фонового потока
        Thread {
            count++ // Может потерять обновления или вызвать краш
        }.start()
    }) { Text("Increment: $count") }
}

// ✅ ХОРОШО - только Main thread
@Composable
fun SafeCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        count++ // Безопасно: выполняется на главном потоке
    }) { Text("Increment: $count") }
}

// ✅ ХОРОШО - обновление из фонового потока через Main Dispatcher
@Composable
fun SafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    val scope = rememberCoroutineScope()
    Button(onClick = {
        scope.launch {
            // Выполнение тяжелой работы на IO потоке
            val result = withContext(Dispatchers.IO) {
                heavyCalculation()
            }
            // Обновление state на главном потоке
            withContext(Dispatchers.Main) {
                count = result
            }
        }
    }) { Text("Count: $count") }
}
```

**2. Доступ из background потоков**

**Проблема:**

Прямое изменение `MutableState` из фоновых потоков (IO, Default, Unconfined) приводит к:
- **Undefined behavior** — `Compose` ожидает, что все изменения state происходят на главном потоке
- **Отсутствие recomposition** — изменения из фоновых потоков могут не вызывать перекомпозицию UI
- **Нарушение snapshot system** — внутренняя система снимков состояния `Compose` может работать некорректно

**Решение:**

Использовать `withContext(Dispatchers.Main)` или `Dispatchers.Main.immediate` для всех обновлений `MutableState`. Предпочтительно использовать `Dispatchers.Main.immediate` для немедленных обновлений без задержек.

```kotlin
// ❌ ПЛОХО - изменение state из фонового потока
@Composable
fun UnsafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        CoroutineScope(Dispatchers.IO).launch {
            // ⚠️ ОПАСНО: прямое изменение state из IO потока
            count = heavyCalculation() // Undefined behavior, может не вызвать recomposition
        }
    }) { Text("Calculate: $count") }
}

// ✅ ХОРОШО - обновление через Main Dispatcher
@Composable
fun SafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    val scope = rememberCoroutineScope()
    Button(onClick = {
        scope.launch {
            // Тяжелая работа на IO потоке
            val result = withContext(Dispatchers.IO) {
                heavyCalculation()
            }
            // Безопасное обновление state на главном потоке
            withContext(Dispatchers.Main.immediate) {
                count = result // Гарантированное обновление и recomposition
            }
        }
    }) { Text("Calculate: $count") }
}

// ✅ ХОРОШО - альтернатива с LaunchedEffect для автоматической отмены
@Composable
fun SafeAsyncCounterWithEffect() {
    var count by remember { mutableStateOf(0) }
    var trigger by remember { mutableStateOf(0) }

    LaunchedEffect(trigger) {
        val result = withContext(Dispatchers.IO) {
            heavyCalculation()
        }
        // Автоматически выполняется на главном потоке
        count = result
    }

    Button(onClick = { trigger++ }) {
        Text("Calculate: $count")
    }
}
```

**3. Shared state между компонентами**

**Проблема:**

Когда несколько `@Composable` функций напрямую изменяют один и тот же `MutableState`, возникают проблемы:
- **Race conditions** — одновременные изменения из разных компонентов могут конфликтовать
- **Нарушение Single Source of Truth** — несколько источников истины для одного состояния
- **Сложность отладки** — трудно отследить, какой компонент изменил состояние
- **Отсутствие жизненного цикла** — `remember { mutableStateOf() }` не сохраняется при конфигурационных изменениях

**Решение:**

Использовать `ViewModel` с `StateFlow` или `MutableStateFlow` для shared state. `StateFlow` является thread-safe и обеспечивает правильный жизненный цикл состояния.

```kotlin
// ❌ ПЛОХО - shared mutable state без синхронизации
@Composable
fun ParentComponent() {
    var sharedState by remember { mutableStateOf(0) }
    // ⚠️ ОПАСНО: два компонента изменяют один state одновременно
    ChildComponent1(sharedState) {
        sharedState++ // Race condition при одновременном клике
    }
    ChildComponent2(sharedState) {
        sharedState++ // Потеря обновлений
    }
}

// ✅ ХОРОШО - ViewModel с StateFlow для shared state
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
        _state.value++ // Thread-safe операция
    }
}

// ✅ ХОРОШО - альтернатива с Flow для реактивного обновления
@Composable
fun ParentComponentWithFlow(viewModel: SharedViewModel = hiltViewModel()) {
    val state by viewModel.stateFlow.collectAsState(initial = 0)
    ChildComponent1(state) { viewModel.increment() }
    ChildComponent2(state) { viewModel.increment() }
}
```

### Решения И Паттерны `Thread` Safety

**1. Корутины с Main Dispatcher**

Использование `withContext(Dispatchers.Main)` или `Dispatchers.Main.immediate` для всех обновлений `MutableState`:

```kotlin
@Composable
fun SafeAsyncComponent() {
    var state by remember { mutableStateOf(initialValue) }
    val scope = rememberCoroutineScope()

    Button(onClick = {
        scope.launch {
            // Тяжелая работа на фоновом потоке
            val result = withContext(Dispatchers.IO) {
                performBackgroundWork()
            }
            // Безопасное обновление на главном потоке
            withContext(Dispatchers.Main.immediate) {
                state = result
            }
        }
    }) {
        Text("Update")
    }
}
```

**2. `ViewModel` с `StateFlow` для shared state**

`StateFlow` является thread-safe и гарантирует, что все обновления происходят безопасно:

```kotlin
class MyViewModel : ViewModel() {
    private val _state = MutableStateFlow(initialValue)
    val state: StateFlow<T> = _state.asStateFlow()

    fun updateState(newValue: T) {
        // Thread-safe операция: StateFlow использует CAS (Compare-And-Swap)
        _state.value = newValue
    }

    fun increment() {
        _state.update { it + 1 } // Атомарная операция
    }
}

@Composable
fun MyScreen(viewModel: MyViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsState()
    // Безопасное использование shared state
}
```

**3. Snapshot State для внутренней синхронизации**

Для простых случаев можно использовать `snapshotFlow` для преобразования `State` в `Flow`:

```kotlin
@Composable
fun ComponentWithSnapshotFlow() {
    var count by remember { mutableStateOf(0) }

    LaunchedEffect(Unit) {
        snapshotFlow { count }
            .filter { it > 10 }
            .collect {
                // Реакция на изменения count только на главном потоке
                performAction(it)
            }
    }
}
```

**4. Классическая синхронизация (Mutex/Channel) для сложных случаев**

Для более сложных случаев с множественными обновлениями можно использовать `Mutex` или `Channel`:

```kotlin
class ThreadSafeCounter {
    private val mutex = Mutex()
    private var _count = 0

    suspend fun increment() {
        mutex.withLock {
            _count++
        }
    }

    suspend fun getCount(): Int {
        return mutex.withLock {
            _count
        }
    }
}

@Composable
fun ComponentWithMutex(viewModel: MyViewModel = hiltViewModel()) {
    val scope = rememberCoroutineScope()
    Button(onClick = {
        scope.launch {
            viewModel.increment() // Thread-safe через Mutex
        }
    }) {
        Text("Increment")
    }
}
```

### Лучшие Практики И Рекомендации

**Архитектурные решения:**

-   **Использовать `MutableState` только на главном потоке** — все изменения должны происходить через `Dispatchers.Main` или `Dispatchers.Main.immediate`
-   **Использовать `ViewModel` для shared state** — `StateFlow` предоставляет thread-safe механизм для состояния, разделяемого между компонентами
-   **Избегать прямых изменений из фоновых потоков** — всегда использовать `withContext(Dispatchers.Main)` для обновлений `MutableState`
-   **Использовать `rememberCoroutineScope()`** — для корректного управления жизненным циклом корутин в `@Composable` функциях
-   **Предпочитать `Dispatchers.Main.immediate`** — для немедленных обновлений без задержек на планировщик

**Оптимизация производительности:**

-   **Минимизировать количество обновлений state** — батчить обновления, когда возможно
-   **Использовать `derivedStateOf` для вычисляемых значений** — избегать лишних recomposition при вычислении производных состояний
-   **Правильно управлять жизненным циклом корутин** — использовать `rememberCoroutineScope()` вместо глобальных scope

**Когда использовать что:**

-   **`MutableState`**: для локального состояния внутри одного `@Composable` компонента
-   **`StateFlow` в `ViewModel`**: для shared state между несколькими компонентами
-   **`Flow` + `collectAsState()`**: для реактивных обновлений из внешних источников (сеть, база данных)
-   **`snapshotFlow`**: для преобразования `State` в `Flow` для использования в других реактивных цепочках

### Типичные Ошибки

**Проблема 1: Изменение state в LaunchedEffect без проверки потока**

```kotlin
// ❌ ПЛОХО
LaunchedEffect(Unit) {
    withContext(Dispatchers.IO) {
        state = fetchData() // Может вызвать проблемы
    }
}

// ✅ ХОРОШО
LaunchedEffect(Unit) {
    val data = withContext(Dispatchers.IO) {
        fetchData()
    }
    withContext(Dispatchers.Main) {
        state = data
    }
}
```

**Проблема 2: Одновременное изменение одного state из разных мест**

```kotlin
// ❌ ПЛОХО
var counter by remember { mutableStateOf(0) }
Button1 { counter++ }
Button2 { counter++ } // Race condition

// ✅ ХОРОШО
val viewModel: CounterViewModel = hiltViewModel()
val counter by viewModel.counter.collectAsState()
Button1 { viewModel.increment() }
Button2 { viewModel.increment() } // Thread-safe через StateFlow
```

## Answer (EN)

**No**, `MutableState` in `Compose` does not guarantee thread safety. `MutableState` is a wrapper around a simple value that does not contain internal thread synchronization mechanisms. Concurrent state modifications from multiple threads cause race conditions that can lead to lost updates, incorrect UI state, and even app crashes. Understanding thread safety mechanisms in `Compose` is critical for writing correct asynchronous code.

### Main Issues

**1. MutableState not thread-safe**

**Problem:**

`MutableState` is not a thread-safe type. Internally, `MutableState` stores value in a regular variable (`var value: T`), without using synchronization (`synchronized`, `volatile`, atomic operations). This means:
- **Lost updates** — concurrent writes from different threads can cause one update to be lost
- **Incorrect reads** — reading from background thread may return stale value
- **Undefined behavior** — accessing `MutableState` from background threads can lead to unpredictable behavior

**Solution:**

Use `MutableState` only on main thread where all UI operations execute. For updates from background threads, use `withContext(Dispatchers.Main)` or `Dispatchers.Main.immediate`.

```kotlin
// ❌ BAD - race condition on concurrent access
@Composable
fun UnsafeCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        // ⚠️ DANGEROUS: modifying state from background thread
        Thread {
            count++ // May lose updates or cause crash
        }.start()
    }) { Text("Increment: $count") }
}

// ✅ GOOD - Main thread only
@Composable
fun SafeCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        count++ // Safe: executes on main thread
    }) { Text("Increment: $count") }
}

// ✅ GOOD - update from background thread via Main Dispatcher
@Composable
fun SafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    val scope = rememberCoroutineScope()
    Button(onClick = {
        scope.launch {
            // Perform heavy work on IO thread
            val result = withContext(Dispatchers.IO) {
                heavyCalculation()
            }
            // Update state on main thread
            withContext(Dispatchers.Main) {
                count = result
            }
        }
    }) { Text("Count: $count") }
}
```

**2. Background thread access**

**Problem:**

Direct modification of `MutableState` from background threads (IO, Default, Unconfined) leads to:
- **Undefined behavior** — `Compose` expects all state changes to occur on main thread
- **Missing recomposition** — changes from background threads may not trigger UI recomposition
- **Snapshot system violation** — internal `Compose` snapshot system may work incorrectly

**Solution:**

Use `withContext(Dispatchers.Main)` or `Dispatchers.Main.immediate` for all `MutableState` updates. Prefer `Dispatchers.Main.immediate` for immediate updates without delays.

```kotlin
// ❌ BAD - modifying state from background thread
@Composable
fun UnsafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        CoroutineScope(Dispatchers.IO).launch {
            // ⚠️ DANGEROUS: direct state modification from IO thread
            count = heavyCalculation() // Undefined behavior, may not trigger recomposition
        }
    }) { Text("Calculate: $count") }
}

// ✅ GOOD - update via Main Dispatcher
@Composable
fun SafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    val scope = rememberCoroutineScope()
    Button(onClick = {
        scope.launch {
            // Heavy work on IO thread
            val result = withContext(Dispatchers.IO) {
                heavyCalculation()
            }
            // Safe state update on main thread
            withContext(Dispatchers.Main.immediate) {
                count = result // Guaranteed update and recomposition
            }
        }
    }) { Text("Calculate: $count") }
}

// ✅ GOOD - alternative with LaunchedEffect for automatic cancellation
@Composable
fun SafeAsyncCounterWithEffect() {
    var count by remember { mutableStateOf(0) }
    var trigger by remember { mutableStateOf(0) }

    LaunchedEffect(trigger) {
        val result = withContext(Dispatchers.IO) {
            heavyCalculation()
        }
        // Automatically executes on main thread
        count = result
    }

    Button(onClick = { trigger++ }) {
        Text("Calculate: $count")
    }
}
```

**3. Shared state between components**

**Problem:**

When multiple `@Composable` functions directly modify the same `MutableState`, problems arise:
- **Race conditions** — concurrent modifications from different components can conflict
- **Single Source of Truth violation** — multiple sources of truth for one state
- **Debugging complexity** — difficult to track which component modified state
- **Missing lifecycle** — `remember { mutableStateOf() }` doesn't persist across configuration changes

**Solution:**

Use `ViewModel` with `StateFlow` or `MutableStateFlow` for shared state. `StateFlow` is thread-safe and provides proper state lifecycle.

```kotlin
// ❌ BAD - shared mutable state without synchronization
@Composable
fun ParentComponent() {
    var sharedState by remember { mutableStateOf(0) }
    // ⚠️ DANGEROUS: two components modify same state simultaneously
    ChildComponent1(sharedState) {
        sharedState++ // Race condition on simultaneous clicks
    }
    ChildComponent2(sharedState) {
        sharedState++ // Lost updates
    }
}

// ✅ GOOD - ViewModel with StateFlow for shared state
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
        _state.value++ // Thread-safe operation
    }
}

// ✅ GOOD - alternative with Flow for reactive updates
@Composable
fun ParentComponentWithFlow(viewModel: SharedViewModel = hiltViewModel()) {
    val state by viewModel.stateFlow.collectAsState(initial = 0)
    ChildComponent1(state) { viewModel.increment() }
    ChildComponent2(state) { viewModel.increment() }
}
```

### `Thread` Safety Solutions and Patterns

**1. Coroutines with Main Dispatcher**

Using `withContext(Dispatchers.Main)` or `Dispatchers.Main.immediate` for all `MutableState` updates:

```kotlin
@Composable
fun SafeAsyncComponent() {
    var state by remember { mutableStateOf(initialValue) }
    val scope = rememberCoroutineScope()

    Button(onClick = {
        scope.launch {
            // Heavy work on background thread
            val result = withContext(Dispatchers.IO) {
                performBackgroundWork()
            }
            // Safe update on main thread
            withContext(Dispatchers.Main.immediate) {
                state = result
            }
        }
    }) {
        Text("Update")
    }
}
```

**2. `ViewModel` with `StateFlow` for shared state**

`StateFlow` is thread-safe and guarantees that all updates occur safely:

```kotlin
class MyViewModel : ViewModel() {
    private val _state = MutableStateFlow(initialValue)
    val state: StateFlow<T> = _state.asStateFlow()

    fun updateState(newValue: T) {
        // Thread-safe operation: StateFlow uses CAS (Compare-And-Swap)
        _state.value = newValue
    }

    fun increment() {
        _state.update { it + 1 } // Atomic operation
    }
}

@Composable
fun MyScreen(viewModel: MyViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsState()
    // Safe usage of shared state
}
```

**3. Snapshot State for internal synchronization**

For simple cases, use `snapshotFlow` to transform `State` to `Flow`:

```kotlin
@Composable
fun ComponentWithSnapshotFlow() {
    var count by remember { mutableStateOf(0) }

    LaunchedEffect(Unit) {
        snapshotFlow { count }
            .filter { it > 10 }
            .collect {
                // React to count changes only on main thread
                performAction(it)
            }
    }
}
```

**4. Mutex synchronization for complex cases**

For more complex cases with multiple concurrent updates, use `Mutex` or `Channel`:

```kotlin
class ThreadSafeCounter {
    private val mutex = Mutex()
    private var _count = 0

    suspend fun increment() {
        mutex.withLock {
            _count++
        }
    }

    suspend fun getCount(): Int {
        return mutex.withLock {
            _count
        }
    }
}

@Composable
fun ComponentWithMutex(viewModel: MyViewModel = hiltViewModel()) {
    val scope = rememberCoroutineScope()
    Button(onClick = {
        scope.launch {
            viewModel.increment() // Thread-safe via Mutex
        }
    }) {
        Text("Increment")
    }
}
```

### Best Practices and Recommendations

**Architectural decisions:**

-   **Use `MutableState` only on main thread** — all changes must occur through `Dispatchers.Main` or `Dispatchers.Main.immediate`
-   **Use `ViewModel` for shared state** — `StateFlow` provides thread-safe mechanism for state shared between components
-   **Avoid direct modifications from background threads** — always use `withContext(Dispatchers.Main)` for `MutableState` updates
-   **Use `rememberCoroutineScope()`** — for correct lifecycle management of coroutines in `@Composable` functions
-   **Prefer `Dispatchers.Main.immediate`** — for immediate updates without scheduler delays

**Performance optimization:**

-   **Minimize number of state updates** — batch updates when possible
-   **Use `derivedStateOf` for computed values** — avoid unnecessary recomposition when computing derived states
-   **Properly manage coroutine lifecycle** — use `rememberCoroutineScope()` instead of global scopes

**When to use what:**

-   **`MutableState`**: for local state within single `@Composable` component
-   **`StateFlow` in `ViewModel`**: for shared state between multiple components
-   **`Flow` + `collectAsState()`**: for reactive updates from external sources (network, database)
-   **`snapshotFlow`**: to transform `State` to `Flow` for use in other reactive chains

### Common Pitfalls

**Problem 1: Modifying state in LaunchedEffect without thread check**

```kotlin
// ❌ BAD
LaunchedEffect(Unit) {
    withContext(Dispatchers.IO) {
        state = fetchData() // May cause issues
    }
}

// ✅ GOOD
LaunchedEffect(Unit) {
    val data = withContext(Dispatchers.IO) {
        fetchData()
    }
    withContext(Dispatchers.Main) {
        state = data
    }
}
```

**Problem 2: Simultaneous modification of same state from different places**

```kotlin
// ❌ BAD
var counter by remember { mutableStateOf(0) }
Button1 { counter++ }
Button2 { counter++ } // Race condition

// ✅ GOOD
val viewModel: CounterViewModel = hiltViewModel()
val counter by viewModel.counter.collectAsState()
Button1 { viewModel.increment() }
Button2 { viewModel.increment() } // Thread-safe via StateFlow
```

---

## Follow-ups

**Базовая теория:**
- Как работает система снимков (snapshot system) в `Compose` внутри?
- Что происходит, когда несколько потоков одновременно изменяют `MutableState`?
- В чем разница между thread-safe и thread-unsafe типами в Kotlin?

**Практические вопросы:**
- Когда использовать `StateFlow` vs `MutableState`?
- Как отлаживать race conditions в `Compose` state?
- Как правильно обновлять state из фоновых корутин?

**Производительность:**
- Как минимизировать количество recomposition при обновлении state?
- Когда использовать `Dispatchers.Main` vs `Dispatchers.Main.immediate`?
- Как оптимизировать обновления shared state между компонентами?

**Архитектура:**
- Как правильно структурировать state management в больших приложениях?
- Когда использовать `ViewModel` vs локальный `remember` state?
- Как обрабатывать ошибки при обновлении state из фоновых потоков?
- Как обеспечить thread safety при работе с `Flow` и `StateFlow`?

**Basic theory:**
- How does snapshot system work internally in `Compose`?
- What happens when multiple threads simultaneously modify `MutableState`?
- What's the difference between thread-safe and thread-unsafe types in Kotlin?

**Practical questions:**
- When to use `StateFlow` vs `MutableState`?
- How to debug race conditions in `Compose` state?
- How to correctly update state from background coroutines?

**Performance:**
- How to minimize number of recomposition when updating state?
- When to use `Dispatchers.Main` vs `Dispatchers.Main.immediate`?
- How to optimize shared state updates between components?

**Architecture:**
- How to properly structure state management in large applications?
- When to use `ViewModel` vs local `remember` state?
- How to handle errors when updating state from background threads?
- How to ensure thread safety when working with `Flow` and `StateFlow`?

## References

- [Compose State Documentation](https://developer.android.com/jetpack/compose/state)
- [`StateFlow` and `SharedFlow`](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)
- [Compose State Hoisting](https://developer.android.com/jetpack/compose/state-hoisting)
- [`Thread` Safety in Kotlin](https://kotlinlang.org/docs/thread-safety.html)
- [Coroutines Dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]
- [[c-jetpack-compose]]
- [[c-viewmodel]]


### Prerequisites (Easier)
- Compose basics and state management
- Coroutines and background threading
- Kotlin concurrency fundamentals

### Related (Same Level)
- Derived state and snapshot system in Compose
- `ViewModel` state management patterns

### Advanced (Harder)
- [[q-derived-state-snapshot-system--android--hard]]
- Custom thread-safe state implementations
- Advanced `Flow` patterns for state synchronization
