---
id: 20251017-144923
title: "Large File Upload / Загрузка больших файлов"
aliases: ["Large File Upload", "Загрузка больших файлов"]
topic: android
subtopics: [networking-http, background-execution, files-media]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-viewmodel-vs-onsavedinstancestate--android--medium]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android/networking-http, android/background-execution, android/files-media, file-upload, workmanager, retrofit, multipart, difficulty/medium]
---
# Вопрос (RU)

Как загрузить большой файл на сервер в Android?

# Question (EN)

How to upload large files to server in Android?

---

## Ответ (RU)

Для загрузки больших файлов используйте **WorkManager + Retrofit** для гарантированного выполнения в фоне. Ключевые требования: асинхронная обработка, устойчивость к configuration changes, retry logic, отображение прогресса.

### 1. WorkManager + Retrofit (Рекомендуемый подход)

#### API Interface

```kotlin
interface FileUploadApi {
    @Multipart
    @POST("upload")
    suspend fun uploadFile(
        @Part file: MultipartBody.Part,
        @Part("description") description: RequestBody
    ): Response<UploadResponse>

    // ✅ Для очень больших файлов - chunked upload
    @Streaming
    @PUT("upload/{fileId}/chunk")
    suspend fun uploadChunk(
        @Path("fileId") fileId: String,
        @Header("Content-Range") contentRange: String,
        @Body chunk: RequestBody
    ): Response<ChunkResponse>
}
```

#### Retrofit Setup

```kotlin
private val okHttpClient = OkHttpClient.Builder()
    .connectTimeout(30, TimeUnit.SECONDS)
    .readTimeout(60, TimeUnit.SECONDS)  // ✅ Увеличен для больших файлов
    .writeTimeout(60, TimeUnit.SECONDS) // ✅ Увеличен для upload
    .build()
```

#### FileUploadWorker

```kotlin
class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val filePath = inputData.getString(KEY_FILE_PATH) ?: return Result.failure()

        return try {
            // ✅ Foreground service с notification
            setForeground(createForegroundInfo(0))

            val file = File(filePath)
            if (!file.exists()) return Result.failure()

            val requestFile = file.asRequestBody("multipart/form-data".toMediaType())
            val filePart = MultipartBody.Part.createFormData("file", file.name, requestFile)

            val response = RetrofitClient.api.uploadFile(filePart, descriptionBody)

            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(workDataOf(KEY_FILE_URL to response.body()?.fileUrl))
            } else {
                Result.retry() // ✅ Автоматический retry
            }
        } catch (e: Exception) {
            if (runAttemptCount < MAX_RETRIES) {
                Result.retry() // ✅ Exponential backoff
            } else {
                Result.failure(workDataOf(KEY_ERROR to e.message))
            }
        }
    }
}
```

#### Starting Upload

```kotlin
fun uploadFile(filePath: String): UUID {
    val constraints = Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED) // ✅ Требует сеть
        .build()

    val uploadRequest = OneTimeWorkRequestBuilder<FileUploadWorker>()
        .setInputData(workDataOf(KEY_FILE_PATH to filePath))
        .setConstraints(constraints)
        .setBackoffCriteria(
            BackoffPolicy.EXPONENTIAL,  // ✅ Exponential backoff
            WorkRequest.MIN_BACKOFF_MILLIS,
            TimeUnit.MILLISECONDS
        )
        .build()

    WorkManager.getInstance(context).enqueue(uploadRequest)
    return uploadRequest.id
}
```

### 2. Chunked Upload (для файлов > 50 MB)

