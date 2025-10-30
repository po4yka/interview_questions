---
id: 20251030-120000
title: "How To Reduce Number Of Recompositions Besides Side Effects / Как уменьшить количество рекомпозиций кроме побочных эффектов"
aliases: ["Reduce Recompositions", "Уменьшить рекомпозиции", "Compose Performance", "Производительность Compose"]
topic: android
subtopics: [ui-compose, performance-rendering]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-compose-performance-optimization--android--hard, q-compose-stability-skippability--android--hard, q-recomposition-compose--android--medium, q-compose-remember-derived-state--android--medium]
created: 2025-10-15
updated: 2025-10-30
sources: []
tags: [android, android/ui-compose, android/performance-rendering, compose, recomposition, difficulty/hard]
---
# Вопрос (RU)

Как можно уменьшить количество рекомпозиций помимо side-эффектов?

# Question (EN)

How can you reduce the number of recompositions besides using side effects?

---

## Ответ (RU)

Уменьшение рекомпозиций улучшает производительность [[c-jetpack-compose]]. Ключевые техники: `remember`, `derivedStateOf`, стабильные data классы, immutable коллекции, правильное размещение состояния и использование `key()`.

### 1. Remember Для Дорогих Вычислений

```kotlin
@Composable
fun ExpensiveCalculation(items: List<Item>) {
    // ❌ Пересчитывает при каждой рекомпозиции
    val result = items.map { it.value * 2 }.sum()

    // ✅ Пересчитывает только при изменении items
    val result = remember(items) {
        items.map { it.value * 2 }.sum()
    }
}
```

### 2. derivedStateOf Для Производного Состояния

```kotlin
@Composable
fun SearchScreen() {
    var query by remember { mutableStateOf("") }
    val items = remember { List(1000) { "Item $it" } }

    // ❌ Фильтрует при каждой рекомпозиции
    val filteredItems = items.filter { it.contains(query, ignoreCase = true) }

    // ✅ Фильтрует только при изменении query
    val filteredItems by remember {
        derivedStateOf {
            items.filter { it.contains(query, ignoreCase = true) }
        }
    }
}
```

### 3. Стабильные Data Классы

```kotlin
// ❌ Нестабильный класс с mutable коллекцией
data class User(
    val name: String,
    val friends: MutableList<String>
)

// ✅ Стабильный класс с @Immutable
@Immutable
data class User(
    val name: String,
    val friends: List<String>
)

// ✅ Использование persistent коллекций
@Stable
data class User(
    val name: String,
    val friends: PersistentList<String>
)
```

### 4. Стабильные Ссылки На Лямбды

```kotlin
// ❌ Создает новую лямбду при каждой рекомпозиции
@Composable
fun ParentScreen(viewModel: ViewModel) {
    ChildScreen(onClick = { viewModel.handleClick() })
}

// ✅ Стабильная ссылка через remember
@Composable
fun ParentScreen(viewModel: ViewModel) {
    val onClick = remember { { viewModel.handleClick() } }
    ChildScreen(onClick = onClick)
}
```

### 5. Правильное Размещение Состояния

```kotlin
// ❌ Состояние слишком высоко
@Composable
fun BadParent() {
    var text1 by remember { mutableStateOf("") }
    var text2 by remember { mutableStateOf("") }

    Column {
        TextField(text1, { text1 = it })
        TextField(text2, { text2 = it })
        StaticContent() // Рекомпозируется при изменении любого текста
    }
}

// ✅ Состояние ближе к использованию
@Composable
fun GoodParent() {
    Column {
        TextFieldWithState()
        TextFieldWithState()
        StaticContent() // Не рекомпозируется
    }
}
```

### 6. key() В Списках

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn {
        items(
            items = users,
            key = { user -> user.id } // Стабильный ключ
        ) { user ->
            UserRow(user)
        }
    }
}
```

### 7. Минимизация Чтений Состояния

```kotlin
// ❌ Читает состояние в композиции
@Composable
fun BadCounter() {
    val count = remember { mutableStateOf(0) }

    Column {
        Text("Count: ${count.value}") // Рекомпозирует весь Column
        Button(onClick = { count.value++ }) { Text("Increment") }
    }
}

// ✅ Состояние читается только там, где нужно
@Composable
fun GoodCounter() {
    val count = remember { mutableStateOf(0) }

    Column {
        CountDisplay(count.value) // Только это рекомпозируется
        Button(onClick = { count.value++ }) { Text("Increment") }
    }
}
```

### 8. Immutable Коллекции

```kotlin
// Зависимость: kotlinx-collections-immutable

// ❌ Mutable список
@Composable
fun MutableListExample(items: MutableList<String>) {
    LazyColumn { items(items) { Text(it) } }
}

