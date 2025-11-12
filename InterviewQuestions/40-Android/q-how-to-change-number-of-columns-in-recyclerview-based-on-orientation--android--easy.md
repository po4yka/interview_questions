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
related: [c-recyclerview, q-looper-empty-queue-behavior--android--medium, q-recyclerview-sethasfixedsize--android--easy]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android, android/ui-views, android/ui-widgets, difficulty/easy, grid-layout, recyclerview]

---

# Вопрос (RU)

> Как изменить количество колонок в RecyclerView в зависимости от ориентации устройства?

# Question (EN)

> How do you change the number of columns in RecyclerView based on device orientation?

---

## Ответ (RU)

Используй `GridLayoutManager` с динамическим `spanCount` в зависимости от ориентации. Оптимальный подход — через ресурсы `dimens.xml`, которые автоматически подхватываются при пересоздании `Activity` после смены конфигурации (включая ориентацию).

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
        // System автоматически выберет нужное значение после пересоздания Activity

        val recyclerView = findViewById<RecyclerView>(R.id.recyclerView)
        recyclerView.layoutManager = GridLayoutManager(this, spanCount)
        recyclerView.adapter = MyAdapter(items)
    }
}
```

**Преимущества:**
- Нет необходимости обрабатывать `onConfigurationChanged()` вручную (рекомендуемый подход)
- Поддержка планшетов через `res/values-sw600dp/`
- Проще в тестировании и поддержке

### Альтернатива: Программно

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
            4  // Landscape: больше колонок
        } else {
            2  // Portrait: меньше колонок
        }

        recyclerView.layoutManager = GridLayoutManager(this, spanCount)
        recyclerView.adapter = MyAdapter(items)
    }

    // Использовать только если вы осознанно берёте на себя обработку конфигурационных изменений
    // и добавили android:configChanges="orientation|screenSize" для этой Activity в манифесте.
    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        (recyclerView.layoutManager as? GridLayoutManager)?.spanCount =
            if (newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE) 4 else 2
        // При необходимости здесь же можно переустановить адаптер или вызвать recyclerView.requestLayout()
    }
}
```

### Адаптивный Подход: По ширине

```kotlin
class AdaptiveGridLayoutManager(
    context: Context,
    private val columnWidth: Int  // минимальная ширина колонки в px
) : GridLayoutManager(context, 1) {

    override fun onLayoutChildren(recycler: RecyclerView.Recycler?, state: RecyclerView.State?) {
        val totalSpace = width - paddingRight - paddingLeft
        val spanCount = maxOf(1, totalSpace / columnWidth)
        // Динамически вычисляет количество колонок под любой экран, гарантируя минимум 1 колонку
        setSpanCount(spanCount)
        super.onLayoutChildren(recycler, state)
    }
}

// Usage
val columnWidthPx = (120 * resources.displayMetrics.density).toInt()
recyclerView.layoutManager = AdaptiveGridLayoutManager(this, columnWidthPx)
```

## Answer (EN)

Use `GridLayoutManager` with dynamic `spanCount` based on orientation. The optimal approach is via `dimens.xml` resources, which are automatically reapplied when the `Activity` is recreated on configuration changes (including rotation).

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
        // System automatically picks the correct value after Activity recreation

        val recyclerView = findViewById<RecyclerView>(R.id.recyclerView)
        recyclerView.layoutManager = GridLayoutManager(this, spanCount)
        recyclerView.adapter = MyAdapter(items)
    }
}
```

**Benefits:**
- No need to manually handle `onConfigurationChanged()` (recommended approach)
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
            4  // Landscape: more columns
        } else {
            2  // Portrait: fewer columns
        }

        recyclerView.layoutManager = GridLayoutManager(this, spanCount)
        recyclerView.adapter = MyAdapter(items)
    }

    // Use only if you intentionally handle configuration changes yourself
    // and have android:configChanges="orientation|screenSize" set for this Activity in the manifest.
    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        (recyclerView.layoutManager as? GridLayoutManager)?.spanCount =
            if (newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE) 4 else 2
        // If needed, you can also re-set the adapter or call recyclerView.requestLayout() here.
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
        // Dynamically calculates columns for any screen, ensuring at least 1 column
        setSpanCount(spanCount)
        super.onLayoutChildren(recycler, state)
    }
}

// Usage
val columnWidthPx = (120 * resources.displayMetrics.density).toInt()
recyclerView.layoutManager = AdaptiveGridLayoutManager(this, columnWidthPx)
```

---

## Дополнительные вопросы (RU)

- Как `GridLayoutManager` обрабатывает span sizes для элементов с разной шириной?
- Как изменение `spanCount` влияет на производительность `RecyclerView` при изменении ориентации?
- Как сохранить позицию прокрутки при изменении `spanCount`?
- Когда стоит использовать `StaggeredGridLayoutManager` вместо `GridLayoutManager`?

## Follow-ups

- How does `GridLayoutManager` handle span sizes for items with different widths?
- What's the impact of changing `spanCount` on `RecyclerView` performance during rotation?
- How do you preserve scroll position when `spanCount` changes?
- When should you use `StaggeredGridLayoutManager` vs `GridLayoutManager`?

## Ссылки (RU)

- [[c-recyclerview]]

## References

- [[c-recyclerview]]

## Связанные вопросы (RU)

### Предварительные знания
- [[q-recyclerview-sethasfixedsize--android--easy]] - Базовые концепции RecyclerView

### Связанные
- [[q-looper-empty-queue-behavior--android--medium]] - Обработка конфигурационных изменений
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Альтернатива на Compose

### Продвинутые
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - Продвинутые паттерны RecyclerView

## Related Questions

### Prerequisites
- [[q-recyclerview-sethasfixedsize--android--easy]] - RecyclerView basics

### Related
- [[q-looper-empty-queue-behavior--android--medium]] - Configuration handling
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Compose alternative

### Advanced
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - Advanced RecyclerView patterns
