---
id: kotlin-191
title: "Retry and exponential Backoff Patterns in Flow / Retry и exponential backoff паттерны в Flow"
aliases: [Error Handling, Exponential Backoff, Resilience, Retry, Retry Patterns]
topic: kotlin
subtopics: [coroutines, flow]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-flow, c-kotlin, q-advanced-coroutine-patterns--kotlin--hard]
created: 2025-10-15
updated: 2025-11-09
tags: [circuit-breaker, coroutines, difficulty/medium, error-handling, exponential-backoff, flow, kotlin, production, resilience, retry]
---
# Вопрос (RU)
> Как реализовать retry логику с экспоненциальным backoff в Kotlin `Flow`? Объясните операторы `retry()` и `retryWhen()`, кастомные retry политики, jitter, интеграцию с circuit breaker и стратегии тестирования. Приведите production-ready примеры для сетевых запросов, операций с БД и устойчивых потоков данных.

# Question (EN)
> How do you implement retry logic with exponential backoff in Kotlin `Flow`? Explain the `retry()` and `retryWhen()` operators, custom retry policies, jitter, circuit breaker integration, and testing strategies. Provide production-ready examples for network requests, database operations, and resilient data streams.

## Ответ (RU)

**Retry** паттерны критически важны для создания устойчивых приложений, которые могут восстанавливаться после временных сбоев. **Exponential backoff** — это стратегия, при которой задержки повторных попыток увеличиваются экспоненциально, чтобы избежать перегрузки падающих сервисов.

#### 1. Базовый Retry С Оператором `retry()`

**Оператор `retry()`:**
- Повторяет `Flow` при возникновении исключения
- Опционально ограничивает количество попыток
- НЕ добавляет задержку между повторами (немедленный retry)

Важно: `retry(retries = N)` использует индекс `attempt`, начиная с 0, и может выполнить до `N + 1` запусков (первоначальный + N повторов), пока предикат возвращает true.

**Простой retry (исправлено):**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import java.io.IOException

fun getData(): Flow<String> {
    var attempt = 0
    return flow {
        println("Попытка ${++attempt}")
        if (attempt < 3) {
            throw IOException("Ошибка сети")
        }
        emit("Успех")
    }
}

suspend fun basicRetryExample() {
    getData()
        .retry(retries = 3) // До 3 повторов (4 попытки всего), пока ошибка удовлетворяет условиям
        .collect { data ->
            println("Получено: $data")
        }
}

// Возможный вывод, если первые 2 попытки падают, а 3-я успешна:
// Попытка 1
// Попытка 2
// Попытка 3
// Получено: Успех
```

**Retry с предикатом:**

```kotlin
suspend fun retryWithPredicateExample() {
    getData()
        .retry(3) { cause ->
            // Повторяем только для IOException, не для IllegalStateException
            cause is IOException
        }
        .collect { data ->
            println("Получено: $data")
        }
}
```

#### 2. Продвинутый Retry С `retryWhen()`

**Оператор `retryWhen()`:**
- Больше контроля над retry логикой
- Можно добавлять задержки между повторами
- Доступ к счетчику попыток и исключению

**Базовый `retryWhen`:**

```kotlin
import java.io.IOException

suspend fun retryWhenExample() {
    flow {
        println("Попытка загрузить данные...")
        throw IOException("Ошибка сети")
    }
        .retryWhen { cause, attempt ->
            // attempt == 0 для первой повторной попытки
            if (cause is IOException && attempt < 3) {
                delay(1000 * (attempt + 1)) // Линейный backoff
                true // Повторить
            } else {
                false // Не повторять
            }
        }
        .catch { e ->
            println("Не удалось после повторов: ${e.message}")
        }
        .collect()
}
```

**`retryWhen` vs `retry`:**

| Функция | `retry()` | `retryWhen()` |
|---------|-----------|---------------|
| Задержка | Нет (немедленно) | Да (ручная `delay`) |
| Счетчик попыток | Недоступен | Доступен |
| Условная логика | Базовый предикат | Полный контроль |
| Лучше для | Простого retry | Кастомных backoff стратегий |

#### 3. Реализация Exponential Backoff

**Алгоритм exponential backoff:**
- Задержка увеличивается экспоненциально: 1s, 2s, 4s, 8s, 16s...
- Формула: `delay = initialDelay * (multiplier ^ attempt)`
- Предотвращает перегрузку падающих сервисов

**Базовый exponential backoff:**

```kotlin
import kotlin.math.pow
import java.io.IOException

suspend fun exponentialBackoffExample() {
    val initialDelayMs = 1000L
    val multiplier = 2.0
    val maxAttempts = 5L

    flow {
        println("Загрузка данных...")
        throw IOException("Ошибка сети")
    }
        .retryWhen { cause, attempt ->
            if (cause is IOException && attempt < maxAttempts) {
                val delayMs = (initialDelayMs * multiplier.pow(attempt.toDouble())).toLong()
                println("Повтор ${attempt + 1}/$maxAttempts через ${delayMs}мс")
                delay(delayMs)
                true
            } else {
                false
            }
        }
        .catch { e ->
            println("Не удалось после $maxAttempts попыток: ${e.message}")
        }
        .collect()
}

// Пример вывода:
// Загрузка данных...
// Повтор 1/5 через 1000мс
// Загрузка данных...
// Повтор 2/5 через 2000мс
// Загрузка данных...
// Повтор 3/5 через 4000мс
// ...
```

**Production-ready exponential backoff:**

```kotlin
import kotlin.math.pow
import kotlin.random.Random
import kotlinx.coroutines.flow.retryWhen

data class RetryConfig(
    val maxAttempts: Int = 5,
    val initialDelayMs: Long = 1000,
    val maxDelayMs: Long = 32000,
    val multiplier: Double = 2.0,
    val jitterFactor: Double = 0.1
)

fun <T> Flow<T>.retryWithExponentialBackoff(
    config: RetryConfig = RetryConfig(),
    predicate: (Throwable) -> Boolean = { true }
): Flow<T> = retryWhen { cause, attempt ->
    if (predicate(cause) && attempt < config.maxAttempts) {
        val baseDelay = (config.initialDelayMs * config.multiplier.pow(attempt.toDouble()))
            .toLong()
            .coerceAtMost(config.maxDelayMs)

        // Добавляем jitter (случайность) для предотвращения thundering herd
        val jitter = (baseDelay * config.jitterFactor * Random.nextDouble(-1.0, 1.0)).toLong()
        val delayMs = (baseDelay + jitter).coerceAtLeast(0)

        println("Повтор ${attempt + 1}/${config.maxAttempts} через ${delayMs}мс (причина: ${cause.message})")
        delay(delayMs)
        true
    } else {
        false
    }
}

