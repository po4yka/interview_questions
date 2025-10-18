---
id: 20251012-600003
title: "Concurrency Fundamentals / Основы параллелизма"
topic: concurrency
difficulty: hard
status: draft
created: 2025-10-12
tags:
  - concurrency
  - multithreading
  - synchronization
  - race-conditions
  - mutexes
  - semaphores
moc: moc-concurrency
related: [q-coroutinescope-vs-supervisorscope--programming-languages--medium, q-decorator-pattern--design-patterns--medium, q-synchronized-blocks-with-coroutines--programming-languages--medium]
  - q-os-fundamentals-concepts--computer-science--hard
  - q-kotlin-coroutines-advanced--kotlin--hard
  - q-clean-code-principles--software-engineering--medium
subtopics:
  - concurrency
  - multithreading
  - synchronization
  - race-conditions
  - locks
---
# Concurrency Fundamentals

## English Version

### Problem Statement

Concurrency is the ability to execute multiple tasks simultaneously. Understanding concurrency is crucial for building responsive, high-performance applications. Key concepts include race conditions, synchronization primitives, deadlocks, and thread-safe data structures.

**The Question:** What is concurrency vs parallelism? What are race conditions and how to prevent them? What are mutexes, semaphores, and monitors? How do you avoid deadlocks?

### Detailed Answer

---

### CONCURRENCY VS PARALLELISM

```
Concurrency:
- Multiple tasks making progress (not necessarily simultaneously)
- About dealing with multiple things at once
- Can be achieved with single CPU core (time-slicing)

Example: Single chef cooking multiple dishes
- Starts pasta water
- While waiting, chops vegetables
- While pasta cooks, prepares sauce
- One person, multiple tasks in progress

Parallelism:
- Multiple tasks executing simultaneously
- About doing multiple things at once
- Requires multiple CPU cores

Example: Multiple chefs cooking
- Chef 1 cooks pasta
- Chef 2 prepares salad
- Chef 3 makes dessert
- Multiple people working simultaneously
```

**Visualization:**
```
Concurrency (Single Core):
Time →
Task A: 
Task B: 
       Context switching between tasks

Parallelism (Multi Core):
Time →
Core 1 Task A: 
Core 2 Task B: 
       True simultaneous execution
```

**Kotlin Example:**
```kotlin
// Concurrency: Coroutines (can run on single thread)
suspend fun fetchUserConcurrently() {
    val user = async { fetchUser() }      // Suspend, not block
    val posts = async { fetchPosts() }    // Can interleave

    // Concurrently fetched, but may use same thread
    println("${user.await()} has ${posts.await().size} posts")
}

// Parallelism: Multiple threads
fun fetchUserInParallel() {
    val executor = Executors.newFixedThreadPool(2)  // 2 threads

    val userFuture = executor.submit { fetchUser() }    // Thread 1
    val postsFuture = executor.submit { fetchPosts() }  // Thread 2

    // Truly parallel on multi-core CPU
    println("${userFuture.get()} has ${postsFuture.get().size} posts")
}
```

---

### RACE CONDITIONS

**Race Condition = Multiple threads access shared data, at least one modifies it, outcome depends on timing**

```kotlin
//  Race condition example
class Counter {
    private var count = 0

    fun increment() {
        count++  // Not atomic! Actually 3 operations:
                 // 1. Read count
                 // 2. Add 1
                 // 3. Write count
    }

    fun getCount() = count
}

// Problem:
fun main() {
    val counter = Counter()

    // Start 1000 threads
    val threads = List(1000) {
        Thread {
            repeat(1000) {
                counter.increment()
            }
        }
    }

    threads.forEach { it.start() }
    threads.forEach { it.join() }

    println(counter.getCount())  // Expected: 1,000,000
                                  // Actual: ~950,000 (varies!)
}
```

**Why it happens:**
```
Time:    Thread 1              Thread 2
t1:      Read count (0)
t2:                            Read count (0)
t3:      Add 1 → 1
t4:                            Add 1 → 1
t5:      Write 1
t6:                            Write 1
Result: count = 1 (should be 2!)
Two increments, but count only increased by 1
```

