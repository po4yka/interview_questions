---
id: android-140
title: "What Can Be Done Through Composer / Что можно сделать через Composer"
aliases: ["Composer in Jetpack Compose", "Composer в Jetpack Compose"]
topic: android
subtopics: [architecture-mvvm, performance-rendering, ui-compose]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, q-compose-stability-skippability--android--hard, q-how-does-jetpackcompose-work--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android, android/architecture-mvvm, android/performance-rendering, android/ui-compose, difficulty/medium, jetpack-compose, recomposition]
---

# Вопрос (RU)

> Что можно делать через Composer в Jetpack Compose? За что он отвечает и как правильно им пользоваться?

# Question (EN)

> What can be done through the Composer in Jetpack Compose? What does it manage and how should you use it?

---

## Ответ (RU)

**Composer** — внутренний компонент runtime Jetpack Compose, управляющий деревом композиции и отслеживанием зависимостей. Разработчики напрямую с самим Composer API не работают, они взаимодействуют с ним косвенно через `@Composable` функции, `remember`, `State`, `CompositionLocal`, side-effect API и т.д. Composer автоматически:

1. **Отслеживает состояние** — связывает изменения `State`/`MutableState` с зависимыми composable-функциями
2. **Управляет рекомпозицией** — переоценивает только те composable, которые зависят от изменившихся значений, минимизируя обновляемый участок UI
3. **Строит дерево композиции** — поддерживает структуру и данные в slot table между рекомпозициями
4. **Обеспечивает CompositionLocal** — передаёт контекстные данные вниз по дереву и реагирует на их изменения
5. **Координирует side effects** — гарантирует выполнение эффектов в корректные моменты жизненного цикла композиции

### Ключевые Концепции

#### Отслеживание Состояния

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) } // ✅ Composer отслеживает зависимость

    Column {
        Text("Count: $count") // Перекомпозится при изменении count
        Button(onClick = { count++ }) { Text("Increment") }
    }
}
```

#### Slot Table И Remember

Composer хранит значения и структуру между рекомпозициями в slot table:

```kotlin
@Composable
fun RememberExample() {
    // ✅ Composer сохраняет значения между рекомпозициями
    val state = remember { mutableStateOf(0) }
    val viewModel: MyViewModel = viewModel()
    val scope = rememberCoroutineScope()
}
```

#### Композиционные Ключи

Composer использует ключи для идентификации элементов и сопоставления их между рекомпозициями:

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn {
        items(
            items = users,
            key = { it.id } // ✅ Помогает Composer отслеживать идентичность элементов
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
    val theme = LocalTheme.current // ✅ Composer обеспечивает доступ к актуальному значению
    Text("Text", color = theme.textColor)
}
```

#### Side Effects

```kotlin
@Composable
fun UserProfile(userId: String) {
    // ✅ Composer управляет запуском и отменой эффектов с учётом жизненного цикла композиции
    LaunchedEffect(userId) {
        loadUserData(userId)
    }

    DisposableEffect(Unit) {
        val listener = registerListener()
        onDispose { unregisterListener(listener) }
    }
}
```

### Умная Рекомпозиция

Composer стремится определить минимальный scope для обновления:

```kotlin
@Composable
fun SmartRecomposition() {
    var counter by remember { mutableStateOf(0) }

    Column {
        Text("Counter: $counter") // ✅ Перекомпозится при изменении counter
        ExpensiveComponent()      // 🔍 Не будет рекомпозирована только из-за counter,
                                  // если сама не зависит от изменившегося состояния
        Button(onClick = { counter++ }) { Text("Increment") }
    }
}
```

### Best Practices

1. **Используйте `remember` и observable-состояние** — доверьте Composer отслеживание зависимостей
2. **Предоставляйте стабильные ключи** — помогите правильно сопоставлять элементы в списках
3. **Минимизируйте scope рекомпозиции** — держите composable-функции небольшими и сфокусированными
4. **Используйте `derivedStateOf`** — для кэширования вычисляемых значений, зависящих от состояния
5. **Не пытайтесь явно управлять рекомпозицией** — описывайте UI декларативно через состояние

### Что НЕ Делать

```kotlin
// ❌ Простые глобальные переменные не являются observable состоянием для Composer
var globalState = 0

@Composable
fun WrongExample() {
    Text("Count: $globalState") // Изменение globalState само по себе не вызовет рекомпозицию
}

// ✅ Правильно — использовать observable-состояние
@Composable
fun CorrectExample() {
    var count by remember { mutableStateOf(0) }
    Text("Count: $count") // Обновится при изменении count
}
```

---

## Answer (EN)

**Composer** is an internal part of the Jetpack Compose runtime that manages the composition tree and dependency tracking. Developers do not work with the Composer API directly; they interact with it indirectly via `@Composable` functions, `remember`, `State`, `CompositionLocal`, side-effect APIs, etc. The Composer automatically:

1. **Tracks state** — links `State`/`MutableState` changes to dependent composables
2. **Manages recomposition** — re-evaluates only composables that depend on changed values, minimizing the updated UI scope
3. **Builds the composition tree** — maintains structure and values in the slot table across recompositions
4. **Provides CompositionLocal** — propagates contextual values down the tree and reacts to their changes
5. **Coordinates side effects** — runs side effects at correct points in the composition lifecycle

### Key Concepts

#### State Tracking

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) } // ✅ Tracked as a dependency by the Composer

    Column {
        Text("Count: $count") // Recomposes when count changes
        Button(onClick = { count++ }) { Text("Increment") }
    }
}
```

#### Slot Table & Remember

The Composer stores values and structure between recompositions in the slot table:

```kotlin
@Composable
fun RememberExample() {
    // ✅ Composer preserves these across recompositions
    val state = remember { mutableStateOf(0) }
    val viewModel: MyViewModel = viewModel()
    val scope = rememberCoroutineScope()
}
```

#### Composition Keys

The Composer uses keys to identify elements and match them between recompositions:

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn {
        items(
            items = users,
            key = { it.id } // ✅ Helps the Composer track item identity
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
    val theme = LocalTheme.current // ✅ Composer exposes the current value
    Text("Text", color = theme.textColor)
}
```

#### Side Effects

```kotlin
@Composable
fun UserProfile(userId: String) {
    // ✅ Composer manages starting/cancelling effects with the composition lifecycle
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

The Composer attempts to determine the minimal scope that needs to be updated:

```kotlin
@Composable
fun SmartRecomposition() {
    var counter by remember { mutableStateOf(0) }

    Column {
        Text("Counter: $counter") // ✅ Will recompose when counter changes
        ExpensiveComponent()      // 🔍 Will not recompose solely because counter changed,
                                  // unless it also reads state affected by that change
        Button(onClick = { counter++ }) { Text("Increment") }
    }
}
```

### Best Practices

1. **Use `remember` and observable state** — let the Composer track dependencies
2. **Provide stable keys** — help the Composer match list items correctly
3. **Minimize recomposition scope** — keep composables small and focused
4. **Use `derivedStateOf`** — for memoized computed values based on state
5. **Do not try to manually force recomposition** — describe UI declaratively from state

### What NOT to Do

```kotlin
// ❌ Simple global variables are not observable by the Composer
var globalState = 0

@Composable
fun WrongExample() {
    Text("Count: $globalState") // Changing globalState alone will not trigger recomposition
}

// ✅ Correct — use observable state
@Composable
fun CorrectExample() {
    var count by remember { mutableStateOf(0) }
    Text("Count: $count") // Will update when count changes
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
