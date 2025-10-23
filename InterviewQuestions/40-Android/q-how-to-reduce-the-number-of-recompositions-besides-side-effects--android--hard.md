---
id: 20251012-1227194
title: "How To Reduce The Number Of Recompositions Besides Side Effects / Как уменьшить количество рекомпозиций кроме побочных эффектов"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-how-application-priority-is-determined-by-the-system--android--hard, q-compose-custom-animations--jetpack-compose--medium, q-clean-architecture-android--android--hard]
created: 2025-10-15
tags: [UI Optimization, android, ui, jetpack-compose, performance, difficulty/medium]
---
# How to reduce the number of recompositions besides side-effects?

# Вопрос (RU)

Как можно уменьшить количество рекомпозиций помимо side-эффектов

## Answer (EN)
Reducing recompositions in Jetpack Compose improves performance. Besides side effects, use `remember`, `derivedStateOf`, `key`, stable data classes, immutable collections, and proper state management.

### 1. Use remember for Expensive Calculations

```kotlin
@Composable
fun ExpensiveCalculation(items: List<Item>) {
    // - BAD: Recalculates on every recomposition
    val result = items.map { it.value * 2 }.sum()

    // - GOOD: Only recalculates when items change
    val result = remember(items) {
        items.map { it.value * 2 }.sum()
    }

    Text("Result: $result")
}
```

### 2. Use derivedStateOf for Derived State

```kotlin
@Composable
fun SearchScreen() {
    var query by remember { mutableStateOf("") }
    val items = remember { List(1000) { "Item $it" } }

    // - BAD: Filters on every recomposition
    val filteredItems = items.filter { it.contains(query, ignoreCase = true) }

    // - GOOD: Only filters when query changes
    val filteredItems by remember {
        derivedStateOf {
            items.filter { it.contains(query, ignoreCase = true) }
        }
    }

    LazyColumn {
        items(filteredItems) { item ->
            Text(item)
        }
    }
}
```

### 3. Use key() to Control Recomposition

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn {
        items(
            items = users,
            key = { user -> user.id } // Stable key prevents unnecessary recomposition
        ) { user ->
            UserRow(user)
        }
    }
}
```

### 4. Stable Data Classes

```kotlin
// - UNSTABLE: Compose can't determine if changed
data class User(
    val name: String,
    val friends: MutableList<String> // Mutable collection
)

// - STABLE: Compose can optimize
@Immutable // or @Stable
data class User(
    val name: String,
    val friends: List<String> // Immutable collection
)

// Use with persistentListOf from kotlinx.collections.immutable
@Stable
data class User(
    val name: String,
    val friends: PersistentList<String>
)
```

### 5. Avoid Lambdas in Composable Parameters

```kotlin
// - BAD: Creates new lambda on each recomposition
@Composable
fun ParentScreen(viewModel: ViewModel) {
    ChildScreen(
        onClick = { viewModel.handleClick() } // New lambda each time
    )
}

// - GOOD: Stable reference
@Composable
fun ParentScreen(viewModel: ViewModel) {
    val onClick = remember { { viewModel.handleClick() } }

    ChildScreen(onClick = onClick)
}

// - BETTER: Use rememberUpdatedState for changing values
@Composable
fun ParentScreen(count: Int, onComplete: () -> Unit) {
    val currentOnComplete by rememberUpdatedState(onComplete)

    ChildScreen(
        onClick = { currentOnComplete() }
    )
}
```

### 6. Hoist State Appropriately

```kotlin
// - BAD: Too much state in parent causes many recompositions
@Composable
fun BadParent() {
    var text1 by remember { mutableStateOf("") }
    var text2 by remember { mutableStateOf("") }

    Column {
        TextField(text1, { text1 = it })
        TextField(text2, { text2 = it })
        StaticContent() // Recomposes when either text changes!
    }
}

// - GOOD: Move state closer to usage
@Composable
fun GoodParent() {
    Column {
        TextFieldWithState()
        TextFieldWithState()
        StaticContent() // Doesn't recompose
    }
}

@Composable
fun TextFieldWithState() {
    var text by remember { mutableStateOf("") }
    TextField(text, { text = it })
}
```

### 7. Use Immutable Collections

```kotlin
// Add dependency: implementation("org.jetbrains.kotlinx:kotlinx-collections-immutable:0.3.5")

// - BAD: Mutable list
@Composable
fun MutableListExample(items: MutableList<String>) {
    LazyColumn {
        items(items) { item ->
            Text(item)
        }
    }
}

// - GOOD: Immutable list
@Composable
fun ImmutableListExample(items: ImmutableList<String>) {
    LazyColumn {
        items(items.size) { index ->
            Text(items[index])
        }
    }
}

// Using persistent collections
val items = persistentListOf("A", "B", "C")
val newItems = items.add("D") // Returns new list, original unchanged
```

### 8. Skip Recomposition with Stable Parameters

```kotlin
// Mark functions as stable
@Stable
interface Repository {
    fun getData(): Flow<Data>
}

@Composable
fun DataScreen(repository: Repository) {
    val data by repository.getData().collectAsState(initial = null)

    data?.let {
        DataView(it)
    }
}

