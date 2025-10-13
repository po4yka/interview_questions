---
topic: android
tags:
  - recyclerview
  - caching
  - android
  - ui
  - performance
difficulty: medium
status: draft
---

# How to write RecyclerView so that it caches ahead?

# Вопрос (RU)

Как можно писать RecyclerView, чтобы он кэшировал наперёд

## Answer (EN)
RecyclerView provides several mechanisms for caching items ahead to improve scrolling performance and user experience. Here are the main approaches:

### 1. setItemViewCacheSize() - View Caching

The view cache stores recently scrolled-off-screen views without rebinding data.

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val recyclerView = findViewById<RecyclerView>(R.id.recyclerView)

        // Default is 2, increase for better caching
        recyclerView.setItemViewCacheSize(20)

        // Setup adapter and layout manager
        recyclerView.adapter = MyAdapter(items)
        recyclerView.layoutManager = LinearLayoutManager(this)
    }
}
```

#### Understanding View Cache Size

```kotlin
class OptimizedRecyclerViewActivity : AppCompatActivity() {

    private fun setupRecyclerView() {
        val recyclerView = findViewById<RecyclerView>(R.id.recyclerView)

        // Cache more views for smoother scrolling
        // Rule of thumb: cache 2-3 screens worth of items
        val itemsPerScreen = 10
        val screensToCache = 2
        recyclerView.setItemViewCacheSize(itemsPerScreen * screensToCache)

        // Enable nested scrolling optimization
        recyclerView.isNestedScrollingEnabled = true

        // Setup adapter
        val adapter = MyAdapter(generateItems())
        recyclerView.adapter = adapter
        recyclerView.layoutManager = LinearLayoutManager(this)
    }
}
```

### 2. Prefetching with LinearLayoutManager

RecyclerView automatically prefetches items when using LinearLayoutManager.

```kotlin
class PrefetchingActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val recyclerView = findViewById<RecyclerView>(R.id.recyclerView)
        val layoutManager = LinearLayoutManager(this)

        // Enable prefetching (enabled by default in LinearLayoutManager)
        layoutManager.isItemPrefetchEnabled = true

        // Set initial prefetch count
        layoutManager.initialPrefetchItemCount = 4

        recyclerView.layoutManager = layoutManager
        recyclerView.adapter = MyAdapter(items)
    }
}
```

#### Custom Prefetch Configuration

```kotlin
class CustomPrefetchLayoutManager(
    context: Context
) : LinearLayoutManager(context) {

    init {
        // Enable prefetching
        isItemPrefetchEnabled = true

        // Prefetch more items for nested RecyclerViews
        initialPrefetchItemCount = 6
    }

    override fun collectInitialPrefetchPositions(
        adapterItemCount: Int,
        layoutPrefetchRegistry: LayoutPrefetchRegistry
    ) {
        // Prefetch first N items when RecyclerView first appears
        val itemsToPreload = minOf(initialPrefetchItemCount, adapterItemCount)
        for (i in 0 until itemsToPreload) {
            layoutPrefetchRegistry.addPosition(i, 0)
        }
    }
}

// Usage
recyclerView.layoutManager = CustomPrefetchLayoutManager(this)
```

### 3. RecyclerView.OnScrollListener for Data Prefetching

Implement custom logic to load data ahead of time.

```kotlin
class DataPrefetchingActivity : AppCompatActivity() {

    private val items = mutableListOf<Item>()
    private lateinit var adapter: MyAdapter
    private var isLoading = false
    private var currentPage = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        adapter = MyAdapter(items)
        val layoutManager = LinearLayoutManager(this)

        val recyclerView = findViewById<RecyclerView>(R.id.recyclerView)
        recyclerView.layoutManager = layoutManager
        recyclerView.adapter = adapter

