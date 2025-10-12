---
id: 20251012-160010
title: "Top 10 common Kotlin coroutines mistakes and anti-patterns / 10 частых ошибок с Kotlin корутинами"
slug: common-coroutine-mistakes-kotlin-medium
topic: kotlin
subtopics:
  - coroutines
  - mistakes
  - anti-patterns
  - best-practices
  - gotchas
status: draft
difficulty: medium
moc: moc-kotlin
date_created: 2025-10-12
date_updated: 2025-10-12
related_questions:
  - q-coroutine-exception-handler--kotlin--medium
  - q-debugging-coroutines-techniques--kotlin--medium
  - q-mutex-synchronized-coroutines--kotlin--medium
tags:
  - kotlin
  - coroutines
  - mistakes
  - anti-patterns
  - best-practices
  - gotchas
  - code-review
---

# Top 10 common Kotlin coroutines mistakes and anti-patterns

## English Version

### Problem Statement

Even experienced developers make common mistakes when working with Kotlin coroutines. These mistakes can lead to memory leaks, crashes, race conditions, or poor performance. Understanding and avoiding these anti-patterns is critical for production-ready code.

**The Question:** What are the most common mistakes when using Kotlin coroutines, and how do you fix them?

### Detailed Answer

#### Mistake 1: Using GlobalScope

**Problem:** `GlobalScope` coroutines are not tied to any lifecycle and can leak.

```kotlin
// ❌ WRONG: GlobalScope coroutine continues after Activity destroyed
class MyActivity : AppCompatActivity() {
    fun loadData() {
        GlobalScope.launch {
            val data = repository.fetchData()
            updateUI(data) // Crashes if Activity destroyed!
        }
    }
}
```

**Why wrong:**
- Coroutine continues even after Activity/ViewModel destroyed
- Can cause memory leaks
- Can crash when accessing destroyed views
- No structured concurrency

**✅ FIX: Use proper scope**

```kotlin
// ✅ CORRECT: Use lifecycleScope
class MyActivity : AppCompatActivity() {
    fun loadData() {
        lifecycleScope.launch {
            val data = repository.fetchData()
            updateUI(data) // Safe: cancelled when Activity destroyed
        }
    }
}

// ✅ CORRECT: Use viewModelScope
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            val data = repository.fetchData()
            _dataState.value = data // Safe: cancelled when ViewModel cleared
        }
    }
}

// ✅ CORRECT: Custom scope with lifecycle
class MyRepository {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    fun fetchData() {
        scope.launch {
            // Work
        }
    }

    fun cleanup() {
        scope.cancel() // Cancel all coroutines
    }
}
```

**Detection:** Search codebase for `GlobalScope`

```bash
# Find all GlobalScope usage
grep -r "GlobalScope" --include="*.kt"
```

#### Mistake 2: Not Handling Cancellation

**Problem:** Ignoring cancellation can waste resources and cause bugs.

```kotlin
// ❌ WRONG: Ignores cancellation
suspend fun processData() {
    while (true) { // Never checks cancellation!
        val data = fetchNextBatch()
        process(data)
    }
}
```

**Why wrong:**
- Coroutine continues running after cancelled
- Wastes CPU/memory/network
- Parent waits forever for child to finish

**✅ FIX: Check cancellation**

```kotlin
// ✅ CORRECT: Check isActive
suspend fun processData() = coroutineScope {
    while (isActive) { // Checks cancellation
        val data = fetchNextBatch()
        process(data)
    }
}

// ✅ CORRECT: Use ensureActive()
suspend fun processData() = coroutineScope {
    while (true) {
        ensureActive() // Throws CancellationException if cancelled
        val data = fetchNextBatch()
        process(data)
    }
}

// ✅ CORRECT: Use cancellable delay
suspend fun processData() {
    while (true) {
        delay(100) // Automatically checks cancellation
        val data = fetchNextBatch()
        process(data)
    }
}

// ✅ CORRECT: yield() for CPU-intensive work
suspend fun processData() {
    while (true) {
        yield() // Gives other coroutines a chance, checks cancellation
        cpuIntensiveWork()
    }
}
```

