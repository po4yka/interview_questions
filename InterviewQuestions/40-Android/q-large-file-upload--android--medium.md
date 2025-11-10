---
id: android-116
title: Large File Upload / Загрузка больших файлов
aliases:
- Large File Upload
- Загрузка больших файлов
topic: android
subtopics:
- background-execution
- files-media
- networking-http
question_kind: android
difficulty: medium
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-retrofit
- c-background-tasks
- q-viewmodel-vs-onsavedinstancestate--android--medium
created: 2025-10-15
updated: 2025-11-10
sources: []
tags:
- android/background-execution
- android/files-media
- android/networking-http
- difficulty/medium
- file-upload
- multipart
- retrofit
- workmanager

---

# Вопрос (RU)

> Как загрузить большой файл на сервер в Android?

# Question (EN)

> How to upload large files to server in Android?

---

## Ответ (RU)

Для загрузки больших файлов используйте **WorkManager + Retrofit** для гарантированного выполнения в фоне. Ключевые требования: асинхронная обработка, устойчивость к `configuration changes`, `retry`-логика, отображение прогресса.

Ниже приведены примерные шаблоны (не полный рабочий код), демонстрирующие ключевые идеи.

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

    // Пример endpoint для chunked upload очень больших файлов
    // Обратите внимание: @Streaming применяется к ответу, а не к телу запроса,
    // здесь он обычно не нужен и приведён только как иллюстрация.
    @PUT("upload/{fileId}/chunk")
    suspend fun uploadChunk(
        @Path("fileId") fileId: String,
        @Header("Content-Range") contentRange: String,
        @Body chunk: RequestBody // обычно application/octet-stream
    ): Response<ChunkResponse>
}
```

#### Retrofit Setup

```kotlin
private val okHttpClient = OkHttpClient.Builder()
    .connectTimeout(30, TimeUnit.SECONDS)
    .readTimeout(60, TimeUnit.SECONDS)  // Увеличен для больших файлов
    .writeTimeout(60, TimeUnit.SECONDS) // Увеличен для upload
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
            // Запуск в foreground с уведомлением для долгих загрузок
            setForeground(createForegroundInfo(0))

            val file = File(filePath)
            if (!file.exists()) return Result.failure()

            val requestFile = file.asRequestBody("application/octet-stream".toMediaType())
            val filePart = MultipartBody.Part.createFormData("file", file.name, requestFile)

            // `descriptionBody`, `RetrofitClient` и т.п. предполагаются как предоставленные извне
            val response = RetrofitClient.api.uploadFile(filePart, descriptionBody)

            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(workDataOf(KEY_FILE_URL to response.body()?.fileUrl))
            } else {
                Result.retry() // Автоматический retry (с учётом политики WorkManager)
            }
        } catch (e: Exception) {
            return if (runAttemptCount < MAX_RETRIES) {
                Result.retry()
            } else {
                Result.failure(workDataOf(KEY_ERROR to (e.message ?: "Unknown error")))
            }
        }
    }
}
```

#### Starting Upload

```kotlin
fun uploadFile(filePath: String): UUID {
    val constraints = Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED) // Требуется сеть
        .build()

    val uploadRequest = OneTimeWorkRequestBuilder<FileUploadWorker>()
        .setInputData(workDataOf(KEY_FILE_PATH to filePath))
        .setConstraints(constraints)
        .setBackoffCriteria(
            BackoffPolicy.EXPONENTIAL,
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
class ChunkedFileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val filePath = inputData.getString(KEY_FILE_PATH) ?: return Result.failure()
        val file = File(filePath)
        if (!file.exists()) return Result.failure()

        val fileId = inputData.getString(KEY_FILE_ID) ?: return Result.failure()
        val chunkSize = 1024 * 1024 * 5  // 5 MB на chunk (пример)

        file.inputStream().use { inputStream ->
            var uploadedBytes = 0L
            val buffer = ByteArray(chunkSize)

            while (uploadedBytes < file.length()) {
                val bytesRead = inputStream.read(buffer)
                if (bytesRead == -1) break

                val chunk = buffer.copyOf(bytesRead)
                val contentRange = "bytes $uploadedBytes-${uploadedBytes + bytesRead - 1}/${file.length()}"

                val requestBody = chunk.toRequestBody("application/octet-stream".toMediaType())
                val response = api.uploadChunk(fileId, contentRange, requestBody)

                if (!response.isSuccessful) return Result.retry()

                uploadedBytes += bytesRead

                // Обновляем прогресс
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
// Отслеживание прогресса через обёртку над RequestBody
class UploadProgressInterceptor(
    private val onProgress: (bytesUploaded: Long, totalBytes: Long) -> Unit
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        val originalRequest = chain.request()
        val originalBody = originalRequest.body
            ?: return chain.proceed(originalRequest)

        val progressBody = ProgressRequestBody(originalBody, onProgress)
        val newRequest = originalRequest.newBuilder()
            .method(originalRequest.method, progressBody)
            .build()

        return chain.proceed(newRequest)
    }
}
```

### 4. Resumable Upload

```kotlin
suspend fun uploadWithResume(fileId: String, file: File): Result<String> {
    // `getUploadProgress` / `saveUploadProgress` — абстракции над хранилищем (SharedPreferences/БД)
    val uploadedBytes = getUploadProgress(fileId)

    file.inputStream().use { stream ->
        stream.skip(uploadedBytes)

        // Продолжить загрузку с последней позиции чанками,
        // после каждого успешного chunk сохранять прогресс.
        // Конкретная реализация зависит от серверного API.
    }

    return Result.success("ok") // заглушка
}
```

### Best Practices

1. **WorkManager** для надёжной фоновой загрузки.
2. **Chunked upload** для очень больших файлов (например, > 50 MB) с размером чанков, согласованным с сервером.
3. **Progress tracking** для лучшего UX (обёртка над `RequestBody` или OkHttp `Interceptor`).
4. **Retry logic** с exponential backoff (через конфигурацию WorkManager и обработку ошибок).
5. Foreground `Service` с уведомлением для долгих/критичных загрузок.
6. Ограничение только WiFi (`NetworkType.UNMETERED`) для больших файлов — по требованиям продукта и UX.
7. **Resumable uploads** — сохранение прогресса (`SharedPreferences`/БД) и поддержка продолжения на уровне серверного API.

```kotlin
// Пример: для некритичных по размеру файлов
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)  // Любая сеть
    .build()

// Пример: для очень больших файлов, когда важно не расходовать мобильный трафик
val largeFileConstraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED)  // Только WiFi
    .build()
