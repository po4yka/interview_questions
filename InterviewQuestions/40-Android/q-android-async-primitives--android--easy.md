---
id: "20251015082237280"
title: "Android Async Primitives / Примитивы асинхронности Android"
topic: android
difficulty: easy
status: draft
created: 2025-10-15
tags: [async, asynctask, coroutines, executorservice, handler, rxjava, threading, difficulty/easy]
---
# Какие асинхронные примитивы используют для обработки данных?

# Question (EN)
> What async primitives are used for data processing in Android?

# Вопрос (RU)
> Какие асинхронные примитивы используют для обработки данных в Android?

---

## Answer (EN)

Android provides several async primitives: **Thread** (basic), **Handler/Looper** (message passing), **AsyncTask** (deprecated), **ExecutorService** (thread pools), **Coroutines** (modern, recommended), **RxJava** (reactive streams), and **WorkManager** (background tasks).

**Modern recommendation**: Use Kotlin Coroutines with Flow for most async operations.

---

## Ответ (RU)

Async primitives in Android are used to perform background tasks without blocking the main UI thread, ensuring smooth app operation and preventing ANR (Application Not Responding) errors.

### Modern Async Primitives (Recommended)

#### 1. Kotlin Coroutines (Recommended)

Lightweight concurrency framework that makes async code look synchronous.

```kotlin
class DataViewModel : ViewModel() {

    fun loadData() {
        viewModelScope.launch {
            // Background work on IO dispatcher
            val data = withContext(Dispatchers.IO) {
                database.fetchData()
            }

            // Automatically switches to Main dispatcher
            _uiState.value = UiState.Success(data)
        }
    }

    fun parallelOperations() {
        viewModelScope.launch {
            // Run multiple operations concurrently
            val result1 = async { fetchFromApi1() }
            val result2 = async { fetchFromApi2() }

            // Wait for both to complete
            val combined = result1.await() + result2.await()
            _data.value = combined
        }
    }
}
```

**Advantages:**
- Structured concurrency
- Automatic lifecycle management
- Readable, sequential code
- Built-in cancellation
- Exception handling

#### 2. Flow (Reactive Streams)

Kotlin's reactive stream for handling multiple values over time.

```kotlin
class UserRepository {
    // Cold flow - starts when collected
    fun getUsers(): Flow<List<User>> = flow {
        val users = api.fetchUsers()
        emit(users)
    }.flowOn(Dispatchers.IO)

    // Hot flow - always active
    private val _userUpdates = MutableStateFlow<User?>(null)
    val userUpdates: StateFlow<User?> = _userUpdates.asStateFlow()
}

// Fragment
class UserListFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            repository.getUsers().collect { users ->
                adapter.submitList(users)
            }
        }
    }
}
```

#### 3. WorkManager

For guaranteed background work that survives app restarts.

```kotlin
class DataSyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            syncData()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// Schedule work
val workRequest = PeriodicWorkRequestBuilder<DataSyncWorker>(
    repeatInterval = 15,
    repeatIntervalTimeUnit = TimeUnit.MINUTES
).build()

WorkManager.getInstance(context).enqueue(workRequest)
```

### Legacy Async Primitives

#### 4. AsyncTask (Deprecated since API 30)

Simple but problematic approach, no longer recommended.

```kotlin
// DO NOT USE - Only for reference
class DownloadTask : AsyncTask<String, Int, String>() {
    override fun doInBackground(vararg params: String): String {
        // Background work
        return downloadData(params[0])
    }

    override fun onProgressUpdate(vararg values: Int?) {
        // Update UI with progress
    }

    override fun onPostExecute(result: String) {
        // Update UI with result
    }
}
```

**Why deprecated:**
- Memory leaks with Activity/Fragment references
- No cancellation mechanism
- Difficult error handling
- Configuration change issues

#### 5. Handler and Looper

Low-level threading primitive for message passing.

```kotlin
class MyActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    fun performBackgroundWork() {
        Thread {
            // Background work
            val result = processData()

            // Post to main thread
            handler.post {
                textView.text = result
            }
        }.start()
    }

    // Delayed execution
    fun scheduleTask() {
        handler.postDelayed({
            updateUI()
        }, 1000) // 1 second delay
    }
}
```

**Use cases:**
- Custom timing mechanisms
- Message queue manipulation
- Low-level thread communication

#### 6. ExecutorService and ThreadPoolExecutor

Java concurrency framework for managing thread pools.

