---
id: android-414
title: "Workmanager Return Result / Возврат результата WorkManager"
aliases: ["Workmanager Return Result", "Возврат результата WorkManager"]
topic: android
subtopics: [background-execution, coroutines]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-workmanager, c-coroutines, q-workmanager-constraints--android--medium]
created: 2025-10-15
updated: 2025-10-29
sources: []
tags: [android/background-execution, android/coroutines, background-processing, coroutines, livedata, workmanager, difficulty/medium]
date created: Wednesday, October 29th 2025, 1:01:15 pm
date modified: Thursday, October 30th 2025, 11:51:06 am
---

# Вопрос (RU)

Как вернуть результат работы WorkManager в приложение?

# Question (EN)

How to return a result from WorkManager to the app?

---

## Ответ (RU)

WorkManager возвращает результаты через механизм `outputData`:

**Основной подход**:
1. В Worker используем `Result.success(outputData)` для передачи данных
2. В Activity/ViewModel наблюдаем за `WorkInfo` через LiveData или Flow
3. Проверяем состояние `WorkInfo.State.SUCCEEDED`
4. Извлекаем данные из `workInfo.outputData`

### Реализация Worker

```kotlin
class DataWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val input = inputData.getInt("value", 0)
            val result = processData(input) // ✅ Perform work

            // ✅ Return success with output data
            Result.success(workDataOf(
                "result" to result,
                "timestamp" to System.currentTimeMillis()
            ))
        } catch (e: IOException) {
            Result.retry() // ✅ Network error - retry
        } catch (e: Exception) {
            // ❌ Fatal error - fail with error info
            Result.failure(workDataOf("error" to e.message))
        }
    }
}
```

### Наблюдение в ViewModel (рекомендуемый способ)

```kotlin
class DataViewModel(
    private val workManager: WorkManager
) : ViewModel() {

    private val _result = MutableLiveData<WorkResult>()
    val result: LiveData<WorkResult> = _result

    fun startWork(value: Int) {
        val request = OneTimeWorkRequestBuilder<DataWorker>()
            .setInputData(workDataOf("value" to value))
            .build()

        workManager.enqueue(request)

        // ✅ Observe work status
        workManager.getWorkInfoByIdLiveData(request.id)
            .observeForever { workInfo ->
                when (workInfo.state) {
                    WorkInfo.State.SUCCEEDED -> {
                        val result = workInfo.outputData.getString("result")
                        _result.value = WorkResult.Success(result)
                    }
                    WorkInfo.State.FAILED -> {
                        val error = workInfo.outputData.getString("error")
                        _result.value = WorkResult.Error(error)
                    }
                    WorkInfo.State.RUNNING -> {
                        _result.value = WorkResult.Loading
                    }
                    else -> {} // ENQUEUED, BLOCKED, CANCELLED
                }
            }
    }
}

sealed class WorkResult {
    object Loading : WorkResult()
    data class Success(val data: String?) : WorkResult()
    data class Error(val message: String?) : WorkResult()
}
```

### Современный подход с Flow

```kotlin
class DataRepository(
    private val workManager: WorkManager
) {
    fun processData(value: Int): Flow<WorkResult> = flow {
        val request = OneTimeWorkRequestBuilder<DataWorker>()
            .setInputData(workDataOf("value" to value))
            .build()

        workManager.enqueue(request)

        // ✅ Convert LiveData to Flow
        workManager.getWorkInfoByIdFlow(request.id)
            .collect { workInfo ->
                emit(when (workInfo.state) {
                    WorkInfo.State.SUCCEEDED -> {
                        val result = workInfo.outputData.getString("result")
                        WorkResult.Success(result)
                    }
                    WorkInfo.State.FAILED -> {
                        val error = workInfo.outputData.getString("error")
                        WorkResult.Error(error)
                    }
                    else -> WorkResult.Loading
                })
            }
    }
}
```

### Передача сложных данных через JSON

