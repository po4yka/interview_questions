---\
id: android-091
title: List Optimization / Оптимизация больших списков
aliases: [List Optimization, Оптимизация списков]
topic: android
subtopics: [performance-memory, performance-rendering, ui-views]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-performance, c-recyclerview, q-canvas-drawing-optimization--android--hard, q-dagger-build-time-optimization--android--medium, q-parsing-optimization-android--android--medium, q-what-is-diffutil-for--android--medium, q-what-is-known-about-recyclerview--android--easy]
created: 2025-10-13
updated: 2025-10-31
tags: [android/performance-memory, android/performance-rendering, android/ui-views, difficulty/hard, optimization, performance, recyclerview]

---\
# Вопрос (RU)
> Оптимизация больших списков

# Question (EN)
> `List` Optimization

---

## Ответ (RU)

Оптимизация больших списков в Android-приложениях критична для плавной прокрутки и хорошего пользовательского опыта. Ниже ключевые аспекты (`RecyclerView` / Views; не Compose):

### 1. Правильное Использование ViewHolder В RecyclerView

Паттерн `ViewHolder` важен для переиспользования view и производительности.

```kotlin
class OptimizedAdapter : RecyclerView.Adapter<OptimizedAdapter.ViewHolder>() {

    private val items = mutableListOf<Item>()

    // ViewHolder кэширует ссылки на view
    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        // Кэшируем ссылки, чтобы не вызывать findViewById в onBindViewHolder
        private val titleText: TextView = itemView.findViewById(R.id.title)
        private val descText: TextView = itemView.findViewById(R.id.description)
        private val imageView: ImageView = itemView.findViewById(R.id.image)
        private val statusBadge: View = itemView.findViewById(R.id.statusBadge)

        fun bind(item: Item) {
            titleText.text = item.title
            descText.text = item.description
            statusBadge.visibility = if (item.isActive) View.VISIBLE else View.GONE

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

### 2. Использование DiffUtil Для Эффективных Обновлений

`DiffUtil` вычисляет минимальный набор изменений при обновлении данных и позволяет избежать `notifyDataSetChanged()`. Сам `DiffUtil.calculateDiff` — синхронный; для больших списков использовать `ListAdapter` / `AsyncListDiffer`, которые запускают diff в фоне.

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

    // Необязательно: payload для частичных обновлений. Требует onBindViewHolder с payloads.
    override fun getChangePayload(oldItemPosition: Int, newItemPosition: Int): Any? {
        val oldItem = oldList[oldItemPosition]
        val newItem = newList[newItemPosition]

        return when {
            oldItem.title != newItem.title -> "title_changed"
            oldItem.isActive != newItem.isActive -> "status_changed"
            else -> null
        }
    }
}

// Обновление списка (упрощенный пример; выполняется синхронно)
fun RecyclerView.Adapter<*>.updateItemsWithDiff(
    current: MutableList<Item>,
    newItems: List<Item>
) {
    val diffResult = DiffUtil.calculateDiff(ItemDiffCallback(current, newItems))
    current.clear()
    current.addAll(newItems)
    diffResult.dispatchUpdatesTo(this)
}
```

Лучше использовать `ListAdapter`, который встроенно использует `DiffUtil` (через `AsyncListDiffer`) и выполняет вычисления не на главном потоке.

```kotlin
class ModernAdapter : ListAdapter<Item, ModernAdapter.ViewHolder>(ItemDiffCallback()) {

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(item: Item) {
            // Привязка полей item к view
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

    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean = oldItem.id == newItem.id
        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean = oldItem == newItem
    }
}

// Использование - submitList запускает diff в фоновом потоке
adapter.submitList(newItems)
```

### 3. Оптимизация Загрузки Изображений

Использовать библиотеки (Glide, Coil, Picasso) с правильной конфигурацией: кэширование, downsampling, отмена запросов при рециклинге.

```kotlin
class ImageOptimizedViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
    private val imageView: ImageView = itemView.findViewById(R.id.image)

    fun bind(item: Item) {
        Glide.with(itemView.context)
            .load(item.imageUrl)
            .diskCacheStrategy(DiskCacheStrategy.AUTOMATIC)
            .override(300, 300)
            .placeholder(R.drawable.placeholder)
            .error(R.drawable.error)
            .thumbnail(0.1f)
            .into(imageView)
    }

    fun unbind() {
        // Отменить запрос и очистить ImageView при переработке
        Glide.with(itemView.context).clear(imageView)
    }
}
```

Coil (пример):

