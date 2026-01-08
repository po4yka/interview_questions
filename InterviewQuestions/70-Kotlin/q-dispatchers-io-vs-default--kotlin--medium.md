---\
id: kotlin-153
title: "Dispatchers IO Vs Default / Dispatchers.IO против Default"
aliases: ["Dispatchers IO vs Default", "Dispatchers.IO против Default"]
topic: kotlin
subtopics: [coroutines, dispatchers]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-concurrency, q-coroutine-scope-basics--kotlin--easy, q-request-coalescing-deduplication--kotlin--hard]
created: 2024-10-15
updated: 2025-11-09
tags: [concurrency, coroutines, difficulty/medium, dispatchers, kotlin, threading]

---\
# Вопрос (RU)
> В чём разница между Dispatchers.IO и Dispatchers.Default? Когда использовать каждый из них?

# Question (EN)
> What's the difference between Dispatchers.IO and Dispatchers.Default? When should you use each?

## Ответ (RU)

**Dispatchers.IO** и **Dispatchers.Default** — два предустановленных диспетчера для выполнения корутин на разных thread pools с разными характеристиками.

### Ключевые Различия

**Dispatchers.IO** предназначен для операций ввода-вывода (I/O), таких как сетевые запросы, чтение/запись файлов и работа с базами данных. Основан на общем пуле потоков и может использовать существенно больше потоков, чем число ядер CPU (исторически — до значения порядка десятков + число ядер; точные детали реализации могут меняться между версиями и не должны восприниматься как стабильный контракт). Используйте для: HTTP-запросов, файловых операций, запросов к БД, блокирующих системных вызовов. Потоки проводят много времени в ожидании (не нагружая CPU).

**Dispatchers.Default** оптимизирован для CPU-интенсивных вычислений. Размер пула примерно равен количеству ядер CPU. Используйте для: парсинга JSON, сортировки больших списков, обработки изображений, шифрования, сложных вычислений. Потоки активно используют процессор.

**Почему разные размеры**: I/O операции часто блокируют потоки в ожидании ответа (сеть/диск), поэтому допустимо иметь существенно больше потоков, чем ядер, так как они большую часть времени простаивают. CPU операции полностью используют ядра, поэтому избыток потоков приводит к накладным расходам на переключение контекста.

| Аспект | Dispatchers.IO | Dispatchers.Default |
|--------|----------------|---------------------|
| **Назначение** | I/O операции (network, disk, DB) | CPU-intensive вычисления |
| **Размер пула** | Существенно больше числа ядер; реализация использует разделённый пул с ограничением, зависящим от версии (детали не стабильны) | Примерно = числу CPU ядер |
| **Тип задач** | Блокирующие I/O операции | Парсинг, сортировка, шифрование |
| **Пример** | `readFile()`, `apiCall()` | `sortList()`, `parseJson()` |
| **`Thread` starvation** | Менее чувствителен (больше потоков) | Высокий риск при блокирующем I/O |

### Сводка

- Используйте `Dispatchers.IO`, когда задачи могут блокироваться или долго ждать I/O.
- Используйте `Dispatchers.Default`, когда работа CPU-интенсивная и неблокирующая.

### Dispatchers.IO - Для I/O Операций

```kotlin
// - Network-запросы (блокирующие или когда библиотека так рекомендует)
suspend fun loadUser(id: Int): User = withContext(Dispatchers.IO) {
    apiService.getUser(id)
}

// - Чтение файлов
suspend fun readConfig(): Config = withContext(Dispatchers.IO) {
    File("config.json").readText().let { json ->
        Json.decodeFromString<Config>(json)
    }
}

// - Database операции (блокирующие драйверы, raw SQL и т.п.)
suspend fun saveUser(user: User) = withContext(Dispatchers.IO) {
    database.userDao().insert(user)
}
```

**Характеристики Dispatchers.IO**:
- Оптимизирован для блокирующих I/O операций.
- Может обслуживать много одновременных задач за счёт большего пула потоков.
- Потоки проводят много времени в состоянии ожидания (waiting).
- Реализован поверх общего пула; точное максимальное количество потоков является деталью реализации.

### Dispatchers.Default - Для CPU Работы

