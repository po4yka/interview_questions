---
id: android-233
title: "View Lifecycle in Android / View lifecycle in Android"
aliases: ["View Lifecycle", "View lifecycle in Android"]
topic: android
subtopics: [lifecycle, ui-views]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-activity-lifecycle, c-fragment-lifecycle]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/lifecycle, android/ui-views, difficulty/medium]

---

# Вопрос (RU)

> Что нужно знать о жизненном цикле `View` в Android?

# Question (EN)

> What is known about `View` lifecycles in Android?

## Ответ (RU)

Жизненный цикл `View` описывает, как `View` создается, прикрепляется к окну, измеряется, раскладывается, рисуется и в итоге отсоединяется. Понимание этого цикла важно для корректного управления ресурсами, обработки смены конфигурации и оптимизации производительности.

### Ключевые стадии

**Constructor → onAttachedToWindow() → onMeasure() → onLayout() → onDraw() → onDetachedFromWindow()**

(Это упрощенная схема: есть дополнительные колбэки, такие как `onFinishInflate()`, `onSizeChanged()`, и возможны несколько проходов `measure`/`layout`/`draw`.)

### 1. Constructor и инициализация

```kotlin
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    // Правильно: инициализировать объекты Paint и т.п. здесь
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLUE
    }

    init {
        attrs?.let {
            val ta = context.obtainStyledAttributes(it, R.styleable.CustomView)
            // Читаем атрибуты
            ta.recycle() // Обязательно вызвать recycle()
        }
    }
}
```

### 2. onAttachedToWindow() – старт ресурсов

Вызывается, когда `View` прикрепляется к окну. Здесь запускают анимации, регистрируют слушатели и т.п.

```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()

    // Правильно: запуск ресурсов при attach
    sensorManager.registerListener(this, sensor, SensorManager.SENSOR_DELAY_NORMAL)
    handler.post(updateRunnable)
}
```

### 3. onMeasure() – определение размера

Определяет размер `View`. Обязательно вызвать `setMeasuredDimension()`.

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    val desiredSize = 200.dpToPx()

    val width = resolveSize(desiredSize, widthMeasureSpec)
    val height = resolveSize(desiredSize, heightMeasureSpec)

    setMeasuredDimension(width, height) // Обязательно!
}
```

**Режимы MeasureSpec:**
- `EXACTLY` – родитель задал точный размер: например, `match_parent` или конкретное значение в dp; родитель также может передать `EXACTLY` для `wrap_content` в зависимости от своей логики.
- `AT_MOST` – максимум: обычно для `wrap_content`, `View` не должен превышать заданный размер (`size <= specSize`).
- `UNSPECIFIED` – нет ограничений; `View` может выбрать любой размер (особые случаи, например внутри `ScrollView`).

### 4. onLayout() – позиционирование

Для `ViewGroup` отвечает за размещение дочерних `View`. Для простых `View` обычно `onLayout()` не переопределяют; вместо этого используют `onSizeChanged()` (или при необходимости `onLayout()`) для перерасчета внутренних координат для рисования.

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

### 5. onDraw() – отрисовка

Отвечает за рисование содержимого `View`. Вызывается часто, поэтому нужно избегать аллокаций внутри.

```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // Правильно: использовать заранее созданные объекты
    canvas.drawCircle(centerX, centerY, radius, paint)
}

// Неправильно: создавать объекты в onDraw
// override fun onDraw(canvas: Canvas) {
//     val paint = Paint() // Лишние аллокации на каждый кадр
//     canvas.drawCircle(x, y, r, paint)
// }
```

### 6. onDetachedFromWindow() – освобождение ресурсов

Вызывается при отсоединении от окна. Останавливаем анимации, отписываем слушатели, чистим ресурсы.

```kotlin
override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()

    // Правильно: корректно освободить ресурсы
    sensorManager.unregisterListener(this)
    handler.removeCallbacks(updateRunnable)
}

