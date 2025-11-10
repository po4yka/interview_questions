---
id: kotlin-168
title: "Using CoroutineWorker with WorkManager / Использование CoroutineWorker с WorkManager"
aliases: [Background Work, CoroutineWorker, CoroutineWorker Background, WorkManager]
topic: kotlin
subtopics: [coroutines]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-workmanager, c-coroutines, q-what-is-coroutine--kotlin--easy]
created: 2025-10-15
updated: 2025-11-09
tags: [android, background, constraints, coroutines, coroutineworker, difficulty/medium, kotlin, periodic-work, worker, workmanager]
---

# Вопрос (RU)
> Что такое CoroutineWorker в Android WorkManager и чем он отличается от Worker и RxWorker? Когда следует использовать WorkManager с корутинами, а когда запускать корутины напрямую? Приведите production-примеры синхронизации данных, загрузки файлов и периодической очистки с обработкой ошибок, обновлениями прогресса и стратегиями тестирования.

# Question (EN)
> What is CoroutineWorker in Android WorkManager and how does it differ from Worker and RxWorker? When should you use WorkManager with coroutines versus launching coroutines directly? Provide production examples of data synchronization, file uploads, and periodic cleanup tasks with proper error handling, progress updates, and testing strategies.

## Ответ (RU)

**CoroutineWorker** — это coroutine-friendly реализация Worker из WorkManager, которая позволяет писать фоновую работу, используя suspend-функции вместо блокирующих операций.

#### 1. Основы CoroutineWorker

**Что такое CoroutineWorker?**

CoroutineWorker специально разработан для работы с Kotlin Coroutines:
- `doWork()` — это **suspend-функция**
- Корректно интегрируется с coroutine scope, управляемым WorkManager
- Учитывает отмену через `Job`
- Хорошо сочетается со структурированной конкурентностью

**Структура класса:**

```kotlin
import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import kotlinx.coroutines.delay

class MyCoroutineWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            performWork()
            Result.success()
        } catch (e: Exception) {
            Result.failure()
        }
    }

    private suspend fun performWork() {
        delay(1000)
    }
}
```

#### 2. Сравнение типов Worker

```kotlin
import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.RxWorker
import androidx.work.Worker
import androidx.work.WorkerParameters
import io.reactivex.Single
import java.util.concurrent.TimeUnit
import kotlinx.coroutines.delay

// 1. Worker (традиционный блокирующий)
class BlockingWorker(context: Context, params: WorkerParameters)
    : Worker(context, params) {

    override fun doWork(): Result {
        Thread.sleep(1000) // Блокирующий вызов
        return Result.success()
    }
}

// 2. CoroutineWorker (на основе корутин)
class CoroutineBasedWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        delay(1000) // Неблокирующая приостановка
        return Result.success()
    }
}

// 3. RxWorker (на основе RxJava)
class RxBasedWorker(context: Context, params: WorkerParameters)
    : RxWorker(context, params) {

    override fun createWork(): Single<Result> {
        return Single.just(Result.success())
            .delay(1, TimeUnit.SECONDS)
    }
}
```

**Таблица сравнения:**

| Характеристика | Worker | CoroutineWorker | RxWorker |
|----------------|--------|-----------------|----------|
| Выполнение | Блокирующий поток | Suspend (неблокирующий) | Реактивный поток |
| Отмена | Ручная/кооперативная | Через `Job` | Через `Disposable` |
| API | Синхронный | Корутинный | RxJava |
| Тестирование | Простое | TestDispatcher / TestWorker | TestScheduler |
| Современность | Менее предпочтителен | Рекомендуется | Для существующего Rx-кода |
| Лучше для | Простой блокирующий I/O | Современные Kotlin-приложения | Наследуемый Rx-код |

#### 3. Когда использовать WorkManager vs прямые корутины

```kotlin
import android.content.Context
import androidx.work.*
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch

// ИСПОЛЬЗУЙТЕ WorkManager + CoroutineWorker, когда:

// 1. Работа должна пережить смерть процесса и перезапуск приложения
class DataSyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        syncDataWithServer()
        return Result.success()
    }

    private suspend fun syncDataWithServer() {
        // Реализация
    }
}

// 2. Нужны гарантированное выполнение и retry/backoff
val workRequest = OneTimeWorkRequestBuilder<DataSyncWorker>()
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,
        WorkRequest.MIN_BACKOFF_MILLIS,
        TimeUnit.MILLISECONDS
    )
    .build()

// 3. Нужны ограничения (сеть, заряд и т.д.)
val constrainedWork = OneTimeWorkRequestBuilder<UploadWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.UNMETERED)
            .setRequiresCharging(true)
            .build()
    )
    .build()

// 4. Периодические задачи
val periodicWork = PeriodicWorkRequestBuilder<CleanupWorker>(
    repeatInterval = 1,
    repeatIntervalTimeUnit = TimeUnit.DAYS
).build()

// НЕ используйте WorkManager, когда:

// 1. Нужен немедленный запуск (используйте обычные корутины)
fun loadUserProfileImmediate(scope: CoroutineScope) {
    scope.launch {
        loadUserProfile()
    }
}

// 2. Работа привязана к жизненному циклу UI
fun updateUiScoped(scope: CoroutineScope) {
    scope.launch {
        updateUI()
    }
}

// 3. Нужны обновления в реальном времени
fun observeMessages() = kotlinx.coroutines.flow.channelFlow {
    // Real-time сообщения — не задача для WorkManager
    websocket.collect { message ->
        send(message)
    }
}
```

**Когда использовать что:**

| Сценарий | Решение | Причина |
|----------|---------|--------|
| Загрузка файла в фоне | WorkManager | Переживает смерть процесса, учитывает ограничения |
| Загрузка данных для экрана | `ViewModel` + корутина | Привязано к lifecycle |
| Периодическая очистка | WorkManager | Планирование, устойчивость |
| Чат в реальном времени | Корутина + `Flow` | Нужны немедленные обновления |
| Миграция БД | WorkManager | Длительная, должна завершиться |
| API-вызов по нажатию кнопки | `ViewModel` + корутина | Немедленно, отменяемо |

#### 4. Production-пример: Data Sync Worker

