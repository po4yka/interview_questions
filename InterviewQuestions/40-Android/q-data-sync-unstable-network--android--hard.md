---
id: 20251020-200000
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
status: draft
moc: moc-android
related:
  - q-offline-first-architecture--android--hard
  - c-workmanager
  - c-coroutines
created: 2025-10-20
updated: 2025-01-27
tags: [android/architecture-clean, android/networking-http, data-sync, difficulty/hard, networking, offline-first, workmanager]
sources: [https://developer.android.com/guide/background/processing-data/sync]
---
# Вопрос (RU)
> Как бы вы обрабатывали синхронизацию данных в Android приложении при нестабильном сетевом соединении?

# Question (EN)
> How would you handle data synchronization in an Android app with an unstable network connection?

## Ответ (RU)

Синхронизация данных при нестабильной сети требует offline-first архитектуры, механизмов повторных попыток и стратегий разрешения конфликтов.

### Ключевые принципы

**Offline-First архитектура:**
- Локальная база данных как единственный источник истины
- Все операции выполняются локально первыми
- Синхронизация происходит асинхронно в фоновом режиме
- Пользователь всегда видит актуальные локальные данные

**Основные компоненты:**
- Repository Pattern для абстракции источников данных
- [[c-workmanager]] для надежного фонового выполнения
- [[c-coroutines]] для асинхронных операций
- Механизмы retry с экспоненциальной задержкой
- Стратегии разрешения конфликтов

### Реализация

**1. Offline-First Repository:**
```kotlin
class DataRepository @Inject constructor(
    private val localDb: LocalDataSource,
    private val remoteApi: RemoteDataSource,
    private val syncManager: SyncManager
) {
    suspend fun saveUser(user: User): Result<User> {
        // ✅ Save locally first for instant UI response
        val saved = localDb.saveUser(user)
        syncManager.scheduleSync(user.id)
        return Result.success(saved)
    }

    // ❌ Don't wait for network before returning data
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

**3. Разрешение конфликтов:**
```kotlin
class ConflictResolver {
    fun resolve(local: User, remote: User, strategy: Strategy): User {
        return when (strategy) {
            // ✅ Last Write Wins - простейшая стратегия
            Strategy.LAST_WRITE_WINS ->
                if (remote.lastModified > local.lastModified) remote else local
            // ✅ Merge - объединение изменений по полям
            Strategy.MERGE ->
                User(local.id, remote.name, local.email,
                     maxOf(local.lastModified, remote.lastModified))
            Strategy.LOCAL_WINS -> local
            Strategy.REMOTE_WINS -> remote
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

Handling data synchronization on unstable networks requires offline-first architecture, retry mechanisms, and conflict resolution strategies.

### Key Principles

**Offline-First Architecture:**
- Local database as single source of truth
- All operations are performed locally first
- Synchronization happens asynchronously in background
- User always sees current local data

**Core Components:**
- Repository Pattern for data source abstraction
- [[c-workmanager]] for reliable background execution
- [[c-coroutines]] for asynchronous operations
- Retry mechanisms with exponential backoff
- Conflict resolution strategies

### Implementation

**1. Offline-First Repository:**
```kotlin
class DataRepository @Inject constructor(
    private val localDb: LocalDataSource,
    private val remoteApi: RemoteDataSource,
    private val syncManager: SyncManager
) {
    suspend fun saveUser(user: User): Result<User> {
        // ✅ Save locally first for instant UI response
        val saved = localDb.saveUser(user)
        syncManager.scheduleSync(user.id)
        return Result.success(saved)
    }

    // ❌ Don't wait for network before returning data
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
            // ✅ Last Write Wins - simplest strategy
            Strategy.LAST_WRITE_WINS ->
                if (remote.lastModified > local.lastModified) remote else local
            // ✅ Merge - combine changes by fields
            Strategy.MERGE ->
                User(local.id, remote.name, local.email,
                     maxOf(local.lastModified, remote.lastModified))
            Strategy.LOCAL_WINS -> local
            Strategy.REMOTE_WINS -> remote
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

- How would you implement CRDTs (Conflict-free Replicated Data Types) for automatic conflict resolution?
- What are the trade-offs between optimistic and pessimistic locking in distributed sync?
- How would you handle partial sync failures and maintain data consistency?
- How would you implement sync batching to reduce network overhead?
- What strategies would you use for conflict resolution when merging incompatible field changes?

## References

- [[c-workmanager]] - Background task scheduling
- [[c-coroutines]] - Asynchronous programming primitives
- Android Data Sync Guide: https://developer.android.com/guide/background/processing-data/sync

## Related Questions

### Prerequisites
- WorkManager basics and constraints configuration
- Local database implementation with Room or SQLite

### Related
- [[q-offline-first-architecture--android--hard]]

### Advanced
- Implementing operational transformation for real-time collaboration
- Building distributed consensus algorithms for multi-node sync
