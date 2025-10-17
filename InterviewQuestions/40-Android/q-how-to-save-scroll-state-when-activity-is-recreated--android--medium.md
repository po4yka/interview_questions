---
id: 20251012-1227197
title: "How To Save Scroll State When Activity Is Recreated / Как сохранить состояние скролла при пересоздании Activity"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - android
---
# How to save scroll state when Activity is recreated?

## Answer (EN)
When an Activity is recreated due to configuration changes or process death, scroll position in ScrollView or RecyclerView is reset. This can be prevented by saving and restoring scroll state.

### Method 1: ScrollView with onSaveInstanceState

```kotlin
class MainActivity : AppCompatActivity() {

    private lateinit var scrollView: ScrollView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        scrollView = findViewById(R.id.scrollView)

        // Restore scroll position
        savedInstanceState?.let {
            val scrollX = it.getInt(KEY_SCROLL_X, 0)
            val scrollY = it.getInt(KEY_SCROLL_Y, 0)

            scrollView.post {
                scrollView.scrollTo(scrollX, scrollY)
            }
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        // Save current scroll position
        outState.putInt(KEY_SCROLL_X, scrollView.scrollX)
        outState.putInt(KEY_SCROLL_Y, scrollView.scrollY)
    }

    companion object {
        private const val KEY_SCROLL_X = "scroll_x"
        private const val KEY_SCROLL_Y = "scroll_y"
    }
}
```

### Method 2: RecyclerView with LayoutManager State

RecyclerView has built-in state saving mechanism:

```kotlin
class MainActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var layoutManager: LinearLayoutManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        recyclerView = findViewById(R.id.recyclerView)
        layoutManager = LinearLayoutManager(this)
        recyclerView.layoutManager = layoutManager

        // Restore RecyclerView state
        savedInstanceState?.let {
            val state = it.getParcelable<Parcelable>(KEY_RECYCLER_STATE)
            layoutManager.onRestoreInstanceState(state)
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        // Save RecyclerView state
        val state = layoutManager.onSaveInstanceState()
        outState.putParcelable(KEY_RECYCLER_STATE, state)
    }

    companion object {
        private const val KEY_RECYCLER_STATE = "recycler_state"
    }
}
```

### Method 3: RecyclerView Simple Position Save

```kotlin
class MainActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private val adapter = MyAdapter()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        recyclerView = findViewById(R.id.recyclerView)
        recyclerView.adapter = adapter
        recyclerView.layoutManager = LinearLayoutManager(this)

        // Restore scroll position
        savedInstanceState?.let {
            val position = it.getInt(KEY_SCROLL_POSITION, 0)
            recyclerView.scrollToPosition(position)
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        // Save first visible item position
        val position = (recyclerView.layoutManager as LinearLayoutManager)
            .findFirstVisibleItemPosition()
        outState.putInt(KEY_SCROLL_POSITION, position)
    }

    companion object {
        private const val KEY_SCROLL_POSITION = "scroll_position"
    }
}
```

### Method 4: RecyclerView with Exact Position and Offset

For precise scroll position restoration:

```kotlin
class MainActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var layoutManager: LinearLayoutManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        recyclerView = findViewById(R.id.recyclerView)
        layoutManager = LinearLayoutManager(this)
        recyclerView.layoutManager = layoutManager

        // Restore scroll position with offset
        savedInstanceState?.let {
            val position = it.getInt(KEY_SCROLL_POSITION, 0)
            val offset = it.getInt(KEY_SCROLL_OFFSET, 0)

            (recyclerView.layoutManager as LinearLayoutManager)
                .scrollToPositionWithOffset(position, offset)
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        val layoutManager = recyclerView.layoutManager as LinearLayoutManager

        // Save position and offset
        val position = layoutManager.findFirstVisibleItemPosition()
        val firstVisibleView = layoutManager.findViewByPosition(position)
        val offset = firstVisibleView?.top ?: 0

        outState.putInt(KEY_SCROLL_POSITION, position)
        outState.putInt(KEY_SCROLL_OFFSET, offset)
    }

    companion object {
        private const val KEY_SCROLL_POSITION = "scroll_position"
        private const val KEY_SCROLL_OFFSET = "scroll_offset"
    }
}
```

### Method 5: ViewModel for Persistent State

```kotlin
class ScrollViewModel : ViewModel() {

    // Survives configuration changes
    var scrollPosition: Int = 0
    var scrollOffset: Int = 0

    // For process death survival, use SavedStateHandle
    // private val savedStateHandle: SavedStateHandle
}

class MainActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private val viewModel: ScrollViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        recyclerView = findViewById(R.id.recyclerView)
        val layoutManager = LinearLayoutManager(this)
        recyclerView.layoutManager = layoutManager

        // Restore from ViewModel
        if (viewModel.scrollPosition > 0) {
            layoutManager.scrollToPositionWithOffset(
                viewModel.scrollPosition,
                viewModel.scrollOffset
            )
        }
    }

    override fun onPause() {
        super.onPause()

        // Save to ViewModel
        val layoutManager = recyclerView.layoutManager as LinearLayoutManager
        viewModel.scrollPosition = layoutManager.findFirstVisibleItemPosition()

        val firstVisibleView = layoutManager.findViewByPosition(viewModel.scrollPosition)
        viewModel.scrollOffset = firstVisibleView?.top ?: 0
    }
}
```

