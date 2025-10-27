---
id: 20251012-122711
title: "What Can Be Done Through Composer / Что можно сделать через Composer"
aliases: ["Composer in Jetpack Compose", "Composer в Jetpack Compose"]
topic: android
subtopics: [ui-compose, architecture-mvvm, performance-rendering]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, q-compose-stability-skippability--android--hard, q-how-does-jetpackcompose-work--android--medium]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags:
  - android
  - android/ui-compose
  - android/architecture-mvvm
  - android/performance-rendering
  - jetpack-compose
  - recomposition
  - difficulty/medium
---
# Вопрос (RU)

> Что можно делать через Composer в Jetpack Compose? За что он отвечает и как правильно им пользоваться?

# Question (EN)

> What can be done through the Composer in Jetpack Compose? What does it manage and how should you use it?

---

## Ответ (RU)

**Composer** — внутренний компонент Jetpack Compose, управляющий деревом композиции и отслеживанием зависимостей. Разработчики напрямую не работают с Composer, но он автоматически:

1. **Отслеживает состояние** — связывает изменения `State` с зависимыми composable-функциями
2. **Управляет рекомпозицией** — перерисовывает только изменённые части UI
3. **Строит дерево композиции** — сохраняет структуру и данные между рекомпозициями
4. **Обеспечивает CompositionLocal** — передаёт контекстные данные вниз по дереву
5. **Координирует side effects** — выполняет эффекты в правильный момент жизненного цикла

### Ключевые концепции

#### Отслеживание состояния

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) } // ✅ Composer отслеживает

    Column {
        Text("Count: $count") // Перекомпозится при изменении count
        Button(onClick = { count++ }) { Text("Increment") }
    }
}
```

#### Slot Table и Remember

Composer хранит значения между рекомпозициями в slot table:

```kotlin
@Composable
fun RememberExample() {
    // ✅ Composer сохраняет значения
    val state = remember { mutableStateOf(0) }
    val viewModel: MyViewModel = viewModel()
    val scope = rememberCoroutineScope()
}
```

#### Композиционные ключи

Composer использует ключи для идентификации элементов:

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn {
        items(
            items = users,
            key = { it.id } // ✅ Помогает Composer отслеживать идентичность
        ) { user ->
            UserItem(user)
        }
    }
}
```

#### CompositionLocal

```kotlin
val LocalTheme = compositionLocalOf<Theme> { error("No theme") }

@Composable
fun ThemedText() {
    val theme = LocalTheme.current // ✅ Composer предоставляет значение
    Text("Text", color = theme.textColor)
}
```

#### Side Effects

```kotlin
@Composable
fun UserProfile(userId: String) {
    // ✅ Composer управляет жизненным циклом
    LaunchedEffect(userId) {
        loadUserData(userId)
    }

    DisposableEffect(Unit) {
        val listener = registerListener()
        onDispose { unregisterListener(listener) }
    }
}
```

### Умная рекомпозиция

Composer автоматически определяет минимальный scope для обновления:

```kotlin
@Composable
fun SmartRecomposition() {
    var counter by remember { mutableStateOf(0) }

    Column {
        Text("Counter: $counter") // ✅ Обновится
        ExpensiveComponent()      // ❌ Не обновится
        Button(onClick = { counter++ }) { Text("Increment") }
    }
}
```

### Best Practices

1. **Используйте `remember`** — доверьте Composer управление состоянием
2. **Предоставляйте стабильные ключи** — помогите идентифицировать элементы
3. **Минимизируйте scope рекомпозиции** — держите composable-функции фокусированными
4. **Используйте `derivedStateOf`** — для вычисляемых значений
5. **Не пытайтесь управлять рекомпозицией вручную**

### Что НЕ делать

```kotlin
// ❌ Глобальное состояние не отслеживается
var globalState = 0

@Composable
fun WrongExample() {
    Text("Count: $globalState") // Не обновится
}

// ✅ Правильно
@Composable
fun CorrectExample() {
    var count by remember { mutableStateOf(0) }
    Text("Count: $count") // Обновится
}
```

