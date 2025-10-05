---
tags:
  - kotlin
  - coroutines
  - launch
  - async
  - runblocking
  - coroutine-builders
difficulty: medium
---

# Launch vs Async vs RunBlocking

**English**: What's the difference between `launch`, `async`, and `runBlocking` coroutine builders?

## Answer

**Launch**, **async**, и **runBlocking** - три основных способа запуска корутин, каждый с разным назначением:

| Builder | Возвращает | Блокирует поток | Результат | Use case |
|---------|------------|-----------------|-----------|----------|
| **launch** | `Job` | ❌ Нет | Нет (fire-and-forget) | Фоновые задачи без результата |
| **async** | `Deferred<T>` | ❌ Нет | ✅ Да через `await()` | Параллельные вычисления с результатом |
| **runBlocking** | `T` | ✅ **ДА** | ✅ Да напрямую | Тесты, main функция, блокирующий bridge |

### launch - Fire and Forget

```kotlin
fun loadUserInBackground() {
    viewModelScope.launch {
        // Запускается асинхронно, результат не возвращается
        val user = userRepository.getUser(1)
        _user.value = user
    }
    // Функция возвращается СРАЗУ, не дожидаясь завершения корутины
}
```

**Характеристики launch**:
- ❌ Не возвращает результат
- ✅ Возвращает `Job` для управления lifecycle
- ❌ Не блокирует вызывающий поток
- ✅ Исключения пробрасываются в parent scope
- 📝 Use case: фоновая работа, обновление UI, side effects

#### Примеры использования launch

