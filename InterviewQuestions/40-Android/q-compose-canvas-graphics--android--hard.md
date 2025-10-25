---
id: 20251012-122802
title: Compose Canvas & Graphics / Canvas и графика в Compose
aliases:
- Compose Canvas & Graphics
- Canvas и графика в Compose
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
- q-canvas-drawing-optimization--android--hard
- q-android-performance-measurement-tools--android--medium
- q-animated-visibility-vs-content--android--medium
created: 2025-10-11
updated: 2025-10-20
tags:
- android/ui-compose
- android/ui-graphics
- difficulty/hard
---

# Вопрос (RU)
> Canvas и графика в Compose?

# Question (EN)
> Compose Canvas & Graphics?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Core concepts
- DrawScope: immediate mode drawing inside `Canvas(modifier) { ... }`
- State: recomposition drives re‑draw; minimize state writes in hot paths
- Remember/caching: precompute paths/bitmaps; avoid allocations in draw lambdas
- Clipping/alpha/layers: apply only where needed (costly); prefer geometry tests

### Minimal patterns

Caching expensive shapes:
```kotlin
@Composable
fun Star(modifier: Modifier = Modifier, points: Int, size: Size) {
  val path = remember(points, size) { buildStarPath(points, size) } // precompute
  Canvas(modifier) { drawPath(path, color = Color.Yellow) }
}
```

Avoid allocations in draw:
```kotlin
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

Clipping to visible bounds:
```kotlin
Canvas(Modifier.fillMaxSize()) {
  val clip = clipBounds
  items.forEach { item -> if (item.bounds.overlaps(clip)) drawItem(item) }
}
```

Layer for animations (use sparingly):
```kotlin
Canvas(Modifier.graphicsLayer(alpha = 0.9f)) { /* draw */ }
```

### Performance checklist
- Precompute paths/bitmaps in `remember`; no new objects in draw
- Use `Stroke`/`Brush` judiciously; avoid unnecessary alpha blending
- Clip only when needed; prefer geometric culling
- Profile with Perfetto + `Trace.beginSection` in custom code (non‑UI thread work)
- Benchmark with Macrobenchmark (render jank, frame time)

## Follow-ups
- How to structure state for large canvases (tiling/virtualization)?
- When to switch to custom Views for extreme cases?
- How to share drawing caches across recompositions/screens?

## References
- [[c-algorithms]] - Drawing and rendering optimization algorithms
- https://developer.android.com/develop/ui/compose/graphics/draw/overview
- https://perfetto.dev

## Related Questions

### Prerequisites (Easier)
- [[q-android-performance-measurement-tools--android--medium]]

### Related (Same Level)
- [[q-canvas-drawing-optimization--android--hard]]
- [[q-animated-visibility-vs-content--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-art--android--medium]]
