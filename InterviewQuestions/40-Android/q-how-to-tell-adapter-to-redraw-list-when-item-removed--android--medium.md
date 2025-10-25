---
id: 20251017-105057
title: "How To Tell Adapter To Redraw List When Item Removed / Как сказать адаптеру перерисовать список когда элемент удален"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-kotlin-context-receivers--kotlin--hard, q-parsing-optimization-android--android--medium, q-what-navigation-methods-exist-in-kotlin--programming-languages--medium]
created: 2025-10-15
tags: [adapter, difficulty/medium, recyclerview]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:11:12 pm
---

# How to Tell Adapter to Redraw List when Item Removed?

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

---

# Как Сказать Адаптеру Перерисовать Список, Если Какой-то Элемент Удалился

## Ответ (RU)

Если элемент был удален из списка, нужно: (1) Удалить его из списка данных, (2) Сообщить Adapter перерисовать только измененные элементы используя специфичные notify методы.

### Правильный Подход

```kotlin
class MyAdapter(private val items: MutableList<Item>) : RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    // НЕПРАВИЛЬНО: Обновляет весь список, нет анимаций
    fun removeItemBad(position: Int) {
        items.removeAt(position)
        notifyDataSetChanged() // Неэффективно!
    }

    // ПРАВИЛЬНО: Обновляет только затронутый элемент
    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position) // Плавная анимация
    }

    // ЛУЧШЕ: Также обновляет последующие элементы
    fun removeItemWithRange(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)
        notifyItemRangeChanged(position, items.size) // Обновляет позиции
    }
}
```

### Использование DiffUtil (Рекомендуется)

DiffUtil автоматически вычисляет различия между старым и новым списком:

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
        submitList(newList) // DiffUtil автоматически вычислит изменения
    }
}
```

### Все Notify Методы

```kotlin
// Удалить один элемент
fun removeItem(position: Int) {
    items.removeAt(position)
    notifyItemRemoved(position)
}

// Удалить диапазон элементов
fun removeItems(startPosition: Int, count: Int) {
    repeat(count) {
        items.removeAt(startPosition)
    }
    notifyItemRangeRemoved(startPosition, count)
}

// Добавить элемент
fun addItem(position: Int, item: Item) {
    items.add(position, item)
    notifyItemInserted(position)
}

// Обновить элемент
fun updateItem(position: Int, item: Item) {
    items[position] = item
    notifyItemChanged(position)
}

// Переместить элемент
fun moveItem(fromPosition: Int, toPosition: Int) {
    val item = items.removeAt(fromPosition)
    items.add(toPosition, item)
    notifyItemMoved(fromPosition, toPosition)
}
```

### Свайп Для Удаления

Реализация swipe-to-delete с ItemTouchHelper:

```kotlin
class SwipeToDeleteActivity : AppCompatActivity() {

    private lateinit var adapter: MyAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        adapter = MyAdapter(items)
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

        ItemTouchHelper(swipeHandler).attachToRecyclerView(recyclerView)
    }
}
```

### Функциональность Undo

Добавьте возможность отменить удаление:

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
fun deleteItemWithUndo(position: Int) {
    adapter.removeItem(position)

    Snackbar.make(binding.root, "Элемент удален", Snackbar.LENGTH_LONG)
        .setAction("ОТМЕНИТЬ") {
            adapter.undoDelete()
        }
        .show()
}
```

### Сравнение Методов

| Метод | Анимация | Производительность | Случай использования |
|-------|----------|---------------------|----------------------|
| `notifyDataSetChanged()` | Нет | Плохая | Избегать если возможно |
| `notifyItemRemoved()` | Да | Хорошая | Удаление одного элемента |
| `notifyItemRangeRemoved()` | Да | Хорошая | Удаление нескольких элементов |
| `DiffUtil` | Да | Лучшая | Сложные изменения |
| `ListAdapter` | Да | Лучшая | Рекомендуется |

### AsyncListDiffer Для Фоновых Вычислений

AsyncListDiffer вычисляет разницу между списками в фоновом потоке:

