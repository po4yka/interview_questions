---
id: android-266
title: "Large File Upload App / Загрузка больших файлов в приложении"
aliases: [Large File Upload, Загрузка больших файлов, File Upload Android, WorkManager Upload]
topic: android
subtopics: [background-execution, networking-http, coroutines]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-workmanager, c-retrofit, c-coroutines, q-background-processing-strategies--android--hard, q-foreground-service-use-cases--android--medium]
created: 2025-10-15
updated: 2025-10-30
tags: [android/background-execution, android/networking-http, android/coroutines, background-processing, file-upload, networking, retrofit, workmanager, foreground-service, difficulty/hard]
---

# Вопрос (RU)

> Как бы вы реализовали приложение, которое может загружать большие файлы на сервер?

# Question (EN)

> How would you implement an app that can upload large files to a server?

---

## Ответ (RU)

### Архитектура решения

**Ключевые компоненты:**

1. **WorkManager** - гарантированное выполнение в фоне
2. **Retrofit + OkHttp** - multipart загрузка с прогрессом
3. **Foreground Service** - видимая пользователю операция
4. **Chunked Upload** - разбиение на части для файлов >100MB
5. **Retry Logic** - автоматические повторы при ошибках

### Реализация

#### 1. API интерфейс

```kotlin
interface FileUploadApi {
    @Multipart
    @POST("upload")
    suspend fun uploadFile(
        @Part file: MultipartBody.Part,
        @Part("metadata") metadata: RequestBody
    ): Response<UploadResponse>

    @Multipart
    @POST("upload/chunk")
    suspend fun uploadChunk(
        @Part chunk: MultipartBody.Part,
        @Part("index") index: RequestBody,
        @Part("total") total: RequestBody,
        @Part("uploadId") uploadId: RequestBody
    ): Response<ChunkResponse>
}
```

#### 2. Progress Tracking

```kotlin
class ProgressRequestBody(
    private val delegate: RequestBody,
    private val onProgress: (Long, Long) -> Unit
) : RequestBody() {
    override fun contentType() = delegate.contentType()
    override fun contentLength() = delegate.contentLength()

    override fun writeTo(sink: BufferedSink) {
        val countingSink = CountingSink(sink, contentLength(), onProgress)
        val bufferedSink = countingSink.buffer()
        delegate.writeTo(bufferedSink)
        bufferedSink.flush()
    }
}

class CountingSink(
    delegate: Sink,
    private val total: Long,
    private val onProgress: (Long, Long) -> Unit
) : ForwardingSink(delegate) {
    private var written = 0L

    override fun write(source: Buffer, byteCount: Long) {
        super.write(source, byteCount)
        written += byteCount
        onProgress(written, total)
    }
}
```

#### 3. FileUploadWorker

```kotlin
class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val filePath = inputData.getString(KEY_FILE_PATH) ?: return Result.failure()
        val file = File(filePath)

        if (!file.exists()) return Result.failure()

        createNotificationChannel()
        setForeground(createForegroundInfo(0))

        return try {
            uploadFile(file)
            showNotification("Завершено", file.name, 100)
            Result.success()
        } catch (e: IOException) {
            Result.retry() // ✅ Повтор при сетевых ошибках
        } catch (e: Exception) {
            Result.failure(workDataOf("error" to e.message))
        }
    }

    private suspend fun uploadFile(file: File): Boolean {
        val api = RetrofitClient.create { written, total ->
            val progress = (100 * written / total).toInt()
            setProgressAsync(workDataOf("progress" to progress))
            showNotification("Загрузка...", file.name, progress)
        }

        val requestFile = file.asRequestBody("application/octet-stream".toMediaType())
        val filePart = MultipartBody.Part.createFormData("file", file.name, requestFile)

        val response = api.uploadFile(filePart, createMetadata())
        return response.isSuccessful
    }

    private fun createForegroundInfo(progress: Int) = ForegroundInfo(
        NOTIFICATION_ID,
        NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setContentTitle("Загрузка файла")
            .setSmallIcon(android.R.drawable.stat_sys_upload)
            .setProgress(100, progress, false)
            .setOngoing(true)
            .build()
    )
}
```

