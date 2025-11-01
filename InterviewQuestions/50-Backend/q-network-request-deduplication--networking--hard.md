---
id: 20251012-12271153
title: "Network Request Deduplication / Дедупликация сетевых запросов"
aliases: [Network Request Deduplication, Дедупликация сетевых запросов, Request Deduplication, Дедупликация запросов]
topic: networking
subtopics: [optimization, concurrency, caching]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-coroutines, c-flow, q-retrofit-call-adapter-advanced--networking--medium, q-data-sync-unstable-network--android--hard]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [networking, optimization, deduplication, concurrency, performance, caching, difficulty/hard]
date created: Tuesday, October 28th 2025, 9:50:49 pm
date modified: Thursday, October 30th 2025, 3:15:08 pm
---

# Вопрос (RU)
> Как реализовать дедупликацию сетевых запросов в Android для предотвращения множественных идентичных вызовов API? Объясните стратегии с использованием Kotlin coroutines и Flow.

# Question (EN)
> How to implement network request deduplication in Android to prevent multiple identical API calls? Explain strategies using Kotlin coroutines and Flow.

---

## Ответ (RU)

**Дедупликация запросов** - это техника оптимизации, которая предотвращает выполнение множественных идентичных сетевых запросов одновременно. Когда несколько частей приложения запрашивают одни и те же данные одновременно, дедупликация гарантирует, что выполняется только один реальный сетевый вызов, а все вызывающие получают один и тот же результат.

### Проблема

```kotlin
// ❌ Проблема: 3 одновременных запроса одних данных
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    init {
        viewModelScope.launch { repository.getUser("123") } // Запрос 1
        viewModelScope.launch { repository.getUser("123") } // Дубликат!
        viewModelScope.launch { repository.getUser("123") } // Ещё дубликат!
    }
}
```

### Стратегии дедупликации

#### 1. Дедупликация на основе Mutex

Простой подход: только одна корутина может выполнять запрос для конкретного ключа.

```kotlin
class MutexDeduplicator {
    private val mutexMap = ConcurrentHashMap<String, Mutex>()

    suspend fun <T> deduplicate(key: String, block: suspend () -> T): T {
        val mutex = mutexMap.getOrPut(key) { Mutex() }
        return mutex.withLock { block() }
    }
}
```

#### 2. Дедупликация на основе Deferred

Эффективнее для множества одновременных вызывающих.

```kotlin
class DeferredDeduplicator(private val scope: CoroutineScope) {
    private val requests = ConcurrentHashMap<String, Deferred<*>>()

    suspend fun <T> deduplicate(key: String, block: suspend () -> T): T {
        @Suppress("UNCHECKED_CAST")
        val deferred = requests.getOrPut(key) {
            scope.async {
                try { block() }
                finally { requests.remove(key) }
            }
        } as Deferred<T>

        return deferred.await()
    }
}
```

### Паттерн Cache-Aside с дедупликацией

```kotlin
class CacheAsideRepository<K, V>(
    private val cache: Cache<K, V>,
    private val deduplicator: RequestDeduplicator
) {
    suspend fun get(
        key: K,
        forceRefresh: Boolean = false,
        loader: suspend (K) -> V
    ): V {
        // ✅ Проверить кеш
        if (!forceRefresh) {
            cache.get(key)?.let { return it }
        }

        // ✅ Загрузить с дедупликацией
        val value = deduplicator.deduplicate(key.toString()) { loader(key) }
        cache.put(key, value)
        return value
    }
}
```

### Debouncing и Throttling

```kotlin
// Debouncing: ждать период тишины перед выполнением
class Debouncer {
    private val lastCallTime = AtomicLong(0)

    suspend fun <T> debounce(delayMs: Long, block: suspend () -> T): T? {
        val currentTime = System.currentTimeMillis()
        lastCallTime.set(currentTime)
        delay(delayMs)

        return if (lastCallTime.get() == currentTime) block() else null
    }
}

// Throttling: ограничить частоту выполнения
class Throttler {
    private val lastExecutionTime = AtomicLong(0)

    suspend fun <T> throttle(intervalMs: Long, block: suspend () -> T): T? {
        val currentTime = System.currentTimeMillis()
        if (currentTime - lastExecutionTime.get() < intervalMs) return null

        lastExecutionTime.set(currentTime)
        return block()
    }
}
```

