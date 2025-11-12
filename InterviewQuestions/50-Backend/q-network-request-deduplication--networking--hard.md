---
id: net-005
title: "Network Request Deduplication / Дедупликация сетевых запросов"
aliases: [Network Request Deduplication, Request Deduplication, Дедупликация запросов, Дедупликация сетевых запросов]
topic: networking
subtopics: [concurrency]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-backend
related: [c-algorithms, q-data-sync-unstable-network--android--hard, q-retrofit-call-adapter-advanced--networking--medium]
created: 2025-10-15
updated: 2025-11-11
sources: []
tags: [networking, concurrency, deduplication, difficulty/hard, performance]

---

# Вопрос (RU)
> Как реализовать дедупликацию сетевых запросов в Android для предотвращения множественных идентичных вызовов API? Объясните стратегии с использованием Kotlin coroutines и `Flow`.

# Question (EN)
> How to implement network request deduplication in Android to prevent multiple identical API calls? Explain strategies using Kotlin coroutines and `Flow`.

---

## Ответ (RU)

**Дедупликация запросов** - это техника оптимизации, которая предотвращает выполнение множественных идентичных сетевых запросов одновременно. Когда несколько частей приложения запрашивают одни и те же данные одновременно, дедупликация гарантирует, что выполняется только один реальный сетевой вызов, а все вызывающие получают один и тот же результат для данного запроса.

Важно: дедупликация работает на уровне "одновременных" (overlapping) запросов. Если первый запрос уже завершился и данные не были закешированы или переиспользованы, следующий такой же запрос снова пойдет в сеть.

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

### Стратегии Дедупликации

#### 1. Дедупликация на основе Mutex (ограничение)

Простой подход: только одна корутина может выполнять критическую секцию для конкретного ключа.

Важное ограничение: такой вариант обеспечивает взаимное исключение, но сам по себе не гарантирует, что все конкурирующие вызовы переиспользуют один и тот же результат. Новые вызовы после выхода из `withLock` выполнят `block()` заново, поэтому для реальной дедупликации его обычно комбинируют с кешированием.

```kotlin
class MutexDeduplicator {
    private val mutexMap = ConcurrentHashMap<String, Mutex>()

    suspend fun <T> deduplicate(key: String, block: suspend () -> T): T {
        val mutex = mutexMap.getOrPut(key) { Mutex() }
        return mutex.withLock { block() }
        // ⚠️ В проде стоит подумать об удалении неиспользуемых mutex-ов,
        // чтобы избежать неограниченного роста mutexMap.
    }
}
```

#### 2. Дедупликация на основе Deferred

Более подходящий подход для множества одновременных вызывающих: все конкурирующие запросы получают один и тот же `Deferred` и ждут общего результата.

```kotlin
interface RequestDeduplicator {
    suspend fun <T> deduplicate(key: String, block: suspend () -> T): T
}

class DeferredDeduplicator(private val scope: CoroutineScope) : RequestDeduplicator {
    private val requests = ConcurrentHashMap<String, Deferred<*>>()

    @Suppress("UNCHECKED_CAST")
    override suspend fun <T> deduplicate(key: String, block: suspend () -> T): T {
        val existing = requests[key] as? Deferred<T>
        if (existing != null) return existing.await()

        val newDeferred = scope.async {
            try {
                block()
            } finally {
                requests.remove(key)
            }
        }

        val result = requests.putIfAbsent(key, newDeferred) as Deferred<T>?
        return (result ?: newDeferred).await()
    }
}
```

Такой вариант:
- гарантирует, что конкурирующие вызовы для одного ключа делят общий `Deferred`;
- очищает `requests` в `finally`;
- уменьшает риск гонок при `getOrPut`.

Важно: отмена одного из ожидающих не должна бездумно вызывать `cancel()` у общего `Deferred`, иначе вы отмените запрос и для остальных. Обычно инициатор, создавший `Deferred`, контролирует его отмену, а остальные только `await()`.

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

        // ✅ Загрузить с дедупликацией (для одновременных запросов одного ключа)
        val value = deduplicator.deduplicate(key.toString()) { loader(key) }
        cache.put(key, value)
        return value
    }
}
```

### Debouncing и Throttling (связанные, но отдельные техники)

Эти техники не являются дедупликацией в строгом смысле, но полезны для снижения числа запросов (например, при вводе текста).

```kotlin
// Упрощённый debouncer: ждать период тишины перед выполнением.
// ⚠️ Пример не потокобезопасен для высококонкурентных сценариев
// и больше иллюстративный, чем готовый продакшн-код.
class Debouncer {
    private val lastCallTime = AtomicLong(0)

    suspend fun <T> debounce(delayMs: Long, block: suspend () -> T): T? {
        val currentTime = System.currentTimeMillis()
        lastCallTime.set(currentTime)
        delay(delayMs)

        return if (lastCallTime.get() == currentTime) block() else null
    }
}

