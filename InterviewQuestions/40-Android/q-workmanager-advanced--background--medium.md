---
tags:
  - android
  - workmanager
  - background-processing
  - jetpack
  - kotlin-coroutines
difficulty: medium
status: draft
related:
  - q-workmanager-chaining--background--medium
  - q-foreground-service-types--background--medium
  - q-coroutines-structured-concurrency--coroutines--hard
created: 2025-10-12
---

# Question (EN)
What are the advanced features of WorkManager? Explain work constraints, periodic work, work chaining, ExistingWorkPolicy, and how WorkManager handles app updates and reboots.

## Answer (EN)
### Overview

**WorkManager** is the recommended solution for deferrable, guaranteed background work. Advanced features:
-  Constraints (network, battery, storage)
-  Periodic work (minimum 15 minutes)
-  Work chaining (sequential and parallel)
-  Unique work (ExistingWorkPolicy)
-  Survives app updates and device reboots
-  Automatic retry with backoff policies

### Work Constraints

**Available constraints:**

```kotlin
val constraints = Constraints.Builder()
    // Network constraints
    .setRequiredNetworkType(NetworkType.CONNECTED) // Any network
    .setRequiredNetworkType(NetworkType.UNMETERED) // WiFi only
    .setRequiredNetworkType(NetworkType.NOT_ROAMING) // No roaming
    .setRequiredNetworkType(NetworkType.METERED) // Mobile data OK

    // Battery constraints
    .setRequiresBatteryNotLow(true) // Don't run when battery < 15%
    .setRequiresCharging(true) // Only run when charging

    // Storage constraints
    .setRequiresStorageNotLow(true) // Don't run when storage low

    // Device state
    .setRequiresDeviceIdle(true) // Only when device idle (API 23+)

    .build()

val uploadWorkRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setConstraints(constraints)
    .build()
```

**Real-world example: Photo backup**

```kotlin
@HiltWorker
class PhotoBackupWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val photoRepository: PhotoRepository,
    private val backupService: BackupService
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            // Get unsynced photos
            val unsyncedPhotos = photoRepository.getUnsyncedPhotos()

            if (unsyncedPhotos.isEmpty()) {
                return Result.success()
            }

            // Upload each photo
            unsyncedPhotos.forEach { photo ->
                setProgress(
                    workDataOf(
                        "current" to photo.id,
                        "total" to unsyncedPhotos.size
                    )
                )

                backupService.uploadPhoto(photo)
                photoRepository.markAsSynced(photo.id)
            }

            Result.success()
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

// Schedule with constraints
fun schedulePhotoBackup() {
    val constraints = Constraints.Builder()
        .setRequiredNetworkType(NetworkType.UNMETERED) // WiFi only
        .setRequiresBatteryNotLow(true) // Don't drain battery
        .setRequiresCharging(false) // Can run while not charging
        .build()

    val backupRequest = OneTimeWorkRequestBuilder<PhotoBackupWorker>()
        .setConstraints(constraints)
        .setBackoffCriteria(
            BackoffPolicy.EXPONENTIAL,
            WorkRequest.MIN_BACKOFF_MILLIS,
            TimeUnit.MILLISECONDS
        )
        .build()

    WorkManager.getInstance(context).enqueue(backupRequest)
}
```

### Periodic Work

**Constraints:**
- Minimum interval: 15 minutes
- Flex interval: For more precise timing within interval

```kotlin
// Simple periodic work - runs every 15 minutes (minimum)
val periodicWorkRequest = PeriodicWorkRequestBuilder<SyncWorker>(
    15, TimeUnit.MINUTES
).build()

// Periodic work with flex interval
// Runs every 1 hour, but can run anytime in last 15 minutes
val flexPeriodicWork = PeriodicWorkRequestBuilder<SyncWorker>(
    repeatInterval = 1, TimeUnit.HOURS,
    flexTimeInterval = 15, TimeUnit.MINUTES
).build()

// With constraints
val constrainedPeriodicWork = PeriodicWorkRequestBuilder<DataSyncWorker>(
    24, TimeUnit.HOURS
)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .build()

WorkManager.getInstance(context)
    .enqueueUniquePeriodicWork(
        "daily_sync",
        ExistingPeriodicWorkPolicy.KEEP, // Keep existing work
        constrainedPeriodicWork
    )
```

