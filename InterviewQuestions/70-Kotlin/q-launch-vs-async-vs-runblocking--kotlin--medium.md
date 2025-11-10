---
id: kotlin-162
title: "Launch Vs Async Vs Runblocking / Launch против Async против Runblocking"
aliases: [Async, Coroutine Builders, Launch, RunBlocking, Запуск корутин]
topic: kotlin
subtopics: [coroutines, coroutine-builders, concurrency]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-coroutines, q-coroutine-memory-leak-detection--kotlin--hard, q-executor-service-java--kotlin--medium, q-list-vs-sequence--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [async, concurrency, coroutines, difficulty/medium, kotlin, launch, runblocking]
---
# Вопрос (RU)
> В чём разница между корутинными билдерами `launch`, `async` и `runBlocking`?

# Question (EN)
> What's the difference between `launch`, `async`, and `runBlocking` coroutine builders?

## Ответ (RU)

**Launch**, **async**, и **runBlocking** - три основных способа запуска корутин, каждый с разным назначением:

| Builder | Возвращает | Блокирует поток | Результат | Use case |
|---------|------------|-----------------|-----------|----------|
| **launch** | `Job` | Нет | Нет (fire-and-forget) | Фоновые задачи без результата или с результатом через побочные эффекты |
| **async** | `Deferred<T>` | Нет | Да через `await()` | Параллельные вычисления с результатом |
| **runBlocking** | `T` | **ДА** | Да напрямую | Тесты, `main` функция, блокирующий bridge к suspend-коду |

### Launch - Fire and Forget

```kotlin
fun loadUserInBackground() {
    viewModelScope.launch {
        // Запускается асинхронно, результат не возвращается напрямую
        val user = userRepository.getUser(1)
        _user.value = user
    }
    // Функция возвращается СРАЗУ, не дожидаясь завершения корутины
}
```

**Характеристики launch**:
- Не возвращает вычисленный результат напрямую
- Возвращает `Job` для управления lifecycle
- Не блокирует вызывающий поток
- Необработанные исключения отменяют родительский scope и обрабатываются его `CoroutineExceptionHandler`
- Use case: фоновая работа, обновление UI, side effects

#### Примеры Использования Launch

```kotlin
class UserViewModel : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users = _users.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    private val _error = MutableStateFlow<String?>(null)

    // 1. Загрузка данных
    fun loadUsers() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val users = userRepository.getUsers()
                _users.value = users
            } catch (e: Exception) {
                _error.value = e.message
            } finally {
                _isLoading.value = false
            }
        }
    }

    // 2. Периодическое обновление
    fun startAutoRefresh() {
        viewModelScope.launch {
            while (isActive) {
                loadUsers()
                delay(30_000) // Каждые 30 секунд
            }
        }
    }

    // 3. Несколько независимых задач
    fun loadDashboard() {
        viewModelScope.launch { loadUsers() }
        viewModelScope.launch { loadStats() }
        viewModelScope.launch { loadNotifications() }
        // Все три запускаются параллельно
    }
}
```

#### Job Management С Launch

```kotlin
class DownloadManager {
    private var downloadJob: Job? = null

    fun startDownload(url: String) {
        // Отменяем предыдущую загрузку если есть
        downloadJob?.cancel()

        downloadJob = CoroutineScope(Dispatchers.IO).launch {
            try {
                val file = downloadFile(url)
                withContext(Dispatchers.Main) {
                    showSuccess(file)
                }
            } catch (e: CancellationException) {
                // Загрузка отменена
                withContext(Dispatchers.Main) {
                    showCancelled()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    showError(e)
                }
            }
        }
    }

    fun cancelDownload() {
        downloadJob?.cancel()
        downloadJob = null
    }

    fun isDownloading(): Boolean {
        return downloadJob?.isActive == true
    }
}
```

### Async - Параллельные Вычисления С Результатом

```kotlin
suspend fun loadDashboard(): DashboardData = coroutineScope {
    // Запускаем три запроса параллельно
    val userDeferred = async { userApi.getUser() }
    val statsDeferred = async { statsApi.getStats() }
    val notificationsDeferred = async { notificationsApi.getNotifications() }

    // Ждем всех результатов
    DashboardData(
        user = userDeferred.await(),
        stats = statsDeferred.await(),
        notifications = notificationsDeferred.await()
    )
}
```

