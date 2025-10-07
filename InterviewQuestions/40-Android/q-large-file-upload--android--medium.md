---
topic: android
tags:
  - android
  - file-upload
  - workmanager
  - retrofit
  - background-processing
  - multipart
difficulty: medium
status: draft
---

# Загрузка больших файлов на сервер в Android

**English**: How to upload large files to server in Android?

## Answer

Для реализации загрузки больших файлов необходимо учитывать: асинхронную обработку, устойчивость к изменениям конфигурации (rotation), восстановление после неудач, отображение прогресса и работу в фоновом режиме.

### 1. WorkManager + Retrofit (рекомендуемый подход)

#### Зависимости

```gradle
dependencies {
    // WorkManager
    implementation "androidx.work:work-runtime-ktx:2.9.0"

    // Retrofit
    implementation "com.squareup.retrofit2:retrofit:2.9.0"
    implementation "com.squareup.retrofit2:converter-gson:2.9.0"

    // OkHttp для логирования и настройки таймаутов
    implementation "com.squareup.okhttp3:okhttp:4.12.0"
    implementation "com.squareup.okhttp3:logging-interceptor:4.12.0"
}
```

#### API интерфейс

```kotlin
interface FileUploadApi {
    @Multipart
    @POST("upload")
    suspend fun uploadFile(
        @Part file: MultipartBody.Part,
        @Part("description") description: RequestBody
    ): Response<UploadResponse>

    // Для chunked upload (частями)
    @Streaming
    @PUT("upload/{fileId}/chunk")
    suspend fun uploadChunk(
        @Path("fileId") fileId: String,
        @Header("Content-Range") contentRange: String,
        @Body chunk: RequestBody
    ): Response<ChunkResponse>
}

data class UploadResponse(
    val success: Boolean,
    val fileUrl: String,
    val message: String
)

data class ChunkResponse(
    val received: Long,
    val total: Long
)
```

#### Retrofit setup с большими таймаутами

```kotlin
object RetrofitClient {
    private const val BASE_URL = "https://api.example.com/"

    private val okHttpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)  // Увеличен для больших файлов
        .writeTimeout(60, TimeUnit.SECONDS) // Увеличен для upload
        .addInterceptor(HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) {
                HttpLoggingInterceptor.Level.BODY
            } else {
                HttpLoggingInterceptor.Level.NONE
            }
        })
        .build()

    val retrofit: Retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    val api: FileUploadApi = retrofit.create(FileUploadApi::class.java)
}
```

#### FileUploadWorker

```kotlin
class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val filePath = inputData.getString(KEY_FILE_PATH) ?: return Result.failure()
        val description = inputData.getString(KEY_DESCRIPTION) ?: ""

        return try {
            // Показать notification о начале загрузки
            setForeground(createForegroundInfo(0))

            // Подготовить файл
            val file = File(filePath)
            if (!file.exists()) {
                return Result.failure(
                    workDataOf(KEY_ERROR to "File not found")
                )
            }

            // Создать MultipartBody.Part
            val requestFile = file.asRequestBody("multipart/form-data".toMediaType())
            val filePart = MultipartBody.Part.createFormData(
                "file",
                file.name,
                requestFile
            )

            val descriptionBody = description.toRequestBody("text/plain".toMediaType())

            // Отправить файл
            val response = RetrofitClient.api.uploadFile(filePart, descriptionBody)

            if (response.isSuccessful && response.body()?.success == true) {
                // Успешная загрузка
                Result.success(
                    workDataOf(
                        KEY_FILE_URL to response.body()?.fileUrl,
                        KEY_MESSAGE to "Upload successful"
                    )
                )
            } else {
                // Ошибка от сервера
                Result.retry()
            }

        } catch (e: Exception) {
            Log.e(TAG, "Upload failed", e)

            // Retry с экспоненциальной задержкой
            if (runAttemptCount < MAX_RETRIES) {
                Result.retry()
            } else {
                Result.failure(
                    workDataOf(KEY_ERROR to e.message)
                )
            }
        }
    }

    private fun createForegroundInfo(progress: Int): ForegroundInfo {
        val notification = NotificationCompat.Builder(
            applicationContext,
            CHANNEL_ID
        )
            .setContentTitle("Uploading file")
            .setContentText("Upload in progress...")
            .setSmallIcon(R.drawable.ic_upload)
            .setProgress(100, progress, false)
            .setOngoing(true)
            .build()

        return ForegroundInfo(NOTIFICATION_ID, notification)
    }

    companion object {
        const val TAG = "FileUploadWorker"
        const val KEY_FILE_PATH = "file_path"
        const val KEY_DESCRIPTION = "description"
        const val KEY_FILE_URL = "file_url"
        const val KEY_MESSAGE = "message"
        const val KEY_ERROR = "error"
        const val MAX_RETRIES = 3

        const val CHANNEL_ID = "file_upload_channel"
        const val NOTIFICATION_ID = 1001
    }
}
```

#### Запуск загрузки

