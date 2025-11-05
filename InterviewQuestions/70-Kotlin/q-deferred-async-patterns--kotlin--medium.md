---
topic: kotlin
id: kotlin-063
title: "Deferred and async patterns deep dive / Deferred и async паттерны подробно"
aliases: [Deferred Async Patterns, Deferred и async паттерны]
subtopics: [async, coroutines]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-12
updated: 2025-10-31
category: "coroutines-advanced"
tags: ["async", "await", "concurrency", "deferred", "difficulty/medium", "parallel-execution", "performance"]
description: "Complete guide to Deferred<T>, async patterns, parallel execution, and advanced async/await usage in Kotlin coroutines"
moc: moc-kotlin
related: [q-kotlin-sealed-classes-purpose--programming-languages--medium, q-lifecyclescope-viewmodelscope--kotlin--medium, q-singleton-object-keyword--programming-languages--easy]
date created: Friday, October 31st 2025, 6:33:46 pm
date modified: Saturday, November 1st 2025, 5:43:26 pm
---
# Deferred and Async Patterns Deep Dive / Deferred И Async Паттерны Подробно

# Вопрос (RU)

> Что такое `Deferred<T>` в корутинах Kotlin? Чем он отличается от `Job`? Объясните билдер `async`, функцию `await()` и различные паттерны параллельного выполнения с реальными примерами.

---

# Question (EN)

> What is `Deferred<T>` in Kotlin coroutines? How does it differ from `Job`? Explain the `async` builder, `await()` function, and various patterns for parallel execution with real-world examples.

## Ответ (RU)

*(Краткое содержание основных пунктов из английской версии)*

#### Что Такое Deferred<T>?

`Deferred<T>` - это неблокирующее отменяемое будущее (future), представляющее обещание будущего значения результата типа `T`. Он расширяет интерфейс `Job` и добавляет возможность возвращать результат при завершении вычисления.

```kotlin
public interface Deferred<out T> : Job {
    public suspend fun await(): T
    public val isCompleted: Boolean
    public fun getCompleted(): T
    public fun getCompletionExceptionOrNull(): Throwable?
}
```

**Ключевые характеристики:**
- **Расширяет Job**: Наследует все свойства и функции Job
- **Возвращает значение**: В отличие от Job, Deferred может вернуть результат
- **Одно значение**: Возвращает ровно одно значение при завершении
- **Неблокирующий**: await() - приостанавливающая функция, не блокирует потоки
- **Отменяемый**: Можно отменить как любой Job

#### Сравнение Deferred И Job

```kotlin
import kotlinx.coroutines.*

fun demonstrateDeferredVsJob() = runBlocking {
    // Job - нет возвращаемого значения
    val job: Job = launch {
        delay(1000)
        println("Job завершён")
    }
    job.join() // Ждём завершения, но нет результата

    // Deferred - возвращает значение
    val deferred: Deferred<String> = async {
        delay(1000)
        "Результат Deferred"
    }
    val result: String = deferred.await() // Ждём и получаем результат
    println(result)
}
```

**Таблица сравнения:**

| Характеристика | Job | Deferred<T> |
|----------------|-----|-------------|
| Возвращаемое значение | Нет | Да (тип T) |
| Функция ожидания | join() | await() |
| Получение результата | Н/Д | await() или getCompleted() |
| Случай использования | Запустить и забыть | Вычислить и вернуть |
| Создаётся через | launch | async |
| Обработка исключений | Пробрасывается родителю | Хранится до await() |

#### Билдер Async

`async` - это билдер корутин, который запускает корутину и возвращает объект `Deferred`:

```kotlin
import kotlinx.coroutines.*

suspend fun fetchUserData(userId: Int): String {
    delay(100) // Имитация сетевого запроса
    return "Пользователь$userId"
}

suspend fun fetchUserOrders(userId: Int): List<String> {
    delay(150)
    return listOf("Заказ1", "Заказ2")
}

// Базовое использование async
suspend fun loadUserProfile(userId: Int): Pair<String, List<String>> = coroutineScope {
    // Запускаем обе операции одновременно
    val userDeferred = async { fetchUserData(userId) }
    val ordersDeferred = async { fetchUserOrders(userId) }

    // Ждём оба результата
    val user = userDeferred.await()
    val orders = ordersDeferred.await()

    user to orders
}

// Использование
fun main() = runBlocking {
    val (user, orders) = loadUserProfile(1)
    println("Пользователь: $user, Заказы: $orders")
}
```

#### Состояния Deferred

Deferred проходит через несколько состояний в течение жизненного цикла:

```kotlin
import kotlinx.coroutines.*

fun demonstrateDeferredStates() = runBlocking {
    // Состояние 1: New (только для ленивых корутин)
    val lazyDeferred = async(start = CoroutineStart.LAZY) {
        delay(100)
        "Результат"
    }
    println("Ленивый - Активен: ${lazyDeferred.isActive}, Завершён: ${lazyDeferred.isCompleted}")

    // Состояние 2: Active
    val activeDeferred = async {
        delay(100)
        "Результат"
    }
    println("Активный - Активен: ${activeDeferred.isActive}, Завершён: ${activeDeferred.isCompleted}")

    // Состояние 3: Completed (успех)
    activeDeferred.await()
    println("Завершён - Активен: ${activeDeferred.isActive}, Завершён: ${activeDeferred.isCompleted}")
}
```

#### Функция await() И Распространение Исключений

