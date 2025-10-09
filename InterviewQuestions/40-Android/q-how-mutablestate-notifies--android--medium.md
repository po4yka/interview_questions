---
topic: android
tags:
  - android
  - android/jetpack-compose
  - jetpack-compose
  - mutablestate
  - observer-pattern
  - recomposition
  - snapshot-system
  - state
  - state-management
difficulty: medium
status: reviewed
---

# Как mutableState сообщает о том, что он изменился?

**English**: How does MutableState notify that it has changed?

## Answer

Each **MutableState** has **subscribers** that are **automatically notified** about changes. When the value is updated, Compose **sends a signal** to trigger recomposition for those UI elements that use this state.

## Notification Mechanism

### Observer Pattern

`MutableState` uses the **Observer pattern** with Compose's **Snapshot system**.

```
┌──────────────┐
│ MutableState │
│   (Subject)  │
└──────┬───────┘
       │
       │ notifies
       ↓
┌──────────────────┐
│   Subscribers    │
│  (Composables)   │
└──────────────────┘
```

---

## How It Works Step-by-Step

### 1. Subscription (Read Phase)

When a Composable **reads** a MutableState, it automatically **subscribes** to changes.

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Column {
        // Reading count subscribes this Text to count changes
        Text("Count: $count")  // 👀 SUBSCRIBES to count

        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

**What happens during composition:**
1. `Text("Count: $count")` reads `count.value`
2. Compose **registers** this `Text` as a subscriber to `count`
3. Compose tracks: "If `count` changes, recompose `Text`"

---

### 2. Notification (Write Phase)

When the value is **updated**, subscribers are **notified**.

```kotlin
count++  // or count = count + 1
```

**What happens:**
1. `count++` writes new value to `MutableState`
2. `MutableState` detects the change
3. `MutableState` **notifies all subscribers**
4. Compose schedules recomposition for subscribed Composables
5. **Only** `Text("Count: $count")` recomposes (not the whole `Column` or `Button`)

---

## Snapshot System

Compose uses a **Snapshot system** to track state changes efficiently.

### Snapshots Explained

A **Snapshot** is an immutable view of all state at a specific point in time.

```kotlin
// Snapshot 1: count = 0
Snapshot {
    count = 0
    // UI shows "Count: 0"
}

// User clicks increment button

// Snapshot 2: count = 1
Snapshot {
    count = 1
    // UI shows "Count: 1"
}
```

**Benefits:**
- **Isolation** - Reads always see consistent state
- **Thread-safety** - Multiple threads can read safely
- **Rollback** - Can discard changes if needed

---

## Granular Recomposition

Only **Composables that read the changed state** are recomposed.

### Example: Multiple States

```kotlin
@Composable
fun Screen() {
    var name by remember { mutableStateOf("Alice") }
    var age by remember { mutableStateOf(25) }
    var city by remember { mutableStateOf("New York") }

    Column {
        // Subscriber 1: Only recomposes when `name` changes
        Text("Name: $name")

        // Subscriber 2: Only recomposes when `age` changes
        Text("Age: $age")

        // Subscriber 3: Only recomposes when `city` changes
        Text("City: $city")

        Button(onClick = { age++ }) {
            Text("Increment Age")
        }
    }
}
```

**When user clicks "Increment Age":**
1. `age++` notifies subscribers
2. **Only** `Text("Age: $age")` recomposes
3. `Text("Name: $name")` and `Text("City: $city")` are **NOT** recomposed

---

## Implementation Details

### Simplified Internal Flow

```kotlin
// Simplified version of MutableState
class MutableStateImpl<T>(private var _value: T) : MutableState<T> {
    private val subscribers = mutableListOf<() -> Unit>()

    override var value: T
        get() {
            // Register current Composable as subscriber (during composition)
            Snapshot.registerRead(this)
            return _value
        }
        set(newValue) {
            if (_value != newValue) {
                _value = newValue
                // Notify all subscribers
                notifySubscribers()
            }
        }

    private fun notifySubscribers() {
        subscribers.forEach { it.invoke() }  // Trigger recomposition
    }
}
```

---

## Practical Example

### Counter with Multiple Displays

```kotlin
@Composable
fun CounterScreen() {
    var count by remember { mutableStateOf(0) }

    println("CounterScreen composing")  // 🔍 This runs only ONCE

    Column {
        // These subscribe to `count`
        Text("Count: $count")
        Text("Double: ${count * 2}")
        Text("Triple: ${count * 3}")

        // This doesn't subscribe to `count`
        Text("Static text")

        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

**Execution flow:**

**Initial composition:**
```
CounterScreen composing        // Column composes
Count: 0                       // Text 1 subscribes to count
Double: 0                      // Text 2 subscribes to count
Triple: 0                      // Text 3 subscribes to count
Static text                    // Text 4 does NOT subscribe
```

**After clicking button (count becomes 1):**
```

# CounterScreen NOT recomposed (no println)

# Only these recompose:
Count: 1                       // Text 1 recomposes
Double: 2                      // Text 2 recomposes
Triple: 3                      // Text 3 recomposes

# Static text NOT recomposed
```

---

## ViewModel Integration

### StateFlow Notifications

```kotlin
class CounterViewModel : ViewModel() {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() {
        _count.value++  // Notifies collectors
    }
}

@Composable
fun CounterScreen(viewModel: CounterViewModel = viewModel()) {
    // collectAsState subscribes to StateFlow
    val count by viewModel.count.collectAsState()

    Column {
        Text("Count: $count")  // Recomposes when StateFlow emits

        Button(onClick = { viewModel.increment() }) {
            Text("Increment")
        }
    }
}
```

**Flow:**
1. `viewModel.increment()` changes `_count.value`
2. `StateFlow` emits new value
3. `collectAsState()` receives new value
4. Updates internal `MutableState`
5. `MutableState` notifies subscribers
6. `Text` recomposes

---

## Subscription Lifecycle

### When Composable Leaves Composition

```kotlin
@Composable
fun ConditionalDisplay() {
    var count by remember { mutableStateOf(0) }
    var showDetails by remember { mutableStateOf(false) }

    Column {
        Button(onClick = { showDetails = !showDetails }) {
            Text("Toggle Details")
        }

        Button(onClick = { count++ }) {
            Text("Increment")
        }

        if (showDetails) {
            // This Text subscribes to count only when visible
            Text("Count: $count")
        }
    }
}
```

**When `showDetails = false`:**
- `Text("Count: $count")` is **not in composition**
- It is **NOT subscribed** to `count`
- Incrementing `count` doesn't trigger its recomposition (it doesn't exist)

**When `showDetails = true`:**
- `Text("Count: $count")` **enters composition**
- It **subscribes** to `count`
- Incrementing `count` triggers its recomposition

**Compose automatically manages subscriptions:**
- Subscribe when Composable enters composition
- Unsubscribe when Composable leaves composition

---

## Performance Implications

### Smart Recomposition

```kotlin
@Composable
fun ExpensiveScreen() {
    var count by remember { mutableStateOf(0) }

    Column {
        // Expensive computation
        ExpensiveComponent()  // NOT recomposed when count changes

        // Simple text
        Text("Count: $count")  // Only this recomposes

        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}

@Composable
fun ExpensiveComponent() {
    println("ExpensiveComponent composing")  // 🔍 Only prints once
    // Heavy computation here
    LazyColumn {
        items(10000) { index ->
            Text("Item $index")
        }
    }
}
```

**Result:**
- `ExpensiveComponent` composes **only once**
- When `count` changes, **only** `Text("Count: $count")` recomposes
- Huge performance benefit!

---

## Debugging Subscriptions

### Composition Tracing

```kotlin
@Composable
fun DebugCounter() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count").also {
            println("Text composing with count = $count")
        }

        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

**Output:**
```
// Initial composition
Text composing with count = 0

// After first click
Text composing with count = 1

// After second click
Text composing with count = 2
```

---

## Summary

**How MutableState notifies about changes:**

1. **Subscription** - Composables automatically subscribe when they **read** the state
2. **Change detection** - When state value changes, `MutableState` detects it
3. **Notification** - All subscribers are notified
4. **Recomposition** - Only subscribed Composables recompose
5. **Snapshot system** - Ensures consistent, thread-safe state reads

**Key benefits:**
- **Granular recomposition** - Only affected Composables update
- **Automatic subscription management** - No manual subscribe/unsubscribe
- **Performance** - Minimal UI updates
- **Thread-safe** - Snapshot system ensures consistency

**Observer pattern in Compose:**
```
MutableState (Subject)
    ↓ notifies
Composables (Observers)
    ↓ trigger
Recomposition (Action)
```

---

## Ответ

Каждый **MutableState** имеет **подписчиков**, которые автоматически уведомляются об изменениях. При обновлении значения Compose отправляет сигнал о необходимости рекомпозиции тем элементам, которые используют это состояние.

**Механизм:**
1. **Подписка** - Composable автоматически подписывается при **чтении** состояния
2. **Обнаружение изменения** - `MutableState` детектирует изменение значения
3. **Уведомление** - Все подписчики уведомляются
4. **Рекомпозиция** - Только подписанные Composable перерисовываются

**Система Snapshot** обеспечивает консистентность и потокобезопасность.

**Гранулярная рекомпозиция:** Только те Composable, которые **читают** изменённое состояние, перерисовываются.

