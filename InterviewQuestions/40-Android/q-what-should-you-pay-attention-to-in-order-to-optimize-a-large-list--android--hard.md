---
id: "20251015082237504"
title: "What Should You Pay Attention To In Order To Optimize A Large List / На что обратить внимание для оптимизации большого списка"
topic: android
difficulty: hard
status: draft
created: 2025-10-13
tags: [android/recyclerview, android/views, recyclerview, ui, viewholder, views, difficulty/hard]
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-android
related_questions: []
---
# На что следует обращать внимание, чтобы оптимизировать большой список?

**English**: What should you pay attention to in order to optimize a large list?

## Answer (EN)
Optimizing large lists in Android applications is critical for smooth scrolling and good user experience. Here are the key areas to focus on:

### 1. Proper Use of ViewHolder in RecyclerView

**ViewHolder pattern** is essential for view reuse and performance.

```kotlin
class OptimizedAdapter : RecyclerView.Adapter<OptimizedAdapter.ViewHolder>() {

    private val items = mutableListOf<Item>()

    // ViewHolder caches view references
    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        // Cache all view references to avoid findViewById calls
        private val titleText: TextView = itemView.findViewById(R.id.title)
        private val descText: TextView = itemView.findViewById(R.id.description)
        private val imageView: ImageView = itemView.findViewById(R.id.image)
        private val statusBadge: View = itemView.findViewById(R.id.statusBadge)

        fun bind(item: Item) {
            // Lightweight binding operations only
            titleText.text = item.title
            descText.text = item.description
            statusBadge.visibility = if (item.isActive) View.VISIBLE else View.GONE

            // Use image loading library with caching
            Glide.with(itemView.context)
                .load(item.imageUrl)
                .into(imageView)
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position])
    }

    override fun getItemCount() = items.size
}
```

### 2. Use DiffUtil for Efficient Updates

**DiffUtil** calculates the minimal number of updates needed when data changes.

```kotlin
class ItemDiffCallback(
    private val oldList: List<Item>,
    private val newList: List<Item>
) : DiffUtil.Callback() {

    override fun getOldListSize() = oldList.size

    override fun getNewListSize() = newList.size

    override fun areItemsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        return oldList[oldItemPosition].id == newList[newItemPosition].id
    }

    override fun areContentsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        return oldList[oldItemPosition] == newList[newItemPosition]
    }

    override fun getChangePayload(oldItemPosition: Int, newItemPosition: Int): Any? {
        val oldItem = oldList[oldItemPosition]
        val newItem = newList[newItemPosition]

        // Return specific changes to enable partial binding
        return when {
            oldItem.title != newItem.title -> "title_changed"
            oldItem.isActive != newItem.isActive -> "status_changed"
            else -> null
        }
    }
}

// Update adapter data efficiently
fun updateItems(newItems: List<Item>) {
    val diffCallback = ItemDiffCallback(items, newItems)
    val diffResult = DiffUtil.calculateDiff(diffCallback)

    items.clear()
    items.addAll(newItems)
    diffResult.dispatchUpdatesTo(this)
}
```

**Better: Use ListAdapter** (built-in DiffUtil support)

```kotlin
class ModernAdapter : ListAdapter<Item, ModernAdapter.ViewHolder>(ItemDiffCallback()) {

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(item: Item) {
            // Bind item
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    // DiffUtil callback
    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem == newItem
        }
    }
}

// Usage - automatic diff calculation
adapter.submitList(newItems)
```

### 3. Image Loading Optimization

**Use libraries** like Glide, Coil, or Picasso with proper configuration.

```kotlin
class ImageOptimizedViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
    private val imageView: ImageView = itemView.findViewById(R.id.image)

    fun bind(item: Item) {
        Glide.with(itemView.context)
            .load(item.imageUrl)
            // Memory cache
            .diskCacheStrategy(DiskCacheStrategy.AUTOMATIC)
            // Reduce image size
            .override(300, 300)
            // Placeholder while loading
            .placeholder(R.drawable.placeholder)
            // Error image
            .error(R.drawable.error)
            // Thumbnail for quick display
            .thumbnail(0.1f)
            // Clear previous requests
            .onlyRetrieveFromCache(false)
            .into(imageView)
    }

    fun unbind() {
        // Clear image when recycled
        Glide.with(itemView.context).clear(imageView)
    }
}
```

**Coil example** (Kotlin-first, more efficient):

