---
id: cs-003
title: Concurrency Fundamentals / Основы параллелизма
aliases:
- Concurrency Fundamentals
- Основы параллелизма
topic: cs
subtopics:
- concurrency
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-cs
related:
- q-abstract-class-purpose--cs--medium
created: 2025-10-12
updated: 2025-11-11
tags:
- concurrency
- difficulty/hard
sources:
- https://en.wikipedia.org/wiki/Concurrency_(computer_science)
anki_cards:
- slug: cs-003-0-en
  language: en
  anki_id: 1768454343139
  synced_at: '2026-01-15T09:41:02.833879'
- slug: cs-003-0-ru
  language: ru
  anki_id: 1768454343165
  synced_at: '2026-01-15T09:41:02.836993'
---
# Вопрос (RU)
> Что такое concurrency vs parallelism? Что такое race conditions и как их предотвратить? Что такое mutexes, semaphores и monitors? Как избежать deadlocks?

# Question (EN)
> What is concurrency vs parallelism? What are race conditions and how to prevent them? What are mutexes, semaphores, and monitors? How do you avoid deadlocks?

## Ответ (RU)

**Concurrency / Параллелизм:**
Concurrency — способность системы выполнять несколько задач с прогрессом (не обязательно одновременно). Parallelism — истинное одновременное выполнение на нескольких ядрах/процессорах. Критические концепции: race conditions, примитивы синхронизации, deadlocks, thread-safe структуры данных.

**1. Concurrency vs Parallelism:**

*Теория:*
- **Concurrency** — множество задач делают прогресс (не обязательно одновременно). Это про работу с несколькими вещами сразу (interleaving), а не обязательно про одновременное исполнение. Может достигаться даже на одном ядре через time-slicing (переключение контекста).
- **Parallelism** — множество задач выполняются физически одновременно. Это про выполнение нескольких вещей одновременно. Обычно требует нескольких ядер CPU или нескольких машин.

*Аналогия:*
- **Concurrency**: Один повар готовит несколько блюд (ставит пасту, пока она варится — режет овощи, пока овощи готовятся — делает соус).
- **Parallelism**: Несколько поваров готовят одновременно (повар 1 — паста, повар 2 — салат, повар 3 — десерт).

```kotlin
// ✅ Concurrency: coroutines могут давать конкурентное выполнение (interleaving)
// даже на одном потоке; реальный параллелизм зависит от диспетчера.

suspend fun fetchDataConcurrently(scope: CoroutineScope) {
    val user = scope.async { fetchUser() }      // suspend, не блокирует поток
    val posts = scope.async { fetchPosts() }    // могут чередоваться
    // Concurrent; при использовании одного потока задачи выполняются вперемешку
    println("${user.await()} has ${posts.await().size} posts")
}

// ✅ Parallelism: множество потоков
fun fetchDataInParallel() {
    val executor = Executors.newFixedThreadPool(2)  // 2 потока
    try {
        val userFuture = executor.submit(Callable { fetchUser() })    // Поток 1
        val postsFuture = executor.submit(Callable { fetchPosts() })  // Поток 2
        // Истинный параллелизм на multi-core CPU (если доступен)
        println("${userFuture.get()} has ${postsFuture.get().size} posts")
    } finally {
        executor.shutdown()
    }
}
```

**2. Race Conditions:**

*Теория:* Race condition — ситуация, когда несколько потоков обращаются к shared data, хотя бы один модифицирует её, и результат зависит от порядка/тайминга операций. Возникает из-за неатомарных операций (например, `count++` = read + add + write).

```kotlin
// ❌ Race condition
class Counter {
    private var count = 0

    fun increment() {
        count++  // НЕ атомарно: read + add + write
    }
}

// Пример: 1000 потоков × 1000 инкрементов = ожидаем 1_000_000
// Реально: меньше, результат недетерминирован.

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

*Теория:* Mutex — примитив синхронизации, позволяющий только одному потоку владеть блокировкой одновременно. Другие потоки блокируются до unlock. Используется для защиты critical section. (Частный случай — бинарный семафор, но с более строгой моделью владения.)

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
            return if (balance >= amount) {
                balance -= amount
                true
            } else {
                false
            }
        } finally {
            lock.unlock()
        }
    }
}
```

**Semaphore:**

*Теория:* Semaphore — счётчик, ограничивающий количество потоков, которые могут получить доступ к ресурсу одновременно. Часто говорят "mutex = semaphore с count=1" как интуитивное сравнение, но в реальных API модели владения различаются.

