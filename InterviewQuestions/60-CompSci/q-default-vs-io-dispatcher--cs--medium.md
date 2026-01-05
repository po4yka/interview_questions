---
id: cs-006
title: "Default vs IO Dispatcher / Разница между Default и IO Dispatcher"
aliases: ["Default vs IO Dispatcher", "Разница между Default и IO Dispatcher"]
topic: cs
subtopics: [coroutines, dispatchers, kotlin]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-coroutines, c-structured-concurrency]
created: 2025-10-13
updated: 2025-11-11
tags: [coroutines, default, difficulty/medium, dispatchers, io, kotlin, programming-languages]
sources: ["https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html"]

---
# Вопрос (RU)
> В чем разница между Default и IO dispatcher? Когда использовать каждый из них?

# Question (EN)
> What is the difference between Default dispatcher and IO dispatcher? When to use each?

---

## Ответ (RU)

**Теория Dispatchers:**
Dispatchers определяют, на каких потоках выполняются корутины. `Dispatchers.Default` — для CPU-intensive задач (computation-heavy), использует общий пул потоков с уровнем параллелизма примерно = количеству CPU-ядер (минимум 2). `Dispatchers.IO` — для потенциально блокирующих I/O операций (network, file, database): это «расширение» Default-пула, позволяющее большему числу операций выполняться параллельно (по умолчанию до 64 одновременно блокирующих задач), перераспределяя те же потоки под I/O-нагрузку.
Ключевое отличие: Default — для вычислений без блокировок, IO — для операций, которые могут блокировать поток или зависят от I/O.

**Различия:**

| Характеристика | Dispatchers.Default | Dispatchers.IO |
|----------------|---------------------|----------------|
| **Цель** | CPU-intensive work | I/O-bound / blocking operations |
| **Thread Pool Size** | ~ CPU cores (min 2) | Расширенный пул поверх Default (большее допустимое число параллельных задач, по умолчанию до 64 блокирующих) |
| **Blocking** | Блокировки нежелательны | Спроектирован для потенциально блокирующих вызовов |
| **Use Cases** | Parsing, sorting, calculations | Network, files, database (особенно блокирующие API) |
| **Thread Type** | Shared computational pool | Shared pool с увеличенной параллельностью под I/O |

**Dispatchers.Default - CPU-Интенсивные операции:**

*Теория:* Default используется для CPU-intensive задач, которые максимально загружают CPU. Размер пула потоков примерно равен количеству CPU-ядер (минимум 2). Потоки не должны надолго блокироваться (sleep, долгие блокирующие I/O-операции), чтобы не снижать общую пропускную способность.
Используется для: computation-heavy operations, JSON/XML parsing (если реализация реально CPU bound), image processing, математические вычисления.

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

// ✅ Image processing (CPU-bound)
suspend fun compressImage(image: Bitmap): ByteArray = withContext(Dispatchers.Default) {
    val outputStream = ByteArrayOutputStream()
    image.compress(Bitmap.CompressFormat.JPEG, 85, outputStream)
    outputStream.toByteArray()
}
```

**Dispatchers.IO - I/O Операции:**

*Теория:* IO используется для потенциально блокирующих I/O операций, где поток может ожидать результата (network, file, database, legacy-библиотеки). `Dispatchers.IO` использует общий пул потоков, основанный на Default, но с увеличенной допустимой параллельностью (по умолчанию до 64 одновременно блокирующих задач), чтобы блокировки не мешали CPU-вычислениям. Предпочтителен для: network requests, database queries, file operations, блокирующие API.

```kotlin
// ✅ Dispatchers.IO для I/O операций
suspend fun fetchUserFromNetwork(userId: Int): User = withContext(Dispatchers.IO) {
    api.getUser(userId)  // Network request; используем IO, особенно если это блокирующий вызов
}

suspend fun saveToDatabase(user: User) = withContext(Dispatchers.IO) {
    database.userDao().insert(user)  // DB write; IO особенно важен для блокирующих драйверов
}