`await()` приостанавливает корутину до завершения Deferred и возвращает результат. Если Deferred завершается с ошибкой, `await()` выбрасывает исключение:

```kotlin
import kotlinx.coroutines.*

suspend fun demonstrateAwaitExceptions() = coroutineScope {
    // Успешный случай
    val successDeferred = async {
        delay(100)
        42
    }
    println("Результат: ${successDeferred.await()}")

    // Случай с исключением - await() выбрасывает исключение
    val failedDeferred = async {
        delay(100)
        throw IllegalArgumentException("Некорректные данные")
    }

    try {
        failedDeferred.await() // Здесь выбросится исключение
    } catch (e: IllegalArgumentException) {
        println("Поймано исключение: ${e.message}")
    }

    // Исключение сохраняется и выбрасывается при каждом вызове await()
    try {
        failedDeferred.await() // Можно await снова, то же исключение
    } catch (e: IllegalArgumentException) {
        println("Снова поймано то же исключение: ${e.message}")
    }
}
```

**Важное поведение:**
- Исключение **сохраняется** в Deferred до вызова await()
- await() **перевыбрасывает** сохранённое исключение
- Можно вызывать await() несколько раз - каждый раз то же исключение
- Если никогда не вызвать await(), исключение **теряется** (с обычным Job)
- С SupervisorJob исключения дочерних корутин не отменяют родителя

#### Объединение Нескольких Deferred С awaitAll()

```kotlin
import kotlinx.coroutines.*

data class ApiResponse(val id: Int, val data: String)

suspend fun fetchFromApi(id: Int): ApiResponse {
    delay(100)
    return ApiResponse(id, "Данные$id")
}

// Паттерн 1: awaitAll() на списке Deferred
suspend fun fetchAllApis(): List<ApiResponse> = coroutineScope {
    val deferreds = (1..5).map { id ->
        async { fetchFromApi(id) }
    }
    deferreds.awaitAll() // Приостанавливается до завершения всех
}

// Паттерн 2: Поведение fail-fast
suspend fun fetchAllApisFailFast() = coroutineScope {
    val deferreds = (1..5).map { id ->
        async {
            if (id == 3) throw IllegalStateException("API $id упал")
            fetchFromApi(id)
        }
    }

    try {
        deferreds.awaitAll() // Падает как только любой async упадёт
    } catch (e: Exception) {
        println("Один API упал: ${e.message}")
        // Все остальные корутины отменяются автоматически
    }
}
```

**Характеристики awaitAll():**
- Приостанавливается до завершения **всех** Deferred
- Возвращает результаты в **том же порядке** что и входные данные
- **Fail-fast**: отменяет все при первой ошибке
- Типобезопасный: `List<Deferred<T>>` → `List<T>`

#### Паттерны Параллельного Выполнения

```kotlin
import kotlinx.coroutines.*
import kotlin.system.measureTimeMillis

data class UserProfile(val name: String, val email: String)
data class UserSettings(val theme: String, val notifications: Boolean)
data class UserStats(val loginCount: Int, val lastLogin: Long)

suspend fun fetchProfile(userId: Int): UserProfile {
    delay(200)
    return UserProfile("Пользователь$userId", "user$userId@example.com")
}

suspend fun fetchSettings(userId: Int): UserSettings {
    delay(150)
    return UserSettings("dark", true)
}

suspend fun fetchStats(userId: Int): UserStats {
    delay(100)
    return UserStats(42, System.currentTimeMillis())
}

// Паттерн 1: Последовательный (медленный)
suspend fun loadUserDataSequential(userId: Int): Triple<UserProfile, UserSettings, UserStats> {
    val profile = fetchProfile(userId)    // 200ms
    val settings = fetchSettings(userId)   // 150ms
    val stats = fetchStats(userId)         // 100ms
    return Triple(profile, settings, stats) // Всего: 450ms
}

// Паттерн 2: Параллельный с async (быстрый)
suspend fun loadUserDataParallel(userId: Int): Triple<UserProfile, UserSettings, UserStats> = coroutineScope {
    val profileDeferred = async { fetchProfile(userId) }
    val settingsDeferred = async { fetchSettings(userId) }
    val statsDeferred = async { fetchStats(userId) }

    Triple(
        profileDeferred.await(),
        settingsDeferred.await(),
        statsDeferred.await()
    ) // Всего: 200ms (самая длинная операция)
}

fun main() = runBlocking {
    val sequential = measureTimeMillis {
        loadUserDataSequential(1)
    }
    println("Последовательно: ${sequential}ms")

    val parallel = measureTimeMillis {
        loadUserDataParallel(1)
    }
    println("Параллельно: ${parallel}ms")
}
```

#### Ленивый Async С CoroutineStart.LAZY

```kotlin
import kotlinx.coroutines.*

// Ленивый async - не запускается пока явно не запросят
suspend fun demonstrateLazyAsync() = coroutineScope {
    val lazyDeferred = async(start = CoroutineStart.LAZY) {
        println("Вычисление дорогого значения...")
        delay(1000)
        42
    }

    println("Deferred создан, но вычисление не началось")
    delay(500)
    println("Всё ещё не началось...")

    // Запускаем вычисление вызовом await() или start()
    println("Запускаем сейчас...")
    val result = lazyDeferred.await() // Запускает вычисление
    println("Результат: $result")
}
```

#### CompletableDeferred Для Ручного Завершения

