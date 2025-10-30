---
id: 20251012-122779
title: API File Upload Server / Загрузка файлов на сервер через API
aliases: ["API File Upload Server", "Загрузка файлов на сервер через API"]
topic: android
subtopics: [files-media, networking-http]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-retrofit, c-okhttp, c-multipart-form-data, q-retrofit-library--android--medium, q-okhttp-interceptors-advanced--networking--medium]
sources: []
created: 2025-10-15
updated: 2025-10-29
tags: [android/files-media, android/networking-http, retrofit, okhttp, workmanager, difficulty/medium]
---
# Вопрос (RU)
> Как реализовать загрузку файлов на сервер через API в Android?

# Question (EN)
> How to implement file upload to a server via API in Android?

## Ответ (RU)

Загрузка файлов на сервер использует HTTP multipart/form-data. Основной подход — Retrofit с OkHttp. Критичны: обработка прогресса, фоновая загрузка через WorkManager, обработка ошибок сети.

**1. Retrofit API (базовая загрузка):**

```kotlin
interface FileUploadApi {
    @Multipart
    @POST("upload")
    suspend fun uploadFile(
        @Part file: MultipartBody.Part,
        @Part("metadata") metadata: RequestBody
    ): UploadResponse
}

// ✅ Suspend функция с Result для обработки ошибок
suspend fun uploadFile(file: File): Result<UploadResponse> = runCatching {
    val requestBody = file.asRequestBody("image/*".toMediaType())
    val part = MultipartBody.Part.createFormData("file", file.name, requestBody)
    api.uploadFile(part, metadata)
}
```

**2. Прогресс загрузки (OkHttp interceptor):**

```kotlin
// ✅ Обёртка RequestBody для отслеживания записи байтов
class ProgressRequestBody(
    private val delegate: RequestBody,
    private val onProgress: (uploaded: Long, total: Long) -> Unit
) : RequestBody() {
    override fun contentType() = delegate.contentType()
    override fun contentLength() = delegate.contentLength()

    override fun writeTo(sink: BufferedSink) {
        val total = contentLength()
        var uploaded = 0L

        delegate.writeTo(object : ForwardingSink(sink) {
            override fun write(source: Buffer, byteCount: Long) {
                super.write(source, byteCount)
                uploaded += byteCount
                onProgress(uploaded, total)
            }
        })
    }
}
```

**3. Фоновая загрузка (WorkManager):**

```kotlin
class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        val uri = inputData.getString("file_uri") ?: return Result.failure()

        return uploadFile(Uri.parse(uri)).fold(
            onSuccess = { Result.success() },
            onFailure = { e ->
                // ✅ Retry с exponential backoff при сетевых ошибках
                if (e is IOException && runAttemptCount < 3) {
                    Result.retry()
                } else {
                    Result.failure()
                }
            }
        )
    }
}

// Запуск загрузки
val request = OneTimeWorkRequestBuilder<FileUploadWorker>()
    .setInputData(workDataOf("file_uri" to uri.toString()))
    .setConstraints(Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .build())
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
    .build()
```

**4. Сжатие изображений перед загрузкой:**

```kotlin
// ✅ Уменьшаем размер для экономии трафика
suspend fun compressImage(uri: Uri): File = withContext(Dispatchers.IO) {
    val bitmap = BitmapFactory.decodeStream(contentResolver.openInputStream(uri))
    val compressed = File(cacheDir, "compressed_${System.currentTimeMillis()}.jpg")

    compressed.outputStream().use { out ->
        bitmap.compress(Bitmap.CompressFormat.JPEG, 80, out)
    }
    compressed
}
```

**Ключевые практики:**
- Используйте WorkManager для гарантированной доставки (переживает рестарт)
- Сжимайте изображения (80% JPEG качество оптимально)
- Добавьте retry с exponential backoff (3 попытки)
- Валидируйте размер/тип файла на клиенте (< 10MB для мобильных сетей)
- Обрабатывайте разрешения (READ_MEDIA_IMAGES для Android 13+)

## Answer (EN)

File upload to server uses HTTP multipart/form-data. Main approach is Retrofit with OkHttp. Critical aspects: progress tracking, background upload via WorkManager, network error handling.

