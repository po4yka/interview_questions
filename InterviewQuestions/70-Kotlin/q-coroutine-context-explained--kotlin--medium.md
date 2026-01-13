---
anki_cards:
- slug: q-coroutine-context-explained--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-coroutine-context-explained--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
## Answer (EN)

**CoroutineContext** is an indexed set of `Element` instances that defines the behavior and environment of a coroutine. It's a fundamental concept in Kotlin coroutines that determines how, where, and under what conditions a coroutine executes.

### Core Concept

`CoroutineContext` is an **immutable indexed set** where each element has a unique `Key`. You can think of it as a `Map<Key, Element>` where elements can be combined and accessed by their keys.

```kotlin
interface CoroutineContext {
    operator fun <E : Element> get(key: Key<E>): E?
    operator fun plus(context: CoroutineContext): CoroutineContext
    fun minusKey(key: Key<*>)

    interface Element : CoroutineContext {
        val key: Key<*>
    }

    interface Key<E : Element>
}
```

### Main Elements

#### 1. Job - Lifecycle Management

Controls coroutine lifecycle, cancellation, and parent-child relationships.

```kotlin
val job = Job()
val scope = CoroutineScope(job)

scope.launch {
    println("Working...")
    delay(1000)
    println("Done!")
}

job.cancel()  // Cancels all coroutines in scope
```

Job hierarchy:

```kotlin
val parentJob = Job()
val scope = CoroutineScope(parentJob)

val childJob1 = scope.launch {
    println("Child 1")
}

val childJob2 = scope.launch {
    println("Child 2")
}

parentJob.cancel()  // Cancels both children
```

Key properties:
- `isActive`, `isCompleted`, `isCancelled`
- `children` for accessing child jobs

```kotlin
val scope = CoroutineScope(Job())

val job = scope.launch {
    println("isActive: ${'$'}{coroutineContext[Job]?.isActive}")
    delay(1000)
}

job.invokeOnCompletion { exception ->
    println("Completed with: $exception")
}
```

#### 2. CoroutineDispatcher - Thread Assignment

Determines which thread(s) the coroutine executes on.

```kotlin
val scope = CoroutineScope(Dispatchers.Main)

// Main thread (Android UI thread)
scope.launch {
    textView.text = "Updated on UI thread"
}

// IO thread pool (for network, disk operations)
scope.launch(Dispatchers.IO) {
    val data = fetchDataFromNetwork()
}

// Default thread pool (for CPU-intensive work)
scope.launch(Dispatchers.Default) {
    val result = performHeavyComputation()
}

// Unconfined (not recommended for production)
scope.launch(Dispatchers.Unconfined) {
    // Starts in caller thread, resumes in any thread
}
```

Android `ViewModel` scope example:

```kotlin
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch(Dispatchers.IO) {
            val data = repository.getData()  // IO thread

            withContext(Dispatchers.Main) {
                _uiState.value = UiState.Success(data)  // Main thread
            }
        }
    }
}
```

Custom dispatcher example:

```kotlin
val customDispatcher = Dispatchers.IO.limitedParallelism(1)

val scope = CoroutineScope(customDispatcher)

scope.launch {
    // Only 1 coroutine executes at a time on this dispatcher
}
```

#### 3. CoroutineExceptionHandler - Error Handling

Handles uncaught exceptions in coroutines started with `launch` (and other fire-and-forget builders). For `async`, exceptions are reported when `await()` is called and should be handled with try/catch around `await()`.

```kotlin
val handler = CoroutineExceptionHandler { context, exception ->
    println("Caught $exception in ${'$'}{context[CoroutineName]?.name}")
}

val scope = CoroutineScope(Job() + handler)

scope.launch(CoroutineName("Root")) {
    throw RuntimeException("Oops!")  // Caught by handler
}

val deferred = scope.async(CoroutineName("AsyncChild")) {
    throw RuntimeException("Async failure")  // Not handled by handler directly
}

scope.launch {
    try {
        deferred.await()
    } catch (e: Exception) {
        println("Caught from async: $e")
    }
}
```