**Example: File processing**

```kotlin
// ❌ WRONG
suspend fun processLargeFile(file: File) {
    file.readLines().forEach { line ->
        // No cancellation check - processes entire file even if cancelled
        processLine(line)
    }
}

// ✅ CORRECT
suspend fun processLargeFile(file: File) {
    file.readLines().forEach { line ->
        ensureActive() // Check cancellation on each line
        processLine(line)
    }
}
```

#### Mistake 3: Using runBlocking in Production

**Problem:** `runBlocking` blocks thread, defeating coroutines' purpose.

```kotlin
// ❌ WRONG: Blocks main thread
fun loadUser() {
    runBlocking {
        val user = repository.getUser()
        updateUI(user) // UI freezes!
    }
}

// ❌ WRONG: Blocks in ViewModel
class MyViewModel : ViewModel() {
    fun loadData() {
        runBlocking { // Blocks UI thread!
            val data = repository.fetchData()
        }
    }
}
```

**Why wrong:**
- Blocks thread (defeats coroutines' non-blocking nature)
- Freezes UI on Android
- Wastes thread pool resources
- Can cause ANRs (Application Not Responding)

**✅ FIX: Use proper coroutine scope**

```kotlin
// ✅ CORRECT: Non-blocking
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            val data = repository.fetchData()
            _dataState.value = data
        }
    }
}

// ✅ CORRECT: In tests
@Test
fun testLoadData() = runTest { // Use runTest, not runBlocking
    val data = repository.fetchData()
    assertEquals(expected, data)
}
```

**When runBlocking is acceptable:**
- `main()` function in CLI apps
- Integration tests (use `runTest` for unit tests)
- Bridging blocking and suspending code (rare)

```kotlin
// ✅ ACCEPTABLE: main() in CLI app
fun main() = runBlocking {
    val data = fetchData()
    println(data)
}
```

#### Mistake 4: Mixing Blocking and Suspending Code

**Problem:** Calling blocking functions in coroutines wastes dispatcher threads.

```kotlin
// ❌ WRONG: Blocking call in coroutine
viewModelScope.launch(Dispatchers.Main) {
    val data = repository.getDataBlocking() // Blocks Main thread!
    updateUI(data)
}

// ❌ WRONG: Thread.sleep in coroutine
launch {
    Thread.sleep(1000) // Blocks thread!
    println("After sleep")
}
```

**Why wrong:**
- Blocks dispatcher thread
- Reduces available threads for other coroutines
- Can cause deadlocks
- Defeats coroutine advantages

**✅ FIX: Use withContext for blocking code**

```kotlin
// ✅ CORRECT: Move blocking work to IO dispatcher
viewModelScope.launch {
    val data = withContext(Dispatchers.IO) {
        repository.getDataBlocking() // Blocking call on IO thread
    }
    updateUI(data) // Back on Main thread
}

// ✅ CORRECT: Use delay, not Thread.sleep
launch {
    delay(1000) // Non-blocking delay
    println("After delay")
}

// ✅ CORRECT: Wrap blocking APIs
suspend fun readFile(path: String): String = withContext(Dispatchers.IO) {
    File(path).readText() // Blocking file I/O
}
```

**Example: Database query**

```kotlin
// ❌ WRONG
class UserRepository {
    suspend fun getUser(id: String): User {
        return database.query("SELECT * FROM users WHERE id = ?", id)
        // If database.query() is blocking, this wastes thread!
    }
}

// ✅ CORRECT
class UserRepository {
    suspend fun getUser(id: String): User = withContext(Dispatchers.IO) {
        database.query("SELECT * FROM users WHERE id = ?", id)
    }
}
```

#### Mistake 5: Not Using supervisorScope for Independent Tasks

**Problem:** One child failure cancels all siblings.

```kotlin
// ❌ WRONG: One failure cancels all
viewModelScope.launch {
    coroutineScope {
        launch { loadUsers() } // If this fails...
        launch { loadPosts() } // ...this gets cancelled!
        launch { loadComments() } // ...and this too!
    }
}
```

**Why wrong:**
- One child's failure cancels parent
- Parent cancellation cancels all children
- Independent tasks should fail independently

**✅ FIX: Use supervisorScope**

```kotlin
// ✅ CORRECT: Independent failure handling
viewModelScope.launch {
    supervisorScope {
        launch {
            try {
                loadUsers()
            } catch (e: Exception) {
                handleUserError(e)
            }
        }

        launch {
            try {
                loadPosts()
            } catch (e: Exception) {
                handlePostError(e)
            }
        }

        launch {
            try {
                loadComments()
            } catch (e: Exception) {
                handleCommentError(e)
            }
        }
    }
}

// ✅ CORRECT: Use SupervisorJob for scope
class MyRepository {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    fun loadData() {
        scope.launch { task1() } // Independent
        scope.launch { task2() } // Independent
        scope.launch { task3() } // Independent
    }
}
```

**Visual explanation:**

```
coroutineScope:
Parent
├── Child 1 (fails) ──> Cancels Parent ──> Cancels Child 2, 3
├── Child 2 (cancelled)
└── Child 3 (cancelled)

supervisorScope:
Parent
├── Child 1 (fails) ──> No effect on others
├── Child 2 (continues)
└── Child 3 (continues)
```

#### Mistake 6: Forgetting to Call await() on async

**Problem:** `async` result never collected, exception silently lost.

```kotlin
// ❌ WRONG: Never awaits result
viewModelScope.launch {
    async {
        repository.fetchData() // Exception silently lost!
    }
    // Result never used!
}

// ❌ WRONG: Starting async without awaiting
fun loadData() {
    viewModelScope.launch {
        val deferred1 = async { fetchUsers() }
        val deferred2 = async { fetchPosts() }

        // Forgot to await!
        // Results never collected, errors never handled
    }
}
```

**Why wrong:**
- Results never collected
- Exceptions silently lost
- Wasted work
- Misleading code (looks like it does something)

**✅ FIX: Always await() async results**

```kotlin
// ✅ CORRECT: await() results
viewModelScope.launch {
    try {
        val result = async {
            repository.fetchData()
        }.await() // Must await!

        updateUI(result)
    } catch (e: Exception) {
        handleError(e)
    }
}

// ✅ CORRECT: Parallel execution with await
suspend fun loadData() = coroutineScope {
    val users = async { fetchUsers() }
    val posts = async { fetchPosts() }

    val usersResult = users.await() // Wait for results
    val postsResult = posts.await()

    combine(usersResult, postsResult)
}

// ✅ BETTER: Use launch if you don't need result
viewModelScope.launch {
    try {
        repository.fetchData()
        // No result needed, use launch not async
    } catch (e: Exception) {
        handleError(e)
    }
}
```

**Rule of thumb:** If you don't need return value, use `launch`, not `async`.

#### Mistake 7: Creating Many Unnecessary Coroutines

**Problem:** Creating coroutines for every small operation.

```kotlin
// ❌ WRONG: Unnecessary coroutine overhead
suspend fun processItems(items: List<Item>) {
    items.forEach { item ->
        coroutineScope {
            launch { // Unnecessary!
                processItem(item)
            }
        }
    }
}

// ❌ WRONG: Coroutine for simple operation
viewModelScope.launch {
    val result = async { // Unnecessary!
        computeValue(x, y)
    }.await()
}
```

**Why wrong:**
- Overhead of coroutine creation
- Unnecessary complexity
- No concurrency benefit
- Harder to debug

**✅ FIX: Only create coroutines when needed**

```kotlin
// ✅ CORRECT: Sequential processing (no coroutines needed)
suspend fun processItems(items: List<Item>) {
    items.forEach { item ->
        processItem(item) // Already suspend, no launch needed
    }
}

// ✅ CORRECT: Parallel processing (coroutines make sense)
suspend fun processItemsParallel(items: List<Item>) = coroutineScope {
    items.map { item ->
        async { processItem(item) } // Parallel processing
    }.awaitAll()
}

// ✅ CORRECT: Simple computation (no coroutine needed)
viewModelScope.launch {
    val result = computeValue(x, y) // Direct call
}
```

**When to create coroutines:**
- Parallel execution needed
- Different dispatchers required
- Independent tasks
- Fire-and-forget operations

**When NOT to create coroutines:**
- Sequential suspend functions
- Simple computations
- Already in coroutine context

#### Mistake 8: Not Using Structured Concurrency

**Problem:** Manually managing Job lifecycle.

```kotlin
// ❌ WRONG: Manual job management
class MyViewModel : ViewModel() {
    private val jobs = mutableListOf<Job>()

    fun loadData() {
        val job = GlobalScope.launch {
            // Work
        }
        jobs.add(job)
    }

    override fun onCleared() {
        jobs.forEach { it.cancel() }
        jobs.clear()
    }
}
```

**Why wrong:**
- Error-prone (easy to forget cancellation)
- Verbose
- No automatic cleanup
- Defeats structured concurrency

**✅ FIX: Use proper scope**

```kotlin
// ✅ CORRECT: viewModelScope handles lifecycle
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            // Automatically cancelled when ViewModel cleared
        }
    }
    // No manual cleanup needed!
}

// ✅ CORRECT: Custom scope with cleanup
class MyRepository {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    fun loadData() {
        scope.launch {
            // Work
        }
    }

    fun cleanup() {
        scope.cancel() // Cancels all child coroutines
    }
}
```

**Structured concurrency benefits:**
- Automatic cancellation propagation
- Exception handling
- No manual job tracking
- Lifecycle-aware

#### Mistake 9: Memory Leaks from Captured Contexts

**Problem:** Coroutine captures reference to Activity/Fragment.

```kotlin
// ❌ WRONG: Captures Activity reference
class MyActivity : AppCompatActivity() {
    fun loadData() {
        GlobalScope.launch {
            delay(10000) // Long operation
            runOnUiThread {
                updateUI() // Captures 'this' (Activity)
            }
        }
    }
}
```

**Why wrong:**
- Activity reference kept alive
- Memory leak (Activity can't be garbage collected)
- Potential crash if Activity destroyed

**✅ FIX: Use proper scope and weak references**

```kotlin
// ✅ CORRECT: Use lifecycleScope
class MyActivity : AppCompatActivity() {
    fun loadData() {
        lifecycleScope.launch {
            val data = repository.fetchData()
            updateUI(data) // Safe: cancelled when Activity destroyed
        }
    }
}

// ✅ CORRECT: Pass data to ViewModel
class MyActivity : AppCompatActivity() {
    private val viewModel: MyViewModel by viewModels()

    fun loadData() {
        viewModel.loadData()

        lifecycleScope.launch {
            viewModel.dataState.collect { data ->
                updateUI(data)
            }
        }
    }
}

// ✅ CORRECT: Use weak reference (rare cases)
class MyActivity : AppCompatActivity() {
    fun loadData() {
        val activityRef = WeakReference(this)

        GlobalScope.launch {
            val data = fetchData()
            activityRef.get()?.runOnUiThread {
                updateUI(data)
            }
        }
    }
}
```

#### Mistake 10: Improper Exception Handling in launch vs async

**Problem:** Not understanding exception handling differences.

```kotlin
// ❌ WRONG: try-catch doesn't catch exception in launch
viewModelScope.launch {
    try {
        launch {
            throw Exception("Error") // Not caught!
        }
    } catch (e: Exception) {
        // Never executes!
    }
}

// ❌ WRONG: Not awaiting async
viewModelScope.launch {
    try {
        async {
            throw Exception("Error") // Exception stored in Deferred
        }
        // Exception not thrown yet!
    } catch (e: Exception) {
        // Never executes!
    }
}
```

**Why wrong:**
- Exceptions in `launch` propagate to parent
- Exceptions in `async` stored in `Deferred`, thrown on `await()`
- Try-catch placement matters

**✅ FIX: Proper exception handling**

```kotlin
// ✅ CORRECT: Catch inside launch
viewModelScope.launch {
    launch {
        try {
            doWork()
        } catch (e: Exception) {
            handleError(e)
        }
    }
}

// ✅ CORRECT: Catch around await()
viewModelScope.launch {
    try {
        val result = async {
            doWork()
        }.await() // Exception thrown here
    } catch (e: Exception) {
        handleError(e)
    }
}

// ✅ CORRECT: Use CoroutineExceptionHandler
val handler = CoroutineExceptionHandler { _, exception ->
    handleError(exception)
}

viewModelScope.launch(handler) {
    launch {
        throw Exception("Error") // Caught by handler
    }
}

// ✅ CORRECT: Use supervisorScope for independent tasks
viewModelScope.launch {
    supervisorScope {
        launch {
            try {
                task1()
            } catch (e: Exception) {
                handleError1(e)
            }
        }

        launch {
            try {
                task2()
            } catch (e: Exception) {
                handleError2(e)
            }
        }
    }
}
```

### Additional Common Mistakes

#### Mistake 11: Using Dispatchers.IO for CPU-Intensive Work

```kotlin
// ❌ WRONG: IO dispatcher for CPU work
viewModelScope.launch(Dispatchers.IO) {
    complexCalculation() // CPU-intensive, not I/O!
}

// ✅ CORRECT: Use Dispatchers.Default
viewModelScope.launch(Dispatchers.Default) {
    complexCalculation()
}
```

**Rule:**
- `Dispatchers.IO`: I/O operations (network, database, files)
- `Dispatchers.Default`: CPU-intensive work (parsing, calculations)
- `Dispatchers.Main`: UI operations

#### Mistake 12: Not Using withContext for Dispatcher Switching

```kotlin
// ❌ WRONG: Unnecessary launch
suspend fun fetchData(): Data {
    return GlobalScope.async(Dispatchers.IO) {
        api.fetch()
    }.await()
}

// ✅ CORRECT: Use withContext
suspend fun fetchData(): Data {
    return withContext(Dispatchers.IO) {
        api.fetch()
    }
}
```

### Code Review Checklist

**Coroutine Creation:**
- [ ] No `GlobalScope` usage
- [ ] Using proper scope (`viewModelScope`, `lifecycleScope`, etc.)
- [ ] Structured concurrency maintained

**Cancellation:**
- [ ] Loops check `isActive` or use `ensureActive()`
- [ ] Long operations use `yield()` or `delay()`
- [ ] Cancellable operations properly handled

**Exception Handling:**
- [ ] Try-catch placed correctly (inside launch or around await)
- [ ] `supervisorScope` used for independent tasks
- [ ] `CoroutineExceptionHandler` for uncaught exceptions

**Dispatchers:**
- [ ] `Dispatchers.Main` for UI operations
- [ ] `Dispatchers.IO` for I/O operations
- [ ] `Dispatchers.Default` for CPU-intensive work
- [ ] `withContext` used for dispatcher switching

**Lifecycle:**
- [ ] No memory leaks from captured contexts
- [ ] Proper scope usage (not `GlobalScope`)
- [ ] Resources cleaned up on cancellation

**Performance:**
- [ ] Not creating unnecessary coroutines
- [ ] Parallel execution where beneficial
- [ ] Proper use of `async`/`await` for parallelism

**Testing:**
- [ ] Using `runTest` instead of `runBlocking`
- [ ] Virtual time tested correctly
- [ ] Cancellation tested

### Detection Tools

**1. Android Lint:**

```kotlin
// Lint warns about GlobalScope
GlobalScope.launch { } // Warning: GlobalScope usage detected
```

**2. Detekt rules:**

```yaml
# .detekt.yml
coroutines:
  GlobalCoroutineUsage:
    active: true
  SuspendFunWithFlowReturnType:
    active: true
```

**3. Code search:**

```bash
# Find problematic patterns
grep -r "GlobalScope" --include="*.kt"
grep -r "runBlocking" --include="*.kt" | grep -v "test"
grep -r "Thread.sleep" --include="*.kt"
```

**4. LeakCanary:**

```kotlin
// Detects memory leaks from coroutines
dependencies {
    debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.x'
}
```

### How to Fix Each Mistake: Summary

1. **GlobalScope** → Use `viewModelScope`/`lifecycleScope`
2. **Not handling cancellation** → Check `isActive`, use `ensureActive()`
3. **runBlocking in production** → Use `launch`/`async`
4. **Mixing blocking and suspending** → Use `withContext(Dispatchers.IO)`
5. **Not using supervisorScope** → Use `supervisorScope` for independent tasks
6. **Forgetting await()** → Always `await()` on `async`
7. **Too many coroutines** → Only create when needed
8. **Not using structured concurrency** → Use proper scopes
9. **Memory leaks** → Use lifecycle-aware scopes
10. **Improper exception handling** → Try-catch inside launch, around await()

### Key Takeaways

1. **Never use GlobalScope** - Use lifecycle-aware scopes
2. **Always handle cancellation** - Check isActive, use ensureActive()
3. **Don't block threads** - No runBlocking or Thread.sleep in production
4. **Use proper dispatchers** - IO for I/O, Default for CPU, Main for UI
5. **supervisorScope for independence** - Independent task failures
6. **Always await() async** - Don't forget results
7. **Minimize coroutine creation** - Only when beneficial
8. **Structured concurrency** - Let framework manage lifecycle
9. **Avoid memory leaks** - Use proper scopes
10. **Proper exception handling** - Know launch vs async differences

---

## Русская версия

### Формулировка проблемы

Даже опытные разработчики совершают типичные ошибки при работе с Kotlin корутинами. Эти ошибки могут привести к утечкам памяти, крашам, состояниям гонки или плохой производительности. Понимание и избегание этих анти-паттернов критично для production-ready кода.

**Вопрос:** Какие самые распространенные ошибки при использовании Kotlin корутин, и как их исправить?

### Подробный ответ

[Полный русский перевод следует той же структуре]

### Ключевые выводы

1. **Никогда не используйте GlobalScope** - Используйте lifecycle-aware области
2. **Всегда обрабатывайте отмену** - Проверяйте isActive, используйте ensureActive()
3. **Не блокируйте потоки** - Никакого runBlocking или Thread.sleep в production
4. **Используйте правильные диспетчеры** - IO для I/O, Default для CPU, Main для UI
5. **supervisorScope для независимости** - Независимые сбои задач
6. **Всегда await() async** - Не забывайте результаты
7. **Минимизируйте создание корутин** - Только когда полезно
8. **Структурированная конкурентность** - Позвольте фреймворку управлять lifecycle
9. **Избегайте утечек памяти** - Используйте правильные области
10. **Правильная обработка исключений** - Знайте различия launch vs async

---

## Follow-ups

1. How do you implement custom CoroutineScope with proper lifecycle management?
2. What tools exist for detecting coroutine-related memory leaks?
3. How do you refactor legacy code with GlobalScope to use proper scopes?
4. Can you explain the performance impact of excessive coroutine creation?
5. How do you audit a codebase for coroutine anti-patterns?
6. What are the most subtle coroutine bugs that are hard to detect?
7. How do you educate a team about coroutine best practices?

## References

- [Kotlin Coroutines Best Practices](https://kotlinlang.org/docs/coroutines-guide.html)
- [Android Coroutines Best Practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)
- [Common Coroutine Mistakes](https://elizarov.medium.com/top-10-coroutines-mistakes-42b19c2a25b2)

## Related Questions

- [[q-coroutine-exception-handler--kotlin--medium|CoroutineExceptionHandler usage]]
- [[q-debugging-coroutines-techniques--kotlin--medium|Debugging coroutines]]
- [[q-mutex-synchronized-coroutines--kotlin--medium|Thread-safe coroutines]]
