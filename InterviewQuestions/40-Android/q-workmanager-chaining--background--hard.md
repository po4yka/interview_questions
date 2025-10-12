---
tags:
  - Android
  - Kotlin
  - Background
  - WorkManager
  - Coroutines
difficulty: hard
status: draft
---

# WorkManager Work Chaining - Advanced Patterns

# Question (EN)
> 
Explain advanced WorkManager chaining patterns. How do you implement parallel execution, sequential chains, and complex dependency graphs? What are best practices for error handling and data passing between workers?

## Answer (EN)
WorkManager provides powerful chaining capabilities for building complex work execution graphs with dependencies, parallel execution, and sophisticated error handling strategies.

#### Core Chaining Concepts

**1. Sequential Chains**
```kotlin
// Simple sequential chain
WorkManager.getInstance(context)
    .beginWith(downloadWorker)
    .then(processWorker)
    .then(uploadWorker)
    .enqueue()

// Multiple workers in sequence
val chain = WorkManager.getInstance(context)
    .beginWith(listOf(validateWorker1, validateWorker2))
    .then(processWorker)
    .then(listOf(uploadWorker1, uploadWorker2))
    .enqueue()
```

**2. Parallel Execution**
```kotlin
// All workers start simultaneously
val parallelWorks = listOf(
    OneTimeWorkRequestBuilder<ImageProcessWorker>().build(),
    OneTimeWorkRequestBuilder<VideoProcessWorker>().build(),
    OneTimeWorkRequestBuilder<AudioProcessWorker>().build()
)

WorkManager.getInstance(context)
    .enqueue(parallelWorks)
```

**3. Complex Dependency Graphs**
```kotlin
// Fan-out pattern: one worker feeds multiple downstream workers
val downloadWorker = OneTimeWorkRequestBuilder<DownloadWorker>().build()
val imageProcessor = OneTimeWorkRequestBuilder<ImageProcessWorker>().build()
val videoProcessor = OneTimeWorkRequestBuilder<VideoProcessWorker>().build()
val metadataExtractor = OneTimeWorkRequestBuilder<MetadataWorker>().build()

WorkManager.getInstance(context)
    .beginWith(downloadWorker)
    .then(listOf(imageProcessor, videoProcessor, metadataExtractor))
    .enqueue()

// Fan-in pattern: multiple workers feed one downstream worker
val source1 = OneTimeWorkRequestBuilder<SourceWorker1>().build()
val source2 = OneTimeWorkRequestBuilder<SourceWorker2>().build()
val source3 = OneTimeWorkRequestBuilder<SourceWorker3>().build()
val aggregator = OneTimeWorkRequestBuilder<AggregatorWorker>().build()

WorkManager.getInstance(context)
    .beginWith(listOf(source1, source2, source3))
    .then(aggregator)
    .enqueue()
```

#### Advanced Implementation

