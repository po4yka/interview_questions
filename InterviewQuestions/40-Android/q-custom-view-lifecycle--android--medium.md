---
id: 20251021-180000
title: Custom View Lifecycle / Жизненный цикл Custom View
aliases: [Custom View Lifecycle, Жизненный цикл Custom View]
topic: android
subtopics: [lifecycle, ui-views]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-activity-lifecycle-methods--android--medium, q-performance-optimization-android--android--medium]
created: 2025-10-21
updated: 2025-10-29
tags: [android/lifecycle, android/ui-views, difficulty/medium]
sources: []
---
# Вопрос (RU)
> Жизненный цикл Custom View?

# Question (EN)
> Custom View Lifecycle?

---

## Ответ (RU)

**View Lifecycle** критичен для эффективных custom view. Основные фазы:

```
Constructor → onAttachedToWindow → onMeasure → onLayout → onDraw → onDetachedFromWindow
```

### 1. Constructor - Инициализация

Инициализация Paint, атрибутов. View еще не в Window, размеры неизвестны.

```kotlin
class CustomProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLUE // ✅ Инициализация в конструкторе
    }

    init {
        setWillNotDraw(false) // ✅ Включить отрисовку

        attrs?.let {
            context.obtainStyledAttributes(it, R.styleable.CustomProgressBar).apply {
                paint.color = getColor(R.styleable.CustomProgressBar_color, Color.BLUE)
                recycle() // ✅ Освободить ресурсы
            }
        }
    }
}
```

### 2. onAttachedToWindow - Подключение к окну

Запуск анимаций, регистрация listeners. View готова к работе.

```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()
    startAnimation() // ✅ Безопасно запускать анимации
    registerListener()
}

override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()
    stopAnimation() // ✅ Обязательная очистка
    unregisterListener()
}
```

### 3. onMeasure - Определение размеров

Вызывается многократно. ОБЯЗАТЕЛЬНО вызвать `setMeasuredDimension()`.

```kotlin
override fun onMeasure(widthSpec: Int, heightSpec: Int) {
    val width = resolveSize(200, widthSpec)  // ✅ Учесть MeasureSpec
    val height = resolveSize(100, heightSpec)
    setMeasuredDimension(width, height) // ✅ Обязательно
}
```

### 4. onDraw - Отрисовка

Вызывается часто — критично для производительности.

```kotlin
// ❌ ПЛОХО - создание объектов
override fun onDraw(canvas: Canvas) {
    val paint = Paint() // Выделение памяти на каждый frame!
    canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), paint)
}

// ✅ ХОРОШО - использование pre-allocated объектов
private val paint = Paint()

override fun onDraw(canvas: Canvas) {
    canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), paint)
}
```

### Ключевые правила

1. **Constructor**: инициализация Paint, атрибутов
2. **onAttachedToWindow**: запуск анимаций
3. **onMeasure**: вызвать `setMeasuredDimension()`
4. **onDraw**: НЕ создавать объекты
5. **onDetachedFromWindow**: остановить анимации, освободить ресурсы

## Answer (EN)

**View Lifecycle** is critical for efficient custom views. Main phases:

```
Constructor → onAttachedToWindow → onMeasure → onLayout → onDraw → onDetachedFromWindow
```

### 1. Constructor - Initialization

Initialize Paint, attributes. View not yet in Window, dimensions unknown.

```kotlin
class CustomProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLUE // ✅ Initialize in constructor
    }

    init {
        setWillNotDraw(false) // ✅ Enable drawing

        attrs?.let {
            context.obtainStyledAttributes(it, R.styleable.CustomProgressBar).apply {
                paint.color = getColor(R.styleable.CustomProgressBar_color, Color.BLUE)
                recycle() // ✅ Release resources
            }
        }
    }
}
```

### 2. onAttachedToWindow - Attach to window

Start animations, register listeners. View is ready.

```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()
    startAnimation() // ✅ Safe to start animations
    registerListener()
}

override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()
    stopAnimation() // ✅ Mandatory cleanup
    unregisterListener()
}
```

### 3. onMeasure - Determine dimensions

Called multiple times. MUST call `setMeasuredDimension()`.

```kotlin
override fun onMeasure(widthSpec: Int, heightSpec: Int) {
    val width = resolveSize(200, widthSpec)  // ✅ Respect MeasureSpec
    val height = resolveSize(100, heightSpec)
    setMeasuredDimension(width, height) // ✅ Required
}
```

### 4. onDraw - Drawing

Called frequently — performance critical.

```kotlin
// ❌ BAD - object creation
override fun onDraw(canvas: Canvas) {
    val paint = Paint() // Memory allocation every frame!
    canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), paint)
}

// ✅ GOOD - use pre-allocated objects
private val paint = Paint()

override fun onDraw(canvas: Canvas) {
    canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), paint)
}
```

### Key rules

1. **Constructor**: initialize Paint, attributes
2. **onAttachedToWindow**: start animations
3. **onMeasure**: call `setMeasuredDimension()`
4. **onDraw**: NO object creation
5. **onDetachedFromWindow**: stop animations, release resources

---

## Follow-ups

- How to save and restore custom view state during configuration changes?
- What happens if you forget to call `setMeasuredDimension()` in onMeasure?
- Why is object allocation in onDraw() problematic for performance?
- When should you override onLayout vs onSizeChanged?
- How to debug custom view rendering issues using Layout Inspector?

## References

- [[c-lifecycle]]
- [[c-custom-views]]
- [[c-memory-management]]
- https://developer.android.com/guide/topics/ui/custom-components
- https://developer.android.com/reference/android/view/View

## Related Questions

### Prerequisites (Easier)
- [[q-activity-lifecycle-methods--android--medium]]
- [[q-view-basics--android--easy]]

### Related (Same Level)
- [[q-custom-view-state-saving--android--medium]]
- [[q-performance-optimization-android--android--medium]]
- [[q-canvas-drawing--android--medium]]

### Advanced (Harder)
- [[q-custom-viewgroup-layout--android--hard]]
- [[q-custom-view-animations--android--hard]]