---

### SYNCHRONIZATION PRIMITIVES

**1. Mutex (Mutual Exclusion Lock)**

```kotlin
//  Fixed with synchronized
class SafeCounter {
    private var count = 0
    private val lock = Any()

    fun increment() {
        synchronized(lock) {
            count++  // Only one thread at a time
        }
    }

    fun getCount() = synchronized(lock) { count }
}

// Or use ReentrantLock
class SafeCounterWithLock {
    private var count = 0
    private val lock = ReentrantLock()

    fun increment() {
        lock.lock()
        try {
            count++
        } finally {
            lock.unlock()  // Always unlock in finally
        }
    }

    fun getCount(): Int {
        lock.lock()
        try {
            return count
        } finally {
            lock.unlock()
        }
    }
}

// Modern Kotlin: Atomic variables
class AtomicCounter {
    private val count = AtomicInteger(0)

    fun increment() {
        count.incrementAndGet()  // Atomic operation
    }

    fun getCount() = count.get()
}
```

**Mutex Properties:**
```
 Only one thread can hold lock at a time
 Thread that locks must unlock (ownership)
 Reentrant: Same thread can lock multiple times
 Can cause deadlock
 Performance overhead
```

---

**2. Semaphore**

```kotlin
// Semaphore: Allows N threads to access resource

// Binary Semaphore (like mutex)
class BinarySemaphoreExample {
    private val semaphore = Semaphore(1)  // Only 1 permit

    fun criticalSection() {
        semaphore.acquire()  // Get permit
        try {
            // Only one thread here
            println("${Thread.currentThread().name} in critical section")
            Thread.sleep(1000)
        } finally {
            semaphore.release()  // Return permit
        }
    }
}

// Counting Semaphore (connection pool)
class ConnectionPool {
    private val connections = mutableListOf<Connection>()
    private val semaphore = Semaphore(5)  // Max 5 connections

    init {
        repeat(5) {
            connections.add(Connection("conn-$it"))
        }
    }

    fun executeQuery(query: String): String {
        semaphore.acquire()  // Wait for available connection
        val connection = synchronized(connections) {
            connections.removeAt(0)
        }

        try {
            return connection.execute(query)
        } finally {
            synchronized(connections) {
                connections.add(connection)
            }
            semaphore.release()  // Release permit
        }
    }
}

// Usage: Only 5 threads can use connections simultaneously
fun main() {
    val pool = ConnectionPool()

    repeat(10) { i ->
        Thread {
            println("Thread $i waiting for connection...")
            val result = pool.executeQuery("SELECT * FROM users")
            println("Thread $i got result: $result")
        }.start()
    }
}
```

**Semaphore Properties:**
```
 Controls access to N resources
 Any thread can release (no ownership)
 Useful for resource pools
 Can implement producer-consumer
 More complex than mutex
```

---

**3. Monitor (synchronized in Java/Kotlin)**

```kotlin
// Monitor: Mutex + Condition Variables

class BoundedBuffer<T>(private val capacity: Int) {
    private val buffer = LinkedList<T>()
    private val lock = ReentrantLock()
    private val notFull = lock.newCondition()
    private val notEmpty = lock.newCondition()

    fun put(item: T) {
        lock.lock()
        try {
            // Wait while buffer is full
            while (buffer.size == capacity) {
                notFull.await()
            }

            buffer.add(item)
            println("Produced: $item, size: ${buffer.size}")

            // Signal that buffer is not empty
            notEmpty.signal()
        } finally {
            lock.unlock()
        }
    }

    fun take(): T {
        lock.lock()
        try {
            // Wait while buffer is empty
            while (buffer.isEmpty()) {
                notEmpty.await()
            }

            val item = buffer.removeFirst()
            println("Consumed: $item, size: ${buffer.size}")

            // Signal that buffer is not full
            notFull.signal()

            return item
        } finally {
            lock.unlock()
        }
    }
}

// Producer-Consumer pattern
fun main() {
    val buffer = BoundedBuffer<Int>(5)

    // Producer thread
    Thread {
        repeat(10) {
            buffer.put(it)
            Thread.sleep(100)
        }
    }.start()

    // Consumer thread
    Thread {
        repeat(10) {
            val item = buffer.take()
            Thread.sleep(200)
        }
    }.start()
}
```

