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
updated: 2025-10-20
tags: [android/ui-animation, android/ui-compose, difficulty/medium]
date created: Saturday, October 25th 2025, 1:26:29 pm
date modified: Saturday, October 25th 2025, 4:52:41 pm
---

# Вопрос (RU)
> Кастомные анимации Compose?

# Question (EN)
> Compose Custom Animations?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Choosing the API
- `animate*AsState`: declarative, simple target‑based, auto‑cancellable on state change
- `Animatable`: imperative control, sequences, interruption, springs/tweens manually

### Minimal Patterns

animate*AsState (declarative):
```kotlin
@Composable
fun Pulse(expanded: Boolean) {
  val scale by animateFloatAsState(if (expanded) 1.2f else 1f, animationSpec = spring())
  Box(Modifier.size(48.dp).graphicsLayer(scaleX = scale, scaleY = scale))
}
```

Animatable (imperative):
```kotlin
@Composable
fun SwipeProgress(target: Float) {
  val progress = remember { Animatable(0f) }
  LaunchedEffect(target) { progress.animateTo(target, spring(dampingRatio = Spring.DampingRatioNoBouncy)) }
  LinearProgressIndicator(progress.value)
}
```

Sequencing and interruption:
```kotlin
LaunchedEffect(Unit) {
  progress.snapTo(0f)
  progress.animateTo(0.5f, tween())
  if (!isActive) return@LaunchedEffect
  progress.animateTo(1f, spring())
}
```

Transition API for multiple values:
```kotlin
@Composable
fun CardTransition(expanded: Boolean) {
  val t = updateTransition(expanded, label = "expansion")
  val alpha by t.animateFloat(label = "alpha") { if (it) 1f else 0.6f }
  val corner by t.animateDp(label = "radius") { if (it) 24.dp else 8.dp }
  Card(Modifier.alpha(alpha), shape = RoundedCornerShape(corner)) { /* ... */ }
}
```

### Specs and Performance
- Specs: `spring` (natural), `tween` (time‑based), `keyframes`, `snap`
- Prefer springs for interruptible UX; use `FastOutSlowInEasing` etc. for material feel
- Avoid allocations in animation lambdas; hoist state; limit recomposition to animated subtree
- Profile with Layout Inspector/Perfetto; measure jank

## Follow-ups
- When to prefer `animate*AsState` vs `Animatable` vs `Transition`?
- How to structure animation state to avoid recomposition storms?
- How to benchmark animation jank in CI (Macrobenchmark)?

## References
- [[c-algorithms]] - Animation interpolation and timing algorithms
- https://developer.android.com/develop/ui/compose/animation
- https://developer.android.com/develop/ui/compose/performance

## Related Questions

### Prerequisites (Easier)
- [[q-animated-visibility-vs-content--android--medium]]

### Related (Same Level)
- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-canvas-graphics--android--hard]]

### Advanced (Harder)
- [[q-android-performance-measurement-tools--android--medium]]
