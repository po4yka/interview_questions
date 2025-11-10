---
id: android-350
title: RecyclerView DiffUtil Advanced / Продвинутый DiffUtil для RecyclerView
aliases:
- RecyclerView DiffUtil Advanced
- Продвинутый DiffUtil для RecyclerView
topic: android
subtopics:
- ui-views
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-recyclerview
- q-android-project-parts--android--easy
created: 2025-10-15
updated: 2025-11-10
tags:
- android/ui-views
- difficulty/medium

---

# Вопрос (RU)
> Как работает DiffUtil внутренне? Объясните алгоритм Myers diff, реализацию пользовательского DiffUtil.`Callback`, использование ListAdapter и оптимизацию DiffUtil для больших наборов данных.

# Question (EN)
> How does DiffUtil work internally? Explain the Myers diff algorithm, implementing custom DiffUtil.`Callback`, using ListAdapter, and optimizing DiffUtil for large datasets.

---

## Ответ (RU)

**DiffUtil** — это утилитный класс, который вычисляет разницу между двумя списками и выдаёт набор операций обновления. Он необходим для эффективных обновлений RecyclerView без полного обновления набора данных.

### Зачем нужен DiffUtil?

**Без DiffUtil:**
```kotlin
//  ПЛОХО — неэффективно
fun updateData(newList: List<Item>) {
    items = newList
    notifyDataSetChanged() // Обновляет всё, теряет анимации, возможны визуальные скачки
}
```

**С DiffUtil:**
```kotlin
//  ХОРОШО — эффективно, с анимированными обновлениями
fun updateData(newList: List<Item>) {
    val diffResult = DiffUtil.calculateDiff(ItemDiffCallback(items, newList))
    items = newList
    diffResult.dispatchUpdatesTo(this) // Обновляет только изменённые элементы
}
```

**Преимущества:**
- Обновляются только изменённые элементы
- Плавные анимации
- Сохраняется идентичность и состояние элементов, когда это возможно
- Лучшая воспринимаемая производительность

---

### Как работает DiffUtil (алгоритм Myers)

DiffUtil основан на **алгоритме Myers diff**, который ищет (почти) минимальный набор операций вставки/удаления для преобразования одной последовательности в другую. В Android он дополнен оптимизациями и поддержкой перемещений и частичных изменений.

Идея:
1. Строится поиск по диагоналям графа редактирования ("змейкам") совпадающих элементов.
2. Находится кратчайший путь редактирования (минимум вставок/удалений).
3. На основе пути формируются операции: вставка, удаление, перемещение, изменение.

Замечания по сложности:
- Пусть `N` — размер старого списка, `M` — нового, `D` — минимальное число правок.
- Классический Myers имеет сложность `O((N + M) * D)` по времени и `O(N + M)` по памяти.
- Реализация DiffUtil оптимизирована и обычно близка к линейной при небольшом количестве изменений, но для очень больших списков и больших отличий может быть дорогой.

**Пример (упрощённый):**

```
Старый список: [A, B, C, D]
Новый список: [A, C, D, E]

Операции:
1. Оставить A (позиция 0)
2. Удалить B (позиция 1)
3. Оставить C (позиция 2 → 1)
4. Оставить D (позиция 3 → 2)
5. Вставить E (позиция 3)

Результат: удалён только B, вставлен E, C и D переиспользуются.
```

---

### Базовая реализация DiffUtil

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

    override fun getOldListSize(): Int = oldList.size
    override fun getNewListSize(): Int = newList.size

    // Одна и та же сущность? (например, одинаковый стабильный ID)
    override fun areItemsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        return oldList[oldItemPosition].id == newList[newItemPosition].id
    }

    // Одинаковое визуальное/контентное состояние?
    override fun areContentsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        val oldItem = oldList[oldItemPosition]
        val newItem = newList[newItemPosition]
        return oldItem == newItem
    }

    // Опционально: что именно изменилось (для частичных обновлений)
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
            // Полная привязка
            onBindViewHolder(holder, position)
        } else {
            // Частичная привязка (только изменённые свойства)
            val item = items[position]

            payloads.forEach { payload ->
                @Suppress("UNCHECKED_CAST")
                val changes = payload as? Map<String, Any> ?: return@forEach

                changes["name"]?.let { holder.nameView.text = it as String }
                changes["description"]?.let { holder.descView.text = it as String }
            }
        }
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]
        // Полная привязка
    }

    // ... остальные методы и ViewHolder
}
```

---

### ListAdapter — упрощённый DiffUtil

**ListAdapter** оборачивает `AsyncListDiffer` и `DiffUtil.ItemCallback`, выполняя вычисление diff не в главном потоке и автоматически вызывая обновления адаптера.

```kotlin
class ItemAdapter : ListAdapter<Item, ItemAdapter.ViewHolder>(ItemDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = getItem(position)
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

    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean =
            oldItem == newItem
    }
}