```kotlin
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.work.*
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import java.util.UUID
import java.util.concurrent.TimeUnit

class DataSyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    companion object {
        const val KEY_SYNC_TYPE = "sync_type"
        const val KEY_USER_ID = "user_id"
        const val KEY_PROGRESS = "progress"
        const val KEY_PROGRESS_TAG = "progress_tag"
        const val TAG_SYNC = "data_sync"
        private const val NOTIFICATION_ID = 1001
        private const val CHANNEL_ID = "sync_channel"

        fun scheduleSyncWork(
            context: Context,
            syncType: String,
            userId: String
        ): UUID {
            val inputData = workDataOf(
                KEY_SYNC_TYPE to syncType,
                KEY_USER_ID to userId
            )

            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .setRequiresBatteryNotLow(true)
                .build()

            val syncRequest = OneTimeWorkRequestBuilder<DataSyncWorker>()
                .setInputData(inputData)
                .setConstraints(constraints)
                .setBackoffCriteria(
                    BackoffPolicy.EXPONENTIAL,
                    WorkRequest.MIN_BACKOFF_MILLIS,
                    TimeUnit.MILLISECONDS
                )
                .addTag(TAG_SYNC)
                .build()

            WorkManager.getInstance(context).enqueueUniqueWork(
                "sync_$userId",
                ExistingWorkPolicy.REPLACE,
                syncRequest
            )

            return syncRequest.id
        }
    }

    override suspend fun doWork(): Result {
        val syncType = inputData.getString(KEY_SYNC_TYPE) ?: return Result.failure()
        val userId = inputData.getString(KEY_USER_ID) ?: return Result.failure()

        return try {
            setForeground(getForegroundInfo())
            performSync(syncType, userId)
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure(
                    workDataOf("error" to (e.message ?: "unknown error"))
                )
            }
        }
    }

    private suspend fun performSync(syncType: String, userId: String) {
        val repository = DataRepository() // В реальном приложении — через DI

        when (syncType) {
            "full" -> syncFullData(repository, userId)
            "incremental" -> syncIncrementalData(repository, userId)
            else -> throw IllegalArgumentException("Unknown sync type: $syncType")
        }
    }

    private suspend fun syncFullData(repository: DataRepository, userId: String) {
        val steps = listOf("users", "posts", "comments", "media")

        steps.forEachIndexed { index, step ->
            if (isStopped) throw CancellationException("Work cancelled")

            setProgressAsync(
                workDataOf(
                    KEY_PROGRESS to ((index + 1) * 100 / steps.size)
                )
            )

            when (step) {
                "users" -> repository.syncUsers(userId)
                "posts" -> repository.syncPosts(userId)
                "comments" -> repository.syncComments(userId)
                "media" -> repository.syncMedia(userId)
            }
        }
    }

    private suspend fun syncIncrementalData(repository: DataRepository, userId: String) {
        val lastSyncTime = repository.getLastSyncTime(userId)
        repository.syncChangesSince(userId, lastSyncTime)
        repository.updateLastSyncTime(userId, System.currentTimeMillis())
    }

    override suspend fun getForegroundInfo(): ForegroundInfo {
        createChannelIfNeeded()

        val notification = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setContentTitle("Syncing data")
            .setContentText("Synchronizing your data in the background")
            .setSmallIcon(R.drawable.ic_sync)
            .setOngoing(true)
            .build()

        return ForegroundInfo(NOTIFICATION_ID, notification)
    }

    private fun createChannelIfNeeded() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val manager = applicationContext
                .getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            if (manager.getNotificationChannel(CHANNEL_ID) == null) {
                val channel = NotificationChannel(
                    CHANNEL_ID,
                    "Data sync",
                    NotificationManager.IMPORTANCE_LOW
                )
                manager.createNotificationChannel(channel)
            }
        }
    }
}

class DataRepository {
    suspend fun syncUsers(userId: String) = withContext(Dispatchers.IO) { delay(500) }
    suspend fun syncPosts(userId: String) = withContext(Dispatchers.IO) { delay(500) }
    suspend fun syncComments(userId: String) = withContext(Dispatchers.IO) { delay(500) }
    suspend fun syncMedia(userId: String) = withContext(Dispatchers.IO) { delay(500) }

    suspend fun getLastSyncTime(userId: String): `Long` = withContext(Dispatchers.IO) {
        System.currentTimeMillis() - 3600000
    }

    suspend fun syncChangesSince(userId: String, timestamp: `Long`) =
        withContext(Dispatchers.IO) { delay(1000) }

    suspend fun updateLastSyncTime(userId: String, timestamp: `Long`) =
        withContext(Dispatchers.IO) { }
}
```

#### 5. Worker загрузки файлов с прогрессом

