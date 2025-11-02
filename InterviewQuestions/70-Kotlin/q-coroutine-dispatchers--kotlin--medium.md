---
id: kotlin-096
title: "Coroutine Dispatchers / Диспетчеры корутин"
aliases: []

# Classification
topic: kotlin
subtopics:
  - concurrency
  - coroutines
  - dispatchers
  - main
  - threading
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive guide to Kotlin Coroutine Dispatchers

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-coroutine-context-explained--kotlin--medium, q-dispatchers-io-vs-default--kotlin--medium, q-kotlin-coroutines-introduction--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [coroutines, default, difficulty/medium, dispatchers, io, kotlin, main, threading, unconfined]
date created: Thursday, October 16th 2025, 4:31:25 pm
date modified: Saturday, November 1st 2025, 5:43:27 pm
---

# Question (EN)
> What are coroutine dispatchers in Kotlin? Explain Main, IO, Default, and Unconfined dispatchers and when to use each.

# Вопрос (RU)
> Что такое диспетчеры корутин в Kotlin? Объясните диспетчеры Main, IO, Default и Unconfined и когда использовать каждый.

---

## Answer (EN)

Coroutine dispatchers determine which thread or thread pool executes a coroutine. Kotlin provides four main dispatchers, each optimized for specific workloads.

### Dispatcher Overview

| Dispatcher | Thread Pool | Use Case | Examples |
|------------|-------------|----------|----------|
| **Dispatchers.Main** | UI thread | UI updates, user interaction | Update TextView, show Dialog |
| **Dispatchers.IO** | Shared pool (64+ threads) | I/O operations, blocking calls | Network, Database, File I/O |
| **Dispatchers.Default** | CPU-bound pool (CPU cores) | CPU-intensive work | Parsing, sorting, calculations |
| **Dispatchers.Unconfined** | No specific thread | Testing, special cases | Unit tests, advanced scenarios |

### Dispatchers.Main

Executes coroutines on the UI thread (Android main thread):

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch(Dispatchers.Main) {
            // Runs on UI thread
            textView.text = "Loading..."

            val data = withContext(Dispatchers.IO) {
                // Switch to IO thread
                fetchData()
            }

            // Back on UI thread automatically
            textView.text = data
        }
    }
}
```

**Characteristics**:
- Single-threaded (UI thread)
- Required for UI updates
- Default for `lifecycleScope` and `viewModelScope`
- Non-blocking: uses event loop

**Use for**:
- Updating UI elements
- Showing dialogs/toasts
- Navigation
- Starting other coroutines

### Dispatchers.IO

Optimized for I/O operations with a large thread pool:

```kotlin
class UserRepository(private val api: ApiService, private val db: UserDao) {
    suspend fun getUser(id: Int): User = withContext(Dispatchers.IO) {
        // Network call
        val user = api.fetchUser(id)

        // Database write
        db.insert(user)

        user
    }

    suspend fun saveToFile(data: String) = withContext(Dispatchers.IO) {
        // File I/O
        File("data.txt").writeText(data)
    }
}
```

**Characteristics**:
- Large thread pool (default 64 threads, configurable)
- Designed for blocking I/O
- Threads can be blocked without affecting performance
- Shares threads efficiently

**Use for**:
- Network requests (Retrofit, Ktor)
- Database operations (Room, SQLite)
- File I/O (reading/writing files)
- Blocking I/O operations

### Dispatchers.Default

Optimized for CPU-intensive work:

```kotlin
class DataProcessor {
    suspend fun processLargeDataset(data: List<Item>): Result = withContext(Dispatchers.Default) {
        // CPU-intensive processing
        data.map { item ->
            complexCalculation(item)
        }.reduce { acc, value ->
            acc + value
        }
    }

    suspend fun sortLargeList(list: List<Int>): List<Int> = withContext(Dispatchers.Default) {
        list.sorted()
    }

