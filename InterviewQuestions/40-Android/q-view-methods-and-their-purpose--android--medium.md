---
id: android-303
title: View Methods And Their Purpose / Методы View и их назначение
aliases:
- View Methods
- Методы View
topic: android
subtopics:
- ui-views
question_kind: theory
difficulty: medium
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android-view-system-basics
- q-viewgroup-vs-view-differences--android--easy
- q-what-methods-redraw-views--android--medium
created: 2025-10-15
updated: 2025-11-10
tags:
- android/ui-views
- difficulty/medium
- drawing
- rendering
- view

---

# Вопрос (RU)
> Методы `View` и их назначение

# Question (EN)
> `View` Methods And Their Purpose

---

## Ответ (RU)

Класс **`View`** в Android предоставляет множество методов для управления внешним видом, поведением и аспектами жизненного цикла элементов UI. Понимание этих методов критически важно для разработки пользовательских `View` и `ViewGroup` и оптимизации интерфейса. См. также [[c-android-view-system-basics]].

### Методы Измерения И Макетирования

#### onMeasure()

Определяет требования к размеру для самой `View`. Для `ViewGroup` именно переопределение `onMeasure()` используется для измерения дочерних элементов (через `measureChild*` / `measureChildren()`), а не происходит "автоматического" измерения.

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    // Вычислить желаемые размеры для этой View
    val desiredWidth = suggestedMinimumWidth + paddingLeft + paddingRight
    val desiredHeight = suggestedMinimumHeight + paddingTop + paddingBottom

    // Определить размер на основе ограничений
    val width = resolveSize(desiredWidth, widthMeasureSpec)
    val height = resolveSize(desiredHeight, heightMeasureSpec)

    // Установить измеренные размеры
    setMeasuredDimension(width, height)
}
```

#### onLayout()

Позиционирует дочерние `View` внутри `ViewGroup`. Обычные `View` обычно не переопределяют этот метод.

```kotlin
// Пример для пользовательского ViewGroup
override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
    // Позиционировать дочерние представления
    for (i in 0 until childCount) {
        val child = getChildAt(i)
        child.layout(0, 0, child.measuredWidth, child.measuredHeight)
    }
}
```

### Методы Рисования

#### onDraw()

Отрисовывает визуальное содержимое `View` на холсте.

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

Запрашивает перерисовку `View` в UI-потоке, помечая её как требующую перерисовки и приводя к последующему вызову `onDraw()`.

```kotlin
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    var progress: Int = 0
        set(value) {
            field = value
            invalidate() // Вызывает перерисовку через onDraw()
        }
}
```

#### postInvalidate()

Запрашивает перерисовку из фонового потока, постя `invalidate`-вызов в UI-поток.

```kotlin
Thread {
    // Фоновая работа
    progress = 50

    // Безопасно запросить перерисовку из фонового потока
    postInvalidate()
}.start()
```

### Методы Размера И Позиции

#### getWidth() И getHeight()

Возвращают текущие размеры `View` (после layout).

```kotlin
val width = view.width
val height = view.height

// Примечание: до завершения layout могут вернуть 0.
// Используйте post{} чтобы убедиться, что размеры доступны.
view.post {
    val actualWidth = view.width
    val actualHeight = view.height
}
```

#### getMeasuredWidth() И getMeasuredHeight()

Возвращают размеры, определённые на этапе измерения в `onMeasure()`.

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    super.onMeasure(widthMeasureSpec, heightMeasureSpec)

    val measuredW = measuredWidth
    val measuredH = measuredHeight
}
```

### Методы Видимости

#### setVisibility()

Управляет состоянием видимости `View`.

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

Проверяет, видимы ли `View` и все её предки и присоединены ли они к окну.

```kotlin
if (view.isShown) {
    // View считается видимой с учётом собственной видимости, предков и присоединения к окну
}
```

### Фон И Внешний Вид

#### setBackgroundColor()

Устанавливает цвет фона `View`.

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

Устанавливает прозрачность `View` (0.0f = полностью прозрачный, 1.0f = полностью непрозрачный).

```kotlin
view.alpha = 0.5f // 50% прозрачность
```

### Методы Взаимодействия

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
    true // Вернуть true, если событие обработано и не должно передаваться дальше
}
```

#### setOnTouchListener()

Устанавливает обработчик события касания.

```kotlin
view.setOnTouchListener { v, event ->
    when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            // Касание началось
            false // вернуть true, если полностью перехватываете событие и не хотите стандартных onClick/onLongClick
        }
        MotionEvent.ACTION_MOVE -> {
            // Касание переместилось
            false
        }
        MotionEvent.ACTION_UP -> {
            // Касание завершилось
            false
        }
        else -> false
    }
}
```

### Методы Фокуса

#### requestFocus()

Запрашивает фокус клавиатуры для `View`.

```kotlin
editText.requestFocus()

