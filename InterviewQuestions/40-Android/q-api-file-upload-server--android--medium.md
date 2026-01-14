---
id: android-161
title: API File Upload Server / Загрузка файлов на сервер через API
aliases:
- API File Upload Server
- Загрузка файлов на сервер через API
topic: android
subtopics:
- background-execution
- files-media
- networking-http
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
sources: []
status: draft
moc: moc-android
related:
- c-okhttp
- c-workmanager
- q-android-storage-types--android--medium
- q-api-rate-limiting-throttling--android--medium
- q-large-file-upload--android--medium
- q-large-file-upload-app--android--hard
created: 2025-10-15
updated: 2025-11-10
tags:
- android/background-execution
- android/files-media
- android/networking-http
- difficulty/medium
- okhttp
- retrofit
- workmanager
anki_cards:
- slug: android-161-0-en
  language: en
  anki_id: 1768364266423
  synced_at: '2026-01-14T09:17:53.102973'
- slug: android-161-0-ru
  language: ru
  anki_id: 1768364266446
  synced_at: '2026-01-14T09:17:53.106274'
---
# Вопрос (RU)

> Как реализовать загрузку файлов на сервер через API в Android?

# Question (EN)

> How to implement file upload to a server via API in Android?

---

## Ответ (RU)

Загрузка файлов обычно реализуется через HTTP `multipart/form-data` с использованием [[c-retrofit|Retrofit]] и [[c-okhttp|OkHttp]]. Критические аспекты: формирование multipart-запроса, работа с `Uri` и `ContentResolver`, отслеживание прогресса, фоновая загрузка через [[c-workmanager|WorkManager]], обработка сетевых ошибок и сжатие изображений.

### 1. Базовая Загрузка Через Retrofit

```kotlin
interface FileUploadApi {
    @Multipart
    @POST("upload")
    suspend fun uploadFile(
        @Part file: MultipartBody.Part,
        @Part("description") description: RequestBody? = null
    ): Response<UploadResponse>
}

// Предполагается, что экземпляр FileUploadApi (uploadApi) создан через Retrofit и
// передан в место вызова (через DI или иным способом).

suspend fun uploadFile(
    context: Context,
    uri: Uri,
    descriptionText: String? = null,
    uploadApi: FileUploadApi
): Result<UploadResponse> = runCatching {
    val contentResolver = context.contentResolver

    val mimeType = contentResolver.getType(uri) ?: "application/octet-stream"

    val requestBody = object : RequestBody() {
        override fun contentType(): MediaType? = mimeType.toMediaTypeOrNull()
        override fun writeTo(sink: BufferedSink) {
            contentResolver.openInputStream(uri)?.use { input ->
                sink.writeAll(input.source())
            } ?: throw IOException("Cannot open input stream")
        }
    }

    val fileName = "upload_${System.currentTimeMillis()}"
    val part = MultipartBody.Part.createFormData("file", fileName, requestBody)

    val description = descriptionText
        ?.toRequestBody("text/plain".toMediaType())

    val response = uploadApi.uploadFile(part, description)
    if (!response.isSuccessful) throw HttpException(response)
    response.body() ?: throw IOException("Empty response body")
}
```

**Ключевые моменты**:
- `@Multipart` для `multipart/form-data`.
- `@Part` для отдельных полей.
- Для `Uri` используем `ContentResolver` (особенно важно с scoped storage и SAF).
- `Result<T>` через `runCatching` для безопасной обработки ошибок.
- `FileUploadApi` должен быть корректно создан (`Retrofit`) и передан в функцию (например, через DI).

### 2. Отслеживание Прогресса

