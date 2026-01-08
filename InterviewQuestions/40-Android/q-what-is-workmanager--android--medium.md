---\
id: android-226
title: "What Is Workmanager / Что такое WorkManager"
aliases: ["What Is WorkManager", "Что такое WorkManager"]
topic: android
subtopics: [background-execution, coroutines]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
sources: []
status: draft
moc: moc-android
related: [c-background-tasks, c-coroutines, c-workmanager]
created: 2025-10-15
updated: 2025-11-10
tags: [android/background-execution, android/coroutines, difficulty/medium, jetpack, scheduled-tasks, workmanager]
---\
# Вопрос (RU)
> Что такое `WorkManager` и когда его следует использовать?

# Question (EN)
> What is `WorkManager` and when should it be used?

## Ответ (RU)

**`WorkManager`** — это Jetpack библиотека для **отложенных (deferrable) и надёжных фоновых задач**, которые должны быть **гарантированно поставлены в очередь и предприняты для выполнения** даже при закрытии приложения или перезагрузке устройства, с учётом системных ограничений (Doze, оптимизация батареи). Это не абсолютная гарантия выполнения (работа может не выполниться, если, например, приложение удалено или условия так и не выполнены), но максимально приближенная в рамках платформы.

### Ключевые Особенности

**Надёжное выполнение**: задачи сохраняются в `SQLite` БД и автоматически пере-планируются после перезапуска процесса или устройства, когда выполняются заданные условия.

**Умный выбор механизма**: под капотом выбирает подходящий планировщик в зависимости от версии Android и ограничений (например, JobScheduler на новых версиях), абстрагируя детали реализации.

**Ограничения выполнения**: декларативно задаются условия — сеть, зарядка, уровень батареи, свободное место.

**Цепочки работ**: последовательное и параллельное выполнение с передачей данных между задачами.

**Интеграция с корутинами**: `CoroutineWorker` для suspend-функций без блокировки потоков.

**Уважение системных ограничений**: `WorkManager` предназначен для отложенных задач и может значительно откладывать выполнение, объединяя работы в батчи, чтобы соответствовать Doze и политикам энергосбережения.

### Основные Компоненты

```kotlin
// 1. Worker — определяет задачу
class UploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        try {
            val path = inputData.getString("file_path") ?: return@withContext Result.failure()
            uploadFile(path)
            Result.success() // ✅ задача завершена
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry() // ✅ повторить с экспоненциальной задержкой (интервалы контролирует система и WorkManager)
            } else {
                Result.failure() // ❌ окончательный провал
            }
        }
    }
}

// 2. WorkRequest — описывает когда и как запустить
val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setInputData(workDataOf("file_path" to "/path/to/file"))
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED) // ✅ только при наличии сети
            .setRequiresBatteryNotLow(true)                // ✅ только когда батарея не в состоянии "низкий заряд" (порог задаётся системой)
            .build()
    )
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,
        15, TimeUnit.SECONDS // ✅ начальная задержка; реальные интервалы могут быть увеличены и минимумы навязаны системой/WorkManager
    )
    .build()

// 3. WorkManager — управляет выполнением
WorkManager.getInstance(context).enqueue(uploadRequest)
```

### Цепочки Работ

```kotlin
// Последовательно-параллельное выполнение
WorkManager.getInstance(context)
    .beginWith(compressWork)                    // Шаг 1: сжатие
    .then(listOf(uploadWork1, uploadWork2))     // Шаг 2: параллельные загрузки
    .then(cleanupWork)                          // Шаг 3: очистка
    .enqueue()
```

### Мониторинг Выполнения

```kotlin
WorkManager.getInstance(context)
    .getWorkInfoByIdLiveData(uploadRequest.id)
    .observe(lifecycleOwner) { workInfo ->
        when (workInfo.state) {
            WorkInfo.State.RUNNING -> {
                val progress = workInfo.progress.getInt("progress", 0)
                updateProgressBar(progress) // ✅ отображаем прогресс
            }
            WorkInfo.State.SUCCEEDED -> {
                val url = workInfo.outputData.getString("uploaded_url")
                showSuccess(url) // ✅ задача выполнена
            }
            WorkInfo.State.FAILED -> {
                val error = workInfo.outputData.getString("error")
                showError(error) // ❌ задача провалилась
            }
            else -> {}
        }
    }
```