```kotlin
// build.gradle
dependencies {
    implementation("io.coil-kt:coil:2.4.0")
}

// Usage
imageView.load(item.imageUrl) {
    crossfade(true)
    placeholder(R.drawable.placeholder)
    error(R.drawable.error)
    size(300, 300)
    memoryCachePolicy(CachePolicy.ENABLED)
    diskCachePolicy(CachePolicy.ENABLED)
}
```

### 4. Implement Pagination

Load data in chunks rather than all at once.

```kotlin
class PaginatedAdapter : RecyclerView.Adapter<PaginatedAdapter.ViewHolder>() {

    private val items = mutableListOf<Item>()
    private var isLoading = false
    var onLoadMore: (() -> Unit)? = null

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(item: Item) {
            // Bind item
        }
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position])

        // Trigger load more when near end
        if (position == items.size - 5 && !isLoading) {
            isLoading = true
            onLoadMore?.invoke()
        }
    }

    fun addItems(newItems: List<Item>) {
        val startPosition = items.size
        items.addAll(newItems)
        notifyItemRangeInserted(startPosition, newItems.size)
        isLoading = false
    }

    override fun getItemCount() = items.size

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }
}

// Usage with ViewModel
class MyViewModel : ViewModel() {
    private var currentPage = 0
    private val pageSize = 20

    fun loadMore() {
        viewModelScope.launch {
            val newItems = repository.getItems(currentPage, pageSize)
            currentPage++
            _items.value = _items.value + newItems
        }
    }
}
```

**Better: Use Paging 3 Library**

```kotlin
// build.gradle
dependencies {
    implementation "androidx.paging:paging-runtime:3.2.0"
}

// PagingSource
class ItemPagingSource(
    private val repository: ItemRepository
) : PagingSource<Int, Item>() {

    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, Item> {
        return try {
            val page = params.key ?: 0
            val items = repository.getItems(page, params.loadSize)

            LoadResult.Page(
                data = items,
                prevKey = if (page == 0) null else page - 1,
                nextKey = if (items.isEmpty()) null else page + 1
            )
        } catch (e: Exception) {
            LoadResult.Error(e)
        }
    }

    override fun getRefreshKey(state: PagingState<Int, Item>): Int? {
        return state.anchorPosition?.let { position ->
            state.closestPageToPosition(position)?.prevKey?.plus(1)
                ?: state.closestPageToPosition(position)?.nextKey?.minus(1)
        }
    }
}

// ViewModel
class MyViewModel(repository: ItemRepository) : ViewModel() {
    val items: Flow<PagingData<Item>> = Pager(
        config = PagingConfig(
            pageSize = 20,
            enablePlaceholders = false,
            prefetchDistance = 5
        ),
        pagingSourceFactory = { ItemPagingSource(repository) }
    ).flow.cachedIn(viewModelScope)
}

// Adapter
class ItemPagingAdapter : PagingDataAdapter<Item, ItemPagingAdapter.ViewHolder>(ItemDiffCallback()) {
    // Implementation similar to ListAdapter
}

// Fragment
class MyFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()
    private val adapter = ItemPagingAdapter()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        recyclerView.adapter = adapter

        lifecycleScope.launch {
            viewModel.items.collectLatest { pagingData ->
                adapter.submitData(pagingData)
            }
        }
    }
}
```

### 5. Avoid Heavy Operations in onBindViewHolder

Keep `onBindViewHolder()` lightweight - it's called frequently during scrolling.

```kotlin
// BAD - Heavy operations in onBindViewHolder
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val item = items[position]

    // DON'T do this - expensive operations
    val processedData = complexCalculation(item.data)  // Bad!
    val formattedDate = SimpleDateFormat("yyyy-MM-dd").format(item.timestamp)  // Bad!
    val drawable = ContextCompat.getDrawable(context, getDrawableId(item.type))  // Bad!

    holder.bind(processedData, formattedDate, drawable)
}

// GOOD - Pre-process data in data model or background thread
data class Item(
    val id: String,
    val rawData: String,
    // Pre-calculated fields
    val processedData: String = complexCalculation(rawData),
    val formattedDate: String = formatDate(timestamp),
    val drawableResId: Int = getDrawableId(type)
)

override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val item = items[position]
    // Fast binding - just set pre-calculated values
    holder.bind(item)
}
```

### 6. RecyclerView Configuration Optimizations

```kotlin
recyclerView.apply {
    // Notify adapter that item size is fixed
    setHasFixedSize(true)

    // Increase view cache size
    setItemViewCacheSize(20)

    // Increase recycled view pool size
    recycledViewPool.setMaxRecycledViews(0, 20)

    // Use custom RecycledViewPool for shared adapter types
    val sharedPool = RecyclerView.RecycledViewPool()
    setRecycledViewPool(sharedPool)

    // Optimize nested RecyclerViews
    (layoutManager as? LinearLayoutManager)?.apply {
        isItemPrefetchEnabled = true
        initialPrefetchItemCount = 4
    }
}
```

