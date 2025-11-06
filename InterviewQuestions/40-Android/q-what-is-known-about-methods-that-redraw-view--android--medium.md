---
id: android-135
title: What Is Known About Methods That Redraw View / Что известно о методах перерисовывающих
  View
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
created: 2025-10-15
updated: 2025-01-27
sources: []
tags:
- android
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

Что известно про методы, которые перерисовывают `View`?

# Question (EN)

What is known about methods that redraw `View`?

## Ответ (RU)

Android предоставляет три основных метода для перерисовки `View`:

### 1. invalidate()

Помечает `View` для перерисовки через вызов `onDraw()`. Используется когда изменяется только визуальный вид, но размер остаётся прежним.

**Когда использовать:**
- Изменения цвета, текста
- Обновления состояния рисования
- Кадры анимации

```kotlin
class CustomView : View {
    private var color = Color.RED

    fun changeColor(newColor: Int) {
        color = newColor
        invalidate() // ✅ Вызывает только onDraw()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawColor(color)
    }
}
```

**Характеристики:**
- Вызывается только из UI потока
- Вызывает `onDraw()`
- НЕ вызывает `onMeasure()` или `onLayout()`

### 2. requestLayout()

Запускает полный цикл layout через вызов `onMeasure()` и `onLayout()`. Используется когда изменяются размеры или позиция `View`.

**Когда использовать:**
- Изменения размера
- Изменения margin/padding
- Изменения LayoutParams
- Добавление/удаление дочерних `View`

```kotlin
class ExpandableView : ViewGroup {
    private var isExpanded = false

    fun toggle() {
        isExpanded = !isExpanded
        requestLayout() // ✅ Пересчитывает размеры
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val height = if (isExpanded) 400.dp else 100.dp
        setMeasuredDimension(
            MeasureSpec.getSize(widthMeasureSpec),
            height
        )
    }
}
```

### 3. postInvalidate()

Потокобезопасная версия `invalidate()` для вызова из фоновых потоков. Отправляет запрос на перерисовку в UI поток.

**Когда использовать:**
- Обновления из фоновых потоков
- Когда невозможно гарантировать выполнение на UI потоке

```kotlin
class LoadingView : View {
    private var progress = 0

    fun startLoading() {
        Thread {
            while (progress < 100) {
                Thread.sleep(100)
                progress += 10
                postInvalidate() // ✅ Безопасно из любого потока
                // invalidate() // ❌ Крашнется из background thread
            }
        }.start()
    }
}
```

### Сравнение Методов

| Метод | Поток | Вызывает | Использование |
|-------|-------|----------|---------------|
| `invalidate()` | UI | `onDraw()` | Визуальные изменения |
| `requestLayout()` | UI | `onMeasure()`, `onLayout()` | Изменения размера/позиции |
| `postInvalidate()` | Любой | `onDraw()` (на UI) | Из фоновых потоков |

### Лучшие Практики

1. **invalidate()** — только для визуальных изменений
2. **requestLayout()** — когда размер/позиция меняются
3. **postInvalidate()** — из фоновых потоков
4. Группируйте обновления чтобы избежать множественных перерисовок
5. Избегайте вызовов в циклах — эти методы дорогие

```kotlin
// ✅ Правильно: группировка обновлений
fun updateMultiple() {
    color = Color.RED
    size = 100
    requestLayout() // Один вызов для всех изменений
}

// ❌ Неправильно: множественные вызовы
fun updateSeparately() {
    color = Color.RED
    invalidate() // Лишний вызов
    size = 100
    requestLayout() // Второй вызов
}
```

## Answer (EN)

Android provides three primary methods to trigger `View` redrawing and layout recalculation:

### 1. invalidate()

Marks the `View` for redrawing by calling `onDraw()`. Use when visual appearance changes but size remains the same.

**When to use:**
- Color changes
- Text updates
- Drawing state changes
- Animation frames

```kotlin
class CustomView : View {
    private var color = Color.RED

    fun changeColor(newColor: Int) {
        color = newColor
        invalidate() // ✅ Calls only onDraw()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawColor(color)
    }
}
```

**Characteristics:**
- Must be called from UI thread
- Triggers `onDraw()`
- Does NOT trigger `onMeasure()` or `onLayout()`

### 2. requestLayout()

Triggers full layout pass by calling `onMeasure()` and `onLayout()`. Use when `View` dimensions change.

**When to use:**
- Size changes
- Margin/padding changes
- LayoutParams changes
- Adding/removing child Views

```kotlin
class ExpandableView : ViewGroup {
    private var isExpanded = false

    fun toggle() {
        isExpanded = !isExpanded
        requestLayout() // ✅ Recalculates dimensions
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val height = if (isExpanded) 400.dp else 100.dp
        setMeasuredDimension(
            MeasureSpec.getSize(widthMeasureSpec),
            height
        )
    }
}
```

### 3. postInvalidate()

`Thread`-safe version of `invalidate()` for calling from background threads. Posts invalidation request to UI thread.

**When to use:**
- Updates from background threads
- When UI thread execution cannot be guaranteed

```kotlin
class LoadingView : View {
    private var progress = 0

    fun startLoading() {
        Thread {
            while (progress < 100) {
                Thread.sleep(100)
                progress += 10
                postInvalidate() // ✅ Safe from any thread
                // invalidate() // ❌ Will crash from background thread
            }
        }.start()
    }
}
```

### Method Comparison

| Method | `Thread` | Calls | Use Case |
|--------|--------|-------|----------|
| `invalidate()` | UI | `onDraw()` | Visual changes |
| `requestLayout()` | UI | `onMeasure()`, `onLayout()` | Size/position changes |
| `postInvalidate()` | Any | `onDraw()` (on UI) | From background threads |

### Best Practices

1. **invalidate()** — visual changes only
2. **requestLayout()** — when size/position changes
3. **postInvalidate()** — from background threads
4. Batch updates to avoid multiple redraws
5. Avoid calling in loops — these methods are expensive

```kotlin
// ✅ Correct: batched updates
fun updateMultiple() {
    color = Color.RED
    size = 100
    requestLayout() // Single call for all changes
}

// ❌ Wrong: multiple calls
fun updateSeparately() {
    color = Color.RED
    invalidate() // Unnecessary call
    size = 100
    requestLayout() // Second call
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

- Android Documentation: `View` Rendering
- Android Source: `View`.java invalidate/requestLayout implementation

## Related Questions

### Prerequisites / Concepts

- [[c-performance]]


### Prerequisites
- Basic understanding of `View` lifecycle (onMeasure, onLayout, onDraw)
- Knowledge of Android UI thread and main looper

### Related
- [[q-handler-looper-main-thread--android--medium]] — UI thread and message handling
- Custom `View` rendering pipeline and drawing process
- `Canvas` drawing operations in Android

### Advanced
- `View` performance optimization techniques
- Advanced `ViewGroup` layout and measure passes
