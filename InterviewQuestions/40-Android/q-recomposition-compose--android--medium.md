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
updated: 2025-11-10
sources: ["https://developer.android.com/jetpack/compose/lifecycle"]
tags: [android/performance-rendering, android/ui-compose, android/ui-state, difficulty/medium, jetpack-compose, performance, recomposition, state]

---

# Вопрос (RU)

> Что такое рекомпозиция в Jetpack Compose? Что триггерит рекомпозицию и как Compose решает какие composable нужно перерисовать?

# Question (EN)

> What is recomposition in Jetpack Compose? What triggers recomposition, and how does Compose decide which composables need to recompose?

---

## Ответ (RU)

**Рекомпозиция** — процесс повторного выполнения composable-функций при изменении отслеживаемых параметров или состояния. См. [[c-jetpack-compose]].

### Как Работает

В отличие от `View` (`textView.text = "new"`), Compose переисполняет composable-функции с новыми данными.

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
2. Compose фиксирует изменение State
3. Функция `Counter()` повторно выполняется (частично или целиком в зависимости от структуры)
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
- изменения значений `mutableStateOf`
- новые значения из `Flow` через `collectAsState()`
- новые значения из `LiveData` через `observeAsState()`

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

Compose стремится рекомпозировать **минимально необходимую область** вокруг мест, где прочитано изменившееся состояние. Насколько локальной получится рекомпозиция, зависит от того, где читается state и как структурированы composable-функции.

```kotlin
@Composable
fun Screen() {
    var topCounter by remember { mutableStateOf(0) }
    var bottomCounter by remember { mutableStateOf(0) }

    Column {
        Text("Top: $topCounter") // ✅ В основном затрагивается при изменении topCounter
        Button(onClick = { topCounter++ }) { Text("Top") }

        Text("Bottom: $bottomCounter") // ✅ В основном затрагивается при изменении bottomCounter
        Button(onClick = { bottomCounter++ }) { Text("Bottom") }
    }
}
```

### Стабильность И Пропуск Рекомпозиции

Compose может **пропускать рекомпозицию** для вызова composable, если:
- параметры стабильны (stable) по модели стабильности Compose
- и их значения (по `equals`) не изменились.

```kotlin
// ✅ Стабильно: Примитивы
@Composable
fun Counter(count: Int) // Может быть пропущен, если count не изменился

// ✅ Стабильно: @Immutable
@Immutable
data class User(val id: String, val name: String)

@Composable
fun UserCard(user: User) // Может быть пропущен, если user — тот же экземпляр и его поля не меняются

// ⚠️ По умолчанию нестабильно: List
@Composable
fun ItemList(items: List<Item>) // Обрабатывается как нестабильный параметр
```

**Почему `List` считается нестабильным?** По модели стабильности Compose обычные `List`/`MutableList` не дают гарантий неизменяемости и могут концептуально меняться без смены ссылки, поэтому Compose не может безопасно относиться к ним как к stable-типам. Это увеличивает вероятность рекомпозиции при изменениях, но не означает "безусловная рекомпозиция каждый кадр".

#### Решение: Сделать Стабильным

```kotlin
// Option 1: @Stable-обертка
@Stable
data class ItemsState(val items: List<Item>)

// Option 2: ImmutableList
import kotlinx.collections.immutable.ImmutableList

@Composable
fun ItemList(items: ImmutableList<Item>) // ✅ Тип может быть тривиально стабильным
```

### Контроль Рекомпозиции

#### 1. `remember {}` — Сохранить Между Рекомпозициями

```kotlin
@Composable
fun ExpensiveCalculation() {
    // ❌ ПЛОХО: Пересчитывает на каждую рекомпозицию этого вызова
    val result = expensiveComputation()

    // ✅ ХОРОШО: Вычисляет один раз для данного места и сохраняет до изменения ключей/жизненного цикла
    val rememberedResult = remember { expensiveComputation() }
}
```

#### 2. `remember(key) {}` — Пересчёт При Изменении Ключа

