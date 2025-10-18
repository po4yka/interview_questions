---
id: 20251017-104924
title: "Custom Drawable Implementation / Custom Drawable Реализация"
topic: android
difficulty: medium
status: draft
created: 2025-10-13
tags: [views, drawable, graphics, android-framework, android/ui-views, android/ui-graphics, difficulty/medium]
moc: moc-android
related: [q-how-to-pass-parameters-to-a-fragment--android--easy, q-how-to-tell-adapter-to-redraw-list-if-element-was-deleted--android--medium, q-what-problems-can-there-be-with-list-items--android--easy]
subtopics: [ui-views, ui-graphics]
---
# Custom Drawable Implementation

# Question (EN)
> How do you create custom Drawables? Explain the Drawable lifecycle, implementing draw(), bounds management, state handling, and when to use Drawable vs custom View.

# Вопрос (RU)
> Как создать пользовательские Drawables? Объясните жизненный цикл Drawable, реализацию draw(), управление границами, обработку состояния и когда использовать Drawable вместо custom View.

---

## Answer (EN)

**Custom Drawables** are lightweight, reusable graphics that can be used in multiple views. They're more efficient than custom Views when you don't need user interaction or complex lifecycle management.

### Drawable vs Custom View

| Feature | Drawable | Custom View |
|---------|----------|-------------|
| **Use case** | Simple graphics, icons | Interactive UI elements |
| **Performance** | Lightweight | Heavier (full View) |
| **Interaction** | No touch handling | Full touch support |
| **Lifecycle** | Simple | Complex (attach/detach) |
| **Reusability** | High | Lower |
| **State** | Limited (ColorStateList) | Full state management |

**Use Drawable when:**
- Non-interactive graphics
- Reusable across views
- Simple shapes/animations
- Background/foreground graphics

**Use Custom View when:**
- Need touch interaction
- Complex lifecycle
- Accessibility requirements
- Animation coordination

---

### 1. Basic Custom Drawable

```kotlin
class CircleDrawable : Drawable() {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }

    var color: Int
        get() = paint.color
        set(value) {
            paint.color = value
            invalidateSelf() // Request redraw
        }

    //  Main drawing method
    override fun draw(canvas: Canvas) {
        val bounds = bounds
        val centerX = bounds.centerX().toFloat()
        val centerY = bounds.centerY().toFloat()
        val radius = min(bounds.width(), bounds.height()) / 2f

        canvas.drawCircle(centerX, centerY, radius, paint)
    }

    //  Set opacity (required)
    override fun setAlpha(alpha: Int) {
        paint.alpha = alpha
        invalidateSelf()
    }

    //  Set color filter (required)
    override fun setColorFilter(colorFilter: ColorFilter?) {
        paint.colorFilter = colorFilter
        invalidateSelf()
    }

    //  Return opacity (required)
    @Deprecated("Deprecated in Java", ReplaceWith("PixelFormat.TRANSLUCENT"))
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT

    //  Intrinsic size (optional)
    override fun getIntrinsicWidth(): Int = 48.dpToPx()
    override fun getIntrinsicHeight(): Int = 48.dpToPx()

    private fun Int.dpToPx(): Int =
        (this * Resources.getSystem().displayMetrics.density).toInt()
}
```

**Usage:**
```kotlin
// Set as background
view.background = CircleDrawable()

// Set as ImageView source
imageView.setImageDrawable(CircleDrawable())

// Set programmatically
val circle = CircleDrawable().apply {
    color = Color.RED
    setBounds(0, 0, 100, 100)
}
canvas.draw(circle)
```

---

### 2. Bounds Management

Drawable must respect the bounds set by the container.

```kotlin
class RectangleDrawable : Drawable() {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)

    override fun draw(canvas: Canvas) {
        //  Always use bounds, never hardcode coordinates
        val bounds = bounds

        // Draw within bounds
        canvas.drawRect(bounds, paint)

        // Or calculate relative coordinates
        val centerX = bounds.centerX().toFloat()
        val centerY = bounds.centerY().toFloat()
        val width = bounds.width().toFloat()
        val height = bounds.height().toFloat()

        // Draw something centered
        canvas.drawRoundRect(
            centerX - width / 4,
            centerY - height / 4,
            centerX + width / 4,
            centerY + height / 4,
            10f, 10f,
            paint
        )
    }

    //  React to bounds changes
    override fun onBoundsChange(bounds: Rect) {
        super.onBoundsChange(bounds)

        // Recreate size-dependent objects
        recreateShader(bounds)
    }

    private fun recreateShader(bounds: Rect) {
        val shader = LinearGradient(
            bounds.left.toFloat(),
            bounds.top.toFloat(),
            bounds.right.toFloat(),
            bounds.bottom.toFloat(),
            Color.BLUE,
            Color.GREEN,
            Shader.TileMode.CLAMP
        )
        paint.shader = shader
    }

    override fun setAlpha(alpha: Int) {
        paint.alpha = alpha
    }

    override fun setColorFilter(colorFilter: ColorFilter?) {
        paint.colorFilter = colorFilter
    }

    @Deprecated("Deprecated in Java")
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}
```

