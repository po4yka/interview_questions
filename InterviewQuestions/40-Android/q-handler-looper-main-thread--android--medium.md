---
id: 20251012-1227148
title: "Handler Looper Main Thread / Handler и Looper главного потока"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-koin-vs-hilt-comparison--dependency-injection--medium, q-offline-first-architecture--android--hard, q-what-is-the-layout-called-where-objects-can-overlay-each-other--android--easy]
created: 2025-10-15
tags: [android/concurrency, concurrency, difficulty/medium, handler, looper, main-thread, message-queue, threading]
date created: Saturday, October 25th 2025, 1:26:29 pm
date modified: Saturday, October 25th 2025, 4:47:00 pm
---

# Как Можно Получить Сообщения На Главном Потоке С Помощью Handler И Looper?

**English**: How can you receive messages on the main thread using Handler and Looper?

## Answer (EN)
In Android, to handle messages on the main thread, use **Handler** and **Looper**:

1. Create a **Handler** bound to the main thread's **Looper** via `Looper.getMainLooper()`
2. Override **`handleMessage()`** to process messages
3. Send messages/tasks from any thread using **`sendMessage()`** or **`post()`**

---

## Handler and Looper Overview

### What is Looper?

**Looper** is a message loop that processes messages from a **MessageQueue** in a thread.

- Each thread can have **one Looper**
- The **main thread** has a Looper by default
- Background threads need `Looper.prepare()` to create a Looper

### What is Handler?

**Handler** is used to send and process messages/tasks on a thread with a Looper.

- Bound to a specific **Looper** (and its thread)
- Sends messages: `sendMessage()`, `sendEmptyMessage()`, `post()`
- Processes messages: `handleMessage()` callback

---

## Getting Messages on Main Thread

### Method 1: Handler with Main Looper (Recommended)

Create a Handler bound to the main thread's Looper:

```kotlin
import android.os.Handler
import android.os.Looper
import android.os.Message

class MainActivity : AppCompatActivity() {

    // Handler bound to main thread's Looper
    private val mainHandler = Handler(Looper.getMainLooper()) { message ->
        when (message.what) {
            MSG_UPDATE_UI -> {
                val data = message.obj as String
                textView.text = data
                Log.d("MainActivity", "UI updated: $data")
            }
            MSG_SHOW_TOAST -> {
                Toast.makeText(this, "Task complete!", Toast.LENGTH_SHORT).show()
            }
        }
        true // Return true if message was handled
    }

    companion object {
        const val MSG_UPDATE_UI = 1
        const val MSG_SHOW_TOAST = 2
    }

    private fun performBackgroundTask() {
        Thread {
            // Simulate heavy work
            Thread.sleep(2000)
            val result = "Data from background thread"

            // Send message to main thread
            val message = Message.obtain().apply {
                what = MSG_UPDATE_UI
                obj = result
            }
            mainHandler.sendMessage(message)

            // Or use post() with a Runnable
            mainHandler.post {
                Toast.makeText(this, "Task done!", Toast.LENGTH_SHORT).show()
            }
        }.start()
    }
}
```

---

### Method 2: Handler with Custom Callback

```kotlin
import android.os.Handler
import android.os.Looper
import android.os.Message

class BackgroundTaskManager(private val callback: (String) -> Unit) {

    private val mainHandler = Handler(Looper.getMainLooper()) { message ->
        val result = message.obj as String
        callback(result) // Invoke callback on main thread
        true
    }

    fun executeTask() {
        Thread {
            // Background work
            Thread.sleep(1500)
            val data = "Processed data"

            // Send to main thread
            val message = Message.obtain().apply {
                obj = data
            }
            mainHandler.sendMessage(message)
        }.start()
    }
}

// Usage
class MainActivity : AppCompatActivity() {

    private val taskManager = BackgroundTaskManager { result ->
        // This runs on main thread
        textView.text = result
        progressBar.visibility = View.GONE
    }

    private fun startTask() {
        progressBar.visibility = View.VISIBLE
        taskManager.executeTask()
    }
}
```

---

### Method 3: Using `post()` for Simple Tasks

For simple UI updates, use `Handler.post()`:

```kotlin
import android.os.Handler
import android.os.Looper

class DataLoader {

    private val mainHandler = Handler(Looper.getMainLooper())

    fun loadData(onResult: (List<String>) -> Unit) {
        Thread {
            // Simulate network request
            Thread.sleep(2000)
            val data = listOf("Item 1", "Item 2", "Item 3")

            // Post to main thread
            mainHandler.post {
                onResult(data)
            }
        }.start()
    }
}

// Usage
class MainActivity : AppCompatActivity() {

    private val dataLoader = DataLoader()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        dataLoader.loadData { items ->
            // This runs on main thread
            recyclerView.adapter = MyAdapter(items)
        }
    }
}
```

---

## Sending Messages from Background Thread

### Using `sendMessage()`

```kotlin
import android.os.Handler
import android.os.Looper
import android.os.Message

class MainActivity : AppCompatActivity() {

    private val mainHandler = object : Handler(Looper.getMainLooper()) {
        override fun handleMessage(msg: Message) {
            when (msg.what) {
                MSG_PROGRESS -> {
                    val progress = msg.arg1
                    progressBar.progress = progress
                }
                MSG_COMPLETE -> {
                    val result = msg.obj as String
                    resultTextView.text = result
                    progressBar.visibility = View.GONE
                }
            }
        }
    }

    companion object {
        const val MSG_PROGRESS = 1
        const val MSG_COMPLETE = 2
    }

    private fun downloadFile() {
        Thread {
            for (i in 0..100 step 10) {
                Thread.sleep(200)

                // Send progress update
                mainHandler.sendMessage(Message.obtain().apply {
                    what = MSG_PROGRESS
                    arg1 = i
                })
            }

            // Send completion
            mainHandler.sendMessage(Message.obtain().apply {
                what = MSG_COMPLETE
                obj = "Download complete!"
            })
        }.start()
    }
}
```

---

### Using `sendEmptyMessage()`

For messages without data:

```kotlin
private val mainHandler = object : Handler(Looper.getMainLooper()) {
    override fun handleMessage(msg: Message) {
        when (msg.what) {
            MSG_REFRESH -> refreshUI()
            MSG_CLEAR -> clearData()
        }
    }
}

// From background thread
mainHandler.sendEmptyMessage(MSG_REFRESH)
```

---

### Using `postDelayed()`

Execute a task after a delay:

```kotlin
private val mainHandler = Handler(Looper.getMainLooper())

// Post delayed task (runs on main thread after 3 seconds)
mainHandler.postDelayed({
    Toast.makeText(this, "3 seconds elapsed", Toast.LENGTH_SHORT).show()
}, 3000)

// Cancel pending tasks
mainHandler.removeCallbacksAndMessages(null)
```

---

## Complete Example: Image Loader

```kotlin
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.os.Handler
import android.os.Looper
import android.os.Message
import android.widget.ImageView
import java.net.URL

class ImageLoader {

    private val mainHandler = Handler(Looper.getMainLooper()) { message ->
        val bitmap = message.obj as Bitmap
        val imageView = message.data.getParcelable<ImageView>("imageView")
        imageView?.setImageBitmap(bitmap)
        true
    }

    fun loadImage(url: String, imageView: ImageView) {
        Thread {
            try {
                // Download image (blocking operation)
                val inputStream = URL(url).openStream()
                val bitmap = BitmapFactory.decodeStream(inputStream)

                // Send to main thread
                val message = Message.obtain().apply {
                    obj = bitmap
                    data = Bundle().apply {
                        putParcelable("imageView", imageView)
                    }
                }
                mainHandler.sendMessage(message)

            } catch (e: Exception) {
                e.printStackTrace()
            }
        }.start()
    }
}

// Usage
class MainActivity : AppCompatActivity() {

    private val imageLoader = ImageLoader()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val imageView = findViewById<ImageView>(R.id.imageView)
        imageLoader.loadImage("https://example.com/image.jpg", imageView)
    }
}
```

---

## Handler Vs Coroutines (Modern Approach)

### Handler Approach (Traditional)

```kotlin
private val mainHandler = Handler(Looper.getMainLooper())

fun loadData() {
    Thread {
        val data = fetchDataFromNetwork()
        mainHandler.post {
            updateUI(data)
        }
    }.start()
}
```

### Coroutines Approach (Recommended)

```kotlin
import kotlinx.coroutines.*

fun loadData() {
    CoroutineScope(Dispatchers.IO).launch {
        val data = fetchDataFromNetwork()
        withContext(Dispatchers.Main) {
            updateUI(data)
        }
    }
}
```