val adapter = ItemAdapter()
recyclerView.adapter = adapter

// Обновление данных
adapter.submitList(newItems) // Diff вычисляется асинхронно, не блокируя главный поток.
```

**Преимущества ListAdapter:**
- Асинхронное вычисление diff через `AsyncListDiffer`
- Более чистый API
- Меньше шаблонного кода
- Корректная работа с обновлениями RecyclerView

---

### Async DiffUtil (большие наборы данных)

Для больших списков или дорогих сравнений переносите вычисление diff с главного потока.

```kotlin
class ItemAdapter : RecyclerView.Adapter<ItemAdapter.ViewHolder>() {

    private var items = emptyList<Item>()
    private val handler = Handler(Looper.getMainLooper())

    fun updateDataAsync(newItems: List<Item>) {
        val oldList = items

        Thread {
            val diffCallback = ItemDiffCallback(oldList, newItems)
            val diffResult = DiffUtil.calculateDiff(diffCallback)

            handler.post {
                items = newItems
                diffResult.dispatchUpdatesTo(this)
            }
        }.start()
    }

    // ... остальная часть адаптера
}
```

**Или используйте AsyncListDiffer:**

```kotlin
class ItemAdapter : RecyclerView.Adapter<ItemAdapter.ViewHolder>() {

    private val differ = AsyncListDiffer(this, ItemDiffCallback())

    private val items: List<Item>
        get() = differ.currentList

    fun updateData(newItems: List<Item>) {
        differ.submitList(newItems) // Вычисляется асинхронно.
    }

    override fun getItemCount(): Int = items.size

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]
        holder.bind(item)
    }

    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean =
            oldItem == newItem
    }
}
```

---

### Оптимизация производительности DiffUtil

**1. Эффективное сравнение содержимого**

Вместо потенциально некорректного переопределения `equals`/`hashCode` у сущностей, реализуйте оптимизации прямо в `areContentsTheSame`:

```kotlin
override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
    // Сначала дешёвые поля
    if (oldItem.name != newItem.name) return false
    if (oldItem.description != newItem.description) return false

    // Тяжёлые поля сравнивайте только при необходимости
    return true
}
```

Если нужны специальные хэши/метаданные для сравнения, моделируйте их явно.

**2. Стабильные ID при необходимости**

```kotlin
class StableIdAdapter : ListAdapter<Item, ViewHolder>(DiffCallback()) {

    init {
        setHasStableIds(true)
    }

    override fun getItemId(position: Int): Long = getItem(position).id
}
```

Стабильные ID помогают RecyclerView лучше переиспользовать ViewHolder'ы. Логику DiffUtil по-прежнему определяют `areItemsTheSame` и `areContentsTheSame`.

**3. Пагинация и частичная загрузка для очень больших списков**

Для очень больших или бесконечных списков (лента, чат) используйте Paging 3 и подгружайте данные частями, вместо одной огромной коллекции. Жёсткого порога по количеству элементов нет — всё зависит от устройства и сложности сравнения.

**4. Debounce быстрых обновлений**

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

### Частичные обновления с payload

Используйте payload, чтобы не выполнять полную привязку, если изменились только отдельные поля.

```kotlin
class ItemAdapter : RecyclerView.Adapter<ItemAdapter.ViewHolder>() {

    private val items = mutableListOf<Item>()

