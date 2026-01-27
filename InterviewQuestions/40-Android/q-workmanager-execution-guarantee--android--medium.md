---
id: android-234
title: WorkManager Execution Guarantee / Гарантия выполнения WorkManager
aliases:
- WorkManager Execution Guarantee
- Гарантия выполнения WorkManager
topic: android
subtopics:
- background-execution
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-background-tasks
- q-background-tasks-decision-guide--android--medium
- q-background-vs-foreground-service--android--medium
- q-service-restrictions-why--android--medium
created: 2025-10-15
updated: 2025-11-10
sources:
- https://developer.android.com/topic/libraries/architecture/workmanager
- https://developer.android.com/topic/libraries/architecture/workmanager/advanced
tags:
- android/background-execution
- background-tasks
- difficulty/medium
- reliability
- workmanager
anki_cards:
- slug: android-234-0-en
  language: en
- slug: android-234-0-ru
  language: ru
---
# Вопрос (RU)

> Как `WorkManager` гарантирует выполнение задач?

# Question (EN)

> How does `WorkManager` guarantee task execution?

## Ответ (RU)

`WorkManager` предоставляет надежный, максимально возможный (best-effort) запуск отложенных фоновых задач, устойчивый к перезапускам, за счет трех ключевых механизмов: персистентного хранилища (`SQLite`), мониторинга системных ограничений и адаптивной интеграции с системными API планирования (в т.ч. JobScheduler на API 23+ и AlarmManager на старых версиях). Это не абсолютная гарантия против всех сценариев (force stop, удаление приложения, factory reset, жесткие OEM-ограничения), но один из самых надежных официальных механизмов.

См. также [[c-background-tasks]].

### Ключевые Гарантии (в Рамках Ограничений ОС)

1. **Персистентность** — все запросы работы сохраняются в `SQLite` и переживают перезапуски приложения/устройства
2. **Constraint-based выполнение** — работа запускается только при выполнении всех условий (сеть, батарея, хранилище)
3. **Автоматический retry** — поддержка повторных попыток с backoff (линейным или экспоненциальным) до установленного лимита
4. **Упорядоченность** — цепочки работ соблюдают последовательность выполнения (следующая работа не начнется, пока предыдущая не завершится успешно, если не указано иное)
5. **Фоновое выполнение** — `doWork()` выполняется не в UI-потоке (но разработчик не должен выполнять UI-операции из `Worker`)

### Механизмы Гарантии

#### 1. Персистентное Хранилище

```kotlin
val workRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setInputData(workDataOf("file_path" to "/path/to/file"))
    .build()

WorkManager.getInstance(context).enqueue(workRequest)
// ✅ Даже если приложение упадет или будет перезапущено, работа сохранена в БД
```

Внутри `SQLite` хранятся: параметры `Worker`, constraints, счетчик попыток, статус, output data. Это позволяет `WorkManager` восстановить состояние и продолжить планирование.

#### 2. Системная Интеграция

`WorkManager` автоматически выбирает подходящий механизм выполнения в зависимости от версии платформы и доступных API (например, JobScheduler на современных версиях и комбинацию AlarmManager/`BroadcastReceiver` на старых). Конкретный выбор является деталью реализации библиотеки и может эволюционировать.

#### 3. Constraint-based Выполнение

```kotlin
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED) // ✅ Только с сетью
    .setRequiresBatteryNotLow(true)                // ✅ Батарея не низкая
    .build()

val workRequest = OneTimeWorkRequestBuilder<SyncWorker>()
    .setConstraints(constraints)
    .build()
```

`WorkManager` мониторит системное состояние и запускает работу только при выполнении всех заданных constraints. Если условия пропадают во время выполнения, работа может быть остановлена и пере-запланирована.

#### 4. Автоматический Retry С Backoff

```kotlin
class RetryableWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) {
    override suspend fun doWork(): Result {
        return try {
            uploadData()
            Result.success()
        } catch (e: IOException) {
            // ✅ Временная ошибка — запрашиваем повтор
            if (runAttemptCount < 5) Result.retry() else Result.failure()
        } catch (e: Exception) {
            // ❌ Фатальная ошибка — помечаем как провал
            Result.failure()
        }
    }
}

val workRequest = OneTimeWorkRequestBuilder<RetryableWorker>()
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,
        Duration.ofSeconds(10)
    )
    .build()
```

**Экспоненциальный backoff** начинается не раньше минимального интервала (по умолчанию ≥ 10 секунд) и увеличивается (10s → 20s → 40s → 80s → ...), но ограничен максимальным интервалом (по умолчанию около 5 часов). Точные моменты запуска контролируются системой.

#### 5. Уникальность Работы

