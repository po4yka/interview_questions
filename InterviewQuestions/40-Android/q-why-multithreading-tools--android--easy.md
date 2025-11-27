---
id: android-437
title: "Why Multithreading Tools / Зачем инструменты многопоточности"
aliases: [Android Concurrency, Multithreading Tools, Инструменты многопоточности]
topic: android
subtopics: [background-execution, coroutines, threads-sync]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-coroutines, c-workmanager]
created: 2025-10-15
updated: 2025-11-10
tags: [android/background-execution, android/coroutines, android/threads-sync, difficulty/easy]
sources: ["https://developer.android.com/guide/background", "https://developer.android.com/kotlin/coroutines"]

date created: Saturday, November 1st 2025, 1:26:27 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---
# Вопрос (RU)

> Для чего нужна многопоточность в Android и какие инструменты использовать?

# Question (EN)

> Why is multithreading needed in Android and which tools should be used?

---

## Ответ (RU)

### Зачем Нужна Многопоточность

**Проблема:** UI поток (Main Thread) выполняет:
- Отрисовку интерфейса (60 FPS ≈ 16ms на кадр)
- Обработку событий пользователя
- Lifecycle callbacks

Если долго блокировать UI поток (сотни миллисекунд и более), интерфейс начинает лагать, а при длительной блокировке (порядка нескольких секунд, например около 5s для обработки ввода) система может показать **ANR** (`Application` Not Responding).

❌ **Плохо: Блокировка UI потока**
```kotlin
class MainActivity : AppCompatActivity() {
    private fun loadData() {
        // Блокирует UI на 5 секунд!
        Thread.sleep(5000)
        val data = fetchFromNetwork()
        textView.text = data
    }
}
```

✅ **Хорошо: Работа в фоновом потоке**
```kotlin
class MainActivity : AppCompatActivity() {
    private fun loadData() {
        lifecycleScope.launch(Dispatchers.IO) {
            // Фоновая работа
            val data = fetchFromNetwork()

            // Обновление UI в главном потоке
            withContext(Dispatchers.Main) {
                textView.text = data
            }
        }
    }
}
```

### Какие Задачи Выполнять В Фоновых Потоках

1. **Сетевые запросы**
2. **Операции с базой данных**
3. **Чтение/запись файлов**
4. **Обработка изображений**
5. **Парсинг больших данных**

### Основные Инструменты Многопоточности

#### 1. Kotlin Coroutines (Рекомендуется)

**Современный подход с учётом жизненного цикла**

```kotlin
class UserViewModel : ViewModel() {
    fun loadUser(userId: String) {
        viewModelScope.launch(Dispatchers.IO) {
            try {
                val user = userRepository.getUser(userId)

                withContext(Dispatchers.Main) {
                    _userState.value = user
                }
            } catch (e: Exception) {
                _errorState.value = e.message
            }
        }
    }
}
```

**Преимущества:**
- ✅ При использовании lifecycleScope/viewModelScope корутины автоматически отменяются при уничтожении соответствующего компонента
- ✅ Простой синтаксис
- ✅ Удобная обработка ошибок (structured concurrency, try/catch, supervisor scopes)
- ✅ Легко переключаться между контекстами (например, IO/Main)

#### 2. WorkManager

**Отложенное и надёжное выполнение фоновых задач**

```kotlin
class SyncWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            syncDataWithServer()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// Запуск периодической синхронизации
val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(syncRequest)
```

**Преимущества:**
- ✅ Может продолжать выполнение задач после перезапуска приложения
- ✅ Учитывает состояние системы (батарея, сеть)
- ✅ Стремится гарантировать выполнение при соблюдении ограничений и доступности соответствующих сервисов

**Когда использовать:** Синхронизация данных, загрузка файлов, очистка кэша

#### 3. Thread + Handler

**Базовый подход (для простых случаев)**

```kotlin
class MainActivity : AppCompatActivity() {
    private fun loadData() {
        Thread {
            // Фоновая работа
            val data = fetchFromNetwork()

            // Обновление UI
            runOnUiThread {
                textView.text = data
            }
        }.start()
    }
}
```

❌ **Недостатки:**
- Создаёт новый поток каждый раз (неэффективно)
- Нет автоматической отмены
- Нужно вручную управлять потоками

### Выбор Диспетчера Для Coroutines

```kotlin
// Сеть, БД, файлы
Dispatchers.IO

// Вычисления, парсинг
Dispatchers.Default

// Обновление UI
Dispatchers.Main
```

### Правило

> Практическое правило: если операция может занять больше бюджета кадра (≈16ms) и её результат не нужен немедленно для отрисовки UI, выполняйте её в фоновом потоке.

---

## Answer (EN)

### Why Multithreading is Needed

**Problem:** The UI thread (Main Thread) handles:
- UI rendering (60 FPS ≈ 16ms per frame)
- User interaction events
- Lifecycle callbacks

If you block the UI thread for a noticeable time (hundreds of milliseconds or more), the UI starts to stutter, and if it is blocked for a long time (on the order of several seconds, e.g. around 5s for input dispatch), the system may show an **ANR** (`Application` Not Responding).

