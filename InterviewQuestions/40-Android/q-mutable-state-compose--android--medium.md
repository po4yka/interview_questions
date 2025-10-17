---
id: "20251015082237361"
title: "Mutable State Compose / Изменяемое состояние Compose"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - android
  - android/jetpack-compose
  - jetpack-compose
  - mutablestate
  - observable
  - recomposition
  - state
  - state-management
---
# What is MutableState in Compose?

**Russian**: Что такое mutable state в Compose?

**English**: What is MutableState in Compose?

## Answer (EN)
**`MutableState<T>`** is a **wrapper for storing state** in Jetpack Compose that **automatically tracks changes** and **triggers recomposition** when the value changes.

## MutableState Overview

`MutableState` is Compose's core mechanism for making UI reactive to state changes.

```kotlin
interface MutableState<T> : State<T> {
    override var value: T
}
```

### Key Characteristics

- **Observable** - Automatically notifies subscribers when value changes
- **Triggers recomposition** - UI elements reading this state will recompose
- **Type-safe** - Strongly typed with `<T>`
- **Scope-aware** - Works with `remember` to survive recomposition

---

## Creating MutableState

### 1. Using `mutableStateOf()`

```kotlin
@Composable
fun Counter() {
    // Create MutableState
    val count = remember { mutableStateOf(0) }

    Column {
        Text("Count: ${count.value}")  // Read value
        Button(onClick = { count.value++ }) {  // Write value
            Text("Increment")
        }
    }
}
```

### 2. Using Delegation (`by`)

```kotlin
@Composable
fun Counter() {
    // Delegate to automatically unwrap .value
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count")  // No .value needed
        Button(onClick = { count++ }) {  // No .value needed
            Text("Increment")
        }
    }
}
```

**Benefit of `by`:** Cleaner syntax, no need to write `.value`

---

## How MutableState Works

### Automatic Tracking

```kotlin
@Composable
fun UserProfile() {
    var name by remember { mutableStateOf("") }
    var age by remember { mutableStateOf(0) }

    Column {
        // These Composables are "subscribed" to name and age
        Text("Name: $name")  // Will recompose when name changes
        Text("Age: $age")    // Will recompose when age changes

        TextField(
            value = name,
            onValueChange = { name = it }  // Changing name triggers recomposition
        )

        Button(onClick = { age++ }) {
            Text("Increment Age")  // Changing age triggers recomposition
        }
    }
}
```

**What happens:**
1. `Text("Name: $name")` **reads** `name` state
2. Compose **registers** this Composable as a subscriber to `name`
3. When `name` changes, Compose **recomposes** only `Text("Name: $name")`
4. `Text("Age: $age")` is **NOT** recomposed (it doesn't read `name`)

---

## MutableState vs Regular Variables

### - Regular Variable (Doesn't Work)

```kotlin
@Composable
fun Counter() {
    var count = 0  // - Regular variable

    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) {  // count changes, but UI doesn't update!
            Text("Increment")
        }
    }
}
```

**Problem:** `count++` changes the variable, but Compose doesn't know about it, so UI doesn't update.

### - MutableState (Works)

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }  // - MutableState

    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) {  // Triggers recomposition!
            Text("Increment")
        }
    }
}
```

**Why it works:** `MutableState` notifies Compose about the change, triggering recomposition.

---

## remember + mutableStateOf

### Without `remember` (Resets on Every Recomposition)

```kotlin
@Composable
fun Counter() {
    var count by mutableStateOf(0)  // - No remember!

    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

**Problem:**
- First click: `count` becomes 1, triggers recomposition
- During recomposition: `mutableStateOf(0)` creates NEW state with value 0
- `count` resets to 0!

### With `remember` (Survives Recomposition)

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }  // - With remember!

    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

**Why it works:**
- `remember` caches the `MutableState` instance across recompositions
- `count` retains its value (1, 2, 3, ...)

---

## MutableState Types

### 1. Primitive Types

```kotlin
var count by remember { mutableStateOf(0) }
var name by remember { mutableStateOf("") }
var isEnabled by remember { mutableStateOf(false) }
var price by remember { mutableStateOf(0.0) }
```

### 2. Complex Types

```kotlin
data class User(val id: String, val name: String, val age: Int)

var user by remember {
    mutableStateOf(User("1", "Alice", 25))
}

// Update entire object
user = user.copy(age = 26)  // Triggers recomposition
```

### 3. Collections

```kotlin
// List
var items by remember { mutableStateOf(listOf<String>()) }
items = items + "New Item"  // Triggers recomposition

// Using mutableStateListOf for in-place modifications
val items = remember { mutableStateListOf<String>() }
items.add("New Item")  // Triggers recomposition
```

