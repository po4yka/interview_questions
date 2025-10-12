---
id: "20251012-170009"
title: "Detecting and preventing coroutine memory leaks / Обнаружение и предотвращение утечек памяти"
subtopics:
  - coroutines
  - memory-leaks
  - lifecycle
  - android
  - debugging
difficulty: hard
moc: moc-kotlin
status: draft
created: 2025-10-12
updated: 2025-10-12
tags:
  - kotlin
  - coroutines
  - memory-leaks
  - android
  - lifecycle
  - debugging
  - leakcanary
  - profiling
---

# Detecting and preventing coroutine memory leaks / Обнаружение и предотвращение утечек памяти

## English

### Overview

Memory leaks in coroutine-based applications can be subtle and devastating. A single leaked coroutine can hold references to large objects (Activities, Fragments, Views), preventing garbage collection and causing OutOfMemoryErrors. Understanding common leak patterns, detection techniques, and prevention strategies is essential for production Android development.

This comprehensive guide covers the 5 most common coroutine leak sources, detection tools (LeakCanary, Memory Profiler, DebugProbes), prevention strategies, and automated testing approaches.

### What Is a Coroutine Memory Leak?

A coroutine memory leak occurs when:
1. A coroutine continues running after its associated component (Activity, ViewModel) is destroyed
2. The coroutine holds strong references to destroyed objects
3. These objects cannot be garbage collected
4. Memory accumulates over time

```kotlin
// LEAK EXAMPLE
class LeakyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // BAD: Coroutine outlives Activity
        GlobalScope.launch {
            while (true) {
                delay(1000)
                updateUI() // Holds reference to Activity!
            }
        }
    }

    private fun updateUI() {
        // Access Activity/Views
    }
}
```

### Common Leak Sources Overview

| Leak Type | Root Cause | Severity | Detection Difficulty |
|-----------|-----------|----------|---------------------|
| **GlobalScope** | No cancellation | Critical | Easy |
| **Missing cancellation** | Forgot to cancel | High | Medium |
| **Captured context** | Strong references | High | Hard |
| **Long operations** | Holds refs during I/O | Medium | Medium |
| **Leaked collectors** | Flow collectors alive | High | Hard |

### Leak #1: GlobalScope Usage

**Problem:** `GlobalScope` coroutines live for the entire application lifetime and are never cancelled automatically.

#### The Problem

```kotlin
import kotlinx.coroutines.*
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle

class GlobalScopeLeakActivity : AppCompatActivity() {
    private var data: String = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // BAD: GlobalScope coroutine
        GlobalScope.launch {
            // Simulate loading data
            delay(10000) // 10 seconds

            // Activity might be destroyed, but coroutine continues
            data = fetchDataFromNetwork()

            // Crash if Activity is destroyed!
            runOnUiThread {
                updateUI(data)
            }
        }
    }

    private suspend fun fetchDataFromNetwork(): String {
        delay(5000)
        return "Network data"
    }

    private fun updateUI(data: String) {
        // Access views - will crash if Activity destroyed
    }
}
```

#### Why It Leaks

1. **GlobalScope never cancels** - coroutine runs even after Activity destroyed
2. **Holds Activity reference** - via `this` in `runOnUiThread`
3. **Holds View references** - in `updateUI`
4. **Multiple instances accumulate** - each Activity rotation creates new leak

#### Memory Impact

```kotlin
// Simulating the leak
class GlobalScopeLeakSimulation {
    fun demonstrateLeak() {
        repeat(10) { iteration ->
            // Simulate Activity being created and destroyed
            val activity = GlobalScopeLeakActivity()

            // Each Activity starts a GlobalScope coroutine
            // Activity destroyed, but coroutine continues
            // After 10 rotations: 10 leaked Activities!
        }

        // Heap contains:
        // - 10 Activity instances (should be 1)
        // - 10 View hierarchies
        // - All associated resources
        // = Potential OutOfMemoryError
    }
}
```

