---
topic: android
tags:
  - android
  - android/concurrency
  - concurrency
  - multithreading
  - performance
  - threading
difficulty: easy
---

# Для чего нужна многопоточность, какие инструменты использовать?

**English**: Why is multithreading needed and which tools should be used?

## Answer

**Multithreading** allows executing **heavy tasks** without blocking the UI thread.

**Main purpose:** Keep the UI responsive by offloading work to background threads.

**Tools in Android:**
1. **Kotlin Coroutines** (modern, recommended)
2. **ExecutorService** (thread pools)
3. **Thread** (basic Java threads)
4. **Handler** + **HandlerThread** (message-based)
5. **WorkManager** (background jobs)
6. **RxJava** (reactive programming)
7. **LiveData** (lifecycle-aware data)
8. **Flow** (reactive streams)

---

## Why Multithreading?

### Problem: UI Thread Blocking

**The UI thread** (main thread) handles:
- User interactions (touch events)
- UI rendering (60 FPS = 16.67ms per frame)
- Lifecycle callbacks

If you block the UI thread for too long → **ANR (Application Not Responding)**

```kotlin
// ❌ BAD: Blocking UI thread
class MainActivity : AppCompatActivity() {

    private fun loadData() {
        // This blocks UI thread for 5 seconds!
        Thread.sleep(5000)
        val data = fetchFromNetwork()
        textView.text = data
    }
}
```

**Result:**
- App freezes
- User can't interact
- ANR dialog after 5 seconds

---

### Solution: Offload to Background Thread

```kotlin
// ✅ GOOD: Background thread
class MainActivity : AppCompatActivity() {

    private fun loadData() {
        lifecycleScope.launch(Dispatchers.IO) {
            // Background work
            val data = fetchFromNetwork()

            // Update UI on main thread
            withContext(Dispatchers.Main) {
                textView.text = data
            }
        }
    }
}
```

**Result:**
- UI stays responsive
- No freezing
- No ANR

---

## Common Heavy Tasks

### 1. Network Requests

```kotlin
// ❌ BAD: Network on UI thread
val response = httpClient.get("https://api.example.com/users")

// ✅ GOOD: Network on background thread
lifecycleScope.launch(Dispatchers.IO) {
    val response = httpClient.get("https://api.example.com/users")
    withContext(Dispatchers.Main) {
        updateUI(response)
    }
}
```

---

### 2. Database Operations

```kotlin
// ❌ BAD: Database query on UI thread
val users = database.userDao().getAllUsers()

// ✅ GOOD: Database on background thread
lifecycleScope.launch(Dispatchers.IO) {
    val users = database.userDao().getAllUsers()
    withContext(Dispatchers.Main) {
        recyclerView.adapter = UserAdapter(users)
    }
}
```

---

### 3. File I/O

```kotlin
// ❌ BAD: File read on UI thread
val content = File("large_file.txt").readText()

// ✅ GOOD: File I/O on background thread
lifecycleScope.launch(Dispatchers.IO) {
    val content = File("large_file.txt").readText()
    withContext(Dispatchers.Main) {
        textView.text = content
    }
}
```

---

### 4. Image Processing

```kotlin
// ❌ BAD: Image decoding on UI thread
val bitmap = BitmapFactory.decodeFile("large_image.jpg")

// ✅ GOOD: Image processing on background thread
lifecycleScope.launch(Dispatchers.Default) {
    val bitmap = BitmapFactory.decodeFile("large_image.jpg")
    val processed = applyFilters(bitmap)

    withContext(Dispatchers.Main) {
        imageView.setImageBitmap(processed)
    }
}
```

---

### 5. Parsing Large Data

```kotlin
// ❌ BAD: JSON parsing on UI thread
val users = Json.decodeFromString<List<User>>(largeJsonString)

// ✅ GOOD: Parsing on background thread
lifecycleScope.launch(Dispatchers.Default) {
    val users = Json.decodeFromString<List<User>>(largeJsonString)
    withContext(Dispatchers.Main) {
        displayUsers(users)
    }
}
```

---

## Multithreading Tools in Android

### 1. Kotlin Coroutines (Recommended)

**Modern, structured concurrency.**

```kotlin
import kotlinx.coroutines.*

class MainActivity : AppCompatActivity() {

    private fun loadUser(userId: String) {
        lifecycleScope.launch {
            try {
                // Background work
                val user = withContext(Dispatchers.IO) {
                    userRepository.getUser(userId)
                }

                // Update UI (automatically on Main)
                textView.text = user.name

            } catch (e: Exception) {
                showError(e.message)
            }
        }
    }
}
```