    suspend fun parseJson(json: String): Data = withContext(Dispatchers.Default) {
        Json.decodeFromString<Data>(json)
    }
}
```

**Characteristics**:
- Thread pool size = number of CPU cores (min 2)
- Optimized for computational work
- Should not be used for blocking I/O
- Good for parallel processing

**Use for**:
- Heavy computations
- Data parsing (JSON, XML)
- Image/video processing
- Sorting/filtering large collections
- Cryptographic operations

### Dispatchers.Unconfined

Starts in caller's context, resumes in arbitrary thread:

```kotlin
fun main() = runBlocking {
    launch(Dispatchers.Unconfined) {
        println("Unconfined 1: ${Thread.currentThread().name}")
        delay(100)
        println("Unconfined 2: ${Thread.currentThread().name}") // Different thread!
    }

    launch {
        println("Main: ${Thread.currentThread().name}")
        delay(100)
        println("Main: ${Thread.currentThread().name}") // Same thread
    }
}

// Output:
// Unconfined 1: main
// Main: main
// Unconfined 2: kotlinx.coroutines.DefaultExecutor
// Main: main
```

**Characteristics**:
- No thread affinity
- Resumes in whatever thread the suspending function resumed in
- Unpredictable thread behavior
- Very low overhead

**Use for**:
- Testing
- Performance-critical code (advanced)
- When thread doesn't matter
- Generally **not recommended** for production

### Switching Dispatchers with withContext

```kotlin
class UserViewModel : ViewModel() {
    fun loadUser(id: Int) {
        viewModelScope.launch(Dispatchers.Main) {
            // Start on Main thread
            showLoading()

            val user = withContext(Dispatchers.IO) {
                // Switch to IO for network
                api.getUser(id)
            }
            // Automatically back to Main

            val processed = withContext(Dispatchers.Default) {
                // Switch to Default for CPU work
                processUserData(user)
            }
            // Automatically back to Main

            updateUI(processed)
        }
    }
}
```

### Real-World Example: Complete Flow

```kotlin
class MovieRepository(
    private val api: MovieApiService,
    private val database: MovieDatabase,
    private val imageProcessor: ImageProcessor
) {
    suspend fun getMovieDetails(id: Int): Movie = withContext(Dispatchers.IO) {
        // 1. Network call on IO dispatcher
        val movieDto = api.fetchMovie(id)

        // 2. CPU-intensive parsing on Default dispatcher
        val movie = withContext(Dispatchers.Default) {
            parseMovieDto(movieDto)
        }

        // 3. Download and process poster image (back on IO)
        val posterUrl = movie.posterUrl
        val posterBytes = api.downloadPoster(posterUrl)

        // 4. Process image on Default dispatcher
        val processedPoster = withContext(Dispatchers.Default) {
            imageProcessor.optimize(posterBytes)
        }

        // 5. Save to database (back on IO)
        database.movieDao().insert(movie.copy(poster = processedPoster))

        movie
    }
}

class MovieViewModel : ViewModel() {
    private val _movie = MutableStateFlow<UiState<Movie>>(UiState.Loading)
    val movie: StateFlow<UiState<Movie>> = _movie

