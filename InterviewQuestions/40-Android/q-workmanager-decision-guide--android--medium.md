---
id: 20251017-144931
title: "Workmanager Decision Guide / Руководство по выбору WorkManager"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-api-rate-limiting-throttling--android--medium, q-compose-modifier-system--android--medium, q-databases-android--android--easy]
created: 2025-10-15
tags: [workmanager, background-work, coroutines, service, difficulty/medium]
---
# WorkManager vs Coroutines vs Service - Decision Guide

**English**: When should you use WorkManager vs Coroutines vs Service for background work?

## Answer (EN)

**WorkManager**, **Coroutines** и **Service** решают разные задачи фоновой работы в Android.

**WorkManager:** для отложенной гарантированной работы (загрузка файлов, синхронизация данных, аналитика, периодические задачи >= 15 мин). Гарантии: переживёт закрытие приложения, device reboot, автоматический retry, battery-эффективность. Поддержка: constraints (WiFi, charging), backoff policies, chaining, progress tracking.

**Coroutines:** для async операций во время работы приложения (загрузка данных для UI, network запросы, database операции, Flow-based real-time данных). Ограничения: отменяются при закрытии приложения, не переживут process death, нет retry/backoff, нет constraints.

**Foreground Service:** для long-running user-visible работы (music player, location tracking, fitness tracking, VoIP, active downloads). Требования: обязательно показывать notification, пользователь видит что работает, может работать при закрытом приложении.

**Правила выбора:** нужна гарантия после закрытия → WorkManager. Нужен немедленный результат для UI → Coroutines. Нужна user-visible long-running работа → Foreground Service. Периодические задачи: <15min → Coroutines, >=15min → WorkManager.

## Ответ (RU)

**WorkManager**, **Coroutines** и **Service** решают разные задачи фоновой работы:

| Критерий | WorkManager | Coroutines | Service (Foreground) |
|----------|-------------|------------|---------------------|
| **Гарантия выполнения** | - Да, даже после reboot | - Нет | WARNING: Пока процесс жив |
| **Работает при закрытом приложении** | - Да | - Нет | WARNING: Foreground - да |
| **Constraints** (WiFi, charging) | - Да | - Нет | - Нет |
| **Retry/backoff** | - Автоматически | - Вручную | - Вручную |
| **Периодические задачи** | - Да (min 15 min) | - Нет | WARNING: Вручную |
| **Use case** | Deferrable гарантированная работа | Async операции в UI | Long-running foreground |

### When to Use WorkManager

```kotlin
// - Загрузка файлов - должна завершиться
class UploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val fileUri = inputData.getString("file_uri") ?: return Result.failure()

        return try {
            uploadFile(fileUri)
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry() // Автоматический retry
            } else {
                Result.failure()
            }
        }
    }
}

// Запуск с constraints
fun scheduleUpload(fileUri: String) {
    val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>()
        .setInputData(workDataOf("file_uri" to fileUri))
        .setConstraints(
            Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED) // WiFi/Mobile
                .setRequiresBatteryNotLow(true)                // Battery > 15%
                .build()
        )
        .setBackoffCriteria(
            BackoffPolicy.EXPONENTIAL,
            15,
            TimeUnit.SECONDS
        )
        .build()

    WorkManager.getInstance(context).enqueue(uploadRequest)
}
```

**Используйте WorkManager для**:
-  Загрузка файлов/данных (upload)
-  Синхронизация данных с сервером
-  Отправка аналитики/логов
-  Очистка кэша/старых данных
-  Обработка/сжатие изображений
-  Периодические задачи (sync каждые N часов)

**Гарантии WorkManager**:
- - Выполнится даже если приложение закрыто
- - Переживет reboot устройства
- - Автоматические retry при сбое
- - Батарейно-эффективно (соблюдает Doze Mode)

### When to Use Coroutines

