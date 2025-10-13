---
topic: kotlin
subtopics: [kmp]
tags:
  - Android
  - Kotlin
  - KMM
  - Production
  - BestPractices
difficulty: hard
status: draft
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-kotlin
related_questions: []
---

# KMM Production Readiness and Best Practices

# Question (EN)
> 
What are the key considerations for taking a KMM project to production? How do you handle versioning, binary compatibility, crash reporting, and performance monitoring across platforms? What are common pitfalls and how do you avoid them?

## Answer (EN)
Production-ready KMM requires careful attention to stability, monitoring, versioning, and platform-specific concerns while maintaining the benefits of code sharing. Success depends on proper tooling, testing, and operational practices.

#### Binary Compatibility and Versioning

**1. Framework Versioning**
```kotlin
// shared/build.gradle.kts
kotlin {
    iosArm64 {
        binaries.framework {
            baseName = "Shared"

            // Semantic versioning
            version = "1.2.3"

            // Static framework (recommended for production)
            isStatic = true

            // Export dependencies to iOS
            export("org.jetbrains.kotlinx:kotlinx-datetime:0.5.0")
            export("io.ktor:ktor-client-core:2.3.7")

            // Freeze all exported objects for thread safety
            freeCompilerArgs += "-Xfreeze-by-default"
        }
    }
}

// CocoaPods versioning
cocoapods {
    version = "1.2.3"
    summary = "Shared business logic"
    homepage = "https://github.com/company/app"

    ios.deploymentTarget = "14.0"

    framework {
        baseName = "Shared"
        isStatic = true

        // Transitivity control
        transitiveExport = false
    }

    // Specify pod version for iOS dependencies
    pod("Alamofire") {
        version = "~> 5.8"
    }
}
```

**2. API Compatibility**
```kotlin
// Maintain backward compatibility
class TaskRepository {
    // Old method - deprecated but not removed
    @Deprecated(
        message = "Use getTasks() instead",
        replaceWith = ReplaceWith("getTasks()"),
        level = DeprecationLevel.WARNING
    )
    suspend fun fetchTasks(): List<Task> {
        return getTasks().getOrThrow()
    }

    // New method returning Result
    suspend fun getTasks(): Result<List<Task>> {
        return try {
            val tasks = api.fetchTasks()
            Result.success(tasks)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

// Version-based feature flags
object FeatureFlags {
    private const val SHARED_VERSION = "1.2.3"

    val isNewApiEnabled: Boolean
        get() = SHARED_VERSION >= "1.2.0"

    val isExperimentalFeatureEnabled: Boolean
        get() = SHARED_VERSION >= "1.3.0"
}
```

**3. Breaking Changes Migration**
```kotlin
// V1 - Old API
class TaskRepositoryV1 {
    suspend fun getTasks(): List<Task> { /* ... */ }
}

// V2 - New API with Result wrapper
class TaskRepositoryV2 {
    suspend fun getTasks(): Result<List<Task>> { /* ... */ }
}

// Compatibility layer during migration period
class TaskRepositoryCompat {
    private val v2Repository = TaskRepositoryV2()

    // Provide both APIs during transition
    @Deprecated("Use getTasksV2() returning Result")
    suspend fun getTasks(): List<Task> {
        return v2Repository.getTasks().getOrThrow()
    }

    suspend fun getTasksV2(): Result<List<Task>> {
        return v2Repository.getTasks()
    }
}
```

#### Crash Reporting

