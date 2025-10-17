---
id: "20251015082237561"
title: "Offline First Architecture / Архитектура Offline First"
topic: android
difficulty: hard
status: draft
created: 2025-10-13
tags: [architecture, offline-first, networking, sync, room, workmanager, difficulty/hard]
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-android
related_questions: []
---
# How to Implement Offline-First Architecture in Android

**Сложность**:  Hard
**Источник**: Amit Shekhar Android Interview Questions

# Question (EN)
> 

# Вопрос (RU)
> 

---

## Answer (EN)
# Question (EN)
How do you design and implement an offline-first architecture in Android? What are the key components, patterns, and best practices?

## Answer (EN)
Offline-first architecture ensures apps work seamlessly without network connectivity, syncing data when connection is available. This approach improves user experience, reduces data usage, and provides resilience to network failures.

#### 1. **Architecture Overview**

```

                   Presentation Layer                 
              (ViewModel + UI State)                  

                     

                 Repository Layer                     
        (Single Source of Truth Pattern)             

                                 
       
  Local Storage          Remote API       
  (Room DB)              (Retrofit)       
       
                                 
       
                  
       
          Sync Manager         
          (WorkManager)        
       
```

#### 2. **Core Components Implementation**

**2.1 Local Database as Single Source of Truth**

```kotlin
@Database(
    entities = [Article::class, User::class, SyncMetadata::class],
    version = 1
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun articleDao(): ArticleDao
    abstract fun userDao(): UserDao
    abstract fun syncMetadataDao(): SyncMetadataDao
}

@Entity(tableName = "articles")
data class Article(
    @PrimaryKey val id: String,
    val title: String,
    val content: String,
    val authorId: String,
    val createdAt: Long,
    val updatedAt: Long,

    // Offline-first specific fields
    @ColumnInfo(name = "is_synced") val isSynced: Boolean = false,
    @ColumnInfo(name = "is_deleted") val isDeleted: Boolean = false,
    @ColumnInfo(name = "pending_action") val pendingAction: PendingAction? = null
)

enum class PendingAction {
    CREATE, UPDATE, DELETE
}

@Entity(tableName = "sync_metadata")
data class SyncMetadata(
    @PrimaryKey val entityType: String,
    val lastSyncTimestamp: Long,
    val syncStatus: SyncStatus
)

enum class SyncStatus {
    IDLE, SYNCING, FAILED
}
```

**2.2 Repository with Offline-First Pattern**

```kotlin
class ArticleRepository(
    private val articleDao: ArticleDao,
    private val apiService: ApiService,
    private val syncMetadataDao: SyncMetadataDao,
    private val networkMonitor: NetworkMonitor
) {
    // Expose local data as Flow (single source of truth)
    fun getArticlesFlow(): Flow<List<Article>> = articleDao.getArticlesFlow()
        .map { articles -> articles.filter { !it.isDeleted } }

    fun getArticleById(id: String): Flow<Article?> = articleDao.getArticleByIdFlow(id)

    // Create/Update/Delete - always write to local first
    suspend fun createArticle(article: Article): Result<Article> {
        return try {
            // 1. Save to local database immediately
            val localArticle = article.copy(
                id = UUID.randomUUID().toString(),
                isSynced = false,
                pendingAction = PendingAction.CREATE
            )
            articleDao.insert(localArticle)

            // 2. Try to sync if online
            if (networkMonitor.isOnline()) {
                syncCreateArticle(localArticle)
            } else {
                // Will sync later via WorkManager
                scheduleSyncWork()
            }

            Result.success(localArticle)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun updateArticle(article: Article): Result<Article> {
        return try {
            val updatedArticle = article.copy(
                updatedAt = System.currentTimeMillis(),
                isSynced = false,
                pendingAction = PendingAction.UPDATE
            )
            articleDao.update(updatedArticle)

            if (networkMonitor.isOnline()) {
                syncUpdateArticle(updatedArticle)
            } else {
                scheduleSyncWork()
            }

            Result.success(updatedArticle)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun deleteArticle(id: String): Result<Unit> {
        return try {
            // Soft delete
            articleDao.markAsDeleted(id, PendingAction.DELETE)

            if (networkMonitor.isOnline()) {
                syncDeleteArticle(id)
            } else {
                scheduleSyncWork()
            }

            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // Sync methods
    private suspend fun syncCreateArticle(article: Article) {
        try {
            val response = apiService.createArticle(article.toDto())
            if (response.isSuccessful) {
                response.body()?.let { serverArticle ->
                    articleDao.update(
                        article.copy(
                            id = serverArticle.id,
                            isSynced = true,
                            pendingAction = null
                        )
                    )
                }
            }
        } catch (e: Exception) {
            Log.e("Sync", "Failed to sync create", e)
            scheduleSyncWork()
        }
    }

    private suspend fun syncUpdateArticle(article: Article) {
        try {
            val response = apiService.updateArticle(article.id, article.toDto())
            if (response.isSuccessful) {
                articleDao.update(article.copy(isSynced = true, pendingAction = null))
            }
        } catch (e: Exception) {
            Log.e("Sync", "Failed to sync update", e)
            scheduleSyncWork()
        }
    }

    private suspend fun syncDeleteArticle(id: String) {
        try {
            val response = apiService.deleteArticle(id)
            if (response.isSuccessful) {
                articleDao.deleteById(id)
            }
        } catch (e: Exception) {
            Log.e("Sync", "Failed to sync delete", e)
            scheduleSyncWork()
        }
    }

    // Fetch from server and update local
    suspend fun refreshArticles(): Result<Unit> {
        return try {
            val lastSync = syncMetadataDao.getLastSyncTimestamp("articles") ?: 0
            val response = apiService.getArticles(since = lastSync)

            if (response.isSuccessful) {
                response.body()?.let { articles ->
                    articleDao.insertAll(
                        articles.map { it.toEntity().copy(isSynced = true) }
                    )
                    syncMetadataDao.updateSyncTimestamp(
                        "articles",
                        System.currentTimeMillis()
                    )
                }
                Result.success(Unit)
            } else {
                Result.failure(Exception("Failed to refresh: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private fun scheduleSyncWork() {
        // Implemented in section 3
    }
}
```