```kotlin
class ChunkedFileUploadWorker : CoroutineWorker() {
    override suspend fun doWork(): Result {
        val file = File(inputData.getString(KEY_FILE_PATH))
        val chunkSize = 1024 * 1024 * 5  // ✅ 5 MB per chunk

        file.inputStream().use { inputStream ->
            var uploadedBytes = 0L
            val buffer = ByteArray(chunkSize)

            while (uploadedBytes < file.length()) {
                val bytesRead = inputStream.read(buffer)
                if (bytesRead == -1) break

                val chunk = buffer.copyOf(bytesRead)
                val contentRange = "bytes $uploadedBytes-${uploadedBytes + bytesRead - 1}/${file.length()}"

                val response = api.uploadChunk(fileId, contentRange, chunk.toRequestBody())

                if (!response.isSuccessful) return Result.retry()

                uploadedBytes += bytesRead

                // ✅ Обновить прогресс
                val progress = (uploadedBytes * 100 / file.length()).toInt()
                setProgress(workDataOf(KEY_PROGRESS to progress))
            }
        }

        return Result.success()
    }
}
```

### 3. Progress Tracking

```kotlin
// ✅ Отслеживание прогресса через OkHttp Interceptor
class UploadProgressInterceptor(
    private val onProgress: (bytesUploaded: Long, totalBytes: Long) -> Unit
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        val progressBody = ProgressRequestBody(originalBody, onProgress)
        return chain.proceed(request.newBuilder().method(method, progressBody).build())
    }
}
```

### 4. Resumable Upload

```kotlin
suspend fun uploadWithResume(file: File): Result<String> {
    val uploadedBytes = getUploadProgress(fileId)  // ✅ Восстановить прогресс

    file.inputStream().use { stream ->
        stream.skip(uploadedBytes)  // ✅ Пропустить уже загруженное

        // Продолжить загрузку с последней позиции
        // Сохранять прогресс после каждого chunk
    }
}
```

### Best Practices

1. **WorkManager** для гарантированной загрузки
2. **Chunked upload** для файлов > 50 MB (chunks по 5 MB)
3. **Progress tracking** для UX (OkHttp Interceptor)
4. **Retry logic** с exponential backoff
5. **Foreground Service** с notification
6. **WiFi-only constraint** для больших файлов (`NetworkType.UNMETERED`)
7. **Resumable uploads** - сохранение прогресса в SharedPreferences

```kotlin
// ❌ Не используйте для больших файлов
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)  // Любая сеть
    .build()

// ✅ Используйте для больших файлов
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED)  // Только WiFi
    .build()
```

---

## Answer (EN)

Use **WorkManager + Retrofit** to upload large files with guaranteed background execution. Key requirements: async processing, configuration change resilience, retry logic, progress tracking.

### 1. WorkManager + Retrofit (Recommended)

#### API Interface

```kotlin
interface FileUploadApi {
    @Multipart
    @POST("upload")
    suspend fun uploadFile(
        @Part file: MultipartBody.Part,
        @Part("description") description: RequestBody
    ): Response<UploadResponse>

    // ✅ For very large files - chunked upload
    @Streaming
    @PUT("upload/{fileId}/chunk")
    suspend fun uploadChunk(
        @Path("fileId") fileId: String,
        @Header("Content-Range") contentRange: String,
        @Body chunk: RequestBody
    ): Response<ChunkResponse>
}
```

#### Retrofit Setup

```kotlin
private val okHttpClient = OkHttpClient.Builder()
    .connectTimeout(30, TimeUnit.SECONDS)
    .readTimeout(60, TimeUnit.SECONDS)  // ✅ Increased for large files
    .writeTimeout(60, TimeUnit.SECONDS) // ✅ Increased for upload
    .build()
```

#### FileUploadWorker

```kotlin
class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val filePath = inputData.getString(KEY_FILE_PATH) ?: return Result.failure()

        return try {
            // ✅ Foreground service with notification
            setForeground(createForegroundInfo(0))

            val file = File(filePath)
            if (!file.exists()) return Result.failure()

            val requestFile = file.asRequestBody("multipart/form-data".toMediaType())
            val filePart = MultipartBody.Part.createFormData("file", file.name, requestFile)

            val response = RetrofitClient.api.uploadFile(filePart, descriptionBody)

            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(workDataOf(KEY_FILE_URL to response.body()?.fileUrl))
            } else {
                Result.retry() // ✅ Automatic retry
            }
        } catch (e: Exception) {
            if (runAttemptCount < MAX_RETRIES) {
                Result.retry() // ✅ Exponential backoff
            } else {
                Result.failure(workDataOf(KEY_ERROR to e.message))
            }
        }
    }
}
```

