---
id: 20251012-122785
title: "Async Operations Android / Асинхронные операции Android"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [android/concurrency, async, concurrency, coroutines, executor, handler, threading, workmanager, difficulty/medium]
---
# How to run asynchronous operations in Android?

# Question (EN)
> How to run asynchronous operations in pure Android?

# Вопрос (RU)
> Как запустить асинхронные операции в чистом Android?

---

## Answer (EN)

Android provides **multiple ways** to run asynchronous operations:

1. **Kotlin Coroutines** (modern, recommended)
2. **ExecutorService** (Java standard)
3. **HandlerThread** (message-based)
4. **WorkManager** (background jobs)
5. **AsyncTask** (deprecated, avoid)
6. **Thread** (low-level)
7. **RxJava** (reactive programming)

---

## 1. Kotlin Coroutines (Recommended)

**Modern, structured concurrency for Android.**

### Basic Usage

```kotlin
import kotlinx.coroutines.*

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Launch coroutine
        lifecycleScope.launch {
            // Background work
            val result = withContext(Dispatchers.IO) {
                fetchDataFromNetwork()
            }

            // Update UI (automatically on Main dispatcher)
            textView.text = result
        }
    }

    private suspend fun fetchDataFromNetwork(): String {
        delay(2000) // Simulate network delay
        return "Data from server"
    }
}
```

---

### Multiple Coroutines

```kotlin
import kotlinx.coroutines.*

lifecycleScope.launch {
    try {
        // Run multiple tasks concurrently
        val deferred1 = async(Dispatchers.IO) { fetchUser() }
        val deferred2 = async(Dispatchers.IO) { fetchPosts() }
        val deferred3 = async(Dispatchers.IO) { fetchComments() }

        // Wait for all results
        val user = deferred1.await()
        val posts = deferred2.await()
        val comments = deferred3.await()

        // Update UI
        displayData(user, posts, comments)

    } catch (e: Exception) {
        showError(e.message)
    }
}
```

---

### With Error Handling

```kotlin
import kotlinx.coroutines.*

class UserViewModel : ViewModel() {

    private val _state = MutableStateFlow<UiState>(UiState.Loading)
    val state: StateFlow<UiState> = _state.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _state.value = UiState.Loading

            try {
                val user = withContext(Dispatchers.IO) {
                    userRepository.getUser(userId)
                }
                _state.value = UiState.Success(user)

            } catch (e: Exception) {
                _state.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

sealed class UiState {
    object Loading : UiState()
    data class Success(val user: User) : UiState()
    data class Error(val message: String) : UiState()
}
```

---

## 2. ExecutorService (Java Standard)

**Thread pool for background tasks.**

### Basic Usage

```kotlin
import java.util.concurrent.Executors

class MainActivity : AppCompatActivity() {

    private val executor = Executors.newSingleThreadExecutor()
    private val mainHandler = Handler(Looper.getMainLooper())

    private fun loadData() {
        executor.execute {
            // Background work
            val result = fetchDataFromNetwork()

            // Update UI on main thread
            mainHandler.post {
                textView.text = result
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        executor.shutdown()
    }
}
```

---

### With Callable and Future

```kotlin
import java.util.concurrent.*

class DataLoader {

    private val executor = Executors.newFixedThreadPool(4)

    fun loadUser(userId: String): Future<User> {
        return executor.submit(Callable {
            // Background work
            Thread.sleep(2000)
            fetchUser(userId)
        })
    }

    fun loadMultipleUsers(ids: List<String>): List<User> {
        val futures = ids.map { id ->
            executor.submit(Callable { fetchUser(id) })
        }

        // Wait for all results
        return futures.map { it.get() }
    }

    fun shutdown() {
        executor.shutdown()
    }
}

// Usage
val loader = DataLoader()
val userFuture = loader.loadUser("123")

// Do other work...

val user = userFuture.get() // Blocks until result is ready
```

---

## 3. HandlerThread (Message-Based)

**Background thread with message queue.**

