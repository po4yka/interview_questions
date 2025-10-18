---
id: 20251016-175035
title: "Default Vs Io Dispatcher"
topic: programming-languages
difficulty: medium
status: draft
created: 2025-10-13
tags:
  - programming-languages
moc: moc-programming-languages
related: [q-primitive-vs-reference-types--programming-languages--easy, q-launch-vs-async-await--programming-languages--medium, q-iterator-pattern--design-patterns--medium]
subtopics: ["computer-science", "fundamentals"]
---
# Default Dispatcher vs IO Dispatcher

# Question (EN)
> What is the difference between Default dispatcher and IO dispatcher?

# Вопрос (RU)
> В чем различие Default диспатчер и IO диспатчер?

---

## Answer (EN)

**Dispatchers.Default** is for heavy computations (CPU-intensive operations).
**Dispatchers.IO** is for I/O operations (network requests, file operations, database queries).

### Key Differences

| Feature | Dispatchers.Default | Dispatchers.IO |
|---------|---------------------|----------------|
| **Purpose** | CPU-intensive work | I/O-bound operations |
| **Thread Pool Size** | Number of CPU cores (min 2) | Up to 64 threads (configurable) |
| **Use Cases** | Parsing, sorting, calculations | Network, files, database |
| **Blocking Allowed** | Should avoid blocking | Designed for blocking operations |
| **Thread Type** | Shared thread pool | Shared thread pool (larger) |

### Dispatchers.Default - CPU Intensive

```kotlin
import kotlinx.coroutines.*

// - Good use of Dispatchers.Default
suspend fun parseJsonData(json: String): List<User> = withContext(Dispatchers.Default) {
    // CPU-intensive parsing
    val users = mutableListOf<User>()
    // Complex parsing logic...
    users
}

suspend fun sortLargeList(items: List<Int>): List<Int> = withContext(Dispatchers.Default) {
    // CPU-intensive sorting
    items.sorted()
}

suspend fun calculateStatistics(data: List<Double>): Statistics = withContext(Dispatchers.Default) {
    // Heavy mathematical computations
    Statistics(
        mean = data.average(),
        median = data.sorted()[data.size / 2],
        stdDev = calculateStdDev(data)
    )
}

suspend fun compressImage(image: Bitmap): ByteArray = withContext(Dispatchers.Default) {
    // CPU-intensive image compression
    val outputStream = ByteArrayOutputStream()
    image.compress(Bitmap.CompressFormat.JPEG, 85, outputStream)
    outputStream.toByteArray()
}

// Complex algorithm
suspend fun findPrimes(n: Int): List<Int> = withContext(Dispatchers.Default) {
    (2..n).filter { candidate ->
        (2 until candidate).none { candidate % it == 0 }
    }
}
```

### Dispatchers.IO - I/O Bound Operations

```kotlin
import kotlinx.coroutines.*
import java.io.File

// - Good use of Dispatchers.IO
suspend fun fetchUserFromNetwork(userId: Int): User = withContext(Dispatchers.IO) {
    // Network request (blocking I/O)
    api.getUser(userId)
}

suspend fun saveToDatabase(user: User) = withContext(Dispatchers.IO) {
    // Database write (blocking I/O)
    database.userDao().insert(user)
}

suspend fun readFileContents(path: String): String = withContext(Dispatchers.IO) {
    // File reading (blocking I/O)
    File(path).readText()
}

suspend fun downloadImage(url: String): Bitmap = withContext(Dispatchers.IO) {
    // Network download (blocking I/O)
    val connection = URL(url).openConnection()
    BitmapFactory.decodeStream(connection.getInputStream())
}

suspend fun writeLogToFile(message: String) = withContext(Dispatchers.IO) {
    // File writing (blocking I/O)
    File("app.log").appendText("$message\n")
}
```

### Thread Pool Sizes

```kotlin
fun main() = runBlocking {
    println("CPU cores: ${Runtime.getRuntime().availableProcessors()}")

    // Default pool size ≈ number of CPU cores
    println("Default threads: ${Dispatchers.Default.toString()}")

    // IO pool size: up to 64 threads
    println("IO threads: ${Dispatchers.IO.toString()}")
}

// Example output on 8-core machine:
// CPU cores: 8
// Default threads: Dispatchers.Default[size=8]
// IO threads: Dispatchers.IO[size=64]
```

### When to Use Each

