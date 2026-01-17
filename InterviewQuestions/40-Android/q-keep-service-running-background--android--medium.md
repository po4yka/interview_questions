---\
id: android-194
title: Keep Service Running Background / Удержание Service в фоне
aliases: [Background Service, Keep Service Running Background, Удержание Service в фоне, Фоновый сервис]
topic: android
subtopics: [background-execution, coroutines, service]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-background-tasks, c-coroutines, q-android-service-types--android--easy, q-background-vs-foreground-service--android--medium, q-foreground-service-types--android--medium, q-service-component--android--medium, q-when-can-the-system-restart-a-service--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-28
tags: [android/background-execution, android/coroutines, android/service, difficulty/medium, foreground-service, jobscheduler, workmanager]
anki_cards:
  - slug: android-194-0-en
    front: "How do you keep a service running in the background on Android?"
    back: |
      **Options by use case:**

      | Approach | When to use |
      |----------|-------------|
      | **Foreground Service** | User-initiated, urgent (music, navigation) |
      | **WorkManager** | Deferrable, survives restarts |
      | **JobScheduler** | Condition-based (network, charging) |

      **Foreground Service rules:**
      - Must show notification
      - Call `startForeground()` within 5 seconds
      - Declare `foregroundServiceType` (Android 10+)

      **Decision:** Urgent + user-initiated = Foreground Service. Deferrable = WorkManager.
    tags:
      - android_services
      - difficulty::medium
  - slug: android-194-0-ru
    front: "Как сохранить работу сервиса в фоне на Android?"
    back: |
      **Варианты по сценарию:**

      | Подход | Когда использовать |
      |--------|-------------------|
      | **Foreground Service** | Инициировано пользователем, срочно (музыка, навигация) |
      | **WorkManager** | Может быть отложено, переживает перезапуск |
      | **JobScheduler** | По условиям (сеть, зарядка) |

      **Правила Foreground Service:**
      - Обязательно уведомление
      - Вызвать `startForeground()` в течение 5 секунд
      - Указать `foregroundServiceType` (Android 10+)

      **Решение:** Срочно + от пользователя = Foreground Service. Отложенное = WorkManager.
    tags:
      - android_services
      - difficulty::medium

---\
# Вопрос (RU)

> Что делать если нужно чтобы сервис продолжал работу в фоне?

# Question (EN)

> What to do if you need a service to continue running in the background?

---

## Ответ (RU)

Для продолжения работы сервиса в фоне выберите правильный подход:

### 1. Foreground `Service` (Высокий приоритет)

**Когда использовать:**
- Задача инициирована пользователем и срочна
- Пользователь ожидает продолжения (музыка, навигация)
- Требуется немедленное выполнение
- Можете показать постоянное уведомление

**Ключевые характеристики:**
- Требует постоянного уведомления (обязательно с Android 8.0+)
- Высокий приоритет — сервис значительно менее вероятно будет убит системой, но это не абсолютная гарантия непрерывной работы
- Должен вызвать `startForeground()` в течение 5 секунд после запуска через `startForegroundService()`
- Требует разрешения `FOREGROUND_SERVICE` в манифесте (Android 9+), а также корректных `foregroundServiceType` для соответствующих сценариев на Android 10+/14+

```kotlin
class DownloadService : Service() {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    override fun onCreate() {
        super.onCreate()
        // ✅ Must call startForeground within 5 seconds after startForegroundService()
        startForeground(NOTIFICATION_ID, createNotification())
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        scope.launch {
            try {
                downloadLargeFile()
            } finally {
                // ✅ Always stop when done
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            }
        }
        // START_STICKY is acceptable here to let system recreate service if killed while work is ongoing
        return START_STICKY
    }

    override fun onDestroy() {
        scope.cancel()
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**Запуск сервиса:**
```kotlin
val intent = Intent(this, DownloadService::class.java)
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
    startForegroundService(intent) // ✅ API 26+: запуск foreground service
} else {
    startService(intent)
}
```

### 2. WorkManager (Рекомендуется)

**Когда использовать:**
- Задача может быть отложена
- Задача должна пережить перезапуск приложения
- Нужно максимально надежное выполнение (best-effort с учётом ограничений системы)
- Важна оптимизация батареи

**Примеры:** загрузка логов, периодическая синхронизация, резервное копирование при WiFi

```kotlin
class UploadWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        return try {
            val fileUrl = inputData.getString("file_url") ?: return Result.failure()
            // ✅ For long-running work that must run in a foreground context (e.g. user-initiated upload)
            setForeground(createForegroundInfo())
            uploadFile(fileUrl)
            Result.success()
        } catch (e: Exception) {
            // ✅ Retry with exponential backoff (ограниченное число попыток)
            if (runAttemptCount < 3) Result.retry() else Result.failure()
        }
    }
}
```

**Планирование работы:**
```kotlin
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .setRequiresBatteryNotLow(true)
    .build()

val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setInputData(workDataOf("file_url" to fileUrl))
    .setConstraints(constraints)
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, WorkRequest.MIN_BACKOFF_MILLIS, TimeUnit.MILLISECONDS)
    .build()

