---
id: "20251015082237381"
title: "Canvas Optimization / Canvas Оптимизация"
topic: android
difficulty: medium
status: draft
created: 2025-10-13
tags: - android
  - canvas
  - custom-drawing
  - graphics
  - performance
  - optimization
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-android
related_questions: []
---
# Canvas Optimization and Custom Drawing

# Question (EN)
> 

# Вопрос (RU)
> 

---

## Answer (EN)
# Question (EN)
How do you optimize Canvas drawing operations in Android? What are the best practices for custom rendering, double buffering, and hardware acceleration? How do you handle complex paths and animations efficiently?

## Answer (EN)
Canvas is Android's primary 2D drawing API, but inefficient usage can cause performance issues. Understanding optimization techniques is crucial for creating smooth custom views and animations.

#### 1. Canvas Fundamentals and Optimization

**Optimized Custom View:**
```kotlin
class OptimizedCanvasView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    // Reuse Paint objects - creating new ones in onDraw is expensive
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }

    private val strokePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 4f
        color = Color.BLACK
    }

    private val textPaint = TextPaint(Paint.ANTI_ALIAS_FLAG).apply {
        textSize = 48f
        color = Color.WHITE
        typeface = Typeface.DEFAULT_BOLD
    }

    // Reuse drawing objects
    private val rect = RectF()
    private val path = Path()
    private val matrix = Matrix()

    // Cache expensive calculations
    private var centerX = 0f
    private var centerY = 0f
    private var radius = 0f

    init {
        // Enable hardware acceleration (usually enabled by default)
        setLayerType(LAYER_TYPE_HARDWARE, null)
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)

        // Cache calculations that depend on view size
        centerX = w / 2f
        centerY = h / 2f
        radius = min(w, h) / 3f

        // Recreate path when size changes
        updatePath()
    }

    private fun updatePath() {
        path.reset()
        path.addCircle(centerX, centerY, radius, Path.Direction.CW)
        path.close()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        // Use canvas.save/restore for isolated transformations
        canvas.save()

        // Draw circle
        canvas.drawCircle(centerX, centerY, radius, paint)
        canvas.drawCircle(centerX, centerY, radius, strokePaint)

        // Draw text (use StaticLayout for multi-line text)
        val text = "Optimized"
        rect.set(0f, 0f, textPaint.measureText(text), textPaint.textSize)
        rect.offset(centerX - rect.width() / 2, centerY + rect.height() / 2)

        canvas.drawText(text, rect.left, rect.bottom, textPaint)

        canvas.restore()
    }

    /**
     * Invalidate only specific region instead of entire view
     */
    fun invalidateCircle() {
        val left = (centerX - radius - strokePaint.strokeWidth).toInt()
        val top = (centerY - radius - strokePaint.strokeWidth).toInt()
        val right = (centerX + radius + strokePaint.strokeWidth).toInt()
        val bottom = (centerY + radius + strokePaint.strokeWidth).toInt()

        invalidate(left, top, right, bottom)
    }

    /**
     * Change color with optimized invalidation
     */
    fun setCircleColor(color: Int) {
        if (paint.color != color) {
            paint.color = color
            invalidateCircle()
        }
    }
}
```