```kotlin
// - Парсинг больших JSON
suspend fun parseData(json: String): Data = withContext(Dispatchers.Default) {
    Json.decodeFromString<Data>(json) // CPU-intensive
}

// - Сортировка больших списков
suspend fun sortUsers(users: List<User>): List<User> = withContext(Dispatchers.Default) {
    users.sortedBy { it.name }
}

// - Обработка изображений
suspend fun processImage(bitmap: Bitmap): Bitmap = withContext(Dispatchers.Default) {
    applyFilters(bitmap) // CPU-intensive
}

// - Шифрование
suspend fun encryptData(data: ByteArray): ByteArray = withContext(Dispatchers.Default) {
    cipher.doFinal(data)
}
```

**Характеристики Dispatchers.Default**:
- Размер пула примерно равен количеству CPU ядер.
- Оптимизирован для CPU-intensive вычислений.
- Используется по умолчанию для `launch`/`async` без явного диспетчера (в не-UI контекстах).
- Потоки активно используют CPU; блокирующие вызовы здесь особенно опасны.

### Почему Размер Пула Разный?

```kotlin
// IO операции — потоки ЖДУТ ответа
suspend fun loadFromNetwork() = withContext(Dispatchers.IO) {
    httpClient.get("https://api.example.com/data")
    // CPU почти не используется, поэтому допустимо больше потоков
}

// CPU операции — потоки РАБОТАЮТ
suspend fun computeResult() = withContext(Dispatchers.Default) {
    (1..1_000_000).sumOf { it * it }
    // Избыток потоков над числом ядер = context switching overhead
}
```

**Вывод**:
- IO: много одновременно работающих задач допустимо — они в основном ждут, не нагружая CPU.
- Default: количество потоков ограничено ядрами CPU для максимальной эффективности; блокирующие операции здесь приводят к starvation.

### Практические Примеры

#### `ViewModel` С Разными Диспетчерами

```kotlin
class UserViewModel(
    private val userRepository: UserRepository
) : ViewModel() {

    fun loadUser(id: Int) {
        viewModelScope.launch {
            _isLoading.value = true

            try {
                // 1. Network-запрос — IO (если блокирующий или тяжёлый)
                val userDto = withContext(Dispatchers.IO) {
                    userApi.getUser(id)
                }

                // 2. Парсинг и маппинг — Default (если нетривиальный)
                val user = withContext(Dispatchers.Default) {
                    mapDtoToUser(userDto)
                }

                // 3. Сохранение в БД — IO (если операция блокирующая)
                withContext(Dispatchers.IO) {
                    database.userDao().insert(user)
                }

                // 4. Обновление UI — Main (автоматический возврат в viewModelScope)
                _user.value = user

            } finally {
                _isLoading.value = false
            }
        }
    }

    fun processUserData(data: String) {
        viewModelScope.launch {
            // CPU-intensive парсинг — Default
            val parsed = withContext(Dispatchers.Default) {
                parseComplexData(data)
            }

            // IO операция сохранения — IO
            withContext(Dispatchers.IO) {
                saveToFile(parsed)
            }
            // После выполнения withContext(...) выполнение автоматически возвращается на Main,
            // поэтому состояние UI можно обновлять без явного переключения.
        }
    }
}
```

#### Repository Pattern

```kotlin
class UserRepository(
    private val api: UserApi,
    private val database: UserDao,
    private val cache: UserCache
) {
    // Network + Database: явно выбираем подходящий диспетчер для блокирующих операций
    suspend fun getUser(id: Int): User = withContext(Dispatchers.IO) {
        val userDto = api.getUser(id)
        database.insertUser(userDto.toEntity())
        userDto.toDomainModel()
    }

    // Явное указание IO для I/O-операций
    suspend fun syncUsers() = withContext(Dispatchers.IO) {
        val remoteUsers = api.getAllUsers()
        database.insertAll(remoteUsers.map { it.toEntity() })
    }

    // CPU-intensive обработка — Default
    suspend fun analyzeUserBehavior(userId: Int): Analytics = withContext(Dispatchers.Default) {
        val events = database.getUserEvents(userId)
        calculateAnalytics(events) // Complex computation
    }
}
```

### Ошибки И Антипаттерны

- Использование IO для CPU работы:

```kotlin
// НЕПРАВИЛЬНО — раздувает IO pool и мешает I/O задачам
suspend fun sortLargeList(items: List<Int>): List<Int> = withContext(Dispatchers.IO) {
    items.sorted() // CPU-intensive, не I/O!
}

// ПРАВИЛЬНО
suspend fun sortLargeList(items: List<Int>): List<Int> = withContext(Dispatchers.Default) {
    items.sorted()
}
```

- Использование Default для I/O:

```kotlin
// НЕПРАВИЛЬНО — блокирует ограниченный CPU pool
suspend fun loadFile(): String = withContext(Dispatchers.Default) {
    File("data.txt").readText() // Блокирующий I/O!
}

// ПРАВИЛЬНО
suspend fun loadFile(): String = withContext(Dispatchers.IO) {
    File("data.txt").readText()
}
```

- Вложенный `withContext` без необходимости (лишние переключения контекстов):

```kotlin
// Избыточные переключения контекста
suspend fun processData() = withContext(Dispatchers.IO) {
    val data = loadData() // Уже в IO

    withContext(Dispatchers.IO) { // Уже в IO!
        saveData(data)
    }
}

// ПРАВИЛЬНО
suspend fun processData() = withContext(Dispatchers.IO) {
    val data = loadData()
    saveData(data) // Уже в правильном контексте
}
```

### Dispatchers.Main - Бонус Для Android

```kotlin
class MainActivity : AppCompatActivity() {
    fun updateUI() {
        lifecycleScope.launch {
            // Запускается на Main (по умолчанию в lifecycleScope)

            // I/O работа
            val data = withContext(Dispatchers.IO) {
                loadFromNetwork()
            }

            // CPU работа
            val processed = withContext(Dispatchers.Default) {
                processData(data)
            }

            // Обратно на Main для UI (автоматически)
            textView.text = processed
        }
    }
}
```

**Dispatchers.Main** (Android/UI):
- Выполняется на Main/UI потоке.
- Нельзя делать тяжёлую работу.
- Только быстрые операции и UI-обновления.
- При запуске из `viewModelScope`/`lifecycleScope` код после внутренних `withContext(Dispatchers.IO/Default)` автоматически продолжает выполняться на Main, поэтому не нужно вручную переключаться обратно.

### Thread Pool Exhaustion

Ключевая идея: блокирующие операции в Default (или Main) могут привести к starvation ограниченного пула.

```kotlin
// Опасность: забить весь Default pool блокирующими операциями
suspend fun riskyOperation() = coroutineScope {
    (1..100).map {
        async(Dispatchers.Default) {
            Thread.sleep(10_000) // Блокирует поток! Только для демонстрации проблемы.
            heavyComputation()
        }
    }.awaitAll()
}

// Проблема: если Default pool = 4 потока
// - Первые 4 задачи блокируют все потоки
// - Остальные 96 ждут
// - Thread starvation

// Решение 1: используйте IO для блокирующих операций
suspend fun fixedWithIO() = coroutineScope {
    (1..100).map {
        async(Dispatchers.IO) {
            Thread.sleep(10_000) // Илллюстрация; в реальном коде лучше suspend-API
            heavyComputation()
        }
    }.awaitAll()
}

// Решение 2: используйте suspend вместо блокировки
suspend fun fixedWithSuspend() = coroutineScope {
    (1..100).map {
        async(Dispatchers.Default) {
            delay(10_000) // Не блокирует поток
            heavyComputation()
        }
    }.awaitAll()
}

// Решение 3: ограничьте параллелизм (пример: chunked)
suspend fun fixedWithLimit() = coroutineScope {
    (1..100).chunked(4).forEach { chunk ->
        chunk.map {
            async(Dispatchers.Default) {
                heavyComputation()
            }
        }.awaitAll()
    }
}
```

### Настройка Размера Пулов

```kotlin
// Важно: детали настройки внутренних пулов Dispatchers.IO/Default являются деталями реализации
// kotlinx.coroutines; следует опираться на документацию конкретной версии.

// По умолчанию (обобщённо, может меняться):
// - IO: использует общий пул с верхней границей по числу потоков (значение порядка десятков + число ядер).
// - Default: количество потоков примерно равно числу CPU ядер.

fun checkDispatchers() {
    println("Default pool size (approx): ${Runtime.getRuntime().availableProcessors()}")
    // Точный размер IO pool получить напрямую нельзя; он скрыт за API.
}
```

