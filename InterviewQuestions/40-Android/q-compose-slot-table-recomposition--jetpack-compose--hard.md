---
tags:
  - jetpack-compose
  - internals
  - recomposition
  - slot-table
  - performance
difficulty: hard
status: draft
---

# Compose Slot Table & Recomposition Tracking

# Question (EN)
> What is the Slot Table in Compose? How does Compose track which composables need to recompose?

# Вопрос (RU)
> Что такое Slot Table в Compose? Как Compose отслеживает, какие composable-функции нужно перекомпоновать?

---

## Answer (EN)

The **Slot Table** is Compose's internal data structure that stores the state and metadata of the composition tree. It's the core mechanism that enables efficient recomposition by tracking what composables exist, their state, and what needs to update.

### What is the Slot Table?

The Slot Table is a **gap buffer** data structure that stores:
- **Groups** - hierarchical nodes representing composables
- **Slots** - storage locations for remembered values and state
- **Keys** - identifiers for positional memoization
- **Metadata** - information about composable structure

Think of it as a flat array representation of your UI tree, optimized for efficient insertions, deletions, and lookups.

```kotlin
// Conceptual structure (simplified)
class SlotTable {
    private val groups: IntArray      // Group structure
    private val slots: Array<Any?>    // Stored values
    private val anchors: List<Anchor> // Stable references

    // Gap buffer for efficient insertions
    private var gapStart: Int
    private var gapEnd: Int
}
```

---

### How the Slot Table Works

**1. During Initial Composition:**

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

**Slot Table after composition:**

```
Group 0: Counter (composable function)
├─ Slot 0: MutableState(0)           // remember { mutableStateOf(0) }
├─ Group 1: Button (composable)
│  ├─ Slot 1: Lambda (onClick)
│  └─ Group 2: Text (composable)
│     └─ Slot 2: "Count: 0"
```

**2. When State Changes:**

```kotlin
count++ // State mutation
```

Compose runtime:
1. Marks the state observer (Counter composable) as **invalid**
2. Schedules recomposition for the affected group
3. During recomposition, reads slots and updates only changed parts

```
Group 0: Counter (RECOMPOSE)
├─ Slot 0: MutableState(1)           // Value changed
├─ Group 1: Button (SKIP - no changes)
│  ├─ Slot 1: Lambda (same)
│  └─ Group 2: Text (RECOMPOSE)
│     └─ Slot 2: "Count: 1"         // Updated
```

---

### Gap Buffer Structure

The Slot Table uses a **gap buffer** for efficient insertions and deletions - similar to text editors.

```kotlin
// Gap buffer concept
// [data | gap | data]
//       ^    ^
//    gapStart gapEnd

// Before insertion at position 5:
// [0,1,2,3,4,_,_,_,5,6,7]
//            ^      ^
//         gap_start gap_end

// After insertion:
// [0,1,2,3,4,NEW,_,_,5,6,7]
//                ^    ^
```

**Benefits:**
- O(1) insertion at gap position
- O(1) deletion at gap position
- Only moves gap, not all data
- Efficient for sequential operations

---

### Positional Memoization

Compose uses **position-based identity** for composables, tracked in the Slot Table:

```kotlin
@Composable
fun UserList(users: List<User>) {
    Column {
        users.forEach { user ->
            UserItem(user) // Position-based identity
        }
    }
}
```

**Problem:** Without keys, position determines identity:

```
Initial:        After removing "Bob":
Slot 0: Alice   Slot 0: Alice
Slot 1: Bob     Slot 1: Charlie  // Wrong! This is Bob's slot
Slot 2: Charlie Slot 2: [empty]
```

**Solution:** Use keys for stable identity:

```kotlin
@Composable
fun UserList(users: List<User>) {
    Column {
        users.forEach { user ->
            key(user.id) { // Stable identity
                UserItem(user)
            }
        }
    }
}
```

**With keys in Slot Table:**

```
Initial:                After removing "Bob":
Slot [key=1]: Alice    Slot [key=1]: Alice
Slot [key=2]: Bob      Slot [key=3]: Charlie  // Correct!
Slot [key=3]: Charlie
```