```kotlin
class AsyncAdapter : RecyclerView.Adapter<ViewHolder>() {

    private val diffCallback = object : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item) =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: Item, newItem: Item) =
            oldItem == newItem
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

    override fun getItemCount() = currentList.size

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(currentList[position])
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(item: Item) {
            itemView.findViewById<TextView>(R.id.textView).text = item.name
        }
    }
}
```

### Продвинутые Сценарии

**Сценарий 1: Множественное удаление с подтверждением**
```kotlin
class MultiSelectAdapter(private val items: MutableList<Item>) :
    RecyclerView.Adapter<MultiSelectAdapter.ViewHolder>() {

    private val selectedItems = mutableSetOf<Int>()
    var isSelectionMode = false
        set(value) {
            field = value
            if (!value) selectedItems.clear()
            notifyDataSetChanged()
        }

    fun toggleSelection(position: Int) {
        if (selectedItems.contains(position)) {
            selectedItems.remove(position)
        } else {
            selectedItems.add(position)
        }
        notifyItemChanged(position)
    }

    fun deleteSelectedItems() {
        // Сортируем в обратном порядке чтобы избежать проблем с индексами
        val sortedPositions = selectedItems.sortedDescending()

        sortedPositions.forEach { position ->
            items.removeAt(position)
            notifyItemRemoved(position)
        }

        selectedItems.clear()
        isSelectionMode = false
    }

    fun getSelectedCount() = selectedItems.size

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_selectable, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position], selectedItems.contains(position), isSelectionMode)
    }

    override fun getItemCount() = items.size

    inner class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val textView: TextView = itemView.findViewById(R.id.textView)
        private val checkBox: CheckBox = itemView.findViewById(R.id.checkBox)

        fun bind(item: Item, isSelected: Boolean, isSelectionMode: Boolean) {
            textView.text = item.name
            checkBox.isVisible = isSelectionMode
            checkBox.isChecked = isSelected

            itemView.setOnClickListener {
                if (isSelectionMode) {
                    toggleSelection(adapterPosition)
                } else {
                    // Обычный клик
                }
            }

            itemView.setOnLongClickListener {
                if (!isSelectionMode) {
                    this@MultiSelectAdapter.isSelectionMode = true
                    toggleSelection(adapterPosition)
                }
                true
            }
        }
    }
}

// Использование в Activity
class MainActivity : AppCompatActivity() {
    private lateinit var adapter: MultiSelectAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        adapter = MultiSelectAdapter(items)
        recyclerView.adapter = adapter

        deleteButton.setOnClickListener {
            if (adapter.getSelectedCount() > 0) {
                AlertDialog.Builder(this)
                    .setTitle("Удаление")
                    .setMessage("Удалить ${adapter.getSelectedCount()} элементов?")
                    .setPositiveButton("Да") { _, _ ->
                        adapter.deleteSelectedItems()
                    }
                    .setNegativeButton("Отмена", null)
                    .show()
            }
        }
    }
}
```

**Сценарий 2: Удаление с анимацией**
```kotlin
class AnimatedAdapter(private val items: MutableList<Item>) :
    RecyclerView.Adapter<AnimatedAdapter.ViewHolder>() {

    fun removeItemWithAnimation(position: Int, recyclerView: RecyclerView) {
        val viewHolder = recyclerView.findViewHolderForAdapterPosition(position)
        viewHolder?.itemView?.let { view ->
            // Анимация исчезновения
            view.animate()
                .alpha(0f)
                .translationX(view.width.toFloat())
                .setDuration(300)
                .withEndAction {
                    items.removeAt(position)
                    notifyItemRemoved(position)
                    notifyItemRangeChanged(position, items.size)
                }
                .start()
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position])

        // Анимация появления
        holder.itemView.alpha = 0f
        holder.itemView.translationX = -holder.itemView.width.toFloat()
        holder.itemView.animate()
            .alpha(1f)
            .translationX(0f)
            .setDuration(300)
            .setStartDelay((position * 50).toLong())
            .start()
    }

    override fun getItemCount() = items.size

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(item: Item) {
            itemView.findViewById<TextView>(R.id.textView).text = item.name
        }
    }
}
```

