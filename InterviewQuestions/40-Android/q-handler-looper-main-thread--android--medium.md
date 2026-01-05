---
id: android-162
title: Handler Looper Main Thread / Handler и Looper главного потока
aliases: [Handler and Looper on Main Thread, Handler и Looper главного потока]
topic: android
subtopics: [background-execution, threads-sync]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-background-tasks, c-coroutines, q-handler-looper-comprehensive--android--medium, q-looper-thread-connection--android--medium, q-main-thread-android--android--medium, q-multithreading-tools-android--android--medium, q-what-is-the-main-application-execution-thread--android--easy]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/background-execution, android/threads-sync, concurrency, difficulty/medium, handler, looper, main-thread, message-queue]

---
# Вопрос (RU)

> Как получить сообщения на главном потоке с помощью Handler и Looper?

# Question (EN)

> How can you receive messages on the main thread using Handler and Looper?

## Ответ (RU)

**Handler** ставит сообщения и runnable-задачи в **MessageQueue** потока, которая обрабатывается **Looper**. Чтобы получать сообщения на главном потоке:

1. Создайте Handler, привязанный к `Looper.getMainLooper()` (это Looper главного потока)
2. Отправьте сообщение из любого потока через `sendMessage()` или `post()` — оно будет добавлено в очередь главного потока
3. Обработайте его в `handleMessage()` или лямбде

> Примечание: используйте конструктор `Handler(Looper, Callback)` или `Handler(Looper)` — безаргументный конструктор `Handler()` устарел и не рекомендуется.

### Основной Подход

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

### Предотвращение Утечек Памяти

```kotlin
// ❌ Потенциально плохо: анонимный класс может удерживать Activity, а
// отложенные сообщения/callback-и могут выполниться после её уничтожения
class MainActivity : AppCompatActivity() {
    private val handler = object : Handler(Looper.getMainLooper()) {
        override fun handleMessage(msg: Message) {
            textView.text = "Updated" // Неявная ссылка на Activity
        }
    }
}

// ✅ Лучше: использовать Handler с Looper главного потока и очищать
// отложенные сообщения/колбэки, которые ссылаются на Activity
class MainActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    override fun onDestroy() {
        super.onDestroy()
        // Очищаем только те callbacks/messages, которые могут пережить Activity
        handler.removeCallbacksAndMessages(null)
    }
}
```

Главная идея: сам по себе Handler на главном Looper не создаёт утечку; риск возникает, если вы размещаете в очереди отложенные задачи, которые удерживают ссылку на `Activity`/`Fragment` после их уничтожения.

### Handler Vs Coroutines

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
    // viewModelScope по умолчанию использует Dispatchers.Main, поэтому updateUI
    // будет вызван на главном потоке
    viewModelScope.launch {
        val data = withContext(Dispatchers.IO) { fetchData() }
        updateUI(data)
    }
}
```

**Ключевые моменты:**
- Главный поток имеет Looper по умолчанию
- `Looper.getMainLooper()` возвращает Looper главного потока
- При использовании Handler'ов внутри `Activity`/`Fragment` очищайте отложенные callbacks/messages, которые могут пережить жизненный цикл компонента, чтобы избежать утечек
- В новых проектах обычно предпочитают coroutines вместо прямого использования Handler, оставляя Handler для интеграции с низкоуровневым/legacy API

---

## Answer (EN)

**Handler** enqueues messages and runnable tasks into a thread's **MessageQueue**, which is processed by a **Looper**. To receive messages on the main thread:

1. Create a Handler bound to `Looper.getMainLooper()` (the main thread's Looper)
2. Send messages from any thread via `sendMessage()` or `post()` — they will be added to the main thread queue
3. Handle them in `handleMessage()` or a lambda callback

> Note: Use `Handler(Looper, Callback)` or `Handler(Looper)` — the no-arg `Handler()` constructor is deprecated and should be avoided.

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
// ❌ Potentially problematic: anonymous Handler class can hold Activity,
// and delayed messages/callbacks may run after it is destroyed
class MainActivity : AppCompatActivity() {
    private val handler = object : Handler(Looper.getMainLooper()) {
        override fun handleMessage(msg: Message) {
            textView.text = "Updated" // Implicit Activity reference
        }
    }
}

// ✅ Better: use a Handler with main looper and clear delayed
// messages/callbacks that might outlive the Activity
class MainActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    override fun onDestroy() {
        super.onDestroy()
        // Clear callbacks/messages that could survive Activity lifecycle
        handler.removeCallbacksAndMessages(null)
    }
}
```

The core idea: a Handler on the main Looper itself does not automatically cause a leak; the risk comes from posting delayed or long-lived tasks that capture an `Activity`/`Fragment` after it is destroyed.

### Handler Vs Coroutines

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
    // viewModelScope uses Dispatchers.Main by default, so updateUI
    // will be called on the main thread
    viewModelScope.launch {
        val data = withContext(Dispatchers.IO) { fetchData() }
        updateUI(data)
    }
}
```

**Key Points:**
- The main thread has a Looper by default
- `Looper.getMainLooper()` returns the main thread's Looper
- When using Handlers inside `Activity`/`Fragment`, clear delayed callbacks/messages that may outlive the component to avoid leaks
- For new projects, coroutines are generally preferred over direct Handler usage, with Handlers kept for low-level/legacy integrations

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

### Prerequisites / Concepts

- [[c-coroutines]]
- [[c-background-tasks]]

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
