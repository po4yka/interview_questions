---
id: 20251021-180000
title: Custom View Lifecycle / Жизненный цикл Custom View
aliases:
  - Custom View Lifecycle
  - Жизненный цикл Custom View
topic: android
subtopics:
  - ui-views
  - lifecycle
question_kind: android
difficulty: medium
original_language: ru
language_tags:
  - ru
  - en
status: reviewed
moc: moc-android
related:
  - q-custom-view-implementation--android--medium
  - q-view-lifecycle-android--android--medium
  - q-android-performance-optimization--android--hard]
created: 2025-10-21
updated: 2025-10-21
tags:
  - android/ui-views
  - android/lifecycle
  - custom-views
  - lifecycle
  - performance
  - difficulty/medium
source: https://developer.android.com/guide/topics/ui/custom-components
source_note: Official custom components guide
---
# Вопрос (RU)
> Объясните жизненный цикл кастомного Android View. Какие методы вызываются и в каком порядке? Когда следует выполнять инициализацию, измерение, компоновку и отрисовку?

# Question (EN)
> Explain the lifecycle of a custom Android View. What methods are called and in what order? When should you perform initialization, measurement, layout, and drawing operations?

---

## Ответ (RU)

### Теория View Lifecycle

**View Lifecycle** состоит из нескольких ключевых фаз, каждая с определенной целью и временем выполнения. Понимание жизненного цикла критично для создания эффективных пользовательских UI компонентов.

**Ключевые принципы**:
- **Фазы выполняются последовательно** при первом создании View
- **Некоторые фазы могут повторяться** при изменениях (measure, layout, draw)
- **Каждая фаза имеет свою ответственность** и ограничения
- **Оптимизация производительности** требует правильного понимания фаз

### Основные фазы жизненного цикла

```
Constructor (once)
    ↓
onAttachedToWindow (once)
    ↓
onMeasure → onLayout → onDraw (can repeat)
    ↓           ↓         ↓
    └───────────┴─────────┘
                ↓
        onDetachedFromWindow (once)
```

### 1. Construction Phase - Создание

**Теория**: Конструктор вызывается при создании View из XML или программно. Это единственный раз, когда View получает Context и AttributeSet. Все ресурсы должны быть инициализированы здесь.

**Ключевые принципы**:
- **Единственный вызов** - конструктор вызывается только один раз
- **Инициализация ресурсов** - Paint объекты, атрибуты, настройки
- **Нет доступа к размерам** - width/height еще не известны
- **Нет анимаций** - View еще не прикреплен к Window

```kotlin
class CustomProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private val progressPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }

    private var progress = 0f

    init {
        // Читаем XML атрибуты
        context.theme.obtainStyledAttributes(
            attrs,
            R.styleable.CustomProgressBar,
            defStyleAttr,
            0
        ).apply {
            try {
                progress = getFloat(R.styleable.CustomProgressBar_progress, 0f)
                progressPaint.color = getColor(
                    R.styleable.CustomProgressBar_progressColor,
                    Color.BLUE
                )
            } finally {
                recycle()
            }
        }

        setWillNotDraw(false) // Важно для view, которые рисуют
    }
}
```

### 2. Attachment Phase - Прикрепление

**Теория**: onAttachedToWindow() вызывается когда View добавляется в иерархию и получает Window. Это место для запуска анимаций, регистрации listeners, и инициализации ресурсов, требующих Window.

**Ключевые принципы**:
- **Получение Window** - View теперь имеет доступ к Window
- **Запуск анимаций** - безопасно начинать анимации
- **Регистрация listeners** - подписка на системные события
- **Инициализация ресурсов** - создание объектов, требующих Context

```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()

    // Запускаем анимации
    startProgressAnimation()

    // Регистрируем listeners
    registerSystemListeners()

    // Инициализируем ресурсы
    initializeResources()
}

private fun startProgressAnimation() {
    // Анимация безопасна здесь
}

private fun registerSystemListeners() {
    // Подписка на системные события
}

private fun initializeResources() {
    // Создание ресурсов, требующих Window
}
```

