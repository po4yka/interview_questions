---
id: dp-007
title: "Proxy Pattern / Proxy Паттерн"
aliases: [Proxy Pattern, Proxy Паттерн]
topic: cs
subtopics: [design-patterns]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-architecture-patterns, q-adapter-pattern--cs--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [cs, design-patterns, difficulty/medium, gof-patterns, proxy, structural-patterns, surrogate]
---
# Вопрос (RU)
> Что такое паттерн Proxy? Когда и зачем его следует использовать?

# Question (EN)
> What is the Proxy pattern? When and why should it be used?

---

## Ответ (RU)

**Proxy (Заместитель)** - это структурный паттерн проектирования, который предоставляет объект-заместитель, контролирующий доступ к другому объекту. Прокси перехватывает обращения и может добавлять дополнительную функциональность до или после передачи вызова оригинальному объекту.

### Определение

Паттерн проектирования Proxy (Заместитель) использует **объект-заместитель для контроля доступа к другому объекту**. Вместо прямого взаимодействия с основным объектом клиент обращается к прокси, который затем управляет взаимодействием. Это полезно для контроля доступа, ленивой инициализации, логирования, кэширования или добавления проверок безопасности.

### Проблемы, Которые Решает

Какие проблемы решает паттерн Proxy:

1. **Доступ к объекту должен быть контролируемым**
2. **При обращении к объекту должна предоставляться дополнительная функциональность**

### Решение

Определить отдельный объект **`Proxy`**, который:

- Может использоваться как заместитель другого объекта (**`Subject`**)
- Реализует дополнительную функциональность для контроля доступа к этому объекту

Это позволяет работать через объект Proxy для выполнения дополнительной функциональности при обращении к объекту, такой как проверка прав доступа, кэширование или логирование.

Чтобы действовать как заместитель объекта, прокси должен реализовывать интерфейс **`Subject`**. Клиенты не должны замечать, работают ли они с реальным объектом или с его прокси.

### Типы Прокси

Основные варианты использования:

1. **Ленивая инициализация (Virtual Proxy)** - откладывает создание дорогих объектов до момента необходимости
2. **Контроль доступа (Protection Proxy)** - управляет доступом к объекту, разрешая/запрещая операции на основе прав
3. **Доступ к удаленным объектам (Remote Proxy)** - представляет объект в другом процессе/расположении, обрабатывает коммуникацию
4. **Логирование и мониторинг (Logging Proxy)** - записывает операции над объектом
5. **Кэширование (Cache Proxy)** - сохраняет результаты операций, возвращает закэшированные данные для повторных запросов

### Пример: Контроль Доступа К Базе Данных

```kotlin
// Шаг 1: Интерфейс
interface Database {
    fun query(dbQuery: String): String
}

// Шаг 2: Реальный объект
class RealDatabase : Database {
    override fun query(dbQuery: String): String {
        // Эмуляция обращения к базе данных
        return "Executing query: $dbQuery"
    }
}

// Шаг 3: Объект Proxy
class ProxyDatabase(private val userRole: String) : Database {
    private val realDatabase = RealDatabase()
    private val restrictedQueries = listOf("DROP", "DELETE", "TRUNCATE")

    override fun query(dbQuery: String): String {
        // Контроль доступа
        if (userRole != "ADMIN" &&
            restrictedQueries.any { dbQuery.contains(it, ignoreCase = true) }) {
            return "Access Denied: You don't have permission for this operation"
        }

        // Логирование
        println("Logging: $dbQuery by $userRole")

        return realDatabase.query(dbQuery)
    }
}

fun main() {
    val adminDB = ProxyDatabase("ADMIN")
    println(adminDB.query("SELECT * FROM users"))
    println(adminDB.query("DROP TABLE users"))

    val userDB = ProxyDatabase("USER")
    println(userDB.query("SELECT * FROM users"))
    println(userDB.query("DROP TABLE users"))
}
```

### Android Пример: Ленивая Загрузка Изображения

