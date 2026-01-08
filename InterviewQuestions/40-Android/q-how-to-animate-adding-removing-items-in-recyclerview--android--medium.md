---\
id: android-419
title: How To Animate Adding/Removing Items In RecyclerView / Как анимировать добавление и удаление элементов в RecyclerView
aliases: [How To Animate Adding Removing Items In RecyclerView, Как анимировать добавление и удаление элементов в RecyclerView]
topic: android
subtopics: [ui-animation]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-custom-views, q-bundle-data-types--android--medium, q-how-to-change-number-of-columns-in-recyclerview-based-on-orientation--android--easy, q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy, q-stack-heap-memory-multiple-threads--android--medium, q-what-problems-can-there-be-with-list-items--android--easy]
created: 2025-10-15
updated: 2025-11-10
tags: [android/ui-animation, animations, difficulty/medium, recyclerview]

---\
# Вопрос (RU)
> Как анимировать добавление и удаление элементов в `RecyclerView`

# Question (EN)
> How To Animate Adding/Removing Items In `RecyclerView`

---

## Ответ (RU)

Для анимации добавления и удаления элементов в `RecyclerView` обычно используют:
- ItemAnimator (по умолчанию `DefaultItemAnimator`), и
- точечные уведомления адаптера (`notifyItemInserted`/`notifyItemRemoved` и т.п.) или `DiffUtil`/`ListAdapter`, которые генерируют эти события автоматически.

Кратко:
- `DefaultItemAnimator` уже анимирует вставки/удаления/перемещения, если вы используете точечные `notifyItem*` вместо `notifyDataSetChanged()`.
- `DiffUtil` и `ListAdapter` вычисляют различия между списками и сами вызывают нужные `notifyItem*`, обеспечивая корректные анимации.
- Для более сложных эффектов можно настроить `DefaultItemAnimator` (длительности) или реализовать свой `ItemAnimator`/`SimpleItemAnimator`, аккуратно вызывая `dispatch*`-методы и корректно управляя жизненным циклом анимаций.

## Answer (EN)

To animate adding and removing items in a `RecyclerView` you typically rely on:
- an `ItemAnimator` (by default `DefaultItemAnimator`), and
- fine-grained adapter updates (`notifyItemInserted`/`notifyItemRemoved`, etc.) or `DiffUtil`/`ListAdapter` to produce those updates.

In short:
- `DefaultItemAnimator` already animates insert/remove/move if you use specific `notifyItem*` calls instead of `notifyDataSetChanged()`.
- `DiffUtil` and `ListAdapter` compute list differences and dispatch proper `notifyItem*` calls for you, resulting in smooth, correct animations.
- For advanced visuals, tune `DefaultItemAnimator` (durations) or implement a custom `ItemAnimator`/`SimpleItemAnimator`, making sure to correctly call `dispatch*` methods and manage the animation lifecycle.

## EN (expanded)

To animate item additions and removals in `RecyclerView`, you use:
- ItemAnimator (DefaultItemAnimator by default), and
- correct adapter notifications (notifyItemInserted/Removed/etc.) or DiffUtil/ListAdapter.

### 1. DefaultItemAnimator (Built-in)

`RecyclerView` includes a default animator:

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
        // Animation triggers automatically for the inserted item
    }

    fun removeItem(position: Int) {
        if (position in items.indices) {
            items.removeAt(position)
            notifyItemRemoved(position)
            // Animation triggers automatically for the removed item
        }
    }

    fun removeItem(item: String) {
        val position = items.indexOf(item)
        if (position != -1) {
            items.removeAt(position)
            notifyItemRemoved(position)
            // Avoid unnecessary notifyItemRangeChanged here; DefaultItemAnimator
            // animates based on fine-grained notifications.
        }
    }

    fun moveItem(fromPosition: Int, toPosition: Int) {
        if (fromPosition in items.indices && toPosition in items.indices) {
            val item = items.removeAt(fromPosition)
            items.add(toPosition, item)
            notifyItemMoved(fromPosition, toPosition)
            // Move animation triggers automatically
        }
    }

    // ... rest of adapter
}
```

Key rule: use the specific notifyItem* methods instead of notifyDataSetChanged() to enable animations.

### 3. DiffUtil for Automatic Animations

`DiffUtil` calculates differences and triggers appropriate animations:

```kotlin
class SmartAdapter : RecyclerView.Adapter<SmartAdapter.ViewHolder>() {
    private var items = listOf<Item>()

