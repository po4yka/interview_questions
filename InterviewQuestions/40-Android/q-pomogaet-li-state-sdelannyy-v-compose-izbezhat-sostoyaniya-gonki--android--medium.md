---
topic: android
tags:
  - android
difficulty: medium
status: draft
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

Помогает ли state, сделанный в Compose, избежать состояния гонки

Нет, MutableState в Compose не гарантирует потокобезопасность. Если несколько потоков одновременно модифицируют состояние, это может привести к состоянию гонки
