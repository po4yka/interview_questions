---
topic: android
tags:
  - android
  - android/background-processing
  - background-processing
  - coroutines
  - livedata
  - workmanager
difficulty: medium
status: draft
---

# Как вернуть результат работы WorkManager в приложение?

**English**: How to return a result from WorkManager to the app?

## Answer

To return a result from **WorkManager**, use:

1. **`Result.success(outputData)`** in Worker to return data
2. **LiveData** to observe work status in Activity/ViewModel
3. **`WorkInfo.State.SUCCEEDED`** to check completion
4. **`outputData`** to extract result values

---

## Returning Results from WorkManager

### Overview

WorkManager provides **three ways** to return results:

1. **One-time observation** - Get result once via `WorkManager.getWorkInfoById()`
2. **LiveData observation** - Observe work status reactively
3. **Flow observation** - Modern reactive approach with Kotlin Flows

---

## Method 1: LiveData Observation (Recommended)

### Step 1: Create Worker with Result

```kotlin
import android.content.Context
import androidx.work.*

class DataProcessingWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            // Get input data
            val inputValue = inputData.getInt("input_value", 0)

            // Perform work
            val processedResult = processData(inputValue)

            // Create output data
            val outputData = workDataOf(
                "result" to processedResult,
                "timestamp" to System.currentTimeMillis(),
                "status" to "completed"
            )

            // Return success with output data
            Result.success(outputData)

        } catch (e: Exception) {
            // Return failure with error info
            val errorData = workDataOf("error" to e.message)
            Result.failure(errorData)
        }
    }

    private suspend fun processData(value: Int): String {
        // Simulate heavy work
        kotlinx.coroutines.delay(2000)
        return "Processed: ${value * 2}"
    }
}
```

---

### Step 2: Enqueue Work and Observe

```kotlin
import androidx.appcompat.app.AppCompatActivity
import androidx.work.*
import androidx.lifecycle.Observer

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Create input data
        val inputData = workDataOf("input_value" to 42)

        // Create work request
        val workRequest = OneTimeWorkRequestBuilder<DataProcessingWorker>()
            .setInputData(inputData)
            .build()

        // Enqueue work
        val workManager = WorkManager.getInstance(applicationContext)
        workManager.enqueue(workRequest)

        // Observe work status
        workManager.getWorkInfoByIdLiveData(workRequest.id)
            .observe(this, Observer { workInfo ->
                when (workInfo.state) {
                    WorkInfo.State.SUCCEEDED -> {
                        // Extract result
                        val result = workInfo.outputData.getString("result")
                        val timestamp = workInfo.outputData.getLong("timestamp", 0)
                        val status = workInfo.outputData.getString("status")

                        textView.text = "Result: $result\nStatus: $status\nTime: $timestamp"
                        progressBar.visibility = View.GONE
                    }

                    WorkInfo.State.FAILED -> {
                        val error = workInfo.outputData.getString("error")
                        textView.text = "Error: $error"
                        progressBar.visibility = View.GONE
                    }

                    WorkInfo.State.RUNNING -> {
                        textView.text = "Processing..."
                        progressBar.visibility = View.VISIBLE
                    }

                    else -> {
                        // ENQUEUED, BLOCKED, CANCELLED
                        textView.text = "Status: ${workInfo.state}"
                    }
                }
            })
    }
}
```

---

## Method 2: ViewModel with LiveData

**Better architecture - recommended for production.**

### ViewModel

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.work.*
import java.util.UUID

class DataViewModel(private val workManager: WorkManager) : ViewModel() {

    private val _workResult = MutableLiveData<WorkResult>()
    val workResult: LiveData<WorkResult> = _workResult

    fun processData(inputValue: Int) {
        val inputData = workDataOf("input_value" to inputValue)

        val workRequest = OneTimeWorkRequestBuilder<DataProcessingWorker>()
            .setInputData(inputData)
            .build()

        workManager.enqueue(workRequest)

        // Observe work
        workManager.getWorkInfoByIdLiveData(workRequest.id)
            .observeForever { workInfo ->
                when (workInfo.state) {
                    WorkInfo.State.SUCCEEDED -> {
                        val result = workInfo.outputData.getString("result") ?: ""
                        _workResult.value = WorkResult.Success(result)
                    }

                    WorkInfo.State.FAILED -> {
                        val error = workInfo.outputData.getString("error") ?: "Unknown error"
                        _workResult.value = WorkResult.Error(error)
                    }

                    WorkInfo.State.RUNNING -> {
                        _workResult.value = WorkResult.Loading
                    }

                    else -> {
                        // Handle other states
                    }
                }
            }
    }
}

