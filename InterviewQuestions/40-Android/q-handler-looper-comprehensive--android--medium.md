---
id: android-198
title: Handler Looper Comprehensive / Handler и Looper подробно
aliases:
- Handler Looper Comprehensive
- Handler и Looper подробно
topic: android
subtopics:
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
- q-glide-image-loading-internals--android--medium
- q-what-should-you-pay-attention-to-in-order-to-optimize-a-large-list--android--hard
created: 2025-10-15
updated: 2025-11-10
tags:
- android/threads-sync
- concurrency
- difficulty/medium

---

# Вопрос (RU)
> Handler и Looper подробно

# Question (EN)
> Handler Looper Comprehensive

---

## Ответ (RU)

Handler и Looper — это фундаментальные примитивы Android для организации межпоточного взаимодействия и обработки событий через очередь сообщений.

Важные идеи:
- Handler связывает вызывающий код с конкретным Looper/потоком.
- Looper крутит бесконечный цикл и вытаскивает сообщения/задачи из MessageQueue.
- MessageQueue хранит `Message` и `Runnable` с временными метками.

### 1. Handler-Looper-MessageQueue Architecture

```text
Thread
   Looper
       MessageQueue
           Message / Runnable

Handler (отправляет) → MessageQueue (хранит) → Looper (обрабатывает)
```

```kotlin
// Концептуальная схема (НЕ реальная реализация SDK)
class Thread {
    var looper: Looper? = null  // Один Looper на поток
}

class Looper {
    val messageQueue: MessageQueue  // Очередь сообщений
    val thread: Thread              // Поток-владелец
}

class Handler(val looper: Looper) {
    fun handleMessage(msg: Message) { /* ... */ }
}
```

Ключевые ограничения:
- Один поток → максимум один Looper → одна MessageQueue.
- Handler всегда привязан к конкретному Looper (а значит — к конкретному потоку).

### 2. Как Looper привязывается к потоку

Looper создается и привязывается к потоку через `Looper.prepare()` и `Looper.loop()`.

```kotlin
// Пример кастомного потока с собственным Looper
class MyHandlerThread : Thread() {
    lateinit var handler: Handler
        private set

    override fun run() {
        // 1. Создаем Looper для этого потока
        Looper.prepare()

        // 2. Создаем Handler, привязанный к Looper этого потока
        handler = object : Handler(Looper.myLooper()!!) {
            override fun handleMessage(msg: Message) {
                when (msg.what) {
                    MSG_TASK -> processTask(msg.obj as Task)
                    MSG_CANCEL -> cancelTask()
                }
            }
        }

        // 3. Запускаем цикл обработки сообщений (блокирующий вызов!)
        Looper.loop()

        // Код здесь выполнится только после quit()/quitSafely()
        cleanup()
    }

    fun quit() {
        // Останавливает Looper, цикл выйдет из loop()
        handler.looper.quit()
    }

    private fun processTask(task: Task) { /* ... */ }
    private fun cancelTask() { /* ... */ }
    private fun cleanup() { /* ... */ }

    companion object {
        const val MSG_TASK = 1
        const val MSG_CANCEL = 2
    }
}

// Использование
val myThread = MyHandlerThread()
myThread.start()

// Ждем инициализации handler (упрощённый пример, в реальном коде лучше использовать синхронизацию)
while (!::myThread.isInitialized) {
    Thread.sleep(10)
}

myThread.handler.sendMessage(
    Message.obtain().apply {
        what = MyHandlerThread.MSG_TASK
        obj = Task("Download file")
    }
)
```

Важно:
- `Looper.prepare()` создает Looper и сохраняет его в `ThreadLocal` текущего потока.
- `Looper.loop()` — бесконечный цикл чтения/диспетчеризации сообщений из очереди; блокирует поток.
- В большинстве случаев вместо ручного `Thread + Looper` следует использовать `HandlerThread`.

### 3. Проверка наличия Looper в потоке

