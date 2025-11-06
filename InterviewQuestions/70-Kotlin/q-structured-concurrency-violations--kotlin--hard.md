---
id: kotlin-086
title: "Structured concurrency violations and escape hatches / Нарушения структурной параллельности"
aliases: [Anti-Patterns, Escape Hatches, Structured Concurrency Violations, Нарушения параллельности]
topic: kotlin
subtopics: [coroutines, structured-concurrency]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-kotlin-advantages-for-android--kotlin--easy]
created: 2025-10-12
updated: 2025-10-31
tags: [anti-patterns, architecture, best-practices, coroutines, difficulty/hard, kotlin, lifecycle, scope, structured-concurrency, violations]
---

# Structured Concurrency Violations and Escape Hatches / Нарушения Структурной Параллельности

## English

### Overview

Structured concurrency is a core principle of Kotlin coroutines that ensures coroutines are organized in a hierarchy with automatic cancellation, exception propagation, and completion guarantees. Violations of structured concurrency can lead to memory leaks, resource leaks, unhandled exceptions, and difficult-to-debug concurrency issues.

This comprehensive guide explores what structured concurrency is, common violations, when breaking the rules is acceptable (rare), legitimate escape hatches, and tools for detection and enforcement.

### What Is Structured Concurrency?

**Structured concurrency** is a paradigm where:
1. Every coroutine belongs to a scope
2. Child coroutines are tied to parent coroutines
3. Parents wait for all children to complete
4. Cancellation propagates from parent to children
5. Exceptions propagate from children to parent
6. No coroutine outlives its scope

#### The Core Principle

```
Scope
   Parent Coroutine
      Child Coroutine 1
         Grandchild 1.1
         Grandchild 1.2
      Child Coroutine 2
          Grandchild 2.1
   All complete together
```

#### Example: Structured Vs Unstructured

```kotlin
import kotlinx.coroutines.*

fun demonstrateStructured() = runBlocking {
    println("=== Structured Concurrency ===")

    // STRUCTURED: Parent waits for children
    coroutineScope {
        launch {
            delay(1000)
            println("Child 1 done")
        }

        launch {
            delay(500)
            println("Child 2 done")
        }

        println("Parent body done, waiting for children...")
    }

    println("All work completed\n")

    // UNSTRUCTURED: Fire and forget
    println("=== Unstructured (violation) ===")

    GlobalScope.launch {
        delay(1000)
        println("This might never execute!")
    }

    println("Function exits immediately")
    // GlobalScope coroutine might be abandoned!
}
```

**Output:**
```
=== Structured Concurrency ===
Parent body done, waiting for children...
Child 2 done
Child 1 done
All work completed

=== Unstructured (violation) ===
Function exits immediately
(GlobalScope coroutine may never complete)
```

### Benefits of Structured Concurrency

#### 1. Automatic Cancellation

```kotlin
import kotlinx.coroutines.*

class AutomaticCancellationDemo {
    suspend fun structuredWork() = coroutineScope {
        launch {
            repeat(10) {
                delay(100)
                println("Working... $it")
            }
        }

        launch {
            delay(300)
            throw Exception("Something went wrong!")
        }

        // When second coroutine throws, first is automatically cancelled
    }

    fun demonstrateBenefit() = runBlocking {
        try {
            structuredWork()
        } catch (e: Exception) {
            println("Caught: ${e.message}")
            println("All coroutines were automatically cancelled")
        }
    }
}
```

#### 2. Exception Propagation

```kotlin
import kotlinx.coroutines.*

class ExceptionPropagationDemo {
    suspend fun structuredWorkWithException() = coroutineScope {
        val deferred1 = async {
            delay(500)
            "Result 1"
        }

        val deferred2 = async {
            delay(100)
            throw IllegalStateException("Deferred 2 failed")
        }

        // Exception propagates to parent scope
        val result1 = deferred1.await() // Never executes
        val result2 = deferred2.await() // Throws

        "Never returned"
    }

    fun demonstrate() = runBlocking {
        try {
            structuredWorkWithException()
        } catch (e: IllegalStateException) {
            println("Exception properly propagated: ${e.message}")
        }
    }
}
```

#### 3. Completion Guarantees

```kotlin
import kotlinx.coroutines.*

class CompletionGuaranteesDemo {
    suspend fun structuredWorkWithGuarantees() = coroutineScope {
        launch {
            try {
                repeat(10) {
                    delay(100)
                    println("Processing $it")
                }
            } finally {
                println("Cleanup executed")
            }
        }

        delay(300)
        println("Parent completing")
        // Parent waits for child, including finally blocks
    }

    fun demonstrate() = runBlocking {
        structuredWorkWithGuarantees()
        println("Everything completed, including cleanup")
    }
}
```

#### 4. Resource Management

```kotlin
import kotlinx.coroutines.*
import java.io.Closeable

class ResourceManagementDemo {
    class Resource : Closeable {
        init {
            println("Resource opened")
        }

        override fun close() {
            println("Resource closed")
        }
    }

    suspend fun structuredResourceManagement() = coroutineScope {
        val resource = Resource()

        try {
            launch {
                delay(500)
                println("Using resource")
            }

            launch {
                delay(300)
                throw Exception("Error occurred")
            }
        } finally {
            resource.close()
            // Guaranteed to execute even if exception or cancellation
        }
    }

    fun demonstrate() = runBlocking {
        try {
            structuredResourceManagement()
        } catch (e: Exception) {
            println("Caught exception, but resource was closed")
        }
    }
}
```

### Violation #1: GlobalScope (The Worst Offender)

**Why it's bad:**
- No parent scope
- Never cancelled automatically
- No exception propagation
- No completion guarantees
- Memory leak risk

#### The Problem

```kotlin
import kotlinx.coroutines.*

class GlobalScopeViolation {
    fun processData() {
        // VIOLATION: Unstructured coroutine
        GlobalScope.launch {
            val data = loadData()
            processData(data)
            saveResults()
        }

        // Function returns immediately
        // Coroutine might:
        // 1. Never complete
        // 2. Complete after component destroyed
        // 3. Fail silently
        // 4. Leak memory
    }

    private suspend fun loadData(): String {
        delay(1000)
        return "data"
    }

    private fun processData(data: String) {
        println("Processing: $data")
    }

    private fun saveResults() {
        println("Saving results")
    }
}
```