```kotlin
// build.gradle
dependencies {
    implementation("io.coil-kt:coil:2.4.0")
}

// Использование
imageView.load(item.imageUrl) {
    crossfade(true)
    placeholder(R.drawable.placeholder)
    error(R.drawable.error)
    size(300, 300)
    memoryCachePolicy(CachePolicy.ENABLED)
    diskCachePolicy(CachePolicy.ENABLED)
}
```

### 4. Реализация Пагинации

Загружайте данные порциями, а не весь список сразу.

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

        // Триггер загрузки при приближении к концу
        if (position >= items.size - 5 && !isLoading) {
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

Лучше использовать библиотеку Paging 3.

```kotlin
// build.gradle
dependencies {
    implementation("androidx.paging:paging-runtime:3.2.0")
}

class ItemPagingSource(
    private val repository: ItemRepository
) : PagingSource<Int, Item>() {

    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, Item> = try {
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

    override fun getRefreshKey(state: PagingState<Int, Item>): Int? {
        return state.anchorPosition?.let { pos ->
            state.closestPageToPosition(pos)?.prevKey?.plus(1)
                ?: state.closestPageToPosition(pos)?.nextKey?.minus(1)
        }
    }
}

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

class ItemPagingAdapter : PagingDataAdapter<Item, ItemPagingAdapter.ViewHolder>(ItemDiffCallback()) {

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(item: Item) {
            // Привязка полей item к view
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        getItem(position)?.let { holder.bind(it) }
    }
}
```

### 5. Избегать Тяжелых Операций В onBindViewHolder

`onBindViewHolder()` должен быть максимально легким.

```kotlin
// ПЛОХО - тяжелые операции в onBindViewHolder
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val item = items[position]

    val processedData = complexCalculation(item.data)        // Плохо
    val formattedDate = SimpleDateFormat("yyyy-MM-dd").format(item.timestamp) // Плохо
    val drawable = ContextCompat.getDrawable(context, getDrawableId(item.type)) // Плохо

    holder.bind(processedData, formattedDate, drawable)
}

// ХОРОШО - предварительная обработка во view-model / бэкграунде / модели
data class Item(
    val id: String,
    val rawData: String,
    val timestamp: Long,
    val type: Int,
    val processedData: String,
    val formattedDate: String,
    val drawableResId: Int
)

override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val item = items[position]
    holder.bind(item)
}
```

### 6. Оптимизация Конфигурации RecyclerView

```kotlin
recyclerView.apply {
    // Использовать, если изменения содержимого не влияют на размер макета
    setHasFixedSize(true)

    // Аккуратно настраивать размер кэша; слишком большой = лишняя память
    setItemViewCacheSize(20)

    // Настройка пула переработанных view (один тип viewType = 0)
    recycledViewPool.setMaxRecycledViews(0, 20)

    // Для вложенных RecyclerView стоит шарить общий RecycledViewPool между ними
    // val sharedPool = RecyclerView.RecycledViewPool()
    // recyclerViewA.setRecycledViewPool(sharedPool)
    // recyclerViewB.setRecycledViewPool(sharedPool)

    (layoutManager as? LinearLayoutManager)?.apply {
        isItemPrefetchEnabled = true
        initialPrefetchItemCount = 4
    }
}
```

### 7. Оптимизация Сложности Layout

```xml
<!-- ПЛОХО - глубокая иерархия view -->
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

<!-- ХОРОШО - более плоская иерархия с ConstraintLayout -->
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

### 8. Использование `View` Binding (типобезопасность)

`View` Binding дает типобезопасный доступ к view и уменьшает количество ошибок; выигрыш по производительности вторичен (по сравнению с ручным `findViewById` при каждом биндинге).

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

### 9. Реализация Предварительной Загрузки Элементов

```kotlin
class PrefetchingLayoutManager(context: Context) : LinearLayoutManager(context) {
    init {
        isItemPrefetchEnabled = true
        initialPrefetchItemCount = 4
    }
}

// Использование
recyclerView.layoutManager = PrefetchingLayoutManager(context)
```

### 10. Мониторинг Производительности

```kotlin
// Включить StrictMode в debug-сборках для отслеживания обращения к диску/сети на главном потоке
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

// Использовать профилировщики Android Studio:
// - CPU Profiler: поиск медленных участков
// - Memory Profiler: утечки и лишние аллокации
// - Network Profiler: загрузка изображений и запросы
// - Инструменты для анализа рендера кадров (Profiler, Perfetto)
```

### Резюме (RU)

Для оптимизации больших списков:

1. Правильно использовать `ViewHolder` и держать биндинг легким.
2. Использовать `DiffUtil` / ListAdapter для эффективных обновлений (с учетом того, где выполняется diff).
3. Оптимизировать загрузку изображений (кэш, уменьшение размера, отмена при рециклинге).
4. Реализовать пагинацию; для сложных случаев использовать Paging 3.
5. Избегать тяжелых операций в `onBindViewHolder()`, выносить их с главного потока.
6. Тонко настраивать `RecyclerView` (fixed size, кэш, пул, prefetch).
7. Упрощать разметку, избегать глубокой иерархии.
8. Использовать `View` Binding для типобезопасности и меньшего boilerplate.
9. Включать предварительную загрузку элементов, когда это уместно.
10. Регулярно профилировать и измерять.

---

## Answer (EN)
Optimizing large lists in Android applications is critical for smooth scrolling and a good user experience. Focus on the following areas (`RecyclerView` / Views; not Compose):

### 1. Proper Use of ViewHolder in RecyclerView

The `ViewHolder` pattern is essential for view reuse and performance.

```kotlin
class OptimizedAdapter : RecyclerView.Adapter<OptimizedAdapter.ViewHolder>() {

    private val items = mutableListOf<Item>()

    // ViewHolder caches view references
    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        // Cache view references to avoid repeated findViewById calls
        private val titleText: TextView = itemView.findViewById(R.id.title)
        private val descText: TextView = itemView.findViewById(R.id.description)
        private val imageView: ImageView = itemView.findViewById(R.id.image)
        private val statusBadge: View = itemView.findViewById(R.id.statusBadge)

        fun bind(item: Item) {
            // Lightweight binding operations only
            titleText.text = item.title
            descText.text = item.description
            statusBadge.visibility = if (item.isActive) View.VISIBLE else View.GONE

            // Use an image loading library with caching
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

`DiffUtil` calculates a minimal set of updates when data changes and helps avoid `notifyDataSetChanged()`. `DiffUtil.calculateDiff` itself is synchronous; for large lists prefer `ListAdapter` / `AsyncListDiffer`, which perform diffing on a background thread.

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

    // Optional: change payload for partial binds. Requires onBindViewHolder with payloads.
    override fun getChangePayload(oldItemPosition: Int, newItemPosition: Int): Any? {
        val oldItem = oldList[oldItemPosition]
        val newItem = newList[newItemPosition]

        return when {
            oldItem.title != newItem.title -> "title_changed"
            oldItem.isActive != newItem.isActive -> "status_changed"
            else -> null
        }
    }
}

// Adapter method to apply diff (synchronously in this example)
fun RecyclerView.Adapter<*>.updateItemsWithDiff(
    current: MutableList<Item>,
    newItems: List<Item>
) {
    val diffResult = DiffUtil.calculateDiff(ItemDiffCallback(current, newItems))
    current.clear()
    current.addAll(newItems)
    diffResult.dispatchUpdatesTo(this)
}
```

Better: use `ListAdapter`, which integrates `DiffUtil` (via `AsyncListDiffer`) and runs diffing off the main thread.

```kotlin
class ModernAdapter : ListAdapter<Item, ModernAdapter.ViewHolder>(ItemDiffCallback()) {

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(item: Item) {
            // Bind item fields to views
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

    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean = oldItem.id == newItem.id
        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean = oldItem == newItem
    }
}

// Usage - automatic diff calculation on a worker thread
adapter.submitList(newItems)
```

### 3. Image Loading Optimization

Use mature libraries (Glide, Coil, Picasso) configured for your use case: caching, downsampling, and cancelling requests on recycle.

```kotlin
class ImageOptimizedViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
    private val imageView: ImageView = itemView.findViewById(R.id.image)

    fun bind(item: Item) {
        Glide.with(itemView.context)
            .load(item.imageUrl)
            .diskCacheStrategy(DiskCacheStrategy.AUTOMATIC)
            .override(300, 300) // avoid loading unnecessarily large bitmaps
            .placeholder(R.drawable.placeholder)
            .error(R.drawable.error)
            .thumbnail(0.1f)
            .into(imageView)
    }

    fun unbind() {
        // Cancel any in-flight requests when view is recycled
        Glide.with(itemView.context).clear(imageView)
    }
}
```

Coil example (Kotlin-first):

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

Load data in chunks instead of all at once.

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
        if (position >= items.size - 5 && !isLoading) {
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

Better: use Paging 3.

```kotlin
// build.gradle
dependencies {
    implementation("androidx.paging:paging-runtime:3.2.0")
}

class ItemPagingSource(
    private val repository: ItemRepository
) : PagingSource<Int, Item>() {

    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, Item> = try {
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

    override fun getRefreshKey(state: PagingState<Int, Item>): Int? {
        return state.anchorPosition?.let { pos ->
            state.closestPageToPosition(pos)?.prevKey?.plus(1)
                ?: state.closestPageToPosition(pos)?.nextKey?.minus(1)
        }
    }
}

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

class ItemPagingAdapter : PagingDataAdapter<Item, ItemPagingAdapter.ViewHolder>(ItemDiffCallback()) {

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(item: Item) {
            // Bind item fields to views
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        getItem(position)?.let { holder.bind(it) }
    }
}

class MyFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()
    private val adapter = ItemPagingAdapter()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        recyclerView.adapter = adapter

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.items.collectLatest { pagingData ->
                adapter.submitData(pagingData)
            }
        }
    }
}
```

### 5. Avoid Heavy Operations in onBindViewHolder

Keep `onBindViewHolder()` lightweight; it is called frequently during scrolling.

```kotlin
// BAD - heavy operations in onBindViewHolder
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val item = items[position]

    val processedData = complexCalculation(item.data)        // Bad
    val formattedDate = SimpleDateFormat("yyyy-MM-dd").format(item.timestamp) // Bad
    val drawable = ContextCompat.getDrawable(context, getDrawableId(item.type)) // Bad

    holder.bind(processedData, formattedDate, drawable)
}

