---
id: android-097
title: Offline First Architecture / Архитектура Offline First
aliases:
- Offline First Architecture
- Архитектура Offline First
topic: android
subtopics:
- architecture-clean
- cache-offline
- room
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
created: 2025-10-13
updated: 2025-11-10
tags:
- android
- android/architecture-clean
- android/cache-offline
- android/room
- architecture
- difficulty/hard
- offline-first
- sync
- workmanager
moc: moc-android
related:
- c-clean-architecture
- c-database-design
- q-clean-architecture-android--android--hard
- q-how-to-create-dynamic-screens-at-runtime--android--hard
- q-multi-module-best-practices--android--hard
- q-play-billing-v6-architecture--android--hard
- q-quick-settings-tiles-architecture--android--medium
anki_cards:
- slug: android-097-0-en
  language: en
  anki_id: 1768382478191
  synced_at: '2026-01-23T16:45:06.249194'
- slug: android-097-0-ru
  language: ru
  anki_id: 1768382478215
  synced_at: '2026-01-23T16:45:06.250068'
---
# Вопрос (RU)

> Как спроектировать и реализовать offline-first архитектуру в Android? Какие ключевые компоненты, паттерны и практики необходимо использовать?

# Question (EN)

> How do you design and implement an offline-first architecture in Android? What are the key components, patterns, and best practices?

---

## Ответ (RU)

offline-first архитектура обеспечивает работу приложения без сети, синхронизируя данные при восстановлении подключения.

### Краткий Вариант

- Локальная БД (`Room`) как единственный источник истины.
- Все операции сначала пишут в локальное хранилище, затем синхронизируются с сервером.
- `WorkManager` и сетевой монитор обеспечивают надежную фоновую синхронизацию.
- Явная стратегия разрешения конфликтов и понятный UX для offline/online состояний.

### Подробный Вариант

### Требования

**Функциональные:**
- Доступ к данным и возможность изменений без сети.
- Автоматическая синхронизация при появлении соединения.
- Поддержка конфликт-резолюшна между локальными и серверными данными.

**Нефункциональные:**
- Надежность: отсутствие потери данных при сбоях и перезапусках.
- Производительность: минимизация сетевых запросов и эффективное кэширование.
- Масштабируемость: возможность расширять модель данных и правила синхронизации.

### Архитектура

```text
UI Layer → Repository (Single Source of Truth) → Room DB + Remote API → WorkManager (Sync)
```

**Принципы:**
- Локальная БД — единственный источник истины
- UI читает только из локальной БД через `Flow`
- Операции CUD пишут локально, затем синхронизируются
- `WorkManager` — надежная фоновая синхронизация

### Ключевые Компоненты

**1. `Room` `Entity` с метаданными синхронизации:**

```kotlin
@Entity(tableName = "articles")
data class Article(
    @PrimaryKey val id: String,
    val title: String,
    val content: String,
    val updatedAt: Long,
    @ColumnInfo(name = "is_synced") val isSynced: Boolean = false,
    @ColumnInfo(name = "pending_action") val pendingAction: PendingAction? = null
)

enum class PendingAction { CREATE, UPDATE, DELETE }
```

**2. Repository с offline-first паттерном:**

```kotlin
class ArticleRepository(
    private val dao: ArticleDao,
    private val api: ApiService,
    private val networkMonitor: NetworkMonitor,
    private val syncScheduler: SyncScheduler
) {
    // ✅ Single source of truth
    fun getArticlesFlow(): Flow<List<Article>> = dao.getArticlesFlow()

    // ✅ Write local first
    suspend fun createArticle(article: Article): Result<Article> {
        val local = article.copy(
            id = UUID.randomUUID().toString(),
            isSynced = false,
            pendingAction = PendingAction.CREATE
        )
        dao.insert(local)

        if (networkMonitor.isOnline()) {
            // упрощённый пример синхронного пуша
            runCatching { api.createArticle(local.toDto()) }
                .onSuccess {
                    dao.markSynced(local.id)
                }
                .onFailure {
                    syncScheduler.scheduleSyncWork()
                }
        } else {
            syncScheduler.scheduleSyncWork()
        }

        return Result.success(local)
    }
}
```

**3. NetworkMonitor:**

