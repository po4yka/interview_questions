---
topic: android
tags:
  - android
  - workmanager
  - background-work
  - jetpack
  - architecture
  - scheduled-tasks
difficulty: medium
status: draft
---

# What is WorkManager?

**Russian**: Что такое WorkManager?

## Answer (EN)
### Definition

**WorkManager** is an API that makes it easy to schedule **deferrable, asynchronous tasks** that are expected to run **even if the app exits or the device restarts**.

The WorkManager API is a suitable and recommended replacement for all previous Android background scheduling APIs, including:
- - **FirebaseJobDispatcher** (deprecated)
- - **GcmNetworkManager** (deprecated)
- - **JobScheduler** (complex, API 21+)

WorkManager incorporates the features of its predecessors in a modern, consistent API that works back to **API level 14** while also being conscious of battery life.

### Key Characteristics

WorkManager handles **background work** that needs to run when various constraints are met, regardless of whether the application process is alive or not.

Background work can be started:
- - When the app is in the **background**
- - When the app is in the **foreground**
- - When the app starts in the foreground but goes to the **background**

**Regardless of what the application is doing, background work should continue to execute, or be restarted if Android kills its process.**

### How WorkManager Works Under the Hood

WorkManager uses an underlying job dispatching service based on the following criteria:

![WorkManager criteria](https://developer.android.com/static/images/topic/libraries/architecture/workmanager/how-workmanager-chooses.png)

**Selection logic**:
- **API 23+**: Uses **JobScheduler**
- **API 14-22**: Uses custom **AlarmManager** + **BroadcastReceiver**
- **Optional**: Uses **Firebase JobDispatcher** (if available)

WorkManager automatically chooses the best option based on the device API level.

### Adding WorkManager Dependency

```gradle
dependencies {
    // WorkManager for Kotlin
    implementation "androidx.work:work-runtime-ktx:2.8.1"

    // Optional - RxJava support
    implementation "androidx.work:work-rxjava3:2.8.1"

    // Optional - Testing
    androidTestImplementation "androidx.work:work-testing:2.8.1"
}
```

## WorkManager Features

### 1. Work Constraints

Declaratively define the **optimal conditions** for your work to run using Work Constraints. For example, run only when:
- 📶 Device has **network connection** (Wi-Fi or cellular)
- 🔋 Device is **charging**
- 🔋 Battery is **not low**
- 💾 Device has **sufficient storage space**
- 📱 Device is **idle** (Doze mode)

```kotlin
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED) // Any network
    .setRequiresBatteryNotLow(true)                // Battery > 15%
    .setRequiresCharging(true)                     // Device charging
    .setRequiresStorageNotLow(true)                // Storage available
    .setRequiresDeviceIdle(false)                  // API 23+
    .build()

val uploadWorkRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setConstraints(constraints)
    .build()

WorkManager.getInstance(context).enqueue(uploadWorkRequest)
```

### 2. Robust Scheduling

WorkManager allows you to schedule work to run:
- **One-time** (execute once)
- **Repeatedly** (periodic execution)

Work can be:
- **Tagged** and **named** for organization
- Scheduled as **unique work** (prevent duplicates)
- **Monitored** or **cancelled** in groups

**Scheduled work is stored in an internally managed SQLite database** and WorkManager takes care of ensuring that this work persists and is rescheduled across device reboots.

WorkManager adheres to power-saving features and best practices like **Doze mode**, so you don't have to worry about it.

```kotlin
// One-time work
val oneTimeWork = OneTimeWorkRequestBuilder<UploadWorker>()
    .setInputData(workDataOf("file_path" to "/path/to/file"))
    .addTag("upload")
    .build()

// Periodic work (minimum 15 minutes)
val periodicWork = PeriodicWorkRequestBuilder<SyncWorker>(
    1, TimeUnit.HOURS  // Repeat every 1 hour
)
    .setConstraints(constraints)
    .build()

WorkManager.getInstance(context).enqueue(oneTimeWork)
```

### 3. Flexible Retry Policy

WorkManager offers **flexible retry policies**, including a configurable **exponential backoff** policy.

```kotlin
val uploadWork = OneTimeWorkRequestBuilder<UploadWorker>()
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,  // or LINEAR
        15,                          // Initial backoff delay
        TimeUnit.SECONDS
    )
    .build()
```

**Retry behavior**:
- Worker returns `Result.retry()`
- WorkManager waits for backoff duration
- Retries automatically
- Backoff increases exponentially: 15s → 30s → 60s → 120s...

### 4. Work Chaining

For complex related work, chain individual work tasks together using a **fluent, natural interface** that allows you to control which pieces run **sequentially** and which run in **parallel**.

```kotlin
WorkManager.getInstance(context)
    .beginWith(listOf(workA, workB))  // Parallel
    .then(workC)                       // Sequential after A and B
    .enqueue()
```

For each work task, you can define **input and output data**. When chaining work together, WorkManager **automatically passes output data** from one work task to the next.

```kotlin
// Complex chain
val compressWork = OneTimeWorkRequestBuilder<CompressImageWorker>().build()
val uploadWork1 = OneTimeWorkRequestBuilder<UploadWorker>().build()
val uploadWork2 = OneTimeWorkRequestBuilder<UploadWorker>().build()
val cleanupWork = OneTimeWorkRequestBuilder<CleanupWorker>().build()

WorkManager.getInstance(context)
    .beginWith(compressWork)                    // Step 1: Compress
    .then(listOf(uploadWork1, uploadWork2))     // Step 2: Upload in parallel
    .then(cleanupWork)                          // Step 3: Cleanup
    .enqueue()
```

### 5. Built-In Threading Interoperability

WorkManager integrates seamlessly with:
- - **Kotlin Coroutines** (`CoroutineWorker`)
- - **RxJava** (`RxWorker`)
- - **ListenableFuture** (`ListenableFutureWorker`)

You have the flexibility to plug in your own asynchronous APIs.

## How WorkManager Works - Core Components

### 1. Worker

`Worker` specifies **what task to perform**. The WorkManager API includes an abstract `Worker` class. You need to extend this class and perform the work.

```kotlin
class UploadWorker(
    context: Context,
    params: WorkerParameters
) : Worker(context, params) {

    override fun doWork(): Result {
        return try {
            // Get input data
            val filePath = inputData.getString("file_path") ?: return Result.failure()

            // Perform work
            uploadFile(filePath)

            // Return success
            Result.success()
        } catch (e: Exception) {
            // Return retry or failure
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure()
            }
        }
    }

    private fun uploadFile(filePath: String) {
        // Upload logic here
        Thread.sleep(2000) // Simulate upload
    }
}
```

**Worker results**:
- `Result.success()` - Work completed successfully
- `Result.failure()` - Work failed, don't retry
- `Result.retry()` - Work failed, retry with backoff

### 2. CoroutineWorker (Recommended)

For Kotlin coroutines support:

```kotlin
class UploadCoroutineWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return withContext(Dispatchers.IO) {
            try {
                val filePath = inputData.getString("file_path") ?: return@withContext Result.failure()

                // Suspend function - no blocking!
                uploadFileAsync(filePath)

                Result.success(
                    workDataOf("uploaded_url" to "https://example.com/file.jpg")
                )
            } catch (e: Exception) {
                if (runAttemptCount < 3) {
                    Result.retry()
                } else {
                    Result.failure(
                        workDataOf("error" to e.message)
                    )
                }
            }
        }
    }

    private suspend fun uploadFileAsync(filePath: String): String {
        delay(2000) // Simulate async upload
        return "https://example.com/uploaded.jpg"
    }
}
```

### 3. WorkRequest

`WorkRequest` represents an individual task that is to be performed. You can add details for the work:
- **Constraints** (network, battery, etc.)
- **Input data** (parameters)
- **Tags** (for organization)
- **Backoff policy** (retry behavior)

**WorkRequest types**:

**OneTimeWorkRequest** - Execute once:
```kotlin
val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setInputData(workDataOf("file_path" to "/path/to/file"))
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .addTag("upload")
    .build()
```

**PeriodicWorkRequest** - Execute repeatedly:
```kotlin
val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(
    repeatInterval = 1,      // Interval
    repeatIntervalTimeUnit = TimeUnit.HOURS,
    flexTimeInterval = 15,   // Flex interval (optional)
    flexTimeIntervalUnit = TimeUnit.MINUTES
)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.UNMETERED) // WiFi only
            .build()
    )
    .build()
```

WARNING: **Important**: Minimum periodic interval is **15 minutes**.

### 4. WorkManager

`WorkManager` class **enqueues and manages** all the work requests. Pass work request object to this WorkManager to enqueue the task.

```kotlin
// Enqueue work
WorkManager.getInstance(context).enqueue(uploadRequest)

// Enqueue unique work (prevent duplicates)
WorkManager.getInstance(context).enqueueUniqueWork(
    "sync_work",                    // Unique name
    ExistingWorkPolicy.KEEP,        // Policy: KEEP, REPLACE, APPEND
    syncRequest
)

// Enqueue unique periodic work
WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "periodic_sync",
    ExistingPeriodicWorkPolicy.KEEP,
    periodicSyncRequest
)

// Cancel work
WorkManager.getInstance(context).cancelWorkById(uploadRequest.id)
WorkManager.getInstance(context).cancelAllWorkByTag("upload")
WorkManager.getInstance(context).cancelUniqueWork("sync_work")
```

### 5. WorkInfo

`WorkInfo` contains the **information about a particular task**. The WorkManager provides **LiveData** for each of the work request objects. We can observe this and get the current status of the task.

```kotlin
// Observe work status
WorkManager.getInstance(context)
    .getWorkInfoByIdLiveData(uploadRequest.id)
    .observe(lifecycleOwner) { workInfo ->
        when (workInfo.state) {
            WorkInfo.State.ENQUEUED -> {
                Log.d("WorkManager", "Work enqueued")
            }
            WorkInfo.State.RUNNING -> {
                Log.d("WorkManager", "Work running")
                val progress = workInfo.progress.getInt("progress", 0)
                updateProgressBar(progress)
            }
            WorkInfo.State.SUCCEEDED -> {
                Log.d("WorkManager", "Work succeeded")
                val url = workInfo.outputData.getString("uploaded_url")
                showSuccess(url)
            }
            WorkInfo.State.FAILED -> {
                Log.d("WorkManager", "Work failed")
                val error = workInfo.outputData.getString("error")
                showError(error)
            }
            WorkInfo.State.CANCELLED -> {
                Log.d("WorkManager", "Work cancelled")
            }
            WorkInfo.State.BLOCKED -> {
                Log.d("WorkManager", "Work blocked (waiting for prerequisites)")
            }
        }
    }
```

## Step-by-Step Implementation

**Step 1: Create a Worker class**
```kotlin
class MyWorker(context: Context, params: WorkerParameters) : Worker(context, params) {
    override fun doWork(): Result {
        // Do work here
        return Result.success()
    }
}
```

**Step 2: Create WorkRequest**
```kotlin
val workRequest = OneTimeWorkRequestBuilder<MyWorker>().build()
```

**Step 3: Enqueue the request with WorkManager**
```kotlin
WorkManager.getInstance(context).enqueue(workRequest)
```

**Step 4: Fetch the task status (optional)**
```kotlin
WorkManager.getInstance(context)
    .getWorkInfoByIdLiveData(workRequest.id)
    .observe(lifecycleOwner) { workInfo ->
        // Handle work status
    }
```

## Practical Example: File Upload with Progress

```kotlin
class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return withContext(Dispatchers.IO) {
            try {
                val filePath = inputData.getString(KEY_FILE_PATH)
                    ?: return@withContext Result.failure()

                val file = File(filePath)
                val totalBytes = file.length()
                var uploadedBytes = 0L

                // Simulate chunked upload with progress
                val chunkSize = totalBytes / 10
                for (i in 1..10) {
                    delay(500) // Simulate network
                    uploadedBytes += chunkSize

                    // Update progress
                    val progress = ((uploadedBytes.toFloat() / totalBytes) * 100).toInt()
                    setProgress(workDataOf(KEY_PROGRESS to progress))
                }

                // Return success with output data
                Result.success(
                    workDataOf(KEY_UPLOADED_URL to "https://example.com/file.jpg")
                )

            } catch (e: Exception) {
                Log.e("FileUploadWorker", "Upload failed", e)
                Result.failure(
                    workDataOf(KEY_ERROR to e.message)
                )
            }
        }
    }

    companion object {
        const val KEY_FILE_PATH = "file_path"
        const val KEY_PROGRESS = "progress"
        const val KEY_UPLOADED_URL = "uploaded_url"
        const val KEY_ERROR = "error"
    }
}

// Usage in Activity/ViewModel
class UploadViewModel : ViewModel() {

    fun uploadFile(filePath: String) {
        val uploadRequest = OneTimeWorkRequestBuilder<FileUploadWorker>()
            .setInputData(workDataOf(FileUploadWorker.KEY_FILE_PATH to filePath))
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .setRequiresBatteryNotLow(true)
                    .build()
            )
            .setBackoffCriteria(
                BackoffPolicy.EXPONENTIAL,
                15,
                TimeUnit.SECONDS
            )
            .build()

        WorkManager.getInstance(application).enqueue(uploadRequest)

        // Observe progress
        WorkManager.getInstance(application)
            .getWorkInfoByIdLiveData(uploadRequest.id)
            .observeForever { workInfo ->
                when (workInfo.state) {
                    WorkInfo.State.RUNNING -> {
                        val progress = workInfo.progress.getInt(FileUploadWorker.KEY_PROGRESS, 0)
                        _uploadProgress.value = progress
                    }
                    WorkInfo.State.SUCCEEDED -> {
                        val url = workInfo.outputData.getString(FileUploadWorker.KEY_UPLOADED_URL)
                        _uploadSuccess.value = url
                    }
                    WorkInfo.State.FAILED -> {
                        val error = workInfo.outputData.getString(FileUploadWorker.KEY_ERROR)
                        _uploadError.value = error
                    }
                    else -> {}
                }
            }
    }
}
```

## Unique Work

Prevent duplicate work from being enqueued:

```kotlin
// Keep existing work if already enqueued
WorkManager.getInstance(context).enqueueUniqueWork(
    "sync_data",
    ExistingWorkPolicy.KEEP,  // KEEP, REPLACE, APPEND, APPEND_OR_REPLACE
    syncRequest
)
```

**ExistingWorkPolicy**:
- `KEEP` - Keep existing work, ignore new request
- `REPLACE` - Cancel existing, start new work
- `APPEND` - Add to chain after existing work
- `APPEND_OR_REPLACE` - Append if existing succeeded, replace if failed

## When to Use WorkManager

- **Use WorkManager for**:
- 📤 **File uploads** that must complete
- 🔄 **Data synchronization** with server
- 📊 **Sending analytics/logs**
- 🗑️ **Cache cleanup** / old data deletion
- 📷 **Image processing/compression**
- 📅 **Periodic tasks** (every N hours)
- 🔔 **Scheduling notifications**

- **Don't use WorkManager for**:
- ⏱️ **Precise timing** (use AlarmManager)
- 🎵 **Long-running foreground work** (use Foreground Service)
- 📱 **Immediate UI updates** (use Coroutines)
- ⚡ **Real-time processing** (use Service or Coroutines)

## Summary

**WorkManager** is a Jetpack library for **deferrable, guaranteed background work**:

**Key features**:
- - Works even if app closes or device reboots
- - Constraint-based execution (WiFi, charging, etc.)
- - Automatic retry with backoff
- - Work chaining (sequential and parallel)
- - Built-in threading (Coroutines, RxJava)
- - Unique work (prevent duplicates)
- - Observable status (LiveData/Flow)
- - Battery-efficient (respects Doze mode)

**Core components**:
1. **Worker** - Defines the task
2. **WorkRequest** - Describes when and how to run
3. **WorkManager** - Enqueues and manages work
4. **WorkInfo** - Provides work status

**Types of work**:
- **OneTimeWorkRequest** - Run once
- **PeriodicWorkRequest** - Run repeatedly (min 15 min)

**Best for**:
- File uploads/downloads
- Data sync
- Analytics
- Periodic cleanup
- Background processing that must complete

## Ответ (Russian)

**WorkManager** — это API, которое упрощает планирование **откладываемых асинхронных задач**, которые должны выполняться, **даже если приложение закрыто или устройство перезагружается**.

WorkManager API — подходящая и рекомендуемая замена всех предыдущих API фонового планирования Android, включая **FirebaseJobDispatcher**, **GcmNetworkManager** и **JobScheduler**. WorkManager включает функции своих предшественников в современном, последовательном API, который работает до **API level 14** и при этом учитывает время автономной работы.

### Ключевые характеристики

WorkManager обрабатывает **фоновую работу**, которая должна выполняться при соблюдении различных ограничений, независимо от того, жив процесс приложения или нет.

Фоновая работа может быть запущена:
- Когда приложение в фоне
- Когда приложение на переднем плане
- Когда приложение переходит в фон

**Независимо от того, что делает приложение, фоновая работа должна продолжать выполняться или перезапускаться, если Android убивает процесс.**

### Как работает WorkManager

WorkManager использует базовый сервис диспетчеризации заданий на основе следующих критериев:
- **API 23+**: использует **JobScheduler**
- **API 14-22**: использует кастомный **AlarmManager** + **BroadcastReceiver**

WorkManager автоматически выбирает лучший вариант на основе уровня API устройства.

### Основные возможности

**1. Work Constraints (Ограничения работы)**

Декларативно определите оптимальные условия для выполнения работы:
- Сеть подключена (Wi-Fi или мобильная)
- Устройство заряжается
- Батарея не разряжена
- Достаточно места для хранения
- Устройство в режиме ожидания

**2. Robust Scheduling (Надежное планирование)**

Планируйте работу для однократного или периодического выполнения. Работа сохраняется во внутренней БД SQLite и переживает перезагрузки устройства.

**3. Flexible Retry Policy (Гибкая политика повторов)**

Гибкие политики повторов, включая настраиваемую экспоненциальную задержку.

**4. Work Chaining (Цепочки работ)**

Объединяйте отдельные рабочие задачи вместе, контролируя, какие части выполняются последовательно, а какие параллельно.

**5. Built-In Threading Interoperability (Встроенная интеграция с потоками)**

Интеграция с Kotlin Coroutines, RxJava и ListenableFuture.

### Основные компоненты

**1. Worker** - определяет, какую задачу выполнять
**2. WorkRequest** - представляет отдельную задачу (OneTimeWorkRequest или PeriodicWorkRequest)
**3. WorkManager** - ставит в очередь и управляет всеми запросами работ
**4. WorkInfo** - содержит информацию о конкретной задаче

### Когда использовать WorkManager

- **Используйте WorkManager для**:
- Загрузка файлов, которая должна завершиться
- Синхронизация данных с сервером
- Отправка аналитики/логов
- Очистка кэша/старых данных
- Обработка/сжатие изображений
- Периодические задачи (каждые N часов)

- **Не используйте WorkManager для**:
- Точного времени (используйте AlarmManager)
- Длительной работы на переднем плане (используйте Foreground Service)
- Немедленных обновлений UI (используйте Coroutines)

### Резюме

WorkManager — это Jetpack библиотека для откладываемой гарантированной фоновой работы. Работает даже при закрытом приложении или перезагрузке устройства. Поддерживает ограничения (WiFi, зарядка), автоматические повторы, цепочки работ, корутины. Идеален для загрузок файлов, синхронизации данных, аналитики и периодических задач очистки.

---

**Source**: [Kirchhoff Android Interview Questions](https://github.com/Kirchhoff-/Android-Interview-Questions)

## Links

- [WorkManager - Android Developers](https://developer.android.com/topic/libraries/architecture/workmanager)
- [WorkManager Basics - Medium](https://medium.com/androiddevelopers/workmanager-basics-beba51e94048)
- [Introducing WorkManager - Medium](https://medium.com/androiddevelopers/introducing-workmanager-2083bcfc4712)
- [Android WorkManager Tutorial - AndroidWave](https://androidwave.com/android-workmanager-tutorial/)
