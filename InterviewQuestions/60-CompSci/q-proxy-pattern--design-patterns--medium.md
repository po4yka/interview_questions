---
tags:
  - design-patterns
  - structural-patterns
  - proxy
  - gof-patterns
  - surrogate
difficulty: medium
status: draft
---

# Proxy Pattern

# Question (EN)
> What is the Proxy pattern? When and why should it be used?

# Вопрос (RU)
> Что такое паттерн Proxy? Когда и зачем его следует использовать?

---

## Answer (EN)


**Proxy (Заместитель)** - это структурный паттерн проектирования, который предоставляет объект-заместитель, контролирующий доступ к другому объекту. Прокси перехватывает обращения и может добавлять дополнительную функциональность до или после передачи вызова оригинальному объекту.

### Definition


The Proxy Design Pattern is a structural design pattern that uses a **placeholder object to control access to another object**. Instead of interacting directly with the main object, the client talks to the proxy, which then manages the interaction. This is useful for controlling access, lazy initialization, logging, or adding security checks.

### Problems it Solves


What problems can the Proxy design pattern solve?

1. **The access to an object should be controlled**
2. **Additional functionality should be provided when accessing an object**

### Solution


Define a separate **`Proxy`** object that:

- Can be used as a substitute for another object (**`Subject`**)
- Implements additional functionality to control the access to this subject

This makes it possible to work through a Proxy object to perform additional functionality when accessing a subject, like checking access rights, caching, or logging.

To act as a substitute for a subject, a proxy must implement the **`Subject`** interface. Clients can't tell whether they work with a subject or its proxy.

## Типы прокси

The main use cases are:

1. **Lazy initialization (Virtual Proxy)** - Delays the creation of expensive objects until necessary
2. **Access control (Protection Proxy)** - Manages access to an object, allowing/denying operations based on permissions
3. **Remote object access (Remote Proxy)** - Represents an object in different location, handles communication
4. **Logging requests (Logging Proxy)** - Records operations on an object
5. **Caching (Cache Proxy)** - Stores results of operations, returns cached data for repeated requests

## Пример: Database Access Control

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

**Output**:
```
Logging: SELECT * FROM users by ADMIN
Executing query: SELECT * FROM users
Logging: DROP TABLE users by ADMIN
Executing query: DROP TABLE users
Logging: SELECT * FROM users by USER
Executing query: SELECT * FROM users
Access Denied: You don't have permission for this operation
```

## Android Example: Image Lazy Loading

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

// Usage in ImageView
class ImageLoader {
    fun loadImage(filename: String): Image {
        // Return proxy instead of real image
        return ProxyImage(filename)
    }
}

fun main() {
    val imageLoader = ImageLoader()
    val image1 = imageLoader.loadImage("photo1.jpg")
    val image2 = imageLoader.loadImage("photo2.jpg")

    // Images not loaded yet
    println("Images created but not loaded")

    // Load only when needed
    image1.display()  // Loads and displays
    image1.display()  // Just displays (already loaded)
}
```

## Kotlin Example: Caching Proxy

```kotlin
// Subject
interface ApiService {
    suspend fun fetchUserData(userId: String): User
}

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
    private val realService: RealApiService
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

// Usage
suspend fun main() {
    val proxy = CachingApiProxy(RealApiService())

    proxy.fetchUserData("123") // Fetches from API
    proxy.fetchUserData("123") // Returns from cache
    delay(6000)
    proxy.fetchUserData("123") // Cache expired, fetches from API
}
```

## Android Retrofit Example: Logging Proxy

```kotlin
// Using OkHttp Interceptor (Proxy pattern)
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

// Retrofit setup with proxy
val okHttpClient = OkHttpClient.Builder()
    .addInterceptor(LoggingInterceptor())
    .build()

val retrofit = Retrofit.Builder()
    .client(okHttpClient)
    .baseUrl("https://api.example.com")
    .build()
```

### Explanation


**Explanation**:

- **`Database`** is the common interface for RealDatabase and ProxyDatabase
- **RealDatabase** performs the real operations
- **ProxyDatabase** controls access, adds logging, restricts certain queries
- **Android**: Lazy loading images, caching network responses, access control
- **OkHttp Interceptors** are a perfect example of Proxy pattern

## Преимущества и недостатки

### Pros (Преимущества)


1. **Separation of Concerns** - Separates business logic from auxiliary responsibilities
2. **Performance optimization** - Lazy initialization and caching improve performance
3. **Access control** - Can control and validate access to objects
4. **Transparent to client** - Client doesn't need to know about the proxy
5. **Open/Closed Principle** - Can add new proxies without changing existing code

### Cons (Недостатки)


1. **Additional complexity** - Extra layer of indirection
2. **Performance overhead** - Slight performance cost from indirection
3. **Design complexity** - Requires good understanding of use case
4. **Testing overhead** - More components to test
5. **Memory concerns** - Caching proxies can cause memory issues if not managed properly

## Best Practices

```kotlin
// - DO: Use for lazy initialization of expensive objects
class LazyImageProxy(private val url: String) : ImageView {
    private val realImage: Bitmap by lazy {
        loadImageFromNetwork(url)
    }