```kotlin
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.net.Uri
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.work.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody
import okio.BufferedSink
import java.io.File
import java.io.IOException
import java.util.UUID

class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    companion object {
        const val KEY_FILE_URI = "file_uri"
        const val KEY_UPLOAD_URL = "upload_url"
        const val KEY_PROGRESS = "progress"
        const val KEY_UPLOADED_BYTES = "uploaded_bytes"
        const val KEY_TOTAL_BYTES = "total_bytes"
        private const val NOTIFICATION_ID = 1002
        private const val CHANNEL_ID = "upload_channel"

        fun uploadFile(
            context: Context,
            fileUri: Uri,
            uploadUrl: String
        ): UUID {
            val inputData = workDataOf(
                KEY_FILE_URI to fileUri.toString(),
                KEY_UPLOAD_URL to uploadUrl
            )

            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.UNMETERED)
                .build()

            val uploadRequest = OneTimeWorkRequestBuilder<FileUploadWorker>()
                .setInputData(inputData)
                .setConstraints(constraints)
                .build()

            WorkManager.getInstance(context).enqueue(uploadRequest)

            return uploadRequest.id
        }
    }

    override suspend fun doWork(): Result {
        val fileUriString = inputData.getString(KEY_FILE_URI) ?: return Result.failure()
        val uploadUrl = inputData.getString(KEY_UPLOAD_URL) ?: return Result.failure()

        return try {
            val fileUri = Uri.parse(fileUriString)
            val file = getFileFromUri(fileUri)

            setForeground(getForegroundInfo())

            uploadFileWithProgress(file, uploadUrl)

            Result.success(workDataOf("uploaded_file" to file.name))
        } catch (e: IOException) {
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure(workDataOf("error" to (e.message ?: "upload failed")))
            }
        }
    }

    private suspend fun uploadFileWithProgress(
        file: File,
        uploadUrl: String
    ) = withContext(Dispatchers.IO) {
        val client = OkHttpClient()

        val requestBody = object : RequestBody() {
            override fun contentType() = "application/octet-stream".toMediaType()
            override fun contentLength() = file.length()

            override fun writeTo(sink: BufferedSink) {
                val fileSize = file.length().coerceAtLeast(1L)
                var uploadedBytes = 0L

                file.inputStream().use { inputStream ->
                    val buffer = ByteArray(8192)
                    var bytesRead: Int

                    while (inputStream.read(buffer).also { bytesRead = it } != -1) {
                        if (isStopped) throw IOException("Загрузка отменена")

                        sink.write(buffer, 0, bytesRead)
                        uploadedBytes += bytesRead

                        val progress = (uploadedBytes * 100 / fileSize).toInt()
                        setProgressAsync(
                            workDataOf(
                                KEY_PROGRESS to progress,
                                KEY_UPLOADED_BYTES to uploadedBytes,
                                KEY_TOTAL_BYTES to fileSize
                            )
                        )
                    }
                }
            }
        }

        val request = Request.Builder()
            .url(uploadUrl)
            .post(requestBody)
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IOException("Upload failed: ${response.code}")
            }
        }
    }

    private fun getFileFromUri(uri: Uri): File {
        // В реальном приложении: разрешить/copy content:// URI в файл-кеш
        return File(requireNotNull(uri.path))
    }

    override suspend fun getForegroundInfo(): ForegroundInfo {
        createChannelIfNeeded()

        val notification = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setContentTitle("Загрузка файла")
            .setContentText("Загрузка в процессе")
            .setSmallIcon(R.drawable.ic_upload)
            .setProgress(100, 0, true)
            .setOngoing(true)
            .build()

        return ForegroundInfo(NOTIFICATION_ID, notification)
    }

    private fun createChannelIfNeeded() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val manager = applicationContext
                .getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            if (manager.getNotificationChannel(CHANNEL_ID) == null) {
                val channel = NotificationChannel(
                    CHANNEL_ID,
                    "File uploads",
                    NotificationManager.IMPORTANCE_LOW
                )
                manager.createNotificationChannel(channel)
            }
        }
    }
}
```

#### 6. Периодический Worker очистки

```kotlin
import android.content.Context
import androidx.work.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import java.io.File
import java.util.concurrent.TimeUnit

class CleanupWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    companion object {
        fun schedulePeriodicCleanup(context: Context) {
            val cleanupRequest = PeriodicWorkRequestBuilder<CleanupWorker>(
                repeatInterval = 1,
                repeatIntervalTimeUnit = TimeUnit.DAYS
            )
                .setConstraints(
                    Constraints.Builder()
                        .setRequiresCharging(true)
                        .setRequiresBatteryNotLow(true)
                        .build()
                )
                .setInitialDelay(1, TimeUnit.HOURS)
                .build()

            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                "periodic_cleanup",
                ExistingPeriodicWorkPolicy.KEEP,
                cleanupRequest
            )
        }
    }

    override suspend fun doWork(): Result {
        return try {
            performCleanup()
            Result.success()
        } catch (e: Exception) {
            Result.failure()
        }
    }

    private suspend fun performCleanup() = withContext(Dispatchers.IO) {
        cleanCacheDirectory()
        deleteOldTempFiles()
        vacuumDatabase()
        clearOldLogs()
    }

    private fun cleanCacheDirectory() {
        val cacheDir = applicationContext.cacheDir
        val maxCacheSize = 50 * 1024 * 1024 // 50 МБ

        fun currentSize(): Long = cacheDir.walkTopDown()
            .filter { it.isFile }
            .map { it.length() }
            .sum()

        var size = currentSize()
        if (size > maxCacheSize) {
            cacheDir.walkTopDown()
                .filter { it.isFile }
                .sortedBy { it.lastModified() }
                .forEach { file ->
                    if (size <= maxCacheSize) return
                    val len = file.length()
                    if (file.delete()) size -= len
                }
        }
    }

    private fun deleteOldTempFiles() {
        val tempDir = File(applicationContext.cacheDir, "temp")
        val maxAge = System.currentTimeMillis() - TimeUnit.DAYS.toMillis(7)

        if (tempDir.exists()) {
            tempDir.walkTopDown()
                .filter { it.isFile && it.lastModified() < maxAge }
                .forEach { it.delete() }
        }
    }

    private suspend fun vacuumDatabase() {
        delay(1000) // Заглушка для VACUUM
    }

    private fun clearOldLogs() {
        val logDir = File(applicationContext.filesDir, "logs")
        val maxAge = System.currentTimeMillis() - TimeUnit.DAYS.toMillis(30)

        if (logDir.exists()) {
            logDir.walkTopDown()
                .filter { it.isFile && it.lastModified() < maxAge }
                .forEach { it.delete() }
        }
    }
}
```

#### 7. Цепочка Workers (Chaining Workers)

```kotlin
import android.content.Context
import androidx.work.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext

fun chainedWorkExample(context: Context) {
    val downloadWork = OneTimeWorkRequestBuilder<DownloadWorker>()
        .setInputData(workDataOf("url" to "https://api.example.com/data"))
        .build()

    val processWork = OneTimeWorkRequestBuilder<ProcessWorker>()
        .build()

    val uploadWork = OneTimeWorkRequestBuilder<UploadWorker>()
        .build()

    WorkManager.getInstance(context)
        .beginWith(downloadWork)
        .then(processWork)
        .then(uploadWork)
        .enqueue()
}

class DownloadWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val url = inputData.getString("url") ?: return Result.failure()

        return try {
            val data = downloadData(url)
            Result.success(workDataOf("downloaded_data" to data))
        } catch (e: Exception) {
            Result.failure()
        }
    }

    private suspend fun downloadData(url: String): String = withContext(Dispatchers.IO) {
        delay(1000)
        "downloaded_data_content"
    }
}

class ProcessWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val data = inputData.getString("downloaded_data") ?: return Result.failure()

        return try {
            val processed = processData(data)
            Result.success(workDataOf("processed_data" to processed))
        } catch (e: Exception) {
            Result.failure()
        }
    }

    private suspend fun processData(data: String): String = withContext(Dispatchers.Default) {
        delay(500)
        "processed_$data"
    }
}

class UploadWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val data = inputData.getString("processed_data") ?: return Result.failure()

        return try {
            uploadData(data)
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }

    private suspend fun uploadData(data: String) = withContext(Dispatchers.IO) {
        delay(1000)
    }
}
```

