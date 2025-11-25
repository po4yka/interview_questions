---
id: android-204
title: "MutableState в Compose / MutableState in Compose"
aliases: ["Compose State Management", "MutableState in Compose", "MutableState в Compose", "Изменяемое состояние Compose"]
topic: android
subtopics: [ui-compose, ui-state]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-state, c-jetpack-compose, q-compose-remember-derived-state--android--medium, q-remember-vs-remembersaveable-compose--android--medium, q-state-hoisting-compose--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android/ui-compose, android/ui-state, difficulty/medium, jetpack-compose, recomposition, state-management]
sources: []

date created: Saturday, November 1st 2025, 12:46:59 pm
date modified: Tuesday, November 25th 2025, 8:53:58 pm
---

# Вопрос (RU)

> Что такое `MutableState` в Compose?

# Question (EN)

> What is `MutableState` in Compose?

---

## Ответ (RU)

**`MutableState<T>`** — это обёртка для хранения состояния в Jetpack Compose, которая автоматически отслеживает изменения и инициирует рекомпозицию при изменении значения.

### Основная Концепция

```kotlin
interface MutableState<T> : State<T> {
    override var value: T
}
```

**Ключевые характеристики:**
- **`Observable`** — автоматически уведомляет подписчиков
- **Триггерит рекомпозицию** — UI-элементы перерисовываются при изменении значения
- **Типобезопасность** — строгая типизация через `<T>`
- **Переживает рекомпозицию** — при корректном размещении (например, внутри `remember`) значение не теряется между рекомпозициями

### Создание Состояния

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

### Как Работает Отслеживание

Compose автоматически отслеживает, какие composable-функции читают состояние, и подписывает соответствующие участки дерева на его изменения.

```kotlin
@Composable
fun UserProfile() {
    var name by remember { mutableStateOf("") }
    var age by remember { mutableStateOf(0) }

    Column {
        Text("Имя: $name")  // ✅ Рекомпозируется при изменении name
        Text("Возраст: $age")  // ✅ Рекомпозируется при изменении age

        Button(onClick = { name = "John" }) {
            Text("Изменить имя")
        }
    }
}
```

При изменении `name` будет запланирована рекомпозиция для той части композиции, где читается `name` (и её поддерева); аналогично для `age`. Гранулярность рекомпозиции зависит от структуры composable-функций.

### MutableState Vs Обычная Переменная

**❌ Обычная переменная:**
```kotlin
@Composable
fun Counter() {
    var count = 0  // ❌ Не работает как состояние

    Button(onClick = { count++ }) {  // count меняется, но UI не обновляется
        Text("Count: $count")
    }
}
```

**✅ MutableState:**
```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }  // ✅ Работает как состояние

    Button(onClick = { count++ }) {  // Триггерит рекомпозицию для чтений count
        Text("Count: $count")
    }
}
```

### Remember Vs Без Remember

Важно, где создаётся `MutableState`:

**Проблемный случай внутри composable без remember:**
```kotlin
@Composable
fun Counter() {
    var count by mutableStateOf(0)  // ⚠️ Состояние создаётся заново при каждом вызове функции

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

Такой код будет работать некорректно как "счётчик", потому что при каждом новом запуске композиции создаётся новый экземпляр состояния. Обычно здесь следует использовать `remember`:

**✅ С remember внутри composable:**
```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }  // ✅ Сохраняется между рекомпозициями

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

**✅ Без remember на устойчивом уровне:**
```kotlin
class CounterState {
    var count by mutableStateOf(0)  // ✅ Можно хранить в ViewModel или state-holder классе
}
```

Здесь `mutableStateOf` используется корректно, потому что объект `CounterState` живёт дольше одной рекомпозиции.

### Типы Состояний

**Примитивы:**
```kotlin
var count by remember { mutableStateOf(0) }
var name by remember { mutableStateOf("") }
var isEnabled by remember { mutableStateOf(false) }
```