// Неправильно: не отписываться от слушателей приводит к утечкам памяти
```

### Методы обновления

**`requestLayout()`** – при изменении размеров/позиционирования:

```kotlin
fun updateSize() {
    radius = 24f
    requestLayout() // Запустит onMeasure() → onLayout() → onDraw()
}
```

**`invalidate()`** – при изменении только внешнего вида:

```kotlin
fun updateColor() {
    paint.color = Color.RED
    invalidate() // Запустит onDraw() (без нового measure/layout)
}
```

Важно: и `requestLayout()`, и `invalidate()` должны вызываться с UI-потока.

### Сохранение состояния

`View` может сохранять и восстанавливать собственное состояние, чтобы значения переживали пересоздание `Activity`, когда восстанавливается та же иерархия `View`.

```kotlin
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var customValue: Int = 0

    override fun onSaveInstanceState(): Parcelable? {
        val superState = super.onSaveInstanceState()
        return SavedState(superState).apply {
            this.customValue = this@CustomView.customValue
        }
    }

    override fun onRestoreInstanceState(state: Parcelable?) {
        if (state is SavedState) {
            super.onRestoreInstanceState(state.superState)
            customValue = state.customValue
        } else {
            super.onRestoreInstanceState(state)
        }
    }

    internal class SavedState : BaseSavedState {
        var customValue: Int = 0

        constructor(superState: Parcelable?) : super(superState)

        private constructor(`in`: Parcel) : super(`in`) {
            customValue = `in`.readInt()
        }

        override fun writeToParcel(out: Parcel, flags: Int) {
            super.writeToParcel(out, flags)
            out.writeInt(customValue)
        }

        companion object CREATOR : Parcelable.Creator<SavedState> {
            override fun createFromParcel(source: Parcel): SavedState = SavedState(source)
            override fun newArray(size: Int): Array<SavedState?> = arrayOfNulls(size)
        }
    }
}
```

### Ключевые принципы

1. Инициализировать тяжелые/статичные объекты в конструкторе или `init` (например, `Paint`, значения по умолчанию).
2. Запускать внешние ресурсы в `onAttachedToWindow()` (анимации, слушатели, сенсоры).
3. Освобождать ресурсы в `onDetachedFromWindow()` во избежание утечек.
4. Избегать аллокаций в `onDraw()`, переиспользовать объекты.
5. Корректно использовать `requestLayout()` и `invalidate()` (разметка/размер vs внешний вид), вызывая их с UI-потока.
6. Правильно реализовывать `onSaveInstanceState()` / `onRestoreInstanceState()` для состояния `View`.

## Answer (EN)

The `View` lifecycle describes how a `View` is created, attached to a window, measured, laid out, drawn, and eventually detached. Understanding this lifecycle is critical for resource management, handling configuration changes correctly, and optimizing performance.

### Key Stages

**Constructor → onAttachedToWindow() → onMeasure() → onLayout() → onDraw() → onDetachedFromWindow()**

(Note: this is a simplified view; there are additional callbacks like `onFinishInflate()`, `onSizeChanged()`, and multiple measure/layout/draw passes.)

### 1. Constructor  Initialization

```kotlin
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    // Correct: initialize Paint objects here
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLUE
    }

    init {
        attrs?.let {
            val ta = context.obtainStyledAttributes(it, R.styleable.CustomView)
            // Read attributes
            ta.recycle() // Must recycle()
        }
    }
}
```

### 2. onAttachedToWindow()  Start Resources

Called when the view is attached to a window. Start animations and register listeners here.

```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()

    // Correct: start resources on attach
    sensorManager.registerListener(this, sensor, SensorManager.SENSOR_DELAY_NORMAL)
    handler.post(updateRunnable)
}
```

### 3. onMeasure()  Determine Size

Determines view size. Must call `setMeasuredDimension()`.

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    val desiredSize = 200.dpToPx()

    val width = resolveSize(desiredSize, widthMeasureSpec)
    val height = resolveSize(desiredSize, heightMeasureSpec)

    setMeasuredDimension(width, height) // Required!
}
```

**MeasureSpec modes:**
- `EXACTLY` – parent has determined an exact size: e.g., `match_parent` or an exact dp value; a parent may also pass `EXACTLY` for `wrap_content` depending on its logic.
- `AT_MOST` – maximum size: commonly used for `wrap_content`, where the `View` must not exceed the given size (`size <= specSize`).
- `UNSPECIFIED` – no constraint; the `View` can be any size (used in special cases like within `ScrollView`).

### 4. onLayout()  Positioning

For `ViewGroup`, positions child views. For simple `View`s, you typically do not override `onLayout`; instead, you often use `onSizeChanged()` (or `onLayout` if needed) to recalculate internal drawing coordinates.

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

### 5. onDraw()  Rendering

Renders view content. Called frequently – avoid allocations inside.

```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // Correct: use pre-created objects
    canvas.drawCircle(centerX, centerY, radius, paint)
}

// Wrong: creating objects in onDraw
// override fun onDraw(canvas: Canvas) {
//     val paint = Paint() // Creates garbage every frame!
//     canvas.drawCircle(x, y, r, paint)
// }
```

### 6. onDetachedFromWindow()  Release Resources

Called when detached from window. Stop animations, unregister listeners.

```kotlin
override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()

    // Correct: clean up all resources
    sensorManager.unregisterListener(this)
    handler.removeCallbacks(updateRunnable)
}

// Wrong: not unregistering listeners → memory leak
```

### Update Methods

**`requestLayout()`** – for size/position changes:

