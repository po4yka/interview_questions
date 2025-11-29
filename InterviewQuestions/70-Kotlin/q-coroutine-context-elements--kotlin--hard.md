---
id: kotlin-239
title: "What are CoroutineContext elements and how do they combine? / Элементы CoroutineContext и их комбинирование"
aliases: [CoroutineContext Elements, Элементы CoroutineContext]
topic: kotlin
subtopics: [coroutines]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
created: "2025-10-12"
updated: "2025-11-11"
tags: [coroutines, difficulty/hard, kotlin]
description: "Comprehensive guide to CoroutineContext elements and how they combine in Kotlin coroutines"
moc: moc-kotlin
related: [c-concurrency, q-coroutine-job-lifecycle--kotlin--medium]

date created: Saturday, November 1st 2025, 5:31:12 pm
date modified: Tuesday, November 25th 2025, 8:53:53 pm
---
# Вопрос (RU)

> Что такое элементы CoroutineContext и как они комбинируются? Объясните Job, CoroutineDispatcher, CoroutineName, CoroutineExceptionHandler и как работает оператор +.

# Question (EN)

> What are CoroutineContext elements and how do they combine? Explain Job, CoroutineDispatcher, CoroutineName, CoroutineExceptionHandler, and how the + operator works.

---

## Ответ (RU)

**CoroutineContext** — это постоянный индексированный набор элементов `Element`, которые предоставляют конфигурацию и поведение для корутин. Это фундаментальная концепция в Kotlin-корутинах, управляющая контекстом выполнения, иерархией задач, обработкой ошибок и отладкой.

### Основная Концепция

`CoroutineContext` работает как отображение, где:
- Ключи — это singleton-объекты `CoroutineContext.Key`
- Значения — это экземпляры `CoroutineContext.Element`
- Каждый элемент соответствует уникальному типу ключа
- Элементы комбинируются оператором `+`

```kotlin
interface CoroutineContext {
    operator fun <E : Element> get(key: Key<E>): E?
    operator fun plus(context: CoroutineContext): CoroutineContext
    fun minusKey(key: Key<*>) : CoroutineContext

    interface Element : CoroutineContext {
        val key: Key<*>
    }

    interface Key<E : Element>
}
```

---

### Четыре Стандартных Элемента

#### 1. Job — Жизненный Цикл И Отмена

Назначение: Управляет жизненным циклом корутины, отношениями родитель–потомок и отменой.

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    // Для каждой корутины создаётся свой Job; у runBlocking тоже есть Job
    val job = launch {
        println("Дочерний Job внутри: ${'$'}{coroutineContext[Job]}")
    }

    println("Job runBlocking: ${'$'}{coroutineContext[Job]}")
    println("Хэндл дочернего job: ${'$'}job")

    job.join()
}
```

Ключевые характеристики:
- У каждой корутины есть `Job` в контексте
- Дочерние корутины наследуют `Job` родителя как родителя своего собственного `Job`
- Отмена родительского `Job` отменяет всех потомков
- Родительский `Job` не считается завершённым, пока не завершены все его дочерние корутины

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val parentJob = launch {
        val child1 = launch {
            try {
                repeat(1000) { i ->
                    println("Потомок 1: ${'$'}i")
                    delay(100)
                }
            } finally {
                println("Потомок 1 отменён")
            }
        }

        val child2 = launch {
            try {
                repeat(1000) { i ->
                    println("Потомок 2: ${'$'}i")
                    delay(100)
                }
            } finally {
                println("Потомок 2 отменён")
            }
        }

        delay(500)
        println("Родитель отменяет себя")
        this.cancel()
    }

    parentJob.join()
    println("Все завершено")
}
// Отмена родителя останавливает обоих потомков
```

SupervisorJob: Изолирует сбои потомков (сбой одного не отменяет других).

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val supervisor = SupervisorJob()
    val scope = CoroutineScope(coroutineContext + supervisor)

    val child1 = scope.launch {
        delay(100)
        throw Exception("Потомок 1 упал")
    }

    val child2 = scope.launch {
        repeat(5) { i ->
            delay(200)
            println("Потомок 2: ${'$'}i")
        }
    }

    joinAll(child1, child2)
}
// Потомок 2 продолжает работу, даже когда Потомок 1 падает
```

---

#### 2. CoroutineDispatcher — Поток Выполнения

Назначение: Определяет, на каких потоках выполняется корутина.

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    // Dispatchers.Default — вычислительные задачи
    launch(Dispatchers.Default) {
        println("Default: ${'$'}{Thread.currentThread().name}")
    }

    // Dispatchers.IO — операции ввода-вывода
    launch(Dispatchers.IO) {
        println("IO: ${'$'}{Thread.currentThread().name}")
    }

    // Dispatchers.Main — UI-поток (Android/Desktop, требует зависимости)
    // launch(Dispatchers.Main) { /* UI обновления */ }

    // Dispatchers.Unconfined — начинает в текущем потоке, продолжает в потоке первого suspend
    launch(Dispatchers.Unconfined) {
        println("Unconfined до: ${'$'}{Thread.currentThread().name}")
        delay(100)
        println("Unconfined после: ${'$'}{Thread.currentThread().name}")
    }

    delay(500)
}
```