**2.3 Network Monitoring**

```kotlin
class NetworkMonitor(private val context: Context) {
    private val connectivityManager = context.getSystemService<ConnectivityManager>()

    fun isOnline(): Boolean {
        val network = connectivityManager?.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }

    fun observeNetworkStatus(): Flow<NetworkStatus> = callbackFlow {
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) {
                trySend(NetworkStatus.Available)
            }

            override fun onLost(network: Network) {
                trySend(NetworkStatus.Lost)
            }

            override fun onCapabilitiesChanged(
                network: Network,
                capabilities: NetworkCapabilities
            ) {
                val hasInternet = capabilities.hasCapability(
                    NetworkCapabilities.NET_CAPABILITY_INTERNET
                )
                trySend(if (hasInternet) NetworkStatus.Available else NetworkStatus.Lost)
            }
        }

        val request = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .build()

        connectivityManager?.registerNetworkCallback(request, callback)

        awaitClose {
            connectivityManager?.unregisterNetworkCallback(callback)
        }
    }
}

sealed class NetworkStatus {
    object Available : NetworkStatus()
    object Lost : NetworkStatus()
}
```

#### 3. **Sync Manager with WorkManager**

```kotlin
class SyncWorker(
    context: Context,
    params: WorkerParameters,
    private val articleRepository: ArticleRepository,
    private val userRepository: UserRepository
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            // Sync pending local changes to server
            syncPendingChanges()

            // Fetch latest data from server
            articleRepository.refreshArticles()
            userRepository.refreshUsers()

            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure()
            }
        }
    }

    private suspend fun syncPendingChanges() {
        // Get all pending articles
        val pendingArticles = articleRepository.getPendingArticles()

        pendingArticles.forEach { article ->
            when (article.pendingAction) {
                PendingAction.CREATE -> articleRepository.syncCreateArticle(article)
                PendingAction.UPDATE -> articleRepository.syncUpdateArticle(article)
                PendingAction.DELETE -> articleRepository.syncDeleteArticle(article.id)
                null -> { /* Already synced */ }
            }
        }
    }
}

object SyncScheduler {
    private const val SYNC_WORK_NAME = "sync_work"

    fun schedulePeriodicSync(context: Context) {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()

        val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(
            repeatInterval = 15,
            repeatIntervalTimeUnit = TimeUnit.MINUTES
        )
            .setConstraints(constraints)
            .setBackoffCriteria(
                BackoffPolicy.EXPONENTIAL,
                WorkRequest.MIN_BACKOFF_MILLIS,
                TimeUnit.MILLISECONDS
            )
            .build()

        WorkManager.getInstance(context).enqueueUniquePeriodicWork(
            SYNC_WORK_NAME,
            ExistingPeriodicWorkPolicy.KEEP,
            syncRequest
        )
    }

    fun scheduleImmediateSync(context: Context) {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()

        val syncRequest = OneTimeWorkRequestBuilder<SyncWorker>()
            .setConstraints(constraints)
            .build()

        WorkManager.getInstance(context).enqueue(syncRequest)
    }
}
```