```kotlin
import android.os.HandlerThread
import android.os.Handler

class BackgroundProcessor {

    private val handlerThread = HandlerThread("BackgroundThread")
    private lateinit var backgroundHandler: Handler
    private val mainHandler = Handler(Looper.getMainLooper())

    fun start() {
        handlerThread.start()
        backgroundHandler = Handler(handlerThread.looper)
    }

    fun processData(data: String, callback: (String) -> Unit) {
        backgroundHandler.post {
            // Background work
            Thread.sleep(2000)
            val result = processHeavyTask(data)

            // Callback on main thread
            mainHandler.post {
                callback(result)
            }
        }
    }

    fun stop() {
        handlerThread.quitSafely()
    }

    private fun processHeavyTask(data: String): String {
        return "Processed: $data"
    }
}

// Usage
class MainActivity : AppCompatActivity() {

    private val processor = BackgroundProcessor()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        processor.start()

        processor.processData("input") { result ->
            textView.text = result
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        processor.stop()
    }
}
```

---

## 4. WorkManager (Background Jobs)

**Deferrable, guaranteed background work.**

### One-Time Work

```kotlin
import androidx.work.*

class UploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val imageUri = inputData.getString("imageUri") ?: return Result.failure()

            // Background work (survives app kill)
            uploadImage(imageUri)

            Result.success()

        } catch (e: Exception) {
            Result.retry()
        }
    }

    private suspend fun uploadImage(uri: String) {
        // Upload logic
    }
}

// Schedule work
class MainActivity : AppCompatActivity() {

    private fun uploadImage(imageUri: String) {
        val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>()
            .setInputData(workDataOf("imageUri" to imageUri))
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build()
            )
            .build()

        WorkManager.getInstance(this).enqueue(uploadRequest)
    }
}
```

---

### Periodic Work

```kotlin
class SyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        syncDataWithServer()
        return Result.success()
    }
}

// Schedule periodic sync (every 1 hour)
val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(syncRequest)
```

---

## 5. AsyncTask (Deprecated)

** Deprecated in API 30 - Use Coroutines instead.**

```kotlin
//  DEPRECATED - DO NOT USE
class DownloadTask : AsyncTask<String, Int, String>() {

    override fun doInBackground(vararg params: String): String {
        val url = params[0]
        // Background work
        return downloadFile(url)
    }

    override fun onProgressUpdate(vararg values: Int?) {
        // Update progress on UI thread
        progressBar.progress = values[0] ?: 0
    }

    override fun onPostExecute(result: String) {
        // Update UI with result
        textView.text = result
    }
}

// Usage
DownloadTask().execute("https://example.com/file.zip")
```

**Why deprecated?**
- Memory leaks (implicit Activity reference)
- No lifecycle awareness
- Not cancelable properly
- Use Coroutines instead

---

## 6. Thread (Low-Level)

**Basic Java Thread.**

```kotlin
class MainActivity : AppCompatActivity() {

    private fun loadData() {
        Thread {
            // Background work
            val result = fetchDataFromNetwork()

            // Update UI on main thread
            runOnUiThread {
                textView.text = result
            }
        }.start()
    }

    private fun fetchDataFromNetwork(): String {
        Thread.sleep(2000)
        return "Data from server"
    }
}
```

**With runOnUiThread:**
```kotlin
Thread {
    val data = performHeavyComputation()

    runOnUiThread {
        updateUI(data)
    }
}.start()
```

---

## 7. RxJava (Reactive Programming)

**Reactive streams for asynchronous programming.**

