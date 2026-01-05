---
id: android-392
title: Как сказать адаптеру перерисовать список если элемент был удален / How To Tell
  Adapter To Redraw List If Element Was Deleted
aliases: [How to tell adapter to redraw list, RecyclerView adapter update, Как сказать адаптеру перерисовать список, Обновление адаптера RecyclerView]
topic: android
subtopics: [ui-views]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-recyclerview, q-dagger-build-time-optimization--android--medium, q-how-to-create-list-like-recyclerview-in-compose--android--medium, q-how-to-tell-adapter-to-redraw-list-if-an-item-was-deleted--android--medium, q-how-to-tell-adapter-to-redraw-list-when-item-removed--android--medium, q-recyclerview-sethasfixedsize--android--easy]
sources: []
created: 2025-10-15
updated: 2025-10-31
tags: [adapter, android, android/ui-views, difficulty/medium, recyclerview]
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
        if (position in newList.indices) {
            newList.removeAt(position)
            submitList(newList)  // DiffUtil работает автоматически
        }
    }

    object ItemComparator : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item) = oldItem.id == newItem.id
        override fun areContentsTheSame(oldItem: Item, newItem: Item) = oldItem == newItem
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
// ✅ Для простых случаев при ручном управлении списком
fun removeItem(position: Int) {
    if (position in items.indices) {
        items.removeAt(position)
        notifyItemRemoved(position)
        // При необходимости обновить отображаемые позиции следующих элементов
        // notifyItemRangeChanged(position, items.size - position)
    }
}

// ❌ Избегать - перерисовывает весь список
fun removeItemBad(position: Int) {
    if (position in items.indices) {
        items.removeAt(position)
        notifyDataSetChanged()  // Неэффективно, теряются анимации
    }
}
```

### Swipe to Delete С Отменой

```kotlin
val itemTouchHelper = ItemTouchHelper(object : ItemTouchHelper.SimpleCallback(
    0, ItemTouchHelper.LEFT or ItemTouchHelper.RIGHT
) {
    override fun onSwiped(viewHolder: ViewHolder, direction: Int) {
        val position = viewHolder.bindingAdapterPosition
        if (position == RecyclerView.NO_POSITION) return

        val currentList = adapter.currentList
        if (position !in currentList.indices) return

        val item = currentList[position]
        val newList = currentList.toMutableList().apply { removeAt(position) }
        adapter.submitList(newList)

        Snackbar.make(recyclerView, "Элемент удален", Snackbar.LENGTH_LONG)
            .setAction("Отменить") {
                val restoreList = adapter.currentList.toMutableList().apply {
                    val safePosition = position.coerceIn(0, size)
                    add(safePosition, item)
                }
                adapter.submitList(restoreList)
            }
            .show()
    }
})
itemTouchHelper.attachToRecyclerView(recyclerView)
```

### Важные Особенности

**Всегда используйте актуальную позицию ViewHolder**

```kotlin
// ❌ Неправильно - позиция из параметра может устареть
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    holder.deleteButton.setOnClickListener {
        removeItem(position)  // position может быть неактуальной!
    }
}

// ✅ Правильно - получаем текущую позицию холдера
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    holder.deleteButton.setOnClickListener {
        val currentPos = holder.bindingAdapterPosition
        if (currentPos != RecyclerView.NO_POSITION) {
            removeItem(currentPos)
        }
    }
}
```

(При отсутствии ConcatAdapter допустимо использовать `adapterPosition`, но `bindingAdapterPosition` более универсален.)

### Jetpack Compose

В Compose обновления списка происходят автоматически через состояние:

```kotlin
@Composable
fun ItemList() {
    var items by remember { mutableStateOf(listOf<Item>()) }

    LazyColumn {
        items(
            items = items,
            key = { it.id }  // Важно для корректных анимаций и сохранения состояния
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

1. **ListAdapter** - выбор по умолчанию для нового кода.
2. **Стабильные ключи** - используйте `key = { it.id }` для правильных анимаций и восстановления состояния.
3. **Избегайте `notifyDataSetChanged()`** - теряются анимации и ухудшается производительность.
4. **Функция отмены** - улучшает UX через Snackbar, особенно для удаления.
5. **Используйте актуальную позицию (`bindingAdapterPosition`/`adapterPosition`) вместо параметра `position`.**

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
        if (position in newList.indices) {
            newList.removeAt(position)
            submitList(newList)  // DiffUtil works automatically
        }
    }

    object ItemComparator : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item) = oldItem.id == newItem.id
        override fun areContentsTheSame(oldItem: Item, newItem: Item) = oldItem == newItem
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
// ✅ For simple cases with manual list management
fun removeItem(position: Int) {
    if (position in items.indices) {
        items.removeAt(position)
        notifyItemRemoved(position)
        // Optionally update following items' bound positions if UI depends on adapter position
        // notifyItemRangeChanged(position, items.size - position)
    }
}

// ❌ Avoid - redraws entire list
fun removeItemBad(position: Int) {
    if (position in items.indices) {
        items.removeAt(position)
        notifyDataSetChanged()  // Inefficient, loses animations
    }
}
```

### Swipe to Delete with Undo

```kotlin
val itemTouchHelper = ItemTouchHelper(object : ItemTouchHelper.SimpleCallback(
    0, ItemTouchHelper.LEFT or ItemTouchHelper.RIGHT
) {
    override fun onSwiped(viewHolder: ViewHolder, direction: Int) {
        val position = viewHolder.bindingAdapterPosition
        if (position == RecyclerView.NO_POSITION) return

        val currentList = adapter.currentList
        if (position !in currentList.indices) return

        val item = currentList[position]
        val newList = currentList.toMutableList().apply { removeAt(position) }
        adapter.submitList(newList)

        Snackbar.make(recyclerView, "Item deleted", Snackbar.LENGTH_LONG)
            .setAction("Undo") {
                val restoreList = adapter.currentList.toMutableList().apply {
                    val safePosition = position.coerceIn(0, size)
                    add(safePosition, item)
                }
                adapter.submitList(restoreList)
            }
            .show()
    }
})
itemTouchHelper.attachToRecyclerView(recyclerView)
```

### Important Considerations

**Always use the holder's current position**

```kotlin
// ❌ Wrong - position parameter may become stale
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    holder.deleteButton.setOnClickListener {
        removeItem(position)  // position may be outdated!
    }
}

// ✅ Correct - get current holder position
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    holder.deleteButton.setOnClickListener {
        val currentPos = holder.bindingAdapterPosition
        if (currentPos != RecyclerView.NO_POSITION) {
            removeItem(currentPos)
        }
    }
}
```

(When not using ConcatAdapter, `adapterPosition` is acceptable; `bindingAdapterPosition` is safer in general.)

### Jetpack Compose

In Compose, list updates are driven by State:

```kotlin
@Composable
fun ItemList() {
    var items by remember { mutableStateOf(listOf<Item>()) }

    LazyColumn {
        items(
            items = items,
            key = { it.id }  // Important for animations and state preservation
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

1. **ListAdapter** - default choice for new code.
2. **Stable keys** - use `key = { it.id }` for proper animations and state.
3. **Avoid `notifyDataSetChanged()`** - it loses animations and hurts performance.
4. **Undo functionality** - improves UX, especially when deleting items.
5. **Use the current position (`bindingAdapterPosition`/`adapterPosition`) instead of the `position` parameter.**

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

### Prerequisites / Concepts

- [[c-recyclerview]]

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
