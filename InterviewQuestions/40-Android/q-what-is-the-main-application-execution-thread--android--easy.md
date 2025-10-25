---
id: 20251012-122711167
title: "What Is The Main Application Execution Thread / Что такое главный поток выполнения приложения"
topic: android
difficulty: easy
status: draft
moc: moc-android
related: [q-what-navigation-methods-do-you-know--android--medium, q-how-to-add-fragment-synchronously-asynchronously--android--medium, q-what-is-pendingintent--programming-languages--medium]
created: 2025-10-15
tags: [threading, main-thread, ui-thread, looper, difficulty/easy]
---

# What is the main application execution thread?

## Answer (EN)
The main application execution thread in Android is called the **Main Thread** (also known as the **UI Thread**). It's the thread where all UI operations and component lifecycle callbacks are executed.

### Key Characteristics

**1. Single Thread**
- Only one main thread per application
- Created when the app starts
- Lives for the entire app lifecycle

**2. UI Updates**
- All UI operations must run on the main thread
- Views can only be accessed from the main thread
- Violating this causes `CalledFromWrongThreadException`

**3. Event Loop**
- Has a Looper that processes messages from MessageQueue
- Handles touch events, lifecycle callbacks, broadcasts

### Main Thread Components

```
Main Thread
   Looper (processes messages)
   MessageQueue (stores messages)
   Handler (sends/handles messages)
```

### Example: Main Thread in Action

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // This runs on MAIN THREAD
        val textView = findViewById<TextView>(R.id.textView)
        textView.text = "Hello" // UI update on main thread

        // Check if we're on main thread
        val isMainThread = Looper.myLooper() == Looper.getMainLooper()
        Log.d("Thread", "Is main thread: $isMainThread") // true
    }
}
```

### Why Main Thread Matters

**1. UI Rendering**
```kotlin
// This works (main thread)
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        textView.text = "Update" // On main thread - OK
    }
}
```

**2. Error When Accessing UI from Background Thread**
```kotlin
// This crashes!
Thread {
    textView.text = "Update" // CalledFromWrongThreadException!
}.start()
```

**3. Correct Way: Switch to Main Thread**
```kotlin
// Option 1: runOnUiThread
Thread {
    val data = fetchDataFromNetwork()
    runOnUiThread {
        textView.text = data // Now on main thread - OK
    }
}.start()

// Option 2: Handler
val mainHandler = Handler(Looper.getMainLooper())
Thread {
    val data = fetchDataFromNetwork()
    mainHandler.post {
        textView.text = data // Posted to main thread - OK
    }
}.start()

// Option 3: Coroutines (recommended)
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) {
        fetchDataFromNetwork()
    }
    textView.text = data // Automatically on main thread - OK
}
```

### Main Thread Responsibilities

1. **UI Rendering** - Drawing and updating views
2. **Event Handling** - Touch events, key events
3. **Lifecycle Callbacks** - onCreate, onStart, onResume, etc.
4. **Broadcast Receivers** - onReceive() runs on main thread
5. **View Callbacks** - onClick, onLongClick, etc.

### The 16ms Rule

The main thread must complete each frame in **16ms** (60 FPS) or **11ms** (90 FPS on some devices):

```
Frame 1: 0-16ms   → UI drawn successfully
Frame 2: 16-32ms  → UI drawn successfully
Frame 3: 32-48ms  → Too slow (20ms)! → Frame drop → Jank
```

**Don't block the main thread:**
```kotlin
// BAD - Blocks main thread
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        Thread.sleep(5000) // Freezes UI for 5 seconds!
        val data = fetchFromNetwork() // Network call on main thread!
    }
}

// GOOD - Use background thread
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val data = withContext(Dispatchers.IO) {
                fetchFromNetwork() // Runs on background thread
            }
            updateUI(data) // Back on main thread
        }
    }
}
```

### Checking if on Main Thread

```kotlin
fun isMainThread(): Boolean {
    return Looper.myLooper() == Looper.getMainLooper()
}

// Usage
if (isMainThread()) {
    // Safe to update UI
    textView.text = "Update"
} else {
    // Need to switch to main thread
    runOnUiThread {
        textView.text = "Update"
    }
}
```

### Main Thread Names

```kotlin
// Getting thread information
val currentThread = Thread.currentThread()
Log.d("Thread", "Name: ${currentThread.name}") // "main"
Log.d("Thread", "ID: ${currentThread.id}") // 1 (usually)
```

### Summary

**Main Thread (UI Thread):**
- Single thread for all UI operations
- Created when app starts
- Has Looper + MessageQueue
- Handles UI updates, events, lifecycle
- Must complete frames in 16ms (60 FPS)
- Never block with long operations

**Best practices:**
- UI updates only on main thread
- Long operations on background threads
- Use Coroutines to switch threads easily
- Keep main thread responsive (<16ms per frame)

## Ответ (RU)
Главный поток выполнения приложения в Android называется **Main Thread** (также известный как **UI Thread**). Это поток, в котором выполняются все операции с UI и обратные вызовы жизненного цикла компонентов.

### Ключевые характеристики

1. **Единственный поток** - только один главный поток на приложение
2. **UI обновления** - все операции с UI должны выполняться в главном потоке
3. **Event Loop** - имеет Looper, обрабатывающий сообщения из MessageQueue

### Правило 16ms

Главный поток должен завершать каждый кадр за **16ms** (60 FPS):
- Если дольше → пропуск кадра → "тормоза" (jank)
- Никогда не блокируйте главный поток долгими операциями

### Проверка главного потока

```kotlin
fun isMainThread(): Boolean {
    return Looper.myLooper() == Looper.getMainLooper()
}
```

### Переключение на главный поток

```kotlin
// Вариант 1: runOnUiThread
runOnUiThread {
    textView.text = data
}

// Вариант 2: Handler
Handler(Looper.getMainLooper()).post {
    textView.text = data
}

// Вариант 3: Coroutines (рекомендуется)
lifecycleScope.launch {
    textView.text = data // Автоматически на главном потоке
}
```

---

## Related Questions

### Related (Easy)
- [[q-architecture-components-libraries--android--easy]] - Fundamentals
- [[q-main-android-components--android--easy]] - Fundamentals
- [[q-what-unifies-android-components--android--easy]] - Fundamentals

### Advanced (Harder)
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Fundamentals
- [[q-anr-application-not-responding--android--medium]] - Fundamentals
- [[q-what-unites-the-main-components-of-an-android-application--android--medium]] - Fundamentals