```kotlin
import kotlinx.coroutines.*

// CompletableDeferred - вручную завершаемое будущее
class AsyncCache<K, V> {
    private val cache = mutableMapOf<K, CompletableDeferred<V>>()

    suspend fun get(key: K, loader: suspend () -> V): V {
        val deferred = cache.getOrPut(key) {
            CompletableDeferred<V>().also { deferred ->
                // Загружаем значение асинхронно
                CoroutineScope(Dispatchers.IO).launch {
                    try {
                        val value = loader()
                        deferred.complete(value) // Вручную завершаем
                    } catch (e: Exception) {
                        deferred.completeExceptionally(e)
                    }
                }
            }
        }
        return deferred.await()
    }
}
```

#### Реальный Пример: Параллельные API Вызовы

```kotlin
import kotlinx.coroutines.*
import kotlin.system.measureTimeMillis

data class User(val id: Int, val name: String)
data class Posts(val userId: Int, val posts: List<String>)
data class Comments(val userId: Int, val comments: List<String>)
data class Friends(val userId: Int, val friends: List<Int>)

suspend fun fetchUser(userId: Int): User {
    delay(200)
    return User(userId, "Пользователь$userId")
}

suspend fun fetchPosts(userId: Int): Posts {
    delay(300)
    return Posts(userId, listOf("Пост1", "Пост2"))
}

suspend fun fetchComments(userId: Int): Comments {
    delay(150)
    return Comments(userId, listOf("Комментарий1", "Комментарий2"))
}

suspend fun fetchFriends(userId: Int): Friends {
    delay(250)
    return Friends(userId, listOf(2, 3, 4))
}

data class CompleteProfile(
    val user: User,
    val posts: Posts,
    val comments: Comments,
    val friends: Friends
)

// Параллельная загрузка (быстро)
suspend fun loadProfileParallel(userId: Int): CompleteProfile = coroutineScope {
    val userDeferred = async { fetchUser(userId) }
    val postsDeferred = async { fetchPosts(userId) }
    val commentsDeferred = async { fetchComments(userId) }
    val friendsDeferred = async { fetchFriends(userId) }

    CompleteProfile(
        user = userDeferred.await(),
        posts = postsDeferred.await(),
        comments = commentsDeferred.await(),
        friends = friendsDeferred.await()
    )
}

fun main() = runBlocking {
    val parallelTime = measureTimeMillis {
        loadProfileParallel(1)
    }
    println("Параллельно: ${parallelTime}ms") // ~300ms
}
```

**Улучшение производительности**: в 3 раза быстрее с параллельным выполнением

#### Обработка Ошибок В async/await

```kotlin
import kotlinx.coroutines.*

// Паттерн 1: Try-catch вокруг await()
suspend fun errorHandlingPattern1() = coroutineScope {
    val deferred1 = async { "Успех" }
    val deferred2 = async<String> { throw Exception("Ошибка") }

    val result1 = deferred1.await() // OK

    val result2 = try {
        deferred2.await() // Здесь выбрасывается
    } catch (e: Exception) {
        "Запасной вариант"
    }

    println("Результаты: $result1, $result2")
}

// Паттерн 2: SupervisorJob для независимых ошибок
suspend fun errorHandlingPattern2() = coroutineScope {
    val supervisor = SupervisorJob()

    val deferred1 = async(supervisor) { "Успех" }
    val deferred2 = async(supervisor) { throw Exception("Ошибка") }
    val deferred3 = async(supervisor) { "Тоже успех" }

    val result1 = deferred1.await()
    val result2 = try {
        deferred2.await()
    } catch (e: Exception) {
        "Запасной вариант"
    }
    val result3 = deferred3.await()

    println("Результаты: $result1, $result2, $result3")
}
```

#### Когда Использовать Async Vs Launch

```kotlin
import kotlinx.coroutines.*

// Используйте async когда нужен результат
suspend fun useAsync(): String = coroutineScope {
    val result = async {
        delay(100)
        "Вычисленное значение"
    }.await()

    result
}

// Используйте launch когда результат не нужен
suspend fun useLaunch() = coroutineScope {
    launch {
        delay(100)
        println("Только побочный эффект")
    }
}
```

**Руководство по выбору:**

| Критерий | Использовать async | Использовать launch |
|----------|-------------------|---------------------|
| Нужен результат? | Да | Нет |
| Ждать завершения? | Да (await) | Опционально (join) |
| Тип возврата | Deferred<T> | Job |
| Обработка ошибок | Исключение в await() | Исключение родителю |
| Случай использования | Вычисление | Побочный эффект |

#### Тестирование Async Кода

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.assertEquals

class AsyncTests {
    @Test
    fun testParallelExecution() = runTest {
        val start = currentTime

        val results = listOf(
            async { delay(100); "A" },
            async { delay(200); "B" },
            async { delay(150); "C" }
        ).awaitAll()

        val duration = currentTime - start

        assertEquals(listOf("A", "B", "C"), results)
        assertEquals(200, duration) // Макс задержка, не сумма
    }
}
```

### Резюме

**Deferred<T>** - это Job, который возвращает результат. Используйте **async** для создания Deferred для параллельных вычислений, **await()** для получения результатов, и **awaitAll()** для нескольких Deferred. Ключевые паттерны:
- **Параллельное выполнение**: Запустить несколько async, ждать всех
- **Ленивый async**: Вычислять только если нужно
- **CompletableDeferred**: Ручное завершение
- **Обработка ошибок**: Try-catch вокруг await()
- **Выбирайте мудро**: async для результатов, launch для побочных эффектов

---

## Answer (EN)

#### What is Deferred<T>?

`Deferred<T>` is a non-blocking cancellable future that represents a promise of a future result value of type `T`. It extends `Job` interface and adds the ability to return a result when the computation completes.

```kotlin
public interface Deferred<out T> : Job {
    public suspend fun await(): T
    public val isCompleted: Boolean
    public fun getCompleted(): T
    public fun getCompletionExceptionOrNull(): Throwable?
}
```

**Key characteristics:**
- **Extends Job**: Inherits all Job properties and functions
- **Returns a value**: Unlike Job, Deferred can return a result
- **Single value**: Returns exactly one value when computation completes
- **Non-blocking**: await() is a suspend function, doesn't block threads
- **Cancellable**: Can be cancelled like any Job

#### Deferred Vs Job Comparison

```kotlin
import kotlinx.coroutines.*