```

---

## Answer (EN)

Use **WorkManager + Retrofit** to upload large files with guaranteed background execution. Key requirements: async processing, resilience to configuration changes, retry logic, and progress tracking.

The snippets below are templates (not full production-ready code) to illustrate key ideas.

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

    // Example endpoint for chunked upload of very large files
    // Note: @Streaming is for response streaming; it's usually not needed here.
    @PUT("upload/{fileId}/chunk")
    suspend fun uploadChunk(
        @Path("fileId") fileId: String,
        @Header("Content-Range") contentRange: String,
        @Body chunk: RequestBody // typically application/octet-stream
    ): Response<ChunkResponse>
}
```

#### Retrofit Setup

```kotlin
private val okHttpClient = OkHttpClient.Builder()
    .connectTimeout(30, TimeUnit.SECONDS)
    .readTimeout(60, TimeUnit.SECONDS)  // Increased for large files
    .writeTimeout(60, TimeUnit.SECONDS) // Increased for upload
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
            // Run as foreground for long-running uploads with a notification
            setForeground(createForegroundInfo(0))

            val file = File(filePath)
            if (!file.exists()) return Result.failure()

            val requestFile = file.asRequestBody("application/octet-stream".toMediaType())
            val filePart = MultipartBody.Part.createFormData("file", file.name, requestFile)

            // `descriptionBody`, `RetrofitClient` etc. are assumed to be provided externally
            val response = RetrofitClient.api.uploadFile(filePart, descriptionBody)

            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(workDataOf(KEY_FILE_URL to response.body()?.fileUrl))
            } else {
                Result.retry() // Automatic retry based on WorkManager policy
            }
        } catch (e: Exception) {
            return if (runAttemptCount < MAX_RETRIES) {
                Result.retry()
            } else {
                Result.failure(workDataOf(KEY_ERROR to (e.message ?: "Unknown error")))
            }
        }
    }
}
```

#### Starting Upload

