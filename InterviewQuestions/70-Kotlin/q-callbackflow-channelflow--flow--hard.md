---
id: kotlin-flow-004
title: callbackFlow vs channelFlow / callbackFlow vs channelFlow
aliases:
- callbackFlow channelFlow
- Callback to Flow
- Channel Flow
topic: kotlin
subtopics:
- coroutines
- flow
- channels
question_kind: comparison
difficulty: hard
original_language: en
language_tags:
- en
- ru
source: internal
status: draft
moc: moc-kotlin
related:
- c-kotlin
- c-flow
- q-channelflow-callbackflow-flow--kotlin--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- coroutines
- difficulty/hard
- flow
- kotlin
- channels
- callbacks
anki_cards:
- slug: kotlin-flow-004-0-en
  language: en
  anki_id: 1769344130573
  synced_at: '2026-01-25T16:29:00.515685'
- slug: kotlin-flow-004-0-ru
  language: ru
  anki_id: 1769344130614
  synced_at: '2026-01-25T16:29:00.517403'
---
# Vopros (RU)
> Когда использовать `callbackFlow` vs `channelFlow`? В чём разница?

---

# Question (EN)
> When to use `callbackFlow` vs `channelFlow`? What's the difference?

## Otvet (RU)

### Обзор

Оба `callbackFlow` и `channelFlow` создают холодный Flow на основе `Channel`, позволяя эмитировать значения из разных корутин или callback-ов. Основное различие - в семантике и требованиях к lifecycle.

### channelFlow

`channelFlow` - базовый builder для создания Flow с возможностью конкурентных эмиссий:

```kotlin
val channelFlow = channelFlow {
    // Можно запускать корутины внутри
    launch {
        repeat(3) {
            send(it)
            delay(100)
        }
    }

    // Можно эмитировать из разных корутин
    launch {
        delay(50)
        send(100)
    }
}
```

**Когда использовать:**
- Когда нужно эмитировать из нескольких корутин
- Когда нужен параллелизм внутри Flow
- Когда нет внешних callback-ов

```kotlin
// Пример: параллельная загрузка
fun loadDataInParallel(ids: List<String>) = channelFlow {
    ids.forEach { id ->
        launch {
            val data = repository.load(id)
            send(data)  // send из разных корутин
        }
    }
}
```

### callbackFlow

`callbackFlow` - специализированный builder для адаптации callback-based API в Flow:

```kotlin
fun locationUpdates(): Flow<Location> = callbackFlow {
    val callback = object : LocationCallback() {
        override fun onLocationResult(result: LocationResult) {
            // trySend не suspend - безопасно из callback
            trySend(result.lastLocation)
        }
    }

    locationClient.requestLocationUpdates(request, callback, Looper.getMainLooper())

    // ОБЯЗАТЕЛЬНО: awaitClose для очистки
    awaitClose {
        locationClient.removeLocationUpdates(callback)
    }
}
```

**Ключевые отличия callbackFlow:**
1. Требует `awaitClose { }` - без него Flow завершится сразу
2. Предназначен для bridge между callback API и Flow
3. `trySend()` и `trySendBlocking()` для эмиссии из non-suspend контекста

### Сравнение

| Аспект | channelFlow | callbackFlow |
|--------|-------------|--------------|
| Назначение | Параллельные эмиссии | Адаптация callback API |
| awaitClose | Опционально | Обязательно |
| Типичный источник | Корутины | Внешние callback-и |
| Очистка ресурсов | Вручную | В awaitClose |

### Полные Примеры

#### callbackFlow - Firebase Realtime Database

```kotlin
fun observeUser(userId: String): Flow<User?> = callbackFlow {
    val listener = object : ValueEventListener {
        override fun onDataChange(snapshot: DataSnapshot) {
            val user = snapshot.getValue(User::class.java)
            trySend(user)
        }

        override fun onCancelled(error: DatabaseError) {
            close(error.toException())
        }
    }

    val ref = database.child("users").child(userId)
    ref.addValueEventListener(listener)

    awaitClose {
        ref.removeEventListener(listener)
    }
}
```