    fun loadMovie(id: Int) {
        // Launch on Main dispatcher
        viewModelScope.launch(Dispatchers.Main) {
            _movie.value = UiState.Loading

            try {
                // Repository handles dispatcher switching internally
                val movie = repository.getMovieDetails(id)

                // Update UI on Main dispatcher (automatically)
                _movie.value = UiState.Success(movie)
            } catch (e: Exception) {
                _movie.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}
```

### Custom Dispatchers

```kotlin
// Limited parallelism dispatcher
val customDispatcher = Dispatchers.IO.limitedParallelism(5)

suspend fun processItems(items: List<Item>) {
    items.map { item ->
        async(customDispatcher) {
            processItem(item)
        }
    }.awaitAll()
    // Max 5 concurrent operations
}

// Single-threaded dispatcher
val singleThreadDispatcher = newSingleThreadContext("MyThread")

suspend fun sequentialOperations() = withContext(singleThreadDispatcher) {
    // All operations on single thread
    operation1()
    operation2()
    operation3()
}

// Fixed thread pool
val fixedThreadPool = newFixedThreadPoolContext(4, "MyPool")
```

### Dispatcher Performance

```kotlin
// BAD: Using wrong dispatcher
suspend fun loadData() = withContext(Dispatchers.Default) {
    // Blocking I/O on CPU-bound dispatcher
    api.fetchData() // Wastes CPU thread!
}

// GOOD: Using correct dispatcher
suspend fun loadData() = withContext(Dispatchers.IO) {
    api.fetchData()
}

// BAD: Unnecessary switching
suspend fun simpleCalculation() = withContext(Dispatchers.Main) {
    val result = withContext(Dispatchers.Default) {
        2 + 2 // Too simple to justify switch
    }
    result
}

// GOOD: Direct calculation
suspend fun simpleCalculation(): Int {
    return 2 + 2
}
```

### Best Practices

#### DO:
```kotlin
// Use IO for blocking I/O
suspend fun readFile() = withContext(Dispatchers.IO) {
    File("data.txt").readText()
}

// Use Default for CPU work
suspend fun sortData(data: List<Int>) = withContext(Dispatchers.Default) {
    data.sorted()
}

// Use Main for UI updates
lifecycleScope.launch(Dispatchers.Main) {
    textView.text = "Updated"
}

// Let viewModelScope default to Main
viewModelScope.launch {
    // Already on Main
    updateUI()
}

// Switch contexts appropriately
viewModelScope.launch {
    val data = withContext(Dispatchers.IO) {
        fetchData()
    }
    updateUI(data)
}
```

#### DON'T:
```kotlin
// Don't use Default for I/O
withContext(Dispatchers.Default) {
    api.fetchData() // Wrong dispatcher!
}

// Don't use IO for CPU work
withContext(Dispatchers.IO) {
    heavyCalculation() // Wastes I/O threads
}

// Don't update UI off Main thread
withContext(Dispatchers.IO) {
    textView.text = "Error" // Crash!
}

// Don't use Unconfined in production
launch(Dispatchers.Unconfined) {
    // Unpredictable behavior
}
```

---

## Ответ (RU)

Диспетчеры корутин определяют, какой поток или пул потоков выполняет корутину. Kotlin предоставляет четыре основных диспетчера, каждый оптимизирован для конкретных задач.

### Обзор Диспетчеров

| Диспетчер | Пул потоков | Случай использования | Примеры |
|------------|-------------|----------|----------|
| **Dispatchers.Main** | UI поток | Обновления UI, взаимодействие с пользователем | Обновить TextView, показать Dialog |
| **Dispatchers.IO** | Общий пул (64+ потоков) | I/O операции, блокирующие вызовы | Сеть, БД, файловый I/O |
| **Dispatchers.Default** | CPU-bound пул (ядра CPU) | CPU-интенсивная работа | Парсинг, сортировка, вычисления |
| **Dispatchers.Unconfined** | Нет конкретного потока | Тестирование, особые случаи | Unit тесты, продвинутые сценарии |

### Dispatchers.Main

Выполняет корутины на UI потоке (основной поток Android):

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch(Dispatchers.Main) {
            // Выполняется на UI потоке
            textView.text = "Загрузка..."

            val data = withContext(Dispatchers.IO) {
                // Переключение на IO поток
                fetchData()
            }

            // Автоматически обратно на UI поток
            textView.text = data
        }
    }
}
```

**Характеристики**:
- Однопоточный (UI поток)
- Требуется для обновлений UI
- По умолчанию для `lifecycleScope` и `viewModelScope`
- Неблокирующий: использует event loop

**Использовать для**:
- Обновления элементов UI
- Показа диалогов/тостов
- Навигации
- Запуска других корутин

### Dispatchers.IO

Оптимизирован для I/O операций с большим пулом потоков:

```kotlin
class UserRepository(private val api: ApiService, private val db: UserDao) {
    suspend fun getUser(id: Int): User = withContext(Dispatchers.IO) {
        // Сетевой вызов
        val user = api.fetchUser(id)

        // Запись в БД
        db.insert(user)

        user
    }

    suspend fun saveToFile(data: String) = withContext(Dispatchers.IO) {
        // Файловый I/O
        File("data.txt").writeText(data)
    }
}
```

**Характеристики**:
- Большой пул потоков (по умолчанию 64 потока, настраиваемый)
- Разработан для блокирующего I/O
- Потоки могут быть заблокированы без влияния на производительность
- Эффективно разделяет потоки

**Использовать для**:
- Сетевых запросов (Retrofit, Ktor)
- Операций с БД (Room, SQLite)
- Файлового I/O (чтение/запись файлов)
- Блокирующих I/O операций

### Dispatchers.Default

Оптимизирован для CPU-интенсивной работы:

```kotlin
class DataProcessor {
    suspend fun processLargeDataset(data: List<Item>): Result = withContext(Dispatchers.Default) {
        // CPU-интенсивная обработка
        data.map { item ->
            complexCalculation(item)
        }.reduce { acc, value ->
            acc + value
        }
    }

    suspend fun sortLargeList(list: List<Int>): List<Int> = withContext(Dispatchers.Default) {
        list.sorted()
    }

    suspend fun parseJson(json: String): Data = withContext(Dispatchers.Default) {
        Json.decodeFromString<Data>(json)
    }
}
```

**Характеристики**:
- Размер пула потоков = количество ядер CPU (минимум 2)
- Оптимизирован для вычислительной работы
- Не должен использоваться для блокирующего I/O
- Хорош для параллельной обработки

**Использовать для**:
- Тяжёлых вычислений
- Парсинга данных (JSON, XML)
- Обработки изображений/видео
- Сортировки/фильтрации больших коллекций
- Криптографических операций

### Dispatchers.Unconfined

Начинает в контексте вызывающей стороны, возобновляется в произвольном потоке:

```kotlin
fun main() = runBlocking {
    launch(Dispatchers.Unconfined) {
        println("Unconfined 1: ${Thread.currentThread().name}")
        delay(100)
        println("Unconfined 2: ${Thread.currentThread().name}") // Другой поток!
    }

    launch {
        println("Main: ${Thread.currentThread().name}")
        delay(100)
        println("Main: ${Thread.currentThread().name}") // Тот же поток
    }
}

// Вывод:
// Unconfined 1: main
// Main: main
// Unconfined 2: kotlinx.coroutines.DefaultExecutor
// Main: main
```

**Характеристики**:
- Нет привязки к потоку
- Возобновляется в том потоке, в котором возобновилась suspend-функция
- Непредсказуемое поведение потока
- Очень низкие накладные расходы

**Использовать для**:
- Тестирования
- Производительно-критичного кода (продвинутый)
- Когда поток не имеет значения
- Обычно **не рекомендуется** для production

### Переключение Диспетчеров С withContext

```kotlin
class UserViewModel : ViewModel() {
    fun loadUser(id: Int) {
        viewModelScope.launch(Dispatchers.Main) {
            // Начать на Main потоке
            showLoading()

            val user = withContext(Dispatchers.IO) {
                // Переключиться на IO для сети
                api.getUser(id)
            }
            // Автоматически обратно на Main

            val processed = withContext(Dispatchers.Default) {
                // Переключиться на Default для CPU работы
                processUserData(user)
            }
            // Автоматически обратно на Main

            updateUI(processed)
        }
    }
}
```

### Реальный Пример: Полный Поток

```kotlin
class MovieRepository(
    private val api: MovieApiService,
    private val database: MovieDatabase,
    private val imageProcessor: ImageProcessor
) {
    suspend fun getMovieDetails(id: Int): Movie = withContext(Dispatchers.IO) {
        // 1. Сетевой вызов на IO диспетчере
        val movieDto = api.fetchMovie(id)

        // 2. CPU-интенсивный парсинг на Default диспетчере
        val movie = withContext(Dispatchers.Default) {
            parseMovieDto(movieDto)
        }

        // 3. Скачать и обработать постер (обратно на IO)
        val posterUrl = movie.posterUrl
        val posterBytes = api.downloadPoster(posterUrl)

        // 4. Обработать изображение на Default диспетчере
        val processedPoster = withContext(Dispatchers.Default) {
            imageProcessor.optimize(posterBytes)
        }

        // 5. Сохранить в базу данных (обратно на IO)
        database.movieDao().insert(movie.copy(poster = processedPoster))

        movie
    }
}

class MovieViewModel : ViewModel() {
    private val _movie = MutableStateFlow<UiState<Movie>>(UiState.Loading)
    val movie: StateFlow<UiState<Movie>> = _movie

    fun loadMovie(id: Int) {
        // Запустить на Main диспетчере
        viewModelScope.launch(Dispatchers.Main) {
            _movie.value = UiState.Loading

            try {
                // Repository обрабатывает переключение диспетчеров внутренне
                val movie = repository.getMovieDetails(id)

                // Обновить UI на Main диспетчере (автоматически)
                _movie.value = UiState.Success(movie)
            } catch (e: Exception) {
                _movie.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}
```

### Пользовательские Диспетчеры

```kotlin
// Диспетчер с ограниченным параллелизмом
val customDispatcher = Dispatchers.IO.limitedParallelism(5)

suspend fun processItems(items: List<Item>) {
    items.map { item ->
        async(customDispatcher) {
            processItem(item)
        }
    }.awaitAll()
    // Максимум 5 одновременных операций
}

// Однопоточный диспетчер
val singleThreadDispatcher = newSingleThreadContext("MyThread")

suspend fun sequentialOperations() = withContext(singleThreadDispatcher) {
    // Все операции на одном потоке
    operation1()
    operation2()
    operation3()
}

// Пул потоков фиксированного размера
val fixedThreadPool = newFixedThreadPoolContext(4, "MyPool")
```

### Производительность Диспетчеров

```kotlin
// ПЛОХО: Использование неправильного диспетчера
suspend fun loadData() = withContext(Dispatchers.Default) {
    // Блокирующий I/O на CPU-bound диспетчере
    api.fetchData() // Тратит впустую CPU поток!
}

// ХОРОШО: Использование правильного диспетчера
suspend fun loadData() = withContext(Dispatchers.IO) {
    api.fetchData()
}

// ПЛОХО: Ненужное переключение
suspend fun simpleCalculation() = withContext(Dispatchers.Main) {
    val result = withContext(Dispatchers.Default) {
        2 + 2 // Слишком просто чтобы оправдать переключение
    }
    result
}

// ХОРОШО: Прямое вычисление
suspend fun simpleCalculation(): Int {
    return 2 + 2
}
```

### Лучшие Практики

#### ДЕЛАТЬ:
```kotlin
// Использовать IO для блокирующего I/O
suspend fun readFile() = withContext(Dispatchers.IO) {
    File("data.txt").readText()
}

// Использовать Default для CPU работы
suspend fun sortData(data: List<Int>) = withContext(Dispatchers.Default) {
    data.sorted()
}

// Использовать Main для обновлений UI
lifecycleScope.launch(Dispatchers.Main) {
    textView.text = "Обновлено"
}

// Позволить viewModelScope по умолчанию использовать Main
viewModelScope.launch {
    // Уже на Main
    updateUI()
}

// Переключать контексты соответственно
viewModelScope.launch {
    val data = withContext(Dispatchers.IO) {
        fetchData()
    }
    updateUI(data)
}
```

#### НЕ ДЕЛАТЬ:
```kotlin
// Не использовать Default для I/O
withContext(Dispatchers.Default) {
    api.fetchData() // Неправильный диспетчер!
}

// Не использовать IO для CPU работы
withContext(Dispatchers.IO) {
    heavyCalculation() // Тратит впустую I/O потоки
}

// Не обновлять UI не на Main потоке
withContext(Dispatchers.IO) {
    textView.text = "Ошибка" // Crash!
}

// Не использовать Unconfined в production
launch(Dispatchers.Unconfined) {
    // Непредсказуемое поведение
}
```

### Дерево Решений

```
Какую операцию нужно выполнить?

 Обновление UI?
   → Dispatchers.Main

 Сетевой запрос / База данных / Файловый I/O?
   → Dispatchers.IO

 Тяжёлые вычисления / Парсинг / Обработка данных?
   → Dispatchers.Default

 Тестирование / Специальный случай?
   → Dispatchers.Unconfined (с осторожностью)

 Нужен специфический пул потоков?
   → Пользовательский диспетчер
```

---

## References

- [Kotlin Coroutine Dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
- [Dispatchers Guide](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-dispatchers/)
- [Android Coroutines Best Practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)

## Related Questions

### Related (Medium)
- [[q-coroutine-context-explained--kotlin--medium]] - Coroutines
- [[q-custom-dispatchers-limited-parallelism--kotlin--hard]] - Coroutines
- [[q-dispatchers-unconfined--kotlin--medium]] - Coroutines
- [[q-deferred-async-patterns--kotlin--medium]] - Coroutines

### Advanced (Harder)
- [[q-coroutine-context-detailed--kotlin--hard]] - Coroutines
- [[q-actor-pattern--kotlin--hard]] - Coroutines
- [[q-fan-in-fan-out--kotlin--hard]] - Coroutines

### Hub
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Comprehensive coroutines introduction

## MOC Links

- [[moc-kotlin]]