```kotlin
fun checkLooper() {
    val looper = Looper.myLooper()

    if (looper != null) {
        println("Looper exists in ${Thread.currentThread().name}")
        println("Is main looper: ${looper == Looper.getMainLooper()}")
    } else {
        println("No looper in ${Thread.currentThread().name}")
    }
}

fun demonstrateLooperCheck() {
    // В нормальном Android-приложении главный поток имеет Looper
    checkLooper()  // Ожидаемо: "Looper exists in main"

    // Обычный Thread по умолчанию не имеет Looper
    Thread {
        checkLooper()  // "No looper in Thread-1"
    }.start()

    // HandlerThread автоматически создает Looper
    val handlerThread = HandlerThread("MyThread")
    handlerThread.start()

    // После старта looper доступен
    val looper = handlerThread.looper
    println("Looper exists in ${looper.thread.name}")
}

// Безопасное создание Handler
fun createHandlerSafely(): Handler? {
    val looper = Looper.myLooper()
    return if (looper != null) {
        Handler(looper)
    } else {
        Log.e("Handler", "Cannot create Handler, no Looper in thread")
        null
    }
}

fun isMainThread(): Boolean {
    return Looper.myLooper() == Looper.getMainLooper()
}
```

### 4. Получение сообщений в главном потоке

#### Метод 1: Handler с main Looper

```kotlin
class BackgroundTask {
    // Handler, привязанный к главному потоку
    private val mainHandler = Handler(Looper.getMainLooper())

    fun executeTask() {
        Thread {
            val result = performHeavyOperation()

            // Передаем результат в главный поток
            mainHandler.post {
                updateUI(result)
            }
        }.start()
    }

    private fun performHeavyOperation(): String {
        Thread.sleep(2000)
        return "Task completed"
    }

    private fun updateUI(result: String) {
        println("UI update: $result on ${Thread.currentThread().name}")
    }
}
```

#### Метод 2: sendMessage

```kotlin
class DataProcessor : Handler(Looper.getMainLooper()) {

    override fun handleMessage(msg: Message) {
        when (msg.what) {
            MSG_UPDATE -> {
                val data = msg.obj as String
                updateUI(data)
            }
            MSG_ERROR -> {
                val error = msg.obj as Exception
                showError(error)
            }
        }
    }

    fun processDataInBackground(data: String) {
        Thread {
            try {
                val processed = processData(data)
                val message = obtainMessage(MSG_UPDATE, processed)
                sendMessage(message)
            } catch (e: Exception) {
                val errorMsg = obtainMessage(MSG_ERROR, e)
                sendMessage(errorMsg)
            }
        }.start()
    }

    private fun processData(data: String): String {
        Thread.sleep(1000)
        return data.uppercase()
    }

    private fun updateUI(data: String) {
        println("UI updated: $data")
    }

    private fun showError(error: Exception) {
        println("Error: ${error.message}")
    }

    companion object {
        const val MSG_UPDATE = 1
        const val MSG_ERROR = 2
    }
}

// Использование
val processor = DataProcessor()
processor.processDataInBackground("hello world")
```

#### Метод 3: postDelayed

```kotlin
class NotificationManager {
    private val handler = Handler(Looper.getMainLooper())

    fun showDelayedNotification(message: String, delayMs: Long) {
        handler.postDelayed({
            showNotification(message)
        }, delayMs)
    }

    fun scheduleRepeatingTask(intervalMs: Long) {
        val runnable = object : Runnable {
            override fun run() {
                performTask()
                handler.postDelayed(this, intervalMs)
            }
        }
        handler.post(runnable)
    }

    fun cancelAllTasks() {
        handler.removeCallbacksAndMessages(null)
    }

    private fun showNotification(message: String) {
        println("Notification: $message")
    }

    private fun performTask() {
        println("Task executed at ${System.currentTimeMillis()}")
    }
}
```

### 5. HandlerThread — готовое решение

```kotlin
class ImageProcessor {
    private val handlerThread = HandlerThread("ImageProcessor").apply { start() }

    private val backgroundHandler = Handler(handlerThread.looper)
    private val mainHandler = Handler(Looper.getMainLooper())

    fun processImage(imageUrl: String, callback: (Bitmap) -> Unit) {
        backgroundHandler.post {
            val bitmap = downloadAndProcessImage(imageUrl)

            mainHandler.post {
                callback(bitmap)
            }
        }
    }

    private fun downloadAndProcessImage(url: String): Bitmap {
        Thread.sleep(1000)
        return Bitmap.createBitmap(100, 100, Bitmap.Config.ARGB_8888)
    }

    fun shutdown() {
        handlerThread.quitSafely()
    }
}

// Использование
val processor = ImageProcessor()
processor.processImage("https://example.com/image.jpg") { bitmap ->
    imageView.setImageBitmap(bitmap)
}
```