---

### 3. Stateful Drawable

Respond to view state changes (pressed, focused, etc.).

```kotlin
class StatefulButtonDrawable : Drawable() {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
    }

    private val normalColor = Color.BLUE
    private val pressedColor = Color.DARK_GRAY
    private val disabledColor = Color.LIGHT_GRAY

    init {
        paint.color = normalColor
    }

    override fun draw(canvas: Canvas) {
        val bounds = bounds
        canvas.drawRoundRect(
            bounds.left.toFloat(),
            bounds.top.toFloat(),
            bounds.right.toFloat(),
            bounds.bottom.toFloat(),
            20f, 20f,
            paint
        )
    }

    //  Declare which states this drawable handles
    override fun isStateful(): Boolean = true

    //  Handle state changes
    override fun onStateChange(state: IntArray): Boolean {
        val oldColor = paint.color

        paint.color = when {
            state.contains(android.R.attr.state_pressed) -> pressedColor
            state.contains(android.R.attr.state_enabled).not() -> disabledColor
            else -> normalColor
        }

        // Return true if visual changed (triggers redraw)
        return oldColor != paint.color
    }

    override fun setAlpha(alpha: Int) {
        paint.alpha = alpha
    }

    override fun setColorFilter(colorFilter: ColorFilter?) {
        paint.colorFilter = colorFilter
    }

    @Deprecated("Deprecated in Java")
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}
```

**Usage:**
```kotlin
button.background = StatefulButtonDrawable()
// Automatically changes color when pressed!
```

---

### 4. Animated Drawable

```kotlin
class SpinnerDrawable : Drawable(), Animatable {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 8f
        color = Color.BLUE
        strokeCap = Paint.Cap.ROUND
    }

    private var rotation = 0f
    private var isRunning = false

    private val animator = ValueAnimator.ofFloat(0f, 360f).apply {
        duration = 1000
        repeatCount = ValueAnimator.INFINITE
        interpolator = LinearInterpolator()
        addUpdateListener { animation ->
            rotation = animation.animatedValue as Float
            invalidateSelf() // Request redraw
        }
    }

    override fun draw(canvas: Canvas) {
        val bounds = bounds
        val centerX = bounds.centerX().toFloat()
        val centerY = bounds.centerY().toFloat()
        val radius = min(bounds.width(), bounds.height()) / 2f * 0.8f

        canvas.save()
        canvas.rotate(rotation, centerX, centerY)

        // Draw arc (incomplete circle for spinner effect)
        canvas.drawArc(
            centerX - radius,
            centerY - radius,
            centerX + radius,
            centerY + radius,
            0f, 270f,
            false, paint
        )

        canvas.restore()
    }

    //  Animatable interface
    override fun start() {
        if (!isRunning) {
            isRunning = true
            animator.start()
            callback?.invalidateDrawable(this)
        }
    }

    override fun stop() {
        if (isRunning) {
            isRunning = false
            animator.cancel()
        }
    }

    override fun isRunning(): Boolean = isRunning

    override fun setAlpha(alpha: Int) {
        paint.alpha = alpha
    }

    override fun setColorFilter(colorFilter: ColorFilter?) {
        paint.colorFilter = colorFilter
    }

    @Deprecated("Deprecated in Java")
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}
```

**Usage:**
```kotlin
val spinner = SpinnerDrawable()
imageView.setImageDrawable(spinner)
spinner.start() // Start animation
```

---

### 5. LayerDrawable - Compose Multiple Drawables

