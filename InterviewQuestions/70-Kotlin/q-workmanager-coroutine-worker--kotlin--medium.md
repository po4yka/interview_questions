---
id: "20251012-180002"
title: "Using CoroutineWorker with WorkManager / Использование CoroutineWorker с WorkManager"
topic: kotlin
difficulty: medium
status: draft
created: 2025-10-15
tags: - kotlin
  - coroutines
  - android
  - workmanager
  - background
  - coroutineworker
  - worker
  - periodic-work
  - constraints
moc: moc-kotlin
subtopics:   - coroutines
  - android
  - workmanager
  - background
  - worker
---
# Using CoroutineWorker with WorkManager

## English

### Question
What is CoroutineWorker in Android WorkManager and how does it differ from Worker and RxWorker? When should you use WorkManager with coroutines versus launching coroutines directly? Provide production examples of data synchronization, file uploads, and periodic cleanup tasks with proper error handling, progress updates, and testing strategies.

### Answer

**CoroutineWorker** is a coroutine-friendly implementation of WorkManager's Worker that allows you to write background work using suspend functions instead of blocking operations.

#### 1. CoroutineWorker Basics

**What is CoroutineWorker?**

CoroutineWorker is specifically designed to work with Kotlin Coroutines:
- `doWork()` is a **suspend function**
- Automatically handles coroutine lifecycle
- Respects WorkManager cancellation
- Integrates with structured concurrency

**Class structure:**

```kotlin
import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters

class MyCoroutineWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    // This is a suspend function!
    override suspend fun doWork(): Result {
        return try {
            // Perform background work with coroutines
            performWork()
            Result.success()
        } catch (e: Exception) {
            Result.failure()
        }
    }

    private suspend fun performWork() {
        // Your suspending work here
        delay(1000)
        // Can call other suspend functions
    }
}
```

#### 2. Worker Types Comparison

**CoroutineWorker vs Worker vs RxWorker:**

```kotlin
// 1. Worker (traditional blocking)
class BlockingWorker(context: Context, params: WorkerParameters)
    : Worker(context, params) {

    // Runs on background thread, but blocks
    override fun doWork(): Result {
        Thread.sleep(1000) // Blocking call
        return Result.success()
    }
}

// 2. CoroutineWorker (coroutine-based)
class CoroutineBasedWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    // Suspend function - non-blocking
    override suspend fun doWork(): Result {
        delay(1000) // Non-blocking suspension
        return Result.success()
    }
}

// 3. RxWorker (RxJava-based)
class RxBasedWorker(context: Context, params: WorkerParameters)
    : RxWorker(context, params) {

    // Returns Single<Result>
    override fun createWork(): Single<Result> {
        return Single.just(Result.success())
            .delay(1, TimeUnit.SECONDS)
    }
}
```

**Comparison Table:**

| Feature | Worker | CoroutineWorker | RxWorker |
|---------|--------|-----------------|----------|
| Execution | Blocking thread | Suspend (non-blocking) | Reactive stream |
| Cancellation | Manual | Automatic (Job) | Disposable |
| API | Synchronous | Coroutines | RxJava |
| Testing | Simple | TestDispatcher | TestScheduler |
| Modern | No | Yes | Legacy |
| Best for | Simple blocking I/O | Modern Kotlin apps | Existing RxJava code |

#### 3. When to Use WorkManager vs Direct Coroutines

**Decision matrix:**

```kotlin
//  USE WorkManager + CoroutineWorker when:

// 1. Work must survive process death
class DataSyncWorker : CoroutineWorker {
    override suspend fun doWork(): Result {
        // Sync will continue even if app is killed
        syncDataWithServer()
        return Result.success()
    }
}

// 2. Need guaranteed execution (even after reboot)
val workRequest = OneTimeWorkRequestBuilder<DataSyncWorker>()
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,
        WorkRequest.MIN_BACKOFF_MILLIS,
        TimeUnit.MILLISECONDS
    )
    .build()

// 3. Need constraints (network, battery, etc.)
val constrainedWork = OneTimeWorkRequestBuilder<UploadWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.UNMETERED) // WiFi only
            .setRequiresCharging(true)
            .build()
    )
    .build()

// 4. Periodic work
val periodicWork = PeriodicWorkRequestBuilder<CleanupWorker>(
    repeatInterval = 1,
    repeatIntervalTimeUnit = TimeUnit.DAYS
).build()

//  DON'T use WorkManager when:

// 1. Immediate execution needed (use regular coroutines)
viewModelScope.launch {
    loadUserProfile() // Immediate, tied to UI lifecycle
}

// 2. Work is tied to UI lifecycle
lifecycleScope.launch {
    updateUI() // Should be cancelled when UI is destroyed
}

// 3. Real-time updates needed
fun observeMessages() = channelFlow {
    // Real-time messaging - not suitable for WorkManager
    websocket.collect { message ->
        send(message)
    }
}
```

