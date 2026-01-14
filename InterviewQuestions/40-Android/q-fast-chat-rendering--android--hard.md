---
id: android-474
title: Fast Chat Rendering / Быстрый рендеринг чата
aliases:
- Fast Chat Rendering
- Быстрый рендеринг чата
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
status: draft
moc: moc-android
related:
- c-compose-recomposition
- c-perfetto
- c-performance-optimization
- c-power-profiling
- c-recomposition
- c-recyclerview
- q-compose-compiler-plugin--android--hard
- q-diffutil-background-calculation-issues--android--medium
- q-list-elements-problems--android--medium
- q-why-diffutil-needed--android--medium
sources:
- https://developer.android.com/jetpack/compose/performance
- https://developer.android.com/topic/libraries/architecture/paging/v3-overview
- https://developer.android.com/topic/performance/rendering
anki_cards:
- slug: android-474-0-en
  language: en
  anki_id: 1768367872383
  synced_at: '2026-01-14T09:17:53.867695'
- slug: android-474-0-ru
  language: ru
  anki_id: 1768367872406
  synced_at: '2026-01-14T09:17:53.870275'
created: 2025-10-20
updated: 2025-11-03
tags:
- android/performance-memory
- android/ui-compose
- android/ui-views
- chat
- difficulty/hard
- diffutil
- paging
- performance
- recyclerview
---
# Вопрос (RU)
> Как оптимизировать рендеринг чатов для высокой производительности?

# Question (EN)
> How can you optimize chat rendering for high performance?

---

## Ответ (RU)

Цель — минимизировать лишние перерисовки, аллокации и тяжелые операции на главном потоке при работе со списком сообщений. Ключевые направления: UI списков (`RecyclerView`/`LazyColumn`), загрузка данных (`Paging 3`), изображения (`Glide`/`Coil`), и кэш (`Room`).

### XML Views: `RecyclerView` + `DiffUtil`

Используем `ListAdapter`/`AsyncListDiffer` с корректной реализацией `DiffUtil.ItemCallback`, чтобы пересоздавать только изменившиеся элементы.

```kotlin
class ChatDiff : DiffUtil.ItemCallback<Msg>() {
  override fun areItemsTheSame(o: Msg, n: Msg): Boolean = o.id == n.id

  override fun areContentsTheSame(o: Msg, n: Msg): Boolean =
    o == n // или сравниваем поля, влияющие на UI

  override fun getChangePayload(o: Msg, n: Msg): Any? = when {
    o.status != n.status -> StatusChangedPayload(n.status)
    o.text != n.text -> TextChangedPayload(n.text)
    else -> null
  }
}
```

В `onBindViewHolder` обрабатывайте payload'ы, чтобы избегать полной перерисовки, когда меняется только статус/прочее поле.

### Paging 3

Загружаем сообщения постепенно, чтобы не держать и не отрисовывать сразу тысячи элементов.

```kotlin
fun messages(): Flow<PagingData<Msg>> = Pager(
  PagingConfig(
    pageSize = 50,
    prefetchDistance = 10,
    enablePlaceholders = false
  )
) { ChatPagingSource(db) }.flow
```

Paging 3 обеспечивает поэтапную подгрузку, уменьшает пиковые аллокации и дает контроль над IO через конфигурацию и `RemoteMediator`.

### Compose: `LazyColumn` Со Стабильными Ключами

Используйте стабильные ключи, чтобы `LazyColumn` правильно переиспользовал элементы и не терял состояние.

```kotlin
@Composable
fun Chat(messages: List<Msg>) {
  LazyColumn(
    reverseLayout = true
  ) {
    items(
      items = messages,
      key = { it.id },
      contentType = { it.contentType } // помогает оптимизации
    ) { m ->
      MessageItem(m)
    }
  }
}
```

Убедитесь, что `MessageItem` не делает тяжелых вычислений на каждую композицию и не создает ненужных объектов в `@Composable` без `remember`.

### Compose: `derivedStateOf` Для Дорогих Вычислений

Дорогие вычисления (например, форматирование дат, вычисление группировки) выносите за пределы элементарных композаблов или мемоизируйте.

```kotlin
val sorted by remember(messages) {
  derivedStateOf {
    messages.sortedByDescending { it.ts }
  }
}
```

Используйте такой подход только если сортировка действительно должна происходить на клиенте и входные данные меняются не на каждую мелкую перерисовку; в противном случае сортировку лучше делать на уровне данных/репозитория.

### Изображения (Coil)

```kotlin
@Composable
fun ChatImage(url: String) {
  AsyncImage(
    model = url,
    contentDescription = null
  )
}
```

Настройте Coil/Glide для ресайза и кэширования изображений (memory/disk cache), чтобы не грузить слишком большие битмапы в чат-списке.