---

## Hoisting State

**State hoisting** = Moving state to a parent Composable for sharing.

```kotlin
@Composable
fun ParentScreen() {
    // State hoisted to parent
    var searchQuery by remember { mutableStateOf("") }

    Column {
        SearchBar(
            query = searchQuery,
            onQueryChange = { searchQuery = it }  // Parent owns state
        )

        SearchResults(query = searchQuery)  // Shared state
    }
}

@Composable
fun SearchBar(
    query: String,
    onQueryChange: (String) -> Unit
) {
    TextField(
        value = query,
        onValueChange = onQueryChange
    )
}

@Composable
fun SearchResults(query: String) {
    Text("Searching for: $query")
}
```

**Benefits:**
- **Single source of truth** - `searchQuery` owned by parent
- **Reusability** - `SearchBar` and `SearchResults` are stateless
- **Testability** - Easier to test stateless Composables

---

## ViewModel Integration

```kotlin
class UserViewModel : ViewModel() {
    // Use StateFlow in ViewModel
    private val _user = MutableStateFlow(User("1", "Alice", 25))
    val user: StateFlow<User> = _user.asStateFlow()

    fun updateAge(newAge: Int) {
        _user.value = _user.value.copy(age = newAge)
    }
}

@Composable
fun UserProfile(viewModel: UserViewModel = viewModel()) {
    // Convert StateFlow to State
    val user by viewModel.user.collectAsState()

    Column {
        Text("Name: ${user.name}")
        Text("Age: ${user.age}")

        Button(onClick = { viewModel.updateAge(user.age + 1) }) {
            Text("Increment Age")
        }
    }
}
```

---

## Performance Optimization

### Smart Recomposition

Compose only recomposes **Composables that read the changed state**.

```kotlin
@Composable
fun Screen() {
    var count1 by remember { mutableStateOf(0) }
    var count2 by remember { mutableStateOf(0) }

    Column {
        // Only recomposes when count1 changes
        Text("Count 1: $count1")

        // Only recomposes when count2 changes
        Text("Count 2: $count2")

        Button(onClick = { count1++ }) {
            Text("Increment Count 1")
        }

        Button(onClick = { count2++ }) {
            Text("Increment Count 2")
        }
    }
}
```

**Result:**
- Clicking "Increment Count 1" only recomposes `Text("Count 1: $count1")`
- `Text("Count 2: $count2")` is NOT recomposed

### derivedStateOf for Expensive Calculations

```kotlin
@Composable
fun ItemList(items: List<Item>) {
    var filter by remember { mutableStateOf("") }

    // - Only recalculate when items or filter change
    val filteredItems by remember {
        derivedStateOf {
            items.filter { it.name.contains(filter, ignoreCase = true) }
        }
    }

    Column {
        TextField(value = filter, onValueChange = { filter = it })
        LazyColumn {
            items(filteredItems) { item ->
                Text(item.name)
            }
        }
    }
}
```

---

## Common Patterns

### 1. Toggle State

```kotlin
var isExpanded by remember { mutableStateOf(false) }

Button(onClick = { isExpanded = !isExpanded }) {
    Text(if (isExpanded) "Collapse" else "Expand")
}
```

### 2. Loading State

```kotlin
var isLoading by remember { mutableStateOf(false) }

LaunchedEffect(Unit) {
    isLoading = true
    val data = fetchData()
    isLoading = false
}

if (isLoading) {
    CircularProgressIndicator()
} else {
    Content()
}
```

### 3. Form State

```kotlin
var email by remember { mutableStateOf("") }
var password by remember { mutableStateOf("") }
var isValid by remember { mutableStateOf(false) }

// Update validation when inputs change
LaunchedEffect(email, password) {
    isValid = email.isNotBlank() && password.length >= 6
}

Button(
    onClick = { submitForm() },
    enabled = isValid
) {
    Text("Submit")
}
```

---

## Summary

**`MutableState<T>`:**
- **Observable wrapper** for state in Compose
- **Automatically tracks changes** and triggers recomposition
- **Type-safe** with generic `<T>`
- **Works with `remember`** to survive recomposition

**Key patterns:**
- `remember { mutableStateOf(value) }` - Create and remember state
- `var state by remember { mutableStateOf(value) }` - Delegation for cleaner syntax
- **State hoisting** - Move state to parent for sharing
- **ViewModel integration** - Use StateFlow, convert with `collectAsState()`

**Performance:**
- Only recomposes Composables that **read** the changed state
- Use `derivedStateOf` for expensive calculations

---

## Ответ (RU)

**`MutableState<T>`** – это **обертка для хранения состояния** в Jetpack Compose, которая **автоматически отслеживает изменения** и **инициирует рекомпозицию** при изменении значения.