    override fun display() {
        canvas.draw(realImage)
    }
}

// - DO: Use for access control
class ProtectedFileProxy(
    private val file: File,
    private val permissions: Permissions
) : FileAccess {
    override fun read(): String {
        if (!permissions.canRead) throw SecurityException("No read permission")
        return file.readText()
    }
}

// - DO: Use for logging and monitoring
class MonitoringProxy<T>(
    private val real: T,
    private val metrics: MetricsCollector
) where T : Service {
    fun execute() {
        val start = System.currentTimeMillis()
        real.execute()
        metrics.record(System.currentTimeMillis() - start)
    }
}

// - DO: Combine with coroutines for async operations
class AsyncCacheProxy(
    private val service: DataService
) {
    private val cache = mutableMapOf<String, Deferred<Data>>()

    suspend fun getData(key: String): Data {
        return cache.getOrPut(key) {
            CoroutineScope(Dispatchers.IO).async {
                service.fetchData(key)
            }
        }.await()
    }
}

// - DON'T: Use for simple pass-through operations
// - DON'T: Create deep proxy chains
// - DON'T: Store large amounts of data in caching proxies
```

**English**: **Proxy** is a structural pattern that provides a placeholder to control access to another object. **Problem**: Need to control access, add functionality when accessing objects. **Solution**: Create proxy that implements same interface and delegates to real object while adding extra behavior. **Use when**: (1) Lazy initialization needed, (2) Access control required, (3) Logging/caching desired, (4) Remote object access. **Android**: Image lazy loading, OkHttp interceptors, caching layers. **Pros**: access control, performance optimization, transparent to client. **Cons**: complexity, performance overhead. **Examples**: Lazy image loading, database access control, caching proxy, logging interceptors.

## Links

- [Proxy Design Pattern](https://www.geeksforgeeks.org/system-design/proxy-design-pattern/)
- [Proxy pattern](https://en.wikipedia.org/wiki/Proxy_pattern)
- [Kotlin Design Patterns: Simplifying the Proxy Pattern](https://fugisawa.com/articles/kotlin-design-patterns-simplifying-the-proxy-pattern/)
- [Proxy Design Pattern in Kotlin](https://www.javaguides.net/2023/10/proxy-design-pattern-in-kotlin.html)

## Further Reading

- [Proxy Design Pattern](https://sourcemaking.com/design_patterns/proxy)
- [Proxy](https://refactoring.guru/design-patterns/proxy)
- [Understanding the Proxy design Pattern in Kotlin](https://medium.com/@samibel/understanding-the-proxy-design-pattern-in-kotlin-23fee0fe8aac)

---
*Source: Kirchhoff Android Interview Questions*


## Ответ (RU)

### Определение


The Proxy Design Pattern is a structural design pattern that uses a **placeholder object to control access to another object**. Instead of interacting directly with the main object, the client talks to the proxy, which then manages the interaction. This is useful for controlling access, lazy initialization, logging, or adding security checks.

### Проблемы, которые решает


What problems can the Proxy design pattern solve?

1. **The access to an object should be controlled**
2. **Additional functionality should be provided when accessing an object**

### Решение


Define a separate **`Proxy`** object that:

- Can be used as a substitute for another object (**`Subject`**)
- Implements additional functionality to control the access to this subject

This makes it possible to work through a Proxy object to perform additional functionality when accessing a subject, like checking access rights, caching, or logging.

To act as a substitute for a subject, a proxy must implement the **`Subject`** interface. Clients can't tell whether they work with a subject or its proxy.

### Объяснение


**Explanation**:

- **`Database`** is the common interface for RealDatabase and ProxyDatabase
- **RealDatabase** performs the real operations
- **ProxyDatabase** controls access, adds logging, restricts certain queries
- **Android**: Lazy loading images, caching network responses, access control
- **OkHttp Interceptors** are a perfect example of Proxy pattern

### Pros (Преимущества)


1. **Separation of Concerns** - Separates business logic from auxiliary responsibilities
2. **Performance optimization** - Lazy initialization and caching improve performance
3. **Access control** - Can control and validate access to objects
4. **Transparent to client** - Client doesn't need to know about the proxy
5. **Open/Closed Principle** - Can add new proxies without changing existing code

### Cons (Недостатки)


1. **Additional complexity** - Extra layer of indirection
2. **Performance overhead** - Slight performance cost from indirection
3. **Design complexity** - Requires good understanding of use case
4. **Testing overhead** - More components to test
5. **Memory concerns** - Caching proxies can cause memory issues if not managed properly


---

## Related Questions

### Hub
- [[q-design-patterns-types--design-patterns--medium]] - Design pattern categories overview

### Structural Patterns
- [[q-adapter-pattern--design-patterns--medium]] - Adapter pattern
- [[q-decorator-pattern--design-patterns--medium]] - Decorator pattern
- [[q-facade-pattern--design-patterns--medium]] - Facade pattern
- [[q-composite-pattern--design-patterns--medium]] - Composite pattern

### Creational Patterns
- [[q-factory-method-pattern--design-patterns--medium]] - Factory Method pattern

### Behavioral Patterns
- [[q-strategy-pattern--design-patterns--medium]] - Strategy pattern

