---
id: 20251012-1227199
title: "How To Tell Adapter To Redraw List If An Item Was Deleted / Как сказать адаптеру перерисовать список если элемент был удален"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-tasks-back-stack--android--medium, q-mvi-handle-one-time-events--android--hard, q-view-fundamentals--android--easy]
created: 2025-10-15
tags: [recyclerview, android, ui, difficulty/medium]
---
# How to tell adapter to redraw list if an item was deleted?

# Вопрос (RU)

Как сказать адаптеру перерисовать список, если какой-то элемент удалился

## Answer (EN)
If an item was deleted from the list, you need to: (1) Remove it from the data list, (2) Tell Adapter to redraw only changed items using specific notify methods.

### 1. Basic Approaches

```kotlin
class MyAdapter(private val items: MutableList<Item>) : RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    // - BAD: Refreshes entire list, no animations
    fun removeItemBad(position: Int) {
        items.removeAt(position)
        notifyDataSetChanged() // Inefficient!
    }

    // - GOOD: Only updates affected item
    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position) // Smooth animation
    }

    // - BETTER: Also updates subsequent items
    fun removeItemWithRange(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)
        notifyItemRangeChanged(position, items.size) // Update positions
    }
}
```

### 2. Using DiffUtil (Recommended)

```kotlin
class MyAdapter : ListAdapter<Item, MyAdapter.ViewHolder>(ItemDiffCallback()) {

    private class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem == newItem
        }
    }

    fun removeItem(item: Item) {
        val newList = currentList.toMutableList()
        newList.remove(item)
        submitList(newList) // DiffUtil automatically calculates changes
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(item: Item) {
            itemView.findViewById<TextView>(R.id.textView).text = item.name
        }
    }
}
```

### 3. All Notify Methods

```kotlin
class AdvancedAdapter(private val items: MutableList<Item>) : RecyclerView.Adapter<ViewHolder>() {

    // Remove single item
    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)
    }

    // Remove range of items
    fun removeItems(startPosition: Int, count: Int) {
        repeat(count) {
            items.removeAt(startPosition)
        }
        notifyItemRangeRemoved(startPosition, count)
    }

    // Add single item
    fun addItem(position: Int, item: Item) {
        items.add(position, item)
        notifyItemInserted(position)
    }

    // Add range of items
    fun addItems(position: Int, newItems: List<Item>) {
        items.addAll(position, newItems)
        notifyItemRangeInserted(position, newItems.size)
    }

    // Update single item
    fun updateItem(position: Int, item: Item) {
        items[position] = item
        notifyItemChanged(position)
    }

    // Update with payload (partial update)
    fun updateItemWithPayload(position: Int, item: Item, payload: Any) {
        items[position] = item
        notifyItemChanged(position, payload)
    }

    // Move item
    fun moveItem(fromPosition: Int, toPosition: Int) {
        val item = items.removeAt(fromPosition)
        items.add(toPosition, item)
        notifyItemMoved(fromPosition, toPosition)
    }

    // Update range
    fun updateRange(startPosition: Int, count: Int) {
        notifyItemRangeChanged(startPosition, count)
    }
}
```

### 4. With Swipe to Delete

```kotlin
class SwipeToDeleteActivity : AppCompatActivity() {

    private lateinit var adapter: MyAdapter
    private val items = mutableListOf<Item>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        adapter = MyAdapter(items)
        val recyclerView = findViewById<RecyclerView>(R.id.recyclerView)
        recyclerView.adapter = adapter

        // Swipe to delete
        val swipeHandler = object : ItemTouchHelper.SimpleCallback(
            0,
            ItemTouchHelper.LEFT or ItemTouchHelper.RIGHT
        ) {
            override fun onMove(
                recyclerView: RecyclerView,
                viewHolder: RecyclerView.ViewHolder,
                target: RecyclerView.ViewHolder
            ): Boolean = false

            override fun onSwiped(viewHolder: RecyclerView.ViewHolder, direction: Int) {
                val position = viewHolder.adapterPosition
                adapter.removeItem(position)
            }
        }

        val itemTouchHelper = ItemTouchHelper(swipeHandler)
        itemTouchHelper.attachToRecyclerView(recyclerView)
    }
}
```

### 5. With Undo Functionality

