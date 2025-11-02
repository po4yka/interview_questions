---
id: android-392
title: "Как сказать адаптеру перерисовать список если элемент был удален / How To Tell Adapter To Redraw List If Element Was Deleted"
aliases: ["How to tell adapter to redraw list", "RecyclerView adapter update", "Как сказать адаптеру перерисовать список", "Обновление адаптера RecyclerView"]
topic: android
subtopics: [ui-views]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-how-to-create-list-like-recyclerview-in-compose--android--medium, q-recyclerview-sethasfixedsize--android--easy]
sources: []
created: 2025-10-15
updated: 2025-10-31
tags: [adapter, android, android/ui-views, difficulty/medium, recyclerview]
date created: Tuesday, October 28th 2025, 9:11:36 pm
date modified: Saturday, November 1st 2025, 5:43:35 pm
---

# Вопрос (RU)

> Как правильно уведомить адаптер RecyclerView о том, что элемент был удален из списка?

# Question (EN)

> How to properly notify a RecyclerView adapter that an item has been deleted from the list?

---

## Ответ (RU)

При удалении элемента необходимо обновить источник данных и уведомить адаптер специфичным методом для эффективной перерисовки.

### Три Основных Подхода

**1. ListAdapter (рекомендуется)**

```kotlin
// ✅ Современный подход - DiffUtil встроен
class ModernAdapter : ListAdapter<Item, ModernAdapter.ViewHolder>(ItemComparator) {

    fun removeItem(position: Int) {
        val newList = currentList.toMutableList()
        newList.removeAt(position)
        submitList(newList)  // DiffUtil работает автоматически
    }

    object ItemComparator : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(old: Item, new: Item) = old.id == new.id
        override fun areContentsTheSame(old: Item, new: Item) = old == new
    }
}
```

**2. DiffUtil с RecyclerView.Adapter**

```kotlin
// ✅ Эффективно для больших списков
class SmartAdapter : RecyclerView.Adapter<ViewHolder>() {
    private var items = listOf<Item>()

    fun updateItems(newItems: List<Item>) {
        val diff = DiffUtil.calculateDiff(ItemDiffCallback(items, newItems))
        items = newItems
        diff.dispatchUpdatesTo(this)
    }
}
```

**3. Прямое уведомление**

```kotlin
// ✅ Для простых случаев
fun removeItem(position: Int) {
    items.removeAt(position)
    notifyItemRemoved(position)
    // Обновить индексы следующих элементов
    notifyItemRangeChanged(position, items.size)
}

// ❌ Избегать - перерисовывает весь список
fun removeItemBad(position: Int) {
    items.removeAt(position)
    notifyDataSetChanged()  // Неэффективно, теряются анимации
}
```

### Swipe to Delete С Отменой

```kotlin
val itemTouchHelper = ItemTouchHelper(object : ItemTouchHelper.SimpleCallback(
    0, ItemTouchHelper.LEFT or ItemTouchHelper.RIGHT
) {
    override fun onSwiped(viewHolder: ViewHolder, direction: Int) {
        val position = viewHolder.adapterPosition
        val item = adapter.currentList[position]

        val newList = adapter.currentList.toMutableList()
        newList.removeAt(position)
        adapter.submitList(newList)

        Snackbar.make(recyclerView, "Элемент удален", Snackbar.LENGTH_LONG)
            .setAction("Отменить") {
                val restoreList = adapter.currentList.toMutableList()
                restoreList.add(position, item)
                adapter.submitList(restoreList)
            }
            .show()
    }
})
itemTouchHelper.attachToRecyclerView(recyclerView)
```

### Важные Особенности

**Всегда используйте adapterPosition**

```kotlin
// ❌ Неправильно - позиция может устареть
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    holder.deleteButton.setOnClickListener {
        removeItem(position)  // position может быть неактуальной!
    }
}

// ✅ Правильно - получаем текущую позицию
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    holder.deleteButton.setOnClickListener {
        val currentPos = holder.adapterPosition
        if (currentPos != RecyclerView.NO_POSITION) {
            removeItem(currentPos)
        }
    }
}
```

### Jetpack Compose

В Compose обновления списка автоматические через State:

```kotlin
@Composable
fun ItemList() {
    var items by remember { mutableStateOf(listOf<Item>()) }

    LazyColumn {
        items(
            items = items,
            key = { it.id }  // Важно для анимаций
        ) { item ->
            ItemRow(
                item = item,
                onDelete = { items = items.filter { it.id != item.id } }
            )
        }
    }
}
```

### Лучшие Практики

1. **ListAdapter** - выбор по умолчанию для нового кода
2. **Стабильные ключи** - используйте `key = { it.id }` для правильных анимаций
3. **Избегайте `notifyDataSetChanged()`** - теряются анимации и производительность
4. **Функция отмены** - улучшает UX через Snackbar
5. **`adapterPosition`** - используйте вместо параметра `position`