#### The Fix

```kotlin
import kotlinx.coroutines.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import android.os.Bundle

class FixedActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // GOOD: Use lifecycleScope
        lifecycleScope.launch {
            try {
                val data = fetchDataFromNetwork()
                updateUI(data)
            } catch (e: CancellationException) {
                // Properly cancelled when Activity destroyed
                throw e
            }
        }
    }

    private suspend fun fetchDataFromNetwork(): String {
        delay(5000)
        return "Network data"
    }

    private fun updateUI(data: String) {
        // Safe: only called if Activity still alive
    }
}
```

#### Detection

```kotlin
// Add this to debug builds
class GlobalScopeDetector {
    companion object {
        fun detectGlobalScopeUsage() {
            // Use Detekt or custom lint rule
            // Fail CI if GlobalScope detected
        }
    }
}
```

### Leak #2: Not Cancelling When Component Dies

**Problem:** Creating coroutines with custom scopes and forgetting to cancel them.

#### The Problem

```kotlin
import kotlinx.coroutines.*
import androidx.fragment.app.Fragment
import android.os.Bundle
import android.view.View

class LeakyFragment : Fragment() {
    // BAD: Custom scope never cancelled
    private val customScope = CoroutineScope(Dispatchers.Main + Job())

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Starts coroutine in custom scope
        customScope.launch {
            while (true) {
                delay(1000)
                updateCounter() // Holds Fragment reference
            }
        }
    }

    private fun updateCounter() {
        // Access views
        view?.findViewById<TextView>(R.id.counter)?.text = "Updated"
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // MISTAKE: Forgot to cancel customScope!
        // customScope.cancel()
    }
}
```

#### Why It Leaks

1. **Fragment destroyed** - `onDestroyView()` called
2. **Views released** - but coroutine still running
3. **Fragment held in memory** - by running coroutine
4. **Multiple fragments accumulate** - navigation creates multiple leaks

#### The Fix

```kotlin
import kotlinx.coroutines.*
import androidx.fragment.app.Fragment
import androidx.lifecycle.viewLifecycleOwner
import androidx.lifecycle.lifecycleScope
import android.os.Bundle
import android.view.View

class FixedFragment : Fragment() {
    // Option 1: Use viewLifecycleOwner.lifecycleScope
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            // Automatically cancelled when view destroyed
            while (true) {
                delay(1000)
                updateCounter()
            }
        }
    }

    // Option 2: Manual scope management
    private var customScope: CoroutineScope? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        customScope = CoroutineScope(Dispatchers.Main + Job())
    }

    override fun onDestroy() {
        super.onDestroy()
        customScope?.cancel()
        customScope = null
    }

    private fun updateCounter() {
        view?.findViewById<TextView>(R.id.counter)?.text = "Updated"
    }
}
```

#### ViewModel Example

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.*

class LeakyViewModel : ViewModel() {
    // BAD: Custom scope never cancelled
    private val customScope = CoroutineScope(Dispatchers.IO + Job())

    fun loadData() {
        customScope.launch {
            // This coroutine might outlive ViewModel!
            val data = fetchData()
            processData(data)
        }
    }

    override fun onCleared() {
        super.onCleared()
        // MISTAKE: Forgot to cancel!
        // customScope.cancel()
    }
}

class FixedViewModel : ViewModel() {
    // GOOD: Use viewModelScope
    fun loadData() {
        viewModelScope.launch {
            // Automatically cancelled in onCleared()
            val data = fetchData()
            processData(data)
        }
    }

    private suspend fun fetchData(): String {
        delay(1000)
        return "data"
    }

    private fun processData(data: String) {
        // Process
    }
}
```

### Leak #3: Captured Strong References

**Problem:** Coroutines capture strong references to Activities, Views, or Contexts in lambdas.

#### The Problem

```kotlin
import kotlinx.coroutines.*
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.TextView

