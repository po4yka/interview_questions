---id: lang-063
title: "How To Create Suspend Function / Как создать suspend функцию"
aliases: [How To Create Suspend Function, Как создать suspend функцию]
topic: kotlin
subtopics: [coroutines, functions, kotlin]
question_kind: coding
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, c-stateflow]
created: 2025-10-15
updated: 2025-11-09
tags: [coroutines, difficulty/medium, functions, kotlin]
---
# Вопрос (RU)
> Как создать suspend функцию?

---

# Question (EN)
> How to create a suspend function?

## Ответ (RU)

Создать suspend-функцию в Kotlin можно, добавив модификатор `suspend` перед `fun`. Тело такой функции может содержать вызовы других suspend-функций. Напрямую (обычным вызовом) вызвать suspend-функцию из несуспендящейся функции нельзя — нужно запустить корутину (через билдеры `launch`, `async`, `runBlocking` и т.п.) или, в редких случаях, использовать низкоуровневые continuation API (`Continuation`, `suspendCoroutine`, `suspendCancellableCoroutine`).

### Базовый Синтаксис

```kotlin
// Простая suspend-функция
suspend fun fetchData(): String {
    delay(1000)  // delay — это suspend-функция
    return "Data loaded"
}

// Suspend-функция с параметрами
suspend fun saveUser(userId: Int, name: String): Boolean {
    delay(500)
    // Сохранение в базу данных
    return true
}

// Suspend-функция, не возвращающая значение
suspend fun logEvent(event: String) {
    delay(100)
    println("Event logged: $event")
}
```

### Вызов Suspend-функций

```kotlin
// - НЕВЕРНО: нельзя вызвать напрямую из обычной функции
fun regularFunction() {
    val data = fetchData()  // Ошибка компиляции: suspend-функцию можно вызывать только из корутины или другой suspend-функции
}

// - ВЕРНО: вызов внутри корутины, запущенной runBlocking
fun main() = runBlocking {
    val data = fetchData()  // OK — внутри корутины
    println(data)
}

// - ВЕРНО: вызов из другой suspend-функции
suspend fun processData() {
    val data = fetchData()  // OK — suspend вызывает suspend
    println(data)
}

// - ВЕРНО: вызов внутри корутины launch/async
fun loadData() {
    CoroutineScope(Dispatchers.IO).launch {
        val data = fetchData()  // OK — внутри корутины
        println(data)
    }
}
```

### Реальные Примеры

```kotlin
// Сетевой запрос (apiService — упрощённый пример)
suspend fun getUserProfile(userId: Int): UserProfile {
    return withContext(Dispatchers.IO) {
        val response = apiService.getUser(userId)
        response.toUserProfile()
    }
}

// Операция с базой данных (database — упрощённый пример)
suspend fun saveToDatabase(user: User): Long {
    return withContext(Dispatchers.IO) {
        database.userDao().insert(user)
    }
}

// Файловый ввод-вывод
suspend fun readFile(path: String): String {
    return withContext(Dispatchers.IO) {
        File(path).readText()
    }
}

// Комбинирование нескольких suspend-вызовов
suspend fun loadUserData(userId: Int): UserData {
    val profile = getUserProfile(userId)
    val posts = getUserPosts(userId)
    val friends = getUserFriends(userId)

    return UserData(profile, posts, friends)
}
```

### Suspend-функции И Коллбеки

```kotlin
// Преобразование callback-API в suspend-функцию (DownloadCallback — упрощённый интерфейс)
suspend fun downloadFile(url: String): File = suspendCoroutine { continuation ->
    fileDownloader.download(url, object : DownloadCallback {
        override fun onSuccess(result: File) {
            continuation.resume(result)
        }

        override fun onError(error: Exception) {
            continuation.resumeWithException(error)
        }
    })
}

// Использование suspendCancellableCoroutine для поддержки отмены (Callback — упрощённый интерфейс)
suspend fun fetchDataWithCancellation(): String = suspendCancellableCoroutine { continuation ->
    val call = apiClient.getData()

    call.enqueue(object : Callback<String> {
        override fun onResponse(result: String) {
            continuation.resume(result)
        }

        override fun onFailure(error: Throwable) {
            continuation.resumeWithException(error)
        }
    })

    // Обработка отмены
    continuation.invokeOnCancellation {
        call.cancel()
    }
}
```