fun demonstrateDeferredVsJob() = runBlocking {
    // Job - no return value
    val job: Job = launch {
        delay(1000)
        println("Job completed")
    }
    job.join() // Wait for completion, but no result

    // Deferred - returns a value
    val deferred: Deferred<String> = async {
        delay(1000)
        "Deferred result"
    }
    val result: String = deferred.await() // Wait and get result
    println(result)
}
```

**Comparison Table:**

| Feature | Job | Deferred<T> |
|---------|-----|-------------|
| Return value | No | Yes (type T) |
| Waiting function | join() | await() |
| Result retrieval | N/A | await() or getCompleted() |
| Use case | Fire-and-forget | Compute and return |
| Created by | launch | async |
| Exception handling | Propagates to parent | Stored until await() |

#### The Async Builder

`async` is a coroutine builder that starts a coroutine and returns a `Deferred` object:

```kotlin
import kotlinx.coroutines.*

suspend fun fetchUserData(userId: Int): String {
    delay(100) // Simulate network call
    return "User$userId"
}

suspend fun fetchUserOrders(userId: Int): List<String> {
    delay(150)
    return listOf("Order1", "Order2")
}

// Basic async usage
suspend fun loadUserProfile(userId: Int): Pair<String, List<String>> = coroutineScope {
    // Start both operations concurrently
    val userDeferred = async { fetchUserData(userId) }
    val ordersDeferred = async { fetchUserOrders(userId) }

    // Wait for both results
    val user = userDeferred.await()
    val orders = ordersDeferred.await()

    user to orders
}

// Usage
fun main() = runBlocking {
    val (user, orders) = loadUserProfile(1)
    println("User: $user, Orders: $orders")
}
```

**async parameters:**
- `context`: Additional coroutine context
- `start`: Coroutine start option (DEFAULT, LAZY, ATOMIC, UNDISPATCHED)

#### Deferred States

Deferred progresses through several states during its lifecycle:

```kotlin
import kotlinx.coroutines.*

fun demonstrateDeferredStates() = runBlocking {
    // State 1: New (only for lazy coroutines)
    val lazyDeferred = async(start = CoroutineStart.LAZY) {
        delay(100)
        "Result"
    }
    println("Lazy - Active: ${lazyDeferred.isActive}, Completed: ${lazyDeferred.isCompleted}")

    // State 2: Active
    val activeDeferred = async {
        delay(100)
        "Result"
    }
    println("Active - Active: ${activeDeferred.isActive}, Completed: ${activeDeferred.isCompleted}")

    // State 3: Completed (success)
    activeDeferred.await()
    println("Completed - Active: ${activeDeferred.isActive}, Completed: ${activeDeferred.isCompleted}")

    // State 4: Completed (failure)
    val failedDeferred = async {
        throw IllegalStateException("Error")
    }
    delay(50) // Let it fail
    println("Failed - Active: ${failedDeferred.isActive}, Completed: ${failedDeferred.isCompleted}")
    println("Failed - Cancelled: ${failedDeferred.isCancelled}")
}
```

**State Transition Diagram:**

```
NEW (lazy only)
    ↓ start()
ACTIVE
    ↓
COMPLETING (body finished, waiting for children)
    ↓
COMPLETED (success) or CANCELLED (failure/cancellation)
```

#### await() Function and Exception Propagation

`await()` suspends the coroutine until the Deferred completes and returns the result. If the Deferred fails, `await()` throws the exception:

```kotlin
import kotlinx.coroutines.*

suspend fun demonstrateAwaitExceptions() = coroutineScope {
    // Success case
    val successDeferred = async {
        delay(100)
        42
    }
    println("Result: ${successDeferred.await()}")

    // Exception case - await() throws the exception
    val failedDeferred = async {
        delay(100)
        throw IllegalArgumentException("Invalid data")
    }

    try {
        failedDeferred.await() // This will throw
    } catch (e: IllegalArgumentException) {
        println("Caught exception: ${e.message}")
    }

    // Exception is stored and thrown on each await() call
    try {
        failedDeferred.await() // Can await again, same exception
    } catch (e: IllegalArgumentException) {
        println("Caught same exception again: ${e.message}")
    }
}
```

**Important behaviors:**
- Exception is **stored** in Deferred until await() is called
- await() **rethrows** the stored exception
- Can call await() multiple times - same exception each time
- If never awaited, exception is **lost** (with regular Job)
- With SupervisorJob, child exceptions don't cancel parent

#### Combining Multiple Deferreds with awaitAll()

```kotlin
import kotlinx.coroutines.*