```kotlin
// Интерфейс Subject
interface Image {
    fun display()
}

// Реальный объект
class RealImage(private val filename: String) : Image {
    init {
        loadFromDisk()
    }

    private fun loadFromDisk() {
        println("Loading image from disk: $filename")
        // Эмуляция дорогой операции
        Thread.sleep(1000)
    }

    override fun display() {
        println("Displaying image: $filename")
    }
}

// Proxy с ленивой загрузкой
class ProxyImage(private val filename: String) : Image {
    private var realImage: RealImage? = null

    override fun display() {
        if (realImage == null) {
            realImage = RealImage(filename)
        }
        realImage?.display()
    }
}

// Использование
fun main() {
    val image1: Image = ProxyImage("photo1.jpg")
    val image2: Image = ProxyImage("photo2.jpg")

    // Объекты созданы, но изображение ещё не загружено
    println("Images created but not loaded")

    // Загрузка только при необходимости
    image1.display()  // Загружает и отображает
    image1.display()  // Повторно только отображает (уже загружено)
}
```

### Kotlin Пример: Кэширующий Proxy

```kotlin
import kotlinx.coroutines.delay

// Subject
interface ApiService {
    suspend fun fetchUserData(userId: String): User
}

data class User(val id: String, val name: String)

// Реальная реализация
class RealApiService : ApiService {
    override suspend fun fetchUserData(userId: String): User {
        println("Fetching user $userId from API...")
        delay(1000) // Эмуляция сетевой задержки
        return User(userId, "User $userId")
    }
}

// Кэширующий Proxy
class CachingApiProxy(
    private val realService: ApiService
) : ApiService {
    private val cache = mutableMapOf<String, Pair<User, Long>>()
    private val cacheTimeout = 5000L // 5 секунд

    override suspend fun fetchUserData(userId: String): User {
        val cached = cache[userId]
        val now = System.currentTimeMillis()

        return if (cached != null && (now - cached.second) < cacheTimeout) {
            println("Returning cached user $userId")
            cached.first
        } else {
            val user = realService.fetchUserData(userId)
            cache[userId] = user to now
            user
        }
    }
}

// Использование (в coroutine scope)
// suspend fun demo() {
//     val proxy: ApiService = CachingApiProxy(RealApiService())
//
//     proxy.fetchUserData("123") // Запрос к API
//     proxy.fetchUserData("123") // Возврат из кэша
//     delay(6000)
//     proxy.fetchUserData("123") // Кэш истёк, снова запрос к API
// }
```

### Android Retrofit Пример: Логирующий/мониторящий Proxy

```kotlin
// OkHttp Interceptor как прокси-подобная обёртка вокруг запросов
class LoggingInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()

        // До вызова
        val t1 = System.nanoTime()
        Log.d("HTTP", "Sending request ${request.url}")

        val response = chain.proceed(request)

        // После вызова
        val t2 = System.nanoTime()
        Log.d("HTTP", "Received response in ${(t2 - t1) / 1e6} ms")

        return response
    }
}

// Настройка Retrofit
val okHttpClient = OkHttpClient.Builder()
    .addInterceptor(LoggingInterceptor())
    .build()

val retrofit = Retrofit.Builder()
    .client(okHttpClient)
    .baseUrl("https://api.example.com")
    .build()
```

### Объяснение

- **`Database`** - общий интерфейс для `RealDatabase` и `ProxyDatabase`.
- **`RealDatabase`** выполняет реальные операции.
- **`ProxyDatabase`** контролирует доступ, добавляет логирование, ограничивает опасные запросы.
- **`Image` / `ProxyImage` / `RealImage`** демонстрируют виртуальный прокси с ленивой загрузкой.
- **`ApiService` / `CachingApiProxy`** демонстрируют кэширующий прокси.
- **OkHttp Interceptors** выступают как прокси-подобные обёртки над HTTP-запросами, добавляя логирование, аутентификацию и другие сквозные аспекты.

### Преимущества

1. **Разделение ответственности** - отделяет бизнес-логику от вспомогательных обязанностей.
2. **Оптимизация производительности** - ленивая инициализация и кэширование могут улучшать производительность.
3. **Контроль доступа** - позволяет контролировать и валидировать доступ к объектам.
4. **Прозрачность для клиента** - при общем интерфейсе клиенту не нужно знать о наличии прокси.
5. **Принцип открытости/закрытости** - можно добавлять новые прокси без изменения клиентского кода.

### Недостатки

