---
id: 20251012-122773
title: Android Service Types / Типы Service в Android
aliases:
- Android Service Types
- Типы Service в Android
topic: android
subtopics:
- service
- background-execution
question_kind: android
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-android-app-components--android--easy
- q-android-async-primitives--android--easy
- q-android-architectural-patterns--android--medium
created: 2025-10-15
updated: 2025-10-15
tags:
- android/service
- android/background-execution
- difficulty/easy
---

## Answer (EN)
**Android Service Types** provide background execution capabilities for long-running operations without user interface.

**Service Types Theory:**
[[c-service]] components run in the background and can continue executing even when the user switches to another app. They are essential for tasks that need to persist beyond the app's [[c-lifecycle]].

**1. Started Service:**
Runs independently in the background without user interaction. Continues until explicitly stopped or system kills it.

```kotlin
class DataSyncService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Background work
        return START_STICKY
    }
}

startService(Intent(this, DataSyncService::class.java))
```

**2. Foreground Service:**
Shows persistent notification and has higher priority. System is less likely to kill it.

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification)
        return START_STICKY
    }
}
```

**3. Bound Service:**
Allows components to bind and communicate through interface. Lives only while bound to clients.

```kotlin
class MusicService : Service() {
    private val binder = MusicBinder()

    inner class MusicBinder : Binder() {
        fun getService(): MusicService = this@MusicService
    }

    override fun onBind(intent: Intent): IBinder = binder
}

bindService(Intent(this, MusicService::class.java), connection, BIND_AUTO_CREATE)
```

**Service Comparison:**

| Type | Notification | Lifecycle | Use Case |
|------|--------------|-----------|----------|
| Started | No | Independent | Data sync, file upload |
| Foreground | Yes | Independent | Music player, location tracking |
| Bound | No | Client-dependent | API calls, local communication |

**Service Characteristics:**
- **Started**: Background tasks without UI interaction
- **Foreground**: Visible operations requiring user awareness
- **Bound**: Client-server communication within app

---

## Follow-ups

- How do you choose between Started and Foreground services?
- What are the limitations of background services on Android 8.0+?
- How do you handle service lifecycle in different Android versions?

## References

- https://developer.android.com/guide/components/services
- https://developer.android.com/guide/components/foreground-services

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components overview
- [[q-android-async-primitives--android--easy]] - Async primitives

### Related (Medium)
- [[q-android-architectural-patterns--android--medium]] - Architecture patterns
- [[q-android-performance-measurement-tools--android--medium]] - Performance tools