#### 8. Наблюдение за прогрессом работы (включая Compose UI пример)

```kotlin
import android.app.Application
import androidx.compose.material3.Button
import androidx.compose.material3.Column
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import androidx.work.WorkInfo
import androidx.work.WorkManager
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.util.UUID

data class WorkProgress(
    val state: WorkInfo.State,
    val progress: Int = 0,
    val error: String? = null
)

class WorkViewModel(
    application: Application
) : AndroidViewModel(application) {

    private val workManager = WorkManager.getInstance(application)

    private val _workProgress = MutableStateFlow<WorkProgress?>(null)
    val workProgress: StateFlow<WorkProgress?> = _workProgress

    fun startDataSync(userId: String) {
        val workId = DataSyncWorker.scheduleSyncWork(
            context = getApplication(),
            syncType = "full",
            userId = userId
        )
        observeWork(workId)
    }

    private fun observeWork(workId: UUID) {
        viewModelScope.launch {
            workManager.getWorkInfoByIdFlow(workId).collect { workInfo ->
                _workProgress.value = when (workInfo.state) {
                    WorkInfo.State.ENQUEUED -> WorkProgress(WorkInfo.State.ENQUEUED)
                    WorkInfo.State.RUNNING -> {
                        val progress = workInfo.progress.getInt(
                            DataSyncWorker.KEY_PROGRESS,
                            0
                        )
                        WorkProgress(WorkInfo.State.RUNNING, progress)
                    }
                    WorkInfo.State.SUCCEEDED -> WorkProgress(WorkInfo.State.SUCCEEDED, 100)
                    WorkInfo.State.FAILED -> {
                        val error = workInfo.outputData.getString("error")
                        WorkProgress(WorkInfo.State.FAILED, error = error)
                    }
                    WorkInfo.State.CANCELLED -> WorkProgress(WorkInfo.State.CANCELLED)
                    WorkInfo.State.BLOCKED -> WorkProgress(WorkInfo.State.BLOCKED)
                }
            }
        }
    }

    fun cancelWork(workId: UUID) {
        workManager.cancelWorkById(workId)
    }
}

@Composable
fun WorkProgressScreen(viewModel: WorkViewModel) {
    val workProgress by viewModel.workProgress.collectAsState()

    Column {
        when (val progress = workProgress) {
            null -> Text("Нет запущенной работы")
            else -> {
                Text("Состояние: ${progress.state}")
                if (progress.state == WorkInfo.State.RUNNING) {
                    LinearProgressIndicator(
                        progress = progress.progress / 100f
                    )
                    Text("${progress.progress}%")
                }
                progress.error?.let { error ->
                    Text("Ошибка: $error")
                }
            }
        }

        Button(onClick = { viewModel.startDataSync("user123") }) {
            Text("Начать синхронизацию")
        }
    }
}
```

#### 9. Тестирование CoroutineWorker

```kotlin
import android.content.Context
import androidx.test.core.app.ApplicationProvider
import androidx.work.ListenableWorker
import androidx.work.testing.TestListenableWorkerBuilder
import androidx.work.workDataOf
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

@RunWith(RobolectricTestRunner::class)
class DataSyncWorkerTest {

    private lateinit var context: Context

    @Before
    fun setUp() {
        context = ApplicationProvider.getApplicationContext()
    }

    @Test
    fun testDataSyncWorker_success() = runBlocking {
        val worker = TestListenableWorkerBuilder<DataSyncWorker>(context)
            .setInputData(
                workDataOf(
                    DataSyncWorker.KEY_SYNC_TYPE to "full",
                    DataSyncWorker.KEY_USER_ID to "test_user"
                )
            )
            .build()

        val result = worker.doWork()

        assertTrue(result is ListenableWorker.Result.Success)
    }

    @Test
    fun testDataSyncWorker_missingInput() = runBlocking {
        val worker = TestListenableWorkerBuilder<DataSyncWorker>(context)
            .build()

        val result = worker.doWork()

        assertTrue(result is ListenableWorker.Result.Failure)
    }
}
```

#### 10. Лучшие практики

```kotlin
// ХОРОШО: уникальная работа для дедупликации
WorkManager.getInstance(context).enqueueUniqueWork(
    "user_sync_$userId",
    ExistingWorkPolicy.KEEP,
    syncRequest
)

// ХОРОШО: корректные constraints
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .setRequiresBatteryNotLow(true)
    .setRequiresStorageNotLow(true)
    .build()

// ХОРОШО: проверять isStopped для отмены
override suspend fun doWork(): Result {
    for (item in items) {
        if (isStopped) {
            return Result.failure()
        }
        processItem(item)
    }
    return Result.success()
}

// ХОРОШО: foreground для длительной работы
override suspend fun doWork(): Result {
    setForeground(getForegroundInfo())
    // Длительная работа
    return Result.success()
}

// ХОРОШО: экспоненциальный backoff для повторов
OneTimeWorkRequestBuilder<MyWorker>()
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,
        WorkRequest.MIN_BACKOFF_MILLIS,
        TimeUnit.MILLISECONDS
    )
    .build()

// ПЛОХО: блокирующие операции в CoroutineWorker
override suspend fun doWork(): Result {
    Thread.sleep(1000) // Вместо этого используйте delay()
    return Result.success()
}

// ПЛОХО: игнорирование отмены
override suspend fun doWork(): Result {
    while (true) {
        if (isStopped) break
        processItem()
    }
    return Result.success()
}

// ПЛОХО: не обрабатывать исключения
override suspend fun doWork(): Result {
    return try {
        performWork()
        Result.success()
    } catch (e: Exception) {
        Result.failure()
    }
}
```

### Связанные вопросы
- [[q-structured-concurrency--kotlin--hard]] - Принципы структурированной конкурентности
- [[q-kotlin-serialization--programming-languages--easy]]
- [[q-flow-basics--kotlin--easy]] - `Flow` для реактивных обновлений

