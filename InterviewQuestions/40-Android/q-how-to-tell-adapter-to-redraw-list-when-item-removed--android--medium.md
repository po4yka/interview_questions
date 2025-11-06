---
id: android-374
title: How To Tell Adapter To Redraw List When Item Removed / Как сказать адаптеру
  перерисовать список когда элемент удален
aliases:
- How To Tell Adapter To Redraw List
- Как сказать адаптеру перерисовать список
topic: android
subtopics:
- ui-animation
- ui-views
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-custom-views
- q-how-to-create-list-like-recyclerview-in-compose--android--medium
- q-recyclerview-sethasfixedsize--android--easy
created: 2025-10-15
updated: 2025-10-31
sources: []
tags:
- adapter
- android/ui-animation
- android/ui-views
- difficulty/medium
- diffutil
- recyclerview
date created: Tuesday, October 28th 2025, 9:11:31 pm
date modified: Saturday, November 1st 2025, 5:43:35 pm
---

# Вопрос (RU)

> Как правильно сообщить адаптеру RecyclerView о том, что элемент был удален из списка?

# Question (EN)

> How to tell a RecyclerView adapter that an item has been removed from the list?

---

## Ответ (RU)

Когда элемент удаляется из списка, необходимо: (1) удалить его из источника данных, (2) уведомить адаптер о конкретном изменении через специализированные notify методы.

### Основные Подходы

```kotlin
class MyAdapter(private val items: MutableList<Item>) :
    RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    // ❌ Обновляет весь список, нет анимаций
    fun removeItemBad(position: Int) {
        items.removeAt(position)
        notifyDataSetChanged() // Неэффективно!
    }

    // ✅ Обновляет только затронутый элемент
    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)
    }

    // ✅ Дополнительно обновляет позиции
    fun removeItemWithRange(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)
        notifyItemRangeChanged(position, items.size)
    }
}
```

### DiffUtil С ListAdapter (рекомендуется)

```kotlin
class MyAdapter : ListAdapter<Item, MyAdapter.ViewHolder>(ItemDiffCallback()) {

    private class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item) =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: Item, newItem: Item) =
            oldItem == newItem
    }

    fun removeItem(item: Item) {
        val newList = currentList.toMutableList()
        newList.remove(item)
        submitList(newList) // ✅ DiffUtil автоматически вычислит изменения
    }
}
```

### Notify Методы

```kotlin
// Удалить один элемент
notifyItemRemoved(position)

// Удалить диапазон
notifyItemRangeRemoved(startPosition, count)

// Добавить элемент
notifyItemInserted(position)

// Обновить элемент
notifyItemChanged(position)

// Переместить элемент
notifyItemMoved(fromPosition, toPosition)
```

### ItemTouchHelper Для Свайпа

```kotlin
val swipeHandler = object : ItemTouchHelper.SimpleCallback(
    0,
    ItemTouchHelper.LEFT or ItemTouchHelper.RIGHT
) {
    override fun onMove(...): Boolean = false

    override fun onSwiped(viewHolder: RecyclerView.ViewHolder, direction: Int) {
        adapter.removeItem(viewHolder.adapterPosition)
    }
}

ItemTouchHelper(swipeHandler).attachToRecyclerView(recyclerView)
```

### Undo Функциональность

```kotlin
class UndoAdapter(private val items: MutableList<Item>) :
    RecyclerView.Adapter<ViewHolder>() {

    private var deletedItem: Item? = null
    private var deletedPosition: Int = -1

    fun removeItem(position: Int) {
        deletedItem = items[position]
        deletedPosition = position
        items.removeAt(position)
        notifyItemRemoved(position)
    }

    fun undoDelete() {
        deletedItem?.let {
            items.add(deletedPosition, it)
            notifyItemInserted(deletedPosition)
        }
    }
}

// Использование
adapter.removeItem(position)
Snackbar.make(view, "Удалено", Snackbar.LENGTH_LONG)
    .setAction("ОТМЕНИТЬ") { adapter.undoDelete() }
    .show()
```

### Лучшие Практики

1. **Используйте ListAdapter** с DiffUtil для автоматического вычисления изменений
2. **Избегайте notifyDataSetChanged()** — нет анимаций, плохая производительность
3. **Обновляйте данные ДО вызова notify** — иначе IndexOutOfBoundsException
4. **Используйте notifyItemRangeChanged()** для обновления позиций после удаления
5. **Добавьте undo** для критичных удалений