    fun updateItems(newItems: List<Item>) {
        val diffCallback = ItemDiffCallback(items, newItems)
        val diffResult = DiffUtil.calculateDiff(diffCallback)

        items = newItems
        diffResult.dispatchUpdatesTo(this)
        // DiffUtil triggers insert/remove/move/change animations
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

ListAdapter automatically handles `DiffUtil` and animations:

```kotlin
class ModernAdapter : ListAdapter<Item, ModernAdapter.ViewHolder>(ItemComparator) {

    fun addItem(item: Item) {
        val newList = currentList.toMutableList()
        newList.add(item)
        submitList(newList)
        // Animations handled automatically (uses DiffUtil under the hood)
    }

    fun removeItem(position: Int) {
        if (position in currentList.indices) {
            val newList = currentList.toMutableList()
            newList.removeAt(position)
            submitList(newList)
            // Animations handled automatically
        }
    }

    fun removeItem(item: Item) {
        val newList = currentList.toMutableList()
        if (newList.remove(item)) {
            submitList(newList)
        }
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

Note: ListAdapter can be configured with stable IDs, but in typical usage rely on ItemCallback for identity and avoid mixing identity strategies unless you understand the implications.

### 5. Custom ItemAnimator (Simple Example)

If you only need to tweak durations and rely on DefaultItemAnimator behavior, prefer configuration over overriding animate*.
If you override animateAdd/animateRemove in DefaultItemAnimator, you must not both run your own ViewPropertyAnimator and delegate to super, otherwise you risk duplicate/incorrect animations.

Minimal, safe customization using DefaultItemAnimator configuration:

```kotlin
val animator = DefaultItemAnimator().apply {
    addDuration = 300
    removeDuration = 300
}
recyclerView.itemAnimator = animator
```

For fully custom effects, extend SimpleItemAnimator and manage dispatch* calls and running state properly (see below).

### 6. Advanced Custom Animator (Skeleton)

Example of a custom animator based on SimpleItemAnimator. This is a conceptual skeleton – a production implementation must track pending/running animations and correctly implement dispatch* calls and isRunning/endAnimation/endAnimations.

```kotlin
class SlideInItemAnimator : SimpleItemAnimator() {

    override fun animateAdd(holder: RecyclerView.ViewHolder): Boolean {
        val view = holder.itemView
        view.translationX = view.width.toFloat()
        view.alpha = 0f

        view.animate()
            .translationX(0f)
            .alpha(1f)
            .setDuration(addDuration)
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationStart(animation: Animator) {
                    dispatchAddStarting(holder)
                }

                override fun onAnimationEnd(animation: Animator) {
                    view.translationX = 0f
                    view.alpha = 1f
                    dispatchAddFinished(holder)
                    // In a real implementation you would also update internal tracking here
                }
            })
            .start()

        // Returning true indicates that an animation was started.
        // For correctness, a real implementation must track this animation
        // so that isRunning()/endAnimations() work properly.
        return true
    }