**Complete Media Processing Pipeline**
```kotlin
class MediaProcessingCoordinator @Inject constructor(
    private val workManager: WorkManager,
    private val mediaRepository: MediaRepository
) {
    suspend fun processMediaBatch(mediaIds: List<String>): Flow<ProcessingStatus> = flow {
        val batchId = UUID.randomUUID().toString()

        // Phase 1: Download all media files in parallel
        val downloadRequests = mediaIds.map { mediaId ->
            OneTimeWorkRequestBuilder<MediaDownloadWorker>()
                .setInputData(workDataOf(
                    KEY_MEDIA_ID to mediaId,
                    KEY_BATCH_ID to batchId
                ))
                .setConstraints(
                    Constraints.Builder()
                        .setRequiredNetworkType(NetworkType.CONNECTED)
                        .setRequiresStorageNotLow(true)
                        .build()
                )
                .setBackoffCriteria(
                    BackoffPolicy.EXPONENTIAL,
                    WorkRequest.MIN_BACKOFF_MILLIS,
                    TimeUnit.MILLISECONDS
                )
                .addTag(TAG_DOWNLOAD)
                .addTag(batchId)
                .build()
        }

        // Phase 2: Process each type of media
        val imageProcessRequest = OneTimeWorkRequestBuilder<ImageProcessWorker>()
            .setInputData(workDataOf(KEY_BATCH_ID to batchId))
            .setConstraints(
                Constraints.Builder()
                    .setRequiresBatteryNotLow(true)
                    .build()
            )
            .addTag(TAG_PROCESS)
            .addTag(batchId)
            .build()

        val videoProcessRequest = OneTimeWorkRequestBuilder<VideoProcessWorker>()
            .setInputData(workDataOf(KEY_BATCH_ID to batchId))
            .setConstraints(
                Constraints.Builder()
                    .setRequiresBatteryNotLow(true)
                    .build()
            )
            .addTag(TAG_PROCESS)
            .addTag(batchId)
            .build()

        val audioProcessRequest = OneTimeWorkRequestBuilder<AudioProcessWorker>()
            .setInputData(workDataOf(KEY_BATCH_ID to batchId))
            .addTag(TAG_PROCESS)
            .addTag(batchId)
            .build()

        // Phase 3: Generate thumbnails in parallel
        val thumbnailRequest = OneTimeWorkRequestBuilder<ThumbnailGeneratorWorker>()
            .setInputData(workDataOf(KEY_BATCH_ID to batchId))
            .addTag(TAG_THUMBNAIL)
            .addTag(batchId)
            .build()

        // Phase 4: Upload all processed files
        val uploadRequest = OneTimeWorkRequestBuilder<MediaUploadWorker>()
            .setInputData(workDataOf(KEY_BATCH_ID to batchId))
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.UNMETERED)
                    .build()
            )
            .addTag(TAG_UPLOAD)
            .addTag(batchId)
            .build()

        // Phase 5: Cleanup temporary files
        val cleanupRequest = OneTimeWorkRequestBuilder<CleanupWorker>()
            .setInputData(workDataOf(KEY_BATCH_ID to batchId))
            .addTag(TAG_CLEANUP)
            .addTag(batchId)
            .build()

        // Phase 6: Send notification
        val notificationRequest = OneTimeWorkRequestBuilder<NotificationWorker>()
            .setInputData(workDataOf(
                KEY_BATCH_ID to batchId,
                KEY_MEDIA_COUNT to mediaIds.size
            ))
            .addTag(TAG_NOTIFICATION)
            .addTag(batchId)
            .build()

        // Build complex chain
        val continuation = workManager
            .beginWith(downloadRequests)
            .then(listOf(imageProcessRequest, videoProcessRequest, audioProcessRequest))
            .then(thumbnailRequest)
            .then(uploadRequest)
            .then(listOf(cleanupRequest, notificationRequest))

        // Enqueue with unique work policy
        continuation.enqueue()

        // Observe progress
        workManager.getWorkInfosByTagFlow(batchId)
            .collect { workInfos ->
                val status = calculateOverallStatus(workInfos)
                emit(status)
            }
    }

    private fun calculateOverallStatus(workInfos: List<WorkInfo>): ProcessingStatus {
        val total = workInfos.size
        val succeeded = workInfos.count { it.state == WorkInfo.State.SUCCEEDED }
        val failed = workInfos.count { it.state == WorkInfo.State.FAILED }
        val running = workInfos.count { it.state == WorkInfo.State.RUNNING }
        val enqueued = workInfos.count { it.state == WorkInfo.State.ENQUEUED }

        return when {
            failed > 0 -> ProcessingStatus.Failed(
                completed = succeeded,
                failed = failed,
                total = total
            )
            succeeded == total -> ProcessingStatus.Completed(total)
            running > 0 || enqueued > 0 -> ProcessingStatus.InProgress(
                completed = succeeded,
                total = total,
                progress = (succeeded.toFloat() / total * 100).toInt()
            )
            else -> ProcessingStatus.Pending
        }
    }

    companion object {
        private const val TAG_DOWNLOAD = "download"
        private const val TAG_PROCESS = "process"
        private const val TAG_THUMBNAIL = "thumbnail"
        private const val TAG_UPLOAD = "upload"
        private const val TAG_CLEANUP = "cleanup"
        private const val TAG_NOTIFICATION = "notification"

        private const val KEY_MEDIA_ID = "media_id"
        private const val KEY_BATCH_ID = "batch_id"
        private const val KEY_MEDIA_COUNT = "media_count"
    }
}

sealed class ProcessingStatus {
    object Pending : ProcessingStatus()
    data class InProgress(
        val completed: Int,
        val total: Int,
        val progress: Int
    ) : ProcessingStatus()
    data class Completed(val total: Int) : ProcessingStatus()
    data class Failed(
        val completed: Int,
        val failed: Int,
        val total: Int
    ) : ProcessingStatus()
}
```

