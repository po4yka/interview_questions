---
id: android-173
title: "Workmanager Chaining / Цепочки WorkManager"
aliases: ["Workmanager Chaining", "Цепочки WorkManager"]
topic: android
subtopics: [background-execution, coroutines]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-coroutines, c-workmanager]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android, android/background-execution, android/coroutines, background, difficulty/hard, workmanager]
---

# Вопрос (RU)

> Объясните продвинутые паттерны цепочек WorkManager. Как реализовать параллельное выполнение, последовательные цепи и сложные графы зависимостей? Каковы best practices для обработки ошибок и передачи данных между воркерами?

# Question (EN)

> Explain advanced WorkManager chaining patterns. How do you implement parallel execution, sequential chains, and complex dependency graphs? What are best practices for error handling and data passing between workers?

## Ответ (RU)

[[c-workmanager|WorkManager]] предоставляет мощные возможности для построения сложных графов выполнения работ с зависимостями, параллельным выполнением и продвинутыми стратегиями обработки ошибок.

### Базовые Паттерны Цепочек

**Последовательное выполнение**
```kotlin
// ✅ Простая последовательная цепь
WorkManager.getInstance(context)
    .beginWith(downloadWorker)
    .then(processWorker)
    .then(uploadWorker)
    .enqueue()
```

**Параллельное выполнение**
```kotlin
// ✅ Fan-out: один воркер → несколько параллельных
WorkManager.getInstance(context)
    .beginWith(downloadWorker)
    .then(listOf(imageProcessor, videoProcessor, metadataExtractor))
    .enqueue()

// ✅ Fan-in: несколько параллельных → один агрегатор
WorkManager.getInstance(context)
    .beginWith(listOf(source1, source2, source3))
    .then(aggregatorWorker)
    .enqueue()
```

### Передача Данных Между Воркерами

**Ограничения WorkData**
- Максимальный размер: 10 KB
- Только примитивные типы и `String`/`Array`
- ❌ Не передавать большие объекты напрямую
- ✅ Передавать ID, пути к файлам, метаданные

```kotlin
class DownloadWorker : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        val fileId = inputData.getString("file_id") ?: return Result.failure()

        return try {
            val localPath = downloadFile(fileId)
            // ✅ Передаем только путь и метаданные
            Result.success(workDataOf(
                "file_id" to fileId,
                "local_path" to localPath,
                "file_size" to getFileSize(localPath)
            ))
        } catch (e: IOException) {
            if (runAttemptCount < 3) Result.retry()
            else Result.failure(workDataOf("error" to e.message))
        }
    }
}

class ProcessWorker : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        // ✅ Читаем outputData предыдущего воркера через inputData
        val localPath = inputData.getString("local_path") ?: return Result.failure()

        val processedPath = processFile(localPath)
        return Result.success(workDataOf("processed_path" to processedPath))
    }
}
```

### Обработка Ошибок

**Селективная retry-стратегия**
```kotlin
class ReliableWorker : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        return try {
            syncData()
            Result.success()
        } catch (e: NetworkException) {
            // ✅ Сетевые ошибки → retry с экспоненциальной задержкой
            if (runAttemptCount < 3) Result.retry()
            else Result.success(workDataOf("partial_success" to true))
        } catch (e: AuthException) {
            // ❌ Ошибки авторизации → немедленный failure
            Result.failure(workDataOf("error_type" to "auth"))
        } catch (e: ValidationException) {
            // ✅ Ошибки валидации → продолжить цепь
            Result.success(workDataOf(
                "partial_success" to true,
                "skipped_ids" to invalidIds.toJson()
            ))
        }
    }
}
```

**Fallback-цепи для критических сбоев**
```kotlin
// ✅ Основная цепь + fallback при сбое
workManager
    .beginWith(primaryChain)
    .then(fallbackWorker)  // Выполнится только если primary успешна
    .then(notificationWorker)
    .enqueue()
```

### Мониторинг И Наблюдение

