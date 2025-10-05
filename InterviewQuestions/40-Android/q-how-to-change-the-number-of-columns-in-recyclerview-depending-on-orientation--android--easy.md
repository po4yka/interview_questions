---
tags:
  - recyclerview
  - gridlayoutmanager
  - android
  - ui
  - layouts
difficulty: medium
---

# How to change the number of columns in RecyclerView depending on orientation?

## Question (RU)

Как изменить количество колонок в RecyclerView в зависимости от ориентации

## Answer

You can use **GridLayoutManager** and set the number of columns dynamically based on screen orientation.

### Basic Implementation

```kotlin
class MainActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        recyclerView = findViewById(R.id.recyclerView)

        setupRecyclerView()
    }

    private fun setupRecyclerView() {
        val spanCount = if (resources.configuration.orientation == Configuration.ORIENTATION_LANDSCAPE) {
            4 // Landscape: 4 columns
        } else {
            2 // Portrait: 2 columns
        }

        recyclerView.layoutManager = GridLayoutManager(this, spanCount)
        recyclerView.adapter = MyAdapter(items)
    }

    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)

        // Update columns when orientation changes
        val spanCount = if (newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE) {
            4
        } else {
            2
        }

        (recyclerView.layoutManager as? GridLayoutManager)?.spanCount = spanCount
    }
}
```

### Using dimens.xml (Recommended)

```xml
<!-- res/values/dimens.xml (Portrait) -->
<resources>
    <integer name="grid_column_count">2</integer>
</resources>

<!-- res/values-land/dimens.xml (Landscape) -->
<resources>
    <integer name="grid_column_count">4</integer>
</resources>

<!-- res/values-sw600dp/dimens.xml (Tablets) -->
<resources>
    <integer name="grid_column_count">3</integer>
</resources>
```

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val spanCount = resources.getInteger(R.integer.grid_column_count)

        val recyclerView = findViewById<RecyclerView>(R.id.recyclerView)
        recyclerView.layoutManager = GridLayoutManager(this, spanCount)
        recyclerView.adapter = MyAdapter(items)
    }
}
```

### Dynamic Span Based on Screen Width

```kotlin
class AdaptiveGridLayoutManager(
    context: Context,
    private val columnWidth: Int // in dp
) : GridLayoutManager(context, 1) {

    private var lastWidth = 0
    private var lastHeight = 0

    override fun onLayoutChildren(recycler: RecyclerView.Recycler?, state: RecyclerView.State?) {
        val width = width
        val height = height

        if (width > 0 && height > 0 && (lastWidth != width || lastHeight != height)) {
            val totalSpace = if (orientation == VERTICAL) {
                width - paddingRight - paddingLeft
            } else {
                height - paddingTop - paddingBottom
            }

            val spanCount = maxOf(1, totalSpace / columnWidth)
            setSpanCount(spanCount)

            lastWidth = width
            lastHeight = height
        }

        super.onLayoutChildren(recycler, state)
    }
}

// Usage
val columnWidthDp = 120 // Minimum column width
val columnWidthPx = (columnWidthDp * resources.displayMetrics.density).toInt()

recyclerView.layoutManager = AdaptiveGridLayoutManager(this, columnWidthPx)
```

## Answer (RU)

Ты можешь использовать GridLayoutManager и задать количество колонок динамически
