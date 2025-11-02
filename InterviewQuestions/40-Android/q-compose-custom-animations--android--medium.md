---
id: android-073
title: Compose Custom Animations / Кастомные анимации Compose
aliases: [Compose Custom Animations, Кастомные анимации Compose]
topic: android
subtopics: [ui-animation, ui-compose]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - q-animated-visibility-vs-content--android--medium
  - q-how-to-create-animations-in-android--android--medium
  - q-vector-graphics-animations--android--medium
  - q-jetpack-compose-basics--android--medium
created: 2025-10-13
updated: 2025-10-29
tags: [android/ui-animation, android/ui-compose, difficulty/medium]
sources: []
date created: Thursday, October 30th 2025, 11:18:59 am
date modified: Thursday, October 30th 2025, 12:43:41 pm
---

# Вопрос (RU)
> Как реализовать кастомные анимации в Jetpack Compose и когда использовать разные Animation API?

# Question (EN)
> How to implement custom animations in Jetpack Compose and when to use different Animation APIs?

---

## Ответ (RU)

### Выбор Animation API

**animate*AsState** — декларативный, для простых анимаций состояния:
- Автоматическая отмена при изменении целевого значения
- Минимальный boilerplate
- Для анимаций одиночных свойств

**Animatable** — императивный контроль для сложных сценариев:
- Последовательные и параллельные анимации
- Прерывание и возобновление
- Жестовые анимации с управлением скоростью

**Transition** — координация нескольких анимированных значений:
- Синхронизация связанных свойств
- Инспектирование через Layout Inspector
- Consistent timing для группы анимаций

### Примеры реализации

**animate*AsState** (декларативный):
```kotlin
@Composable
fun PulsingButton(expanded: Boolean) {
  // ✅ Автоматически отменяется при изменении expanded
  val scale by animateFloatAsState(
    targetValue = if (expanded) 1.2f else 1f,
    animationSpec = spring(stiffness = Spring.StiffnessLow)
  )
  Box(Modifier.graphicsLayer {
    scaleX = scale
    scaleY = scale
  })
}
```

**Animatable** (императивный):
```kotlin
@Composable
fun GestureAnimation(targetOffset: Float) {
  val offset = remember { Animatable(0f) }

  LaunchedEffect(targetOffset) {
    // ✅ Контроль последовательности и прерываний
    offset.animateTo(
      targetValue = targetOffset,
      animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy)
    )
  }

  Box(Modifier.offset(x = offset.value.dp))
}
```

**Transition** (координация):
```kotlin
@Composable
fun AnimatedCard(isExpanded: Boolean) {
  val transition = updateTransition(isExpanded, label = "card_expand")

  // ✅ Все анимации синхронизированы
  val alpha by transition.animateFloat(label = "alpha") {
    if (it) 1f else 0.6f
  }
  val elevation by transition.animateDp(label = "elevation") {
    if (it) 8.dp else 2.dp
  }
  val cornerRadius by transition.animateDp(label = "corner") {
    if (it) 24.dp else 8.dp
  }

  Card(
    modifier = Modifier.alpha(alpha).shadow(elevation),
    shape = RoundedCornerShape(cornerRadius)
  ) { /* content */ }
}
```

### AnimationSpec стратегии

**spring()** — естественное поведение с физикой:
- Прерываемые анимации без рывков
- Адаптивная продолжительность
- Подходит для жестовых интерфейсов

**tween()** — контролируемая продолжительность:
- Предсказуемый timing
- Easing функции для характера анимации
- Подходит для переходов UI

**keyframes()** — точный контроль в промежуточных точках:
- Сложные траектории
- Кастомные кривые анимации

### Оптимизация производительности

- Используйте `graphicsLayer` вместо `offset`/`size` для hardware-accelerated анимаций
- Ограничивайте recomposition через `derivedStateOf` для вычисляемых значений
- Избегайте lambda allocations в animationSpec
- `Modifier.animateContentSize()` для layout-based анимаций
- Профилируйте через Layout Inspector (animation preview) и Macrobenchmark

## Answer (EN)

### Choosing Animation API

**animate*AsState** — declarative, for simple state animations:
- Automatic cancellation on target value change
- Minimal boilerplate
- For single property animations