---

### How Recomposition Tracking Works

**1. State Observation Registration:**

When a composable reads a `State<T>`, Compose registers it as an observer:

```kotlin
@Composable
fun Counter() {
    val count by remember { mutableStateOf(0) } // State creation
    Text("Count: $count") // Reading state registers observer
}
```

**Internal tracking:**

```kotlin
// Simplified internal representation
class SnapshotMutableStateImpl<T> : MutableState<T> {
    private var value: T
    private val observers = mutableSetOf<RecomposeScope>()

    override fun getValue(): T {
        // Register current composable as observer
        currentComposer.recordReadOf(this)
        return value
    }

    override fun setValue(value: T) {
        if (this.value != value) {
            this.value = value
            // Notify all observers
            observers.forEach { it.invalidate() }
        }
    }
}
```

**2. Invalidation:**

When state changes, Compose marks affected scopes as invalid:

```kotlin
@Composable
fun Parent() {
    val parentState by remember { mutableStateOf(0) }

    Child1(parentState) // Depends on parentState
    Child2()            // Independent
}

// When parentState changes:
// - Parent scope: INVALID (reads parentState)
// - Child1 scope: INVALID (receives parentState as parameter)
// - Child2 scope: VALID (no dependency)
```

**3. Recomposition Scope:**

Each composable creates a **RecomposeScope** - a boundary for recomposition:

```kotlin
// Conceptual structure
class RecomposeScope {
    var valid: Boolean = true
    var block: () -> Unit
    var used: Boolean = false

    fun invalidate() {
        if (valid && used) {
            valid = false
            scheduleRecompose()
        }
    }
}
```

---

### Practical Example: Tracking in Action

```kotlin
@Composable
fun App() {
    var counter by remember { mutableStateOf(0) }
    var name by remember { mutableStateOf("Alice") }

    Column {
        // Group 1: Reads counter
        Text("Counter: $counter")

        // Group 2: Reads name
        Text("Name: $name")

        // Group 3: Reads counter
        Button(onClick = { counter++ }) {
            Text("Count: $counter")
        }

        // Group 4: Independent
        Text("Static text")
    }
}
```

**Slot Table structure:**

```
Group 0: App
├─ Slot 0: MutableState(counter=0)
├─ Slot 1: MutableState(name="Alice")
├─ Group 1: Text - observes Slot 0
├─ Group 2: Text - observes Slot 1
├─ Group 3: Button - observes Slot 0
│  └─ Group 3.1: Text - observes Slot 0
└─ Group 4: Text - no observations
```

**When `counter` changes:**

```kotlin
counter++ // Triggers invalidation
```

**Recomposition:**
- Group 0 (App): ✅ Recompose (owns the state)
- Group 1: ✅ Recompose (reads counter)
- Group 2: ❌ Skip (only reads name)
- Group 3: ✅ Recompose (reads counter)
  - Group 3.1: ✅ Recompose (reads counter)
- Group 4: ❌ Skip (no dependencies)

---

### Slot Table Visualization Tool

**Using Layout Inspector:**

```kotlin
// Enable composition tracing
adb shell setprop debug.compose.trace true

// View in Android Studio
// Tools > Layout Inspector > Show Recomposition Counts
```

**Compose Compiler Metrics:**

```gradle
// build.gradle.kts
android {
    kotlinOptions {
        freeCompilerArgs += listOf(
            "-P",
            "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=" +
                "${project.buildDir}/compose_metrics"
        )
    }
}
```

**Generated report shows groups and slots:**

```
restartable skippable scheme("[0]") fun Counter(
  stable %composer: Composer?,
  stable %changed: Int
): Unit {
  %composer = %composer.startRestartGroup()
  val tmp0_remember = remember({ mutableStateOf(0) }, %composer, 0)
  val count = tmp0_remember.value

  // Slot table operations
  Button(
    onClick = { count++ },
    %composer,
    0
  ) {
    Text("Count: $count", %composer, 0)
  }
  %composer.endRestartGroup()
}
```

---

### Advanced: Slot Table Anchors

