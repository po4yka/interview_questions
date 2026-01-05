---
id: kotlin-200
title: "Request coalescing and deduplication patterns / Объединение и дедупликация запросов"
aliases: [Caching, Deduplication, Optimization, Request Coalescing, Объединение запросов]
topic: kotlin
subtopics: [coroutines, performance]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-job-vs-supervisorjob--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [caching, coalescing, coroutines, deduplication, difficulty/hard, kotlin, optimization, patterns, performance]
---
# Вопрос (RU)

> Объясните паттерны объединения запросов (request coalescing) и дедупликации в Kotlin: зачем они нужны, как реализуются (на базе корутин), какие существуют потокобезопасные варианты, как отличать от батчинга и кэширования, и в каких продакшн-сценариях они применяются.

# Question (EN)

> Explain request coalescing and deduplication patterns in Kotlin: why they are needed, how to implement them (with coroutines), how to build thread-safe variants, how they differ from batching and caching, and where to apply them in real production systems.

## Ответ (RU)

Ниже приведена русскоязычная версия, полностью соответствующая английской части по структуре и глубине, с сохранением всех ключевых примеров и паттернов.

---

## Оглавление

- [Обзор](#обзор)
- [Определение паттерна](#определение-паттерна)
- [Проблемный сценарий](#проблемный-сценарий)
- [Архитектура решения (концептуально)](#архитектура-решения-концептуально)
- [Потокобезопасная реализация с ConcurrentHashMap](#потокобезопасная-реализация-с-concurrenthashmap)
- [Альтернативная реализация с Mutex](#альтернативная-реализация-с-mutex)
- [Полный класс RequestCoalescer](#полный-класс-requestcoalescer)
- [Истечение по времени (Time-Based Expiration)](#истечение-по-времени-time-based-expiration)
- [Батчинг против объединения запросов](#батчинг-против-объединения-запросов)
- [Объединение на основе `SharedFlow`](#объединение-на-основе-sharedflow)
- [Реальные примеры](#реальные-примеры)
- [Преимущества производительности](#преимущества-производительности)
- [Комбинация с in-memory кэшем](#комбинация-с-in-memory-кэшем)
- [Тестирование объединения](#тестирование-объединения)
- [Продакшн-сценарии](#продакшн-сценарии)
- [Паттерны интеграции](#паттерны-интеграции)
- [Лучшие практики](#лучшие-лучшие-практики)
- [Мониторинг и метрики](#мониторинг-и-метрики)
- [Типичные ошибки](#типичные-ошибки)
- [Дополнительные вопросы](#дополнительные-вопросы)
- [Ссылки](#ссылки)
- [Связанные вопросы](#связанные-вопросы)

---

## Обзор

Объединение запросов (request coalescing, дедупликация или схлопывание запросов) — техника оптимизации, которая объединяет несколько одновременных запросов к одному и тому же ресурсу в единый вызов бэкенда.

Ключевые преимущества:
- Существенно снижает нагрузку на бэкенд (часто в разы, иногда 10–100x)
- Улучшает время отклика (все запрашивающие получают один результат)
- Помогает избежать «лавины» запросов / cache stampede
- Уменьшает использование сетевого трафика
- Повышает эффективность кэширования

Когда использовать:
- Несколько компонентов одновременно запрашивают одни и те же данные
- Высоконагруженные эндпоинты с идентичными (по ключу) запросами
- Дорогие операции (запросы к БД, удалённые API)
- Подписки на данные в реальном времени

---

## Определение Паттерна

### Что Такое Объединение Запросов?

```text
БЕЗ объединения:
     Запрос 1
  Клиент
    A

     Запрос 2
  Клиент   Бэкенд
    B

     Запрос 3
  Клиент
    C

Результат: 3 идентичных вызова бэкенда

С объединением:

  Клиент
    A

     Единственный
  Клиент  Запрос   Бэкенд
    B

  Клиент
    C

Результат: 1 вызов бэкенда, 3 клиента получают общий результат
```

### Основные Концепции

1. Отслеживание выполняющихся запросов.
2. Совместное использование `Deferred<T>` между конкурентными запросами.
3. Дедупликация по ключу: одинаковый ключ → один запрос.
4. Широковещательная доставка результата всем ожидающим.
5. Очистка: удаление завершённых запросов из структуры отслеживания.

---

## Проблемный Сценарий

### Сценарий: Загрузка Профиля Пользователя

```kotlin
// ПРОБЛЕМА: несколько компонентов загружают один и тот же профиль пользователя
class UserProfileScreen : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // Компонент 1
        userRepository.getUser(userId) // API вызов 1

        // Компонент 2
        userRepository.getUser(userId) // API вызов 2

        // Компонент 3
        userRepository.getUser(userId) // API вызов 3

        // Компонент 4
        userRepository.getUser(userId) // API вызов 4
    }
}

// Результат: 4 идентичных API-вызова подряд
// Бэкенд получает 4x нагрузку
// Все вызовы конкурируют за сеть/CPU
```

### Реальное Влияние (пример метрик)

```kotlin
// Иллюстративный пример:
// БЕЗ объединения:
// - 10 000 запросов профиля/мин
// - В среднем 3 дубля на пользователя
// - Итого: 30 000 вызовов/мин
// - CPU бэкенда: 85%
// - P95: ~450мс

// С объединением:
// - 10 000 запросов профиля/мин
// - Дедуплицировано до ~3 500/мин
// - CPU бэкенда: ~30%
// - P95: ~120мс
```

---

## Архитектура Решения (концептуально)

Минимальная реализация (упрощённая, с потенциальными гонками):

```kotlin
class RequestCoalescer<K, V> {
    // Отслеживание выполняющихся запросов
    private val inFlightRequests = ConcurrentHashMap<K, Deferred<V>>()

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): V = coroutineScope {
        // Быстрый путь: если запрос уже выполняется — ждём его
        val existingRequest = inFlightRequests[key]
        if (existingRequest != null && existingRequest.isActive) {
            return@coroutineScope existingRequest.await()
        }

        // Запускаем новый запрос
        val deferred = async {
            try {
                operation()
            } finally {
                inFlightRequests.remove(key)
            }
        }

        // Возможна гонка между проверкой и вставкой — см. безопасные версии ниже
        inFlightRequests[key] = deferred

        deferred.await()
    }
}
```

Для продакшн-использования нужны потокобезопасные варианты ниже.

---

## Потокобезопасная Реализация С ConcurrentHashMap

### Вариант С putIfAbsent

```kotlin
class RequestCoalescer<K, V> {
    private val inFlightRequests = ConcurrentHashMap<K, Deferred<V>>()

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): V = coroutineScope {
        // Сначала пробуем переиспользовать активный запрос
        inFlightRequests[key]?.takeIf { it.isActive }?.let { existing ->
            return@coroutineScope existing.await()
        }

        val newDeferred = async {
            try {
                operation()
            } finally {
                // Здесь "this" — это сам Deferred внутри async-блока
                inFlightRequests.remove(key, this)
            }
        }

        // Публикуем запрос; если кто-то успел раньше — используем его
        val winner = inFlightRequests.putIfAbsent(key, newDeferred)
        val actual = (winner?.takeIf { it.isActive } ?: newDeferred)

        if (actual !== newDeferred) {
            // Проиграли гонку — отменяем свой deferred и ждём победителя
            newDeferred.cancel()
        }

        actual.await()
    }
}
```

### Обработка Ошибок С Общим Result

```kotlin
class ResilientRequestCoalescer<K, V> {
    private val inFlightRequests = ConcurrentHashMap<K, Deferred<Result<V>>>()

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): Result<V> = coroutineScope {
        inFlightRequests[key]?.takeIf { it.isActive }?.let { existing ->
            return@coroutineScope existing.await()
        }

        val newDeferred = async {
            try {
                Result.success(operation())
            } catch (e: Exception) {
                Result.failure(e)
            } finally {
                inFlightRequests.remove(key, this)
            }
        }

        val winner = inFlightRequests.putIfAbsent(key, newDeferred)
        val actual = (winner?.takeIf { it.isActive } ?: newDeferred)

        if (actual !== newDeferred) {
            newDeferred.cancel()
        }

        actual.await()
    }
}
```

Важно: не выполнять долгие или подвешивающие операции внутри `ConcurrentHashMap.compute` или других map-операций; в приведённых примерах внутри них мы только создаём `Deferred` (операция синхронная), а `await` вызывается снаружи.

---

## Альтернативная Реализация С Mutex

```kotlin
class MutexRequestCoalescer<K, V> {
    private val inFlightRequests = mutableMapOf<K, Deferred<V>>()
    private val mutex = Mutex()

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): V = coroutineScope {
        // Быстрый путь под мьютексом
        mutex.withLock {
            inFlightRequests[key]?.takeIf { it.isActive }?.let { existing ->
                return@coroutineScope existing.await()
            }
        }

        val newDeferred = async {
            try {
                operation()
            } finally {
                mutex.withLock {
                    inFlightRequests.remove(key, this)
                }
            }
        }

        // Публикация под мьютексом с double-check
        val actual = mutex.withLock {
            val existing = inFlightRequests[key]?.takeIf { it.isActive }
            if (existing != null) {
                newDeferred.cancel()
                existing
            } else {
                inFlightRequests[key] = newDeferred
                newDeferred
            }
        }

        actual.await()
    }
}
```

Рекомендации:
- `ConcurrentHashMap` + `putIfAbsent`: лучше при очень высокой конкуренции.
- `Mutex`: проще для понимания, достаточно для многих in-app сценариев.

---

## Полный Класс RequestCoalescer

Ниже — более «production-style» реализация с метриками и управлением временем жизни записей.

```kotlin
class RequestCoalescer<K, V>(
    private val config: CoalescerConfig = CoalescerConfig()
) {
    private val inFlightRequests = ConcurrentHashMap<K, RequestEntry<V>>()
    private val metrics = CoalescerMetrics()

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): V = coroutineScope {
        if (config.enableMetrics) metrics.totalRequests.incrementAndGet()

        val entry = inFlightRequests.compute(key) { _, existing ->
            if (existing != null && existing.isActive()) {
                if (config.enableMetrics) metrics.coalescedRequests.incrementAndGet()
                existing.incrementWaiters()
                existing
            } else {
                if (config.enableMetrics) metrics.uniqueRequests.incrementAndGet()
                RequestEntry(
                    deferred = async {
                        try {
                            executeWithTimeout(operation)
                        } finally {
                            // Удаление условное — в cleanup
                        }
                    },
                    createdAt = System.currentTimeMillis()
                )
            }
        }!!

        try {
            entry.deferred.await()
        } finally {
            entry.decrementWaiters()
            cleanupIfNeeded(key, entry)
        }
    }

    private suspend fun executeWithTimeout(
        operation: suspend () -> V
    ): V {
        return if (config.timeoutMs > 0) {
            withTimeout(config.timeoutMs) { operation() }
        } else {
            operation()
        }
    }

    private fun cleanupIfNeeded(key: K, entry: RequestEntry<V>) {
        if (!entry.hasWaiters() && !entry.isActive()) {
            inFlightRequests.remove(key, entry)
        }
    }

    fun getMetrics(): CoalescerMetrics = metrics

    fun clear() {
        inFlightRequests.clear()
        metrics.reset()
    }
}

data class RequestEntry<V>(
    val deferred: Deferred<V>,
    val createdAt: Long
) {
    private val waitersCount = AtomicInteger(1)

    fun isActive(): Boolean = deferred.isActive

    fun incrementWaiters() {
        waitersCount.incrementAndGet()
    }

    fun decrementWaiters() {
        waitersCount.decrementAndGet()
    }

    fun hasWaiters(): Boolean = waitersCount.get() > 0

    fun age(): Long = System.currentTimeMillis() - createdAt
}

data class CoalescerConfig(
    val timeoutMs: Long = 30_000,
    val maxEntryAge: Long = 60_000,
    val enableMetrics: Boolean = true
)

class CoalescerMetrics {
    val totalRequests = AtomicLong(0)
    val uniqueRequests = AtomicLong(0)
    val coalescedRequests = AtomicLong(0)

    fun getCoalescingRate(): Double {
        val total = totalRequests.get()
        return if (total > 0) {
            (coalescedRequests.get().toDouble() / total) * 100
        } else 0.0
    }

    fun getSavingsRate(): Double {
        val total = totalRequests.get()
        val unique = uniqueRequests.get()
        return if (total > 0) {
            ((total - unique).toDouble() / total) * 100
        } else 0.0
    }

    fun reset() {
        totalRequests.set(0)
        uniqueRequests.set(0)
        coalescedRequests.set(0)
    }
}
```

Замечание: при использовании `compute` не выполняйте внутри него длительных или подвешивающих операций; в данном примере внутри `compute` только создаётся `RequestEntry` с `Deferred`, а ожидание (`await`) и тяжёлая работа происходят вне `compute`.

---

## Истечение По Времени (Time-Based Expiration)

### Автоочистка Устаревших Записей

Чтобы карта не росла безгранично, можно истекать записи по времени. Используем отдельный конфиг для expiring-коалесера:

```kotlin
data class ExpiringCoalescerConfig(
    val maxEntryAge: Long = 60_000,      // 1 минута
    val cleanupInterval: Long = 10_000,  // 10 секунд
    val timeoutMs: Long = 30_000
)

class ExpiringRequestCoalescer<K, V>(
    private val config: ExpiringCoalescerConfig
) {
    private val inFlightRequests = ConcurrentHashMap<K, RequestEntry<V>>()
    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    private val cleanupJob: Job = scope.launch {
        while (isActive) {
            delay(config.cleanupInterval)
            cleanupExpired()
        }
    }

    private fun cleanupExpired() {
        val now = System.currentTimeMillis()
        inFlightRequests.forEach { (key, entry) ->
            if (!entry.isActive() && now - entry.createdAt > config.maxEntryAge) {
                inFlightRequests.remove(key, entry)
            }
        }
    }

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): V = coroutineScope {
        val entry = inFlightRequests.compute(key) { _, existing ->
            if (existing != null && existing.isActive() && existing.age() < config.maxEntryAge) {
                existing.incrementWaiters()
                existing
            } else {
                RequestEntry(
                    deferred = async {
                        try {
                            if (config.timeoutMs > 0) {
                                withTimeout(config.timeoutMs) { operation() }
                            } else {
                                operation()
                            }
                        } finally {
                            // Очистка через waiters и периодический cleanup
                        }
                    },
                    createdAt = System.currentTimeMillis()
                )
            }
        }!!

        try {
            entry.deferred.await()
        } finally {
            entry.decrementWaiters()
            if (!entry.hasWaiters() && !entry.isActive()) {
                inFlightRequests.remove(key, entry)
            }
        }
    }

    fun close() {
        cleanupJob.cancel()
        inFlightRequests.clear()
    }
}
```

---

## Батчинг Против Объединения Запросов

### Сравнение

```kotlin
// Coalescing: несколько идентичных (по ключу) запросов → одно выполнение
// Batching: несколько разных ключей → один батчевый вызов к бэкенду
```

### Request Batching (упрощённый пример)

```kotlin
class RequestBatcher<K, V>(
    private val scope: CoroutineScope,
    private val batchSize: Int = 10,
    private val batchTimeout: Long = 100
) {
    private val mutex = Mutex()
    private val pending = LinkedHashMap<K, CompletableDeferred<V>>()

    suspend fun execute(
        key: K,
        batchOperation: suspend (List<K>) -> Map<K, V>
    ): V {
        val deferred = CompletableDeferred<V>()

        val existing = mutex.withLock {
            val existingDeferred = pending[key]
            if (existingDeferred != null) {
                // Уже есть запрос для этого ключа — просто возвращаем его
                return@withLock existingDeferred
            }

            pending[key] = deferred
            if (pending.size >= batchSize || pending.size == 1) {
                // Запускаем батч, если достигли размера или это первый элемент
                scope.launch { launchBatch(batchOperation) }
            }

            deferred
        }

        return existing.await()
    }

    private suspend fun launchBatch(
        batchOperation: suspend (List<K>) -> Map<K, V>
    ) {
        delay(batchTimeout)

        val batch: Map<K, CompletableDeferred<V>> = mutex.withLock {
            if (pending.isEmpty()) return
            val copy = LinkedHashMap(pending)
            pending.clear()
            copy
        }

        try {
            val result = batchOperation(batch.keys.toList())
            batch.forEach { (key, deferred) ->
                val value = result[key]
                if (value != null) {
                    deferred.complete(value)
                } else {
                    deferred.completeExceptionally(
                        IllegalStateException("No result for key: $key")
                    )
                }
            }
        } catch (e: Exception) {
            batch.values.forEach { it.completeExceptionally(e) }
        }
    }
}
```

---

## Объединение На Основе `SharedFlow`

### Для Подписок И Стримов (один процесс)

```kotlin
class SharedFlowCoalescer<K, V>(
    private val scope: CoroutineScope
) {
    private val flows = ConcurrentHashMap<K, MutableSharedFlow<V>>()

    fun observe(
        key: K,
        producer: Flow<V>
    ): Flow<V> {
        val shared = flows.getOrPut(key) {
            MutableSharedFlow<V>(
                replay = 1,
                onBufferOverflow = BufferOverflow.DROP_OLDEST
            ).also { sharedFlow ->
                scope.launch {
                    try {
                        producer.collect { value ->
                            sharedFlow.emit(value)
                        }
                    } finally {
                        flows.remove(key)
                    }
                }
            }
        }

        return shared.asSharedFlow()
    }
}
```

Здесь `SharedFlow` используется для разделения одного источника данных по ключу между несколькими подписчиками. Важно использовать корректный долгоживущий `CoroutineScope`, чтобы избежать утечек.

---

## Реальные Примеры

### Пример 1: UserRepository С Кэшем И Coalescing

```kotlin
class UserRepository(
    private val api: UserApi,
    private val cache: UserCache,
    private val coalescer: RequestCoalescer<String, User>
) {
    suspend fun getUser(userId: String): User {
        cache.get(userId)?.let { return it }

        return coalescer.execute(userId) {
            val user = api.getUser(userId)
            cache.put(userId, user)
            user
        }
    }
}

class ProfileScreen : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            // Все вызовы схлопываются в один сетевой запрос
            val user1 = userRepository.getUser(userId)
            val user2 = userRepository.getUser(userId)
            val user3 = userRepository.getUser(userId)
            val user4 = userRepository.getUser(userId)
        }
    }
}
```

### Пример 2: Дедупликация Загрузки Изображений

```kotlin
class ImageLoader(
    private val httpClient: HttpClient,
    private val coalescer: RequestCoalescer<String, Bitmap>
) {
    suspend fun loadImage(url: String): Bitmap = coalescer.execute(url) {
        httpClient.get(url).use { response ->
            BitmapFactory.decodeStream(response.bodyStream())
        }
    }
}

class ImageAdapter(
    private val imageLoader: ImageLoader
) : RecyclerView.Adapter<ImageViewHolder>() {
    override fun onBindViewHolder(holder: ImageViewHolder, position: Int) {
        val imageUrl = items[position].imageUrl
        holder.scope.launch {
            val bitmap = imageLoader.loadImage(imageUrl)
            holder.imageView.setImageBitmap(bitmap)
        }
    }
}
```

### Пример 3: GraphQLRepository С Ключом-запросом

```kotlin
class GraphQLRepository(
    private val client: GraphQLClient,
    private val coalescer: RequestCoalescer<GraphQLQuery, GraphQLResponse>
) {
    suspend fun query(query: GraphQLQuery): GraphQLResponse {
        return coalescer.execute(query) {
            client.execute(query)
        }
    }
}
```

---

## Преимущества Производительности

### Набросок Бенчмарка

```kotlin
@Test
fun benchmarkCoalescing() = runBlocking {
    val api = MockApi(latency = 100)
    val coalescedRepository = UserRepository(api, cache = InMemoryCache(), coalescer = RequestCoalescer())
    val regularRepository = UserRepository(api, cache = InMemoryCache(), coalescer = object : RequestCoalescer<String, User>({}) {}) // псевдо-пример без коалесинга

    val concurrentRequests = 100
    val userId = "test-user"

    // БЕЗ объединения (логика без использования коалесера должна вызывать API каждый раз)
    val withoutTime = measureTimeMillis {
        val jobs = List(concurrentRequests) {
            launch {
                api.getUser(userId)
            }
        }
        jobs.joinAll()
    }

    println("Without coalescing: ${withoutTime}ms")

    // С объединением
    api.reset()
    val withTime = measureTimeMillis {
        val jobs = List(concurrentRequests) {
            launch {
                coalescedRepository.getUser(userId)
            }
        }
        jobs.joinAll()
    }

    println("With coalescing: ${withTime}ms")
}
```

Идея: при большом числе параллельных идентичных запросов стоимость должна приближаться к одному вызову. В реальном коде важно явно разделить варианты с/без коалесинга, чтобы сравнение было корректным.

---

## Комбинация С In-memory Кэшем

### Двухуровневая Схема: Кэш + Coalescer

```kotlin
class OptimizedRepository<K, V>(
    private val api: Api<K, V>,
    private val memoryCache: LruCache<K, CacheEntry<V>>,
    private val coalescer: RequestCoalescer<K, V>,
    private val cacheTtl: Long = 5 * 60 * 1000
) {
    suspend fun get(key: K): V {
        val cached = memoryCache.get(key)
        if (cached != null && !cached.isExpired(cacheTtl)) {
            return cached.value
        }

        return coalescer.execute(key) {
            val value = api.fetch(key)
            memoryCache.put(key, CacheEntry(value, System.currentTimeMillis()))
            value
        }
    }
}

data class CacheEntry<V>(
    val value: V,
    val timestamp: Long
) {
    fun isExpired(ttl: Long): Boolean = System.currentTimeMillis() - timestamp > ttl
}
```

---

## Тестирование Объединения

### Примеры Юнит-тестов

```kotlin
class RequestCoalescerTest {
    private lateinit var coalescer: RequestCoalescer<String, String>

    @Before
    fun setup() {
        coalescer = RequestCoalescer()
    }

    @Test
    fun `coalesces concurrent identical requests`() = runTest {
        var executionCount = 0

        val operation: suspend () -> String = {
            delay(100)
            executionCount++
            "result"
        }

        val results = List(10) {
            async { coalescer.execute("key1", operation) }
        }.awaitAll()

        assertEquals(10, results.size)
        assertTrue(results.all { it == "result" })
        assertEquals(1, executionCount)
    }

    @Test
    fun `does not coalesce different keys`() = runTest {
        var executionCount = 0

        val operation: suspend () -> String = {
            delay(50)
            executionCount++
            "result"
        }

        val results = listOf(
            async { coalescer.execute("key1", operation) },
            async { coalescer.execute("key2", operation) },
            async { coalescer.execute("key3", operation) }
        ).awaitAll()

        assertEquals(3, results.size)
        assertEquals(3, executionCount)
    }

    @Test
    fun `propagates failures to all waiters`() = runTest {
        val failing = ResilientRequestCoalescer<String, String>()

        val operation: suspend () -> String = {
            delay(50)
            throw IOException("Network error")
        }

        val results = List(5) {
            async { failing.execute("key1", operation) }
        }.awaitAll()

        assertTrue(results.all { it.isFailure })
    }
}
```

---

## Продакшн-сценарии

- Подсказки поиска: debounce + coalescing для одинаковых запросов.
- Загрузка метаданных: схлопывание одновременных запросов по одному ключу.
- Стриминг/real-time: одна подписка на ключ, несколько подписчиков.

---

## Паттерны Интеграции

При интеграции с библиотеками загрузки данных (Glide, Coil и т.п.) используйте коалесер внутри fetcher/loader, чтобы не дублировать сетевую работу. Важно:
- применять долгоживущий `CoroutineScope`;
- избегать утечек и зависимостей от UI-состояния.

---

## Лучшие Практики

Делать:
1. Использовать для дорогих, идемпотентных, безопасных операций.
2. Формировать точный ключ (все параметры, влияющие на результат).
3. Явно обрабатывать ошибки; все ожидающие получают один и тот же исход.
4. Отслеживать метрики: доля коалесированных запросов, экономия, латентность.
5. Ставить разумные таймауты.

Не делать:
1. Не объединять неидемпотентные операции (платежи, записи и т.п.).
2. Не забывать про очистку, чтобы избежать утечек.
3. Не использовать слишком широкие ключи.
4. Не выполнять тяжёлую работу внутри операций `ConcurrentHashMap`.

---

## Мониторинг И Метрики

```kotlin
data class CoalescerStats(
    val totalRequests: Long,
    val coalescedRequests: Long,
    val uniqueRequests: Long,
    val failedRequests: Long,
    val coalescingRate: Double,
    val savingsRate: Double,
    val averageDuration: Double
)
```

Рекомендуется отслеживать до/после по количеству вызовов, латентности и загрузке CPU, чтобы подтвердить эффект.

---

## Типичные Ошибки

- Объединение неидемпотентных операций (например, платежей).
- Отсутствие удаления завершённых записей → утечки памяти.
- Игнорирование отмены корутин → висящие записи.
- Долгие или блокирующие операции внутри операций над `ConcurrentHashMap`.

---

## Дополнительные Вопросы

1. В чём разница между объединением запросов и кэшированием на уровне клиента/сервера?
2. Как правильно распространять ошибки на всех участников объединённого запроса?
3. Как выбирать стратегию TTL и истечения для in-flight и кэшированных данных?
4. Как сравнить и совместить coalescing и batching в одном сервисе?
5. Как реализовать объединение запросов между процессами или сервисами (распределённая координация)?
6. Как проектировать и интерпретировать метрики эффективности коалесинга?

---

## Ссылки

- [[c-kotlin]]
- [[c-coroutines]]

---

## Связанные Вопросы

- [[q-job-vs-supervisorjob--kotlin--medium]]

---

## Answer (EN)

Below is the English version with full detail, aligned with the Russian section.

---

## Table of Contents

- [Overview](#overview)
- [Pattern Definition](#pattern-definition)
- [Problem Scenario](#problem-scenario)
- [Solution Architecture](#solution-architecture)
- [Thread-Safe Implementation with ConcurrentHashMap](#thread-safe-implementation-with-concurrenthashmap)
- [Alternative Implementation with Mutex](#alternative-implementation-with-mutex)
- [Complete RequestCoalescer Class](#complete-requestcoalescer-class)
- [Time-Based Expiration](#time-based-expiration)
- [Request Batching vs Coalescing](#request-batching-vs-coalescing)
- [SharedFlow-Based Coalescing](#sharedflow-based-coalescing)
- [Real Examples](#real-examples)
- [Performance Benefits](#performance-benefits)
- [Combining with Memory Cache](#combining-with-memory-cache)
- [Testing Coalescing](#testing-coalescing)
- [Production Use Cases](#production-use-cases)
- [Integration Patterns](#integration-patterns)
- [Best Practices](#best-practices)
- [Monitoring and Metrics](#monitoring-and-metrics)
- [Common Pitfalls](#common-pitfalls)
- [Follow-ups](#follow-ups)
- [References](#references)
- [Related Questions](#related-questions)

---

## Overview

Request coalescing (also called request deduplication or request collapsing) is an optimization technique that combines multiple concurrent requests for the same resource into a single backend call.

Key benefits:
- Reduces backend load significantly (often several times, sometimes 10-100x)
- Improves response times (all requesters get the same result)
- Helps mitigate thundering herd / cache stampede
- Reduces network bandwidth usage
- Improves cache hit rates

When to use:
- Multiple components requesting the same data simultaneously
- High-traffic endpoints with identical or key-equivalent requests
- Expensive operations (database queries, API calls)
- Real-time data subscriptions

---

## Pattern Definition

### What is Request Coalescing?

```text
WITHOUT Coalescing:
     Request 1
  Client
    A

     Request 2
  Client   Backend
    B

     Request 3
  Client
    C

Result: 3 identical backend calls

WITH Coalescing:

  Client
    A

     Single
  Client  Request Backend
    B

  Client
    C

Result: 1 backend call, 3 clients get result
```

### Core Concepts

1. In-Flight Tracking: Keep track of ongoing requests.
2. Deferred Sharing: Share `Deferred<T>` among concurrent requesters.
3. Key-Based Deduplication: Use unique keys to identify identical requests.
4. Result Broadcasting: All waiters receive the same result.
5. Cleanup: Remove completed requests from the tracking map.

---

## Problem Scenario

### Scenario: User Profile Loading

```kotlin
// PROBLEM: Multiple components load the same user profile
class UserProfileScreen : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // Component 1: Header loads user
        userRepository.getUser(userId) // API call 1

        // Component 2: Avatar loads user
        userRepository.getUser(userId) // API call 2

        // Component 3: Stats load user
        userRepository.getUser(userId) // API call 3

        // Component 4: Actions load user
        userRepository.getUser(userId) // API call 4
    }
}

// Result: 4 identical API calls in rapid succession!
// Backend receives 4x load
// All calls compete for network/CPU
```

### Real-World Impact

```kotlin
// Example metrics from a production app (illustrative):

// WITHOUT coalescing:
// - 10,000 user profile requests/minute
// - Average 3 duplicate requests per user
// - Total backend calls: 30,000/minute
// - Backend CPU: 85%
// - P95 latency: 450ms

// WITH coalescing:
// - 10,000 user profile requests/minute
// - Deduplicated to: 3,500/minute
// - Backend CPU: 30%
// - P95 latency: 120ms
```

---

## Solution Architecture

```kotlin
class RequestCoalescer<K, V> {
    // Track in-flight requests
    private val inFlightRequests = ConcurrentHashMap<K, Deferred<V>>()

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): V = coroutineScope {
        // Fast-path: if a request is already in flight, await it
        val existingRequest = inFlightRequests[key]
        if (existingRequest != null && existingRequest.isActive) {
            return@coroutineScope existingRequest.await()
        }

        // Start new request
        val deferred = async {
            try {
                operation()
            } finally {
                inFlightRequests.remove(key)
            }
        }

        // Possible race here; safe implementations use putIfAbsent / compute
        inFlightRequests[key] = deferred

        deferred.await()
    }
}
```

---

## Thread-Safe Implementation with ConcurrentHashMap

```kotlin
class RequestCoalescer<K, V> {
    private val inFlightRequests = ConcurrentHashMap<K, Deferred<V>>()

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): V = coroutineScope {
        // First, try to reuse an active in-flight request
        inFlightRequests[key]?.takeIf { it.isActive }?.let { existing ->
            return@coroutineScope existing.await()
        }

        // Create a new deferred in this scope
        val newDeferred = async {
            try {
                operation()
            } finally {
                // Inside async, "this" refers to the Deferred instance
                inFlightRequests.remove(key, this)
            }
        }

        // Try to publish it; if another coroutine won, use theirs instead
        val winner = inFlightRequests.putIfAbsent(key, newDeferred)
        val actual = (winner?.takeIf { it.isActive } ?: newDeferred)

        if (actual !== newDeferred) {
            // Lost the race; cancel our own deferred and await the winner
            newDeferred.cancel()
        }

        actual.await()
    }
}
```

### Handling Failures with Shared Result

```kotlin
class ResilientRequestCoalescer<K, V> {
    private val inFlightRequests = ConcurrentHashMap<K, Deferred<Result<V>>>()

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): Result<V> = coroutineScope {
        // Try to reuse existing
        inFlightRequests[key]?.takeIf { it.isActive }?.let { existing ->
            return@coroutineScope existing.await()
        }

        val newDeferred = async {
            try {
                Result.success(operation())
            } catch (e: Exception) {
                Result.failure(e)
            } finally {
                inFlightRequests.remove(key, this)
            }
        }

        val winner = inFlightRequests.putIfAbsent(key, newDeferred)
        val actual = (winner?.takeIf { it.isActive } ?: newDeferred)

        if (actual !== newDeferred) {
            newDeferred.cancel()
        }

        actual.await()
    }
}
```

Note: Do not run long or suspending work inside `ConcurrentHashMap.compute`/`putIfAbsent` lambdas; here we only create `Deferred` synchronously, and `await` happens outside.

---

## Alternative Implementation with Mutex

```kotlin
class MutexRequestCoalescer<K, V> {
    private val inFlightRequests = mutableMapOf<K, Deferred<V>>()
    private val mutex = Mutex()

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): V = coroutineScope {
        // Fast path under lock
        mutex.withLock {
            inFlightRequests[key]?.takeIf { it.isActive }?.let { existing ->
                return@coroutineScope existing.await()
            }
        }

        // Create candidate deferred in this scope
        val newDeferred = async {
            try {
                operation()
            } finally {
                mutex.withLock {
                    inFlightRequests.remove(key, this)
                }
            }
        }

        // Publish under lock with double-check
        val actual = mutex.withLock {
            val existing = inFlightRequests[key]?.takeIf { it.isActive }
            if (existing != null) {
                newDeferred.cancel()
                existing
            } else {
                inFlightRequests[key] = newDeferred
                newDeferred
            }
        }

        actual.await()
    }
}
```

---

## Complete RequestCoalescer Class

(Production-style implementation as in RU section.)

---

## Time-Based Expiration

(Time-based expiration implementation mirrored from RU section.)

---

## Request Batching Vs Coalescing

```kotlin
// Coalescing: multiple identical (by key) requests -> single execution
// Batching: multiple different keys -> single batched backend call
```

### Request Batching (simplified example)

```kotlin
class RequestBatcher<K, V>(
    private val scope: CoroutineScope,
    private val batchSize: Int = 10,
    private val batchTimeout: Long = 100
) {
    private val mutex = Mutex()
    private val pending = LinkedHashMap<K, CompletableDeferred<V>>()

    suspend fun execute(
        key: K,
        batchOperation: suspend (List<K>) -> Map<K, V>
    ): V {
        val deferred = CompletableDeferred<V>()

        val existing = mutex.withLock {
            val existingDeferred = pending[key]
            if (existingDeferred != null) {
                // Already have an entry for this key; reuse it
                return@withLock existingDeferred
            }

            pending[key] = deferred
            if (pending.size >= batchSize || pending.size == 1) {
                // Start a batch when first item arrives or limit reached
                scope.launch { launchBatch(batchOperation) }
            }

            deferred
        }

        return existing.await()
    }

    private suspend fun launchBatch(
        batchOperation: suspend (List<K>) -> Map<K, V>
    ) {
        delay(batchTimeout)

        val batch: Map<K, CompletableDeferred<V>> = mutex.withLock {
            if (pending.isEmpty()) return
            val copy = LinkedHashMap(pending)
            pending.clear()
            copy
        }

        try {
            val result = batchOperation(batch.keys.toList())
            batch.forEach { (key, deferred) ->
                val value = result[key]
                if (value != null) {
                    deferred.complete(value)
                } else {
                    deferred.completeExceptionally(
                        IllegalStateException("No result for key: $key")
                    )
                }
            }
        } catch (e: Exception) {
            batch.values.forEach { it.completeExceptionally(e) }
        }
    }
}
```

---

## SharedFlow-Based Coalescing

```kotlin
class SharedFlowCoalescer<K, V>(
    private val scope: CoroutineScope
) {
    private val flows = ConcurrentHashMap<K, MutableSharedFlow<V>>()

    fun observe(
        key: K,
        producer: Flow<V>
    ): Flow<V> {
        val shared = flows.getOrPut(key) {
            MutableSharedFlow<V>(
                replay = 1,
                onBufferOverflow = BufferOverflow.DROP_OLDEST
            ).also { sharedFlow ->
                scope.launch {
                    try {
                        producer.collect { value ->
                            sharedFlow.emit(value)
                        }
                    } finally {
                        flows.remove(key)
                    }
                }
            }
        }

        return shared.asSharedFlow()
    }
}
```

---

## Real Examples

(Examples of UserRepository, ImageLoader, GraphQLRepository as in RU section.)

---

## Performance Benefits

(Benchmark sketch aligned with RU explanation; ensure real implementation clearly separates with/without coalescing.)

---

## Combining with Memory Cache

(OptimizedRepository and CacheEntry as in RU section.)

---

## Testing Coalescing

(Tests as in RU section.)

---

## Production Use Cases

- Search suggestions: debounce + coalescing for identical queries.
- Metadata loading: coalescing concurrent lookups by key.
- Streaming/real-time: single subscription per key, multiple subscribers.

---

## Integration Patterns

When integrating with loaders/fetchers (e.g., Glide, Coil), use a coalescer internally to avoid duplicate network work. Use an appropriate long-lived scope and avoid leaking UI scopes.

---

## Best Practices

Do:
1. Use for expensive, idempotent, side-effect-free operations.
2. Build precise keys including all parameters.
3. Handle errors explicitly; all coalesced callers see a consistent outcome.
4. Track metrics: coalescing ratio, savings, latency.
5. Use reasonable timeouts.

Don't:
1. Coalesce non-idempotent operations (payments, writes, etc.).
2. Forget to clean up completed entries.
3. Use overly broad keys.
4. Run blocking work inside concurrent map operations.

---

## Monitoring and Metrics

```kotlin
data class CoalescerStats(
    val totalRequests: Long,
    val coalescedRequests: Long,
    val uniqueRequests: Long,
    val failedRequests: Long,
    val coalescingRate: Double,
    val savingsRate: Double,
    val averageDuration: Double
)
```

---

## Common Pitfalls

- Coalescing non-idempotent operations.
- Not removing completed entries (memory leaks).
- Ignoring coroutine cancellation.
- Doing heavy or blocking work inside `ConcurrentHashMap` operations.

---

## Follow-ups

1. What is the difference between request coalescing and client/server-side caching?
2. How should failures be propagated to all coalesced callers?
3. How to choose TTL/expiration strategies for in-flight and cached data?
4. How to combine coalescing and batching in the same system?
5. How would you design cross-process or cross-service coalescing?
6. Which metrics would you track to demonstrate coalescing effectiveness?

---

## References

- [[c-kotlin]]
- [[c-coroutines]]

---

## Related Questions

- [[q-job-vs-supervisorjob--kotlin--medium]]