**How periodic work actually works:**

```
Interval: 1 hour, Flex: 15 minutes

Timeline:
0:00  1:00
     [    Maintenance Window    ]
     
                    0:45         1:00

Work can run anywhere between 0:45 and 1:00
```

**Real-world example: News sync**

```kotlin
@HiltWorker
class NewsSyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val newsRepository: NewsRepository
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val lastSyncTime = newsRepository.getLastSyncTime()
            val newArticles = newsRepository.fetchNewsSince(lastSyncTime)

            newsRepository.saveArticles(newArticles)
            newsRepository.updateSyncTime(System.currentTimeMillis())

            // Show notification if there are new articles
            if (newArticles.isNotEmpty()) {
                showNotification(newArticles.size)
            }

            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }

    private fun showNotification(count: Int) {
        val notification = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_news)
            .setContentTitle("New articles")
            .setContentText("You have $count new articles")
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .build()

        NotificationManagerCompat.from(applicationContext)
            .notify(NOTIFICATION_ID, notification)
    }
}

// Schedule periodic sync every 4 hours
fun scheduleNewsSyncing() {
    val syncRequest = PeriodicWorkRequestBuilder<NewsSyncWorker>(
        repeatInterval = 4, TimeUnit.HOURS,
        flexTimeInterval = 30, TimeUnit.MINUTES
    )
        .setConstraints(
            Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()
        )
        .build()

    WorkManager.getInstance(context)
        .enqueueUniquePeriodicWork(
            "news_sync",
            ExistingPeriodicWorkPolicy.KEEP,
            syncRequest
        )
}
```

### Work Chaining

**Sequential chaining:**

```kotlin
// Task 1 → Task 2 → Task 3
val task1 = OneTimeWorkRequestBuilder<DownloadWorker>().build()
val task2 = OneTimeWorkRequestBuilder<ProcessWorker>().build()
val task3 = OneTimeWorkRequestBuilder<UploadWorker>().build()

WorkManager.getInstance(context)
    .beginWith(task1)
    .then(task2)
    .then(task3)
    .enqueue()
```

**Parallel chaining:**

```kotlin
// Task 1A \
//          → Task 3
// Task 1B /

val task1A = OneTimeWorkRequestBuilder<DownloadImageWorker>().build()
val task1B = OneTimeWorkRequestBuilder<DownloadVideoWorker>().build()
val task3 = OneTimeWorkRequestBuilder<CombineWorker>().build()

WorkManager.getInstance(context)
    .beginWith(listOf(task1A, task1B)) // Run in parallel
    .then(task3) // Runs after both complete
    .enqueue()
```

**Complex chaining:**

```kotlin
//     Task 1A \
//              → Task 2 \
//     Task 1B /          → Task 4
//                        /
//     Task 3 →

val chain1 = WorkManager.getInstance(context)
    .beginWith(listOf(task1A, task1B))
    .then(task2)

val chain2 = WorkManager.getInstance(context)
    .beginWith(task3)

WorkContinuation.combine(listOf(chain1, chain2))
    .then(task4)
    .enqueue()
```

**Real-world example: Image processing pipeline**

