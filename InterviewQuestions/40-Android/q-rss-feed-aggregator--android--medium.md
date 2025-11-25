---
id: android-348
title: RSS Feed Aggregator / Агрегатор RSS лент
aliases: [RSS Feed Aggregator, Агрегатор RSS лент]
topic: android
subtopics:
  - networking-http
  - room
question_kind: theory
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-retrofit
  - c-room
  - q-dagger-build-time-optimization--android--medium
  - q-data-sync-unstable-network--android--hard
  - q-databases-android--android--easy
  - q-how-to-choose-layout-for-fragment--android--easy
  - q-tiktok-video-feed--android--hard
  - q-webp-image-format-android--android--easy
created: 2025-10-15
updated: 2025-11-10
tags: [android/networking-http, android/room, difficulty/medium]

date created: Saturday, November 1st 2025, 12:47:03 pm
date modified: Tuesday, November 25th 2025, 8:53:57 pm
---

# Вопрос (RU)
> Агрегатор RSS лент

# Question (EN)
> RSS Feed Aggregator

---

## Ответ (RU)

RSS-агрегатор получает и отображает RSS-ленты из нескольких источников. Ключевые требования: парсинг XML (RSS/Atom), локальное хранение, фоновая синхронизация и уведомления о новых публикациях.

### Архитектура

```

   UI Layer     Compose/XML + ViewModel



 Repository         Координация данных



 Network        Room      WorkManager
  (RSS)       Database      (Sync)

```

### 1. Модели Данных

```kotlin
// Entity для Room
@Entity(tableName = "rss_feeds")
data class RssFeed(
    @PrimaryKey val feedUrl: String,
    val title: String,
    val description: String,
    val lastUpdated: Long = 0L,
    val isActive: Boolean = true
)

@Entity(
    tableName = "rss_items",
    foreignKeys = [
        ForeignKey(
            entity = RssFeed::class,
            parentColumns = ["feedUrl"],
            childColumns = ["feedUrl"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("feedUrl")]
)
data class RssItem(
    // В продакшене разумно включать feedUrl в ключ (guid + feedUrl),
    // чтобы избежать коллизий между лентами.
    @PrimaryKey val guid: String,  // Уникальный ID из RSS или fallback: link/комбинация с feedUrl
    val feedUrl: String,
    val title: String,
    val description: String,
    val link: String,
    val pubDate: Long,
    val author: String? = null,
    val imageUrl: String? = null,
    val isRead: Boolean = false,
    val isFavorite: Boolean = false
)

// Relation для UI
data class FeedWithItems(
    @Embedded val feed: RssFeed,
    @Relation(
        parentColumn = "feedUrl",
        entityColumn = "feedUrl"
    )
    val items: List<RssItem>
)
```

### 2. Room Database

```kotlin
@Dao
interface RssFeedDao {
    @Query("SELECT * FROM rss_feeds WHERE isActive = 1")
    fun getActiveFeeds(): Flow<List<RssFeed>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertFeed(feed: RssFeed)

    @Delete
    suspend fun deleteFeed(feed: RssFeed)

    @Query("UPDATE rss_feeds SET lastUpdated = :timestamp WHERE feedUrl = :url")
    suspend fun updateLastSync(url: String, timestamp: Long)
}

@Dao
interface RssItemDao {
    @Query("SELECT * FROM rss_items ORDER BY pubDate DESC LIMIT :limit")
    fun getRecentItems(limit: Int = 100): Flow<List<RssItem>>

    @Query("SELECT * FROM rss_items WHERE feedUrl = :feedUrl ORDER BY pubDate DESC")
    fun getItemsForFeed(feedUrl: String): Flow<List<RssItem>>

    @Query("SELECT * FROM rss_items WHERE isRead = 0 ORDER BY pubDate DESC")
    fun getUnreadItems(): Flow<List<RssItem>>

    @Query("SELECT * FROM rss_items WHERE isFavorite = 1 ORDER BY pubDate DESC")
    fun getFavoriteItems(): Flow<List<RssItem>>

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertItems(items: List<RssItem>): List<Long>

    @Query("UPDATE rss_items SET isRead = :isRead WHERE guid = :guid")
    suspend fun markAsRead(guid: String, isRead: Boolean = true)

    @Query("UPDATE rss_items SET isFavorite = :isFavorite WHERE guid = :guid")
    suspend fun toggleFavorite(guid: String, isFavorite: Boolean)

    @Query("DELETE FROM rss_items WHERE pubDate < :cutoffTime AND isFavorite = 0")
    suspend fun deleteOldItems(cutoffTime: Long)
}

@Database(entities = [RssFeed::class, RssItem::class], version = 1)
abstract class RssDatabase : RoomDatabase() {
    abstract fun feedDao(): RssFeedDao
    abstract fun itemDao(): RssItemDao
}
```