#### Why It Violates Structured Concurrency

```kotlin
import kotlinx.coroutines.*

fun demonstrateGlobalScopeProblems() = runBlocking {
    println("=== GlobalScope Problems ===")

    class Component {
        fun start() {
            println("Component started")

            // PROBLEM 1: No parent
            GlobalScope.launch {
                delay(2000)
                println("This has no parent to cancel it")
            }
        }

        fun stop() {
            println("Component stopped")
            // PROBLEM 2: Coroutine not cancelled
            // Still running in background!
        }
    }

    val component = Component()
    component.start()

    delay(500)
    component.stop()

    // Component stopped, but coroutine still running
    delay(2000)
    println("Coroutine still executed even after component stopped!")
}
```

**Output:**
```
=== GlobalScope Problems ===
Component started
Component stopped
This has no parent to cancel it
Coroutine still executed even after component stopped!
```

#### The Fix

```kotlin
import kotlinx.coroutines.*

class StructuredComponent {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    fun start() {
        println("Component started")

        // GOOD: Structured coroutine
        scope.launch {
            delay(2000)
            println("This will be cancelled properly")
        }
    }

    fun stop() {
        println("Component stopped")
        scope.cancel()
        // All coroutines cancelled!
    }
}

fun demonstrateStructuredFix() = runBlocking {
    val component = StructuredComponent()
    component.start()

    delay(500)
    component.stop()

    delay(2000)
    println("Coroutine was properly cancelled")
}
```

### Violation #2: Creating Job() Without Lifecycle

**The Problem:**

```kotlin
import kotlinx.coroutines.*

class UnmanagedJobViolation {
    // VIOLATION: Scope created but never cancelled
    private val customScope = CoroutineScope(Job() + Dispatchers.Main)

    fun doWork() {
        customScope.launch {
            // Work that might outlive the class
            repeat(100) {
                delay(100)
                println("Working $it")
            }
        }
    }

    // MISSING: fun cleanup() { customScope.cancel() }
}
```

#### Why It's a Violation

1. **No explicit lifecycle** - when does scope end?
2. **No cancellation** - coroutines run forever
3. **Memory leak** - holds references
4. **No parent** - can't be cancelled from outside

#### The Fix: Explicit Lifecycle

```kotlin
import kotlinx.coroutines.*

class ManagedJobComponent {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)

    fun doWork() {
        scope.launch {
            repeat(100) {
                delay(100)
                println("Working $it")
            }
        }
    }

    fun cleanup() {
        // EXPLICIT lifecycle management
        scope.cancel()
        println("All coroutines cancelled")
    }
}

// Usage with explicit lifecycle
fun demonstrateExplicitLifecycle() = runBlocking {
    val component = ManagedJobComponent()

    component.doWork()

    delay(500)

    // Explicitly clean up
    component.cleanup()

    println("Component cleaned up")
}
```

### Violation #3: CoroutineScope() Factory Without Lifecycle

**The Problem:**

```kotlin
import kotlinx.coroutines.*

class FactoryScopeViolation {
    fun processItems(items: List<String>) {
        // VIOLATION: Creates scope without tying to lifecycle
        CoroutineScope(Dispatchers.Default).launch {
            items.forEach { item ->
                delay(1000)
                println("Processing: $item")
            }
        }

        // Scope abandoned immediately!
    }
}
```

#### Why It's Problematic

```kotlin
import kotlinx.coroutines.*

fun demonstrateFactoryProblem() = runBlocking {
    println("=== CoroutineScope() Factory Problem ===")

    fun processData() {
        // Creates scope
        CoroutineScope(Dispatchers.Default).launch {
            repeat(5) {
                delay(500)
                println("Processing $it")
            }
        }

        println("Function returned")
        // Scope reference lost!
        // No way to cancel!
    }

    processData()

    delay(1000)
    println("Want to cancel, but can't - no reference!")

    delay(3000)
    println("Coroutine completed on its own")
}
```

#### The Fix: Pass Scope as Parameter

```kotlin
import kotlinx.coroutines.*

class FactoryScopeFix {
    // Accept scope as parameter
    fun processItems(scope: CoroutineScope, items: List<String>) {
        scope.launch {
            items.forEach { item ->
                delay(1000)
                println("Processing: $item")
            }
        }
    }
}

// Usage with managed scope
fun demonstrateFactoryFix() = runBlocking {
    val scope = CoroutineScope(Job() + Dispatchers.Default)
    val processor = FactoryScopeFix()

    processor.processItems(scope, listOf("A", "B", "C"))

    delay(1500)

    println("Cancelling...")
    scope.cancel()

    println("Processing cancelled")
}
```

### Violation #4: Leaking Coroutines Across Architectural Boundaries

**The Problem:**

```kotlin
import kotlinx.coroutines.*

// VIOLATION: Repository launches coroutines
class LeakyRepository {
    fun loadData(callback: (String) -> Unit) {
        // BAD: Repository shouldn't launch coroutines
        GlobalScope.launch {
            val data = fetchFromNetwork()
            callback(data)
        }
    }

    private suspend fun fetchFromNetwork(): String {
        delay(1000)
        return "Network data"
    }
}

// ViewModel has no control over Repository's coroutines
class LeakyViewModel {
    private val repository = LeakyRepository()

    fun loadData() {
        repository.loadData { data ->
            // Can't cancel repository's coroutine!
            println("Got data: $data")
        }
    }

    fun onCleared() {
        // Can't cancel repository's work!
    }
}
```

#### Why It Violates Architecture

1. **Layer boundary violation** - Repository controls concurrency
2. **No cancellation** - ViewModel can't cancel
3. **Tight coupling** - ViewModel depends on Repository's threading
4. **Testing difficulty** - Hard to test Repository

#### The Fix: Suspend Functions