// GOOD - pre-process in background / model
data class Item(
    val id: String,
    val rawData: String,
    val timestamp: Long,
    val type: Int,
    val processedData: String,
    val formattedDate: String,
    val drawableResId: Int
)

override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val item = items[position]
    holder.bind(item)
}
```

### 6. RecyclerView Configuration Optimizations

```kotlin
recyclerView.apply {
    // Use if changes in content do not affect layout size
    setHasFixedSize(true)

    // Adjust cache size carefully; too large wastes memory
    setItemViewCacheSize(20)

    // RecycledViewPool tuning for viewType = 0
    recycledViewPool.setMaxRecycledViews(0, 20)

    // For nested RecyclerViews, share a pool instance between them
    // val sharedPool = RecyclerView.RecycledViewPool()
    // recyclerViewA.setRecycledViewPool(sharedPool)
    // recyclerViewB.setRecycledViewPool(sharedPool)

    (layoutManager as? LinearLayoutManager)?.apply {
        isItemPrefetchEnabled = true
        initialPrefetchItemCount = 4
    }
}
```

### 7. Optimize Layout Complexity

```xml
<!-- BAD - deep view hierarchy -->
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

<!-- GOOD - flatter hierarchy with ConstraintLayout -->
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

### 8. Use `View` Binding (Type Safety / Fewer findViewById)

