---
id: 20251012-12271130
title: "Looper Empty Queue Behavior / Поведение Looper при пустой очереди"
topic: android
difficulty: medium
status: draft
created: 2025-10-13
tags: [android/concurrency, blocking, concurrency, looper, message-queue, threading, difficulty/medium]
moc: moc-android
related: [q-how-does-fragment-lifecycle-differ-from-activity-v2--android--medium, q-main-thread-android--android--medium, q-v-chyom-raznitsa-mezhdu-fragmentmanager-i-fragmenttransaction--programming-languages--medium]
---
# Что происходит, когда поток разбирает пустую очередь сообщений с помощью Looper.loop()?

**English**: What happens when a thread processes an empty message queue with Looper.loop()?

## Answer (EN)
When `Looper.loop()` processes an **empty message queue**, the thread:

1. **Blocks** (enters waiting state)
2. **Does NOT terminate** or exit
3. **Waits** until a new message arrives
4. **Consumes minimal resources** (not busy-waiting)

This is the **normal behavior** for Looper threads - they stay alive to process future messages asynchronously.

---

## How Looper.loop() Handles Empty Queue

### Internal Mechanism

```java
// Simplified Looper.loop() implementation
public static void loop() {
    final Looper me = myLooper();
    final MessageQueue queue = me.mQueue;

    for (;;) {
        Message msg = queue.next(); // ← BLOCKS here if queue is empty!

        if (msg == null) {
            return; // Only happens when quit() is called
        }

        msg.target.dispatchMessage(msg);
        msg.recycleUnchecked();
    }
}
```

**Key point:** `MessageQueue.next()` **blocks** until a message is available.

---

### MessageQueue.next() Blocking

```java
// Simplified MessageQueue.next() implementation
Message next() {
    for (;;) {
        // If queue is empty, wait for new message
        nativePollOnce(ptr, nextPollTimeoutMillis); // ← BLOCKS here

        synchronized (this) {
            Message msg = mMessages;
            if (msg != null) {
                return msg; // Message available
            } else {
                // No message, continue waiting
                nextPollTimeoutMillis = -1; // Wait indefinitely
            }
        }
    }
}
```

**Blocking mechanism:**
- Uses **native epoll** (Linux) for efficient waiting
- Thread goes to **sleep state** (not consuming CPU)
- Wakes up when:
  - New message is added
  - Delayed message becomes ready
  - `quit()` is called

---

## Complete Example: Empty Queue Behavior

```kotlin
import android.os.Handler
import android.os.Looper
import android.os.Message
import java.util.concurrent.CountDownLatch

class LooperThread : Thread("LooperThread") {

    lateinit var handler: Handler
        private set

    private val latch = CountDownLatch(1)

    override fun run() {
        println("[${Thread.currentThread().name}] Starting...")

        // Prepare Looper
        Looper.prepare()

        // Create Handler
        handler = object : Handler(Looper.myLooper()!!) {
            override fun handleMessage(msg: Message) {
                println("[${Thread.currentThread().name}] Received message: ${msg.what}")
                Thread.sleep(1000)
                println("[${Thread.currentThread().name}] Processed message: ${msg.what}")
            }
        }

        latch.countDown()

        println("[${Thread.currentThread().name}] Entering Looper.loop() - queue is EMPTY")

        // Start message loop (blocks here with empty queue)
        Looper.loop()

        println("[${Thread.currentThread().name}] Looper stopped")
    }

    fun waitUntilReady() = latch.await()

    fun quit() {
        handler.looper.quitSafely()
    }
}

fun main() {
    val looperThread = LooperThread()

    println("[Main] Starting LooperThread...")
    looperThread.start()
    looperThread.waitUntilReady()

    println("[Main] LooperThread is now waiting with EMPTY queue")
    println("[Main] Thread state: ${looperThread.state}") // WAITING or TIMED_WAITING

    Thread.sleep(2000)

    println("[Main] Sending message 1...")
    looperThread.handler.sendEmptyMessage(1)

    Thread.sleep(1500)

    println("[Main] Sending message 2...")
    looperThread.handler.sendEmptyMessage(2)

    Thread.sleep(1500)

    println("[Main] Quitting Looper...")
    looperThread.quit()

    looperThread.join()
    println("[Main] LooperThread terminated")
}
```

