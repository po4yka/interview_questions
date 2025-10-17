---
id: 20251006-100008
title: "What is setHasFixedSize(true) in RecyclerView? / Что такое setHasFixedSize(true) в RecyclerView?"
aliases: []

# Classification
topic: android
subtopics: [recyclerview, performance, optimization]
question_kind: explanation
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru, android/recyclerview, android/performance, android/optimization, difficulty/easy]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-android
related: []

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [en, ru, android/recyclerview, android/performance, android/optimization, difficulty/easy]
---

# Question (EN)

> What is setHasFixedSize(true) in RecyclerView?

# Вопрос (RU)

> Что такое setHasFixedSize(true) в RecyclerView?

---

## Answer (EN)

`setHasFixedSize(true)` is a performance optimization method in RecyclerView that tells the RecyclerView that **its size will not change** when the adapter's content changes (items added, removed, or updated).

### How It Works

When you call `setHasFixedSize(true)`, you're informing RecyclerView that:
- Adding items won't change RecyclerView's dimensions
- Removing items won't change RecyclerView's dimensions
- The RecyclerView can skip expensive layout calculations

### Performance Impact

```kotlin
// - Use when RecyclerView size is fixed
recyclerView.apply {
    layoutManager = LinearLayoutManager(context)
    adapter = myAdapter
    setHasFixedSize(true)  // Optimization: size won't change
}
```

**What happens internally:**

Without `setHasFixedSize(true)`:
```
Item Added/Removed
    ↓
requestLayout() called
    ↓
Entire view hierarchy remeasured
    ↓
Expensive operations
```

With `setHasFixedSize(true)`:
```
Item Added/Removed
    ↓
Only RecyclerView content updates
    ↓
View hierarchy NOT remeasured
    ↓
Better performance
```

### When to Use

#### Use `setHasFixedSize(true)` when:

1. **RecyclerView fills parent**

```kotlin
// Size determined by parent, won't change
<androidx.recyclerview.widget.RecyclerView
    android:layout_width="match_parent"
    android:layout_height="match_parent" />

recyclerView.setHasFixedSize(true)  // - Safe to use
```

2. **RecyclerView has fixed dimensions**

```kotlin
// Fixed size in dp/px
<androidx.recyclerview.widget.RecyclerView
    android:layout_width="match_parent"
    android:layout_height="400dp" />

recyclerView.setHasFixedSize(true)  // - Safe to use
```

3. **Inside ConstraintLayout with constraints**

```kotlin
<androidx.constraintlayout.widget.ConstraintLayout>
    <androidx.recyclerview.widget.RecyclerView
        android:layout_width="0dp"
        android:layout_height="0dp"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent" />
</androidx.constraintlayout.widget.ConstraintLayout>

recyclerView.setHasFixedSize(true)  // - Safe to use
```

#### DON'T use `setHasFixedSize(true)` when:

1. **RecyclerView uses wrap_content**

```kotlin
// Size changes based on content
<androidx.recyclerview.widget.RecyclerView
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />

recyclerView.setHasFixedSize(true)  // - Don't use!
// Size WILL change as items are added/removed
```

2. **Dynamic content changes RecyclerView bounds**

```kotlin
// Example: Expandable items that change RecyclerView size
recyclerView.setHasFixedSize(true)  // - Don't use if items expand/collapse
```

### Code Examples

#### Example 1: Typical Usage (Full Screen List)

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val recyclerView = findViewById<RecyclerView>(R.id.recyclerView)
        val adapter = UserAdapter()

        recyclerView.apply {
            layoutManager = LinearLayoutManager(this@MainActivity)
            this.adapter = adapter
            setHasFixedSize(true)  // - RecyclerView is match_parent
        }

        adapter.submitList(getUsers())
    }
}
```

```xml
<!-- activity_main.xml -->
<androidx.recyclerview.widget.RecyclerView
    android:id="@+id/recyclerView"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

#### Example 2: With ConstraintLayout

```kotlin
class ProductListFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.recyclerView.apply {
            layoutManager = GridLayoutManager(context, 2)
            adapter = ProductAdapter()
            setHasFixedSize(true)  // - Size constrained by layout
        }
    }
}
```

```xml
<androidx.constraintlayout.widget.ConstraintLayout>
    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/recyclerView"
        android:layout_width="0dp"
        android:layout_height="0dp"
        app:layout_constraintTop_toBottomOf="@id/toolbar"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent" />
</androidx.constraintlayout.widget.ConstraintLayout>
```

#### Example 3: Performance Comparison

```kotlin
class PerformanceTestActivity : AppCompatActivity() {
    private lateinit var adapter: TestAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Without setHasFixedSize
        val recyclerViewSlow = findViewById<RecyclerView>(R.id.recyclerViewSlow)
        recyclerViewSlow.apply {
            layoutManager = LinearLayoutManager(this@PerformanceTestActivity)
            adapter = TestAdapter()
            // setHasFixedSize NOT set - slower
        }

        // With setHasFixedSize
        val recyclerViewFast = findViewById<RecyclerView>(R.id.recyclerViewFast)
        recyclerViewFast.apply {
            layoutManager = LinearLayoutManager(this@PerformanceTestActivity)
            adapter = TestAdapter()
            setHasFixedSize(true)  // - Faster
        }

        // Benchmark: Add 1000 items
        measureTimeMillis {
            repeat(1000) {
                adapter.addItem(Item(it, "Item $it"))
            }
        }.also { time ->
            Log.d("Performance", "Time taken: $time ms")
        }
    }
}
```