```kotlin
class UndoDeleteAdapter(private val items: MutableList<Item>) : RecyclerView.Adapter<ViewHolder>() {

    private var recentlyDeletedItem: Item? = null
    private var recentlyDeletedPosition: Int = -1

    fun removeItem(position: Int) {
        recentlyDeletedItem = items[position]
        recentlyDeletedPosition = position

        items.removeAt(position)
        notifyItemRemoved(position)
    }

    fun undoDelete() {
        recentlyDeletedItem?.let { item ->
            items.add(recentlyDeletedPosition, item)
            notifyItemInserted(recentlyDeletedPosition)
        }
    }
}

// Usage in Activity
class MainActivity : AppCompatActivity() {
    private fun deleteItemWithUndo(position: Int) {
        adapter.removeItem(position)

        Snackbar.make(binding.root, "Item deleted", Snackbar.LENGTH_LONG)
            .setAction("UNDO") {
                adapter.undoDelete()
            }
            .show()
    }
}
```

### 6. AsyncListDiffer for Background Diff

```kotlin
class AsyncAdapter : RecyclerView.Adapter<ViewHolder>() {

    private val diffCallback = object : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item) = oldItem.id == newItem.id
        override fun areContentsTheSame(oldItem: Item, newItem: Item) = oldItem == newItem
    }

    private val differ = AsyncListDiffer(this, diffCallback)

    val currentList: List<Item>
        get() = differ.currentList

    fun submitList(list: List<Item>) {
        differ.submitList(list)
    }

    fun removeItem(item: Item) {
        val newList = currentList.toMutableList()
        newList.remove(item)
        submitList(newList)
    }
}
```

### Comparison of Methods

| Method | Animation | Performance | Use Case |
|--------|-----------|-------------|----------|
| `notifyDataSetChanged()` | - No | - Poor | Avoid if possible |
| `notifyItemRemoved()` | - Yes | - Good | Single item delete |
| `notifyItemRangeRemoved()` | - Yes | - Good | Multiple items |
| `DiffUtil` | - Yes | - Best | Complex changes |
| `ListAdapter` | - Yes | - Best | Recommended |

### Best Practices

1. - Use `notifyItemRemoved()` for single deletions
2. - Use `ListAdapter` with DiffUtil for modern apps
3. - Avoid `notifyDataSetChanged()` - no animations
4. - Update data model BEFORE calling notify
5. - Use `notifyItemRangeChanged()` to update positions
6. - Implement undo functionality for better UX

## Ответ (RU)

Если удалился элемент из списка, нужно: (1) Удалить его из списка данных, (2) Сообщить Adapter, чтобы он перерисовал только изменённые элементы, используя специфичные notify методы.

### 1. Базовые подходы

```kotlin
class MyAdapter(private val items: MutableList<Item>) : RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    // - ПЛОХО: Обновляет весь список, нет анимаций
    fun removeItemBad(position: Int) {
        items.removeAt(position)
        notifyDataSetChanged() // Неэффективно!
    }

    // - ХОРОШО: Обновляет только затронутый элемент
    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position) // Плавная анимация
    }

    // - ЛУЧШЕ: Также обновляет последующие элементы
    fun removeItemWithRange(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)
        notifyItemRangeChanged(position, items.size) // Обновляем позиции
    }
}
```

### 2. Использование DiffUtil (Рекомендуется)

```kotlin
class MyAdapter : ListAdapter<Item, MyAdapter.ViewHolder>(ItemDiffCallback()) {

    private class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem == newItem
        }
    }

    fun removeItem(item: Item) {
        val newList = currentList.toMutableList()
        newList.remove(item)
        submitList(newList) // DiffUtil автоматически вычисляет изменения
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(item: Item) {
            itemView.findViewById<TextView>(R.id.textView).text = item.name
        }
    }
}
```

### 3. Все методы Notify

```kotlin
class AdvancedAdapter(private val items: MutableList<Item>) : RecyclerView.Adapter<ViewHolder>() {

    // Удаление одного элемента
    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)
    }

    // Удаление диапазона элементов
    fun removeItems(startPosition: Int, count: Int) {
        repeat(count) {
            items.removeAt(startPosition)
        }
        notifyItemRangeRemoved(startPosition, count)
    }

    // Добавление одного элемента
    fun addItem(position: Int, item: Item) {
        items.add(position, item)
        notifyItemInserted(position)
    }

    // Добавление диапазона элементов
    fun addItems(position: Int, newItems: List<Item>) {
        items.addAll(position, newItems)
        notifyItemRangeInserted(position, newItems.size)
    }

    // Обновление одного элемента
    fun updateItem(position: Int, item: Item) {
        items[position] = item
        notifyItemChanged(position)
    }

    // Обновление с payload (частичное обновление)
    fun updateItemWithPayload(position: Int, item: Item, payload: Any) {
        items[position] = item
        notifyItemChanged(position, payload)
    }

    // Перемещение элемента
    fun moveItem(fromPosition: Int, toPosition: Int) {
        val item = items.removeAt(fromPosition)
        items.add(toPosition, item)
        notifyItemMoved(fromPosition, toPosition)
    }

    // Обновление диапазона
    fun updateRange(startPosition: Int, count: Int) {
        notifyItemRangeChanged(startPosition, count)
    }
}
```