```kotlin
@Composable
fun FilteredList(items: List<Item>, query: String) {
    // ✅ Пересчет только при изменении query (или items, если добавить их в ключи)
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
    // ❌ Наивно: showButton вычисляется напрямую и будет читаться при каждом изменении listState
    // val showButton = listState.firstVisibleItemIndex > 0

    // ✅ derivedStateOf: пересчитывается при изменении зависимостей
    // и триггерит рекомпозицию только при изменении результата по equals
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

**Почему это помогает?** `derivedStateOf` отслеживает чтения внутри лямбды и уведомляет только когда итоговое значение действительно меняется, уменьшая число лишних рекомпозиций потребителей.

### Распространённые Ошибки

#### 1. Лямбды и стабильность

```kotlin
// При таком объявлении формально создается новая лямбда на каждую рекомпозицию,
// но большинство Material-компонентов оптимизированы для обработки таких onClick.
@Composable
fun LambdaButton(viewModel: ViewModel) {
    Button(onClick = { viewModel.doAction() }) {
        Text("Клик")
    }
}

// Использование ссылок на методы или remember для колбеков может снизить шум изменений
// при передаче колбеков глубже по иерархии.
@Composable
fun MethodRefButton(viewModel: ViewModel) {
    Button(onClick = viewModel::doAction) {
        Text("Клик")
    }
}
```

Главная идея: избегать нестабильных/каждый раз новых параметров там, где они передаются дальше и могут вызывать лишние рекомпозиции дочерних composable.

#### 2. Чтение Состояния Слишком Высоко

```kotlin
// ❌ ПЛОХО: Вся Column рекомпозируется при любом изменении uiState
@Composable
fun BadExample(viewModel: ViewModel) {
    val uiState by viewModel.uiState.collectAsState()

    Column {
        Text(uiState.title)
        ExpensiveComponent() // ❌ Может рекомпозироваться вместе с Column из-за uiState
        Text(uiState.subtitle)
    }
}

// ✅ ХОРОШО: Узкая область — состояние читается ближе к месту использования
@Composable
fun GoodExample(viewModel: ViewModel) {
    Column {
        TitleText(viewModel) // ✅ Независимая рекомпозиция для title-состояния
        ExpensiveComponent() // ✅ Не зависит от uiState → не рекомпозируется из-за его изменений
        SubtitleText(viewModel)
    }
}
```

### Best Practices

1. **State hoisting** — поднимать состояние к ближайшему общему предку.
2. **Стабильные параметры** — использовать типы, совместимые с моделью стабильности (`@Immutable`, `@Stable`, иммутабельные коллекции), где это оправдано.
3. **Узкая область** — читать состояние как можно ближе к месту использования.
4. **Ключи в списках** — использовать `key` в `items()` для устойчивой идентификации.
5. **Derived state** — применять `derivedStateOf` для вычисляемых значений на основе других состояний.
6. **Remember дорогих операций** — кэшировать с `remember`, чтобы не повторять тяжелые вычисления на каждую рекомпозицию.
7. **Стабильные колбеки при глубокой передаче** — по возможности использовать method reference или `remember` для колбеков, которые пробрасываются вниз по дереву.

---

## Answer (EN)

**Recomposition** is the process of re-executing composable functions when tracked parameters or observable state change. See [[c-jetpack-compose]].

### How it Works

Unlike the classic `View` system (`textView.text = "new"`), Compose re-runs composable functions with new data.

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
2. Compose observes the State change
3. `Counter()` is scheduled for recomposition (partially or fully depending on structure)
4. The UI is updated

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
- changes to `mutableStateOf` values
- emissions from `Flow` via `collectAsState()`
- `LiveData` updates via `observeAsState()`

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

Compose tries to recompose at the **narrowest possible scope** around where the changed state is read. How narrow it actually is depends on where you read state and how your composables are structured.

```kotlin
@Composable
fun Screen() {
    var topCounter by remember { mutableStateOf(0) }
    var bottomCounter by remember { mutableStateOf(0) }

    Column {
        Text("Top: $topCounter") // ✅ Primarily affected when topCounter changes
        Button(onClick = { topCounter++ }) { Text("Top") }

        Text("Bottom: $bottomCounter") // ✅ Primarily affected when bottomCounter changes
        Button(onClick = { bottomCounter++ }) { Text("Bottom") }
    }
}
```

### Stability and Skipping

Compose can **skip recomposition** for a composable call when:
- its parameters are stable according to Compose's stability model, and
- their values (by `equals`) have not changed.

```kotlin
// ✅ Stable: primitives
@Composable
fun Counter(count: Int) // May be skipped if count is unchanged

// ✅ Stable: @Immutable
@Immutable
data class User(val id: String, val name: String)