data class ApiResponse(val id: Int, val data: String)

suspend fun fetchFromApi(id: Int): ApiResponse {
    delay(100)
    return ApiResponse(id, "Data$id")
}

// Pattern 1: awaitAll() on list of Deferreds
suspend fun fetchAllApis(): List<ApiResponse> = coroutineScope {
    val deferreds = (1..5).map { id ->
        async { fetchFromApi(id) }
    }
    deferreds.awaitAll() // Suspends until all complete
}

// Pattern 2: Fail-fast behavior
suspend fun fetchAllApisFailFast() = coroutineScope {
    val deferreds = (1..5).map { id ->
        async {
            if (id == 3) throw IllegalStateException("API $id failed")
            fetchFromApi(id)
        }
    }

    try {
        deferreds.awaitAll() // Fails as soon as any async fails
    } catch (e: Exception) {
        println("One API failed: ${e.message}")
        // All other coroutines are cancelled automatically
    }
}

// Pattern 3: Process results as they complete
suspend fun processAsCompleted() = coroutineScope {
    val deferreds = (1..5).map { id ->
        async {
            delay((100..500).random().toLong())
            ApiResponse(id, "Data$id")
        }
    }

    // Process each result as soon as it's available
    for (deferred in deferreds) {
        val result = deferred.await()
        println("Processed: $result")
    }
}
```

**awaitAll() characteristics:**
- Suspends until **all** Deferreds complete
- Returns results in **same order** as input
- **Fail-fast**: cancels all on first failure
- Type-safe: `List<Deferred<T>>` → `List<T>`

#### Parallel Execution Patterns

```kotlin
import kotlinx.coroutines.*
import kotlin.system.measureTimeMillis

data class UserProfile(val name: String, val email: String)
data class UserSettings(val theme: String, val notifications: Boolean)
data class UserStats(val loginCount: Int, val lastLogin: Long)

suspend fun fetchProfile(userId: Int): UserProfile {
    delay(200)
    return UserProfile("User$userId", "user$userId@example.com")
}

suspend fun fetchSettings(userId: Int): UserSettings {
    delay(150)
    return UserSettings("dark", true)
}

suspend fun fetchStats(userId: Int): UserStats {
    delay(100)
    return UserStats(42, System.currentTimeMillis())
}

// Pattern 1: Sequential (slow)
suspend fun loadUserDataSequential(userId: Int): Triple<UserProfile, UserSettings, UserStats> {
    val profile = fetchProfile(userId)    // 200ms
    val settings = fetchSettings(userId)   // 150ms
    val stats = fetchStats(userId)         // 100ms
    return Triple(profile, settings, stats) // Total: 450ms
}

// Pattern 2: Parallel with async (fast)
suspend fun loadUserDataParallel(userId: Int): Triple<UserProfile, UserSettings, UserStats> = coroutineScope {
    val profileDeferred = async { fetchProfile(userId) }
    val settingsDeferred = async { fetchSettings(userId) }
    val statsDeferred = async { fetchStats(userId) }

    Triple(
        profileDeferred.await(),
        settingsDeferred.await(),
        statsDeferred.await()
    ) // Total: 200ms (longest operation)
}

// Pattern 3: Parallel with awaitAll
suspend fun loadUserDataParallelAwaitAll(userId: Int): Triple<UserProfile, UserSettings, UserStats> = coroutineScope {
    val results = listOf(
        async { fetchProfile(userId) },
        async { fetchSettings(userId) },
        async { fetchStats(userId) }
    ).awaitAll()

    Triple(
        results[0] as UserProfile,
        results[1] as UserSettings,
        results[2] as UserStats
    )
}

// Performance comparison
fun main() = runBlocking {
    val sequential = measureTimeMillis {
        loadUserDataSequential(1)
    }
    println("Sequential: ${sequential}ms")

    val parallel = measureTimeMillis {
        loadUserDataParallel(1)
    }
    println("Parallel: ${parallel}ms")
}
```

#### Lazy Async with CoroutineStart.LAZY

```kotlin
import kotlinx.coroutines.*

// Lazy async - doesn't start until explicitly requested
suspend fun demonstrateLazyAsync() = coroutineScope {
    val lazyDeferred = async(start = CoroutineStart.LAZY) {
        println("Computing expensive value...")
        delay(1000)
        42
    }

    println("Deferred created, but computation hasn't started")
    delay(500)
    println("Still not started...")

    // Start computation by calling await() or start()
    println("Starting now...")
    val result = lazyDeferred.await() // Triggers computation
    println("Result: $result")
}

// Real-world example: conditional computation
data class Report(val data: String)

suspend fun generateExpensiveReport(userId: Int): Report {
    println("Generating expensive report...")
    delay(2000)
    return Report("Report data for user $userId")
}

suspend fun getUserDashboard(userId: Int, includeReport: Boolean) = coroutineScope {
    // Start report generation lazily
    val reportDeferred = async(start = CoroutineStart.LAZY) {
        generateExpensiveReport(userId)
    }

    val basicData = async {
        delay(100)
        "Basic dashboard data"
    }

    val basic = basicData.await()

    // Only generate report if needed
    val report = if (includeReport) {
        reportDeferred.await() // Start and wait
    } else {
        null // Never started
    }

    basic to report
}

