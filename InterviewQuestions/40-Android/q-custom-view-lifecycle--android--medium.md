---
id: 20251021-180000
title: Custom View Lifecycle / Жизненный цикл Custom View
aliases: [Custom View Lifecycle, Жизненный цикл Custom View]
topic: android
subtopics: [lifecycle, ui-views, ui-graphics]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-view-lifecycle, c-custom-views, q-view-measure-layout--android--medium, q-view-rendering-performance--android--hard]
created: 2025-10-21
updated: 2025-10-30
tags: [android/lifecycle, android/ui-views, android/ui-graphics, custom-views, difficulty/medium]
sources: []
date created: Thursday, October 30th 2025, 11:56:31 am
date modified: Thursday, October 30th 2025, 12:44:42 pm
---

# Вопрос (RU)
> Каков жизненный цикл Custom View в Android? Какие методы вызываются при создании, отрисовке и удалении view?

# Question (EN)
> What is the Custom View lifecycle in Android? Which methods are called during view creation, drawing, and removal?

---

## Ответ (RU)

**View Lifecycle** определяет последовательность вызовов методов от создания до удаления view:

```
Constructor → onAttachedToWindow → onMeasure → onLayout → onDraw → onDetachedFromWindow
```

### Фазы жизненного цикла

#### 1. Constructor — Инициализация

View создается, но еще не присоединена к окну. Размеры неизвестны.

**Действия**: инициализация Paint, загрузка атрибутов XML.

```kotlin
class CustomProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLUE  // ✅ Инициализация в конструкторе
    }

    init {
        setWillNotDraw(false)  // ✅ Включить отрисовку

        attrs?.let {
            context.obtainStyledAttributes(it, R.styleable.CustomProgressBar).apply {
                paint.color = getColor(R.styleable.CustomProgressBar_color, Color.BLUE)
                recycle()  // ✅ Освобождение TypedArray
            }
        }
    }
}
```

#### 2. onAttachedToWindow — Присоединение к окну

View добавлена в иерархию, можно начинать анимации, регистрировать listeners.

```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()
    animator?.start()  // ✅ Безопасно запускать анимации
}

override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()
    animator?.cancel()  // ✅ Обязательная очистка
}
```

#### 3. onMeasure — Измерение размеров

Вызывается многократно. **Обязательно** установить размеры через `setMeasuredDimension()`.

```kotlin
override fun onMeasure(widthSpec: Int, heightSpec: Int) {
    val desiredWidth = 200
    val desiredHeight = 100

    val width = resolveSize(desiredWidth, widthSpec)   // ✅ Учет MeasureSpec
    val height = resolveSize(desiredHeight, heightSpec)

    setMeasuredDimension(width, height)  // ✅ Обязательный вызов
}
```

#### 4. onLayout — Позиционирование (для ViewGroup)

Для простых View не требуется. ViewGroup использует для размещения потомков.

#### 5. onDraw — Отрисовка

Вызывается часто (каждый frame). **Критично для производительности**: не создавать объекты.

```kotlin
// ❌ НЕПРАВИЛЬНО
override fun onDraw(canvas: Canvas) {
    val paint = Paint()  // Выделение памяти каждый кадр!
    canvas.drawCircle(width / 2f, height / 2f, 50f, paint)
}

// ✅ ПРАВИЛЬНО
private val paint = Paint()

override fun onDraw(canvas: Canvas) {
    canvas.drawCircle(width / 2f, height / 2f, 50f, paint)
}
```

### Ключевые правила

1. **Constructor**: инициализация Paint, атрибутов; НЕ использовать размеры
2. **onAttachedToWindow**: запуск анимаций, регистрация listeners
3. **onMeasure**: ВСЕГДА вызывать `setMeasuredDimension()`
4. **onDraw**: НЕ создавать объекты, НЕ выделять память
5. **onDetachedFromWindow**: остановить анимации, отписаться от listeners, освободить ресурсы

### Оптимизация производительности

```kotlin
class OptimizedCustomView(context: Context, attrs: AttributeSet?) : View(context, attrs) {

    // ✅ Переиспользуемые объекты
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val rect = RectF()

    override fun onDraw(canvas: Canvas) {
        // ✅ Переиспользование rect вместо создания нового
        rect.set(0f, 0f, width.toFloat(), height.toFloat())
        canvas.drawRect(rect, paint)
    }
}
```