### Impact on Different Operations

```kotlin
class BenchmarkAdapter : RecyclerView.Adapter<BenchmarkAdapter.ViewHolder>() {
    private val items = mutableListOf<String>()

    // Adding item
    fun addItem(item: String) {
        items.add(item)
        notifyItemInserted(items.size - 1)
        // With setHasFixedSize(true): Only item view created
        // Without: Entire RecyclerView remeasured
    }

    // Removing item
    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)
        // With setHasFixedSize(true): Only affected items shifted
        // Without: Entire RecyclerView remeasured
    }

    // Updating item
    fun updateItem(position: Int, item: String) {
        items[position] = item
        notifyItemChanged(position)
        // With setHasFixedSize(true): Only item view updated
        // Without: Entire RecyclerView remeasured
    }

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        // Bind data
    }

    override fun getItemCount() = items.size
}
```

### Comparison Table

| Scenario | setHasFixedSize(true) | setHasFixedSize(false) |
|----------|----------------------|------------------------|
| RecyclerView remeasured on item add/remove | - No | - Yes |
| Parent view hierarchy remeasured | - No | - Yes |
| Performance with many updates | - Fast | - Slower |
| Works with wrap_content height | - No | - Yes |
| Works with match_parent | - Yes | - Yes |
| Works with fixed dimensions | - Yes | - Yes |

### Best Practices

1. **Use for full-screen lists**

```kotlin
// - GOOD
recyclerView.apply {
    layoutManager = LinearLayoutManager(context)
    setHasFixedSize(true)  // RecyclerView is match_parent
}
```

2. **Use for fixed-dimension layouts**

```kotlin
// - GOOD
recyclerView.apply {
    layoutManager = GridLayoutManager(context, 2)
    setHasFixedSize(true)  // Fixed grid layout
}
```

3. **DON'T use with wrap_content**

```kotlin
// - BAD
<RecyclerView
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />

recyclerView.setHasFixedSize(true)  // Wrong! Size changes with content
```

4. **Combine with other optimizations**

```kotlin
recyclerView.apply {
    setHasFixedSize(true)
    setItemViewCacheSize(20)  // Increase cache
    recycledViewPool.setMaxRecycledViews(0, 20)  // Pool size
}
```

### Common Mistakes

**Mistake 1: Using with wrap_content**

```kotlin
// - WRONG
<RecyclerView
    android:layout_height="wrap_content" />

recyclerView.setHasFixedSize(true)  // Inconsistent!
```

**Mistake 2: Assuming it affects adapter**

```kotlin
// - MISCONCEPTION
recyclerView.setHasFixedSize(true)
// This does NOT mean adapter size is fixed!
// It means RecyclerView VIEW size is fixed

adapter.addItem()  // Still works fine
adapter.removeItem()  // Still works fine
```

### Summary

**setHasFixedSize(true)** tells RecyclerView:
- "My dimensions won't change when content changes"
- Skip expensive layout recalculations
- Improve performance for add/remove/update operations

**Use when:**
- RecyclerView uses `match_parent` or fixed dimensions
- RecyclerView is constrained by parent layout

**Don't use when:**
- RecyclerView uses `wrap_content`
- RecyclerView size changes based on content

---

## Ответ (RU)

`setHasFixedSize(true)` — это метод оптимизации производительности в RecyclerView, который сообщает RecyclerView, что **его размер не изменится** при изменении содержимого адаптера (добавление, удаление или обновление элементов).

### Как это работает

Когда вы вызываете `setHasFixedSize(true)`, вы информируете RecyclerView:
- Добавление элементов не изменит размеры RecyclerView
- Удаление элементов не изменит размеры RecyclerView
- RecyclerView может пропустить дорогостоящие вычисления layout

### Влияние на производительность

Без `setHasFixedSize(true)`:
- При добавлении/удалении элемента вызывается `requestLayout()`
- Вся иерархия представлений пересчитывается
- Дорогостоящие операции

С `setHasFixedSize(true)`:
- Обновляется только содержимое RecyclerView
- Иерархия представлений НЕ пересчитывается
- Лучшая производительность

### Когда использовать

Используйте `setHasFixedSize(true)` когда:
- RecyclerView заполняет родительский контейнер (`match_parent`)
- RecyclerView имеет фиксированные размеры
- RecyclerView находится внутри ConstraintLayout с ограничениями

НЕ используйте когда:
- RecyclerView использует `wrap_content`
- Динамическое содержимое изменяет границы RecyclerView

---

## Related Questions

### Advanced (Harder)
- [[q-macrobenchmark-startup--performance--medium]] - Performance
- [[q-app-startup-optimization--performance--medium]] - Performance
- [[q-baseline-profiles-optimization--performance--medium]] - Performance

## References
- [RecyclerView Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/RecyclerView#setHasFixedSize(boolean))
- [RecyclerView Performance](https://developer.android.com/topic/performance/rendering/recyclerview)
