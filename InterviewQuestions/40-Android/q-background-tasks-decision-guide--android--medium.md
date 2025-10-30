---
id: 20251012-122786
title: Background Tasks Decision Guide / Руководство по фоновым задачам
aliases: ["Background Tasks Decision Guide", "Руководство по фоновым задачам"]
topic: android
subtopics: [background-execution, coroutines, service]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-what-is-workmanager--android--medium, q-foreground-service-types--android--medium, q-async-operations-android--android--medium, c-coroutines]
sources: []
created: 2025-10-05
updated: 2025-10-29
tags: [android/background-execution, android/coroutines, android/service, difficulty/medium]
---

# Вопрос (RU)
> Как выбрать правильный способ выполнения фоновых задач в Android?

---

# Question (EN)
> How to choose the right approach for background tasks in Android?

---

## Ответ (RU)

**Подход**: Выбор определяется тремя критериями: необходимость продолжения в фоне, возможность отложенного выполнения, критичность задачи.

**Категории фоновых задач**:

1. **Асинхронная работа** (coroutines/threads)
   - Выполнение только при активном приложении
   - Автоматическая отмена при уничтожении lifecycle scope
   - Применение: загрузка данных, вычисления для UI

2. **Отложенные задачи** (WorkManager)
   - Гарантированное выполнение после закрытия приложения
   - Соблюдение системных ограничений (сеть, батарея, Doze Mode)
   - Применение: синхронизация, загрузка контента, очистка кэша

3. **Foreground Services**
   - Немедленное выполнение с обязательным уведомлением
   - Строгие ограничения типов
   - Применение: воспроизведение медиа, навигация, отслеживание тренировки

**Дерево решений**:
```
Нужно продолжать в фоне? → НЕТ → Coroutines
                        ↓ ДА
Можно отложить? → ДА → WorkManager
                ↓ НЕТ
Есть специализированный API? → ДА → MediaSession / Location API
                              ↓ НЕТ
Короткая задача (<3 мин)? → ДА → ShortService
                          ↓ НЕТ
                          → Regular Foreground Service
```

**Код**:

```kotlin
// ✅ Coroutines: lifecycle-aware асинхронность
viewModelScope.launch {
    // ✅ Автоматическая отмена при уничтожении ViewModel
    val result = withContext(Dispatchers.IO) {
        repository.fetchData()
    }
    _uiState.value = result
}

// ❌ Неправильно: GlobalScope живет вечно
GlobalScope.launch { /* ❌ утечка памяти */ }

// ✅ WorkManager: отложенная задача с ограничениями
val syncWork = OneTimeWorkRequestBuilder<SyncWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.UNMETERED) // только Wi-Fi
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 10, TimeUnit.SECONDS)
    .build()
WorkManager.getInstance(context).enqueue(syncWork)

// ✅ ShortService: критичная задача <3 мин
class FileTransferService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        ServiceCompat.startForeground(
            this, NOTIFICATION_ID,
            createNotification(),
            ServiceInfo.FOREGROUND_SERVICE_TYPE_SHORT_SERVICE
        )
        lifecycleScope.launch {
            transferFiles()
            stopSelf()
        }
        return START_NOT_STICKY
    }
}

// ❌ Неправильно: обычный сервис для длительной работы
class BadService : Service() {
    override fun onStartCommand(...): Int {
        // ❌ будет убит системой без foreground статуса
        doLongRunningWork()
        return START_STICKY
    }
}
```

**Ключевые моменты**:
- **Coroutines**: используйте `viewModelScope` / `lifecycleScope` для автоматической отмены
- **WorkManager**: гарантирует выполнение даже после перезагрузки устройства
- **ShortService**: требует тип `FOREGROUND_SERVICE_TYPE_SHORT_SERVICE` и завершение <3 мин
- **Избегайте**: обычных Service без foreground режима для любых задач >1 сек

---

## Answer (EN)

**Approach**: Selection is driven by three criteria: background continuation requirement, deferability, and task criticality.

**Background Task Categories**:

1. **Asynchronous work** (coroutines/threads)
   - Execution only while app is active
   - Automatic cancellation on lifecycle scope destruction
   - Use cases: data loading, UI computations

2. **Deferred tasks** (WorkManager)
   - Guaranteed execution after app termination
   - Respects system constraints (network, battery, Doze Mode)
   - Use cases: synchronization, content downloads, cache cleanup

3. **Foreground Services**
   - Immediate execution with mandatory notification
   - Strict type restrictions
   - Use cases: media playback, navigation, workout tracking

**Decision tree**:
```
Need background continuation? → NO → Coroutines
                             ↓ YES
Can be deferred? → YES → WorkManager
                 ↓ NO
Specialized API available? → YES → MediaSession / Location API
                            ↓ NO
Short task (<3 min)? → YES → ShortService
                     ↓ NO
                     → Regular Foreground Service
```

**Code**:

```kotlin
// ✅ Coroutines: lifecycle-aware asynchronicity
viewModelScope.launch {
    // ✅ Automatic cancellation on ViewModel destruction
    val result = withContext(Dispatchers.IO) {
        repository.fetchData()
    }
    _uiState.value = result
}

// ❌ Wrong: GlobalScope lives forever
GlobalScope.launch { /* ❌ memory leak */ }

// ✅ WorkManager: deferred task with constraints
val syncWork = OneTimeWorkRequestBuilder<SyncWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.UNMETERED) // Wi-Fi only
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 10, TimeUnit.SECONDS)
    .build()
WorkManager.getInstance(context).enqueue(syncWork)

// ✅ ShortService: critical task <3 min
class FileTransferService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        ServiceCompat.startForeground(
            this, NOTIFICATION_ID,
            createNotification(),
            ServiceInfo.FOREGROUND_SERVICE_TYPE_SHORT_SERVICE
        )
        lifecycleScope.launch {
            transferFiles()
            stopSelf()
        }
        return START_NOT_STICKY
    }
}

// ❌ Wrong: regular service for long-running work
class BadService : Service() {
    override fun onStartCommand(...): Int {
        // ❌ will be killed by system without foreground status
        doLongRunningWork()
        return START_STICKY
    }
}
```

**Key points**:
- **Coroutines**: use `viewModelScope` / `lifecycleScope` for automatic cancellation
- **WorkManager**: guarantees execution even after device reboot
- **ShortService**: requires `FOREGROUND_SERVICE_TYPE_SHORT_SERVICE` type and completion <3 min
- **Avoid**: regular Services without foreground mode for any tasks >1 sec

---

## Follow-ups

- How does Doze Mode affect WorkManager and foreground services differently?
- What happens to ShortService if execution exceeds 3 minutes?
- When should you use `ExactAlarmPermission` vs WorkManager for time-sensitive tasks?
- How to implement graceful degradation when foreground service permission is denied?
- What are the implications of using `START_STICKY` vs `START_NOT_STICKY` in services?

## References

- [[c-coroutines]]
- https://developer.android.com/develop/background-work/background-tasks
- https://developer.android.com/develop/background-work/services/foreground-services

## Related Questions

### Prerequisites (Easier)
- [[q-android-service-types--android--easy]]
- [[q-android-services-purpose--android--easy]]
- [[q-what-are-services-for--android--easy]]

### Related (Same Level)
- [[q-what-is-workmanager--android--medium]]
- [[q-foreground-service-types--android--medium]]
- [[q-async-operations-android--android--medium]]
- [[q-workmanager-execution-guarantee--android--medium]]

### Advanced (Harder)
- [[q-service-lifecycle-binding--android--hard]]
- [[q-workmanager-chaining--android--hard]]
