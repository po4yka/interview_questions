---
id: kotlin-081
title: "Mutex vs synchronized in Kotlin coroutines / Mutex vs synchronized в Kotlin корутинах"
topic: kotlin
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-12
updated: 2025-11-09
aliases: ["Mutex vs synchronized in Kotlin coroutines", "Mutex vs synchronized в Kotlin корутинах"]
question_kind: coding
tags: [concurrency, coroutines, difficulty/medium, kotlin, mutex, synchronization, thread-safety]
moc: moc-kotlin
related: [c-kotlin, q-channelflow-callbackflow-flow--kotlin--medium, q-debounce-throttle-flow--kotlin--medium, q-race-conditions-coroutines--kotlin--hard, q-semaphore-rate-limiting--kotlin--medium]
subtopics:
  - concurrency
  - coroutines
  - mutex
date created: Saturday, November 1st 2025, 12:10:12 pm
date modified: Tuesday, November 25th 2025, 8:53:49 pm
---

# Вопрос (RU)
> В чем разница между `Mutex` и `synchronized` в Kotlin корутинах, и когда следует использовать каждый из них?

---

# Question (EN)
> What is the difference between `Mutex` and `synchronized` in Kotlin coroutines, and when should you use each?

## Ответ (RU)

При работе с общим изменяемым состоянием в Kotlin корутинах необходимы потокобезопасные механизмы синхронизации. Традиционные Java блоки `synchronized` и Kotlin аннотация `@Synchronized` блокируют потоки, что неэффективно в мире корутин. `Mutex` предоставляет альтернативу на основе приостановки, которая старается не блокировать потоки и гораздо лучше масштабируется с большим числом корутин.


### Что Такое Mutex?

`Mutex` (взаимное исключение) — это примитив синхронизации из `kotlinx.coroutines.sync`, который обеспечивает взаимное исключение, интегрированное с корутинами. При использовании `withLock` он приостанавливает корутину, ожидая освобождения блокировки, вместо того чтобы блокировать поток.

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

val mutex = Mutex()
var counter = 0

suspend fun incrementCounter() {
    mutex.withLock {
        counter++
    }
}
```

### Mutex Vs Synchronized: Ключевые Различия

| Характеристика | Mutex | synchronized |
|----------------|-------|--------------|
| **Блокировка** | Обычно приостанавливает корутину (без блокировки потока при `withLock`) | Блокирует поток |
| **Использование** | Оптимален внутри `suspend`-кода (`withLock`), есть и не-suspend API (`tryLock`, `unlock`) | Любая функция |
| **Эффективность потоков** | Высокая при большом числе корутин (потоки остаются свободны) | Ниже при высокой конкуренции (потоки простаивают) |
| **Реентерабельность** | Не реентерабелен для владельца (повторный захват приведёт к зависанию/deadlock) | Реентерабелен по потоку (один и тот же поток может войти повторно) |
| **Справедливость** | По умолчанию несправедливый; строгая справедливость не гарантируется | Зависит от JVM, строгая справедливость не гарантируется |
| **Отмена** | Интеграция с отменой: `withLock` корректно освобождает mutex при отмене корутины | Отмена корутины не освобождает `synchronized`; блокирует поток до выхода из блока |
| **Try lock** | Есть `tryLock()` | Нет прямого аналога у `synchronized` |
| **Производительность** | Лучше масштабируется с большим числом корутин | Может быть быстрее при очень низкой конкуренции и небольшом числе потоков |

### Базовое Использование Mutex

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

class BankAccount {
    private val mutex = Mutex()
    private var balance = 0

    suspend fun deposit(amount: Int) {
        mutex.withLock {
            val current = balance
            delay(10) // Имитация обработки
            balance = current + amount
        }
    }

    suspend fun withdraw(amount: Int): Boolean {
        return mutex.withLock {
            if (balance >= amount) {
                val current = balance
                delay(10) // Имитация обработки
                balance = current - amount
                true
            } else {
                false
            }
        }
    }

    suspend fun getBalance(): Int {
        return mutex.withLock { balance }
    }
}

// Использование
suspend fun main() = coroutineScope {
    val account = BankAccount()

    // Запускаем 100 конкурентных депозитов
    val jobs = List(100) {
        launch {
            account.deposit(10)
        }
    }

    jobs.joinAll()
    println("Итоговый баланс: ${account.getBalance()}") // Всегда 1000
}
```

### Почему Mutex НЕ Реентерабельный (Критично!)

Реентерабельность в контексте `synchronized` означает, что один и тот же поток может захватить одну и ту же мониторовую блокировку несколько раз. В отличие от этого, `Mutex` из `kotlinx.coroutines` отслеживает владельца и не является реентерабельным: повторный захват тем же владельцем без освобождения приведёт к вечному ожиданию и фактическому взаимному блокированию.