fun main() = runBlocking {
    // Report not needed - computation never starts
    val (data1, report1) = getUserDashboard(1, includeReport = false)
    println("Dashboard without report: $data1")

    // Report needed - computation starts
    val (data2, report2) = getUserDashboard(2, includeReport = true)
    println("Dashboard with report: $data2, ${report2?.data}")
}
```

**CoroutineStart.LAZY benefits:**
- No computation until needed
- Can cancel before starting
- Useful for conditional/on-demand work
- Memory efficient

#### CompletableDeferred for Manual Completion

```kotlin
import kotlinx.coroutines.*

// CompletableDeferred - manually completed future
class AsyncCache<K, V> {
    private val cache = mutableMapOf<K, CompletableDeferred<V>>()

    suspend fun get(key: K, loader: suspend () -> V): V {
        val deferred = cache.getOrPut(key) {
            CompletableDeferred<V>().also { deferred ->
                // Load value asynchronously
                CoroutineScope(Dispatchers.IO).launch {
                    try {
                        val value = loader()
                        deferred.complete(value) // Manually complete
                    } catch (e: Exception) {
                        deferred.completeExceptionally(e)
                    }
                }
            }
        }
        return deferred.await()
    }
}

// Real-world example: Callback-based API to coroutines
class LegacyApiClient {
    fun fetchData(callback: (Result<String>) -> Unit) {
        // Simulate async callback API
        Thread {
            Thread.sleep(100)
            callback(Result.success("Data from legacy API"))
        }.start()
    }
}

suspend fun fetchDataAsync(client: LegacyApiClient): String {
    val deferred = CompletableDeferred<String>()

    client.fetchData { result ->
        result.onSuccess { data ->
            deferred.complete(data)
        }.onFailure { error ->
            deferred.completeExceptionally(error)
        }
    }

    return deferred.await()
}

// Example: Coordinating multiple callbacks
class MultiStepProcess {
    private val step1Complete = CompletableDeferred<Unit>()
    private val step2Complete = CompletableDeferred<Unit>()

    fun onStep1Complete() {
        step1Complete.complete(Unit)
    }

    fun onStep2Complete() {
        step2Complete.complete(Unit)
    }

    suspend fun waitForAllSteps() {
        step1Complete.await()
        step2Complete.await()
        println("All steps completed!")
    }
}

fun main() = runBlocking {
    val process = MultiStepProcess()

    launch {
        delay(100)
        process.onStep1Complete()
        delay(100)
        process.onStep2Complete()
    }

    process.waitForAllSteps()
}
```

**CompletableDeferred use cases:**
- Bridge callback APIs to coroutines
- Manual result injection (testing)
- Coordinating async events
- Custom async primitives

#### Real Example: Parallel API Calls

```kotlin
import kotlinx.coroutines.*
import kotlin.system.measureTimeMillis

// Simulated API endpoints
data class User(val id: Int, val name: String)
data class Posts(val userId: Int, val posts: List<String>)
data class Comments(val userId: Int, val comments: List<String>)
data class Friends(val userId: Int, val friends: List<Int>)

suspend fun fetchUser(userId: Int): User {
    delay(200)
    return User(userId, "User$userId")
}

suspend fun fetchPosts(userId: Int): Posts {
    delay(300)
    return Posts(userId, listOf("Post1", "Post2"))
}

suspend fun fetchComments(userId: Int): Comments {
    delay(150)
    return Comments(userId, listOf("Comment1", "Comment2"))
}

suspend fun fetchFriends(userId: Int): Friends {
    delay(250)
    return Friends(userId, listOf(2, 3, 4))
}

// Complete user profile
data class CompleteProfile(
    val user: User,
    val posts: Posts,
    val comments: Comments,
    val friends: Friends
)

// Sequential loading (slow)
suspend fun loadProfileSequential(userId: Int): CompleteProfile {
    val user = fetchUser(userId)
    val posts = fetchPosts(userId)
    val comments = fetchComments(userId)
    val friends = fetchFriends(userId)
    return CompleteProfile(user, posts, comments, friends)
}

// Parallel loading (fast)
suspend fun loadProfileParallel(userId: Int): CompleteProfile = coroutineScope {
    val userDeferred = async { fetchUser(userId) }
    val postsDeferred = async { fetchPosts(userId) }
    val commentsDeferred = async { fetchComments(userId) }
    val friendsDeferred = async { fetchFriends(userId) }

    CompleteProfile(
        user = userDeferred.await(),
        posts = postsDeferred.await(),
        comments = commentsDeferred.await(),
        friends = friendsDeferred.await()
    )
}

// Map + awaitAll pattern
suspend fun loadMultipleProfiles(userIds: List<Int>): List<CompleteProfile> = coroutineScope {
    userIds.map { userId ->
        async { loadProfileParallel(userId) }
    }.awaitAll()
}

fun main() = runBlocking {
    // Single profile comparison
    val sequentialTime = measureTimeMillis {
        loadProfileSequential(1)
    }
    println("Sequential: ${sequentialTime}ms") // ~900ms

    val parallelTime = measureTimeMillis {
        loadProfileParallel(1)
    }
    println("Parallel: ${parallelTime}ms") // ~300ms

    // Multiple profiles
    val multipleTime = measureTimeMillis {
        loadMultipleProfiles(listOf(1, 2, 3))
    }
    println("Multiple profiles parallel: ${multipleTime}ms") // ~300ms
}
```

**Performance improvement**: 3x faster with parallel execution

#### Performance: Parallel Vs Sequential

```kotlin
import kotlinx.coroutines.*
import kotlin.system.measureTimeMillis

