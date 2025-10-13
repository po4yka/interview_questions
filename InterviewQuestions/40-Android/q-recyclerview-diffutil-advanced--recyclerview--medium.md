---
tags:
  - recyclerview
  - diffutil
  - performance
  - lists
difficulty: medium
status: draft
---

# RecyclerView DiffUtil Advanced

# Question (EN)
> How does DiffUtil work internally? Explain the Myers diff algorithm, implementing custom DiffUtil.Callback, using ListAdapter, and optimizing DiffUtil for large datasets.

# Вопрос (RU)
> Как работает DiffUtil внутренне? Объясните алгоритм Myers diff, реализацию пользовательского DiffUtil.Callback, использование ListAdapter и оптимизацию DiffUtil для больших наборов данных.

---

## Answer (EN)

**DiffUtil** is a utility class that calculates the difference between two lists and outputs a list of update operations. It's essential for efficient RecyclerView updates without full dataset refreshes.

### Why DiffUtil?

**Without DiffUtil:**
```kotlin
//  BAD - Inefficient
fun updateData(newList: List<Item>) {
    items = newList
    notifyDataSetChanged() // Refreshes EVERYTHING, loses scroll position, animations
}
```

**With DiffUtil:**
```kotlin
//  GOOD - Efficient, animated updates
fun updateData(newList: List<Item>) {
    val diffResult = DiffUtil.calculateDiff(ItemDiffCallback(items, newList))
    items = newList
    diffResult.dispatchUpdatesTo(this) // Only updates changed items
}
```

**Benefits:**
- Only changed items are updated
- Smooth animations
- Preserves scroll position
- Better performance

---

### How DiffUtil Works (Myers Algorithm)

DiffUtil uses the **Myers diff algorithm** to find the minimum number of operations to transform one list into another.

**Algorithm steps:**
1. Build a "snake" graph of common elements
2. Find shortest edit path (minimum operations)
3. Generate list of operations (insert, delete, move, change)

**Time complexity:** O(N + D²) where:
- N = size of lists
- D = number of differences

**Space complexity:** O(N + D²)

**Example:**

```
Old list: [A, B, C, D]
New list: [A, C, D, E]

Operations:
1. Keep A (position 0)
2. Delete B (position 1)
3. Keep C (position 2 → 1)
4. Keep D (position 3 → 2)
5. Insert E (position 3)

Result: Only B is removed, E is inserted, C and D are kept
```

---

### Basic DiffUtil Implementation

```kotlin
data class Item(
    val id: Long,
    val name: String,
    val description: String
)

class ItemDiffCallback(
    private val oldList: List<Item>,
    private val newList: List<Item>
) : DiffUtil.Callback() {

    // Return sizes
    override fun getOldListSize(): Int = oldList.size
    override fun getNewListSize(): Int = newList.size

    //  Are items the same entity? (same ID)
    override fun areItemsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        return oldList[oldItemPosition].id == newList[newItemPosition].id
    }

    //  Are item contents the same? (all properties equal)
    override fun areContentsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        val oldItem = oldList[oldItemPosition]
        val newItem = newList[newItemPosition]
        return oldItem == newItem
    }

    //  Optional: What specifically changed? (for partial updates)
    override fun getChangePayload(oldItemPosition: Int, newItemPosition: Int): Any? {
        val oldItem = oldList[oldItemPosition]
        val newItem = newList[newItemPosition]

        val changes = mutableMapOf<String, Any>()

        if (oldItem.name != newItem.name) {
            changes["name"] = newItem.name
        }

        if (oldItem.description != newItem.description) {
            changes["description"] = newItem.description
        }

        return if (changes.isNotEmpty()) changes else null
    }
}

// Usage in adapter
class ItemAdapter : RecyclerView.Adapter<ItemAdapter.ViewHolder>() {

    private var items = emptyList<Item>()

    fun updateData(newItems: List<Item>) {
        val diffCallback = ItemDiffCallback(items, newItems)
        val diffResult = DiffUtil.calculateDiff(diffCallback)

        items = newItems
        diffResult.dispatchUpdatesTo(this)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int, payloads: List<Any>) {
        if (payloads.isEmpty()) {
            // Full bind
            super.onBindViewHolder(holder, position, payloads)
        } else {
            // Partial bind (only changed properties)
            val item = items[position]

            @Suppress("UNCHECKED_CAST")
            val changes = payloads[0] as Map<String, Any>

            changes["name"]?.let { holder.nameView.text = it as String }
            changes["description"]?.let { holder.descView.text = it as String }
        }
    }

    // ... other adapter methods
}
```

---

### ListAdapter - Simplified DiffUtil

