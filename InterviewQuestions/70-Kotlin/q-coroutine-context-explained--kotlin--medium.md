---
id: kotlin-039
title: Coroutine Context Explained / CoroutineContext объяснение
aliases: [Coroutine Context Explained, CoroutineContext объяснение]
topic: kotlin
subtopics: [coroutine-context, coroutines]
question_kind: theory
difficulty: medium
original_language: ru
language_tags: [en, ru]
source: ""
source_note: ""
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-inline-value-classes-performance--kotlin--medium, q-kotlin-channels--kotlin--medium]
created: 2025-10-06
updated: 2025-11-11
tags: [async-programming, concurrency, coroutine-context, coroutines, difficulty/medium, kotlin]

date created: Sunday, October 12th 2025, 12:27:46 pm
date modified: Tuesday, November 25th 2025, 8:53:52 pm
---
# Вопрос (RU)
> Что такое CoroutineContext и какие у него основные элементы?

# Question (EN)
> What is CoroutineContext and what are its main elements?

## Ответ (RU)

**CoroutineContext** — это индексированный набор элементов `Element`, который определяет поведение и окружение корутины. Это фундаментальная концепция в Kotlin coroutines, определяющая как, где и при каких условиях выполняется корутина.

### Основная Концепция

`CoroutineContext` — это **неизменяемый индексированный набор**, где каждый элемент имеет уникальный `Key`. Его можно представить как `Map<Key, Element>`, где элементы можно комбинировать и получать по ключам.

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

### Основные Элементы Контекста

**1. Job** — Управляет жизненным циклом корутины. Позволяет отменять корутину и отслеживать её состояние. Также определяет отношения родитель-дети и используется для структурированной конкурентности.

```kotlin
val job = Job()
val scope = CoroutineScope(job)

scope.launch {
    println("Working...")
    delay(1000)
    println("Done!")
}

job.cancel()  // Отмена всех корутин в scope
```

Иерархия `Job`:

```kotlin
val parentJob = Job()
val scope = CoroutineScope(parentJob)

val childJob1 = scope.launch {
    println("Child 1")
}

val childJob2 = scope.launch {
    println("Child 2")
}

parentJob.cancel()  // Отменяет обе дочерние корутины
```

Ключевые свойства `Job`:
- `isActive`, `isCompleted`, `isCancelled`
- `children` — доступ к дочерним job

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

**2. CoroutineDispatcher** — Определяет, на каких потоках будет выполняться корутина.

```kotlin
val scope = CoroutineScope(Dispatchers.Main)

// Главный поток (UI)
scope.launch {
    // Обновление UI
}

// Пул потоков для I/O операций
scope.launch(Dispatchers.IO) {
    val data = fetchDataFromNetwork()
}

// Пул потоков для CPU-интенсивных операций
scope.launch(Dispatchers.Default) {
    val result = performHeavyComputation()
}

// Unconfined (обычно не рекомендуется для продакшена)
scope.launch(Dispatchers.Unconfined) {
    // Старт в потоке вызывающего, продолжение в любом потоке
}
```

Пример с `viewModelScope` в `ViewModel`:

```kotlin
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch(Dispatchers.IO) {
            val data = repository.getData()  // IO поток

            withContext(Dispatchers.Main) {
                _uiState.value = UiState.Success(data)  // Главный поток
            }
        }
    }
}
```

Кастомный диспетчер:

```kotlin
val customDispatcher = Dispatchers.IO.limitedParallelism(1)

val scope = CoroutineScope(customDispatcher)

scope.launch {
    // В каждый момент времени выполняется только одна корутина
}
```

**3. CoroutineExceptionHandler** — Обрабатывает неперехваченные исключения в корутинах, запущенных через `launch` и другие fire-and-forget билдеры. Для `async` исключения пробрасываются при вызове `await()` и должны обрабатываться через try/catch вокруг `await()`.

```kotlin
val handler = CoroutineExceptionHandler { context, exception ->
    println("Caught $exception in ${'$'}{context[CoroutineName]?.name}")
}

val scope = CoroutineScope(Job() + handler)

scope.launch(CoroutineName("Root")) {
    throw RuntimeException("Oops!")  // Будет перехвачено handler
}

val deferred = scope.async(CoroutineName("AsyncChild")) {
    throw RuntimeException("Async failure")  // Не обрабатывается handler напрямую
}

scope.launch {
    try {
        deferred.await()
    } catch (e: Exception) {
        println("Caught from async: $e")
    }
}
```

Важно: `CoroutineExceptionHandler` участвует в обработке неперехваченных исключений корневых корутин в его контексте, включая дочерние корутины, согласно правилам структурированной конкурентности.

**4. CoroutineName** — Назначает имя корутине для отладки.

```kotlin
val scope = CoroutineScope(Dispatchers.Default)

scope.launch(CoroutineName("DataLoader")) {
    println("Running in: ${'$'}{coroutineContext[CoroutineName]?.name}")
}
```

