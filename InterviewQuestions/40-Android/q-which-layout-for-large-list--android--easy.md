---
tags:
  - recyclerview
  - layout
  - easy_kotlin
  - android/recyclerview
  - android/ui
  - android
  - ui
difficulty: easy
---

# Какой layout выбрать для списка из большого количества элементов?

**English**: Which layout to choose for a list with a large number of elements?

## Answer

For displaying lists with a large number of elements in Android, you should use **RecyclerView**. It is the most efficient and recommended component for displaying large datasets in list or grid format.

### Why RecyclerView?

RecyclerView provides significant performance improvements through:

1. **View Recycling**: Reuses view holders instead of creating new views
2. **Efficient Memory Usage**: Only keeps visible items in memory
3. **Flexible Layout Management**: Supports lists, grids, and custom layouts
4. **Built-in Animations**: Provides smooth item animations
5. **Modular Design**: Separates layout, data, and view logic

### Basic RecyclerView Implementation

```kotlin
// 1. Add dependency in build.gradle
dependencies {
    implementation "androidx.recyclerview:recyclerview:1.3.2"
}

// 2. Add to layout XML
<androidx.recyclerview.widget.RecyclerView
    android:id="@+id/recyclerView"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />

// 3. Create ViewHolder and Adapter
class MyAdapter(private val items: List<String>) :
    RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val textView: TextView = view.findViewById(R.id.textView)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.textView.text = items[position]
    }

    override fun getItemCount() = items.size
}

// 4. Set up RecyclerView
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val recyclerView: RecyclerView = findViewById(R.id.recyclerView)
        recyclerView.layoutManager = LinearLayoutManager(this)
        recyclerView.adapter = MyAdapter(generateLargeList())
    }

    private fun generateLargeList(): List<String> {
        return (1..10000).map { "Item $it" }
    }
}
```

### Different Layout Managers

#### 1. LinearLayoutManager (Vertical List)

```kotlin
recyclerView.layoutManager = LinearLayoutManager(this)
```

#### 2. LinearLayoutManager (Horizontal List)

```kotlin
recyclerView.layoutManager = LinearLayoutManager(
    this,
    LinearLayoutManager.HORIZONTAL,
    false
)
```

#### 3. GridLayoutManager (Grid)

```kotlin
// 2 columns
recyclerView.layoutManager = GridLayoutManager(this, 2)
```

#### 4. StaggeredGridLayoutManager (Pinterest-style)

```kotlin
recyclerView.layoutManager = StaggeredGridLayoutManager(
    2, // span count
    StaggeredGridLayoutManager.VERTICAL
)
```

### Modern Approach with ListAdapter

For better performance with large changing datasets:

```kotlin
class MyAdapter : ListAdapter<String, MyAdapter.ViewHolder>(DiffCallback()) {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val textView: TextView = view.findViewById(R.id.textView)

        fun bind(item: String) {
            textView.text = item
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

    class DiffCallback : DiffUtil.ItemCallback<String>() {
        override fun areItemsTheSame(oldItem: String, newItem: String): Boolean {
            return oldItem == newItem
        }

        override fun areContentsTheSame(oldItem: String, newItem: String): Boolean {
            return oldItem == newItem
        }
    }
}
```

### View Binding in RecyclerView

```kotlin
class MyAdapter(private val items: List<String>) :
    RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    class ViewHolder(private val binding: ItemLayoutBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(item: String) {
            binding.textView.text = item
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
        holder.bind(items[position])
    }

    override fun getItemCount() = items.size
}
```

### Performance Optimizations

```kotlin
// 1. Set fixed size if RecyclerView size doesn't change
recyclerView.setHasFixedSize(true)

// 2. Enable view recycling pool
recyclerView.setRecycledViewPool(RecyclerView.RecycledViewPool())

// 3. Enable item prefetching
(recyclerView.layoutManager as? LinearLayoutManager)?.apply {
    isItemPrefetchEnabled = true
}

// 4. Use DiffUtil for efficient updates
adapter.submitList(newList)
```

### Comparison: RecyclerView vs ListView

| Feature | RecyclerView | ListView |
|---------|--------------|----------|
| View Recycling | Enforced | Optional |
| Performance | Excellent | Poor for large lists |
| Flexibility | High | Limited |
| Animations | Built-in | Manual |
| Layout Options | Multiple | Vertical only |
| Recommendation | ✅ Preferred | ❌ Deprecated |

### When NOT to Use RecyclerView

For very small, static lists (< 20 items), simpler alternatives might suffice:
- **LinearLayout** with ScrollView (for ~5-10 items)
- **Compose LazyColumn** (for new Compose projects)

### Jetpack Compose Alternative

```kotlin
@Composable
fun MyList(items: List<String>) {
    LazyColumn {
        items(items) { item ->
            Text(
                text = item,
                modifier = Modifier.padding(16.dp)
            )
        }
    }
}
```

## Ответ

Для списка из большого количества элементов следует использовать RecyclerView. Это наиболее эффективный и рекомендуемый компонент для отображения больших данных в виде списка или сетки в Android

