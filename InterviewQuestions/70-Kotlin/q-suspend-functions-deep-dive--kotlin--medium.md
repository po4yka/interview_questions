---
id: kotlin-196
title: "Suspend Functions Deep Dive / Suspend функции детальный разбор"
aliases: [Coroutine Suspension, Deep Dive, Suspend Functions, Suspend функции]
topic: kotlin
subtopics: [coroutines, suspend-functions]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-destructuring-declarations--kotlin--medium, q-kotlin-delegation--programming-languages--easy, q-reified-type-parameters--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [concurrency, continuation, coroutines, difficulty/medium, kotlin, suspend-functions]
date created: Friday, October 31st 2025, 6:31:34 pm
date modified: Saturday, November 1st 2025, 5:43:23 pm
---

# Suspend Functions - Deep Dive

**English**: Explain how suspend functions work in Kotlin coroutines. What does the `suspend` keyword do?

## Answer (EN)
**Suspend functions** are functions that can **suspend** execution without blocking threads. The `suspend` keyword transforms a function into a state machine, allowing it to pause at certain points and resume later on any thread.

### What the Suspend Keyword Does

```kotlin
// Regular function - blocks thread
fun loadUser(id: Int): User {
    Thread.sleep(1000) // - Blocks thread!
    return database.getUser(id)
}

// Suspend function - does NOT block thread
suspend fun loadUser(id: Int): User {
    delay(1000) // - Suspends coroutine, releases thread
    return database.getUser(id)
}
```

**Key differences**:
- - **Regular function**: blocks thread → other tasks wait
- - **Suspend function**: releases thread → other tasks execute

### Rules for Using Suspend Functions

```kotlin
class UserRepository {
    // - Suspend function can be called from another suspend function
    suspend fun getUser(id: Int): User {
        return apiService.fetchUser(id) // fetchUser is also suspend
    }

    // - Or from coroutine scope
    fun loadUserInBackground(id: Int) {
        viewModelScope.launch {
            val user = getUser(id) // OK inside coroutine
        }
    }

    // - CANNOT call from regular function
    fun getUserSync(id: Int): User {
        return getUser(id) // - Compilation error!
    }
}
```

**3 ways to call suspend function**:
1. From another suspend function
2. From coroutine builder (`launch`, `async`)
3. From `runBlocking` (only for tests/main)

### How Suspend Works under the Hood

Kotlin compiler transforms suspend functions using **Continuation Passing Style (CPS)**:

```kotlin
// Code you write:
suspend fun loginUser(email: String, password: String): User {
    val token = authenticate(email, password)  // suspension point 1
    val user = fetchUserData(token)            // suspension point 2
    return user
}

// What compiler generates (simplified):
fun loginUser(
    email: String,
    password: String,
    continuation: Continuation<User>
): Any? {
    val stateMachine = continuation as? LoginUserStateMachine
        ?: LoginUserStateMachine(continuation)

    when (stateMachine.label) {
        0 -> {
            stateMachine.label = 1
            val result = authenticate(email, password, stateMachine)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            stateMachine.token = result as String
        }
        1 -> {
            val token = stateMachine.token
            stateMachine.label = 2
            val result = fetchUserData(token, stateMachine)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            return result as User
        }
    }
}
```

**What happens**:
1. Suspend function is transformed into a **state machine** with labels
2. A `Continuation<T>` parameter is added - callback for resumption
3. At each suspension point, function may return `COROUTINE_SUSPENDED`
4. When ready to resume - calls `continuation.resumeWith(result)`

### Continuation - what is It?

```kotlin
// Continuation - is a callback for coroutine resumption
public interface Continuation<in T> {
    public val context: CoroutineContext
    public fun resumeWith(result: Result<T>)
}

// Extension functions for convenience
fun <T> Continuation<T>.resume(value: T)
fun <T> Continuation<T>.resumeWithException(exception: Throwable)
```

**Example using Continuation API**:

```kotlin
// Transform callback API into suspend function
suspend fun fetchUserFromCallback(id: Int): User = suspendCoroutine { continuation ->
    // Old callback API
    userApi.getUser(id, object : Callback<User> {
        override fun onSuccess(user: User) {
            continuation.resume(user) // Resume with result
        }

        override fun onError(error: Exception) {
            continuation.resumeWithException(error) // Resume with error
        }
    })
}

// Now can use as regular suspend function
suspend fun loadUser(id: Int) {
    try {
        val user = fetchUserFromCallback(id) // Looks synchronous!
        println("Loaded: ${user.name}")
    } catch (e: Exception) {
        println("Error: ${e.message}")
    }
}
```