### 6. Message и Runnable

```kotlin
// Runnable — простые задачи без явных полей Message
handler.post {
    // Выполнить код
}

// Message — с идентификатором и данными
val message = Message.obtain().apply {
    what = MSG_DOWNLOAD_COMPLETE
    arg1 = 100
    arg2 = 200
    obj = "file.pdf"
}
handler.sendMessage(message)

// Message.obtain() — переиспользует объекты из пула
val msg1 = Message.obtain()
val msg2 = Message.obtain(handler, MSG_UPDATE)
val msg3 = Message.obtain(handler, MSG_DATA, data)

// Рекомендуется избегать прямого конструктора
// val wrong = Message()       // Нежелательно
// val correct = Message.obtain()
```

### 7. Управление очередью сообщений

```kotlin
class TaskQueue {
    private val handler = Handler(Looper.getMainLooper())

    fun enqueueTasks() {
        handler.post { task1() }
        handler.postDelayed({ task2() }, 1000)
        handler.postAtFrontOfQueue { urgentTask() }
        handler.postAtTime({ scheduledTask() }, SystemClock.uptimeMillis() + 5000)

        val msg = Message.obtain(handler, MSG_PROCESS)
        handler.sendMessage(msg)
        handler.sendMessageDelayed(Message.obtain(handler, MSG_PROCESS), 2000)
    }

    fun cancelTasks() {
        handler.removeCallbacksAndMessages(null)

        val myRunnable = Runnable { }
        handler.removeCallbacks(myRunnable)

        handler.removeMessages(MSG_PROCESS)
    }

    fun checkQueue() {
        val hasPending = handler.hasMessages(MSG_PROCESS)
        println("Has pending messages: $hasPending")
    }

    private fun task1() { /* ... */ }
    private fun task2() { /* ... */ }
    private fun urgentTask() { /* ... */ }
    private fun scheduledTask() { /* ... */ }

    companion object {
        const val MSG_PROCESS = 1
    }
}
```

### 8. IdleHandler — выполнение, когда очередь пуста

```kotlin
class IdleMonitor {
    private val mainQueue = Looper.getMainLooper().queue

    fun setupIdleHandler() {
        mainQueue.addIdleHandler {
            // Выполнится когда MessageQueue становится idle
            println("Queue is idle, performing maintenance...")
            performMaintenance()
            false
        }
    }

    fun oneTimeIdleTask(task: () -> Unit) {
        mainQueue.addIdleHandler {
            task()
            false // Выполнить один раз
        }
    }

    private fun performMaintenance() {
        // Cleanup, cache clearing, etc.
    }
}
```

```kotlin
// Использование для отложенной инициализации
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        setupCriticalUI()

        Looper.getMainLooper().queue.addIdleHandler {
            initializeAnalytics()
            loadNonCriticalData()
            false
        }
    }

    private fun setupCriticalUI() { /* ... */ }
    private fun initializeAnalytics() { /* ... */ }
    private fun loadNonCriticalData() { /* ... */ }
}
```

### 9. Утечки памяти и очистка

```kotlin
// Потенциальная утечка, если задачи живут дольше Activity
class LeakyActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        handler.postDelayed({
            updateUI() // Activity может быть уже уничтожена
        }, 10000)
    }

    private fun updateUI() { /* ... */ }
}
```

```kotlin
// Безопаснее — static/inner class + WeakReference + очистка
class SafeActivity : AppCompatActivity() {

    private val handler = SafeHandler(this)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        handler.postDelayed({
            handler.sendEmptyMessage(SafeHandler.MSG_UPDATE)
        }, 10000)
    }

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacksAndMessages(null)
    }

    private fun updateUI() {
        // Update UI
    }

    private class SafeHandler(activity: SafeActivity) : Handler(Looper.getMainLooper()) {
        private val activityRef = WeakReference(activity)

        override fun handleMessage(msg: Message) {
            val activity = activityRef.get() ?: return
            when (msg.what) {
                MSG_UPDATE -> activity.updateUI()
            }
        }

        companion object {
            const val MSG_UPDATE = 1
        }
    }
}
```