// Показать клавиатуру
val imm = getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager
imm.showSoftInput(editText, InputMethodManager.SHOW_IMPLICIT)
```

#### clearFocus()

Удаляет фокус с `View`.

```kotlin
editText.clearFocus()
```

### Методы Анимации

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

Устанавливает смещение `View` в 3D-пространстве.

```kotlin
view.translationX = 100f
view.translationY = 200f
view.translationZ = 10f
```

#### setRotation/RotationX/RotationY()

Устанавливает поворот `View`.

```kotlin
view.rotation = 45f // Повернуть на 45 градусов
view.rotationX = 30f // Повернуть вокруг оси X
view.rotationY = 30f // Повернуть вокруг оси Y
```

#### setScaleX/ScaleY()

Устанавливает масштаб `View`.

```kotlin
view.scaleX = 1.5f // Масштаб до 150% по горизонтали
view.scaleY = 1.5f // Масштаб до 150% по вертикали
```

### Управление Состоянием

#### setEnabled()

Включает или отключает `View`.

```kotlin
button.isEnabled = false // Отключить
button.isEnabled = true  // Включить
```

#### setClickable()

Управляет тем, реагирует ли `View` на клики.

```kotlin
view.isClickable = true
view.isLongClickable = true
```

#### setSelected()

Устанавливает состояние выбора `View`.

```kotlin
view.isSelected = true
```

#### setPressed()

Устанавливает состояние нажатия `View`.

```kotlin
view.isPressed = true
```

### Отступы И Поля

#### setPadding()

Устанавливает внутренние отступы.

```kotlin
view.setPadding(16, 16, 16, 16) // left, top, right, bottom

// Относительные отступы
view.setPaddingRelative(16, 16, 16, 16) // start, top, end, bottom
```

#### setLayoutParams()

Устанавливает параметры макета, включая поля (если используется `MarginLayoutParams`).

```kotlin
val params = view.layoutParams as? ViewGroup.MarginLayoutParams
params?.setMargins(16, 16, 16, 16)
view.layoutParams = params
```

### Методы Тегов

#### setTag() / getTag()

Сохраняют произвольные данные, связанные с `View`.

```kotlin
view.tag = userData
val userData = view.tag as? UserData

// С ключом
view.setTag(R.id.user_data, userData)
val data = view.getTag(R.id.user_data) as? UserData
```

### Методы Жизненного Цикла

#### onAttachedToWindow()

Вызывается, когда `View` присоединена к окну.

```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()
    // Запустить анимации или зарегистрировать слушателей
}
```

#### onDetachedFromWindow()

Вызывается, когда `View` отсоединена от окна.

```kotlin
override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()
    // Остановить анимации, отменить регистрацию слушателей
}
```

### Резюме Ключевых Методов

- onMeasure() — определить требования к размеру (и в `ViewGroup` — измерить детей).
- onLayout() — позиционировать дочерние представления в `ViewGroup`.
- onDraw() — нарисовать визуальное содержимое.
- invalidate() — запросить перерисовку.
- getWidth/Height() — получить текущие размеры.
- setVisibility() — управлять видимостью.
- setOnClickListener() — обрабатывать клики.
- setBackgroundColor() — установить цвет фона.
- animate() — создать анимации.
- requestFocus() — запросить фокус клавиатуры.

## Answer (EN)
The Android **`View`** class provides numerous methods for controlling appearance, behavior, and lifecycle-related aspects of UI elements. Understanding these methods is crucial for custom view and `ViewGroup` development and UI optimization. See also [[c-android-view-system-basics]].

### Measurement and Layout Methods

#### onMeasure()

Determines the size requirements for the `View` itself. For a `ViewGroup`, overriding `onMeasure()` is where you measure child views explicitly (via `measureChild*` / `measureChildren()`); there is no implicit automatic measuring logic without doing this.

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    // Calculate desired dimensions for this View
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

Positions child Views within a `ViewGroup`. Regular leaf `View`s typically do not override this method.

```kotlin
// Example for a custom ViewGroup
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

Renders the `View`'s visual content on the canvas.

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

Requests a redraw of the `View` on the UI thread by marking it as needing to be redrawn; this leads to a later `onDraw()` call.

```kotlin
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    var progress: Int = 0
        set(value) {
            field = value
            invalidate() // Triggers a redraw via onDraw()
        }
}
```

#### postInvalidate()

Requests a redraw from a non-UI thread by posting an invalidate to be executed on the UI thread.

```kotlin
Thread {
    // Background work
    progress = 50

    // Request redraw safely from a background thread
    postInvalidate()
}.start()
```

### Size and Position Methods

#### getWidth() And getHeight()

Return the `View`'s current dimensions (after layout).

```kotlin
val width = view.width
val height = view.height

// Note: May return 0 before layout is complete.
// Use post{} to ensure dimensions are available.
view.post {
    val actualWidth = view.width
    val actualHeight = view.height
}
```

#### getMeasuredWidth() And getMeasuredHeight()

Return the size determined during the measurement pass by `onMeasure()`.

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    super.onMeasure(widthMeasureSpec, heightMeasureSpec)

    val measuredW = measuredWidth
    val measuredH = measuredHeight
}
```

### Visibility Methods

#### setVisibility()

Controls `View` visibility state.

```kotlin
// Make view invisible but keep its space
view.visibility = View.INVISIBLE

