---
id: android-042
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
  - c-android-graphics
  - c-compose-ui
  - q-android-performance-measurement-tools--android--medium
  - q-compose-compiler-plugin--android--hard
  - q-compose-performance-optimization--android--hard
  - q-compose-stability-skippability--android--hard
created: 2025-10-11
updated: 2025-11-11
sources: []
tags: [android/ui-compose, android/ui-graphics, difficulty/hard]
date created: Saturday, November 1st 2025, 1:24:23 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---

# Вопрос (RU)
> Как эффективно работать с Canvas и графикой в Jetpack Compose?

# Question (EN)
> How to effectively work with Canvas and graphics in Jetpack Compose?

## Ответ (RU)

### Краткая Версия
- Используйте `Canvas`, `DrawScope` и `drawWithCache` для точного контроля рисования.
- Кэшируйте дорогие вычисления (`Path`, `ImageBitmap`) через `remember`/`drawWithCache`, избегайте лишних аллокаций при каждом перерисовывании.
- Минимизируйте использование `alpha`, сложного клиппинга и лишних слоев, особенно на больших или часто обновляемых областях.
- Профилируйте через Perfetto и бенчмарки, измеряйте реальную нагрузку.

### Подробная Версия
#### Основные Концепции
- `DrawScope`: рисование в immediate-режиме внутри `Canvas(modifier) { ... }` / `drawBehind` / `drawWithContent`.
- Состояние: изменения состояния приводят к инвалидации и перерисовке; минимизируйте записи состояния и тяжелые вычисления в горячих участках.
- `remember` / `drawWithCache` / кэширование: предвычисляйте пути/битмапы и другие дорогие структуры; избегайте лишних аллокаций в `draw`-лямбдах, особенно при частых инвалидациях.
- Clipping / alpha / слои: применяйте только где нужно (могут быть дорогими по производительности, особенно на больших поверхностях и при сложном контенте); по возможности используйте геометрическую отсечку до клиппинга/отрисовки.

#### Паттерны

**Кэширование дорогих фигур**:
```kotlin
// ✅ ПРАВИЛЬНО: предвычисление path в remember с учетом параметров
@Composable
fun Star(modifier: Modifier = Modifier, points: Int, size: Size) {
  val path = remember(points, size) { buildStarPath(points, size) }
  Canvas(modifier) { drawPath(path, color = Color.Yellow) }
}

// Пример для размера, зависящего от Canvas: используйте drawWithCache на Modifier
@Composable
fun StarCanvas(modifier: Modifier = Modifier, points: Int) {
  Canvas(
    modifier.drawWithCache {
      val path = buildStarPath(points, size) // size из DrawScope
      onDrawBehind {
        drawPath(path, color = Color.Yellow)
      }
    }
  )
}

// ❌ НЕПРАВИЛЬНО: создание path при каждой отрисовке без необходимости
@Composable
fun SlowStar(modifier: Modifier = Modifier, points: Int, size: Size) {
  Canvas(modifier) {
    val path = buildStarPath(points, size) // лишняя аллокация при каждом проходе рисования
    drawPath(path, color = Color.Yellow)
  }
}
```

**Переиспользование объектов**:
```kotlin
// ✅ ПРАВИЛЬНО: reset вместо создания нового Path каждый раз
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
// ✅ ПРАВИЛЬНО: отрисовка только видимых элементов (геометрическая отсечка)
Canvas(Modifier.fillMaxSize()) {
  val clip = clipBounds // локальные координаты DrawScope
  items.forEach { item ->
    if (item.bounds.overlaps(clip)) { // bounds в тех же координатах
      drawItem(item)
    }
  }
}
```

**Слои для анимаций**:
```kotlin
// ✅ ИСПОЛЬЗУЙТЕ ЭКОНОМНО: graphicsLayer для GPU-акселерации трансформаций/альфы,
// особенно полезно для анимируемых/часто меняющихся элементов
Canvas(Modifier.graphicsLayer(alpha = 0.9f)) { /* draw */ }
```