suspend fun simulateApiCall(id: Int, delayMs: Long): String {
    delay(delayMs)
    return "Result$id"
}

// Benchmark different patterns
fun main() = runBlocking {
    val apiCount = 10
    val delayMs = 100L

    // Sequential
    val sequentialTime = measureTimeMillis {
        val results = mutableListOf<String>()
        for (i in 1..apiCount) {
            results.add(simulateApiCall(i, delayMs))
        }
    }
    println("Sequential ($apiCount calls): ${sequentialTime}ms") // ~1000ms

    // Parallel with async
    val parallelTime = measureTimeMillis {
        val results = (1..apiCount).map { i ->
            async { simulateApiCall(i, delayMs) }
        }.awaitAll()
    }
    println("Parallel ($apiCount calls): ${parallelTime}ms") // ~100ms

    // Speedup
    val speedup = sequentialTime.toDouble() / parallelTime.toDouble()
    println("Speedup: ${String.format("%.2f", speedup)}x")
}
```

**Benchmark results:**
```
Sequential (10 calls): 1005ms
Parallel (10 calls): 112ms
Speedup: 8.97x
```

#### Error Handling in async/await

```kotlin
import kotlinx.coroutines.*

// Pattern 1: Try-catch around await()
suspend fun errorHandlingPattern1() = coroutineScope {
    val deferred1 = async { "Success" }
    val deferred2 = async<String> { throw Exception("Failed") }

    val result1 = deferred1.await() // OK

    val result2 = try {
        deferred2.await() // Throws here
    } catch (e: Exception) {
        "Fallback"
    }

    println("Results: $result1, $result2")
}

// Pattern 2: SupervisorJob for independent failures
suspend fun errorHandlingPattern2() = coroutineScope {
    val supervisor = SupervisorJob()

    val deferred1 = async(supervisor) { "Success" }
    val deferred2 = async(supervisor) { throw Exception("Failed") }
    val deferred3 = async(supervisor) { "Also success" }

    val result1 = deferred1.await()
    val result2 = try {
        deferred2.await()
    } catch (e: Exception) {
        "Fallback"
    }
    val result3 = deferred3.await()

    println("Results: $result1, $result2, $result3")
}

// Pattern 3: Result wrapper
sealed class AsyncResult<out T> {
    data class Success<T>(val value: T) : AsyncResult<T>()
    data class Error(val exception: Exception) : AsyncResult<Nothing>()
}

suspend fun <T> Deferred<T>.awaitResult(): AsyncResult<T> = try {
    AsyncResult.Success(await())
} catch (e: Exception) {
    AsyncResult.Error(e)
}

suspend fun errorHandlingPattern3() = coroutineScope {
    val deferreds = listOf(
        async { "Success1" },
        async<String> { throw Exception("Failed") },
        async { "Success2" }
    )

    val results = deferreds.map { it.awaitResult() }

    results.forEach { result ->
        when (result) {
            is AsyncResult.Success -> println("Got: ${result.value}")
            is AsyncResult.Error -> println("Error: ${result.exception.message}")
        }
    }
}

// Pattern 4: Cancellation on first failure
suspend fun errorHandlingPattern4() = coroutineScope {
    try {
        val results = listOf(
            async { delay(100); "Success1" },
            async { delay(50); throw Exception("Failed"); "Success2" },
            async { delay(200); "Success3" }
        ).awaitAll() // Cancels all on first failure

        println(results)
    } catch (e: Exception) {
        println("One failed, all cancelled: ${e.message}")
    }
}

fun main() = runBlocking {
    println("Pattern 1:")
    errorHandlingPattern1()

    println("\nPattern 2:")
    errorHandlingPattern2()

    println("\nPattern 3:")
    errorHandlingPattern3()

    println("\nPattern 4:")
    errorHandlingPattern4()
}
```

#### When to Use Async Vs Launch

```kotlin
import kotlinx.coroutines.*

// Use async when you need the result
suspend fun useAsync(): String = coroutineScope {
    val result = async {
        delay(100)
        "Computed value"
    }.await()

    result
}

// Use launch when you don't need the result
suspend fun useLaunch() = coroutineScope {
    launch {
        delay(100)
        println("Side effect only")
    }
}

// Decision table example
class DataProcessor {
    // async: Computing and returning value
    suspend fun computeSum(numbers: List<Int>): Int = coroutineScope {
        async {
            delay(100) // Simulate heavy computation
            numbers.sum()
        }.await()
    }

    // launch: Side effect only
    suspend fun logEvent(event: String) = coroutineScope {
        launch {
            delay(50) // Simulate network call
            println("Event logged: $event")
        }
    }

    // async: Multiple results needed
    suspend fun fetchUserData(userId: Int): Pair<String, Int> = coroutineScope {
        val name = async { fetchUserName(userId) }
        val age = async { fetchUserAge(userId) }
        name.await() to age.await()
    }

    // launch: Multiple independent side effects
    suspend fun sendNotifications(userIds: List<Int>) = coroutineScope {
        userIds.forEach { userId ->
            launch {
                sendNotification(userId)
            }
        }
    }

    private suspend fun fetchUserName(userId: Int): String {
        delay(100)
        return "User$userId"
    }

    private suspend fun fetchUserAge(userId: Int): Int {
        delay(100)
        return 25
    }

