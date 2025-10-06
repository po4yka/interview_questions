---
id: 20251006-coroutines-threads-android
title: Coroutines vs Threads on Android / Корутины vs Потоки на Android
topic: kotlin
subtopics:
  - coroutines
  - threads
  - performance
  - android
difficulty: easy
language_tags:
  - en
  - ru
original_language: en
status: draft
source: Kotlin Coroutines Interview Questions PDF
tags:
  - kotlin
  - coroutines
  - threads
  - performance
  - android
  - comparison
  - difficulty/easy
---

# Question (EN)
> What are the key differences between coroutines and threads in Android development?

# Вопрос (RU)
> Каковы ключевые различия между корутинами и потоками в Android разработке?

---

## Answer (EN)

**Coroutines and threads** both enable concurrent programming, but coroutines are **lightweight**, **easier to use**, and **safer** for Android development.

### Core Differences

| Aspect | Threads | Coroutines |
|--------|---------|-----------|
| **Weight** | Heavyweight (1-2 MB per thread) | Lightweight (bytes per coroutine) |
| **Creation Cost** | Expensive (OS kernel call) | Cheap (object allocation) |
| **Context Switching** | Expensive (kernel-level) | Cheap (user-level) |
| **Number** | Limited (~thousands) | Virtually unlimited (millions) |
| **Cancellation** | Hard (interrupt, unsafe) | Easy (cooperative, safe) |
| **Main Thread Safety** | Manual switching required | Built-in with dispatchers |
| **Memory** | Fixed stack (1-2 MB) | Dynamic, minimal overhead |
| **Exception Handling** | UncaughtExceptionHandler | Structured with scope |
| **Lifecycle** | Manual management | Automatic with scopes |

### Weight: Lightweight vs Heavyweight

**Threads - Heavyweight**:
```kotlin
// ❌ EXPENSIVE: Creating many threads
fun loadData() {
    // Each thread costs ~1-2 MB of memory
    repeat(10000) { i ->
        Thread {
            val data = fetchData(i)
            runOnUiThread { updateUI(data) }
        }.start()
    }
    // 10,000 threads = ~10-20 GB memory! → Crash!
}
```

**Coroutines - Lightweight**:
```kotlin
// ✅ CHEAP: Creating many coroutines
fun loadData() {
    lifecycleScope.launch {
        // Each coroutine costs bytes, not megabytes
        repeat(10000) { i ->
            launch {
                val data = fetchData(i)
                updateUI(data) // Already on main thread
            }
        }
    }
    // 10,000 coroutines = ~few MB memory → No problem!
}
```

**Memory Impact**:
- Thread: ~1-2 MB each → 1000 threads = ~1-2 GB
- Coroutine: ~bytes each → 1,000,000 coroutines = ~few MB

### Context Switching Cost

**Threads - Expensive Switching**:
```kotlin
// Context switch involves:
// 1. Save thread state (registers, stack pointer)
// 2. Kernel mode switch
// 3. Schedule next thread
// 4. Restore thread state
// Time: ~1-10 microseconds per switch

Thread {
    // Work on background thread
    val data = loadData()

    runOnUiThread {
        // Expensive context switch to main thread
        updateUI(data)
    }
}.start()
```

**Coroutines - Cheap Switching**:
```kotlin
// Context switch is just a function call
// No kernel involvement
// Time: ~nanoseconds

lifecycleScope.launch {
    // Work on background dispatcher
    val data = withContext(Dispatchers.IO) {
        loadData()
    }

    // Cheap switch to main dispatcher
    updateUI(data) // No runOnUiThread needed!
}
```

### Main Thread Safety

**Threads - Manual Switching**:
```kotlin
// ❌ VERBOSE: Manual thread management
class UserViewModel {
    fun loadUser() {
        Thread {
            // Background thread
            val user = repository.getUser()

            // Must manually switch to main thread
            Handler(Looper.getMainLooper()).post {
                _userData.value = user
            }

            // Or
            runOnUiThread {
                _userData.value = user
            }
        }.start()
    }
}
```

**Coroutines - Automatic Switching**:
```kotlin
// ✅ CLEAN: Automatic dispatcher handling
class UserViewModel : ViewModel() {
    fun loadUser() {
        viewModelScope.launch {
            // IO work on background dispatcher
            val user = withContext(Dispatchers.IO) {
                repository.getUser()
            }

            // Automatically switches back to main dispatcher
            _userData.value = user // Safe on main thread!
        }
    }
}
```

### Cancellation

