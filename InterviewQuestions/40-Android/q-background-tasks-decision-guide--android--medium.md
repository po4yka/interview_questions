---
id: 20251012-122786
title: Background Tasks Decision Guide / Руководство по фоновым задачам
aliases: [Background Tasks Decision Guide, Руководство по фоновым задачам]
topic: android
subtopics: [background-execution, coroutines, service]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: reviewed
moc: moc-android
related: [q-async-operations-android--android--medium, q-workmanager-basics--android--medium, q-foreground-services--android--medium]
created: 2025-10-05
updated: 2025-10-15
tags: [android/background-execution, android/coroutines, android/service, workmanager, coroutines, service, difficulty/medium]
---# Вопрос (RU)
> Что такое фоновая задача и как она должна выполняться?

---

# Question (EN)
> What is a background task and how should it be performed?

## Ответ (RU)

### Типы фоновых задач

**Асинхронная работа**
- Теория: Параллельные операции пока приложение на переднем плане; предотвращает ANR; останавливается при переходе в фон
- Случаи использования: UI вычисления, обработка данных, API вызовы
- Варианты: Kotlin корутины, Java потоки

**API планирования задач**
- Теория: Отложенное выполнение; переживает завершение приложения; учитывает системные ограничения
- Случаи использования: Периодическая синхронизация, сбор данных с датчиков, загрузка контента
- Варианты: WorkManager (рекомендуется), JobScheduler

**Сервисы переднего плана**
- Теория: Немедленное выполнение; видимы пользователю; высокое потребление ресурсов; строгие ограничения
- Случаи использования: Воспроизведение медиа, отслеживание местоположения, загрузка файлов
- Типы: Обычный сервис, shortService (< 3 минут)

### Фреймворк принятия решений

**Задачи, инициированные пользователем**

1. **Продолжать в фоне?**
   - Нет → Асинхронная работа
   - Да → Следующий вопрос

2. **Можно отложить?**
   - Да → API планирования задач
   - Нет → Следующий вопрос

3. **Короткая и критическая?**
   - Да → Сервис переднего плана (shortService)
   - Нет → Проверить специализированные API

4. **Доступен специализированный API?**
   - Да → Использовать специализированный API (geofence, media session)
   - Нет → Сервис переднего плана

**Задачи, вызванные событиями**

1. **Длительность < несколько секунд?**
   - Да → Асинхронная работа
   - Нет → Проверить возможность запуска сервиса переднего плана

2. **Можно запустить сервис переднего плана?**
   - Да → Сервис переднего плана
   - Нет → API планирования задач

### Примеры реализации

**Асинхронная работа**
```kotlin
// Корутины - структурированная конкурентность
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) { fetchData() }
    updateUI(data)
}

// Потоки - ручное управление
Thread {
    val result = compute()
    runOnUiThread { render(result) }
}.start()
```

**WorkManager**
```kotlin
// Периодическая работа с ограничениями
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .setRequiresBatteryNotLow(true)
    .build()

val workRequest = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS)
    .setConstraints(constraints)
    .build()

WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "sync", ExistingPeriodicWorkPolicy.KEEP, workRequest
)
```

**Сервис переднего плана**
```kotlin
// Короткий сервис для быстрых задач
class QuickTaskService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(1, notification)

        // Выполнить работу
        stopSelf()
        return START_NOT_STICKY
    }
}
```

---

## Answer (EN)

### Background Task Types

**Asynchronous Work**
- Theory: Concurrent operations while app is foreground; prevents ANR; stops when app backgrounded
- Use cases: UI calculations, data processing, API calls
- Options: Kotlin coroutines, Java threads

**Task Scheduling APIs**
- Theory: Deferred execution; survives app termination; respects system constraints
- Use cases: Periodic sync, sensor data collection, content uploads
- Options: WorkManager (recommended), JobScheduler

**Foreground Services**
- Theory: Immediate execution; user-visible; high resource usage; strict restrictions
- Use cases: Media playback, location tracking, file downloads
- Types: Regular service, shortService (< 3 minutes)

### Decision Framework

**User-Initiated Tasks**

1. **Continue in background?**
   - No → Asynchronous work
   - Yes → Next question

2. **Can be deferred?**
   - Yes → Task scheduling APIs
   - No → Next question

3. **Short and critical?**
   - Yes → Foreground service (shortService)
   - No → Check for specialized APIs

4. **Specialized API available?**
   - Yes → Use specialized API (geofence, media session)
   - No → Foreground service

**Event-Triggered Tasks**

1. **Duration < few seconds?**
   - Yes → Asynchronous work
   - No → Check foreground service eligibility

2. **Can start foreground service?**
   - Yes → Foreground service
   - No → Task scheduling APIs

### Implementation Examples

**Asynchronous Work**
```kotlin
// Coroutines - structured concurrency
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) { fetchData() }
    updateUI(data)
}

// Threads - manual management
Thread {
    val result = compute()
    runOnUiThread { render(result) }
}.start()
```

**WorkManager**
```kotlin
// Periodic work with constraints
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .setRequiresBatteryNotLow(true)
    .build()

val workRequest = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS)
    .setConstraints(constraints)
    .build()

WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "sync", ExistingPeriodicWorkPolicy.KEEP, workRequest
)
```

**Foreground Service**
```kotlin
// Short service for quick tasks
class QuickTaskService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(1, notification)

        // Do work
        stopSelf()
        return START_NOT_STICKY
    }
}
```

## Follow-ups

- What are the battery optimization implications of each approach?
- How do you handle task cancellation and cleanup?
- What are the differences between WorkManager and JobScheduler?

## References

- [[c-coroutines]]
- https://developer.android.com/develop/background-work/background-tasks

## Related Questions

### Prerequisites (Easier)
- [[q-async-operations-android--android--medium]]
- [[q-android-service-types--android--easy]]
- [[q-android-services-purpose--android--easy]]

### Related (Same Level)
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]
- [[q-android-build-optimization--android--medium]]
- [[q-android-modularization--android--medium]]

