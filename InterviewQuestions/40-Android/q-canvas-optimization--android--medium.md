---
id: android-088
title: Canvas Optimization / Оптимизация Canvas
aliases: [Canvas Optimization, Оптимизация Canvas]
topic: android
subtopics:
  - performance-rendering
  - ui-graphics
  - ui-views
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-custom-views
  - q-android-app-lag-analysis--android--medium
  - q-android-performance-measurement-tools--android--medium
  - q-canvas-drawing-optimization--android--hard
  - q-custom-view-lifecycle--android--medium
sources: []
created: 2025-10-13
updated: 2025-10-29
tags: [android/performance-rendering, android/ui-graphics, android/ui-views, custom-views, difficulty/medium, performance]
date created: Thursday, October 30th 2025, 11:10:52 am
date modified: Sunday, November 2nd 2025, 1:29:16 pm
---

# Вопрос (RU)
> Как оптимизировать отрисовку Canvas для достижения 60 FPS?

# Question (EN)
> How do you optimize Canvas drawing to achieve 60 FPS?

---

## Ответ (RU)

### Цель Производительности
**60 FPS = 16.67 мс/кадр**. Бюджет onDraw(): **< 5 мс** (остальное — измерение, компоновка, системные операции). Нулевые аллокации в цикле отрисовки.

### 1. Паттерн Без Аллокаций

Создавайте Paint/Path/Rect/Matrix как поля класса. Переиспользуйте через `reset()`/`set()`.

```kotlin
class OptimizedView : View {
  // ✅ Выделить память один раз
  private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
  private val rect = RectF()
  private val path = Path()

  override fun onDraw(canvas: Canvas) {
    // ✅ Переиспользование
    rect.set(0f, 0f, width.toFloat(), height.toFloat())
    path.reset()
    path.addCircle(width / 2f, height / 2f, radius, Path.Direction.CW)

    canvas.drawPath(path, paint)

    // ❌ Никогда не создавать объекты здесь
    // val tempPaint = Paint() // Аллокация каждый кадр!
  }
}
```

**Результат**: нет GC пауз во время отрисовки.

### 2. Аппаратное Ускорение (GPU)

```kotlin
// GPU кеширует команды отрисовки
setLayerType(LAYER_TYPE_HARDWARE, null)
```

**Когда использовать**:
- Статичный или редко меняющийся контент
- Сложная графика (тени, градиенты, размытие)
- Анимация с постоянными визуальными эффектами

**Эффект**: ускорение в 5-10 раз для сложных путей.

**Компромисс**: дополнительная память (копия текстуры в GPU); не подходит для часто меняющегося контента.

### 3. Bitmap Кеширование

Рендерьте дорогой контент один раз, сохраните в Bitmap, переиспользуйте.

```kotlin
private var cache: Bitmap? = null
private var cacheValid = false

override fun onDraw(canvas: Canvas) {
  if (!cacheValid) {
    cache = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
    Canvas(cache!!).apply {
      drawComplexBackground(this)  // Дорогая операция
    }
    cacheValid = true
  }
  canvas.drawBitmap(cache!!, 0f, 0f, null)
}

fun invalidateCache() {
  cacheValid = false
  invalidate()
}
```

**Применение**: фоновые узоры, сложные статичные слои, шейдеры.

### 4. Клиппинг Видимой Области

Рисуйте только видимые элементы.

```kotlin
override fun onDraw(canvas: Canvas) {
  val visibleBounds = canvas.clipBounds

  items
    .filter { it.bounds.intersects(visibleBounds) }
    .forEach { it.draw(canvas) }
}
```

**Эффект**: ускорение в 10-20 раз для прокручиваемого контента с сотнями элементов.

### 5. Оптимизация Paint

```kotlin
// ✅ Хорошо: простые настройки
paint.isAntiAlias = false  // Для прямых линий
paint.color = Color.parseColor("#FF5733")  // Непрозрачный
paint.style = Paint.Style.FILL

// ❌ Плохо: дорогие операции
paint.isAntiAlias = true  // +30% времени рендеринга
paint.alpha = 128  // Требует альфа-блендинга
paint.setShadowLayer(10f, 0f, 0f, Color.BLACK)  // Тяжелая операция
```

**Совет**: используйте `Paint.ANTI_ALIAS_FLAG` только для кривых/окружностей.

### Профилирование

```kotlin
override fun onDraw(canvas: Canvas) {
  Trace.beginSection("CustomViewDraw")
  // Код отрисовки
  Trace.endSection()
}
```