**Объекты:**
```kotlin
data class User(val id: String, val name: String, val age: Int)

var user by remember { mutableStateOf(User("1", "Alice", 25)) }
user = user.copy(age = 26)  // ✅ Создаёт новый объект, триггерит рекомпозицию
```

**Коллекции:**
```kotlin
// ✅ Неизменяемый список
var items by remember { mutableStateOf(listOf<String>()) }
items = items + "Новый элемент"  // Создаёт новый список

// ✅ Наблюдаемый изменяемый список
val items = remember { mutableStateListOf<String>() }
items.add("Новый элемент")  // Триггерит рекомпозицию напрямую
```

### Подъём Состояния (State Hoisting)

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
- Переиспользуемые stateless-компоненты
- Простое тестирование

### Интеграция С `ViewModel`

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
    val user by viewModel.user.collectAsState()  // ✅ StateFlow → State, используется аналогично MutableState

    Column {
        Text("Возраст: ${user.age}")
        Button(onClick = { viewModel.updateAge(user.age + 1) }) {
            Text("Увеличить возраст")
        }
    }
}
```

Здесь `ViewModel` использует состояние на основе `Flow`, которое в UI представлено как Compose-`State`. С точки зрения подписки и рекомпозиции оно ведёт себя аналогично `MutableState`.

### Оптимизация Производительности

**Умная рекомпозиция:**
Compose пытается рекомпозировать только те части дерева, которые читают изменившееся состояние (и их поддеревья), исходя из границ composable-функций.

```kotlin
@Composable
fun Screen() {
    var count1 by remember { mutableStateOf(0) }
    var count2 by remember { mutableStateOf(0) }

    Column {
        Text("Count 1: $count1")  // ✅ Рекомпозируется при изменении count1
        Text("Count 2: $count2")  // ✅ Рекомпозируется при изменении count2
    }
}
```

**derivedStateOf для вычислений:**
```kotlin
@Composable
fun ItemList(items: List<Item>) {
    var filter by remember { mutableStateOf("") }

    // ✅ Пересчитывается только когда items или filter изменились
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
- **`Observable`** — automatically notifies dependents
- **Triggers recomposition** — UI elements are redrawn when the value changes
- **Type-safe** — strongly typed via `<T>`
- **Survives recomposition** — when placed correctly (e.g., inside `remember`), the value is preserved across recompositions

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

Compose automatically tracks which composable functions read a given state and schedules recomposition for those parts of the composition tree when the state changes.

```kotlin
@Composable
fun UserProfile() {
    var name by remember { mutableStateOf("") }
    var age by remember { mutableStateOf(0) }

    Column {
        Text("Name: $name")  // ✅ Recomposes when name changes
        Text("Age: $age")    // ✅ Recomposes when age changes

        Button(onClick = { name = "John" }) {
            Text("Change Name")
        }
    }
}
```

When `name` changes, Compose schedules recomposition for the scope where `name` is read (and its subtree); similarly for `age`. The exact granularity depends on how your composables are structured.

### MutableState Vs Regular Variable

**❌ Regular variable:**
```kotlin
@Composable
fun Counter() {
    var count = 0  // ❌ Not treated as state

    Button(onClick = { count++ }) {  // count changes, but UI doesn't update
        Text("Count: $count")
    }
}
```

**✅ MutableState:**
```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }  // ✅ Works as state

    Button(onClick = { count++ }) {  // Triggers recomposition for readers of count
        Text("Count: $count")
    }
}
```

### Remember Vs Without Remember

What matters is where `MutableState` is created:

**Problematic case inside a composable without remember:**
```kotlin
@Composable
fun Counter() {
    var count by mutableStateOf(0)  // ⚠️ New state instance created on each invocation

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

This won't behave as a stable counter because each new composition pass creates a new state instance. In this scenario you should use `remember`:

**✅ With remember inside a composable:**
```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }  // ✅ Preserved across recompositions

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

**✅ Without remember at a stable scope:**
```kotlin
class CounterState {
    var count by mutableStateOf(0)  // ✅ Safe when the holder outlives individual recompositions
}
```

