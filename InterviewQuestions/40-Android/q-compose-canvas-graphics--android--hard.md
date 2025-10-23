---
id: 20251012-122802
title: Compose Canvas & Graphics / Canvas и графика в Compose
aliases:
- Compose Canvas & Graphics
- Canvas и графика в Compose
topic: android
subtopics:
- ui-compose
- graphics
question_kind: android
difficulty: hard
status: reviewed
moc: moc-android
related:
- q-canvas-drawing-optimization--custom-views--hard
- q-android-performance-measurement-tools--android--medium
- q-animated-visibility-vs-content--jetpack-compose--medium
created: 2025-10-11
updated: 2025-10-20
original_language: en
language_tags:
- en
- ru
tags:
- android/ui-compose
- android/graphics
- compose
- canvas
- performance
- difficulty/hard
---# Вопрос (RU)
> Как рендерить высокопроизводительную пользовательскую графику в Compose Canvas (state/remember, кеширование, клиппинг, draw scope и профилирование производительности)?

---

# Question (EN)
> How do you render high‑performance custom graphics with Compose Canvas (state/remember, caching, clipping, draw scope, and performance profiling)?

## Ответ (RU)

### Базовые концепции
- DrawScope: immediate‑рендер в `Canvas(modifier) { ... }`
- Состояние: рекомпозиция вызывает перерисовку; минимизировать записи state в горячих путях
- Remember/кеш: предвычислять path/bitmap; избегать аллокаций в draw‑лямбдах
- Клиппинг/альфа/слои: применять точечно (дорого); предпочитать геометрические проверки

### Минимальные паттерны

Кеширование дорогих фигур:
```kotlin
@Composable
fun Star(modifier: Modifier = Modifier, points: Int, size: Size) {
  val path = remember(points, size) { buildStarPath(points, size) } // precompute
  Canvas(modifier) { drawPath(path, color = Color.Yellow) }
}
```

Без аллокаций в draw:
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

Клиппинг по видимым границам:
```kotlin
Canvas(Modifier.fillMaxSize()) {
  val clip = clipBounds
  items.forEach { item -> if (item.bounds.overlaps(clip)) drawItem(item) }
}
```

Слой для анимаций (умеренно):
```kotlin
Canvas(Modifier.graphicsLayer(alpha = 0.9f)) { /* draw */ }
```

### Чек‑лист производительности
- Предвычислять path/bitmap в `remember`; не создавать объекты в draw
- Аккуратно с `Stroke`/`Brush`; избегать лишнего alpha‑смешения
- Клиппинг только при необходимости; геометрическое отсечение быстрее
- Профилировать Perfetto + `Trace.beginSection` (в своей логике)
- Бенчмарк Macrobenchmark (jank, время кадра)

---

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

