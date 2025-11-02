---
id: android-226
title: "What Is Workmanager / Что такое WorkManager"
aliases: ["What Is WorkManager", "Что такое WorkManager"]

# Classification
topic: android
subtopics: [background-execution, coroutines]
question_kind: android
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
sources: []

# Workflow & relations
status: draft
moc: moc-android
related: [c-background-tasks, c-coroutines, c-jetpack, c-workmanager]

# Timestamps
created: 2025-10-15
updated: 2025-10-29

# Tags (EN only; no leading #)
tags: [android/background-execution, android/coroutines, difficulty/medium, jetpack, scheduled-tasks, workmanager]
date created: Saturday, November 1st 2025, 1:26:05 pm
date modified: Saturday, November 1st 2025, 5:43:30 pm
---

# Вопрос (RU)
> Что такое WorkManager и когда его следует использовать?

# Question (EN)
> What is WorkManager and when should it be used?

---

## Ответ (RU)

**WorkManager** — это Jetpack библиотека для **откладываемых гарантированных фоновых задач**, которые должны выполняться даже при закрытии приложения или перезагрузке устройства.

### Ключевые Особенности

**Гарантированное выполнение**: задачи сохраняются в SQLite БД и переживают перезагрузки, уничтожение процесса, режим Doze.

**Умный выбор механизма**: автоматически использует JobScheduler (API 23+) или AlarmManager + BroadcastReceiver (API 14-22).

**Ограничения выполнения**: декларативно задаются условия — сеть, зарядка, уровень батареи, свободное место.

**Цепочки работ**: последовательное и параллельное выполнение с передачей данных между задачами.

**Интеграция с корутинами**: `CoroutineWorker` для suspend-функций без блокировки потоков.

### Основные Компоненты

```kotlin
// 1. Worker — определяет задачу
class UploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        try {
            val path = inputData.getString("file_path") ?: return@withContext Result.failure()
            uploadFile(path)
            Result.success() // ✅ задача завершена
        } catch (e: Exception) {
            if (runAttemptCount < 3) Result.retry() // ✅ повторить с экспоненциальной задержкой
            else Result.failure() // ❌ окончательный провал
        }
    }
}

// 2. WorkRequest — описывает когда и как запустить
val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setInputData(workDataOf("file_path" to "/path/to/file"))
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED) // ✅ только при наличии сети
            .setRequiresBatteryNotLow(true)                // ✅ батарея > 15%
            .build()
    )
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,
        15, TimeUnit.SECONDS // ✅ повторы: 15s → 30s → 60s...
    )
    .build()

// 3. WorkManager — управляет выполнением
WorkManager.getInstance(context).enqueue(uploadRequest)
```

### Цепочки Работ

```kotlin
// Последовательно-параллельное выполнение
WorkManager.getInstance(context)
    .beginWith(compressWork)                    // Шаг 1: сжатие
    .then(listOf(uploadWork1, uploadWork2))     // Шаг 2: параллельные загрузки
    .then(cleanupWork)                          // Шаг 3: очистка
    .enqueue()
```

### Мониторинг Выполнения

```kotlin
WorkManager.getInstance(context)
    .getWorkInfoByIdLiveData(uploadRequest.id)
    .observe(lifecycleOwner) { workInfo ->
        when (workInfo.state) {
            WorkInfo.State.RUNNING -> {
                val progress = workInfo.progress.getInt("progress", 0)
                updateProgressBar(progress) // ✅ отображаем прогресс
            }
            WorkInfo.State.SUCCEEDED -> {
                val url = workInfo.outputData.getString("uploaded_url")
                showSuccess(url) // ✅ задача выполнена
            }
            WorkInfo.State.FAILED -> {
                val error = workInfo.outputData.getString("error")
                showError(error) // ❌ задача провалилась
            }
            else -> {}
        }
    }
```

### Когда Использовать

**Используйте WorkManager**:
- Загрузка файлов, которая должна завершиться
- Синхронизация данных с сервером
- Отправка аналитики/логов
- Очистка кэша/старых данных
- Обработка изображений
- Периодические задачи (мин. 15 минут)

**Не используйте WorkManager**:
- Точное время выполнения (используйте AlarmManager)
- Длительная работа на переднем плане (используйте Foreground Service)
- Немедленные UI обновления (используйте корутины)
- Задачи реального времени (используйте Service)

## Answer (EN)