1. **Дополнительная сложность** - дополнительный уровень косвенности.
2. **Накладные расходы на производительность** - дополнительный вызов между клиентом и реальным объектом.
3. **Сложность проектирования** - требует хорошего понимания варианта использования.
4. **Накладные расходы на тестирование** - больше компонентов для тестирования.
5. **Проблемы с памятью** - кэширующие прокси могут вызывать перерасход памяти при отсутствии политики очистки.

### Примеры В Android

Паттерн Proxy активно используется в следующих сценариях:

- **Ленивая загрузка изображений** - прокси-объект откладывает загрузку до момента отображения.
- **Перехват HTTP-запросов (OkHttp Interceptors)** - добавляют логирование, аутентификацию, кэширование.
- **Кэширование сетевых ответов** - прокси оборачивает сетевой слой и повторно использует результаты.
- **Контроль доступа к базе данных или файловой системе** - прокси ограничивает операции в зависимости от прав.

### Лучшие Практики (Best Practices)

```kotlin
// DO: использовать для ленивой инициализации дорогих объектов
interface ImageViewLike {
    fun display()
}

class LazyImageProxy(private val url: String) : ImageViewLike {
    private val bitmap: Bitmap by lazy {
        loadImageFromNetwork(url)
    }

    override fun display() {
        // Делегирование отрисовки логике UI, используя загруженный bitmap
        render(bitmap)
    }
}

// DO: использовать для контроля доступа
interface FileAccess {
    fun read(): String
}

class ProtectedFileProxy(
    private val file: File,
    private val permissions: Permissions
) : FileAccess {
    override fun read(): String {
        if (!permissions.canRead) throw SecurityException("No read permission")
        return file.readText()
    }
}

// DO: использовать для логирования и мониторинга
interface Service {
    fun execute()
}

class MonitoringProxy(
    private val real: Service,
    private val metrics: MetricsCollector
) : Service {
    override fun execute() {
        val start = System.currentTimeMillis()
        real.execute()
        metrics.record(System.currentTimeMillis() - start)
    }
}

// DO: комбинировать с корутинами для асинхронных операций
interface DataService {
    suspend fun fetchData(key: String): Data
}

class AsyncCacheProxy(
    private val service: DataService
) : DataService {
    private val cache = mutableMapOf<String, Deferred<Data>>()

    override suspend fun fetchData(key: String): Data {
        val deferred = cache.getOrPut(key) {
            CoroutineScope(Dispatchers.IO).async {
                service.fetchData(key)
            }
        }
        return deferred.await()
    }
}

// DON'T: использовать, если прокси только прозрачно пробрасывает вызовы без доп. поведения
// DON'T: создавать глубокие цепочки прокси
// DON'T: хранить большие объёмы данных в кэширующих прокси без политики очистки
```

### Краткое Резюме

Паттерн **Proxy** предоставляет заместитель (placeholder) для управления доступом к другому объекту.

- **Проблема**: нужен контроль доступа, ленивая инициализация, логирование, кэширование или удалённый доступ.
- **Решение**: создать прокси, реализующий тот же интерфейс, что и реальный объект, и делегирующий ему вызовы с добавлением дополнительного поведения.
- **Когда использовать**: при необходимости ленивой инициализации, контроля прав, мониторинга, кэширования или работы с удалёнными объектами.
- **В Android**: ленивая загрузка изображений, перехват HTTP-запросов (OkHttp), кэширование, контроль доступа к ресурсам.

---

## Answer (EN)

**Proxy** is a structural design pattern that provides a substitute object controlling access to another object. The proxy intercepts calls and can add extra behavior before or after delegating to the real object.

### Definition

The Proxy Design Pattern uses a **placeholder object to control access to another object**. Instead of interacting directly with the main object, the client talks to the proxy, which manages the interaction. This is useful for access control, lazy initialization, logging, caching, or security checks.

### Problems it Solves

1. **Access to an object should be controlled.**
2. **Additional behavior should be executed when accessing an object.**

### Solution

Define a separate **`Proxy`** object that:

- Can be used as a substitute for another object (**`Subject`**).
- Implements additional logic to control access to this subject.

The proxy implements the same interface as the real subject so clients cannot tell whether they work with the subject or its proxy.

### Types of Proxies

1. **Virtual Proxy (Lazy initialization)** - delays creation of expensive objects.
2. **Protection Proxy (Access control)** - checks permissions before delegating.
3. **Remote Proxy** - represents an object in a different process/machine.
4. **Logging Proxy** - logs operations performed on the object.
5. **Cache Proxy** - caches results and returns them on repeated calls.

