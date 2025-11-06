---
id: android-393
title: Android App Components / Компоненты Android приложения
aliases: [Android App Components, Компоненты Android приложения]
topic: android
subtopics:
  - activity
  - broadcast-receiver
  - service
question_kind: android
difficulty: easy
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-broadcast-receiver
  - c-content-provider
  - c-service
  - q-activity-lifecycle-methods--android--medium
  - q-service-types-android--android--easy
created: 2025-10-15
updated: 2025-10-29
sources: []
tags: [android/activity, android/broadcast-receiver, android/service, difficulty/easy]
---

# Вопрос (RU)
> Назовите четыре основных компонента Android приложения и их назначение.

---

# Question (EN)
> What are the four fundamental components of an Android application?

---

## Ответ (RU)

Android определяет четыре типа компонентов приложения: **`Activity`**, **[[c-service|Service]]**, **[[c-broadcast-receiver|Broadcast Receiver]]** и **[[c-content-provider|Content Provider]]**. Все компоненты объявляются в `AndroidManifest.xml` и взаимодействуют через **`Intent`**.

### 1. `Activity`

Представляет один экран с UI. Управляет жизненным циклом (`onCreate`, `onStart`, `onResume`, `onPause`, `onStop`, `onDestroy`) и обрабатывает ввод пользователя.

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        // ✅ Инициализация UI и восстановление состояния
    }
}
```

### 2. `Service`

Выполняет длительные операции в фоне без UI. Три типа:
- **Started**: запускается через `startService()`, работает независимо
- **Bound**: связан с компонентом через `bindService()`, живёт пока есть привязки
- **Foreground**: видим пользователю (нотификация), защищён от завершения

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Воспроизведение музыки в фоне
        return START_STICKY  // ✅ Перезапуск после kill
    }

    override fun onBind(intent: Intent?): IBinder? = null  // ❌ Unbound service
}
```

### 3. Broadcast Receiver

Реагирует на системные или пользовательские события. Регистрация:
- **Статическая** (manifest): получает события даже когда приложение не запущено
- **Динамическая** (код): работает только пока компонент активен

```kotlin
class BatteryReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
            Intent.ACTION_BATTERY_LOW -> // ✅ Реакция на низкий заряд
        }
    }
}
```

### 4. Content Provider

Управляет общими данными приложения и обеспечивает безопасный доступ для других приложений через стандартизированный URI-интерфейс. Контролирует разрешения на чтение/запись.

```kotlin
class ContactsProvider : ContentProvider() {
    override fun query(
        uri: Uri, projection: Array<String>?,
        selection: String?, selectionArgs: Array<String>?, sortOrder: String?
    ): Cursor? {
        // ✅ Возврат данных через Cursor
        return database.query(uri, projection, selection, selectionArgs, sortOrder)
    }
}
```

### Взаимодействие Компонентов

- **`Intent`**: явные (конкретный класс) или неявные (action/category)
- **`Intent` Filter**: объявляет возможности компонента для неявных `Intent`
- **Manifest**: обязательная регистрация + разрешения

---

## Answer (EN)

Android defines four application components: **`Activity`**, **[[c-service|Service]]**, **[[c-broadcast-receiver|Broadcast Receiver]]**, and **[[c-content-provider|Content Provider]]**. All components are declared in `AndroidManifest.xml` and interact via **`Intent`**.

### 1. `Activity`

Represents a single screen with UI. Manages lifecycle (`onCreate`, `onStart`, `onResume`, `onPause`, `onStop`, `onDestroy`) and handles user input.

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        // ✅ UI initialization and state restoration
    }
}
```

### 2. `Service`

Performs long-running background operations without UI. Three types:
- **Started**: launched via `startService()`, runs independently
- **Bound**: bound to component via `bindService()`, lives while bindings exist
- **Foreground**: visible to user (notification), protected from termination

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Background music playback
        return START_STICKY  // ✅ Restart after kill
    }

    override fun onBind(intent: Intent?): IBinder? = null  // ❌ Unbound service
}
```

### 3. Broadcast Receiver

Responds to system-wide or custom events. Registration:
- **Static** (manifest): receives events even when app is not running
- **Dynamic** (code): works only while component is active

```kotlin
class BatteryReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
            Intent.ACTION_BATTERY_LOW -> // ✅ React to battery low
        }
    }
}
```

### 4. Content Provider

Manages shared application data and provides secure access for other apps through standardized URI interface. Controls read/write permissions.

```kotlin
class ContactsProvider : ContentProvider() {
    override fun query(
        uri: Uri, projection: Array<String>?,
        selection: String?, selectionArgs: Array<String>?, sortOrder: String?
    ): Cursor? {
        // ✅ Return data via Cursor
        return database.query(uri, projection, selection, selectionArgs, sortOrder)
    }
}
```

### Component Communication

- **`Intent`**: explicit (specific class) or implicit (action/category)
- **`Intent` Filter**: declares component capabilities for implicit intents
- **Manifest**: mandatory registration + permissions

---

## Follow-ups

- What are the lifecycle differences between started, bound, and foreground services?
- When should you use static vs dynamic `BroadcastReceiver` registration?
- How does Android determine which component receives an implicit `Intent`?
- What happens when a process with a `Service` is killed by the system?
- How do Content Providers handle concurrent access to data?

## References

- [[c-service]] - `Service` implementation patterns
- [[c-broadcast-receiver]] - Receiver registration and security
- [[c-content-provider]] - Data sharing and URIs
- https://developer.android.com/guide/components/fundamentals - Official Android Components Guide
- https://developer.android.com/guide/components/intents-filters - `Intent` and `Intent` Filters

## Related Questions

### Prerequisites
- [[q-what-is-intent--android--easy]] - `Intent` basics for component communication

### Related
- [[q-activity-lifecycle-methods--android--medium]] - `Activity` lifecycle states and callbacks
- [[q-service-types-android--android--easy]] - `Service` types and use cases
- [[q-how-to-register-broadcastreceiver-to-receive-messages--android--medium]] - `BroadcastReceiver` registration patterns

### Advanced
- Process lifecycle and component priority in Android
- Inter-process communication mechanisms (AIDL, Binder)
- Content Provider URI design and permission handling