        // Add scroll listener for data prefetching
        recyclerView.addOnScrollListener(object : RecyclerView.OnScrollListener() {
            override fun onScrolled(recyclerView: RecyclerView, dx: Int, dy: Int) {
                super.onScrolled(recyclerView, dx, dy)

                val visibleItemCount = layoutManager.childCount
                val totalItemCount = layoutManager.itemCount
                val firstVisibleItemPosition = layoutManager.findFirstVisibleItemPosition()

                // Prefetch when approaching the end
                val threshold = 5 // Start loading 5 items before the end
                if (!isLoading &&
                    (visibleItemCount + firstVisibleItemPosition + threshold) >= totalItemCount) {
                    loadMoreData()
                }
            }
        })

        // Load initial data
        loadMoreData()
    }

    private fun loadMoreData() {
        if (isLoading) return

        isLoading = true

        // Simulate network call
        lifecycleScope.launch {
            val newItems = fetchItemsFromNetwork(currentPage)
            items.addAll(newItems)
            adapter.notifyItemRangeInserted(items.size - newItems.size, newItems.size)
            currentPage++
            isLoading = false
        }
    }

    private suspend fun fetchItemsFromNetwork(page: Int): List<Item> {
        // Simulate network delay
        delay(1000)
        return List(20) { Item("Item ${page * 20 + it}") }
    }
}
```

### 4. Advanced Prefetch with Custom LayoutManager

```kotlin
class AdvancedPrefetchLayoutManager(
    context: Context,
    private val prefetchItemCount: Int = 10
) : LinearLayoutManager(context) {

    init {
        isItemPrefetchEnabled = true
    }

    override fun collectAdjacentPrefetchPositions(
        dx: Int,
        dy: Int,
        state: RecyclerView.State,
        layoutPrefetchRegistry: LayoutPrefetchRegistry
    ) {
        super.collectAdjacentPrefetchPositions(dx, dy, state, layoutPrefetchRegistry)

        // Determine scroll direction
        val scrollingDown = dy > 0

        // Get currently visible range
        val firstVisible = findFirstVisibleItemPosition()
        val lastVisible = findLastVisibleItemPosition()

        if (scrollingDown) {
            // Prefetch items below
            val startPos = lastVisible + 1
            val endPos = minOf(startPos + prefetchItemCount, state.itemCount)
            for (i in startPos until endPos) {
                layoutPrefetchRegistry.addPosition(i, 0)
            }
        } else {
            // Prefetch items above
            val endPos = firstVisible - 1
            val startPos = maxOf(endPos - prefetchItemCount, 0)
            for (i in startPos..endPos) {
                layoutPrefetchRegistry.addPosition(i, 0)
            }
        }
    }
}
```

### 5. Image Prefetching with Glide/Coil

Prefetch images for upcoming items.

```kotlin
class ImagePrefetchAdapter(
    private val items: List<ImageItem>
) : RecyclerView.Adapter<ImagePrefetchAdapter.ViewHolder>() {

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position])

        // Prefetch next images
        prefetchUpcomingImages(position)
    }

    private fun prefetchUpcomingImages(currentPosition: Int) {
        val prefetchCount = 5
        val startPos = currentPosition + 1
        val endPos = minOf(startPos + prefetchCount, items.size)

        for (i in startPos until endPos) {
            Glide.with(context)
                .load(items[i].imageUrl)
                .preload()
        }
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val imageView: ImageView = itemView.findViewById(R.id.imageView)

        fun bind(item: ImageItem) {
            Glide.with(itemView.context)
                .load(item.imageUrl)
                .into(imageView)
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_image, parent, false)
        return ViewHolder(view)
    }

    override fun getItemCount() = items.size
}
```

### 6. RecyclerView Pool for Nested RecyclerViews

```kotlin
class ParentAdapter(
    private val items: List<ParentItem>
) : RecyclerView.Adapter<ParentAdapter.ViewHolder>() {

    // Shared pool for all nested RecyclerViews
    private val sharedPool = RecyclerView.RecycledViewPool().apply {
        setMaxRecycledViews(0, 20) // viewType 0, max 20 views
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val nestedRecyclerView: RecyclerView = itemView.findViewById(R.id.nestedRecyclerView)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_parent, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]

        holder.nestedRecyclerView.apply {
            // Use shared pool
            setRecycledViewPool(sharedPool)

            // Increase cache size
            setItemViewCacheSize(10)

            // Setup layout manager with prefetching
            layoutManager = LinearLayoutManager(
                context,
                LinearLayoutManager.HORIZONTAL,
                false
            ).apply {
                isItemPrefetchEnabled = true
                initialPrefetchItemCount = 4
            }

            // Set adapter
            adapter = ChildAdapter(item.children)
        }
    }

    override fun getItemCount() = items.size
}
```

### 7. Complete Optimized Example

```kotlin
class OptimizedRecyclerViewSetup(
    private val activity: AppCompatActivity
) {

    fun setupRecyclerView(
        recyclerView: RecyclerView,
        items: List<Item>
    ) {
        // 1. Configure view caching
        recyclerView.setItemViewCacheSize(20)

        // 2. Setup optimized layout manager
        val layoutManager = LinearLayoutManager(activity).apply {
            isItemPrefetchEnabled = true
            initialPrefetchItemCount = 6
        }
        recyclerView.layoutManager = layoutManager

        // 3. Configure RecycledViewPool
        recyclerView.recycledViewPool.setMaxRecycledViews(0, 30)

        // 4. Enable optimizations
        recyclerView.setHasFixedSize(true) // If size doesn't change
        recyclerView.isNestedScrollingEnabled = true

        // 5. Setup adapter
        val adapter = OptimizedAdapter(items)
        recyclerView.adapter = adapter

        // 6. Add data prefetching listener
        recyclerView.addOnScrollListener(object : RecyclerView.OnScrollListener() {
            override fun onScrolled(recyclerView: RecyclerView, dx: Int, dy: Int) {
                super.onScrolled(recyclerView, dx, dy)

                val visibleItemCount = layoutManager.childCount
                val totalItemCount = layoutManager.itemCount
                val firstVisibleItem = layoutManager.findFirstVisibleItemPosition()

                // Prefetch data when nearing end
                if ((visibleItemCount + firstVisibleItem + 10) >= totalItemCount) {
                    prefetchMoreData()
                }
            }
        })
    }

    private fun prefetchMoreData() {
        // Load more data from network/database
    }
}
```

### Best Practices Summary

1. **setItemViewCacheSize(20-30)** - Cache views for smooth scrolling
2. **Enable prefetching** - Use LinearLayoutManager with prefetching enabled
3. **setInitialPrefetchItemCount()** - Prefetch items on initial load
4. **Implement scroll listener** - Load data before reaching the end
5. **Shared RecycledViewPool** - For nested RecyclerViews
6. **Image prefetching** - Preload images using Glide/Coil
7. **setHasFixedSize(true)** - If RecyclerView size doesn't change
8. **Custom LayoutManager** - For advanced prefetching logic

### Performance Metrics

```kotlin
// Monitor prefetching effectiveness
recyclerView.addOnScrollListener(object : RecyclerView.OnScrollListener() {
    private var totalScroll = 0

    override fun onScrolled(recyclerView: RecyclerView, dx: Int, dy: Int) {
        totalScroll += abs(dy)

        // Log metrics every 1000px of scroll
        if (totalScroll > 1000) {
            Log.d("Prefetch", "Cache hit rate: ${getCacheHitRate()}")
            totalScroll = 0
        }
    }
})
```

## Ответ (RU)

1. Использовать setItemViewCacheSize для кэширования определённого количества элементов. 2. Включить предзагрузку данных с помощью RecyclerView.OnScrollListener. 3. Реализовать Prefetching через LinearLayoutManager или RecyclerView.LayoutManager.

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
