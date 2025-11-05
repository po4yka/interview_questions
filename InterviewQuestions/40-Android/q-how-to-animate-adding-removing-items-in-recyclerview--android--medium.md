---
id: android-419
title: "How To Animate Adding/Removing Items In RecyclerView / Как анимировать добавление и удаление элементов в RecyclerView"
aliases: [How To Animate Adding Removing Items In RecyclerView, Как анимировать добавление и удаление элементов в RecyclerView]
topic: android
subtopics: [ui-animation]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-bundle-data-types--android--medium, q-compositionlocal-advanced--jetpack-compose--medium, q-stack-heap-memory-multiple-threads--android--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [android/ui-animation, animations, difficulty/medium, recyclerview]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, November 1st 2025, 5:43:35 pm
---

# What Needs to Be Used to Animate adding/removing Items in RecyclerView?

## EN (expanded)

To animate item additions and removals in RecyclerView, you use **ItemAnimator** (default is **DefaultItemAnimator**) combined with proper adapter notifications or **DiffUtil**.

### 1. DefaultItemAnimator (Built-in)

RecyclerView includes a default animator:

```kotlin
recyclerView.itemAnimator = DefaultItemAnimator()
// This is actually the default, so you don't need to set it explicitly
```

### 2. Basic Item Notifications

```kotlin
class MyAdapter : RecyclerView.Adapter<MyAdapter.ViewHolder>() {
    private val items = mutableListOf<String>()

    fun addItem(item: String) {
        items.add(item)
        notifyItemInserted(items.size - 1)
        // Animation triggers automatically
    }

    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)
        // Animation triggers automatically
    }

    fun removeItem(item: String) {
        val position = items.indexOf(item)
        if (position != -1) {
            items.removeAt(position)
            notifyItemRemoved(position)
            notifyItemRangeChanged(position, items.size)
        }
    }

    fun moveItem(fromPosition: Int, toPosition: Int) {
        val item = items.removeAt(fromPosition)
        items.add(toPosition, item)
        notifyItemMoved(fromPosition, toPosition)
        // Move animation triggers
    }

    // ... rest of adapter
}
```

### 3. DiffUtil for Automatic Animations

DiffUtil calculates differences and triggers appropriate animations:

```kotlin
class SmartAdapter : RecyclerView.Adapter<SmartAdapter.ViewHolder>() {
    private var items = listOf<Item>()

    fun updateItems(newItems: List<Item>) {
        val diffCallback = ItemDiffCallback(items, newItems)
        val diffResult = DiffUtil.calculateDiff(diffCallback)

        items = newItems
        diffResult.dispatchUpdatesTo(this)
        // DiffUtil triggers appropriate animations
    }

    class ItemDiffCallback(
        private val oldList: List<Item>,
        private val newList: List<Item>
    ) : DiffUtil.Callback() {

        override fun getOldListSize() = oldList.size
        override fun getNewListSize() = newList.size

        override fun areItemsTheSame(oldPos: Int, newPos: Int): Boolean {
            return oldList[oldPos].id == newList[newPos].id
        }

        override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
            return oldList[oldPos] == newList[newPos]
        }
    }
}
```

### 4. ListAdapter (Recommended)

ListAdapter automatically handles DiffUtil and animations:

```kotlin
class ModernAdapter : ListAdapter<Item, ModernAdapter.ViewHolder>(ItemComparator) {

    fun addItem(item: Item) {
        val newList = currentList.toMutableList()
        newList.add(item)
        submitList(newList)
        // Animations handled automatically
    }

    fun removeItem(position: Int) {
        val newList = currentList.toMutableList()
        newList.removeAt(position)
        submitList(newList)
        // Animations handled automatically
    }

    fun removeItem(item: Item) {
        val newList = currentList.toMutableList()
        newList.remove(item)
        submitList(newList)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemLayoutBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ViewHolder(private val binding: ItemLayoutBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(item: Item) {
            binding.titleText.text = item.title
            binding.descriptionText.text = item.description
        }
    }

    object ItemComparator : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem == newItem
        }
    }
}
```

### 5. Custom ItemAnimator

Create custom animations:

```kotlin
class CustomItemAnimator : DefaultItemAnimator() {

    override fun animateAdd(holder: RecyclerView.ViewHolder): Boolean {
        holder.itemView.alpha = 0f
        holder.itemView.animate()
            .alpha(1f)
            .setDuration(300)
            .start()
        return super.animateAdd(holder)
    }

    override fun animateRemove(holder: RecyclerView.ViewHolder): Boolean {
        holder.itemView.animate()
            .alpha(0f)
            .scaleX(0f)
            .scaleY(0f)
            .setDuration(300)
            .start()
        return super.animateRemove(holder)
    }
}

// Usage
recyclerView.itemAnimator = CustomItemAnimator()
```

