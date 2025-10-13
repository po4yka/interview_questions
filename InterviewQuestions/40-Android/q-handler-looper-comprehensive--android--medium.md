---
topic: android
tags:
  - android
  - handler
  - looper
  - threading
  - message-queue
  - concurrency
difficulty: medium
status: draft
---

# Handler and Looper: Complete guide

**Russian**: Handler и Looper: Полное руководство

**English**: Handler and Looper: Complete guide to Android message threading

## Answer (EN)
Handler и Looper — это фундаментальные компоненты Android для организации межпоточного взаимодействия и обработки сообщений в очереди.

### 1. Архитектура Handler-Looper-MessageQueue

```
Thread
   Looper
       MessageQueue
           Message / Runnable

Handler (отправляет) → MessageQueue (хранит) → Looper (обрабатывает)
```

```kotlin
// Компоненты
class Thread {
    var looper: Looper? = null  // Один Looper на поток
}

class Looper {
    val messageQueue: MessageQueue  // Очередь сообщений
    val thread: Thread               // Поток владелец
}

class Handler {
    val looper: Looper              // Looper для обработки
    fun handleMessage(msg: Message) // Обработчик
}
```

### 2. Как Looper связывается с потоком

Looper создается и привязывается к потоку через `Looper.prepare()` и `Looper.loop()`.

```kotlin
// Создание потока с Looper
class MyHandlerThread : Thread() {
    lateinit var handler: Handler
        private set

    override fun run() {
        // 1. Создать Looper для этого потока
        Looper.prepare()

        // 2. Создать Handler привязанный к Looper
        handler = object : Handler(Looper.myLooper()!!) {
            override fun handleMessage(msg: Message) {
                // Обработка сообщений в этом потоке
                when (msg.what) {
                    MSG_TASK -> processTask(msg.obj as Task)
                    MSG_CANCEL -> cancelTask()
                }
            }
        }

        // 3. Запустить цикл обработки сообщений (блокирующий вызов!)
        Looper.loop()

        // Код после loop() выполнится только после quit()
        cleanup()
    }

    fun quit() {
        handler.looper.quit()
    }

    companion object {
        const val MSG_TASK = 1
        const val MSG_CANCEL = 2
    }
}

// Использование
val handlerThread = MyHandlerThread()
handlerThread.start()

// Подождать пока Handler будет готов
while (!::handler.isInitialized) {
    Thread.sleep(10)
}

// Отправить сообщение из другого потока
handlerThread.handler.sendMessage(
    Message.obtain().apply {
        what = MyHandlerThread.MSG_TASK
        obj = Task("Download file")
    }
)
```

**Важно**:
- `Looper.prepare()` создает Looper и сохраняет его в `ThreadLocal`
- `Looper.loop()` — бесконечный цикл, блокирует поток
- Один поток → один Looper → один MessageQueue

### 3. Проверка наличия Looper в потоке

```kotlin
// Проверка есть ли Looper в текущем потоке
fun checkLooper() {
    val looper = Looper.myLooper()

    if (looper != null) {
        println("Looper exists in ${Thread.currentThread().name}")
        println("Is main looper: ${looper == Looper.getMainLooper()}")
    } else {
        println("No looper in ${Thread.currentThread().name}")
    }
}

// Использование
fun demonstrateLooperCheck() {
    // Main thread - всегда имеет Looper
    checkLooper()  // "Looper exists in main"

    // Обычный поток - нет Looper
    Thread {
        checkLooper()  // "No looper in Thread-1"
    }.start()

    // HandlerThread - имеет Looper
    val handlerThread = HandlerThread("MyThread")
    handlerThread.start()

    handlerThread.looper.queue.addIdleHandler {
        checkLooper()  // "Looper exists in MyThread"
        false
    }
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

// Проверка main thread
fun isMainThread(): Boolean {
    return Looper.myLooper() == Looper.getMainLooper()
}
```

### 4. Получение сообщений на главном потоке

#### Способ 1: Handler с Main Looper

```kotlin
class BackgroundTask {
    // Handler привязан к main thread
    private val mainHandler = Handler(Looper.getMainLooper())

    fun executeTask() {
        Thread {
            // Фоновая работа
            val result = performHeavyOperation()

            // Отправить результат в main thread
            mainHandler.post {
                // Выполнится в main thread
                updateUI(result)
            }
        }.start()
    }

    fun performHeavyOperation(): String {
        Thread.sleep(2000)
        return "Task completed"
    }

    fun updateUI(result: String) {
        // Обновление UI в main thread
        println("UI update: $result on ${Thread.currentThread().name}")
    }
}
```