// Use @Immutable for data classes
@Immutable
data class Config(
    val title: String,
    val isEnabled: Boolean
)
```

### 9. Avoid Unnecessary State Reads

```kotlin
// - BAD: Reads state in composition
@Composable
fun BadCounter() {
    val count = remember { mutableStateOf(0) }

    Column {
        Text("Count: ${count.value}") // Recomposes entire Column
        Button(onClick = { count.value++ }) {
            Text("Increment")
        }
    }
}

// - GOOD: Read state only where needed
@Composable
fun GoodCounter() {
    val count = remember { mutableStateOf(0) }

    Column {
        CountDisplay(count.value) // Only this recomposes
        Button(onClick = { count.value++ }) {
            Text("Increment")
        }
    }
}

@Composable
fun CountDisplay(count: Int) {
    Text("Count: $count")
}
```

### 10. Use rememberSaveable for State

```kotlin
@Composable
fun PersistentState() {
    // Survives configuration changes
    var text by rememberSaveable { mutableStateOf("") }

    TextField(
        value = text,
        onValueChange = { text = it }
    )
}
```

### 11. Lazy State Initialization

```kotlin
@Composable
fun LazyInit() {
    // Only creates once
    val expensiveObject = remember {
        ExpensiveObject()
    }

    // Only fetches data once
    val data by produceState<Data?>(initialValue = null) {
        value = fetchData()
    }
}
```

### 12. Memoize Composables with key()

```kotlin
@Composable
fun DynamicList(items: List<Item>, selectedId: String) {
    LazyColumn {
        items(
            items = items,
            key = { it.id }
        ) { item ->
            key(item.id, selectedId) { // Additional key for selected state
                ItemRow(
                    item = item,
                    isSelected = item.id == selectedId
                )
            }
        }
    }
}
```

### Performance Checklist

1. - Use `remember` for expensive calculations
2. - Use `derivedStateOf` for derived state
3. - Use stable `key()` in lists
4. - Make data classes `@Immutable` or `@Stable`
5. - Use immutable collections
6. - Hoist state appropriately (not too high)
7. - Avoid creating lambdas in composable body
8. - Read state only where needed
9. - Use `rememberSaveable` for persistence
10. - Minimize state dependencies

### Debugging Recompositions

```kotlin
@Composable
fun RecompositionCounter() {
    val recomposeCount = remember { mutableStateOf(0) }

    SideEffect {
        recomposeCount.value++
    }

    Text("Recompositions: ${recomposeCount.value}")
}
```

## Ответ (RU)

Уменьшение количества рекомпозиций в Jetpack Compose улучшает производительность. Помимо side effects, используйте `remember`, `derivedStateOf`, `key`, стабильные data классы, immutable коллекции и правильное управление состоянием.

### Основные техники оптимизации

**1. remember для дорогих вычислений** - кэширует результаты и пересчитывает только при изменении зависимостей.

**2. derivedStateOf для производного состояния** - создает производное состояние, которое обновляется только при изменении источников.

**3. key() для контроля рекомпозиции** - использование стабильных ключей в списках предотвращает ненужные рекомпозиции элементов.

**4. Стабильные типы данных** - отмечайте классы как `@Immutable` или `@Stable`, используйте неизменяемые коллекции.

**5. Избегайте создания лямбд** - используйте `remember` для кэширования callback функций или `rememberUpdatedState` для изменяющихся значений.

**6. Правильное поднятие состояния** - размещайте состояние как можно ближе к месту использования, а не слишком высоко в иерархии.

**7. Immutable коллекции** - используйте `kotlinx.collections.immutable` для гарантированной неизменяемости.

**8. Минимизация чтений состояния** - читайте состояние только в тех composable, которые действительно должны реагировать на изменения.

### Практические рекомендации

- Используйте `rememberSaveable` для состояния, которое должно пережить конфигурационные изменения
- Применяйте ленивую инициализацию с `remember` для дорогих объектов
- Используйте `SideEffect` для отладки и подсчета рекомпозиций
- Проверяйте стабильность типов с помощью Compose Compiler Reports
- Минимизируйте зависимости состояния в composable функциях

### Резюме

Ключевые принципы: кэширование вычислений (`remember`), производное состояние (`derivedStateOf`), стабильные ключи и типы (`@Stable`, `@Immutable`), правильное управление состоянием, избегание ненужных пересозданий объектов и функций. Все это в совокупности значительно сокращает количество рекомпозиций и улучшает производительность приложения

---

## Related Questions

### Related (Medium)
- [[q-how-does-jetpackcompose-work--android--medium]] - Compose
- [[q-compose-modifier-order-performance--android--medium]] - Compose
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Compose
- [[q-compositionlocal-advanced--android--medium]] - Compose
- [[q-accessibility-compose--android--medium]] - Compose

### Advanced (Harder)
- [[q-compose-side-effects-advanced--android--hard]] - Compose
- [[q-compose-side-effects-launchedeffect-disposableeffect--android--hard]] - Compose
- [[q-compose-stability-skippability--android--hard]] - Compose
