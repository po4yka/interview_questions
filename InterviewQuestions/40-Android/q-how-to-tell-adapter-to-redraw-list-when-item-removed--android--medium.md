---\
id: android-374
title: How To Tell Adapter To Redraw List When Item Removed / Как сказать адаптеру
  перерисовать список когда элемент удален
aliases: [How To Tell Adapter To Redraw List, Как сказать адаптеру перерисовать список]
topic: android
subtopics: [ui-views]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-custom-views, q-how-to-create-list-like-recyclerview-in-compose--android--medium, q-how-to-tell-adapter-to-redraw-list-if-an-item-was-deleted--android--medium, q-recyclerview-sethasfixedsize--android--easy, q-what-is-known-about-methods-that-redraw-view--android--medium, q-what-problems-can-there-be-with-list-items--android--easy]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [adapter, android/ui-views, difficulty/medium, diffutil, recyclerview]
anki_cards:
  - slug: android-374-0-en
    front: "Why use ListAdapter with DiffUtil instead of manual notify calls?"
    back: |
      **ListAdapter + DiffUtil benefits:**
      - Automatic change detection
      - Smooth item animations
      - Background diff calculation
      - Less boilerplate code

      ```kotlin
      class MyAdapter : ListAdapter<Item, VH>(ItemDiffCallback()) {
          fun updateList(newList: List<Item>) {
              submitList(newList)  // Handles everything
          }
      }
      ```

      No need to call `notifyItemRemoved/Changed/Inserted` manually
    tags:
      - android_layouts
      - difficulty::medium
  - slug: android-374-0-ru
    front: "Почему использовать ListAdapter с DiffUtil вместо ручных notify вызовов?"
    back: |
      **ListAdapter + DiffUtil преимущества:**
      - Автоматическое определение изменений
      - Плавные анимации элементов
      - Вычисление diff в фоне
      - Меньше шаблонного кода

      ```kotlin
      class MyAdapter : ListAdapter<Item, VH>(ItemDiffCallback()) {
          fun updateList(newList: List<Item>) {
              submitList(newList)  // Всё делает сам
          }
      }
      ```

      Не нужно вручную вызывать `notifyItemRemoved/Changed/Inserted`
    tags:
      - android_layouts
      - difficulty::medium

---\
# Вопрос (RU)

> Как правильно сообщить адаптеру `RecyclerView` о том, что элемент был удален из списка?

# Question (EN)

> How to tell a `RecyclerView` adapter that an item has been removed from the list?

---

## Ответ (RU)

Когда элемент удаляется из списка, необходимо: (1) удалить его из источника данных, (2) уведомить адаптер о конкретном изменении через специализированные notify-методы.

### Основные Подходы