```kotlin
val mutex = Mutex()

suspend fun outer() {
    mutex.withLock {
        println("Outer захватил блокировку")
        inner() // DEADLOCK: попытка захватить ту же блокировку тем же владельцем
    }
}

suspend fun inner() {
    mutex.withLock { // Это будет ожидать освобождения, которое не наступит
        println("Inner захватил блокировку")
    }
}

// НЕ ДЕЛАЙТЕ ТАК - Будет взаимная блокировка!
// outer()
```

Решение: не вкладывайте вызовы `withLock` на одном и том же `Mutex` внутри одного и того же пути выполнения. Рефакторите код так, чтобы критическая секция была плоской:

```kotlin
val mutex = Mutex()
private var data = 0

suspend fun outer() {
    mutex.withLock {
        data++
        innerWithoutLock() // вызываем версию без повторного захвата
    }
}

private fun innerWithoutLock() {
    // Работаем с данными без повторного захвата того же mutex.
    // Вызывающая сторона отвечает за синхронизацию.
}
```

### Mutex Vs AtomicInteger/AtomicReference

Для простых операций типа увеличения счётчика используйте атомарные типы вместо `Mutex`:

```kotlin
import java.util.concurrent.atomic.AtomicInteger

// Хорошо: используем atomic для простого счётчика
val atomicCounter = AtomicInteger(0)

suspend fun increment() {
    atomicCounter.incrementAndGet()
}

// Mutex избыточен для таких простых операций
val mutex = Mutex()
var counter = 0

suspend fun incrementWithMutex() {
    mutex.withLock {
        counter++
    }
}
```

Когда использовать `Mutex` вместо атомарных типов:
- Несколько операций должны быть атомарными вместе
- Сложные трансформации состояния
- Состояние зависит от нескольких связанных переменных

```kotlin
class UserSession {
    private val mutex = Mutex()
    private var userId: String? = null
    private var sessionToken: String? = null
    private var lastActivity: Long = 0

    // Все три должны обновляться атомарно
    suspend fun login(id: String, token: String) {
        mutex.withLock {
            userId = id
            sessionToken = token
            lastActivity = System.currentTimeMillis()
        }
    }

    suspend fun getSession(): Triple<String?, String?, Long> {
        return mutex.withLock {
            Triple(userId, sessionToken, lastActivity)
        }
    }
}
```

### Производительность

Производительность `Mutex`:
- Подходит для большого числа корутин, конкурирующих за ресурс
- При высокой конкуренции корутины приостанавливаются, потоки остаются свободными
- Хорошо масштабируется для coroutine-based нагрузок

Производительность `synchronized`:
- Очень быстрый в простых сценариях с низкой конкуренцией и ограниченным числом потоков
- При высокой конкуренции блокирует потоки и хуже масштабируется
- Конкретные цифры зависят от JVM/платформы и должны проверяться бенчмарками под вашу нагрузку

### Общие Паттерны

Паттерн 1: общий счётчик

```kotlin
class RequestCounter {
    private val mutex = Mutex()
    private var count = 0

    suspend fun increment(): Int {
        return mutex.withLock {
            ++count
        }
    }

    suspend fun get(): Int {
        return mutex.withLock { count }
    }
}
```

Паттерн 2: потокобезопасный кеш

```kotlin
class CacheWithMutex<K, V> {
    private val mutex = Mutex()
    private val cache = mutableMapOf<K, V>()

    suspend fun get(key: K): V? {
        return mutex.withLock {
            cache[key]
        }
    }

    suspend fun put(key: K, value: V) {
        mutex.withLock {
            cache[key] = value
        }
    }

    suspend fun getOrPut(key: K, defaultValue: suspend () -> V): V {
        // Быстрая проверка под кратким локом
        mutex.withLock {
            cache[key]?.let { return it }
        }

        // Дорогой расчёт вне блокировки
        val computed = defaultValue()

        // Повторно пытаемся сохранить результат под локом (double-check)
        return mutex.withLock {
            cache.getOrPut(key) { computed }
        }
    }
}
```

Паттерн 3: пул соединений (упрощённо)

```kotlin
class ConnectionPool(private val maxConnections: Int) {
    private val mutex = Mutex()
    private val connections = mutableListOf<Connection>()
    private var activeCount = 0

    suspend fun acquire(): Connection {
        return mutex.withLock {
            // Переиспользуем существующее соединение
            if (connections.isNotEmpty()) {
                return connections.removeAt(connections.lastIndex)
            }

            // Создаём новое, если не превышен лимит
            if (activeCount < maxConnections) {
                activeCount++
                return createConnection()
            }

            throw IllegalStateException("Пул соединений исчерпан (в этом упрощённом примере нет ожидания)")
        }
    }

    suspend fun release(connection: Connection) {
        mutex.withLock {
            connections.add(connection)
        }
    }

    private fun createConnection(): Connection {
        return Connection()
    }
}

class Connection {
    fun execute(query: String) {
        // Выполнение запроса
    }
}
```