limitedParallelism (Kotlin 1.6+):

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val limitedIO = Dispatchers.IO.limitedParallelism(2)

    repeat(10) { i ->
        launch(limitedIO) {
            println("Задача ${'$'}i на ${'$'}{Thread.currentThread().name}")
            delay(1000)
        }
    }

    delay(2000)
}
// Только 2 задачи выполняются параллельно из 10 запущенных
```

---

#### 3. CoroutineName — Отладка

Назначение: Предоставляет осмысленные имена для отладки и логирования.

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    launch(CoroutineName("DataLoader")) {
        println("Выполняется: ${'$'}{coroutineContext[CoroutineName]}")
        launch(CoroutineName("DatabaseQuery")) {
            println("Выполняется: ${'$'}{coroutineContext[CoroutineName]}")
        }
    }

    delay(100)
}
// Пример вывода:
// Выполняется: CoroutineName(DataLoader)
// Выполняется: CoroutineName(DatabaseQuery)
```

---

#### 4. CoroutineExceptionHandler — Обработка Ошибок

Назначение: Обрабатывает неперехваченные исключения в корутинах (как правило, в корневых корутинах с `launch`, чьи исключения не наблюдаются через `join`).

```kotlin
import kotlinx.coroutines.*

val handler = CoroutineExceptionHandler { context, exception ->
    println("Перехвачено ${'$'}exception в ${'$'}{context[CoroutineName]}")
}

fun main() = runBlocking {
    val job = launch(handler + CoroutineName("ErrorProne")) {
        throw RuntimeException("Упс!")
    }

    job.join()
}
// Неперехваченное исключение передается в handler
```

Важные правила:

1. launch vs async:

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, e ->
        println("Перехвачено handler'ом: ${'$'}e")
    }

    launch(handler) {
        throw Exception("Исключение в launch")
    }

    val deferred = async(handler) {
        throw Exception("Исключение в async")
    }

    try {
        deferred.await()
    } catch (e: Exception) {
        println("Перехвачено из await: ${'$'}e")
    }
}
```

1. Handler должен находиться в контексте той корутины, чьи неперехваченные исключения вы хотите обрабатывать.

2. SupervisorJob влияет на распространение исключений: падение одного потомка не отменяет остальных, но неперехваченные исключения по-прежнему могут быть направлены в `CoroutineExceptionHandler`.

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, e ->
        println("Handler поймал: ${'$'}e")
    }

    val supervisor = SupervisorJob()
    val scope = CoroutineScope(coroutineContext + supervisor + handler)

    scope.launch {
        throw Exception("Потомок 1 упал")
    }

    scope.launch {
        delay(200)
        println("Потомок 2 продолжает работу")
    }

    delay(300)
}
```

---

### Как Комбинируются Элементы: Оператор +

Фундаментальное правило: при комбинировании контекстов элементы с одинаковым ключом справа замещают элементы слева ("правая сторона выигрывает").

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val context1 = Dispatchers.Default + CoroutineName("First")
    val context2 = Dispatchers.IO + CoroutineName("Second")

    val combined = context1 + context2

    println("Dispatcher: ${'$'}{combined[CoroutineDispatcher]}")
    println("Name: ${'$'}{combined[CoroutineName]}")
}
// Dispatcher: Dispatchers.IO
// Name: CoroutineName(Second)
```

Комбинирование нескольких элементов (полный исполняемый пример):

```kotlin
import kotlinx.coroutines.*

val handlerCombined = CoroutineExceptionHandler { _, e ->
    println("Ошибка: ${'$'}e")
}

val fullContext =
    Dispatchers.IO +
    CoroutineName("DataProcessor") +
    handlerCombined +
    Job()

fun main() = runBlocking {
    launch(fullContext) {
        println("Context has:")
        println("  Dispatcher: ${'$'}{coroutineContext[CoroutineDispatcher]}")
        println("  Name: ${'$'}{coroutineContext[CoroutineName]}")
        println("  Job: ${'$'}{coroutineContext[Job]}")
        println("  Handler: ${'$'}{coroutineContext[CoroutineExceptionHandler]}")
    }

    delay(100)
}
```

Порядок имеет значение:

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val context1 = Dispatchers.Default + Dispatchers.IO
    println(context1[CoroutineDispatcher]) // Dispatchers.IO

    val context2 =
        CoroutineName("First") +
        CoroutineName("Second") +
        CoroutineName("Third")
    println(context2[CoroutineName]) // CoroutineName(Third)
}
```

