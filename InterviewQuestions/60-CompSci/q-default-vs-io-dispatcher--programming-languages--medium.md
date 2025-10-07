---
tags:
  - programming-languages
difficulty: medium
status: draft
---

# Default Dispatcher vs IO Dispatcher

## Answer

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

// ✅ Good use of Dispatchers.Default
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

// ✅ Good use of Dispatchers.IO
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
// ❌ WRONG: CPU-intensive on IO dispatcher
suspend fun badExample1() = withContext(Dispatchers.IO) {
    // This blocks an IO thread for CPU work
    (1..1_000_000).sum()  // Should use Dispatchers.Default
}

// ❌ WRONG: I/O operation on Default dispatcher
suspend fun badExample2() = withContext(Dispatchers.Default) {
    // This blocks a CPU thread for I/O
    File("data.txt").readText()  // Should use Dispatchers.IO
}

// ✅ CORRECT: Use appropriate dispatchers
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

// ❌ Default dispatcher should avoid blocking
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
    // ✅ DO: Use IO for network
    suspend fun fetchFromNetwork() = withContext(Dispatchers.IO) {
        api.getData()
    }

    // ✅ DO: Use Default for computation
    suspend fun calculateResult(data: List<Int>) = withContext(Dispatchers.Default) {
        data.map { it * it }.sum()
    }

    // ✅ DO: Switch dispatchers as needed
    suspend fun pipeline() {
        val data = withContext(Dispatchers.IO) { fetchData() }
        val result = withContext(Dispatchers.Default) { process(data) }
        withContext(Dispatchers.IO) { save(result) }
    }

    // ❌ DON'T: Use Default for blocking I/O
    suspend fun badPractice1() = withContext(Dispatchers.Default) {
        File("data.txt").readText()  // BAD
    }

    // ❌ DON'T: Use IO for CPU-heavy work unnecessarily
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
## Вопрос (RU)

В чем различие Default диспатчер и IO диспатчер

## Ответ

Dispatchers.Default — для тяжёлых вычислений (CPU-операции). Dispatchers.IO — для операций ввода-вывода (сеть, файлы, БД).
