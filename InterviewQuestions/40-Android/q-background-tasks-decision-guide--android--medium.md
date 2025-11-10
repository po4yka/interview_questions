---
id: android-006
title: Background Tasks Decision Guide / Руководство по фоновым задачам
aliases: [Background Tasks Decision Guide, Руководство по фоновым задачам]
topic: android
subtopics:
  - background-execution
  - coroutines
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
  - c-coroutines
  - c-service
  - q-async-operations-android--android--medium
  - q-foreground-service-types--android--medium
  - q-what-is-workmanager--android--medium
sources: []
created: 2025-10-05
updated: 2025-10-30
tags: [android/background-execution, android/coroutines, android/service, difficulty/medium]
---

# Вопрос (RU)
> Как выбрать правильный способ выполнения фоновых задач в Android?

---

# Question (EN)
> How to choose the right approach for background tasks in Android?

---

## Ответ (RU)

**Подход**: Выбор механизма определяется тремя критериями — необходимость продолжения после закрытия UI, возможность отложенного выполнения, критичность немедленного старта.

**Дерево решений**:

```mermaid
flowchart TD
    Start[Нужно продолжать в фоне?] -->|НЕТ| Coroutines[Coroutines<br/>viewModelScope/lifecycleScope]
    Start -->|ДА| Deferrable[Можно отложить?]
    Deferrable -->|ДА| WorkManager[WorkManager]
    Deferrable -->|НЕТ| SpecializedAPI[Есть специализированный API?]
    SpecializedAPI -->|ДА| Specialized[MediaSession / Location API]
    SpecializedAPI -->|НЕТ| ShortTask[Короткая задача <3 мин?]
    ShortTask -->|ДА| ShortService[ShortService]
    ShortTask -->|НЕТ| ForegroundService[Regular Foreground Service]
```

**Категории**:

**1. Coroutines (lifecycle-aware)**
- Автоматическая отмена при уничтожении scope
- Применение: загрузка данных UI, вычисления для экрана

**2. WorkManager (отложенные задачи)**
- Гарантированное выполнение с учетом ограничений системы (сеть, батарея, Doze Mode)
- Применение: синхронизация, периодические загрузки, очистка кэша

**3. Foreground Services (немедленное выполнение)**
- Обязательное уведомление и строгие ограничения типов
- Применение: медиа, навигация, отслеживание активности

**Код**:

```kotlin
// ✅ Coroutines: автоматическая отмена
viewModelScope.launch {
    val result = withContext(Dispatchers.IO) {
        repository.fetchData()
    }
    _uiState.value = result
}
// ⚠️ GlobalScope живет дольше, чем lifecycle-компоненты, что может привести к утечкам и крашам — избегайте для UI-заданий

// ✅ WorkManager: отложенная задача с ограничениями
val syncWork = OneTimeWorkRequestBuilder<SyncWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.UNMETERED)
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 10, TimeUnit.SECONDS)
    .build()
WorkManager.getInstance(context).enqueue(syncWork)

// ✅ ShortService: критичная задача <3 мин (на поддерживаемых API)
class FileTransferService : LifecycleService() {
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
// ⚠️ Обычный Service без foreground-статуса для долгих задач имеет повышенный риск быть убитым системой (особенно в фоне) и не должен использоваться для продолжительных операций
```

**Ключевые моменты**:
- **Coroutines**: используйте структурированные scope (`viewModelScope`, `lifecycleScope`) для автоотмены
- **WorkManager**: гарантирует выполнение даже после перезагрузки устройства, соблюдает Doze Mode
- **ShortService**: требует тип `FOREGROUND_SERVICE_TYPE_SHORT_SERVICE`, доступный на современных версиях Android, и завершение в пределах лимита (~3 минут)
- **Избегайте**: обычных Service без foreground режима для продолжительных задач; они нестабильны и подвержены убийству системой

---

## Answer (EN)

**Approach**: Selection is driven by three criteria — background continuation requirement, deferability, and criticality of immediate start.

**Decision tree**:

```mermaid
flowchart TD
    Start[Need background continuation?] -->|NO| Coroutines[Coroutines<br/>viewModelScope/lifecycleScope]
    Start -->|YES| Deferrable[Can be deferred?]
    Deferrable -->|YES| WorkManager[WorkManager]
    Deferrable -->|NO| SpecializedAPI[Specialized API available?]
    SpecializedAPI -->|YES| Specialized[MediaSession / Location API]
    SpecializedAPI -->|NO| ShortTask[Short task <3 min?]
    ShortTask -->|YES| ShortService[ShortService]
    ShortTask -->|NO| ForegroundService[Regular Foreground Service]
```

**Categories**:

**1. Coroutines (lifecycle-aware)**
- Automatic cancellation on scope destruction
- Use cases: UI data loading, screen computations

**2. WorkManager (deferred tasks)**
- Guaranteed execution respecting system constraints (network, battery, Doze Mode)
- Use cases: synchronization, periodic downloads, cache cleanup

**3. Foreground Services (immediate execution)**
- Mandatory notification and strict type restrictions
- Use cases: media playback, navigation, activity tracking

**Code**:

```kotlin
// ✅ Coroutines: automatic cancellation
viewModelScope.launch {
    val result = withContext(Dispatchers.IO) {
        repository.fetchData()
    }
    _uiState.value = result
}
// ⚠️ GlobalScope outlives lifecycle components and can cause leaks/crashes — avoid it for UI-related work

// ✅ WorkManager: deferred task with constraints
val syncWork = OneTimeWorkRequestBuilder<SyncWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.UNMETERED)
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 10, TimeUnit.SECONDS)
    .build()
WorkManager.getInstance(context).enqueue(syncWork)

// ✅ ShortService: critical task <3 min (on supported API levels)
class FileTransferService : LifecycleService() {
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
// ⚠️ A regular Service without foreground status for long-running work is at high risk of being killed by the system (especially in background) and must not be used for long operations
```

**Key points**:
- **Coroutines**: use structured scopes (`viewModelScope`, `lifecycleScope`) for auto-cancellation
- **WorkManager**: guarantees execution even after device reboot, respects Doze Mode
- **ShortService**: requires `FOREGROUND_SERVICE_TYPE_SHORT_SERVICE`, available on modern Android versions, and must finish within the enforced time limit (~3 minutes)
- **Avoid**: using regular Services without foreground mode for long-running tasks; they are unstable and likely to be killed by the system

---

## Follow-ups

- How does Doze Mode affect WorkManager execution timing and constraints?
- What happens to ShortService if execution exceeds 3 minutes timeout?
- When to use ExactAlarmPermission vs WorkManager for time-sensitive operations?
- How to implement graceful degradation when foreground service permission is denied?
- What are the battery implications of using START_STICKY vs START_NOT_STICKY?

## References

- [[c-coroutines]]
- [[c-service]]
- [[c-workmanager]]
- https://developer.android.com/develop/background-work/background-tasks
- [Foreground Services](https://developer.android.com/develop/background-work/services/foreground-services)


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
```
