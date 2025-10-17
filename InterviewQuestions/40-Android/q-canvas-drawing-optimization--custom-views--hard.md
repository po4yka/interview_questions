---
id: "20251015082237350"
title: "Canvas Drawing Optimization / Canvas Drawing Оптимизация"
topic: android
difficulty: hard
status: draft
created: 2025-10-15
tags: - custom-views
  - canvas
  - performance
  - graphics
---
# Canvas Drawing Optimization

# Question (EN)
> How do you optimize Canvas drawing operations in custom views? Discuss techniques like object pooling, hardware acceleration, bitmap caching, and avoiding allocations in onDraw().

# Вопрос (RU)
> Как оптимизировать операции отрисовки Canvas в пользовательских view? Обсудите техники, такие как пулинг объектов, аппаратное ускорение, кэширование bitmap и избежание выделения памяти в onDraw().

---

## Answer (EN)

**Canvas drawing optimization** is critical for smooth, performant custom views. Poor drawing performance leads to dropped frames, jank, and bad user experience. Understanding optimization techniques can improve performance by **10-100x**.

### Performance Baseline

**Target: 60 FPS = 16.67ms per frame**
- onDraw() should complete in < 5ms
- Complex animations: < 10ms
- Exceeding 16ms → dropped frames

---

### 1. Never Allocate Objects in onDraw()

**Problem:** Object allocation triggers garbage collection, causing frame drops.

** BAD - Allocates on every frame:**
```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    //  Allocates new Paint every frame!
    val paint = Paint().apply {
        color = Color.BLUE
        strokeWidth = 10f
    }

    //  Allocates new Rect every frame!
    val rect = Rect(0, 0, width, height)

    //  Allocates new Path every frame!
    val path = Path().apply {
        moveTo(0f, 0f)
        lineTo(width.toFloat(), height.toFloat())
    }

    canvas.drawPath(path, paint)
}
```

** GOOD - Pre-allocate and reuse:**
```kotlin
class OptimizedView : View {
    //  Allocate once, reuse forever
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLUE
        strokeWidth = 10f
    }

    private val rect = Rect()
    private val rectF = RectF()
    private val path = Path()
    private val matrix = Matrix()

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        //  Reuse pre-allocated objects
        rect.set(0, 0, width, height)
        path.reset()
        path.moveTo(0f, 0f)
        path.lineTo(width.toFloat(), height.toFloat())

        canvas.drawPath(path, paint)
    }
}
```

**Performance impact:**
- Before: 50 allocations/frame → GC every 2 seconds → 30 FPS
- After: 0 allocations/frame → No GC → 60 FPS
- **2x FPS improvement!**

---

### 2. Hardware Acceleration

**Hardware layers** cache drawing results on GPU, avoiding repeated CPU drawing.

**Use cases:**
- Complex static content
- Views with animations
- Temporarily during animations

```kotlin
class HardwareAcceleratedView : View {

    init {
        // Enable hardware layer
        setLayerType(LAYER_TYPE_HARDWARE, null)
    }

    // For temporary optimization during animation
    fun animateWithHardware() {
        // Enable hardware layer for animation
        setLayerType(LAYER_TYPE_HARDWARE, null)

        animate()
            .alpha(0f)
            .setDuration(300)
            .withEndAction {
                // Disable after animation
                setLayerType(LAYER_TYPE_NONE, null)
            }
            .start()
    }
}
```

**Layer types comparison:**

| Type | Description | Use Case | Performance |
|------|-------------|----------|-------------|
| `LAYER_TYPE_NONE` | Software rendering | Default | Baseline |
| `LAYER_TYPE_SOFTWARE` | Software bitmap cache | Rare | CPU intensive |
| `LAYER_TYPE_HARDWARE` | GPU texture cache | Animations, static complex views | **10x faster** |

**ViewPropertyAnimator automatically uses hardware layers:**
```kotlin
// Automatically uses hardware layer during animation
view.animate()
    .translationX(100f)
    .alpha(0.5f)
    .setDuration(300)
    .start()
```

