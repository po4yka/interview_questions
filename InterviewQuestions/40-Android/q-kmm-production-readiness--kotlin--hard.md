---
id: 20251012-12271121
title: "KMM Production Readiness / Готовность KMM к production"
aliases: ["KMM Production Readiness", "Готовность KMM к production"]
topic: kotlin
subtopics: [kmp]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-13
updated: 2025-10-28
sources: []
tags: [kotlin, kmp, production, best-practices, difficulty/hard]
moc: moc-kotlin
related: [q-handler-looper-comprehensive--android--medium, q-intent-filters-android--android--medium, q-what-is-layout-types-and-when-to-use--android--easy]
date created: Tuesday, October 28th 2025, 9:23:20 pm
date modified: Thursday, October 30th 2025, 3:11:49 pm
---

# Вопрос (RU)

> Каковы ключевые соображения для вывода KMM проекта в production? Как обрабатывать versioning, binary compatibility, crash reporting и performance monitoring на разных платформах? Каковы частые ошибки и как их избегать?

# Question (EN)

> What are the key considerations for taking a KMM project to production? How do you handle versioning, binary compatibility, crash reporting, and performance monitoring across platforms? What are common pitfalls and how do you avoid them?

---

## Ответ (RU)

Production-ready KMM требует тщательного внимания к стабильности, мониторингу, версионированию и платформенной специфике при сохранении преимуществ code sharing.

### Binary Compatibility и Versioning

**Framework Versioning**:

```kotlin
// shared/build.gradle.kts
kotlin {
    iosArm64 {
        binaries.framework {
            baseName = "Shared"
            version = "1.2.3"
            isStatic = true  // ✅ Рекомендуется для production

            export("org.jetbrains.kotlinx:kotlinx-datetime")
            export("io.ktor:ktor-client-core")
        }
    }
}
```

**API Compatibility**:

```kotlin
class TaskRepository {
    // ❌ Старый метод - deprecated, но не удален
    @Deprecated("Use getTasks()", ReplaceWith("getTasks()"))
    suspend fun fetchTasks(): List<Task> = getTasks().getOrThrow()

    // ✅ Новый метод возвращает Result
    suspend fun getTasks(): Result<List<Task>> {
        return try {
            Result.success(api.fetchTasks())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Crash Reporting

**Unified Interface**:

```kotlin
// commonMain
interface CrashReporter {
    fun logException(exception: Throwable, context: Map<String, String> = emptyMap())
    fun setUserId(userId: String)
}

expect class CrashReporterFactory {
    fun create(): CrashReporter
}

// androidMain - Firebase Crashlytics
actual class CrashReporterFactory {
    actual fun create(): CrashReporter = FirebaseCrashReporter(
        FirebaseCrashlytics.getInstance()
    )
}

class FirebaseCrashReporter(
    private val crashlytics: FirebaseCrashlytics
) : CrashReporter {
    override fun logException(exception: Throwable, context: Map<String, String>) {
        context.forEach { (k, v) -> crashlytics.setCustomKey(k, v) }
        crashlytics.recordException(exception)
    }

    override fun setUserId(userId: String) {
        crashlytics.setUserId(userId)
    }
}
```

**Global Exception Handler**:

```kotlin
class GlobalExceptionHandler(private val crashReporter: CrashReporter) {
    fun handleException(exception: Throwable, context: String = "") {
        crashReporter.logException(
            exception,
            mapOf(
                "context" to context,
                "timestamp" to Clock.System.now().toString(),
                "platform" to getPlatform().name
            )
        )
    }
}
```

### Performance Monitoring

```kotlin
interface PerformanceMonitor {
    fun startTrace(name: String): Trace
    fun recordMetric(name: String, value: Long, attrs: Map<String, String>)
}

interface Trace {
    fun putAttribute(key: String, value: String)
    fun stop()
}

// Usage
class TaskRepository(
    private val api: TaskApi,
    private val perfMonitor: PerformanceMonitor
) {
    suspend fun getTasks(): Result<List<Task>> {
        val trace = perfMonitor.startTrace("get_tasks")

        return try {
            val tasks = api.fetchTasks()
            trace.putAttribute("task_count", tasks.size.toString())
            Result.success(tasks)
        } catch (e: Exception) {
            trace.putAttribute("error", e.message ?: "unknown")
            Result.failure(e)
        } finally {
            trace.stop()
        }
    }
}
```

### Thread Safety (iOS)

**New Memory Model** (Kotlin 1.7.20+):

```kotlin
class ThreadSafeRepository {
    // ✅ StateFlow thread-safe с новой моделью памяти
    private val _tasks = MutableStateFlow<List<Task>>(emptyList())
    val tasks: StateFlow<List<Task>> = _tasks.asStateFlow()