---

### ANDROID CONCURRENCY

**1. Main Thread (UI Thread)**

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        //  Bad: Network on main thread
        // This will crash with NetworkOnMainThreadException
        // val data = fetchFromNetwork()

        //  Bad: Blocking operation on main thread
        // Thread.sleep(5000)  // ANR (Application Not Responding)

        //  Good: Background thread
        Thread {
            val data = fetchFromNetwork()

            //  Bad: Update UI from background thread
            // textView.text = data  // Crash!

            //  Good: Post to main thread
            runOnUiThread {
                textView.text = data
            }
        }.start()

        //  Better: AsyncTask (deprecated)
        //  Best: Coroutines
        lifecycleScope.launch {
            val data = withContext(Dispatchers.IO) {
                fetchFromNetwork()  // Background thread
            }
            textView.text = data  // Main thread automatically
        }
    }
}
```

**2. Thread Safety in Android**

```kotlin
//  Bad: Shared mutable state
class UserRepository {
    private var cachedUser: User? = null  // Not thread-safe!

    fun getUser(): User? {
        if (cachedUser == null) {
            cachedUser = fetchFromDatabase()
        }
        return cachedUser
    }
}

//  Good: Synchronized access
class SafeUserRepository {
    @Volatile
    private var cachedUser: User? = null

    @Synchronized
    fun getUser(): User? {
        if (cachedUser == null) {
            cachedUser = fetchFromDatabase()
        }
        return cachedUser
    }
}

//  Better: Double-checked locking
class OptimizedUserRepository {
    @Volatile
    private var cachedUser: User? = null
    private val lock = Any()

    fun getUser(): User? {
        // First check (no lock)
        cachedUser?.let { return it }

        // Second check (with lock)
        synchronized(lock) {
            cachedUser?.let { return it }
            cachedUser = fetchFromDatabase()
            return cachedUser
        }
    }
}

//  Best: Immutable + Flow
class ModernUserRepository {
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    suspend fun loadUser() {
        val user = withContext(Dispatchers.IO) {
            fetchFromDatabase()
        }
        _user.value = user  // Thread-safe emission
    }
}
```

---

### DEADLOCK

**Deadlock = Circular wait where threads block each other**

```kotlin
//  Deadlock example
val lock1 = ReentrantLock()
val lock2 = ReentrantLock()

// Thread 1
thread {
    lock1.lock()
    println("Thread 1: Acquired lock1")
    Thread.sleep(100)  // Simulate work

    println("Thread 1: Waiting for lock2...")
    lock2.lock()  //  Waits forever
    println("Thread 1: Acquired lock2")

    lock2.unlock()
    lock1.unlock()
}

// Thread 2
thread {
    lock2.lock()
    println("Thread 2: Acquired lock2")
    Thread.sleep(100)  // Simulate work

    println("Thread 2: Waiting for lock1...")
    lock1.lock()  //  Waits forever
    println("Thread 2: Acquired lock1")

    lock1.unlock()
    lock2.unlock()
}

// Deadlock:
// Thread 1: Holds lock1, waits for lock2
// Thread 2: Holds lock2, waits for lock1
```

**Deadlock Prevention:**

```kotlin
//  Solution 1: Lock ordering
// Always acquire locks in same order

thread {
    lock1.lock()
    lock2.lock()
    // Work
    lock2.unlock()
    lock1.unlock()
}

thread {
    lock1.lock()  // Same order
    lock2.lock()
    // Work
    lock2.unlock()
    lock1.unlock()
}

//  Solution 2: tryLock with timeout
thread {
    lock1.lock()
    try {
        if (lock2.tryLock(1, TimeUnit.SECONDS)) {
            try {
                // Work
            } finally {
                lock2.unlock()
            }
        } else {
            println("Could not acquire lock2, backing off")
        }
    } finally {
        lock1.unlock()
    }
}

