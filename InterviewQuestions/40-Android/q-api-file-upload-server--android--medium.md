---
id: 20251012-122779
title: API File Upload Server / Загрузка файлов на сервер через API
aliases: ["API File Upload Server", "Загрузка файлов на сервер через API"]

# Classification
topic: android
subtopics: [networking-http, files-media, background-execution]
question_kind: android
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
sources: []

# Workflow & relations
status: draft
moc: moc-android
related: [c-retrofit, c-okhttp, c-multipart-form-data, c-workmanager]

# Timestamps
created: 2025-10-15
updated: 2025-10-30

tags: [android/networking-http, android/files-media, android/background-execution, retrofit, okhttp, workmanager, difficulty/medium]
---
# Вопрос (RU)

> Как реализовать загрузку файлов на сервер через API в Android?

# Question (EN)

> How to implement file upload to a server via API in Android?

---

## Ответ (RU)

Загрузка файлов использует HTTP multipart/form-data через [[c-retrofit|Retrofit]] с [[c-okhttp|OkHttp]]. Критические аспекты: отслеживание прогресса, фоновая загрузка через [[c-workmanager|WorkManager]], обработка сетевых ошибок и сжатие изображений.

### 1. Базовая загрузка через Retrofit

```kotlin
interface FileUploadApi {
    @Multipart
    @POST("upload")
    suspend fun uploadFile(
        @Part file: MultipartBody.Part,
        @Part("description") description: RequestBody
    ): Response<UploadResponse>
}

// ✅ Suspend функция с Result для обработки ошибок
suspend fun uploadFile(file: File): Result<UploadResponse> = runCatching {
    val requestBody = file.asRequestBody("image/*".toMediaType())
    val part = MultipartBody.Part.createFormData("file", file.name, requestBody)
    val description = "Photo upload".toRequestBody("text/plain".toMediaType())

    api.uploadFile(part, description).body() ?: throw IOException("Empty response")
}
```

**Ключевые моменты**:
- `@Multipart` для multipart/form-data
- `@Part` для отдельных полей
- `asRequestBody()` создает тело запроса с MIME типом
- `Result<T>` для безопасной обработки ошибок

### 2. Отслеживание прогресса

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
        val forwardingSink = object : ForwardingSink(sink) {
            override fun write(source: Buffer, byteCount: Long) {
                super.write(source, byteCount)
                uploaded += byteCount
                onProgress(uploaded, total)
            }
        }
        delegate.writeTo(forwardingSink.buffer())
    }
}

// Использование
val progressBody = ProgressRequestBody(requestBody) { uploaded, total ->
    val progress = (uploaded * 100 / total).toInt()
    _uploadProgress.value = progress
}
```

### 3. Фоновая загрузка через WorkManager

```kotlin
class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val uri = inputData.getString("file_uri")?.let(Uri::parse)
            ?: return Result.failure()

        return uploadFile(uri).fold(
            onSuccess = {
                setProgress(workDataOf("progress" to 100))
                Result.success()
            },
            onFailure = { e ->
                // ✅ Retry с exponential backoff при сетевых ошибках
                if (e is IOException && runAttemptCount < 3) {
                    Result.retry()
                } else {
                    Result.failure(workDataOf("error" to e.message))
                }
            }
        )
    }
}

// Планирование загрузки
val uploadRequest = OneTimeWorkRequestBuilder<FileUploadWorker>()
    .setInputData(workDataOf("file_uri" to uri.toString()))
    .setConstraints(Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .build())
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
    .build()