```kotlin
class BadgeDrawable(
    context: Context,
    count: Int
) : LayerDrawable(emptyArray()) {

    private val backgroundDrawable = GradientDrawable().apply {
        shape = GradientDrawable.OVAL
        setColor(Color.RED)
    }

    private val textDrawable = TextDrawable(context, count.toString())

    init {
        addLayer(backgroundDrawable)
        addLayer(textDrawable)

        // Set layer sizes
        setLayerSize(0, 24.dpToPx(), 24.dpToPx())
        setLayerSize(1, 24.dpToPx(), 24.dpToPx())
    }

    private fun Int.dpToPx(): Int =
        (this * context.resources.displayMetrics.density).toInt()
}

class TextDrawable(
    private val context: Context,
    private val text: String
) : Drawable() {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        textAlign = Paint.Align.CENTER
        textSize = 12.spToPx()
        color = Color.WHITE
    }

    override fun draw(canvas: Canvas) {
        val bounds = bounds
        val x = bounds.centerX().toFloat()
        val y = bounds.centerY() - (paint.descent() + paint.ascent()) / 2

        canvas.drawText(text, x, y, paint)
    }

    override fun setAlpha(alpha: Int) {
        paint.alpha = alpha
    }

    override fun setColorFilter(colorFilter: ColorFilter?) {
        paint.colorFilter = colorFilter
    }

    @Deprecated("Deprecated in Java")
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT

    private fun Int.spToPx(): Float =
        this * context.resources.displayMetrics.scaledDensity
}
```

---

### 6. Gradient Drawable

```kotlin
class CustomGradientDrawable : Drawable() {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private var gradientShader: Shader? = null

    var startColor: Int = Color.BLUE
        set(value) {
            field = value
            recreateGradient()
        }

    var endColor: Int = Color.GREEN
        set(value) {
            field = value
            recreateGradient()
        }

    var orientation: Orientation = Orientation.TOP_BOTTOM
        set(value) {
            field = value
            recreateGradient()
        }

    enum class Orientation {
        TOP_BOTTOM, LEFT_RIGHT, DIAGONAL
    }

    override fun draw(canvas: Canvas) {
        val bounds = bounds

        if (gradientShader == null) {
            recreateGradient()
        }

        paint.shader = gradientShader
        canvas.drawRect(bounds, paint)
    }

    override fun onBoundsChange(bounds: Rect) {
        super.onBoundsChange(bounds)
        recreateGradient()
    }

    private fun recreateGradient() {
        val bounds = bounds
        if (bounds.isEmpty) return

        gradientShader = when (orientation) {
            Orientation.TOP_BOTTOM -> LinearGradient(
                bounds.centerX().toFloat(),
                bounds.top.toFloat(),
                bounds.centerX().toFloat(),
                bounds.bottom.toFloat(),
                startColor, endColor,
                Shader.TileMode.CLAMP
            )

            Orientation.LEFT_RIGHT -> LinearGradient(
                bounds.left.toFloat(),
                bounds.centerY().toFloat(),
                bounds.right.toFloat(),
                bounds.centerY().toFloat(),
                startColor, endColor,
                Shader.TileMode.CLAMP
            )

            Orientation.DIAGONAL -> LinearGradient(
                bounds.left.toFloat(),
                bounds.top.toFloat(),
                bounds.right.toFloat(),
                bounds.bottom.toFloat(),
                startColor, endColor,
                Shader.TileMode.CLAMP
            )
        }

        invalidateSelf()
    }

    override fun setAlpha(alpha: Int) {
        paint.alpha = alpha
    }

    override fun setColorFilter(colorFilter: ColorFilter?) {
        paint.colorFilter = colorFilter
    }

    @Deprecated("Deprecated in Java")
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}
```

---

### 7. Shape Drawable with Path

```kotlin
class StarDrawable : Drawable() {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.YELLOW
    }

    private val path = Path()
    private var pathCreated = false

    override fun draw(canvas: Canvas) {
        if (!pathCreated) {
            createStarPath()
            pathCreated = true
        }

        canvas.drawPath(path, paint)
    }

    override fun onBoundsChange(bounds: Rect) {
        super.onBoundsChange(bounds)
        pathCreated = false // Recreate path on size change
    }

    private fun createStarPath() {
        path.reset()

        val bounds = bounds
        val cx = bounds.centerX().toFloat()
        val cy = bounds.centerY().toFloat()
        val outerRadius = min(bounds.width(), bounds.height()) / 2f * 0.9f
        val innerRadius = outerRadius * 0.4f

        // Create 5-point star
        for (i in 0 until 10) {
            val angle = Math.PI / 5 * i - Math.PI / 2
            val radius = if (i % 2 == 0) outerRadius else innerRadius
            val x = cx + (radius * cos(angle)).toFloat()
            val y = cy + (radius * sin(angle)).toFloat()

            if (i == 0) {
                path.moveTo(x, y)
            } else {
                path.lineTo(x, y)
            }
        }

        path.close()
    }

    override fun setAlpha(alpha: Int) {
        paint.alpha = alpha
    }

    override fun setColorFilter(colorFilter: ColorFilter?) {
        paint.colorFilter = colorFilter
    }

    @Deprecated("Deprecated in Java")
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}
```

