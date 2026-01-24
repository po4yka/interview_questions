---
anki_cards:
- slug: q-coroutines-threads-android-differences--kotlin--easy-0-en
  language: en
  anki_id: 1768326294180
  synced_at: '2026-01-23T17:03:51.626108'
- slug: q-coroutines-threads-android-differences--kotlin--easy-0-ru
  language: ru
  anki_id: 1768326294206
  synced_at: '2026-01-23T17:03:51.626947'
---
# Question (EN)
> What are the key differences between coroutines and threads in Android development?
## Ответ (RU)

**Корутины и потоки** оба обеспечивают конкурентное программирование, но корутины **легковесные**, **проще в использовании** и **лучше интегрированы** с Android стеком.

### Основные Различия

| Аспект | Потоки | Корутины |
|--------|---------|-----------|
| **Вес** | Тяжеловесные (обычно 0.5-2 МБ стека на поток) | Легковесные (на порядки меньше памяти на корутину) |
| **Стоимость Создания** | Дорогая (вызов ядра ОС) | Дешевая (выделение объектов в user-space) |
| **Переключение Контекста** | Дорогое (уровень ядра) | Дешевое (организуется в user-space поверх потоков) |
| **Количество** | Практически ограничено (обычно сотни/тысячи) | Намного больше при тех же ресурсах (десятки/сотни тысяч) |
| **Отмена** | Кооперативная через interrupt, требует ручной поддержки | Кооперативная, встроена в API (isActive, cancel, cancellation exceptions) |
| **Безопасность Main Потока** | Требуется ручное переключение | Упрощена с диспетчерами (Dispatchers.Main и т.п.) |
| **Память** | Фиксированный стек на поток | Динамическая, низкие накладные расходы на корутину |
| **Обработка Исключений** | Через UncaughtExceptionHandler и try/catch в потоках | Структурированная с CoroutineScope и SupervisorJob |
| **Жизненный Цикл** | Ручное управление | Жизненный цикл можно привязать к scope (viewModelScope, lifecycleScope) |

### Вес: Легковесные vs Тяжеловесные

**Потоки - Тяжеловесные**:
```kotlin
// - ДОРОГО: Создание множества потоков
fun loadData() {
    // Каждый поток обычно резервирует значимый объем памяти под стек
    repeat(10000) { i ->
        Thread {
            val data = fetchData(i)
            runOnUiThread { updateUI(data) }
        }.start()
    }
    // Такое количество потоков с высокой вероятностью приведет к OOM или серьезному падению производительности.
}
```

**Корутины - Легковесные**:
```kotlin
// - ДЕШЕВО: Создание множества корутин
fun loadData() {
    lifecycleScope.launch { // в Activity/Fragment по умолчанию запускает на Dispatchers.Main
        repeat(10000) { i ->
            launch { // наследует Dispatcher родителя (Main)
                val data = withContext(Dispatchers.IO) {
                    fetchData(i)
                }
                updateUI(data) // Выполняется на main-потоке
            }
        }
    }
    // Тысячи корутин при разумной работе не приводят к таким же накладным расходам, как тысячи потоков.
}
```

**Влияние на Память**:
- Поток: заметные фиксированные накладные расходы на каждый поток → большое количество потоков быстро исчерпывает память.
- Корутина: гораздо меньшие накладные расходы → можно обрабатывать существенно больше конкурентных задач поверх ограниченного пула потоков.

### Android-специфические преимущества

**1. Безопасность Main потока**:
```kotlin
// Корутины упрощают возвращение на main-поток
lifecycleScope.launch { // Main dispatcher
    val data = withContext(Dispatchers.IO) { loadData() }
    updateUI(data) // Безопасно - снова на main-потоке
}
```

**2. Интеграция с жизненным циклом**:
```kotlin
// Автоматическая отмена при использовании lifecycle-aware scopes
viewModelScope.launch { ... } // Отменяется в onCleared()
lifecycleScope.launch { ... } // Отменяется когда соответствующий LifecycleOwner уничтожен
```

