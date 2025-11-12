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
related: [c-kotlin, c-coroutines, q-destructuring-declarations--kotlin--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [concurrency, continuation, coroutines, difficulty/medium, kotlin, suspend-functions]
---

# Вопрос (RU)

> Объясните, как работают suspend функции в корутинах Kotlin. Что делает ключевое слово `suspend`?

# Question (EN)

> Explain how suspend functions work in Kotlin coroutines. What does the `suspend` keyword do?

## Ответ (RU)

**Suspend функции** — это функции, которые могут приостанавливать выполнение без обязательной блокировки потоков. Ключевое слово `suspend` помечает функцию, чьё выполнение может быть приостановлено и возобновлено позже с помощью механизма корутин. Важно: `suspend` само по себе не гарантирует неблокирующее поведение — оно лишь позволяет интегрировать функцию в корутинную модель и использовать точки приостановки.

Когда в suspend функции есть точки приостановки (вызовы других suspend функций, таких как `delay`, `withContext` и т.п.), компилятор (концептуально) переписывает её в **машину состояний** на основе Continuation Passing Style (CPS), чтобы уметь приостанавливать и возобновлять выполнение.

### Что делает `suspend`

```kotlin
// Обычная функция — блокирует поток
fun loadUser(id: Int): User {
    Thread.sleep(1000) // Блокирует поток!
    return database.getUser(id)
}

// Suspend функция — может не блокировать поток при использовании неблокирующих suspend-API
suspend fun loadUser(id: Int): User {
    delay(1000) // Приостанавливает корутину, поток освобождается
    return database.getUser(id)
}
```

Ключевые отличия:
- Обычная функция выполняется до конца на текущем потоке; блокирующие вызовы (например, `Thread.sleep()`) блокируют поток.
- Suspend функция может останавливаться в точках приостановки, не блокируя поток, если использует корректные неблокирующие suspend-API или смену контекста. При этом внутри `suspend` функции всё ещё можно заблокировать поток, если вызвать блокирующий код напрямую, поэтому `suspend` — это не автоматическая магия.

### Правила использования suspend функций

```kotlin
class UserRepository {
    // Suspend функцию можно вызывать из другой suspend функции
    suspend fun getUser(id: Int): User {
        return apiService.fetchUser(id) // fetchUser тоже suspend
    }

    // Или из корутинного скоупа
    fun loadUserInBackground(id: Int) {
        viewModelScope.launch {
            val user = getUser(id) // OK внутри корутины
        }
    }

    // НЕЛЬЗЯ вызывать напрямую из обычной функции без корутины / runBlocking
    fun getUserSync(id: Int): User {
        return getUser(id) // Ошибка компиляции!
    }
}
```

3 способа вызывать suspend функции:
1. Из другой suspend функции
2. Из корутинных билдров (`launch`, `async` и т.д.)
3. Из `runBlocking` на границах (например, `main`, тесты)

### Как suspend работает под капотом

Компилятор Kotlin реализует suspend функции через **CPS** и при наличии точек приостановки концептуально преобразует их в **машину состояний**.

```kotlin
// Код, который вы пишете:
suspend fun loginUser(email: String, password: String): User {
    val token = authenticate(email, password)  // точка приостановки 1
    val user = fetchUserData(token)            // точка приостановки 2
    return user
}

// Концептуально сгенерированный код (сильно упрощено, иллюстрация):
fun loginUser(
    email: String,
    password: String,
    continuation: Continuation<User>
): Any? {
    val stateMachine = continuation as? LoginUserStateMachine
        ?: LoginUserStateMachine(continuation)

    return when (stateMachine.label) {
        0 -> {
            stateMachine.label = 1
            val result = authenticate(email, password, stateMachine)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            stateMachine.token = result as String
            // Переход логики к следующему состоянию
            stateMachine.label = 1
            loginUser(email, password, stateMachine)
        }
        1 -> {
            val token = stateMachine.token
            stateMachine.label = 2
            val result = fetchUserData(token, stateMachine)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            result as User
        }
        else -> error("Already completed")
    }
}
```

Что здесь важно (концептуально):
1. Suspend функция с точками приостановки представляется как машина состояний с метками.
2. Параметр `Continuation<T>` хранит контекст возобновления и текущее состояние.
3. В точке приостановки функция может вернуть `COROUTINE_SUSPENDED`, управление уходит рантайму.
4. После завершения асинхронной операции вызывается `continuation.resumeWith(result)`, что приводит к возобновлению машины состояний в нужном месте.
5. Конкретный сгенерированный код зависит от версии компилятора и детали следует воспринимать как модель, а не точную реализацию.

### `Continuation` — что это такое?

```kotlin
// Continuation представляет "оставшуюся" часть вычисления
public interface Continuation<in T> {
    public val context: CoroutineContext
    public fun resumeWith(result: Result<T>)
}

// Утилитные функции (stdlib)
fun <T> Continuation<T>.resume(value: T)
fun <T> Continuation<T>.resumeWithException(exception: Throwable)
```

### Пример использования Continuation API

```kotlin
// Оборачиваем callback API в suspend функцию
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
        val user = fetchUserFromCallback(id) // Выглядит синхронно
        println("Loaded: ${user.name}")
    } catch (e: Exception) {
        println("Error: ${e.message}")
    }
}
```

### `suspendCoroutine` vs `suspendCancellableCoroutine`

```kotlin
// НЕОТМЕНЯЕМО: работа не отменяется при отмене корутины
suspend fun downloadFile(url: String): File = suspendCoroutine { continuation ->
    val call = networkClient.download(url, object : DownloadCallback {
        override fun onComplete(file: File) {
            continuation.resume(file)
        }

        override fun onError(error: Exception) {
            continuation.resumeWithException(error)
        }
    })
    // Если корутина отменена, запрос всё равно продолжится.
}

// ОТМЕНЯЕМО — предпочтительный вариант для долгих операций
suspend fun downloadFile(url: String): File = suspendCancellableCoroutine { continuation ->
    val call = networkClient.download(url, object : DownloadCallback {
        override fun onComplete(file: File) {
            if (continuation.isActive) {
                continuation.resume(file)
            }
        }

        override fun onError(error: Exception) {
            if (continuation.isActive) {
                continuation.resumeWithException(error)
            }
        }
    })

    // Реакция на отмену корутины
    continuation.invokeOnCancellation {
        call.cancel()
    }
}
```

Рекомендация: для отменяемых операций предпочитайте `suspendCancellableCoroutine`.

### Suspend функции и потоки

```kotlin
suspend fun processData() {
    println("Start: ${Thread.currentThread().name}")

    delay(100) // точка приостановки

    println("After delay: ${Thread.currentThread().name}")

    withContext(Dispatchers.IO) { // приостановка + смена контекста
        println("In IO: ${Thread.currentThread().name}")
    }

    println("End: ${Thread.currentThread().name}")
}

// Возможный вывод:
// Start: main
// After delay: main (может быть тот же или другой поток того же диспетчера)
// In IO: DefaultDispatcher-worker-1
// End: main
```

Важно: после точки приостановки корутина может возобновиться на другом потоке, в зависимости от диспетчера и контекста.

### Реальные примеры suspend функций

#### 1. Сетевые запросы (Retrofit)

```kotlin
interface UserApi {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: Int): User

    @POST("users")
    suspend fun createUser(@Body user: UserRequest): User
}

// Пример обёртки с Result-подобным типом
sealed class UserResult<out T> {
    data class Success<T>(val data: T) : UserResult<T>()
    data class Failure(val exception: Throwable) : UserResult<Nothing>()
}

class UserRepository(private val api: UserApi) {
    suspend fun getUser(id: Int): UserResult<User> = try {
        UserResult.Success(api.getUser(id))
    } catch (e: Exception) {
        UserResult.Failure(e)
    }
}

// Использование во ViewModel
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    fun loadUser(id: Int) {
        viewModelScope.launch {
            _isLoading.value = true

            when (val result = repository.getUser(id)) {
                is UserResult.Success -> _user.value = result.data
                is UserResult.Failure -> _error.value = result.exception.message
            }

            _isLoading.value = false
        }
    }
}
```

#### 2. Операции с базой данных (Room)

```kotlin
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUserById(id: Int): User?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User)

    @Query("SELECT * FROM users")
    fun observeUsers(): Flow<List<User>> // `Flow` интегрируется с suspend через операторы и collect
}

class LocalUserRepository(private val dao: UserDao) {
    suspend fun saveUser(user: User) {
        dao.insertUser(user)
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
    val isAvailable = checkEmailAvailability(email)
    if (!isAvailable) {
        throw EmailAlreadyExistsException()
    }

    val userId = createAccount(email, password)
    val profile = createProfile(userId, name)
    sendWelcomeEmail(email)

    return User(userId, email, profile)
}

suspend fun checkEmailAvailability(email: String): Boolean {
    delay(200)
    return apiService.checkEmail(email)
}
```

#### 4. Параллельные операции с `async`

```kotlin
suspend fun loadDashboardData(): DashboardData = coroutineScope {
    val userDeferred = async { userApi.getUser() }
    val statsDeferred = async { statsApi.getStats() }
    val notificationsDeferred = async { notificationsApi.getUnread() }

    DashboardData(
        user = userDeferred.await(),
        stats = statsDeferred.await(),
        notifications = notificationsDeferred.await()
    )
}

// Время ≈ максимум из трёх запросов, а не сумма
```

#### 5. Timeout и Retry

```kotlin
suspend fun fetchWithTimeout(url: String): String {
    return withTimeout(5000) {
        httpClient.get(url)
    }
}

suspend fun fetchWithRetry(url: String, maxAttempts: Int = 3): String {
    repeat(maxAttempts - 1) { attempt ->
        try {
            return httpClient.get(url)
        } catch (e: IOException) {
            println("Attempt ${attempt + 1} failed, retrying...")
            delay(1000L * (attempt + 1))
        }
    }
    return httpClient.get(url)
}
```

### Ошибки и Best Practices

#### Неправильно: блокирующие операции в suspend функциях

```kotlin
suspend fun loadData(): String {
    Thread.sleep(1000) // Блокирует поток и игнорирует отмену
    return "data"
}
```

#### Правильно: используйте suspend-friendly альтернативы

```kotlin
suspend fun loadData(): String {
    delay(1000) // Приостанавливает, не блокирует
    return "data"
}

suspend fun processImage(bitmap: Bitmap): Bitmap {
    return withContext(Dispatchers.Default) {
        applyFilters(bitmap)
    }
}
```

#### Неправильно: `runBlocking` в production

```kotlin
fun loadUserSync(id: Int): User {
    return runBlocking {
        userRepository.getUser(id)
    }
}
```

#### Правильно: используйте `CoroutineScope` (а `runBlocking` — только на границах, например, в `main` или тестах)

```kotlin
class UserViewModel : ViewModel() {
    fun loadUser(id: Int) {
        viewModelScope.launch {
            val user = userRepository.getUser(id)
            _user.value = user
        }
    }
}
```

#### Неправильно: ненужный модификатор `suspend`

```kotlin
suspend fun calculateSum(a: Int, b: Int): Int {
    return a + b
}
```

#### Правильно: `suspend` только при реальной приостановке / асинхронной работе

```kotlin
fun calculateSum(a: Int, b: Int): Int {
    return a + b
}

suspend fun loadAndCalculate(): Int {
    val a = fetchA()
    val b = fetchB()
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
            local.fetch()
        }
    }

    override suspend fun save(data: User) {
        local.save(data)
        remote.save(data)
    }
}
```

### Suspend функции с `Flow`

```kotlin
interface UserRepository {
    // Возвращает `Flow` — НЕ suspend функция
    fun observeUsers(): Flow<List<User>>

    // Suspend функция — разовая операция
    suspend fun refreshUsers()
}

class UserRepositoryImpl(
    private val api: UserApi,
    private val dao: UserDao
) : UserRepository {
    override fun observeUsers(): Flow<List<User>> {
        return dao.observeUsers()
    }

    override suspend fun refreshUsers() {
        val users = api.getUsers()
        dao.insertAll(users)
    }
}

class UsersViewModel(private val repository: UserRepository) : ViewModel() {
    val users = repository.observeUsers()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun refresh() {
        viewModelScope.launch {
            try {
                repository.refreshUsers()
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
    fun `test getUser returns user`() = runTest {
        val repository = UserRepository(fakeApi)

        val user = repository.getUser(1)

        assertEquals("Alice", user.name)
    }

    @Test
    fun `test parallel loading`() = runTest {
        val repository = UserRepository(fakeApi)

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

#### 1. Suspend-ленивая инициализация

```kotlin
class ExpensiveResource2 {
    private val mutex = Mutex()
    private var _data: Data? = null

    suspend fun getData(): Data {
        if (_data == null) {
            mutex.withLock {
                if (_data == null) {
                    _data = expensiveInitialization()
                }
            }
        }
        return _data!!
    }
}
```

#### 2. Suspend и делегирование свойств (предупреждение)

```kotlin
class UserCache {
    private val cache = mutableMapOf<Int, User>()

    // Важно: operator getValue/setValue не могут быть suspend в стандартном синтаксисе.
    // Реальные решения делают явные suspend-функции вместо делегатов.
}
```

#### 3. Освобождение ресурсов с использованием suspend

```kotlin
suspend fun <T : Closeable, R> T.useSuspending(block: suspend (T) -> R): R {
    return try {
        block(this)
    } finally {
        close()
    }
}

suspend fun processFile(path: String) {
    FileInputStream(path).useSuspending { stream ->
        val data = readSuspending(stream)
        processSuspending(data)
    }
}
```

### Производительность suspend функций

```kotlin
@Benchmark
fun regularFunction(): Int {
    return 42
}

@Benchmark
suspend fun suspendFunction(): Int {
    return 42 // Нет точек приостановки
}

suspend fun withSuspension(): Int {
    delay(1)
    return 42
}
```

Выводы:
- Сам по себе модификатор `suspend` почти бесплатный.
- Оверхед появляется при реальном приостановлении (`delay`, `withContext` и т.д.).
- Концептуально машина состояний важна при наличии точек приостановки; конкретные детали реализации зависят от компилятора.

### Suspend функции и `inline`

```kotlin
inline suspend fun <T> measureTime(
    block: suspend () -> T
): Pair<T, Long> {
    val start = System.currentTimeMillis()
    val result = block()
    val duration = System.currentTimeMillis() - start
    return result to duration
}

suspend fun example() {
    val (user, time) = measureTime {
        userRepository.getUser(1)
    }
    println("Loaded in ${time}ms")
}
```

### Частые ошибки

#### 1. Игнорирование отмены

```kotlin
suspend fun longRunningTaskWrong() {
    repeat(1000) {
        processItem(it)
        Thread.sleep(100)
    }
}

suspend fun longRunningTask() {
    repeat(1000) {
        ensureActive()
        processItem(it)
        delay(100)
    }
}
```

#### 2. Неправильная обработка исключений

```kotlin
suspend fun fetchDataWrong() {
    try {
        apiService.getData()
    } catch (e: Exception) {
        logError(e)
    }
}

suspend fun fetchData() {
    try {
        apiService.getData()
    } catch (e: CancellationException) {
        throw e
    } catch (e: Exception) {
        logError(e)
    }
}
```

## Answer (EN)

Suspend functions are functions that can suspend execution without necessarily blocking threads. The `suspend` keyword marks a function whose execution may be paused and resumed later using the coroutine machinery. Importantly, `suspend` by itself does not guarantee non-blocking behavior; it enables integration with the coroutine model and use of suspension points.

When a suspend function contains at least one suspension point (calls another suspend function such as `delay`, `withContext`, etc.), the compiler (conceptually) rewrites it into a state machine so it can be paused and resumed.

### What the `suspend` keyword does

```kotlin
// Regular function - blocks thread
fun loadUser(id: Int): User {
    Thread.sleep(1000) // Blocks thread
    return database.getUser(id)
}

// Suspend function - can avoid blocking when using non-blocking suspend APIs
suspend fun loadUser(id: Int): User {
    delay(1000) // Suspends coroutine, underlying thread is released
    return database.getUser(id)
}
```

Key points:
- Regular function: runs to completion on the current thread; blocking calls like `Thread.sleep()` block the thread.
- Suspend function: can pause at suspension points without blocking the underlying thread when using proper suspend/non-blocking APIs or appropriate dispatchers. You can still block a thread inside a suspend function if you call blocking code directly, so `suspend` is not magic by itself.

### Rules for using suspend functions

```kotlin
class UserRepository {
    // Suspend function can be called from another suspend function
    suspend fun getUser(id: Int): User {
        return apiService.fetchUser(id)
    }

    // Or from a coroutine scope
    fun loadUserInBackground(id: Int) {
        viewModelScope.launch {
            val user = getUser(id) // OK inside coroutine
        }
    }

    // Cannot call directly from a regular function without a coroutine / runBlocking
    fun getUserSync(id: Int): User {
        return getUser(id) // Compilation error
    }
}
```

Ways to call suspend functions:
1. From another suspend function
2. From coroutine builders (`launch`, `async`, etc.)
3. From `runBlocking` at boundaries (e.g., `main`, tests)

### How suspend works under the hood

The Kotlin compiler implements suspend functions using Continuation Passing Style (CPS) and, when there are suspension points, conceptually transforms them into state machines.

```kotlin
// Code you write
suspend fun loginUser(email: String, password: String): User {
    val token = authenticate(email, password)
    val user = fetchUserData(token)
    return user
}

// Conceptual generated code (highly simplified, illustrative only)
fun loginUser(
    email: String,
    password: String,
    continuation: Continuation<User>
): Any? {
    val stateMachine = continuation as? LoginUserStateMachine
        ?: LoginUserStateMachine(continuation)

    return when (stateMachine.label) {
        0 -> {
            stateMachine.label = 1
            val result = authenticate(email, password, stateMachine)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            stateMachine.token = result as String
            // Continue with next state
            stateMachine.label = 1
            loginUser(email, password, stateMachine)
        }
        1 -> {
            val token = stateMachine.token
            stateMachine.label = 2
            val result = fetchUserData(token, stateMachine)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            result as User
        }
        else -> error("Already completed")
    }
}
```

Conceptually:
- Suspend functions with suspension points are represented as labeled state machines.
- A `Continuation<T>` parameter captures where and how to resume and holds the state.
- At suspension, they may return `COROUTINE_SUSPENDED`, handing control to the runtime.
- On completion of async work, `continuation.resumeWith(result)` resumes execution at the appropriate state.
- The exact generated code is compiler-version-specific; treat this as a mental model, not a decompiled reality.

### Continuation - what is it?

```kotlin
public interface Continuation<in T> {
    public val context: CoroutineContext
    public fun resumeWith(result: Result<T>)
}

fun <T> Continuation<T>.resume(value: T)
fun <T> Continuation<T>.resumeWithException(exception: Throwable)
```

### Example using Continuation API

```kotlin
suspend fun fetchUserFromCallback(id: Int): User = suspendCoroutine { continuation ->
    userApi.getUser(id, object : Callback<User> {
        override fun onSuccess(user: User) {
            continuation.resume(user)
        }

        override fun onError(error: Exception) {
            continuation.resumeWithException(error)
        }
    })
}

suspend fun loadUser(id: Int) {
    try {
        val user = fetchUserFromCallback(id)
        println("Loaded: ${user.name}")
    } catch (e: Exception) {
        println("Error: ${e.message}")
    }
}
```

### `suspendCoroutine` vs `suspendCancellableCoroutine`

```kotlin
// Non-cancellable: work continues even if coroutine is cancelled
suspend fun downloadFile(url: String): File = suspendCoroutine { continuation ->
    val call = networkClient.download(url, object : DownloadCallback {
        override fun onComplete(file: File) {
            continuation.resume(file)
        }

        override fun onError(error: Exception) {
            continuation.resumeWithException(error)
        }
    })
}

// Cancellable — preferred for long-running operations
suspend fun downloadFile(url: String): File = suspendCancellableCoroutine { continuation ->
    val call = networkClient.download(url, object : DownloadCallback {
        override fun onComplete(file: File) {
            if (continuation.isActive) {
                continuation.resume(file)
            }
        }

        override fun onError(error: Exception) {
            if (continuation.isActive) {
                continuation.resumeWithException(error)
            }
        }
    })

    // React to coroutine cancellation
    continuation.invokeOnCancellation {
        call.cancel()
    }
}
```

Guideline: prefer `suspendCancellableCoroutine` for cancellable work.

### Suspend functions and threads

```kotlin
suspend fun processData() {
    println("Start: ${Thread.currentThread().name}")

    delay(100)

    println("After delay: ${Thread.currentThread().name}")

    withContext(Dispatchers.IO) {
        println("In IO: ${Thread.currentThread().name}")
    }

    println("End: ${Thread.currentThread().name}")
}
```

Important: after suspension a coroutine may resume on a different thread depending on its dispatcher and context.

### Real examples of suspend functions

#### 1. Network requests (Retrofit)

```kotlin
interface UserApi {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: Int): User

    @POST("users")
    suspend fun createUser(@Body user: UserRequest): User
}

