---
id: kotlin-069
title: "Debugging Kotlin coroutines: tools and techniques / Отладка Kotlin корутин: инструменты и техники"
topic: kotlin
difficulty: medium
status: draft
created: 2025-10-12
tags: [coroutines, debugging, difficulty/medium, kotlin, profiling, tools, troubleshooting]
moc: moc-kotlin
related: [q-common-coroutine-mistakes--kotlin--medium, q-coroutine-exception-handler--kotlin--medium, q-kotlin-any-unit-nothing--programming-languages--medium, q-kotlin-null-safety--kotlin--medium, q-produce-actor-builders--kotlin--medium, q-race-conditions-coroutines--kotlin--hard]
subtopics:
  - coroutines
  - debugging
  - profiling
  - troubleshooting
date created: Saturday, November 1st 2025, 12:10:44 pm
date modified: Saturday, November 1st 2025, 5:43:26 pm
---

# Question (EN)
> What tools and techniques are available for debugging Kotlin coroutines? How do you identify deadlocks, leaks, and performance issues?

# Вопрос (RU)
> Какие инструменты и техники доступны для отладки Kotlin корутин? Как идентифицировать deadlock, утечки и проблемы производительности?

---

## Answer (EN)

Debugging coroutines is challenging because traditional debugging tools are designed for threads, not suspending functions. Coroutines can suspend, resume on different threads, and have complex hierarchies. Understanding how to debug coroutines effectively is crucial for production readiness.



### 1. Enable Debug Mode

**First step:** Enable kotlinx.coroutines debug mode to add coroutine info to thread names.

```kotlin
// Add JVM argument:
-Dkotlinx.coroutines.debug

// Or programmatically (must be done before any coroutines run):
System.setProperty("kotlinx.coroutines.debug", "on")
```

**Effect:** Thread names include coroutine info:

```
// Without debug mode:
Thread: DefaultDispatcher-worker-1

// With debug mode:
Thread: DefaultDispatcher-worker-1 @coroutine#2
```

**Example:**

```kotlin
import kotlinx.coroutines.*

fun main() {
    System.setProperty("kotlinx.coroutines.debug", "on")

    runBlocking {
        launch {
            println("Running on: ${Thread.currentThread().name}")
        }
    }
}

// Output:
// Running on: main @coroutine#2
```

### 2. CoroutineName for Debugging

**Use CoroutineName** to identify coroutines in logs and debugger:

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    System.setProperty("kotlinx.coroutines.debug", "on")

    launch(CoroutineName("DataLoader")) {
        println("Loading data on: ${Thread.currentThread().name}")
        loadData()
    }

    launch(CoroutineName("ImageDownloader")) {
        println("Downloading images on: ${Thread.currentThread().name}")
        downloadImages()
    }
}

// Output:
// Loading data on: main @DataLoader#2
// Downloading images on: main @ImageDownloader#3
```

**Production usage:**

```kotlin
class UserRepository {
    suspend fun loadUser(userId: String): User {
        return withContext(Dispatchers.IO + CoroutineName("LoadUser-$userId")) {
            println("Loading user $userId on ${Thread.currentThread().name}")
            api.getUser(userId)
        }
    }
}

// Log output:
// Loading user 123 on: DefaultDispatcher-worker-2 @LoadUser-123#5
```

### 3. Reading Coroutine Stack Traces

**Problem:** Coroutine stack traces can be confusing because they show suspension points, not call stacks.

**Example:**

```kotlin
suspend fun functionA() {
    functionB()
}

suspend fun functionB() {
    functionC()
}

suspend fun functionC() {
    delay(100)
    throw RuntimeException("Error in C")
}

fun main() = runBlocking {
    functionA()
}

// Stack trace:
// Exception in thread "main" java.lang.RuntimeException: Error in C
//     at FileKt.functionC(File.kt:12)
//     at FileKt.functionB(File.kt:8)
//     at FileKt.functionA(File.kt:4)
//     at FileKt.main(File.kt:16)
```

**With debug mode + CoroutineName:**

```kotlin
fun main() = runBlocking(CoroutineName("MainCoroutine")) {
    launch(CoroutineName("Worker")) {
        functionA()
    }.join()
}

