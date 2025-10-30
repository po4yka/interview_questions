---
id: 20251017-144931
title: "WorkManager Decision Guide / Руководство по выбору WorkManager"
aliases: ["WorkManager Decision Guide", "Руководство по выбору WorkManager"]
topic: android
subtopics: [background-execution, coroutines, performance-battery]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-api-rate-limiting-throttling--android--medium, q-compose-modifier-system--android--medium, q-databases-android--android--easy]
created: 2025-10-15
updated: 2025-10-29
sources: []
tags: [android/background-execution, android/coroutines, android/performance-battery, workmanager, background-work, service, difficulty/medium]
---

# Вопрос (RU)

Когда использовать WorkManager vs Coroutines vs Service для фоновой работы в Android?

# Question (EN)

When should you use WorkManager vs Coroutines vs Service for background work in Android?

---

## Ответ (RU)

**WorkManager**, **Coroutines** и **Service** решают разные задачи фоновой работы в Android.

### Критерии выбора

| Критерий | WorkManager | Coroutines | Foreground Service |
|----------|-------------|------------|---------------------|
| **Гарантия выполнения** | Да, даже после reboot | Нет | Пока процесс жив |
| **Работает при закрытом приложении** | Да | Нет | Foreground - да |
| **Constraints** (WiFi, charging) | Да | Нет | Нет |
| **Retry/backoff** | Автоматически | Вручную | Вручную |
| **Периодические задачи** | Да (min 15 min) | Нет | Вручную |
| **Use case** | Deferrable гарантированная работа | Async операции в UI | Long-running foreground |

### WorkManager

**Когда использовать**: загрузка файлов, синхронизация данных, аналитика, очистка кэша, периодические задачи >= 15 мин.

**Гарантии**: выполнится даже если приложение закрыто, переживет reboot, автоматический retry, battery-эффективность (соблюдает Doze Mode).

```kotlin
// Загрузка с constraints и retry
class UploadWorker(context: Context, params: WorkerParameters) :
    CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val fileUri = inputData.getString("file_uri") ?: return Result.failure()

        return try {
            uploadFile(fileUri)  // ✅ Выполнится даже если приложение закрыто
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry()  // ✅ Автоматический retry
            } else {
                Result.failure()
            }
        }
    }
}

fun scheduleUpload(fileUri: String) {
    val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>()
        .setInputData(workDataOf("file_uri" to fileUri))
        .setConstraints(
            Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .setRequiresBatteryNotLow(true)
                .build()
        )
        .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.SECONDS)
        .build()

    WorkManager.getInstance(context).enqueue(uploadRequest)
}
```

### Coroutines

**Когда использовать**: загрузка данных для UI, network запросы для экрана, database операции, Flow-based real-time данных, любая работа привязанная к lifecycle компонента.

**Ограничения**: отменяются при закрытии приложения, не переживут process death, нет retry/backoff из коробки.

```kotlin
class ProductsViewModel(private val repository: ProductsRepository) : ViewModel() {

    // ✅ Загрузка данных для UI
    fun loadProducts() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val products = repository.getProducts()
                _products.value = products
            } catch (e: Exception) {
                _error.value = e.message
            } finally {
                _isLoading.value = false
            }
        }
    }

    // ✅ Параллельные запросы
    suspend fun loadDashboard() = coroutineScope {
        val products = async { repository.getProducts() }
        val orders = async { repository.getOrders() }

        DashboardData(products.await(), orders.await())
    }
}
```

### Foreground Service

**Когда использовать**: music/audio player, location tracking, fitness tracking, VoIP calls, active downloads с прогрессом.

**Требования**: ОБЯЗАТЕЛЬНО показывать notification, пользователь видит что приложение работает, может работать при закрытом приложении.

```kotlin
class MusicPlayerService : Service() {

    override fun onCreate() {
        super.onCreate()
        startForeground(NOTIFICATION_ID, createNotification())  // ✅ Обязательно
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_PLAY -> play()
            ACTION_PAUSE -> pause()
            ACTION_STOP -> stopSelf()
        }
        return START_STICKY
    }
}
```

### Примеры сравнения

#### Загрузка файла

```kotlin
// ❌ НЕПРАВИЛЬНО - Coroutines (отменится при закрытии приложения)
fun uploadFile(file: File) {
    viewModelScope.launch {
        uploadToServer(file)  // Может не завершиться!
    }
}

// ✅ ПРАВИЛЬНО - WorkManager (гарантия завершения)
fun uploadFile(file: File) {
    val uploadWork = OneTimeWorkRequestBuilder<UploadWorker>()
        .setInputData(workDataOf("file_path" to file.path))
        .setConstraints(
            Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()
        )
        .build()

    WorkManager.getInstance(context).enqueue(uploadWork)
}
```

