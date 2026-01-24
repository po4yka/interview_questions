---
id: android-132
title: Main Thread Android / Главный поток Android
aliases:
- Main Thread Android
- UI Thread
- Главный поток Android
- Поток UI
topic: android
subtopics:
- lifecycle
- threads-sync
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-coroutines
- c-lifecycle
- q-handler-looper-main-thread--android--medium
- q-how-does-the-main-thread-work--android--medium
- q-room-code-generation-timing--android--medium
- q-what-is-the-main-application-execution-thread--android--easy
created: 2025-10-15
updated: 2025-11-10
sources: []
tags:
- android/lifecycle
- android/threads-sync
- difficulty/medium
- threading
- ui-thread
anki_cards:
- slug: android-132-0-en
  language: en
  anki_id: 1768396093547
  synced_at: '2026-01-23T16:45:05.327725'
- slug: android-132-0-ru
  language: ru
  anki_id: 1768396093572
  synced_at: '2026-01-23T16:45:05.329156'
---
# Вопрос (RU)

> Какой основной поток выполнения в Android-приложении?

# Question (EN)

> What is the main execution thread in an Android application?

---

## Ответ (RU)

Главный поток (Main `Thread`), также известный как UI `Thread`, создаётся фреймворком при запуске процесса приложения и отвечает за обработку пользовательского интерфейса и событий в Android. Большинство API Android UI не являются потокобезопасными, поэтому взаимодействие с ними должно выполняться именно из этого потока.

### Основные Характеристики

#### 1. Обработка UI

Все операции с UI выполняются в главном потоке:

```kotlin
// ✅ UI обновления в main thread
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        findViewById<TextView>(R.id.textView).text = "Hello World"
    }
}
```

#### 2. Event Loop

Main thread работает на основе очереди сообщений/событий (`Looper` + MessageQueue):

```kotlin
// ✅ Отправка задачи в main thread
val handler = Handler(Looper.getMainLooper())
thread {
    val result = performComputation()
    handler.post {
        textView.text = result
    }
}
```

#### 3. ANR При Блокировке

Если главный поток надолго блокируется (например, на несколько секунд), система может сгенерировать ANR (`Application` Not Responding). Для пользовательского ввода типичный таймаут около 5 секунд, для некоторых других операций (например, `BroadcastReceiver`, сервисы) используются другие значения.

```kotlin
// ❌ Блокирует UI
button.setOnClickListener {
    val data = URL("https://api.example.com").readText()  // Может вызвать NetworkOnMainThreadException и фриз UI
    textView.text = data
}

// ✅ Использование фонового потока
button.setOnClickListener {
    lifecycleScope.launch(Dispatchers.IO) {
        val data = URL("https://api.example.com").readText()
        withContext(Dispatchers.Main) {
            textView.text = data
        }
    }
}
```

### Нежелательные Операции

В главном потоке нельзя выполнять длительные или блокирующие операции, такие как:

- Сетевые запросы
- Тяжёлые операции с базой данных
- Тяжёлые вычисления
- Чтение/запись больших файлов

Они должны выполняться на фоновых потоках / подходящих диспетчерах, чтобы не блокировать обработку событий и не приводить к ANR.

### Современные Подходы

```kotlin
// ✅ Coroutines с LifecycleScope
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) {
        repository.fetchData()
    }
    updateUI(data) // вызывается на главном потоке
}

// ✅ ViewModel с StateFlow
class MyViewModel : ViewModel() {
    private val _state = MutableStateFlow<UiState>(UiState.Loading)
    val state = _state.asStateFlow()

    fun loadData() {
        viewModelScope.launch {
            _state.value = UiState.Loading
            _state.value = try {
                UiState.Success(repository.getData())
            } catch (e: Exception) {
                UiState.Error(e.message)
            }
        }
    }
}
```

---

## Answer (EN)

The Main `Thread`, also known as the UI `Thread`, is created by the Android framework when the app process starts and is responsible for handling user interface operations and events. Most Android UI toolkit APIs are not thread-safe, so they must be accessed from this thread.

### Key Characteristics

#### 1. UI Processing

All UI-related operations must execute on the main thread:

```kotlin
// ✅ UI updates on main thread
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        findViewById<TextView>(R.id.textView).text = "Hello World"
    }
}
```

#### 2. Event Loop

The main thread operates using a message/event queue (`Looper` + MessageQueue):

```kotlin
// ✅ Posting task to main thread
val handler = Handler(Looper.getMainLooper())
thread {
    val result = performComputation()
    handler.post {
        textView.text = result
    }
}
```

#### 3. ANR on Blocking

If the main thread is blocked for too long (for example, several seconds), the system may trigger an ANR (`Application` Not Responding). For input events the typical timeout is around 5 seconds; other components (e.g., `BroadcastReceiver`, services) have different timeouts.

```kotlin
// ❌ Blocks UI
button.setOnClickListener {
    val data = URL("https://api.example.com").readText()  // May cause NetworkOnMainThreadException and freeze the UI
    textView.text = data
}

// ✅ Use background thread
button.setOnClickListener {
    lifecycleScope.launch(Dispatchers.IO) {
        val data = URL("https://api.example.com").readText()
        withContext(Dispatchers.Main) {
            textView.text = data
        }
    }
}
```

### Prohibited / Undesired Operations

`Long`-running or blocking work must NOT be performed on the main thread, including:

- Network requests
- Heavy database operations
- Heavy computations
- Reading/writing large files

Such work should run on background threads / appropriate dispatchers to keep the UI responsive and avoid ANRs.

### Modern Approaches

```kotlin
// ✅ Coroutines with LifecycleScope
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) {
        repository.fetchData()
    }
    updateUI(data) // runs on main thread
}

// ✅ ViewModel with StateFlow
class MyViewModel : ViewModel() {
    private val _state = MutableStateFlow<UiState>(UiState.Loading)
    val state = _state.asStateFlow()

    fun loadData() {
        viewModelScope.launch {
            _state.value = UiState.Loading
            _state.value = try {
                UiState.Success(repository.getData())
            } catch (e: Exception) {
                UiState.Error(e.message)
            }
        }
    }
}
```

---

## Follow-ups

- How does `Looper.prepare()` work internally?
- What's the difference between `Handler.post()` and `View.post()`?
- How to detect if current code is running on main thread?
- What happens when `MessageQueue` is full?
- How does StrictMode detect main thread violations?

## References

- ["https://developer.android.com/guide/components/processes-and-threads"]
- ["https://developer.android.com/kotlin/coroutines"]

## Related Questions

### Prerequisites / Concepts

- [[c-coroutines]]
- [[c-lifecycle]]

### Prerequisites

- Understanding of threads and processes in Android
- Coroutines fundamentals

### Related

- [[q-room-code-generation-timing--android--medium]] - `Database` operations and threading
- `Handler` and `Looper` patterns

### Advanced

- ANR debugging techniques
- StrictMode for thread policy violations