### 6. Advanced Custom Animator

```kotlin
class SlideInItemAnimator : SimpleItemAnimator() {

    override fun animateAdd(holder: RecyclerView.ViewHolder): Boolean {
        holder.itemView.apply {
            translationX = width.toFloat()
            alpha = 0f

            animate()
                .translationX(0f)
                .alpha(1f)
                .setDuration(300)
                .setListener(object : AnimatorListenerAdapter() {
                    override fun onAnimationEnd(animation: Animator) {
                        dispatchAddFinished(holder)
                    }
                })
                .start()
        }
        return true
    }

    override fun animateRemove(holder: RecyclerView.ViewHolder): Boolean {
        holder.itemView.animate()
            .translationX(-holder.itemView.width.toFloat())
            .alpha(0f)
            .setDuration(300)
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    dispatchRemoveFinished(holder)
                }
            })
            .start()
        return true
    }

    override fun animateMove(
        holder: RecyclerView.ViewHolder,
        fromX: Int, fromY: Int,
        toX: Int, toY: Int
    ): Boolean {
        holder.itemView.apply {
            translationX = (fromX - toX).toFloat()
            translationY = (fromY - toY).toFloat()

            animate()
                .translationX(0f)
                .translationY(0f)
                .setDuration(300)
                .setListener(object : AnimatorListenerAdapter() {
                    override fun onAnimationEnd(animation: Animator) {
                        dispatchMoveFinished(holder)
                    }
                })
                .start()
        }
        return true
    }

    override fun animateChange(
        oldHolder: RecyclerView.ViewHolder,
        newHolder: RecyclerView.ViewHolder?,
        fromLeft: Int, fromTop: Int,
        toLeft: Int, toTop: Int
    ): Boolean {
        if (newHolder != null) {
            newHolder.itemView.alpha = 0f
            newHolder.itemView.animate()
                .alpha(1f)
                .setDuration(300)
                .setListener(object : AnimatorListenerAdapter() {
                    override fun onAnimationEnd(animation: Animator) {
                        dispatchChangeFinished(newHolder, false)
                    }
                })
                .start()
        }

        oldHolder.itemView.animate()
            .alpha(0f)
            .setDuration(300)
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    dispatchChangeFinished(oldHolder, true)
                }
            })
            .start()

        return true
    }

    override fun runPendingAnimations() {
        // Handle any pending animations
    }

    override fun endAnimation(item: RecyclerView.ViewHolder) {
        item.itemView.animate().cancel()
    }

    override fun endAnimations() {
        // Cancel all animations
    }

    override fun isRunning(): Boolean {
        return false // Check if any animations are running
    }
}

// Usage
recyclerView.itemAnimator = SlideInItemAnimator()
```

### 7. Complete Example with Swipe to Delete

```kotlin
class AnimatedListActivity : AppCompatActivity() {

    private lateinit var adapter: ModernAdapter
    private val items = mutableListOf<Item>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_list)

        // Setup RecyclerView
        adapter = ModernAdapter()
        recyclerView.apply {
            adapter = this@AnimatedListActivity.adapter
            layoutManager = LinearLayoutManager(this@AnimatedListActivity)
            itemAnimator = DefaultItemAnimator() // Or custom animator
        }

        // Setup swipe to delete with animation
        val itemTouchHelper = ItemTouchHelper(object : ItemTouchHelper.SimpleCallback(
            0,
            ItemTouchHelper.LEFT or ItemTouchHelper.RIGHT
        ) {
            override fun onMove(
                recyclerView: RecyclerView,
                viewHolder: RecyclerView.ViewHolder,
                target: RecyclerView.ViewHolder
            ) = false

            override fun onSwiped(viewHolder: RecyclerView.ViewHolder, direction: Int) {
                val position = viewHolder.adapterPosition
                val item = adapter.currentList[position]

                // Remove with animation
                adapter.removeItem(position)

                // Show undo
                Snackbar.make(recyclerView, "Item deleted", Snackbar.LENGTH_LONG)
                    .setAction("Undo") {
                        // Restore with animation
                        val restoreList = adapter.currentList.toMutableList()
                        restoreList.add(position, item)
                        adapter.submitList(restoreList)
                    }
                    .show()
            }
        })

        itemTouchHelper.attachToRecyclerView(recyclerView)

        // Add button
        fabAdd.setOnClickListener {
            val newItem = Item("${items.size}", "New Item", "Description")
            adapter.addItem(newItem)

            // Scroll to new item
            recyclerView.smoothScrollToPosition(adapter.itemCount - 1)
        }

        // Load initial data
        loadItems()
    }

    private fun loadItems() {
        adapter.submitList(items)
    }
}
```

