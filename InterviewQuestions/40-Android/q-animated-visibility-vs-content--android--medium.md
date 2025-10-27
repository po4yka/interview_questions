---
id: 20251012-122777
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
  - q-android-architectural-patterns--android--medium
  - q-android-performance-measurement-tools--android--medium
  - q-android-testing-strategies--android--medium
created: 2025-10-13
updated: 2025-01-27
tags: [android/ui-animation, android/ui-compose, difficulty/medium]
sources: []
---
# Вопрос (RU)
> В чем разница между AnimatedVisibility, AnimatedContent и Crossfade в Jetpack Compose?

---

# Question (EN)
> What is the difference between AnimatedVisibility, AnimatedContent, and Crossfade in Jetpack Compose?

---

## Ответ (RU)

**Три основных API анимации в Compose** решают разные задачи: AnimatedVisibility для показа/скрытия, AnimatedContent для смены контента по состоянию, и Crossfade для простых переходов с затуханием.

**1. AnimatedVisibility:**
Анимирует появление/исчезновение контента с настраиваемыми enter/exit переходами.

```kotlin
@Composable
fun ExpandableCard() {
    var expanded by remember { mutableStateOf(false) }

    Card(modifier = Modifier.clickable { expanded = !expanded }) {
        Column {
            Text("Заголовок")
            AnimatedVisibility(
                visible = expanded,
                enter = expandVertically() + fadeIn(),  // ✅ Комбинация анимаций
                exit = shrinkVertically() + fadeOut()
            ) {
                Text("Развернутый контент")
            }
        }
    }
}
```

**2. AnimatedContent:**
Переключает между разными composable по целевому состоянию с полным контролем направления анимации.

```kotlin
@Composable
fun LoadingStates() {
    var state by remember { mutableStateOf(LoadingState.Loading) }

    AnimatedContent(
        targetState = state,
        transitionSpec = {
            // ✅ Направленные анимации на основе состояния
            if (targetState > initialState) {
                slideInVertically { it } togetherWith slideOutVertically { -it }
            } else {
                slideInVertically { -it } togetherWith slideOutVertically { it }
            }
        }
    ) { currentState ->
        when (currentState) {
            LoadingState.Loading -> CircularProgressIndicator()
            LoadingState.Success -> Text("Успех!")
            LoadingState.Error -> Text("Ошибка")
        }
    }
}
```

**3. Crossfade:**
Простое затухание между состояниями без дополнительных настроек.

```kotlin
@Composable
fun SimpleSwitcher() {
    var screen by remember { mutableStateOf("Home") }

    // ✅ Минималистичный API для базовых переходов
    Crossfade(targetState = screen) { currentScreen ->
        when (currentScreen) {
            "Home" -> HomeScreen()
            "Profile" -> ProfileScreen()
        }
    }
}
```

**Сравнение API:**

| Критерий | AnimatedVisibility | AnimatedContent | Crossfade |
|---------|-------------------|-----------------|-----------|
| Сценарий | Показ/скрытие | Смена по состоянию | Простое переключение |
| Типы анимаций | Enter/exit | Кастомные | Только fade |
| Контроль направления | Да | Да | Нет |
| Анимация размера | Да | Да | Нет |
| Сложность | Средняя | Высокая | Низкая |

**Когда использовать:**

- **AnimatedVisibility**: раскрывающиеся секции, тултипы, опциональные элементы
- **AnimatedContent**: экраны с состояниями (loading/success/error), wizard-формы, карусели
- **Crossfade**: быстрое прототипирование, минимальные требования к анимации

**Важные детали:**
- AnimatedVisibility управляет композицией (добавляет/удаляет из дерева)
- AnimatedContent всегда хранит оба состояния во время перехода
- Crossfade — специализированная версия AnimatedContent для fade-переходов
- Все три API являются частью [[c-jetpack-compose]] animation framework

## Answer (EN)

**Three core Compose animation APIs** serve distinct purposes: AnimatedVisibility for show/hide, AnimatedContent for state-based content switching, and Crossfade for simple fade transitions.

**1. AnimatedVisibility:**
Animates content appearance/disappearance with customizable enter/exit transitions.

```kotlin
@Composable
fun ExpandableCard() {
    var expanded by remember { mutableStateOf(false) }

    Card(modifier = Modifier.clickable { expanded = !expanded }) {
        Column {
            Text("Header")
            AnimatedVisibility(
                visible = expanded,
                enter = expandVertically() + fadeIn(),  // ✅ Combined animations
                exit = shrinkVertically() + fadeOut()
            ) {
                Text("Expanded content")
            }
        }
    }
}
```

**2. AnimatedContent:**
Switches between different composables based on target state with full directional control.

```kotlin
@Composable
fun LoadingStates() {
    var state by remember { mutableStateOf(LoadingState.Loading) }

    AnimatedContent(
        targetState = state,
        transitionSpec = {
            // ✅ Directional animations based on state
            if (targetState > initialState) {
                slideInVertically { it } togetherWith slideOutVertically { -it }
            } else {
                slideInVertically { -it } togetherWith slideOutVertically { it }
            }
        }
    ) { currentState ->
        when (currentState) {
            LoadingState.Loading -> CircularProgressIndicator()
            LoadingState.Success -> Text("Success!")
            LoadingState.Error -> Text("Error")
        }
    }
}
```

**3. Crossfade:**
Simple fade transition between states without additional configuration.

```kotlin
@Composable
fun SimpleSwitcher() {
    var screen by remember { mutableStateOf("Home") }

    // ✅ Minimalist API for basic transitions
    Crossfade(targetState = screen) { currentScreen ->
        when (currentScreen) {
            "Home" -> HomeScreen()
            "Profile" -> ProfileScreen()
        }
    }
}
```

**API Comparison:**

| Criterion | AnimatedVisibility | AnimatedContent | Crossfade |
|---------|-------------------|-----------------|-----------|
| Use Case | Show/hide | State-based switching | Simple switching |
| Animation Types | Enter/exit | Custom | Fade only |
| Direction Control | Yes | Yes | No |
| Size Animation | Yes | Yes | No |
| Complexity | Medium | High | Low |

**When to Use:**

- **AnimatedVisibility**: expandable sections, tooltips, optional UI elements
- **AnimatedContent**: loading/success/error states, wizard forms, carousels
- **Crossfade**: rapid prototyping, minimal animation requirements

**Key Details:**
- AnimatedVisibility manages composition (adds/removes from tree)
- AnimatedContent always keeps both states during transition
- Crossfade is a specialized AnimatedContent for fade-only transitions
- All three APIs are part of [[c-jetpack-compose]] animation framework

---

## Follow-ups

- How do you optimize performance when animating large composable trees?
- What are the trade-offs between AnimatedContent transitionSpec customization and complexity?
- When should you use animateEnterExit modifier instead of AnimatedVisibility?
- How do you handle interruptions in mid-transition for AnimatedContent?

## References

- [[c-jetpack-compose]]
- https://developer.android.com/jetpack/compose/animation

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]]
- [[q-android-project-parts--android--easy]]

### Related (Same Level)
- [[q-android-testing-strategies--android--medium]]
- [[q-android-architectural-patterns--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]