//  Solution 3: Single lock for related operations
val singleLock = ReentrantLock()

thread {
    singleLock.lock()
    try {
        // Access both resources
    } finally {
        singleLock.unlock()
    }
}

//  Solution 4: Avoid nested locks
// Redesign to not need multiple locks
```

---

### THREAD-SAFE DATA STRUCTURES

**1. ConcurrentHashMap**

```kotlin
//  Not thread-safe
val map = HashMap<String, Int>()

// Multiple threads
thread { map["key1"] = 1 }
thread { map["key2"] = 2 }  // May corrupt map

//  Thread-safe
val concurrentMap = ConcurrentHashMap<String, Int>()

thread { concurrentMap["key1"] = 1 }
thread { concurrentMap["key2"] = 2 }  // Safe

//  Atomic operations
concurrentMap.compute("counter") { _, oldValue ->
    (oldValue ?: 0) + 1
}

concurrentMap.computeIfAbsent("user:123") {
    fetchUserFromDatabase(it)
}
```

**2. CopyOnWriteArrayList**

```kotlin
//  Thread-safe list for read-heavy workloads
val listeners = CopyOnWriteArrayList<Listener>()

// Safe to iterate while other threads modify
thread {
    for (listener in listeners) {  // Safe iteration
        listener.onEvent()
    }
}

thread {
    listeners.add(newListener)  // Safe modification
}

// Trade-off:
//  Fast reads (no locking)
//  Slow writes (creates copy)
// Use when reads >> writes
```

**3. BlockingQueue**

```kotlin
//  Thread-safe producer-consumer queue
val queue = LinkedBlockingQueue<Task>(capacity = 10)

// Producer thread
thread {
    repeat(20) {
        val task = Task(it)
        queue.put(task)  // Blocks if queue full
        println("Produced: $task")
    }
}

// Consumer threads
repeat(3) { workerId ->
    thread {
        while (true) {
            val task = queue.take()  // Blocks if queue empty
            println("Worker $workerId consumed: $task")
            task.execute()
        }
    }
}
```

---

### VOLATILE KEYWORD

```kotlin
// Problem: CPU caching
class TaskRunner {
    private var flag = false  //  May be cached per-thread

    fun runTask() {
        thread {
            while (!flag) {  // May never see flag change!
                // Wait
            }
            println("Task finished")
        }

        Thread.sleep(1000)
        flag = true  // May not be visible to other thread
    }
}

// Solution: @Volatile
class SafeTaskRunner {
    @Volatile
    private var flag = false  //  Always reads from main memory

    fun runTask() {
        thread {
            while (!flag) {  // Sees flag change immediately
                // Wait
            }
            println("Task finished")
        }

        Thread.sleep(1000)
        flag = true  // Write is immediately visible
    }
}
```

**@Volatile guarantees:**
```
 Reads always get latest value from main memory
 Writes immediately visible to all threads
 No instruction reordering around volatile access
 Does NOT guarantee atomicity of compound operations

//  Not atomic (still race condition)
@Volatile var counter = 0
counter++  // Read + increment + write (not atomic!)

//  Use AtomicInteger instead
val counter = AtomicInteger(0)
counter.incrementAndGet()  // Atomic
```

---

### HAPPENS-BEFORE RELATIONSHIP

```kotlin
// Happens-before: Guarantees visibility and ordering

// 1. Program Order Rule
var x = 0
var y = 0

fun thread1() {
    x = 1  // Happens-before
    y = 2  // This line
}
// y = 2 sees x = 1

// 2. Monitor Lock Rule
val lock = Any()
var shared = 0

fun thread1() {
    synchronized(lock) {
        shared = 1  // Happens-before unlock
    }
}

fun thread2() {
    synchronized(lock) {  // Lock happens-after unlock in thread1
        println(shared)    // Sees shared = 1
    }
}

// 3. Volatile Variable Rule
@Volatile var flag = false
var data = 0

