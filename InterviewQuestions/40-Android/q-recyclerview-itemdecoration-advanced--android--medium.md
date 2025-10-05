---
id: q-recyclerview-itemdecoration-advanced--android--medium--1728115320000
title: "RecyclerView ItemDecoration Advanced / RecyclerView ItemDecoration продвинутый"
aliases:
  - RecyclerView ItemDecoration Advanced
  - RecyclerView ItemDecoration продвинутый
date_created: 2025-10-05
date_modified: 2025-10-05
status: draft
original_language: en
language_tags:
  - en
  - ru
type: question
category: android
difficulty: medium
subtopics:
  - ui-views
  - ui-widgets
  - performance-rendering
tags:
  - android
  - recyclerview
  - itemdecoration
  - ui
  - custom-views
  - difficulty/medium
moc: moc-android
source: "https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20do%20you%20know%20about%20RecyclerView%20ItemDecoration.md"
---

# RecyclerView ItemDecoration Advanced / RecyclerView ItemDecoration продвинутый

## EN

### Question

What do you know about RecyclerView ItemDecoration?

### Answer

An ItemDecoration allows the application to add a special drawing and layout offset to specific item views from the adapter's data set. This can be useful for drawing dividers between items, highlights, visual grouping boundaries and more.

All ItemDecorations are drawn in the order they were added, before the item views (in `onDraw()`) and after the items (in `onDrawOver(Canvas, RecyclerView, RecyclerView.State)`).

Multiple ItemDecorations can be added to a single `RecyclerView`.

### Examples of ItemDecoration

#### ItemDecoration for top and bottom margins

```kotlin
import android.graphics.Rect
import android.view.View
import androidx.recyclerview.widget.RecyclerView

class TopBottomMarginItemDecoration(
    private val topMargin: Int,
    private val bottomMargin: Int
) : RecyclerView.ItemDecoration() {

    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        with(outRect) {
            top = topMargin
            bottom = bottomMargin
        }
    }
}
```

#### ItemDecoration for right and left margins

```kotlin
import android.graphics.Rect
import android.view.View
import androidx.recyclerview.widget.RecyclerView

class EdgesMarginItemDecoration(private val edgesMargin: Int) : RecyclerView.ItemDecoration() {

    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        with(outRect) {
            val position = parent.getChildAdapterPosition(view)
            when (position) {
                0 -> {
                    left = edgesMargin
                    right = edgesMargin / 2
                }
                parent.adapter!!.itemCount - 1 -> {
                    right = edgesMargin
                    left = edgesMargin / 2
                }
                else -> {
                    left = edgesMargin / 2
                    right = edgesMargin / 2
                }
            }
        }
    }
}
```

### Key Methods

The main methods you can override in ItemDecoration are:

1. **`getItemOffsets()`** - Used to add spacing/padding around items
2. **`onDraw()`** - Called before the item views are drawn (draw behind items)
3. **`onDrawOver()`** - Called after the item views are drawn (draw on top of items)

### Use Cases

ItemDecoration is commonly used for:

- Adding dividers between list items
- Adding spacing/margins around items
- Drawing backgrounds or borders
- Creating visual grouping boundaries
- Adding headers or section dividers
- Drawing custom decorations or overlays

---

## RU

### Вопрос

Что вы знаете о RecyclerView ItemDecoration?

### Ответ

ItemDecoration позволяет приложению добавлять специальную отрисовку и смещение макета к конкретным представлениям элементов из набора данных адаптера. Это может быть полезно для рисования разделителей между элементами, выделений, границ визуального группирования и многого другого.

Все ItemDecoration отрисовываются в порядке их добавления, перед представлениями элементов (в `onDraw()`) и после элементов (в `onDrawOver(Canvas, RecyclerView, RecyclerView.State)`).

К одному `RecyclerView` можно добавить несколько ItemDecoration.

### Примеры ItemDecoration

#### ItemDecoration для верхних и нижних отступов

```kotlin
import android.graphics.Rect
import android.view.View
import androidx.recyclerview.widget.RecyclerView

class TopBottomMarginItemDecoration(
    private val topMargin: Int,
    private val bottomMargin: Int
) : RecyclerView.ItemDecoration() {

    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        with(outRect) {
            top = topMargin
            bottom = bottomMargin
        }
    }
}
```

#### ItemDecoration для правых и левых отступов

```kotlin
import android.graphics.Rect
import android.view.View
import androidx.recyclerview.widget.RecyclerView

class EdgesMarginItemDecoration(private val edgesMargin: Int) : RecyclerView.ItemDecoration() {

    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        with(outRect) {
            val position = parent.getChildAdapterPosition(view)
            when (position) {
                0 -> {
                    left = edgesMargin
                    right = edgesMargin / 2
                }
                parent.adapter!!.itemCount - 1 -> {
                    right = edgesMargin
                    left = edgesMargin / 2
                }
                else -> {
                    left = edgesMargin / 2
                    right = edgesMargin / 2
                }
            }
        }
    }
}
```

### Основные методы

Основные методы, которые вы можете переопределить в ItemDecoration:

1. **`getItemOffsets()`** - Используется для добавления интервалов/отступов вокруг элементов
2. **`onDraw()`** - Вызывается перед отрисовкой представлений элементов (рисование за элементами)
3. **`onDrawOver()`** - Вызывается после отрисовки представлений элементов (рисование поверх элементов)

### Варианты использования

ItemDecoration обычно используется для:

- Добавления разделителей между элементами списка
- Добавления интервалов/отступов вокруг элементов
- Рисования фонов или границ
- Создания границ визуального группирования
- Добавления заголовков или разделителей секций
- Рисования пользовательских декораций или наложений