**1. Unified Crash Reporting**
```kotlin
// commonMain/monitoring/CrashReporter.kt
interface CrashReporter {
    fun logException(exception: Throwable, context: Map<String, String> = emptyMap())
    fun logMessage(message: String, level: LogLevel)
    fun setUserId(userId: String)
    fun setCustomKey(key: String, value: String)
}

enum class LogLevel {
    DEBUG, INFO, WARNING, ERROR, FATAL
}

expect class CrashReporterFactory {
    fun create(): CrashReporter
}

// androidMain - Firebase Crashlytics
actual class CrashReporterFactory {
    actual fun create(): CrashReporter {
        return FirebaseCrashReporter(
            FirebaseCrashlytics.getInstance()
        )
    }
}

class FirebaseCrashReporter(
    private val crashlytics: FirebaseCrashlytics
) : CrashReporter {
    override fun logException(exception: Throwable, context: Map<String, String>) {
        context.forEach { (key, value) ->
            crashlytics.setCustomKey(key, value)
        }
        crashlytics.recordException(exception)
    }

    override fun logMessage(message: String, level: LogLevel) {
        crashlytics.log("${level.name}: $message")
    }

    override fun setUserId(userId: String) {
        crashlytics.setUserId(userId)
    }

    override fun setCustomKey(key: String, value: String) {
        crashlytics.setCustomKey(key, value)
    }
}

// iosMain - Firebase Crashlytics
actual class CrashReporterFactory {
    actual fun create(): CrashReporter {
        return IOSCrashReporter()
    }
}

class IOSCrashReporter : CrashReporter {
    override fun logException(exception: Throwable, context: Map<String, String>) {
        // Log to Firebase Crashlytics iOS
        context.forEach { (key, value) ->
            Crashlytics.crashlytics().setCustomValue(value, forKey: key)
        }

        Crashlytics.crashlytics().record(
            error: NSError(
                domain: "SharedError",
                code: 0,
                userInfo: mapOf(
                    NSLocalizedDescriptionKey to exception.message
                )
            )
        )
    }

    override fun logMessage(message: String, level: LogLevel) {
        Crashlytics.crashlytics().log(message)
    }

    override fun setUserId(userId: String) {
        Crashlytics.crashlytics().setUserID(userId)
    }

    override fun setCustomKey(key: String, value: String) {
        Crashlytics.crashlytics().setCustomValue(value, forKey: key)
    }
}
```

**2. Global Exception Handler**
```kotlin
// commonMain/monitoring/GlobalExceptionHandler.kt
class GlobalExceptionHandler(
    private val crashReporter: CrashReporter
) {
    fun handleException(exception: Throwable, context: String = "") {
        crashReporter.logException(
            exception = exception,
            context = mapOf(
                "context" to context,
                "timestamp" to Clock.System.now().toString(),
                "platform" to getPlatform().name
            )
        )

        // Log to console as well
        Logger.e("GlobalExceptionHandler", "Unhandled exception in $context", exception)
    }
}

// Usage in repository
class TaskRepositoryImpl(
    private val api: TaskApi,
    private val database: TaskDatabase,
    private val exceptionHandler: GlobalExceptionHandler
) : TaskRepository {
    override suspend fun getTasks(): Result<List<Task>> {
        return try {
            val tasks = api.fetchTasks()
            Result.success(tasks)
        } catch (e: Exception) {
            exceptionHandler.handleException(e, "TaskRepository.getTasks")
            Result.failure(e)
        }
    }
}
```

#### Performance Monitoring