#### Способ 2: sendMessage

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
                // Фоновая обработка
                val processed = processData(data)

                // Отправить в main thread
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

#### Способ 3: postDelayed

```kotlin
class NotificationManager {
    private val handler = Handler(Looper.getMainLooper())

    fun showDelayedNotification(message: String, delayMs: Long) {
        handler.postDelayed({
            // Выполнится в main thread через delayMs
            showNotification(message)
        }, delayMs)
    }

    fun scheduleRepeatingTask(intervalMs: Long) {
        val runnable = object : Runnable {
            override fun run() {
                performTask()
                // Запланировать следующий запуск
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

### 5. HandlerThread - готовое решение

Android предоставляет `HandlerThread` — поток с встроенным Looper.

```kotlin
class ImageProcessor {
    private val handlerThread = HandlerThread("ImageProcessor").apply {
        start()
    }

    private val backgroundHandler = Handler(handlerThread.looper)
    private val mainHandler = Handler(Looper.getMainLooper())

    fun processImage(imageUrl: String, callback: (Bitmap) -> Unit) {
        // Обработка в фоновом потоке
        backgroundHandler.post {
            val bitmap = downloadAndProcessImage(imageUrl)

            // Вернуть результат в main thread
            mainHandler.post {
                callback(bitmap)
            }
        }
    }

    private fun downloadAndProcessImage(url: String): Bitmap {
        // Тяжелая операция
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
    // Выполнится в main thread
    imageView.setImageBitmap(bitmap)
}
```

### 6. Message и Runnable

```kotlin
// Runnable - простые задачи
handler.post {
    // Выполнить код
}

// Message - с данными и идентификатором
val message = Message.obtain().apply {
    what = MSG_DOWNLOAD_COMPLETE
    arg1 = 100  // progress
    arg2 = 200  // total
    obj = "file.pdf"  // любой объект
}
handler.sendMessage(message)

// Message.obtain() - переиспользует объекты из пула
val msg1 = Message.obtain()  // Взять из пула
val msg2 = Message.obtain(handler, MSG_UPDATE)  // С handler и what
val msg3 = Message.obtain(handler, MSG_DATA, data)  // С данными

// ВАЖНО: Не создавать через конструктор!
// val wrong = Message()  // НЕПРАВИЛЬНО
// val correct = Message.obtain()  //  ПРАВИЛЬНО
```

### 7. Управление очередью сообщений

```kotlin
class TaskQueue {
    private val handler = Handler(Looper.getMainLooper())

    fun enqueueTasks() {
        // Добавить задачу
        handler.post { task1() }

        // Добавить с задержкой
        handler.postDelayed({ task2() }, 1000)

        // Добавить в начало очереди
        handler.postAtFrontOfQueue { urgentTask() }

        // Добавить в определенное время
        handler.postAtTime({ scheduledTask() }, SystemClock.uptimeMillis() + 5000)

        // Отправить Message
        val msg = Message.obtain(handler, MSG_PROCESS)
        handler.sendMessage(msg)

        // Отправить Message с задержкой
        handler.sendMessageDelayed(msg, 2000)
    }

    fun cancelTasks() {
        // Удалить все Runnable
        handler.removeCallbacksAndMessages(null)

        // Удалить конкретный Runnable
        val myRunnable = Runnable { }
        handler.removeCallbacks(myRunnable)

        // Удалить сообщения определенного типа
        handler.removeMessages(MSG_PROCESS)
    }

    fun checkQueue() {
        // Проверить есть ли pending сообщения
        val hasPending = handler.hasMessages(MSG_PROCESS)
        println("Has pending messages: $hasPending")
    }

    companion object {
        const val MSG_PROCESS = 1
    }
}
```

### 8. IdleHandler - выполнение когда очередь пуста

```kotlin
class IdleMonitor {
    private val handler = Handler(Looper.getMainLooper())