```kotlin
class MyAdapter(private val items: MutableList<Item>) :
    RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    // ❌ Обновляет весь список, нет диффа, нет выборочных анимаций
    fun removeItemBad(position: Int) {
        items.removeAt(position)
        notifyDataSetChanged() // Неэффективно, используйте точечные уведомления
    }

    // ✅ Уведомляем об удалении конкретного элемента
    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)
    }

    // ✅ При необходимости обновляем элементы, индексы которых зависят от позиции
    fun removeItemWithRange(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)
        // Вызывайте range-обновление только если view зависят от adapterPosition
        notifyItemRangeChanged(position, itemCount - position)
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

### Notify-методы

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
        val position = viewHolder.bindingAdapterPosition
        if (position != RecyclerView.NO_POSITION) {
            adapter.removeItem(position)
        }
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
        deletedItem?.let { item ->
            if (deletedPosition in 0..items.size) {
                items.add(deletedPosition, item)
                notifyItemInserted(deletedPosition)
            }
            // Сброс состояния после undo
            deletedItem = null
            deletedPosition = -1
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

1. Используйте `ListAdapter` с `DiffUtil` для автоматического вычисления изменений.
2. Избегайте `notifyDataSetChanged()`, когда можно использовать более точечные уведомления — иначе нет анимаций и лишние перерисовки.
3. Сначала обновляйте данные, затем вызывайте `notify*` — иначе возможны ошибки индексов (`IndexOutOfBoundsException`, рассинхронизация).
4. Вызывайте `notifyItemRangeChanged()` только при необходимости, когда содержимое последующих элементов зависит от их `adapterPosition` (например, отображаете порядковый номер).
5. Добавьте undo для критичных удалений (через `Snackbar` или другой UI-паттерн).

| Метод | Анимация | Производительность | Случай |
|-------|----------|---------------------|--------|
| `notifyDataSetChanged()` | Нет (только полное обновление) | Плохая | Избегать, если есть альтернатива |
| `notifyItemRemoved()` | Да | Хорошая | Один элемент |
| `DiffUtil` | Да | Отличная | Рекомендуется |

---

## Answer (EN)

When an item is deleted, you must: (1) remove it from the data source, (2) notify the adapter using specific notify methods.

### Basic Approaches

```kotlin
class MyAdapter(private val items: MutableList<Item>) :
    RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    // ❌ Refreshes entire list, no fine-grained diff or animations
    fun removeItemBad(position: Int) {
        items.removeAt(position)
        notifyDataSetChanged() // Inefficient, prefer specific notifications
    }

    // ✅ Notify about removal of a single item
    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)
    }

    // ✅ Use range update only if later items' content depends on their position
    fun removeItemWithRange(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)
        // Call range-changed only when views depend on adapterPosition
        notifyItemRangeChanged(position, itemCount - position)
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
        val position = viewHolder.bindingAdapterPosition
        if (position != RecyclerView.NO_POSITION) {
            adapter.removeItem(position)
        }
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
        deletedItem?.let { item ->
            if (deletedPosition in 0..items.size) {
                items.add(deletedPosition, item)
                notifyItemInserted(deletedPosition)
            }
            // Reset state after undo
            deletedItem = null
            deletedPosition = -1
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

1. Use `ListAdapter` with `DiffUtil` for automatic diff calculation.
2. Avoid `notifyDataSetChanged()` when you can use more specific calls — it skips animations and causes unnecessary redraws.
3. Update data BEFORE calling `notify*` to avoid index issues (`IndexOutOfBoundsException`, desync).
4. `Call` `notifyItemRangeChanged()` only when necessary, e.g., when subsequent items render content based on their `adapterPosition` (such as ordinal numbers).
5. Provide undo for critical deletions (via `Snackbar` or similar UX pattern).

| Method | Animation | Performance | Use Case |
|--------|-----------|-------------|----------|
| `notifyDataSetChanged()` | No (full refresh only) | Poor | Avoid when a more specific call is possible |
| `notifyItemRemoved()` | Yes | Good | Single item |
| `DiffUtil` | Yes | Excellent | Recommended |

---

## Дополнительные Вопросы (RU)

- Что произойдет, если вызвать `notifyItemRemoved()` до удаления элемента из списка данных?
- Как `DiffUtil` вычисляет различия между списками?
- Когда стоит использовать `AsyncListDiffer` вместо `ListAdapter`?
- Как эффективно обрабатывать множественные одновременные удаления?
- Каковы преимущества использования `payload` с `notifyItemChanged()`?

## Follow-ups

- What happens if you call `notifyItemRemoved()` before removing from the data list?
- How does `DiffUtil` calculate differences between lists?
- When should you use `AsyncListDiffer` instead of `ListAdapter`?
- How to handle multiple simultaneous deletions efficiently?
- What are the benefits of using `payload` with `notifyItemChanged()`?

## Ссылки (RU)

- [Документация по RecyclerView](https://developer.android.com/reference/androidx/recyclerview/widget/RecyclerView)
- [Документация по DiffUtil](https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil)
- [Документация по ListAdapter](https://developer.android.com/reference/androidx/recyclerview/widget/ListAdapter)

## References

- [RecyclerView Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/RecyclerView)
- [DiffUtil Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil)
- [ListAdapter Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/ListAdapter)

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-custom-views]]

### Предпосылки (Проще)

- [[q-recyclerview-sethasfixedsize--android--easy]] - Основы оптимизации `RecyclerView`

### Связанные (Средний уровень)

- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Альтернатива на Compose

### Продвинутые (Сложнее)

- Вопросы об оптимизации производительности `RecyclerView` с большими наборами данных
- Вопросы о реализации кастомного `ItemAnimator` для `RecyclerView`
- Вопросы о `ConcatAdapter` для нескольких типов представлений

## Related Questions

### Prerequisites / Concepts

- [[c-custom-views]]

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - `RecyclerView` optimization basics

### Related (Same Level)
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Compose alternative

### Advanced (Harder)
- Questions about `RecyclerView` performance optimization with large datasets
- Questions about implementing custom ItemAnimator for `RecyclerView`
- Questions about ConcatAdapter for multiple view types