### limitedParallelism - Создание Ограниченных Dispatcher-ов

```kotlin
// Создаём dispatcher с ограниченным параллелизмом поверх IO
val databaseDispatcher = Dispatchers.IO.limitedParallelism(1)
// Только 1 одновременно выполняющаяся задача — сериализованный доступ к БД

class DatabaseManager {
    private val singleThreadDispatcher = Dispatchers.IO.limitedParallelism(1)

    suspend fun write(data: Data) = withContext(singleThreadDispatcher) {
        // Гарантированно последовательное выполнение (до указанного лимита)
        database.write(data)
    }
}

// Пул для heavy operations
val heavyWorkDispatcher = Dispatchers.Default.limitedParallelism(2)

suspend fun processImages(images: List<Bitmap>) = coroutineScope {
    images.map { bitmap ->
        async(heavyWorkDispatcher) {
            // Максимум 2 изображения параллельно
            processImage(bitmap)
        }
    }.awaitAll()
}
```

### Комбинирование Диспетчеров

```kotlin
suspend fun complexWorkflow() = coroutineScope {
    // 1. Загружаем данные — IO
    val rawData = withContext(Dispatchers.IO) {
        downloadFromServer()
    }

    // 2. Парсим — Default
    val parsed = withContext(Dispatchers.Default) {
        parseJson(rawData)
    }

    // 3. Обрабатываем изображения — Default
    val processedImages = withContext(Dispatchers.Default) {
        parsed.images.map { processImage(it) }
    }

    // 4. Сохраняем результат — IO
    withContext(Dispatchers.IO) {
        database.save(parsed, processedImages)
    }

    // 5. Обновляем UI — Main (если вызывается из UI scope)
    updateUI(parsed)
}
```

### Dispatchers И `Flow`

```kotlin
flow {
    emit(loadFromDisk()) // Выполнится на dispatcher до первого flowOn (ниже — IO)
}
.flowOn(Dispatchers.IO) // Всё выше по цепочке будет выполняться на IO
.map { data ->
    parseData(data)
}
.flowOn(Dispatchers.Default) // Всё выше этого вызова (включая map) — на Default
.collect { parsed ->
    updateUI(parsed) // Выполняется на dispatcher коллектора (например, Main)
}
```

### Production Пример

```kotlin
class ArticleRepository(
    private val api: ArticleApi,
    private val database: ArticleDao,
    private val imageProcessor: ImageProcessor
) {
    suspend fun loadAndProcessArticle(id: Int): Article = coroutineScope {
        // 1. Параллельно загружаем статью и изображения — IO
        val articleDeferred = async(Dispatchers.IO) {
            api.getArticle(id)
        }

        val imagesDeferred = async(Dispatchers.IO) {
            api.getArticleImages(id)
        }

        val articleDto = articleDeferred.await()
        val images = imagesDeferred.await()

        // 2. Обрабатываем изображения — Default (CPU-intensive)
        val processedImages = withContext(Dispatchers.Default) {
            images.map { image ->
                imageProcessor.process(image)
            }
        }

        // 3. Маппим DTO -> Domain model — Default
        val article = withContext(Dispatchers.Default) {
            Article(
                id = articleDto.id,
                title = articleDto.title,
                content = parseMarkdown(articleDto.content), // CPU-intensive
                images = processedImages
            )
        }

        // 4. Сохраняем в БД — IO
        withContext(Dispatchers.IO) {
            database.insertArticle(article.toEntity())
        }

        article
    }

    // Stream данных с правильным диспетчером
    fun observeArticles(): Flow<List<Article>> {
        return database.observeArticles() // Room Flow
            .map { entities ->
                entities.map { it.toDomainModel() }
            }
            .flowOn(Dispatchers.Default)
    }
}
```