**WorkManager** is a Jetpack library for **deferrable, guaranteed background work** that must run even if the app exits or the device restarts.

### Key Features

**Guaranteed execution**: tasks are persisted in SQLite database and survive reboots, process death, Doze mode.

**Smart mechanism selection**: automatically uses JobScheduler (API 23+) or AlarmManager + BroadcastReceiver (API 14-22).

**Execution constraints**: declaratively specify conditions — network, charging, battery level, storage space.

**Work chaining**: sequential and parallel execution with data passing between tasks.

**Coroutines integration**: `CoroutineWorker` for suspend functions without blocking threads.

### Core Components

```kotlin
// 1. Worker — defines the task
class UploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        try {
            val path = inputData.getString("file_path") ?: return@withContext Result.failure()
            uploadFile(path)
            Result.success() // ✅ task completed
        } catch (e: Exception) {
            if (runAttemptCount < 3) Result.retry() // ✅ retry with exponential backoff
            else Result.failure() // ❌ final failure
        }
    }
}

// 2. WorkRequest — describes when and how to run
val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setInputData(workDataOf("file_path" to "/path/to/file"))
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED) // ✅ only when network available
            .setRequiresBatteryNotLow(true)                // ✅ battery > 15%
            .build()
    )
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,
        15, TimeUnit.SECONDS // ✅ retries: 15s → 30s → 60s...
    )
    .build()

// 3. WorkManager — manages execution
WorkManager.getInstance(context).enqueue(uploadRequest)
```

### Work Chaining

```kotlin
// Sequential-parallel execution
WorkManager.getInstance(context)
    .beginWith(compressWork)                    // Step 1: compression
    .then(listOf(uploadWork1, uploadWork2))     // Step 2: parallel uploads
    .then(cleanupWork)                          // Step 3: cleanup
    .enqueue()
```

### Monitoring Execution

```kotlin
WorkManager.getInstance(context)
    .getWorkInfoByIdLiveData(uploadRequest.id)
    .observe(lifecycleOwner) { workInfo ->
        when (workInfo.state) {
            WorkInfo.State.RUNNING -> {
                val progress = workInfo.progress.getInt("progress", 0)
                updateProgressBar(progress) // ✅ display progress
            }
            WorkInfo.State.SUCCEEDED -> {
                val url = workInfo.outputData.getString("uploaded_url")
                showSuccess(url) // ✅ task completed
            }
            WorkInfo.State.FAILED -> {
                val error = workInfo.outputData.getString("error")
                showError(error) // ❌ task failed
            }
            else -> {}
        }
    }
```

### When to Use

**Use WorkManager for**:
- File uploads that must complete
- Data synchronization with server
- Sending analytics/logs
- Cache cleanup/old data deletion
- Image processing
- Periodic tasks (min 15 minutes)

**Don't use WorkManager for**:
- Precise timing (use AlarmManager)
- Long-running foreground work (use Foreground Service)
- Immediate UI updates (use coroutines)
- Real-time processing (use Service)

---

## Follow-ups

- How does WorkManager handle battery optimization and Doze mode constraints?
- What is the difference between `Worker`, `CoroutineWorker`, and `RxWorker`?
- How do you implement progress tracking for long-running WorkManager tasks?
- What policies exist for handling duplicate work with `enqueueUniqueWork`?
- How does WorkManager's exponential backoff retry mechanism work and how can it be customized?

## References

- [[c-coroutines]] — WorkManager integrates with Kotlin coroutines via CoroutineWorker
- [[c-background-tasks]] — Overview of Android background execution options
- [WorkManager Documentation](https://developer.android.com/topic/libraries/architecture/workmanager) — Official Android guide
- [WorkManager Basics](https://medium.com/androiddevelopers/workmanager-basics-beba51e94048) — Introduction article

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-service--android--easy]] — Understanding Android Service lifecycle
- [[q-coroutines-basics--kotlin--easy]] — Kotlin coroutines fundamentals

### Related (Same Level)
- [[q-coroutines-flow--kotlin--medium]] — Asynchronous data streams with Flow
- [[q-foreground-service-types--android--medium]] — Long-running visible background work
- [[q-jobscheduler--android--medium]] — Lower-level scheduled task API

### Advanced (Harder)
- [[q-background-execution-limits--android--hard]] — Android background execution restrictions and workarounds
- [[q-battery-optimization--android--hard]] — Battery optimization strategies and Doze mode