suspend fun readFileContents(path: String): String = withContext(Dispatchers.IO) {
    File(path).readText()  // File I/O - классический блокирующий вызов
}

// ✅ Room database
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getAllUsers(): List<User>
    // Реализация Room сама использует подходящий диспетчер под капотом,
    // но вызовы часто делаются из Dispatchers.IO контекста, особенно для блокирующих сценариев
}
```

**Правильный выбор dispatcher:**

*Теория:* Критерий выбора — природа операции.
- CPU-intensive (вычисления, парсинг/обработка в памяти, сортировка) → `Dispatchers.Default`.
- Потенциально блокирующий I/O (network, file, database, старые синхронные API) → `Dispatchers.IO`.

Если операция реально блокирует поток ожиданием внешнего ресурса — используйте IO. Если операция в основном нагружает CPU — используйте Default. Если библиотека уже предоставляет неблокирующие `suspend`-функции, они могут эффективно работать и на Default, но для I/O по соглашению часто используют IO.

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
    File("data.txt").readText()  // ❌ Блокирующий I/O в Default - занимает вычислительный поток
}

suspend fun badPractice2() = withContext(Dispatchers.IO) {
    (1..1_000_000).map { it * it }  // ❌ Длительная CPU-работа в IO - неэффективно расходует I/O-пул
}
```

**Когда использовать Default:**

- JSON/XML parsing (CPU-bound реализация)
- Image/video processing
- Sorting/filtering large collections
- Data compression/decompression
- Mathematical computations
- Algorithm execution

**Когда использовать IO:**

- Network requests (HTTP, WebSocket), особенно при использовании блокирующих клиентов
- Database queries (Room, SQLite, JDBC и др. блокирующие драйверы)
- File I/O operations
- Работа с SharedPreferences или другими строго блокирующими хранилищами
- Legacy / blocking API calls

**Ключевые концепции:**

1. **CPU vs I/O** — Default для CPU-bound, IO для потенциально блокирующего I/O
2. **Thread Pool / Parallelism** — Default ≈ CPU cores; IO увеличивает доступную параллельность для блокирующих задач
3. **Blocking Allowed** — в IO допускаются блокирующие вызовы; в Default их следует избегать
4. **Performance** — правильный выбор диспетчера улучшает latency и throughput
5. **`Context` Switching** — переключайте диспетчеры при смене характера работы (CPU ↔ I/O)

## Answer (EN)

**Dispatchers Theory:**
Dispatchers determine which threads coroutines execute on. `Dispatchers.Default` is for CPU-intensive (computation-heavy) tasks; it uses a shared thread pool with parallelism roughly equal to the number of CPU cores (minimum 2). `Dispatchers.IO` is for potentially blocking I/O operations (network, file, database); it is effectively an extension of the Default pool that allows more concurrent blocking operations (by default up to 64 concurrent blocking tasks) by repurposing threads for I/O-heavy workloads.
Key difference: Default for non-blocking CPU-bound computations, IO for operations that may block threads or depend on I/O.

**Differences:**

| Feature | Dispatchers.Default | Dispatchers.IO |
|---------|---------------------|----------------|
| **Purpose** | CPU-intensive work | I/O-bound / blocking operations |
| **Thread Pool Size** | ~ CPU cores (min 2) | Extended pool on top of Default (higher allowed parallelism, default cap around 64 blocking tasks) |
| **Blocking** | Blocking should be avoided | Designed for potentially blocking calls |
| **Use Cases** | Parsing, sorting, calculations | Network, files, database (especially blocking APIs) |
| **Thread Type** | Shared computational pool | Shared pool with increased parallelism for I/O |

**Dispatchers.Default - CPU-Intensive Operations:**

*Theory:* Default is used for CPU-intensive tasks that maximize CPU usage. Thread pool size is approximately equal to the number of CPU cores (minimum 2). Threads should not be blocked for long (sleep, long blocking I/O), to avoid harming throughput.
Use for: computation-heavy operations, JSON/XML parsing when it is effectively CPU-bound, image processing, mathematical computations.

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