**Hardware Acceleration Best Practices:**
```kotlin
class HardwareAcceleratedView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val paint = Paint()

    init {
        // Hardware layers cache the view's rendering on GPU
        // Use for complex views that don't change often
        setLayerType(LAYER_TYPE_HARDWARE, null)
    }

    /**
     * Operations well-supported by hardware acceleration:
     * - drawBitmap (simple transformations)
     * - drawRect, drawRoundRect
     * - drawCircle, drawOval
     * - drawArc (simple)
     * - drawPath (simple paths)
     * - drawText (simple)
     * - Canvas transformations (translate, rotate, scale)
     */
    fun drawHardwareAccelerated(canvas: Canvas) {
        // These operations are GPU-accelerated
        canvas.drawColor(Color.WHITE)
        canvas.drawRect(100f, 100f, 300f, 300f, paint)
        canvas.drawCircle(400f, 400f, 100f, paint)

        // Simple transformations are accelerated
        canvas.save()
        canvas.rotate(45f, 500f, 500f)
        canvas.drawBitmap(getBitmap(), 500f, 500f, paint)
        canvas.restore()
    }

    /**
     * Operations NOT well-supported (use software layer):
     * - drawBitmapMesh
     * - drawPicture
     * - drawVertices
     * - drawTextOnPath
     * - Complex paths with PathEffect
     * - Certain paint operations (some shaders, xfermode)
     */
    fun drawSoftwareOnly(canvas: Canvas) {
        // Temporarily disable hardware acceleration for unsupported ops
        setLayerType(LAYER_TYPE_SOFTWARE, null)

        // Draw complex operations
        val path = Path().apply {
            // Complex path operations
        }
        paint.pathEffect = DashPathEffect(floatArrayOf(10f, 5f), 0f)
        canvas.drawPath(path, paint)

        // Re-enable hardware acceleration
        setLayerType(LAYER_TYPE_HARDWARE, null)
    }

    /**
     * Use LAYER_TYPE_NONE when:
     * - View content changes frequently
     * - Simple drawing operations
     * - Want to save memory
     */
    fun useDefaultLayerType() {
        setLayerType(LAYER_TYPE_NONE, null)
    }

    private fun getBitmap(): Bitmap {
        return Bitmap.createBitmap(100, 100, Bitmap.Config.ARGB_8888)
    }
}
```

#### 2. Double Buffering and Off-Screen Rendering

**Double Buffering Implementation:**
```kotlin
class DoubleBufferedView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var bufferBitmap: Bitmap? = null
    private var bufferCanvas: Canvas? = null
    private val paint = Paint()

    private val drawables = mutableListOf<Drawable>()

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)

        // Create off-screen buffer
        if (w > 0 && h > 0) {
            bufferBitmap?.recycle()
            bufferBitmap = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888)
            bufferCanvas = Canvas(bufferBitmap!!)

            // Redraw content to buffer
            drawToBuffer()
        }
    }

    /**
     * Draw complex content to off-screen buffer
     * This happens only when content changes, not every frame
     */
    private fun drawToBuffer() {
        val canvas = bufferCanvas ?: return

        // Clear buffer
        canvas.drawColor(Color.TRANSPARENT, PorterDuff.Mode.CLEAR)

        // Draw all complex content to buffer
        drawables.forEach { drawable ->
            drawable.draw(canvas)
        }
    }

    override fun onDraw(canvas: Canvas) {
        // Simply blit the pre-rendered buffer
        bufferBitmap?.let {
            canvas.drawBitmap(it, 0f, 0f, paint)
        }
    }

    /**
     * Add drawable and redraw buffer
     */
    fun addDrawable(drawable: Drawable) {
        drawables.add(drawable)
        drawToBuffer()
        invalidate()
    }

    /**
     * Clear all and redraw
     */
    fun clear() {
        drawables.clear()
        drawToBuffer()
        invalidate()
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        bufferBitmap?.recycle()
        bufferBitmap = null
        bufferCanvas = null
    }

    interface Drawable {
        fun draw(canvas: Canvas)
    }
}
```

**Picture for Recorded Drawing:**
```kotlin
class PictureBasedView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var picture: Picture? = null
    private val paint = Paint()

    /**
     * Picture records drawing commands (like a display list)
     * More memory efficient than Bitmap for vector content
     */
    fun recordDrawing(width: Int, height: Int, draw: (Canvas) -> Unit) {
        picture = Picture().apply {
            val canvas = beginRecording(width, height)
            draw(canvas)
            endRecording()
        }
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        picture?.let { pic ->
            // Replay recorded drawing commands
            canvas.drawPicture(pic)

            // Or draw with transformations
            canvas.save()
            canvas.scale(2f, 2f)
            canvas.drawPicture(pic)
            canvas.restore()
        }
    }

    /**
     * Convert Picture to Bitmap if needed
     */
    fun pictureToBitmap(picture: Picture): Bitmap {
        val bitmap = Bitmap.createBitmap(
            picture.width,
            picture.height,
            Bitmap.Config.ARGB_8888
        )
        val canvas = Canvas(bitmap)
        canvas.drawPicture(picture)
        return bitmap
    }
}
```