class CapturedReferenceLeakActivity : AppCompatActivity() {
    private lateinit var textView: TextView
    private var userData: LargeUserData? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        textView = findViewById(R.id.textView)
        userData = LargeUserData() // Large object

        lifecycleScope.launch {
            delay(30000) // Long operation

            // BAD: Captures Activity, TextView, userData
            // Even if Activity destroyed, these are kept alive
            textView.text = "Updated: ${userData?.info}"
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        // Activity destroyed, but coroutine holds references!
    }
}

data class LargeUserData(
    val info: String = "User info",
    val largeArray: ByteArray = ByteArray(1024 * 1024) // 1MB
)
```

#### Why It Leaks

1. **Lambda captures references** - `textView`, `userData`, implicit `this`
2. **Long-running coroutine** - 30 second delay
3. **Activity destroyed early** - user navigates away
4. **Objects held for 30 seconds** - preventing GC

#### The Fix: Weak References

```kotlin
import kotlinx.coroutines.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import android.os.Bundle
import android.widget.TextView
import java.lang.ref.WeakReference

class FixedCapturedReferenceActivity : AppCompatActivity() {
    private lateinit var textView: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        textView = findViewById(R.id.textView)

        // Create weak references
        val textViewRef = WeakReference(textView)
        val userData = LargeUserData()

        lifecycleScope.launch {
            val result = withContext(Dispatchers.IO) {
                delay(5000)
                "Updated: ${userData.info}"
            }

            // Check if Activity still alive
            textViewRef.get()?.text = result
            // If Activity destroyed, textViewRef.get() returns null
        }
    }
}
```

#### The Fix: Check Lifecycle State

```kotlin
import kotlinx.coroutines.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.*
import android.os.Bundle

class LifecycleAwareActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val data = fetchData()

            // Check if still in valid state
            if (lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)) {
                updateUI(data)
            }
        }
    }

    private suspend fun fetchData(): String {
        delay(5000)
        return "data"
    }

    private fun updateUI(data: String) {
        // Update UI
    }
}
```

#### The Fix: Extract Processing

```kotlin
import kotlinx.coroutines.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope

class ExtractedProcessingActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Do heavy work without capturing Activity
            val result = processDataWithoutContext()

            // Only capture Activity briefly for UI update
            updateUI(result)
        }
    }

    // No Activity references captured
    private suspend fun processDataWithoutContext(): String = withContext(Dispatchers.Default) {
        delay(5000)
        // Heavy computation without UI references
        "Processed result"
    }

    private fun updateUI(result: String) {
        // Quick UI update
    }
}
```

### Leak #4: Long-Running Operations Holding References

**Problem:** Long network/database operations holding references to UI components.

#### The Problem

```kotlin
import kotlinx.coroutines.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import java.io.File

class LongOperationLeakActivity : AppCompatActivity() {
    private lateinit var progressBar: ProgressBar
    private var results = mutableListOf<String>()

    fun downloadLargeFile() {
        lifecycleScope.launch {
            // BAD: Holds Activity reference for entire download
            progressBar.visibility = View.VISIBLE

            repeat(100) { i ->
                delay(1000) // Simulate slow download (100 seconds!)

                // Captures 'this' Activity and 'results'
                val chunk = downloadChunk(i)
                results.add(chunk)

                // Holds progressBar reference
                progressBar.progress = i
            }

            progressBar.visibility = View.GONE
        }
    }

    private suspend fun downloadChunk(index: Int): String {
        delay(1000)
        return "Chunk $index"
    }
}
```

#### The Fix: Use Flow with Lifecycle-Aware Collection

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.lifecycle.Lifecycle

class FixedLongOperationActivity : AppCompatActivity() {
    private lateinit var progressBar: ProgressBar

    fun downloadLargeFile() {
        lifecycleScope.launch {
            // Flow doesn't hold Activity reference
            downloadFlow()
                .flowOn(Dispatchers.IO)
                .collect { progress ->
                    // Only updates UI when Activity is STARTED
                    updateProgress(progress)
                }
        }
    }

    private fun downloadFlow(): Flow<DownloadProgress> = flow {
        repeat(100) { i ->
            delay(1000)
            val chunk = downloadChunk(i)
            emit(DownloadProgress(i, chunk))
        }
    }

    private suspend fun downloadChunk(index: Int): String {
        delay(1000)
        return "Chunk $index"
    }

    private fun updateProgress(progress: DownloadProgress) {
        progressBar.progress = progress.percentage
    }
}

data class DownloadProgress(val percentage: Int, val data: String)
```

