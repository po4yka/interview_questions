---
id: android-440
title: Data Sync Unstable Network / Синхронизация данных при нестабильной сети
aliases: [Data Sync Unstable Network, Синхронизация данных при нестабильной сети]
topic: android
subtopics:
  - architecture-clean
  - networking-http
question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-coroutines
  - c-workmanager
  - q-offline-first-architecture--android--hard
created: 2025-10-20
updated: 2025-11-02
tags: [android/architecture-clean, android/networking-http, data-sync, difficulty/hard, networking, offline-first, workmanager]
sources:
  - https://developer.android.com/guide/background/processing-data/sync
---

# Вопрос (RU)
> Как бы вы обрабатывали синхронизацию данных в Android приложении при нестабильном сетевом соединении?

# Question (EN)
> How would you handle data synchronization in an Android app with an unstable network connection?

## Ответ (RU)

Синхронизация данных при нестабильной сети требует `offline-first` архитектуры, механизмов повторных попыток с экспоненциальной задержкой и стратегий разрешения конфликтов. Основная цель — обеспечить отзывчивость UI и надежность синхронизации независимо от состояния сети.

### Ключевые Принципы

**Offline-First архитектура:**
- Локальная база данных (`Room`/SQLite) как единственный источник истины — всегда доступна
- Все операции выполняются локально первыми — мгновенный отклик UI
- Синхронизация происходит асинхронно в фоновом режиме — не блокирует пользователя
- Пользователь всегда видит актуальные локальные данные — даже без сети

**Основные компоненты:**
- `Repository Pattern` для абстракции источников данных — единый интерфейс для local/remote
- `WorkManager` для надежного фонового выполнения — автоматические retry и constraints
- `Coroutines` для асинхронных операций — неблокирующее выполнение
- Механизмы retry с экспоненциальной задержкой — уменьшение нагрузки на сервер
- Стратегии разрешения конфликтов — `Last Write Wins`, `Merge`, `Local Wins`, `Remote Wins`

### Реализация

**1. Offline-First Repository:**
```kotlin
class DataRepository @Inject constructor(
    private val localDb: LocalDataSource,
    private val remoteApi: RemoteDataSource,
    private val syncManager: SyncManager
) {
    suspend fun saveUser(user: User): Result<User> {
        // ✅ Сохраняем локально первым для мгновенного отклика UI
        val saved = localDb.saveUser(user)
        syncManager.scheduleSync(user.id)
        return Result.success(saved)
    }

    // ❌ НЕ ждем сеть перед возвратом данных
    suspend fun getUser(id: String): User = localDb.getUser(id)
}
```

**2. Retry с экспоненциальной задержкой:**
```kotlin
class RetryManager {
    suspend fun <T> executeWithRetry(operation: suspend () -> T): Result<T> {
        repeat(3) { attempt ->
            try {
                return Result.success(operation())
            } catch (e: Exception) {
                // ✅ Экспоненциальная задержка с jitter предотвращает thundering herd
                if (attempt < 2) {
                    delay(1000L * (1L shl attempt) + (0..1000).random())
                }
            }
        }
        return Result.failure(Exception("Max retries exceeded"))
    }
}
```

**3. Разрешение конфликтов:**
```kotlin
class ConflictResolver {
    fun resolve(local: User, remote: User, strategy: Strategy): User {
        return when (strategy) {
            // ✅ Last Write Wins — простейшая стратегия (по timestamp)
            Strategy.LAST_WRITE_WINS ->
                if (remote.lastModified > local.lastModified) remote else local
            // ✅ Merge — объединение изменений по полям (интеллектуальное слияние)
            Strategy.MERGE ->
                User(local.id, remote.name, local.email,
                     maxOf(local.lastModified, remote.lastModified))
            Strategy.LOCAL_WINS -> local  // Локальные изменения имеют приоритет
            Strategy.REMOTE_WINS -> remote  // Удаленные изменения имеют приоритет
        }
    }
}
```

**4. Фоновая синхронизация с WorkManager:**
```kotlin
class SyncWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            SyncManager(applicationContext).performSync()
            Result.success()
        } catch (e: Exception) {
            // ✅ Автоматический retry при ошибке (до 3 попыток)
            if (runAttemptCount < 3) Result.retry() else Result.failure()
        }
    }
}

class SyncManager @Inject constructor(private val context: Context) {
    fun scheduleSync(userId: String) {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)  // ✅ Ждем доступность сети
            .build()
        val request = OneTimeWorkRequestBuilder<SyncWorker>()
            .setConstraints(constraints)
            .build()
        WorkManager.getInstance(context).enqueue(request)
    }
}
```

**5. Мониторинг состояния сети:**
```kotlin
class NetworkMonitor @Inject constructor(private val context: Context) {
    private val connectivityManager = context.getSystemService<ConnectivityManager>()

    fun observeNetworkState(): Flow<Boolean> = callbackFlow {
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) = trySend(true)
            override fun onLost(network: Network) = trySend(false)
        }
        connectivityManager?.registerDefaultNetworkCallback(callback)
        awaitClose { connectivityManager?.unregisterNetworkCallback(callback) }
    }
}
```