    override fun animateRemove(holder: RecyclerView.ViewHolder): Boolean {
        val view = holder.itemView

        view.animate()
            .translationX(-view.width.toFloat())
            .alpha(0f)
            .setDuration(removeDuration)
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationStart(animation: Animator) {
                    dispatchRemoveStarting(holder)
                }

                override fun onAnimationEnd(animation: Animator) {
                    view.translationX = 0f
                    view.alpha = 1f
                    dispatchRemoveFinished(holder)
                    // In a real implementation you would also update internal tracking here
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
        // Implement if needed; otherwise return false to indicate no custom move animation
        return false
    }

    override fun animateChange(
        oldHolder: RecyclerView.ViewHolder,
        newHolder: RecyclerView.ViewHolder?,
        fromLeft: Int, fromTop: Int,
        toLeft: Int, toTop: Int
    ): Boolean {
        // Implement if needed; otherwise return false
        return false
    }

    override fun runPendingAnimations() {
        // In a complete implementation, start any queued animations here.
    }

    override fun endAnimation(item: RecyclerView.ViewHolder) {
        // Cancel animations specific to this ViewHolder and update tracking.
        item.itemView.animate().cancel()
    }

    override fun endAnimations() {
        // Cancel all running animations and clear tracking in a real implementation.
    }

    override fun isRunning(): Boolean {
        // Return true if any animations are currently running.
        // This skeleton always returns false and is NOT production-ready.
        return false
    }
}

// Usage (demo only)
recyclerView.itemAnimator = SlideInItemAnimator()
```

Note: This SlideInItemAnimator is intentionally incomplete and for conceptual demonstration only. A real ItemAnimator must correctly track pending and running animations to comply with `RecyclerView`'s expectations.

### 7. Complete Example with Swipe to Delete (with ListAdapter)

```kotlin
class AnimatedListActivity : AppCompatActivity() {

    private lateinit var adapter: ModernAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_list)

        adapter = ModernAdapter()

        recyclerView.apply {
            adapter = this@AnimatedListActivity.adapter
            layoutManager = LinearLayoutManager(this@AnimatedListActivity)
            itemAnimator = DefaultItemAnimator() // Or a custom animator
        }

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
                val position = viewHolder.bindingAdapterPosition
                if (position != RecyclerView.NO_POSITION) {
                    val currentList = adapter.currentList
                    if (position < currentList.size) {
                        val item = currentList[position]

                        // Remove with animation via submitList
                        adapter.removeItem(position)

                        Snackbar.make(recyclerView, "Item deleted", Snackbar.LENGTH_LONG)
                            .setAction("Undo") {
                                val restoreList = adapter.currentList.toMutableList()
                                val safePosition = restoreList.coerceIndex(position)
                                restoreList.add(safePosition, item)
                                adapter.submitList(restoreList)
                            }
                            .show()
                    }
                }
            }
        })

        itemTouchHelper.attachToRecyclerView(recyclerView)

        fabAdd.setOnClickListener {
            val newItem = Item(
                id = System.currentTimeMillis().toString(),
                title = "New Item",
                description = "Description"
            )
            adapter.addItem(newItem)
            recyclerView.smoothScrollToPosition(adapter.itemCount - 1)
        }

        loadItems()
    }

    private fun loadItems() {
        // Initial data
        val initialItems = listOf<Item>(
            // ...
        )
        adapter.submitList(initialItems)
    }
}

// Helper extension used above
private fun <T> MutableList<T>.coerceIndex(index: Int): Int =
    when {
        isEmpty() -> 0
        index < 0 -> 0
        index > size -> size
        else -> index
    }
```

This demonstrates how ListAdapter + DefaultItemAnimator provide smooth add/remove animations. It also uses bindingAdapterPosition and validates indices to avoid subtle bugs.

### 8. Disabling/Configuring Specific Animations

```kotlin
// Configure DefaultItemAnimator durations
val animator = DefaultItemAnimator().apply {
    addDuration = 300
    removeDuration = 300
    moveDuration = 300
    changeDuration = 300
}
recyclerView.itemAnimator = animator

// Disable change animations (useful to prevent flicker when using DiffUtil)
(recyclerView.itemAnimator as? SimpleItemAnimator)?.supportsChangeAnimations = false

