---
id: android-060
title: "Recomposition in Compose / Рекомпозиция в Compose"
aliases: [Compose Recomposition, Recomposition, Рекомпозиция, Рекомпозиция Compose]
topic: android
subtopics: [performance-rendering, ui-compose, ui-state]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, q-compose-performance-optimization--android--hard, q-jetpack-compose-basics--android--medium]
created: 2025-10-12
updated: 2025-10-27
sources: [https://developer.android.com/jetpack/compose/lifecycle]
tags: [android/performance-rendering, android/ui-compose, android/ui-state, difficulty/medium, jetpack-compose, performance, recomposition, state]
---

# Вопрос (RU)

> Что такое рекомпозиция в Jetpack Compose? Что триггерит рекомпозицию и как Compose решает какие composable нужно перерисовать?

# Question (EN)

> What is recomposition in Jetpack Compose? What triggers recomposition, and how does Compose decide which composables need to recompose?

---

## Ответ (RU)

**Рекомпозиция** — процесс повторного выполнения composable функций при изменении параметров или состояния. См. [[c-jetpack-compose]].

### Как Работает

В отличие от `View` (`textView.text = "new"`), Compose перезапускает функцию с новыми данными:

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Нажато $count раз") // ✅ Рекомпозиция при изменении count
    }
}
```

**Что происходит:**
1. Клик → `count` меняется с 0 на 1
2. Compose обнаруживает изменение
3. Функция `Counter()` выполняется заново
4. UI обновляется

### Что Триггерит Рекомпозицию?

#### 1. Изменения State

```kotlin
@Composable
fun UserProfile(viewModel: ProfileViewModel) {
    val user by viewModel.user.collectAsState() // ✅ Наблюдает за Flow

    Column {
        Text(user.name) // ✅ Рекомпозиция при изменении user
        Text(user.email)
    }
}
```

**Триггеры:**
- `mutableStateOf` changes
- `collectAsState()` emits from `Flow`
- `observeAsState()` for `LiveData`

#### 2. Изменения Параметров

```kotlin
@Composable
fun Greeting(name: String) { // ✅ Рекомпозиция при изменении name
    Text("Привет, $name!")
}

@Composable
fun Parent() {
    var name by remember { mutableStateOf("Алиса") }
    Greeting(name = name)
    Button(onClick = { name = "Боб" }) {
        Text("Изменить имя")
    }
}
```

### Область Рекомпозиции (Scoping)

Compose делает рекомпозицию **в максимально узкой области**:

```kotlin
@Composable
fun Screen() {
    var topCounter by remember { mutableStateOf(0) }
    var bottomCounter by remember { mutableStateOf(0) }

    Column {
        Text("Top: $topCounter") // ✅ Только это при изменении topCounter
        Button(onClick = { topCounter++ }) { Text("Top") }

        Text("Bottom: $bottomCounter") // ✅ Только это при изменении bottomCounter
        Button(onClick = { bottomCounter++ }) { Text("Bottom") }
    }
}
```

### Стабильность И Пропуск Рекомпозиции

Compose **пропускает рекомпозицию** если параметры стабильны и не изменились:

```kotlin
// ✅ Стабильно: Примитивы
@Composable
fun Counter(count: Int) // Пропускает если count не изменился

// ✅ Стабильно: @Immutable
@Immutable
data class User(val id: String, val name: String)

@Composable
fun UserCard(user: User) // Пропускает если user тот же экземпляр

// ❌ Нестабильно: List
@Composable
fun ItemList(items: List<Item>) // ВСЕГДА делает рекомпозицию
```

**Почему `List` нестабилен?** Kotlin's `List` = `java.util.List`, может быть изменён извне.

#### Решение: Сделать Стабильным

```kotlin
// Option 1: @Stable wrapper
@Stable
data class ItemsState(val items: List<Item>)

// Option 2: ImmutableList
import kotlinx.collections.immutable.ImmutableList

