---
id: android-267
title: How To Write RecyclerView So That It Caches Ahead
aliases: [RecyclerView caching, RecyclerView prefetching, Кеширование RecyclerView, Предзагрузка RecyclerView]
topic: android
subtopics:
  - performance-memory
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
  - c-android-components
  - q-how-animations-work-in-recyclerview--android--medium
  - q-how-to-change-number-of-columns-in-recyclerview-based-on-orientation--android--easy
  - q-how-to-write-recyclerview-cache-ahead--android--medium
  - q-recyclerview-async-list-differ--android--medium
  - q-recyclerview-sethasfixedsize--android--easy
  - q-what-is-known-about-methods-that-redraw-view--android--medium
sources: []
created: 2025-10-15
updated: 2025-11-11
tags: [android, android/performance-memory, android/performance-rendering, android/ui-views, caching, difficulty/medium, prefetching, recyclerview]

date created: Saturday, November 1st 2025, 12:46:55 pm
date modified: Tuesday, November 25th 2025, 8:53:59 pm
---
# Вопрос (RU)

> Как можно писать RecyclerView, чтобы он кэшировал наперёд?

---

# Question (EN)

> How to write RecyclerView so that it caches ahead?

---

## Ответ (RU)

RecyclerView предоставляет несколько механизмов для кэширования и предзагрузки элементов, улучшая производительность скроллинга. Важно различать:
- кэширование view (повторное использование уже созданных и привязанных `View`),
- предзагрузку layout/bind (layout prefetch из `LayoutManager`),
- предзагрузку данных (pagination, предварительная загрузка контента).

### 1. Кэширование `View` Через `setItemViewCacheSize()`

Кэш хранит недавно скрытые `View` в привязанном состоянии (без повторного биндинга данных), чтобы ускорить повторное появление этих же позиций в пределах небольшого диапазона.

```kotlin
// ✅ Пример: увеличиваем размер кэша, если View дорогие
recyclerView.setItemViewCacheSize(20) // default = 2

// Вариант: кэшируем несколько экранов, если это оправдано по памяти
val itemsPerScreen = 10
recyclerView.setItemViewCacheSize(itemsPerScreen * 2)
```

Это не «загружает вперёд» новые элементы, а уменьшает количество пересозданий/ребиндинга для недавно использованных `View`. Слишком большой cache size увеличивает использование памяти и может навредить.

### 2. Предзагрузка Через `LinearLayoutManager`

```kotlin
val layoutManager = LinearLayoutManager(context).apply {
    isItemPrefetchEnabled = true        // default = true: включает layout prefetch
    initialPrefetchItemCount = 4        // сколько элементов предзагружать при первой прокрутке
}
recyclerView.layoutManager = layoutManager
```

`LayoutManager` с включённым item prefetch может заранее создавать и байндить `View` для позиций рядом с видимой областью, снижая jank при скролле.

### 3. Загрузка Данных Через `OnScrollListener` (или Paging library)

```kotlin
recyclerView.addOnScrollListener(object : RecyclerView.OnScrollListener() {
    override fun onScrolled(recyclerView: RecyclerView, dx: Int, dy: Int) {
        val layoutManager = recyclerView.layoutManager as LinearLayoutManager
        val visibleCount = layoutManager.childCount
        val totalCount = layoutManager.itemCount
        val firstVisible = layoutManager.findFirstVisibleItemPosition()

        // Загружаем новые данные заранее, за 5 элементов до конца
        if (!isLoading && (visibleCount + firstVisible + 5) >= totalCount) {
            loadMoreData()
        }
    }
})
```

Это предзагрузка данных (pagination), а не только кэширование `View`, и она должна учитывать состояние загрузки и возможный повторный вызов. В продакшене часто удобнее использовать paging library, чтобы получать автоматическое подгружание и кэширование страниц.