// Использование
import retrofit2.HttpException

suspend fun retryWithConfigExample() {
    getDataFromApi()
        .retryWithExponentialBackoff(
            config = RetryConfig(
                maxAttempts = 5,
                initialDelayMs = 1000,
                maxDelayMs = 30000,
                multiplier = 2.0,
                jitterFactor = 0.1
            ),
            predicate = { it is IOException || it is HttpException }
        )
        .collect { data ->
            println("Успех: $data")
        }
}
```

#### 4. Jitter Для Времени Retry

**Зачем jitter?**
- Предотвращает проблему **thundering herd**
- Многие клиенты не повторяют запросы в одно и то же время
- Более равномерно распределяет нагрузку

**Стратегии jitter:**

```kotlin
import kotlin.random.Random
import kotlin.math.pow

// 1. Full jitter: случайная задержка от 0 до рассчитанной задержки
fun calculateFullJitter(baseDelay: Long): Long {
    return (baseDelay * Random.nextDouble()).toLong()
}

// 2. Equal jitter: половина базовой задержки + случайная половина
fun calculateEqualJitter(baseDelay: Long): Long {
    return (baseDelay / 2) + (baseDelay / 2 * Random.nextDouble()).toLong()
}

// 3. Decorrelated jitter: на основе предыдущей задержки
fun calculateDecorrelatedJitter(previousDelay: Long, baseDelay: Long): Long {
    return (baseDelay + (previousDelay * 3 * Random.nextDouble())).toLong()
}

// Пример с equal jitter
fun <T> Flow<T>.retryWithJitter(
    maxAttempts: Int = 5,
    initialDelayMs: Long = 1000,
    maxDelayMs: Long = 32000
): Flow<T> = retryWhen { _, attempt ->
    if (attempt < maxAttempts) {
        val baseDelay = (initialDelayMs * (2.0.pow(attempt.toDouble())))
            .toLong()
            .coerceAtMost(maxDelayMs)

        // Equal jitter
        val delayMs = (baseDelay / 2) + (baseDelay / 2 * Random.nextDouble()).toLong()

        delay(delayMs)
        true
    } else {
        false
    }
}
```

#### 5. Production Пример: Сетевые Запросы

**Устойчивый API клиент:**

```kotlin
import kotlinx.coroutines.flow.*
import retrofit2.HttpException
import java.io.IOException

class ApiClient(private val api: ApiService) {

    // Retry конфигурация для разных типов запросов
    private val standardRetry = RetryConfig(
        maxAttempts = 3,
        initialDelayMs = 1000,
        maxDelayMs = 10000
    )

    private val longRetry = RetryConfig(
        maxAttempts = 5,
        initialDelayMs = 2000,
        maxDelayMs = 60000
    )

    fun getUser(userId: String): Flow<User> = flow {
        emit(api.getUser(userId))
    }
        .retryWithExponentialBackoff(
            config = standardRetry,
            predicate = ::isRetriableError
        )
        .catch { e ->
            // Обрабатываем неповторяемые ошибки (корректно пробрасываем или врапим)
            throw ApiException("Не удалось получить пользователя", e)
        }

    fun syncData(): Flow<SyncResult> = flow {
        emit(api.syncData())
    }
        .retryWithExponentialBackoff(
            config = longRetry,
            predicate = ::isRetriableError
        )
        .onEach { result ->
            println("Синхронизация завершена: $result")
        }

    fun searchUsers(query: String): Flow<List<User>> = flow {
        emit(api.searchUsers(query))
    }
        .timeout(5000) // Timeout каждой попытки через 5 секунд
        .retryWithExponentialBackoff(
            config = standardRetry,
            predicate = { it is IOException || it is TimeoutCancellationException }
        )

    private fun isRetriableError(error: Throwable): Boolean {
        return when (error) {
            // Сетевые ошибки - повторяем
            is IOException -> true

            // Timeout - повторяем
            is TimeoutCancellationException -> true

            // HTTP ошибки - проверяем статус-код
            is HttpException -> when (error.code()) {
                // 5xx ошибки сервера - повторяем
                in 500..599 -> true

                // 408 Request Timeout - повторяем
                408 -> true

                // 429 Too Many Requests - повторяем (в проде учитывать Retry-After)
                429 -> true

                // Другие 4xx клиентские ошибки - не повторяем
                else -> false
            }

            // Другие ошибки - не повторяем
            else -> false
        }
    }
}

// Использование
suspend fun fetchUserWithRetry(apiService: ApiService) {
    val apiClient = ApiClient(apiService)

    apiClient.getUser("user123")
        .onStart { println("Загрузка пользователя...") }
        .onEach { user -> println("Пользователь: ${user.name}") }
        .catch { e -> println("Ошибка: ${e.message}") }
        .collect()
}
```

#### 6. Production Пример: Операции С БД

**Устойчивые операции с базой данных с retry:**

```kotlin
import kotlinx.coroutines.flow.*
import android.database.sqlite.SQLiteException

class DatabaseRepository(private val database: AppDatabase) {

    fun insertWithRetry(item: Item): Flow<Long> = flow {
        emit(database.itemDao().insert(item))
    }
        .retryWhen { cause, attempt ->
            // Повторяем при блокировке БД (условие упрощено для примера)
            if (cause is SQLiteException && attempt < 3) {
                val delayMs = 100L * (attempt + 1)
                println("БД заблокирована, повтор ${attempt + 1} через ${delayMs}мс")
                delay(delayMs)
                true
            } else {
                false
            }
        }

    fun batchInsertWithRetry(items: List<Item>): Flow<Unit> = flow {
        database.withTransaction {
            items.forEach { item ->
                database.itemDao().insert(item)
            }
        }
        emit(Unit)
    }
        .retryWithExponentialBackoff(
            config = RetryConfig(
                maxAttempts = 3,
                initialDelayMs = 100,
                maxDelayMs = 1000
            ),
            predicate = { it is SQLiteException }
        )