WorkManager.getInstance(context).enqueue(uploadRequest)
```

**Преимущества WorkManager**:
- Переживает рестарт приложения
- Автоматический retry с backoff
- Работает только при наличии сети
- Встроенный механизм прогресса

### 4. Сжатие изображений

```kotlin
// ✅ Уменьшаем размер для экономии трафика
suspend fun compressImage(uri: Uri, quality: Int = 80): File = withContext(Dispatchers.IO) {
    val bitmap = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
        ImageDecoder.decodeBitmap(ImageDecoder.createSource(contentResolver, uri))
    } else {
        @Suppress("DEPRECATION")
        MediaStore.Images.Media.getBitmap(contentResolver, uri)
    }

    val compressed = File(cacheDir, "compressed_${System.currentTimeMillis()}.jpg")
    compressed.outputStream().use { out ->
        bitmap.compress(Bitmap.CompressFormat.JPEG, quality, out)
    }
    compressed
}
```

### 5. Полный пример ViewModel

```kotlin
class FileUploadViewModel @Inject constructor(
    private val uploadApi: FileUploadApi,
    private val workManager: WorkManager
) : ViewModel() {

    private val _uploadState = MutableStateFlow<UploadState>(UploadState.Idle)
    val uploadState = _uploadState.asStateFlow()

    fun uploadFile(uri: Uri) {
        viewModelScope.launch {
            _uploadState.value = UploadState.Compressing
            val compressed = compressImage(uri)

            _uploadState.value = UploadState.Uploading(0)
            uploadApi.uploadFile(compressed).fold(
                onSuccess = { _uploadState.value = UploadState.Success },
                onFailure = { _uploadState.value = UploadState.Error(it.message) }
            )
        }
    }
}

sealed class UploadState {
    object Idle : UploadState()
    object Compressing : UploadState()
    data class Uploading(val progress: Int) : UploadState()
    object Success : UploadState()
    data class Error(val message: String?) : UploadState()
}
```

### Рекомендации

| Аспект | Рекомендация | Причина |
|--------|-------------|---------|
| **Сжатие** | JPEG 80% для фото | Оптимальный баланс качества и размера |
| **Retry** | 3 попытки с exponential backoff | Учитывает временные сетевые проблемы |
| **Размер** | < 10MB для мобильных сетей | Избегаем таймаутов и лимитов оператора |
| **Фоновая загрузка** | WorkManager вместо Service | Гарантированная доставка, экономия батареи |
| **Разрешения** | READ_MEDIA_IMAGES для Android 13+ | Granular media permissions |

## Answer (EN)

File upload uses HTTP multipart/form-data via [[c-retrofit|Retrofit]] with [[c-okhttp|OkHttp]]. Critical aspects: progress tracking, background upload via [[c-workmanager|WorkManager]], network error handling, and image compression.

### 1. Basic upload via Retrofit

```kotlin
interface FileUploadApi {
    @Multipart
    @POST("upload")
    suspend fun uploadFile(
        @Part file: MultipartBody.Part,
        @Part("description") description: RequestBody
    ): Response<UploadResponse>
}

// ✅ Suspend function with Result for error handling
suspend fun uploadFile(file: File): Result<UploadResponse> = runCatching {
    val requestBody = file.asRequestBody("image/*".toMediaType())
    val part = MultipartBody.Part.createFormData("file", file.name, requestBody)
    val description = "Photo upload".toRequestBody("text/plain".toMediaType())

    api.uploadFile(part, description).body() ?: throw IOException("Empty response")
}
```

**Key points**:
- `@Multipart` for multipart/form-data
- `@Part` for individual fields
- `asRequestBody()` creates request body with MIME type
- `Result<T>` for safe error handling

### 2. Progress tracking

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
        val forwardingSink = object : ForwardingSink(sink) {
            override fun write(source: Buffer, byteCount: Long) {
                super.write(source, byteCount)
                uploaded += byteCount
                onProgress(uploaded, total)
            }
        }
        delegate.writeTo(forwardingSink.buffer())
    }
}

// Usage
val progressBody = ProgressRequestBody(requestBody) { uploaded, total ->
    val progress = (uploaded * 100 / total).toInt()
    _uploadProgress.value = progress
}
```

### 3. Background upload via WorkManager