```kotlin
class NetworkMonitor(context: Context) {

    private val connectivityManager =
        context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager

    private val request: NetworkRequest = NetworkRequest.Builder()
        .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
        .build()

    fun observeNetworkStatus(): Flow<NetworkStatus> = callbackFlow {
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) {
                trySend(NetworkStatus.Available).isSuccess
            }
            override fun onLost(network: Network) {
                trySend(NetworkStatus.Lost).isSuccess
            }
        }
        connectivityManager.registerNetworkCallback(request, callback)
        awaitClose { connectivityManager.unregisterNetworkCallback(callback) }
    }

    fun isOnline(): Boolean {
        val activeNetwork = connectivityManager.activeNetwork ?: return false
        val caps = connectivityManager.getNetworkCapabilities(activeNetwork) ?: return false
        return caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }
}
```

```kotlin
interface SyncScheduler {
    fun scheduleSyncWork()
}
```

**4. `WorkManager` для синхронизации:**

```kotlin
class SyncWorker(
    appContext: Context,
    params: WorkerParameters,
    private val repository: ArticleRepository
) : CoroutineWorker(appContext, params) {

    override suspend fun doWork(): Result {
        return try {
            // ✅ отправляем локальные изменения и получаем обновления
            repository.syncPendingChanges()
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) Result.retry() else Result.failure()
        }
    }
}

// ✅ Периодическая синхронизация каждые 15 минут
fun scheduleSync(context: Context) {
    val constraints = Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .setRequiresBatteryNotLow(true)
        .build()
    val request = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
        .setConstraints(constraints)
        .setBackoffCriteria(
            BackoffPolicy.EXPONENTIAL,
            WorkRequest.MIN_BACKOFF_MILLIS,
            TimeUnit.MILLISECONDS
        )
        .build()
    WorkManager.getInstance(context).enqueueUniquePeriodicWork(
        "sync_work",
        ExistingPeriodicWorkPolicy.KEEP,
        request
    )
}
```

**5. Разрешение конфликтов:**

```kotlin
class ConflictResolver {
    // ✅ Last-Write-Wins: побеждает последнее изменение по updatedAt
    fun resolveConflict(local: Article, remote: Article): Article {
        return if (local.updatedAt > remote.updatedAt) local else remote
    }

    // ✅ Three-way merge: слияние на основе общего предка
    fun mergeArticle(base: Article?, local: Article, remote: Article): Article {
        if (base == null) return resolveConflict(local, remote)

        return Article(
            id = base.id,
            title = mergeField(base.title, local.title, remote.title),
            content = mergeField(base.content, local.content, remote.content),
            updatedAt = maxOf(local.updatedAt, remote.updatedAt),
            isSynced = true
        )
    }

    private fun mergeField(base: String, local: String, remote: String): String {
        return when {
            local == remote -> local
            local == base -> remote  // ✅ изменился remote
            remote == base -> local  // ✅ изменился local
            else -> remote           // ⚠️ конфликт: здесь выбран server wins как пример политики
        }
    }
}
```

**6. UI с индикацией статуса:**

```kotlin
@Composable
fun ArticlesScreen(viewModel: ArticlesViewModel = hiltViewModel()) {
    val articles by viewModel.articles.collectAsState()
    val networkStatus by viewModel.networkStatus.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Articles") },
                actions = {
                    Icon(
                        imageVector = when (networkStatus) {
                            NetworkStatus.Available -> Icons.Default.CloudDone
                            NetworkStatus.Lost -> Icons.Default.CloudOff
                        },
                        tint = when (networkStatus) {
                            NetworkStatus.Available -> Color.Green
                            NetworkStatus.Lost -> Color.Gray
                        }
                    )
                }
            )
        }
    ) { padding ->
        LazyColumn(Modifier.padding(padding)) {
            items(articles) { article ->
                ArticleItem(article, showSyncIndicator = !article.isSynced)
            }
        }
    }
}
```

### Стратегии Кэширования

**Cache-First** (кэш сначала, затем обновление):
```kotlin
fun getCacheFirst(): Flow<List<Article>> = flow {
    // предполагается, что dao.getArticles() — suspend-функция Room
    emit(dao.getArticles()) // ✅ отдаём кэш мгновенно
    try {
        val response = api.getArticles()
        if (response.isSuccessful) {
            response.body()?.let { list ->
                dao.insertAll(list.map { it.toEntity() })
                emit(dao.getArticles()) // ✅ отдаём обновлённые данные
            }
        }
    } catch (e: Exception) {
        // ✅ продолжаем с кэшем
    }
}
```

