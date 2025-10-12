---
tags:
  - programming-languages
difficulty: medium
status: draft
---

# How to Create a Suspend Function?

# Question (EN)
> How to create a suspend function?

# Вопрос (RU)
> Как создать suspend функцию?

---

## Answer (EN)

Create a suspend function by adding the **suspend** modifier before `fun`. Suspend functions cannot be called directly from regular functions, only from coroutines or other suspend functions.

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
// - WRONG: Cannot call from regular function
fun regularFunction() {
    val data = fetchData()  // Compilation error!
}

// - CORRECT: Call from coroutine builder
fun main() = runBlocking {
    val data = fetchData()  // OK - inside runBlocking
    println(data)
}

// - CORRECT: Call from another suspend function
suspend fun processData() {
    val data = fetchData()  // OK - suspend calling suspend
    println(data)
}

// - CORRECT: Call from launch/async
fun loadData() {
    CoroutineScope(Dispatchers.IO).launch {
        val data = fetchData()  // OK - inside launch
        println(data)
    }
}
```

### Real-World Examples

```kotlin
// Network request
suspend fun getUserProfile(userId: Int): UserProfile {
    return withContext(Dispatchers.IO) {
        val response = apiService.getUser(userId)
        response.toUserProfile()
    }
}

// Database operation
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
// Converting callback-based API to suspend function
suspend fun downloadFile(url: String): File = suspendCoroutine { continuation ->
    fileDownloader.download(url, object : DownloadCallback {
        override fun onSuccess(file: File) {
            continuation.resume(file)
        }

        override fun onError(error: Exception) {
            continuation.resumeWithException(error)
        }
    })
}

// Using suspendCancellableCoroutine for cancellation support
suspend fun fetchDataWithCancellation(): String = suspendCancellableCoroutine { continuation ->
    val call = apiClient.getData()

    call.enqueue(object : Callback<String> {
        override fun onResponse(response: String) {
            continuation.resume(response)
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

    // Public suspend function using private suspend
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
    delay: Long = 1000,
    block: suspend () -> T
): T {
    repeat(times - 1) {
        try {
            return block()
        } catch (e: Exception) {
            delay(delay)
        }
    }
    return block()  // Last attempt
}

// Usage
suspend fun fetchWithRetry() {
    val data = retry(times = 5, delay = 2000) {
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
// Inline suspend function for better performance
suspend inline fun <T> measureTime(
    block: suspend () -> T
): Pair<T, Long> {
    val startTime = System.currentTimeMillis()
    val result = block()
    val duration = System.currentTimeMillis() - startTime
    return result to duration
}

// Usage
suspend fun example() {
    val (data, time) = measureTime {
        fetchData()
    }
    println("Fetched in ${time}ms")
}
```

### Suspend Functions with Flow

```kotlin
// Suspend function returning Flow
suspend fun getUserUpdates(userId: Int): Flow<UserUpdate> = flow {
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

// Suspend function that throws
suspend fun fetchDataOrThrow(): String {
    val response = withContext(Dispatchers.IO) {
        api.getData()
    }

    if (response.isSuccessful) {
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
// 1. Suspend function with default dispatcher
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
        // or check manually:
        if (!isActive) return

        // Do work
        processItem(i)
        delay(10)
    }
}
```

### Key Rules

1. - Add `suspend` modifier before `fun`
2. - Can only call suspend functions from:
   - Other suspend functions
   - Coroutine builders (`launch`, `async`, `runBlocking`)
   - Coroutine scope extensions
3. - Cannot call from regular functions directly
4. - Can use all regular Kotlin features (generics, extensions, inline, etc.)
5. - Automatically receives `Continuation` parameter (compiler adds it)

---

## Ответ (RU)

Создать suspend-функцию можно, добавив suspend перед fun. Suspend функции нельзя вызывать напрямую из обычных функций, только из корутин.