### 3. RSS Parser (Jsoup)

В реальном приложении обычно используют HTTP-клиент (например, OkHttp/Retrofit) и передают тело ответа в `Jsoup`; прямой вызов `Jsoup.connect` здесь приведён для простоты. Также стоит учитывать, что Jsoup оптимизирован для HTML и демонстрационный код не покрывает все варианты RSS/Atom-форматов — для продакшена лучше использовать полнофункциональный XML-парсер или специализированную RSS-библиотеку.

```kotlin
class RssParser {

    suspend fun parseFeed(feedUrl: String): Result<ParsedFeed> = withContext(Dispatchers.IO) {
        try {
            val doc = Jsoup.connect(feedUrl)
                .timeout(10_000)
                .get()

            // Извлекаем базовые метаданные канала
            val channel = doc.selectFirst("channel")
            val feedTitle = channel?.selectFirst("title")?.text().orEmpty()
            val feedDescription = channel?.selectFirst("description")?.text().orEmpty()

            val items = doc.select("item").map { element ->
                RssItem(
                    guid = element.selectFirst("guid")?.text()
                        ?.takeIf { it.isNotBlank() }
                        ?: element.selectFirst("link")?.text().orEmpty(),
                    feedUrl = feedUrl,
                    title = element.selectFirst("title")?.text().orEmpty(),
                    description = element.selectFirst("description")?.text()
                        ?.stripHtml().orEmpty(),
                    link = element.selectFirst("link")?.text().orEmpty(),
                    pubDate = parseDate(element.selectFirst("pubDate")?.text().orEmpty()),
                    author = element.select("author, dc|creator").text()
                        .ifBlank { null },
                    imageUrl = extractImageUrl(element)
                )
            }

            Result.success(
                ParsedFeed(
                    title = feedTitle,
                    description = feedDescription,
                    items = items
                )
            )
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private fun parseDate(dateString: String): Long {
        return try {
            if (dateString.isBlank()) return System.currentTimeMillis()
            val formatter = SimpleDateFormat("EEE, dd MMM yyyy HH:mm:ss Z", Locale.ENGLISH)
            formatter.parse(dateString)?.time ?: System.currentTimeMillis()
        } catch (e: Exception) {
            System.currentTimeMillis()
        }
    }

    private fun extractImageUrl(element: Element): String? {
        // Best-effort: распространённые RSS media-паттерны
        val fromMedia = element.select("media|content, enclosure[type^=image]")
            .attr("url")
        if (fromMedia.isNotBlank()) return fromMedia

        val desc = element.selectFirst("description")?.html().orEmpty()
        val fromDesc = Jsoup.parse(desc).selectFirst("img")?.attr("src").orEmpty()
        return fromDesc.ifBlank { null }
    }

    private fun String.stripHtml(): String = Jsoup.parse(this).text()
}

data class ParsedFeed(
    val title: String,
    val description: String,
    val items: List<RssItem>
)
```

### 4. Repository

