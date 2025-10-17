---
id: 20251006-000007
title: "How to handle data sync on unstable network? / Как обрабатывать синхронизацию данных при нестабильной сети?"
aliases: []

# Classification
topic: android
subtopics: [networking, offline-first, sync, architecture]
question_kind: design
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-android
related: [offline-first, workmanager, networking, data-persistence]

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [android, networking, sync, offline-first, workmanager, difficulty/hard]
---

# Question (EN)

> How would you handle data synchronization in an Android app with an unstable network connection?

# Вопрос (RU)

> Как бы вы обрабатывали синхронизацию данных в Android приложении при нестабильном сетевом соединении?

---

## Answer (EN)

Handling data synchronization on unstable networks requires offline-first architecture, retry mechanisms, and conflict resolution strategies.

### 1. Offline-First Architecture

**Core Principle:** Local database is the single source of truth.

```kotlin
class OfflineFirstRepository @Inject constructor(
    private val localDataSource: LocalDataSource,
    private val remoteDataSource: RemoteDataSource,
    private val syncQueue: SyncQueue,
    private val networkMonitor: NetworkMonitor
) {
    // Always read from local database
    fun getData(): Flow<List<Data>> {
        return localDataSource.observeData()
    }

    // Write locally first, sync when possible
    suspend fun saveData(data: Data) {
        // 1. Save to local database immediately
        localDataSource.insert(data)

        // 2. Queue for sync
        syncQueue.enqueue(SyncOperation.Create(data))

        // 3. Sync if online
        if (networkMonitor.isOnline()) {
            syncData()
        }
    }

    private suspend fun syncData() {
        syncQueue.getPendingOperations().forEach { operation ->
            try {
                when (operation) {
                    is SyncOperation.Create -> {
                        remoteDataSource.create(operation.data)
                        syncQueue.markAsCompleted(operation.id)
                    }
                    is SyncOperation.Update -> {
                        remoteDataSource.update(operation.data)
                        syncQueue.markAsCompleted(operation.id)
                    }
                    is SyncOperation.Delete -> {
                        remoteDataSource.delete(operation.id)
                        syncQueue.markAsCompleted(operation.id)
                    }
                }
            } catch (e: Exception) {
                handleSyncError(operation, e)
            }
        }
    }
}
```

### 2. Sync Queue with WorkManager

```kotlin
@Entity(tableName = "sync_queue")
data class SyncQueueItem(
    @PrimaryKey val id: String,
    val operation: OperationType,
    val data: String,  // JSON serialized
    val timestamp: Long,
    val retryCount: Int = 0,
    val status: SyncStatus
)

enum class OperationType { CREATE, UPDATE, DELETE }
enum class SyncStatus { PENDING, IN_PROGRESS, COMPLETED, FAILED }

class SyncWorker(
    context: Context,
    params: WorkerParameters,
    private val repository: Repository
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            repository.syncPendingChanges()
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry()  // Exponential backoff
            } else {
                Result.failure()
            }
        }
    }

    companion object {
        fun schedule(workManager: WorkManager) {
            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()

            val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(
                15, TimeUnit.MINUTES
            )
                .setConstraints(constraints)
                .setBackoffCriteria(
                    BackoffPolicy.EXPONENTIAL,
                    WorkRequest.MIN_BACKOFF_MILLIS,
                    TimeUnit.MILLISECONDS
                )
                .build()

            workManager.enqueueUniquePeriodicWork(
                "data_sync",
                ExistingPeriodicWorkPolicy.KEEP,
                syncWork
            )
        }
    }
}
```

### 3. Network Monitoring

```kotlin
class NetworkMonitor @Inject constructor(
    private val context: Context
) {
    private val connectivityManager = context.getSystemService<ConnectivityManager>()

    private val _isOnline = MutableStateFlow(false)
    val isOnline: StateFlow<Boolean> = _isOnline.asStateFlow()

    private val networkCallback = object : ConnectivityManager.NetworkCallback() {
        override fun onAvailable(network: Network) {
            _isOnline.value = true
            triggerSync()
        }

        override fun onLost(network: Network) {
            _isOnline.value = false
        }
    }

    fun startMonitoring() {
        val request = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .build()

        connectivityManager?.registerNetworkCallback(request, networkCallback)
    }

    private fun triggerSync() {
        // Trigger sync when network becomes available
        SyncWorker.schedule(WorkManager.getInstance(context))
    }
}
```

### 4. Conflict Resolution

```kotlin
class ConflictResolver {
    fun resolve(
        local: Data,
        remote: Data
    ): Data {
        return when {
            // Last write wins
            local.timestamp > remote.timestamp -> local

            // Server always wins
            else -> remote

            // Custom merge logic
            // mergeChanges(local, remote)
        }
    }

    private fun mergeChanges(local: Data, remote: Data): Data {
        // Implement field-level merge
        return local.copy(
            field1 = if (local.field1Timestamp > remote.field1Timestamp)
                local.field1 else remote.field1,
            field2 = if (local.field2Timestamp > remote.field2Timestamp)
                local.field2 else remote.field2
        )
    }
}
```