#### 4. **Conflict Resolution**

```kotlin
data class ArticleWithVersion(
    val article: Article,
    val version: Int
)

class ConflictResolver {
    suspend fun resolveArticleConflict(
        local: Article,
        remote: Article
    ): Article {
        return when {
            // Server wins if both modified at same time
            local.updatedAt == remote.updatedAt -> remote

            // Most recent wins
            local.updatedAt > remote.updatedAt -> local
            else -> remote
        }
    }

    // Three-way merge for complex objects
    suspend fun mergeArticle(
        base: Article?,
        local: Article,
        remote: Article
    ): Article {
        if (base == null) {
            // No common ancestor, use timestamp
            return if (local.updatedAt > remote.updatedAt) local else remote
        }

        return Article(
            id = remote.id,
            title = mergeField(base.title, local.title, remote.title),
            content = mergeField(base.content, local.content, remote.content),
            authorId = remote.authorId,
            createdAt = remote.createdAt,
            updatedAt = maxOf(local.updatedAt, remote.updatedAt),
            isSynced = true,
            isDeleted = local.isDeleted || remote.isDeleted,
            pendingAction = null
        )
    }

    private fun mergeField(base: String, local: String, remote: String): String {
        return when {
            local == remote -> local
            local == base -> remote
            remote == base -> local
            else -> remote // Default to server value
        }
    }
}
```

#### 5. **Caching Strategy**

```kotlin
class CachingStrategy(
    private val database: AppDatabase,
    private val apiService: ApiService
) {
    // Cache-First: Return cached data immediately, refresh in background
    fun getArticlesCacheFirst(): Flow<List<Article>> = flow {
        // Emit cached data first
        emit(database.articleDao().getArticles())

        // Refresh from network
        try {
            val response = apiService.getArticles()
            if (response.isSuccessful) {
                response.body()?.let { articles ->
                    database.articleDao().insertAll(articles.map { it.toEntity() })
                    emit(database.articleDao().getArticles())
                }
            }
        } catch (e: Exception) {
            // Continue with cached data
        }
    }

    // Network-First with fallback to cache
    suspend fun getArticleNetworkFirst(id: String): Article? {
        return try {
            val response = apiService.getArticle(id)
            if (response.isSuccessful) {
                response.body()?.let { article ->
                    val entity = article.toEntity()
                    database.articleDao().insert(entity)
                    entity
                }
            } else {
                database.articleDao().getArticleById(id)
            }
        } catch (e: Exception) {
            database.articleDao().getArticleById(id)
        }
    }

    // Stale-While-Revalidate
    fun getArticlesStaleWhileRevalidate(maxAge: Long): Flow<List<Article>> = flow {
        val lastSync = database.syncMetadataDao().getLastSyncTimestamp("articles") ?: 0
        val articles = database.articleDao().getArticles()

        // Emit cached data
        emit(articles)

        // Refresh if stale
        if (System.currentTimeMillis() - lastSync > maxAge) {
            try {
                val response = apiService.getArticles()
                if (response.isSuccessful) {
                    response.body()?.let { newArticles ->
                        database.articleDao().insertAll(newArticles.map { it.toEntity() })
                        database.syncMetadataDao().updateSyncTimestamp(
                            "articles",
                            System.currentTimeMillis()
                        )
                        emit(database.articleDao().getArticles())
                    }
                }
            } catch (e: Exception) {
                // Keep using cached data
            }
        }
    }
}
```

#### 6. **ViewModel Integration**

```kotlin
@HiltViewModel
class ArticlesViewModel @Inject constructor(
    private val articleRepository: ArticleRepository,
    private val networkMonitor: NetworkMonitor
) : ViewModel() {

    val networkStatus = networkMonitor.observeNetworkStatus()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = NetworkStatus.Lost
        )

    val articles = articleRepository.getArticlesFlow()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    val syncStatus = articleRepository.getSyncStatus()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = SyncStatus.IDLE
        )

    fun createArticle(title: String, content: String) {
        viewModelScope.launch {
            val article = Article(
                id = "",
                title = title,
                content = content,
                authorId = getCurrentUserId(),
                createdAt = System.currentTimeMillis(),
                updatedAt = System.currentTimeMillis()
            )
            articleRepository.createArticle(article)
        }
    }

    fun refreshArticles() {
        viewModelScope.launch {
            articleRepository.refreshArticles()
        }
    }
}
```