**Отслеживание прогресса цепи**
```kotlin
class ChainMonitor(private val workManager: WorkManager) {
    fun monitorChain(chainTag: String): Flow<ChainStatus> =
        workManager.getWorkInfosByTagFlow(chainTag)
            .map { workInfos ->
                ChainStatus(
                    total = workInfos.size,
                    succeeded = workInfos.count { it.state == SUCCEEDED },
                    failed = workInfos.count { it.state == FAILED },
                    running = workInfos.count { it.state == RUNNING },
                    progress = calculateProgress(workInfos)
                )
            }

    private fun calculateProgress(workInfos: List<WorkInfo>): Int {
        val totalProgress = workInfos.sumOf { workInfo ->
            when (workInfo.state) {
                SUCCEEDED -> 100
                RUNNING -> workInfo.progress.getInt("progress", 0)
                else -> 0
            }
        }
        return if (workInfos.isNotEmpty()) totalProgress / workInfos.size else 0
    }
}
```

### Лучшие Практики

**1. Передача данных**
- Держите WorkData < 10 KB
- Используйте БД/файлы для больших данных
- Передавайте ID вместо объектов
- Сериализуйте через JSON для коллекций

**2. Обработка ошибок**
- Проектируйте для частичных сбоев
- Разные retry-политики для разных ошибок
- Передавайте контекст ошибки downstream
- Используйте fallback-цепи для критических операций

**3. Дизайн цепи**
- Используйте теги для группировки: `.addTag(batchId)`
- Минимизируйте количество воркеров
- Группируйте похожие операции
- Проектируйте для наблюдаемости

**4. Constraints и политики**
```kotlin
val worker = OneTimeWorkRequestBuilder<DownloadWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,
        MIN_BACKOFF_MILLIS,
        TimeUnit.MILLISECONDS
    )
    .build()
```

### Частые Ошибки

1. **Слишком сложные цепи** — усложняют отладку
2. **Большие объемы в WorkData** — превышают лимит 10 KB
3. **Циклические зависимости** — вызывают deadlock
4. **Отсутствие обработки ошибок** — блокируют всю цепь
5. **Нет reporting прогресса** — плохой UX

## Answer (EN)

[[c-workmanager|WorkManager]] provides powerful chaining capabilities for building complex work execution graphs with dependencies, parallel execution, and sophisticated error handling strategies.

### Basic Chaining Patterns

**Sequential execution**
```kotlin
// ✅ Simple sequential chain
WorkManager.getInstance(context)
    .beginWith(downloadWorker)
    .then(processWorker)
    .then(uploadWorker)
    .enqueue()
```

**Parallel execution**
```kotlin
// ✅ Fan-out: one worker → multiple parallel workers
WorkManager.getInstance(context)
    .beginWith(downloadWorker)
    .then(listOf(imageProcessor, videoProcessor, metadataExtractor))
    .enqueue()

// ✅ Fan-in: multiple parallel workers → one aggregator
WorkManager.getInstance(context)
    .beginWith(listOf(source1, source2, source3))
    .then(aggregatorWorker)
    .enqueue()
```

### Data Passing Between Workers

**WorkData Constraints**
- Maximum size: 10 KB
- Only primitive types and `String`/`Array`
- ❌ Don't pass large objects directly
- ✅ Pass IDs, file paths, metadata

```kotlin
class DownloadWorker : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        val fileId = inputData.getString("file_id") ?: return Result.failure()

        return try {
            val localPath = downloadFile(fileId)
            // ✅ Pass only path and metadata
            Result.success(workDataOf(
                "file_id" to fileId,
                "local_path" to localPath,
                "file_size" to getFileSize(localPath)
            ))
        } catch (e: IOException) {
            if (runAttemptCount < 3) Result.retry()
            else Result.failure(workDataOf("error" to e.message))
        }
    }
}

class ProcessWorker : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        // ✅ Read previous worker's outputData through inputData
        val localPath = inputData.getString("local_path") ?: return Result.failure()

        val processedPath = processFile(localPath)
        return Result.success(workDataOf("processed_path" to processedPath))
    }
}
```