**When to use each:**

| Scenario | Solution | Reason |
|----------|----------|--------|
| Upload file in background | WorkManager | Survives process death |
| Load data for screen | ViewModel + coroutine | Tied to lifecycle |
| Periodic cleanup | WorkManager | Scheduled execution |
| Real-time chat | Coroutine + Flow | Needs immediate updates |
| Database migration | WorkManager | Long-running, guaranteed |
| API call on button click | ViewModel + coroutine | Immediate, cancellable |

#### 4. Production Example: Data Sync Worker

**Complete data synchronization implementation:**

```kotlin
import android.content.Context
import androidx.work.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.concurrent.TimeUnit

class DataSyncWorker(
    private val context: Context,
    private val params: WorkerParameters
) : CoroutineWorker(context, params) {

    companion object {
        const val KEY_SYNC_TYPE = "sync_type"
        const val KEY_USER_ID = "user_id"
        const val KEY_PROGRESS = "progress"
        const val TAG_SYNC = "data_sync"

        fun scheduleSyncWork(
            context: Context,
            syncType: String,
            userId: String
        ): UUID {
            val inputData = workDataOf(
                KEY_SYNC_TYPE to syncType,
                KEY_USER_ID to userId
            )

            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .setRequiresBatteryNotLow(true)
                .build()

            val syncRequest = OneTimeWorkRequestBuilder<DataSyncWorker>()
                .setInputData(inputData)
                .setConstraints(constraints)
                .setBackoffCriteria(
                    BackoffPolicy.EXPONENTIAL,
                    WorkRequest.MIN_BACKOFF_MILLIS,
                    TimeUnit.MILLISECONDS
                )
                .addTag(TAG_SYNC)
                .build()

            WorkManager.getInstance(context).enqueueUniqueWork(
                "sync_$userId",
                ExistingWorkPolicy.REPLACE,
                syncRequest
            )

            return syncRequest.id
        }
    }

    override suspend fun doWork(): Result {
        val syncType = inputData.getString(KEY_SYNC_TYPE) ?: return Result.failure()
        val userId = inputData.getString(KEY_USER_ID) ?: return Result.failure()

        return try {
            // Show foreground notification for long-running work
            setForeground(createForegroundInfo())

            // Perform sync with progress updates
            performSync(syncType, userId)

            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                // Retry with exponential backoff
                Result.retry()
            } else {
                // Max retries exceeded
                Result.failure(
                    workDataOf("error" to e.message)
                )
            }
        }
    }

    private suspend fun performSync(syncType: String, userId: String) {
        val repository = DataRepository() // Get from DI in real app

        when (syncType) {
            "full" -> syncFullData(repository, userId)
            "incremental" -> syncIncrementalData(repository, userId)
            else -> throw IllegalArgumentException("Unknown sync type: $syncType")
        }
    }

    private suspend fun syncFullData(repository: DataRepository, userId: String) {
        val steps = listOf("users", "posts", "comments", "media")

        steps.forEachIndexed { index, step ->
            // Check if work is cancelled
            if (isStopped) {
                throw CancellationException("Work cancelled")
            }

            // Update progress
            setProgress(
                workDataOf(
                    KEY_PROGRESS to ((index + 1) * 100 / steps.size)
                )
            )

            // Sync specific data type
            when (step) {
                "users" -> repository.syncUsers(userId)
                "posts" -> repository.syncPosts(userId)
                "comments" -> repository.syncComments(userId)
                "media" -> repository.syncMedia(userId)
            }
        }
    }

    private suspend fun syncIncrementalData(repository: DataRepository, userId: String) {
        val lastSyncTime = repository.getLastSyncTime(userId)
        repository.syncChangesSince(userId, lastSyncTime)

        // Update last sync time
        repository.updateLastSyncTime(userId, System.currentTimeMillis())
    }

    private fun createForegroundInfo(): ForegroundInfo {
        val notification = NotificationCompat.Builder(context, "sync_channel")
            .setContentTitle("Syncing data")
            .setContentText("Synchronizing your data in the background")
            .setSmallIcon(R.drawable.ic_sync)
            .setOngoing(true)
            .build()

        return ForegroundInfo(NOTIFICATION_ID, notification)
    }

    private companion object {
        const val NOTIFICATION_ID = 1001
    }
}

// Mock repository for example
class DataRepository {
    suspend fun syncUsers(userId: String) = withContext(Dispatchers.IO) {
        // Simulate network call
        delay(500)
        println("Synced users for $userId")
    }

    suspend fun syncPosts(userId: String) = withContext(Dispatchers.IO) {
        delay(500)
        println("Synced posts for $userId")
    }

    suspend fun syncComments(userId: String) = withContext(Dispatchers.IO) {
        delay(500)
        println("Synced comments for $userId")
    }

    suspend fun syncMedia(userId: String) = withContext(Dispatchers.IO) {
        delay(500)
        println("Synced media for $userId")
    }

    suspend fun getLastSyncTime(userId: String): Long = withContext(Dispatchers.IO) {
        // Get from local database
        System.currentTimeMillis() - 3600000 // 1 hour ago
    }

    suspend fun syncChangesSince(userId: String, timestamp: Long) =
        withContext(Dispatchers.IO) {
            delay(1000)
            println("Synced changes since $timestamp")
        }

    suspend fun updateLastSyncTime(userId: String, timestamp: Long) =
        withContext(Dispatchers.IO) {
            // Save to local database
            println("Updated last sync time: $timestamp")
        }
}
```

