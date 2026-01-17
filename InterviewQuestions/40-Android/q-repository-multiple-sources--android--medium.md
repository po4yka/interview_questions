---
id: android-030
title: Repository Pattern with Multiple Data Sources / Паттерн Repository с несколькими источниками данных
aliases: [Repository Pattern with Multiple Data Sources, Паттерн Repository с несколькими источниками данных]
topic: android
subtopics: [architecture-clean, cache-offline]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
source: "https://github.com/amitshekhariitbhu/android-interview-questions"
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority
status: draft
moc: moc-android
related: [c-clean-architecture, c-database-design, q-dagger-field-injection--android--medium, q-data-sync-unstable-network--android--hard, q-does-state-made-in-compose-help-avoid-race-condition--android--medium, q-mvvm-pattern--android--medium, q-repository-pattern--android--medium]
created: 2025-10-06
updated: 2025-11-10
tags: [android/architecture-clean, android/cache-offline, difficulty/medium, en, ru]
anki_cards:
  - slug: android-030-0-en
    front: "What are common data source strategies in Repository pattern?"
    back: |
      **Strategies**:
      1. **Single Source of Truth** - DB observed via Flow, network updates it
      2. **Cache-first** - memory -> network -> update cache
      3. **Network-first + fallback** - network -> DB if fails
      4. **Stale-while-revalidate** - show cache, refresh in background
      5. **Time-based** - check TTL before network request

      ```kotlin
      fun getProducts(): Flow<List<Product>> = dao.observeProducts()
          .onStart { refreshFromNetwork() }
      ```
    tags:
      - android_architecture
      - difficulty::medium
  - slug: android-030-0-ru
    front: "Какие стратегии источников данных используются в паттерне Repository?"
    back: |
      **Стратегии**:
      1. **Single Source of Truth** - БД наблюдается через Flow, сеть обновляет её
      2. **Cache-first** - память -> сеть -> обновить кэш
      3. **Network-first + fallback** - сеть -> БД при ошибке
      4. **Stale-while-revalidate** - показать кэш, обновить в фоне
      5. **Time-based** - проверить TTL перед запросом

      ```kotlin
      fun getProducts(): Flow<List<Product>> = dao.observeProducts()
          .onStart { refreshFromNetwork() }
      ```
    tags:
      - android_architecture
      - difficulty::medium

---
# Вопрос (RU)
> Как реализовать паттерн Repository с несколькими источниками данных (сеть, БД, кэш)?

# Question (EN)
> How to implement Repository pattern with multiple data sources (network, database, cache)?

---

## Ответ (RU)

**Repository** абстрагирует несколько источников данных, предоставляя единый вход для доменного слоя и отвечая за кэширование и синхронизацию между сетью, базой данных и in-memory/другими кэшами.

### Паттерн Единого Источника Истины

```kotlin
class ProductRepository(
    private val api: ProductApi,
    private val dao: ProductDao
) {
    // База данных — единый источник истины; сеть только обновляет её
    fun getProducts(): Flow<List<Product>> = dao.observeProducts()
        .onStart {
            // При первом сборе пробуем обновить данные из сети в фоне
            try {
                val freshProducts = api.getProducts()
                dao.insertProducts(freshProducts) // Обновит flow выше
            } catch (e: Exception) {
                // При ошибке остаёмся на локальных данных
            }
        }
}
```

### Стратегия Cache-First

```kotlin
class UserRepository(
    private val api: UserApi,
    private val cache: InMemoryCache<User>
) {
    suspend fun getUser(id: String): User {
        // 1. Сначала пробуем in-memory кэш
        cache.get(id)?.let { return it }

        // 2. Загружаем из сети
        val user = api.getUser(id)

        // 3. Обновляем кэш
        cache.put(id, user)

        return user
    }
}
```

### Network-First С Fallback

```kotlin
class NewsRepository(
    private val api: NewsApi,
    private val dao: NewsDao
) {
    suspend fun getNews(): Result<List<News>> {
        return try {
            // 1. Сначала пробуем сеть
            val news = api.getNews()
            dao.insertNews(news)  // Сохраняем в БД для оффлайна
            Result.success(news)
        } catch (e: IOException) {
            // 2. Fallback к локальному кэшу (БД)
            val cachedNews = dao.getNews()
            if (cachedNews.isNotEmpty()) {
                Result.success(cachedNews)
            } else {
                Result.failure(e)
            }
        }
    }
}
```

### Stale-While-Revalidate (устаревшие Данные + Фоновое обновление)

