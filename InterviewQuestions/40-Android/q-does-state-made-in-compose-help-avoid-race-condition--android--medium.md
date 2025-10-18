---
id: 20251012-1227131
title: "Does State Made In Compose Help Avoid Race Condition / Помогает ли State в Compose избежать состояния гонки"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-network-request-deduplication--networking--hard, q-multiple-manifests-multimodule--android--medium, q-what-are-the-most-important-components-of-compose--android--medium]
created: 2025-10-15
tags:
  - android
---
# Does state in Compose help avoid race conditions?

## EN (expanded)

### Short Answer

**No**, `MutableState` in Compose does not guarantee thread safety. If multiple threads simultaneously modify the state, it can lead to race conditions.

### Understanding the Problem

```kotlin
@Composable
fun UnsafeCounter() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count")

        Button(onClick = {
            // Multiple concurrent clicks can cause race conditions
            Thread {
                count++ // NOT thread-safe
            }.start()
        }) {
            Text("Increment in background")
        }
    }
}
```

### Why MutableState is Not Thread-Safe

`MutableState` is designed for single-threaded UI updates on the main thread:

```kotlin
// This is safe (main thread only)
@Composable
fun SafeCounter() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) { // Runs on main thread
            Text("Increment")
        }
    }
}
```

### Solutions for Thread Safety

#### 1. Use Coroutines with Main Dispatcher

```kotlin
@Composable
fun SafeCounterWithCoroutines() {
    var count by remember { mutableStateOf(0) }
    val scope = rememberCoroutineScope()

    Column {
        Text("Count: $count")

        Button(onClick = {
            scope.launch {
                // Background work
                val result = withContext(Dispatchers.IO) {
                    performHeavyCalculation()
                }
                // Update state on main thread
                count = result
            }
        }) {
            Text("Calculate")
        }
    }
}
```

#### 2. Use Flow for Reactive State

```kotlin
@Composable
fun FlowBasedCounter(viewModel: CounterViewModel) {
    val count by viewModel.count.collectAsState()

    Column {
        Text("Count: $count")
        Button(onClick = {
            viewModel.increment() // Thread-safe in ViewModel
        }) {
            Text("Increment")
        }
    }
}

class CounterViewModel : ViewModel() {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() {
        _count.update { it + 1 } // Thread-safe atomic update
    }
}
```

#### 3. Use Atomic Operations

```kotlin
@Composable
fun AtomicCounter() {
    val count = remember { mutableStateOf(AtomicInteger(0)) }

    Column {
        Text("Count: ${count.value.get()}")

        Button(onClick = {
            repeat(10) {
                Thread {
                    count.value.incrementAndGet() // Thread-safe
                }.start()
            }
        }) {
            Text("Increment 10 times")
        }
    }
}
```

#### 4. Use Mutex for Critical Sections

```kotlin
@Composable
fun MutexProtectedState() {
    var data by remember { mutableStateOf(emptyList<String>()) }
    val mutex = remember { Mutex() }
    val scope = rememberCoroutineScope()

    Column {
        Text("Items: ${data.size}")

        Button(onClick = {
            scope.launch {
                mutex.withLock {
                    // Protected critical section
                    val newData = data.toMutableList()
                    newData.add("Item ${newData.size}")
                    data = newData
                }
            }
        }) {
            Text("Add Item")
        }
    }
}
```

### Race Condition Example

```kotlin
// DANGEROUS: Race condition!
@Composable
fun RaceConditionExample() {
    var counter by remember { mutableStateOf(0) }

    LaunchedEffect(Unit) {
        // Launch multiple coroutines
        repeat(100) {
            launch(Dispatchers.Default) {
                // Race condition: reading and writing simultaneously
                val current = counter
                delay(1) // Simulate work
                counter = current + 1
            }
        }
    }

    Text("Counter: $counter") // Will likely be less than 100
}

// SAFE: Using StateFlow
@Composable
fun SafeExample(viewModel: SafeViewModel) {
    val counter by viewModel.counter.collectAsState()

    LaunchedEffect(Unit) {
        repeat(100) {
            launch(Dispatchers.Default) {
                viewModel.increment()
            }
        }
    }

    Text("Counter: $counter") // Will correctly be 100
}

class SafeViewModel : ViewModel() {
    private val _counter = MutableStateFlow(0)
    val counter = _counter.asStateFlow()

    fun increment() {
        _counter.update { it + 1 } // Thread-safe
    }
}
```

### Best Practices

1. **Keep State on Main Thread**: Update `MutableState` only from the main thread
2. **Use StateFlow for Shared State**: When multiple threads need to access state
3. **Use Coroutines Properly**: Always switch to `Dispatchers.Main` before updating state
4. **ViewModel for Business Logic**: Keep thread-unsafe operations in ViewModels
5. **Avoid Direct Threading**: Don't use `Thread` directly, use coroutines

### Correct Pattern

```kotlin
@Composable
fun CorrectPattern(viewModel: MyViewModel) {
    val state by viewModel.uiState.collectAsState()
    val scope = rememberCoroutineScope()

    Column {
        Text("Result: ${state.result}")

        Button(onClick = {
            // Launch coroutine
            scope.launch {
                // Do background work
                viewModel.performAction()
            }
        }) {
            Text("Perform Action")
        }
    }
}

class MyViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(UiState())
    val uiState = _uiState.asStateFlow()

    fun performAction() {
        viewModelScope.launch {
            // Background work on IO dispatcher
            val result = withContext(Dispatchers.IO) {
                performHeavyWork()
            }
            // Safe state update (happens on main thread automatically)
            _uiState.update { it.copy(result = result) }
        }
    }
}
```