fun writer() {
    data = 42   // Happens-before
    flag = true // Volatile write
}

fun reader() {
    if (flag) {      // Volatile read
        println(data) // Sees data = 42 (happens-after)
    }
}

// 4. Thread Start Rule
var x = 0

fun main() {
    x = 1  // Happens-before thread start

    val t = Thread {
        println(x)  // Sees x = 1
    }
    t.start()
}

// 5. Thread Join Rule
var x = 0

fun main() {
    val t = Thread {
        x = 1  // Happens-before thread termination
    }
    t.start()
    t.join()  // Join happens-after thread termination

    println(x)  // Sees x = 1
}
```

---

### ANDROID THREAD POOLS

```kotlin
//  Use thread pools instead of creating threads

// Don't do this:
repeat(1000) {
    Thread {
        doWork()
    }.start()  // Creates 1000 threads! 
}

// Do this:
val executor = Executors.newFixedThreadPool(4)  // 4 worker threads

repeat(1000) {
    executor.execute {
        doWork()  // Reuses threads
    }
}

executor.shutdown()

// Common executors:
val singleThread = Executors.newSingleThreadExecutor()
val fixedPool = Executors.newFixedThreadPool(4)
val cachedPool = Executors.newCachedThreadPool()
val scheduled = Executors.newScheduledThreadPool(2)

// Android specific:
val mainExecutor = ContextCompat.getMainExecutor(context)
val ioExecutor = Executors.newFixedThreadPool(
    Runtime.getRuntime().availableProcessors()
)

// Modern approach: Coroutines with Dispatchers
lifecycleScope.launch(Dispatchers.IO) {
    val data = fetchData()
    withContext(Dispatchers.Main) {
        updateUI(data)
    }
}
```

---

### COMMON CONCURRENCY PATTERNS

**1. Producer-Consumer**

```kotlin
val queue = LinkedBlockingQueue<Int>(10)

// Producer
thread {
    repeat(20) {
        queue.put(it)
        println("Produced: $it")
        Thread.sleep(50)
    }
}

// Consumers
repeat(3) { id ->
    thread {
        while (true) {
            val item = queue.take()
            println("Consumer $id consumed: $item")
            Thread.sleep(100)
        }
    }
}
```

**2. Reader-Writer Lock**

```kotlin
val rwLock = ReentrantReadWriteLock()
var data = 0

// Multiple readers (concurrent)
fun read(): Int {
    rwLock.readLock().lock()
    try {
        return data
    } finally {
        rwLock.readLock().unlock()
    }
}

// Single writer (exclusive)
fun write(value: Int) {
    rwLock.writeLock().lock()
    try {
        data = value
    } finally {
        rwLock.writeLock().unlock()
    }
}

// Many readers can read simultaneously
// Writer gets exclusive access
```

**3. Future/Promise Pattern**

```kotlin
// CompletableFuture
fun fetchDataAsync(): CompletableFuture<String> {
    return CompletableFuture.supplyAsync {
        Thread.sleep(1000)
        "Data"
    }
}

// Usage
val future = fetchDataAsync()
future.thenApply { data ->
    data.uppercase()
}.thenAccept { result ->
    println(result)
}

// Kotlin Coroutines (better)
suspend fun fetchData(): String {
    delay(1000)
    return "Data"
}