```kotlin
// - WRONG: CPU-intensive on IO dispatcher
suspend fun badExample1() = withContext(Dispatchers.IO) {
    // This blocks an IO thread for CPU work
    (1..1_000_000).sum()  // Should use Dispatchers.Default
}

// - WRONG: I/O operation on Default dispatcher
suspend fun badExample2() = withContext(Dispatchers.Default) {
    // This blocks a CPU thread for I/O
    File("data.txt").readText()  // Should use Dispatchers.IO
}

// - CORRECT: Use appropriate dispatchers
suspend fun goodExample() {
    // I/O operation on IO dispatcher
    val fileContent = withContext(Dispatchers.IO) {
        File("data.txt").readText()
    }

    // CPU-intensive on Default dispatcher
    val parsed = withContext(Dispatchers.Default) {
        parseComplexData(fileContent)
    }

    // Save result back with IO
    withContext(Dispatchers.IO) {
        database.save(parsed)
    }
}
```

### Real-World Example

```kotlin
class DataProcessor {
    // Fetch data from network (I/O)
    suspend fun fetchData(url: String): String = withContext(Dispatchers.IO) {
        URL(url).readText()
    }

    // Process data (CPU-intensive)
    suspend fun processData(rawData: String): ProcessedData = withContext(Dispatchers.Default) {
        // Complex parsing and transformation
        val parsed = JsonParser.parse(rawData)
        val transformed = parsed.map { transformItem(it) }
        ProcessedData(transformed)
    }

    // Save to database (I/O)
    suspend fun saveData(data: ProcessedData) = withContext(Dispatchers.IO) {
        database.insert(data)
    }

    // Complete pipeline
    suspend fun processAndSave(url: String) {
        val rawData = fetchData(url)        // Dispatchers.IO
        val processed = processData(rawData) // Dispatchers.Default
        saveData(processed)                  // Dispatchers.IO
    }
}
```

### Parallel Execution

```kotlin
suspend fun parallelIOOperations() = coroutineScope {
    // Can run many IO operations in parallel (up to 64 threads)
    val results = (1..100).map { id ->
        async(Dispatchers.IO) {
            fetchUser(id)  // Each on separate IO thread
        }
    }.awaitAll()

    println("Fetched ${results.size} users")
}

suspend fun parallelComputations() = coroutineScope {
    // Limited by CPU cores (typically 4-16 threads)
    val results = (1..100).map { data ->
        async(Dispatchers.Default) {
            processData(data)  // Shared among CPU cores
        }
    }.awaitAll()

    println("Processed ${results.size} items")
}
```

### Dispatcher Configuration

```kotlin
// Custom IO dispatcher with more threads
val customIODispatcher = Dispatchers.IO.limitedParallelism(128)

suspend fun useCustomDispatcher() = withContext(customIODispatcher) {
    // Use expanded thread pool
    fetchData()
}

// Custom Default-like dispatcher
val customComputeDispatcher = Dispatchers.Default.limitedParallelism(4)

suspend fun useCustomCompute() = withContext(customComputeDispatcher) {
    // Limited to 4 threads regardless of CPU count
    heavyComputation()
}
```

### Blocking Operations

```kotlin
// IO dispatcher handles blocking calls well
suspend fun multipleBlockingCalls() = coroutineScope {
    // All can run concurrently on IO threads
    val user = async(Dispatchers.IO) {
        Thread.sleep(1000)  // Blocking call OK here
        fetchUser()
    }
    val posts = async(Dispatchers.IO) {
        Thread.sleep(1000)  // Blocking call OK here
        fetchPosts()
    }
    val settings = async(Dispatchers.IO) {
        Thread.sleep(1000)  // Blocking call OK here
        fetchSettings()
    }

    CombinedData(user.await(), posts.await(), settings.await())
}

// - Default dispatcher should avoid blocking
suspend fun badBlocking() = withContext(Dispatchers.Default) {
    Thread.sleep(1000)  // BAD: Blocks precious CPU thread
    // Use delay() or Dispatchers.IO instead
}
```

### Mixed Workloads

```kotlin
suspend fun mixedWorkload() {
    // Step 1: Fetch data (I/O)
    val rawData = withContext(Dispatchers.IO) {
        api.fetchData()
    }

    // Step 2: Transform data (CPU)
    val transformed = withContext(Dispatchers.Default) {
        rawData.map { item ->
            complexTransform(item)
        }
    }

    // Step 3: Save to DB (I/O)
    withContext(Dispatchers.IO) {
        database.save(transformed)
    }

    // Step 4: Generate report (CPU)
    val report = withContext(Dispatchers.Default) {
        generateReport(transformed)
    }

    // Step 5: Upload report (I/O)
    withContext(Dispatchers.IO) {
        api.uploadReport(report)
    }
}
```

### Performance Comparison

