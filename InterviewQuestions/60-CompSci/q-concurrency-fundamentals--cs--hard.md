---
id: cs-003
title: "Concurrency Fundamentals / Основы параллелизма"
aliases: ["Concurrency Fundamentals", "Основы параллелизма"]
topic: cs
subtopics: [concurrency, multithreading, synchronization]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-concurrency]
created: 2025-10-12
updated: 2025-01-25
tags: [concurrency, difficulty/hard, multithreading, mutexes, race-conditions, synchronization]
sources: [https://en.wikipedia.org/wiki/Concurrency_(computer_science)]
---

# Вопрос (RU)
> Что такое concurrency vs parallelism? Что такое race conditions и как их предотвратить? Что такое mutexes, semaphores и monitors? Как избежать deadlocks?

# Question (EN)
> What is concurrency vs parallelism? What are race conditions and how to prevent them? What are mutexes, semaphores, and monitors? How do you avoid deadlocks?

---

## Ответ (RU)

**Теория параллелизма:**
Concurrency - способность выполнять несколько задач с прогрессом (не обязательно одновременно). Parallelism - истинное одновременное выполнение на нескольких ядрах. Критические концепции: race conditions, synchronization primitives, deadlocks, thread-safe структуры данных.

**1. Concurrency vs Parallelism:**

*Теория:*
- **Concurrency** - множество задач делают прогресс (не обязательно одновременно). О работе с несколькими вещами сразу. Достигается даже на одном ядре через time-slicing (переключение контекста).
- **Parallelism** - множество задач выполняются одновременно. О выполнении нескольких вещей сразу. Требует несколько ядер CPU.

*Аналогия:*
- **Concurrency**: Один повар готовит несколько блюд (ставит пасту, пока она варится - режет овощи, пока овощи готовятся - делает соус)
- **Parallelism**: Несколько поваров готовят одновременно (повар 1 - паста, повар 2 - салат, повар 3 - десерт)

```kotlin
// ✅ Concurrency: Coroutines (могут работать на одном потоке)
suspend fun fetchDataConcurrently() {
    val user = async { fetchUser() }      // Suspend, не блокирует
    val posts = async { fetchPosts() }    // Могут чередоваться
    // Concurrent, но могут использовать один поток
    println("${user.await()} has ${posts.await().size} posts")
}

// ✅ Parallelism: Множество потоков
fun fetchDataInParallel() {
    val executor = Executors.newFixedThreadPool(2)  // 2 потока
    val userFuture = executor.submit { fetchUser() }    // Поток 1
    val postsFuture = executor.submit { fetchPosts() }  // Поток 2
    // Истинный параллелизм на multi-core CPU
    println("${userFuture.get()} has ${postsFuture.get().size} posts")
}
```

**2. Race Conditions:**

*Теория:* Race condition - ситуация, когда несколько потоков обращаются к shared data, хотя бы один модифицирует, и результат зависит от timing. Происходит из-за non-atomic операций (например, `count++` = read + add + write).

```kotlin
// ❌ Race condition
class Counter {
    private var count = 0

    fun increment() {
        count++  // НЕ атомарно! 3 операции:
                 // 1. Read count
                 // 2. Add 1
                 // 3. Write count
    }
}

// Проблема: 1000 потоков × 1000 инкрементов = ожидаем 1,000,000
// Получаем: ~950,000 (варьируется!)

// ✅ Решение 1: synchronized
class SafeCounter {
    private var count = 0
    private val lock = Any()

    fun increment() {
        synchronized(lock) {
            count++  // Только один поток одновременно
        }
    }
}

// ✅ Решение 2: AtomicInteger
class AtomicCounter {
    private val count = AtomicInteger(0)

    fun increment() {
        count.incrementAndGet()  // Атомарная операция
    }
}
```

**3. Synchronization Primitives:**

**Mutex (Mutual Exclusion Lock):**

*Теория:* Mutex - примитив синхронизации, позволяющий только одному потоку владеть lock одновременно. Другие потоки блокируются до unlock. Используется для защиты critical section.

```kotlin
// ✅ Mutex с ReentrantLock
class BankAccount {
    private var balance = 0
    private val lock = ReentrantLock()

    fun deposit(amount: Int) {
        lock.lock()
        try {
            balance += amount
        } finally {
            lock.unlock()  // Всегда unlock в finally
        }
    }

    fun withdraw(amount: Int): Boolean {
        lock.lock()
        try {
            if (balance >= amount) {
                balance -= amount
                return true
            }
            return false
        } finally {
            lock.unlock()
        }
    }
}
```

**Semaphore:**

*Теория:* Semaphore - счётчик, ограничивающий количество потоков, которые могут получить доступ к ресурсу одновременно. Mutex = semaphore с count=1. Используется для resource pooling (например, connection pool).

```kotlin
// ✅ Semaphore для connection pool
class ConnectionPool(maxConnections: Int) {
    private val semaphore = Semaphore(maxConnections)
    private val connections = mutableListOf<Connection>()

    fun acquireConnection(): Connection {
        semaphore.acquire()  // Блокируется если нет доступных
        return connections.removeFirst()
    }

    fun releaseConnection(conn: Connection) {
        connections.add(conn)
        semaphore.release()  // Освобождает слот
    }
}
```

**Monitor (synchronized):**

*Теория:* Monitor - высокоуровневый примитив, комбинирующий mutex + condition variables. В Java/Kotlin - `synchronized` блоки. Автоматически управляет lock + позволяет wait/notify.

```kotlin
// ✅ Monitor pattern: Producer-Consumer
class BlockingQueue<T>(private val capacity: Int) {
    private val queue = LinkedList<T>()

    @Synchronized
    fun put(item: T) {
        while (queue.size >= capacity) {
            (this as Object).wait()  // Ждём, пока не освободится место
        }
        queue.add(item)
        (this as Object).notifyAll()  // Уведомляем consumers
    }

    @Synchronized
    fun take(): T {
        while (queue.isEmpty()) {
            (this as Object).wait()  // Ждём, пока не появится элемент
        }
        val item = queue.removeFirst()
        (this as Object).notifyAll()  // Уведомляем producers
        return item
    }
}
```

**4. Deadlocks:**

*Теория:* Deadlock - ситуация, когда два или более потока ждут друг друга бесконечно. Возникает при выполнении 4 условий Coffman: mutual exclusion, hold and wait, no preemption, circular wait.

```kotlin
// ❌ Deadlock пример
class Account(val id: Int, var balance: Int)

fun transfer(from: Account, to: Account, amount: Int) {
    synchronized(from) {              // Поток 1: lock A
        Thread.sleep(10)
        synchronized(to) {            // Поток 1: ждёт lock B
            from.balance -= amount
            to.balance += amount
        }
    }
}

// Deadlock:
// Thread 1: transfer(accountA, accountB, 100) - locks A, waits for B
// Thread 2: transfer(accountB, accountA, 50)  - locks B, waits for A
// Circular wait!

// ✅ Решение: Lock ordering
fun transferSafe(from: Account, to: Account, amount: Int) {
    val first = if (from.id < to.id) from else to
    val second = if (from.id < to.id) to else from

    synchronized(first) {   // Всегда блокируем в одном порядке
        synchronized(second) {
            from.balance -= amount
            to.balance += amount
        }
    }
}
```

**Предотвращение Deadlocks:**

1. **Lock ordering** - всегда блокировать в одном порядке
2. **Lock timeout** - использовать `tryLock(timeout)`
3. **Deadlock detection** - мониторинг и recovery
4. **Avoid nested locks** - минимизировать вложенные блокировки
5. **Use higher-level primitives** - channels, actors вместо низкоуровневых locks

**5. Thread-Safe Data Structures:**

*Теория:* Thread-safe структуры данных используют внутреннюю синхронизацию. Примеры: `ConcurrentHashMap`, `CopyOnWriteArrayList`, `BlockingQueue`. Trade-off: безопасность vs производительность.

```kotlin
// ✅ Thread-safe collections
val map = ConcurrentHashMap<String, Int>()
map.put("key", 1)  // Thread-safe

val queue = LinkedBlockingQueue<String>()
queue.put("item")  // Блокирующая операция, thread-safe

// ✅ Atomic variables
val counter = AtomicInteger(0)
counter.incrementAndGet()  // Атомарная операция

val reference = AtomicReference<User>(null)
reference.compareAndSet(null, newUser)  // CAS operation
```

**6. Ключевые концепции:**

**Visibility:**
*Теория:* Изменения одного потока могут быть не видны другим из-за CPU cache. `volatile` гарантирует visibility (но не atomicity).

```kotlin
// ❌ Без volatile - может зависнуть
class Task {
    private var running = true

    fun run() {
        while (running) {  // Может кешироваться в CPU cache
            // work
        }
    }

    fun stop() {
        running = false  // Может не быть видно другому потоку
    }
}

// ✅ С volatile
class SafeTask {
    @Volatile
    private var running = true  // Гарантирует visibility

    fun run() {
        while (running) {
            // work
        }
    }

    fun stop() {
        running = false  // Сразу видно всем потокам
    }
}
```

**Happens-Before:**
*Теория:* Happens-before relationship - гарантия, что операция A видна операции B. Устанавливается через: volatile, synchronized, thread start/join, lock acquire/release.

**Ключевые правила:**

1. **Minimize shared state** - меньше shared data = меньше проблем
2. **Immutability** - immutable объекты thread-safe по определению
3. **Use high-level primitives** - coroutines, actors вместо низкоуровневых threads
4. **Avoid premature optimization** - сначала корректность, потом производительность
5. **Test thoroughly** - concurrency bugs сложно воспроизвести

## Answer (EN)

**Concurrency Theory:**
Concurrency - ability to execute multiple tasks with progress (not necessarily simultaneously). Parallelism - true simultaneous execution on multiple cores. Critical concepts: race conditions, synchronization primitives, deadlocks, thread-safe data structures.

**1. Concurrency vs Parallelism:**

*Theory:*
- **Concurrency** - multiple tasks making progress (not necessarily simultaneously). About dealing with multiple things at once. Achieved even on single core through time-slicing (context switching).
- **Parallelism** - multiple tasks executing simultaneously. About doing multiple things at once. Requires multiple CPU cores.

*Analogy:*
- **Concurrency**: One chef cooking multiple dishes (starts pasta, while it cooks - chops vegetables, while vegetables cook - makes sauce)
- **Parallelism**: Multiple chefs cooking simultaneously (chef 1 - pasta, chef 2 - salad, chef 3 - dessert)

```kotlin
// ✅ Concurrency: Coroutines (can run on single thread)
suspend fun fetchDataConcurrently() {
    val user = async { fetchUser() }      // Suspend, doesn't block
    val posts = async { fetchPosts() }    // Can interleave
    // Concurrent, but may use same thread
    println("${user.await()} has ${posts.await().size} posts")
}

// ✅ Parallelism: Multiple threads
fun fetchDataInParallel() {
    val executor = Executors.newFixedThreadPool(2)  // 2 threads
    val userFuture = executor.submit { fetchUser() }    // Thread 1
    val postsFuture = executor.submit { fetchPosts() }  // Thread 2
    // True parallelism on multi-core CPU
    println("${userFuture.get()} has ${postsFuture.get().size} posts")
}
```

**2. Race Conditions:**

*Theory:* Race condition - situation when multiple threads access shared data, at least one modifies, and result depends on timing. Occurs due to non-atomic operations (e.g., `count++` = read + add + write).

```kotlin
// ❌ Race condition
class Counter {
    private var count = 0

    fun increment() {
        count++  // NOT atomic! 3 operations:
                 // 1. Read count
                 // 2. Add 1
                 // 3. Write count
    }
}

// Problem: 1000 threads × 1000 increments = expect 1,000,000
// Get: ~950,000 (varies!)

// ✅ Solution 1: synchronized
class SafeCounter {
    private var count = 0
    private val lock = Any()

    fun increment() {
        synchronized(lock) {
            count++  // Only one thread at a time
        }
    }
}

// ✅ Solution 2: AtomicInteger
class AtomicCounter {
    private val count = AtomicInteger(0)

    fun increment() {
        count.incrementAndGet()  // Atomic operation
    }
}
```

**3. Synchronization Primitives:**

**Mutex (Mutual Exclusion Lock):**

*Theory:* Mutex - synchronization primitive allowing only one thread to own lock at a time. Other threads block until unlock. Used to protect critical section.

```kotlin
// ✅ Mutex with ReentrantLock
class BankAccount {
    private var balance = 0
    private val lock = ReentrantLock()

    fun deposit(amount: Int) {
        lock.lock()
        try {
            balance += amount
        } finally {
            lock.unlock()  // Always unlock in finally
        }
    }

    fun withdraw(amount: Int): Boolean {
        lock.lock()
        try {
            if (balance >= amount) {
                balance -= amount
                return true
            }
            return false
        } finally {
            lock.unlock()
        }
    }
}
```

**Semaphore:**

*Theory:* Semaphore - counter limiting number of threads that can access resource simultaneously. Mutex = semaphore with count=1. Used for resource pooling (e.g., connection pool).

```kotlin
// ✅ Semaphore for connection pool
class ConnectionPool(maxConnections: Int) {
    private val semaphore = Semaphore(maxConnections)
    private val connections = mutableListOf<Connection>()

    fun acquireConnection(): Connection {
        semaphore.acquire()  // Blocks if none available
        return connections.removeFirst()
    }

    fun releaseConnection(conn: Connection) {
        connections.add(conn)
        semaphore.release()  // Frees slot
    }
}
```

**Monitor (synchronized):**

*Theory:* Monitor - high-level primitive combining mutex + condition variables. In Java/Kotlin - `synchronized` blocks. Automatically manages lock + allows wait/notify.

```kotlin
// ✅ Monitor pattern: Producer-Consumer
class BlockingQueue<T>(private val capacity: Int) {
    private val queue = LinkedList<T>()

    @Synchronized
    fun put(item: T) {
        while (queue.size >= capacity) {
            (this as Object).wait()  // Wait until space available
        }
        queue.add(item)
        (this as Object).notifyAll()  // Notify consumers
    }

    @Synchronized
    fun take(): T {
        while (queue.isEmpty()) {
            (this as Object).wait()  // Wait until item available
        }
        val item = queue.removeFirst()
        (this as Object).notifyAll()  // Notify producers
        return item
    }
}
```

**4. Deadlocks:**

*Theory:* Deadlock - situation when two or more threads wait for each other infinitely. Occurs when 4 Coffman conditions met: mutual exclusion, hold and wait, no preemption, circular wait.

```kotlin
// ❌ Deadlock example
class Account(val id: Int, var balance: Int)

fun transfer(from: Account, to: Account, amount: Int) {
    synchronized(from) {              // Thread 1: lock A
        Thread.sleep(10)
        synchronized(to) {            // Thread 1: waits for lock B
            from.balance -= amount
            to.balance += amount
        }
    }
}

// Deadlock:
// Thread 1: transfer(accountA, accountB, 100) - locks A, waits for B
// Thread 2: transfer(accountB, accountA, 50)  - locks B, waits for A
// Circular wait!

// ✅ Solution: Lock ordering
fun transferSafe(from: Account, to: Account, amount: Int) {
    val first = if (from.id < to.id) from else to
    val second = if (from.id < to.id) to else from

    synchronized(first) {   // Always lock in same order
        synchronized(second) {
            from.balance -= amount
            to.balance += amount
        }
    }
}
```

**Preventing Deadlocks:**

1. **Lock ordering** - always lock in same order
2. **Lock timeout** - use `tryLock(timeout)`
3. **Deadlock detection** - monitoring and recovery
4. **Avoid nested locks** - minimize nested locking
5. **Use higher-level primitives** - channels, actors instead of low-level locks

**5. Thread-Safe Data Structures:**

*Theory:* Thread-safe data structures use internal synchronization. Examples: `ConcurrentHashMap`, `CopyOnWriteArrayList`, `BlockingQueue`. Trade-off: safety vs performance.

```kotlin
// ✅ Thread-safe collections
val map = ConcurrentHashMap<String, Int>()
map.put("key", 1)  // Thread-safe

val queue = LinkedBlockingQueue<String>()
queue.put("item")  // Blocking operation, thread-safe

// ✅ Atomic variables
val counter = AtomicInteger(0)
counter.incrementAndGet()  // Atomic operation

val reference = AtomicReference<User>(null)
reference.compareAndSet(null, newUser)  // CAS operation
```

**6. Key Concepts:**

**Visibility:**
*Theory:* Changes by one thread may not be visible to others due to CPU cache. `volatile` guarantees visibility (but not atomicity).

```kotlin
// ❌ Without volatile - may hang
class Task {
    private var running = true

    fun run() {
        while (running) {  // May be cached in CPU cache
            // work
        }
    }

    fun stop() {
        running = false  // May not be visible to other thread
    }
}

// ✅ With volatile
class SafeTask {
    @Volatile
    private var running = true  // Guarantees visibility

    fun run() {
        while (running) {
            // work
        }
    }

    fun stop() {
        running = false  // Immediately visible to all threads
    }
}
```

**Happens-Before:**
*Theory:* Happens-before relationship - guarantee that operation A is visible to operation B. Established through: volatile, synchronized, thread start/join, lock acquire/release.

**Key Rules:**

1. **Minimize shared state** - less shared data = fewer problems
2. **Immutability** - immutable objects thread-safe by definition
3. **Use high-level primitives** - coroutines, actors instead of low-level threads
4. **Avoid premature optimization** - correctness first, performance later
5. **Test thoroughly** - concurrency bugs hard to reproduce

---

## Follow-ups

- What is the difference between volatile and synchronized?
- How do you implement lock-free data structures?
- What are compare-and-swap (CAS) operations?

## Related Questions

### Prerequisites (Easier)
- [[q-clean-code-principles--software-engineering--medium]] - Clean code principles
- Basic threading concepts


### Advanced (Harder)
- Advanced concurrency patterns
- Lock-free algorithms