#### Периодическая синхронизация

```kotlin
// ❌ НЕПРАВИЛЬНО - Coroutines (убьется при закрытии приложения)
fun startSync() {
    viewModelScope.launch {
        while (isActive) {
            syncData()
            delay(3600_000)  // Каждый час
        }
    }
}

// ✅ ПРАВИЛЬНО - WorkManager (минимум 15 минут!)
fun schedulePeriodicSync() {
    val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS)
        .setConstraints(
            Constraints.Builder()
                .setRequiredNetworkType(NetworkType.UNMETERED)  // WiFi only
                .setRequiresBatteryNotLow(true)
                .build()
        )
        .build()

    WorkManager.getInstance(context).enqueueUniquePeriodicWork(
        "data_sync",
        ExistingPeriodicWorkPolicy.KEEP,
        syncWork
    )
}
```

### Комбинирование подходов

```kotlin
class DataSyncManager(
    private val context: Context,
    private val repository: DataRepository
) {
    // Немедленная синхронизация - Coroutines
    suspend fun syncNow() {
        withContext(Dispatchers.IO) {
            val data = fetchFromServer()
            repository.save(data)
        }
    }

    // Отложенная гарантированная синхронизация - WorkManager
    fun scheduleSyncWhenOnline() {
        val syncWork = OneTimeWorkRequestBuilder<SyncWorker>()
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build()
            )
            .build()

        WorkManager.getInstance(context).enqueue(syncWork)
    }
}
```

### Decision Tree

```
Нужна ли гарантия выполнения после закрытия приложения?
 ДА: Можно отложить выполнение?
    ДА: WorkManager
    НЕТ: Пользователь должен видеть уведомление?
        ДА: Foreground Service
        НЕТ: WorkManager с Expedited Work

 НЕТ: Нужен немедленный результат для UI?
     ДА: Coroutines (viewModelScope/lifecycleScope)
     НЕТ: Периодическая работа?
         ДА (< 15 min): Coroutines с delay
         ДА (≥ 15 min): WorkManager Periodic
```

## Answer (EN)

**WorkManager**, **Coroutines**, and **Services** solve different background work needs in Android.

### Selection Criteria

| Criterion | WorkManager | Coroutines | Foreground Service |
|----------|-------------|------------|---------------------|
| **Execution Guarantee** | Yes, even after reboot | No | While process alive |
| **Works When App Closed** | Yes | No | Foreground - yes |
| **Constraints** (WiFi, charging) | Yes | No | No |
| **Retry/backoff** | Automatic | Manual | Manual |
| **Periodic Tasks** | Yes (min 15 min) | No | Manual |
| **Use Case** | Deferrable guaranteed work | Async UI operations | Long-running foreground |

### WorkManager

**When to use**: file uploads, data synchronization, analytics, cache cleanup, periodic tasks >= 15 min.

**Guarantees**: executes even if app closed, survives reboot, automatic retry, battery-efficient (respects Doze Mode).

```kotlin
// Upload with constraints and retry
class UploadWorker(context: Context, params: WorkerParameters) :
    CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val fileUri = inputData.getString("file_uri") ?: return Result.failure()

        return try {
            uploadFile(fileUri)  // ✅ Completes even if app closes
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry()  // ✅ Automatic retry
            } else {
                Result.failure()
            }
        }
    }
}

fun scheduleUpload(fileUri: String) {
    val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>()
        .setInputData(workDataOf("file_uri" to fileUri))
        .setConstraints(
            Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .setRequiresBatteryNotLow(true)
                .build()
        )
        .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.SECONDS)
        .build()

    WorkManager.getInstance(context).enqueue(uploadRequest)
}
```

### Coroutines

**When to use**: UI data loading, network requests for screens, database operations, Flow-based real-time data, any lifecycle-bound work.

**Limitations**: cancelled when app closes, doesn't survive process death, no out-of-the-box retry/backoff.

```kotlin
class ProductsViewModel(private val repository: ProductsRepository) : ViewModel() {

    // ✅ Load data for UI
    fun loadProducts() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val products = repository.getProducts()
                _products.value = products
            } catch (e: Exception) {
                _error.value = e.message
            } finally {
                _isLoading.value = false
            }
        }
    }

    // ✅ Parallel requests
    suspend fun loadDashboard() = coroutineScope {
        val products = async { repository.getProducts() }
        val orders = async { repository.getOrders() }

        DashboardData(products.await(), orders.await())
    }
}
```