---

## Answer (EN)

When deleting an item, you need to update the data source and notify the adapter with specific methods for efficient redrawing.

### Three Main Approaches

**1. ListAdapter (recommended)**

```kotlin
// ✅ Modern approach - DiffUtil built-in
class ModernAdapter : ListAdapter<Item, ModernAdapter.ViewHolder>(ItemComparator) {

    fun removeItem(position: Int) {
        val newList = currentList.toMutableList()
        newList.removeAt(position)
        submitList(newList)  // DiffUtil works automatically
    }

    object ItemComparator : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(old: Item, new: Item) = old.id == new.id
        override fun areContentsTheSame(old: Item, new: Item) = old == new
    }
}
```

**2. DiffUtil with RecyclerView.Adapter**

```kotlin
// ✅ Efficient for large lists
class SmartAdapter : RecyclerView.Adapter<ViewHolder>() {
    private var items = listOf<Item>()

    fun updateItems(newItems: List<Item>) {
        val diff = DiffUtil.calculateDiff(ItemDiffCallback(items, newItems))
        items = newItems
        diff.dispatchUpdatesTo(this)
    }
}
```

**3. Direct Notification**

```kotlin
// ✅ For simple cases
fun removeItem(position: Int) {
    items.removeAt(position)
    notifyItemRemoved(position)
    // Update indices of following items
    notifyItemRangeChanged(position, items.size)
}

// ❌ Avoid - redraws entire list
fun removeItemBad(position: Int) {
    items.removeAt(position)
    notifyDataSetChanged()  // Inefficient, loses animations
}
```

### Swipe to Delete with Undo

```kotlin
val itemTouchHelper = ItemTouchHelper(object : ItemTouchHelper.SimpleCallback(
    0, ItemTouchHelper.LEFT or ItemTouchHelper.RIGHT
) {
    override fun onSwiped(viewHolder: ViewHolder, direction: Int) {
        val position = viewHolder.adapterPosition
        val item = adapter.currentList[position]

        val newList = adapter.currentList.toMutableList()
        newList.removeAt(position)
        adapter.submitList(newList)

        Snackbar.make(recyclerView, "Item deleted", Snackbar.LENGTH_LONG)
            .setAction("Undo") {
                val restoreList = adapter.currentList.toMutableList()
                restoreList.add(position, item)
                adapter.submitList(restoreList)
            }
            .show()
    }
})
itemTouchHelper.attachToRecyclerView(recyclerView)
```

### Important Considerations

**Always use adapterPosition**

```kotlin
// ❌ Wrong - position may become stale
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    holder.deleteButton.setOnClickListener {
        removeItem(position)  // position may be outdated!
    }
}

// ✅ Correct - get current position
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    holder.deleteButton.setOnClickListener {
        val currentPos = holder.adapterPosition
        if (currentPos != RecyclerView.NO_POSITION) {
            removeItem(currentPos)
        }
    }
}
```

### Jetpack Compose

In Compose, list updates are automatic through State:

```kotlin
@Composable
fun ItemList() {
    var items by remember { mutableStateOf(listOf<Item>()) }

    LazyColumn {
        items(
            items = items,
            key = { it.id }  // Important for animations
        ) { item ->
            ItemRow(
                item = item,
                onDelete = { items = items.filter { it.id != item.id } }
            )
        }
    }
}
```

### Best Practices

1. **ListAdapter** - default choice for new code
2. **Stable keys** - use `key = { it.id }` for proper animations
3. **Avoid `notifyDataSetChanged()`** - loses animations and performance
4. **Undo functionality** - improves UX through Snackbar
5. **`adapterPosition`** - use instead of `position` parameter

---

## Follow-ups

- What are the performance implications of `notifyDataSetChanged()` vs `notifyItemRemoved()`?
- How does DiffUtil determine which items changed?
- When should you use `notifyItemRangeChanged()` after deletion?
- How to handle item deletion in a multi-selection scenario?
- What happens if you call `notifyItemRemoved()` without actually removing the item from the data source?

## References

- Android Documentation: [RecyclerView.Adapter](https://developer.android.com/reference/androidx/recyclerview/widget/RecyclerView.Adapter)
- Android Documentation: [ListAdapter](https://developer.android.com/reference/androidx/recyclerview/widget/ListAdapter)
- Android Documentation: [DiffUtil](https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil)

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - RecyclerView basics
- [[q-why-separate-ui-and-business-logic--android--easy]] - Architecture fundamentals
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - UI fundamentals

### Related (Same Level)
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Compose alternative
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - RecyclerView customization
- [[q-testing-compose-ui--android--medium]] - Testing UI components

### Advanced (Harder)
- Performance optimization with large lists and complex diff calculations
- Custom ItemAnimator implementation for deletion effects
- Handling concurrent modifications and race conditions in adapter updates
