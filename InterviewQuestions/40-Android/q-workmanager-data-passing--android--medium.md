---
topic: android
tags:
  - android
  - android/background-processing
  - background-processing
  - data-passing
  - workmanager
difficulty: medium
status: draft
---

# How to pass and receive data from WorkManager?

**Russian**: Как передать и как получить данные из WorkManager?

**English**: How to pass and receive data from WorkManager?

## Answer (EN)
Data is passed using a special **Data** container:

1. **Pass data IN:** Use `setInputData(workDataOf(...))` when creating WorkRequest
2. **Access data IN Worker:** Use `inputData.getInt()`, `inputData.getString()`, etc.
3. **Return data OUT:** Use `Result.success(workDataOf(...))`
4. **Access result:** Use `workInfo.outputData` via LiveData or Flow

---

## Overview

WorkManager uses **`Data`** class for passing data:

```

  Activity   

        workDataOf("key" -> value)
       ↓

 WorkRequest  ← setInputData()

       
       ↓

   Worker     ← inputData.getString("key")
             
   doWork()   → Result.success(workDataOf("result" -> value))

       
       ↓

  Activity    ← workInfo.outputData.getString("result")

```

---

## Passing Data TO Worker (Input Data)

### Basic Example

```kotlin
import androidx.work.*

class MainActivity : AppCompatActivity() {

    private fun startWork() {
        // Create input data
        val inputData = workDataOf(
            "user_id" to "user123",
            "count" to 42,
            "is_premium" to true,
            "items" to arrayOf("item1", "item2", "item3")
        )

        // Create work request with input data
        val workRequest = OneTimeWorkRequestBuilder<MyWorker>()
            .setInputData(inputData)
            .build()

        // Enqueue work
        WorkManager.getInstance(applicationContext).enqueue(workRequest)
    }
}
```

---

### Accessing Input Data in Worker

```kotlin
import android.content.Context
import androidx.work.*

class MyWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        // Get input data
        val userId = inputData.getString("user_id") ?: return Result.failure()
        val count = inputData.getInt("count", 0)
        val isPremium = inputData.getBoolean("is_premium", false)
        val items = inputData.getStringArray("items")

        // Use the data
        println("User ID: $userId")
        println("Count: $count")
        println("Premium: $isPremium")
        println("Items: ${items?.joinToString()}")

        // Perform work
        val result = processData(userId, count, isPremium)

        // Return success (optionally with output data)
        return Result.success(workDataOf("result" to result))
    }

    private suspend fun processData(
        userId: String,
        count: Int,
        isPremium: Boolean
    ): String {
        // Work logic
        kotlinx.coroutines.delay(2000)
        return "Processed $count items for $userId"
    }
}
```

---

## Returning Data FROM Worker (Output Data)

### Worker with Output Data

```kotlin
class DataProcessingWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            // Get input
            val inputValue = inputData.getInt("input_value", 0)

            // Process
            val processedValue = inputValue * 2
            val timestamp = System.currentTimeMillis()
            val status = "completed"

            // Return output data
            val outputData = workDataOf(
                "processed_value" to processedValue,
                "timestamp" to timestamp,
                "status" to status,
                "message" to "Successfully processed $inputValue"
            )

            Result.success(outputData)

        } catch (e: Exception) {
            // Return error data
            val errorData = workDataOf(
                "error_message" to e.message,
                "error_type" to e::class.simpleName
            )

            Result.failure(errorData)
        }
    }
}
```

---

### Receiving Output Data

