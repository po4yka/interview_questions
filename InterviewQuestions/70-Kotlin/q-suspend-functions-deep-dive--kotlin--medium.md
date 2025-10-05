---
tags:
  - kotlin
  - coroutines
  - suspend-functions
  - concurrency
  - cps
difficulty: medium
---

# Suspend Functions - Deep Dive

**English**: Explain how suspend functions work in Kotlin coroutines. What does the `suspend` keyword do?

## Answer

**Suspend функции** - это функции, которые могут **приостанавливать** (suspend) выполнение без блокировки потока. Ключевое слово `suspend` превращает функцию в state machine, позволяя ей останавливаться в определенных точках и возобновляться позже на любом потоке.

### Что делает suspend keyword

```kotlin
// Обычная функция - блокирует поток
fun loadUser(id: Int): User {
    Thread.sleep(1000) // ❌ Блокирует поток!
    return database.getUser(id)
}

// Suspend функция - НЕ блокирует поток
suspend fun loadUser(id: Int): User {
    delay(1000) // ✅ Приостанавливает корутину, освобождает поток
    return database.getUser(id)
}
```

**Ключевые отличия**:
- ❌ **Обычная функция**: блокирует поток → другие задачи ждут
- ✅ **Suspend функция**: освобождает поток → другие задачи выполняются

### Правила использования suspend функций

```kotlin
class UserRepository {
    // ✅ Suspend функцию можно вызвать из другой suspend функции
    suspend fun getUser(id: Int): User {
        return apiService.fetchUser(id) // fetchUser - тоже suspend
    }

    // ✅ Или из coroutine scope
    fun loadUserInBackground(id: Int) {
        viewModelScope.launch {
            val user = getUser(id) // OK внутри корутины
        }
    }

    // ❌ НЕЛЬЗЯ вызвать из обычной функции
    fun getUserSync(id: Int): User {
        return getUser(id) // ❌ Compilation error!
    }
}
```

**3 способа вызвать suspend функцию**:
1. Из другой suspend функции
2. Из coroutine builder (`launch`, `async`)
3. Из `runBlocking` (только для тестов/main)

### Как работает suspend под капотом

Компилятор Kotlin трансформирует suspend функции используя **Continuation Passing Style (CPS)**:

```kotlin
// Код который вы пишете:
suspend fun loginUser(email: String, password: String): User {
    val token = authenticate(email, password)  // suspension point 1
    val user = fetchUserData(token)            // suspension point 2
    return user
}

// Что генерирует компилятор (упрощенно):
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

**Что происходит**:
1. Suspend функция превращается в **state machine** с метками (labels)
2. Добавляется параметр `Continuation<T>` - callback для возобновления
3. При каждом suspension point функция может вернуть `COROUTINE_SUSPENDED`
4. Когда готова возобновиться - вызывает `continuation.resumeWith(result)`

### Continuation - что это?

```kotlin
// Continuation - это callback для возобновления корутины
public interface Continuation<in T> {
    public val context: CoroutineContext
    public fun resumeWith(result: Result<T>)
}

// Extension функции для удобства
fun <T> Continuation<T>.resume(value: T)
fun <T> Continuation<T>.resumeWithException(exception: Throwable)
```

**Пример использования Continuation API**:

```kotlin
// Превращаем callback API в suspend функцию
suspend fun fetchUserFromCallback(id: Int): User = suspendCoroutine { continuation ->
    // Старый callback API
    userApi.getUser(id, object : Callback<User> {
        override fun onSuccess(user: User) {
            continuation.resume(user) // Возобновляем с результатом
        }

        override fun onError(error: Exception) {
            continuation.resumeWithException(error) // Возобновляем с ошибкой
        }
    })
}

// Теперь можно использовать как обычную suspend функцию
suspend fun loadUser(id: Int) {
    try {
        val user = fetchUserFromCallback(id) // Выглядит синхронно!
        println("Loaded: ${user.name}")
    } catch (e: Exception) {
        println("Error: ${e.message}")
    }
}
```

### suspendCoroutine vs suspendCancellableCoroutine

```kotlin
// ❌ НЕ отменяемая - может привести к утечкам
suspend fun downloadFile(url: String): File = suspendCoroutine { continuation ->
    networkClient.download(url, object : DownloadCallback {
        override fun onComplete(file: File) {
            continuation.resume(file)
        }
    })
    // Проблема: если корутина отменена, callback все равно выполнится!
}

