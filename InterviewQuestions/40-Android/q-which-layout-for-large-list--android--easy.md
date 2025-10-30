---
id: 20251012-122711
title: "Which Layout For Large List / Какой layout для большого списка"
aliases: ["Which Layout For Large List", "Какой layout для большого списка"]

# Classification
topic: android
subtopics: [ui-views, performance-memory]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
sources: []

# Workflow & relations
status: draft
moc: moc-android
related: [q-recyclerview-sethasfixedsize--android--easy, q-what-do-you-know-about-modifications--android--medium, q-how-to-create-list-like-recyclerview-in-compose--android--medium]

# Timestamps
created: 2025-10-15
updated: 2025-10-29

# Tags (EN only; no leading #)
tags: [android/ui-views, android/performance-memory, recyclerview, ui, layout, difficulty/easy]
---
# Вопрос (RU)

> Какой layout выбрать для списка из большого количества элементов?

# Question (EN)

> Which layout to choose for a list with a large number of elements?

---

## Ответ (RU)

Для отображения больших списков используйте **RecyclerView** — современный компонент Android с эффективным переиспользованием представлений.

### Почему RecyclerView?

**Ключевые преимущества**:
1. **View Recycling** — переиспользует ViewHolder'ы вместо создания новых
2. **Эффективная память** — держит в памяти только видимые элементы
3. **Гибкие LayoutManager'ы** — списки, сетки, каскады, горизонтальная прокрутка
4. **Встроенные анимации** — плавные insert/remove/change операции
5. **Модульная архитектура** — разделение layout, data, view логики

### Базовая реализация

```kotlin
// ViewHolder + Adapter
class MyAdapter(private val items: List<String>) :
    RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val textView: TextView = view.findViewById(R.id.textView)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        // ✅ attachToRoot = false — правильно
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.textView.text = items[position]
    }

    override fun getItemCount() = items.size
}

// Setup в Activity/Fragment
recyclerView.apply {
    layoutManager = LinearLayoutManager(context)
    adapter = MyAdapter(largeDataset)
    setHasFixedSize(true) // ✅ оптимизация, если размер не меняется
}
```

### LayoutManager'ы

```kotlin
// Вертикальный список
LinearLayoutManager(context)

// Сетка (2 колонки)
GridLayoutManager(context, 2)

// Каскадная сетка (Pinterest-style)
StaggeredGridLayoutManager(2, VERTICAL)
```

### ListAdapter + DiffUtil (рекомендуется)

Для динамических данных используйте `ListAdapter` с автоматическим diff:

```kotlin
class MyAdapter : ListAdapter<Item, MyAdapter.ViewHolder>(DiffCallback) {

    object DiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(old: Item, new: Item) = old.id == new.id
        override fun areContentsTheSame(old: Item, new: Item) = old == new
    }

    // onCreateViewHolder, onBindViewHolder...
}

// Обновление данных — автоматический diff на фоновом потоке
adapter.submitList(newList)
```

### Оптимизации производительности

```kotlin
// 1. Фиксированный размер (если не изменяется)
recyclerView.setHasFixedSize(true)

// 2. Item prefetch (включён по умолчанию в LinearLayoutManager)
(layoutManager as? LinearLayoutManager)?.isItemPrefetchEnabled = true

// 3. Shared RecycledViewPool для вложенных RecyclerView
val sharedPool = RecyclerView.RecycledViewPool()
recyclerView.setRecycledViewPool(sharedPool)

// 4. ❌ Не создавайте объекты в onBindViewHolder
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    // ❌ Плохо: новый объект каждый раз
    holder.textView.setOnClickListener { onClick(items[position]) }

    // ✅ Хорошо: слушатель создаётся один раз в onCreateViewHolder
}
```

### Сравнение: RecyclerView vs ListView

| Критерий | RecyclerView | ListView |
|----------|--------------|----------|
| View Recycling | Обязательный ViewHolder | Опциональный |
| Производительность | Отличная | Плохая для больших списков |
| Layout варианты | Списки, сетки, каскады | Только вертикальный список |
| Анимации | Встроенные | Ручная реализация |
| Статус | ✅ Рекомендуется | ❌ Deprecated |

### Когда НЕ использовать RecyclerView

Для маленьких статических списков (<20 элементов):
- **LinearLayout + ScrollView** — простейший вариант для 5-10 элементов
- **Compose LazyColumn** — для проектов на Jetpack Compose

### Jetpack Compose альтернатива

```kotlin
@Composable
fun MyList(items: List<String>) {
    LazyColumn {
        items(items) { item ->
            Text(item, modifier = Modifier.padding(16.dp))
        }
    }
}
```