**3. Структурированная конкурентность**:
```kotlin
// Отношение родитель-потомок помогает избежать утечек и "висящих" задач
lifecycleScope.launch {
    val job1 = launch { work1() }
    val job2 = launch { work2() }
    // Оба будут отменены, если будет отменен родительский scope
}
```

### Сравнение кода: Реальный пример

**Версия с потоками**:
```kotlin
// - СЛОЖНЕЕ: Сетевой вызов на потоках
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

// Использование
repository.getUser { user ->
    if (user != null) {
        updateUI(user)
    }
}
```

**Версия с корутинами**:
```kotlin
// - ПРОЩЕ: Сетевой вызов на корутинах
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

// Использование
lifecycleScope.launch {
    val user = repository.getUser()
    if (user != null) {
        updateUI(user)
    }
}
```

### Когда использовать каждый

**Используйте Потоки Когда**:
- Нужно взаимодействовать с Java API, которые явно требуют управления потоками.
- Для низкоуровневых задач, где необходим прямой контроль над потоками.

**Используйте Корутины Когда** (типичный выбор на Android):
- Сетевые вызовы
- Операции с базой данных
- Файловый I/O
- Обработка изображений
- Любая асинхронная работа в Android-приложении
- Обновление UI после фоновой работы
- Сложные конкурентные операции и координация задач

### Резюме

**Потоки**:
- Тяжеловесные накладные расходы на память
- Дорогое переключение контекста
- Ограниченное количество на устройство
- Отмена через interrupt требует дисциплины и ручной поддержки
- Ручное управление жизненным циклом и переключением на main-поток

**Корутины**:
- Легковесные
- Более дешевое планирование и переключение на уровне библиотеки
- Позволяют запускать существенно больше задач поверх фиксированного пула потоков
- Встроенная кооперативная отмена
- Удобная интеграция с lifecycleScope/viewModelScope и структурированной конкурентностью
- Упрощенное переключение диспетчеров (например, IO ⇄ Main)

**Ключевой Вывод**: На Android для асинхронных операций обычно предпочтительнее использовать корутины поверх Dispatchers (особенно с lifecycleScope/viewModelScope), так как это легче, безопаснее и лучше интегрируется с компонентами платформы, чем ручное управление потоками.

---

## Answer (EN)

**Coroutines and threads** both enable concurrent programming, but coroutines are **lightweight**, **easier to work with**, and **better integrated** with the Android stack.

### Core Differences

| Aspect | Threads | Coroutines |
|--------|---------|-----------|
| **Weight** | Heavyweight (typically ~0.5-2 MB stack per thread) | Lightweight (orders of magnitude less memory per coroutine) |
| **Creation Cost** | Expensive (OS kernel involvement) | Cheap (user-space object allocation) |
| **`Context` Switching** | Expensive (kernel-level scheduling) | Cheaper (managed in user-space on top of threads) |
| **Number** | Practically limited (hundreds/thousands typical) | Can run far more tasks for same resources (tens/hundreds of thousands) |
| **Cancellation** | Cooperative via interrupt, requires manual handling | Cooperative, built into API (isActive, cancel, cancellation exceptions) |
| **Main `Thread` Safety** | Manual switching required | Simplified via dispatchers (Dispatchers.Main, etc.) |
| **Memory** | Fixed stack per thread | Dynamic, low per-coroutine overhead |
| **Exception Handling** | Via UncaughtExceptionHandler and try/catch in threads | Structured via CoroutineScope and SupervisorJob |
| **`Lifecycle`** | Manual management | Can be lifecycle-aware when using scopes (viewModelScope, lifecycleScope) |

### Weight: Lightweight vs Heavyweight

**Threads - Heavyweight**:
```kotlin
// - EXPENSIVE: Creating many threads
fun loadData() {
    // Each thread reserves a significant stack
    repeat(10000) { i ->
        Thread {
            val data = fetchData(i)
            runOnUiThread { updateUI(data) }
        }.start()
    }
    // Such a large number of threads is likely to cause OOM or severe slowdown.
}
```