```kotlin
fun uploadFile(filePath: String): UUID {
    val constraints = Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED) // Requires network
        .build()

    val uploadRequest = OneTimeWorkRequestBuilder<FileUploadWorker>()
        .setInputData(workDataOf(KEY_FILE_PATH to filePath))
        .setConstraints(constraints)
        .setBackoffCriteria(
            BackoffPolicy.EXPONENTIAL,
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
class ChunkedFileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val filePath = inputData.getString(KEY_FILE_PATH) ?: return Result.failure()
        val file = File(filePath)
        if (!file.exists()) return Result.failure()

        val fileId = inputData.getString(KEY_FILE_ID) ?: return Result.failure()
        val chunkSize = 1024 * 1024 * 5  // 5 MB per chunk (example)

        file.inputStream().use { inputStream ->
            var uploadedBytes = 0L
            val buffer = ByteArray(chunkSize)

            while (uploadedBytes < file.length()) {
                val bytesRead = inputStream.read(buffer)
                if (bytesRead == -1) break

                val chunk = buffer.copyOf(bytesRead)
                val contentRange = "bytes $uploadedBytes-${uploadedBytes + bytesRead - 1}/${file.length()}"

                val requestBody = chunk.toRequestBody("application/octet-stream".toMediaType())
                val response = api.uploadChunk(fileId, contentRange, requestBody)

                if (!response.isSuccessful) return Result.retry()

                uploadedBytes += bytesRead

                // Update progress
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
// Track progress via a wrapper around RequestBody
class UploadProgressInterceptor(
    private val onProgress: (bytesUploaded: Long, totalBytes: Long) -> Unit
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        val originalRequest = chain.request()
        val originalBody = originalRequest.body
            ?: return chain.proceed(originalRequest)

        val progressBody = ProgressRequestBody(originalBody, onProgress)
        val newRequest = originalRequest.newBuilder()
            .method(originalRequest.method, progressBody)
            .build()

        return chain.proceed(newRequest)
    }
}
```

### 4. Resumable Upload

```kotlin
suspend fun uploadWithResume(fileId: String, file: File): Result<String> {
    // `getUploadProgress` / `saveUploadProgress` are abstractions over storage (SharedPreferences/DB)
    val uploadedBytes = getUploadProgress(fileId)

    file.inputStream().use { stream ->
        stream.skip(uploadedBytes)

        // Continue uploading from the last position in chunks,
        // persisting progress after each successful chunk.
        // Exact implementation depends on the server API.
    }

    return Result.success("ok") // placeholder
}
```

### Best Practices

1. **WorkManager** for reliable background uploads.
2. **Chunked upload** for very large files (e.g., > 50 MB), with chunk size coordinated with the server.
3. **Progress tracking** for better UX (`RequestBody` wrapper / OkHttp `Interceptor`).
4. **Retry logic** with exponential backoff (via WorkManager configuration and error handling).
5. Foreground `Service` with a notification for long-running/critical uploads.
6. WiFi-only constraint (`NetworkType.UNMETERED`) for large files when appropriate.
7. **Resumable uploads** — persist progress (`SharedPreferences`/DB) and rely on server-side support for partial uploads.

```kotlin
// Example: for not-so-large files
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)  // Any network
    .build()

// Example: for very large files where mobile data usage should be avoided
val largeFileConstraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED)  // WiFi only
    .build()
```

---

## Дополнительные вопросы (RU)

- Как реализовать сжатие файла перед загрузкой?
- Каковы trade-off'ы между chunked upload и multipart upload?
- Как обрабатывать отмену загрузки и очистку частично загруженных данных?
- Какие меры безопасности важны для endpoint'ов загрузки файлов?
- Как реализовать очередь приоритезации загрузок для нескольких файлов?

## Follow-ups

- How to implement file compression before upload?
- What are the trade-offs between chunked upload and multipart upload?
- How to handle upload cancellation and cleanup of partial uploads?
- What security considerations exist for file upload endpoints?
- How to implement upload priority queue for multiple files?

## Ссылки (RU)

- Документация Android WorkManager
- Рекомендации по загрузке файлов с использованием Retrofit и OkHttp
- Спецификация HTTP multipart/form-data

## References

- Android WorkManager documentation
- Retrofit and OkHttp best practices for file uploads
- HTTP multipart/form-data specification

## Связанные вопросы (RU)

### Предварительные знания / Концепции

- [[c-retrofit]]
- [[c-background-tasks]]

### Предварительные требования

- Понимание корутин Kotlin для асинхронных операций
- Подходы к фоновым задачам в Android (`Service` vs WorkManager)

### Связанные

- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] — сохранение состояния при `configuration changes`
- Foreground services для долгих операций

### Продвинутое

- Продвинутые техники оптимизации сетевого взаимодействия (connection pooling, сжатие)
- Кастомные ограничения и стратегии планирования для WorkManager

## Related Questions

### Prerequisites / Concepts

- [[c-retrofit]]
- [[c-background-tasks]]

### Prerequisites

- Understanding Kotlin coroutines for async operations
- Background work strategies in Android (`Service` vs WorkManager)

### Related

- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] - State preservation across configuration changes
- Foreground services for long-running operations

### Advanced

- Advanced networking optimization techniques (connection pooling, compression)
- Custom WorkManager constraints and scheduling strategies