sealed class UserResult<out T> {
    data class Success<T>(val data: T) : UserResult<T>()
    data class Failure(val exception: Throwable) : UserResult<Nothing>()
}

class UserRepository(private val api: UserApi) {
    suspend fun getUser(id: Int): UserResult<User> = try {
        UserResult.Success(api.getUser(id))
    } catch (e: Exception) {
        UserResult.Failure(e)
    }
}

class UserViewModel(private val repository: UserRepository) : ViewModel() {
    fun loadUser(id: Int) {
        viewModelScope.launch {
            _isLoading.value = true

            when (val result = repository.getUser(id)) {
                is UserResult.Success -> _user.value = result.data
                is UserResult.Failure -> _error.value = result.exception.message
            }

            _isLoading.value = false
        }
    }
}
```

#### 2. Database operations (Room)

```kotlin
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUserById(id: Int): User?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User)

    @Query("SELECT * FROM users")
    fun observeUsers(): Flow<List<User>>
}

class LocalUserRepository(private val dao: UserDao) {
    suspend fun saveUser(user: User) {
        dao.insertUser(user)
    }

    suspend fun getUser(id: Int): User? {
        return dao.getUserById(id)
    }

    fun observeUsers(): Flow<List<User>> {
        return dao.observeUsers()
    }
}
```

#### 3. Sequential operations

```kotlin
suspend fun registerUser(
    email: String,
    password: String,
    name: String
): User {
    val isAvailable = checkEmailAvailability(email)
    if (!isAvailable) {
        throw EmailAlreadyExistsException()
    }

    val userId = createAccount(email, password)
    val profile = createProfile(userId, name)
    sendWelcomeEmail(email)

    return User(userId, email, profile)
}

