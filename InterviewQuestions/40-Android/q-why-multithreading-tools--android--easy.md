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
related: [c-coroutines, c-main-thread, c-workmanager]
created: 2025-10-15
updated: 2025-10-30
tags: [android/background-execution, android/coroutines, android/threads-sync, difficulty/easy]
sources: [https://developer.android.com/guide/background, https://developer.android.com/kotlin/coroutines]

---

# Вопрос (RU)

> Для чего нужна многопоточность в Android и какие инструменты использовать?

# Question (EN)

> Why is multithreading needed in Android and which tools should be used?

---

## Ответ (RU)

### Зачем Нужна Многопоточность

**Проблема:** UI поток (Main `Thread`) выполняет:
- Отрисовку интерфейса (60 FPS = 16ms на кадр)
- Обработку событий пользователя
- `Lifecycle` callbacks

Если блокировать UI поток > 5 секунд → **ANR** (`Application` Not Responding)

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
- ✅ Автоматическая отмена при уничтожении `Activity`/`ViewModel`
- ✅ Простой синтаксис
- ✅ Встроенная обработка ошибок
- ✅ Легко переключаться между потоками

#### 2. WorkManager

**Гарантированное выполнение фоновых задач**

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
- ✅ Работает даже после перезапуска приложения
- ✅ Учитывает состояние системы (батарея, сеть)
- ✅ Гарантированное выполнение

**Когда использовать:** Синхронизация данных, загрузка файлов, очистка кэша

#### 3. `Thread` + `Handler`

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

> Если операция занимает > **16ms** (один кадр), выполняйте её в фоновом потоке

---

## Answer (EN)

### Why Multithreading is Needed

**Problem:** The UI thread (Main `Thread`) handles:
- UI rendering (60 FPS = 16ms per frame)
- User interaction events
- `Lifecycle` callbacks

If you block the UI thread for > 5 seconds → **ANR** (`Application` Not Responding)

❌ **Bad: Blocking UI `Thread`**
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

✅ **Good: Background `Thread`**
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
- ✅ Automatic cancellation when `Activity`/`ViewModel` is destroyed
- ✅ Simple syntax
- ✅ Built-in error handling
- ✅ Easy thread switching

#### 2. WorkManager

**Guaranteed background job execution**

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
- ✅ Survives app restarts
- ✅ Respects system conditions (battery, network)
- ✅ Guaranteed execution

**When to use:** Data sync, file uploads, cache cleanup

#### 3. `Thread` + `Handler`

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
- Creates new thread each time (inefficient)
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

> If an operation takes > **16ms** (one frame), run it on a background thread

---

## Follow-ups

1. What happens if you perform a network request on the main thread?
2. What is the difference between Dispatchers.IO and Dispatchers.Default?
3. When should you use WorkManager instead of Coroutines?
4. How do lifecycleScope and viewModelScope prevent memory leaks?
5. What is ANR and how to prevent it?

## References

- [[c-coroutines]]
- 
- 
- [[moc-android]]
- [Android Background Work Guide](https://developer.android.com/guide/background)
- [Kotlin Coroutines on Android](https://developer.android.com/kotlin/coroutines)
- [WorkManager Guide](https://developer.android.com/topic/libraries/architecture/workmanager)

## Related Questions

### Prerequisites (Easier)
- 

### Related (Same Level)
- [[q-repository-multiple-sources--android--medium]]
- 

### Advanced (Harder)
- [[q-how-to-reduce-number-of-recompositions-besides-side-effects--android--hard]]
- [[q-how-to-display-snackbar-or-toast-based-on-results--android--medium]]