### Реальный Пример Android `ViewModel`

```kotlin
class UserProfileViewModel : ViewModel() {
    private val mutex = Mutex()

    private val _profileState = MutableStateFlow<ProfileState>(ProfileState.Loading)
    val profileState: StateFlow<ProfileState> = _profileState.asStateFlow()

    private var cachedProfile: UserProfile? = null
    private var lastFetchTime = 0L
    private val cacheTtlMs = 5 * 60 * 1000L // 5 минут

    fun loadProfile(userId: String, forceRefresh: Boolean = false) {
        viewModelScope.launch {
            var shouldFetch = true

            mutex.withLock {
                val now = System.currentTimeMillis()
                val cacheValid = (now - lastFetchTime) < cacheTtlMs

                // Возвращаем кешированное, если валидно и не форсируем обновление
                if (!forceRefresh && cacheValid && cachedProfile != null) {
                    _profileState.value = ProfileState.Success(cachedProfile!!)
                    shouldFetch = false
                } else {
                    _profileState.value = ProfileState.Loading
                }
            }

            if (!shouldFetch) return@launch

            // Сетевой вызов вне блокировки
            try {
                val profile = fetchProfileFromNetwork(userId)

                mutex.withLock {
                    cachedProfile = profile
                    lastFetchTime = System.currentTimeMillis()
                    _profileState.value = ProfileState.Success(profile)
                }
            } catch (e: Exception) {
                // Ошибку обновляем без удержания mutex для состояния кэша
                _profileState.value = ProfileState.Error(e.message ?: "Неизвестная ошибка")
            }
        }
    }

    private suspend fun fetchProfileFromNetwork(userId: String): UserProfile {
        delay(1000) // Имитация сетевого вызова
        return UserProfile(userId, "John Doe", "john@example.com")
    }
}
```

### Справедливость Mutex

По умолчанию `Mutex` несправедлив: корутины могут получать блокировку не в порядке ожидания. В `kotlinx.coroutines` нет встроенного строго справедливого `Mutex`. Справедливость можно приблизительно реализовать поверх примитивов (например, `Channel`), но такие реализации сложнее и могут ухудшать производительность.

Упрощённый пример (не production-ready):

```kotlin
import kotlinx.coroutines.channels.Channel

class FairMutex {
    private val channel = Channel<Unit>(Channel.UNLIMITED)

    init {
        channel.trySend(Unit) // начальный "допуск"
    }

    suspend fun <T> withLock(action: suspend () -> T): T {
        channel.receive() // порядок FIFO за счёт канала
        try {
            return action()
        } finally {
            channel.send(Unit)
        }
    }
}
```

### Сценарии Deadlock И Как Их Избежать

Сценарий 1: взаимная блокировка из-за порядка захвата

```kotlin
val mutex1 = Mutex()
val mutex2 = Mutex()

// Корутина 1
launch {
    mutex1.withLock {
        delay(10)
        mutex2.withLock {
            // Работа
        }
    }
}

// Корутина 2
launch {
    mutex2.withLock {
        delay(10)
        mutex1.withLock {
            // Работа
        }
    }
}
```

Обе корутины могут навсегда ждать друг друга.

Профилактика: всегда захватывайте несколько `Mutex` в одном и том же глобальном порядке.

```kotlin
val mutex1 = Mutex()
val mutex2 = Mutex()

suspend fun safeOperation() {
    mutex1.withLock {
        mutex2.withLock {
            // Работа
        }
    }
}
```

Сценарий 2: псевдо-реентерабельный deadlock

```kotlin
val mutex = Mutex()

suspend fun outer() {
    mutex.withLock {
        inner() // inner пытается захватить тот же mutex
    }
}

suspend fun inner() {
    mutex.withLock {
        // Работа
    }
}
```

Профилактика: не брать один и тот же `Mutex` повторно в одном пути выполнения; разделяйте обязанности на функции, которые вызываются уже под локом, и функции, которые сами захватывают лок.

### tryLock И Тайм-ауты

```kotlin
val mutex = Mutex()

// Мгновенная попытка без приостановки
if (mutex.tryLock()) {
    try {
        // Критическая секция
    } finally {
        mutex.unlock()
    }
} else {
    // Лок недоступен
}

// Попытка с ограничением по времени для работы под локом
suspend fun acquireWithTimeout(): Boolean {
    return withTimeoutOrNull(1000) {
        mutex.withLock {
            // Критическая секция
            true
        }
    } != null
}
```

### Production-пример: Rate-Limited API Client