**Anchors** provide stable references to positions in the Slot Table, even as it changes:

```kotlin
@Composable
fun DynamicList(items: List<String>) {
    items.forEach { item ->
        key(item) {
            // Anchor created here
            RememberableItem(item)
        }
    }
}

@Composable
fun RememberableItem(item: String) {
    val anchor = rememberSaveableStateHolder()
    // Anchor maintains reference even if list reorders
    SaveableStateProvider(item) {
        Text(item)
    }
}
```

**How anchors work:**

```kotlin
// Simplified anchor implementation
class Anchor(private val table: SlotTable) {
    private var location: Int = -1

    fun toIndex(): Int {
        // Translates anchor to current index
        // Accounts for gap buffer shifts
        return if (location < table.gapStart) {
            location
        } else {
            location + (table.gapEnd - table.gapStart)
        }
    }
}
```

---

### Performance Implications

**Efficient Recomposition:**

```kotlin
@Composable
fun EfficientList(items: List<Item>) {
    LazyColumn {
        items(
            items = items,
            key = { it.id } // Stable keys = efficient slot reuse
        ) { item ->
            ItemRow(item)
        }
    }
}
```

**Inefficient (no keys):**
- All items recompose when list changes
- Slot table must rebuild entire structure
- Lost state and animations

**Efficient (with keys):**
- Only changed items recompose
- Slot table reuses existing groups
- State preserved across recompositions

---

### Best Practices

**1. Use stable keys for collections:**

```kotlin
// ✅ DO
items.forEach { item ->
    key(item.id) {
        ItemView(item)
    }
}

// ❌ DON'T (position-based)
items.forEach { item ->
    ItemView(item)
}
```

**2. Minimize state reads:**

```kotlin
// ❌ DON'T (reads state multiple times)
@Composable
fun UserProfile(userState: State<User>) {
    Text(userState.value.name)    // Read 1
    Text(userState.value.email)   // Read 2
    Text(userState.value.phone)   // Read 3
}

// ✅ DO (read once)
@Composable
fun UserProfile(userState: State<User>) {
    val user = userState.value    // Single read
    Text(user.name)
    Text(user.email)
    Text(user.phone)
}
```

**3. Use remember for expensive computations:**

```kotlin
// ✅ DO (computed once, stored in slot)
@Composable
fun ExpensiveView(data: List<Int>) {
    val sorted = remember(data) {
        data.sortedDescending() // Memoized in slot table
    }
    LazyColumn {
        items(sorted) { Text("$it") }
    }
}
```

**4. Understand recomposition scope:**

```kotlin
@Composable
fun Outer() {
    var state by remember { mutableStateOf(0) }

    // Only this composable recomposes when state changes
    InlineComposable { Text("$state") }

    // This creates a new recomposition scope
    SeparateComposable(state)
}

@Composable
inline fun InlineComposable(content: @Composable () -> Unit) {
    content() // No new scope
}

@Composable
fun SeparateComposable(value: Int) {
    Text("$value") // New recomposition scope
}
```

---

### Debugging Slot Table Issues

**Problem: State lost during recomposition**

```kotlin
// ❌ BAD: Conditional composable without key
@Composable
fun ConditionalView(showA: Boolean) {
    if (showA) {
        ComponentA() // Position 0
    } else {
        ComponentB() // Also position 0! State confusion
    }
}

// ✅ GOOD: Use keys
@Composable
fun ConditionalView(showA: Boolean) {
    if (showA) {
        key("A") { ComponentA() }
    } else {
        key("B") { ComponentB() }
    }
}
```

**Problem: Excessive recompositions**

Enable composition tracing:

```kotlin
// In your composable
@Composable
fun DebugComposable() {
    val recomposeCount = remember { mutableStateOf(0) }
    SideEffect {
        recomposeCount.value++
        Log.d("Recompose", "Count: ${recomposeCount.value}")
    }

    // Your UI
}
```

---

### Real-World Example: Optimized Chat List