suspend fun checkEmailAvailability(email: String): Boolean {
    delay(200)
    return apiService.checkEmail(email)
}
```

#### 4. Parallel operations with `async`

```kotlin
suspend fun loadDashboardData(): DashboardData = coroutineScope {
    val userDeferred = async { userApi.getUser() }
    val statsDeferred = async { statsApi.getStats() }
    val notificationsDeferred = async { notificationsApi.getUnread() }

    DashboardData(
        user = userDeferred.await(),
        stats = statsDeferred.await(),
        notifications = notificationsDeferred.await()
    )
}

// Total time ≈ max of the calls, not the sum
```

#### 5. Timeout and Retry

```kotlin
suspend fun fetchWithTimeout(url: String): String {
    return withTimeout(5000) {
        httpClient.get(url)
    }
}

suspend fun fetchWithRetry(url: String, maxAttempts: Int = 3): String {
    repeat(maxAttempts - 1) { attempt ->
        try {
            return httpClient.get(url)
        } catch (e: IOException) {
            println("Attempt ${attempt + 1} failed, retrying...")
            delay(1000L * (attempt + 1))
        }
    }
    return httpClient.get(url)
}
```

### Errors and best practices

#### Wrong: blocking operations in suspend functions

```kotlin
suspend fun loadData(): String {
    Thread.sleep(1000)
    return "data"
}
```

#### Correct: use suspend-friendly alternatives

```kotlin
suspend fun loadData(): String {
    delay(1000)
    return "data"
}