@Composable
fun UserCard(user: User) // May be skipped if the same instance is passed and it doesn't mutate

// ⚠️ By default unstable: List
@Composable
fun ItemList(items: List<Item>) // Treated as having an unstable parameter
```

**Why is `List` treated as unstable?** In Compose's stability model, regular `List`/`MutableList` do not provide immutability guarantees and can conceptually change without a new reference, so Compose cannot safely assume they are stable types. This increases the likelihood of recomposition when they change; it does not mean "unconditionally recompose every frame."

#### Solution: Make It Stable

```kotlin
// Option 1: @Stable wrapper
@Stable
data class ItemsState(val items: List<Item>)

// Option 2: ImmutableList
import kotlinx.collections.immutable.ImmutableList

@Composable
fun ItemList(items: ImmutableList<Item>) // ✅ Type can be trivially stable
```

### Controlling Recomposition

#### 1. `remember {}` — Preserve Across Recompositions

```kotlin
@Composable
fun ExpensiveCalculation() {
    // ❌ BAD: Recomputed on every recomposition of this call site
    val result = expensiveComputation()

    // ✅ GOOD: Computed once for this call site and retained across recompositions
    val rememberedResult = remember { expensiveComputation() }
}
```

#### 2. `remember(key) {}` — Recalculate on Key Change

```kotlin
@Composable
fun FilteredList(items: List<Item>, query: String) {
    // ✅ Recalculates only when query changes (or include items in keys if needed)
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
    // Naive (commented out): direct read would participate in recomposition whenever listState changes
    // val showButton = listState.firstVisibleItemIndex > 0

    // ✅ derivedStateOf: tracks reads inside, recomputes on dependency changes,
    // and notifies only when the resulting value actually changes by equals
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

**Why does this help?** `derivedStateOf` tracks dependencies and triggers recomposition of its consumers only when the computed value changes, reducing unnecessary recompositions.

### Common Pitfalls

#### 1. Lambdas and Stability

```kotlin
// Formally creates a new lambda each recomposition,
// but Material components are optimized for typical onClick lambdas.
@Composable
fun LambdaButton(viewModel: ViewModel) {
    Button(onClick = { viewModel.doAction() }) {
        Text("Click")
    }
}

// Using method references or remember for callbacks can reduce change noise
// when callbacks are passed deeper down the tree.
@Composable
fun MethodRefButton(viewModel: ViewModel) {
    Button(onClick = viewModel::doAction) {
        Text("Click")
    }
}
```

Key idea: avoid unnecessarily unstable/changing parameters especially when they are forwarded to child composables and can cause extra recompositions.

#### 2. Reading State Too High

```kotlin
// ❌ BAD: Entire Column recomposes for any uiState change
@Composable
fun BadExample(viewModel: ViewModel) {
    val uiState by viewModel.uiState.collectAsState()

    Column {
        Text(uiState.title)
        ExpensiveComponent() // ❌ May recompose along with Column because of uiState changes
        Text(uiState.subtitle)
    }
}

// ✅ GOOD: Narrower scope — read state closer to where it is used
@Composable
fun GoodExample(viewModel: ViewModel) {
    Column {
        TitleText(viewModel) // ✅ Independent recomposition for title-related state
        ExpensiveComponent() // ✅ Not tied to uiState → won't recompose due to its changes
        SubtitleText(viewModel)
    }
}
```

### Best Practices

1. **State hoisting** — lift state to the lowest common ancestor that needs to control it.
2. **Stable parameters** — prefer types compatible with Compose stability (`@Immutable`, `@Stable`, immutable collections`) when appropriate.
3. **Narrow scope** — read state as close as possible to where it is used.
4. **Keys in lists** — use `key` in `items()` to provide stable identities.
5. **Derived state** — use `derivedStateOf` for derived/computed values.
6. **Remember expensive operations** — use `remember` to avoid recomputing heavy work on every recomposition.
7. **Stable callbacks when propagating deeply** — consider method references or `remember` for callbacks passed down the tree.

---

## Follow-ups

- How does Compose's positional memoization work?
- What are the performance implications of unstable parameters?
- How to debug excessive recompositions using Layout Inspector?

## References

- [[c-jetpack-compose]] - Jetpack Compose concept
- https://developer.android.com/jetpack/compose/lifecycle - Compose Lifecycle
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