**Характеристики async**:
- Возвращает результат через `Deferred<T>`
- Можно получить результат через `await()`
- Не блокирует вызывающий поток до вызова `await()`
- Исключения выбрасываются при вызове `await()` (и при завершении scope, если результат так и не запрошен)
- Use case: параллельные вычисления, где нужен результат

#### Примеры Использования Async

```kotlin
// 1. Параллельная загрузка нескольких ресурсов
suspend fun loadUserProfile(userId: Int): UserProfile = coroutineScope {
    val userDeferred = async { userRepository.getUser(userId) }
    val postsDeferred = async { postsRepository.getUserPosts(userId) }
    val followersDeferred = async { socialRepository.getFollowers(userId) }

    // Все три запроса идут параллельно
    // Время ~ max(user, posts, followers), не сумма
    UserProfile(
        user = userDeferred.await(),
        posts = postsDeferred.await(),
        followers = followersDeferred.await()
    )
}

// 2. Parallel map
suspend fun loadMultipleUsers(ids: List<Int>): List<User> = coroutineScope {
    ids.map { id ->
        async { userRepository.getUser(id) }
    }.awaitAll() // Ждем всех одновременно
}

// 3. First successful result
suspend fun loadFromMultipleSources(): Data = coroutineScope {
    val source1 = async { loadFromServer1() }
    val source2 = async { loadFromServer2() }
    val source3 = async { loadFromCache() }

    // Возвращаем первый успешный результат
    select<Data> {
        source1.onAwait { it }
        source2.onAwait { it }
        source3.onAwait { it }
    }
}
```

#### Async С Обработкой Ошибок

```kotlin
suspend fun loadWithFallback(): UserData = coroutineScope {
    val primaryDeferred = async {
        try {
            primaryApi.loadData()
        } catch (e: Exception) {
            null
        }
    }

    val secondaryDeferred = async {
        try {
            secondaryApi.loadData()
        } catch (e: Exception) {
            null
        }
    }

    // Используем первый успешный результат
    primaryDeferred.await() ?: secondaryDeferred.await() ?: cachedData
}
```

### runBlocking - Блокирующий Мост

```kotlin
fun main() = runBlocking { // Блокирует main поток
    val user = userRepository.getUser(1)
    println("User: $user")
} // main поток разблокируется только здесь
```

**Характеристики runBlocking**:
- Возвращает результат напрямую
- **БЛОКИРУЕТ** вызывающий поток до завершения
- Для тестов, `main` функции и точечных блокирующих мостов к suspend-коду; в обычном production-коде следует избегать
- Use case: мост между синхронным и асинхронным кодом

#### Когда Использовать runBlocking

```kotlin
// 1. Main функция
fun main() = runBlocking {
    val app = MyApplication()
    app.start()
}

// 2. Unit тесты (но лучше runTest)
@Test
fun `test user loading`() = runBlocking {
    val repository = UserRepository()
    val user = repository.getUser(1)
    assertEquals("Alice", user.name)
}

// 3. Migration legacy code
class LegacyService {
    fun getUserSync(id: Int): User = runBlocking {
        // Временное решение для интеграции с suspend функциями
        userRepository.getUser(id)
    }
}

// Никогда не используйте в Android UI коде
class BadViewModel : ViewModel() {
    fun loadUser(id: Int) {
        val user = runBlocking { // ПЛОХО: блокирует UI поток
            userRepository.getUser(id)
        }
        _user.value = user
    }
}
```

### Сравнение На Реальном Примере