```kotlin
// Обёртка RequestBody для отслеживания прогресса
class ProgressRequestBody(
    private val delegate: RequestBody,
    private val onProgress: (uploaded: Long, total: Long) -> Unit
) : RequestBody() {

    override fun contentType(): MediaType? = delegate.contentType()
    override fun contentLength(): Long = delegate.contentLength()

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

        val bufferedSink = forwardingSink.buffer()
        delegate.writeTo(bufferedSink)
        bufferedSink.flush()
    }
}

// Использование: оборачиваем исходный RequestBody
val baseRequestBody: RequestBody = /* исходный RequestBody для файла */
val progressBody = ProgressRequestBody(baseRequestBody) { uploaded, total ->
    val progress = if (total > 0) (uploaded * 100 / total).toInt() else 0
    _uploadProgress.value = progress
}

val part = MultipartBody.Part.createFormData("file", fileName, progressBody)
```

### 3. Фоновая Загрузка Через WorkManager

```kotlin
class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val uri = inputData.getString("file_uri")?.let(Uri::parse)
            ?: return Result.failure()

        return uploadFile(
            context = applicationContext,
            uri = uri,
            uploadApi = /* предоставить экземпляр FileUploadApi (через DI или ServiceLocator) */
        ).fold(
            onSuccess = {
                setProgressAsync(workDataOf("progress" to 100))
                Result.success()
            },
            onFailure = { e ->
                if (e is IOException && runAttemptCount < 3) {
                    Result.retry()
                } else {
                    Result.failure(workDataOf("error" to (e.message ?: "unknown error")))
                }
            }
        )
    }
}

// Планирование загрузки
val uploadRequest = OneTimeWorkRequestBuilder<FileUploadWorker>()
    .setInputData(workDataOf("file_uri" to uri.toString()))
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
    .build()

WorkManager.getInstance(context).enqueue(uploadRequest)
```

**Преимущества `WorkManager`**:
- Переживает рестарт приложения.
- Автоматический retry с backoff.
- Выполняется только при наличии сети (через `Constraints`).
- Поддержка прогресса задач.

### 4. Сжатие Изображений

```kotlin
// Уменьшаем размер для экономии трафика
suspend fun compressImage(
    context: Context,
    uri: Uri,
    quality: Int = 80
): File = withContext(Dispatchers.IO) {
    val contentResolver = context.contentResolver

    val bitmap = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
        ImageDecoder.decodeBitmap(ImageDecoder.createSource(contentResolver, uri))
    } else {
        @Suppress("DEPRECATION")
        MediaStore.Images.Media.getBitmap(contentResolver, uri)
    }

    val compressed = File(context.cacheDir, "compressed_${System.currentTimeMillis()}.jpg")
    compressed.outputStream().use { out ->
        bitmap.compress(Bitmap.CompressFormat.JPEG, quality, out)
    }
    compressed
}
```

### 5. Полный Пример `ViewModel`

```kotlin
class FileUploadViewModel @Inject constructor(
    private val uploadApi: FileUploadApi
) : ViewModel() {

    private val _uploadState = MutableStateFlow<UploadState>(UploadState.Idle)
    val uploadState = _uploadState.asStateFlow()

    fun uploadFile(context: Context, uri: Uri) {
        viewModelScope.launch {
            _uploadState.value = UploadState.Compressing
            val compressed = compressImage(context, uri)

            // Формат файла соответствует JPEG после сжатия
            val mimeType = "image/jpeg"
            val requestBody = compressed.asRequestBody(mimeType.toMediaType())

            val progressBody = ProgressRequestBody(requestBody) { uploaded, total ->
                val progress = if (total > 0) (uploaded * 100 / total).toInt() else 0
                _uploadState.value = UploadState.Uploading(progress)
            }

            val part = MultipartBody.Part.createFormData(
                "file",
                compressed.name,
                progressBody
            )

            val result = runCatching {
                val response = uploadApi.uploadFile(part)
                if (!response.isSuccessful) throw HttpException(response)
            }

            result.onSuccess {
                _uploadState.value = UploadState.Success
            }.onFailure {
                _uploadState.value = UploadState.Error(it.message)
            }
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
| Сжатие | JPEG 80% для фото | Баланс качества и размера |
| Retry | До 3 попыток с exponential backoff | Учитывает временные сетевые проблемы |
| Размер | < 10MB для мобильных сетей (по возможности) | Снижение риска таймаутов и ограничений |
| Фоновая загрузка | `WorkManager` вместо `Service` | Гарантированные условия выполнения, экономия батареи |
| Разрешения | В зависимости от API уровня: для API 33+ `READ_MEDIA_IMAGES` (при доступе к медиа), для ниже — `READ_EXTERNAL_STORAGE`; для SAF/Uri-провайдеров возможен доступ без явных storage-разрешений | Корректная работа с медиа-файлами и scoped storage |

## Answer (EN)

File upload is typically implemented using HTTP `multipart/form-data` via [[c-retrofit|Retrofit]] with [[c-okhttp|OkHttp]]. Critical aspects: building the multipart request, working with `Uri` and `ContentResolver`, progress tracking, background upload via [[c-workmanager|WorkManager]], network error handling, and image compression.

### 1. Basic Upload via Retrofit

```kotlin
interface FileUploadApi {
    @Multipart
    @POST("upload")
    suspend fun uploadFile(
        @Part file: MultipartBody.Part,
        @Part("description") description: RequestBody? = null
    ): Response<UploadResponse>
}

