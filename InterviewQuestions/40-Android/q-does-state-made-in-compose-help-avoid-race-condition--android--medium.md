---
id: 20251020-200200
title: Does State Made In Compose Help Avoid Race Condition / Помогает ли State в
  Compose избежать состояния гонки
aliases: [Does State Made In Compose Help Avoid Race Condition, Помогает ли State в Compose избежать состояния гонки]
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
source: https://developer.android.com/jetpack/compose/state
source_note: Android Compose state management documentation
status: draft
moc: moc-android
related:
  - q-android-performance-optimization--android--medium
  - q-compose-state-management--android--medium
  - q-derived-state-snapshot-system--android--hard
created: 2025-10-20
updated: 2025-10-20
tags: [android/ui-compose, android/ui-state, compose, concurrency, difficulty/medium, state]
date created: Saturday, October 25th 2025, 1:26:29 pm
date modified: Saturday, October 25th 2025, 4:52:06 pm
---

# Вопрос (RU)
> Помогает ли State в Compose избежать состояния гонки?

# Question (EN)
> Does State Made In Compose Help Avoid Race Condition?

---
## Ответ (RU)

**Нет**, `MutableState` в Compose не гарантирует thread safety. При одновременном изменении состояния несколькими потоками возникают race conditions.

### Основные Проблемы

**1. MutableState не thread-safe**
- Проблема: одновременные изменения из разных потоков
- Результат: потеря обновлений, некорректные значения, краши
- Решение: использовать только в Main thread или применять thread-safe обертки

```kotlin
// ПЛОХО - race condition
@Composable
fun UnsafeCounter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = {
        Thread {
            count++ // ОПАСНО! Не thread-safe
        }.start()
    }) { Text("Increment") }
}

// ХОРОШО - только Main thread
@Composable
fun SafeCounter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = {
        count++ // Безопасно - Main thread
    }) { Text("Increment") }
}
```

**2. Concurrent access из background threads**
- Проблема: изменение state из background потоков
- Результат: undefined behavior, потеря данных
- Решение: использовать Dispatchers.Main для обновлений

```kotlin
// ПЛОХО - background thread access
@Composable
fun UnsafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = {
        CoroutineScope(Dispatchers.IO).launch {
            count = heavyCalculation() // ОПАСНО!
        }
    }) { Text("Calculate") }
}

// ХОРОШО - Main thread updates
@Composable
fun SafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    val scope = rememberCoroutineScope()

    Button(onClick = {
        scope.launch {
            val result = withContext(Dispatchers.IO) {
                heavyCalculation()
            }
            count = result // Безопасно - Main thread
        }
    }) { Text("Calculate") }
}
```

**3. Shared state между компонентами**
- Проблема: несколько компонентов изменяют один state
- Результат: race conditions при одновременных обновлениях
- Решение: использовать ViewModel или StateFlow для shared state

```kotlin
// ПЛОХО - shared mutable state
@Composable
fun ParentComponent() {
    var sharedState by remember { mutableStateOf(0) }

    ChildComponent1(state = sharedState) { sharedState++ }
    ChildComponent2(state = sharedState) { sharedState++ }
}

// ХОРОШО - ViewModel для shared state
@Composable
fun ParentComponent(viewModel: SharedViewModel) {
    val state by viewModel.state.collectAsState()

    ChildComponent1(state = state) { viewModel.increment() }
    ChildComponent2(state = state) { viewModel.increment() }
}
```

**4. Snapshot system limitations**
- Проблема: Compose snapshot system не защищает от concurrent writes
- Результат: inconsistent snapshots, потеря изменений
- Решение: использовать atomic operations или proper synchronization

```kotlin
// ПЛОХО - concurrent snapshot modifications
@Composable
fun UnsafeSnapshotUsage() {
    var data by remember { mutableStateOf(emptyList<String>()) }

    LaunchedEffect(Unit) {
        // Поток 1
        data = data + "item1"
        // Поток 2 может изменить data здесь
        data = data + "item2" // Может потерять изменения потока 2
    }
}

// ХОРОШО - atomic operations
@Composable
fun SafeSnapshotUsage() {
    var data by remember { mutableStateOf(emptyList<String>()) }

    LaunchedEffect(Unit) {
        data = data + "item1" + "item2" // Atomic update
    }
}
```

### Теория Compose State

**Snapshot System:**
- Compose использует snapshot system для отслеживания изменений состояния
- Snapshots создаются для каждого recomposition
- Изменения в snapshot не видны другим snapshot'ам до commit

**Thread Safety Model:**
- `MutableState` не thread-safe по дизайну
- Предполагается использование только в Main thread
- Background work должна завершаться в Main thread для UI updates

**Race Condition Sources:**
- Concurrent writes из разных потоков
- Shared mutable state между компонентами
- Non-atomic compound operations
- Snapshot modifications из background threads

**Best Practices:**
- Использовать `rememberCoroutineScope()` для background work
- Применять `withContext(Dispatchers.Main)` для UI updates
- Использовать ViewModel для shared state
- Избегать прямых изменений state из background threads

### Решения Для Thread Safety

**1. Coroutines с Main Dispatcher**
```kotlin
@Composable
fun SafeAsyncComponent() {
    var state by remember { mutableStateOf(initialValue) }
    val scope = rememberCoroutineScope()

    scope.launch {
        val result = withContext(Dispatchers.IO) {
            performBackgroundWork()
        }
        state = result // Main thread
    }
}
```

