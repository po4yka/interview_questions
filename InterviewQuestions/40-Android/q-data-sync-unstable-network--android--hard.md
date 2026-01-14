---
id: android-440
title: Data Sync Unstable Network / Синхронизация данных при нестабильной сети
aliases:
- Data Sync Unstable Network
- Синхронизация данных при нестабильной сети
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
- c-coroutines
- c-workmanager
- q-design-instagram-stories--android--hard
- q-large-file-upload-app--android--hard
- q-network-operations-android--android--medium
- q-offline-first-architecture--android--hard
created: 2025-10-20
updated: 2025-11-02
tags:
- android/architecture-clean
- android/networking-http
- data-sync
- difficulty/hard
- networking
- offline-first
- workmanager
anki_cards:
- slug: android-440-0-en
  language: en
  anki_id: 1768366746882
  synced_at: '2026-01-14T12:07:32.176134'
- slug: android-440-0-ru
  language: ru
  anki_id: 1768366746931
  synced_at: '2026-01-14T12:07:32.183785'
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
- `WorkManager` для надежного фонового выполнения — constraints и управляемый retry при ошибках
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
        // user.id может быть использован для таргетированной синхронизации
        syncManager.scheduleSync(user.id)
        return Result.success(saved)
    }

    // ✅ Не ждем сеть перед возвратом данных: читаем из локального источника,
    // а обновление из сети выполняется асинхронно
    suspend fun getUser(id: String): User = localDb.getUser(id)
}
```

**2. Retry с экспоненциальной задержкой:**
```kotlin
class RetryManager {
    suspend fun <T> executeWithRetry(operation: suspend () -> T): Result<T> {
        var lastError: Throwable? = null
        repeat(3) { attempt ->
            try {
                return Result.success(operation())
            } catch (e: Exception) {
                lastError = e
                // ✅ Экспоненциальная задержка с jitter предотвращает thundering herd
                if (attempt < 2) {
                    delay(1000L * (1L shl attempt) + (0..1000).random())
                }
            }
        }
        return Result.failure(lastError ?: Exception("Max retries exceeded"))
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
            // ✅ Merge — объединение изменений по полям (упрощенный пример)
            Strategy.MERGE ->
                User(
                    id = local.id,
                    name = remote.name,
                    email = local.email,
                    lastModified = maxOf(local.lastModified, remote.lastModified)
                )
            Strategy.LOCAL_WINS -> local  // Локальные изменения имеют приоритет
            Strategy.REMOTE_WINS -> remote  // Удаленные изменения имеют приоритет
        }
    }
}
```

**4. Фоновая синхронизация с `WorkManager`:**
```kotlin
class SyncWorker(
    appContext: Context,
    params: WorkerParameters
) : CoroutineWorker(appContext, params) {

    override suspend fun doWork(): Result {
        return try {
            // В реальном приложении зависимости (например, SyncManager) должны
            // предоставляться через DI (Hilt/ручной Injector), здесь упрощено
            val syncManager = (applicationContext as AppDependenciesProvider).syncManager
            syncManager.performSync()
            Result.success()
        } catch (e: Exception) {
            // ✅ Управляемый retry при ошибке: пробуем до 3 попыток
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
            .setInputData(workDataOf("userId" to userId))  // пример передачи идентификатора
            .build()

        WorkManager.getInstance(context).enqueue(request)
    }

    suspend fun performSync() {
        // Упрощенный пример: здесь должна быть логика чтения локальных изменений,
        // отправки их на сервер и обновления локальной БД ответами сервера.
    }
}
```

**5. Мониторинг состояния сети:**
```kotlin
class NetworkMonitor @Inject constructor(private val context: Context) {
    private val connectivityManager = context.getSystemService<ConnectivityManager>()

    fun observeNetworkState(): Flow<Boolean> = callbackFlow {
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) { trySend(true).isSuccess }
            override fun onLost(network: Network) { trySend(false).isSuccess }
        }
        // Для упрощения примера ошибки регистрации не обрабатываются;
        // в продакшене учтите API-уровень (registerDefaultNetworkCallback требует API 24+)
        // и nullability ConnectivityManager, а для старых API используйте registerNetworkCallback.
        connectivityManager?.registerDefaultNetworkCallback(callback)
        awaitClose { connectivityManager?.unregisterNetworkCallback(callback) }
    }
}
```

## Answer (EN)

Handling data synchronization on unstable networks requires an `offline-first` architecture, retry mechanisms with exponential backoff, and conflict resolution strategies. The main goal is to keep the UI responsive and sync reliable regardless of network state.

### Key Principles

**Offline-First Architecture:**
- Local database (`Room`/SQLite) as a single source of truth — always available
- All operations performed locally first — instant UI response
- Synchronization happens asynchronously in the background — does not block the user
- User always sees current local data — even without network

**Core Components:**
- `Repository Pattern` for data source abstraction — unified interface for local/remote
- `WorkManager` for reliable background execution — constraints and controlled retry on failures
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
        // ✅ Save locally first for instant UI feedback
        val saved = localDb.saveUser(user)
        // user.id can be used for targeted sync
        syncManager.scheduleSync(user.id)
        return Result.success(saved)
    }

    // ✅ Do not wait for network before returning: read from local source,
    // and refresh from network asynchronously
    suspend fun getUser(id: String): User = localDb.getUser(id)
}
```