// Stack trace includes coroutine info:
// Exception in thread "main @Worker#2" java.lang.RuntimeException: Error in C
//     at FileKt.functionC(File.kt:12)
//     ...
```

### 4. IntelliJ IDEA Coroutine Debugger

**IntelliJ IDEA** has built-in coroutine debugging support (2021.2+).

**Features:**
- **Coroutines panel**: View all running coroutines
- **Coroutine call stack**: See full suspension path
- **Coroutine state**: Check if suspended, running, or cancelled
- **Step through suspending functions**: Debug like regular functions

**How to use:**

1. Set breakpoint in suspend function
2. Run in debug mode
3. Open **Coroutines** panel (View > Tool Windows > Debug > Coroutines)
4. See all coroutines, their state, and call stacks

**Example debugging session:**

```kotlin
suspend fun loadUser(userId: String): User {
    println("Start loading user")  // Breakpoint here
    val user = api.getUser(userId) // Breakpoint here
    println("User loaded")
    return user
}

// In Coroutines panel:
// - Coroutine #2 (LoadUser-123): SUSPENDED at api.getUser()
// - Coroutine #3 (DataProcessor): RUNNING
// - Coroutine #4 (ImageDownloader): CANCELLED
```

### 5. Coroutine Dump Analysis

**Dump all coroutines** to see what's running:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.debug.*

fun main() = runBlocking {
    repeat(5) { index ->
        launch(CoroutineName("Worker-$index")) {
            delay(1000)
        }
    }

    delay(100) // Let coroutines start

    // Dump all coroutines
    DebugProbes.dumpCoroutines()

    delay(2000)
}
```

**Enable DebugProbes:**

```kotlin
fun main() {
    DebugProbes.install()

    runBlocking {
        launch(CoroutineName("Worker")) {
            delay(1000)
        }

        delay(100)
        DebugProbes.dumpCoroutines().forEach { info ->
            println("Coroutine: ${info.name}")
            println("State: ${info.state}")
            println("Context: ${info.context}")
        }
    }

    DebugProbes.uninstall()
}
```

### 6. Finding Suspended Coroutines

**Problem:** Coroutine appears "stuck" - is it suspended or deadlocked?

**Technique: Periodic logging**

```kotlin
class MonitoredScope : CoroutineScope {
    private val job = SupervisorJob()
    override val coroutineContext = job + Dispatchers.Default

    private val activeCoroutines = ConcurrentHashMap<String, Long>()

    fun launchMonitored(name: String, block: suspend CoroutineScope.() -> Unit): Job {
        return launch(CoroutineName(name)) {
            activeCoroutines[name] = System.currentTimeMillis()
            try {
                block()
            } finally {
                activeCoroutines.remove(name)
            }
        }
    }

    fun printActiveCoroutines() {
        val now = System.currentTimeMillis()
        activeCoroutines.forEach { (name, startTime) ->
            val duration = now - startTime
            println("$name: running for ${duration}ms")
        }
    }
}

// Usage
val scope = MonitoredScope()

scope.launchMonitored("DataLoader") {
    loadData() // Takes long time
}

// Periodically check
repeat(10) {
    delay(1000)
    scope.printActiveCoroutines()
}
```

### 7. Detecting Deadlocks

**Scenario: Two coroutines waiting for each other**

```kotlin
val mutex1 = Mutex()
val mutex2 = Mutex()

// Coroutine 1
launch(CoroutineName("Coroutine-1")) {
    mutex1.withLock {
        println("C1: Acquired mutex1")
        delay(100)
        mutex2.withLock { // Waiting for C2 to release
            println("C1: Acquired mutex2")
        }
    }
}

// Coroutine 2
launch(CoroutineName("Coroutine-2")) {
    mutex2.withLock {
        println("C2: Acquired mutex2")
        delay(100)
        mutex1.withLock { // Waiting for C1 to release - DEADLOCK!
            println("C2: Acquired mutex1")
        }
    }
}
```

**Detection technique: Timeout**

```kotlin
suspend fun <T> withTimeout(name: String, timeoutMs: Long, block: suspend () -> T): T {
    return withTimeoutOrNull(timeoutMs) {
        block()
    } ?: throw TimeoutException("$name timed out after ${timeoutMs}ms")
}

// Usage
launch(CoroutineName("Coroutine-1")) {
    withTimeout("Mutex acquisition", 5000) {
        mutex1.withLock {
            mutex2.withLock {
                // Work
            }
        }
    }
}
```

### 8. Identifying Leaked Coroutines