    fun observeItemsWithRetry(userId: String): Flow<List<Item>> {
        return database.itemDao().observeItems(userId)
            .catch { e ->
                if (e is SQLiteException) {
                    // Отдаем пустой список при ошибке и даем retryWhen переинициализироваться
                    emit(emptyList())
                    delay(1000)
                    throw e
                }
            }
            .retryWhen { cause, attempt ->
                cause is SQLiteException && attempt < 5
            }
    }
}
```

#### 7. Комбинирование Retry С Timeout

**Паттерн Timeout + retry:**

```kotlin
suspend fun fetchDataWithTimeoutAndRetry() {
    flow {
        emit(fetchDataFromSlowApi())
    }
        .timeout(5000) // Timeout каждой попытки через 5 секунд
        .retryWithExponentialBackoff(
            config = RetryConfig(maxAttempts = 3)
        )
        .catch { e ->
            when (e) {
                is TimeoutCancellationException -> {
                    println("Все попытки превысили timeout")
                }
                else -> println("Не удалось: ${e.message}")
            }
        }
        .collect { data ->
            println("Успех: $data")
        }
}

// Timeout на одну попытку vs общий timeout
suspend fun fetchWithTotalTimeout() {
    withTimeout(15000) { // Общий timeout: 15 секунд
        flow {
            emit(fetchDataFromApi())
        }
            .timeout(5000) // Timeout на попытку: 5 секунд
            .retryWhen { cause, attempt ->
                if (cause is TimeoutCancellationException && attempt < 2) {
                    println("Попытка превысила timeout, повторяем...")
                    delay(1000)
                    true
                } else {
                    false
                }
            }
            .collect { data ->
                println("Успех: $data")
            }
    }
}
```

#### 8. Интеграция Circuit Breaker

**Circuit breaker с retry:**

```kotlin
enum class CircuitState {
    CLOSED,  // Нормальная работа
    OPEN,    // Падает, отклоняем запросы
    HALF_OPEN // Тестируем восстановление
}

class CircuitBreaker(
    private val failureThreshold: Int = 5,
    private val resetTimeoutMs: Long = 60000
) {
    private var state = CircuitState.CLOSED
    private var failureCount = 0
    private var lastFailureTime = 0L

    fun <T> protect(block: suspend () -> T): Flow<T> = flow {
        when (state) {
            CircuitState.OPEN -> {
                if (System.currentTimeMillis() - lastFailureTime >= resetTimeoutMs) {
                    state = CircuitState.HALF_OPEN
                    println("Circuit breaker: HALF_OPEN (тестирование)")
                } else {
                    throw CircuitBreakerOpenException("Circuit breaker OPEN")
                }
            }
            else -> { /* CLOSED или HALF_OPEN: разрешаем попытку */ }
        }

        try {
            val result = block()
            onSuccess()
            emit(result)
        } catch (e: Exception) {
            onFailure()
            throw e
        }
    }

    private fun onSuccess() {
        failureCount = 0
        if (state == CircuitState.HALF_OPEN) {
            state = CircuitState.CLOSED
            println("Circuit breaker: CLOSED (восстановлен)")
        }
    }

    private fun onFailure() {
        failureCount++
        lastFailureTime = System.currentTimeMillis()

        if (failureCount >= failureThreshold) {
            state = CircuitState.OPEN
            println("Circuit breaker: OPEN (слишком много сбоев)")
        }
    }
}

class CircuitBreakerOpenException(message: String) : Exception(message)

// Использование с retry
suspend fun fetchWithCircuitBreaker() {
    val circuitBreaker = CircuitBreaker(
        failureThreshold = 3,
        resetTimeoutMs = 30000
    )

    circuitBreaker.protect {
        fetchDataFromApi()
    }
        .retryWithExponentialBackoff(
            config = RetryConfig(maxAttempts = 3),
            predicate = { it !is CircuitBreakerOpenException }
        )
        .catch { e ->
            when (e) {
                is CircuitBreakerOpenException -> {
                    println("Circuit breaker открыт, не повторяем")
                }
                else -> println("Не удалось: ${e.message}")
            }
        }
        .collect { data ->
            println("Успех: $data")
        }
}
```

#### 9. Retry Для Разных Типов Исключений

**Разные стратегии для разных ошибок:**

```kotlin
import kotlin.reflect.KClass
import kotlin.math.pow

data class RetryStrategy(
    val maxAttempts: Int,
    val initialDelayMs: Long,
    val multiplier: Double = 2.0
)

fun <T> Flow<T>.retryByExceptionType(
    strategies: Map<KClass<out Throwable>, RetryStrategy>,
    defaultStrategy: RetryStrategy? = null
): Flow<T> = retryWhen { cause, attempt ->
    // Находим подходящую стратегию
    val strategy = strategies.entries
        .firstOrNull { (exceptionType, _) ->
            exceptionType.isInstance(cause)
        }?.value ?: defaultStrategy

    if (strategy != null && attempt < strategy.maxAttempts) {
        val delayMs = (strategy.initialDelayMs * strategy.multiplier.pow(attempt.toDouble()))
            .toLong()

        println("Повтор ${cause::class.simpleName} (${attempt + 1}/${strategy.maxAttempts}) через ${delayMs}мс")
        delay(delayMs)
        true
    } else {
        false
    }
}

// Использование
suspend fun fetchWithCustomStrategies() {
    getDataFromApi()
        .retryByExceptionType(
            strategies = mapOf(
                IOException::class to RetryStrategy(
                    maxAttempts = 5,
                    initialDelayMs = 1000,
                    multiplier = 2.0
                ),
                HttpException::class to RetryStrategy(
                    maxAttempts = 3,
                    initialDelayMs = 2000,
                    multiplier = 1.5
                ),
                TimeoutCancellationException::class to RetryStrategy(
                    maxAttempts = 2,
                    initialDelayMs = 5000,
                    multiplier = 1.0
                )
            ),
            defaultStrategy = RetryStrategy(
                maxAttempts = 1,
                initialDelayMs = 1000
            )
        )
        .collect { data ->
            println("Успех: $data")
        }
}
```

#### 10. Мониторинг И Логирование Попыток Retry

**Production мониторинг:**

```kotlin
interface RetryLogger {
    fun onRetryAttempt(attempt: Int, maxAttempts: Int, cause: Throwable, delayMs: Long)
    fun onRetryExhausted(attempts: Int, lastCause: Throwable)
    fun onRetrySuccess(totalAttempts: Int)
}

