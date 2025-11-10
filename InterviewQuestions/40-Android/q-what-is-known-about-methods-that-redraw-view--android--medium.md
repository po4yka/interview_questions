---
id: android-135
title: What Is Known About Methods That Redraw View / Что известно о методах перерисовки View
aliases:
- Methods That Redraw View
- Методы перерисовки View
topic: android
subtopics:
- performance-rendering
- ui-graphics
- ui-views
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-performance
- q-handler-looper-main-thread--android--medium
created: 2023-10-15
updated: 2023-10-15
sources: []
tags:
- android/performance-rendering
- android/ui-graphics
- android/ui-views
- difficulty/medium
- postInvalidate
- rendering
- requestLayout
- ui
- views

---

# Вопрос (RU)

> Что известно про методы, которые перерисовывают `View`?

# Question (EN)

> What is known about methods that redraw `View`?

## Ответ (RU)

Android предоставляет три основных метода для обновления состояния `View` и запуска перерисовки/перелэйаута:

### 1. invalidate()

Помечает `View` (и при необходимости её родителей) как "грязную" для перерисовки. Это приводит к вызову `onDraw()` (и `draw()`) при следующем проходе отрисовки на UI-потоке. Используется, когда меняется только визуальное представление, но не размер и не позиция.

**Когда использовать:**
- Изменения цвета, текста
- Обновления состояния рисования
- Кадры анимации

```kotlin
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var color = Color.RED

    fun changeColor(newColor: Int) {
        color = newColor
        invalidate() // ✅ Помечает View для перерисовки (onDraw при следующем кадре)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawColor(color)
    }
}
```

**Характеристики:**
- Должен вызываться из UI-потока (main thread)
- Планирует вызов `onDraw()` при следующем кадре
- НЕ инициирует `onMeasure()` или `onLayout()`

### 2. requestLayout()

Помечает `View` и её предков как требующие переразмещения. В следующем layout-проходе это может привести к вызову `onMeasure()` и `onLayout()`. Используется, когда изменяются размеры или потенциально позиция `View`.

**Когда использовать:**
- Изменения размера
- Изменения padding (и других параметров, влияющих на размер)
- Изменения `LayoutParams`
- Добавление/удаление дочерних `View`

```kotlin
class ExpandableView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : ViewGroup(context, attrs, defStyleAttr) {

    private var isExpanded = false

    fun toggle() {
        isExpanded = !isExpanded
        requestLayout() // ✅ Запрашивает новый layout-проход
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val desiredHeight = if (isExpanded) 400.dp else 100.dp
        val width = MeasureSpec.getSize(widthMeasureSpec)
        setMeasuredDimension(width, desiredHeight)
    }

    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
        // Реальное размещение дочерних View опущено для краткости
    }
}
```

Важно: `requestLayout()` отвечает за измерение и размещение. Если при этом также меняется внешний вид (например, цвет, контент), может понадобиться дополнительно вызвать `invalidate()`.

### 3. postInvalidate()

Вариант `invalidate()`, предназначенный для безопасного вызова из не-UI потоков. Он публикует запрос на перерисовку в очередь сообщений UI-потока, где затем произойдёт обычная invalidation. Это не "общая" потокобезопасность, а именно безопасный мост к main thread.

**Когда использовать:**
- Обновления из фоновых потоков
- Когда нельзя гарантировать выполнение кода на UI-потоке

```kotlin
class LoadingView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var progress = 0

    fun startLoading() {
        Thread {
            while (progress < 100) {
                Thread.sleep(100)
                progress += 10
                postInvalidate() // ✅ Безопасно вызывать из background thread
                // invalidate() // ❌ Может привести к исключению, если вызвать не с UI-потока
            }
        }.start()
    }
}
```

### Сравнение Методов

| Метод | Поток вызова | Что делает | Использование |
|-------|--------------|-----------|---------------|
| `invalidate()` | UI | Помечает для перерисовки (`onDraw()` при следующем кадре) | Визуальные изменения |
| `requestLayout()` | Обычно UI | Помечает для нового измерения/размещения (`onMeasure()`, `onLayout()` в layout-проходе) | Изменения размера/позиции |
| `postInvalidate()` | Любой | Планирует `invalidate()` на UI-потоке | Запросы из фоновых потоков |

### Лучшие Практики

1. `invalidate()` — для визуальных изменений без изменения размеров/позиции.
2. `requestLayout()` — когда изменение затрагивает размеры или может повлиять на layout.
3. `postInvalidate()` — для запуска перерисовки из не-UI потоков.
4. Группируйте обновления, чтобы избежать лишних проходов layout/draw.
5. Осторожно с вызовами в жёстких циклах: частые `invalidate()`/`requestLayout()` допустимы для анимаций, но должны быть осознанными и по возможности батчиться, чтобы не перегружать rendering-пайплайн.
6. Если меняются и размеры, и внешний вид, при необходимости комбинируйте `requestLayout()` и `invalidate()`.

```kotlin
// ✅ Правильно: группировка обновлений
fun updateMultiple() {
    color = Color.RED
    size = 100
    requestLayout()   // Запрос нового layout
    invalidate()      // Явный запрос перерисовки, если отрисовка тоже изменилась
}

// ❌ Неправильно: лишние/нескоординированные вызовы
fun updateSeparately() {
    color = Color.RED
    invalidate()      // Может быть лишним, если далее всё равно будет layout + перерисовка
    size = 100
    requestLayout()   // Второй вызов, без учёта предыдущего
}
```

## Дополнительные вопросы (RU)

- Что произойдет, если вызвать `invalidate()` из фонового потока?
- Когда следует вызывать одновременно `requestLayout()` и `invalidate()`?
- Как распространяется invalidation `View` вверх по иерархии `View`?
- В чем разница между `forceLayout()` и `requestLayout()`?
- Как оптимизировать множественные обновления `View` в кастомном `ViewGroup`?