### 4. Кастомный `LayoutManager` Для Продвинутой Предзагрузки

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

        if (scrollingDown && lastVisible != RecyclerView.NO_POSITION) {
            val endPos = minOf(lastVisible + prefetchCount, state.itemCount)
            for (i in (lastVisible + 1) until endPos) {
                registry.addPosition(i, 0)
            }
        }
    }
}
```

Здесь явно предзагружаются позиции вперёд по направлению скролла. Аналогично можно добавить логику для скролла вверх.

### 5. Предзагрузка Изображений (Glide/Coil)

```kotlin
// Упрощённый пример: предзагружаем следующие изображения
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    holder.bind(items[position])

    // Prefetch next 5 images (следим, чтобы не создавать лишних запросов)
    val end = minOf(position + 6, items.size)
    for (i in position + 1 until end) {
        Glide.with(holder.itemView)
            .load(items[i].imageUrl)
            .preload()
    }
}
```

На практике стоит учитывать направление скролла, сетевые ограничения и уметь отменять больше не нужные запросы, чтобы не перегружать сеть и память.

### 6. `SharedPool` Для Вложенных `RecyclerView`

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

Общий пул уменьшает количество пересозданий `ViewHolder` во вложенных списках.

### Полная Оптимизация

```kotlin
fun setupOptimizedRecyclerView(recyclerView: RecyclerView, context: Context) {
    // View caching (тюним в зависимости от сложности layout и памяти)
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

✅ Аккуратно увеличивайте `setItemViewCacheSize(...)` только если `View` дорогие и хватает памяти
✅ Держите `isItemPrefetchEnabled = true` для автоматической предзагрузки layout/bind
✅ Используйте `OnScrollListener` (или paging library) для заблаговременной загрузки данных
✅ Используйте `SharedPool` для вложенных списков
✅ Предзагружайте изображения (Glide/Coil), контролируя объём, направление, сетевые ограничения и возможность отмены

❌ Не ставьте чрезмерный cache size (например, >50) без профилирования — риск утечек памяти и OOM
❌ Не забывайте про pagination — загружайте данные порциями и избегайте лишней предзагрузки

---

## Answer (EN)

RecyclerView provides several mechanisms for caching and prefetching items to improve scrolling performance. It is important to distinguish between:
- view caching (reusing already created and bound views),
- layout/bind prefetch (LayoutManager item prefetch),
- data preloading (pagination / fetching content ahead).

### 1. `View` Caching via `setItemViewCacheSize()`

The view cache keeps recently off-screen views in a bound state (no rebind) so they can quickly reappear when scrolled back within a small range.

```kotlin
// ✅ Example: increase cache size when item views are expensive
recyclerView.setItemViewCacheSize(20) // default = 2

// Option: cache multiple screens if it is justified for your layouts/memory
val itemsPerScreen = 10
recyclerView.setItemViewCacheSize(itemsPerScreen * 2)
```

This does not "prefetch" new items ahead; it reduces rebinding/recreation for recently used views. Oversized cache increases memory usage and can be harmful.

### 2. Prefetching with `LinearLayoutManager`

```kotlin
val layoutManager = LinearLayoutManager(context).apply {
    isItemPrefetchEnabled = true        // default = true: enables layout prefetch
    initialPrefetchItemCount = 4        // how many items to prefetch on initial scroll
}
recyclerView.layoutManager = layoutManager
```

With item prefetch enabled, the `LayoutManager` can pre-create and bind views for positions adjacent to the viewport to reduce jank.

### 3. Data Loading via `OnScrollListener` (or Paging library)

```kotlin
recyclerView.addOnScrollListener(object : RecyclerView.OnScrollListener() {
    override fun onScrolled(recyclerView: RecyclerView, dx: Int, dy: Int) {
        val layoutManager = recyclerView.layoutManager as LinearLayoutManager
        val visibleCount = layoutManager.childCount
        val totalCount = layoutManager.itemCount
        val firstVisible = layoutManager.findFirstVisibleItemPosition()

        // Load more data 5 items before the end
        if (!isLoading && (visibleCount + firstVisible + 5) >= totalCount) {
            loadMoreData()
        }
    }
})
```

This is data preloading (pagination), not just view caching. It should guard against duplicate calls and handle loading state correctly. In production, a paging library is often preferable, as it encapsulates prefetch thresholds, caching, and lifecycle-awareness.

### 4. Custom `LayoutManager` for Advanced Prefetching

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

        if (scrollingDown && lastVisible != RecyclerView.NO_POSITION) {
            val endPos = minOf(lastVisible + prefetchCount, state.itemCount)
            for (i in (lastVisible + 1) until endPos) {
                registry.addPosition(i, 0)
            }
        }
    }
}
```

This explicitly prefetches positions ahead in the scroll direction. Similar logic can be added for scrolling up.

### 5. Image Prefetching (Glide/Coil)

```kotlin
// Simplified example: prefetch next images
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    holder.bind(items[position])

    // Prefetch next 5 images (be careful to not over-fetch on fast scroll)
    val end = minOf(position + 6, items.size)
    for (i in position + 1 until end) {
        Glide.with(holder.itemView)
            .load(items[i].imageUrl)
            .preload()
    }
}
```

In real apps you should take scroll direction, network constraints, and cancellation into account to avoid unnecessary work.

### 6. `SharedPool` For Nested RecyclerViews

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

A shared pool reduces `ViewHolder` recreations across nested child `RecyclerView`s.

### Complete Optimization

```kotlin
fun setupOptimizedRecyclerView(recyclerView: RecyclerView, context: Context) {
    // View caching (tuned based on layout cost and memory)
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

✅ Carefully increase `setItemViewCacheSize(...)` only when item views are expensive and memory allows
✅ Keep `isItemPrefetchEnabled = true` for automatic layout/bind prefetching
✅ Use an `OnScrollListener` (or paging library) for proactive data loading
✅ Use a `SharedPool` for nested lists
✅ Preload images via Glide/Coil with proper limits, direction-awareness, and cancellation

❌ Don't set an excessively large cache size (e.g. >50) without profiling — risk of high memory usage / OOM
❌ Don't forget proper pagination — load data in chunks and avoid aggressive unnecessary prefetching

---

## Дополнительные Вопросы (RU)

- Как внутренне работает механизм ресайклинга `RecyclerView`?
- В чём разница между `ViewCache` и `RecycledViewPool`?
- Когда стоит использовать `DiffUtil` против `AsyncListDiffer`?
- Как измерять hit ratio кэша в продакшене?
- Как влияет на производительность использование вложенных `RecyclerView`?

---

## Follow-ups

- How does RecyclerView's view recycling work internally?
- What's the difference between ViewCache and RecycledViewPool?
- When should you use DiffUtil vs AsyncListDiffer?
- How to measure cache hit rate in production?
- What's the performance impact of nested RecyclerViews?

---

## Ссылки (RU)

- [[q-recyclerview-sethasfixedsize--android--easy]]
- [[q-recyclerview-async-list-differ--android--medium]]
- [[q-how-animations-work-in-recyclerview--android--medium]]

---

## References

- [[q-recyclerview-sethasfixedsize--android--easy]]
- [[q-recyclerview-async-list-differ--android--medium]]
- [[q-how-animations-work-in-recyclerview--android--medium]]

---

## Связанные Вопросы (RU)

### База / Концепты

- [[c-android-components]]

### Предпосылки (проще)

- [[q-recyclerview-sethasfixedsize--android--easy]]

### Похожие (тот Же уровень)

- [[q-how-animations-work-in-recyclerview--android--medium]]
- [[q-recyclerview-async-list-differ--android--medium]]

### Продвинутое

- Профилирование производительности `RecyclerView`

---

## Related Questions

### Prerequisites / Concepts

- [[c-android-components]]

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]]

### Related (Same Level)
- [[q-how-animations-work-in-recyclerview--android--medium]]
- [[q-recyclerview-async-list-differ--android--medium]]

### Advanced (Harder)
- Profiling RecyclerView performance with systrace
