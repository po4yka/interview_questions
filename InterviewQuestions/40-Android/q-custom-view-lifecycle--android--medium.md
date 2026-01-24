---
id: android-479
title: Custom View Lifecycle / Жизненный цикл Custom View
aliases:
- Custom View Lifecycle
- Жизненный цикл Custom View
topic: android
subtopics:
- lifecycle
- ui-graphics
- ui-views
question_kind: android
difficulty: medium
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android-view-system
- q-custom-view-attributes--android--medium
- q-custom-view-state-saving--android--medium
- q-what-is-known-about-view-lifecycles--android--medium
created: 2025-10-21
updated: 2025-11-11
tags:
- android/lifecycle
- android/ui-graphics
- android/ui-views
- custom-views
- difficulty/medium
sources: []
anki_cards:
- slug: android-479-0-en
  language: en
  anki_id: 1768366343375
  synced_at: '2026-01-23T16:45:05.842103'
- slug: android-479-0-ru
  language: ru
  anki_id: 1768366343401
  synced_at: '2026-01-23T16:45:05.843381'
---
# Вопрос (RU)
> Каков жизненный цикл Custom `View` в Android? Какие методы вызываются при создании, отрисовке и удалении `View`?

# Question (EN)
> What is the Custom `View` lifecycle in Android? Which methods are called during view creation, drawing, and removal?

---

## Ответ (RU)

**`View` `Lifecycle`** описывает ключевые этапы от создания до удаления `View`. Упрощенная типичная последовательность для уже добавленной в иерархию `View` выглядит так:

```text
Constructor → onAttachedToWindow → onMeasure → onLayout → onSizeChanged (при изменении размеров) → onDraw → onDetachedFromWindow
```

Важно: `onMeasure`, `onLayout` и `onDraw` могут вызываться многократно в течение жизни `View`. `onAttachedToWindow`/`onDetachedFromWindow` связаны с присоединением к окну, а не с каждым циклом измерения/отрисовки.

### Фазы Жизненного Цикла

#### 1. Constructor — Инициализация

`View` создается, но еще не присоединена к окну. Размеры неизвестны.

**Действия**: инициализация `Paint`, чтение атрибутов XML, подготовка статических ресурсов.

```kotlin
class CustomProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLUE  // ✅ Инициализация в конструкторе
    }

    init {
        // Для View, переопределяющих onDraw, setWillNotDraw(false) вызывать не обязательно.
        // setWillNotDraw(false) нужно в основном для ViewGroup, если вы хотите что-то рисовать.

        attrs?.let {
            context.obtainStyledAttributes(it, R.styleable.CustomProgressBar).apply {
                paint.color = getColor(R.styleable.CustomProgressBar_color, Color.BLUE)
                recycle()  // ✅ Освобождение TypedArray
            }
        }
    }
}
```

#### 2. onAttachedToWindow — Присоединение К Окну

`View` добавлена в иерархию и присоединена к окну. Здесь безопасно запускать анимации, регистрировать listeners, подписки и т.п.

```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()
    animator?.start()  // ✅ Безопасно запускать анимации
}

override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()
    animator?.cancel()  // ✅ Очистка и остановка анимаций/подписок
}
```

#### 3. onMeasure — Измерение Размеров

Вызывается многократно. **Обязательно** установить размеры через `setMeasuredDimension()` (либо вызвать реализацию суперкласса, которая это делает), с учетом `MeasureSpec`.

```kotlin
override fun onMeasure(widthSpec: Int, heightSpec: Int) {
    val desiredWidth = 200
    val desiredHeight = 100

    val width = resolveSize(desiredWidth, widthSpec)   // ✅ Учет MeasureSpec
    val height = resolveSize(desiredHeight, heightSpec)

    setMeasuredDimension(width, height)  // ✅ Обязательный вызов в кастомной реализации
}
```

#### 4. onLayout — Позиционирование (для `ViewGroup`)

Для простых наследников `View` не требуется. В `ViewGroup` используется для размещения потомков и может вызываться многократно.

#### 5. onSizeChanged — Реакция На Изменение Размеров

Вызывается после того, как размер `View` был вычислен или изменился. Удобное место для пересчета геометрии, кэшированных путей, шейдеров и т.п., если они зависят от ширины/высоты.

#### 6. onDraw — Отрисовка

Вызывается часто (каждый кадр при необходимости перерисовки). **Критично для производительности**: избегать лишних аллокаций и тяжелых операций внутри.

```kotlin
// ❌ НЕЖЕЛАТЕЛЬНО
override fun onDraw(canvas: Canvas) {
    val paint = Paint()  // Лишнее выделение памяти каждый кадр
    canvas.drawCircle(width / 2f, height / 2f, 50f, paint)
}

// ✅ ПРАВИЛЬНО
private val paint = Paint()

override fun onDraw(canvas: Canvas) {
    canvas.drawCircle(width / 2f, height / 2f, 50f, paint)
}
```

### Ключевые Правила

1. **Constructor**: инициализация `Paint`, атрибутов и ресурсов; не использовать размеры `View`.
2. **onAttachedToWindow**: запуск анимаций, регистрация listeners/подписок.
3. **onMeasure**: всегда корректно задавать размеры (`setMeasuredDimension()` или super-реализация).
4. **onLayout** (для `ViewGroup`): размещать дочерние `View`.
5. **onSizeChanged**: пересчет зависящей от размеров геометрии и данных.
6. **onDraw**: минимизировать создание объектов и тяжелые операции в hot path.
7. **onDetachedFromWindow**: остановить анимации, отписаться от listeners, освободить ресурсы.