### Дополнительные вопросы
1. Как WorkManager гарантирует выполнение работы даже после смерти процесса приложения? Опишите роль внутреннего планировщика и сохраненных work-запросов.
2. В чем разница между setForeground()/getForegroundInfo() в CoroutineWorker и когда их использовать для длительных задач?
3. Как реализовать менеджер загрузок с паузой/возобновлением, используя CoroutineWorker и ограничения WorkManager?
4. Объясните, как работает backoff policy в WorkManager с экспоненциальными задержками. Какова максимальная задержка и как она рассчитывается?
5. Как тестировать CoroutineWorker, использующий Android-специфичные API или DI-фреймворки (например, Hilt)?
6. Что происходит с выполняющейся работой, когда constraints больше не выполняются (например, отключается Wi-Fi), и как WorkManager обрабатывает повторное планирование?
7. Как реализовать worker, который отправляет детальные обновления прогресса в UI с использованием progress API WorkManager и `Flow`/`LiveData`?

## Answer (EN)

**CoroutineWorker** is a coroutine-friendly implementation of WorkManager's Worker that allows you to write background work using suspend functions instead of blocking operations.

#### 1. CoroutineWorker Basics

**What is CoroutineWorker?**

CoroutineWorker is specifically designed to work with Kotlin Coroutines:
- `doWork()` is a **suspend function**
- Properly integrates with the WorkManager-managed coroutine scope
- Respects WorkManager cancellation via the coroutine `Job`
- Plays well with structured concurrency

**Class structure:**

```kotlin
import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import kotlinx.coroutines.delay

class MyCoroutineWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    // This is a suspend function!
    override suspend fun doWork(): Result {
        return try {
            // Perform background work with coroutines
            performWork()
            Result.success()
        } catch (e: Exception) {
            Result.failure()
        }
    }

    private suspend fun performWork() {
        // Your suspending work here
        delay(1000)
        // Can call other suspend functions
    }
}
```

#### 2. Worker Types Comparison

```kotlin
import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.RxWorker
import androidx.work.Worker
import androidx.work.WorkerParameters
import io.reactivex.Single
import java.util.concurrent.TimeUnit
import kotlinx.coroutines.delay

// 1. Worker (traditional blocking)
class BlockingWorker(context: Context, params: WorkerParameters)
    : Worker(context, params) {

    // Runs on background thread, but blocks
    override fun doWork(): Result {
        Thread.sleep(1000) // Blocking call
        return Result.success()
    }
}

// 2. CoroutineWorker (coroutine-based)
class CoroutineBasedWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    // Suspend function - non-blocking
    override suspend fun doWork(): Result {
        delay(1000) // Non-blocking suspension
        return Result.success()
    }
}

// 3. RxWorker (RxJava-based)
class RxBasedWorker(context: Context, params: WorkerParameters)
    : RxWorker(context, params) {

    // Returns Single<Result>
    override fun createWork(): Single<Result> {
        return Single.just(Result.success())
            .delay(1, TimeUnit.SECONDS)
    }
}
```

**Comparison Table:**

| Feature | Worker | CoroutineWorker | RxWorker |
|---------|--------|-----------------|----------|
| Execution | Blocking thread | Suspending (non-blocking) | Reactive stream |
| Cancellation | Manual/cooperative | Integrated with `Job` | Via `Disposable` |
| API | Synchronous | Coroutines | RxJava |
| Testing | Simple | TestDispatcher / TestWorker | TestScheduler |
| Modern | Less preferred | Recommended | For legacy Rx code |
| Best for | Simple blocking I/O | Modern Kotlin apps | Existing RxJava code |

#### 3. When to Use WorkManager Vs Direct Coroutines

```kotlin
import android.content.Context
import androidx.work.*
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

// USE WorkManager + CoroutineWorker when:

// 1. Work must survive process death and app restarts
class DataSyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        // Sync can be resumed even if app was killed and constraints are met again
        syncDataWithServer()
        return Result.success()
    }

    private suspend fun syncDataWithServer() {
        // Implementation
    }
}

// 2. Need guaranteed execution with retry/backoff
val workRequest = OneTimeWorkRequestBuilder<DataSyncWorker>()
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,
        WorkRequest.MIN_BACKOFF_MILLIS,
        TimeUnit.MILLISECONDS
    )
    .build()

// 3. Need constraints (network, battery, etc.)
val constrainedWork = OneTimeWorkRequestBuilder<UploadWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.UNMETERED) // WiFi only
            .setRequiresCharging(true)
            .build()
    )
    .build()

// 4. Periodic work
val periodicWork = PeriodicWorkRequestBuilder<CleanupWorker>(
    repeatInterval = 1,
    repeatIntervalTimeUnit = TimeUnit.DAYS
).build()

// DON'T use WorkManager when:

// 1. Immediate execution needed (use regular coroutines)
fun loadUserProfileImmediate(scope: CoroutineScope) {
    scope.launch {
        loadUserProfile() // Immediate, tied to lifecycle
    }
}

// 2. Work is tied to UI lifecycle
fun updateUiScoped(scope: CoroutineScope) {
    scope.launch {
        updateUI() // Should be cancelled when UI is destroyed
    }
}

// 3. Real-time updates needed
fun observeMessages() = kotlinx.coroutines.flow.channelFlow {
    // Real-time messaging - not suitable for WorkManager
    websocket.collect { message ->
        send(message)
    }
}
```

**When to use each:**

| Scenario | Solution | Reason |
|----------|----------|--------|
| Upload file in background | WorkManager | Survives process death, can enforce constraints |
| Load data for screen | `ViewModel` + coroutine | Tied to lifecycle |
| Periodic cleanup | WorkManager | Scheduled, resilient |
| Real-time chat | Coroutine + `Flow` | Needs immediate, continuous updates |
| Database migration | WorkManager | Long-running, needs completion |
| API call on button click | `ViewModel` + coroutine | Immediate, cancellable |

#### 4. Production Example: Data Sync Worker