// Hide view and remove it from layout
view.visibility = View.GONE

// Show view
view.visibility = View.VISIBLE

// Toggle visibility
view.visibility = if (view.visibility == View.VISIBLE) View.GONE else View.VISIBLE
```

#### isShown()

Checks whether the `View` and all its ancestors are visible and attached to a window.

```kotlin
if (view.isShown) {
    // View is visible considering its own visibility, its ancestors, and window attachment
}
```

### Background and Appearance

#### setBackgroundColor()

Sets the `View`'s background color.

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

Sets `View` transparency (0.0f = fully transparent, 1.0f = fully opaque).

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

Sets a long-press listener.

```kotlin
view.setOnLongClickListener {
    // Handle long click
    true // Return true if consumed and should not propagate further
}
```

#### setOnTouchListener()

Sets a touch event listener.

```kotlin
view.setOnTouchListener { v, event ->
    when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            // Touch started
            false // return true only if you fully handle and consume the event
        }
        MotionEvent.ACTION_MOVE -> {
            // Touch moved
            false
        }
        MotionEvent.ACTION_UP -> {
            // Touch ended
            false
        }
        else -> false
    }
}
```

### Focus Methods

#### requestFocus()

Requests keyboard focus for the `View`.

```kotlin
editText.requestFocus()

// Show keyboard
val imm = getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager
imm.showSoftInput(editText, InputMethodManager.SHOW_IMPLICIT)
```

#### clearFocus()

Removes focus from the `View`.

```kotlin
editText.clearFocus()
```

### Animation Methods

#### animate()

Returns a ViewPropertyAnimator for animating properties.

```kotlin
view.animate()
    .alpha(0f)
    .translationY(100f)
    .scaleX(1.5f)
    .setDuration(500)
    .start()
```

#### setTranslationX/Y/Z()

Sets `View` translation in 3D space.

```kotlin
view.translationX = 100f
view.translationY = 200f
view.translationZ = 10f
```

#### setRotation/RotationX/RotationY()

Sets `View` rotation.

```kotlin
view.rotation = 45f // Rotate 45 degrees
view.rotationX = 30f // Rotate around X-axis
view.rotationY = 30f // Rotate around Y-axis
```

#### setScaleX/ScaleY()

Sets `View` scale.

```kotlin
view.scaleX = 1.5f // Scale to 150% horizontally
view.scaleY = 1.5f // Scale to 150% vertically
```

### State Management

#### setEnabled()

Enables or disables the `View`.

```kotlin
button.isEnabled = false // Disable
button.isEnabled = true  // Enable
```

#### setClickable()

Controls whether the `View` responds to clicks.

```kotlin
view.isClickable = true
view.isLongClickable = true
```

#### setSelected()

Sets the `View`'s selected state.

```kotlin
view.isSelected = true
```

#### setPressed()

Sets the `View`'s pressed state.

```kotlin
view.isPressed = true
```

### Padding and Margins

#### setPadding()

Sets internal padding.

```kotlin
view.setPadding(16, 16, 16, 16) // left, top, right, bottom

// Relative padding
view.setPaddingRelative(16, 16, 16, 16) // start, top, end, bottom
```

#### setLayoutParams()

Sets layout parameters, including margins (when using `MarginLayoutParams`).

```kotlin
val params = view.layoutParams as? ViewGroup.MarginLayoutParams
params?.setMargins(16, 16, 16, 16)
view.layoutParams = params
```

### Tag Methods

#### setTag() / getTag()

Store arbitrary data with the `View`.

```kotlin
view.tag = userData
val userData = view.tag as? UserData

// With key
view.setTag(R.id.user_data, userData)
val data = view.getTag(R.id.user_data) as? UserData
```

### Lifecycle Methods

#### onAttachedToWindow()

Called when the `View` is attached to a window.

```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()
    // Start animations or register listeners
}
```

#### onDetachedFromWindow()

Called when the `View` is detached from a window.

```kotlin
override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()
    // Stop animations, unregister listeners
}
```

### Summary of Key Methods

- onMeasure() — determine size requirements (and in a `ViewGroup` — measure children).
- onLayout() — position child views in `ViewGroup`.
- onDraw() — draw visual content.
- invalidate() — request redraw.
- getWidth/Height() — get current dimensions.
- setVisibility() — control visibility.
- setOnClickListener() — handle clicks.
- setBackgroundColor() — set background color.
- animate() — create animations.
- requestFocus() — request keyboard focus.

---

## Follow-ups

- [[q-viewgroup-vs-view-differences--android--easy]]
- [[q-what-methods-redraw-views--android--medium]]
- [[q-activity-lifecycle-methods--android--medium]]

## References

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)
- [Lifecycle](https://developer.android.com/topic/libraries/architecture/lifecycle)

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - `View`
- [[q-viewmodel-pattern--android--easy]] - `View`

### Related (Medium)
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - `View`
- [[q-testing-viewmodels-turbine--android--medium]] - `View`
- [[q-what-is-viewmodel--android--medium]] - `View`
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - `View`

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]] - `View`