---

### 3. Bitmap Caching

**Cache complex drawings** to avoid redrawing on every frame.

```kotlin
class CachedDrawingView : View {

    private var cachedBitmap: Bitmap? = null
    private val cachedCanvas = Canvas()
    private val bitmapPaint = Paint(Paint.ANTI_ALIAS_FLAG)

    private var needsRedraw = true

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)

        // Recreate bitmap on size change
        cachedBitmap?.recycle()
        cachedBitmap = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888)
        cachedCanvas.setBitmap(cachedBitmap)

        needsRedraw = true
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val bitmap = cachedBitmap ?: return

        // Only redraw cached content when needed
        if (needsRedraw) {
            drawComplexContent(cachedCanvas)
            needsRedraw = false
        }

        // Fast: just draw the cached bitmap
        canvas.drawBitmap(bitmap, 0f, 0f, bitmapPaint)
    }

    private fun drawComplexContent(canvas: Canvas) {
        // Expensive drawing operations here
        // This only runs when needsRedraw = true
        for (i in 0..1000) {
            canvas.drawCircle(
                random() * width,
                random() * height,
                10f,
                paint
            )
        }
    }

    fun invalidateCache() {
        needsRedraw = true
        invalidate()
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        cachedBitmap?.recycle()
        cachedBitmap = null
    }
}
```

**Performance impact:**
- Without cache: Draw 1000 circles every frame (16ms) → 30 FPS
- With cache: Draw once, then just blit bitmap (0.5ms) → 60 FPS
- **32x faster!**

---

### 4. Clip Rect Optimization

**Only draw visible regions** using canvas clipping.

```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // Get visible region
    val clipBounds = canvas.clipBounds

    for (item in items) {
        //  Skip items outside visible area
        if (!item.bounds.intersect(clipBounds)) {
            continue
        }

        drawItem(canvas, item)
    }
}
```

**Real-world example: Scrollable graph**
```kotlin
class GraphView : View {

    private val dataPoints = mutableListOf<PointF>()

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val clipBounds = canvas.clipBounds

        // Only draw visible data points
        val visiblePoints = dataPoints.filter { point ->
            point.x >= clipBounds.left &&
            point.x <= clipBounds.right &&
            point.y >= clipBounds.top &&
            point.y <= clipBounds.bottom
        }

        // Draw only visible points
        for (i in 0 until visiblePoints.size - 1) {
            canvas.drawLine(
                visiblePoints[i].x,
                visiblePoints[i].y,
                visiblePoints[i + 1].x,
                visiblePoints[i + 1].y,
                paint
            )
        }
    }
}
```

**Performance impact:**
- Before: Draw 10,000 points (even off-screen) → 50ms
- After: Draw 500 visible points only → 2.5ms
- **20x faster!**

---

### 5. Path Caching

**Cache Path objects** for complex shapes that don't change.

```kotlin
class StarView : View {

    private val starPath = Path()
    private var pathCached = false

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        pathCached = false // Invalidate cache on size change
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        if (!pathCached) {
            createStarPath()
            pathCached = true
        }

        // Fast: just draw the cached path
        canvas.drawPath(starPath, paint)
    }

    private fun createStarPath() {
        starPath.reset()

        val cx = width / 2f
        val cy = height / 2f
        val outerRadius = min(width, height) / 2f * 0.8f
        val innerRadius = outerRadius * 0.4f

        // Create 5-point star
        for (i in 0 until 10) {
            val angle = Math.PI / 5 * i - Math.PI / 2
            val radius = if (i % 2 == 0) outerRadius else innerRadius
            val x = cx + (radius * cos(angle)).toFloat()
            val y = cy + (radius * sin(angle)).toFloat()

            if (i == 0) {
                starPath.moveTo(x, y)
            } else {
                starPath.lineTo(x, y)
            }
        }
        starPath.close()
    }
}
```

---

### 6. Paint Optimization

**Reuse Paint objects** and disable unnecessary features.