#### 4. Запуск загрузки

```kotlin
class MainActivity : AppCompatActivity() {
    private val workManager by lazy { WorkManager.getInstance(this) }

    private fun uploadFile(uri: Uri) {
        val file = copyToCache(uri)

        val uploadRequest = OneTimeWorkRequestBuilder<FileUploadWorker>()
            .setInputData(workDataOf(KEY_FILE_PATH to file.absolutePath))
            .setConstraints(Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED) // ✅ Только при сети
                .setRequiresBatteryNotLow(true) // ✅ Батарея не разряжена
                .build())
            .setBackoffCriteria(
                BackoffPolicy.EXPONENTIAL,
                WorkRequest.MIN_BACKOFF_MILLIS,
                TimeUnit.MILLISECONDS
            )
            .build()

        workManager.enqueue(uploadRequest)

        // Наблюдение за прогрессом
        workManager.getWorkInfoByIdLiveData(uploadRequest.id)
            .observe(this) { workInfo ->
                when (workInfo.state) {
                    WorkInfo.State.RUNNING -> {
                        val progress = workInfo.progress.getInt("progress", 0)
                        updateProgress(progress)
                    }
                    WorkInfo.State.SUCCEEDED -> showSuccess()
                    WorkInfo.State.FAILED -> showError()
                    else -> {}
                }
            }
    }
}
```

#### 5. Chunked Upload для больших файлов

```kotlin
class ChunkedUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    companion object {
        const val CHUNK_SIZE = 5 * 1024 * 1024 // 5MB
    }

    override suspend fun doWork(): Result {
        val file = File(inputData.getString(KEY_FILE_PATH)!!)
        return try {
            uploadInChunks(file)
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }

    private suspend fun uploadInChunks(file: File) {
        val totalChunks = (file.length() / CHUNK_SIZE + 1).toInt()
        val uploadId = UUID.randomUUID().toString()

        file.inputStream().buffered().use { input ->
            var index = 0
            val buffer = ByteArray(CHUNK_SIZE)

            while (true) {
                val bytesRead = input.read(buffer)
                if (bytesRead == -1) break

                val chunk = File(cacheDir, "chunk_$index")
                chunk.writeBytes(buffer.copyOf(bytesRead))

                uploadChunk(chunk, index, totalChunks, uploadId)
                chunk.delete()

                setProgressAsync(workDataOf("progress" to (100 * ++index / totalChunks)))
            }
        }
    }

    private suspend fun uploadChunk(file: File, index: Int, total: Int, uploadId: String) {
        val api = RetrofitClient.create()
        val part = MultipartBody.Part.createFormData(
            "chunk", file.name,
            file.asRequestBody("application/octet-stream".toMediaType())
        )

        val response = api.uploadChunk(
            part,
            index.toRequestBody(),
            total.toRequestBody(),
            uploadId.toRequestBody()
        )

        if (!response.isSuccessful) {
            throw IOException("Chunk $index failed: ${response.code()}")
        }
    }
}
```

### Лучшие практики

✅ **Правильно:**
- Использовать WorkManager для гарантированного выполнения
- Показывать Foreground Service для длительных операций
- Разбивать файлы >100MB на chunks
- Добавлять constraints (сеть, батарея)
- Реализовать exponential backoff для retry
- Очищать cache после загрузки
- Компрессовать перед отправкой (если применимо)

❌ **Неправильно:**
- Загружать в main thread
- Использовать Service без Foreground для Android 8+
- Не обрабатывать ошибки сети
- Не показывать прогресс пользователю
- Хранить большие файлы в памяти целиком
- Не очищать временные файлы

### Компромиссы

| Подход | Плюсы | Минусы |
|--------|-------|--------|
| **Простая загрузка** | Проще реализация | Не для файлов >100MB |
| **Chunked upload** | Поддержка pause/resume | Сложнее backend |
| **WorkManager** | Гарантированное выполнение | Не мгновенный запуск |
| **Foreground Service** | Приоритет системы | Требует уведомление |