---

## RU (original)
Помогает ли state, сделанный в Compose, избежать состояния гонки?

**Краткий ответ:**

**Нет**, `MutableState` в Compose не гарантирует потокобезопасность. Если несколько потоков одновременно модифицируют состояние, это может привести к состоянию гонки (race condition).

**Понимание проблемы:**

```kotlin
@Composable
fun UnsafeCounter() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count")

        Button(onClick = {
            // Множественные конкурентные клики могут вызвать race condition
            Thread {
                count++ // НЕ потокобезопасно
            }.start()
        }) {
            Text("Increment в фоне")
        }
    }
}
```

**Почему MutableState не является потокобезопасным:**

`MutableState` спроектирован для односторонних UI-обновлений на главном потоке:

```kotlin
// Это безопасно (только главный поток)
@Composable
fun SafeCounter() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) { // Выполняется на главном потоке
            Text("Increment")
        }
    }
}
```

**Решения для потокобезопасности:**

**1. Используйте Coroutines с Main Dispatcher:**

```kotlin
@Composable
fun SafeCounterWithCoroutines() {
    var count by remember { mutableStateOf(0) }
    val scope = rememberCoroutineScope()

    Column {
        Text("Count: $count")

        Button(onClick = {
            scope.launch {
                // Фоновая работа
                val result = withContext(Dispatchers.IO) {
                    performHeavyCalculation()
                }
                // Обновление state на главном потоке
                count = result
            }
        }) {
            Text("Calculate")
        }
    }
}
```

**2. Используйте Flow для реактивного State:**

```kotlin
@Composable
fun FlowBasedCounter(viewModel: CounterViewModel) {
    val count by viewModel.count.collectAsState()

    Column {
        Text("Count: $count")
        Button(onClick = {
            viewModel.increment() // Потокобезопасно в ViewModel
        }) {
            Text("Increment")
        }
    }
}

class CounterViewModel : ViewModel() {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() {
        _count.update { it + 1 } // Потокобезопасное атомарное обновление
    }
}
```

**3. Используйте атомарные операции:**

```kotlin
@Composable
fun AtomicCounter() {
    val count = remember { mutableStateOf(AtomicInteger(0)) }

    Column {
        Text("Count: \${count.value.get()}")

        Button(onClick = {
            repeat(10) {
                Thread {
                    count.value.incrementAndGet() // Потокобезопасно
                }.start()
            }
        }) {
            Text("Increment 10 раз")
        }
    }
}
```

**4. Используйте Mutex для критических секций:**

```kotlin
@Composable
fun MutexProtectedState() {
    var data by remember { mutableStateOf(emptyList<String>()) }
    val mutex = remember { Mutex() }
    val scope = rememberCoroutineScope()

    Column {
        Text("Items: \${data.size}")

        Button(onClick = {
            scope.launch {
                mutex.withLock {
                    // Защищенная критическая секция
                    val newData = data.toMutableList()
                    newData.add("Item \${newData.size}")
                    data = newData
                }
            }
        }) {
            Text("Добавить Item")
        }
    }
}
```

**Лучшие практики:**

1. **Держите State на главном потоке**: Обновляйте `MutableState` только с главного потока
2. **Используйте StateFlow для shared State**: Когда несколько потоков нуждаются в доступе к состоянию
3. **Используйте Coroutines правильно**: Всегда переключайтесь на `Dispatchers.Main` перед обновлением state
4. **ViewModel для бизнес-логики**: Держите потоконебезопасные операции в ViewModels
5. **Избегайте прямого Threading**: Не используйте `Thread` напрямую, используйте корутины

**Правильный паттерн:**

```kotlin
@Composable
fun CorrectPattern(viewModel: MyViewModel) {
    val state by viewModel.uiState.collectAsState()
    val scope = rememberCoroutineScope()

    Column {
        Text("Result: \${state.result}")

        Button(onClick = {
            scope.launch {
                viewModel.performAction()
            }
        }) {
            Text("Perform Action")
        }
    }
}

class MyViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(UiState())
    val uiState = _uiState.asStateFlow()

    fun performAction() {
        viewModelScope.launch {
            // Фоновая работа на IO dispatcher
            val result = withContext(Dispatchers.IO) {
                performHeavyWork()
            }
            // Безопасное обновление state (автоматически на главном потоке)
            _uiState.update { it.copy(result = result) }
        }
    }
}
```

**Ключевые выводы:**

- `MutableState` в Compose НЕ является потокобезопасным
- Для потокобезопасности используйте `StateFlow` с `update()`
- Всегда обновляйте UI state на главном потоке
- Используйте `Mutex` или атомарные операции для конкурентного доступа
- ViewModel + StateFlow - рекомендуемый паттерн для управления состоянием
## Related Questions

### Related (Medium)
- [[q-compose-modifier-order-performance--jetpack-compose--medium]] - Compose
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Compose
- [[q-compositionlocal-advanced--jetpack-compose--medium]] - Compose
- [[q-accessibility-compose--accessibility--medium]] - Compose
- [[q-compose-navigation-advanced--jetpack-compose--medium]] - Compose

### Advanced (Harder)
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Compose
- [[q-compose-custom-layout--jetpack-compose--hard]] - Compose
- [[q-compose-performance-optimization--android--hard]] - Compose
