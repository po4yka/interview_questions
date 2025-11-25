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
updated: 2025-11-10
sources: ["https://developer.android.com/topic/libraries/architecture/workmanager/advanced/custom-configuration"]
tags: [android/background-execution, android/coroutines, background-processing, data-passing, difficulty/medium, workmanager]

date created: Saturday, November 1st 2025, 12:47:12 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---

# Вопрос (RU)

> Как передать данные в WorkManager Worker и получить результат обратно? Какие типы данных поддерживаются и какие есть ограничения?

# Question (EN)

> How to pass data to WorkManager Worker and receive results back? What data types are supported and what are the limitations?

## Ответ (RU)

WorkManager использует класс **Data** для передачи небольших наборов данных (конфигурации, параметры) между вызывающим кодом (например, `Activity`/Repository) и Worker. Связано с [[c-workmanager]], [[c-coroutines]], [[c-background-tasks]].

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
        val userId = inputData.getString("user_id") ?: return Result.failure(
            workDataOf("error" to "Missing user_id")
        )
        val count = inputData.getInt("count", 0) // ✅ С дефолтным значением
        val isPremium = inputData.getBoolean("is_premium", false)

        val result = processData(userId, count, isPremium)

        // ✅ Возвращаем результат
        return Result.success(workDataOf("result" to result))
    }
}
```

### Получение Данных ИЗ Worker (Output)

```kotlin
WorkManager.getInstance(context)
    .getWorkInfoByIdLiveData(workRequest.id)
    .observe(this /* LifecycleOwner */) { workInfo ->
        when (workInfo.state) {
            WorkInfo.State.SUCCEEDED -> {
                // ✅ Извлекаем выходные данные
                val result = workInfo.outputData.getString("result")
                textView.text = "Result: $result"
            }
            WorkInfo.State.FAILED -> {
                // ❌ Ошибка (Worker должен положить описание в outputData)
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
    "string" to "value",                 // ✅ String
    "int" to 42,                         // ✅ Int
    "long" to 123L,                      // ✅ Long
    "double" to 2.718,                   // ✅ Double (Float напрямую не поддерживается, приводите к Double)
    "boolean" to true,                   // ✅ Boolean
    "string_array" to arrayOf("a", "b"), // ✅ Array<String>
    "int_array" to intArrayOf(1, 2),     // ✅ IntArray
    "long_array" to longArrayOf(1L, 2L), // ✅ LongArray
    "double_array" to doubleArrayOf(1.0, 2.0), // ✅ DoubleArray
    "boolean_array" to booleanArrayOf(true, false) // ✅ BooleanArray
)

// ❌ НЕ поддерживается: произвольные custom-объекты напрямую
// ✅ Используйте сериализацию (например, JSON) для сложных объектов
```

### Передача Сложных Объектов Через JSON

```kotlin
@Serializable
data class User(val id: String, val name: String)

// ✅ Сериализуем в JSON
val user = User("1", "Alice")
val json = Json // kotlinx.serialization.json.Json
val userJson = json.encodeToString(user)

val workRequest = OneTimeWorkRequestBuilder<UserWorker>()
    .setInputData(workDataOf("user_json" to userJson))
    .build()

class UserWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val json = Json
        val userJson = inputData.getString("user_json") ?: return Result.failure(
            workDataOf("error" to "Missing user_json")
        )
        val user = json.decodeFromString<User>(userJson)

        // ... обрабатываем user по необходимости
        return Result.success()
    }
}
```

### Ограничения По Размеру Данных

**Максимум ~10KB** (10,240 байт) на все Data — при превышении будет `IllegalStateException` при построении/использовании запроса.

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

class MyWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val dataId = inputData.getLong("data_id", 0L)
        // ✅ Обработка только при валидном ID
        if (dataId == 0L) return Result.failure(
            workDataOf("error" to "Invalid data_id")
        )

        val largeData = database.getData(dataId) // ✅ Полные данные
        processData(largeData)
        return Result.success()
    }
}
```

### Дополнительные Вопросы (RU)

- Как WorkManager гарантирует доставку данных при гибели процесса?
- Что происходит с выходными данными, если приложение завершится до их получения наблюдателем (данные остаются в WorkInfo до очистки истории)?
- Можно ли связывать несколько Worker и передавать данные между ними (через `WorkContinuation` и `InputMerger`)?

### Ссылки (RU)

- https://developer.android.com/topic/libraries/architecture/workmanager — официальное руководство по WorkManager
- https://developer.android.com/reference/androidx/work/Data — документация по классу Data