### suspendCoroutine Vs suspendCancellableCoroutine

```kotlin
// - NOT cancellable - can lead to leaks
suspend fun downloadFile(url: String): File = suspendCoroutine { continuation ->
    networkClient.download(url, object : DownloadCallback {
        override fun onComplete(file: File) {
            continuation.resume(file)
        }
    })
    // Problem: if coroutine is cancelled, callback still executes!
}

// - Cancellable - correct approach
suspend fun downloadFile(url: String): File = suspendCancellableCoroutine { continuation ->
    val call = networkClient.download(url, object : DownloadCallback {
        override fun onComplete(file: File) {
            continuation.resume(file)
        }

        override fun onError(error: Exception) {
            continuation.resumeWithException(error)
        }
    })

    // Register cancellation handler
    continuation.invokeOnCancellation {
        call.cancel() // Cancel network request
    }
}
```

**Always use `suspendCancellableCoroutine`** for callback API integration!

### Suspend Functions and Threads

```kotlin
suspend fun processData() {
    println("Start: ${Thread.currentThread().name}")

    delay(100) // suspension point

    println("After delay: ${Thread.currentThread().name}")

    withContext(Dispatchers.IO) { // suspension point
        println("In IO: ${Thread.currentThread().name}")
    }

    println("End: ${Thread.currentThread().name}")
}

// Output:
// Start: main
// After delay: main (may be different thread from same dispatcher!)
// In IO: DefaultDispatcher-worker-1
// End: main
```

**Important**: After suspension point, coroutine may resume on **different thread**!

### Real Examples of Suspend Functions

#### 1. Network Запросы (Retrofit)

```kotlin
interface UserApi {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: Int): User

    @POST("users")
    suspend fun createUser(@Body user: UserRequest): User
}

class UserRepository(private val api: UserApi) {
    suspend fun getUser(id: Int): Result<User> = try {
        Result.success(api.getUser(id)) // Автоматически suspend
    } catch (e: Exception) {
        Result.failure(e)
    }
}

// Использование в ViewModel
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    fun loadUser(id: Int) {
        viewModelScope.launch {
            _isLoading.value = true

            when (val result = repository.getUser(id)) {
                is Result.Success -> _user.value = result.data
                is Result.Failure -> _error.value = result.exception.message
            }

            _isLoading.value = false
        }
    }
}
```

#### 2. Database Операции (Room)

```kotlin
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUserById(id: Int): User?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User)

    @Query("SELECT * FROM users")
    fun observeUsers(): Flow<List<User>> // Flow - тоже работает с suspend
}

class LocalUserRepository(private val dao: UserDao) {
    suspend fun saveUser(user: User) {
        dao.insertUser(user) // Выполняется на IO dispatcher автоматически
    }

    suspend fun getUser(id: Int): User? {
        return dao.getUserById(id)
    }

    fun observeUsers(): Flow<List<User>> {
        return dao.observeUsers()
    }
}
```

#### 3. Последовательные Операции

```kotlin
suspend fun registerUser(
    email: String,
    password: String,
    name: String
): User {
    // 1. Проверяем доступность email
    val isAvailable = checkEmailAvailability(email)
    if (!isAvailable) {
        throw EmailAlreadyExistsException()
    }

    // 2. Создаем аккаунт
    val userId = createAccount(email, password)

    // 3. Создаем профиль
    val profile = createProfile(userId, name)

    // 4. Отправляем welcome email
    sendWelcomeEmail(email)

    // 5. Возвращаем пользователя
    return User(userId, email, profile)
}

// Каждая функция - suspend, выполняется последовательно
suspend fun checkEmailAvailability(email: String): Boolean {
    delay(200) // Network request
    return apiService.checkEmail(email)
}
```

#### 4. Параллельные Операции С Async