// Or provide a variant with disabled change animations
class NoChangeItemAnimator : DefaultItemAnimator() {
    init {
        supportsChangeAnimations = false
    }
}
```

### 9. Best Practices (EN)

- Prefer fine-grained notifyItem* calls or DiffUtil/ListAdapter.
- Avoid notifyDataSetChanged() when you want animations.
- With ListAdapter, typically rely on ItemCallback for identity; use stable IDs only if you fully understand how they interact.
- If implementing a custom ItemAnimator:
  - Use SimpleItemAnimator when you need full control.
  - `Call` dispatchAdd/Remove/Move/ChangeStarting/Finished appropriately.
  - Implement isRunning/endAnimation/endAnimations correctly with real tracking.
- Disable change animations if you see blinking with partial updates.
- Test animations on low-end devices to ensure performance.

---

## RU (расширенный ответ)

Для анимации добавления и удаления элементов в `RecyclerView` используются:
- ItemAnimator (по умолчанию DefaultItemAnimator), и
- корректные уведомления адаптера (notifyItemInserted/Removed и т.п.) или DiffUtil/ListAdapter.

### 1. DefaultItemAnimator (Встроенный)

`RecyclerView` включает аниматор по умолчанию:

```kotlin
recyclerView.itemAnimator = DefaultItemAnimator()
// Это значение используется по умолчанию, можно не устанавливать явно
```

### 2. Базовые Уведомления Элементов

```kotlin
class MyAdapter : RecyclerView.Adapter<MyAdapter.ViewHolder>() {
    private val items = mutableListOf<String>()

    fun addItem(item: String) {
        items.add(item)
        notifyItemInserted(items.size - 1)
        // Анимация вставки срабатывает автоматически
    }

    fun removeItem(position: Int) {
        if (position in items.indices) {
            items.removeAt(position)
            notifyItemRemoved(position)
            // Анимация удаления срабатывает автоматически
        }
    }

    fun removeItem(item: String) {
        val position = items.indexOf(item)
        if (position != -1) {
            items.removeAt(position)
            notifyItemRemoved(position)
            // Избегаем лишнего notifyItemRangeChanged: анимации строятся
            // на точечных уведомлениях
        }
    }

    fun moveItem(fromPosition: Int, toPosition: Int) {
        if (fromPosition in items.indices && toPosition in items.indices) {
            val item = items.removeAt(fromPosition)
            items.add(toPosition, item)
            notifyItemMoved(fromPosition, toPosition)
            // Анимация перемещения срабатывает автоматически
        }
    }

    // ... остальной код адаптера
}
```

Ключевое правило: используйте конкретные методы notifyItem* вместо notifyDataSetChanged(), если нужны анимации.

### 3. DiffUtil Для Автоматических Анимаций

`DiffUtil` вычисляет различия и генерирует соответствующие анимации:

```kotlin
class SmartAdapter : RecyclerView.Adapter<SmartAdapter.ViewHolder>() {
    private var items = listOf<Item>()