```kotlin
class RssRepository(
    private val feedDao: RssFeedDao,
    private val itemDao: RssItemDao,
    private val parser: RssParser
) {
    val allFeeds: Flow<List<RssFeed>> = feedDao.getActiveFeeds()
    val recentItems: Flow<List<RssItem>> = itemDao.getRecentItems()
    val unreadItems: Flow<List<RssItem>> = itemDao.getUnreadItems()

    suspend fun addFeed(feedUrl: String): Result<RssFeed> {
        return parser.parseFeed(feedUrl).mapCatching { parsed ->
            val feed = RssFeed(
                feedUrl = feedUrl,
                title = parsed.title.ifBlank { feedUrl },
                description = parsed.description,
                lastUpdated = System.currentTimeMillis()
            )

            feedDao.insertFeed(feed)
            itemDao.insertItems(parsed.items)

            feed
        }
    }

    suspend fun refreshFeed(feedUrl: String): Result<Int> {
        return parser.parseFeed(feedUrl).mapCatching { parsed ->
            val inserted = itemDao.insertItems(parsed.items)
            feedDao.updateLastSync(feedUrl, System.currentTimeMillis())
            inserted.count { it != -1L } // количество успешно вставленных строк
        }
    }

    suspend fun refreshAllFeeds(): Result<Int> {
        val feeds = feedDao.getActiveFeeds().first()
        var totalNew = 0
        var hadFailure = false

        for (feed in feeds) {
            val result = refreshFeed(feed.feedUrl)
            result.onSuccess { count ->
                totalNew += count
            }.onFailure {
                hadFailure = true
            }
        }

        // Упрощённая стратегия: если хоть одна лента не обновилась — считаем, что операция неуспешна.
        // В продакшене можно возвращать частичный успех/детализированные ошибки.
        return if (hadFailure) Result.failure(IllegalStateException("Some feeds failed to refresh"))
        else Result.success(totalNew)
    }

    suspend fun markAsRead(itemGuid: String) {
        itemDao.markAsRead(itemGuid, true)
    }

    suspend fun toggleFavorite(itemGuid: String, isFavorite: Boolean) {
        itemDao.toggleFavorite(itemGuid, isFavorite)
    }

    suspend fun cleanupOldItems() {
        val cutoff = System.currentTimeMillis() - (30L * 24 * 60 * 60 * 1000L) // 30 дней
        itemDao.deleteOldItems(cutoff)
    }
}
```

### 5. WorkManager Для Фоновой Синхронизации

```kotlin
class RssSyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val repository = (applicationContext as MyApp).rssRepository

        return try {
            val newItemsCount = repository.refreshAllFeeds().getOrThrow()

            if (newItemsCount > 0) {
                showNotification(newItemsCount)
            }

            repository.cleanupOldItems()

            Result.success()
        } catch (e: Exception) {
            Log.e(TAG, "RSS sync failed", e)
            return Result.retry()
        }
    }

    private fun showNotification(count: Int) {
        val notification = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_rss)
            .setContentTitle("New RSS items")
            .setContentText("$count new items available")
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setAutoCancel(true)
            .build()

        NotificationManagerCompat.from(applicationContext)
            .notify(NOTIFICATION_ID, notification)
    }

    companion object {
        const val TAG = "RssSyncWorker"
        const val CHANNEL_ID = "rss_updates"
        const val NOTIFICATION_ID = 2001
    }
}

// Планирование периодической синхронизации
// Минимальный интервал для PeriodicWorkRequest — 15 минут;
// intervalHours должен соответствовать этому ограничению.
fun scheduleRssSync(context: Context, intervalHours: Long = 1) {
    val constraints = Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .build()

    val syncRequest = PeriodicWorkRequestBuilder<RssSyncWorker>(
        intervalHours, TimeUnit.HOURS
    )
        .setConstraints(constraints)
        .setBackoffCriteria(
            BackoffPolicy.EXPONENTIAL,
            WorkRequest.MIN_BACKOFF_MILLIS,
            TimeUnit.MILLISECONDS
        )
        .build()

    WorkManager.getInstance(context).enqueueUniquePeriodicWork(
        "rss_sync",
        ExistingPeriodicWorkPolicy.KEEP,
        syncRequest
    )
}
```

### 6. `ViewModel` + UI