```kotlin
// Альтернатива — lifecycle-aware подход (Kotlin coroutines)
class ModernActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            delay(10000)
            if (lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)) {
                updateUI()
            }
        }
    }

    private fun updateUI() {
        // Update UI
    }
}
```

### 10. Advanced Techniques (для полноты, с пометкой об ограничениях)

Некоторые возможности доступны через скрытые/внутренние API и не предназначены для прямого использования в прикладном коде. Ниже — концепции, а не призыв использовать эти методы напрямую:

```kotlin
// Async Messages: можно помечать сообщения как асинхронные
val asyncMsg = Message.obtain().apply {
    setAsynchronous(true)
}
handler.sendMessage(asyncMsg)

// Группировка и удаление по token поддерживается только для удаления:
val token = Any()

val r1 = Runnable { task1() }
val r2 = Runnable { task2() }

handler.post(r1)
handler.post(r2)

// Позже можно удалить callbacks/сообщения, ассоциированные с token
handler.removeCallbacksAndMessages(token)

// Мониторинг очереди сообщений главного потока
Looper.getMainLooper().setMessageLogging { log ->
    if (log.startsWith(">>>>> Dispatching")) {
        // Сообщение начало обработку
    } else if (log.startsWith("<<<<< Finished")) {
        // Сообщение завершило обработку
    }
}
```

(Методы sync barrier в Handler/MessageQueue — внутренние и не должны использоваться в production-коде без полной осознанности рисков и ограничений.)

### Сравнение компонентов

| Компонент | Назначение                 | Количество на поток |
|----------|----------------------------|---------------------|
| Looper   | Цикл обработки сообщений   | 1                   |
| MessageQueue | Очередь сообщений      | 1 (у Looper)        |
| Handler  | Отправка/обработка сообщений | Много             |
| Message  | Контейнер данных/события  | Много               |

### Best Practices

1. Очищать Handler в onDestroy()/onCleared(), если он может жить дольше компонента.
   ```kotlin
   handler.removeCallbacksAndMessages(null)
   ```
2. Не держать сильные ссылки на `Activity`/`Fragment`/`Context` в длительно живущих Handler- callback'ах; использовать WeakReference или lifecycle-aware решения.
3. Для фоновых задач предпочтительнее `HandlerThread` или современные средства (Executors, coroutines), чем вручную созданный `Thread` с Looper.
4. Использовать `Message.obtain()` вместо прямого конструктора для переиспользования объектов.
5. Проверять lifecycle перед обновлением UI из отложенных задач.

---

## Answer (EN)

Handler and Looper are fundamental Android primitives for thread-confined, message-based execution and inter-thread communication.

Key ideas:
- A Handler binds calling code to a specific Looper/thread.
- A Looper runs an infinite loop pulling messages/tasks from its MessageQueue.
- MessageQueue stores `Message` and `Runnable` instances with timestamps.

### 1. Handler-Looper-MessageQueue Architecture

```text
Thread
   Looper
       MessageQueue
           Message / Runnable

Handler (sender) → MessageQueue (stores) → Looper (dispatches)
```

```kotlin
// Conceptual model (NOT the exact SDK impl)
class Thread {
    var looper: Looper? = null  // One Looper per thread
}

class Looper {
    val messageQueue: MessageQueue  // Message queue
    val thread: Thread              // Owning thread
}

class Handler(val looper: Looper) {
    fun handleMessage(msg: Message) { /* ... */ }
}
```

Constraints:
- One thread → at most one Looper → one MessageQueue.
- A Handler is always bound to a particular Looper (and thus a specific thread).

### 2. How a Looper is bound to a thread

A Looper is created and attached to a thread via `Looper.prepare()` and `Looper.loop()`.