### 8. Animation Duration Configuration

```kotlin
// Configure default animator
val animator = DefaultItemAnimator()
animator.addDuration = 300
animator.removeDuration = 300
animator.moveDuration = 300
animator.changeDuration = 300

recyclerView.itemAnimator = animator
```

### 9. Disabling Specific Animations

```kotlin
// Disable change animations (useful for flickering issues)
(recyclerView.itemAnimator as? SimpleItemAnimator)?.supportsChangeAnimations = false

// Or create custom animator without change animations
class NoChangeItemAnimator : DefaultItemAnimator() {
    init {
        supportsChangeAnimations = false
    }
}
```

### 10. Best Practices

```kotlin
class BestPracticeAdapter : ListAdapter<Item, BestPracticeAdapter.ViewHolder>(ItemComparator) {

    // Use ListAdapter - handles DiffUtil automatically
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        // Create view holder
        return ViewHolder(/* ... */)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    // Stable IDs improve animation performance
    init {
        setHasStableIds(true)
    }

    override fun getItemId(position: Int): Long {
        return getItem(position).id.hashCode().toLong()
    }

    // Item comparator for DiffUtil
    object ItemComparator : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem == newItem
        }

        // Optional: Provide payload for partial updates
        override fun getChangePayload(oldItem: Item, newItem: Item): Any? {
            return if (oldItem.title != newItem.title) {
                "title_changed"
            } else {
                null
            }
        }
    }

    // Handle partial updates
    override fun onBindViewHolder(holder: ViewHolder, position: Int, payloads: MutableList<Any>) {
        if (payloads.isEmpty()) {
            super.onBindViewHolder(holder, position, payloads)
        } else {
            // Update only changed parts
            val item = getItem(position)
            if (payloads.contains("title_changed")) {
                holder.updateTitle(item.title)
            }
        }
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(item: Item) {
            // Bind all data
        }

        fun updateTitle(title: String) {
            // Update only title
        }
    }
}
```

### Summary

**Essential Components:**
1. **ItemAnimator** (DefaultItemAnimator is default)
2. **Proper notifications** (notifyItemInserted, notifyItemRemoved, etc.)
3. **DiffUtil** or **ListAdapter** for automatic detection
4. **Stable IDs** for better performance

**Quick Setup:**
```kotlin
// Minimal setup with animations
recyclerView.adapter = ListAdapter(/* ... */)
recyclerView.itemAnimator = DefaultItemAnimator() // Optional, it's default

// Animations work automatically with ListAdapter.submitList()
```

---

## RU (расширенный ответ)

Для анимации добавления и удаления элементов в RecyclerView используется **ItemAnimator** (по умолчанию **DefaultItemAnimator**) в сочетании с правильными уведомлениями адаптера или **DiffUtil**.

### 1. DefaultItemAnimator (Встроенный)

RecyclerView включает анимацию по умолчанию:

```kotlin
recyclerView.itemAnimator = DefaultItemAnimator()
// Это фактически значение по умолчанию, поэтому явно устанавливать не обязательно
```

### 2. Базовые Уведомления Элементов

```kotlin
class MyAdapter : RecyclerView.Adapter<MyAdapter.ViewHolder>() {
    private val items = mutableListOf<String>()

    fun addItem(item: String) {
        items.add(item)
        notifyItemInserted(items.size - 1)
        // Анимация срабатывает автоматически
    }

    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)
        // Анимация срабатывает автоматически
    }

    fun removeItem(item: String) {
        val position = items.indexOf(item)
        if (position != -1) {
            items.removeAt(position)
            notifyItemRemoved(position)
            notifyItemRangeChanged(position, items.size)
        }
    }

    fun moveItem(fromPosition: Int, toPosition: Int) {
        val item = items.removeAt(fromPosition)
        items.add(toPosition, item)
        notifyItemMoved(fromPosition, toPosition)
        // Срабатывает анимация перемещения
    }

    // ... остальной код адаптера
}
```

### 3. DiffUtil Для Автоматических Анимаций

DiffUtil вычисляет различия и запускает соответствующие анимации:

```kotlin
class SmartAdapter : RecyclerView.Adapter<SmartAdapter.ViewHolder>() {
    private var items = listOf<Item>()

    fun updateItems(newItems: List<Item>) {
        val diffCallback = ItemDiffCallback(items, newItems)
        val diffResult = DiffUtil.calculateDiff(diffCallback)

        items = newItems
        diffResult.dispatchUpdatesTo(this)
        // DiffUtil запускает соответствующие анимации
    }

    class ItemDiffCallback(
        private val oldList: List<Item>,
        private val newList: List<Item>
    ) : DiffUtil.Callback() {

        override fun getOldListSize() = oldList.size
        override fun getNewListSize() = newList.size

        override fun areItemsTheSame(oldPos: Int, newPos: Int): Boolean {
            return oldList[oldPos].id == newList[newPos].id
        }

        override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
            return oldList[oldPos] == newList[newPos]
        }
    }
}
```

### 4. ListAdapter (Рекомендуется)

ListAdapter автоматически обрабатывает DiffUtil и анимации:

```kotlin
class ModernAdapter : ListAdapter<Item, ModernAdapter.ViewHolder>(ItemComparator) {

    fun addItem(item: Item) {
        val newList = currentList.toMutableList()
        newList.add(item)
        submitList(newList)
        // Анимации обрабатываются автоматически
    }

    fun removeItem(position: Int) {
        val newList = currentList.toMutableList()
        newList.removeAt(position)
        submitList(newList)
        // Анимации обрабатываются автоматически
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemLayoutBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ViewHolder(private val binding: ItemLayoutBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(item: Item) {
            binding.titleText.text = item.title
            binding.descriptionText.text = item.description
        }
    }

    object ItemComparator : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem == newItem
        }
    }
}
```

### 5. Кастомный ItemAnimator

Создание пользовательских анимаций:

```kotlin
class CustomItemAnimator : DefaultItemAnimator() {

    override fun animateAdd(holder: RecyclerView.ViewHolder): Boolean {
        holder.itemView.alpha = 0f
        holder.itemView.animate()
            .alpha(1f)
            .setDuration(300)
            .start()
        return super.animateAdd(holder)
    }

    override fun animateRemove(holder: RecyclerView.ViewHolder): Boolean {
        holder.itemView.animate()
            .alpha(0f)
            .scaleX(0f)
            .scaleY(0f)
            .setDuration(300)
            .start()
        return super.animateRemove(holder)
    }
}

// Использование
recyclerView.itemAnimator = CustomItemAnimator()
```

### 6. Продвинутый Кастомный Аниматор

```kotlin
class SlideInItemAnimator : SimpleItemAnimator() {

    override fun animateAdd(holder: RecyclerView.ViewHolder): Boolean {
        holder.itemView.apply {
            translationX = width.toFloat()
            alpha = 0f

            animate()
                .translationX(0f)
                .alpha(1f)
                .setDuration(300)
                .setListener(object : AnimatorListenerAdapter() {
                    override fun onAnimationEnd(animation: Animator) {
                        dispatchAddFinished(holder)
                    }
                })
                .start()
        }
        return true
    }

    override fun animateRemove(holder: RecyclerView.ViewHolder): Boolean {
        holder.itemView.animate()
            .translationX(-holder.itemView.width.toFloat())
            .alpha(0f)
            .setDuration(300)
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    dispatchRemoveFinished(holder)
                }
            })
            .start()
        return true
    }

    override fun animateMove(
        holder: RecyclerView.ViewHolder,
        fromX: Int, fromY: Int,
        toX: Int, toY: Int
    ): Boolean {
        holder.itemView.apply {
            translationX = (fromX - toX).toFloat()
            translationY = (fromY - toY).toFloat()

            animate()
                .translationX(0f)
                .translationY(0f)
                .setDuration(300)
                .setListener(object : AnimatorListenerAdapter() {
                    override fun onAnimationEnd(animation: Animator) {
                        dispatchMoveFinished(holder)
                    }
                })
                .start()
        }
        return true
    }

    override fun animateChange(
        oldHolder: RecyclerView.ViewHolder,
        newHolder: RecyclerView.ViewHolder?,
        fromLeft: Int, fromTop: Int,
        toLeft: Int, toTop: Int
    ): Boolean {
        if (newHolder != null) {
            newHolder.itemView.alpha = 0f
            newHolder.itemView.animate()
                .alpha(1f)
                .setDuration(300)
                .setListener(object : AnimatorListenerAdapter() {
                    override fun onAnimationEnd(animation: Animator) {
                        dispatchChangeFinished(newHolder, false)
                    }
                })
                .start()
        }

        oldHolder.itemView.animate()
            .alpha(0f)
            .setDuration(300)
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    dispatchChangeFinished(oldHolder, true)
                }
            })
            .start()

        return true
    }

    override fun runPendingAnimations() {
        // Обработка отложенных анимаций
    }

    override fun endAnimation(item: RecyclerView.ViewHolder) {
        item.itemView.animate().cancel()
    }

    override fun endAnimations() {
        // Отмена всех анимаций
    }

    override fun isRunning(): Boolean {
        return false // Проверка запущенных анимаций
    }
}

// Использование
recyclerView.itemAnimator = SlideInItemAnimator()
```

