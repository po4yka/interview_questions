---
id: 20251016-174636
title: Coroutines vs Threads on Android / Корутины vs Потоки на Android
topic: kotlin
difficulty: easy
status: draft
created: 2025-10-15
tags: - kotlin
  - coroutines
  - threads
  - performance
  - android
  - comparison
  - difficulty/easy
language_tags:   - en
  - ru
original_language: en
source: Kotlin Coroutines Interview Questions PDF
subtopics:   - coroutines
  - threads
  - performance
  - android
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
// - EXPENSIVE: Creating many threads
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
// - CHEAP: Creating many coroutines
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
// - VERBOSE: Manual thread management
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
// - CLEAN: Automatic dispatcher handling
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
// - DANGEROUS: Thread interruption is risky
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
// - SAFE: Cooperative cancellation
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
// - LEAK RISK: Must manually track and cancel threads
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
// - NO LEAKS: Automatic lifecycle management
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
// - COMPLEX: Thread-based network call
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
// - SIMPLE: Coroutine-based network call
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
- WARNING: Working with Java libraries that require threads
- WARNING: Long-running blocking operations (rare - use WorkManager instead)
- WARNING: Low-level system programming

**Use Coroutines When** (Almost Always on Android):
- - Network calls
- - Database operations
- - File I/O
- - Image processing
- - Any async work in Android app
- - UI updates with background work
- - Complex concurrent operations

### Summary

**Threads**:
- - Heavyweight (1-2 MB each)
- - Expensive context switching
- - Limited number (~thousands)
- - Hard to cancel safely
- - Manual lifecycle management
- - Verbose thread switching
- - High memory usage

**Coroutines**:
- - Lightweight (bytes each)
- - Cheap context switching
- - Virtually unlimited (millions)
- - Easy, safe cancellation
- - Automatic lifecycle management
- - Clean dispatcher switching
- - Low memory usage

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
// - ДОРОГО: Создание множества потоков
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
// - ДЕШЕВО: Создание множества корутин
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

### Android-специфические преимущества

**1. Безопасность Main потока**:
```kotlin
// Корутины делают легким сохранение main-safe
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) { loadData() }
    updateUI(data) // Безопасно - обратно на main потоке
}
```

**2. Интеграция с жизненным циклом**:
```kotlin
// Автоматическая отмена с жизненным циклом
viewModelScope.launch { ... } // Отменяется в onCleared()
lifecycleScope.launch { ... } // Отменяется когда жизненный цикл уничтожен
```

**3. Структурированная конкурентность**:
```kotlin
// Отношение родитель-потомок предотвращает утечки
lifecycleScope.launch {
    val job1 = launch { work1() }
    val job2 = launch { work2() }
    // Оба отменяются если родитель отменен
}
```

### Сравнение кода: Реальный пример

**Версия с потоками**:
```kotlin
// - СЛОЖНО: Сетевой вызов на потоках
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
// - ПРОСТО: Сетевой вызов на корутинах
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
- WARNING: Работа с Java библиотеками, которые требуют потоки
- WARNING: Долгие блокирующие операции (редко - используйте WorkManager вместо этого)
- WARNING: Низкоуровневое системное программирование

**Используйте Корутины Когда** (Почти Всегда на Android):
- - Сетевые вызовы
- - Операции с базой данных
- - Файловый I/O
- - Обработка изображений
- - Любая async работа в Android приложении
- - Обновления UI с фоновой работой
- - Сложные конкурентные операции

### Резюме

**Потоки**:
- - Тяжеловесные (1-2 МБ каждый)
- - Дорогое переключение контекста
- - Ограниченное количество (~тысячи)
- - Сложно безопасно отменить
- - Ручное управление жизненным циклом
- - Многословное переключение потоков
- - Высокое использование памяти

**Корутины**:
- - Легковесные (байты каждая)
- - Дешевое переключение контекста
- - Практически неограничены (миллионы)
- - Легкая, безопасная отмена
- - Автоматическое управление жизненным циклом
- - Чистое переключение диспетчеров
- - Низкое использование памяти

### Переключение контекста: Стоимость

**Потоки - Дорогое переключение**:
```kotlin
// Переключение контекста включает:
// 1. Сохранение состояния потока (регистры, указатель стека)
// 2. Переключение в режим ядра
// 3. Планирование следующего потока
// 4. Восстановление состояния потока
// Время: ~1-10 микросекунд на переключение

Thread {
    // Работа в фоновом потоке
    val data = loadData()

    runOnUiThread {
        // Дорогое переключение контекста на main поток
        updateUI(data)
    }
}.start()
```

**Корутины - Дешевое переключение**:
```kotlin
// Переключение контекста это просто вызов функции
// Нет вовлечения ядра
// Время: ~наносекунды

lifecycleScope.launch {
    // Работа на background диспетчере
    val data = withContext(Dispatchers.IO) {
        loadData()
    }

    // Дешевое переключение на main диспетчер
    updateUI(data) // runOnUiThread не нужен!
}
```

### Безопасность Main потока

**Потоки - Ручное переключение**:
```kotlin
// - МНОГОСЛОВНО: Ручное управление потоками
class UserViewModel {
    fun loadUser() {
        Thread {
            // Фоновый поток
            val user = repository.getUser()

            // Нужно вручную переключиться на main поток
            Handler(Looper.getMainLooper()).post {
                _userData.value = user
            }

            // Или
            runOnUiThread {
                _userData.value = user
            }
        }.start()
    }
}
```

**Корутины - Автоматическое переключение**:
```kotlin
// - ЧИСТО: Автоматическая обработка диспетчером
class UserViewModel : ViewModel() {
    fun loadUser() {
        viewModelScope.launch {
            // IO работа на background диспетчере
            val user = withContext(Dispatchers.IO) {
                repository.getUser()
            }

            // Автоматически переключается обратно на main диспетчер
            _userData.value = user // Безопасно на main потоке!
        }
    }
}
```

### Отмена

**Потоки - Сложно отменить**:
```kotlin
// - ОПАСНО: Прерывание потока рискованно
class DataLoader {
    private var thread: Thread? = null

