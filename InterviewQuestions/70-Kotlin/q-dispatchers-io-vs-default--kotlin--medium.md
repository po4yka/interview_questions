---
tags:
  - kotlin
  - coroutines
  - dispatchers
  - threading
  - concurrency
difficulty: medium
status: reviewed
---

# Dispatchers.IO vs Dispatchers.Default

**English**: What's the difference between Dispatchers.IO and Dispatchers.Default? When should you use each?

## Answer

**Dispatchers.IO** и **Dispatchers.Default** - два предустановленных диспетчера для выполнения корутин на разных thread pools с разными характеристиками:

| Аспект | Dispatchers.IO | Dispatchers.Default |
|--------|----------------|---------------------|
| **Назначение** | I/O операции (network, disk, DB) | CPU-intensive вычисления |
| **Размер пула** | 64+ потоков (динамический) | Кол-во CPU ядер (обычно 4-8) |
| **Тип задач** | Блокирующие I/O операции | Парсинг, сортировка, шифрование |
| **Пример** | `readFile()`, `apiCall()` | `sortList()`, `parseJson()` |
| **Thread starvation** | Устойчив (большой пул) | Опасен при блокирующих операциях |

### Dispatchers.IO - для I/O операций

```kotlin
// ✅ Network запросы
suspend fun loadUser(id: Int): User = withContext(Dispatchers.IO) {
    apiService.getUser(id) // Блокирующий HTTP call
}

// ✅ Чтение файлов
suspend fun readConfig(): Config = withContext(Dispatchers.IO) {
    File("config.json").readText().let { json ->
        Json.decodeFromString(it)
    }
}

// ✅ Database операции
suspend fun saveUser(user: User) = withContext(Dispatchers.IO) {
    database.userDao().insert(user)
}
```

**Характеристики Dispatchers.IO**:
- 📊 Размер пула: **64 потока** (по умолчанию, можно увеличить)
- ⏸️ Оптимизирован для **блокирующих** I/O операций
- 🔄 Динамически расширяется при необходимости
- ⚡ Потоки проводят много времени в состоянии ожидания (waiting)

### Dispatchers.Default - для CPU работы

```kotlin
// ✅ Парсинг больших JSON
suspend fun parseData(json: String): Data = withContext(Dispatchers.Default) {
    Json.decodeFromString<Data>(json) // CPU-intensive
}

// ✅ Сортировка больших списков
suspend fun sortUsers(users: List<User>): List<User> = withContext(Dispatchers.Default) {
    users.sortedBy { it.name }
}

// ✅ Обработка изображений
suspend fun processImage(bitmap: Bitmap): Bitmap = withContext(Dispatchers.Default) {
    applyFilters(bitmap) // CPU-intensive
}

// ✅ Шифрование
suspend fun encryptData(data: ByteArray): ByteArray = withContext(Dispatchers.Default) {
    cipher.doFinal(data)
}
```

**Характеристики Dispatchers.Default**:
- 📊 Размер пула: **равен количеству CPU ядер** (обычно 4-8)
- 💻 Оптимизирован для **CPU-intensive** вычислений
- 🚫 НЕ расширяется динамически
- ⚡ Потоки активно используют CPU

### Почему размер пула разный?

```kotlin
// IO операции - потоки ЖДУТ ответа
suspend fun loadFromNetwork() = withContext(Dispatchers.IO) {
    // Поток заблокирован в ожидании network response
    httpClient.get("https://api.example.com/data")
    // CPU не используется! Можем безопасно иметь много потоков
}

// CPU операции - потоки РАБОТАЮТ
suspend fun computeResult() = withContext(Dispatchers.Default) {
    // Поток активно использует CPU для вычислений
    (1..1_000_000).sumOf { it * it }
    // Больше потоков чем ядер CPU = context switching overhead
}
```

**Вывод**:
- **IO**: Много потоков OK - они в основном ждут, не нагружают CPU
- **Default**: Потоков = ядрам CPU - максимальная эффективность без overhead

### Практические примеры

#### ViewModel с разными диспетчерами

