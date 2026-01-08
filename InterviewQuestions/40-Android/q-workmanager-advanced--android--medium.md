---\
id: android-065
title: "WorkManager Advanced / Продвинутый WorkManager"
aliases: ["WorkManager Advanced", "Продвинутый WorkManager"]
topic: android
subtopics: [background-execution]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-background-tasks, c-android-background-execution, c-jobscheduler]
created: 2025-10-12
updated: 2025-11-10
tags: [android/background-execution, background-processing, difficulty/medium, jetpack, workmanager]
sources: ["https://developer.android.com/topic/libraries/architecture/workmanager"]
---\
# Вопрос (RU)
> Какие продвинутые возможности `WorkManager`?

# Question (EN)
> What are the advanced features of `WorkManager`?

---

## Ответ (RU)

`WorkManager` обеспечивает надежное планирование и выполнение отложенной фоновой работы (best-effort, без гарантий точного времени запуска), с поддержкой ограничений, цепочек, уникальной работы и восстановления после перезагрузок в рамках системных лимитов платформы.

**`Constraints` (Ограничения):**
Выполнение работы только при соблюдении условий для экономии батареи и трафика.

```kotlin
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED) // ✅ WiFi only
    .setRequiresBatteryNotLow(true)                // ✅ Battery check
    .build()

val uploadRequest = OneTimeWorkRequestBuilder<PhotoUploadWorker>()
    .setConstraints(constraints)
    .build()
```

**Periodic Work:**
Минимальный интервал 15 минут с гибким окном выполнения.

```kotlin
val syncRequest = PeriodicWorkRequestBuilder<DataSyncWorker>(
    repeatInterval = 24, TimeUnit.HOURS,
    flexTimeInterval = 2, TimeUnit.HOURS  // ✅ Execution window
).build()

WorkManager.getInstance(context)
    .enqueueUniquePeriodicWork(
        "daily_sync",
        ExistingPeriodicWorkPolicy.KEEP,  // ✅ Не запускать новую, если уже есть работа с этим именем
        syncRequest
    )
```

**Work Chaining:**
Последовательное/параллельное выполнение с передачей данных через InputData/OutputData.

```kotlin
// Sequential: download → process → upload
WorkManager.getInstance(context)
    .beginWith(downloadRequest)
    .then(processRequest)
    .then(uploadRequest)
    .enqueue()

// Parallel + combine
WorkManager.getInstance(context)
    .beginWith(listOf(task1, task2))  // ✅ Parallel
    .then(combineRequest)             // ✅ Waits for both
    .enqueue()
```

**ExistingWorkPolicy (Unique Work):**
Управление поведением при повторной постановке уникальной работы.

```kotlin
// REPLACE — отменить существующую цепочку и запустить новую
WorkManager.getInstance(context)
    .enqueueUniqueWork("sync", ExistingWorkPolicy.REPLACE, request)

// KEEP — сохранить существующую, игнорировать новую
WorkManager.getInstance(context)
    .enqueueUniqueWork("cleanup", ExistingWorkPolicy.KEEP, request)

// APPEND_OR_REPLACE — если существует незавершённая уникальная работа, добавить новый Work в конец цепочки;
// если вся цепочка завершилась (включая FAILURE/CANCELLED), она будет заменена новой
WorkManager.getInstance(context)
    .enqueueUniqueWork("queue", ExistingWorkPolicy.APPEND_OR_REPLACE, request)
```

(Примечание: `APPEND` устарел и заменён на `APPEND_OR_REPLACE`.)

**Persistence:**
`WorkManager` сохраняет задачи в `SQLite` и восстанавливает их после перезагрузки устройства или обновления приложения.

```kotlin
@HiltWorker
class MigrationWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val database: AppDatabase
) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result = try {
        val fromVersion = inputData.getInt("from_version", 0)
        database.migrate(fromVersion, BuildConfig.VERSION_CODE)
        Result.success()  // ✅ Успешное завершение, без повторных запусков
    } catch (e: Exception) {
        Result.retry()    // ✅ Запросить повторный запуск согласно backoff policy
    }
}
```

**Прогресс и результаты (Progress / Result / Retry):**
- `Worker` может публиковать прогресс, чтобы UI мог подписаться на обновления.
- Через `Result.success()`, `Result.failure()` и `Result.retry()` контролируется окончательный исход и повторные попытки (с backoff-стратегией).

```kotlin
// In CoroutineWorker
override suspend fun doWork(): Result {
    setProgress(workDataOf("progress" to 50, "file" to "photo.jpg"))
    // ... work ...
    return Result.success()
}

// In ViewModel
val progress = workManager.getWorkInfoByIdLiveData(workId)
    .map { it?.progress?.getInt("progress", 0) ?: 0 }
```

## Answer (EN)

`WorkManager` provides robust scheduling and execution of deferrable background work (best-effort, no guarantee of exact execution time), with support for constraints, chaining, unique work, and recovery after reboots within platform limits.

**`Constraints`:**
Execute work only when conditions are met to save battery and data.

```kotlin
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED) // ✅ WiFi only
    .setRequiresBatteryNotLow(true)                // ✅ Battery check
    .build()

val uploadRequest = OneTimeWorkRequestBuilder<PhotoUploadWorker>()
    .setConstraints(constraints)
    .build()
```