**Media Download Worker with Data Passing**
```kotlin
class MediaDownloadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    @Inject lateinit var downloadService: DownloadService
    @Inject lateinit var fileManager: FileManager

    override suspend fun doWork(): Result {
        val mediaId = inputData.getString(KEY_MEDIA_ID) ?: return Result.failure()
        val batchId = inputData.getString(KEY_BATCH_ID) ?: return Result.failure()

        return try {
            setProgress(workDataOf(KEY_PROGRESS to 0))

            // Download file with progress
            val localFile = downloadService.downloadMedia(mediaId) { progress ->
                runBlocking {
                    setProgress(workDataOf(KEY_PROGRESS to progress))
                }
            }

            // Store file path for downstream workers
            val outputData = workDataOf(
                KEY_MEDIA_ID to mediaId,
                KEY_LOCAL_PATH to localFile.absolutePath,
                KEY_FILE_SIZE to localFile.length(),
                KEY_MIME_TYPE to getMimeType(localFile),
                KEY_BATCH_ID to batchId
            )

            Result.success(outputData)
        } catch (e: IOException) {
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure(workDataOf(
                    KEY_ERROR_MESSAGE to e.message,
                    KEY_MEDIA_ID to mediaId
                ))
            }
        } catch (e: Exception) {
            Result.failure(workDataOf(
                KEY_ERROR_MESSAGE to e.message,
                KEY_MEDIA_ID to mediaId
            ))
        }
    }

    private fun getMimeType(file: File): String {
        return MimeTypeMap.getSingleton()
            .getMimeTypeFromExtension(file.extension)
            ?: "application/octet-stream"
    }

    companion object {
        private const val KEY_MEDIA_ID = "media_id"
        private const val KEY_BATCH_ID = "batch_id"
        private const val KEY_LOCAL_PATH = "local_path"
        private const val KEY_FILE_SIZE = "file_size"
        private const val KEY_MIME_TYPE = "mime_type"
        private const val KEY_PROGRESS = "progress"
        private const val KEY_ERROR_MESSAGE = "error_message"
    }
}
```

**Image Processing Worker - Collecting Input from Multiple Upstream Workers**
```kotlin
class ImageProcessWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    @Inject lateinit var imageProcessor: ImageProcessor
    @Inject lateinit var fileManager: FileManager
    @Inject lateinit var workManager: WorkManager

    override suspend fun doWork(): Result {
        val batchId = inputData.getString(KEY_BATCH_ID) ?: return Result.failure()

        return try {
            // Get all completed download workers from the same batch
            val downloadedFiles = getCompletedDownloads(batchId)

            if (downloadedFiles.isEmpty()) {
                return Result.success()
            }

            setProgress(workDataOf(
                KEY_PROGRESS to 0,
                KEY_TOTAL_FILES to downloadedFiles.size
            ))

            val processedFiles = mutableListOf<ProcessedFile>()

            downloadedFiles.forEachIndexed { index, fileInfo ->
                if (fileInfo.mimeType.startsWith("image/")) {
                    val inputFile = File(fileInfo.path)
                    val processedFile = imageProcessor.processImage(
                        input = inputFile,
                        operations = listOf(
                            ImageOperation.Resize(maxWidth = 1920, maxHeight = 1080),
                            ImageOperation.Compress(quality = 85),
                            ImageOperation.OptimizeMetadata
                        )
                    )

                    processedFiles.add(ProcessedFile(
                        mediaId = fileInfo.mediaId,
                        originalPath = fileInfo.path,
                        processedPath = processedFile.absolutePath,
                        fileSize = processedFile.length()
                    ))
                }

                val progress = ((index + 1).toFloat() / downloadedFiles.size * 100).toInt()
                setProgress(workDataOf(
                    KEY_PROGRESS to progress,
                    KEY_PROCESSED_COUNT to index + 1
                ))
            }

            // Pass processed files to next worker
            val outputData = workDataOf(
                KEY_BATCH_ID to batchId,
                KEY_PROCESSED_FILES to processedFiles.toJson(),
                KEY_PROCESSED_COUNT to processedFiles.size
            )

            Result.success(outputData)
        } catch (e: Exception) {
            Result.failure(workDataOf(
                KEY_ERROR_MESSAGE to e.message,
                KEY_BATCH_ID to batchId
            ))
        }
    }

    private suspend fun getCompletedDownloads(batchId: String): List<FileInfo> {
        val workInfos = workManager
            .getWorkInfosByTag(TAG_DOWNLOAD)
            .await()
            .filter { it.tags.contains(batchId) && it.state == WorkInfo.State.SUCCEEDED }

        return workInfos.mapNotNull { workInfo ->
            val outputData = workInfo.outputData
            val mediaId = outputData.getString(KEY_MEDIA_ID) ?: return@mapNotNull null
            val path = outputData.getString(KEY_LOCAL_PATH) ?: return@mapNotNull null
            val mimeType = outputData.getString(KEY_MIME_TYPE) ?: return@mapNotNull null

            FileInfo(
                mediaId = mediaId,
                path = path,
                mimeType = mimeType
            )
        }
    }

    private fun List<ProcessedFile>.toJson(): String {
        return Gson().toJson(this)
    }

    data class FileInfo(
        val mediaId: String,
        val path: String,
        val mimeType: String
    )

    data class ProcessedFile(
        val mediaId: String,
        val originalPath: String,
        val processedPath: String,
        val fileSize: Long
    )

    companion object {
        private const val TAG_DOWNLOAD = "download"
        private const val KEY_BATCH_ID = "batch_id"
        private const val KEY_PROGRESS = "progress"
        private const val KEY_TOTAL_FILES = "total_files"
        private const val KEY_PROCESSED_COUNT = "processed_count"
        private const val KEY_PROCESSED_FILES = "processed_files"
        private const val KEY_ERROR_MESSAGE = "error_message"
        private const val KEY_MEDIA_ID = "media_id"
        private const val KEY_LOCAL_PATH = "local_path"
        private const val KEY_MIME_TYPE = "mime_type"
    }
}
```

