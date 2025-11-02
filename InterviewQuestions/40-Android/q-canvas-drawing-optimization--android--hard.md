---
id: android-117
title: Canvas Drawing Optimization / Оптимизация отрисовки Canvas
aliases: ["Canvas Drawing Optimization", "Оптимизация отрисовки Canvas"]
topic: android
subtopics: [performance-rendering, ui-views]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-app-lag-analysis--android--medium, q-android-performance-measurement-tools--android--medium]
created: 2025-10-15
updated: 2025-10-29
sources: []
tags: [android/performance-rendering, android/ui-views, custom-views, performance, canvas, difficulty/hard]
date created: Thursday, October 30th 2025, 11:11:20 am
date modified: Thursday, October 30th 2025, 12:43:32 pm
---

# Вопрос (RU)
> Как оптимизировать отрисовку в Canvas для достижения 60 FPS в кастомных View?

# Question (EN)
> How to optimize Canvas drawing to achieve 60 FPS in custom Views?

---

## Ответ (RU)

**Цель производительности**: 60 FPS = 16.67 мс на кадр, `onDraw()` должен занимать < 5 мс, нулевые аллокации на кадр.

### 1. Нулевые аллокации памяти

Создание объектов в `onDraw()` вызывает GC паузы и пропуски кадров.

```kotlin
class OptimizedView(context: Context) : View(context) {
  // ✅ Предварительное выделение - переиспользуем на каждый кадр
  private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
  private val rect = Rect()
  private val path = Path()

  override fun onDraw(canvas: Canvas) {
    rect.set(0, 0, width, height) // ✅ Переиспользование
    path.reset() // ✅ Очистка вместо создания
    path.moveTo(0f, 0f)
    path.lineTo(width.toFloat(), height.toFloat())

    // ❌ val newPaint = Paint() // НИКОГДА не создавать объекты здесь
  }
}
```

### 2. Аппаратное ускорение

GPU кеширует содержимое слоя, минуя CPU повторную отрисовку.

```kotlin
// ✅ Для статичного сложного контента
setLayerType(LAYER_TYPE_HARDWARE, null)

// ✅ Временно для анимаций
view.animate().alpha(0f).withLayer() // Автоматически управляет слоем
```

**Когда использовать**: сложные Path, многослойные эффекты, частые анимации. До 10x ускорения.

### 3. Bitmap кеширование

Дорогостоящие операции отрисовываем один раз в Bitmap, затем только `drawBitmap()`.

```kotlin
private var cache: Bitmap? = null
private var isDirty = true

override fun onDraw(canvas: Canvas) {
  if (isDirty) {
    cache = Bitmap.createBitmap(width, height, ARGB_8888)
    Canvas(cache!!).drawComplexContent() // ✅ Дорогая операция один раз
    isDirty = false
  }
  canvas.drawBitmap(cache!!, 0f, 0f, null) // ✅ Быстрая операция
}
```

Инвалидировать кеш при изменении данных: `isDirty = true; invalidate()`.

### 4. Clipping (отсечение)

Отрисовываем только видимую область viewport.

```kotlin
override fun onDraw(canvas: Canvas) {
  val bounds = canvas.clipBounds // ✅ Видимая область
  visibleItems(bounds).forEach { item ->
    canvas.drawItem(item) // Отрисовка только видимого
  }
}
```

Для списков из тысяч элементов ускорение до 20x.

### 5. Профилирование

```kotlin
override fun onDraw(canvas: Canvas) {
  Trace.beginSection("MyView.onDraw") // ✅ Трейс для Systrace
  // отрисовка
  Trace.endSection()
}
```

**Инструменты**: Android Profiler (CPU/Memory), GPU Rendering Profile (Settings > Developer Options), Systrace.

**Что искать**: аллокации в onDraw, кадры > 16 мс, GC события во время отрисовки.

## Answer (EN)

**Performance target**: 60 FPS = 16.67ms per frame, `onDraw()` should take < 5ms, zero allocations per frame.

### 1. Zero Allocations

Creating objects in `onDraw()` triggers GC pauses and frame drops.

```kotlin
class OptimizedView(context: Context) : View(context) {
  // ✅ Pre-allocate - reuse every frame
  private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
  private val rect = Rect()
  private val path = Path()

  override fun onDraw(canvas: Canvas) {
    rect.set(0, 0, width, height) // ✅ Reuse
    path.reset() // ✅ Clear instead of recreate
    path.moveTo(0f, 0f)
    path.lineTo(width.toFloat(), height.toFloat())

    // ❌ val newPaint = Paint() // NEVER allocate here
  }
}
```

### 2. Hardware Acceleration

GPU caches layer content, bypassing CPU redraw.

```kotlin
// ✅ For static complex content
setLayerType(LAYER_TYPE_HARDWARE, null)

// ✅ Temporarily for animations
view.animate().alpha(0f).withLayer() // Auto-manages layer
```

**When to use**: complex Paths, multilayer effects, frequent animations. Up to 10x speedup.

### 3. Bitmap Caching

Expensive operations drawn once to Bitmap, then only `drawBitmap()`.

```kotlin
private var cache: Bitmap? = null
private var isDirty = true

override fun onDraw(canvas: Canvas) {
  if (isDirty) {
    cache = Bitmap.createBitmap(width, height, ARGB_8888)
    Canvas(cache!!).drawComplexContent() // ✅ Expensive once
    isDirty = false
  }
  canvas.drawBitmap(cache!!, 0f, 0f, null) // ✅ Fast operation
}
```

Invalidate cache on data change: `isDirty = true; invalidate()`.

### 4. Clipping

Draw only visible viewport region.

```kotlin
override fun onDraw(canvas: Canvas) {
  val bounds = canvas.clipBounds // ✅ Visible area
  visibleItems(bounds).forEach { item ->
    canvas.drawItem(item) // Draw only visible
  }
}
```

For lists with thousands of items, up to 20x speedup.

### 5. Profiling

```kotlin
override fun onDraw(canvas: Canvas) {
  Trace.beginSection("MyView.onDraw") // ✅ Trace for Systrace
  // drawing
  Trace.endSection()
}
```

**Tools**: Android Profiler (CPU/Memory), GPU Rendering Profile (Settings > Developer Options), Systrace.

**Look for**: allocations in onDraw, frames > 16ms, GC events during drawing.

## Follow-ups
- What is overdraw and how does it affect Canvas performance?
- When should you use `LAYER_TYPE_SOFTWARE` vs `LAYER_TYPE_HARDWARE`?
- How do RenderNode and DisplayList optimize rendering internally?
- What are the memory implications of Bitmap caching for large views?
- How do you profile custom view performance in production builds?

## References
- https://developer.android.com/topic/performance/rendering
- https://developer.android.com/topic/performance/inspect-gpu-rendering
- https://developer.android.com/reference/android/graphics/Canvas
- https://developer.android.com/training/custom-views/optimizing-view

## Related Questions

### Prerequisites
- [[q-android-performance-measurement-tools--android--medium]] - Profiling tools and techniques

### Related
- [[q-android-app-lag-analysis--android--medium]] - Diagnosing frame drops
- Custom View lifecycle and invalidation patterns

### Advanced
- RenderNode API for advanced rendering optimization
- PixelCopy and hardware bitmap usage for complex scenarios