---

### Наследование Контекста

Дочерние корутины наследуют родительский контекст:

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    launch(Dispatchers.Default + CoroutineName("Parent")) {
        println("Parent:")
        println("  Thread: ${'$'}{Thread.currentThread().name}")
        println("  Name: ${'$'}{coroutineContext[CoroutineName]}")

        launch {
            println("Child (inherited):")
            println("  Thread: ${'$'}{Thread.currentThread().name}")
            println("  Name: ${'$'}{coroutineContext[CoroutineName]}")
        }

        launch(Dispatchers.IO + CoroutineName("Child")) {
            println("Child (overridden):")
            println("  Thread: ${'$'}{Thread.currentThread().name}")
            println("  Name: ${'$'}{coroutineContext[CoroutineName]}")
        }

        delay(100)
    }

    delay(200)
}
```

Наследование Job:

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val parentJob = coroutineContext[Job]!!

    launch {
        val childJob = coroutineContext[Job]!!
        println("Same job? ${'$'}{childJob == parentJob}") // false
        println("Parent? ${'$'}{childJob.parent == parentJob}") // true
    }

    delay(100)
}
// Для каждой дочерней корутины создаётся новый Job с родителем parentJob
```

---

### Практические Паттерны

Паттерн 1: Репозиторий с контекстом

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

data class User(val id: String, val name: String)

class UserRepository(
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) {
    private val repositoryContext =
        dispatcher +
        CoroutineName("UserRepository") +
        SupervisorJob()

    private val scope = CoroutineScope(repositoryContext)

    suspend fun fetchUser(id: String): User = withContext(dispatcher) {
        delay(1000)
        User(id, "User ${'$'}id")
    }

    fun observeUser(id: String): Flow<User> = flow {
        while (currentCoroutineContext().isActive) {
            emit(fetchUser(id))
            delay(5000)
        }
    }.flowOn(dispatcher)

    fun cleanup() {
        scope.cancel()
    }
}
```

Паттерн 2: Настраиваемый обработчик/воркер

```kotlin
import kotlinx.coroutines.*

class DataProcessor(
    dispatcher: CoroutineDispatcher = Dispatchers.Default,
    name: String = "DataProcessor"
) {
    private val handler = CoroutineExceptionHandler { _, e ->
        println("[${'$'}name] Error: ${'$'}e")
    }

    private val context =
        dispatcher +
        CoroutineName(name) +
        handler +
        SupervisorJob()

    private val scope = CoroutineScope(context)

    fun processData(data: List<Int>) = scope.launch {
        println("Processing on ${'$'}{Thread.currentThread().name}")

        data.chunked(10).forEach { chunk ->
            launch {
                chunk.forEach { item ->
                    if (item < 0) throw IllegalArgumentException("Negative: ${'$'}item")
                    println("Processed: ${'$'}item")
                }
            }
        }
    }
}

fun main() = runBlocking {
    val processor = DataProcessor(
        dispatcher = Dispatchers.Default.limitedParallelism(2),
        name = "NumberProcessor"
    )

    processor.processData(List(100) { it })
    delay(1000)
}
```

Паттерн 3: Тестирование с TestDispatcher

```kotlin
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*
import kotlin.test.*

@OptIn(ExperimentalCoroutinesApi::class)
class RepositoryTest {
    @Test
    fun testDataFetch() = runTest {
        val testDispatcher = StandardTestDispatcher(testScheduler)
        val repo = UserRepository(testDispatcher)

        val user = repo.fetchUser("123")
        assertEquals("User 123", user.name)
    }
}
```

---

### Правила Распространения Контекста

Правило 1: Явный контекст переопределяет унаследованный

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking(Dispatchers.Default + CoroutineName("Parent")) {
    launch {
        println("Inherited: ${'$'}{Thread.currentThread().name}")
    }

    launch(Dispatchers.IO) {
        println("Overridden: ${'$'}{Thread.currentThread().name}")
    }

    delay(100)
}
```

Правило 2: Job для потомка всегда новый

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val parentJob = coroutineContext[Job]!!

    launch {
        val childJob = coroutineContext[Job]!!
        println("Same job? ${'$'}{childJob == parentJob}") // false
        println("Parent? ${'$'}{childJob.parent == parentJob}") // true
    }

    delay(100)
}
```

Правило 3: `withContext` временно переопределяет контекст

```kotlin
import kotlinx.coroutines.*

suspend fun fetchData() = withContext(Dispatchers.IO) {
    println("Fetching on: ${'$'}{Thread.currentThread().name}")
    delay(1000)
    "Data"
}