```kotlin
// ✅ Semaphore для ограничения количества одновременно используемых соединений
class ConnectionPool(maxConnections: Int, private val factory: () -> Connection) {
    private val semaphore = Semaphore(maxConnections)
    private val connections = ArrayDeque<Connection>().apply {
        repeat(maxConnections) { add(factory()) }
    }
    private val lock = ReentrantLock()

    fun acquireConnection(): Connection {
        semaphore.acquire()              // Блокируется, если нет доступных слотов
        lock.lock()
        try {
            return connections.removeFirst()
        } finally {
            lock.unlock()
        }
    }

    fun releaseConnection(conn: Connection) {
        lock.lock()
        try {
            connections.addLast(conn)
        } finally {
            lock.unlock()
        }
        semaphore.release()              // Освобождает слот
    }
}
```

**Monitor (synchronized):**

*Теория:* Monitor — высокоуровневый примитив, комбинирующий mutual exclusion + condition variables. В Java/Kotlin на JVM — это `synchronized` и связанный с ним монитор объекта + методы `wait/notify/notifyAll`, которые должны вызываться на том же мониторе.

```kotlin
// ✅ Monitor pattern: Producer-Consumer с использованием монитора this
class BlockingQueue<T>(private val capacity: Int) {
    private val queue = LinkedList<T>()

    fun put(item: T) {
        synchronized(this) {
            while (queue.size >= capacity) {
                (this as java.lang.Object).wait()  // ждём, пока не освободится место
            }
            queue.add(item)
            (this as java.lang.Object).notifyAll() // уведомляем consumers
        }
    }

    fun take(): T {
        synchronized(this) {
            while (queue.isEmpty()) {
                (this as java.lang.Object).wait()  // ждём, пока не появится элемент
            }
            val item = queue.removeFirst()
            (this as java.lang.Object).notifyAll() // уведомляем producers
            return item
        }
    }
}
```

**4. Deadlocks:**

*Теория:* Deadlock — ситуация, когда два или более потока навсегда ждут освобождения ресурсов друг другом. Часто анализируют через 4 условия Coffman: mutual exclusion, hold and wait, no preemption, circular wait.

```kotlin
// ❌ Потенциальный deadlock-пример
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

// Возможный deadlock:
// Thread 1: transfer(accountA, accountB, 100) - держит A, ждёт B
// Thread 2: transfer(accountB, accountA, 50)  - держит B, ждёт A
// Циклическое ожидание -> возможный взаимный блок (недетерминированно).

// ✅ Решение: фиксированный порядок захвата блокировок
fun transferSafe(from: Account, to: Account, amount: Int) {
    val (first, second) = if (from.id < to.id) from to to else to to from

    synchronized(first) {             // Всегда блокируем в одном порядке
        synchronized(second) {
            from.balance -= amount
            to.balance += amount
        }
    }
}
```

**Предотвращение Deadlocks:**

1. **Lock ordering** — всегда блокировать ресурсы в консистентном порядке.
2. **Lock timeout** — использовать `tryLock(timeout)` / неблокирующие попытки.
3. **Deadlock detection** — мониторинг зависимостей и recovery.
4. **Avoid nested locks** — минимизировать вложенные блокировки.
5. **Use higher-level primitives** — channels, actors вместо низкоуровневых locks.

**5. `Thread`-Safe Data Structures:**

*Теория:* `Thread`-safe структуры данных используют внутреннюю синхронизацию или lock-free алгоритмы. Примеры: `ConcurrentHashMap`, `CopyOnWriteArrayList`, `BlockingQueue`. Компромисс: безопасность vs производительность.

```kotlin
// ✅ Thread-safe collections (Java/JVM)
val map = ConcurrentHashMap<String, Int>()
map["key"] = 1  // Thread-safe операции (с учётом контрактов коллекции)

val queue = LinkedBlockingQueue<String>()
queue.put("item")  // Блокирующая, thread-safe

// ✅ Atomic variables
val counter = AtomicInteger(0)
counter.incrementAndGet()  // Атомарная операция

val reference = AtomicReference<User?>(null)
reference.compareAndSet(null, newUser)  // CAS-операция
```

**6. Ключевые концепции:**

**Visibility:**
*Теория:* Изменения одного потока могут быть не видны другим из-за кэширования и reorderings. В модели памяти Java (и Kotlin/JVM) `volatile` гарантирует видимость (happens-before для записи/чтения), но не делает составные операции атомарными.

```kotlin
// ❌ Без volatile - цикл может не увидеть обновление
class Task {
    private var running = true

    fun run() {
        while (running) {
            // work
        }
    }

    fun stop() {
        running = false
    }
}

// ✅ С volatile
class SafeTask {
    @Volatile
    private var running = true

    fun run() {
        while (running) {
            // work
        }
    }

    fun stop() {
        running = false  // Гарантирована видимость другим потокам
    }
}
```

**Happens-Before:**
*Теория:* Happens-before — отношение, гарантирующее, что эффекты операции A видимы операции B. На JVM устанавливается, например, через: volatile write->read, вход/выход из synchronized блока, lock acquire/release, `Thread.start()`, `Thread.join()` и др.

