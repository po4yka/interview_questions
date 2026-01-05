---
id: android-072
title: Compose Core Components / Основные компоненты Compose
aliases: [Compose Components, Jetpack Compose Architecture, Архитектура Jetpack Compose, Основные компоненты Compose]
topic: android
subtopics: [architecture-mvvm, ui-compose]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-recomposition, c-compose-state, c-mvvm-pattern, q-compose-modifier-order-performance--android--medium, q-compose-stability-skippability--android--hard, q-how-jetpack-compose-works--android--medium, q-migration-to-compose--android--medium, q-what-are-the-most-important-components-of-compose--android--medium]
created: 2025-10-13
updated: 2025-11-10
tags: [android/architecture-mvvm, android/ui-compose, declarative-ui, difficulty/medium, jetpack-compose]
sources:
  - "https://developer.android.com/jetpack/compose/architecture"
---
# Вопрос (RU)
> Из каких более важных компонентов состоит Compose?

# Question (EN)
> What are the most important components that make up Compose?

## Ответ (RU)

Jetpack Compose в контексте архитектуры и разработки UI можно рассматривать как набор из восьми ключевых концепций, которые работают вместе для создания декларативного UI-фреймворка (это не официальная каноническая классификация, а практическое разбиение для собеседований).

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

**5. Recomposition** — механизм интеллектуального обновления UI при изменении состояния (переотрисовываются только composable, зависящие от изменившегося состояния).

**6. Effect Handlers** — управление побочными эффектами и lifecycle с помощью специальных API Compose (примеры, не исчерпывающий список):
- `LaunchedEffect` — запуск suspend-кода, привязанного к жизненному циклу composable
- `DisposableEffect` — освобождение ресурсов при выходе composable из композиции
- `SideEffect` — синхронизация с внешним (non-Compose) состоянием

**7. Material Components** — готовые UI-компоненты по Material Design (`Button`, `TextField`, `Card` и др.), построенные поверх базовых возможностей Compose.

**8. Theme System** — централизованная стилизация через систему тем (`MaterialTheme` и связанные CompositionLocal), обеспечивающая единый дизайн.

## Answer (EN)

From a practical architecture and UI-development perspective, Jetpack Compose can be viewed as eight key concepts that work together to form the declarative UI framework (this is an interview-oriented breakdown, not an official canonical list).

### Core Components

**1. Composable Functions** — the basic building blocks of UI annotated with ``@Composable``:
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

**2. State Management** — manages UI updates through `remember` and `mutableStateOf`, driving changes via [[c-compose-recomposition]]:
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

**5. Recomposition** — the smart UI update mechanism when state changes (only composables that depend on the changed state are recomposed).

**6. Effect Handlers** — APIs for managing side effects and lifecycle-related work (examples, not exhaustive):
- `LaunchedEffect` — runs suspend code tied to the composable's lifecycle
- `DisposableEffect` — performs resource cleanup when the composable leaves the composition
- `SideEffect` — synchronizes with external (non-Compose) state

**7. Material Components** — pre-built UI components following Material Design (`Button`, `TextField`, `Card`, etc.), built on top of core Compose.

**8. Theme System** — centralized styling through the theming system (`MaterialTheme` and related CompositionLocals) to provide a consistent design.

## Дополнительные Вопросы (RU)

- Как recomposition в Compose отличается от традиционных обновлений `View`?
- Каковы последствия для производительности при подъёме состояния (state hoisting)?
- Как отлаживать проблемы с recomposition в Compose?
- Когда следует использовать `LaunchedEffect` vs `DisposableEffect` vs `SideEffect`?
- Как Compose обрабатывает изменения конфигурации по сравнению с традиционными `View`?

## Follow-ups

- How does Compose's recomposition differ from traditional `View` updates?
- What are the performance implications of state hoisting?
- How do you debug recomposition issues in Compose?
- When should you use `LaunchedEffect` vs `DisposableEffect` vs `SideEffect`?
- How does Compose handle configuration changes compared to traditional `View`s?

## Ссылки (RU)

- [[c-compose-state]]
- [[c-compose-recomposition]]
- [[c-mvvm-pattern]]
- https://developer.android.com/jetpack/compose/architecture
- https://developer.android.com/jetpack/compose/mental-model

## References

- [[c-compose-state]]
- [[c-compose-recomposition]]
- [[c-mvvm-pattern]]
- https://developer.android.com/jetpack/compose/architecture
- https://developer.android.com/jetpack/compose/mental-model

## Связанные Вопросы (RU)

### Предпосылки (Проще)
- Понимание декларативных UI-паттернов
- Базовые знания Kotlin

### Связанные (Тот Же уровень)
- [[q-compose-modifier-order-performance--android--medium]] — Оптимизация порядка `Modifier`
- Паттерны и лучшие практики управления состоянием

### Продвинутые (Сложнее)
- [[q-compose-stability-skippability--android--hard]] — Стабильность и возможность пропуска
- [[q-compose-performance-optimization--android--hard]] — Оптимизация производительности

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