#### Advanced Error Handling

**Selective Retry Strategy**
```kotlin
class ReliableDataSyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            syncData()
            Result.success()
        } catch (e: NetworkException) {
            // Network errors - retry with exponential backoff
            if (runAttemptCount < MAX_NETWORK_RETRIES) {
                Result.retry()
            } else {
                // After max retries, mark as failure but don't fail the chain
                Result.success(workDataOf(
                    KEY_PARTIAL_SUCCESS to true,
                    KEY_ERROR_TYPE to "network_timeout"
                ))
            }
        } catch (e: AuthException) {
            // Auth errors - don't retry, fail immediately
            Result.failure(workDataOf(
                KEY_ERROR_TYPE to "authentication",
                KEY_ERROR_MESSAGE to e.message
            ))
        } catch (e: ValidationException) {
            // Validation errors - don't retry, but continue chain
            Result.success(workDataOf(
                KEY_PARTIAL_SUCCESS to true,
                KEY_ERROR_TYPE to "validation",
                KEY_SKIPPED_ITEMS to e.invalidItemIds.toJson()
            ))
        } catch (e: Exception) {
            // Unknown errors - retry once then fail
            if (runAttemptCount == 0) {
                Result.retry()
            } else {
                Result.failure(workDataOf(
                    KEY_ERROR_TYPE to "unknown",
                    KEY_ERROR_MESSAGE to e.message
                ))
            }
        }
    }

    companion object {
        private const val MAX_NETWORK_RETRIES = 5
        private const val KEY_PARTIAL_SUCCESS = "partial_success"
        private const val KEY_ERROR_TYPE = "error_type"
        private const val KEY_ERROR_MESSAGE = "error_message"
        private const val KEY_SKIPPED_ITEMS = "skipped_items"
    }
}
```

**Chain-Level Error Recovery**
```kotlin
class MediaProcessingOrchestrator @Inject constructor(
    private val workManager: WorkManager
) {
    fun startProcessingWithRecovery(mediaIds: List<String>): UUID {
        val batchId = UUID.randomUUID().toString()

        // Primary processing chain
        val primaryChain = buildPrimaryChain(mediaIds, batchId)

        // Fallback chain for critical failures
        val fallbackRequest = OneTimeWorkRequestBuilder<FallbackProcessWorker>()
            .setInputData(workDataOf(
                KEY_BATCH_ID to batchId,
                KEY_ORIGINAL_MEDIA_IDS to mediaIds.toJson()
            ))
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build()
            )
            .build()

        // Error notification worker
        val errorNotificationRequest = OneTimeWorkRequestBuilder<ErrorNotificationWorker>()
            .setInputData(workDataOf(KEY_BATCH_ID to batchId))
            .build()

        // Build chain with error handling
        workManager
            .beginWith(primaryChain)
            .then(fallbackRequest)
            .then(errorNotificationRequest)
            .enqueue()

        return UUID.fromString(batchId)
    }

    private fun buildPrimaryChain(
        mediaIds: List<String>,
        batchId: String
    ): List<OneTimeWorkRequest> {
        return mediaIds.map { mediaId ->
            OneTimeWorkRequestBuilder<MediaDownloadWorker>()
                .setInputData(workDataOf(
                    KEY_MEDIA_ID to mediaId,
                    KEY_BATCH_ID to batchId
                ))
                .setBackoffCriteria(
                    BackoffPolicy.EXPONENTIAL,
                    WorkRequest.MIN_BACKOFF_MILLIS,
                    TimeUnit.MILLISECONDS
                )
                .addTag(batchId)
                .build()
        }
    }
}

class FallbackProcessWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    @Inject lateinit var workManager: WorkManager
    @Inject lateinit var recoveryService: RecoveryService

    override suspend fun doWork(): Result {
        val batchId = inputData.getString(KEY_BATCH_ID) ?: return Result.failure()

        // Check if any workers in the batch failed
        val workInfos = workManager.getWorkInfosByTag(batchId).await()
        val failedWorks = workInfos.filter { it.state == WorkInfo.State.FAILED }

        if (failedWorks.isEmpty()) {
            // No failures, nothing to recover
            return Result.success()
        }

        // Attempt recovery for failed items
        val recoveryResults = failedWorks.map { failedWork ->
            val mediaId = failedWork.outputData.getString(KEY_MEDIA_ID)
            val errorType = failedWork.outputData.getString(KEY_ERROR_TYPE)

            recoveryService.attemptRecovery(
                mediaId = mediaId,
                errorType = errorType,
                batchId = batchId
            )
        }

        val outputData = workDataOf(
            KEY_BATCH_ID to batchId,
            KEY_RECOVERED_COUNT to recoveryResults.count { it.success },
            KEY_FAILED_COUNT to recoveryResults.count { !it.success }
        )

        return if (recoveryResults.any { it.success }) {
            Result.success(outputData)
        } else {
            Result.failure(outputData)
        }
    }
}
```