```kotlin
import kotlinx.coroutines.*

// GOOD: Repository exposes suspend functions
class StructuredRepository {
    suspend fun loadData(): String {
        // Repository doesn't launch coroutines
        // Just does work and returns
        return withContext(Dispatchers.IO) {
            fetchFromNetwork()
        }
    }

    private suspend fun fetchFromNetwork(): String {
        delay(1000)
        return "Network data"
    }
}

// ViewModel controls concurrency
class StructuredViewModel {
    private val repository = StructuredRepository()
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)

    fun loadData() {
        scope.launch {
            try {
                val data = repository.loadData()
                println("Got data: $data")
            } catch (e: CancellationException) {
                println("Cancelled")
                throw e
            }
        }
    }

    fun onCleared() {
        scope.cancel()
        // Now Repository's work is cancelled too!
    }
}
```

### When Breaking Structure Is Acceptable (Rare)

#### Legitimate Use Case 1: Application-Level Background Work

```kotlin
import kotlinx.coroutines.*

class BackgroundSyncManager(
    private val applicationScope: CoroutineScope // Explicit application-lifetime scope
) {
    fun startPeriodicSync() {
        // ACCEPTABLE: Application-level work
        applicationScope.launch {
            while (isActive) {
                try {
                    performSync()
                    delay(3600_000) // 1 hour
                } catch (e: Exception) {
                    // Log error
                }
            }
        }
    }

    private suspend fun performSync() {
        // Sync data with server
    }
}

// Application class
class MyApplication : Application() {
    private val applicationScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    override fun onCreate() {
        super.onCreate()

        val syncManager = BackgroundSyncManager(applicationScope)
        syncManager.startPeriodicSync()
    }
}
```

**Why this is acceptable:**
- **Explicit lifetime** - tied to Application lifecycle
- **Intentional** - truly needs to outlive screens
- **Managed** - applicationScope can be cancelled
- **Documented** - clear that it's application-level

#### Legitimate Use Case 2: Fire-and-Forget Analytics

```kotlin
import kotlinx.coroutines.*

class AnalyticsTracker(
    private val analyticsScope: CoroutineScope // Dedicated analytics scope
) {
    fun trackEvent(event: String) {
        // ACCEPTABLE: Fire-and-forget analytics
        analyticsScope.launch {
            try {
                sendToAnalyticsServer(event)
            } catch (e: Exception) {
                // Silently fail - analytics shouldn't crash app
            }
        }

        // Don't wait for completion
    }

    private suspend fun sendToAnalyticsServer(event: String) {
        withContext(Dispatchers.IO) {
            // Send event
        }
    }
}

// Setup with explicit scope
fun setupAnalytics(app: Application): AnalyticsTracker {
    // Dedicated scope with supervisor (failures don't propagate)
    val analyticsScope = CoroutineScope(
        SupervisorJob() +
        Dispatchers.IO +
        CoroutineName("Analytics")
    )

    return AnalyticsTracker(analyticsScope)
}
```

**Why this is acceptable:**
- **Non-critical** - analytics failures shouldn't affect app
- **Fire-and-forget** - intentionally don't wait
- **Isolated** - dedicated scope with SupervisorJob
- **Explicit** - clear separation from app logic

#### Legitimate Use Case 3: Crash Reporting

```kotlin
import kotlinx.coroutines.*

class CrashReporter {
    // ACCEPTABLE: Uses dedicated scope that survives cancellations
    private val crashScope = CoroutineScope(
        NonCancellable + // Survives cancellations
        Dispatchers.IO +
        CoroutineName("CrashReporter")
    )

    fun reportCrash(exception: Throwable) {
        crashScope.launch {
            try {
                sendCrashReport(exception)
            } catch (e: Exception) {
                // Last resort logging
                println("Failed to report crash: $e")
            }
        }
    }

    private suspend fun sendCrashReport(exception: Throwable) {
        // Send to crash reporting service
    }
}

// Usage in exception handler
class MyApplication : Application() {
    private val crashReporter = CrashReporter()

    override fun onCreate() {
        super.onCreate()

        Thread.setDefaultUncaughtExceptionHandler { _, exception ->
            crashReporter.reportCrash(exception)

            // Give time to report
            Thread.sleep(1000)

            // Then crash
            System.exit(1)
        }
    }
}
```

**Why this is acceptable:**
- **Critical path** - must complete even if app crashing
- **NonCancellable** - explicitly survives cancellations
- **Last resort** - only for crash reporting
- **Short-lived** - completes quickly

### Escape Hatch Patterns

#### Pattern 1: Explicit Application Scope

```kotlin
import kotlinx.coroutines.*

class ApplicationScopeProvider {
    val applicationScope = CoroutineScope(
        SupervisorJob() +
        Dispatchers.Default +
        CoroutineName("Application")
    )

    fun shutdown() {
        applicationScope.cancel()
    }
}

// Usage
class LongRunningService(
    private val applicationScope: CoroutineScope
) {
    fun startBackgroundWork() {
        applicationScope.launch {
            // Explicitly tied to application lifetime
            while (isActive) {
                doWork()
                delay(60_000)
            }
        }
    }

    private suspend fun doWork() {
        // Work that needs to outlive UI
    }
}
```

#### Pattern 2: Supervisor Scope for Independent Tasks

```kotlin
import kotlinx.coroutines.*

class IndependentTaskRunner {
    suspend fun runIndependentTasks() = supervisorScope {
        // Each task independent - one failure doesn't cancel others
        val task1 = launch {
            try {
                performTask1()
            } catch (e: Exception) {
                // Handle task 1 failure
            }
        }

        val task2 = launch {
            try {
                performTask2()
            } catch (e: Exception) {
                // Handle task 2 failure
            }
        }

        // Wait for all tasks
        task1.join()
        task2.join()
    }

    private suspend fun performTask1() {
        delay(1000)
    }

    private suspend fun performTask2() {
        delay(500)
        throw Exception("Task 2 failed")
    }
}

fun demonstrateSupervisorScope() = runBlocking {
    val runner = IndependentTaskRunner()

    runCatching {
        runner.runIndependentTasks()
    }

    println("Both tasks completed independently")
}
```

#### Pattern 3: Detached Coroutine (Use Sparingly)