```kotlin
class DataLoader(
    private val repository: DataRepository,
    private val scope: CoroutineScope
) {
    // launch - результат не возвращается напрямую
    fun loadWithLaunch() {
        scope.launch {
            val data = repository.loadData()
            // Как получить data наружу? Через callback/StateFlow и т.п.
        }
        // Возвращается сразу, data еще не загружена
    }

    // async - можно получить результат
    fun loadWithAsync(): Deferred<Data> {
        return scope.async {
            repository.loadData()
        }
        // Возвращается Deferred<Data>, результат через await()
    }

    // runBlocking - блокирует поток
    fun loadWithRunBlocking(): Data {
        return runBlocking {
            repository.loadData()
        }
        // Возвращается только после загрузки, поток заблокирован
    }

    // Правильный подход - suspend функция
    suspend fun loadData(): Data {
        return repository.loadData()
    }
}

// Использование
class ViewModel {
    fun example() {
        // launch - fire and forget
        viewModelScope.launch {
            loader.loadWithLaunch() // Не можем получить результат
        }

        // async - получаем Deferred
        viewModelScope.launch {
            val deferred = loader.loadWithAsync()
            val data = deferred.await() // Получаем результат
        }

        // runBlocking - не делайте так в UI коде
        val data = loader.loadWithRunBlocking() // Блокирует текущий поток

        // Правильно - suspend функция
        viewModelScope.launch {
            val data2 = loader.loadData()
        }
    }
}
```

### Launch Vs Async - Когда Что Использовать

```kotlin
// НЕПРАВИЛЬНО - async без await()
viewModelScope.launch {
    async { loadUsers() } // Результат и возможные исключения игнорируются
    async { loadPosts() }
}

// ПРАВИЛЬНО - launch для fire-and-forget
viewModelScope.launch {
    launch { loadUsers() }
    launch { loadPosts() }
}

// НЕПРАВИЛЬНО - launch когда нужен результат
viewModelScope.launch {
    launch { userRepository.getUser(1) } // Как получить User?
}

// ПРАВИЛЬНО - async когда нужен результат
viewModelScope.launch {
    val user = async { userRepository.getUser(1) }.await()
}

// Или еще лучше - просто suspend вызов
viewModelScope.launch {
    val user = userRepository.getUser(1) // Последовательно
}
```

### Structured Concurrency

```kotlin
suspend fun loadAllData() = coroutineScope {
    // Все дочерние корутины должны завершиться перед return

    launch {
        loadUsers() // Дочерняя корутина 1
    }

    launch {
        loadPosts() // Дочерняя корутина 2
    }

    // coroutineScope ждет завершения ВСЕХ дочерних корутин
}

suspend fun computeResults() = coroutineScope {
    val result1 = async { compute1() }
    val result2 = async { compute2() }

    result1.await() + result2.await()
    // Возвращается только когда ОБА async завершены
}
```

### Exception Handling

```kotlin
// launch - исключения обрабатываются родительским scope
viewModelScope.launch {
    try {
        userRepository.getUser(1)
    } catch (e: Exception) {
        _error.value = e.message
    }
}

// async - исключения выбрасываются при await()
viewModelScope.launch {
    val deferred = async {
        userRepository.getUser(1) // Исключение не выбросится наружу здесь
    }

    try {
        val user = deferred.await() // Исключение выбросится здесь
    } catch (e: Exception) {
        _error.value = e.message
    }
}

// runBlocking - исключения выбрасываются синхронно
try {
    runBlocking {
        userRepository.getUser(1)
    }
} catch (e: Exception) {
    println("Error: ${e.message}")
}
```

### supervisorScope - Независимые Дочерние Корутины

```kotlin
// coroutineScope - одна ошибка отменяет все
suspend fun loadDataStrict() = coroutineScope {
    launch { loadUsers() }     // Если упадет -
    launch { loadPosts() }     // - все дочерние отменятся
    launch { loadComments() }
}

// supervisorScope - ошибки изолированы
suspend fun loadDataResilient() = supervisorScope {
    launch {
        try {
            loadUsers() // Если упадет - только эта корутина
        } catch (e: Exception) {
            logError(e)
        }
    }

    launch {
        try {
            loadPosts() // Продолжит работать даже если loadUsers упал
        } catch (e: Exception) {
            logError(e)
        }
    }
}
```

### Продвинутые Паттерны

#### 1. Timeout Для Async

```kotlin
suspend fun loadWithTimeout(): Data? = coroutineScope {
    val deferred = async { repository.loadData() }

    try {
        withTimeout(5000) {
            deferred.await()
        }
    } catch (e: TimeoutCancellationException) {
        deferred.cancel() // Отменяем корутину
        null
    }
}
```