### 7. Optimize Layout Complexity

```xml
<!-- BAD - Deep view hierarchy -->
<LinearLayout>
    <RelativeLayout>
        <LinearLayout>
            <FrameLayout>
                <TextView />
                <ImageView />
            </FrameLayout>
        </LinearLayout>
    </RelativeLayout>
</LinearLayout>

<!-- GOOD - Flat hierarchy with ConstraintLayout -->
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content">

    <ImageView
        android:id="@+id/image"
        android:layout_width="48dp"
        android:layout_height="48dp"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

    <TextView
        android:id="@+id/title"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        app:layout_constraintStart_toEndOf="@id/image"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
```

### 8. Use View Binding for Type Safety

```kotlin
class ViewBindingViewHolder(
    private val binding: ItemLayoutBinding
) : RecyclerView.ViewHolder(binding.root) {

    fun bind(item: Item) {
        binding.apply {
            title.text = item.title
            description.text = item.description

            Glide.with(root.context)
                .load(item.imageUrl)
                .into(image)
        }
    }
}

override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewBindingViewHolder {
    val binding = ItemLayoutBinding.inflate(
        LayoutInflater.from(parent.context),
        parent,
        false
    )
    return ViewBindingViewHolder(binding)
}
```

### 9. Implement Item Prefetching

```kotlin
class PrefetchingLayoutManager(context: Context) : LinearLayoutManager(context) {
    init {
        // Enable prefetching
        isItemPrefetchEnabled = true
        // Number of items to prefetch
        initialPrefetchItemCount = 4
    }
}

// Usage
recyclerView.layoutManager = PrefetchingLayoutManager(context)
```

### 10. Monitor Performance

```kotlin
// Enable strict mode in debug builds
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectDiskReads()
            .detectDiskWrites()
            .detectNetwork()
            .penaltyLog()
            .build()
    )
}

// Profile with Android Profiler
// - CPU Profiler: Identify slow methods
// - Memory Profiler: Check for memory leaks
// - Network Profiler: Monitor image loading

// Use Systrace for frame rendering analysis
```

### Summary

To optimize large lists:

1. **Use ViewHolder pattern** properly - cache view references
2. **Use DiffUtil or ListAdapter** - efficient updates
3. **Optimize image loading** - use Glide/Coil with caching and sizing
4. **Implement pagination** - load data in chunks (Paging 3)
5. **Avoid heavy operations** in `onBindViewHolder()`
6. **Configure RecyclerView** - fixed size, view cache, recycled pool
7. **Optimize layouts** - flat hierarchies with ConstraintLayout
8. **Use View Binding** - type-safe and efficient
9. **Enable prefetching** - smoother scrolling
10. **Monitor performance** - use profilers and tools

## Ответ (RU)

Оптимизация больших списков в Android-приложениях критична для плавной прокрутки и хорошего пользовательского опыта. Вот ключевые области для фокуса:

### 1. Правильное использование ViewHolder в RecyclerView

**Паттерн ViewHolder** важен для повторного использования view и производительности.

```kotlin
class OptimizedAdapter : RecyclerView.Adapter<OptimizedAdapter.ViewHolder>() {

    private val items = mutableListOf<Item>()

    // ViewHolder кэширует ссылки на view
    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        // Кэшировать все ссылки на view для избежания вызовов findViewById
        private val titleText: TextView = itemView.findViewById(R.id.title)
        private val descText: TextView = itemView.findViewById(R.id.description)
        private val imageView: ImageView = itemView.findViewById(R.id.image)

        fun bind(item: Item) {
            // Только легкие операции привязки
            titleText.text = item.title
            descText.text = item.description

            // Использовать библиотеку загрузки изображений с кэшированием
            Glide.with(itemView.context)
                .load(item.imageUrl)
                .into(imageView)
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position])
    }

    override fun getItemCount() = items.size
}
```

### 2. Использование DiffUtil для эффективных обновлений

**DiffUtil** вычисляет минимальное количество обновлений при изменении данных.

