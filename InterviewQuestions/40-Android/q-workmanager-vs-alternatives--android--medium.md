---
id: 20251017-114414
title: "WorkManager vs Alternatives / WorkManager против альтернатив"
aliases: [WorkManager vs Alternatives, WorkManager против альтернатив]
topic: android
subtopics: [background-execution]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-workmanager, c-alarmmanager, q-workmanager-return-result--android--medium]
created: 2025-10-12
updated: 2025-01-25
tags: [android/background-execution, workmanager, alarmmanager, jobscheduler, foreground-service, difficulty/medium]
sources: [https://developer.android.com/topic/libraries/architecture/workmanager]
---

# Вопрос (RU)
> Когда использовать WorkManager vs AlarmManager vs JobScheduler vs Foreground Service?

# Question (EN)
> When to use WorkManager vs AlarmManager vs JobScheduler vs Foreground Service?

---

## Ответ (RU)

**Теория выбора API:**
Android предоставляет несколько API для фоновой работы с разными гарантиями и ограничениями. Выбор зависит от требований к таймингу, гарантиям выполнения и видимости для пользователя.

**WorkManager:**
Гарантированное выполнение с гибким таймингом и поддержкой ограничений. Переживает перезагрузки и обновления приложения.

```kotlin
// Периодическая синхронизация с ограничениями
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED)
    .setRequiresBatteryNotLow(true)
    .build()

val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(24, TimeUnit.HOURS)
    .setConstraints(constraints)
    .build()

WorkManager.getInstance(context)
    .enqueueUniquePeriodicWork("sync", ExistingPeriodicWorkPolicy.KEEP, syncRequest)
```

**AlarmManager:**
Точный тайминг для критичных по времени операций. Может будить устройство из сна.

```kotlin
// Точный будильник
val alarmManager = context.getSystemService(AlarmManager::class.java)
val intent = Intent(context, AlarmReceiver::class.java)
val pendingIntent = PendingIntent.getBroadcast(context, 0, intent, PendingIntent.FLAG_IMMUTABLE)

alarmManager.setExactAndAllowWhileIdle(
    AlarmManager.RTC_WAKEUP,
    triggerTime,
    pendingIntent
)
```

**JobScheduler:**
Планировщик задач с ограничениями для API 21+. WorkManager использует его внутри.

```kotlin
// Очистка базы данных при зарядке
val jobInfo = JobInfo.Builder(JOB_ID, ComponentName(context, CleanupJobService::class.java))
    .setRequiresCharging(true)
    .setRequiresDeviceIdle(true)
    .setPeriodic(TimeUnit.DAYS.toMillis(1))
    .build()

context.getSystemService(JobScheduler::class.java).schedule(jobInfo)
```

**Foreground Service:**
Долгосрочные операции с обязательным уведомлением для пользователя.

```kotlin
// Музыкальный плеер
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_music)
            .setContentTitle("Now Playing")
            .build()

        startForeground(NOTIFICATION_ID, notification)
        return START_STICKY
    }
}
```

**Критерии выбора:**
- Нужен точный тайминг? → AlarmManager
- Работа должна завершиться гарантированно? → WorkManager
- Пользователь должен видеть процесс? → Foreground Service
- Быстрая операция в UI? → Coroutines

## Answer (EN)

**API Selection Theory:**
Android provides multiple APIs for background work with different guarantees and constraints. Choice depends on timing requirements, execution guarantees, and user visibility.

**WorkManager:**
Guaranteed execution with flexible timing and constraint support. Survives reboots and app updates.

```kotlin
// Periodic sync with constraints
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED)
    .setRequiresBatteryNotLow(true)
    .build()

val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(24, TimeUnit.HOURS)
    .setConstraints(constraints)
    .build()

WorkManager.getInstance(context)
    .enqueueUniquePeriodicWork("sync", ExistingPeriodicWorkPolicy.KEEP, syncRequest)
```

**AlarmManager:**
Exact timing for time-critical operations. Can wake device from sleep.

```kotlin
// Exact alarm
val alarmManager = context.getSystemService(AlarmManager::class.java)
val intent = Intent(context, AlarmReceiver::class.java)
val pendingIntent = PendingIntent.getBroadcast(context, 0, intent, PendingIntent.FLAG_IMMUTABLE)

alarmManager.setExactAndAllowWhileIdle(
    AlarmManager.RTC_WAKEUP,
    triggerTime,
    pendingIntent
)
```

**JobScheduler:**
Task scheduler with constraints for API 21+. WorkManager uses it internally.

```kotlin
// Database cleanup while charging
val jobInfo = JobInfo.Builder(JOB_ID, ComponentName(context, CleanupJobService::class.java))
    .setRequiresCharging(true)
    .setRequiresDeviceIdle(true)
    .setPeriodic(TimeUnit.DAYS.toMillis(1))
    .build()

context.getSystemService(JobScheduler::class.java).schedule(jobInfo)
```

**Foreground Service:**
Long-running operations with mandatory user notification.

```kotlin
// Music player
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_music)
            .setContentTitle("Now Playing")
            .build()

        startForeground(NOTIFICATION_ID, notification)
        return START_STICKY
    }
}
```

**Selection Criteria:**
- Need exact timing? → AlarmManager
- Work must complete guaranteed? → WorkManager
- User must see process? → Foreground Service
- Quick UI operation? → Coroutines

---

## Follow-ups

- How do you handle WorkManager constraints for different Android versions?
- What are the battery optimization implications of each approach?
- How do you migrate from deprecated APIs to WorkManager?

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components
- [[q-android-lifecycle--android--easy]] - Lifecycle management

### Related (Same Level)
- [[q-workmanager-return-result--android--medium]] - WorkManager results
- [[q-foreground-service-types--background--medium]] - Foreground services
- [[q-android-background-limits--android--medium]] - Background limits

### Advanced (Harder)
- [[q-workmanager-advanced--background--medium]] - Advanced WorkManager
- [[q-android-runtime-internals--android--hard]] - Runtime internals