**Advantages:**
- ✅ Lifecycle-aware (`lifecycleScope`, `viewModelScope`)
- ✅ Easy cancellation
- ✅ Structured concurrency
- ✅ Clean syntax

---

### 2. ExecutorService (Thread Pools)

**Java standard thread pool.**

```kotlin
import java.util.concurrent.Executors
import android.os.Handler
import android.os.Looper

class MainActivity : AppCompatActivity() {

    private val executor = Executors.newFixedThreadPool(4)
    private val mainHandler = Handler(Looper.getMainLooper())

    private fun loadData() {
        executor.execute {
            // Background work
            val data = fetchFromNetwork()

            // Update UI on main thread
            mainHandler.post {
                textView.text = data
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        executor.shutdown()
    }
}
```

**Advantages:**
- ✅ Reuses threads efficiently
- ✅ Configurable pool size
- ⚠️ No lifecycle awareness (manual cleanup needed)

---

### 3. Thread (Basic)

**Low-level Java threads.**

```kotlin
class MainActivity : AppCompatActivity() {

    private fun loadData() {
        Thread {
            // Background work
            val data = fetchFromNetwork()

            // Update UI on main thread
            runOnUiThread {
                textView.text = data
            }
        }.start()
    }
}
```

**Advantages:**
- ✅ Simple, no dependencies
- ⚠️ Creates new thread each time (inefficient)
- ⚠️ No lifecycle awareness

---

### 4. Handler + HandlerThread

**Message-based threading.**

```kotlin
import android.os.Handler
import android.os.HandlerThread
import android.os.Looper

class MainActivity : AppCompatActivity() {

    private val handlerThread = HandlerThread("BackgroundThread")
    private lateinit var backgroundHandler: Handler
    private val mainHandler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handlerThread.start()
        backgroundHandler = Handler(handlerThread.looper)
    }

    private fun loadData() {
        backgroundHandler.post {
            // Background work
            val data = fetchFromNetwork()

            // Update UI
            mainHandler.post {
                textView.text = data
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        handlerThread.quitSafely()
    }
}
```

**Advantages:**
- ✅ Sequential task processing
- ✅ Single background thread
- ⚠️ Verbose compared to Coroutines

---

### 5. WorkManager (Background Jobs)

**Deferrable, guaranteed background work.**

```kotlin
import androidx.work.*
import java.util.concurrent.TimeUnit

class SyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            syncDataWithServer()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// Schedule work
val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(syncRequest)
```

**Advantages:**
- ✅ Survives app restarts
- ✅ Constraint-based (network, battery, etc.)
- ✅ Guaranteed execution
- ⚠️ Not for immediate tasks (use Coroutines instead)

---

### 6. RxJava (Reactive Programming)

**Reactive streams for async operations.**

```kotlin
import io.reactivex.rxjava3.android.schedulers.AndroidSchedulers
import io.reactivex.rxjava3.schedulers.Schedulers

class UserRepository {

    fun getUser(userId: String): Single<User> {
        return Single.fromCallable {
            fetchUserFromNetwork(userId)
        }
        .subscribeOn(Schedulers.io())
        .observeOn(AndroidSchedulers.mainThread())
    }
}

// Usage
repository.getUser("123")
    .subscribe(
        { user -> displayUser(user) },
        { error -> showError(error) }
    )
```

**Advantages:**
- ✅ Powerful operators (map, filter, combine, etc.)
- ✅ Reactive paradigm
- ⚠️ Steep learning curve

---

### 7. LiveData (Lifecycle-Aware)

**Reactive data holder with lifecycle awareness.**

```kotlin
class UserViewModel : ViewModel() {

    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    fun loadUser(userId: String) {
        viewModelScope.launch(Dispatchers.IO) {
            val user = userRepository.getUser(userId)
            _user.postValue(user) // Thread-safe update
        }
    }
}

// Usage in Activity
class MainActivity : AppCompatActivity() {

    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.user.observe(this) { user ->
            // Automatically called on main thread
            textView.text = user.name
        }

        viewModel.loadUser("123")
    }
}
```

**Advantages:**
- ✅ Lifecycle-aware (no memory leaks)
- ✅ Automatic UI updates
- ✅ Thread-safe with `postValue()`

---

### 8. Flow (Kotlin Coroutines)

**Reactive streams in Kotlin.**