### 3. Measurement Phase - Измерение

**Теория**: onMeasure() определяет размеры View на основе содержимого и ограничений родителя. Вызывается когда View нужно определить свои размеры. Может вызываться многократно.

**Ключевые принципы**:
- **Определение размеров** - View должен вычислить желаемые размеры
- **Учет ограничений** - размеры должны соответствовать MeasureSpec
- **Вызов setMeasuredDimension()** - обязательный вызов в конце
- **Может повторяться** - при изменениях layout

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    val desiredWidth = 200 // Желаемая ширина
    val desiredHeight = 100 // Желаемая высота

    val width = resolveSize(desiredWidth, widthMeasureSpec)
    val height = resolveSize(desiredHeight, heightMeasureSpec)

    setMeasuredDimension(width, height)
}

private fun resolveSize(desiredSize: Int, measureSpec: Int): Int {
    val specMode = MeasureSpec.getMode(measureSpec)
    val specSize = MeasureSpec.getSize(measureSpec)

    return when (specMode) {
        MeasureSpec.EXACTLY -> specSize
        MeasureSpec.AT_MOST -> min(desiredSize, specSize)
        MeasureSpec.UNSPECIFIED -> desiredSize
        else -> desiredSize
    }
}
```

### 4. Layout Phase - Компоновка

**Теория**: onLayout() вызывается после измерения для размещения View в заданных координатах. Определяет окончательное положение и размеры View. Вызывается когда изменяется layout.

**Ключевые принципы**:
- **Размещение View** - определение окончательного положения
- **Размеры известны** - width/height теперь доступны
- **Координаты заданы** - left, top, right, bottom установлены
- **Может повторяться** - при изменениях layout

```kotlin
override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
    super.onLayout(changed, left, top, right, bottom)

    if (changed) {
        // Layout изменился - обновляем внутренние компоненты
        updateInternalLayout()

        // Пересчитываем кэшированные значения
        recalculateCachedValues()
    }
}

private fun updateInternalLayout() {
    // Обновляем внутренние компоненты на основе новых размеров
}

private fun recalculateCachedValues() {
    // Пересчитываем кэшированные значения
}
```

### 5. Drawing Phase - Отрисовка

**Теория**: onDraw() вызывается для отрисовки View на Canvas. Это место где происходит фактическое рисование содержимого. Может вызываться очень часто.

**Ключевые принципы**:
- **Фактическое рисование** - отрисовка содержимого на Canvas
- **Частые вызовы** - может вызываться при каждом invalidate()
- **Оптимизация критична** - избегать создания объектов
- **Использовать кэширование** - предвычислять значения

```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // Рисуем фон
    canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), backgroundPaint)

    // Рисуем прогресс
    val progressWidth = width * (progress / 100f)
    canvas.drawRect(0f, 0f, progressWidth, height.toFloat(), progressPaint)

    // Рисуем текст
    if (showPercentage) {
        val text = "${progress.toInt()}%"
        canvas.drawText(text, width / 2f, height / 2f, textPaint)
    }
}
```

### 6. Detachment Phase - Отсоединение

**Теория**: onDetachedFromWindow() вызывается когда View удаляется из иерархии. Это место для очистки ресурсов, отмены анимаций, и отмены подписок.

**Ключевые принципы**:
- **Очистка ресурсов** - освобождение всех ресурсов
- **Отмена анимаций** - остановка всех анимаций
- **Отмена подписок** - отмена listeners и callbacks
- **Предотвращение memory leaks** - критично для производительности

```kotlin
override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()

    // Отменяем анимации
    cancelAnimations()

    // Отменяем подписки
    unregisterSystemListeners()

    // Очищаем ресурсы
    cleanupResources()
}

private fun cancelAnimations() {
    // Отмена всех анимаций
}

private fun unregisterSystemListeners() {
    // Отмена подписок на системные события
}

