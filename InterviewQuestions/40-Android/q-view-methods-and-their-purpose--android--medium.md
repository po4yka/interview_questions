---
id: 202510031411
title: What methods does View have and what does each do / Какие методы есть у view и что каждый из них делает
aliases: []

# Classification
topic: android
subtopics: [android, ui, view]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/550
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-android
related:
  - c-android-view
  - c-android-view-lifecycle

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [view lifecycle, ui components, difficulty/medium, easy_kotlin, lang/ru, android/view, android/ui]
---

# Question (EN)
> What methods does View have and what does each do

# Вопрос (RU)
> Какие методы есть у view и что каждый из них делает

---

## Answer (EN)

The Android **View** class provides numerous methods for controlling appearance, behavior, and lifecycle. Understanding these methods is crucial for custom view development and UI optimization.

### Measurement and Layout Methods

#### onMeasure()

Determines the size requirements for the View and its children.

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    // Calculate desired dimensions
    val desiredWidth = suggestedMinimumWidth + paddingLeft + paddingRight
    val desiredHeight = suggestedMinimumHeight + paddingTop + paddingBottom

    // Resolve size based on constraints
    val width = resolveSize(desiredWidth, widthMeasureSpec)
    val height = resolveSize(desiredHeight, heightMeasureSpec)

    // Set measured dimensions
    setMeasuredDimension(width, height)
}
```

#### onLayout()

Positions the View and its children within the parent container.

```kotlin
override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
    // Position child views
    for (i in 0 until childCount) {
        val child = getChildAt(i)
        child.layout(0, 0, child.measuredWidth, child.measuredHeight)
    }
}
```

### Drawing Methods

#### onDraw()

Renders the View's visual content on the canvas.

```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // Draw custom content
    val paint = Paint().apply {
        color = Color.BLUE
        style = Paint.Style.FILL
    }

    canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), paint)
}
```

#### invalidate()

Requests a redraw of the View on the UI thread.

```kotlin
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    var progress: Int = 0
        set(value) {
            field = value
            invalidate() // Triggers onDraw()
        }
}
```

#### postInvalidate()

Requests a redraw from a non-UI thread.

```kotlin
Thread {
    // Background work
    progress = 50

    // Request redraw from background thread
    postInvalidate()
}.start()
```

### Size and Position Methods

#### getWidth() and getHeight()

Returns the View's current dimensions.

```kotlin
val width = view.width
val height = view.height

// Note: Returns 0 before layout is complete
// Use post{} to ensure dimensions are available
view.post {
    val actualWidth = view.width
    val actualHeight = view.height
}
```

#### getMeasuredWidth() and getMeasuredHeight()

Returns the size determined by `onMeasure()`.

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    super.onMeasure(widthMeasureSpec, heightMeasureSpec)

    val measuredW = measuredWidth
    val measuredH = measuredHeight
}
```

### Visibility Methods

#### setVisibility()

Controls View visibility state.

```kotlin
// Make view invisible but keep its space
view.visibility = View.INVISIBLE

// Hide view and remove from layout
view.visibility = View.GONE

// Show view
view.visibility = View.VISIBLE

// Toggle visibility
view.visibility = if (view.visibility == View.VISIBLE) View.GONE else View.VISIBLE
```

#### isShown()

Checks if the View and all ancestors are visible.

```kotlin
if (view.isShown) {
    // View is actually visible on screen
}
```

### Background and Appearance

#### setBackgroundColor()

Sets the View's background color.

```kotlin
view.setBackgroundColor(Color.RED)
view.setBackgroundColor(ContextCompat.getColor(context, R.color.primary))

// With alpha
view.setBackgroundColor(Color.argb(128, 255, 0, 0))
```

#### setBackground()

Sets a drawable background.

```kotlin
view.background = ContextCompat.getDrawable(context, R.drawable.background)

// Remove background
view.background = null
```

#### setAlpha()

Sets View transparency (0.0f = transparent, 1.0f = opaque).

```kotlin
view.alpha = 0.5f // 50% transparent
```

### Interaction Methods

#### setOnClickListener()

Sets a click event listener.

```kotlin
view.setOnClickListener {
    // Handle click
    Toast.makeText(context, "Clicked!", Toast.LENGTH_SHORT).show()
}

// Remove listener
view.setOnClickListener(null)
```

#### setOnLongClickListener()

Sets a long press listener.

```kotlin
view.setOnLongClickListener {
    // Handle long click
    true // Return true if consumed
}
```

#### setOnTouchListener()