```kotlin
class UserRepository {

    fun getUserFlow(userId: String): Flow<User> = flow {
        val user = fetchUserFromNetwork(userId)
        emit(user)
    }.flowOn(Dispatchers.IO)
}

// Usage in ViewModel
class UserViewModel : ViewModel() {

    val user: StateFlow<User?> = userRepository.getUserFlow("123")
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = null
        )
}

// Usage in Activity
lifecycleScope.launch {
    viewModel.user.collect { user ->
        textView.text = user?.name ?: "Loading..."
    }
}
```

**Advantages:**
- ✅ Cold streams (lazy evaluation)
- ✅ Backpressure handling
- ✅ Integrates with Coroutines

---

## Tool Selection Guide

| Task Type | Recommended Tool | Alternative |
|-----------|-----------------|-------------|
| **Network request** | Coroutines + Retrofit | RxJava |
| **Database query** | Coroutines + Room | LiveData |
| **File I/O** | Coroutines (Dispatchers.IO) | ExecutorService |
| **Image processing** | Coroutines (Dispatchers.Default) | Thread |
| **Background job** | WorkManager | - |
| **Periodic sync** | WorkManager | - |
| **Real-time updates** | Flow | LiveData, RxJava |
| **One-time task** | Coroutines | Thread |

---

## Best Practices

### 1. Use Coroutines for Most Cases

```kotlin
// ✅ GOOD
lifecycleScope.launch(Dispatchers.IO) {
    val data = repository.fetchData()
    withContext(Dispatchers.Main) {
        updateUI(data)
    }
}
```

### 2. Use WorkManager for Background Jobs

```kotlin
// ✅ GOOD: For work that must complete even if app is killed
val uploadWork = OneTimeWorkRequestBuilder<UploadWorker>().build()
WorkManager.getInstance(context).enqueue(uploadWork)
```

### 3. Don't Block the UI Thread

```kotlin
// ❌ BAD
val data = database.userDao().getAllUsers() // Blocks UI

// ✅ GOOD
lifecycleScope.launch(Dispatchers.IO) {
    val data = database.userDao().getAllUsers()
}
```

### 4. Choose the Right Dispatcher

```kotlin
// CPU-intensive work
Dispatchers.Default // For calculations, parsing

// I/O operations
Dispatchers.IO // For network, database, file I/O

// UI updates
Dispatchers.Main // For updating views
```

---

## Summary

**Why multithreading?**
- ✅ Keep UI responsive
- ✅ Prevent ANR (Application Not Responding)
- ✅ Improve performance
- ✅ Handle heavy tasks (network, database, file I/O)

**Recommended tools:**
1. **Kotlin Coroutines** - default choice for most async tasks
2. **WorkManager** - guaranteed background jobs
3. **ExecutorService** - Java thread pools
4. **Flow** - reactive streams
5. **LiveData** - lifecycle-aware data

**Avoid:**
- ❌ Running heavy tasks on UI thread
- ❌ Using AsyncTask (deprecated)

**Rule of thumb:**
> If an operation takes more than **16ms** (one frame), run it on a background thread.

---

## Ответ

**Многопоточность** позволяет выполнять **тяжёлые задачи** без блокировки UI потока.

**Основная цель:** Сохранить отзывчивость UI, перенося работу в фоновые потоки.

**Инструменты в Android:**
1. **Kotlin Coroutines** (современный, рекомендуется)
2. **ExecutorService** (пулы потоков)
3. **Thread** (базовые Java потоки)
4. **Handler** + **HandlerThread** (на основе сообщений)
5. **WorkManager** (фоновые задачи)
6. **RxJava** (реактивное программирование)
7. **LiveData** (данные с учётом жизненного цикла)
8. **Flow** (реактивные потоки)

**Рекомендуемый инструмент:**
```kotlin
// ✅ Kotlin Coroutines для большинства случаев
lifecycleScope.launch(Dispatchers.IO) {
    val data = repository.fetchData()
    withContext(Dispatchers.Main) {
        updateUI(data)
    }
}

// ✅ WorkManager для гарантированных фоновых задач
val work = OneTimeWorkRequestBuilder<UploadWorker>().build()
WorkManager.getInstance(context).enqueue(work)
```

**Зачем нужна многопоточность:**
- ✅ UI остается отзывчивым
- ✅ Предотвращает ANR (приложение не отвечает)
- ✅ Улучшает производительность
- ✅ Обрабатывает тяжёлые задачи (сеть, БД, файлы)

**Правило:**
> Если операция занимает > **16ms** (один кадр), выполняйте её в фоновом потоке.

