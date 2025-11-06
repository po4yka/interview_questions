---
id: android-275
title: "Multithreading Tools Android / Инструменты многопоточности Android"
aliases: [Android Threading, Multithreading Tools Android, Инструменты многопоточности Android, Многопоточность Android]
topic: android
subtopics: [background-execution, coroutines, performance-startup]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: []
created: 2025-10-15
updated: 2025-10-30
sources: [https://developer.android.com/kotlin/coroutines, https://developer.android.com/topic/libraries/architecture/workmanager]
tags: [android/background-execution, android/coroutines, android/performance-startup, concurrency, difficulty/medium, rxjava, workmanager]
---

# Вопрос (RU)

> Какие инструменты для многопоточности в Android вы знаете?

# Question (EN)

> What tools for multithreading in Android do you know?

---

## Ответ (RU)

Android предоставляет несколько инструментов для многопоточности и асинхронных операций:

### 1. Kotlin Coroutines (Рекомендуется)

**Корутина** — паттерн для конкурентности, упрощающий асинхронный код.

**Ключевые преимущества:**
- **Легковесные** — множество корутин на одном потоке благодаря приостановке
- **Структурированная конкурентность** — операции в области видимости, меньше утечек
- **Автоматическая отмена** — распространяется через иерархию корутин
- **Интеграция Jetpack** — полная поддержка в библиотеках

**✅ Базовый пример:**

```kotlin
class MyViewModel : ViewModel() {
    fun fetchData() {
        viewModelScope.launch {
            try {
                val data = withContext(Dispatchers.IO) {
                    repository.fetchData()
                }
                _uiState.value = UiState.Success(data)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e)
            }
        }
    }
}
```

**Диспетчеры:**
- `Dispatchers.Main` — UI поток
- `Dispatchers.IO` — I/O операции (сеть, БД, файлы)
- `Dispatchers.Default` — CPU-интенсивные вычисления

**✅ Структурированная конкурентность:**

```kotlin
coroutineScope {
    val data1 = async(Dispatchers.IO) { fetchData1() }
    val data2 = async(Dispatchers.IO) { fetchData2() }
    val result = data1.await() + data2.await()
}
```

**Области видимости:**
- `viewModelScope` — привязан к жизненному циклу `ViewModel`
- `lifecycleScope` — привязан к `Activity`/`Fragment`
- `GlobalScope` — уровень приложения (осторожно)

**✅ `Flow` для потоков данных:**

```kotlin
fun fetchUpdates(): Flow<Update> = flow {
    while (true) {
        emit(api.getUpdate())
        delay(1000)
    }
}

viewModelScope.launch {
    fetchUpdates()
        .flowOn(Dispatchers.IO)
        .collect { updateUI(it) }
}
```

### 2. WorkManager

API для планирования **отложенных асинхронных задач**, которые должны выполняться даже после закрытия приложения.

**Ключевые особенности:**
- **Гарантированное выполнение** — работа сохраняется при убийстве приложения/перезагрузке
- **Ограничения** — запуск только при выполнении условий (сеть, батарея, хранилище)
- **Обратная совместимость** — с API level 14
- **Экономия батареи** — учитывает Doze и App Standby

**✅ Пример:**

```kotlin
class UploadWorker(context: Context, params: WorkerParameters) : Worker(context, params) {
    override fun doWork(): Result {
        uploadData()
        return Result.success()
    }
}

val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(uploadRequest)
```

**Когда использовать:**
- Задачи должны выполняться даже при закрытом приложении
- Специфические ограничения (сеть, зарядка)
- Периодические задачи (синхронизация, бэкап)

### 3. RxJava / RxAndroid

Reactive Extensions для Java VM — композиция асинхронных программ через наблюдаемые последовательности.

**✅ Пример с переключением потоков:**

```kotlin
Observable.fromCallable { fetchDataFromNetwork() }
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe(
        { result -> updateUI(result) },
        { error -> showError(error) }
    )
```

**Основные планировщики:**
- `Schedulers.io()` — I/O операции
- `Schedulers.computation()` — CPU-интенсивные вычисления
- `AndroidSchedulers.mainThread()` — UI поток

**Преимущества:**
- Мощные операторы для трансформации данных
- Легкое переключение потоков
- Отлично для сложных асинхронных потоков

**❌ Недостатки:**
- Крутая кривая обучения
- Большой размер библиотеки
- Вытесняется Kotlin Coroutines

### 4. AsyncTask (❌ Устарел)

`AsyncTask` был предназначен для UI потока, но **deprecated** и не должен использоваться.

**Почему устарел:**
- Утечки `Context`, пропущенные коллбэки, сбои при изменении конфигурации
- Несогласованное поведение на разных версиях Android
- Поглощает исключения из `doInBackground`

**Альтернатива:** Kotlin Coroutines или Executors

### Сравнительная Таблица

| Инструмент | Статус | Лучше всего для | Сложность |
|------------|--------|-----------------|-----------|
| **Kotlin Coroutines** | ✅ Рекомендуется | Общие async/await, современная разработка | Низкая-Средняя |
| **WorkManager** | ✅ Рекомендуется | Гарантированная фоновая работа с ограничениями | Средняя |
| **RxJava** | Зрелый | Сложные потоки событий, реактивное программирование | Высокая |
| **AsyncTask** | ❌ Устарел | Ничего (используйте альтернативы) | Низкая |

### Современные Рекомендации

Для новой разработки Android:
1. **Kotlin Coroutines** — для асинхронных операций, сетевых вызовов, доступа к БД
2. **WorkManager** — для отложенных фоновых задач с гарантированным выполнением
3. **RxJava** — только при существующей кодовой базе или специфических реактивных требованиях
4. **❌ AsyncTask** — не использовать (устарел)

## Answer (EN)

Android provides several tools for multithreading and asynchronous operations:

### 1. Kotlin Coroutines (Recommended)

A **coroutine** is a concurrency design pattern that simplifies asynchronous code.

**Key Benefits:**
- **Lightweight** — many coroutines on a single thread via suspension
- **Structured concurrency** — operations within scope, fewer memory leaks
- **Built-in cancellation** — propagates automatically through hierarchy
- **Jetpack integration** — full support across libraries

**✅ Basic Example:**

```kotlin
class MyViewModel : ViewModel() {
    fun fetchData() {
        viewModelScope.launch {
            try {
                val data = withContext(Dispatchers.IO) {
                    repository.fetchData()
                }
                _uiState.value = UiState.Success(data)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e)
            }
        }
    }
}
```

**Dispatchers:**
- `Dispatchers.Main` — UI thread
- `Dispatchers.IO` — I/O operations (network, database, files)
- `Dispatchers.Default` — CPU-intensive work

**✅ Structured Concurrency:**

```kotlin
coroutineScope {
    val data1 = async(Dispatchers.IO) { fetchData1() }
    val data2 = async(Dispatchers.IO) { fetchData2() }
    val result = data1.await() + data2.await()
}
```

**`Coroutine` Scopes:**
- `viewModelScope` — tied to `ViewModel` lifecycle
- `lifecycleScope` — tied to `Activity`/`Fragment` lifecycle
- `GlobalScope` — application-level scope (use carefully)

**✅ `Flow` for Streams:**

```kotlin
fun fetchUpdates(): Flow<Update> = flow {
    while (true) {
        emit(api.getUpdate())
        delay(1000)
    }
}

viewModelScope.launch {
    fetchUpdates()
        .flowOn(Dispatchers.IO)
        .collect { updateUI(it) }
}
```

### 2. WorkManager

API for scheduling **deferrable asynchronous tasks** that run even if app exits.

**Key Features:**
- **Guaranteed execution** — work persists through app kill/device restart
- **Constraint-based** — run only when conditions met (network, battery, storage)
- **Backward compatibility** — works back to API level 14
- **Battery-conscious** — respects Doze mode and App Standby

**✅ Example:**

```kotlin
class UploadWorker(context: Context, params: WorkerParameters) : Worker(context, params) {
    override fun doWork(): Result {
        uploadData()
        return Result.success()
    }
}

val uploadRequest = OneTimeWorkRequestBuilder<UploadWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(uploadRequest)
```

**When to Use:**
- Tasks need to run even if app closed
- Specific constraints (network, charging)
- Periodic tasks (sync, backup)

### 3. RxJava / RxAndroid

Reactive Extensions for Java VM — composing asynchronous programs via observable sequences.

**✅ `Thread` Switching Example:**

```kotlin
Observable.fromCallable { fetchDataFromNetwork() }
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe(
        { result -> updateUI(result) },
        { error -> showError(error) }
    )
```

**Common Schedulers:**
- `Schedulers.io()` — I/O operations
- `Schedulers.computation()` — CPU-intensive computations
- `AndroidSchedulers.mainThread()` — Android UI thread

**Advantages:**
- Powerful operators for data transformation
- Easy thread switching
- Excellent for complex asynchronous flows

**❌ Disadvantages:**
- Steep learning curve
- Large library size
- Being superseded by Kotlin Coroutines

### 4. AsyncTask (❌ Deprecated)

`AsyncTask` was designed for UI thread but is **deprecated** and should not be used.

**Why Deprecated:**
- `Context` leaks, missed callbacks, crashes on configuration changes
- Inconsistent behavior across Android versions
- Swallows exceptions from `doInBackground`

**Alternative:** Kotlin Coroutines or Executors

### Comparison Summary

| Tool | Status | Best For | Complexity |
|------|--------|----------|------------|
| **Kotlin Coroutines** | ✅ Recommended | General async/await, modern Android development | Low-Medium |
| **WorkManager** | ✅ Recommended | Guaranteed background work with constraints | Medium |
| **RxJava** | Mature | Complex event streams, reactive programming | High |
| **AsyncTask** | ❌ Deprecated | Nothing (use alternatives) | Low |

### Modern Recommendations

For new Android development:
1. **Kotlin Coroutines** — for async operations, network calls, database access
2. **WorkManager** — for deferrable background tasks with guaranteed execution
3. **RxJava** — only if existing RxJava codebase or specific reactive requirements
4. **❌ AsyncTask** — never use (deprecated)

---

## Follow-ups

- How does structured concurrency prevent memory leaks in coroutines?
- When should you choose WorkManager over a Foreground `Service`?
- What are the differences between `flowOn()` and `withContext()` in coroutines?
- How do you handle backpressure in RxJava vs `Flow`?
- What happens to running coroutines when `ViewModel` is cleared?

## References

- [[c-coroutines]]
- [[c-structured-concurrency]]
- [[c-flow]]
- [Kotlin Coroutines on Android](https://developer.android.com/kotlin/coroutines)
- [WorkManager Guide](https://developer.android.com/topic/libraries/architecture/workmanager)

## Related Questions

### Prerequisites (Easier)
- [[q-android-async-primitives--android--easy]] - Basic async primitives in Android
- [[q-why-multithreading-tools--android--easy]] - Why use multithreading
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Main thread basics

### Related (Same Level)
- [[q-background-vs-foreground-service--android--medium]] - Background service types
- [[q-handler-looper-comprehensive--android--medium]] - `Handler` and `Looper` mechanics
- [[q-looper-empty-queue-behavior--android--medium]] - `Looper` queue behavior
- [[q-workmanager-vs-alternatives--android--medium]] - WorkManager comparison

### Advanced (Harder)
- [[q-workmanager-chaining--android--hard]] - Complex WorkManager workflows
- [[q-kotlin-context-receivers--android--hard]] - Advanced context patterns
- [[q-android-runtime-internals--android--hard]] - ART internals