#### 2. Retry Для Launch

```kotlin
fun loadUserWithRetry(id: Int) {
    viewModelScope.launch {
        repeat(3) { attempt ->
            try {
                val user = userRepository.getUser(id)
                _user.value = user
                return@launch // Успех - выходим
            } catch (e: Exception) {
                if (attempt == 2) throw e // Последняя попытка
                delay(1000L * (attempt + 1)) // Линейная задержка
            }
        }
    }
}
```

#### 3. Cancellable Async Работа

```kotlin
class ImageProcessor {
    private var processingJob: Job? = null

    fun processImage(bitmap: Bitmap) {
        processingJob?.cancel() // Отменяем предыдущую обработку

        processingJob = CoroutineScope(Dispatchers.Default).launch {
            val deferred = async {
                applyFilters(bitmap)
            }

            try {
                val result = deferred.await()
                withContext(Dispatchers.Main) {
                    showResult(result)
                }
            } catch (e: CancellationException) {
                // Processing cancelled
            }
        }
    }

    fun cancel() {
        processingJob?.cancel()
    }
}
```

### Performance Comparison

```kotlin
// Последовательное выполнение
suspend fun loadSequentially() {
    val user = userRepository.getUser(1)       // ~500ms
    val posts = postsRepository.getPosts(1)    // ~500ms
    val comments = commentsRepository.getComments(1) // ~500ms
    // Общее время: ~1500ms
}

// Параллельное с async
suspend fun loadInParallel() = coroutineScope {
    val userDeferred = async { userRepository.getUser(1) }      // ~500ms
    val postsDeferred = async { postsRepository.getPosts(1) }   // ~500ms
    val commentsDeferred = async { commentsRepository.getComments(1) } // ~500ms

    Triple(
        userDeferred.await(),
        postsDeferred.await(),
        commentsDeferred.await()
    )
    // Общее время: ~500ms (max из трех)
}

// Параллельное с launch - без прямого результата
fun loadWithLaunch() {
    scope.launch {
        launch { loadUsers() }
        launch { loadPosts() }
        launch { loadComments() }
        // Чтобы собрать результаты, используйте общий стейт/каналы и т.п.
    }
}
```

### Best Practices

#### 1. Используйте Launch Для Side Effects

```kotlin
// ПРАВИЛЬНО
viewModelScope.launch {
    analyticsService.logEvent("screen_viewed")
    cacheService.warmUpCache()
}
```

#### 2. Используйте Async Для Параллельных Вычислений

```kotlin
// ПРАВИЛЬНО
suspend fun calculateComplexResult() = coroutineScope {
    val part1 = async { calculatePart1() }
    val part2 = async { calculatePart2() }
    val part3 = async { calculatePart3() }

    combineResults(part1.await(), part2.await(), part3.await())
}
```

#### 3. Не Используйте runBlocking В Обычном Production-Коде

```kotlin
// НЕПРАВИЛЬНО (за исключением контролируемых точек входа/тестов)
fun loadUser(id: Int): User = runBlocking {
    userRepository.getUser(id)
}

// ПРАВИЛЬНО - сделайте suspend функцию
suspend fun loadUser(id: Int): User {
    return userRepository.getUser(id)
}

// Или используйте scope
fun loadUser(id: Int) {
    viewModelScope.launch {
        val user = userRepository.getUser(id)
        _user.value = user
    }
}
```

#### 4. Всегда await() Результаты Async

```kotlin
// НЕПРАВИЛЬНО - async без await
scope.launch {
    async { loadData() } // Результат и исключения потеряны
}

// ПРАВИЛЬНО
scope.launch {
    val data = async { loadData() }.await()
}

// Или используйте launch, если результат не нужен
scope.launch {
    loadData()
}
```

#### 5. Обрабатывайте Cancellation

```kotlin
viewModelScope.launch {
    try {
        val data = async { repository.loadData() }.await()
        processData(data)
    } catch (e: CancellationException) {
        // Cleanup if needed, затем пробрасываем дальше
        throw e
    } catch (e: Exception) {
        _error.value = e.message
    }
}
```

### Тестирование