// ✅ Отменяемая - правильный подход
suspend fun downloadFile(url: String): File = suspendCancellableCoroutine { continuation ->
    val call = networkClient.download(url, object : DownloadCallback {
        override fun onComplete(file: File) {
            continuation.resume(file)
        }

        override fun onError(error: Exception) {
            continuation.resumeWithException(error)
        }
    })

    // Регистрируем cancellation handler
    continuation.invokeOnCancellation {
        call.cancel() // Отменяем network запрос
    }
}
```

**Всегда используйте `suspendCancellableCoroutine`** для интеграции с callback API!

### Suspend функции и потоки

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

// Вывод:
// Start: main
// After delay: main (может быть другой поток из того же диспетчера!)
// In IO: DefaultDispatcher-worker-1
// End: main
```

**Важно**: После suspension point корутина может возобновиться на **другом потоке**!

### Реальные примеры suspend функций

#### 1. Network запросы (Retrofit)

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

#### 2. Database операции (Room)

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

#### 3. Последовательные операции

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

#### 4. Параллельные операции с async

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

#### 5. Timeout и retry

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

### Ошибки и Best Practices

#### ❌ НЕПРАВИЛЬНО: Блокирующие операции в suspend функциях

```kotlin
suspend fun loadData(): String {
    Thread.sleep(1000) // ❌ Блокирует поток!
    return "data"
}
```

#### ✅ ПРАВИЛЬНО: Используйте suspend-friendly альтернативы

```kotlin
suspend fun loadData(): String {
    delay(1000) // ✅ Приостанавливает, не блокирует
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

#### ❌ НЕПРАВИЛЬНО: runBlocking в production коде

```kotlin
fun loadUserSync(id: Int): User {
    return runBlocking { // ❌ Блокирует поток!
        userRepository.getUser(id)
    }
}
```

#### ✅ ПРАВИЛЬНО: Используйте coroutine scope

```kotlin
class UserViewModel : ViewModel() {
    fun loadUser(id: Int) {
        viewModelScope.launch { // ✅ Асинхронно
            val user = userRepository.getUser(id)
            _user.value = user
        }
    }
}
```

#### ❌ НЕПРАВИЛЬНО: Ненужный suspend modifier

```kotlin
// Не делает ничего suspend - модификатор не нужен
suspend fun calculateSum(a: Int, b: Int): Int {
    return a + b
}
```

#### ✅ ПРАВИЛЬНО: suspend только если действительно приостанавливает

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

### Suspend функции в интерфейсах

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

### Suspend функции с Flow

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

### Тестирование suspend функций

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

### Продвинутые паттерны

#### 1. Suspend lazy initialization

```kotlin
class ExpensiveResource {
    private val _data = lazy {
        // ❌ Проблема: lazy не поддерживает suspend
        expensiveInitialization()
    }
}

// ✅ Решение: suspend lazy
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

#### 2. Suspend property delegation

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

#### 3. Resource cleanup с использованием suspend

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

### Производительность suspend функций

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

### Suspend функции и inline

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

### Частые ошибки

#### 1. Забыли обработать отмену

```kotlin
// ❌ НЕПРАВИЛЬНО
suspend fun longRunningTask() {
    repeat(1000) {
        processItem(it) // Не проверяет отмену!
        Thread.sleep(100)
    }
}

// ✅ ПРАВИЛЬНО
suspend fun longRunningTask() {
    repeat(1000) {
        ensureActive() // Проверяет отмену
        processItem(it)
        delay(100) // delay тоже проверяет отмену
    }
}
```

#### 2. Неправильный exception handling

```kotlin
// ❌ НЕПРАВИЛЬНО - глотает CancellationException
suspend fun fetchData() {
    try {
        apiService.getData()
    } catch (e: Exception) { // Ловит и CancellationException!
        logError(e)
    }
}

// ✅ ПРАВИЛЬНО - пробрасывает CancellationException
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
