---
id: android-180
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
related: [c-background-tasks, q-api-rate-limiting-throttling--android--medium, q-compose-modifier-system--android--medium, q-databases-android--android--easy]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/background-execution, android/coroutines, android/performance-battery, background-work, difficulty/medium, service, workmanager]

date created: Saturday, November 1st 2025, 12:47:12 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---
# Вопрос (RU)

> Когда использовать WorkManager vs Coroutines vs `Service` для фоновой работы в Android?

# Question (EN)

> When should you use WorkManager vs Coroutines vs `Service` for background work in Android?

---

## Ответ (RU)

**WorkManager**, **Coroutines** и **`Service`** решают разные задачи фоновой работы в Android.

### Критерии Выбора

| Критерий | WorkManager | Coroutines | Foreground `Service` |
|----------|-------------|------------|---------------------|
| **Гарантия выполнения** | Высокая надёжность, переживает reboot и рестарты процесса (но не 100%) | Нет, живут только в процессе | Пока сервис активен и не убит системой, при соблюдении ограничений |
| **Работает при закрытом приложении** | Да, при корректной конфигурации и ограничениях системы | Нет | Да, если запущен как foreground и соблюдены ограничения запуска |
| **Constraints** (WiFi, charging) | Да | Нет | Нет |
| **Retry/backoff** | Встроенная поддержка | Вручную | Вручную |
| **Периодические задачи** | Да (минимальный интервал 15 мин, неточная) | Нет надёжных при убийстве процесса | Только вручную, без гарантий |
| **Use case** | Отложенная, надёжная, совместимая с ограничениями система работа | Async операции в UI и в рамках жизни процесса | Длительные операции с явным уведомлением |

### WorkManager

**Когда использовать**: загрузка файлов, синхронизация данных, аналитика, очистка кэша, периодические задачи c интервалом ≥ 15 мин, любая отложенная работа, которая должна по возможности выполниться даже при закрытии приложения.

**Гарантии**: повышенная надёжность — задачи планируются через системные механизмы, могут выполняться даже если приложение закрыто, переживают reboot устройства и перезапуск процесса приложения, поддерживают автоматический retry и backoff, оптимизируют батарею (учитывают Doze Mode и App Standby). Это не контракт «100% гарантированного выполнения», но значительно надёжнее решений, завязанных только на процесс.

```kotlin
// Загрузка с constraints и retry
class UploadWorker(context: Context, params: WorkerParameters) :
    CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val fileUri = inputData.getString("file_uri") ?: return Result.failure()

        return try {
            uploadFile(fileUri)  // ✅ Планируется системой, может завершиться даже если UI закрыт
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry()  // ✅ Повтор с backoff по правилам WorkManager
            } else {
                Result.failure()
            }
        }
    }
}

fun scheduleUpload(context: Context, fileUri: String) {
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

    // ✅ Используем applicationContext, чтобы не протекал Activity/Fragment
    WorkManager.getInstance(context.applicationContext).enqueue(uploadRequest)
}
```

### Coroutines

**Когда использовать**: загрузка данных для UI, network-запросы для экрана, database-операции, `Flow`-based real-time данные, любая работа, привязанная к lifecycle компонента или живущая в пределах процесса.

**Ограничения**: отменяются при закрытии приложения или уничтожении владельца scope, не переживут process death, нет встроенного долговременного планирования и системных гарантий.

```kotlin
class ProductsViewModel(private val repository: ProductsRepository) : ViewModel() {

    // ✅ Загрузка данных для UI в рамках жизни ViewModel
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

    // ✅ Параллельные запросы в одном scope
    suspend fun loadDashboard() = coroutineScope {
        val products = async { repository.getProducts() }
        val orders = async { repository.getOrders() }

        DashboardData(products.await(), orders.await())
    }
}
```

### Foreground `Service`

**Когда использовать**: music/audio player, отслеживание геолокации, фитнес-трекинг, VoIP-звонки, активные загрузки с явным прогрессом — когда работа длительная, критичная и пользователь должен видеть уведомление.

**Требования**: ОБЯЗАТЕЛЬНО показывать постоянное notification через `startForeground` в установленный срок, пользователь видит, что приложение выполняет работу. Может продолжать работу при свернутом UI, но с Android 8+ и новее действуют строгие ограничения на запуск сервисов в фоне — нужно соблюдать актуальные правила платформы.

```kotlin
class MusicPlayerService : Service() {

    override fun onCreate() {
        super.onCreate()
        // Для Android O+ необходимо создать notification channel до вызова startForeground
        startForeground(NOTIFICATION_ID, createNotification())  // ✅ Обязательно для foreground
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

### Примеры Сравнения

#### Загрузка Файла

```kotlin
// ⚠️ Не подходит для надёжной фоновой загрузки - Coroutines
// Завершится только пока жив ViewModel/процесс. Использовать, если
// пользователю не обещана гарантия завершения после выхода из приложения.
fun uploadFile(file: File) {
    viewModelScope.launch {
        uploadToServer(file)
    }
}