```kotlin
class ArticleRepository(
    private val api: ArticleApi,
    private val dao: ArticleDao
) {
    fun getArticles(): Flow<Resource<List<Article>>> = flow {
        // 1. Эмитим состояние загрузки
        emit(Resource.Loading())

        // 2. Эмитим кэш (может быть устаревшим)
        val cached = dao.getArticles()
        if (cached.isNotEmpty()) {
            emit(Resource.Success(cached))
        }

        // 3. Пробуем получить свежие данные и обновить
        try {
            val fresh = api.getArticles()
            dao.insertArticles(fresh)
            emit(Resource.Success(fresh))
        } catch (e: Exception) {
            if (cached.isEmpty()) {
                emit(Resource.Error(e.message))
            }
            // иначе продолжаем показывать данные из кэша
        }
    }
}

sealed class Resource<T> {
    class Loading<T> : Resource<T>()
    data class Success<T>(val data: T) : Resource<T>()
    data class Error<T>(val message: String?) : Resource<T>()
}
```

### Кэширование С Ограничением По Времени (Time-Based)

```kotlin
import kotlin.time.Duration
import kotlin.time.Duration.Companion.minutes

class WeatherRepository(
    private val api: WeatherApi,
    private val dao: WeatherDao
) {
    private val cacheValidityDuration: Duration = 5.minutes

    suspend fun getWeather(city: String): Weather {
        val cached = dao.getWeather(city)

        // Проверяем, не истёк ли срок действия кэша
        if (cached != null && !isCacheExpired(cached.timestamp)) {
            return cached
        }

        // Получаем свежие данные из сети
        val weather = api.getWeather(city)
        dao.insertWeather(weather.copy(timestamp = System.currentTimeMillis()))

        return weather
    }

    private fun isCacheExpired(timestamp: Long): Boolean {
        val now = System.currentTimeMillis()
        return now - timestamp > cacheValidityDuration.inWholeMilliseconds
    }
}
```

### Комбинирование Нескольких Источников

```kotlin
class ProfileRepository(
    private val api: ProfileApi,
    private val dao: ProfileDao,
    private val preferences: ProfilePreferences
) {
    fun getProfile(userId: String): Flow<Profile> = flow {
        // 1. Быстрый источник — preferences (последний использованный профиль и т.п.)
        preferences.getProfile()?.let { emit(it) }

        // 2. Затем данные из БД (одноразовое чтение перед запросом к сети)
        dao.getProfile(userId)?.let { emit(it) }

        // 3. Наконец, сеть: обновляем все слои
        try {
            val profile = api.getProfile(userId)
            dao.insertProfile(profile)
            preferences.saveProfile(profile)
            emit(profile)
        } catch (e: Exception) {
            // Если кэш уже отдал данные — просто остаёмся на них
        }
    }
}
```

**Краткое содержание (RU)**: Repository координирует несколько источников данных. Основные стратегии: (1) Единый источник истины (наблюдаем БД через `Flow`, сеть только обновляет её, например через `onStart`). (2) Cache-first (in-memory → сеть → обновить кэш). (3) Network-first с fallback к БД. (4) Stale-while-revalidate (показать кэш, параллельно обновить). (5) Кэширование по времени (TTL). (6) Комбинация уровней (preferences → БД → сеть) за единым API, с использованием `Flow` для реактивных обновлений.

---

## Answer (EN)

**Repository** abstracts multiple data sources, providing a single entry point for the domain layer and handling caching/synchronization between network, database, and in-memory/other caches.

### Single Source of Truth Pattern

```kotlin
class ProductRepository(
    private val api: ProductApi,
    private val dao: ProductDao
) {
    // Database is the single source of truth; network only updates it
    fun getProducts(): Flow<List<Product>> = dao.observeProducts()
        .onStart {
            // On first collection, try to refresh from network in the background
            try {
                val freshProducts = api.getProducts()
                dao.insertProducts(freshProducts) // Will update the flow above
            } catch (e: Exception) {
                // Stay with local data on failure
            }
        }
}
```

### Cache-First Strategy

```kotlin
class UserRepository(
    private val api: UserApi,
    private val cache: InMemoryCache<User>
) {
    suspend fun getUser(id: String): User {
        // 1. Try in-memory cache
        cache.get(id)?.let { return it }

        // 2. Fetch from network
        val user = api.getUser(id)

        // 3. Update cache
        cache.put(id, user)

        return user
    }
}
```

### Network-First with Fallback