suspend fun processImage(bitmap: Bitmap): Bitmap {
    return withContext(Dispatchers.Default) {
        applyFilters(bitmap)
    }
}
```

#### Wrong: `runBlocking` in production

```kotlin
fun loadUserSync(id: Int): User {
    return runBlocking {
        userRepository.getUser(id)
    }
}
```

#### Correct: use `CoroutineScope` (and keep `runBlocking` for top-level boundaries, e.g., `main`, tests)

```kotlin
class UserViewModel : ViewModel() {
    fun loadUser(id: Int) {
        viewModelScope.launch {
            val user = userRepository.getUser(id)
            _user.value = user
        }
    }
}
```

#### Wrong: unnecessary `suspend`

```kotlin
suspend fun calculateSum(a: Int, b: Int): Int {
    return a + b
}
```

#### Correct: `suspend` only when needed

```kotlin
fun calculateSum(a: Int, b: Int): Int {
    return a + b
}

suspend fun loadAndCalculate(): Int {
    val a = fetchA()
    val b = fetchB()
    return calculateSum(a, b)
}
```

#### Cancellation and exceptions

```kotlin
suspend fun longRunningTaskWrong() {
    repeat(1000) {
        processItem(it)
        Thread.sleep(100)
    }
}

suspend fun longRunningTask() {
    repeat(1000) {
        ensureActive()
        processItem(it)
        delay(100)
    }
}

