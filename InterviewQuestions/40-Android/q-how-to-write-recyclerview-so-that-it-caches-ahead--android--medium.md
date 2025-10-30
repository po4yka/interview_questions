---
id: 20251012-122711
title: "How To Write RecyclerView So That It Caches Ahead / Как написать RecyclerView чтобы он кешировал вперед"
aliases:
  - RecyclerView caching
  - RecyclerView prefetching
  - Кеширование RecyclerView
  - Предзагрузка RecyclerView
topic: android
subtopics: [ui-views, performance-rendering, performance-memory]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - q-recyclerview-sethasfixedsize--android--easy
  - q-how-animations-work-in-recyclerview--android--medium
  - q-recyclerview-async-list-differ--android--medium
sources: []
created: 2025-10-15
updated: 2025-10-30
tags:
  - android
  - android/ui-views
  - android/performance-rendering
  - android/performance-memory
  - recyclerview
  - caching
  - prefetching
  - difficulty/medium
---

# Вопрос (RU)

Как можно писать RecyclerView, чтобы он кэшировал наперёд?

---

# Question (EN)

How to write RecyclerView so that it caches ahead?

---

## Ответ (RU)

RecyclerView предоставляет несколько механизмов для кэширования элементов наперёд, улучшая производительность скроллинга.

### 1. Кэширование View через setItemViewCacheSize()

Кэш хранит недавно скрытые View без повторного биндинга данных.

```kotlin
// ✅ Хорошо: увеличиваем размер кэша
recyclerView.setItemViewCacheSize(20) // default = 2

// Правило: кэшируем 2-3 экрана
val itemsPerScreen = 10
recyclerView.setItemViewCacheSize(itemsPerScreen * 2)
```

### 2. Предзагрузка через LinearLayoutManager

```kotlin
val layoutManager = LinearLayoutManager(context).apply {
    isItemPrefetchEnabled = true        // default = true
    initialPrefetchItemCount = 4        // prefetch при первой загрузке
}
recyclerView.layoutManager = layoutManager
```

### 3. Загрузка данных через OnScrollListener

```kotlin
recyclerView.addOnScrollListener(object : RecyclerView.OnScrollListener() {
    override fun onScrolled(recyclerView: RecyclerView, dx: Int, dy: Int) {
        val layoutManager = recyclerView.layoutManager as LinearLayoutManager
        val visibleCount = layoutManager.childCount
        val totalCount = layoutManager.itemCount
        val firstVisible = layoutManager.findFirstVisibleItemPosition()

        // Загружаем за 5 элементов до конца
        if (!isLoading && (visibleCount + firstVisible + 5) >= totalCount) {
            loadMoreData()
        }
    }
})
```

### 4. Кастомный LayoutManager для продвинутой предзагрузки

```kotlin
class PrefetchLayoutManager(
    context: Context,
    private val prefetchCount: Int = 10
) : LinearLayoutManager(context) {

    override fun collectAdjacentPrefetchPositions(
        dx: Int, dy: Int,
        state: RecyclerView.State,
        registry: LayoutPrefetchRegistry
    ) {
        super.collectAdjacentPrefetchPositions(dx, dy, state, registry)

        val scrollingDown = dy > 0
        val lastVisible = findLastVisibleItemPosition()

        if (scrollingDown) {
            val endPos = minOf(lastVisible + prefetchCount, state.itemCount)
            for (i in lastVisible + 1 until endPos) {
                registry.addPosition(i, 0)
            }
        }
    }
}
```

### 5. Предзагрузка изображений (Glide/Coil)

```kotlin
// ✅ Хорошо: предзагружаем следующие изображения
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    holder.bind(items[position])

    // Prefetch next 5 images
    for (i in position + 1 until minOf(position + 6, items.size)) {
        Glide.with(context).load(items[i].imageUrl).preload()
    }
}
```

### 6. SharedPool для вложенных RecyclerView

```kotlin
private val sharedPool = RecyclerView.RecycledViewPool().apply {
    setMaxRecycledViews(0, 20)
}

override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    holder.nestedRecyclerView.apply {
        setRecycledViewPool(sharedPool)
        setItemViewCacheSize(10)
    }
}
```

### Полная оптимизация

```kotlin
fun setupOptimizedRecyclerView(recyclerView: RecyclerView) {
    // View caching
    recyclerView.setItemViewCacheSize(20)

    // Prefetching
    recyclerView.layoutManager = LinearLayoutManager(context).apply {
        isItemPrefetchEnabled = true
        initialPrefetchItemCount = 6
    }

    // ViewPool
    recyclerView.recycledViewPool.setMaxRecycledViews(0, 30)

    // Optimizations
    recyclerView.setHasFixedSize(true)
}
```

### Best Practices

✅ **setItemViewCacheSize(20-30)** для плавного скроллинга
✅ **isItemPrefetchEnabled = true** для автоматической предзагрузки
✅ **OnScrollListener** для загрузки данных заранее
✅ **SharedPool** для вложенных списков
✅ **Preload images** через Glide/Coil

