---
---
---id: kotlin-162
title: "Launch Vs Async Vs Runblocking / Launch против Async против Runblocking"
aliases: [Async, Coroutine Builders, Launch, RunBlocking]
topic: kotlin
subtopics: [concurrency, coroutines]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, c-stateflow, q-coroutine-memory-leak-detection--kotlin--hard, q-executor-service-java--kotlin--medium, q-list-vs-sequence--kotlin--medium]
created: 2024-10-15
updated: 2025-11-11
tags: [async, concurrency, coroutines, difficulty/medium, kotlin, launch, runblocking]
---
# Вопрос (RU)
> В чём разница между корутинными билдерами `launch`, `async` и `runBlocking`?

# Question (EN)
> What's the difference between `launch`, `async`, and `runBlocking` coroutine builders?

## Ответ (RU)

**launch**, **async** и **runBlocking** — три ключевых coroutine builder'а с разным назначением:

| Builder | Возвращает | Блокирует поток | Результат | Use case |
|---------|------------|-----------------|-----------|----------|
| **launch** | `Job` | Нет | Нет (fire-and-forget, через сайд-эффекты) | Фоновые задачи без прямого результата или с результатом через состояние/сайд-эффекты |
| **async** | `Deferred<T>` | Нет | Да, через `await()` | Параллельные вычисления с результатом |
| **runBlocking** | `T` | **ДА** | Да, напрямую | Тесты, `main` функция, блокирующий мост к suspend-коду |

### Launch — Fire-and-forget

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

Характеристики `launch`:
- Не возвращает вычисленный результат напрямую
- Возвращает `Job` для управления жизненным циклом (cancel, join и т.п.)
- Не блокирует вызывающий поток
- Необработанные исключения по умолчанию отменяют родительский scope и обрабатываются его `CoroutineExceptionHandler`
- Используется для фоновой работы, обновления UI и других сайд-эффектов

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
        // Все три запускаются параллельно в рамках одного scope
    }
}
```

#### Управление Job С Launch

```kotlin
class DownloadManager(private val scope: CoroutineScope) {
    private var downloadJob: Job? = null