```kotlin
// Custom thread with its own Looper
class MyHandlerThread : Thread() {
    lateinit var handler: Handler
        private set

    override fun run() {
        Looper.prepare()

        handler = object : Handler(Looper.myLooper()!!) {
            override fun handleMessage(msg: Message) {
                when (msg.what) {
                    MSG_TASK -> processTask(msg.obj as Task)
                    MSG_CANCEL -> cancelTask()
                }
            }
        }

        // Blocking message loop
        Looper.loop()

        // Executes after quit()/quitSafely()
        cleanup()
    }

    fun quit() {
        handler.looper.quit()
    }

    private fun processTask(task: Task) { /* ... */ }
    private fun cancelTask() { /* ... */ }
    private fun cleanup() { /* ... */ }

    companion object {
        const val MSG_TASK = 1
        const val MSG_CANCEL = 2
    }
}

// Usage
val myThread = MyHandlerThread()
myThread.start()

while (!::myThread.isInitialized) {
    Thread.sleep(10)
}

myThread.handler.sendMessage(
    Message.obtain().apply {
        what = MyHandlerThread.MSG_TASK
        obj = Task("Download file")
    }
)
```

Notes:
- `Looper.prepare()` creates and stores the Looper in the current thread's `ThreadLocal`.
- `Looper.loop()` is a blocking loop that reads/dispatches messages from the queue.
- In practice, prefer `HandlerThread` over manually wiring `Thread + Looper`.

### 3. Checking for a Looper in the current thread

```kotlin
fun checkLooper() {
    val looper = Looper.myLooper()

    if (looper != null) {
        println("Looper exists in ${Thread.currentThread().name}")
        println("Is main looper: ${looper == Looper.getMainLooper()}")
    } else {
        println("No looper in ${Thread.currentThread().name}")
    }
}

fun demonstrateLooperCheck() {
    // Main thread in Android normally has a Looper
    checkLooper()

    // Regular Thread has no Looper by default
    Thread {
        checkLooper()
    }.start()

    // HandlerThread creates Looper automatically
    val handlerThread = HandlerThread("MyThread")
    handlerThread.start()

    val looper = handlerThread.looper
    println("Looper exists in ${looper.thread.name}")
}

fun createHandlerSafely(): Handler? {
    val looper = Looper.myLooper()
    return if (looper != null) {
        Handler(looper)
    } else {
        Log.e("Handler", "Cannot create Handler, no Looper in thread")
        null
    }
}

fun isMainThread(): Boolean {
    return Looper.myLooper() == Looper.getMainLooper()
}
```

### 4. Receiving and posting work on the main thread

#### Method 1: Handler with main Looper

```kotlin
class BackgroundTask {
    private val mainHandler = Handler(Looper.getMainLooper())

    fun executeTask() {
        Thread {
            val result = performHeavyOperation()

            mainHandler.post {
                updateUI(result)
            }
        }.start()
    }

    private fun performHeavyOperation(): String {
        Thread.sleep(2000)
        return "Task completed"
    }

    private fun updateUI(result: String) {
        println("UI update: $result on ${Thread.currentThread().name}")
    }
}
```

#### Method 2: `sendMessage`

```kotlin
class DataProcessor : Handler(Looper.getMainLooper()) {

    override fun handleMessage(msg: Message) {
        when (msg.what) {
            MSG_UPDATE -> {
                val data = msg.obj as String
                updateUI(data)
            }
            MSG_ERROR -> {
                val error = msg.obj as Exception
                showError(error)
            }
        }
    }

    fun processDataInBackground(data: String) {
        Thread {
            try {
                val processed = processData(data)
                val message = obtainMessage(MSG_UPDATE, processed)
                sendMessage(message)
            } catch (e: Exception) {
                val errorMsg = obtainMessage(MSG_ERROR, e)
                sendMessage(errorMsg)
            }
        }.start()
    }

    private fun processData(data: String): String {
        Thread.sleep(1000)
        return data.uppercase()
    }

    private fun updateUI(data: String) {
        println("UI updated: $data")
    }

    private fun showError(error: Exception) {
        println("Error: ${error.message}")
    }

    companion object {
        const val MSG_UPDATE = 1
        const val MSG_ERROR = 2
    }
}

// Usage
val processor = DataProcessor()
processor.processDataInBackground("hello world")
```

#### Method 3: `postDelayed`

```kotlin
class NotificationManager {
    private val handler = Handler(Looper.getMainLooper())

    fun showDelayedNotification(message: String, delayMs: Long) {
        handler.postDelayed({
            showNotification(message)
        }, delayMs)
    }

    fun scheduleRepeatingTask(intervalMs: Long) {
        val runnable = object : Runnable {
            override fun run() {
                performTask()
                handler.postDelayed(this, intervalMs)
            }
        }
        handler.post(runnable)
    }

    fun cancelAllTasks() {
        handler.removeCallbacksAndMessages(null)
    }

    private fun showNotification(message: String) {
        println("Notification: $message")
    }

    private fun performTask() {
        println("Task executed at ${System.currentTimeMillis()}")
    }
}
```

