---
id: android-266
title: "Large File Upload App / Загрузка больших файлов в приложении"
aliases: [File Upload Android, Large File Upload, WorkManager Upload, Загрузка больших файлов]
topic: android
subtopics: [background-execution, coroutines, networking-http]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android, c-coroutines, q-android-testing-strategies--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android/background-execution, android/coroutines, android/networking-http, background-processing, difficulty/hard, file-upload, foreground-service, networking, retrofit, workmanager]

date created: Saturday, November 1st 2025, 1:24:41 pm
date modified: Tuesday, November 25th 2025, 8:53:59 pm
---
# Вопрос (RU)

> Как бы вы реализовали приложение, которое может загружать большие файлы на сервер?

# Question (EN)

> How would you implement an app that can upload large files to a server?

---

## Ответ (RU)

### Краткий Вариант

- Использовать `WorkManager` с `ForegroundInfo` для надёжного фонового выполнения загрузки с уведомлением (best-effort с учётом системных ограничений).
- Реализовать загрузку больших файлов через `Retrofit`/`OkHttp` с `ProgressRequestBody` для отслеживания прогресса.
- Для очень больших файлов использовать chunked upload с возможностью повторных попыток.

### Подробный Вариант

### Требования

- Функциональные:
  - Загрузка больших файлов (сотни МБ и более).
  - Отслеживание прогресса.
  - Корректная работа при сворачивании/перезапуске приложения.
  - Обработка ошибок сети и повторные попытки.
- Нефункциональные:
  - Не блокировать UI-поток.
  - Соблюдать ограничения Android на фоновые операции.
  - Минимизировать использование памяти и батареи.

### Архитектура Решения

**Ключевые компоненты:**

1. **WorkManager** - надёжное планирование и выполнение в фоне (с поддержкой foreground-режима).
2. **Retrofit + OkHttp** - multipart загрузка с прогрессом.
3. **Foreground (WorkManager + ForegroundInfo)** - видимая пользователю длительная операция.
4. **Chunked Upload** - разбиение на части для файлов >100MB (по согласованному с backend протоколу).
5. **Retry Logic** - автоматические повторы при сетевых ошибках.

### Реализация

#### 1. API Интерфейс

```kotlin
interface FileUploadApi {
    @Multipart
    @POST("upload")
    suspend fun uploadFile(
        @Part file: MultipartBody.Part,
        @Part("metadata") metadata: RequestBody
    ): Response<UploadResponse>

    @Multipart
    @POST("upload/chunk")
    suspend fun uploadChunk(
        @Part chunk: MultipartBody.Part,
        @Part("index") index: RequestBody,
        @Part("total") total: RequestBody,
        @Part("uploadId") uploadId: RequestBody
    ): Response<ChunkResponse>
}
```

#### 2. Отслеживание Прогресса

```kotlin
class ProgressRequestBody(
    private val delegate: RequestBody,
    private val onProgress: (Long, Long) -> Unit
) : RequestBody() {
    override fun contentType() = delegate.contentType()
    override fun contentLength() = delegate.contentLength()

    override fun writeTo(sink: BufferedSink) {
        val countingSink = CountingSink(sink, contentLength(), onProgress)
        val bufferedSink = countingSink.buffer()
        delegate.writeTo(bufferedSink)
        bufferedSink.flush()
        // В реальной реализации стоит также учитывать отмену корутин / запроса
    }
}

class CountingSink(
    delegate: Sink,
    private val total: Long,
    private val onProgress: (Long, Long) -> Unit
) : ForwardingSink(delegate) {
    private var written = 0L

    override fun write(source: Buffer, byteCount: Long) {
        super.write(source, byteCount)
        written += byteCount
        onProgress(written, total)
    }
}
```

Пример интеграции с OkHttp:

```kotlin
// Пример: оборачиваем исходный RequestBody в ProgressRequestBody перед созданием MultipartBody.Part
val original = file.asRequestBody("application/octet-stream".toMediaType())
val progressBody = ProgressRequestBody(original) { written, total ->
    val progress = if (total > 0) (100L * written / total).toInt() else 0
    setProgressAsync(workDataOf("progress" to progress))
}
val filePart = MultipartBody.Part.createFormData("file", file.name, progressBody)
```

#### 3. FileUploadWorker

