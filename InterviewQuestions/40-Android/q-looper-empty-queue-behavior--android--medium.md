---
id: android-106
title: Looper Empty Queue Behavior / Поведение Looper при пустой очереди
aliases: [Looper Blocking Behavior, Looper Empty Queue, Блокировка Looper, Поведение Looper при пустой очереди]
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
  - c-android
  - c-concurrency
  - q-handler-looper-comprehensive--android--medium
  - q-handler-looper-main-thread--android--medium
  - q-looper-thread-connection--android--medium
sources: []
created: 2025-10-13
updated: 2025-11-11
tags: [android/coroutines, android/threads-sync, blocking, difficulty/medium, looper, message-queue]

date created: Saturday, November 1st 2025, 1:25:04 pm
date modified: Tuesday, November 25th 2025, 8:53:58 pm
---

# Вопрос (RU)

> Что происходит, когда поток разбирает пустую очередь сообщений с помощью Looper.loop()?

# Question (EN)

> What happens when a thread processes an empty message queue with Looper.loop()?

---

## Ответ (RU)

Когда `Looper.loop()` обрабатывает **пустую очередь**, поток:

1. **Блокируется** в `MessageQueue.next()` (не завершает работу)
2. **Переходит в состояние ожидания** через native poll (epoll/подобный механизм)
3. **Не выполняет активное ожидание и практически не потребляет CPU** во время простоя
4. **Пробуждается** при добавлении нового сообщения (`nativeWake()`) или вызове `quit()/quitSafely()`

Это **штатное поведение** — поток остается живым, чтобы асинхронно обрабатывать будущие сообщения.

### Механизм Блокировки

```java
// Упрощенная реализация Looper.loop()
public static void loop() {
    final MessageQueue queue = myLooper().mQueue;

    for (;;) {
        Message msg = queue.next(); // ✅ БЛОКИРУЕТСЯ здесь при пустой очереди

        if (msg == null) return; // Возврат только при quit()/quitSafely()

        msg.target.dispatchMessage(msg);
    }
}
```

```java
// Упрощенная схема MessageQueue.next()
Message next() {
    for (;;) {
        nativePollOnce(ptr, timeout); // ✅ Блокировка в native (epoll/pipe/и т.п.)

        synchronized (this) {
            Message msg = mMessages;
            if (msg != null) return msg;

            // При отсутствии сообщений выбирается соответствующий таймаут;
            // -1 означает ожидание до пробуждения через nativeWake().
            timeout = -1;
        }
    }
}
```

**Native механизм:**
- Использует эффективный блокирующий вызов (напр. **epoll_wait** на Linux) вместо busy-waiting
- Поток отображается как **RUNNABLE**, но фактически заблокирован в native-коде (а не в `Object.wait()` Java)
- Пробуждается через **nativeWake()** при добавлении сообщения или изменении состояния очереди (практически немедленно с точки зрения приложения, с учетом планировщика)

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
        Looper.loop() // ✅ Блокируется здесь при отсутствии сообщений
        println("Loop exited")
    }

    fun waitReady() = latch.await()
}

// Использование
val thread = LooperThread().apply { start() }
thread.waitReady()

println("Thread state: ${thread.state}") // Обычно RUNNABLE (заблокирован в native-вызове)

// Пробуждение потока
thread.handler.post { println("Message processed") }

// Остановка
thread.handler.looper.quitSafely()
```

### Остановка Looper

```kotlin
// quit() - немедленный запрос выхода из цикла, дальнейшие сообщения из очереди не будут обрабатываться
looper.quit()

// quitSafely() - дать обработать сообщения с when <= now, затем корректно выйти
looper.quitSafely()
```

**Только `quit()` или `quitSafely()` (или их внутренние вызовы) завершают `Looper.loop()` — пустая очередь сама по себе НЕ завершает цикл и не убивает поток.**

---

## Answer (EN)

When `Looper.loop()` processes an **empty queue**, the thread:

1. **Blocks** inside `MessageQueue.next()` (it does NOT terminate)
2. **Enters a waiting state** via a native poll (epoll/similar mechanism)
3. **Does not busy-wait and effectively does not consume CPU** while idle
4. **Wakes up** when a new message is enqueued (`nativeWake()`) or when `quit()/quitSafely()` is requested

This is **expected behavior** — the thread stays alive to process future messages asynchronously.

### Blocking Mechanism

```java
// Simplified Looper.loop() implementation
public static void loop() {
    final MessageQueue queue = myLooper().mQueue;

    for (;;) {
        Message msg = queue.next(); // ✅ BLOCKS here if the queue has nothing ready

        if (msg == null) return; // Returns only when quit()/quitSafely() has been called

        msg.target.dispatchMessage(msg);
    }
}
```

```java
// Simplified sketch of MessageQueue.next()
Message next() {
    for (;;) {
        nativePollOnce(ptr, timeout); // ✅ Blocks in native (epoll/pipe/etc.)

        synchronized (this) {
            Message msg = mMessages;
            if (msg != null) return msg;

            // When no messages are ready, an appropriate timeout is chosen;
            // -1 means wait indefinitely until woken via nativeWake().
            timeout = -1;
        }
    }
}
```

**Native mechanism:**
- Uses an efficient blocking primitive (e.g., **epoll_wait** on Linux) instead of busy-waiting
- Thread state is shown as **RUNNABLE**, but it is actually blocked in native code (not in Java `Object.wait()`) 
- Woken up via **nativeWake()** when a message is posted or queue state changes (effectively immediately from the app's perspective, subject to scheduler)

### Example: Thread with Empty `Queue`

```kotlin
class LooperThread : Thread("Worker") {
    lateinit var handler: Handler
    private val latch = CountDownLatch(1)

