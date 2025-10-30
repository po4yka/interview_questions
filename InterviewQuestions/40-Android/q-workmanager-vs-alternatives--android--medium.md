---
id: 20251017-114414
title: "WorkManager vs Alternatives / WorkManager против альтернатив"
aliases: ["WorkManager vs Alternatives", "WorkManager против альтернатив"]
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
updated: 2025-10-29
tags: [android/background-execution, workmanager, alarmmanager, jobscheduler, foreground-service, difficulty/medium]
sources: []
---

# Вопрос (RU)
> Когда использовать WorkManager vs AlarmManager vs JobScheduler vs Foreground Service?

# Question (EN)
> When to use WorkManager vs AlarmManager vs JobScheduler vs Foreground Service?

---

## Ответ (RU)

**Теория выбора API:**
Android предоставляет несколько API для фоновой работы с разными гарантиями и ограничениями. Выбор зависит от требований к таймингу, гарантиям выполнения и видимости для пользователя.

**Критерии выбора:**

| API | Когда использовать | Ключевая особенность |
|-----|-------------------|---------------------|
| **WorkManager** | Отложенная работа с гарантией выполнения | Переживает перезагрузки, поддерживает ограничения |
| **AlarmManager** | Точный тайминг (будильники, напоминания) | Может будить устройство, точность до миллисекунд |
| **Foreground Service** | Долгие задачи с видимостью пользователю | Обязательное уведомление, защита от kill |
| **JobScheduler** | Прямой доступ к планировщику (API 21+) | WorkManager использует его внутри |

**WorkManager — гарантированное выполнение:**

```kotlin
// ✅ Правильно: периодическая синхронизация с ограничениями
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED) // ✅ Только Wi-Fi
    .setRequiresBatteryNotLow(true)                // ✅ Экономия батареи
    .build()

val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(24, TimeUnit.HOURS)
    .setConstraints(constraints)
    .build()

WorkManager.getInstance(context)
    .enqueueUniquePeriodicWork("sync", ExistingPeriodicWorkPolicy.KEEP, syncRequest)
```

**AlarmManager — точный тайминг:**

```kotlin
// ✅ Правильно: точный будильник для критичных событий
val alarmManager = context.getSystemService(AlarmManager::class.java)
val pendingIntent = PendingIntent.getBroadcast(
    context, 0,
    Intent(context, AlarmReceiver::class.java),
    PendingIntent.FLAG_IMMUTABLE // ✅ Безопасность
)

alarmManager.setExactAndAllowWhileIdle(
    AlarmManager.RTC_WAKEUP, // ✅ Будит устройство
    triggerTime,
    pendingIntent
)
```

**Foreground Service — видимая работа:**

```kotlin
// ✅ Правильно: музыкальный плеер с уведомлением
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification() // ✅ Обязательное уведомление
        startForeground(NOTIFICATION_ID, notification)
        return START_STICKY // ✅ Перезапуск после kill
    }
}

// ❌ Неправильно: использовать для скрытой работы без уведомления
// ❌ Неправильно: использовать для быстрых операций (используй WorkManager)
```

## Answer (EN)

**API Selection Theory:**
Android provides multiple APIs for background work with different guarantees and constraints. Choice depends on timing requirements, execution guarantees, and user visibility.

**Selection Criteria:**

| API | When to Use | Key Feature |
|-----|------------|-------------|
| **WorkManager** | Deferrable guaranteed work | Survives reboots, supports constraints |
| **AlarmManager** | Exact timing (alarms, reminders) | Can wake device, millisecond precision |
| **Foreground Service** | Long tasks with user visibility | Mandatory notification, kill protection |
| **JobScheduler** | Direct scheduler access (API 21+) | WorkManager uses it internally |

**WorkManager — guaranteed execution:**

```kotlin
// ✅ Correct: periodic sync with constraints
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED) // ✅ Wi-Fi only
    .setRequiresBatteryNotLow(true)                // ✅ Battery saving
    .build()

val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(24, TimeUnit.HOURS)
    .setConstraints(constraints)
    .build()

WorkManager.getInstance(context)
    .enqueueUniquePeriodicWork("sync", ExistingPeriodicWorkPolicy.KEEP, syncRequest)
```

**AlarmManager — exact timing:**

```kotlin
// ✅ Correct: exact alarm for critical events
val alarmManager = context.getSystemService(AlarmManager::class.java)
val pendingIntent = PendingIntent.getBroadcast(
    context, 0,
    Intent(context, AlarmReceiver::class.java),
    PendingIntent.FLAG_IMMUTABLE // ✅ Security
)

alarmManager.setExactAndAllowWhileIdle(
    AlarmManager.RTC_WAKEUP, // ✅ Wakes device
    triggerTime,
    pendingIntent
)
```

**Foreground Service — visible work:**

```kotlin
// ✅ Correct: music player with notification
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification() // ✅ Mandatory notification
        startForeground(NOTIFICATION_ID, notification)
        return START_STICKY // ✅ Restart after kill
    }
}

// ❌ Wrong: use for hidden work without notification
// ❌ Wrong: use for quick operations (use WorkManager instead)
```

---

## Follow-ups

- How does WorkManager handle constraints on different Android versions (API 14+ vs 23+ vs 26+)?
- What are the battery optimization implications of each approach, and how does Doze mode affect them?
- How do you migrate from deprecated JobScheduler or AlarmManager APIs to WorkManager?
- When would you combine multiple approaches (e.g., WorkManager + Foreground Service)?
- What are the trade-offs between exact alarms and inexact window-based alarms for battery life?

## References

- [[c-workmanager]] - WorkManager concept
- [[c-alarmmanager]] - AlarmManager concept
- [WorkManager Documentation](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Background Execution Limits](https://developer.android.com/about/versions/oreo/background)
- [Schedule Tasks with WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager/basics)

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