```kotlin
class ItemDiffCallback(
    private val oldList: List<Item>,
    private val newList: List<Item>
) : DiffUtil.Callback() {

    override fun getOldListSize() = oldList.size
    override fun getNewListSize() = newList.size

    override fun areItemsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        return oldList[oldItemPosition].id == newList[newItemPosition].id
    }

    override fun areContentsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        return oldList[oldItemPosition] == newList[newItemPosition]
    }

    override fun getChangePayload(oldItemPosition: Int, newItemPosition: Int): Any? {
        val oldItem = oldList[oldItemPosition]
        val newItem = newList[newItemPosition]

        // Возвращать конкретные изменения для частичной привязки
        return when {
            oldItem.title != newItem.title -> "title_changed"
            oldItem.isActive != newItem.isActive -> "status_changed"
            else -> null
        }
    }
}

// Эффективное обновление данных адаптера
fun updateItems(newItems: List<Item>) {
    val diffCallback = ItemDiffCallback(items, newItems)
    val diffResult = DiffUtil.calculateDiff(diffCallback)

    items.clear()
    items.addAll(newItems)
    diffResult.dispatchUpdatesTo(this)
}
```

**Лучше: Использовать ListAdapter** (встроенная поддержка DiffUtil)

```kotlin
class ModernAdapter : ListAdapter<Item, ModernAdapter.ViewHolder>(ItemDiffCallback()) {

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(item: Item) {
            // Привязать item
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    // DiffUtil callback
    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem == newItem
        }
    }
}

// Использование - автоматический расчет diff
adapter.submitList(newItems)
```

### 3. Оптимизация загрузки изображений

**Использовать библиотеки** как Glide, Coil или Picasso с правильной конфигурацией.

```kotlin
class ImageOptimizedViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
    private val imageView: ImageView = itemView.findViewById(R.id.image)

    fun bind(item: Item) {
        Glide.with(itemView.context)
            .load(item.imageUrl)
            // Кэш в памяти
            .diskCacheStrategy(DiskCacheStrategy.AUTOMATIC)
            // Уменьшить размер изображения
            .override(300, 300)
            // Placeholder во время загрузки
            .placeholder(R.drawable.placeholder)
            // Изображение ошибки
            .error(R.drawable.error)
            // Миниатюра для быстрого отображения
            .thumbnail(0.1f)
            .into(imageView)
    }

    fun unbind() {
        // Очистить изображение при переработке
        Glide.with(itemView.context).clear(imageView)
    }
}
```

### 4. Реализация пагинации

Загружать данные порциями, а не все сразу.

```kotlin
class PaginatedAdapter : RecyclerView.Adapter<PaginatedAdapter.ViewHolder>() {

    private val items = mutableListOf<Item>()
    private var isLoading = false
    var onLoadMore: (() -> Unit)? = null

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(item: Item) {
            // Привязать item
        }
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position])

        // Запустить загрузку больше при приближении к концу
        if (position == items.size - 5 && !isLoading) {
            isLoading = true
            onLoadMore?.invoke()
        }
    }

    fun addItems(newItems: List<Item>) {
        val startPosition = items.size
        items.addAll(newItems)
        notifyItemRangeInserted(startPosition, newItems.size)
        isLoading = false
    }

    override fun getItemCount() = items.size

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }
}
```

**Лучше: Использовать библиотеку Paging 3**

```kotlin
// PagingSource
class ItemPagingSource(
    private val repository: ItemRepository
) : PagingSource<Int, Item>() {

    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, Item> {
        return try {
            val page = params.key ?: 0
            val items = repository.getItems(page, params.loadSize)

            LoadResult.Page(
                data = items,
                prevKey = if (page == 0) null else page - 1,
                nextKey = if (items.isEmpty()) null else page + 1
            )
        } catch (e: Exception) {
            LoadResult.Error(e)
        }
    }

    override fun getRefreshKey(state: PagingState<Int, Item>): Int? {
        return state.anchorPosition?.let { position ->
            state.closestPageToPosition(position)?.prevKey?.plus(1)
                ?: state.closestPageToPosition(position)?.nextKey?.minus(1)
        }
    }
}

// ViewModel
class MyViewModel(repository: ItemRepository) : ViewModel() {
    val items: Flow<PagingData<Item>> = Pager(
        config = PagingConfig(
            pageSize = 20,
            enablePlaceholders = false,
            prefetchDistance = 5
        ),
        pagingSourceFactory = { ItemPagingSource(repository) }
    ).flow.cachedIn(viewModelScope)
}
```

### 5. Избегать тяжелых операций в onBindViewHolder

Держать `onBindViewHolder()` легким - он вызывается часто во время прокрутки.