### Оптимизация Производительности

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

**`View` `Lifecycle`** describes the key stages from creation to removal of a `View`. A simplified typical sequence for a `View` already added to a hierarchy looks like:

```text
Constructor → onAttachedToWindow → onMeasure → onLayout → onSizeChanged (when size changes) → onDraw → onDetachedFromWindow
```

Note: `onMeasure`, `onLayout`, and `onDraw` can be called many times during the `View`'s lifetime. `onAttachedToWindow` / `onDetachedFromWindow` are tied to window attachment, not to each measure/draw pass.

### Lifecycle Phases

#### 1. Constructor — Initialization

`View` is created but not yet attached to a window. Dimensions are unknown.

**Actions**: initialize `Paint`, read XML attributes, prepare static resources.

```kotlin
class CustomProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLUE  // ✅ Initialize in constructor
    }

    init {
        // For View subclasses that override onDraw, setWillNotDraw(false) is not required.
        // It's mainly needed for ViewGroup when you want it to perform drawing.

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

`View` has been added to the hierarchy and attached to the window. It is safe to start animations, register listeners, subscribe to data sources, etc.

```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()
    animator?.start()  // ✅ Safe to start animations
}

override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()
    animator?.cancel()  // ✅ Cleanup and stop animations/subscriptions
}
```

#### 3. onMeasure — Measure Dimensions

Called multiple times. You **must** set dimensions via `setMeasuredDimension()` (or rely on the super implementation that does so), respecting the incoming `MeasureSpec`.

```kotlin
override fun onMeasure(widthSpec: Int, heightSpec: Int) {
    val desiredWidth = 200
    val desiredHeight = 100

    val width = resolveSize(desiredWidth, widthSpec)   // ✅ Respect MeasureSpec
    val height = resolveSize(desiredHeight, heightSpec)

    setMeasuredDimension(width, height)  // ✅ Required in a custom implementation
}
```

#### 4. onLayout — Positioning (for `ViewGroup`)

Not required for simple `View` subclasses. `ViewGroup` uses it to position child views and it may be called multiple times.

#### 5. onSizeChanged — Size Change Handling

Called after the `View`'s size has been determined or changed. A good place to recompute geometry, paths, shaders, etc., that depend on `width`/`height`.

#### 6. onDraw — Drawing

Called frequently (every frame when a redraw is needed). **Performance critical**: avoid unnecessary allocations and heavy work in this hot path.

```kotlin
// ❌ NOT RECOMMENDED
override fun onDraw(canvas: Canvas) {
    val paint = Paint()  // Extra allocation every frame
    canvas.drawCircle(width / 2f, height / 2f, 50f, paint)
}

// ✅ CORRECT
private val paint = Paint()

override fun onDraw(canvas: Canvas) {
    canvas.drawCircle(width / 2f, height / 2f, 50f, paint)
}
```

### Key Rules

1. **Constructor**: initialize `Paint`, attributes, and resources; do not rely on `View` dimensions.
2. **onAttachedToWindow**: start animations, register listeners/subscriptions.
3. **onMeasure**: always provide correct dimensions (`setMeasuredDimension()` or super implementation).
4. **onLayout** (for `ViewGroup`): position child views.
5. **onSizeChanged**: recompute any size-dependent geometry/data.
6. **onDraw**: minimize object allocations and heavy work in the drawing hot path.
7. **onDetachedFromWindow**: stop animations, unregister listeners, release resources.

### Performance Optimization

```kotlin
class OptimizedCustomView(context: Context, attrs: AttributeSet?) : View(context, attrs) {

    // ✅ Reusable objects
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val rect = RectF()

    override fun onDraw(canvas: Canvas) {
        // ✅ Reuse rect instead of creating a new one
        rect.set(0f, 0f, width.toFloat(), height.toFloat())
        canvas.drawRect(rect, paint)
    }
}
```

---

## Дополнительные Вопросы (RU)

- Что произойдет, если забыть вызвать `setMeasuredDimension()` в `onMeasure`?
- Чем `invalidate()` отличается от `requestLayout()` и когда использовать каждый из них?
- Почему выделение объектов в `onDraw` проблематично, даже с современными сборщиками мусора?
- Как сохранять и восстанавливать состояние кастомной `View` при изменении конфигурации?
- Какова роль `onSizeChanged()` и когда он вызывается относительно `onMeasure`/`onLayout`?

## Follow-ups

- What happens if you forget to call `setMeasuredDimension()` in onMeasure?
- How does `invalidate()` differ from `requestLayout()` and when should each be used?
- Why is object allocation in onDraw problematic even with modern garbage collectors?
- How do you save and restore custom view state during configuration changes?
- What is the role of `onSizeChanged()` and when is it called relative to onMeasure/onLayout?

## Ссылки (RU)

- [[c-android-view-system]]
- https://developer.android.com/guide/topics/ui/custom-components
- https://developer.android.com/reference/android/view/View

## References

- [[c-android-view-system]]
- https://developer.android.com/guide/topics/ui/custom-components
- https://developer.android.com/reference/android/view/View

## Связанные Вопросы (RU)

### База (проще)

### Связанные (тот Же уровень)
- [[q-custom-view-state-saving--android--medium]]

### Продвинутое (сложнее)
- [[q-custom-viewgroup-layout--android--hard]]

## Related Questions

### Prerequisites (Easier)

### Related (Same Level)
- [[q-custom-view-state-saving--android--medium]]

### Advanced (Harder)
- [[q-custom-viewgroup-layout--android--hard]]