```kotlin
fun updateSize() {
    radius = 24f
    requestLayout() // Triggers onMeasure() → onLayout() → onDraw()
}
```

**`invalidate()`** – for visual changes only:

```kotlin
fun updateColor() {
    paint.color = Color.RED
    invalidate() // Triggers onDraw() (faster)
}
```

(Note: both `requestLayout()` and `invalidate()` must be called from the UI thread.)

### State Preservation

Views can save and restore their own instance state so that values persist across `Activity` recreation when the same `View` hierarchy is restored.

```kotlin
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var customValue: Int = 0

    override fun onSaveInstanceState(): Parcelable? {
        val superState = super.onSaveInstanceState()
        return SavedState(superState).apply {
            this.customValue = this@CustomView.customValue
        }
    }

    override fun onRestoreInstanceState(state: Parcelable?) {
        if (state is SavedState) {
            super.onRestoreInstanceState(state.superState)
            customValue = state.customValue
        } else {
            super.onRestoreInstanceState(state)
        }
    }

    internal class SavedState : BaseSavedState {
        var customValue: Int = 0

        constructor(superState: Parcelable?) : super(superState)

        private constructor(`in`: Parcel) : super(`in`) {
            customValue = `in`.readInt()
        }

        override fun writeToParcel(out: Parcel, flags: Int) {
            super.writeToParcel(out, flags)
            out.writeInt(customValue)
        }

        companion object CREATOR : Parcelable.Creator<SavedState> {
            override fun createFromParcel(source: Parcel): SavedState = SavedState(source)
            override fun newArray(size: Int): Array<SavedState?> = arrayOfNulls(size)
        }
    }
}
```

### Core Principles

1. Initialize heavy/static objects in the constructor or `init` block (e.g., `Paint`, default values).
2. Start external resources in `onAttachedToWindow()` (animations, listeners, sensors).
3. Stop and clean up in `onDetachedFromWindow()` to prevent leaks.
4. Avoid allocations in `onDraw()`; reuse objects.
5. Use `requestLayout()` vs `invalidate()` appropriately (layout/size vs appearance) and from the UI thread.
6. Implement `onSaveInstanceState()` / `onRestoreInstanceState()` correctly (e.g., via `BaseSavedState`) for `View`-specific state.

## Дополнительные вопросы (RU)

1. В чем разница между `invalidate()` и `postInvalidate()`?
2. Когда лучше переопределять `onSizeChanged()`, а когда `onLayout()`?
3. Как `onMeasure()` обрабатывает вложенные `ViewGroup` и несколько проходов измерения?
4. Что произойдет, если не вызвать `setMeasuredDimension()` в `onMeasure()`?
5. Как определить, прикреплена ли `View` в данный момент к окну?

## Follow-ups

1. What is the difference between `invalidate()` and `postInvalidate()`?
2. When should you override `onSizeChanged()` vs `onLayout()`?
3. How does `onMeasure()` handle nested ViewGroups and measure passes?
4. What happens if you forget to call `setMeasuredDimension()` in `onMeasure()`?
5. How can you detect if a `View` is currently attached to a window?

## Ссылки (RU)

- Официальная документация по `View`: https://developer.android.com/reference/android/view/View
- Руководство по созданию кастомных `View`: https://developer.android.com/develop/ui/views/layout/custom-views/custom-components
- Обзор жизненного цикла компонентов: [[c-activity-lifecycle]], [[c-fragment-lifecycle]]

## References

- Android `View` API Documentation: https://developer.android.com/reference/android/view/View
- Custom `View` Components Guide: https://developer.android.com/develop/ui/views/layout/custom-views/custom-components
- Related lifecycle concepts: [[c-activity-lifecycle]], [[c-fragment-lifecycle]]

## Связанные вопросы (RU)

### Базовые
- [[q-activity-lifecycle-methods--android--medium]] — базовые принципы жизненного цикла `Activity`
- [[q-android-app-components--android--easy]] — компоненты Android-приложения

### На том же уровне
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] — подходы к сохранению состояния
- [[q-how-to-tell-adapter-to-redraw-list-if-an-item-was-deleted--android--medium]] — обновление `View` в `RecyclerView`

### Сложнее
- [[q-compose-custom-layout--android--hard]] — кастомные layout-ы в Jetpack Compose

## Related Questions

### Prerequisites (Easier)
- [[q-activity-lifecycle-methods--android--medium]] - Understanding lifecycle concepts
- [[q-android-app-components--android--easy]] - Android app components overview

### Related (Same Level)
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] - State preservation patterns
- [[q-how-to-tell-adapter-to-redraw-list-if-an-item-was-deleted--android--medium]] - `View` updates in RecyclerView

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]] - Custom layouts in Jetpack Compose
