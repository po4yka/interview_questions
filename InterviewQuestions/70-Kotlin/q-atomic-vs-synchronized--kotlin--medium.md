---
id: 20251017-150235
title: "Atomic Vs Synchronized / Atomic против Synchronized"
topic: kotlin
difficulty: medium
status: draft
created: 2025-10-15
tags: - kotlin
  - java
  - concurrency
  - thread-safety
  - atomic
  - synchronized
---
# Atomic vs Synchronized: когда использовать

**English**: When to use atomic variables vs synchronized?

## Answer (EN)
**Atomic** переменные (`AtomicInteger`, `AtomicReference`) и **synchronized** блоки — два способа обеспечить потокобезопасность. Используются в разных ситуациях в зависимости от сложности операций.

### Atomic Variables - for simple operations

Используйте для **одиночных** операций с **одной** переменной. Lock-free, высокая производительность.

```kotlin
// Atomic переменные
class Counter {
    private val count = AtomicInteger(0)

    fun increment() {
        count.incrementAndGet()  // Атомарная операция
    }

    fun decrement() {
        count.decrementAndGet()
    }

    fun get(): Int = count.get()

    // Compare-and-swap
    fun incrementIfLessThan(max: Int): Boolean {
        while (true) {
            val current = count.get()
            if (current >= max) return false

            if (count.compareAndSet(current, current + 1)) {
                return true
            }
        }
    }
}

// Использование
val counter = Counter()
repeat(1000) {
    thread {
        counter.increment()
    }
}
// Гарантированно: counter.get() == 1000
```

**When to use Atomic:**
- - Simple counter
- - Flag (boolean)
- - Single reference
- - Read-modify-write operation for ONE variable
- - Compare-and-swap logic

### Synchronized - for complex operations

Используйте для **множественных** операций или работы с **несколькими** переменными.

```kotlin
// Synchronized блоки
class BankAccount {
    private var balance = 0
    private val lock = Any()

    // Операция с ОДНОЙ переменной, но НЕСКОЛЬКО шагов
    fun deposit(amount: Int) = synchronized(lock) {
        if (amount > 0) {
            balance += amount
            logTransaction("Deposit: $amount")  // Дополнительная логика
        }
    }

    fun withdraw(amount: Int): Boolean = synchronized(lock) {
        if (balance >= amount) {
            balance -= amount
            logTransaction("Withdraw: $amount")
            return true
        }
        return false
    }

    fun getBalance(): Int = synchronized(lock) {
        balance
    }

    private fun logTransaction(msg: String) {
        // Логирование
    }
}
```

**When to use Synchronized:**
- - Working with multiple variables
- - Complex logic (if-else, loops)
- - Method calls inside critical section
- - Need mutual exclusion
- - Working with collections

### Usage examples

#### Example 1: Counter (Atomic is better)

```kotlin
// - Atomic - идеально для счетчика
class RequestCounter {
    private val count = AtomicLong(0)

    fun increment() {
        count.incrementAndGet()
    }

    fun getCount() = count.get()
}

// - Synchronized - избыточно
class RequestCounter {
    private var count = 0L
    private val lock = Any()

    fun increment() = synchronized(lock) {
        count++  // Overkill для простой операции
    }

    fun getCount() = synchronized(lock) { count }
}
```

#### Example 2: Cache with TTL (Synchronized is better)

```kotlin
// - Synchronized - нужен для сложной логики
class Cache<K, V>(private val ttlMs: Long) {
    private data class Entry<V>(
        val value: V,
        val timestamp: Long
    )

    private val cache = mutableMapOf<K, Entry<V>>()
    private val lock = Any()

    fun put(key: K, value: V) = synchronized(lock) {
        cache[key] = Entry(value, System.currentTimeMillis())
        cleanupExpired()  // Сложная операция
    }

    fun get(key: K): V? = synchronized(lock) {
        val entry = cache[key] ?: return null
        if (System.currentTimeMillis() - entry.timestamp > ttlMs) {
            cache.remove(key)
            return null
        }
        return entry.value
    }

    private fun cleanupExpired() {
        val now = System.currentTimeMillis()
        cache.entries.removeIf { (_, entry) ->
            now - entry.timestamp > ttlMs
        }
    }
}
```

