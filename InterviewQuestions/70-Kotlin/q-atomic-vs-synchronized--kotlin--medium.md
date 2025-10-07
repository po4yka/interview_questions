---
tags:
  - kotlin
  - java
  - concurrency
  - thread-safety
  - atomic
  - synchronized
difficulty: medium
status: draft
---

# Atomic vs Synchronized: когда использовать

**English**: When to use atomic variables vs synchronized?

## Answer

**Atomic** переменные (`AtomicInteger`, `AtomicReference`) и **synchronized** блоки — два способа обеспечить потокобезопасность. Используются в разных ситуациях в зависимости от сложности операций.

### Atomic Variables — для простых операций

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

**Когда использовать Atomic:**
- ✅ Простой счетчик
- ✅ Флаг (boolean)
- ✅ Одиночная ссылка
- ✅ Операция читай-изменяй-запиши для ОДНОЙ переменной
- ✅ Compare-and-swap логика

### Synchronized — для сложных операций

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

**Когда использовать Synchronized:**
- ✅ Работа с несколькими переменными
- ✅ Сложная логика (if-else, циклы)
- ✅ Вызов методов внутри критической секции
- ✅ Нужна взаимная исключительность (mutual exclusion)
- ✅ Работа с коллекциями

### Примеры использования

#### Пример 1: Счетчик (Atomic лучше)

```kotlin
// ✅ Atomic - идеально для счетчика
class RequestCounter {
    private val count = AtomicLong(0)

    fun increment() {
        count.incrementAndGet()
    }

    fun getCount() = count.get()
}

// ❌ Synchronized - избыточно
class RequestCounter {
    private var count = 0L
    private val lock = Any()

    fun increment() = synchronized(lock) {
        count++  // Overkill для простой операции
    }

    fun getCount() = synchronized(lock) { count }
}
```

#### Пример 2: Cache с TTL (Synchronized лучше)

```kotlin
// ✅ Synchronized - нужен для сложной логики
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

#### Пример 3: Флаг состояния (Atomic проще)

```kotlin
// ✅ Atomic - для простого флага
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

#### Пример 4: Transfer между аккаунтами (Synchronized обязателен)

```kotlin
// ✅ Synchronized - работа с несколькими объектами
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

// ❌ Atomic НЕ ПОМОЖЕТ - нужна координация между аккаунтами
```

### Performance сравнение

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

**Результат**: Atomic в ~2 раза быстрее synchronized для простых операций.

### Типы Atomic переменных

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

### Compare-and-Swap (CAS) паттерн

Основа atomic операций — CAS loop.

```kotlin
class CASExample {
    private val atomicValue = AtomicInteger(0)

    // CAS loop для сложной логики
    fun updateWithFunction(updateFn: (Int) -> Int) {
        while (true) {
            val current = atomicValue.get()
            val updated = updateFn(current)

            if (atomicValue.compareAndSet(current, updated)) {
                break  // Успешно обновили
            }
            // Retry если другой поток изменил значение
        }
    }

    // Использование
    fun incrementIfEven() {
        updateWithFunction { current ->
            if (current % 2 == 0) current + 1 else current
        }
    }
}
```

### Когда НЕ использовать ни то, ни другое

Для Android — используйте высокоуровневые абстракции:

```kotlin
// ✅ Корутины с Mutex
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

// ✅ Actor для sequential processing
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

**1. Предпочитайте Atomic для простых случаев**

```kotlin
// ✅ ПРАВИЛЬНО
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

**2. Используйте Synchronized для сложной логики**

```kotlin
// ✅ ПРАВИЛЬНО
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

**3. Избегайте смешивания**

```kotlin
// ❌ НЕПРАВИЛЬНО - смешивание подходов
class BadExample {
    private val atomicCount = AtomicInteger(0)
    private var syncCount = 0
    private val lock = Any()

    fun update() {
        atomicCount.incrementAndGet()
        synchronized(lock) {
            syncCount++  // Разные механизмы синхронизации!
        }
    }
}
```

**4. В Android используйте корутины**

```kotlin
// ✅ ЛУЧШИЙ ПОДХОД для Android
class DataRepository {
    private val cache = mutableMapOf<String, Data>()

    suspend fun getData(key: String) = withContext(Dispatchers.IO) {
        cache[key] ?: loadData(key).also { cache[key] = it }
    }
}
```

### Сравнительная таблица

| Аспект | Atomic | Synchronized |
|--------|--------|--------------|
| **Операции** | Одиночные | Множественные |
| **Переменные** | Одна | Несколько |
| **Performance** | ⚡ Быстрее | 🐢 Медленнее |
| **Сложность логики** | ❌ Простая только | ✅ Любая |
| **Lock-free** | ✅ Да | ❌ Нет |
| **Deadlock риск** | ✅ Нет | ⚠️ Возможен |
| **Use case** | Счетчики, флаги | Кэши, коллекции |

**English**: Use **Atomic** variables (`AtomicInteger`, `AtomicReference`) for single operations on single variable (counters, flags) - lock-free, ~2x faster. Use **synchronized** for complex operations or multiple variables (caches, collections, multiple steps) - ensures mutual exclusion. Atomic uses CAS (Compare-And-Swap) loop. For Android, prefer coroutines with `Mutex` or `actor` pattern. Don't mix approaches. Atomic: simple & fast. Synchronized: complex & safe.
