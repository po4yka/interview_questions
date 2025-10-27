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
related: [q-retrofit-library--android--medium, q-okhttp-interceptors-advanced--networking--medium, q-network-error-handling-strategies--networking--medium]
sources: []
created: 2025-10-15
updated: 2025-01-27
tags: [android/files-media, android/networking-http, difficulty/medium]
---
# Вопрос (RU)
> Как реализовать загрузку файлов на сервер через API в Android?

# Question (EN)
> How to implement file upload to a server via API in Android?

## Ответ (RU)

Для загрузки файлов используются HTTP multipart/form-data запросы. Основные подходы: Retrofit (рекомендуется), OkHttp, или прямой HTTP. Ключевые аспекты — multipart кодирование, обработка прогресса, фоновая загрузка через WorkManager.

**Retrofit (рекомендуется):**

```kotlin
interface FileUploadApi {
    @Multipart
    @POST("upload")
    suspend fun uploadFile(
        @Part file: MultipartBody.Part,
        @Part("description") description: RequestBody
    ): Response<UploadResponse>
}

suspend fun uploadFile(file: File): Result<UploadResponse> {
    // ✅ Используем suspend функцию
    val requestFile = file.asRequestBody("image/*".toMediaTypeOrNull())
    val filePart = MultipartBody.Part.createFormData("file", file.name, requestFile)

    val response = api.uploadFile(filePart, descriptionBody)
    return if (response.isSuccessful) {
        Result.success(response.body()!!)
    } else {
        Result.failure(IOException("Upload failed: ${response.code()}"))
    }
}
```

**Отслеживание прогресса:**

```kotlin
class ProgressRequestBody(
    private val file: File,
    private val onProgress: (Long, Long) -> Unit
) : RequestBody() {
    override fun writeTo(sink: BufferedSink) {
        val source = file.source()
        var totalBytesRead = 0L

        source.use { fileSource ->
            var bytesRead: Long
            // ✅ Читаем чанками 8KB
            while (fileSource.read(sink.buffer, 8192).also { bytesRead = it } != -1L) {
                totalBytesRead += bytesRead
                onProgress(totalBytesRead, file.length())
            }
        }
    }
}
```

**Фоновая загрузка через WorkManager:**

```kotlin
class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        val filePath = inputData.getString("file_path") ?: return Result.failure()
        val file = File(filePath)

        return try {
            // ✅ WorkManager автоматически переживает перезапуск
            val result = uploadFile(file)
            if (result.isSuccess) Result.success() else Result.retry()
        } catch (e: Exception) {
            Result.retry() // ✅ Автоматический retry при ошибке
        }
    }
}
```

**Ключевые практики:**
- Используйте Retrofit для REST API (type-safe)
- Сжимайте изображения перед загрузкой
- Реализуйте retry логику с экспоненциальной задержкой
- Используйте WorkManager для надёжной фоновой загрузки
- Проверяйте разрешения (READ_MEDIA_IMAGES для Android 13+)
- Валидируйте размер и тип файла на клиенте

## Answer (EN)

File uploads use HTTP multipart/form-data encoding. Main approaches: Retrofit (recommended), OkHttp, or direct HTTP. Key aspects include multipart encoding, progress tracking, and background uploads via WorkManager.

**Retrofit (recommended):**

```kotlin
interface FileUploadApi {
    @Multipart
    @POST("upload")
    suspend fun uploadFile(
        @Part file: MultipartBody.Part,
        @Part("description") description: RequestBody
    ): Response<UploadResponse>
}

suspend fun uploadFile(file: File): Result<UploadResponse> {
    // ✅ Use suspend function for coroutine support
    val requestFile = file.asRequestBody("image/*".toMediaTypeOrNull())
    val filePart = MultipartBody.Part.createFormData("file", file.name, requestFile)

    val response = api.uploadFile(filePart, descriptionBody)
    return if (response.isSuccessful) {
        Result.success(response.body()!!)
    } else {
        Result.failure(IOException("Upload failed: ${response.code()}"))
    }
}
```

**Progress tracking:**

```kotlin
class ProgressRequestBody(
    private val file: File,
    private val onProgress: (Long, Long) -> Unit
) : RequestBody() {
    override fun writeTo(sink: BufferedSink) {
        val source = file.source()
        var totalBytesRead = 0L

        source.use { fileSource ->
            var bytesRead: Long
            // ✅ Read in 8KB chunks
            while (fileSource.read(sink.buffer, 8192).also { bytesRead = it } != -1L) {
                totalBytesRead += bytesRead
                onProgress(totalBytesRead, file.length())
            }
        }
    }
}
```

**Background upload with WorkManager:**

```kotlin
class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        val filePath = inputData.getString("file_path") ?: return Result.failure()
        val file = File(filePath)

        return try {
            // ✅ WorkManager survives app restart automatically
            val result = uploadFile(file)
            if (result.isSuccess) Result.success() else Result.retry()
        } catch (e: Exception) {
            Result.retry() // ✅ Automatic retry on failure
        }
    }
}
```

**Key practices:**
- Use Retrofit for REST APIs (type-safe)
- Compress images before upload
- Implement retry logic with exponential backoff
- Use WorkManager for reliable background uploads
- Handle permissions (READ_MEDIA_IMAGES for Android 13+)
- Validate file type and size on client

## Follow-ups

- How to implement chunked file upload for large files?
- What are the differences between multipart/form-data and application/octet-stream?
- How to implement resumable uploads using HTTP range headers?
- What security validations should be performed before file upload?

## References

- [[q-retrofit-library--android--medium]]
- [[q-okhttp-interceptors-advanced--networking--medium]]

## Related Questions

### Prerequisites (Easier)
- [[q-retrofit-library--android--medium]]
- [[q-graphql-vs-rest--networking--easy]]

### Related (Same Level)
- [[q-okhttp-interceptors-advanced--networking--medium]]
- [[q-network-error-handling-strategies--networking--medium]]
- [[q-retrofit-usage-tutorial--android--medium]]

### Advanced (Harder)
- [[q-retrofit-modify-all-requests--android--hard]]
- [[q-network-request-deduplication--networking--hard]]