### 7. Настройка Длительности Анимации

```kotlin
// Конфигурация стандартного аниматора
val animator = DefaultItemAnimator()
animator.addDuration = 300
animator.removeDuration = 300
animator.moveDuration = 300
animator.changeDuration = 300

recyclerView.itemAnimator = animator
```

### 8. Отключение Определённых Анимаций

```kotlin
// Отключение анимаций изменения (полезно при проблемах с мерцанием)
(recyclerView.itemAnimator as? SimpleItemAnimator)?.supportsChangeAnimations = false

// Или создать кастомный аниматор без анимаций изменения
class NoChangeItemAnimator : DefaultItemAnimator() {
    init {
        supportsChangeAnimations = false
    }
}
```

### 9. Лучшие Практики

```kotlin
class BestPracticeAdapter : ListAdapter<Item, BestPracticeAdapter.ViewHolder>(ItemComparator) {

    // Используйте ListAdapter - обрабатывает DiffUtil автоматически
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        // Создание view holder
        return ViewHolder(/* ... */)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    // Стабильные ID улучшают производительность анимаций
    init {
        setHasStableIds(true)
    }

    override fun getItemId(position: Int): Long {
        return getItem(position).id.hashCode().toLong()
    }

    // Компаратор элементов для DiffUtil
    object ItemComparator : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem == newItem
        }

        // Опционально: Предоставить payload для частичных обновлений
        override fun getChangePayload(oldItem: Item, newItem: Item): Any? {
            return if (oldItem.title != newItem.title) {
                "title_changed"
            } else {
                null
            }
        }
    }

    // Обработка частичных обновлений
    override fun onBindViewHolder(holder: ViewHolder, position: Int, payloads: MutableList<Any>) {
        if (payloads.isEmpty()) {
            super.onBindViewHolder(holder, position, payloads)
        } else {
            // Обновление только изменённых частей
            val item = getItem(position)
            if (payloads.contains("title_changed")) {
                holder.updateTitle(item.title)
            }
        }
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(item: Item) {
            // Привязка всех данных
        }

        fun updateTitle(title: String) {
            // Обновление только заголовка
        }
    }
}
```

### Резюме

**Основные компоненты:**
1. **ItemAnimator** (DefaultItemAnimator по умолчанию)
2. **Правильные уведомления** (notifyItemInserted, notifyItemRemoved и т.д.)
3. **DiffUtil** или **ListAdapter** для автоматического обнаружения
4. **Стабильные ID** для лучшей производительности

**Быстрая настройка:**
```kotlin
// Минимальная настройка с анимациями
recyclerView.adapter = ListAdapter(/* ... */)
recyclerView.itemAnimator = DefaultItemAnimator() // Опционально, это значение по умолчанию

// Анимации работают автоматически с ListAdapter.submitList()
```

**Best Practices:**

1. Используйте `notifyItemInserted()` вместо `notifyDataSetChanged()`
2. ListAdapter + DiffUtil для автоматических анимаций
3. Не забывайте про `dispatchAddFinished()` в custom animators
4. Тестируйте анимации на медленных устройствах
5. Используйте стабильные ID для улучшения производительности

## Follow-ups

- [[q-bundle-data-types--android--medium]]
- [[q-compositionlocal-advanced--jetpack-compose--medium]]
- [[q-stack-heap-memory-multiple-threads--android--medium]]


## References

- https://developer.android.com/develop/ui/views/animations


## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - View, Ui
- [[q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy]] - View, Ui

### Related (Medium)
- q-rxjava-pagination-recyclerview--android--medium - View, Ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - View, Ui
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - View, Ui
- [[q-how-animations-work-in-recyclerview--android--medium]] - View, Ui
- [[q-recyclerview-async-list-differ--android--medium]] - View, Ui