### Полный Repository с дедупликацией

```kotlin
class OptimizedUserRepository(
    private val api: UserApiService,
    scope: CoroutineScope
) {
    private val deduplicator = DeferredDeduplicator(scope)
    private val cache = MemoryCache<String, User>()
    private val searchDebouncer = Debouncer()

    suspend fun getUser(userId: String, forceRefresh: Boolean = false): Result<User> {
        return runCatching {
            // ✅ Проверить кеш
            if (!forceRefresh) {
                cache.get(userId)?.let { return@runCatching it }
            }

            // ✅ Загрузить с дедупликацией
            deduplicator.deduplicate("user:$userId") {
                api.getUser(userId).also { cache.put(userId, it) }
            }
        }
    }

    suspend fun searchUsers(query: String): Result<List<User>> {
        return runCatching {
            searchDebouncer.debounce(300L) {
                deduplicator.deduplicate("search:$query") {
                    api.searchUsers(query)
                }
            } ?: emptyList()
        }
    }
}
```

### Best Practices

1. **Выбирайте правильную стратегию**
   - Mutex: простая, последовательное выполнение
   - Deferred: лучше для множества одновременных вызовов
   - SharedFlow: лучше для реактивных потоков

2. **Устанавливайте TTL для кеша**
   ```kotlin
   val cache = MemoryCache(ttlMs = TimeUnit.MINUTES.toMillis(5))
   ```

3. **Обрабатывайте отмену**
   ```kotlin
   deferred.cancel() // Отменить активный запрос
   ```

4. **Используйте debouncing для пользовательского ввода**
   ```kotlin
   searchDebouncer.debounce(300L) { searchUsers(query) }
   ```

### Распространённые ошибки

```kotlin
// ❌ Не обработка ошибок и очистка
val result = block()

// ✅ Правильно: очистка в finally
try { block() }
finally { requests.remove(key) }

// ❌ Неограниченный кеш
val cache = mutableMapOf<String, Data>()

// ✅ LRU кеш с maxSize
val cache = MemoryCache(maxSize = 100)
```

### Резюме

**Преимущества дедупликации:**
- Сокращение сетевых вызовов: множество вызывающих делят один запрос
- Лучшая производительность: меньше задержек и нагрузки
- Эффективность ресурсов: меньше одновременных соединений
- Улучшенный UX: быстрые ответы из кеша

**Ключевые техники:**
- Дедупликация с Mutex/Deferred
- Паттерн Cache-aside
- Debouncing для пользовательского ввода
- Throttling для частых событий
- LRU кеширование с TTL

---

## Answer (EN)

**Request deduplication** is an optimization technique that prevents making multiple identical network requests simultaneously. When multiple parts of an application request the same data concurrently, deduplication ensures only one actual network call is made, with all callers receiving the same response.

### The Problem

```kotlin
// ❌ Problem: 3 simultaneous identical requests
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    init {
        viewModelScope.launch { repository.getUser("123") } // Request 1
        viewModelScope.launch { repository.getUser("123") } // Duplicate!
        viewModelScope.launch { repository.getUser("123") } // Another duplicate!
    }
}
```

### Deduplication Strategies

#### 1. Mutex-Based Deduplication

Simple approach: only one coroutine can execute request for specific key.

```kotlin
class MutexDeduplicator {
    private val mutexMap = ConcurrentHashMap<String, Mutex>()

    suspend fun <T> deduplicate(key: String, block: suspend () -> T): T {
        val mutex = mutexMap.getOrPut(key) { Mutex() }
        return mutex.withLock { block() }
    }
}
```

#### 2. Deferred-Based Deduplication

More efficient for many concurrent callers.

```kotlin
class DeferredDeduplicator(private val scope: CoroutineScope) {
    private val requests = ConcurrentHashMap<String, Deferred<*>>()

    suspend fun <T> deduplicate(key: String, block: suspend () -> T): T {
        @Suppress("UNCHECKED_CAST")
        val deferred = requests.getOrPut(key) {
            scope.async {
                try { block() }
                finally { requests.remove(key) }
            }
        } as Deferred<T>

        return deferred.await()
    }
}
```

### Cache-Aside Pattern with Deduplication

