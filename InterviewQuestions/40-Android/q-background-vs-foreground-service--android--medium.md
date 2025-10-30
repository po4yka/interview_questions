---
id: 20251016-161808
title: Background vs Foreground Service / Фоновый vs активный сервис
aliases: ["Background vs Foreground Service", "Фоновый vs активный сервис"]
topic: android
subtopics: [background-execution, service]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-service, c-workmanager, q-android-service-types--android--easy, q-background-tasks-decision-guide--android--medium, q-foreground-service-types--background--medium]
sources: []
created: 2025-10-15
updated: 2025-10-29
tags: [android/background-execution, android/service, difficulty/medium]
---

# Вопрос (RU)
> В чём разница между Background и Foreground Service?

---

# Question (EN)
> What is the difference between background and foreground service?

---

## Ответ (RU)

### Основные различия

| Характеристика | Background Service | Foreground Service |
|----------------|-------------------|-------------------|
| Уведомление | Не требуется | Обязательно |
| Приоритет | Низкий | Высокий |
| Завершение | Система может убить | Защищён от завершения |
| Ограничения | Заблокирован с Android 8.0+ | Нужен тип сервиса с Android 14+ |
| Применение | Устарел | Долгие видимые операции |

### Реализация

**✅ Foreground Service**
```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ОБЯЗАТЕЛЬНО в течение 5 секунд после startForegroundService()
        startForeground(NOTIFICATION_ID, buildNotification())
        playMusic()
        return START_STICKY
    }

    private fun buildNotification() = NotificationCompat.Builder(this, CHANNEL_ID)
        .setContentTitle("Playing music")
        .setSmallIcon(R.drawable.ic_music)
        .setOngoing(true)
        .build()
}

// Запуск
context.startForegroundService(Intent(context, MusicService::class.java))
```

**❌ Background Service (запрещён с Android 8.0+)**
```kotlin
class BackgroundService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ❌ IllegalStateException: Not allowed to start service Intent
        performWork()
        return START_NOT_STICKY
    }
}
```

**✅ Альтернатива: WorkManager**
```kotlin
val workRequest = OneTimeWorkRequestBuilder<SyncWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(workRequest)
```

### Ограничения платформы

**Android 8.0 (API 26)+**
- `startService()` → `IllegalStateException` для фоновых приложений
- Решение: `startForegroundService()` + `startForeground()` за 5 секунд

**Android 14 (API 34)+**
- Обязательный тип сервиса в манифесте:
```xml
<service android:name=".MusicService"
    android:foregroundServiceType="mediaPlayback" />
```

**Приоритет процессов**
1. **Foreground** (Foreground Service) - не завершается
2. Visible - редко завершается
3. **Service** (Background Service) - может быть убит
4. Cached - убивается первым

### Выбор подхода

**Foreground Service когда:**
- Операция видима пользователю (музыка, навигация, загрузка)
- Требуется немедленное выполнение
- Долгая операция (> 10 минут)

**WorkManager когда:**
- Можно отложить выполнение
- Нужны ограничения (Wi-Fi, зарядка)
- Периодическая синхронизация

---

## Answer (EN)

### Core Differences

| Feature | Background Service | Foreground Service |
|---------|-------------------|-------------------|
| Notification | Not required | Mandatory |
| Priority | Low | High |
| Termination | System can kill | Protected from termination |
| Restrictions | Blocked since Android 8.0+ | Requires type since Android 14+ |
| Use case | Deprecated | Long-running visible operations |

### Implementation

**✅ Foreground Service**
```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // MUST call within 5 seconds of startForegroundService()
        startForeground(NOTIFICATION_ID, buildNotification())
        playMusic()
        return START_STICKY
    }

    private fun buildNotification() = NotificationCompat.Builder(this, CHANNEL_ID)
        .setContentTitle("Playing music")
        .setSmallIcon(R.drawable.ic_music)
        .setOngoing(true)
        .build()
}

// Starting
context.startForegroundService(Intent(context, MusicService::class.java))
```

**❌ Background Service (prohibited since Android 8.0+)**
```kotlin
class BackgroundService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ❌ IllegalStateException: Not allowed to start service Intent
        performWork()
        return START_NOT_STICKY
    }
}
```

**✅ Alternative: WorkManager**
```kotlin
val workRequest = OneTimeWorkRequestBuilder<SyncWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(workRequest)
```

### Platform Restrictions

**Android 8.0 (API 26)+**
- `startService()` → `IllegalStateException` for background apps
- Solution: `startForegroundService()` + `startForeground()` within 5 seconds

**Android 14 (API 34)+**
- Mandatory service type in manifest:
```xml
<service android:name=".MusicService"
    android:foregroundServiceType="mediaPlayback" />
```

**Process Priority**
1. **Foreground** (Foreground Service) - never killed
2. Visible - rarely killed
3. **Service** (Background Service) - can be killed
4. Cached - killed first

### Choosing Approach

**Foreground Service when:**
- Operation is user-visible (music, navigation, download)
- Immediate execution required
- Long operation (> 10 minutes)

**WorkManager when:**
- Deferrable execution
- Constraints needed (Wi-Fi, charging)
- Periodic sync

---

## Follow-ups

- What are the 12 foreground service types introduced in Android 14 and when to use each?
- How to properly stop a foreground service and remove notification?
- What happens if `startForeground()` is not called within 5 seconds?
- How to handle service lifecycle during process death and restoration?
- What are the notification channel requirements for foreground services?

---

## References

- [[c-service]]
- [[c-workmanager]]
- [[c-notification]]
- https://developer.android.com/develop/background-work/services/foreground-services
- https://developer.android.com/develop/background-work/background-tasks

---

## Related Questions

### Prerequisites (Easier)
- [[q-android-service-types--android--easy]]
- [[q-android-services-purpose--android--easy]]

### Related (Same Level)
- [[q-background-tasks-decision-guide--android--medium]]
- [[q-foreground-service-types--background--medium]]
- [[q-workmanager-basics--android--medium]]

### Advanced (Harder)
- [[q-workmanager-advanced--android--hard]]
- [[q-service-lifecycle-edge-cases--android--hard]]