**Coroutines - Lightweight**:
```kotlin
// - CHEAP: Creating many coroutines
fun loadData() {
    lifecycleScope.launch { // in Activity/Fragment defaults to Dispatchers.Main
        repeat(10000) { i ->
            launch { // inherits parent's dispatcher (Main)
                val data = withContext(Dispatchers.IO) {
                    fetchData(i)
                }
                updateUI(data) // Runs on main thread
            }
        }
    }
    // Thousands of coroutines are feasible without the same overhead as thousands of threads.
}
```

**Memory Impact**:
- Threads: significant fixed overhead per thread → many threads quickly exhaust memory.
- Coroutines: much smaller overhead → can schedule many more concurrent tasks on a limited thread pool.

### Context Switching Cost

**Threads - Expensive Switching**:
```kotlin
// Thread context switch involves kernel-level scheduling and saving/restoring thread state.
Thread {
    val data = loadData()

    runOnUiThread {
        updateUI(data)
    }
}.start()
```

**Coroutines - Cheaper Switching**:
```kotlin
// Coroutine dispatching is implemented in user-space on top of a few threads.
// Switching between coroutine continuations avoids creating new OS threads.

lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) {
        loadData()
    }

    updateUI(data) // Back on main dispatcher, no explicit runOnUiThread needed
}
```

### Main Thread Safety

**Threads - Manual Switching**:
```kotlin
// - VERBOSE: Manual thread management
class UserViewModel {
    fun loadUser() {
        Thread {
            val user = repository.getUser()

            // Must manually switch to main thread
            Handler(Looper.getMainLooper()).post {
                _userData.value = user
            }
        }.start()
    }
}
```

**Coroutines - Simplified Switching**:
```kotlin
// - CLEAN: Dispatcher-based switching
class UserViewModel : ViewModel() {
    fun loadUser() {
        viewModelScope.launch {
            val user = withContext(Dispatchers.IO) {
                repository.getUser()
            }

            _userData.value = user // On main thread when using viewModelScope + Main dispatcher
        }
    }
}
```

### Cancellation

**Threads - Manual Cooperative Cancellation**:
```kotlin
class DataLoader {
    private var thread: Thread? = null

    fun loadData() {
        thread = Thread {
            try {
                while (!Thread.currentThread().isInterrupted) {
                    val data = fetchData()
                    // Periodically check interruption to stop safely
                    if (Thread.interrupted()) break
                }
            } catch (e: InterruptedException) {
                // Handle interruption
            }
        }
        thread?.start()
    }

    fun cancel() {
        thread?.interrupt() // Requires code inside thread to cooperate to remain safe
    }
}
```

**Coroutines - Built-in Cooperative Cancellation**:
```kotlin
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
        job?.cancel() // Structured, predictable cancellation
    }
}
```

### Lifecycle Management

**Threads - Manual Management**:
```kotlin
// - LEAK RISK: Must manually track and cancel threads
class MyActivity : AppCompatActivity() {
    private val activeThreads = mutableListOf<Thread>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val thread = Thread {
            repeat(1000) {
                Thread.sleep(1000)
                // If Activity is destroyed, this may keep running unless interrupted
            }
        }
        activeThreads.add(thread)
        thread.start()
    }

    override fun onDestroy() {
        super.onDestroy()
        activeThreads.forEach { it.interrupt() }
        activeThreads.clear()
    }
}
```

**Coroutines - `Lifecycle`-Aware with Proper Scope**:
```kotlin
// - REDUCED LEAK RISK: lifecycleScope ties coroutines to Activity/Fragment lifecycle
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            repeat(1000) {
                delay(1000)
                // This coroutine is cancelled automatically when Activity is destroyed
            }
        }
    }
}
```

### Performance Comparison

**Benchmark: 10,000 Concurrent Tasks (Illustrative)**