```kotlin
import kotlinx.coroutines.*

class DetachedCoroutinePattern {
    fun performDetachedWork(scope: CoroutineScope, work: suspend () -> Unit) {
        // ESCAPE HATCH: Start detached coroutine
        scope.launch(start = CoroutineStart.UNDISPATCHED) {
            // Create new Job, breaking parent-child relationship
            withContext(Job()) {
                work()
            }
        }
    }
}

// Example: Long-running logging that shouldn't block parent
fun demonstrateDetached() = runBlocking {
    val scope = CoroutineScope(Job() + Dispatchers.Default)

    val pattern = DetachedCoroutinePattern()

    pattern.performDetachedWork(scope) {
        repeat(10) {
            delay(100)
            println("Detached work $it")
        }
    }

    delay(300)
    scope.cancel()

    println("Parent cancelled, but detached work continues")

    delay(1000)
}
```

### Real-World Examples

#### Example 1: Background Data Sync

```kotlin
import kotlinx.coroutines.*

class DataSyncManager(
    private val applicationScope: CoroutineScope
) {
    private var syncJob: Job? = null

    fun startSync() {
        // Cancel previous sync if running
        syncJob?.cancel()

        // Start new sync in application scope
        syncJob = applicationScope.launch {
            while (isActive) {
                try {
                    performSync()
                    delay(3600_000) // 1 hour
                } catch (e: CancellationException) {
                    throw e
                } catch (e: Exception) {
                    // Log and retry
                    delay(60_000) // Retry in 1 minute
                }
            }
        }
    }

    fun stopSync() {
        syncJob?.cancel()
        syncJob = null
    }

    private suspend fun performSync() {
        withContext(Dispatchers.IO) {
            // Sync data with server
            println("Syncing data...")
            delay(5000)
            println("Sync complete")
        }
    }
}

// Application setup
fun setupBackgroundSync(app: Application) {
    val applicationScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    val syncManager = DataSyncManager(applicationScope)
    syncManager.startSync()

    // Stop sync when app terminated
    Runtime.getRuntime().addShutdownHook(Thread {
        syncManager.stopSync()
    })
}
```

#### Example 2: Analytics SDK

```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.ConcurrentLinkedQueue

class AnalyticsSDK private constructor() {
    private val analyticsScope = CoroutineScope(
        SupervisorJob() +
        Dispatchers.IO +
        CoroutineName("Analytics") +
        CoroutineExceptionHandler { _, exception ->
            println("Analytics error: $exception")
        }
    )

    private val eventQueue = ConcurrentLinkedQueue<AnalyticsEvent>()
    private var flushJob: Job? = null

    fun initialize() {
        startPeriodicFlush()
    }

    fun trackEvent(event: AnalyticsEvent) {
        eventQueue.offer(event)

        // Fire-and-forget - intentionally unstructured
        // Analytics should never block app
    }

    private fun startPeriodicFlush() {
        flushJob = analyticsScope.launch {
            while (isActive) {
                delay(10_000) // Flush every 10 seconds

                val events = mutableListOf<AnalyticsEvent>()
                while (eventQueue.isNotEmpty()) {
                    eventQueue.poll()?.let { events.add(it) }
                }

                if (events.isNotEmpty()) {
                    try {
                        flushEvents(events)
                    } catch (e: Exception) {
                        // Re-queue events
                        events.forEach { eventQueue.offer(it) }
                    }
                }
            }
        }
    }

    private suspend fun flushEvents(events: List<AnalyticsEvent>) {
        withContext(Dispatchers.IO) {
            // Send to analytics server
            println("Flushing ${events.size} events")
        }
    }

    fun shutdown() {
        flushJob?.cancel()
        analyticsScope.cancel()
    }

    companion object {
        val instance = AnalyticsSDK()
    }
}

data class AnalyticsEvent(val name: String, val properties: Map<String, Any>)
```

#### Example 3: Crash Reporter

```kotlin
import kotlinx.coroutines.*

class CrashReportingSDK {
    private val crashScope = CoroutineScope(
        NonCancellable + // Must survive cancellations
        Dispatchers.IO +
        CoroutineName("CrashReporter")
    )

    fun reportException(exception: Throwable) {
        // Intentionally unstructured - must complete
        crashScope.launch {
            try {
                val report = buildCrashReport(exception)
                sendCrashReport(report)
            } catch (e: Exception) {
                // Log locally as fallback
                println("Failed to send crash report: $e")
            }
        }
    }

    private fun buildCrashReport(exception: Throwable): CrashReport {
        return CrashReport(
            exception = exception.toString(),
            stackTrace = exception.stackTraceToString(),
            timestamp = System.currentTimeMillis()
        )
    }

    private suspend fun sendCrashReport(report: CrashReport) {
        withContext(Dispatchers.IO) {
            // Send to crash reporting service
            delay(1000) // Simulate network call
            println("Crash report sent: ${report.exception}")
        }
    }
}

data class CrashReport(
    val exception: String,
    val stackTrace: String,
    val timestamp: Long
)
```

#### Example 4: App-Level Cache

```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.ConcurrentHashMap

class ApplicationCache(
    private val applicationScope: CoroutineScope
) {
    private val cache = ConcurrentHashMap<String, CacheEntry>()
    private var cleanupJob: Job? = null

    fun initialize() {
        startPeriodicCleanup()
    }

    fun put(key: String, value: Any, ttlMs: Long = 3600_000) {
        cache[key] = CacheEntry(
            value = value,
            expiryTime = System.currentTimeMillis() + ttlMs
        )
    }

    fun get(key: String): Any? {
        val entry = cache[key] ?: return null

        return if (entry.isExpired()) {
            cache.remove(key)
            null
        } else {
            entry.value
        }
    }

    private fun startPeriodicCleanup() {
        // Runs for application lifetime
        cleanupJob = applicationScope.launch {
            while (isActive) {
                delay(60_000) // Cleanup every minute

                val now = System.currentTimeMillis()
                cache.entries.removeIf { (_, entry) ->
                    entry.expiryTime < now
                }

                println("Cache cleanup: ${cache.size} entries remain")
            }
        }
    }

    fun shutdown() {
        cleanupJob?.cancel()
        cache.clear()
    }

    private data class CacheEntry(
        val value: Any,
        val expiryTime: Long
    ) {
        fun isExpired() = System.currentTimeMillis() > expiryTime
    }
}
```

### Detecting Violations

#### Tool 1: Detekt Custom Rules

