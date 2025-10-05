---
tags:
  - android
difficulty: medium
---

# How does the main thread work?

## Answer

The main thread (also called UI thread) is the central thread in Android that handles UI rendering, user input events, and component lifecycle callbacks. Understanding how it works is crucial for building responsive applications.

### Main Thread Responsibilities

1. **UI Rendering and Drawing**:
   - Measuring, laying out, and drawing views
   - Processing view hierarchy changes
   - Handling animations

2. **User Input Processing**:
   - Touch events
   - Key presses
   - Gestures

3. **Component Lifecycle Callbacks**:
   - Activity/Fragment lifecycle methods
   - Service callbacks
   - BroadcastReceiver events

4. **System Callbacks**:
   - Configuration changes
   - Memory warnings
   - Permission results

### Message Queue and Looper

The main thread operates using a message queue (Looper) pattern:

```
Main Thread
    ↓
[Looper] → [Message Queue] → [Handler]
    ↓            ↓
  Loop        Messages
               Tasks
               Runnables
```

**Components**:
- **Looper**: Runs infinite loop, processes messages sequentially
- **Message Queue**: Holds pending messages and tasks
- **Handler**: Posts messages/runnables to the queue

```kotlin
// Behind the scenes (simplified)
fun main() {
    Looper.prepare() // Prepare looper for current thread

    val handler = Handler(Looper.myLooper()!!)

    Looper.loop() // Start processing message queue
    // This blocks and processes messages until quit()
}
```

### Message Processing Flow

```kotlin
class MainActivity : AppCompatActivity() {
    private val mainHandler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // All these execute on main thread sequentially
        mainHandler.post {
            // Task 1
        }

        mainHandler.postDelayed({
            // Task 2 - executes after 1000ms
        }, 1000)

        view.setOnClickListener {
            // Click event - queued in message queue
        }
    }
}
```

### Main Thread Rules

#### ✅ Allowed Operations
- UI updates (setText, setVisibility, etc.)
- View inflation (should be optimized)
- Short computations (<16ms for 60fps)
- Lifecycle callbacks

#### ❌ Prohibited Operations
- Network requests
- Database queries (large datasets)
- File I/O operations
- Heavy computations
- Sleep/blocking calls

### ANR (Application Not Responding)

When the main thread is blocked for too long:

```kotlin
// ❌ BAD: Blocks main thread
class BadActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // This will cause ANR!
        Thread.sleep(10000) // 10 seconds

        // This will also cause ANR!
        val data = downloadLargeFile() // Network on main thread
    }
}
```

**ANR Triggers**:
- No response to input event within 5 seconds
- BroadcastReceiver doesn't finish within 10 seconds
- Service doesn't complete within 20 seconds (foreground)

### Proper Threading Patterns

#### 1. Coroutines (Recommended)
```kotlin
class GoodActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Background work
            val data = withContext(Dispatchers.IO) {
                downloadLargeFile()
            }
            // Main thread - UI update
            textView.text = data
        }
    }
}
```

#### 2. Handler + Background Thread
```kotlin
class DataProcessor {
    private val mainHandler = Handler(Looper.getMainLooper())

    fun processData(callback: (String) -> Unit) {
        Thread {
            // Background thread
            val result = heavyComputation()

            // Switch to main thread for callback
            mainHandler.post {
                callback(result)
            }
        }.start()
    }
}
```

#### 3. AsyncTask (Deprecated)
```kotlin
// ⚠️ Deprecated - use Coroutines instead
class DownloadTask : AsyncTask<String, Int, String>() {
    override fun doInBackground(vararg params: String): String {
        // Background thread
        return downloadFile(params[0])
    }

    override fun onPostExecute(result: String) {
        // Main thread
        updateUI(result)
    }
}
```

### Main Thread Optimization

1. **Frame Budget**: 60fps = 16ms per frame
   ```kotlin
   // Measure performance
   val startTime = System.currentTimeMillis()
   performOperation()
   val duration = System.currentTimeMillis() - startTime
   if (duration > 16) {
       Log.w("Performance", "Frame drop: ${duration}ms")
   }
   ```

2. **View Hierarchy Optimization**:
   - Flatten layouts (use ConstraintLayout)
   - Avoid nested weights
   - Use ViewStub for conditional views
   - Implement RecyclerView.ViewHolder pattern

3. **Choreographer for Frame Timing**:
   ```kotlin
   Choreographer.getInstance().postFrameCallback { frameTimeNanos ->
       // Execute on next frame
       updateAnimation()
   }
   ```

### Main Thread vs UI Thread

**They are the same!**
- Main thread = UI thread
- Both refer to the thread where Android app starts
- Where `onCreate()` and UI operations execute

### Checking Current Thread

```kotlin
fun isMainThread(): Boolean {
    return Looper.myLooper() == Looper.getMainLooper()
}

// Usage
if (isMainThread()) {
    updateUI()
} else {
    Handler(Looper.getMainLooper()).post {
        updateUI()
    }
}
```

### Summary

The main thread operates on a message queue pattern (Looper), processing events sequentially. Blocking operations must be moved to background threads to prevent ANR and maintain smooth UI performance (60fps = 16ms budget per frame).

## Answer (RU)
Это центральный поток, который отвечает за управление пользовательским интерфейсом приложения. Этот поток критически важен, потому что именно он обрабатывает все действия пользовательского интерфейса, включая отрисовку вьюх (views), обработку взаимодействий пользователя и выполнение анимаций. Также основной поток обрабатывает системные вызовы, такие как события жизненного цикла активности. Работа основной поток: обработка событий, выполнение задач связанных с пользовательским интерфейсом, цикл событий (Looper), запрет на тяжелые операции.

## Related Topics
- Looper and Handler
- ANR (Application Not Responding)
- Coroutines and Dispatchers
- Thread safety
- Performance optimization