```kotlin
class ProductsViewModel(
    private val repository: ProductsRepository
) : ViewModel() {

    // - Загрузка данных для UI
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

    // - Параллельные запросы
    suspend fun loadDashboard() = coroutineScope {
        val products = async { repository.getProducts() }
        val orders = async { repository.getOrders() }
        val stats = async { repository.getStats() }

        DashboardData(
            products = products.await(),
            orders = orders.await(),
            stats = stats.await()
        )
    }

    // - Flow для real-time данных
    val orders: StateFlow<List<Order>> = repository.observeOrders()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )
}
```

**Используйте Coroutines для**:
-  Загрузка данных для UI
-  Async операции во время работы приложения
-  Network запросы для экрана
-  Database операции
-  Flow-based real-time данных
-  Любая работа привязанная к lifecycle компонента

**Ограничения Coroutines**:
- - Отменяются при закрытии приложения
- - Не переживут process death
- - Нет retry/backoff из коробки
- - Нет constraints (WiFi, charging)

### When to Use Foreground Service

```kotlin
class MusicPlayerService : Service() {

    override fun onCreate() {
        super.onCreate()
        startForeground(NOTIFICATION_ID, createNotification())
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_PLAY -> play()
            ACTION_PAUSE -> pause()
            ACTION_STOP -> stopSelf()
        }
        return START_STICKY
    }

    private fun play() {
        // Долгоиграющая работа с постоянным уведомлением
        mediaPlayer.start()
    }

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Now Playing")
            .setContentText(currentSong.title)
            .setSmallIcon(R.drawable.ic_music)
            .addAction(R.drawable.ic_pause, "Pause", pausePendingIntent)
            .build()
    }
}

// Запуск
fun startMusicPlayer() {
    val intent = Intent(context, MusicPlayerService::class.java).apply {
        action = ACTION_PLAY
    }
    ContextCompat.startForegroundService(context, intent)
}
```

**Используйте Foreground Service для**:
-  Music/audio player
-  Location tracking
-  Fitness tracking
-  VoIP calls
-  Active downloads с прогрессом
-  Video recording

**Требования Foreground Service**:
- - **ОБЯЗАТЕЛЬНО** показывать notification
- WARNING: Пользователь видит что приложение работает
- - Может работать пока приложение закрыто
- WARNING: Система может убить при низкой памяти

### Comparison with Examples

#### Example 1: File Upload

```kotlin
// - НЕПРАВИЛЬНО - Coroutines
// Проблема: отменится при закрытии приложения
fun uploadFile(file: File) {
    viewModelScope.launch {
        uploadToServer(file) // Может не завершиться!
    }
}

// - ПРАВИЛЬНО - WorkManager
// Гарантия: загрузка завершится даже если приложение закрыто
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

#### Example 2: Periodic Synchronization

```kotlin
// - НЕПРАВИЛЬНО - Coroutines с while loop
// Проблема: убьется при закрытии приложения
fun startSync() {
    viewModelScope.launch {
        while (isActive) {
            syncData()
            delay(3600_000) // Каждый час
        }
    }
}