```kotlin
@HiltWorker
class DownloadImageWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val imageService: ImageService
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val imageUrl = inputData.getString("image_url") ?: return Result.failure()

        return try {
            val imagePath = imageService.downloadImage(imageUrl)

            Result.success(
                workDataOf("image_path" to imagePath)
            )
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

@HiltWorker
class CompressImageWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val imageProcessor: ImageProcessor
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val imagePath = inputData.getString("image_path") ?: return Result.failure()

        return try {
            val compressedPath = imageProcessor.compressImage(imagePath)

            Result.success(
                workDataOf("compressed_path" to compressedPath)
            )
        } catch (e: Exception) {
            Result.failure()
        }
    }
}

@HiltWorker
class UploadImageWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val uploadService: UploadService
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val imagePath = inputData.getString("compressed_path") ?: return Result.failure()

        return try {
            val imageUrl = uploadService.uploadImage(imagePath)

            Result.success(
                workDataOf("uploaded_url" to imageUrl)
            )
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// Create chain
fun processAndUploadImage(imageUrl: String) {
    val downloadRequest = OneTimeWorkRequestBuilder<DownloadImageWorker>()
        .setInputData(workDataOf("image_url" to imageUrl))
        .setConstraints(
            Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()
        )
        .build()

    val compressRequest = OneTimeWorkRequestBuilder<CompressImageWorker>()
        .build()

    val uploadRequest = OneTimeWorkRequestBuilder<UploadImageWorker>()
        .setConstraints(
            Constraints.Builder()
                .setRequiredNetworkType(NetworkType.UNMETERED)
                .build()
        )
        .build()

    WorkManager.getInstance(context)
        .beginWith(downloadRequest)
        .then(compressRequest)
        .then(uploadRequest)
        .enqueue()
}
```

### ExistingWorkPolicy

**For unique one-time work:**

```kotlin
enum class ExistingWorkPolicy {
    REPLACE,  // Cancel existing, start new
    KEEP,     // Keep existing, ignore new
    APPEND,   // Run new after existing completes
    APPEND_OR_REPLACE // Replace if existing is finished/cancelled, else append
}

// Example: REPLACE - Always use latest request
WorkManager.getInstance(context)
    .beginUniqueWork(
        "image_upload",
        ExistingWorkPolicy.REPLACE,
        uploadRequest
    )
    .enqueue()

// Example: KEEP - Don't restart if already running
WorkManager.getInstance(context)
    .enqueueUniqueWork(
        "database_cleanup",
        ExistingWorkPolicy.KEEP,
        cleanupRequest
    )

// Example: APPEND - Queue up requests
WorkManager.getInstance(context)
    .beginUniqueWork(
        "sync_queue",
        ExistingWorkPolicy.APPEND,
        syncRequest
    )
    .enqueue()
```

**For periodic work:**

```kotlin
enum class ExistingPeriodicWorkPolicy {
    KEEP,    // Keep existing periodic work
    REPLACE, // Replace with new periodic work
    UPDATE   // Update existing work (API 31+)
}

WorkManager.getInstance(context)
    .enqueueUniquePeriodicWork(
        "daily_backup",
        ExistingPeriodicWorkPolicy.KEEP,
        backupRequest
    )
```

**Real-world example: Sync queue**

```kotlin
// User can trigger multiple syncs - queue them up
fun syncData(dataType: String) {
    val syncRequest = OneTimeWorkRequestBuilder<DataSyncWorker>()
        .setInputData(workDataOf("data_type" to dataType))
        .setConstraints(
            Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()
        )
        .build()

    WorkManager.getInstance(context)
        .beginUniqueWork(
            "data_sync_$dataType",
            ExistingWorkPolicy.APPEND_OR_REPLACE,
            syncRequest
        )
        .enqueue()
}

// Only allow one cleanup at a time
fun cleanupOldData() {
    val cleanupRequest = OneTimeWorkRequestBuilder<CleanupWorker>()
        .build()

    WorkManager.getInstance(context)
        .enqueueUniqueWork(
            "cleanup",
            ExistingWorkPolicy.KEEP, // Don't start if already running
            cleanupRequest
        )
}
```

### Surviving App Updates and Reboots

**How WorkManager persists:**

```
WorkManager stores work in SQLite database:
- Work specifications
- Constraints
- Input/output data
- Scheduling information

On reboot/update:
1. WorkManager reads database
2. Reschedules all pending work
3. Checks constraints
4. Runs work when constraints met
```

**Testing persistence:**

```kotlin
@Test
fun testWorkSurvivesReboot() = runTest {
    val workManager = WorkManager.getInstance(context)

    // Schedule work
    val request = OneTimeWorkRequestBuilder<TestWorker>()
        .build()

    workManager.enqueue(request).result.get()

    // Simulate reboot
    val testDriver = WorkManagerTestInitHelper.getTestDriver(context)
    testDriver?.setAllConstraintsMet(request.id)

    // Verify work still exists
    val workInfo = workManager.getWorkInfoById(request.id).get()
    assertEquals(WorkInfo.State.ENQUEUED, workInfo.state)
}
```

