---
id: android-117
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
status: reviewed
moc: moc-android
related:
  - c-performance
  - c-performance-optimization
  - q-android-app-lag-analysis--android--medium
  - q-android-performance-measurement-tools--android--medium
  - q-canvas-optimization--android--medium
  - q-dagger-build-time-optimization--android--medium
  - q-parsing-optimization-android--android--medium
created: 2025-10-15
updated: 2025-10-29
sources: []
tags: [android/performance-rendering, android/ui-views, canvas, custom-views, difficulty/hard, performance]
date created: Saturday, November 1st 2025, 12:46:45 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---

# Вопрос (RU)
> Как оптимизировать отрисовку в Canvas для достижения 60 FPS в кастомных View?

# Question (EN)
> How to optimize Canvas drawing to achieve 60 FPS in custom Views?

---

## Ответ (RU)

**Цель производительности**: 60 FPS = 16.67 мс на кадр. Стремимся к тому, чтобы `onDraw()` обычно занимал < 5 мс, избегал лишних аллокаций и не вызывал GC во время анимаций.

### 1. Нулевые Аллокации Памяти (по возможности)

Создание объектов в `onDraw()` вызывает давление на GC и может приводить к пропускам кадров, особенно при частых обновлениях (анимации).

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

    // 🚫 Избегать систематического создания новых объектов здесь в каждом кадре
    // val newPaint = Paint()
  }
}
```

Принцип: не обязательно «абсолютный ноль», но регулярных аллокаций в каждом кадре следует избегать.

### 2. Аппаратное Ускорение

Аппаратное ускорение (GPU) может ускорить сложную отрисовку, работать с слоями и эффектами и разгрузить CPU, но не всегда даёт выигрыш и поддерживается не для всех операций.

```kotlin
// ✅ Для статичного или редко меняющегося сложного контента
setLayerType(LAYER_TYPE_HARDWARE, null)

// ✅ Временно для анимаций
view.animate().alpha(0f).withLayer() // Автоматически управляет слоем
```

**Когда использовать**: сложные Path, многослойные эффекты, дорогие операции, которые можно кешировать в слое. Оценивать профилированием; прирост зависит от устройства и сценария и не гарантирован.

### 3. Bitmap Кеширование

Дорогостоящие операции выполняем один раз в `Bitmap`, затем в `onDraw()` только `drawBitmap()`.

```kotlin
private var cache: Bitmap? = null
private var isDirty = true

override fun onDraw(canvas: Canvas) {
  if (isDirty || cache == null || cache!!.width != width || cache!!.height != height) {
    cache?.recycle()
    if (width > 0 && height > 0) {
      cache = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
      val cacheCanvas = Canvas(cache!!)
      cacheCanvas.drawComplexContent() // ✅ Дорогая операция один раз/при изменениях
    }
    isDirty = false
  }
  cache?.let {
    canvas.drawBitmap(it, 0f, 0f, null) // ✅ Быстрая операция
  }
}
```

Инвалидируйте кеш при изменении данных или размеров: `isDirty = true; invalidate()` / `requestLayout()`.

### 4. Clipping (отсечение)

Отрисовываем только видимую область (viewport) и не рисуем элементы за её пределами.

```kotlin
override fun onDraw(canvas: Canvas) {
  val bounds = canvas.clipBounds // ✅ Текущая видимая область после клиппинга
  // При необходимости можно дополнительно ограничить область: canvas.clipRect(...)
  visibleItems(bounds).forEach { item ->
    canvas.drawItem(item) // Отрисовка только видимого
  }
}
```

Эффект зависит от сцены: для списков из тысяч элементов или сложной геометрии выигрыш может быть очень значительным, но конкретный множитель нужно подтверждать профилированием.

### 5. Профилирование

```kotlin
override fun onDraw(canvas: Canvas) {
  Trace.beginSection("MyView.onDraw") // ✅ Trace для System Tracing / Perfetto
  // отрисовка
  Trace.endSection()
}
```

**Инструменты**:
- Android Profiler (CPU/Memory)
- Inspect GPU Rendering / Profile HWUI rendering (Developer Options)
- System Tracing / Perfetto (современная замена классического Systrace)

**Что искать**: аллокации в `onDraw`, кадры > 16 мс, GC-события во время отрисовки, тяжёлые операции на UI-потоке.

## Answer (EN)

**Performance target**: 60 FPS = 16.67ms per frame. Aim for `onDraw()` to typically stay under ~5ms, avoid unnecessary allocations, and prevent GC during animations.

### 1. Zero Allocations (as much as possible)

Allocating new objects in `onDraw()` increases GC pressure and can cause frame drops, especially under continuous animations.

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

    // 🚫 Avoid systematic per-frame allocations here
    // val newPaint = Paint()
  }
}
```