sealed class WorkResult {
    object Loading : WorkResult()
    data class Success(val data: String) : WorkResult()
    data class Error(val message: String) : WorkResult()
}
```

### Activity

```kotlin
class MainActivity : AppCompatActivity() {

    private val viewModel: DataViewModel by viewModels {
        DataViewModelFactory(WorkManager.getInstance(applicationContext))
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        viewModel.workResult.observe(this) { result ->
            when (result) {
                is WorkResult.Loading -> {
                    progressBar.visibility = View.VISIBLE
                    textView.text = "Processing..."
                }

                is WorkResult.Success -> {
                    progressBar.visibility = View.GONE
                    textView.text = "Result: ${result.data}"
                }

                is WorkResult.Error -> {
                    progressBar.visibility = View.GONE
                    textView.text = "Error: ${result.message}"
                }
            }
        }

        button.setOnClickListener {
            viewModel.processData(42)
        }
    }
}
```

---

## Method 3: Flow Observation (Modern)

**Modern reactive approach with Kotlin Flow.**

```kotlin
import androidx.work.*
import kotlinx.coroutines.flow.*

class DataRepository(private val workManager: WorkManager) {

    fun processData(inputValue: Int): Flow<WorkResult> = flow {
        val inputData = workDataOf("input_value" to inputValue)

        val workRequest = OneTimeWorkRequestBuilder<DataProcessingWorker>()
            .setInputData(inputData)
            .build()

        workManager.enqueue(workRequest)

        // Convert LiveData to Flow
        workManager.getWorkInfoByIdFlow(workRequest.id)
            .collect { workInfo ->
                when (workInfo.state) {
                    WorkInfo.State.SUCCEEDED -> {
                        val result = workInfo.outputData.getString("result") ?: ""
                        emit(WorkResult.Success(result))
                    }

                    WorkInfo.State.FAILED -> {
                        val error = workInfo.outputData.getString("error") ?: "Unknown error"
                        emit(WorkResult.Error(error))
                    }

                    WorkInfo.State.RUNNING -> {
                        emit(WorkResult.Loading)
                    }

                    else -> {
                        // Handle other states
                    }
                }
            }
    }
}

// In ViewModel
class DataViewModel(private val repository: DataRepository) : ViewModel() {

    private val _workResult = MutableStateFlow<WorkResult>(WorkResult.Loading)
    val workResult: StateFlow<WorkResult> = _workResult.asStateFlow()

    fun processData(inputValue: Int) {
        viewModelScope.launch {
            repository.processData(inputValue)
                .collect { result ->
                    _workResult.value = result
                }
        }
    }
}

// In Activity
lifecycleScope.launch {
    viewModel.workResult.collect { result ->
        when (result) {
            is WorkResult.Loading -> showLoading()
            is WorkResult.Success -> showSuccess(result.data)
            is WorkResult.Error -> showError(result.message)
        }
    }
}
```

---

## Returning Complex Data

### Using Data class with JSON

```kotlin
import kotlinx.serialization.*
import kotlinx.serialization.json.Json

@Serializable
data class ProcessingResult(
    val processedItems: Int,
    val totalItems: Int,
    val duration: Long,
    val errors: List<String>
)

class ComplexDataWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val result = ProcessingResult(
            processedItems = 100,
            totalItems = 150,
            duration = 5000,
            errors = listOf("Error 1", "Error 2")
        )

        // Serialize to JSON
        val resultJson = Json.encodeToString(result)

        val outputData = workDataOf("result_json" to resultJson)

        return Result.success(outputData)
    }
}

// In Activity
val resultJson = workInfo.outputData.getString("result_json") ?: ""
val result = Json.decodeFromString<ProcessingResult>(resultJson)

textView.text = """
    Processed: ${result.processedItems}/${result.totalItems}
    Duration: ${result.duration}ms
    Errors: ${result.errors.joinToString()}
""".trimIndent()
```

---

## Observing Work by Tag or Unique Name

### By Tag

```kotlin
// Enqueue work with tag
val workRequest = OneTimeWorkRequestBuilder<DataProcessingWorker>()
    .addTag("data_processing")
    .build()

workManager.enqueue(workRequest)

// Observe by tag (returns all works with this tag)
workManager.getWorkInfosByTagLiveData("data_processing")
    .observe(this) { workInfoList ->
        workInfoList.forEach { workInfo ->
            if (workInfo.state == WorkInfo.State.SUCCEEDED) {
                val result = workInfo.outputData.getString("result")
                println("Result: $result")
            }
        }
    }
```

### By Unique Name

```kotlin
// Enqueue unique work
workManager.enqueueUniqueWork(
    "data_processing_unique",
    ExistingWorkPolicy.REPLACE,
    workRequest
)