## Answer (EN)

**View Lifecycle** defines the sequence of method calls from creation to removal:

```
Constructor → onAttachedToWindow → onMeasure → onLayout → onDraw → onDetachedFromWindow
```

### Lifecycle Phases

#### 1. Constructor — Initialization

View is created but not yet attached to window. Dimensions unknown.

**Actions**: initialize Paint, load XML attributes.

```kotlin
class CustomProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLUE  // ✅ Initialize in constructor
    }

    init {
        setWillNotDraw(false)  // ✅ Enable drawing

        attrs?.let {
            context.obtainStyledAttributes(it, R.styleable.CustomProgressBar).apply {
                paint.color = getColor(R.styleable.CustomProgressBar_color, Color.BLUE)
                recycle()  // ✅ Release TypedArray
            }
        }
    }
}
```

#### 2. onAttachedToWindow — Attach to Window

View added to hierarchy, safe to start animations, register listeners.

```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()
    animator?.start()  // ✅ Safe to start animations
}

override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()
    animator?.cancel()  // ✅ Mandatory cleanup
}
```

#### 3. onMeasure — Measure Dimensions

Called multiple times. **Must** set dimensions via `setMeasuredDimension()`.

```kotlin
override fun onMeasure(widthSpec: Int, heightSpec: Int) {
    val desiredWidth = 200
    val desiredHeight = 100

    val width = resolveSize(desiredWidth, widthSpec)   // ✅ Respect MeasureSpec
    val height = resolveSize(desiredHeight, heightSpec)

    setMeasuredDimension(width, height)  // ✅ Required call
}
```

#### 4. onLayout — Positioning (for ViewGroup)

Not required for simple Views. ViewGroup uses it to position children.

#### 5. onDraw — Drawing

Called frequently (every frame). **Performance critical**: no object creation.

```kotlin
// ❌ WRONG
override fun onDraw(canvas: Canvas) {
    val paint = Paint()  // Memory allocation every frame!
    canvas.drawCircle(width / 2f, height / 2f, 50f, paint)
}

// ✅ CORRECT
private val paint = Paint()

override fun onDraw(canvas: Canvas) {
    canvas.drawCircle(width / 2f, height / 2f, 50f, paint)
}
```

### Key Rules

1. **Constructor**: initialize Paint, attributes; DO NOT use dimensions
2. **onAttachedToWindow**: start animations, register listeners
3. **onMeasure**: ALWAYS call `setMeasuredDimension()`
4. **onDraw**: NO object creation, NO memory allocation
5. **onDetachedFromWindow**: stop animations, unregister listeners, release resources

### Performance Optimization

```kotlin
class OptimizedCustomView(context: Context, attrs: AttributeSet?) : View(context, attrs) {

    // ✅ Reusable objects
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val rect = RectF()

    override fun onDraw(canvas: Canvas) {
        // ✅ Reuse rect instead of creating new one
        rect.set(0f, 0f, width.toFloat(), height.toFloat())
        canvas.drawRect(rect, paint)
    }
}
```

---

## Follow-ups

- What happens if you forget to call `setMeasuredDimension()` in onMeasure?
- How does `invalidate()` differ from `requestLayout()` and when should each be used?
- Why is object allocation in onDraw problematic even with modern garbage collectors?
- How do you save and restore custom view state during configuration changes?
- What is the role of `onSizeChanged()` and when is it called relative to onMeasure?

## References

- [[c-view-lifecycle]]
- [[c-custom-views]]
- [[c-canvas-drawing]]
- [[c-memory-optimization]]
- https://developer.android.com/guide/topics/ui/custom-components
- https://developer.android.com/reference/android/view/View

## Related Questions

### Prerequisites (Easier)
- [[q-view-basics--android--easy]]
- [[q-xml-layouts--android--easy]]

### Related (Same Level)
- [[q-view-measure-layout--android--medium]]
- [[q-canvas-drawing-techniques--android--medium]]
- [[q-view-state-saving--android--medium]]

### Advanced (Harder)
- [[q-custom-viewgroup-layout--android--hard]]
- [[q-view-rendering-performance--android--hard]]
- [[q-hardware-acceleration-views--android--hard]]