**Stale-While-Revalidate** (устаревшие данные + обновление):
```kotlin
fun getStaleWhileRevalidate(maxAge: Long): Flow<List<Article>> = flow {
    emit(dao.getArticles()) // ✅ отдаём кэш сразу

    val lastSync = syncMetadataDao.getLastSyncTimestamp("articles") ?: 0
    if (System.currentTimeMillis() - lastSync > maxAge) {
        try {
            val response = api.getArticles()
            if (response.isSuccessful) {
                response.body()?.let { list ->
                    dao.insertAll(list.map { it.toEntity() })
                    syncMetadataDao.updateSyncTimestamp(
                        "articles",
                        System.currentTimeMillis()
                    )
                    emit(dao.getArticles()) // ✅ отдаём свежие данные
                }
            }
        } catch (e: Exception) {
            // ✅ оставляем кэш
        }
    }
}
```

### Лучшие Практики

**Архитектура:**
- Локальная БД как единственный источник истины (Single Source of Truth)
- Repository pattern для изоляции источников данных
- Reactive UI через Kotlin `Flow`
- Явная обработка состояния сети

**Синхронизация:**
- `WorkManager` с exponential backoff (`BackoffPolicy.EXPONENTIAL`)
- Отслеживание pending-операций (CREATE, UPDATE, DELETE)
- Конфликт-резолюшн: Last-Write-Wins или Three-Way Merge (или другая выбранная политика)
- Incremental sync: передача только изменений (`lastSyncTimestamp`)

**Производительность:**
- Пагинация через Paging 3 для больших наборов
- Batch-операции для минимизации транзакций БД
- Фоновый I/O (`Dispatchers.IO`)

**UX:**
- Четкая индикация статуса синхронизации
- Offline-маркеры для несинхронизированных элементов
- Graceful error handling с retry-механизмом

---

## Answer (EN)

offline-first architecture ensures apps work without network, syncing data when connection is restored.

### Short Version

- Local DB (`Room`) as single source of truth.
- All operations write to local storage first, then sync with backend.
- `WorkManager` and network monitoring for reliable background sync.
- Explicit conflict resolution strategy and clear UX for offline/online states.

### Detailed Version

### Requirements

**Functional:**
- Access and modify data while offline.
- Automatic sync when connection is available.
- Support for conflict resolution between local and server data.

**Non-functional:**
- Reliability: no data loss across crashes/restarts.
- Performance: minimize network calls and leverage caching.
- Scalability: easy to extend data model and sync rules.

### Architecture

```text
UI Layer → Repository (Single Source of Truth) → Room DB + Remote API → WorkManager (Sync)
```

**Principles:**
- Local DB is single source of truth
- UI reads only from local DB via `Flow`
- CUD operations write locally first, then sync
- `WorkManager` ensures reliable background sync

### Key Components

**1. `Room` `Entity` with sync metadata:**

```kotlin
@Entity(tableName = "articles")
data class Article(
    @PrimaryKey val id: String,
    val title: String,
    val content: String,
    val updatedAt: Long,
    @ColumnInfo(name = "is_synced") val isSynced: Boolean = false,
    @ColumnInfo(name = "pending_action") val pendingAction: PendingAction? = null
)

enum class PendingAction { CREATE, UPDATE, DELETE }
```

**2. Repository with offline-first pattern:**

```kotlin
class ArticleRepository(
    private val dao: ArticleDao,
    private val api: ApiService,
    private val networkMonitor: NetworkMonitor,
    private val syncScheduler: SyncScheduler
) {
    // ✅ Single source of truth
    fun getArticlesFlow(): Flow<List<Article>> = dao.getArticlesFlow()

    // ✅ Write local first
    suspend fun createArticle(article: Article): Result<Article> {
        val local = article.copy(
            id = UUID.randomUUID().toString(),
            isSynced = false,
            pendingAction = PendingAction.CREATE
        )
        dao.insert(local)

        if (networkMonitor.isOnline()) {
            // simplified example of pushing immediately when online
            runCatching { api.createArticle(local.toDto()) }
                .onSuccess {
                    dao.markSynced(local.id)
                }
                .onFailure {
                    syncScheduler.scheduleSyncWork()
                }
        } else {
            syncScheduler.scheduleSyncWork()
        }

        return Result.success(local)
    }
}
```

