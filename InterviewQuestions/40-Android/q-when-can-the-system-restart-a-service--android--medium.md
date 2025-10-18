---
id: 20251012-122711179
title: "When Can The System Restart A Service / Когда система может перезапустить Service"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-koin-scope-management--dependency-injection--medium, q-biometric-authentication--android--medium, q-android-jetpack-overview--android--easy]
created: 2025-10-15
tags:
  - android
---

# Question (EN)

> When can the system restart a service?

# Вопрос (RU)

> Когда система может перезапустить сервис?

---

## Answer (EN)

The Android system can restart a service after it has been killed, depending on the return value from `onStartCommand()` and the service type. Understanding when and how services restart is crucial for building robust Android applications.

### Service Restart Behavior by Return Value

#### 1. START_STICKY

System restarts the service after being killed, but does NOT redeliver the original Intent.

```kotlin
class MusicPlayerService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Service logic
        setupMediaPlayer()

        // Service will be restarted if killed, but intent will be null
        return START_STICKY
    }

    override fun onCreate() {
        super.onCreate()
        // This will be called again when service restarts
    }
}
```

**Behavior:**

-   Service is killed due to memory pressure
-   System recreates the service when resources become available
-   `onStartCommand()` is called with **null Intent**
-   Service continues running in its default state

**Use cases:**