### Example: Database Access Control

```kotlin
// Step 1: Interface
interface Database {
    fun query(dbQuery: String): String
}

// Step 2: Real Object
class RealDatabase : Database {
    override fun query(dbQuery: String): String {
        // Simulating a database operation
        return "Executing query: $dbQuery"
    }
}

// Step 3: Proxy Object
class ProxyDatabase(private val userRole: String) : Database {
    private val realDatabase = RealDatabase()
    private val restrictedQueries = listOf("DROP", "DELETE", "TRUNCATE")

    override fun query(dbQuery: String): String {
        // Access control
        if (userRole != "ADMIN" &&
            restrictedQueries.any { dbQuery.contains(it, ignoreCase = true) }) {
            return "Access Denied: You don't have permission for this operation"
        }

        // Logging
        println("Logging: $dbQuery by $userRole")

        return realDatabase.query(dbQuery)
    }
}

fun main() {
    val adminDB = ProxyDatabase("ADMIN")
    println(adminDB.query("SELECT * FROM users"))
    println(adminDB.query("DROP TABLE users"))

    val userDB = ProxyDatabase("USER")
    println(userDB.query("SELECT * FROM users"))
    println(userDB.query("DROP TABLE users"))
}
```

### Android Example: Image Lazy Loading

```kotlin
// Subject interface
interface Image {
    fun display()
}

// Real object
class RealImage(private val filename: String) : Image {
    init {
        loadFromDisk()
    }

    private fun loadFromDisk() {
        println("Loading image from disk: $filename")
        // Simulate expensive operation
        Thread.sleep(1000)
    }

    override fun display() {
        println("Displaying image: $filename")
    }
}

// Proxy with lazy loading
class ProxyImage(private val filename: String) : Image {
    private var realImage: RealImage? = null

    override fun display() {
        if (realImage == null) {
            realImage = RealImage(filename)
        }
        realImage?.display()
    }
}

// Usage
fun main() {
    val image1: Image = ProxyImage("photo1.jpg")
    val image2: Image = ProxyImage("photo2.jpg")

    // Images not loaded yet
    println("Images created but not loaded")

    // Load only when needed
    image1.display()  // Loads and displays
    image1.display()  // Just displays (already loaded)
}
```

### Kotlin Example: Caching Proxy

```kotlin
import kotlinx.coroutines.delay

// Subject
interface ApiService {
    suspend fun fetchUserData(userId: String): User
}

data class User(val id: String, val name: String)

// Real implementation
class RealApiService : ApiService {
    override suspend fun fetchUserData(userId: String): User {
        println("Fetching user $userId from API...")
        delay(1000) // Simulate network delay
        return User(userId, "User $userId")
    }
}

// Caching Proxy
class CachingApiProxy(
    private val realService: ApiService
) : ApiService {
    private val cache = mutableMapOf<String, Pair<User, Long>>()
    private val cacheTimeout = 5000L // 5 seconds

    override suspend fun fetchUserData(userId: String): User {
        val cached = cache[userId]
        val now = System.currentTimeMillis()

        return if (cached != null && (now - cached.second) < cacheTimeout) {
            println("Returning cached user $userId")
            cached.first
        } else {
            val user = realService.fetchUserData(userId)
            cache[userId] = user to now
            user
        }
    }
}

// Usage (in coroutine scope)
// suspend fun demo() {
//     val proxy: ApiService = CachingApiProxy(RealApiService())
//
//     proxy.fetchUserData("123") // Fetches from API
//     proxy.fetchUserData("123") // Returns from cache
//     delay(6000)
//     proxy.fetchUserData("123") // Cache expired, fetches from API
// }
```

### Android Retrofit Example: Logging/Monitoring Proxy

```kotlin
// Using OkHttp Interceptor (acts as a proxy/decorator around requests)
class LoggingInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()

        // Before
        val t1 = System.nanoTime()
        Log.d("HTTP", "Sending request ${request.url}")

        val response = chain.proceed(request)

        // After
        val t2 = System.nanoTime()
        Log.d("HTTP", "Received response in ${(t2 - t1) / 1e6} ms")

        return response
    }
}

// Retrofit setup
val okHttpClient = OkHttpClient.Builder()
    .addInterceptor(LoggingInterceptor())
    .build()

val retrofit = Retrofit.Builder()
    .client(okHttpClient)
    .baseUrl("https://api.example.com")
    .build()
```