### 5. HandlerThread — ready-made solution

```kotlin
class ImageProcessor {
    private val handlerThread = HandlerThread("ImageProcessor").apply { start() }

    private val backgroundHandler = Handler(handlerThread.looper)
    private val mainHandler = Handler(Looper.getMainLooper())

    fun processImage(imageUrl: String, callback: (Bitmap) -> Unit) {
        backgroundHandler.post {
            val bitmap = downloadAndProcessImage(imageUrl)

            mainHandler.post {
                callback(bitmap)
            }
        }
    }

    private fun downloadAndProcessImage(url: String): Bitmap {
        Thread.sleep(1000)
        return Bitmap.createBitmap(100, 100, Bitmap.Config.ARGB_8888)
    }

    fun shutdown() {
        handlerThread.quitSafely()
    }
}

// Usage
val processor = ImageProcessor()
processor.processImage("https://example.com/image.jpg") { bitmap ->
    imageView.setImageBitmap(bitmap)
}
```

### 6. Message vs Runnable

```kotlin
// Runnable — simple fire-and-forget task
handler.post {
    // Execute code
}

// Message — structured event with id and data
val message = Message.obtain().apply {
    what = MSG_DOWNLOAD_COMPLETE
    arg1 = 100
    arg2 = 200
    obj = "file.pdf"
}
handler.sendMessage(message)

// Message.obtain() reuses instances from an internal pool
val msg1 = Message.obtain()
val msg2 = Message.obtain(handler, MSG_UPDATE)
val msg3 = Message.obtain(handler, MSG_DATA, data)

// Prefer obtain() over direct constructor
// val wrong = Message()       // Not recommended
// val correct = Message.obtain()
```

Use:
- `Runnable` for simple tasks when you don't need routing or metadata.
- `Message` when you need `what` codes, args, or pooling.

### 7. Message queue operations

```kotlin
class TaskQueue {
    private val handler = Handler(Looper.getMainLooper())

    fun enqueueTasks() {
        handler.post { task1() }
        handler.postDelayed({ task2() }, 1000)
        handler.postAtFrontOfQueue { urgentTask() }
        handler.postAtTime({ scheduledTask() }, SystemClock.uptimeMillis() + 5000)

        val msg = Message.obtain(handler, MSG_PROCESS)
        handler.sendMessage(msg)
        handler.sendMessageDelayed(Message.obtain(handler, MSG_PROCESS), 2000)
    }

    fun cancelTasks() {
        handler.removeCallbacksAndMessages(null)

        val myRunnable = Runnable { }
        handler.removeCallbacks(myRunnable)

        handler.removeMessages(MSG_PROCESS)
    }

    fun checkQueue() {
        val hasPending = handler.hasMessages(MSG_PROCESS)
        println("Has pending messages: $hasPending")
    }

    private fun task1() { /* ... */ }
    private fun task2() { /* ... */ }
    private fun urgentTask() { /* ... */ }
    private fun scheduledTask() { /* ... */ }

    companion object {
        const val MSG_PROCESS = 1
    }
}
```

This shows how to:
- Enqueue work in different ways (immediate, delayed, front of queue, at specific time).
- Cancel callbacks/messages by `Runnable`, `what`, or all at once.
- Inspect whether certain messages are pending.

### 8. IdleHandler — run work when the queue is idle

```kotlin
class IdleMonitor {
    private val mainQueue = Looper.getMainLooper().queue

    fun setupIdleHandler() {
        mainQueue.addIdleHandler {
            println("Queue is idle, performing maintenance...")
            performMaintenance()
            false
        }
    }

    fun oneTimeIdleTask(task: () -> Unit) {
        mainQueue.addIdleHandler {
            task()
            false // Run once
        }
    }

    private fun performMaintenance() {
        // Cleanup, cache clearing, etc.
    }
}
```