**3. NetworkMonitor:**

```kotlin
class NetworkMonitor(context: Context) {

    private val connectivityManager =
        context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager

    private val request: NetworkRequest = NetworkRequest.Builder()
        .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
        .build()

    fun observeNetworkStatus(): Flow<NetworkStatus> = callbackFlow {
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) {
                trySend(NetworkStatus.Available).isSuccess
            }
            override fun onLost(network: Network) {
                trySend(NetworkStatus.Lost).isSuccess
            }
        }
        connectivityManager.registerNetworkCallback(request, callback)
        awaitClose { connectivityManager.unregisterNetworkCallback(callback) }
    }

    fun isOnline(): Boolean {
        val activeNetwork = connectivityManager.activeNetwork ?: return false
        val caps = connectivityManager.getNetworkCapabilities(activeNetwork) ?: return false
        return caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }
}
```

```kotlin
interface SyncScheduler {
    fun scheduleSyncWork()
}
```

**4. `WorkManager` for sync:**

```kotlin
class SyncWorker(
    appContext: Context,
    params: WorkerParameters,
    private val repository: ArticleRepository
) : CoroutineWorker(appContext, params) {

    override suspend fun doWork(): Result {
        return try {
            // ✅ push local changes and pull updates through repository
            repository.syncPendingChanges()
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) Result.retry() else Result.failure()
        }
    }
}

// ✅ Schedule periodic sync every 15 minutes
fun scheduleSync(context: Context) {
    val constraints = Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .setRequiresBatteryNotLow(true)
        .build()
    val request = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
        .setConstraints(constraints)
        .setBackoffCriteria(
            BackoffPolicy.EXPONENTIAL,
            WorkRequest.MIN_BACKOFF_MILLIS,
            TimeUnit.MILLISECONDS
        )
        .build()
    WorkManager.getInstance(context).enqueueUniquePeriodicWork(
        "sync_work",
        ExistingPeriodicWorkPolicy.KEEP,
        request
    )
}
```

**5. Conflict resolution:**

```kotlin
class ConflictResolver {
    // ✅ Last-Write-Wins: most recent by updatedAt wins
    fun resolveConflict(local: Article, remote: Article): Article {
        return if (local.updatedAt > remote.updatedAt) local else remote
    }

    // ✅ Three-way merge: merge based on common ancestor
    fun mergeArticle(base: Article?, local: Article, remote: Article): Article {
        if (base == null) return resolveConflict(local, remote)

        return Article(
            id = base.id,
            title = mergeField(base.title, local.title, remote.title),
            content = mergeField(base.content, local.content, remote.content),
            updatedAt = maxOf(local.updatedAt, remote.updatedAt),
            isSynced = true
        )
    }

    private fun mergeField(base: String, local: String, remote: String): String {
        return when {
            local == remote -> local
            local == base -> remote  // ✅ remote changed only
            remote == base -> local  // ✅ local changed only
            else -> remote           // ⚠️ conflict: server wins policy used as example
        }
    }
}
```

**6. UI with status indication:**

```kotlin
@Composable
fun ArticlesScreen(viewModel: ArticlesViewModel = hiltViewModel()) {
    val articles by viewModel.articles.collectAsState()
    val networkStatus by viewModel.networkStatus.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Articles") },
                actions = {
                    Icon(
                        imageVector = when (networkStatus) {
                            NetworkStatus.Available -> Icons.Default.CloudDone
                            NetworkStatus.Lost -> Icons.Default.CloudOff
                        },
                        tint = when (networkStatus) {
                            NetworkStatus.Available -> Color.Green
                            NetworkStatus.Lost -> Color.Gray
                        }
                    )
                }
            )
        }
    ) { padding ->
        LazyColumn(Modifier.padding(padding)) {
            items(articles) { article ->
                ArticleItem(article, showSyncIndicator = !article.isSynced)
            }
        }
    }
}
```

### Caching Strategies

**Cache-First** (cache first, then update):
```kotlin
fun getCacheFirst(): Flow<List<Article>> = flow {
    // assumes dao.getArticles() is a Room suspend function
    emit(dao.getArticles()) // ✅ emit cache immediately
    try {
        val response = api.getArticles()
        if (response.isSuccessful) {
            response.body()?.let { list ->
                dao.insertAll(list.map { it.toEntity() })
                emit(dao.getArticles()) // ✅ emit updated
            }
        }
    } catch (e: Exception) {
        // ✅ continue with cache
    }
}
```