#### 5. File Upload Worker with Progress

**Complete file upload implementation:**

```kotlin
import android.content.Context
import android.net.Uri
import androidx.work.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File
import java.io.IOException

class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    companion object {
        const val KEY_FILE_URI = "file_uri"
        const val KEY_UPLOAD_URL = "upload_url"
        const val KEY_PROGRESS = "progress"
        const val KEY_UPLOADED_BYTES = "uploaded_bytes"
        const val KEY_TOTAL_BYTES = "total_bytes"

        fun uploadFile(
            context: Context,
            fileUri: Uri,
            uploadUrl: String
        ): UUID {
            val inputData = workDataOf(
                KEY_FILE_URI to fileUri.toString(),
                KEY_UPLOAD_URL to uploadUrl
            )

            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.UNMETERED) // WiFi only
                .build()

            val uploadRequest = OneTimeWorkRequestBuilder<FileUploadWorker>()
                .setInputData(inputData)
                .setConstraints(constraints)
                .build()

            WorkManager.getInstance(context).enqueue(uploadRequest)

            return uploadRequest.id
        }
    }

    override suspend fun doWork(): Result {
        val fileUriString = inputData.getString(KEY_FILE_URI)
            ?: return Result.failure()
        val uploadUrl = inputData.getString(KEY_UPLOAD_URL)
            ?: return Result.failure()

        return try {
            val fileUri = Uri.parse(fileUriString)
            val file = getFileFromUri(fileUri)

            // Set as foreground for long uploads
            setForeground(createForegroundInfo())

            // Upload file with progress
            uploadFileWithProgress(file, uploadUrl)

            Result.success(
                workDataOf("uploaded_file" to file.name)
            )
        } catch (e: IOException) {
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure(
                    workDataOf("error" to e.message)
                )
            }
        }
    }

    private suspend fun uploadFileWithProgress(
        file: File,
        uploadUrl: String
    ) = withContext(Dispatchers.IO) {
        val client = OkHttpClient()

        val requestBody = object : RequestBody() {
            override fun contentType() = "application/octet-stream".toMediaType()

            override fun contentLength() = file.length()

            override fun writeTo(sink: BufferedSink) {
                val fileSize = file.length()
                var uploadedBytes = 0L

                file.inputStream().use { inputStream ->
                    val buffer = ByteArray(8192)
                    var bytesRead: Int

                    while (inputStream.read(buffer).also { bytesRead = it } != -1) {
                        // Check cancellation
                        if (isStopped) {
                            throw IOException("Upload cancelled")
                        }

                        sink.write(buffer, 0, bytesRead)
                        uploadedBytes += bytesRead

                        // Update progress
                        val progress = (uploadedBytes * 100 / fileSize).toInt()
                        setProgressAsync(
                            workDataOf(
                                KEY_PROGRESS to progress,
                                KEY_UPLOADED_BYTES to uploadedBytes,
                                KEY_TOTAL_BYTES to fileSize
                            )
                        )
                    }
                }
            }
        }

        val request = Request.Builder()
            .url(uploadUrl)
            .post(requestBody)
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IOException("Upload failed: ${response.code}")
            }
        }
    }

    private fun getFileFromUri(uri: Uri): File {
        // In real app, copy content:// URI to cache file
        return File(uri.path!!)
    }

    private fun createForegroundInfo(): ForegroundInfo {
        val notification = NotificationCompat.Builder(applicationContext, "upload_channel")
            .setContentTitle("Uploading file")
            .setContentText("Upload in progress")
            .setSmallIcon(R.drawable.ic_upload)
            .setProgress(100, 0, false)
            .setOngoing(true)
            .build()

        return ForegroundInfo(NOTIFICATION_ID, notification)
    }

    private companion object {
        const val NOTIFICATION_ID = 1002
    }
}
```

