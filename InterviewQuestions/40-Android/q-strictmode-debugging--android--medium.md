---
id: android-331
title: StrictMode Debugging / Отладка StrictMode
aliases:
- StrictMode Debugging
- Отладка StrictMode
topic: android
subtopics:
- performance-rendering
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-performance
- q-compose-core-components--android--medium
- q-dagger-build-time-optimization--android--medium
- q-data-sync-unstable-network--android--hard
- q-migration-to-compose--android--medium
- q-real-time-updates-android--android--medium
- q-what-are-fragments-for-if-there-is-activity--android--medium
created: 2025-10-15
updated: 2025-11-11
tags:
- android/performance-rendering
- difficulty/medium
source: https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20is%20StrictMode.md
anki_cards:
- slug: android-331-0-ru
  language: ru
  anki_id: 1768420618793
  synced_at: '2026-01-14 23:56:58.797492'
- slug: android-331-0-en
  language: en
  anki_id: 1768420618765
  synced_at: '2026-01-14 23:56:58.768125'
---
# Вопрос (RU)
> Отладка StrictMode

# Question (EN)
> StrictMode Debugging

---

## Ответ (RU)
`StrictMode` — это инструмент для разработчиков, который помогает обнаруживать потенциально опасные или неэффективные действия (часто совершаемые по ошибке) и обращать на них внимание, чтобы вы могли их исправить.

`StrictMode` чаще всего используется для обнаружения случайного доступа к диску или сети в основном потоке приложения, где выполняются UI-операции и анимации. Вынос дисковых и сетевых операций из основного потока делает приложения более плавными и отзывчивыми и снижает вероятность появления ANR.

## Пример Использования

Пример кода для включения `StrictMode` на ранней стадии в `Activity` или `Application` (в их методах `onCreate()`). В реальных проектах такие настройки обычно оборачивают в проверку `BuildConfig.DEBUG` и используют строгие политики только в debug-сборках:

```kotlin
// Пример для Activity
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    if (BuildConfig.DEBUG) {
        StrictMode.setThreadPolicy(
            StrictMode.ThreadPolicy.Builder()
                .detectAll()
                .penaltyLog()
                .build()
        )
        StrictMode.setVmPolicy(
            StrictMode.VmPolicy.Builder()
                .detectAll()
                .penaltyLog()
                .build()
        )
    }
}

// Пример для Application
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        if (BuildConfig.DEBUG) {
            StrictMode.setThreadPolicy(
                StrictMode.ThreadPolicy.Builder()
                    .detectAll()
                    .penaltyLog()
                    .build()
            )
            StrictMode.setVmPolicy(
                StrictMode.VmPolicy.Builder()
                    .detectAll()
                    .penaltyLog()
                    .build()
            )
        }
    }
}
```

Примечание: если вы задаёте политику, вызывая только методы `detect*()` без `penalty*()`, нарушения будут определяться, но не будут наглядно сообщаться. На практике всегда добавляйте хотя бы один `penalty*()`, например `penaltyLog()`.

Вы можете настроить, что должно происходить при обнаружении нарушения. Например, используя `StrictMode.ThreadPolicy.Builder().penaltyLog()`, можно отслеживать нарушения в выводе `adb logcat` во время работы приложения.

## Типы Наказаний

`StrictMode` использует «penalty» для сигнализации о нарушениях:

### penaltyLog()

Записывает нарушение в системный logcat, упрощая поиск причин проблемы.

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectAll()
        .penaltyLog()
        .build()
)
```

### penaltyDeath()

Радикальная мера: приложение аварийно завершается при нарушении. Полезно для немедленного выявления серьёзных проблем во время разработки.

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectAll()
        .penaltyDeath()
        .build()
)
```

### penaltyDialog()

Отображает диалоговое окно пользователю при нарушении (обычно используется только при отладке, а не в продакшене).

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectAll()
        .penaltyDialog()
        .build()
)
```

**Примечание**: доступные политики и "penalty" в `StrictMode` изменялись между версиями Android. Примеры не являются исчерпывающим списком — сверяйтесь с документацией для вашей min/target SDK; часть API доступна только на новых версиях.

## Thread Policy

`Thread` policy описывает правила для конкретного потока (обычно основного), фиксируя опасные операции:

### Общие Обнаружения

- **detectDiskReads()** — Обнаруживает чтение с диска в потоке с этой политикой (обычно основной поток).
- **detectDiskWrites()** — Обнаруживает запись на диск в этом потоке.
- **detectNetwork()** — Обнаруживает сетевые операции в этом потоке.
- **detectCustomSlowCalls()** — Обнаруживает медленные операции, явно помеченные вызовами `StrictMode.noteSlowCall()`.
- **detectAll()** — Включает все доступные для текущего уровня API проверки thread policy.

### Пример

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectDiskReads()
        .detectDiskWrites()
        .detectNetwork()
        .penaltyLog()
        .build()
)

// Это вызовет нарушение (если политика применяется в основном потоке):
val file = File("/sdcard/test.txt")
file.writeText("Hello World") // Запись на диск в основном потоке!
```