```kotlin
class DataLoaderTest {
    @Test
    fun `test launch execution`() = runTest { // runTest вместо runBlocking
        val loader = DataLoader(repository, this)

        loader.loadWithLaunch()

        // Как проверить результат? launch не возвращает данные
        advanceUntilIdle() // Ждем завершения всех корутин
        // Проверяем side effects
    }

    @Test
    fun `test async returns result`() = runTest {
        val loader = DataLoader(repository, this)

        val deferred = loader.loadWithAsync()
        val result = deferred.await()

        assertEquals(expected, result)
    }

    @Test
    fun `test parallel execution`() = runTest {
        val startTime = currentTime

        coroutineScope {
            val job1 = async { delay(100); "A" }
            val job2 = async { delay(100); "B" }

            job1.await()
            job2.await()
        }

        val duration = currentTime - startTime
        assertTrue(duration < 150) // Параллельно, не 200ms
    }
}
```

## Answer (EN)

**launch**, **async**, and **runBlocking** are three main coroutine builders with different purposes:

| Builder | Returns | Blocks thread | Result | Use case |
|---------|---------|---------------|--------|----------|
| **launch** | `Job` | No | No direct value (fire-and-forget via side effects) | Background tasks, UI updates, side effects |
| **async** | `Deferred<T>` | No | Yes via `await()` | Parallel computations with results |
| **runBlocking** | `T` | **YES** | Yes directly | Tests, `main` function, blocking bridge to suspending code |

### Launch - Fire and Forget

```kotlin
fun loadUserInBackground() {
    viewModelScope.launch {
        // Runs asynchronously; result is exposed via state/side effects
        val user = userRepository.getUser(1)
        _user.value = user
    }
    // Function returns immediately, without waiting for the coroutine
}
```

Key properties of `launch`:
- Does not return a computed value directly
- Returns a `Job` that you can use to manage lifecycle (cancel, join, etc.)
- Does not block the calling thread
- Unhandled exceptions cancel the parent scope and are handled by its `CoroutineExceptionHandler`
- Use for: background work, UI updates, side effects, fire-and-forget tasks

Example usages:
- Loading data into `StateFlow`/`LiveData` in `viewModelScope`
- Periodic refresh loops (with `isActive` and `delay`)
- Running multiple independent tasks in parallel using multiple `launch` calls

Job management example:

```kotlin
class DownloadManager {
    private var downloadJob: Job? = null

    fun startDownload(url: String) {
        downloadJob?.cancel()

        downloadJob = CoroutineScope(Dispatchers.IO).launch {
            try {
                val file = downloadFile(url)
                withContext(Dispatchers.Main) { showSuccess(file) }
            } catch (e: CancellationException) {
                withContext(Dispatchers.Main) { showCancelled() }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) { showError(e) }
            }
        }
    }

    fun cancelDownload() {
        downloadJob?.cancel()
        downloadJob = null
    }

    fun isDownloading(): Boolean = downloadJob?.isActive == true
}
```

### Async - Parallel Computations With Result

```kotlin
suspend fun loadDashboard(): DashboardData = coroutineScope {
    val userDeferred = async { userApi.getUser() }
    val statsDeferred = async { statsApi.getStats() }
    val notificationsDeferred = async { notificationsApi.getNotifications() }

    DashboardData(
        user = userDeferred.await(),
        stats = statsDeferred.await(),
        notifications = notificationsDeferred.await()
    )
}
```

Key properties of `async`:
- Returns `Deferred<T>`; call `await()` to get the result
- Non-blocking until you call `await()`
- Exceptions are thrown when `await()` is called (or on parent completion if never awaited)
- Use for: parallel API calls/computations when you need the results

Example usages:
- Parallel loading of parts of a profile (`user`, `posts`, `followers`) and combining them
- `parallelMap` style helpers using `map { async { ... } }.awaitAll()`
- Competing sources pattern (first-successful result) with `select {}`

Error-handling example with fallback:

```kotlin
suspend fun loadWithFallback(): UserData = coroutineScope {
    val primaryDeferred = async {
        try {
            primaryApi.loadData()
        } catch (e: Exception) {
            null
        }
    }

    val secondaryDeferred = async {
        try {
            secondaryApi.loadData()
        } catch (e: Exception) {
            null
        }
    }

    primaryDeferred.await() ?: secondaryDeferred.await() ?: cachedData
}
```