```kotlin
@Serializable
data class ProcessingResult(
    val processed: Int,
    val total: Int,
    val errors: List<String>
)

class ComplexDataWorker(...) : CoroutineWorker(...) {
    override suspend fun doWork(): Result {
        val result = ProcessingResult(
            processed = 100,
            total = 150,
            errors = listOf("Error 1", "Error 2")
        )

        // ✅ Serialize complex data to JSON
        val json = Json.encodeToString(result)
        return Result.success(workDataOf("result_json" to json))
    }
}

// In observer:
val json = workInfo.outputData.getString("result_json")
val result = Json.decodeFromString<ProcessingResult>(json)
```

### Наблюдение по тегу или уникальному имени

```kotlin
// By tag
workManager.getWorkInfosByTagLiveData("data_sync")
    .observe(this) { workInfoList ->
        workInfoList.forEach { workInfo ->
            if (workInfo.state.isFinished) {
                processResult(workInfo.outputData)
            }
        }
    }

// By unique name
workManager.getWorkInfosForUniqueWorkLiveData("background_sync")
    .observe(this) { workInfoList ->
        workInfoList.firstOrNull()?.let { workInfo ->
            processResult(workInfo.outputData)
        }
    }
```

**Ключевые классы**:
- `workDataOf()` — создание Data объекта
- `Result.success(data)` — возврат с данными
- `Result.failure(data)` — возврат с ошибкой
- `WorkInfo.State` — состояние работы
- `workInfo.outputData` — извлечение результата

**Лучшие практики**:
- Используйте ViewModel для разделения логики
- Предпочитайте Flow для современного реактивного кода
- Сериализуйте сложные объекты в JSON
- Обрабатывайте все состояния (SUCCEEDED, FAILED, RUNNING)
- Для прогресса используйте `setProgress()` (API 29+)

---

## Answer (EN)

WorkManager returns results through the `outputData` mechanism:

**Core Approach**:
1. In Worker, use `Result.success(outputData)` to pass data
2. In Activity/ViewModel, observe `WorkInfo` via LiveData or Flow
3. Check for `WorkInfo.State.SUCCEEDED` state
4. Extract data from `workInfo.outputData`

### Worker Implementation

```kotlin
class DataWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val input = inputData.getInt("value", 0)
            val result = processData(input) // ✅ Perform work

            // ✅ Return success with output data
            Result.success(workDataOf(
                "result" to result,
                "timestamp" to System.currentTimeMillis()
            ))
        } catch (e: IOException) {
            Result.retry() // ✅ Network error - retry
        } catch (e: Exception) {
            // ❌ Fatal error - fail with error info
            Result.failure(workDataOf("error" to e.message))
        }
    }
}
```

### ViewModel Observation (Recommended)

```kotlin
class DataViewModel(
    private val workManager: WorkManager
) : ViewModel() {

    private val _result = MutableLiveData<WorkResult>()
    val result: LiveData<WorkResult> = _result

    fun startWork(value: Int) {
        val request = OneTimeWorkRequestBuilder<DataWorker>()
            .setInputData(workDataOf("value" to value))
            .build()

        workManager.enqueue(request)

        // ✅ Observe work status
        workManager.getWorkInfoByIdLiveData(request.id)
            .observeForever { workInfo ->
                when (workInfo.state) {
                    WorkInfo.State.SUCCEEDED -> {
                        val result = workInfo.outputData.getString("result")
                        _result.value = WorkResult.Success(result)
                    }
                    WorkInfo.State.FAILED -> {
                        val error = workInfo.outputData.getString("error")
                        _result.value = WorkResult.Error(error)
                    }
                    WorkInfo.State.RUNNING -> {
                        _result.value = WorkResult.Loading
                    }
                    else -> {} // ENQUEUED, BLOCKED, CANCELLED
                }
            }
    }
}

sealed class WorkResult {
    object Loading : WorkResult()
    data class Success(val data: String?) : WorkResult()
    data class Error(val message: String?) : WorkResult()
}
```

### Modern Flow Approach

