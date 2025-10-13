---
id: 20251012-160001
title: "Mutex vs synchronized in Kotlin coroutines / Mutex vs synchronized в Kotlin корутинах"
slug: mutex-synchronized-coroutines-kotlin-medium
topic: kotlin
subtopics:
  - coroutines
  - mutex
  - synchronization
  - thread-safety
  - concurrency
status: draft
difficulty: medium
moc: moc-kotlin
date_created: 2025-10-12
date_updated: 2025-10-12
related_questions:
  - q-race-conditions-coroutines--kotlin--hard
  - q-semaphore-rate-limiting--kotlin--medium
  - q-channelflow-callbackflow-flow--kotlin--medium
tags:
  - kotlin
  - coroutines
  - concurrency
  - thread-safety
  - mutex
  - synchronization
---

# Mutex vs synchronized in Kotlin coroutines

## English Version

### Problem Statement

When working with shared mutable state in Kotlin coroutines, you need thread-safe synchronization mechanisms. Traditional Java's `synchronized` blocks and Kotlin's `@Synchronized` annotation block threads, which is inefficient in the coroutine world. **Mutex** provides a suspension-based alternative that doesn't block threads.

**The Question:** What is the difference between `Mutex` and `synchronized` in Kotlin coroutines, and when should you use each?

### Detailed Answer

#### What is Mutex?

**Mutex** (Mutual Exclusion) is a synchronization primitive from `kotlinx.coroutines.sync` that provides mutual exclusion without blocking threads. Instead of blocking, it **suspends** the coroutine until the lock is available.

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

#### Mutex vs synchronized: Key Differences

| Feature | Mutex | synchronized |
|---------|-------|--------------|
| **Blocking** | Suspends coroutine (non-blocking) | Blocks thread |
| **Usage** | `suspend` functions only | Any function |
| **Thread efficiency** | High (doesn't block threads) | Low (blocks threads) |
| **Reentrant** |  NO (will deadlock) |  YES |
| **Fairness** | Optional (default: unfair) | JVM-dependent |
| **Cancellation** | Supports coroutine cancellation | No cancellation support |
| **Try lock** | `tryLock()` available | `synchronized` doesn't support |
| **Performance** | Better for high contention | Better for very low contention |

#### Basic Mutex Usage

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
    val jobs = List(100) { i ->
        launch {
            account.deposit(10)
        }
    }

    jobs.joinAll()
    println("Final balance: ${account.getBalance()}") // Always 1000
}
```

#### Why Mutex is NOT Reentrant (Critical!)

**Reentrant** means the same thread can acquire the lock multiple times. Mutex is **NOT reentrant** and will deadlock:

```kotlin
val mutex = Mutex()

suspend fun outer() {
    mutex.withLock {
        println("Outer acquired lock")
        inner() // DEADLOCK! Trying to acquire the same lock
    }
}

suspend fun inner() {
    mutex.withLock { // This will suspend forever
        println("Inner acquired lock")
    }
}

// DON'T DO THIS - Will deadlock!
// outer()
```

**Solution:** Don't nest `withLock` calls on the same mutex. Refactor your code:

```kotlin
val mutex = Mutex()
private var data = 0

suspend fun outer() {
    mutex.withLock {
        data++
    }
    innerWithoutLock() // Call version that doesn't lock
}

private fun innerWithoutLock() {
    // Work with data without locking
    // Caller is responsible for synchronization
}
```

#### Mutex vs AtomicInteger/AtomicReference

For simple operations like counter increment, use **atomic types** instead of Mutex:

```kotlin
import java.util.concurrent.atomic.AtomicInteger

//  GOOD: Use atomic for simple counter
val atomicCounter = AtomicInteger(0)

suspend fun increment() {
    atomicCounter.incrementAndGet()
}

//  BAD: Mutex overkill for simple operations
val mutex = Mutex()
var counter = 0

suspend fun incrementWithMutex() {
    mutex.withLock {
        counter++
    }
}
```

**When to use Mutex instead of Atomic:**
- Multiple operations need to be atomic together
- Complex state transformations
- State depends on multiple variables

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

#### Performance Implications

**Mutex Performance:**
- Low contention: ~10-20ns overhead per lock (very fast)
- High contention: Coroutines suspend, threads remain free
- Scalability: Excellent (1000s of coroutines competing for lock)

**synchronized Performance:**
- Low contention: ~5-10ns overhead (fastest)
- High contention: Threads block, wasting OS resources
- Scalability: Poor (100s of threads competing for lock)

**Benchmark example:**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlin.system.measureTimeMillis

fun main() = runBlocking {
    val iterations = 10_000
    val coroutines = 1000

    // Test Mutex
    val mutex = Mutex()
    var mutexCounter = 0
    val mutexTime = measureTimeMillis {
        val jobs = List(coroutines) {
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
        val jobs = List(coroutines) {
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

#### Common Patterns

**Pattern 1: Shared Counter**

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

**Pattern 2: Thread-Safe Cache**

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
        // First check without holding lock for long
        mutex.withLock {
            cache[key]?.let { return it }
        }

        // Compute outside lock (if expensive)
        val computed = defaultValue()

        // Store result
        mutex.withLock {
            cache.getOrPut(key) { computed }
        }
    }
}
```