    private suspend fun sendNotification(userId: Int) {
        delay(50)
        println("Notification sent to user $userId")
    }
}
```

**Decision Guide:**

| Criteria | Use async | Use launch |
|----------|-----------|------------|
| Need result? | Yes | No |
| Await completion? | Yes (await) | Optional (join) |
| Return type | Deferred<T> | Job |
| Error handling | Exception in await() | Exception to parent |
| Use case | Computation | Side effect |

#### Testing Async Code

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith

class AsyncTests {
    @Test
    fun testParallelExecution() = runTest {
        val start = currentTime

        val results = listOf(
            async { delay(100); "A" },
            async { delay(200); "B" },
            async { delay(150); "C" }
        ).awaitAll()

        val duration = currentTime - start

        assertEquals(listOf("A", "B", "C"), results)
        assertEquals(200, duration) // Max delay, not sum
    }

    @Test
    fun testErrorPropagation() = runTest {
        val deferred = async {
            delay(100)
            throw IllegalStateException("Test error")
        }

        advanceTimeBy(100)

        assertFailsWith<IllegalStateException> {
            deferred.await()
        }
    }

    @Test
    fun testLazyAsync() = runTest {
        var started = false

        val deferred = async(start = CoroutineStart.LAZY) {
            started = true
            delay(100)
            "Result"
        }

        assertEquals(false, started) // Not started yet

        deferred.start()
        assertEquals(true, started) // Now started

        advanceTimeBy(100)
        assertEquals("Result", deferred.await())
    }

    @Test
    fun testAwaitAll() = runTest {
        val results = (1..5).map { id ->
            async {
                delay(id * 10L)
                id * 2
            }
        }.awaitAll()

        assertEquals(listOf(2, 4, 6, 8, 10), results)
    }
}
```

### Common Pitfalls and Gotchas

1. **Not using coroutineScope**
```kotlin
// Bad - breaks structured concurrency
suspend fun loadDataBad(): String {
    val deferred = CoroutineScope(Dispatchers.IO).async {
        delay(1000)
        "Data"
    }
    return deferred.await() // Scope may leak
}

// Good - properly scoped
suspend fun loadDataGood(): String = coroutineScope {
    val deferred = async {
        delay(1000)
        "Data"
    }
    deferred.await()
}
```

2. **Ignoring exceptions in async**
```kotlin
// Bad - exception is lost if never awaited
suspend fun loadDataBad() = coroutineScope {
    async {
        throw Exception("Error")
    }
    // Exception never surfaces if we don't await()
}

// Good - always await or handle
suspend fun loadDataGood() = coroutineScope {
    val deferred = async {
        throw Exception("Error")
    }
    try {
        deferred.await()
    } catch (e: Exception) {
        // Handle error
    }
}
```

3. **Sequential awaits**
```kotlin
// Bad - sequential execution
suspend fun loadDataBad() = coroutineScope {
    val result1 = async { fetchData1() }.await() // Waits here
    val result2 = async { fetchData2() }.await() // Then waits here
    result1 to result2
}

// Good - parallel execution
suspend fun loadDataGood() = coroutineScope {
    val deferred1 = async { fetchData1() }
    val deferred2 = async { fetchData2() }
    deferred1.await() to deferred2.await()
}
```

### Summary

**Deferred<T>** is a Job that returns a result. Use **async** to create Deferreds for parallel computation, **await()** to retrieve results, and **awaitAll()** for multiple Deferreds. Key patterns:
- **Parallel execution**: Start multiple async, await all
- **Lazy async**: Compute only if needed
- **CompletableDeferred**: Manual completion
- **Error handling**: Try-catch around await()
- **Choose wisely**: async for results, launch for side effects

---

## Follow-ups

1. How does `Deferred` handle cancellation differently from regular `Job`? What happens to awaiting coroutines when a `Deferred` is cancelled?

2. Explain the performance implications of using `awaitAll()` vs individually awaiting multiple `Deferred` objects. When would you choose one over the other?

3. How can you implement a timeout for a group of async operations? Compare `withTimeout` wrapping `awaitAll()` vs individual timeouts for each async.

4. What are the thread-safety guarantees of `CompletableDeferred`? Can multiple threads safely call `complete()` concurrently?

5. How would you implement a rate-limited parallel execution pattern where only N async operations run concurrently?

6. Explain the difference between `Deferred.await()` and `Deferred.getCompleted()`. When would each throw an exception?

7. How can you convert a Flow into a Deferred? What are the semantics when the Flow emits multiple values?

## References

- [Kotlin Coroutines Guide - Composing Suspending Functions](https://kotlinlang.org/docs/composing-suspending-functions.html)
- [Deferred API Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-deferred/)
- [async Coroutine Builder](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/async.html)
- [Roman Elizarov - Structured Concurrency](https://medium.com/@elizarov/structured-concurrency-722d765aa952)
- [Kotlin Coroutines Performance Best Practices](https://github.com/Kotlin/kotlinx.coroutines/blob/master/docs/topics/performance.md)

## Related Questions

- [[q-job-state-machine-transitions--kotlin--medium]] - Understanding Job states that Deferred inherits
- [[q-structured-concurrency-violations--kotlin--hard]] - Proper scoping for async operations
- [[q-testing-coroutine-timing-control--kotlin--medium]] - Testing async/await patterns
- [[q-custom-dispatchers-limited-parallelism--kotlin--hard]] - Controlling where async executes
- [[q-coroutine-memory-leak-detection--kotlin--hard]] - Avoiding leaks with async

## Tags
#kotlin #coroutines #async #deferred #parallelism #concurrency #performance #structured-concurrency