```kotlin
@Stable
data class Message(
    val id: String,
    val text: String,
    val timestamp: Long,
    val author: String
)

@Composable
fun ChatList(messages: List<Message>) {
    LazyColumn {
        items(
            items = messages,
            key = { it.id } // Stable identity in slot table
        ) { message ->
            ChatMessage(message)
        }
    }
}

@Composable
fun ChatMessage(message: Message) {
    // Each message has its own recomposition scope
    // Only recomposes when this specific message changes

    var expanded by remember { mutableStateOf(false) }

    Card(
        modifier = Modifier.clickable { expanded = !expanded }
    ) {
        Column {
            Text(message.author)
            Text(message.text)

            if (expanded) {
                Text(
                    "Sent: ${formatTimestamp(message.timestamp)}",
                    style = MaterialTheme.typography.caption
                )
            }
        }
    }
}

@Composable
fun formatTimestamp(timestamp: Long): String {
    return remember(timestamp) {
        // Stored in slot table, not recomputed
        SimpleDateFormat("HH:mm", Locale.getDefault())
            .format(Date(timestamp))
    }
}
```

**Benefits:**
- New messages don't cause existing messages to recompose
- Expanding one message doesn't affect others
- Timestamp formatting cached in slot table
- Efficient insertions/deletions via gap buffer

---

## Ответ (RU)

**Slot Table** — это внутренняя структура данных Compose, которая хранит состояние и метаданные дерева композиции. Это основной механизм, обеспечивающий эффективную перекомпозицию путем отслеживания существующих composable-функций, их состояния и того, что нужно обновить.

### Что такое Slot Table?

Slot Table — это **gap buffer** структура данных, которая хранит:
- **Группы (Groups)** - иерархические узлы, представляющие composables
- **Слоты (Slots)** - места хранения для запомненных значений и состояния
- **Ключи (Keys)** - идентификаторы для позиционной мемоизации
- **Метаданные** - информация о структуре composable

Представьте её как плоское представление массива вашего UI-дерева, оптимизированное для эффективных вставок, удалений и поиска.

### Как работает Slot Table

**Во время начальной композиции:**

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

**Slot Table после композиции:**

```
Группа 0: Counter (composable функция)
├─ Слот 0: MutableState(0)           // remember { mutableStateOf(0) }
├─ Группа 1: Button (composable)
│  ├─ Слот 1: Lambda (onClick)
│  └─ Группа 2: Text (composable)
│     └─ Слот 2: "Count: 0"
```

### Отслеживание перекомпозиции

**Регистрация наблюдателей состояния:**

Когда composable читает `State<T>`, Compose регистрирует его как наблюдателя:

```kotlin
@Composable
fun Counter() {
    val count by remember { mutableStateOf(0) } // Создание состояния
    Text("Count: $count") // Чтение состояния регистрирует наблюдателя
}
```

**Инвалидация:**

При изменении состояния Compose помечает затронутые области как недействительные:

```kotlin
@Composable
fun Parent() {
    val parentState by remember { mutableStateOf(0) }

    Child1(parentState) // Зависит от parentState
    Child2()            // Независим
}

// При изменении parentState:
// - Parent scope: НЕДЕЙСТВИТЕЛЕН (читает parentState)
// - Child1 scope: НЕДЕЙСТВИТЕЛЕН (получает parentState как параметр)
// - Child2 scope: ДЕЙСТВИТЕЛЕН (нет зависимости)
```

### Gap Buffer структура

Slot Table использует **gap buffer** для эффективных вставок и удалений - аналогично текстовым редакторам.

**Преимущества:**
- O(1) вставка в позиции gap
- O(1) удаление в позиции gap
- Перемещается только gap, а не все данные
- Эффективно для последовательных операций

### Позиционная мемоизация

Compose использует **идентичность на основе позиции** для composables, отслеживаемую в Slot Table. Используйте `key()` для стабильной идентичности при работе с коллекциями.

### Лучшие практики

1. **Используйте стабильные ключи для коллекций**
2. **Минимизируйте чтения состояния**
3. **Используйте remember для дорогих вычислений**
4. **Понимайте область перекомпозиции**

Slot Table обеспечивает производительность Compose, позволяя перекомпоновать только то, что изменилось.