**Pattern 3: Connection Pool**

```kotlin
class ConnectionPool(private val maxConnections: Int) {
    private val mutex = Mutex()
    private val connections = mutableListOf<Connection>()
    private var activeCount = 0

    suspend fun acquire(): Connection {
        mutex.withLock {
            // Reuse existing connection
            if (connections.isNotEmpty()) {
                return connections.removeAt(connections.lastIndex)
            }

            // Create new if under limit
            if (activeCount < maxConnections) {
                activeCount++
                return createConnection()
            }

            throw IllegalStateException("Connection pool exhausted")
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

#### Real Android ViewModel Example

```kotlin
class UserProfileViewModel : ViewModel() {
    private val mutex = Mutex()

    private val _profileState = MutableStateFlow<ProfileState>(ProfileState.Loading)
    val profileState: StateFlow<ProfileState> = _profileState.asStateFlow()

    private var cachedProfile: UserProfile? = null
    private var lastFetchTime = 0L

    fun loadProfile(userId: String, forceRefresh: Boolean = false) {
        viewModelScope.launch {
            mutex.withLock {
                val now = System.currentTimeMillis()
                val cacheValid = (now - lastFetchTime) < 5.minutes.inWholeMilliseconds

                // Return cached if valid and not forcing refresh
                if (!forceRefresh && cacheValid && cachedProfile != null) {
                    _profileState.value = ProfileState.Success(cachedProfile!!)
                    return@launch
                }

                // Fetch fresh data
                _profileState.value = ProfileState.Loading
            }

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

val Int.minutes: kotlin.time.Duration
    get() = kotlin.time.Duration.parse("${this}m")
```

#### Mutex Fairness

By default, Mutex is **unfair** - coroutines may acquire the lock out of order. For fair ordering:

```kotlin
// Note: Fair mutex is not directly available in kotlinx.coroutines
// You'd need to implement using Channel:

class FairMutex {
    private val channel = Channel<Unit>(Channel.UNLIMITED)

    init {
        channel.trySend(Unit) // Initial permit
    }

    suspend fun <T> withLock(action: suspend () -> T): T {
        channel.receive() // Wait for permit (FIFO order)
        try {
            return action()
        } finally {
            channel.send(Unit) // Return permit
        }
    }
}
```

#### Deadlock Scenarios and Prevention

**Scenario 1: Lock Ordering Deadlock**

```kotlin
val mutex1 = Mutex()
val mutex2 = Mutex()

// Coroutine 1
launch {
    mutex1.withLock {
        delay(10)
        mutex2.withLock { // Waiting for mutex2
            // Work
        }
    }
}

// Coroutine 2
launch {
    mutex2.withLock {
        delay(10)
        mutex1.withLock { // Waiting for mutex1 - DEADLOCK!
            // Work
        }
    }
}
```

**Prevention: Always acquire locks in the same order**

```kotlin
val mutex1 = Mutex()
val mutex2 = Mutex()

// Both coroutines acquire in same order
suspend fun safeOperation() {
    mutex1.withLock {
        mutex2.withLock {
            // Work
        }
    }
}
```

**Scenario 2: Reentrant Deadlock**

```kotlin
val mutex = Mutex()

suspend fun outer() {
    mutex.withLock {
        inner() // DEADLOCK!
    }
}

suspend fun inner() {
    mutex.withLock {
        // Work
    }
}
```

**Prevention: Don't nest locks, or use separate mutexes**

```kotlin
val mutex = Mutex()

suspend fun outer() {
    mutex.withLock {
        // Work
    }
    innerWithoutLock()
}

private fun innerWithoutLock() {
    // Work without locking
}
```

#### tryLock and Timeouts

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

// With timeout
suspend fun acquireWithTimeout(): Boolean {
    return withTimeoutOrNull(1000) {
        mutex.withLock {
            true
        }
    } ?: false
}
```

#### Production Code Example: Rate-Limited API Client

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

#### Testing Mutex-Based Code

```kotlin
import kotlinx.coroutines.test.*
import org.junit.Test
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

#### Pitfalls

1. **Using Mutex reentrantly** - Will deadlock
2. **Holding lock during long operations** - Blocks other coroutines unnecessarily
3. **Using synchronized with coroutines** - Blocks threads, wastes resources
4. **Not handling cancellation** - Use `withLock` instead of manual lock/unlock
5. **Forgetting to release lock** - Always use `withLock` or try-finally
6. **Lock ordering violations** - Causes deadlocks
7. **Using Mutex for simple counters** - Use AtomicInteger instead

#### Best Practices

1.  Use `withLock` instead of manual `lock()`/`unlock()`
2.  Keep critical sections small and fast
3.  Perform expensive operations outside the lock
4.  Use atomic types for simple operations
5.  Document lock ordering requirements
6.  Consider using `Channel` or `Actor` for complex state management
7.  Test concurrent access thoroughly
8.  Use Mutex fairness only when needed (usually unfair is fine)

### When to Use What?

**Use Mutex when:**
- Working with shared mutable state in coroutines
- Multiple operations need to be atomic
- You need suspension instead of thread blocking
- High concurrency (1000s of coroutines)

**Use synchronized when:**
- Very simple, short critical sections
- Working with legacy Java code
- No coroutines involved
- Performance-critical path with very low contention

**Use Atomic types when:**
- Single variable updates (counters, flags)
- Simple compare-and-swap operations
- No suspend functions needed

**Use Channel/Actor when:**
- Complex state machines
- Message-passing style preferred
- Natural producer-consumer patterns

### Key Takeaways

1. **Mutex suspends, synchronized blocks** - Mutex is more efficient for coroutines
2. **Mutex is NOT reentrant** - Avoid nested locks
3. **Use `withLock`** - Handles cancellation and ensures unlock
4. **Keep critical sections small** - Do expensive work outside lock
5. **Prefer atomic types for simple operations** - Mutex is overkill for counters
6. **Test concurrent access** - Race conditions are subtle
7. **Document lock dependencies** - Prevent deadlocks

---

## Русская версия

### Формулировка проблемы

При работе с общим изменяемым состоянием в Kotlin корутинах необходимы потокобезопасные механизмы синхронизации. Традиционные Java блоки `synchronized` и Kotlin аннотация `@Synchronized` блокируют потоки, что неэффективно в мире корутин. **Mutex** предоставляет альтернативу на основе приостановки, которая не блокирует потоки.

**Вопрос:** В чем разница между `Mutex` и `synchronized` в Kotlin корутинах, и когда следует использовать каждый из них?

### Подробный ответ

#### Что такое Mutex?

**Mutex** (Взаимное исключение) - это примитив синхронизации из `kotlinx.coroutines.sync`, который обеспечивает взаимное исключение без блокировки потоков. Вместо блокировки он **приостанавливает** корутину, пока блокировка не станет доступной.

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

#### Mutex vs synchronized: Ключевые различия

| Характеристика | Mutex | synchronized |
|----------------|-------|--------------|
| **Блокировка** | Приостанавливает корутину (неблокирующая) | Блокирует поток |
| **Использование** | Только `suspend` функции | Любая функция |
| **Эффективность потоков** | Высокая (не блокирует потоки) | Низкая (блокирует потоки) |
| **Реентерабельность** |  НЕТ (будет deadlock) |  ДА |
| **Справедливость** | Опционально (по умолчанию: несправедливый) | Зависит от JVM |
| **Отмена** | Поддерживает отмену корутины | Нет поддержки отмены |
| **Try lock** | Доступен `tryLock()` | `synchronized` не поддерживает |
| **Производительность** | Лучше при высокой конкуренции | Лучше при очень низкой конкуренции |

#### Базовое использование Mutex

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
    val jobs = List(100) { i ->
        launch {
            account.deposit(10)
        }
    }

    jobs.joinAll()
    println("Итоговый баланс: ${account.getBalance()}") // Всегда 1000
}
```

#### Почему Mutex НЕ реентерабельный (Критично!)

**Реентерабельность** означает, что один и тот же поток может захватить блокировку несколько раз. Mutex **НЕ реентерабельный** и приведет к deadlock:

```kotlin
val mutex = Mutex()

suspend fun outer() {
    mutex.withLock {
        println("Outer захватил блокировку")
        inner() // DEADLOCK! Попытка захватить ту же блокировку
    }
}

suspend fun inner() {
    mutex.withLock { // Это приостановится навсегда
        println("Inner захватил блокировку")
    }
}

// НЕ ДЕЛАЙТЕ ТАК - Будет deadlock!
// outer()
```

**Решение:** Не вкладывайте вызовы `withLock` на одном и том же mutex. Рефакторите код:

```kotlin
val mutex = Mutex()
private var data = 0

suspend fun outer() {
    mutex.withLock {
        data++
    }
    innerWithoutLock() // Вызываем версию без блокировки
}

private fun innerWithoutLock() {
    // Работаем с данными без блокировки
    // Вызывающая сторона отвечает за синхронизацию
}
```

#### Mutex vs AtomicInteger/AtomicReference

Для простых операций типа увеличения счетчика используйте **атомарные типы** вместо Mutex:

```kotlin
import java.util.concurrent.atomic.AtomicInteger

//  ХОРОШО: Используйте atomic для простого счетчика
val atomicCounter = AtomicInteger(0)

suspend fun increment() {
    atomicCounter.incrementAndGet()
}

//  ПЛОХО: Mutex излишен для простых операций
val mutex = Mutex()
var counter = 0

suspend fun incrementWithMutex() {
    mutex.withLock {
        counter++
    }
}
```

**Когда использовать Mutex вместо Atomic:**
- Несколько операций должны быть атомарными вместе
- Сложные трансформации состояния
- Состояние зависит от нескольких переменных

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

#### Производительность

**Производительность Mutex:**
- Низкая конкуренция: ~10-20нс накладные расходы на блокировку (очень быстро)
- Высокая конкуренция: Корутины приостанавливаются, потоки остаются свободными
- Масштабируемость: Отличная (1000и корутин конкурируют за блокировку)

**Производительность synchronized:**
- Низкая конкуренция: ~5-10нс накладные расходы (самый быстрый)
- Высокая конкуренция: Потоки блокируются, тратя ресурсы ОС
- Масштабируемость: Плохая (100и потоков конкурируют за блокировку)

#### Общие паттерны

**Паттерн 1: Общий счетчик**

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

**Паттерн 2: Потокобезопасный кеш**

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
        // Сначала проверяем без долгого удержания блокировки
        mutex.withLock {
            cache[key]?.let { return it }
        }

        // Вычисляем вне блокировки (если дорого)
        val computed = defaultValue()

        // Сохраняем результат
        mutex.withLock {
            cache.getOrPut(key) { computed }
        }
    }
}
```

#### Реальный пример Android ViewModel

```kotlin
class UserProfileViewModel : ViewModel() {
    private val mutex = Mutex()

