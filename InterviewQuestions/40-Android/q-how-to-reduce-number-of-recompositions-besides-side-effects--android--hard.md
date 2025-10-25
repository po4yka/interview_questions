---
id: 20251012-1227193
title: "How To Reduce Number Of Recompositions Besides Side Effects / Как уменьшить количество рекомпозиций кроме побочных эффектов"
topic: android
difficulty: hard
status: draft
moc: moc-android
related: [q-architecture-components-libraries--android--easy, q-compose-ui-testing-advanced--testing--hard, q-what-is-hilt--android--medium]
created: 2025-10-15
tags: [android, difficulty/hard, languages]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:11:20 pm
---

# Как Можно Уменьшить Количество Рекомпозиций Помимо Side-эффектов?

## Answer (EN)
Reducing recompositions in Jetpack Compose improves performance. Besides side effects, use `remember`, `derivedStateOf`, `key`, stable data classes, immutable collections, and proper state management.

### 1. Use Remember for Expensive Calculations

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

---

# Как Можно Уменьшить Количество Рекомпозиций Помимо Side-эффектов

## Ответ (RU)

Уменьшение количества рекомпозиций в Jetpack Compose улучшает производительность. Помимо side effects, используйте `remember`, `derivedStateOf`, `key`, стабильные data классы, immutable коллекции и правильное управление состоянием.

### 1. Использование Remember Для Дорогих Вычислений

```kotlin
@Composable
fun ExpensiveCalculation(items: List<Item>) {
    // - ПЛОХО: Пересчитывает при каждой рекомпозиции
    val result = items.map { it.value * 2 }.sum()

    // - ХОРОШО: Пересчитывает только при изменении items
    val result = remember(items) {
        items.map { it.value * 2 }.sum()
    }

    Text("Result: $result")
}
```

### 2. Использование derivedStateOf Для Производного Состояния

```kotlin
@Composable
fun SearchScreen() {
    var query by remember { mutableStateOf("") }
    val items = remember { List(1000) { "Item $it" } }

    // - ПЛОХО: Фильтрует при каждой рекомпозиции
    val filteredItems = items.filter { it.contains(query, ignoreCase = true) }

    // - ХОРОШО: Фильтрует только при изменении query
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

### 3. Использование key() Для Контроля Рекомпозиции

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn {
        items(
            items = users,
            key = { user -> user.id } // Стабильный ключ предотвращает ненужные рекомпозиции
        ) { user ->
            UserRow(user)
        }
    }
}
```

### 4. Стабильные Data Классы

```kotlin
// - НЕСТАБИЛЬНЫЙ: Compose не может определить изменения
data class User(
    val name: String,
    val friends: MutableList<String> // Изменяемая коллекция
)

// - СТАБИЛЬНЫЙ: Compose может оптимизировать
@Immutable // или @Stable
data class User(
    val name: String,
    val friends: List<String> // Неизменяемая коллекция
)

// Использование с persistentListOf из kotlinx.collections.immutable
@Stable
data class User(
    val name: String,
    val friends: PersistentList<String>
)
```

### 5. Избегайте Лямбд В Параметрах Composable

```kotlin
// - ПЛОХО: Создает новую лямбду при каждой рекомпозиции
@Composable
fun ParentScreen(viewModel: ViewModel) {
    ChildScreen(
        onClick = { viewModel.handleClick() } // Новая лямбда каждый раз
    )
}

// - ХОРОШО: Стабильная ссылка
@Composable
fun ParentScreen(viewModel: ViewModel) {
    val onClick = remember { { viewModel.handleClick() } }

    ChildScreen(onClick = onClick)
}

// - ЛУЧШЕ: Использование rememberUpdatedState для изменяющихся значений
@Composable
fun ParentScreen(count: Int, onComplete: () -> Unit) {
    val currentOnComplete by rememberUpdatedState(onComplete)

    ChildScreen(
        onClick = { currentOnComplete() }
    )
}
```

### 6. Правильное Поднятие Состояния

