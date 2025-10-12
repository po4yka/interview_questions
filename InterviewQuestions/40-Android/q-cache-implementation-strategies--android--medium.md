---
topic: android
tags:
  - android
  - caching
  - performance
  - data-storage
  - optimization
difficulty: medium
status: draft
---

# Как реализовать кэширование в Android?

# Question (EN)
> How to implement caching in Android?

# Вопрос (RU)
> Как реализовать кэширование в Android?

---

## Answer (EN)

Android caching strategies: **SharedPreferences** for simple key-value data, **Room Database** for structured data with TTL, **Retrofit + OkHttp** for HTTP caching with offline support, **Glide** for image caching, **LruCache** for in-memory caching, **DataStore** for preferences. Patterns: Cache-Aside (lazy load), Write-Through (update cache + source), Write-Behind (async writes), Refresh-Ahead (proactive refresh). Multi-level caching: Memory → Disk → Network. Implement TTL, cache invalidation, and monitoring for optimal performance.

---

## Ответ (RU)

Создание кэша в Android приложении помогает улучшить производительность и UX, сохраняя данные локально для быстрого доступа. В зависимости от типа данных и потребностей приложения, можно использовать различные методы кэширования.

### 1. SharedPreferences для простых данных

Подходит для сохранения небольших объемов данных, таких как настройки или кэшированные ответы от API.

```kotlin
// Singleton для работы с кэшем
object PreferencesCache {
    private const val PREF_NAME = "app_cache"
    private const val KEY_USER_DATA = "user_data"
    private const val KEY_LAST_UPDATE = "last_update"

    private fun getPrefs(context: Context): SharedPreferences {
        return context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
    }

    // Сохранение данных
    fun cacheUserData(context: Context, userData: String) {
        getPrefs(context).edit {
            putString(KEY_USER_DATA, userData)
            putLong(KEY_LAST_UPDATE, System.currentTimeMillis())
        }
    }

    // Чтение данных
    fun getUserData(context: Context): String? {
        return getPrefs(context).getString(KEY_USER_DATA, null)
    }

    // Проверка актуальности кэша (TTL - Time To Live)
    fun isCacheValid(context: Context, maxAgeMs: Long = 5 * 60 * 1000): Boolean {
        val lastUpdate = getPrefs(context).getLong(KEY_LAST_UPDATE, 0)
        return System.currentTimeMillis() - lastUpdate < maxAgeMs
    }

    // Очистка кэша
    fun clearCache(context: Context) {
        getPrefs(context).edit { clear() }
    }
}

// Использование
class UserRepository(private val context: Context) {
    suspend fun getUser(): User {
        // Проверяем кэш
        if (PreferencesCache.isCacheValid(context)) {
            val cachedData = PreferencesCache.getUserData(context)
            if (cachedData != null) {
                return Json.decodeFromString(cachedData)
            }
        }

        // Загружаем с сервера
        val user = apiService.getUser()

        // Кэшируем
        PreferencesCache.cacheUserData(
            context,
            Json.encodeToString(user)
        )

        return user
    }
}
```

### 2. Room Database для структурированных данных

Room — это библиотека ORM для работы с SQLite, которая упрощает создание и использование базы данных.