**ListAdapter** handles DiffUtil automatically with cleaner API.

```kotlin
class ItemAdapter : ListAdapter<Item, ItemAdapter.ViewHolder>(ItemDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = getItem(position) // ListAdapter provides this
        holder.bind(item)
    }

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        private val nameView: TextView = view.findViewById(R.id.name)
        private val descView: TextView = view.findViewById(R.id.description)

        fun bind(item: Item) {
            nameView.text = item.name
            descView.text = item.description
        }
    }

    // Static DiffCallback (more efficient)
    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem == newItem
        }
    }
}

// Usage - super simple!
val adapter = ItemAdapter()
recyclerView.adapter = adapter

// Update data
adapter.submitList(newItems) // DiffUtil calculated automatically on background thread!
```

**Benefits of ListAdapter:**
- Automatic background thread calculation
- Cleaner API
- Less boilerplate
- Built-in thread safety

---

### Async DiffUtil (Large Datasets)

For large lists, calculate diff on background thread.

```kotlin
class ItemAdapter : RecyclerView.Adapter<ItemAdapter.ViewHolder>() {

    private var items = emptyList<Item>()
    private val handler = Handler(Looper.getMainLooper())

    fun updateDataAsync(newItems: List<Item>) {
        val oldList = items

        // Calculate diff on background thread
        Thread {
            val diffCallback = ItemDiffCallback(oldList, newItems)
            val diffResult = DiffUtil.calculateDiff(diffCallback)

            // Apply updates on main thread
            handler.post {
                items = newItems
                diffResult.dispatchUpdatesTo(this)
            }
        }.start()
    }

    // ... rest of adapter
}
```

**Or use AsyncListDiffer:**

```kotlin
class ItemAdapter : RecyclerView.Adapter<ItemAdapter.ViewHolder>() {

    private val differ = AsyncListDiffer(this, ItemDiffCallback())

    // Access current list
    private val items: List<Item>
        get() = differ.currentList

    fun updateData(newItems: List<Item>) {
        differ.submitList(newItems) // Automatically async!
    }

    override fun getItemCount(): Int = items.size

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]
        holder.bind(item)
    }

    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem == newItem
        }
    }
}
```

---

### Optimizing DiffUtil Performance

**1. Implement efficient equals()**

```kotlin
data class Item(
    val id: Long,
    val name: String,
    val description: String,
    val imageUrl: String,
    val metadata: Map<String, Any> // Expensive to compare
) {
    //  Optimize equals to skip expensive comparisons when possible
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Item) return false

        // Check cheap properties first
        if (id != other.id) return false
        if (name != other.name) return false
        if (description != other.description) return false
        if (imageUrl != other.imageUrl) return false

        // Only check expensive property if everything else matches
        if (metadata != other.metadata) return false

        return true
    }

    override fun hashCode(): Int {
        var result = id.hashCode()
        result = 31 * result + name.hashCode()
        result = 31 * result + description.hashCode()
        result = 31 * result + imageUrl.hashCode()
        // Don't include expensive metadata in hashCode
        return result
    }
}
```

**2. Use stable IDs**

```kotlin
class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
    override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {
        //  Compare by ID only (fast)
        return oldItem.id == newItem.id
    }

    override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
        //  Use data class equals (efficient)
        return oldItem == newItem
    }
}
```

**3. Limit list size with pagination**

```kotlin
// Don't use DiffUtil for lists > 10,000 items
// Use Paging 3 library instead
```

**4. Debounce rapid updates**

```kotlin
class ItemAdapter : ListAdapter<Item, ItemAdapter.ViewHolder>(ItemDiffCallback()) {

    private var pendingUpdate: List<Item>? = null
    private val updateHandler = Handler(Looper.getMainLooper())
    private val updateRunnable = Runnable {
        pendingUpdate?.let { submitList(it) }
        pendingUpdate = null
    }

    fun updateDataDebounced(newItems: List<Item>, delayMs: Long = 300) {
        pendingUpdate = newItems
        updateHandler.removeCallbacks(updateRunnable)
        updateHandler.postDelayed(updateRunnable, delayMs)
    }
}
```

---

### Partial Updates with Payloads

**Use payloads for efficient partial updates:**