### Тестирование

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class RepositoryTest {
    @Test
    fun `test IO dispatcher usage`() = runTest {
        val repository = UserRepository(mockApi, mockDatabase, mockCache)

        // runTest использует TestScope и TestDispatcher для корутин, запущенных внутри него.
        // Если production-код жёстко использует Dispatchers.IO/Default, тестировать сложнее,
        // поэтому лучше передавать dispatcher-ы через конструктор/интерфейс.
        val user = repository.getUser(1)

        assertEquals("Alice", user.name)
    }

    @Test
    fun `test with custom dispatcher`() = runTest {
        val testDispatcher = StandardTestDispatcher(testScheduler)
        Dispatchers.setMain(testDispatcher)

        val viewModel = UserViewModel(repository)
        viewModel.loadUser(1)

        // Продвигаем все корутины до завершения
        advanceUntilIdle()

        assertEquals(UserState.Loaded, viewModel.state.value)
    }
}
```

## Answer (EN)

Dispatchers.IO and Dispatchers.Default are two built-in coroutine dispatchers backed by different thread pool configurations and optimized for different types of work.

### Key Differences

- Dispatchers.IO:
  - Target: I/O-bound operations (network, disk, database, blocking system calls).
  - `Thread` pool: shared pool that may use significantly more threads than CPU cores; the exact max size is implementation-specific and may change between kotlinx.coroutines versions.
  - Rationale: many tasks are blocked waiting for I/O, so having more threads is acceptable.

- Dispatchers.Default:
  - Target: CPU-bound work (parsing, sorting, image processing, encryption, heavy calculations).
  - `Thread` pool: approximately equal to the number of CPU cores.
  - Rationale: threads are busy doing computations; too many threads cause context switches and reduce throughput.

Summary:
- Use IO when threads may block or wait on slow I/O.
- Use Default when work is CPU-heavy and non-blocking.

### Dispatchers.IO – For I/O Operations

Examples of correct usage:

```kotlin
// Network requests (blocking or as recommended by the client)
suspend fun loadUser(id: Int): User = withContext(Dispatchers.IO) {
    apiService.getUser(id)
}

// File I/O
suspend fun readConfig(): Config = withContext(Dispatchers.IO) {
    File("config.json").readText().let { json ->
        Json.decodeFromString<Config>(json)
    }
}

// Database (blocking drivers / DAO calls)
suspend fun saveUser(user: User) = withContext(Dispatchers.IO) {
    database.userDao().insert(user)
}
```

Use IO for:
- Network calls when the client is blocking or library recommends IO.
- File read/write.
- `Database` access.
- `SharedPreferences` commit.
- Other blocking or slow system calls (examples using `Thread.sleep` are for demonstration; prefer suspend-friendly APIs).

### Dispatchers.Default – For CPU-bound Work

Examples of correct usage:

```kotlin
// Heavy JSON parsing
suspend fun parseData(json: String): Data = withContext(Dispatchers.Default) {
    Json.decodeFromString<Data>(json)
}

// Sorting large collections
suspend fun sortUsers(users: List<User>): List<User> = withContext(Dispatchers.Default) {
    users.sortedBy { it.name }
}

// Image processing
suspend fun processImage(bitmap: Bitmap): Bitmap = withContext(Dispatchers.Default) {
    applyFilters(bitmap)
}

// Encryption
suspend fun encryptData(data: ByteArray): ByteArray = withContext(Dispatchers.Default) {
    cipher.doFinal(data)
}
```

Use Default for:
- Parsing, transformation, mapping of large data sets.
- Image / media processing.
- Encryption / decryption.
- Numerical and other CPU-intensive algorithms.

### Why Are Pool Sizes Different?

```kotlin
// I/O: threads mostly WAIT
suspend fun loadFromNetwork() = withContext(Dispatchers.IO) {
    httpClient.get("https://api.example.com/data")
}