---

### 8. Using Drawable from XML

**Create drawable XML (res/drawable/custom_background.xml):**
```xml
<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">

    <solid android:color="#3F51B5" />

    <corners android:radius="8dp" />

    <stroke
        android:width="2dp"
        android:color="#FFFFFF" />

    <padding
        android:left="16dp"
        android:top="8dp"
        android:right="16dp"
        android:bottom="8dp" />
</shape>
```

**Use in layout:**
```xml
<TextView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Hello"
    android:background="@drawable/custom_background" />
```

---

### 9. Tinting Drawables

Support tinting for color customization.

```kotlin
class TintableDrawable : Drawable() {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private var tintColor: Int? = null

    override fun draw(canvas: Canvas) {
        paint.color = tintColor ?: Color.BLUE
        canvas.drawCircle(
            bounds.centerX().toFloat(),
            bounds.centerY().toFloat(),
            min(bounds.width(), bounds.height()) / 2f,
            paint
        )
    }

    override fun setTint(tintColor: Int) {
        this.tintColor = tintColor
        invalidateSelf()
    }

    override fun setTintList(tint: ColorStateList?) {
        tintColor = tint?.defaultColor
        invalidateSelf()
    }

    override fun setAlpha(alpha: Int) {
        paint.alpha = alpha
    }

    override fun setColorFilter(colorFilter: ColorFilter?) {
        paint.colorFilter = colorFilter
    }

    @Deprecated("Deprecated in Java")
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}
```

**Usage:**
```kotlin
val drawable = TintableDrawable()
DrawableCompat.setTint(drawable, Color.RED)
imageView.setImageDrawable(drawable)
```

---

### 10. Best Practices

**1. Always use bounds, never hardcode**
```kotlin
//  DO
override fun draw(canvas: Canvas) {
    val bounds = bounds
    canvas.drawRect(bounds, paint)
}

//  DON'T
override fun draw(canvas: Canvas) {
    canvas.drawRect(0f, 0f, 100f, 100f, paint) // Hardcoded!
}
```

**2. Implement required methods**
```kotlin
//  Must implement these 3 methods
override fun setAlpha(alpha: Int)
override fun setColorFilter(colorFilter: ColorFilter?)
override fun getOpacity(): Int
```

**3. Call invalidateSelf() when state changes**
```kotlin
var color: Int = Color.BLUE
    set(value) {
        field = value
        paint.color = value
        invalidateSelf() //  Request redraw
    }
```

**4. Pre-allocate objects**
```kotlin
//  DO - Allocate once
private val paint = Paint()
private val path = Path()

override fun draw(canvas: Canvas) {
    path.reset() // Reuse
    // ...
}

//  DON'T - Allocate in draw()
override fun draw(canvas: Canvas) {
    val paint = Paint() // Allocates every draw!
}
```

**5. Handle bounds changes**
```kotlin
override fun onBoundsChange(bounds: Rect) {
    super.onBoundsChange(bounds)
    // Recreate size-dependent objects
    recreateShader()
    recreatePath()
}
```

**6. Provide intrinsic size (optional)**
```kotlin
override fun getIntrinsicWidth(): Int = 48.dpToPx()
override fun getIntrinsicHeight(): Int = 48.dpToPx()
```

---

### Summary

**Creating custom Drawables:**
1. Extend `Drawable` class
2. Implement `draw(canvas: Canvas)`
3. Implement `setAlpha()`, `setColorFilter()`, `getOpacity()`
4. Use `bounds` for coordinates
5. Call `invalidateSelf()` when state changes

**Key methods:**
- `draw()` - Render drawable
- `onBoundsChange()` - Handle size changes
- `isStateful()` - Support state changes
- `onStateChange()` - Handle state changes
- `invalidateSelf()` - Request redraw

**Drawable vs View:**
- Drawable: Lightweight, reusable graphics
- View: Interactive UI elements with full lifecycle

**Best practices:**
- Always use bounds
- Pre-allocate objects
- Handle bounds changes
- Support tinting
- Provide intrinsic size

---

## Ответ (RU)

**Пользовательские Drawables** - это легковесная, переиспользуемая графика, которая может использоваться в нескольких view. Они более эффективны, чем custom View, когда не нужно взаимодействие с пользователем или сложное управление жизненным циклом.

### Drawable vs Custom View

