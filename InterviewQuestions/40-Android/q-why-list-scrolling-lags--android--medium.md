---
topic: android
tags:
  - android
  - android/performance
  - android/recyclerview
  - diffutil
  - optimization
  - performance
  - recyclerview
  - scrolling
  - viewholder
difficulty: medium
status: draft
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-android
related_questions: []
---

# Почему при скролле может тормозить список?

**English**: Why might list scrolling lag?

## Answer (EN)
List scrolling can lag due to **performance issues in RecyclerView** implementation. The main causes are:

## 1. Incorrect ViewHolder Usage

**Problem:** Not using ViewHolder pattern or using it incorrectly.

### - BAD: No ViewHolder (ListView pattern)

```kotlin
// Old ListView approach - SLOW
class MyAdapter : BaseAdapter() {
    override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
        val view = convertView ?: layoutInflater.inflate(R.layout.item, parent, false)

        // findViewById called every time! BAD
        val title = view.findViewById<TextView>(R.id.title)
        val description = view.findViewById<TextView>(R.id.description)
        val image = view.findViewById<ImageView>(R.id.image)

        title.text = items[position].title
        description.text = items[position].description
        image.setImageResource(items[position].imageRes)

        return view
    }
}
```

**Problem:** findViewById() called on every scroll.

### - GOOD: Proper ViewHolder

```kotlin
class MyAdapter : RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val title: TextView = view.findViewById(R.id.title)
        val description: TextView = view.findViewById(R.id.description)
        val image: ImageView = view.findViewById(R.id.image)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item, parent, false)
        return ViewHolder(view)  // findViewById called ONCE
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]
        holder.title.text = item.title
        holder.description.text = item.description
        holder.image.setImageResource(item.imageRes)
    }
}
```

**Benefit:** findViewById() called only once per ViewHolder.

### - BETTER: ViewBinding

```kotlin
class MyAdapter : RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    class ViewHolder(val binding: ItemLayoutBinding) :
        RecyclerView.ViewHolder(binding.root)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemLayoutBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]
        holder.binding.apply {
            title.text = item.title
            description.text = item.description
            image.setImageResource(item.imageRes)
        }
    }
}
```

---

## 2. Heavy Operations in onBindViewHolder

**Problem:** Long-running operations block UI during scrolling.

### - BAD: Heavy operations in onBindViewHolder

```kotlin
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val item = items[position]

    // - Synchronous image loading - BLOCKS UI!
    val bitmap = BitmapFactory.decodeFile(item.imagePath)
    holder.image.setImageBitmap(bitmap)

    // - Data processing - SLOW!
    val processedData = item.data.map { it.process() }
    holder.description.text = processedData.joinToString()

    // - Database query - BLOCKS UI!
    val relatedItems = database.getRelatedItems(item.id)
    holder.relatedCount.text = relatedItems.size.toString()
}
```

**Result:** Scrolling stutters on every item.

### - GOOD: Async operations with libraries

```kotlin
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val item = items[position]

    // - Async image loading with Glide
    Glide.with(holder.itemView.context)
        .load(item.imagePath)
        .placeholder(R.drawable.placeholder)
        .into(holder.image)

    // - Use pre-processed data
    holder.description.text = item.processedDescription

    // - Use cached/pre-fetched data
    holder.relatedCount.text = item.relatedItemsCount.toString()
}
```

**Key principle:** onBindViewHolder should **only set data**, not compute it.

---

## 3. Unoptimized Image Handling

**Problem:** Loading images without proper library support.

### - BAD: Manual image loading

```kotlin
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val item = items[position]

    // - No caching, no resizing
    Thread {
        val bitmap = BitmapFactory.decodeFile(item.imagePath)
        holder.itemView.post {
            holder.image.setImageBitmap(bitmap)
        }
    }.start()
}
```

**Problems:**
- No caching (reloads on scroll)
- No memory management
- Thread creation overhead
- Full-resolution images

### - GOOD: Using Glide

```kotlin
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val item = items[position]

    Glide.with(holder.itemView.context)
        .load(item.imageUrl)
        .override(200, 200)  // Resize
        .centerCrop()
        .placeholder(R.drawable.placeholder)
        .error(R.drawable.error)
        .into(holder.image)
}
```

**Benefits:**
- Automatic caching (memory + disk)
- Image resizing
- Lifecycle awareness
- Thread pool management

### - GOOD: Using Coil (Kotlin-first)

```kotlin
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val item = items[position]

    holder.image.load(item.imageUrl) {
        crossfade(true)
        placeholder(R.drawable.placeholder)
        transformations(CircleCropTransformation())
        size(200, 200)
    }
}
```

---

## 4. Complex Layout Hierarchies

**Problem:** Deeply nested layouts cause slow inflation and rendering.

### - BAD: Complex nested layout

