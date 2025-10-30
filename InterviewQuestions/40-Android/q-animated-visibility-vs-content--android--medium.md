---
id: 20251012-122777
title: AnimatedVisibility vs AnimatedContent vs Crossfade / AnimatedVisibility против AnimatedContent против Crossfade
aliases: ["AnimatedVisibility vs AnimatedContent vs Crossfade", "AnimatedVisibility против AnimatedContent против Crossfade"]
topic: android
subtopics: [ui-animation, ui-compose]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, q-compose-recomposition--android--medium, q-compose-performance--android--hard]
created: 2025-10-13
updated: 2025-10-29
tags: [android/ui-animation, android/ui-compose, compose, animation, difficulty/medium]
sources: []
---
# Вопрос (RU)
> В чем разница между AnimatedVisibility, AnimatedContent и Crossfade в Jetpack Compose?

---

# Question (EN)
> What is the difference between AnimatedVisibility, AnimatedContent, and Crossfade in Jetpack Compose?

---

## Ответ (RU)

Compose предоставляет три специализированных API для анимации контента, каждый решает свою задачу.

### AnimatedVisibility
Управляет появлением/исчезновением контента с настраиваемыми переходами. Добавляет/удаляет composable из дерева композиции.

```kotlin
AnimatedVisibility(
    visible = expanded,
    enter = expandVertically() + fadeIn(),  // ✅ Комбинация переходов
    exit = shrinkVertically() + fadeOut()
) {
    DetailContent()
}
```

**Применение**: раскрывающиеся секции, тултипы, условный UI.

### AnimatedContent
Переключает между состояниями с полным контролем направления анимации. Оба состояния существуют одновременно во время перехода.

```kotlin
AnimatedContent(
    targetState = loadingState,
    transitionSpec = {
        // ✅ Направленные анимации по изменению состояния
        if (targetState > initialState) {
            slideInVertically { it } togetherWith slideOutVertically { -it }
        } else {
            slideInVertically { -it } togetherWith slideOutVertically { it }
        }
    }
) { state ->
    when (state) {
        Loading -> Spinner()
        Success -> Content()
        Error -> ErrorView()
    }
}
```

**Применение**: state машины (loading/success/error), wizard-формы, пагинация.

### Crossfade
Упрощенная версия AnimatedContent только для fade-переходов. Минималистичный API.

```kotlin
Crossfade(targetState = screen) { currentScreen ->
    when (currentScreen) {
        Home -> HomeScreen()
        Profile -> ProfileScreen()
    }
}
```

**Применение**: быстрое прототипирование, переключение экранов без сложных анимаций.

### Сравнение

| Критерий | AnimatedVisibility | AnimatedContent | Crossfade |
|---------|-------------------|-----------------|-----------|
| Управление композицией | Добавляет/удаляет | Оба состояния существуют | Оба состояния существуют |
| Типы анимаций | Enter/exit комбинации | Полный контроль | Только fade |
| Анимация размера | ✅ Да | ✅ Да | ❌ Нет |
| Сложность API | Средняя | Высокая | Низкая |

**Ключевое отличие**: AnimatedVisibility изменяет композицию, AnimatedContent/Crossfade переключают видимый контент.

## Answer (EN)

Compose provides three specialized APIs for content animation, each addressing distinct use cases.

### AnimatedVisibility
Manages content appearance/disappearance with customizable transitions. Adds/removes composables from composition tree.

```kotlin
AnimatedVisibility(
    visible = expanded,
    enter = expandVertically() + fadeIn(),  // ✅ Combined transitions
    exit = shrinkVertically() + fadeOut()
) {
    DetailContent()
}
```

**Use case**: expandable sections, tooltips, conditional UI.

### AnimatedContent
Switches between states with full directional control. Both states exist simultaneously during transition.

```kotlin
AnimatedContent(
    targetState = loadingState,
    transitionSpec = {
        // ✅ Directional animations based on state changes
        if (targetState > initialState) {
            slideInVertically { it } togetherWith slideOutVertically { -it }
        } else {
            slideInVertically { -it } togetherWith slideOutVertically { it }
        }
    }
) { state ->
    when (state) {
        Loading -> Spinner()
        Success -> Content()
        Error -> ErrorView()
    }
}
```

**Use case**: state machines (loading/success/error), wizard forms, pagination.

### Crossfade
Simplified AnimatedContent for fade-only transitions. Minimalist API.

```kotlin
Crossfade(targetState = screen) { currentScreen ->
    when (currentScreen) {
        Home -> HomeScreen()
        Profile -> ProfileScreen()
    }
}
```

**Use case**: rapid prototyping, screen switching without complex animations.

### Comparison

| Criterion | AnimatedVisibility | AnimatedContent | Crossfade |
|---------|-------------------|-----------------|-----------|
| Composition Control | Adds/removes | Both states exist | Both states exist |
| Animation Types | Enter/exit combinations | Full control | Fade only |
| Size Animation | ✅ Yes | ✅ Yes | ❌ No |
| API Complexity | Medium | High | Low |

**Key distinction**: AnimatedVisibility modifies composition, AnimatedContent/Crossfade switch visible content.

---

## Follow-ups

- How does AnimatedVisibility handle interruptions when visibility changes mid-animation?
- What are the performance implications of keeping both states in memory with AnimatedContent?
- When should you use `animateEnterExit` modifier instead of wrapping with AnimatedVisibility?
- How do you create custom enter/exit transitions beyond the built-in ones?
- What happens to state and side effects in composables removed by AnimatedVisibility?

## References

- [[c-jetpack-compose]]
- Official Compose Animation documentation: https://developer.android.com/jetpack/compose/animation

## Related Questions

### Prerequisites (Easier)
- [[q-compose-basics--android--easy]] - Understanding Compose fundamentals
- [[q-compose-state--android--easy]] - State management in Compose

### Related (Same Level)
- [[q-compose-recomposition--android--medium]] - Recomposition optimization
- [[q-compose-side-effects--android--medium]] - Side effects in Compose lifecycle

### Advanced (Harder)
- [[q-compose-performance--android--hard]] - Advanced performance optimization
- [[q-compose-custom-layouts--android--hard]] - Custom layout and measurement