```kotlin
class ItemAdapter : RecyclerView.Adapter<ItemAdapter.ViewHolder>() {

    override fun onBindViewHolder(
        holder: ViewHolder,
        position: Int,
        payloads: List<Any>
    ) {
        if (payloads.isEmpty()) {
            // Full bind
            onBindViewHolder(holder, position)
        } else {
            // Partial bind
            val item = items[position]

            @Suppress("UNCHECKED_CAST")
            payloads.forEach { payload ->
                when (payload) {
                    is Bundle -> {
                        // Update only changed fields
                        if (payload.containsKey("name")) {
                            holder.nameView.text = item.name
                        }
                        if (payload.containsKey("likeCount")) {
                            holder.likeCountView.text = item.likeCount.toString()
                        }
                    }
                }
            }
        }
    }

    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item) =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: Item, newItem: Item) =
            oldItem == newItem

        // Return what changed
        override fun getChangePayload(oldItem: Item, newItem: Item): Any? {
            val bundle = Bundle()

            if (oldItem.name != newItem.name) {
                bundle.putString("name", newItem.name)
            }

            if (oldItem.likeCount != newItem.likeCount) {
                bundle.putInt("likeCount", newItem.likeCount)
            }

            return if (bundle.isEmpty) null else bundle
        }
    }
}
```

---

### Real-World Example: Social Feed

```kotlin
data class Post(
    val id: Long,
    val authorName: String,
    val authorAvatar: String,
    val content: String,
    val imageUrl: String?,
    val likeCount: Int,
    val isLiked: Boolean,
    val commentCount: Int,
    val timestamp: Long
)

class PostAdapter : ListAdapter<Post, PostAdapter.ViewHolder>(PostDiffCallback()) {

    var onLikeClick: ((Post) -> Unit)? = null
    var onCommentClick: ((Post) -> Unit)? = null

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemPostBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    override fun onBindViewHolder(
        holder: ViewHolder,
        position: Int,
        payloads: List<Any>
    ) {
        if (payloads.isEmpty()) {
            super.onBindViewHolder(holder, position, payloads)
        } else {
            // Partial update for like button
            holder.bindPartial(getItem(position), payloads)
        }
    }

    inner class ViewHolder(
        private val binding: ItemPostBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(post: Post) {
            binding.authorName.text = post.authorName
            binding.content.text = post.content
            binding.likeCount.text = post.likeCount.toString()
            binding.commentCount.text = post.commentCount.toString()

            // Load images
            Glide.with(binding.root)
                .load(post.authorAvatar)
                .into(binding.authorAvatar)

            post.imageUrl?.let { url ->
                binding.postImage.isVisible = true
                Glide.with(binding.root)
                    .load(url)
                    .into(binding.postImage)
            } ?: run {
                binding.postImage.isVisible = false
            }

            // Like button state
            binding.likeButton.setImageResource(
                if (post.isLiked) R.drawable.ic_liked
                else R.drawable.ic_like
            )

            binding.likeButton.setOnClickListener {
                onLikeClick?.invoke(post)
            }

            binding.commentButton.setOnClickListener {
                onCommentClick?.invoke(post)
            }
        }

        fun bindPartial(post: Post, payloads: List<Any>) {
            payloads.forEach { payload ->
                if (payload is Bundle) {
                    // Only update changed fields
                    if (payload.containsKey("likeCount")) {
                        binding.likeCount.text = post.likeCount.toString()
                    }

                    if (payload.containsKey("isLiked")) {
                        binding.likeButton.setImageResource(
                            if (post.isLiked) R.drawable.ic_liked
                            else R.drawable.ic_like
                        )
                    }

                    if (payload.containsKey("commentCount")) {
                        binding.commentCount.text = post.commentCount.toString()
                    }
                }
            }
        }
    }

    class PostDiffCallback : DiffUtil.ItemCallback<Post>() {
        override fun areItemsTheSame(oldItem: Post, newItem: Post): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Post, newItem: Post): Boolean {
            return oldItem == newItem
        }

        override fun getChangePayload(oldItem: Post, newItem: Post): Any? {
            val bundle = Bundle()

            if (oldItem.likeCount != newItem.likeCount) {
                bundle.putInt("likeCount", newItem.likeCount)
            }

            if (oldItem.isLiked != newItem.isLiked) {
                bundle.putBoolean("isLiked", newItem.isLiked)
            }

            if (oldItem.commentCount != newItem.commentCount) {
                bundle.putInt("commentCount", newItem.commentCount)
            }

            return if (bundle.isEmpty) null else bundle
        }
    }
}
```

---

### Performance Benchmarks

**Test: Updating 1,000 items, 10 items changed**

| Method | Time | Animations | Scroll Position |
|--------|------|------------|-----------------|
| `notifyDataSetChanged()` | ~50ms |  No |  Lost |
| `DiffUtil` (sync) | ~15ms |  Yes |  Kept |
| `ListAdapter` (async) | ~1ms (UI) |  Yes |  Kept |

**DiffUtil is 3x faster and provides better UX!**

---

### Best Practices