WorkManager.getInstance(this).enqueue(uploadRequest)
```

### 3. JobScheduler (Управляется системой)

**Когда использовать:**
- Задача требует специфических условий (сеть, зарядка, idle)
- Задача не критична по времени
- Не нужны функции `WorkManager` (chaining, unique work)

**Примечание:** `WorkManager` использует JobScheduler внутри на Android 6.0+, поэтому `WorkManager` обычно предпочтительнее.

```kotlin
class SyncJobService : JobService() {
    private var job: Job? = null

    override fun onStartJob(params: JobParameters): Boolean {
        job = CoroutineScope(Dispatchers.IO).launch {
            try {
                performSync()
                jobFinished(params, false) // ✅ false = don't reschedule
            } catch (e: Exception) {
                jobFinished(params, true) // ✅ true = reschedule on failure (subject to system policies)
            }
        }
        return true // Work is ongoing
    }

    override fun onStopJob(params: JobParameters): Boolean {
        job?.cancel()
        return true // Request reschedule; реальное поведение зависит от системы
    }
}
```

### Сравнение Подходов

| Критерий | Foreground `Service` | `WorkManager` | JobScheduler |
|----------|-------------------|-------------|--------------|
| **Уведомление пользователя** | Требуется | Опционально / требуется при foreground-работе | Не требуется |
| **Приоритет** | Высокий (но не абсолютный) | Средний | Низкий |
| **Время выполнения** | Немедленное | Отложенное | Отложенное |
| **`Constraints`** | Нет встроенных (решаются вручную) | Сеть, батарея, хранилище | Сеть, зарядка, idle |
| **Переживает перезагрузку** | Нет (если явно не обработан BOOT_COMPLETED) | Да | Да (если persisted) |
| **Случай использования** | Музыка, навигация | Фоновая синхронизация | Периодическая очистка |

### Лучшие Практики

**1. Выбирайте правильный инструмент:**
```kotlin
// ❌ BAD: Foreground service для периодической синхронизации
class PeriodicSyncService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(1, notification) // Пользователь не должен это видеть без веской причины
        syncData()
        return START_STICKY
    }
}

// ✅ GOOD: WorkManager для периодической синхронизации
val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES).build()
WorkManager.getInstance(context).enqueue(syncRequest)
```

**2. Учитывайте различия версий Android:**
- Android 12+ имеет дополнительные ограничения на запуск foreground service из фона
- Android 8+ требует `startForegroundService()` для запуска foreground service
- Android 14+ требует корректного `foregroundServiceType` в манифесте для соответствующих сценариев

**3. Всегда останавливайте сервисы:**
```kotlin
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    val scope = CoroutineScope(Dispatchers.IO)
    scope.launch {
        try {
            performTask()
        } finally {
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelf() // ✅ Always stop when done
            scope.cancel()
        }
    }
    // NOT_STICKY: система не будет перезапускать сервис автоматически после успешного завершения
    return START_NOT_STICKY
}
```

### Алгоритм Выбора

```text
Задача инициирована пользователем и срочна?
 ДА → Foreground Service
 НЕТ → Задача может быть отложена?
     ДА → WorkManager
     НЕТ → Пересмотрите необходимость задачи
```

---

## Answer (EN)

To keep a service running in the background, choose the right approach:

### 1. Foreground `Service` (High Priority)

**When to use:**
- Task is user-initiated and time-sensitive
- User expects the task to continue (music playback, navigation)
- Task requires immediate execution
- You can show a persistent notification

**Key characteristics:**
- Requires a persistent notification (mandatory on Android 8.0+)
- High priority — much less likely to be killed by the system, but not guaranteed to run forever
- Must call `startForeground()` within 5 seconds after starting via `startForegroundService()`
- Requires `FOREGROUND_SERVICE` permission in manifest (Android 9+), and appropriate `foregroundServiceType` values for the given use case on Android 10+/14+

```kotlin
class DownloadService : Service() {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    override fun onCreate() {
        super.onCreate()
        // ✅ Must call startForeground within 5 seconds after startForegroundService()
        startForeground(NOTIFICATION_ID, createNotification())
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        scope.launch {
            try {
                downloadLargeFile()
            } finally {
                // ✅ Always stop when done
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            }
        }
        // START_STICKY is acceptable here to let the system recreate the service if killed while work is still relevant
        return START_STICKY
    }

