---
id: "20251015082237471"
title: "View Methods And Their Purpose"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [android/ui, android/view, ui, ui components, view, view lifecycle, difficulty/medium]
---
# Какие методы есть у view и что каждый из них делает?

**English**: What methods does View have and what does each do?

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

Класс **View** в Android предоставляет множество методов для управления внешним видом, поведением и жизненным циклом. Понимание этих методов критически важно для разработки пользовательских представлений и оптимизации UI.

### Методы измерения и макетирования

#### onMeasure()

Определяет требования к размеру для View и его дочерних элементов.

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    // Вычислить желаемые размеры
    val desiredWidth = suggestedMinimumWidth + paddingLeft + paddingRight
    val desiredHeight = suggestedMinimumHeight + paddingTop + paddingBottom

    // Разрешить размер на основе ограничений
    val width = resolveSize(desiredWidth, widthMeasureSpec)
    val height = resolveSize(desiredHeight, heightMeasureSpec)

    // Установить измеренные размеры
    setMeasuredDimension(width, height)
}
```

#### onLayout()

Позиционирует View и его дочерние элементы внутри родительского контейнера.

```kotlin
override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
    // Позиционировать дочерние представления
    for (i in 0 until childCount) {
        val child = getChildAt(i)
        child.layout(0, 0, child.measuredWidth, child.measuredHeight)
    }
}
```

### Методы рисования

#### onDraw()

Отрисовывает визуальное содержимое View на холсте.

```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // Нарисовать пользовательское содержимое
    val paint = Paint().apply {
        color = Color.BLUE
        style = Paint.Style.FILL
    }

    canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), paint)
}
```

#### invalidate()

Запрашивает перерисовку View в UI потоке.

```kotlin
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    var progress: Int = 0
        set(value) {
            field = value
            invalidate() // Вызывает onDraw()
        }
}
```

#### postInvalidate()

Запрашивает перерисовку из фонового потока.

```kotlin
Thread {
    // Фоновая работа
    progress = 50

    // Запросить перерисовку из фонового потока
    postInvalidate()
}.start()
```

### Методы размера и позиции

#### getWidth() и getHeight()

Возвращает текущие размеры View.

```kotlin
val width = view.width
val height = view.height

// Примечание: возвращает 0 до завершения layout
// Используйте post{} чтобы убедиться, что размеры доступны
view.post {
    val actualWidth = view.width
    val actualHeight = view.height
}
```

#### getMeasuredWidth() и getMeasuredHeight()

Возвращает размер, определенный в `onMeasure()`.

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    super.onMeasure(widthMeasureSpec, heightMeasureSpec)

    val measuredW = measuredWidth
    val measuredH = measuredHeight
}
```

### Методы видимости

#### setVisibility()

Управляет состоянием видимости View.

```kotlin
// Сделать представление невидимым, но сохранить его пространство
view.visibility = View.INVISIBLE

// Скрыть представление и удалить из макета
view.visibility = View.GONE

// Показать представление
view.visibility = View.VISIBLE

// Переключить видимость
view.visibility = if (view.visibility == View.VISIBLE) View.GONE else View.VISIBLE
```

#### isShown()

Проверяет, видимы ли View и все его предки.

```kotlin
if (view.isShown) {
    // View фактически видим на экране
}
```

### Фон и внешний вид

#### setBackgroundColor()

Устанавливает цвет фона View.

```kotlin
view.setBackgroundColor(Color.RED)
view.setBackgroundColor(ContextCompat.getColor(context, R.color.primary))

// С альфа-каналом
view.setBackgroundColor(Color.argb(128, 255, 0, 0))
```

#### setBackground()

Устанавливает drawable в качестве фона.

```kotlin
view.background = ContextCompat.getDrawable(context, R.drawable.background)

// Удалить фон
view.background = null
```

#### setAlpha()

Устанавливает прозрачность View (0.0f = прозрачный, 1.0f = непрозрачный).

```kotlin
view.alpha = 0.5f // 50% прозрачность
```

### Методы взаимодействия

#### setOnClickListener()

Устанавливает обработчик события клика.

```kotlin
view.setOnClickListener {
    // Обработать клик
    Toast.makeText(context, "Clicked!", Toast.LENGTH_SHORT).show()
}

// Удалить обработчик
view.setOnClickListener(null)
```

#### setOnLongClickListener()

Устанавливает обработчик длительного нажатия.