### Когда Использовать

**Используйте `WorkManager`**:
- Загрузка файлов, которые должны быть надёжно поставлены в очередь и завершены при выполнении условий
- Синхронизация данных с сервером
- Отправка аналитики/логов
- Очистка кэша/старых данных
- Обработка изображений
- Периодические задачи (минимальный интервал ~15 минут, фактическое время запуска может быть отложено системой)

**Не используйте `WorkManager`**:
- Жёстко точное время выполнения (используйте AlarmManager или специализированные механизмы планирования)
- Задачи, требующие немедленного и непрерывного выполнения в реальном времени (используйте foreground service / bound service)
- Немедленные UI-обновления (используйте корутины, `ViewModel`, др. механизмы на основном потоке)

Если вам нужен как гарантированный план/ретраи, так и выполнение в переднем плане (например, видимая пользователю долгая загрузка), используйте `WorkManager` с `setForeground()` внутри `ListenableWorker`/`CoroutineWorker` вместо ручного управления службой.

### Дополнительные Вопросы (RU)

- Как `WorkManager` обрабатывает ограничения Doze и оптимизации батареи?
- В чем разница между `Worker`, `CoroutineWorker` и `RxWorker`?
- Как реализовать отслеживание прогресса для длительных задач `WorkManager`?
- Какие политики доступны для обработки дублирующейся работы с `enqueueUniqueWork`?
- Как работает механизм экспоненциального бэкофф-ретрая `WorkManager` и как его настроить?

### Ссылки (RU)