## Answer (EN)

Handling data synchronization on unstable networks requires `offline-first` architecture, retry mechanisms with exponential backoff, and conflict resolution strategies. Main goal: ensure UI responsiveness and sync reliability regardless of network state.

### Key Principles

**Offline-First Architecture:**
- Local database (`Room`/SQLite) as single source of truth — always available
- All operations performed locally first — instant UI response
- Synchronization happens asynchronously in background — doesn't block user
- User always sees current local data — even without network

**Core Components:**
- `Repository Pattern` for data source abstraction — unified interface for local/remote
- `WorkManager` for reliable background execution — automatic retry and constraints
- `Coroutines` for asynchronous operations — non-blocking execution
- Retry mechanisms with exponential backoff — reduce server load
- Conflict resolution strategies — `Last Write Wins`, `Merge`, `Local Wins`, `Remote Wins`

### Implementation

**1. Offline-First Repository:**
```kotlin
class DataRepository @Inject constructor(
    private val localDb: LocalDataSource,
    private val remoteApi: RemoteDataSource,
    private val syncManager: SyncManager
) {
    suspend fun saveUser(user: User): Result<User> {
        // ✅ Сохраняем локально первым для мгновенного отклика UI
        val saved = localDb.saveUser(user)
        syncManager.scheduleSync(user.id)
        return Result.success(saved)
    }

    // ❌ НЕ ждем сеть перед возвратом данных
    suspend fun getUser(id: String): User = localDb.getUser(id)
}
```

**2. Retry with exponential backoff:**
```kotlin
class RetryManager {
    suspend fun <T> executeWithRetry(operation: suspend () -> T): Result<T> {
        repeat(3) { attempt ->
            try {
                return Result.success(operation())
            } catch (e: Exception) {
                // ✅ Exponential backoff with jitter prevents thundering herd
                if (attempt < 2) {
                    delay(1000L * (1L shl attempt) + (0..1000).random())
                }
            }
        }
        return Result.failure(Exception("Max retries exceeded"))
    }
}
```

**3. Conflict Resolution:**
```kotlin
class ConflictResolver {
    fun resolve(local: User, remote: User, strategy: Strategy): User {
        return when (strategy) {
            // ✅ Last Write Wins — simplest strategy (by timestamp)
            Strategy.LAST_WRITE_WINS ->
                if (remote.lastModified > local.lastModified) remote else local
            // ✅ Merge — combine changes by fields (intelligent merging)
            Strategy.MERGE ->
                User(local.id, remote.name, local.email,
                     maxOf(local.lastModified, remote.lastModified))
            Strategy.LOCAL_WINS -> local  // Local changes have priority
            Strategy.REMOTE_WINS -> remote  // Remote changes have priority
        }
    }
}
```

**4. Background sync with WorkManager:**
```kotlin
class SyncWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            SyncManager(applicationContext).performSync()
            Result.success()
        } catch (e: Exception) {
            // ✅ Automatic retry on failure
            if (runAttemptCount < 3) Result.retry() else Result.failure()
        }
    }
}

class SyncManager @Inject constructor(private val context: Context) {
    fun scheduleSync(userId: String) {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)  // ✅ Wait for network
            .build()
        val request = OneTimeWorkRequestBuilder<SyncWorker>()
            .setConstraints(constraints)
            .build()
        WorkManager.getInstance(context).enqueue(request)
    }
}
```

**5. Network state monitoring:**
```kotlin
class NetworkMonitor @Inject constructor(private val context: Context) {
    private val connectivityManager = context.getSystemService<ConnectivityManager>()

    fun observeNetworkState(): Flow<Boolean> = callbackFlow {
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) = trySend(true)
            override fun onLost(network: Network) = trySend(false)
        }
        connectivityManager?.registerDefaultNetworkCallback(callback)
        awaitClose { connectivityManager?.unregisterNetworkCallback(callback) }
    }
}
```


## Follow-ups

- How would you implement `CRDTs` (Conflict-free Replicated Data Types) for automatic conflict resolution?
- What are the trade-offs between optimistic and pessimistic locking in distributed sync?
- How would you handle partial sync failures and maintain data consistency?
- How would you implement sync batching to reduce network overhead?
- What strategies would you use for conflict resolution when merging incompatible field changes?
- How to implement sync priority queues for critical vs non-critical data?

## References

- [[c-workmanager]] - Background task scheduling
- [[c-coroutines]] - Asynchronous programming primitives
- Android Data Sync Guide: https://developer.android.com/guide/background/processing-data/sync

## Related Questions

### Prerequisites (Easier)
- `WorkManager` basics and constraints configuration
- Local database implementation with `Room` or SQLite
- Basic understanding of `Coroutines` and `Flow`

### Related (Same Level)
- [[q-offline-first-architecture--android--hard]]
- `Repository Pattern` implementation
- Network state monitoring

### Advanced (Harder)
- Implementing operational transformation for real-time collaboration
- Building distributed consensus algorithms for multi-node sync
- `CRDTs` for automatic conflict resolution