    override fun onDestroy() {
        scope.cancel()
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**Starting the service:**
```kotlin
val intent = Intent(this, DownloadService::class.java)
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
    startForegroundService(intent) // ✅ API 26+: proper way to start a foreground service
} else {
    startService(intent)
}
```

### 2. WorkManager (Recommended)

**When to use:**
- Task is deferrable
- Task should survive app restarts
- You need highly reliable, best-effort execution under system constraints
- Battery optimization is important

**Examples:** log uploads, periodic sync, WiFi-based photo backup

```kotlin
class UploadWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        return try {
            val fileUrl = inputData.getString("file_url") ?: return Result.failure()
            // ✅ For long-running work that must run in a foreground context (e.g. user-initiated upload)
            setForeground(createForegroundInfo())
            uploadFile(fileUrl)
            Result.success()
        } catch (e: Exception) {
            // ✅ Retry with exponential backoff (limited attempts)
            if (runAttemptCount < 3) Result.retry() else Result.failure()
        }
    }
}
```

**Scheduling work:**
```kotlin
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .setRequiresBatteryNotLow(true)
    .build()

val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setInputData(workDataOf("file_url" to fileUrl))
    .setConstraints(constraints)
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, WorkRequest.MIN_BACKOFF_MILLIS, TimeUnit.MILLISECONDS)
    .build()

WorkManager.getInstance(this).enqueue(uploadRequest)
```

### 3. JobScheduler (System-Managed)

**When to use:**
- Task requires specific conditions (network, charging, idle)
- Task is not time-critical
- You don't need `WorkManager` features (chaining, unique work)

**Note:** `WorkManager` uses JobScheduler internally on Android 6.0+, so `WorkManager` is usually preferred.

```kotlin
class SyncJobService : JobService() {
    private var job: Job? = null

    override fun onStartJob(params: JobParameters): Boolean {
        job = CoroutineScope(Dispatchers.IO).launch {
            try {
                performSync()
                jobFinished(params, false) // ✅ false = don't reschedule
            } catch (e: Exception) {
                jobFinished(params, true) // ✅ true = ask to reschedule (subject to system policies)
            }
        }
        return true // Work is ongoing
    }

    override fun onStopJob(params: JobParameters): Boolean {
        job?.cancel()
        return true // Request reschedule; actual behavior depends on the system
    }
}
```

### Comparison

| Criteria | Foreground `Service` | `WorkManager` | JobScheduler |
|----------|-------------------|-------------|--------------|
| **User notification** | Required | Optional / required for foreground work | Not required |
| **Priority** | High (but not absolute) | Medium | Low |
| **Execution timing** | Immediate | Deferred | Deferred |
| **`Constraints`** | None built-in (handled manually) | Network, battery, storage | Network, charging, idle |
| **Survives reboot** | No (unless BOOT_COMPLETED is handled) | Yes | Yes (if persisted) |
| **Use case** | Music, navigation | Background sync | Periodic cleanup |

### Best Practices

**1. Choose the right tool:**
```kotlin
// ❌ BAD: Foreground service for periodic sync
class PeriodicSyncService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(1, notification) // User shouldn't see this without a strong reason
        syncData()
        return START_STICKY
    }
}

// ✅ GOOD: WorkManager for periodic sync
val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES).build()
WorkManager.getInstance(context).enqueue(syncRequest)
```

**2. Handle Android version differences:**
- Android 12+ has additional restrictions on starting foreground services from the background
- Android 8+ requires `startForegroundService()` to start a foreground service
- Android 14+ requires appropriate `foregroundServiceType` entries in the manifest for relevant use cases

**3. Always stop services:**
```kotlin
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    val scope = CoroutineScope(Dispatchers.IO)
    scope.launch {
        try {
            performTask()
        } finally {
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelf() // ✅ Always stop when done
            scope.cancel()
        }
    }
    // NOT_STICKY: system won't restart the service automatically after successful completion
    return START_NOT_STICKY
}
```

### Decision Flowchart

```text
Is task user-initiated and time-sensitive?
 YES → Foreground Service
 NO → Is task deferrable?
     YES → WorkManager
     NO → Reconsider task necessity
```

---

## Follow-ups

- How to handle battery optimization restrictions (Doze mode, App Standby)?
- What happens if foreground service doesn't call `startForeground()` within 5 seconds?
- How to chain multiple `WorkManager` tasks sequentially or in parallel?
- What are the differences between `START_STICKY`, `START_NOT_STICKY`, and `START_REDELIVER_INTENT`?
- How to test background services and `WorkManager` in unit tests?

## References

- [Android Developer Guide: Background Work](https://developer.android.com/guide/background)
- [WorkManager Documentation](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Foreground Services](https://developer.android.com/guide/components/foreground-services)
- [JobScheduler API](https://developer.android.com/reference/android/app/job/JobScheduler)

## Related Questions

### Prerequisites / Concepts

- [[c-coroutines]]
- [[c-background-tasks]]

### Prerequisites (Easier)
- [[q-android-service-types--android--easy]] - Types of Android services

### Related (Same Level)
- [[q-service-component--android--medium]] - `Service` component lifecycle
- [[q-foreground-service-types--android--medium]] - Foreground service types
- [[q-when-can-the-system-restart-a-service--android--medium]] - `Service` restart behavior
- [[q-background-vs-foreground-service--android--medium]] - Comparing service types

### Advanced (Harder)
- [[q-service-lifecycle-binding--android--hard]] - Complex service binding scenarios
- [[q-compose-side-effects-launchedeffect-disposableeffect--android--hard]] - Handling background work in Compose