| Функция | Drawable | Custom View |
|---------|----------|-------------|
| **Случай использования** | Простая графика, иконки | Интерактивные UI элементы |
| **Производительность** | Легковесный | Тяжелее (полный View) |
| **Взаимодействие** | Нет обработки касаний | Полная поддержка касаний |
| **Жизненный цикл** | Простой | Сложный (attach/detach) |
| **Переиспользуемость** | Высокая | Ниже |
| **Состояние** | Ограниченное (ColorStateList) | Полное управление состоянием |

**Используйте Drawable когда**:
- Неинтерактивная графика
- Переиспользование в разных view
- Простые формы/анимации
- Фоновая/передняя графика

**Используйте Custom View когда**:
- Нужно взаимодействие с касаниями
- Сложный жизненный цикл
- Требования доступности
- Координация анимаций

---

### 1. Жизненный цикл Drawable

Drawable имеет упрощенный жизненный цикл по сравнению с View:

1. **Создание** - конструктор вызывается системой или вами
2. **setBounds()** - система устанавливает границы для отрисовки
3. **draw()** - вызывается для отрисовки на Canvas
4. **onBoundsChange()** - вызывается при изменении размера
5. **setState()** - обновление состояния (pressed, focused и т.д.)
6. **onStateChange()** - реакция на изменения состояния
7. **invalidateSelf()** - запрос перерисовки

---

### 2. Базовый Custom Drawable

```kotlin
class CircleDrawable : Drawable() {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }

    var color: Int
        get() = paint.color
        set(value) {
            paint.color = value
            invalidateSelf() // Запросить перерисовку
        }

    //  Основной метод отрисовки
    override fun draw(canvas: Canvas) {
        val bounds = bounds
        val centerX = bounds.centerX().toFloat()
        val centerY = bounds.centerY().toFloat()
        val radius = min(bounds.width(), bounds.height()) / 2f

        canvas.drawCircle(centerX, centerY, radius, paint)
    }

    //  Установить прозрачность (обязательно)
    override fun setAlpha(alpha: Int) {
        paint.alpha = alpha
        invalidateSelf()
    }

    //  Установить цветовой фильтр (обязательно)
    override fun setColorFilter(colorFilter: ColorFilter?) {
        paint.colorFilter = colorFilter
        invalidateSelf()
    }

    //  Вернуть прозрачность (обязательно)
    @Deprecated("Deprecated in Java", ReplaceWith("PixelFormat.TRANSLUCENT"))
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT

    //  Intrinsic size (опционально)
    override fun getIntrinsicWidth(): Int = 48.dpToPx()
    override fun getIntrinsicHeight(): Int = 48.dpToPx()

    private fun Int.dpToPx(): Int =
        (this * Resources.getSystem().displayMetrics.density).toInt()
}
```

**Использование:**
```kotlin
// Установить как фон
view.background = CircleDrawable()

// Установить как источник ImageView
imageView.setImageDrawable(CircleDrawable())

// Установить программно
val circle = CircleDrawable().apply {
    color = Color.RED
    setBounds(0, 0, 100, 100)
}
canvas.draw(circle)
```

---

### 3. Управление границами (Bounds Management)

Drawable должен уважать границы, установленные контейнером.

```kotlin
class RectangleDrawable : Drawable() {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)

    override fun draw(canvas: Canvas) {
        //  Всегда использовать bounds, никогда не hardcode координаты
        val bounds = bounds

        // Рисовать в пределах bounds
        canvas.drawRect(bounds, paint)

        // Или вычислить относительные координаты
        val centerX = bounds.centerX().toFloat()
        val centerY = bounds.centerY().toFloat()
        val width = bounds.width().toFloat()
        val height = bounds.height().toFloat()

        // Рисовать что-то центрированное
        canvas.drawRoundRect(
            centerX - width / 4,
            centerY - height / 4,
            centerX + width / 4,
            centerY + height / 4,
            10f, 10f,
            paint
        )
    }

    //  Реагировать на изменения bounds
    override fun onBoundsChange(bounds: Rect) {
        super.onBoundsChange(bounds)

        // Пересоздать объекты, зависящие от размера
        recreateShader(bounds)
    }

    private fun recreateShader(bounds: Rect) {
        val shader = LinearGradient(
            bounds.left.toFloat(),
            bounds.top.toFloat(),
            bounds.right.toFloat(),
            bounds.bottom.toFloat(),
            Color.BLUE,
            Color.GREEN,
            Shader.TileMode.CLAMP
        )
        paint.shader = shader
    }

    override fun setAlpha(alpha: Int) {
        paint.alpha = alpha
    }

    override fun setColorFilter(colorFilter: ColorFilter?) {
        paint.colorFilter = colorFilter
    }

    @Deprecated("Deprecated in Java")
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}
```

