---
id: 20251012-122714
title: "Handler Looper Main Thread / Handler и Looper главного потока"
aliases: ["Handler and Looper on Main Thread", "Handler и Looper главного потока"]
topic: android
subtopics: [threads-sync, background-execution]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-main-thread-android--android--medium, q-looper-thread-connection--android--medium, q-multithreading-tools-android--android--medium]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android/threads-sync, android/background-execution, concurrency, difficulty/medium, handler, looper, main-thread, message-queue]
date created: Monday, October 27th 2025, 5:04:18 pm
date modified: Thursday, October 30th 2025, 12:48:05 pm
---

# Вопрос (RU)

Как получить сообщения на главном потоке с помощью Handler и Looper?

# Question (EN)

How can you receive messages on the main thread using Handler and Looper?

## Ответ (RU)

**Handler** отправляет сообщения в **MessageQueue** потока, который обрабатывается **Looper**. Чтобы получать сообщения на главном потоке:

1. Создайте Handler, привязанный к `Looper.getMainLooper()`
2. Отправьте сообщение из любого потока через `sendMessage()` или `post()`
3. Обработайте в `handleMessage()` или лямбде

### Основной подход

```kotlin
// ✅ Правильно: Handler привязан к главному потоку
private val mainHandler = Handler(Looper.getMainLooper()) { msg ->
    when (msg.what) {
        MSG_UPDATE -> textView.text = msg.obj as String
    }
    true
}

// Отправка из фонового потока
Thread {
    val result = fetchData()
    mainHandler.sendMessage(Message.obtain().apply {
        what = MSG_UPDATE
        obj = result
    })
}.start()
```

### Использование post()

Для простых задач используйте `post()`:

```kotlin
private val mainHandler = Handler(Looper.getMainLooper())

fun loadData() {
    Thread {
        val data = fetchFromNetwork()
        // ✅ Выполняется на главном потоке
        mainHandler.post {
            recyclerView.adapter = DataAdapter(data)
        }
    }.start()
}
```

### Предотвращение утечек памяти

```kotlin
// ❌ Плохо: анонимный класс держит ссылку на Activity
class MainActivity : AppCompatActivity() {
    private val handler = object : Handler(Looper.getMainLooper()) {
        override fun handleMessage(msg: Message) {
            textView.text = "Updated" // Неявная ссылка на Activity
        }
    }
}

// ✅ Хорошо: очистка в onDestroy
class MainActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacksAndMessages(null) // Удаляет все сообщения
    }
}
```

### Handler vs Coroutines

**Handler (традиционный)**:
```kotlin
fun loadData() {
    Thread {
        val data = fetchData()
        mainHandler.post { updateUI(data) }
    }.start()
}
```

**Coroutines (современный)**:
```kotlin
fun loadData() {
    viewModelScope.launch {
        val data = withContext(Dispatchers.IO) { fetchData() }
        updateUI(data) // Автоматически на главном потоке
    }
}
```

**Ключевые моменты:**
- Главный поток имеет Looper по умолчанию
- `Looper.getMainLooper()` возвращает Looper главного потока
- Всегда очищайте сообщения в `onDestroy()` во избежание утечек
- Для новых проектов предпочитайте coroutines вместо Handler

---

## Answer (EN)

**Handler** posts messages to a thread's **MessageQueue**, which is processed by a **Looper**. To receive messages on the main thread:

1. Create a Handler bound to `Looper.getMainLooper()`
2. Send messages from any thread via `sendMessage()` or `post()`
3. Process in `handleMessage()` or lambda

### Basic Approach

```kotlin
// ✅ Correct: Handler bound to main thread
private val mainHandler = Handler(Looper.getMainLooper()) { msg ->
    when (msg.what) {
        MSG_UPDATE -> textView.text = msg.obj as String
    }
    true
}

// Send from background thread
Thread {
    val result = fetchData()
    mainHandler.sendMessage(Message.obtain().apply {
        what = MSG_UPDATE
        obj = result
    })
}.start()
```

### Using post()

For simple tasks, use `post()`:

```kotlin
private val mainHandler = Handler(Looper.getMainLooper())

fun loadData() {
    Thread {
        val data = fetchFromNetwork()
        // ✅ Executes on main thread
        mainHandler.post {
            recyclerView.adapter = DataAdapter(data)
        }
    }.start()
}
```

### Memory Leak Prevention

```kotlin
// ❌ Bad: Anonymous class holds Activity reference
class MainActivity : AppCompatActivity() {
    private val handler = object : Handler(Looper.getMainLooper()) {
        override fun handleMessage(msg: Message) {
            textView.text = "Updated" // Implicit Activity reference
        }
    }
}

// ✅ Good: Cleanup in onDestroy
class MainActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacksAndMessages(null) // Removes all messages
    }
}
```

### Handler vs Coroutines

**Handler (traditional)**:
```kotlin
fun loadData() {
    Thread {
        val data = fetchData()
        mainHandler.post { updateUI(data) }
    }.start()
}
```

**Coroutines (modern)**:
```kotlin
fun loadData() {
    viewModelScope.launch {
        val data = withContext(Dispatchers.IO) { fetchData() }
        updateUI(data) // Automatically on main thread
    }
}
```

**Key Points:**
- Main thread has a Looper by default
- `Looper.getMainLooper()` returns the main thread's Looper
- Always clean up messages in `onDestroy()` to prevent leaks
- For new projects, prefer coroutines over Handler

---

## Follow-ups

- How does MessageQueue prioritize messages with different timestamps?
- What happens if you call `Looper.prepare()` on the main thread?
- How do `sendMessageAtFrontOfQueue()` and `sendMessageDelayed()` differ?
- When would you use Handler instead of coroutines in modern Android?

## References

- Android Developer Documentation - Handler and Looper
- Android Developer Documentation - Processes and Threads

## Related Questions

### Prerequisites
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Understanding Android main thread
- [[q-why-multithreading-tools--android--easy]] - Why we need threading tools

### Related
- [[q-main-thread-android--android--medium]] - Main thread responsibilities
- [[q-looper-thread-connection--android--medium]] - Looper and thread relationship
- [[q-multithreading-tools-android--android--medium]] - Threading tools comparison

### Advanced
- [[q-which-class-to-use-for-rendering-view-in-background-thread--android--hard]] - Background rendering patterns
- [[q-unit-testing-coroutines-flow--android--medium]] - Testing async code
