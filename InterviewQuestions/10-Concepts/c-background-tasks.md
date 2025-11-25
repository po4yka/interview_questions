---
id: ivc-20251030-122941
title: Background Tasks / Фоновые задачи
aliases: [Background Tasks, Background Work, Фоновые задачи]
kind: concept
summary: Android mechanisms for executing work outside main thread
links: []
created: 2025-10-30
updated: 2025-10-30
tags: [android, background-tasks, concept, performance, workmanager]
date created: Thursday, October 30th 2025, 12:30:17 pm
date modified: Tuesday, November 25th 2025, 8:54:04 pm
---

# Summary (EN)

Background tasks are operations that execute outside the main (UI) thread in Android. Since Android 6.0 (API 23), the platform introduced aggressive battery optimization through Doze mode and App Standby, restricting background execution. Modern Android development requires careful selection of background execution strategies based on task requirements: deferrable work, immediate execution, exact timing, or user-visible operations.

# Сводка (RU)

Фоновые задачи - это операции, которые выполняются вне главного (UI) потока в Android. Начиная с Android 6.0 (API 23), платформа ввела агрессивную оптимизацию батареи через Doze режим и App Standby, ограничивая фоновое выполнение. Современная разработка под Android требует тщательного выбора стратегии фонового выполнения в зависимости от требований задачи: отложенная работа, немедленное выполнение, точное время или видимые пользователю операции.

---

## Core Concept

**Battery Optimization Constraints**:
- **Doze Mode**: Device idle, network/CPU restricted, periodic maintenance windows
- **App Standby**: Apps unused for period, network and job restrictions
- **Background Execution Limits** (API 26+): Background services terminated after app enters background

**Threading vs Background Work**:
- Threading (coroutines, threads): In-process concurrency, dies with app process
- Background work: Survives app termination, respects system constraints

---

## Options for Background Work

### 1. WorkManager (RECOMMENDED)
**Use for**: Deferrable, guaranteed work (sync, upload, periodic cleanup)

**Characteristics**:
- Guaranteed execution (survives app/device restart)
- Constraint-based (network, battery, storage)
- Respects Doze/App Standby automatically
- Backward compatible (uses JobScheduler/AlarmManager internally)

```kotlin
// Periodic work example
class SyncWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        return try {
            syncRepository.sync()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// Schedule periodic sync (minimum 15 minutes)
val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "sync_work",
    ExistingPeriodicWorkPolicy.KEEP,
    syncRequest
)
```

### 2. Foreground Service
**Use for**: User-visible, long-running tasks (music playback, navigation, file download)

**Characteristics**:
- Requires ongoing notification (user aware)
- NOT killed by system during Doze
- API 28+ requires `FOREGROUND_SERVICE` permission
- API 34+ requires specific types (location, mediaPlayback, etc.)

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification)
        // Start playback
        return START_STICKY
    }
}
```

### 3. AlarmManager
**Use for**: Exact-time work (alarm clock, calendar reminder)

**Characteristics**:
- Can wake device from Doze
- API 31+ requires `SCHEDULE_EXACT_ALARM` permission
- Use sparingly (battery impact)

### 4. JobScheduler (Low-level)
**Use for**: Custom scheduling logic (rare, prefer WorkManager)

---

## Decision Guide

| Requirement | Solution |
|-------------|----------|
| Deferrable, guaranteed | WorkManager |
| User-visible, long-running | Foreground Service |
| Exact time execution | AlarmManager + WorkManager |
| Immediate one-time | WorkManager (expedited) |
| In-app only | Coroutines/Threads |

---

## Best Practices

1. **Prefer WorkManager**: Handles all edge cases (Doze, battery, constraints)
2. **Minimize exact alarms**: Use inexact timing when possible
3. **Use constraints**: Network, battery, storage requirements
4. **Foreground service = visible work**: Only for user-aware operations
5. **Test Doze/Standby**: `adb shell dumpsys deviceidle force-idle`
6. **Handle failures**: Implement retry logic with exponential backoff
7. **API 31+ permissions**: Request exact alarm permission explicitly

---

## Common Pitfalls

- Using background services on API 26+ (will be killed)
- Not handling Doze mode (work delayed unexpectedly)
- Exact alarms without permission (API 31+)
- Foreground service without notification type (API 34+)
- Ignoring battery optimization (user can disable background work)

---

## Use Cases / Trade-offs

**WorkManager**:
- USE: Data sync, uploads, periodic cleanup, database migrations
- TRADE-OFF: Not exact timing (can be delayed by hours in Doze)

**Foreground Service**:
- USE: Music, navigation, download with progress, live location
- TRADE-OFF: Requires notification, user can stop service

**AlarmManager**:
- USE: Alarm clock, calendar events, medication reminders
- TRADE-OFF: Battery drain, requires special permission

---

## References

- [Android Background Execution Limits](https://developer.android.com/about/versions/oreo/background)
- [WorkManager Documentation](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Doze and App Standby](https://developer.android.com/training/monitoring-device-state/doze-standby)
- [Foreground Services](https://developer.android.com/develop/background-work/services/foreground-services)
- [AlarmManager Best Practices](https://developer.android.com/training/scheduling/alarms)