```kotlin
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.work.*
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import java.util.UUID
import java.util.concurrent.TimeUnit

class DataSyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    companion object {
        const val KEY_SYNC_TYPE = "sync_type"
        const val KEY_USER_ID = "user_id"
        const val KEY_PROGRESS = "progress"
        const val KEY_PROGRESS_TAG = "progress_tag"
        const val TAG_SYNC = "data_sync"
        private const val NOTIFICATION_ID = 1001
        private const val CHANNEL_ID = "sync_channel"

        fun scheduleSyncWork(
            context: Context,
            syncType: String,
            userId: String
        ): UUID {
            val inputData = workDataOf(
                KEY_SYNC_TYPE to syncType,
                KEY_USER_ID to userId
            )

            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .setRequiresBatteryNotLow(true)
                .build()

            val syncRequest = OneTimeWorkRequestBuilder<DataSyncWorker>()
                .setInputData(inputData)
                .setConstraints(constraints)
                .setBackoffCriteria(
                    BackoffPolicy.EXPONENTIAL,
                    WorkRequest.MIN_BACKOFF_MILLIS,
                    TimeUnit.MILLISECONDS
                )
                .addTag(TAG_SYNC)
                .build()

            WorkManager.getInstance(context).enqueueUniqueWork(
                "sync_$userId",
                ExistingWorkPolicy.REPLACE,
                syncRequest
            )

            return syncRequest.id
        }
    }

    override suspend fun doWork(): Result {
        val syncType = inputData.getString(KEY_SYNC_TYPE) ?: return Result.failure()
        val userId = inputData.getString(KEY_USER_ID) ?: return Result.failure()

        return try {
            // Show foreground notification for long-running work
            setForeground(getForegroundInfo())

            // Perform sync with progress updates
            performSync(syncType, userId)

            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure(
                    workDataOf("error" to (e.message ?: "unknown error"))
                )
            }
        }
    }

    private suspend fun performSync(syncType: String, userId: String) {
        val repository = DataRepository() // Inject via DI in a real app

        when (syncType) {
            "full" -> syncFullData(repository, userId)
            "incremental" -> syncIncrementalData(repository, userId)
            else -> throw IllegalArgumentException("Unknown sync type: $syncType")
        }
    }

    private suspend fun syncFullData(repository: DataRepository, userId: String) {
        val steps = listOf("users", "posts", "comments", "media")

        steps.forEachIndexed { index, step ->
            if (isStopped) throw CancellationException("Work cancelled")

            setProgressAsync(
                workDataOf(
                    KEY_PROGRESS to ((index + 1) * 100 / steps.size)
                )
            )

            when (step) {
                "users" -> repository.syncUsers(userId)
                "posts" -> repository.syncPosts(userId)
                "comments" -> repository.syncComments(userId)
                "media" -> repository.syncMedia(userId)
            }
        }
    }

    private suspend fun syncIncrementalData(repository: DataRepository, userId: String) {
        val lastSyncTime = repository.getLastSyncTime(userId)
        repository.syncChangesSince(userId, lastSyncTime)
        repository.updateLastSyncTime(userId, System.currentTimeMillis())
    }

    override suspend fun getForegroundInfo(): ForegroundInfo {
        createChannelIfNeeded()

        val notification = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setContentTitle("Syncing data")
            .setContentText("Synchronizing your data in the background")
            .setSmallIcon(R.drawable.ic_sync)
            .setOngoing(true)
            .build()

        return ForegroundInfo(NOTIFICATION_ID, notification)
    }

    private fun createChannelIfNeeded() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val manager = applicationContext
                .getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            if (manager.getNotificationChannel(CHANNEL_ID) == null) {
                val channel = NotificationChannel(
                    CHANNEL_ID,
                    "Data sync",
                    NotificationManager.IMPORTANCE_LOW
                )
                manager.createNotificationChannel(channel)
            }
        }
    }
}

// Mock repository for example
class DataRepository {
    suspend fun syncUsers(userId: String) = withContext(Dispatchers.IO) {
        delay(500)
    }

    suspend fun syncPosts(userId: String) = withContext(Dispatchers.IO) {
        delay(500)
    }

    suspend fun syncComments(userId: String) = withContext(Dispatchers.IO) {
        delay(500)
    }

    suspend fun syncMedia(userId: String) = withContext(Dispatchers.IO) {
        delay(500)
    }

    suspend fun getLastSyncTime(userId: String): `Long` = withContext(Dispatchers.IO) {
        System.currentTimeMillis() - 3600000
    }

    suspend fun syncChangesSince(userId: String, timestamp: `Long`) =
        withContext(Dispatchers.IO) {
            delay(1000)
        }

    suspend fun updateLastSyncTime(userId: String, timestamp: `Long`) =
        withContext(Dispatchers.IO) {
        }
}
```

#### 5. File Upload Worker with Progress

```kotlin
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.net.Uri
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.work.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody
import okio.BufferedSink
import java.io.File
import java.io.IOException
import java.util.UUID

class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    companion object {
        const val KEY_FILE_URI = "file_uri"
        const val KEY_UPLOAD_URL = "upload_url"
        const val KEY_PROGRESS = "progress"
        const val KEY_UPLOADED_BYTES = "uploaded_bytes"
        const val KEY_TOTAL_BYTES = "total_bytes"
        private const val NOTIFICATION_ID = 1002
        private const val CHANNEL_ID = "upload_channel"

        fun uploadFile(
            context: Context,
            fileUri: Uri,
            uploadUrl: String
        ): UUID {
            val inputData = workDataOf(
                KEY_FILE_URI to fileUri.toString(),
                KEY_UPLOAD_URL to uploadUrl
            )

            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.UNMETERED) // For large uploads
                .build()

            val uploadRequest = OneTimeWorkRequestBuilder<FileUploadWorker>()
                .setInputData(inputData)
                .setConstraints(constraints)
                .build()

            WorkManager.getInstance(context).enqueue(uploadRequest)

            return uploadRequest.id
        }
    }

    override suspend fun doWork(): Result {
        val fileUriString = inputData.getString(KEY_FILE_URI) ?: return Result.failure()
        val uploadUrl = inputData.getString(KEY_UPLOAD_URL) ?: return Result.failure()

        return try {
            val fileUri = Uri.parse(fileUriString)
            val file = getFileFromUri(fileUri)

            setForeground(getForegroundInfo())

            uploadFileWithProgress(file, uploadUrl)

            Result.success(
                workDataOf("uploaded_file" to file.name)
            )
        } catch (e: IOException) {
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure(
                    workDataOf("error" to (e.message ?: "upload failed"))
                )
            }
        }
    }

    private suspend fun uploadFileWithProgress(
        file: File,
        uploadUrl: String
    ) = withContext(Dispatchers.IO) {
        val client = OkHttpClient()

        val requestBody = object : RequestBody() {
            override fun contentType() = "application/octet-stream".toMediaType()
            override fun contentLength() = file.length()

            override fun writeTo(sink: BufferedSink) {
                val fileSize = file.length().coerceAtLeast(1L)
                var uploadedBytes = 0L

                file.inputStream().use { inputStream ->
                    val buffer = ByteArray(8192)
                    var bytesRead: Int

                    while (inputStream.read(buffer).also { bytesRead = it } != -1) {
                        if (isStopped) throw IOException("Upload cancelled")

                        sink.write(buffer, 0, bytesRead)
                        uploadedBytes += bytesRead

                        val progress = (uploadedBytes * 100 / fileSize).toInt()
                        setProgressAsync(
                            workDataOf(
                                KEY_PROGRESS to progress,
                                KEY_UPLOADED_BYTES to uploadedBytes,
                                KEY_TOTAL_BYTES to fileSize
                            )
                        )
                    }
                }
            }
        }

        val request = Request.Builder()
            .url(uploadUrl)
            .post(requestBody)
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IOException("Upload failed: ${response.code}")
            }
        }
    }

    private fun getFileFromUri(uri: Uri): File {
        // In a real app, resolve/copy content:// URI to a cache file
        return File(requireNotNull(uri.path))
    }

    override suspend fun getForegroundInfo(): ForegroundInfo {
        createChannelIfNeeded()

        val notification = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setContentTitle("Uploading file")
            .setContentText("Upload in progress")
            .setSmallIcon(R.drawable.ic_upload)
            .setProgress(100, 0, true)
            .setOngoing(true)
            .build()

        return ForegroundInfo(NOTIFICATION_ID, notification)
    }

    private fun createChannelIfNeeded() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val manager = applicationContext
                .getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            if (manager.getNotificationChannel(CHANNEL_ID) == null) {
                val channel = NotificationChannel(
                    CHANNEL_ID,
                    "File uploads",
                    NotificationManager.IMPORTANCE_LOW
                )
                manager.createNotificationChannel(channel)
            }
        }
    }
}
```