```kotlin
class ApiClient {
    private val mutex = Mutex()
    private var lastRequestTime = 0L
    private val minRequestInterval = 100L // минимум 100 мс между запросами

    suspend fun makeRequest(endpoint: String): Result<String> {
        mutex.withLock {
            val now = System.currentTimeMillis()
            val timeSinceLastRequest = now - lastRequestTime

            if (timeSinceLastRequest < minRequestInterval) {
                delay(minRequestInterval - timeSinceLastRequest)
            }

            lastRequestTime = System.currentTimeMillis()
        }

        // Фактический запрос вне блокировки
        return try {
            val response = performNetworkRequest(endpoint)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private suspend fun performNetworkRequest(endpoint: String): String {
        delay(50) // Имитация сетевого вызова
        return "Response from $endpoint"
    }
}
```

### Тестирование Кода С Mutex

```kotlin
import kotlinx.coroutines.launch
import kotlinx.coroutines.joinAll
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals

class BankAccountTest {
    @Test
    fun `concurrent deposits should be thread-safe`() = runTest {
        val account = BankAccount()

        val jobs = List(1000) {
            launch {
                account.deposit(1)
            }
        }

        jobs.joinAll()

        assertEquals(1000, account.getBalance())
    }

    @Test
    fun `withdrawal should respect balance`() = runTest {
        val account = BankAccount()
        account.deposit(100)

        val success = account.withdraw(50)
        assertEquals(true, success)
        assertEquals(50, account.getBalance())

        val failure = account.withdraw(100)
        assertEquals(false, failure)
        assertEquals(50, account.getBalance())
    }
}
```

### Типичные Ошибки

1. Использование `Mutex` реентерабельно в одном пути выполнения — приводит к взаимной блокировке.
2. Длительная или блокирующая работа под локом — задерживает другие корутины.
3. Использование `synchronized` в корутин-ориентированном коде — зря блокирует потоки.
4. Ручные `lock()`/`unlock()` без `try/finally` — риск забыть разблокировать.
5. Игнорирование семантики отмены — `withLock` безопаснее.
6. Нарушение порядка захвата нескольких `Mutex` — риск deadlock.
7. Применение `Mutex` для тривиальных счётчиков или флагов вместо атомиков.

### Рекомендуемые Практики

1. Предпочитайте `withLock` ручным `lock()`/`unlock()`.
2. Держите критические секции маленькими и быстрыми.
3. Выполняйте тяжёлую или блокирующую работу вне блокировки.
4. Используйте атомарные типы для простых одиночных переменных.
5. Документируйте порядок и правила захвата локов.
6. Рассматривайте `Channel`/Actor-подход для сложного состояния.
7. Тщательно тестируйте конкурентный доступ (включая стресс-тесты).

### Когда Что Использовать?

Используйте `Mutex`, когда:
- Работаете с общим изменяемым состоянием в корутинах.
- Несколько операций должны быть атомарными как единое целое.
- Важно не блокировать потоки, а приостанавливать корутины.
- Ожидается высокая конкуренция (много корутин).

Используйте `synchronized`, когда:
- Критические секции очень простые и короткие.
- Интегрируетесь с Java/наследуемым не-корутинным кодом.
- Нет необходимости в корутин-дружественной приостановке.
- Низкая конкуренция и важен минимальный JVM-оверхед.

Используйте атомарные типы, когда:
- Нужно менять одну переменную (счётчик, флаг).
- Достаточны простые CAS-операции.
- Внутри не нужны `suspend`-вызовы.

Используйте `Channel`/Actor-подход, когда:
- Управляете сложными или долгоживущими состояниями.
- Естественно ложится модель обмена сообщениями.
- Нужны producer-consumer или actor-style паттерны.

### Ключевые Выводы

1. `Mutex` с `withLock` приостанавливает корутины, `synchronized` блокирует поток — `Mutex` более подходящ для корутин.
2. `Mutex` не реентерабелен — избегайте вложенных локов на одном и том же `Mutex`.
3. Используйте `withLock` — он безопасен и учитывает отмену.
4. Держите критические секции маленькими — тяжёлую работу выносите наружу.
5. Для простых операций предпочитайте атомарные типы — `Mutex` избыточен.
6. Тестируйте конкурентный доступ и документируйте порядок захвата локов.

---

## Answer (EN)

When working with shared mutable state in Kotlin coroutines, you need thread-safe synchronization mechanisms. Traditional Java `synchronized` blocks and Kotlin's `@Synchronized` annotation block threads, which is often inefficient in coroutine-heavy code. `Mutex` provides a coroutine-friendly alternative that integrates with suspension and scales better with many coroutines.


### What is Mutex?

`Mutex` (Mutual Exclusion) is a synchronization primitive from `kotlinx.coroutines.sync` that provides mutual exclusion integrated with coroutines. When using `withLock`, it suspends the coroutine until the lock is available instead of blocking the underlying thread.

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

