---
id: android-088
title: Canvas Optimization / Оптимизация Canvas
aliases: [Canvas Optimization, Оптимизация Canvas]
topic: android
subtopics: [performance-rendering, ui-graphics, ui-views]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-custom-views, q-android-app-lag-analysis--android--medium, q-android-build-optimization--android--medium, q-android-performance-measurement-tools--android--medium, q-canvas-drawing-optimization--android--hard, q-custom-view-lifecycle--android--medium, q-optimize-memory-usage-android--android--medium]
sources: []
created: 2025-10-13
updated: 2025-11-10
tags: [android/performance-rendering, android/ui-graphics, android/ui-views, custom-views, difficulty/medium, performance]

---
# Вопрос (RU)
> Как оптимизировать отрисовку Canvas для достижения 60 FPS?

# Question (EN)
> How do you optimize Canvas drawing to achieve 60 FPS?

---

## Ответ (RU)

### Цель Производительности
**60 FPS = 16.67 мс/кадр**. Хорошая цель для `onDraw()`: **~3-5 мс** (остальное — измерение, компоновка, системные операции). Минимизируйте аллокации в цикле отрисовки, особенно в часто вызываемых методах; избегайте лишних объектов на каждый кадр, чтобы не провоцировать GC во время анимаций.

### 1. Паттерн Без Аллокаций

Создавайте `Paint`/`Path`/`Rect`/`Matrix` как поля класса. Переиспользуйте через `reset()`/`set()`.

```kotlin
class OptimizedView(context: Context, attrs: AttributeSet? = null) : View(context, attrs) {
  // ✅ Выделить память один раз
  private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
  private val rect = RectF()
  private val path = Path()
  private val radius = 40f

  override fun onDraw(canvas: Canvas) {
    // ✅ Переиспользование
    rect.set(0f, 0f, width.toFloat(), height.toFloat())
    path.reset()
    path.addCircle(width / 2f, height / 2f, radius, Path.Direction.CW)

    canvas.drawPath(path, paint)

    // ❌ Избегать новых объектов здесь без необходимости
    // val tempPaint = Paint() // Аллокация каждый кадр!
  }
}
```

**Результат**: сниженный риск GC-пауз во время отрисовки.

### 2. Аппаратное Ускорение (GPU)

```kotlin
// Включить аппаратную отрисовку слоя для этого View
setLayerType(LAYER_TYPE_HARDWARE, null)
```

**Когда использовать**:
- Статичный или редко меняющийся сложный контент, который выгодно кешировать в отдельном слое
- Сложная графика (тени, градиенты, размытие), поддерживаемая аппаратным ускорением
- Анимации, где эффекты могут быть эффективно отрисованы GPU

**Эффект**: может существенно ускорить сложные операции по сравнению с программным рендерингом, но выигрыш зависит от устройства и конкретной сцены.

**Компромиссы**:
- Дополнительная память под текстуры на GPU
- Частая инвалидация большого или сложного аппаратного слоя может съесть выигрыш
- Некоторые эффекты поддерживаются только в программном рендеринге (может потребоваться `LAYER_TYPE_SOFTWARE` для конкретных кейсов)

### 3. Bitmap-кеширование

Рендерьте дорогой контент один раз, сохраните в `Bitmap`, переиспользуйте.

```kotlin
private var cache: Bitmap? = null
private var cacheValid = false

override fun onDraw(canvas: Canvas) {
  if (width == 0 || height == 0) return

  if (!cacheValid || cache?.width != width || cache?.height != height) {
    // Освобождаем предыдущий Bitmap, если размер изменился
    cache?.recycle()

    cache = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
    val offscreenCanvas = Canvas(cache!!)
    drawComplexBackground(offscreenCanvas)  // Дорогая операция
    cacheValid = true
  }

  cache?.let { canvas.drawBitmap(it, 0f, 0f, null) }
}

fun invalidateCache() {
  cacheValid = false
  invalidate()
}
```

**Применение**: фоновые узоры, сложные статичные слои, комбинации нескольких дорогих операций.

**Замечание**: учитывайте расход памяти под большие `Bitmap`-ы; следите за жизненным циклом и очисткой.