fun main() = runBlocking(Dispatchers.Default) {
    println("Main on: ${'$'}{Thread.currentThread().name}")
    val data = fetchData()
    println("Back to: ${'$'}{Thread.currentThread().name}")
}
```

---

### Расширенные: Пользовательские Элементы Контекста

```kotlin
import kotlinx.coroutines.*
import kotlin.coroutines.*

data class RequestId(val id: String) : AbstractCoroutineContextElement(RequestId) {
    companion object Key : CoroutineContext.Key<RequestId>

    override fun toString(): String = "RequestId(${ '$'}id)"
}

val CoroutineContext.requestId: String?
    get() = this[RequestId]?.id

suspend fun processRequest() {
    val reqId = currentCoroutineContext().requestId
    println("Processing request: ${'$'}reqId")

    withContext(Dispatchers.IO) {
        println("On IO, request: ${'$'}{coroutineContext.requestId}")
    }
}

fun main() = runBlocking {
    launch(RequestId("REQ-123")) {
        processRequest()
    }

    launch(RequestId("REQ-456")) {
        processRequest()
    }

    delay(100)
}
```

---

### Распространенные Анти-паттерны

Анти-паттерн 1: Игнорирование диспетчера

```kotlin
import kotlinx.coroutines.*
import java.io.File

suspend fun loadUserBad() = withContext(Dispatchers.Default) {
    File("user.json").readText()
}

suspend fun loadUserGood() = withContext(Dispatchers.IO) {
    File("user.json").readText()
}
```

Анти-паттерн 2: GlobalScope

```kotlin
import kotlinx.coroutines.*

fun fetchDataBad() {
    GlobalScope.launch {
        // Не привязано к жизненному циклу компонента
    }
}

class Repository(private val scope: CoroutineScope) {
    fun fetchData() = scope.launch {
        // Управляемый жизненный цикл
    }
}
```

Анти-паттерн 3: Неверное ожидание поведения ExceptionHandler

```kotlin
import kotlinx.coroutines.*

fun badExample(scope: CoroutineScope) {
    scope.launch {
        val handler = CoroutineExceptionHandler { _, e ->
            println("Не будет вызван для ошибок родителя: ${'$'}e")
        }

        launch(handler) {
            throw Exception("Этот обработается только здесь")
        }
    }
}

fun goodExample(scope: CoroutineScope) {
    val handler = CoroutineExceptionHandler { _, e ->
        println("Перехвачено: ${'$'}e")
    }

    scope.launch(handler) {
        throw Exception("Корректно перехвачено")
    }
}
```

---

### Соображения Производительности

1. Накладные расходы переключения контекста

```kotlin
import kotlinx.coroutines.*

suspend fun processItemsBad(items: List<Int>) {
    items.forEach { item ->
        withContext(Dispatchers.IO) {
            processItem(item)
        }
    }
}

suspend fun processItemsBetter(items: List<Int>) = withContext(Dispatchers.IO) {
    items.forEach { item ->
        processItem(item)
    }
}

suspend fun processItem(i: Int) { /* ... */ }
```

1. Размер пулов диспетчеров

```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.Executors

val hugeDispatcher = Executors.newFixedThreadPool(1000).asCoroutineDispatcher()
val cpuDispatcher = Dispatchers.Default
val ioDispatcher = Dispatchers.IO
```

1. Выделение элементов контекста

```kotlin
import kotlinx.coroutines.*

fun processMany() = runBlocking {
    repeat(1000) {
        launch(CoroutineName("Worker-${'$'}it")) {
            delay(10)
        }
    }
}

fun processManyReused() = runBlocking {
    val baseName = CoroutineName("Worker")
    repeat(1000) {
        launch(baseName) {
            delay(10)
        }
    }
}
```

---

### Стратегии Тестирования

Стратегия 1: Инъекция диспетчеров

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class DataService(
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO,
    private val defaultDispatcher: CoroutineDispatcher = Dispatchers.Default
) {
    suspend fun processData(): String = withContext(ioDispatcher) {
        val raw = "raw"
        withContext(defaultDispatcher) {
            raw.uppercase()
        }
    }
}

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun testProcessData() = runTest {
    val testDispatcher = StandardTestDispatcher(testScheduler)
    val service = DataService(
        ioDispatcher = testDispatcher,
        defaultDispatcher = testDispatcher
    )

    val result = service.processData()
    assertEquals("RAW", result)
}
```

