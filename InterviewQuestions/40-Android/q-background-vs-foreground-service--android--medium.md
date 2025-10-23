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
status: reviewed
moc: moc-android
related:
- q-android-service-types--android--easy
- q-foreground-services--android--medium
- q-background-tasks-decision-guide--android--medium
created: 2025-10-15
updated: 2025-10-15
tags:
- android/service
- android/background-execution
- service
- foreground-service
- background-service
- difficulty/medium
---# Вопрос (RU)
> Чем background service отличается от foreground service?

---

# Question (EN)
> How does background service differ from foreground service?

## Ответ (RU)

### Основные различия

**Background Service**
- Теория: Работает без ведома пользователя; низкий приоритет; может быть убит системой
- Характеристики: Уведомление не требуется; приоритет Service Process; Android 8.0+ сильно ограничен
- Случаи использования: Только legacy приложения; современные приложения должны использовать WorkManager

**Foreground Service**
- Теория: Видим пользователю с постоянным уведомлением; высокий приоритет; защищен от завершения
- Характеристики: Обязательное уведомление; приоритет Foreground Process; выживает при системном давлении
- Случаи использования: Воспроизведение музыки, навигация, загрузка файлов, длительные задачи по инициативе пользователя

### Сравнение реализации

**Background Service (Устарел)**
```kotlin
// Теория: Без уведомления, низкий приоритет, может быть убит
class BackgroundService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Работа без уведомления - рискованно на Android 8.0+
        doWork()
        return START_NOT_STICKY
    }
}
```

**Foreground Service**
```kotlin
// Теория: Уведомление обязательно, высокий приоритет, защищен
class ForegroundService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Должен вызвать startForeground в течение 5 секунд
        startForeground(NOTIFICATION_ID, createNotification())
        doWork()
        return START_STICKY
    }

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Сервис работает")
            .setSmallIcon(R.drawable.ic_service)
            .setOngoing(true)
            .build()
    }
}
```

### Ограничения Android 8.0+

**Ограничения Background Service**
- Теория: Система предотвращает запуск background service когда приложение в фоне
- Исключение: `IllegalStateException: Not allowed to start service`
- Решение: Использовать `startForegroundService()` или WorkManager

**Требования Foreground Service**
- Теория: Должен вызвать `startForeground()` в течение 5 секунд после `onStartCommand()`
- Неудача: Система убивает сервис с ANR
- Уведомление: Должно быть постоянным и ongoing

### Иерархия приоритетов процессов

```
1. Foreground Process (Foreground Service) - Высший приоритет
2. Visible Process
3. Service Process (Background Service) - Может быть убит
4. Cached Process
5. Empty Process
```

### Фреймворк принятия решений

**Используйте Foreground Service когда:**
- Задача видима пользователю и чувствительна ко времени
- Пользователь инициировал операцию
- Задача требует немедленного выполнения
- Примеры: Воспроизведение музыки, навигация, загрузка файлов

**Используйте WorkManager вместо Background Service когда:**
- Задачу можно отложить
- Нужно периодическое выполнение
- Следует учитывать системные ограничения
- Примеры: Синхронизация данных, периодические обновления, очистка

---

## Answer (EN)

### Core Differences

**Background Service**
- Theory: Runs without user awareness; low priority; can be killed by system
- Characteristics: No notification required; Service Process priority; Android 8.0+ severely restricted
- Use cases: Legacy apps only; modern apps should use WorkManager

**Foreground Service**
- Theory: User-visible with persistent notification; high priority; protected from termination
- Characteristics: Required notification; Foreground Process priority; survives system pressure
- Use cases: Music playback, navigation, file downloads, user-initiated long tasks

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