#### The Fix: Separate Business Logic from UI

```kotlin
import kotlinx.coroutines.*
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.*

class DownloadViewModel : ViewModel() {
    private val _downloadProgress = MutableStateFlow<DownloadState>(DownloadState.Idle)
    val downloadProgress: StateFlow<DownloadState> = _downloadProgress.asStateFlow()

    fun startDownload() {
        viewModelScope.launch {
            _downloadProgress.value = DownloadState.Downloading(0)

            repeat(100) { i ->
                delay(1000)
                val chunk = downloadChunk(i)
                // No UI references - just state
                _downloadProgress.value = DownloadState.Downloading(i)
            }

            _downloadProgress.value = DownloadState.Complete
        }
    }

    private suspend fun downloadChunk(index: Int): String {
        delay(1000)
        return "Chunk $index"
    }
}

sealed class DownloadState {
    object Idle : DownloadState()
    data class Downloading(val progress: Int) : DownloadState()
    object Complete : DownloadState()
}

class DownloadActivity : AppCompatActivity() {
    private val viewModel: DownloadViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Collect safely with lifecycle awareness
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.downloadProgress.collect { state ->
                    updateUI(state)
                }
            }
        }

        viewModel.startDownload()
    }

    private fun updateUI(state: DownloadState) {
        when (state) {
            is DownloadState.Idle -> { /* ... */ }
            is DownloadState.Downloading -> { /* ... */ }
            is DownloadState.Complete -> { /* ... */ }
        }
    }
}
```

### Leak #5: Flow Collectors Not Cancelled

**Problem:** Flow collectors that continue collecting after component destruction.

#### The Problem

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import androidx.fragment.app.Fragment

class LeakyFlowFragment : Fragment() {
    private val dataFlow = MutableSharedFlow<String>()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // BAD: Collector never cancelled
        GlobalScope.launch {
            dataFlow.collect { data ->
                // Holds Fragment reference
                updateUI(data)
            }
        }
    }

    private fun updateUI(data: String) {
        view?.findViewById<TextView>(R.id.textView)?.text = data
    }
}
```

#### The Fix

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle

class FixedFlowFragment : Fragment() {
    private val dataFlow = MutableSharedFlow<String>()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // GOOD: Collector cancelled with lifecycle
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                dataFlow.collect { data ->
                    updateUI(data)
                }
            }
        }
    }

    private fun updateUI(data: String) {
        view?.findViewById<TextView>(R.id.textView)?.text = data
    }
}
```

### Detection Tool #1: LeakCanary 2.x

LeakCanary 2.x has built-in coroutine support and can detect leaked coroutines.

#### Setup

```kotlin
// build.gradle.kts
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.12")
}

// No initialization needed - auto-installs
```

#### Reading LeakCanary Reports

```
====================================
HEAP ANALYSIS RESULT
====================================
1 APPLICATION LEAKS

Leak 1:
┬─
│ GC Root: Thread
│
├─ Thread name: DefaultDispatcher-worker-1
│
├─ CoroutineScope instance
│
├─ LeakyActivity instance
│    Leaking: YES (Activity destroyed but not GC'd)
│    Retained size: 8.5 MB
│
╰→ View hierarchy (leaked)

LEAK TRACE:
GlobalScope.launch -> LeakyActivity -> ViewRoot -> Views
```

#### Example: Detecting GlobalScope Leak