#### 3. Complex Path Optimization

**Path Caching and Optimization:**
```kotlin
class PathOptimizationView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 4f
        strokeCap = Paint.Cap.ROUND
        strokeJoin = Paint.Join.ROUND
    }

    // Cache computed paths
    private val pathCache = mutableMapOf<String, Path>()

    // Reusable objects
    private val tempPath = Path()
    private val pathMeasure = PathMeasure()

    /**
     * Create and cache complex path
     */
    fun createStarPath(cx: Float, cy: Float, outerRadius: Float, innerRadius: Float): Path {
        val cacheKey = "star_${cx}_${cy}_${outerRadius}_$innerRadius"

        return pathCache.getOrPut(cacheKey) {
            Path().apply {
                val points = 10 // 5-pointed star
                val angle = Math.PI / points

                moveTo(
                    cx + (outerRadius * cos(0.0)).toFloat(),
                    cy + (outerRadius * sin(0.0)).toFloat()
                )

                for (i in 1 until points * 2) {
                    val radius = if (i % 2 == 0) outerRadius else innerRadius
                    val currentAngle = angle * i
                    lineTo(
                        cx + (radius * cos(currentAngle)).toFloat(),
                        cy + (radius * sin(currentAngle)).toFloat()
                    )
                }

                close()
            }
        }
    }

    /**
     * Optimize path by reducing points
     */
    fun simplifyPath(path: Path, tolerance: Float): Path {
        val simplified = Path()
        val points = mutableListOf<PointF>()

        // Extract points from path
        pathMeasure.setPath(path, false)
        val length = pathMeasure.length
        val coords = FloatArray(2)

        var distance = 0f
        while (distance <= length) {
            pathMeasure.getPosTan(distance, coords, null)
            points.add(PointF(coords[0], coords[1]))
            distance += tolerance
        }

        // Reconstruct simplified path
        if (points.isNotEmpty()) {
            simplified.moveTo(points[0].x, points[0].y)
            for (i in 1 until points.size) {
                simplified.lineTo(points[i].x, points[i].y)
            }
        }

        return simplified
    }

    /**
     * Interpolate between two paths for animation
     */
    fun interpolatePaths(start: Path, end: Path, fraction: Float): Path {
        // Note: Paths must be compatible (same number/type of operations)
        val result = Path()

        // This is simplified - real implementation needs path parsing
        // Consider using AnimatedVectorDrawable for complex path morphing

        return result
    }

    /**
     * Draw path with dash effect efficiently
     */
    fun drawDashedPath(canvas: Canvas, path: Path, dashLength: Float, gapLength: Float) {
        val dashedPaint = Paint(paint).apply {
            pathEffect = DashPathEffect(floatArrayOf(dashLength, gapLength), 0f)
        }
        canvas.drawPath(path, dashedPaint)
    }

    /**
     * Draw text along path
     */
    fun drawTextOnPath(canvas: Canvas, text: String, path: Path) {
        val textPaint = TextPaint(Paint.ANTI_ALIAS_FLAG).apply {
            textSize = 32f
            color = Color.BLACK
        }
        canvas.drawTextOnPath(text, path, 0f, 0f, textPaint)
    }

    /**
     * Get path bounds efficiently
     */
    fun getPathBounds(path: Path): RectF {
        val bounds = RectF()
        path.computeBounds(bounds, true) // true = exact bounds (slower), false = approximate (faster)
        return bounds
    }

    override fun onDraw(canvas: Canvas) {
        // Use cached paths
        val starPath = createStarPath(width / 2f, height / 2f, 200f, 100f)
        canvas.drawPath(starPath, paint)
    }

    /**
     * Clear cache if memory is low
     */
    fun clearPathCache() {
        pathCache.clear()
    }
}
```

