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

> Как Looper связывается с потоком?

# Question (EN)

> How does Looper connect to a thread?

---

## Ответ (RU)

**Looper** связывается с потоком через два ключевых метода:

1. **`Looper.prepare()`** — создает и привязывает Looper к текущему потоку через `ThreadLocal`
2. **`Looper.loop()`** — запускает бесконечный цикл обработки сообщений для этого Looper

### Механизм Связывания

**`Looper.prepare()`** сохраняет Looper в `ThreadLocal<Looper>` текущего потока. **`Handler`** при создании привязывается к конкретному `Looper` (и его `MessageQueue`), обычно полученному через `Looper.myLooper()` или явно переданному.

```kotlin
// ✅ Правильное создание потока с Looper (API 28+ используйте явный Looper)
class LooperThread : Thread() {
    override fun run() {
        Looper.prepare()  // Создать и привязать Looper к этому потоку

        val looper = Looper.myLooper()!!
        val handler = Handler(looper) { msg ->
            println("Обработка: ${msg.what}")
            true
        }

        Looper.loop()  // Запустить цикл (блокирует поток до quit/quitSafely)
    }
}
```

**Ключевые особенности:**
- Один Looper на поток (повторный вызов `prepare()` выбросит `RuntimeException`)
- Главный поток имеет Looper, подготовленный системой автоматически
- `Looper.loop()` блокирует поток и извлекает сообщения/задачи из очереди до вызова `quit()`/`quitSafely()`
- `Handler` связан с конкретным `Looper` при создании; `ThreadLocal` используется самим `Looper` для связи с потоком

### Жизненный Цикл

```kotlin
// ✅ HandlerThread — готовая реализация потока с Looper
val handlerThread = HandlerThread("Worker")
handlerThread.start()

val handler = Handler(handlerThread.looper) { msg ->
    // Обработка на фоновом потоке
    true
}

handler.sendEmptyMessage(1)

// Остановка
handlerThread.quitSafely()  // Завершает цикл после обработки уже находящихся в очереди сообщений (без принятия новых)
```

### Распространенные Ошибки

```kotlin
// ❌ Повторный вызов prepare() в одном и том же потоке
Looper.prepare()
Looper.prepare()  // RuntimeException!

// ❌ Handler до prepare() (если Looper ещё не создан)
val handler = Handler(Looper.myLooper()!!)  // NPE или RuntimeException при отсутствии Looper!
Looper.prepare()

// ❌ Забыли вызвать loop()
Looper.prepare()
val handler = Handler(Looper.myLooper()!!)
// Сообщения не обрабатываются, т.к. не запущен цикл Looper!
```

**Лучшая практика:** по возможности используйте `HandlerThread` вместо ручной настройки Looper.

## Answer (EN)

**Looper** connects to a thread via two key methods:

1. **`Looper.prepare()`** — creates and binds a Looper to the current thread using `ThreadLocal`
2. **`Looper.loop()`** — starts the infinite message processing loop for that Looper

### Binding Mechanism

**`Looper.prepare()`** stores the Looper in the current thread's `ThreadLocal<Looper>`. A **`Handler`** is bound to a specific `Looper` (and its `MessageQueue`) at construction time, typically obtained via `Looper.myLooper()` or passed explicitly.

```kotlin
// ✅ Correct Looper thread creation (on modern Android prefer explicit Looper)
class LooperThread : Thread() {
    override fun run() {
        Looper.prepare()  // Create and bind Looper to this thread

        val looper = Looper.myLooper()!!
        val handler = Handler(looper) { msg ->
            println("Processing: ${msg.what}")
            true
        }

        Looper.loop()  // Start loop (blocks thread until quit/quitSafely)
    }
}
```

**Key characteristics:**
- One Looper per thread (calling `prepare()` twice on the same thread throws `RuntimeException`)
- The main thread gets its Looper prepared by the system automatically
- `Looper.loop()` blocks the thread and pulls messages/tasks from the queue until `quit()`/`quitSafely()` is called
- A `Handler` is bound to a specific `Looper` at construction; `ThreadLocal` is used internally by `Looper` to associate itself with the thread

### Lifecycle

```kotlin
// ✅ HandlerThread — ready-made implementation of a thread with a Looper
val handlerThread = HandlerThread("Worker")
handlerThread.start()

val handler = Handler(handlerThread.looper) { msg ->
    // Processed on background thread
    true
}

handler.sendEmptyMessage(1)

// Stopping
handlerThread.quitSafely()  // Ends loop after processing messages already in the queue (no new messages accepted)
```

### Common Mistakes

```kotlin
// ❌ Calling prepare() twice on the same thread
Looper.prepare()
Looper.prepare()  // RuntimeException!

// ❌ Handler before prepare() (if Looper not created yet)
val handler = Handler(Looper.myLooper()!!)  // NPE or RuntimeException when no Looper!
Looper.prepare()

// ❌ Forgot to call loop()
Looper.prepare()
val handler = Handler(Looper.myLooper()!!)
// Messages won't be processed because Looper loop is not started!
```

**Best practice:** Prefer `HandlerThread` over manual Looper setup when possible.

---

## Follow-ups

- What happens if you call `Looper.prepare()` twice on the same thread?
- How does the main thread get its Looper without calling `prepare()`?
- What's the difference between `quit()` and `quitSafely()`?
- Can multiple Handlers share the same Looper?
- How does `HandlerThread` simplify Looper management?

## References

- Android Developer Docs: Looper and Handler
- Android Threading Guide

## Related Questions

### Prerequisites / Concepts

- [[c-coroutines]]


### Prerequisites
- [[q-handler-looper-main-thread--android--medium]] — Understanding Handler-Looper-Thread relationship

### Related
- Handler-Thread interaction patterns
- Message queue implementation details

### Advanced
- Advanced HandlerThread patterns and lifecycle management
- Custom Looper implementations for specialized use cases
