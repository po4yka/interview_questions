---
id: kotlin-146
title: "Atomic vs Synchronized / Atomic против Synchronized"
aliases: [Atomic vs Synchronized, Atomic против Synchronized]
topic: kotlin
subtopics: [concurrency, thread-safety]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-continuation-cps-internals--kotlin--hard, q-kotlin-flow-basics--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [atomic, concurrency, difficulty/medium, java, kotlin, synchronized, thread-safety]
---

# Вопрос (RU)

> Когда в Kotlin использовать атомарные переменные (`Atomic*`) вместо `synchronized`, и наоборот?

# Question (EN)

> When should you use atomic variables (`Atomic*`) vs `synchronized` in Kotlin?

## Ответ (RU)

Используйте **Atomic** переменные (`AtomicInteger`, `AtomicReference` и т.п.) для одиночных операций с одной переменной (счетчики, флаги) и простых read-modify-write операций. Они основаны на CAS (Compare-And-Swap) циклах, не требуют явных пользовательских блокировок и обычно быстрее для простых сценариев. Однако реальная производительность зависит от JVM/платформы, уровня конкуренции (contention) и профиля нагрузки.

Важно: атомарные переменные обеспечивают атомарность и видимость только для СВОЕГО значения и не защищают инварианты между несколькими переменными.

Используйте **`synchronized`** для сложных операций или работы с несколькими переменными/объектами (кеши, коллекции, переводы между счетами, поддержание инвариантов), когда требуется взаимное исключение и единая критическая секция. Подходит для произвольной сложной логики внутри блока.

Ниже приведены примеры и детали, полностью соответствующие английской секции.

### Atomic переменные — для простых операций

Используйте для:
- простого счетчика;
- флага (boolean);
- одной ссылки;
- read-modify-write операции для ОДНОЙ переменной;
- логики compare-and-swap.

Основаны на атомарных инструкциях (CAS), выполняются без явных lock-объектов.

```kotlin
import java.util.concurrent.atomic.AtomicInteger
import kotlin.concurrent.thread

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
val threads = List(1000) {
    thread {
        counter.increment()
    }
}
threads.forEach { it.join() }
// При корректном ожидании потоков: counter.get() == 1000
```

### `synchronized` — для сложных операций

Используйте для:
- работы с несколькими переменными или объектами;
- сложной логики (if-else, циклы, несколько шагов);
- вызовов методов внутри критической секции;
- работы с коллекциями и сложными инвариантами;
- случаев, когда нужна строгая взаимная эксклюзивность.

```kotlin
// Synchronized блоки
class BankAccount(
    val id: Long
) {
    // Поле используется только под синхронизацией на this
    private var _balance = 0

    val balance: Int
        get() = synchronized(this) { _balance }

    // Операция с ОДНОЙ переменной, но в НЕСКОЛЬКО шагов — нужна единая критическая секция
    fun deposit(amount: Int) = synchronized(this) {
        if (amount > 0) {
            _balance += amount
            logTransaction("Deposit: $amount")  // Дополнительная логика
        }
    }

    fun withdraw(amount: Int): Boolean = synchronized(this) {
        if (_balance >= amount) {
            _balance -= amount
            logTransaction("Withdraw: $amount")
            true
        } else {
            false
        }
    }

    private fun logTransaction(msg: String) {
        // Логирование (если трогает состояние, также должно быть потокобезопасным)
    }
}
```

### Примеры использования

#### Пример 1: Счетчик (Atomic лучше)

```kotlin
import java.util.concurrent.atomic.AtomicLong

// Atomic — идеально для счетчика
class RequestCounterAtomic {
    private val count = AtomicLong(0)

    fun increment() {
        count.incrementAndGet()
    }

    fun getCount(): Long = count.get()
}

// Synchronized — избыточно для такой простой операции
class RequestCounterSync {
    private var count = 0L
    private val lock = Any()

    fun increment() = synchronized(lock) {
        count++
    }

    fun getCount(): Long = synchronized(lock) { count }
}
```

#### Пример 2: Cache с TTL (`synchronized` лучше)