### 4. Клиппинг Видимой Области

Рисуйте только видимые элементы.

```kotlin
override fun onDraw(canvas: Canvas) {
  val visibleBounds = canvas.clipBounds

  for (item in items) {
    if (Rect.intersects(item.bounds, visibleBounds)) {
      item.draw(canvas)
    }
  }
}
```

**Эффект**: значительное снижение лишней работы при прокрутке или большом количестве элементов; реальный выигрыш зависит от сцены.

### 5. Оптимизация Paint

```kotlin
// ✅ Хорошо: простые настройки там, где качество приемлемо
paint.isAntiAlias = false  // Для прямых линий / пиксель-идеальной графики
paint.color = Color.parseColor("#FF5733")  // Непрозрачный
paint.style = Paint.Style.FILL

// ❌ Осторожно: потенциально дорогие операции
paint.isAntiAlias = true              // Требует дополнительной обработки пикселей
paint.alpha = 128                     // Включает альфа-блендинг
paint.setShadowLayer(10f, 0f, 0f, Color.BLACK)  // Тяжелая операция, особенно на больших объектах
```

**Совет**: включайте `Paint.ANTI_ALIAS_FLAG` и сложные эффекты только там, где это визуально оправдано, и измеряйте влияние.

### Профилирование

```kotlin
override fun onDraw(canvas: Canvas) {
  Trace.beginSection("CustomViewDraw")
  // Код отрисовки
  Trace.endSection()
}
```

Анализируйте через Android Studio Profiler → CPU → System Trace, а также инспектируйте кадры в Layout Inspector и профилях рендеринга.

---

## Answer (EN)

### Performance Target
**60 FPS = 16.67 ms/frame**. A good target for `onDraw()`: **~3-5 ms** (the rest is for measure, layout, and system overhead). Minimize allocations in the draw path, especially per-frame; avoid unnecessary objects every frame to reduce the risk of GC during animations.

### 1. Zero-Allocation Pattern

Create `Paint`/`Path`/`Rect`/`Matrix` as class fields. Reuse via `reset()`/`set()`.

```kotlin
class OptimizedView(context: Context, attrs: AttributeSet? = null) : View(context, attrs) {
  // ✅ Allocate once
  private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
  private val rect = RectF()
  private val path = Path()
  private val radius = 40f

  override fun onDraw(canvas: Canvas) {
    // ✅ Reuse
    rect.set(0f, 0f, width.toFloat(), height.toFloat())
    path.reset()
    path.addCircle(width / 2f, height / 2f, radius, Path.Direction.CW)

    canvas.drawPath(path, paint)

    // ❌ Avoid new objects here unless truly necessary
    // val tempPaint = Paint() // Allocation per frame!
  }
}
```

**Result**: reduced risk of GC pauses during rendering.

### 2. Hardware Acceleration (GPU)

```kotlin
// Enable hardware-accelerated layer for this View
setLayerType(LAYER_TYPE_HARDWARE, null)
```

**When to use**:
- Static or infrequently changing complex content that benefits from being cached into a separate layer
- Complex graphics (shadows, gradients, blur) supported by hardware acceleration
- Animations where the GPU can efficiently handle the drawing workload

**Impact**: can significantly speed up complex drawing compared to pure software rendering, but the gain depends on the device and scene.

**Trade-offs**:
- Extra GPU memory for layer textures
- Frequent invalidation of a large/complex hardware layer can reduce or negate benefits
- Some effects are only supported in software rendering (may require `LAYER_TYPE_SOFTWARE` for specific cases)

### 3. Bitmap Caching

Render expensive content once, save to `Bitmap`, reuse.

```kotlin
private var cache: Bitmap? = null
private var cacheValid = false

override fun onDraw(canvas: Canvas) {
  if (width == 0 || height == 0) return

  if (!cacheValid || cache?.width != width || cache?.height != height) {
    // Release previous bitmap if size has changed
    cache?.recycle()

    cache = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
    val offscreenCanvas = Canvas(cache!!)
    drawComplexBackground(offscreenCanvas)  // Expensive operation
    cacheValid = true
  }

  cache?.let { canvas.drawBitmap(it, 0f, 0f, null) }
}

fun invalidateCache() {
  cacheValid = false
  invalidate()
}
```