// Usage
lifecycleScope.launch {
    val data = fetchData()
    println(data.uppercase())
}
```

---

### KEY TAKEAWAYS

1. **Concurrency** ≠ **Parallelism** (multiple tasks vs multiple cores)
2. **Race condition** = unsynchronized shared mutable state
3. **Mutex** = mutual exclusion lock (one thread at a time)
4. **Semaphore** = counting lock (N threads at a time)
5. **Monitor** = mutex + condition variables
6. **Deadlock** = circular wait, prevent with lock ordering
7. **@Volatile** = visibility guarantee, not atomicity
8. **Atomic classes** for lock-free thread safety
9. **Thread pools** better than creating many threads
10. **Happens-before** guarantees visibility and ordering

---

## Russian Version

### Постановка задачи

Параллелизм - это способность выполнять несколько задач одновременно. Понимание параллелизма критично для создания отзывчивых, высокопроизводительных приложений. Ключевые концепции включают состояния гонки (race conditions), примитивы синхронизации, взаимные блокировки (deadlocks) и потокобезопасные структуры данных.

**Вопрос:** Что такое concurrency vs parallelism? Что такое race conditions и как их предотвратить? Что такое mutexes, semaphores и monitors? Как избежать deadlocks?

### Детальный ответ

---

### CONCURRENCY VS PARALLELISM

```
Concurrency (Параллелизм):
- Несколько задач делают прогресс (не обязательно одновременно)
- О работе с несколькими вещами одновременно
- Может быть достигнуто с одним ядром CPU (разделение времени)

Пример: Один повар готовит несколько блюд
- Ставит воду для пасты
- Пока ждет, режет овощи
- Пока паста варится, готовит соус
- Один человек, несколько задач в процессе

Parallelism (Истинный параллелизм):
- Несколько задач выполняются одновременно
- О выполнении нескольких вещей одновременно
- Требует нескольких ядер CPU

Пример: Несколько поваров готовят
- Повар 1 готовит пасту
- Повар 2 готовит салат
- Повар 3 делает десерт
- Несколько людей работают одновременно
```

**Визуализация:**
```
Concurrency (Одно ядро):
Время →
Задача A: ████░░░░████░░░░████
Задача B: ░░░░████░░░░████░░░░
       Переключение контекста между задачами

Parallelism (Множество ядер):
Время →
Ядро 1 Задача A: ████████████████
Ядро 2 Задача B: ████████████████
       Истинное одновременное выполнение
```

---

### СОСТОЯНИЯ ГОНКИ (RACE CONDITIONS)

**Race Condition = Несколько потоков обращаются к разделяемым данным, как минимум один изменяет их, результат зависит от времени**

**Почему это происходит:**
```
Время:    Поток 1              Поток 2
t1:       Читает count (0)
t2:                            Читает count (0)
t3:       Добавляет 1 → 1
t4:                            Добавляет 1 → 1
t5:       Записывает 1
t6:                            Записывает 1
Результат: count = 1 (должно быть 2!)
Два инкремента, но count увеличился только на 1
```

---

### ПРИМИТИВЫ СИНХРОНИЗАЦИИ

**1. Mutex (Блокировка взаимного исключения)**

```kotlin
// ✓ Исправлено с synchronized
class SafeCounter {
    private var count = 0
    private val lock = Any()

    fun increment() {
        synchronized(lock) {
            count++  // Только один поток за раз
        }
    }

    fun getCount() = synchronized(lock) { count }
}

// Или используем ReentrantLock
class SafeCounterWithLock {
    private var count = 0
    private val lock = ReentrantLock()

    fun increment() {
        lock.lock()
        try {
            count++
        } finally {
            lock.unlock()  // Всегда разблокируем в finally
        }
    }
}

// Современный Kotlin: Атомарные переменные
class AtomicCounter {
    private val count = AtomicInteger(0)

    fun increment() {
        count.incrementAndGet()  // Атомарная операция
    }

    fun getCount() = count.get()
}
```

**Свойства Mutex:**
```
✓ Только один поток может удерживать блокировку одновременно
✓ Поток, который блокирует, должен разблокировать (владение)
✓ Реентерабельный: Тот же поток может блокировать несколько раз
✗ Может вызвать deadlock
✗ Накладные расходы на производительность
```

---

**2. Semaphore (Семафор)**

```kotlin
// Semaphore: Позволяет N потокам обращаться к ресурсу

// Бинарный семафор (как mutex)
class BinarySemaphoreExample {
    private val semaphore = Semaphore(1)  // Только 1 разрешение

    fun criticalSection() {
        semaphore.acquire()  // Получаем разрешение
        try {
            // Только один поток здесь
            println("${Thread.currentThread().name} в критической секции")
            Thread.sleep(1000)
        } finally {
            semaphore.release()  // Возвращаем разрешение
        }
    }
}

