---
id: android-314
title: How To Write Recyclerview Cache Ahead / Как написать RecyclerView с кешированием вперед
aliases: [RecyclerView Cache Ahead, RecyclerView Prefetching, Кеширование RecyclerView, Предзагрузка RecyclerView]
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
  - q-cache-implementation-strategies--android--medium
  - q-how-animations-work-in-recyclerview--android--medium
  - q-how-to-change-number-of-columns-in-recyclerview-based-on-orientation--android--easy
  - q-how-to-write-recyclerview-so-that-it-caches-ahead--android--medium
  - q-recyclerview-async-list-differ--android--medium
  - q-recyclerview-sethasfixedsize--android--easy
sources: []
created: 2025-10-15
updated: 2025-11-11
tags: [android/cache-offline, android/performance-rendering, android/ui-views, difficulty/medium, optimization, prefetching, recyclerview]
date created: Saturday, November 1st 2025, 12:46:54 pm
date modified: Tuesday, November 25th 2025, 8:53:59 pm
---
# Вопрос (RU)

> Как настроить RecyclerView для кеширования и предзагрузки элементов (cache/prefetch ahead)?

# Question (EN)

> How to configure RecyclerView to cache and prefetch items ahead?

---

## Ответ (RU)

RecyclerView предоставляет несколько механизмов для предзагрузки и кеширования элементов вперед (уменьшения работы при появлении следующих элементов на экране):

**1. setItemViewCacheSize() - кеш view (view cache)**

```kotlin
recyclerView.setItemViewCacheSize(20) // Default: 2
```

Сохраняет недавно ушедшие с экрана ViewHolder'ы в отсоединенном, но уже связанном (bound) состоянии, чтобы при повторном появлении их не приходилось пересоздавать или заново искать view. Это не выполняет асинхронную предзагрузку данных, а лишь уменьшает объем работы при повторном показе.

Важно: слишком большое значение увеличивает потребление памяти и может ухудшить производительность — подбирайте его на основе профилирования.

**2. Prefetching через LinearLayoutManager**

```kotlin
val layoutManager = LinearLayoutManager(context).apply {
    isItemPrefetchEnabled = true // ✅ Default: true
    initialPrefetchItemCount = 6  // Для вложенных RecyclerView: предзагрузка первых N элементов
}
recyclerView.layoutManager = layoutManager
```

`isItemPrefetchEnabled` включает layout prefetch (по умолчанию включен).
`initialPrefetchItemCount` используется в основном, когда этот LayoutManager вложен внутри другого скроллируемого контейнера (например, горизонтальный список внутри вертикального), чтобы заранее подготовить несколько child-элементов. Для обычного "топ-левел" RecyclerView этот параметр не управляет сетевой/дата-предзагрузкой и не заменяет собственную логику пагинации.

**3. OnScrollListener для предзагрузки данных (data prefetch)**

```kotlin
recyclerView.addOnScrollListener(object : RecyclerView.OnScrollListener() {
    override fun onScrolled(recyclerView: RecyclerView, dx: Int, dy: Int) {
        val visibleItemCount = layoutManager.childCount
        val totalItemCount = layoutManager.itemCount
        val firstVisibleItem = layoutManager.findFirstVisibleItemPosition()

        val threshold = 5
        if (!isLoading && (visibleItemCount + firstVisibleItem + threshold) >= totalItemCount) {
            loadMoreData() // Загрузка следующей страницы / fetch next page
        }
    }
})
```

Этот подход управляет именно предзагрузкой данных (пагинацией, сетевыми запросами), а не только переиспользованием view. Порог (threshold) подбирается эмпирически.

**4. Кастомный LayoutManager для точного контроля prefetch**