```kotlin
import com.squareup.leakcanary.ObjectWatcher
import kotlinx.coroutines.*

class LeakCanaryIntegration {
    fun detectLeakedCoroutine() {
        val activity = LeakyActivity()

        // Simulate Activity lifecycle
        activity.onCreate(null)
        activity.onDestroy()

        // LeakCanary will detect that Activity is still retained
        // by running GlobalScope coroutine

        // Report will show:
        // - Thread: DefaultDispatcher-worker-X
        // - Coroutine: launch
        // - Retained object: LeakyActivity
    }
}
```

### Detection Tool #2: Android Studio Memory Profiler

#### Heap Dump Analysis

1. **Trigger heap dump** after Activity destroyed
2. **Look for multiple instances** of Activity/Fragment classes
3. **Inspect references** to find holding coroutines

```kotlin
// Trigger heap dump programmatically in debug
class MemoryProfilerHelper {
    fun dumpHeap() {
        if (BuildConfig.DEBUG) {
            val heapDumpFile = File(context.filesDir, "heap_dump.hprof")
            Debug.dumpHprofData(heapDumpFile.absolutePath)
            println("Heap dumped to: ${heapDumpFile.absolutePath}")
        }
    }
}
```

#### Analyzing Dump

```
1. Open Memory Profiler
2. Capture heap dump
3. Search for "Activity" or "Fragment"
4. If count > expected:
   - Select instance
   - View "References" tab
   - Look for:
     - CoroutineScope
     - Job
     - Thread references
   - Trace to root GC cause
```

### Detection Tool #3: DebugProbes for Coroutines

`kotlinx-coroutines-debug` provides coroutine-specific debugging.

#### Setup

```kotlin
// build.gradle.kts
dependencies {
    debugImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-debug:1.7.3")
}

// Enable in Application class
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        if (BuildConfig.DEBUG) {
            DebugProbes.install()
        }
    }
}
```

#### Dumping Active Coroutines

```kotlin
import kotlinx.coroutines.debug.DebugProbes
import kotlinx.coroutines.*

class CoroutineDebugger {
    fun dumpActiveCoroutines() {
        // Get all active coroutines
        val coroutines = DebugProbes.dumpCoroutinesInfo()

        println("Active coroutines: ${coroutines.size}")

        coroutines.forEach { info ->
            println("Coroutine: ${info.context}")
            println("  State: ${info.state}")
            println("  Stack trace:")
            info.lastObservedStackTrace().forEach { frame ->
                println("    $frame")
            }
        }
    }

    fun detectLeakedCoroutines(expectedCount: Int) {
        val coroutines = DebugProbes.dumpCoroutinesInfo()

        if (coroutines.size > expectedCount) {
            println("WARNING: ${coroutines.size - expectedCount} leaked coroutines!")

            coroutines.drop(expectedCount).forEach { leaked ->
                println("Leaked coroutine:")
                println("  Context: ${leaked.context}")
                println("  Created at:")
                leaked.creationStackTrace().forEach { frame ->
                    println("    $frame")
                }
            }
        }
    }
}
```

#### Example Usage

```kotlin
class DebugActivity : AppCompatActivity() {
    private val debugger = CoroutineDebugger()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Start some coroutines
        lifecycleScope.launch {
            delay(10000)
        }

        // Dump after 1 second
        lifecycleScope.launch {
            delay(1000)
            debugger.dumpActiveCoroutines()
        }
    }

    override fun onDestroy() {
        super.onDestroy()

        // Check for leaks after destroy
        GlobalScope.launch {
            delay(1000)
            debugger.detectLeakedCoroutines(0)
        }
    }
}
```

### Job Tree Inspection

