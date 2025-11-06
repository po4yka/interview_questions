---
id: android-474
title: Fast Chat Rendering / Быстрый рендеринг чата
aliases: [Fast Chat Rendering, Быстрый рендеринг чата]
topic: android
subtopics:
  - performance-memory
  - ui-compose
  - ui-views
question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-performance-optimization
  - c-recyclerview
  - q-diffutil-background-calculation-issues--android--medium
sources:
  - https://developer.android.com/jetpack/compose/performance
  - https://developer.android.com/topic/libraries/architecture/paging/v3-overview
  - https://developer.android.com/topic/performance/rendering
created: 2025-10-20
updated: 2025-11-03
tags: [android/performance-memory, android/ui-compose, android/ui-views, chat, difficulty/hard, diffutil, paging, performance, recyclerview]
---

# Вопрос (RU)
> Как оптимизировать рендеринг чатов для высокой производительности?

# Question (EN)
> How can you optimize chat rendering for high performance?

---

## Ответ (RU)

Цель — минимизировать лишние перерисовки и аллокации при списках сообщений. Ключевые направления: UI списков (`RecyclerView`/`LazyColumn`), загрузка данных (`Paging 3`), изображения (`Glide`/`Coil`), и кэш (`Room`).

### XML Views: `RecyclerView` + `DiffUtil`

```kotlin
class ChatDiff : DiffUtil.ItemCallback<Msg>() {
  override fun areItemsTheSame(o: Msg, n: Msg) = o.id == n.id
  override fun getChangePayload(o: Msg, n: Msg): Any? = when {
    o.status != n.status -> n.status
    o.text != n.text -> n.text
    else -> null
  }
}
```

### Paging 3

```kotlin
fun messages(): Flow<PagingData<Msg>> = Pager(
  PagingConfig(pageSize = 50, prefetchDistance = 10)
) { ChatPagingSource(db) }.flow
```

### Compose: `LazyColumn` Со Стабильными Ключами

```kotlin
@Composable
fun Chat(messages: List<Msg>) {
  LazyColumn(reverseLayout = true) {
    items(items = messages, key = { it.id }) { m ->
      MessageItem(m)
    }
  }
}
```

### Compose: `derivedStateOf` Для Дорогих Вычислений

```kotlin
val sorted by remember(messages) { derivedStateOf { messages.sortedByDescending { it.ts } } }
```

### Изображения (Coil)

```kotlin
@Composable
fun ChatImage(url: String) { AsyncImage(model = url, contentDescription = null) }
```

### Лучшие Практики
- Частичные обновления (`DiffUtil` payloads), стабильные ключи в `LazyColumn`
- `Paging 3` + бэк‑давление, батчинг IO
- Кэш изображений (память/диск), ограничение размеров
- Кэш сообщений в `Room`, индексы по `timestamp`

### Типичные Ошибки
- Полная перерисовка `ViewHolder` без payloads
- Отсутствие ключей/нестабильные ключи → лишние recomposition
- Большие изображения без ресайза, отсутствие кеша
- Тяжелые вычисления в `@Composable` без `remember/derivedStateOf`


## Answer (EN)

Goal — minimize redundant redraws and allocations for message lists. Focus on list UI (`RecyclerView`/`LazyColumn`), data loading (`Paging 3`), images (`Glide`/`Coil`), and cache (`Room`).

### XML Views: `RecyclerView` + `DiffUtil`

```kotlin
class ChatDiff : DiffUtil.ItemCallback<Msg>() {
  override fun areItemsTheSame(o: Msg, n: Msg) = o.id == n.id
  override fun getChangePayload(o: Msg, n: Msg): Any? = when {
    o.status != n.status -> n.status
    o.text != n.text -> n.text
    else -> null
  }
}
```

### Paging 3

```kotlin
fun messages(): Flow<PagingData<Msg>> = Pager(
  PagingConfig(pageSize = 50, prefetchDistance = 10)
) { ChatPagingSource(db) }.flow
```

### Compose: `LazyColumn` with Stable Keys

```kotlin
@Composable
fun Chat(messages: List<Msg>) {
  LazyColumn(reverseLayout = true) {
    items(items = messages, key = { it.id }) { m ->
      MessageItem(m)
    }
  }
}
```

### Compose: `derivedStateOf` for Expensive Work

```kotlin
val sorted by remember(messages) { derivedStateOf { messages.sortedByDescending { it.ts } } }
```

### Images (Coil)

```kotlin
@Composable
fun ChatImage(url: String) { AsyncImage(model = url, contentDescription = null) }
```

### Best Practices
- Partial updates (`DiffUtil` payloads), stable keys in `LazyColumn`
- `Paging 3` + backpressure, IO batching
- Image caches (memory/disk), size constraints
- Message cache in `Room`, indexes on `timestamp`

### Common Pitfalls
- Full `ViewHolder` redraw without payloads
- Missing/unstable keys → extra recomposition
- Large images without resize, missing cache
- Heavy work inside `@Composable` without `remember/derivedStateOf`
---

## Follow-ups

- How to handle real-time message updates efficiently?
- What are the memory implications of caching thousands of messages?
- When should you use AsyncListDiffer vs ListAdapter?
- How to optimize chat with rich media (videos, GIFs)?
- What's the best strategy for bidirectional infinite scrolling?

## References

- [[c-performance-optimization]]
- [[c-recyclerview]]
- [[moc-android]]
- [Android Performance: Rendering](https://developer.android.com/topic/performance/rendering)
- [DiffUtil (AndroidX)](https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil)
- [Paging 3 Overview](https://developer.android.com/topic/libraries/architecture/paging/v3-overview)
- [Compose Performance](https://developer.android.com/jetpack/compose/performance)
- [Compose Lists](https://developer.android.com/jetpack/compose/lists)
- [Coil Compose Docs](https://coil-kt.github.io/coil/compose/)
- [Glide Docs](https://bumptech.github.io/glide/)
- [Room Persistence Library](https://developer.android.com/training/data-storage/room)

## Related Questions

### Prerequisites
- [[q-diffutil-background-calculation-issues--android--medium]]

### Same Level

### Advanced