Important:
- Always `await`/`awaitAll` on `Deferred`s you create, or you risk missing failures.
- If you only need fire-and-forget semantics, prefer `launch` over `async`.

### runBlocking - Blocking Bridge

```kotlin
fun main() = runBlocking {
    val user = userRepository.getUser(1)
    println("User: $user")
}
```

Key properties of `runBlocking`:
- Returns the result directly from its lambda
- Blocks the calling thread until completion
- Use only at boundaries: `main`, some tests, or legacy integration points
- Avoid in normal production code; never use on Android main thread

Examples:
- Main entry point:

```kotlin
fun main() = runBlocking {
    val app = MyApplication()
    app.start()
}
```

- Tests (though `runTest` from kotlinx-coroutines-test is preferred):

```kotlin
@Test
fun `test user loading`() = runBlocking {
    val repository = UserRepository()
    val user = repository.getUser(1)
    assertEquals("Alice", user.name)
}
```

- Temporary bridge in legacy synchronous APIs:

```kotlin
class LegacyService {
    fun getUserSync(id: Int): User = runBlocking {
        userRepository.getUser(id)
    }
}
```

Anti-example (do NOT do this):

```kotlin
class BadViewModel : ViewModel() {
    fun loadUser(id: Int) {
        val user = runBlocking { // Blocks UI thread
            userRepository.getUser(id)
        }
        _user.value = user
    }
}
```

### Practical Comparison Example

```kotlin
class DataLoader(
    private val repository: DataRepository,
    private val scope: CoroutineScope
) {
    fun loadWithLaunch() {
        scope.launch {
            val data = repository.loadData()
            // Expose via state/callback instead of return value
        }
    }

    fun loadWithAsync(): Deferred<Data> = scope.async {
        repository.loadData()
    }

    fun loadWithRunBlocking(): Data = runBlocking {
        repository.loadData()
    }

    suspend fun loadData(): Data = repository.loadData()
}
```

Usage:
- `launch`: fire-and-forget, caller returns immediately
- `async`: caller gets `Deferred` and can `await()` result
- `runBlocking`: caller blocked until result is ready (only for controlled boundaries)
- Preferred: expose `suspend` APIs instead of forcing `runBlocking`

### Launch vs Async - When to Use What

Misuse:

```kotlin
// Wrong: async without await()
viewModelScope.launch {
    async { loadUsers() } // Result and failures ignored
    async { loadPosts() }
}
```

Correct:

```kotlin
// Use launch for fire-and-forget
viewModelScope.launch {
    launch { loadUsers() }
    launch { loadPosts() }
}

// Use async when you need a result
viewModelScope.launch {
    val user = async { userRepository.getUser(1) }.await()
}

// Or keep it simple: plain suspend call in a launch
viewModelScope.launch {
    val user = userRepository.getUser(1)
}
```

Guidelines:
- If you need a result: `async` + `await()` (or structured helper around it)
- If you need side effects only: `launch`
- Never use `async` as fire-and-forget

### Structured Concurrency

```kotlin
suspend fun loadAllData() = coroutineScope {
    launch { loadUsers() }
    launch { loadPosts() }
}

suspend fun computeResults() = coroutineScope {
    val r1 = async { compute1() }
    val r2 = async { compute2() }
    r1.await() + r2.await()
}
```

Key points:
- `coroutineScope` waits for all children to complete
- Child failures cancel the scope (unless using supervisor-style scopes)

### Exception Handling

```kotlin
// launch: handle inside the coroutine
viewModelScope.launch {
    try {
        userRepository.getUser(1)
    } catch (e: Exception) {
        _error.value = e.message
    }
}

// async: exceptions surface on await()
viewModelScope.launch {
    val deferred = async { userRepository.getUser(1) }
    try {
        val user = deferred.await()
        _user.value = user
    } catch (e: Exception) {
        _error.value = e.message
    }
}

// runBlocking: behaves like regular blocking code
try {
    runBlocking { userRepository.getUser(1) }
} catch (e: Exception) {
    println("Error: ${e.message}")
}
```