```kotlin
import kotlinx.coroutines.*

class JobTreeInspector {
    fun inspectJobTree(job: Job, indent: String = "") {
        println("${indent}Job: $job")
        println("${indent}  isActive: ${job.isActive}")
        println("${indent}  isCompleted: ${job.isCompleted}")
        println("${indent}  isCancelled: ${job.isCancelled}")

        job.children.forEach { child ->
            inspectJobTree(child, "$indent  ")
        }
    }

    fun findLeakedJobs(scope: CoroutineScope): List<Job> {
        val job = scope.coroutineContext[Job] ?: return emptyList()
        return findActiveJobs(job)
    }

    private fun findActiveJobs(job: Job): List<Job> {
        val leaked = mutableListOf<Job>()

        if (job.isActive) {
            leaked.add(job)
        }

        job.children.forEach { child ->
            leaked.addAll(findActiveJobs(child))
        }

        return leaked
    }
}

// Usage
class InspectedActivity : AppCompatActivity() {
    private val inspector = JobTreeInspector()
    private lateinit var activityScope: CoroutineScope

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        activityScope = CoroutineScope(Job() + Dispatchers.Main)

        activityScope.launch {
            delay(5000)
        }

        activityScope.launch {
            delay(10000)
        }

        // Inspect job tree
        val job = activityScope.coroutineContext[Job]!!
        inspector.inspectJobTree(job)
    }

    override fun onDestroy() {
        super.onDestroy()

        // Check for leaks before cancelling
        val leakedJobs = inspector.findLeakedJobs(activityScope)
        println("Leaked jobs before cancel: ${leakedJobs.size}")

        activityScope.cancel()
    }
}
```

### Prevention: Lifecycle-Aware Scopes

#### Android Built-in Scopes

```kotlin
import androidx.lifecycle.*
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import kotlinx.coroutines.*

class LifecycleScopesDemo : AppCompatActivity() {
    fun demonstrateScopes() {
        // Activity scope - cancelled in onDestroy
        lifecycleScope.launch {
            // Safe: cancelled when Activity destroyed
        }

        // ViewModel scope (in ViewModel class)
        class MyViewModel : ViewModel() {
            init {
                viewModelScope.launch {
                    // Safe: cancelled in onCleared()
                }
            }
        }
    }
}

class FragmentScopesDemo : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Fragment lifecycle scope - cancelled in onDestroy
        lifecycleScope.launch {
            // Lives as long as Fragment
        }

        // View lifecycle scope - cancelled in onDestroyView
        viewLifecycleOwner.lifecycleScope.launch {
            // Lives as long as View
            // PREFERRED for UI updates
        }
    }
}
```

#### Choosing the Right Scope

| Scope | Lifecycle | Use Case |
|-------|-----------|----------|
| `GlobalScope` | Application | **AVOID** (almost never correct) |
| `lifecycleScope` (Activity) | onCreate → onDestroy | Activity-level operations |
| `lifecycleScope` (Fragment) | onCreate → onDestroy | Fragment-level operations |
| `viewLifecycleOwner.lifecycleScope` | onCreateView → onDestroyView | UI updates in Fragment |
| `viewModelScope` | ViewModel creation → onCleared | Business logic |

### Prevention: Structured Concurrency

```kotlin
import kotlinx.coroutines.*

class StructuredConcurrencyDemo {
    // BAD: Unstructured
    fun unstructuredExample() {
        GlobalScope.launch {
            // Parent doesn't know about this
        }
    }

    // GOOD: Structured
    suspend fun structuredExample() = coroutineScope {
        // All children launched here
        launch {
            // Child 1
        }

        launch {
            // Child 2
        }

        // coroutineScope waits for all children
        // If cancelled, all children cancelled
    }
}
```

### Testing for Leaks

#### Automated Leak Detection Test

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.*

class LeakDetectionTest {
    @Test
    fun testNoLeakedCoroutines() = runTest {
        val scope = CoroutineScope(Job() + Dispatchers.Default)

        // Start some work
        scope.launch {
            delay(1000)
        }

        // Cancel scope
        scope.cancel()

        // Verify all coroutines cancelled
        advanceUntilIdle()

        val job = scope.coroutineContext[Job]!!
        assertFalse(job.isActive, "Scope should be cancelled")
        assertTrue(job.children.toList().isEmpty(), "All children should be cancelled")
    }