@Composable
fun ItemList(items: ImmutableList<Item>) // ✅ Стабильно
```

### Контроль Рекомпозиции

#### 1. `remember {}` — Сохранить Между Рекомпозициями

```kotlin
@Composable
fun ExpensiveCalculation() {
    // ❌ ПЛОХО: Пересчитывает каждый раз
    val result = expensiveComputation()

    // ✅ ХОРОШО: Вычисляет только один раз
    val result = remember { expensiveComputation() }
}
```

#### 2. `remember(key) {}` — Пересчёт При Изменении Ключа

```kotlin
@Composable
fun FilteredList(items: List<Item>, query: String) {
    // ✅ Пересчёт ТОЛЬКО при изменении query
    val filteredItems = remember(query) {
        items.filter { it.name.contains(query, ignoreCase = true) }
    }

    LazyColumn {
        items(filteredItems, key = { it.id }) { item ->
            ItemCard(item)
        }
    }
}
```

#### 3. `derivedStateOf {}` — Вычисляемое Состояние

```kotlin
@Composable
fun ScrollToTopButton(listState: LazyListState) {
    // ❌ ПЛОХО: Рекомпозиция на КАЖДЫЙ пиксель
    val showButton = listState.firstVisibleItemIndex > 0

    // ✅ ХОРОШО: Только при пересечении порога
    val showButton by remember {
        derivedStateOf {
            listState.firstVisibleItemIndex > 0
        }
    }

    AnimatedVisibility(visible = showButton) {
        FloatingActionButton(onClick = { /* scroll */ }) {
            Icon(Icons.Default.ArrowUpward, null)
        }
    }
}
```

**Почему?** `derivedStateOf` батчит изменения и уведомляет только при изменении boolean результата.

### Распространённые Ошибки

#### 1. Нестабильность Лямбд

```kotlin
// ❌ ПЛОХО: Новая лямбда каждый раз
@Composable
fun BadButton(viewModel: ViewModel) {
    Button(onClick = { viewModel.doAction() }) {
        Text("Клик")
    }
}

// ✅ ХОРОШО: Ссылка на метод стабильна
@Composable
fun GoodButton(viewModel: ViewModel) {
    Button(onClick = viewModel::doAction) {
        Text("Клик")
    }
}
```

#### 2. Чтение Состояния Слишком Высоко

```kotlin
// ❌ ПЛОХО: Вся Column делает рекомпозицию
@Composable
fun BadExample(viewModel: ViewModel) {
    val uiState by viewModel.uiState.collectAsState()

    Column {
        Text(uiState.title)
        ExpensiveComponent() // ❌ Ненужная рекомпозиция
        Text(uiState.subtitle)
    }
}

// ✅ ХОРОШО: Узкая область
@Composable
fun GoodExample(viewModel: ViewModel) {
    Column {
        TitleText(viewModel) // ✅ Независимая рекомпозиция
        ExpensiveComponent() // ✅ Никогда не делает рекомпозицию
        SubtitleText(viewModel)
    }
}
```

### Best Practices

1. **State hoisting** — поднимать к ближайшему общему предку
2. **Стабильные параметры** — `@Immutable` и `@Stable`
3. **Узкая область** — читать состояние близко к использованию
4. **Ключи в списках** — `key` в `items()`
5. **Derived state** — `derivedStateOf` для вычислений
6. **Remember дорогих операций** — кэшировать с `remember`
7. **Ссылки на методы** — `viewModel::action` вместо `{ viewModel.action() }`

---

## Answer (EN)

**Recomposition** is re-executing composable functions when parameters or observed state changes. See [[c-jetpack-compose]].

### How it Works

Unlike `View` (`textView.text = "new"`), Compose re-runs the function with new data:

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Clicked $count times") // ✅ Recomposes when count changes
    }
}
```

**What happens:**
1. Click → `count` changes from 0 to 1
2. Compose detects change
3. `Counter()` re-executes
4. UI updates

### What Triggers Recomposition?

#### 1. State Changes

```kotlin
@Composable
fun UserProfile(viewModel: ProfileViewModel) {
    val user by viewModel.user.collectAsState() // ✅ Observes Flow

    Column {
        Text(user.name) // ✅ Recomposes when user changes
        Text(user.email)
    }
}
```

**Triggers:**
- `mutableStateOf` changes
- `collectAsState()` emits from `Flow`
- `observeAsState()` for `LiveData`

#### 2. Parameter Changes

```kotlin
@Composable
fun Greeting(name: String) { // ✅ Recomposes when name changes
    Text("Hello, $name!")
}

@Composable
fun Parent() {
    var name by remember { mutableStateOf("Alice") }
    Greeting(name = name)
    Button(onClick = { name = "Bob" }) {
        Text("Change Name")
    }
}
```

### Recomposition Scoping

Compose recomposes at the **narrowest scope possible**:

```kotlin
@Composable
fun Screen() {
    var topCounter by remember { mutableStateOf(0) }
    var bottomCounter by remember { mutableStateOf(0) }

    Column {
        Text("Top: $topCounter") // ✅ Only this when topCounter changes
        Button(onClick = { topCounter++ }) { Text("Top") }

        Text("Bottom: $bottomCounter") // ✅ Only this when bottomCounter changes
        Button(onClick = { bottomCounter++ }) { Text("Bottom") }
    }
}
```

### Stability and Skipping

Compose **skips recomposition** if parameters are stable and unchanged:

