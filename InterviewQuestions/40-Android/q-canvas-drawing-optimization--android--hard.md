---
id: 20251012-122793
title: Canvas Drawing Optimization / Оптимизация отрисовки Canvas
aliases: [Canvas Drawing Optimization, Оптимизация отрисовки Canvas]
topic: android
subtopics:
  - performance-rendering
  - ui-views
question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-android-app-lag-analysis--android--medium
  - q-android-performance-measurement-tools--android--medium
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android/performance-rendering, android/ui-views, difficulty/hard]
---
# Вопрос (RU)
> Как оптимизировать отрисовку в Canvas для достижения 60 FPS в кастомных View?

# Question (EN)
> How to optimize Canvas drawing to achieve 60 FPS in custom Views?

---

## Ответ (RU)

### Основные принципы
**Цель**: 60 FPS (16.67 мс на кадр), onDraw() должен занимать < 5 мс, нулевые выделения памяти на кадр.

**Ключевые техники**:
- Переиспользование объектов Paint/Path/Rect
- Аппаратное ускорение для сложных/анимированных View
- Кеширование в Bitmap для статичного контента
- Отсечение (clipping) для видимой области

### Нулевые выделения памяти

```kotlin
class OptimizedView : View {
  // ✅ Предварительное выделение объектов
  private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
  private val rect = Rect()
  private val path = Path()

  override fun onDraw(canvas: Canvas) {
    // ✅ Переиспользование через set/reset
    rect.set(0, 0, width, height)
    path.reset()
    path.moveTo(0f, 0f)
    path.lineTo(width.toFloat(), height.toFloat())
    canvas.drawPath(path, paint)

    // ❌ НИКОГДА не создавать объекты здесь
    // val newPaint = Paint() // вызывает GC паузы
  }
}
```

### Аппаратное ускорение
Включить hardware layer для сложных/анимированных View:

```kotlin
// ✅ Для статичного сложного контента
setLayerType(LAYER_TYPE_HARDWARE, null)

// ✅ Для анимаций временно
view.setLayerType(LAYER_TYPE_HARDWARE, null)
// ... анимация ...
view.setLayerType(LAYER_TYPE_NONE, null)
```

GPU кеширует отрисовку, ускорение до 10x для сложной графики.

### Bitmap кеширование
Для дорогостоящей статичной отрисовки:

```kotlin
private var cachedBitmap: Bitmap? = null
private var cacheValid = false

override fun onDraw(canvas: Canvas) {
  if (!cacheValid) {
    cachedBitmap = Bitmap.createBitmap(width, height, ARGB_8888)
    Canvas(cachedBitmap!!).apply {
      // ✅ Дорогостоящая отрисовка один раз
      drawComplexShape(this)
    }
    cacheValid = true
  }
  canvas.drawBitmap(cachedBitmap!!, 0f, 0f, null)
}
```

### Clipping (отсечение)

```kotlin
override fun onDraw(canvas: Canvas) {
  val clipBounds = canvas.clipBounds
  // ✅ Отрисовка только видимых элементов
  items.filter { it.intersects(clipBounds) }.forEach {
    drawItem(canvas, it)
  }
}
```

Для прокручиваемого контента ускорение до 20x.

### Профилирование
Использовать Android Profiler и Systrace:

```kotlin
override fun onDraw(canvas: Canvas) {
  Trace.beginSection("MyView.onDraw")
  // отрисовка
  Trace.endSection()
}
```

Искать: выделения памяти, длительные операции отрисовки, GC события.

## Answer (EN)

### Core Principles
**Target**: 60 FPS (16.67ms per frame), onDraw() should take < 5ms, zero allocations per frame.

**Key techniques**:
- Reuse Paint/Path/Rect objects
- Hardware acceleration for complex/animated Views
- Bitmap caching for static content
- Clipping for visible region

### Zero Allocations

```kotlin
class OptimizedView : View {
  // ✅ Pre-allocate objects
  private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
  private val rect = Rect()
  private val path = Path()

  override fun onDraw(canvas: Canvas) {
    // ✅ Reuse via set/reset
    rect.set(0, 0, width, height)
    path.reset()
    path.moveTo(0f, 0f)
    path.lineTo(width.toFloat(), height.toFloat())
    canvas.drawPath(path, paint)

    // ❌ NEVER create objects here
    // val newPaint = Paint() // causes GC pauses
  }
}
```

### Hardware Acceleration
Enable hardware layer for complex/animated Views:

```kotlin
// ✅ For static complex content
setLayerType(LAYER_TYPE_HARDWARE, null)

// ✅ For animations temporarily
view.setLayerType(LAYER_TYPE_HARDWARE, null)
// ... animation ...
view.setLayerType(LAYER_TYPE_NONE, null)
```

GPU caches drawing, up to 10x speedup for complex graphics.

### Bitmap Caching
For expensive static drawing:

```kotlin
private var cachedBitmap: Bitmap? = null
private var cacheValid = false

override fun onDraw(canvas: Canvas) {
  if (!cacheValid) {
    cachedBitmap = Bitmap.createBitmap(width, height, ARGB_8888)
    Canvas(cachedBitmap!!).apply {
      // ✅ Expensive drawing once
      drawComplexShape(this)
    }
    cacheValid = true
  }
  canvas.drawBitmap(cachedBitmap!!, 0f, 0f, null)
}
```

### Clipping

```kotlin
override fun onDraw(canvas: Canvas) {
  val clipBounds = canvas.clipBounds
  // ✅ Draw only visible items
  items.filter { it.intersects(clipBounds) }.forEach {
    drawItem(canvas, it)
  }
}
```

For scrollable content, up to 20x speedup.

### Profiling
Use Android Profiler and Systrace:

```kotlin
override fun onDraw(canvas: Canvas) {
  Trace.beginSection("MyView.onDraw")
  // drawing
  Trace.endSection()
}
```

Look for: allocations, long draw times, GC events.

## Follow-ups
- How does overdraw impact Canvas performance and how to detect it?
- When should you use DisplayList vs immediate mode rendering?
- How to optimize Path operations for complex shapes?
- What are the trade-offs between LAYER_TYPE_HARDWARE vs LAYER_TYPE_SOFTWARE?

## References
- https://developer.android.com/topic/performance/rendering
- https://developer.android.com/topic/performance/inspect-gpu-rendering

## Related Questions

### Prerequisites (Easier)
- [[q-android-performance-measurement-tools--android--medium]]

### Related (Same Level)
- [[q-android-app-lag-analysis--android--medium]]

### Advanced (Harder)
- Advanced custom view rendering with RenderNode
- Canvas performance profiling in production apps