---

### 4. Stateful Drawable (с состояниями)

Реагирует на изменения состояния view (pressed, focused и т.д.).

```kotlin
class StatefulButtonDrawable : Drawable() {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
    }

    private val normalColor = Color.BLUE
    private val pressedColor = Color.DARK_GRAY
    private val disabledColor = Color.LIGHT_GRAY

    init {
        paint.color = normalColor
    }

    override fun draw(canvas: Canvas) {
        val bounds = bounds
        canvas.drawRoundRect(
            bounds.left.toFloat(),
            bounds.top.toFloat(),
            bounds.right.toFloat(),
            bounds.bottom.toFloat(),
            20f, 20f,
            paint
        )
    }

    //  Объявить, какие состояния обрабатывает этот drawable
    override fun isStateful(): Boolean = true

    //  Обработать изменения состояния
    override fun onStateChange(state: IntArray): Boolean {
        val oldColor = paint.color

        paint.color = when {
            state.contains(android.R.attr.state_pressed) -> pressedColor
            state.contains(android.R.attr.state_enabled).not() -> disabledColor
            else -> normalColor
        }

        // Вернуть true, если визуальное представление изменилось (вызывает перерисовку)
        return oldColor != paint.color
    }

    override fun setAlpha(alpha: Int) {
        paint.alpha = alpha
    }

    override fun setColorFilter(colorFilter: ColorFilter?) {
        paint.colorFilter = colorFilter
    }

    @Deprecated("Deprecated in Java")
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}
```

**Использование:**
```kotlin
button.background = StatefulButtonDrawable()
// Автоматически меняет цвет при нажатии!
```

---

### 5. Анимированный Drawable

```kotlin
class SpinnerDrawable : Drawable(), Animatable {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 8f
        color = Color.BLUE
        strokeCap = Paint.Cap.ROUND
    }

    private var rotation = 0f
    private var isRunning = false

    private val animator = ValueAnimator.ofFloat(0f, 360f).apply {
        duration = 1000
        repeatCount = ValueAnimator.INFINITE
        interpolator = LinearInterpolator()
        addUpdateListener { animation ->
            rotation = animation.animatedValue as Float
            invalidateSelf() // Запросить перерисовку
        }
    }

    override fun draw(canvas: Canvas) {
        val bounds = bounds
        val centerX = bounds.centerX().toFloat()
        val centerY = bounds.centerY().toFloat()
        val radius = min(bounds.width(), bounds.height()) / 2f * 0.8f

        canvas.save()
        canvas.rotate(rotation, centerX, centerY)

        // Нарисовать дугу (неполный круг для эффекта спиннера)
        canvas.drawArc(
            centerX - radius,
            centerY - radius,
            centerX + radius,
            centerY + radius,
            0f, 270f,
            false, paint
        )

        canvas.restore()
    }

    //  Интерфейс Animatable
    override fun start() {
        if (!isRunning) {
            isRunning = true
            animator.start()
            callback?.invalidateDrawable(this)
        }
    }

    override fun stop() {
        if (isRunning) {
            isRunning = false
            animator.cancel()
        }
    }

    override fun isRunning(): Boolean = isRunning

    override fun setAlpha(alpha: Int) {
        paint.alpha = alpha
    }

    override fun setColorFilter(colorFilter: ColorFilter?) {
        paint.colorFilter = colorFilter
    }

    @Deprecated("Deprecated in Java")
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}
```

**Использование:**
```kotlin
val spinner = SpinnerDrawable()
imageView.setImageDrawable(spinner)
spinner.start() // Запустить анимацию
```

---

### 6. LayerDrawable - Комбинирование нескольких Drawables

