---
id: "20251015082237391"
title: "Looper Thread Connection / Связь Looper и потока"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [android/concurrency, concurrency, handler, looper, message-queue, threading, difficulty/medium]
---
# Как Looper связывается с потоком?

**English**: How does Looper connect to a thread?

## Answer (EN)
**Looper** connects to a thread using two key methods:

1. **`Looper.prepare()`** - Creates a Looper for the current thread
2. **`Looper.loop()`** - Starts the message processing loop for that thread

---

## Looper Binding Mechanism

### How It Works

```kotlin
// In a background thread
class LooperThread : Thread() {
    override fun run() {
        // 1. Prepare Looper for this thread
        Looper.prepare()

        // 2. Create Handler (will use this thread's Looper)
        val handler = Handler(Looper.myLooper()!!) { message ->
            // Process messages on this thread
            println("Message received: ${message.what}")
            true
        }

        // 3. Start message processing loop
        Looper.loop()
    }
}
```

**Key points:**
- **`Looper.prepare()`** stores Looper in `ThreadLocal<Looper>`
- **One Looper per thread** (calling `prepare()` twice throws exception)
- **Main thread** has Looper prepared automatically
- **`Looper.loop()`** blocks the thread to process messages

---

## Step-by-Step Process

### 1. Looper.prepare()

Creates and stores Looper for current thread:

```kotlin
public static void prepare() {
    prepare(true);
}

private static void prepare(boolean quitAllowed) {
    if (sThreadLocal.get() != null) {
        throw new RuntimeException("Only one Looper may be created per thread");
    }
    sThreadLocal.set(new Looper(quitAllowed));
}
```

**What happens:**
1. Checks if thread already has a Looper (via `ThreadLocal`)
2. If yes → throws exception
3. If no → creates new Looper with MessageQueue
4. Stores Looper in `ThreadLocal<Looper>` for this thread

---

### 2. Looper.loop()

Starts infinite message processing loop:

```kotlin
public static void loop() {
    final Looper me = myLooper();
    if (me == null) {
        throw new RuntimeException("No Looper; Looper.prepare() wasn't called on this thread.");
    }
    final MessageQueue queue = me.mQueue;

    for (;;) {
        Message msg = queue.next(); // Blocks until message available
        if (msg == null) {
            return; // Quit
        }

        msg.target.dispatchMessage(msg); // Deliver to Handler
        msg.recycleUnchecked();
    }
}
```

**What happens:**
1. Retrieves Looper from current thread
2. Gets MessageQueue from Looper
3. Enters infinite loop
4. Blocks on `queue.next()` until message arrives
5. Dispatches message to target Handler
6. Repeats

---

## Complete Example: Custom Looper Thread

### Creating a Background Thread with Looper

```kotlin
import android.os.Handler
import android.os.Looper
import android.os.Message
import java.util.concurrent.CountDownLatch

class WorkerThread(private val name: String) : Thread(name) {

    lateinit var handler: Handler
        private set

    private val latch = CountDownLatch(1)

    override fun run() {
        // 1. Prepare Looper for this thread
        Looper.prepare()

        // 2. Create Handler bound to this thread's Looper
        handler = object : Handler(Looper.myLooper()!!) {
            override fun handleMessage(msg: Message) {
                println("[$name] Processing message: ${msg.what}")

                // Simulate work
                Thread.sleep(1000)

                println("[$name] Message ${msg.what} processed")
            }
        }

        // 3. Signal that Handler is ready
        latch.countDown()

        // 4. Start message loop (blocks here)
        Looper.loop()

        println("[$name] Looper stopped")
    }

    fun waitUntilReady() {
        latch.await()
    }

    fun quit() {
        handler.looper.quit()
    }
}

// Usage
fun main() {
    val workerThread = WorkerThread("Worker-1")
    workerThread.start()
    workerThread.waitUntilReady()

    // Send messages from main thread
    for (i in 1..5) {
        val message = Message.obtain().apply { what = i }
        workerThread.handler.sendMessage(message)
    }

    // Wait and quit
    Thread.sleep(6000)
    workerThread.quit()
}
```