```kotlin
// ✅ Stable: Primitives
@Composable
fun Counter(count: Int) // Skips if count unchanged

// ✅ Stable: @Immutable
@Immutable
data class User(val id: String, val name: String)

@Composable
fun UserCard(user: User) // Skips if same instance

// ❌ Unstable: List
@Composable
fun ItemList(items: List<Item>) // ALWAYS recomposes
```

**Why is `List` unstable?** Kotlin's `List` = `java.util.List`, could be mutated elsewhere.

#### Solution: Make Stable

```kotlin
// Option 1: @Stable wrapper
@Stable
data class ItemsState(val items: List<Item>)

// Option 2: ImmutableList
import kotlinx.collections.immutable.ImmutableList

@Composable
fun ItemList(items: ImmutableList<Item>) // ✅ Stable
```

### Controlling Recomposition

#### 1. `remember {}` — Preserve Across Recompositions

```kotlin
@Composable
fun ExpensiveCalculation() {
    // ❌ BAD: Recalculates every time
    val result = expensiveComputation()

    // ✅ GOOD: Calculates once
    val result = remember { expensiveComputation() }
}
```

#### 2. `remember(key) {}` — Recalculate on Key Change

```kotlin
@Composable
fun FilteredList(items: List<Item>, query: String) {
    // ✅ Recalculates ONLY when query changes
    val filteredItems = remember(query) {
        items.filter { it.name.contains(query, ignoreCase = true) }
    }

    LazyColumn {
        items(filteredItems, key = { it.id }) { item ->
            ItemCard(item)
        }
    }
}
```

#### 3. `derivedStateOf {}` — Computed State

```kotlin
@Composable
fun ScrollToTopButton(listState: LazyListState) {
    // ❌ BAD: Recomposes on EVERY scroll pixel
    val showButton = listState.firstVisibleItemIndex > 0

    // ✅ GOOD: Only when threshold crossed
    val showButton by remember {
        derivedStateOf {
            listState.firstVisibleItemIndex > 0
        }
    }

    AnimatedVisibility(visible = showButton) {
        FloatingActionButton(onClick = { /* scroll */ }) {
            Icon(Icons.Default.ArrowUpward, null)
        }
    }
}
```

**Why?** `derivedStateOf` batches changes and notifies only when boolean result changes.

### Common Pitfalls

#### 1. Lambda Instability

```kotlin
// ❌ BAD: New lambda each time
@Composable
fun BadButton(viewModel: ViewModel) {
    Button(onClick = { viewModel.doAction() }) {
        Text("Click")
    }
}

// ✅ GOOD: Method reference is stable
@Composable
fun GoodButton(viewModel: ViewModel) {
    Button(onClick = viewModel::doAction) {
        Text("Click")
    }
}
```

#### 2. Reading State Too High

```kotlin
// ❌ BAD: Entire Column recomposes
@Composable
fun BadExample(viewModel: ViewModel) {
    val uiState by viewModel.uiState.collectAsState()

    Column {
        Text(uiState.title)
        ExpensiveComponent() // ❌ Unnecessary recomposition
        Text(uiState.subtitle)
    }
}

// ✅ GOOD: Narrow scope
@Composable
fun GoodExample(viewModel: ViewModel) {
    Column {
        TitleText(viewModel) // ✅ Independent recomposition
        ExpensiveComponent() // ✅ Never recomposes
        SubtitleText(viewModel)
    }
}
```

### Best Practices

1. **State hoisting** — lift to lowest common ancestor
2. **Stable parameters** — use `@Immutable` and `@Stable`
3. **Narrow scope** — read state close to usage
4. **Keys in lists** — use `key` in `items()`
5. **Derived state** — use `derivedStateOf` for computations
6. **Remember expensive operations** — cache with `remember`
7. **Method references** — `viewModel::action` over `{ viewModel.action() }`

---

## Follow-ups

- How does Compose's positional memoization work?
- What are the performance implications of unstable parameters?
- How to debug excessive recompositions using Layout Inspector?

## References

- [[c-jetpack-compose]] - Jetpack Compose concept
- https://developer.android.com/jetpack/compose/lifecycle - Compose `Lifecycle`
- https://developer.android.com/jetpack/compose/state - State and Compose
- https://developer.android.com/jetpack/compose/performance - Compose Performance

## Related Questions

### Hub

- [[moc-android]] - Android MOC

### Related (Medium)

- [[q-jetpack-compose-basics--android--medium]] - Compose basics
- [[q-remember-remembersaveable--android--medium]] - Remember vs RememberSaveable
- [[q-compose-modifier-system--android--medium]] - Modifier system

### Advanced (Harder)

- [[q-compose-performance-optimization--android--hard]] - Performance optimization