#### Starting Upload

```kotlin
fun uploadFile(filePath: String): UUID {
    val constraints = Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED) // ✅ Requires network
        .build()

    val uploadRequest = OneTimeWorkRequestBuilder<FileUploadWorker>()
        .setInputData(workDataOf(KEY_FILE_PATH to filePath))
        .setConstraints(constraints)
        .setBackoffCriteria(
            BackoffPolicy.EXPONENTIAL,  // ✅ Exponential backoff
            WorkRequest.MIN_BACKOFF_MILLIS,
            TimeUnit.MILLISECONDS
        )
        .build()

    WorkManager.getInstance(context).enqueue(uploadRequest)
    return uploadRequest.id
}
```

### 2. Chunked Upload (files > 50 MB)

```kotlin
class ChunkedFileUploadWorker : CoroutineWorker() {
    override suspend fun doWork(): Result {
        val file = File(inputData.getString(KEY_FILE_PATH))
        val chunkSize = 1024 * 1024 * 5  // ✅ 5 MB per chunk

        file.inputStream().use { inputStream ->
            var uploadedBytes = 0L
            val buffer = ByteArray(chunkSize)

            while (uploadedBytes < file.length()) {
                val bytesRead = inputStream.read(buffer)
                if (bytesRead == -1) break

                val chunk = buffer.copyOf(bytesRead)
                val contentRange = "bytes $uploadedBytes-${uploadedBytes + bytesRead - 1}/${file.length()}"

                val response = api.uploadChunk(fileId, contentRange, chunk.toRequestBody())

                if (!response.isSuccessful) return Result.retry()

                uploadedBytes += bytesRead

                // ✅ Update progress
                val progress = (uploadedBytes * 100 / file.length()).toInt()
                setProgress(workDataOf(KEY_PROGRESS to progress))
            }
        }

        return Result.success()
    }
}
```

### 3. Progress Tracking

```kotlin
// ✅ Track progress via OkHttp Interceptor
class UploadProgressInterceptor(
    private val onProgress: (bytesUploaded: Long, totalBytes: Long) -> Unit
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        val progressBody = ProgressRequestBody(originalBody, onProgress)
        return chain.proceed(request.newBuilder().method(method, progressBody).build())
    }
}
```

### 4. Resumable Upload

```kotlin
suspend fun uploadWithResume(file: File): Result<String> {
    val uploadedBytes = getUploadProgress(fileId)  // ✅ Restore progress

    file.inputStream().use { stream ->
        stream.skip(uploadedBytes)  // ✅ Skip already uploaded

        // Continue upload from last position
        // Save progress after each chunk
    }
}
```

### Best Practices

1. **WorkManager** for guaranteed upload
2. **Chunked upload** for files > 50 MB (5 MB chunks)
3. **Progress tracking** for UX (OkHttp Interceptor)
4. **Retry logic** with exponential backoff
5. **Foreground Service** with notification
6. **WiFi-only constraint** for large files (`NetworkType.UNMETERED`)
7. **Resumable uploads** - save progress in SharedPreferences

```kotlin
// ❌ Don't use for large files
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)  // Any network
    .build()

// ✅ Use for large files
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED)  // WiFi only
    .build()
```

---

## Follow-ups

- How to implement file compression before upload?
- What are the trade-offs between chunked upload and multipart upload?
- How to handle upload cancellation and cleanup of partial uploads?
- What security considerations exist for file upload endpoints?
- How to implement upload priority queue for multiple files?

## References

- Android WorkManager documentation
- Retrofit and OkHttp best practices for file uploads
- HTTP multipart/form-data specification

## Related Questions

### Prerequisites
- Understanding Kotlin coroutines for async operations
- Background work strategies in Android (Service vs WorkManager)

### Related
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] - State preservation across configuration changes
- Foreground services for long-running operations

### Advanced
- Advanced networking optimization techniques (connection pooling, compression)
- Custom WorkManager constraints and scheduling strategies