❌ **Bad: Blocking UI Thread**
```kotlin
class MainActivity : AppCompatActivity() {
    private fun loadData() {
        // Blocks UI for 5 seconds!
        Thread.sleep(5000)
        val data = fetchFromNetwork()
        textView.text = data
    }
}
```

✅ **Good: Background Thread**
```kotlin
class MainActivity : AppCompatActivity() {
    private fun loadData() {
        lifecycleScope.launch(Dispatchers.IO) {
            // Background work
            val data = fetchFromNetwork()

            // Update UI on main thread
            withContext(Dispatchers.Main) {
                textView.text = data
            }
        }
    }
}
```

### Tasks for Background Threads

1. **Network requests**
2. **Database operations**
3. **File I/O**
4. **Image processing**
5. **Parsing large data**

### Main Multithreading Tools

#### 1. Kotlin Coroutines (Recommended)

**Modern approach with lifecycle awareness**

```kotlin
class UserViewModel : ViewModel() {
    fun loadUser(userId: String) {
        viewModelScope.launch(Dispatchers.IO) {
            try {
                val user = userRepository.getUser(userId)

                withContext(Dispatchers.Main) {
                    _userState.value = user
                }
            } catch (e: Exception) {
                _errorState.value = e.message
            }
        }
    }
}
```

**Advantages:**
- ✅ When using lifecycleScope/viewModelScope, coroutines are automatically cancelled when the corresponding component is destroyed
- ✅ Simple syntax
- ✅ Convenient error handling via structured concurrency, try/catch, supervisor scopes
- ✅ Easy to switch between contexts (e.g., IO/Main)

#### 2. WorkManager

**Deferred and reliable background job execution**

```kotlin
class SyncWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            syncDataWithServer()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// Schedule periodic sync
val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(syncRequest)
```

**Advantages:**
- ✅ Can continue work after app restarts
- ✅ Respects system conditions (battery, network)
- ✅ Aims to guarantee execution as long as constraints are met and required services are available

**When to use:** Data sync, file uploads, cache cleanup

#### 3. Thread + Handler

**Basic approach (for simple cases)**

```kotlin
class MainActivity : AppCompatActivity() {
    private fun loadData() {
        Thread {
            // Background work
            val data = fetchFromNetwork()

            // Update UI
            runOnUiThread {
                textView.text = data
            }
        }.start()
    }
}
```

❌ **Drawbacks:**
- Creates a new thread each time (inefficient)
- No automatic cancellation
- Manual thread management needed

### Choosing Dispatchers for Coroutines

```kotlin
// Network, database, files
Dispatchers.IO

// Computations, parsing
Dispatchers.Default

// UI updates
Dispatchers.Main
```

### Rule of Thumb

> Practical guideline: if an operation can exceed the frame budget (~16ms) and its result is not needed immediately for the current frame's rendering, run it on a background thread.

---

## Дополнительные Вопросы (RU)

1. Что произойдёт, если выполнить сетевой запрос в главном потоке?
2. В чём разница между `Dispatchers.IO` и `Dispatchers.Default`?
3. В каких случаях стоит использовать WorkManager вместо только корутин?
4. Как lifecycleScope и viewModelScope помогают избежать утечек памяти?
5. Что такое ANR и как его предотвратить?

## Follow-ups

1. What happens if you perform a network request on the main thread?
2. What is the difference between Dispatchers.IO and Dispatchers.Default?
3. When should you use WorkManager instead of Coroutines?
4. How do lifecycleScope and viewModelScope prevent memory leaks?
5. What is ANR and how to prevent it?

## Ссылки (RU)

- [[c-coroutines]]
- [[c-workmanager]]
- [[moc-android]]
- [Руководство по фоновой работе в Android](https://developer.android.com/guide/background)
- [Kotlin Coroutines на Android](https://developer.android.com/kotlin/coroutines)
- [Руководство по WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager)

## References

- [[c-coroutines]]
- [[c-workmanager]]
- [[moc-android]]
- [Android Background Work Guide](https://developer.android.com/guide/background)
- [Kotlin Coroutines on Android](https://developer.android.com/kotlin/coroutines)
- [WorkManager Guide](https://developer.android.com/topic/libraries/architecture/workmanager)

## Связанные Вопросы (RU)

### Предпосылки (проще)
- (нет соответствующей локализованной ссылки)

### Похожие (тот Же уровень)
- [[q-repository-multiple-sources--android--medium]]

### Продвинутые (сложнее)
- [[q-how-to-reduce-number-of-recompositions-besides-side-effects--android--hard]]
- [[q-how-to-display-snackbar-or-toast-based-on-results--android--medium]]

## Related Questions

### Prerequisites (Easier)
- (no matching localized prerequisite link)

### Related (Same Level)
- [[q-repository-multiple-sources--android--medium]]

### Advanced (Harder)
- [[q-how-to-reduce-number-of-recompositions-besides-side-effects--android--hard]]
- [[q-how-to-display-snackbar-or-toast-based-on-results--android--medium]]