### 5. Retry Mechanism

```kotlin
class RetryInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        var response = chain.proceed(request)
        var tryCount = 0
        val maxRetries = 3

        while (!response.isSuccessful && tryCount < maxRetries) {
            tryCount++

            // Exponential backoff
            val delay = (2.0.pow(tryCount) * 1000).toLong()
            Thread.sleep(delay)

            response.close()
            response = chain.proceed(request)
        }

        return response
    }
}
```

### 6. Pagination for Large Datasets

```kotlin
class PaginatedSyncManager {
    suspend fun syncAllData() {
        var page = 0
        var hasMore = true

        while (hasMore) {
            try {
                val response = apiService.getData(page, PAGE_SIZE)
                localDatabase.insertAll(response.items)

                hasMore = response.hasMore
                page++

                // Save sync state
                preferences.edit {
                    putInt("last_synced_page", page)
                }
            } catch (e: Exception) {
                // Resume from last page on next sync
                break
            }
        }
    }

    companion object {
        const val PAGE_SIZE = 50
    }
}
```

### Best Practices

1. **Local-First**: Always save to local DB first
2. **Queue Operations**: Store failed syncs for retry
3. **Exponential Backoff**: Don't hammer the server
4. **Conflict Resolution**: Have clear rules
5. **Network Monitoring**: Sync when network returns
6. **WorkManager**: For reliable background sync
7. **Partial Sync**: Use pagination for large datasets
8. **Timestamp Everything**: For conflict resolution
9. **Optimistic UI**: Show changes immediately
10. **Sync Indicators**: Show user sync status

### Common Pitfalls

1. Not handling partial syncs
2. Missing conflict resolution strategy
3. Blocking UI during sync
4. Not queuing failed operations
5. Infinite retry loops
6. Not using WorkManager for background work
7. Poor error messaging to users

## Ответ (RU)

Обработка синхронизации данных при нестабильной сети требует offline-first архитектуры, механизмов повторных попыток и стратегий разрешения конфликтов.

### 1. Offline-First архитектура

**Принцип:** Локальная база данных - единственный источник истины.

-   Всегда читать из локальной БД
-   Сначала сохранять локально, затем синхронизировать
-   Ставить операции в очередь при отсутствии сети

### 2. Очередь синхронизации с WorkManager

-   Хранение неотправленных изменений
-   Автоматическая синхронизация при появлении сети
-   Экспоненциальная задержка между попытками
-   Максимум 3 попытки

### 3. Мониторинг сети

-   ConnectivityManager для отслеживания состояния сети
-   Автоматический запуск синхронизации при появлении соединения
-   StateFlow для реактивного обновления UI

### 4. Разрешение конфликтов

**Стратегии:**

-   Last Write Wins (побеждает последняя запись)
-   Server Always Wins (всегда побеждает сервер)
-   Custom Merge (пользовательское слияние)
-   Field-level merge (слияние на уровне полей)

### 5. Механизм повторных попыток

-   Retry Interceptor для OkHttp
-   Экспоненциальная задержка
-   Максимальное количество попыток

### 6. Пагинация для больших данных

-   Синхронизация частями
-   Сохранение прогресса
-   Возобновление с последней страницы

### Лучшие практики:

1. **Local-First**: Всегда сохранять в локальную БД первым делом
2. **Очередь операций**: Хранить неудавшиеся синхронизации
3. **Экспоненциальная задержка**: Не перегружать сервер
4. **Разрешение конфликтов**: Иметь четкие правила
5. **Мониторинг сети**: Синхронизировать при возврате сети
6. **WorkManager**: Для надежной фоновой синхронизации
7. **Частичная синхронизация**: Использовать пагинацию
8. **Временные метки**: Для разрешения конфликтов
9. **Оптимистичный UI**: Показывать изменения сразу
10. **Индикаторы синхронизации**: Показывать пользователю статус

### Частые ошибки:

1. Необработка частичных синхронизаций
2. Отсутствие стратегии разрешения конфликтов
3. Блокировка UI во время синхронизации
4. Неочереживание неудавшихся операций
5. Бесконечные циклы повторов
6. Неиспользование WorkManager для фоновой работы

---

## References

-   [Offline-First Architecture](https://developer.android.com/topic/architecture/data-layer/offline-first)
-   [WorkManager Guide](https://developer.android.com/topic/libraries/architecture/workmanager)
-   [Network Connectivity](https://developer.android.com/training/monitoring-device-state/connectivity-status-type)
-   [Room Database](https://developer.android.com/training/data-storage/room)

## Related Questions