#### Dynamic Chain Modification

**Conditional Chain Building**
```kotlin
class AdaptiveMediaProcessor @Inject constructor(
    private val workManager: WorkManager,
    private val deviceCapabilities: DeviceCapabilities
) {
    fun processMedia(files: List<File>): WorkContinuation {
        val downloadChain = workManager.beginWith(
            buildDownloadRequests(files)
        )

        // Analyze files and decide processing strategy
        val processingChain = when {
            deviceCapabilities.hasHighPerformanceGpu() -> {
                // Use GPU-accelerated processing
                downloadChain.then(buildGpuProcessingRequests(files))
            }
            deviceCapabilities.hasMultipleProcessors() -> {
                // Use parallel CPU processing
                downloadChain.then(buildParallelCpuProcessingRequests(files))
            }
            else -> {
                // Use sequential processing
                downloadChain.then(buildSequentialProcessingRequests(files))
            }
        }

        // Add conditional quality checks
        val qualityCheckChain = if (deviceCapabilities.hasSufficientBattery()) {
            processingChain.then(buildQualityCheckRequest())
        } else {
            processingChain // Skip quality check to save battery
        }

        // Final upload with appropriate network requirements
        return qualityCheckChain.then(
            buildUploadRequest(
                requireUnmetered = !deviceCapabilities.hasUnlimitedData()
            )
        )
    }
}
```

**Chain Branching Based on Results**
```kotlin
class ConditionalChainBuilder @Inject constructor(
    private val workManager: WorkManager
) {
    fun buildAdaptiveChain(inputData: WorkData): UUID {
        val analysisRequest = OneTimeWorkRequestBuilder<AnalysisWorker>()
            .setInputData(inputData)
            .build()

        workManager.beginWith(analysisRequest).enqueue()

        // Monitor analysis result and build next chain dynamically
        observeWorkAndBranch(analysisRequest.id)

        return analysisRequest.id
    }

    private fun observeWorkAndBranch(workId: UUID) {
        workManager.getWorkInfoByIdLiveData(workId)
            .observeForever { workInfo ->
                if (workInfo?.state == WorkInfo.State.SUCCEEDED) {
                    val analysisResult = workInfo.outputData.getString(KEY_ANALYSIS_RESULT)

                    val nextChain = when (analysisResult) {
                        "high_quality" -> buildHighQualityProcessingChain()
                        "medium_quality" -> buildMediumQualityProcessingChain()
                        "low_quality" -> buildEnhancementChain()
                        else -> buildDefaultChain()
                    }

                    workManager.beginWith(nextChain).enqueue()
                }
            }
    }
}
```

#### Monitoring and Observing Chains