```kotlin
suspend fun loadDashboardData(): DashboardData = coroutineScope {
    // Все 3 запроса выполняются параллельно
    val userDeferred = async { userApi.getUser() }
    val statsDeferred = async { statsApi.getStats() }
    val notificationsDeferred = async { notificationsApi.getUnread() }

    // Ждем завершения всех
    DashboardData(
        user = userDeferred.await(),
        stats = statsDeferred.await(),
        notifications = notificationsDeferred.await()
    )
}

// Время выполнения: max(user, stats, notifications), а не sum!
```

#### 5. Timeout И Retry

```kotlin
suspend fun fetchWithTimeout(url: String): String {
    return withTimeout(5000) { // 5 секунд timeout
        httpClient.get(url)
    }
}

suspend fun fetchWithRetry(url: String, maxAttempts: Int = 3): String {
    repeat(maxAttempts - 1) { attempt ->
        try {
            return httpClient.get(url)
        } catch (e: IOException) {
            println("Attempt ${attempt + 1} failed, retrying...")
            delay(1000 * (attempt + 1)) // Exponential backoff
        }
    }

    // Последняя попытка без catch - пусть exception пробросится
    return httpClient.get(url)
}
```

### Ошибки И Best Practices

#### - НЕПРАВИЛЬНО: Блокирующие Операции В Suspend Функциях

```kotlin
suspend fun loadData(): String {
    Thread.sleep(1000) // - Блокирует поток!
    return "data"
}
```

#### - ПРАВИЛЬНО: Используйте Suspend-friendly Альтернативы

```kotlin
suspend fun loadData(): String {
    delay(1000) // - Приостанавливает, не блокирует
    return "data"
}

// Или для CPU-intensive работы
suspend fun processImage(bitmap: Bitmap): Bitmap {
    return withContext(Dispatchers.Default) {
        // CPU-intensive обработка
        applyFilters(bitmap)
    }
}
```

#### - НЕПРАВИЛЬНО: runBlocking В Production Коде

```kotlin
fun loadUserSync(id: Int): User {
    return runBlocking { // - Блокирует поток!
        userRepository.getUser(id)
    }
}
```

#### - ПРАВИЛЬНО: Используйте Coroutine Scope

```kotlin
class UserViewModel : ViewModel() {
    fun loadUser(id: Int) {
        viewModelScope.launch { // - Асинхронно
            val user = userRepository.getUser(id)
            _user.value = user
        }
    }
}
```

#### - НЕПРАВИЛЬНО: Ненужный Suspend Modifier

```kotlin
// Не делает ничего suspend - модификатор не нужен
suspend fun calculateSum(a: Int, b: Int): Int {
    return a + b
}
```

#### - ПРАВИЛЬНО: Suspend Только Если Действительно Приостанавливает

```kotlin
// Обычная функция - нет suspend операций
fun calculateSum(a: Int, b: Int): Int {
    return a + b
}

// Suspend - вызывает другие suspend функции
suspend fun loadAndCalculate(): Int {
    val a = fetchA() // suspend
    val b = fetchB() // suspend
    return calculateSum(a, b)
}
```

### Suspend Функции В Интерфейсах

```kotlin
interface DataSource<T> {
    suspend fun fetch(): T
    suspend fun save(data: T)
}

class RemoteDataSource : DataSource<User> {
    override suspend fun fetch(): User {
        return apiService.getUser()
    }

    override suspend fun save(data: User) {
        apiService.updateUser(data)
    }
}

class CachedDataSource(
    private val remote: DataSource<User>,
    private val local: DataSource<User>
) : DataSource<User> {
    override suspend fun fetch(): User {
        return try {
            remote.fetch().also { local.save(it) }
        } catch (e: Exception) {
            local.fetch() // Fallback to cache
        }
    }

    override suspend fun save(data: User) {
        local.save(data)
        remote.save(data)
    }
}
```

### Suspend Функции С Flow

```kotlin
interface UserRepository {
    // Возвращает Flow - НЕ suspend функция!
    fun observeUsers(): Flow<List<User>>

    // Suspend функция - разовая операция
    suspend fun refreshUsers()
}

class UserRepositoryImpl(
    private val api: UserApi,
    private val dao: UserDao
) : UserRepository {
    override fun observeUsers(): Flow<List<User>> {
        return dao.observeUsers() // Flow из Room
    }

    override suspend fun refreshUsers() {
        val users = api.getUsers() // Suspend вызов
        dao.insertAll(users)       // Suspend вызов
    }
}

// Использование в ViewModel
class UsersViewModel(private val repository: UserRepository) : ViewModel() {
    val users = repository.observeUsers() // Flow
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun refresh() {
        viewModelScope.launch {
            try {
                repository.refreshUsers() // Suspend вызов
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }
}
```

