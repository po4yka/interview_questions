---
id: 20251012-1227111106
title: "Workmanager Execution Guarantee / Гарантия выполнения WorkManager"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [workmanager, background-tasks, reliability, difficulty/medium]
---
# How does WorkManager guarantee task execution?

**Russian**: Как WorkManager гарантирует выполнение задач?

## Answer (EN)
WorkManager guarantees task execution through a combination of persistent storage, system constraints monitoring, and integration with various Android background execution mechanisms. It ensures that work will execute even if the app exits or the device restarts.

### Core Guarantees

WorkManager provides several key guarantees:

1. **Task persistence** - Work requests survive app and device restarts
2. **Constraint-based execution** - Respects system constraints (network, battery, storage)
3. **Automatic retry** - Failed tasks are retried with configurable backoff policy
4. **Ordering** - Work chains maintain execution order
5. **Threading** - Work always executes off the main thread

### How WorkManager Guarantees Execution

#### 1. Persistent Storage

WorkManager stores all work requests in a SQLite database, ensuring they survive across:
- App restarts
- Device reboots
- Process death

```kotlin
// Work is saved to database immediately
val workRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setInputData(workDataOf("file_path" to "/path/to/file"))
    .build()

WorkManager.getInstance(context).enqueue(workRequest)
// Even if app crashes here, work is persisted
```

**Database structure:**
- Work requests
- Worker parameters
- Constraints
- Retry count
- Output data

#### 2. System Integration

WorkManager uses the best available background execution mechanism for each Android version:

| Android Version | Mechanism |
|-----------------|-----------|
| API 23+ | JobScheduler |
| API 14-22 | AlarmManager + BroadcastReceiver |
| All versions | Custom AlarmManager + WorkManager Service |

```kotlin
// WorkManager automatically chooses the right executor
class BackupWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        // This will execute reliably on any Android version
        return try {
            performBackup()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}
```

#### 3. Constraint-Based Execution

Work only executes when all constraints are met. WorkManager monitors system state and automatically starts work when conditions are satisfied.

```kotlin
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .setRequiresBatteryNotLow(true)
    .setRequiresStorageNotLow(true)
    .setRequiresCharging(false)
    .setRequiresDeviceIdle(false)
    .build()

val workRequest = OneTimeWorkRequestBuilder<SyncWorker>()
    .setConstraints(constraints)
    .build()

WorkManager.getInstance(context).enqueue(workRequest)
```

**What happens:**
1. Work is enqueued and saved to database
2. WorkManager monitors system state
3. When ALL constraints are met → work executes
4. If constraints change during execution → work can be stopped
5. Work will restart when constraints are met again

#### 4. Automatic Retry with Backoff

Failed work is automatically retried with exponential backoff:

```kotlin
class RetryableWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val result = uploadData()
            Result.success(workDataOf("upload_id" to result.id))
        } catch (e: IOException) {
            // Network error - retry
            if (runAttemptCount < 5) {
                Result.retry()  // Will retry with backoff
            } else {
                Result.failure()
            }
        } catch (e: Exception) {
            // Non-recoverable error
            Result.failure()
        }
    }
}

// Configure backoff policy
val workRequest = OneTimeWorkRequestBuilder<RetryableWorker>()
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,
        OneTimeWorkRequest.MIN_BACKOFF_MILLIS,  // 10 seconds
        TimeUnit.MILLISECONDS
    )
    .build()
```

**Backoff calculation:**
```
EXPONENTIAL: delay = min(10s * 2^(attempts - 1), 5 hours)
LINEAR: delay = min(10s * attempts, 5 hours)

Attempt 1: 10s
Attempt 2: 20s
Attempt 3: 40s
Attempt 4: 80s
...
```

#### 5. Work States and Lifecycle

WorkManager tracks work through various states to ensure execution:

```
                ENQUEUED
                    ↓
                RUNNING
                    ↓
        
        ↓           ↓           ↓
    SUCCEEDED    FAILED     CANCELLED

For periodic work:

    ENQUEUED → RUNNING → ENQUEUED (repeats)
```