#### 4. Animated Canvas Drawing

**Smooth Animation Implementation:**
```kotlin
class AnimatedCanvasView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)

    // Animation state
    private var animationProgress = 0f
    private var isAnimating = false

    // Use ValueAnimator for smooth 60fps animation
    private val animator = ValueAnimator.ofFloat(0f, 1f).apply {
        duration = 1000
        interpolator = AccelerateDecelerateInterpolator()
        addUpdateListener { animation ->
            animationProgress = animation.animatedValue as Float
            invalidate() // Request redraw
        }
        addListener(object : AnimatorListenerAdapter() {
            override fun onAnimationEnd(animation: Animator) {
                isAnimating = false
            }
        })
    }

    /**
     * Start animation
     */
    fun startAnimation() {
        if (!isAnimating) {
            isAnimating = true
            animator.start()
        }
    }

    /**
     * Draw with current animation progress
     */
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        if (!isAnimating) return

        val cx = width / 2f
        val cy = height / 2f

        // Animated circle growth
        val radius = 100f * animationProgress
        paint.color = Color.BLUE
        paint.alpha = (255 * (1 - animationProgress)).toInt()
        canvas.drawCircle(cx, cy, radius, paint)

        // Animated rotation
        canvas.save()
        canvas.rotate(360f * animationProgress, cx, cy)
        paint.color = Color.RED
        paint.alpha = 255
        canvas.drawRect(cx - 50, cy - 50, cx + 50, cy + 50, paint)
        canvas.restore()
    }

    /**
     * Use Choreographer for custom animation frame callbacks
     */
    private val frameCallback = object : Choreographer.FrameCallback {
        override fun doFrame(frameTimeNanos: Long) {
            // Custom animation logic
            updateAnimationState(frameTimeNanos)
            invalidate()

            if (isAnimating) {
                Choreographer.getInstance().postFrameCallback(this)
            }
        }
    }

    private fun updateAnimationState(frameTimeNanos: Long) {
        // Update animation based on frame time
    }

    fun startCustomAnimation() {
        isAnimating = true
        Choreographer.getInstance().postFrameCallback(frameCallback)
    }

    fun stopCustomAnimation() {
        isAnimating = false
        Choreographer.getInstance().removeFrameCallback(frameCallback)
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        animator.cancel()
        stopCustomAnimation()
    }
}
```

**Frame Rate Optimization:**
```kotlin
class OptimizedAnimationView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val paint = Paint()
    private var lastFrameTime = 0L
    private var fps = 0
    private var frameCount = 0

    // Throttle frame rate for battery saving
    private val targetFrameTime = 1000L / 30L // 30 FPS
    private var lastDrawTime = 0L

    /**
     * Measure and display FPS
     */
    override fun onDraw(canvas: Canvas) {
        val currentTime = System.currentTimeMillis()

        // Throttle frame rate
        if (currentTime - lastDrawTime < targetFrameTime) {
            postInvalidateDelayed(targetFrameTime - (currentTime - lastDrawTime))
            return
        }
        lastDrawTime = currentTime

        // Calculate FPS
        frameCount++
        if (currentTime - lastFrameTime >= 1000) {
            fps = frameCount
            frameCount = 0
            lastFrameTime = currentTime
        }

        // Draw content
        drawContent(canvas)

        // Draw FPS counter
        paint.color = Color.GREEN
        paint.textSize = 32f
        canvas.drawText("FPS: $fps", 20f, 50f, paint)
    }

    private fun drawContent(canvas: Canvas) {
        // Your drawing code here
    }

    /**
     * Use dirty region tracking for partial updates
     */
    private val dirtyRegion = Rect()

    fun markRegionDirty(left: Int, top: Int, right: Int, bottom: Int) {
        dirtyRegion.set(left, top, right, bottom)
        invalidate(dirtyRegion)
    }
}
```

#### 5. Bitmap Operations and Caching

