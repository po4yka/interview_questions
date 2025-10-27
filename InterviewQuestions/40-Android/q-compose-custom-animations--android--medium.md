---
id: 20251012-122710
title: Compose Custom Animations / Кастомные анимации Compose
aliases: [Compose Custom Animations, Кастомные анимации Compose]
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
  - q-android-performance-measurement-tools--android--medium
  - q-animated-visibility-vs-content--android--medium
  - q-compose-compiler-plugin--android--hard
created: 2025-10-13
updated: 2025-01-27
tags: [android/ui-animation, android/ui-compose, difficulty/medium]
sources: []
---
# Вопрос (RU)
> Как реализовать кастомные анимации в Jetpack Compose и когда использовать разные Animation API?

# Question (EN)
> How to implement custom animations in Jetpack Compose and when to use different Animation APIs?

---

## Ответ (RU)

### Выбор API
- `animate*AsState`: декларативный подход, автоматическая отмена при изменении состояния
- `Animatable`: императивный контроль, последовательности, прерывания
- `Transition`: координация нескольких анимированных значений

### Паттерны

**animate*AsState** (декларативный):
```kotlin
@Composable
fun Pulse(expanded: Boolean) {
  // ✅ Автоматическая отмена при изменении expanded
  val scale by animateFloatAsState(
    targetValue = if (expanded) 1.2f else 1f,
    animationSpec = spring()
  )
  Box(Modifier.graphicsLayer(scaleX = scale, scaleY = scale))
}
```

**Animatable** (императивный):
```kotlin
@Composable
fun SwipeProgress(target: Float) {
  val progress = remember { Animatable(0f) }
  LaunchedEffect(target) {
    // ✅ Ручной контроль последовательности
    progress.animateTo(target, spring(dampingRatio = Spring.DampingRatioNoBouncy))
  }
  LinearProgressIndicator(progress = progress.value)
}
```

**Transition** (множественные значения):
```kotlin
@Composable
fun CardTransition(expanded: Boolean) {
  val transition = updateTransition(expanded, label = "card")
  val alpha by transition.animateFloat(label = "alpha") { if (it) 1f else 0.6f }
  val cornerRadius by transition.animateDp(label = "radius") { if (it) 24.dp else 8.dp }
  Card(
    modifier = Modifier.alpha(alpha),
    shape = RoundedCornerShape(cornerRadius)
  ) { /* content */ }
}
```

### Производительность
- `spring()` для естественных прерываемых анимаций
- `tween()` с easing для контролируемой продолжительности
- Избегайте аллокаций в лямбдах анимаций
- Ограничивайте рекомпозицию анимированным поддеревом
- Профилируйте через Layout Inspector и Macrobenchmark

## Answer (EN)

### Choosing the API
- `animate*AsState`: declarative, auto-cancellable on state change
- `Animatable`: imperative control, sequences, interruptions
- `Transition`: coordinate multiple animated values

### Patterns

**animate*AsState** (declarative):
```kotlin
@Composable
fun Pulse(expanded: Boolean) {
  // ✅ Automatically cancels when expanded changes
  val scale by animateFloatAsState(
    targetValue = if (expanded) 1.2f else 1f,
    animationSpec = spring()
  )
  Box(Modifier.graphicsLayer(scaleX = scale, scaleY = scale))
}
```

**Animatable** (imperative):
```kotlin
@Composable
fun SwipeProgress(target: Float) {
  val progress = remember { Animatable(0f) }
  LaunchedEffect(target) {
    // ✅ Manual sequence control
    progress.animateTo(target, spring(dampingRatio = Spring.DampingRatioNoBouncy))
  }
  LinearProgressIndicator(progress = progress.value)
}
```

**Transition** (multiple values):
```kotlin
@Composable
fun CardTransition(expanded: Boolean) {
  val transition = updateTransition(expanded, label = "card")
  val alpha by transition.animateFloat(label = "alpha") { if (it) 1f else 0.6f }
  val cornerRadius by transition.animateDp(label = "radius") { if (it) 24.dp else 8.dp }
  Card(
    modifier = Modifier.alpha(alpha),
    shape = RoundedCornerShape(cornerRadius)
  ) { /* content */ }
}
```

### Performance
- Use `spring()` for natural interruptible animations
- Use `tween()` with easing for controlled duration
- Avoid allocations in animation lambdas
- Limit recomposition to animated subtree
- Profile with Layout Inspector and Macrobenchmark

---

## Follow-ups
- How to sequence multiple animations with different timing?
- When does `Transition` provide better performance than multiple `animate*AsState` calls?
- How to implement gesture-driven animations with `Animatable`?

## References
- [[c-jetpack-compose]] - Compose fundamentals
- https://developer.android.com/develop/ui/compose/animation

## Related Questions

### Prerequisites (Easier)
- [[q-animated-visibility-vs-content--android--medium]]

### Related (Same Level)
- [[q-compose-compiler-plugin--android--hard]]

### Advanced (Harder)
- [[q-android-performance-measurement-tools--android--medium]]