```kotlin
// Custom Detekt rule to detect GlobalScope
class GlobalScopeUsageRule : Rule() {
    override val issue = Issue(
        id = "GlobalScopeUsage",
        severity = Severity.Warning,
        description = "GlobalScope violates structured concurrency",
        debt = Debt.FIVE_MINS
    )

    override fun visitCallExpression(expression: KtCallExpression) {
        super.visitCallExpression(expression)

        val callee = expression.calleeExpression?.text
        if (callee == "GlobalScope.launch" || callee == "GlobalScope.async") {
            report(CodeSmell(
                issue = issue,
                entity = Entity.from(expression),
                message = "GlobalScope usage detected. Use a structured scope instead."
            ))
        }
    }
}
```

#### Tool 2: Android Lint Rule

```kotlin
// Custom Android Lint rule
class UncancelledScopeDetector : Detector(), SourceCodeScanner {
    override fun getApplicableMethodNames(): List<String> {
        return listOf("CoroutineScope")
    }

    override fun visitMethodCall(
        context: JavaContext,
        node: UCallExpression,
        method: PsiMethod
    ) {
        // Check if CoroutineScope is created without lifecycle management
        val containingClass = node.getContainingClass()
        val hasCancelMethod = containingClass?.methods?.any { it.name == "cancel" }

        if (hasCancelMethod != true) {
            context.report(
                issue = ISSUE,
                location = context.getLocation(node),
                message = "CoroutineScope created without cancellation mechanism"
            )
        }
    }

    companion object {
        val ISSUE = Issue.create(
            id = "UncancelledCoroutineScope",
            briefDescription = "CoroutineScope without cancellation",
            explanation = "Every CoroutineScope should have a clear cancellation point",
            category = Category.CORRECTNESS,
            priority = 8,
            severity = Severity.WARNING,
            implementation = Implementation(
                UncancelledScopeDetector::class.java,
                Scope.JAVA_FILE_SCOPE
            )
        )
    }
}
```

#### Tool 3: Code Review Checklist

```kotlin
/**
 * Code Review Checklist for Structured Concurrency
 *
 *  RED FLAGS:
 * - GlobalScope.launch
 * - GlobalScope.async
 * - CoroutineScope(Job()) without cancellation
 * - Repository/UseCase launching coroutines
 * - Coroutines launched in constructors
 * - No clear lifecycle for scope
 *
 *  GREEN FLAGS:
 * - viewModelScope.launch
 * - lifecycleScope.launch
 * - Suspend functions in Repository/UseCase
 * - Explicit scope lifecycle (create + cancel)
 * - supervisorScope for independent tasks
 * - Well-documented escape hatches
 */
```

### Testing Structured Concurrency

#### Test 1: Verify Cancellation Propagation

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class StructuredConcurrencyTest {
    @Test
    fun testCancellationPropagates() = runTest {
        var child1Cancelled = false
        var child2Cancelled = false

        val scope = CoroutineScope(Job())

        scope.launch {
            try {
                delay(10000)
            } catch (e: CancellationException) {
                child1Cancelled = true
                throw e
            }
        }

        scope.launch {
            try {
                delay(10000)
            } catch (e: CancellationException) {
                child2Cancelled = true
                throw e
            }
        }

        advanceTimeBy(100)

        // Cancel parent
        scope.cancel()

        advanceUntilIdle()

        // Verify both children cancelled
        assertTrue(child1Cancelled, "Child 1 should be cancelled")
        assertTrue(child2Cancelled, "Child 2 should be cancelled")
    }

    @Test
    fun testExceptionPropagates() = runTest {
        var parentCaught = false

        try {
            coroutineScope {
                launch {
                    delay(100)
                    throw IllegalStateException("Child failed")
                }

                launch {
                    delay(10000)
                    // Should be cancelled due to sibling failure
                }
            }
        } catch (e: IllegalStateException) {
            parentCaught = true
        }

        assertTrue(parentCaught, "Exception should propagate to parent")
    }

    @Test
    fun testParentWaitsForChildren() = runTest {
        var child1Done = false
        var child2Done = false
        var parentDone = false

        coroutineScope {
            launch {
                delay(500)
                child1Done = true
            }

            launch {
                delay(1000)
                child2Done = true
            }

            parentDone = true
        }

        // Parent waits for all children
        assertTrue(child1Done)
        assertTrue(child2Done)
        assertTrue(parentDone)
    }
}
```

#### Test 2: Verify No Leaked Coroutines

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class LeakDetectionTest {
    @Test
    fun testNoLeakedCoroutines() = runTest {
        val scope = CoroutineScope(Job())

        // Start work
        repeat(10) {
            scope.launch {
                delay(1000)
            }
        }

        // Cancel scope
        scope.cancel()

        advanceUntilIdle()

        // Verify all cancelled
        val job = scope.coroutineContext[Job]!!
        assertTrue(job.isCancelled, "Scope should be cancelled")
        assertTrue(job.children.toList().isEmpty(), "No children should remain")
    }

    @Test
    fun testScopeCompletesAfterChildren() = runTest {
        var scopeCompleted = false

        val scope = CoroutineScope(Job())

        repeat(5) {
            scope.launch {
                delay(1000)
            }
        }

        scope.coroutineContext[Job]!!.invokeOnCompletion {
            scopeCompleted = true
        }

        advanceTimeBy(1000)

        assertTrue(scopeCompleted, "Scope should complete after all children")
    }
}
```

### Best Practices

1. **Always prefer structured concurrency**
   ```kotlin
   // GOOD
   suspend fun loadData() = coroutineScope {
       val data1 = async { fetchData1() }
       val data2 = async { fetchData2() }
       DataResult(data1.await(), data2.await())
   }
   ```

2. **Use lifecycle-aware scopes in Android**
   ```kotlin
   // GOOD
   class MyViewModel : ViewModel() {
       fun loadData() {
           viewModelScope.launch {
               // Automatically cancelled in onCleared()
           }
       }
   }
   ```

3. **Repositories expose suspend functions, not coroutines**
   ```kotlin
   // GOOD
   class Repository {
       suspend fun fetchData(): Data {
           return withContext(Dispatchers.IO) {
               // Work
           }
       }
   }
   ```