suspend fun fetchDataWrong() {
    try {
        apiService.getData()
    } catch (e: Exception) {
        logError(e)
    }
}

suspend fun fetchData() {
    try {
        apiService.getData()
    } catch (e: CancellationException) {
        throw e
    } catch (e: Exception) {
        logError(e)
    }
}
```

### Advanced patterns

#### 1. Suspend-lazy initialization

```kotlin
class ExpensiveResource2 {
    private val mutex = Mutex()
    private var _data: Data? = null

    suspend fun getData(): Data {
        if (_data == null) {
            mutex.withLock {
                if (_data == null) {
                    _data = expensiveInitialization()
                }
            }
        }
        return _data!!
    }
}
```

#### 2. Suspend and property delegation (warning)

```kotlin
class UserCache {
    private val cache = mutableMapOf<Int, User>()

    // operator getValue/setValue cannot be suspend in standard syntax;
    // real-world solutions use explicit suspend functions instead of delegates.
}
```

#### 3. Resource cleanup with suspend

```kotlin
suspend fun <T : Closeable, R> T.useSuspending(block: suspend (T) -> R): R {
    return try {
        block(this)
    } finally {
        close()
    }
}

suspend fun processFile(path: String) {
    FileInputStream(path).useSuspending { stream ->
        val data = readSuspending(stream)
        processSuspending(data)
    }
}
```

### Performance

```kotlin
@Benchmark
fun regularFunction(): Int {
    return 42
}

