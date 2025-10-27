---
id: 20251027-120000
title: "Raise Process Priority / Повышение приоритета процесса"
aliases: ["Raise Process Priority", "Повышение приоритета процесса"]
topic: android
subtopics: [service, lifecycle, processes]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-network-operations-android--android--medium, q-what-events-are-activity-methods-tied-to--android--medium]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android/service, android/lifecycle, android/processes, foreground-service, lifecycle, process-priority, services, difficulty/medium]
---
# Вопрос (RU)

> Можно ли поднять приоритет процесса в Android?

# Question (EN)

> Can you raise the priority of a process in Android?

---

## Ответ (RU)

**Да**, можно поднять приоритет процесса используя **`startForeground()`** в сервисах. Это переводит сервис в режим **foreground service** с высоким приоритетом, защищая его от уничтожения системой при нехватке памяти.

### Уровни приоритета процессов

Android использует иерархию важности процессов для принятия решений об освобождении памяти:

1. **Foreground Process** (высший) — активный UI или foreground service
2. **Visible Process** — видимый, но не в фокусе
3. **Service Process** — фоновый сервис
4. **Cached Process** — недавно использованный, нет активных компонентов
5. **Empty Process** (низший) — убивается первым

При нехватке памяти система убивает процессы снизу вверх.

### Foreground Service (высокий приоритет)

```kotlin
class DownloadService : Service() {
    private val NOTIFICATION_ID = 1

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Поднимаем приоритет
        startForeground(NOTIFICATION_ID, createNotification())

        // Долгая задача теперь защищена
        performDownload()

        return START_NOT_STICKY
    }

    private fun createNotification(): Notification {
        val channelId = "download_channel"

        // Android 8.0+ требует канал уведомлений
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId, "Downloads", NotificationManager.IMPORTANCE_LOW
            )
            getSystemService(NotificationManager::class.java)
                .createNotificationChannel(channel)
        }

        return NotificationCompat.Builder(this, channelId)
            .setContentTitle("Downloading")
            .setContentText("Download in progress...")
            .setSmallIcon(android.R.drawable.stat_sys_download)
            .setOngoing(true)
            .build()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

### Запуск foreground service

```kotlin
// Android 8.0+ требует startForegroundService()
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
    startForegroundService(Intent(this, DownloadService::class.java))
} else {
    startService(Intent(this, DownloadService::class.java))
}
```

**Важно:** На Android 8.0+ необходимо вызвать `startForeground()` в течение **5 секунд** после старта, иначе система убьёт сервис.

### Когда использовать

**✅ Используйте** foreground service для:
- Воспроизведения музыки
- Навигации/отслеживания местоположения
- Активной фитнес-трекинга
- Скачивания файлов (инициировано пользователем)

**❌ НЕ используйте** для:
- Простых фоновых задач (используйте WorkManager)
- Периодической синхронизации (используйте JobScheduler)

### Другие способы влияния на приоритет

**Bound Service с foreground activity:**
```kotlin
// Сервис наследует приоритет активности при биндинге
bindService(Intent(this, MyService::class.java), connection, BIND_AUTO_CREATE)
```

**JobScheduler priority hint:**
```kotlin
// ❌ Приоритет — это подсказка, не гарантия
val job = JobInfo.Builder(JOB_ID, componentName)
    .setPriority(JobInfo.PRIORITY_HIGH)
    .build()
```

### Ограничения

1. **Обязательное уведомление** — нельзя скрыть работу сервиса от пользователя
2. **Android 12+ ограничения** — нельзя запускать foreground service из фона
3. **Тип сервиса (Android 10+)** — требуется указать `foregroundServiceType` в манифесте

```xml
<service
    android:name=".LocationService"
    android:foregroundServiceType="location" />
```

### Best Practices

- Используйте только когда **действительно необходимо**
- Всегда вызывайте `stopForeground(STOP_FOREGROUND_REMOVE)` по завершении
- Указывайте правильный тип сервиса для Android 10+
- Рассмотрите WorkManager для отложенных задач

---

## Answer (EN)

**Yes**, you can raise process priority using **`startForeground()`** in Services. This promotes the service to a **foreground service** with high priority, protecting it from being killed when system runs low on memory.

### Process Priority Levels

Android uses a hierarchy of process importance for memory management decisions:

1. **Foreground Process** (highest) — active UI or foreground service
2. **Visible Process** — visible but not focused
3. **Service Process** — background service
4. **Cached Process** — recently used, no active components
5. **Empty Process** (lowest) — killed first

When memory is low, system kills processes from bottom to top.

### Foreground Service (high priority)

```kotlin
class DownloadService : Service() {
    private val NOTIFICATION_ID = 1

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Raise priority
        startForeground(NOTIFICATION_ID, createNotification())

        // Long-running task is now protected
        performDownload()

        return START_NOT_STICKY
    }

    private fun createNotification(): Notification {
        val channelId = "download_channel"

        // Android 8.0+ requires notification channel
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId, "Downloads", NotificationManager.IMPORTANCE_LOW
            )
            getSystemService(NotificationManager::class.java)
                .createNotificationChannel(channel)
        }

        return NotificationCompat.Builder(this, channelId)
            .setContentTitle("Downloading")
            .setContentText("Download in progress...")
            .setSmallIcon(android.R.drawable.stat_sys_download)
            .setOngoing(true)
            .build()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

### Starting Foreground Service

```kotlin
// Android 8.0+ requires startForegroundService()
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
    startForegroundService(Intent(this, DownloadService::class.java))
} else {
    startService(Intent(this, DownloadService::class.java))
}
```

**Important:** On Android 8.0+, you **must** call `startForeground()` within **5 seconds** of service start, or system will kill it.

### When to Use

**✅ Use** foreground service for:
- Music playback
- Navigation/location tracking
- Active fitness tracking
- File downloads (user-initiated)

**❌ DON'T use** for:
- Simple background tasks (use WorkManager)
- Periodic sync (use JobScheduler)

### Other Ways to Influence Priority

**Bound Service with foreground activity:**
```kotlin
// Service inherits activity's priority when bound
bindService(Intent(this, MyService::class.java), connection, BIND_AUTO_CREATE)
```

**JobScheduler priority hint:**
```kotlin
// ❌ Priority is a hint, not a guarantee
val job = JobInfo.Builder(JOB_ID, componentName)
    .setPriority(JobInfo.PRIORITY_HIGH)
    .build()
```

### Limitations

1. **Notification required** — can't hide service work from user
2. **Android 12+ restrictions** — can't start foreground service from background
3. **Service type (Android 10+)** — must declare `foregroundServiceType` in manifest

```xml
<service
    android:name=".LocationService"
    android:foregroundServiceType="location" />
```

### Best Practices

- Use only when **truly necessary**
- Always call `stopForeground(STOP_FOREGROUND_REMOVE)` when done
- Specify correct service type for Android 10+
- Consider WorkManager for deferrable tasks

---

## Follow-ups

- What happens if you don't call `startForeground()` within 5 seconds on Android 8.0+?
- How does bound service priority differ from foreground service priority?
- When should you choose WorkManager over foreground service?
- What foreground service types are available and how do they affect permissions?

## References

- Android Documentation: Services and Foreground Services
- Android Documentation: Process and Application Lifecycle

## Related Questions

### Prerequisites
- [[q-what-events-are-activity-methods-tied-to--android--medium]] — understanding Activity lifecycle helps with service lifecycle

### Related
- [[q-network-operations-android--android--medium]] — common use case for background services

### Advanced
- Consider bound services, JobScheduler priority hints, and Android 12+ background launch restrictions
