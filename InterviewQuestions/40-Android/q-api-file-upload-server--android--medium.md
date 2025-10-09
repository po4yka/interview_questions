---
topic: android
tags:
  - android
  - android/networking
  - file-upload
  - http
  - multipart
  - networking
  - okhttp
  - retrofit
difficulty: medium
status: reviewed
---

# Какое API или другие инструменты будешь использовать для отправления файлов на сервер?

**English**: What API or tools would you use for uploading files to a server?

## Answer

For uploading files to a server in Android, you can use several APIs and libraries:

1. **Retrofit** (with Multipart) - Most popular, type-safe, easy to use
2. **OkHttp** - Lower-level, more control, direct HTTP client
3. **HttpURLConnection** - Standard Java API, no external dependencies

**Recommended:** **Retrofit** for most cases (simple, powerful, well-supported).

---

## Option 1: Retrofit (Recommended)

### Why Retrofit?

**Advantages:**
- ✅ Type-safe API declarations
- ✅ Automatic JSON/XML conversion
- ✅ Built on top of OkHttp (powerful)
- ✅ Easy multipart file upload
- ✅ Coroutines support
- ✅ Extensive documentation

---

### Implementation

#### 1. Add Dependencies

```kotlin
// build.gradle.kts
dependencies {
    // Retrofit
    implementation("com.squareup.retrofit2:retrofit:2.11.0")
    implementation("com.squareup.retrofit2:converter-gson:2.11.0")

    // OkHttp (for logging)
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
}
```

---

#### 2. Define API Interface

```kotlin
interface FileUploadApi {

    @Multipart
    @POST("upload")
    suspend fun uploadFile(
        @Part file: MultipartBody.Part,
        @Part("description") description: RequestBody
    ): Response<UploadResponse>

    @Multipart
    @POST("upload/multiple")
    suspend fun uploadMultipleFiles(
        @Part files: List<MultipartBody.Part>,
        @Part("userId") userId: RequestBody
    ): Response<UploadResponse>
}

data class UploadResponse(
    val success: Boolean,
    val fileUrl: String,
    val message: String
)
```

---

#### 3. Create Retrofit Instance

```kotlin
object RetrofitClient {

    private const val BASE_URL = "https://api.example.com/"

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    val api: FileUploadApi = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
        .create(FileUploadApi::class.java)
}
```

---

#### 4. Upload File

```kotlin
class FileUploadRepository {

    suspend fun uploadFile(file: File, description: String): Result<UploadResponse> {
        return try {
            // Create RequestBody from file
            val requestFile = file.asRequestBody("image/*".toMediaTypeOrNull())

            // Create MultipartBody.Part
            val filePart = MultipartBody.Part.createFormData(
                "file",           // Parameter name on server
                file.name,        // Original filename
                requestFile       // File content
            )

            // Create RequestBody for description
            val descriptionBody = description.toRequestBody("text/plain".toMediaTypeOrNull())

            // Upload
            val response = RetrofitClient.api.uploadFile(filePart, descriptionBody)

            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(IOException("Upload failed: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun uploadMultipleFiles(files: List<File>, userId: String): Result<UploadResponse> {
        return try {
            // Create MultipartBody.Part for each file
            val fileParts = files.map { file ->
                val requestFile = file.asRequestBody("image/*".toMediaTypeOrNull())
                MultipartBody.Part.createFormData("files", file.name, requestFile)
            }

            val userIdBody = userId.toRequestBody("text/plain".toMediaTypeOrNull())

            val response = RetrofitClient.api.uploadMultipleFiles(fileParts, userIdBody)

            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(IOException("Upload failed: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

---

#### 5. Use in ViewModel

```kotlin
class FileUploadViewModel(
    private val repository: FileUploadRepository
) : ViewModel() {

    private val _uploadState = MutableStateFlow<UploadState>(UploadState.Idle)
    val uploadState: StateFlow<UploadState> = _uploadState

    fun uploadFile(file: File, description: String) {
        viewModelScope.launch {
            _uploadState.value = UploadState.Loading

            repository.uploadFile(file, description)
                .onSuccess { response ->
                    _uploadState.value = UploadState.Success(response.fileUrl)
                }
                .onFailure { error ->
                    _uploadState.value = UploadState.Error(error.message ?: "Unknown error")
                }
        }
    }
}