### Тестирование Suspend Функций

```kotlin
class UserRepositoryTest {
    @Test
    fun `test getUser returns user`() = runTest { // runTest для корутин
        val repository = UserRepository(fakeApi)

        val user = repository.getUser(1) // Вызываем suspend функцию

        assertEquals("Alice", user.name)
    }

    @Test
    fun `test parallel loading`() = runTest {
        val repository = UserRepository(fakeApi)

        // Тестируем параллельную загрузку
        val users = coroutineScope {
            (1..10).map { id ->
                async { repository.getUser(id) }
            }.awaitAll()
        }

        assertEquals(10, users.size)
    }

    @Test
    fun `test timeout handling`() = runTest {
        val repository = UserRepository(slowApi)

        assertFailsWith<TimeoutCancellationException> {
            withTimeout(100) {
                repository.getUser(1)
            }
        }
    }
}
```

### Продвинутые Паттерны

#### 1. Suspend Lazy Initialization

```kotlin
class ExpensiveResource {
    private val _data = lazy {
        // - Проблема: lazy не поддерживает suspend
        expensiveInitialization()
    }
}

// - Решение: suspend lazy
class ExpensiveResource {
    private val mutex = Mutex()
    private var _data: Data? = null

    suspend fun getData(): Data {
        if (_data == null) {
            mutex.withLock {
                if (_data == null) {
                    _data = expensiveInitialization() // suspend функция
                }
            }
        }
        return _data!!
    }
}
```

#### 2. Suspend Property Delegation

```kotlin
class UserCache {
    private val cache = mutableMapOf<Int, User>()

    suspend operator fun getValue(
        thisRef: Any?,
        property: KProperty<*>
    ): User? {
        val id = property.name.removePrefix("user").toInt()
        return cache.getOrPut(id) {
            fetchUser(id) // suspend функция
        }
    }
}

// Использование (только в suspend контексте!)
suspend fun example() {
    val cache = UserCache()
    val user1 by cache // Работает только в suspend функциях!
}
```

#### 3. Resource Cleanup С Использованием Suspend

```kotlin
suspend fun <T : Closeable, R> T.useSuspending(block: suspend (T) -> R): R {
    return try {
        block(this)
    } finally {
        close()
    }
}

// Использование
suspend fun processFile(path: String) {
    FileInputStream(path).useSuspending { stream ->
        val data = readSuspending(stream) // suspend операция
        processSuspending(data)           // suspend операция
    } // Автоматически закроется
}
```

### Производительность Suspend Функций

```kotlin
// Миф: suspend функции медленнее обычных
// Реальность: overhead минимальный

@Benchmark
fun regularFunction(): Int {
    return 42
}

@Benchmark
suspend fun suspendFunction(): Int {
    return 42 // Нет suspension points
}

// Результаты: разница < 1% если нет реальных suspension points!

// Реальный overhead появляется только при suspension:
suspend fun withSuspension(): Int {
    delay(1) // Вот здесь появляется overhead state machine
    return 42
}
```

**Выводы**:
- Suspend модификатор сам по себе почти бесплатный
- Overhead появляется при реальном приостановлении (delay, withContext, etc.)
- State machine оптимизирован компилятором

### Suspend Функции И Inline

```kotlin
// Inline suspend функции - для zero-overhead abstractions
inline suspend fun <T> measureTime(
    block: suspend () -> T
): Pair<T, Long> {
    val start = System.currentTimeMillis()
    val result = block()
    val duration = System.currentTimeMillis() - start
    return result to duration
}

// Использование - код block() будет инлайнен
suspend fun example() {
    val (user, time) = measureTime {
        userRepository.getUser(1)
    }
    println("Loaded in ${time}ms")
}
```

### Частые Ошибки

#### 1. Забыли Обработать Отмену