**Handling app updates:**

```kotlin
@HiltWorker
class MigrationWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val database: AppDatabase
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val currentVersion = inputData.getInt("version", 0)

        return try {
            when (currentVersion) {
                1 -> migrateToV2()
                2 -> migrateToV3()
                else -> Result.success()
            }

            Result.success()
        } catch (e: Exception) {
            Result.failure()
        }
    }

    private suspend fun migrateToV2() {
        database.userDao().addNewColumn()
    }

    private suspend fun migrateToV3() {
        database.userDao().renameColumn()
    }
}

// Run migration on app update
class MyApplication : Application(), Configuration.Provider {

    override fun onCreate() {
        super.onCreate()

        val currentVersion = BuildConfig.VERSION_CODE
        val lastVersion = getLastAppVersion()

        if (currentVersion > lastVersion) {
            val migrationRequest = OneTimeWorkRequestBuilder<MigrationWorker>()
                .setInputData(workDataOf("version" to lastVersion))
                .build()

            WorkManager.getInstance(this)
                .enqueueUniqueWork(
                    "migration",
                    ExistingWorkPolicy.REPLACE,
                    migrationRequest
                )

            saveAppVersion(currentVersion)
        }
    }
}
```

### Observing Work Progress

```kotlin
@HiltWorker
class DownloadWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val downloadService: DownloadService
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val fileUrl = inputData.getString("file_url") ?: return Result.failure()

        return try {
            downloadService.downloadFile(fileUrl) { progress ->
                // Update progress
                setProgressAsync(
                    workDataOf(
                        "progress" to progress,
                        "file_url" to fileUrl
                    )
                )
            }

            Result.success()
        } catch (e: Exception) {
            Result.failure()
        }
    }
}

// Observe progress in UI
@HiltViewModel
class DownloadViewModel @Inject constructor(
    private val workManager: WorkManager,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val workId: UUID = savedStateHandle["work_id"]!!

    val workProgress: LiveData<WorkInfo> = workManager
        .getWorkInfoByIdLiveData(workId)

    val downloadProgress: LiveData<Int> = workProgress.map { workInfo ->
        workInfo?.progress?.getInt("progress", 0) ?: 0
    }

    val downloadState: LiveData<String> = workProgress.map { workInfo ->
        when (workInfo?.state) {
            WorkInfo.State.RUNNING -> "Downloading..."
            WorkInfo.State.SUCCEEDED -> "Download complete"
            WorkInfo.State.FAILED -> "Download failed"
            WorkInfo.State.CANCELLED -> "Download cancelled"
            else -> "Waiting..."
        }
    }

    fun cancelDownload() {
        workManager.cancelWorkById(workId)
    }
}

@Composable
fun DownloadScreen(viewModel: DownloadViewModel = hiltViewModel()) {
    val progress by viewModel.downloadProgress.observeAsState(0)
    val state by viewModel.downloadState.observeAsState("")

    Column(modifier = Modifier.padding(16.dp)) {
        Text(text = state)

        LinearProgressIndicator(
            progress = progress / 100f,
            modifier = Modifier.fillMaxWidth()
        )

        Button(onClick = { viewModel.cancelDownload() }) {
            Text("Cancel")
        }
    }
}
```

### Cancellation and Cleanup

```kotlin
@HiltWorker
class UploadWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val uploadService: UploadService
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result = coroutineScope {
        val uploadJob = async {
            uploadService.uploadFile()
        }

        // Handle cancellation
        try {
            uploadJob.await()
            Result.success()
        } catch (e: CancellationException) {
            // Clean up
            uploadService.cancelUpload()
            throw e // Rethrow to mark work as cancelled
        } catch (e: Exception) {
            Result.failure()
        }
    }

    override suspend fun onStopped() {
        // Called when work is stopped (cancelled or constraints no longer met)
        super.onStopped()
        uploadService.cleanup()
    }
}

// Cancel work
fun cancelUpload(workId: UUID) {
    WorkManager.getInstance(context).cancelWorkById(workId)
}

// Cancel all work with tag
fun cancelAllUploads() {
    WorkManager.getInstance(context).cancelAllWorkByTag("upload")
}

// Cancel unique work
fun cancelSync() {
    WorkManager.getInstance(context).cancelUniqueWork("sync")
}
```

