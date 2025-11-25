---
id: android-076
title: AnimatedVisibility vs AnimatedContent vs Crossfade / AnimatedVisibility против AnimatedContent против Crossfade
aliases: [AnimatedVisibility vs AnimatedContent vs Crossfade, AnimatedVisibility против AnimatedContent против Crossfade]
topic: android
subtopics:
  - ui-animation
  - ui-compose
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-compose-recomposition
  - c-jetpack-compose
  - q-android-jetpack-overview--android--easy
  - q-compose-custom-animations--android--medium
  - q-compose-gesture-detection--android--medium
  - q-compose-semantics--android--medium
created: 2025-10-13
updated: 2025-11-10
tags: [android/ui-animation, android/ui-compose, animation, compose, difficulty/medium]
sources: []
date created: Saturday, November 1st 2025, 1:03:10 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---

# Вопрос (RU)
> В чем разница между AnimatedVisibility, AnimatedContent и Crossfade в Jetpack Compose?

---

# Question (EN)
> What is the difference between AnimatedVisibility, AnimatedContent, and Crossfade in Jetpack Compose?

---

## Ответ (RU)

Compose предоставляет три специализированных API для анимации контента с разной семантикой управления композицией.

### AnimatedVisibility
Управляет присутствием composable в дереве композиции. Добавляет/удаляет узлы с настраиваемыми enter/exit переходами.

```kotlin
AnimatedVisibility(
    visible = expanded,
    enter = expandVertically() + fadeIn(),
    exit = shrinkVertically() + fadeOut()
) {
    DetailContent()
}
```

**Применение**: раскрывающиеся секции, модальные окна, условный UI.

### AnimatedContent
Переключает между состояниями с полным контролем направления анимации. Во время перехода исходное и целевое содержимое могут одновременно участвовать в измерении/отрисовке, чтобы сформировать анимацию.

```kotlin
AnimatedContent(
    targetState = currentState,
    transitionSpec = {
        slideInHorizontally { it } togetherWith slideOutHorizontally { -it }
    }
) { state ->
    when (state) {
        Loading -> LoadingIndicator()
        Success -> Content()
    }
}
```

**Применение**: state-машины (loading/success/error), пагинация, wizard-формы.

### Crossfade
Упрощенная версия AnimatedContent только для fade-переходов. Минималистичный API: тип анимации зафиксирован как crossfade, но длительность/интерполяцию можно настраивать через `animationSpec`.

```kotlin
Crossfade(targetState = screen) { currentScreen ->
    when (currentScreen) {
        Home -> HomeScreen()
        Profile -> ProfileScreen()
    }
}
```

**Применение**: прототипирование, простые переключения экранов.

### Ключевые Различия

- AnimatedVisibility: управляет добавлением/удалением из композиции, освобождает ресурсы после завершения hide-анимации.
- AnimatedContent: анимированное переключение состояний с гибкими переходами, старое и новое содержимое участвуют в композиции во время анимации.
- Crossfade: простой fade-переход между состояниями без настройки типа анимации.

---

## Answer (EN)

Compose provides three specialized APIs for content animation with different composition management semantics.

### AnimatedVisibility
Controls composable presence in the composition tree. Adds/removes nodes with customizable enter/exit transitions.

```kotlin
AnimatedVisibility(
    visible = expanded,
    enter = expandVertically() + fadeIn(),
    exit = shrinkVertically() + fadeOut()
) {
    DetailContent()
}
```

**Use case**: expandable sections, modals, conditional UI.

### AnimatedContent
Switches between states with detailed control over the transition (including direction). During the transition, both the previous and target content can be measured/placed/drawn simultaneously to produce the animation.

```kotlin
AnimatedContent(
    targetState = currentState,
    transitionSpec = {
        slideInHorizontally { it } togetherWith slideOutHorizontally { -it }
    }
) { state ->
    when (state) {
        Loading -> LoadingIndicator()
        Success -> Content()
    }
}
```

**Use case**: state machines (loading/success/error), pagination, wizard forms.

### Crossfade
A simplified AnimatedContent variant for fade-only transitions. Minimal API: the transition type is fixed to crossfade, but you can still adjust duration/easing via `animationSpec`.

```kotlin
Crossfade(targetState = screen) { currentScreen ->
    when (currentScreen) {
        Home -> HomeScreen()
        Profile -> ProfileScreen()
    }
}
```

**Use case**: prototyping, simple screen switching.

### Key Differences

- AnimatedVisibility: controls appearance/disappearance and removes content from composition after the hide animation.
- AnimatedContent: animates transitions between states with flexible specs; old and new content coexist during the transition.
- Crossfade: fixed fade transition for simple switches.

---

## Дополнительные Вопросы (RU)

- Как `AnimatedVisibility` обрабатывает прерывания, когда видимость меняется во время анимации?
- Каковы последствия для производительности, когда старое и новое содержимое одновременно участвуют в композиции в `AnimatedContent` / `Crossfade`?
- Как создавать кастомные enter/exit переходы сверх встроенных?
- В каких случаях лучше использовать модификатор `animateEnterExit` вместо обертки `AnimatedVisibility`?
- Что происходит с состоянием и побочными эффектами composable-элементов, удаляемых через `AnimatedVisibility`?

---

## Follow-ups

- How does `AnimatedVisibility` handle interruptions when visibility changes mid-animation?
- What are the performance implications of both contents participating in composition during `AnimatedContent` / `Crossfade` transitions?
- How do you create custom enter/exit transitions beyond the built-in ones?
- When should you use the `animateEnterExit` modifier instead of wrapping with `AnimatedVisibility`?
- What happens to state and side effects in composables removed by `AnimatedVisibility`?

---

## Ссылки (RU)

- [[c-jetpack-compose]]
- https://developer.android.com/jetpack/compose/animation/composables-modifiers
- https://developer.android.com/develop/ui/compose/animation/introduction

---

## References

- [[c-jetpack-compose]]
- https://developer.android.com/jetpack/compose/animation/composables-modifiers
- https://developer.android.com/develop/ui/compose/animation/introduction

---

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-android-jetpack-overview--android--easy]]

### Связанные (средний уровень)
- [[c-compose-recomposition]]

### Продвинутое (сложнее)
- [[q-android-app-lag-analysis--android--medium]]

---

## Related Questions

### Prerequisites (Easier)
- [[q-android-jetpack-overview--android--easy]]

### Related (Same Level)
- [[c-compose-recomposition]]

### Advanced (Harder)
- [[q-android-app-lag-analysis--android--medium]]