```kotlin
class BadgeDrawable(
    context: Context,
    count: Int
) : LayerDrawable(emptyArray()) {

    private val backgroundDrawable = GradientDrawable().apply {
        shape = GradientDrawable.OVAL
        setColor(Color.RED)
    }

    private val textDrawable = TextDrawable(context, count.toString())

    init {
        addLayer(backgroundDrawable)
        addLayer(textDrawable)

        // Установить размеры слоев
        setLayerSize(0, 24.dpToPx(), 24.dpToPx())
        setLayerSize(1, 24.dpToPx(), 24.dpToPx())
    }

    private fun Int.dpToPx(): Int =
        (this * context.resources.displayMetrics.density).toInt()
}

class TextDrawable(
    private val context: Context,
    private val text: String
) : Drawable() {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        textAlign = Paint.Align.CENTER
        textSize = 12.spToPx()
        color = Color.WHITE
    }

    override fun draw(canvas: Canvas) {
        val bounds = bounds
        val x = bounds.centerX().toFloat()
        val y = bounds.centerY() - (paint.descent() + paint.ascent()) / 2

        canvas.drawText(text, x, y, paint)
    }

    override fun setAlpha(alpha: Int) {
        paint.alpha = alpha
    }

    override fun setColorFilter(colorFilter: ColorFilter?) {
        paint.colorFilter = colorFilter
    }

    @Deprecated("Deprecated in Java")
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT

    private fun Int.spToPx(): Float =
        this * context.resources.displayMetrics.scaledDensity
}
```

---

### 7. Gradient Drawable (Градиентный Drawable)

```kotlin
class CustomGradientDrawable : Drawable() {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private var gradientShader: Shader? = null

    var startColor: Int = Color.BLUE
        set(value) {
            field = value
            recreateGradient()
        }

    var endColor: Int = Color.GREEN
        set(value) {
            field = value
            recreateGradient()
        }

    var orientation: Orientation = Orientation.TOP_BOTTOM
        set(value) {
            field = value
            recreateGradient()
        }

    enum class Orientation {
        TOP_BOTTOM, LEFT_RIGHT, DIAGONAL
    }

    override fun draw(canvas: Canvas) {
        val bounds = bounds

        if (gradientShader == null) {
            recreateGradient()
        }

        paint.shader = gradientShader
        canvas.drawRect(bounds, paint)
    }

    override fun onBoundsChange(bounds: Rect) {
        super.onBoundsChange(bounds)
        recreateGradient()
    }

    private fun recreateGradient() {
        val bounds = bounds
        if (bounds.isEmpty) return

        gradientShader = when (orientation) {
            Orientation.TOP_BOTTOM -> LinearGradient(
                bounds.centerX().toFloat(),
                bounds.top.toFloat(),
                bounds.centerX().toFloat(),
                bounds.bottom.toFloat(),
                startColor, endColor,
                Shader.TileMode.CLAMP
            )

            Orientation.LEFT_RIGHT -> LinearGradient(
                bounds.left.toFloat(),
                bounds.centerY().toFloat(),
                bounds.right.toFloat(),
                bounds.centerY().toFloat(),
                startColor, endColor,
                Shader.TileMode.CLAMP
            )

            Orientation.DIAGONAL -> LinearGradient(
                bounds.left.toFloat(),
                bounds.top.toFloat(),
                bounds.right.toFloat(),
                bounds.bottom.toFloat(),
                startColor, endColor,
                Shader.TileMode.CLAMP
            )
        }

        invalidateSelf()
    }

    override fun setAlpha(alpha: Int) {
        paint.alpha = alpha
    }

    override fun setColorFilter(colorFilter: ColorFilter?) {
        paint.colorFilter = colorFilter
    }

    @Deprecated("Deprecated in Java")
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}
```

---

### 8. Shape Drawable с Path

```kotlin
class StarDrawable : Drawable() {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.YELLOW
    }

    private val path = Path()
    private var pathCreated = false

    override fun draw(canvas: Canvas) {
        if (!pathCreated) {
            createStarPath()
            pathCreated = true
        }

        canvas.drawPath(path, paint)
    }

    override fun onBoundsChange(bounds: Rect) {
        super.onBoundsChange(bounds)
        pathCreated = false // Пересоздать path при изменении размера
    }

    private fun createStarPath() {
        path.reset()

        val bounds = bounds
        val cx = bounds.centerX().toFloat()
        val cy = bounds.centerY().toFloat()
        val outerRadius = min(bounds.width(), bounds.height()) / 2f * 0.9f
        val innerRadius = outerRadius * 0.4f

        // Создать 5-конечную звезду
        for (i in 0 until 10) {
            val angle = Math.PI / 5 * i - Math.PI / 2
            val radius = if (i % 2 == 0) outerRadius else innerRadius
            val x = cx + (radius * cos(angle)).toFloat()
            val y = cy + (radius * sin(angle)).toFloat()

            if (i == 0) {
                path.moveTo(x, y)
            } else {
                path.lineTo(x, y)
            }
        }

        path.close()
    }

    override fun setAlpha(alpha: Int) {
        paint.alpha = alpha
    }

    override fun setColorFilter(colorFilter: ColorFilter?) {
        paint.colorFilter = colorFilter
    }

    @Deprecated("Deprecated in Java")
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}
```