    fun startDownload(url: String) {
        // Отменяем предыдущую загрузку если есть
        downloadJob?.cancel()

        // Используем предоставленный scope, а не глобальный
        downloadJob = scope.launch(Dispatchers.IO) {
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
                throw e
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

    fun isDownloading(): Boolean = downloadJob?.isActive == true
}
```

### Async — Параллельные Вычисления С Результатом

```kotlin
suspend fun loadDashboard(): DashboardData = coroutineScope {
    // Запускаем три запроса параллельно (в рамках структурированной конкуренции)
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

Характеристики `async`:
- Возвращает `Deferred<T>`
- Результат получается через `await()`
- Не блокирует поток; `await()` приостанавливает корутину до результата
- Исключения сохраняются в `Deferred` и повторно выбрасываются при `await()`;
  в структурированном scope необработанное исключение дочернего `async` также приведёт к отмене родителя при завершении scope
- Используется для параллельных вычислений, где нужен результат

#### Примеры Использования Async

```kotlin
// 1. Параллельная загрузка нескольких ресурсов
suspend fun loadUserProfile(userId: Int): UserProfile = coroutineScope {
    val userDeferred = async { userRepository.getUser(userId) }
    val postsDeferred = async { postsRepository.getUserPosts(userId) }
    val followersDeferred = async { socialRepository.getFollowers(userId) }

    // Все три запроса идут параллельно
    // Время ~ max(user, posts, followers), а не сумма
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
    }.awaitAll() // Ждем всех одновременно; ошибки не теряются
}

// 3. First successful result (продвинутый пример)
suspend fun loadFromMultipleSources(): Data = coroutineScope {
    val source1 = async { loadFromServer1() }
    val source2 = async { loadFromServer2() }
    val source3 = async { loadFromCache() }

    select<Data> {
        source1.onAwait { it }
        source2.onAwait { it }
        source3.onAwait { it }
    }
    // Остальные Deferred следует при необходимости отменить, если их результат больше не нужен
}
```

#### Async С Обработкой Ошибок

```kotlin
suspend fun loadWithFallback(cachedData: UserData): UserData = coroutineScope {
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

### runBlocking — Блокирующий Мост

```kotlin
fun main() = runBlocking { // Блокирует main-поток
    val user = userRepository.getUser(1)
    println("User: $user")
} // main-поток разблокируется только здесь
```

Характеристики `runBlocking`:
- Возвращает результат напрямую (значение последнего выражения в блоке или указанное явно)
- Блокирует вызывающий поток до завершения
- Предназначен для:
  - `main` функции JVM-приложений
  - некоторых unit-тестов (хотя лучше `runTest`)
  - точечных блокирующих мостов к suspend-коду
- В обычном production-коде, особенно на Android main thread, следует избегать

#### Когда Использовать runBlocking

```kotlin
// 1. Main-функция
fun main() = runBlocking {
    val app = MyApplication()
    app.start()
}

// 2. Unit-тесты (но лучше runTest из kotlinx-coroutines-test)
@Test
fun `test user loading`() = runBlocking {
    val repository = UserRepository()
    val user = repository.getUser(1)
    assertEquals("Alice", user.name)
}

// 3. Временная миграция легаси-кода
class LegacyService {
    fun getUserSync(id: Int): User = runBlocking {
        userRepository.getUser(id)
    }
}

// Никогда не используйте runBlocking в Android UI-коде
class BadViewModel : ViewModel() {
    fun loadUser(id: Int) {
        val user = runBlocking { // ПЛОХО: блокирует UI-поток
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
    // launch — результат не возвращается напрямую
    fun loadWithLaunch() {
        scope.launch {
            val data = repository.loadData()
            // Отдаем data наружу через StateFlow/LiveData/callback и т.п.
        }
        // Возвращается сразу, data ещё не загружена
    }

    // async — можно получить результат через Deferred
    fun loadWithAsync(): Deferred<Data> {
        return scope.async {
            repository.loadData()
        }
    }

    // runBlocking — блокирует вызывающий поток
    fun loadWithRunBlocking(): Data {
        return runBlocking {
            repository.loadData()
        }
    }

    // Предпочтительный подход — suspending API
    suspend fun loadData(): Data {
        return repository.loadData()
    }
}

class ExampleViewModel(
    private val loader: DataLoader
) : ViewModel() {

    fun example() {
        // launch — fire-and-forget
        viewModelScope.launch {
            loader.loadWithLaunch()
        }

        // async — получаем Deferred и явно ждем результат
        viewModelScope.launch {
            val deferred = loader.loadWithAsync()
            val data = deferred.await()
        }

        // runBlocking — не делайте так в UI-коде (пример анти-паттерна)
        // val data = loader.loadWithRunBlocking()

        // Правильно — вызывать suspend-функцию из корутины
        viewModelScope.launch {
            val data2 = loader.loadData()
        }
    }
}
```

### Launch Vs Async — Когда Что Использовать

```kotlin
// НЕПРАВИЛЬНО — async без await()
viewModelScope.launch {
    async { loadUsers() } // Результат и возможные исключения могут быть проигнорированы
    async { loadPosts() }
}

// ПРАВИЛЬНО — launch для fire-and-forget
viewModelScope.launch {
    launch { loadUsers() }
    launch { loadPosts() }
}

// НЕПРАВИЛЬНО — launch когда нужен результат
viewModelScope.launch {
    launch { userRepository.getUser(1) } // Непонятно, как получить User
}

// ПРАВИЛЬНО — async когда нужен результат
viewModelScope.launch {
    val user = async { userRepository.getUser(1) }.await()
}

// Или ещё лучше — просто последовательный suspend-вызов
viewModelScope.launch {
    val user = userRepository.getUser(1)
}
```

### Structured Concurrency

```kotlin
suspend fun loadAllData() = coroutineScope {
    // Все дочерние корутины должны завершиться перед возвратом

    launch {
        loadUsers()
    }

    launch {
        loadPosts()
    }
    // coroutineScope дождётся завершения ВСЕХ дочерних корутин или выбросит исключение при ошибке
}

suspend fun computeResults() = coroutineScope {
    val result1 = async { compute1() }
    val result2 = async { compute2() }

    result1.await() + result2.await()
    // Возвращается только когда ОБА async завершены или выброшено исключение
}
```

### Обработка Исключений

```kotlin
// launch — исключения можно обрабатывать внутри корутины
viewModelScope.launch {
    try {
        userRepository.getUser(1)
    } catch (e: Exception) {
        _error.value = e.message
    }
}

// async — исключения выбрасываются при await()
viewModelScope.launch {
    val deferred = async {
        userRepository.getUser(1)
    }

    try {
        val user = deferred.await() // Исключение появится здесь
        _user.value = user
    } catch (e: Exception) {
        _error.value = e.message
    }
}

// runBlocking — исключения ведут себя как в обычном блокирующем коде
try {
    runBlocking {
        userRepository.getUser(1)
    }
} catch (e: Exception) {
    println("Error: ${e.message}")
}
```

Примечания:
- Для `launch` необработанное исключение пробрасывается в родительский scope/handler.
- Для `async` важно всегда «потреблять» `Deferred` через `await`/`awaitAll`, иначе ошибка может быть замечена только при завершении scope; как правило, `async` без `await` — запах.

### supervisorScope — Независимые Дочерние Корутины

```kotlin
// coroutineScope — одна ошибка отменяет все
suspend fun loadDataStrict() = coroutineScope {
    launch { loadUsers() }
    launch { loadPosts() }
    launch { loadComments() }
}

// supervisorScope — ошибки изолированы
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
        deferred.cancel() // Отменяем корутину, если результат больше не нужен
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
                return@launch // Успех — выходим
            } catch (e: Exception) {
                if (attempt == 2) throw e // Последняя попытка
                delay(1000L * (attempt + 1))
            }
        }
    }
}
```

#### 3. Отменяемая Работа С Async

```kotlin
class ImageProcessor(private val scope: CoroutineScope) {
    private var processingJob: Job? = null

