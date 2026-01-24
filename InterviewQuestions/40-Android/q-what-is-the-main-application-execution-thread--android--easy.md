---
id: android-207
title: What Is The Main Application Execution Thread / Что такое главный поток выполнения
  приложения
aliases:
- Main Thread
- UI Thread
- Главный поток
- Поток UI
topic: android
subtopics:
- lifecycle
- performance-rendering
- threads-sync
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
sources: []
status: draft
moc: moc-android
related:
- c-android-components
- q-handler-looper-main-thread--android--medium
- q-how-does-the-main-thread-work--android--medium
- q-main-thread-android--android--medium
created: 2024-10-15
updated: 2025-11-10
tags:
- android/lifecycle
- android/performance-rendering
- android/threads-sync
- difficulty/easy
anki_cards:
- slug: android-207-0-en
  language: en
  anki_id: 1768398853010
  synced_at: '2026-01-23T16:45:05.694551'
- slug: android-207-0-ru
  language: ru
  anki_id: 1768398853034
  synced_at: '2026-01-23T16:45:05.695802'
---
# Вопрос (RU)

> Что такое главный поток выполнения приложения в Android и для чего он используется?

# Question (EN)

> What is the main application execution thread in Android and what is it used for?

---

## Ответ (RU)

**Main `Thread`** (или **UI `Thread`**) — основной поток в Android-приложении, в котором выполняются все операции с пользовательским интерфейсом и большинство обратных вызовов жизненного цикла компонентов. Он создаётся вместе с процессом приложения и живёт, пока живёт процесс.

### Ключевые Характеристики

1. **Единственный UI-поток на процесс** — создаётся при старте процесса приложения и существует весь его жизненный цикл (дополнительные UI-потоки создавать нельзя).
2. **Все UI-операции** — только Main `Thread` может безопасно обращаться к `View` и другим UI-компонентам (в противном случае возможен `CalledFromWrongThreadException`).
3. **Event Loop** — поток использует `Looper` + `MessageQueue` для обработки сообщений и событий (touch, lifecycle callbacks, некоторые Binder callbacks, broadcasts). Все задачи выполняются по очереди в этом цикле сообщений.

### Правило 16ms (60 FPS)

Главный поток должен обработать логику кадра за **≈16ms** (60 FPS) или **≈11ms** (90 FPS):

```kotlin
// ❌ Плохо - блокирует UI
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    Thread.sleep(5000) // Зависание на 5 секунд
}

// ✅ Хорошо - асинхронная работа
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    lifecycleScope.launch {
        val data = withContext(Dispatchers.IO) {
            fetchDataFromNetwork() // Фоновая операция
        }
        textView.text = data // Обновление UI в главном потоке
    }
}
```

### Переключение На Главный Поток

```kotlin
// Вариант 1: runOnUiThread (из Activity)
Thread {
    val data = fetchData()
    runOnUiThread { textView.text = data }
}.start()

// Вариант 2: Handler с Looper главного потока
Handler(Looper.getMainLooper()).post {
    textView.text = data
}

// Вариант 3: Coroutines (рекомендуется для современного кода)
// В lifecycleScope (Activity/Fragment) по умолчанию используется Dispatchers.Main
lifecycleScope.launch {
    textView.text = data // Выполняется в Main Thread
}
```

### Проверка Текущего Потока

```kotlin
fun isMainThread(): Boolean =
    Looper.myLooper() == Looper.getMainLooper()
```

**Ответственность Main `Thread`:**
- Отрисовка UI (measure, layout, draw)
- Обработка пользовательских событий (touch, key events)
- `Lifecycle` callbacks (onCreate, onStart, onResume и др.)
- Вызовы `BroadcastReceiver.onReceive()` (если не указано иное)
- Обработка сообщений/колбэков, отправленных в основной `Looper`

## Answer (EN)

The **Main `Thread`** (also called the **UI `Thread`**) is the primary thread in an Android application where all UI operations and most component lifecycle callbacks are executed. It is created with the app process and exists as long as that process is alive.

### Key Characteristics