```kotlin
class OptimizedPaintView : View {

    //  Pre-allocate and configure
    private val fillPaint = Paint().apply {
        style = Paint.Style.FILL
        color = Color.BLUE
        // Only enable anti-aliasing if needed
        isAntiAlias = false // Faster for straight lines/rectangles
    }

    private val strokePaint = Paint().apply {
        style = Paint.Style.STROKE
        strokeWidth = 5f
        isAntiAlias = true // Needed for smooth curves
    }

    private val textPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        textSize = 24f
        color = Color.BLACK
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        // Draw rectangle (no AA needed)
        canvas.drawRect(0f, 0f, 100f, 100f, fillPaint)

        // Draw circle (AA makes it smooth)
        canvas.drawCircle(200f, 200f, 50f, strokePaint)

        // Draw text (AA for readability)
        canvas.drawText("Hello", 300f, 300f, textPaint)
    }
}
```

**Paint optimization tips:**

| Feature | Cost | When to Disable |
|---------|------|----------------|
| Anti-aliasing | Medium | Straight lines, rectangles |
| Alpha blending | High | Opaque colors only |
| Shadows | Very High | When not needed |
| Color filters | High | Simple colors |
| Shader | High | Solid colors |

---

### 7. Canvas.save() / restore() Optimization

**Avoid unnecessary save/restore** - they're expensive.

** SLOW:**
```kotlin
override fun onDraw(canvas: Canvas) {
    for (item in items) {
        canvas.save() // Expensive!
        canvas.translate(item.x, item.y)
        canvas.rotate(item.angle)
        drawItem(canvas, item)
        canvas.restore() // Expensive!
    }
}
```

** FASTER - Use saveLayer sparingly:**
```kotlin
override fun onDraw(canvas: Canvas) {
    for (item in items) {
        // Draw with manual matrix calculations
        val savedMatrix = canvas.matrix
        canvas.translate(item.x, item.y)
        canvas.rotate(item.angle)
        drawItem(canvas, item)
        canvas.matrix = savedMatrix
    }
}
```

** FASTEST - No save/restore:**
```kotlin
private val tempMatrix = Matrix()

override fun onDraw(canvas: Canvas) {
    for (item in items) {
        tempMatrix.reset()
        tempMatrix.setTranslate(item.x, item.y)
        tempMatrix.preRotate(item.angle)

        // Draw with pre-calculated matrix
        drawItemWithMatrix(canvas, item, tempMatrix)
    }
}
```

---

### 8. Real-World Example: Chart Optimization

**Before optimization:**
```kotlin
class SlowChartView : View {

    private val dataPoints = List(1000) { it to random() * height }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        //  Allocations in onDraw
        val paint = Paint()
        val path = Path()

        //  Draw everything, even off-screen
        path.moveTo(0f, dataPoints[0].second.toFloat())
        for ((x, y) in dataPoints) {
            path.lineTo(x.toFloat(), y.toFloat())
        }

        canvas.drawPath(path, paint)

        //  Draw all data point circles
        for ((x, y) in dataPoints) {
            canvas.drawCircle(x.toFloat(), y.toFloat(), 5f, paint)
        }
    }
}
```

