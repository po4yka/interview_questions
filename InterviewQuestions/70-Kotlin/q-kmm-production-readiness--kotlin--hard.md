---
id: kotlin-138
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
updated: 2025-11-10
sources: []
tags: [best-practices, difficulty/hard, kmp, kotlin, production]
moc: moc-kotlin
related: [c-kotlin, q-handler-looper-comprehensive--android--medium]
---

# Вопрос (RU)

> Каковы ключевые соображения для вывода KMM проекта в production? Как обрабатывать versioning, binary compatibility, crash reporting и performance monitoring на разных платформах? Каковы частые ошибки и как их избегать?

# Question (EN)

> What are the key considerations for taking a KMM project to production? How do you handle versioning, binary compatibility, crash reporting, and performance monitoring across platforms? What are common pitfalls and how do you avoid them?

## Ответ (RU)

Production-ready KMM требует тщательного внимания к стабильности, мониторингу, версионированию и платформенной специфике при сохранении преимуществ code sharing.

### Binary Compatibility И Versioning

Важно отдельно версионировать общий модуль (shared) и гарантировать стабильность его публичного API для обеих платформ.

**Framework Versioning (iOS)**:

```kotlin
// shared/build.gradle.kts (упрощенный пример)
kotlin {
    iosArm64()
    iosSimulatorArm64()

    ios()

    targets.withType<org.jetbrains.kotlin.gradle.plugin.mpp.KotlinNativeTarget> {
        binaries.framework {
            baseName = "Shared"
            isStatic = true  // ✅ Рекомендуется для production во многих сценариях, уменьшает runtime-issues

            export("org.jetbrains.kotlinx:kotlinx-datetime")
            export("io.ktor:ktor-client-core")
        }
    }
}
```

Версию артефакта (semver) задаём на уровне Gradle/Maven и/или CocoaPods podspec, а не через поле `version` у `framework`. Для production важно:
- использовать семантическое версионирование для общего модуля;
- не ломать бинарную совместимость между минорными/patch-версиями для уже интегрированных iOS фреймворков (не удалять/не менять сигнатуры публичных API без мейджор-версии);
- согласованно обновлять зависимости (Kotlin, Ktor, SQLDelight и т.п.) на обеих платформах.

**API Compatibility**:

```kotlin
class TaskRepository {
    // ❌ Старый метод - deprecated, но не удален (сохраняем для совместимости)
    @Deprecated("Use getTasks()", ReplaceWith("getTasks()"))
    suspend fun fetchTasks(): List<Task> = getTasks().getOrThrow()

    // ✅ Новый метод возвращает Result и лучше моделирует ошибки
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

**Единый интерфейс**:

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

// iosMain должен предоставить свою actual-реализацию (например, Sentry/Firebase/встроенное логирование)
```

**Глобальный обработчик исключений** (пример):

```kotlin
expect fun getPlatformName(): String

class GlobalExceptionHandler(private val crashReporter: CrashReporter) {
    fun handleException(exception: Throwable, context: String = "") {
        crashReporter.logException(
            exception,
            mapOf(
                "context" to context,
                "timestamp" to Clock.System.now().toString(),
                "platform" to getPlatformName()
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

Реализации `PerformanceMonitor` могут быть разными на Android и iOS (Firebase Performance, OSS SDK, собственный трейсинг), но интерфейс остаётся общим.

### Thread Safety (iOS)

**Новая модель памяти** (Kotlin/Native с новым менеджером памяти включён):

```kotlin
class ThreadSafeRepository {
    // ✅ StateFlow thread-safe с новой моделью памяти (при корректном использовании)
    private val _tasks = MutableStateFlow<List<Task>>(emptyList())
    val tasks: StateFlow<List<Task>> = _tasks.asStateFlow()

    // ✅ AtomicReference (из kotlin.concurrent или аналогичных) для безопасных обновлений
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

Важно убедиться, что используемые диспетчеры и базы данных поддерживают многопоточность на iOS с учётом выбранной версии Kotlin/Native.

### Частые Ошибки

**1. Shared Mutable State**:

```kotlin
// ❌ Mutable shared state - не thread-safe
object GlobalState {
    var currentUser: User? = null
    val tasks = mutableListOf<Task>()
}

// ✅ Immutable / observable state с flows
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
- **Versioning**: Семантическое версионирование shared-модуля, контроль бинарной совместимости, аккуратная деприкация API.
- **Crash Reporting**: Единый интерфейс, platform-specific реализации (Firebase Crashlytics, Sentry и т.п.), контекстное логирование.
- **Performance**: Трейсы, метрики, анализ сетевых вызовов.
- **Memory**: Leak detection, корректный cleanup, thread safety с учётом модели памяти Kotlin/Native.
- **Testing**: Автоматизированный CI/CD, покрытие логики на всех целевых платформах.

**Избегайте**: shared mutable state, проглатывания исключений, утечек памяти, чрезмерных platform calls, отсутствия cleanup.

## Answer (EN)

Production-ready KMM requires careful attention to stability, monitoring, versioning, and platform-specific concerns while maintaining code sharing benefits.

### Binary Compatibility and Versioning

You should version the shared module explicitly and guarantee stability of its public API for both platforms.

**Framework Versioning (iOS)**:

```kotlin
// shared/build.gradle.kts (simplified example)
kotlin {
    iosArm64()
    iosSimulatorArm64()

    ios()

    targets.withType<org.jetbrains.kotlin.gradle.plugin.mpp.KotlinNativeTarget> {
        binaries.framework {
            baseName = "Shared"
            isStatic = true  // ✅ Recommended for many production setups; reduces runtime issues

            export("org.jetbrains.kotlinx:kotlinx-datetime")
            export("io.ktor:ktor-client-core")
        }
    }
}
```

The artifact version (semver) is defined at the Gradle/Maven and/or CocoaPods podspec level, not via a `version` property on the framework binary. For production:
- use semantic versioning for the shared module;
- avoid breaking binary compatibility between minor/patch releases for iOS frameworks already integrated (do not remove/change public API signatures without a major version bump);
- keep dependency versions (Kotlin, Ktor, SQLDelight, etc.) aligned across platforms.

**API Compatibility**:

```kotlin
class TaskRepository {
    // ❌ Old method - deprecated but kept for compatibility
    @Deprecated("Use getTasks()", ReplaceWith("getTasks()"))
    suspend fun fetchTasks(): List<Task> = getTasks().getOrThrow()