### Suspend-функции В Классах

```kotlin
class UserRepository {
    // Публичный suspend-метод класса
    suspend fun fetchUser(id: Int): User {
        return withContext(Dispatchers.IO) {
            api.getUser(id)
        }
    }

    // Приватный suspend-хелпер
    private suspend fun validateUser(user: User): Boolean {
        delay(100)
        return user.email.isNotEmpty()
    }

    // Публичная suspend-функция, использующая приватную suspend-функцию
    suspend fun saveUser(user: User): Result<Unit> {
        return if (validateUser(user)) {
            withContext(Dispatchers.IO) {
                database.save(user)
                Result.success(Unit)
            }
        } else {
            Result.failure(IllegalArgumentException("Invalid user"))
        }
    }
}
```

### Suspend-функции-расширения

```kotlin
// Расширение для обычного класса
suspend fun String.fetchFromUrl(): String {
    return withContext(Dispatchers.IO) {
        URL(this@fetchFromUrl).readText()
    }
}

// Использование
suspend fun example() {
    val content = "https://example.com".fetchFromUrl()
    println(content)
}

// Обобщённое расширение
suspend fun <T> List<T>.processAsync(
    transform: suspend (T) -> T
): List<T> = coroutineScope {
    map { item ->
        async { transform(item) }
    }.awaitAll()
}

// Использование
suspend fun processItems() {
    val items = listOf(1, 2, 3, 4, 5)
    val processed = items.processAsync { item ->
        delay(100)
        item * 2
    }
    println(processed)  // [2, 4, 6, 8, 10]
}
```

### Suspend-лямбды

```kotlin
// Функция, принимающая suspend-лямбду
suspend fun <T> retry(
    times: Int = 3,
    delayMs: Long = 1000,
    block: suspend () -> T
): T {
    repeat(times - 1) {
        try {
            return block()
        } catch (e: Exception) {
            delay(delayMs)
        }
    }
    return block()  // Последняя попытка
}

// Использование
suspend fun fetchWithRetry() {
    val data = retry(times = 5, delayMs = 2000) {
        fetchData()  // Будет пробовать до 5 раз
    }
}

// Suspend-лямбда как параметр
fun processInBackground(action: suspend () -> Unit) {
    CoroutineScope(Dispatchers.IO).launch {
        action()
    }
}

// Использование
processInBackground {
    val data = fetchData()
    saveToDatabase(data)
}
```

### Inline Suspend-функции

```kotlin
// Inline suspend-функция для измерения времени выполнения
suspend inline fun <T> measureTime(
    block: suspend () -> T
): Pair<T, Long> {
    val startTime = System.currentTimeMillis()
    val result = block()
    val duration = System.currentTimeMillis() - startTime
    return result to duration
}

// Использование
suspend fun exampleMeasure() {
    val (data, time) = measureTime {
        fetchData()
    }
    println("Fetched in ${time}ms")
}
```

### Suspend-функции И `Flow`

```kotlin
// Функция, возвращающая Flow (сама не suspend)
fun getUserUpdates(userId: Int): Flow<UserUpdate> = flow {
    while (true) {
        val update = fetchUserUpdate(userId)  // suspend-вызов
        emit(update)
        delay(5000)
    }
}

// Suspend-функция, собирающая Flow
suspend fun processUpdates(userId: Int) {
    getUserUpdates(userId).collect { update ->
        println("Received update: $update")
    }
}
```

### Обработка Ошибок В Suspend-функциях

```kotlin
// Suspend-функция с try-catch
suspend fun fetchDataSafely(): Result<String> {
    return try {
        val data = fetchData()
        Result.success(data)
    } catch (e: Exception) {
        Result.failure(e)
    }
}

// Suspend-функция, которая выбрасывает исключение (response — упрощённый тип)
suspend fun fetchDataOrThrow(): String {
    val response = withContext(Dispatchers.IO) {
        api.getData()
    }

    if (response.isSuccessful && response.body != null) {
        return response.body
    } else {
        throw ApiException("Failed to fetch data")
    }
}

// Обработка исключений при вызове suspend-функций
suspend fun handleErrors() {
    try {
        val data = fetchDataOrThrow()
        println(data)
    } catch (e: ApiException) {
        println("API Error: ${e.message}")
    } catch (e: CancellationException) {
        throw e  // CancellationException всегда пробрасываем дальше
    } catch (e: Exception) {
        println("Unexpected error: ${e.message}")
    }
}
```

