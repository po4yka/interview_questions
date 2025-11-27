---
id: android-195
title: Background vs Foreground Service / Фоновый vs Foreground-сервис
aliases: [Background vs Foreground Service, Фоновый vs Foreground-сервис]
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
status: draft
moc: moc-android
related:
  - c-background-tasks
  - q-android-service-types--android--easy
  - q-android-services-purpose--android--easy
  - q-background-tasks-decision-guide--android--medium
  - q-foreground-service-types--android--medium
  - q-when-can-the-system-restart-a-service--android--medium
sources: []
created: 2023-10-15
updated: 2025-11-10
tags: [android/background-execution, android/service, difficulty/medium]

date created: Saturday, November 1st 2025, 1:04:15 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---
# Вопрос (RU)
> В чем разница между background-сервисом и foreground-сервисом в Android?

---

# Question (EN)
> What is the difference between background and foreground service in Android?

---

## Ответ (RU)

### Ключевые Отличия

| Характеристика | Background `Service` | Foreground `Service` |
|----------------|----------------------|----------------------|
| Уведомление | Не требуется по умолчанию; может показываться при необходимости | Обязательно: постоянное уведомление |
| Приоритет процесса | Ниже | Выше (foreground-приоритет) |
| Завершение системой | Может быть завершен системой при нехватке ресурсов | Сильно приоритизируется; все еще может быть убит при экстремальном давлении |
| Ограничения запуска | С API 26+ сильно ограничен запуск из фона | Для многих кейсов требуется `foregroundServiceType` (API 29+, ужесточено в API 34+) |
| Типичные кейсы | Ограниченное применение; нельзя свободно запускать из фона | Длительные, заметные пользователю операции (медиа, навигация, тренировки и т.п.) |

(Background-сервисы формально не помечены как deprecated, но свободные фоновые запуски сильно ограничены; рекомендуется использовать современные API для фоновых задач.)

### Реализация

**✅ Foreground `Service`**
```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ОБЯЗАТЕЛЬНО: вызвать startForeground() в течение 5 секунд после startForegroundService()
        startForeground(NOTIFICATION_ID, buildNotification())
        playMusic()
        return START_STICKY
    }

    private fun buildNotification() = NotificationCompat.Builder(this, CHANNEL_ID)
        .setContentTitle("Playing music")
        .setSmallIcon(R.drawable.ic_music)
        .setOngoing(true) // ✅ Постоянное уведомление
        .build()
}

// Запуск, когда приложению разрешено создать foreground service
context.startForegroundService(Intent(context, MusicService::class.java))
```

**❌ Background `Service` (небезопасно запускать из фона с API 26+)**
```kotlin
class BackgroundService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // На API 26+: возможен IllegalStateException, если startService() вызван, когда приложение в фоне
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

WorkManager (см. [[c-background-tasks]]):
- подходит для отложенных и гарантированных задач;
- учитывает условия (Wi‑Fi, зарядка и т.п.);
- обеспечивает повторные попытки при сбоях.

### Платформенные Ограничения

**API 26+** (Android 8.0)
- Вызов `startService()` из фонового состояния может привести к `IllegalStateException` ("Not allowed to start service `Intent`").
- Решение: для работы, которая должна продолжаться в фоне, использовать `startForegroundService()` и вызвать `startForeground()` в течение 5 секунд.

**API 34+** (Android 14)
- Foreground-сервисы, работающие при нахождении приложения в фоне, должны объявлять соответствующий `android:foregroundServiceType` в манифесте; требования стали строже и строго применяются.
```xml
<service android:name=".MusicService"
    android:foregroundServiceType="mediaPlayback" />
```
- Примеры типов: `camera`, `connectedDevice`, `dataSync`, `health`, `location`, `mediaPlayback`, `mediaProjection`, `microphone`, `phoneCall`, `remoteMessaging`, `shortService`, `specialUse`, `systemExempted`.

**Приоритет процесса**
1. Foreground (например, активность в resumed-состоянии или foreground `Service`) — наивысший приоритет, минимальный риск быть убитым.
2. Visible — компонент видим пользователю, но не в полном foreground; реже всего завершается.
3. `Service` (процесс с background-сервисами) — ниже, чем foreground/visible; может быть убит при нехватке памяти.
4. Cached — нет активных компонентов; убивается первым.

### Выбор Подхода

**Foreground `Service`:**
- Пользовательская, заметная операция (музыка, навигация, трекинг тренировок и т.п.).
- Требуется немедленное и непрерывное выполнение, пока пользователь ожидает результат.
- Подходит для долгих задач, которые должны продолжать работу в фоне и не могут быть отложены.

**WorkManager:**
- Задача может быть отложена.
- Зависит от условий (Wi‑Fi, зарядка и т.п.).
- Подходит для периодической синхронизации, загрузок, задач обслуживания.
- Нужна гарантированная попытка выполнения с ретраями.

---

## Answer (EN)

### Core Differences

| Feature | Background `Service` | Foreground `Service` |
|---------|-------------------|-------------------|
| Notification | Not required by default; may be shown if needed | Mandatory (ongoing notification) |
| Process priority | Lower | Higher (foreground priority) |
| System termination | Can be killed | Strongly prioritized; can still be killed under extreme pressure |
| Launch restrictions | Restricted since API 26+ for background apps | Requires `foregroundServiceType` (API 29+, tightened in API 34+) for many use cases |
| Use case | Limited use; cannot be started freely from background | `Long`-running, user-visible operations (media, navigation, workout, etc.) |

(Background services are not formally deprecated as a class, but unrestricted background starts are heavily constrained; prefer modern background APIs.)

### Implementation

**✅ Foreground `Service`**
```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // REQUIRED: Call startForeground() within 5 seconds after startForegroundService()
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