**After optimization:**
```kotlin
class FastChartView : View {

    //  Pre-allocate
    private val linePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 3f
        color = Color.BLUE
    }

    private val pointPaint = Paint().apply {
        style = Paint.Style.FILL
        color = Color.RED
        isAntiAlias = false // Faster for small circles
    }

    private val linePath = Path()
    private val dataPoints = List(1000) { it to random() * 1000 }

    //  Bitmap cache for static content
    private var cachedBitmap: Bitmap? = null
    private var needsRedraw = true

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        cachedBitmap?.recycle()
        cachedBitmap = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888)
        needsRedraw = true
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val bitmap = cachedBitmap ?: return

        //  Only redraw when data changes
        if (needsRedraw) {
            val cacheCanvas = Canvas(bitmap)
            drawChart(cacheCanvas)
            needsRedraw = false
        }

        //  Fast bitmap blit
        canvas.drawBitmap(bitmap, 0f, 0f, null)
    }

    private fun drawChart(canvas: Canvas) {
        //  Clip to visible region
        val clipBounds = canvas.clipBounds

        //  Only draw visible points
        val visiblePoints = dataPoints.filter { (x, _) ->
            x >= clipBounds.left && x <= clipBounds.right
        }

        if (visiblePoints.isEmpty()) return

        //  Reuse path
        linePath.reset()
        linePath.moveTo(visiblePoints[0].first.toFloat(), visiblePoints[0].second.toFloat())

        for ((x, y) in visiblePoints.drop(1)) {
            linePath.lineTo(x.toFloat(), y.toFloat())
        }

        canvas.drawPath(linePath, linePaint)

        //  Draw points with batching
        for ((x, y) in visiblePoints) {
            canvas.drawCircle(x.toFloat(), y.toFloat(), 4f, pointPaint)
        }
    }

    fun updateData(newData: List<Pair<Int, Double>>) {
        // dataPoints = newData
        needsRedraw = true
        invalidate()
    }
}
```

**Performance comparison:**

| Optimization | Before | After | Improvement |
|--------------|--------|-------|-------------|
| Object allocation | 1003/frame | 0/frame | ∞ |
| Drawing time | 45ms | 1.5ms | **30x faster** |
| Frame rate | 22 FPS | 60 FPS | **2.7x faster** |
| Memory pressure | High GC | No GC | Smooth |

---

### 9. Profiling Canvas Performance

**Use Android Profiler:**
```kotlin
class ProfiledView : View {

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        // Add trace sections
        Trace.beginSection("DrawBackground")
        drawBackground(canvas)
        Trace.endSection()

        Trace.beginSection("DrawContent")
        drawContent(canvas)
        Trace.endSection()

        Trace.beginSection("DrawOverlay")
        drawOverlay(canvas)
        Trace.endSection()
    }
}
```

**Analyze with systrace:**
```bash
# Capture trace
python systrace.py --time=10 gfx view

# Look for:
# - Frames taking > 16ms
# - Long onDraw() executions
# - GC_FOR_ALLOC events
```

---

### 10. Best Practices Checklist

**Memory:**
-  Pre-allocate Paint, Path, Rect objects
-  Reuse objects with reset() methods
-  Recycle bitmaps in onDetachedFromWindow()
-  Never allocate in onDraw()

**Drawing:**
-  Use hardware layers for animations
-  Cache complex static content to bitmap
-  Clip to visible regions
-  Disable unnecessary Paint features
-  Don't save/restore unnecessarily

**Performance:**
-  Target < 5ms for onDraw()
-  Use Trace.beginSection() for profiling
-  Test on low-end devices
-  Monitor frame rate with GPU rendering

---

### Complete Optimized Example

```kotlin
class HighPerformanceWaveView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    //  Pre-allocated objects
    private val wavePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }

    private val wavePath = Path()
    private val matrix = Matrix()

    //  Cached calculations
    private var amplitude = 0f
    private var wavelength = 0f
    private var phase = 0f

    //  Animation with hardware layer
    private val animator = ValueAnimator.ofFloat(0f, 2 * PI.toFloat()).apply {
        duration = 2000
        repeatCount = ValueAnimator.INFINITE
        addUpdateListener { animation ->
            phase = animation.animatedValue as Float
            invalidate()
        }
    }

    init {
        //  Enable hardware acceleration
        setLayerType(LAYER_TYPE_HARDWARE, null)
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)

        //  Cache calculations on size change
        amplitude = h / 4f
        wavelength = w / 2f
    }

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        animator.start()
    }

    override fun onDetachedFromWindow() {
        animator.cancel()
        super.onDetachedFromWindow()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        Trace.beginSection("WaveView.onDraw")

        //  Reuse path
        wavePath.reset()
        wavePath.moveTo(0f, height / 2f)

        //  Optimized wave calculation
        val step = 10f // Trade accuracy for performance
        var x = 0f
        while (x <= width) {
            val y = height / 2f + amplitude * sin(2 * PI * x / wavelength + phase).toFloat()
            wavePath.lineTo(x, y)
            x += step
        }

        wavePath.lineTo(width.toFloat(), height.toFloat())
        wavePath.lineTo(0f, height.toFloat())
        wavePath.close()

        canvas.drawPath(wavePath, wavePaint)

        Trace.endSection()
    }
}
```