`View` Binding mainly improves type safety and reduces boilerplate; performance benefits versus repeated `findViewById` are secondary but positive.

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
        isItemPrefetchEnabled = true
        initialPrefetchItemCount = 4
    }
}

// Usage
recyclerView.layoutManager = PrefetchingLayoutManager(context)
```

### 10. Monitor Performance

```kotlin
// Enable StrictMode in debug builds to catch disk/network operations on the main thread
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

// Use Android Studio Profilers:
// - CPU Profiler: find slow methods
// - Memory Profiler: detect leaks / excessive allocations
// - Network Profiler: monitor image loading
// - Frame rendering tools (Profiler, Perfetto) for jank analysis.
```

### Summary (EN)

To optimize large lists:

1. Use `ViewHolder` correctly and keep bindings lightweight.
2. Use `DiffUtil` / ListAdapter for efficient item updates (being explicit about where diffing runs).
3. Optimize image loading (caching, downsampling, cancel on recycle).
4. Implement pagination; prefer Paging 3 for complex / large data.
5. Avoid heavy work in `onBindViewHolder()`; precompute off the main thread.
6. Tune `RecyclerView` (fixed size when valid, cache, recycled pool, prefetch).
7. Simplify item layouts; avoid deep hierarchies.
8. Use `View` Binding for type safety and fewer errors.
9. Enable item prefetching where appropriate.
10. Continuously profile and measure.

---

## Follow-ups

- [[c-performance]]
- [[c-recyclerview]]
- [[q-what-is-diffutil-for--android--medium]]

## References

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)

## Related Questions

### Computer Science Fundamentals
- [[q-list-vs-sequence--kotlin--medium]] - Data Structures

### Kotlin Language Features
- [[q-kotlin-collections--kotlin--medium]] - Data Structures
- [[q-list-vs-sequence--kotlin--medium]] - Data Structures

### Related Algorithms
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Data Structures
- [[q-advanced-graph-algorithms--algorithms--hard]] - Data Structures
- [[q-binary-search-trees-bst--algorithms--hard]] - Data Structures
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Data Structures