### Тестирование Suspend-функций

```kotlin
class UserRepositoryTest {
    @Test
    fun `test fetchUser returns user`() = runTest {
        val repository = UserRepository()

        val user = repository.fetchUser(1)

        assertEquals("John Doe", user.name)
    }

    @Test
    fun `test fetchUser with timeout`() = runTest {
        val repository = UserRepository()

        withTimeout(1000) {
            val user = repository.fetchUser(1)
            assertNotNull(user)
        }
    }
}
```

### Распространённые Паттерны

```kotlin
// 1. CPU-интенсивная задача с использованием Dispatchers.Default
suspend fun cpuIntensiveTask(): Int = withContext(Dispatchers.Default) {
    (1..1000000).sum()
}

// 2. Suspend-функция с таймаутом
suspend fun fetchWithTimeout(timeoutMs: Long = 5000): String {
    return withTimeout(timeoutMs) {
        fetchData()
    }
}

// 3. Suspend-функция со структурированной конкуррентностью
suspend fun loadAllData(): AppData = coroutineScope {
    val users = async { fetchUsers() }
    val posts = async { fetchPosts() }
    val settings = async { fetchSettings() }

    AppData(
        users = users.await(),
        posts = posts.await(),
        settings = settings.await()
    )
}

// 4. Длинная задача с проверкой отмены
suspend fun longRunningTask() {
    repeat(1000) { i ->
        ensureActive()  // Бросает исключение при отмене
        if (!isActive) return

        // Работа с элементом
        processItem(i)
        delay(10)
    }
}
```

### Ключевые Правила

1. Добавьте модификатор `suspend` перед `fun`, чтобы объявить suspend-функцию.
2. Suspend-функции можно вызывать:
   - из других suspend-функций;
   - из тел корутин, запущенных билдерами (`launch`, `async`, `runBlocking` и т.п.);
   - через низкоуровневые continuation API (в прикладном коде используется редко).
3. Нельзя вызывать suspend-функции как обычные синхронные из регулярных функций без запуска корутины или использования continuation API.
4. Suspend-функции поддерживают все обычные возможности Kotlin (дженерики, расширения, inline и т.д.).
5. Под капотом компилятор трансформирует suspend-функции в автоматы состояний с дополнительным параметром `Continuation`.

---

## Answer (EN)

Create a suspend function by adding the `suspend` modifier before `fun`. The body of a suspend function may call other suspend functions. You cannot call a suspend function directly (as a regular call) from a non-suspend function — you must start a coroutine (via builders like `launch`, `async`, `runBlocking`, etc.) or, in rare cases, use lower-level continuation APIs (`Continuation`, `suspendCoroutine`, `suspendCancellableCoroutine`).

### Basic Syntax

```kotlin
// Simple suspend function
suspend fun fetchData(): String {
    delay(1000)  // delay is a suspend function
    return "Data loaded"
}

// Suspend function with parameters
suspend fun saveUser(userId: Int, name: String): Boolean {
    delay(500)
    // Save to database
    return true
}

// Suspend function that returns nothing
suspend fun logEvent(event: String) {
    delay(100)
    println("Event logged: $event")
}
```

### Calling Suspend Functions

```kotlin
// - WRONG: Cannot call directly as a regular function from non-suspend
fun regularFunction() {
    val data = fetchData()  // Compilation error: suspend function should be called only from a coroutine or another suspend function
}

// - CORRECT: Call inside coroutine started by runBlocking
fun main() = runBlocking {
    val data = fetchData()  // OK - inside coroutine started by runBlocking
    println(data)
}

// - CORRECT: Call from another suspend function
suspend fun processData() {
    val data = fetchData()  // OK - suspend calling suspend
    println(data)
}

// - CORRECT: Call inside coroutine started by launch/async
fun loadData() {
    CoroutineScope(Dispatchers.IO).launch {
        val data = fetchData()  // OK - inside coroutine
        println(data)
    }
}
```

### Real-World Examples