**Comprehensive Chain Monitoring**
```kotlin
class WorkChainMonitor @Inject constructor(
    private val workManager: WorkManager
) {
    fun monitorChain(chainTag: String): Flow<ChainStatus> = flow {
        workManager.getWorkInfosByTagFlow(chainTag)
            .collect { workInfos ->
                val status = analyzeChainStatus(workInfos)
                emit(status)
            }
    }

    private fun analyzeChainStatus(workInfos: List<WorkInfo>): ChainStatus {
        val states = workInfos.groupBy { it.state }

        return ChainStatus(
            total = workInfos.size,
            enqueued = states[WorkInfo.State.ENQUEUED]?.size ?: 0,
            running = states[WorkInfo.State.RUNNING]?.size ?: 0,
            succeeded = states[WorkInfo.State.SUCCEEDED]?.size ?: 0,
            failed = states[WorkInfo.State.FAILED]?.size ?: 0,
            cancelled = states[WorkInfo.State.CANCELLED]?.size ?: 0,
            blocked = states[WorkInfo.State.BLOCKED]?.size ?: 0,
            progress = calculateOverallProgress(workInfos),
            estimatedTimeRemaining = estimateTimeRemaining(workInfos),
            currentPhase = determineCurrentPhase(workInfos)
        )
    }

    private fun calculateOverallProgress(workInfos: List<WorkInfo>): Int {
        val totalProgress = workInfos.sumOf { workInfo ->
            when (workInfo.state) {
                WorkInfo.State.SUCCEEDED -> 100
                WorkInfo.State.RUNNING -> {
                    workInfo.progress.getInt(KEY_PROGRESS, 0)
                }
                WorkInfo.State.ENQUEUED, WorkInfo.State.BLOCKED -> 0
                else -> 0
            }
        }
        return if (workInfos.isNotEmpty()) {
            totalProgress / workInfos.size
        } else 0
    }

    private fun estimateTimeRemaining(workInfos: List<WorkInfo>): Duration {
        val runningWork = workInfos.filter { it.state == WorkInfo.State.RUNNING }
        val enqueuedWork = workInfos.filter {
            it.state == WorkInfo.State.ENQUEUED || it.state == WorkInfo.State.BLOCKED
        }

        // Simple estimation based on average worker duration
        val avgDuration = Duration.ofMinutes(2) // Configurable
        return avgDuration * (runningWork.size + enqueuedWork.size)
    }

    private fun determineCurrentPhase(workInfos: List<WorkInfo>): String {
        val runningWorkers = workInfos.filter { it.state == WorkInfo.State.RUNNING }
        return when {
            runningWorkers.any { it.tags.contains(TAG_DOWNLOAD) } -> "Downloading"
            runningWorkers.any { it.tags.contains(TAG_PROCESS) } -> "Processing"
            runningWorkers.any { it.tags.contains(TAG_UPLOAD) } -> "Uploading"
            workInfos.all { it.state == WorkInfo.State.SUCCEEDED } -> "Completed"
            workInfos.any { it.state == WorkInfo.State.FAILED } -> "Failed"
            else -> "Preparing"
        }
    }
}

data class ChainStatus(
    val total: Int,
    val enqueued: Int,
    val running: Int,
    val succeeded: Int,
    val failed: Int,
    val cancelled: Int,
    val blocked: Int,
    val progress: Int,
    val estimatedTimeRemaining: Duration,
    val currentPhase: String
)
```

**Real-time Progress UI**
```kotlin
@Composable
fun WorkChainProgressScreen(
    chainTag: String,
    viewModel: WorkChainViewModel = hiltViewModel()
) {
    val chainStatus by viewModel.monitorChain(chainTag).collectAsState(
        initial = ChainStatus.empty()
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "Processing Status",
            style = MaterialTheme.typography.headlineMedium
        )

        Spacer(modifier = Modifier.height(16.dp))

        LinearProgressIndicator(
            progress = chainStatus.progress / 100f,
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = "${chainStatus.progress}% - ${chainStatus.currentPhase}",
            style = MaterialTheme.typography.bodyLarge
        )

        Spacer(modifier = Modifier.height(24.dp))

        WorkStatusGrid(status = chainStatus)

        Spacer(modifier = Modifier.height(16.dp))

        if (chainStatus.estimatedTimeRemaining > Duration.ZERO) {
            Text(
                text = "Estimated time remaining: ${chainStatus.estimatedTimeRemaining.toMinutes()} min",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        Spacer(modifier = Modifier.height(24.dp))

        if (chainStatus.failed > 0) {
            Button(
                onClick = { viewModel.retryFailed(chainTag) },
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.error
                )
            ) {
                Text("Retry Failed (${chainStatus.failed})")
            }
        }

        if (chainStatus.running > 0 || chainStatus.enqueued > 0) {
            OutlinedButton(
                onClick = { viewModel.cancelChain(chainTag) }
            ) {
                Text("Cancel All")
            }
        }
    }
}

@Composable
fun WorkStatusGrid(status: ChainStatus) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        StatusCard("Total", status.total, MaterialTheme.colorScheme.primary)
        StatusCard("Running", status.running, MaterialTheme.colorScheme.tertiary)
        StatusCard("Succeeded", status.succeeded, MaterialTheme.colorScheme.secondary)
        StatusCard("Failed", status.failed, MaterialTheme.colorScheme.error)
    }
}

@Composable
fun StatusCard(label: String, count: Int, color: Color) {
    Card(
        modifier = Modifier.size(80.dp),
        colors = CardDefaults.cardColors(containerColor = color.copy(alpha = 0.1f))
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(8.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = count.toString(),
                style = MaterialTheme.typography.headlineMedium,
                color = color
            )
            Text(
                text = label,
                style = MaterialTheme.typography.bodySmall,
                color = color
            )
        }
    }
}
```