**Coroutine leaks** occur when coroutines keep running after they should have been cancelled.

**Example leak:**

```kotlin
class LeakyViewModel : ViewModel() {
    //  BAD: Using GlobalScope
    fun loadData() {
        GlobalScope.launch {
            while (true) {
                fetchData()
                delay(1000)
            }
        }
    }
    // Coroutine continues even after ViewModel is cleared!
}
```

**Detection: Track active coroutines**

```kotlin
object CoroutineTracker {
    private val activeCoroutines = ConcurrentHashMap<String, Job>()

    fun trackCoroutine(name: String, job: Job) {
        activeCoroutines[name] = job
        job.invokeOnCompletion {
            activeCoroutines.remove(name)
        }
    }

    fun printActiveCoroutines() {
        println("Active coroutines: ${activeCoroutines.size}")
        activeCoroutines.forEach { (name, job) ->
            println("  - $name: ${if (job.isActive) "ACTIVE" else "COMPLETED"}")
        }
    }
}

// Usage
class TrackedViewModel : ViewModel() {
    fun loadData() {
        val job = viewModelScope.launch(CoroutineName("LoadData")) {
            // Work
        }
        CoroutineTracker.trackCoroutine("ViewModel-LoadData", job)
    }
}

// In tests or debug menu:
CoroutineTracker.printActiveCoroutines()
```

### 9. LeakCanary for Coroutine Leaks

**LeakCanary** can detect coroutine leaks:

```kotlin
// In build.gradle:
dependencies {
    debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.x'
}

// LeakCanary automatically detects leaked coroutines
class MyActivity : AppCompatActivity() {
    private val scope = CoroutineScope(Job() + Dispatchers.Main)

    override fun onDestroy() {
        super.onDestroy()
        // If you forget to cancel, LeakCanary will report it
        // scope.cancel() // ← Forgot to cancel!
    }
}
```

### 10. Logging Best Practices

**Pattern: Structured logging with coroutine context**

```kotlin
suspend fun logWithContext(message: String) {
    val context = coroutineContext
    val name = context[CoroutineName]?.name ?: "unnamed"
    val job = context[Job]
    val thread = Thread.currentThread().name

    println("[$name] [${job?.hashCode()}] [$thread] $message")
}

// Usage
suspend fun loadData() {
    logWithContext("Starting data load")
    val data = api.fetchData()
    logWithContext("Data loaded: ${data.size} items")
}

// Output:
// [DataLoader] [123456] [DefaultDispatcher-worker-1 @DataLoader#2] Starting data load
// [DataLoader] [123456] [DefaultDispatcher-worker-3 @DataLoader#2] Data loaded: 42 items
```

**Production logging wrapper:**

```kotlin
object CoroutineLogger {
    suspend fun d(tag: String, message: String) {
        val name = coroutineContext[CoroutineName]?.name ?: "unnamed"
        Log.d(tag, "[$name] $message")
    }

    suspend fun e(tag: String, message: String, throwable: Throwable? = null) {
        val name = coroutineContext[CoroutineName]?.name ?: "unnamed"
        Log.e(tag, "[$name] $message", throwable)
    }
}

// Usage
suspend fun loadUser(userId: String) {
    CoroutineLogger.d("UserRepo", "Loading user $userId")
    try {
        val user = api.getUser(userId)
        CoroutineLogger.d("UserRepo", "User loaded: ${user.name}")
    } catch (e: Exception) {
        CoroutineLogger.e("UserRepo", "Failed to load user", e)
    }
}
```

### 11. Android Studio Debugging Features

**Android Studio** provides specific coroutine debugging tools:

**Layout Inspector:**
- Shows coroutines attached to Views
- Detects leaked coroutines in UI components

**Profiler:**
- CPU Profiler shows coroutine traces
- Memory Profiler detects coroutine-related leaks

**Database Inspector:**
- View Room database queries triggered by coroutines
- See active queries and their coroutine context

### 12. Thread Dumps Interpretation

**Get thread dump:**

```bash
# On Android:
adb shell kill -3 <PID>
adb logcat -d > threaddump.txt

# On JVM:
jstack <PID> > threaddump.txt
```

**Interpreting coroutine info:**