@Benchmark
suspend fun suspendFunction(): Int {
    return 42 // No suspension points
}

suspend fun withSuspension(): Int {
    delay(1)
    return 42
}
```

Key points:
- The `suspend` modifier itself is almost free.
- Overhead appears at real suspension points (`delay`, `withContext`, etc.).
- Treat the state machine transformation as the conceptual mechanism used when suspension is involved; exact details are compiler-specific.

### Common mistakes

- Blocking inside suspend functions (e.g. `Thread.sleep()` instead of `delay()` or proper dispatcher).
- Ignoring cancellation (no `ensureActive()`, never checking `isActive`).
- Swallowing `CancellationException` in broad `catch` blocks.
- Overusing `runBlocking` outside of top-level boundaries.
- Marking trivially synchronous functions as `suspend`.

## Дополнительные вопросы (RU)

- В чём отличие подхода с suspend функциями от традиционных callback API в Java?
- Когда на практике стоит выносить операции в suspend функции и корутины?
- Какие типичные ошибки при работе с suspend функциями нужно избегать?

## Follow-ups

- What are the key differences between this and Java-style callbacks or futures?
- When would you use suspend functions and coroutines in real projects?
- What are common pitfalls to avoid when designing suspend APIs?

## Ссылки (RU)

- Официальная документация Kotlin Coroutines: https://kotlinlang.org/docs/coroutines-overview.html
- Обзор языка Kotlin: https://kotlinlang.org/docs/home.html
- [[c-kotlin]]
- [[c-coroutines]]

## References

- Kotlin Coroutines documentation: https://kotlinlang.org/docs/coroutines-overview.html
- Kotlin language docs: https://kotlinlang.org/docs/home.html
- [[c-kotlin]]
- [[c-coroutines]]

## Связанные вопросы (RU)

- [[q-reified-type-parameters--kotlin--medium]]
- [[q-destructuring-declarations--kotlin--medium]]

## Related Questions

- [[q-reified-type-parameters--kotlin--medium]]
- [[q-destructuring-declarations--kotlin--medium]]