```kotlin
// ✅ KEEP — игнорировать новый запрос, если работа с таким именем уже есть
WorkManager.getInstance(context).enqueueUniqueWork(
    "sync_work",
    ExistingWorkPolicy.KEEP,
    workRequest
)

// ✅ REPLACE — отменить старую, запустить новую
WorkManager.getInstance(context).enqueueUniqueWork(
    "sync_work",
    ExistingWorkPolicy.REPLACE,
    workRequest
)
```

Уникальные работы и цепочки позволяют избежать дублирования и более детерминированно управлять выполнением, повышая надежность поведения.

### Обработка Перезагрузки

После перезагрузки устройства `WorkManager` восстанавливает незавершенные работы из своей БД и продолжает планирование в соответствии с их статусами и constraints (механизмы доставки событий перезагрузки являются деталью реализации и могут отличаться между версиями библиотеки).

### Expedited Work

Для срочных задач `WorkManager` поддерживает "expedited work" — приоритетное выполнение с использованием foreground service-подхода под капотом, в рамках квот платформы. Если квота исчерпана, запрос может быть выполнен как обычная (non-expedited) работа в соответствии с выбранной политикой.

```kotlin
class ExpeditedWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) {
    override suspend fun getForegroundInfo(): ForegroundInfo {
        return ForegroundInfo(NOTIFICATION_ID, createNotification())
    }

    override suspend fun doWork(): Result {
        setForeground(getForegroundInfo()) // ✅ Переводим в foreground для expedited work при необходимости
        return try {
            processUrgentData()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

val expeditedRequest = OneTimeWorkRequestBuilder<ExpeditedWorker>()
    .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
    .build()
```

### Резюме

`WorkManager` обеспечивает высокую надежность выполнения отложенных задач за счет:
- Немедленного сохранения в `SQLite` при enqueue
- Автоматического выбора системных механизмов планирования (JobScheduler и др.)
- Строгого учета constraints
- Backoff-стратегий для повторных попыток
- Восстановления задач после перезагрузки устройства
- Поддержки expedited work / интеграции с foreground service-подходом для срочных задач

**Ограничения**:
- Периодические работы не гарантируют точное время выполнения (минимум 15 минут), возможны сдвиги.
- Doze Mode, App Standby, ограничения OEM, force stop, удаление приложения или очистка данных могут помешать выполнению.

## Answer (EN)

`WorkManager` provides a resilient, best-effort execution of deferrable background work that needs guaranteed scheduling and persistence, using three core mechanisms: persistent storage (`SQLite`), system constraint monitoring, and adaptive integration with platform scheduling APIs (including JobScheduler on API 23+ and AlarmManager on older versions). It is not an absolute guarantee against all scenarios (force stop, app uninstall, factory reset, aggressive OEM kills), but it is the recommended reliable solution within platform constraints.

See also [[c-background-tasks]].

### Key Guarantees (Within OS Constraints)

1. **Persistence** — all work requests are stored in `SQLite` and survive app/process/device restarts
2. **Constraint-based execution** — work runs only when all specified conditions are met (network, battery, storage, etc.)
3. **Automatic retry** — supports retries with linear or exponential backoff up to configured limits
4. **Ordering** — work chains preserve execution order (next work runs only after the prerequisite succeeds, unless configured otherwise)
5. **Background execution** — `doWork()` is invoked off the main thread (your `Worker` must not perform UI operations directly)

### Guarantee Mechanisms

#### 1. Persistent Storage

```kotlin
val workRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setInputData(workDataOf("file_path" to "/path/to/file"))
    .build()

WorkManager.getInstance(context).enqueue(workRequest)
// ✅ Even if the app crashes or restarts, the work is persisted in the DB
```

`SQLite` stores: `Worker` parameters, constraints, run attempt count, status, and output data. This allows `WorkManager` to restore state and continue scheduling.

#### 2. System Integration

`WorkManager` automatically selects appropriate scheduling mechanisms based on API level and capabilities (e.g., JobScheduler on modern devices and combinations of AlarmManager/`BroadcastReceiver` on older ones). The exact choice is an implementation detail of the library and may evolve.

#### 3. Constraint-based Execution

```kotlin
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED) // ✅ Only with network
    .setRequiresBatteryNotLow(true)                // ✅ Battery not low
    .build()

val workRequest = OneTimeWorkRequestBuilder<SyncWorker>()
    .setConstraints(constraints)
    .build()
```

`WorkManager` tracks system state and runs work only when all constraints are satisfied. If constraints are no longer met while running, the work may be stopped and rescheduled.

#### 4. Automatic Retry with Backoff