```kotlin
// Synchronized — нужен для сложной логики
class Cache<K, V>(private val ttlMs: Long) {
    private data class Entry<V>(
        val value: V,
        val timestamp: Long
    )

    private val cache = mutableMapOf<K, Entry<V>>()\
    private val lock = Any()

    fun put(key: K, value: V) = synchronized(lock) {
        cache[key] = Entry(value, System.currentTimeMillis())
        cleanupExpired()  // Дополнительная логика очистки
    }

    fun get(key: K): V? = synchronized(lock) {
        val entry = cache[key] ?: return@synchronized null
        return if (System.currentTimeMillis() - entry.timestamp > ttlMs) {
            cache.remove(key)
            null
        } else {
            entry.value
        }
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
import java.util.concurrent.atomic.AtomicBoolean

// Atomic — для простого флага
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

    fun isConnected(): Boolean = isConnected.get()

    private fun establishConnection() { /* ... */ }
    private fun closeConnection() { /* ... */ }
}
```

#### Пример 4: Перевод между счетами (`synchronized` обязателен)

Важно: все операции с `BankAccount` должны использовать один и тот же монитор (например, `synchronized(this)`), иначе возможны гонки.

```kotlin
// Synchronized — работа с несколькими объектами
class Bank {
    fun transfer(from: BankAccount, to: BankAccount, amount: Int) {
        // Блокируем оба аккаунта в фиксированном порядке (избежать deadlock)
        val (first, second) = if (from.id < to.id) {
            from to to
        } else {
            to to from
        }

        synchronized(first) {
            synchronized(second) {
                // Используем только методы, которые сами синхронизируют доступ к балансу
                if (from.withdraw(amount)) {
                    to.deposit(amount)
                }
            }
        }
    }
}

// Atomic здесь не помогает — нужна координация между аккаунтами и единая критическая секция
```

### Сравнение производительности

Для простых операций атомарные переменные часто быстрее, чем `synchronized`, за счет lock-free реализации на CAS. Но:
- при высокой конкуренции CAS может многократно переотклоняться и терять преимущество;
- реальные цифры сильно зависят от JVM, архитектуры и профиля нагрузки.

```kotlin
import java.util.concurrent.atomic.AtomicInteger

// Упрощенный пример; реальные цифры зависят от JVM, нагрузки и contention
class BenchmarkCounter {
    @Volatile
    private var volatileCount = 0

    private val atomicCount = AtomicInteger(0)

    private var syncCount = 0
    private val lock = Any()

    fun incrementAtomic() {
        atomicCount.incrementAndGet()
    }

    fun incrementSync() = synchronized(lock) {
        syncCount++
    }

    // @Volatile: не потокобезопасно для increment!
    fun incrementVolatile() {
        volatileCount++  // Race condition!
    }
}
```

### Типы атомарных переменных

```kotlin
import java.util.concurrent.atomic.*

// Примитивы
val atomicInt = AtomicInteger(0)
val atomicLong = AtomicLong(0L)
val atomicBool = AtomicBoolean(false)

// Ссылки
val atomicRef = AtomicReference<User?>(null)

// Массивы
val atomicIntArray = AtomicIntegerArray(10)
val atomicRefArray = AtomicReferenceArray<String?>(10)

// Поля (через FieldUpdater)
class CounterFieldUpdater {
    @Volatile
    private var count = 0

    companion object {
        private val UPDATER = AtomicIntegerFieldUpdater.newUpdater(
            CounterFieldUpdater::class.java,
            "count"
        )
    }

    fun increment() {
        UPDATER.incrementAndGet(this)
    }
}
```

### Паттерн Compare-and-Swap (CAS)

Базовый принцип реализации атомарных операций — CAS-цикл: читаем текущее значение, вычисляем новое, пытаемся применить через `compareAndSet`; при неудаче повторяем.

```kotlin
import java.util.concurrent.atomic.AtomicInteger

class CASExample {
    private val atomicValue = AtomicInteger(0)

    // CAS-цикл для произвольной логики обновления
    fun updateWithFunction(updateFn: (Int) -> Int) {
        while (true) {
            val current = atomicValue.get()
            val updated = updateFn(current)

            if (atomicValue.compareAndSet(current, updated)) {
                break  // Успешно обновили
            }
            // Повтор, если значение изменил другой поток
        }
    }

    fun incrementIfEven() {
        updateWithFunction { current ->
            if (current % 2 == 0) current + 1 else current
        }
    }
}
```

