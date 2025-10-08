---
topic: android
tags:
  - android
  - android/background-processing
  - android/services
  - android/workmanager
  - background-processing
  - foreground-service
  - jobscheduler
  - services
  - workmanager
difficulty: medium
status: reviewed
---

# How to keep service running in background?

**Russian**: Что делать если нужно чтобы сервис продолжал работу в фоне?

**English**: What to do if you need a service to continue running in the background?

## Answer

To keep a service running in the background, choose the right approach based on your needs:

1. **`startForegroundService()`** - For high-priority tasks that need user awareness
2. **`WorkManager`** - For long-running tasks with power efficiency considerations
3. **`JobScheduler`** - For tasks requiring network connectivity or specific conditions

Each has different guarantees, restrictions, and use cases.

---

## Option 1: Foreground Service (High Priority)

### When to Use

**Use foreground service when:**
- ✅ Task is **user-initiated** and **time-sensitive**
- ✅ User **expects** the task to continue (music playback, navigation)
- ✅ Task requires **immediate execution**
- ✅ You can show a **persistent notification**

**Don't use when:**
- ❌ Task is **deferrable** (can wait until better conditions)
- ❌ User is **unaware** of the task
- ❌ Task is **periodic** (daily sync, etc.)

---

### Implementation

```kotlin
class DownloadService : Service() {
    private val NOTIFICATION_ID = 1

    override fun onCreate() {
        super.onCreate()
        // Must call startForeground() within 5 seconds on Android 8.0+
        startForeground(NOTIFICATION_ID, createNotification())
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Start long-running task
        CoroutineScope(Dispatchers.IO).launch {
            try {
                downloadLargeFile()
                // Task completes successfully
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            } catch (e: Exception) {
                // Handle error
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            }
        }

        return START_STICKY  // Restart if killed
    }

    private fun createNotification(): Notification {
        val channelId = "download_channel"

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Downloads",
                NotificationManager.IMPORTANCE_LOW
            )
            getSystemService(NotificationManager::class.java)
                .createNotificationChannel(channel)
        }

        return NotificationCompat.Builder(this, channelId)
            .setContentTitle("Downloading file")
            .setContentText("Download in progress...")
            .setSmallIcon(android.R.drawable.stat_sys_download)
            .setOngoing(true)
            .build()
    }

    private suspend fun downloadLargeFile() {
        // Actual download logic
        for (i in 1..100) {
            delay(100)
            updateProgress(i)
        }
    }

    private fun updateProgress(progress: Int) {
        val notification = NotificationCompat.Builder(this, "download_channel")
            .setContentTitle("Downloading file")
            .setContentText("Progress: $progress%")
            .setSmallIcon(android.R.drawable.stat_sys_download)
            .setProgress(100, progress, false)
            .setOngoing(true)
            .build()

        val notificationManager = getSystemService(NotificationManager::class.java)
        notificationManager.notify(NOTIFICATION_ID, notification)
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**Starting the service:**

```kotlin
class MainActivity : AppCompatActivity() {

    private fun startDownload() {
        val intent = Intent(this, DownloadService::class.java)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
    }
}
```

**Manifest:**

```xml
<manifest>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <application>
        <service
            android:name=".DownloadService"
            android:foregroundServiceType="dataSync"
            android:exported="false" />
    </application>
</manifest>
```

---

## Option 2: WorkManager (Recommended for Most Cases)

### When to Use

**Use WorkManager when:**
- ✅ Task is **deferrable** (can wait for optimal conditions)
- ✅ Task should **survive app restarts**
- ✅ You need **guaranteed execution** (even after device reboot)
- ✅ You care about **battery optimization**

**Examples:**
- Uploading logs to server
- Syncing data periodically
- Backing up photos when on WiFi
- Processing images in background

---

### Implementation

**1. Create a Worker:**

```kotlin
class UploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            // Get input data
            val fileUrl = inputData.getString("file_url") ?: return Result.failure()

            // Show notification for long-running work
            setForeground(createForegroundInfo())

            // Perform upload
            uploadFile(fileUrl)

            // Return success
            Result.success()
        } catch (e: Exception) {
            // Retry on failure
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure()
            }
        }
    }

    private fun createForegroundInfo(): ForegroundInfo {
        val channelId = "upload_channel"

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Uploads",
                NotificationManager.IMPORTANCE_LOW
            )
            val notificationManager = applicationContext.getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }

        val notification = NotificationCompat.Builder(applicationContext, channelId)
            .setContentTitle("Uploading file")
            .setContentText("Upload in progress...")
            .setSmallIcon(android.R.drawable.stat_sys_upload)
            .setOngoing(true)
            .build()

        return ForegroundInfo(NOTIFICATION_ID, notification)
    }

    private suspend fun uploadFile(fileUrl: String) {
        // Actual upload logic
        withContext(Dispatchers.IO) {
            // Upload implementation
        }
    }

    companion object {
        private const val NOTIFICATION_ID = 2
    }
}
```

**2. Schedule the Work:**

```kotlin
class MainActivity : AppCompatActivity() {

