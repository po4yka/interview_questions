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
related: [c-android, c-background-tasks, c-concurrency, q-android-architectural-patterns--android--medium]
created: 2025-10-15
updated: 2025-11-11
sources: []
tags: [android/background-execution, android/coroutines, difficulty/medium, workmanager]

date created: Saturday, November 1st 2025, 1:26:42 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---

# Вопрос (RU)

> Как вернуть результат работы WorkManager в приложение?

# Question (EN)

> How to return a result from WorkManager to the app?

---

## Ответ (RU)

WorkManager возвращает результаты через механизм `outputData`.

**Основной подход**:
1. В Worker используем `Result.success(outputData)` для передачи данных
2. В `Activity`/`ViewModel` наблюдаем за `WorkInfo` через `LiveData` или `Flow`
3. Проверяем состояние `WorkInfo.State.SUCCEEDED` (или `state.isFinished` для общих кейсов)
4. Извлекаем данные из `workInfo.outputData` (доступно только для завершённых работ)

Важно: `Data` в WorkManager поддерживает только примитивные типы, строки и их массивы, поэтому сложные объекты нужно сериализовать (например, в JSON).

### Реализация Worker

```kotlin
class DataWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val input = inputData.getInt("value", 0)
            val result: String = processData(input) // ✅ Выполняем работу, получаем String

            // ✅ Возвращаем успех с выходными данными
            Result.success(workDataOf(
                "result" to result,
                "timestamp" to System.currentTimeMillis()
            ))
        } catch (e: IOException) {
            Result.retry() // ✅ Сетевые ошибки — пробуем ещё раз
        } catch (e: Exception) {
            // ❌ Фатальная ошибка — завершаем с информацией об ошибке
            Result.failure(workDataOf("error" to (e.message ?: "Unknown error")))
        }
    }
}
```

(В этом примере `result` имеет тип `String`, поддерживаемый `Data`. Метод чтения должен совпадать с типом записи, например `getString("result")`.)