Стратегия 2: Тестирование распространения контекста

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun testContextPropagation() = runTest {
    val customElement = RequestId("TEST-123")

    launch(customElement) {
        assertEquals("TEST-123", coroutineContext.requestId)

        withContext(Dispatchers.IO) {
            assertEquals("TEST-123", coroutineContext.requestId)
        }
    }
}
```

Стратегия 3: Тестирование обработки исключений

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun testExceptionHandlerUsage() = runTest {
    var caught: Throwable? = null

    val handler = CoroutineExceptionHandler { _, e ->
        caught = e
    }

    val scope = CoroutineScope(SupervisorJob() + handler)

    scope.launch {
        throw IllegalStateException("boom")
    }

    advanceUntilIdle()

    assertTrue(caught is IllegalStateException)
    scope.cancel()
}
```

---

## Answer (EN)

CoroutineContext is a persistent indexed set of Element instances that provide configuration and behavior for coroutines. It controls execution context, job hierarchy, error handling, and debugging.

### Core Concept

CoroutineContext is like a map where:
- Keys are singleton CoroutineContext.Key objects
- Values are CoroutineContext.Element instances
- Each element has a unique key type
- Elements combine using the + operator

```kotlin
interface CoroutineContext {
    operator fun <E : Element> get(key: Key<E>): E?
    operator fun plus(context: CoroutineContext): CoroutineContext
    fun minusKey(key: Key<*>) : CoroutineContext

    interface Element : CoroutineContext {
        val key: Key<*>
    }

    interface Key<E : Element>
}
```

---

### The Four Standard Elements

#### 1. Job - Lifecycle and Cancellation

Purpose: Manages coroutine lifecycle, parent-child relationships, and cancellation.

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val job = launch {
        println("Child Job from inside: ${'$'}{coroutineContext[Job]}")
    }

    println("Parent job in runBlocking: ${'$'}{coroutineContext[Job]}")
    println("Child job handle: ${'$'}job")

    job.join()
}
```

Key Characteristics:
- Every coroutine has a Job in its context
- Child coroutines inherit their parent Job as parent of their own Job
- Cancelling a parent cancels all its children
- A parent Job is not complete until all its children complete

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val parentJob = launch {
        val child1 = launch {
            try {
                repeat(1000) { i ->
                    println("Child 1: ${'$'}i")
                    delay(100)
                }
            } finally {
                println("Child 1 cancelled")
            }
        }

        val child2 = launch {
            try {
                repeat(1000) { i ->
                    println("Child 2: ${'$'}i")
                    delay(100)
                }
            } finally {
                println("Child 2 cancelled")
            }
        }

        delay(500)
        println("Parent cancelling itself")
        this.cancel()
    }

    parentJob.join()
    println("All done")
}
// Parent cancellation stops both children
```

SupervisorJob: Isolates child failures.

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val supervisor = SupervisorJob()
    val scope = CoroutineScope(coroutineContext + supervisor)

    val child1 = scope.launch {
        delay(100)
        throw Exception("Child 1 failed")
    }

    val child2 = scope.launch {
        repeat(5) { i ->
            delay(200)
            println("Child 2: ${'$'}i")
        }
    }

    joinAll(child1, child2)
}
// Child 2 continues even when Child 1 fails
```

---

#### 2. CoroutineDispatcher - Execution Thread

Purpose: Determines which thread(s) the coroutine uses for execution.

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    launch(Dispatchers.Default) {
        println("Default: ${'$'}{Thread.currentThread().name}")
    }

    launch(Dispatchers.IO) {
        println("IO: ${'$'}{Thread.currentThread().name}")
    }

    // launch(Dispatchers.Main) { /* UI updates */ }

    launch(Dispatchers.Unconfined) {
        println("Unconfined before: ${'$'}{Thread.currentThread().name}")
        delay(100)
        println("Unconfined after: ${'$'}{Thread.currentThread().name}")
    }

    delay(500)
}
```

limitedParallelism:

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val limitedIO = Dispatchers.IO.limitedParallelism(2)

    repeat(10) { i ->
        launch(limitedIO) {
            println("Task ${'$'}i on ${'$'}{Thread.currentThread().name}")
            delay(1000)
        }
    }

    delay(2000)
}
```

---

#### 3. CoroutineName - Debugging

Purpose: Provides meaningful names for debugging and logging.

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    launch(CoroutineName("DataLoader")) {
        println("Running: ${'$'}{coroutineContext[CoroutineName]}")
        launch(CoroutineName("DatabaseQuery")) {
            println("Running: ${'$'}{coroutineContext[CoroutineName]}")
        }
    }

    delay(100)
}
```

---

#### 4. CoroutineExceptionHandler - Error Handling

Purpose: Handles uncaught exceptions in coroutines.

```kotlin
import kotlinx.coroutines.*

val handlerEn = CoroutineExceptionHandler { context, exception ->
    println("Caught ${'$'}exception in ${'$'}{context[CoroutineName]}")
}

fun main() = runBlocking {
    val job = launch(handlerEn + CoroutineName("ErrorProne")) {
        throw RuntimeException("Oops!")
    }

    job.join()
}
```