### 4. С функцией Swipe to Delete

```kotlin
class SwipeToDeleteActivity : AppCompatActivity() {

    private lateinit var adapter: MyAdapter
    private val items = mutableListOf<Item>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        adapter = MyAdapter(items)
        val recyclerView = findViewById<RecyclerView>(R.id.recyclerView)
        recyclerView.adapter = adapter

        // Swipe для удаления
        val swipeHandler = object : ItemTouchHelper.SimpleCallback(
            0,
            ItemTouchHelper.LEFT or ItemTouchHelper.RIGHT
        ) {
            override fun onMove(
                recyclerView: RecyclerView,
                viewHolder: RecyclerView.ViewHolder,
                target: RecyclerView.ViewHolder
            ): Boolean = false

            override fun onSwiped(viewHolder: RecyclerView.ViewHolder, direction: Int) {
                val position = viewHolder.adapterPosition
                adapter.removeItem(position)
            }
        }

        val itemTouchHelper = ItemTouchHelper(swipeHandler)
        itemTouchHelper.attachToRecyclerView(recyclerView)
    }
}
```

### 5. С функциональностью Undo

```kotlin
class UndoDeleteAdapter(private val items: MutableList<Item>) : RecyclerView.Adapter<ViewHolder>() {

    private var recentlyDeletedItem: Item? = null
    private var recentlyDeletedPosition: Int = -1

    fun removeItem(position: Int) {
        recentlyDeletedItem = items[position]
        recentlyDeletedPosition = position

        items.removeAt(position)
        notifyItemRemoved(position)
    }

    fun undoDelete() {
        recentlyDeletedItem?.let { item ->
            items.add(recentlyDeletedPosition, item)
            notifyItemInserted(recentlyDeletedPosition)
        }
    }
}

// Использование в Activity
class MainActivity : AppCompatActivity() {
    private fun deleteItemWithUndo(position: Int) {
        adapter.removeItem(position)

        Snackbar.make(binding.root, "Элемент удален", Snackbar.LENGTH_LONG)
            .setAction("ОТМЕНИТЬ") {
                adapter.undoDelete()
            }
            .show()
    }
}
```

### 6. AsyncListDiffer для фонового Diff

```kotlin
class AsyncAdapter : RecyclerView.Adapter<ViewHolder>() {

    private val diffCallback = object : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item) = oldItem.id == newItem.id
        override fun areContentsTheSame(oldItem: Item, newItem: Item) = oldItem == newItem
    }

    private val differ = AsyncListDiffer(this, diffCallback)

    val currentList: List<Item>
        get() = differ.currentList

    fun submitList(list: List<Item>) {
        differ.submitList(list)
    }

    fun removeItem(item: Item) {
        val newList = currentList.toMutableList()
        newList.remove(item)
        submitList(newList)
    }
}
```

### Сравнение методов

| Метод | Анимация | Производительность | Случай использования |
|--------|-----------|-------------|----------|
| `notifyDataSetChanged()` | - Нет | - Плохая | Избегайте, если возможно |
| `notifyItemRemoved()` | - Да | - Хорошая | Удаление одного элемента |
| `notifyItemRangeRemoved()` | - Да | - Хорошая | Множественные элементы |
| `DiffUtil` | - Да | - Лучшая | Сложные изменения |
| `ListAdapter` | - Да | - Лучшая | Рекомендуется |

### Лучшие практики

1. - Используйте `notifyItemRemoved()` для одиночных удалений
2. - Используйте `ListAdapter` с DiffUtil для современных приложений
3. - Избегайте `notifyDataSetChanged()` - нет анимаций
4. - Обновляйте модель данных ПЕРЕД вызовом notify
5. - Используйте `notifyItemRangeChanged()` для обновления позиций
6. - Реализуйте функциональность undo для лучшего UX

---

## Related Questions

### Prerequisites (Easier)
- [[q-why-separate-ui-and-business-logic--android--easy]] - Ui
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - Ui
- [[q-recyclerview-sethasfixedsize--android--easy]] - Ui

### Related (Medium)
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Ui
- [[q-dagger-build-time-optimization--android--medium]] - Ui
- [[q-rxjava-pagination-recyclerview--android--medium]] - Ui
- [[q-build-optimization-gradle--android--medium]] - Ui
- [[q-testing-compose-ui--android--medium]] - Ui