```kotlin
class UserViewModel(
    private val userRepository: UserRepository
) : ViewModel() {

    fun loadUser(id: Int) {
        viewModelScope.launch {
            _isLoading.value = true

            try {
                // 1. Network запрос - IO
                val userDto = withContext(Dispatchers.IO) {
                    userApi.getUser(id)
                }

                // 2. Парсинг и маппинг - Default (если сложный)
                val user = withContext(Dispatchers.Default) {
                    mapDtoToUser(userDto)
                }

                // 3. Сохранение в БД - IO
                withContext(Dispatchers.IO) {
                    database.userDao().insert(user)
                }

                // 4. Обновление UI - Main (автоматически)
                _user.value = user

            } finally {
                _isLoading.value = false
            }
        }
    }

    fun processUserData(data: String) {
        viewModelScope.launch {
            // CPU-intensive парсинг - Default
            val parsed = withContext(Dispatchers.Default) {
                parseComplexData(data)
            }

            // IO операция сохранения - IO
            withContext(Dispatchers.IO) {
                saveToFile(parsed)
            }
        }
    }
}
```

#### Repository pattern

```kotlin
class UserRepository(
    private val api: UserApi,
    private val database: UserDao,
    private val cache: UserCache
) {
    // Network + Database - автоматически используют IO
    suspend fun getUser(id: Int): User {
        // Retrofit автоматически использует IO dispatcher
        val userDto = api.getUser(id)

        // Room автоматически использует IO dispatcher
        database.insertUser(userDto.toEntity())

        return userDto.toDomainModel()
    }

    // Явное указание IO для custom операций
    suspend fun syncUsers() = withContext(Dispatchers.IO) {
        val remoteUsers = api.getAllUsers()
        database.insertAll(remoteUsers.map { it.toEntity() })
    }

    // CPU-intensive обработка - Default
    suspend fun analyzeUserBehavior(userId: Int): Analytics = withContext(Dispatchers.Default) {
        val events = database.getUserEvents(userId)
        calculateAnalytics(events) // Complex computation
    }
}
```

### Когда использовать IO

```kotlin
// ✅ Network запросы
withContext(Dispatchers.IO) {
    httpClient.get("https://api.com/data")
}

// ✅ Чтение/запись файлов
withContext(Dispatchers.IO) {
    File("data.txt").writeText("content")
}

// ✅ Database операции
withContext(Dispatchers.IO) {
    database.query("SELECT * FROM users")
}

// ✅ SharedPreferences (хоть и быстро, но I/O)
withContext(Dispatchers.IO) {
    preferences.edit().putString("key", "value").commit()
}

// ✅ Блокирующие системные вызовы
withContext(Dispatchers.IO) {
    Thread.sleep(1000) // Блокирующая операция
}
```

### Когда использовать Default

```kotlin
// ✅ Парсинг JSON/XML
withContext(Dispatchers.Default) {
    Json.decodeFromString<User>(jsonString)
}

// ✅ Сортировка больших коллекций
withContext(Dispatchers.Default) {
    list.sortedWith(complexComparator)
}

// ✅ Обработка изображений
withContext(Dispatchers.Default) {
    bitmap.applyColorFilter()
}

// ✅ Шифрование/дешифрование
withContext(Dispatchers.Default) {
    cipher.encrypt(data)
}

// ✅ Сложные вычисления
withContext(Dispatchers.Default) {
    calculateComplexFormula(params)
}

// ✅ Маппинг больших структур данных
withContext(Dispatchers.Default) {
    users.map { it.toDto() }
}
```

### Ошибки и антипаттерны

#### ❌ Использование IO для CPU работы

```kotlin
// ❌ НЕПРАВИЛЬНО - забивает IO pool
suspend fun sortLargeList(items: List<Int>): List<Int> = withContext(Dispatchers.IO) {
    items.sorted() // CPU-intensive, не I/O!
}

// Проблема:
// - Блокируем IO поток для CPU работы
// - Другие I/O операции могут ждать
// - Неоптимальное использование ресурсов

// ✅ ПРАВИЛЬНО
suspend fun sortLargeList(items: List<Int>): List<Int> = withContext(Dispatchers.Default) {
    items.sorted()
}
```

#### ❌ Использование Default для I/O