```kotlin
import androidx.lifecycle.Observer

class MainActivity : AppCompatActivity() {

    private fun observeWorkResult(workRequest: OneTimeWorkRequest) {
        WorkManager.getInstance(applicationContext)
            .getWorkInfoByIdLiveData(workRequest.id)
            .observe(this, Observer { workInfo ->
                when (workInfo.state) {
                    WorkInfo.State.SUCCEEDED -> {
                        // Extract output data
                        val processedValue = workInfo.outputData.getInt("processed_value", 0)
                        val timestamp = workInfo.outputData.getLong("timestamp", 0)
                        val status = workInfo.outputData.getString("status")
                        val message = workInfo.outputData.getString("message")

                        textView.text = """
                            Status: $status
                            Value: $processedValue
                            Time: $timestamp
                            Message: $message
                        """.trimIndent()
                    }

                    WorkInfo.State.FAILED -> {
                        // Extract error data
                        val errorMessage = workInfo.outputData.getString("error_message")
                        val errorType = workInfo.outputData.getString("error_type")

                        textView.text = "Error ($errorType): $errorMessage"
                    }

                    WorkInfo.State.RUNNING -> {
                        textView.text = "Processing..."
                    }

                    else -> {
                        // ENQUEUED, BLOCKED, CANCELLED
                    }
                }
            })
    }
}
```

---

## Supported Data Types

### Data Class Methods

```kotlin
// Create Data object
val data = workDataOf(
    "string_key" to "value",
    "int_key" to 42,
    "long_key" to 123L,
    "float_key" to 3.14f,
    "double_key" to 2.718,
    "boolean_key" to true
)

// Arrays
val arrayData = workDataOf(
    "string_array" to arrayOf("a", "b", "c"),
    "int_array" to intArrayOf(1, 2, 3),
    "long_array" to longArrayOf(1L, 2L, 3L),
    "float_array" to floatArrayOf(1.0f, 2.0f),
    "double_array" to doubleArrayOf(1.0, 2.0),
    "boolean_array" to booleanArrayOf(true, false)
)
```

### Get Methods in Worker

```kotlin
// Primitives
val stringValue = inputData.getString("string_key") // Returns String?
val intValue = inputData.getInt("int_key", defaultValue = 0)
val longValue = inputData.getLong("long_key", defaultValue = 0L)
val floatValue = inputData.getFloat("float_key", defaultValue = 0f)
val doubleValue = inputData.getDouble("double_key", defaultValue = 0.0)
val booleanValue = inputData.getBoolean("boolean_key", defaultValue = false)

// Arrays
val stringArray = inputData.getStringArray("string_array")
val intArray = inputData.getIntArray("int_array")
val longArray = inputData.getLongArray("long_array")
val floatArray = inputData.getFloatArray("float_array")
val doubleArray = inputData.getDoubleArray("double_array")
val booleanArray = inputData.getBooleanArray("boolean_array")
```

---

## Passing Complex Objects

### Option 1: JSON Serialization (Recommended)

```kotlin
import kotlinx.serialization.*
import kotlinx.serialization.json.Json

@Serializable
data class User(
    val id: String,
    val name: String,
    val age: Int,
    val email: String
)

class UserDataWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        // Get JSON from input
        val userJson = inputData.getString("user_json") ?: return Result.failure()

        // Deserialize
        val user = Json.decodeFromString<User>(userJson)

        // Process
        println("Processing user: ${user.name}, ${user.email}")

        // Return result with serialized object
        val resultUser = user.copy(name = "${user.name} (processed)")
        val resultJson = Json.encodeToString(resultUser)

        return Result.success(workDataOf("result_json" to resultJson))
    }
}

// Usage
val user = User("1", "Alice", 25, "alice@example.com")
val userJson = Json.encodeToString(user)

val workRequest = OneTimeWorkRequestBuilder<UserDataWorker>()
    .setInputData(workDataOf("user_json" to userJson))
    .build()

WorkManager.getInstance(context).enqueue(workRequest)
```

---

### Option 2: Multiple Primitive Values