-   Music players (don't need original Intent data)
-   Background monitoring services
-   Services that maintain state independently

#### 2. START_REDELIVER_INTENT

System restarts the service AND redelivers the last Intent.

```kotlin
class DownloadService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val fileUrl = intent?.getStringExtra("file_url")
        val fileId = intent?.getIntExtra("file_id", -1)

        fileUrl?.let { url ->
            downloadFile(url, fileId ?: -1)
        }

        // Service will restart and receive the same Intent
        return START_REDELIVER_INTENT
    }

    private fun downloadFile(url: String, id: Int) {
        // Download logic - will be retried if service is killed
    }
}
```

**Behavior:**

-   Service is killed while processing
-   System recreates the service
-   `onStartCommand()` is called with the **same Intent** that was being processed
-   Service can continue the interrupted task

**Use cases:**

-   File downloads/uploads
-   Data synchronization
-   Critical task processing
-   Any operation that must complete

#### 3. START_NOT_STICKY

Service is NOT restarted automatically after being killed.

```kotlin
class OneTimeTaskService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        performTask()

        // Service will NOT be restarted if killed
        return START_NOT_STICKY
    }

    private fun performTask() {
        // Short-lived task
        stopSelf()
    }
}
```

**Behavior:**

-   Service is killed
-   System does NOT restart it
-   Exception: If there are pending Intents waiting to be delivered

**Use cases:**

-   Short-lived tasks
-   Tasks that can be safely abandoned
-   Tasks that are not critical

#### 4. START_STICKY_COMPATIBILITY

Legacy mode for apps targeting old API levels. Behaves like START_STICKY but without guarantees.

**Not recommended** - use START_STICKY instead.

### Foreground Services

Foreground services have special treatment and are much less likely to be killed:

```kotlin
class MusicService : Service() {

    override fun onCreate() {
        super.onCreate()
        startForeground()
    }

    private fun startForeground() {
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Music Playing")
            .setContentText("Currently playing: Song Name")
            .setSmallIcon(R.drawable.ic_music)
            .build()

        // Become a foreground service
        startForeground(NOTIFICATION_ID, notification)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Foreground service is highly unlikely to be killed
        // If killed, will be restarted based on return value
        return START_STICKY
    }
}
```

**Special properties:**

-   Highest priority among services
-   Must display persistent notification
-   Rarely killed by system
-   If killed, system prioritizes restarting them
-   Requires special permissions on Android 9+

### Conditions When System Restarts Services

**Memory pressure decreases:**

```kotlin
// System behavior timeline:
1. Memory is low → Service is killed
2. Memory becomes available → Service is restarted (if STICKY)
3. onStartCommand() is called again
```

**Service importance:**

-   Foreground services: Highest priority
-   Started services with START_STICKY: Medium priority
-   Bound services: Priority depends on bound components

### Practical Example: Combining Patterns

```kotlin
class DownloadService : Service() {
    private val downloads = mutableMapOf<Int, DownloadTask>()

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START_DOWNLOAD -> {
                val downloadId = intent.getIntExtra("download_id", -1)
                val url = intent.getStringExtra("url")

                if (downloadId != -1 && url != null) {
                    startDownload(downloadId, url)

                    // If service is killed, this download will be retried
                    return START_REDELIVER_INTENT
                }
            }
        }

        return START_NOT_STICKY
    }

    private fun startDownload(id: Int, url: String) {
        // Start as foreground if downloading critical data
        if (isCriticalDownload(id)) {
            startForeground(id, createNotification(url))
        }

        // Perform download
        performDownload(id, url)
    }

    private fun performDownload(id: Int, url: String) {
        // Download logic with progress tracking
    }
}
```

### Comparison Table

| Return Value           | Restarts?      | Intent Redelivered?  | Use Case                         |
| ---------------------- | -------------- | -------------------- | -------------------------------- |
| START_STICKY           | Yes            | No (null Intent)     | Long-running, stateless services |
| START_REDELIVER_INTENT | Yes            | Yes (same Intent)    | Critical task completion         |
| START_NOT_STICKY       | No             | Only pending Intents | Short-lived tasks                |
| Foreground + STICKY    | Yes (priority) | No                   | User-visible services            |
| Foreground + REDELIVER | Yes (priority) | Yes                  | Critical user-visible tasks      |

### How to Prevent Unwanted Restarts

```kotlin
class ControlledService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val shouldAllowRestart = intent?.getBooleanExtra("allow_restart", false) ?: false

        performTask()

        // Conditional restart behavior
        return if (shouldAllowRestart) {
            START_STICKY
        } else {
            START_NOT_STICKY
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        // Clean shutdown - service won't restart
        stopSelf()
    }
}
```

### Best Practices

**1. Choose the right return value:**

```kotlin
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    return when {
        // Critical data that must be processed
        isCriticalTask(intent) -> START_REDELIVER_INTENT

        // Background monitoring or playback
        isLongRunningTask(intent) -> START_STICKY

        // One-time quick task
        else -> START_NOT_STICKY
    }
}
```

**2. Use foreground services for user-visible work:**

```kotlin
// User expects this to continue
startForeground(NOTIFICATION_ID, notification)
return START_STICKY
```

**3. Handle null Intents for START_STICKY:**

```kotlin
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    if (intent == null) {
        // Service was restarted by system, initialize with default state
        initializeDefaultState()
    } else {
        // Process the intent
        processIntent(intent)
    }

    return START_STICKY
}
```

**4. Modern alternative - WorkManager:**

For most background work, prefer WorkManager over services:

```kotlin
val workRequest = OneTimeWorkRequestBuilder<DownloadWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(workRequest)
// WorkManager handles restart logic automatically
```

### Summary

The system can restart a service based on:

**1. onStartCommand() return value:**

-   START_STICKY: Restarts with null Intent
-   START_REDELIVER_INTENT: Restarts with same Intent
-   START_NOT_STICKY: Does not restart

**2. Service type:**

-   Foreground services: Highest restart priority
-   Started services: Medium priority
-   Bound services: Depends on bound components

**3. System resources:**

-   Restarted when memory pressure decreases
-   Priority based on service importance

**Modern recommendation:** For guaranteed background work, use WorkManager instead of services.

## Ответ (RU)

Система Android может перезапустить сервис в нескольких случаях, особенно если это касается долгосрочных или критически важных задач, которые должны продолжаться даже если приложение было закрыто или убито системой. Использование START_STICKY позволяет системе перезапустить сервис если он был убит. Использование START_REDELIVER_INTENT также позволяет системе перезапустить сервис если он был убит но с повторной доставкой последнего Intent. Foreground сервисы имеют более высокий приоритет и менее вероятно будут убиты системой но если это произойдет система постарается их перезапустить

## Related Topics

-   Service lifecycle
-   onStartCommand() return values
-   Foreground services
-   Memory management

---

## Related Questions

## Follow-ups

-   When should you prefer WorkManager over a background Service?
-   How do foreground service restrictions (Android 12+) affect restart behavior?
-   What are best practices for idempotent work when using START_REDELIVER_INTENT?

## References

-   `https://developer.android.com/guide/components/services` — Services guide
-   `https://developer.android.com/guide/background` — Background work
-   `https://developer.android.com/topic/libraries/architecture/workmanager` — WorkManager

### Prerequisites (Easier)

-   [[q-android-service-types--android--easy]] - Service

### Related (Medium)

-   [[q-service-component--android--medium]] - Service
-   [[q-foreground-service-types--background--medium]] - Service
-   [[q-if-activity-starts-after-a-service-can-you-connect-to-this-service--android--medium]] - Service
-   [[q-keep-service-running-background--android--medium]] - Service
-   [[q-background-vs-foreground-service--android--medium]] - Service

### Advanced (Harder)

-   [[q-service-lifecycle-binding--background--hard]] - Service