```kotlin
class DataProcessor {
    private val executor = Executors.newFixedThreadPool(4)

    fun processInBackground() {
        executor.execute {
            // Background task
            val result = heavyComputation()

            runOnUiThread {
                updateUI(result)
            }
        }
    }

    // With Future
    fun processWithResult(): Future<String> {
        return executor.submit<String> {
            performOperation()
        }
    }

    fun cleanup() {
        executor.shutdown()
    }
}

// Usage
val future = processor.processWithResult()
val result = future.get() // Blocks until complete
```

#### 7. RxJava

Reactive programming library for composing async operations.

```kotlin
class DataRepository {

    fun loadData(): Observable<List<Item>> {
        return Observable.create { emitter ->
            try {
                val data = api.fetchData()
                emitter.onNext(data)
                emitter.onComplete()
            } catch (e: Exception) {
                emitter.onError(e)
            }
        }
        .subscribeOn(Schedulers.io())
        .observeOn(AndroidSchedulers.mainThread())
    }

    fun combineData(): Observable<CombinedData> {
        return Observable.zip(
            loadUsers(),
            loadPosts(),
            BiFunction { users, posts ->
                CombinedData(users, posts)
            }
        )
    }
}

// Usage
disposable = repository.loadData()
    .subscribe(
        { data -> updateUI(data) },
        { error -> handleError(error) }
    )
```

### Comparison Table

| Primitive | Difficulty | Lifecycle Aware | Cancellation | Modern | Use Case |
|-----------|------------|-----------------|--------------|--------|----------|
| **Coroutines** | Low | Yes | Yes | Yes | General async operations |
| **Flow** | Medium | Yes | Yes | Yes | Reactive streams |
| **WorkManager** | Low | Yes | Yes | Yes | Guaranteed background work |
| **AsyncTask** | Low | No | No | No | Deprecated |
| **Handler** | Medium | No | Manual | Yes | Message passing |
| **ExecutorService** | Medium | No | Manual | Yes | Thread pool management |
| **RxJava** | High | No | Yes | Yes | Complex reactive streams |

### Best Practices

**Use Coroutines for most cases:**

```kotlin
class ModernViewModel : ViewModel() {

    // Simple async operation
    fun loadData() {
        viewModelScope.launch {
            val data = repository.getData()
            _uiState.value = data
        }
    }

    // With error handling
    fun loadDataSafe() {
        viewModelScope.launch {
            try {
                val data = withContext(Dispatchers.IO) {
                    repository.getData()
                }
                _uiState.value = UiState.Success(data)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message)
            }
        }
    }

    // Concurrent operations
    fun loadMultiple() {
        viewModelScope.launch {
            coroutineScope {
                val users = async { repository.getUsers() }
                val posts = async { repository.getPosts() }

                _data.value = CombinedData(
                    users = users.await(),
                    posts = posts.await()
                )
            }
        }
    }
}
```

**Use Flow for reactive data:**

```kotlin
class UserViewModel : ViewModel() {
    val users: Flow<List<User>> = repository.observeUsers()
        .map { it.filter { user -> user.isActive } }
        .flowOn(Dispatchers.Default)
}

// Fragment
viewLifecycleOwner.lifecycleScope.launch {
    viewModel.users.collect { users ->
        adapter.submitList(users)
    }
}
```

**Use WorkManager for guaranteed execution:**

```kotlin
// One-time work
val uploadWork = OneTimeWorkRequestBuilder<UploadWorker>()
    .setInputData(workDataOf("file_path" to path))
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(uploadWork)
```

### Summary

**Modern Android async primitives:**
1. **Kotlin Coroutines** - Primary choice for async operations
2. **Flow** - Reactive data streams
3. **WorkManager** - Guaranteed background work

**Legacy primitives (still valid for specific cases):**
4. **Handler/Looper** - Message passing and scheduling
5. **ExecutorService** - Thread pool management
6. **RxJava** - Complex reactive operations (if already using it)

**Deprecated:**
7. **AsyncTask** - Don't use in new code

For new Android development, prefer Coroutines + Flow + WorkManager combination.

## Ответ (RU)
Асинхронные примитивы в Android используются для выполнения задач в фоновом режиме, чтобы не блокировать основной поток пользовательского интерфейса (UI) и обеспечивать плавную работу приложений. Основные асинхронные примитивы включают: AsyncTask, Handler и Looper, ExecutorService и Future, RxJava и Coroutines.

