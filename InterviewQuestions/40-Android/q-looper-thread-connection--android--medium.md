---
id: android-229
anki_cards:
- slug: android-229-0-en
  language: en
  anki_id: 1768414139894
  synced_at: '2026-01-23T16:45:05.799994'
- slug: android-229-0-ru
  language: ru
  anki_id: 1768414139918
  synced_at: '2026-01-23T16:45:05.801271'
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
- q-handler-looper-comprehensive--android--medium
- q-handler-looper-main-thread--android--medium
- q-main-thread-android--android--medium
sources: []
created: 2024-10-15
updated: 2025-11-11
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

**`Looper`** связывается с потоком через два ключевых шага и `ThreadLocal`:

1. **`Looper.prepare()`** — создаёт `Looper` и сохраняет его в `ThreadLocal<Looper>` текущего потока, логически привязывая один `Looper` к этому потоку.
2. **`Looper.loop()`** — запускает бесконечный цикл обработки сообщений для `MessageQueue` этого `Looper` (блокирует поток до `quit()`/`quitSafely()`).

### Механизм Связывания

- `Looper.prepare()` сохраняет `Looper` в `ThreadLocal<Looper>` текущего потока.
- `Looper.myLooper()` читает `Looper` из этого `ThreadLocal`, тем самым обеспечивает доступ только из "своего" потока.
- **`Handler`** при создании привязывается к конкретному `Looper` (и его `MessageQueue`), переданному явно или полученному через `Looper.myLooper()`.

```kotlin
// ✅ Пример потока с Looper (используем явный Looper и Callback)
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
- Один `Looper` на поток (повторный вызов `prepare()` в одном потоке выбросит `RuntimeException`).
- Главный поток имеет `Looper`, подготовленный системой автоматически при старте.
- `Looper.loop()` блокирует поток и извлекает сообщения/задачи из очереди до вызова `quit()`/`quitSafely()`.
- `Handler` жёстко связан с конкретным `Looper` при создании; `ThreadLocal` используется самим `Looper` для связи с конкретным потоком.

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
handlerThread.quitSafely()  // Завершает цикл после обработки уже находящихся в очереди сообщений
```

### Распространенные Ошибки

```kotlin
// ❌ Повторный вызов prepare() в одном и том же потоке
Looper.prepare()
Looper.prepare()  // RuntimeException!

// ❌ Handler до prepare() (если Looper ещё не создан)
val looper = Looper.myLooper()  // null, если prepare() не вызывался
val handler = Handler(looper!!)  // NPE из-за !! при отсутствии Looper
// (или RuntimeException в реальном коде, если логика полагается на наличие Looper)

// ❌ Забыли вызвать loop()
Looper.prepare()
val handler2 = Handler(Looper.myLooper()!!)
// Сообщения не обрабатываются, т.к. не запущен цикл Looper!
```

**Лучшая практика:** по возможности используйте `HandlerThread` вместо ручной настройки `Looper` и передавайте `Looper` явно при создании `Handler`.

## Answer (EN)

**`Looper`** connects to a thread via two key steps and a `ThreadLocal`:

1. **`Looper.prepare()`** — creates a `Looper` and stores it in the current thread's `ThreadLocal<Looper>`, logically binding a single `Looper` instance to that thread.
2. **`Looper.loop()`** — starts the infinite message-processing loop for that `Looper`'s `MessageQueue` (blocking the thread until `quit()`/`quitSafely()`).

### Binding Mechanism

- `Looper.prepare()` stores the `Looper` in the current thread's `ThreadLocal<Looper>`.
- `Looper.myLooper()` reads the `Looper` from this `ThreadLocal`, ensuring access only from its owning thread.
- A **`Handler`** is bound to a specific `Looper` (and its `MessageQueue`) at construction time, either passed explicitly or obtained via `Looper.myLooper()`.

```kotlin
// ✅ Example of a thread with a Looper (using explicit Looper and Callback)
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
- One `Looper` per thread (calling `prepare()` twice on the same thread throws `RuntimeException`).
- The main (UI) thread gets its `Looper` prepared automatically by the framework.
- `Looper.loop()` blocks the thread and pulls messages/tasks from the queue until `quit()`/`quitSafely()` is called.
- A `Handler` is tightly bound to a specific `Looper` at construction; `Looper` uses `ThreadLocal` internally to associate itself with its thread.

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
handlerThread.quitSafely()  // Ends loop after processing messages already in the queue
```

### Common Mistakes

```kotlin
// ❌ Calling prepare() twice on the same thread
Looper.prepare()
Looper.prepare()  // RuntimeException!

// ❌ Creating Handler before prepare() (if Looper not created yet)
val looper = Looper.myLooper()  // null if prepare() hasn't been called
val handler = Handler(looper!!)  // NPE due to !! when no Looper is present
// (or a logical error / RuntimeException later if code assumes a Looper exists)

// ❌ Forgot to call loop()
Looper.prepare()
val handler2 = Handler(Looper.myLooper()!!)
// Messages won't be processed because the Looper loop is not started!
```

**Best practice:** Prefer `HandlerThread` over manual `Looper` setup where possible, and always bind `Handler` to an explicit `Looper`.

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