// Assume FileUploadApi (uploadApi) is created via Retrofit and
// injected or otherwise provided to the caller.

suspend fun uploadFile(
    context: Context,
    uri: Uri,
    descriptionText: String? = null,
    uploadApi: FileUploadApi
): Result<UploadResponse> = runCatching {
    val contentResolver = context.contentResolver

    val mimeType = contentResolver.getType(uri) ?: "application/octet-stream"

    val requestBody = object : RequestBody() {
        override fun contentType(): MediaType? = mimeType.toMediaTypeOrNull()
        override fun writeTo(sink: BufferedSink) {
            contentResolver.openInputStream(uri)?.use { input ->
                sink.writeAll(input.source())
            } ?: throw IOException("Cannot open input stream")
        }
    }

    val fileName = "upload_${System.currentTimeMillis()}"
    val part = MultipartBody.Part.createFormData("file", fileName, requestBody)

    val description = descriptionText
        ?.toRequestBody("text/plain".toMediaType())

    val response = uploadApi.uploadFile(part, description)
    if (!response.isSuccessful) throw HttpException(response)
    response.body() ?: throw IOException("Empty response body")
}
```

**Key points**:
- `@Multipart` for `multipart/form-data`.
- `@Part` for individual fields.
- Use `ContentResolver` with `Uri` (important for scoped storage and SAF).
- Use `Result<T>` / `runCatching` for safer error handling.
- Ensure `FileUploadApi` is properly created (`Retrofit`) and passed into the function (e.g., via DI).

### 2. Progress Tracking

```kotlin
// RequestBody wrapper to track upload progress
class ProgressRequestBody(
    private val delegate: RequestBody,
    private val onProgress: (uploaded: Long, total: Long) -> Unit
) : RequestBody() {

    override fun contentType(): MediaType? = delegate.contentType()
    override fun contentLength(): Long = delegate.contentLength()

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

        val bufferedSink = forwardingSink.buffer()
        delegate.writeTo(bufferedSink)
        bufferedSink.flush()
    }
}

// Usage: wrap the original RequestBody
val baseRequestBody: RequestBody = /* original RequestBody for file */
val progressBody = ProgressRequestBody(baseRequestBody) { uploaded, total ->
    val progress = if (total > 0) (uploaded * 100 / total).toInt() else 0
    _uploadProgress.value = progress
}

val part = MultipartBody.Part.createFormData("file", fileName, progressBody)
```

### 3. Background Upload via WorkManager

```kotlin
class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val uri = inputData.getString("file_uri")?.let(Uri::parse)
            ?: return Result.failure()

        return uploadFile(
            context = applicationContext,
            uri = uri,
            uploadApi = /* provide FileUploadApi instance (via DI or ServiceLocator) */
        ).fold(
            onSuccess = {
                setProgressAsync(workDataOf("progress" to 100))
                Result.success()
            },
            onFailure = { e ->
                if (e is IOException && runAttemptCount < 3) {
                    Result.retry()
                } else {
                    Result.failure(workDataOf("error" to (e.message ?: "unknown error")))
                }
            }
        )
    }
}