#### 6. Periodic Cleanup Worker

**Periodic work with maintenance tasks:**

```kotlin
import android.content.Context
import androidx.work.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.util.concurrent.TimeUnit

class CleanupWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    companion object {
        fun schedulePeriodicCleanup(context: Context) {
            val cleanupRequest = PeriodicWorkRequestBuilder<CleanupWorker>(
                repeatInterval = 1,
                repeatIntervalTimeUnit = TimeUnit.DAYS
            )
                .setConstraints(
                    Constraints.Builder()
                        .setRequiresCharging(true)
                        .setRequiresBatteryNotLow(true)
                        .build()
                )
                .setInitialDelay(1, TimeUnit.HOURS)
                .build()

            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                "periodic_cleanup",
                ExistingPeriodicWorkPolicy.KEEP,
                cleanupRequest
            )
        }
    }

    override suspend fun doWork(): Result {
        return try {
            performCleanup()
            Result.success()
        } catch (e: Exception) {
            // Don't retry periodic work
            Result.failure()
        }
    }

    private suspend fun performCleanup() = withContext(Dispatchers.IO) {
        // 1. Clean cache directory
        cleanCacheDirectory()

        // 2. Delete old temporary files
        deleteOldTempFiles()

        // 3. Vacuum database
        vacuumDatabase()

        // 4. Clear old logs
        clearOldLogs()
    }

    private fun cleanCacheDirectory() {
        val cacheDir = applicationContext.cacheDir
        val maxCacheSize = 50 * 1024 * 1024 // 50 MB

        val cacheSize = cacheDir.walkTopDown()
            .filter { it.isFile }
            .map { it.length() }
            .sum()

        if (cacheSize > maxCacheSize) {
            cacheDir.walkTopDown()
                .filter { it.isFile }
                .sortedBy { it.lastModified() }
                .forEach { file ->
                    file.delete()
                    if (cacheDir.walkTopDown().filter { it.isFile }
                            .map { it.length() }.sum() < maxCacheSize) {
                        return@forEach
                    }
                }
        }
    }

    private fun deleteOldTempFiles() {
        val tempDir = File(applicationContext.cacheDir, "temp")
        val maxAge = System.currentTimeMillis() - TimeUnit.DAYS.toMillis(7)

        tempDir.walkTopDown()
            .filter { it.isFile && it.lastModified() < maxAge }
            .forEach { it.delete() }
    }

    private suspend fun vacuumDatabase() {
        // Vacuum SQLite database to reclaim space
        // val database = YourDatabase.getInstance(applicationContext)
        // database.query("VACUUM", null)
        delay(1000) // Simulate vacuum operation
    }

    private fun clearOldLogs() {
        val logDir = File(applicationContext.filesDir, "logs")
        val maxAge = System.currentTimeMillis() - TimeUnit.DAYS.toMillis(30)

        logDir.walkTopDown()
            .filter { it.isFile && it.lastModified() < maxAge }
            .forEach { it.delete() }
    }
}
```

