---
id: android-234
title: "WorkManager Execution Guarantee / Гарантия выполнения WorkManager"
aliases: ["WorkManager Execution Guarantee", "Гарантия выполнения WorkManager"]
topic: android
subtopics: [background-execution, service]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-workmanager, q-background-tasks-decision-guide--android--medium, q-background-vs-foreground-service--android--medium, q-service-restrictions-why--android--medium]
created: 2025-10-15
updated: 2025-10-29
sources: []
tags: [android/background-execution, android/service, background-tasks, difficulty/medium, reliability, workmanager]
---

# Вопрос (RU)

> Как WorkManager гарантирует выполнение задач?

# Question (EN)

> How does WorkManager guarantee task execution?

## Ответ (RU)

WorkManager гарантирует выполнение задач через три ключевых механизма: персистентное хранилище SQLite, мониторинг системных ограничений и адаптивную интеграцию с API планировщика (JobScheduler на API 23+, AlarmManager на более старых версиях).

### Ключевые Гарантии

1. **Персистентность** — все запросы работы сохраняются в SQLite и переживают перезапуски приложения/устройства
2. **Constraint-based выполнение** — работа запускается только при выполнении всех условий (сеть, батарея, хранилище)
3. **Автоматический retry** — неудачные задачи повторяются с экспоненциальным backoff
4. **Упорядоченность** — цепочки работ соблюдают последовательность выполнения
5. **Фоновый поток** — работа всегда выполняется вне UI-потока

### Механизмы Гарантии

#### 1. Персистентное Хранилище

```kotlin
val workRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setInputData(workDataOf("file_path" to "/path/to/file"))
    .build()

WorkManager.getInstance(context).enqueue(workRequest)
// ✅ Даже если приложение упадет, работа сохранена в БД
```

Внутри SQLite хранятся: параметры Worker, constraints, счетчик retry, output data.

#### 2. Системная Интеграция

WorkManager автоматически выбирает оптимальный исполнитель:
- **API 23+**: JobScheduler
- **API 14-22**: AlarmManager + `BroadcastReceiver`

#### 3. Constraint-based Выполнение

```kotlin
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED) // ✅ Только с сетью
    .setRequiresBatteryNotLow(true)                // ✅ Батарея не низкая
    .build()

val workRequest = OneTimeWorkRequestBuilder<SyncWorker>()
    .setConstraints(constraints)
    .build()
```

WorkManager мониторит системное состояние и запускает работу только при выполнении всех constraints.

#### 4. Автоматический Retry С Backoff

```kotlin
class RetryableWorker : CoroutineWorker() {
    override suspend fun doWork(): Result {
        return try {
            uploadData()
            Result.success()
        } catch (e: IOException) {
            // ✅ Временная ошибка — повтор
            if (runAttemptCount < 5) Result.retry() else Result.failure()
        } catch (e: Exception) {
            // ❌ Фатальная ошибка — провал
            Result.failure()
        }
    }
}

val workRequest = OneTimeWorkRequestBuilder<RetryableWorker>()
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,
        Duration.ofSeconds(10)
    )
    .build()
```

**Exponential backoff**: 10s → 20s → 40s → 80s (max 5 часов)

#### 5. Уникальность Работы

```kotlin
// ✅ KEEP — игнорировать новый запрос, если работа уже есть
WorkManager.getInstance(context).enqueueUniqueWork(
    "sync_work",
    ExistingWorkPolicy.KEEP,
    workRequest
)

// ✅ REPLACE — отменить старую, запустить новую
WorkManager.getInstance(context).enqueueUniqueWork(
    "sync_work",
    ExistingWorkPolicy.REPLACE,
    workRequest
)
```

### Обработка Перезагрузки

WorkManager автоматически регистрирует BOOT_COMPLETED receiver, который восстанавливает все незавершенные работы из БД после перезагрузки.

### Expedited Work (API 31+)

Для срочных задач WorkManager может запуститься как Foreground `Service`:

```kotlin
class ExpeditedWorker : CoroutineWorker() {
    override suspend fun getForegroundInfo(): ForegroundInfo {
        return ForegroundInfo(NOTIFICATION_ID, createNotification())
    }

    override suspend fun doWork(): Result {
        setForeground(getForegroundInfo()) // ✅ Foreground Service
        return try {
            processUrgentData()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

val expeditedRequest = OneTimeWorkRequestBuilder<ExpeditedWorker>()
    .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
    .build()
```

### Резюме

WorkManager обеспечивает надежность через:
- Немедленное сохранение в SQLite при enqueue
- Автоматический выбор JobScheduler/AlarmManager в зависимости от API
- Строгое соблюдение constraints
- Экспоненциальный backoff для retry
- Восстановление после перезагрузки через BOOT_COMPLETED
- Интеграцию с Foreground `Service` для срочных задач

**Ограничения**: периодические работы не гарантируют точное время выполнения (минимум 15 минут), Doze Mode может отложить выполнение до maintenance window.