---

## Answer (EN)

### Architecture Overview

**Key Components:**

1. **WorkManager** - guaranteed background execution
2. **Retrofit + OkHttp** - multipart upload with progress
3. **Foreground Service** - user-visible operation
4. **Chunked Upload** - split files >100MB into parts
5. **Retry Logic** - automatic retry on failures

### Implementation

#### 1. API Interface

```kotlin
interface FileUploadApi {
    @Multipart
    @POST("upload")
    suspend fun uploadFile(
        @Part file: MultipartBody.Part,
        @Part("metadata") metadata: RequestBody
    ): Response<UploadResponse>

    @Multipart
    @POST("upload/chunk")
    suspend fun uploadChunk(
        @Part chunk: MultipartBody.Part,
        @Part("index") index: RequestBody,
        @Part("total") total: RequestBody,
        @Part("uploadId") uploadId: RequestBody
    ): Response<ChunkResponse>
}
```

#### 2. Progress Tracking

```kotlin
class ProgressRequestBody(
    private val delegate: RequestBody,
    private val onProgress: (Long, Long) -> Unit
) : RequestBody() {
    override fun contentType() = delegate.contentType()
    override fun contentLength() = delegate.contentLength()

    override fun writeTo(sink: BufferedSink) {
        val countingSink = CountingSink(sink, contentLength(), onProgress)
        val bufferedSink = countingSink.buffer()
        delegate.writeTo(bufferedSink)
        bufferedSink.flush()
    }
}

class CountingSink(
    delegate: Sink,
    private val total: Long,
    private val onProgress: (Long, Long) -> Unit
) : ForwardingSink(delegate) {
    private var written = 0L

    override fun write(source: Buffer, byteCount: Long) {
        super.write(source, byteCount)
        written += byteCount
        onProgress(written, total)
    }
}
```

#### 3. FileUploadWorker

```kotlin
class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val filePath = inputData.getString(KEY_FILE_PATH) ?: return Result.failure()
        val file = File(filePath)

        if (!file.exists()) return Result.failure()

        createNotificationChannel()
        setForeground(createForegroundInfo(0))

        return try {
            uploadFile(file)
            showNotification("Complete", file.name, 100)
            Result.success()
        } catch (e: IOException) {
            Result.retry() // ✅ Retry on network errors
        } catch (e: Exception) {
            Result.failure(workDataOf("error" to e.message))
        }
    }

    private suspend fun uploadFile(file: File): Boolean {
        val api = RetrofitClient.create { written, total ->
            val progress = (100 * written / total).toInt()
            setProgressAsync(workDataOf("progress" to progress))
            showNotification("Uploading...", file.name, progress)
        }

        val requestFile = file.asRequestBody("application/octet-stream".toMediaType())
        val filePart = MultipartBody.Part.createFormData("file", file.name, requestFile)

        val response = api.uploadFile(filePart, createMetadata())
        return response.isSuccessful
    }

    private fun createForegroundInfo(progress: Int) = ForegroundInfo(
        NOTIFICATION_ID,
        NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setContentTitle("Uploading File")
            .setSmallIcon(android.R.drawable.stat_sys_upload)
            .setProgress(100, progress, false)
            .setOngoing(true)
            .build()
    )
}
```

#### 4. Enqueue Upload