**Threads - Hard to Cancel**:
```kotlin
// ❌ DANGEROUS: Thread interruption is risky
class DataLoader {
    private var thread: Thread? = null

    fun loadData() {
        thread = Thread {
            try {
                while (!Thread.currentThread().isInterrupted) {
                    // Work
                    val data = fetchData()

                    // Check interruption manually
                    if (Thread.interrupted()) break
                }
            } catch (e: InterruptedException) {
                // Handle interruption
            }
        }
        thread?.start()
    }

    fun cancel() {
        thread?.interrupt() // Unsafe - can corrupt state!
    }
}
```

**Coroutines - Easy to Cancel**:
```kotlin
// ✅ SAFE: Cooperative cancellation
class DataLoader {
    private var job: Job? = null

    fun loadData() {
        job = lifecycleScope.launch {
            while (isActive) { // Built-in cancellation check
                val data = fetchData()
                updateUI(data)
            }
        }
    }

    fun cancel() {
        job?.cancel() // Safe, predictable cancellation
    }
}
```

### Lifecycle Management

**Threads - Manual Management**:
```kotlin
// ❌ LEAK RISK: Must manually track and cancel threads
class MyActivity : AppCompatActivity() {
    private val activeThreads = mutableListOf<Thread>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val thread = Thread {
            // Long-running work
            repeat(1000) {
                Thread.sleep(1000)
                // If Activity destroyed, this keeps running!
            }
        }
        activeThreads.add(thread)
        thread.start()
    }

    override fun onDestroy() {
        super.onDestroy()
        // Must manually cancel all threads
        activeThreads.forEach { it.interrupt() }
        activeThreads.clear()
    }
}
```

**Coroutines - Automatic Management**:
```kotlin
// ✅ NO LEAKS: Automatic lifecycle management
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Long-running work
            repeat(1000) {
                delay(1000)
                // Automatically cancelled when Activity destroyed!
            }
        }
    }

    // No onDestroy needed - automatic cleanup!
}
```

### Performance Comparison

**Benchmark: 10,000 Concurrent Tasks**

```kotlin
// Threads - Crash or severe slowdown
fun threadBenchmark() {
    val startTime = System.currentTimeMillis()

    repeat(10000) {
        Thread {
            Thread.sleep(1000)
            println("Done")
        }.start()
    }
    // Result: OutOfMemoryError or extreme slowdown
}

// Coroutines - No problem
suspend fun coroutineBenchmark() {
    val startTime = System.currentTimeMillis()

    coroutineScope {
        repeat(10000) {
            launch {
                delay(1000)
                println("Done")
            }
        }
    }
    // Result: ~1 second, minimal memory usage
}
```

**Results**:
- Threads: Crash with OutOfMemoryError (too many threads)
- Coroutines: Complete successfully in ~1 second

### Android-Specific Benefits

**1. Main Thread Safety**:
```kotlin
// Coroutines make it easy to stay main-safe
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) { loadData() }
    updateUI(data) // Safe - back on main thread
}
```

**2. Lifecycle Integration**:
```kotlin
// Automatic cancellation with lifecycle
viewModelScope.launch { ... } // Cancelled in onCleared()
lifecycleScope.launch { ... } // Cancelled when lifecycle destroyed
```

**3. Structured Concurrency**:
```kotlin
// Parent-child relationship prevents leaks
lifecycleScope.launch {
    val job1 = launch { work1() }
    val job2 = launch { work2() }
    // Both cancelled if parent cancelled
}
```

### Code Comparison: Real Example

**Thread Version**:
```kotlin
// ❌ COMPLEX: Thread-based network call
class UserRepository {
    fun getUser(callback: (User?) -> Unit) {
        Thread {
            try {
                val response = api.getUser()
                val user = parseUser(response)

                Handler(Looper.getMainLooper()).post {
                    callback(user)
                }
            } catch (e: Exception) {
                Handler(Looper.getMainLooper()).post {
                    callback(null)
                }
            }
        }.start()
    }
}

// Usage
repository.getUser { user ->
    if (user != null) {
        updateUI(user)
    }
}
```

**Coroutine Version**:
```kotlin
// ✅ SIMPLE: Coroutine-based network call
class UserRepository {
    suspend fun getUser(): User? {
        return withContext(Dispatchers.IO) {
            try {
                val response = api.getUser()
                parseUser(response)
            } catch (e: Exception) {
                null
            }
        }
    }
}

// Usage
lifecycleScope.launch {
    val user = repository.getUser()
    if (user != null) {
        updateUI(user)
    }
}
```

### When to Use Each

**Use Threads When**:
- ⚠️ Working with Java libraries that require threads
- ⚠️ Long-running blocking operations (rare - use WorkManager instead)
- ⚠️ Low-level system programming