```kotlin
@HiltViewModel
class RssViewModel @Inject constructor(
    private val repository: RssRepository
) : ViewModel() {

    val feeds = repository.allFeeds
        .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

    val items = repository.recentItems
        .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

    private val _isRefreshing = MutableStateFlow(false)
    val isRefreshing = _isRefreshing.asStateFlow()

    fun addFeed(url: String) {
        viewModelScope.launch {
            repository.addFeed(url)
            // Демонстрационно: ошибки не пробрасываются в UI.
        }
    }

    fun refreshAll() {
        viewModelScope.launch {
            _isRefreshing.value = true
            repository.refreshAllFeeds()
            _isRefreshing.value = false
            // Упрощение: результат и ошибки не отображаются в UI.
        }
    }

    fun markAsRead(itemGuid: String) {
        viewModelScope.launch {
            repository.markAsRead(itemGuid)
        }
    }

    fun toggleFavorite(itemGuid: String, isFavorite: Boolean) {
        viewModelScope.launch {
            repository.toggleFavorite(itemGuid, isFavorite)
        }
    }
}

@Composable
fun RssFeedScreen(viewModel: RssViewModel = hiltViewModel()) {
    val items by viewModel.items.collectAsState()
    val isRefreshing by viewModel.isRefreshing.collectAsState()

    SwipeRefresh(
        state = rememberSwipeRefreshState(isRefreshing),
        onRefresh = viewModel::refreshAll
    ) {
        LazyColumn {
            items(items, key = { it.guid }) { item ->
                RssItemCard(
                    item = item,
                    onMarkRead = { viewModel.markAsRead(item.guid) },
                    onToggleFavorite = { viewModel.toggleFavorite(item.guid, !item.isFavorite) }
                )
            }
        }
    }
}

@Composable
fun RssItemCard(
    item: RssItem,
    onMarkRead: () -> Unit,
    onToggleFavorite: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
            .clickable { onMarkRead() }
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = item.title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = if (item.isRead) FontWeight.Normal else FontWeight.Bold
            )

            Text(
                text = item.description,
                style = MaterialTheme.typography.bodySmall,
                maxLines = 3,
                overflow = TextOverflow.Ellipsis
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = formatDate(item.pubDate),
                    style = MaterialTheme.typography.labelSmall
                )

                IconButton(onClick = onToggleFavorite) {
                    Icon(
                        imageVector = if (item.isFavorite) {
                            Icons.Filled.Favorite
                        } else {
                            Icons.Outlined.FavoriteBorder
                        },
                        contentDescription = "Favorite"
                    )
                }
            }
        }
    }
}

fun formatDate(timestamp: Long): String {
    val date = Date(timestamp)
    val format = SimpleDateFormat("dd MMM yyyy HH:mm", Locale.getDefault())
    return format.format(date)
}
```

### Итог

RU: Архитектура RSS-агрегатора: Jsoup (в примере) для парсинга RSS/XML, Room для локального хранения (ленты и элементы с внешним ключом), WorkManager для периодической синхронизации (с учётом минимального интервала платформы), Repository для координации данных. Реактивный UI на основе `Flow`/`StateFlow`. Возможности: отметка как прочитано, избранное, swipe-to-refresh, очистка старых данных. Пример кода демонстрационный: обработка ошибок и ключи элементов могут быть доработаны в продакшене.

---

## Answer (EN)
An RSS aggregator fetches and displays feeds from multiple sources. Key requirements: XML (RSS/Atom) parsing, local storage, background sync, and notifications for new posts.

### Architecture

```

   UI Layer     Compose/XML + ViewModel



 Repository         Data coordination



 Network        Room      WorkManager
  (RSS)       Database      (Sync)

```

### 1. Data Models

```kotlin
// Entity for Room
@Entity(tableName = "rss_feeds")
data class RssFeed(
    @PrimaryKey val feedUrl: String,
    val title: String,
    val description: String,
    val lastUpdated: Long = 0L,
    val isActive: Boolean = true
)

@Entity(
    tableName = "rss_items",
    foreignKeys = [
        ForeignKey(
            entity = RssFeed::class,
            parentColumns = ["feedUrl"],
            childColumns = ["feedUrl"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("feedUrl")]
)
data class RssItem(
    // In production it's safer to include feedUrl in the key (guid + feedUrl)
    // to avoid collisions across different feeds.
    @PrimaryKey val guid: String,  // Unique ID from RSS or fallback: link/combination with feedUrl
    val feedUrl: String,
    val title: String,
    val description: String,
    val link: String,
    val pubDate: Long,
    val author: String? = null,
    val imageUrl: String? = null,
    val isRead: Boolean = false,
    val isFavorite: Boolean = false
)

// Relation for UI
data class FeedWithItems(
    @Embedded val feed: RssFeed,
    @Relation(
        parentColumn = "feedUrl",
        entityColumn = "feedUrl"
    )
    val items: List<RssItem>
)
```

### 2. Room Database

