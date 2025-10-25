---
id: 20251012-12271145
title: "Multithreading Tools Android / Инструменты многопоточности Android"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-background-vs-foreground-service--android--medium, q-push-notification-navigation--android--medium, q-room-vs-sqlite--android--medium]
created: 2025-10-15
tags: [multithreading, concurrency, asynctask, workmanager, rxjava, coroutines, background-tasks, difficulty/medium]
---

# Multithreading Tools in Android / Инструменты многопоточности в Android

**English**: What tools for multithreading do you know?

## Answer (EN)
Android provides several tools and APIs for handling multithreading and asynchronous operations. Here's a comprehensive overview of the main tools:

## 1. AsyncTask (Deprecated)

`AsyncTask` was intended to enable proper and easy use of the UI thread. However, it has been deprecated and should no longer be used.

**Why it was deprecated:**
- The most common use case was integrating into UI, which caused **Context leaks**, **missed callbacks**, or **crashes on configuration changes**
- **Inconsistent behavior** on different versions of the Android platform
- **Swallows exceptions** from `doInBackground`
- **Doesn't provide much utility** over using `Executors` directly

**How it worked:**

`AsyncTask` was designed to be a helper class around `Thread` and `Handler`. It was ideally used for short operations (a few seconds at most). An asynchronous task was defined by:
- **3 generic types**: `Params`, `Progress`, and `Result`
- **4 steps**: `onPreExecute`, `doInBackground`, `onProgressUpdate`, and `onPostExecute`

```kotlin
// Example (DEPRECATED - Don't use in new code)
class DownloadTask : AsyncTask<String, Int, String>() {
    override fun onPreExecute() {
        // Runs on UI thread before background work
    }

    override fun doInBackground(vararg params: String): String {
        // Runs on background thread
        // publishProgress() to update UI
        return "Result"
    }

    override fun onProgressUpdate(vararg values: Int) {
        // Runs on UI thread when publishProgress() is called
    }

    override fun onPostExecute(result: String) {
        // Runs on UI thread with result
    }
}
```

**Alternative**: Use `Executors` directly or modern alternatives like Coroutines or WorkManager.

## 2. WorkManager

`WorkManager` is an API that makes it easy to schedule **deferrable, asynchronous tasks** that are expected to run even if the app exits or the device restarts.

**Key Features:**
- **Guaranteed execution**: Work will be executed even if app is killed or device restarts
- **Constraint-based execution**: Run work only when specific conditions are met (network, battery, storage, etc.)
- **Backward compatibility**: Works back to API level 14
- **Battery-conscious**: Respects Doze mode and App Standby

**Use Cases:**
- Uploading logs or analytics
- Syncing application data with a server
- Downloading fresh content
- Processing images or media
- Backing up data

**Example:**

```kotlin
// Define Worker
class UploadWorker(context: Context, params: WorkerParameters) : Worker(context, params) {
    override fun doWork(): Result {
        // Perform background work
        uploadData()

        return Result.success()
    }

    private fun uploadData() {
        // Upload logic
    }
}

// Schedule work
val uploadWorkRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(uploadWorkRequest)

// Periodic work
val periodicWorkRequest = PeriodicWorkRequestBuilder<UploadWorker>(
    1, TimeUnit.HOURS
).build()

WorkManager.getInstance(context).enqueue(periodicWorkRequest)
```

**When to use WorkManager:**
- Tasks that need to run even if app is closed
- Tasks with specific constraints (network, charging, etc.)
- Background sync operations
- Scheduled periodic tasks

**Source**: [WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager)

## 3. RxJava / RxAndroid