```kotlin
class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val filePath = inputData.getString(KEY_FILE_PATH) ?: return Result.failure()
        val file = File(filePath)

        if (!file.exists()) return Result.failure()

        createNotificationChannel() // placeholder: создать канал уведомлений
        setForeground(createForegroundInfo(0))

        return try {
            val success = uploadFile(file)
            if (success) {
                showNotification("Завершено", file.name, 100) // placeholder
                Result.success()
            } else {
                // HTTP-ошибки 4xx/5xx здесь трактуем как неуспех без автоповтора (политика может настраиваться)
                Result.failure()
            }
        } catch (e: IOException) {
            // Сетевые ошибки: даём WorkManager возможность повторить по backoff-политике
            Result.retry()
        } catch (e: Exception) {
            Result.failure(workDataOf("error" to e.message))
        }
    }

    private suspend fun uploadFile(file: File): Boolean {
        val api = RetrofitClient.create { written, total -> // RetrofitClient: placeholder фабрики Retrofit
            val progress = if (total > 0) (100L * written / total).toInt() else 0
            setProgressAsync(workDataOf("progress" to progress))
            showNotification("Загрузка...", file.name, progress) // placeholder
        }

        val requestFile = file.asRequestBody("application/octet-stream".toMediaType())
        val filePart = MultipartBody.Part.createFormData("file", file.name, requestFile)

        val response = api.uploadFile(filePart, createMetadata()) // createMetadata: placeholder
        return response.isSuccessful
    }

    private fun createForegroundInfo(progress: Int) = ForegroundInfo(
        NOTIFICATION_ID, // placeholder константы
        NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setContentTitle("Загрузка файла")
            .setSmallIcon(android.R.drawable.stat_sys_upload)
            .setProgress(100, progress, false)
            .setOngoing(true)
            .build()
    )
}
```

#### 4. Запуск Загрузки

```kotlin
class MainActivity : AppCompatActivity() {
    private val workManager by lazy { WorkManager.getInstance(this) }

    private fun uploadFile(uri: Uri) {
        val file = copyToCache(uri) // placeholder: копирование в доступный путь

        val uploadRequest = OneTimeWorkRequestBuilder<FileUploadWorker>()
            .setInputData(workDataOf(KEY_FILE_PATH to file.absolutePath))
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED) // Только при сети
                    .setRequiresBatteryNotLow(true) // Батарея не разряжена
                    .build()
            )
            .setBackoffCriteria(
                BackoffPolicy.EXPONENTIAL,
                WorkRequest.MIN_BACKOFF_MILLIS,
                TimeUnit.MILLISECONDS
            )
            .build()

        workManager.enqueue(uploadRequest)

        // Наблюдение за прогрессом
        workManager.getWorkInfoByIdLiveData(uploadRequest.id)
            .observe(this) { workInfo ->
                when (workInfo.state) {
                    WorkInfo.State.RUNNING -> {
                        val progress = workInfo.progress.getInt("progress", 0)
                        updateProgress(progress) // placeholder UI-обновления
                    }
                    WorkInfo.State.SUCCEEDED -> showSuccess() // placeholder
                    WorkInfo.State.FAILED -> showError() // placeholder
                    else -> {}
                }
            }
    }
}
```

#### 5. Chunked Upload Для Больших Файлов

```kotlin
class ChunkedUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    companion object {
        const val CHUNK_SIZE = 5 * 1024 * 1024 // 5MB
    }

    override suspend fun doWork(): Result {
        val filePath = inputData.getString(KEY_FILE_PATH) ?: return Result.failure()
        val file = File(filePath)
        if (!file.exists()) return Result.failure()

        // Для реально больших файлов и долгих загрузок рекомендуется также вызывать setForeground()
        // с ForegroundInfo, аналогично FileUploadWorker

        return try {
            uploadInChunks(file)
            Result.success()
        } catch (e: IOException) {
            // для сетевых сбоев имеет смысл повтор; политика ретраев настраивается
            Result.retry()
        } catch (e: Exception) {
            Result.failure()
        }
    }

    private suspend fun uploadInChunks(file: File) {
        val totalChunks = ((file.length() + CHUNK_SIZE - 1) / CHUNK_SIZE).toInt()
        val uploadId = UUID.randomUUID().toString() // в реальном API обычно выдаётся сервером

        file.inputStream().buffered().use { input ->
            var index = 0
            val buffer = ByteArray(CHUNK_SIZE)

            while (true) {
                val bytesRead = input.read(buffer)
                if (bytesRead == -1) break

                val chunkFile = File(applicationContext.cacheDir, "chunk_$index")
                chunkFile.writeBytes(buffer.copyOf(bytesRead))

                uploadChunk(chunkFile, index, totalChunks, uploadId)
                chunkFile.delete()

                index++
                val progress = (100L * index / totalChunks).toInt()
                setProgressAsync(workDataOf("progress" to progress))
            }
        }
    }

    private suspend fun uploadChunk(file: File, index: Int, total: Int, uploadId: String) {
        val api = RetrofitClient.create() // placeholder
        val part = MultipartBody.Part.createFormData(
            "chunk",
            file.name,
            file.asRequestBody("application/octet-stream".toMediaType())
        )

        val response = api.uploadChunk(
            part,
            index.toString().toRequestBody("text/plain".toMediaType()),
            total.toString().toRequestBody("text/plain".toMediaType()),
            uploadId.toRequestBody("text/plain".toMediaType())
        )

        if (!response.isSuccessful) {
            // В реальной системе здесь также различаем временные (5xx/сеть) и постоянные (4xx) ошибки
            throw IOException("Chunk $index failed: ${response.code()}")
        }
    }
}
```