Important: `CoroutineExceptionHandler` participates in handling uncaught exceptions of root coroutines in its context, including exceptions from their child coroutines, according to structured concurrency rules.

#### 4. CoroutineName - Debugging

Assigns a name to coroutines for debugging and logging.

```kotlin
val scope = CoroutineScope(Dispatchers.Default)

scope.launch(CoroutineName("DataLoader")) {
    println("Running in: ${'$'}{coroutineContext[CoroutineName]?.name}")
    // Output: Running in: DataLoader
}
```

`Thread` names example:

```kotlin
val scope = CoroutineScope(Dispatchers.IO)

scope.launch(CoroutineName("NetworkCall")) {
    println(Thread.currentThread().name)
    // Example: DefaultDispatcher-worker-1 @NetworkCall#1
}
```

Note: besides these commonly used elements, the context also includes standard elements such as `ContinuationInterceptor` and other `CoroutineContext.Element` implementations in the library.

### Context Composition

Elements combine using the `+` operator:

```kotlin
val context = Dispatchers.IO +
              Job() +
              CoroutineName("DataProcessor") +
              handler

val scope = CoroutineScope(context)

scope.launch {
    // Coroutine with combined context
}
```

Later elements override earlier ones with the same key:

```kotlin
val context1 = Dispatchers.IO + Dispatchers.Main
// Result: Dispatchers.Main (overrides IO)

val context2 = CoroutineName("First") + CoroutineName("Second")
// Result: CoroutineName("Second")
```

### Context Inheritance

Child coroutines inherit parent context but can override specific elements:

```kotlin
val parentContext = Dispatchers.Main + CoroutineName("Parent")
val scope = CoroutineScope(parentContext)

scope.launch {
    println(coroutineContext[CoroutineName]?.name)  // "Parent"

    launch(Dispatchers.IO) {  // Override dispatcher only
        println(coroutineContext[CoroutineName]?.name)  // Still "Parent"
        println(Thread.currentThread().name)  // IO thread
    }
}
```

A new `Job` is created for each `launch`/`async`, as a child of the parent `Job` if present:

```kotlin
val scope = CoroutineScope(Job())

scope.launch {
    val myJob = coroutineContext[Job]
    val scopeJob = scope.coroutineContext[Job]

    println(myJob !== scopeJob)          // true: child job
    println(myJob?.parent === scopeJob)  // true
}
```

### Accessing Context Elements

Inside a coroutine:

```kotlin
val scope = CoroutineScope(Dispatchers.IO)

scope.launch(CoroutineName("Worker")) {
    val name = coroutineContext[CoroutineName]?.name
    val job = coroutineContext[Job]
    val dispatcher = coroutineContext[ContinuationInterceptor]

    println("Name: $name")
    println("Job: $job")
    println("Dispatcher: $dispatcher")
}
```

From a `CoroutineScope` implementation:

```kotlin
class MyRepository : CoroutineScope {
    override val coroutineContext = Dispatchers.IO + SupervisorJob()

    fun fetchData() {
        launch {
            // Uses repository's context
        }
    }
}
```

### Structured Concurrency

`CoroutineContext` and `Job` hierarchy enable structured concurrency:

```kotlin
val scope = CoroutineScope(Job() + Dispatchers.Main)

scope.launch {  // Parent
    launch {
        delay(1000)
        println("Child 1 done")
    }

    launch {
        delay(500)
        throw Exception("Child 2 failed")
    }
}
// Parent waits for children and propagates exception according to Job hierarchy
```

`SupervisorJob` for independent children:

```kotlin
val scope = CoroutineScope(SupervisorJob())

scope.launch {
    launch {
        throw Exception("Failed")  // Doesn't cancel siblings
    }

    launch {
        delay(1000)
        println("Still running")
    }
}
```

### Real Android Examples

`ViewModel` with proper context:

```kotlin
class UserViewModel : ViewModel() {
    private val exceptionHandler = CoroutineExceptionHandler { _, e ->
        Timber.e(e)
        _error.value = e.message
    }

    private val scope = viewModelScope + exceptionHandler

    fun loadUser(id: String) {
        scope.launch {
            _loading.value = true
            try {
                val user = withContext(Dispatchers.IO) {
                    repository.getUser(id)
                }
                _user.value = user
            } finally {
                _loading.value = false
            }
        }
    }
}
```

