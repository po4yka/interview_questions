---\
id: android-315
title: How To Tell Adapter To Redraw List If An Item Was Deleted / Как сказать адаптеру перерисовать список если элемент был удален
aliases: [Adapter Redraw on Item Deletion, Перерисовка адаптера при удалении элемента]
topic: android
subtopics: [architecture-modularization, ui-views, ui-widgets]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-recyclerview, q-how-to-tell-adapter-to-redraw-list-when-item-removed--android--medium, q-mvi-handle-one-time-events--android--hard, q-tasks-back-stack--android--medium, q-view-fundamentals--android--easy, q-what-is-known-about-methods-that-redraw-view--android--medium, q-what-problems-can-there-be-with-list-items--android--easy]
created: 2025-10-15
updated: 2025-11-11
sources: []
tags: [adapters, android, android/architecture-modularization, android/ui-views, android/ui-widgets, difficulty/medium, recyclerview, ui]
anki_cards:
  - slug: android-315-0-en
    front: "How to notify RecyclerView adapter when an item is deleted?"
    back: |
      **Best approaches:**

      1. **notifyItemRemoved(position)** - smooth animation
      ```kotlin
      items.removeAt(position)
      notifyItemRemoved(position)
      ```

      2. **ListAdapter + DiffUtil** (recommended)
      ```kotlin
      val newList = currentList.toMutableList().apply { remove(item) }
      submitList(newList)  // Auto-calculates changes
      ```

      **Avoid:** `notifyDataSetChanged()` - no animation, inefficient
    tags:
      - android_layouts
      - difficulty::medium
  - slug: android-315-0-ru
    front: "Как уведомить адаптер RecyclerView об удалении элемента?"
    back: |
      **Лучшие подходы:**

      1. **notifyItemRemoved(position)** - плавная анимация
      ```kotlin
      items.removeAt(position)
      notifyItemRemoved(position)
      ```

      2. **ListAdapter + DiffUtil** (рекомендуется)
      ```kotlin
      val newList = currentList.toMutableList().apply { remove(item) }
      submitList(newList)  // Авто-вычисление изменений
      ```

      **Избегать:** `notifyDataSetChanged()` - нет анимации, неэффективно
    tags:
      - android_layouts
      - difficulty::medium

---\
# Вопрос (RU)

> Как сказать адаптеру перерисовать список, если какой-то элемент удалился?

# Question (EN)

> How to tell adapter to redraw list if an item was deleted?

---

## Ответ (RU)

Если удалился элемент из списка, нужно: (1) удалить его из списка данных, (2) сообщить `Adapter`, чтобы он перерисовал только изменённые элементы, используя специфичные `notify`-методы (а не всегда весь список целиком).

### Три Подхода

**1. Базовые notify-методы**

```kotlin
class MyAdapter(private val items: MutableList<Item>) : RecyclerView.Adapter<ViewHolder>() {

    // ❌ НЕЭФФЕКТИВНО: Обновляет весь список, нет анимаций, используется только если
    // поменялись данные всего списка или точные изменения сложно определить
    fun removeItemBad(position: Int) {
        items.removeAt(position)
        notifyDataSetChanged()
    }

    // ✅ ПРЕДПОЧТИТЕЛЬНО: Сообщает об удалении позиции, даёт плавную анимацию
    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)  // Плавная анимация
        // При жёсткой привязке логики к позициям можно дополнительно вызвать
        // notifyItemRangeChanged(position, itemCount - position)
    }
}
```

**2. `ListAdapter` с `DiffUtil` (рекомендуется для динамических списков)**

```kotlin
class MyAdapter : ListAdapter<Item, MyAdapter.ItemViewHolder>(ItemDiffCallback()) {

    class ItemViewHolder(view: View) : RecyclerView.ViewHolder(view)

    private class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item) =
            oldItem.id == newItem.id
        override fun areContentsTheSame(oldItem: Item, newItem: Item) =
            oldItem == newItem
    }

    fun removeItem(item: Item) {
        val newList = currentList.toMutableList().apply { remove(item) }
        submitList(newList)  // ✅ DiffUtil автоматически вычисляет изменения и анимации
    }
}
```

**3. `Swipe to Delete` с Undo**

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
|-------|----------|-------------------|----------------------|
| `notifyDataSetChanged()` | Нет | Ниже (перерисовка всего списка) | Когда изменения глобальные или сложно посчитать дифф |
| `notifyItemRemoved()` | Да | Хорошая | Одиночные/локальные удаления |
| `ListAdapter` + `DiffUtil` | Да | Отличная | Динамические списки, частые обновления |

### Ключевые Правила

1. По возможности используйте точечные `notify`-методы (`notifyItemRemoved`, `notifyItemInserted`, `notifyItemChanged`, `notifyItemRange...`) вместо `notifyDataSetChanged()`.
2. Для современных приложений и динамических списков предпочтителен `ListAdapter` с `DiffUtil`.
3. Обновляйте данные ДО вызова `notify`-методов.
4. Для лучшего UX можно добавить `undo` через `Snackbar`.

## Answer (EN)