**Output:**
```
[Main] Starting LooperThread...
[LooperThread] Starting...
[LooperThread] Entering Looper.loop() - queue is EMPTY
[Main] LooperThread is now waiting with EMPTY queue
[Main] Thread state: RUNNABLE  ← Blocked in native code
[Main] Sending message 1...
[LooperThread] Received message: 1
[LooperThread] Processed message: 1
[Main] Sending message 2...
[LooperThread] Received message: 2
[LooperThread] Processed message: 2
[Main] Quitting Looper...
[LooperThread] Looper stopped
[Main] LooperThread terminated
```

---

## Thread States During Looper.loop()

### When Queue is Empty

```kotlin
// Thread is BLOCKED in native code (epoll_wait)
// CPU usage: ~0%
// Memory: Minimal (thread stack + Looper/MessageQueue objects)
```

**Check thread state:**
```kotlin
val looperThread = LooperThread()
looperThread.start()
Thread.sleep(100)

println("Thread state: ${looperThread.state}")
// Output: RUNNABLE (but actually blocked in native epoll_wait)
```

**Why RUNNABLE and not WAITING?**
- Thread is blocked in **native code** (epoll_wait), not Java wait()
- JVM thread state shows RUNNABLE for native blocking

---

## Message Processing Flow

### 1. Queue is Empty

```

 Looper.loop()           
   ↓                     
 MessageQueue.next()     
   ↓                     
 nativePollOnce()         ← Thread BLOCKS here
   (waiting...)              (epoll_wait in native code)

```

### 2. Message Arrives

```

 Handler.sendMessage()    ← From any thread
   ↓                     
 MessageQueue.enqueue()  
   ↓                     
 nativeWake()             ← Wakes up Looper thread



 nativePollOnce() WAKES  
   ↓                     
 MessageQueue.next()     
   returns Message       
   ↓                     
 Handler.dispatchMessage  ← Process message

```

---

## Performance and Resource Usage

### Efficient Waiting

**Looper uses native epoll (Linux):**
- **No busy-waiting** (not checking queue in a loop)
- **No CPU consumption** when idle
- **Instant wake-up** when message arrives

```kotlin
// - BAD: Busy-waiting (wastes CPU)
while (true) {
    if (queue.hasMessages()) {
        processMessage(queue.next())
    }
    // Continuously checks → 100% CPU usage!
}

// - GOOD: Looper's approach (efficient)
while (true) {
    val msg = queue.next() // Blocks in epoll_wait (0% CPU when idle)
    if (msg == null) break
    processMessage(msg)
}
```

---

## When Does Looper.loop() Exit?

### Only When quit() is Called

```kotlin
val looperThread = HandlerThread("Worker")
looperThread.start()

// Looper is running (waiting for messages)

looperThread.quitSafely() // Signal to quit

// After processing pending messages, Looper.loop() exits
// Thread terminates
```

### quit() vs quitSafely()

```kotlin
// Option 1: quit() - Discard all pending messages
looper.quit()
// - MessageQueue.next() returns null immediately
// - Pending messages are discarded
// - Looper.loop() exits

// Option 2: quitSafely() - Process pending messages first
looper.quitSafely()
// - Processes all messages with timestamp <= now
// - Discards delayed messages
// - Then exits
```

---

## HandlerThread Example

**HandlerThread** manages Looper lifecycle automatically:

```kotlin
import android.os.HandlerThread
import android.os.Handler

class BackgroundWorker {

    private val handlerThread = HandlerThread("BackgroundWorker")
    private lateinit var handler: Handler

    fun start() {
        handlerThread.start() // Calls Looper.prepare() and Looper.loop()

        handler = Handler(handlerThread.looper) { message ->
            println("Processing: ${message.what}")
            // Looper thread is BLOCKED when no messages
            true
        }
    }

    fun sendTask(taskId: Int) {
        handler.sendEmptyMessage(taskId)
    }

    fun stop() {
        handlerThread.quitSafely() // Stops Looper gracefully
    }
}

// Usage
val worker = BackgroundWorker()
worker.start()

println("Worker thread is IDLE (blocked with empty queue)")
Thread.sleep(2000)

worker.sendTask(1) // Wakes up thread
worker.sendTask(2)

Thread.sleep(2000)
worker.stop()
```

---

## Common Use Cases

### 1. UI Thread (Main Thread)

```kotlin
// Main thread Looper runs forever
Looper.getMainLooper().thread.state
// → RUNNABLE (blocked in epoll_wait when no UI events)

// CPU usage: 0% when idle
// Wakes up when: touch events, messages, vsync signals
```

### 2. Background Worker Thread

```kotlin
class DatabaseWorker {
    private val dbThread = HandlerThread("DatabaseThread")
    private lateinit var dbHandler: Handler

    init {
        dbThread.start()
        dbHandler = Handler(dbThread.looper)
    }

    fun query(sql: String, callback: (Result) -> Unit) {
        dbHandler.post {
            val result = database.rawQuery(sql)
            mainHandler.post { callback(result) }
        }
    }

    fun close() {
        dbThread.quitSafely()
    }
}
```

### 3. Service with Message Queue

```kotlin
class MyService : Service() {

    private val serviceThread = HandlerThread("ServiceThread")
    private lateinit var serviceHandler: Handler

    override fun onCreate() {
        super.onCreate()
        serviceThread.start()
        serviceHandler = Handler(serviceThread.looper)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        serviceHandler.post {
            // Process in background
            processTask()
        }
        return START_STICKY
    }

    override fun onDestroy() {
        super.onDestroy()
        serviceThread.quitSafely()
    }
}
```

---

## Summary

**What happens when Looper.loop() processes empty queue:**

1. Thread **blocks** in `MessageQueue.next()`
2. Uses **native epoll_wait** (efficient, no CPU consumption)
3. Thread state: **RUNNABLE** (but blocked in native code)
4. **Does NOT exit** - waits for messages indefinitely
5. **Wakes up** when:
   - New message arrives
   - Delayed message becomes ready
   - `quit()` or `quitSafely()` is called

**Key characteristics:**
- - **Efficient**: 0% CPU when idle
- - **Responsive**: Instant wake-up on new message
- - **Persistent**: Thread stays alive for future work
- - **Safe**: Managed by Android framework

**Stopping Looper:**
```kotlin
looper.quit()        // Immediate quit, discard pending
looper.quitSafely()  // Graceful quit, process pending
```

---

## Ответ (RU)
Когда поток разбирает **пустую очередь сообщений** с помощью `Looper.loop()`, он:

1. **Блокируется** (переходит в состояние ожидания)
2. **НЕ завершает работу**
3. **Ждет** появления нового сообщения
4. **Не потребляет ресурсы** (не выполняет busy-waiting)

Это **нормальное поведение** для Looper - поток остается активным для асинхронной обработки будущих сообщений.

**Механизм:**

```java
public static void loop() {
    for (;;) {
        Message msg = queue.next(); // ← БЛОКИРУЕТСЯ здесь при пустой очереди
        if (msg == null) return;
        msg.target.dispatchMessage(msg);
    }
}
```

**Блокировка:**
- Использует **native epoll** (Linux) для эффективного ожидания
- Поток переходит в **состояние сна** (не потребляет CPU)
- Пробуждается при добавлении нового сообщения или вызове `quit()`

**Остановка Looper:**
```kotlin
looper.quit()        // Немедленный выход, отбросить pending
looper.quitSafely()  // Обработать pending, затем выйти
```

## Related Questions

- [[q-how-does-fragment-lifecycle-differ-from-activity-v2--android--medium]]
- [[q-main-thread-android--android--medium]]
- [[q-v-chyom-raznitsa-mezhdu-fragmentmanager-i-fragmenttransaction--android--medium]]