    private val _profileState = MutableStateFlow<ProfileState>(ProfileState.Loading)
    val profileState: StateFlow<ProfileState> = _profileState.asStateFlow()

    private var cachedProfile: UserProfile? = null
    private var lastFetchTime = 0L

    fun loadProfile(userId: String, forceRefresh: Boolean = false) {
        viewModelScope.launch {
            mutex.withLock {
                val now = System.currentTimeMillis()
                val cacheValid = (now - lastFetchTime) < 5.minutes.inWholeMilliseconds

                // Возвращаем кешированное, если валидно и не форсируем обновление
                if (!forceRefresh && cacheValid && cachedProfile != null) {
                    _profileState.value = ProfileState.Success(cachedProfile!!)
                    return@launch
                }

                // Загружаем свежие данные
                _profileState.value = ProfileState.Loading
            }

            // Сетевой вызов вне блокировки
            try {
                val profile = fetchProfileFromNetwork(userId)

                mutex.withLock {
                    cachedProfile = profile
                    lastFetchTime = System.currentTimeMillis()
                    _profileState.value = ProfileState.Success(profile)
                }
            } catch (e: Exception) {
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

### Ключевые выводы

1. **Mutex приостанавливает, synchronized блокирует** - Mutex эффективнее для корутин
2. **Mutex НЕ реентерабельный** - Избегайте вложенных блокировок
3. **Используйте `withLock`** - Обрабатывает отмену и гарантирует разблокировку
4. **Держите критические секции маленькими** - Выполняйте дорогую работу вне блокировки
5. **Предпочитайте атомарные типы для простых операций** - Mutex избыточен для счетчиков
6. **Тестируйте конкурентный доступ** - Состояния гонки тонкие
7. **Документируйте зависимости блокировок** - Предотвращайте deadlock

---

## Follow-ups

1. How does Mutex handle coroutine cancellation compared to synchronized blocks?
2. Can you implement a fair Mutex using Channel in Kotlin coroutines?
3. What are the memory visibility guarantees of Mutex compared to @Volatile?
4. How would you debug a deadlock caused by nested Mutex locks?
5. When would you choose Actor pattern over Mutex for managing shared state?
6. How does Mutex performance compare to ReentrantLock in coroutine contexts?
7. Can you explain the internal implementation of Mutex using state machines?

## References

- [Kotlinx.coroutines Sync Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.sync/-mutex/)
- [Shared Mutable State and Concurrency](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html)
- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [Thread Safety in Kotlin](https://kotlinlang.org/docs/multiplatform-mobile-concurrency-overview.html)

## Related Questions

- [[q-race-conditions-coroutines--kotlin--hard|Race conditions and data races in Kotlin coroutines]]
- [[q-semaphore-rate-limiting--kotlin--medium|Semaphore for rate limiting and resource pooling]]
- [[q-channelflow-callbackflow-flow--kotlin--medium|channelFlow vs callbackFlow vs flow]]
- [[q-debugging-coroutines-techniques--kotlin--medium|Debugging Kotlin coroutines]]