#### callbackFlow - BroadcastReceiver

```kotlin
fun batteryStatus(context: Context): Flow<Int> = callbackFlow {
    val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
            trySend(level)
        }
    }

    val filter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
    context.registerReceiver(receiver, filter)

    awaitClose {
        context.unregisterReceiver(receiver)
    }
}
```

#### callbackFlow - WebSocket

```kotlin
fun websocketMessages(url: String): Flow<Message> = callbackFlow {
    val socket = OkHttpClient().newWebSocket(
        Request.Builder().url(url).build(),
        object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                trySend(Message.Text(text))
            }

            override fun onMessage(webSocket: WebSocket, bytes: ByteString) {
                trySend(Message.Binary(bytes))
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                close(t)
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                close()
            }
        }
    )

    awaitClose {
        socket.close(1000, "Flow cancelled")
    }
}
```

#### channelFlow - Параллельная загрузка с прогрессом

```kotlin
sealed class DownloadState {
    data class Progress(val percent: Int) : DownloadState()
    data class Success(val file: File) : DownloadState()
    data class Error(val exception: Throwable) : DownloadState()
}

fun downloadWithProgress(url: String): Flow<DownloadState> = channelFlow {
    val progressJob = launch {
        var progress = 0
        while (progress < 100) {
            send(DownloadState.Progress(progress))
            delay(100)
            progress += 10
        }
    }

    try {
        val file = withContext(Dispatchers.IO) {
            downloadFile(url)
        }
        progressJob.cancel()
        send(DownloadState.Success(file))
    } catch (e: Exception) {
        progressJob.cancel()
        send(DownloadState.Error(e))
    }
}
```

### Методы Отправки

```kotlin
callbackFlow {
    // send() - suspend, блокирует если буфер полон
    send(value)

    // trySend() - non-suspend, возвращает ChannelResult
    val result = trySend(value)
    if (result.isFailure) {
        // Обработка: буфер полон или канал закрыт
    }

    // trySendBlocking() - блокирует поток (не корутину)
    // Использовать только когда нет suspend контекста
    trySendBlocking(value)

    awaitClose { }
}
```

### Распространённые Ошибки

```kotlin
// ОШИБКА: Забыли awaitClose
fun badFlow() = callbackFlow {
    val callback = { value: Int -> trySend(value) }
    api.registerCallback(callback)
    // Flow завершится немедленно!
    // Нет awaitClose
}

// ПРАВИЛЬНО:
fun goodFlow() = callbackFlow {
    val callback = { value: Int -> trySend(value) }
    api.registerCallback(callback)
    awaitClose {
        api.unregisterCallback(callback)
    }
}

// ОШИБКА: Использование send() вместо trySend() в callback
fun badCallbackFlow() = callbackFlow {
    val callback = object : Callback {
        override fun onResult(value: Int) {
            send(value)  // ОШИБКА: send() - suspend функция!
        }
    }
    // ...
}

// ПРАВИЛЬНО: trySend() в callback
fun goodCallbackFlow() = callbackFlow {
    val callback = object : Callback {
        override fun onResult(value: Int) {
            trySend(value)  // non-suspend, безопасно в callback
        }
    }
    // ...
}
```

### Buffer Overflow

```kotlin
// Настройка буфера для callbackFlow
fun highFrequencyEvents() = callbackFlow {
    // Настройка через buffer()
}.buffer(
    capacity = 64,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)

// Или внутри callbackFlow через channel
fun customBufferFlow() = callbackFlow {
    // Можно использовать channel.invokeOnClose для очистки
    channel.invokeOnClose {
        // Cleanup
    }

    awaitClose { }
}
```

---

## Answer (EN)