val mutex = Mutex()
var counter = 0

suspend fun incrementCounter() {
    mutex.withLock {
        counter++
    }
}
```

### Mutex Vs Synchronized: Key Differences

| Feature | Mutex | synchronized |
|---------|-------|--------------|
| **Blocking** | With `withLock`, suspends coroutine instead of blocking the thread | Blocks the thread |
| **Usage** | Best used in `suspend` code (`withLock`); also has non-suspend APIs (`tryLock`, `unlock`) | Any function |
| **Thread efficiency** | High with many coroutines (threads stay free while coroutines wait) | Lower under high contention (threads can be parked/blocked) |
| **Reentrant** | NOT reentrant for its owner: re-acquiring without unlock will cause a logical deadlock | Reentrant per thread: same thread can enter the same monitor multiple times |
| **Fairness** | Unfair by default; strict fairness not guaranteed | JVM-dependent; strict fairness not guaranteed |
| **Cancellation** | Integrated with coroutine cancellation: `withLock` releases on cancellation | Coroutine cancellation does not release a `synchronized` monitor; thread stays blocked until exit |
| **Try lock** | `tryLock()` available | No direct equivalent for `synchronized` |
| **Performance** | Better scalability for coroutine-based concurrency | Can be very fast under low contention and few threads; benchmarks are workload-specific |

### Basic Mutex Usage

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

class BankAccount {
    private val mutex = Mutex()
    private var balance = 0

    suspend fun deposit(amount: Int) {
        mutex.withLock {
            val current = balance
            delay(10) // Simulate processing
            balance = current + amount
        }
    }

    suspend fun withdraw(amount: Int): Boolean {
        return mutex.withLock {
            if (balance >= amount) {
                val current = balance
                delay(10) // Simulate processing
                balance = current - amount
                true
            } else {
                false
            }
        }
    }

    suspend fun getBalance(): Int {
        return mutex.withLock { balance }
    }
}

// Usage
suspend fun main() = coroutineScope {
    val account = BankAccount()

    // Launch 100 concurrent deposits
    val jobs = List(100) {
        launch {
            account.deposit(10)
        }
    }

    jobs.joinAll()
    println("Final balance: ${account.getBalance()}") // Always 1000
}
```

### Why Mutex is NOT Reentrant (Critical!)

For `synchronized`, "reentrant" means the same thread can acquire the same monitor multiple times. In contrast, `Mutex` from `kotlinx.coroutines` tracks ownership and is not reentrant: trying to acquire the same mutex again along the same execution path without releasing it will suspend forever and effectively deadlock.

```kotlin
val mutex = Mutex()

suspend fun outer() {
    mutex.withLock {
        println("Outer acquired lock")
        inner() // DEADLOCK: attempts to acquire the same mutex again
    }
}

suspend fun inner() {
    mutex.withLock { // Will wait for a release that never happens
        println("Inner acquired lock")
    }
}

// DON'T DO THIS - Will deadlock!
// outer()
```

Solution: Avoid nested `withLock` calls on the same mutex along the same code path. Keep the critical section flat:

```kotlin
val mutex = Mutex()
private var data = 0

suspend fun outer() {
    mutex.withLock {
        data++
        innerWithoutLock()
    }
}

private fun innerWithoutLock() {
    // Work with data without reacquiring the same mutex.
    // Caller is responsible for synchronization.
}
```

### Mutex Vs AtomicInteger/AtomicReference

For simple operations like incrementing a counter, prefer atomic types over `Mutex`:

```kotlin
import java.util.concurrent.atomic.AtomicInteger

// GOOD: use atomic for simple counter
val atomicCounter = AtomicInteger(0)

suspend fun increment() {
    atomicCounter.incrementAndGet()
}

// Mutex is overkill for simple increments
val mutex = Mutex()
var counter = 0

suspend fun incrementWithMutex() {
    mutex.withLock {
        counter++
    }
}
```

When to use `Mutex` instead of atomic types:
- Multiple operations must be atomic together
- Complex state transformations
- State spans multiple related variables

```kotlin
class UserSession {
    private val mutex = Mutex()
    private var userId: String? = null
    private var sessionToken: String? = null
    private var lastActivity: Long = 0

    // All three must be updated atomically
    suspend fun login(id: String, token: String) {
        mutex.withLock {
            userId = id
            sessionToken = token
            lastActivity = System.currentTimeMillis()
        }
    }

    suspend fun getSession(): Triple<String?, String?, Long> {
        return mutex.withLock {
            Triple(userId, sessionToken, lastActivity)
        }
    }
}
```

### Performance Implications

Mutex:
- Designed to work well with many coroutines contending for a resource
- Under contention, waiting coroutines are suspended so threads can run other work
- Good scalability for coroutine-heavy architectures