Here `mutableStateOf` is used correctly because the `CounterState` instance is not recreated on each recomposition (e.g., it's stored in a `ViewModel` or other state holder).

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
items = items + "New Item"  // Creates a new list

// ✅ Mutable observable list
val items = remember { mutableStateListOf<String>() }
items.add("New Item")  // Triggers recomposition directly
```

### State Hoisting

**Pattern:** state lives in the parent and is passed down via parameters.

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
- Easier testing

### `ViewModel` Integration

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
    val user by viewModel.user.collectAsState()  // ✅ StateFlow → State, consumed similarly to MutableState

    Column {
        Text("Age: ${user.age}")
        Button(onClick = { viewModel.updateAge(user.age + 1) }) {
            Text("Increment Age")
        }
    }
}
```

Here the `ViewModel` exposes `Flow`-based state, which is collected into a Compose `State`. From the UI perspective it behaves similarly to `MutableState` regarding observation and recomposition.

### Performance Optimization

**Smart Recomposition:**
Compose attempts to recompose only those parts of the UI tree that read the changed state (and their subtrees), based on composable function boundaries.

```kotlin
@Composable
fun Screen() {
    var count1 by remember { mutableStateOf(0) }
    var count2 by remember { mutableStateOf(0) }

    Column {
        Text("Count 1: $count1")  // ✅ Recomposes when count1 changes
        Text("Count 2: $count2")  // ✅ Recomposes when count2 changes
    }
}
```

**derivedStateOf for Calculations:**
```kotlin
@Composable
fun ItemList(items: List<Item>) {
    var filter by remember { mutableStateOf("") }

    // ✅ Recalculates only when items or filter change
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

## Дополнительные Вопросы (RU)

1. Когда следует использовать `rememberSaveable` вместо `remember`?
2. Чем `derivedStateOf` отличается от вычисляемых свойств или простых геттеров?
3. Что произойдёт, если забыть использовать `remember` с `mutableStateOf` внутри composable?
4. Как разделять состояние между несколькими экранами в навигации Compose?
5. Каковы последствия для производительности при хранении больших объектов в `MutableState`?

## Follow-ups

1. When should you use `rememberSaveable` instead of `remember`?
2. How does `derivedStateOf` differ from computed properties?
3. What happens if you forget to use `remember` with `mutableStateOf` inside a composable?
4. How do you share state between multiple screens in Compose Navigation?
5. What are the performance implications of putting large objects in `MutableState`?

## Источники (RU)

- [[c-compose-state]] — концепции управления состоянием в Compose
- [[c-jetpack-compose]] — основы Jetpack Compose
- [[c-compose-recomposition]] — механика рекомпозиции
- "State in Compose" в официальной документации: https://developer.android.com/jetpack/compose/state
- Ментальная модель Compose: https://developer.android.com/jetpack/compose/mental-model

## References

- [[c-compose-state]] - Compose state management concepts
- [[c-jetpack-compose]] - Jetpack Compose fundamentals
- [[c-compose-recomposition]] - Recomposition mechanics
- https://developer.android.com/jetpack/compose/state
- https://developer.android.com/jetpack/compose/mental-model

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-jetpack-compose-basics--android--medium]] - основы Compose

### Связанные (такой Же уровень)
- [[q-state-hoisting-compose--android--medium]] - паттерны подъёма состояния
- [[q-remember-vs-remembersaveable-compose--android--medium]] - варианты `remember`
- [[q-compose-remember-derived-state--android--medium]] - использование `derivedStateOf`
- [[q-recomposition-compose--android--medium]] - механика рекомпозиции
- [[q-how-mutablestate-notifies--android--medium]] - как `MutableState` уведомляет об изменениях

### Продвинутое (сложнее)
- [[q-compose-stability-skippability--android--hard]] - стабильность и возможность пропуска рекомпозиции
- [[q-stable-classes-compose--android--hard]] - аннотация `@Stable`
- [[q-compose-performance-optimization--android--hard]] - оптимизация производительности

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