    // ✅ AtomicReference для thread-safe updates
    private val cachedData = AtomicReference<CachedData?>(null)
}
```

**Background Safety**:

```kotlin
class TaskDatabaseImpl(
    private val database: TaskDatabase,
    private val dispatcher: CoroutineDispatcher
) : TaskDatabase {
    override suspend fun getAllTasks(): List<Task> = withContext(dispatcher) {
        database.taskQueries.selectAll().executeAsList()
    }
}
```

### Частые Ошибки

**1. Shared Mutable State**:

```kotlin
// ❌ Mutable shared state - не thread-safe
object GlobalState {
    var currentUser: User? = null
    val tasks = mutableListOf<Task>()
}

// ✅ Immutable state с flows
class AppState {
    private val _currentUser = MutableStateFlow<User?>(null)
    val currentUser: StateFlow<User?> = _currentUser.asStateFlow()
}
```

**2. Swallowing Exceptions**:

```kotlin
// ❌ Молча проглатывает ошибки
suspend fun getTasks(): List<Task> {
    return try {
        api.fetchTasks()
    } catch (e: Exception) {
        emptyList()  // Silently fails
    }
}

// ✅ Правильная обработка ошибок
suspend fun getTasks(): Result<List<Task>> {
    return try {
        Result.success(api.fetchTasks())
    } catch (e: Exception) {
        crashReporter.logException(e)
        Result.failure(e)
    }
}
```

**3. Resource Cleanup**:

```kotlin
// ❌ Нет cleanup
class ViewModel {
    private val scope = CoroutineScope(Dispatchers.Main)
    fun loadData() {
        scope.launch { /* ... */ }
    }
}

// ✅ Правильный lifecycle management
class ViewModel {
    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())

    fun onCleared() {
        scope.cancel()  // ✅ Отменяем все корутины
    }
}
```

**4. Excessive Platform Calls**:

```kotlin
// ❌ Частые platform calls
fun processItems(items: List<Item>) {
    items.forEach { item ->
        platformSpecificLogging(item.id)  // Called 1000 times
    }
}

// ✅ Batch platform calls
fun processItems(items: List<Item>) {
    val itemIds = items.map { it.id }
    platformSpecificLogging(itemIds.joinToString())  // Called once
}
```

### Резюме

**Production KMM требует**:
- **Versioning**: Semantic versioning, binary compatibility, API deprecation
- **Crash Reporting**: Unified interface, Firebase Crashlytics, context logging
- **Performance**: Monitoring traces, metrics, network tracing
- **Memory**: Leak detection, proper cleanup, thread safety
- **Testing**: Automated CI/CD, comprehensive coverage

**Избегайте**: shared mutable state, swallowed exceptions, memory leaks, excessive platform calls, отсутствие cleanup.

---

## Answer (EN)

Production-ready KMM requires careful attention to stability, monitoring, versioning, and platform-specific concerns while maintaining code sharing benefits.

### Binary Compatibility and Versioning

**Framework Versioning**:

```kotlin
// shared/build.gradle.kts
kotlin {
    iosArm64 {
        binaries.framework {
            baseName = "Shared"
            version = "1.2.3"
            isStatic = true  // ✅ Recommended for production

            export("org.jetbrains.kotlinx:kotlinx-datetime")
            export("io.ktor:ktor-client-core")
        }
    }
}
```

**API Compatibility**:

```kotlin
class TaskRepository {
    // ❌ Old method - deprecated but not removed
    @Deprecated("Use getTasks()", ReplaceWith("getTasks()"))
    suspend fun fetchTasks(): List<Task> = getTasks().getOrThrow()