    override fun onBindViewHolder(
        holder: ViewHolder,
        position: Int,
        payloads: List<Any>
    ) {
        if (payloads.isEmpty()) {
            onBindViewHolder(holder, position)
        } else {
            val item = items[position]

            payloads.forEach { payload ->
                if (payload is Bundle) {
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

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]
        // Полная привязка
    }

    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean =
            oldItem == newItem

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

### Боевое применение: лента новостей

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
        override fun areItemsTheSame(oldItem: Post, newItem: Post): Boolean =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: Post, newItem: Post): Boolean =
            oldItem == newItem

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

### Бенчмарки (иллюстративно)

Пример для ~1 000 элементов и ~10 изменений (точные значения зависят от устройства и данных):

| Метод                    | Время (пример) | Анимации | Позиция прокрутки |
|--------------------------|----------------|----------|-------------------|
| `notifyDataSetChanged()` | выше            | нет      | может прыгать     |
| `DiffUtil` (sync)        | ниже           | да       | сохраняется       |
| `ListAdapter` (async)    | минимум в UI   | да       | сохраняется       |

Подходы на основе DiffUtil уменьшают работу в главном потоке и дают лучший UX по сравнению с полным обновлением.

---

### Лучшие практики

- Предпочитайте `ListAdapter` / `AsyncListDiffer` для большинства списков.
- Точно реализуйте `areItemsTheSame` (идентичность) и `areContentsTheSame` (визуальное равенство).
- Используйте payload для частичных обновлений.
- Выносите вычисление diff с главного потока для больших списков.
- Используйте пагинацию / частичную загрузку для очень больших или бесконечных списков.
- Применяйте стабильные ID для улучшения переиспользования ViewHolder, но не вместо корректных колбэков DiffUtil.
- Для очень простых или редко обновляемых списков допустимо использовать `notifyDataSetChanged()`.

---

## Answer (EN)

**DiffUtil** is a utility class that calculates the difference between two lists and outputs a list of update operations. It's essential for efficient RecyclerView updates without full dataset refreshes.

### Why DiffUtil?

**Without DiffUtil:**
```kotlin
//  BAD - Inefficient
fun updateData(newList: List<Item>) {
    items = newList
    notifyDataSetChanged() // Refreshes EVERYTHING, loses animations, may visually jump
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
- Keeps item identity and layout state when possible
- Better perceived performance

---

### How DiffUtil Works (Myers Algorithm)

DiffUtil is based on the **Myers diff algorithm**, which finds a (near) minimum edit script (insert/delete) to transform one sequence into another. Android's implementation includes optimizations and support for moves and content changes.

Conceptually:
1. It builds a search over edit graph diagonals ("snakes") of matching elements.
2. It finds a shortest edit path (minimal inserts/deletes) between old and new lists.
3. From this path it derives operations: insert, remove, move, change.

Important notes:
- Let `N` be old size, `M` be new size, `D` be minimal edit distance.
- Classic Myers runs in `O((N + M) * D)` time and `O(N + M)` space; practical performance is usually close to linear when `D` is small relative to list size.
- DiffUtil's implementation is optimized for typical UI lists but still can be expensive for very large lists or huge diffs.

**Example (simplified):**

```
Old list: [A, B, C, D]
New list: [A, C, D, E]

Operations:
1. Keep A (position 0)
2. Delete B (position 1)
3. Keep C (position 2 → 1)
4. Keep D (position 3 → 2)
5. Insert E (position 3)

Result: Only B is removed, E is inserted, C and D are reused.
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

    override fun getOldListSize(): Int = oldList.size
    override fun getNewListSize(): Int = newList.size

    // Are items the same logical entity? (e.g., same stable ID)
    override fun areItemsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        return oldList[oldItemPosition].id == newList[newItemPosition].id
    }

    // Do items have the same visual/content state?
    override fun areContentsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        val oldItem = oldList[oldItemPosition]
        val newItem = newList[newItemPosition]
        return oldItem == newItem
    }

    // Optional: provide fine-grained changes for partial bind
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
            onBindViewHolder(holder, position)
        } else {
            // Partial bind (only changed properties)
            val item = items[position]

            payloads.forEach { payload ->
                @Suppress("UNCHECKED_CAST")
                val changes = payload as? Map<String, Any> ?: return@forEach

                changes["name"]?.let { holder.nameView.text = it as String }
                changes["description"]?.let { holder.descView.text = it as String }
            }
        }
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]
        // full bind implementation here
    }

    // ... other adapter methods and ViewHolder
}
```

---

### ListAdapter - Simplified DiffUtil

**ListAdapter** wraps `AsyncListDiffer` and `DiffUtil.ItemCallback` to perform diffs off the main thread and dispatch updates to the adapter.

```kotlin
class ItemAdapter : ListAdapter<Item, ItemAdapter.ViewHolder>(ItemDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = getItem(position)
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

    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean =
            oldItem == newItem
    }
}

val adapter = ItemAdapter()
recyclerView.adapter = adapter

// Update data
adapter.submitList(newItems) // Diff is computed asynchronously (off the main thread).
```

**Benefits of ListAdapter:**
- Asynchronous diff calculation via `AsyncListDiffer`
- Cleaner API
- Less boilerplate
- Correct interaction with RecyclerView update APIs

---

### Async DiffUtil (Large Datasets)

For larger lists or expensive comparisons, move diff calculation off the main thread.

```kotlin
class ItemAdapter : RecyclerView.Adapter<ItemAdapter.ViewHolder>() {

