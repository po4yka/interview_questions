---\
id: "20251030-140000"
title: "View Lifecycle / Жизненный цикл View"
aliases: ["Custom View Lifecycle", "Lifecycle View", "View Lifecycle", "Жизненный цикл View"]
summary: "Android View lifecycle methods from creation to cleanup"
topic: "android"
subtopics: ["custom-views", "lifecycle", "ui"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: []
created: "2025-10-30"
updated: "2025-10-30"
tags: ["android", "concept", "custom-views", "lifecycle", "ui", "difficulty/medium"]
---\

# Summary (EN)

The Android `View` lifecycle defines the sequence of callback methods invoked as a `View` is created, attached to a window, measured, laid out, drawn, and eventually detached. Understanding this lifecycle is critical for custom views to properly allocate resources, handle state, and clean up when destroyed.

**Core `Lifecycle` Sequence**:
1. **Constructor** - `View` instantiation
2. **onAttachedToWindow()** - `View` attached to window, acquire resources
3. **onMeasure()** - Calculate view dimensions
4. **onLayout()** - Position child views
5. **onDraw()** - Render view content
6. **onDetachedFromWindow()** - `View` removed from window, release resources

# Сводка (RU)

Жизненный цикл `View` определяет последовательность вызова методов-обратного вызова при создании `View`, присоединении к окну, измерении, размещении, отрисовке и, в конечном итоге, отсоединении. Понимание этого цикла критически важно для custom views, чтобы правильно выделять ресурсы, управлять состоянием и освобождать память при уничтожении.

**Основная последовательность жизненного цикла**:
1. **Конструктор** - Создание экземпляра `View`
2. **onAttachedToWindow()** - `View` присоединена к окну, получить ресурсы
3. **onMeasure()** - Вычислить размеры view
4. **onLayout()** - Разместить дочерние view
5. **onDraw()** - Отрисовать содержимое view
6. **onDetachedFromWindow()** - `View` удалена из окна, освободить ресурсы

---

## Lifecycle Methods (EN)

**Constructor(context: `Context`, attrs: AttributeSet?)**: Initialize view, parse custom attributes from XML. Keep lightweight - avoid heavy operations.

**onAttachedToWindow()**: `View` added to window hierarchy. Start animations, register listeners, acquire resources. Called when view becomes visible to user.

**onMeasure(widthMeasureSpec: `Int`, heightMeasureSpec: `Int`)**: Calculate desired dimensions based on constraints. Must call `setMeasuredDimension()`. May be called multiple times.

**onLayout(changed: `Boolean`, left: `Int`, top: `Int`, right: `Int`, bottom: `Int`)**: Position child views. Only relevant for ViewGroups. Final position/size now known.

**onDraw(canvas: `Canvas`)**: Render view content. Performance-critical - avoid allocations. Use `invalidate()` to trigger redraw.

**onDetachedFromWindow()**: `View` removed from window. Stop animations, unregister listeners, release resources. Mirror of `onAttachedToWindow()`.

**onSaveInstanceState()** / **onRestoreInstanceState()**: Save/restore view state across configuration changes or process death.

## Методы Жизненного Цикла (RU)

**Конструктор(context: `Context`, attrs: AttributeSet?)**: Инициализация view, парсинг атрибутов из XML. Должен быть легковесным - избегать тяжелых операций.

**onAttachedToWindow()**: `View` добавлена в иерархию окна. Запустить анимации, зарегистрировать слушатели, получить ресурсы. Вызывается, когда view становится видимой для пользователя.

**onMeasure(widthMeasureSpec: `Int`, heightMeasureSpec: `Int`)**: Вычислить желаемые размеры на основе ограничений. Обязательно вызвать `setMeasuredDimension()`. Может вызываться многократно.

**onLayout(changed: `Boolean`, left: `Int`, top: `Int`, right: `Int`, bottom: `Int`)**: Разместить дочерние view. Актуально только для ViewGroups. Финальная позиция/размер теперь известны.

**onDraw(canvas: `Canvas`)**: Отрисовать содержимое view. Критично для производительности - избегать аллокаций. Использовать `invalidate()` для перерисовки.

**onDetachedFromWindow()**: `View` удалена из окна. Остановить анимации, отменить регистрацию слушателей, освободить ресурсы. Зеркальный метод для `onAttachedToWindow()`.

**onSaveInstanceState()** / **onRestoreInstanceState()**: Сохранить/восстановить состояние view при изменении конфигурации или уничтожении процесса.

---

## Code Example (EN/RU)

```kotlin
class CustomProgressView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var progress: Float = 0f
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private var animator: ValueAnimator? = null

    init {
        // Parse custom attributes / Парсинг custom атрибутов
        context.theme.obtainStyledAttributes(attrs, R.styleable.CustomProgressView, 0, 0).apply {
            progress = getFloat(R.styleable.CustomProgressView_progress, 0f)
            recycle()
        }
    }

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        // Acquire resources / Получить ресурсы
        startAnimation()
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val desiredWidth = 200.dpToPx()
        val desiredHeight = 200.dpToPx()

        val width = resolveSize(desiredWidth, widthMeasureSpec)
        val height = resolveSize(desiredHeight, heightMeasureSpec)

        setMeasuredDimension(width, height)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // Draw progress arc / Отрисовать дугу прогресса
        val rect = RectF(0f, 0f, width.toFloat(), height.toFloat())
        canvas.drawArc(rect, -90f, 360f * progress, true, paint)
    }

    override fun onDetachedFromWindow() {
        // Release resources / Освободить ресурсы
        animator?.cancel()
        animator = null
        super.onDetachedFromWindow()
    }

    override fun onSaveInstanceState(): Parcelable {
        val superState = super.onSaveInstanceState()
        return Bundle().apply {
            putParcelable("superState", superState)
            putFloat("progress", progress)
        }
    }

    override fun onRestoreInstanceState(state: Parcelable?) {
        if (state is Bundle) {
            progress = state.getFloat("progress")
            super.onRestoreInstanceState(state.getParcelable("superState"))
        } else {
            super.onRestoreInstanceState(state)
        }
    }

    private fun startAnimation() {
        animator = ValueAnimator.ofFloat(0f, 1f).apply {
            duration = 2000
            addUpdateListener {
                progress = it.animatedValue as Float
                invalidate()
            }
            start()
        }
    }
}
```

---

## Use Cases / Trade-offs

**Use Cases**:
- Custom animated views requiring resource management
- Views with heavy initialization needing proper timing
- State-preserving views across configuration changes
- ViewGroups with complex child layout logic

**Best Practices**:
- Acquire expensive resources in `onAttachedToWindow()`, release in `onDetachedFromWindow()`
- Avoid allocations in `onDraw()` - pre-allocate objects in constructor/onAttach
- Use `invalidate()` for full redraw, `invalidate(rect)` for partial updates
- Save essential state in `onSaveInstanceState()` for process death scenarios
- Cancel animations/async work in `onDetachedFromWindow()` to prevent leaks

**Trade-offs**:
- More lifecycle awareness = more boilerplate code
- State restoration adds complexity but improves UX
- Frequent `invalidate()` calls impact performance - batch updates when possible

## References

- [Android `View` Documentation](https://developer.android.com/reference/android/view/View)
- [Custom `View` Components Guide](https://developer.android.com/develop/ui/views/layout/custom-views/custom-components)
- [Saving UI States](https://developer.android.com/topic/libraries/architecture/saving-states)