```kotlin
class CacheAsideRepository<K, V>(
    private val cache: Cache<K, V>,
    private val deduplicator: RequestDeduplicator
) {
    suspend fun get(
        key: K,
        forceRefresh: Boolean = false,
        loader: suspend (K) -> V
    ): V {
        // ✅ Check cache first
        if (!forceRefresh) {
            cache.get(key)?.let { return it }
        }

        // ✅ Load with deduplication
        val value = deduplicator.deduplicate(key.toString()) { loader(key) }
        cache.put(key, value)
        return value
    }
}
```

### Debouncing and Throttling

```kotlin
// Debouncing: wait for quiet period before executing
class Debouncer {
    private val lastCallTime = AtomicLong(0)

    suspend fun <T> debounce(delayMs: Long, block: suspend () -> T): T? {
        val currentTime = System.currentTimeMillis()
        lastCallTime.set(currentTime)
        delay(delayMs)

        return if (lastCallTime.get() == currentTime) block() else null
    }
}

// Throttling: limit execution frequency
class Throttler {
    private val lastExecutionTime = AtomicLong(0)

    suspend fun <T> throttle(intervalMs: Long, block: suspend () -> T): T? {
        val currentTime = System.currentTimeMillis()
        if (currentTime - lastExecutionTime.get() < intervalMs) return null

        lastExecutionTime.set(currentTime)
        return block()
    }
}
```

### Complete Repository with Deduplication

```kotlin
class OptimizedUserRepository(
    private val api: UserApiService,
    scope: CoroutineScope
) {
    private val deduplicator = DeferredDeduplicator(scope)
    private val cache = MemoryCache<String, User>()
    private val searchDebouncer = Debouncer()

    suspend fun getUser(userId: String, forceRefresh: Boolean = false): Result<User> {
        return runCatching {
            // ✅ Check cache
            if (!forceRefresh) {
                cache.get(userId)?.let { return@runCatching it }
            }

            // ✅ Load with deduplication
            deduplicator.deduplicate("user:$userId") {
                api.getUser(userId).also { cache.put(userId, it) }
            }
        }
    }

    suspend fun searchUsers(query: String): Result<List<User>> {
        return runCatching {
            searchDebouncer.debounce(300L) {
                deduplicator.deduplicate("search:$query") {
                    api.searchUsers(query)
                }
            } ?: emptyList()
        }
    }
}
```

### Best Practices

1. **Choose Right Strategy**
   - Mutex: simple, sequential execution
   - Deferred: best for many concurrent callers
   - SharedFlow: best for reactive streams

2. **Set Appropriate TTL**
   ```kotlin
   val cache = MemoryCache(ttlMs = TimeUnit.MINUTES.toMillis(5))
   ```

3. **Handle Cancellation**
   ```kotlin
   deferred.cancel() // Cancel active request
   ```

4. **Use Debouncing for User Input**
   ```kotlin
   searchDebouncer.debounce(300L) { searchUsers(query) }
   ```

### Common Pitfalls

```kotlin
// ❌ Not handling errors and cleanup
val result = block()

// ✅ Correct: cleanup in finally
try { block() }
finally { requests.remove(key) }

// ❌ Unbounded cache
val cache = mutableMapOf<String, Data>()

// ✅ LRU cache with maxSize
val cache = MemoryCache(maxSize = 100)
```

### Summary

**Deduplication Benefits:**
- Reduced network calls: multiple callers share single request
- Better performance: less latency and load
- Resource efficiency: fewer concurrent connections
- Improved UX: faster responses from cache

**Key Techniques:**
- Deduplication with Mutex/Deferred
- Cache-aside pattern
- Debouncing for user input
- Throttling for frequent events
- LRU caching with TTL

---

## Follow-ups

- How to handle partial failures in batch requests with deduplication?
- What's the difference between debouncing and throttling for search queries?
- How to implement deduplication for GraphQL queries with different parameters?
- When should you invalidate the deduplication cache?
- How to monitor deduplication effectiveness in production?

## References

- [[c-coroutines]] - Kotlin Coroutines basics
- [[c-flow]] - Flow fundamentals
- Kotlin Coroutines official documentation
- Android caching best practices

## Related Questions

### Prerequisites (Easier)
- [[q-retrofit-call-adapter-advanced--networking--medium]] - Networking fundamentals

### Related (Same Level)
- [[q-data-sync-unstable-network--android--hard]] - Network reliability patterns
