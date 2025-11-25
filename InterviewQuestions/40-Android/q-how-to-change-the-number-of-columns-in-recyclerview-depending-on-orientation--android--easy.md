---
id: android-188
title: How To Change The Number Of Columns In RecyclerView Depending On Orientation / Как изменить количество колонок в RecyclerView в зависимости от ориентации
aliases: [How To Change The Number Of Columns In RecyclerView Depending On Orientation, Как изменить количество колонок в RecyclerView в зависимости от ориентации]
topic: android
subtopics:
  - ui-views
question_kind: theory
difficulty: easy
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-android
  - q-broadcastreceiver-contentprovider--android--easy
  - q-compose-ui-testing-advanced--android--hard
  - q-how-animations-work-in-recyclerview--android--medium
  - q-how-to-change-number-of-columns-in-recyclerview-based-on-orientation--android--easy
  - q-recyclerview-itemdecoration-advanced--android--medium
created: 2024-10-15
updated: 2025-11-10
tags: [android/ui-views, difficulty/easy]

date created: Saturday, November 1st 2025, 12:46:52 pm
date modified: Tuesday, November 25th 2025, 8:54:00 pm
---

# Вопрос (RU)
> Как изменить количество колонок в RecyclerView в зависимости от ориентации

# Question (EN)
> How To Change The Number Of Columns In RecyclerView Depending On Orientation

## Ответ (RU)

Вы можете использовать `GridLayoutManager` и динамически задавать количество колонок в зависимости от ориентации экрана.

### Базовая Реализация

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
            4 // Ландшафт: 4 колонки
        } else {
            2 // Портрет: 2 колонки
        }

        recyclerView.layoutManager = GridLayoutManager(this, spanCount)
        recyclerView.adapter = MyAdapter(items)
    }

    // Вариант с обработкой смены ориентации через onConfigurationChanged
    // Требует указать configChanges в манифесте для Activity, иначе она будет пересоздана.
    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)

        val spanCount = if (newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE) {
            4
        } else {
            2
        }

        (recyclerView.layoutManager as? GridLayoutManager)?.spanCount = spanCount
    }
}
```

> Примечание: Чаще всего при смене ориентации `Activity` пересоздаётся, и `spanCount` можно пересчитать в `onCreate`/`onViewCreated`. Использование `onConfigurationChanged` требует соответствующей настройки в `AndroidManifest`.

### Использование dimens.xml (рекомендуется)

```xml
<!-- res/values/dimens.xml (портрет) -->
<resources>
    <integer name="grid_column_count">2</integer>
</resources>

<!-- res/values-land/dimens.xml (ландшафт) -->
<resources>
    <integer name="grid_column_count">4</integer>
</resources>

<!-- res/values-sw600dp/dimens.xml (планшеты) -->
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

### Динамический Span В Зависимости От Ширины Экрана (опционально)

```kotlin
class AdaptiveGridLayoutManager(
    context: Context,
    private val columnWidthPx: Int // минимальная ширина колонки в пикселях
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

            val newSpanCount = maxOf(1, totalSpace / columnWidthPx)
            spanCount = newSpanCount

            lastWidth = width
            lastHeight = height
        }

        super.onLayoutChildren(recycler, state)
    }
}

// Использование
val columnWidthDp = 120 // минимальная ширина колонки в dp
val columnWidthPx = (columnWidthDp * resources.displayMetrics.density).toInt()

recyclerView.layoutManager = AdaptiveGridLayoutManager(this, columnWidthPx)
```

## Дополнительные Вопросы (RU)

- [[q-broadcastreceiver-contentprovider--android--easy]]
- [[q-compose-ui-testing-advanced--android--hard]]
- Как реализовать адаптивное количество колонок с учётом `sw600dp` и планшетов?
- Как обрабатывать изменение ориентации без пересоздания `Activity` и какие у этого последствия?
- Когда стоит использовать `StaggeredGridLayoutManager` вместо `GridLayoutManager`?

## Ссылки (RU)

- https://developer.android.com/develop/ui/views
- https://developer.android.com/docs
- [[c-android]]

## Связанные Вопросы (RU)

### Предпосылки / Концепции (RU)

- Android UI основы

### Похожие (средний уровень) (RU)

- [[q-recyclerview-sethasfixedsize--android--easy]] - `View`, UI

### Продвинутые (сложнее) (RU)

- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - `View`, UI
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - `View`, UI

---

## Answer (EN)

You can use `GridLayoutManager` and set the number of columns dynamically based on screen orientation.

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

    // Variant using onConfigurationChanged to handle orientation changes.
    // Requires declaring configChanges for this Activity in AndroidManifest,
    // otherwise the Activity will be recreated instead.
    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)

        val spanCount = if (newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE) {
            4
        } else {
            2
        }

        (recyclerView.layoutManager as? GridLayoutManager)?.spanCount = spanCount
    }
}
```

> Note: In typical setups, the `Activity` is recreated on orientation change, so you can recalculate `spanCount` in `onCreate`/`onViewCreated`. Using `onConfigurationChanged` requires proper manifest configuration.

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

### Dynamic Span Based on Screen Width (Optional)

```kotlin
class AdaptiveGridLayoutManager(
    context: Context,
    private val columnWidthPx: Int // minimum column width in pixels
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

            val newSpanCount = maxOf(1, totalSpace / columnWidthPx)
            spanCount = newSpanCount

            lastWidth = width
            lastHeight = height
        }

        super.onLayoutChildren(recycler, state)
    }
}

// Usage
val columnWidthDp = 120 // Minimum column width in dp
val columnWidthPx = (columnWidthDp * resources.displayMetrics.density).toInt()

recyclerView.layoutManager = AdaptiveGridLayoutManager(this, columnWidthPx)
```

## Follow-ups

- [[q-broadcastreceiver-contentprovider--android--easy]]
- [[q-compose-ui-testing-advanced--android--hard]]
- How to design adaptive span counts for tablets and large screens using `sw600dp`?
- How to handle orientation changes without recreating the `Activity`, and what are the trade-offs?
- When should you use `StaggeredGridLayoutManager` instead of `GridLayoutManager`?

## References

- https://developer.android.com/develop/ui/views
- https://developer.android.com/docs
- [[c-android]]

## Related Questions

### Prerequisites / Concepts

- Basic Android UI concepts

### Related (Medium)
- [[q-recyclerview-sethasfixedsize--android--easy]] - `View`, UI

### Advanced (Harder)
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - `View`, UI
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - `View`, UI
