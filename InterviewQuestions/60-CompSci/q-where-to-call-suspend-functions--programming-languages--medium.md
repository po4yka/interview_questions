---
tags:
  - programming-languages
difficulty: medium
status: reviewed
---

# Where to Call Suspend Functions?

## Answer

Suspend functions can only be called from **coroutines**. You can call them from:
- **launch {}** or **async {}** within a CoroutineScope
- **Other suspend functions**
- **runBlocking {}** for testing or in main thread

### 1. From Other Suspend Functions

```kotlin
// Suspend function calling another suspend function
suspend fun fetchUserData(userId: Int): UserData {
    val profile = fetchUserProfile(userId)  // ✅ OK
    val settings = fetchUserSettings(userId)  // ✅ OK
    return UserData(profile, settings)
}

suspend fun fetchUserProfile(userId: Int): UserProfile {
    delay(100)
    return UserProfile("User $userId")
}

suspend fun fetchUserSettings(userId: Int): UserSettings {
    delay(50)
    return UserSettings(darkMode = true)
}
```

### 2. From launch {} Builder

```kotlin
import kotlinx.coroutines.*

fun loadDataInBackground() {
    // Create a coroutine scope
    CoroutineScope(Dispatchers.IO).launch {
        // ✅ OK: Inside launch coroutine builder
        val data = fetchData()
        println("Data: $data")
    }
}

// In Android ViewModel
class MyViewModel : ViewModel() {
    fun loadUser(userId: Int) {
        viewModelScope.launch {
            // ✅ OK: Inside viewModelScope.launch
            val user = fetchUser(userId)
            _userState.value = user
        }
    }
}

// In Android Activity/Fragment
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // ✅ OK: Inside lifecycleScope.launch
            val data = loadInitialData()
            updateUI(data)
        }
    }
}
```

### 3. From async {} Builder

```kotlin
suspend fun loadParallelData(): CombinedData = coroutineScope {
    // ✅ OK: Inside coroutineScope and async
    val userData = async { fetchUserData(1) }
    val postsData = async { fetchPostsData(1) }
    val settingsData = async { fetchSettings() }

    CombinedData(
        user = userData.await(),
        posts = postsData.await(),
        settings = settingsData.await()
    )
}

fun parallelFetch() {
    CoroutineScope(Dispatchers.IO).launch {
        val deferred = async {
            // ✅ OK: Inside async
            fetchData()
        }
        val result = deferred.await()
        println(result)
    }
}
```

### 4. From runBlocking {}

```kotlin
// Main function
fun main() = runBlocking {
    // ✅ OK: Inside runBlocking
    val data = fetchData()
    println("Data: $data")
}

// For testing
class MyRepositoryTest {
    @Test
    fun testFetchUser() = runBlocking {
        // ✅ OK: Inside runBlocking for testing
        val repository = MyRepository()
        val user = repository.fetchUser(1)
        assertEquals("User 1", user.name)
    }
}

// Bridge between regular and suspend code (use sparingly)
fun regularFunction(): String = runBlocking {
    // ✅ OK but not recommended: Blocks the thread
    fetchData()
}
```

### 5. From coroutineScope {} or supervisorScope {}

```kotlin
suspend fun performComplexOperation() {
    // ✅ OK: Inside coroutineScope
    coroutineScope {
        val task1 = async { fetchData1() }
        val task2 = async { fetchData2() }

        val result1 = task1.await()
        val result2 = task2.await()

        processResults(result1, result2)
    }
}

suspend fun performIndependentTasks() {
    // ✅ OK: Inside supervisorScope
    supervisorScope {
        launch { performTask1() }
        launch { performTask2() }  // Won't be cancelled if task1 fails
    }
}
```

### 6. From withContext {}

```kotlin
suspend fun saveToDatabase(data: String) {
    // ✅ OK: Inside withContext
    withContext(Dispatchers.IO) {
        val validated = validateData(data)  // suspend call
        database.save(validated)
    }
}

suspend fun processOnMain(data: String) {
    withContext(Dispatchers.Main) {
        // ✅ OK: Switch to main thread and call suspend
        val processed = processData(data)
        updateUI(processed)
    }
}
```

### 7. From Flow Builders

```kotlin
fun getUserFlow(): Flow<User> = flow {
    // ✅ OK: Inside flow builder
    val user = fetchUser(1)  // suspend call
    emit(user)

    delay(1000)  // suspend call
    emit(fetchUser(2))
}

fun dataStream(): Flow<String> = channelFlow {
    // ✅ OK: Inside channelFlow
    repeat(5) { i ->
        val data = fetchData()  // suspend call
        send(data)
        delay(1000)
    }
}
```

### 8. Cannot Call from Regular Functions

```kotlin
// ❌ WRONG: Cannot call from regular function
fun regularFunction() {
    val data = fetchData()  // ❌ Compilation error!
    // "Suspend function 'fetchData' should be called only from a coroutine or another suspend function"
}

// ✅ SOLUTION 1: Make function suspend
suspend fun suspendFunction() {
    val data = fetchData()  // ✅ OK
}

// ✅ SOLUTION 2: Use coroutine builder
fun regularFunctionFixed() {
    CoroutineScope(Dispatchers.IO).launch {
        val data = fetchData()  // ✅ OK
    }
}

// ✅ SOLUTION 3: Use runBlocking (blocks thread, avoid in production)
fun regularFunctionBlocking() = runBlocking {
    val data = fetchData()  // ✅ OK but blocks
}
```

