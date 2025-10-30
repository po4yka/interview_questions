---
id: 20251017-105120
title: "MutableState в Compose / MutableState in Compose"
aliases: ["MutableState в Compose", "MutableState in Compose", "Изменяемое состояние Compose", "Compose State Management"]
topic: android
subtopics: [ui-compose, ui-state]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-state, c-jetpack-compose, q-state-hoisting-compose--android--medium, q-remember-vs-remembersaveable-compose--android--medium, q-compose-remember-derived-state--android--medium]
created: 2025-10-15
updated: 2025-10-30
tags: [android/ui-compose, android/ui-state, jetpack-compose, state-management, recomposition, difficulty/medium]
sources: []
---

# Вопрос (RU)

Что такое MutableState в Compose?

# Question (EN)

What is MutableState in Compose?

---

## Ответ (RU)

**`MutableState<T>`** — это обёртка для хранения состояния в Jetpack Compose, которая автоматически отслеживает изменения и инициирует рекомпозицию при изменении значения.

### Основная концепция

```kotlin
interface MutableState<T> : State<T> {
    override var value: T
}
```

**Ключевые характеристики:**
- **Observable** — автоматически уведомляет подписчиков
- **Триггерит рекомпозицию** — UI элементы перерисовываются
- **Типобезопасность** — строгая типизация через `<T>`
- **Переживает рекомпозицию** — работает с `remember`

### Создание состояния

**С явным .value:**
```kotlin
@Composable
fun Counter() {
    val count = remember { mutableStateOf(0) }

    Button(onClick = { count.value++ }) {  // ✅ Явное обращение к value
        Text("Count: ${count.value}")
    }
}
```

**С делегированием (by):**
```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }  // ✅ Автоматическая распаковка

    Button(onClick = { count++ }) {  // Чище, нет .value
        Text("Count: $count")
    }
}
```

### Как работает отслеживание

Compose автоматически подписывает composable на изменения состояния:

```kotlin
@Composable
fun UserProfile() {
    var name by remember { mutableStateOf("") }
    var age by remember { mutableStateOf(0) }

    Column {
        Text("Имя: $name")  // ✅ Подписан на name
        Text("Возраст: $age")  // ✅ Подписан на age

        Button(onClick = { name = "Иван" }) {  // Триггерит ТОЛЬКО Text с name
            Text("Изменить имя")
        }
    }
}
```

### MutableState vs обычная переменная

**❌ Обычная переменная:**
```kotlin
@Composable
fun Counter() {
    var count = 0  // ❌ Не работает

    Button(onClick = { count++ }) {  // count меняется, но UI не обновляется
        Text("Count: $count")
    }
}
```

**✅ MutableState:**
```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }  // ✅ Работает

    Button(onClick = { count++ }) {  // Триггерит рекомпозицию
        Text("Count: $count")
    }
}
```

### remember vs без remember

**❌ Без remember:**
```kotlin
var count by mutableStateOf(0)  // ❌ Сбрасывается на каждой рекомпозиции
```

**✅ С remember:**
```kotlin
var count by remember { mutableStateOf(0) }  // ✅ Кэшируется между рекомпозициями
```

### Типы состояний

**Примитивы:**
```kotlin
var count by remember { mutableStateOf(0) }
var name by remember { mutableStateOf("") }
var isEnabled by remember { mutableStateOf(false) }
```

**Объекты:**
```kotlin
data class User(val id: String, val name: String, val age: Int)

var user by remember { mutableStateOf(User("1", "Алиса", 25)) }
user = user.copy(age = 26)  // ✅ Создаёт новый объект, триггерит рекомпозицию
```

**Коллекции:**
```kotlin
// ✅ Immutable List
var items by remember { mutableStateOf(listOf<String>()) }
items = items + "Новый элемент"  // Создаёт новый список

// ✅ Mutable observable list
val items = remember { mutableStateListOf<String>() }
items.add("Новый элемент")  // Триггерит рекомпозицию напрямую
```

### Подъём состояния (State Hoisting)

**Паттерн:** состояние хранится в родителе, передаётся вниз через параметры.

