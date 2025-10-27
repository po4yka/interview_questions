---
id: 20251021-140000
title: Custom Drawable Implementation / Реализация Custom Drawable
aliases: ["Custom Drawable Implementation", "Реализация Custom Drawable"]
topic: android
subtopics: [ui-graphics, ui-views]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-canvas-drawing-optimization--android--hard, q-custom-viewgroup-layout--android--hard]
created: 2025-10-21
updated: 2025-10-27
tags: [android/ui-graphics, android/ui-views, difficulty/medium]
sources: ["https://developer.android.com/reference/android/graphics/drawable/Drawable"]
---

# Вопрос (RU)
> Как реализовать Custom Drawable в Android?

# Question (EN)
> How to implement a Custom Drawable in Android?

---

## Ответ (RU)

### Что такое Custom Drawable
- Легковесная переиспользуемая графика для нескольких View
- Эффективнее, чем кастомная View для простой графики без взаимодействия
- Управляется системой Android, не требует сложного жизненного цикла

Связано с концептами [[c-custom-views]], c-canvas-drawing и [[c-lifecycle]].

### Drawable vs Custom View

| Характеристика | Drawable | Custom View |
|---------|----------|-------------|
| **Случай использования** | Простая графика, иконки | Интерактивные UI элементы |
| **Производительность** | Легковесная | Тяжелая (полноценная View) |
| **Взаимодействие** | Без обработки касаний | Полная поддержка касаний |
| **Жизненный цикл** | Простой | Сложный (attach/detach) |
| **Переиспользуемость** | Высокая | Ниже |
| **Состояние** | Ограниченное | Полное управление состоянием |

**Используйте Drawable когда:**
- Неинтерактивная графика
- Переиспользование в разных View
- Простые формы/анимации
- Фоновая/передняя графика

**Используйте Custom View когда:**
- Нужно взаимодействие с касаниями
- Сложный жизненный цикл
- Требования доступности
- Координация анимаций

### Жизненный цикл Drawable
1. **Создание** - конструктор или фабричные методы
2. **Установка границ** - `setBounds()` определяет область рисования
3. **Отрисовка** - `draw()` вызывается системой
4. **Изменения состояния** - `setState()` для обновления внешнего вида
5. **Очистка** - автоматическое управление памятью

### Ключевые методы для переопределения

**draw(canvas: Canvas)**
- Основной метод отрисовки
- Вызывается системой для рендеринга

**setBounds()**
- Устанавливает границы области рисования
- Определяет где и какого размера рисовать

**getOpacity()**
- Возвращает прозрачность drawable
- PixelFormat.OPAQUE, TRANSLUCENT, TRANSPARENT

**setAlpha(alpha: Int)**
- Устанавливает альфа-канал
- Влияет на прозрачность

**setColorFilter(colorFilter: ColorFilter?)**
- Применяет цветовой фильтр
- Для тонирования и цветовых эффектов

### Минимальная реализация

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
            invalidateSelf() // Запрос перерисовки
        }

    override fun draw(canvas: Canvas) {
        val bounds = bounds
        val centerX = bounds.centerX().toFloat()
        val centerY = bounds.centerY().toFloat()
        val radius = min(bounds.width(), bounds.height()) / 2f

        canvas.drawCircle(centerX, centerY, radius, paint)
    }

    override fun setAlpha(alpha: Int) {
        paint.alpha = alpha
        invalidateSelf()
    }

    override fun setColorFilter(colorFilter: ColorFilter?) {
        paint.colorFilter = colorFilter
        invalidateSelf()
    }

    @Deprecated("Deprecated in Java")
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT

    override fun getIntrinsicWidth(): Int = 48
    override fun getIntrinsicHeight(): Int = 48
}
```

### Управление состоянием

```kotlin
class StatefulDrawable : Drawable() {
    private val paint = Paint()
    private var isPressed = false

    override fun draw(canvas: Canvas) {
        // ✅ Оптимально: выбор цвета по состоянию
        paint.color = if (isPressed) Color.RED else Color.BLUE
        canvas.drawRect(bounds, paint)
    }

    override fun setState(stateSet: IntArray): Boolean {
        val wasPressed = isPressed
        isPressed = stateSet.contains(android.R.attr.state_pressed)

        if (wasPressed != isPressed) {
            invalidateSelf()
            return true
        }
        return false
    }

    override fun isStateful(): Boolean = true

    // ... остальные методы
}
```

### Анимированный Drawable

```kotlin
class AnimatedDrawable : Drawable() {
    private val paint = Paint()
    private var animationProgress = 0f

    override fun draw(canvas: Canvas) {
        val bounds = bounds
        val animatedRadius = bounds.width() * animationProgress / 2

        canvas.drawCircle(
            bounds.centerX().toFloat(),
            bounds.centerY().toFloat(),
            animatedRadius,
            paint
        )
    }

    fun startAnimation() {
        // Использование ValueAnimator
        ValueAnimator.ofFloat(0f, 1f).apply {
            duration = 1000
            addUpdateListener { animator ->
                animationProgress = animator.animatedValue as Float
                invalidateSelf()
            }
            start()
        }
    }