// - ПРАВИЛЬНО - WorkManager
// Гарантия: будет работать в background
fun schedulePeriodicSync() {
    val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(
        1, TimeUnit.HOURS // Минимум 15 минут!
    )
        .setConstraints(
            Constraints.Builder()
                .setRequiredNetworkType(NetworkType.UNMETERED) // WiFi only
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

#### Example 3: Music Player

```kotlin
// - НЕПРАВИЛЬНО - WorkManager
// Проблема: WorkManager для deferrable работы, не для long-running
fun playMusic() {
    val playWork = OneTimeWorkRequestBuilder<MusicWorker>().build()
    WorkManager.getInstance(context).enqueue(playWork)
}

// - ПРАВИЛЬНО - Foreground Service
// Пользователь видит что музыка играет
class MusicPlayerService : Service() {
    override fun onCreate() {
        super.onCreate()
        startForeground(NOTIFICATION_ID, createNotification())
    }

    fun play() {
        mediaPlayer.start()
        updateNotification("Now Playing: ${currentSong.title}")
    }
}
```

#### Example 4: Loading Data for UI

```kotlin
// - НЕПРАВИЛЬНО - WorkManager
// Проблема: overkill для UI данных
fun loadProducts() {
    val loadWork = OneTimeWorkRequestBuilder<LoadProductsWorker>().build()
    WorkManager.getInstance(context).enqueue(loadWork)
    // Как получить результат для UI?
}

// - ПРАВИЛЬНО - Coroutines
fun loadProducts() {
    viewModelScope.launch {
        _isLoading.value = true
        val products = repository.getProducts()
        _products.value = products
        _isLoading.value = false
    }
}
```

### Combining Approaches

```kotlin
class DataSyncManager(
    private val context: Context,
    private val repository: DataRepository
) {
    // 1. Immediate sync - Coroutines
    suspend fun syncNow() {
        withContext(Dispatchers.IO) {
            val data = fetchFromServer()
            repository.save(data)
        }
    }

    // 2. Delayed guaranteed sync - WorkManager
    fun scheduleSyncWhenOnline() {
        val syncWork = OneTimeWorkRequestBuilder<SyncWorker>()
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build()
            )
            .setInitialDelay(1, TimeUnit.HOURS)
            .build()

        WorkManager.getInstance(context).enqueue(syncWork)
    }

    // 3. Periodic sync - WorkManager
    fun schedulePeriodicSync() {
        val periodicSync = PeriodicWorkRequestBuilder<SyncWorker>(
            6, TimeUnit.HOURS
        ).build()

        WorkManager.getInstance(context).enqueueUniquePeriodicWork(
            "periodic_sync",
            ExistingPeriodicWorkPolicy.KEEP,
            periodicSync
        )
    }
}

// ViewModel использует immediate sync
class DashboardViewModel(
    private val syncManager: DataSyncManager
) : ViewModel() {
    fun refresh() {
        viewModelScope.launch {
            syncManager.syncNow() // Coroutines для UI
        }
    }
}

// Application запускает periodic sync
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        syncManager.schedulePeriodicSync() // WorkManager для background
    }
}
```

### WorkManager Best Practices

```kotlin
// - Unique work - предотвращает дубликаты
fun scheduleUpload(fileId: String) {
    val uploadWork = OneTimeWorkRequestBuilder<UploadWorker>()
        .setInputData(workDataOf("file_id" to fileId))
        .build()

    WorkManager.getInstance(context).enqueueUniqueWork(
        "upload_$fileId",
        ExistingWorkPolicy.KEEP, // Не запускать если уже идет
        uploadWork
    )
}

// - Chaining - последовательная работа
fun processAndUpload(imageUri: String) {
    val compressWork = OneTimeWorkRequestBuilder<CompressImageWorker>()
        .setInputData(workDataOf("image_uri" to imageUri))
        .build()

    val uploadWork = OneTimeWorkRequestBuilder<UploadWorker>()
        .build()

    WorkManager.getInstance(context)
        .beginWith(compressWork)
        .then(uploadWork)
        .enqueue()
}

// - Observing work status
fun observeUploadStatus(workId: UUID) {
    WorkManager.getInstance(context)
        .getWorkInfoByIdLiveData(workId)
        .observe(lifecycleOwner) { workInfo ->
            when (workInfo.state) {
                WorkInfo.State.SUCCEEDED -> showSuccess()
                WorkInfo.State.FAILED -> showError()
                WorkInfo.State.RUNNING -> showProgress(workInfo.progress)
                else -> {}
            }
        }
}

// - Progress updates
class UploadWorker(context: Context, params: WorkerParameters) :
    CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val total = 100
        for (i in 1..total) {
            uploadChunk(i)

            // Обновляем прогресс
            setProgress(workDataOf("progress" to i))
        }

        return Result.success()
    }
}
```

### Coroutines Best Practices

```kotlin
// - Используйте правильный scope
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch { // Автоматически отменится
            repository.getData()
        }
    }
}

// - withContext для смены диспетчера
suspend fun loadFromDisk() {
    withContext(Dispatchers.IO) {
        file.readText()
    }
}

// - Обрабатывайте ошибки
viewModelScope.launch {
    try {
        val data = repository.getData()
        _data.value = data
    } catch (e: Exception) {
        _error.value = e.message
    }
}

// - async для параллельных операций
suspend fun loadMultiple() = coroutineScope {
    val user = async { userRepo.getUser() }
    val posts = async { postsRepo.getPosts() }

    UserData(user.await(), posts.await())
}
```

### Service Best Practices

```kotlin
// - Всегда используйте Foreground для long-running
class TrackingService : Service() {
    override fun onCreate() {
        super.onCreate()
        startForeground(NOTIFICATION_ID, createNotification())
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START -> startTracking()
            ACTION_STOP -> stopSelf()
        }
        return START_STICKY // Restart после kill
    }

    private fun startTracking() {
        serviceScope.launch {
            while (isActive) {
                val location = getLocation()
                sendToServer(location)
                delay(5000)
            }
        }
    }

    override fun onDestroy() {
        serviceScope.cancel()
        super.onDestroy()
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

### Migration Examples

```kotlin
// Было: AsyncTask (deprecated)
class DownloadTask : AsyncTask<String, Int, File>() {
    override fun doInBackground(vararg params: String): File {
        return downloadFile(params[0])
    }

    override fun onPostExecute(result: File) {
        updateUI(result)
    }
}

// Стало: Coroutines для UI
fun downloadForUI(url: String) {
    viewModelScope.launch {
        val file = withContext(Dispatchers.IO) {
            downloadFile(url)
        }
        updateUI(file)
    }
}

// Или WorkManager для guaranteed
fun downloadInBackground(url: String) {
    val downloadWork = OneTimeWorkRequestBuilder<DownloadWorker>()
        .setInputData(workDataOf("url" to url))
        .build()
    WorkManager.getInstance(context).enqueue(downloadWork)
}
```

**English**: **WorkManager**, **Coroutines**, and **Services** solve different background work needs:

**WorkManager**: For **deferrable guaranteed work**. Use for: file uploads, data sync, analytics, periodic tasks (min 15 min), cache cleanup. Guarantees: survives app closure, device reboot, automatic retry, battery-efficient. Supports: constraints (WiFi, charging), backoff policies, chaining, progress tracking.

**Coroutines**: For **async operations during app lifetime**. Use for: UI data loading, network requests for screens, database operations, Flow-based real-time data, lifecycle-bound work. Limitations: cancelled when app closes, no retry/backoff, no constraints, doesn't survive process death.

**Foreground Service**: For **long-running user-visible work**. Use for: music player, location tracking, fitness tracking, VoIP, active downloads. Requirements: must show notification, user sees it's running, can work when app closed, system may kill under low memory.

**Decision rules**: Need guaranteed execution after app closes → WorkManager. Need immediate UI result → Coroutines. Need user-visible long-running work → Foreground Service. Periodic tasks: <15min use Coroutines, ≥15min use WorkManager.

**Common mistakes**: Using Coroutines for uploads (won't complete if app closes). Using WorkManager for UI data (overkill). Using WorkManager for music player (use Foreground Service). Not using constraints with WorkManager.


---

## Related Questions

### Prerequisites (Easier)
- [[q-why-separate-ui-and-business-logic--android--easy]] - Ui
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - Ui
- [[q-recyclerview-sethasfixedsize--android--easy]] - Ui

### Related (Medium)
- [[q-dagger-build-time-optimization--android--medium]] - Ui
- q-rxjava-pagination-recyclerview--android--medium - Ui
- [[q-build-optimization-gradle--android--medium]] - Ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Ui
- [[q-testing-compose-ui--android--medium]] - Ui