```kotlin
class CustomPrefetchLayoutManager(context: Context) : LinearLayoutManager(context) {

    override fun collectAdjacentPrefetchPositions(
        dx: Int,
        dy: Int,
        state: RecyclerView.State,
        layoutPrefetchRegistry: LayoutPrefetchRegistry
    ) {
        super.collectAdjacentPrefetchPositions(dx, dy, state, layoutPrefetchRegistry)

        val scrollingDown = dy > 0
        val lastVisible = findLastVisibleItemPosition()
        val itemCount = state.itemCount

        if (scrollingDown && lastVisible != RecyclerView.NO_POSITION) {
            val startPos = lastVisible + 1
            val endPosExclusive = minOf(startPos + 10, itemCount)
            for (i in startPos until endPosExclusive) {
                if (i in 0 until itemCount) {
                    layoutPrefetchRegistry.addPosition(i, 0) // ✅ Регистрация позиций для prefetch
                }
            }
        }
    }
}
```

Переопределяя `collectAdjacentPrefetchPositions`, можно явно указать, какие позиции нужно подготовить заранее. Важно не выходить за пределы `itemCount`.

**5. RecycledViewPool для вложенных RecyclerView**

```kotlin
val sharedPool = RecyclerView.RecycledViewPool().apply {
    setMaxRecycledViews(0, 20) // viewType, maxViews
}

// Использование в адаптере
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    holder.nestedRecyclerView.apply {
        setRecycledViewPool(sharedPool) // ✅ Переиспользование view pool между вложенными списками
        setItemViewCacheSize(10)
    }
}
```

Общий `RecycledViewPool` полезен для множества вложенных RecyclerView с одинаковыми viewType'ами (например, карусели в списке). Это уменьшает количество инфляций и создает эффект "cache ahead" на уровне переиспользуемых view. Для разных макетов или сильно различающихся списков общий пул может не дать эффекта или навредить.

**Лучшие практики** (ориентиры, требующие профилирования):
- увеличивать `setItemViewCacheSize()` только при наличии фризов из-за частого пересоздания view и с учетом памяти устройства;
- для вложенных RecyclerView `initialPrefetchItemCount` часто выбирают в диапазоне 4–6, чтобы элементы были готовы при скролле;
- использовать `OnScrollListener` (или Paging 3) для предзагрузки данных с порогом (например, 5–10 элементов) до конца списка;
- применять `RecycledViewPool` для вложенных списков с одинаковыми типами элементов.

## Answer (EN)

RecyclerView provides several mechanisms to prefetch and cache items ahead (reducing work before items appear on screen):

**1. setItemViewCacheSize() - view cache**

```kotlin
recyclerView.setItemViewCacheSize(20) // Default: 2
```

Keeps recently scrolled-off ViewHolders in a detached but bound state so they can be reused without full rebind/inflation when they come back. This does not perform asynchronous data prefetching; it optimizes view reuse.

Important: setting this too high increases memory usage and can hurt performance—tune it based on profiling.

**2. Prefetching with LinearLayoutManager**

```kotlin
val layoutManager = LinearLayoutManager(context).apply {
    isItemPrefetchEnabled = true // ✅ Default: true (layout prefetch)
    initialPrefetchItemCount = 6  // For nested RecyclerViews: prefetch first N child items
}
recyclerView.layoutManager = layoutManager
```

`isItemPrefetchEnabled` controls layout prefetching (enabled by default).
`initialPrefetchItemCount` is mainly effective when this LayoutManager is inside another scrolling container (e.g., horizontal RV inside vertical RV), so child views are prepared in advance. For a top-level list it does not replace proper data prefetching/paging.

**3. OnScrollListener for data prefetching**

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

This pattern handles data prefetching/pagination (network or DB), not just view reuse. Choose the threshold empirically.

**4. Custom LayoutManager for fine-grained prefetch**