**1. Performance Metrics**
```kotlin
// commonMain/monitoring/PerformanceMonitor.kt
interface PerformanceMonitor {
    fun startTrace(name: String): Trace
    fun recordMetric(name: String, value: Long, attributes: Map<String, String> = emptyMap())
}

interface Trace {
    fun putAttribute(key: String, value: String)
    fun incrementMetric(name: String, incrementBy: Long = 1)
    fun stop()
}

expect class PerformanceMonitorFactory {
    fun create(): PerformanceMonitor
}

// androidMain - Firebase Performance
actual class PerformanceMonitorFactory {
    actual fun create(): PerformanceMonitor {
        return FirebasePerformanceMonitor(
            FirebasePerformance.getInstance()
        )
    }
}

class FirebasePerformanceMonitor(
    private val performance: FirebasePerformance
) : PerformanceMonitor {
    override fun startTrace(name: String): Trace {
        val trace = performance.newTrace(name)
        trace.start()
        return FirebaseTraceWrapper(trace)
    }

    override fun recordMetric(
        name: String,
        value: Long,
        attributes: Map<String, String>
    ) {
        val trace = performance.newTrace(name)
        attributes.forEach { (key, value) ->
            trace.putAttribute(key, value)
        }
        trace.incrementMetric(name, value)
    }
}

class FirebaseTraceWrapper(
    private val trace: com.google.firebase.perf.metrics.Trace
) : Trace {
    override fun putAttribute(key: String, value: String) {
        trace.putAttribute(key, value)
    }

    override fun incrementMetric(name: String, incrementBy: Long) {
        trace.incrementMetric(name, incrementBy)
    }

    override fun stop() {
        trace.stop()
    }
}

// Usage
class TaskRepository(
    private val api: TaskApi,
    private val performanceMonitor: PerformanceMonitor
) {
    suspend fun getTasks(): Result<List<Task>> {
        val trace = performanceMonitor.startTrace("get_tasks")

        return try {
            val startTime = currentTimeMillis()
            val tasks = api.fetchTasks()
            val duration = currentTimeMillis() - startTime

            trace.putAttribute("task_count", tasks.size.toString())
            trace.incrementMetric("tasks_fetched", tasks.size.toLong())

            performanceMonitor.recordMetric(
                name = "api_call_duration",
                value = duration,
                attributes = mapOf(
                    "endpoint" to "tasks",
                    "status" to "success"
                )
            )

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

**2. Network Performance**
```kotlin
// Ktor interceptor for performance monitoring
class PerformanceInterceptor(
    private val performanceMonitor: PerformanceMonitor
) {
    fun install(client: HttpClient) {
        client.plugin(HttpSend).intercept { request ->
            val endpoint = request.url.encodedPath
            val trace = performanceMonitor.startTrace("api_$endpoint")

            trace.putAttribute("method", request.method.value)
            trace.putAttribute("url", request.url.toString())

            val startTime = currentTimeMillis()

            val response = try {
                execute(request)
            } catch (e: Exception) {
                trace.putAttribute("error", e.message ?: "unknown")
                trace.stop()
                throw e
            }

            val duration = currentTimeMillis() - startTime

            trace.putAttribute("status_code", response.status.value.toString())
            trace.incrementMetric("response_size", response.contentLength() ?: 0)

            performanceMonitor.recordMetric(
                name = "network_request_duration",
                value = duration,
                attributes = mapOf(
                    "endpoint" to endpoint,
                    "status" to response.status.value.toString()
                )
            )

            trace.stop()
            response
        }
    }
}
```

#### Memory Management

**1. Memory Leak Detection**
```kotlin
// iOS - Monitor for retain cycles
class MemoryLeakDetector {
    private val allocatedObjects = mutableSetOf<WeakReference<Any>>()

    fun trackObject(obj: Any) {
        allocatedObjects.add(WeakReference(obj))
    }

    fun checkForLeaks(): List<String> {
        val leaks = mutableListOf<String>()

        allocatedObjects.removeIf { ref ->
            ref.get() == null // Remove deallocated objects
        }

        // Objects that should have been deallocated but weren't
        allocatedObjects.forEach { ref ->
            ref.get()?.let { obj ->
                leaks.add("Potential leak: ${obj::class.simpleName}")
            }
        }

        return leaks
    }
}

// Usage in ViewModel
class TaskListViewModel(/* dependencies */) {
    init {
        if (isDebug()) {
            MemoryLeakDetector.shared.trackObject(this)
        }
    }

    fun onCleared() {
        viewModelScope.cancel()

        // Check for leaks in debug builds
        if (isDebug()) {
            val leaks = MemoryLeakDetector.shared.checkForLeaks()
            if (leaks.isNotEmpty()) {
                Logger.w("MemoryLeakDetector", "Detected leaks: $leaks")
            }
        }
    }
}
```

**2. Memory Optimization**
```kotlin
// Use appropriate data structures
class TaskCache {
    // WeakReference for cache to allow GC
    private val cache = mutableMapOf<String, WeakReference<Task>>()

    fun put(task: Task) {
        cache[task.id] = WeakReference(task)
    }

    fun get(id: String): Task? {
        return cache[id]?.get()
    }

    fun clear() {
        cache.clear()
    }
}

// Limit collection sizes
class RecentTasksManager {
    private val maxRecentTasks = 100

    private val recentTasks = mutableListOf<Task>()

    fun addTask(task: Task) {
        recentTasks.add(0, task)

        // Trim to max size
        if (recentTasks.size > maxRecentTasks) {
            recentTasks.subList(maxRecentTasks, recentTasks.size).clear()
        }
    }
}
```

#### Thread Safety (iOS)

**1. Freezing and New Memory Model**
```kotlin
// shared/build.gradle.kts
kotlin {
    iosArm64 {
        binaries.framework {
            // New memory model (Kotlin 1.7.20+)
            // No manual freezing required

            freeCompilerArgs += listOf(
                "-Xbinary=bundleId=com.example.shared"
            )
        }
    }
}

// Thread-safe shared state
class ThreadSafeRepository {
    // StateFlow is thread-safe with new memory model
    private val _tasks = MutableStateFlow<List<Task>>(emptyList())
    val tasks: StateFlow<List<Task>> = _tasks.asStateFlow()