```kotlin
suspend fun compareDispatchers() {
    // CPU-intensive task
    val cpuTask = {
        (1..10_000_000).sum()
    }

    // Correct: Default for CPU
    val time1 = measureTimeMillis {
        withContext(Dispatchers.Default) {
            cpuTask()
        }
    }
    println("CPU on Default: ${time1}ms")  // Fast

    // Incorrect: IO for CPU
    val time2 = measureTimeMillis {
        withContext(Dispatchers.IO) {
            cpuTask()
        }
    }
    println("CPU on IO: ${time2}ms")  // Similar, but wastes IO thread

    // I/O task
    val ioTask = {
        File("test.txt").readText()
    }

    // Correct: IO for I/O
    val time3 = measureTimeMillis {
        withContext(Dispatchers.IO) {
            ioTask()
        }
    }
    println("IO on IO: ${time3}ms")  // Appropriate

    // Incorrect: Default for I/O
    val time4 = measureTimeMillis {
        withContext(Dispatchers.Default) {
            ioTask()
        }
    }
    println("IO on Default: ${time4}ms")  // Works but blocks CPU thread
}
```

### Best Practices

```kotlin
class BestPractices {
    // - DO: Use IO for network
    suspend fun fetchFromNetwork() = withContext(Dispatchers.IO) {
        api.getData()
    }

    // - DO: Use Default for computation
    suspend fun calculateResult(data: List<Int>) = withContext(Dispatchers.Default) {
        data.map { it * it }.sum()
    }

    // - DO: Switch dispatchers as needed
    suspend fun pipeline() {
        val data = withContext(Dispatchers.IO) { fetchData() }
        val result = withContext(Dispatchers.Default) { process(data) }
        withContext(Dispatchers.IO) { save(result) }
    }

    // - DON'T: Use Default for blocking I/O
    suspend fun badPractice1() = withContext(Dispatchers.Default) {
        File("data.txt").readText()  // BAD
    }

    // - DON'T: Use IO for CPU-heavy work unnecessarily
    suspend fun badPractice2() = withContext(Dispatchers.IO) {
        (1..1_000_000).map { it * it }  // BAD
    }
}
```

### Summary

**Use Dispatchers.Default for:**
- Parsing JSON/XML
- Sorting/filtering large collections
- Image/video processing
- Compression/decompression
- Mathematical calculations
- Algorithm execution

**Use Dispatchers.IO for:**
- Network requests (HTTP, WebSocket)
- Database queries (Room, SQL)
- File operations (read/write)
- SharedPreferences/DataStore
- Blocking APIs

---

## Ответ (RU)

**Dispatchers.Default** предназначен для тяжелых вычислений (CPU-интенсивные операции).
**Dispatchers.IO** предназначен для операций ввода-вывода (сетевые запросы, операции с файлами, запросы к БД).

### Ключевые различия

| Характеристика | Dispatchers.Default | Dispatchers.IO |
|----------------|---------------------|----------------|
| **Назначение** | CPU-интенсивная работа | I/O-операции |
| **Размер пула потоков** | Количество ядер CPU (минимум 2) | До 64 потоков (настраиваемо) |
| **Примеры использования** | Парсинг, сортировка, вычисления | Сеть, файлы, база данных |
| **Блокировки допустимы** | Следует избегать блокировок | Разработан для блокирующих операций |
| **Тип потоков** | Общий пул потоков | Общий пул потоков (больший) |

### Dispatchers.Default - CPU-интенсивные операции

```kotlin
import kotlinx.coroutines.*

// Хорошее использование Dispatchers.Default
suspend fun parseJsonData(json: String): List<User> = withContext(Dispatchers.Default) {
    // CPU-интенсивный парсинг
    val users = mutableListOf<User>()
    // Сложная логика парсинга...
    users
}

suspend fun sortLargeList(items: List<Int>): List<Int> = withContext(Dispatchers.Default) {
    // CPU-интенсивная сортировка
    items.sorted()
}

suspend fun calculateStatistics(data: List<Double>): Statistics = withContext(Dispatchers.Default) {
    // Тяжелые математические вычисления
    Statistics(
        mean = data.average(),
        median = data.sorted()[data.size / 2],
        stdDev = calculateStdDev(data)
    )
}

suspend fun compressImage(image: Bitmap): ByteArray = withContext(Dispatchers.Default) {
    // CPU-интенсивное сжатие изображения
    val outputStream = ByteArrayOutputStream()
    image.compress(Bitmap.CompressFormat.JPEG, 85, outputStream)
    outputStream.toByteArray()
}

// Сложный алгоритм
suspend fun findPrimes(n: Int): List<Int> = withContext(Dispatchers.Default) {
    (2..n).filter { candidate ->
        (2 until candidate).none { candidate % it == 0 }
    }
}
```

