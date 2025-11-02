---
id: android-119
title: "How Does Jetpack Compose Work / Как работает Jetpack Compose"
aliases: ["How Does Jetpack Compose Work", "Как работает Jetpack Compose"]
topic: android
subtopics: [ui-compose, ui-state, architecture-mvvm]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-cache-implementation-strategies--android--medium, q-how-does-the-main-thread-work--android--medium, q-how-does-activity-lifecycle-work--android--medium]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android, android/ui-compose, android/ui-state, android/architecture-mvvm, difficulty/medium]
date created: Monday, October 27th 2025, 3:33:03 pm
date modified: Thursday, October 30th 2025, 12:48:15 pm
---

# Вопрос (RU)

Как работает Jetpack Compose?

# Question (EN)

How does Jetpack Compose work?

## Ответ (RU)

**Jetpack Compose** - декларативный UI-фреймворк от Google для Android. Вместо XML и императивного управления View, использует Kotlin-функции для описания UI.

### Основные Принципы

**Declarative UI**: описываете что должно быть, а не как построить
**Reactive**: UI автоматически обновляется при изменении данных
**Component-based**: UI из переиспользуемых функций
**Kotlin-first**: полная интеграция с корутинами и Flow

### Как Работает Composition

Compose создаёт дерево composable-функций - **Composition**. Внутри используется **slot table**, отслеживающая активные composable, их позицию, состояние и параметры.

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) } // ✅ State hoisting with remember

    Column {
        Text("Count: $count") // ✅ Recomposes when count changes
        Button(onClick = { count++ }) {
            Text("Increment") // ✅ Never recomposes (static)
        }
    }
}
```

### Recomposition - Сердце Compose

При изменении данных Compose перекомпонует только затронутые части:

1. Изменение state (`count++`)
2. Compose помечает зависимые composable невалидными
3. Выполняются только невалидные composable
4. UI обновляется новыми значениями

### State Hoisting (Поднятие Состояния)

Перемещайте состояние вверх для переиспользуемости:

```kotlin
// ✅ Stateless composable (reusable, testable)
@Composable
fun Counter(count: Int, onIncrement: () -> Unit) {
    Column {
        Text("Count: $count")
        Button(onClick = onIncrement) { Text("+") }
    }
}

// ✅ Stateful parent manages state
@Composable
fun CounterScreen() {
    var count by remember { mutableStateOf(0) }
    Counter(count = count, onIncrement = { count++ })
}
```

### Effect Handlers

Для побочных эффектов (side effects):

```kotlin
@Composable
fun EffectsExample(userId: String) {
    // ✅ LaunchedEffect: suspend functions, restarts on key change
    LaunchedEffect(userId) {
        val user = loadUser(userId)
    }

    // ✅ DisposableEffect: cleanup resources
    DisposableEffect(Unit) {
        val listener = LocationListener()
        locationManager.addListener(listener)
        onDispose { locationManager.removeListener(listener) }
    }
}
```

### Modifiers - Стилизация И Поведение

Модификаторы настраивают внешний вид. **Порядок важен**:

```kotlin
// ✅ Padding before background - background includes padding
Box(Modifier.padding(16.dp).background(Color.Blue))

// ❌ Background before padding - padding outside background
Box(Modifier.background(Color.Blue).padding(16.dp))
```

### Производительность

```kotlin
@Composable
fun OptimizedList(items: List<Item>) {
    // ✅ LazyColumn for large lists (like RecyclerView)
    LazyColumn {
        items(items) { item -> ItemRow(item) }
    }
}