| Метод | Анимация | Производительность | Случай |
|-------|----------|---------------------|--------|
| `notifyDataSetChanged()` | Нет | Плохая | Избегать |
| `notifyItemRemoved()` | Да | Хорошая | Один элемент |
| `DiffUtil` | Да | Отличная | Рекомендуется |

---

## Answer (EN)

When an item is deleted, you must: (1) remove it from the data source, (2) notify the adapter using specific notify methods.

### Basic Approaches

```kotlin
class MyAdapter(private val items: MutableList<Item>) :
    RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    // ❌ Refreshes entire list, no animations
    fun removeItemBad(position: Int) {
        items.removeAt(position)
        notifyDataSetChanged() // Inefficient!
    }

    // ✅ Updates only affected item
    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)
    }

    // ✅ Also updates subsequent positions
    fun removeItemWithRange(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)
        notifyItemRangeChanged(position, items.size)
    }
}
```

### DiffUtil with ListAdapter (recommended)

```kotlin
class MyAdapter : ListAdapter<Item, MyAdapter.ViewHolder>(ItemDiffCallback()) {

    private class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item) =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: Item, newItem: Item) =
            oldItem == newItem
    }

    fun removeItem(item: Item) {
        val newList = currentList.toMutableList()
        newList.remove(item)
        submitList(newList) // ✅ DiffUtil calculates changes automatically
    }
}
```

### Notify Methods

```kotlin
// Remove single item
notifyItemRemoved(position)

// Remove range
notifyItemRangeRemoved(startPosition, count)

// Add item
notifyItemInserted(position)

// Update item
notifyItemChanged(position)

// Move item
notifyItemMoved(fromPosition, toPosition)
```

### ItemTouchHelper for Swipe

```kotlin
val swipeHandler = object : ItemTouchHelper.SimpleCallback(
    0,
    ItemTouchHelper.LEFT or ItemTouchHelper.RIGHT
) {
    override fun onMove(...): Boolean = false

    override fun onSwiped(viewHolder: RecyclerView.ViewHolder, direction: Int) {
        adapter.removeItem(viewHolder.adapterPosition)
    }
}

ItemTouchHelper(swipeHandler).attachToRecyclerView(recyclerView)
```

### Undo Functionality

```kotlin
class UndoAdapter(private val items: MutableList<Item>) :
    RecyclerView.Adapter<ViewHolder>() {

    private var deletedItem: Item? = null
    private var deletedPosition: Int = -1

    fun removeItem(position: Int) {
        deletedItem = items[position]
        deletedPosition = position
        items.removeAt(position)
        notifyItemRemoved(position)
    }

    fun undoDelete() {
        deletedItem?.let {
            items.add(deletedPosition, it)
            notifyItemInserted(deletedPosition)
        }
    }
}

// Usage
adapter.removeItem(position)
Snackbar.make(view, "Deleted", Snackbar.LENGTH_LONG)
    .setAction("UNDO") { adapter.undoDelete() }
    .show()
```

### Best Practices

1. **Use ListAdapter** with DiffUtil for automatic change calculation
2. **Avoid notifyDataSetChanged()** — no animations, poor performance
3. **Update data BEFORE calling notify** — otherwise IndexOutOfBoundsException
4. **Use notifyItemRangeChanged()** to update positions after removal
5. **Add undo** for critical deletions

| Method | Animation | Performance | Use Case |
|--------|-----------|-------------|----------|
| `notifyDataSetChanged()` | No | Poor | Avoid |
| `notifyItemRemoved()` | Yes | Good | Single item |
| `DiffUtil` | Yes | Excellent | Recommended |

---

## Follow-ups

- What happens if you call notifyItemRemoved() before removing from the data list?
- How does DiffUtil calculate differences between lists?
- When should you use AsyncListDiffer instead of ListAdapter?
- How to handle multiple simultaneous deletions efficiently?
- What are the benefits of using payload with notifyItemChanged()?

## References

- [RecyclerView Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/RecyclerView)
- [DiffUtil Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil)
- [ListAdapter Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/ListAdapter)

## Related Questions

### Prerequisites / Concepts

- [[c-custom-views]]


### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - RecyclerView optimization basics
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - Android UI fundamentals
- [[q-why-separate-ui-and-business-logic--android--easy]] - Architecture principles

### Related (Same Level)
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Compose alternative
- [[q-testing-compose-ui--android--medium]] - UI testing patterns

### Advanced (Harder)
- Questions about RecyclerView performance optimization with large datasets
- Questions about implementing custom ItemAnimator for RecyclerView
- Questions about ConcatAdapter for multiple view types