class ProductionRetryLogger(private val analyticsService: AnalyticsService) : RetryLogger {
    override fun onRetryAttempt(attempt: Int, maxAttempts: Int, cause: Throwable, delayMs: Long) {
        val event = mapOf(
            "event" to "retry_attempt",
            "attempt" to attempt,
            "max_attempts" to maxAttempts,
            "cause" to cause::class.simpleName,
            "delay_ms" to delayMs
        )
        analyticsService.logEvent(event)
        println("[RETRY] Попытка $attempt/$maxAttempts через ${delayMs}мс - ${cause.message}")
    }

    override fun onRetryExhausted(attempts: Int, lastCause: Throwable) {
        val event = mapOf(
            "event" to "retry_exhausted",
            "attempts" to attempts,
            "cause" to lastCause::class.simpleName
        )
        analyticsService.logEvent(event)
        println("[RETRY] Исчерпано после $attempts попыток - ${lastCause.message}")
    }

    override fun onRetrySuccess(totalAttempts: Int) {
        if (totalAttempts > 0) {
            val event = mapOf(
                "event" to "retry_success",
                "attempts" to totalAttempts
            )
            analyticsService.logEvent(event)
            println("[RETRY] Успех после $totalAttempts повторов")
        }
    }
}

fun <T> Flow<T>.retryWithLogging(
    config: RetryConfig,
    logger: RetryLogger,
    predicate: (Throwable) -> Boolean = { true }
): Flow<T> {
    var attemptCount = 0

    return this
        .retryWhen { cause, attempt ->
            attemptCount = attempt.toInt()

            if (predicate(cause) && attempt < config.maxAttempts) {
                val delayMs = calculateBackoff(config, attempt)
                logger.onRetryAttempt(
                    attempt = (attempt + 1).toInt(),
                    maxAttempts = config.maxAttempts,
                    cause = cause,
                    delayMs = delayMs
                )
                delay(delayMs)
                true
            } else {
                // Для простоты считаем ситуацию "исчерпанной",
                // как при достижении лимита, так и при неповторяемой ошибке
                logger.onRetryExhausted(attemptCount + 1, cause)
                false
            }
        }
        .onEach {
            if (attemptCount > 0) {
                logger.onRetrySuccess(attemptCount)
            }
        }
}

private fun calculateBackoff(config: RetryConfig, attempt: Long): Long {
    val baseDelay = (config.initialDelayMs * config.multiplier.pow(attempt.toDouble()))
        .toLong()
        .coerceAtMost(config.maxDelayMs)

    val jitter = (baseDelay * config.jitterFactor * Random.nextDouble(-1.0, 1.0)).toLong()
    return (baseDelay + jitter).coerceAtLeast(0)
}
```

#### 11. Тестирование Логики Retry

**Unit-тесты с виртуальным временем:**

```kotlin
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.test.runTest
import org.junit.Test
import kotlin.math.pow
import kotlin.test.assertEquals
import java.io.IOException
import kotlinx.coroutines.TimeoutCancellationException

class RetryTest {

    @Test
    fun `retry успешен после 2 попыток`() = runTest {
        var attempts = 0

        val flow = flow {
            attempts++
            if (attempts < 2) {
                throw IOException("Ошибка сети")
            }
            emit("Успех")
        }

        val result = flow
            .retry(retries = 3)
            .first()

        assertEquals("Успех", result)
        assertEquals(2, attempts)
    }

    @Test
    fun `exponential backoff имеет увеличивающиеся задержки`() = runTest {
        val delays = mutableListOf<Long>()
        var attempts = 0

        val flow = flow {
            attempts++
            throw IOException("Ошибка")
        }

        flow
            .retryWhen { _, attempt ->
                if (attempt < 3) {
                    val d = 1000L * (2.0.pow(attempt.toDouble())).toLong()
                    delays.add(d)
                    delay(d)
                    true
                } else {
                    false
                }
            }
            .catch { }
            .collect()

        // Проверяем экспоненциальные задержки: 1000, 2000, 4000
        assertEquals(listOf(1000L, 2000L, 4000L), delays)
        assertEquals(4, attempts)
    }

    @Test
    fun `retry только для конкретного типа исключения`() = runTest {
        var ioAttempts = 0
        var otherAttempts = 0

        val flow = flow {
            if (ioAttempts < 2) {
                ioAttempts++
                throw IOException("Ошибка сети")
            } else {
                otherAttempts++
                throw IllegalStateException("Некорректное состояние")
            }
        }

        try {
            flow
                .retry(5) { it is IOException }
                .collect()
        } catch (e: IllegalStateException) {
            // Ожидается
        }

        assertEquals(2, ioAttempts) // Повторили IOException дважды
        assertEquals(1, otherAttempts) // IllegalStateException не повторяли
    }

    @Test
    fun `retry с timeout`() = runTest {
        val flow = flow {
            delay(10000) // Имитация медленной операции
            emit("Данные")
        }

        var timeoutCount = 0

        flow
            .timeout(1000)
            .retryWhen { cause, attempt ->
                if (cause is TimeoutCancellationException && attempt < 2) {
                    timeoutCount++ // считаем повторы по причине timeout
                    delay(100)
                    true
                } else {
                    false
                }
            }
            .catch { }
            .collect()

        // Две повторные попытки были инициированы из-за timeout
        assertEquals(2, timeoutCount)
    }
}
```

#### 12. Резюме Лучших Практик

**Что делать:**

```kotlin
// Используйте exponential backoff для сетевых запросов
flow { fetchFromApi() }
    .retryWithExponentialBackoff()

// Добавляйте jitter для предотвращения thundering herd
.retryWithExponentialBackoff(
    config = RetryConfig(jitterFactor = 0.1)
)

// Устанавливайте максимальную задержку, чтобы избежать очень долгих ожиданий
RetryConfig(maxDelayMs = 60000)

// Повторяйте только повторяемые ошибки
.retry { it is IOException }

// Комбинируйте с timeout
.timeout(5000)
.retryWithExponentialBackoff()

// Логируйте попытки retry для мониторинга
.retryWithLogging(config, logger)
```

**Чего не делать:**

```kotlin
// Не повторяйте немедленно без задержки
.retry(10) // Молотит сервер