`synchronized`:
- Very fast for short, uncontended critical sections on a small number of threads
- Under contention, blocks threads; scales worse with many threads/coroutines
- Exact performance is JVM- and workload-dependent; validate with benchmarks for your use case

Illustrative benchmark example (for experimentation only):

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlin.system.measureTimeMillis

fun main() = runBlocking {
    val iterations = 10_000
    val coroutinesCount = 1000

    // Test Mutex
    val mutex = Mutex()
    var mutexCounter = 0
    val mutexTime = measureTimeMillis {
        val jobs = List(coroutinesCount) {
            launch {
                repeat(iterations) {
                    mutex.withLock {
                        mutexCounter++
                    }
                }
            }
        }
        jobs.joinAll()
    }

    // Test synchronized
    val lock = Any()
    var syncCounter = 0
    val syncTime = measureTimeMillis {
        val jobs = List(coroutinesCount) {
            launch(Dispatchers.Default) {
                repeat(iterations) {
                    synchronized(lock) {
                        syncCounter++
                    }
                }
            }
        }
        jobs.joinAll()
    }

    println("Mutex: $mutexTime ms, counter: $mutexCounter")
    println("Synchronized: $syncTime ms, counter: $syncCounter")
}
```

### Common Patterns

Pattern 1: Shared Counter

```kotlin
class RequestCounter {
    private val mutex = Mutex()
    private var count = 0

    suspend fun increment(): Int {
        return mutex.withLock {
            ++count
        }
    }

    suspend fun get(): Int {
        return mutex.withLock { count }
    }
}
```

Pattern 2: Thread-Safe Cache

```kotlin
class CacheWithMutex<K, V> {
    private val mutex = Mutex()
    private val cache = mutableMapOf<K, V>()

    suspend fun get(key: K): V? {
        return mutex.withLock {
            cache[key]
        }
    }

    suspend fun put(key: K, value: V) {
        mutex.withLock {
            cache[key] = value
        }
    }

    suspend fun getOrPut(key: K, defaultValue: suspend () -> V): V {
        // Quick check under a short lock
        mutex.withLock {
            cache[key]?.let { return it }
        }

        // Compute outside lock if expensive
        val computed = defaultValue()

        // Store result with double-check under lock
        return mutex.withLock {
            cache.getOrPut(key) { computed }
        }
    }
}
```

Pattern 3: Connection Pool (simplified)

```kotlin
class ConnectionPool(private val maxConnections: Int) {
    private val mutex = Mutex()
    private val connections = mutableListOf<Connection>()
    private var activeCount = 0

    suspend fun acquire(): Connection {
        return mutex.withLock {
            // Reuse existing connection
            if (connections.isNotEmpty()) {
                return connections.removeAt(connections.lastIndex)
            }

            // Create new if under limit
            if (activeCount < maxConnections) {
                activeCount++
                return createConnection()
            }

            throw IllegalStateException("Connection pool exhausted (no waiting strategy in this simplified example)")
        }
    }

    suspend fun release(connection: Connection) {
        mutex.withLock {
            connections.add(connection)
        }
    }

    private fun createConnection(): Connection {
        return Connection()
    }
}

class Connection {
    fun execute(query: String) {
        // Execute query
    }
}
```

### Real Android `ViewModel` Example

```kotlin
class UserProfileViewModel : ViewModel() {
    private val mutex = Mutex()

    private val _profileState = MutableStateFlow<ProfileState>(ProfileState.Loading)
    val profileState: StateFlow<ProfileState> = _profileState.asStateFlow()

    private var cachedProfile: UserProfile? = null
    private var lastFetchTime = 0L
    private val cacheTtlMs = 5 * 60 * 1000L // 5 minutes

    fun loadProfile(userId: String, forceRefresh: Boolean = false) {
        viewModelScope.launch {
            var shouldFetch = true

            mutex.withLock {
                val now = System.currentTimeMillis()
                val cacheValid = (now - lastFetchTime) < cacheTtlMs

                // Return cached if valid and not forcing refresh
                if (!forceRefresh && cacheValid && cachedProfile != null) {
                    _profileState.value = ProfileState.Success(cachedProfile!!)
                    shouldFetch = false
                } else {
                    _profileState.value = ProfileState.Loading
                }
            }

            if (!shouldFetch) return@launch

            // Network call outside lock
            try {
                val profile = fetchProfileFromNetwork(userId)

                mutex.withLock {
                    cachedProfile = profile
                    lastFetchTime = System.currentTimeMillis()
                    _profileState.value = ProfileState.Success(profile)
                }
            } catch (e: Exception) {
                _profileState.value = ProfileState.Error(e.message ?: "Unknown error")
            }
        }
    }

    private suspend fun fetchProfileFromNetwork(userId: String): UserProfile {
        delay(1000) // Simulate network call
        return UserProfile(userId, "John Doe", "john@example.com")
    }
}

