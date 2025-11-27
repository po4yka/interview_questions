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
related: [c-coroutines, q-android-async-primitives--android--easy]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android, android/background-execution, android/coroutines, background, difficulty/hard, workmanager]

date created: Saturday, November 1st 2025, 12:47:12 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
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
val downloadRequest = OneTimeWorkRequestBuilder<DownloadWorker>().build()
val processRequest = OneTimeWorkRequestBuilder<ProcessWorker>().build()
val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>().build()

WorkManager.getInstance(context)
    .beginWith(downloadRequest)
    .then(processRequest)
    .then(uploadRequest)
    .enqueue()
```

**Параллельное выполнение**
```kotlin
// ✅ Fan-out: один воркер → несколько параллельных
val downloadRequest = OneTimeWorkRequestBuilder<DownloadWorker>().build()
val imageProcessor = OneTimeWorkRequestBuilder<ImageProcessorWorker>().build()
val videoProcessor = OneTimeWorkRequestBuilder<VideoProcessorWorker>().build()
val metadataExtractor = OneTimeWorkRequestBuilder<MetadataExtractorWorker>().build()

WorkManager.getInstance(context)
    .beginWith(downloadRequest)
    .then(listOf(imageProcessor, videoProcessor, metadataExtractor))
    .enqueue()

// ✅ Fan-in: несколько параллельных → один агрегатор
val source1 = OneTimeWorkRequestBuilder<Source1Worker>().build()
val source2 = OneTimeWorkRequestBuilder<Source2Worker>().build()
val source3 = OneTimeWorkRequestBuilder<Source3Worker>().build()
val aggregatorWorker = OneTimeWorkRequestBuilder<AggregatorWorker>().build()

WorkManager.getInstance(context)
    .beginWith(listOf(source1, source2, source3))
    .then(aggregatorWorker)
    .enqueue()
```

### Передача Данных Между Воркерами

**Ограничения WorkData**
- Практический лимит ~10 KB на `Data` (input/output), хранится в БД WorkManager
- Только примитивные типы и `String`/Array
- ❌ Не передавать большие объекты напрямую
- ✅ Передавать ID, пути к файлам, метаданные

```kotlin
class DownloadWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) {
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
            else Result.failure(workDataOf("error" to (e.message ?: "io_error")))
        }
    }
}

class ProcessWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) {
    override suspend fun doWork(): Result {
        // ✅ Читаем outputData предыдущего воркера через inputData
        val localPath = inputData.getString("local_path") ?: return Result.failure()

        val processedPath = processFile(localPath)
        return Result.success(workDataOf("processed_path" to processedPath))
    }
}
```

### Обработка Ошибок

**Селективная retry-стратегия (псевдокод, доменные классы исключений условные)**
```kotlin
class ReliableWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) {
    override suspend fun doWork(): Result {
        return try {
            syncData()
            Result.success()
        } catch (e: NetworkException) { // domain-specific
            // ✅ Сетевые ошибки → retry с экспоненциальной задержкой (см. BackoffCriteria)
            if (runAttemptCount < 3) Result.retry()
            else {
                // В реальных сценариях чаще отдаём failure; здесь показан вариант частичного успеха
                Result.success(workDataOf("partial_success" to true))
            }
        } catch (e: AuthException) { // domain-specific
            // ❌ Ошибки авторизации → немедленный failure
            Result.failure(workDataOf("error_type" to "auth"))
        } catch (e: ValidationException) { // domain-specific
            // ✅ Ошибки валидации → можно продолжить цепь с пометкой (псевдокод invalidIds)
            val skippedIdsJson = invalidIds.toJson() // псевдокод сериализации
            Result.success(workDataOf(
                "partial_success" to true,
                "skipped_ids" to skippedIdsJson
            ))
        }
    }
}
```

**Fallback-цепи для критических сбоев**

WorkManager не поддерживает условные ветки напрямую. Важно:
- если воркер возвращает `Result.failure()`, следующие по цепочке воркеры не будут выполнены;
- fallback обычно реализуется через:
  - анализ `WorkInfo` и постановку альтернативной задачи из приложения, или
  - моделирование «fallback» в рамках success-результата с контекстом ошибки в `outputData` и логикой в следующем воркере.

```kotlin
// ✅ Пример: fallback-воркер читает контекст из outputData и решает, что делать
class PrimaryWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) {
    override suspend fun doWork(): Result {
        return try {
            doPrimary()
            Result.success()
        } catch (e: Exception) {
            // Моделируем soft-failure как success с флагом и сообщением,
            // чтобы цепочка продолжилась до FallbackWorker
            Result.success(workDataOf(
                "primary_error" to (e.message ?: "error"),
                "should_fallback" to true
            ))
        }
    }
}

class FallbackWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) {
    override suspend fun doWork(): Result {
        val shouldFallback = inputData.getBoolean("should_fallback", false)
        val error = inputData.getString("primary_error")
        if (shouldFallback && error != null) {
            performFallback(error)
        }
        return Result.success()
    }
}

val primary = OneTimeWorkRequestBuilder<PrimaryWorker>().build()
val fallback = OneTimeWorkRequestBuilder<FallbackWorker>().build()

WorkManager.getInstance(context)
    .beginWith(primary)
    .then(fallback) // fallback анализирует контекст и выполняется только логически при soft-failure
    .enqueue()
```

### Мониторинг И Наблюдение

**Отслеживание прогресса цепи**

Ниже используется псевдо-обертка над стандартными API WorkManager; `getWorkInfosByTagFlow` иллюстрирует идею и может быть реализован, например, через `getWorkInfosByTagLiveData().asFlow()`.

```kotlin
class ChainMonitor(private val workManager: WorkManager) {
    fun monitorChain(chainTag: String): Flow<ChainStatus> =
        getWorkInfosByTagFlow(chainTag)
            .map { workInfos ->
                ChainStatus(
                    total = workInfos.size,
                    succeeded = workInfos.count { it.state == WorkInfo.State.SUCCEEDED },
                    failed = workInfos.count { it.state == WorkInfo.State.FAILED },
                    running = workInfos.count { it.state == WorkInfo.State.RUNNING },
                    progress = calculateProgress(workInfos)
                )
            }

    // Реализация getWorkInfosByTagFlow зависит от инфраструктуры проекта (LiveData.asFlow и т.п.)

    private fun calculateProgress(workInfos: List<WorkInfo>): Int {
        val totalProgress = workInfos.sumOf { workInfo ->
            when (workInfo.state) {
                WorkInfo.State.SUCCEEDED -> 100
                WorkInfo.State.RUNNING -> workInfo.progress.getInt("progress", 0)
                else -> 0
            }
        }
        return if (workInfos.isNotEmpty()) totalProgress / workInfos.size else 0
    }
}
```

### Лучшие Практики

**1. Передача данных**
- Держите WorkData ≲ 10 KB (включая output)
- Используйте БД/файлы для больших данных
- Передавайте ID вместо объектов
- Сериализуйте через JSON для коллекций

**2. Обработка ошибок**
- Проектируйте для частичных сбоев
- Задавайте разные retry-политики для разных типов ошибок
- Передавайте контекст ошибки downstream при необходимости
- Fallback/альтернативные ветки реализуйте через анализ состояния/данных или моделирование soft-failure, а не через ожидание встроенной условной логики цепей

**3. Дизайн цепи**
- Используйте теги для группировки: `.addTag(batchId)`
- Минимизируйте количество воркеров, группируйте похожие операции
- Проектируйте для наблюдаемости (логи, прогресс, теги)
- Используйте `beginUniqueWork` / `enqueueUniqueWork` и `ExistingWorkPolicy` для управления уникальными цепочками и повторными постановками

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
        OneTimeWorkRequest.MIN_BACKOFF_MILLIS,
        TimeUnit.MILLISECONDS
    )
    .build()
```

### Частые Ошибки