// Не повторяйте бесконечно
.retry(Long.MAX_VALUE) // Никогда не сдается

// Не повторяйте неповторяемые ошибки
.retry { true } // Повторяет всё

// Не забывайте максимальную задержку
RetryConfig(multiplier = 10.0) // Может привести к ожиданию часами

// Не игнорируйте исключения после retry
.retry(3)
// Отсутствует .catch { }
```

### Связанные Вопросы
- [[c-kotlin]] - Концепции Kotlin
- [[c-flow]] - Концепции `Flow`

### Дополнительные Вопросы
1. Как exponential backoff с jitter предотвращает проблему thundering herd? Приведите математическое объяснение.
2. В чем разница между `retry()` на уровне `Flow` и retry логикой в репозитории? Когда выбирать каждый подход?
3. Как реализовать retry политику, которая делает backoff на основе заголовков ответа сервера (например, `Retry-After`)?
4. Объясните, как тестировать retry логику с виртуальным временем без реального ожидания задержек.
5. Как балансировать между агрессивностью retry и избеганием перегрузки сервера в production?
6. Какая связь между circuit breaker, retry и timeout паттернами? Как они дополняют друг друга?
7. Как реализовать retry с разными стратегиями для разных HTTP статус кодов (например, retry 503, не retry 400)?

### Ссылки
- [Обработка исключений Flow](https://kotlinlang.org/docs/flow.html#flow-exceptions)
- [Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
- [Retry Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/retry)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)

## Answer (EN)

**Retry** patterns are essential for building resilient applications that can recover from transient failures. **Exponential backoff** is a strategy where retry delays increase exponentially to avoid overwhelming failing services.

#### 1. Basic Retry with `retry()` Operator

**`retry()` operator:**
- Retries the `Flow` on exception
- Optionally limits number of attempts
- Does NOT add delay between retries (immediate retry)

Important: `retry(retries = N)` uses the `attempt` index starting at 0. It allows up to `N + 1` total executions (initial + N retries) while the predicate returns true.

**Simple retry (corrected):**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import java.io.IOException

fun getData(): Flow<String> {
    var attempt = 0
    return flow {
        println("Attempt ${++attempt}")
        if (attempt < 3) {
            throw IOException("Network error")
        }
        emit("Success")
    }
}

suspend fun basicRetryExample() {
    getData()
        .retry(retries = 3) // Up to 3 retries (4 attempts total) if exceptions keep matching
        .collect { data ->
            println("Received: $data")
        }
}

// Possible output when first 2 attempts fail and 3rd succeeds:
// Attempt 1
// Attempt 2
// Attempt 3
// Received: Success
```

**Retry with predicate:**

```kotlin
suspend fun retryWithPredicateExample() {
    getData()
        .retry(3) { cause ->
            // Only retry on IOException, not on IllegalStateException
            cause is IOException
        }
        .collect { data ->
            println("Received: $data")
        }
}
```

#### 2. Advanced Retry with `retryWhen()`

**`retryWhen()` operator:**
- More control over retry logic
- Can add delays between retries
- Access to attempt count and exception

**Basic `retryWhen`:**

```kotlin
import java.io.IOException

suspend fun retryWhenExample() {
    flow {
        println("Attempting to fetch data...")
        throw IOException("Network error")
    }
        .retryWhen { cause, attempt ->
            // attempt is 0 for the first retry
            if (cause is IOException && attempt < 3) {
                delay(1000 * (attempt + 1)) // Linear backoff per retry
                true // Retry
            } else {
                false // Don't retry
            }
        }
        .catch { e ->
            println("Failed after retries: ${e.message}")
        }
        .collect()
}
```

**`retryWhen` vs `retry`:**

| Feature | `retry()` | `retryWhen()` |
|---------|-----------|---------------|
| Delay | No (immediate) | Yes (manual delay) |
| Attempt count | Not accessible | Available |
| Conditional logic | Basic predicate | Full control |
| Best for | Simple retry | Custom backoff strategies |

#### 3. Exponential Backoff Implementation

**Exponential backoff algorithm:**
- Delay increases exponentially: 1s, 2s, 4s, 8s, 16s...
- Formula: `delay = initialDelay * (multiplier ^ attempt)`
- Prevents overwhelming failing services

**Basic exponential backoff:**

```kotlin
import kotlin.math.pow
import java.io.IOException

suspend fun exponentialBackoffExample() {
    val initialDelayMs = 1000L
    val multiplier = 2.0
    val maxAttempts = 5L

    flow {
        println("Fetching data...")
        throw IOException("Network error")
    }
        .retryWhen { cause, attempt ->
            if (cause is IOException && attempt < maxAttempts) {
                val delayMs = (initialDelayMs * multiplier.pow(attempt.toDouble())).toLong()
                println("Retry ${attempt + 1}/$maxAttempts after ${delayMs}ms")
                delay(delayMs)
                true
            } else {
                false
            }
        }
        .catch { e ->
            println("Failed after $maxAttempts attempts: ${e.message}")
        }
        .collect()
}

// Example output:
// Fetching data...
// Retry 1/5 after 1000ms
// Fetching data...
// Retry 2/5 after 2000ms
// Fetching data...
// Retry 3/5 after 4000ms
// ...
```

**Production-ready exponential backoff:**

```kotlin
import kotlin.math.pow
import kotlin.random.Random
import kotlinx.coroutines.flow.retryWhen

data class RetryConfig(
    val maxAttempts: Int = 5,
    val initialDelayMs: Long = 1000,
    val maxDelayMs: Long = 32000,
    val multiplier: Double = 2.0,
    val jitterFactor: Double = 0.1
)

fun <T> Flow<T>.retryWithExponentialBackoff(
    config: RetryConfig = RetryConfig(),
    predicate: (Throwable) -> Boolean = { true }
): Flow<T> = retryWhen { cause, attempt ->
    if (predicate(cause) && attempt < config.maxAttempts) {
        val baseDelay = (config.initialDelayMs * config.multiplier.pow(attempt.toDouble()))
            .toLong()
            .coerceAtMost(config.maxDelayMs)

        // Add jitter (randomness) to prevent thundering herd
        val jitter = (baseDelay * config.jitterFactor * Random.nextDouble(-1.0, 1.0)).toLong()
        val delayMs = (baseDelay + jitter).coerceAtLeast(0)

        println("Retry ${attempt + 1}/${config.maxAttempts} after ${delayMs}ms (cause: ${cause.message})")
        delay(delayMs)
        true
    } else {
        false
    }
}

// Usage
import retrofit2.HttpException

suspend fun retryWithConfigExample() {
    getDataFromApi()
        .retryWithExponentialBackoff(
            config = RetryConfig(
                maxAttempts = 5,
                initialDelayMs = 1000,
                maxDelayMs = 30000,
                multiplier = 2.0,
                jitterFactor = 0.1
            ),
            predicate = { it is IOException || it is HttpException }
        )
        .collect { data ->
            println("Success: $data")
        }
}
```

