---
topic: android
tags:
  - android
  - android/background-processing
  - background-processing
  - file-upload
  - networking
  - retrofit
  - workmanager
difficulty: hard
status: reviewed
---

# Как бы реализовал приложение, которое может загружать большие файлы на сервер?

**English**: How would you implement an app that can upload large files to a server?

## Answer

To implement reliable **large file upload**, consider:

1. **WorkManager** for guaranteed background execution
2. **Retrofit** with multipart requests for upload
3. **Foreground Service** for user-visible uploads
4. **Progress tracking** with notifications
5. **Chunked upload** for very large files
6. **Retry logic** for failed uploads

---

## Complete Implementation

### Architecture

```
┌─────────────┐
│   Activity  │ ← User selects file
└──────┬──────┘
       │ Enqueue upload
       ↓
┌─────────────┐
│ WorkManager │ ← Schedules upload work
└──────┬──────┘
       │ Executes in background
       ↓
┌─────────────┐
│FileUploadWorker│ ← Uploads via Retrofit
└──────┬──────┘
       │ Shows progress notification
       ↓
┌─────────────┐
│   Server    │ ← Receives file
└─────────────┘
```

---

## Step 1: Setup Dependencies

### build.gradle (app)

```gradle
dependencies {
    // WorkManager
    implementation "androidx.work:work-runtime-ktx:2.8.1"

    // Retrofit
    implementation "com.squareup.retrofit2:retrofit:2.9.0"
    implementation "com.squareup.retrofit2:converter-gson:2.9.0"

    // OkHttp (for progress tracking)
    implementation "com.squareup.okhttp3:okhttp:4.11.0"
    implementation "com.squareup.okhttp3:logging-interceptor:4.11.0"

    // Coroutines
    implementation "org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3"
}
```

---

## Step 2: Create API Interface

```kotlin
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.*

interface FileUploadApi {

    @Multipart
    @POST("upload")
    suspend fun uploadFile(
        @Part file: MultipartBody.Part,
        @Part("description") description: RequestBody,
        @Part("userId") userId: RequestBody
    ): Response<UploadResponse>

    @Multipart
    @POST("upload/chunk")
    suspend fun uploadChunk(
        @Part file: MultipartBody.Part,
        @Part("chunkIndex") chunkIndex: RequestBody,
        @Part("totalChunks") totalChunks: RequestBody,
        @Part("uploadId") uploadId: RequestBody
    ): Response<ChunkUploadResponse>
}

data class UploadResponse(
    val success: Boolean,
    val fileUrl: String,
    val fileId: String,
    val message: String
)

data class ChunkUploadResponse(
    val success: Boolean,
    val chunkIndex: Int,
    val uploadId: String
)
```

---

## Step 3: Setup Retrofit with Progress Tracking

```kotlin
import okhttp3.*
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.io.IOException
import java.util.concurrent.TimeUnit

object RetrofitClient {

    private const val BASE_URL = "https://api.example.com/"

    fun create(
        onProgressUpdate: ((bytesWritten: Long, contentLength: Long) -> Unit)? = null
    ): FileUploadApi {
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

        val okHttpClient = OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .apply {
                if (onProgressUpdate != null) {
                    addInterceptor(ProgressInterceptor(onProgressUpdate))
                }
            }
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .writeTimeout(60, TimeUnit.SECONDS)
            .build()

        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(FileUploadApi::class.java)
    }
}

// Progress tracking interceptor
class ProgressInterceptor(
    private val onProgressUpdate: (bytesWritten: Long, contentLength: Long) -> Unit
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        val originalBody = originalRequest.body ?: return chain.proceed(originalRequest)

        val progressRequestBody = ProgressRequestBody(originalBody, onProgressUpdate)

        val progressRequest = originalRequest.newBuilder()
            .method(originalRequest.method, progressRequestBody)
            .build()

        return chain.proceed(progressRequest)
    }
}

class ProgressRequestBody(
    private val delegate: RequestBody,
    private val onProgressUpdate: (bytesWritten: Long, contentLength: Long) -> Unit
) : RequestBody() {

    override fun contentType(): MediaType? = delegate.contentType()

    override fun contentLength(): Long = delegate.contentLength()

    override fun writeTo(sink: BufferedSink) {
        val countingSink = CountingSink(sink, contentLength(), onProgressUpdate)
        val bufferedSink = countingSink.buffer()
        delegate.writeTo(bufferedSink)
        bufferedSink.flush()
    }
}

class CountingSink(
    delegate: Sink,
    private val contentLength: Long,
    private val onProgressUpdate: (bytesWritten: Long, contentLength: Long) -> Unit
) : ForwardingSink(delegate) {

    private var bytesWritten = 0L

    override fun write(source: Buffer, byteCount: Long) {
        super.write(source, byteCount)
        bytesWritten += byteCount
        onProgressUpdate(bytesWritten, contentLength)
    }
}
```

