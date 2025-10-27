---
id: 20251012-122794
title: Canvas Optimization / Оптимизация Canvas
aliases: ["Canvas Optimization", "Оптимизация Canvas"]
topic: android
subtopics: [ui-graphics, ui-views]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-app-lag-analysis--android--medium, q-android-performance-measurement-tools--android--medium, q-canvas-drawing-optimization--android--hard]
sources: []
created: 2025-10-13
updated: 2025-10-27
tags: [android/ui-graphics, android/ui-views, difficulty/medium]
---

# Вопрос (RU)
> Как оптимизировать отрисовку Canvas для достижения 60 FPS?

# Question (EN)
> How do you optimize Canvas drawing to achieve 60 FPS?

---

## Ответ (RU)

### Ключевые принципы
- **Цель**: 60 FPS (16.67 мс/кадр); onDraw() < 5 мс; ноль аллокаций на кадр.
- **Предварительная аллокация**: Paint/Path/Rect/Matrix как поля класса; переиспользование через reset()/set().
- **Кеширование**: Bitmap-кеш для статичного контента; клиппинг видимой области.
- **Аппаратное ускорение**: включать для сложных/анимированных view; отключать для совместимости.

### Паттерн без аллокаций
```kotlin
class OptimizedView : View {
  private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
  private val rect = RectF()
  private val path = Path()

  override fun onDraw(canvas: Canvas) {
    // ✅ Переиспользование объектов
    rect.set(0f, 0f, width.toFloat(), height.toFloat())
    path.reset()
    path.addCircle(width/2f, height/2f, radius, Path.Direction.CW)

    // ❌ Не создавать объекты здесь
    // val tempPaint = Paint() // Аллокация каждый кадр

    canvas.drawPath(path, paint)
  }
}
```

### Аппаратное ускорение
```kotlin
// GPU кеширует отрисовку
setLayerType(LAYER_TYPE_HARDWARE, null)
```
- В 10 раз быстрее для статичного/сложного контента.
- Использовать для теней, градиентов, сложных путей.

### Bitmap кеширование
```kotlin
private var cachedBitmap: Bitmap? = null

override fun onDraw(canvas: Canvas) {
  if (cachedBitmap == null || contentChanged) {
    cachedBitmap = Bitmap.createBitmap(width, height, ARGB_8888)
    val cacheCanvas = Canvas(cachedBitmap!!)
    // Отрисовать сложный контент один раз
    drawExpensiveContent(cacheCanvas)
  }
  canvas.drawBitmap(cachedBitmap!!, 0f, 0f, null)
}
```

### Клиппинг
```kotlin
override fun onDraw(canvas: Canvas) {
  val bounds = canvas.clipBounds
  // Рисовать только видимые элементы
  items.filter { it.intersects(bounds) }
       .forEach { it.draw(canvas) }
}
```
- Ускорение в 20 раз для прокручиваемого контента.

### Оптимизация Paint
- Переиспользовать объекты Paint
- Отключать anti-aliasing для прямых линий
- Использовать непрозрачные цвета (alpha = 255)

### Профилирование
```kotlin
override fun onDraw(canvas: Canvas) {
  Trace.beginSection("ExpensiveDrawing")
  // Код отрисовки
  Trace.endSection()
}
```
Анализ через Android Profiler: аллокации, время отрисовки, GC события.

## Answer (EN)

### Core Principles
- **Target**: 60 FPS (16.67 ms/frame); onDraw() < 5 ms; zero allocations per frame.
- **Pre-allocate**: Paint/Path/Rect/Matrix as class fields; reuse with reset()/set().
- **Cache**: Bitmap cache for static content; clip to visible regions.
- **Hardware acceleration**: Enable for complex/animated views; disable for compatibility.

### Zero Allocations Pattern
```kotlin
class OptimizedView : View {
  private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
  private val rect = RectF()
  private val path = Path()

  override fun onDraw(canvas: Canvas) {
    // ✅ Reuse objects
    rect.set(0f, 0f, width.toFloat(), height.toFloat())
    path.reset()
    path.addCircle(width/2f, height/2f, radius, Path.Direction.CW)

    // ❌ Don't create objects here
    // val tempPaint = Paint() // Allocation per frame

    canvas.drawPath(path, paint)
  }
}
```

### Hardware Acceleration
```kotlin
// GPU caches drawing commands
setLayerType(LAYER_TYPE_HARDWARE, null)
```
- 10x faster for static/complex content.
- Use for shadows, gradients, complex paths.

### Bitmap Caching
```kotlin
private var cachedBitmap: Bitmap? = null

override fun onDraw(canvas: Canvas) {
  if (cachedBitmap == null || contentChanged) {
    cachedBitmap = Bitmap.createBitmap(width, height, ARGB_8888)
    val cacheCanvas = Canvas(cachedBitmap!!)
    // Draw expensive content once
    drawExpensiveContent(cacheCanvas)
  }
  canvas.drawBitmap(cachedBitmap!!, 0f, 0f, null)
}
```

### Clipping Optimization
```kotlin
override fun onDraw(canvas: Canvas) {
  val bounds = canvas.clipBounds
  // Draw only visible items
  items.filter { it.intersects(bounds) }
       .forEach { it.draw(canvas) }
}
```
- 20x speedup for scrollable content.

### Paint Optimization
- Reuse Paint objects
- Disable anti-aliasing for straight lines
- Use opaque colors (alpha = 255)

### Profiling
```kotlin
override fun onDraw(canvas: Canvas) {
  Trace.beginSection("ExpensiveDrawing")
  // Drawing code
  Trace.endSection()
}
```
Analyze with Android Profiler: allocations, draw times, GC events.

## Follow-ups
- How to profile path complexity and overdraw using GPU Rendering tools?
- When to choose software vs hardware layer types?
- How to implement view recycling for large scrollable canvases?

## References
- https://developer.android.com/topic/performance/rendering
- https://developer.android.com/topic/performance/vitals

## Related Questions

### Prerequisites
- [[q-android-performance-measurement-tools--android--medium]] - Profiling tools overview

### Related
- [[q-android-app-lag-analysis--android--medium]] - Frame drops diagnosis
- Custom view drawing patterns

### Advanced
- [[q-canvas-drawing-optimization--android--hard]] - Advanced drawing techniques
- Hardware layer internals and GPU pipeline
