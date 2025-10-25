---
id: 20251012-1227111103
title: "WorkManager Advanced / Продвинутый WorkManager"
aliases: [WorkManager Advanced, Продвинутый WorkManager]
topic: android
subtopics: [background-execution]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-workmanager, q-workmanager-vs-alternatives--android--medium, q-workmanager-return-result--android--medium]
created: 2025-10-12
updated: 2025-01-25
tags: [android/background-execution, workmanager, background-processing, jetpack, difficulty/medium]
sources: [https://developer.android.com/topic/libraries/architecture/workmanager]
---

# Вопрос (RU)
> Какие продвинутые возможности WorkManager?

# Question (EN)
> What are the advanced features of WorkManager?

---

## Ответ (RU)

**Теория WorkManager:**
WorkManager обеспечивает гарантированное выполнение откладываемой фоновой работы с поддержкой ограничений, цепочек задач и автоматического восстановления после перезагрузок.

**Constraints (Ограничения):**
Ограничения позволяют WorkManager выполнять работу только при выполнении определенных условий для экономии батареи и данных.

```kotlin
// Ограничения для загрузки фото
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED) // Только WiFi
    .setRequiresBatteryNotLow(true) // Батарея не разряжена
    .setRequiresCharging(false) // Не обязательно заряжать
    .build()

val uploadRequest = OneTimeWorkRequestBuilder<PhotoUploadWorker>()
    .setConstraints(constraints)
    .build()
```

**Periodic Work (Периодическая работа):**
Минимальный интервал 15 минут с возможностью гибкого окна выполнения.

```kotlin
// Ежедневная синхронизация с гибким окном
val syncRequest = PeriodicWorkRequestBuilder<DataSyncWorker>(
    repeatInterval = 24, TimeUnit.HOURS,
    flexTimeInterval = 2, TimeUnit.HOURS
)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()

WorkManager.getInstance(context)
    .enqueueUniquePeriodicWork("daily_sync", ExistingPeriodicWorkPolicy.KEEP, syncRequest)
```

**Work Chaining (Цепочки задач):**
Последовательное и параллельное выполнение задач с передачей данных между ними.

```kotlin
// Последовательная цепочка: загрузка → обработка → отправка
val downloadRequest = OneTimeWorkRequestBuilder<DownloadWorker>().build()
val processRequest = OneTimeWorkRequestBuilder<ProcessWorker>().build()
val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>().build()

WorkManager.getInstance(context)
    .beginWith(downloadRequest)
    .then(processRequest)
    .then(uploadRequest)
    .enqueue()
```

**ExistingWorkPolicy:**
Управление поведением при повторном запуске уникальных задач.

```kotlin
// REPLACE - отменить существующую, запустить новую
WorkManager.getInstance(context)
    .enqueueUniqueWork("sync", ExistingWorkPolicy.REPLACE, syncRequest)

// KEEP - сохранить существующую, игнорировать новую
WorkManager.getInstance(context)
    .enqueueUniqueWork("cleanup", ExistingWorkPolicy.KEEP, cleanupRequest)

// APPEND - добавить в очередь после существующей
WorkManager.getInstance(context)
    .enqueueUniqueWork("queue", ExistingWorkPolicy.APPEND, queueRequest)
```

**Surviving Updates/Reboots:**
WorkManager сохраняет задачи в SQLite и автоматически восстанавливает их после перезагрузки или обновления приложения.

```kotlin
// Миграция базы данных после обновления
@HiltWorker
class MigrationWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val database: AppDatabase
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val fromVersion = inputData.getInt("from_version", 0)
            database.migrate(fromVersion, BuildConfig.VERSION_CODE)
            Result.success()
        } catch (e: Exception) {
            Result.failure()
        }
    }
}
```

**Progress Tracking:**
Отслеживание прогресса выполнения задач в UI.

```kotlin
// В Worker
setProgress(workDataOf("progress" to 50, "current_file" to "photo.jpg"))

// В ViewModel
val workProgress = workManager.getWorkInfoByIdLiveData(workId)
val progress = workProgress.map { it?.progress?.getInt("progress", 0) ?: 0 }
```

## Answer (EN)

**WorkManager Theory:**
WorkManager provides guaranteed execution of deferrable background work with constraint support, work chaining, and automatic recovery after reboots.

**Constraints:**
Constraints allow WorkManager to execute work only when specific conditions are met to preserve battery and data.

```kotlin
// Constraints for photo upload
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED) // WiFi only
    .setRequiresBatteryNotLow(true) // Battery not low
    .setRequiresCharging(false) // Not required to charge
    .build()

val uploadRequest = OneTimeWorkRequestBuilder<PhotoUploadWorker>()
    .setConstraints(constraints)
    .build()
```

**Periodic Work:**
Minimum interval of 15 minutes with flexible execution window.

```kotlin
// Daily sync with flexible window
val syncRequest = PeriodicWorkRequestBuilder<DataSyncWorker>(
    repeatInterval = 24, TimeUnit.HOURS,
    flexTimeInterval = 2, TimeUnit.HOURS
)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()

WorkManager.getInstance(context)
    .enqueueUniquePeriodicWork("daily_sync", ExistingPeriodicWorkPolicy.KEEP, syncRequest)
```

**Work Chaining:**
Sequential and parallel task execution with data passing between tasks.

```kotlin
// Sequential chain: download → process → upload
val downloadRequest = OneTimeWorkRequestBuilder<DownloadWorker>().build()
val processRequest = OneTimeWorkRequestBuilder<ProcessWorker>().build()
val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>().build()

WorkManager.getInstance(context)
    .beginWith(downloadRequest)
    .then(processRequest)
    .then(uploadRequest)
    .enqueue()
```

**ExistingWorkPolicy:**
Controls behavior when restarting unique tasks.

```kotlin
// REPLACE - cancel existing, start new
WorkManager.getInstance(context)
    .enqueueUniqueWork("sync", ExistingWorkPolicy.REPLACE, syncRequest)

// KEEP - keep existing, ignore new
WorkManager.getInstance(context)
    .enqueueUniqueWork("cleanup", ExistingWorkPolicy.KEEP, cleanupRequest)

// APPEND - add to queue after existing
WorkManager.getInstance(context)
    .enqueueUniqueWork("queue", ExistingWorkPolicy.APPEND, queueRequest)
```

**Surviving Updates/Reboots:**
WorkManager persists tasks in SQLite and automatically restores them after reboot or app update.

```kotlin
// Database migration after update
@HiltWorker
class MigrationWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val database: AppDatabase
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val fromVersion = inputData.getInt("from_version", 0)
            database.migrate(fromVersion, BuildConfig.VERSION_CODE)
            Result.success()
        } catch (e: Exception) {
            Result.failure()
        }
    }
}
```

**Progress Tracking:**
Track task execution progress in UI.

```kotlin
// In Worker
setProgress(workDataOf("progress" to 50, "current_file" to "photo.jpg"))

// In ViewModel
val workProgress = workManager.getWorkInfoByIdLiveData(workId)
val progress = workProgress.map { it?.progress?.getInt("progress", 0) ?: 0 }
```

---

## Follow-ups

- How do you handle WorkManager constraints across different Android versions?
- What are the performance implications of work chaining?
- How do you test WorkManager persistence and recovery?

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components
- [[q-android-lifecycle--android--easy]] - Lifecycle management

### Related (Same Level)
- [[q-workmanager-vs-alternatives--android--medium]] - WorkManager alternatives
- [[q-workmanager-return-result--android--medium]] - WorkManager results
- [[q-android-background-limits--android--medium]] - Background limits

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] - Runtime internals
- [[q-coroutines-structured-concurrency--coroutines--hard]] - Structured concurrency