```kotlin
// Entity
@Entity(tableName = "cached_users")
data class CachedUser(
    @PrimaryKey val id: Int,
    val name: String,
    val email: String,
    val avatarUrl: String?,
    val cachedAt: Long = System.currentTimeMillis()
)

// DAO
@Dao
interface UserCacheDao {
    @Query("SELECT * FROM cached_users WHERE id = :userId")
    suspend fun getUser(userId: Int): CachedUser?

    @Query("SELECT * FROM cached_users WHERE cachedAt > :minTime ORDER BY cachedAt DESC")
    suspend fun getRecentUsers(minTime: Long): List<CachedUser>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: CachedUser)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUsers(users: List<CachedUser>)

    @Query("DELETE FROM cached_users WHERE cachedAt < :expireTime")
    suspend fun deleteExpired(expireTime: Long)

    @Query("DELETE FROM cached_users")
    suspend fun clearAll()
}

// Database
@Database(entities = [CachedUser::class], version = 1)
abstract class CacheDatabase : RoomDatabase() {
    abstract fun userCacheDao(): UserCacheDao

    companion object {
        @Volatile
        private var INSTANCE: CacheDatabase? = null

        fun getInstance(context: Context): CacheDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    CacheDatabase::class.java,
                    "app_cache.db"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}

// Repository с кэшированием
class UserRepository(
    private val apiService: ApiService,
    private val cacheDao: UserCacheDao
) {
    private val cacheTimeout = 5 * 60 * 1000L // 5 minutes

    suspend fun getUser(userId: Int, forceRefresh: Boolean = false): User {
        // 1. Проверяем кэш
        if (!forceRefresh) {
            val cached = cacheDao.getUser(userId)
            if (cached != null && isCacheValid(cached.cachedAt)) {
                return cached.toUser()
            }
        }

        // 2. Загружаем с сервера
        return try {
            val user = apiService.getUser(userId)

            // 3. Кэшируем результат
            cacheDao.insertUser(user.toCachedUser())

            user
        } catch (e: Exception) {
            // 4. Если сеть недоступна, используем устаревший кэш
            val cached = cacheDao.getUser(userId)
            cached?.toUser() ?: throw e
        }
    }

    private fun isCacheValid(cachedAt: Long): Boolean {
        return System.currentTimeMillis() - cachedAt < cacheTimeout
    }

    // Периодическая очистка устаревшего кэша
    suspend fun cleanupExpiredCache() {
        val expireTime = System.currentTimeMillis() - cacheTimeout
        cacheDao.deleteExpired(expireTime)
    }
}

// Extension functions для конвертации
fun CachedUser.toUser() = User(id, name, email, avatarUrl)
fun User.toCachedUser() = CachedUser(id, name, email, avatarUrl)
```

### 3. Retrofit + OkHttp Cache для HTTP запросов

Настройка Retrofit с OkHttpClient для кэширования сетевых запросов.

```kotlin
object NetworkCache {
    // Создание OkHttp кэша
    fun createCache(context: Context): Cache {
        val cacheSize = 10 * 1024 * 1024L // 10 MB
        val cacheDir = File(context.cacheDir, "http_cache")
        return Cache(cacheDir, cacheSize)
    }

    // OkHttpClient с кэшированием
    fun createOkHttpClient(context: Context): OkHttpClient {
        return OkHttpClient.Builder()
            .cache(createCache(context))
            .addNetworkInterceptor(CacheInterceptor())
            .addInterceptor(OfflineCacheInterceptor(context))
            .build()
    }

    // Network cache interceptor
    private class CacheInterceptor : Interceptor {
        override fun intercept(chain: Interceptor.Chain): Response {
            val response = chain.proceed(chain.request())

            val cacheControl = CacheControl.Builder()
                .maxAge(5, TimeUnit.MINUTES) // Cache for 5 minutes
                .build()

            return response.newBuilder()
                .removeHeader("Pragma")
                .removeHeader("Cache-Control")
                .header("Cache-Control", cacheControl.toString())
                .build()
        }
    }

    // Offline cache interceptor
    private class OfflineCacheInterceptor(
        private val context: Context
    ) : Interceptor {
        override fun intercept(chain: Interceptor.Chain): Response {
            var request = chain.request()

            // Если нет интернета, используем кэш
            if (!isNetworkAvailable(context)) {
                val cacheControl = CacheControl.Builder()
                    .maxStale(7, TimeUnit.DAYS)
                    .onlyIfCached()
                    .build()

                request = request.newBuilder()
                    .cacheControl(cacheControl)
                    .build()
            }

            return chain.proceed(request)
        }

        private fun isNetworkAvailable(context: Context): Boolean {
            val connectivityManager = context.getSystemService(
                Context.CONNECTIVITY_SERVICE
            ) as ConnectivityManager

            val network = connectivityManager.activeNetwork ?: return false
            val capabilities = connectivityManager.getNetworkCapabilities(network)
                ?: return false

            return capabilities.hasCapability(
                NetworkCapabilities.NET_CAPABILITY_INTERNET
            )
        }
    }
}

// API интерфейс с аннотациями кэширования
interface ApiService {
    // Кэшировать на 5 минут
    @Headers("Cache-Control: max-age=300")
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: Int): User

    // Всегда запрашивать с сервера
    @Headers("Cache-Control: no-cache")
    @POST("users")
    suspend fun createUser(@Body user: User): User
}

// Создание Retrofit
val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .client(NetworkCache.createOkHttpClient(context))
    .addConverterFactory(GsonConverterFactory.create())
    .build()
```