```kotlin
// Threads - often leads to OOM or severe slowdown on typical devices
fun threadBenchmark() {
    repeat(10000) {
        Thread {
            Thread.sleep(1000)
            println("Done")
        }.start()
    }
}

// Coroutines - can handle many logical tasks on a limited thread pool
suspend fun coroutineBenchmark() {
    coroutineScope {
        repeat(10000) {
            launch {
                delay(1000)
                println("Done")
            }
        }
    }
}
```

**Typical Results**:
- Threads: Very high overhead; may hit OutOfMemoryError or heavy contention on many devices.
- Coroutines: Can complete with much lower memory footprint because they share a bounded pool of threads.

### Android-Specific Benefits

**1. Main `Thread` Safety**:
```kotlin
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) { loadData() }
    updateUI(data) // Back on main thread via Dispatchers.Main
}
```

**2. `Lifecycle` Integration**:
```kotlin
viewModelScope.launch { ... } // Cancelled in onCleared()
lifecycleScope.launch { ... } // Cancelled when LifecycleOwner is destroyed
```

**3. Structured Concurrency**:
```kotlin
lifecycleScope.launch {
    val job1 = launch { work1() }
    val job2 = launch { work2() }
    // Both cancelled when parent scope is cancelled
}
```

### Code Comparison: Real Example

**`Thread` Version**:
```kotlin
// - MORE COMPLEX: Thread-based network call
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

**`Coroutine` Version**:
```kotlin
// - SIMPLER: Coroutine-based network call
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
- Interacting with Java APIs that explicitly require managing threads.
- Low-level system or library code where you need full control over thread behavior.

**Use Coroutines When** (the default on Android):
- Network calls
- `Database` operations
- File I/O
- Image processing
- Any async work in an Android app
- UI updates coordinated with background work
- Complex concurrent flows

### Summary

**Threads**:
- Heavyweight per-thread memory and scheduling cost
- Expensive context switches at OS level
- Practically limited in number
- Cancellation via interrupt is cooperative but manual
- Manual lifecycle and main-thread coordination

**Coroutines**:
- Lightweight abstractions over thread pools
- Cheaper, user-space scheduling and context switching
- Support a far larger number of concurrent tasks
- Built-in cooperative cancellation and structured concurrency
- `Lifecycle`-aware when using viewModelScope/lifecycleScope
- Clear dispatcher-based main/background switching

**Key Takeaway**: On Android, prefer coroutines (with proper scopes and dispatchers) over manually managed threads for most async operations. They are lighter, safer when used correctly, and integrate seamlessly with Android lifecycle components.

---

## Follow-ups

- What are the key differences between this and Java's concurrency model?
- When would you still choose raw threads instead of coroutines in Android?
- What are common pitfalls when using coroutines on Android (e.g., missing scopes, blocking calls in coroutines)?

## References

- [Coroutines vs Threads - Kotlin Docs](https://kotlinlang.org/docs/coroutines-basics.html)
- [Threading on Android - Android Developers](https://developer.android.com/guide/background/threading)
- [Coroutines Best Practices - Android Developers](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)

---

**Source**: Kotlin Coroutines Interview Questions for Android Developers PDF

---

## Related Questions

### Hub
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Comprehensive coroutines introduction

### Same Level (Easy)
- [[q-what-is-coroutine--kotlin--easy]] - Basic coroutine concepts
- [[q-coroutine-builders-basics--kotlin--easy]] - launch, async, runBlocking
- [[q-coroutine-scope-basics--kotlin--easy]] - CoroutineScope fundamentals
- [[q-coroutine-delay-vs-thread-sleep--kotlin--easy]] - delay() vs `Thread`.sleep()

### Next Steps (Medium)
- [[q-suspend-functions-basics--kotlin--easy]] - Understanding suspend functions
- [[q-coroutine-dispatchers--kotlin--medium]] - `Coroutine` dispatchers overview
- [[q-coroutinescope-vs-coroutinecontext--kotlin--medium]] - Scope vs `Context`