**Periodic Work:**
Minimum 15-minute interval with a flexible execution window.

```kotlin
val syncRequest = PeriodicWorkRequestBuilder<DataSyncWorker>(
    repeatInterval = 24, TimeUnit.HOURS,
    flexTimeInterval = 2, TimeUnit.HOURS  // ✅ Execution window
).build()

WorkManager.getInstance(context)
    .enqueueUniquePeriodicWork(
        "daily_sync",
        ExistingPeriodicWorkPolicy.KEEP,  // ✅ Don't start new if one with this name already exists
        syncRequest
    )
```

**Work Chaining:**
Sequential/parallel execution with data passing via InputData/OutputData.

```kotlin
// Sequential: download → process → upload
WorkManager.getInstance(context)
    .beginWith(downloadRequest)
    .then(processRequest)
    .then(uploadRequest)
    .enqueue()

// Parallel + combine
WorkManager.getInstance(context)
    .beginWith(listOf(task1, task2))  // ✅ Parallel
    .then(combineRequest)             // ✅ Waits for both
    .enqueue()
```

**ExistingWorkPolicy (Unique Work):**
Control behavior when re-enqueueing unique work.

```kotlin
// REPLACE — cancel existing chain and start a new one
WorkManager.getInstance(context)
    .enqueueUniqueWork("sync", ExistingWorkPolicy.REPLACE, request)

// KEEP — keep existing, ignore new
WorkManager.getInstance(context)
    .enqueueUniqueWork("cleanup", ExistingWorkPolicy.KEEP, request)

// APPEND_OR_REPLACE — if there is unfinished unique work, append the new request to the end of its chain;
// if the entire chain has finished (including FAILURE/CANCELLED), replace it with the new work
WorkManager.getInstance(context)
    .enqueueUniqueWork("queue", ExistingWorkPolicy.APPEND_OR_REPLACE, request)
```

(Note: `APPEND` is deprecated and replaced by `APPEND_OR_REPLACE`.)

**Persistence:**
`WorkManager` persists work in `SQLite` and restores it after device reboot or app update.

```kotlin
@HiltWorker
class MigrationWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val database: AppDatabase
) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result = try {
        val fromVersion = inputData.getInt("from_version", 0)
        database.migrate(fromVersion, BuildConfig.VERSION_CODE)
        Result.success()  // ✅ Successful completion, no further retries
    } catch (e: Exception) {
        Result.retry()    // ✅ Request retry according to the configured backoff policy
    }
}
```

**Progress and Result/Retry:**
- A `Worker` can publish progress so that UI can observe updates.
- `Result.success()`, `Result.failure()`, and `Result.retry()` control completion outcome and retries (with backoff policy).

```kotlin
// In CoroutineWorker
override suspend fun doWork(): Result {
    setProgress(workDataOf("progress" to 50, "file" to "photo.jpg"))
    // ... work ...
    return Result.success()
}

// In ViewModel
val progress = workManager.getWorkInfoByIdLiveData(workId)
    .map { it?.progress?.getInt("progress", 0) ?: 0 }
```

---

## Дополнительные Вопросы (RU)

- Как ограничения ведут себя на разных версиях Android (особенно с учетом Doze и ограничений Android 12+)?
- Каковы накладные расходы и компромиссы между цепочками работ и отдельными `Worker`-ами?
- Как обрабатывать отмену `Worker` во время отслеживания прогресса?
- Что произойдет при использовании `ExistingWorkPolicy.APPEND` с завершившимися с ошибкой задачами?
- Как тестировать периодическую работу с `flexTimeInterval` в модульных тестах?

## Follow-ups

- How do constraints behave across different Android versions (especially Android 12+ Doze restrictions)?
- What are the performance trade-offs of work chaining vs. separate Workers?
- How to handle `Worker` cancellation during progress tracking?
- What happens when `ExistingWorkPolicy.APPEND` is used with failed workers?
- How to test periodic work with `flexTimeInterval` in unit tests?

## Ссылки (RU)

- [[c-workmanager]]
- "https://developer.android.com/topic/libraries/architecture/workmanager/advanced"
- "https://developer.android.com/topic/libraries/architecture/workmanager/how-to/chain-work"

## References

- [[c-workmanager]] - `WorkManager` concepts
- "https://developer.android.com/topic/libraries/architecture/workmanager/advanced"
- "https://developer.android.com/topic/libraries/architecture/workmanager/how-to/chain-work"

## Связанные Вопросы (RU)

### Предварительные (проще)
- [[q-android-app-components--android--easy]] - Обзор компонентов приложения

### Связанные (такой Же уровень)
- [[q-workmanager-vs-alternatives--android--medium]] - `WorkManager` и альтернативы
- [[q-workmanager-return-result--android--medium]] - Возврат результатов из `Worker`-ов

### Продвинутые (сложнее)
- [[q-android-runtime-internals--android--hard]] - Внутреннее устройство Android Runtime

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components overview

### Related (Same Level)
- [[q-workmanager-vs-alternatives--android--medium]] - `WorkManager` vs alternatives
- [[q-workmanager-return-result--android--medium]] - Returning results from Workers

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] - Android runtime internals
