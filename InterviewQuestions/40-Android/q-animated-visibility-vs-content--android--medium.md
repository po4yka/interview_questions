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
status: reviewed
moc: moc-android
related:
  - c-jetpack-compose
created: 2025-10-13
updated: 2025-10-30
tags: [android/ui-animation, android/ui-compose, animation, compose, difficulty/medium]
sources: []
date created: Thursday, October 30th 2025, 11:36:05 am
date modified: Sunday, November 2nd 2025, 12:52:08 pm
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
    enter = expandVertically() + fadeIn(),  // ✅ Комбинация переходов
    exit = shrinkVertically() + fadeOut()
) {
    DetailContent()  // Не существует в композиции, когда invisible
}
```

**Применение**: раскрывающиеся секции, модальные окна, условный UI.

### AnimatedContent
Переключает между состояниями с полным контролем направления анимации. Оба состояния сосуществуют во время перехода.

```kotlin
AnimatedContent(
    targetState = currentState,
    transitionSpec = {
        // ✅ Направленная анимация
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
Упрощенная версия AnimatedContent только для fade-переходов. Минималистичный API без контроля анимации.

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

| Критерий | AnimatedVisibility | AnimatedContent | Crossfade |
|---------|-------------------|-----------------|-----------|
| Управление композицией | Добавляет/удаляет | Переключает | Переключает |
| Память | Освобождает invisible | Оба в памяти | Оба в памяти |
| Анимации | Enter/exit комбинации | Полный контроль | Только fade |
| API сложность | Средняя | Высокая | Низкая |

**Выбор API**: AnimatedVisibility для условного UI, AnimatedContent для state-переходов с контролем направления, Crossfade для быстрого прототипирования.

---

## Answer (EN)

Compose provides three specialized APIs for content animation with different composition management semantics.

### AnimatedVisibility
Controls composable presence in the composition tree. Adds/removes nodes with customizable enter/exit transitions.

```kotlin
AnimatedVisibility(
    visible = expanded,
    enter = expandVertically() + fadeIn(),  // ✅ Combined transitions
    exit = shrinkVertically() + fadeOut()
) {
    DetailContent()  // Does not exist in composition when invisible
}
```

**Use case**: expandable sections, modals, conditional UI.

### AnimatedContent
Switches between states with full directional control. Both states coexist during transition.

```kotlin
AnimatedContent(
    targetState = currentState,
    transitionSpec = {
        // ✅ Directional animation
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
Simplified AnimatedContent for fade-only transitions. Minimalist API without animation control.

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

| Criterion | AnimatedVisibility | AnimatedContent | Crossfade |
|---------|-------------------|-----------------|-----------|
| Composition Control | Adds/removes | Switches | Switches |
| Memory | Frees invisible | Both in memory | Both in memory |
| Animations | Enter/exit combinations | Full control | Fade only |
| API Complexity | Medium | High | Low |

**API Selection**: AnimatedVisibility for conditional UI, AnimatedContent for state transitions with directional control, Crossfade for rapid prototyping.

---

## Follow-ups

- How does AnimatedVisibility handle interruptions when visibility changes mid-animation?
- What are the performance implications of keeping both states in memory with AnimatedContent?
- How do you create custom enter/exit transitions beyond the built-in ones?
- When should you use `animateEnterExit` modifier instead of wrapping with AnimatedVisibility?
- What happens to state and side effects in composables removed by AnimatedVisibility?

## References

- [[c-jetpack-compose]]
- https://developer.android.com/jetpack/compose/animation/composables-modifiers
- https://developer.android.com/develop/ui/compose/animation/introduction

## Related Questions

### Prerequisites (Easier)
- [[q-jetpack-compose-basics--android--medium]] - Understanding Compose fundamentals
- [[q-how-jetpack-compose-works--android--medium]] - Compose architecture

### Related (Same Level)
- Recomposition mechanics
- [[q-compose-remember-derived-state--android--medium]] - State management
- [[q-compose-modifier-system--android--medium]] - Modifier API

### Advanced (Harder)
 - Performance optimization
- [[q-compose-custom-layout--android--hard]] - Custom layout and measurement
- [[q-compose-stability-skippability--android--hard]] - Stability system