Анализируйте через **Android Studio Profiler** → CPU → System Trace.

## Answer (EN)

### Performance Target
**60 FPS = 16.67 ms/frame**. Budget for onDraw(): **< 5 ms** (rest for measure, layout, system overhead). Zero allocations in draw loop.

### 1. Zero-Allocation Pattern

Create Paint/Path/Rect/Matrix as class fields. Reuse via `reset()`/`set()`.

```kotlin
class OptimizedView : View {
  // ✅ Allocate once
  private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
  private val rect = RectF()
  private val path = Path()

  override fun onDraw(canvas: Canvas) {
    // ✅ Reuse
    rect.set(0f, 0f, width.toFloat(), height.toFloat())
    path.reset()
    path.addCircle(width / 2f, height / 2f, radius, Path.Direction.CW)

    canvas.drawPath(path, paint)

    // ❌ Never create objects here
    // val tempPaint = Paint() // Allocation per frame!
  }
}
```

**Result**: no GC pauses during rendering.

### 2. Hardware Acceleration (GPU)

```kotlin
// GPU caches drawing commands
setLayerType(LAYER_TYPE_HARDWARE, null)
```

**When to use**:
- Static or infrequently changing content
- Complex graphics (shadows, gradients, blur)
- Animation with consistent visual effects

**Impact**: 5-10x speedup for complex paths.

**Trade-off**: extra memory (texture copy on GPU); not suitable for frequently changing content.

### 3. Bitmap Caching

Render expensive content once, save to Bitmap, reuse.

```kotlin
private var cache: Bitmap? = null
private var cacheValid = false

override fun onDraw(canvas: Canvas) {
  if (!cacheValid) {
    cache = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
    Canvas(cache!!).apply {
      drawComplexBackground(this)  // Expensive operation
    }
    cacheValid = true
  }
  canvas.drawBitmap(cache!!, 0f, 0f, null)
}

fun invalidateCache() {
  cacheValid = false
  invalidate()
}
```

**Use cases**: background patterns, complex static layers, shaders.

### 4. Clipping to Visible Region

Draw only visible items.

```kotlin
override fun onDraw(canvas: Canvas) {
  val visibleBounds = canvas.clipBounds

  items
    .filter { it.bounds.intersects(visibleBounds) }
    .forEach { it.draw(canvas) }
}
```

**Impact**: 10-20x speedup for scrollable content with hundreds of items.

### 5. Paint Optimization

```kotlin
// ✅ Good: simple settings
paint.isAntiAlias = false  // For straight lines
paint.color = Color.parseColor("#FF5733")  // Opaque
paint.style = Paint.Style.FILL

// ❌ Bad: expensive operations
paint.isAntiAlias = true  // +30% rendering time
paint.alpha = 128  // Requires alpha blending
paint.setShadowLayer(10f, 0f, 0f, Color.BLACK)  // Heavy operation
```

**Tip**: use `Paint.ANTI_ALIAS_FLAG` only for curves/circles.

### Profiling

```kotlin
override fun onDraw(canvas: Canvas) {
  Trace.beginSection("CustomViewDraw")
  // Drawing code
  Trace.endSection()
}
```

Analyze via **Android Studio Profiler** → CPU → System Trace.

---

## Follow-ups

- How does overdraw affect Canvas performance and how to detect it?
- When should you use LAYER_TYPE_SOFTWARE vs LAYER_TYPE_HARDWARE?
- How to implement efficient view recycling for scrollable canvas-based lists?
- What are the memory implications of Bitmap caching for large views?
- How to optimize Path operations for complex vector graphics?

## References

- [[c-custom-views]] - Custom View fundamentals
- https://developer.android.com/topic/performance/rendering
- https://developer.android.com/topic/performance/vitals/render

## Related Questions

### Prerequisites (Easier)
- [[q-custom-view-lifecycle--android--medium]] - Custom View lifecycle basics
- [[q-android-performance-measurement-tools--android--medium]] - Profiling tools overview

### Related (Same Level)
- [[q-android-app-lag-analysis--android--medium]] - Frame drop analysis
- [[q-custom-view-state-saving--android--medium]] - State management in custom views
- [[q-anr-application-not-responding--android--medium]] - ANR debugging strategies

### Advanced (Harder)
- [[q-canvas-drawing-optimization--android--hard]] - Advanced Canvas techniques
- [[q-custom-viewgroup-layout--android--hard]] - ViewGroup layout optimization
- [[q-tiktok-video-feed--android--hard]] - Complex scrolling performance
