---
id: 20251012-122711
title: "Main Thread Android / Главный поток Android"
aliases: ["Main Thread Android", "Главный поток Android", "UI Thread", "Поток UI"]
topic: android
subtopics: [threads-sync, lifecycle]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-room-code-generation-timing--android--medium]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android/threads-sync, android/lifecycle, threading, ui-thread, difficulty/medium]
---
# Вопрос (RU)

> Какой основной поток выполнения в Android-приложении?

# Question (EN)

> What is the main execution thread in an Android application?

---

## Ответ (RU)

Главный поток (Main Thread), также известный как UI Thread, отвечает за обработку пользовательского интерфейса и событий в Android.

### Основные характеристики

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

Main thread работает на основе очереди событий (Looper + MessageQueue):

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

#### 3. ANR при блокировке

Блокировка главного потока более 5 секунд вызывает ANR (Application Not Responding):

```kotlin
// ❌ Блокирует UI
button.setOnClickListener {
    val data = URL("https://api.example.com").readText()  // NetworkOnMainThreadException!
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

### Запрещённые операции

**Нельзя выполнять в main thread**:

- Сетевые запросы
- Операции с базой данных
- Тяжёлые вычисления
- Чтение/запись больших файлов

### Современные подходы

```kotlin
// ✅ Coroutines с LifecycleScope
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) {
        repository.fetchData()
    }
    updateUI(data)
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

The Main Thread, also known as the UI Thread, is responsible for handling user interface operations and events in Android.

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

The main thread operates using an event queue (Looper + MessageQueue):

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

Blocking the main thread for more than 5 seconds triggers ANR (Application Not Responding):

```kotlin
// ❌ Blocks UI
button.setOnClickListener {
    val data = URL("https://api.example.com").readText()  // NetworkOnMainThreadException!
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

### Prohibited Operations

**Must NOT be performed on main thread**:

- Network requests
- Database operations
- Heavy computations
- Reading/writing large files

### Modern Approaches

```kotlin
// ✅ Coroutines with LifecycleScope
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) {
        repository.fetchData()
    }
    updateUI(data)
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

- How does Looper.prepare() work internally?
- What's the difference between Handler.post() and View.post()?
- How to detect if current code is running on main thread?
- What happens when MessageQueue is full?
- How does StrictMode detect main thread violations?

## References

- Official Android documentation on threading
- Kotlin Coroutines guide

## Related Questions

### Prerequisites
- Understanding of threads and processes in Android
- Coroutines fundamentals

### Related
- [[q-room-code-generation-timing--android--medium]] - Database operations and threading
- Handler and Looper patterns

### Advanced
- ANR debugging techniques
- StrictMode for thread policy violations