    fun processImage(bitmap: Bitmap) {
        processingJob?.cancel()

        processingJob = scope.launch(Dispatchers.Default) {
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
                throw e
            }
        }
    }

    fun cancel() {
        processingJob?.cancel()
    }
}
```

### Сравнение Производительности

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
    // Общее время: ~500ms (max из трёх)
}

// Параллельное с launch — без прямого результата
fun loadWithLaunch(scope: CoroutineScope) {
    scope.launch {
        launch { loadUsers() }
        launch { loadPosts() }
        launch { loadComments() }
        // Результаты передаются через общее состояние/каналы и т.п.
    }
}
```

### Best Practices (RU)

1. Используйте `launch` для сайд-эффектов.
2. Используйте `async` для параллельных вычислений, когда результат нужен.
3. Не используйте `runBlocking` в обычных продакшн-путях, особенно на UI-потоке.
4. Всегда потребляйте результаты `Deferred` (`await`/`awaitAll`) или используйте `launch` вместо `async`.
5. Обрабатывайте отмену, при необходимости делая cleanup и повторно бросая `CancellationException`.

### Тестирование

```kotlin
class DataLoaderTest {
    @Test
    fun `test launch execution`() = runTest {
        val loader = DataLoader(repository, this)

        loader.loadWithLaunch()

        advanceUntilIdle() // Ждем завершения всех корутин во времени теста
        // Проверяем сайд-эффекты
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
        // В тесте с виртуальным временем обе корутины завершаются "параллельно":
        assertTrue(duration < 150)
    }
}
```

## Answer (EN)

`launch`, `async`, and `runBlocking` are three primary coroutine builders with different purposes:

| Builder | Returns | Blocks thread | Result | Use case |
|---------|---------|---------------|--------|----------|
| **launch** | `Job` | No | No direct value (fire-and-forget via side effects) | Background tasks, UI updates, side effects |
| **async** | `Deferred<T>` | No | Yes via `await()` | Parallel computations with results |
| **runBlocking** | `T` | **YES** | Yes directly | Tests, `main` function, blocking bridge to suspending code |

### Launch — Fire-and-forget

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
- Use for background work, UI updates, and other side effects

Example usages:
- Loading data into `StateFlow`/`LiveData` in `viewModelScope`
- Periodic refresh loops (with `isActive` and `delay`)
- Running multiple independent tasks in parallel using multiple `launch` calls within the same scope

Job management example:

```kotlin
class DownloadManager(private val scope: CoroutineScope) {
    private var downloadJob: Job? = null

    fun startDownload(url: String) {
        downloadJob?.cancel()

        // Use the passed-in scope instead of creating a global one
        downloadJob = scope.launch(Dispatchers.IO) {
            try {
                val file = downloadFile(url)
                withContext(Dispatchers.Main) { showSuccess(file) }
            } catch (e: CancellationException) {
                withContext(Dispatchers.Main) { showCancelled() }
                throw e
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

### Async — Parallel Computations with a Result

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
- Non-blocking; `await()` suspends the coroutine until completion
- Exceptions are captured in the `Deferred` and rethrown when `await()` is called;
  in a structured scope, an unhandled exception in an `async` child will also cancel the parent when the scope completes
- Use for parallel API calls/computations when you need their results

Example usages:

```kotlin
// 1. Parallel loading of multiple resources
suspend fun loadUserProfile(userId: Int): UserProfile = coroutineScope {
    val userDeferred = async { userRepository.getUser(userId) }
    val postsDeferred = async { postsRepository.getUserPosts(userId) }
    val followersDeferred = async { socialRepository.getFollowers(userId) }

    UserProfile(
        user = userDeferred.await(),
        posts = postsDeferred.await(),
        followers = followersDeferred.await()
    )
}

// 2. Parallel map
suspend fun loadMultipleUsers(ids: List<Int>): List<User> = coroutineScope {
    ids.map { id -> async { userRepository.getUser(id) } }.awaitAll()
}

