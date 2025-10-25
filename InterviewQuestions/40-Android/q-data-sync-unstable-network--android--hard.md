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
  - q-android-networking-basics--android--medium
  - q-android-workmanager--android--medium
  - q-offline-first-architecture--android--hard
created: 2025-10-20
updated: 2025-10-20
tags: [android/architecture-clean, android/networking-http, data-sync, difficulty/hard, networking, offline-first, workmanager]
source: https://developer.android.com/guide/background/processing-data/sync
source_note: Android Data Sync documentation
date created: Saturday, October 25th 2025, 1:26:29 pm
date modified: Saturday, October 25th 2025, 4:52:13 pm
---

# Вопрос (RU)
> Как бы вы обрабатывали синхронизацию данных в Android приложении при нестабильном сетевом соединении?

# Question (EN)
> How would you handle data synchronization in an Android app with an unstable network connection?

## Ответ (RU)

Обработка синхронизации данных при нестабильной сети требует offline-first архитектуры, механизмов повторных попыток и стратегий разрешения конфликтов.

### Теория: Принципы Синхронизации При Нестабильной Сети

**Основные концепции:**
- **Offline-First архитектура** - локальная база данных как единственный источник истины
- **Механизмы повторных попыток** - автоматические retry с экспоненциальной задержкой
- **Разрешение конфликтов** - стратегии для обработки конфликтующих изменений
- **Очереди синхронизации** - отложенная синхронизация при восстановлении сети
- **Мониторинг состояния сети** - отслеживание доступности сети

**Принципы работы:**
- Все операции выполняются локально в первую очередь
- Синхронизация происходит в фоновом режиме
- Конфликты разрешаются на основе бизнес-логики
- Пользователь всегда видит актуальные локальные данные

**Архитектурные паттерны:**
- **Repository Pattern** - абстракция над источниками данных
- **Observer Pattern** - уведомления о изменениях состояния сети
- **Strategy Pattern** - выбор стратегии синхронизации
- **Queue Pattern** - отложенное выполнение операций

### 1. Offline-First Архитектура

**Теоретические основы:**
Offline-First архитектура основана на принципе "локальная база данных как источник истины". Это означает, что все операции чтения и записи выполняются против локальной базы данных, а синхронизация с сервером происходит асинхронно в фоновом режиме.

**Преимущества:**
- Мгновенная отзывчивость интерфейса
- Работа без интернета
- Снижение нагрузки на сервер
- Лучший пользовательский опыт

**Компактная реализация:**
```kotlin
class OfflineFirstRepository @Inject constructor(
    private val localDataSource: LocalDataSource,
    private val syncManager: SyncManager
) {
    suspend fun saveUser(user: User): Result<User> {
        val savedUser = localDataSource.saveUser(user)
        syncManager.scheduleSync(user.id)
        return Result.success(savedUser)
    }

    suspend fun getUser(id: String): Result<User> {
        return Result.success(localDataSource.getUser(id))
    }
}
```

### 2. Механизмы Повторных Попыток

**Теоретические основы:**
Экспоненциальная задержка с jitter предотвращает "thundering herd" проблему, когда множество клиентов одновременно пытаются переподключиться к серверу. Jitter добавляет случайность к задержке, распределяя нагрузку во времени.

**Алгоритм задержки:**
- Базовая задержка: 1 секунда
- Экспоненциальное увеличение: delay = baseDelay * (2^attempt)
- Jitter: добавление случайной задержки 0-1000ms
- Максимальное количество попыток: 3

**Компактная реализация:**
```kotlin
class RetryManager {
    suspend fun <T> executeWithRetry(operation: suspend () -> T): Result<T> {
        repeat(3) { attempt ->
            try {
                return Result.success(operation())
            } catch (e: Exception) {
                if (attempt < 2) delay(1000L * (1L shl attempt) + (0..1000).random())
            }
        }
        return Result.failure(Exception("Max retries exceeded"))
    }
}
```

### 3. Разрешение Конфликтов

**Теоретические основы:**
Конфликты возникают когда одни и те же данные изменяются локально и на сервере. Стратегии разрешения конфликтов определяют, какая версия данных должна быть сохранена.

**Стратегии разрешения:**
- **Last Write Wins** - побеждает последняя запись по времени
- **Local Wins** - локальные изменения имеют приоритет
- **Remote Wins** - серверные изменения имеют приоритет
- **Merge** - объединение изменений по полям

**Компактная реализация:**
```kotlin
class ConflictResolver {
    fun resolveConflict(local: User, remote: User, strategy: Strategy): User {
        return when (strategy) {
            Strategy.LAST_WRITE_WINS -> if (remote.lastModified > local.lastModified) remote else local
            Strategy.LOCAL_WINS -> local
            Strategy.REMOTE_WINS -> remote
            Strategy.MERGE -> User(local.id, remote.name, local.email, maxOf(local.lastModified, remote.lastModified))
        }
    }
}
```