```xml
<!-- item_complex.xml - 5 levels deep! -->
<LinearLayout>
    <RelativeLayout>
        <LinearLayout orientation="horizontal">
            <FrameLayout>
                <LinearLayout orientation="vertical">
                    <TextView android:id="@+id/title" />
                    <TextView android:id="@+id/description" />
                </LinearLayout>
            </FrameLayout>
        </LinearLayout>
    </RelativeLayout>
</LinearLayout>
```

**Result:** Slow layout inflation on every scroll.

### - GOOD: Flat ConstraintLayout

```xml
<!-- item_simple.xml - 1 level only! -->
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content">

    <ImageView
        android:id="@+id/image"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

    <TextView
        android:id="@+id/title"
        app:layout_constraintStart_toEndOf="@id/image"
        app:layout_constraintTop_toTopOf="parent" />

    <TextView
        android:id="@+id/description"
        app:layout_constraintStart_toEndOf="@id/image"
        app:layout_constraintTop_toBottomOf="@id/title" />
</androidx.constraintlayout.widget.ConstraintLayout>
```

**Alternatives:**
- Use **ViewStub** for conditionally displayed views
- Use **merge** tag when appropriate
- Avoid nested LinearLayout with weights

---

## 5. Excessive notifyDataSetChanged()

**Problem:** Redrawing entire list instead of specific items.

### - BAD: Full list refresh

```kotlin
fun updateData(newItems: List<Item>) {
    items = newItems
    notifyDataSetChanged()  // - Redraws EVERYTHING!
}

fun addItem(item: Item) {
    items = items + item
    notifyDataSetChanged()  // - Redraws entire list for 1 item!
}
```

**Result:** All visible items re-rendered, scrolling resets.

### - GOOD: Granular updates

```kotlin
fun addItem(item: Item) {
    items = items + item
    notifyItemInserted(items.size - 1)  // - Only new item animated
}

fun removeItem(position: Int) {
    items = items.toMutableList().also { it.removeAt(position) }
    notifyItemRemoved(position)  // - Only removed item animated
}

fun updateItem(position: Int, item: Item) {
    items = items.toMutableList().also { it[position] = item }
    notifyItemChanged(position)  // - Only changed item updated
}
```

### - BEST: DiffUtil

```kotlin
fun updateData(newItems: List<Item>) {
    val diffCallback = object : DiffUtil.Callback() {
        override fun getOldListSize() = items.size
        override fun getNewListSize() = newItems.size

        override fun areItemsTheSame(oldPos: Int, newPos: Int): Boolean {
            return items[oldPos].id == newItems[newPos].id
        }

        override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
            return items[oldPos] == newItems[newPos]
        }
    }

    val diffResult = DiffUtil.calculateDiff(diffCallback)
    items = newItems
    diffResult.dispatchUpdatesTo(this)  // - Optimal updates!
}
```

### - EVEN BETTER: ListAdapter (DiffUtil built-in)

```kotlin
class MyAdapter : ListAdapter<Item, MyAdapter.ViewHolder>(ItemDiffCallback()) {

    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem == newItem
        }
    }

    // ... ViewHolder and binding code
}

// Usage
adapter.submitList(newItems)  // - DiffUtil automatically applied!
```

---

## 6. Missing Data Caching

**Problem:** Reloading data on every scroll.

### - BAD: No caching

```kotlin
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val item = items[position]

    // - Loads from network every time!
    viewModelScope.launch {
        val details = api.getItemDetails(item.id)
        holder.details.text = details
    }
}
```

**Result:** Network request for every visible item on scroll.

### - GOOD: LiveData caching

```kotlin
class ItemViewModel : ViewModel() {
    private val _items = MutableLiveData<List<Item>>()
    val items: LiveData<List<Item>> = _items

    init {
        loadItems()
    }

    private fun loadItems() {
        viewModelScope.launch {
            val data = repository.getItems()  // Cached in repository
            _items.value = data
        }
    }
}

// In Activity/Fragment
viewModel.items.observe(viewLifecycleOwner) { items ->
    adapter.submitList(items)  // Data cached in ViewModel
}
```

### - GOOD: Repository pattern with caching

```kotlin
class ItemRepository(
    private val api: ApiService,
    private val database: ItemDao
) {
    fun getItems(): Flow<List<Item>> {
        return database.getItemsFlow()  // Room caches in database
            .onStart {
                refreshFromNetwork()  // Refresh in background
            }
    }

    private suspend fun refreshFromNetwork() {
        try {
            val items = api.getItems()
            database.insertAll(items)  // Update cache
        } catch (e: Exception) {
            // Use cached data if network fails
        }
    }
}
```

---

## Summary of Causes

| Cause | Problem | Solution |
|-------|---------|----------|
| **No ViewHolder** | findViewById on every scroll | Use RecyclerView.ViewHolder or ViewBinding |
| **Heavy operations in onBindViewHolder** | Blocking UI thread | Pre-process data, use async operations |
| **Unoptimized images** | No caching, full resolution | Use Glide, Coil, or Picasso |
| **Complex layouts** | Slow inflation | Use ConstraintLayout, flat hierarchy |
| **notifyDataSetChanged()** | Full list redraw | Use DiffUtil or ListAdapter |
| **No caching** | Reload on scroll | Use LiveData, Flow, Repository pattern |

