---
id: android-065
title: "WorkManager Advanced / Продвинутый WorkManager"
aliases: ["WorkManager Advanced", "Продвинутый WorkManager"]
topic: android
subtopics: [background-execution]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-background-tasks, c-constraints, c-workmanager]
created: 2025-10-12
updated: 2025-10-29
tags: [android/background-execution, background-processing, difficulty/medium, jetpack, workmanager]
sources: [https://developer.android.com/topic/libraries/architecture/workmanager]
---

# Вопрос (RU)
> Какие продвинутые возможности WorkManager?

# Question (EN)
> What are the advanced features of WorkManager?

---

## Ответ (RU)

WorkManager обеспечивает гарантированное выполнение откладываемой фоновой работы с поддержкой ограничений, цепочек и восстановления после перезагрузок.

**Constraints (Ограничения):**
Выполнение работы только при соблюдении условий для экономии батареи и трафика.

```kotlin
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED) // ✅ WiFi only
    .setRequiresBatteryNotLow(true)                // ✅ Battery check
    .build()

val uploadRequest = OneTimeWorkRequestBuilder<PhotoUploadWorker>()
    .setConstraints(constraints)
    .build()
```

**Periodic Work:**
Минимальный интервал 15 минут с гибким окном выполнения.

```kotlin
val syncRequest = PeriodicWorkRequestBuilder<DataSyncWorker>(
    repeatInterval = 24, TimeUnit.HOURS,
    flexTimeInterval = 2, TimeUnit.HOURS  // ✅ Execution window
).build()

WorkManager.getInstance(context)
    .enqueueUniquePeriodicWork(
        "daily_sync",
        ExistingPeriodicWorkPolicy.KEEP,  // ✅ Don't restart if running
        syncRequest
    )
```

**Work Chaining:**
Последовательное/параллельное выполнение с передачей данных.

```kotlin
// Sequential: download → process → upload
WorkManager.getInstance(context)
    .beginWith(downloadRequest)
    .then(processRequest)
    .then(uploadRequest)
    .enqueue()

// Parallel + combine
WorkManager.getInstance(context)
    .beginWith(listOf(task1, task2))  // ✅ Parallel
    .then(combineRequest)              // ✅ Waits for both
    .enqueue()
```

**ExistingWorkPolicy:**
Управление дублированием уникальных задач.

```kotlin
// REPLACE — отменить существующую, запустить новую
WorkManager.getInstance(context)
    .enqueueUniqueWork("sync", ExistingWorkPolicy.REPLACE, request)

// KEEP — сохранить существующую, игнорировать новую
WorkManager.getInstance(context)
    .enqueueUniqueWork("cleanup", ExistingWorkPolicy.KEEP, request)

// APPEND — добавить в очередь после существующей
WorkManager.getInstance(context)
    .enqueueUniqueWork("queue", ExistingWorkPolicy.APPEND, request)
```

**Persistence:**
WorkManager сохраняет задачи в SQLite, восстанавливает после перезагрузки/обновления приложения.

```kotlin
@HiltWorker
class MigrationWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val database: AppDatabase
) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result = try {
        val fromVersion = inputData.getInt("from_version", 0)
        database.migrate(fromVersion, BuildConfig.VERSION_CODE)
        Result.success()  // ✅ Success with retry support
    } catch (e: Exception) {
        Result.retry()    // ✅ Retry with backoff policy
    }
}
```

**Progress Tracking:**
Обновление прогресса для UI.

```kotlin
// In Worker
setProgress(workDataOf("progress" to 50, "file" to "photo.jpg"))

// In ViewModel
val progress = workManager.getWorkInfoByIdLiveData(workId)
    .map { it?.progress?.getInt("progress", 0) ?: 0 }
```

## Answer (EN)

WorkManager provides guaranteed execution of deferrable background work with constraints, chaining, and recovery after reboots.

**Constraints:**
Execute work only when conditions are met to save battery and data.

```kotlin
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED) // ✅ WiFi only
    .setRequiresBatteryNotLow(true)                // ✅ Battery check
    .build()

val uploadRequest = OneTimeWorkRequestBuilder<PhotoUploadWorker>()
    .setConstraints(constraints)
    .build()
```

**Periodic Work:**
Minimum 15-minute interval with flexible execution window.

```kotlin
val syncRequest = PeriodicWorkRequestBuilder<DataSyncWorker>(
    repeatInterval = 24, TimeUnit.HOURS,
    flexTimeInterval = 2, TimeUnit.HOURS  // ✅ Execution window
).build()

WorkManager.getInstance(context)
    .enqueueUniquePeriodicWork(
        "daily_sync",
        ExistingPeriodicWorkPolicy.KEEP,  // ✅ Don't restart if running
        syncRequest
    )
```

**Work Chaining:**
Sequential/parallel execution with data passing.

```kotlin
// Sequential: download → process → upload
WorkManager.getInstance(context)
    .beginWith(downloadRequest)
    .then(processRequest)
    .then(uploadRequest)
    .enqueue()

// Parallel + combine
WorkManager.getInstance(context)
    .beginWith(listOf(task1, task2))  // ✅ Parallel
    .then(combineRequest)              // ✅ Waits for both
    .enqueue()
```

**ExistingWorkPolicy:**
Control behavior when re-enqueueing unique work.

```kotlin
// REPLACE — cancel existing, start new
WorkManager.getInstance(context)
    .enqueueUniqueWork("sync", ExistingWorkPolicy.REPLACE, request)

// KEEP — keep existing, ignore new
WorkManager.getInstance(context)
    .enqueueUniqueWork("cleanup", ExistingWorkPolicy.KEEP, request)

// APPEND — enqueue after existing
WorkManager.getInstance(context)
    .enqueueUniqueWork("queue", ExistingWorkPolicy.APPEND, request)
```

**Persistence:**
WorkManager persists tasks in SQLite, restores after reboot/app update.

```kotlin
@HiltWorker
class MigrationWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val database: AppDatabase
) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result = try {
        val fromVersion = inputData.getInt("from_version", 0)
        database.migrate(fromVersion, BuildConfig.VERSION_CODE)
        Result.success()  // ✅ Success with retry support
    } catch (e: Exception) {
        Result.retry()    // ✅ Retry with backoff policy
    }
}
```

**Progress Tracking:**
Update progress for UI updates.

```kotlin
// In Worker
setProgress(workDataOf("progress" to 50, "file" to "photo.jpg"))

// In ViewModel
val progress = workManager.getWorkInfoByIdLiveData(workId)
    .map { it?.progress?.getInt("progress", 0) ?: 0 }
```

---

## Follow-ups

- How do constraints behave across different Android versions (especially Android 12+ Doze restrictions)?
- What are the performance trade-offs of work chaining vs. separate Workers?
- How to handle Worker cancellation during progress tracking?
- What happens when ExistingWorkPolicy.APPEND is used with failed workers?
- How to test periodic work with flexTimeInterval in unit tests?

## References

- [[c-workmanager]] - WorkManager concepts
- [[c-android-background-execution]] - Background execution strategies
- https://developer.android.com/topic/libraries/architecture/workmanager/advanced
- https://developer.android.com/topic/libraries/architecture/workmanager/how-to/chain-work

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components overview
- [[q-android-lifecycle--android--easy]] - Lifecycle management basics
- [[q-workmanager-basics--android--easy]] - WorkManager fundamentals

### Related (Same Level)
- [[q-workmanager-vs-alternatives--android--medium]] - WorkManager vs alternatives
- [[q-workmanager-return-result--android--medium]] - Returning results from Workers
- [[q-android-background-limits--android--medium]] - Background execution limits

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] - Android runtime internals
- [[q-android-power-battery-optimization--android--hard]] - Power and battery optimization