Rules:

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, e ->
        println("Caught by handler: ${'$'}e")
    }

    launch(handler) {
        throw Exception("Launch exception")
    }

    val deferred = async(handler) {
        throw Exception("Async exception")
    }

    try {
        deferred.await()
    } catch (e: Exception) {
        println("Caught from await: ${'$'}e")
    }
}
```

SupervisorJob with handler:

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, e ->
        println("Caught by handler: ${'$'}e")
    }

    val supervisor = SupervisorJob()
    val scope = CoroutineScope(coroutineContext + supervisor + handler)

    scope.launch {
        throw Exception("Child 1 failed")
    }

    scope.launch {
        delay(200)
        println("Child 2 still running")
    }

    delay(300)
}
```

---

### How Elements Combine: The + Operator

Fundamental rule: Right side wins for the same key.

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val context1 = Dispatchers.Default + CoroutineName("First")
    val context2 = Dispatchers.IO + CoroutineName("Second")

    val combined = context1 + context2

    println("Dispatcher: ${'$'}{combined[CoroutineDispatcher]}")
    println("Name: ${'$'}{combined[CoroutineName]}")
}
```

Combining multiple elements:

```kotlin
import kotlinx.coroutines.*

val handlerFull = CoroutineExceptionHandler { _, e ->
    println("Error: ${'$'}e")
}

val fullContext =
    Dispatchers.IO +
    CoroutineName("DataProcessor") +
    handlerFull +
    Job()

fun main() = runBlocking {
    launch(fullContext) {
        println("Context has:")
        println("  Dispatcher: ${'$'}{coroutineContext[CoroutineDispatcher]}")
        println("  Name: ${'$'}{coroutineContext[CoroutineName]}")
        println("  Job: ${'$'}{coroutineContext[Job]}")
        println("  Handler: ${'$'}{coroutineContext[CoroutineExceptionHandler]}")
    }

    delay(100)
}
```

Order matters:

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val context1 = Dispatchers.Default + Dispatchers.IO
    println(context1[CoroutineDispatcher])

    val context2 =
        CoroutineName("First") +
        CoroutineName("Second") +
        CoroutineName("Third")
    println(context2[CoroutineName])
}
```

---

### Context Inheritance

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    launch(Dispatchers.Default + CoroutineName("Parent")) {
        println("Parent:")
        println("  Thread: ${'$'}{Thread.currentThread().name}")
        println("  Name: ${'$'}{coroutineContext[CoroutineName]}")

        launch {
            println("Child (inherited):")
            println("  Thread: ${'$'}{Thread.currentThread().name}")
            println("  Name: ${'$'}{coroutineContext[CoroutineName]}")
        }

        launch(Dispatchers.IO + CoroutineName("Child")) {
            println("Child (overridden):")
            println("  Thread: ${'$'}{Thread.currentThread().name}")
            println("  Name: ${'$'}{coroutineContext[CoroutineName]}")
        }

        delay(100)
    }

    delay(200)
}
```

Job inheritance:

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val parentJob = coroutineContext[Job]!!

    launch {
        val childJob = coroutineContext[Job]!!
        println("Same job? ${'$'}{childJob == parentJob}")
        println("Parent? ${'$'}{childJob.parent == parentJob}")
    }

    delay(100)
}
```

---

### Practical Patterns

Pattern 1: Repository with context

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

data class User(val id: String, val name: String)

class UserRepository(
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) {
    private val repositoryContext =
        dispatcher +
        CoroutineName("UserRepository") +
        SupervisorJob()

    private val scope = CoroutineScope(repositoryContext)

    suspend fun fetchUser(id: String): User = withContext(dispatcher) {
        delay(1000)
        User(id, "User ${'$'}id")
    }

    fun observeUser(id: String): Flow<User> = flow {
        while (currentCoroutineContext().isActive) {
            emit(fetchUser(id))
            delay(5000)
        }
    }.flowOn(dispatcher)

    fun cleanup() {
        scope.cancel()
    }
}
```

Pattern 2: Configurable Worker

```kotlin
import kotlinx.coroutines.*

class DataProcessor(
    dispatcher: CoroutineDispatcher = Dispatchers.Default,
    name: String = "DataProcessor"
) {
    private val handler = CoroutineExceptionHandler { _, e ->
        println("[${'$'}name] Error: ${'$'}e")
    }

    private val context =
        dispatcher +
        CoroutineName(name) +
        handler +
        SupervisorJob()

    private val scope = CoroutineScope(context)

    fun processData(data: List<Int>) = scope.launch {
        println("Processing on ${'$'}{Thread.currentThread().name}")

        data.chunked(10).forEach { chunk ->
            launch {
                chunk.forEach { item ->
                    if (item < 0) throw IllegalArgumentException("Negative: ${'$'}item")
                    println("Processed: ${'$'}item")
                }
            }
        }
    }
}