@Composable
fun ItemRow(item: Item) {
    // ✅ derivedStateOf: recompute only when dependencies change
    val isExpensive by remember(item) {
        derivedStateOf { expensiveCalculation(item) }
    }
    // ✅ remember: cache expensive objects by key
    val obj = remember(item.id) { createExpensiveObject(item) }
}
```

### Как Работает Внутри

**Три фазы**:
1. **Composition**: построение UI дерева из @Composable функций
2. **Layout**: измерение и позиционирование элементов
3. **Drawing**: отрисовка пикселей

**Slot Table**: gap buffer для эффективного отслеживания позиций composable, объектов состояния, значений remember, ключей для перекомпозиции.

### Резюме

Compose работает через:
- Объявление UI с @Composable функциями
- Построение composition tree
- Автоматическое наблюдение за состоянием
- Умную перекомпозицию только затронутых частей
- Эффективный layout и отрисовку

**Магия** в умной перекомпозиции - выполняются только функции, зависящие от изменённого состояния.

## Answer (EN)

**Jetpack Compose** is Google's declarative UI toolkit for Android. Instead of XML and imperative View manipulation, it uses Kotlin functions to describe UI.

### Core Principles

**Declarative UI**: describe what the UI should look like, not how to build it
**Reactive**: UI automatically updates when data changes
**Component-based**: build UIs from reusable functions
**Kotlin-first**: full integration with coroutines and Flow

### How Composition Works

Compose builds a tree of composable functions called **Composition**. Internally, it uses a **slot table** that tracks active composables, their positions, state, and parameters.

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) } // ✅ State hoisting with remember

    Column {
        Text("Count: $count") // ✅ Recomposes when count changes
        Button(onClick = { count++ }) {
            Text("Increment") // ✅ Never recomposes (static)
        }
    }
}
```

### Recomposition - The Heart of Compose

When data changes, Compose intelligently recomposes only affected parts:

1. State changes (`count++`)
2. Compose marks dependent composables as invalid
3. Only invalid composables re-execute
4. UI updates with new values

### State Hoisting

Move state up to make components reusable and testable:

```kotlin
// ✅ Stateless composable (reusable, testable)
@Composable
fun Counter(count: Int, onIncrement: () -> Unit) {
    Column {
        Text("Count: $count")
        Button(onClick = onIncrement) { Text("+") }
    }
}

// ✅ Stateful parent manages state
@Composable
fun CounterScreen() {
    var count by remember { mutableStateOf(0) }
    Counter(count = count, onIncrement = { count++ })
}
```

### Effect Handlers

For side effects:

```kotlin
@Composable
fun EffectsExample(userId: String) {
    // ✅ LaunchedEffect: suspend functions, restarts on key change
    LaunchedEffect(userId) {
        val user = loadUser(userId)
    }

    // ✅ DisposableEffect: cleanup resources
    DisposableEffect(Unit) {
        val listener = LocationListener()
        locationManager.addListener(listener)
        onDispose { locationManager.removeListener(listener) }
    }
}
```

### Modifiers - Styling and Behavior

Modifiers customize appearance and behavior. **Order matters**:

```kotlin
// ✅ Padding before background - background includes padding
Box(Modifier.padding(16.dp).background(Color.Blue))

// ❌ Background before padding - padding outside background
Box(Modifier.background(Color.Blue).padding(16.dp))
```

### Performance Optimization

```kotlin
@Composable
fun OptimizedList(items: List<Item>) {
    // ✅ LazyColumn for large lists (like RecyclerView)
    LazyColumn {
        items(items) { item -> ItemRow(item) }
    }
}

@Composable
fun ItemRow(item: Item) {
    // ✅ derivedStateOf: recompute only when dependencies change
    val isExpensive by remember(item) {
        derivedStateOf { expensiveCalculation(item) }
    }
    // ✅ remember: cache expensive objects by key
    val obj = remember(item.id) { createExpensiveObject(item) }
}
```

### How It Works Under the Hood

**Three phases**:
1. **Composition**: build UI tree from @Composable functions
2. **Layout**: measure and position elements
3. **Drawing**: render pixels to screen

**Slot Table**: gap buffer for efficiently tracking composable positions, state objects, remember values, group keys for recomposition.

### Summary

Compose works by:
- Declaring UI with @Composable functions
- Building composition tree
- Automatically observing state
- Smart recomposition of only affected parts
- Efficient layout and drawing

**The magic** is in smart recomposition - Compose only re-executes functions that depend on changed state.

## Follow-ups

- How does Compose handle configuration changes compared to traditional Views?
- What are the performance implications of deep nesting in Compose?
- How does remember work across process death and restoration?
- When should you use derivedStateOf vs regular state?
- How does Compose interop affect performance in hybrid apps?

## References

- Official Jetpack Compose documentation
- Thinking in Compose guide
- State management in Compose best practices

## Related Questions

### Prerequisites
- Basic Kotlin knowledge with lambdas and delegates
- Understanding of Android View system basics

### Related
- [[q-cache-implementation-strategies--android--medium]]
- [[q-how-does-the-main-thread-work--android--medium]]
- [[q-how-does-activity-lifecycle-work--android--medium]]

### Advanced
- Advanced Compose performance optimization techniques
- Custom layout implementation in Compose
- Compose compiler internals and code generation

