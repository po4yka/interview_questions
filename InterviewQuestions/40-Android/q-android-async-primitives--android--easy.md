---
id: 20251012-122762
title: Android Async Primitives / Примитивы асинхронности Android
aliases:
- Android Async Primitives
- Примитивы асинхронности Android
topic: android
subtopics:
- coroutines
- threads-sync
question_kind: android
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-coroutine-builders-basics--kotlin--easy
- q-viewmodel-pattern--android--easy
created: 2025-10-15
updated: 2025-10-15
tags:
- android/coroutines
- android/threads-sync
- difficulty/easy
---

# Вопрос (RU)
> Что такое Примитивы асинхронности Android?

---

# Question (EN)
> What are Android Async Primitives?

## Answer (EN)
Android provides several async primitives: Thread (basic), Handler/Looper (message passing), AsyncTask (deprecated), ExecutorService (thread pools), [[c-coroutines|Coroutines]] (modern, recommended), RxJava (reactive streams), and [[c-workmanager|WorkManager]] (background tasks).

**Modern recommendation**: Use Kotlin Coroutines with Flow for most async operations.

**1. Kotlin Coroutines (Recommended)**
- **Lightweight concurrency** framework
- **Structured concurrency** with automatic lifecycle management
- **Readable, sequential code** that looks synchronous

```kotlin
// Basic coroutine usage
class DataViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            val data = withContext(Dispatchers.IO) {
                repository.fetchData()
            }
            _uiState.value = UiState.Success(data)
        }
    }

    // Parallel operations
    fun loadMultiple() {
        viewModelScope.launch {
            val result1 = async { fetchFromApi1() }
            val result2 = async { fetchFromApi2() }
            val combined = result1.await() + result2.await()
            _data.value = combined
        }
    }
}
```

**2. Flow (Reactive Streams)**
- **Cold flow**: Starts when collected
- **Hot flow**: Always active (StateFlow, SharedFlow)
- **Operators**: map, filter, combine, etc.

```kotlin
// Cold flow
fun getUsers(): Flow<List<User>> = flow {
    val users = api.fetchUsers()
    emit(users)
}.flowOn(Dispatchers.IO)

// Hot flow
private val _userUpdates = MutableStateFlow<User?>(null)
val userUpdates: StateFlow<User?> = _userUpdates.asStateFlow()

// Usage
lifecycleScope.launch {
    repository.getUsers().collect { users ->
        adapter.submitList(users)
    }
}
```

**3. WorkManager**
- **Guaranteed execution** that survives app restarts
- **Constraints**: WiFi, charging, low battery
- **Periodic work** and **one-time work**

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

**4. Handler/Looper (Legacy)**
- **Message passing** between threads
- **Delayed execution** with postDelayed
- **Low-level** threading primitive

```kotlin
class MyActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    fun performBackgroundWork() {
        Thread {
            val result = processData()
            handler.post {
                textView.text = result
            }
        }.start()
    }

    fun scheduleTask() {
        handler.postDelayed({
            updateUI()
        }, 1000)
    }
}
```

**5. ExecutorService (Legacy)**
- **Thread pool management**
- **Future** for getting results
- **Manual lifecycle** management

```kotlin
class DataProcessor {
    private val executor = Executors.newFixedThreadPool(4)

    fun processInBackground() {
        executor.execute {
            val result = heavyComputation()
            runOnUiThread {
                updateUI(result)
            }
        }
    }

    fun processWithResult(): Future<String> {
        return executor.submit<String> {
            performOperation()
        }
    }
}
```

**6. RxJava (Legacy)**
- **Reactive programming** library
- **Complex operators** for data transformation
- **Steep learning curve**

```kotlin
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
```

**7. AsyncTask (Deprecated)**
- **Deprecated since API 30**
- **Memory leaks** with Activity/Fragment references
- **No cancellation** mechanism
- **Don't use** in new code

**Comparison:**

| Primitive | Difficulty | Lifecycle Aware | Cancellation | Modern | Use Case |
|-----------|------------|-----------------|--------------|--------|----------|
| **Coroutines** | Low | Yes | Yes | Yes | General async operations |
| **Flow** | Medium | Yes | Yes | Yes | Reactive streams |
| **WorkManager** | Low | Yes | Yes | Yes | Guaranteed background work |
| **Handler** | Medium | No | Manual | Yes | Message passing |
| **ExecutorService** | Medium | No | Manual | Yes | Thread pool management |
| **RxJava** | High | No | Yes | Yes | Complex reactive streams |
| **AsyncTask** | Low | No | No | No | Deprecated |

**Best Practices:**
- **Use Coroutines** for most async operations
- **Use Flow** for reactive data streams
- **Use WorkManager** for guaranteed background work
- **Avoid AsyncTask** - use Coroutines instead
- **Use Handler** only for specific message passing needs

## Follow-ups

- How do you choose between Coroutines and RxJava for a new project?
- What are the key differences between StateFlow and SharedFlow?
- How do you handle cancellation in long-running coroutines?
- What are the benefits of using WorkManager over other background task solutions?
- How do you debug async operations in Android?

## References

- [Kotlin Coroutines](https://kotlinlang.org/docs/coroutines-overview.html)
- [Flow Documentation](https://kotlinlang.org/docs/flow.html)
- [WorkManager Guide](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Android Threading](https://developer.android.com/guide/components/processes-and-threads)

## Related Questions

### Prerequisites (Easier)
- q-coroutines-basics--kotlin--easy - Coroutines fundamentals
- [[q-viewmodel-pattern--android--easy]] - ViewModel pattern

### Related (Medium)
- q-lifecycle-aware-components--android--medium - Lifecycle management
- [[q-flow-operators--kotlin--medium]] - Flow operators
- [[q-what-is-workmanager--android--medium]] - WorkManager basics

### Advanced (Harder)
- [[q-advanced-coroutine-patterns--kotlin--hard]] - Advanced coroutines
- [[q-workmanager-execution-guarantee--android--medium]] - WorkManager guarantees