❌ Не устанавливайте слишком большой cache size (>50) - расход памяти
❌ Не забывайте про pagination - загружайте данные порциями

---

## Answer (EN)

RecyclerView provides several mechanisms for caching items ahead to improve scrolling performance.

### 1. View Caching via setItemViewCacheSize()

The view cache stores recently off-screen views without rebinding data.

```kotlin
// ✅ Good: increase cache size
recyclerView.setItemViewCacheSize(20) // default = 2

// Rule: cache 2-3 screens worth
val itemsPerScreen = 10
recyclerView.setItemViewCacheSize(itemsPerScreen * 2)
```

### 2. Prefetching with LinearLayoutManager

```kotlin
val layoutManager = LinearLayoutManager(context).apply {
    isItemPrefetchEnabled = true        // default = true
    initialPrefetchItemCount = 4        // prefetch on initial load
}
recyclerView.layoutManager = layoutManager
```

### 3. Data Loading via OnScrollListener

```kotlin
recyclerView.addOnScrollListener(object : RecyclerView.OnScrollListener() {
    override fun onScrolled(recyclerView: RecyclerView, dx: Int, dy: Int) {
        val layoutManager = recyclerView.layoutManager as LinearLayoutManager
        val visibleCount = layoutManager.childCount
        val totalCount = layoutManager.itemCount
        val firstVisible = layoutManager.findFirstVisibleItemPosition()

        // Load 5 items before end
        if (!isLoading && (visibleCount + firstVisible + 5) >= totalCount) {
            loadMoreData()
        }
    }
})
```

### 4. Custom LayoutManager for Advanced Prefetching

```kotlin
class PrefetchLayoutManager(
    context: Context,
    private val prefetchCount: Int = 10
) : LinearLayoutManager(context) {

    override fun collectAdjacentPrefetchPositions(
        dx: Int, dy: Int,
        state: RecyclerView.State,
        registry: LayoutPrefetchRegistry
    ) {
        super.collectAdjacentPrefetchPositions(dx, dy, state, registry)

        val scrollingDown = dy > 0
        val lastVisible = findLastVisibleItemPosition()

        if (scrollingDown) {
            val endPos = minOf(lastVisible + prefetchCount, state.itemCount)
            for (i in lastVisible + 1 until endPos) {
                registry.addPosition(i, 0)
            }
        }
    }
}
```

### 5. Image Prefetching (Glide/Coil)

```kotlin
// ✅ Good: prefetch next images
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    holder.bind(items[position])

    // Prefetch next 5 images
    for (i in position + 1 until minOf(position + 6, items.size)) {
        Glide.with(context).load(items[i].imageUrl).preload()
    }
}
```

### 6. SharedPool for Nested RecyclerViews

```kotlin
private val sharedPool = RecyclerView.RecycledViewPool().apply {
    setMaxRecycledViews(0, 20)
}

override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    holder.nestedRecyclerView.apply {
        setRecycledViewPool(sharedPool)
        setItemViewCacheSize(10)
    }
}
```

### Complete Optimization

```kotlin
fun setupOptimizedRecyclerView(recyclerView: RecyclerView) {
    // View caching
    recyclerView.setItemViewCacheSize(20)

    // Prefetching
    recyclerView.layoutManager = LinearLayoutManager(context).apply {
        isItemPrefetchEnabled = true
        initialPrefetchItemCount = 6
    }

    // ViewPool
    recyclerView.recycledViewPool.setMaxRecycledViews(0, 30)

    // Optimizations
    recyclerView.setHasFixedSize(true)
}
```

### Best Practices

✅ **setItemViewCacheSize(20-30)** for smooth scrolling
✅ **isItemPrefetchEnabled = true** for automatic prefetching
✅ **OnScrollListener** for proactive data loading
✅ **SharedPool** for nested lists
✅ **Preload images** via Glide/Coil

❌ Don't set cache size too large (>50) - memory overhead
❌ Don't forget pagination - load data in chunks

---

## Follow-ups

- How does RecyclerView's view recycling work internally?
- What's the difference between ViewCache and RecycledViewPool?
- When should you use DiffUtil vs AsyncListDiffer?
- How to measure cache hit rate in production?
- What's the performance impact of nested RecyclerViews?

---

## References

- [[q-recyclerview-sethasfixedsize--android--easy]]
- [[q-recyclerview-async-list-differ--android--medium]]
- [[q-how-animations-work-in-recyclerview--android--medium]]

---

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - Fixed size optimization
- [[q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy]] - Layout basics

### Related (Same Level)
- [[q-how-animations-work-in-recyclerview--android--medium]] - Animation optimization
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - Advanced decoration
- [[q-recyclerview-async-list-differ--android--medium]] - Async updates
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Compose alternative

### Advanced (Harder)
- Custom layout managers for complex scrolling patterns
- Profiling RecyclerView performance with systrace
- Memory optimization strategies for large lists