Notes:
- For `launch`, unhandled exceptions go to the parent/supervisor
- For `async`, if you never `await`, failures can be effectively ignored; always consume results

### supervisorScope - Independent Children

```kotlin
suspend fun loadDataStrict() = coroutineScope {
    launch { loadUsers() }
    launch { loadPosts() }
    launch { loadComments() }
}

suspend fun loadDataResilient() = supervisorScope {
    launch {
        try {
            loadUsers()
        } catch (e: Exception) {
            logError(e)
        }
    }

    launch {
        try {
            loadPosts()
        } catch (e: Exception) {
            logError(e)
        }
    }
}
```

- `coroutineScope`: one child failure cancels all children
- `supervisorScope`: children fail independently; useful for UI where partial failure is acceptable

### Advanced Patterns

1) Timeout with async:

```kotlin
suspend fun loadWithTimeout(): Data? = coroutineScope {
    val deferred = async { repository.loadData() }
    try {
        withTimeout(5000) { deferred.await() }
    } catch (e: TimeoutCancellationException) {
        deferred.cancel()
        null
    }
}
```

2) Retry with launch:

```kotlin
fun loadUserWithRetry(id: Int) {
    viewModelScope.launch {
        repeat(3) { attempt ->
            try {
                val user = userRepository.getUser(id)
                _user.value = user
                return@launch
            } catch (e: Exception) {
                if (attempt == 2) throw e
                delay(1000L * (attempt + 1))
            }
        }
    }
}
```

3) Cancellable async work:

```kotlin
class ImageProcessor {
    private var processingJob: Job? = null

    fun processImage(bitmap: Bitmap) {
        processingJob?.cancel()

        processingJob = CoroutineScope(Dispatchers.Default).launch {
            val deferred = async { applyFilters(bitmap) }
            try {
                val result = deferred.await()
                withContext(Dispatchers.Main) { showResult(result) }
            } catch (e: CancellationException) {
                // Cancelled
            }
        }
    }

    fun cancel() {
        processingJob?.cancel()
    }
}
```

### Performance Comparison

```kotlin
suspend fun loadSequentially() {
    val user = userRepository.getUser(1)
    val posts = postsRepository.getPosts(1)
    val comments = commentsRepository.getComments(1)
}

suspend fun loadInParallel() = coroutineScope {
    val userDeferred = async { userRepository.getUser(1) }
    val postsDeferred = async { postsRepository.getPosts(1) }
    val commentsDeferred = async { commentsRepository.getComments(1) }

    Triple(
        userDeferred.await(),
        postsDeferred.await(),
        commentsDeferred.await()
    )
}

fun loadWithLaunch() {
    scope.launch {
        launch { loadUsers() }
        launch { loadPosts() }
        launch { loadComments() }
    }
}
```

Observations:
- Sequential: total time ≈ sum
- Parallel with `async`: total time ≈ max
- `launch` is fine when you publish results via shared state instead of return values

### Best Practices

1) Use `launch` for side effects:

```kotlin
viewModelScope.launch {
    analyticsService.logEvent("screen_viewed")
    cacheService.warmUpCache()
}
```

2) Use `async` for parallel computations with required results:

```kotlin
suspend fun calculateComplexResult() = coroutineScope {
    val part1 = async { calculatePart1() }
    val part2 = async { calculatePart2() }
    val part3 = async { calculatePart3() }
    combineResults(part1.await(), part2.await(), part3.await())
}
```

3) Avoid `runBlocking` in production paths; prefer `suspend` APIs and coroutine scopes.

4) Always consume `Deferred` results (via `await`/`awaitAll`), or use `launch` instead.

5) Handle cancellation explicitly when needed; rethrow `CancellationException` after cleanup.

---

## Follow-ups

- What are key differences between these and Java executors/futures?
- When would you use each builder in practice in a real project?
- What are common pitfalls (e.g., `async` without `await`, `runBlocking` on main thread)?

## References

- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [[c-kotlin]]
- [[c-coroutines]]

## Related Questions

- [[q-executor-service-java--kotlin--medium]]
- [[q-coroutine-memory-leak-detection--kotlin--hard]]
- [[q-list-vs-sequence--kotlin--medium]]