// Observe by unique name
workManager.getWorkInfosForUniqueWorkLiveData("data_processing_unique")
    .observe(this) { workInfoList ->
        val workInfo = workInfoList.firstOrNull()
        workInfo?.let {
            if (it.state == WorkInfo.State.SUCCEEDED) {
                val result = it.outputData.getString("result")
                println("Result: $result")
            }
        }
    }
```

---

## Returning Progress Updates

**WorkManager doesn't support real-time progress**, but you can use:

### Option 1: setProgress() (API 29+)

```kotlin
class ProgressWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        for (i in 0..100 step 10) {
            delay(500)

            // Set progress
            setProgress(workDataOf("progress" to i))
        }

        return Result.success(workDataOf("result" to "Complete"))
    }
}

// Observe progress
workManager.getWorkInfoByIdLiveData(workRequest.id)
    .observe(this) { workInfo ->
        if (workInfo.state == WorkInfo.State.RUNNING) {
            val progress = workInfo.progress.getInt("progress", 0)
            progressBar.progress = progress
        }
    }
```

### Option 2: Use ForegroundInfo for Ongoing Notification

```kotlin
class DownloadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        setForeground(createForegroundInfo(0))

        for (i in 0..100 step 10) {
            delay(500)
            setForeground(createForegroundInfo(i))
        }

        return Result.success()
    }

    private fun createForegroundInfo(progress: Int): ForegroundInfo {
        val notification = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setContentTitle("Downloading")
            .setContentText("Progress: $progress%")
            .setSmallIcon(R.drawable.ic_download)
            .setProgress(100, progress, false)
            .build()

        return ForegroundInfo(NOTIFICATION_ID, notification)
    }
}
```

---

## Error Handling

```kotlin
class RobustWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val result = performWork()

            Result.success(workDataOf("result" to result))

        } catch (e: IOException) {
            // Network error - retry
            Result.retry()

        } catch (e: Exception) {
            // Fatal error - fail permanently
            Result.failure(workDataOf(
                "error" to e.message,
                "errorType" to e::class.simpleName
            ))
        }
    }

    private suspend fun performWork(): String {
        // Work implementation
        return "Success"
    }
}

// Handle errors
workManager.getWorkInfoByIdLiveData(workRequest.id)
    .observe(this) { workInfo ->
        when (workInfo.state) {
            WorkInfo.State.FAILED -> {
                val error = workInfo.outputData.getString("error")
                val errorType = workInfo.outputData.getString("errorType")
                showError("$errorType: $error")
            }

            WorkInfo.State.SUCCEEDED -> {
                val result = workInfo.outputData.getString("result")
                showSuccess(result)
            }

            else -> {
                // Handle other states
            }
        }
    }
```

---

## Summary

**How to return result from WorkManager:**

1. **In Worker:** Return `Result.success(outputData)` with data
   ```kotlin
   val outputData = workDataOf("key" to value)
   return Result.success(outputData)
   ```

2. **In Activity/ViewModel:** Observe via LiveData
   ```kotlin
   workManager.getWorkInfoByIdLiveData(workRequest.id)
       .observe(this) { workInfo ->
           if (workInfo.state == WorkInfo.State.SUCCEEDED) {
               val result = workInfo.outputData.getString("key")
           }
       }
   ```

**Key classes:**
- **`workDataOf()`** - Create output data
- **`Result.success(data)`** - Return with result
- **`WorkInfo.State.SUCCEEDED`** - Check completion
- **`workInfo.outputData`** - Extract values

**Best practices:**
- ✅ Use ViewModel to separate concerns
- ✅ Use StateFlow for modern reactive approach
- ✅ Serialize complex objects to JSON
- ✅ Handle all work states (ENQUEUED, RUNNING, SUCCEEDED, FAILED, CANCELLED)
- ✅ Use `setProgress()` for progress updates (API 29+)

---

## Ответ

Чтобы вернуть результат из **WorkManager**:

1. **В Worker:** Возвращаем `Result.success(outputData)` с данными
2. **В Activity/ViewModel:** Наблюдаем через LiveData
3. **Проверяем состояние:** `WorkInfo.State.SUCCEEDED`
4. **Извлекаем данные:** `workInfo.outputData`

**Пример:**

```kotlin
// Worker
override suspend fun doWork(): Result {
    val result = performWork()
    val outputData = workDataOf("result" to result)
    return Result.success(outputData)
}

// Activity
workManager.getWorkInfoByIdLiveData(workRequest.id)
    .observe(this) { workInfo ->
        if (workInfo.state == WorkInfo.State.SUCCEEDED) {
            val result = workInfo.outputData.getString("result")
            textView.text = result
        }
    }
```

**Лучшие практики:**
- Используйте ViewModel для разделения ответственности
- Используйте StateFlow для современного реактивного подхода
- Сериализуйте сложные объекты в JSON
- Обрабатывайте все состояния работы