---

## Best Practices

### - DO

1. **Use RecyclerView.ViewHolder** or ViewBinding
2. **Keep onBindViewHolder simple** (only set data, no computation)
3. **Use image loading libraries** (Glide, Coil, Picasso)
4. **Optimize layouts** (ConstraintLayout, flat hierarchy)
5. **Use DiffUtil/ListAdapter** for updates
6. **Cache data** (LiveData, Flow, Repository)
7. **Pre-fetch data** before binding
8. **Use RecyclerView.RecycledViewPool** for nested lists
9. **Set fixed size** if list size doesn't change:
   ```kotlin
   recyclerView.setHasFixedSize(true)
   ```
10. **Profile performance** (Systrace, GPU Profiling)

### - DON'T

1. - Use findViewById in onBindViewHolder
2. - Load images synchronously
3. - Perform database queries in onBindViewHolder
4. - Process data in onBindViewHolder
5. - Use notifyDataSetChanged() for small updates
6. - Create complex nested layouts
7. - Allocate objects in onBindViewHolder
8. - Use large uncompressed images

---

## Performance Optimization Tips

### 1. Enable Prefetching

```kotlin
val layoutManager = LinearLayoutManager(context)
layoutManager.isItemPrefetchEnabled = true  // Default: true
layoutManager.initialPrefetchItemCount = 4  // Prefetch 4 items
recyclerView.layoutManager = layoutManager
```

### 2. RecycledViewPool for Nested Lists

```kotlin
val sharedPool = RecyclerView.RecycledViewPool()

parentAdapter.onBindViewHolder { holder, position ->
    holder.childRecyclerView.setRecycledViewPool(sharedPool)
}
```

### 3. Payload for Partial Updates

```kotlin
class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
    override fun areItemsTheSame(oldItem: Item, newItem: Item) =
        oldItem.id == newItem.id

    override fun areContentsTheSame(oldItem: Item, newItem: Item) =
        oldItem == newItem

    override fun getChangePayload(oldItem: Item, newItem: Item): Any? {
        return if (oldItem.title != newItem.title) {
            "TITLE_CHANGED"  // Payload for partial update
        } else null
    }
}

override fun onBindViewHolder(holder: ViewHolder, position: Int, payloads: List<Any>) {
    if (payloads.isEmpty()) {
        super.onBindViewHolder(holder, position, payloads)
    } else {
        payloads.forEach { payload ->
            if (payload == "TITLE_CHANGED") {
                holder.title.text = getItem(position).title  // Only update title
            }
        }
    }
}
```

---

## Ответ (RU)
Причины торможения списка при скролле:

1. **Неправильное использование ViewHolder в RecyclerView** - findViewById вызывается каждый раз.

2. **Тяжелые операции в onBindViewHolder** - загрузка изображений или обработка данных без асинхронных задач и библиотек для загрузки изображений.

3. **Неправильная обработка изображений** - без использования библиотек, таких как Glide или Picasso.

4. **Неоптимизированные макеты** - сложные иерархии, которые можно упростить или использовать ViewStub для отложенной загрузки.

5. **Частые вызовы notifyDataSetChanged** - вместо использования notifyItemInserted, notifyItemRemoved или notifyItemChanged для частичных обновлений списка.

6. **Отсутствие кэширования данных** - что приводит к повторной загрузке при каждом скролле. Рекомендуется использовать LiveData для кэширования данных.


---

## Related Questions

### Computer Science Fundamentals
- [[q-list-vs-sequence--programming-languages--medium]] - Data Structures

### Kotlin Language Features
- [[q-list-set-map-differences--programming-languages--easy]] - Data Structures
- [[q-array-vs-list-kotlin--kotlin--easy]] - Data Structures
- [[q-kotlin-collections--kotlin--medium]] - Data Structures
- [[q-list-vs-sequence--kotlin--medium]] - Data Structures
- [[q-deferred-async-patterns--kotlin--medium]] - Performance
- [[q-channel-buffering-strategies--kotlin--hard]] - Performance

---

## Related Questions

### Computer Science Fundamentals
- [[q-list-vs-sequence--programming-languages--medium]] - Data Structures

### Kotlin Language Features
- [[q-list-set-map-differences--programming-languages--easy]] - Data Structures
- [[q-array-vs-list-kotlin--kotlin--easy]] - Data Structures
- [[q-kotlin-collections--kotlin--medium]] - Data Structures
- [[q-list-vs-sequence--kotlin--medium]] - Data Structures
- [[q-deferred-async-patterns--kotlin--medium]] - Performance
- [[q-channel-buffering-strategies--kotlin--hard]] - Performance