#### 6. Periodic Cleanup Worker

```kotlin
import android.content.Context
import androidx.work.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import java.io.File
import java.util.concurrent.TimeUnit

class CleanupWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    companion object {
        fun schedulePeriodicCleanup(context: Context) {
            val cleanupRequest = PeriodicWorkRequestBuilder<CleanupWorker>(
                repeatInterval = 1,
                repeatIntervalTimeUnit = TimeUnit.DAYS
            )
                .setConstraints(
                    Constraints.Builder()
                        .setRequiresCharging(true)
                        .setRequiresBatteryNotLow(true)
                        .build()
                )
                .setInitialDelay(1, TimeUnit.HOURS)
                .build()

            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                "periodic_cleanup",
                ExistingPeriodicWorkPolicy.KEEP,
                cleanupRequest
            )
        }
    }

    override suspend fun doWork(): Result {
        return try {
            performCleanup()
            Result.success()
        } catch (e: Exception) {
            // For periodic work, explicit retry logic is usually not needed
            Result.failure()
        }
    }

    private suspend fun performCleanup() = withContext(Dispatchers.IO) {
        cleanCacheDirectory()
        deleteOldTempFiles()
        vacuumDatabase()
        clearOldLogs()
    }

    private fun cleanCacheDirectory() {
        val cacheDir = applicationContext.cacheDir
        val maxCacheSize = 50 * 1024 * 1024 // 50 MB

        fun currentSize(): Long = cacheDir.walkTopDown()
            .filter { it.isFile }
            .map { it.length() }
            .sum()

        var size = currentSize()
        if (size > maxCacheSize) {
            cacheDir.walkTopDown()
                .filter { it.isFile }
                .sortedBy { it.lastModified() }
                .forEach { file ->
                    if (size <= maxCacheSize) return
                    val len = file.length()
                    if (file.delete()) {
                        size -= len
                    }
                }
        }
    }

    private fun deleteOldTempFiles() {
        val tempDir = File(applicationContext.cacheDir, "temp")
        val maxAge = System.currentTimeMillis() - TimeUnit.DAYS.toMillis(7)

        if (tempDir.exists()) {
            tempDir.walkTopDown()
                .filter { it.isFile && it.lastModified() < maxAge }
                .forEach { it.delete() }
        }
    }

    private suspend fun vacuumDatabase() {
        // Example placeholder
        delay(1000)
    }

    private fun clearOldLogs() {
        val logDir = File(applicationContext.filesDir, "logs")
        val maxAge = System.currentTimeMillis() - TimeUnit.DAYS.toMillis(30)

        if (logDir.exists()) {
            logDir.walkTopDown()
                .filter { it.isFile && it.lastModified() < maxAge }
                .forEach { it.delete() }
        }
    }
}
```

#### 7. Chaining Workers

```kotlin
import android.content.Context
import androidx.work.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext

fun chainedWorkExample(context: Context) {
    val downloadWork = OneTimeWorkRequestBuilder<DownloadWorker>()
        .setInputData(workDataOf("url" to "https://api.example.com/data"))
        .build()

    val processWork = OneTimeWorkRequestBuilder<ProcessWorker>()
        .build()

    val uploadWork = OneTimeWorkRequestBuilder<UploadWorker>()
        .build()

    WorkManager.getInstance(context)
        .beginWith(downloadWork)
        .then(processWork)
        .then(uploadWork)
        .enqueue()
}

class DownloadWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val url = inputData.getString("url") ?: return Result.failure()

        return try {
            val data = downloadData(url)
            Result.success(workDataOf("downloaded_data" to data))
        } catch (e: Exception) {
            Result.failure()
        }
    }

    private suspend fun downloadData(url: String): String = withContext(Dispatchers.IO) {
        delay(1000)
        "downloaded_data_content"
    }
}

class ProcessWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val data = inputData.getString("downloaded_data") ?: return Result.failure()

        return try {
            val processed = processData(data)
            Result.success(workDataOf("processed_data" to processed))
        } catch (e: Exception) {
            Result.failure()
        }
    }

    private suspend fun processData(data: String): String = withContext(Dispatchers.Default) {
        delay(500)
        "processed_$data"
    }
}

class UploadWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val data = inputData.getString("processed_data") ?: return Result.failure()

        return try {
            uploadData(data)
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }

    private suspend fun uploadData(data: String) = withContext(Dispatchers.IO) {
        delay(1000)
    }
}
```

#### 8. Observing Work Progress