4. **For escape hatches, use explicit scopes with clear lifecycle**
   ```kotlin
   // ACCEPTABLE (with justification)
   class BackgroundService(
       private val applicationScope: CoroutineScope
   ) {
       fun startWork() {
           applicationScope.launch {
               // Explicitly tied to application lifetime
           }
       }
   }
   ```

5. **Document violations with clear reasoning**
   ```kotlin
   /**
    * Uses application-level scope because:
    * - Work must outlive UI components
    * - Data sync is application-level concern
    * - Scope is explicitly managed in Application.onTerminate()
    */
   ```

6. **Test cancellation behavior**
   ```kotlin
   @Test
   fun testCancellation() = runTest {
       val scope = CoroutineScope(Job())
       // Start work
       scope.cancel()
       // Verify cancelled
   }
   ```

---

## Русский

### Обзор

Структурная конкурентность — это основной принцип Kotlin корутин, который обеспечивает организацию корутин в иерархию с автоматической отменой, распространением исключений и гарантиями завершения. Нарушения структурной конкурентности могут привести к утечкам памяти, утечкам ресурсов, необработанным исключениям и трудно отлаживаемым проблемам конкурентности.

Это подробное руководство исследует что такое структурная конкурентность, распространённые нарушения, когда нарушение правил приемлемо (редко), легитимные пути обхода, а также инструменты для обнаружения и обеспечения соблюдения.

### Что Такое Структурная Конкурентность?

**Структурная конкурентность** — это парадигма, где:
1. Каждая корутина принадлежит скоупу
2. Дочерние корутины связаны с родительскими корутинами
3. Родители ждут завершения всех детей
4. Отмена распространяется от родителя к детям
5. Исключения распространяются от детей к родителю
6. Ни одна корутина не переживает свой скоуп

#### Основной Принцип

```
Scope
   Родительская корутина
      Дочерняя корутина 1
         Внучатая 1.1
         Внучатая 1.2
      Дочерняя корутина 2
          Внучатая 2.1
   Все завершаются вместе
```

#### Пример: Структурированная Vs Неструктурированная

```kotlin
import kotlinx.coroutines.*

fun demonstrateStructured() = runBlocking {
    println("=== Структурная конкурентность ===")

    // СТРУКТУРИРОВАННАЯ: Родитель ждёт детей
    coroutineScope {
        launch {
            delay(1000)
            println("Дочерняя 1 завершена")
        }

        launch {
            delay(500)
            println("Дочерняя 2 завершена")
        }

        println("Тело родителя завершено, ждём детей...")
    }

    println("Вся работа завершена\n")

    // НЕСТРУКТУРИРОВАННАЯ: Fire and forget
    println("=== Неструктурированная (нарушение) ===")

    GlobalScope.launch {
        delay(1000)
        println("Это может никогда не выполниться!")
    }

    println("Функция завершается немедленно")
    // Корутина GlobalScope может быть заброшена!
}
```

**Вывод:**
```
=== Структурная конкурентность ===
Тело родителя завершено, ждём детей...
Дочерняя 2 завершена
Дочерняя 1 завершена
Вся работа завершена

=== Неструктурированная (нарушение) ===
Функция завершается немедленно
(Корутина GlobalScope может никогда не завершиться)
```

### Преимущества Структурной Конкурентности

#### 1. Автоматическая Отмена

Когда родительская корутина отменяется или выбрасывает исключение, все дочерние корутины автоматически отменяются.

#### 2. Распространение Исключений

Исключения в дочерних корутинах автоматически распространяются к родительскому скоупу для обработки.

#### 3. Гарантии Завершения

Родительский скоуп не завершится до тех пор, пока все дочерние корутины не завершатся, включая блоки finally.

#### 4. Управление Ресурсами

Ресурсы гарантированно освобождаются даже при отмене или исключениях благодаря структурированному управлению жизненным циклом.

### Нарушение #1: GlobalScope (худшее нарушение)

**Почему это плохо:**
- Нет родительского скоупа
- Никогда не отменяется автоматически
- Нет распространения исключений
- Нет гарантий завершения
- Риск утечки памяти

#### Проблема

```kotlin
import kotlinx.coroutines.*

class GlobalScopeViolation {
    fun processData() {
        // НАРУШЕНИЕ: Неструктурированная корутина
        GlobalScope.launch {
            val data = loadData()
            processData(data)
            saveResults()
        }

        // Функция возвращается немедленно
        // Корутина может:
        // 1. Никогда не завершиться
        // 2. Завершиться после уничтожения компонента
        // 3. Упасть молча
        // 4. Вызвать утечку памяти
    }

    private suspend fun loadData(): String {
        delay(1000)
        return "data"
    }

    private fun processData(data: String) {
        println("Обработка: $data")
    }

    private fun saveResults() {
        println("Сохранение результатов")
    }
}
```

#### Исправление

```kotlin
import kotlinx.coroutines.*

class StructuredComponent {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    fun start() {
        println("Компонент запущен")

        // ХОРОШО: Структурированная корутина
        scope.launch {
            delay(2000)
            println("Это будет правильно отменено")
        }
    }

    fun stop() {
        println("Компонент остановлен")
        scope.cancel()
        // Все корутины отменены!
    }
}
```

### Нарушение #2: Создание Job() Без Жизненного Цикла

**Проблема:**

```kotlin
import kotlinx.coroutines.*

class UnmanagedJobViolation {
    // НАРУШЕНИЕ: Скоуп создан, но никогда не отменяется
    private val customScope = CoroutineScope(Job() + Dispatchers.Main)

    fun doWork() {
        customScope.launch {
            // Работа, которая может пережить класс
            repeat(100) {
                delay(100)
                println("Работа $it")
            }
        }
    }

    // ОТСУТСТВУЕТ: fun cleanup() { customScope.cancel() }
}
```

#### Почему Это Нарушение

1. **Нет явного жизненного цикла** - когда скоуп заканчивается?
2. **Нет отмены** - корутины работают вечно
3. **Утечка памяти** - держит ссылки
4. **Нет родителя** - нельзя отменить извне

#### Исправление: Явный Жизненный Цикл

```kotlin
import kotlinx.coroutines.*

class ManagedJobComponent {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)

    fun doWork() {
        scope.launch {
            repeat(100) {
                delay(100)
                println("Работа $it")
            }
        }
    }

    fun cleanup() {
        // ЯВНОЕ управление жизненным циклом
        scope.cancel()
        println("Все корутины отменены")
    }
}
```