### Связанные Вопросы (RU)

#### Предварительные Материалы
- [[c-workmanager]] — концепция WorkManager
- [[c-coroutines]] — корутины Kotlin
- [[c-background-tasks]] — фоновые задачи

#### На Том Же Уровне
- [[q-workmanager-execution-guarantee--android--medium]] — гарантии выполнения
- [[q-workmanager-vs-alternatives--android--medium]] — WorkManager vs альтернативы

#### Продвинутое
- [[q-workmanager-advanced--android--medium]] — продвинутые паттерны WorkManager

---

## Answer (EN)

WorkManager uses the **Data** class to pass small sets of primitive/configuration data between the caller (e.g., `Activity`/Repository) and a Worker. Related to [[c-workmanager]], [[c-coroutines]], [[c-background-tasks]].

### Passing Data TO Worker

```kotlin
// ✅ Create input data
val inputData = workDataOf(
    "user_id" to "user123",
    "count" to 42,
    "is_premium" to true
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
        val userId = inputData.getString("user_id") ?: return Result.failure(
            workDataOf("error" to "Missing user_id")
        )
        val count = inputData.getInt("count", 0) // ✅ With default
        val isPremium = inputData.getBoolean("is_premium", false)

        val result = processData(userId, count, isPremium)

        // ✅ Return output
        return Result.success(workDataOf("result" to result))
    }
}
```

### Receiving Data FROM Worker

```kotlin
WorkManager.getInstance(context)
    .getWorkInfoByIdLiveData(workRequest.id)
    .observe(this /* LifecycleOwner */) { workInfo ->
        when (workInfo.state) {
            WorkInfo.State.SUCCEEDED -> {
                // ✅ Extract output
                val result = workInfo.outputData.getString("result")
                // use result, e.g. update UI: textView.text = "Result: $result"
            }
            WorkInfo.State.FAILED -> {
                // ❌ Error (Worker should put description into outputData)
                val error = workInfo.outputData.getString("error")
                // handle error, e.g. textView.text = "Error: $error"
            }
            WorkInfo.State.RUNNING -> {
                // optional: show progress state, e.g. textView.text = "Processing..."
            }
            else -> { /* ENQUEUED, BLOCKED, CANCELLED */ }
        }
    }
```

### Supported Data Types

```kotlin
val data = workDataOf(
    "string" to "value",                 // ✅ String
    "int" to 42,                         // ✅ Int
    "long" to 123L,                      // ✅ Long
    "double" to 2.718,                   // ✅ Double (Float is not directly supported; convert to Double)
    "boolean" to true,                   // ✅ Boolean
    "string_array" to arrayOf("a", "b"), // ✅ Array<String>
    "int_array" to intArrayOf(1, 2),     // ✅ IntArray
    "long_array" to longArrayOf(1L, 2L), // ✅ LongArray
    "double_array" to doubleArrayOf(1.0, 2.0), // ✅ DoubleArray
    "boolean_array" to booleanArrayOf(true, false) // ✅ BooleanArray
)

// ❌ NOT supported: arbitrary custom objects directly
// ✅ Use serialization (e.g., JSON) for complex objects
```

### Passing Complex Objects via JSON

```kotlin
@Serializable
data class User(val id: String, val name: String)

// ✅ Serialize to JSON
val user = User("1", "Alice")
val json = Json // kotlinx.serialization.json.Json
val userJson = json.encodeToString(user)

val workRequest = OneTimeWorkRequestBuilder<UserWorker>()
    .setInputData(workDataOf("user_json" to userJson))
    .build()

class UserWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val json = Json
        val userJson = inputData.getString("user_json") ?: return Result.failure(
            workDataOf("error" to "Missing user_json")
        )
        val user = json.decodeFromString<User>(userJson)

        // ... process user as needed
        return Result.success()
    }
}
```

### Data Size Limitations

**Maximum ~10KB** (10,240 bytes) for the entire Data payload — exceeding this will throw an `IllegalStateException` when building or using the request.

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

class MyWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val dataId = inputData.getLong("data_id", 0L)
        if (dataId == 0L) return Result.failure(
            workDataOf("error" to "Invalid data_id")
        )

        val largeData = database.getData(dataId) // ✅ Full data
        // ... process largeData
        return Result.success()
    }
}
```

---

## Follow-ups

- How does WorkManager guarantee data delivery across process death?
- What happens to output data if the app is killed before observation (it remains in WorkInfo until history is pruned)?
- Can you chain workers and pass data between them (via `WorkContinuation` and `InputMerger`)?

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