// ✅ Image processing (CPU-bound)
suspend fun compressImage(image: Bitmap): ByteArray = withContext(Dispatchers.Default) {
    val outputStream = ByteArrayOutputStream()
    image.compress(Bitmap.CompressFormat.JPEG, 85, outputStream)
    outputStream.toByteArray()
}
```

**Dispatchers.IO - I/O Operations:**

*Theory:* IO is used for potentially blocking I/O operations, where a thread may wait for the result (network, file, database, legacy libraries). `Dispatchers.IO` uses a shared pool built on top of Default but with increased allowed parallelism (by default up to 64 concurrently blocking tasks), so that blocking calls do not starve CPU computations.
Use for: network requests, database queries, file operations, blocking APIs.

```kotlin
// ✅ Dispatchers.IO for I/O operations
suspend fun fetchUserFromNetwork(userId: Int): User = withContext(Dispatchers.IO) {
    api.getUser(userId)  // Network request; use IO, especially if the client is blocking
}

suspend fun saveToDatabase(user: User) = withContext(Dispatchers.IO) {
    database.userDao().insert(user)  // Database write; IO is important for blocking drivers
}

suspend fun readFileContents(path: String): String = withContext(Dispatchers.IO) {
    File(path).readText()  // Classic blocking File I/O
}

// ✅ Room database
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getAllUsers(): List<User>
    // Room's implementation manages threading internally,
    // but callers often use it from Dispatchers.IO when interacting with blocking layers
}
```

**Choosing Right Dispatcher:**

*Theory:* The key criterion is the nature of the operation.
- CPU-intensive (computations, in-memory processing/parsing, sorting) → `Dispatchers.Default`.
- Potentially blocking I/O (network, file, database, legacy synchronous APIs) → `Dispatchers.IO`.

If an operation truly blocks a thread while waiting on an external resource, use IO. If it primarily uses CPU, use Default. If a library provides proper non-blocking suspend functions, they can run efficiently even on Default, but by convention I/O-related work is often dispatched to IO.

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
    File("data.txt").readText()  // ❌ Blocking I/O on Default - occupies a computational thread
}

suspend fun badPractice2() = withContext(Dispatchers.IO) {
    (1..1_000_000).map { it * it }  // ❌ Long CPU work on IO - misuses threads intended for I/O-heavy tasks
}
```

**When to use Default:**

- JSON/XML parsing (if CPU-bound)
- Image/video processing
- Sorting/filtering large collections
- Data compression/decompression
- Mathematical computations
- Algorithm execution

**When to use IO:**

- Network requests (HTTP, WebSocket), especially with blocking clients
- Database queries (Room, SQLite, JDBC, other blocking drivers)
- File I/O operations
- Working with SharedPreferences or other strictly blocking storage
- Legacy / blocking API calls

**Key Concepts:**

1. **CPU vs I/O** - Default for CPU-bound, IO for potentially blocking I/O
2. **Thread Pool / Parallelism** - Default ≈ CPU cores; IO increases available parallelism for blocking tasks
3. **Blocking Allowed** - Blocking is acceptable on IO; should be avoided on Default
4. **Performance** - choosing the right dispatcher improves latency and throughput
5. **`Context` Switching** - switch dispatchers when the nature of work changes (CPU ↔ I/O)

---

## Follow-ups

- What happens if you use Default dispatcher for I/O operations?
- Can you create custom dispatchers in Kotlin?
- How does thread pool size / parallelism configuration affect performance?

## Related Questions

### Prerequisites (Easier)
- Basic Kotlin coroutines
- Threading fundamentals

### Related (Same Level)
- Overview of coroutine dispatchers
- `Coroutine` scope builders

### Advanced (Harder)
- Concurrency concepts
- Custom dispatcher implementation

## References

- [[c-coroutines]]
- [[c-structured-concurrency]]
- "Kotlin `Coroutine` `Context` and Dispatchers" - official docs