**Use Coroutines When** (Almost Always on Android):
- ✅ Network calls
- ✅ Database operations
- ✅ File I/O
- ✅ Image processing
- ✅ Any async work in Android app
- ✅ UI updates with background work
- ✅ Complex concurrent operations

### Summary

**Threads**:
- ❌ Heavyweight (1-2 MB each)
- ❌ Expensive context switching
- ❌ Limited number (~thousands)
- ❌ Hard to cancel safely
- ❌ Manual lifecycle management
- ❌ Verbose thread switching
- ❌ High memory usage

**Coroutines**:
- ✅ Lightweight (bytes each)
- ✅ Cheap context switching
- ✅ Virtually unlimited (millions)
- ✅ Easy, safe cancellation
- ✅ Automatic lifecycle management
- ✅ Clean dispatcher switching
- ✅ Low memory usage

**Key Takeaway**: On Android, **always prefer coroutines over threads** for async operations. Coroutines are lighter, safer, and integrate seamlessly with Android lifecycle components.

---

## Ответ (RU)

**Корутины и потоки** оба обеспечивают конкурентное программирование, но корутины **легковесные**, **проще в использовании** и **безопаснее** для Android разработки.

### Основные Различия

| Аспект | Потоки | Корутины |
|--------|---------|-----------|
| **Вес** | Тяжеловесные (1-2 МБ на поток) | Легковесные (байты на корутину) |
| **Стоимость Создания** | Дорогая (вызов ядра ОС) | Дешевая (выделение объекта) |
| **Переключение Контекста** | Дорогое (уровень ядра) | Дешевое (уровень пользователя) |
| **Количество** | Ограничено (~тысячи) | Практически неограничено (миллионы) |
| **Отмена** | Сложная (прерывание, небезопасно) | Легкая (кооперативная, безопасная) |
| **Безопасность Main Потока** | Требуется ручное переключение | Встроенная с диспетчерами |
| **Память** | Фиксированный стек (1-2 МБ) | Динамическая, минимальные издержки |
| **Обработка Исключений** | UncaughtExceptionHandler | Структурированная со scope |
| **Жизненный Цикл** | Ручное управление | Автоматическое со scopes |

### Вес: Легковесные vs Тяжеловесные

**Потоки - Тяжеловесные**:
```kotlin
// ❌ ДОРОГО: Создание множества потоков
fun loadData() {
    // Каждый поток стоит ~1-2 МБ памяти
    repeat(10000) { i ->
        Thread {
            val data = fetchData(i)
            runOnUiThread { updateUI(data) }
        }.start()
    }
    // 10,000 потоков = ~10-20 ГБ памяти! → Крэш!
}
```

**Корутины - Легковесные**:
```kotlin
// ✅ ДЕШЕВО: Создание множества корутин
fun loadData() {
    lifecycleScope.launch {
        // Каждая корутина стоит байты, а не мегабайты
        repeat(10000) { i ->
            launch {
                val data = fetchData(i)
                updateUI(data) // Уже в main потоке
            }
        }
    }
    // 10,000 корутин = ~несколько МБ памяти → Без проблем!
}
```

**Влияние на Память**:
- Поток: ~1-2 МБ каждый → 1000 потоков = ~1-2 ГБ
- Корутина: ~байты каждая → 1,000,000 корутин = ~несколько МБ

### Резюме

**Потоки**:
- ❌ Тяжеловесные (1-2 МБ каждый)
- ❌ Дорогое переключение контекста
- ❌ Ограниченное количество (~тысячи)
- ❌ Сложно безопасно отменить
- ❌ Ручное управление жизненным циклом
- ❌ Многословное переключение потоков
- ❌ Высокое использование памяти

**Корутины**:
- ✅ Легковесные (байты каждая)
- ✅ Дешевое переключение контекста
- ✅ Практически неограничены (миллионы)
- ✅ Легкая, безопасная отмена
- ✅ Автоматическое управление жизненным циклом
- ✅ Чистое переключение диспетчеров
- ✅ Низкое использование памяти

**Ключевой Вывод**: На Android **всегда предпочитайте корутины потокам** для асинхронных операций. Корутины легче, безопаснее и бесшовно интегрируются с компонентами жизненного цикла Android.

---

## References

- [Coroutines vs Threads - Kotlin Docs](https://kotlinlang.org/docs/coroutines-basics.html)
- [Threading on Android - Android Developers](https://developer.android.com/guide/background/threading)
- [Coroutines Performance - Android Developers](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)

---

**Source**: Kotlin Coroutines Interview Questions for Android Developers PDF