```kotlin
class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val uri = inputData.getString("file_uri")?.let(Uri::parse)
            ?: return Result.failure()

        return uploadFile(uri).fold(
            onSuccess = {
                setProgress(workDataOf("progress" to 100))
                Result.success()
            },
            onFailure = { e ->
                // ✅ Retry with exponential backoff on network errors
                if (e is IOException && runAttemptCount < 3) {
                    Result.retry()
                } else {
                    Result.failure(workDataOf("error" to e.message))
                }
            }
        )
    }
}

// Schedule upload
val uploadRequest = OneTimeWorkRequestBuilder<FileUploadWorker>()
    .setInputData(workDataOf("file_uri" to uri.toString()))
    .setConstraints(Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .build())
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
    .build()

WorkManager.getInstance(context).enqueue(uploadRequest)
```

**WorkManager advantages**:
- Survives app restart
- Automatic retry with backoff
- Works only with network connection
- Built-in progress mechanism

### 4. Image compression

```kotlin
// ✅ Reduce size to save bandwidth
suspend fun compressImage(uri: Uri, quality: Int = 80): File = withContext(Dispatchers.IO) {
    val bitmap = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
        ImageDecoder.decodeBitmap(ImageDecoder.createSource(contentResolver, uri))
    } else {
        @Suppress("DEPRECATION")
        MediaStore.Images.Media.getBitmap(contentResolver, uri)
    }

    val compressed = File(cacheDir, "compressed_${System.currentTimeMillis()}.jpg")
    compressed.outputStream().use { out ->
        bitmap.compress(Bitmap.CompressFormat.JPEG, quality, out)
    }
    compressed
}
```

### 5. Complete ViewModel example

```kotlin
class FileUploadViewModel @Inject constructor(
    private val uploadApi: FileUploadApi,
    private val workManager: WorkManager
) : ViewModel() {

    private val _uploadState = MutableStateFlow<UploadState>(UploadState.Idle)
    val uploadState = _uploadState.asStateFlow()

    fun uploadFile(uri: Uri) {
        viewModelScope.launch {
            _uploadState.value = UploadState.Compressing
            val compressed = compressImage(uri)

            _uploadState.value = UploadState.Uploading(0)
            uploadApi.uploadFile(compressed).fold(
                onSuccess = { _uploadState.value = UploadState.Success },
                onFailure = { _uploadState.value = UploadState.Error(it.message) }
            )
        }
    }
}

sealed class UploadState {
    object Idle : UploadState()
    object Compressing : UploadState()
    data class Uploading(val progress: Int) : UploadState()
    object Success : UploadState()
    data class Error(val message: String?) : UploadState()
}
```

### Recommendations

| Aspect | Recommendation | Reason |
|--------|---------------|--------|
| **Compression** | JPEG 80% for photos | Optimal quality-size balance |
| **Retry** | 3 attempts with exponential backoff | Handles temporary network issues |
| **Size** | < 10MB for mobile networks | Avoids timeouts and carrier limits |
| **Background upload** | WorkManager instead of Service | Guaranteed delivery, battery efficient |
| **Permissions** | READ_MEDIA_IMAGES for Android 13+ | Granular media permissions |

---

## Follow-ups

- How to implement resumable uploads for large files (100MB+)?
- What are chunked transfer encoding advantages over multipart?
- How to handle multiple simultaneous file uploads with priority queue?
- What security measures should be implemented for file uploads?
- How to implement upload queue that survives app termination?

## References

- [[c-retrofit]] - Retrofit HTTP client basics
- [[c-okhttp]] - OkHttp interceptors and customization
- [[c-multipart-form-data]] - Multipart form data specification
- [[c-workmanager]] - WorkManager background tasks
- https://developer.android.com/topic/libraries/architecture/workmanager
- https://square.github.io/retrofit/
- https://square.github.io/okhttp/

## Related Questions

### Prerequisites (Easier)

- Understanding Retrofit basics and HTTP requests
- File I/O and permissions in Android
- Coroutines and suspend functions

### Related (Medium)

- Network error handling strategies
- Progress tracking patterns in Android
- Image compression techniques

### Advanced (Harder)

- Resumable upload implementation with chunked transfer
- Multi-file upload orchestration with priority
- Network request deduplication for retry scenarios