```kotlin
// Network request (apiService is a simplified placeholder)
suspend fun getUserProfile(userId: Int): UserProfile {
    return withContext(Dispatchers.IO) {
        val response = apiService.getUser(userId)
        response.toUserProfile()
    }
}

// Database operation (database is a simplified placeholder)
suspend fun saveToDatabase(user: User): Long {
    return withContext(Dispatchers.IO) {
        database.userDao().insert(user)
    }
}

// File I/O
suspend fun readFile(path: String): String {
    return withContext(Dispatchers.IO) {
        File(path).readText()
    }
}

// Combining multiple suspend calls
suspend fun loadUserData(userId: Int): UserData {
    val profile = getUserProfile(userId)
    val posts = getUserPosts(userId)
    val friends = getUserFriends(userId)

    return UserData(profile, posts, friends)
}
```

### Suspend Functions with Callbacks

```kotlin
// Converting callback-based API to suspend function (DownloadCallback is a simplified interface)
suspend fun downloadFile(url: String): File = suspendCoroutine { continuation ->
    fileDownloader.download(url, object : DownloadCallback {
        override fun onSuccess(result: File) {
            continuation.resume(result)
        }

        override fun onError(error: Exception) {
            continuation.resumeWithException(error)
        }
    })
}

// Using suspendCancellableCoroutine for cancellation support (Callback is a simplified interface)
suspend fun fetchDataWithCancellation(): String = suspendCancellableCoroutine { continuation ->
    val call = apiClient.getData()

    call.enqueue(object : Callback<String> {
        override fun onResponse(result: String) {
            continuation.resume(result)
        }

        override fun onFailure(error: Throwable) {
            continuation.resumeWithException(error)
        }
    })

    // Handle cancellation
    continuation.invokeOnCancellation {
        call.cancel()
    }
}
```

### Suspend Functions in Classes

```kotlin
class UserRepository {
    // Suspend function as class method
    suspend fun fetchUser(id: Int): User {
        return withContext(Dispatchers.IO) {
            api.getUser(id)
        }
    }

    // Private suspend helper
    private suspend fun validateUser(user: User): Boolean {
        delay(100)
        return user.email.isNotEmpty()
    }

    // Public suspend function using private suspend function
    suspend fun saveUser(user: User): Result<Unit> {
        return if (validateUser(user)) {
            withContext(Dispatchers.IO) {
                database.save(user)
                Result.success(Unit)
            }
        } else {
            Result.failure(IllegalArgumentException("Invalid user"))
        }
    }
}
```

### Suspend Extension Functions

```kotlin
// Extension on regular class
suspend fun String.fetchFromUrl(): String {
    return withContext(Dispatchers.IO) {
        URL(this@fetchFromUrl).readText()
    }
}

// Usage
suspend fun example() {
    val content = "https://example.com".fetchFromUrl()
    println(content)
}

// Extension on generic type
suspend fun <T> List<T>.processAsync(
    transform: suspend (T) -> T
): List<T> = coroutineScope {
    map { item ->
        async { transform(item) }
    }.awaitAll()
}

// Usage
suspend fun processItems() {
    val items = listOf(1, 2, 3, 4, 5)
    val processed = items.processAsync { item ->
        delay(100)
        item * 2
    }
    println(processed)  // [2, 4, 6, 8, 10]
}
```

### Suspend Lambda Functions

```kotlin
// Function that accepts suspend lambda
suspend fun <T> retry(
    times: Int = 3,
    delayMs: Long = 1000,
    block: suspend () -> T
): T {
    repeat(times - 1) {
        try {
            return block()
        } catch (e: Exception) {
            delay(delayMs)
        }
    }
    return block()  // Last attempt
}

// Usage
suspend fun fetchWithRetry() {
    val data = retry(times = 5, delayMs = 2000) {
        fetchData()  // Will retry up to 5 times
    }
}

// Suspend lambda as parameter
fun processInBackground(action: suspend () -> Unit) {
    CoroutineScope(Dispatchers.IO).launch {
        action()
    }
}

// Usage
processInBackground {
    val data = fetchData()
    saveToDatabase(data)
}
```

### Inline Suspend Functions