### Overview

Both `callbackFlow` and `channelFlow` create cold Flows based on `Channel`, allowing emissions from different coroutines or callbacks. The main difference is in semantics and lifecycle requirements.

### channelFlow

`channelFlow` - basic builder for creating Flow with concurrent emissions:

```kotlin
val channelFlow = channelFlow {
    // Can launch coroutines inside
    launch {
        repeat(3) {
            send(it)
            delay(100)
        }
    }

    // Can emit from different coroutines
    launch {
        delay(50)
        send(100)
    }
}
```

**When to use:**
- When you need to emit from multiple coroutines
- When you need parallelism inside Flow
- When there are no external callbacks

```kotlin
// Example: parallel loading
fun loadDataInParallel(ids: List<String>) = channelFlow {
    ids.forEach { id ->
        launch {
            val data = repository.load(id)
            send(data)  // send from different coroutines
        }
    }
}
```

### callbackFlow

`callbackFlow` - specialized builder for adapting callback-based APIs to Flow:

```kotlin
fun locationUpdates(): Flow<Location> = callbackFlow {
    val callback = object : LocationCallback() {
        override fun onLocationResult(result: LocationResult) {
            // trySend is not suspend - safe from callback
            trySend(result.lastLocation)
        }
    }

    locationClient.requestLocationUpdates(request, callback, Looper.getMainLooper())

    // REQUIRED: awaitClose for cleanup
    awaitClose {
        locationClient.removeLocationUpdates(callback)
    }
}
```

**Key differences of callbackFlow:**
1. Requires `awaitClose { }` - without it Flow completes immediately
2. Designed for bridging callback APIs to Flow
3. `trySend()` and `trySendBlocking()` for emission from non-suspend context

### Comparison

| Aspect | channelFlow | callbackFlow |
|--------|-------------|--------------|
| Purpose | Concurrent emissions | Adapt callback APIs |
| awaitClose | Optional | Required |
| Typical source | Coroutines | External callbacks |
| Resource cleanup | Manual | In awaitClose |

### Full Examples

#### callbackFlow - Firebase Realtime Database

```kotlin
fun observeUser(userId: String): Flow<User?> = callbackFlow {
    val listener = object : ValueEventListener {
        override fun onDataChange(snapshot: DataSnapshot) {
            val user = snapshot.getValue(User::class.java)
            trySend(user)
        }

        override fun onCancelled(error: DatabaseError) {
            close(error.toException())
        }
    }

    val ref = database.child("users").child(userId)
    ref.addValueEventListener(listener)

    awaitClose {
        ref.removeEventListener(listener)
    }
}
```

#### callbackFlow - BroadcastReceiver

```kotlin
fun batteryStatus(context: Context): Flow<Int> = callbackFlow {
    val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
            trySend(level)
        }
    }

    val filter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
    context.registerReceiver(receiver, filter)

    awaitClose {
        context.unregisterReceiver(receiver)
    }
}
```

#### callbackFlow - WebSocket

```kotlin
fun websocketMessages(url: String): Flow<Message> = callbackFlow {
    val socket = OkHttpClient().newWebSocket(
        Request.Builder().url(url).build(),
        object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                trySend(Message.Text(text))
            }

            override fun onMessage(webSocket: WebSocket, bytes: ByteString) {
                trySend(Message.Binary(bytes))
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                close(t)
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                close()
            }
        }
    )

    awaitClose {
        socket.close(1000, "Flow cancelled")
    }
}
```

#### channelFlow - Parallel Download with Progress