    private fun scheduleUpload(fileUrl: String) {
        // Create input data
        val inputData = workDataOf("file_url" to fileUrl)

        // Create constraints
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)  // Needs internet
            .setRequiresBatteryNotLow(true)  // Wait until battery is OK
            .build()

        // Create work request
        val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>()
            .setInputData(inputData)
            .setConstraints(constraints)
            .setBackoffCriteria(
                BackoffPolicy.EXPONENTIAL,
                WorkRequest.MIN_BACKOFF_MILLIS,
                TimeUnit.MILLISECONDS
            )
            .build()

        // Enqueue work
        WorkManager.getInstance(this).enqueue(uploadRequest)
    }

    private fun schedulePeriodicSync() {
        val syncRequest = PeriodicWorkRequestBuilder<UploadWorker>(
            15,  // Minimum interval: 15 minutes
            TimeUnit.MINUTES
        )
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.UNMETERED)  // WiFi only
                    .build()
            )
            .build()

        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            "periodic_sync",
            ExistingPeriodicWorkPolicy.KEEP,
            syncRequest
        )
    }
}
```

**3. Observe Work Status:**

```kotlin
WorkManager.getInstance(this)
    .getWorkInfoByIdLiveData(uploadRequest.id)
    .observe(this) { workInfo ->
        when (workInfo?.state) {
            WorkInfo.State.ENQUEUED -> Log.d("Upload", "Queued")
            WorkInfo.State.RUNNING -> Log.d("Upload", "Running")
            WorkInfo.State.SUCCEEDED -> Log.d("Upload", "Success")
            WorkInfo.State.FAILED -> Log.d("Upload", "Failed")
            WorkInfo.State.CANCELLED -> Log.d("Upload", "Cancelled")
            else -> {}
        }
    }
```

**Dependencies:**

```gradle
// build.gradle
dependencies {
    implementation "androidx.work:work-runtime-ktx:2.9.0"
}
```

---

## Option 3: JobScheduler (System-Managed)

### When to Use

**Use JobScheduler when:**
- ✅ Task requires **specific conditions** (network type, charging, idle)
- ✅ Task is **not time-critical**
- ✅ You want **system to optimize** execution time
- ✅ You don't need WorkManager features (chaining, unique work)

**Note:** WorkManager uses JobScheduler internally on Android 6.0+, so WorkManager is usually preferred.

---

### Implementation

**1. Create a JobService:**

```kotlin
class SyncJobService : JobService() {

    private var job: Job? = null

    override fun onStartJob(params: JobParameters?): Boolean {
        // Return true if work is ongoing (asynchronous)
        job = CoroutineScope(Dispatchers.IO).launch {
            try {
                performSync()
                // Notify system job is complete
                jobFinished(params, false)  // false = don't reschedule
            } catch (e: Exception) {
                // Reschedule on failure
                jobFinished(params, true)  // true = reschedule
            }
        }

        return true  // Work is ongoing
    }

    override fun onStopJob(params: JobParameters?): Boolean {
        // Called when system decides to stop job early
        job?.cancel()
        return true  // true = reschedule, false = drop
    }

    private suspend fun performSync() {
        // Actual sync logic
        delay(5000)
        Log.d("JobService", "Sync completed")
    }
}
```

**2. Schedule the Job:**

```kotlin
class MainActivity : AppCompatActivity() {

    private fun scheduleJob() {
        val jobScheduler = getSystemService(JobScheduler::class.java)

        val job = JobInfo.Builder(
            JOB_ID,
            ComponentName(this, SyncJobService::class.java)
        )
            .setRequiredNetworkType(JobInfo.NETWORK_TYPE_ANY)
            .setPersisted(true)  // Survive reboot
            .setPeriodic(15 * 60 * 1000L)  // Every 15 minutes
            .build()

        val result = jobScheduler.schedule(job)

        if (result == JobScheduler.RESULT_SUCCESS) {
            Log.d("JobScheduler", "Job scheduled successfully")
        } else {
            Log.e("JobScheduler", "Job scheduling failed")
        }
    }

    companion object {
        private const val JOB_ID = 100
    }
}
```

**Manifest:**

```xml
<manifest>
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />

    <application>
        <service
            android:name=".SyncJobService"
            android:permission="android.permission.BIND_JOB_SERVICE"
            android:exported="true" />
    </application>