```kotlin
// Pass object as separate fields
data class Task(
    val id: String,
    val title: String,
    val priority: Int,
    val isDone: Boolean
)

val task = Task("task1", "Buy groceries", 3, false)

val inputData = workDataOf(
    "task_id" to task.id,
    "task_title" to task.title,
    "task_priority" to task.priority,
    "task_is_done" to task.isDone
)

// In Worker
override suspend fun doWork(): Result {
    val task = Task(
        id = inputData.getString("task_id") ?: "",
        title = inputData.getString("task_title") ?: "",
        priority = inputData.getInt("task_priority", 0),
        isDone = inputData.getBoolean("task_is_done", false)
    )

    // Process task
    val updatedTask = processTask(task)

    return Result.success(workDataOf(
        "result_id" to updatedTask.id,
        "result_title" to updatedTask.title,
        "result_priority" to updatedTask.priority,
        "result_is_done" to updatedTask.isDone
    ))
}
```

---

## Data Size Limitations

### Size Limit

**Data size is limited to ~10KB** (10,240 bytes total).

```kotlin
// - BAD: Large data
val largeData = workDataOf(
    "large_string" to "A".repeat(20000) // Exceeds limit!
)
// Throws: IllegalStateException - Data cannot occupy more than 10240 bytes

// - GOOD: Pass reference instead
val data = workDataOf(
    "file_path" to "/path/to/file.txt", // Small reference
    "user_id" to "user123"
)
```

---

### Workaround for Large Data

**Option 1: Save to file/database and pass ID**

```kotlin
// In Activity
val largeData = getLargeDataObject()

// Save to database
val dataId = database.insertData(largeData)

// Pass only ID
val workRequest = OneTimeWorkRequestBuilder<MyWorker>()
    .setInputData(workDataOf("data_id" to dataId))
    .build()

// In Worker
override suspend fun doWork(): Result {
    val dataId = inputData.getLong("data_id", 0)
    val largeData = database.getData(dataId) // Retrieve full data

    processData(largeData)

    return Result.success()
}
```

**Option 2: Use FileProvider for files**

```kotlin
// In Activity
val file = File(cacheDir, "large_data.bin")
file.writeBytes(largeDataBytes)

val workRequest = OneTimeWorkRequestBuilder<MyWorker>()
    .setInputData(workDataOf("file_path" to file.absolutePath))
    .build()

// In Worker
override suspend fun doWork(): Result {
    val filePath = inputData.getString("file_path") ?: return Result.failure()
    val file = File(filePath)

    if (!file.exists()) return Result.failure()

    val data = file.readBytes()
    processData(data)

    return Result.success()
}
```

---

## Complete Example: Bidirectional Data Flow

```kotlin
// Data model
@Serializable
data class ImageProcessingRequest(
    val imageUrl: String,
    val filters: List<String>,
    val quality: Int
)

@Serializable
data class ImageProcessingResult(
    val originalUrl: String,
    val processedUrl: String,
    val appliedFilters: List<String>,
    val processingTime: Long,
    val fileSize: Long
)

// Worker
class ImageProcessingWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            // Get input
            val requestJson = inputData.getString("request") ?: return Result.failure()
            val request = Json.decodeFromString<ImageProcessingRequest>(requestJson)

            // Process
            val startTime = System.currentTimeMillis()

            val processedImageUrl = processImage(
                request.imageUrl,
                request.filters,
                request.quality
            )

            val processingTime = System.currentTimeMillis() - startTime

            // Create result
            val result = ImageProcessingResult(
                originalUrl = request.imageUrl,
                processedUrl = processedImageUrl,
                appliedFilters = request.filters,
                processingTime = processingTime,
                fileSize = getFileSize(processedImageUrl)
            )

            val resultJson = Json.encodeToString(result)

            Result.success(workDataOf("result" to resultJson))

        } catch (e: Exception) {
            Result.failure(workDataOf("error" to e.message))
        }
    }

    private suspend fun processImage(
        imageUrl: String,
        filters: List<String>,
        quality: Int
    ): String {
        // Image processing logic
        kotlinx.coroutines.delay(3000)
        return "https://example.com/processed_image.jpg"
    }

    private fun getFileSize(url: String): Long {
        return 1024 * 512 // 512KB
    }
}

// Activity
class MainActivity : AppCompatActivity() {

    private val workManager by lazy { WorkManager.getInstance(applicationContext) }

    private fun processImage() {
        val request = ImageProcessingRequest(
            imageUrl = "https://example.com/image.jpg",
            filters = listOf("blur", "sepia", "contrast"),
            quality = 85
        )

        val requestJson = Json.encodeToString(request)

        val workRequest = OneTimeWorkRequestBuilder<ImageProcessingWorker>()
            .setInputData(workDataOf("request" to requestJson))
            .build()

        workManager.enqueue(workRequest)

        workManager.getWorkInfoByIdLiveData(workRequest.id)
            .observe(this) { workInfo ->
                when (workInfo.state) {
                    WorkInfo.State.SUCCEEDED -> {
                        val resultJson = workInfo.outputData.getString("result") ?: return@observe
                        val result = Json.decodeFromString<ImageProcessingResult>(resultJson)

                        textView.text = """
                            Original: ${result.originalUrl}
                            Processed: ${result.processedUrl}
                            Filters: ${result.appliedFilters.joinToString()}
                            Time: ${result.processingTime}ms
                            Size: ${result.fileSize / 1024}KB
                        """.trimIndent()
                    }

                    WorkInfo.State.FAILED -> {
                        val error = workInfo.outputData.getString("error")
                        textView.text = "Error: $error"
                    }

                    WorkInfo.State.RUNNING -> {
                        textView.text = "Processing image..."
                    }

                    else -> { /* Other states */ }
                }
            }
    }
}
```