sealed class ProfileState {
    object Loading : ProfileState()
    data class Success(val profile: UserProfile) : ProfileState()
    data class Error(val message: String) : ProfileState()
}

data class UserProfile(
    val id: String,
    val name: String,
    val email: String
)
```

### Mutex Fairness

By default, `Mutex` is unfair: coroutines may acquire the lock out of order. There is no built-in strictly fair `Mutex` in `kotlinx.coroutines`. A fair lock can be approximated, but implementations are non-trivial and can have performance trade-offs.

Simplified illustrative example (not production-grade):

```kotlin
import kotlinx.coroutines.channels.Channel

class FairMutex {
    private val channel = Channel<Unit>(Channel.UNLIMITED)

    init {
        channel.trySend(Unit) // Initial permit
    }

    suspend fun <T> withLock(action: suspend () -> T): T {
        channel.receive() // FIFO order based on channel
        try {
            return action()
        } finally {
            channel.send(Unit)
        }
    }
}
```

### Deadlock Scenarios and Prevention

Scenario 1: Lock Ordering Deadlock

```kotlin
val mutex1 = Mutex()
val mutex2 = Mutex()

// Coroutine 1
launch {
    mutex1.withLock {
        delay(10)
        mutex2.withLock {
            // Work
        }
    }
}

// Coroutine 2
launch {
    mutex2.withLock {
        delay(10)
        mutex1.withLock {
            // Work
        }
    }
}
```

This can deadlock if each coroutine holds one mutex and waits for the other.

Prevention: Always acquire locks in the same global order.

```kotlin
val mutex1 = Mutex()
val mutex2 = Mutex()

suspend fun safeOperation() {
    mutex1.withLock {
        mutex2.withLock {
            // Work
        }
    }
}
```

Scenario 2: Reentrant-style Deadlock with Mutex

```kotlin
val mutex = Mutex()

suspend fun outer() {
    mutex.withLock {
        inner() // Attempts to reacquire the same mutex
    }
}

suspend fun inner() {
    mutex.withLock {
        // Work
    }
}
```

Prevention: Don't nest locks on the same mutex in the same call chain; split responsibilities into functions that assume the lock is already held vs. functions that acquire it.

### tryLock and Timeouts

```kotlin
val mutex = Mutex()

// Try to acquire without suspending
if (mutex.tryLock()) {
    try {
        // Critical section
    } finally {
        mutex.unlock()
    }
} else {
    // Lock not available
}

// With timeout for acquiring + work under lock
suspend fun acquireWithTimeout(): Boolean {
    return withTimeoutOrNull(1000) {
        mutex.withLock {
            // Critical section
            true
        }
    } != null
}
```

### Production Code Example: Rate-Limited API Client

```kotlin
class ApiClient {
    private val mutex = Mutex()
    private var lastRequestTime = 0L
    private val minRequestInterval = 100L // 100ms between requests

