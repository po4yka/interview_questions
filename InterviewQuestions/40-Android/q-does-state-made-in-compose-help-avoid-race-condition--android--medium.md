---
id: android-444
title: Does State Made In Compose Help Avoid Race Condition / Помогает ли State в Compose избежать состояния гонки
aliases:
  - Does State Made In Compose Help Avoid Race Condition
  - Помогает ли State в Compose избежать состояния гонки
  - Compose State Thread Safety
  - Thread Safety в Compose State
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
  - q-compose-state-management--android--medium
  - q-derived-state-snapshot-system--android--hard
  - q-android-performance-optimization--android--medium
sources:
  - https://developer.android.com/jetpack/compose/state
created: 2025-10-20
updated: 2025-10-28
tags:
  - android/ui-compose
  - android/ui-state
  - compose
  - concurrency
  - difficulty/medium
  - state
  - thread-safety
date created: Tuesday, October 28th 2025, 9:22:03 am
date modified: Thursday, October 30th 2025, 12:47:42 pm
---

# Вопрос (RU)
> Помогает ли State в Compose избежать состояния гонки?

# Question (EN)
> Does State Made In Compose Help Avoid Race Condition?

---

## Ответ (RU)

**Нет**, `MutableState` в Compose не гарантирует thread safety. При одновременном изменении состояния несколькими потоками возникают race conditions.

### Основные Проблемы

**MutableState не thread-safe**
- Одновременные изменения из разных потоков вызывают потерю обновлений
- Решение: использовать только в Main thread или применять thread-safe обертки

```kotlin
// ❌ ПЛОХО - race condition
@Composable
fun UnsafeCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        Thread { count++ }.start()
    }) { Text("Increment") }
}

// ✅ ХОРОШО - только Main thread
@Composable
fun SafeCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = { count++ }) { Text("Increment") }
}
```

**Background thread access**
- Изменение state из background потоков приводит к undefined behavior
- Решение: использовать `withContext(Dispatchers.Main)` для обновлений

```kotlin
// ❌ ПЛОХО - background thread access
@Composable
fun UnsafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        CoroutineScope(Dispatchers.IO).launch {
            count = heavyCalculation()
        }
    }) { Text("Calculate") }
}

// ✅ ХОРОШО - Main thread updates
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
    }) { Text("Calculate") }
}
```

**Shared state между компонентами**
- Несколько компонентов изменяют один state
- Решение: использовать ViewModel с StateFlow

```kotlin
// ❌ ПЛОХО - shared mutable state
@Composable
fun ParentComponent() {
    var sharedState by remember { mutableStateOf(0) }
    ChildComponent1(sharedState) { sharedState++ }
    ChildComponent2(sharedState) { sharedState++ }
}

// ✅ ХОРОШО - ViewModel для shared state
@Composable
fun ParentComponent(viewModel: SharedViewModel) {
    val state by viewModel.state.collectAsState()
    ChildComponent1(state) { viewModel.increment() }
    ChildComponent2(state) { viewModel.increment() }
}
```

### Thread Safety Решения

**Coroutines с Main Dispatcher**
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

**ViewModel для shared state**
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

**MutableState not thread-safe**
- Concurrent modifications from different threads cause lost updates
- Solution: use only in Main thread or apply thread-safe wrappers

```kotlin
// ❌ BAD - race condition
@Composable
fun UnsafeCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        Thread { count++ }.start()
    }) { Text("Increment") }
}

// ✅ GOOD - Main thread only
@Composable
fun SafeCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = { count++ }) { Text("Increment") }
}
```

**Background thread access**
- Modifying state from background threads leads to undefined behavior
- Solution: use `withContext(Dispatchers.Main)` for updates

```kotlin
// ❌ BAD - background thread access
@Composable
fun UnsafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        CoroutineScope(Dispatchers.IO).launch {
            count = heavyCalculation()
        }
    }) { Text("Calculate") }
}

// ✅ GOOD - Main thread updates
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
    }) { Text("Calculate") }
}
```

**Shared state between components**
- Multiple components modifying same state
- Solution: use ViewModel with StateFlow

```kotlin
// ❌ BAD - shared mutable state
@Composable
fun ParentComponent() {
    var sharedState by remember { mutableStateOf(0) }
    ChildComponent1(sharedState) { sharedState++ }
    ChildComponent2(sharedState) { sharedState++ }
}

// ✅ GOOD - ViewModel for shared state
@Composable
fun ParentComponent(viewModel: SharedViewModel) {
    val state by viewModel.state.collectAsState()
    ChildComponent1(state) { viewModel.increment() }
    ChildComponent2(state) { viewModel.increment() }
}
```

### Thread Safety Solutions

**Coroutines with Main Dispatcher**
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

**ViewModel for shared state**
```kotlin
class MyViewModel : ViewModel() {
    private val _state = MutableStateFlow(initialValue)
    val state = _state.asStateFlow()

    fun updateState(newValue: T) {
        _state.value = newValue // Thread-safe
    }
}
```

---

## Follow-ups

- How does Compose snapshot system work internally?
- What happens when multiple threads modify MutableState simultaneously?
- When to use StateFlow vs MutableState?
- How to debug race conditions in Compose state?

## References

- [[c-race-condition]]
- [[c-thread-safety]]
- [[c-compose-state]]
- [[moc-android]]

## Related Questions

### Prerequisites (Easier)
- [[q-compose-state-management--android--medium]]

### Advanced (Harder)
- [[q-derived-state-snapshot-system--android--hard]]
- [[q-android-performance-optimization--android--medium]]