#### 7. **UI Implementation**

```kotlin
@Composable
fun ArticlesScreen(viewModel: ArticlesViewModel = hiltViewModel()) {
    val articles by viewModel.articles.collectAsState()
    val networkStatus by viewModel.networkStatus.collectAsState()
    val syncStatus by viewModel.syncStatus.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Articles") },
                actions = {
                    // Show network status
                    NetworkStatusIndicator(networkStatus)

                    // Show sync status
                    if (syncStatus == SyncStatus.SYNCING) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(24.dp),
                            strokeWidth = 2.dp
                        )
                    }
                }
            )
        }
    ) { padding ->
        LazyColumn(modifier = Modifier.padding(padding)) {
            items(articles) { article ->
                ArticleItem(
                    article = article,
                    showSyncStatus = !article.isSynced
                )
            }
        }
    }
}

@Composable
fun NetworkStatusIndicator(status: NetworkStatus) {
    Icon(
        imageVector = when (status) {
            is NetworkStatus.Available -> Icons.Default.CloudDone
            is NetworkStatus.Lost -> Icons.Default.CloudOff
        },
        contentDescription = "Network status",
        tint = when (status) {
            is NetworkStatus.Available -> Color.Green
            is NetworkStatus.Lost -> Color.Gray
        }
    )
}
```

### Best Practices

**Architecture:**
- [ ] Use local database as single source of truth
- [ ] Implement repository pattern
- [ ] Use Flow for reactive data
- [ ] Handle network state changes
- [ ] Implement proper error handling

**Data Synchronization:**
- [ ] Use WorkManager for reliable sync
- [ ] Implement exponential backoff
- [ ] Handle conflicts gracefully
- [ ] Track sync status
- [ ] Queue offline operations

**Performance:**
- [ ] Implement pagination
- [ ] Use incremental sync
- [ ] Cache strategically
- [ ] Minimize database operations
- [ ] Use background threads

**User Experience:**
- [ ] Show sync status
- [ ] Display network connectivity
- [ ] Provide offline indicators
- [ ] Handle errors gracefully
- [ ] Implement pull-to-refresh

---



## Ответ (RU)
# Вопрос (RU)
Как спроектировать и реализовать offline-first архитектуру в Android? Каковы ключевые компоненты, паттерны и лучшие практики?

## Ответ (RU)
Offline-first архитектура обеспечивает бесперебойную работу приложений без сетевого подключения, синхронизируя данные при доступности соединения.

#### Ключевые компоненты:

**1. Локальная база данных как единственный источник истины**
- Все операции сначала выполняются локально
- UI всегда читает из локальной БД
- Данные синхронизируются в фоне

**2. Репозиторий с offline-first паттерном**
- Немедленная запись в локальную БД
- Попытка синхронизации при наличии сети
- Отложенная синхронизация при отсутствии связи

**3. Мониторинг сети**
- Отслеживание статуса подключения
- Автоматическая синхронизация при восстановлении связи

**4. Менеджер синхронизации (WorkManager)**
- Периодическая синхронизация
- Retry-логика с экспоненциальной задержкой
- Синхронизация только при наличии сети

**5. Разрешение конфликтов**
- Стратегии слияния (last-write-wins, three-way merge)
- Версионирование данных
- Обработка конфликтов на уровне полей

**6. Стратегии кэширования**
- Cache-First: кэш → сеть
- Network-First: сеть → кэш
- Stale-While-Revalidate: кэш + фоновое обновление

### Лучшие практики:

**Архитектура:**
- Локальная БД - единственный источник истины
- Паттерн репозитория
- Reactive data с Flow
- Обработка состояний сети

**Синхронизация:**
- WorkManager для надежной синхронизации
- Экспоненциальная задержка повторов
- Обработка конфликтов
- Отслеживание статуса синхронизации

**Производительность:**
- Пагинация
- Инкрементальная синхронизация
- Стратегическое кэширование

**UX:**
- Отображение статуса синхронизации
- Индикация сетевого подключения
- Offline-индикаторы
- Обработка ошибок


---

## Related Questions

### Hub
- [[q-clean-architecture-android--android--hard]] - Clean Architecture principles

### Related (Hard)
- [[q-mvi-architecture--android--hard]] - MVI architecture pattern
- [[q-mvi-handle-one-time-events--android--hard]] - MVI one-time event handling
- [[q-kmm-architecture--multiplatform--hard]] - KMM architecture patterns