Repository with custom context:

```kotlin
class UserRepository(
    private val api: ApiService,
    private val db: UserDao
) {
    private val ioDispatcher = Dispatchers.IO.limitedParallelism(10)

    suspend fun getUser(id: String): User = withContext(ioDispatcher) {
        try {
            api.getUser(id).also { user ->
                db.insert(user)
            }
        } catch (e: IOException) {
            db.getUser(id) ?: throw e
        }
    }
}
```

### Common Patterns

1. `Context` switching:

```kotlin
val scope = CoroutineScope(Dispatchers.Main)

scope.launch {
    val user = withContext(Dispatchers.IO) {
        // Temporarily switch to IO
        repository.getUser()
    }  // Back to Main

    updateUI(user)  // On Main thread
}
```

1. Combining contexts:

```kotlin
val baseContext = Dispatchers.IO + CoroutineName("Worker")

val scope = CoroutineScope(baseContext)

scope.launch(Job()) {
    // New job, but keeps IO and name via combination with parent context
}
```

1. Removing elements:

```kotlin
val context = Dispatchers.IO + CoroutineName("Test") + Job()
val newContext = context.minusKey(CoroutineName)
// Result: Dispatchers.IO + Job()
```

### Key Takeaways

1. `CoroutineContext` is immutable — operations return new contexts.
2. Elements are indexed by `Key` — one element per key.
3. Composition via `+` — later elements override earlier ones with the same key.
4. Inheritance from parent — each child gets a new `Job` as a child of the parent `Job` if present.
5. Commonly used elements: `Job`, `CoroutineDispatcher`, `CoroutineExceptionHandler`, `CoroutineName` (this list is not exhaustive).
6. Structured concurrency — enforced through `Job` hierarchy and context inheritance.

---

## Дополнительные Вопросы (RU)

- В чём ключевые отличия подхода Kotlin coroutines от традиционного Java-подхода к потокам?
- Когда на практике вы будете явно задавать или менять `CoroutineContext`?
- Как избежать распространённых ошибок при работе с `CoroutineContext` (утечки, неверный dispatcher и т.п.)?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Kotlin `Coroutines` Guide - `Coroutine` `Context`](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
- [CoroutineContext (stdlib) API](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.coroutines/-coroutine-context/)
- [[c-kotlin]]
- [[c-coroutines]]

## References

- [Kotlin `Coroutines` Guide - `Coroutine` `Context`](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
- [CoroutineContext (stdlib) API](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.coroutines/-coroutine-context/)
- [[c-kotlin]]
- [[c-coroutines]]

---

## Связанные Вопросы (RU)

### Средний Уровень
- [[q-coroutine-dispatchers--kotlin--medium]] — Коррутины
- [[q-coroutine-builders-comparison--kotlin--medium]] — Коррутины
- [[q-callback-to-coroutine-conversion--kotlin--medium]] — Коррутины
- [[q-parallel-network-calls-coroutines--kotlin--medium]] — Коррутины

### Продвинутый Уровень
- [[q-actor-pattern--kotlin--hard]] — Коррутины
- [[q-fan-in-fan-out--kotlin--hard]] — Коррутины

### Хаб
- [[q-kotlin-coroutines-introduction--kotlin--medium]] — Обзор корутин

## Related Questions

### Related (Medium)
- [[q-coroutine-dispatchers--kotlin--medium]] - `Coroutines`
- [[q-coroutine-builders-comparison--kotlin--medium]] - `Coroutines`
- [[q-callback-to-coroutine-conversion--kotlin--medium]] - `Coroutines`
- [[q-parallel-network-calls-coroutines--kotlin--medium]] - `Coroutines`

### Advanced (Harder)
- [[q-actor-pattern--kotlin--hard]] - `Coroutines`
- [[q-fan-in-fan-out--kotlin--hard]] - `Coroutines`

### Hub
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Comprehensive coroutines introduction