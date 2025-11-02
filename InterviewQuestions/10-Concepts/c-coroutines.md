---
id: "20251018-140003"
title: "Kotlin Coroutines / Корутины Kotlin"
aliases: ["Coroutines", "Kotlin Coroutines", "Корутины", "Сопрограммы"]
summary: "Lightweight concurrency framework for asynchronous programming with structured concurrency and suspend functions"
topic: "kotlin"
subtopics: ["async", "concurrency", "coroutines"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-kotlin"
related: []
created: "2025-10-18"
updated: "2025-10-18"
tags: ["async", "concept", "concurrency", "coroutines", "difficulty/medium", "kotlin", "structured-concurrency"]
date created: Saturday, October 18th 2025, 3:07:46 pm
date modified: Saturday, November 1st 2025, 5:43:38 pm
---

# Summary (EN)

**Kotlin Coroutines** are a lightweight concurrency framework that enables asynchronous, non-blocking programming through suspendable functions. Coroutines provide an elegant way to write concurrent code that is sequential in appearance but asynchronous in execution, making complex async operations simple and readable.

Key characteristics:
- Lightweight threads that can suspend without blocking
- Structured concurrency for lifecycle management
- Sequential-looking code for async operations
- Built-in cancellation and exception handling
- Thread-efficient execution

# Краткое Описание (RU)

**Корутины Kotlin** — это легковесная система параллелизма, которая позволяет писать асинхронный, неблокирующий код с помощью приостанавливаемых функций. Корутины предоставляют элегантный способ написания параллельного кода, который выглядит последовательным, но выполняется асинхронно, делая сложные асинхронные операции простыми и читаемыми.

Ключевые характеристики:
- Легковесные потоки, которые могут приостанавливаться без блокировки
- Структурированная конкурентность для управления жизненным циклом
- Последовательный на вид код для асинхронных операций
- Встроенная поддержка отмены и обработки исключений
- Эффективное использование потоков

---

## What Are Coroutines

### Definition

A **coroutine** is an instance of **suspendable computation**. It is conceptually similar to a thread, in that it takes a block of code to run that works concurrently with the rest of the code. However, a coroutine is not bound to any particular thread. It may suspend its execution in one thread and resume in another one.

### Core Principles

**1. Lightweight Threads**
- Coroutines are much cheaper than threads
- Can run thousands/millions of coroutines on a single thread
- No OS-level context switching overhead

**2. Non-blocking Suspension**
- Coroutines can pause (suspend) without blocking the thread
- Suspended coroutines free up the thread for other work
- Resume execution when ready

**3. Structured Concurrency**
- Coroutines are launched within a scope
- Parent-child relationship ensures proper lifecycle management
- Automatic cancellation and cleanup

### Coroutines Vs Threads

| Feature | Coroutine | Thread |
|---------|-----------|--------|
| **Resource Cost** | Very cheap (lightweight) | Expensive (heavyweight) |
| **Blocking** | Non-blocking (suspends) | Blocking |
| **Management** | Managed by Kotlin runtime | Managed by Operating System |
| **Creation** | Fast | Slow |
| **Context Switching** | Fast (in-process) | Slow (OS-level) |
| **Lifecycle** | Tied to scope | Independent |
| **Cancellation** | Built-in, hierarchical | Manual |

**Example:**
```kotlin
// Threads: expensive, limited
repeat(100_000) {
    thread {
        Thread.sleep(1000)
        print(".")
    }
}
// OutOfMemoryError!

// Coroutines: lightweight, scalable
runBlocking {
    repeat(100_000) {
        launch {
            delay(1000)
            print(".")
        }
    }
}
// Works fine!
```

---

## Core Components

### 1. Suspend Functions

Functions marked with `suspend` keyword that can pause execution:

```kotlin
suspend fun fetchData(): String {
    delay(1000)  // Suspends without blocking
    return "Data loaded"
}
```

**Characteristics:**
- Can only be called from coroutines or other suspend functions
- Enable sequential-looking async code
- Under the hood: use continuations (state machines)

**Example:**
```kotlin
suspend fun loadUserData(userId: String): UserData {
    val profile = fetchProfile(userId)      // Suspends
    val settings = fetchSettings(userId)    // Suspends after profile
    return UserData(profile, settings)
}
```

### 2. Coroutine Builders

Functions that launch new coroutines:

**launch**: Fire-and-forget coroutine
```kotlin
val job: Job = scope.launch {
    // Do async work
    println("Task completed")
}
job.cancel()  // Can cancel
```

**async**: Coroutine that returns a result
```kotlin
val deferred: Deferred<String> = scope.async {
    fetchData()  // Returns Deferred
}
val result = deferred.await()  // Get result
```

**runBlocking**: Blocks current thread until completion
```kotlin
fun main() = runBlocking {
    launch { doWork() }
    // Blocks until all child coroutines complete
}
```

**Comparison:**

| Builder | Returns | Blocks Thread | Use Case |
|---------|---------|---------------|----------|
| `launch` | Job | No | Fire and forget |
| `async` | Deferred<T> | No | Need result |
| `runBlocking` | T | Yes | main(), tests, bridging |

### 3. CoroutineScope

Defines lifecycle and context for coroutines:

```kotlin
// Create custom scope
val scope = CoroutineScope(Dispatchers.Default + Job())

scope.launch {
    // Coroutine tied to this scope
}

// Cancel all coroutines in scope
scope.cancel()
```

**Android-specific scopes:**
```kotlin
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            // Canceled when ViewModel is cleared
        }
    }
}

class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Canceled when lifecycle is destroyed
        }
    }
}
```

### 4. CoroutineContext

Configuration for coroutine execution:

```kotlin
val context = Dispatchers.IO + Job() + CoroutineName("MyCoroutine")

scope.launch(context) {
    // Runs with this context
}
```

**Elements:**
- **Dispatcher**: Which thread(s) to use
- **Job**: Lifecycle and cancellation
- **CoroutineName**: Debug name
- **CoroutineExceptionHandler**: Error handling

---

## Dispatchers

Control which thread(s) execute coroutines:

### Dispatchers.Main
- Android/UI main thread
- Use for UI updates

```kotlin
launch(Dispatchers.Main) {
    updateUI(data)  // Safe to update UI
}
```

### Dispatchers.IO
- Optimized for I/O operations
- File operations, network calls, database

```kotlin
launch(Dispatchers.IO) {
    val data = readFile()
    val response = apiCall()
}
```

### Dispatchers.Default
- CPU-intensive work
- Parsing, sorting, computation

```kotlin
launch(Dispatchers.Default) {
    val result = complexCalculation()
}
```

### Dispatchers.Unconfined
- Not confined to specific thread
- Advanced use cases only

**Switching Dispatchers:**
```kotlin
suspend fun loadData(): Data {
    val result = withContext(Dispatchers.IO) {
        // Run on IO thread
        fetchFromNetwork()
    }
    // Back to original dispatcher
    return result
}
```

**Comparison:**

| Dispatcher | Thread Pool | Use Case |
|------------|-------------|----------|
| Main | UI thread | UI updates, Android main |
| IO | Shared pool (64 threads) | Network, file, database |
| Default | CPU cores count | Computation, parsing |
| Unconfined | Any | Advanced patterns |

---

## Structured Concurrency

The principle that ties coroutine lifetimes to scopes, ensuring predictable cancellation and resource cleanup.

### Core Principles

**1. Scope Hierarchy**
```kotlin
viewModelScope.launch {                  // Parent
    val user = async { fetchUser() }     // Child 1
    val posts = async { fetchPosts() }   // Child 2

    // If viewModelScope cancels:
    // - Parent cancels
    // - All children cancel automatically
    // - No orphans remain
}
```

**2. Automatic Cancellation**
```kotlin
lifecycleScope.launch {
    launch { task1() }
    launch { task2() }

    // When lifecycle destroys:
    // - lifecycleScope cancels
    // - All child coroutines cancel
    // - No memory leaks
}
```

**3. Exception Propagation**
```kotlin
scope.launch {
    try {
        val result1 = async { riskyOp1() }
        val result2 = async { riskyOp2() }

        // If either fails:
        // - Exception propagates to parent
        // - Sibling cancels
        // - Parent can handle error
    } catch (e: Exception) {
        handleError(e)
    }
}
```

### Benefits

- **Memory leak prevention**: Auto-cancel when scope ends
- **Predictable cancellation**: Cancel parent → all children cancel
- **Exception handling**: Predictable propagation through hierarchy
- **Resource management**: Automatic cleanup

### Anti-pattern Vs Best Practice

**WRONG: Unstructured (GlobalScope)**
```kotlin
GlobalScope.launch {
    // Runs forever unless manually canceled
    // Memory leak risk!
}
```

**CORRECT: Structured (lifecycleScope)**
```kotlin
lifecycleScope.launch {
    // Tied to component lifecycle
    // Auto-cancels when lifecycle destroys
}
```

---

## Common Patterns

### 1. Sequential Execution
```kotlin
suspend fun loadUserProfile(userId: String): Profile {
    val user = fetchUser(userId)           // Wait for user
    val settings = fetchSettings(userId)   // Then get settings
    return Profile(user, settings)
}
```

### 2. Parallel Execution
```kotlin
suspend fun loadUserProfileParallel(userId: String): Profile = coroutineScope {
    val userDeferred = async { fetchUser(userId) }
    val settingsDeferred = async { fetchSettings(userId) }

    // Both fetch in parallel
    Profile(userDeferred.await(), settingsDeferred.await())
}
```

### 3. Cancellation with Timeout
```kotlin
suspend fun fetchWithTimeout(): String? {
    return withTimeoutOrNull(5000) {
        fetchData()  // Cancels if takes > 5 seconds
    }
}
```

### 4. Resource Cleanup
```kotlin
suspend fun processFile(path: String) {
    val file = openFile(path)
    try {
        file.process()
    } finally {
        file.close()  // Always runs, even if canceled
    }
}
```

### 5. Retry Logic
```kotlin
suspend fun <T> retry(
    times: Int,
    block: suspend () -> T
): T {
    repeat(times - 1) {
        try {
            return block()
        } catch (e: Exception) {
            // Continue to next attempt
        }
    }
    return block()  // Last attempt
}

// Usage
val data = retry(3) { fetchData() }
```

---

## Advantages Over Threads

### 1. Lightweight
- Threads: ~1MB stack size, limited by OS
- Coroutines: Bytes of memory, millions possible

### 2. Non-blocking
```kotlin
// Thread: blocks thread for 1 second
Thread.sleep(1000)

// Coroutine: suspends, thread free for other work
delay(1000)
```

### 3. Structured Lifecycle
- Threads: manual management, easy to leak
- Coroutines: auto-cancel with scope

### 4. Sequential-looking Code
```kotlin
// With threads: callback hell
thread {
    val user = fetchUser()
    thread {
        val posts = fetchPosts(user)
        thread {
            display(user, posts)
        }
    }
}

// With coroutines: sequential
launch {
    val user = fetchUser()
    val posts = fetchPosts(user)
    display(user, posts)
}
```

### 5. Built-in Cancellation
- Threads: no standard cancellation mechanism
- Coroutines: cooperative cancellation built-in

---

## Use Cases

### Mobile Development (Android)
- Network requests without blocking UI
- Database operations
- Image loading/processing
- Lifecycle-aware background work

```kotlin
class UserViewModel : ViewModel() {
    fun loadUser() {
        viewModelScope.launch {
            val user = repository.fetchUser()
            _userData.value = user
        }
    }
}
```

### Backend Development
- Handling concurrent requests
- Non-blocking I/O operations
- Parallel data processing
- Database queries

```kotlin
suspend fun handleRequest(id: String): Response {
    val data = database.query(id)  // Non-blocking
    return Response(data)
}
```

### Data Processing
- Parallel computations
- Pipeline processing
- Fan-out/fan-in patterns

```kotlin
suspend fun processBatch(items: List<Item>) = coroutineScope {
    items.map { item ->
        async { processItem(item) }
    }.awaitAll()
}
```

---

## Code Examples

### Example 1: Basic Coroutine
```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    println("Main program starts: ${Thread.currentThread().name}")

    launch {
        println("Coroutine starts: ${Thread.currentThread().name}")
        delay(1000)
        println("Coroutine finishes: ${Thread.currentThread().name}")
    }

    println("Main program continues: ${Thread.currentThread().name}")
    delay(2000)
    println("Main program ends: ${Thread.currentThread().name}")
}

// Output:
// Main program starts: main
// Main program continues: main
// Coroutine starts: main
// Coroutine finishes: main
// Main program ends: main
```

### Example 2: Parallel Network Calls
```kotlin
suspend fun loadDashboard(): Dashboard = coroutineScope {
    // All fetch in parallel
    val userDeferred = async { fetchUser() }
    val postsDeferred = async { fetchPosts() }
    val notificationsDeferred = async { fetchNotifications() }

    Dashboard(
        user = userDeferred.await(),
        posts = postsDeferred.await(),
        notifications = notificationsDeferred.await()
    )
}
```

### Example 3: Android ViewModel
```kotlin
class ArticlesViewModel : ViewModel() {
    private val _articles = MutableStateFlow<List<Article>>(emptyList())
    val articles: StateFlow<List<Article>> = _articles.asStateFlow()

    fun loadArticles() {
        viewModelScope.launch {
            try {
                val result = repository.fetchArticles()
                _articles.value = result
            } catch (e: Exception) {
                // Handle error
            }
        }
    }
}
```

### Example 4: Flow Processing
```kotlin
suspend fun processUserEvents() {
    userEventFlow
        .debounce(300)
        .map { event -> processEvent(event) }
        .collect { result ->
            updateUI(result)
        }
}
```

---

## Common Mistakes

### 1. Using GlobalScope
```kotlin
// WRONG: leaks memory, ignores lifecycle
GlobalScope.launch { doWork() }

// CORRECT: use appropriate scope
viewModelScope.launch { doWork() }
```

### 2. Blocking in Coroutines
```kotlin
// WRONG: blocks thread
launch {
    Thread.sleep(1000)  // Blocks!
}

// CORRECT: suspend instead
launch {
    delay(1000)  // Suspends without blocking
}
```

### 3. Not Handling Cancellation
```kotlin
// WRONG: doesn't check cancellation
launch {
    while (true) {
        // Infinite loop, won't cancel!
    }
}

// CORRECT: cooperative cancellation
launch {
    while (isActive) {
        // Checks cancellation
    }
}
```

### 4. Swallowing Exceptions
```kotlin
// WRONG: exception disappears
launch {
    try {
        riskyOperation()
    } catch (e: Exception) {
        // Silent failure
    }
}

// CORRECT: handle or propagate
launch {
    try {
        riskyOperation()
    } catch (e: Exception) {
        log(e)
        throw e  // Propagate to handler
    }
}
```

---

## Trade-offs

### Advantages
- Lightweight and scalable
- Sequential-looking async code
- Built-in lifecycle management
- Excellent performance
- Great IDE support

### Disadvantages
- Learning curve for beginners
- Debugging can be challenging
- Must understand suspend functions
- Requires dependency on kotlinx.coroutines
- Android: min API 21 (or desugaring)

### When to Use
- Asynchronous operations (network, I/O)
- Concurrent processing
- Lifecycle-aware background work
- Replacing callbacks/RxJava

### When NOT to Use
- Simple, purely synchronous code
- When legacy callback APIs are sufficient
- Performance-critical tight loops (use threads directly)

---

## References

### Official Documentation
- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [Coroutines Overview](https://kotlinlang.org/docs/coroutines-overview.html)
- [Android Coroutines](https://developer.android.com/kotlin/coroutines)

### Articles
- [Structured Concurrency](https://kotlinlang.org/docs/coroutines-basics.html#structured-concurrency)
- [Coroutines Best Practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)

### Videos
- [KotlinConf - Introduction to Coroutines](https://www.youtube.com/watch?v=_hfBv0a09Jc)

---

## Related Questions

### Prerequisites (Easy)
- [[q-what-is-coroutine--kotlin--easy]] - What is a coroutine? Basic concepts
- [[q-coroutine-scope-basics--kotlin--easy]] - CoroutineScope fundamentals
- [[q-suspend-functions-basics--kotlin--easy]] - Understanding suspend functions
- [[q-coroutine-builders-basics--kotlin--easy]] - Coroutine builders: launch, async, runBlocking
- [[q-launch-vs-async--kotlin--easy]] - Difference between launch and async
- [[q-coroutine-delay-vs-thread-sleep--kotlin--easy]] - delay() vs Thread.sleep()
- [[q-coroutines-threads-android-differences--kotlin--easy]] - Coroutines vs Threads on Android
- [[q-globalscope-antipattern--kotlin--easy]] - Why avoid GlobalScope

### Core Concepts (Medium)
- [[q-structured-concurrency-kotlin--kotlin--medium]] - Structured concurrency explained
- [[q-coroutine-context-explained--kotlin--medium]] - CoroutineContext explained
- [[q-coroutine-dispatchers--kotlin--medium]] - Coroutine dispatchers overview
- [[q-coroutinescope-vs-coroutinecontext--kotlin--medium]] - Scope vs Context
- [[q-launch-vs-async-vs-runblocking--kotlin--medium]] - Detailed builder comparison
- [[q-dispatchers-io-vs-default--kotlin--medium]] - When to use IO vs Default
- [[q-withcontext-use-cases--kotlin--medium]] - Using withContext
- [[q-coroutine-cancellation-mechanisms--kotlin--medium]] - Cancellation mechanisms
- [[q-coroutine-exception-handling--kotlin--medium]] - Exception handling in coroutines
- [[q-suspend-functions-deep-dive--kotlin--medium]] - Deep dive into suspend functions
- [[q-coroutine-parent-child-relationship--kotlin--medium]] - Parent-child relationship
- [[q-coroutine-job-lifecycle--kotlin--medium]] - Job lifecycle states

### Advanced Scopes & Lifecycle (Medium)
- [[q-lifecycle-scopes-viewmodelscope-lifecyclescope--kotlin--medium]] - Android lifecycle scopes
- [[q-lifecyclescope-viewmodelscope--kotlin--medium]] - lifecycleScope vs viewModelScope
- [[q-viewmodel-coroutines-lifecycle--kotlin--medium]] - ViewModel coroutines lifecycle
- [[q-coroutinescope-vs-supervisorscope--kotlin--medium]] - CoroutineScope vs SupervisorScope
- [[q-supervisor-scope-vs-coroutine-scope--kotlin--medium]] - Supervisor scope details
- [[q-job-vs-supervisorjob--kotlin--medium]] - Job vs SupervisorJob
- [[q-coroutine-supervisorjob-use-cases--kotlin--medium]] - When to use SupervisorJob

### Testing (Medium)
- [[q-testing-viewmodels-coroutines--kotlin--medium]] - Testing ViewModels with coroutines
- [[q-testing-viewmodel-coroutines--kotlin--medium]] - ViewModel coroutines testing
- [[q-testing-coroutine-timing-control--kotlin--medium]] - Controlling time in tests
- [[q-test-dispatcher-types--kotlin--medium]] - Test dispatcher types
- [[q-testing-coroutine-cancellation--kotlin--medium]] - Testing cancellation
- [[q-coroutine-virtual-time--kotlin--medium]] - Virtual time in tests

### Debugging & Optimization (Medium/Hard)
- [[q-debugging-coroutines-techniques--kotlin--medium]] - Debugging techniques
- [[q-common-coroutine-mistakes--kotlin--medium]] - Common mistakes
- [[q-coroutine-profiling--kotlin--hard]] - Profiling coroutines
- [[q-coroutine-performance-optimization--kotlin--hard]] - Performance optimization
- [[q-coroutine-memory-leaks--kotlin--hard]] - Preventing memory leaks
- [[q-coroutine-memory-leak-detection--kotlin--hard]] - Detecting memory leaks

### Advanced Patterns (Hard)
- [[q-advanced-coroutine-patterns--kotlin--hard]] - Advanced patterns
- [[q-structured-concurrency--kotlin--hard]] - Deep dive into structured concurrency
- [[q-structured-concurrency-violations--kotlin--hard]] - Structured concurrency violations
- [[q-coroutine-context-detailed--kotlin--hard]] - CoroutineContext deep dive
- [[q-coroutinecontext-composition--kotlin--hard]] - Context composition
- [[q-coroutine-context-elements--kotlin--hard]] - Context elements
- [[q-continuation-cps-internals--kotlin--hard]] - Continuation internals
- [[q-suspend-cancellable-coroutine--kotlin--hard]] - suspendCancellableCoroutine

### Dispatchers & Threading (Medium/Hard)
- [[q-dispatchers-main-immediate--kotlin--medium]] - Dispatchers.Main.immediate
- [[q-dispatchers-unconfined--kotlin--medium]] - Unconfined dispatcher
- [[q-custom-dispatchers-limited-parallelism--kotlin--hard]] - Custom dispatchers
- [[q-dispatcher-performance--kotlin--hard]] - Dispatcher performance

### Flows (Medium/Hard)
- [[q-kotlin-flow-basics--kotlin--medium]] - Kotlin Flow basics
- [[q-flow-basics--kotlin--easy]] - Flow fundamentals
- [[q-flow-cold-flow-fundamentals--kotlin--easy]] - Cold Flow fundamentals
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold Flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Cold vs Hot Flows comparison
- [[q-sharedflow-stateflow--kotlin--medium]] - SharedFlow and StateFlow
- [[q-stateflow-sharedflow-differences--kotlin--medium]] - StateFlow vs SharedFlow
- [[q-sharedflow-stateflow-android--kotlin--medium]] - StateFlow/SharedFlow in Android
- [[q-flow-operators-map-filter--kotlin--medium]] - Flow operators
- [[q-flow-operators--kotlin--medium]] - Flow operators overview
- [[q-flow-combining-zip-combine--kotlin--medium]] - Combining flows

### Channels (Medium/Hard)
- [[q-kotlin-channels--kotlin--medium]] - Kotlin Channels
- [[q-channels-basics-types--kotlin--medium]] - Channel basics and types
- [[q-channels-vs-flow--kotlin--medium]] - Channels vs Flow
- [[q-channel-flow-comparison--kotlin--medium]] - Channel/Flow comparison
- [[q-fan-in-fan-out--kotlin--hard]] - Fan-in/fan-out patterns
- [[q-fan-in-fan-out-channels--kotlin--hard]] - Fan-in/fan-out with channels

### Practical Patterns (Medium)
- [[q-parallel-network-calls-coroutines--kotlin--medium]] - Parallel network calls
- [[q-retry-exponential-backoff-flow--kotlin--medium]] - Retry with backoff
- [[q-debounce-search-coroutines--kotlin--medium]] - Debounce search
- [[q-coroutine-timeout-withtimeout--kotlin--medium]] - Timeout handling
- [[q-coroutine-resource-cleanup--kotlin--medium]] - Resource cleanup
- [[q-noncancellable-context-cleanup--kotlin--medium]] - Non-cancellable cleanup

### Integration (Medium)
- [[q-retrofit-coroutines-best-practices--kotlin--medium]] - Retrofit with coroutines
- [[q-room-coroutines-flow--kotlin--medium]] - Room with coroutines and Flow
- [[q-workmanager-coroutine-worker--kotlin--medium]] - WorkManager CoroutineWorker
- [[q-rxjava-to-coroutines-migration--kotlin--medium]] - RxJava to Coroutines migration

### Synchronization (Medium/Hard)
- [[q-mutex-synchronized-coroutines--kotlin--medium]] - Mutex vs synchronized
- [[q-atomic-vs-synchronized--kotlin--medium]] - Atomic vs synchronized
- [[q-race-conditions-coroutines--kotlin--hard]] - Race conditions
- [[q-semaphore-rate-limiting--kotlin--medium]] - Semaphore for rate limiting