```kotlin
class DataRepository(
    private val workManager: WorkManager
) {
    fun processData(value: Int): Flow<WorkResult> = flow {
        val request = OneTimeWorkRequestBuilder<DataWorker>()
            .setInputData(workDataOf("value" to value))
            .build()

        workManager.enqueue(request)

        // ✅ Convert LiveData to Flow
        workManager.getWorkInfoByIdFlow(request.id)
            .collect { workInfo ->
                emit(when (workInfo.state) {
                    WorkInfo.State.SUCCEEDED -> {
                        val result = workInfo.outputData.getString("result")
                        WorkResult.Success(result)
                    }
                    WorkInfo.State.FAILED -> {
                        val error = workInfo.outputData.getString("error")
                        WorkResult.Error(error)
                    }
                    else -> WorkResult.Loading
                })
            }
    }
}
```

### Passing Complex Data via JSON

```kotlin
@Serializable
data class ProcessingResult(
    val processed: Int,
    val total: Int,
    val errors: List<String>
)

class ComplexDataWorker(...) : CoroutineWorker(...) {
    override suspend fun doWork(): Result {
        val result = ProcessingResult(
            processed = 100,
            total = 150,
            errors = listOf("Error 1", "Error 2")
        )

        // ✅ Serialize complex data to JSON
        val json = Json.encodeToString(result)
        return Result.success(workDataOf("result_json" to json))
    }
}

// In observer:
val json = workInfo.outputData.getString("result_json")
val result = Json.decodeFromString<ProcessingResult>(json)
```

### Observing by Tag or Unique Name

```kotlin
// By tag
workManager.getWorkInfosByTagLiveData("data_sync")
    .observe(this) { workInfoList ->
        workInfoList.forEach { workInfo ->
            if (workInfo.state.isFinished) {
                processResult(workInfo.outputData)
            }
        }
    }

// By unique name
workManager.getWorkInfosForUniqueWorkLiveData("background_sync")
    .observe(this) { workInfoList ->
        workInfoList.firstOrNull()?.let { workInfo ->
            processResult(workInfo.outputData)
        }
    }
```

**Key Classes**:
- `workDataOf()` — create Data object
- `Result.success(data)` — return with data
- `Result.failure(data)` — return with error
- `WorkInfo.State` — work state
- `workInfo.outputData` — extract result

**Best Practices**:
- Use ViewModel for separation of concerns
- Prefer Flow for modern reactive code
- Serialize complex objects to JSON
- Handle all states (SUCCEEDED, FAILED, RUNNING)
- Use `setProgress()` for progress updates (API 29+)

---

## Follow-ups

1. How do you handle progress updates in long-running WorkManager tasks?
2. What are the size limitations for outputData in WorkManager?
3. How do you chain multiple Workers and pass data between them?
4. What's the difference between `observeForever()` and `observe()` for WorkInfo?
5. How do you handle WorkManager results when the app is killed and restarted?

---

## References

- [[c-workmanager]] — WorkManager core concepts
- [[c-coroutines]] — Kotlin coroutines fundamentals
- [[c-livedata]] — LiveData reactive pattern
- [[c-flow]] — Kotlin Flow fundamentals
- [WorkManager Documentation](https://developer.android.com/topic/libraries/architecture/workmanager)
- [WorkManager Advanced Guide](https://developer.android.com/topic/libraries/architecture/workmanager/advanced)

---

## Related Questions

### Prerequisites (Easier)
- [[q-workmanager-basics--android--easy]] — WorkManager fundamentals
- [[q-coroutine-basics--kotlin--easy]] — Coroutines introduction

### Related (Same Level)
- [[q-workmanager-constraints--android--medium]] — WorkManager constraints
- [[q-workmanager-chaining--android--medium]] — Chaining work requests
- [[q-livedata-vs-flow--kotlin--medium]] — LiveData vs Flow comparison

### Advanced (Harder)
- [[q-workmanager-testing--android--hard]] — Testing WorkManager
- [[q-background-execution-limits--android--hard]] — Background execution strategies