**Ключевые правила:**

1. **Minimize shared state** — меньше shared data = меньше проблем.
2. **Immutability** — immutable-объекты thread-safe по определению (при корректной публикации).
3. **Use high-level primitives** — coroutines, actors, thread pools вместо ручного управления потоками и raw locks, где это возможно.
4. **Avoid premature optimization** — сначала корректность, потом производительность.
5. **Test thoroughly** — concurrency-bugs сложно воспроизвести, нужны стресс-тесты.

## Answer (EN)

**Concurrency / Parallelism:**
Concurrency is the ability of a system to make progress on multiple tasks (not necessarily simultaneously). Parallelism is true simultaneous execution on multiple cores/processors. Critical concepts: race conditions, synchronization primitives, deadlocks, thread-safe data structures.

**1. Concurrency vs Parallelism:**

*Theory:*
- **Concurrency**: multiple tasks make progress (not necessarily at the same instant). It's about dealing with many things at once via interleaving; can be achieved even on a single core via time-slicing (context switching).
- **Parallelism**: multiple tasks execute physically at the same time. It's about doing many things at once; typically requires multiple CPU cores or machines.

*Analogy:*
- **Concurrency**: One chef cooking multiple dishes (starts pasta; while it cooks, chops vegetables; while vegetables cook, makes sauce).
- **Parallelism**: Multiple chefs cooking simultaneously (chef 1 - pasta, chef 2 - salad, chef 3 - dessert).

```kotlin
// ✅ Concurrency: coroutines provide concurrent (interleaved) execution
// even on a single thread; actual parallelism depends on dispatcher/threads.

suspend fun fetchDataConcurrently(scope: CoroutineScope) {
    val user = scope.async { fetchUser() }      // suspend, non-blocking
    val posts = scope.async { fetchPosts() }    // can interleave
    // Concurrent; if using a single-threaded dispatcher, work is interleaved
    println("${user.await()} has ${posts.await().size} posts")
}

// ✅ Parallelism: multiple threads
fun fetchDataInParallel() {
    val executor = Executors.newFixedThreadPool(2)  // 2 threads
    try {
        val userFuture = executor.submit(Callable { fetchUser() })    // Thread 1
        val postsFuture = executor.submit(Callable { fetchPosts() })  // Thread 2
        // True parallelism on multi-core CPU (if available)
        println("${userFuture.get()} has ${postsFuture.get().size} posts")
    } finally {
        executor.shutdown()
    }
}
```

**2. Race Conditions:**

*Theory:* Race condition is a situation where multiple threads access shared data, at least one modifies it, and the result depends on timing/order of operations. It occurs due to non-atomic compound operations (e.g., `count++` = read + add + write).

```kotlin
// ❌ Race condition
class Counter {
    private var count = 0

    fun increment() {
        count++  // NOT atomic: read + add + write
    }
}

// Example: 1000 threads × 1000 increments = expect 1_000_000
// In practice: less; result is nondeterministic.

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

*Theory:* Mutex is a synchronization primitive that allows only one thread to own the lock at a time. Other threads block until it is unlocked. Used to protect critical sections. (Often compared to a binary semaphore; real APIs differ in ownership semantics.)

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
            return if (balance >= amount) {
                balance -= amount
                true
            } else {
                false
            }
        } finally {
            lock.unlock()
        }
    }
}
```

**Semaphore:**

*Theory:* Semaphore is a counter that limits how many threads can access a resource simultaneously. People often say "mutex = semaphore with count=1" informally, but typical implementations have different usage/ownership semantics.

```kotlin
// ✅ Semaphore for limiting concurrent connections
class ConnectionPool(maxConnections: Int, private val factory: () -> Connection) {
    private val semaphore = Semaphore(maxConnections)
    private val connections = ArrayDeque<Connection>().apply {
        repeat(maxConnections) { add(factory()) }
    }
    private val lock = ReentrantLock()

    fun acquireConnection(): Connection {
        semaphore.acquire()              // Blocks if no permits available
        lock.lock()
        try {
            return connections.removeFirst()
        } finally {
            lock.unlock()
        }
    }

    fun releaseConnection(conn: Connection) {
        lock.lock()
        try {
            connections.addLast(conn)
        } finally {
            lock.unlock()
        }
        semaphore.release()              // Releases permit
    }
}
```

**Monitor (synchronized):**

*Theory:* A monitor is a high-level construct combining mutual exclusion with condition variables. On Java/Kotlin (JVM), `synchronized` uses an intrinsic monitor per object; `wait/notify/notifyAll` must be called on the same monitor while holding its lock.