#### Best Practices

1. **Data Passing**:
   - Keep WorkData small (<10KB)
   - Use database/files for large data
   - Pass IDs instead of complex objects
   - Serialize collections properly

2. **Error Handling**:
   - Design for partial failures
   - Use appropriate retry policies
   - Pass error context downstream
   - Implement fallback chains

3. **Chain Design**:
   - Keep chains logical and maintainable
   - Use tags for grouping related work
   - Design for observability
   - Plan for cancellation

4. **Performance**:
   - Minimize worker count
   - Batch similar operations
   - Use parallel execution where possible
   - Monitor memory usage

5. **Testing**:
   - Test individual workers
   - Test chain logic
   - Test error scenarios
   - Use TestListenableWorkerBuilder

#### Common Pitfalls

1. **Over-complex Chains**: Too many dependencies make debugging hard
2. **Large Data Transfer**: WorkData has size limits
3. **Circular Dependencies**: Can cause deadlocks
4. **Missing Error Handling**: Failed workers block entire chains
5. **No Progress Reporting**: Users don't know what's happening
6. **Ignoring Constraints**: Work starts in inappropriate conditions

#### Testing Work Chains

```kotlin
@Test
fun testMediaProcessingChain() = runTest {
    val context = ApplicationProvider.getApplicationContext<Context>()
    val workManager = WorkManager.getInstance(context)

    // Create test input
    val testMediaIds = listOf("media1", "media2", "media3")
    val batchId = UUID.randomUUID().toString()

    // Build chain
    val downloadRequests = testMediaIds.map { mediaId ->
        OneTimeWorkRequestBuilder<MediaDownloadWorker>()
            .setInputData(workDataOf(
                "media_id" to mediaId,
                "batch_id" to batchId
            ))
            .addTag(batchId)
            .build()
    }

    val processRequest = OneTimeWorkRequestBuilder<ImageProcessWorker>()
        .setInputData(workDataOf("batch_id" to batchId))
        .addTag(batchId)
        .build()

    // Enqueue chain
    workManager
        .beginWith(downloadRequests)
        .then(processRequest)
        .enqueue()
        .result
        .await()

    // Wait for completion
    testScheduler.advanceUntilIdle()

    // Verify all workers succeeded
    val workInfos = workManager.getWorkInfosByTag(batchId).await()
    assertThat(workInfos).hasSize(4) // 3 downloads + 1 process
    assertThat(workInfos.all { it.state == WorkInfo.State.SUCCEEDED }).isTrue()

    // Verify output data
    val processWorkInfo = workInfos.first {
        it.id == processRequest.id
    }
    val processedCount = processWorkInfo.outputData.getInt("processed_count", 0)
    assertThat(processedCount).isEqualTo(3)
}
```

### Summary

WorkManager chaining enables sophisticated background processing pipelines with:
- **Sequential & Parallel Execution**: Flexible work scheduling
- **Data Passing**: Transfer results between workers
- **Error Handling**: Retry policies and fallback chains
- **Observability**: Real-time progress monitoring
- **Conditional Logic**: Dynamic chain building based on results

Key considerations: Keep chains maintainable, handle errors gracefully, minimize data transfer, use tags for organization, and design for observability.

---

# Вопрос (RU)
> 
Объясните продвинутые паттерны цепочек WorkManager. Как реализовать параллельное выполнение, последовательные цепи и сложные графы зависимостей? Каковы best practices для обработки ошибок и передачи данных между воркерами?

## Ответ (RU)
WorkManager предоставляет мощные возможности для построения сложных графов выполнения работ с зависимостями, параллельным выполнением и продвинутыми стратегиями обработки ошибок.