// Starting while app is allowed to create a foreground service
context.startForegroundService(Intent(context, MusicService::class.java))
```

**❌ Background `Service` (unsafe from background since API 26+)**
```kotlin
class BackgroundService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // On API 26+: may throw IllegalStateException if startService() is called while app is in background
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

WorkManager (see [[c-background-tasks]]):
- suitable for deferred and guaranteed tasks;
- respects conditions (Wi‑Fi, charging, etc.);
- provides retries on failure.

### Platform Restrictions

**API 26+** (Android 8.0)
- `startService()` from the background can cause `IllegalStateException` ("Not allowed to start service `Intent`").
- Solution: use `startForegroundService()` for work that must continue in the background, and call `startForeground()` within 5 seconds.

**API 34+** (Android 14)
- Foreground services that run while the app is in the background must declare an appropriate `android:foregroundServiceType` in the manifest; requirements are stricter and enforced.
```xml
<service android:name=".MusicService"
    android:foregroundServiceType="mediaPlayback" />
```
- Types include: `camera`, `connectedDevice`, `dataSync`, `health`, `location`, `mediaPlayback`, `mediaProjection`, `microphone`, `phoneCall`, `remoteMessaging`, `shortService`, `specialUse`, `systemExempted`.

**Process Priority**
1. Foreground (e.g., hosting a foreground service or resumed activity) - highest, less likely to be killed.
2. Visible - user-visible but not foreground; rarely killed.
3. `Service` (process hosting background services) - lower than visible/foreground; can be killed under memory pressure.
4. Cached - no active components; killed first.

### Choosing Approach

**Foreground `Service`:**
- User-visible operation (e.g., music playback, navigation, workout tracking).
- Needs immediate and continuous execution while user expects it.
- Suitable for long-running tasks that must keep running in background and cannot be deferred.

**WorkManager:**
- Execution can be deferred.
- Requires conditions (Wi-Fi, charging, etc.).
- Periodic sync, uploads, maintenance jobs.
- Needs guaranteed execution with retries.

---

## Дополнительные Вопросы (RU)

- Что произойдет, если `startForeground()` не будет вызван в течение 5 секунд после `startForegroundService()`?
- Как корректно остановить foreground-сервис и убрать его уведомление?
- Какие типы foreground-сервисов требуют runtime-разрешений?
- Как приоритет процесса влияет на жизненный цикл сервиса при нехватке памяти?
- Какие альтернативы использовать для немедленного выполнения задач без foreground-сервиса?

---

## Follow-ups

- What happens if `startForeground()` is not called within 5 seconds after `startForegroundService()`?
- How to properly stop a foreground service and remove its notification?
- Which foreground service types require runtime permissions?
- How does process priority affect service lifecycle during low memory?
- What are the alternatives for immediate task execution without a foreground service?

---

## Ссылки (RU)

- [Foreground Services](https://developer.android.com/develop/background-work/services/foreground-services)
- https://developer.android.com/develop/background-work/background-tasks

---

## References

- [Foreground Services](https://developer.android.com/develop/background-work/services/foreground-services)
- https://developer.android.com/develop/background-work/background-tasks

---

## Связанные Вопросы (RU)

### База (проще)
- [[q-android-service-types--android--easy]] - Типы сервисов в Android
- [[q-android-services-purpose--android--easy]] - Зачем нужны сервисы

### Связанные (тот Же уровень)
- [[q-background-tasks-decision-guide--android--medium]] - Выбор подхода для фоновых задач

### Продвинутые (сложнее)
- [[q-service-lifecycle-binding--android--hard]] - Особенности жизненного цикла `Service`

---

## Related Questions

### Prerequisites (Easier)
- [[q-android-service-types--android--easy]] - Understanding service types
- [[q-android-services-purpose--android--easy]] - Why use services

### Related (Same Level)
- [[q-background-tasks-decision-guide--android--medium]] - Choosing background execution approach

### Advanced (Harder)
- [[q-service-lifecycle-binding--android--hard]] - `Service` lifecycle edge cases