---

### 9. Tinting Drawables (Тонирование)

Поддержка тонирования для кастомизации цвета.

```kotlin
class TintableDrawable : Drawable() {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private var tintColor: Int? = null

    override fun draw(canvas: Canvas) {
        paint.color = tintColor ?: Color.BLUE
        canvas.drawCircle(
            bounds.centerX().toFloat(),
            bounds.centerY().toFloat(),
            min(bounds.width(), bounds.height()) / 2f,
            paint
        )
    }

    override fun setTint(tintColor: Int) {
        this.tintColor = tintColor
        invalidateSelf()
    }

    override fun setTintList(tint: ColorStateList?) {
        tintColor = tint?.defaultColor
        invalidateSelf()
    }

    override fun setAlpha(alpha: Int) {
        paint.alpha = alpha
    }

    override fun setColorFilter(colorFilter: ColorFilter?) {
        paint.colorFilter = colorFilter
    }

    @Deprecated("Deprecated in Java")
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}
```

**Использование:**
```kotlin
val drawable = TintableDrawable()
DrawableCompat.setTint(drawable, Color.RED)
imageView.setImageDrawable(drawable)
```

---

### 10. Лучшие практики

**1. Всегда использовать bounds, никогда не hardcode**
```kotlin
//  ПРАВИЛЬНО
override fun draw(canvas: Canvas) {
    val bounds = bounds
    canvas.drawRect(bounds, paint)
}

//  НЕПРАВИЛЬНО
override fun draw(canvas: Canvas) {
    canvas.drawRect(0f, 0f, 100f, 100f, paint) // Hardcoded!
}
```

**2. Реализовать обязательные методы**
```kotlin
//  Должны реализовать эти 3 метода
override fun setAlpha(alpha: Int)
override fun setColorFilter(colorFilter: ColorFilter?)
override fun getOpacity(): Int
```

**3. Вызывать invalidateSelf() при изменении состояния**
```kotlin
var color: Int = Color.BLUE
    set(value) {
        field = value
        paint.color = value
        invalidateSelf() //  Запросить перерисовку
    }
```

**4. Предварительно выделять объекты**
```kotlin
//  ПРАВИЛЬНО - Выделить один раз
private val paint = Paint()
private val path = Path()

override fun draw(canvas: Canvas) {
    path.reset() // Переиспользовать
    // ...
}

//  НЕПРАВИЛЬНО - Выделение в draw()
override fun draw(canvas: Canvas) {
    val paint = Paint() // Выделяется при каждой отрисовке!
}
```

**5. Обрабатывать изменения bounds**
```kotlin
override fun onBoundsChange(bounds: Rect) {
    super.onBoundsChange(bounds)
    // Пересоздать объекты, зависящие от размера
    recreateShader()
    recreatePath()
}
```

**6. Предоставлять intrinsic size (опционально)**
```kotlin
override fun getIntrinsicWidth(): Int = 48.dpToPx()
override fun getIntrinsicHeight(): Int = 48.dpToPx()
```

---

### Резюме

**Создание пользовательских Drawables:**
1. Наследовать класс `Drawable`
2. Реализовать `draw(canvas: Canvas)`
3. Реализовать `setAlpha()`, `setColorFilter()`, `getOpacity()`
4. Использовать `bounds` для координат
5. Вызывать `invalidateSelf()` при изменении состояния

**Ключевые методы:**
- `draw()` - Отрисовать drawable
- `onBoundsChange()` - Обработать изменения размера
- `isStateful()` - Поддержка изменений состояния
- `onStateChange()` - Обработать изменения состояния
- `invalidateSelf()` - Запросить перерисовку

**Drawable vs View:**
- Drawable: легковесная, переиспользуемая графика
- View: интерактивные UI элементы с полным жизненным циклом

**Лучшие практики:**
- Всегда использовать bounds
- Предварительно выделять объекты
- Обрабатывать изменения bounds
- Поддерживать tinting
- Предоставлять intrinsic size
- Оптимизировать производительность - избегать лишних вычислений в draw()
- Использовать callback для уведомления об изменениях
- Переопределять isStateful() для stateful drawables

---

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - View
- [[q-viewmodel-pattern--android--easy]] - View

### Related (Medium)
- [[q-testing-viewmodels-turbine--testing--medium]] - View
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - View
- [[q-rxjava-pagination-recyclerview--android--medium]] - View
- [[q-what-is-viewmodel--android--medium]] - View
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - View

### Advanced (Harder)
- [[q-compose-custom-layout--jetpack-compose--hard]] - View