    // ✅ New method returns Result to model errors explicitly
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

// iosMain should provide its own actual implementation (e.g., Sentry/Firebase/native reporting)
```

**Global Exception Handler** (example):

```kotlin
expect fun getPlatformName(): String

class GlobalExceptionHandler(private val crashReporter: CrashReporter) {
    fun handleException(exception: Throwable, context: String = "") {
        crashReporter.logException(
            exception,
            mapOf(
                "context" to context,
                "timestamp" to Clock.System.now().toString(),
                "platform" to getPlatformName()
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

Concrete `PerformanceMonitor` implementations will differ per platform (Firebase Performance, OSS SDKs, custom tracing), but the shared contract stays common.

### Thread Safety (iOS)

**New Memory Model** (Kotlin/Native with the new memory manager enabled):

```kotlin
class ThreadSafeRepository {
    // ✅ StateFlow is thread-safe with the new memory model (when used correctly)
    private val _tasks = MutableStateFlow<List<Task>>(emptyList())
    val tasks: StateFlow<List<Task>> = _tasks.asStateFlow()

    // ✅ AtomicReference (from kotlin.concurrent or similar) for safe updates
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

Ensure that the chosen dispatchers and database drivers are safe for use with the current Kotlin/Native memory model and threading.

### Common Pitfalls

**1. Shared Mutable State**:

```kotlin
// ❌ Mutable shared state - not thread-safe
object GlobalState {
    var currentUser: User? = null
    val tasks = mutableListOf<Task>()
}

// ✅ Immutable / observable state with flows
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
- **Versioning**: Semantic versioning of the shared module, binary compatibility guarantees, careful API deprecation.
- **Crash Reporting**: Unified interface, platform-specific implementations (Firebase Crashlytics, Sentry, etc.), rich context logging.
- **Performance**: Traces, metrics, network profiling.
- **Memory**: Leak detection, proper cleanup, thread safety aligned with the Kotlin/Native memory model.
- **Testing**: Automated CI/CD and thorough coverage on all target platforms.

**Avoid**: shared mutable state, swallowed exceptions, memory leaks, excessive platform calls, missing cleanup.

## Дополнительные вопросы (RU)

- Как вы обрабатываете конфликты зависимостей KMM между Android и iOS?
- Какие стратегии позволяют обновлять KMM framework без поломки существующих приложений?
- Как реализовать A/B-тестирование в общем KMM-коде при сохранении независимости платформ?
- В чём компромиссы между static и dynamic linking фреймворка на iOS?
- Как профилировать и оптимизировать использование памяти в общем KMM-коде на разных платформах?

## Follow-ups

- How do you handle KMM dependency conflicts between Android and iOS platforms?
- What strategies ensure smooth KMM framework updates without breaking existing apps?
- How do you implement A/B testing in shared KMM code while maintaining platform independence?
- What are the trade-offs between static and dynamic framework linking in iOS?
- How do you profile and optimize memory usage in shared KMM code across platforms?

## Ссылки (RU)

- [[c-coroutines]]
- https://kotlinlang.org/docs/multiplatform-mobile-getting-started.html
- https://kotlinlang.org/docs/native-memory-manager.html

## References

- [[c-coroutines]]
- https://kotlinlang.org/docs/multiplatform-mobile-getting-started.html
- https://kotlinlang.org/docs/native-memory-manager.html

## Related Questions

### Prerequisites
- Понимание основ корутин
- [[q-what-is-viewmodel--android--medium]] - Паттерны управления жизненным циклом

### Related
- [[q-handler-looper-comprehensive--android--medium]] - Threading concepts
- [[q-intent-filters-android--android--medium]] - Android platform specifics

### Advanced
- [[q-what-is-layout-types-and-when-to-use--android--easy]] - Platform UI integration