#### Example 3: State flag (Atomic is simpler)

```kotlin
// - Atomic - для простого флага
class ConnectionManager {
    private val isConnected = AtomicBoolean(false)

    fun connect() {
        if (isConnected.compareAndSet(false, true)) {
            // Установить соединение
            establishConnection()
        }
    }

    fun disconnect() {
        if (isConnected.compareAndSet(true, false)) {
            // Закрыть соединение
            closeConnection()
        }
    }

    fun isConnected() = isConnected.get()
}
```

#### Example 4: Transfer between accounts (Synchronized required)

```kotlin
// - Synchronized - работа с несколькими объектами
class Bank {
    fun transfer(from: BankAccount, to: BankAccount, amount: Int) {
        // Блокируем ОБА аккаунта в фиксированном порядке (избежать deadlock)
        val (first, second) = if (from.id < to.id) {
            from to to
        } else {
            to to from
        }

        synchronized(first) {
            synchronized(second) {
                if (from.balance >= amount) {
                    from.balance -= amount
                    to.balance += amount
                }
            }
        }
    }
}

// - Atomic НЕ ПОМОЖЕТ - нужна координация между аккаунтами
```

### Performance comparison

```kotlin
// Benchmark (примерные результаты)
class BenchmarkCounter {
    @Volatile
    private var volatileCount = 0

    private val atomicCount = AtomicInteger(0)

    private var syncCount = 0
    private val lock = Any()

    // AtomicInteger: ~30 ns per operation
    fun incrementAtomic() {
        atomicCount.incrementAndGet()
    }

    // Synchronized: ~60 ns per operation
    fun incrementSync() = synchronized(lock) {
        syncCount++
    }

    // @Volatile: НЕ ПОТОКОБЕЗОПАСНО для increment!
    fun incrementVolatile() {
        volatileCount++  // Race condition!
    }
}
```

**Result**: Atomic ~2x faster than synchronized for simple operations.

### Atomic variable types

```kotlin
// Примитивы
val atomicInt = AtomicInteger(0)
val atomicLong = AtomicLong(0L)
val atomicBool = AtomicBoolean(false)

// Ссылки
val atomicRef = AtomicReference<User>(null)

// Массивы
val atomicIntArray = AtomicIntegerArray(10)
val atomicRefArray = AtomicReferenceArray<String>(10)

// Поля (через Updater)
class Counter {
    @Volatile
    private var count = 0

    companion object {
        private val UPDATER = AtomicIntegerFieldUpdater.newUpdater(
            Counter::class.java,
            "count"
        )
    }

    fun increment() {
        UPDATER.incrementAndGet(this)
    }
}
```

### Compare-and-Swap (CAS) pattern

The foundation of atomic operations - CAS loop.

```kotlin
class CASExample {
    private val atomicValue = AtomicInteger(0)

    // CAS loop for complex logic
    fun updateWithFunction(updateFn: (Int) -> Int) {
        while (true) {
            val current = atomicValue.get()
            val updated = updateFn(current)

            if (atomicValue.compareAndSet(current, updated)) {
                break  // Successfully updated
            }
            // Retry if another thread changed the value
        }
    }

    // Usage
    fun incrementIfEven() {
        updateWithFunction { current ->
            if (current % 2 == 0) current + 1 else current
        }
    }
}
```

### When NOT to use either

For Android - use high-level abstractions:

```kotlin
// - Coroutines with Mutex
class SafeCache {
    private val cache = mutableMapOf<String, String>()
    private val mutex = Mutex()

    suspend fun put(key: String, value: String) {
        mutex.withLock {
            cache[key] = value
        }
    }

    suspend fun get(key: String): String? {
        return mutex.withLock {
            cache[key]
        }
    }
}

// - Actor for sequential processing
@OptIn(ObsoleteCoroutinesApi::class)
fun cacheActor() = actor<CacheCommand> {
    val cache = mutableMapOf<String, String>()

    for (cmd in channel) {
        when (cmd) {
            is CacheCommand.Put -> cache[cmd.key] = cmd.value
            is CacheCommand.Get -> cmd.response.complete(cache[cmd.key])
        }
    }
}

sealed class CacheCommand {
    data class Put(val key: String, val value: String) : CacheCommand()
    data class Get(val key: String, val response: CompletableDeferred<String?>) : CacheCommand()
}
```

### Best Practices

**1. Prefer Atomic for simple cases**

```kotlin
// - ПРАВИЛЬНО
class Statistics {
    private val requestCount = AtomicLong(0)
    private val errorCount = AtomicLong(0)

    fun recordRequest() {
        requestCount.incrementAndGet()
    }

    fun recordError() {
        errorCount.incrementAndGet()
    }
}
```

**2. Use Synchronized for complex logic**

```kotlin
// - CORRECT
class ResourcePool<T>(private val factory: () -> T) {
    private val available = mutableListOf<T>()
    private val lock = Any()

    fun acquire(): T = synchronized(lock) {
        if (available.isEmpty()) {
            factory()
        } else {
            available.removeAt(available.size - 1)
        }
    }

    fun release(resource: T) = synchronized(lock) {
        available.add(resource)
    }
}
```

**3. Avoid mixing**

```kotlin
// - INCORRECT - mixing approaches
class BadExample {
    private val atomicCount = AtomicInteger(0)
    private var syncCount = 0
    private val lock = Any()

    fun update() {
        atomicCount.incrementAndGet()
        synchronized(lock) {
            syncCount++  // Different synchronization mechanisms!
        }
    }
}
```

**4. In Android use coroutines**

```kotlin
// - BEST APPROACH for Android
class DataRepository {
    private val cache = mutableMapOf<String, Data>()

    suspend fun getData(key: String) = withContext(Dispatchers.IO) {
        cache[key] ?: loadData(key).also { cache[key] = it }
    }
}
```

### Comparison table

| Aspect | Atomic | Synchronized |
|--------|--------|--------------|
| **Operations** | Single | Multiple |
| **Variables** | One | Multiple |
| **Performance** |  Faster |  Slower |
| **Logic complexity** | - Simple only | - Any |
| **Lock-free** | - Yes | - No |
| **Deadlock risk** | - No | WARNING: Possible |
| **Use case** | Counters, flags | Caches, collections |

**English**: Use **Atomic** variables (`AtomicInteger`, `AtomicReference`) for single operations on single variable (counters, flags) - lock-free, ~2x faster. Use **synchronized** for complex operations or multiple variables (caches, collections, multiple steps) - ensures mutual exclusion. Atomic uses CAS (Compare-And-Swap) loop. For Android, prefer coroutines with `Mutex` or `actor` pattern. Don't mix approaches. Atomic: simple & fast. Synchronized: complex & safe.

## Ответ (RU)

Используйте **Atomic** переменные (`AtomicInteger`, `AtomicReference`) для одиночных операций с одной переменной (счетчики, флаги) - lock-free, примерно в 2 раза быстрее. Используйте **synchronized** для сложных операций или работы с несколькими переменными (кеши, коллекции, множественные шаги) - обеспечивает взаимное исключение.

### Когда использовать Atomic

- Простой счетчик
- Флаг (boolean)
- Одна ссылка
- Read-modify-write операция для ОДНОЙ переменной
- Compare-and-swap логика

### Когда использовать Synchronized

- Работа с несколькими переменными
- Сложная логика (if-else, циклы)
- Вызовы методов внутри критической секции
- Нужна взаимная эксклюзивность
- Работа с коллекциями

Atomic использует CAS (Compare-And-Swap) цикл. Для Android предпочитайте корутины с `Mutex` или паттерн `actor`. Не смешивайте подходы. Atomic: просто и быстро. Synchronized: сложно и безопасно.

