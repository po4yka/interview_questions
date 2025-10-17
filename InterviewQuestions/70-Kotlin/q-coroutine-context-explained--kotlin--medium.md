---
id: 20251012-12271111100
title: Coroutine Context Explained / CoroutineContext объяснение
aliases: []

# Classification
topic: kotlin
subtopics: [coroutines, coroutine-context, async, concurrency]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: ""
source_note: ""

# Workflow & relations
status: draft
moc: moc-kotlin
related: []

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [kotlin, coroutines, coroutine-context, async-programming, concurrency, difficulty/medium]
---
# Question (EN)
> What is CoroutineContext and what are its main elements?

# Вопрос (RU)
> Что такое CoroutineContext и какие у него основные элементы?

---

## Answer (EN)

**CoroutineContext** is an indexed set of `Element` instances that defines the behavior and environment of a coroutine. It's a fundamental concept in Kotlin coroutines that determines how, where, and under what conditions a coroutine executes.

### Core Concept

CoroutineContext is an **immutable indexed set** where each element has a unique `Key`. Think of it as a `Map<Key, Element>` where elements can be combined and accessed by their keys.

```kotlin
interface CoroutineContext {
    operator fun <E : Element> get(key: Key<E>): E?
    operator fun plus(context: CoroutineContext): CoroutineContext
    fun minusKey(key: Key<*>): CoroutineContext

    interface Element : CoroutineContext {
        val key: Key<*>
    }

    interface Key<E : Element>
}
```

### Main Elements

#### 1. **Job** - Lifecycle Management

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

**Job hierarchy:**
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

**Key properties:**
- `isActive`: Is the job currently active?
- `isCompleted`: Has the job completed?
- `isCancelled`: Was the job cancelled?
- `children`: Access child jobs

```kotlin
val job = launch {
    println("isActive: ${coroutineContext[Job]?.isActive}")
    delay(1000)
}

job.invokeOnCompletion { exception ->
    println("Completed with: $exception")
}
```

#### 2. **CoroutineDispatcher** - Thread Assignment

Determines which thread(s) the coroutine executes on.

```kotlin
// Main thread (Android UI thread)
launch(Dispatchers.Main) {
    textView.text = "Updated on UI thread"
}

// IO thread pool (for network, disk operations)
launch(Dispatchers.IO) {
    val data = fetchDataFromNetwork()
}

// Default thread pool (for CPU-intensive work)
launch(Dispatchers.Default) {
    val result = performHeavyComputation()
}

// Unconfined (not recommended)
launch(Dispatchers.Unconfined) {
    // Starts in caller thread, resumes in any thread
}
```

**Android ViewModelScope example:**
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

**Dispatcher internals:**
```kotlin
// Custom dispatcher with limited parallelism
val customDispatcher = Dispatchers.IO.limitedParallelism(1)

launch(customDispatcher) {
    // Only 1 coroutine executes at a time
}
```

#### 3. **CoroutineExceptionHandler** - Error Handling

Catches uncaught exceptions in coroutines (only works with `launch`, not `async`).

```kotlin
val handler = CoroutineExceptionHandler { context, exception ->
    println("Caught $exception in ${context[CoroutineName]?.name}")
    // Log to Crashlytics, show error UI, etc.
}

val scope = CoroutineScope(Job() + handler)

scope.launch {
    throw RuntimeException("Oops!")  // Caught by handler
}

scope.async {
    throw RuntimeException("Not caught!")  // Handler doesn't work with async!
}
```

**Important**: ExceptionHandler only catches exceptions in **root** coroutines:
```kotlin
val handler = CoroutineExceptionHandler { _, e ->
    println("Caught: $e")
}

launch(handler) {
    // - Handler works here (root coroutine)
    throw Exception("Error")
}

launch {
    launch(handler) {
        // - Handler doesn't work (child coroutine)
        throw Exception("Error")
    }
}
```

**Android example:**
```kotlin
class MyViewModel : ViewModel() {
    private val exceptionHandler = CoroutineExceptionHandler { _, exception ->
        _errorState.value = exception.message
        Timber.e(exception, "Coroutine exception")
    }

    private val scope = CoroutineScope(
        SupervisorJob() + Dispatchers.Main + exceptionHandler
    )

    fun loadData() {
        scope.launch {
            throw IOException("Network error")  // Caught by handler
        }
    }
}
```