If an item was deleted from the list, you need to: (1) remove it from the data list, (2) tell the `Adapter` to redraw only the changed items using specific `notify` methods (instead of always refreshing the whole list).

### Three Approaches

**1. Basic notify methods**

```kotlin
class MyAdapter(private val items: MutableList<Item>) : RecyclerView.Adapter<ViewHolder>() {

    // ❌ INEFFICIENT: Refreshes entire list, no animations; use only when
    // the whole dataset changed or you cannot reasonably compute precise changes
    fun removeItemBad(position: Int) {
        items.removeAt(position)
        notifyDataSetChanged()
    }

    // ✅ PREFERRED: Notifies about item removal, gives smooth animation
    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)  // Smooth animation
        // If your logic is tightly bound to adapter positions, you may also call:
        // notifyItemRangeChanged(position, itemCount - position)
    }
}
```

**2. ListAdapter with `DiffUtil` (Recommended for dynamic lists)**

```kotlin
class MyAdapter : ListAdapter<Item, MyAdapter.ItemViewHolder>(ItemDiffCallback()) {

    class ItemViewHolder(view: View) : RecyclerView.ViewHolder(view)

    private class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item) =
            oldItem.id == newItem.id
        override fun areContentsTheSame(oldItem: Item, newItem: Item) =
            oldItem == newItem
    }

    fun removeItem(item: Item) {
        val newList = currentList.toMutableList().apply { remove(item) }
        submitList(newList)  // ✅ DiffUtil calculates changes and animations automatically
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
| `notifyDataSetChanged()` | No | Lower (redraws entire list) | When changes are global or diff is hard to compute |
| `notifyItemRemoved()` | Yes | Good | Single/local deletions |
| `ListAdapter` + `DiffUtil` | Yes | Excellent | Dynamic lists with frequent updates |

### Key Rules

1. Prefer precise `notify` methods (`notifyItemRemoved`, `notifyItemInserted`, `notifyItemChanged`, `notifyItemRange...`) over `notifyDataSetChanged()` when you know what changed.
2. For modern apps and dynamic lists, `ListAdapter` with `DiffUtil` is generally the best choice.
3. Update your data BEFORE calling `notify` methods.
4. For better UX, add undo via `Snackbar`.

---

## Дополнительные Вопросы (RU)

- Чем `notifyItemRangeRemoved()` отличается от `notifyItemRemoved()`?
- Что произойдёт, если вызвать `notify` до удаления элемента из списка данных?
- Когда стоит использовать `AsyncListDiffer` вместо `ListAdapter`?
- Как работают payload'ы в `notifyItemChanged(position, payload)`?
- В чём разница между `areItemsTheSame()` и `areContentsTheSame()` в `DiffUtil`?

## Follow-ups

- How does `notifyItemRangeRemoved()` differ from `notifyItemRemoved()`?
- What happens if you call notify before removing from the data list?
- When should you use `AsyncListDiffer` instead of `ListAdapter`?
- How do payloads work with `notifyItemChanged(position, payload)`?
- What's the difference between `areItemsTheSame()` and `areContentsTheSame()` in `DiffUtil`?

## Ссылки (RU)

- [Официальное руководство по RecyclerView](https://developer.android.com/guide/topics/ui/layout/recyclerview)
- [Документация по DiffUtil](https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil)
- [Справочник по ListAdapter](https://developer.android.com/reference/androidx/recyclerview/widget/ListAdapter)

## References

- [RecyclerView Official Guide](https://developer.android.com/guide/topics/ui/layout/recyclerview)
- [DiffUtil Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil)
- [ListAdapter API Reference](https://developer.android.com/reference/androidx/recyclerview/widget/ListAdapter)

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-recyclerview]]

### Предпосылки (проще)

- [[q-recyclerview-sethasfixedsize--android--easy]] - Оптимизация `RecyclerView`
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - Основы UI
- [[q-view-fundamentals--android--easy]] - Базовые принципы системы `View`

### Похожие (средний уровень)

- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Альтернатива на Compose
- [[q-mvi-handle-one-time-events--android--hard]] - Паттерны обработки событий
- [[q-testing-compose-ui--android--medium]] - Тестирование UI

### Продвинутые (сложнее)

- Как реализовать бесконечный скролл с Paging?
- Как эффективно работать со сложными адаптерами с несколькими типами `View`?
- Каковы особенности производительности вложенных `RecyclerView`?

## Related Questions

### Prerequisites / Concepts

- [[c-recyclerview]]

### Prerequisites (Easier)

- [[q-recyclerview-sethasfixedsize--android--easy]] - `RecyclerView` optimization
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - UI fundamentals
- [[q-view-fundamentals--android--easy]] - `View` system basics

### Related (Same Level)

- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Compose alternative
- [[q-mvi-handle-one-time-events--android--hard]] - Event handling patterns
- [[q-testing-compose-ui--android--medium]] - UI testing

### Advanced (Harder)

- How to implement infinite scroll with paging?
- How to handle complex multi-view-type adapters efficiently?
- What are the performance implications of nested RecyclerViews?