**State transitions:**

```kotlin
// Observe work state
WorkManager.getInstance(context)
    .getWorkInfoByIdLiveData(workRequest.id)
    .observe(lifecycleOwner) { workInfo ->
        when (workInfo.state) {
            WorkInfo.State.ENQUEUED -> {
                // Waiting for constraints or scheduling
                Log.d("Work", "Work is queued")
            }
            WorkInfo.State.RUNNING -> {
                // Currently executing
                Log.d("Work", "Work is running")
            }
            WorkInfo.State.SUCCEEDED -> {
                // Completed successfully
                val result = workInfo.outputData.getString("result")
                Log.d("Work", "Work succeeded: $result")
            }
            WorkInfo.State.FAILED -> {
                // Failed permanently (no more retries)
                Log.d("Work", "Work failed")
            }
            WorkInfo.State.BLOCKED -> {
                // Waiting for prerequisite work
                Log.d("Work", "Work is blocked")
            }
            WorkInfo.State.CANCELLED -> {
                // Cancelled by user or system
                Log.d("Work", "Work was cancelled")
            }
        }
    }
```

#### 6. Work Chaining Guarantees

WorkManager ensures ordered execution in work chains:

```kotlin
val workA = OneTimeWorkRequestBuilder<WorkerA>().build()
val workB = OneTimeWorkRequestBuilder<WorkerB>().build()
val workC = OneTimeWorkRequestBuilder<WorkerC>().build()

WorkManager.getInstance(context)
    .beginWith(workA)  // Executes first
    .then(workB)       // Executes after A succeeds
    .then(workC)       // Executes after B succeeds
    .enqueue()

// workB only starts if workA succeeds
// workC only starts if workB succeeds
// If any fails, chain stops
```

**Parallel execution:**

```kotlin
val work1 = OneTimeWorkRequestBuilder<Worker1>().build()
val work2 = OneTimeWorkRequestBuilder<Worker2>().build()
val work3 = OneTimeWorkRequestBuilder<Worker3>().build()
val finalWork = OneTimeWorkRequestBuilder<FinalWorker>().build()

WorkManager.getInstance(context)
    .beginWith(listOf(work1, work2, work3))  // Execute in parallel
    .then(finalWork)  // Execute after all complete
    .enqueue()
```

### Device Reboot Handling

WorkManager automatically restarts work after device reboot:

**Manifest configuration:**

```xml
<!-- WorkManager adds this automatically -->
<receiver
    android:name="androidx.work.impl.utils.ForceStopRunnable$BroadcastReceiver"
    android:enabled="true"
    android:exported="false">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
        <action android:name="android.intent.action.MY_PACKAGE_REPLACED" />
    </intent-filter>
</receiver>
```

**Behavior after reboot:**

```kotlin
// 1. Schedule work
val workRequest = OneTimeWorkRequestBuilder<BackupWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(workRequest)

// 2. Device reboots

// 3. After reboot:
//    - WorkManager automatically restarts
//    - Reads persisted work from database
//    - Re-schedules work with JobScheduler/AlarmManager
//    - Work executes when constraints are met
```

### Periodic Work Guarantees

Periodic work is guaranteed to execute at specified intervals:

```kotlin
val periodicWork = PeriodicWorkRequestBuilder<SyncWorker>(
    15, TimeUnit.MINUTES  // Minimum interval: 15 minutes
).setConstraints(
    Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .build()
).build()

WorkManager.getInstance(context).enqueue(periodicWork)
```

**Guarantees:**
- Executes approximately every 15 minutes (not exact)
- Survives app restarts and device reboots
- Respects system Doze mode and battery optimization
- Flex interval allows for optimization:

```kotlin
// Execute once every 2 hours, with 30 min flex at the end
val periodicWork = PeriodicWorkRequestBuilder<SyncWorker>(
    repeatInterval = 2, repeatIntervalTimeUnit = TimeUnit.HOURS,
    flexTimeInterval = 30, flexTimeIntervalUnit = TimeUnit.MINUTES
).build()

// Can execute anytime in the last 30 minutes of each 2-hour window
```