- [[c-coroutines]] — Интеграция `WorkManager` с Kotlin coroutines через `CoroutineWorker`
- [[c-background-tasks]] — Обзор вариантов фонового выполнения в Android
- [Документация WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager) — Официальное руководство
- [WorkManager Basics](https://medium.com/androiddevelopers/workmanager-basics-beba51e94048) — Вводная статья

### Связанные Вопросы (RU)

#### База (проще)
- [[q-android-service-types--android--easy]] — Понимание типов и назначения Android `Service`
- [[q-android-async-primitives--android--easy]] — Базовые асинхронные примитивы в Android

#### Связанные (средний уровень)
- [[q-foreground-service-types--android--medium]] — Длительная видимая фоновая работа через foreground service
- [[q-android-architectural-patterns--android--medium]] — Архитектурные подходы и место фоновых задач

#### Продвинутые (сложнее)
- [[q-android14-permissions--android--medium]] — Новые ограничения и влияние на фоновую работу
- [[q-android-app-lag-analysis--android--medium]] — Анализ лагов и влияние фоновых задач на производительность

## Answer (EN)

**`WorkManager`** is a Jetpack library for **deferrable and reliable background work** that should be **persistently enqueued and best-effort guaranteed to run** even if the app exits or the device restarts, while respecting system constraints (Doze, battery optimizations). It is not an absolute guarantee (e.g., work will not run if the app is uninstalled or constraints are never met), but it is the most robust option within platform limits.

### Key Features

**Reliable execution**: tasks are persisted in an internal `SQLite` database and automatically rescheduled after process death or device reboot when constraints are met.

**Smart mechanism selection**: under the hood chooses an appropriate scheduler based on Android version and constraints (e.g., JobScheduler on newer APIs), hiding implementation details.

**Execution constraints**: declaratively specify conditions — network, charging, battery state, storage space.

**Work chaining**: sequential and parallel execution with data passing between tasks.

**Coroutines integration**: `CoroutineWorker` for suspend functions without blocking threads.

**Respects system limits**: designed for deferrable work and may significantly delay execution or batch work to comply with Doze and power-saving policies.

### Core Components

```kotlin
// 1. Worker — defines the task
class UploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        try {
            val path = inputData.getString("file_path") ?: return@withContext Result.failure()
            uploadFile(path)
            Result.success() // ✅ task completed
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry() // ✅ retry with exponential backoff (actual intervals are managed by WorkManager and the system)
            } else {
                Result.failure() // ❌ final failure
            }
        }
    }
}

// 2. WorkRequest — describes when and how to run
val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setInputData(workDataOf("file_path" to "/path/to/file"))
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED) // ✅ only when network is available
            .setRequiresBatteryNotLow(true)                // ✅ only when battery is not in "low" state (threshold defined by system)
            .build()
    )
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,
        15, TimeUnit.SECONDS // ✅ initial delay; real retry times may be clamped/extended by WorkManager and the OS
    )
    .build()

// 3. WorkManager — manages execution
WorkManager.getInstance(context).enqueue(uploadRequest)
```

### Work Chaining

```kotlin
// Sequential-parallel execution
WorkManager.getInstance(context)
    .beginWith(compressWork)                    // Step 1: compression
    .then(listOf(uploadWork1, uploadWork2))     // Step 2: parallel uploads
    .then(cleanupWork)                          // Step 3: cleanup
    .enqueue()
```

### Monitoring Execution

```kotlin
WorkManager.getInstance(context)
    .getWorkInfoByIdLiveData(uploadRequest.id)
    .observe(lifecycleOwner) { workInfo ->
        when (workInfo.state) {
            WorkInfo.State.RUNNING -> {
                val progress = workInfo.progress.getInt("progress", 0)
                updateProgressBar(progress) // ✅ display progress
            }
            WorkInfo.State.SUCCEEDED -> {
                val url = workInfo.outputData.getString("uploaded_url")
                showSuccess(url) // ✅ task completed
            }
            WorkInfo.State.FAILED -> {
                val error = workInfo.outputData.getString("error")
                showError(error) // ❌ task failed
            }
            else -> {}
        }
    }
```

### When to Use

**Use `WorkManager` for**:
- File uploads that must be reliably enqueued and completed when constraints are met
- Data synchronization with server
- Sending analytics/logs
- Cache cleanup/old data deletion
- Image processing
- Periodic tasks (minimum interval ~15 minutes; actual runs may be batched/delayed by the system)

**Don't use `WorkManager` for**:
- Strictly exact timing (use AlarmManager or other precise scheduling mechanisms)
- Tasks requiring immediate, continuous, real-time/low-latency execution (use a foreground service / bound service)
- Immediate UI updates (use coroutines, `ViewModel`, and main-thread mechanisms)

If you need both robust scheduling/retries and foreground execution (e.g., user-visible long-running upload), use `WorkManager` with `setForeground()` inside your `ListenableWorker`/`CoroutineWorker` instead of manually managing a service.

## Follow-ups

- How does `WorkManager` handle battery optimization and Doze mode constraints?
- What is the difference between `Worker`, `CoroutineWorker`, and `RxWorker`?
- How do you implement progress tracking for long-running `WorkManager` tasks?
- What policies exist for handling duplicate work with `enqueueUniqueWork`?
- How does `WorkManager`'s exponential backoff retry mechanism work and how can it be customized?

## References

- [[c-coroutines]] — `WorkManager` integrates with Kotlin coroutines via `CoroutineWorker`
- [[c-background-tasks]] — Overview of Android background execution options
- [WorkManager Documentation](https://developer.android.com/topic/libraries/architecture/workmanager) — Official Android guide
- [WorkManager Basics](https://medium.com/androiddevelopers/workmanager-basics-beba51e94048) — Introduction article

## Related Questions

### Prerequisites (Easier)
- [[q-android-service-types--android--easy]] — Understanding Android `Service` lifecycle
- [[q-android-async-primitives--android--easy]] — Basic async primitives on Android

### Related (Same Level)
- [[q-foreground-service-types--android--medium]] — `Long`-running visible background work using foreground services
- [[q-android-architectural-patterns--android--medium]] — Architectural approaches and where background work fits

### Advanced (Harder)
- [[q-android14-permissions--android--medium]] — New restrictions and their impact on background work
- [[q-android-app-lag-analysis--android--medium]] — Lag analysis and impact of background work on performance
