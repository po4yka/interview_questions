---
id: 20251012-122802
title: Compose Canvas & Graphics / Canvas и графика в Compose
aliases: [Canvas и графика в Compose, Compose Canvas & Graphics]
topic: android
subtopics:
  - ui-compose
  - ui-graphics
question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-android-performance-measurement-tools--android--medium
  - q-animated-visibility-vs-content--android--medium
  - q-canvas-drawing-optimization--android--hard
created: 2025-10-11
updated: 2025-10-30
sources: []
tags: [android/ui-compose, android/ui-graphics, difficulty/hard]
date created: Thursday, October 30th 2025, 11:18:11 am
date modified: Thursday, October 30th 2025, 12:43:39 pm
---

# Вопрос (RU)
> Как эффективно работать с Canvas и графикой в Jetpack Compose?

# Question (EN)
> How to effectively work with Canvas and graphics in Jetpack Compose?

---

## Ответ (RU)

### Основные концепции
- **DrawScope**: рисование в immediate-режиме внутри `Canvas(modifier) { ... }`
- **State**: рекомпозиция триггерит перерисовку; минимизируйте записи состояния в hot paths
- **Remember/кэширование**: предвычисляйте пути/битмапы; избегайте аллокаций в draw-лямбдах
- **Clipping/alpha/layers**: применяйте только где нужно (дорого); предпочитайте геометрические тесты

### Паттерны

**Кэширование дорогих фигур**:
```kotlin
// ✅ ПРАВИЛЬНО: предвычисление path в remember
@Composable
fun Star(modifier: Modifier = Modifier, points: Int, size: Size) {
  val path = remember(points, size) { buildStarPath(points, size) }
  Canvas(modifier) { drawPath(path, color = Color.Yellow) }
}

// ❌ НЕПРАВИЛЬНО: создание path при каждой отрисовке
@Composable
fun SlowStar(modifier: Modifier = Modifier, points: Int, size: Size) {
  Canvas(modifier) {
    val path = buildStarPath(points, size) // аллокация в draw!
    drawPath(path, color = Color.Yellow)
  }
}
```

**Переиспользование объектов**:
```kotlin
// ✅ ПРАВИЛЬНО: reset вместо новых Path
@Composable
fun Lines(modifier: Modifier = Modifier, data: List<Offset>) {
  val path = remember { Path() }
  Canvas(modifier) {
    path.reset()
    if (data.isNotEmpty()) {
      path.moveTo(data[0].x, data[0].y)
      for (i in 1 until data.size) path.lineTo(data[i].x, data[i].y)
      drawPath(path, Color.Cyan, style = Stroke(3f))
    }
  }
}
```

**Clipping по видимым границам**:
```kotlin
// ✅ ПРАВИЛЬНО: отрисовка только видимых элементов
Canvas(Modifier.fillMaxSize()) {
  val clip = clipBounds
  items.forEach { item ->
    if (item.bounds.overlaps(clip)) drawItem(item)
  }
}
```

**Слои для анимаций**:
```kotlin
// ✅ ИСПОЛЬЗУЙТЕ ЭКОНОМНО: graphicsLayer для GPU-акселерации
Canvas(Modifier.graphicsLayer(alpha = 0.9f)) { /* draw */ }
```

### Чеклист производительности
- Предвычисляйте пути/битмапы в `remember`; никаких новых объектов в draw
- Используйте `Stroke`/`Brush` осторожно; избегайте лишнего альфа-блендинга
- Клиппинг только когда нужно; предпочитайте геометрическую отсечку
- Профилируйте с Perfetto + `Trace.beginSection` в custom коде
- Бенчмаркинг с Macrobenchmark (render jank, frame time)

## Answer (EN)

### Core Concepts
- **DrawScope**: immediate mode drawing inside `Canvas(modifier) { ... }`
- **State**: recomposition drives re-draw; minimize state writes in hot paths
- **Remember/caching**: precompute paths/bitmaps; avoid allocations in draw lambdas
- **Clipping/alpha/layers**: apply only where needed (costly); prefer geometry tests

### Patterns

**Caching expensive shapes**:
```kotlin
// ✅ CORRECT: precompute path in remember
@Composable
fun Star(modifier: Modifier = Modifier, points: Int, size: Size) {
  val path = remember(points, size) { buildStarPath(points, size) }
  Canvas(modifier) { drawPath(path, color = Color.Yellow) }
}

// ❌ WRONG: creating path on every draw
@Composable
fun SlowStar(modifier: Modifier = Modifier, points: Int, size: Size) {
  Canvas(modifier) {
    val path = buildStarPath(points, size) // allocation in draw!
    drawPath(path, color = Color.Yellow)
  }
}
```

**Reusing objects**:
```kotlin
// ✅ CORRECT: reset instead of new Path
@Composable
fun Lines(modifier: Modifier = Modifier, data: List<Offset>) {
  val path = remember { Path() }
  Canvas(modifier) {
    path.reset()
    if (data.isNotEmpty()) {
      path.moveTo(data[0].x, data[0].y)
      for (i in 1 until data.size) path.lineTo(data[i].x, data[i].y)
      drawPath(path, Color.Cyan, style = Stroke(3f))
    }
  }
}
```

**Clipping to visible bounds**:
```kotlin
// ✅ CORRECT: draw only visible items
Canvas(Modifier.fillMaxSize()) {
  val clip = clipBounds
  items.forEach { item ->
    if (item.bounds.overlaps(clip)) drawItem(item)
  }
}
```

**Layers for animations**:
```kotlin
// ✅ USE SPARINGLY: graphicsLayer for GPU acceleration
Canvas(Modifier.graphicsLayer(alpha = 0.9f)) { /* draw */ }
```

### Performance Checklist
- Precompute paths/bitmaps in `remember`; no new objects in draw
- Use `Stroke`/`Brush` judiciously; avoid unnecessary alpha blending
- Clip only when needed; prefer geometric culling
- Profile with Perfetto + `Trace.beginSection` in custom code
- Benchmark with Macrobenchmark (render jank, frame time)

## Follow-ups
- How to structure state for large canvases (tiling/virtualization)?
- When to switch to custom Views for extreme performance cases?
- How to share drawing caches across recompositions/screens?
- How to handle complex paths with bezier curves efficiently?
- What's the difference between `drawWithCache` and `remember` for Canvas?

## References
- [[c-compose-state]] - State management in Compose
- [[c-compose-recomposition]] - Recomposition lifecycle
- [[c-remember-derivedstateof]] - Memoization patterns
- [[c-android-graphics-pipeline]] - Graphics rendering fundamentals
- https://developer.android.com/develop/ui/compose/graphics/draw/overview
- https://perfetto.dev
- https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview

## Related Questions

### Prerequisites (Easier)
- [[q-android-performance-measurement-tools--android--medium]] - Profiling and benchmarking tools
- [[q-animated-visibility-vs-content--android--medium]] - Animation performance basics

### Related (Same Level)
- [[q-canvas-drawing-optimization--android--hard]] - Advanced drawing optimization techniques
- [[q-compose-custom-layout--android--hard]] - Custom layout performance
- [[q-compose-remember-derivedstateof--android--medium]] - State optimization patterns

### Advanced (Harder)
- [[q-android-runtime-art--android--medium]] - Runtime and memory management
- [[q-compose-performance-optimization--android--hard]] - Comprehensive Compose performance