Sets a touch event listener.

```kotlin
view.setOnTouchListener { v, event ->
    when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            // Touch started
            true
        }
        MotionEvent.ACTION_MOVE -> {
            // Touch moved
            true
        }
        MotionEvent.ACTION_UP -> {
            // Touch ended
            true
        }
        else -> false
    }
}
```

### Focus Methods

#### requestFocus()

Requests keyboard focus for the View.

```kotlin
editText.requestFocus()

// Show keyboard
val imm = getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager
imm.showSoftInput(editText, InputMethodManager.SHOW_IMPLICIT)
```

#### clearFocus()

Removes focus from the View.

```kotlin
editText.clearFocus()
```

### Animation Methods

#### animate()

Returns ViewPropertyAnimator for animating properties.

```kotlin
view.animate()
    .alpha(0f)
    .translationY(100f)
    .scaleX(1.5f)
    .setDuration(500)
    .start()
```

#### setTranslationX/Y/Z()

Sets View translation in 3D space.

```kotlin
view.translationX = 100f
view.translationY = 200f
view.translationZ = 10f
```

#### setRotation/RotationX/RotationY()

Sets View rotation.

```kotlin
view.rotation = 45f // Rotate 45 degrees
view.rotationX = 30f // Rotate around X-axis
view.rotationY = 30f // Rotate around Y-axis
```

#### setScaleX/ScaleY()

Sets View scale.

```kotlin
view.scaleX = 1.5f // Scale to 150% horizontally
view.scaleY = 1.5f // Scale to 150% vertically
```

### State Management

#### setEnabled()

Enables or disables the View.

```kotlin
button.isEnabled = false // Disable
button.isEnabled = true  // Enable
```

#### setClickable()

Controls whether the View responds to clicks.

```kotlin
view.isClickable = true
view.isLongClickable = true
```

#### setSelected()

Sets the View's selected state.

```kotlin
view.isSelected = true
```

#### setPressed()

Sets the View's pressed state.

```kotlin
view.isPressed = true
```

### Padding and Margins

#### setPadding()

Sets internal padding.

```kotlin
view.setPadding(16, 16, 16, 16) // left, top, right, bottom

// Individual sides
view.setPaddingRelative(16, 16, 16, 16) // start, top, end, bottom
```

#### setLayoutParams()

Sets layout parameters including margins.

```kotlin
val params = view.layoutParams as ViewGroup.MarginLayoutParams
params.setMargins(16, 16, 16, 16)
view.layoutParams = params
```

### Tag Methods

#### setTag() / getTag()

Stores arbitrary data with the View.

```kotlin
view.tag = userData
val userData = view.tag as? UserData

// With key
view.setTag(R.id.user_data, userData)
val data = view.getTag(R.id.user_data) as? UserData
```

### Lifecycle Methods

#### onAttachedToWindow()

Called when View is attached to a window.

```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()
    // Start animations or register listeners
}
```

#### onDetachedFromWindow()

Called when View is detached from window.

```kotlin
override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()
    // Stop animations, unregister listeners
}
```

### Summary of Key Methods

| Method | Purpose |
|--------|---------|
| onMeasure() | Determine size requirements |
| onLayout() | Position child views |
| onDraw() | Draw visual content |
| invalidate() | Request redraw |
| getWidth/Height() | Get current dimensions |
| setVisibility() | Control visibility |
| setOnClickListener() | Handle clicks |
| setBackgroundColor() | Set background color |
| animate() | Create animations |
| requestFocus() | Request keyboard focus |

## Ответ (RU)

onMeasure - определяет размер View. onLayout - отвечает за позиционирование View внутри родительского контейнера. onDraw - отвечает за рисование View. invalidate - используется для перерисовывания View. setOnClickListener - устанавливает слушатель нажатия. setVisibility - управляет видимостью View. getWidth и getHeight - возвращают размеры View. setBackgroundColor - устанавливает цвет фона.

---

## Follow-ups
- What's the difference between invalidate() and requestLayout()?
- How do you optimize onDraw() for better performance?
- When should you override onMeasure() vs using layout parameters?

## References
- [[c-android-view]]
- [[c-android-view-lifecycle]]
- [[c-android-custom-views]]
- [[c-android-canvas]]
- [[moc-android]]

## Related Questions
- [[q-how-to-create-animations-in-android--android--medium]]
- [[q-how-to-start-drawing-ui-in-android--android--easy]]
- [[q-what-is-layout-types-and-when-to-use--android--easy]]