// ✅ Правильно для гарантированной отложенной загрузки - WorkManager
fun uploadFileWithRetry(context: Context, file: File) {
    val uploadWork = OneTimeWorkRequestBuilder<UploadWorker>()
        .setInputData(workDataOf("file_path" to file.path))
        .setConstraints(
            Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()
        )
        .build()

    WorkManager.getInstance(context.applicationContext).enqueue(uploadWork)
}
```

#### Периодическая Синхронизация

```kotlin
// ⚠️ Недостаточно надёжно - Coroutines в ViewModel/процессе
// Работает только пока жив процесс/owner; при закрытии приложения цикл остановится.
fun startSync() {
    viewModelScope.launch {
        while (isActive) {
            syncData()
            delay(3600_000)  // Каждый час пока приложение активно
        }
    }
}

// ✅ Правильно для долгосрочной периодической задачи - WorkManager
// Минимальный интервал 15 минут, фактическое время запуска может быть неточным.
fun schedulePeriodicSync(context: Context) {
    val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS)
        .setConstraints(
            Constraints.Builder()
                .setRequiredNetworkType(NetworkType.UNMETERED)  // WiFi only
                .setRequiresBatteryNotLow(true)
                .build()
        )
        .build()

    WorkManager.getInstance(context.applicationContext).enqueueUniquePeriodicWork(
        "data_sync",
        ExistingPeriodicWorkPolicy.KEEP,
        syncWork
    )
}
```

### Комбинирование Подходов

```kotlin
class DataSyncManager(
    private val context: Context,
    private val repository: DataRepository
) {
    // Немедленная синхронизация в рамках процесса - Coroutines
    suspend fun syncNow() {
        withContext(Dispatchers.IO) {
            val data = fetchFromServer()
            repository.save(data)
        }
    }

    // Отложенная синхронизация с повышенной надёжностью - WorkManager
    fun scheduleSyncWhenOnline() {
        val syncWork = OneTimeWorkRequestBuilder<SyncWorker>()
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build()
            )
            .build()

        WorkManager.getInstance(context.applicationContext).enqueue(syncWork)
    }
}
```

### Decision Tree

```text
Нужна ли повышенная гарантия выполнения после закрытия приложения / перезапуска процесса?
 ДА: Можно отложить выполнение?
    ДА: WorkManager
    НЕТ: Пользователь должен видеть уведомление и работа действительно foreground?
        ДА: Foreground Service (соблюдая ограничения платформы)
        НЕТ: Рассмотреть WorkManager с Expedited Work (ограниченный ресурс)

 НЕТ: Нужен немедленный результат для UI в рамках текущей сессии?
     ДА: Coroutines (viewModelScope/lifecycleScope)
     НЕТ: Периодическая работа?
         ДА (< 15 min): Coroutines с delay, пока ожидается, что процесс активен
         ДА (≥ 15 min): WorkManager Periodic
```

## Answer (EN)

**WorkManager**, **Coroutines**, and **Services** solve different background work needs in Android.

### Selection Criteria

| Criterion | WorkManager | Coroutines | Foreground `Service` |
|----------|-------------|------------|---------------------|
| **Execution Guarantee** | High reliability, survives reboot/process restarts (not 100%) | No, tied to process/scope | While service is running and not killed, subject to platform limits |
| **Works When App Closed** | Yes, when properly configured and allowed by system | No | Yes when started as foreground and launch restrictions are met |
| **Constraints** (WiFi, charging) | Yes | No | No |
| **Retry/backoff** | Built-in support | Manual | Manual |
| **Periodic Tasks** | Yes (min 15 min interval, inexact) | No durable periodic tasks across process death | Manual, no strong guarantees |
| **Use Case** | Deferrable, reliable, system-cooperative work | Async work for UI / within app lifetime | `Long`-running user-visible foreground work |

### WorkManager

**When to use**: file uploads, data synchronization, analytics, cache cleanup, periodic work with interval ≥ 15 min, any deferrable work that should best-effort complete even if the app is closed.

**Guarantees**: increased reliability — uses system schedulers; work can run even if the app UI is closed, survives device reboot and process recreation, supports automatic retry/backoff, and is battery-aware (respects Doze Mode and App Standby). This is not a strict "100% will run" guarantee, but much stronger than in-process-only approaches.

```kotlin
// Upload with constraints and retry
class UploadWorker(context: Context, params: WorkerParameters) :
    CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val fileUri = inputData.getString("file_uri") ?: return Result.failure()

        return try {
            uploadFile(fileUri)  // ✅ Scheduled via WorkManager; can complete even if UI is closed
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry()  // ✅ Retries with configured backoff
            } else {
                Result.failure()
            }
        }
    }
}

