---
id: android-315
title: "How To Tell Adapter To Redraw List If An Item Was Deleted / Как сказать адаптеру перерисовать список если элемент был удален"
aliases: ["Adapter Redraw on Item Deletion", "Перерисовка адаптера при удалении элемента"]
topic: android
subtopics: [ui-views, ui-widgets, architecture-modularization]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-mvi-handle-one-time-events--android--hard, q-tasks-back-stack--android--medium, q-view-fundamentals--android--easy]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android, android/ui-views, android/ui-widgets, android/architecture-modularization, recyclerview, adapters, ui, difficulty/medium]
date created: Tuesday, October 28th 2025, 9:12:57 pm
date modified: Thursday, October 30th 2025, 3:09:58 pm
---

# Вопрос (RU)

> Как сказать адаптеру перерисовать список, если какой-то элемент удалился?

# Question (EN)

> How to tell adapter to redraw list if an item was deleted?

---

## Ответ (RU)

Если удалился элемент из списка, нужно: (1) Удалить его из списка данных, (2) Сообщить Adapter, чтобы он перерисовал только изменённые элементы, используя специфичные notify методы.

### Три Подхода

**1. Базовый notify метод**

```kotlin
class MyAdapter(private val items: MutableList<Item>) : RecyclerView.Adapter<ViewHolder>() {

    // ❌ ПЛОХО: Обновляет весь список, нет анимаций
    fun removeItemBad(position: Int) {
        items.removeAt(position)
        notifyDataSetChanged()
    }

    // ✅ ХОРОШО: Обновляет только затронутый элемент
    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)  // Плавная анимация
    }
}
```

**2. ListAdapter с DiffUtil (Рекомендуется)**

```kotlin
class MyAdapter : ListAdapter<Item, MyAdapter.ViewHolder>(ItemDiffCallback()) {

    private class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item) =
            oldItem.id == newItem.id
        override fun areContentsTheSame(oldItem: Item, newItem: Item) =
            oldItem == newItem
    }

    fun removeItem(item: Item) {
        val newList = currentList.toMutableList().apply { remove(item) }
        submitList(newList)  // ✅ DiffUtil автоматически вычисляет изменения
    }
}
```

**3. Swipe to Delete с Undo**

```kotlin
class UndoDeleteAdapter(private val items: MutableList<Item>) :
    RecyclerView.Adapter<ViewHolder>() {

    private var recentlyDeleted: Pair<Item, Int>? = null

    fun removeItem(position: Int) {
        recentlyDeleted = items[position] to position
        items.removeAt(position)
        notifyItemRemoved(position)
    }

    fun undoDelete() {
        recentlyDeleted?.let { (item, pos) ->
            items.add(pos, item)
            notifyItemInserted(pos)
        }
    }
}
```

### Сравнение Методов

| Метод | Анимация | Производительность | Случай использования |
|-------|----------|-------------------|---------------------|
| `notifyDataSetChanged()` | Нет | Плохая | Избегайте |
| `notifyItemRemoved()` | Да | Хорошая | Одиночные удаления |
| `ListAdapter` + DiffUtil | Да | Отличная | Рекомендуется для всех случаев |

### Ключевые Правила

1. **Всегда используйте** `notifyItemRemoved()` вместо `notifyDataSetChanged()`
2. **Для современных приложений** — `ListAdapter` с DiffUtil
3. **Обновляйте данные ПЕРЕД** вызовом notify
4. **Для UX** — добавьте undo через Snackbar

## Answer (EN)

If an item was deleted from the list, you need to: (1) Remove it from the data list, (2) Tell Adapter to redraw only changed items using specific notify methods.

### Three Approaches

**1. Basic notify method**

```kotlin
class MyAdapter(private val items: MutableList<Item>) : RecyclerView.Adapter<ViewHolder>() {

    // ❌ BAD: Refreshes entire list, no animations
    fun removeItemBad(position: Int) {
        items.removeAt(position)
        notifyDataSetChanged()
    }

    // ✅ GOOD: Only updates affected item
    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)  // Smooth animation
    }
}
```

**2. ListAdapter with DiffUtil (Recommended)**

```kotlin
class MyAdapter : ListAdapter<Item, MyAdapter.ViewHolder>(ItemDiffCallback()) {

    private class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item) =
            oldItem.id == newItem.id
        override fun areContentsTheSame(oldItem: Item, newItem: Item) =
            oldItem == newItem
    }

    fun removeItem(item: Item) {
        val newList = currentList.toMutableList().apply { remove(item) }
        submitList(newList)  // ✅ DiffUtil automatically calculates changes
    }
}
```

**3. Swipe to Delete with Undo**

```kotlin
class UndoDeleteAdapter(private val items: MutableList<Item>) :
    RecyclerView.Adapter<ViewHolder>() {

    private var recentlyDeleted: Pair<Item, Int>? = null

    fun removeItem(position: Int) {
        recentlyDeleted = items[position] to position
        items.removeAt(position)
        notifyItemRemoved(position)
    }

    fun undoDelete() {
        recentlyDeleted?.let { (item, pos) ->
            items.add(pos, item)
            notifyItemInserted(pos)
        }
    }
}
```

### Method Comparison

| Method | Animation | Performance | Use Case |
|--------|-----------|------------|----------|
| `notifyDataSetChanged()` | No | Poor | Avoid |
| `notifyItemRemoved()` | Yes | Good | Single deletions |
| `ListAdapter` + DiffUtil | Yes | Excellent | Recommended for all cases |

### Key Rules

1. **Always use** `notifyItemRemoved()` instead of `notifyDataSetChanged()`
2. **For modern apps** — `ListAdapter` with DiffUtil
3. **Update data BEFORE** calling notify
4. **For UX** — add undo via Snackbar

---

## Follow-ups

- How does `notifyItemRangeRemoved()` differ from `notifyItemRemoved()`?
- What happens if you call notify before removing from the data list?
- When should you use `AsyncListDiffer` instead of `ListAdapter`?
- How do payloads work with `notifyItemChanged(position, payload)`?
- What's the difference between `areItemsTheSame()` and `areContentsTheSame()` in DiffUtil?

## References

- [RecyclerView Official Guide](https://developer.android.com/guide/topics/ui/layout/recyclerview)
- [DiffUtil Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil)
- [ListAdapter API Reference](https://developer.android.com/reference/androidx/recyclerview/widget/ListAdapter)

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - RecyclerView optimization
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - UI fundamentals
- [[q-view-fundamentals--android--easy]] - View system basics

### Related (Same Level)
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Compose alternative
- [[q-mvi-handle-one-time-events--android--hard]] - Event handling patterns
- [[q-testing-compose-ui--android--medium]] - UI testing

### Advanced (Harder)
- How to implement infinite scroll with paging?
- How to handle complex multi-view-type adapters efficiently?
- What are the performance implications of nested RecyclerViews?