```
"DefaultDispatcher-worker-1 @coroutine#2" #15 prio=5 os_prio=0 tid=0x00007f8 nid=0x1234 waiting on condition
   java.lang.Thread.State: TIMED_WAITING
        at java.lang.Thread.sleep(Native Method)
        at kotlinx.coroutines.DelayKt.delay(Delay.kt:140)
        at com.example.MyClass.suspendingFunction(MyClass.kt:25)
```

**Key info:**
- `@coroutine#2`: Coroutine ID
- `TIMED_WAITING`: Coroutine is suspended (delay)
- `MyClass.kt:25`: Suspension point

### 13. Common Debugging Scenarios

**Scenario 1: Coroutine never completes**

```kotlin
// Debugging steps:
// 1. Enable debug mode
// 2. Add CoroutineName
// 3. Add logging at key points
// 4. Use timeout to detect

suspend fun problematicFunction() = withContext(CoroutineName("ProblematicFunc")) {
    println("Starting")

    withTimeout(5000) { // Detect if stuck
        // Problem code
        mutex.withLock { // Is this waiting forever?
            println("Got lock")
            // ...
        }
    }

    println("Completed")
}
```

**Scenario 2: Exception swallowed**

```kotlin
// Problem: Exception not visible
launch {
    async {
        throw Exception("Hidden exception")
    }
    // Forgot to await() - exception lost!
}

// Solution: Add logging + exception handler
val handler = CoroutineExceptionHandler { _, exception ->
    println("Caught: $exception")
}

launch(handler) {
    val deferred = async {
        throw Exception("Now visible")
    }
    try {
        deferred.await()
    } catch (e: Exception) {
        println("Exception in async: $e")
    }
}
```

**Scenario 3: Race condition**

```kotlin
// Use logging to detect race conditions
var counter = 0
val mutex = Mutex()

suspend fun increment() {
    val before = counter
    println("[${Thread.currentThread().name}] Before: $before")

    delay(10) // Race condition window

    counter = before + 1
    println("[${Thread.currentThread().name}] After: $counter")
}

// Run with multiple coroutines to see race
repeat(10) {
    launch {
        increment()
    }
}

// Output shows race condition:
// [worker-1 @coroutine#2] Before: 0
// [worker-2 @coroutine#3] Before: 0  ← Both read 0!
// [worker-1 @coroutine#2] After: 1
// [worker-2 @coroutine#3] After: 1   ← Lost update!
```

### 14. Profiling Coroutine Performance

**Android Studio Profiler:**

1. Open CPU Profiler
2. Record coroutine execution
3. Look for:
   - Long-running coroutines
   - Excessive coroutine creation
   - Dispatcher contention

**Custom performance tracking:**

```kotlin
class CoroutineProfiler {
    private val metrics = ConcurrentHashMap<String, MutableList<Long>>()

    suspend fun <T> profile(name: String, block: suspend () -> T): T {
        val start = System.nanoTime()
        try {
            return block()
        } finally {
            val duration = System.nanoTime() - start
            metrics.getOrPut(name) { mutableListOf() }.add(duration)
        }
    }

    fun printStats() {
        metrics.forEach { (name, durations) ->
            val avg = durations.average() / 1_000_000 // Convert to ms
            val max = durations.maxOrNull()!! / 1_000_000
            val min = durations.minOrNull()!! / 1_000_000
            println("$name: avg=${avg}ms, min=${min}ms, max=${max}ms, count=${durations.size}")
        }
    }
}

// Usage
val profiler = CoroutineProfiler()

suspend fun loadData() {
    profiler.profile("LoadData") {
        api.fetchData()
    }
}

// Print stats periodically
profiler.printStats()
// Output:
// LoadData: avg=245ms, min=180ms, max=450ms, count=127
```

### 15. Testing Tools

**kotlinx-coroutines-test** provides debugging utilities:

```kotlin
@Test
fun debugTest() = runTest {
    val job = launch(CoroutineName("TestCoroutine")) {
        repeat(5) { i ->
            println("Iteration $i at ${currentTime}ms")
            delay(1000)
        }
    }

    advanceTimeBy(2500)
    println("Test time: ${currentTime}ms")

    job.cancelAndJoin()
}

// Output:
// Iteration 0 at 0ms
// Iteration 1 at 1000ms
// Iteration 2 at 2000ms
// Test time: 2500ms
```

### Best Practices