## Ссылки (RU)

- Официальная документация Android по отрисовке, invalidation и layout для `View`

## Связанные вопросы (RU)

### Предварительные знания / Концепции

- [[c-performance]]

### Предварительные знания

- Базовое понимание жизненного цикла `View` (`onMeasure`, `onLayout`, `onDraw`)
- Знание UI-потока Android и главного looper

### Связанные

- [[q-handler-looper-main-thread--android--medium]] — UI-поток и обработка сообщений
- Пайплайн отрисовки и прорисовки кастомных `View` в Android
- Операции рисования на `Canvas` в Android

### Продвинутое

- Техники оптимизации производительности `View`
- Продвинутые сценарии измерения и размещения в `ViewGroup`

## Answer (EN)

Android provides three primary methods to update `View` state and trigger redraw/layout passes:

### 1. invalidate()

Marks the `View` (and, if needed, its parents) as "dirty" for redrawing. This results in `onDraw()` (and `draw()`) being called on the next rendering pass on the UI thread. Use it when only the visual appearance changes and not the size or position.

**When to use:**
- Color changes
- Text/content updates that do not affect layout
- Drawing state changes
- Animation frames

```kotlin
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var color = Color.RED

    fun changeColor(newColor: Int) {
        color = newColor
        invalidate() // ✅ Schedules redraw (onDraw on the next frame)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawColor(color)
    }
}
```

**Characteristics:**
- Must be called from the UI (main) thread
- Schedules `onDraw()` for the next frame
- Does NOT trigger `onMeasure()` or `onLayout()`

### 2. requestLayout()

Marks the `View` and its ancestors as needing a new layout pass. During the next layout, `onMeasure()` and `onLayout()` may be called. Use it when dimensions or layout-relevant properties change.

**When to use:**
- Size changes
- Padding changes (and other properties affecting size)
- Changes to `LayoutParams`
- Adding/removing child Views

```kotlin
class ExpandableView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : ViewGroup(context, attrs, defStyleAttr) {

    private var isExpanded = false

    fun toggle() {
        isExpanded = !isExpanded
        requestLayout() // ✅ Requests a new layout pass
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val desiredHeight = if (isExpanded) 400.dp else 100.dp
        val width = MeasureSpec.getSize(widthMeasureSpec)
        setMeasuredDimension(width, desiredHeight)
    }

    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
        // Actual child layout omitted for brevity
    }
}
```

Note: `requestLayout()` is responsible for measurement and layout. If the visual appearance also changes (e.g., colors, custom drawing), you may additionally need `invalidate()`.

### 3. postInvalidate()

A variant of `invalidate()` intended for safe use from non-UI threads. It posts an invalidation request to the UI thread's message queue, where a regular `invalidate()`/draw pass will occur. It is not a general synchronization mechanism but a safe bridge to the main thread for redraw requests.

**When to use:**
- Updates initiated from background threads
- When you cannot guarantee execution on the UI thread

```kotlin
class LoadingView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var progress = 0

    fun startLoading() {
        Thread {
            while (progress < 100) {
                Thread.sleep(100)
                progress += 10
                postInvalidate() // ✅ Safe from a background thread
                // invalidate() // ❌ May throw if called off the UI thread
            }
        }.start()
    }
}
```

### Method Comparison

| Method | Calling thread | What it does | Use case |
|--------|----------------|--------------|----------|
| `invalidate()` | UI | Marks for redraw (`onDraw()` on next frame) | Visual-only changes |
| `requestLayout()` | Typically UI | Marks for re-measure/layout (`onMeasure()`, `onLayout()` in layout pass) | Size/position/layout changes |
| `postInvalidate()` | Any | Schedules `invalidate()` on UI thread | Requests from background threads |

### Best Practices

1. Use `invalidate()` for visual changes that do not affect layout.
2. Use `requestLayout()` when size or layout-related properties change.
3. Use `postInvalidate()` when triggering a redraw from a background thread.
4. Batch updates to minimize redundant layout and draw passes.
5. Be cautious with calls inside tight loops: frequent invalidations/layouts are expected for animations but should be intentional and optimized to avoid overloading the rendering pipeline.
6. When both size and appearance change, combine `requestLayout()` and `invalidate()` as needed.

```kotlin
// ✅ Correct: batched and explicit updates
fun updateMultiple() {
    color = Color.RED
    size = 100
    requestLayout()   // Request new layout
    invalidate()      // Ensure visual changes are redrawn
}

// ❌ Wrong: redundant/uncoordinated calls
fun updateSeparately() {
    color = Color.RED
    invalidate()      // Potentially redundant if another pass is imminent
    size = 100
    requestLayout()   // Second separate request
}
```

---

## Follow-ups

- What happens if you call `invalidate()` from a background thread?
- When should you call both `requestLayout()` and `invalidate()`?
- How does `View` invalidation propagate up the `View` hierarchy?
- What is the difference between `forceLayout()` and `requestLayout()`?
- How can you optimize multiple `View` updates in a custom `ViewGroup`?

## References

- Android Documentation: `View` rendering, invalidation and layout

## Related Questions

### Prerequisites / Concepts

- [[c-performance]]

### Prerequisites

- Basic understanding of `View` lifecycle (`onMeasure`, `onLayout`, `onDraw`)
- Knowledge of Android UI thread and main looper

### Related

- [[q-handler-looper-main-thread--android--medium]] — UI thread and message handling
- Custom `View` rendering pipeline and drawing process
- Canvas drawing operations in Android

### Advanced

- `View` performance optimization techniques
- Advanced `ViewGroup` layout and measure passes