#### Базовые концепции цепочек

**1. Последовательные цепи**
```kotlin
// Простая последовательная цепь
WorkManager.getInstance(context)
    .beginWith(downloadWorker)
    .then(processWorker)
    .then(uploadWorker)
    .enqueue()

// Несколько воркеров в последовательности
val chain = WorkManager.getInstance(context)
    .beginWith(listOf(validateWorker1, validateWorker2))
    .then(processWorker)
    .then(listOf(uploadWorker1, uploadWorker2))
    .enqueue()
```

**2. Параллельное выполнение**
```kotlin
// Все воркеры стартуют одновременно
val parallelWorks = listOf(
    OneTimeWorkRequestBuilder<ImageProcessWorker>().build(),
    OneTimeWorkRequestBuilder<VideoProcessWorker>().build(),
    OneTimeWorkRequestBuilder<AudioProcessWorker>().build()
)

WorkManager.getInstance(context)
    .enqueue(parallelWorks)
```

**3. Сложные графы зависимостей**
```kotlin
// Паттерн fan-out: один воркер питает несколько downstream воркеров
val downloadWorker = OneTimeWorkRequestBuilder<DownloadWorker>().build()
val imageProcessor = OneTimeWorkRequestBuilder<ImageProcessWorker>().build()
val videoProcessor = OneTimeWorkRequestBuilder<VideoProcessWorker>().build()
val metadataExtractor = OneTimeWorkRequestBuilder<MetadataWorker>().build()

WorkManager.getInstance(context)
    .beginWith(downloadWorker)
    .then(listOf(imageProcessor, videoProcessor, metadataExtractor))
    .enqueue()

// Паттерн fan-in: несколько воркеров питают один downstream воркер
val source1 = OneTimeWorkRequestBuilder<SourceWorker1>().build()
val source2 = OneTimeWorkRequestBuilder<SourceWorker2>().build()
val source3 = OneTimeWorkRequestBuilder<SourceWorker3>().build()
val aggregator = OneTimeWorkRequestBuilder<AggregatorWorker>().build()

WorkManager.getInstance(context)
    .beginWith(listOf(source1, source2, source3))
    .then(aggregator)
    .enqueue()
```

Полные примеры реализации см. в английской версии ответа.

#### Продвинутая обработка ошибок

**Селективная стратегия retry**:
- Сетевые ошибки → retry с экспоненциальной задержкой
- Ошибки аутентификации → немедленный failure без retry
- Ошибки валидации → продолжить цепь, но пометить частичный успех

**Восстановление на уровне цепи**:
- Основная цепь обработки
- Fallback-цепь для критических сбоев
- Уведомление об ошибках

#### Лучшие практики

1. **Передача данных**:
   - Держите WorkData маленьким (<10KB)
   - Используйте БД/файлы для больших данных
   - Передавайте ID вместо сложных объектов

2. **Обработка ошибок**:
   - Проектируйте для частичных сбоев
   - Используйте подходящие retry-политики
   - Передавайте контекст ошибки далее по цепи

3. **Дизайн цепи**:
   - Держите цепи логичными и поддерживаемыми
   - Используйте теги для группировки связанной работы
   - Проектируйте для наблюдаемости
   - Планируйте возможность отмены

4. **Производительность**:
   - Минимизируйте количество воркеров
   - Группируйте похожие операции
   - Используйте параллельное выполнение где возможно

5. **Тестирование**:
   - Тестируйте отдельные воркеры
   - Тестируйте логику цепи
   - Тестируйте сценарии ошибок

#### Частые ошибки

1. **Слишком сложные цепи**: Множество зависимостей усложняет отладку
2. **Большой объем передаваемых данных**: WorkData имеет ограничения по размеру
3. **Циклические зависимости**: Могут вызвать deadlock
4. **Отсутствие обработки ошибок**: Упавший воркер блокирует всю цепь
5. **Нет отчетности о прогрессе**: Пользователь не знает, что происходит

### Резюме

Цепочки WorkManager позволяют создавать продвинутые конвейеры фоновой обработки с:
- **Последовательным и параллельным выполнением**: Гибкое планирование работы
- **Передачей данных**: Передача результатов между воркерами
- **Обработкой ошибок**: Retry-политики и fallback-цепи
- **Наблюдаемостью**: Мониторинг прогресса в реальном времени
- **Условной логикой**: Динамическое построение цепей на основе результатов

Ключевые моменты: держите цепи поддерживаемыми, обрабатывайте ошибки gracefully, минимизируйте передачу данных, используйте теги для организации, проектируйте для наблюдаемости.