    // ... остальные методы
}
```

### Лучшие практики

1. **Используйте Paint.ANTI_ALIAS_FLAG** для гладких краёв
2. **Кэшируйте Paint объекты** - не создавайте в draw()
3. **Вызывайте invalidateSelf()** при изменении внешнего вида
4. **Реализуйте intrinsic размеры** для правильной разметки
5. **Обрабатывайте состояния** через setState() для интерактивности
6. **Избегайте сложных вычислений** в draw() - предварительно вычисляйте
7. **Используйте правильные границы** через свойство bounds

### Подводные камни

- **Не создавайте объекты в draw()** - влияет на производительность
- **Правильно обрабатывайте bounds** - система может их изменить
- **Помните о прозрачности** - корректно реализуйте getOpacity()
- **Не забывайте invalidateSelf()** при изменениях
- **Тестируйте на разных размерах** - intrinsic размеры важны

## Answer (EN)

### What is Custom Drawable
- Lightweight, reusable graphics for multiple views
- More efficient than custom View for simple graphics without interaction
- Managed by Android system, no complex lifecycle needed

Related to concepts [[c-custom-views]], c-canvas-drawing, and [[c-lifecycle]].

### Drawable vs Custom View

| Feature | Drawable | Custom View |
|---------|----------|-------------|
| **Use case** | Simple graphics, icons | Interactive UI elements |
| **Performance** | Lightweight | Heavier (full View) |
| **Interaction** | No touch handling | Full touch support |
| **Lifecycle** | Simple | Complex (attach/detach) |
| **Reusability** | High | Lower |

**Use Drawable when:** non-interactive graphics, reusable across views, simple shapes/animations.

**Use Custom View when:** need touch interaction, complex lifecycle, accessibility requirements.

### Drawable Lifecycle
1. **Creation** - constructor or factory methods
2. **Bounds setting** - `setBounds()` defines drawing area
3. **Drawing** - `draw()` called by system
4. **State changes** - `setState()` for appearance updates
5. **Cleanup** - automatic memory management

### Key Methods to Override

**draw(canvas: Canvas)** - Main drawing method called by system for rendering

**setBounds()** - Sets drawing area boundaries, defines where and how big to draw

**getOpacity()** - Returns drawable transparency (PixelFormat.OPAQUE, TRANSLUCENT, TRANSPARENT)

**setAlpha(alpha: Int)** - Sets alpha channel for transparency

**setColorFilter(colorFilter: ColorFilter?)** - Applies color filter for tinting

### Minimal Implementation

```kotlin
class CircleDrawable : Drawable() {
    // ✅ Cache Paint - create once, reuse
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }

    var color: Int
        get() = paint.color
        set(value) {
            paint.color = value
            invalidateSelf() // ✅ Request redraw
        }

    override fun draw(canvas: Canvas) {
        val radius = min(bounds.width(), bounds.height()) / 2f
        canvas.drawCircle(
            bounds.centerX().toFloat(),
            bounds.centerY().toFloat(),
            radius, paint
        )
    }

    override fun setAlpha(alpha: Int) {
        paint.alpha = alpha
        invalidateSelf()
    }

    override fun setColorFilter(colorFilter: ColorFilter?) {
        paint.colorFilter = colorFilter
        invalidateSelf()
    }

    @Deprecated("Deprecated in Java")
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT
}
```

### State Management

```kotlin
class StatefulDrawable : Drawable() {
    private val paint = Paint()
    private var isPressed = false

    override fun draw(canvas: Canvas) {
        // ✅ Optimal: select color by state
        paint.color = if (isPressed) Color.RED else Color.BLUE
        canvas.drawRect(bounds, paint)
    }

    override fun setState(stateSet: IntArray): Boolean {
        val wasPressed = isPressed
        isPressed = stateSet.contains(android.R.attr.state_pressed)

        if (wasPressed != isPressed) {
            invalidateSelf()
            return true
        }
        return false
    }

    override fun isStateful(): Boolean = true
}
```

### Best Practices

1. **Use Paint.ANTI_ALIAS_FLAG** for smooth edges
2. **Cache Paint objects** - don't create in draw()
3. **Call invalidateSelf()** when appearance changes
4. **Implement intrinsic sizes** for proper layout
5. **Avoid complex calculations** in draw() - precompute

### Pitfalls

- **Don't create objects in draw()** - affects performance
- **Handle bounds correctly** - system may change them
- **Remember invalidateSelf()** on changes
- **Test on different sizes** - intrinsic sizes matter

---

## Follow-ups

- How to implement compound drawables using LayerDrawable or DrawableContainer?
- When should you use VectorDrawable instead of custom Drawable?
- How to handle density-independent sizing in custom Drawables?
- What are the performance implications of complex draw() operations?
- How to implement animated state transitions in Drawable?

## References

- [[c-custom-views]] - Custom View implementation patterns
- [[c-canvas-drawing]] - Canvas drawing fundamentals
- [[c-lifecycle]] - Android component lifecycle
- [Drawable API Reference](https://developer.android.com/reference/android/graphics/drawable/Drawable)
- [Custom Drawables Guide](https://developer.android.com/guide/topics/graphics/drawables)

## Related Questions

### Prerequisites
- [[q-canvas-drawing-basics--android--easy]] - Basic Canvas drawing operations
- [[q-paint-and-canvas-api--android--easy]] - Understanding Paint and Canvas

### Related
- [[q-custom-viewgroup-layout--android--hard]] - Custom ViewGroup implementation
- [[q-vector-drawable-usage--android--medium]] - VectorDrawable vs custom Drawable

### Advanced
- [[q-canvas-drawing-optimization--android--hard]] - Advanced Canvas optimization techniques
- [[q-hardware-acceleration-layers--android--hard]] - Hardware acceleration and layer types