1. **Слишком сложные цепи** — усложняют отладку
2. **Большие объемы в WorkData** — приближаются или превышают лимит
3. **Циклические зависимости** — недопустимы, приводят к некорректному графу
4. **Отсутствие обработки ошибок** — может блокировать или скрывать состояние цепи
5. **Нет reporting прогресса** — плохой UX для долгих задач

## Answer (EN)

[[c-workmanager|WorkManager]] provides powerful chaining capabilities for building complex work execution graphs with dependencies, parallel execution, and sophisticated error handling strategies.

### Basic Chaining Patterns

**Sequential execution**
```kotlin
// ✅ Simple sequential chain
val downloadRequest = OneTimeWorkRequestBuilder<DownloadWorker>().build()
val processRequest = OneTimeWorkRequestBuilder<ProcessWorker>().build()
val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>().build()

WorkManager.getInstance(context)
    .beginWith(downloadRequest)
    .then(processRequest)
    .then(uploadRequest)
    .enqueue()
```

**Parallel execution**
```kotlin
// ✅ Fan-out: one worker → multiple parallel workers
val downloadRequest = OneTimeWorkRequestBuilder<DownloadWorker>().build()
val imageProcessor = OneTimeWorkRequestBuilder<ImageProcessorWorker>().build()
val videoProcessor = OneTimeWorkRequestBuilder<VideoProcessorWorker>().build()
val metadataExtractor = OneTimeWorkRequestBuilder<MetadataExtractorWorker>().build()

WorkManager.getInstance(context)
    .beginWith(downloadRequest)
    .then(listOf(imageProcessor, videoProcessor, metadataExtractor))
    .enqueue()

// ✅ Fan-in: multiple parallel workers → one aggregator
val source1 = OneTimeWorkRequestBuilder<Source1Worker>().build()
val source2 = OneTimeWorkRequestBuilder<Source2Worker>().build()
val source3 = OneTimeWorkRequestBuilder<Source3Worker>().build()
val aggregatorWorker = OneTimeWorkRequestBuilder<AggregatorWorker>().build()

WorkManager.getInstance(context)
    .beginWith(listOf(source1, source2, source3))
    .then(aggregatorWorker)
    .enqueue()
```

### Data Passing Between Workers

**WorkData constraints**
- Practical limit is ~10 KB for `Data` (input/output), stored in WorkManager DB
- Only primitive types and `String`/Array are supported
- ❌ Don't pass large objects directly
- ✅ Pass IDs, file paths, metadata

```kotlin
class DownloadWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) {
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
            else Result.failure(workDataOf("error" to (e.message ?: "io_error")))
        }
    }
}

class ProcessWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) {
    override suspend fun doWork(): Result {
        // ✅ Read previous worker's outputData through inputData
        val localPath = inputData.getString("local_path") ?: return Result.failure()

        val processedPath = processFile(localPath)
        return Result.success(workDataOf("processed_path" to processedPath))
    }
}
```

### Error Handling

**Selective retry strategy (pseudo-code with domain-specific exceptions)**
```kotlin
class ReliableWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) {
    override suspend fun doWork(): Result {
        return try {
            syncData()
            Result.success()
        } catch (e: NetworkException) { // domain-specific
            // ✅ Network errors → retry with exponential backoff (see BackoffCriteria)
            if (runAttemptCount < 3) Result.retry()
            else {
                // In many real cases you'd return failure; this illustrates partial success handling
                Result.success(workDataOf("partial_success" to true))
            }
        } catch (e: AuthException) { // domain-specific
            // ❌ Auth errors → immediate failure
            Result.failure(workDataOf("error_type" to "auth"))
        } catch (e: ValidationException) { // domain-specific
            // ✅ Validation errors → continue chain with context (pseudo-code invalidIds)
            val skippedIdsJson = invalidIds.toJson() // serialization pseudo-code
            Result.success(workDataOf(
                "partial_success" to true,
                "skipped_ids" to skippedIdsJson
            ))
        }
    }
}
```

**Fallback chains for critical failures**

