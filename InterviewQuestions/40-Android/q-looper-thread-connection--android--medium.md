---
id: android-229
title: Looper Thread Connection / Связь Looper и потока
aliases:
- Looper Thread Connection
- Связь Looper и потока
topic: android
subtopics:
- coroutines
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
- q-handler-looper-main-thread--android--medium
sources: []
created: 2025-10-15
updated: 2025-10-28
tags:
- android/coroutines
- android/threads-sync
- difficulty/medium
- handler
- looper
- message-queue
---

# Вопрос (RU)

> Как `Looper` связывается с потоком?

# Question (EN)

> How does `Looper` connect to a thread?

---

## Ответ (RU)

**`Looper`** связывается с потоком через два ключевых метода:

1. **`Looper.prepare()`** — создает `Looper` для текущего потока
2. **`Looper.loop()`** — запускает бесконечный цикл обработки сообщений

### Механизм Связывания

**`Looper`.prepare()** сохраняет `Looper` в `ThreadLocal<`Looper`>`:

```kotlin
// ✅ Правильное создание потока с Looper
class LooperThread : Thread() {
    override fun run() {
        Looper.prepare()  // Создать Looper для этого потока

        val handler = Handler(Looper.myLooper()!!) { msg ->
            println("Обработка: ${msg.what}")
            true
        }

        Looper.loop()  // Запустить цикл (блокирует поток)
    }
}
```

**Ключевые особенности:**
- Один `Looper` на поток (повторный вызов `prepare()` выбросит исключение)
- Главный поток имеет `Looper` автоматически
- `Looper.loop()` блокирует поток для обработки сообщений
- `Handler` получает доступ к `Looper` через `ThreadLocal`

### Жизненный Цикл

```kotlin
// ✅ HandlerThread — готовая реализация
val handlerThread = HandlerThread("Worker")
handlerThread.start()

val handler = Handler(handlerThread.looper) { msg ->
    // Обрабатывается на фоновом потоке
    true
}

handler.sendEmptyMessage(1)

// Остановка
handlerThread.quitSafely()  // Обработает pending сообщения
```

### Распространенные Ошибки

```kotlin
// ❌ Повторный вызов prepare()
Looper.prepare()
Looper.prepare()  // RuntimeException!

// ❌ Handler до prepare()
val handler = Handler(Looper.myLooper()!!)  // NPE!
Looper.prepare()

// ❌ Забыли вызвать loop()
Looper.prepare()
val handler = Handler(Looper.myLooper()!!)
// Сообщения не обрабатываются!
```

**Лучшая практика:** используйте `HandlerThread` вместо ручной настройки `Looper`.

## Answer (EN)

**`Looper`** connects to a thread using two key methods:

1. **`Looper.prepare()`** — creates a `Looper` for the current thread
2. **`Looper.loop()`** — starts the infinite message processing loop

### Binding Mechanism

**`Looper`.prepare()** stores the `Looper` in `ThreadLocal<`Looper`>`:

```kotlin
// ✅ Correct Looper thread creation
class LooperThread : Thread() {
    override fun run() {
        Looper.prepare()  // Create Looper for this thread

        val handler = Handler(Looper.myLooper()!!) { msg ->
            println("Processing: ${msg.what}")
            true
        }

        Looper.loop()  // Start loop (blocks thread)
    }
}
```

**Key characteristics:**
- One `Looper` per thread (calling `prepare()` twice throws exception)
- Main thread has `Looper` prepared automatically
- `Looper.loop()` blocks the thread to process messages
- `Handler` accesses `Looper` via `ThreadLocal`

### `Lifecycle`

```kotlin
// ✅ HandlerThread — ready-made implementation
val handlerThread = HandlerThread("Worker")
handlerThread.start()

val handler = Handler(handlerThread.looper) { msg ->
    // Processed on background thread
    true
}

handler.sendEmptyMessage(1)

// Stopping
handlerThread.quitSafely()  // Process pending messages
```

### Common Mistakes

```kotlin
// ❌ Calling prepare() twice
Looper.prepare()
Looper.prepare()  // RuntimeException!

// ❌ Handler before prepare()
val handler = Handler(Looper.myLooper()!!)  // NPE!
Looper.prepare()

// ❌ Forgot to call loop()
Looper.prepare()
val handler = Handler(Looper.myLooper()!!)
// Messages won't be processed!
```

**Best practice:** Use `HandlerThread` instead of manual `Looper` setup.

---

## Follow-ups

- What happens if you call `Looper.prepare()` twice on the same thread?
- How does the main thread get its `Looper` without calling `prepare()`?
- What's the difference between `quit()` and `quitSafely()`?
- Can multiple Handlers share the same `Looper`?
- How does `HandlerThread` simplify `Looper` management?

## References

- Android Developer Docs: `Looper` and `Handler`
- Android Threading Guide

## Related Questions

### Prerequisites / Concepts

- [[c-coroutines]]


### Prerequisites
- [[q-handler-looper-main-thread--android--medium]] — Understanding `Handler`-`Looper`-`Thread` relationship

### Related
- `Handler`-`Thread` interaction patterns
- `Message` queue implementation details

### Advanced
- Advanced HandlerThread patterns and lifecycle management
- Custom `Looper` implementations for specialized use cases