### Method 6: SavedStateHandle in ViewModel

Best practice - combines ViewModel and process death survival:

```kotlin
class ScrollViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    var scrollPosition: Int
        get() = savedStateHandle.get<Int>(KEY_SCROLL_POSITION) ?: 0
        set(value) { savedStateHandle.set(KEY_SCROLL_POSITION, value) }

    var scrollOffset: Int
        get() = savedStateHandle.get<Int>(KEY_SCROLL_OFFSET) ?: 0
        set(value) { savedStateHandle.set(KEY_SCROLL_OFFSET, value) }

    companion object {
        private const val KEY_SCROLL_POSITION = "scroll_position"
        private const val KEY_SCROLL_OFFSET = "scroll_offset"
    }
}

class MainActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private val viewModel: ScrollViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        setupRecyclerView()

        // Restore scroll state
        restoreScrollPosition()
    }

    private fun setupRecyclerView() {
        recyclerView = findViewById(R.id.recyclerView)
        recyclerView.layoutManager = LinearLayoutManager(this)
        recyclerView.adapter = MyAdapter()

        // Save scroll position when scrolling stops
        recyclerView.addOnScrollListener(object : RecyclerView.OnScrollListener() {
            override fun onScrollStateChanged(recyclerView: RecyclerView, newState: Int) {
                if (newState == RecyclerView.SCROLL_STATE_IDLE) {
                    saveScrollPosition()
                }
            }
        })
    }

    private fun saveScrollPosition() {
        val layoutManager = recyclerView.layoutManager as LinearLayoutManager
        viewModel.scrollPosition = layoutManager.findFirstVisibleItemPosition()

        val firstVisibleView = layoutManager.findViewByPosition(viewModel.scrollPosition)
        viewModel.scrollOffset = firstVisibleView?.top ?: 0
    }

    private fun restoreScrollPosition() {
        if (viewModel.scrollPosition > 0) {
            recyclerView.post {
                (recyclerView.layoutManager as LinearLayoutManager)
                    .scrollToPositionWithOffset(
                        viewModel.scrollPosition,
                        viewModel.scrollOffset
                    )
            }
        }
    }
}
```

### Method 7: GridLayoutManager

For grid layouts:

```kotlin
class MainActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var gridLayoutManager: GridLayoutManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        gridLayoutManager = GridLayoutManager(this, 2) // 2 columns
        recyclerView = findViewById(R.id.recyclerView)
        recyclerView.layoutManager = gridLayoutManager

        // Restore state
        savedInstanceState?.let {
            val state = it.getParcelable<Parcelable>(KEY_LAYOUT_STATE)
            gridLayoutManager.onRestoreInstanceState(state)
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        val state = gridLayoutManager.onSaveInstanceState()
        outState.putParcelable(KEY_LAYOUT_STATE, state)
    }

    companion object {
        private const val KEY_LAYOUT_STATE = "layout_state"
    }
}
```

### Method 8: NestedScrollView

```kotlin
class MainActivity : AppCompatActivity() {

    private lateinit var nestedScrollView: NestedScrollView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        nestedScrollView = findViewById(R.id.nestedScrollView)

        // Restore scroll position
        savedInstanceState?.let {
            val scrollY = it.getInt(KEY_SCROLL_Y, 0)
            nestedScrollView.post {
                nestedScrollView.scrollTo(0, scrollY)
            }
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putInt(KEY_SCROLL_Y, nestedScrollView.scrollY)
    }

    companion object {
        private const val KEY_SCROLL_Y = "scroll_y"
    }
}
```

### Comparison of Methods

| Method | Survives Config Change | Survives Process Death | Precision | Complexity |
|--------|------------------------|------------------------|-----------|------------|
| onSaveInstanceState | Yes | Yes | High | Low |
| LayoutManager state | Yes | Yes | Exact | Low |
| Simple position | Yes | Yes | Medium | Very Low |
| Position + offset | Yes | Yes | Exact | Medium |
| ViewModel only | Yes | No | Exact | Medium |
| SavedStateHandle | Yes | Yes | Exact | Medium |

### Best Practices

1. **Use LayoutManager.onSaveInstanceState()**: Most reliable for RecyclerView
2. **SavedStateHandle in ViewModel**: Best for production apps
3. **Post scroll operations**: Ensure view is laid out
4. **Save in onPause()**: For ViewModel approach
5. **Test process death**: Enable "Don't keep activities"

## Ответ (RU)
При пересоздании Activity состояние ScrollView или RecyclerView сбрасывается. Чтобы этого избежать, можно сохранить и восстановить позицию скролла. Использование onSaveInstanceState() позволяет сохранять данные в Bundle перед уничтожением Activity и восстанавливать их. Для RecyclerView можно использовать встроенный механизм сохранения состояния через LinearLayoutManager.

## Related Topics
- onSaveInstanceState
- RecyclerView state management
- LayoutManager
- SavedStateHandle
- ViewModel lifecycle

---

## Related Questions

### Prerequisites (Easier)
- [[q-android-components-besides-activity--android--easy]] - Activity

### Related (Medium)
- [[q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]] - Activity
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Activity
- [[q-single-activity-pros-cons--android--medium]] - Activity
- [[q-if-activity-starts-after-a-service-can-you-connect-to-this-service--android--medium]] - Activity
- [[q-activity-lifecycle-methods--android--medium]] - Activity

### Advanced (Harder)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Activity
