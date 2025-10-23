---
id: 20251012-122779
title: API File Upload Server / Загрузка файлов на сервер через API
aliases:
- API File Upload Server
- Загрузка файлов на сервер через API
topic: android
subtopics:
- networking-http
- files-media
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-android-testing-strategies--android--medium
- q-android-build-optimization--android--medium
- q-android-performance-measurement-tools--android--medium
created: 2025-10-15
updated: 2025-10-15
tags:
- android/networking-http
- android/files-media
- difficulty/medium
---

## Answer (EN)
**File Upload APIs** in Android include Retrofit (recommended), OkHttp, and HttpURLConnection for uploading files to servers via HTTP multipart requests.

**File Upload Theory:**
File uploads use HTTP multipart/form-data encoding to send binary data with metadata. The client creates multipart requests containing file content, headers, and form fields, which the server processes to store or process the uploaded files.

**1. Retrofit (Recommended):**

**API Interface Definition:**
Defines a type-safe interface for file upload endpoints using Retrofit annotations. The `@Multipart` annotation indicates multipart form data, `@POST` specifies the HTTP method, and `@Part` marks parameters for the multipart request. [[c-retrofit]] provides a powerful, type-safe HTTP client for Android.

```kotlin
// API Interface
interface FileUploadApi {
    @Multipart
    @POST("upload")
    suspend fun uploadFile(
        @Part file: MultipartBody.Part,
        @Part("description") description: RequestBody
    ): Response<UploadResponse>
}

// Upload Implementation
suspend fun uploadFile(file: File, description: String): Result<UploadResponse> {
    val requestFile = file.asRequestBody("image/*".toMediaTypeOrNull())
    val filePart = MultipartBody.Part.createFormData("file", file.name, requestFile)
    val descriptionBody = description.toRequestBody("text/plain".toMediaTypeOrNull())

    val response = api.uploadFile(filePart, descriptionBody)
    return if (response.isSuccessful) {
        Result.success(response.body()!!)
    } else {
        Result.failure(IOException("Upload failed: ${response.code()}"))
    }
}
```

**Upload Implementation:**
Converts the file to a RequestBody with proper MIME type, creates a MultipartBody.Part for the file data, converts the description string to RequestBody, and makes the API call. Returns a Result wrapper for success/failure handling.

**2. OkHttp (Direct HTTP):**

**Direct HTTP Implementation:**
Uses OkHttp directly without Retrofit for more control over the HTTP request. Builds a multipart request body manually, creates the HTTP request, and executes it on a background thread. Provides direct access to response handling and error management.

```kotlin
// Direct OkHttp Implementation
suspend fun uploadFile(file: File): Result<String> {
    val requestBody = MultipartBody.Builder()
        .setType(MultipartBody.FORM)
        .addFormDataPart("file", file.name, file.asRequestBody("image/*".toMediaTypeOrNull()))
        .build()

    val request = Request.Builder()
        .url("https://api.example.com/upload")
        .post(requestBody)
        .build()

    return withContext(Dispatchers.IO) {
        try {
            val response = okHttpClient.newCall(request).execute()
            if (response.isSuccessful) {
                Result.success(response.body?.string() ?: "")
            } else {
                Result.failure(IOException("Upload failed: ${response.code}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

**3. Progress Tracking:**

**Custom RequestBody for Progress:**
Creates a custom RequestBody that wraps file uploads to track progress. Reads the file in chunks and calls a progress callback with current and total bytes. This allows UI updates during upload without blocking the main thread.

```kotlin
// Progress Tracking with OkHttp
class ProgressRequestBody(
    private val file: File,
    private val contentType: MediaType?,
    private val onProgress: (Long, Long) -> Unit
) : RequestBody() {

    override fun contentLength(): Long = file.length()

    override fun contentType(): MediaType? = contentType

    override fun writeTo(sink: BufferedSink) {
        val source = file.source()
        var totalBytesRead = 0L
        val totalBytes = file.length()

        source.use { fileSource ->
            var bytesRead: Long
            while (fileSource.read(sink.buffer, 8192).also { bytesRead = it } != -1L) {
                totalBytesRead += bytesRead
                onProgress(totalBytesRead, totalBytes)
            }
        }
    }
}
```

**4. Multiple File Upload:**

**Batch File Upload Implementation:**
Handles uploading multiple files in a single request by converting each file to a MultipartBody.Part and sending them as a list. This is more efficient than individual uploads and reduces server round trips.

```kotlin
// Multiple Files Upload
suspend fun uploadMultipleFiles(files: List<File>): Result<UploadResponse> {
    val fileParts = files.map { file ->
        val requestFile = file.asRequestBody("image/*".toMediaTypeOrNull())
        MultipartBody.Part.createFormData("files", file.name, requestFile)
    }

    val response = api.uploadMultipleFiles(fileParts)
    return if (response.isSuccessful) {
        Result.success(response.body()!!)
    } else {
        Result.failure(IOException("Upload failed: ${response.code()}"))
    }
}
```

**5. Error Handling and Retry:**

**Exponential Backoff Retry Logic:**
Implements automatic retry with exponential backoff for failed uploads. Attempts the upload multiple times with increasing delays between attempts. This handles temporary network issues and improves upload reliability.

```kotlin
// Retry Logic
suspend fun uploadWithRetry(file: File, maxRetries: Int = 3): Result<UploadResponse> {
    repeat(maxRetries) { attempt ->
        try {
            val result = uploadFile(file)
            if (result.isSuccess) return result
        } catch (e: Exception) {
            if (attempt == maxRetries - 1) return Result.failure(e)
            delay(1000 * (attempt + 1)) // Exponential backoff
        }
    }
    return Result.failure(IOException("Upload failed after $maxRetries attempts"))
}
```

**6. WorkManager Integration:**

**Background Upload Worker:**
Uses WorkManager to handle file uploads in the background with automatic retry and system constraints. This ensures uploads continue even if the app is killed and provides reliable background processing for file uploads.

```kotlin
// WorkManager for Reliable Uploads
class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val filePath = inputData.getString("file_path") ?: return Result.failure()
        val file = File(filePath)

        return try {
            val result = uploadFile(file)
            if (result.isSuccess) {
                Result.success()
            } else {
                Result.retry()
            }
        } catch (e: Exception) {
            Result.retry()
        }
    }
}
```

**Best Practices:**
- Use Retrofit for REST APIs (type-safe, easy to use)
- Use OkHttp for custom upload logic and progress tracking
- Compress images before uploading to reduce bandwidth
- Implement retry logic for network failures
- Use WorkManager for reliable background uploads
- Handle permissions properly (READ_EXTERNAL_STORAGE, READ_MEDIA_IMAGES)
- Validate file types and sizes on client side
- Show upload progress to users

## Follow-ups

- How do you handle large file uploads without blocking the UI?
- What's the difference between multipart and binary upload?
- How do you implement resumable file uploads?
- What security considerations are important for file uploads?

## References

- [Retrofit Documentation](https://square.github.io/retrofit/)
- [OkHttp Documentation](https://square.github.io/okhttp/)

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]]
- [[q-android-project-parts--android--easy]]

### Related (Same Level)
- [[q-android-testing-strategies--android--medium]]
- [[q-android-build-optimization--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]