#### Чеклист Производительности
- Предвычисляйте пути/битмапы в `remember` или `drawWithCache`; минимизируйте создание новых объектов в `onDraw`/`onDrawBehind` при частых инвалидациях.
- Используйте `Stroke`/`Brush` осторожно; избегайте лишнего альфа-блендинга и сложных градиентов без реальной необходимости.
- Применяйте клиппинг только когда нужно; по возможности сначала выполняйте геометрическую отсечку.
- Профилируйте с Perfetto + `Trace.beginSection` в кастомном коде рисования.
- Бенчмаркинг с Macrobenchmark (render jank, frame time).

## Answer (EN)

### Short Version
- Use `Canvas`, `DrawScope`, and `drawWithCache` for precise drawing control.
- Cache expensive computations (`Path`, `ImageBitmap`) via `remember`/`drawWithCache`; avoid unnecessary allocations on each redraw.
- Minimize use of `alpha`, complex clipping, and extra layers, especially for large or frequently updated content.
- Profile with Perfetto and benchmarks; measure real-world performance.

### Detailed Version
#### Core Concepts
- `DrawScope`: immediate-mode drawing inside `Canvas(modifier) { ... }` / `drawBehind` / `drawWithContent`.
- State: state changes cause invalidation and redraw; minimize state writes and heavy work in hot paths.
- `remember` / `drawWithCache` / caching: precompute paths/bitmaps and other expensive structures; avoid unnecessary allocations inside draw lambdas, especially when drawing frequently.
- Clipping / alpha / layers: use only where needed (can be expensive, especially for large areas or complex content); prefer geometric culling before clipping/drawing when possible.

#### Patterns

**Caching expensive shapes**:
```kotlin
// ✅ CORRECT: precompute path in remember, based on stable parameters
@Composable
fun Star(modifier: Modifier = Modifier, points: Int, size: Size) {
  val path = remember(points, size) { buildStarPath(points, size) }
  Canvas(modifier) { drawPath(path, color = Color.Yellow) }
}

// Example when size depends on Canvas: use drawWithCache on the Modifier
@Composable
fun StarCanvas(modifier: Modifier = Modifier, points: Int) {
  Canvas(
    modifier.drawWithCache {
      val path = buildStarPath(points, size) // size from DrawScope
      onDrawBehind {
        drawPath(path, color = Color.Yellow)
      }
    }
  )
}

// ❌ WRONG: rebuilding path on every draw without need
@Composable
fun SlowStar(modifier: Modifier = Modifier, points: Int, size: Size) {
  Canvas(modifier) {
    val path = buildStarPath(points, size) // unnecessary allocation on each draw pass
    drawPath(path, color = Color.Yellow)
  }
}
```

**Reusing objects**:
```kotlin
// ✅ CORRECT: reset instead of allocating a new Path each time
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
// ✅ CORRECT: draw only visible items (geometric culling)
Canvas(Modifier.fillMaxSize()) {
  val clip = clipBounds // local DrawScope coordinates
  items.forEach { item ->
    if (item.bounds.overlaps(clip)) { // bounds in the same coordinate space
      drawItem(item)
    }
  }
}
```

**Layers for animations**:
```kotlin
// ✅ USE SPARINGLY: graphicsLayer for GPU-accelerated transforms/alpha,
// especially helpful for animating / frequently changing content
Canvas(Modifier.graphicsLayer(alpha = 0.9f)) { /* draw */ }
```

### Performance Checklist
- Precompute paths/bitmaps using `remember` or `drawWithCache`; minimize new allocations in `onDraw`/`onDrawBehind` when drawing frequently.
- Use `Stroke`/`Brush` judiciously; avoid unnecessary alpha blending and complex gradients when not needed.
- Clip only when necessary; prefer geometric culling before drawing.
- Profile with Perfetto + `Trace.beginSection` in custom drawing code.
- Benchmark with Macrobenchmark (render jank, frame time).

## Follow-ups
- How to structure state for large canvases (tiling/virtualization)?
- When to switch to custom Views for extreme performance cases?
- How to share drawing caches across recompositions/screens?
- How to handle complex paths with bezier curves efficiently?
- What's the difference between `drawWithCache` and `remember` for Canvas?

## References
- [[c-compose-state]] - State management in Compose
- [[c-compose-recomposition]] - Recomposition lifecycle
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

### Advanced (Harder)
- [[q-android-runtime-art--android--medium]] - Runtime and memory management
- [[q-compose-performance-optimization--android--hard]] - Comprehensive Compose performance
