---
id: 20251012-122711162
title: "View Lifecycle in Android / Жизненный цикл View в Android"
aliases: ["View Lifecycle", "Жизненный цикл View"]
topic: android
subtopics: [ui-views, lifecycle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-compose-custom-layout--android--hard, q-viewmodel-vs-onsavedinstancestate--android--medium]
created: 2025-10-15
updated: 2025-10-29
sources: []
tags: [android/ui-views, android/lifecycle, view, custom-view, difficulty/medium]
---

# Вопрос (RU)

> Что известно о жизненном цикле View в Android?

# Question (EN)

> What is known about View lifecycles in Android?

---

## Ответ (RU)

Жизненный цикл View описывает последовательность методов от создания до уничтожения представления. Понимание этого цикла критично для управления ресурсами, обработки configuration changes и оптимизации производительности.

### Основные этапы

**Constructor → onAttachedToWindow() → onMeasure() → onLayout() → onDraw() → onDetachedFromWindow()**

### 1. Constructor — Инициализация

```kotlin
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    // ✅ Правильно: инициализация Paint-объектов здесь
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLUE
    }

    init {
        attrs?.let {
            val ta = context.obtainStyledAttributes(it, R.styleable.CustomView)
            // Чтение атрибутов
            ta.recycle() // ✅ Обязательно recycle()
        }
    }
}
```

### 2. onAttachedToWindow() — Запуск ресурсов

Вызывается когда View прикрепляется к окну. Здесь запускаем анимации, регистрируем слушатели.

```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()

    // ✅ Правильно: запуск ресурсов при attach
    sensorManager.registerListener(this, sensor, SensorManager.SENSOR_DELAY_NORMAL)
    handler.post(updateRunnable)
}
```

### 3. onMeasure() — Измерение размера

Определяет размер View. Обязательно вызвать `setMeasuredDimension()`.

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    val desiredSize = 200.dpToPx()

    val width = resolveSize(desiredSize, widthMeasureSpec)
    val height = resolveSize(desiredSize, heightMeasureSpec)

    setMeasuredDimension(width, height) // ✅ Обязательно!
}
```

**MeasureSpec режимы:**
- `EXACTLY` — точный размер (match_parent или конкретное значение)
- `AT_MOST` — максимальный размер (wrap_content)
- `UNSPECIFIED` — любой размер

### 4. onLayout() — Позиционирование

Для ViewGroup позиционирует дочерние элементы. Для простых View можно пересчитать координаты отрисовки.

```kotlin
// ViewGroup
override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
    var currentTop = paddingTop

    for (i in 0 until childCount) {
        val child = getChildAt(i)
        if (child.visibility != GONE) {
            child.layout(
                paddingLeft,
                currentTop,
                paddingLeft + child.measuredWidth,
                currentTop + child.measuredHeight
            )
            currentTop += child.measuredHeight
        }
    }
}
```

### 5. onDraw() — Отрисовка

Рендеринг содержимого View. Вызывается часто — избегать аллокаций!

```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // ✅ Правильно: используем заранее созданные объекты
    canvas.drawCircle(centerX, centerY, radius, paint)
}

// ❌ Неправильно: создание объектов в onDraw
// override fun onDraw(canvas: Canvas) {
//     val paint = Paint() // Создаёт мусор каждый кадр!
//     canvas.drawCircle(x, y, r, paint)
// }
```

### 6. onDetachedFromWindow() — Освобождение ресурсов

Вызывается при отсоединении от окна. Останавливаем анимации, отписываемся от слушателей.

```kotlin
override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()

    // ✅ Правильно: очистка всех ресурсов
    sensorManager.unregisterListener(this)
    handler.removeCallbacks(updateRunnable)
}

// ❌ Неправильно: не отписываться от слушателей → memory leak
```

### Методы обновления

**requestLayout()** — для изменения размера/позиции:
```kotlin
fun updateSize() {
    textSize = 24f
    requestLayout() // → onMeasure() → onLayout() → onDraw()
}
```

**invalidate()** — только для визуальных изменений:
```kotlin
fun updateColor() {
    paint.color = Color.RED
    invalidate() // → onDraw() (быстрее)
}
```

### Сохранение состояния

```kotlin
override fun onSaveInstanceState(): Parcelable {
    val superState = super.onSaveInstanceState()
    return Bundle().apply {
        putParcelable("super_state", superState)
        putInt("custom_value", customValue)
    }
}

