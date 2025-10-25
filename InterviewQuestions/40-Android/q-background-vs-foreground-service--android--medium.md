---
id: 20251016-161808
title: Background vs Foreground Service / Background vs Foreground Service
aliases:
- Background vs Foreground Service
- Background vs Foreground Service
topic: android
subtopics:
- service
- background-execution
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-android-service-types--android--easy
- q-foreground-service-types--background--medium
- q-background-tasks-decision-guide--android--medium
created: 2025-10-15
updated: 2025-10-15
tags:
- android/service
- android/background-execution
- difficulty/medium
---

# Вопрос (RU)
> Что такое Background vs Foreground Service?

---

# Question (EN)
> What is the difference between background vs foreground service?

## Answer (EN)
### Core Differences

**Background Service**
- Theory: Runs without user awareness; low priority; can be killed by system
- Characteristics: No notification required; Service Process priority; Android 8.0+ severely restricted
- Use cases: Legacy apps only; modern apps should use [[c-workmanager]]

**Foreground Service**
- Theory: User-visible with persistent notification; high priority; protected from termination
- Characteristics: Required notification; Foreground Process priority; survives system pressure
- Use cases: Music playback, navigation, file downloads, user-initiated long tasks. [[c-service]] components must follow strict lifecycle rules.

### Implementation Comparison

**Background Service (Deprecated)**
```kotlin
// Theory: No notification, low priority, can be killed
class BackgroundService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Work without notification - risky on Android 8.0+
        doWork()
        return START_NOT_STICKY
    }
}
```

**Foreground Service**
```kotlin
// Theory: Notification required, high priority, protected
class ForegroundService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Must call startForeground within 5 seconds
        startForeground(NOTIFICATION_ID, createNotification())
        doWork()
        return START_STICKY
    }

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Service Running")
            .setSmallIcon(R.drawable.ic_service)
            .setOngoing(true)
            .build()
    }
}
```

### Android 8.0+ Restrictions

**Background Service Limitations**
- Theory: System prevents background service starts when app is backgrounded
- Exception: `IllegalStateException: Not allowed to start service`
- Solution: Use `startForegroundService()` or WorkManager

**Foreground Service Requirements**
- Theory: Must call `startForeground()` within 5 seconds of `onStartCommand()`
- Failure: System kills service with ANR
- Notification: Must be persistent and ongoing

### Process Priority Hierarchy

```
1. Foreground Process (Foreground Service) - Highest priority
2. Visible Process
3. Service Process (Background Service) - Can be killed
4. Cached Process
5. Empty Process
```

### Decision Framework

**Use Foreground Service when:**
- Task is user-visible and time-sensitive
- User initiated the operation
- Task requires immediate execution
- Examples: Music playback, navigation, file downloads

**Use WorkManager instead of Background Service when:**
- Task can be deferred
- Periodic execution needed
- System constraints should be respected
- Examples: Data sync, periodic updates, cleanup tasks

## Follow-ups

- What are the notification requirements for foreground services?
- How do you handle service lifecycle in Android 8.0+?
- When should you use WorkManager instead of services?

## References

- https://developer.android.com/guide/components/services

## Related Questions

### Prerequisites (Easier)
- [[q-android-service-types--android--easy]]
- [[q-android-services-purpose--android--easy]]
- [[q-background-tasks-decision-guide--android--medium]]

### Related (Same Level)
- [[q-android-performance-measurement-tools--android--medium]]
- [[q-android-runtime-art--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]
- [[q-android-build-optimization--android--medium]]
- [[q-android-modularization--android--medium]]