fun main() = runBlocking {
    val processor = DataProcessor(
        dispatcher = Dispatchers.Default.limitedParallelism(2),
        name = "NumberProcessor"
    )

    processor.processData(List(100) { it })
    delay(1000)
}
```

Pattern 3: Testing with TestDispatcher

```kotlin
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*
import kotlin.test.*

@OptIn(ExperimentalCoroutinesApi::class)
class RepositoryTest {
    @Test
    fun testDataFetch() = runTest {
        val testDispatcher = StandardTestDispatcher(testScheduler)
        val repo = UserRepository(testDispatcher)

        val user = repo.fetchUser("123")
        assertEquals("User 123", user.name)
    }
}
```

---

### Context Propagation Rules

Rule 1: Explicit context overrides inherited

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking(Dispatchers.Default + CoroutineName("Parent")) {
    launch {
        println("Inherited: ${'$'}{Thread.currentThread().name}")
    }

    launch(Dispatchers.IO) {
        println("Overridden: ${'$'}{Thread.currentThread().name}")
    }

    delay(100)
}
```

Rule 2: Job is always new for child coroutines

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val parentJob = coroutineContext[Job]!!

    launch {
        val childJob = coroutineContext[Job]!!
        println("Same job? ${'$'}{childJob == parentJob}")
        println("Parent? ${'$'}{childJob.parent == parentJob}")
    }

    delay(100)
}
```

Rule 3: withContext temporarily overrides

```kotlin
import kotlinx.coroutines.*

suspend fun fetchData() = withContext(Dispatchers.IO) {
    println("Fetching on: ${'$'}{Thread.currentThread().name}")
    delay(1000)
    "Data"
}

fun main() = runBlocking(Dispatchers.Default) {
    println("Main on: ${'$'}{Thread.currentThread().name}")
    val data = fetchData()
    println("Back to: ${'$'}{Thread.currentThread().name}")
}
```

---

### Advanced: Custom Context Elements

```kotlin
import kotlinx.coroutines.*
import kotlin.coroutines.*

data class RequestId(val id: String) : AbstractCoroutineContextElement(RequestId) {
    companion object Key : CoroutineContext.Key<RequestId>

    override fun toString(): String = "RequestId(${ '$'}id)"
}

val CoroutineContext.requestId: String?
    get() = this[RequestId]?.id

suspend fun processRequest() {
    val reqId = currentCoroutineContext().requestId
    println("Processing request: ${'$'}reqId")

    withContext(Dispatchers.IO) {
        println("On IO, request: ${'$'}{coroutineContext.requestId}")
    }
}

fun main() = runBlocking {
    launch(RequestId("REQ-123")) {
        processRequest()
    }

    launch(RequestId("REQ-456")) {
        processRequest()
    }

    delay(100)
}
```

---

### Common Anti-Patterns

Anti-Pattern 1: Ignoring Dispatcher

```kotlin
import kotlinx.coroutines.*
import java.io.File

suspend fun loadUserBad() = withContext(Dispatchers.Default) {
    File("user.json").readText()
}

suspend fun loadUserGood() = withContext(Dispatchers.IO) {
    File("user.json").readText()
}
```

Anti-Pattern 2: GlobalScope

```kotlin
import kotlinx.coroutines.*

fun fetchDataBad() {
    GlobalScope.launch {
        // This coroutine is not tied to any component lifecycle
    }
}

class Repository(private val scope: CoroutineScope) {
    fun fetchData() = scope.launch {
        // Properly managed lifecycle
    }
}
```

Anti-Pattern 3: Misplaced Exception Handler

```kotlin
import kotlinx.coroutines.*

fun badExample(scope: CoroutineScope) {
    scope.launch {
        val handler = CoroutineExceptionHandler { _, e ->
            println("Won't be called for parent's failure: ${'$'}e")
        }

        launch(handler) {
            throw Exception("Handled only here")
        }
    }
}

fun goodExample(scope: CoroutineScope) {
    val handler = CoroutineExceptionHandler { _, e ->
        println("Caught: ${'$'}e")
    }

    scope.launch(handler) {
        throw Exception("Caught correctly")
    }
}
```

---

### Performance Considerations

1. `Context` switching overhead

```kotlin
import kotlinx.coroutines.*

suspend fun processItemsBad(items: List<Int>) {
    items.forEach { item ->
        withContext(Dispatchers.IO) {
            processItem(item)
        }
    }
}

suspend fun processItemsBetter(items: List<Int>) = withContext(Dispatchers.IO) {
    items.forEach { item ->
        processItem(item)
    }
}

suspend fun processItem(i: Int) { /* ... */ }
```

1. Dispatcher pool sizing

```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.Executors

