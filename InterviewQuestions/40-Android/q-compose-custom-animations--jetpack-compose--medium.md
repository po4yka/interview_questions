---
id: 20251012-1227101
title: Compose Custom Animations / Кастомные анимации Compose
aliases: [Compose Custom Animations, Кастомные анимации Compose]
topic: android
subtopics: [ui-compose, animations]
question_kind: android
difficulty: medium
status: draft
moc: moc-android
related: [q-animated-visibility-vs-content--jetpack-compose--medium, q-compose-compiler-plugin--jetpack-compose--hard, q-android-performance-measurement-tools--android--medium]
created: 2025-10-13
updated: 2025-10-20
original_language: en
language_tags: [en, ru]
tags: [android/ui-compose, android/animations, compose, animatable, difficulty/medium]
---

# Question (EN)
> How do you build custom animations in Compose using `animate*AsState` and `Animatable` (state, specs, interruption, and performance)?

# Вопрос (RU)
> Как строить кастомные анимации в Compose с `animate*AsState` и `Animatable` (state, спецификации, прерывание, производительность)?

---

## Answer (EN)

### Choosing the API
- `animate*AsState`: declarative, simple target‑based, auto‑cancellable on state change
- `Animatable`: imperative control, sequences, interruption, springs/tweens manually

### Minimal patterns

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

### Specs and performance
- Specs: `spring` (natural), `tween` (time‑based), `keyframes`, `snap`
- Prefer springs for interruptible UX; use `FastOutSlowInEasing` etc. for material feel
- Avoid allocations in animation lambdas; hoist state; limit recomposition to animated subtree
- Profile with Layout Inspector/Perfetto; measure jank

## Ответ (RU)

### Выбор API
- `animate*AsState`: декларативный, простые цели, авто‑отмена при смене состояния
- `Animatable`: императивный контроль, последовательности, прерывание, ручной выбор spring/tween

### Минимальные паттерны

animate*AsState (декларативно):
```kotlin
@Composable
fun Pulse(expanded: Boolean) {
  val scale by animateFloatAsState(if (expanded) 1.2f else 1f, animationSpec = spring())
  Box(Modifier.size(48.dp).graphicsLayer(scaleX = scale, scaleY = scale))
}
```

Animatable (императивно):
```kotlin
@Composable
fun SwipeProgress(target: Float) {
  val progress = remember { Animatable(0f) }
  LaunchedEffect(target) { progress.animateTo(target, spring(dampingRatio = Spring.DampingRatioNoBouncy)) }
  LinearProgressIndicator(progress.value)
}
```

Последовательности и прерывание:
```kotlin
LaunchedEffect(Unit) {
  progress.snapTo(0f)
  progress.animateTo(0.5f, tween())
  if (!isActive) return@LaunchedEffect
  progress.animateTo(1f, spring())
}
```

Transition API для нескольких значений:
```kotlin
@Composable
fun CardTransition(expanded: Boolean) {
  val t = updateTransition(expanded, label = "expansion")
  val alpha by t.animateFloat(label = "alpha") { if (it) 1f else 0.6f }
  val corner by t.animateDp(label = "radius") { if (it) 24.dp else 8.dp }
  Card(Modifier.alpha(alpha), shape = RoundedCornerShape(corner)) { /* ... */ }
}
```

### Спеки и производительность
- Спеки: `spring` (естественно), `tween` (по времени), `keyframes`, `snap`
- Весенние (spring) лучше для прерываемых сценариев; эйзинги для Material‑ощущения
- Не аллоцировать в лямбдах анимации; поднимать состояние; ограничивать рекомпозицию анимируемым поддеревом
- Профилировать Layout Inspector/Perfetto; измерять jank

---

## Follow-ups
- When to prefer `animate*AsState` vs `Animatable` vs `Transition`?
- How to structure animation state to avoid recomposition storms?
- How to benchmark animation jank in CI (Macrobenchmark)?

## References
- https://developer.android.com/develop/ui/compose/animation
- https://developer.android.com/develop/ui/compose/performance

## Related Questions

### Prerequisites (Easier)
- [[q-animated-visibility-vs-content--jetpack-compose--medium]]

### Related (Same Level)
- [[q-compose-compiler-plugin--jetpack-compose--hard]]
- [[q-compose-canvas-graphics--jetpack-compose--hard]]

### Advanced (Harder)
- [[q-android-performance-measurement-tools--android--medium]]