### Лучшие Практики

- Использовать WorkManager для надёжного планирования и выполнения задач с учётом ограничений ОС.
- Для длительных операций в фоне использовать foreground-режим через WorkManager + ForegroundInfo.
- Разбивать большие файлы на chunks при ограничениях по времени/стабильности сети и для поддержки возобновления.
- Добавлять constraints (сеть, батарея).
- Реализовать exponential backoff для retry.
- Очищать cache и временные файлы после загрузки.
- Компрессовать перед отправкой (если применимо и если backend поддерживает).

- Не загружать в main thread.
- Не использовать фоновый `Service` без foreground-уведомления на Android 8+.
- Не игнорировать ошибки сети и HTTP-коды.
- Не скрывать прогресс пользователя для длительных загрузок.
- Не хранить большие файлы в памяти целиком.
- Не оставлять временные файлы.

### Компромиссы

| Подход | Плюсы | Минусы |
|--------|-------|--------|
| **Простая загрузка** | Проще реализация | Не подходит для очень больших файлов / нестабильных сетей |
| **Chunked upload** | Поддержка pause/resume, устойчивость к сбоям | Требует поддержки на backend |
| **WorkManager** | Надёжное планирование, учет ограничений ОС | Не мгновенный запуск |
| **Foreground `Service`** | Высокий приоритет, контроль пользователем | Требует уведомление; для фоновых задач предпочтительно использовать через WorkManager |

---

## Answer (EN)

### Short Version

- Use `WorkManager` with `ForegroundInfo` for robust background upload scheduling with a visible notification (best-effort within OS constraints).
- Implement large file uploads via `Retrofit`/`OkHttp` using a `ProgressRequestBody` to report progress.
- For very large files, use chunked upload with retry support.

### Detailed Version

### Requirements

- Functional:
  - Support uploading large files (hundreds of MB+).
  - Show upload progress.
  - Survive app backgrounding and restarts.
  - Handle network errors and retries.
- Non-functional:
  - Do not block the UI thread.
  - Respect Android background execution limits.
  - Be efficient in memory and battery usage.

### Architecture Overview

**Key Components:**

1. **WorkManager** - robust background scheduling and execution (with foreground support).
2. **Retrofit + OkHttp** - multipart upload with progress.
3. **Foreground (WorkManager + ForegroundInfo)** - user-visible long-running operation.
4. **Chunked Upload** - split large files into parts (protocol aligned with backend).
5. **Retry Logic** - automatic retry on network-related failures.

### Implementation

#### 1. API Interface

```kotlin
interface FileUploadApi {
    @Multipart
    @POST("upload")
    suspend fun uploadFile(
        @Part file: MultipartBody.Part,
        @Part("metadata") metadata: RequestBody
    ): Response<UploadResponse>

    @Multipart
    @POST("upload/chunk")
    suspend fun uploadChunk(
        @Part chunk: MultipartBody.Part,
        @Part("index") index: RequestBody,
        @Part("total") total: RequestBody,
        @Part("uploadId") uploadId: RequestBody
    ): Response<ChunkResponse>
}
```

#### 2. Progress Tracking

```kotlin
class ProgressRequestBody(
    private val delegate: RequestBody,
    private val onProgress: (Long, Long) -> Unit
) : RequestBody() {
    override fun contentType() = delegate.contentType()
    override fun contentLength() = delegate.contentLength()

    override fun writeTo(sink: BufferedSink) {
        val countingSink = CountingSink(sink, contentLength(), onProgress)
        val bufferedSink = countingSink.buffer()
        delegate.writeTo(bufferedSink)
        bufferedSink.flush()
        // In production you should also handle request/coroutine cancellation
    }
}

class CountingSink(
    delegate: Sink,
    private val total: Long,
    private val onProgress: (Long, Long) -> Unit
) : ForwardingSink(delegate) {
    private var written = 0L

    override fun write(source: Buffer, byteCount: Long) {
        super.write(source, byteCount)
        written += byteCount
        onProgress(written, total)
    }
}
```

