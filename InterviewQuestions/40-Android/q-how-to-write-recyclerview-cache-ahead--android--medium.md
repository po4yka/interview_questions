---
id: android-314
title: How To Write Recyclerview Cache Ahead / Как написать RecyclerView с кешированием
  вперед
aliases:
- RecyclerView Cache Ahead
- RecyclerView Prefetching
- Кеширование RecyclerView
- Предзагрузка RecyclerView
topic: android
subtopics:
- cache-offline
- performance-rendering
- ui-views
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-database-design
- c-performance
- q-how-animations-work-in-recyclerview--android--medium
- q-recyclerview-async-list-differ--android--medium
- q-recyclerview-sethasfixedsize--android--easy
sources: []
created: 2025-10-15
updated: 2025-10-28
tags:
- android/cache-offline
- android/performance-rendering
- android/ui-views
- difficulty/medium
- optimization
- prefetching
- recyclerview
---

# Вопрос (RU)

> Как настроить `RecyclerView` для кеширования элементов вперед?

# Question (EN)

> How to configure `RecyclerView` to cache items ahead?

---

## Ответ (RU)

`RecyclerView` предоставляет несколько механизмов для кеширования элементов вперед:

**1. setItemViewCacheSize() - Кеш представлений**

```kotlin
recyclerView.setItemViewCacheSize(20) // Default: 2
```

Сохраняет недавно прокрученные view без ребиндинга данных.

**2. Prefetching через LinearLayoutManager**

```kotlin
val layoutManager = LinearLayoutManager(context).apply {
    isItemPrefetchEnabled = true // ✅ Default: true
    initialPrefetchItemCount = 6  // Prefetch первые N элементов
}
recyclerView.layoutManager = layoutManager
```

**3. OnScrollListener для предзагрузки данных**

```kotlin
recyclerView.addOnScrollListener(object : RecyclerView.OnScrollListener() {
    override fun onScrolled(recyclerView: RecyclerView, dx: Int, dy: Int) {
        val visibleItemCount = layoutManager.childCount
        val totalItemCount = layoutManager.itemCount
        val firstVisibleItem = layoutManager.findFirstVisibleItemPosition()

        val threshold = 5
        if (!isLoading && (visibleItemCount + firstVisibleItem + threshold) >= totalItemCount) {
            loadMoreData() // Загрузка следующей страницы
        }
    }
})
```

**4. Кастомный LayoutManager**

```kotlin
class CustomPrefetchLayoutManager(context: Context) : LinearLayoutManager(context) {

    override fun collectAdjacentPrefetchPositions(
        dx: Int, dy: Int,
        state: RecyclerView.State,
        layoutPrefetchRegistry: LayoutPrefetchRegistry
    ) {
        super.collectAdjacentPrefetchPositions(dx, dy, state, layoutPrefetchRegistry)

        val scrollingDown = dy > 0
        val lastVisible = findLastVisibleItemPosition()

        if (scrollingDown) {
            val startPos = lastVisible + 1
            val endPos = minOf(startPos + 10, state.itemCount)
            for (i in startPos until endPos) {
                layoutPrefetchRegistry.addPosition(i, 0) // ✅ Регистрация позиций для prefetch
            }
        }
    }
}
```

**5. RecycledViewPool для вложенных `RecyclerView`**

```kotlin
val sharedPool = RecyclerView.RecycledViewPool().apply {
    setMaxRecycledViews(0, 20) // viewType, maxViews
}

// Использование в адаптере
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    holder.nestedRecyclerView.apply {
        setRecycledViewPool(sharedPool) // ✅ Переиспользование view pool
        setItemViewCacheSize(10)
    }
}
```

**Рекомендации**:
- setItemViewCacheSize(20-30) для гладкой прокрутки
- initialPrefetchItemCount = 4-6 для вложенных `RecyclerView`
- OnScrollListener для пагинации с threshold = 5-10
- RecycledViewPool для вложенных списков

## Answer (EN)

`RecyclerView` provides several mechanisms for caching items ahead:

**1. setItemViewCacheSize() - `View` Cache**

```kotlin
recyclerView.setItemViewCacheSize(20) // Default: 2
```

Stores recently scrolled-off views without rebinding data.

**2. Prefetching with LinearLayoutManager**

```kotlin
val layoutManager = LinearLayoutManager(context).apply {
    isItemPrefetchEnabled = true // ✅ Default: true
    initialPrefetchItemCount = 6  // Prefetch first N items
}
recyclerView.layoutManager = layoutManager
```

**3. OnScrollListener for Data Prefetching**

```kotlin
recyclerView.addOnScrollListener(object : RecyclerView.OnScrollListener() {
    override fun onScrolled(recyclerView: RecyclerView, dx: Int, dy: Int) {
        val visibleItemCount = layoutManager.childCount
        val totalItemCount = layoutManager.itemCount
        val firstVisibleItem = layoutManager.findFirstVisibleItemPosition()

        val threshold = 5
        if (!isLoading && (visibleItemCount + firstVisibleItem + threshold) >= totalItemCount) {
            loadMoreData() // Load next page
        }
    }
})
```

**4. Custom LayoutManager**

```kotlin
class CustomPrefetchLayoutManager(context: Context) : LinearLayoutManager(context) {

    override fun collectAdjacentPrefetchPositions(
        dx: Int, dy: Int,
        state: RecyclerView.State,
        layoutPrefetchRegistry: LayoutPrefetchRegistry
    ) {
        super.collectAdjacentPrefetchPositions(dx, dy, state, layoutPrefetchRegistry)

        val scrollingDown = dy > 0
        val lastVisible = findLastVisibleItemPosition()

        if (scrollingDown) {
            val startPos = lastVisible + 1
            val endPos = minOf(startPos + 10, state.itemCount)
            for (i in startPos until endPos) {
                layoutPrefetchRegistry.addPosition(i, 0) // ✅ Register positions for prefetch
            }
        }
    }
}
```

**5. RecycledViewPool for Nested RecyclerViews**

```kotlin
val sharedPool = RecyclerView.RecycledViewPool().apply {
    setMaxRecycledViews(0, 20) // viewType, maxViews
}

// Usage in adapter
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    holder.nestedRecyclerView.apply {
        setRecycledViewPool(sharedPool) // ✅ Reuse view pool
        setItemViewCacheSize(10)
    }
}
```

**Best Practices**:
- setItemViewCacheSize(20-30) for smooth scrolling
- initialPrefetchItemCount = 4-6 for nested RecyclerViews
- OnScrollListener for pagination with threshold = 5-10
- RecycledViewPool for nested lists

---

## Follow-ups

- What's the difference between view cache and RecycledViewPool?
- How does prefetching impact memory consumption?
- When to use custom LayoutManager vs OnScrollListener?
- How to measure cache hit rate in production?

## References

- [`RecyclerView` Performance Best Practices](https://developer.android.com/develop/ui/views/layout/recyclerview)
- [Understanding `RecyclerView` Caching](https://proandroiddev.com/recyclerview-caching-8f3c5c6b4e92)

## Related Questions

### Prerequisites / Concepts

- [[c-database-design]]
- [[c-performance]]


### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]]
- [[q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy]]

### Related (Medium)
- [[q-recyclerview-async-list-differ--android--medium]]
- [[q-how-animations-work-in-recyclerview--android--medium]]
- [[q-recyclerview-itemdecoration-advanced--android--medium]]

### Advanced (Harder)
- Advanced `RecyclerView` optimization with custom ItemAnimator
- Building infinite scroll with prefetching and error handling