```kotlin
import io.reactivex.rxjava3.android.schedulers.AndroidSchedulers
import io.reactivex.rxjava3.core.Single
import io.reactivex.rxjava3.schedulers.Schedulers

class UserRepository {

    fun getUser(userId: String): Single<User> {
        return Single.fromCallable {
            // Background work
            fetchUserFromNetwork(userId)
        }
        .subscribeOn(Schedulers.io())
        .observeOn(AndroidSchedulers.mainThread())
    }
}

// Usage
class MainActivity : AppCompatActivity() {

    private val repository = UserRepository()
    private val compositeDisposable = CompositeDisposable()

    private fun loadUser(userId: String) {
        val disposable = repository.getUser(userId)
            .subscribe(
                { user ->
                    // Success - on main thread
                    displayUser(user)
                },
                { error ->
                    // Error - on main thread
                    showError(error.message)
                }
            )

        compositeDisposable.add(disposable)
    }

    override fun onDestroy() {
        super.onDestroy()
        compositeDisposable.dispose()
    }
}
```

---

## Comparison Table

| Method | Use Case | Lifecycle Aware | Cancellation | Learning Curve |
|--------|----------|----------------|--------------|----------------|
| **Coroutines** | General async | Yes | Easy | Medium |
| **ExecutorService** | Thread pool | No | Manual | Low |
| **HandlerThread** | Sequential tasks | No | Manual | Low |
| **WorkManager** | Background jobs | Yes | Easy | Medium |
| **AsyncTask** | Deprecated | No | Poor | Low |
| **Thread** | Simple tasks | No | No | Low |
| **RxJava** | Reactive streams | No | Easy | High |

---

## Best Practices

### 1. Use Coroutines for Most Cases

```kotlin
// GOOD: Coroutines with lifecycle scope
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) {
        repository.fetchData()
    }
    updateUI(data)
}
```

### 2. Use WorkManager for Background Jobs

```kotlin
// GOOD: WorkManager for deferrable, guaranteed work
val uploadWork = OneTimeWorkRequestBuilder<UploadWorker>()
    .setConstraints(Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .build())
    .build()

WorkManager.getInstance(context).enqueue(uploadWork)
```

### 3. Avoid AsyncTask

```kotlin
// BAD: AsyncTask (deprecated)
class MyTask : AsyncTask<Void, Void, String>() { ... }

// GOOD: Coroutines
lifecycleScope.launch {
    val result = withContext(Dispatchers.IO) { doWork() }
    updateUI(result)
}
```

### 4. Clean Up Resources

```kotlin
// GOOD: Proper cleanup
class MainActivity : AppCompatActivity() {

    private val executor = Executors.newSingleThreadExecutor()

    override fun onDestroy() {
        super.onDestroy()
        executor.shutdown() // Clean up
    }
}
```

---

## Summary

**Recommended approaches for async operations in Android:**

1. **Kotlin Coroutines** (default choice)
   - Lifecycle-aware
   - Structured concurrency
   - Easy cancellation
   - Clean syntax

2. **WorkManager** (background jobs)
   - Survives app restarts
   - Constraint-based execution
   - Guaranteed execution

3. **ExecutorService** (Java compatibility)
   - Thread pool management
   - Simple but no lifecycle awareness

**Avoid:**
- AsyncTask (deprecated)
- Raw Thread (hard to manage)

---

## Ответ (RU)

В Android существует **несколько способов** запуска асинхронных операций:

1. **Kotlin Coroutines** (современный, рекомендуется)
2. **ExecutorService** (стандарт Java)
3. **HandlerThread** (на основе сообщений)
4. **WorkManager** (фоновые задачи)
5. **AsyncTask** (устарел, избегать)
6. **Thread** (низкоуровневый)
7. **RxJava** (реактивное программирование)

**Рекомендуемые подходы:**

```kotlin
// Kotlin Coroutines (для большинства случаев)
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) {
        repository.fetchData()
    }
    updateUI(data)
}

// WorkManager (для гарантированных фоновых задач)
val work = OneTimeWorkRequestBuilder<UploadWorker>().build()
WorkManager.getInstance(context).enqueue(work)

// ExecutorService (для совместимости с Java)
val executor = Executors.newSingleThreadExecutor()
executor.execute {
    val result = doWork()
    mainHandler.post { updateUI(result) }
}
```

**Избегайте:**
- AsyncTask (deprecated в API 30)
- Сырые Thread (сложно управлять)