**Use cases**: background patterns, complex static layers, combinations of several expensive operations.

**Note**: consider memory usage for large `Bitmap`s; manage lifecycle and cleanup carefully.

### 4. Clipping to Visible Region

Draw only visible items.

```kotlin
override fun onDraw(canvas: Canvas) {
  val visibleBounds = canvas.clipBounds

  for (item in items) {
    if (Rect.intersects(item.bounds, visibleBounds)) {
      item.draw(canvas)
    }
  }
}
```

**Impact**: can greatly reduce overdraw and wasted work for scrollable or large content; actual speedup depends on the scenario.

### 5. Paint Optimization

```kotlin
// ✅ Good: simple settings where quality is acceptable
paint.isAntiAlias = false  // For straight lines / pixel-perfect graphics
paint.color = Color.parseColor("#FF5733")  // Opaque
paint.style = Paint.Style.FILL

// ❌ Caution: potentially expensive operations
paint.isAntiAlias = true              // Requires extra pixel processing
paint.alpha = 128                     // Triggers alpha blending
paint.setShadowLayer(10f, 0f, 0f, Color.BLACK)  // Heavy, especially on large shapes
```

**Tip**: enable `Paint.ANTI_ALIAS_FLAG` and heavy effects only where visually needed, and measure their impact.

### Profiling

```kotlin
override fun onDraw(canvas: Canvas) {
  Trace.beginSection("CustomViewDraw")
  // Drawing code
  Trace.endSection()
}
```

Analyze via Android Studio Profiler → CPU → System Trace, and inspect rendering using Layout Inspector / rendering profiles.

---

## Дополнительные Вопросы (RU)

- Как овердроу влияет на производительность Canvas и как его обнаружить?
- Когда следует использовать `LAYER_TYPE_SOFTWARE` vs `LAYER_TYPE_HARDWARE`?
- Как реализовать эффективное переиспользование представлений для прокручиваемых списков на основе Canvas?
- Каковы последствия по памяти при использовании Bitmap-кеширования для больших представлений?
- Как оптимизировать операции с `Path` для сложной векторной графики?

## Follow-ups

- How does overdraw affect Canvas performance and how to detect it?
- When should you use `LAYER_TYPE_SOFTWARE` vs `LAYER_TYPE_HARDWARE`?
- How to implement efficient view recycling for scrollable canvas-based lists?
- What are the memory implications of Bitmap caching for large views?
- How to optimize `Path` operations for complex vector graphics?

## Ссылки (RU)

- [[c-custom-views]] — основы работы с кастомными `View`
- [Rendering Performance](https://developer.android.com/topic/performance/rendering)
- https://developer.android.com/topic/performance/vitals/render

## References

- [[c-custom-views]] - Custom `View` fundamentals
- [Rendering Performance](https://developer.android.com/topic/performance/rendering)
- https://developer.android.com/topic/performance/vitals/render

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-custom-view-lifecycle--android--medium]] - основы жизненного цикла кастомных `View`
- [[q-android-performance-measurement-tools--android--medium]] - обзор инструментов профилирования

### Похожие (средний уровень)
- [[q-android-app-lag-analysis--android--medium]] - анализ просадок кадров
- [[q-canvas-drawing-optimization--android--hard]] - продвинутые техники Canvas

### Продвинутые (сложнее)
- [[q-canvas-drawing-optimization--android--hard]] - продвинутая оптимизация отрисовки Canvas

## Related Questions

### Prerequisites (Easier)
- [[q-custom-view-lifecycle--android--medium]] - Custom `View` lifecycle basics
- [[q-android-performance-measurement-tools--android--medium]] - Profiling tools overview

### Related (Same Level)
- [[q-android-app-lag-analysis--android--medium]] - Frame drop analysis
- [[q-canvas-drawing-optimization--android--hard]] - Advanced Canvas techniques

### Advanced (Harder)
- [[q-canvas-drawing-optimization--android--hard]] - Advanced Canvas techniques
