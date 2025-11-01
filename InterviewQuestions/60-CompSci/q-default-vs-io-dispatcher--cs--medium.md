---
id: 20251016-175035
title: "Default vs IO Dispatcher / Разница между Default и IO Dispatcher"
aliases: ["Default vs IO Dispatcher", "Разница между Default и IO Dispatcher"]
topic: cs
subtopics: [coroutines, dispatchers, kotlin, programming-languages]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [q-concurrency-fundamentals--computer-science--hard, q-coroutine-dispatchers--programming-languages--medium, q-coroutinescope-vs-supervisorscope--programming-languages--medium]
created: 2025-10-13
updated: 2025-01-25
tags: [coroutines, default, difficulty/medium, dispatchers, io, kotlin, programming-languages]
sources: [https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html]
date created: Saturday, October 4th 2025, 10:45:30 am
date modified: Sunday, October 26th 2025, 11:53:02 am
---

# Вопрос (RU)
> В чем разница между Default и IO dispatcher? Когда использовать каждый из них?

# Question (EN)
> What is the difference between Default dispatcher and IO dispatcher? When to use each?

---

## Ответ (RU)

**Теория Dispatchers:**
Dispatchers определяют, на каком потоке выполняется корутина. `Dispatchers.Default` - CPU-intensive задачи (computation-heavy), shared thread pool = CPU cores. `Dispatchers.IO` - blocking I/O операции (network, file, database), shared thread pool до 64 threads. Ключевое отличие: Default для heavy computation, IO для blocking I/O.

**Различия:**

| Характеристика | Dispatchers.Default | Dispatchers.IO |
|----------------|---------------------|----------------|
| **Цель** | CPU-intensive work | I/O-bound operations |
| **Thread Pool Size** | CPU cores (min 2) | До 64 threads |
| **Blocking** | Не допускается | Допускается |
| **Use Cases** | Parsing, sorting, calculations | Network, files, database |
| **Thread Type** | Shared computational pool | Shared I/O pool |

**Dispatchers.Default - CPU-Интенсивные операции:**

*Теория:* Default используется для CPU-intensive задач, которые максимизируют CPU usage. Thread pool размером = количество CPU cores (минимум 2). Threads не должны блокироваться. Используется для: computation-heavy operations, JSON/XML parsing, image processing, математические вычисления.

```kotlin
// ✅ Dispatchers.Default для CPU-intensive задач
suspend fun parseJsonData(json: String): List<User> = withContext(Dispatchers.Default) {
    // CPU-intensive parsing
    Json.decodeFromString<List<User>>(json)
}

suspend fun sortLargeList(items: List<Int>): List<Int> = withContext(Dispatchers.Default) {
    items.sorted()  // CPU-intensive sorting
}

suspend fun calculateStatistics(data: List<Double>): Statistics = withContext(Dispatchers.Default) {
    Statistics(
        mean = data.average(),
        median = data.sorted()[data.size / 2]
    )
}

// ✅ Image processing
suspend fun compressImage(image: Bitmap): ByteArray = withContext(Dispatchers.Default) {
    val outputStream = ByteArrayOutputStream()
    image.compress(Bitmap.CompressFormat.JPEG, 85, outputStream)
    outputStream.toByteArray()
}
```

**Dispatchers.IO - I/O Операции:**

*Теория:* IO используется для blocking I/O операций, где threads могут блокироваться (waiting for I/O). Thread pool больше (до 64), так как threads могут idle. Используется для: network requests, database queries, file operations, blocking API calls.

```kotlin
// ✅ Dispatchers.IO для I/O операций
suspend fun fetchUserFromNetwork(userId: Int): User = withContext(Dispatchers.IO) {
    api.getUser(userId)  // Network request - блокирует thread
}

suspend fun saveToDatabase(user: User) = withContext(Dispatchers.IO) {
    database.userDao().insert(user)  // Database write - блокирует thread
}

suspend fun readFileContents(path: String): String = withContext(Dispatchers.IO) {
    File(path).readText()  // File I/O - блокирует thread
}

// ✅ Room database
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getAllUsers(): List<User>  // Используется в Dispatchers.IO контексте
}
```

**Правильный выбор dispatcher:**

*Теория:* Критерий выбора - природа операции. CPU-intensive (вычисления, парсинг, сортировка) → Default. Blocking I/O (network, file, database) → IO. Если операция блокирует thread (waiting for I/O), используйте IO. Если операция использует CPU, используйте Default.

```kotlin
// ✅ Правильное использование
suspend fun dataProcessingPipeline() {
    // I/O: fetch data
    val data = withContext(Dispatchers.IO) { fetchData() }

    // CPU: process data
    val processed = withContext(Dispatchers.Default) { process(data) }

    // I/O: save result
    withContext(Dispatchers.IO) { save(processed) }
}

// ❌ Неправильное использование
suspend fun badPractice1() = withContext(Dispatchers.Default) {
    File("data.txt").readText()  // ❌ I/O в Default - thread блокируется
}

suspend fun badPractice2() = withContext(Dispatchers.IO) {
    (1..1_000_000).map { it * it }  // ❌ CPU work в IO - waste of threads
}
```

**Когда использовать Default:**

- JSON/XML parsing
- Image/video processing
- Sorting/filtering large collections
- Data compression/decompression
- Mathematical computations
- Algorithm execution

**Когда использовать IO:**

- Network requests (HTTP, WebSocket)
- Database queries (Room, SQLite)
- File I/O operations
- SharedPreferences/DataStore
- Blocking API calls

**Ключевые концепции:**