```kotlin
class FileUploadManager(private val context: Context) {

    fun uploadFile(filePath: String, description: String): UUID {
        // Создать constraints
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(false)  // Можно загружать даже при низком заряде
            .build()

        // Создать WorkRequest
        val uploadRequest = OneTimeWorkRequestBuilder<FileUploadWorker>()
            .setInputData(
                workDataOf(
                    FileUploadWorker.KEY_FILE_PATH to filePath,
                    FileUploadWorker.KEY_DESCRIPTION to description
                )
            )
            .setConstraints(constraints)
            .setBackoffCriteria(
                BackoffPolicy.EXPONENTIAL,
                WorkRequest.MIN_BACKOFF_MILLIS,
                TimeUnit.MILLISECONDS
            )
            .addTag("file_upload")
            .build()

        // Enqueue работу
        WorkManager.getInstance(context).enqueue(uploadRequest)

        return uploadRequest.id
    }

    fun observeUpload(uploadId: UUID): LiveData<WorkInfo> {
        return WorkManager.getInstance(context)
            .getWorkInfoByIdLiveData(uploadId)
    }

    fun cancelUpload(uploadId: UUID) {
        WorkManager.getInstance(context).cancelWorkById(uploadId)
    }
}

// Использование в Activity/Fragment
class UploadActivity : AppCompatActivity() {
    private lateinit var uploadManager: FileUploadManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        uploadManager = FileUploadManager(this)

        uploadButton.setOnClickListener {
            val filePath = getSelectedFilePath()
            val uploadId = uploadManager.uploadFile(filePath, "My file description")

            // Наблюдать за прогрессом
            uploadManager.observeUpload(uploadId).observe(this) { workInfo ->
                when (workInfo.state) {
                    WorkInfo.State.RUNNING -> {
                        progressBar.visibility = View.VISIBLE
                        statusText.text = "Uploading..."
                    }
                    WorkInfo.State.SUCCEEDED -> {
                        progressBar.visibility = View.GONE
                        val fileUrl = workInfo.outputData.getString(
                            FileUploadWorker.KEY_FILE_URL
                        )
                        statusText.text = "Upload complete: $fileUrl"
                    }
                    WorkInfo.State.FAILED -> {
                        progressBar.visibility = View.GONE
                        val error = workInfo.outputData.getString(
                            FileUploadWorker.KEY_ERROR
                        )
                        statusText.text = "Upload failed: $error"
                    }
                    WorkInfo.State.CANCELLED -> {
                        progressBar.visibility = View.GONE
                        statusText.text = "Upload cancelled"
                    }
                    else -> {}
                }
            }
        }
    }
}
```

### 2. Chunked Upload (для очень больших файлов)

Разбиение файла на части (chunks) для загрузки.

```kotlin
class ChunkedFileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val filePath = inputData.getString(KEY_FILE_PATH) ?: return Result.failure()
        val file = File(filePath)

        if (!file.exists()) return Result.failure()

        val fileSize = file.length()
        val chunkSize = 1024 * 1024 * 5  // 5 MB per chunk
        val totalChunks = (fileSize + chunkSize - 1) / chunkSize

        return try {
            // Создать upload session на сервере
            val fileId = createUploadSession(file.name, fileSize)

            // Загрузить файл чанками
            file.inputStream().use { inputStream ->
                var uploadedBytes = 0L
                var chunkIndex = 0L

                val buffer = ByteArray(chunkSize.toInt())

                while (uploadedBytes < fileSize) {
                    val bytesRead = inputStream.read(buffer, 0, buffer.size)
                    if (bytesRead == -1) break

                    val chunk = buffer.copyOf(bytesRead)
                    val chunkBody = chunk.toRequestBody(
                        "application/octet-stream".toMediaType()
                    )

                    val contentRange = "bytes $uploadedBytes-${uploadedBytes + bytesRead - 1}/$fileSize"

                    val response = RetrofitClient.api.uploadChunk(
                        fileId,
                        contentRange,
                        chunkBody
                    )

                    if (!response.isSuccessful) {
                        return Result.retry()
                    }

                    uploadedBytes += bytesRead
                    chunkIndex++

                    // Обновить прогресс
                    val progress = (uploadedBytes * 100 / fileSize).toInt()
                    setProgress(workDataOf(KEY_PROGRESS to progress))
                    setForeground(createForegroundInfo(progress))
                }
            }

            Result.success(workDataOf(KEY_FILE_ID to fileId))

        } catch (e: Exception) {
            Log.e(TAG, "Chunked upload failed", e)
            Result.retry()
        }
    }

    private suspend fun createUploadSession(fileName: String, fileSize: Long): String {
        // Вызов API для создания upload session
        // Возвращает fileId для последующих chunk uploads
        return "file_${System.currentTimeMillis()}"
    }

    private fun createForegroundInfo(progress: Int): ForegroundInfo {
        val notification = NotificationCompat.Builder(
            applicationContext,
            CHANNEL_ID
        )
            .setContentTitle("Uploading large file")
            .setContentText("Progress: $progress%")
            .setSmallIcon(R.drawable.ic_upload)
            .setProgress(100, progress, false)
            .setOngoing(true)
            .build()

        return ForegroundInfo(NOTIFICATION_ID, notification)
    }

    companion object {
        const val TAG = "ChunkedUpload"
        const val KEY_FILE_PATH = "file_path"
        const val KEY_FILE_ID = "file_id"
        const val KEY_PROGRESS = "progress"
        const val CHANNEL_ID = "chunked_upload_channel"
        const val NOTIFICATION_ID = 1002
    }
}
```