    @Test
    fun testViewModelScopeCancellation() {
        val viewModel = MyViewModel()

        // Start work
        viewModel.loadData()

        // Simulate onCleared
        viewModel.onCleared()

        // Verify scope cancelled
        // (Requires exposing scope for testing or using reflection)
    }
}
```

#### LeakCanary Test

```kotlin
import leakcanary.DetectLeaksAfterTestSuccess
import org.junit.Rule
import org.junit.Test

class ActivityLeakTest {
    @get:Rule
    val rule = DetectLeaksAfterTestSuccess()

    @Test
    fun testActivityDoesNotLeak() {
        val scenario = ActivityScenario.launch(MyActivity::class.java)

        // Perform actions
        scenario.onActivity { activity ->
            activity.doSomething()
        }

        // Destroy activity
        scenario.close()

        // LeakCanary will detect leaks after test
    }
}
```

### Code Review Checklist

#### Manual Review Points

```kotlin
// Checklist for code review:

// ❌ GlobalScope usage
GlobalScope.launch { }

// ❌ Custom scope without cancellation
class MyClass {
    private val scope = CoroutineScope(Job())
    // Missing: fun cleanup() { scope.cancel() }
}

// ❌ Capturing Activity/View in long operations
lifecycleScope.launch {
    delay(60000)
    activity.updateUI() // BAD: holds Activity for 1 minute
}

// ❌ Flow collection without lifecycle awareness
GlobalScope.launch {
    flow.collect { } // BAD: never cancelled
}

// ✅ Lifecycle-aware scope
lifecycleScope.launch { }

// ✅ ViewModel scope
viewModelScope.launch { }

// ✅ Proper cancellation
private val scope = CoroutineScope(Job())
fun cleanup() {
    scope.cancel()
}

// ✅ Lifecycle-aware Flow collection
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        flow.collect { }
    }
}
```

### Static Analysis: Detekt Rules

```yaml
# detekt.yml
potential-bugs:
  GlobalScope:
    active: true
    description: "GlobalScope usage can cause memory leaks"

coroutines:
  SuspendFunctionOnCoroutineScope:
    active: true

  RedundantSuspendModifier:
    active: true

custom-rules:
  UncancelledCoroutineScope:
    active: true
    description: "CoroutineScope should be cancelled"
```

### Production Monitoring

```kotlin
import kotlinx.coroutines.*

class CoroutineLeakMonitor {
    private var activeScopes = 0

    fun onScopeCreated() {
        activeScopes++
        if (activeScopes > 100) {
            // Alert: possible leak!
            logWarning("Too many active scopes: $activeScopes")
        }
    }

    fun onScopeCancelled() {
        activeScopes--
    }

    private fun logWarning(message: String) {
        // Send to crash reporting
        // Crashlytics.log(message)
    }
}

