---
id: android-409
anki_cards:
  - slug: android-409-0-en
    front: "What are the core components of Paging 3 library?"
    back: |
      **3 core components:**

      1. **PagingSource** - Loads data incrementally with `LoadResult.Page`
      2. **Pager** - Creates `Flow<PagingData<T>>` with config
      3. **PagingDataAdapter** - RecyclerView adapter with DiffUtil

      ```kotlin
      Pager(PagingConfig(pageSize = 20)) {
          dao.pagingSource()
      }.flow.cachedIn(viewModelScope)
      ```

      Use `RemoteMediator` for network + database.
    tags:
      - android_room
      - android_architecture
      - difficulty::medium
  - slug: android-409-0-ru
    front: "Какие основные компоненты библиотеки Paging 3?"
    back: |
      **3 основных компонента:**

      1. **PagingSource** - Загружает данные инкрементально через `LoadResult.Page`
      2. **Pager** - Создает `Flow<PagingData<T>>` с конфигурацией
      3. **PagingDataAdapter** - Адаптер RecyclerView с DiffUtil

      ```kotlin
      Pager(PagingConfig(pageSize = 20)) {
          dao.pagingSource()
      }.flow.cachedIn(viewModelScope)
      ```

      Используйте `RemoteMediator` для network + database.
    tags:
      - android_room
      - android_architecture
      - difficulty::medium
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

---\
# Вопрос (RU)

> Что вы знаете о библиотеке Paging?

# Question (EN)

> What do you know about the Paging Library?

## Ответ (RU)

**Библиотека Paging** помогает загружать и отображать данные порционно, снижая нагрузку на сеть и системные ресурсы.

### Архитектура Данных

Обычно используют три подхода (они не являются жёстким ограничением библиотеки):
- **Network-only**: прямая загрузка с сервера в UI
- **`Database`-only**: данные только из локальной БД
- **Network + `Database`**: сервер → `Room` → UI (кэширование через локальное хранилище)

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
            LoadResult.Error(e)
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

**PagingDataAdapter**: адаптер для `RecyclerView`.

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

✅ `Room` автоматически генерирует реализацию `PagingSource` для таких запросов; ключ используется для индексации страниц и управляется Paging.

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

- **Управление запросами и отсутствием дубликатов в рамках одного Paging-потока**: библиотека сериализует и координирует загрузки страниц, избегая лишних повторных вызовов для уже инициированных запросов.
- **Кэширование страниц в памяти** во время работы Paging-пайплайна; для долгоживущего кэша используйте такие подходы, как `cachedIn` или локальную БД.
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
- **`Database`-only**: data only from local DB
- **Network + `Database`**: server → `Room` → UI (caching via local storage)

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
            LoadResult.Error(e)
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

**PagingDataAdapter**: `RecyclerView` adapter.

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

✅ `Room` automatically generates a `PagingSource` implementation for such queries; the key type is used for page indexing and managed by the Paging library.

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

- **Managed requests without duplicate loads within a Paging stream**: the library serializes and coordinates page loads, so already requested pages aren't redundantly loaded.
- **In-memory page caching** while the Paging pipeline is active; for longer-lived caching use patterns like `cachedIn` or a local DB.
- **Retry/Refresh API**: built-in support for retrying failed loads and refreshing data.
- **Prefetching**: data preloading before scrolling.
- **Kotlin `Flow`/`LiveData`**: native reactivity support.

❌ **Anti-pattern**: loading all data at once without pagination.

---

## Дополнительные Вопросы (RU)

- Как `RemoteMediator` координирует источники сети и базы данных?
- В чём разница между типами загрузки `refresh`, `prepend` и `append`?
- Каковы последствия для памяти при использовании `cachedIn()` по сравнению с некэшированным `Flow`?

## Follow-ups (EN)

- How does `RemoteMediator` coordinate network and database sources?
- What's the difference between `refresh`, `prepend`, and `append` load types?
- What are the memory implications of using `cachedIn()` compared to a non-cached `Flow`?

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

### Связанные (такой Же уровень)
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
