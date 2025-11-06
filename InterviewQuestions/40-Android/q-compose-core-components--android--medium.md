---
id: android-072
title: Compose Core Components / Основные компоненты Compose
aliases: [Compose Components, Jetpack Compose Architecture, Архитектура Jetpack Compose, Основные компоненты Compose]
topic: android
subtopics:
  - architecture-mvvm
  - ui-compose
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-compose-recomposition
  - c-compose-state
  - c-mvvm-pattern
  - q-compose-modifier-order-performance--android--medium
  - q-compose-stability-skippability--android--hard
created: 2025-10-13
updated: 2025-11-02
tags: [android/architecture-mvvm, android/ui-compose, declarative-ui, difficulty/medium, jetpack-compose]
sources:
  - https://developer.android.com/jetpack/compose/architecture
---

# Вопрос (RU)
> Из каких более важных компонентов состоит Compose?

# Question (EN)
> What are the most important components that make up Compose?

## Ответ (RU)

Jetpack Compose состоит из восьми ключевых компонентов, работающих вместе для создания декларативного UI-фреймворка.

### Основные Компоненты

**1. Composable Functions** — базовые строительные блоки UI с аннотацией ``@Composable``:
```kotlin
@Composable
fun UserProfile(user: User) {
    Column {
        Text(user.name)
        Button(onClick = { /* action */ }) {
            Text("Подписаться")
        }
    }
}
```

**2. State Management** — управление состоянием через `remember` и `mutableStateOf`, управляет обновлениями UI через [[c-compose-recomposition]].
```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }
    Column {
        Text("Счёт: $count")
        Button(onClick = { count++ }) { Text("Увеличить") }
    }
}
```

**3. Modifiers** — изменяют внешний вид, поведение и layout composable:
```kotlin
Text(
    text = "Карточка",
    modifier = Modifier
        .fillMaxWidth()
        .padding(16.dp)
        .background(Color.White, RoundedCornerShape(8.dp))
        .clickable { /* action */ }
)
```

**4. Layouts** — организация элементов (`Column`, `Row`, `Box`, `LazyColumn`):
```kotlin
Column(
    modifier = Modifier.fillMaxSize(),
    verticalArrangement = Arrangement.SpaceBetween
) {
    Text("Верх")
    Text("Низ")
}
```

**5. Recomposition** — умное обновление UI при изменении состояния (только зависимые composable перерисовываются).

**6. Effect Handlers** — управление побочными эффектами и lifecycle:
- `LaunchedEffect` — suspending код
- `DisposableEffect` — cleanup ресурсов
- `SideEffect` — синхронизация с внешним состоянием

**7. Material Components** — готовые UI-компоненты по Material Design: `Button`, `TextField`, `Card` и др.

**8. Theme System** — централизованная стилизация через `MaterialTheme`.

## Answer (EN)

Jetpack Compose consists of eight core components that work together to create a declarative UI framework.

### Core Components

**1. Composable Functions** — building blocks of UI annotated with ``@Composable``:
```kotlin
@Composable
fun UserProfile(user: User) {
    Column {
        Text(user.name)
        Button(onClick = { /* action */ }) {
            Text("Follow")
        }
    }
}
```

**2. State Management** — manages UI updates through `remember` and `mutableStateOf`, drives updates via [[c-compose-recomposition]]:
```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }
    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) { Text("Increment") }
    }
}
```

**3. Modifiers** — modify appearance, behavior, and layout of composables:
```kotlin
Text(
    text = "Card",
    modifier = Modifier
        .fillMaxWidth()
        .padding(16.dp)
        .background(Color.White, RoundedCornerShape(8.dp))
        .clickable { /* action */ }
)
```

**4. Layouts** — arrange elements (`Column`, `Row`, `Box`, `LazyColumn`):
```kotlin
Column(
    modifier = Modifier.fillMaxSize(),
    verticalArrangement = Arrangement.SpaceBetween
) {
    Text("Top")
    Text("Bottom")
}
```

**5. Recomposition** — smart UI update mechanism when state changes (only dependent composables recompose).

**6. Effect Handlers** — manage side effects and lifecycle:
- `LaunchedEffect` — suspending code
- `DisposableEffect` — resource cleanup
- `SideEffect` — synchronization with external state

**7. Material Components** — pre-built UI components following Material Design: `Button`, `TextField`, `Card`, etc.

**8. Theme System** — centralized styling through `MaterialTheme`.

## Follow-ups

- How does Compose's recomposition differ from traditional `View` updates?
- What are the performance implications of state hoisting?
- How do you debug recomposition issues in Compose?
- When should you use `LaunchedEffect` vs `DisposableEffect` vs `SideEffect`?
- How does Compose handle configuration changes compared to traditional `View`s?

## References

- [[c-compose-state]]
- [[c-compose-recomposition]]
- [[c-mvvm-pattern]]
- https://developer.android.com/jetpack/compose/architecture
- https://developer.android.com/jetpack/compose/mental-model

## Related Questions

### Prerequisites (Easier)
- Understanding of declarative UI patterns
- Basic Kotlin knowledge

### Related (Same Level)
- [[q-compose-modifier-order-performance--android--medium]] — Modifier order optimization
- State management patterns and best practices

### Advanced (Harder)
- [[q-compose-stability-skippability--android--hard]] — Stability and skippability
- [[q-compose-performance-optimization--android--hard]] — Performance optimization