```kotlin
// ✅ Monitor pattern: Producer-Consumer using this as monitor
class BlockingQueue<T>(private val capacity: Int) {
    private val queue = LinkedList<T>()

    fun put(item: T) {
        synchronized(this) {
            while (queue.size >= capacity) {
                (this as java.lang.Object).wait()  // wait until space available
            }
            queue.add(item)
            (this as java.lang.Object).notifyAll() // notify consumers
        }
    }

    fun take(): T {
        synchronized(this) {
            while (queue.isEmpty()) {
                (this as java.lang.Object).wait()  // wait until item available
            }
            val item = queue.removeFirst()
            (this as java.lang.Object).notifyAll() // notify producers
            return item
        }
    }
}
```

**4. Deadlocks:**

*Theory:* Deadlock is a situation where two or more threads wait forever for resources held by each other. It can arise when the 4 Coffman conditions hold: mutual exclusion, hold and wait, no preemption, circular wait.

```kotlin
// ❌ Potential deadlock example
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

// Possible deadlock:
// Thread 1: transfer(accountA, accountB, 100) - holds A, waits for B
// Thread 2: transfer(accountB, accountA, 50)  - holds B, waits for A
// Circular wait -> potential deadlock (nondeterministic).

// ✅ Solution: consistent lock ordering
fun transferSafe(from: Account, to: Account, amount: Int) {
    val (first, second) = if (from.id < to.id) from to to else to to from

    synchronized(first) {             // Always lock in the same order
        synchronized(second) {
            from.balance -= amount
            to.balance += amount
        }
    }
}
```

**Preventing Deadlocks:**

1. **Lock ordering** - always acquire locks in a consistent global order.
2. **Lock timeout** - use `tryLock(timeout)` / non-blocking attempts.
3. **Deadlock detection** - monitor lock dependencies and recover.
4. **Avoid nested locks** - minimize nested locking.
5. **Use higher-level primitives** - channels, actors instead of low-level locks when possible.

**5. `Thread`-Safe Data Structures:**

*Theory:* `Thread`-safe data structures use internal synchronization or lock-free algorithms. Examples: `ConcurrentHashMap`, `CopyOnWriteArrayList`, `BlockingQueue`. Trade-off: safety vs performance.

```kotlin
// ✅ Thread-safe collections (Java/JVM)
val map = ConcurrentHashMap<String, Int>()
map["key"] = 1  // Thread-safe operations (per collection's contract)

val queue = LinkedBlockingQueue<String>()
queue.put("item")  // Blocking, thread-safe

// ✅ Atomic variables
val counter = AtomicInteger(0)
counter.incrementAndGet()  // Atomic operation

val reference = AtomicReference<User?>(null)
reference.compareAndSet(null, newUser)  // CAS operation
```

**6. Key Concepts:**

**Visibility:**
*Theory:* Changes by one thread may not be visible to others due to caching and reordering. On the Java Memory Model (also used by Kotlin/JVM), `volatile` guarantees visibility and establishes happens-before between write and subsequent read, but does not make compound operations atomic.

```kotlin
// ❌ Without volatile - loop may never observe update
class Task {
    private var running = true

    fun run() {
        while (running) {
            // work
        }
    }

    fun stop() {
        running = false
    }
}

// ✅ With volatile
class SafeTask {
    @Volatile
    private var running = true

    fun run() {
        while (running) {
            // work
        }
    }

    fun stop() {
        running = false  // Guaranteed visible to other threads
    }
}
```

**Happens-Before:**
*Theory:* A happens-before relationship guarantees that effects of operation A are visible to operation B. On the JVM it's established via, e.g., volatile write->read, entering/exiting synchronized blocks, lock acquire/release, `Thread.start()`, `Thread.join()`, etc.

**Key Rules:**

1. **Minimize shared state** - less shared data -> fewer issues.
2. **Immutability** - immutable objects are thread-safe by definition (given correct publication).
3. **Use high-level primitives** - coroutines, actors, thread pools instead of raw threads/locks where possible.
4. **Avoid premature optimization** - correctness first, then performance.
5. **Test thoroughly** - concurrency bugs are hard to reproduce; use stress tests.

---

## Дополнительные Вопросы (RU)

- В чем разница между `volatile` и `synchronized`?
- Как реализуются lock-free структуры данных?
- Что такое операции compare-and-swap (CAS)?

## Follow-ups

- What is the difference between `volatile` and `synchronized`?
- How do you implement lock-free data structures?
- What are compare-and-swap (CAS) operations?

## Связанные Вопросы (RU)

### Базовые (проще)
- Базовые концепции потоков

### Продвинутые (сложнее)
- Продвинутые паттерны конкурентности
- Lock-free алгоритмы

## Related Questions

### Prerequisites (Easier)
- Basic threading concepts

### Advanced (Harder)
- Advanced concurrency patterns
- Lock-free algorithms

## References

- "https://en.wikipedia.org/wiki/Concurrency_(computer_science)"