```kotlin
// ПЛОХО - Тяжелые операции в onBindViewHolder
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val item = items[position]

    // НЕ делать - дорогие операции
    val processedData = complexCalculation(item.data)  // Плохо!
    val formattedDate = SimpleDateFormat("yyyy-MM-dd").format(item.timestamp)  // Плохо!

    holder.bind(processedData, formattedDate)
}

// ХОРОШО - Предварительная обработка данных в модели данных или фоновом потоке
data class Item(
    val id: String,
    val rawData: String,
    // Предвычисленные поля
    val processedData: String = complexCalculation(rawData),
    val formattedDate: String = formatDate(timestamp)
)

override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val item = items[position]
    // Быстрая привязка - просто установить предвычисленные значения
    holder.bind(item)
}
```

### 6. Оптимизация конфигурации RecyclerView

```kotlin
recyclerView.apply {
    // Уведомить адаптер что размер элемента фиксирован
    setHasFixedSize(true)

    // Увеличить размер кэша view
    setItemViewCacheSize(20)

    // Увеличить размер пула переработанных view
    recycledViewPool.setMaxRecycledViews(0, 20)

    // Оптимизировать вложенные RecyclerViews
    (layoutManager as? LinearLayoutManager)?.apply {
        isItemPrefetchEnabled = true
        initialPrefetchItemCount = 4
    }
}
```

### 7. Оптимизация сложности Layout

```xml
<!-- ПЛОХО - Глубокая иерархия view -->
<LinearLayout>
    <RelativeLayout>
        <LinearLayout>
            <FrameLayout>
                <TextView />
                <ImageView />
            </FrameLayout>
        </LinearLayout>
    </RelativeLayout>
</LinearLayout>

<!-- ХОРОШО - Плоская иерархия с ConstraintLayout -->
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content">

    <ImageView
        android:id="@+id/image"
        android:layout_width="48dp"
        android:layout_height="48dp"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

    <TextView
        android:id="@+id/title"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        app:layout_constraintStart_toEndOf="@id/image"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
```

### 8. Использование View Binding для типобезопасности

```kotlin
class ViewBindingViewHolder(
    private val binding: ItemLayoutBinding
) : RecyclerView.ViewHolder(binding.root) {

    fun bind(item: Item) {
        binding.apply {
            title.text = item.title
            description.text = item.description

            Glide.with(root.context)
                .load(item.imageUrl)
                .into(image)
        }
    }
}

override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewBindingViewHolder {
    val binding = ItemLayoutBinding.inflate(
        LayoutInflater.from(parent.context),
        parent,
        false
    )
    return ViewBindingViewHolder(binding)
}
```

### 9. Реализация предварительной загрузки элементов

```kotlin
class PrefetchingLayoutManager(context: Context) : LinearLayoutManager(context) {
    init {
        // Включить предварительную загрузку
        isItemPrefetchEnabled = true
        // Количество элементов для предварительной загрузки
        initialPrefetchItemCount = 4
    }
}

// Использование
recyclerView.layoutManager = PrefetchingLayoutManager(context)
```

### 10. Мониторинг производительности

```kotlin
// Включить strict mode в debug сборках
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectDiskReads()
            .detectDiskWrites()
            .detectNetwork()
            .penaltyLog()
            .build()
    )
}

// Профилирование с Android Profiler
// - CPU Profiler: Идентифицировать медленные методы
// - Memory Profiler: Проверить утечки памяти
// - Network Profiler: Мониторить загрузку изображений

// Использовать Systrace для анализа рендеринга кадров
```

### Резюме

Для оптимизации больших списков:

1. **Использовать паттерн ViewHolder** правильно - кэшировать ссылки на view
2. **Использовать DiffUtil или ListAdapter** - эффективные обновления
3. **Оптимизировать загрузку изображений** - использовать Glide/Coil с кэшированием и изменением размера
4. **Реализовать пагинацию** - загружать данные порциями (Paging 3)
5. **Избегать тяжелых операций** в `onBindViewHolder()`
6. **Конфигурировать RecyclerView** - фиксированный размер, кэш view, пул переработки
7. **Оптимизировать layouts** - плоские иерархии с ConstraintLayout
8. **Использовать View Binding** - типобезопасно и эффективно
9. **Включить предварительную загрузку** - более плавная прокрутка
10. **Мониторить производительность** - использовать профилировщики и инструменты


---

## Related Questions

### Computer Science Fundamentals
- [[q-list-vs-sequence--programming-languages--medium]] - Data Structures

### Kotlin Language Features
- [[q-kotlin-collections--kotlin--medium]] - Data Structures
- [[q-list-vs-sequence--kotlin--medium]] - Data Structures

### Related Algorithms
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Data Structures
- [[q-advanced-graph-algorithms--algorithms--hard]] - Data Structures
- [[q-binary-search-trees-bst--algorithms--hard]] - Data Structures
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Data Structures