1. **CPU vs I/O** - Default для CPU, IO для blocking I/O
2. **Thread Pool Size** - Default = CPU cores, IO может быть больше
3. **Blocking Allowed** - IO позволяет blocking, Default нет
4. **Performance** - правильный dispatcher = лучше performance
5. **Context Switching** - переключайте dispatchers при смене операции типа

## Answer (EN)

**Dispatchers Theory:**
Dispatchers determine which thread coroutine executes on. `Dispatchers.Default` - CPU-intensive tasks (computation-heavy), shared thread pool = CPU cores. `Dispatchers.IO` - blocking I/O operations (network, file, database), shared thread pool up to 64 threads. Key difference: Default for heavy computation, IO for blocking I/O.

**Differences:**

| Feature | Dispatchers.Default | Dispatchers.IO |
|---------|---------------------|----------------|
| **Purpose** | CPU-intensive work | I/O-bound operations |
| **Thread Pool Size** | CPU cores (min 2) | Up to 64 threads |
| **Blocking** | Should avoid blocking | Designed for blocking |
| **Use Cases** | Parsing, sorting, calculations | Network, files, database |
| **Thread Type** | Shared computational pool | Shared I/O pool |

**Dispatchers.Default - CPU-Intensive Operations:**

*Theory:* Default used for CPU-intensive tasks that maximize CPU usage. Thread pool size = number of CPU cores (minimum 2). Threads shouldn't block. Used for: computation-heavy operations, JSON/XML parsing, image processing, mathematical computations.

```kotlin
// ✅ Dispatchers.Default for CPU-intensive tasks
suspend fun parseJsonData(json: String): List<User> = withContext(Dispatchers.Default) {
    // CPU-intensive parsing
    Json.decodeFromString<List<User>>(json)
}

suspend fun sortLargeList(items: List<Int>): List<Int> = withContext(Dispatchers.Default) {
    items.sorted()  // CPU-intensive sorting
}

suspend fun calculateStatistics(data: List<Double>): Statistics = withContext(Dispatchers.Default) {
    Statistics(
        mean = data.average(),
        median = data.sorted()[data.size / 2]
    )
}

// ✅ Image processing
suspend fun compressImage(image: Bitmap): ByteArray = withContext(Dispatchers.Default) {
    val outputStream = ByteArrayOutputStream()
    image.compress(Bitmap.CompressFormat.JPEG, 85, outputStream)
    outputStream.toByteArray()
}
```

**Dispatchers.IO - I/O Operations:**

*Theory:* IO used for blocking I/O operations, where threads can block (waiting for I/O). Thread pool larger (up to 64), because threads can idle. Used for: network requests, database queries, file operations, blocking API calls.

```kotlin
// ✅ Dispatchers.IO for I/O operations
suspend fun fetchUserFromNetwork(userId: Int): User = withContext(Dispatchers.IO) {
    api.getUser(userId)  // Network request - blocks thread
}

suspend fun saveToDatabase(user: User) = withContext(Dispatchers.IO) {
    database.userDao().insert(user)  // Database write - blocks thread
}

suspend fun readFileContents(path: String): String = withContext(Dispatchers.IO) {
    File(path).readText()  // File I/O - blocks thread
}

// ✅ Room database
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getAllUsers(): List<User>  // Used in Dispatchers.IO context
}
```

**Choosing Right Dispatcher:**

*Theory:* Selection criterion - operation nature. CPU-intensive (computations, parsing, sorting) → Default. Blocking I/O (network, file, database) → IO. If operation blocks thread (waiting for I/O), use IO. If operation uses CPU, use Default.

```kotlin
// ✅ Correct usage
suspend fun dataProcessingPipeline() {
    // I/O: fetch data
    val data = withContext(Dispatchers.IO) { fetchData() }

    // CPU: process data
    val processed = withContext(Dispatchers.Default) { process(data) }

    // I/O: save result
    withContext(Dispatchers.IO) { save(processed) }
}

// ❌ Incorrect usage
suspend fun badPractice1() = withContext(Dispatchers.Default) {
    File("data.txt").readText()  // ❌ I/O in Default - thread blocks
}

suspend fun badPractice2() = withContext(Dispatchers.IO) {
    (1..1_000_000).map { it * it }  // ❌ CPU work in IO - waste of threads
}
```

**When to use Default:**

- JSON/XML parsing
- Image/video processing
- Sorting/filtering large collections
- Data compression/decompression
- Mathematical computations
- Algorithm execution

**When to use IO:**

- Network requests (HTTP, WebSocket)
- Database queries (Room, SQLite)
- File I/O operations
- SharedPreferences/DataStore
- Blocking API calls

**Key Concepts:**

1. **CPU vs I/O** - Default for CPU, IO for blocking I/O
2. **Thread Pool Size** - Default = CPU cores, IO can be larger
3. **Blocking Allowed** - IO allows blocking, Default does not
4. **Performance** - right dispatcher = better performance
5. **Context Switching** - switch dispatchers when operation type changes

---

## Follow-ups

- What happens if you use Default dispatcher for I/O operations?
- Can you create custom dispatchers in Kotlin?
- How does thread pool size affect performance?

## Related Questions

### Prerequisites (Easier)
- Basic Kotlin coroutines
- Threading fundamentals

### Related (Same Level)
- [[q-coroutine-dispatchers--programming-languages--medium]] - All dispatchers overview
- [[q-coroutinescope-vs-supervisorscope--programming-languages--medium]] - Scope builders

### Advanced (Harder)
- [[q-concurrency-fundamentals--computer-science--hard]] - Concurrency concepts
- Custom dispatcher implementation