// Instrumented scope factory
class InstrumentedScopeFactory(private val monitor: CoroutineLeakMonitor) {
    fun createScope(): CoroutineScope {
        monitor.onScopeCreated()

        val job = Job()
        job.invokeOnCompletion {
            monitor.onScopeCancelled()
        }

        return CoroutineScope(job + Dispatchers.Main)
    }
}
```

### Best Practices Summary

1. **Always use lifecycle-aware scopes**
   - `lifecycleScope`, `viewModelScope`, `viewLifecycleOwner.lifecycleScope`

2. **Never use GlobalScope**
   - Except for application-lifetime operations (rare)

3. **Cancel custom scopes**
   - If you create `CoroutineScope`, you must cancel it

4. **Avoid capturing Activity/View references in long operations**
   - Use Flow, weak references, or lifecycle checks

5. **Use `repeatOnLifecycle` for Flow collection**
   - Automatically starts/stops with lifecycle

6. **Enable LeakCanary in debug builds**
   - Catches leaks during development

7. **Review coroutine usage in code reviews**
   - Check for scope management, cancellation

8. **Test for leaks**
   - Automated tests for scope cancellation

---

## Русский

### Обзор

Утечки памяти в приложениях на основе корутин могут быть незаметными и разрушительными. Одна утёкшая корутина может удерживать ссылки на большие объекты (Activities, Fragments, Views), предотвращая сборку мусора и вызывая OutOfMemoryErrors.

### Что такое утечка памяти корутины?

Утечка памяти корутины происходит когда:
1. Корутина продолжает работать после уничтожения компонента
2. Корутина удерживает сильные ссылки на уничтоженные объекты
3. Эти объекты не могут быть собраны сборщиком мусора
4. Память накапливается со временем

### Утечка #1: Использование GlobalScope

**Проблема:** Корутины `GlobalScope` живут всё время работы приложения и никогда не отменяются автоматически.

### Утечка #2: Неотмена при уничтожении компонента

**Проблема:** Создание корутин с пользовательскими скоупами и забывание их отменить.

### Утечка #3: Захваченные сильные ссылки

**Проблема:** Корутины захватывают сильные ссылки на Activities, Views или Contexts в лямбдах.

### Утечка #4: Длительные операции удерживают ссылки

**Проблема:** Долгие сетевые/БД операции удерживают ссылки на UI компоненты.

### Утечка #5: Коллекторы Flow не отменены

**Проблема:** Коллекторы Flow продолжают собирать после уничтожения компонента.

### Инструмент обнаружения #1: LeakCanary 2.x

LeakCanary 2.x имеет встроенную поддержку корутин и может обнаруживать утёкшие корутины.

### Инструмент обнаружения #2: Android Studio Memory Profiler

Анализ heap dump для поиска утёкших объектов.

### Инструмент обнаружения #3: DebugProbes для корутин

`kotlinx-coroutines-debug` предоставляет специфичную для корутин отладку.

### Предотвращение: Lifecycle-Aware Scopes

Использование встроенных в Android скоупов для автоматической отмены.

### Тестирование на утечки

Автоматизированные тесты для обнаружения утечек корутин.

### Лучшие практики

1. **Всегда используйте lifecycle-aware скоупы**
2. **Никогда не используйте GlobalScope**
3. **Отменяйте пользовательские скоупы**
4. **Избегайте захвата Activity/View ссылок**
5. **Используйте `repeatOnLifecycle` для Flow**
6. **Включайте LeakCanary в debug сборках**
7. **Проверяйте использование корутин в code review**
8. **Тестируйте на утечки**

---

## Follow-up Questions

1. How do you detect a memory leak caused by a coroutine that completes eventually but takes too long?
2. What's the difference between a memory leak and a memory retention issue in coroutines?
3. How can you use Java heap dumps to specifically identify coroutine-related leaks?
4. When is it acceptable to use GlobalScope, and how do you do it safely?
5. How do you test that a ViewModel properly cancels all coroutines in onCleared()?
6. What are the performance implications of using WeakReference in coroutines?
7. How do you monitor coroutine memory usage in production without LeakCanary?

## References

- [LeakCanary Documentation](https://square.github.io/leakcanary/)
- [Android Memory Profiler](https://developer.android.com/studio/profile/memory-profiler)
- [Coroutines Debug Mode](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html#debugging-coroutines-and-threads)
- [Lifecycle-aware Components](https://developer.android.com/topic/libraries/architecture/lifecycle)

## Related Questions

- [[q-structured-concurrency-violations--kotlin--hard|Structured concurrency violations]]
- [[q-coroutine-lifecycle-management--kotlin--medium|Coroutine lifecycle management]]
- [[q-job-state-machine-transitions--kotlin--medium|Job state machine and transitions]]
- [[q-android-lifecycle-coroutines-integration--kotlin--medium|Android lifecycle and coroutines integration]]