### Нарушение #3: CoroutineScope() Фабрика Без Жизненного Цикла

**Проблема:**

```kotlin
import kotlinx.coroutines.*

class FactoryScopeViolation {
    fun processItems(items: List<String>) {
        // НАРУШЕНИЕ: Создаёт скоуп без привязки к жизненному циклу
        CoroutineScope(Dispatchers.Default).launch {
            items.forEach { item ->
                delay(1000)
                println("Обработка: $item")
            }
        }

        // Скоуп заброшен немедленно!
    }
}
```

#### Исправление: Передача Скоупа Как Параметра

```kotlin
import kotlinx.coroutines.*

class FactoryScopeFix {
    // Принимать скоуп как параметр
    fun processItems(scope: CoroutineScope, items: List<String>) {
        scope.launch {
            items.forEach { item ->
                delay(1000)
                println("Обработка: $item")
            }
        }
    }
}

// Использование с управляемым скоупом
fun demonstrateFactoryFix() = runBlocking {
    val scope = CoroutineScope(Job() + Dispatchers.Default)
    val processor = FactoryScopeFix()

    processor.processItems(scope, listOf("A", "B", "C"))

    delay(1500)

    println("Отмена...")
    scope.cancel()

    println("Обработка отменена")
}
```

### Нарушение #4: Утечка Корутин Через Архитектурные Границы

**Проблема:**

```kotlin
import kotlinx.coroutines.*

// НАРУШЕНИЕ: Репозиторий запускает корутины
class LeakyRepository {
    fun loadData(callback: (String) -> Unit) {
        // ПЛОХО: Репозиторий не должен запускать корутины
        GlobalScope.launch {
            val data = fetchFromNetwork()
            callback(data)
        }
    }

    private suspend fun fetchFromNetwork(): String {
        delay(1000)
        return "Данные из сети"
    }
}

// ViewModel не имеет контроля над корутинами Repository
class LeakyViewModel {
    private val repository = LeakyRepository()

    fun loadData() {
        repository.loadData { data ->
            // Не может отменить корутину репозитория!
            println("Получены данные: $data")
        }
    }

    fun onCleared() {
        // Не может отменить работу репозитория!
    }
}
```

#### Исправление: Suspend Функции

```kotlin
import kotlinx.coroutines.*

// ХОРОШО: Репозиторий предоставляет suspend функции
class StructuredRepository {
    suspend fun loadData(): String {
        // Репозиторий не запускает корутины
        // Просто выполняет работу и возвращает результат
        return withContext(Dispatchers.IO) {
            fetchFromNetwork()
        }
    }

    private suspend fun fetchFromNetwork(): String {
        delay(1000)
        return "Данные из сети"
    }
}

// ViewModel контролирует конкурентность
class StructuredViewModel {
    private val repository = StructuredRepository()
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)

    fun loadData() {
        scope.launch {
            try {
                val data = repository.loadData()
                println("Получены данные: $data")
            } catch (e: CancellationException) {
                println("Отменено")
                throw e
            }
        }
    }

    fun onCleared() {
        scope.cancel()
        // Теперь работа Repository тоже отменена!
    }
}
```

### Когда Нарушение Структуры Приемлемо (редко)

#### Легитимный Случай 1: Фоновая Работа Уровня Приложения

```kotlin
import kotlinx.coroutines.*

class BackgroundSyncManager(
    private val applicationScope: CoroutineScope // Явный скоуп времени жизни приложения
) {
    fun startPeriodicSync() {
        // ПРИЕМЛЕМО: Работа уровня приложения
        applicationScope.launch {
            while (isActive) {
                try {
                    performSync()
                    delay(3600_000) // 1 час
                } catch (e: Exception) {
                    // Логирование ошибки
                }
            }
        }
    }

    private suspend fun performSync() {
        // Синхронизация данных с сервером
    }
}
```

**Почему это приемлемо:**
- **Явное время жизни** - привязано к жизненному циклу Application
- **Намеренно** - действительно нужно пережить экраны
- **Управляемо** - applicationScope может быть отменён
- **Документировано** - ясно, что это уровень приложения

#### Легитимный Случай 2: Fire-and-Forget Аналитика

```kotlin
import kotlinx.coroutines.*

class AnalyticsTracker(
    private val analyticsScope: CoroutineScope // Выделенный скоуп для аналитики
) {
    fun trackEvent(event: String) {
        // ПРИЕМЛЕМО: Fire-and-forget аналитика
        analyticsScope.launch {
            try {
                sendToAnalyticsServer(event)
            } catch (e: Exception) {
                // Молча провалиться - аналитика не должна ронять приложение
            }
        }

        // Не ждём завершения
    }

    private suspend fun sendToAnalyticsServer(event: String) {
        withContext(Dispatchers.IO) {
            // Отправка события
        }
    }
}
```

**Почему это приемлемо:**
- **Некритично** - сбои аналитики не должны влиять на приложение
- **Fire-and-forget** - намеренно не ждём
- **Изолировано** - выделенный скоуп с SupervisorJob
- **Явно** - чёткое разделение от логики приложения

#### Легитимный Случай 3: Отчёты О Крашах

```kotlin
import kotlinx.coroutines.*

class CrashReporter {
    // ПРИЕМЛЕМО: Использует выделенный скоуп, который переживает отмены
    private val crashScope = CoroutineScope(
        NonCancellable + // Переживает отмены
        Dispatchers.IO +
        CoroutineName("CrashReporter")
    )

    fun reportCrash(exception: Throwable) {
        crashScope.launch {
            try {
                sendCrashReport(exception)
            } catch (e: Exception) {
                // Последнее средство логирования
                println("Не удалось отправить отчёт о краше: $e")
            }
        }
    }

    private suspend fun sendCrashReport(exception: Throwable) {
        // Отправка в сервис отчётов о крашах
    }
}
```

**Почему это приемлемо:**
- **Критический путь** - должен завершиться даже при краше приложения
- **NonCancellable** - явно переживает отмены
- **Последнее средство** - только для отчётов о крашах
- **Короткоживущий** - завершается быстро

### Паттерны Escape Hatch

#### Паттерн 1: Явный Application Scope