## VM Policy

VM policy описывает проверки на уровне всего процесса приложения:

### Общие Обнаружения

- **detectActivityLeaks()** — Обнаруживает утечки экземпляров `Activity`.
- **detectLeakedClosableObjects()** — Обнаруживает незакрытые `Closeable`-объекты (потоки, курсоры и т.п.).
- **detectLeakedSqlLiteObjects()** — Обнаруживает незакрытые объекты `SQLite` (устаревший метод в новых версиях API, приведён для полноты картины).
- **detectLeakedRegistrationObjects()** — Обнаруживает утечки `BroadcastReceiver` и `ServiceConnection`.
- **detectFileUriExposure()** — Обнаруживает раскрытие `file://`-URI за пределы приложения (на соответствующих уровнях API).
- **detectAll()** — Включает все доступные для текущего уровня API проверки VM policy.

(На новых уровнях API доступны дополнительные проверки, а часть методов помечена устаревшими; см. официальную документацию.)

### Пример

```kotlin
StrictMode.setVmPolicy(
    StrictMode.VmPolicy.Builder()
        .detectActivityLeaks()
        .detectLeakedClosableObjects()
        .penaltyLog()
        .build()
)

// Это вызовет нарушение:
val cursor = database.query(...) // Не закрытый курсор может привести к утечке
```

## Лучшие Практики

### 1. Включайте Только В Debug-сборках

```kotlin
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectAll()
            .penaltyLog()
            .build()
    )
    StrictMode.setVmPolicy(
        StrictMode.VmPolicy.Builder()
            .detectAll()
            .penaltyLog()
            .build()
    )
}
```

### 2. Используйте penaltyLog() При Разработке

Используйте `penaltyLog()` во время разработки, чтобы фиксировать нарушения без немедленных падений приложения.

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectAll()
        .penaltyLog()
        .build()
)
```

### 3. Используйте penaltyDeath() Для Критических Проблем

Для нарушений, которые категорически недопустимы, можно использовать `penaltyDeath()`, чтобы немедленно их выявлять во время разработки.

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectNetwork()
        .penaltyDeath()
        .build()
)
```

### 4. Настройка Под Разные Сценарии

```kotlin
// Строгая политика для разработки
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectAll()
            .penaltyDeath()
            .build()
    )
} else {
    // В продакшене StrictMode обычно ослабляют или отключают,
    // но это не должно быть оправданием для тяжёлых операций в основном потоке.
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .permitAll()
            .build()
    )
}
```

## Распространённые Нарушения И Их Исправления

### 1. Сетевые Вызовы В Основном Потоке

**Проблема:**
```kotlin
// - ПЛОХО - Сетевой вызов в основном потоке
fun loadData() {
    val response = httpClient.get("https://api.example.com/data")
}
```

**Решение:**
```kotlin
// - ХОРОШО - Перенос в фоновый поток
suspend fun loadData() = withContext(Dispatchers.IO) {
    val response = httpClient.get("https://api.example.com/data")
}
```

### 2. Дисковый I/O В Основном Потоке

**Проблема:**
```kotlin
// - ПЛОХО - Чтение файла в основном потоке
fun loadConfig(): String {
    return File("config.txt").readText()
}
```

**Решение:**
```kotlin
// - ХОРОШО - Перенос в фоновый поток
suspend fun loadConfig(): String = withContext(Dispatchers.IO) {
    File("config.txt").readText()
}
```

### 3. Утечки Закрываемых Объектов

**Проблема:**
```kotlin
// - ПЛОХО - Курсор не закрыт
fun getUsers(): List<User> {
    val cursor = database.query(...)
    val users = mutableListOf<User>()
    while (cursor.moveToNext()) {
        users.add(User(cursor))
    }
    return users
}
```

**Решение:**
```kotlin
// - ХОРОШО - Корректно закрывать курсор
fun getUsers(): List<User> {
    database.query(...).use { cursor ->
        val users = mutableListOf<User>()
        while (cursor.moveToNext()) {
            users.add(User(cursor))
        }
        return users
    }
}
```