### Обзор MutableState

`MutableState` - это основной механизм Compose для создания реактивного UI к изменениям состояния.

```kotlin
interface MutableState<T> : State<T> {
    override var value: T
}
```

### Ключевые характеристики

- **Наблюдаемый** - Автоматически уведомляет подписчиков при изменении значения
- **Триггерит рекомпозицию** - UI элементы, читающие это состояние, будут перекомпонованы
- **Типобезопасный** - Строго типизированный с `<T>`
- **Осведомлен о области видимости** - Работает с `remember` для сохранения между рекомпозициями

---

### Создание MutableState

#### 1. Использование `mutableStateOf()`

```kotlin
@Composable
fun Counter() {
    // Создание MutableState
    val count = remember { mutableStateOf(0) }

    Column {
        Text("Счетчик: ${count.value}")  // Чтение значения
        Button(onClick = { count.value++ }) {  // Запись значения
            Text("Увеличить")
        }
    }
}
```

#### 2. Использование делегирования (`by`)

```kotlin
@Composable
fun Counter() {
    // Делегирование для автоматической распаковки .value
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Счетчик: $count")  // Не нужно .value
        Button(onClick = { count++ }) {  // Не нужно .value
            Text("Увеличить")
        }
    }
}
```

**Преимущество `by`:** Более чистый синтаксис, не нужно писать `.value`

---

### Как работает MutableState

#### Автоматическое отслеживание

```kotlin
@Composable
fun UserProfile() {
    var name by remember { mutableStateOf("") }
    var age by remember { mutableStateOf(0) }

    Column {
        // Эти Composables "подписаны" на name и age
        Text("Имя: $name")  // Будет перекомпонован при изменении name
        Text("Возраст: $age")    // Будет перекомпонован при изменении age

        TextField(
            value = name,
            onValueChange = { name = it }  // Изменение name вызывает рекомпозицию
        )

        Button(onClick = { age++ }) {
            Text("Увеличить возраст")  // Изменение age вызывает рекомпозицию
        }
    }
}
```

**Что происходит:**
1. `Text("Имя: $name")` **читает** состояние `name`
2. Compose **регистрирует** этот Composable как подписчика на `name`
3. Когда `name` изменяется, Compose **перекомпоновывает** только `Text("Имя: $name")`
4. `Text("Возраст: $age")` **НЕ** перекомпонуется (он не читает `name`)

---

### MutableState vs Обычные переменные

#### ❌ Обычная переменная (Не работает)

```kotlin
@Composable
fun Counter() {
    var count = 0  // ❌ Обычная переменная

    Column {
        Text("Счетчик: $count")
        Button(onClick = { count++ }) {  // count изменяется, но UI не обновляется!
            Text("Увеличить")
        }
    }
}
```

**Проблема:** `count++` изменяет переменную, но Compose не знает об этом, поэтому UI не обновляется.

#### ✅ MutableState (Работает)

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }  // ✅ MutableState

    Column {
        Text("Счетчик: $count")
        Button(onClick = { count++ }) {  // Вызывает рекомпозицию!
            Text("Увеличить")
        }
    }
}
```

**Почему работает:** `MutableState` уведомляет Compose об изменении, вызывая рекомпозицию.

---

### remember + mutableStateOf

#### Без `remember` (Сбрасывается при каждой рекомпозиции)

```kotlin
@Composable
fun Counter() {
    var count by mutableStateOf(0)  // ❌ Нет remember!

    Column {
        Text("Счетчик: $count")
        Button(onClick = { count++ }) {
            Text("Увеличить")
        }
    }
}
```

**Проблема:**
- Первый клик: `count` становится 1, вызывает рекомпозицию
- Во время рекомпозиции: `mutableStateOf(0)` создает НОВОЕ состояние со значением 0
- `count` сбрасывается на 0!

#### С `remember` (Сохраняется между рекомпозициями)

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }  // ✅ С remember!

    Column {
        Text("Счетчик: $count")
        Button(onClick = { count++ }) {
            Text("Увеличить")
        }
    }
}
```

**Почему работает:**
- `remember` кэширует экземпляр `MutableState` между рекомпозициями
- `count` сохраняет свое значение (1, 2, 3, ...)

---

### Типы MutableState

#### 1. Примитивные типы

```kotlin
var count by remember { mutableStateOf(0) }
var name by remember { mutableStateOf("") }
var isEnabled by remember { mutableStateOf(false) }
var price by remember { mutableStateOf(0.0) }
```

#### 2. Сложные типы