</manifest>
```

---

## Comparison: Which to Choose?

| Criteria | Foreground Service | WorkManager | JobScheduler |
|----------|-------------------|-------------|--------------|
| **User awareness** | Required (notification) | Optional | Not required |
| **Priority** | High (won't be killed) | Medium | Low |
| **Execution timing** | Immediate | Deferred (optimized) | Deferred (system decides) |
| **Constraints** | None | Network, battery, storage | Network, charging, idle |
| **Survives reboot** | No | Yes | Yes (if persisted) |
| **Min Android version** | All | 4.0+ (API 14+) | 5.0+ (API 21+) |
| **Use case** | Music, navigation, download | Background sync, uploads | Periodic sync, cleanup |

---

## Advanced: Combining Approaches

### Example: Smart Upload Service

```kotlin
class SmartUploadManager(private val context: Context) {

    fun uploadFile(fileUrl: String, isUrgent: Boolean) {
        if (isUrgent) {
            // User-initiated, immediate upload
            startForegroundServiceUpload(fileUrl)
        } else {
            // Background upload, use WorkManager
            scheduleWorkManagerUpload(fileUrl)
        }
    }

    private fun startForegroundServiceUpload(fileUrl: String) {
        val intent = Intent(context, UploadService::class.java).apply {
            putExtra("file_url", fileUrl)
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.startForegroundService(intent)
        } else {
            context.startService(intent)
        }
    }

    private fun scheduleWorkManagerUpload(fileUrl: String) {
        val inputData = workDataOf("file_url" to fileUrl)

        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.UNMETERED)  // WiFi only
            .setRequiresBatteryNotLow(true)
            .build()

        val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>()
            .setInputData(inputData)
            .setConstraints(constraints)
            .build()

        WorkManager.getInstance(context).enqueue(uploadRequest)
    }
}
```

**Usage:**

```kotlin
val uploadManager = SmartUploadManager(this)

// User taps "Upload Now" button
uploadManager.uploadFile(fileUrl, isUrgent = true)  // Foreground service

// Auto-backup in background
uploadManager.uploadFile(fileUrl, isUrgent = false)  // WorkManager
```

---

## Best Practices

### 1. Choose the Right Tool

```kotlin
// ❌ BAD: Foreground service for periodic sync
class PeriodicSyncService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(1, notification)  // User doesn't need to see this!
        syncData()
        return START_STICKY
    }
}

// ✅ GOOD: WorkManager for periodic sync
val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
    .build()
WorkManager.getInstance(context).enqueue(syncRequest)
```

### 2. Handle Android Version Differences

```kotlin
fun startBackgroundTask() {
    when {
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            // Android 12+: Restrictions on foreground service starts from background
            useWorkManager()
        }
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.O -> {
            // Android 8+: Must use startForegroundService()
            startForegroundService()
        }
        else -> {
            // Older versions: Regular service
            startService()
        }
    }
}
```

### 3. Stop Services When Done

```kotlin
// ✅ Always stop service when task completes
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    CoroutineScope(Dispatchers.IO).launch {
        try {
            performTask()
        } finally {
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelf()  // Don't forget this!
        }
    }
    return START_NOT_STICKY
}
```

---

## Summary

**How to keep a service running in background:**

### 1. **Foreground Service**
- **Use for:** User-visible, time-sensitive tasks
- **Method:** `startForegroundService()` + `startForeground()`
- **Pros:** High priority, won't be killed
- **Cons:** Requires notification, user awareness

### 2. **WorkManager** (Recommended)
- **Use for:** Deferrable background tasks
- **Method:** Create Worker, enqueue with constraints
- **Pros:** Battery efficient, survives reboot, guaranteed execution
- **Cons:** Not immediate execution

### 3. **JobScheduler**
- **Use for:** System-optimized periodic tasks
- **Method:** Create JobService, schedule with JobScheduler
- **Pros:** System-managed, constraint-based
- **Cons:** Requires API 21+, less flexible than WorkManager

**Decision flowchart:**
```
Is task user-initiated and time-sensitive?
├─ YES → Foreground Service
└─ NO → Is task deferrable?
    ├─ YES → WorkManager
    └─ NO → Consider task necessity
        (Most tasks are deferrable!)
```

---

## Ответ

Для продолжения работы сервиса в фоне используйте:

1. **`startForegroundService()`** - для задач с высоким приоритетом, требующих уведомления пользователя
2. **`WorkManager`** - для длительных задач с учётом энергопотребления (рекомендуется)
3. **`JobScheduler`** - для задач, требующих сетевого подключения или определенных условий

**Когда что использовать:**
- **Foreground Service**: музыка, навигация, срочная загрузка
- **WorkManager**: синхронизация данных, загрузка в фоне, периодические задачи
- **JobScheduler**: системно-оптимизированные периодические задачи