**1. Retrofit API (basic upload):**

```kotlin
interface FileUploadApi {
    @Multipart
    @POST("upload")
    suspend fun uploadFile(
        @Part file: MultipartBody.Part,
        @Part("metadata") metadata: RequestBody
    ): UploadResponse
}

// ✅ Suspend function with Result for error handling
suspend fun uploadFile(file: File): Result<UploadResponse> = runCatching {
    val requestBody = file.asRequestBody("image/*".toMediaType())
    val part = MultipartBody.Part.createFormData("file", file.name, requestBody)
    api.uploadFile(part, metadata)
}
```

**2. Upload progress (OkHttp interceptor):**

```kotlin
// ✅ RequestBody wrapper to track byte writes
class ProgressRequestBody(
    private val delegate: RequestBody,
    private val onProgress: (uploaded: Long, total: Long) -> Unit
) : RequestBody() {
    override fun contentType() = delegate.contentType()
    override fun contentLength() = delegate.contentLength()

    override fun writeTo(sink: BufferedSink) {
        val total = contentLength()
        var uploaded = 0L

        delegate.writeTo(object : ForwardingSink(sink) {
            override fun write(source: Buffer, byteCount: Long) {
                super.write(source, byteCount)
                uploaded += byteCount
                onProgress(uploaded, total)
            }
        })
    }
}
```

**3. Background upload (WorkManager):**

```kotlin
class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        val uri = inputData.getString("file_uri") ?: return Result.failure()

        return uploadFile(Uri.parse(uri)).fold(
            onSuccess = { Result.success() },
            onFailure = { e ->
                // ✅ Retry with exponential backoff on network errors
                if (e is IOException && runAttemptCount < 3) {
                    Result.retry()
                } else {
                    Result.failure()
                }
            }
        )
    }
}

// Schedule upload
val request = OneTimeWorkRequestBuilder<FileUploadWorker>()
    .setInputData(workDataOf("file_uri" to uri.toString()))
    .setConstraints(Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .build())
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
    .build()
```

**4. Image compression before upload:**

```kotlin
// ✅ Reduce size to save bandwidth
suspend fun compressImage(uri: Uri): File = withContext(Dispatchers.IO) {
    val bitmap = BitmapFactory.decodeStream(contentResolver.openInputStream(uri))
    val compressed = File(cacheDir, "compressed_${System.currentTimeMillis()}.jpg")

    compressed.outputStream().use { out ->
        bitmap.compress(Bitmap.CompressFormat.JPEG, 80, out)
    }
    compressed
}
```

**Key practices:**
- Use WorkManager for guaranteed delivery (survives restart)
- Compress images (80% JPEG quality is optimal)
- Add retry with exponential backoff (3 attempts)
- Validate file size/type on client (< 10MB for mobile networks)
- Handle permissions (READ_MEDIA_IMAGES for Android 13+)

## Follow-ups

- How to implement resumable uploads for large files (100MB+)?
- What are the security risks of file uploads and how to mitigate them?
- How to handle multiple simultaneous file uploads?
- When should you use chunked transfer encoding vs. multipart?
- How to implement upload queue with priority and cancellation?

## References

- [[c-retrofit]]
- [[c-okhttp]]
- [[c-multipart-form-data]]
- [[q-retrofit-library--android--medium]]
- [[q-okhttp-interceptors-advanced--networking--medium]]
- https://developer.android.com/topic/libraries/architecture/workmanager
- https://square.github.io/okhttp/interceptors/
- https://square.github.io/retrofit/

## Related Questions

### Prerequisites (Easier)
- [[q-retrofit-library--android--medium]]
- [[q-files-permissions-android--android--easy]]

### Related (Same Level)
- [[q-okhttp-interceptors-advanced--networking--medium]]
- [[q-network-error-handling-strategies--networking--medium]]
- [[q-workmanager-background-tasks--android--medium]]

### Advanced (Harder)
- [[q-retrofit-modify-all-requests--android--hard]]
- [[q-network-request-deduplication--networking--hard]]
- [[q-chunked-file-upload-resume--android--hard]]