### 4. Glide для кэширования изображений

Glide — мощная библиотека для загрузки и кэширования изображений.

```kotlin
// Настройка Glide
@GlideModule
class MyGlideModule : AppGlideModule() {
    override fun applyOptions(context: Context, builder: GlideBuilder) {
        // Размер кэша в памяти
        val memoryCacheSizeBytes = 1024 * 1024 * 20L // 20 MB
        builder.setMemoryCache(LruResourceCache(memoryCacheSizeBytes))

        // Размер дискового кэша
        val diskCacheSizeBytes = 1024 * 1024 * 100L // 100 MB
        builder.setDiskCache(
            InternalCacheDiskCacheFactory(context, diskCacheSizeBytes)
        )

        // Logging
        if (BuildConfig.DEBUG) {
            builder.setLogLevel(Log.DEBUG)
        }
    }
}

// Загрузка изображения
Glide.with(context)
    .load(imageUrl)
    .diskCacheStrategy(DiskCacheStrategy.ALL) // Кэшировать оригинал и трансформации
    .placeholder(R.drawable.placeholder)
    .error(R.drawable.error_image)
    .into(imageView)

// Предзагрузка изображений
Glide.with(context)
    .load(imageUrl)
    .preload()

// Очистка кэша
// Memory cache (на main thread)
Glide.get(context).clearMemory()

// Disk cache (на background thread)
GlobalScope.launch(Dispatchers.IO) {
    Glide.get(context).clearDiskCache()
}

// Custom cache key
Glide.with(context)
    .load(imageUrl)
    .signature(ObjectKey(System.currentTimeMillis() / (24 * 60 * 60 * 1000))) // Кэш на 1 день
    .into(imageView)
```

### 5. In-Memory кэш (LruCache)

Для быстрого доступа к часто используемым данным.

```kotlin
// Generic LRU Cache
class MemoryCache<K, V>(maxSize: Int) {
    private val cache = object : LruCache<K, V>(maxSize) {
        override fun sizeOf(key: K, value: V): Int {
            return when (value) {
                is Bitmap -> value.byteCount / 1024 // Size in KB
                is String -> value.length / 1024
                else -> 1
            }
        }

        override fun entryRemoved(
            evicted: Boolean,
            key: K,
            oldValue: V,
            newValue: V?
        ) {
            if (evicted && oldValue is Bitmap) {
                oldValue.recycle()
            }
        }
    }

    fun get(key: K): V? = cache.get(key)

    fun put(key: K, value: V) {
        cache.put(key, value)
    }

    fun remove(key: K): V? = cache.remove(key)

    fun clear() {
        cache.evictAll()
    }

    fun size(): Int = cache.size()

    fun maxSize(): Int = cache.maxSize()
}

// Использование для кэширования пользователей
class UserCache {
    private val cache = MemoryCache<Int, User>(maxSize = 50) // 50 users max

    fun getUser(userId: Int): User? = cache.get(userId)

    fun putUser(user: User) {
        cache.put(user.id, user)
    }

    fun invalidateUser(userId: Int) {
        cache.remove(userId)
    }

    fun clear() {
        cache.clear()
    }
}

// Repository с multi-level кэшированием
class UserRepository(
    private val memoryCache: UserCache,
    private val diskCache: UserCacheDao,
    private val apiService: ApiService
) {
    suspend fun getUser(userId: Int): User {
        // Level 1: Memory cache
        memoryCache.getUser(userId)?.let { return it }

        // Level 2: Disk cache
        diskCache.getUser(userId)?.let { cached ->
            if (isCacheValid(cached.cachedAt)) {
                val user = cached.toUser()
                memoryCache.putUser(user) // Store in memory
                return user
            }
        }

        // Level 3: Network
        val user = apiService.getUser(userId)

        // Update caches
        memoryCache.putUser(user)
        diskCache.insertUser(user.toCachedUser())

        return user
    }

    private fun isCacheValid(cachedAt: Long): Boolean {
        return System.currentTimeMillis() - cachedAt < 5 * 60 * 1000
    }
}
```

