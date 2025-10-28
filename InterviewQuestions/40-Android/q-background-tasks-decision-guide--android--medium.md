---
id: 20251012-122786
title: Background Tasks Decision Guide / Руководство по фоновым задачам
aliases: [Background Tasks Decision Guide, Руководство по фоновым задачам, Android Background Work]
topic: android
subtopics: [background-execution, coroutines, service]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - q-async-operations-android--android--medium
  - q-foreground-service-types--background--medium
  - q-what-is-workmanager--android--medium
  - c-coroutines
sources: []
created: 2025-10-05
updated: 2025-10-28
tags: [android/background-execution, android/coroutines, android/service, difficulty/medium]
---

# Вопрос (RU)
> Как выбрать правильный способ выполнения фоновых задач в Android?

---

# Question (EN)
> How to choose the right approach for background tasks in Android?

---

## Ответ (RU)

**Подход**: Выбор зависит от трех факторов: нужно ли продолжать работу в фоне, можно ли отложить выполнение, насколько критична задача

**Типы фоновых задач**:

**Асинхронная работа** - операции во время работы приложения
- Останавливается при сворачивании
- Для UI-расчетов, API-запросов
- Инструменты: Kotlin coroutines, Java threads

**Отложенные задачи** - выживают после закрытия приложения
- Учитывают системные ограничения
- Для периодической синхронизации, загрузки контента
- Инструменты: WorkManager, JobScheduler

**Foreground сервисы** - немедленное выполнение с уведомлением
- Строгие ограничения Android 14+
- Для воспроизведения медиа, отслеживания местоположения
- Типы: обычный, shortService (< 3 минут)

**Дерево решений для пользовательских задач**:

1. Нужно продолжать в фоне? НЕТ → асинхронная работа
2. Можно отложить? ДА → WorkManager
3. Короткая и критичная? ДА → foreground service (shortService)
4. Есть специализированный API? ДА → использовать (geofence, media session)
5. Иначе → foreground service

**Код**:

```kotlin
// ✅ Асинхронная работа - coroutines
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) { fetchData() }
    updateUI(data)
}

// ✅ Отложенные задачи - WorkManager
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .build()

val work = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS)
    .setConstraints(constraints)
    .build()

// ✅ Foreground service - shortService
class QuickService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(1, createNotification())
        doWork()
        stopSelf()
        return START_NOT_STICKY
    }
}
```

**Объяснение**:
- **Coroutines**: для работы во время активности приложения, автоматическая отмена при уничтожении scope
- **WorkManager**: гарантирует выполнение даже после перезагрузки, соблюдает battery optimization
- **ShortService**: для критичных задач до 3 минут (файловый менеджер, быстрая синхронизация)

---

## Answer (EN)

**Approach**: Choice depends on three factors: must continue in background, can be deferred, criticality level

**Background Task Types**:

**Asynchronous work** - operations while app is foreground
- Stops when app backgrounded
- For UI calculations, API calls
- Tools: Kotlin coroutines, Java threads

**Task scheduling** - survives app termination
- Respects system constraints
- For periodic sync, content uploads
- Tools: WorkManager, JobScheduler

**Foreground services** - immediate execution with notification
- Strict restrictions on Android 14+
- For media playback, location tracking
- Types: regular, shortService (< 3 minutes)

**Decision tree for user-initiated tasks**:

1. Continue in background? NO → asynchronous work
2. Can be deferred? YES → WorkManager
3. Short and critical? YES → foreground service (shortService)
4. Specialized API available? YES → use it (geofence, media session)
5. Otherwise → foreground service

**Code**:

```kotlin
// ✅ Asynchronous work - coroutines
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) { fetchData() }
    updateUI(data)
}

// ✅ Task scheduling - WorkManager
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .build()

val work = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS)
    .setConstraints(constraints)
    .build()

// ✅ Foreground service - shortService
class QuickService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(1, createNotification())
        doWork()
        stopSelf()
        return START_NOT_STICKY
    }
}
```

**Explanation**:
- **Coroutines**: for work during app activity, automatic cancellation when scope destroyed
- **WorkManager**: guarantees execution even after reboot, respects battery optimization
- **ShortService**: for critical tasks up to 3 minutes (file manager, quick sync)

---

## Follow-ups

- What are foreground service type restrictions on Android 14+?
- How does WorkManager handle retries and backoff?
- When to use JobScheduler instead of WorkManager?
- How to migrate from deprecated background APIs?

## References

- [[c-coroutines]]
- [[c-workmanager]]
- https://developer.android.com/develop/background-work/background-tasks

## Related Questions

### Prerequisites (Easier)
- [[q-async-operations-android--android--medium]]
- [[q-android-service-types--android--easy]]
- [[q-android-services-purpose--android--easy]]

### Related (Same Level)
- [[q-what-is-workmanager--android--medium]]
- [[q-foreground-service-types--background--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]