### Лучшие Практики
- Частичные обновления (`DiffUtil` payloads), корректные `areItemsTheSame`/`areContentsTheSame`.
- Стабильные ключи и `contentType` в `LazyColumn` для сохранения состояния и эффективного переиспользования.
- `Paging 3` для постепенной подгрузки длинной истории сообщений, уменьшения пиковых аллокаций и контролируемого IO.
- Кэш изображений (память/диск), ограничение размеров загружаемых изображений.
- Кэш сообщений в `Room`, индексы по `timestamp` (и по полям фильтрации/поиска) для быстрых запросов.

### Типичные Ошибки
- Полная перерисовка `ViewHolder` без обработки payload'ов.
- Отсутствие ключей/нестабильные ключи в `LazyColumn` → лишние рекомпозиции и потеря состояния элементов.
- Большие изображения без ресайза, отсутствие кэша → утечки памяти и OOM.
- Тяжелые вычисления в `@Composable` (парсинг, сортировка, форматирование) без `remember`/`derivedStateOf` или вынесения в слой данных.

## Answer (EN)

The goal is to minimize unnecessary redraws, allocations, and heavy work on the main thread when rendering message lists. Focus on list UI (`RecyclerView`/`LazyColumn`), data loading (`Paging 3`), images (`Glide`/`Coil`), and caching (`Room`).

### XML Views: `RecyclerView` + `DiffUtil`

Use `ListAdapter`/`AsyncListDiffer` with a correct `DiffUtil.ItemCallback` so only changed items are updated.

```kotlin
class ChatDiff : DiffUtil.ItemCallback<Msg>() {
  override fun areItemsTheSame(o: Msg, n: Msg): Boolean = o.id == n.id

  override fun areContentsTheSame(o: Msg, n: Msg): Boolean =
    o == n // or compare only fields that affect the UI

  override fun getChangePayload(o: Msg, n: Msg): Any? = when {
    o.status != n.status -> StatusChangedPayload(n.status)
    o.text != n.text -> TextChangedPayload(n.text)
    else -> null
  }
}
```

Handle payloads in `onBindViewHolder` to avoid full rebinds when only a specific field (e.g., status) changes.

### Paging 3

Load messages incrementally instead of keeping and rendering thousands of items at once.

```kotlin
fun messages(): Flow<PagingData<Msg>> = Pager(
  PagingConfig(
    pageSize = 50,
    prefetchDistance = 10,
    enablePlaceholders = false
  )
) { ChatPagingSource(db) }.flow
```

Paging 3 provides staged loading, reduces peak allocations, and gives control over IO via configuration and `RemoteMediator`.

### Compose: `LazyColumn` with Stable Keys

Use stable keys so `LazyColumn` can reuse items efficiently and preserve item state.

```kotlin
@Composable
fun Chat(messages: List<Msg>) {
  LazyColumn(
    reverseLayout = true
  ) {
    items(
      items = messages,
      key = { it.id },
      contentType = { it.contentType } // helps performance
    ) { m ->
      MessageItem(m)
    }
  }
}
```

Ensure `MessageItem` does not perform heavy work per composition and avoids unnecessary allocations without `remember`.

### Compose: `derivedStateOf` for Expensive Work

Move expensive computations (e.g., date formatting, grouping) out of leaf composables or memoize them.

```kotlin
val sorted by remember(messages) {
  derivedStateOf {
    messages.sortedByDescending { it.ts }
  }
}
```

Use this pattern only if sorting must happen on the client and the input list changes at meaningful intervals; otherwise prefer sorting in the data/repository layer.

### Images (Coil)

```kotlin
@Composable
fun ChatImage(url: String) {
  AsyncImage(
    model = url,
    contentDescription = null
  )
}
```

Configure Coil/Glide to resize and cache chat images (memory/disk) to avoid loading overly large bitmaps in the scrolling list.

### Best Practices
- Partial updates via `DiffUtil` payloads; correct `areItemsTheSame`/`areContentsTheSame` implementations.
- Stable keys and `contentType` in `LazyColumn` for state preservation and efficient reuse.
- Use `Paging 3` for long histories to reduce peak memory usage and control IO through incremental loading.
- Use image caches (memory/disk) and enforce size limits on images.
- Use `Room` to cache messages; add indexes on `timestamp` (and filter/search fields) for fast queries.

### Common Pitfalls
- Full `ViewHolder` redraw without handling payloads.
- Missing/unstable keys in `LazyColumn` → extra recompositions and lost item state.
- Large images without resize and missing cache → memory pressure and OOM.
- Heavy work inside `@Composable` (parsing, sorting, formatting) without `remember`/`derivedStateOf` or moving it to the data layer.
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
