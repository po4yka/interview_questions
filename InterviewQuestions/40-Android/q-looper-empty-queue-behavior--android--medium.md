---
id: android-106
title: Looper Empty Queue Behavior / Поведение Looper при пустой очереди
aliases:
- Looper Blocking Behavior
- Looper Empty Queue
- Блокировка Looper
- Поведение Looper при пустой очереди
topic: android
subtopics:
- coroutines
- threads-sync
question_kind: theory
difficulty: medium
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-coroutines
- q-handler-looper-messagequeue-relationship--android--medium
- q-handlerthread-vs-thread--android--medium
- q-message-scheduling-looper--android--medium
sources: []
created: 2025-10-13
updated: 2025-10-31
tags:
- android/coroutines
- android/threads-sync
- blocking
- difficulty/medium
- looper
- message-queue
---

# Вопрос (RU)

> Что происходит, когда поток разбирает пустую очередь сообщений с помощью Looper.loop()?

# Question (EN)

> What happens when a thread processes an empty message queue with Looper.loop()?

---

## Ответ (RU)

Когда `Looper.loop()` обрабатывает **пустую очередь**, поток:

1. **Блокируется** в `MessageQueue.next()` (не завершает работу)
2. **Переходит в состояние ожидания** через native epoll_wait
3. **Не потребляет CPU** (0% при отсутствии сообщений)
4. **Пробуждается** при добавлении нового сообщения или вызове `quit()`

Это **штатное поведение** — поток остается живым для обработки будущих сообщений.

### Механизм Блокировки

```java
// Упрощенная реализация Looper.loop()
public static void loop() {
    final MessageQueue queue = myLooper().mQueue;

    for (;;) {
        Message msg = queue.next(); // ✅ БЛОКИРУЕТСЯ здесь при пустой очереди

        if (msg == null) return; // Только при quit()

        msg.target.dispatchMessage(msg);
    }
}
```

```java
// MessageQueue.next() блокирует поток
Message next() {
    for (;;) {
        nativePollOnce(ptr, timeout); // ✅ Блокируется в native epoll_wait

        synchronized (this) {
            Message msg = mMessages;
            if (msg != null) return msg;

            timeout = -1; // Ждать бесконечно
        }
    }
}
```

**Native механизм:**
- Использует **epoll_wait** (Linux) вместо busy-waiting
- Поток в состоянии **RUNNABLE** (блокировка в native коде, не Java wait())
- Мгновенное пробуждение через **nativeWake()** при добавлении сообщения

### Пример: Поток С Пустой Очередью

```kotlin
class LooperThread : Thread("Worker") {
    lateinit var handler: Handler
    private val latch = CountDownLatch(1)

    override fun run() {
        Looper.prepare()
        handler = Handler(Looper.myLooper()!!)
        latch.countDown()

        println("Entering loop with EMPTY queue...")
        Looper.loop() // ✅ Блокируется здесь
        println("Loop exited")
    }

    fun waitReady() = latch.await()
}

// Использование
val thread = LooperThread().apply { start() }
thread.waitReady()

println("Thread state: ${thread.state}") // RUNNABLE (в native блокировке)

// Пробуждение потока
thread.handler.post { println("Message processed") }

// Остановка
thread.handler.looper.quitSafely()
```

### Остановка Looper

```kotlin
// ❌ quit() - немедленный выход, отбросить все сообщения
looper.quit()

// ✅ quitSafely() - обработать pending, затем выйти
looper.quitSafely()
```

**Только `quit()` или `quitSafely()` завершают `Looper.loop()`** — пустая очередь НЕ завершает поток.

---

## Answer (EN)

When `Looper.loop()` processes an **empty queue**, the thread:

1. **Blocks** in `MessageQueue.next()` (does NOT terminate)
2. **Enters waiting state** via native epoll_wait
3. **Consumes no CPU** (0% when idle)
4. **Wakes up** when a new message arrives or `quit()` is called

This is **normal behavior** — the thread stays alive to process future messages asynchronously.

### Blocking Mechanism

```java
// Simplified Looper.loop() implementation
public static void loop() {
    final MessageQueue queue = myLooper().mQueue;

    for (;;) {
        Message msg = queue.next(); // ✅ BLOCKS here if queue is empty

        if (msg == null) return; // Only when quit() is called

        msg.target.dispatchMessage(msg);
    }
}
```

```java
// MessageQueue.next() blocks the thread
Message next() {
    for (;;) {
        nativePollOnce(ptr, timeout); // ✅ Blocks in native epoll_wait

        synchronized (this) {
            Message msg = mMessages;
            if (msg != null) return msg;

            timeout = -1; // Wait indefinitely
        }
    }
}
```

**Native mechanism:**
- Uses **epoll_wait** (Linux) instead of busy-waiting
- Thread state: **RUNNABLE** (blocked in native code, not Java wait())
- Instant wake-up via **nativeWake()** when message is added

### Example: Thread with Empty Queue

```kotlin
class LooperThread : Thread("Worker") {
    lateinit var handler: Handler
    private val latch = CountDownLatch(1)

    override fun run() {
        Looper.prepare()
        handler = Handler(Looper.myLooper()!!)
        latch.countDown()

        println("Entering loop with EMPTY queue...")
        Looper.loop() // ✅ Blocks here
        println("Loop exited")
    }

    fun waitReady() = latch.await()
}

// Usage
val thread = LooperThread().apply { start() }
thread.waitReady()

println("Thread state: ${thread.state}") // RUNNABLE (in native blocking)

// Wake up thread
thread.handler.post { println("Message processed") }

// Stop
thread.handler.looper.quitSafely()
```

### Stopping Looper

```kotlin
// ❌ quit() - immediate exit, discard all messages
looper.quit()

// ✅ quitSafely() - process pending messages, then exit
looper.quitSafely()
```

**Only `quit()` or `quitSafely()` exits `Looper.loop()`** — an empty queue does NOT terminate the thread.

---

## Follow-ups

- What's the difference between `quit()` and `quitSafely()`?
- Why does the thread state show RUNNABLE when it's blocked?
- How does `nativePollOnce()` wake up when a message arrives?
- What happens if you call `Looper.loop()` twice on the same thread?
- How does HandlerThread manage Looper lifecycle?

## References

- [Android Source: Looper.java](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/master/core/java/android/os/Looper.java)
- [Android Source: MessageQueue.java](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/master/core/java/android/os/MessageQueue.java)
- [Linux epoll documentation](https://man7.org/linux/man-pages/man7/epoll.7.html)

## Related Questions

### Prerequisites / Concepts

- [[c-coroutines]]


### Prerequisites (Easier)
- Related content to be added

### Related (Same Level)
- [[q-handler-looper-messagequeue-relationship--android--medium]]
- [[q-handlerthread-vs-thread--android--medium]]
- [[q-message-scheduling-looper--android--medium]]

### Advanced (Harder)
- Related content to be added