#### 4. Jitter for Retry Timing

**Why jitter?**
- Prevents **thundering herd** problem
- Multiple clients don't retry at exact same time
- Distributes load more evenly

**Jitter strategies:**

```kotlin
import kotlin.random.Random
import kotlin.math.pow

// 1. Full jitter: random delay between 0 and calculated delay
fun calculateFullJitter(baseDelay: Long): Long {
    return (baseDelay * Random.nextDouble()).toLong()
}

// 2. Equal jitter: half base delay + random half
fun calculateEqualJitter(baseDelay: Long): Long {
    return (baseDelay / 2) + (baseDelay / 2 * Random.nextDouble()).toLong()
}

// 3. Decorrelated jitter: based on previous delay
fun calculateDecorrelatedJitter(previousDelay: Long, baseDelay: Long): Long {
    return (baseDelay + (previousDelay * 3 * Random.nextDouble())).toLong()
}

// Example with equal jitter
fun <T> Flow<T>.retryWithJitter(
    maxAttempts: Int = 5,
    initialDelayMs: Long = 1000,
    maxDelayMs: Long = 32000
): Flow<T> = retryWhen { _, attempt ->
    if (attempt < maxAttempts) {
        val baseDelay = (initialDelayMs * (2.0.pow(attempt.toDouble())))
            .toLong()
            .coerceAtMost(maxDelayMs)

        // Equal jitter
        val delayMs = (baseDelay / 2) + (baseDelay / 2 * Random.nextDouble()).toLong()

        delay(delayMs)
        true
    } else {
        false
    }
}
```

#### 5. Production Example: Network Requests

**Resilient API client:**

```kotlin
import kotlinx.coroutines.flow.*
import retrofit2.HttpException
import java.io.IOException

class ApiClient(private val api: ApiService) {

    // Retry configuration for different request types
    private val standardRetry = RetryConfig(
        maxAttempts = 3,
        initialDelayMs = 1000,
        maxDelayMs = 10000
    )

    private val longRetry = RetryConfig(
        maxAttempts = 5,
        initialDelayMs = 2000,
        maxDelayMs = 60000
    )

    fun getUser(userId: String): Flow<User> = flow {
        emit(api.getUser(userId))
    }
        .retryWithExponentialBackoff(
            config = standardRetry,
            predicate = ::isRetriableError
        )
        .catch { e ->
            // Handle non-retriable errors (surface or wrap appropriately)
            throw ApiException("Failed to get user", e)
        }

    fun syncData(): Flow<SyncResult> = flow {
        emit(api.syncData())
    }
        .retryWithExponentialBackoff(
            config = longRetry,
            predicate = ::isRetriableError
        )
        .onEach { result ->
            println("Sync completed: $result")
        }

    fun searchUsers(query: String): Flow<List<User>> = flow {
        emit(api.searchUsers(query))
    }
        .timeout(5000) // Timeout each attempt after 5 seconds
        .retryWithExponentialBackoff(
            config = standardRetry,
            predicate = { it is IOException || it is TimeoutCancellationException }
        )

    private fun isRetriableError(error: Throwable): Boolean {
        return when (error) {
            // Network errors - retry
            is IOException -> true

            // Timeout - retry
            is TimeoutCancellationException -> true

            // HTTP errors - check status code
            is HttpException -> when (error.code()) {
                // 5xx server errors - retry
                in 500..599 -> true

                // 408 Request Timeout - retry
                408 -> true

                // 429 Too Many Requests - retry (in production, respect Retry-After)
                429 -> true

                // Other 4xx client errors - don't retry
                else -> false
            }

            // Other errors - don't retry
            else -> false
        }
    }
}

// Usage
suspend fun fetchUserWithRetry(apiService: ApiService) {
    val apiClient = ApiClient(apiService)

    apiClient.getUser("user123")
        .onStart { println("Fetching user...") }
        .onEach { user -> println("User: ${user.name}") }
        .catch { e -> println("Error: ${e.message}") }
        .collect()
}
```

#### 6. Production Example: Database Operations

**Resilient database operations with retry:**

```kotlin
import kotlinx.coroutines.flow.*
import android.database.sqlite.SQLiteException

class DatabaseRepository(private val database: AppDatabase) {

    fun insertWithRetry(item: Item): Flow<Long> = flow {
        emit(database.itemDao().insert(item))
    }
        .retryWhen { cause, attempt ->
            // Retry on database locked errors (simplified condition)
            if (cause is SQLiteException && attempt < 3) {
                val delayMs = 100L * (attempt + 1)
                println("Database locked, retry ${attempt + 1} after ${delayMs}ms")
                delay(delayMs)
                true
            } else {
                false
            }
        }

    fun batchInsertWithRetry(items: List<Item>): Flow<Unit> = flow {
        database.withTransaction {
            items.forEach { item ->
                database.itemDao().insert(item)
            }
        }
        emit(Unit)
    }
        .retryWithExponentialBackoff(
            config = RetryConfig(
                maxAttempts = 3,
                initialDelayMs = 100,
                maxDelayMs = 1000
            ),
            predicate = { it is SQLiteException }
        )

    fun observeItemsWithRetry(userId: String): Flow<List<Item>> {
        return database.itemDao().observeItems(userId)
            .catch { e ->
                if (e is SQLiteException) {
                    // Emit empty list on error and let retryWhen resubscribe
                    emit(emptyList())
                    delay(1000)
                    throw e
                }
            }
            .retryWhen { cause, attempt ->
                cause is SQLiteException && attempt < 5
            }
    }
}
```

#### 7. Combining Retry with Timeout

**Timeout + retry pattern:**