fun scheduleUpload(context: Context, fileUri: String) {
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

    // ✅ Use applicationContext to avoid leaking UI contexts
    WorkManager.getInstance(context.applicationContext).enqueue(uploadRequest)
}
```

### Coroutines

**When to use**: UI data loading, screen-specific network requests, database operations, `Flow`-based real-time updates, any work bound to lifecycle or that only needs to run while the app/process is alive.

**Limitations**: cancelled when the app or owning scope is destroyed, do not survive process death, no built-in durable scheduling or system-level guarantees.

```kotlin
class ProductsViewModel(private val repository: ProductsRepository) : ViewModel() {

    // ✅ Load data for UI within ViewModel lifetime
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

    // ✅ Parallel requests within the same scope
    suspend fun loadDashboard() = coroutineScope {
        val products = async { repository.getProducts() }
        val orders = async { repository.getOrders() }

        DashboardData(products.await(), orders.await())
    }
}
```

### Foreground `Service`

**When to use**: music/audio playback, location tracking, fitness tracking, VoIP calls, active downloads with visible progress — long-running, high-priority work that must remain active and visible to the user.

**Requirements**: MUST show an ongoing notification via `startForeground` within the allowed time; user must see that the app is doing work. Can continue when the UI is closed, but from Android 8+ there are strict background execution and foreground service start limits — implementations must follow current platform rules.

```kotlin
class MusicPlayerService : Service() {

    override fun onCreate() {
        super.onCreate()
        // For Android O+ you must create a notification channel before startForeground
        startForeground(NOTIFICATION_ID, createNotification())  // ✅ Required for foreground
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
// ⚠️ Not suitable for reliable background upload - Coroutines
// Runs only while ViewModel/process is alive. Fine when no guarantee beyond session is needed.
fun uploadFile(file: File) {
    viewModelScope.launch {
        uploadToServer(file)
    }
}

// ✅ Correct for deferred, more reliable upload - WorkManager
fun uploadFileWithRetry(context: Context, file: File) {
    val uploadWork = OneTimeWorkRequestBuilder<UploadWorker>()
        .setInputData(workDataOf("file_path" to file.path))
        .setConstraints(
            Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()
        )
        .build()

    WorkManager.getInstance(context.applicationContext).enqueue(uploadWork)
}
```

#### Periodic Synchronization

```kotlin
// ⚠️ Not durable - Coroutines loop in ViewModel/process
// Works only while process/owner is alive; stops when app is closed.
fun startSync() {
    viewModelScope.launch {
        while (isActive) {
            syncData()
            delay(3600_000)  // Every hour while app is active
        }
    }
}

// ✅ Appropriate for long-term periodic sync - WorkManager
// Minimum interval is 15 minutes; actual execution time is inexact.
fun schedulePeriodicSync(context: Context) {
    val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS)
        .setConstraints(
            Constraints.Builder()
                .setRequiredNetworkType(NetworkType.UNMETERED)  // WiFi only
                .setRequiresBatteryNotLow(true)
                .build()
        )
        .build()

    WorkManager.getInstance(context.applicationContext).enqueueUniquePeriodicWork(
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
    // Immediate sync within process lifetime - Coroutines
    suspend fun syncNow() {
        withContext(Dispatchers.IO) {
            val data = fetchFromServer()
            repository.save(data)
        }
    }

    // Deferred sync with higher reliability - WorkManager
    fun scheduleSyncWhenOnline() {
        val syncWork = OneTimeWorkRequestBuilder<SyncWorker>()
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build()
            )
            .build()

        WorkManager.getInstance(context.applicationContext).enqueue(syncWork)
    }
}
```

### Decision Tree

```text
Need higher reliability beyond app/process lifetime (including after app close/restart)?
 YES: Can execution be deferred?
    YES: WorkManager
    NO: Must the user see an ongoing notification and is it truly foreground work?
        YES: Foreground Service (respect platform limits)
        NO: Consider WorkManager with Expedited Work (limited resource)

 NO: Need immediate result for current UI/session only?
     YES: Coroutines (viewModelScope/lifecycleScope)
     NO: Periodic work?
         YES (< 15 min): Coroutines with delay, only while process is expected alive
         YES (≥ 15 min): WorkManager Periodic
```

---

## Follow-ups

1. How does WorkManager behave under modern background execution limits (Doze, App Standby buckets, restricted apps)?
2. When should you use expedited WorkManager work vs a foreground service, and what quotas apply?
3. How can you observe WorkManager state and progress from UI and handle cancellation safely?
4. What are the differences between `START_STICKY`, `START_NOT_STICKY`, and `START_REDELIVER_INTENT` for services and how do they affect reliability?
5. How would you migrate legacy `JobScheduler` or `AlarmManager`-based background tasks to WorkManager?

## References

- [WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Background work overview](https://developer.android.com/develop/background-work/background-tasks)
- [Foreground services](https://developer.android.com/develop/background-work/services/foreground-services)
- [[c-background-tasks]]


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