**1. Use ListAdapter when possible**
```kotlin
//  Simplest and most efficient
class MyAdapter : ListAdapter<Item, ViewHolder>(DiffCallback())
```

**2. Implement efficient equals()**
```kotlin
//  Check cheap properties first
override fun areContentsTheSame(old: Item, new: Item): Boolean {
    if (old.id != new.id) return false // Fast check first
    return old == new // Full comparison
}
```

**3. Use payloads for partial updates**
```kotlin
//  Only update changed views
override fun getChangePayload(old: Item, new: Item): Any? {
    // Return what changed
}
```

**4. Stable IDs for better performance**
```kotlin
init {
    setHasStableIds(true)
}

override fun getItemId(position: Int): Long {
    return items[position].id
}
```

**5. Consider pagination for large lists**
```kotlin
// For lists > 10,000 items, use Paging 3 instead of DiffUtil
```

---

### Summary

**DiffUtil benefits:**
- Efficient updates (only changed items)
- Smooth animations
- Preserves scroll position
- Better performance than `notifyDataSetChanged()`

**How it works:**
- Myers diff algorithm
- O(N + D²) complexity
- Finds minimum operations

**Implementation options:**
1. **DiffUtil.Callback** - Full control
2. **ListAdapter** - Automatic async (recommended)
3. **AsyncListDiffer** - Custom adapter with async

**Performance tips:**
- Use ListAdapter
- Implement efficient equals()
- Use payloads for partial updates
- Debounce rapid updates
- Consider pagination for large lists

**When NOT to use DiffUtil:**
- Very large lists (> 10,000 items) - use Paging 3
- Frequent rapid updates - debounce first
- Simple lists that fully refresh - notifyDataSetChanged() is fine

---

## Ответ (RU)

**DiffUtil** - это утилитный класс, который вычисляет разницу между двумя списками и выдаёт список операций обновления. Это необходимо для эффективных обновлений RecyclerView без полного обновления набора данных.

### Зачем DiffUtil?

**Без DiffUtil:**
```kotlin
//  ПЛОХО - Неэффективно
fun updateData(newList: List<Item>) {
    items = newList
    notifyDataSetChanged() // Обновляет ВСЁ, теряет позицию прокрутки
}
```

**С DiffUtil:**
```kotlin
//  ХОРОШО - Эффективно, анимированные обновления
fun updateData(newList: List<Item>) {
    val diffResult = DiffUtil.calculateDiff(ItemDiffCallback(items, newList))
    items = newList
    diffResult.dispatchUpdatesTo(this) // Обновляет только изменённые элементы
}
```

### ListAdapter - Упрощённый DiffUtil

```kotlin
class ItemAdapter : ListAdapter<Item, ItemAdapter.ViewHolder>(ItemDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        // ...
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = getItem(position)
        holder.bind(item)
    }

    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem == newItem
        }
    }
}

// Использование
adapter.submitList(newItems) // DiffUtil вычисляется автоматически в фоне!
```

### Преимущества ListAdapter

- Автоматическое вычисление в фоновом потоке
- Более чистый API
- Меньше boilerplate кода
- Встроенная безопасность потоков

### Оптимизация производительности

**1. Реализуйте эффективный equals()**
```kotlin
//  Проверяйте дешёвые свойства первыми
override fun areContentsTheSame(old: Item, new: Item): Boolean {
    if (old.id != new.id) return false // Быстрая проверка
    return old == new
}
```

**2. Используйте payloads для частичных обновлений**
```kotlin
override fun getChangePayload(old: Item, new: Item): Any? {
    // Вернуть что изменилось
}
```

**3. Используйте пагинацию для больших списков**
```kotlin
// Для списков > 10,000 элементов используйте Paging 3
```

### Когда НЕ использовать DiffUtil

- Очень большие списки (> 10,000 элементов) - используйте Paging 3
- Частые быстрые обновления - используйте debounce
- Простые списки с полным обновлением - `notifyDataSetChanged()` подойдёт

---

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - View, Ui
- [[q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy]] - View, Ui

### Related (Medium)
- [[q-rxjava-pagination-recyclerview--android--medium]] - View, Ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - View, Ui
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - View, Ui
- [[q-how-animations-work-in-recyclerview--android--medium]] - View, Ui
- [[q-recyclerview-async-list-differ--recyclerview--medium]] - View, Ui

---

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - View, Ui
- [[q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy]] - View, Ui

### Related (Medium)
- [[q-rxjava-pagination-recyclerview--android--medium]] - View, Ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - View, Ui
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - View, Ui
- [[q-how-animations-work-in-recyclerview--android--medium]] - View, Ui
- [[q-recyclerview-async-list-differ--recyclerview--medium]] - View, Ui