override fun onRestoreInstanceState(state: Parcelable?) {
    if (state is Bundle) {
        customValue = state.getInt("custom_value")
        super.onRestoreInstanceState(state.getParcelable("super_state"))
    } else {
        super.onRestoreInstanceState(state)
    }
}
```

### Основные принципы

1. **Инициализация в constructor** — Paint-объекты, значения по умолчанию
2. **Запуск ресурсов в onAttachedToWindow()** — анимации, слушатели
3. **Остановка в onDetachedFromWindow()** — предотвращение утечек памяти
4. **Избегать аллокаций в onDraw()** — создавать объекты заранее
5. **requestLayout() vs invalidate()** — размер vs внешний вид
6. **Сохранение состояния** — для configuration changes

---

## Answer (EN)

The View lifecycle describes the sequence of method calls from view creation to destruction. Understanding this lifecycle is critical for resource management, handling configuration changes, and optimizing performance.

### Key Stages

**Constructor → onAttachedToWindow() → onMeasure() → onLayout() → onDraw() → onDetachedFromWindow()**

### 1. Constructor — Initialization

```kotlin
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    // ✅ Correct: initialize Paint objects here
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLUE
    }

    init {
        attrs?.let {
            val ta = context.obtainStyledAttributes(it, R.styleable.CustomView)
            // Read attributes
            ta.recycle() // ✅ Must recycle()
        }
    }
}
```

### 2. onAttachedToWindow() — Start Resources

Called when the view is attached to a window. Start animations and register listeners here.

```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()

    // ✅ Correct: start resources on attach
    sensorManager.registerListener(this, sensor, SensorManager.SENSOR_DELAY_NORMAL)
    handler.post(updateRunnable)
}
```

### 3. onMeasure() — Determine Size

Determines view size. Must call `setMeasuredDimension()`.

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    val desiredSize = 200.dpToPx()

    val width = resolveSize(desiredSize, widthMeasureSpec)
    val height = resolveSize(desiredSize, heightMeasureSpec)

    setMeasuredDimension(width, height) // ✅ Required!
}
```

**MeasureSpec modes:**
- `EXACTLY` — exact size (match_parent or specific value)
- `AT_MOST` — maximum size (wrap_content)
- `UNSPECIFIED` — any size

### 4. onLayout() — Positioning

For ViewGroups, positions child views. For simple Views, can recalculate drawing coordinates.

```kotlin
// ViewGroup
override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
    var currentTop = paddingTop

    for (i in 0 until childCount) {
        val child = getChildAt(i)
        if (child.visibility != GONE) {
            child.layout(
                paddingLeft,
                currentTop,
                paddingLeft + child.measuredWidth,
                currentTop + child.measuredHeight
            )
            currentTop += child.measuredHeight
        }
    }
}
```

### 5. onDraw() — Rendering

Renders view content. Called frequently — avoid allocations!

```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // ✅ Correct: use pre-created objects
    canvas.drawCircle(centerX, centerY, radius, paint)
}

// ❌ Wrong: creating objects in onDraw
// override fun onDraw(canvas: Canvas) {
//     val paint = Paint() // Creates garbage every frame!
//     canvas.drawCircle(x, y, r, paint)
// }
```

### 6. onDetachedFromWindow() — Release Resources

Called when detached from window. Stop animations, unregister listeners.

```kotlin
override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()

    // ✅ Correct: clean up all resources
    sensorManager.unregisterListener(this)
    handler.removeCallbacks(updateRunnable)
}

// ❌ Wrong: not unregistering listeners → memory leak
```

### Update Methods

**requestLayout()** — for size/position changes:
```kotlin
fun updateSize() {
    textSize = 24f
    requestLayout() // → onMeasure() → onLayout() → onDraw()
}
```

**invalidate()** — for visual changes only:
```kotlin
fun updateColor() {
    paint.color = Color.RED
    invalidate() // → onDraw() (faster)
}
```

### State Preservation

```kotlin
override fun onSaveInstanceState(): Parcelable {
    val superState = super.onSaveInstanceState()
    return Bundle().apply {
        putParcelable("super_state", superState)
        putInt("custom_value", customValue)
    }
}

override fun onRestoreInstanceState(state: Parcelable?) {
    if (state is Bundle) {
        customValue = state.getInt("custom_value")
        super.onRestoreInstanceState(state.getParcelable("super_state"))
    } else {
        super.onRestoreInstanceState(state)
    }
}
```

### Core Principles

1. **Initialize in constructor** — Paint objects, default values
2. **Start resources in onAttachedToWindow()** — animations, listeners
3. **Stop in onDetachedFromWindow()** — prevent memory leaks
4. **Avoid allocations in onDraw()** — pre-create objects
5. **requestLayout() vs invalidate()** — size vs appearance
6. **Save state** — for configuration changes

---

## Follow-ups

1. What is the difference between `invalidate()` and `postInvalidate()`?
2. When should you override `onSizeChanged()` vs `onLayout()`?
3. How does `onMeasure()` handle nested ViewGroups and measure passes?
4. What happens if you forget to call `setMeasuredDimension()` in `onMeasure()`?
5. How can you detect if a View is currently attached to a window?

## References

- [Android View API Documentation](https://developer.android.com/reference/android/view/View)
- [Custom View Components Guide](https://developer.android.com/develop/ui/views/layout/custom-views/custom-components)
- [[c-view-lifecycle]] (concept note)
- [[c-custom-views]] (concept note)

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-activity-lifecycle--android--easy]] - Understanding lifecycle concepts
- [[q-what-is-fragment-lifecycle--android--easy]] - Fragment lifecycle basics

### Related (Same Level)
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] - State preservation patterns
- [[q-spannable-text-styling--android--medium]] - Advanced View text handling
- [[q-how-to-tell-adapter-to-redraw-list-if-an-item-was-deleted--android--medium]] - View updates in RecyclerView

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]] - Custom layouts in Jetpack Compose
- [[q-advanced-custom-views-performance--android--hard]] - Performance optimization for custom views
- [[q-view-rendering-pipeline--android--hard]] - Deep dive into rendering internals