**Efficient Bitmap Handling:**
```kotlin
class BitmapCanvasView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        isFilterBitmap = true // Enable bitmap filtering
        isDither = true // Enable dithering
    }

    // Bitmap pool for reuse
    private val bitmapPool = mutableListOf<Bitmap>()
    private val maxPoolSize = 10

    /**
     * Get bitmap from pool or create new
     */
    fun obtainBitmap(width: Int, height: Int, config: Bitmap.Config): Bitmap {
        // Try to find reusable bitmap
        val reusable = bitmapPool.find {
            it.width == width && it.height == height && it.config == config
        }

        return if (reusable != null) {
            bitmapPool.remove(reusable)
            reusable.eraseColor(Color.TRANSPARENT)
            reusable
        } else {
            Bitmap.createBitmap(width, height, config)
        }
    }

    /**
     * Return bitmap to pool
     */
    fun recycleBitmap(bitmap: Bitmap) {
        if (bitmapPool.size < maxPoolSize && !bitmap.isRecycled) {
            bitmapPool.add(bitmap)
        } else {
            bitmap.recycle()
        }
    }

    /**
     * Draw bitmap with transformations
     */
    fun drawTransformedBitmap(canvas: Canvas, bitmap: Bitmap, matrix: Matrix) {
        // Use matrix for efficient transformations
        canvas.drawBitmap(bitmap, matrix, paint)
    }

    /**
     * Draw bitmap with shader for tiling/patterns
     */
    fun drawBitmapPattern(canvas: Canvas, bitmap: Bitmap) {
        val shader = BitmapShader(bitmap, Shader.TileMode.REPEAT, Shader.TileMode.REPEAT)
        val patternPaint = Paint().apply {
            this.shader = shader
        }
        canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), patternPaint)
    }

    /**
     * Downscale bitmap for efficient drawing
     */
    fun downscaleBitmap(original: Bitmap, maxWidth: Int, maxHeight: Int): Bitmap {
        if (original.width <= maxWidth && original.height <= maxHeight) {
            return original
        }

        val ratio = min(
            maxWidth.toFloat() / original.width,
            maxHeight.toFloat() / original.height
        )

        val newWidth = (original.width * ratio).toInt()
        val newHeight = (original.height * ratio).toInt()

        return Bitmap.createScaledBitmap(original, newWidth, newHeight, true)
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        bitmapPool.forEach { it.recycle() }
        bitmapPool.clear()
    }
}
```

### Best Practices

1. **Object Reuse:**
   - Reuse Paint, Path, Rect, Matrix objects
   - Avoid allocations in onDraw()
   - Use object pools for frequently created objects

2. **Hardware Acceleration:**
   - Use LAYER_TYPE_HARDWARE for static complex views
   - Use LAYER_TYPE_SOFTWARE only for unsupported operations
   - Profile with GPU rendering tools

3. **Partial Invalidation:**
   - Use invalidate(Rect) for partial updates
   - Only redraw changed regions
   - Track dirty regions explicitly

4. **Path Optimization:**
   - Cache complex paths
   - Simplify paths when possible
   - Use PathMeasure for path analysis

5. **Animation:**
   - Target 60fps (16ms per frame)
   - Use ValueAnimator or Choreographer
   - Avoid heavy calculations in onDraw()

6. **Memory Management:**
   - Recycle bitmaps when done
   - Use bitmap pooling
   - Clear caches when memory is low

### Common Pitfalls

1. **Allocating in onDraw()** → GC pauses and jank
   - Pre-allocate all objects in constructor or onSizeChanged()

2. **Not using hardware acceleration** → Slow rendering
   - Enable by default, disable only when necessary

3. **Overdrawing** → Wasted GPU cycles
   - Use GPU overdraw visualization tool
   - Clip unnecessary drawing

4. **Not caching complex paths** → Repeated expensive calculations
   - Cache paths that don't change

5. **Full view invalidation** → Unnecessary redraws
   - Use partial invalidation with Rect

6. **Forgetting to recycle bitmaps** → Memory leaks
   - Always recycle or pool bitmaps

### Summary