    // AtomicReference for thread-safe updates
    private val cachedData = AtomicReference<CachedData?>(null)

    fun updateCache(data: CachedData) {
        cachedData.value = data
    }
}
```

**2. Background Thread Safety**
```kotlin
// Ensure database operations are thread-safe
class TaskDatabaseImpl(
    private val database: TaskDatabase,
    private val dispatcher: CoroutineDispatcher
) : TaskDatabase {
    override suspend fun getAllTasks(): List<Task> = withContext(dispatcher) {
        database.taskQueries.selectAll().executeAsList()
    }

    override suspend fun insertTask(task: Task) = withContext(dispatcher) {
        database.taskQueries.insertTask(task)
    }
}
```

#### Common Production Pitfalls

**1. Avoid Shared Mutable State**
```kotlin
//  Bad - Mutable shared state
object GlobalState {
    var currentUser: User? = null  // Not thread-safe
    val tasks = mutableListOf<Task>()  // Not thread-safe
}

//  Good - Immutable state with flows
class AppState {
    private val _currentUser = MutableStateFlow<User?>(null)
    val currentUser: StateFlow<User?> = _currentUser.asStateFlow()

    private val _tasks = MutableStateFlow<List<Task>>(emptyList())
    val tasks: StateFlow<List<Task>> = _tasks.asStateFlow()

    fun setUser(user: User?) {
        _currentUser.value = user
    }

    fun setTasks(tasks: List<Task>) {
        _tasks.value = tasks
    }
}
```

**2. Proper Error Handling**
```kotlin
//  Bad - Swallowing exceptions
suspend fun getTasks(): List<Task> {
    return try {
        api.fetchTasks()
    } catch (e: Exception) {
        emptyList()  // Silently fails
    }
}

//  Good - Propagate errors properly
suspend fun getTasks(): Result<List<Task>> {
    return try {
        val tasks = api.fetchTasks()
        Result.success(tasks)
    } catch (e: Exception) {
        crashReporter.logException(e)
        Result.failure(e)
    }
}
```

**3. Resource Cleanup**
```kotlin
//  Bad - No cleanup
class ViewModel {
    private val scope = CoroutineScope(Dispatchers.Main)

    fun loadData() {
        scope.launch {
            // Launch coroutine but never cancel
        }
    }
}

//  Good - Proper lifecycle management
class ViewModel {
    private val scope = CoroutineScope(
        Dispatchers.Main + SupervisorJob()
    )

    fun loadData() {
        scope.launch {
            // Coroutine work
        }
    }

    fun onCleared() {
        scope.cancel()  // Cancel all coroutines
    }
}
```

**4. Platform-Specific Optimizations**
```kotlin
// Avoid excessive JNI calls on Android
// or Objective-C interop on iOS

//  Bad - Frequent platform calls
fun processItems(items: List<Item>) {
    items.forEach { item ->
        platformSpecificLogging(item.id)  // Called 1000 times
    }
}

//  Good - Batch platform calls
fun processItems(items: List<Item>) {
    val itemIds = items.map { it.id }
    platformSpecificLogging(itemIds.joinToString())  // Called once
}
```

#### CI/CD for Production

**1. Automated Testing**
```yaml
# .github/workflows/kmm-ci.yml
name: KMM CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: macos-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Run shared tests
        run: ./gradlew shared:allTests

      - name: Run Android tests
        run: ./gradlew androidApp:testDebugUnitTest

      - name: Build iOS framework
        run: ./gradlew shared:linkDebugFrameworkIosSimulatorArm64

      - name: Run iOS tests
        run: xcodebuild test -workspace iosApp/iosApp.xcworkspace \
          -scheme iosApp -destination 'platform=iOS Simulator,name=iPhone 15'

      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: '**/build/test-results/**/*.xml'
```

**2. Version Management**
```kotlin
// buildSrc/src/main/kotlin/Versions.kt
object Versions {
    const val kotlin = "1.9.21"
    const val shared = "1.2.3"

    object Android {
        const val compileSdk = 34
        const val minSdk = 24
        const val targetSdk = 34
        const val versionCode = 10203  // 1.2.3 -> 10203
        const val versionName = shared
    }