    fun setupIdleHandler() {
        Looper.myQueue()?.addIdleHandler {
            // Выполнится когда MessageQueue пуста
            println("Queue is idle, performing maintenance...")
            performMaintenance()

            // return true - оставить IdleHandler
            // return false - удалить IdleHandler после выполнения
            false
        }
    }

    fun oneTimeIdleTask(task: () -> Unit) {
        Looper.myQueue()?.addIdleHandler {
            task()
            false  // Выполнить один раз
        }
    }

    private fun performMaintenance() {
        // Cleanup, cache clearing, etc.
    }
}

// Использование для отложенной инициализации
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Критичные задачи сразу
        setupCriticalUI()

        // Некритичные задачи когда UI свободен
        Looper.myQueue()?.addIdleHandler {
            initializeAnalytics()
            loadNonCriticalData()
            false
        }
    }
}
```

### 9. Утечки памяти и очистка

```kotlin
// УТЕЧКА ПАМЯТИ
class LeakyActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Handler держит ссылку на Activity!
        handler.postDelayed({
            updateUI()  // Activity может быть уничтожена
        }, 10000)
    }
}

//  ПРАВИЛЬНО - static Handler + WeakReference
class SafeActivity : AppCompatActivity() {

    private val handler = SafeHandler(this)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        handler.postDelayed({
            updateUI()
        }, 10000)
    }

    override fun onDestroy() {
        super.onDestroy()
        // Отменить все pending задачи
        handler.removeCallbacksAndMessages(null)
    }

    private fun updateUI() {
        // Update UI
    }

    private class SafeHandler(activity: SafeActivity) : Handler(Looper.getMainLooper()) {
        private val activityRef = WeakReference(activity)

        override fun handleMessage(msg: Message) {
            activityRef.get()?.let { activity ->
                // Activity еще жива
                when (msg.what) {
                    MSG_UPDATE -> activity.updateUI()
                }
            }
        }

        companion object {
            const val MSG_UPDATE = 1
        }
    }
}

//  АЛЬТЕРНАТИВА - Lifecycle-aware подход
class ModernActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

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

### 10. Продвинутые техники

```kotlin
// Barrier Messages - блокируют выполнение async сообщений
handler.postSyncBarrier()  // Начать барьер
handler.removeSyncBarrier(token)  // Убрать барьер

// Async Messages - выполняются даже при барьере
val msg = Message.obtain()
msg.setAsynchronous(true)
handler.sendMessage(msg)

// Token для группировки сообщений
val token = Any()
handler.post(token) { task1() }
handler.post(token) { task2() }
// Удалить все по token
handler.removeCallbacksAndMessages(token)

// MessageQueue monitoring
Looper.getMainLooper().setMessageLogging { log ->
    if (log.startsWith(">>>>> Dispatching")) {
        // Сообщение начало обработку
    } else if (log.startsWith("<<<<< Finished")) {
        // Сообщение завершило обработку
    }
}
```

### Сравнительная таблица

| Компонент | Назначение | Количество на поток |
|-----------|------------|---------------------|
| **Looper** | Цикл обработки сообщений | 1 |
| **MessageQueue** | Очередь сообщений | 1 (внутри Looper) |
| **Handler** | Отправка/обработка сообщений | Много |
| **Message** | Данные для передачи | Много |

### Best Practices

1. **Всегда очищать Handler при onDestroy()**
   ```kotlin
   handler.removeCallbacksAndMessages(null)
   ```

2. **Использовать WeakReference для Activity/Fragment**
   ```kotlin
   private val activityRef = WeakReference(activity)
   ```

3. **Предпочитать HandlerThread обычным Thread**
   ```kotlin
   val handlerThread = HandlerThread("Background")
   ```

4. **Использовать Message.obtain() вместо конструктора**
   ```kotlin
   val msg = Message.obtain()  // Переиспользование
   ```

5. **Проверять Lifecycle перед UI обновлениями**
   ```kotlin
   if (lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)) {
       updateUI()
   }
   ```

**English**: **Handler** sends messages, **Looper** processes them in a loop, **MessageQueue** stores them. Looper attaches to thread via `Looper.prepare()` and `Looper.loop()`. Check looper exists with `Looper.myLooper()`. Send messages to main thread: `Handler(Looper.getMainLooper()).post { }`. Use `HandlerThread` for background processing. Always clean up handlers in `onDestroy()` to prevent leaks. Use `Message.obtain()` for object reuse.