// CPU: threads actively WORK
suspend fun computeResult() = withContext(Dispatchers.Default) {
    (1..1_000_000).sumOf { it * it }
}
```

- IO can safely use many threads because they are often blocked and not consuming CPU.
- Default keeps threads near the CPU core count to avoid contention and context switching.

### Practical Patterns

#### `ViewModel` With Multiple Dispatchers

```kotlin
class UserViewModel(
    private val userRepository: UserRepository
) : ViewModel() {

    fun loadUser(id: Int) {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val userDto = withContext(Dispatchers.IO) {
                    userApi.getUser(id)
                }

                val user = withContext(Dispatchers.Default) {
                    mapDtoToUser(userDto)
                }

                withContext(Dispatchers.IO) {
                    database.userDao().insert(user)
                }

                _user.value = user
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun processUserData(data: String) {
        viewModelScope.launch {
            val parsed = withContext(Dispatchers.Default) { parseComplexData(data) }
            withContext(Dispatchers.IO) { saveToFile(parsed) }
        }
    }
}
```

Note: when you start in `viewModelScope` or `lifecycleScope` on `Dispatchers.Main`, after inner `withContext(Dispatchers.IO/Default)` blocks complete, execution automatically returns to the original Main dispatcher, so you can safely update UI state without manually switching back.

#### Repository Pattern

```kotlin
class UserRepository(
    private val api: UserApi,
    private val database: UserDao,
    private val cache: UserCache
) {
    // Network + Database: pick IO for blocking operations
    suspend fun getUser(id: Int): User = withContext(Dispatchers.IO) {
        val userDto = api.getUser(id)
        database.insertUser(userDto.toEntity())
        userDto.toDomainModel()
    }

    suspend fun syncUsers() = withContext(Dispatchers.IO) {
        val remoteUsers = api.getAllUsers()
        database.insertAll(remoteUsers.map { it.toEntity() })
    }

    // CPU-intensive processing — Default
    suspend fun analyzeUserBehavior(userId: Int): Analytics = withContext(Dispatchers.Default) {
        val events = database.getUserEvents(userId)
        calculateAnalytics(events)
    }
}
```

### Common Mistakes and Anti-patterns

- Using IO for CPU-heavy work:

```kotlin
// Wrong: bloats IO pool
suspend fun sortLargeList(items: List<Int>): List<Int> = withContext(Dispatchers.IO) {
    items.sorted()
}

// Correct
suspend fun sortLargeList(items: List<Int>): List<Int> = withContext(Dispatchers.Default) {
    items.sorted()
}
```

- Using Default for blocking I/O:

```kotlin
// Wrong: blocks limited CPU pool
suspend fun loadFile(): String = withContext(Dispatchers.Default) {
    File("data.txt").readText()
}

// Correct
suspend fun loadFile(): String = withContext(Dispatchers.IO) {
    File("data.txt").readText()
}
```

- Nested `withContext` with the same dispatcher:

```kotlin
suspend fun processData() = withContext(Dispatchers.IO) {
    val data = loadData()
    // No need for another withContext(Dispatchers.IO)
    saveData(data)
}
```

### Dispatchers.Main (Android bonus)

```kotlin
class MainActivity : AppCompatActivity() {
    fun updateUI() {
        lifecycleScope.launch {
            val data = withContext(Dispatchers.IO) { loadFromNetwork() }
            val processed = withContext(Dispatchers.Default) { processData(data) }
            // Returned to Main automatically after withContext
            textView.text = processed
        }
    }
}
```

- Main is for quick UI work only; delegate heavy tasks to IO/Default.
- When started on Main (e.g., `viewModelScope`, `lifecycleScope`), code after `withContext(Dispatchers.IO/Default)` resumes on Main automatically.

### Thread Pool Exhaustion

Key idea: blocking calls in Default (or Main) can starve the limited pool.

```kotlin
suspend fun riskyOperation() = coroutineScope {
    (1..100).map {
        async(Dispatchers.Default) {
            Thread.sleep(10_000) // Blocks thread — demonstration only.
            heavyComputation()
        }
    }.awaitAll()
}
```

Better approaches:
- Use IO for blocking calls (while preferring non-blocking APIs when available).
- Prefer suspend-friendly APIs (`delay` instead of `Thread.sleep`) so threads are not blocked.
- Limit concurrency explicitly (e.g., chunking, semaphores, or `limitedParallelism`).

### Pool Configuration

Defaults (high-level, implementation may change):
- IO: uses a shared pool with an upper bound on threads; more than CPU cores.
- Default: about number of CPU cores.

### limitedParallelism – Creating Constrained Dispatchers

```kotlin
// Constrain parallelism on top of IO
val singleDbDispatcher = Dispatchers.IO.limitedParallelism(1)

class DatabaseManager {
    private val singleThreadDispatcher = Dispatchers.IO.limitedParallelism(1)

    suspend fun write(data: Data) = withContext(singleThreadDispatcher) {
        // Sequential (up to the limit) DB access
        database.write(data)
    }
}

// Pool for heavy work
val heavyWorkDispatcher = Dispatchers.Default.limitedParallelism(2)

suspend fun processImages(images: List<Bitmap>) = coroutineScope {
    images.map { bitmap ->
        async(heavyWorkDispatcher) {
            // At most 2 images in parallel
            processImage(bitmap)
        }
    }.awaitAll()
}
```

### Dispatchers and `Flow`

```kotlin
flow {
    emit(loadFromDisk())
}
.flowOn(Dispatchers.IO) // upstream I/O on IO
.map { data -> parseData(data) }
.flowOn(Dispatchers.Default) // heavy mapping on Default
.collect { parsed ->
    updateUI(parsed) // collector context (e.g., Main)
}
```

### Production-style Example

```kotlin
class ArticleRepository(
    private val api: ArticleApi,
    private val database: ArticleDao,
    private val imageProcessor: ImageProcessor
) {
    suspend fun loadAndProcessArticle(id: Int): Article = coroutineScope {
        val articleDeferred = async(Dispatchers.IO) { api.getArticle(id) }
        val imagesDeferred = async(Dispatchers.IO) { api.getArticleImages(id) }

        val articleDto = articleDeferred.await()
        val images = imagesDeferred.await()

        val processedImages = withContext(Dispatchers.Default) {
            images.map { imageProcessor.process(it) }
        }

        val article = withContext(Dispatchers.Default) {
            Article(
                id = articleDto.id,
                title = articleDto.title,
                content = parseMarkdown(articleDto.content),
                images = processedImages
            )
        }

        withContext(Dispatchers.IO) {
            database.insertArticle(article.toEntity())
        }

        article
    }

    fun observeArticles(): Flow<List<Article>> {
        return database.observeArticles()
            .map { entities -> entities.map { it.toDomainModel() } }
            .flowOn(Dispatchers.Default)
    }
}
```

### Testing Notes

- Prefer injecting dispatchers (e.g., via constructor or provider) instead of hard-coding `Dispatchers.IO`/`Dispatchers.Default`.
- Use `runTest` and `TestDispatcher`/`StandardTestDispatcher` to control coroutine execution.

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class RepositoryTest {
    @Test
    fun `test IO dispatcher usage`() = runTest {
        val repository = UserRepository(mockApi, mockDatabase, mockCache)

        // runTest uses a TestScope and TestDispatcher inside.
        // If production code hardcodes Dispatchers.IO/Default, passing dispatchers via constructor
        // or an interface makes testing easier.
        val user = repository.getUser(1)

        assertEquals("Alice", user.name)
    }

    @Test
    fun `test with custom dispatcher`() = runTest {
        val testDispatcher = StandardTestDispatcher(testScheduler)
        Dispatchers.setMain(testDispatcher)

        val viewModel = UserViewModel(repository)
        viewModel.loadUser(1)

        // Move virtual time until all coroutines complete
        advanceUntilIdle()

        assertEquals(UserState.Loaded, viewModel.state.value)
    }
}
```

## Дополнительные Вопросы (RU)
- В чем ключевые отличия по сравнению с потоками и executors в Java?
- Когда вы бы использовали эти диспетчеры в реальных Android или backend-приложениях?
- Какие типичные ошибки стоит избегать при переключении диспетчеров?

## Follow-ups

- What are the key differences between this and Java threading/executors?
- When would you use these dispatchers in real-world Android or backend apps?
- What are common pitfalls to avoid when switching dispatchers?

## Ссылки (RU)

- [Kotlin Документация](https://kotlinlang.org/docs/home.html)
- [[c-concurrency]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-concurrency]]

## Связанные Вопросы (RU)

- [[q-infix-functions--kotlin--medium]]
- [[q-coroutine-scope-basics--kotlin--easy]]
- [[q-request-coalescing-deduplication--kotlin--hard]]

## Related Questions

- [[q-infix-functions--kotlin--medium]]
- [[q-coroutine-scope-basics--kotlin--easy]]
- [[q-request-coalescing-deduplication--kotlin--hard]]