**Output:**
```
[Worker-1] Processing message: 1
[Worker-1] Message 1 processed
[Worker-1] Processing message: 2
[Worker-1] Message 2 processed
...
[Worker-1] Looper stopped
```

---

## Main Thread Looper

The **main thread** has a Looper prepared automatically by `ActivityThread`:

```java
// ActivityThread.java (Android framework)
public static void main(String[] args) {
    ...
    Looper.prepareMainLooper(); // Prepare main thread Looper
    ...
    Looper.loop(); // Start main thread message loop
    ...
}
```

### Accessing Main Thread Looper

```kotlin
import android.os.Handler
import android.os.Looper

// Get main thread Looper
val mainLooper = Looper.getMainLooper()

// Create Handler for main thread (from any thread)
val mainHandler = Handler(mainLooper) { message ->
    // This runs on main thread
    println("Main thread: ${Thread.currentThread().name}")
    true
}

// Send from background thread
Thread {
    mainHandler.sendEmptyMessage(1)
}.start()
```

---

## HandlerThread (Built-in Looper Thread)

Android provides **HandlerThread** - a Thread with Looper already set up:

```kotlin
import android.os.HandlerThread
import android.os.Handler

class MyService {

    private val handlerThread = HandlerThread("MyBackgroundThread")
    private lateinit var backgroundHandler: Handler

    fun start() {
        // Start thread (calls Looper.prepare() and Looper.loop() internally)
        handlerThread.start()

        // Create Handler for this thread
        backgroundHandler = Handler(handlerThread.looper) { message ->
            println("Background work: ${message.what}")
            true
        }
    }

    fun doBackgroundWork(taskId: Int) {
        backgroundHandler.sendEmptyMessage(taskId)
    }

    fun stop() {
        handlerThread.quitSafely() // Stops Looper
    }
}

// Usage
val service = MyService()
service.start()
service.doBackgroundWork(1)
service.doBackgroundWork(2)
Thread.sleep(2000)
service.stop()
```

**Advantages of HandlerThread:**
- No need to call `Looper.prepare()` and `Looper.loop()`
- Thread-safe Looper access via `handlerThread.looper`
- Safe quit methods: `quit()` and `quitSafely()`

---

## Multiple Handlers, One Looper

Multiple Handlers can share the same Looper (and thread):

```kotlin
class MultiHandlerThread : Thread() {

    lateinit var handler1: Handler
    lateinit var handler2: Handler

    override fun run() {
        Looper.prepare()

        val looper = Looper.myLooper()!!

        // Both handlers share the same Looper and thread
        handler1 = Handler(looper) { message ->
            println("Handler1 processing: ${message.what}")
            true
        }

        handler2 = Handler(looper) { message ->
            println("Handler2 processing: ${message.what}")
            true
        }

        Looper.loop()
    }
}

// Usage
val thread = MultiHandlerThread()
thread.start()
Thread.sleep(100) // Wait for Looper to be ready

thread.handler1.sendEmptyMessage(1)
thread.handler2.sendEmptyMessage(2)
```

**Result:** Both handlers' messages are processed **sequentially** on the same thread.

---

## Looper Lifecycle

### Start Looper

```kotlin
class WorkerThread : Thread() {
    override fun run() {
        Looper.prepare()    // Create Looper
        // ... create Handlers ...
        Looper.loop()       // Start processing (blocks)
    }
}
```

### Stop Looper

```kotlin
// Option 1: quit() - Discard pending messages
looper.quit()

// Option 2: quitSafely() - Process pending messages first
looper.quitSafely()
```

**After quitting:**
- `Looper.loop()` exits
- Thread can finish execution
- Pending messages (with `quit()`) are discarded
- Pending messages (with `quitSafely()`) are processed