```kotlin
// Deferred initialization example
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        setupCriticalUI()

        Looper.getMainLooper().queue.addIdleHandler {
            initializeAnalytics()
            loadNonCriticalData()
            false
        }
    }

    private fun setupCriticalUI() { /* ... */ }
    private fun initializeAnalytics() { /* ... */ }
    private fun loadNonCriticalData() { /* ... */ }
}
```

Use IdleHandler for:
- Low-priority work.
- Deferred initialization when the main queue is idle.

### 9. Memory leaks and cleanup

```kotlin
// Risky: tasks can outlive Activity
class LeakyActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        handler.postDelayed({
            updateUI() // Activity might be destroyed
        }, 10000)
    }

    private fun updateUI() { /* ... */ }
}
```

```kotlin
// Safer: static/inner handler + WeakReference + cleanup
class SafeActivity : AppCompatActivity() {

    private val handler = SafeHandler(this)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        handler.postDelayed({
            handler.sendEmptyMessage(SafeHandler.MSG_UPDATE)
        }, 10000)
    }

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacksAndMessages(null)
    }

    private fun updateUI() {
        // Update UI
    }

    private class SafeHandler(activity: SafeActivity) : Handler(Looper.getMainLooper()) {
        private val activityRef = WeakReference(activity)

        override fun handleMessage(msg: Message) {
            val activity = activityRef.get() ?: return
            when (msg.what) {
                MSG_UPDATE -> activity.updateUI()
            }
        }

        companion object {
            const val MSG_UPDATE = 1
        }
    }
}
```

```kotlin
// Modern lifecycle-aware alternative with coroutines
class ModernActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            delay(10000)
            if (lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)) {
                updateUI()
            }
        }
    }

    private fun updateUI() {
        // Update UI
    }
}
```

Guidelines:
- Always remove callbacks/messages in `onDestroy`/`onCleared` for long-lived Handlers.
- Avoid implicit strong references from Handlers to Activities/Fragments.
- Prefer lifecycle-aware constructs (e.g., coroutines + `lifecycleScope`).

### 10. Advanced techniques (with caveats)

Conceptual-only; most of this relies on hidden/internal APIs and must be used with caution.

```kotlin
// Asynchronous messages
val asyncMsg = Message.obtain().apply {
    setAsynchronous(true)
}
handler.sendMessage(asyncMsg)

// Token-based removal (supported for removal)
val token = Any()

val r1 = Runnable { task1() }
val r2 = Runnable { task2() }

handler.post(r1)
handler.post(r2)

handler.removeCallbacksAndMessages(token)

// Monitoring main thread message dispatch
Looper.getMainLooper().setMessageLogging { log ->
    if (log.startsWith(">>>>> Dispatching")) {
        // Message started processing
    } else if (log.startsWith("<<<<< Finished")) {
        // Message finished processing
    }
}
```

Note: sync barriers and related internals are not for regular production use unless you fully understand the risks.

### Component comparison

| Component   | Purpose                        | Per thread        |
|------------|--------------------------------|-------------------|
| Looper     | Message processing loop        | 1                 |
| MessageQueue | Holds scheduled messages     | 1 (per Looper)    |
| Handler    | Send/handle messages to Looper | Many              |
| Message    | Data/event container           | Many              |

### Best Practices

1. Clear callbacks/messages in `onDestroy()` / `onCleared()` when a Handler can outlive its owner.
   ```kotlin
   handler.removeCallbacksAndMessages(null)
   ```
2. Avoid strong references from long-lived Handlers to `Activity`/`Fragment`/`Context`; use `WeakReference` or lifecycle-aware APIs.
3. Prefer `HandlerThread` or modern mechanisms (Executors, coroutines) for background work instead of raw `Thread + Looper`.
4. Use `Message.obtain()` for pooling instead of `Message()`.
5. Always ensure you are on the correct thread before updating UI.

---

## Follow-ups

- [[q-glide-image-loading-internals--android--medium]]
- [[q-what-should-you-pay-attention-to-in-order-to-optimize-a-large-list--android--hard]]

## References

- [Threading](https://developer.android.com/guide/background/threading)

## Related Questions

### Prerequisites / Concepts

- [[c-coroutines]]
- [[q-glide-image-loading-internals--android--medium]]
- [[q-what-should-you-pay-attention-to-in-order-to-optimize-a-large-list--android--hard]]