### 6. DataStore для кэширования настроек

Современная замена SharedPreferences.

```kotlin
// Preferences DataStore
val Context.dataStore: DataStore<Preferences> by preferencesDataStore(
    name = "app_cache"
)

class CacheManager(private val context: Context) {
    private val CACHE_KEY = stringPreferencesKey("cached_data")
    private val TIMESTAMP_KEY = longPreferencesKey("cache_timestamp")

    // Сохранение в кэш
    suspend fun cacheData(data: String) {
        context.dataStore.edit { preferences ->
            preferences[CACHE_KEY] = data
            preferences[TIMESTAMP_KEY] = System.currentTimeMillis()
        }
    }

    // Чтение из кэша с проверкой TTL
    suspend fun getCachedData(maxAge: Long = 5 * 60 * 1000): String? {
        val preferences = context.dataStore.data.first()
        val timestamp = preferences[TIMESTAMP_KEY] ?: 0L

        return if (System.currentTimeMillis() - timestamp < maxAge) {
            preferences[CACHE_KEY]
        } else {
            null
        }
    }

    // Очистка кэша
    suspend fun clearCache() {
        context.dataStore.edit { it.clear() }
    }
}
```

### Стратегии кэширования

#### Cache-Aside (Lazy Loading)

```kotlin
suspend fun getData(key: String): Data {
    // 1. Try to get from cache
    val cached = cache.get(key)
    if (cached != null) return cached

    // 2. Load from source
    val data = dataSource.load(key)

    // 3. Store in cache
    cache.put(key, data)

    return data
}
```

#### Write-Through

```kotlin
suspend fun updateData(key: String, data: Data) {
    // 1. Update cache first
    cache.put(key, data)

    // 2. Update data source
    dataSource.save(key, data)
}
```

#### Write-Behind (Write-Back)

```kotlin
suspend fun updateData(key: String, data: Data) {
    // 1. Update cache immediately
    cache.put(key, data)

    // 2. Queue update to data source
    updateQueue.enqueue(key, data)

    // 3. Periodic flush to data source
    scope.launch {
        delay(1000)
        flushUpdateQueue()
    }
}
```

#### Refresh-Ahead

```kotlin
suspend fun getData(key: String): Data {
    val cached = cache.get(key)

    // Если кэш скоро истечет, обновляем в фоне
    if (cached != null && cached.isNearExpiration()) {
        scope.launch {
            val fresh = dataSource.load(key)
            cache.put(key, fresh)
        }
    }

    return cached ?: dataSource.load(key).also {
        cache.put(key, it)
    }
}
```

### Best Practices

**1. Cache Invalidation**

```kotlin
class SmartCache<K, V>(
    private val maxAge: Long = 5 * 60 * 1000 // 5 minutes
) {
    private data class CacheEntry<V>(
        val value: V,
        val timestamp: Long
    )

    private val cache = mutableMapOf<K, CacheEntry<V>>()

    fun get(key: K): V? {
        val entry = cache[key] ?: return null

        return if (isValid(entry)) {
            entry.value
        } else {
            cache.remove(key)
            null
        }
    }

    fun put(key: K, value: V) {
        cache[key] = CacheEntry(value, System.currentTimeMillis())
    }

    private fun isValid(entry: CacheEntry<V>): Boolean {
        return System.currentTimeMillis() - entry.timestamp < maxAge
    }

    fun invalidate(key: K) {
        cache.remove(key)
    }

    fun invalidateAll() {
        cache.clear()
    }
}
```

**2. Cache Warming**

```kotlin
class UserRepository {
    suspend fun warmupCache() {
        // Предзагрузка популярных данных
        val popularUsers = apiService.getPopularUsers()
        popularUsers.forEach { user ->
            memoryCache.put(user.id, user)
            diskCache.insertUser(user.toCachedUser())
        }
    }
}
```

**3. Cache Monitoring**

```kotlin
class CacheMetrics {
    private var hits = 0
    private var misses = 0

    fun recordHit() {
        hits++
    }

    fun recordMiss() {
        misses++
    }

    fun hitRate(): Double {
        val total = hits + misses
        return if (total > 0) hits.toDouble() / total else 0.0
    }

    fun reset() {
        hits = 0
        misses = 0
    }
}
```