RxJava is a Java VM implementation of [Reactive Extensions](https://reactivex.io/): a library for composing asynchronous and event-based programs by using observable sequences.

**Key Concepts:**
- Extends the **observer pattern** to support sequences of data/events
- Provides **operators** to compose sequences together declaratively
- Abstracts away concerns about **threading, synchronization, thread-safety**, and concurrent data structures

**RxAndroid Extension:**
- RxAndroid is an extension of RxJava specifically for Android
- Introduces the **Main Thread** support required for Android
- Provides `AndroidSchedulers.mainThread()` to perform actions on the UI thread

**Threading in RxJava:**

```kotlin
// Example: Network request with RxJava
Observable.fromCallable {
    // This runs on IO thread
    fetchDataFromNetwork()
}
.subscribeOn(Schedulers.io())           // Specify thread for source
.observeOn(AndroidSchedulers.mainThread())  // Specify thread for observer
.subscribe(
    { result ->
        // Update UI with result (runs on main thread)
        updateUI(result)
    },
    { error ->
        // Handle error (runs on main thread)
        showError(error)
    }
)
```

**Common Schedulers:**
- `Schedulers.io()` - I/O operations (network, database, file)
- `Schedulers.computation()` - CPU-intensive computations
- `Schedulers.newThread()` - Creates a new thread for each unit of work
- `AndroidSchedulers.mainThread()` - Android UI thread
- `Schedulers.trampoline()` - Execute immediately on current thread

**Advantages:**
- Powerful operators for data transformation
- Easy thread switching
- Excellent for complex asynchronous flows
- Great for handling events and streams

**Disadvantages:**
- Steep learning curve
- Can lead to complex and hard-to-debug code
- Large library size
- Being superseded by Kotlin Coroutines for new projects

**Source**: [RxJava For Android - RxAndroid](https://blog.mindorks.com/rxjava-for-android-rxandroid/)

## 4. Kotlin Coroutines

A **coroutine** is a concurrency design pattern that you can use on Android to simplify code that executes asynchronously. Coroutines were added to Kotlin in version 1.3 and are based on established concepts from other languages.

**Key Benefits:**
- **Lightweight**: You can run many coroutines on a single thread due to support for suspension
- **Fewer memory leaks**: Use structured concurrency to run operations within a scope
- **Built-in cancellation support**: Cancellation propagates automatically through the coroutine hierarchy
- **Jetpack integration**: Many Jetpack libraries include extensions with full coroutines support

**Basic Example:**

```kotlin
// Launch coroutine in ViewModel
class MyViewModel : ViewModel() {
    fun fetchData() {
        viewModelScope.launch {
            try {
                // This suspends the coroutine, not the thread
                val data = withContext(Dispatchers.IO) {
                    // Network or database call
                    repository.fetchData()
                }

                // Back on Main thread automatically
                _uiState.value = UiState.Success(data)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e)
            }
        }
    }
}
```

**Dispatchers:**
- `Dispatchers.Main` - UI thread (Android main thread)
- `Dispatchers.IO` - I/O operations (network, database, file)
- `Dispatchers.Default` - CPU-intensive work
- `Dispatchers.Unconfined` - Not confined to any specific thread

**Structured Concurrency:**

```kotlin
// All child coroutines are cancelled if parent is cancelled
coroutineScope {
    val data1 = async(Dispatchers.IO) { fetchData1() }
    val data2 = async(Dispatchers.IO) { fetchData2() }

    // Wait for both to complete
    val result = data1.await() + data2.await()
}
```

**Coroutine Scopes:**
- `viewModelScope` - Tied to ViewModel lifecycle
- `lifecycleScope` - Tied to Activity/Fragment lifecycle
- `GlobalScope` - Application-level scope (use carefully)
- Custom scopes - For specific use cases

**Flow for Streams:**

```kotlin
// Emit values over time
fun fetchUpdates(): Flow<Update> = flow {
    while (true) {
        val update = api.getUpdate()
        emit(update)
        delay(1000)
    }
}

// Collect values
viewModelScope.launch {
    fetchUpdates()
        .flowOn(Dispatchers.IO)  // Upstream operations on IO thread
        .collect { update ->      // Collection on Main thread
            updateUI(update)
        }
}
```

**When to use Coroutines:**
- Modern Android development (recommended by Google)
- Asynchronous operations with clean, sequential code
- Network requests and database operations
- Any background task that needs to update UI
- Complex concurrent operations with structured concurrency

**Source**: [Kotlin coroutines on Android](https://developer.android.com/kotlin/coroutines)

## Comparison Summary

| Tool | Status | Best For | Complexity | Thread Management |
|------|--------|----------|------------|-------------------|
| **AsyncTask** | Deprecated | Nothing (use alternatives) | Low | Automatic |
| **WorkManager** | Recommended | Guaranteed background work with constraints | Medium | Automatic |
| **RxJava/RxAndroid** | Mature | Complex event streams, reactive programming | High | Manual (Schedulers) |
| **Kotlin Coroutines** | Recommended | General async/await, modern Android development | Low-Medium | Dispatchers |

## Modern Recommendations

For new Android development:
1. **Kotlin Coroutines** - For most asynchronous operations, network calls, database access
2. **WorkManager** - For deferrable background tasks that need guaranteed execution
3. **RxJava** - Only if you have existing RxJava codebase or specific reactive requirements
4. **Never use AsyncTask** - It's deprecated and has many issues

## Other Threading Tools

- **Thread & Handler** - Low-level threading (rarely needed with modern tools)
- **Executors** - Java's thread pool management (use directly or via Coroutines)
- **IntentService** - Deprecated, use WorkManager instead
- **JobScheduler** - Lower-level API, WorkManager is preferred
- **Looper & HandlerThread** - For creating background threads with message queue

## Ответ (RU)
Android предоставляет несколько инструментов и API для обработки многопоточности и асинхронных операций. Вот полный обзор основных инструментов:

## 1. AsyncTask (Устарел)

`AsyncTask` был предназначен для упрощения использования UI потока. Однако он устарел и больше не должен использоваться.

**Почему устарел:**
- Наиболее распространённый вариант использования был для интеграции в UI, что вызывало утечки Context, пропущенные коллбэки или сбои при изменении конфигурации
- Несогласованное поведение на разных версиях платформы Android
- Поглощает исключения из `doInBackground`
- Не предоставляет большой пользы по сравнению с прямым использованием `Executors`

**Альтернатива**: Используйте `Executors` напрямую или современные альтернативы, такие как Coroutines или WorkManager.

## 2. WorkManager

`WorkManager` — это API, который упрощает планирование отложенных асинхронных задач, которые должны выполняться, даже если приложение закрывается или устройство перезагружается.

**Ключевые особенности:**
- Гарантированное выполнение: работа будет выполнена, даже если приложение убито или устройство перезагружено
- Выполнение на основе ограничений: запуск работы только при выполнении определённых условий (сеть, батарея, хранилище и т.д.)
- Обратная совместимость: работает с API level 14
- Экономия батареи: учитывает режим Doze и App Standby

**Варианты использования:**
- Загрузка логов или аналитики
- Синхронизация данных приложения с сервером
- Загрузка свежего контента
- Обработка изображений или медиа
- Резервное копирование данных

## 3. RxJava / RxAndroid

RxJava — это реализация Reactive Extensions для Java VM: библиотека для композиции асинхронных программ на основе событий с использованием наблюдаемых последовательностей.

**Ключевые концепции:**
- Расширяет паттерн наблюдателя для поддержки последовательностей данных/событий
- Предоставляет операторы для декларативной композиции последовательностей
- Абстрагирует вопросы о потоках, синхронизации, потокобезопасности и concurrent структурах данных

**RxAndroid:**
- RxAndroid — расширение RxJava специально для Android
- Вводит поддержку Main Thread, необходимую для Android
- Предоставляет `AndroidSchedulers.mainThread()` для выполнения действий в UI потоке

**Преимущества:**
- Мощные операторы для преобразования данных
- Простое переключение потоков
- Отлично подходит для сложных асинхронных потоков
- Отлично для обработки событий и потоков

**Недостатки:**
- Крутая кривая обучения
- Может привести к сложному и трудному для отладки коду
- Большой размер библиотеки
- Вытесняется Kotlin Coroutines для новых проектов

## 4. Kotlin Coroutines (Корутины)

**Корутина** — это паттерн проектирования для конкурентности, который можно использовать в Android для упрощения кода, выполняющегося асинхронно.

**Ключевые преимущества:**
- **Легковесные**: Можно запускать множество корутин в одном потоке благодаря поддержке приостановки
- **Меньше утечек памяти**: Использование структурированной конкурентности для выполнения операций в области видимости
- **Встроенная поддержка отмены**: Отмена распространяется автоматически через иерархию корутин
- **Интеграция с Jetpack**: Многие библиотеки Jetpack включают расширения с полной поддержкой корутин

**Диспетчеры (Dispatchers):**
- `Dispatchers.Main` - UI поток (главный поток Android)
- `Dispatchers.IO` - I/O операции (сеть, база данных, файлы)
- `Dispatchers.Default` - CPU-интенсивная работа
- `Dispatchers.Unconfined` - Не привязан к конкретному потоку

**Когда использовать корутины:**
- Современная разработка Android (рекомендуется Google)
- Асинхронные операции с чистым последовательным кодом
- Сетевые запросы и операции с базой данных
- Любая фоновая задача, которая должна обновлять UI
- Сложные конкурентные операции со структурированной конкурентностью

## Сравнительная таблица

| Инструмент | Статус | Лучше всего для | Сложность | Управление потоками |
|------------|--------|-----------------|-----------|---------------------|
| **AsyncTask** | Устарел | Ничего (используйте альтернативы) | Низкая | Автоматическое |
| **WorkManager** | Рекомендуется | Гарантированная фоновая работа с ограничениями | Средняя | Автоматическое |
| **RxJava/RxAndroid** | Зрелый | Сложные потоки событий, реактивное программирование | Высокая | Ручное (Schedulers) |
| **Kotlin Coroutines** | Рекомендуется | Общие async/await, современная разработка Android | Низкая-Средняя | Диспетчеры |

## Современные рекомендации

Для новой разработки Android:
1. **Kotlin Coroutines** - для большинства асинхронных операций, сетевых вызовов, доступа к БД
2. **WorkManager** - для отложенных фоновых задач, требующих гарантированного выполнения
3. **RxJava** - только если у вас есть существующая кодовая база RxJava или специфические реактивные требования
4. **Никогда не используйте AsyncTask** - он устарел и имеет много проблем

## Related Questions

- [[q-background-vs-foreground-service--android--medium]]
- [[q-push-notification-navigation--android--medium]]
- [[q-room-vs-sqlite--android--medium]]