```kotlin
@Composable
fun ParentScreen() {
    var searchQuery by remember { mutableStateOf("") }  // ✅ Единственный источник истины

    Column {
        SearchBar(
            query = searchQuery,
            onQueryChange = { searchQuery = it }
        )
        SearchResults(query = searchQuery)
    }
}

@Composable
fun SearchBar(query: String, onQueryChange: (String) -> Unit) {
    TextField(value = query, onValueChange = onQueryChange)
}
```

**Преимущества:**
- Единственный источник истины
- Переиспользуемые stateless компоненты
- Простое тестирование

### Интеграция с ViewModel

```kotlin
class UserViewModel : ViewModel() {
    private val _user = MutableStateFlow(User("1", "Алиса", 25))
    val user: StateFlow<User> = _user.asStateFlow()

    fun updateAge(newAge: Int) {
        _user.value = _user.value.copy(age = newAge)
    }
}

@Composable
fun UserProfile(viewModel: UserViewModel = viewModel()) {
    val user by viewModel.user.collectAsState()  // ✅ StateFlow → State

    Column {
        Text("Возраст: ${user.age}")
        Button(onClick = { viewModel.updateAge(user.age + 1) }) {
            Text("Увеличить возраст")
        }
    }
}
```

### Оптимизация производительности

**Умная рекомпозиция:**
Compose перерисовывает ТОЛЬКО composables, читающие изменённое состояние.

```kotlin
@Composable
fun Screen() {
    var count1 by remember { mutableStateOf(0) }
    var count2 by remember { mutableStateOf(0) }

    Column {
        Text("Count 1: $count1")  // ✅ Перерисуется только при изменении count1
        Text("Count 2: $count2")  // ✅ Перерисуется только при изменении count2
    }
}
```

**derivedStateOf для вычислений:**
```kotlin
@Composable
fun ItemList(items: List<Item>) {
    var filter by remember { mutableStateOf("") }

    // ✅ Пересчитывается ТОЛЬКО когда items или filter изменились
    val filteredItems by remember {
        derivedStateOf {
            items.filter { it.name.contains(filter, ignoreCase = true) }
        }
    }

    LazyColumn {
        items(filteredItems) { item -> Text(item.name) }
    }
}
```

---

## Answer (EN)

**`MutableState<T>`** is a wrapper for storing state in Jetpack Compose that automatically tracks changes and triggers recomposition when the value changes.

### Core Concept

```kotlin
interface MutableState<T> : State<T> {
    override var value: T
}
```

**Key characteristics:**
- **Observable** — automatically notifies subscribers
- **Triggers recomposition** — UI elements redraw automatically
- **Type-safe** — strongly typed via `<T>`
- **Survives recomposition** — works with `remember`

### Creating State

**With explicit .value:**
```kotlin
@Composable
fun Counter() {
    val count = remember { mutableStateOf(0) }

    Button(onClick = { count.value++ }) {  // ✅ Explicit value access
        Text("Count: ${count.value}")
    }
}
```

**With delegation (by):**
```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }  // ✅ Auto-unwrapping

    Button(onClick = { count++ }) {  // Cleaner, no .value
        Text("Count: $count")
    }
}
```

### How Tracking Works

Compose automatically subscribes composables to state changes:

```kotlin
@Composable
fun UserProfile() {
    var name by remember { mutableStateOf("") }
    var age by remember { mutableStateOf(0) }

    Column {
        Text("Name: $name")  // ✅ Subscribed to name
        Text("Age: $age")  // ✅ Subscribed to age

        Button(onClick = { name = "John" }) {  // Triggers ONLY Text with name
            Text("Change Name")
        }
    }
}
```

### MutableState vs Regular Variable

**❌ Regular variable:**
```kotlin
@Composable
fun Counter() {
    var count = 0  // ❌ Doesn't work

    Button(onClick = { count++ }) {  // count changes, but UI doesn't update
        Text("Count: $count")
    }
}
```

**✅ MutableState:**
```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }  // ✅ Works

    Button(onClick = { count++ }) {  // Triggers recomposition
        Text("Count: $count")
    }
}
```

### remember vs Without remember

**❌ Without remember:**
```kotlin
var count by mutableStateOf(0)  // ❌ Resets on every recomposition
```

**✅ With remember:**
```kotlin
var count by remember { mutableStateOf(0) }  // ✅ Cached across recompositions
```

### State Types