### Dispatchers.IO - I/O операции

```kotlin
import kotlinx.coroutines.*
import java.io.File

// Хорошее использование Dispatchers.IO
suspend fun fetchUserFromNetwork(userId: Int): User = withContext(Dispatchers.IO) {
    // Сетевой запрос (блокирующий I/O)
    api.getUser(userId)
}

suspend fun saveToDatabase(user: User) = withContext(Dispatchers.IO) {
    // Запись в БД (блокирующий I/O)
    database.userDao().insert(user)
}

suspend fun readFileContents(path: String): String = withContext(Dispatchers.IO) {
    // Чтение файла (блокирующий I/O)
    File(path).readText()
}

suspend fun downloadImage(url: String): Bitmap = withContext(Dispatchers.IO) {
    // Загрузка из сети (блокирующий I/O)
    val connection = URL(url).openConnection()
    BitmapFactory.decodeStream(connection.getInputStream())
}

suspend fun writeLogToFile(message: String) = withContext(Dispatchers.IO) {
    // Запись в файл (блокирующий I/O)
    File("app.log").appendText("$message\n")
}
```

### Размеры пулов потоков

```kotlin
fun main() = runBlocking {
    println("Ядер CPU: ${Runtime.getRuntime().availableProcessors()}")

    // Размер пула Default ≈ количество ядер CPU
    println("Потоков Default: ${Dispatchers.Default.toString()}")

    // Размер пула IO: до 64 потоков
    println("Потоков IO: ${Dispatchers.IO.toString()}")
}

// Пример вывода на 8-ядерной машине:
// Ядер CPU: 8
// Потоков Default: Dispatchers.Default[size=8]
// Потоков IO: Dispatchers.IO[size=64]
```

### Когда использовать каждый

```kotlin
// НЕПРАВИЛЬНО: CPU-интенсивная работа на IO dispatcher
suspend fun badExample1() = withContext(Dispatchers.IO) {
    // Блокирует поток IO для CPU работы
    (1..1_000_000).sum()  // Следует использовать Dispatchers.Default
}

// НЕПРАВИЛЬНО: I/O операция на Default dispatcher
suspend fun badExample2() = withContext(Dispatchers.Default) {
    // Блокирует поток CPU для I/O
    File("data.txt").readText()  // Следует использовать Dispatchers.IO
}

// ПРАВИЛЬНО: Используйте подходящие dispatchers
suspend fun goodExample() {
    // I/O операция на IO dispatcher
    val fileContent = withContext(Dispatchers.IO) {
        File("data.txt").readText()
    }

    // CPU-интенсивная работа на Default dispatcher
    val parsed = withContext(Dispatchers.Default) {
        parseComplexData(fileContent)
    }

    // Сохранение результата с IO
    withContext(Dispatchers.IO) {
        database.save(parsed)
    }
}
```

### Реальный пример

```kotlin
class DataProcessor {
    // Получить данные из сети (I/O)
    suspend fun fetchData(url: String): String = withContext(Dispatchers.IO) {
        URL(url).readText()
    }

    // Обработать данные (CPU-интенсивно)
    suspend fun processData(rawData: String): ProcessedData = withContext(Dispatchers.Default) {
        // Сложный парсинг и трансформация
        val parsed = JsonParser.parse(rawData)
        val transformed = parsed.map { transformItem(it) }
        ProcessedData(transformed)
    }

    // Сохранить в БД (I/O)
    suspend fun saveData(data: ProcessedData) = withContext(Dispatchers.IO) {
        database.insert(data)
    }

    // Полный пайплайн
    suspend fun processAndSave(url: String) {
        val rawData = fetchData(url)        // Dispatchers.IO
        val processed = processData(rawData) // Dispatchers.Default
        saveData(processed)                  // Dispatchers.IO
    }
}
```

### Параллельное выполнение

```kotlin
suspend fun parallelIOOperations() = coroutineScope {
    // Можно выполнять много I/O операций параллельно (до 64 потоков)
    val results = (1..100).map { id ->
        async(Dispatchers.IO) {
            fetchUser(id)  // Каждый в отдельном IO потоке
        }
    }.awaitAll()

    println("Получено ${results.size} пользователей")
}

suspend fun parallelComputations() = coroutineScope {
    // Ограничено ядрами CPU (обычно 4-16 потоков)
    val results = (1..100).map { data ->
        async(Dispatchers.Default) {
            processData(data)  // Распределяется между ядрами CPU
        }
    }.awaitAll()

    println("Обработано ${results.size} элементов")
}
```

### Конфигурация Dispatcher