```kotlin
view.setOnLongClickListener {
    // Обработать длительное нажатие
    true // Вернуть true если обработано
}
```

#### setOnTouchListener()

Устанавливает обработчик события касания.

```kotlin
view.setOnTouchListener { v, event ->
    when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            // Касание началось
            true
        }
        MotionEvent.ACTION_MOVE -> {
            // Касание переместилось
            true
        }
        MotionEvent.ACTION_UP -> {
            // Касание завершилось
            true
        }
        else -> false
    }
}
```

### Методы фокуса

#### requestFocus()

Запрашивает фокус клавиатуры для View.

```kotlin
editText.requestFocus()

// Показать клавиатуру
val imm = getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager
imm.showSoftInput(editText, InputMethodManager.SHOW_IMPLICIT)
```

#### clearFocus()

Удаляет фокус с View.

```kotlin
editText.clearFocus()
```

### Методы анимации

#### animate()

Возвращает ViewPropertyAnimator для анимации свойств.

```kotlin
view.animate()
    .alpha(0f)
    .translationY(100f)
    .scaleX(1.5f)
    .setDuration(500)
    .start()
```

#### setTranslationX/Y/Z()

Устанавливает смещение View в 3D пространстве.

```kotlin
view.translationX = 100f
view.translationY = 200f
view.translationZ = 10f
```

#### setRotation/RotationX/RotationY()

Устанавливает поворот View.

```kotlin
view.rotation = 45f // Повернуть на 45 градусов
view.rotationX = 30f // Повернуть вокруг оси X
view.rotationY = 30f // Повернуть вокруг оси Y
```

#### setScaleX/ScaleY()

Устанавливает масштаб View.

```kotlin
view.scaleX = 1.5f // Масштаб до 150% по горизонтали
view.scaleY = 1.5f // Масштаб до 150% по вертикали
```

### Управление состоянием

#### setEnabled()

Включает или отключает View.

```kotlin
button.isEnabled = false // Отключить
button.isEnabled = true  // Включить
```

#### setClickable()

Управляет реагированием View на клики.

```kotlin
view.isClickable = true
view.isLongClickable = true
```

#### setSelected()

Устанавливает состояние выбора View.

```kotlin
view.isSelected = true
```

#### setPressed()

Устанавливает состояние нажатия View.

```kotlin
view.isPressed = true
```

### Отступы и поля

#### setPadding()

Устанавливает внутренние отступы.

```kotlin
view.setPadding(16, 16, 16, 16) // left, top, right, bottom

// Отдельные стороны
view.setPaddingRelative(16, 16, 16, 16) // start, top, end, bottom
```

#### setLayoutParams()

Устанавливает параметры макета, включая поля.

```kotlin
val params = view.layoutParams as ViewGroup.MarginLayoutParams
params.setMargins(16, 16, 16, 16)
view.layoutParams = params
```

### Методы тегов

#### setTag() / getTag()

Сохраняет произвольные данные с View.

```kotlin
view.tag = userData
val userData = view.tag as? UserData

// С ключом
view.setTag(R.id.user_data, userData)
val data = view.getTag(R.id.user_data) as? UserData
```

### Методы жизненного цикла

#### onAttachedToWindow()

Вызывается когда View присоединен к окну.

```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()
    // Запустить анимации или зарегистрировать слушателей
}
```

#### onDetachedFromWindow()

Вызывается когда View отсоединен от окна.

```kotlin
override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()
    // Остановить анимации, отменить регистрацию слушателей
}
```

### Резюме ключевых методов

| Метод | Назначение |
|--------|---------|
| onMeasure() | Определить требования к размеру |
| onLayout() | Позиционировать дочерние представления |
| onDraw() | Нарисовать визуальное содержимое |
| invalidate() | Запросить перерисовку |
| getWidth/Height() | Получить текущие размеры |
| setVisibility() | Управлять видимостью |
| setOnClickListener() | Обрабатывать клики |
| setBackgroundColor() | Установить цвет фона |
| animate() | Создать анимации |
| requestFocus() | Запросить фокус клавиатуры |


---

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - View
- [[q-viewmodel-pattern--android--easy]] - View

### Related (Medium)
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - View
- [[q-testing-viewmodels-turbine--testing--medium]] - View
- [[q-rxjava-pagination-recyclerview--android--medium]] - View
- [[q-what-is-viewmodel--android--medium]] - View
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - View

### Advanced (Harder)
- [[q-compose-custom-layout--jetpack-compose--hard]] - View