**2. Retry with exponential backoff:**
```kotlin
class RetryManager {
    suspend fun <T> executeWithRetry(operation: suspend () -> T): Result<T> {
        var lastError: Throwable? = null
        repeat(3) { attempt ->
            try {
                return Result.success(operation())
            } catch (e: Exception) {
                lastError = e
                // ✅ Exponential backoff with jitter helps avoid thundering herd
                if (attempt < 2) {
                    delay(1000L * (1L shl attempt) + (0..1000).random())
                }
            }
        }
        return Result.failure(lastError ?: Exception("Max retries exceeded"))
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
            // ✅ Merge — combine changes by fields (simplified example)
            Strategy.MERGE ->
                User(
                    id = local.id,
                    name = remote.name,
                    email = local.email,
                    lastModified = maxOf(local.lastModified, remote.lastModified)
                )
            Strategy.LOCAL_WINS -> local  // Local changes have priority
            Strategy.REMOTE_WINS -> remote  // Remote changes have priority
        }
    }
}
```

**4. Background sync with `WorkManager`:**
```kotlin
class SyncWorker(
    appContext: Context,
    params: WorkerParameters
) : CoroutineWorker(appContext, params) {

    override suspend fun doWork(): Result {
        return try {
            // In a real app dependencies (e.g., SyncManager) should be provided
            // via DI (Hilt/manual injector); simplified here
            val syncManager = (applicationContext as AppDependenciesProvider).syncManager
            syncManager.performSync()
            Result.success()
        } catch (e: Exception) {
            // ✅ Controlled retry on failure: retry up to 3 attempts
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
            .setInputData(workDataOf("userId" to userId))  // example of passing identifier
            .build()

        WorkManager.getInstance(context).enqueue(request)
    }

    suspend fun performSync() {
        // Simplified example: implement reading local changes,
        // pushing them to server, and updating local DB from responses.
    }
}
```

**5. Network state monitoring:**
```kotlin
class NetworkMonitor @Inject constructor(private val context: Context) {
    private val connectivityManager = context.getSystemService<ConnectivityManager>()

    fun observeNetworkState(): Flow<Boolean> = callbackFlow {
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) { trySend(true).isSuccess }
            override fun onLost(network: Network) { trySend(false).isSuccess }
        }
        // For brevity, registration errors are not handled here;
        // in production, account for API level (registerDefaultNetworkCallback requires API 24+)
        // and ConnectivityManager nullability, and use registerNetworkCallback for older APIs.
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
- Local database implementation with `Room` or `SQLite`
- Basic understanding of `Coroutines` and `Flow`

### Related (Same Level)
- [[q-offline-first-architecture--android--hard]]
- `Repository Pattern` implementation
- Network state monitoring

### Advanced (Harder)
- Implementing operational transformation for real-time collaboration
- Building distributed consensus algorithms for multi-node sync
- `CRDTs` for automatic conflict resolution