```kotlin
class CustomPrefetchLayoutManager(context: Context) : LinearLayoutManager(context) {

    override fun collectAdjacentPrefetchPositions(
        dx: Int,
        dy: Int,
        state: RecyclerView.State,
        layoutPrefetchRegistry: LayoutPrefetchRegistry
    ) {
        super.collectAdjacentPrefetchPositions(dx, dy, state, layoutPrefetchRegistry)

        val scrollingDown = dy > 0
        val lastVisible = findLastVisibleItemPosition()
        val itemCount = state.itemCount

        if (scrollingDown && lastVisible != RecyclerView.NO_POSITION) {
            val startPos = lastVisible + 1
            val endPosExclusive = minOf(startPos + 10, itemCount)
            for (i in startPos until endPosExclusive) {
                if (i in 0 until itemCount) {
                    layoutPrefetchRegistry.addPosition(i, 0) // ✅ Register positions for prefetch
                }
            }
        }
    }
}
```

By overriding `collectAdjacentPrefetchPositions`, you can explicitly specify which positions should be prepared ahead of time. Ensure you never go beyond `itemCount`.

**5. RecycledViewPool for nested RecyclerViews**

```kotlin
val sharedPool = RecyclerView.RecycledViewPool().apply {
    setMaxRecycledViews(0, 20) // viewType, maxViews
}

// Usage in adapter
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    holder.nestedRecyclerView.apply {
        setRecycledViewPool(sharedPool) // ✅ Share pool between nested lists
        setItemViewCacheSize(10)
    }
}
```

A shared `RecycledViewPool` is beneficial when you have many nested RecyclerViews with the same view types (e.g., carousels in a feed). It reduces view inflation and contributes to "cache ahead" behavior at the view level. For heterogeneous layouts, a shared pool may not help.

**Best Practices** (guidelines; always validate with profiling):
- Increase `setItemViewCacheSize()` only when you see jank from frequent view recreation and have memory headroom.
- For nested RecyclerViews, `initialPrefetchItemCount` is often set around 4–6 to have items ready before they appear.
- Use an `OnScrollListener` (or Paging 3) for data prefetching with a threshold (e.g., 5–10 items) before the end.
- Use a shared `RecycledViewPool` for nested lists with matching view types.

---

## Дополнительные Вопросы (RU)

- В чем разница между кешем view и `RecycledViewPool`?
- Как предзагрузка влияет на потребление памяти?
- Когда использовать кастомный `LayoutManager` вместо `OnScrollListener`?
- Как измерять эффективность кеширования/предзагрузки в продакшене?

## Follow-ups

- What's the difference between view cache and RecycledViewPool?
- How does prefetching impact memory consumption?
- When to use custom LayoutManager vs OnScrollListener?
- How to measure cache hit rate in production?

## Ссылки (RU)

- [Руководство по оптимизации производительности RecyclerView](https://developer.android.com/develop/ui/views/layout/recyclerview)
- [Понимание кеширования в RecyclerView](https://proandroiddev.com/recyclerview-caching-8f3c5c6b4e92)

## References

- [RecyclerView Performance Best Practices](https://developer.android.com/develop/ui/views/layout/recyclerview)
- [Understanding RecyclerView Caching](https://proandroiddev.com/recyclerview-caching-8f3c5c6b4e92)

## Связанные Вопросы (RU)

### Предпосылки / Концепты

- [[c-database-design]]
- [[c-performance]]

### Предпосылки (проще)

- [[q-recyclerview-sethasfixedsize--android--easy]]
- [[q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy]]

### Похожие (средний уровень)

- [[q-recyclerview-async-list-differ--android--medium]]
- [[q-how-animations-work-in-recyclerview--android--medium]]
- [[q-recyclerview-itemdecoration-advanced--android--medium]]

### Продвинутое (сложнее)

- Продвинутая оптимизация RecyclerView с кастомным `ItemAnimator`
- Построение бесконечного скролла с предзагрузкой и обработкой ошибок

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
- Advanced RecyclerView optimization with custom ItemAnimator
- Building infinite scroll with prefetching and error handling
