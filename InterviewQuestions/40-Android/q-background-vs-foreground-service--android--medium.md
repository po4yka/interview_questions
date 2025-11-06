---
id: android-195
title: Background vs Foreground Service / Фоновый vs активный сервис
aliases: [Background vs Foreground Service, Фоновый vs активный сервис]
topic: android
subtopics:
  - background-execution
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
  - c-service
  - c-workmanager
  - q-android-service-types--android--easy
sources: []
created: 2025-10-15
updated: 2025-10-30
tags: [android/background-execution, android/service, difficulty/medium]
---

# Вопрос (RU)
> В чём разница между Background и Foreground Service в Android?

---

# Question (EN)
> What is the difference between background and foreground service in Android?

---

## Ответ (RU)

### Ключевые Различия

| Характеристика | Background Service | Foreground Service |
|----------------|-------------------|-------------------|
| Уведомление | Не требуется | Обязательно (непрерывное) |
| Приоритет процесса | Низкий | Высокий |
| Завершение системой | Может быть убит | Защищён |
| Ограничения запуска | Запрещён с API 26+ | Требует тип с API 34+ |
| Применение | Устарел | Видимые долгие операции |

### Реализация

**✅ Foreground Service**
```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ОБЯЗАТЕЛЬНО: в течение 5 секунд после startForegroundService()
        startForeground(NOTIFICATION_ID, buildNotification())
        playMusic()
        return START_STICKY
    }

    private fun buildNotification() = NotificationCompat.Builder(this, CHANNEL_ID)
        .setContentTitle("Воспроизведение музыки")
        .setSmallIcon(R.drawable.ic_music)
        .setOngoing(true) // ✅ Непрерывное уведомление
        .build()
}

// Запуск
context.startForegroundService(Intent(context, MusicService::class.java))
```

**❌ Background Service (запрещён с API 26+)**
```kotlin
class BackgroundService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ❌ IllegalStateException: Not allowed to start service Intent
        performWork()
        return START_NOT_STICKY
    }
}
```

**✅ Современная альтернатива: WorkManager**
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

### Ограничения Платформы

**API 26+** (Android 8.0)
- `startService()` → `IllegalStateException` для фоновых приложений
- Решение: `startForegroundService()` + `startForeground()` за 5 секунд

**API 34+** (Android 14)
- Обязательный тип сервиса в манифесте:
```xml
<service android:name=".MusicService"
    android:foregroundServiceType="mediaPlayback" />
```
- Типы: `camera`, `connectedDevice`, `dataSync`, `health`, `location`, `mediaPlayback`, `mediaProjection`, `microphone`, `phoneCall`, `remoteMessaging`, `shortService`, `specialUse`, `systemExempted`

**Приоритет процессов**
1. Foreground (с Foreground Service) - защищён от завершения
2. Visible - редко завершается
3. Service (Background Service) - может быть убит при нехватке памяти
4. Cached - убивается первым

### Выбор Подхода

**Foreground Service:**
- Операция видна пользователю (музыка, навигация, отслеживание тренировки)
- Требуется немедленное выполнение
- Длительность > 10 минут

**WorkManager:**
- Отложенное выполнение допустимо
- Нужны условия (Wi-Fi, зарядка)
- Периодическая синхронизация
- Гарантированное выполнение с повторными попытками

---

## Answer (EN)

### Core Differences

| Feature | Background Service | Foreground Service |
|---------|-------------------|-------------------|
| Notification | Not required | Mandatory (ongoing) |
| Process priority | Low | High |
| System termination | Can be killed | Protected |
| Launch restrictions | Prohibited since API 26+ | Requires type since API 34+ |
| Use case | Deprecated | Visible long operations |

### Implementation

**✅ Foreground Service**
```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // REQUIRED: within 5 seconds of startForegroundService()
        startForeground(NOTIFICATION_ID, buildNotification())
        playMusic()
        return START_STICKY
    }

    private fun buildNotification() = NotificationCompat.Builder(this, CHANNEL_ID)
        .setContentTitle("Playing music")
        .setSmallIcon(R.drawable.ic_music)
        .setOngoing(true) // ✅ Ongoing notification
        .build()
}

// Starting
context.startForegroundService(Intent(context, MusicService::class.java))
```

**❌ Background Service (prohibited since API 26+)**
```kotlin
class BackgroundService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ❌ IllegalStateException: Not allowed to start service Intent
        performWork()
        return START_NOT_STICKY
    }
}
```

**✅ Modern alternative: WorkManager**
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

**API 26+** (Android 8.0)
- `startService()` → `IllegalStateException` for background apps
- Solution: `startForegroundService()` + `startForeground()` within 5 seconds

**API 34+** (Android 14)
- Mandatory service type in manifest:
```xml
<service android:name=".MusicService"
    android:foregroundServiceType="mediaPlayback" />
```
- Types: `camera`, `connectedDevice`, `dataSync`, `health`, `location`, `mediaPlayback`, `mediaProjection`, `microphone`, `phoneCall`, `remoteMessaging`, `shortService`, `specialUse`, `systemExempted`

**Process Priority**
1. Foreground (with Foreground Service) - protected from termination
2. Visible - rarely killed
3. Service (Background Service) - can be killed when low on memory
4. Cached - killed first

### Choosing Approach

**Foreground Service:**
- User-visible operation (music, navigation, workout tracking)
- Immediate execution required
- Duration > 10 minutes

**WorkManager:**
- Deferrable execution acceptable
- Constraints needed (Wi-Fi, charging)
- Periodic synchronization
- Guaranteed execution with retries

---

## Follow-ups

- What happens if `startForeground()` is not called within 5 seconds after `startForegroundService()`?
- How to properly stop a foreground service and remove its notification?
- Which foreground service types require runtime permissions?
- How does process priority affect service lifecycle during low memory?
- What are the alternatives for immediate task execution without foreground service?

---

## References

- [[c-service]]
- [[c-workmanager]]
- [[c-notification]]
- [[c-process-lifecycle]]
- [Foreground Services](https://developer.android.com/develop/background-work/services/foreground-services)
- https://developer.android.com/develop/background-work/background-tasks
---


## Related Questions

### Prerequisites (Easier)
- [[q-android-service-types--android--easy]] - Understanding service types
- [[q-android-services-purpose--android--easy]] - Why use services

### Related (Same Level)
- [[q-background-tasks-decision-guide--android--medium]] - Choosing background execution approach
 - WorkManager fundamentals
 - Notification requirements

### Advanced (Harder)
- [[q-service-lifecycle-binding--android--hard]] - Service lifecycle edge cases