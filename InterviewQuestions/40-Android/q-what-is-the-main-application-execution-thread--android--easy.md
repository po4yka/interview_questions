---
id: 202510031417003
title: "What is the main application execution thread"
question_ru: "Какой основной поток выполнения приложения"
question_en: "What is the main application execution thread"
topic: android
moc: moc-android
status: draft
difficulty: easy
tags:
  - main thread
  - UI thread
  - lifecycle
  - easy_kotlin
  - lang/ru
source: https://t.me/easy_kotlin/18
---

# What is the main application execution thread

## English Answer

The main application execution thread, also known as the **UI thread** (User Interface Thread), plays a key role in application functionality. This thread is responsible for managing the user interface and handling user interactions.

### Key Responsibilities

#### 1. User Interface Management
- Handles all UI updates and rendering
- Processes touch events and user input
- Updates views and draws on screen

```kotlin
// This code runs on the main thread
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // UI operations on main thread
        textView.text = "Hello, World!"
        button.setOnClickListener {
            // Click handler runs on main thread
            updateUI()
        }
    }
}
```

#### 2. Event Loop Processing
- Uses an event loop (event loop) that processes events from the event queue
- Continuously monitors and dispatches events
- Ensures smooth UI responsiveness

```
Main Thread Event Loop:
┌─────────────────────┐
│   Message Queue     │
│  - UI Update        │
│  - Touch Event      │
│  - Click Event      │
└──────────┬──────────┘
           │
           ↓
    ┌──────────────┐
    │ Event Loop   │
    │ (Looper)     │
    └──────┬───────┘
           │
           ↓
    Process Events
```

#### 3. Prohibits Long-Running Operations
- **Critical Rule**: Never block the main thread
- Long operations cause Application Not Responding (ANR) errors
- ANR threshold: ~5 seconds for user input, ~10 seconds for broadcast receivers

### What Should NOT Run on Main Thread

```kotlin
// ❌ BAD - Network call on main thread
class BadExample : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // This will cause NetworkOnMainThreadException
        val data = URL("https://api.example.com/data").readText()
        textView.text = data
    }
}
```

### Proper Background Work

```kotlin
// ✅ GOOD - Using coroutines for background work
class GoodExample : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Background work on IO thread
            val data = withContext(Dispatchers.IO) {
                URL("https://api.example.com/data").readText()
            }
            // UI update on main thread
            textView.text = data
        }
    }
}
```

### Main Thread Characteristics

| Aspect | Description |
|--------|-------------|
| **Name** | Main Thread / UI Thread |
| **Purpose** | Handle UI and user interactions |
| **Event Processing** | Event loop with message queue |
| **Blocking** | Causes ANR if blocked too long |
| **Thread Safety** | Only main thread can update UI |

### How to Switch Between Threads

#### 1. Using Coroutines (Recommended)
```kotlin
lifecycleScope.launch {
    // Main thread by default
    textView.text = "Loading..."

    // Switch to background
    val result = withContext(Dispatchers.IO) {
        // Perform long operation
        fetchData()
    }

    // Automatically back on main thread
    textView.text = result
}
```

#### 2. Using Handler
```kotlin
val handler = Handler(Looper.getMainLooper())

// From background thread, post to main thread
Thread {
    // Background work
    val result = performHeavyWork()

    // Update UI on main thread
    handler.post {
        textView.text = result
    }
}.start()
```

#### 3. Using runOnUiThread
```kotlin
Thread {
    // Background work
    val result = performHeavyWork()

    // Switch to main thread
    runOnUiThread {
        textView.text = result
    }
}.start()
```

### ANR (Application Not Responding)

```kotlin
// ❌ This will cause ANR
button.setOnClickListener {
    // Blocking main thread for 10 seconds
    Thread.sleep(10000)
    textView.text = "Done" // User will see ANR dialog
}

// ✅ Correct approach
button.setOnClickListener {
    lifecycleScope.launch {
        textView.text = "Processing..."
        delay(10000) // Non-blocking delay
        textView.text = "Done"
    }
}
```

### Best Practices

1. **Keep main thread responsive** - Never perform heavy operations
2. **Use coroutines or WorkManager** for background tasks
3. **Update UI only from main thread**
4. **Monitor performance** - Use Android Profiler to detect blocking
5. **Handle configuration changes** properly to avoid recreating work

## Russian Answer

Основной поток выполнения приложения, также известный как UI-поток (User Interface Thread), играет ключевую роль в функционировании приложения. Этот поток ответственен за управление пользовательским интерфейсом и обработку взаимодействий с пользователем.

### Основные обязанности

Он отвечает за:
- **Обработку пользовательского интерфейса**: Все обновления UI, отрисовка элементов, обработка касаний
- **Обработку событий**: Нажатия кнопок, жесты, ввод текста
- **Запрещает длительные операции**: Блокировка главного потока приводит к зависанию приложения (ANR - Application Not Responding)

Использует петлю событий (event loop), которая обрабатывает события из очереди событий. Это обеспечивает плавную работу пользовательского интерфейса и быструю реакцию на действия пользователя.

### Важно помнить

- Только главный поток может обновлять UI
- Длительные операции (сеть, база данных) должны выполняться в фоновых потоках
- Блокировка главного потока более 5 секунд вызывает диалог ANR