#### 4. **CoroutineName** - Debugging

Assigns a name to coroutines for debugging and logging.

```kotlin
launch(CoroutineName("DataLoader")) {
    println("Running in: ${coroutineContext[CoroutineName]?.name}")
    // Output: Running in: DataLoader
}
```

**Thread names:**
```kotlin
launch(Dispatchers.IO + CoroutineName("NetworkCall")) {
    println(Thread.currentThread().name)
    // Output: DefaultDispatcher-worker-1 @NetworkCall#1
}
```

### Context Composition

Elements combine using the `+` operator:

```kotlin
val context = Dispatchers.IO +
              Job() +
              CoroutineName("DataProcessor") +
              exceptionHandler

launch(context) {
    // Coroutine with combined context
}
```

**Later elements override earlier ones** with the same key:
```kotlin
val context1 = Dispatchers.IO + Dispatchers.Main
// Result: Dispatchers.Main (overrides IO)

val context2 = CoroutineName("First") + CoroutineName("Second")
// Result: CoroutineName("Second")
```

### Context Inheritance

Child coroutines inherit parent context but can override elements:

```kotlin
val parentContext = Dispatchers.Main + CoroutineName("Parent")

launch(parentContext) {
    println(coroutineContext[CoroutineName]?.name)  // "Parent"

    launch(Dispatchers.IO) {  // Override dispatcher
        println(coroutineContext[CoroutineName]?.name)  // Still "Parent"
        println(Thread.currentThread().name)  // IO thread
    }
}
```

**New Job always created:**
```kotlin
val scope = CoroutineScope(Job())

scope.launch {  // Gets NEW Job, child of scope's Job
    val myJob = coroutineContext[Job]
    val scopeJob = scope.coroutineContext[Job]

    println(myJob !== scopeJob)  // true
    println(myJob?.parent === scopeJob)  // true
}
```

### Accessing Context Elements

**Inside coroutine:**
```kotlin
launch(Dispatchers.IO + CoroutineName("Worker")) {
    val name = coroutineContext[CoroutineName]?.name
    val job = coroutineContext[Job]
    val dispatcher = coroutineContext[ContinuationInterceptor]

    println("Name: $name")
    println("Job: $job")
    println("Dispatcher: $dispatcher")
}
```

**From CoroutineScope:**
```kotlin
class MyRepository : CoroutineScope {
    override val coroutineContext = Dispatchers.IO + SupervisorJob()

    fun fetchData() {
        launch {  // Uses repository's context
            // ...
        }
    }
}
```

### Structured Concurrency

Context ensures structured concurrency through Job hierarchy:

```kotlin
val scope = CoroutineScope(Job() + Dispatchers.Main)

scope.launch {  // Parent
    launch {  // Child 1
        delay(1000)
        println("Child 1 done")
    }

    launch {  // Child 2
        delay(500)
        throw Exception("Child 2 failed")
    }
}  // Parent waits for all children, then propagates exception
```

**SupervisorJob for independent children:**
```kotlin
val scope = CoroutineScope(SupervisorJob())

scope.launch {  // Parent
    launch {  // Child 1
        throw Exception("Failed")  // Doesn't affect Child 2
    }

    launch {  // Child 2
        delay(1000)
        println("Still running")  // - Continues
    }
}
```

### Real Android Examples

**ViewModel with proper context:**
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

**Repository with custom context:**
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

**1. Context switching:**
```kotlin
launch(Dispatchers.Main) {
    val user = withContext(Dispatchers.IO) {
        // Temporarily switch to IO
        repository.getUser()
    }  // Back to Main

    updateUI(user)  // On Main thread
}
```

**2. Combining contexts:**
```kotlin
val baseContext = Dispatchers.IO + CoroutineName("Worker")

launch(baseContext + Job()) {
    // New job, but keeps IO and name
}
```

**3. Removing elements:**
```kotlin
val context = Dispatchers.IO + CoroutineName("Test") + Job()
val newContext = context.minusKey(CoroutineName)
// Result: Dispatchers.IO + Job()
```

### Key Takeaways