// 3. First successful result (advanced)
suspend fun loadFromMultipleSources(): Data = coroutineScope {
    val source1 = async { loadFromServer1() }
    val source2 = async { loadFromServer2() }
    val source3 = async { loadFromCache() }

    select<Data> {
        source1.onAwait { it }
        source2.onAwait { it }
        source3.onAwait { it }
    }
    // Cancel or ignore remaining Deferreds if their results are no longer needed
}
```

Error-handling with fallback:

```kotlin
suspend fun loadWithFallback(cachedData: UserData): UserData = coroutineScope {
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
- Always `await`/`awaitAll` on `Deferred`s you create (or otherwise handle them), or you risk effectively ignoring failures.
- If you only need fire-and-forget semantics, prefer `launch` over `async`.

### runBlocking — Blocking Bridge

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

```kotlin
// 1. Main entry point
fun main() = runBlocking {
    val app = MyApplication()
    app.start()
}

// 2. Unit tests (though runTest from kotlinx-coroutines-test is preferred)
@Test
fun `test user loading`() = runBlocking {
    val repository = UserRepository()
    val user = repository.getUser(1)
    assertEquals("Alice", user.name)
}

// 3. Temporary bridge in legacy synchronous APIs
class LegacyService {
    fun getUserSync(id: Int): User = runBlocking {
        userRepository.getUser(id)
    }
}

// Anti-example: do NOT do this on main/UI thread
class BadViewModel : ViewModel() {
    fun loadUser(id: Int) {
        val user = runBlocking { // Blocks UI thread — bad
            userRepository.getUser(id)
        }
        _user.value = user
    }
}
```

### Practical Comparison

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

class ExampleViewModel(
    private val loader: DataLoader
) : ViewModel() {

    fun example() {
        viewModelScope.launch {
            loader.loadWithLaunch()
        }

        viewModelScope.launch {
            val deferred = loader.loadWithAsync()
            val data = deferred.await()
        }

        // val data = loader.loadWithRunBlocking() // Anti-pattern on UI thread

        viewModelScope.launch {
            val data2 = loader.loadData()
        }
    }
}
```

Usage summary:
- `launch`: fire-and-forget; caller returns immediately.
- `async`: returns `Deferred`; caller can `await()` for result.
- `runBlocking`: blocks caller; only for controlled boundaries.
- Preferred: expose `suspend` APIs and call them from coroutines.

### Launch Vs Async — when to Use what

Misuse:

```kotlin
// Wrong: async without await()
viewModelScope.launch {
    async { loadUsers() } // Result and failures may be ignored
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

// Or just call suspend in launch
viewModelScope.launch {
    val user = userRepository.getUser(1)
}
```

Guidelines:
- Need a result: `async` + `await()`.
- Need only side effects: `launch`.
- Don't use `async` as fire-and-forget.

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
- `coroutineScope` waits for all children to complete or throws on first failure.
- Child failures cancel the scope (unless using supervisor-style scopes).

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
- For `launch`, unhandled exceptions go to the parent/supervisor/handler.
- For `async`, if you never `await`, failures can be effectively ignored or only surface when the scope completes.

### supervisorScope — Independent Children

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

- `coroutineScope`: one child failure cancels all children.
- `supervisorScope`: children fail independently; good for UI/partial-failure scenarios.

### Advanced Patterns

1. Timeout with async:

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

1. Retry with launch:

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

1. Cancellable async work:

```kotlin
class ImageProcessor(private val scope: CoroutineScope) {
    private var processingJob: Job? = null

    fun processImage(bitmap: Bitmap) {
        processingJob?.cancel()

        processingJob = scope.launch(Dispatchers.Default) {
            val deferred = async { applyFilters(bitmap) }
            try {
                val result = deferred.await()
                withContext(Dispatchers.Main) { showResult(result) }
            } catch (e: CancellationException) {
                // Cancelled
                throw e
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

fun loadWithLaunch(scope: CoroutineScope) {
    scope.launch {
        launch { loadUsers() }
        launch { loadPosts() }
        launch { loadComments() }
    }
}
```

Observations:
- Sequential: total time ≈ sum of individual times.
- Parallel with `async`: total time ≈ max of individual times.
- `launch` is appropriate when publishing results via shared state instead of return values.

### Best Practices (EN)

1. Use `launch` for side effects.
2. Use `async` for parallel computations when you need the results.
3. Avoid `runBlocking` on production hot paths; prefer `suspend` APIs and coroutine scopes.
4. Always consume `Deferred` results (`await`/`awaitAll`), or use `launch` instead when no result is needed.
5. Handle cancellation explicitly when needed and rethrow `CancellationException` after cleanup.

---

## Дополнительные Вопросы (RU)

- В чём ключевые отличия этих билдров от Java executors/futures?
- Когда бы вы использовали каждый из билдров на практике в реальном проекте?
- Каковы распространённые ошибки (например, `async` без `await`, `runBlocking` на main-потоке)?

## Follow-ups

- What are key differences between these and Java executors/futures?
- When would you use each builder in practice in a real project?
- What are common pitfalls (e.g., `async` without `await`, `runBlocking` on main thread)?

## Ссылки (RU)

- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [[c-kotlin]]
- [[c-coroutines]]

## References

- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [[c-kotlin]]
- [[c-coroutines]]

## Связанные Вопросы (RU)

- [[q-executor-service-java--kotlin--medium]]
- [[q-coroutine-memory-leak-detection--kotlin--hard]]
- [[q-list-vs-sequence--kotlin--medium]]

## Related Questions

- [[q-executor-service-java--kotlin--medium]]
- [[q-coroutine-memory-leak-detection--kotlin--hard]]
- [[q-list-vs-sequence--kotlin--medium]]