```kotlin
class UserViewModel : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users = _users.asStateFlow()

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

#### Job management с launch

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

### async - Параллельные вычисления с результатом

```kotlin
suspend fun loadDashboard(): DashboardData = coroutineScope {
    // Запускаем три запроса параллельно
    val userDeferred = async { userApi.getUser() }
    val statsDeferred = async { statsApi.getStats() }
    val notificationsDeferred = async { notificationsApi.getNotifications() }

    // Ждем всех результатов
    DashboardData(
        user = userDeferred.await(),      // Блокирует до получения результата
        stats = statsDeferred.await(),
        notifications = notificationsDeferred.await()
    )
}
```

**Характеристики async**:
- ✅ Возвращает результат через `Deferred<T>`
- ✅ Можно получить результат через `await()`
- ❌ Не блокирует вызывающий поток до вызова `await()`
- ✅ Исключения выбрасываются при вызове `await()`
- 📝 Use case: параллельные вычисления, где нужен результат

#### Примеры использования async

```kotlin
// 1. Параллельная загрузка нескольких ресурсов
suspend fun loadUserProfile(userId: Int): UserProfile = coroutineScope {
    val userDeferred = async { userRepository.getUser(userId) }
    val postsDeferred = async { postsRepository.getUserPosts(userId) }
    val followersDeferred = async { socialRepository.getFollowers(userId) }

    // Все три запроса идут параллельно!
    // Время = max(user, posts, followers), не sum
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

#### async с обработкой ошибок

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

### runBlocking - Блокирующий мост

```kotlin
fun main() = runBlocking { // Блокирует main поток
    val user = userRepository.getUser(1) // Выполняется синхронно
    println("User: $user")
} // main поток разблокируется только здесь
```

**Характеристики runBlocking**:
- ✅ Возвращает результат напрямую
- ✅ **БЛОКИРУЕТ** вызывающий поток до завершения
- ❌ НЕ для production кода
- ✅ Для тестов и main функции
- 📝 Use case: мост между синхронным и асинхронным кодом

#### Когда использовать runBlocking

```kotlin
// ✅ 1. Main функция
fun main() = runBlocking {
    val app = MyApplication()
    app.start()
}

// ✅ 2. Unit тесты (но лучше runTest)
@Test
fun `test user loading`() = runBlocking {
    val repository = UserRepository()
    val user = repository.getUser(1)
    assertEquals("Alice", user.name)
}

// ✅ 3. Migration legacy code
class LegacyService {
    fun getUserSync(id: Int): User = runBlocking {
        // Временное решение для интеграции с suspend функциями
        userRepository.getUser(id)
    }
}

// ❌ НИКОГДА не используйте в Android UI коде!
class BadViewModel : ViewModel() {
    fun loadUser(id: Int) {
        val user = runBlocking { // ❌❌❌ Блокирует UI поток!
            userRepository.getUser(id)
        }
        _user.value = user
    }
}
```

### Сравнение на реальном примере

```kotlin
class DataLoader(
    private val repository: DataRepository,
    private val scope: CoroutineScope
) {
    // ❌ launch - результат не возвращается
    fun loadWithLaunch() {
        scope.launch {
            val data = repository.loadData()
            // Как получить data наружу? Только через callback/StateFlow
        }
        // Возвращается сразу, data еще не загружена
    }

    // ✅ async - можно получить результат
    fun loadWithAsync(): Deferred<Data> {
        return scope.async {
            repository.loadData()
        }
        // Возвращается Deferred<Data>, результат через await()
    }

    // ❌ runBlocking - блокирует поток
    fun loadWithRunBlocking(): Data {
        return runBlocking {
            repository.loadData()
        }
        // Возвращается только после загрузки, поток ЗАБЛОКИРОВАН
    }

    // ✅ Правильный подход - suspend функция
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

        // ❌ runBlocking - НЕ ДЕЛАЙТЕ ТАК
        val data = loader.loadWithRunBlocking() // Блокирует UI!

        // ✅ Правильно - suspend функция
        viewModelScope.launch {
            val data = loader.loadData()
        }
    }
}
```

### launch vs async - когда что использовать

```kotlin
// ❌ НЕПРАВИЛЬНО - async без await()
viewModelScope.launch {
    async { loadUsers() } // Результат игнорируется!
    async { loadPosts() }
}

// ✅ ПРАВИЛЬНО - launch для fire-and-forget
viewModelScope.launch {
    launch { loadUsers() }
    launch { loadPosts() }
}

// ❌ НЕПРАВИЛЬНО - launch когда нужен результат
viewModelScope.launch {
    launch { userRepository.getUser(1) } // Как получить User?
}

// ✅ ПРАВИЛЬНО - async когда нужен результат
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

### Exception handling

```kotlin
// launch - исключения пробрасываются в scope
viewModelScope.launch {
    try {
        userRepository.getUser(1) // Если ошибка - catch сработает
    } catch (e: Exception) {
        _error.value = e.message
    }
}

// async - исключения выбрасываются при await()
viewModelScope.launch {
    val deferred = async {
        userRepository.getUser(1) // Исключение НЕ выбросится здесь
    }

    try {
        val user = deferred.await() // Исключение выбросится ЗДЕСЬ
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

### supervisorScope - независимые дочерние корутины

```kotlin
// coroutineScope - одна ошибка отменяет все
suspend fun loadDataStrict() = coroutineScope {
    launch { loadUsers() }     // Если упадет -
    launch { loadPosts() }     // - ВСЕ отменятся
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

### Продвинутые паттерны

#### 1. Timeout для async

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

#### 2. Retry для launch

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
                delay(1000 * (attempt + 1)) // Exponential backoff
            }
        }
    }
}
```

#### 3. Cancellable async работа

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

### Performance comparison

```kotlin
// Последовательное выполнение - медленно
suspend fun loadSequentially() {
    val user = userRepository.getUser(1)       // 500ms
    val posts = postsRepository.getPosts(1)    // 500ms
    val comments = commentsRepository.getComments(1) // 500ms
    // Общее время: 1500ms
}

// Параллельное с async - быстро
suspend fun loadInParallel() = coroutineScope {
    val userDeferred = async { userRepository.getUser(1) }      // 500ms
    val postsDeferred = async { postsRepository.getPosts(1) }   // 500ms
    val commentsDeferred = async { commentsRepository.getComments(1) } // 500ms

    Triple(
        userDeferred.await(),
        postsDeferred.await(),
        commentsDeferred.await()
    )
    // Общее время: ~500ms (max из трех)
}

// Параллельное с launch - нет результата
fun loadWithLaunch() {
    scope.launch {
        launch { loadUsers() }    // 500ms
        launch { loadPosts() }    // 500ms
        launch { loadComments() } // 500ms
        // Как собрать результаты? Только через shared state
    }
}
```

### Best Practices

#### 1. Используйте launch для side effects

```kotlin
// ✅ ПРАВИЛЬНО
viewModelScope.launch {
    analyticsService.logEvent("screen_viewed")
    cacheService.warmUpCache()
}
```

#### 2. Используйте async для параллельных вычислений

```kotlin
// ✅ ПРАВИЛЬНО
suspend fun calculateComplexResult() = coroutineScope {
    val part1 = async { calculatePart1() }
    val part2 = async { calculatePart2() }
    val part3 = async { calculatePart3() }

    combineResults(part1.await(), part2.await(), part3.await())
}
```

#### 3. НЕ используйте runBlocking в production

```kotlin
// ❌ НЕПРАВИЛЬНО
fun loadUser(id: Int): User = runBlocking {
    userRepository.getUser(id)
}

// ✅ ПРАВИЛЬНО - сделайте suspend функцию
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

#### 4. Всегда await() результаты async

```kotlin
// ❌ НЕПРАВИЛЬНО - async без await
scope.launch {
    async { loadData() } // Результат потерян!
}

// ✅ ПРАВИЛЬНО
scope.launch {
    val data = async { loadData() }.await()
}

// Или используйте launch
scope.launch {
    loadData()
}
```

#### 5. Обрабатывайте cancellation

```kotlin
viewModelScope.launch {
    try {
        val data = async { repository.loadData() }.await()
        processData(data)
    } catch (e: CancellationException) {
        // Cleanup if needed
        throw e // ВАЖНО: пробросить дальше
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
        val loader = DataLoader()

        loader.loadWithLaunch()

        // Как проверить результат? launch не возвращает данные
        advanceUntilIdle() // Ждем завершения всех корутин
        // Проверяем side effects
    }

    @Test
    fun `test async returns result`() = runTest {
        val loader = DataLoader()

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

**English**: **launch**, **async**, and **runBlocking** are three main coroutine builders with different purposes:

**launch**: Returns `Job`, doesn't block thread, no result value (fire-and-forget). Use for: background tasks without results, UI updates, side effects. Exceptions propagate to parent scope.

**async**: Returns `Deferred<T>`, doesn't block thread until `await()`, returns result. Use for: parallel computations with results, multiple concurrent API calls, first-successful-result patterns. Exceptions thrown at `await()`.

**runBlocking**: Returns result directly, **BLOCKS** calling thread until completion. Use ONLY for: tests (prefer `runTest`), main function, bridging sync/async code. NEVER use in Android UI code.

**Key differences**:
- Time to complete 3 sequential 500ms tasks: launch (500ms parallel), async (500ms parallel with results), runBlocking (1500ms if sequential, blocks thread)
- Exception handling: launch (immediate in scope), async (at await()), runBlocking (synchronous)
- Result access: launch (none, use StateFlow/callbacks), async (await()), runBlocking (direct return)

**Best practices**: Use launch for side effects. Use async for parallel computations needing results. Never runBlocking in production. Always await() async results. Handle CancellationException properly. Prefer suspend functions over runBlocking bridges.