val hugeDispatcher = Executors.newFixedThreadPool(1000).asCoroutineDispatcher()
val cpuDispatcher = Dispatchers.Default
val ioDispatcher = Dispatchers.IO
```

1. `Context` element allocation

```kotlin
import kotlinx.coroutines.*

fun processMany() = runBlocking {
    repeat(1000) {
        launch(CoroutineName("Worker-${'$'}it")) {
            delay(10)
        }
    }
}

fun processManyReused() = runBlocking {
    val baseName = CoroutineName("Worker")
    repeat(1000) {
        launch(baseName) {
            delay(10)
        }
    }
}
```

---

### Testing Strategies

Strategy 1: Inject Dispatchers

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class DataService(
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO,
    private val defaultDispatcher: CoroutineDispatcher = Dispatchers.Default
) {
    suspend fun processData(): String = withContext(ioDispatcher) {
        val raw = "raw"
        withContext(defaultDispatcher) {
            raw.uppercase()
        }
    }
}

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun testProcessData() = runTest {
    val testDispatcher = StandardTestDispatcher(testScheduler)
    val service = DataService(
        ioDispatcher = testDispatcher,
        defaultDispatcher = testDispatcher
    )

    val result = service.processData()
    assertEquals("RAW", result)
}
```

Strategy 2: Test `Context` Propagation

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun testContextPropagation() = runTest {
    val customElement = RequestId("TEST-123")

    launch(customElement) {
        assertEquals("TEST-123", coroutineContext.requestId)

        withContext(Dispatchers.IO) {
            assertEquals("TEST-123", coroutineContext.requestId)
        }
    }
}
```

Strategy 3: Test Exception Handling

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

@OptIn(ExperimentalCoroutinesApi::class)
@Test
fun testExceptionHandlerUsage() = runTest {
    var caught: Throwable? = null

    val handler = CoroutineExceptionHandler { _, e ->
        caught = e
    }

    val scope = CoroutineScope(SupervisorJob() + handler)

    scope.launch {
        throw IllegalStateException("boom")
    }

    advanceUntilIdle()

    assertTrue(caught is IllegalStateException)
    scope.cancel()
}
```

---

## Дополнительные Вопросы (RU)

1. Как работает `CoroutineContext.Element.Key` и как он обеспечивает типобезопасность?
2. Что произойдёт при комбинировании двух `Job` оператором `+`?
3. Как `ThreadLocal`-значения интегрируются с `CoroutineContext` (через `ThreadContextElement`)?
4. В чём разница по производительности между `Dispatchers.Default` и `Dispatchers.IO`?
5. Как реализовать собственный `CoroutineContext.Element` для распределённого трейсинга?
6. Каковы гарантии потокобезопасности операций с `CoroutineContext`?
7. Как работает распространение контекста вместе с операторами `Flow`, такими как `flowOn()`?

## Follow-ups

1. How does `CoroutineContext.Element.Key` work internally to ensure type safety?
2. What happens when you combine two `Job`s using the `+` operator?
3. How do `ThreadLocal` values interact with `CoroutineContext` (e.g., `ThreadContextElement`)?
4. What is the performance difference between `Dispatchers.Default` and `Dispatchers.IO`?
5. How would you implement a custom `CoroutineContext.Element` for distributed tracing?
6. What are the thread safety guarantees of `CoroutineContext` operations?
7. How does context propagation work with `Flow` operators like `flowOn()`?

## Ссылки (RU)

- [[c-concurrency]]
- Официальная документация по корутинам Kotlin
- API `CoroutineContext` в kotlinx.coroutines
- Материалы по structured concurrency

## References

- https://kotlinlang.org/docs/coroutines-guide.html
- https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-context/
- https://medium.com/@elizarov/structured-concurrency-722d765aa952
- https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-dispatchers/
- https://kotlinlang.org/docs/exception-handling.html

## Связанные Вопросы (RU)

### База (проще)
- [[q-what-is-job-object--kotlin--medium]]
- [[q-coroutine-job-lifecycle--kotlin--medium]]
- Базовые концепции корутин

### На Том Же Уровне
- [[q-coroutine-context-explained--kotlin--medium]]
- [[q-structured-concurrency--kotlin--hard]]
- [[q-coroutine-supervisorjob-use-cases--kotlin--medium]]

### Продвинутое (сложнее)
- Advanced context propagation patterns

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-job-object--kotlin--medium]]
- [[q-coroutine-job-lifecycle--kotlin--medium]]
- Basic coroutine concepts

### Related (Same Level)
- [[q-coroutine-context-explained--kotlin--medium]]
- [[q-structured-concurrency--kotlin--hard]]
- [[q-coroutine-supervisorjob-use-cases--kotlin--medium]]

### Advanced (Harder)
- Advanced context propagation patterns
