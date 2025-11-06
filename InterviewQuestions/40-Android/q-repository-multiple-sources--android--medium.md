---
id: android-030
title: Repository Pattern with Multiple Data Sources / Паттерн Repository с несколькими
  источниками данных
aliases: []
topic: android
subtopics:
- architecture-clean
- cache-offline
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- android/architecture
- android/caching
- android/data-layer
- android/repository
- difficulty/medium
- en
- ru
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority
status: draft
moc: moc-android
related:
- c-database-design
- c-clean-architecture
- q-dagger-field-injection--android--medium
- q-does-state-made-in-compose-help-avoid-race-condition--android--medium
- q-kmm-ktor-networking--multiplatform--medium
created: 2025-10-06
updated: 2025-10-06
tags:
- android/architecture-clean
- android/cache-offline
- difficulty/medium
- en
- ru
date created: Saturday, November 1st 2025, 12:47:02 pm
date modified: Saturday, November 1st 2025, 5:43:32 pm
---

# Question (EN)
> How to implement Repository pattern with multiple data sources (network, database, cache)?
# Вопрос (RU)
> Как реализовать паттерн Repository с несколькими источниками данных (сеть, БД, кэш)?

---

## Answer (EN)

**Repository** abstracts data sources, providing single source of truth and handling caching/synchronization.

### Single Source of Truth Pattern

```kotlin
class ProductRepository(
    private val api: ProductApi,
    private val dao: ProductDao,
    private val cache: ProductCache
) {
    // Database is single source of truth
    fun getProducts(): Flow<List<Product>> = flow {
        // 1. Emit cached/DB data immediately
        emitAll(dao.observeProducts())

        // 2. Fetch fresh data in background
        try {
            val freshProducts = api.getProducts()
            dao.insertProducts(freshProducts)  // Updates flow above
        } catch (e: Exception) {
            // Ignore, using cached data
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
        // 1. Try cache
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
            // 2. Fallback to cache
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

        // 3. Fetch fresh data
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
class WeatherRepository(
    private val api: WeatherApi,
    private val dao: WeatherDao
) {
    private val cacheValidityDuration = 5.minutes

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
        // 1. Emit from preferences (fastest)
        preferences.getProfile()?.let { emit(it) }

        // 2. Emit from database
        dao.getProfile(userId)?.let { emit(it) }

        // 3. Fetch from network
        try {
            val profile = api.getProfile(userId)

            // Update all layers
            dao.insertProfile(profile)
            preferences.saveProfile(profile)

            emit(profile)
        } catch (e: Exception) {
            // Already emitted cached data
        }
    }
}
```

**English Summary**: Repository patterns: **Single source of truth** (DB is source, network updates it). **Cache-first** (memory cache → network → update cache). **Network-first** (network → DB fallback). **Stale-while-revalidate** (show cached, fetch fresh). **Time-based** (check expiry before fetching). Combine multiple sources: preferences → DB → network. Use Flow for reactive updates.


# Question (EN)
> How to implement Repository pattern with multiple data sources (network, database, cache)?
# Вопрос (RU)
> Как реализовать паттерн Repository с несколькими источниками данных (сеть, БД, кэш)?

---


---


## Answer (EN)

**Repository** abstracts data sources, providing single source of truth and handling caching/synchronization.

### Single Source of Truth Pattern

```kotlin
class ProductRepository(
    private val api: ProductApi,
    private val dao: ProductDao,
    private val cache: ProductCache
) {
    // Database is single source of truth
    fun getProducts(): Flow<List<Product>> = flow {
        // 1. Emit cached/DB data immediately
        emitAll(dao.observeProducts())

        // 2. Fetch fresh data in background
        try {
            val freshProducts = api.getProducts()
            dao.insertProducts(freshProducts)  // Updates flow above
        } catch (e: Exception) {
            // Ignore, using cached data
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
        // 1. Try cache
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
            // 2. Fallback to cache
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

        // 3. Fetch fresh data
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
class WeatherRepository(
    private val api: WeatherApi,
    private val dao: WeatherDao
) {
    private val cacheValidityDuration = 5.minutes

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
        // 1. Emit from preferences (fastest)
        preferences.getProfile()?.let { emit(it) }

        // 2. Emit from database
        dao.getProfile(userId)?.let { emit(it) }

        // 3. Fetch from network
        try {
            val profile = api.getProfile(userId)

            // Update all layers
            dao.insertProfile(profile)
            preferences.saveProfile(profile)

            emit(profile)
        } catch (e: Exception) {
            // Already emitted cached data
        }
    }
}
```

**English Summary**: Repository patterns: **Single source of truth** (DB is source, network updates it). **Cache-first** (memory cache → network → update cache). **Network-first** (network → DB fallback). **Stale-while-revalidate** (show cached, fetch fresh). **Time-based** (check expiry before fetching). Combine multiple sources: preferences → DB → network. Use Flow for reactive updates.

## Ответ (RU)

**Repository** абстрагирует источники данных, предоставляя единый источник истины и обрабатывая кэширование/синхронизацию.

### Паттерн Единого Источника Истины

```kotlin
class ProductRepository(
    private val api: ProductApi,
    private val dao: ProductDao
) {
    // База данных - единый источник истины
    fun getProducts(): Flow<List<Product>> = flow {
        // 1. Эмитить кэшированные/DB данные немедленно
        emitAll(dao.observeProducts())

        // 2. Загрузить свежие данные в фоне
        try {
            val freshProducts = api.getProducts()
            dao.insertProducts(freshProducts)  // Обновляет flow выше
        } catch (e: Exception) {
            // Игнорировать, использовать кэшированные данные
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
        // 1. Попробовать кэш
        cache.get(id)?.let { return it }

        // 2. Загрузить из сети
        val user = api.getUser(id)

        // 3. Обновить кэш
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
            // 1. Попробовать сеть сначала
            val news = api.getNews()
            dao.insertNews(news)  // Кэшировать для оффлайна
            Result.success(news)
        } catch (e: IOException) {
            // 2. Fallback к кэшу
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

**Краткое содержание**: Паттерны Repository: **Единый источник истины** (БД источник, сеть обновляет её). **Cache-first** (кэш памяти → сеть → обновить кэш). **Network-first** (сеть → БД fallback). **Stale-while-revalidate** (показать кэш, загрузить свежее). **Time-based** (проверить истечение до загрузки). Комбинировать источники: preferences → DB → network. Использовать Flow для реактивных обновлений.

---

## References
- [Data layer - Android](https://developer.android.com/topic/architecture/data-layer)


## Follow-ups

- [[q-dagger-field-injection--android--medium]]
- [[q-does-state-made-in-compose-help-avoid-race-condition--android--medium]]
- [[q-kmm-ktor-networking--multiplatform--medium]]


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