```kotlin
class NewsRepository(
    private val api: NewsApi,
    private val dao: NewsDao
) {
    suspend fun getNews(): Result<List<News>> {
        return try {
            // 1. Try network first
            val news = api.getNews()
            dao.insertNews(news)  // Cache for offline
            Result.success(news)
        } catch (e: IOException) {
            // 2. Fallback to local cache (DB)
            val cachedNews = dao.getNews()
            if (cachedNews.isNotEmpty()) {
                Result.success(cachedNews)
            } else {
                Result.failure(e)
            }
        }
    }
}
```

### Stale-While-Revalidate

```kotlin
class ArticleRepository(
    private val api: ArticleApi,
    private val dao: ArticleDao
) {
    fun getArticles(): Flow<Resource<List<Article>>> = flow {
        // 1. Emit loading
        emit(Resource.Loading())

        // 2. Emit cached data (might be stale)
        val cached = dao.getArticles()
        if (cached.isNotEmpty()) {
            emit(Resource.Success(cached))
        }

        // 3. Fetch fresh data and update
        try {
            val fresh = api.getArticles()
            dao.insertArticles(fresh)
            emit(Resource.Success(fresh))
        } catch (e: Exception) {
            if (cached.isEmpty()) {
                emit(Resource.Error(e.message))
            }
            // else: keep showing cached data
        }
    }
}

sealed class Resource<T> {
    class Loading<T> : Resource<T>()
    data class Success<T>(val data: T) : Resource<T>()
    data class Error<T>(val message: String?) : Resource<T>()
}
```

### Time-Based Caching

```kotlin
import kotlin.time.Duration
import kotlin.time.Duration.Companion.minutes

class WeatherRepository(
    private val api: WeatherApi,
    private val dao: WeatherDao
) {
    private val cacheValidityDuration: Duration = 5.minutes

    suspend fun getWeather(city: String): Weather {
        val cached = dao.getWeather(city)

        // Check if cache is still valid
        if (cached != null && !isCacheExpired(cached.timestamp)) {
            return cached
        }

        // Fetch fresh data
        val weather = api.getWeather(city)
        dao.insertWeather(weather.copy(timestamp = System.currentTimeMillis()))

        return weather
    }

    private fun isCacheExpired(timestamp: Long): Boolean {
        val now = System.currentTimeMillis()
        return now - timestamp > cacheValidityDuration.inWholeMilliseconds
    }
}
```

### Combining Multiple Sources

```kotlin
class ProfileRepository(
    private val api: ProfileApi,
    private val dao: ProfileDao,
    private val preferences: ProfilePreferences
) {
    fun getProfile(userId: String): Flow<Profile> = flow {
        // 1. Emit from preferences (fastest, e.g., last used profile)
        preferences.getProfile()?.let { emit(it) }

        // 2. Emit from database (one-shot read before network request)
        dao.getProfile(userId)?.let { emit(it) }

        // 3. Fetch from network and update all layers
        try {
            val profile = api.getProfile(userId)
            dao.insertProfile(profile)
            preferences.saveProfile(profile)
            emit(profile)
        } catch (e: Exception) {
            // Already emitted cached data if any
        }
    }
}
```

**English Summary**: Repository coordinates multiple data sources. Typical strategies: (1) Single source of truth (DB observed via `Flow`, network updates it, e.g., using `onStart`). (2) Cache-first (in-memory → network → update cache). (3) Network-first with DB fallback. (4) Stale-while-revalidate (show cached, refresh in background). (5) Time-based caching (validate TTL before network). (6) Combining multiple layers (preferences → DB → network) behind a single API, using `Flow` for reactive updates.

---

## Follow-ups

- [[q-dagger-field-injection--android--medium]]
- [[q-does-state-made-in-compose-help-avoid-race-condition--android--medium]]
- Как организовать `Repository` и `UseCase` взаимодействие при сложных правилах выборки данных?
- Как реализовать стратегию синхронизации, когда локальные изменения пользователя должны отправляться на сервер и объединяться с удалёнными данными?
- Как тестировать `Repository` с несколькими источниками данных (моки для API/БД/кэша, фейковые реализация и т.д.)?

## References
- [Data layer - Android](https://developer.android.com/topic/architecture/data-layer)

## Related Questions

### Prerequisites / Concepts

- [[c-database-design]]
- [[c-clean-architecture]]

### Related (Medium)
- [[q-repository-pattern--android--medium]] - Architecture
- [[q-usecase-pattern-android--android--medium]] - Architecture
- [[q-glide-image-loading-internals--android--medium]] - Glide

### Advanced (Harder)
- [[q-data-sync-unstable-network--android--hard]] - Networking
- [[q-multi-module-best-practices--android--hard]] - Architecture
- [[q-modularization-patterns--android--hard]] - Architecture

### Hub
- [[q-clean-architecture-android--android--hard]] - Clean Architecture principles