```kotlin
class RetryableWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) {
    override suspend fun doWork(): Result {
        return try {
            uploadData()
            Result.success()
        } catch (e: IOException) {
            // ✅ Transient error — request retry
            if (runAttemptCount < 5) Result.retry() else Result.failure()
        } catch (e: Exception) {
            // ❌ Fatal error — fail permanently
            Result.failure()
        }
    }
}

val workRequest = OneTimeWorkRequestBuilder<RetryableWorker>()
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,
        Duration.ofSeconds(10)
    )
    .build()
```

**Exponential backoff** starts at or above the minimum delay (default ≥ 10 seconds) and doubles (10s → 20s → 40s → 80s → ...), capped at a maximum delay (default around 5 hours). Exact execution times remain under system control.

#### 5. Work Uniqueness

```kotlin
// ✅ KEEP — ignore new request if existing work with the same name is enqueued
WorkManager.getInstance(context).enqueueUniqueWork(
    "sync_work",
    ExistingWorkPolicy.KEEP,
    workRequest
)

// ✅ REPLACE — cancel old, start new
WorkManager.getInstance(context).enqueueUniqueWork(
    "sync_work",
    ExistingWorkPolicy.REPLACE,
    workRequest
)
```

Unique work and chaining help avoid duplication and make behavior deterministic, improving overall reliability.

### Device Reboot Handling

After a device reboot, `WorkManager` reloads unfinished work from its database and resumes scheduling according to their status and constraints. The low-level reboot handling (e.g., receivers) is internal to the library and may differ between versions.

### Expedited Work

For urgent tasks, `WorkManager` supports "expedited work" — prioritized execution that may use a foreground service under the hood, subject to platform quotas. If the quota is exceeded, the request can fall back to a normal (non-expedited) work request depending on the specified `OutOfQuotaPolicy`.

```kotlin
class ExpeditedWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) {
    override suspend fun getForegroundInfo(): ForegroundInfo {
        return ForegroundInfo(NOTIFICATION_ID, createNotification())
    }

    override suspend fun doWork(): Result {
        setForeground(getForegroundInfo()) // ✅ Promote to foreground for expedited execution when required
        return try {
            processUrgentData()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

val expeditedRequest = OneTimeWorkRequestBuilder<ExpeditedWorker>()
    .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
    .build()
```

### Summary

`WorkManager` ensures high reliability for deferrable background work via:
- Immediate `SQLite` persistence on enqueue
- Automatic selection of platform scheduling mechanisms (JobScheduler, etc.)
- Strict constraint enforcement
- Configurable backoff strategies for retries
- Recovery of pending work after device reboot
- Support for expedited work / foreground-like execution for urgent tasks

**Limitations**:
- Periodic work does not guarantee exact execution time (minimum interval ~15 minutes; execution may be delayed).
- Doze Mode, App Standby, OEM restrictions, force stop, app uninstall, or data wipe can prevent completion.

## Дополнительные Вопросы (RU)

1. Что происходит с задачами `WorkManager` во время Doze Mode?
2. Как отслеживать прогресс `WorkManager` в `ViewModel`?
3. Когда следует использовать expedited work вместо прямого foreground service?
4. Как `WorkManager` обрабатывает сбои в цепочке работ (например, если `workA` завершилась с ошибкой)?
5. Каковы trade-off'ы между `ExistingWorkPolicy.KEEP` и `ExistingWorkPolicy.REPLACE`?

## Follow-ups

1. What happens to `WorkManager` tasks during Doze Mode?
2. How do you observe `WorkManager` progress in a `ViewModel`?
3. When should you use expedited work vs. a direct foreground service?
4. How does `WorkManager` handle work chain failures (e.g., if `workA` fails)?
5. What are the trade-offs between `ExistingWorkPolicy.KEEP` vs. `ExistingWorkPolicy.REPLACE`?

## Ссылки (RU)

- [Документация WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Расширенные возможности WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager/advanced)

## References

- [WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager)
- https://developer.android.com/topic/libraries/architecture/workmanager/advanced

## Связанные Вопросы (RU)

### Предпосылки

- [[q-android-services-purpose--android--easy]]
- [[q-background-tasks-decision-guide--android--medium]]

### Похожие

- [[q-background-vs-foreground-service--android--medium]]
- [[q-service-restrictions-why--android--medium]]

### Продвинутое

- [[q-service-lifecycle-binding--android--hard]]
- [[q-keep-service-running-background--android--medium]]

## Related Questions

### Prerequisites

- [[q-android-services-purpose--android--easy]]
- [[q-background-tasks-decision-guide--android--medium]]

### Related

- [[q-background-vs-foreground-service--android--medium]]
- [[q-service-restrictions-why--android--medium]]

### Advanced

- [[q-service-lifecycle-binding--android--hard]]
- [[q-keep-service-running-background--android--medium]]