Principle: aim to minimize per-frame allocations; "absolute zero" is an ideal, but regular allocations in every frame should be avoided.

### 2. Hardware Acceleration

Hardware acceleration (GPU) can speed up complex rendering, handle layers and effects and offload work from the CPU, but it is not universally faster and some operations are still CPU-bound or unsupported.

```kotlin
// ✅ For static or rarely changing complex content
setLayerType(LAYER_TYPE_HARDWARE, null)

// ✅ Temporarily for animations
view.animate().alpha(0f).withLayer() // Auto-manages layer
```

**When to use**: complex Paths, multi-layer effects, expensive drawing that can be cached into a layer. Always verify with profiling; actual speedup is device- and case-dependent.

### 3. Bitmap Caching

Render expensive content once into a `Bitmap`, then in `onDraw()` only call `drawBitmap()`.

```kotlin
private var cache: Bitmap? = null
private var isDirty = true

override fun onDraw(canvas: Canvas) {
  if (isDirty || cache == null || cache!!.width != width || cache!!.height != height) {
    cache?.recycle()
    if (width > 0 && height > 0) {
      cache = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
      val cacheCanvas = Canvas(cache!!)
      cacheCanvas.drawComplexContent() // ✅ Expensive only on changes
    }
    isDirty = false
  }
  cache?.let {
    canvas.drawBitmap(it, 0f, 0f, null) // ✅ Fast operation
  }
}
```

Invalidate cache on data or size changes: `isDirty = true; invalidate()` / `requestLayout()`.

### 4. Clipping

Draw only the visible viewport area and skip items outside it.

```kotlin
override fun onDraw(canvas: Canvas) {
  val bounds = canvas.clipBounds // ✅ Current visible area after clipping
  // Optionally further restrict: canvas.clipRect(...)
  visibleItems(bounds).forEach { item ->
    canvas.drawItem(item) // Draw only visible
  }
}
```

Actual gain is content-dependent: for large lists or complex geometry the speedup can be substantial, but any numeric factor should be validated via profiling.

### 5. Profiling

```kotlin
override fun onDraw(canvas: Canvas) {
  Trace.beginSection("MyView.onDraw") // ✅ Trace for System Tracing / Perfetto
  // drawing
  Trace.endSection()
}
```

**Tools**:
- Android Profiler (CPU/Memory)
- Inspect GPU Rendering / Profile HWUI rendering (Developer Options)
- System Tracing / Perfetto (modern replacement for classic Systrace)

**Look for**: allocations in `onDraw`, frames > 16ms, GC events during drawing, heavy work on the UI thread.

## Follow-ups
- What is overdraw and how does it affect Canvas performance?
- When should you use `LAYER_TYPE_SOFTWARE` vs `LAYER_TYPE_HARDWARE`?
- How do RenderNode and DisplayList optimize rendering internally?
- What are the memory implications of Bitmap caching for large views?
- How do you profile custom view performance in production builds?

## References

- [Rendering Performance](https://developer.android.com/topic/performance/rendering)
- https://developer.android.com/topic/performance/inspect-gpu-rendering
- https://developer.android.com/reference/android/graphics/Canvas
- https://developer.android.com/training/custom-views/optimizing-view


## Related Questions

### Prerequisites / Concepts

- [[c-performance]]
- [[c-performance-optimization]]


### Prerequisites
- [[q-android-performance-measurement-tools--android--medium]] - Profiling tools and techniques

### Related
- [[q-android-app-lag-analysis--android--medium]] - Diagnosing frame drops
- Custom View lifecycle and invalidation patterns

### Advanced
- RenderNode API for advanced rendering optimization
- PixelCopy and hardware bitmap usage for complex scenarios