// Считающий семафор (пул соединений)
class ConnectionPool {
    private val connections = mutableListOf<Connection>()
    private val semaphore = Semaphore(5)  // Максимум 5 соединений

    fun executeQuery(query: String): String {
        semaphore.acquire()  // Ждем доступного соединения
        val connection = synchronized(connections) {
            connections.removeAt(0)
        }

        try {
            return connection.execute(query)
        } finally {
            synchronized(connections) {
                connections.add(connection)
            }
            semaphore.release()  // Освобождаем разрешение
        }
    }
}
```

**Свойства Semaphore:**
```
✓ Контролирует доступ к N ресурсам
✓ Любой поток может освободить (нет владения)
✓ Полезен для пулов ресурсов
✓ Может реализовать producer-consumer
✗ Более сложный чем mutex
```

---

**3. Monitor (synchronized в Java/Kotlin)**

```kotlin
// Monitor: Mutex + Условные переменные

class BoundedBuffer<T>(private val capacity: Int) {
    private val buffer = LinkedList<T>()
    private val lock = ReentrantLock()
    private val notFull = lock.newCondition()
    private val notEmpty = lock.newCondition()

    fun put(item: T) {
        lock.lock()
        try {
            // Ждем пока буфер не заполнен
            while (buffer.size == capacity) {
                notFull.await()
            }

            buffer.add(item)
            println("Произведено: $item, размер: ${buffer.size}")

            // Сигнализируем что буфер не пуст
            notEmpty.signal()
        } finally {
            lock.unlock()
        }
    }

    fun take(): T {
        lock.lock()
        try {
            // Ждем пока буфер не пустой
            while (buffer.isEmpty()) {
                notEmpty.await()
            }

            val item = buffer.removeFirst()
            println("Потреблено: $item, размер: ${buffer.size}")

            // Сигнализируем что буфер не заполнен
            notFull.signal()

            return item
        } finally {
            lock.unlock()
        }
    }
}
```

---

### ПОТОКОБЕЗОПАСНЫЕ СТРУКТУРЫ ДАННЫХ

**1. ConcurrentHashMap**

```kotlin
// ✗ Не потокобезопасно
val map = HashMap<String, Int>()

// Несколько потоков
thread { map["key1"] = 1 }
thread { map["key2"] = 2 }  // Может повредить map

// ✓ Потокобезопасно
val concurrentMap = ConcurrentHashMap<String, Int>()

thread { concurrentMap["key1"] = 1 }
thread { concurrentMap["key2"] = 2 }  // Безопасно

// ✓ Атомарные операции
concurrentMap.compute("counter") { _, oldValue ->
    (oldValue ?: 0) + 1
}
```

**2. CopyOnWriteArrayList**

```kotlin
// ✓ Потокобезопасный список для чтения-интенсивных нагрузок
val listeners = CopyOnWriteArrayList<Listener>()

// Безопасная итерация пока другие потоки модифицируют
thread {
    for (listener in listeners) {  // Безопасная итерация
        listener.onEvent()
    }
}

thread {
    listeners.add(newListener)  // Безопасная модификация
}

// Компромисс:
// ✓ Быстрые чтения (без блокировок)
// ✗ Медленные записи (создает копию)
// Использовать когда чтений >> записей
```

**3. BlockingQueue**

```kotlin
// ✓ Потокобезопасная очередь producer-consumer
val queue = LinkedBlockingQueue<Task>(capacity = 10)

// Поток-производитель
thread {
    repeat(20) {
        val task = Task(it)
        queue.put(task)  // Блокируется если очередь заполнена
        println("Произведено: $task")
    }
}

// Потоки-потребители
repeat(3) { workerId ->
    thread {
        while (true) {
            val task = queue.take()  // Блокируется если очередь пуста
            println("Работник $workerId потребил: $task")
            task.execute()
        }
    }
}
```

---

### VOLATILE КЛЮЧЕВОЕ СЛОВО

```kotlin
// Проблема: Кэширование CPU
class TaskRunner {
    private var flag = false  // ✗ Может быть закэширован для каждого потока