```kotlin
// - ПЛОХО: Слишком много состояния в родителе вызывает много рекомпозиций
@Composable
fun BadParent() {
    var text1 by remember { mutableStateOf("") }
    var text2 by remember { mutableStateOf("") }

    Column {
        TextField(text1, { text1 = it })
        TextField(text2, { text2 = it })
        StaticContent() // Рекомпозируется при изменении любого текста!
    }
}

// - ХОРОШО: Переместить состояние ближе к использованию
@Composable
fun GoodParent() {
    Column {
        TextFieldWithState()
        TextFieldWithState()
        StaticContent() // Не рекомпозируется
    }
}

@Composable
fun TextFieldWithState() {
    var text by remember { mutableStateOf("") }
    TextField(text, { text = it })
}
```

### 7. Использование Immutable Коллекций

```kotlin
// Добавьте зависимость: implementation("org.jetbrains.kotlinx:kotlinx-collections-immutable:0.3.5")

// - ПЛОХО: Изменяемый список
@Composable
fun MutableListExample(items: MutableList<String>) {
    LazyColumn {
        items(items) { item ->
            Text(item)
        }
    }
}

// - ХОРОШО: Неизменяемый список
@Composable
fun ImmutableListExample(items: ImmutableList<String>) {
    LazyColumn {
        items(items.size) { index ->
            Text(items[index])
        }
    }
}

// Использование persistent коллекций
val items = persistentListOf("A", "B", "C")
val newItems = items.add("D") // Возвращает новый список, оригинал неизменен
```

### 8. Пропуск Рекомпозиции С Стабильными Параметрами

```kotlin
// Отмечайте функции как стабильные
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

// Используйте @Immutable для data классов
@Immutable
data class Config(
    val title: String,
    val isEnabled: Boolean
)
```

### 9. Избегайте Ненужных Чтений Состояния

```kotlin
// - ПЛОХО: Читает состояние в композиции
@Composable
fun BadCounter() {
    val count = remember { mutableStateOf(0) }

    Column {
        Text("Count: ${count.value}") // Рекомпозирует весь Column
        Button(onClick = { count.value++ }) {
            Text("Increment")
        }
    }
}

// - ХОРОШО: Читать состояние только там, где нужно
@Composable
fun GoodCounter() {
    val count = remember { mutableStateOf(0) }

    Column {
        CountDisplay(count.value) // Только это рекомпозируется
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

### 10. Использование rememberSaveable Для Состояния

```kotlin
@Composable
fun PersistentState() {
    // Переживает изменения конфигурации
    var text by rememberSaveable { mutableStateOf("") }

    TextField(
        value = text,
        onValueChange = { text = it }
    )
}
```

### 11. Ленивая Инициализация Состояния

```kotlin
@Composable
fun LazyInit() {
    // Создается только один раз
    val expensiveObject = remember {
        ExpensiveObject()
    }

    // Данные загружаются только один раз
    val data by produceState<Data?>(initialValue = null) {
        value = fetchData()
    }
}
```

### 12. Мемоизация Composable С Помощью key()

```kotlin
@Composable
fun DynamicList(items: List<Item>, selectedId: String) {
    LazyColumn {
        items(
            items = items,
            key = { it.id }
        ) { item ->
            key(item.id, selectedId) { // Дополнительный ключ для выбранного состояния
                ItemRow(
                    item = item,
                    isSelected = item.id == selectedId
                )
            }
        }
    }
}
```

### Чеклист Производительности

1. - Используйте `remember` для дорогих вычислений
2. - Используйте `derivedStateOf` для производного состояния
3. - Используйте стабильный `key()` в списках
4. - Делайте data классы `@Immutable` или `@Stable`
5. - Используйте immutable коллекции
6. - Поднимайте состояние правильно (не слишком высоко)
7. - Избегайте создания лямбд в теле composable
8. - Читайте состояние только там, где нужно
9. - Используйте `rememberSaveable` для персистентности
10. - Минимизируйте зависимости состояния

### Отладка Рекомпозиций

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

## Related Questions

- [[q-what-is-hilt--android--medium]]
- [[q-compose-ui-testing-advanced--testing--hard]]
- [[q-architecture-components-libraries--android--easy]]