```kotlin
// Inline suspend function for measuring execution time
suspend inline fun <T> measureTime(
    block: suspend () -> T
): Pair<T, Long> {
    val startTime = System.currentTimeMillis()
    val result = block()
    val duration = System.currentTimeMillis() - startTime
    return result to duration
}

// Usage
suspend fun exampleMeasure() {
    val (data, time) = measureTime {
        fetchData()
    }
    println("Fetched in ${time}ms")
}
```

### Suspend Functions with Flow

```kotlin
// Function returning Flow (note: not suspend)
fun getUserUpdates(userId: Int): Flow<UserUpdate> = flow {
    while (true) {
        val update = fetchUserUpdate(userId)  // suspend call
        emit(update)
        delay(5000)
    }
}

// Suspend function collecting Flow
suspend fun processUpdates(userId: Int) {
    getUserUpdates(userId).collect { update ->
        println("Received update: $update")
    }
}
```

### Error Handling in Suspend Functions

```kotlin
// Suspend function with try-catch
suspend fun fetchDataSafely(): Result<String> {
    return try {
        val data = fetchData()
        Result.success(data)
    } catch (e: Exception) {
        Result.failure(e)
    }
}

// Suspend function that throws (response is a simplified placeholder type)
suspend fun fetchDataOrThrow(): String {
    val response = withContext(Dispatchers.IO) {
        api.getData()
    }

    if (response.isSuccessful && response.body != null) {
        return response.body
    } else {
        throw ApiException("Failed to fetch data")
    }
}

// Handling exceptions when calling suspend functions
suspend fun handleErrors() {
    try {
        val data = fetchDataOrThrow()
        println(data)
    } catch (e: ApiException) {
        println("API Error: ${e.message}")
    } catch (e: CancellationException) {
        throw e  // Always rethrow CancellationException
    } catch (e: Exception) {
        println("Unexpected error: ${e.message}")
    }
}
```

### Testing Suspend Functions

```kotlin
class UserRepositoryTest {
    @Test
    fun `test fetchUser returns user`() = runTest {
        val repository = UserRepository()

        val user = repository.fetchUser(1)

        assertEquals("John Doe", user.name)
    }

    @Test
    fun `test fetchUser with timeout`() = runTest {
        val repository = UserRepository()

        withTimeout(1000) {
            val user = repository.fetchUser(1)
            assertNotNull(user)
        }
    }
}
```

### Common Patterns

```kotlin
// 1. CPU-intensive task using Dispatchers.Default
suspend fun cpuIntensiveTask(): Int = withContext(Dispatchers.Default) {
    // Heavy computation
    (1..1000000).sum()
}

// 2. Suspend function with timeout
suspend fun fetchWithTimeout(timeoutMs: Long = 5000): String {
    return withTimeout(timeoutMs) {
        fetchData()
    }
}

// 3. Suspend function with structured concurrency
suspend fun loadAllData(): AppData = coroutineScope {
    val users = async { fetchUsers() }
    val posts = async { fetchPosts() }
    val settings = async { fetchSettings() }

    AppData(
        users = users.await(),
        posts = posts.await(),
        settings = settings.await()
    )
}

// 4. Suspend function that checks cancellation
suspend fun longRunningTask() {
    repeat(1000) { i ->
        ensureActive()  // Throws if cancelled
        if (!isActive) return

        // Do work
        processItem(i)
        delay(10)
    }
}
```

### Key Rules

1. Add `suspend` modifier before `fun` to declare a suspend function.
2. Suspend functions can be invoked:
   - From other suspend functions
   - From within coroutine bodies started by builders (`launch`, `async`, `runBlocking`, etc.)
   - Via low-level continuation APIs (rarely used in application code)
3. They cannot be invoked as plain synchronous calls from regular functions without starting a coroutine or using continuation APIs.
4. Suspend functions can use all regular Kotlin features (generics, extensions, inline, etc.).
5. Under the hood, the compiler transforms suspend functions to state machines with an extra `Continuation` parameter.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого подхода от Java?
- Когда вы бы использовали suspend-функции на практике?
- Каковы типичные ошибки и подводные камни при использовании suspend-функций?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [[c-coroutines]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-java-access-modifiers--kotlin--medium]]
- [[q-iterator-order-guarantee--kotlin--medium]]

## Related Questions

- [[q-java-access-modifiers--kotlin--medium]]
- [[q-iterator-order-guarantee--kotlin--medium]]