1. **CoroutineContext is immutable** - Operations return new contexts
2. **Elements are indexed by Key** - Unique per element type
3. **Composition via +** - Later elements override earlier ones
4. **Inheritance from parent** - With new Job created
5. **Four main elements**: Job, Dispatcher, ExceptionHandler, Name
6. **Structured concurrency** - Enforced through Job hierarchy

---

## Ответ (RU)

**CoroutineContext** — это индексированный набор элементов `Element`, который определяет поведение и окружение корутины. Это фундаментальная концепция в Kotlin coroutines, определяющая как, где и при каких условиях выполняется корутина.

### Основная концепция

CoroutineContext — это **неизменяемый индексированный набор**, где каждый элемент имеет уникальный `Key`. Можно представить как `Map<Key, Element>`, где элементы можно комбинировать и получать по ключам.

### Основные элементы контекста

**1. Job** - Управляет жизненным циклом корутины. Позволяет отменять корутину и отслеживать её состояние.

```kotlin
val job = Job()
val scope = CoroutineScope(job)

scope.launch {
    // Работа корутины
}

job.cancel()  // Отмена всех корутин в scope
```

**2. Dispatcher** - Определяет, на каком потоке будет выполняться корутина.

```kotlin
launch(Dispatchers.Main) {
    // Выполняется в главном потоке (UI)
}

launch(Dispatchers.IO) {
    // Выполняется в пуле потоков для I/O операций
}

launch(Dispatchers.Default) {
    // Выполняется в пуле потоков для CPU-интенсивных операций
}
```

**3. CoroutineExceptionHandler** - Обрабатывает исключения, возникающие в корутинах.

```kotlin
val handler = CoroutineExceptionHandler { _, exception ->
    println("Caught $exception")
}

val scope = CoroutineScope(Job() + handler)
scope.launch {
    throw Exception("Error!")
}
```

**4. CoroutineName** - Назначает имя корутине для отладки.

```kotlin
launch(CoroutineName("MyCoroutine")) {
    println(coroutineContext[CoroutineName]?.name)  // "MyCoroutine"
}
```

### Композиция контекста

Элементы контекста можно комбинировать с помощью оператора `+`:

```kotlin
val context = Dispatchers.IO + Job() + CoroutineName("DataLoader")

launch(context) {
    // Корутина с объединённым контекстом
}
```

### Наследование контекста

Дочерние корутины наследуют контекст родителя, но могут переопределять элементы:

```kotlin
val parentContext = Dispatchers.Main + CoroutineName("Parent")

launch(parentContext) {
    launch(Dispatchers.IO) {  // Переопределяем dispatcher
        // Выполняется на IO потоке, но имя остается "Parent"
    }
}
```

### Пример для Android

```kotlin
class MyViewModel : ViewModel() {
    private val exceptionHandler = CoroutineExceptionHandler { _, e ->
        _error.value = e.message
    }

    fun loadData() {
        viewModelScope.launch(exceptionHandler) {
            val data = withContext(Dispatchers.IO) {
                repository.getData()
            }
            _uiState.value = UiState.Success(data)
        }
    }
}
```

### Ключевые моменты

1. **CoroutineContext неизменяем** - операции возвращают новые контексты
2. **Элементы индексируются по Key** - уникальный на тип элемента
3. **Композиция через +** - поздние элементы переопределяют ранние
4. **Наследование от родителя** - с созданием нового Job
5. **Четыре основных элемента**: Job, Dispatcher, ExceptionHandler, Name
6. **Структурированная конкурентность** - через иерархию Job

---

## References
- [Kotlin Coroutines Guide - Coroutine Context](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
- [CoroutineContext API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-context/)


---

## Related Questions

### Related (Medium)
- [[q-coroutine-dispatchers--kotlin--medium]] - Coroutines
- [[q-coroutine-builders-comparison--kotlin--medium]] - Coroutines
- [[q-callback-to-coroutine-conversion--kotlin--medium]] - Coroutines
- [[q-parallel-network-calls-coroutines--kotlin--medium]] - Coroutines

### Advanced (Harder)
- [[q-actor-pattern--kotlin--hard]] - Coroutines
- [[q-fan-in-fan-out--kotlin--hard]] - Coroutines

### Hub
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Comprehensive coroutines introduction