## Answer (EN)
`StrictMode` is a developer tool which detects things you might be doing by accident and brings them to your attention so you can fix them.

`StrictMode` is most commonly used to catch accidental disk or network access on the application's main thread, where UI operations are received and animations take place. Keeping disk and network operations off the main thread makes for much smoother, more responsive applications. By keeping your application's main thread responsive, you also reduce the chance of ANR dialogs being shown to users.

## Example Usage

Example code to enable `StrictMode` early in your `Activity` or `Application` (in their respective `onCreate()` methods). In real projects you normally wrap this in a `BuildConfig.DEBUG` check and keep strict policies only in debug builds:

```kotlin
// Activity example
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    if (BuildConfig.DEBUG) {
        StrictMode.setThreadPolicy(
            StrictMode.ThreadPolicy.Builder()
                .detectAll()
                .penaltyLog()
                .build()
        )
        StrictMode.setVmPolicy(
            StrictMode.VmPolicy.Builder()
                .detectAll()
                .penaltyLog()
                .build()
        )
    }
}

// Application example
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        if (BuildConfig.DEBUG) {
            StrictMode.setThreadPolicy(
                StrictMode.ThreadPolicy.Builder()
                    .detectAll()
                    .penaltyLog()
                    .build()
            )
            StrictMode.setVmPolicy(
                StrictMode.VmPolicy.Builder()
                    .detectAll()
                    .penaltyLog()
                    .build()
            )
        }
    }
}
```

Note: If you configure a policy using only `detect*()` calls without any `penalty*()` calls, violations will be detected but not reported in a visible way. In practice, always add at least one penalty such as `penaltyLog()`.

You can decide what should happen when a violation is detected. For example, using `StrictMode.ThreadPolicy.Builder().penaltyLog()` you can watch the output of adb logcat while you use your application to see the violations as they happen.

## Penalty Types

`StrictMode` uses penalties to signal violations:

### penaltyLog()

Logs the violation in the system logcat, making it easy to see what went wrong.

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectAll()
        .penaltyLog()
        .build()
)
```

### penaltyDeath()

A drastic measure, forcing the app to crash on a violation. Useful for catching severe problems immediately during development.

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectAll()
        .penaltyDeath()
        .build()
)
```

### penaltyDialog()

Displays a dialog to the user (primarily useful during development; not typically used in production).

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectAll()
        .penaltyDialog()
        .build()
)
```

**Note**: The exact policies and penalties offered by `StrictMode` have evolved over Android versions. Examples here are illustrative, not exhaustive. Some APIs (including certain penalties and detections) are only available on newer API levels; always refer to the documentation for your min/target SDK.

## Thread Policy

`Thread` policy detects certain violations that occur on specific threads (commonly configured for the main thread):

### Common Detections

- **detectDiskReads()** - Detects when your app reads from disk on the thread under this policy (usually the main thread).
- **detectDiskWrites()** - Detects when your app writes to disk on that thread.
- **detectNetwork()** - Detects when your app does network operations on that thread.
- **detectCustomSlowCalls()** - Detects when your code does slow operations marked with `StrictMode.noteSlowCall()`.
- **detectAll()** - Enables all available thread policy detections for the current API level.

### Example

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectDiskReads()
        .detectDiskWrites()
        .detectNetwork()
        .penaltyLog()
        .build()
)

// This will trigger a violation (if this policy is on the main thread):
val file = File("/sdcard/test.txt")
file.writeText("Hello World") // Disk write on main thread!
```

## VM Policy

VM policy detects violations across your entire application process:

### Common Detections

- **detectActivityLeaks()** - Detects when `Activity` instances are leaked.
- **detectLeakedClosableObjects()** - Detects when closeable objects (like Streams or Cursors) are not closed.
- **detectLeakedSqlLiteObjects()** - Detects when `SQLite` objects are not closed. (Deprecated in newer API levels; kept here for legacy awareness.)
- **detectLeakedRegistrationObjects()** - Detects when `BroadcastReceiver` or `ServiceConnection` instances are leaked.
- **detectFileUriExposure()** - Detects when `file://` URIs are exposed beyond your app on API levels where this is relevant.
- **detectAll()** - Enables all available VM policy detections for the current API level.

(Additional detections exist and some methods are deprecated on newer API levels; consult the current documentation.)

### Example

```kotlin
StrictMode.setVmPolicy(
    StrictMode.VmPolicy.Builder()
        .detectActivityLeaks()
        .detectLeakedClosableObjects()
        .penaltyLog()
        .build()
)

// This will trigger a violation:
val cursor = database.query(...) // Not closing cursor can cause a leak
```