sealed class UploadState {
    object Idle : UploadState()
    object Loading : UploadState()
    data class Success(val fileUrl: String) : UploadState()
    data class Error(val message: String) : UploadState()
}
```

---

#### 6. UI Integration

```kotlin
@Composable
fun FileUploadScreen(viewModel: FileUploadViewModel = viewModel()) {
    val uploadState by viewModel.uploadState.collectAsState()
    var selectedFile by remember { mutableStateOf<File?>(null) }

    val launcher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri ->
        uri?.let {
            selectedFile = uriToFile(it)
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Button(onClick = { launcher.launch("image/*") }) {
            Text("Select File")
        }

        selectedFile?.let { file ->
            Text("Selected: ${file.name}")

            Button(
                onClick = { viewModel.uploadFile(file, "My photo") },
                enabled = uploadState !is UploadState.Loading
            ) {
                Text("Upload")
            }
        }

        when (val state = uploadState) {
            is UploadState.Loading -> CircularProgressIndicator()
            is UploadState.Success -> Text("Uploaded: ${state.fileUrl}")
            is UploadState.Error -> Text("Error: ${state.message}", color = Color.Red)
            else -> {}
        }
    }
}
```

---

## Option 2: OkHttp (Direct)

### When to Use OkHttp Directly?

- Need fine-grained control over requests
- Don't want Retrofit abstraction
- Building custom upload logic

---

### Implementation

```kotlin
class OkHttpFileUploader {

    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    suspend fun uploadFile(file: File, url: String): String = withContext(Dispatchers.IO) {
        // Create multipart body
        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart(
                "file",
                file.name,
                file.asRequestBody("image/*".toMediaTypeOrNull())
            )
            .addFormDataPart("description", "Uploaded from Android")
            .build()

        // Create request
        val request = Request.Builder()
            .url(url)
            .post(requestBody)
            .addHeader("Authorization", "Bearer YOUR_TOKEN")
            .build()

        // Execute
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IOException("Upload failed: ${response.code}")
            }
            response.body?.string() ?: throw IOException("Empty response")
        }
    }

    suspend fun uploadFileWithProgress(
        file: File,
        url: String,
        onProgress: (Int) -> Unit
    ): String = withContext(Dispatchers.IO) {
        val requestBody = ProgressRequestBody(
            file.asRequestBody("image/*".toMediaTypeOrNull()),
            onProgress
        )

        val multipartBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("file", file.name, requestBody)
            .build()

        val request = Request.Builder()
            .url(url)
            .post(multipartBody)
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IOException("Upload failed: ${response.code}")
            }
            response.body?.string() ?: throw IOException("Empty response")
        }
    }
}

// Progress tracking
class ProgressRequestBody(
    private val requestBody: RequestBody,
    private val onProgress: (Int) -> Unit
) : RequestBody() {

    override fun contentType(): MediaType? = requestBody.contentType()

    override fun contentLength(): Long = requestBody.contentLength()

    override fun writeTo(sink: BufferedSink) {
        val totalLength = contentLength()
        val progressSink = object : ForwardingSink(sink) {
            var bytesWritten = 0L

            override fun write(source: Buffer, byteCount: Long) {
                super.write(source, byteCount)
                bytesWritten += byteCount
                val progress = (100 * bytesWritten / totalLength).toInt()
                onProgress(progress)
            }
        }

        val bufferedSink = progressSink.buffer()
        requestBody.writeTo(bufferedSink)
        bufferedSink.flush()
    }
}
```

---

## Option 3: HttpURLConnection (Standard Java API)

### When to Use?

- No external dependencies allowed
- Legacy codebases
- Very simple upload requirements

---

### Implementation

```kotlin
class HttpURLConnectionUploader {

    suspend fun uploadFile(file: File, uploadUrl: String): String = withContext(Dispatchers.IO) {
        val boundary = "===" + System.currentTimeMillis() + "==="
        val lineEnd = "\r\n"
        val twoHyphens = "--"

        val url = URL(uploadUrl)
        val connection = url.openConnection() as HttpURLConnection

        try {
            // Configure connection
            connection.apply {
                doInput = true
                doOutput = true
                useCaches = false
                requestMethod = "POST"
                setRequestProperty("Connection", "Keep-Alive")
                setRequestProperty("Content-Type", "multipart/form-data;boundary=$boundary")
            }

            // Write multipart data
            DataOutputStream(connection.outputStream).use { dos ->
                // File part
                dos.writeBytes(twoHyphens + boundary + lineEnd)
                dos.writeBytes("Content-Disposition: form-data; name=\"file\";filename=\"${file.name}\"$lineEnd")
                dos.writeBytes("Content-Type: image/*$lineEnd")
                dos.writeBytes(lineEnd)

                // Write file content
                FileInputStream(file).use { fis ->
                    fis.copyTo(dos)
                }

                dos.writeBytes(lineEnd)
                dos.writeBytes(twoHyphens + boundary + twoHyphens + lineEnd)

                dos.flush()
            }

            // Read response
            val responseCode = connection.responseCode
            if (responseCode == HttpURLConnection.HTTP_OK) {
                connection.inputStream.bufferedReader().use { it.readText() }
            } else {
                throw IOException("Upload failed: $responseCode")
            }
        } finally {
            connection.disconnect()
        }
    }
}
```

---

## Comparison

| Aspect | Retrofit | OkHttp | HttpURLConnection |
|--------|----------|--------|-------------------|
| **Ease of use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Type safety** | Yes | No | No |
| **Coroutines** | Built-in | Manual | Manual |
| **Progress tracking** | Via OkHttp | ✅ Easy | ✅ Manual |
| **Dependencies** | Retrofit + OkHttp | OkHttp | None |
| **Flexibility** | Medium | High | High |
| **Boilerplate** | Low | Medium | High |
| **Best for** | REST APIs | Custom uploads | No dependencies |

---

## Complete Example: Image Upload with Progress

```kotlin
// Repository
class ImageUploadRepository {