    fun updateItems(newItems: List<Item>) {
        val diffCallback = ItemDiffCallback(items, newItems)
        val diffResult = DiffUtil.calculateDiff(diffCallback)

        items = newItems
        diffResult.dispatchUpdatesTo(this)
        // DiffUtil вызывает вставки/удаления/перемещения/изменения с анимацией
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

ListAdapter автоматически использует `DiffUtil` и анимирует изменения списка:

```kotlin
class ModernAdapter : ListAdapter<Item, ModernAdapter.ViewHolder>(ItemComparator) {

    fun addItem(item: Item) {
        val newList = currentList.toMutableList()
        newList.add(item)
        submitList(newList)
        // Анимации обрабатываются автоматически
    }

    fun removeItem(position: Int) {
        if (position in currentList.indices) {
            val newList = currentList.toMutableList()
            newList.removeAt(position)
            submitList(newList)
            // Анимации обрабатываются автоматически
        }
    }

    fun removeItem(item: Item) {
        val newList = currentList.toMutableList()
        if (newList.remove(item)) {
            submitList(newList)
        }
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

Примечание: ListAdapter можно настроить для работы со стабильными ID, но в типичном случае опирайтесь на ItemCallback для идентичности и не смешивайте стратегии, если не уверены в последствиях.

### 5. Кастомный ItemAnimator (простая настройка)

Если нужно только изменить скорость/длительность анимаций, обычно достаточно настроить DefaultItemAnimator, не переопределяя animate*.

```kotlin
val animator = DefaultItemAnimator().apply {
    addDuration = 300
    removeDuration = 300
}
recyclerView.itemAnimator = animator
```

Если вы переопределяете animateAdd/animateRemove у DefaultItemAnimator, нельзя одновременно запускать свои ViewPropertyAnimator и вызывать super.animate* — это может привести к двойным или некорректным анимациям. Для полноценного контроля лучше наследоваться от SimpleItemAnimator.

### 6. Продвинутый Кастомный Аниматор (скелет)

Пример на базе SimpleItemAnimator. Это демонстрационный скелет — реальная реализация должна отслеживать pending/running анимации, корректно вызывать dispatch* и правильно реализовывать isRunning/endAnimation/endAnimations.

```kotlin
class SlideInItemAnimator : SimpleItemAnimator() {

    override fun animateAdd(holder: RecyclerView.ViewHolder): Boolean {
        val view = holder.itemView
        view.translationX = view.width.toFloat()
        view.alpha = 0f

        view.animate()
            .translationX(0f)
            .alpha(1f)
            .setDuration(addDuration)
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationStart(animation: Animator) {
                    dispatchAddStarting(holder)
                }

                override fun onAnimationEnd(animation: Animator) {
                    view.translationX = 0f
                    view.alpha = 1f
                    dispatchAddFinished(holder)
                    // В реальной реализации здесь также нужно обновлять состояние трекинга
                }
            })
            .start()

        // true означает, что анимация запущена.
        // Для корректности реальная реализация должна отслеживать эту анимацию,
        // чтобы isRunning()/endAnimations() работали правильно.
        return true
    }

    override fun animateRemove(holder: RecyclerView.ViewHolder): Boolean {
        val view = holder.itemView

        view.animate()
            .translationX(-view.width.toFloat())
            .alpha(0f)
            .setDuration(removeDuration)
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationStart(animation: Animator) {
                    dispatchRemoveStarting(holder)
                }

                override fun onAnimationEnd(animation: Animator) {
                    view.translationX = 0f
                    view.alpha = 1f
                    dispatchRemoveFinished(holder)
                    // В реальной реализации здесь также нужно обновлять состояние трекинга
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
        // Реализуйте при необходимости; иначе верните false, если нет собственной анимации перемещения
        return false
    }

    override fun animateChange(
        oldHolder: RecyclerView.ViewHolder,
        newHolder: RecyclerView.ViewHolder?,
        fromLeft: Int, fromTop: Int,
        toLeft: Int, toTop: Int
    ): Boolean {
        // Реализуйте при необходимости; иначе верните false
        return false
    }

    override fun runPendingAnimations() {
        // В полной реализации здесь должны запускаться отложенные анимации.
    }

    override fun endAnimation(item: RecyclerView.ViewHolder) {
        // Отмените анимации для конкретного ViewHolder и обновите трекинг.
        item.itemView.animate().cancel()
    }

    override fun endAnimations() {
        // В полной реализации отмените все анимации и очистите трекинг.
    }

    override fun isRunning(): Boolean {
        // Верните true, если какие-либо анимации реально выполняются.
        // В текущем скелете всегда false — это НЕ готовое решение.
        return false
    }
}

// Использование (только для демонстрации)
recyclerView.itemAnimator = SlideInItemAnimator()
```

Важно: этот SlideInItemAnimator намеренно неполный и подходит только как концептуальный пример. В реальном проекте необходимо корректно отслеживать состояние анимаций.

### 7. Пример Со Swipe-to-delete (ListAdapter)

```kotlin
class AnimatedListActivity : AppCompatActivity() {

    private lateinit var adapter: ModernAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_list)

        adapter = ModernAdapter()

