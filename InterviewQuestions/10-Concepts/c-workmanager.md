---
id: "20251025-140300"
title: "WorkManager / WorkManager"
aliases: ["Android WorkManager", "Background Work", "Deferrable Work", "WorkManager", "Отложенная работа", "Фоновая работа"]
summary: "Android Jetpack library for deferrable, guaranteed background work"
topic: "android"
subtopics: ["background-tasks", "jetpack", "workmanager"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: []
created: "2025-10-25"
updated: "2025-10-25"
tags: ["android", "background-tasks", "concept", "coroutines", "difficulty/medium", "jetpack", "threading", "workmanager"]
date created: Saturday, October 25th 2025, 11:07:27 am
date modified: Saturday, November 1st 2025, 5:43:38 pm
---

# WorkManager / WorkManager

## Summary (EN)

WorkManager is an Android Jetpack library designed for scheduling deferrable, guaranteed background work that needs to run even if the app exits or the device restarts. It intelligently chooses the best way to execute work based on device API level (JobScheduler, AlarmManager, or BroadcastReceiver) and respects system constraints like battery optimization, Doze mode, and App Standby. WorkManager is ideal for tasks like uploading logs, syncing data, backing up content, or processing images when constraints are met.

## Краткое Описание (RU)

WorkManager - это библиотека Android Jetpack для планирования отложенной, гарантированной фоновой работы, которая должна выполняться, даже если приложение закрыто или устройство перезагружено. Интеллектуально выбирает лучший способ выполнения работы в зависимости от уровня API устройства (JobScheduler, AlarmManager или BroadcastReceiver) и учитывает системные ограничения, такие как оптимизация батареи, режим Doze и App Standby. WorkManager идеально подходит для задач, таких как загрузка логов, синхронизация данных, резервное копирование контента или обработка изображений при соблюдении ограничений.

## Key Points (EN)

- **Guaranteed Execution**: Work will run even if app is killed or device restarts
- **Constraint-based**: Execute only when conditions met (network, battery, storage)
- **Backwards Compatible**: Works on API 14+, uses optimal implementation per API level
- **Persistent**: Work survives app and device restarts
- **Chainable**: Create sequences of work with dependencies
- **Cancellable**: Cancel work by ID or tag
- **Observable**: Monitor work status with LiveData or Flow
- **One-time or Periodic**: Support for both execution patterns
- **Exponential Backoff**: Automatic retry with configurable backoff policy
- **Thread-safe**: Safe to schedule from any thread

## Ключевые Моменты (RU)

- **Гарантированное выполнение**: Работа будет выполнена, даже если приложение закрыто или устройство перезагружено
- **На основе ограничений**: Выполнение только при соблюдении условий (сеть, батарея, хранилище)
- **Обратная совместимость**: Работает на API 14+, использует оптимальную реализацию для каждого уровня API
- **Персистентность**: Работа сохраняется при перезапуске приложения и устройства
- **Цепочки**: Создание последовательностей работ с зависимостями
- **Отменяемость**: Отмена работы по ID или тегу
- **Наблюдаемость**: Мониторинг статуса работы через LiveData или Flow
- **Разовая или периодическая**: Поддержка обоих шаблонов выполнения
- **Экспоненциальная задержка**: Автоматические повторы с настраиваемой политикой задержки
- **Потокобезопасность**: Безопасное планирование из любого потока

## Use Cases

### When to Use

- **Data synchronization**: Upload/download data when network available
- **Log uploading**: Send analytics/crash logs periodically
- **Image processing**: Compress, resize, or filter images
- **Database cleanup**: Periodic maintenance tasks
- **Content backup**: Backup user data to cloud storage
- **Notifications**: Schedule notifications for future delivery
- **Prefetching content**: Download content when on WiFi
- **Reports generation**: Create and upload reports
- **File compression**: Compress files before upload

### When to Avoid

- **Immediate execution**: Use coroutines or RxJava instead
- **Precise timing**: Use AlarmManager for exact timing (e.g., alarm clock)
- **User-initiated**: For tasks user expects immediately (use coroutines)
- **Long-running tasks**: Limited to 10 minutes (use Foreground Service)
- **Real-time updates**: Use WebSockets, Firebase, or similar
- **Background location**: Use Foreground Service with notification

## Trade-offs

**Pros**:
- **Guaranteed execution**: Survives app/device restarts
- **Battery efficient**: Respects Doze, App Standby, battery saver
- **Simple API**: Easy to use, less boilerplate than JobScheduler
- **Backwards compatible**: No need for API-level checks
- **Flexible constraints**: Network type, battery, storage, charging
- **Built-in retry**: Automatic retry with exponential backoff
- **Chainable**: Complex workflows with dependencies
- **Observable**: Easy status monitoring
- **Testable**: Good testing support

**Cons**:
- **Not immediate**: Work may be delayed (batching, constraints)
- **Not precise**: Cannot guarantee exact execution time
- **10-minute limit**: Tasks longer than 10 minutes may be stopped
- **Overhead**: Heavier than simple coroutines for immediate work
- **Complexity for simple tasks**: Overkill for one-off immediate tasks
- **Database dependency**: Uses Room internally (adds to APK size)

## Worker Types

### Worker (Synchronous)

```kotlin
class UploadWorker(
    context: Context,
    params: WorkerParameters
) : Worker(context, params) {

    override fun doWork(): Result {
        return try {
            val data = inputData.getString("file_path")
            // Perform synchronous work
            uploadFile(data)
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }

    private fun uploadFile(filePath: String?) {
        // Upload logic
    }
}
```

### CoroutineWorker (Asynchronous)

```kotlin
class DownloadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val url = inputData.getString("url") ?: return Result.failure()

            // Suspend function call
            val result = downloadFile(url)

            // Return data to next worker in chain
            val outputData = workDataOf("downloaded_path" to result.path)
            Result.success(outputData)
        } catch (e: Exception) {
            Log.e("DownloadWorker", "Download failed", e)
            Result.retry()
        }
    }

    private suspend fun downloadFile(url: String): DownloadResult {
        // Suspend download logic
        return withContext(Dispatchers.IO) {
            // Download implementation
            DownloadResult(path = "/path/to/file")
        }
    }
}
```

### RxWorker (RxJava)

```kotlin
class RxUploadWorker(
    context: Context,
    params: WorkerParameters
) : RxWorker(context, params) {

    override fun createWork(): Single<Result> {
        val data = inputData.getString("data")
        return uploadService.upload(data)
            .map { Result.success() }
            .onErrorReturn { Result.retry() }
    }
}
```

### ListenableWorker (ListenableFuture)

```kotlin
class ListenableUploadWorker(
    context: Context,
    params: WorkerParameters
) : ListenableWorker(context, params) {

    override fun startWork(): ListenableFuture<Result> {
        return CallbackToFutureAdapter.getFuture { completer ->
            // Async work with callback
            uploadService.upload(inputData) { result ->
                completer.set(Result.success())
            }
        }
    }
}
```

## Scheduling Work

### One-Time Work

```kotlin
// Simple one-time work
val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .build()

WorkManager.getInstance(context).enqueue(uploadRequest)

// With constraints and input data
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .setRequiresBatteryNotLow(true)
    .build()

val inputData = workDataOf(
    "file_path" to "/path/to/file",
    "user_id" to 12345
)

val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setConstraints(constraints)
    .setInputData(inputData)
    .addTag("upload")
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,
        WorkRequest.MIN_BACKOFF_MILLIS,
        TimeUnit.MILLISECONDS
    )
    .build()

WorkManager.getInstance(context).enqueue(uploadRequest)
```

### Periodic Work

```kotlin
// Runs every 15 minutes (minimum interval)
val periodicWork = PeriodicWorkRequestBuilder<SyncWorker>(
    repeatInterval = 15,
    repeatIntervalTimeUnit = TimeUnit.MINUTES
).build()

WorkManager.getInstance(context).enqueue(periodicWork)

// With flex interval (run within last 5 minutes of 15-minute window)
val flexibleWork = PeriodicWorkRequestBuilder<SyncWorker>(
    repeatInterval = 15,
    repeatIntervalTimeUnit = TimeUnit.MINUTES,
    flexTimeInterval = 5,
    flexTimeIntervalUnit = TimeUnit.MINUTES
).build()
```

### Expedited Work (API 31+)

```kotlin
// High-priority work that should run immediately
val expeditedRequest = OneTimeWorkRequestBuilder<UrgentWorker>()
    .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
    .build()

WorkManager.getInstance(context).enqueue(expeditedRequest)
```

## Constraints

```kotlin
val constraints = Constraints.Builder()
    // Network constraints
    .setRequiredNetworkType(NetworkType.CONNECTED) // Any network
    .setRequiredNetworkType(NetworkType.UNMETERED) // WiFi only
    .setRequiredNetworkType(NetworkType.NOT_ROAMING) // Not roaming

    // Battery constraints
    .setRequiresBatteryNotLow(true) // Battery > 15%
    .setRequiresCharging(true) // Device charging

    // Storage constraint
    .setRequiresStorageNotLow(true) // Storage > 15%

    // Device state
    .setRequiresDeviceIdle(true) // Device idle (API 23+)

    // Content URI trigger (API 24+)
    .addContentUriTrigger(
        uri = MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
        triggerForDescendants = true
    )
    .build()
```

## Work Chaining

### Sequential Chain

```kotlin
WorkManager.getInstance(context)
    .beginWith(downloadWorker)       // Step 1: Download
    .then(processWorker)             // Step 2: Process
    .then(uploadWorker)              // Step 3: Upload
    .enqueue()
```

### Parallel + Sequential

```kotlin
val resize = OneTimeWorkRequestBuilder<ResizeWorker>().build()
val compress = OneTimeWorkRequestBuilder<CompressWorker>().build()
val upload = OneTimeWorkRequestBuilder<UploadWorker>().build()

WorkManager.getInstance(context)
    .beginWith(listOf(resize, compress)) // Parallel: resize and compress
    .then(upload)                        // Sequential: then upload
    .enqueue()
```

### Complex Chains

```kotlin
val downloadA = OneTimeWorkRequestBuilder<DownloadWorker>()
    .setInputData(workDataOf("url" to "https://example.com/a"))
    .build()

val downloadB = OneTimeWorkRequestBuilder<DownloadWorker>()
    .setInputData(workDataOf("url" to "https://example.com/b"))
    .build()

val process = OneTimeWorkRequestBuilder<ProcessWorker>().build()
val upload = OneTimeWorkRequestBuilder<UploadWorker>().build()

WorkManager.getInstance(context)
    .beginWith(listOf(downloadA, downloadB)) // Parallel downloads
    .then(process)                            // Process both
    .then(upload)                             // Upload result
    .enqueue()
```

## Observing Work

### LiveData

```kotlin
val workRequest = OneTimeWorkRequestBuilder<UploadWorker>().build()
WorkManager.getInstance(context).enqueue(workRequest)

// Observe by ID
WorkManager.getInstance(context)
    .getWorkInfoByIdLiveData(workRequest.id)
    .observe(lifecycleOwner) { workInfo ->
        when (workInfo.state) {
            WorkInfo.State.SUCCEEDED -> {
                val result = workInfo.outputData.getString("result")
                Log.d("WorkManager", "Work succeeded: $result")
            }
            WorkInfo.State.FAILED -> {
                Log.e("WorkManager", "Work failed")
            }
            WorkInfo.State.RUNNING -> {
                Log.d("WorkManager", "Work running")
            }
            else -> {}
        }
    }

// Observe by tag
WorkManager.getInstance(context)
    .getWorkInfosByTagLiveData("upload")
    .observe(lifecycleOwner) { workInfoList ->
        val inProgress = workInfoList.count { it.state == WorkInfo.State.RUNNING }
        Log.d("WorkManager", "$inProgress uploads in progress")
    }
```

### Flow

```kotlin
WorkManager.getInstance(context)
    .getWorkInfoByIdFlow(workRequest.id)
    .collect { workInfo ->
        when (workInfo.state) {
            WorkInfo.State.SUCCEEDED -> { /* ... */ }
            WorkInfo.State.FAILED -> { /* ... */ }
            else -> {}
        }
    }
```

### Coroutines (One-shot)

```kotlin
val workInfo = WorkManager.getInstance(context)
    .getWorkInfoById(workRequest.id)
    .await()

if (workInfo.state == WorkInfo.State.SUCCEEDED) {
    // Work completed
}
```

## Canceling Work

```kotlin
// Cancel by ID
WorkManager.getInstance(context).cancelWorkById(workRequest.id)

// Cancel by tag
WorkManager.getInstance(context).cancelAllWorkByTag("upload")

// Cancel unique work
WorkManager.getInstance(context).cancelUniqueWork("sync_data")

// Cancel all work
WorkManager.getInstance(context).cancelAllWork()
```

## Unique Work

### Replace

```kotlin
// Replace existing work with same name
WorkManager.getInstance(context).enqueueUniqueWork(
    "sync_data",
    ExistingWorkPolicy.REPLACE,
    syncWorkRequest
)
```

### Keep

```kotlin
// Keep existing work, ignore new request
WorkManager.getInstance(context).enqueueUniqueWork(
    "sync_data",
    ExistingWorkPolicy.KEEP,
    syncWorkRequest
)
```

### Append

```kotlin
// Add to end of existing chain
WorkManager.getInstance(context).enqueueUniqueWork(
    "sync_data",
    ExistingWorkPolicy.APPEND,
    syncWorkRequest
)
```

### Append or Replace

```kotlin
// Append if running, replace if finished
WorkManager.getInstance(context).enqueueUniqueWork(
    "sync_data",
    ExistingWorkPolicy.APPEND_OR_REPLACE,
    syncWorkRequest
)
```

### Unique Periodic Work

```kotlin
WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "daily_sync",
    ExistingPeriodicWorkPolicy.KEEP,
    periodicSyncRequest
)
```

## Progress Updates

```kotlin
class ProgressWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val total = 100
        for (i in 0..total) {
            // Update progress
            setProgress(workDataOf("progress" to i))
            delay(100)
        }
        return Result.success()
    }
}

// Observe progress
WorkManager.getInstance(context)
    .getWorkInfoByIdLiveData(workRequest.id)
    .observe(lifecycleOwner) { workInfo ->
        val progress = workInfo.progress.getInt("progress", 0)
        progressBar.progress = progress
    }
```

## Foreground Work (Long-running)

```kotlin
class DownloadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        // Create notification for foreground service
        val notification = createNotification()

        // Run as foreground service
        setForeground(
            ForegroundInfo(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
            )
        )

        // Long-running work
        downloadLargeFile()

        return Result.success()
    }

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setContentTitle("Downloading")
            .setSmallIcon(R.drawable.ic_download)
            .setOngoing(true)
            .build()
    }
}
```

## Testing

```kotlin
@RunWith(AndroidJUnit4::class)
class UploadWorkerTest {
    @Test
    fun testUploadWorker() {
        val context = ApplicationProvider.getApplicationContext<Context>()

        val inputData = workDataOf("file_path" to "/test/path")

        val request = OneTimeWorkRequestBuilder<UploadWorker>()
            .setInputData(inputData)
            .build()

        val workManager = WorkManager.getInstance(context)
        val testDriver = WorkManagerTestInitHelper.getTestDriver(context)!!

        workManager.enqueue(request).result.get()

        // Simulate constraints met
        testDriver.setAllConstraintsMet(request.id)

        val workInfo = workManager.getWorkInfoById(request.id).get()
        assertThat(workInfo.state).isEqualTo(WorkInfo.State.SUCCEEDED)
    }
}
```

## Best Practices

1. **Use CoroutineWorker** - Simplifies async work with coroutines
2. **Set appropriate constraints** - Minimize battery/data usage
3. **Use unique work** - Prevent duplicate work
4. **Tag your work** - Easier to query and cancel related work
5. **Handle retries** - Return `Result.retry()` for transient failures
6. **Pass small data** - Input/output data limited to 10KB
7. **Use exponential backoff** - Avoid overwhelming servers
8. **Monitor work status** - Inform users of long-running tasks
9. **Clean up resources** - In `onStopped()` override
10. **Test with TestDriver** - Simulate constraints and delays

## Common Patterns

### Upload with Retry

```kotlin
class UploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val data = inputData.getString("data")
            uploadService.upload(data)
            Result.success()
        } catch (e: IOException) {
            // Network error - retry
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure()
            }
        } catch (e: Exception) {
            // Other error - fail immediately
            Result.failure()
        }
    }
}
```

## Related Concepts

- [[c-coroutines]] - CoroutineWorker uses coroutines
- [[c-service]] - Alternative for long-running tasks
- [[c-foreground-service]] - For user-visible work
- [[c-threading]] - Background threading concepts
- [[c-rxjava]] - RxWorker integration
- [[c-dependency-injection]] - Hilt WorkerFactory
- [[c-testing]] - Testing WorkManager

## References

- [WorkManager Documentation](https://developer.android.com/topic/libraries/architecture/workmanager)
- [WorkManager Basics](https://developer.android.com/topic/libraries/architecture/workmanager/basics)
- [Advanced WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager/advanced)
- [Testing WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager/how-to/testing)
- [WorkManager Codelab](https://developer.android.com/codelabs/android-workmanager)
- [Background Work Guide](https://developer.android.com/guide/background)