---

## Step 4: Create FileUploadWorker

```kotlin
import android.content.Context
import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.work.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File

class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    companion object {
        const val KEY_FILE_PATH = "file_path"
        const val KEY_DESCRIPTION = "description"
        const val KEY_USER_ID = "user_id"

        const val CHANNEL_ID = "file_upload_channel"
        const val NOTIFICATION_ID = 1
    }

    private val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

    override suspend fun doWork(): Result {
        // Get input data
        val filePath = inputData.getString(KEY_FILE_PATH) ?: return Result.failure()
        val description = inputData.getString(KEY_DESCRIPTION) ?: ""
        val userId = inputData.getString(KEY_USER_ID) ?: ""

        val file = File(filePath)
        if (!file.exists()) {
            return Result.failure(workDataOf("error" to "File not found"))
        }

        // Create notification channel
        createNotificationChannel()

        // Set as foreground service
        setForeground(createForegroundInfo(0))

        return try {
            // Upload file with progress tracking
            val result = uploadFile(file, description, userId)

            if (result) {
                showNotification("Upload Complete", "File uploaded successfully", 100)
                Result.success(workDataOf("result" to "Upload successful"))
            } else {
                Result.failure(workDataOf("error" to "Upload failed"))
            }

        } catch (e: Exception) {
            e.printStackTrace()

            // Retry on network errors
            if (e is IOException || e is java.net.SocketTimeoutException) {
                Result.retry()
            } else {
                Result.failure(workDataOf("error" to e.message))
            }
        }
    }

    private suspend fun uploadFile(file: File, description: String, userId: String): Boolean {
        val api = RetrofitClient.create { bytesWritten, contentLength ->
            val progress = (100 * bytesWritten / contentLength).toInt()
            setProgressAsync(workDataOf("progress" to progress))
            showNotification("Uploading...", file.name, progress)
        }

        // Create multipart request
        val requestFile = file.asRequestBody("application/octet-stream".toMediaTypeOrNull())
        val filePart = MultipartBody.Part.createFormData("file", file.name, requestFile)

        val descriptionBody = RequestBody.create("text/plain".toMediaTypeOrNull(), description)
        val userIdBody = RequestBody.create("text/plain".toMediaTypeOrNull(), userId)

        // Upload
        val response = api.uploadFile(filePart, descriptionBody, userIdBody)

        return response.isSuccessful && response.body()?.success == true
    }

    private fun createForegroundInfo(progress: Int): ForegroundInfo {
        createNotificationChannel()

        val notification = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setContentTitle("Uploading File")
            .setContentText("Upload in progress...")
            .setSmallIcon(android.R.drawable.stat_sys_upload)
            .setProgress(100, progress, false)
            .setOngoing(true)
            .build()

        return ForegroundInfo(NOTIFICATION_ID, notification)
    }

    private fun showNotification(title: String, content: String, progress: Int) {
        val notification = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setContentTitle(title)
            .setContentText(content)
            .setSmallIcon(android.R.drawable.stat_sys_upload)
            .setProgress(100, progress, false)
            .build()

        notificationManager.notify(NOTIFICATION_ID, notification)
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "File Upload",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "File upload progress"
            }
            notificationManager.createNotificationChannel(channel)
        }
    }
}
```

---

## Step 5: Enqueue Upload from Activity