### Наблюдение В `ViewModel` (рекомендуемый способ)

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

        // ✅ Наблюдаем за статусом работы
        workManager.getWorkInfoByIdLiveData(request.id)
            .observeForever { workInfo ->
                if (workInfo == null) return@observeForever
                when (workInfo.state) {
                    WorkInfo.State.SUCCEEDED -> {
                        val data = workInfo.outputData.getString("result")
                        _result.value = WorkResult.Success(data)
                    }
                    WorkInfo.State.FAILED -> {
                        val error = workInfo.outputData.getString("error")
                        _result.value = WorkResult.Error(error)
                    }
                    WorkInfo.State.RUNNING -> {
                        _result.value = WorkResult.Loading
                    }
                    else -> { /* ENQUEUED, BLOCKED, CANCELLED и т.п. при необходимости можно обработать отдельно */ }
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

Важно: в реальном коде избегайте `observeForever` без явного вызова `removeObserver` (например, в `onCleared()`), чтобы не создавать утечки. В проде предпочтительнее наблюдать из UI-слоя с `observe(owner, ...)`.

### Современный Подход С `Flow`

```kotlin
class DataRepository(
    private val workManager: WorkManager
) {
    fun processData(value: Int): Flow<WorkResult> {
        val request = OneTimeWorkRequestBuilder<DataWorker>()
            .setInputData(workDataOf("value" to value))
            .build()

        workManager.enqueue(request)

        // ✅ Используем KTX Flow API WorkManager
        return workManager.getWorkInfoByIdFlow(request.id)
            .map { workInfo ->
                if (workInfo == null) {
                    WorkResult.Loading
                } else when (workInfo.state) {
                    WorkInfo.State.SUCCEEDED -> {
                        val data = workInfo.outputData.getString("result")
                        WorkResult.Success(data)
                    }
                    WorkInfo.State.FAILED -> {
                        val error = workInfo.outputData.getString("error")
                        WorkResult.Error(error)
                    }
                    else -> WorkResult.Loading
                }
            }
    }
}
```

### Передача Сложных Данных Через JSON

```kotlin
@Serializable
data class ProcessingResult(
    val processed: Int,
    val total: Int,
    val errors: List<String>
)

class ComplexDataWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val result = ProcessingResult(
            processed = 100,
            total = 150,
            errors = listOf("Error 1", "Error 2")
        )

        // ✅ Сериализуем сложные данные в JSON
        val json = Json.encodeToString(result)
        return Result.success(workDataOf("result_json" to json))
    }
}

// В наблюдателе:
val json = workInfo.outputData.getString("result_json")
val result = json?.let { Json.decodeFromString<ProcessingResult>(it) }
```

### Наблюдение По Тегу Или Уникальному Имени

```kotlin
// По тегу
workManager.getWorkInfosByTagLiveData("data_sync")
    .observe(this) { workInfoList ->
        workInfoList.forEach { workInfo ->
            if (workInfo.state.isFinished) {
                processResult(workInfo.outputData)
            }
        }
    }

// По уникальному имени
workManager.getWorkInfosForUniqueWorkLiveData("background_sync")
    .observe(this) { workInfoList ->
        workInfoList.firstOrNull()?.let { workInfo ->
            if (workInfo.state.isFinished) {
                processResult(workInfo.outputData)
            }
        }
    }
```

**Ключевые классы**:
- `workDataOf()` — создание `Data` объекта
- `Result.success(data)` — возврат с данными
- `Result.failure(data)` — возврат с ошибкой
- `WorkInfo.State` — состояние работы
- `workInfo.outputData` — извлечение результата для завершённой работы

**Лучшие практики**:
- Используйте `ViewModel` для разделения логики
- Предпочитайте `Flow` и KTX-расширения для современного реактивного кода
- Сериализуйте сложные объекты в JSON
- Обрабатывайте все состояния (SUCCEEDED, FAILED, RUNNING, CANCELLED и т.д.)
- Для прогресса используйте `setProgress()` и `setProgressAsync()` в Worker и отслеживайте `WorkInfo.progress` (не привязано к API 29 платформы)
- Следите за тем, чтобы не использовать `observeForever` без снятия подписки

---

## Answer (EN)

WorkManager returns results through the `outputData` mechanism.

**Core Approach**:
1. In Worker, use `Result.success(outputData)` to pass data
2. In `Activity`/`ViewModel`, observe `WorkInfo` via `LiveData` or `Flow`
3. Check for `WorkInfo.State.SUCCEEDED` (or `state.isFinished` for generic finished checks)
4. Extract data from `workInfo.outputData` (available only for finished work)

Note: WorkManager `Data` supports only primitive types, Strings, and their arrays, so complex objects must be serialized (e.g., to JSON).

### Worker Implementation

```kotlin
class DataWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val input = inputData.getInt("value", 0)
            val result: String = processData(input) // ✅ Perform work, producing a String

            // ✅ Return success with output data
            Result.success(workDataOf(
                "result" to result,
                "timestamp" to System.currentTimeMillis()
            ))
        } catch (e: IOException) {
            Result.retry() // ✅ Network error - retry
        } catch (e: Exception) {
            // ❌ Fatal error - fail with error info
            Result.failure(workDataOf("error" to (e.message ?: "Unknown error")))
        }
    }
}
```

(In this example, `result` is a `String`, which is supported by `Data`. The getter must match the stored type, e.g., `getString("result")`.)

### `ViewModel` Observation (Recommended)

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
                if (workInfo == null) return@observeForever
                when (workInfo.state) {
                    WorkInfo.State.SUCCEEDED -> {
                        val data = workInfo.outputData.getString("result")
                        _result.value = WorkResult.Success(data)
                    }
                    WorkInfo.State.FAILED -> {
                        val error = workInfo.outputData.getString("error")
                        _result.value = WorkResult.Error(error)
                    }
                    WorkInfo.State.RUNNING -> {
                        _result.value = WorkResult.Loading
                    }
                    else -> { /* ENQUEUED, BLOCKED, CANCELLED etc.; handle explicitly if needed */ }
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

Important: in production code, avoid `observeForever` without removing the observer (e.g., in `onCleared()`), otherwise you can leak the observer. Prefer observing from UI with `observe(owner, ...)`.

### Modern `Flow` Approach

```kotlin
class DataRepository(
    private val workManager: WorkManager
) {
    fun processData(value: Int): Flow<WorkResult> {
        val request = OneTimeWorkRequestBuilder<DataWorker>()
            .setInputData(workDataOf("value" to value))
            .build()

        workManager.enqueue(request)

        // ✅ Use WorkManager KTX Flow API directly
        return workManager.getWorkInfoByIdFlow(request.id)
            .map { workInfo ->
                if (workInfo == null) {
                    WorkResult.Loading
                } else when (workInfo.state) {
                    WorkInfo.State.SUCCEEDED -> {
                        val data = workInfo.outputData.getString("result")
                        WorkResult.Success(data)
                    }
                    WorkInfo.State.FAILED -> {
                        val error = workInfo.outputData.getString("error")
                        WorkResult.Error(error)
                    }
                    else -> WorkResult.Loading
                }
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

class ComplexDataWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

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
val result = json?.let { Json.decodeFromString<ProcessingResult>(it) }
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
            if (workInfo.state.isFinished) {
                processResult(workInfo.outputData)
            }
        }
    }
```

**Key Classes**:
- `workDataOf()` — create `Data` object
- `Result.success(data)` — return with data
- `Result.failure(data)` — return with error
- `WorkInfo.State` — work state
- `workInfo.outputData` — extract result for finished work

**Best Practices**:
- Use `ViewModel` for separation of concerns
- Prefer `Flow` and KTX extensions for modern reactive code
- Serialize complex objects to JSON
- Handle all states (SUCCEEDED, FAILED, RUNNING, CANCELLED, etc.)
- Use `setProgress()` / `setProgressAsync()` in Worker and observe `WorkInfo.progress` for progress updates (not limited to Android API 29)
- Avoid `observeForever` without removing observers to prevent leaks

---

## Дополнительные Вопросы (RU)

1. Как реализовать обновление прогресса для долгих задач WorkManager с помощью `setProgress`/`setProgressAsync`, как наблюдать `WorkInfo.progress` и какие паттерны использовать для стабильных обновлений UI после изменения конфигурации?
2. Каковы ограничения по размеру и типам данных `Data`/`outputData` в WorkManager, как они влияют на максимальный размер возвращаемого результата и когда следует использовать только идентификаторы с последующим чтением из БД или файлов?
3. Как связать несколько `Worker` так, чтобы `outputData` одного становился входными данными следующего (через `then()`/`beginWith()`), и как при этом корректно организовать обработку ошибок и повторов?
4. В каких случаях оправдано использование `observeForever()` для отслеживания `WorkInfo`, и как структурировать код (например, через `ViewModel` или репозиторий), чтобы гарантированно отписываться и не допускать утечек памяти?
5. Как спроектировать обработку результатов так, чтобы вывод WorkManager корректно доставлялся и восстанавливался при убийстве и последующем перезапуске процесса приложения (используя уникальные имена работ, теги, идемпотентных потребителей и персистентное хранилище)?

---

## Follow-ups

1. How can you implement progress updates for long-running WorkManager tasks using `setProgress`/`setProgressAsync` and observe them via `WorkInfo.progress`, and what patterns ensure consistent UI updates after configuration changes?
2. What are the size and type limitations of `Data`/`outputData` in WorkManager, how do they restrict the payload you can return, and when should you switch to using only identifiers with actual data stored in a database or files?
3. How would you chain multiple `Worker`s so that the output of one becomes the input of the next using APIs like `then()`/`beginWith()`, and how do you design error handling and retries in such chains?
4. When is using `observeForever()` for tracking `WorkInfo` justified, and how do you structure code (e.g., via `ViewModel`/repository) to ensure observers are removed and memory leaks are avoided?
5. How should you design result handling so that WorkManager outputs are correctly restored and delivered if the app process is killed and later recreated (e.g., with unique work names, tags, idempotent consumers, and persistent storage)?

---

## Ссылки (RU)

- [[c-android]] — базовые концепции Android
- [[c-background-tasks]] — общие подходы к фоновой работе
- [Документация WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Расширенное руководство по WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager/advanced)

---

## References

- [[c-android]] — Android core concepts
- [[c-background-tasks]] — Background work concepts
- [WorkManager Documentation](https://developer.android.com/topic/libraries/architecture/workmanager)
- [WorkManager Advanced Guide](https://developer.android.com/topic/libraries/architecture/workmanager/advanced)

---

## Связанные Вопросы (RU)

### База (проще)
- Основы WorkManager — см. более простые вопросы по WorkManager в этом хранилище
- Введение в корутины — см. базовые вопросы по корутинам в этом хранилище

### Связанные (тот Же уровень)
- Настройка ограничений WorkManager и их влияние на выполнение работ
- Цепочки WorkRequests и передача данных между ними
- Сравнение `LiveData` и `Flow` для наблюдения за результатами фоновых задач

### Продвинуто (сложнее)
- Стратегии и подводные камни при тестировании логики на базе WorkManager
- Ограничения фонового выполнения в Android и их влияние на дизайн WorkManager-задач

---

## Related Questions

### Prerequisites (Easier)
- WorkManager basics — see easier-level WorkManager introduction questions in this vault
- Coroutines introduction — see easier-level coroutine basics questions in this vault

### Related (Same Level)
- WorkManager constraints configuration and behavior
- Chaining multiple WorkRequests and passing data between them
- Comparing `LiveData` and `Flow` for observing background work results

### Advanced (Harder)
- Strategies and pitfalls when testing WorkManager-based background logic
- Android background execution limits and how they impact WorkManager design