### Когда НЕ использовать Atomic и `synchronized`

Во многих сценариях на Android/Kotlin предпочтительнее более высокоуровневые абстракции над потоками: корутины, `Mutex`, акторы.

```kotlin
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.ObsoleteCoroutinesApi
import kotlinx.coroutines.channels.actor
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

// Корутины с Mutex
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

// Актор для последовательной обработки
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

### Рекомендации (Best Practices)

1. Предпочитайте Atomic для простых независимых значений (счётчиков/флагов), не завязанных на общие инварианты с другими полями.

```kotlin
import java.util.concurrent.atomic.AtomicLong

// Правильно для независимых счетчиков/флагов
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

2. Используйте `synchronized` для сложной логики и общих инвариантов

```kotlin
// Вся работа с коллекцией под одним lock — корректно
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

3. Не смешивайте разные механизмы синхронизации для одного логического состояния

```kotlin
import java.util.concurrent.atomic.AtomicInteger

// Некорректно: смешение Atomic и synchronized для связанного состояния
class BadExample {
    private val atomicCount = AtomicInteger(0)
    private var syncCount = 0
    private val lock = Any()

    fun update() {
        atomicCount.incrementAndGet()
        synchronized(lock) {
            syncCount++
        }
    }
}
```

4. В Android по возможности используйте корутины и диспетчеры вместо ручных блокировок

```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

// Для многих задач в Android лучше использовать корутины и диспетчеры
class DataRepository {
    private val cache = mutableMapOf<String, Data>()

    suspend fun getData(key: String): Data = withContext(Dispatchers.IO) {
        cache[key] ?: loadData(key).also { cache[key] = it }
    }

    private fun loadData(key: String): Data {
        // Загрузка данных
        TODO()
    }
}
```

### Сводное сравнение

| Aspekt | Atomic | synchronized |
|--------|--------|--------------|
| Операции | Одинарные read/modify/write над одним значением | Произвольные/сложные критические секции |
| Переменные | Обычно одна | Одна или много |
| Производительность | Часто быстрее для простых операций | Дороже из-за входа/выхода из монитора |
| Сложность логики | Простая | Любая |
| Lock-free (API) | Да (CAS, без явных lock-объектов) | Нет (монитор/lock) |
| Риск deadlock | Нет (возможен livelock/ретраи) | Есть при неверном порядке lock'ов |
| Типичные случаи | Счетчики, флаги, простые ссылки | Кеши, коллекции, координированные обновления |

Кратко: Atomic — просто и эффективно для изолированных значений. `synchronized` — гибко и безопасно для сложного совместно используемого состояния и поддержания инвариантов.

## Answer (EN)

Use **Atomic** variables (`AtomicInteger`, `AtomicReference`, etc.) for single-variable, simple read-modify-write operations (counters, flags). They are CAS (Compare-And-Swap) based, lock-free at the API level, and typically faster for simple cases, but real performance depends on JVM/platform, contention, and workload.

Important: atomic variables only guarantee atomicity/visibility for THEIR OWN value; they do not protect invariants spanning multiple fields or objects.

Use **`synchronized`** for complex operations or when coordinating multiple variables/objects (caches, collections, transfers between accounts, invariants) where you need a single critical section and mutual exclusion. Suitable for arbitrary complex logic.

### Atomic Variables – for Simple Operations

Use when:
- simple counter;
- boolean flag;
- single reference;
- read-modify-write on ONE variable;
- compare-and-swap style updates.

Based on CAS instructions; no explicit user-managed lock objects.

```kotlin
import java.util.concurrent.atomic.AtomicInteger
import kotlin.concurrent.thread

class Counter {
    private val count = AtomicInteger(0)

    fun increment() {
        count.incrementAndGet()
    }

    fun decrement() {
        count.decrementAndGet()
    }

