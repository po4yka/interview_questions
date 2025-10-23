---
id: 20251012-122786
title: Background Tasks Decision Guide / Руководство по фоновым задачам
aliases:
- Background Tasks Decision Guide
- Руководство по фоновым задачам
topic: android
subtopics:
- background-execution
- coroutines
- service
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-async-operations-android--android--medium
- q-what-is-workmanager--android--medium
- q-foreground-service-types--background--medium
created: 2025-10-05
updated: 2025-10-15
tags:
- android/background-execution
- android/coroutines
- android/service
- difficulty/medium
---

## Answer (EN)
### Background Task Types

**Asynchronous Work**
- Theory: Concurrent operations while app is foreground; prevents ANR; stops when app backgrounded
- Use cases: UI calculations, data processing, API calls
- Options: Kotlin coroutines, Java threads

**Task Scheduling APIs**
- Theory: Deferred execution; survives app termination; respects system constraints
- Use cases: Periodic sync, sensor data collection, content uploads
- Options: WorkManager (recommended), JobScheduler

**Foreground Services**
- Theory: Immediate execution; user-visible; high resource usage; strict restrictions
- Use cases: Media playback, location tracking, file downloads
- Types: Regular service, shortService (< 3 minutes)

### Decision Framework

**User-Initiated Tasks**

1. **Continue in background?**
   - No → Asynchronous work
   - Yes → Next question

2. **Can be deferred?**
   - Yes → Task scheduling APIs
   - No → Next question

3. **Short and critical?**
   - Yes → Foreground service (shortService)
   - No → Check for specialized APIs

4. **Specialized API available?**
   - Yes → Use specialized API (geofence, media session)
   - No → Foreground service

**Event-Triggered Tasks**

1. **Duration < few seconds?**
   - Yes → Asynchronous work
   - No → Check foreground service eligibility

2. **Can start foreground service?**
   - Yes → Foreground service
   - No → Task scheduling APIs

### Implementation Examples

**Asynchronous Work**
```kotlin
// Coroutines - structured concurrency
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) { fetchData() }
    updateUI(data)
}

// Threads - manual management
Thread {
    val result = compute()
    runOnUiThread { render(result) }
}.start()
```

**WorkManager**
```kotlin
// Periodic work with constraints
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .setRequiresBatteryNotLow(true)
    .build()

val workRequest = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS)
    .setConstraints(constraints)
    .build()

WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "sync", ExistingPeriodicWorkPolicy.KEEP, workRequest
)
```

**Foreground Service**
```kotlin
// Short service for quick tasks
class QuickTaskService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(1, notification)

        // Do work
        stopSelf()
        return START_NOT_STICKY
    }
}
```

## Follow-ups

- What are the battery optimization implications of each approach?
- How do you handle task cancellation and cleanup?
- What are the differences between WorkManager and JobScheduler?

## References

- [[c-coroutines]]
- https://developer.android.com/develop/background-work/background-tasks

## Related Questions

### Prerequisites (Easier)
- [[q-async-operations-android--android--medium]]
- [[q-android-service-types--android--easy]]
- [[q-android-services-purpose--android--easy]]

### Related (Same Level)
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]
- [[q-android-build-optimization--android--medium]]
- [[q-android-modularization--android--medium]]