**Stale-While-Revalidate** (stale data + background refresh):
```kotlin
fun getStaleWhileRevalidate(maxAge: Long): Flow<List<Article>> = flow {
    emit(dao.getArticles()) // ✅ emit cache immediately

    val lastSync = syncMetadataDao.getLastSyncTimestamp("articles") ?: 0
    if (System.currentTimeMillis() - lastSync > maxAge) {
        try {
            val response = api.getArticles()
            if (response.isSuccessful) {
                response.body()?.let { list ->
                    dao.insertAll(list.map { it.toEntity() })
                    syncMetadataDao.updateSyncTimestamp(
                        "articles",
                        System.currentTimeMillis()
                    )
                    emit(dao.getArticles()) // ✅ emit fresh
                }
            }
        } catch (e: Exception) {
            // ✅ keep cache
        }
    }
}
```

### Best Practices

**Architecture:**
- Local DB as single source of truth
- Repository pattern to isolate data sources
- Reactive UI via Kotlin `Flow`
- Explicit network state handling

**Synchronization:**
- `WorkManager` with exponential backoff (`BackoffPolicy.EXPONENTIAL`)
- Track pending operations (CREATE, UPDATE, DELETE)
- Conflict resolution: Last-Write-Wins or Three-Way Merge (or another explicit policy)
- Incremental sync: only changes since `lastSyncTimestamp`

**Performance:**
- Pagination via Paging 3 for large datasets
- Batch operations to minimize DB transactions
- Background I/O (`Dispatchers.IO`)

**UX:**
- Clear sync status indication
- Offline markers for unsynced items
- Graceful error handling with retry mechanism

---

## Дополнительные Вопросы (RU)

- Как обрабатывать частичные ошибки синхронизации (часть элементов успешно, часть нет)?
- Какую стратегию использовать для больших бинарных данных (изображения, файлы) в offline-first?
- Как реализовать оптимистичные обновления UI с откатом при неудачной синхронизации?
- Каковы компромиссы между Last-Write-Wins и Operational Transform для сценариев совместного редактирования?
- Как обрабатывать миграции схемы, когда локальная БД расходится с сервером?

## Follow-ups

- How to handle partial sync failures (some items succeed, others fail)?
- What strategy for large binary data (images, files) in offline-first?
- How to implement optimistic UI updates with rollback on sync failure?
- Trade-offs between Last-Write-Wins and Operational Transform for collaborative editing scenarios?
- How to handle schema migrations when local DB is out of sync with server?

## Ссылки (RU)

- Repository pattern как Single Source of Truth
- Документация `WorkManager`
- Рекомендации по использованию `Room`
- [[moc-android]]

## References

- Repository pattern as single source of truth
- `WorkManager` official documentation
- `Room` database best practices
- [[moc-android]]

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-database-design]]
- [[c-clean-architecture]]

### Предпосылки

- Основы `Room`: локальные операции с базой данных
- Основы `WorkManager`: планирование фоновых задач
- Kotlin `Flow`: реактивные потоки данных

### Связанные

- [[q-clean-architecture-android--android--hard]] — Clean Architecture в Android
- [[q-how-to-create-dynamic-screens-at-runtime--android--hard]] — динамические UI-паттерны

### Продвинутые Темы

- Распределенная синхронизация с использованием CRDT (Conflict-free Replicated Data Types)
- Event sourcing для offline-first приложений
- Мультиустройственная синхронизация с облачным разрешением конфликтов

## Related Questions

### Prerequisites / Concepts

- [[c-database-design]]
- [[c-clean-architecture]]

### Prerequisites
- `Room` database fundamentals - local database operations
- `WorkManager` basics - background task scheduling
- Kotlin `Flow` - reactive data streams

### Related
- [[q-clean-architecture-android--android--hard]] - Clean Architecture in Android
- [[q-how-to-create-dynamic-screens-at-runtime--android--hard]] - Dynamic UI patterns

### Advanced
- Distributed sync with CRDTs (Conflict-free Replicated Data Types)
- Event sourcing for offline-first apps
- Multi-device sync with cloud-based conflict resolution