    fun get(): Int = count.get()

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

val counter = Counter()
val threads = List(1000) {
    thread {
        counter.increment()
    }
}
threads.forEach { it.join() }
```

### `synchronized` – for Complex Operations

Use when:
- multiple variables/objects must be updated together;
- complex branching/loops inside critical section;
- calling methods inside critical section;
- working with collections and invariants;
- strict mutual exclusion is required.

```kotlin
class BankAccount(
    val id: Long
) {
    // Field is accessed only under synchronization on this
    private var _balance = 0

    val balance: Int
        get() = synchronized(this) { _balance }

    // Multi-step operation on the same variable — needs one critical section
    fun deposit(amount: Int) = synchronized(this) {
        if (amount > 0) {
            _balance += amount
            logTransaction("Deposit: $amount")
        }
    }

    fun withdraw(amount: Int): Boolean = synchronized(this) {
        if (_balance >= amount) {
            _balance -= amount
            logTransaction("Withdraw: $amount")
            true
        } else {
            false
        }
    }

    private fun logTransaction(msg: String) {
        // Thread-safe logging if needed
    }
}
```

### Usage Examples

1) Counter (Atomic is better)

```kotlin
import java.util.concurrent.atomic.AtomicLong

class RequestCounterAtomic {
    private val count = AtomicLong(0)

    fun increment() {
        count.incrementAndGet()
    }

    fun getCount(): Long = count.get()
}

class RequestCounterSync {
    private var count = 0L
    private val lock = Any()

    fun increment() = synchronized(lock) {
        count++
    }

    fun getCount(): Long = synchronized(lock) { count }
}
```

2) Cache with TTL (`synchronized` is better)

```kotlin
class Cache<K, V>(private val ttlMs: Long) {
    private data class Entry<V>(
        val value: V,
        val timestamp: Long
    )

    private val cache = mutableMapOf<K, Entry<V>>()
    private val lock = Any()

    fun put(key: K, value: V) = synchronized(lock) {
        cache[key] = Entry(value, System.currentTimeMillis())
        cleanupExpired()
    }

    fun get(key: K): V? = synchronized(lock) {
        val entry = cache[key] ?: return@synchronized null
        return if (System.currentTimeMillis() - entry.timestamp > ttlMs) {
            cache.remove(key)
            null
        } else {
            entry.value
        }
    }

    private fun cleanupExpired() {
        val now = System.currentTimeMillis()
        cache.entries.removeIf { (_, entry) ->
            now - entry.timestamp > ttlMs
        }
    }
}
```

3) State Flag (Atomic is simpler)

```kotlin
import java.util.concurrent.atomic.AtomicBoolean

class ConnectionManager {
    private val isConnected = AtomicBoolean(false)

    fun connect() {
        if (isConnected.compareAndSet(false, true)) {
            establishConnection()
        }
    }

    fun disconnect() {
        if (isConnected.compareAndSet(true, false)) {
            closeConnection()
        }
    }

    fun isConnected(): Boolean = isConnected.get()

    private fun establishConnection() { /* ... */ }
    private fun closeConnection() { /* ... */ }
}
```

4) Transfer between Accounts (`synchronized` required)

```kotlin
class Bank {
    fun transfer(from: BankAccount, to: BankAccount, amount: Int) {
        val (first, second) = if (from.id < to.id) {
            from to to
        } else {
            to to from
        }

        synchronized(first) {
            synchronized(second) {
                if (from.withdraw(amount)) {
                    to.deposit(amount)
                }
            }
        }
    }
}

// Atomic alone is not enough; you need one coordinated critical section.
```

### Performance Considerations

Atomic variables can be significantly faster for simple operations, but:
- under high contention, CAS retries may reduce or negate benefits;
- actual performance depends on JVM, CPU, and workload.

```kotlin
import java.util.concurrent.atomic.AtomicInteger

class BenchmarkCounter {
    @Volatile
    private var volatileCount = 0

    private val atomicCount = AtomicInteger(0)

    private var syncCount = 0
    private val lock = Any()

    fun incrementAtomic() {
        atomicCount.incrementAndGet()
    }

    fun incrementSync() = synchronized(lock) {
        syncCount++
    }