        recyclerView.apply {
            adapter = this@AnimatedListActivity.adapter
            layoutManager = LinearLayoutManager(this@AnimatedListActivity)
            itemAnimator = DefaultItemAnimator() // Или кастомный аниматор
        }

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
                val position = viewHolder.bindingAdapterPosition
                if (position != RecyclerView.NO_POSITION) {
                    val currentList = adapter.currentList
                    if (position < currentList.size) {
                        val item = currentList[position]

                        // Удаляем через submitList c анимацией
                        adapter.removeItem(position)

                        Snackbar.make(recyclerView, "Item deleted", Snackbar.LENGTH_LONG)
                            .setAction("Undo") {
                                val restoreList = adapter.currentList.toMutableList()
                                val safePosition = restoreList.coerceIndex(position)
                                restoreList.add(safePosition, item)
                                adapter.submitList(restoreList)
                            }
                            .show()
                    }
                }
            }
        })

        itemTouchHelper.attachToRecyclerView(recyclerView)

        fabAdd.setOnClickListener {
            val newItem = Item(
                id = System.currentTimeMillis().toString(),
                title = "New Item",
                description = "Description"
            )
            adapter.addItem(newItem)
            recyclerView.smoothScrollToPosition(adapter.itemCount - 1)
        }

        loadItems()
    }

    private fun loadItems() {
        val initialItems = listOf<Item>(
            // ...
        )
        adapter.submitList(initialItems)
    }
}

// Вспомогательное расширение
private fun <T> MutableList<T>.coerceIndex(index: Int): Int =
    when {
        isEmpty() -> 0
        index < 0 -> 0
        index > size -> size
        else -> index
    }
```

Этот пример показывает, как ListAdapter + DefaultItemAnimator обеспечивают плавные анимации при добавлении/удалении, и демонстрирует использование bindingAdapterPosition и проверок индексов для избежания тонких багов.

### 8. Настройка И Отключение Отдельных Анимаций

```kotlin
// Настройка стандартного аниматора
val animator = DefaultItemAnimator().apply {
    addDuration = 300
    removeDuration = 300
    moveDuration = 300
    changeDuration = 300
}
recyclerView.itemAnimator = animator

// Отключение анимаций изменений (полезно при мерцании с DiffUtil)
(recyclerView.itemAnimator as? SimpleItemAnimator)?.supportsChangeAnimations = false

// Вариант с отключёнными change-анимациями
class NoChangeItemAnimator : DefaultItemAnimator() {
    init {
        supportsChangeAnimations = false
    }
}
```

### 9. Лучшие Практики (RU)

1. Используйте точечные методы notifyItem* или DiffUtil/ListAdapter вместо notifyDataSetChanged(), если нужны анимации.
2. В случае ListAdapter обычно опирайтесь на ItemCallback для идентификации; стабильные ID используйте только если понимаете их взаимодействие.
3. При написании кастомного ItemAnimator:
   - Предпочитайте SimpleItemAnimator для полного контроля.
   - Корректно вызывайте dispatchAdd/Remove/Move/ChangeStarting/Finished.
   - Реализуйте isRunning/endAnimation/endAnimations с реальным трекингом анимаций.
4. Отключайте change-анимации при мерцаниях/частичных обновлениях.
5. Тестируйте анимации на медленных устройствах, следите за производительностью.

### Резюме

Кратко:
- ItemAnimator (DefaultItemAnimator по умолчанию) + точечные notifyItem* уже дают базовые анимации.
- `DiffUtil` или ListAdapter обеспечивают автоматическое вычисление изменений и анимацию добавлений/удалений/перемещений.
- При необходимости — настраивайте durations или пишите кастомный ItemAnimator, корректно управляя dispatch* и состоянием.

## Follow-ups

- [[q-bundle-data-types--android--medium]]
- [[q-compositionlocal-advanced--android--medium]]
- [[q-stack-heap-memory-multiple-threads--android--medium]]

## References

- [Animations](https://developer.android.com/develop/ui/views/animations)

## Related Questions

### Prerequisites / Concepts

- [[c-custom-views]]

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - `View`, Ui
- [[q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy]] - `View`, Ui

### Related (Medium)
- q-rxjava-pagination-recyclerview--android--medium - `View`, Ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - `View`, Ui
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - `View`, Ui
- [[q-how-animations-work-in-recyclerview--android--medium]] - `View`, Ui
- [[q-recyclerview-async-list-differ--android--medium]] - `View`, Ui
