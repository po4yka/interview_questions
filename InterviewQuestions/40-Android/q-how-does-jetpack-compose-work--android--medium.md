---
id: android-368
title: "How Does Jetpack Compose Work / Как работает Jetpack Compose"
aliases: [Compose UI, Declarative UI, Jetpack Compose, Декларативный UI]
topic: android
subtopics: [architecture-mvvm, ui-compose]
question_kind: theory
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-mutable-state-compose--android--medium, q-what-are-the-most-important-components-of-compose--android--medium]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/architecture-mvvm, android/ui-compose, compose, declarative-ui, difficulty/medium, recomposition]
---

# Вопрос (RU)

> Как работает Jetpack Compose? Объясните основные принципы декларативного UI и процесс рендеринга.

# Question (EN)

> How does Jetpack Compose work? Explain the core principles of declarative UI and the rendering process.

---

## Ответ (RU)

**Подход**: Jetpack Compose использует декларативный подход для построения UI, где вы описываете "что" должно отображаться, а не "как" это сделать.

**Основные Концепции**:

### 1. Декларативный Vs Императивный

```kotlin
// ❌ Императивный (View System)
textView.text = "Привет"
textView.visibility = View.VISIBLE

// ✅ Декларативный (Compose)
@Composable
fun Greeting(name: String, isVisible: Boolean) {
 if (isVisible) {
 Text("Привет $name")
 }
}
```

### 2. Composable-функции

Основа фреймворка - функции с аннотацией `@Composable`:

```kotlin
@Composable
fun Counter() {
 var count by remember { mutableStateOf(0) }

 Column {
 Text("Счет: $count")
 Button(onClick = { count++ }) {
 Text("Увеличить")
 }
 }
}
```

**Характеристики**:
- Вызываются только из других composable-функций
- Могут поддерживать состояние через `remember`
- Запускают рекомпозицию при изменении состояния

### 3. Три Фазы Рендеринга

**Composition** → **Layout** → **Drawing**

```kotlin
// 1. Composition - строит дерево UI
Column {
 Text("Заголовок")
 Button(onClick = {}) { Text("Действие") }
}

// 2. Layout - измеряет и позиционирует
Box(modifier = Modifier.fillMaxWidth().height(200.dp)) {
 Text(modifier = Modifier.align(Alignment.Center))
}

// 3. Drawing - рендерит на Canvas
Canvas(modifier = Modifier.size(100.dp)) {
 drawCircle(color = Color.Blue)
}
```

### 4. Умная Рекомпозиция

```kotlin
@Composable
fun SmartRecomposition() {
 var counter by remember { mutableStateOf(0) }

 Column {
 Text("Счетчик: $counter") // ✅ Перекомпонуется
 StaticHeader() // ✅ Пропускается (нет зависимостей)
 Button(onClick = { counter++ }) { Text("Увеличить") }
 }
}
```

### 5. Управление Побочными Эффектами

```kotlin
@Composable
fun UserProfile(userId: String) {
 var user by remember { mutableStateOf<User?>(null) }

 LaunchedEffect(userId) {
 user = fetchUser(userId) // Запускается при изменении userId
 }

 DisposableEffect(Unit) {
 onDispose { cleanup() } // Очистка
 }

 user?.let { UserCard(it) }
}
```

**Сложность**: Recomposition - O(n) где n - измененные composable, Layout - O(n), Drawing - O(n)

---

## Answer (EN)

**Approach**: Jetpack Compose uses a declarative approach where you describe "what" the UI should look like, not "how" to build it.

**Core Concepts**:

### 1. Declarative Vs Imperative

```kotlin
// ❌ Imperative (View System)
textView.text = "Hello"
textView.visibility = View.VISIBLE

// ✅ Declarative (Compose)
@Composable
fun Greeting(name: String, isVisible: Boolean) {
 if (isVisible) {
 Text("Hello $name")
 }
}
```

### 2. Composable Functions

Foundation - functions annotated with `@Composable`:

```kotlin
@Composable
fun Counter() {
 var count by remember { mutableStateOf(0) }

 Column {
 Text("Count: $count")
 Button(onClick = { count++ }) {
 Text("Increment")
 }
 }
}
```

**Characteristics**:
- Called only from other composable functions
- Can maintain state via `remember`
- Trigger recomposition on state changes

### 3. Three Rendering Phases

**Composition** → **Layout** → **Drawing**

```kotlin
// 1. Composition - builds UI tree
Column {
 Text("Header")
 Button(onClick = {}) { Text("Action") }
}

// 2. Layout - measures and positions
Box(modifier = Modifier.fillMaxWidth().height(200.dp)) {
 Text(modifier = Modifier.align(Alignment.Center))
}

// 3. Drawing - renders to Canvas
Canvas(modifier = Modifier.size(100.dp)) {
 drawCircle(color = Color.Blue)
}
```

### 4. Smart Recomposition

```kotlin
@Composable
fun SmartRecomposition() {
 var counter by remember { mutableStateOf(0) }

 Column {
 Text("Counter: $counter") // ✅ Recomposes
 StaticHeader() // ✅ Skipped (no dependencies)
 Button(onClick = { counter++ }) { Text("Increment") }
 }
}
```

### 5. Side Effects Management

```kotlin
@Composable
fun UserProfile(userId: String) {
 var user by remember { mutableStateOf<User?>(null) }

 LaunchedEffect(userId) {
 user = fetchUser(userId) // Runs when userId changes
 }

 DisposableEffect(Unit) {
 onDispose { cleanup() } // Cleanup
 }

 user?.let { UserCard(it) }
}
```

**Complexity**: Recomposition - O(n) where n is changed composables, Layout - O(n), Drawing - O(n)

---

## Follow-ups

- How does Compose determine what to recompose?
- What is the difference between remember and rememberSaveable?
- How do modifiers work and what is the order of execution?
- What are stable classes and why do they matter?
- How does Compose integrate with `ViewModel`?

## References

- - Compose UI fundamentals
- - Declarative programming paradigm
- [[c-recomposition]] - Recomposition mechanics
- https://developer.android.com/jetpack/compose/mental-model

## Related Questions

### Prerequisites (Easier)

### Related (Same Level)
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Essential components
- [[q-mutable-state-compose--android--medium]] - State management
- [[q-remember-vs-remembersaveable-compose--android--medium]] - State persistence
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Lists in Compose

### Advanced (Harder)
- [[q-compose-stability-skippability--android--hard]] - Stability & skippability
- [[q-stable-classes-compose--android--hard]] - @Stable annotation
- [[q-compose-performance-optimization--android--hard]] - Performance tuning