Canvas optimization is crucial for smooth custom views and animations. Key techniques include object reuse, hardware acceleration, partial invalidation, path caching, and efficient bitmap handling. Understanding hardware acceleration limitations and using appropriate layer types ensures optimal performance across different drawing operations.

---



## Ответ (RU)
# Вопрос (RU)
Как оптимизировать операции рисования Canvas в Android? Каковы лучшие практики для пользовательского рендеринга, двойной буферизации и аппаратного ускорения? Как эффективно обрабатывать сложные пути и анимации?

## Ответ (RU)
Canvas — это основной 2D API для рисования в Android, но неэффективное использование может вызвать проблемы с производительностью. Понимание техник оптимизации критически важно для создания плавных пользовательских view и анимаций.

#### Основные техники оптимизации

**1. Переиспользование объектов:**
- Создавайте Paint, Path, Rect, Matrix один раз
- Избегайте аллокаций в onDraw()
- Используйте пулы объектов

**2. Аппаратное ускорение:**
- LAYER_TYPE_HARDWARE — для статичных сложных view
- LAYER_TYPE_SOFTWARE — только для неподдерживаемых операций
- LAYER_TYPE_NONE — по умолчанию

**Поддерживается GPU:**
- drawBitmap, drawRect, drawCircle, drawOval
- Простые трансформации (translate, rotate, scale)
- Простой drawPath и drawText

**НЕ поддерживается GPU:**
- drawBitmapMesh, drawPicture, drawVertices
- drawTextOnPath
- Сложные PathEffect
- Некоторые shaders и xfermode

**3. Частичная инвалидация:**
```kotlin
// Вместо
invalidate()

// Используйте
invalidate(left, top, right, bottom)
```

**4. Кеширование путей:**
- Кешируйте сложные Path вычисления
- Упрощайте пути при возможности
- Используйте PathMeasure для анализа

**5. Оптимизация анимаций:**
- Целевая частота: 60fps (16мс на кадр)
- Используйте ValueAnimator или Choreographer
- Избегайте тяжёлых вычислений в onDraw()

**6. Двойная буферизация:**
- Используйте off-screen Bitmap для сложного содержимого
- Рисуйте в буфер только при изменениях
- Просто blitting буфера в onDraw()

**7. Управление памятью:**
- Утилизируйте bitmap после использования
- Используйте пулинг bitmap
- Очищайте кеши при нехватке памяти

### Лучшие практики

1. Переиспользуйте Paint и другие объекты рисования
2. Включайте аппаратное ускорение (по умолчанию включено)
3. Используйте частичную инвалидацию
4. Кешируйте сложные вычисления путей
5. Профилируйте с GPU rendering tools
6. Избегайте overdraw
7. Утилизируйте bitmap правильно

### Распространённые ошибки

1. Аллокации в onDraw() → GC паузы
2. Не использовать аппаратное ускорение → медленный рендеринг
3. Overdrawing → потраченные GPU циклы
4. Не кешировать пути → повторные вычисления
5. Полная инвалидация view → лишние перерисовки
6. Не утилизировать bitmap → утечки памяти

### Резюме

Оптимизация Canvas критически важна для плавных пользовательских view и анимаций. Ключевые техники включают переиспользование объектов, аппаратное ускорение, частичную инвалидацию, кеширование путей и эффективную обработку bitmap. Понимание ограничений аппаратного ускорения и использование соответствующих типов слоёв обеспечивает оптимальную производительность для различных операций рисования.

---

## Related Questions

### Kotlin Language Features
- [[q-kotlin-collections--kotlin--medium]] - Data Structures
- [[q-deferred-async-patterns--kotlin--medium]] - Performance
- [[q-coroutine-performance-optimization--kotlin--hard]] - Performance
- [[q-channel-buffering-strategies--kotlin--hard]] - Performance
- [[q-custom-dispatchers-limited-parallelism--kotlin--hard]] - Performance
- [[q-kotlin-inline-functions--kotlin--medium]] - Performance

### Related Algorithms
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Data Structures
