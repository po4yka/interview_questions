---
id: android-409
title: Paging Library 3 / Библиотека Paging 3
aliases: [Android Paging, Paging 3, Paging Library 3, Библиотека Paging 3]
topic: android
subtopics: [architecture-clean, room]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-room, c-viewmodel]
created: 2025-10-15
updated: 2025-11-10
tags: [android/architecture-clean, android/room, difficulty/medium, jetpack, pagination, paging, recyclerview]
sources: ["https://github.com/Kirchhoff-/Android-Interview-Questions"]

---

# Вопрос (RU)

> Что вы знаете о библиотеке Paging?

# Question (EN)

> What do you know about the Paging Library?

## Ответ (RU)

**Библиотека Paging** помогает загружать и отображать данные порционно, снижая нагрузку на сеть и системные ресурсы.

### Архитектура Данных

Обычно используют три подхода (они не являются жёстким ограничением библиотеки):
- **Network-only**: прямая загрузка с сервера в UI
- **Database-only**: данные только из локальной БД
- **Network + Database**: сервер → Room → UI (кэширование через локальное хранилище)

### Ключевые Компоненты Paging 3

**PagingSource**: источник данных с поддержкой инкрементальной загрузки.

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
            return LoadResult.Error(e)
        }
    }

    override fun getRefreshKey(state: PagingState<Int, Concert>): Int? {
        // Пример простой реализации: выбрать ключ, ближайший к текущей позиции
        val anchorPosition = state.anchorPosition ?: return null
        val anchorPage = state.closestPageToPosition(anchorPosition)
        return anchorPage?.prevKey?.plus(1) ?: anchorPage?.nextKey?.minus(1)
    }
}
```

✅ **Best Practice**: используйте `RemoteMediator` для архитектуры network + database.

**Pager**: конфигурация и создание `Flow`.

```kotlin
class ConcertViewModel(private val dao: ConcertDao) : ViewModel() {
    val concerts: Flow<PagingData<Concert>> = Pager(
        config = PagingConfig(pageSize = 20, prefetchDistance = 5),
        pagingSourceFactory = { dao.pagingSource() }
    ).flow.cachedIn(viewModelScope)
}
```

**PagingDataAdapter**: адаптер для RecyclerView.

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

✅ Room автоматически генерирует реализацию `PagingSource` (или `PagingSource.Factory`) для таких запросов.

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

- **Автоматическая дедупликация запросов**: предотвращает дублирование загрузок.
- **Кэширование страниц в памяти** во время работы Paging-пайплайна; для долгоживущего кэша используйте подходы вроде `cachedIn` или локальную БД.
- **Retry/Refresh API**: встроенная поддержка повторных запросов и обновления данных.
- **Prefetching**: предзагрузка данных до прокрутки.
- **Поддержка Kotlin `Flow`/`LiveData`**: нативная реактивность.

❌ **Anti-pattern**: загрузка всех данных сразу без пагинации.

---

## Answer (EN)

The **Paging Library** helps load and display data in chunks, reducing network and system resource usage.

### Data Architecture

Commonly used patterns (not strict limitations of the library) are:
- **Network-only**: direct loading from server to UI
- **Database-only**: data only from local DB
- **Network + Database**: server → Room → UI (caching via local storage)

### Core Paging 3 Components

**PagingSource**: data source with incremental loading support.

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
            return LoadResult.Error(e)
        }
    }

    override fun getRefreshKey(state: PagingState<Int, Concert>): Int? {
        // Simple example: choose the key closest to the current position
        val anchorPosition = state.anchorPosition ?: return null
        val anchorPage = state.closestPageToPosition(anchorPosition)
        return anchorPage?.prevKey?.plus(1) ?: anchorPage?.nextKey?.minus(1)
    }
}
```

✅ **Best Practice**: use `RemoteMediator` for network + database architecture.

**Pager**: configuration and `Flow` creation.

```kotlin
class ConcertViewModel(private val dao: ConcertDao) : ViewModel() {
    val concerts: Flow<PagingData<Concert>> = Pager(
        config = PagingConfig(pageSize = 20, prefetchDistance = 5),
        pagingSourceFactory = { dao.pagingSource() }
    ).flow.cachedIn(viewModelScope)
}
```

**PagingDataAdapter**: RecyclerView adapter.

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

✅ Room automatically generates a `PagingSource` (or `PagingSource.Factory`) implementation for such queries.

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

- **Automatic request deduplication**: prevents duplicate loads.
- **In-memory page caching** while the Paging pipeline is active; for longer-lived caching use patterns like `cachedIn` or a local DB.
- **Retry/Refresh API**: built-in support for retrying failed loads and refreshing data.
- **Prefetching**: data preloading before scrolling.
- **Kotlin `Flow`/`LiveData`**: native reactivity support.

❌ **Anti-pattern**: loading all data at once without pagination.

---

## Дополнительные вопросы (RU)

- Как `RemoteMediator` координирует источники сети и базы данных?
- В чём разница между типами загрузки `refresh`, `prepend` и `append`?
- Каковы последствия для памяти при использовании `cachedIn()` по сравнению с не кэшированным `Flow`?

## Follow-ups (EN)

- How does `RemoteMediator` coordinate network and database sources?
- What's the difference between `refresh`, `prepend`, and `append` load types?

## References

- [[c-room]]
- [[c-viewmodel]]
- [Обзор Paging Library](https://developer.android.com/topic/libraries/architecture/paging)
- [Руководство по миграции на Paging 3](https://developer.android.com/topic/libraries/architecture/paging/v3-migration)
- [Paging Library Overview](https://developer.android.com/topic/libraries/architecture/paging)
- [Paging 3 Migration Guide](https://developer.android.com/topic/libraries/architecture/paging/v3-migration)

## Related Questions

### Предпосылки (проще)
- [[q-android-app-components--android--easy]]
- [[q-android-manifest-file--android--easy]]

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]]
- [[q-android-manifest-file--android--easy]]

### Связанные (такой же уровень)
- [[q-android-architectural-patterns--android--medium]]
- [[q-android-jetpack-overview--android--easy]]
- [[q-sharedflow-stateflow--kotlin--medium]]

### Related (Same Level)
- [[q-android-architectural-patterns--android--medium]]
- [[q-android-jetpack-overview--android--easy]]
- [[q-sharedflow-stateflow--kotlin--medium]]

### Продвинутые (сложнее)
- [[q-android-modularization--android--medium]]
- [[q-android-runtime-internals--android--hard]]

### Advanced (Harder)
- [[q-android-modularization--android--medium]]
- [[q-android-runtime-internals--android--hard]]