```kotlin
@Dao
interface RssFeedDao {
    @Query("SELECT * FROM rss_feeds WHERE isActive = 1")
    fun getActiveFeeds(): Flow<List<RssFeed>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertFeed(feed: RssFeed)

    @Delete
    suspend fun deleteFeed(feed: RssFeed)

    @Query("UPDATE rss_feeds SET lastUpdated = :timestamp WHERE feedUrl = :url")
    suspend fun updateLastSync(url: String, timestamp: Long)
}

@Dao
interface RssItemDao {
    @Query("SELECT * FROM rss_items ORDER BY pubDate DESC LIMIT :limit")
    fun getRecentItems(limit: Int = 100): Flow<List<RssItem>>

    @Query("SELECT * FROM rss_items WHERE feedUrl = :feedUrl ORDER BY pubDate DESC")
    fun getItemsForFeed(feedUrl: String): Flow<List<RssItem>>

    @Query("SELECT * FROM rss_items WHERE isRead = 0 ORDER BY pubDate DESC")
    fun getUnreadItems(): Flow<List<RssItem>>

    @Query("SELECT * FROM rss_items WHERE isFavorite = 1 ORDER BY pubDate DESC")
    fun getFavoriteItems(): Flow<List<RssItem>>

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertItems(items: List<RssItem>): List<Long>

    @Query("UPDATE rss_items SET isRead = :isRead WHERE guid = :guid")
    suspend fun markAsRead(guid: String, isRead: Boolean = true)

    @Query("UPDATE rss_items SET isFavorite = :isFavorite WHERE guid = :guid")
    suspend fun toggleFavorite(guid: String, isFavorite: Boolean)

    @Query("DELETE FROM rss_items WHERE pubDate < :cutoffTime AND isFavorite = 0")
    suspend fun deleteOldItems(cutoffTime: Long)
}

@Database(entities = [RssFeed::class, RssItem::class], version = 1)
abstract class RssDatabase : RoomDatabase() {
    abstract fun feedDao(): RssFeedDao
    abstract fun itemDao(): RssItemDao
}
```

### 3. RSS Parser (Jsoup)

Note: In a real app you would usually use an HTTP client (e.g., OkHttp/Retrofit) and feed Jsoup with the response body; direct `Jsoup.connect` is used here for brevity. Also, Jsoup is HTML-oriented; this sample does not cover all RSS/Atom edge cases and should be treated as illustrative. For production, prefer a robust XML parser or dedicated RSS library.

```kotlin
class RssParser {

    suspend fun parseFeed(feedUrl: String): Result<ParsedFeed> = withContext(Dispatchers.IO) {
        try {
            val doc = Jsoup.connect(feedUrl)
                .timeout(10_000)
                .get()

            // Extract basic channel metadata
            val channel = doc.selectFirst("channel")
            val feedTitle = channel?.selectFirst("title")?.text().orEmpty()
            val feedDescription = channel?.selectFirst("description")?.text().orEmpty()

            val items = doc.select("item").map { element ->
                RssItem(
                    guid = element.selectFirst("guid")?.text()
                        ?.takeIf { it.isNotBlank() }
                        ?: element.selectFirst("link")?.text().orEmpty(),
                    feedUrl = feedUrl,
                    title = element.selectFirst("title")?.text().orEmpty(),
                    description = element.selectFirst("description")?.text()
                        ?.stripHtml().orEmpty(),
                    link = element.selectFirst("link")?.text().orEmpty(),
                    pubDate = parseDate(element.selectFirst("pubDate")?.text().orEmpty()),
                    author = element.select("author, dc|creator").text()
                        .ifBlank { null },
                    imageUrl = extractImageUrl(element)
                )
            }

            Result.success(
                ParsedFeed(
                    title = feedTitle,
                    description = feedDescription,
                    items = items
                )
            )
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private fun parseDate(dateString: String): Long {
        return try {
            if (dateString.isBlank()) return System.currentTimeMillis()
            val formatter = SimpleDateFormat("EEE, dd MMM yyyy HH:mm:ss Z", Locale.ENGLISH)
            formatter.parse(dateString)?.time ?: System.currentTimeMillis()
        } catch (e: Exception) {
            System.currentTimeMillis()
        }
    }

    private fun extractImageUrl(element: Element): String? {
        // Best-effort: common RSS media patterns
        val fromMedia = element.select("media|content, enclosure[type^=image]")
            .attr("url")
        if (fromMedia.isNotBlank()) return fromMedia

        val desc = element.selectFirst("description")?.html().orEmpty()
        val fromDesc = Jsoup.parse(desc).selectFirst("img")?.attr("src").orEmpty()
        return fromDesc.ifBlank { null }
    }

    private fun String.stripHtml(): String = Jsoup.parse(this).text()
}

data class ParsedFeed(
    val title: String,
    val description: String,
    val items: List<RssItem>
)
```