### Doze Mode and App Standby

WorkManager respects Android battery optimization:

```kotlin
class DozeFriendlyWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        // This work respects Doze mode
        // Will execute during maintenance windows

        return try {
            syncData()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// Urgent work that can run in Doze
val urgentWork = OneTimeWorkRequestBuilder<UrgentWorker>()
    .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
    .build()
```

### Expedited Work (Foreground Service Integration)

For urgent work that needs immediate execution:

```kotlin
class ExpeditedWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun getForegroundInfo(): ForegroundInfo {
        return ForegroundInfo(
            NOTIFICATION_ID,
            createNotification()
        )
    }

    override suspend fun doWork(): Result {
        // Runs as foreground service
        // Not subject to background execution limits

        setForeground(getForegroundInfo())

        return try {
            processUrgentData()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// Request expedited execution
val expeditedRequest = OneTimeWorkRequestBuilder<ExpeditedWorker>()
    .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
    .build()

WorkManager.getInstance(context).enqueue(expeditedRequest)
```

### Work Uniqueness Guarantees

Prevent duplicate work execution:

```kotlin
// REPLACE - Cancel existing work and enqueue new
WorkManager.getInstance(context).enqueueUniqueWork(
    "sync_work",
    ExistingWorkPolicy.REPLACE,
    workRequest
)

// KEEP - Keep existing work, ignore new request
WorkManager.getInstance(context).enqueueUniqueWork(
    "sync_work",
    ExistingWorkPolicy.KEEP,
    workRequest
)

// APPEND - Add to existing chain
WorkManager.getInstance(context).enqueueUniqueWork(
    "sync_work",
    ExistingWorkPolicy.APPEND,
    workRequest
)

// APPEND_OR_REPLACE - Append if running, replace if finished
WorkManager.getInstance(context).enqueueUniqueWork(
    "sync_work",
    ExistingWorkPolicy.APPEND_OR_REPLACE,
    workRequest
)
```

### Complete Example with All Guarantees

```kotlin
class ReliableUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val filePath = inputData.getString(KEY_FILE_PATH)
            ?: return Result.failure()

        return try {
            // Update progress
            setProgress(workDataOf("progress" to 0))

            // Perform upload
            val uploadId = uploadFile(filePath) { progress ->
                // Update progress
                setProgress(workDataOf("progress" to progress))
            }

            // Success
            Result.success(workDataOf("upload_id" to uploadId))

        } catch (e: IOException) {
            // Transient error - retry
            if (runAttemptCount < MAX_RETRIES) {
                Result.retry()
            } else {
                Result.failure(workDataOf("error" to "Max retries exceeded"))
            }
        } catch (e: Exception) {
            // Permanent error
            Result.failure(workDataOf("error" to e.message))
        }
    }

    companion object {
        const val KEY_FILE_PATH = "file_path"
        const val MAX_RETRIES = 3
    }
}

// Schedule with all guarantees
fun scheduleUpload(context: Context, filePath: String) {
    val workRequest = OneTimeWorkRequestBuilder<ReliableUploadWorker>()
        // Input data
        .setInputData(workDataOf("file_path" to filePath))

        // Constraints
        .setConstraints(
            Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .setRequiresBatteryNotLow(true)
                .build()
        )

        // Retry policy
        .setBackoffCriteria(
            BackoffPolicy.EXPONENTIAL,
            OneTimeWorkRequest.MIN_BACKOFF_MILLIS,
            TimeUnit.MILLISECONDS
        )

        .build()

    // Enqueue with uniqueness
    WorkManager.getInstance(context).enqueueUniqueWork(
        "upload_$filePath",
        ExistingWorkPolicy.KEEP,  // Don't duplicate uploads
        workRequest
    )

    // Observe progress
    WorkManager.getInstance(context)
        .getWorkInfoByIdLiveData(workRequest.id)
        .observe(lifecycleOwner) { workInfo ->
            when {
                workInfo.state == WorkInfo.State.RUNNING -> {
                    val progress = workInfo.progress.getInt("progress", 0)
                    updateUI("Uploading: $progress%")
                }
                workInfo.state == WorkInfo.State.SUCCEEDED -> {
                    val uploadId = workInfo.outputData.getString("upload_id")
                    updateUI("Upload complete: $uploadId")
                }
                workInfo.state == WorkInfo.State.FAILED -> {
                    val error = workInfo.outputData.getString("error")
                    updateUI("Upload failed: $error")
                }
            }
        }
}
```

