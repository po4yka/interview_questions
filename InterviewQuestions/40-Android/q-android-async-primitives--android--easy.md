---
id: 20251012-122762
title: Android Async Primitives / Примитивы асинхронности Android
aliases: ["Android Async Primitives", "Примитивы асинхронности Android"]
topic: android
subtopics: [coroutines, threads-sync]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-coroutine-builders-basics--kotlin--easy, q-viewmodel-pattern--android--easy]
created: 2025-10-15
updated: 2025-01-27
tags: [android/coroutines, android/threads-sync, difficulty/easy]
---
# Вопрос (RU)
> Какие примитивы асинхронности предоставляет Android?

---

# Question (EN)
> What are Android Async Primitives?

---

## Ответ (RU)

Android предоставляет несколько примитивов для асинхронной работы:

**Современные (рекомендуемые):**
- **[[c-coroutines|Корутины]]** — легковесная конкурентность с автоматическим управлением жизненным циклом
- **Flow** — реактивные потоки данных (cold/hot)
- **[[c-workmanager|WorkManager]]** — гарантированное выполнение фоновых задач

**Legacy (устаревшие):**
- **Handler/Looper** — передача сообщений между потоками
- **ExecutorService** — управление пулом потоков
- **RxJava** — реактивное программирование
- **AsyncTask** — DEPRECATED, не использовать

### 1. Kotlin Coroutines (основной выбор)

```kotlin
class DataViewModel : ViewModel() {
    // ✅ Базовое использование
    fun loadData() {
        viewModelScope.launch {
            val data = withContext(Dispatchers.IO) {
                repository.fetchData() // выполняется на IO потоке
            }
            _uiState.value = UiState.Success(data)
        }
    }

    // ✅ Параллельные операции
    fun loadMultiple() {
        viewModelScope.launch {
            val result1 = async { fetchFromApi1() }
            val result2 = async { fetchFromApi2() }
            _data.value = result1.await() + result2.await()
        }
    }
}
```

### 2. Flow (реактивные потоки)

```kotlin
// ✅ StateFlow для UI состояния
private val _users = MutableStateFlow<List<User>>(emptyList())
val users: StateFlow<List<User>> = _users.asStateFlow()

// ✅ Обработка потока
lifecycleScope.launch {
    repository.getUsers()
        .flowOn(Dispatchers.IO)
        .collect { users ->
            adapter.submitList(users)
        }
}
```

### 3. WorkManager (гарантированная фоновая работа)

```kotlin
class DataSyncWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    // ✅ Переживает перезапуск приложения
    override suspend fun doWork(): Result = try {
        syncData()
        Result.success()
    } catch (e: Exception) {
        Result.retry()
    }
}
```

**Сравнение:**

| Примитив | Lifecycle | Отмена | Рекомендуется |
|----------|-----------|--------|---------------|
| Coroutines | ✅ Да | ✅ Да | ✅ Да |
| Flow | ✅ Да | ✅ Да | ✅ Да |
| WorkManager | ✅ Да | ✅ Да | ✅ Да |
| Handler/Looper | ❌ Нет | ⚠️ Вручную | ⚠️ Редко |
| ExecutorService | ❌ Нет | ⚠️ Вручную | ❌ Нет |
| RxJava | ❌ Нет | ✅ Да | ❌ Нет |
| AsyncTask | ❌ Нет | ❌ Нет | ❌ DEPRECATED |

**Лучшие практики:**
- Используйте [[c-coroutines|корутины]] для большинства асинхронных операций
- Используйте Flow для реактивных потоков данных
- Используйте [[c-workmanager|WorkManager]] для задач, которые должны выполниться гарантированно

---

## Answer (EN)

Android provides several async primitives:

**Modern (recommended):**
- **[[c-coroutines|Coroutines]]** — lightweight concurrency with automatic lifecycle management
- **Flow** — reactive data streams (cold/hot)
- **[[c-workmanager|WorkManager]]** — guaranteed background task execution

**Legacy (outdated):**
- **Handler/Looper** — message passing between threads
- **ExecutorService** — thread pool management
- **RxJava** — reactive programming
- **AsyncTask** — DEPRECATED, don't use

### 1. Kotlin Coroutines (primary choice)

```kotlin
class DataViewModel : ViewModel() {
    // ✅ Basic usage
    fun loadData() {
        viewModelScope.launch {
            val data = withContext(Dispatchers.IO) {
                repository.fetchData() // runs on IO thread
            }
            _uiState.value = UiState.Success(data)
        }
    }

    // ✅ Parallel operations
    fun loadMultiple() {
        viewModelScope.launch {
            val result1 = async { fetchFromApi1() }
            val result2 = async { fetchFromApi2() }
            _data.value = result1.await() + result2.await()
        }
    }
}
```

### 2. Flow (reactive streams)

```kotlin
// ✅ StateFlow for UI state
private val _users = MutableStateFlow<List<User>>(emptyList())
val users: StateFlow<List<User>> = _users.asStateFlow()

// ✅ Stream processing
lifecycleScope.launch {
    repository.getUsers()
        .flowOn(Dispatchers.IO)
        .collect { users ->
            adapter.submitList(users)
        }
}
```

### 3. WorkManager (guaranteed background work)

```kotlin
class DataSyncWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    // ✅ Survives app restarts
    override suspend fun doWork(): Result = try {
        syncData()
        Result.success()
    } catch (e: Exception) {
        Result.retry()
    }
}
```

**Comparison:**

| Primitive | Lifecycle | Cancellation | Recommended |
|-----------|-----------|--------------|-------------|
| Coroutines | ✅ Yes | ✅ Yes | ✅ Yes |
| Flow | ✅ Yes | ✅ Yes | ✅ Yes |
| WorkManager | ✅ Yes | ✅ Yes | ✅ Yes |
| Handler/Looper | ❌ No | ⚠️ Manual | ⚠️ Rarely |
| ExecutorService | ❌ No | ⚠️ Manual | ❌ No |
| RxJava | ❌ No | ✅ Yes | ❌ No |
| AsyncTask | ❌ No | ❌ No | ❌ DEPRECATED |

**Best practices:**
- Use [[c-coroutines|coroutines]] for most async operations
- Use Flow for reactive data streams
- Use [[c-workmanager|WorkManager]] for tasks that must complete reliably

---

## Follow-ups

- How does `viewModelScope` ensure automatic cancellation when ViewModel is cleared?
- What's the difference between `StateFlow` and `SharedFlow` in terms of buffering and replay?
- When would you prefer `ExecutorService` over coroutines despite the recommendation?
- How does WorkManager guarantee task execution across process death?
- What are the memory implications of using Handler with long-lived Activity references?

## References

- [[c-coroutines]] — Coroutines fundamentals
- [[c-workmanager]] — WorkManager architecture
- [Kotlin Flow Documentation](https://kotlinlang.org/docs/flow.html)
- [Android Threading Guide](https://developer.android.com/guide/components/processes-and-threads)

## Related Questions

### Prerequisites
- [[q-coroutine-builders-basics--kotlin--easy]] — Coroutines fundamentals
- [[q-viewmodel-pattern--android--easy]] — ViewModel pattern

### Related
- [[q-flow-operators--kotlin--medium]] — Flow operators
- [[q-what-is-workmanager--android--medium]] — WorkManager basics

### Advanced
- [[q-advanced-coroutine-patterns--kotlin--hard]] — Advanced coroutines
- [[q-workmanager-execution-guarantee--android--medium]] — WorkManager guarantees