// ✅ Immutable список
@Composable
fun ImmutableListExample(items: ImmutableList<String>) {
    LazyColumn { items(items.size) { Text(items[it]) } }
}
```

### Чеклист Производительности

1. ✅ `remember` для дорогих вычислений
2. ✅ `derivedStateOf` для производного состояния
3. ✅ Стабильные `key()` в списках
4. ✅ Data классы с `@Immutable` или `@Stable`
5. ✅ Immutable коллекции
6. ✅ Состояние размещено правильно (не слишком высоко)
7. ✅ Стабильные ссылки на лямбды
8. ✅ Минимизация чтений состояния

### Отладка Рекомпозиций

```kotlin
@Composable
fun RecompositionCounter() {
    val count = remember { mutableStateOf(0) }

    SideEffect {
        count.value++
    }

    Text("Recompositions: ${count.value}")
}
```

## Answer (EN)

Reducing recompositions improves [[c-jetpack-compose]] performance. Key techniques: `remember`, `derivedStateOf`, stable data classes, immutable collections, proper state hoisting, and using `key()`.

### 1. Remember For Expensive Calculations

```kotlin
@Composable
fun ExpensiveCalculation(items: List<Item>) {
    // ❌ Recalculates on every recomposition
    val result = items.map { it.value * 2 }.sum()

    // ✅ Only recalculates when items change
    val result = remember(items) {
        items.map { it.value * 2 }.sum()
    }
}
```

### 2. derivedStateOf For Derived State

```kotlin
@Composable
fun SearchScreen() {
    var query by remember { mutableStateOf("") }
    val items = remember { List(1000) { "Item $it" } }

    // ❌ Filters on every recomposition
    val filteredItems = items.filter { it.contains(query, ignoreCase = true) }

    // ✅ Only filters when query changes
    val filteredItems by remember {
        derivedStateOf {
            items.filter { it.contains(query, ignoreCase = true) }
        }
    }
}
```

### 3. Stable Data Classes

```kotlin
// ❌ Unstable class with mutable collection
data class User(
    val name: String,
    val friends: MutableList<String>
)

// ✅ Stable class with @Immutable
@Immutable
data class User(
    val name: String,
    val friends: List<String>
)

// ✅ Using persistent collections
@Stable
data class User(
    val name: String,
    val friends: PersistentList<String>
)
```

### 4. Stable Lambda References

```kotlin
// ❌ Creates new lambda on each recomposition
@Composable
fun ParentScreen(viewModel: ViewModel) {
    ChildScreen(onClick = { viewModel.handleClick() })
}

// ✅ Stable reference with remember
@Composable
fun ParentScreen(viewModel: ViewModel) {
    val onClick = remember { { viewModel.handleClick() } }
    ChildScreen(onClick = onClick)
}
```

### 5. Proper State Hoisting

```kotlin
// ❌ State hoisted too high
@Composable
fun BadParent() {
    var text1 by remember { mutableStateOf("") }
    var text2 by remember { mutableStateOf("") }

    Column {
        TextField(text1, { text1 = it })
        TextField(text2, { text2 = it })
        StaticContent() // Recomposes when either text changes
    }
}

// ✅ State closer to usage
@Composable
fun GoodParent() {
    Column {
        TextFieldWithState()
        TextFieldWithState()
        StaticContent() // Doesn't recompose
    }
}
```

### 6. key() In Lists

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn {
        items(
            items = users,
            key = { user -> user.id } // Stable key
        ) { user ->
            UserRow(user)
        }
    }
}
```

### 7. Minimize State Reads

```kotlin
// ❌ Reads state in composition
@Composable
fun BadCounter() {
    val count = remember { mutableStateOf(0) }

    Column {
        Text("Count: ${count.value}") // Recomposes entire Column
        Button(onClick = { count.value++ }) { Text("Increment") }
    }
}

// ✅ State read only where needed
@Composable
fun GoodCounter() {
    val count = remember { mutableStateOf(0) }

    Column {
        CountDisplay(count.value) // Only this recomposes
        Button(onClick = { count.value++ }) { Text("Increment") }
    }
}
```

### 8. Immutable Collections

```kotlin
// Dependency: kotlinx-collections-immutable

// ❌ Mutable list
@Composable
fun MutableListExample(items: MutableList<String>) {
    LazyColumn { items(items) { Text(it) } }
}

// ✅ Immutable list
@Composable
fun ImmutableListExample(items: ImmutableList<String>) {
    LazyColumn { items(items.size) { Text(items[it]) } }
}
```

### Performance Checklist

1. ✅ Use `remember` for expensive calculations
2. ✅ Use `derivedStateOf` for derived state
3. ✅ Use stable `key()` in lists
4. ✅ Mark data classes with `@Immutable` or `@Stable`
5. ✅ Use immutable collections
6. ✅ Hoist state appropriately (not too high)
7. ✅ Create stable lambda references
8. ✅ Minimize state reads

### Debugging Recompositions

```kotlin
@Composable
fun RecompositionCounter() {
    val count = remember { mutableStateOf(0) }

    SideEffect {
        count.value++
    }

    Text("Recompositions: ${count.value}")
}
```

---

## Follow-ups

- How does Compose determine when to skip recomposition?
- What is the difference between `@Stable` and `@Immutable` annotations?
- How can you measure recomposition count in production?
- When should you use `key()` vs stable parameters?
- How do persistent collections improve Compose performance?

## References

- [[q-compose-stability-skippability--android--hard]] - Compose stability inference and skippability
- [[q-compose-performance-optimization--android--hard]] - Comprehensive performance optimization
- [[q-recomposition-compose--android--medium]] - Recomposition basics
- [[q-compose-remember-derived-state--android--medium]] - State management patterns
- [Jetpack Compose Performance](https://developer.android.com/jetpack/compose/performance)
- [Compose Stability](https://developer.android.com/jetpack/compose/performance/stability)

## Related Questions

### Prerequisites (Easier)
- [[q-recomposition-compose--android--medium]] - Understanding recomposition basics
- [[q-compose-remember-derived-state--android--medium]] - State management fundamentals

### Related (Same Level)
- [[q-compose-performance-optimization--android--hard]] - Comprehensive performance strategies
- [[q-compose-stability-skippability--android--hard]] - Stability and skippability details
- [[q-compose-slot-table-recomposition--android--hard]] - Internal recomposition mechanics

### Advanced
- [[q-compose-compiler-plugin--android--hard]] - Compiler optimizations
- [[q-derived-state-snapshot-system--android--hard]] - Advanced state management