```kotlin
sealed class DownloadState {
    data class Progress(val percent: Int) : DownloadState()
    data class Success(val file: File) : DownloadState()
    data class Error(val exception: Throwable) : DownloadState()
}

fun downloadWithProgress(url: String): Flow<DownloadState> = channelFlow {
    val progressJob = launch {
        var progress = 0
        while (progress < 100) {
            send(DownloadState.Progress(progress))
            delay(100)
            progress += 10
        }
    }

    try {
        val file = withContext(Dispatchers.IO) {
            downloadFile(url)
        }
        progressJob.cancel()
        send(DownloadState.Success(file))
    } catch (e: Exception) {
        progressJob.cancel()
        send(DownloadState.Error(e))
    }
}
```

### Send Methods

```kotlin
callbackFlow {
    // send() - suspend, blocks if buffer is full
    send(value)

    // trySend() - non-suspend, returns ChannelResult
    val result = trySend(value)
    if (result.isFailure) {
        // Handle: buffer full or channel closed
    }

    // trySendBlocking() - blocks thread (not coroutine)
    // Use only when no suspend context available
    trySendBlocking(value)

    awaitClose { }
}
```

### Common Mistakes

```kotlin
// WRONG: Forgot awaitClose
fun badFlow() = callbackFlow {
    val callback = { value: Int -> trySend(value) }
    api.registerCallback(callback)
    // Flow completes immediately!
    // No awaitClose
}

// CORRECT:
fun goodFlow() = callbackFlow {
    val callback = { value: Int -> trySend(value) }
    api.registerCallback(callback)
    awaitClose {
        api.unregisterCallback(callback)
    }
}

// WRONG: Using send() instead of trySend() in callback
fun badCallbackFlow() = callbackFlow {
    val callback = object : Callback {
        override fun onResult(value: Int) {
            send(value)  // ERROR: send() is a suspend function!
        }
    }
    // ...
}

// CORRECT: trySend() in callback
fun goodCallbackFlow() = callbackFlow {
    val callback = object : Callback {
        override fun onResult(value: Int) {
            trySend(value)  // non-suspend, safe in callback
        }
    }
    // ...
}
```

### Buffer Overflow

```kotlin
// Configure buffer for callbackFlow
fun highFrequencyEvents() = callbackFlow {
    // Configure via buffer()
}.buffer(
    capacity = 64,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)

// Or inside callbackFlow via channel
fun customBufferFlow() = callbackFlow {
    // Can use channel.invokeOnClose for cleanup
    channel.invokeOnClose {
        // Cleanup
    }

    awaitClose { }
}
```

---

## Dopolnitelnye Voprosy (RU)

1. Как обрабатывать backpressure в `callbackFlow` когда источник эмитирует слишком быстро?
2. Можно ли использовать `callbackFlow` для однократных callback-ов?
3. Как тестировать Flow созданные через `callbackFlow`?
4. Чем `callbackFlow` лучше ручного создания `Channel`?
5. Как правильно обрабатывать ошибки в `callbackFlow`?

---

## Follow-ups

1. How to handle backpressure in `callbackFlow` when source emits too fast?
2. Can you use `callbackFlow` for one-shot callbacks?
3. How to test Flows created via `callbackFlow`?
4. Why is `callbackFlow` better than manually creating a `Channel`?
5. How to properly handle errors in `callbackFlow`?

---

## Ssylki (RU)

- [[c-kotlin]]
- [[c-flow]]
- [callbackFlow Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/callback-flow.html)

---

## References

- [[c-kotlin]]
- [[c-flow]]
- [callbackFlow Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/callback-flow.html)

---

## Svyazannye Voprosy (RU)

### Sredniy Uroven
- [[q-channelflow-callbackflow-flow--kotlin--medium]]
- [[q-flow-operators--flow--medium]]

### Prodvinutyy Uroven
- [[q-channel-pipelines--kotlin--hard]]

---

## Related Questions

### Related (Medium)
- [[q-channelflow-callbackflow-flow--kotlin--medium]] - callbackFlow and channelFlow basics
- [[q-flow-operators--flow--medium]] - Flow operators

### Advanced (Harder)
- [[q-channel-pipelines--kotlin--hard]] - Channel pipelines