WorkManager does not support conditional branches natively inside chains. Important points:
- when a worker returns `Result.failure()`, subsequent chained workers are not executed;
- typical fallback patterns:
  - observe `WorkInfo` in app code and enqueue alternative work when a chain/worker fails;
  - model a "fallback" as a soft failure: encode error context in `outputData` of a successful result and let the next worker decide.

```kotlin
// ✅ Example: fallback worker reads context from outputData and decides what to do
class PrimaryWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) {
    override suspend fun doWork(): Result {
        return try {
            doPrimary()
            Result.success()
        } catch (e: Exception) {
            // Model soft-failure as success with flags so that chain continues to FallbackWorker
            Result.success(workDataOf(
                "primary_error" to (e.message ?: "error"),
                "should_fallback" to true
            ))
        }
    }
}

class FallbackWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) {
    override suspend fun doWork(): Result {
        val shouldFallback = inputData.getBoolean("should_fallback", false)
        val error = inputData.getString("primary_error")
        if (shouldFallback && error != null) {
            performFallback(error)
        }
        return Result.success()
    }
}

val primary = OneTimeWorkRequestBuilder<PrimaryWorker>().build()
val fallback = OneTimeWorkRequestBuilder<FallbackWorker>().build()

WorkManager.getInstance(context)
    .beginWith(primary)
    .then(fallback) // fallback decides based on context; no implicit run-after-failure
    .enqueue()
```

### Monitoring and Observing

**Chain progress tracking**

The following uses a pseudo-wrapper over standard WorkManager APIs; `getWorkInfosByTagFlow` is illustrative and could be implemented via `getWorkInfosByTagLiveData().asFlow()` or similar.

```kotlin
class ChainMonitor(private val workManager: WorkManager) {
    fun monitorChain(chainTag: String): Flow<ChainStatus> =
        getWorkInfosByTagFlow(chainTag)
            .map { workInfos ->
                ChainStatus(
                    total = workInfos.size,
                    succeeded = workInfos.count { it.state == WorkInfo.State.SUCCEEDED },
                    failed = workInfos.count { it.state == WorkInfo.State.FAILED },
                    running = workInfos.count { it.state == WorkInfo.State.RUNNING },
                    progress = calculateProgress(workInfos)
                )
            }

    // Implementation of getWorkInfosByTagFlow depends on your project stack (e.g., LiveData.asFlow)

    private fun calculateProgress(workInfos: List<WorkInfo>): Int {
        val totalProgress = workInfos.sumOf { workInfo ->
            when (workInfo.state) {
                WorkInfo.State.SUCCEEDED -> 100
                WorkInfo.State.RUNNING -> workInfo.progress.getInt("progress", 0)
                else -> 0
            }
        }
        return if (workInfos.isNotEmpty()) totalProgress / workInfos.size else 0
    }
}
```

### Best Practices

**1. Data Passing**
- Keep WorkData ≲ 10 KB (including outputs)
- Use database/files for large data
- Pass IDs instead of objects
- Use JSON or similar serialization for collections

**2. Error Handling**
- Design for partial failures where appropriate
- Apply different retry policies for different error types
- Pass error context downstream when needed
- Implement fallback/alternative flows via state inspection or soft-failure modeling, not by assuming built-in conditional branches in chains

**3. Chain Design**
- Use tags for grouping: `.addTag(batchId)`
- Minimize number of workers; batch similar operations
- Design for observability (logs, progress, tags)
- Use `beginUniqueWork` / `enqueueUniqueWork` with `ExistingWorkPolicy` to control unique chains and restarts

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
        OneTimeWorkRequest.MIN_BACKOFF_MILLIS,
        TimeUnit.MILLISECONDS
    )
    .build()
```

### Common Pitfalls

1. **Over-complex chains** — make debugging difficult
2. **Large WorkData payloads** — approach or exceed practical limits
3. **Circular dependencies** — invalid graphs / non-executable chains
4. **Missing error handling** — may block or obscure overall chain state
5. **No progress reporting** — poor UX for long-running tasks

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