## Answer (EN)

For large lists, use **RecyclerView** — Android's modern component with efficient view recycling.

### Why RecyclerView?

**Key advantages**:
1. **View Recycling** — reuses ViewHolders instead of creating new views
2. **Memory Efficiency** — keeps only visible items in memory
3. **Flexible LayoutManagers** — lists, grids, staggered grids, horizontal scrolling
4. **Built-in Animations** — smooth insert/remove/change operations
5. **Modular Architecture** — separates layout, data, view logic

### Basic Implementation

```kotlin
// ViewHolder + Adapter
class MyAdapter(private val items: List<String>) :
    RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val textView: TextView = view.findViewById(R.id.textView)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        // ✅ attachToRoot = false — correct
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.textView.text = items[position]
    }

    override fun getItemCount() = items.size
}

// Setup in Activity/Fragment
recyclerView.apply {
    layoutManager = LinearLayoutManager(context)
    adapter = MyAdapter(largeDataset)
    setHasFixedSize(true) // ✅ optimization if size doesn't change
}
```

### LayoutManagers

```kotlin
// Vertical list
LinearLayoutManager(context)

// Grid (2 columns)
GridLayoutManager(context, 2)

// Staggered grid (Pinterest-style)
StaggeredGridLayoutManager(2, VERTICAL)
```

### ListAdapter + DiffUtil (Recommended)

For dynamic data, use `ListAdapter` with automatic diffing:

```kotlin
class MyAdapter : ListAdapter<Item, MyAdapter.ViewHolder>(DiffCallback) {

    object DiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(old: Item, new: Item) = old.id == new.id
        override fun areContentsTheSame(old: Item, new: Item) = old == new
    }

    // onCreateViewHolder, onBindViewHolder...
}

// Update data — automatic diff on background thread
adapter.submitList(newList)
```

### Performance Optimizations

```kotlin
// 1. Fixed size (if doesn't change)
recyclerView.setHasFixedSize(true)

// 2. Item prefetch (enabled by default in LinearLayoutManager)
(layoutManager as? LinearLayoutManager)?.isItemPrefetchEnabled = true

// 3. Shared RecycledViewPool for nested RecyclerViews
val sharedPool = RecyclerView.RecycledViewPool()
recyclerView.setRecycledViewPool(sharedPool)

// 4. ❌ Don't create objects in onBindViewHolder
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    // ❌ Bad: new object every time
    holder.textView.setOnClickListener { onClick(items[position]) }

    // ✅ Good: listener created once in onCreateViewHolder
}
```

### Comparison: RecyclerView vs ListView

| Criterion | RecyclerView | ListView |
|-----------|--------------|----------|
| View Recycling | Mandatory ViewHolder | Optional |
| Performance | Excellent | Poor for large lists |
| Layout Options | Lists, grids, staggered | Vertical list only |
| Animations | Built-in | Manual implementation |
| Status | ✅ Recommended | ❌ Deprecated |

### When NOT to Use RecyclerView

For small static lists (<20 items):
- **LinearLayout + ScrollView** — simplest for 5-10 items
- **Compose LazyColumn** — for Jetpack Compose projects

### Jetpack Compose Alternative

```kotlin
@Composable
fun MyList(items: List<String>) {
    LazyColumn {
        items(items) { item ->
            Text(item, modifier = Modifier.padding(16.dp))
        }
    }
}
```

---

## Follow-ups

- When should you use `ListAdapter + DiffUtil` instead of plain `RecyclerView.Adapter`?
- How does `setHasFixedSize(true)` improve performance and when shouldn't you use it?
- What's the difference between `notifyDataSetChanged()` and `DiffUtil` for list updates?
- How do you implement infinite scroll pagination with RecyclerView?
- When would you choose Compose `LazyColumn` over RecyclerView?

## References

- [RecyclerView Guide](https://developer.android.com/guide/topics/ui/layout/recyclerview) — Official Android documentation
- [DiffUtil Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil) — Efficient list updates
- [LayoutManager Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/RecyclerView.LayoutManager) — Layout manager reference

## Related Questions

### Prerequisites (Easier)

- [[q-recyclerview-sethasfixedsize--android--easy]] — RecyclerView optimization
- [[q-viewmodel-pattern--android--easy]] — ViewModel basics

### Related (Same Level)

- [[q-what-do-you-know-about-modifications--android--medium]] — UI modifications
- [[q-what-events-are-activity-methods-tied-to--android--medium]] — Activity lifecycle

### Advanced (Harder)

- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] — Compose LazyColumn
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] — View redrawing
