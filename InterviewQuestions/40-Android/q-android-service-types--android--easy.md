---
topic: android
tags:
  - android
  - android/background-execution
  - android/service
  - background-execution
  - bound-service
  - foreground-service
  - service
  - started-service
difficulty: easy
---

# Какие виды сервисов есть в Android?

**English**: What types of services are there in Android?

## Answer

**Three main types of services:**

**1. Started Service (Background Service)**

Performs operation and doesn't return result.

```kotlin
class DataSyncService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Do work
        return START_STICKY
    }
}

// Start service
startService(Intent(this, DataSyncService::class.java))
```

**2. Foreground Service**

Shows notification, higher priority, harder to kill.

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification)
        return START_STICKY
    }
}
```

**3. Bound Service**

Allows components to bind and interact.

```kotlin
class MusicService : Service() {
    private val binder = MusicBinder()

    inner class MusicBinder : Binder() {
        fun getService(): MusicService = this@MusicService
    }

    override fun onBind(intent: Intent): IBinder = binder
}

// Bind to service
bindService(Intent(this, MusicService::class.java), connection, BIND_AUTO_CREATE)
```

**Comparison:**

| Type | Notification | User Interaction | Use Case |
|------|--------------|------------------|----------|
| Started | ❌ No | ❌ No | Data sync |
| Foreground | ✅ Yes | ✅ Visible | Music player |
| Bound | ❌ No | ✅ Client-server | API calls |

**Summary:**

- **Started**: Background tasks without UI
- **Foreground**: Ongoing notifications (music, location)
- **Bound**: Client-server interaction within app

## Ответ

В Android есть три основных вида сервисов: обычные (Started Service), фоновые с уведомлением (Foreground Service) и привязанные (Bound Service).

