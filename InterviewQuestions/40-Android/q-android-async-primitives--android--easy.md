---
id: 20251012-122762
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

Асинхронные примитивы в Android используются для выполнения задач в фоновом режиме без блокировки главного UI потока, что обеспечивает плавную работу приложения и предотвращает ошибки ANR (Application Not Responding).

### Современные примитивы (Рекомендуемые)

#### 1. Kotlin Coroutines (Рекомендуется)

**Корутины** - это легковесный framework для конкурентного программирования, который делает асинхронный код похожим на синхронный.

**Преимущества:**
- Структурированная конкурентность (structured concurrency)
- Автоматическое управление lifecycle
- Читаемый, последовательный код
- Встроенная поддержка отмены
- Удобная обработка исключений

**Основные компоненты:**
- `suspend` функции - могут приостанавливаться и возобновляться
- `viewModelScope` - автоматическая привязка к lifecycle ViewModel
- `lifecycleScope` - автоматическая привязка к lifecycle Activity/Fragment
- `Dispatchers.IO` - для I/O операций (сеть, БД)
- `Dispatchers.Main` - для обновления UI
- `Dispatchers.Default` - для тяжелых вычислений

#### 2. Flow (Реактивные потоки)

**Flow** - это реактивный поток Kotlin для обработки множественных значений во времени.

**Типы Flow:**
- **Cold Flow**: Начинает работу только при подписке (collect)
- **Hot Flow** (StateFlow, SharedFlow): Всегда активны, независимо от подписчиков

**Преимущества:**
- Асинхронная обработка потоков данных
- Операторы трансформации (`map`, `filter`, `combine`)
- Автоматическая отмена при уничтожении scope
- Поддержка backpressure

#### 3. WorkManager

**WorkManager** - для гарантированного выполнения фоновых задач, которые переживают перезапуск приложения.

**Когда использовать:**
- Синхронизация данных с сервером
- Загрузка/скачивание файлов
- Периодические задачи (раз в день, неделю)
- Задачи, которые должны выполниться даже после закрытия приложения

**Особенности:**
- Гарантированное выполнение
- Constraints (WiFi, зарядка, low battery)
- Периодические задачи (`PeriodicWorkRequest`)
- Цепочки задач с зависимостями

### Устаревшие примитивы

#### 4. AsyncTask (Deprecated с API 30)

**Не используйте** - только для справки. Проблемы:
- Утечки памяти при ссылках на Activity/Fragment
- Нет механизма отмены
- Сложная обработка ошибок
- Проблемы при изменении конфигурации (поворот экрана)

#### 5. Handler и Looper

**Низкоуровневый** примитив для передачи сообщений между потоками.

**Когда использовать:**
- Кастомные механизмы таймингов
- Манипуляции с message queue
- Низкоуровневая коммуникация между потоками
- Delayed execution (`postDelayed`)

**Не рекомендуется** для общих async задач - используйте Coroutines.

#### 6. ExecutorService и ThreadPoolExecutor

**Java concurrency framework** для управления пулами потоков.

**Когда использовать:**
- Работа с legacy Java кодом
- Необходим точный контроль над пулом потоков
- Интеграция с Java библиотеками

**Недостатки:**
- Ручное управление lifecycle
- Verbose код
- Нужно manually переключаться на UI поток

#### 7. RxJava

**Reactive programming** библиотека для композиции async операций.

**Когда использовать:**
- Уже используется в проекте
- Сложные реактивные цепочки
- Операторы, которых нет в Flow

**Недостатки:**
- Крутая кривая обучения
- Большой размер библиотеки
- Корутины + Flow покрывают большинство use cases

### Сравнительная таблица

| Примитив | Сложность | Lifecycle Aware | Отмена | Современный | Use Case |
|----------|-----------|-----------------|--------|-------------|----------|
| **Coroutines** | Низкая | Да | Да | Да | Общие async операции |
| **Flow** | Средняя | Да | Да | Да | Реактивные потоки |
| **WorkManager** | Низкая | Да | Да | Да | Гарантированная фоновая работа |
| **AsyncTask** | Низкая | Нет | Нет | Нет | Deprecated |
| **Handler** | Средняя | Нет | Вручную | Да | Передача сообщений |
| **ExecutorService** | Средняя | Нет | Вручную | Да | Управление пулом потоков |
| **RxJava** | Высокая | Нет | Да | Да | Сложные реактивные потоки |

### Лучшие практики

**Используйте Coroutines для большинства случаев:**
- Простые async операции
- Параллельные запросы (`async`/`await`)
- Обработка ошибок с `try-catch`
- Автоматическая отмена при уничтожении scope

**Используйте Flow для реактивных данных:**
- Наблюдение за изменениями в БД
- Реактивные UI обновления
- Трансформация потоков данных
- Комбинирование множественных источников

**Используйте WorkManager для гарантированного выполнения:**
- Задачи, которые должны выполниться обязательно
- Периодические задачи
- Задачи с constraints (WiFi, зарядка)
- Загрузка/синхронизация данных

### Резюме

**Современные Android async примитивы:**
1. **Kotlin Coroutines** - основной выбор для async операций
2. **Flow** - реактивные потоки данных
3. **WorkManager** - гарантированная фоновая работа

**Legacy примитивы (для специфических случаев):**
4. **Handler/Looper** - передача сообщений и планирование
5. **ExecutorService** - управление пулом потоков
6. **RxJava** - сложные реактивные операции (если уже используется)

**Deprecated:**
7. **AsyncTask** - не используйте в новом коде

Для нового Android приложения рекомендуется комбинация Coroutines + Flow + WorkManager.