### 4. Очереди Синхронизации

**Теоретические основы:**
WorkManager обеспечивает надежное выполнение фоновых задач с учетом системных ограничений. Он автоматически обрабатывает перезапуск приложения, оптимизирует батарею и соблюдает ограничения Doze Mode.

**Принципы работы:**
- Очереди задач сохраняются между перезапусками приложения
- Автоматический retry с экспоненциальной задержкой
- Ограничения по типу сети и состоянию батареи
- Гарантированное выполнение при восстановлении сети

**Компактная реализация:**
```kotlin
class SyncWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        return try {
            SyncManager(applicationContext).performSync()
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) Result.retry() else Result.failure()
        }
    }
}

class SyncManager @Inject constructor(private val context: Context) {
    fun scheduleSync(userId: String) {
        val constraints = Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build()
        val request = OneTimeWorkRequestBuilder<SyncWorker>().setConstraints(constraints).build()
        WorkManager.getInstance(context).enqueue(request)
    }
}
```

### 5. Мониторинг Состояния Сети

**Теоретические основы:**
NetworkCallback API позволяет отслеживать изменения состояния сети в реальном времени. Это критически важно для адаптации стратегии синхронизации к текущим условиям сети.

**Типы сетевых состояний:**
- **Connected** - стабильное соединение
- **Unstable** - нестабильное соединение
- **Disconnected** - отсутствие соединения
- **Metered** - ограниченный трафик

**Компактная реализация:**
```kotlin
class NetworkMonitor @Inject constructor(private val context: Context) {
    private val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager

    fun isNetworkAvailable(): Boolean {
        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }

    fun observeNetworkState(): Flow<Boolean> = callbackFlow {
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) = trySend(true)
            override fun onLost(network: Network) = trySend(false)
        }
        connectivityManager.registerDefaultNetworkCallback(callback)
        awaitClose { connectivityManager.unregisterNetworkCallback(callback) }
    }
}
```

### CPU-интенсивные Операции

**Теоретические основы:**
Нестабильная сеть требует адаптивной стратегии синхронизации. CPU-интенсивные операции включают анализ стабильности сети, определение оптимального размера батча и выбор алгоритма сжатия данных.

**Оптимизация производительности:**
- Анализ задержки сети для определения стабильности
- Динамическое изменение размера батча в зависимости от пропускной способности
- Сжатие данных для снижения трафика
- Кэширование результатов анализа сети

**Компактная реализация:**
```kotlin
class SyncStrategy @Inject constructor(private val networkMonitor: NetworkMonitor) {
    suspend fun determineSyncStrategy(): SyncStrategyType {
        return when {
            !networkMonitor.isNetworkAvailable() -> SyncStrategyType.OFFLINE
            isNetworkStable() -> SyncStrategyType.IMMEDIATE
            else -> SyncStrategyType.BATCHED
        }
    }

    private suspend fun isNetworkStable(): Boolean {
        return try {
            val startTime = System.currentTimeMillis()
            delay(100) // Ping simulation
            (System.currentTimeMillis() - startTime) < 1000
        } catch (e: Exception) { false }
    }
}
```

## Answer (EN)

Handling data synchronization on unstable networks requires offline-first architecture, retry mechanisms, and conflict resolution strategies.

### Theory: Unstable Network Sync Principles

**Core Concepts:**
- **Offline-First Architecture** - local database as single source of truth
- **Retry Mechanisms** - automatic retry with exponential backoff
- **Conflict Resolution** - strategies for handling conflicting changes
- **Sync Queues** - deferred synchronization on network recovery
- **Network State Monitoring** - tracking network availability

**Working Principles:**
- All operations are performed locally first
- Synchronization happens in background
- Conflicts are resolved based on business logic
- User always sees current local data

**Architectural Patterns:**
- **Repository Pattern** - abstraction over data sources
- **Observer Pattern** - notifications about network state changes
- **Strategy Pattern** - sync strategy selection
- **Queue Pattern** - deferred operation execution

### 1. Offline-First Architecture

**Theoretical Foundations:**
Offline-First architecture is based on the principle of "local database as source of truth". This means all read and write operations are performed against the local database, while synchronization with the server happens asynchronously in the background.

**Benefits:**
- Instant UI responsiveness
- Offline functionality
- Reduced server load
- Better user experience

**Compact Implementation:**
```kotlin
class OfflineFirstRepository @Inject constructor(
    private val localDataSource: LocalDataSource,
    private val syncManager: SyncManager
) {
    suspend fun saveUser(user: User): Result<User> {
        val savedUser = localDataSource.saveUser(user)
        syncManager.scheduleSync(user.id)
        return Result.success(savedUser)
    }

    suspend fun getUser(id: String): Result<User> {
        return Result.success(localDataSource.getUser(id))
    }
}
```