```kotlin
// ❌ НЕПРАВИЛЬНО - блокирует CPU threads
suspend fun loadFile(): String = withContext(Dispatchers.Default) {
    File("data.txt").readText() // Блокирующий I/O!
}

// Проблема:
// - Блокируем ценный CPU поток для ожидания I/O
// - Если таких операций много - thread starvation
// - CPU threads должны ВЫЧИСЛЯТЬ, не ждать

// ✅ ПРАВИЛЬНО
suspend fun loadFile(): String = withContext(Dispatchers.IO) {
    File("data.txt").readText()
}
```

#### ❌ Nested withContext без необходимости

```kotlin
// ❌ Избыточные переключения контекста
suspend fun processData() = withContext(Dispatchers.IO) {
    val data = loadData() // Уже в IO

    withContext(Dispatchers.IO) { // ❌ Уже в IO!
        saveData(data)
    }
}

// ✅ ПРАВИЛЬНО
suspend fun processData() = withContext(Dispatchers.IO) {
    val data = loadData()
    saveData(data) // Уже в правильном контексте
}
```

### Dispatchers.Main - бонус для Android

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
- 📱 Выполняется на **Main/UI потоке**
- ⚠️ НЕЛЬЗЯ делать тяжелую работу
- ✅ Только UI обновления
- 🔄 Возврат на Main после withContext автоматический в viewModelScope/lifecycleScope

### Thread Pool Exhaustion

```kotlin
// Опасность: забить весь Default pool
suspend fun riskyOperation() = coroutineScope {
    // Запускаем 100 CPU-intensive задач
    (1..100).map {
        async(Dispatchers.Default) {
            Thread.sleep(10000) // ❌ Блокирует поток!
            heavyComputation()
        }
    }.awaitAll()
}

// Проблема: если Default pool = 4 потока
// - Первые 4 задачи блокируют все потоки
// - Остальные 96 ждут
// - Thread starvation!

// ✅ Решение 1: используйте IO для блокирующих операций
suspend fun fixedWithIO() = coroutineScope {
    (1..100).map {
        async(Dispatchers.IO) {
            Thread.sleep(10000) // IO pool больше
            heavyComputation()
        }
    }.awaitAll()
}

// ✅ Решение 2: используйте suspend вместо блокировки
suspend fun fixedWithSuspend() = coroutineScope {
    (1..100).map {
        async(Dispatchers.Default) {
            delay(10000) // ✅ Не блокирует!
            heavyComputation()
        }
    }.awaitAll()
}

// ✅ Решение 3: ограничьте параллелизм
suspend fun fixedWithLimit() {
    (1..100).chunked(4).forEach { chunk ->
        chunk.map {
            async(Dispatchers.Default) {
                heavyComputation()
            }
        }.awaitAll()
    }
}
```

### Настройка размера пулов

```kotlin
// Настройка IO pool
System.setProperty("kotlinx.coroutines.io.parallelism", "128")

// По умолчанию:
// - IO: max(64, количество CPU ядер)
// - Default: количество CPU ядер

// Проверка текущих значений
fun checkDispatchers() {
    println("Default pool size: ${Runtime.getRuntime().availableProcessors()}")
    // IO pool size узнать нельзя напрямую, но обычно 64
}
```

### limitedParallelism - создание custom пулов