### Summary of Guarantees

| Guarantee | How It Works |
|-----------|--------------|
| **Persistence** | Stored in SQLite database |
| **Survives reboot** | BOOT_COMPLETED receiver restarts work |
| **Constraint enforcement** | System monitors state, executes when constraints met |
| **Automatic retry** | Configurable backoff policy |
| **Ordered execution** | Work chains maintain dependencies |
| **Off main thread** | Always executes on background thread |
| **Uniqueness** | ExistingWorkPolicy prevents duplicates |
| **Doze-aware** | Respects battery optimization |
| **Version compatibility** | Uses best mechanism for each Android version |

**Key points:**
- Work is persisted immediately upon enqueueing
- Execution is guaranteed even across app/device restarts
- Constraints are strictly enforced
- Failed work is automatically retried
- System chooses optimal execution mechanism
- Work chains maintain execution order
- Periodic work runs reliably at intervals
- Integration with foreground services for urgent work

## Ответ (RU)
WorkManager гарантирует выполнение задач через комбинацию постоянного хранилища, мониторинга системных ограничений и интеграции с различными механизмами фонового выполнения Android.

### Основные гарантии

1. **Персистентность задач** - задачи переживают перезапуск приложения и устройства
2. **Выполнение по ограничениям** - соблюдает системные ограничения (сеть, батарея, хранилище)
3. **Автоматический повтор** - неудачные задачи повторяются с настраиваемой политикой backoff
4. **Упорядоченность** - цепочки работ сохраняют порядок выполнения
5. **Потоки** - работа всегда выполняется вне главного потока

### Как WorkManager гарантирует выполнение

#### 1. Постоянное хранилище

WorkManager сохраняет все запросы работы в базе данных SQLite:

```kotlin
val workRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setInputData(workDataOf("file_path" to "/path/to/file"))
    .build()

WorkManager.getInstance(context).enqueue(workRequest)
// Даже если приложение упадет, работа сохранена
```

#### 2. Интеграция с системой

WorkManager использует лучший доступный механизм для каждой версии Android:
- API 23+: JobScheduler
- API 14-22: AlarmManager + BroadcastReceiver

#### 3. Выполнение по ограничениям

Работа выполняется только когда все ограничения выполнены:

```kotlin
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .setRequiresBatteryNotLow(true)
    .build()

val workRequest = OneTimeWorkRequestBuilder<SyncWorker>()
    .setConstraints(constraints)
    .build()
```

#### 4. Автоматический повтор с backoff

```kotlin
class RetryableWorker : CoroutineWorker() {
    override suspend fun doWork(): Result {
        return try {
            uploadData()
            Result.success()
        } catch (e: IOException) {
            if (runAttemptCount < 5) {
                Result.retry()  // Повтор с backoff
            } else {
                Result.failure()
            }
        }
    }
}
```

#### 5. Обработка перезагрузки

WorkManager автоматически перезапускает работу после перезагрузки устройства через BOOT_COMPLETED receiver.

#### 6. Цепочки работ

```kotlin
WorkManager.getInstance(context)
    .beginWith(workA)
    .then(workB)
    .then(workC)
    .enqueue()
// workB выполнится только после успеха workA
```

**Резюме:** WorkManager гарантирует выполнение через персистентное хранилище в SQLite, мониторинг системных ограничений, автоматический повтор с backoff, интеграцию с JobScheduler/AlarmManager, и обработку перезагрузок устройства.