```kotlin
import kotlinx.coroutines.*

class ApplicationScopeProvider {
    val applicationScope = CoroutineScope(
        SupervisorJob() +
        Dispatchers.Default +
        CoroutineName("Application")
    )

    fun shutdown() {
        applicationScope.cancel()
    }
}

// Использование
class LongRunningService(
    private val applicationScope: CoroutineScope
) {
    fun startBackgroundWork() {
        applicationScope.launch {
            // Явно привязано к времени жизни приложения
            while (isActive) {
                doWork()
                delay(60_000)
            }
        }
    }

    private suspend fun doWork() {
        // Работа, которая должна пережить UI
    }
}
```

#### Паттерн 2: Supervisor Scope Для Независимых Задач

```kotlin
import kotlinx.coroutines.*

class IndependentTaskRunner {
    suspend fun runIndependentTasks() = supervisorScope {
        // Каждая задача независима - один сбой не отменяет другие
        val task1 = launch {
            try {
                performTask1()
            } catch (e: Exception) {
                // Обработка сбоя задачи 1
            }
        }

        val task2 = launch {
            try {
                performTask2()
            } catch (e: Exception) {
                // Обработка сбоя задачи 2
            }
        }

        // Ждём все задачи
        task1.join()
        task2.join()
    }

    private suspend fun performTask1() {
        delay(1000)
    }

    private suspend fun performTask2() {
        delay(500)
        throw Exception("Задача 2 провалилась")
    }
}
```

### Обнаружение Нарушений

#### Инструмент 1: Пользовательские Правила Detekt

Можно создать пользовательские правила Detekt для обнаружения использования GlobalScope и других нарушений структурной конкурентности.

#### Инструмент 2: Правила Android Lint

Пользовательские правила Lint могут обнаруживать CoroutineScope, созданные без механизма отмены.

#### Инструмент 3: Чеклист Code Review

**КРАСНЫЕ ФЛАГИ:**
- GlobalScope.launch
- GlobalScope.async
- CoroutineScope(Job()) без отмены
- Repository/UseCase запускающие корутины
- Корутины запущенные в конструкторах
- Нет чёткого жизненного цикла для скоупа

**ЗЕЛЁНЫЕ ФЛАГИ:**
- viewModelScope.launch
- lifecycleScope.launch
- Suspend функции в Repository/UseCase
- Явный жизненный цикл скоупа (create + cancel)
- supervisorScope для независимых задач
- Хорошо задокументированные пути обхода

### Тестирование Структурной Конкурентности

#### Тест 1: Проверка Распространения Отмены

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class StructuredConcurrencyTest {
    @Test
    fun testCancellationPropagates() = runTest {
        var child1Cancelled = false
        var child2Cancelled = false

        val scope = CoroutineScope(Job())

        scope.launch {
            try {
                delay(10000)
            } catch (e: CancellationException) {
                child1Cancelled = true
                throw e
            }
        }

        scope.launch {
            try {
                delay(10000)
            } catch (e: CancellationException) {
                child2Cancelled = true
                throw e
            }
        }

        advanceTimeBy(100)

        // Отменить родителя
        scope.cancel()

        advanceUntilIdle()

        // Проверить что оба ребёнка отменены
        assertTrue(child1Cancelled, "Ребёнок 1 должен быть отменён")
        assertTrue(child2Cancelled, "Ребёнок 2 должен быть отменён")
    }
}
```

### Лучшие Практики

1. **Всегда предпочитайте структурную конкурентность**
   ```kotlin
   // ХОРОШО
   suspend fun loadData() = coroutineScope {
       val data1 = async { fetchData1() }
       val data2 = async { fetchData2() }
       DataResult(data1.await(), data2.await())
   }
   ```

2. **Используйте lifecycle-aware скоупы в Android**
   ```kotlin
   // ХОРОШО
   class MyViewModel : ViewModel() {
       fun loadData() {
           viewModelScope.launch {
               // Автоматически отменяется в onCleared()
           }
       }
   }
   ```

3. **Репозитории предоставляют suspend функции, а не корутины**
   ```kotlin
   // ХОРОШО
   class Repository {
       suspend fun fetchData(): Data {
           return withContext(Dispatchers.IO) {
               // Работа
           }
       }
   }
   ```

4. **Для путей обхода используйте явные скоупы с чётким жизненным циклом**
   ```kotlin
   // ПРИЕМЛЕМО (с обоснованием)
   class BackgroundService(
       private val applicationScope: CoroutineScope
   ) {
       fun startWork() {
           applicationScope.launch {
               // Явно привязано к времени жизни приложения
           }
       }
   }
   ```

5. **Документируйте нарушения с чётким обоснованием**
   ```kotlin
   /**
    * Использует скоуп уровня приложения потому что:
    * - Работа должна пережить UI компоненты
    * - Синхронизация данных это забота уровня приложения
    * * - Скоуп явно управляется в Application.onTerminate()
    */
   ```

6. **Тестируйте поведение отмены**
   ```kotlin
   @Test
   fun testCancellation() = runTest {
       val scope = CoroutineScope(Job())
       // Запустить работу
       scope.cancel()
       // Проверить отменено
   }
   ```

---

## Follow-ups

1. How do you refactor code that uses GlobalScope to use structured concurrency?
2. What's the difference between `coroutineScope` and `supervisorScope`, and when should each be used?
3. How do you handle a situation where you genuinely need a coroutine to outlive its parent?
4. What are the performance implications of structured concurrency compared to unstructured?
5. How do you test that a scope properly cancels all its children in all scenarios?
6. Can you have structured concurrency across microservices, and what would that look like?
7. How do you migrate a large codebase from unstructured to structured coroutines?

## References

- [Kotlin Coroutines Guide - Structured Concurrency](https://kotlinlang.org/docs/coroutines-basics.html#structured-concurrency)
- [Roman Elizarov on Structured Concurrency](https://medium.com/@elizarov/structured-concurrency-722d765aa952)
- [Coroutine Scope Best Practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)
- [Android Lifecycle-Aware Components](https://developer.android.com/topic/libraries/architecture/lifecycle)

## Related Questions

- [[q-kotlin-advantages-for-android--kotlin--easy|Kotlin advantages for Android]]