```kotlin
import androidx.appcompat.app.AppCompatActivity
import androidx.work.*
import androidx.lifecycle.Observer
import android.net.Uri
import android.content.Intent
import android.provider.OpenableColumns

class MainActivity : AppCompatActivity() {

    private val workManager by lazy { WorkManager.getInstance(applicationContext) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        buttonSelectFile.setOnClickListener {
            selectFile()
        }
    }

    private fun selectFile() {
        val intent = Intent(Intent.ACTION_GET_CONTENT).apply {
            type = "*/*"
            addCategory(Intent.CATEGORY_OPENABLE)
        }
        startActivityForResult(intent, REQUEST_CODE_PICK_FILE)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)

        if (requestCode == REQUEST_CODE_PICK_FILE && resultCode == RESULT_OK) {
            data?.data?.let { uri ->
                uploadFile(uri)
            }
        }
    }

    private fun uploadFile(uri: Uri) {
        // Copy file to cache directory
        val file = copyFileToCache(uri)

        // Create upload request
        val uploadRequest = OneTimeWorkRequestBuilder<FileUploadWorker>()
            .setInputData(workDataOf(
                FileUploadWorker.KEY_FILE_PATH to file.absolutePath,
                FileUploadWorker.KEY_DESCRIPTION to "My file",
                FileUploadWorker.KEY_USER_ID to "user123"
            ))
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .setRequiresBatteryNotLow(true)
                    .build()
            )
            .setBackoffCriteria(
                BackoffPolicy.EXPONENTIAL,
                WorkRequest.MIN_BACKOFF_MILLIS,
                TimeUnit.MILLISECONDS
            )
            .build()

        // Enqueue work
        workManager.enqueue(uploadRequest)

        // Observe progress
        workManager.getWorkInfoByIdLiveData(uploadRequest.id)
            .observe(this, Observer { workInfo ->
                when (workInfo.state) {
                    WorkInfo.State.RUNNING -> {
                        val progress = workInfo.progress.getInt("progress", 0)
                        progressBar.progress = progress
                        textStatus.text = "Uploading: $progress%"
                    }

                    WorkInfo.State.SUCCEEDED -> {
                        progressBar.progress = 100
                        textStatus.text = "Upload complete!"
                        Toast.makeText(this, "File uploaded successfully", Toast.LENGTH_SHORT).show()
                    }

                    WorkInfo.State.FAILED -> {
                        val error = workInfo.outputData.getString("error")
                        textStatus.text = "Upload failed: $error"
                        Toast.makeText(this, "Upload failed: $error", Toast.LENGTH_LONG).show()
                    }

                    else -> {
                        textStatus.text = "Status: ${workInfo.state}"
                    }
                }
            })
    }

    private fun copyFileToCache(uri: Uri): File {
        val fileName = getFileName(uri)
        val cacheFile = File(cacheDir, fileName)

        contentResolver.openInputStream(uri)?.use { input ->
            cacheFile.outputStream().use { output ->
                input.copyTo(output)
            }
        }

        return cacheFile
    }

    private fun getFileName(uri: Uri): String {
        var name = "file_${System.currentTimeMillis()}"
        contentResolver.query(uri, null, null, null, null)?.use { cursor ->
            val nameIndex = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
            if (cursor.moveToFirst()) {
                name = cursor.getString(nameIndex)
            }
        }
        return name
    }

    companion object {
        private const val REQUEST_CODE_PICK_FILE = 1001
    }
}
```

---

## Advanced: Chunked Upload for Very Large Files

For files > 100MB, use **chunked upload**:

```kotlin
class ChunkedFileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    companion object {
        const val CHUNK_SIZE = 5 * 1024 * 1024 // 5MB chunks
    }

    override suspend fun doWork(): Result {
        val filePath = inputData.getString("file_path") ?: return Result.failure()
        val file = File(filePath)

        if (!file.exists()) return Result.failure()

        return try {
            uploadFileInChunks(file)
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }

    private suspend fun uploadFileInChunks(file: File) {
        val fileSize = file.length()
        val totalChunks = (fileSize / CHUNK_SIZE) + if (fileSize % CHUNK_SIZE != 0L) 1 else 0
        val uploadId = java.util.UUID.randomUUID().toString()

        file.inputStream().use { input ->
            var chunkIndex = 0
            val buffer = ByteArray(CHUNK_SIZE)

            while (true) {
                val bytesRead = input.read(buffer)
                if (bytesRead == -1) break

                val chunkFile = File(cacheDir, "chunk_$chunkIndex")
                chunkFile.writeBytes(buffer.copyOf(bytesRead))

                uploadChunk(chunkFile, chunkIndex, totalChunks.toInt(), uploadId)

                chunkFile.delete()
                chunkIndex++

                // Update progress
                val progress = (100 * chunkIndex / totalChunks).toInt()
                setProgressAsync(workDataOf("progress" to progress))
            }
        }
    }

    private suspend fun uploadChunk(
        chunkFile: File,
        chunkIndex: Int,
        totalChunks: Int,
        uploadId: String
    ) {
        val api = RetrofitClient.create()

        val requestFile = chunkFile.asRequestBody("application/octet-stream".toMediaTypeOrNull())
        val filePart = MultipartBody.Part.createFormData("chunk", chunkFile.name, requestFile)

        val chunkIndexBody = RequestBody.create("text/plain".toMediaTypeOrNull(), chunkIndex.toString())
        val totalChunksBody = RequestBody.create("text/plain".toMediaTypeOrNull(), totalChunks.toString())
        val uploadIdBody = RequestBody.create("text/plain".toMediaTypeOrNull(), uploadId)

        val response = api.uploadChunk(filePart, chunkIndexBody, totalChunksBody, uploadIdBody)

        if (!response.isSuccessful) {
            throw IOException("Chunk upload failed: ${response.code()}")
        }
    }
}
```

---

## Summary

**Key implementation components:**

1. **WorkManager** - Guaranteed execution
   ```kotlin
   val uploadRequest = OneTimeWorkRequestBuilder<FileUploadWorker>()
       .setConstraints(Constraints.Builder()
           .setRequiredNetworkType(NetworkType.CONNECTED)
           .build())
       .build()
   ```

2. **Retrofit** - Multipart upload
   ```kotlin
   @Multipart
   @POST("upload")
   suspend fun uploadFile(@Part file: MultipartBody.Part): Response<UploadResponse>
   ```

3. **Progress tracking** - Custom interceptor
   ```kotlin
   class ProgressInterceptor(
       private val onProgressUpdate: (bytesWritten: Long, contentLength: Long) -> Unit
   ) : Interceptor { ... }
   ```

4. **Foreground service** - User-visible notification
   ```kotlin
   setForeground(createForegroundInfo(progress))
   ```

5. **Retry logic** - Automatic retries on failure
   ```kotlin
   return Result.retry()
   ```

**Best practices:**
- - Use WorkManager for guaranteed execution
- - Show progress notifications
- - Handle network errors with retry
- - Use chunked upload for large files (>100MB)
- - Add constraints (network, battery)
- - Compress files before upload if possible
- - Clean up cache files after upload

---

## Ответ

Для реализации надежной **загрузки больших файлов**:

1. **WorkManager** - гарантированное выполнение в фоне
2. **Retrofit** - multipart запросы для загрузки
3. **Foreground Service** - уведомления для пользователя
4. **Progress tracking** - отслеживание прогресса
5. **Chunked upload** - разбиение на части для очень больших файлов
6. **Retry logic** - повтор при ошибках

**Пример:**

```kotlin
// Worker
class FileUploadWorker : CoroutineWorker() {
    override suspend fun doWork(): Result {
        val file = File(inputData.getString("file_path")!!)

        return try {
            uploadFile(file)
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// Activity
val uploadRequest = OneTimeWorkRequestBuilder<FileUploadWorker>()
    .setInputData(workDataOf("file_path" to file.absolutePath))
    .setConstraints(Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .build())
    .build()

WorkManager.getInstance(context).enqueue(uploadRequest)
```

**Лучшие практики:**
- Используйте WorkManager для надежности
- Показывайте прогресс через уведомления
- Обрабатывайте ошибки с повторами
- Используйте chunked upload для файлов >100MB