Example integration with OkHttp/Retrofit:

```kotlin
// Wrap the original RequestBody with ProgressRequestBody before building MultipartBody.Part
val original = file.asRequestBody("application/octet-stream".toMediaType())
val progressBody = ProgressRequestBody(original) { written, total ->
    val progress = if (total > 0) (100L * written / total).toInt() else 0
    setProgressAsync(workDataOf("progress" to progress))
}
val filePart = MultipartBody.Part.createFormData("file", file.name, progressBody)
```

#### 3. FileUploadWorker

```kotlin
class FileUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val filePath = inputData.getString(KEY_FILE_PATH) ?: return Result.failure()
        val file = File(filePath)

        if (!file.exists()) return Result.failure()

        createNotificationChannel() // placeholder: create notification channel
        setForeground(createForegroundInfo(0))

        return try {
            val success = uploadFile(file)
            if (success) {
                showNotification("Complete", file.name, 100) // placeholder
                Result.success()
            } else {
                // Treat non-successful HTTP responses as failure without automatic retry (policy can be adjusted)
                Result.failure()
            }
        } catch (e: IOException) {
            // Network errors: let WorkManager retry according to backoff policy
            Result.retry()
        } catch (e: Exception) {
            Result.failure(workDataOf("error" to e.message))
        }
    }

    private suspend fun uploadFile(file: File): Boolean {
        val api = RetrofitClient.create { written, total -> // RetrofitClient: placeholder for Retrofit factory
            val progress = if (total > 0) (100L * written / total).toInt() else 0
            setProgressAsync(workDataOf("progress" to progress))
            showNotification("Uploading...", file.name, progress) // placeholder
        }

        val requestFile = file.asRequestBody("application/octet-stream".toMediaType())
        val filePart = MultipartBody.Part.createFormData("file", file.name, requestFile)

        val response = api.uploadFile(filePart, createMetadata()) // createMetadata: placeholder
        return response.isSuccessful
    }

    private fun createForegroundInfo(progress: Int) = ForegroundInfo(
        NOTIFICATION_ID, // placeholder constants
        NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setContentTitle("Uploading File")
            .setSmallIcon(android.R.drawable.stat_sys_upload)
            .setProgress(100, progress, false)
            .setOngoing(true)
            .build()
    )
}
```

#### 4. Enqueue Upload

```kotlin
class MainActivity : AppCompatActivity() {
    private val workManager by lazy { WorkManager.getInstance(this) }

    private fun uploadFile(uri: Uri) {
        val file = copyToCache(uri) // placeholder: copy to accessible path

        val uploadRequest = OneTimeWorkRequestBuilder<FileUploadWorker>()
            .setInputData(workDataOf(KEY_FILE_PATH to file.absolutePath))
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED) // Network required
                    .setRequiresBatteryNotLow(true) // Battery not low
                    .build()
            )
            .setBackoffCriteria(
                BackoffPolicy.EXPONENTIAL,
                WorkRequest.MIN_BACKOFF_MILLIS,
                TimeUnit.MILLISECONDS
            )
            .build()

        workManager.enqueue(uploadRequest)

        // Observe progress
        workManager.getWorkInfoByIdLiveData(uploadRequest.id)
            .observe(this) { workInfo ->
                when (workInfo.state) {
                    WorkInfo.State.RUNNING -> {
                        val progress = workInfo.progress.getInt("progress", 0)
                        updateProgress(progress) // placeholder UI update
                    }
                    WorkInfo.State.SUCCEEDED -> showSuccess() // placeholder
                    WorkInfo.State.FAILED -> showError() // placeholder
                    else -> {}
                }
            }
    }
}
```

#### 5. Chunked Upload for Large Files