## Best Practices

### 1. Enable Only in Debug Builds

```kotlin
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectAll()
            .penaltyLog()
            .build()
    )
    StrictMode.setVmPolicy(
        StrictMode.VmPolicy.Builder()
            .detectAll()
            .penaltyLog()
            .build()
    )
}
```

### 2. Use penaltyLog() in Development

Use `penaltyLog()` during development to catch issues without crashing your app.

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectAll()
        .penaltyLog() // Just log, don't crash
        .build()
)
```

### 3. Use penaltyDeath() for Critical Issues

For critical violations that should never happen, use `penaltyDeath()` to catch them immediately during development:

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectNetwork()
        .penaltyDeath() // Crash on network access from main thread
        .build()
)
```

### 4. Customize for Different Scenarios

```kotlin
// Strict policy for development
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectAll()
            .penaltyDeath()
            .build()
    )
} else {
    // In production you typically relax or disable StrictMode,
    // but avoid using this as justification for main-thread I/O.
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .permitAll()
            .build()
    )
}
```

## Common Violations and Fixes

### 1. Network on Main Thread

**Problem:**
```kotlin
// - BAD - Network call on main thread
fun loadData() {
    val response = httpClient.get("https://api.example.com/data")
}
```

**Solution:**
```kotlin
// - GOOD - Move to background thread
suspend fun loadData() = withContext(Dispatchers.IO) {
    val response = httpClient.get("https://api.example.com/data")
}
```

### 2. Disk I/O on Main Thread

**Problem:**
```kotlin
// - BAD - Reading file on main thread
fun loadConfig(): String {
    return File("config.txt").readText()
}
```

**Solution:**
```kotlin
// - GOOD - Move to background thread
suspend fun loadConfig(): String = withContext(Dispatchers.IO) {
    File("config.txt").readText()
}
```

### 3. Leaked Closeable Objects

**Problem:**
```kotlin
// - BAD - Cursor not closed
fun getUsers(): List<User> {
    val cursor = database.query(...)
    val users = mutableListOf<User>()
    while (cursor.moveToNext()) {
        users.add(User(cursor))
    }
    return users
}
```

**Solution:**
```kotlin
// - GOOD - Close cursor properly
fun getUsers(): List<User> {
    database.query(...).use { cursor ->
        val users = mutableListOf<User>()
        while (cursor.moveToNext()) {
            users.add(User(cursor))
        }
        return users
    }
}
```

## Ссылки (RU)

- [StrictMode](https://developer.android.com/reference/android/os/StrictMode)
- [StrictMode: Your Android App's Watchdog](https://medium.com/@sandeepkella23/strictmode-your-android-apps-watchdog-4c97be188d57)
- [Smooth Operator: Using StrictMode to make your Android App ANR free](https://riggaroo.dev/smooth-operator-using-strictmode-to-make-your-android-app-anr-free/)
- [Android Best Practices: StrictMode](https://code.tutsplus.com/android-best-practices-strictmode--mobile-7581t)
- [Raising the Bar with Android StrictMode](https://medium.com/wizeline-mobile/raising-the-bar-with-android-strictmode-7042d8a9e67b)

## Follow-ups (RU)

- [[q-migration-to-compose--android--medium]]
- [[q-real-time-updates-android--android--medium]]
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]]

## References (EN)

- [StrictMode](https://developer.android.com/reference/android/os/StrictMode)
- [StrictMode: Your Android App's Watchdog](https://medium.com/@sandeepkella23/strictmode-your-android-apps-watchdog-4c97be188d57)
- [Smooth Operator: Using StrictMode to make your Android App ANR free](https://riggaroo.dev/smooth-operator-using-strictmode-to-make-your-android-app-anr-free/)
- [Android Best Practices: StrictMode](https://code.tutsplus.com/android-best-practices-strictmode--mobile-7581t)
- [Raising the Bar with Android StrictMode](https://medium.com/wizeline-mobile/raising-the-bar-with-android-strictmode-7042d8a9e67b)
- [Rendering Performance](https://developer.android.com/topic/performance/rendering)

## Follow-ups (EN)

- [[q-migration-to-compose--android--medium]]
- [[q-real-time-updates-android--android--medium]]
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]]

## Related Questions (EN)

### Prerequisites / Concepts (EN)

- [[c-performance]]

- [[q-real-time-updates-android--android--medium]]
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]]
- [[q-migration-to-compose--android--medium]]