1. **Single UI thread per process** — created when the app process starts and exists for the lifetime of that process (you cannot create additional UI-capable threads).
2. **All UI operations** — only the Main `Thread` may safely access `View` and other UI toolkit components (otherwise you may get a `CalledFromWrongThreadException`).
3. **Event Loop** — the thread uses a `Looper` + `MessageQueue` to process messages and events (touch, lifecycle callbacks, some Binder callbacks, broadcasts). All tasks run sequentially on this message loop.

### The 16ms Rule (60 FPS)

The main thread should complete the work for each frame in about **16ms** (60 FPS) or **11ms** (90 FPS):

```kotlin
// ❌ Bad - blocks UI
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    Thread.sleep(5000) // Freezes for 5 seconds
}

// ✅ Good - async work
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    lifecycleScope.launch {
        val data = withContext(Dispatchers.IO) {
            fetchDataFromNetwork() // Background work
        }
        textView.text = data // UI update on the main thread
    }
}
```

### Switching to Main Thread

```kotlin
// Option 1: runOnUiThread (from an Activity)
Thread {
    val data = fetchData()
    runOnUiThread { textView.text = data }
}.start()

// Option 2: Handler with the main Looper
Handler(Looper.getMainLooper()).post {
    textView.text = data
}

// Option 3: Coroutines (recommended for modern code)
// In lifecycleScope (Activity/Fragment), Dispatchers.Main is used by default
lifecycleScope.launch {
    textView.text = data // Runs on the Main Thread
}
```

### Checking Current Thread

```kotlin
fun isMainThread(): Boolean =
    Looper.myLooper() == Looper.getMainLooper()
```

**Main `Thread` Responsibilities:**
- UI rendering (measure, layout, draw)
- Event handling (touch, key events)
- `Lifecycle` callbacks (onCreate, onStart, onResume, etc.)
- `BroadcastReceiver.onReceive()` calls (unless specified otherwise)
- Handling messages/callbacks posted to the main `Looper`

---

## Дополнительные Вопросы (RU)

- Что произойдет, если заблокировать Main `Thread` более чем на 5 секунд (например, ANR)?
- Как `Looper.loop()` поддерживает отзывчивость Main `Thread`, оставаясь блокирующим вызовом?
- Можно ли создать дополнительные UI-потоки в Android?
- В чем разница между `Handler.post()` и `Handler.postDelayed()`?
- Как корутины Kotlin обеспечивают выполнение обновлений UI в Main `Thread`?

## Follow-ups

- What happens if you block the Main `Thread` for more than 5 seconds (e.g., ANR)?
- How does `Looper.loop()` keep the Main `Thread` responsive while being a blocking call?
- Can you create additional UI threads in Android?
- What is the difference between `Handler.post()` and `Handler.postDelayed()`?
- How do Kotlin coroutines ensure UI updates run on the Main `Thread`?

## Ссылки (RU)

- [Android Processes and Threads](https://developer.android.com/guide/components/processes-and-threads)
- [Looper and Handler](https://developer.android.com/reference/android/os/Looper)
- [Kotlin Coroutines on Android](https://developer.android.com/kotlin/coroutines)

## References

- [Android Processes and Threads](https://developer.android.com/guide/components/processes-and-threads)
- [Looper and Handler](https://developer.android.com/reference/android/os/Looper)
- [Kotlin Coroutines on Android](https://developer.android.com/kotlin/coroutines)

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-android-components]]

### Предпосылки (проще)
- [[q-main-android-components--android--easy]] — Базовые компоненты Android

### Связанные (тот Же уровень)
- [[q-what-unifies-android-components--android--easy]] — Основы компонентов

### Продвинутые (сложнее)
- [[q-anr-application-not-responding--android--medium]] — Отладка ANR
- [[q-what-navigation-methods-do-you-know--android--medium]] — Архитектура навигации

## Related Questions

### Prerequisites / Concepts

- [[c-android-components]]

### Prerequisites (Easier)
- [[q-main-android-components--android--easy]] — Basic Android components

### Related (Same Level)
- [[q-what-unifies-android-components--android--easy]] — `Component` fundamentals

### Advanced (Harder)
- [[q-anr-application-not-responding--android--medium]] — ANR debugging
- [[q-what-navigation-methods-do-you-know--android--medium]] — Navigation architecture