1.  **Always enable debug mode** in development
2.  **Name all coroutines** using CoroutineName
3.  **Add structured logging** at suspension points
4.  **Use timeouts** to detect stuck coroutines
5.  **Track active coroutines** in debug builds
6.  **Use IntelliJ IDEA's coroutine debugger**
7.  **Monitor with LeakCanary** in Android
8.  **Profile regularly** to catch performance issues
9.  **Write tests** with explicit timing
10.  **Document suspension points** in complex flows

### Key Takeaways

1. **Enable debug mode** - Adds coroutine info to thread names
2. **Use CoroutineName** - Makes debugging much easier
3. **IntelliJ IDEA has excellent tools** - Coroutines panel, step debugging
4. **Stack traces are different** - Show suspension points
5. **Detect deadlocks with timeouts** - Don't wait forever
6. **Track coroutines** - Prevent leaks
7. **LeakCanary helps** - Automatically detects coroutine leaks
8. **Structured logging** - Include coroutine context
9. **Profile performance** - Find bottlenecks
10. **Test with kotlinx-coroutines-test** - Control time and execution

---

## Ответ (RU)

Отладка корутин сложна, потому что традиционные инструменты отладки разработаны для потоков, а не для suspend функций. Корутины могут приостанавливаться, возобновляться на разных потоках и имеют сложные иерархии. Понимание эффективной отладки корутин критично для production готовности.



### 1. Включение Режима Отладки

**Первый шаг:** Включите режим отладки kotlinx.coroutines для добавления информации о корутинах в имена потоков.

```kotlin
// Добавьте JVM аргумент:
-Dkotlinx.coroutines.debug

// Или программно (должно быть сделано до запуска любых корутин):
System.setProperty("kotlinx.coroutines.debug", "on")
```

**Эффект:** Имена потоков включают информацию о корутинах:

```
// Без режима отладки:
Thread: DefaultDispatcher-worker-1

// С режимом отладки:
Thread: DefaultDispatcher-worker-1 @coroutine#2
```

### 2. CoroutineName Для Отладки

**Используйте CoroutineName** для идентификации корутин в логах и отладчике:

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    System.setProperty("kotlinx.coroutines.debug", "on")

    launch(CoroutineName("DataLoader")) {
        println("Загрузка данных на: ${Thread.currentThread().name}")
        loadData()
    }

    launch(CoroutineName("ImageDownloader")) {
        println("Загрузка изображений на: ${Thread.currentThread().name}")
        downloadImages()
    }
}

// Вывод:
// Загрузка данных на: main @DataLoader#2
// Загрузка изображений на: main @ImageDownloader#3
```

### Ключевые Выводы

1. **Включайте режим отладки** - Добавляет информацию о корутинах в имена потоков
2. **Используйте CoroutineName** - Значительно упрощает отладку
3. **IntelliJ IDEA имеет отличные инструменты** - Панель корутин, пошаговая отладка
4. **Стектрейсы отличаются** - Показывают точки приостановки
5. **Обнаруживайте deadlock таймаутами** - Не ждите вечно
6. **Отслеживайте корутины** - Предотвращайте утечки
7. **LeakCanary помогает** - Автоматически обнаруживает утечки корутин
8. **Структурированное логирование** - Включайте контекст корутины
9. **Профилируйте производительность** - Находите узкие места
10. **Тестируйте с kotlinx-coroutines-test** - Контролируйте время и выполнение

---

## Follow-ups

1. How do you debug coroutines that suspend across multiple threads?
2. What's the performance impact of enabling debug mode in production?
3. How can you implement custom DebugProbes for production monitoring?
4. What tools exist for visualizing coroutine execution flow?
5. How do you debug race conditions that only appear under high load?
6. Can you explain how to interpret coroutine state machine bytecode?
7. How do you set up continuous monitoring of coroutine health in production?

## References

- [Debugging Coroutines](https://kotlinlang.org/docs/debug-coroutines-with-idea.html)
- [kotlinx-coroutines-debug](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-debug/)
- [Android Studio Coroutine Debugging](https://developer.android.com/kotlin/coroutines/test)
- [LeakCanary](https://square.github.io/leakcanary/)

## Related Questions

- [[q-coroutine-exception-handler--kotlin--medium|CoroutineExceptionHandler usage]]
- [[q-common-coroutine-mistakes--kotlin--medium|Common coroutine mistakes]]
- [[q-race-conditions-coroutines--kotlin--hard|Race conditions in coroutines]]