    private var items = emptyList<Item>()
    private val handler = Handler(Looper.getMainLooper())

    fun updateDataAsync(newItems: List<Item>) {
        val oldList = items

        Thread {
            val diffCallback = ItemDiffCallback(oldList, newItems)
            val diffResult = DiffUtil.calculateDiff(diffCallback)

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

    private val items: List<Item>
        get() = differ.currentList

    fun updateData(newItems: List<Item>) {
        differ.submitList(newItems) // Computed asynchronously.
    }

    override fun getItemCount(): Int = items.size

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]
        holder.bind(item)
    }

    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean =
            oldItem == newItem
    }
}
```

---

### Optimizing DiffUtil Performance

**1. Efficient content comparison**

Rather than overriding `equals`/`hashCode` in a way that breaks their contract, keep them consistent and implement efficient checks directly in `areContentsTheSame`:

```kotlin
override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
    // Cheap fields first
    if (oldItem.name != newItem.name) return false
    if (oldItem.description != newItem.description) return false

    // If you have very heavy fields, compare them only if needed
    // e.g., if (oldItem.metadataHash != newItem.metadataHash) return false

    return true
}
```

If you need custom heavy logic, model it explicitly instead of misaligning `equals` and `hashCode`.

**2. Use stable IDs where appropriate**

```kotlin
class StableIdAdapter : ListAdapter<Item, ViewHolder>(DiffCallback()) {

    init {
        setHasStableIds(true)
    }

    override fun getItemId(position: Int): Long = getItem(position).id
}
```

Stable IDs help RecyclerView reuse ViewHolders more effectively. DiffUtil still relies primarily on `areItemsTheSame` / `areContentsTheSame`.

**3. Prefer paging / incremental loading for very large lists**

For very large or unbounded lists (e.g., feeds with tens of thousands of items), use libraries like Paging 3 with DiffUtil instead of loading gigantic lists at once. There is no strict item-count limit; it's about keeping computation and memory reasonable.

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

Use payloads to avoid rebinding the whole item when only a few fields changed.

```kotlin
class ItemAdapter : RecyclerView.Adapter<ItemAdapter.ViewHolder>() {

    private val items = mutableListOf<Item>()

    override fun onBindViewHolder(
        holder: ViewHolder,
        position: Int,
        payloads: List<Any>
    ) {
        if (payloads.isEmpty()) {
            onBindViewHolder(holder, position)
        } else {
            val item = items[position]

            payloads.forEach { payload ->
                if (payload is Bundle) {
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

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]
        // full bind
    }

    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean =
            oldItem == newItem

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
        override fun areItemsTheSame(oldItem: Post, newItem: Post): Boolean =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: Post, newItem: Post): Boolean =
            oldItem == newItem

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

### Performance Benchmarks (Illustrative)

Example scenario: updating ~1,000 items where ~10 items changed. Actual numbers depend on device and data.

| Method                   | Time (example) | Animations | Scroll Position |
|--------------------------|----------------|------------|-----------------|
| `notifyDataSetChanged()` | higher         | No         | May jump        |
| `DiffUtil` (sync)        | lower          | Yes        | Kept            |
| `ListAdapter` (async)    | minimal on UI  | Yes        | Kept            |

DiffUtil-based approaches reduce main-thread work and provide better UX compared to blind full refreshes.

---

### Best Practices

- Prefer `ListAdapter` / `AsyncListDiffer` for most RecyclerView lists.
- Implement precise `areItemsTheSame` (stable identity) and `areContentsTheSame` (visual equality).
- Use payloads for partial updates to avoid rebinding whole items.
- Offload diffing from the main thread for larger lists.
- Use paging/incremental loading for very large or infinite lists.
- Use stable IDs when it helps RecyclerView reuse ViewHolders; don't rely on them to replace proper DiffUtil callbacks.
- For very simple or rarely updated lists, `notifyDataSetChanged()` can be acceptable.

---

## Follow-ups

- [[q-android-project-parts--android--easy]]

## References

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)

## Related Questions

### Prerequisites / Concepts

- [[c-recyclerview]]

### Prerequisites (Easier)

- [[q-recyclerview-sethasfixedsize--android--easy]] - `View`, Ui
- [[q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy]] - `View`, Ui

### Related (Medium)

- q-rxjava-pagination-recyclerview--android--medium - `View`, Ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - `View`, Ui
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - `View`, Ui
- [[q-how-animations-work-in-recyclerview--android--medium]] - `View`, Ui
- [[q-recyclerview-async-list-differ--android--medium]] - `View`, Ui