    // @Volatile alone: not thread-safe for increment!
    fun incrementVolatile() {
        volatileCount++  // Race condition!
    }
}
```

### Atomic Variable Types

```kotlin
import java.util.concurrent.atomic.*

val atomicInt = AtomicInteger(0)
val atomicLong = AtomicLong(0L)
val atomicBool = AtomicBoolean(false)

val atomicRef = AtomicReference<User?>(null)

val atomicIntArray = AtomicIntegerArray(10)
val atomicRefArray = AtomicReferenceArray<String?>(10)

class CounterFieldUpdater {
    @Volatile
    private var count = 0

    companion object {
        private val UPDATER = AtomicIntegerFieldUpdater.newUpdater(
            CounterFieldUpdater::class.java,
            "count"
        )
    }

    fun increment() {
        UPDATER.incrementAndGet(this)
    }
}
```

### Compare-and-Swap (CAS) Pattern

Atomic operations are typically built on CAS loops.

```kotlin
import java.util.concurrent.atomic.AtomicInteger

class CASExample {
    private val atomicValue = AtomicInteger(0)

    fun updateWithFunction(updateFn: (Int) -> Int) {
        while (true) {
            val current = atomicValue.get()
            val updated = updateFn(current)

            if (atomicValue.compareAndSet(current, updated)) {
                break
            }
            // retry on conflict
        }
    }

    fun incrementIfEven() {
        updateWithFunction { current ->
            if (current % 2 == 0) current + 1 else current
        }
    }
}
```

### When NOT to Use Either

On Android/Kotlin, prefer higher-level concurrency primitives when possible: coroutines, `Mutex`, actors, structured concurrency.

```kotlin
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.ObsoleteCoroutinesApi
import kotlinx.coroutines.channels.actor
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

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

1) Prefer Atomic for simple independent state (counters/flags not tied to shared invariants)

```kotlin
import java.util.concurrent.atomic.AtomicLong

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

2) Use `synchronized` for complex/compound state and invariants

```kotlin
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

3) Avoid mixing synchronization mechanisms for the same logical state

```kotlin
import java.util.concurrent.atomic.AtomicInteger

class BadExample {
    private val atomicCount = AtomicInteger(0)
    private var syncCount = 0
    private val lock = Any()

    fun update() {
        atomicCount.incrementAndGet()
        synchronized(lock) {
            syncCount++
        }
    }
}
```

4) On Android, favor coroutines/Dispatchers instead of manual threads/locks when appropriate

```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class DataRepository {
    private val cache = mutableMapOf<String, Data>()

    suspend fun getData(key: String): Data = withContext(Dispatchers.IO) {
        cache[key] ?: loadData(key).also { cache[key] = it }
    }

    private fun loadData(key: String): Data {
        // Load data
        TODO()
    }
}
```

### Comparison Table

| Aspect | Atomic | synchronized |
|--------|--------|--------------|
| Operations | Single read/modify/write on one value | Arbitrary complex critical sections |
| Variables | Typically one | One or many |
| Performance | Usually faster for simple ops | Higher cost (monitor enter/exit) |
| Logic complexity | Simple | Any |
| Lock-free (API) | Yes (CAS-based) | No (uses monitor/lock) |
| Deadlock risk | None (but possible livelock/retries) | Yes if locks ordered incorrectly |
| Use case | Counters, flags, simple references | Caches, collections, coordinated updates |

In short: Atomic is simple and efficient for isolated values. `synchronized` is flexible and safe for complex shared state and invariants.

## Дополнительные вопросы (RU)

- В чем ключевые отличия использования Atomic/`synchronized` в Kotlin по сравнению с Java?
- В каких реальных сценариях Android/Kotlin-кода вы бы выбрали Atomic, а в каких — `synchronized` или корутины?
- Каковы типичные ошибки при работе с Atomic и `synchronized` (например, смешение механизмов, забытые инварианты)?

## Follow-ups

- What are the key differences between this and Java usage?
- When would you use this in real-world Android/Kotlin code?
- What common pitfalls should be avoided (e.g., mixing mechanisms, broken invariants)?

## Ссылки (RU)

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Связанные вопросы (RU)

- [[q-continuation-cps-internals--kotlin--hard]]
- [[q-kotlin-flow-basics--kotlin--medium]]

## Related Questions

- [[q-continuation-cps-internals--kotlin--hard]]
- [[q-kotlin-flow-basics--kotlin--medium]]