---

## Summary

**How to pass data TO WorkManager:**

1. Create Data object:
   ```kotlin
   val inputData = workDataOf("key" to value)
   ```

2. Set on WorkRequest:
   ```kotlin
   val workRequest = OneTimeWorkRequestBuilder<MyWorker>()
       .setInputData(inputData)
       .build()
   ```

3. Access in Worker:
   ```kotlin
   val value = inputData.getString("key")
   ```

**How to get data FROM WorkManager:**

1. Return in Worker:
   ```kotlin
   Result.success(workDataOf("result" to value))
   ```

2. Observe in Activity:
   ```kotlin
   workManager.getWorkInfoByIdLiveData(workRequest.id)
       .observe(this) { workInfo ->
           if (workInfo.state == WorkInfo.State.SUCCEEDED) {
               val result = workInfo.outputData.getString("result")
           }
       }
   ```

**Limitations:**
- WARNING: Maximum size: ~10KB total
- WARNING: Only primitive types and arrays
- - Use JSON for complex objects
- - Pass file paths or IDs for large data

---

## Ответ (RU)
Данные передаются с помощью специального контейнера **Data**:

1. **Передача IN:** `setInputData(workDataOf(...))` при создании WorkRequest
2. **Получение в Worker:** `inputData.getString()`, `inputData.getInt()`, и т.д.
3. **Возврат OUT:** `Result.success(workDataOf(...))`
4. **Получение результата:** `workInfo.outputData` через LiveData

**Пример:**

```kotlin
// Передача данных
val inputData = workDataOf(
    "user_id" to "user123",
    "count" to 42
)

val workRequest = OneTimeWorkRequestBuilder<MyWorker>()
    .setInputData(inputData)
    .build()

// В Worker
override suspend fun doWork(): Result {
    val userId = inputData.getString("user_id")
    val count = inputData.getInt("count", 0)

    val result = processData(userId, count)

    return Result.success(workDataOf("result" to result))
}

// Получение результата
workManager.getWorkInfoByIdLiveData(workRequest.id)
    .observe(this) { workInfo ->
        if (workInfo.state == WorkInfo.State.SUCCEEDED) {
            val result = workInfo.outputData.getString("result")
        }
    }
```

**Ограничения:**
- Максимум ~10KB данных
- Только примитивные типы и массивы
- Для сложных объектов используйте JSON
- Для больших данных передавайте ID или путь к файлу

