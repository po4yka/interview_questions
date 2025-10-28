---
id: 20251016-161808
title: Background vs Foreground Service / Background vs Foreground Service
aliases: [Background vs Foreground Service, Background Service, Foreground Service, Background сервис, Foreground сервис]
topic: android
subtopics: [background-execution, service]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-service-types--android--easy, q-background-tasks-decision-guide--android--medium, q-foreground-service-types--background--medium]
sources: []
created: 2025-10-15
updated: 2025-10-28
tags: [android/background-execution, android/service, difficulty/medium]
---

# Вопрос (RU)
> В чём разница между Background и Foreground Service?

---

# Question (EN)
> What is the difference between background and foreground service?

---

## Ответ (RU)

### Ключевые различия

**Background Service**
- Работает без уведомления пользователя; низкий приоритет; система может завершить процесс
- Android 8.0+ сильно ограничивает использование
- Современные приложения должны использовать WorkManager

**Foreground Service**
- Видимый пользователю через постоянное уведомление; высокий приоритет; защищён от завершения
- Обязательно требует уведомление
- Примеры: воспроизведение музыки, навигация, загрузка файлов

### Реализация Foreground Service

```kotlin
class ForegroundService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ ОБЯЗАТЕЛЬНО вызвать в течение 5 секунд
        startForeground(NOTIFICATION_ID, createNotification())
        performWork()
        return START_STICKY
    }

    private fun createNotification() = NotificationCompat.Builder(this, CHANNEL_ID)
        .setContentTitle("Сервис запущен")
        .setSmallIcon(R.drawable.ic_service)
        .setOngoing(true) // ✅ Постоянное уведомление
        .build()
}
```

**❌ Background Service (устарел)**
```kotlin
class BackgroundService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ❌ Без уведомления - система завершит на Android 8.0+
        performWork()
        return START_NOT_STICKY
    }
}
```

### Ограничения Android 8.0+

**Background Service**
- ❌ Система блокирует запуск фоновых сервисов: `IllegalStateException: Not allowed to start service`
- ✅ Решение: использовать `startForegroundService()` или WorkManager

**Foreground Service**
- ✅ Обязательно вызвать `startForeground()` в течение 5 секунд
- ❌ Иначе: система завершит сервис с ANR

### Иерархия приоритетов процессов

```
1. Foreground Process (Foreground Service) - Наивысший приоритет
2. Visible Process
3. Service Process (Background Service) - Может быть завершён
4. Cached Process
5. Empty Process
```

### Когда использовать

**Foreground Service:**
- Задача видима пользователю и критична по времени
- Пользователь инициировал операцию
- Примеры: музыка, навигация, загрузка

**WorkManager (вместо Background Service):**
- Задачу можно отложить
- Нужно периодическое выполнение
- Примеры: синхронизация данных, обновления

---

## Answer (EN)

### Core Differences

**Background Service**
- Runs without user notification; low priority; can be terminated by system
- Android 8.0+ severely restricts usage
- Modern apps should use WorkManager

**Foreground Service**
- User-visible with persistent notification; high priority; protected from termination
- Notification is mandatory
- Examples: music playback, navigation, file downloads

### Foreground Service Implementation

```kotlin
class ForegroundService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ MUST call within 5 seconds
        startForeground(NOTIFICATION_ID, createNotification())
        performWork()
        return START_STICKY
    }

    private fun createNotification() = NotificationCompat.Builder(this, CHANNEL_ID)
        .setContentTitle("Service Running")
        .setSmallIcon(R.drawable.ic_service)
        .setOngoing(true) // ✅ Persistent notification
        .build()
}
```

**❌ Background Service (deprecated)**
```kotlin
class BackgroundService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ❌ No notification - system will kill on Android 8.0+
        performWork()
        return START_NOT_STICKY
    }
}
```

### Android 8.0+ Restrictions

**Background Service**
- ❌ System blocks background service starts: `IllegalStateException: Not allowed to start service`
- ✅ Solution: use `startForegroundService()` or WorkManager

**Foreground Service**
- ✅ Must call `startForeground()` within 5 seconds of `onStartCommand()`
- ❌ Otherwise: system kills service with ANR

### Process Priority Hierarchy

```
1. Foreground Process (Foreground Service) - Highest priority
2. Visible Process
3. Service Process (Background Service) - Can be killed
4. Cached Process
5. Empty Process
```

### When to Use

**Foreground Service:**
- Task is user-visible and time-sensitive
- User initiated the operation
- Examples: music, navigation, downloads

**WorkManager (instead of Background Service):**
- Task can be deferred
- Periodic execution needed
- Examples: data sync, updates

---

## Follow-ups

- What notification requirements exist for foreground services in Android 13+?
- How to migrate from background services to WorkManager?
- What are foreground service types and why are they required?
- How to handle service lifecycle during configuration changes?

---

## References

- [[c-service]]
- [[c-workmanager]]
- https://developer.android.com/guide/components/services
- https://developer.android.com/develop/background-work/services/foreground-services

---

## Related Questions

### Prerequisites (Easier)
- [[q-android-service-types--android--easy]]
- [[q-android-services-purpose--android--easy]]

### Related (Same Level)
- [[q-background-tasks-decision-guide--android--medium]]
- [[q-foreground-service-types--background--medium]]

### Advanced (Harder)
- [[q-workmanager-advanced--android--hard]]