```kotlin
class MainActivity : AppCompatActivity() {
    private val workManager by lazy { WorkManager.getInstance(this) }

    private fun uploadFile(uri: Uri) {
        val file = copyToCache(uri)

        val uploadRequest = OneTimeWorkRequestBuilder<FileUploadWorker>()
            .setInputData(workDataOf(KEY_FILE_PATH to file.absolutePath))
            .setConstraints(Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED) // ✅ Network required
                .setRequiresBatteryNotLow(true) // ✅ Battery not low
                .build())
            .setBackoffCriteria(
                BackoffPolicy.EXPONENTIAL,
                WorkRequest.MIN_BACKOFF_MILLIS,
                TimeUnit.MILLISECONDS
            )
            .build()

        workManager.enqueue(uploadRequest)

        // Observe progress
        workManager.getWorkInfoByIdLiveData(uploadRequest.id)
            .observe(this) { workInfo ->
                when (workInfo.state) {
                    WorkInfo.State.RUNNING -> {
                        val progress = workInfo.progress.getInt("progress", 0)
                        updateProgress(progress)
                    }
                    WorkInfo.State.SUCCEEDED -> showSuccess()
                    WorkInfo.State.FAILED -> showError()
                    else -> {}
                }
            }
    }
}
```

#### 5. Chunked Upload for Large Files

```kotlin
class ChunkedUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    companion object {
        const val CHUNK_SIZE = 5 * 1024 * 1024 // 5MB
    }

    override suspend fun doWork(): Result {
        val file = File(inputData.getString(KEY_FILE_PATH)!!)
        return try {
            uploadInChunks(file)
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }

    private suspend fun uploadInChunks(file: File) {
        val totalChunks = (file.length() / CHUNK_SIZE + 1).toInt()
        val uploadId = UUID.randomUUID().toString()

        file.inputStream().buffered().use { input ->
            var index = 0
            val buffer = ByteArray(CHUNK_SIZE)

            while (true) {
                val bytesRead = input.read(buffer)
                if (bytesRead == -1) break

                val chunk = File(cacheDir, "chunk_$index")
                chunk.writeBytes(buffer.copyOf(bytesRead))

                uploadChunk(chunk, index, totalChunks, uploadId)
                chunk.delete()

                setProgressAsync(workDataOf("progress" to (100 * ++index / totalChunks)))
            }
        }
    }

    private suspend fun uploadChunk(file: File, index: Int, total: Int, uploadId: String) {
        val api = RetrofitClient.create()
        val part = MultipartBody.Part.createFormData(
            "chunk", file.name,
            file.asRequestBody("application/octet-stream".toMediaType())
        )

        val response = api.uploadChunk(
            part,
            index.toRequestBody(),
            total.toRequestBody(),
            uploadId.toRequestBody()
        )

        if (!response.isSuccessful) {
            throw IOException("Chunk $index failed: ${response.code()}")
        }
    }
}
```

### Best Practices

✅ **Do:**
- Use WorkManager for guaranteed execution
- Show Foreground Service for long operations
- Split files >100MB into chunks
- Add constraints (network, battery)
- Implement exponential backoff for retry
- Clean up cache after upload
- Compress before sending (if applicable)

❌ **Don't:**
- Upload on main thread
- Use Service without Foreground on Android 8+
- Ignore network errors
- Hide progress from user
- Load entire large files into memory
- Keep temporary files after upload

### Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| **Simple upload** | Easier implementation | Not for files >100MB |
| **Chunked upload** | Supports pause/resume | More complex backend |
| **WorkManager** | Guaranteed execution | Not instant start |
| **Foreground Service** | System priority | Requires notification |

---

## Follow-ups

1. How would you implement pause/resume functionality for uploads?
2. What strategies would you use to handle upload failures on slow networks?
3. How can you optimize memory usage when uploading very large files?
4. What approach would you take for uploading multiple files in parallel?
5. How would you implement upload progress persistence across app restarts?

## References

- [[c-workmanager]]
- [[c-retrofit]]
- [[c-coroutines]]
- [[c-foreground-service]]
- [Android WorkManager Documentation](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Retrofit Documentation](https://square.github.io/retrofit/)

## Related Questions

### Prerequisites (Medium)
- [[q-foreground-service-use-cases--android--medium]]
- [[q-workmanager-vs-jobscheduler--android--medium]]

### Related (Hard)
- [[q-background-processing-strategies--android--hard]]
- [[q-network-optimization-techniques--android--hard]]

### Advanced (Hard)
- [[q-resilient-network-architecture--android--hard]]
- [[q-offline-first-sync-strategy--android--hard]]