```kotlin
// Кастомный IO dispatcher с большим количеством потоков
val customIODispatcher = Dispatchers.IO.limitedParallelism(128)

suspend fun useCustomDispatcher() = withContext(customIODispatcher) {
    // Использует расширенный пул потоков
    fetchData()
}

// Кастомный Default-подобный dispatcher
val customComputeDispatcher = Dispatchers.Default.limitedParallelism(4)

suspend fun useCustomCompute() = withContext(customComputeDispatcher) {
    // Ограничен 4 потоками независимо от количества CPU
    heavyComputation()
}
```

### Блокирующие операции

```kotlin
// IO dispatcher хорошо справляется с блокирующими вызовами
suspend fun multipleBlockingCalls() = coroutineScope {
    // Все могут выполняться параллельно на IO потоках
    val user = async(Dispatchers.IO) {
        Thread.sleep(1000)  // Блокирующий вызов OK здесь
        fetchUser()
    }
    val posts = async(Dispatchers.IO) {
        Thread.sleep(1000)  // Блокирующий вызов OK здесь
        fetchPosts()
    }
    val settings = async(Dispatchers.IO) {
        Thread.sleep(1000)  // Блокирующий вызов OK здесь
        fetchSettings()
    }

    CombinedData(user.await(), posts.await(), settings.await())
}

// Default dispatcher должен избегать блокировок
suspend fun badBlocking() = withContext(Dispatchers.Default) {
    Thread.sleep(1000)  // ПЛОХО: Блокирует ценный CPU поток
    // Используйте delay() или Dispatchers.IO вместо этого
}
```

### Смешанные нагрузки

```kotlin
suspend fun mixedWorkload() {
    // Шаг 1: Получить данные (I/O)
    val rawData = withContext(Dispatchers.IO) {
        api.fetchData()
    }

    // Шаг 2: Трансформировать данные (CPU)
    val transformed = withContext(Dispatchers.Default) {
        rawData.map { item ->
            complexTransform(item)
        }
    }

    // Шаг 3: Сохранить в БД (I/O)
    withContext(Dispatchers.IO) {
        database.save(transformed)
    }

    // Шаг 4: Сгенерировать отчет (CPU)
    val report = withContext(Dispatchers.Default) {
        generateReport(transformed)
    }

    // Шаг 5: Загрузить отчет (I/O)
    withContext(Dispatchers.IO) {
        api.uploadReport(report)
    }
}
```

### Лучшие практики

```kotlin
class BestPractices {
    // ПРАВИЛЬНО: Используйте IO для сети
    suspend fun fetchFromNetwork() = withContext(Dispatchers.IO) {
        api.getData()
    }

    // ПРАВИЛЬНО: Используйте Default для вычислений
    suspend fun calculateResult(data: List<Int>) = withContext(Dispatchers.Default) {
        data.map { it * it }.sum()
    }

    // ПРАВИЛЬНО: Переключайте dispatchers по необходимости
    suspend fun pipeline() {
        val data = withContext(Dispatchers.IO) { fetchData() }
        val result = withContext(Dispatchers.Default) { process(data) }
        withContext(Dispatchers.IO) { save(result) }
    }

    // НЕ ДЕЛАЙТЕ: Default для блокирующего I/O
    suspend fun badPractice1() = withContext(Dispatchers.Default) {
        File("data.txt").readText()  // ПЛОХО
    }

    // НЕ ДЕЛАЙТЕ: IO для CPU-тяжелой работы без необходимости
    suspend fun badPractice2() = withContext(Dispatchers.IO) {
        (1..1_000_000).map { it * it }  // ПЛОХО
    }
}
```

### Резюме

**Используйте Dispatchers.Default для:**
- Парсинга JSON/XML
- Сортировки/фильтрации больших коллекций
- Обработки изображений/видео
- Сжатия/распаковки
- Математических вычислений
- Выполнения алгоритмов

**Используйте Dispatchers.IO для:**
- Сетевых запросов (HTTP, WebSocket)
- Запросов к БД (Room, SQL)
- Операций с файлами (чтение/запись)
- SharedPreferences/DataStore
- Блокирующих API

---

## Related Questions

### Prerequisites (Easier)
- [[q-xml-acronym--programming-languages--easy]] - Computer Science
- [[q-data-structures-overview--algorithms--easy]] - Data Structures

### Related (Medium)
- [[q-clean-code-principles--software-engineering--medium]] - Computer Science
- [[q-oop-principles-deep-dive--computer-science--medium]] - Computer Science

### Advanced (Harder)
- [[q-os-fundamentals-concepts--computer-science--hard]] - Computer Science
