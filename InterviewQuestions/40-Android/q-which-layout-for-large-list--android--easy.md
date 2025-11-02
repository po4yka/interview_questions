---
id: android-372
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
updated: 2025-10-30

# Tags (EN only; no leading #)
tags: [android/ui-views, android/performance-memory, recyclerview, difficulty/easy]
---

# Вопрос (RU)

> Какой layout выбрать для списка из большого количества элементов?

# Question (EN)

> Which layout to choose for a list with a large number of elements?

---

## Ответ (RU)

Для больших списков используйте **RecyclerView** — современный компонент Android с переиспользованием views.

### Почему RecyclerView?

**Ключевые преимущества**:
1. **View Recycling** — переиспользует ViewHolder'ы вместо создания новых
2. **Эффективная память** — держит в памяти только видимые элементы
3. **Гибкие LayoutManager'ы** — вертикальные/горизонтальные списки, сетки
4. **Встроенные анимации** — плавные изменения списка

### Базовая реализация

```kotlin
class MyAdapter(private val items: List<String>) :
    RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val textView: TextView = view.findViewById(R.id.textView)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false) // ✅ attachToRoot = false
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
}
```

### LayoutManager'ы

```kotlin
// Вертикальный список
LinearLayoutManager(context)

// Сетка
GridLayoutManager(context, spanCount = 2)

// Горизонтальный список
LinearLayoutManager(context, HORIZONTAL, false)
```

### Сравнение: RecyclerView vs ListView

| Критерий | RecyclerView | ListView |
|----------|--------------|----------|
| View Recycling | ✅ Обязательный ViewHolder | Опциональный |
| Производительность | ✅ Отличная | ❌ Плохая для больших списков |
| Layout варианты | ✅ Списки, сетки | ❌ Только список |
| Статус | ✅ Рекомендуется | ❌ Deprecated |

### Когда НЕ использовать RecyclerView

Для маленьких статических списков (<20 элементов):
- **LinearLayout + ScrollView** — для 5-10 элементов
- **Compose LazyColumn** — для проектов на Jetpack Compose

## Answer (EN)

For large lists, use **RecyclerView** — Android's modern component with view recycling.

### Why RecyclerView?

**Key advantages**:
1. **View Recycling** — reuses ViewHolders instead of creating new views
2. **Memory Efficiency** — keeps only visible items in memory
3. **Flexible LayoutManagers** — vertical/horizontal lists, grids
4. **Built-in Animations** — smooth list changes

### Basic Implementation

```kotlin
class MyAdapter(private val items: List<String>) :
    RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val textView: TextView = view.findViewById(R.id.textView)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false) // ✅ attachToRoot = false
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
}
```

### LayoutManagers

```kotlin
// Vertical list
LinearLayoutManager(context)

// Grid
GridLayoutManager(context, spanCount = 2)

// Horizontal list
LinearLayoutManager(context, HORIZONTAL, false)
```

### Comparison: RecyclerView vs ListView

| Criterion | RecyclerView | ListView |
|-----------|--------------|----------|
| View Recycling | ✅ Mandatory ViewHolder | Optional |
| Performance | ✅ Excellent | ❌ Poor for large lists |
| Layout Options | ✅ Lists, grids | ❌ List only |
| Status | ✅ Recommended | ❌ Deprecated |

### When NOT to Use RecyclerView

For small static lists (<20 items):
- **LinearLayout + ScrollView** — for 5-10 items
- **Compose LazyColumn** — for Jetpack Compose projects

---

## Follow-ups

- What is the ViewHolder pattern and why is it mandatory in RecyclerView?
- What are the main differences between RecyclerView and ListView?
- What LayoutManagers does RecyclerView support out of the box?
- When would you use GridLayoutManager instead of LinearLayoutManager?
- How does RecyclerView handle memory efficiently for large lists?

## References

- [[c-recyclerview]] — RecyclerView concept
- [[c-view-recycling]] — View recycling pattern
- [[c-adapter-pattern]] — Adapter design pattern
- https://developer.android.com/guide/topics/ui/layout/recyclerview — RecyclerView guide

## Related Questions

### Prerequisites (Easier)

- [[q-recyclerview-sethasfixedsize--android--easy]] — RecyclerView optimization
- [[q-what-is-view--android--easy]] — View basics

### Related (Same Level)

- [[q-what-is-viewholder--android--easy]] — ViewHolder pattern
- [[q-recyclerview-adapter--android--easy]] — RecyclerView adapter

### Advanced (Harder)

- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] — Compose LazyColumn
- [[q-what-do-you-know-about-modifications--android--medium]] — List updates
- [[q-diffutil-recyclerview--android--medium]] — DiffUtil for efficient updates