```kotlin
import android.app.Application
import androidx.compose.material3.Button
import androidx.compose.material3.Column
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import androidx.work.WorkInfo
import androidx.work.WorkManager
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.util.UUID

data class WorkProgress(
    val state: WorkInfo.State,
    val progress: Int = 0,
    val error: String? = null
)

class WorkViewModel(
    application: Application
) : AndroidViewModel(application) {

    private val workManager = WorkManager.getInstance(application)

    private val _workProgress = MutableStateFlow<WorkProgress?>(null)
    val workProgress: StateFlow<WorkProgress?> = _workProgress

    fun startDataSync(userId: String) {
        val workId = DataSyncWorker.scheduleSyncWork(
            context = getApplication(),
            syncType = "full",
            userId = userId
        )
        observeWork(workId)
    }

    private fun observeWork(workId: UUID) {
        viewModelScope.launch {
            workManager.getWorkInfoByIdFlow(workId).collect { workInfo ->
                _workProgress.value = when (workInfo.state) {
                    WorkInfo.State.ENQUEUED -> WorkProgress(WorkInfo.State.ENQUEUED)
                    WorkInfo.State.RUNNING -> {
                        val progress = workInfo.progress.getInt(
                            DataSyncWorker.KEY_PROGRESS,
                            0
                        )
                        WorkProgress(WorkInfo.State.RUNNING, progress)
                    }
                    WorkInfo.State.SUCCEEDED -> WorkProgress(WorkInfo.State.SUCCEEDED, 100)
                    WorkInfo.State.FAILED -> {
                        val error = workInfo.outputData.getString("error")
                        WorkProgress(WorkInfo.State.FAILED, error = error)
                    }
                    WorkInfo.State.CANCELLED -> WorkProgress(WorkInfo.State.CANCELLED)
                    WorkInfo.State.BLOCKED -> WorkProgress(WorkInfo.State.BLOCKED)
                }
            }
        }
    }

    fun cancelWork(workId: UUID) {
        workManager.cancelWorkById(workId)
    }
}

@Composable
fun WorkProgressScreen(viewModel: WorkViewModel) {
    val workProgress by viewModel.workProgress.collectAsState()

    Column {
        when (val progress = workProgress) {
            null -> Text("No work running")
            else -> {
                Text("State: ${progress.state}")
                if (progress.state == WorkInfo.State.RUNNING) {
                    LinearProgressIndicator(
                        progress = progress.progress / 100f
                    )
                    Text("${progress.progress}%")
                }
                progress.error?.let { error ->
                    Text("Error: $error")
                }
            }
        }

        Button(onClick = { viewModel.startDataSync("user123") }) {
            Text("Start Sync")
        }
    }
}
```

#### 9. Testing CoroutineWorker

```kotlin
import android.content.Context
import androidx.test.core.app.ApplicationProvider
import androidx.work.ListenableWorker
import androidx.work.testing.TestListenableWorkerBuilder
import androidx.work.workDataOf
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

@RunWith(RobolectricTestRunner::class)
class DataSyncWorkerTest {

    private lateinit var context: Context

    @Before
    fun setUp() {
        context = ApplicationProvider.getApplicationContext()
    }

    @Test
    fun testDataSyncWorker_success() = runBlocking {
        val worker = TestListenableWorkerBuilder<DataSyncWorker>(context)
            .setInputData(
                workDataOf(
                    DataSyncWorker.KEY_SYNC_TYPE to "full",
                    DataSyncWorker.KEY_USER_ID to "test_user"
                )
            )
            .build()

        val result = worker.doWork()

        assertTrue(result is ListenableWorker.Result.Success)
    }

    @Test
    fun testDataSyncWorker_missingInput() = runBlocking {
        val worker = TestListenableWorkerBuilder<DataSyncWorker>(context)
            .build()

        val result = worker.doWork()

        assertTrue(result is ListenableWorker.Result.Failure)
    }
}
```

#### 10. Best Practices

```kotlin
// GOOD: Use unique work for deduplication
WorkManager.getInstance(context).enqueueUniqueWork(
    "user_sync_$userId",
    ExistingWorkPolicy.KEEP,
    syncRequest
)

// GOOD: Set appropriate constraints
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .setRequiresBatteryNotLow(true)
    .setRequiresStorageNotLow(true)
    .build()

// GOOD: Check isStopped for cancellation
override suspend fun doWork(): Result {
    for (item in items) {
        if (isStopped) {
            return Result.failure()
        }
        processItem(item)
    }
    return Result.success()
}

// GOOD: Use foreground for long-running work
override suspend fun doWork(): Result {
    setForeground(getForegroundInfo())
    // Long-running work
    return Result.success()
}

// GOOD: Exponential backoff for retries
OneTimeWorkRequestBuilder<MyWorker>()
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,
        WorkRequest.MIN_BACKOFF_MILLIS,
        TimeUnit.MILLISECONDS
    )
    .build()

// BAD: Blocking operations in CoroutineWorker
override suspend fun doWork(): Result {
    Thread.sleep(1000) // Don't block; use delay()
    return Result.success()
}

// BAD: Ignoring cancellation
override suspend fun doWork(): Result {
    while (true) {
        if (isStopped) break
        processItem()
    }
    return Result.success()
}

// BAD: Not handling exceptions
override suspend fun doWork(): Result {
    return try {
        performWork()
        Result.success()
    } catch (e: Exception) {
        Result.failure()
    }
}
```

### Related Questions
- [[q-structured-concurrency--kotlin--hard]] - Structured concurrency principles
- [[q-kotlin-serialization--programming-languages--easy]]
- [[q-flow-basics--kotlin--easy]] - `Flow` for reactive updates

## Follow-ups
1. How does WorkManager ensure work execution survives app process death? Describe the role of internal scheduling and persisted work requests.
2. What's the difference between setForeground()/getForegroundInfo() in CoroutineWorker and when should each be used in long-running tasks?
3. How would you implement a download manager with pause/resume using CoroutineWorker and WorkManager constraints?
4. Explain how WorkManager's backoff policy works with exponential delays. What is the maximum delay and how is it calculated?
5. How do you test a CoroutineWorker that depends on Android-specific APIs or uses DI frameworks like Hilt?
6. What happens to running work when constraints are no longer met (e.g., WiFi disconnects) and how does WorkManager handle rescheduling?
7. How would you implement a worker that reports granular progress updates to the UI using WorkManager's progress APIs and `Flow`/`LiveData`?

## References
- [[c-workmanager]]
- [[c-coroutines]]
- Official WorkManager and CoroutineWorker documentation on developer.android.com