    object IOS {
        const val deploymentTarget = "14.0"
        const val versionString = shared
        const val buildNumber = "123"
    }
}
```

#### Monitoring Dashboard

```kotlin
// Production metrics collection
class ProductionMetrics(
    private val crashReporter: CrashReporter,
    private val performanceMonitor: PerformanceMonitor,
    private val analytics: Analytics
) {
    fun trackAppLaunch() {
        val trace = performanceMonitor.startTrace("app_launch")

        analytics.logEvent("app_launch") {
            param("platform", getPlatform().name)
            param("version", BuildConfig.VERSION_NAME)
            param("timestamp", Clock.System.now().toString())
        }

        trace.stop()
    }

    fun trackFeatureUsage(feature: String, success: Boolean) {
        analytics.logEvent("feature_usage") {
            param("feature", feature)
            param("success", success)
            param("platform", getPlatform().name)
        }

        if (!success) {
            crashReporter.logMessage(
                "Feature failed: $feature",
                LogLevel.WARNING
            )
        }
    }

    fun trackNetworkRequest(
        endpoint: String,
        duration: Long,
        success: Boolean
    ) {
        performanceMonitor.recordMetric(
            name = "network_request",
            value = duration,
            attributes = mapOf(
                "endpoint" to endpoint,
                "success" to success.toString(),
                "platform" to getPlatform().name
            )
        )
    }
}
```

### Summary

Production-ready KMM requires:
- **Versioning**: Semantic versioning, binary compatibility
- **Crash Reporting**: Unified crash reporting across platforms
- **Performance**: Monitoring traces, metrics, optimization
- **Memory**: Leak detection, proper cleanup, thread safety
- **Testing**: Automated CI/CD, comprehensive test coverage
- **Monitoring**: Analytics, performance dashboards

**Common Pitfalls to Avoid**:
- Shared mutable state
- Swallowing exceptions
- Memory leaks
- Excessive platform calls
- No resource cleanup
- Missing crash reports

Key considerations: stability, observability, proper error handling, memory management, and continuous monitoring in production.

---

# Вопрос (RU)
> 
Каковы ключевые соображения для вывода KMM проекта в production? Как обрабатывать versioning, binary compatibility, crash reporting и performance monitoring на разных платформах? Каковы частые ошибки и как их избегать?

## Ответ (RU)
Production-ready KMM требует тщательного внимания к stability, monitoring, versioning и platform-specific concerns при сохранении преимуществ code sharing.

#### Ключевые аспекты

**Versioning**:
- Semantic versioning (1.2.3)
- Binary compatibility
- API deprecation strategy
- Breaking changes migration

**Crash Reporting**:
- Unified interface
- Firebase Crashlytics (Android + iOS)
- Context logging
- User identification

**Performance Monitoring**:
- Firebase Performance
- Custom metrics
- Network tracing
- Database profiling

**Memory Management**:
- Leak detection
- Proper cleanup
- WeakReferences
- Collection size limits

#### Thread Safety (iOS)

**New Memory Model**:
- Kotlin 1.7.20+
- No manual freezing
- StateFlow thread-safe
- AtomicReference

**Background Safety**:
- withContext для DB operations
- CoroutineDispatcher isolation
- Proper scope management

#### Частые ошибки

1. **Shared Mutable State**:
   -  var в object
   -  StateFlow

2. **Swallowing Exceptions**:
   -  catch { return null }
   -  Result<T> + crash reporting

3. **Memory Leaks**:
   -  No scope.cancel()
   -  Lifecycle-aware cleanup

4. **Excessive Platform Calls**:
   -  Loop с platform call
   -  Batch operations

#### CI/CD

**Automated Testing**:
- shared:allTests
- Android unit tests
- iOS framework build
- iOS simulator tests

**Versioning**:
- Centralized version management
- Consistent across platforms
- Automated bumping

#### Monitoring

**Metrics**:
- App launch time
- Feature usage
- Network performance
- Crash-free rate
- Memory usage

**Dashboards**:
- Firebase Console
- Custom analytics
- Platform-specific metrics

### Резюме

Production KMM требует:
- **Versioning**: Semantic versioning, compatibility
- **Crash Reporting**: Unified across platforms
- **Performance**: Monitoring, optimization
- **Memory**: Leak detection, cleanup
- **Testing**: Automated CI/CD
- **Monitoring**: Analytics, dashboards

Избегайте: shared mutable state, swallowed exceptions, memory leaks, excessive platform calls.

Ключевые моменты: stability, observability, proper error handling, memory management, continuous monitoring.