    fun loadData() {
        thread = Thread {
            try {
                while (!Thread.currentThread().isInterrupted) {
                    // Работа
                    val data = fetchData()

                    // Проверить прерывание вручную
                    if (Thread.interrupted()) break
                }
            } catch (e: InterruptedException) {
                // Обработать прерывание
            }
        }
        thread?.start()
    }

    fun cancel() {
        thread?.interrupt() // Небезопасно - может повредить состояние!
    }
}
```

**Корутины - Легко отменить**:
```kotlin
// - БЕЗОПАСНО: Кооперативная отмена
class DataLoader {
    private var job: Job? = null

    fun loadData() {
        job = lifecycleScope.launch {
            while (isActive) { // Встроенная проверка отмены
                val data = fetchData()
                updateUI(data)
            }
        }
    }

    fun cancel() {
        job?.cancel() // Безопасная, предсказуемая отмена
    }
}
```

### Управление жизненным циклом

**Потоки - Ручное управление**:
```kotlin
// - РИСК УТЕЧКИ: Нужно вручную отслеживать и отменять потоки
class MyActivity : AppCompatActivity() {
    private val activeThreads = mutableListOf<Thread>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val thread = Thread {
            // Долгая работа
            repeat(1000) {
                Thread.sleep(1000)
                // Если Activity уничтожена, это продолжает работать!
            }
        }
        activeThreads.add(thread)
        thread.start()
    }

    override fun onDestroy() {
        super.onDestroy()
        // Нужно вручную отменить все потоки
        activeThreads.forEach { it.interrupt() }
        activeThreads.clear()
    }
}
```

**Корутины - Автоматическое управление**:
```kotlin
// - БЕЗ УТЕЧЕК: Автоматическое управление жизненным циклом
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Долгая работа
            repeat(1000) {
                delay(1000)
                // Автоматически отменяется когда Activity уничтожена!
            }
        }
    }

    // onDestroy не нужен - автоматическая очистка!
}
```

### Сравнение производительности

**Бенчмарк: 10,000 конкурентных задач**

```kotlin
// Потоки - Крэш или серьезное замедление
fun threadBenchmark() {
    val startTime = System.currentTimeMillis()

    repeat(10000) {
        Thread {
            Thread.sleep(1000)
            println("Done")
        }.start()
    }
    // Результат: OutOfMemoryError или экстремальное замедление
}

// Корутины - Без проблем
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
    // Результат: ~1 секунда, минимальное использование памяти
}
```

**Результаты**:
- Потоки: Крэш с OutOfMemoryError (слишком много потоков)
- Корутины: Завершаются успешно за ~1 секунду

### Преимущества специфичные для Android

**1. Безопасность Main потока**:
```kotlin
// Корутины делают легким сохранение main-safe
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) { loadData() }
    updateUI(data) // Безопасно - обратно на main потоке
}
```

**2. Интеграция с жизненным циклом**:
```kotlin
// Автоматическая отмена с жизненным циклом
viewModelScope.launch { ... } // Отменяется в onCleared()
lifecycleScope.launch { ... } // Отменяется когда жизненный цикл уничтожен
```

**3. Структурированная конкурентность**:
```kotlin
// Отношение родитель-потомок предотвращает утечки
lifecycleScope.launch {
    val job1 = launch { work1() }
    val job2 = launch { work2() }
    // Оба отменяются если родитель отменен
}
```

### Сравнение кода: Реальный пример

**Версия с потоками**:
```kotlin
// - СЛОЖНО: Сетевой вызов на потоках
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
// - ПРОСТО: Сетевой вызов на корутинах
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
- WARNING: Работа с Java библиотеками, которые требуют потоки
- WARNING: Долгие блокирующие операции (редко - используйте WorkManager вместо этого)
- WARNING: Низкоуровневое системное программирование

**Используйте Корутины Когда** (Почти Всегда на Android):
- - Сетевые вызовы
- - Операции с базой данных
- - Файловый I/O
- - Обработка изображений
- - Любая async работа в Android приложении
- - Обновления UI с фоновой работой
- - Сложные конкурентные операции

**Ключевой Вывод**: На Android **всегда предпочитайте корутины потокам** для асинхронных операций. Корутины легче, безопаснее и бесшовно интегрируются с компонентами жизненного цикла Android.

---

## References

- [Coroutines vs Threads - Kotlin Docs](https://kotlinlang.org/docs/coroutines-basics.html)
- [Threading on Android - Android Developers](https://developer.android.com/guide/background/threading)
- [Coroutines Performance - Android Developers](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)

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
- [[q-coroutine-delay-vs-thread-sleep--kotlin--easy]] - delay() vs Thread.sleep()

### Next Steps (Medium)
- [[q-suspend-functions-basics--kotlin--easy]] - Understanding suspend functions
- [[q-coroutine-dispatchers--kotlin--medium]] - Coroutine dispatchers overview
- [[q-coroutinescope-vs-coroutinecontext--kotlin--medium]] - Scope vs Context