## Answer (EN)

WorkManager guarantees task execution through three core mechanisms: persistent SQLite storage, system constraint monitoring, and adaptive integration with scheduling APIs (JobScheduler on API 23+, AlarmManager on older versions).

### Key Guarantees

1. **Persistence** — all work requests are saved to SQLite and survive app/device restarts
2. **Constraint-based execution** — work runs only when all conditions are met (network, battery, storage)
3. **Automatic retry** — failed tasks are retried with exponential backoff
4. **Ordering** — work chains maintain execution sequence
5. **Background thread** — work always executes off the UI thread

### Guarantee Mechanisms

#### 1. Persistent Storage

```kotlin
val workRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setInputData(workDataOf("file_path" to "/path/to/file"))
    .build()

WorkManager.getInstance(context).enqueue(workRequest)
// ✅ Even if app crashes, work is persisted to DB
```

SQLite stores: Worker parameters, constraints, retry count, output data.

#### 2. System Integration

WorkManager automatically selects the optimal executor:
- **API 23+**: JobScheduler
- **API 14-22**: AlarmManager + `BroadcastReceiver`

#### 3. Constraint-based Execution

```kotlin
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED) // ✅ Only with network
    .setRequiresBatteryNotLow(true)                // ✅ Battery not low
    .build()

val workRequest = OneTimeWorkRequestBuilder<SyncWorker>()
    .setConstraints(constraints)
    .build()
```

WorkManager monitors system state and starts work only when all constraints are satisfied.

#### 4. Automatic Retry with Backoff

```kotlin
class RetryableWorker : CoroutineWorker() {
    override suspend fun doWork(): Result {
        return try {
            uploadData()
            Result.success()
        } catch (e: IOException) {
            // ✅ Transient error — retry
            if (runAttemptCount < 5) Result.retry() else Result.failure()
        } catch (e: Exception) {
            // ❌ Fatal error — fail
            Result.failure()
        }
    }
}

val workRequest = OneTimeWorkRequestBuilder<RetryableWorker>()
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,
        Duration.ofSeconds(10)
    )
    .build()
```

**Exponential backoff**: 10s → 20s → 40s → 80s (max 5 hours)

#### 5. Work Uniqueness

```kotlin
// ✅ KEEP — ignore new request if work already exists
WorkManager.getInstance(context).enqueueUniqueWork(
    "sync_work",
    ExistingWorkPolicy.KEEP,
    workRequest
)

// ✅ REPLACE — cancel old, start new
WorkManager.getInstance(context).enqueueUniqueWork(
    "sync_work",
    ExistingWorkPolicy.REPLACE,
    workRequest
)
```

### Device Reboot Handling

WorkManager automatically registers a BOOT_COMPLETED receiver that restores all unfinished work from the database after reboot.

### Expedited Work (API 31+)

For urgent tasks, WorkManager can run as a Foreground `Service`:

```kotlin
class ExpeditedWorker : CoroutineWorker() {
    override suspend fun getForegroundInfo(): ForegroundInfo {
        return ForegroundInfo(NOTIFICATION_ID, createNotification())
    }

    override suspend fun doWork(): Result {
        setForeground(getForegroundInfo()) // ✅ Foreground Service
        return try {
            processUrgentData()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

val expeditedRequest = OneTimeWorkRequestBuilder<ExpeditedWorker>()
    .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
    .build()
```

### Summary

WorkManager ensures reliability through:
- Immediate SQLite persistence on enqueue
- Automatic JobScheduler/AlarmManager selection based on API level
- Strict constraint enforcement
- Exponential backoff for retry
- Recovery after reboot via BOOT_COMPLETED
- Foreground `Service` integration for urgent tasks

**Limitations**: periodic work doesn't guarantee exact timing (15-minute minimum), Doze Mode may defer execution to maintenance windows.

## Follow-ups

1. What happens to WorkManager tasks during Doze Mode?
2. How do you observe WorkManager progress in a `ViewModel`?
3. When should you use expedited work vs. foreground service directly?
4. How does WorkManager handle work chain failures (e.g., if workA fails)?
5. What are the trade-offs between ExistingWorkPolicy.KEEP vs. REPLACE?

## References

- [[c-workmanager]]
- [[q-background-tasks-decision-guide--android--medium]]
- [[q-background-vs-foreground-service--android--medium]]
- [WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager)
- https://developer.android.com/topic/libraries/architecture/workmanager/advanced


## Related Questions

### Prerequisites

- [[q-android-services-purpose--android--easy]]
- [[q-background-tasks-decision-guide--android--medium]]

### Related

- [[q-background-vs-foreground-service--android--medium]]
- [[q-service-restrictions-why--android--medium]]
- [[q-foreground-service-types--android--medium]]

### Advanced

- [[q-service-lifecycle-binding--android--hard]]
- [[q-keep-service-running-background--android--medium]]