private fun cleanupResources() {
    // Очистка ресурсов
}
```

### Лучшие практики

1. **Инициализируйте ресурсы в конструкторе** - Paint объекты, атрибуты
2. **Запускайте анимации в onAttachedToWindow()** - безопасно для Window
3. **Оптимизируйте onDraw()** - избегайте создания объектов
4. **Очищайте ресурсы в onDetachedFromWindow()** - предотвращайте memory leaks
5. **Используйте кэширование** - предвычисляйте значения
6. **Правильно обрабатывайте изменения** - проверяйте changed параметры
7. **Тестируйте на слабых устройствах** - проверяйте производительность

### Подводные камни

- **Не создавайте объекты в onDraw()** - влияет на производительность
- **Не забывайте setMeasuredDimension()** - обязательный вызов в onMeasure()
- **Правильно очищайте ресурсы** - предотвращайте memory leaks
- **Не запускайте анимации в конструкторе** - View еще не прикреплен
- **Проверяйте changed параметры** - избегайте ненужных вычислений

---

## Answer (EN)

### View Lifecycle Theory

**View Lifecycle** consists of several key phases, each with a specific purpose and timing. Understanding the lifecycle is critical for building efficient custom UI components.

**Key principles**:
- **Phases execute sequentially** on first View creation
- **Some phases can repeat** on changes (measure, layout, draw)
- **Each phase has its responsibility** and limitations
- **Performance optimization** requires proper understanding of phases

### Main Lifecycle Phases

```
Constructor (once)
    ↓
onAttachedToWindow (once)
    ↓
onMeasure → onLayout → onDraw (can repeat)
    ↓           ↓         ↓
    └───────────┴─────────┘
                ↓
        onDetachedFromWindow (once)
```

### 1. Construction Phase

**Theory**: Constructor is called when View is created from XML or programmatically. This is the only time View receives Context and AttributeSet. All resources should be initialized here.

**Key principles**:
- **Single call** - constructor called only once
- **Resource initialization** - Paint objects, attributes, settings
- **No size access** - width/height not yet known
- **No animations** - View not yet attached to Window

```kotlin
class CustomProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private val progressPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }

    private var progress = 0f

    init {
        // Read XML attributes
        context.theme.obtainStyledAttributes(
            attrs,
            R.styleable.CustomProgressBar,
            defStyleAttr,
            0
        ).apply {
            try {
                progress = getFloat(R.styleable.CustomProgressBar_progress, 0f)
                progressPaint.color = getColor(
                    R.styleable.CustomProgressBar_progressColor,
                    Color.BLUE
                )
            } finally {
                recycle()
            }
        }

        setWillNotDraw(false) // Important for views that draw
    }
}
```

### 2. Attachment Phase

**Theory**: onAttachedToWindow() is called when View is added to hierarchy and receives Window. This is the place to start animations, register listeners, and initialize resources requiring Window.

**Key principles**:
- **Window access** - View now has access to Window
- **Start animations** - safe to begin animations
- **Register listeners** - subscribe to system events
- **Initialize resources** - create objects requiring Context

```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()

    // Start animations
    startProgressAnimation()

    // Register listeners
    registerSystemListeners()

    // Initialize resources
    initializeResources()
}

private fun startProgressAnimation() {
    // Animation is safe here
}

private fun registerSystemListeners() {
    // Subscribe to system events
}