---

## Common Mistakes

### 1. Calling Looper.prepare() Twice

```kotlin
// - CRASH: RuntimeException
class BadThread : Thread() {
    override fun run() {
        Looper.prepare()
        Looper.prepare() // - Only one Looper per thread!
    }
}
```

### 2. Using Handler Before Looper.prepare()

```kotlin
// - CRASH: RuntimeException
class BadThread : Thread() {
    override fun run() {
        val handler = Handler(Looper.myLooper()!!) // - Looper is null!
        Looper.prepare()
    }
}

// - CORRECT
class GoodThread : Thread() {
    override fun run() {
        Looper.prepare()
        val handler = Handler(Looper.myLooper()!!)
        Looper.loop()
    }
}
```

### 3. Not Calling Looper.loop()

```kotlin
// - BAD: Looper created but not started
class BadThread : Thread() {
    override fun run() {
        Looper.prepare()
        val handler = Handler(Looper.myLooper()!!)
        // - Missing Looper.loop() - messages won't be processed!
    }
}
```

### 4. Accessing Handler Before It's Ready

```kotlin
// - RACE CONDITION
class WorkerThread : Thread() {
    lateinit var handler: Handler

    override fun run() {
        Looper.prepare()
        handler = Handler(Looper.myLooper()!!)
        Looper.loop()
    }
}

val thread = WorkerThread()
thread.start()
thread.handler.sendEmptyMessage(1) // - May crash if handler not initialized yet!

// - SOLUTION: Use CountDownLatch (see complete example above)
```

---

## Looper vs Thread Comparison

| Aspect | Regular Thread | Thread with Looper |
|--------|----------------|-------------------|
| **Purpose** | Execute code once | Process messages continuously |
| **Lifecycle** | Runs and exits | Runs until `quit()` called |
| **Message Queue** | No | Yes (MessageQueue) |
| **Handler Support** | No | Yes |
| **Use Case** | One-time task | Event-driven processing |

---

## Summary

**How Looper connects to thread:**

1. **Call `Looper.prepare()`** on the thread to create a Looper
   - Stores Looper in `ThreadLocal<Looper>`
   - Creates MessageQueue for that thread
   - Can only be called once per thread

2. **Call `Looper.loop()`** to start processing messages
   - Infinite loop that blocks the thread
   - Retrieves messages from MessageQueue
   - Dispatches messages to target Handlers

3. **Create Handler** with that Looper
   - `Handler(Looper.myLooper()!!)` uses current thread's Looper
   - Handler sends messages to its Looper's MessageQueue
   - Messages are processed on the Looper's thread

**Main thread:**
- Looper prepared automatically (`Looper.prepareMainLooper()`)
- Access via `Looper.getMainLooper()`

**Best practice:**
- Use **HandlerThread** instead of manual Looper setup
- Always call `quit()` or `quitSafely()` to stop Looper

---

## Ответ (RU)
**Looper** связывается с потоком через методы:

1. **`Looper.prepare()`** - Создает Looper для текущего потока
2. **`Looper.loop()`** - Запускает цикл обработки сообщений

**Механизм:**

```kotlin
class LooperThread : Thread() {
    override fun run() {
        Looper.prepare()    // 1. Создать Looper для этого потока

        val handler = Handler(Looper.myLooper()!!) { message ->
            println("Сообщение: ${message.what}")
            true
        }

        Looper.loop()       // 2. Запустить цикл обработки
    }
}
```

**Как работает:**
- `Looper.prepare()` создает Looper и сохраняет в `ThreadLocal<Looper>`
- Один Looper на поток (повторный вызов `prepare()` вызовет исключение)
- Главный поток имеет Looper автоматически
- `Looper.loop()` блокирует поток для обработки сообщений

**Лучшая практика:**
- Используйте **HandlerThread** вместо ручной настройки
- Всегда вызывайте `quit()` или `quitSafely()` для остановки