### Explanation

- **`Database`** is the common interface for `RealDatabase` and `ProxyDatabase`.
- **`RealDatabase`** performs real operations.
- **`ProxyDatabase`** controls access, logs actions, restricts dangerous queries.
- **`Image` / `ProxyImage` / `RealImage`** demonstrate a Virtual Proxy via lazy loading.
- **`ApiService` / `CachingApiProxy`** demonstrate a Caching Proxy.
- **OkHttp Interceptors** behave as proxy-like wrappers around HTTP requests for logging, auth, monitoring, etc.

### Pros and Cons

Pros:

1. Separation of concerns.
2. Performance optimization via lazy loading and caching.
3. Access control and validation.
4. Transparency to clients via shared interface.
5. Supports Open/Closed Principle.

Cons:

1. Extra indirection and complexity.
2. Small performance overhead.
3. More components to reason about and test.
4. Risk of memory issues if cache proxies are not managed.

### Best Practices

```kotlin
// DO: Use for lazy initialization of expensive objects
interface ImageViewLike {
    fun display()
}

class LazyImageProxy(private val url: String) : ImageViewLike {
    private val bitmap: Bitmap by lazy {
        loadImageFromNetwork(url)
    }

    override fun display() {
        // Delegate drawing to underlying UI logic using the loaded bitmap
        render(bitmap)
    }
}

// DO: Use for access control
interface FileAccess {
    fun read(): String
}

class ProtectedFileProxy(
    private val file: File,
    private val permissions: Permissions
) : FileAccess {
    override fun read(): String {
        if (!permissions.canRead) throw SecurityException("No read permission")
        return file.readText()
    }
}

// DO: Use for logging and monitoring
interface Service {
    fun execute()
}

class MonitoringProxy(
    private val real: Service,
    private val metrics: MetricsCollector
) : Service {
    override fun execute() {
        val start = System.currentTimeMillis()
        real.execute()
        metrics.record(System.currentTimeMillis() - start)
    }
}

// DO: Combine with coroutines for async operations
interface DataService {
    suspend fun fetchData(key: String): Data
}

class AsyncCacheProxy(
    private val service: DataService
) : DataService {
    private val cache = mutableMapOf<String, Deferred<Data>>()

    override suspend fun fetchData(key: String): Data {
        val deferred = cache.getOrPut(key) {
            CoroutineScope(Dispatchers.IO).async {
                service.fetchData(key)
            }
        }
        return deferred.await()
    }
}

// DON'T: Use when proxy only forwards calls without adding value
// DON'T: Create deep chains of proxies
// DON'T: Keep large data in cache proxies without eviction
```

### Summary

Proxy is a structural pattern that provides a placeholder to control access to another object.

- Problem: need to control access, add behavior, or optimize interactions.
- Solution: introduce a proxy implementing the same interface and delegating to the real object with extra behavior.
- Use when: lazy loading, access control, logging/monitoring, caching, remote access are required.
- Android: image lazy loading, HTTP interception (OkHttp), caching layers.

---

## Связанные Вопросы (RU)

- [[q-adapter-pattern--cs--medium]]

## Related Questions

- [[q-adapter-pattern--cs--medium]]

## References

- [[c-architecture-patterns]]
- [Proxy Design Pattern](https://www.geeksforgeeks.org/system-design/proxy-design-pattern/)
- [Proxy pattern](https://en.wikipedia.org/wiki/Proxy_pattern)
- [Proxy Design Pattern](https://sourcemaking.com/design_patterns/proxy)
- [Proxy](https://refactoring.guru/design-patterns/proxy)
- [Kotlin Design Patterns: Simplifying the Proxy Pattern](https://fugisawa.com/articles/kotlin-design-patterns-simplifying-the-proxy-pattern/)
- [Proxy Design Pattern in Kotlin](https://www.javaguides.net/2023/10/proxy-design-pattern-in-kotlin.html)
- [Understanding the Proxy design Pattern in Kotlin](https://medium.com/@samibel/understanding-the-proxy-design-pattern-in-kotlin-23fee0fe8aac)

---
*Source: Kirchhoff Android Interview Questions*