Пример с именем в имени потока:

```kotlin
val scope = CoroutineScope(Dispatchers.IO)

scope.launch(CoroutineName("NetworkCall")) {
    println(Thread.currentThread().name)
    // Пример: DefaultDispatcher-worker-1 @NetworkCall#1
}
```

Примечание: помимо этих часто используемых элементов, в контекст также входят стандартные элементы вроде `ContinuationInterceptor` и других `CoroutineContext.Element` в библиотеке.

### Композиция Контекста

Элементы контекста можно комбинировать с помощью оператора `+`:

```kotlin
val context = Dispatchers.IO +
              Job() +
              CoroutineName("DataProcessor") +
              handler

val scope = CoroutineScope(context)

scope.launch {
    // Корутина с объединённым контекстом
}
```

Поздние элементы с тем же ключом переопределяют ранние:

```kotlin
val context1 = Dispatchers.IO + Dispatchers.Main
// Результат: Dispatchers.Main (переопределяет IO)

val context2 = CoroutineName("First") + CoroutineName("Second")
// Результат: CoroutineName("Second")
```

### Наследование Контекста

Дочерние корутины наследуют контекст родителя, но могут переопределять отдельные элементы.

```kotlin
val parentContext = Dispatchers.Main + CoroutineName("Parent")
val scope = CoroutineScope(parentContext)

scope.launch {
    println(coroutineContext[CoroutineName]?.name)  // "Parent"

    launch(Dispatchers.IO) {  // Переопределяем только dispatcher
        println(coroutineContext[CoroutineName]?.name)  // Всё ещё "Parent"
        println(Thread.currentThread().name)  // IO поток
    }
}
```

Для каждого `launch`/`async` создаётся новый `Job` как дочерний от родительского `Job`, если он есть:

```kotlin
val scope = CoroutineScope(Job())

scope.launch {
    val myJob = coroutineContext[Job]
    val scopeJob = scope.coroutineContext[Job]

    println(myJob !== scopeJob)          // true: дочерний job
    println(myJob?.parent === scopeJob)  // true
}
```

### Доступ К Элементам Контекста

Внутри корутины:

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

Из собственной реализации `CoroutineScope`:

```kotlin
class MyRepository : CoroutineScope {
    override val coroutineContext = Dispatchers.IO + SupervisorJob()

    fun fetchData() {
        launch {
            // Использует контекст репозитория
        }
    }
}
```

### Структурированная Конкурентность

`CoroutineContext` и иерархия `Job` обеспечивают структурированную конкурентность:

```kotlin
val scope = CoroutineScope(Job() + Dispatchers.Main)

scope.launch {  // Родитель
    launch {
        delay(1000)
        println("Child 1 done")
    }

    launch {
        delay(500)
        throw Exception("Child 2 failed")
    }
}
// Родитель ждёт детей и обрабатывает исключение согласно иерархии Job
```

`SupervisorJob` позволяет изолировать ошибки дочерних корутин:

```kotlin
val scope = CoroutineScope(SupervisorJob())

scope.launch {
    launch {
        throw Exception("Failed")  // Не отменяет соседние корутины
    }

    launch {
        delay(1000)
        println("Still running")
    }
}
```

### Реальные Примеры В Android

`ViewModel` с корректным использованием контекста:

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

Репозиторий с кастомным контекстом:

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

### Частые Паттерны

1. Переключение контекста:

```kotlin
val scope = CoroutineScope(Dispatchers.Main)

scope.launch {
    val user = withContext(Dispatchers.IO) {
        // Временный переход на IO
        repository.getUser()
    }  // Возврат на Main

    updateUI(user)  // На главном потоке
}
```

1. Комбинация контекстов:

```kotlin
val baseContext = Dispatchers.IO + CoroutineName("Worker")

val scope = CoroutineScope(baseContext)

scope.launch(Job()) {
    // Новый Job, но сохраняются IO и имя через композицию
}
```

1. Удаление элементов:

```kotlin
val context = Dispatchers.IO + CoroutineName("Test") + Job()
val newContext = context.minusKey(CoroutineName)
// Результат: Dispatchers.IO + Job()
```

### Ключевые Моменты

1. `CoroutineContext` неизменяем — операции возвращают новые контексты.
2. Элементы индексируются по `Key` — по одному элементу на каждый ключ.
3. Композиция через `+` — поздние элементы переопределяют ранние.
4. Наследование от родителя — дочерние корутины получают новый `Job` как дочерний, если родительский `Job` присутствует.
5. Часто используемые элементы: `Job`, `CoroutineDispatcher`, `CoroutineExceptionHandler`, `CoroutineName` (этот список не исчерпывающий).
6. Структурированная конкурентность — обеспечивается иерархией `Job` и наследованием контекста.

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

Thread names example:

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