### Error Handling

**Selective retry strategy**
```kotlin
class ReliableWorker : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        return try {
            syncData()
            Result.success()
        } catch (e: NetworkException) {
            // ✅ Network errors → retry with exponential backoff
            if (runAttemptCount < 3) Result.retry()
            else Result.success(workDataOf("partial_success" to true))
        } catch (e: AuthException) {
            // ❌ Auth errors → immediate failure
            Result.failure(workDataOf("error_type" to "auth"))
        } catch (e: ValidationException) {
            // ✅ Validation errors → continue chain
            Result.success(workDataOf(
                "partial_success" to true,
                "skipped_ids" to invalidIds.toJson()
            ))
        }
    }
}
```

**Fallback chains for critical failures**
```kotlin
// ✅ Primary chain + fallback on failure
workManager
    .beginWith(primaryChain)
    .then(fallbackWorker)  // Runs only if primary succeeds
    .then(notificationWorker)
    .enqueue()
```

### Monitoring and Observing

**Chain progress tracking**
```kotlin
class ChainMonitor(private val workManager: WorkManager) {
    fun monitorChain(chainTag: String): Flow<ChainStatus> =
        workManager.getWorkInfosByTagFlow(chainTag)
            .map { workInfos ->
                ChainStatus(
                    total = workInfos.size,
                    succeeded = workInfos.count { it.state == SUCCEEDED },
                    failed = workInfos.count { it.state == FAILED },
                    running = workInfos.count { it.state == RUNNING },
                    progress = calculateProgress(workInfos)
                )
            }

    private fun calculateProgress(workInfos: List<WorkInfo>): Int {
        val totalProgress = workInfos.sumOf { workInfo ->
            when (workInfo.state) {
                SUCCEEDED -> 100
                RUNNING -> workInfo.progress.getInt("progress", 0)
                else -> 0
            }
        }
        return if (workInfos.isNotEmpty()) totalProgress / workInfos.size else 0
    }
}
```

### Best Practices

**1. Data Passing**
- Keep WorkData < 10 KB
- Use database/files for large data
- Pass IDs instead of objects
- Serialize via JSON for collections

**2. Error Handling**
- Design for partial failures
- Different retry policies for different errors
- Pass error context downstream
- Use fallback chains for critical operations

**3. Chain Design**
- Use tags for grouping: `.addTag(batchId)`
- Minimize worker count
- Batch similar operations
- Design for observability

**4. Constraints and policies**
```kotlin
val worker = OneTimeWorkRequestBuilder<DownloadWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,
        MIN_BACKOFF_MILLIS,
        TimeUnit.MILLISECONDS
    )
    .build()
```

### Common Pitfalls

1. **Over-complex chains** — make debugging difficult
2. **Large WorkData payloads** — exceed 10 KB limit
3. **Circular dependencies** — cause deadlocks
4. **Missing error handling** — blocks entire chain
5. **No progress reporting** — poor UX

## Follow-ups

- How do you test complex WorkManager chains?
- What's the difference between `beginWith(listOf(...))` and `enqueue(listOf(...))`?
- How do you handle scenarios where one worker in a parallel group fails but others succeed?
- How do you implement conditional branching in WorkManager chains based on worker results?
- What's the performance impact of having too many workers in a chain?

## References

- [[c-workmanager]]
- [[c-coroutines]]

## Related Questions

### Prerequisites
- Basic WorkManager concepts and worker implementation
- Understanding Kotlin coroutines and `Flow` for monitoring

### Related
- WorkManager constraints and network requirements
- Periodic work scheduling patterns
- Background task scheduling strategies

### Advanced
- Custom WorkManager configuration and initialization
- Comparing background processing approaches (WorkManager vs Services vs AlarmManager)
- Testing complex work chains and dependency graphs