// Schedule upload
val uploadRequest = OneTimeWorkRequestBuilder<FileUploadWorker>()
    .setInputData(workDataOf("file_uri" to uri.toString()))
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
    .build()

WorkManager.getInstance(context).enqueue(uploadRequest)
```

**`WorkManager` advantages**:
- Survives app restart.
- Automatic retry with backoff.
- Runs only when network is available (via `Constraints`).
- Built-in support for reporting progress.

### 4. Image Compression

```kotlin
// Reduce size to save bandwidth
suspend fun compressImage(
    context: Context,
    uri: Uri,
    quality: Int = 80
): File = withContext(Dispatchers.IO) {
    val contentResolver = context.contentResolver

    val bitmap = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
        ImageDecoder.decodeBitmap(ImageDecoder.createSource(contentResolver, uri))
    } else {
        @Suppress("DEPRECATION")
        MediaStore.Images.Media.getBitmap(contentResolver, uri)
    }

    val compressed = File(context.cacheDir, "compressed_${System.currentTimeMillis()}.jpg")
    compressed.outputStream().use { out ->
        bitmap.compress(Bitmap.CompressFormat.JPEG, quality, out)
    }
    compressed
}
```

### 5. Complete `ViewModel` Example

```kotlin
class FileUploadViewModel @Inject constructor(
    private val uploadApi: FileUploadApi
) : ViewModel() {

    private val _uploadState = MutableStateFlow<UploadState>(UploadState.Idle)
    val uploadState = _uploadState.asStateFlow()

    fun uploadFile(context: Context, uri: Uri) {
        viewModelScope.launch {
            _uploadState.value = UploadState.Compressing
            val compressed = compressImage(context, uri)

            // The compressed file is JPEG, make MIME type consistent
            val mimeType = "image/jpeg"
            val requestBody = compressed.asRequestBody(mimeType.toMediaType())

            val progressBody = ProgressRequestBody(requestBody) { uploaded, total ->
                val progress = if (total > 0) (uploaded * 100 / total).toInt() else 0
                _uploadState.value = UploadState.Uploading(progress)
            }

            val part = MultipartBody.Part.createFormData(
                "file",
                compressed.name,
                progressBody
            )

            val result = runCatching {
                val response = uploadApi.uploadFile(part)
                if (!response.isSuccessful) throw HttpException(response)
            }

            result.onSuccess {
                _uploadState.value = UploadState.Success
            }.onFailure {
                _uploadState.value = UploadState.Error(it.message)
            }
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
| Compression | JPEG 80% for photos | Good quality-size balance |
| Retry | Up to 3 attempts with exponential backoff | Handles temporary network issues |
| Size | Prefer < 10MB over mobile networks when possible | Reduces risk of timeouts and carrier limits |
| Background upload | Use `WorkManager` instead of a plain `Service` | Better execution guarantees, battery efficiency |
| Permissions | Depends on API level: for API 33+ use `READ_MEDIA_IMAGES` when accessing shared media; below 33 use `READ_EXTERNAL_STORAGE`; for SAF/provider Uris you may rely on granted URI permissions without broad storage permission | Correct access to media under scoped storage |

---

## Follow-ups

- How to implement resumable uploads for large files (100MB+)?
- What are chunked transfer encoding advantages over multipart?
- How to handle multiple simultaneous file uploads with priority queue?
- What security measures should be implemented for file uploads?
- How to implement upload queue that survives app termination?

## References

- [[c-retrofit]] - `Retrofit` HTTP client basics
- [[c-okhttp]] - `OkHttp` interceptors and customization
- [[c-workmanager]] - `WorkManager` background tasks
- [WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager)
- https://square.github.io/retrofit/
- https://square.github.io/okhttp/

## Related Questions

### Prerequisites (Easier)

- Understanding `Retrofit` basics and HTTP requests
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