    // ✅ New method returns Result
    suspend fun getTasks(): Result<List<Task>> {
        return try {
            Result.success(api.fetchTasks())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Crash Reporting

**Unified Interface**:

```kotlin
// commonMain
interface CrashReporter {
    fun logException(exception: Throwable, context: Map<String, String> = emptyMap())
    fun setUserId(userId: String)
}

expect class CrashReporterFactory {
    fun create(): CrashReporter
}

// androidMain - Firebase Crashlytics
actual class CrashReporterFactory {
    actual fun create(): CrashReporter = FirebaseCrashReporter(
        FirebaseCrashlytics.getInstance()
    )
}

class FirebaseCrashReporter(
    private val crashlytics: FirebaseCrashlytics
) : CrashReporter {
    override fun logException(exception: Throwable, context: Map<String, String>) {
        context.forEach { (k, v) -> crashlytics.setCustomKey(k, v) }
        crashlytics.recordException(exception)
    }

    override fun setUserId(userId: String) {
        crashlytics.setUserId(userId)
    }
}
```

**Global Exception Handler**:

```kotlin
class GlobalExceptionHandler(private val crashReporter: CrashReporter) {
    fun handleException(exception: Throwable, context: String = "") {
        crashReporter.logException(
            exception,
            mapOf(
                "context" to context,
                "timestamp" to Clock.System.now().toString(),
                "platform" to getPlatform().name
            )
        )
    }
}
```

### Performance Monitoring

```kotlin
interface PerformanceMonitor {
    fun startTrace(name: String): Trace
    fun recordMetric(name: String, value: Long, attrs: Map<String, String>)
}

interface Trace {
    fun putAttribute(key: String, value: String)
    fun stop()
}

// Usage
class TaskRepository(
    private val api: TaskApi,
    private val perfMonitor: PerformanceMonitor
) {
    suspend fun getTasks(): Result<List<Task>> {
        val trace = perfMonitor.startTrace("get_tasks")

        return try {
            val tasks = api.fetchTasks()
            trace.putAttribute("task_count", tasks.size.toString())
            Result.success(tasks)
        } catch (e: Exception) {
            trace.putAttribute("error", e.message ?: "unknown")
            Result.failure(e)
        } finally {
            trace.stop()
        }
    }
}
```

### Thread Safety (iOS)

**New Memory Model** (Kotlin 1.7.20+):

```kotlin
class ThreadSafeRepository {
    // ✅ StateFlow is thread-safe with new memory model
    private val _tasks = MutableStateFlow<List<Task>>(emptyList())
    val tasks: StateFlow<List<Task>> = _tasks.asStateFlow()

    // ✅ AtomicReference for thread-safe updates
    private val cachedData = AtomicReference<CachedData?>(null)
}
```

**Background Safety**:

```kotlin
class TaskDatabaseImpl(
    private val database: TaskDatabase,
    private val dispatcher: CoroutineDispatcher
) : TaskDatabase {
    override suspend fun getAllTasks(): List<Task> = withContext(dispatcher) {
        database.taskQueries.selectAll().executeAsList()
    }
}
```

### Common Pitfalls

**1. Shared Mutable State**:

```kotlin
// ❌ Mutable shared state - not thread-safe
object GlobalState {
    var currentUser: User? = null
    val tasks = mutableListOf<Task>()
}

// ✅ Immutable state with flows
class AppState {
    private val _currentUser = MutableStateFlow<User?>(null)
    val currentUser: StateFlow<User?> = _currentUser.asStateFlow()
}
```

**2. Swallowing Exceptions**:

```kotlin
// ❌ Silently fails
suspend fun getTasks(): List<Task> {
    return try {
        api.fetchTasks()
    } catch (e: Exception) {
        emptyList()  // Silently fails
    }
}

// ✅ Proper error handling
suspend fun getTasks(): Result<List<Task>> {
    return try {
        Result.success(api.fetchTasks())
    } catch (e: Exception) {
        crashReporter.logException(e)
        Result.failure(e)
    }
}
```

**3. Resource Cleanup**:

```kotlin
// ❌ No cleanup
class ViewModel {
    private val scope = CoroutineScope(Dispatchers.Main)
    fun loadData() {
        scope.launch { /* ... */ }
    }
}

// ✅ Proper lifecycle management
class ViewModel {
    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())

    fun onCleared() {
        scope.cancel()  // ✅ Cancel all coroutines
    }
}
```

**4. Excessive Platform Calls**:

```kotlin
// ❌ Frequent platform calls
fun processItems(items: List<Item>) {
    items.forEach { item ->
        platformSpecificLogging(item.id)  // Called 1000 times
    }
}

// ✅ Batch platform calls
fun processItems(items: List<Item>) {
    val itemIds = items.map { it.id }
    platformSpecificLogging(itemIds.joinToString())  // Called once
}
```

### Summary

**Production KMM requires**:
- **Versioning**: Semantic versioning, binary compatibility, API deprecation
- **Crash Reporting**: Unified interface, Firebase Crashlytics, context logging
- **Performance**: Monitoring traces, metrics, network tracing
- **Memory**: Leak detection, proper cleanup, thread safety
- **Testing**: Automated CI/CD, comprehensive coverage

**Avoid**: shared mutable state, swallowed exceptions, memory leaks, excessive platform calls, missing cleanup.

---

## Follow-ups

- How do you handle KMM dependency conflicts between Android and iOS platforms?
- What strategies ensure smooth KMM framework updates without breaking existing apps?
- How do you implement A/B testing in shared KMM code while maintaining platform independence?
- What are the trade-offs between static and dynamic framework linking in iOS?
- How do you profile and optimize memory usage in shared KMM code across platforms?

## References

- [[c-coroutines]]
- [[c-kotlin-multiplatform]]
- https://kotlinlang.org/docs/multiplatform-mobile-getting-started.html
- https://kotlinlang.org/docs/native-memory-manager.html

## Related Questions

### Prerequisites
- [[q-coroutine-basics--kotlin--easy]] - Understanding coroutines fundamentals
- [[q-what-is-viewmodel--android--medium]] - Lifecycle management patterns

### Related
- [[q-handler-looper-comprehensive--android--medium]] - Threading concepts
- [[q-intent-filters-android--android--medium]] - Android platform specifics

### Advanced
- [[q-what-is-layout-types-and-when-to-use--android--easy]] - Platform UI integration