```kotlin
// Создаем dispatcher с ограниченным параллелизмом
val databaseDispatcher = Dispatchers.IO.limitedParallelism(1)
// Только 1 поток - сериализованный доступ к БД

class DatabaseManager {
    private val singleThreadDispatcher = Dispatchers.IO.limitedParallelism(1)

    suspend fun write(data: Data) = withContext(singleThreadDispatcher) {
        // Гарантированно последовательное выполнение
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

### Комбинирование диспетчеров

```kotlin
suspend fun complexWorkflow() {
    // 1. Загружаем данные - IO
    val rawData = withContext(Dispatchers.IO) {
        downloadFromServer()
    }

    // 2. Парсим - Default
    val parsed = withContext(Dispatchers.Default) {
        parseJson(rawData)
    }

    // 3. Обрабатываем изображения - Default
    val processedImages = withContext(Dispatchers.Default) {
        parsed.images.map { processImage(it) }
    }

    // 4. Сохраняем результат - IO
    withContext(Dispatchers.IO) {
        database.save(parsed, processedImages)
    }

    // 5. Обновляем UI - Main (автоматически если в lifecycleScope)
    updateUI(parsed)
}
```

### Dispatchers и Flow

```kotlin
flow {
    emit(loadFromDisk()) // Откуда выполняется?
}
.flowOn(Dispatchers.IO) // ✅ Все выше flowOn - на IO
.map { data ->
    parseData(data) // ❌ Выполняется на том же диспетчере что и collect
}
.flowOn(Dispatchers.Default) // ✅ map теперь на Default
.collect { parsed ->
    updateUI(parsed) // Выполняется на диспетчере вызывающего (Main)
}
```

### Production пример

```kotlin
class ArticleRepository(
    private val api: ArticleApi,
    private val database: ArticleDao,
    private val imageProcessor: ImageProcessor
) {
    suspend fun loadAndProcessArticle(id: Int): Article = coroutineScope {
        // 1. Параллельно загружаем статью и изображения - IO
        val articleDeferred = async(Dispatchers.IO) {
            api.getArticle(id)
        }

        val imagesDeferred = async(Dispatchers.IO) {
            api.getArticleImages(id)
        }

        val articleDto = articleDeferred.await()
        val images = imagesDeferred.await()

        // 2. Обрабатываем изображения - Default (CPU-intensive)
        val processedImages = withContext(Dispatchers.Default) {
            images.map { image ->
                imageProcessor.process(image)
            }
        }

        // 3. Маппим DTO -> Domain model - Default
        val article = withContext(Dispatchers.Default) {
            Article(
                id = articleDto.id,
                title = articleDto.title,
                content = parseMarkdown(articleDto.content), // CPU-intensive
                images = processedImages
            )
        }

        // 4. Сохраняем в БД - IO
        withContext(Dispatchers.IO) {
            database.insertArticle(article.toEntity())
        }

        article
    }

    // Stream данных с правильным диспетчером
    fun observeArticles(): Flow<List<Article>> {
        return database.observeArticles() // Room Flow
            .map { entities ->
                entities.map { it.toDomainModel() } // Маппинг на Default
            }
            .flowOn(Dispatchers.Default)
    }
}
```

### Тестирование

```kotlin
class RepositoryTest {
    @Test
    fun `test IO dispatcher usage`() = runTest {
        val repository = UserRepository(mockApi, mockDatabase)

        // runTest автоматически использует TestDispatcher
        // Все withContext(Dispatchers.IO) заменяются на test dispatcher
        val user = repository.getUser(1)

        assertEquals("Alice", user.name)
    }

    // Можно явно указать dispatcher для теста
    @OptIn(ExperimentalCoroutinesApi::class)
    @Test
    fun `test with custom dispatcher`() = runTest {
        val testDispatcher = StandardTestDispatcher(testScheduler)
        Dispatchers.setMain(testDispatcher)

        val viewModel = UserViewModel(repository)
        viewModel.loadUser(1)

        // Продвигаем время
        advanceUntilIdle()

        assertEquals(UserState.Loaded, viewModel.state.value)
    }
}
```

**English**: **Dispatchers.IO** and **Dispatchers.Default** are two thread pools optimized for different workloads:

**Dispatchers.IO**: For I/O-bound operations (network, disk, database). Thread pool size: 64+ threads (expandable). Use for: HTTP requests, file read/write, database queries, blocking system calls. Threads spend time waiting (not using CPU).

**Dispatchers.Default**: For CPU-bound computations. Thread pool size: number of CPU cores (4-8). Use for: JSON parsing, sorting large lists, image processing, encryption, complex calculations. Threads actively use CPU.

**Why different sizes**: IO operations block threads waiting for responses (network/disk), so many threads OK - they don't burden CPU. CPU operations fully utilize cores, so more threads than cores = context switching overhead.

**Common mistakes**: Using IO for CPU work (wastes IO pool), using Default for I/O (thread starvation risk), unnecessary nested withContext, blocking threads with Thread.sleep.

**Best practices**: Use IO for all blocking operations. Use Default for computations. Combine dispatchers in workflows (download on IO → parse on Default → save on IO). Use `limitedParallelism()` for custom pools. In tests, runTest replaces all dispatchers with TestDispatcher.