#### 7. Chaining Workers

**Sequential work execution:**

```kotlin
fun chainedWorkExample(context: Context) {
    // Step 1: Download data
    val downloadWork = OneTimeWorkRequestBuilder<DownloadWorker>()
        .setInputData(workDataOf("url" to "https://api.example.com/data"))
        .build()

    // Step 2: Process data (depends on download)
    val processWork = OneTimeWorkRequestBuilder<ProcessWorker>()
        .build()

    // Step 3: Upload results (depends on process)
    val uploadWork = OneTimeWorkRequestBuilder<UploadWorker>()
        .build()

    // Chain workers
    WorkManager.getInstance(context)
        .beginWith(downloadWork)
        .then(processWork)
        .then(uploadWork)
        .enqueue()
}

class DownloadWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val url = inputData.getString("url") ?: return Result.failure()

        return try {
            val data = downloadData(url)

            // Pass data to next worker
            Result.success(
                workDataOf("downloaded_data" to data)
            )
        } catch (e: Exception) {
            Result.failure()
        }
    }

    private suspend fun downloadData(url: String): String = withContext(Dispatchers.IO) {
        // Download logic
        delay(1000)
        "downloaded_data_content"
    }
}

class ProcessWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        // Get data from previous worker
        val data = inputData.getString("downloaded_data")
            ?: return Result.failure()

        return try {
            val processed = processData(data)

            Result.success(
                workDataOf("processed_data" to processed)
            )
        } catch (e: Exception) {
            Result.failure()
        }
    }

    private suspend fun processData(data: String): String = withContext(Dispatchers.Default) {
        // Process logic
        delay(500)
        "processed_$data"
    }
}

class UploadWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val data = inputData.getString("processed_data")
            ?: return Result.failure()

        return try {
            uploadData(data)
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }

    private suspend fun uploadData(data: String) = withContext(Dispatchers.IO) {
        // Upload logic
        delay(1000)
        println("Uploaded: $data")
    }
}
```

#### 8. Observing Work Progress

**Monitoring work status and progress:**

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.work.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.util.UUID

data class WorkProgress(
    val state: WorkInfo.State,
    val progress: Int = 0,
    val error: String? = null
)

class WorkViewModel(private val workManager: WorkManager) : ViewModel() {

    private val _workProgress = MutableStateFlow<WorkProgress?>(null)
    val workProgress: StateFlow<WorkProgress?> = _workProgress

    fun startDataSync(userId: String) {
        val workId = DataSyncWorker.scheduleSyncWork(
            context = getApplication(),
            syncType = "full",
            userId = userId
        )

        observeWork(workId)
    }

    private fun observeWork(workId: UUID) {
        viewModelScope.launch {
            workManager.getWorkInfoByIdFlow(workId).collect { workInfo ->
                _workProgress.value = when (workInfo.state) {
                    WorkInfo.State.ENQUEUED -> WorkProgress(WorkInfo.State.ENQUEUED)
                    WorkInfo.State.RUNNING -> {
                        val progress = workInfo.progress.getInt(
                            DataSyncWorker.KEY_PROGRESS,
                            0
                        )
                        WorkProgress(WorkInfo.State.RUNNING, progress)
                    }
                    WorkInfo.State.SUCCEEDED -> WorkProgress(WorkInfo.State.SUCCEEDED, 100)
                    WorkInfo.State.FAILED -> {
                        val error = workInfo.outputData.getString("error")
                        WorkProgress(WorkInfo.State.FAILED, error = error)
                    }
                    WorkInfo.State.CANCELLED -> WorkProgress(WorkInfo.State.CANCELLED)
                    WorkInfo.State.BLOCKED -> WorkProgress(WorkInfo.State.BLOCKED)
                }
            }
        }
    }

    fun cancelWork(workId: UUID) {
        workManager.cancelWorkById(workId)
    }
}