### Best Practices

1. **Use Constraints for Battery/Network**
   ```kotlin
   //  GOOD - Respect user's data/battery
   Constraints.Builder()
       .setRequiredNetworkType(NetworkType.UNMETERED)
       .setRequiresBatteryNotLow(true)
       .build()

   //  BAD - No constraints for large uploads
   OneTimeWorkRequestBuilder<UploadWorker>().build()
   ```

2. **Use Unique Work to Avoid Duplicates**
   ```kotlin
   //  GOOD - Only one sync at a time
   WorkManager.getInstance(context)
       .enqueueUniqueWork("sync", ExistingWorkPolicy.KEEP, request)

   //  BAD - Multiple syncs can run
   WorkManager.getInstance(context).enqueue(request)
   ```

3. **Keep doWork() Short**
   ```kotlin
   //  GOOD - Complete within 10 minutes
   override suspend fun doWork(): Result {
       // Quick operation
       return Result.success()
   }

   //  BAD - Long-running operation
   override suspend fun doWork(): Result {
       while (true) { // Infinite loop!
           delay(1000)
       }
   }
   ```

4. **Use WorkManager for Deferrable Work**
   ```kotlin
   //  GOOD - Use WorkManager
   // - Sync data when WiFi available
   // - Backup photos overnight
   // - Clean cache when idle

   //  BAD - Use WorkManager for:
   // - Real-time messaging (use FCM)
   // - Time-sensitive operations (use AlarmManager)
   // - Long-running tasks (use Foreground Service)
   ```

### Summary

**WorkManager advanced features:**
-  **Constraints** - Network, battery, storage, device state
-  **Periodic work** - Minimum 15 minutes, with flex interval
-  **Work chaining** - Sequential and parallel execution
-  **ExistingWorkPolicy** - REPLACE, KEEP, APPEND, APPEND_OR_REPLACE
-  **Persistence** - Survives app updates and reboots
-  **Progress tracking** - setProgress() and observe in UI
-  **Cancellation** - Cancel by ID, tag, or unique name

**Use cases:**
- Photo/video backup (with WiFi constraint)
- Data synchronization (periodic work)
- File compression (work chaining)
- Cache cleanup (unique work with KEEP policy)
- Database migration (runs once after update)

**Key principles:**
- Use constraints to respect battery and data
- Use unique work to avoid duplicates
- Keep doWork() short (< 10 minutes)
- Handle cancellation gracefully
- Use for deferrable, guaranteed work only

---

# Вопрос (RU)
Какие продвинутые возможности WorkManager? Объясните work constraints, periodic work, work chaining, ExistingWorkPolicy, и как WorkManager справляется с обновлениями приложения и перезагрузками.

## Ответ (RU)
[Перевод с примерами из английской версии...]

### Резюме

**Продвинутые возможности WorkManager:**
-  **Constraints** — сеть, батарея, хранилище, состояние устройства
-  **Periodic work** — минимум 15 минут, с flex интервалом
-  **Work chaining** — последовательное и параллельное выполнение
-  **ExistingWorkPolicy** — REPLACE, KEEP, APPEND, APPEND_OR_REPLACE
-  **Persistence** — переживает обновления приложения и перезагрузки
-  **Progress tracking** — setProgress() и наблюдение в UI
-  **Cancellation** — отмена по ID, тегу или уникальному имени

**Применение:**
- Резервное копирование фото/видео (с WiFi constraint)
- Синхронизация данных (periodic work)
- Сжатие файлов (work chaining)
- Очистка кеша (unique work с KEEP policy)
- Миграция базы данных (запускается после обновления)

**Ключевые принципы:**
- Используйте constraints для экономии батареи и данных
- Используйте unique work чтобы избежать дубликатов
- Держите doWork() коротким (< 10 минут)
- Корректно обрабатывайте отмену
- Используйте только для откладываемой, гарантированной работы