```kotlin
class ChunkedUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    companion object {
        const val CHUNK_SIZE = 5 * 1024 * 1024 // 5MB
    }

    override suspend fun doWork(): Result {
        val filePath = inputData.getString(KEY_FILE_PATH) ?: return Result.failure()
        val file = File(filePath)
        if (!file.exists()) return Result.failure()

        // For truly long-running large uploads, also call setForeground(...) with ForegroundInfo
        // similar to FileUploadWorker to comply with background execution limits.

        return try {
            uploadInChunks(file)
            Result.success()
        } catch (e: IOException) {
            // Retry on network-related issues; tune retry policy as needed
            Result.retry()
        } catch (e: Exception) {
            Result.failure()
        }
    }

    private suspend fun uploadInChunks(file: File) {
        val totalChunks = ((file.length() + CHUNK_SIZE - 1) / CHUNK_SIZE).toInt()
        val uploadId = UUID.randomUUID().toString() // in real APIs usually returned by server

        file.inputStream().buffered().use { input ->
            var index = 0
            val buffer = ByteArray(CHUNK_SIZE)

            while (true) {
                val bytesRead = input.read(buffer)
                if (bytesRead == -1) break

                val chunkFile = File(applicationContext.cacheDir, "chunk_$index")
                chunkFile.writeBytes(buffer.copyOf(bytesRead))

                uploadChunk(chunkFile, index, totalChunks, uploadId)
                chunkFile.delete()

                index++
                val progress = (100L * index / totalChunks).toInt()
                setProgressAsync(workDataOf("progress" to progress))
            }
        }
    }

    private suspend fun uploadChunk(file: File, index: Int, total: Int, uploadId: String) {
        val api = RetrofitClient.create() // placeholder
        val part = MultipartBody.Part.createFormData(
            "chunk",
            file.name,
            file.asRequestBody("application/octet-stream".toMediaType())
        )

        val response = api.uploadChunk(
            part,
            index.toString().toRequestBody("text/plain".toMediaType()),
            total.toString().toRequestBody("text/plain".toMediaType()),
            uploadId.toRequestBody("text/plain".toMediaType())
        )

        if (!response.isSuccessful) {
            // In a real implementation you'd distinguish temporary vs permanent errors
            throw IOException("Chunk $index failed: ${response.code()}")
        }
    }
}
```

### Best Practices

- Use WorkManager for robust scheduling that respects OS constraints.
- Use foreground mode via WorkManager + ForegroundInfo for long-running uploads.
- Split very large files into chunks when needed for reliability/time limits and to support resume.
- Add constraints (network, battery).
- Implement exponential backoff for retry.
- Clean up cache and temporary files after upload.
- Compress before sending (when applicable and supported by backend).

- Do not upload on main thread.
- Do not use a background `Service` without a foreground notification on Android 8+.
- Do not ignore network and HTTP errors.
- Do not hide progress for long uploads.
- Do not load entire large files into memory.
- Do not leave temporary files.

### Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| **Simple upload** | Easier implementation | Not suitable for very large files / unstable networks |
| **Chunked upload** | Supports pause/resume, resilient to failures | Requires backend support |
| **WorkManager** | Robust scheduling, respects OS limits | Not instant start |
| **Foreground `Service`** | Higher priority, user-visible | Requires notification; for background uploads prefer via WorkManager |

---

## Дополнительные Вопросы (RU)

1. Как бы вы реализовали паузу и возобновление загрузок больших файлов?
2. Какие стратегии вы бы использовали для обработки сбоев загрузки в медленных сетях?
3. Как оптимизировать использование памяти при загрузке очень больших файлов?
4. Какой подход вы выберете для параллельной загрузки нескольких файлов?
5. Как вы бы сохранили и восстановили прогресс загрузки при перезапуске приложения?

## Follow-ups

1. How would you implement pause/resume functionality for uploads?
2. What strategies would you use to handle upload failures on slow networks?
3. How can you optimize memory usage when uploading very large files?
4. What approach would you take for uploading multiple files in parallel?
5. How would you implement upload progress persistence across app restarts?

## Ссылки (RU)

- [[c-android-components]]
- [[c-coroutines]]
- Документация Android WorkManager: https://developer.android.com/topic/libraries/architecture/workmanager
- Документация Retrofit: https://square.github.io/retrofit/

## References

- [[c-android-components]]
- [[c-coroutines]]
- [Android WorkManager Documentation](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Retrofit Documentation](https://square.github.io/retrofit/)

## Связанные Вопросы (RU)

### Предварительные (Medium)
- [[q-android-testing-strategies--android--medium]]

### Связанные (Hard)
- Как спроектировать офлайн-синхронизацию для больших объёмов данных (см. соответствующие вопросы в разделе Android)?

### Продвинутые (Hard)
- Как обеспечить наблюдаемость и мониторинг загрузок в продакшене (логи, метрики, трейсинг)?

## Related Questions

### Prerequisites (Medium)
- [[q-android-testing-strategies--android--medium]]

### Related (Hard)
- How to design offline-first sync for large datasets on Android?

### Advanced (Hard)
- How to implement observability and monitoring for upload flows in production?