// UI observing progress
@Composable
fun WorkProgressScreen(viewModel: WorkViewModel) {
    val workProgress by viewModel.workProgress.collectAsState()

    Column {
        when (val progress = workProgress) {
            null -> Text("No work running")
            else -> {
                Text("State: ${progress.state}")
                if (progress.state == WorkInfo.State.RUNNING) {
                    LinearProgressIndicator(
                        progress = progress.progress / 100f
                    )
                    Text("${progress.progress}%")
                }
                progress.error?.let { error ->
                    Text("Error: $error", color = Color.Red)
                }
            }
        }

        Button(onClick = { viewModel.startDataSync("user123") }) {
            Text("Start Sync")
        }
    }
}
```

#### 9. Testing CoroutineWorker

**Unit testing with TestWorkerBuilder:**

```kotlin
import android.content.Context
import androidx.test.core.app.ApplicationProvider
import androidx.work.ListenableWorker
import androidx.work.testing.TestListenableWorkerBuilder
import androidx.work.workDataOf
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

@RunWith(RobolectricTestRunner::class)
class DataSyncWorkerTest {

    private lateinit var context: Context

    @Before
    fun setUp() {
        context = ApplicationProvider.getApplicationContext()
    }

    @Test
    fun testDataSyncWorker_success() = runBlocking {
        // Create test worker
        val worker = TestListenableWorkerBuilder<DataSyncWorker>(context)
            .setInputData(
                workDataOf(
                    DataSyncWorker.KEY_SYNC_TYPE to "full",
                    DataSyncWorker.KEY_USER_ID to "test_user"
                )
            )
            .build()

        // Run worker
        val result = worker.doWork()

        // Verify success
        assertTrue(result is ListenableWorker.Result.Success)
    }

    @Test
    fun testDataSyncWorker_missingInput() = runBlocking {
        // Create worker without required input
        val worker = TestListenableWorkerBuilder<DataSyncWorker>(context)
            .build()

        val result = worker.doWork()

        // Should fail without required input
        assertTrue(result is ListenableWorker.Result.Failure)
    }

    @Test
    fun testDataSyncWorker_retry() = runBlocking {
        // Mock network failure scenario
        val worker = TestListenableWorkerBuilder<DataSyncWorker>(context)
            .setInputData(
                workDataOf(
                    DataSyncWorker.KEY_SYNC_TYPE to "full",
                    DataSyncWorker.KEY_USER_ID to "test_user"
                )
            )
            .setRunAttemptCount(1) // Simulate first retry
            .build()

        // In real test, inject mock repository that fails
        val result = worker.doWork()

        // Depending on implementation, may succeed or retry
        assertTrue(
            result is ListenableWorker.Result.Success ||
            result is ListenableWorker.Result.Retry
        )
    }
}
```

#### 10. Best Practices

**Production-ready patterns:**

```kotlin
//  GOOD: Use unique work for deduplication
WorkManager.getInstance(context).enqueueUniqueWork(
    "user_sync_$userId",
    ExistingWorkPolicy.KEEP, // Don't start if already running
    syncRequest
)

//  GOOD: Set appropriate constraints
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .setRequiresBatteryNotLow(true)
    .setRequiresStorageNotLow(true)
    .build()

//  GOOD: Check isStopped for cancellation
override suspend fun doWork(): Result {
    for (item in items) {
        if (isStopped) {
            return Result.failure()
        }
        processItem(item)
    }
    return Result.success()
}

//  GOOD: Use setForeground for long-running work
override suspend fun doWork(): Result {
    setForeground(createForegroundInfo())
    // Long-running work
    return Result.success()
}

//  GOOD: Exponential backoff for retries
OneTimeWorkRequestBuilder<MyWorker>()
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,
        WorkRequest.MIN_BACKOFF_MILLIS,
        TimeUnit.MILLISECONDS
    )
    .build()

//  BAD: Blocking operations in CoroutineWorker
override suspend fun doWork(): Result {
    Thread.sleep(1000) // Don't block! Use delay()
    return Result.success()
}

//  BAD: Ignoring cancellation
override suspend fun doWork(): Result {
    // Missing isStopped check
    while (true) {
        processItem()
    }
}