    fun runTask() {
        thread {
            while (!flag) {  // Может никогда не увидеть изменение flag!
                // Ждем
            }
            println("Задача завершена")
        }

        Thread.sleep(1000)
        flag = true  // Может быть не видно другому потоку
    }
}

// Решение: @Volatile
class SafeTaskRunner {
    @Volatile
    private var flag = false  // ✓ Всегда читает из основной памяти

    fun runTask() {
        thread {
            while (!flag) {  // Видит изменение flag немедленно
                // Ждем
            }
            println("Задача завершена")
        }

        Thread.sleep(1000)
        flag = true  // Запись немедленно видна
    }
}
```

**@Volatile гарантирует:**
```
✓ Чтения всегда получают последнее значение из основной памяти
✓ Записи немедленно видны всем потокам
✓ Нет переупорядочивания инструкций вокруг volatile доступа
✗ НЕ гарантирует атомарность составных операций

// ✗ Не атомарно (все еще race condition)
@Volatile var counter = 0
counter++  // Чтение + инкремент + запись (не атомарно!)

// ✓ Используйте AtomicInteger вместо этого
val counter = AtomicInteger(0)
counter.incrementAndGet()  // Атомарно
```

---

### HAPPENS-BEFORE ОТНОШЕНИЕ

```kotlin
// Happens-before: Гарантирует видимость и порядок

// 1. Правило порядка программы
var x = 0
var y = 0

fun thread1() {
    x = 1  // Happens-before
    y = 2  // Эта строка
}
// y = 2 видит x = 1

// 2. Правило блокировки монитора
val lock = Any()
var shared = 0

fun thread1() {
    synchronized(lock) {
        shared = 1  // Happens-before разблокировка
    }
}

fun thread2() {
    synchronized(lock) {  // Блокировка happens-after разблокировка в thread1
        println(shared)    // Видит shared = 1
    }
}

// 3. Правило volatile переменной
@Volatile var flag = false
var data = 0

fun writer() {
    data = 42   // Happens-before
    flag = true // Volatile запись
}

fun reader() {
    if (flag) {      // Volatile чтение
        println(data) // Видит data = 42 (happens-after)
    }
}
```

---

### КЛЮЧЕВЫЕ ВЫВОДЫ

1. **Concurrency** ≠ **Parallelism** (множество задач vs множество ядер)
2. **Race condition** = несинхронизированное разделяемое изменяемое состояние
3. **Mutex** = блокировка взаимного исключения (один поток за раз)
4. **Semaphore** = счетная блокировка (N потоков за раз)
5. **Monitor** = mutex + условные переменные
6. **Deadlock** = циклическое ожидание, предотвращается упорядочением блокировок
7. **@Volatile** = гарантия видимости, не атомарности
8. **Atomic классы** для lock-free потокобезопасности
9. **Thread pools** лучше чем создание множества потоков
10. **Happens-before** гарантирует видимость и порядок

## Follow-ups

1. What is the difference between lock and synchronized?
2. How does compare-and-swap (CAS) work?
3. What is lock-free programming?
4. How do you handle thread interruption?
5. What is the Fork-Join framework?
6. What are memory barriers and fences?
7. How does the Java Memory Model work?
8. What is false sharing and how to avoid it?
9. What are wait-free algorithms?
10. How do coroutines compare to threads for concurrency?

---

## Related Questions

### Kotlin Language Features
- [[q-structured-concurrency-violations--kotlin--hard]] - Concurrency
- [[q-structured-concurrency--kotlin--hard]] - Concurrency
- [[q-channel-pipelines--kotlin--hard]] - Concurrency
- [[q-deferred-async-patterns--kotlin--medium]] - Concurrency
- [[q-produce-actor-builders--kotlin--medium]] - Concurrency
- [[q-actor-pattern--kotlin--hard]] - Concurrency
- [[q-testing-viewmodel-coroutines--kotlin--medium]] - Concurrency