### 4. Repository

```kotlin
class RssRepository(
    private val feedDao: RssFeedDao,
    private val itemDao: RssItemDao,
    private val parser: RssParser
) {
    val allFeeds: Flow<List<RssFeed>> = feedDao.getActiveFeeds()
    val recentItems: Flow<List<RssItem>> = itemDao.getRecentItems()
    val unreadItems: Flow<List<RssItem>> = itemDao.getUnreadItems()

    suspend fun addFeed(feedUrl: String): Result<RssFeed> {
        return parser.parseFeed(feedUrl).mapCatching { parsed ->
            val feed = RssFeed(
                feedUrl = feedUrl,
                title = parsed.title.ifBlank { feedUrl },
                description = parsed.description,
                lastUpdated = System.currentTimeMillis()
            )

            feedDao.insertFeed(feed)
            itemDao.insertItems(parsed.items)

            feed
        }
    }

    suspend fun refreshFeed(feedUrl: String): Result<Int> {
        return parser.parseFeed(feedUrl).mapCatching { parsed ->
            val inserted = itemDao.insertItems(parsed.items)
            feedDao.updateLastSync(feedUrl, System.currentTimeMillis())
            inserted.count { it != -1L } // count successfully inserted rows
        }
    }

    suspend fun refreshAllFeeds(): Result<Int> {
        val feeds = feedDao.getActiveFeeds().first()
        var totalNew = 0
        var hadFailure = false

        for (feed in feeds) {
            val result = refreshFeed(feed.feedUrl)
            result.onSuccess { count ->
                totalNew += count
            }.onFailure {
                hadFailure = true
            }
        }

        // Simplified strategy: treat any single-feed failure as overall failure.
        // In production you might want partial success reporting.
        return if (hadFailure) Result.failure(IllegalStateException("Some feeds failed to refresh"))
        else Result.success(totalNew)
    }

    suspend fun markAsRead(itemGuid: String) {
        itemDao.markAsRead(itemGuid, true)
    }

    suspend fun toggleFavorite(itemGuid: String, isFavorite: Boolean) {
        itemDao.toggleFavorite(itemGuid, isFavorite)
    }

    suspend fun cleanupOldItems() {
        val cutoff = System.currentTimeMillis() - (30L * 24 * 60 * 60 * 1000L) // 30 days
        itemDao.deleteOldItems(cutoff)
    }
}
```

### 5. WorkManager for Background Sync

```kotlin
class RssSyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val repository = (applicationContext as MyApp).rssRepository

        return try {
            val newItemsCount = repository.refreshAllFeeds().getOrThrow()

            if (newItemsCount > 0) {
                showNotification(newItemsCount)
            }

            repository.cleanupOldItems()

            Result.success()
        } catch (e: Exception) {
            Log.e(TAG, "RSS sync failed", e)
            return Result.retry()
        }
    }

    private fun showNotification(count: Int) {
        val notification = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_rss)
            .setContentTitle("New RSS items")
            .setContentText("$count new items available")
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setAutoCancel(true)
            .build()

        NotificationManagerCompat.from(applicationContext)
            .notify(NOTIFICATION_ID, notification)
    }

    companion object {
        const val TAG = "RssSyncWorker"
        const val CHANNEL_ID = "rss_updates"
        const val NOTIFICATION_ID = 2001
    }
}

// Periodic sync scheduling
// Minimum interval for PeriodicWorkRequest is 15 minutes;
// intervalHours should respect that constraint.
fun scheduleRssSync(context: Context, intervalHours: Long = 1) {
    val constraints = Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .build()

    val syncRequest = PeriodicWorkRequestBuilder<RssSyncWorker>(
        intervalHours, TimeUnit.HOURS
    )
        .setConstraints(constraints)
        .setBackoffCriteria(
            BackoffPolicy.EXPONENTIAL,
            WorkRequest.MIN_BACKOFF_MILLIS,
            TimeUnit.MILLISECONDS
        )
        .build()

    WorkManager.getInstance(context).enqueueUniquePeriodicWork(
        "rss_sync",
        ExistingPeriodicWorkPolicy.KEEP,
        syncRequest
    )
}
```

### 6. `ViewModel` + UI

