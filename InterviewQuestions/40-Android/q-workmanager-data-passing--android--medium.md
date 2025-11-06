---
id: android-210
title: "WorkManager Data Passing / Передача данных WorkManager"
aliases: [WorkManager Data Passing, WorkManager Input Output, WorkManager workDataOf, Передача данных WorkManager]
topic: android
subtopics: [background-execution, coroutines]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-coroutines, c-workmanager, q-workmanager-execution-guarantee--android--medium]
created: 2025-10-15
updated: 2025-10-27
sources: [https://developer.android.com/topic/libraries/architecture/workmanager/advanced/custom-configuration]
tags: [android/background-execution, android/coroutines, background-processing, data-passing, difficulty/medium, workmanager]
---

# Вопрос (RU)

> Как передать данные в WorkManager Worker и получить результат обратно? Какие типы данных поддерживаются и какие есть ограничения?

# Question (EN)

> How to pass data to WorkManager Worker and receive results back? What data types are supported and what are the limitations?

## Ответ (RU)

WorkManager использует класс **Data** для передачи данных между `Activity` и Worker. Связано с [[c-workmanager]], [[c-coroutines]], [[c-background-tasks]].

### Передача Данных В Worker (Input)

```kotlin
// ✅ Создаем входные данные
val inputData = workDataOf(
    "user_id" to "user123",
    "count" to 42,
    "is_premium" to true
)

// ✅ Создаем WorkRequest с данными
val workRequest = OneTimeWorkRequestBuilder<MyWorker>()
    .setInputData(inputData)
    .build()

WorkManager.getInstance(context).enqueue(workRequest)
```

### Получение Данных В Worker

```kotlin
class MyWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        // ✅ Читаем входные данные
        val userId = inputData.getString("user_id") ?: return Result.failure()
        val count = inputData.getInt("count", 0) // ✅ С дефолтным значением
        val isPremium = inputData.getBoolean("is_premium", false)

        val result = processData(userId, count)

        // ✅ Возвращаем результат
        return Result.success(workDataOf("result" to result))
    }
}
```

### Получение Данных ИЗ Worker (Output)

```kotlin
WorkManager.getInstance(context)
    .getWorkInfoByIdLiveData(workRequest.id)
    .observe(this) { workInfo ->
        when (workInfo.state) {
            WorkInfo.State.SUCCEEDED -> {
                // ✅ Извлекаем выходные данные
                val result = workInfo.outputData.getString("result")
                textView.text = "Result: $result"
            }
            WorkInfo.State.FAILED -> {
                // ❌ Ошибка
                val error = workInfo.outputData.getString("error")
                textView.text = "Error: $error"
            }
            WorkInfo.State.RUNNING -> {
                textView.text = "Processing..."
            }
            else -> { /* ENQUEUED, BLOCKED, CANCELLED */ }
        }
    }
```

### Поддерживаемые Типы Данных

```kotlin
val data = workDataOf(
    "string" to "value",      // ✅ String
    "int" to 42,              // ✅ Int
    "long" to 123L,           // ✅ Long
    "float" to 3.14f,         // ✅ Float
    "double" to 2.718,        // ✅ Double
    "boolean" to true,        // ✅ Boolean
    "string_array" to arrayOf("a", "b") // ✅ Массивы примитивов
)

// ❌ НЕ поддерживается: custom объекты напрямую
// ✅ Используйте JSON для сложных объектов
```

### Передача Сложных Объектов Через JSON

```kotlin
@Serializable
data class User(val id: String, val name: String, val age: Int)

// ✅ Сериализуем в JSON
val user = User("1", "Alice", 25)
val userJson = Json.encodeToString(user)

val workRequest = OneTimeWorkRequestBuilder<UserWorker>()
    .setInputData(workDataOf("user_json" to userJson))
    .build()

// ✅ В Worker десериализуем
override suspend fun doWork(): Result {
    val userJson = inputData.getString("user_json") ?: return Result.failure()
    val user = Json.decodeFromString<User>(userJson)

    val resultUser = processUser(user)
    val resultJson = Json.encodeToString(resultUser)

    return Result.success(workDataOf("result_json" to resultJson))
}
```

### Ограничения По Размеру Данных

**Максимум ~10KB** (10,240 байт) — иначе `IllegalStateException`

```kotlin
// ❌ ПЛОХО: превышает лимит
val largeData = workDataOf("large_string" to "A".repeat(20000))

// ✅ ХОРОШО: передаем ссылку
val data = workDataOf("file_path" to "/path/to/file.txt")
```

**Решение для больших данных:**

1. Сохраните данные в базу/файл
2. Передайте только ID или путь к файлу
3. В Worker загрузите данные по ID/пути

```kotlin
// ✅ Передаем ID вместо больших данных
val dataId = database.insert(largeObject)
val workRequest = OneTimeWorkRequestBuilder<MyWorker>()
    .setInputData(workDataOf("data_id" to dataId))
    .build()

// ✅ В Worker загружаем по ID
override suspend fun doWork(): Result {
    val dataId = inputData.getLong("data_id", 0)
    val largeData = database.getData(dataId) // ✅ Полные данные
    processData(largeData)
    return Result.success()
}
```

---

## Answer (EN)

WorkManager uses **Data** class for passing data between `Activity` and Worker. Related to [[c-workmanager]], [[c-coroutines]], [[c-background-tasks]].

### Passing Data TO Worker

```kotlin
// ✅ Create input data
val inputData = workDataOf(
    "user_id" to "user123",
    "count" to 42
)

// ✅ Create WorkRequest
val workRequest = OneTimeWorkRequestBuilder<MyWorker>()
    .setInputData(inputData)
    .build()

WorkManager.getInstance(context).enqueue(workRequest)
```

### Receiving Data in Worker

```kotlin
class MyWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        // ✅ Read input
        val userId = inputData.getString("user_id") ?: return Result.failure()
        val count = inputData.getInt("count", 0) // ✅ With default

        // ✅ Return output
        return Result.success(workDataOf("result" to "Done"))
    }
}
```

### Receiving Data FROM Worker

```kotlin
WorkManager.getInstance(context)
    .getWorkInfoByIdLiveData(workRequest.id)
    .observe(this) { workInfo ->
        when (workInfo.state) {
            WorkInfo.State.SUCCEEDED -> {
                // ✅ Extract output
                val result = workInfo.outputData.getString("result")
            }
            WorkInfo.State.FAILED -> {
                // ❌ Error
                val error = workInfo.outputData.getString("error")
            }
            else -> { /* RUNNING, ENQUEUED, etc. */ }
        }
    }
```

### Supported Data Types

```kotlin
val data = workDataOf(
    "string" to "value",    // ✅ String
    "int" to 42,            // ✅ Int
    "long" to 123L,         // ✅ Long
    "float" to 3.14f,       // ✅ Float
    "double" to 2.718,      // ✅ Double
    "boolean" to true,      // ✅ Boolean
    "array" to arrayOf("a", "b") // ✅ Primitive arrays
)

// ❌ NOT supported: custom objects directly
// ✅ Use JSON for complex objects
```

### Passing Complex Objects via JSON

```kotlin
@Serializable
data class User(val id: String, val name: String)

// ✅ Serialize to JSON
val userJson = Json.encodeToString(user)
val workRequest = OneTimeWorkRequestBuilder<UserWorker>()
    .setInputData(workDataOf("user_json" to userJson))
    .build()

// ✅ Deserialize in Worker
override suspend fun doWork(): Result {
    val user = Json.decodeFromString<User>(inputData.getString("user_json")!!)
    return Result.success()
}
```

### Data Size Limitations

**Maximum ~10KB** (10,240 bytes) — otherwise `IllegalStateException`

```kotlin
// ❌ BAD: exceeds limit
val largeData = workDataOf("large" to "A".repeat(20000))

// ✅ GOOD: pass reference
val data = workDataOf("file_path" to "/path/to/file.txt")
```

**Solution for large data:**

1. Save data to database/file
2. Pass only ID or file path
3. Load data by ID/path in Worker

```kotlin
// ✅ Pass ID instead of large data
val dataId = database.insert(largeObject)
val workRequest = OneTimeWorkRequestBuilder<MyWorker>()
    .setInputData(workDataOf("data_id" to dataId))
    .build()

// ✅ Load by ID in Worker
override suspend fun doWork(): Result {
    val dataId = inputData.getLong("data_id", 0)
    val largeData = database.getData(dataId) // ✅ Full data
    return Result.success()
}
```

---

## Follow-ups

- How does WorkManager guarantee data delivery across process death?
- What happens to output data if the app is killed before observation?
- Can you chain workers and pass data between them?

## References

- https://developer.android.com/topic/libraries/architecture/workmanager — Official WorkManager guide
- https://developer.android.com/reference/androidx/work/Data — Data class documentation

## Related Questions

### Prerequisites
- [[c-workmanager]] - WorkManager concept
- [[c-coroutines]] - Kotlin coroutines
- [[c-background-tasks]] - Background processing

### Same Level
- [[q-workmanager-execution-guarantee--android--medium]] - Execution guarantees
- [[q-workmanager-vs-alternatives--android--medium]] - WorkManager vs alternatives

### Advanced
- [[q-workmanager-advanced--android--medium]] - Advanced WorkManager patterns