**2. Flow для reactive state**
```kotlin
@Composable
fun FlowBasedComponent(viewModel: MyViewModel) {
    val state by viewModel.state.collectAsState()
    // Flow автоматически thread-safe
}
```

**3. ViewModel для shared state**
```kotlin
class MyViewModel : ViewModel() {
    private val _state = MutableStateFlow(initialValue)
    val state = _state.asStateFlow()

    fun updateState(newValue: T) {
        _state.value = newValue // Thread-safe
    }
}
```

## Answer (EN)

**No**, `MutableState` in Compose does not guarantee thread safety. Concurrent state modifications from multiple threads cause race conditions.

### Main Issues

**1. MutableState not thread-safe**
- Problem: concurrent modifications from different threads
- Result: lost updates, incorrect values, crashes
- Solution: use only in Main thread or apply thread-safe wrappers

```kotlin
// BAD - race condition
@Composable
fun UnsafeCounter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = {
        Thread {
            count++ // DANGEROUS! Not thread-safe
        }.start()
    }) { Text("Increment") }
}

// GOOD - Main thread only
@Composable
fun SafeCounter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = {
        count++ // Safe - Main thread
    }) { Text("Increment") }
}
```

**2. Concurrent access from background threads**
- Problem: modifying state from background threads
- Result: undefined behavior, data loss
- Solution: use Dispatchers.Main for updates

```kotlin
// BAD - background thread access
@Composable
fun UnsafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = {
        CoroutineScope(Dispatchers.IO).launch {
            count = heavyCalculation() // DANGEROUS!
        }
    }) { Text("Calculate") }
}

// GOOD - Main thread updates
@Composable
fun SafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    val scope = rememberCoroutineScope()

    Button(onClick = {
        scope.launch {
            val result = withContext(Dispatchers.IO) {
                heavyCalculation()
            }
            count = result // Safe - Main thread
        }
    }) { Text("Calculate") }
}
```

**3. Shared state between components**
- Problem: multiple components modifying same state
- Result: race conditions on concurrent updates
- Solution: use ViewModel or StateFlow for shared state

```kotlin
// BAD - shared mutable state
@Composable
fun ParentComponent() {
    var sharedState by remember { mutableStateOf(0) }

    ChildComponent1(state = sharedState) { sharedState++ }
    ChildComponent2(state = sharedState) { sharedState++ }
}

// GOOD - ViewModel for shared state
@Composable
fun ParentComponent(viewModel: SharedViewModel) {
    val state by viewModel.state.collectAsState()

    ChildComponent1(state = state) { viewModel.increment() }
    ChildComponent2(state = state) { viewModel.increment() }
}
```

**4. Snapshot system limitations**
- Problem: Compose snapshot system doesn't protect from concurrent writes
- Result: inconsistent snapshots, lost changes
- Solution: use atomic operations or proper synchronization

```kotlin
// BAD - concurrent snapshot modifications
@Composable
fun UnsafeSnapshotUsage() {
    var data by remember { mutableStateOf(emptyList<String>()) }

    LaunchedEffect(Unit) {
        // Thread 1
        data = data + "item1"
        // Thread 2 can modify data here
        data = data + "item2" // Can lose Thread 2 changes
    }
}

// GOOD - atomic operations
@Composable
fun SafeSnapshotUsage() {
    var data by remember { mutableStateOf(emptyList<String>()) }

    LaunchedEffect(Unit) {
        data = data + "item1" + "item2" // Atomic update
    }
}
```

### Compose State Theory

**Snapshot System:**
- Compose uses snapshot system for tracking state changes
- Snapshots created for each recomposition
- Changes in snapshot not visible to other snapshots until commit

**Thread Safety Model:**
- `MutableState` not thread-safe by design
- Assumes usage only in Main thread
- Background work should complete in Main thread for UI updates

**Race Condition Sources:**
- Concurrent writes from different threads
- Shared mutable state between components
- Non-atomic compound operations
- Snapshot modifications from background threads

**Best Practices:**
- Use `rememberCoroutineScope()` for background work
- Apply `withContext(Dispatchers.Main)` for UI updates
- Use ViewModel for shared state
- Avoid direct state modifications from background threads

### Thread Safety Solutions

**1. Coroutines with Main Dispatcher**
```kotlin
@Composable
fun SafeAsyncComponent() {
    var state by remember { mutableStateOf(initialValue) }
    val scope = rememberCoroutineScope()

    scope.launch {
        val result = withContext(Dispatchers.IO) {
            performBackgroundWork()
        }
        state = result // Main thread
    }
}
```

**2. Flow for reactive state**
```kotlin
@Composable
fun FlowBasedComponent(viewModel: MyViewModel) {
    val state by viewModel.state.collectAsState()
    // Flow automatically thread-safe
}
```

**3. ViewModel for shared state**
```kotlin
class MyViewModel : ViewModel() {
    private val _state = MutableStateFlow(initialValue)
    val state = _state.asStateFlow()

    fun updateState(newValue: T) {
        _state.value = newValue // Thread-safe
    }
}
```

**See also:** c-race-condition, c-thread-safety


## Follow-ups
- How does Compose snapshot system work internally?
- What's the difference between MutableState and StateFlow thread safety?
- How to handle state updates in Compose with coroutines?

## Related Questions
- [[q-derived-state-snapshot-system--android--hard]]
