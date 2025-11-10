---
id: android-372
title: "Which Layout For Large List / Какой layout для большого списка"
aliases: ["Which Layout For Large List", "Какой layout для большого списка"]
topic: android
subtopics: [performance-memory, ui-views]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
sources: []
status: draft
moc: moc-android
related: [c-recyclerview, q-recyclerview-sethasfixedsize--android--easy]
created: 2025-10-15
updated: 2025-11-10
tags: [android/performance-memory, android/ui-views, difficulty/easy, recyclerview]

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
1. **`View` Recycling** — переиспользует ViewHolder'ы вместо создания новых
2. **Эффективная память** — держит в памяти только видимые элементы
3. **Гибкие LayoutManager'ы** — вертикальные/горизонтальные списки, сетки
4. **Встроенные анимации** — плавные изменения списка

### Базовая Реализация

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

### Сравнение: RecyclerView Vs ListView

| Критерий | RecyclerView | ListView |
|----------|--------------|----------|
| `View` Recycling | ✅ Требуется использование ViewHolder-класса в API RecyclerView.Adapter | Опциональный ViewHolder-паттерн как оптимизация |
| Производительность | ✅ Лучше масштабируется для больших динамических списков | ⚠️ Подходит, но менее гибок и обычно не рекомендуется для сложных/очень больших списков |
| Layout варианты | ✅ Списки, сетки и др. через LayoutManager | ❌ По умолчанию только вертикальный список |
| Статус | ✅ Рекомендуется для новых реализаций | ⚠️ Не устаревший формально, но считается устаревающим решением по сравнению с RecyclerView |

### Когда НЕ Использовать RecyclerView

Для маленьких статических списков (<20 элементов), где нет сложной логики и переиспользование не критично, можно упростить:
- **LinearLayout + ScrollView** — для 5-10 элементов
- **Compose LazyColumn** — для проектов на Jetpack Compose

---

## Дополнительные вопросы (RU)

- Что такое паттерн ViewHolder и почему он обязателен в RecyclerView?
- Каковы основные отличия между RecyclerView и ListView?
- Какие LayoutManager'ы поддерживает RecyclerView "из коробки"?
- Когда стоит использовать GridLayoutManager вместо LinearLayoutManager?
- Как RecyclerView эффективно работает с памятью для больших списков?

## Ссылки (RU)

- [[c-recyclerview]] — концепт RecyclerView
- https://developer.android.com/guide/topics/ui/layout/recyclerview — руководство по RecyclerView

## Связанные вопросы (RU)

### Предварительные (проще)

- [[q-recyclerview-sethasfixedsize--android--easy]] — оптимизация RecyclerView
- [[q-what-is-intent--android--easy]] — основы `View`

### На том же уровне сложности

- [[q-android-app-components--android--easy]] — обзор компонентов Android-приложения

### Продвинутые (сложнее)

- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] — Compose LazyColumn
- [[q-what-do-you-know-about-modifications--android--medium]] — обновление `List`

## Answer (EN)

For large lists, use **RecyclerView** — Android's modern component with view recycling.

### Why RecyclerView?

**Key advantages**:
1. **`View` Recycling** — reuses ViewHolders instead of creating new views
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

### Comparison: RecyclerView Vs ListView

| Criterion | RecyclerView | ListView |
|-----------|--------------|----------|
| `View` Recycling | ✅ Requires a ViewHolder class in the RecyclerView.Adapter API | Optional ViewHolder pattern as an optimization |
| Performance | ✅ Scales better for large, dynamic lists | ⚠️ Usable, but less flexible and generally not recommended for complex/very large lists |
| Layout Options | ✅ Lists, grids, etc. via LayoutManagers | ❌ Only vertical list by default |
| Status | ✅ Recommended for new implementations | ⚠️ Not formally deprecated, but considered legacy compared to RecyclerView |

### When NOT to Use RecyclerView

For small static lists (<20 items) where complexity and recycling are not critical, you can keep it simpler:
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
- https://developer.android.com/guide/topics/ui/layout/recyclerview — RecyclerView guide

## Related Questions

### Prerequisites (Easier)

- [[q-recyclerview-sethasfixedsize--android--easy]] — RecyclerView optimization
- [[q-what-is-intent--android--easy]] — `View` basics

### Related (Same Level)

- [[q-android-app-components--android--easy]] — Android app components overview

### Advanced (Harder)

- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] — Compose LazyColumn
- [[q-what-do-you-know-about-modifications--android--medium]] — `List` updates