**Сценарий 3: Оптимизация с payload**
```kotlin
class OptimizedAdapter(private val items: MutableList<Item>) :
    RecyclerView.Adapter<OptimizedAdapter.ViewHolder>() {

    companion object {
        const val PAYLOAD_FAVORITE = "favorite"
        const val PAYLOAD_NAME = "name"
    }

    fun updateItemFavorite(position: Int, isFavorite: Boolean) {
        items[position] = items[position].copy(isFavorite = isFavorite)
        notifyItemChanged(position, PAYLOAD_FAVORITE)
    }

    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position])
    }

    override fun onBindViewHolder(
        holder: ViewHolder,
        position: Int,
        payloads: MutableList<Any>
    ) {
        if (payloads.isEmpty()) {
            super.onBindViewHolder(holder, position, payloads)
        } else {
            // Частичное обновление только измененных элементов
            payloads.forEach { payload ->
                when (payload) {
                    PAYLOAD_FAVORITE -> holder.updateFavorite(items[position].isFavorite)
                    PAYLOAD_NAME -> holder.updateName(items[position].name)
                }
            }
        }
    }

    override fun getItemCount() = items.size

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val textView: TextView = itemView.findViewById(R.id.textView)
        private val favoriteIcon: ImageView = itemView.findViewById(R.id.favoriteIcon)

        fun bind(item: Item) {
            textView.text = item.name
            updateFavorite(item.isFavorite)
        }

        fun updateFavorite(isFavorite: Boolean) {
            favoriteIcon.setImageResource(
                if (isFavorite) R.drawable.ic_favorite_filled
                else R.drawable.ic_favorite_outline
            )
        }

        fun updateName(name: String) {
            textView.text = name
        }
    }
}
```

### Лучшие Практики

1. **Используйте `notifyItemRemoved()`** для удаления одного элемента с анимацией
2. **Используйте `ListAdapter` с DiffUtil** для современных приложений
3. **Избегайте `notifyDataSetChanged()`** - нет анимаций и плохая производительность
4. **Обновляйте модель данных ПЕРЕД вызовом notify** - иначе будет exception
5. **Используйте `notifyItemRangeChanged()`** для обновления позиций после удаления
6. **Реализуйте функциональность undo** для лучшего UX
7. **Тестируйте с различными размерами списков** - от пустого до тысяч элементов
8. **Используйте AsyncListDiffer** для фоновых вычислений больших списков
9. **Используйте payload** для частичных обновлений ViewHolder
10. **Сортируйте позиции в обратном порядке** при множественном удалении

### Распространенные Ошибки

**Ошибка 1: Вызов notify до обновления данных**
```kotlin
// НЕПРАВИЛЬНО
notifyItemRemoved(position)
items.removeAt(position)  // Crash! IndexOutOfBoundsException

// ПРАВИЛЬНО
items.removeAt(position)
notifyItemRemoved(position)
```

**Ошибка 2: Не обновлять позиции после удаления**
```kotlin
// НЕПРАВИЛЬНО - позиции элементов будут неверными
fun removeItem(position: Int) {
    items.removeAt(position)
    notifyItemRemoved(position)
}

// ПРАВИЛЬНО - обновить позиции следующих элементов
fun removeItem(position: Int) {
    items.removeAt(position)
    notifyItemRemoved(position)
    notifyItemRangeChanged(position, items.size)
}
```

**Ошибка 3: Модификация currentList напрямую с ListAdapter**
```kotlin
// НЕПРАВИЛЬНО - не работает с ListAdapter
adapter.currentList.remove(item)
adapter.notifyItemRemoved(position)

// ПРАВИЛЬНО - создать новый список
val newList = adapter.currentList.toMutableList()
newList.remove(item)
adapter.submitList(newList)
```

---

## Related Questions

### Prerequisites (Easier)
- [[q-why-separate-ui-and-business-logic--android--easy]] - Ui
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - Ui
- [[q-recyclerview-sethasfixedsize--android--easy]] - Ui

### Related (Medium)
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Ui
- [[q-dagger-build-time-optimization--android--medium]] - Ui
- q-rxjava-pagination-recyclerview--android--medium - Ui
- [[q-build-optimization-gradle--android--medium]] - Ui
- [[q-testing-compose-ui--android--medium]] - Ui
