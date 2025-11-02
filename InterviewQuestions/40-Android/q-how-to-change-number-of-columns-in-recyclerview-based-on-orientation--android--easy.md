---
id: android-146
title: "How To Change Number Of Columns In RecyclerView Based On Orientation / Как изменить количество колонок в RecyclerView в зависимости от ориентации"
aliases: ["Change RecyclerView Columns by Orientation", "Изменить количество колонок RecyclerView по ориентации"]
topic: android
subtopics: [ui-views, ui-widgets]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-looper-empty-queue-behavior--android--medium, q-recyclerview-sethasfixedsize--android--easy]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android, android/ui-views, android/ui-widgets, difficulty/easy, grid-layout, recyclerview]
date created: Monday, October 27th 2025, 3:57:01 pm
date modified: Saturday, November 1st 2025, 5:43:35 pm
---

# Вопрос (RU)

Как изменить количество колонок в RecyclerView в зависимости от ориентации устройства?

# Question (EN)

How do you change the number of columns in RecyclerView based on device orientation?

---

## Ответ (RU)

Используй **GridLayoutManager** с динамическим spanCount в зависимости от ориентации. Оптимальный подход — через ресурсы `dimens.xml`, который автоматически адаптируется при rotation.

### Рекомендуемый Подход: dimens.xml

```xml
<!-- res/values/dimens.xml (Portrait) -->
<resources>
    <integer name="grid_column_count">2</integer>
</resources>

<!-- res/values-land/dimens.xml (Landscape) -->
<resources>
    <integer name="grid_column_count">4</integer>
</resources>
```

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val spanCount = resources.getInteger(R.integer.grid_column_count)
        // ✅ Система автоматически выбирает значение при смене ориентации

        val recyclerView = findViewById<RecyclerView>(R.id.recyclerView)
        recyclerView.layoutManager = GridLayoutManager(this, spanCount)
        recyclerView.adapter = MyAdapter(items)
    }
}
```

**Преимущества:**
- Нет необходимости обрабатывать `onConfigurationChanged()`
- Поддержка планшетов через `res/values-sw600dp/`
- Проще в тестировании и поддержке

### Альтернатива: Programmatic

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
            4  // ✅ Landscape: больше колонок
        } else {
            2  // ✅ Portrait: меньше колонок
        }

        recyclerView.layoutManager = GridLayoutManager(this, spanCount)
        recyclerView.adapter = MyAdapter(items)
    }

    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        // ❌ Требует android:configChanges="orientation|screenSize" в манифесте
        (recyclerView.layoutManager as? GridLayoutManager)?.spanCount =
            if (newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE) 4 else 2
    }
}
```

### Адаптивный Подход: По Ширине

```kotlin
class AdaptiveGridLayoutManager(
    context: Context,
    private val columnWidth: Int  // минимальная ширина колонки в px
) : GridLayoutManager(context, 1) {

    override fun onLayoutChildren(recycler: RecyclerView.Recycler?, state: RecyclerView.State?) {
        val totalSpace = width - paddingRight - paddingLeft
        val spanCount = maxOf(1, totalSpace / columnWidth)
        // ✅ Динамически вычисляет количество колонок под любой экран
        setSpanCount(spanCount)
        super.onLayoutChildren(recycler, state)
    }
}

// Usage
val columnWidthPx = (120 * resources.displayMetrics.density).toInt()
recyclerView.layoutManager = AdaptiveGridLayoutManager(this, columnWidthPx)
```

## Answer (EN)

Use **GridLayoutManager** with dynamic spanCount based on orientation. The optimal approach is through `dimens.xml` resources, which automatically adapts on rotation.

### Recommended: dimens.xml Approach

```xml
<!-- res/values/dimens.xml (Portrait) -->
<resources>
    <integer name="grid_column_count">2</integer>
</resources>

<!-- res/values-land/dimens.xml (Landscape) -->
<resources>
    <integer name="grid_column_count">4</integer>
</resources>
```

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val spanCount = resources.getInteger(R.integer.grid_column_count)
        // ✅ System automatically picks value on orientation change

        val recyclerView = findViewById<RecyclerView>(R.id.recyclerView)
        recyclerView.layoutManager = GridLayoutManager(this, spanCount)
        recyclerView.adapter = MyAdapter(items)
    }
}
```

**Benefits:**
- No need to handle `onConfigurationChanged()`
- Tablet support via `res/values-sw600dp/`
- Easier to test and maintain

### Alternative: Programmatic

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
            4  // ✅ Landscape: more columns
        } else {
            2  // ✅ Portrait: fewer columns
        }

        recyclerView.layoutManager = GridLayoutManager(this, spanCount)
        recyclerView.adapter = MyAdapter(items)
    }

    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        // ❌ Requires android:configChanges="orientation|screenSize" in manifest
        (recyclerView.layoutManager as? GridLayoutManager)?.spanCount =
            if (newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE) 4 else 2
    }
}
```

### Adaptive Approach: by Width

```kotlin
class AdaptiveGridLayoutManager(
    context: Context,
    private val columnWidth: Int  // minimum column width in px
) : GridLayoutManager(context, 1) {

    override fun onLayoutChildren(recycler: RecyclerView.Recycler?, state: RecyclerView.State?) {
        val totalSpace = width - paddingRight - paddingLeft
        val spanCount = maxOf(1, totalSpace / columnWidth)
        // ✅ Dynamically calculates columns for any screen
        setSpanCount(spanCount)
        super.onLayoutChildren(recycler, state)
    }
}

// Usage
val columnWidthPx = (120 * resources.displayMetrics.density).toInt()
recyclerView.layoutManager = AdaptiveGridLayoutManager(this, columnWidthPx)
```

---

## Follow-ups

- How does GridLayoutManager handle span sizes for items with different widths?
- What's the impact of changing spanCount on RecyclerView performance during rotation?
- How do you preserve scroll position when spanCount changes?
- When should you use StaggeredGridLayoutManager vs GridLayoutManager?

## References

- [[c-recyclerview]]
- [[c-configuration-changes]]

## Related Questions

### Prerequisites
- [[q-recyclerview-sethasfixedsize--android--easy]] - RecyclerView basics

### Related
- [[q-looper-empty-queue-behavior--android--medium]] - Configuration handling
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Compose alternative

### Advanced
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - Advanced RecyclerView patterns