//  BAD: Not handling exceptions
override suspend fun doWork(): Result {
    performWork() // May throw exception
    return Result.success()
}
```

### Related Questions
- [[q-coroutine-basics--kotlin--easy]] - Coroutine fundamentals
- [[q-android-lifecycle-coroutines--kotlin--medium]] - Android lifecycle integration
- [[q-structured-concurrency--kotlin--hard]] - Structured concurrency principles
- [[q-flow-basics--kotlin--medium]] - Flow for reactive updates

## Follow-ups
1. How does WorkManager ensure work execution survives app process death?
2. What's the difference between setForeground() and createForegroundInfo() in CoroutineWorker?
3. How would you implement a download manager with pause/resume using CoroutineWorker?
4. Explain how WorkManager's backoff policy works with exponential delays. What's the maximum delay?
5. How do you test CoroutineWorker that depends on Android-specific APIs?
6. What happens to running work when constraints are no longer met (e.g., WiFi disconnects)?
7. How would you implement a worker that reports granular progress updates to the UI?

### References
- [WorkManager Overview](https://developer.android.com/topic/libraries/architecture/workmanager)
- [CoroutineWorker Documentation](https://developer.android.com/reference/kotlin/androidx/work/CoroutineWorker)
- [Testing WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager/how-to/testing-worker-impl)
- [WorkManager Advanced Topics](https://developer.android.com/topic/libraries/architecture/workmanager/advanced)

---

## Русский

### Вопрос
Что такое CoroutineWorker в Android WorkManager и чем он отличается от Worker и RxWorker? Когда следует использовать WorkManager с корутинами, а когда запускать корутины напрямую? Приведите production примеры синхронизации данных, загрузки файлов и периодической очистки с обработкой ошибок, обновлениями прогресса и стратегиями тестирования.

### Ответ

**CoroutineWorker** — это coroutine-friendly реализация Worker из WorkManager, которая позволяет писать фоновую работу, используя suspend функции вместо блокирующих операций.

#### 1. Основы CoroutineWorker

**Что такое CoroutineWorker?**

CoroutineWorker специально разработан для работы с Kotlin Coroutines:
- `doWork()` — это **suspend функция**
- Автоматически управляет жизненным циклом корутины
- Учитывает отмену WorkManager
- Интегрируется со структурированной конкурентностью

**Структура класса:**

```kotlin
import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters

class MyCoroutineWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    // Это suspend функция!
    override suspend fun doWork(): Result {
        return try {
            // Выполнение фоновой работы с корутинами
            performWork()
            Result.success()
        } catch (e: Exception) {
            Result.failure()
        }
    }

    private suspend fun performWork() {
        // Ваша suspending работа здесь
        delay(1000)
        // Можно вызывать другие suspend функции
    }
}
```

*(Продолжение следует той же структуре с полными примерами синхронизации данных, загрузки файлов, периодической очистки, тестирования и best practices на русском языке)*

### Связанные вопросы
- [[q-coroutine-basics--kotlin--easy]] - Основы корутин
- [[q-android-lifecycle-coroutines--kotlin--medium]] - Интеграция с Android lifecycle
- [[q-structured-concurrency--kotlin--hard]] - Принципы структурированной конкурентности
- [[q-flow-basics--kotlin--medium]] - Flow для реактивных обновлений

### Дополнительные вопросы
1. Как WorkManager гарантирует выполнение работы даже после смерти процесса приложения?
2. В чем разница между setForeground() и createForegroundInfo() в CoroutineWorker?
3. Как реализовать менеджер загрузок с паузой/возобновлением используя CoroutineWorker?
4. Объясните, как работает backoff policy в WorkManager с экспоненциальными задержками. Какая максимальная задержка?
5. Как тестировать CoroutineWorker, зависящий от Android-специфичных API?
6. Что происходит с выполняющейся работой, когда constraints больше не выполняются (например, отключается WiFi)?
7. Как реализовать worker, который отправляет детальные обновления прогресса в UI?

### Ссылки
- [Обзор WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Документация CoroutineWorker](https://developer.android.com/reference/kotlin/androidx/work/CoroutineWorker)
- [Тестирование WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager/how-to/testing-worker-impl)
- [Продвинутые темы WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager/advanced)