```kotlin
suspend fun fetchDataWithTimeoutAndRetry() {
    flow {
        emit(fetchDataFromSlowApi())
    }
        .timeout(5000) // Timeout each attempt after 5 seconds
        .retryWithExponentialBackoff(
            config = RetryConfig(maxAttempts = 3)
        )
        .catch { e ->
            when (e) {
                is TimeoutCancellationException -> {
                    println("All attempts timed out")
                }
                else -> println("Failed: ${e.message}")
            }
        }
        .collect { data ->
            println("Success: $data")
        }
}

// Per-request timeout vs total timeout
suspend fun fetchWithTotalTimeout() {
    withTimeout(15000) { // Total timeout: 15 seconds
        flow {
            emit(fetchDataFromApi())
        }
            .timeout(5000) // Per-attempt timeout: 5 seconds
            .retryWhen { cause, attempt ->
                if (cause is TimeoutCancellationException && attempt < 2) {
                    println("Attempt timed out, retrying...")
                    delay(1000)
                    true
                } else {
                    false
                }
            }
            .collect { data ->
                println("Success: $data")
            }
    }
}
```

#### 8. Circuit Breaker Integration

**Circuit breaker with retry:**

```kotlin
enum class CircuitState {
    CLOSED,  // Normal operation
    OPEN,    // Failing, reject requests
    HALF_OPEN // Testing if recovered
}

class CircuitBreaker(
    private val failureThreshold: Int = 5,
    private val resetTimeoutMs: Long = 60000
) {
    private var state = CircuitState.CLOSED
    private var failureCount = 0
    private var lastFailureTime = 0L

    fun <T> protect(block: suspend () -> T): Flow<T> = flow {
        when (state) {
            CircuitState.OPEN -> {
                if (System.currentTimeMillis() - lastFailureTime >= resetTimeoutMs) {
                    state = CircuitState.HALF_OPEN
                    println("Circuit breaker: HALF_OPEN (testing)")
                } else {
                    throw CircuitBreakerOpenException("Circuit breaker is OPEN")
                }
            }
            else -> { /* CLOSED or HALF_OPEN: allow attempt */ }
        }

        try {
            val result = block()
            onSuccess()
            emit(result)
        } catch (e: Exception) {
            onFailure()
            throw e
        }
    }

    private fun onSuccess() {
        failureCount = 0
        if (state == CircuitState.HALF_OPEN) {
            state = CircuitState.CLOSED
            println("Circuit breaker: CLOSED (recovered)")
        }
    }

    private fun onFailure() {
        failureCount++
        lastFailureTime = System.currentTimeMillis()

        if (failureCount >= failureThreshold) {
            state = CircuitState.OPEN
            println("Circuit breaker: OPEN (too many failures)")
        }
    }
}

class CircuitBreakerOpenException(message: String) : Exception(message)

// Usage with retry
suspend fun fetchWithCircuitBreaker() {
    val circuitBreaker = CircuitBreaker(
        failureThreshold = 3,
        resetTimeoutMs = 30000
    )

    circuitBreaker.protect {
        fetchDataFromApi()
    }
        .retryWithExponentialBackoff(
            config = RetryConfig(maxAttempts = 3),
            predicate = { it !is CircuitBreakerOpenException }
        )
        .catch { e ->
            when (e) {
                is CircuitBreakerOpenException -> {
                    println("Circuit breaker open, not retrying")
                }
                else -> println("Failed: ${e.message}")
            }
        }
        .collect { data ->
            println("Success: $data")
        }
}
```

#### 9. Retry for Different Exception Types

**Different strategies for different errors:**

```kotlin
import kotlin.reflect.KClass
import kotlin.math.pow

data class RetryStrategy(
    val maxAttempts: Int,
    val initialDelayMs: Long,
    val multiplier: Double = 2.0
)

fun <T> Flow<T>.retryByExceptionType(
    strategies: Map<KClass<out Throwable>, RetryStrategy>,
    defaultStrategy: RetryStrategy? = null
): Flow<T> = retryWhen { cause, attempt ->
    // Find matching strategy
    val strategy = strategies.entries
        .firstOrNull { (exceptionType, _) ->
            exceptionType.isInstance(cause)
        }?.value ?: defaultStrategy

    if (strategy != null && attempt < strategy.maxAttempts) {
        val delayMs = (strategy.initialDelayMs * strategy.multiplier.pow(attempt.toDouble()))
            .toLong()

        println("Retry ${cause::class.simpleName} (${attempt + 1}/${strategy.maxAttempts}) after ${delayMs}ms")
        delay(delayMs)
        true
    } else {
        false
    }
}

// Usage
suspend fun fetchWithCustomStrategies() {
    getDataFromApi()
        .retryByExceptionType(
            strategies = mapOf(
                IOException::class to RetryStrategy(
                    maxAttempts = 5,
                    initialDelayMs = 1000,
                    multiplier = 2.0
                ),
                HttpException::class to RetryStrategy(
                    maxAttempts = 3,
                    initialDelayMs = 2000,
                    multiplier = 1.5
                ),
                TimeoutCancellationException::class to RetryStrategy(
                    maxAttempts = 2,
                    initialDelayMs = 5000,
                    multiplier = 1.0
                )
            ),
            defaultStrategy = RetryStrategy(
                maxAttempts = 1,
                initialDelayMs = 1000
            )
        )
        .collect { data ->
            println("Success: $data")
        }
}
```

#### 10. Monitoring and Logging Retry Attempts

**Production monitoring:**