---

## Answer (EN)

**Composer** is an internal component of Jetpack Compose managing the composition tree and state dependencies. Developers don't interact with Composer directly, but it automatically:

1. **Tracks state** — links `State` changes to dependent composables
2. **Manages recomposition** — redraws only changed UI parts
3. **Builds composition tree** — preserves structure and data between recompositions
4. **Provides CompositionLocal** — passes contextual data down the tree
5. **Coordinates side effects** — executes effects at the right lifecycle moment

### Key Concepts

#### State Tracking

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) } // ✅ Composer tracks

    Column {
        Text("Count: $count") // Recomposes when count changes
        Button(onClick = { count++ }) { Text("Increment") }
    }
}
```

#### Slot Table & Remember

Composer stores values between recompositions in the slot table:

```kotlin
@Composable
fun RememberExample() {
    // ✅ Composer preserves values
    val state = remember { mutableStateOf(0) }
    val viewModel: MyViewModel = viewModel()
    val scope = rememberCoroutineScope()
}
```

#### Composition Keys

Composer uses keys to identify elements:

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn {
        items(
            items = users,
            key = { it.id } // ✅ Helps Composer track identity
        ) { user ->
            UserItem(user)
        }
    }
}
```

#### CompositionLocal

```kotlin
val LocalTheme = compositionLocalOf<Theme> { error("No theme") }

@Composable
fun ThemedText() {
    val theme = LocalTheme.current // ✅ Composer provides value
    Text("Text", color = theme.textColor)
}
```

#### Side Effects

```kotlin
@Composable
fun UserProfile(userId: String) {
    // ✅ Composer manages lifecycle
    LaunchedEffect(userId) {
        loadUserData(userId)
    }

    DisposableEffect(Unit) {
        val listener = registerListener()
        onDispose { unregisterListener(listener) }
    }
}
```

### Smart Recomposition

Composer automatically determines minimal scope for updates:

```kotlin
@Composable
fun SmartRecomposition() {
    var counter by remember { mutableStateOf(0) }

    Column {
        Text("Counter: $counter") // ✅ Will update
        ExpensiveComponent()      // ❌ Won't update
        Button(onClick = { counter++ }) { Text("Increment") }
    }
}
```

### Best Practices

1. **Use `remember`** — trust Composer with state management
2. **Provide stable keys** — help identify elements
3. **Minimize recomposition scope** — keep composables focused
4. **Use `derivedStateOf`** — for computed values
5. **Don't manually control recomposition**

### What NOT to Do

```kotlin
// ❌ Global state not tracked
var globalState = 0

@Composable
fun WrongExample() {
    Text("Count: $globalState") // Won't update
}

// ✅ Correct
@Composable
fun CorrectExample() {
    var count by remember { mutableStateOf(0) }
    Text("Count: $count") // Will update
}
```

---

## Follow-ups

- How does Composer decide what to recompose and what to skip?
- How do `@Stable` and `@Immutable` annotations affect recomposition behavior?
- What strategies minimize unnecessary recomposition scope?
- How does Composer handle CompositionLocal value changes?
- What's the relationship between Composer's slot table and remembering values?

## References

- [[c-jetpack-compose]] — Jetpack Compose fundamentals
- https://developer.android.com/jetpack/compose/mental-model
- https://developer.android.com/jetpack/compose/performance
- https://developer.android.com/jetpack/compose/state

## Related Questions

### Prerequisites (Easier)

- [[q-what-are-the-most-important-components-of-compose--android--medium]] — Compose basics

### Related (Medium)

- [[q-how-does-jetpackcompose-work--android--medium]] — Compose architecture
- [[q-compositionlocal-advanced--android--medium]] — CompositionLocal patterns

### Advanced (Harder)

- [[q-compose-stability-skippability--android--hard]] — Stability and skippability
- [[q-compose-performance-optimization--android--hard]] — Performance optimization