**Animatable** — imperative control for complex scenarios:
- Sequential and parallel animations
- Interruption and resumption handling
- Gesture-driven animations with velocity control

**Transition** — coordinate multiple animated values:
- Synchronize related properties
- Inspectable through Layout Inspector
- Consistent timing for animation groups

### Implementation Examples

**animate*AsState** (declarative):
```kotlin
@Composable
fun PulsingButton(expanded: Boolean) {
  // ✅ Automatically cancels when expanded changes
  val scale by animateFloatAsState(
    targetValue = if (expanded) 1.2f else 1f,
    animationSpec = spring(stiffness = Spring.StiffnessLow)
  )
  Box(Modifier.graphicsLayer {
    scaleX = scale
    scaleY = scale
  })
}
```

**Animatable** (imperative):
```kotlin
@Composable
fun GestureAnimation(targetOffset: Float) {
  val offset = remember { Animatable(0f) }

  LaunchedEffect(targetOffset) {
    // ✅ Sequence control and interruption handling
    offset.animateTo(
      targetValue = targetOffset,
      animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy)
    )
  }

  Box(Modifier.offset(x = offset.value.dp))
}
```

**Transition** (coordination):
```kotlin
@Composable
fun AnimatedCard(isExpanded: Boolean) {
  val transition = updateTransition(isExpanded, label = "card_expand")

  // ✅ All animations synchronized
  val alpha by transition.animateFloat(label = "alpha") {
    if (it) 1f else 0.6f
  }
  val elevation by transition.animateDp(label = "elevation") {
    if (it) 8.dp else 2.dp
  }
  val cornerRadius by transition.animateDp(label = "corner") {
    if (it) 24.dp else 8.dp
  }

  Card(
    modifier = Modifier.alpha(alpha).shadow(elevation),
    shape = RoundedCornerShape(cornerRadius)
  ) { /* content */ }
}
```

### AnimationSpec Strategies

**spring()** — natural physics-based behavior:
- Interruptible animations without jarring
- Adaptive duration
- Suitable for gesture-driven interfaces

**tween()** — controlled duration:
- Predictable timing
- Easing functions for animation character
- Suitable for UI transitions

**keyframes()** — precise control at intermediate points:
- Complex trajectories
- Custom animation curves

### Performance Optimization

- Use `graphicsLayer` instead of `offset`/`size` for hardware-accelerated animations
- Limit recomposition via `derivedStateOf` for computed values
- Avoid lambda allocations in animationSpec
- `Modifier.animateContentSize()` for layout-based animations
- Profile with Layout Inspector (animation preview) and Macrobenchmark

---

## Follow-ups

- How to sequence multiple animations with different delays and durations?
- When does `Transition` provide better performance than multiple independent `animate*AsState` calls?
- How to implement gesture-driven animations with velocity tracking using `Animatable`?
- What are the memory implications of using `rememberInfiniteTransition` for continuous animations?
- How to test animations in composables using Compose Testing APIs?

## References

- [[c-jetpack-compose]] - Jetpack Compose concepts and architecture
- [[q-jetpack-compose-basics--android--medium]] - Compose fundamentals
- [[q-animated-visibility-vs-content--android--medium]] - AnimatedVisibility vs AnimatedContent
- https://developer.android.com/develop/ui/compose/animation/introduction
- https://developer.android.com/develop/ui/compose/animation/quick-guide

## Related Questions

### Prerequisites (Easier)
- [[q-jetpack-compose-basics--android--medium]] - Understanding Compose fundamentals and state
- [[q-how-to-create-animations-in-android--android--medium]] - Basic Android animation concepts

### Related (Same Level)
- [[q-animated-visibility-vs-content--android--medium]] - Choosing between AnimatedVisibility and AnimatedContent
- [[q-vector-graphics-animations--android--medium]] - Animating vector graphics in Compose
- [[q-remember-remembersaveable--android--medium]] - State preservation patterns in Compose

### Advanced (Harder)
- [[q-how-to-reduce-the-number-of-recompositions-besides-side-effects--android--hard]] - Performance optimization techniques
- [[q-compose-compiler-plugin--android--hard]] - Understanding Compose compiler optimizations
