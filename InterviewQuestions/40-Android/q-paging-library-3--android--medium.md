---
id: android-409
title: Paging Library 3 / Библиотека Paging 3
aliases: [Android Paging, Paging 3, Paging Library 3, Библиотека Paging 3]
topic: android
subtopics: [architecture-clean, performance-rendering, room]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-recyclerview, c-room, c-viewmodel]
created: 2025-10-15
updated: 2025-10-30
tags: [android/architecture-clean, android/performance-rendering, android/room, difficulty/medium, jetpack, pagination, paging, recyclerview]
sources: [https://github.com/Kirchhoff-/Android-Interview-Questions]
---

# Вопрос (RU)

> Что вы знаете о библиотеке Paging?

# Question (EN)

> What do you know about the Paging Library?

---

## Ответ (RU)

**Библиотека Paging** помогает загружать и отображать данные порционно, снижая нагрузку на сеть и системные ресурсы.

### Архитектура Данных

Библиотека поддерживает три подхода:
- **Network-only**: прямая загрузка с сервера в UI
- **Database-only**: данные только из локальной БД
- **Network + Database**: сервер → Room → UI (кэширование)

### Ключевые Компоненты Paging 3

**PagingSource**: источник данных с поддержкой инкрементальной загрузки

```kotlin
class ConcertPagingSource(
    private val api: ConcertApi
) : PagingSource<Int, Concert>() {
    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, Concert> {
        val page = params.key ?: 0
        return try {
            val response = api.getConcerts(page, params.loadSize)
            LoadResult.Page(
                data = response.concerts,
                prevKey = if (page > 0) page - 1 else null,
                nextKey = if (response.hasMore) page + 1 else null
            )
        } catch (e: Exception) {
            LoadResult.Error(e)
        }
    }
}
```

✅ **Best Practice**: используйте `RemoteMediator` для network + database архитектуры

**Pager**: конфигурация и создание Flow

```kotlin
class ConcertViewModel(private val dao: ConcertDao) : ViewModel() {
    val concerts: Flow<PagingData<Concert>> = Pager(
        config = PagingConfig(pageSize = 20, prefetchDistance = 5),
        pagingSourceFactory = { dao.pagingSource() }
    ).flow.cachedIn(viewModelScope)
}
```

**PagingDataAdapter**: адаптер для RecyclerView

```kotlin
class ConcertAdapter : PagingDataAdapter<Concert, ConcertViewHolder>(DIFF_CALLBACK) {
    override fun onBindViewHolder(holder: ConcertViewHolder, position: Int) {
        getItem(position)?.let { holder.bind(it) }
    }

    companion object {
        private val DIFF_CALLBACK = object : DiffUtil.ItemCallback<Concert>() {
            override fun areItemsTheSame(old: Concert, new: Concert) =
                old.id == new.id
            override fun areContentsTheSame(old: Concert, new: Concert) =
                old == new
        }
    }
}
```

### Room Интеграция

```kotlin
@Dao
interface ConcertDao {
    @Query("SELECT * FROM concerts ORDER BY date DESC")
    fun pagingSource(): PagingSource<Int, Concert>
}
```

✅ Room автоматически генерирует `PagingSource` для запросов

### Обработка Состояний Загрузки

```kotlin
adapter.addLoadStateListener { loadState ->
    when (loadState.refresh) {
        is LoadState.Loading -> showProgress()
        is LoadState.Error -> showError((loadState.refresh as LoadState.Error).error)
        is LoadState.NotLoading -> hideProgress()
    }
}
```

### Преимущества

- **Автоматическая дедупликация запросов**: предотвращает дублирование загрузок
- **Встроенное кэширование**: эффективное использование памяти
- **Retry/Refresh API**: встроенная обработка ошибок
- **Prefetching**: предзагрузка данных до прокрутки
- **Kotlin Flow/LiveData**: нативная поддержка реактивности

❌ **Anti-pattern**: загрузка всех данных сразу без пагинации

## Answer (EN)

The **Paging Library** helps load and display data in chunks, reducing network and system resource usage.

### Data Architecture

The library supports three approaches:
- **Network-only**: direct loading from server to UI
- **Database-only**: data only from local DB
- **Network + Database**: server → Room → UI (caching)

### Core Paging 3 Components

**PagingSource**: data source with incremental loading support

```kotlin
class ConcertPagingSource(
    private val api: ConcertApi
) : PagingSource<Int, Concert>() {
    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, Concert> {
        val page = params.key ?: 0
        return try {
            val response = api.getConcerts(page, params.loadSize)
            LoadResult.Page(
                data = response.concerts,
                prevKey = if (page > 0) page - 1 else null,
                nextKey = if (response.hasMore) page + 1 else null
            )
        } catch (e: Exception) {
            LoadResult.Error(e)
        }
    }
}
```

✅ **Best Practice**: use `RemoteMediator` for network + database architecture

**Pager**: configuration and Flow creation

```kotlin
class ConcertViewModel(private val dao: ConcertDao) : ViewModel() {
    val concerts: Flow<PagingData<Concert>> = Pager(
        config = PagingConfig(pageSize = 20, prefetchDistance = 5),
        pagingSourceFactory = { dao.pagingSource() }
    ).flow.cachedIn(viewModelScope)
}
```

**PagingDataAdapter**: RecyclerView adapter

```kotlin
class ConcertAdapter : PagingDataAdapter<Concert, ConcertViewHolder>(DIFF_CALLBACK) {
    override fun onBindViewHolder(holder: ConcertViewHolder, position: Int) {
        getItem(position)?.let { holder.bind(it) }
    }

    companion object {
        private val DIFF_CALLBACK = object : DiffUtil.ItemCallback<Concert>() {
            override fun areItemsTheSame(old: Concert, new: Concert) =
                old.id == new.id
            override fun areContentsTheSame(old: Concert, new: Concert) =
                old == new
        }
    }
}
```

### Room Integration

```kotlin
@Dao
interface ConcertDao {
    @Query("SELECT * FROM concerts ORDER BY date DESC")
    fun pagingSource(): PagingSource<Int, Concert>
}
```

✅ Room automatically generates `PagingSource` for queries

### Load State Handling

```kotlin
adapter.addLoadStateListener { loadState ->
    when (loadState.refresh) {
        is LoadState.Loading -> showProgress()
        is LoadState.Error -> showError((loadState.refresh as LoadState.Error).error)
        is LoadState.NotLoading -> hideProgress()
    }
}
```

### Benefits

- **Automatic request deduplication**: prevents duplicate loads
- **Built-in caching**: efficient memory usage
- **Retry/Refresh API**: built-in error handling
- **Prefetching**: data preloading before scrolling
- **Kotlin Flow/LiveData**: native reactivity support

❌ **Anti-pattern**: loading all data at once without pagination

---

## Follow-ups

- How does `RemoteMediator` coordinate network and database sources?
- What's the difference between `refresh`, `prepend`, and `append` load types?
- How to implement custom retry logic for failed page loads?
- What are the memory implications of `cachedIn()` vs uncached Flow?
- How to handle deletions and insertions in paginated lists?

## References

- [[c-recyclerview]]
- [[c-room]]
- [[c-viewmodel]]
- [Paging Library Overview](https://developer.android.com/topic/libraries/architecture/paging)
- [Paging 3 Migration Guide](https://developer.android.com/topic/libraries/architecture/paging/v3-migration)

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-basics--android--easy]]
- [[q-room-basics--android--easy]]

### Related (Same Level)
- [[q-recyclerview-optimization--android--medium]]
- [[q-room-migration--android--medium]]
- [[q-sharedflow-stateflow--kotlin--medium]]

### Advanced (Harder)
- [[q-remotemediator-implementation--android--hard]]
- [[q-custom-paging-source--android--hard]]