**Result:** Smooth 60 FPS wave animation with no GC pressure!

---

### Summary

**Key optimization techniques:**

1. **Never allocate in onDraw()** - Pre-allocate and reuse objects
2. **Hardware acceleration** - Use LAYER_TYPE_HARDWARE for complex views
3. **Bitmap caching** - Cache static or slowly-changing content
4. **Clip optimization** - Only draw visible regions
5. **Path caching** - Reuse Path objects for complex shapes
6. **Paint optimization** - Disable unnecessary features
7. **Minimize save/restore** - Use matrix calculations instead

**Performance targets:**
- onDraw() < 5ms
- 60 FPS (16.67ms/frame)
- Zero allocations per frame
- Smooth animations with no jank

**Tools:**
- Android Profiler
- Trace.beginSection()
- GPU rendering profile
- Systrace

---

## Ответ (RU)

**Оптимизация отрисовки Canvas** критична для плавных, производительных пользовательских view. Плохая производительность отрисовки приводит к пропущенным кадрам, "дёрганиям" и плохому пользовательскому опыту.

### Ключевые техники оптимизации

**1. Никогда не выделяйте объекты в onDraw()**

```kotlin
//  ПЛОХО
override fun onDraw(canvas: Canvas) {
    val paint = Paint() // Выделение на каждый кадр!
    val rect = Rect() // Выделение на каждый кадр!
}

//  ХОРОШО
class OptimizedView : View {
    private val paint = Paint() // Выделить один раз
    private val rect = Rect()

    override fun onDraw(canvas: Canvas) {
        // Переиспользовать объекты
        rect.set(0, 0, width, height)
    }
}
```

**2. Аппаратное ускорение**

```kotlin
init {
    // Включить hardware layer для кэширования на GPU
    setLayerType(LAYER_TYPE_HARDWARE, null)
}
```

**3. Кэширование Bitmap**

```kotlin
private var cachedBitmap: Bitmap? = null
private var needsRedraw = true

override fun onDraw(canvas: Canvas) {
    if (needsRedraw) {
        drawToCache() // Отрисовать в кэш
        needsRedraw = false
    }
    canvas.drawBitmap(cachedBitmap!!, 0f, 0f, null) // Быстро!
}
```

**4. Оптимизация клиппинга**

```kotlin
override fun onDraw(canvas: Canvas) {
    val clipBounds = canvas.clipBounds

    for (item in items) {
        // Пропустить элементы вне видимости
        if (!item.intersects(clipBounds)) continue
        drawItem(canvas, item)
    }
}
```

### Влияние на производительность

| Оптимизация | До | После | Улучшение |
|------------|-----|-------|-----------|
| Без аллокаций | 30 FPS | 60 FPS | **2x** |
| Hardware layer | 22 FPS | 60 FPS | **2.7x** |
| Bitmap cache | 30 FPS | 60 FPS | **32x быстрее** |
| Clipping | 50ms | 2.5ms | **20x быстрее** |

### Цели производительности

- onDraw() < 5ms
- 60 FPS (16.67ms/кадр)
- Ноль аллокаций на кадр
- Плавные анимации без рывков

---

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-layout-performance-measured-in--android--medium]] - Performance, View
- [[q-dagger-build-time-optimization--android--medium]] - Performance
- [[q-performance-optimization-android--android--medium]] - Performance

### Related (Hard)
- [[q-compose-lazy-layout-optimization--jetpack-compose--hard]] - Performance, View
- [[q-compose-custom-layout--jetpack-compose--hard]] - View
- [[q-compose-performance-optimization--android--hard]] - Performance