// Упрощённый throttler: ограничить частоту выполнения.
// ⚠️ Аналогично, для реальной конкуренции нужна атомарная логика обновления.
class Throttler {
    private val lastExecutionTime = AtomicLong(0)

    suspend fun <T> throttle(intervalMs: Long, block: suspend () -> T): T? {
        val currentTime = System.currentTimeMillis()
        val last = lastExecutionTime.get()
        if (currentTime - last < intervalMs) return null

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
    private val deduplicator: RequestDeduplicator = DeferredDeduplicator(scope)
    private val cache = MemoryCache<String, User>()
    private val searchDebouncer = Debouncer()

    suspend fun getUser(userId: String, forceRefresh: Boolean = false): Result<User> {
        return runCatching {
            // ✅ Проверить кеш
            if (!forceRefresh) {
                cache.get(userId)?.let { return@runCatching it }
            }

            // ✅ Загрузить с дедупликацией для конкурирующих запросов userId
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
   - Mutex: простая синхронизация, но для дедупликации почти всегда должен сочетаться с кешированием.
   - Deferred: лучше для множества одновременных вызовов, позволяет шарить результат.
   - `SharedFlow`/`StateFlow`: подходят для реактивных потоков, где подписчики разделяют одни и те же данные.

2. **Устанавливайте TTL для кеша**
   ```kotlin
   val cache = MemoryCache(ttlMs = TimeUnit.MINUTES.toMillis(5))
   ```

3. **Аккуратно обрабатывайте отмену**
   - Отмена одного потребителя не должна неожиданно отменять общий запрос для всех.
   - Отмену общего `Deferred` контролирует владелец, а не каждый await-ящий.

4. **Используйте debouncing для пользовательского ввода**
   ```kotlin
   searchDebouncer.debounce(300L) { searchUsers(query) }
   ```

### Распространённые ошибки

```kotlin
// ❌ Нет очистки состояния при ошибках
val result = block()

// ✅ Правильно: очистка в finally
try {
    block()
} finally {
    requests.remove(key)
}

// ❌ Неограниченный кеш
val cache = mutableMapOf<String, Data>()

// ✅ LRU-кеш с maxSize
val cache = MemoryCache(maxSize = 100)
```

### Резюме

**Преимущества дедупликации:**
- Сокращение сетевых вызовов: множество вызывающих делят один запрос.
- Лучшая производительность: меньше задержек и нагрузки.
- Эффективность ресурсов: меньше одновременных соединений.
- Улучшенный UX: быстрые ответы из кеша.

**Ключевые техники:**
- Дедупликация с помощью Deferred (и Mutex + кеш для простых случаев).
- Паттерн Cache-aside.
- Debouncing для пользовательского ввода.
- Throttling для частых событий.
- Ограниченное кеширование (LRU) с TTL.

---

## Answer (EN)

**Request deduplication** is an optimization technique that prevents making multiple identical network requests simultaneously. When multiple parts of an application request the same data concurrently, deduplication ensures only one actual network call is performed, and all callers share the same result for that overlapping request.

Note: deduplication acts on overlapping (concurrent) requests. If one request is already completed and the result is not cached or reused, a subsequent identical request will still hit the network.

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

#### 1. Mutex-Based Deduplication (with a caveat)

Simple approach: only one coroutine can execute the critical section for a given key.

Important caveat: this ensures mutual exclusion but does not, by itself, guarantee that all competing calls reuse the same result. New callers entering after `withLock` completes will run `block()` again. In real deduplication scenarios this is typically combined with caching.

```kotlin
class MutexDeduplicator {
    private val mutexMap = ConcurrentHashMap<String, Mutex>()

    suspend fun <T> deduplicate(key: String, block: suspend () -> T): T {
        val mutex = mutexMap.getOrPut(key) { Mutex() }
        return mutex.withLock { block() }
        // ⚠️ In production, consider cleaning up unused mutexes
        // to avoid unbounded growth of mutexMap.
    }
}
```

#### 2. Deferred-Based Deduplication

More suitable for many concurrent callers: all competing calls for the same key share a single `Deferred` and await the same result.

```kotlin
interface RequestDeduplicator {
    suspend fun <T> deduplicate(key: String, block: suspend () -> T): T
}

class DeferredDeduplicator(private val scope: CoroutineScope) : RequestDeduplicator {
    private val requests = ConcurrentHashMap<String, Deferred<*>>()

    @Suppress("UNCHECKED_CAST")
    override suspend fun <T> deduplicate(key: String, block: suspend () -> T): T {
        val existing = requests[key] as? Deferred<T>
        if (existing != null) return existing.await()

        val newDeferred = scope.async {
            try {
                block()
            } finally {
                requests.remove(key)
            }
        }

        val result = requests.putIfAbsent(key, newDeferred) as Deferred<T>?
        return (result ?: newDeferred).await()
    }
}
```

This approach:
- Ensures concurrent callers for the same key share the same `Deferred`.
- Cleans up the `requests` map in `finally`.
- Reduces races versus a naive `getOrPut`.

Important: cancellation of one waiter should not blindly call `cancel()` on the shared `Deferred`, otherwise you cancel the request for everyone. Typically, the creator controls cancellation; others only `await()`.

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

        // ✅ Load with deduplication for overlapping requests
        val value = deduplicator.deduplicate(key.toString()) { loader(key) }
        cache.put(key, value)
        return value
    }
}
```

### Debouncing and Throttling (related but distinct)

These are not strict deduplication, but they reduce the number of calls (e.g., for search).

```kotlin
// Simplified debouncer: wait for a quiet period before executing.
// ⚠️ Not fully thread-safe for heavy concurrency; illustrative only.
class Debouncer {
    private val lastCallTime = AtomicLong(0)

    suspend fun <T> debounce(delayMs: Long, block: suspend () -> T): T? {
        val currentTime = System.currentTimeMillis()
        lastCallTime.set(currentTime)
        delay(delayMs)

        return if (lastCallTime.get() == currentTime) block() else null
    }
}

// Simplified throttler: limit execution frequency.
// ⚠️ For real concurrent load, atomic update logic must be tightened.
class Throttler {
    private val lastExecutionTime = AtomicLong(0)

    suspend fun <T> throttle(intervalMs: Long, block: suspend () -> T): T? {
        val currentTime = System.currentTimeMillis()
        val last = lastExecutionTime.get()
        if (currentTime - last < intervalMs) return null

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
    private val deduplicator: RequestDeduplicator = DeferredDeduplicator(scope)
    private val cache = MemoryCache<String, User>()
    private val searchDebouncer = Debouncer()

    suspend fun getUser(userId: String, forceRefresh: Boolean = false): Result<User> {
        return runCatching {
            // ✅ Check cache first
            if (!forceRefresh) {
                cache.get(userId)?.let { return@runCatching it }
            }

            // ✅ Load with deduplication for concurrent userId requests
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

1. **Choose the right strategy**
   - Mutex: simple synchronization; for true deduplication, combine with caching.
   - Deferred: best for many concurrent callers, allows sharing a single result.
   - `SharedFlow`/`StateFlow`: good for reactive streams where subscribers share the same data.

2. **Set appropriate TTL**
   ```kotlin
   val cache = MemoryCache(ttlMs = TimeUnit.MINUTES.toMillis(5))
   ```

3. **Handle cancellation carefully**
   - Do not let one consumer cancel a shared request for everyone unintentionally.
   - The owner that created the shared `Deferred` typically manages its lifecycle.

4. **Use debouncing for user input**
   ```kotlin
   searchDebouncer.debounce(300L) { searchUsers(query) }
   ```

### Common Pitfalls

```kotlin
// ❌ Not cleaning up state on error
val result = block()

// ✅ Correct: cleanup in finally
try {
    block()
} finally {
    requests.remove(key)
}

// ❌ Unbounded cache
val cache = mutableMapOf<String, Data>()

// ✅ LRU cache with maxSize
val cache = MemoryCache(maxSize = 100)
```

### Summary

**Deduplication Benefits:**
- Reduced network calls: multiple callers share a single request.
- Better performance: less latency and load.
- Resource efficiency: fewer concurrent connections.
- Improved UX: faster responses from cache.

**Key Techniques:**
- Deduplication with Deferred (and Mutex + cache for simpler cases).
- Cache-aside pattern.
- Debouncing for user input.
- Throttling for frequent events.
- Bounded caching (LRU) with TTL.

---

## Follow-ups (RU)

- Как обрабатывать частичные ошибки в батч-запросах при дедупликации?
- В чем разница между debouncing и throttling для поисковых запросов?
- Как реализовать дедупликацию для GraphQL-запросов с разными параметрами?
- Когда следует инвалидировать кеш дедупликации?
- Как мониторить эффективность дедупликации в продакшене?

## Follow-ups

- How to handle partial failures in batch requests with deduplication?
- What's the difference between debouncing and throttling for search queries?
- How to implement deduplication for GraphQL queries with different parameters?
- When should you invalidate the deduplication cache?
- How to monitor deduplication effectiveness in production?

## References (RU)

- Официальная документация Kotlin Coroutines
- Официальные рекомендации по кешированию сетевых данных
- [[c-algorithms]]

## References

- Kotlin Coroutines official documentation
- Official best practices for network data caching
- [[c-algorithms]]

## Related Questions (RU)

### Предпосылки (проще)
- [[q-retrofit-call-adapter-advanced--networking--medium]] - Основы сетевого взаимодействия

### Похожие (тот же уровень)
- [[q-data-sync-unstable-network--android--hard]] - Паттерны надёжности сети

## Related Questions

### Prerequisites (Easier)
- [[q-retrofit-call-adapter-advanced--networking--medium]] - Networking fundamentals

### Related (Same Level)
- [[q-data-sync-unstable-network--android--hard]] - Network reliability patterns