private fun initializeResources() {
    // Create resources requiring Window
}
```

### 3. Measurement Phase

**Theory**: onMeasure() determines View dimensions based on content and parent constraints. Called when View needs to determine its size. Can be called multiple times.

**Key principles**:
- **Determine dimensions** - View must calculate desired size
- **Respect constraints** - dimensions must match MeasureSpec
- **Call setMeasuredDimension()** - mandatory call at the end
- **Can repeat** - on layout changes

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    val desiredWidth = 200 // Desired width
    val desiredHeight = 100 // Desired height

    val width = resolveSize(desiredWidth, widthMeasureSpec)
    val height = resolveSize(desiredHeight, heightMeasureSpec)

    setMeasuredDimension(width, height)
}

private fun resolveSize(desiredSize: Int, measureSpec: Int): Int {
    val specMode = MeasureSpec.getMode(measureSpec)
    val specSize = MeasureSpec.getSize(measureSpec)

    return when (specMode) {
        MeasureSpec.EXACTLY -> specSize
        MeasureSpec.AT_MOST -> min(desiredSize, specSize)
        MeasureSpec.UNSPECIFIED -> desiredSize
        else -> desiredSize
    }
}
```

### 4. Layout Phase

**Theory**: onLayout() is called after measurement to place View at given coordinates. Determines final position and size of View. Called when layout changes.

**Key principles**:
- **Place View** - determine final position
- **Sizes known** - width/height now available
- **Coordinates set** - left, top, right, bottom established
- **Can repeat** - on layout changes

```kotlin
override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
    super.onLayout(changed, left, top, right, bottom)

    if (changed) {
        // Layout changed - update internal components
        updateInternalLayout()

        // Recalculate cached values
        recalculateCachedValues()
    }
}

private fun updateInternalLayout() {
    // Update internal components based on new dimensions
}

private fun recalculateCachedValues() {
    // Recalculate cached values
}
```

### 5. Drawing Phase

**Theory**: onDraw() is called to draw View on Canvas. This is where actual content drawing happens. Can be called very frequently.

**Key principles**:
- **Actual drawing** - draw content on Canvas
- **Frequent calls** - can be called on every invalidate()
- **Optimization critical** - avoid object creation
- **Use caching** - precompute values

```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // Draw background
    canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), backgroundPaint)

    // Draw progress
    val progressWidth = width * (progress / 100f)
    canvas.drawRect(0f, 0f, progressWidth, height.toFloat(), progressPaint)

    // Draw text
    if (showPercentage) {
        val text = "${progress.toInt()}%"
        canvas.drawText(text, width / 2f, height / 2f, textPaint)
    }
}
```

### 6. Detachment Phase

**Theory**: onDetachedFromWindow() is called when View is removed from hierarchy. This is the place to clean up resources, cancel animations, and unsubscribe.

**Key principles**:
- **Clean up resources** - release all resources
- **Cancel animations** - stop all animations
- **Unsubscribe** - cancel listeners and callbacks
- **Prevent memory leaks** - critical for performance

```kotlin
override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()

    // Cancel animations
    cancelAnimations()

    // Unsubscribe
    unregisterSystemListeners()

    // Clean up resources
    cleanupResources()
}

private fun cancelAnimations() {
    // Cancel all animations
}

private fun unregisterSystemListeners() {
    // Cancel system event subscriptions
}

private fun cleanupResources() {
    // Clean up resources
}
```

### Best Practices

1. **Initialize resources in constructor** - Paint objects, attributes
2. **Start animations in onAttachedToWindow()** - safe for Window
3. **Optimize onDraw()** - avoid object creation
4. **Clean up resources in onDetachedFromWindow()** - prevent memory leaks
5. **Use caching** - precompute values
6. **Handle changes properly** - check changed parameters
7. **Test on weak devices** - verify performance

### Pitfalls

- **Don't create objects in onDraw()** - affects performance
- **Don't forget setMeasuredDimension()** - mandatory call in onMeasure()
- **Clean up resources properly** - prevent memory leaks
- **Don't start animations in constructor** - View not yet attached
- **Check changed parameters** - avoid unnecessary calculations

---

## Follow-ups

- How to handle configuration changes in custom views?
- What are the performance implications of each lifecycle phase?
- How to implement custom measurement logic?
- When to use onSizeChanged vs onLayout?

## References

- [Custom Components Guide](https://developer.android.com/guide/topics/ui/custom-components)
- [View Lifecycle Documentation](https://developer.android.com/reference/android/view/View)