```kotlin
@HiltViewModel
class RssViewModel @Inject constructor(
    private val repository: RssRepository
) : ViewModel() {

    val feeds = repository.allFeeds
        .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

    val items = repository.recentItems
        .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

    private val _isRefreshing = MutableStateFlow(false)
    val isRefreshing = _isRefreshing.asStateFlow()

    fun addFeed(url: String) {
        viewModelScope.launch {
            repository.addFeed(url)
            // Simplified: errors are not surfaced to UI.
        }
    }

    fun refreshAll() {
        viewModelScope.launch {
            _isRefreshing.value = true
            repository.refreshAllFeeds()
            _isRefreshing.value = false
            // Simplified: result/errors are ignored for brevity.
        }
    }

    fun markAsRead(itemGuid: String) {
        viewModelScope.launch {
            repository.markAsRead(itemGuid)
        }
    }

    fun toggleFavorite(itemGuid: String, isFavorite: Boolean) {
        viewModelScope.launch {
            repository.toggleFavorite(itemGuid, isFavorite)
        }
    }
}

@Composable
fun RssFeedScreen(viewModel: RssViewModel = hiltViewModel()) {
    val items by viewModel.items.collectAsState()
    val isRefreshing by viewModel.isRefreshing.collectAsState()

    SwipeRefresh(
        state = rememberSwipeRefreshState(isRefreshing),
        onRefresh = viewModel::refreshAll
    ) {
        LazyColumn {
            items(items, key = { it.guid }) { item ->
                RssItemCard(
                    item = item,
                    onMarkRead = { viewModel.markAsRead(item.guid) },
                    onToggleFavorite = { viewModel.toggleFavorite(item.guid, !item.isFavorite) }
                )
            }
        }
    }
}

@Composable
fun RssItemCard(
    item: RssItem,
    onMarkRead: () -> Unit,
    onToggleFavorite: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
            .clickable { onMarkRead() }
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = item.title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = if (item.isRead) FontWeight.Normal else FontWeight.Bold
            )

            Text(
                text = item.description,
                style = MaterialTheme.typography.bodySmall,
                maxLines = 3,
                overflow = TextOverflow.Ellipsis
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = formatDate(item.pubDate),
                    style = MaterialTheme.typography.labelSmall
                )

                IconButton(onClick = onToggleFavorite) {
                    Icon(
                        imageVector = if (item.isFavorite) {
                            Icons.Filled.Favorite
                        } else {
                            Icons.Outlined.FavoriteBorder
                        },
                        contentDescription = "Favorite"
                    )
                }
            }
        }
    }
}

fun formatDate(timestamp: Long): String {
    val date = Date(timestamp)
    val format = SimpleDateFormat("dd MMM yyyy HH:mm", Locale.getDefault())
    return format.format(date)
}
```

### Summary

English: RSS aggregator architecture: Jsoup (in this sample) for XML parsing, Room for local storage (feeds + items with relations), WorkManager for periodic sync (respecting the platform’s 15-minute minimum), Repository pattern for data coordination. Reactive UI with `Flow` + `StateFlow`. Features: mark as read, favorites, swipe-to-refresh, cleanup of old data. Sample code is illustrative; production code should improve error handling and item key strategy.

---

## Дополнительные Вопросы (RU)

- [[q-databases-android--android--easy]]
- [[q-how-to-choose-layout-for-fragment--android--easy]]
- [[q-webp-image-format-android--android--easy]]

## Follow-ups

- [[q-databases-android--android--easy]]
- [[q-how-to-choose-layout-for-fragment--android--easy]]
- [[q-webp-image-format-android--android--easy]]

## Ссылки (RU)

- [Подключение к сети](https://developer.android.com/training/basics/network-ops/connecting)
- [Room Database](https://developer.android.com/training/data-storage/room)

## References

- [Connecting to the Network](https://developer.android.com/training/basics/network-ops/connecting)
- [Room Database](https://developer.android.com/training/data-storage/room)

## Связанные Вопросы (RU)

### Предпосылки / Концепты

- [[c-retrofit]]
- [[c-room]]
- [[q-how-to-choose-layout-for-fragment--android--easy]]
- [[q-webp-image-format-android--android--easy]]
- [[q-databases-android--android--easy]]

## Related Questions

### Prerequisites / Concepts

- [[c-retrofit]]
- [[c-room]]
- [[q-how-to-choose-layout-for-fragment--android--easy]]
- [[q-webp-image-format-android--android--easy]]
- [[q-databases-android--android--easy]]