```kotlin
data class User(val id: String, val name: String, val age: Int)

var user by remember {
    mutableStateOf(User("1", "Алиса", 25))
}

// Обновление всего объекта
user = user.copy(age = 26)  // Вызывает рекомпозицию
```

#### 3. Коллекции

```kotlin
// Список
var items by remember { mutableStateOf(listOf<String>()) }
items = items + "Новый элемент"  // Вызывает рекомпозицию

// Использование mutableStateListOf для изменений на месте
val items = remember { mutableStateListOf<String>() }
items.add("Новый элемент")  // Вызывает рекомпозицию
```

---

### Подъем состояния

**Подъем состояния** = Перемещение состояния в родительский Composable для совместного использования.

```kotlin
@Composable
fun ParentScreen() {
    // Состояние поднято в родительский элемент
    var searchQuery by remember { mutableStateOf("") }

    Column {
        SearchBar(
            query = searchQuery,
            onQueryChange = { searchQuery = it }  // Родитель владеет состоянием
        )

        SearchResults(query = searchQuery)  // Общее состояние
    }
}

@Composable
fun SearchBar(
    query: String,
    onQueryChange: (String) -> Unit
) {
    TextField(
        value = query,
        onValueChange = onQueryChange
    )
}

@Composable
fun SearchResults(query: String) {
    Text("Поиск: $query")
}
```

**Преимущества:**
- **Единственный источник истины** - `searchQuery` принадлежит родителю
- **Переиспользуемость** - `SearchBar` и `SearchResults` не имеют состояния
- **Тестируемость** - Легче тестировать Composables без состояния

---

### Интеграция с ViewModel

```kotlin
class UserViewModel : ViewModel() {
    // Используйте StateFlow в ViewModel
    private val _user = MutableStateFlow(User("1", "Алиса", 25))
    val user: StateFlow<User> = _user.asStateFlow()

    fun updateAge(newAge: Int) {
        _user.value = _user.value.copy(age = newAge)
    }
}

@Composable
fun UserProfile(viewModel: UserViewModel = viewModel()) {
    // Преобразование StateFlow в State
    val user by viewModel.user.collectAsState()

    Column {
        Text("Имя: ${user.name}")
        Text("Возраст: ${user.age}")

        Button(onClick = { viewModel.updateAge(user.age + 1) }) {
            Text("Увеличить возраст")
        }
    }
}
```

---

### Оптимизация производительности

#### Умная рекомпозиция

Compose перекомпонует только **Composables, которые читают измененное состояние**.

```kotlin
@Composable
fun Screen() {
    var count1 by remember { mutableStateOf(0) }
    var count2 by remember { mutableStateOf(0) }

    Column {
        // Перекомпонуется только при изменении count1
        Text("Счетчик 1: $count1")

        // Перекомпонуется только при изменении count2
        Text("Счетчик 2: $count2")

        Button(onClick = { count1++ }) {
            Text("Увеличить счетчик 1")
        }

        Button(onClick = { count2++ }) {
            Text("Увеличить счетчик 2")
        }
    }
}
```

**Результат:**
- Клик "Увеличить счетчик 1" перекомпонует только `Text("Счетчик 1: $count1")`
- `Text("Счетчик 2: $count2")` НЕ перекомпонуется

---

### Резюме

**`MutableState<T>`:**
- **Наблюдаемая обертка** для состояния в Compose
- **Автоматически отслеживает изменения** и вызывает рекомпозицию
- **Типобезопасный** с generic `<T>`
- **Работает с `remember`** для сохранения между рекомпозициями

**Ключевые паттерны:**
- `remember { mutableStateOf(value) }` - Создать и запомнить состояние
- `var state by remember { mutableStateOf(value) }` - Делегирование для более чистого синтаксиса
- **Подъем состояния** - Перемещение состояния в родительский элемент для совместного использования
- **Интеграция с ViewModel** - Использование StateFlow, преобразование с `collectAsState()`

**Производительность:**
- Перекомпонует только Composables, которые **читают** измененное состояние
- Используйте `derivedStateOf` для дорогих вычислений



---

## Related Questions

### Hub
- [[q-jetpack-compose-basics--android--medium]] - Comprehensive Compose introduction

### Related (Medium)
- [[q-how-does-jetpack-compose-work--android--medium]] - How Compose works
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Essential Compose components
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - RecyclerView in Compose
- [[q-remember-vs-remembersaveable-compose--android--medium]] - remember vs rememberSaveable
- [[q-compose-remember-derived-state--jetpack-compose--medium]] - Derived state patterns

### Advanced (Harder)
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Stability & skippability
- [[q-stable-classes-compose--android--hard]] - @Stable annotation
- [[q-stable-annotation-compose--android--hard]] - Stability annotations