```kotlin
// - НЕПРАВИЛЬНО
suspend fun longRunningTask() {
    repeat(1000) {
        processItem(it) // Не проверяет отмену!
        Thread.sleep(100)
    }
}

// - ПРАВИЛЬНО
suspend fun longRunningTask() {
    repeat(1000) {
        ensureActive() // Проверяет отмену
        processItem(it)
        delay(100) // delay тоже проверяет отмену
    }
}
```

#### 2. Неправильный exception Handling

```kotlin
// - НЕПРАВИЛЬНО - глотает CancellationException
suspend fun fetchData() {
    try {
        apiService.getData()
    } catch (e: Exception) { // Ловит и CancellationException!
        logError(e)
    }
}

// - ПРАВИЛЬНО - пробрасывает CancellationException
suspend fun fetchData() {
    try {
        apiService.getData()
    } catch (e: CancellationException) {
        throw e // ВАЖНО: пробросить!
    } catch (e: Exception) {
        logError(e)
    }
}
```

**English**: **Suspend functions** are functions that can pause execution without blocking threads. The `suspend` keyword transforms a function into a state machine, allowing it to suspend at certain points and resume later on any thread.

**How it works**: The Kotlin compiler uses Continuation Passing Style (CPS) to transform suspend functions into state machines. Each suspension point gets a label, and a `Continuation<T>` callback parameter is added for resumption. When a suspend function pauses, it returns `COROUTINE_SUSPENDED`; when ready to resume, it calls `continuation.resumeWith(result)`.

**Key rules**: Suspend functions can only be called from: (1) other suspend functions, (2) coroutine builders (`launch`, `async`), or (3) `runBlocking` (tests/main only).

**Thread switching**: After a suspension point, the coroutine may resume on a different thread. Suspend functions don't block threads - they release them for other tasks.

**Best practices**: Use `delay()` not `Thread.sleep()`. Use `suspendCancellableCoroutine` for callback integration (not `suspendCoroutine`). Always register cancellation handlers with `invokeOnCancellation`. Don't use `runBlocking` in production code. Always propagate `CancellationException`. Check for cancellation in long-running loops with `ensureActive()`.

**Performance**: Minimal overhead if no actual suspension occurs. State machine optimized by compiler. Use `inline suspend` for zero-overhead abstractions.

**Common uses**: Network requests (Retrofit), database operations (Room), sequential async operations, parallel operations with `async`/`await`, timeout/retry logic, Flow emissions.

## Ответ (RU)

**Suspend функции** - это функции, которые могут приостанавливать выполнение без блокировки потоков. Ключевое слово `suspend` преобразует функцию в машину состояний, позволяя ей приостановиться в определенных точках и возобновиться позже на любом потоке.

### Как Это Работает

Компилятор Kotlin использует Continuation Passing Style (CPS) для преобразования suspend функций в машины состояний. Каждая точка приостановки получает метку, и добавляется параметр `Continuation<T>` для возобновления. Когда suspend функция приостанавливается, она возвращает `COROUTINE_SUSPENDED`; когда готова возобновиться, вызывает `continuation.resumeWith(result)`.

### Основные Правила

Suspend функции можно вызывать только из:
1. Других suspend функций
2. Coroutine builders (`launch`, `async`)
3. `runBlocking` (только для тестов/main)

### Переключение Потоков

После точки приостановки корутина может возобновиться на другом потоке. Suspend функции не блокируют потоки - они освобождают их для других задач.

### Best Practices

- Используйте `delay()`, а не `Thread.sleep()`
- Используйте `suspendCancellableCoroutine` для интеграции callback API (не `suspendCoroutine`)
- Всегда регистрируйте обработчики отмены через `invokeOnCancellation`
- Не используйте `runBlocking` в production коде
- Всегда пробрасывайте `CancellationException`
- Проверяйте отмену в длительных циклах через `ensureActive()`

### Производительность

Минимальный overhead если нет реального приостановления. State machine оптимизирован компилятором. Используйте `inline suspend` для zero-overhead абстракций.

### Типичные Случаи Использования

Сетевые запросы (Retrofit), операции с БД (Room), последовательные async операции, параллельные операции с `async`/`await`, timeout/retry логика, эмиссии Flow.

## Related Questions

- [[q-reified-type-parameters--kotlin--medium]]
- [[q-kotlin-delegation--programming-languages--easy]]
- [[q-destructuring-declarations--kotlin--medium]]