### Foreground Service

**When to use**: music/audio player, location tracking, fitness tracking, VoIP calls, active downloads with progress.

**Requirements**: MUST show notification, user sees it's running, can work when app closed.

```kotlin
class MusicPlayerService : Service() {

    override fun onCreate() {
        super.onCreate()
        startForeground(NOTIFICATION_ID, createNotification())  // ✅ Required
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_PLAY -> play()
            ACTION_PAUSE -> pause()
            ACTION_STOP -> stopSelf()
        }
        return START_STICKY
    }
}
```

### Comparison Examples

#### File Upload

```kotlin
// ❌ WRONG - Coroutines (cancelled when app closes)
fun uploadFile(file: File) {
    viewModelScope.launch {
        uploadToServer(file)  // May not complete!
    }
}

// ✅ CORRECT - WorkManager (guaranteed completion)
fun uploadFile(file: File) {
    val uploadWork = OneTimeWorkRequestBuilder<UploadWorker>()
        .setInputData(workDataOf("file_path" to file.path))
        .setConstraints(
            Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()
        )
        .build()

    WorkManager.getInstance(context).enqueue(uploadWork)
}
```

#### Periodic Synchronization

```kotlin
// ❌ WRONG - Coroutines (killed when app closes)
fun startSync() {
    viewModelScope.launch {
        while (isActive) {
            syncData()
            delay(3600_000)  // Every hour
        }
    }
}

// ✅ CORRECT - WorkManager (minimum 15 minutes!)
fun schedulePeriodicSync() {
    val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS)
        .setConstraints(
            Constraints.Builder()
                .setRequiredNetworkType(NetworkType.UNMETERED)  // WiFi only
                .setRequiresBatteryNotLow(true)
                .build()
        )
        .build()

    WorkManager.getInstance(context).enqueueUniquePeriodicWork(
        "data_sync",
        ExistingPeriodicWorkPolicy.KEEP,
        syncWork
    )
}
```

### Combining Approaches

```kotlin
class DataSyncManager(
    private val context: Context,
    private val repository: DataRepository
) {
    // Immediate sync - Coroutines
    suspend fun syncNow() {
        withContext(Dispatchers.IO) {
            val data = fetchFromServer()
            repository.save(data)
        }
    }

    // Delayed guaranteed sync - WorkManager
    fun scheduleSyncWhenOnline() {
        val syncWork = OneTimeWorkRequestBuilder<SyncWorker>()
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build()
            )
            .build()

        WorkManager.getInstance(context).enqueue(syncWork)
    }
}
```

### Decision Tree

```
Need guaranteed execution after app closes?
 YES: Can defer execution?
    YES: WorkManager
    NO: User must see notification?
        YES: Foreground Service
        NO: WorkManager with Expedited Work

 NO: Need immediate UI result?
     YES: Coroutines (viewModelScope/lifecycleScope)
     NO: Periodic work?
         YES (< 15 min): Coroutines with delay
         YES (≥ 15 min): WorkManager Periodic
```

---

## Follow-ups

1. How does WorkManager handle device Doze mode and App Standby buckets?
2. What are Expedited Jobs in WorkManager and when to use them?
3. How to observe WorkManager progress and handle cancellation?
4. What are the differences between START_STICKY, START_NOT_STICKY, and START_REDELIVER_INTENT for Services?
5. How to chain multiple WorkManager tasks with proper error handling?

## References

- [[c-coroutines]]
- [[c-structured-concurrency]]
- https://developer.android.com/topic/libraries/architecture/workmanager
- https://developer.android.com/develop/background-work/background-tasks
- https://developer.android.com/develop/background-work/services/foreground-services

## Related Questions

### Prerequisites (Easier)
- [[q-why-separate-ui-and-business-logic--android--easy]] - Architecture fundamentals
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - Android UI basics
- [[q-databases-android--android--easy]] - Data persistence

### Related (Same Level)
- [[q-api-rate-limiting-throttling--android--medium]] - Network optimization
- [[q-compose-modifier-system--android--medium]] - UI patterns
- [[q-build-optimization-gradle--android--medium]] - Build performance

### Advanced (Harder)
- Design background sync system respecting battery constraints
- Implement reliable file upload queue with retry and progress tracking
- Build offline-first architecture with sync conflict resolution