    override fun run() {
        Looper.prepare()
        handler = Handler(Looper.myLooper()!!)
        latch.countDown()

        println("Entering loop with EMPTY queue...")
        Looper.loop() // ✅ Blocks here when there are no messages
        println("Loop exited")
    }

    fun waitReady() = latch.await()
}

// Usage
val thread = LooperThread().apply { start() }
thread.waitReady()

println("Thread state: ${thread.state}") // Typically RUNNABLE (blocked in native call)

// Wake up thread
thread.handler.post { println("Message processed") }

// Stop
thread.handler.looper.quitSafely()
```

### Stopping Looper

```kotlin
// quit() - request immediate exit from the loop; further pending messages won't be processed
looper.quit()

// quitSafely() - process messages with when <= now, then exit cleanly
looper.quitSafely()
```

**Only `quit()` or `quitSafely()` (or their internal uses) cause `Looper.loop()` to exit — an empty queue alone does NOT terminate the loop or the thread.**

---

## Дополнительные Вопросы (RU)

- В чем разница между `quit()` и `quitSafely()`?
- Почему состояние потока отображается как RUNNABLE, когда он заблокирован?
- Как `nativePollOnce()` пробуждается при поступлении сообщения?
- Что произойдет, если вызвать `Looper.loop()` дважды в одном и том же потоке?
- Как `HandlerThread` управляет жизненным циклом `Looper`?

## Follow-ups

- What's the difference between `quit()` and `quitSafely()`?
- Why does the thread state show RUNNABLE when it's blocked?
- How does `nativePollOnce()` wake up when a message arrives?
- What happens if you call `Looper.loop()` twice on the same thread?
- How does HandlerThread manage Looper lifecycle?

## Ссылки (RU)

- Android Source: `Looper.java` (AOSP)
- Android Source: `MessageQueue.java` (AOSP)
- Документация по `epoll` в Linux

## References

- [Android Source: Looper.java](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/master/core/java/android/os/Looper.java)
- [Android Source: MessageQueue.java](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/master/core/java/android/os/MessageQueue.java)
- [Linux epoll documentation](https://man7.org/linux/man-pages/man7/epoll.7.html)

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-coroutines]]

### Предпосылки (проще)

- [[q-what-is-the-main-application-execution-thread--android--easy]] - базовые понятия о главном потоке
- [[q-android-async-primitives--android--easy]] - обзор асинхронных примитивов
- [[q-why-multithreading-tools--android--easy]] - основы многопоточности

### Связанные (того Же уровня)

- [[q-handler-looper-comprehensive--android--medium]] - подробный разбор Handler и Looper
- [[q-multithreading-tools-android--android--medium]] - сравнение инструментов многопоточности

### Продвинутые (сложнее)

- [[q-android-runtime-internals--android--hard]] - детали рантайма ART
- [[q-recomposition-choreographer--android--hard]] - Choreographer и vsync
- [[q-how-vsync-and-recomposition-events-are-related--android--hard]] - планирование кадров

## Related Questions

### Prerequisites / Concepts

- [[c-coroutines]]

### Prerequisites (Easier)
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Main thread basics
- [[q-android-async-primitives--android--easy]] - Async primitives overview
- [[q-why-multithreading-tools--android--easy]] - Threading fundamentals

### Related (Same Level)
- [[q-handler-looper-comprehensive--android--medium]] - Handler and Looper deep dive
- [[q-multithreading-tools-android--android--medium]] - Threading tools comparison

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] - ART runtime details
- [[q-recomposition-choreographer--android--hard]] - Choreographer and vsync
- [[q-how-vsync-and-recomposition-events-are-related--android--hard]] - Frame scheduling