    private val api = RetrofitClient.api

    suspend fun uploadImage(
        imageFile: File,
        onProgress: (Int) -> Unit
    ): Result<String> {
        return try {
            // Create progress tracking request body
            val requestFile = imageFile.asRequestBody("image/*".toMediaTypeOrNull())
            val progressBody = ProgressRequestBody(requestFile, onProgress)

            val filePart = MultipartBody.Part.createFormData(
                "image",
                imageFile.name,
                progressBody
            )

            val response = api.uploadFile(
                file = filePart,
                description = "Image upload".toRequestBody()
            )

            if (response.isSuccessful) {
                Result.success(response.body()!!.fileUrl)
            } else {
                Result.failure(IOException("Upload failed: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

// ViewModel
class ImageUploadViewModel(
    private val repository: ImageUploadRepository
) : ViewModel() {

    private val _uploadProgress = MutableStateFlow(0)
    val uploadProgress: StateFlow<Int> = _uploadProgress

    private val _uploadState = MutableStateFlow<UploadState>(UploadState.Idle)
    val uploadState: StateFlow<UploadState> = _uploadState

    fun uploadImage(file: File) {
        viewModelScope.launch {
            _uploadState.value = UploadState.Loading
            _uploadProgress.value = 0

            repository.uploadImage(file) { progress ->
                _uploadProgress.value = progress
            }
                .onSuccess { url ->
                    _uploadState.value = UploadState.Success(url)
                    _uploadProgress.value = 100
                }
                .onFailure { error ->
                    _uploadState.value = UploadState.Error(error.message ?: "Unknown error")
                    _uploadProgress.value = 0
                }
        }
    }
}

// UI
@Composable
fun ImageUploadScreen(viewModel: ImageUploadViewModel = viewModel()) {
    val uploadState by viewModel.uploadState.collectAsState()
    val uploadProgress by viewModel.uploadProgress.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        when (val state = uploadState) {
            is UploadState.Loading -> {
                CircularProgressIndicator(progress = uploadProgress / 100f)
                Text("Uploading: $uploadProgress%")
            }
            is UploadState.Success -> {
                Text("Uploaded successfully!")
                AsyncImage(
                    model = state.fileUrl,
                    contentDescription = "Uploaded image"
                )
            }
            is UploadState.Error -> {
                Text("Error: ${state.message}", color = Color.Red)
            }
            else -> {
                Button(onClick = { /* Launch file picker */ }) {
                    Text("Select Image")
                }
            }
        }
    }
}
```

---

## Best Practices

### 1. Use WorkManager for Reliability

```kotlin
class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val fileUri = inputData.getString("file_uri") ?: return Result.failure()
        val file = File(fileUri)

        return try {
            val repository = ImageUploadRepository()
            repository.uploadImage(file) { }.getOrThrow()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// Schedule upload
val uploadRequest = OneTimeWorkRequestBuilder<FileUploadWorker>()
    .setInputData(workDataOf("file_uri" to file.path))
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(uploadRequest)
```

### 2. Compress Images Before Upload

```kotlin
suspend fun compressImage(file: File): File = withContext(Dispatchers.IO) {
    val bitmap = BitmapFactory.decodeFile(file.path)
    val compressedFile = File(context.cacheDir, "compressed_${file.name}")

    FileOutputStream(compressedFile).use { out ->
        bitmap.compress(Bitmap.CompressFormat.JPEG, 80, out)
    }

    compressedFile
}
```

### 3. Handle Permissions

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
```

---

## Summary

**For uploading files to server in Android:**

1. **Retrofit (Recommended)**
   - Type-safe, easy to use
   - Built-in multipart support
   - Coroutines integration
   - Use for REST APIs

2. **OkHttp**
   - More control, lower-level
   - Easy progress tracking
   - Use for custom upload logic

3. **HttpURLConnection**
   - Standard Java API
   - No dependencies
   - Use when dependencies not allowed

**Best practices:**
- Use WorkManager for reliable uploads
- Compress images before uploading
- Track upload progress
- Handle errors gracefully
- Add retry logic

---

## Ответ

Для отправки файлов на сервер в Android можно использовать:

1. **Retrofit** (с Multipart) - самый популярный, типобезопасный, простой в использовании
2. **OkHttp** - более низкоуровневый, больше контроля
3. **HttpURLConnection** - стандартный Java API, без внешних зависимостей

**Рекомендуется:** **Retrofit** для большинства случаев.

**Ключевые шаги:**
- Добавить зависимости Retrofit
- Создать API интерфейс с `@Multipart` и `@POST`
- Использовать `MultipartBody.Part` для файлов
- Обрабатывать прогресс загрузки через OkHttp Interceptor