### Complete Example: All Valid Contexts

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Sample suspend functions
suspend fun fetchData(): String {
    delay(100)
    return "Data"
}

suspend fun fetchUser(id: Int): String {
    delay(50)
    return "User $id"
}

// 1. ✅ From other suspend function
suspend fun example1() {
    val data = fetchData()
    println(data)
}

// 2. ✅ From launch
fun example2() {
    CoroutineScope(Dispatchers.IO).launch {
        val data = fetchData()
        println(data)
    }
}

// 3. ✅ From async
fun example3() {
    CoroutineScope(Dispatchers.IO).launch {
        val deferred = async { fetchData() }
        println(deferred.await())
    }
}

// 4. ✅ From runBlocking
fun example4() = runBlocking {
    val data = fetchData()
    println(data)
}

// 5. ✅ From coroutineScope
suspend fun example5() = coroutineScope {
    val data = fetchData()
    println(data)
}

// 6. ✅ From withContext
suspend fun example6() {
    withContext(Dispatchers.IO) {
        val data = fetchData()
        println(data)
    }
}

// 7. ✅ From flow
fun example7(): Flow<String> = flow {
    val data = fetchData()
    emit(data)
}

// 8. ✅ From suspend lambda
fun example8(action: suspend () -> Unit) {
    CoroutineScope(Dispatchers.IO).launch {
        action()  // Call suspend lambda
    }
}

fun useExample8() {
    example8 {
        val data = fetchData()  // ✅ OK
        println(data)
    }
}
```

### Real-World Examples

```kotlin
// Android ViewModel
class UserViewModel : ViewModel() {
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    fun loadUser(id: Int) {
        viewModelScope.launch {  // ✅ Coroutine scope
            val userData = fetchUser(id)  // ✅ Can call suspend
            _user.value = userData
        }
    }
}

// Repository pattern
class UserRepository {
    suspend fun getUser(id: Int): User {  // ✅ Suspend function
        return withContext(Dispatchers.IO) {  // ✅ Can call suspend
            api.fetchUser(id)  // ✅ Can call suspend
        }
    }
}

// Use case pattern
class LoadUserUseCase(private val repository: UserRepository) {
    suspend operator fun invoke(id: Int): Result<User> {  // ✅ Suspend
        return try {
            Result.success(repository.getUser(id))  // ✅ Can call suspend
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

// Composable function (Jetpack Compose)
@Composable
fun UserScreen(userId: Int) {
    val user by remember { mutableStateOf<User?>(null) }

    LaunchedEffect(userId) {  // ✅ Coroutine scope
        user = fetchUser(userId)  // ✅ Can call suspend
    }

    // UI rendering...
}
```

### Common Scopes in Android

```kotlin
// 1. viewModelScope - tied to ViewModel lifecycle
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            val data = fetchData()  // ✅ OK
        }
    }
}

// 2. lifecycleScope - tied to Activity/Fragment lifecycle
class MyActivity : AppCompatActivity() {
    fun loadData() {
        lifecycleScope.launch {
            val data = fetchData()  // ✅ OK
        }
    }
}

// 3. GlobalScope - application lifetime (use with caution)
fun someFunction() {
    GlobalScope.launch {
        val data = fetchData()  // ✅ OK but not recommended
    }
}

// 4. Custom scope
class MyManager {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    fun loadData() {
        scope.launch {
            val data = fetchData()  // ✅ OK
        }
    }

    fun cleanup() {
        scope.cancel()  // Cancel all coroutines
    }
}
```

### Best Practices

```kotlin
// ✅ DO: Use appropriate scope
class GoodExample : ViewModel() {
    fun loadUser() {
        viewModelScope.launch {  // Automatically cancelled when ViewModel clears
            val user = fetchUser(1)
        }
    }
}

// ❌ DON'T: Use GlobalScope unnecessarily
class BadExample {
    fun loadUser() {
        GlobalScope.launch {  // Leaks if object is destroyed
            val user = fetchUser(1)
        }
    }
}

// ✅ DO: Handle errors
fun properErrorHandling() {
    CoroutineScope(Dispatchers.IO).launch {
        try {
            val data = fetchData()
        } catch (e: Exception) {
            // Handle error
        }
    }
}

// ✅ DO: Use structured concurrency
suspend fun structuredApproach() = coroutineScope {
    // Child coroutines are automatically managed
    val result1 = async { fetchData() }
    val result2 = async { fetchUser(1) }

    combinedResult(result1.await(), result2.await())
}
```

### Summary Table

| Context | Can Call Suspend? | Blocks Thread? | Use Case |
|---------|-------------------|----------------|----------|
| Another suspend function | ✅ Yes | No | Sequential suspend calls |
| `launch {}` | ✅ Yes | No | Fire-and-forget |
| `async {}` | ✅ Yes | No | Parallel execution with result |
| `runBlocking {}` | ✅ Yes | **Yes** | Tests, main function |
| `coroutineScope {}` | ✅ Yes | No | Structured concurrency |
| `withContext {}` | ✅ Yes | No | Change dispatcher |
| `flow {}` | ✅ Yes | No | Stream of values |
| Regular function | ❌ No | - | Must use builder |

---
## Вопрос (RU)

Откуда можно запускать suspend-функции

## Ответ

suspend-функции можно запускать только из корутин. Можно вызывать их из: launch {} или async {} в CoroutineScope, другое suspend-функции и runBlocking {} для тестирования в main-потоке