### 3. Progress tracking с OkHttp Interceptor

```kotlin
class UploadProgressInterceptor(
    private val onProgress: (bytesUploaded: Long, totalBytes: Long) -> Unit
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        val originalRequest = chain.request()

        val progressRequestBody = originalRequest.body?.let {
            ProgressRequestBody(it, onProgress)
        }

        val progressRequest = originalRequest.newBuilder()
            .method(originalRequest.method, progressRequestBody)
            .build()

        return chain.proceed(progressRequest)
    }
}

class ProgressRequestBody(
    private val delegate: RequestBody,
    private val onProgress: (bytesUploaded: Long, totalBytes: Long) -> Unit
) : RequestBody() {

    override fun contentType() = delegate.contentType()

    override fun contentLength() = delegate.contentLength()

    override fun writeTo(sink: BufferedSink) {
        val totalBytes = contentLength()
        var uploadedBytes = 0L

        val progressSink = object : ForwardingSink(sink) {
            override fun write(source: Buffer, byteCount: Long) {
                super.write(source, byteCount)
                uploadedBytes += byteCount
                onProgress(uploadedBytes, totalBytes)
            }
        }

        val bufferedSink = progressSink.buffer()
        delegate.writeTo(bufferedSink)
        bufferedSink.flush()
    }
}

// Использование
val client = OkHttpClient.Builder()
    .addInterceptor(UploadProgressInterceptor { uploaded, total ->
        val progress = (uploaded * 100 / total).toInt()
        Log.d("Upload", "Progress: $progress%")
    })
    .build()
```

### 4. Resumable upload (с возобновлением)

```kotlin
class ResumableUploadManager(
    private val context: Context,
    private val api: FileUploadApi
) {
    private val prefs = context.getSharedPreferences("uploads", Context.MODE_PRIVATE)

    suspend fun uploadWithResume(file: File): Result<String> {
        val fileId = getOrCreateUploadSession(file)
        val uploadedBytes = getUploadProgress(fileId)

        return try {
            file.inputStream().use { inputStream ->
                inputStream.skip(uploadedBytes)

                val chunkSize = 1024 * 1024 * 5L
                val buffer = ByteArray(chunkSize.toInt())
                var currentPosition = uploadedBytes

                while (currentPosition < file.length()) {
                    val bytesRead = inputStream.read(buffer)
                    if (bytesRead == -1) break

                    val chunk = buffer.copyOf(bytesRead)
                    val response = api.uploadChunk(
                        fileId,
                        "bytes $currentPosition-${currentPosition + bytesRead - 1}/${file.length()}",
                        chunk.toRequestBody()
                    )

                    if (!response.isSuccessful) {
                        // Сохранить прогресс
                        saveUploadProgress(fileId, currentPosition)
                        return Result.failure(Exception("Upload failed at $currentPosition"))
                    }

                    currentPosition += bytesRead
                    saveUploadProgress(fileId, currentPosition)
                }
            }

            // Очистить прогресс после успешной загрузки
            clearUploadProgress(fileId)
            Result.success(fileId)

        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private fun getOrCreateUploadSession(file: File): String {
        val existingId = prefs.getString("upload_${file.absolutePath}", null)
        return existingId ?: "upload_${System.currentTimeMillis()}"
    }

    private fun getUploadProgress(fileId: String): Long {
        return prefs.getLong("progress_$fileId", 0L)
    }

    private fun saveUploadProgress(fileId: String, bytes: Long) {
        prefs.edit().putLong("progress_$fileId", bytes).apply()
    }

    private fun clearUploadProgress(fileId: String) {
        prefs.edit()
            .remove("progress_$fileId")
            .remove("upload_$fileId")
            .apply()
    }
}
```

### Best Practices

1. **Используйте WorkManager** для гарантированной загрузки
2. **Chunked upload** для файлов > 50 MB
3. **Progress tracking** для UX
4. **Retry logic** с exponential backoff
5. **Notification** для фонового процесса
6. **Compression** перед загрузкой (если применимо)
7. **WiFi-only constraint** для больших файлов
8. **Resumable uploads** для плохого интернета

```kotlin
// Оптимальная конфигурация
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED)  // Only WiFi
    .setRequiresCharging(false)
    .build()
```

**English**: Upload large files using **WorkManager + Retrofit** for guaranteed background execution. Use **Multipart** for files < 50MB, **chunked upload** for larger files (5MB chunks). Implement progress tracking with **UploadProgressInterceptor**, resumable uploads with progress persistence, foreground service notification. Configure OkHttp with increased timeouts (60s read/write). Use constraints for WiFi-only uploads. Retry with exponential backoff on failure. Save upload progress in SharedPreferences for resume capability.