    suspend fun makeRequest(endpoint: String): Result<String> {
        mutex.withLock {
            val now = System.currentTimeMillis()
            val timeSinceLastRequest = now - lastRequestTime

            if (timeSinceLastRequest < minRequestInterval) {
                delay(minRequestInterval - timeSinceLastRequest)
            }

            lastRequestTime = System.currentTimeMillis()
        }

        // Actual request outside lock
        return try {
            val response = performNetworkRequest(endpoint)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private suspend fun performNetworkRequest(endpoint: String): String {
        delay(50) // Simulate network call
        return "Response from $endpoint"
    }
}
```

### Testing Mutex-Based Code

```kotlin
import kotlinx.coroutines.launch
import kotlinx.coroutines.joinAll
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals

class BankAccountTest {
    @Test
    fun `concurrent deposits should be thread-safe`() = runTest {
        val account = BankAccount()

        // Launch 1000 concurrent deposits
        val jobs = List(1000) {
            launch {
                account.deposit(1)
            }
        }

        jobs.joinAll()

        assertEquals(1000, account.getBalance())
    }

    @Test
    fun `withdrawal should respect balance`() = runTest {
        val account = BankAccount()
        account.deposit(100)

        val success = account.withdraw(50)
        assertEquals(true, success)
        assertEquals(50, account.getBalance())

        val failure = account.withdraw(100)
        assertEquals(false, failure)
        assertEquals(50, account.getBalance())
    }
}
```

### Common Pitfalls and Best Practices

### Pitfalls

1. Using `Mutex` reentrantly along the same call path — will deadlock.
2. Holding a lock during long or blocking operations — delays other coroutines.
3. Using `synchronized` inside coroutine-heavy code — blocks threads unnecessarily.
4. Manually calling `lock()`/`unlock()` without `try/finally` — risk of forgetting to unlock.
5. Ignoring cancellation semantics — prefer `withLock` which is cancellation-safe.
6. Violating lock ordering across multiple mutexes — leads to deadlocks.
7. Using `Mutex` for trivial counters or flags — atomic types are simpler and faster.

### Best Practices

1. Use `withLock` instead of manual `lock()`/`unlock()` where possible.
2. Keep critical sections small and fast.
3. Do expensive or blocking work outside the lock.
4. Use atomic types for simple single-variable concurrency.
5. Document lock ordering requirements.
6. Consider `Channel`/Actor patterns for complex state management.
7. Test concurrent access thoroughly (property-based and stress tests).

### When to Use What?

Use `Mutex` when:
- Working with shared mutable state in coroutines.
- Multiple operations must be atomic together.
- You want suspension instead of blocking threads.
- You expect high concurrency (many coroutines).

Use `synchronized` when:
- Very simple, short critical sections.
- Interacting with legacy Java / non-coroutine code.
- No need for coroutine-friendly suspension.
- Low contention and you want minimal overhead on the JVM.

Use atomic types when:
- Single-variable updates (counters, flags).
- Simple CAS (compare-and-set) operations.
- No suspend functions required inside the critical section.

Use `Channel`/Actor when:
- Managing complex or stateful workflows.
- Message-passing fits naturally.
- Producer-consumer or actor-style concurrency is desired.

### Key Takeaways

1. `Mutex` suspends (with `withLock`), `synchronized` blocks — `Mutex` is more suitable for coroutines.
2. `Mutex` is not reentrant — avoid nested locks on the same `Mutex`.
3. Use `withLock` — it is safer and cancellation-aware.
4. Keep critical sections small — push heavy work outside.
5. Prefer atomic types for simple operations — `Mutex` is overkill for counters.
6. Test concurrent access — race conditions are subtle.
7. Document lock dependencies — helps prevent deadlocks.

---

## Дополнительные Вопросы (RU)

1. Как `Mutex` обрабатывает отмену корутин по сравнению с блоками `synchronized`?
2. Можно ли реализовать справедливый `Mutex` с помощью `Channel` в Kotlin корутинах и каковы издержки?
3. Каковы гарантии видимости памяти у `Mutex` по сравнению с `@Volatile`?
4. Как бы вы отлаживали взаимную блокировку, вызванную вложенными `Mutex`?
5. В каких случаях вы выберете Actor-подход вместо `Mutex` для управления общим состоянием?
6. Как `Mutex` по производительности соотносится с `ReentrantLock` в контексте корутин?
7. Можете кратко описать идею внутренней реализации `Mutex` (очередь ожидания, состояние)?

## Follow-ups

1. How does `Mutex` handle coroutine cancellation compared to `synchronized` blocks?
2. Can you implement a fair `Mutex` using `Channel` in Kotlin coroutines? What are the trade-offs?
3. What are the memory visibility guarantees of `Mutex` compared to `@Volatile`?
4. How would you debug a deadlock caused by nested `Mutex` locks?
5. When would you choose Actor pattern over `Mutex` for managing shared state?
6. How does `Mutex` performance compare to `ReentrantLock` in coroutine contexts?
7. Can you explain the internal implementation idea of `Mutex` (state machine, queueing)?

## Ссылки (RU)

- [Kotlinx.coroutines Sync Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.sync/-mutex/)
- [Shared Mutable State and Concurrency](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html)
- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [Thread Safety in Kotlin](https://kotlinlang.org/docs/multiplatform-mobile-concurrency-overview.html)
- [[c-kotlin]]

## References

- [Kotlinx.coroutines Sync Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.sync/-mutex/)
- [Shared Mutable State and Concurrency](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html)
- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [Thread Safety in Kotlin](https://kotlinlang.org/docs/multiplatform-mobile-concurrency-overview.html)
- [[c-kotlin]]

## Связанные Вопросы (RU)

- [[q-race-conditions-coroutines--kotlin--hard|Состояния гонки и data races в Kotlin корутинах]]
- [[q-semaphore-rate-limiting--kotlin--medium|Semaphore для rate limiting и пула ресурсов]]
- [[q-channelflow-callbackflow-flow--kotlin--medium|channelFlow vs callbackFlow vs flow]]
- [[q-debugging-coroutines-techniques--kotlin--medium|Отладка Kotlin корутин]]

## Related Questions

- [[q-race-conditions-coroutines--kotlin--hard|Race conditions and data races in Kotlin coroutines]]
- [[q-semaphore-rate-limiting--kotlin--medium|Semaphore for rate limiting and resource pooling]]
- [[q-channelflow-callbackflow-flow--kotlin--medium|channelFlow vs callbackFlow vs flow]]
- [[q-debugging-coroutines-techniques--kotlin--medium|Debugging Kotlin coroutines]]