```kotlin
interface RetryLogger {
    fun onRetryAttempt(attempt: Int, maxAttempts: Int, cause: Throwable, delayMs: Long)
    fun onRetryExhausted(attempts: Int, lastCause: Throwable)
    fun onRetrySuccess(totalAttempts: Int)
}

class ProductionRetryLogger(private val analyticsService: AnalyticsService) : RetryLogger {
    override fun onRetryAttempt(attempt: Int, maxAttempts: Int, cause: Throwable, delayMs: Long) {
        val event = mapOf(
            "event" to "retry_attempt",
            "attempt" to attempt,
            "max_attempts" to maxAttempts,
            "cause" to cause::class.simpleName,
            "delay_ms" to delayMs
        )
        analyticsService.logEvent(event)
        println("[RETRY] Attempt $attempt/$maxAttempts after ${delayMs}ms - ${cause.message}")
    }

    override fun onRetryExhausted(attempts: Int, lastCause: Throwable) {
        val event = mapOf(
            "event" to "retry_exhausted",
            "attempts" to attempts,
            "cause" to lastCause::class.simpleName
        )
        analyticsService.logEvent(event)
        println("[RETRY] Exhausted after $attempts attempts - ${lastCause.message}")
    }

    override fun onRetrySuccess(totalAttempts: Int) {
        if (totalAttempts > 0) {
            val event = mapOf(
                "event" to "retry_success",
                "attempts" to totalAttempts
            )
            analyticsService.logEvent(event)
            println("[RETRY] Success after $totalAttempts retries")
        }
    }
}

fun <T> Flow<T>.retryWithLogging(
    config: RetryConfig,
    logger: RetryLogger,
    predicate: (Throwable) -> Boolean = { true }
): Flow<T> {
    var attemptCount = 0

    return this
        .retryWhen { cause, attempt ->
            attemptCount = attempt.toInt()

            if (predicate(cause) && attempt < config.maxAttempts) {
                val delayMs = calculateBackoff(config, attempt)
                logger.onRetryAttempt(
                    attempt = (attempt + 1).toInt(),
                    maxAttempts = config.maxAttempts,
                    cause = cause,
                    delayMs = delayMs
                )
                delay(delayMs)
                true
            } else {
                // Treat both true exhaustion and non-retriable error as "exhausted" for logging purposes
                logger.onRetryExhausted(attemptCount + 1, cause)
                false
            }
        }
        .onEach {
            if (attemptCount > 0) {
                logger.onRetrySuccess(attemptCount)
            }
        }
}

private fun calculateBackoff(config: RetryConfig, attempt: Long): Long {
    val baseDelay = (config.initialDelayMs * config.multiplier.pow(attempt.toDouble()))
        .toLong()
        .coerceAtMost(config.maxDelayMs)

    val jitter = (baseDelay * config.jitterFactor * Random.nextDouble(-1.0, 1.0)).toLong()
    return (baseDelay + jitter).coerceAtLeast(0)
}
```

#### 11. Testing Retry Logic

**Unit tests with virtual time:**

```kotlin
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow*
import kotlinx.coroutines.test.runTest
import org.junit.Test
import kotlin.math.pow
import kotlin.test.assertEquals
import java.io.IOException
import kotlinx.coroutines.TimeoutCancellationException

class RetryTest {

    @Test
    fun `retry succeeds after 2 attempts`() = runTest {
        var attempts = 0

        val flow = flow {
            attempts++
            if (attempts < 2) {
                throw IOException("Network error")
            }
            emit("Success")
        }

        val result = flow
            .retry(retries = 3)
            .first()

        assertEquals("Success", result)
        assertEquals(2, attempts)
    }

    @Test
    fun `exponential backoff has increasing delays`() = runTest {
        val delays = mutableListOf<Long>()
        var attempts = 0

        val flow = flow {
            attempts++
            throw IOException("Error")
        }

        flow
            .retryWhen { _, attempt ->
                if (attempt < 3) {
                    val d = 1000L * (2.0.pow(attempt.toDouble())).toLong()
                    delays.add(d)
                    delay(d)
                    true
                } else {
                    false
                }
            }
            .catch { }
            .collect()

        // Verify exponential delays: 1000, 2000, 4000
        assertEquals(listOf(1000L, 2000L, 4000L), delays)
        assertEquals(4, attempts)
    }

    @Test
    fun `retry only on specific exception type`() = runTest {
        var ioAttempts = 0
        var otherAttempts = 0

        val flow = flow {
            if (ioAttempts < 2) {
                ioAttempts++
                throw IOException("Network error")
            } else {
                otherAttempts++
                throw IllegalStateException("Invalid state")
            }
        }

        try {
            flow
                .retry(5) { it is IOException }
                .collect()
        } catch (e: IllegalStateException) {
            // Expected
        }

        assertEquals(2, ioAttempts) // Retried IOException twice
        assertEquals(1, otherAttempts) // IllegalStateException not retried
    }

    @Test
    fun `retry with timeout`() = runTest {
        val flow = flow {
            delay(10000) // Simulate slow operation
            emit("Data")
        }

        var timeoutCount = 0

        flow
            .timeout(1000)
            .retryWhen { cause, attempt ->
                if (cause is TimeoutCancellationException && attempt < 2) {
                    timeoutCount++ // counting retries triggered by timeout
                    delay(100)
                    true
                } else {
                    false
                }
            }
            .catch { }
            .collect()

        // Two retry attempts were initiated due to timeouts
        assertEquals(2, timeoutCount)
    }
}
```

#### 12. Best Practices Summary

**Do's:**

```kotlin
// Use exponential backoff for network requests
flow { fetchFromApi() }
    .retryWithExponentialBackoff()

// Add jitter to prevent thundering herd
.retryWithExponentialBackoff(
    config = RetryConfig(jitterFactor = 0.1)
)

// Set max delay to avoid very long waits
RetryConfig(maxDelayMs = 60000)

// Only retry retriable errors
.retry { it is IOException }

// Combine with timeout
.timeout(5000)
.retryWithExponentialBackoff()

// Log retry attempts for monitoring
.retryWithLogging(config, logger)
```

**Don'ts:**

```kotlin
// Don't retry immediately without delay
.retry(10) // Hammers the server

// Don't retry forever
.retry(Long.MAX_VALUE) // Never gives up

// Don't retry non-retriable errors
.retry { true } // Retries everything

// Don't forget max delay
RetryConfig(multiplier = 10.0) // Can lead to hours of waiting

// Don't ignore exceptions after retry
.retry(3)
// Missing .catch { }
```

### Related Questions

## Follow-ups
1. How does exponential backoff with jitter prevent the thundering herd problem? Provide mathematical explanation.
2. What's the difference between `retry()` at the `Flow` level vs retry logic in the repository? When to choose each?
3. How would you implement a retry policy that backs off based on server response headers (e.g., `Retry-After`)?
4. Explain how to test retry logic with virtual time without actually waiting for delays.
5. How do you balance between retry aggressiveness and avoiding server overload in production?
6. What's the relationship between circuit breaker, retry, and timeout patterns? How do they complement each other?
7. How would you implement retry with different strategies for different HTTP status codes (e.g., retry 503, don't retry 400)?

### References
- [Flow Exception Handling](https://kotlinlang.org/docs/flow.html#flow-exceptions)
- [Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
- [Retry Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/retry)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