**Why Coroutines?**
- Cleaner syntax
- Built-in cancellation
- Better error handling
- Structured concurrency

---

## Memory Leak Prevention

### Problem: Handler with Anonymous Inner Class

```kotlin
// BAD: Potential memory leak
class MainActivity : AppCompatActivity() {

    private val handler = object : Handler(Looper.getMainLooper()) {
        override fun handleMessage(msg: Message) {
            // This holds implicit reference to MainActivity
            textView.text = "Updated"
        }
    }
}
```

**Issue:** If messages are pending when Activity is destroyed, Handler holds reference to Activity → memory leak.

### Solution 1: WeakReference

```kotlin
// GOOD: Use WeakReference
class MainActivity : AppCompatActivity() {

    private val handler = MyHandler(this)

    class MyHandler(activity: MainActivity) : Handler(Looper.getMainLooper()) {
        private val activityRef = WeakReference(activity)

        override fun handleMessage(msg: Message) {
            activityRef.get()?.let { activity ->
                activity.textView.text = "Updated"
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacksAndMessages(null) // Clear pending messages
    }
}
```

### Solution 2: Remove Callbacks in onDestroy

```kotlin
// GOOD: Clean up in lifecycle
class MainActivity : AppCompatActivity() {

    private val mainHandler = Handler(Looper.getMainLooper())

    override fun onDestroy() {
        super.onDestroy()
        mainHandler.removeCallbacksAndMessages(null)
    }
}
```

---

## Summary

**How to receive messages on main thread:**

1. Create Handler bound to main thread:
   ```kotlin
   val mainHandler = Handler(Looper.getMainLooper())
   ```

2. Send messages from any thread:
   ```kotlin
   // Using sendMessage()
   mainHandler.sendMessage(Message.obtain().apply {
       what = MSG_ID
       obj = data
   })

   // Using post()
   mainHandler.post {
       updateUI(data)
   }
   ```

3. Process messages in `handleMessage()`:
   ```kotlin
   override fun handleMessage(msg: Message) {
       when (msg.what) {
           MSG_UPDATE -> updateUI(msg.obj)
       }
   }
   ```

**Key points:**
- **Main thread** has Looper by default (no `Looper.prepare()` needed)
- **`Looper.getMainLooper()`** returns main thread's Looper
- **Handler** sends messages to the thread it's bound to
- **`post()`** executes Runnable on Handler's thread
- **Always clean up** pending messages in `onDestroy()`

**Modern alternatives:**
- Use **Kotlin Coroutines** with `withContext(Dispatchers.Main)`
- Use **LiveData** for reactive UI updates
- Use **Flow** with `.flowOn(Dispatchers.Main)`

---

## Ответ (RU)
В Android для обработки сообщений на главном потоке используют **Handler** и **Looper**:

1. Создайте **Handler**, привязанный к Looper главного потока через `Looper.getMainLooper()`
2. Переопределите **`handleMessage()`** для обработки сообщений
3. Отправляйте сообщения/задачи из любого потока с помощью **`sendMessage()`** или **`post()`**

**Пример:**

```kotlin
// Создание Handler для главного потока
private val mainHandler = Handler(Looper.getMainLooper()) { message ->
    when (message.what) {
        MSG_UPDATE_UI -> {
            val data = message.obj as String
            textView.text = data
        }
    }
    true
}

// Отправка из фонового потока
Thread {
    val result = doBackgroundWork()
    mainHandler.sendMessage(Message.obtain().apply {
        what = MSG_UPDATE_UI
        obj = result
    })
}.start()
```

**Важно:**
- `Looper.getMainLooper()` возвращает Looper главного потока
- `post()` выполняет Runnable на потоке Handler
- Всегда очищайте pending сообщения в `onDestroy()`: `handler.removeCallbacksAndMessages(null)`

**Современные альтернативы:**
- Kotlin Coroutines с `withContext(Dispatchers.Main)`
- LiveData для реактивного обновления UI
- Flow с `.flowOn(Dispatchers.Main)`

## Related Questions

- [[q-what-is-the-layout-called-where-objects-can-overlay-each-other--android--easy]]
- q-koin-vs-hilt-comparison--dependency-injection--medium
- [[q-offline-first-architecture--android--hard]]