**Primitives:**
```kotlin
var count by remember { mutableStateOf(0) }
var name by remember { mutableStateOf("") }
var isEnabled by remember { mutableStateOf(false) }
```

**Objects:**
```kotlin
data class User(val id: String, val name: String, val age: Int)

var user by remember { mutableStateOf(User("1", "Alice", 25)) }
user = user.copy(age = 26)  // ✅ Creates new object, triggers recomposition
```

**Collections:**
```kotlin
// ✅ Immutable List
var items by remember { mutableStateOf(listOf<String>()) }
items = items + "New Item"  // Creates new list

// ✅ Mutable observable list
val items = remember { mutableStateListOf<String>() }
items.add("New Item")  // Triggers recomposition directly
```

### State Hoisting

**Pattern:** state lives in parent, passed down via parameters.

```kotlin
@Composable
fun ParentScreen() {
    var searchQuery by remember { mutableStateOf("") }  // ✅ Single source of truth

    Column {
        SearchBar(
            query = searchQuery,
            onQueryChange = { searchQuery = it }
        )
        SearchResults(query = searchQuery)
    }
}

@Composable
fun SearchBar(query: String, onQueryChange: (String) -> Unit) {
    TextField(value = query, onValueChange = onQueryChange)
}
```

**Benefits:**
- Single source of truth
- Reusable stateless components
- Easy testing

### ViewModel Integration

```kotlin
class UserViewModel : ViewModel() {
    private val _user = MutableStateFlow(User("1", "Alice", 25))
    val user: StateFlow<User> = _user.asStateFlow()

    fun updateAge(newAge: Int) {
        _user.value = _user.value.copy(age = newAge)
    }
}

@Composable
fun UserProfile(viewModel: UserViewModel = viewModel()) {
    val user by viewModel.user.collectAsState()  // ✅ StateFlow → State

    Column {
        Text("Age: ${user.age}")
        Button(onClick = { viewModel.updateAge(user.age + 1) }) {
            Text("Increment Age")
        }
    }
}
```

### Performance Optimization

**Smart Recomposition:**
Compose redraws ONLY composables reading the changed state.

```kotlin
@Composable
fun Screen() {
    var count1 by remember { mutableStateOf(0) }
    var count2 by remember { mutableStateOf(0) }

    Column {
        Text("Count 1: $count1")  // ✅ Recomposes only when count1 changes
        Text("Count 2: $count2")  // ✅ Recomposes only when count2 changes
    }
}
```

**derivedStateOf for Calculations:**
```kotlin
@Composable
fun ItemList(items: List<Item>) {
    var filter by remember { mutableStateOf("") }

    // ✅ Recalculates ONLY when items or filter change
    val filteredItems by remember {
        derivedStateOf {
            items.filter { it.name.contains(filter, ignoreCase = true) }
        }
    }

    LazyColumn {
        items(filteredItems) { item -> Text(item.name) }
    }
}
```

---

## Follow-ups

1. When should you use `rememberSaveable` instead of `remember`?
2. How does `derivedStateOf` differ from computed properties?
3. What happens if you forget to use `remember` with `mutableStateOf`?
4. How do you share state between multiple screens in Compose Navigation?
5. What are the performance implications of putting large objects in MutableState?

## References

- [[c-compose-state]] - Compose state management concepts
- [[c-jetpack-compose]] - Jetpack Compose fundamentals
- [[c-compose-recomposition]] - Recomposition mechanics
- https://developer.android.com/jetpack/compose/state
- https://developer.android.com/jetpack/compose/mental-model

## Related Questions

### Prerequisites (Easier)
- [[q-jetpack-compose-basics--android--medium]] - Compose fundamentals

### Related (Same Level)
- [[q-state-hoisting-compose--android--medium]] - State hoisting patterns
- [[q-remember-vs-remembersaveable-compose--android--medium]] - remember variants
- [[q-compose-remember-derived-state--android--medium]] - derivedStateOf usage
- [[q-recomposition-compose--android--medium]] - Recomposition mechanics
- [[q-how-mutablestate-notifies--android--medium]] - Notification internals

### Advanced (Harder)
- [[q-compose-stability-skippability--android--hard]] - Stability and skippability
- [[q-stable-classes-compose--android--hard]] - @Stable annotation
- [[q-compose-performance-optimization--android--hard]] - Performance best practices