### 2. Retry Mechanisms

**Theoretical Foundations:**
Exponential backoff with jitter prevents the "thundering herd" problem when multiple clients simultaneously try to reconnect to the server. Jitter adds randomness to the delay, distributing load over time.

**Delay Algorithm:**
- Base delay: 1 second
- Exponential increase: delay = baseDelay * (2^attempt)
- Jitter: add random delay 0-1000ms
- Maximum retry attempts: 3

**Compact Implementation:**
```kotlin
class RetryManager {
    suspend fun <T> executeWithRetry(operation: suspend () -> T): Result<T> {
        repeat(3) { attempt ->
            try {
                return Result.success(operation())
            } catch (e: Exception) {
                if (attempt < 2) delay(1000L * (1L shl attempt) + (0..1000).random())
            }
        }
        return Result.failure(Exception("Max retries exceeded"))
    }
}
```

### 3. Conflict Resolution

**Theoretical Foundations:**
Conflicts occur when the same data is modified both locally and on the server. Conflict resolution strategies determine which version of data should be saved.

**Resolution Strategies:**
- **Last Write Wins** - last write by timestamp wins
- **Local Wins** - local changes have priority
- **Remote Wins** - server changes have priority
- **Merge** - combine changes by fields

**Compact Implementation:**
```kotlin
class ConflictResolver {
    fun resolveConflict(local: User, remote: User, strategy: Strategy): User {
        return when (strategy) {
            Strategy.LAST_WRITE_WINS -> if (remote.lastModified > local.lastModified) remote else local
            Strategy.LOCAL_WINS -> local
            Strategy.REMOTE_WINS -> remote
            Strategy.MERGE -> User(local.id, remote.name, local.email, maxOf(local.lastModified, remote.lastModified))
        }
    }
}
```

### 4. Sync Queues

**Theoretical Foundations:**
WorkManager provides reliable execution of background tasks considering system constraints. It automatically handles app restarts, optimizes battery usage, and respects Doze Mode limitations.

**Working Principles:**
- Task queues persist across app restarts
- Automatic retry with exponential backoff
- Constraints by network type and battery state
- Guaranteed execution on network recovery

**Compact Implementation:**
```kotlin
class SyncWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        return try {
            SyncManager(applicationContext).performSync()
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) Result.retry() else Result.failure()
        }
    }
}

class SyncManager @Inject constructor(private val context: Context) {
    fun scheduleSync(userId: String) {
        val constraints = Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build()
        val request = OneTimeWorkRequestBuilder<SyncWorker>().setConstraints(constraints).build()
        WorkManager.getInstance(context).enqueue(request)
    }
}
```

### 5. Network State Monitoring

**Theoretical Foundations:**
NetworkCallback API allows real-time tracking of network state changes. This is critical for adapting sync strategy to current network conditions.

**Network State Types:**
- **Connected** - stable connection
- **Unstable** - unstable connection
- **Disconnected** - no connection
- **Metered** - limited traffic

**Compact Implementation:**
```kotlin
class NetworkMonitor @Inject constructor(private val context: Context) {
    private val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager

    fun isNetworkAvailable(): Boolean {
        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }

    fun observeNetworkState(): Flow<Boolean> = callbackFlow {
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) = trySend(true)
            override fun onLost(network: Network) = trySend(false)
        }
        connectivityManager.registerDefaultNetworkCallback(callback)
        awaitClose { connectivityManager.unregisterNetworkCallback(callback) }
    }
}
```

### CPU-Intensive Operations

**Theoretical Foundations:**
Unstable networks require adaptive sync strategy. CPU-intensive operations include network stability analysis, optimal batch size determination, and data compression algorithm selection.

**Performance Optimization:**
- Network latency analysis for stability determination
- Dynamic batch size adjustment based on throughput
- Data compression to reduce traffic
- Network analysis result caching

**Compact Implementation:**
```kotlin
class SyncStrategy @Inject constructor(private val networkMonitor: NetworkMonitor) {
    suspend fun determineSyncStrategy(): SyncStrategyType {
        return when {
            !networkMonitor.isNetworkAvailable() -> SyncStrategyType.OFFLINE
            isNetworkStable() -> SyncStrategyType.IMMEDIATE
            else -> SyncStrategyType.BATCHED
        }
    }

    private suspend fun isNetworkStable(): Boolean {
        return try {
            val startTime = System.currentTimeMillis()
            delay(100) // Ping simulation
            (System.currentTimeMillis() - startTime) < 1000
        } catch (e: Exception) { false }
    }
}
```

**See also:** c-network-protocols, c-rest-api


## Follow-ups

- How do you handle data conflicts in offline-first architecture?
- What are the performance implications of different sync strategies?
- How do you implement efficient network state monitoring?

## Related Questions

### Advanced (Harder)
- [[q-offline-first-architecture--android--hard]]
