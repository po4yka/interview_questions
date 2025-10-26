---
id: "20251025-120000"
title: "Android Service / Сервис Android"
aliases: ["Service", "Android Service", "Сервис", "Фоновый сервис"]
summary: "Android component for executing long-running operations in the background without a user interface"
topic: "android"
subtopics: ["service", "background-tasks", "lifecycle"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: []
created: "2025-10-25"
updated: "2025-10-25"
tags: ["concept", "android", "service", "background-tasks", "lifecycle"]
---

# Android Service / Сервис Android

## Summary (EN)

An Android Service is a component that performs long-running operations in the background without providing a user interface. Services can be started to perform a task (Started Service) or bound to provide client-server interaction (Bound Service). Unlike Activities, Services have no UI and continue running even when the user switches to another application.

## Краткое описание (RU)

Android Service - это компонент, который выполняет длительные операции в фоновом режиме без пользовательского интерфейса. Сервисы могут быть запущены для выполнения задачи (Started Service) или привязаны для клиент-серверного взаимодействия (Bound Service). В отличие от Activity, Service не имеет UI и продолжает работу даже когда пользователь переключается на другое приложение.

## Key Points (EN)

- Services run in the main thread by default and don't create their own thread
- Started Services continue running until explicitly stopped or they stop themselves
- Bound Services allow components to bind to them and interact through an interface
- Services can be both started and bound simultaneously
- Foreground Services require a notification and have higher priority
- Since Android 8.0 (API 26), background execution limits apply to Services

## Ключевые моменты (RU)

- Сервисы по умолчанию работают в главном потоке и не создают свой собственный поток
- Запущенные сервисы (Started Services) продолжают работу пока не будут явно остановлены
- Привязанные сервисы (Bound Services) позволяют компонентам подключаться и взаимодействовать через интерфейс
- Сервисы могут быть одновременно запущены и привязаны
- Foreground Services требуют уведомления и имеют более высокий приоритет
- С Android 8.0 (API 26) действуют ограничения на фоновое выполнение сервисов

## Service Types

### Started Service
A service that is started by calling `startService()`. It runs indefinitely until stopped.

```kotlin
class DownloadService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Perform background work
        downloadFile(intent?.getStringExtra("url"))

        // Return START_STICKY to restart service if killed
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun downloadFile(url: String?) {
        // Implementation in background thread
        thread {
            // Download logic
            stopSelf() // Stop service when done
        }
    }
}
```

### Bound Service
A service that allows components to bind to it using `bindService()`.

```kotlin
class MusicService : Service() {
    private val binder = MusicBinder()

    inner class MusicBinder : Binder() {
        fun getService(): MusicService = this@MusicService
    }

    override fun onBind(intent: Intent?): IBinder = binder

    fun play() {
        // Play music
    }

    fun pause() {
        // Pause music
    }
}

// In Activity
private var musicService: MusicService? = null
private val connection = object : ServiceConnection {
    override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
        val binder = service as MusicService.MusicBinder
        musicService = binder.getService()
    }

    override fun onServiceDisconnected(name: ComponentName?) {
        musicService = null
    }
}
```

### Foreground Service
A service that shows a notification and has higher priority.

```kotlin
class ForegroundService : Service() {
    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification)

        // Perform work
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Service Running")
            .setContentText("Processing...")
            .setSmallIcon(R.drawable.ic_service)
            .build()
    }
}
```

## Use Cases

### When to Use

- **Music playback**: Keep playing audio when app is in background
- **File downloads**: Download large files without blocking UI
- **Location tracking**: Track user location over time
- **Sync operations**: Sync data with remote servers periodically
- **Network operations**: Handle long-running network requests
- **Sensor monitoring**: Monitor device sensors continuously

### When to Avoid

- **Short tasks**: Use coroutines or WorkManager instead
- **Scheduled tasks**: Use WorkManager for guaranteed execution
- **UI updates**: Services have no UI; use ViewModels and LiveData
- **Battery-intensive operations**: Consider JobScheduler or WorkManager
- **Android 8.0+ background limits**: Use WorkManager or Foreground Service

## Trade-offs

**Pros**:
- Can run operations independently of UI lifecycle
- Allows client-server interaction through binding
- Foreground Services have high priority and won't be killed easily
- Can be accessed from multiple components simultaneously
- Suitable for continuous or long-running operations

**Cons**:
- Runs on main thread by default (must create threads for heavy work)
- Background execution limits on Android 8.0+ (API 26+)
- Can be killed by system under memory pressure (except Foreground)
- Requires proper lifecycle management to avoid leaks
- Users may kill Foreground Services through notification
- Battery consumption concerns for long-running services

## Service Lifecycle

**Started Service**:
1. `onCreate()` - Service created
2. `onStartCommand()` - Service started (can be called multiple times)
3. Service runs
4. `onDestroy()` - Service stopped

**Bound Service**:
1. `onCreate()` - Service created
2. `onBind()` - First client binds
3. Clients interact through IBinder
4. `onUnbind()` - All clients unbind
5. `onDestroy()` - Service destroyed

## Return Flags for onStartCommand

```kotlin
// START_STICKY: Recreate service if killed, but don't redeliver intent
return START_STICKY

// START_NOT_STICKY: Don't recreate service if killed
return START_NOT_STICKY

// START_REDELIVER_INTENT: Recreate service and redeliver last intent
return START_REDELIVER_INTENT
```

## Modern Alternatives

Since Android 8.0 (Oreo), Google recommends alternatives to background Services:

- **WorkManager**: For deferrable, guaranteed background work
- **Foreground Service**: For user-visible ongoing tasks
- **JobScheduler**: For scheduled tasks with constraints
- **Coroutines**: For short asynchronous operations within app lifecycle

## Best Practices

- Always run heavy operations in a background thread (not main thread)
- Use Foreground Service for user-visible tasks
- Stop service when work is complete to save resources
- Consider WorkManager for most background tasks
- Properly handle service lifecycle to prevent memory leaks
- Request appropriate permissions (e.g., FOREGROUND_SERVICE)
- Use IntentService or JobIntentService for simpler cases (deprecated, use WorkManager)

## Related Concepts

- [[c-workmanager]]
- [[c-lifecycle]]
- [[c-jobscheduler]]
- [[c-broadcast-receiver]]
- [[c-intentservice]]
- [[c-foreground-service]]
- [[c-bound-service]]

## References

- [Android Developer Guide: Services Overview](https://developer.android.com/guide/components/services)
- [Android Developer Guide: Foreground Services](https://developer.android.com/guide/components/foreground-services)
- [Android Developer Guide: Bound Services](https://developer.android.com/guide/components/bound-services)
- [Background Execution Limits](https://developer.android.com/about/versions/oreo/background)
