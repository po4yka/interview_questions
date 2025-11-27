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
status: draft
moc: moc-android
related:
  - c-broadcast-receiver
  - c-content-provider
  - c-service
  - q-activity-lifecycle-methods--android--medium
  - q-android-app-bundles--android--easy
  - q-android-components-besides-activity--android--easy
  - q-how-to-start-drawing-ui-in-android--android--easy
  - q-service-types-android--android--easy
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/activity, android/broadcast-receiver, android/service, difficulty/easy]

date created: Saturday, November 1st 2025, 12:46:42 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---
# Вопрос (RU)
> Назовите четыре основных компонента Android приложения и их назначение.

---

# Question (EN)
> What are the four fundamental components of an Android application and what is their purpose?

---

## Ответ (RU)

Android определяет четыре типа компонентов приложения: **`Activity`**, **[[c-service|`Service`]]**, **[[c-broadcast-receiver|Broadcast Receiver]]** и **[[c-content-provider|Content Provider]]**. Обычно компоненты объявляются в `AndroidManifest.xml`, а также могут регистрироваться динамически из кода (например, `BroadcastReceiver`). Они взаимодействуют через **`Intent`**.

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

Выполняет длительные операции в фоне без UI. Три основных типа:
- **Started**: запускается через `startService()` / `startForegroundService()` (Android 8+ для запуска из фона), работает независимо от вызывающего компонента
- **Bound**: связан с компонентом через `bindService()`, живёт пока есть привязки
- **Foreground**: показывает постоянную нотификацию, имеет повышенный приоритет и меньше шансов быть убитым системой

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Воспроизведение музыки в фоне
        return START_STICKY  // ✅ Система попытается перезапустить после kill; intent может быть null
    }

    override fun onBind(intent: Intent?): IBinder? = null  // ❌ Не предоставляет привязанный интерфейс (started-only service)
}
```

### 3. Broadcast Receiver

Реагирует на системные или пользовательские события. Регистрация:
- **Статическая** (manifest): может получать определённые широковещательные сообщения даже когда приложение не запущено (с учётом ограничений Android 8+ на implicit broadcasts)
- **Динамическая** (код): работает только пока компонент активен; используется для большинства случаев, особенно для ограниченных implicit broadcasts

```kotlin
class BatteryReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
            Intent.ACTION_BATTERY_LOW -> {
                // ✅ Реакция на низкий заряд
            }
        }
    }
}
```

### 4. Content Provider

Управляет общими данными приложения и обеспечивает безопасный доступ для других приложений через стандартизированный URI-интерфейс. Контролирует разрешения на чтение/запись.

```kotlin
class ContactsProvider : ContentProvider() {
    override fun query(
        uri: Uri,
        projection: Array<String>?,
        selection: String?,
        selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? {
        // ✅ Возврат данных через Cursor (псевдокод; реализация зависит от хранилища)
        return database.query(/* ... */)
    }
}
```

### Взаимодействие Компонентов

- **`Intent`**: явные (конкретный класс) или неявные (action/category)
- **`Intent` Filter**: объявляет возможности компонента для неявных `Intent`
- **Manifest**: регистрация компонентов и разрешений; часть поведения (особенно `BroadcastReceiver`) зависит от ограничений конкретной версии Android

---

## Answer (EN)

Android defines four application components: **`Activity`**, **[[c-service|`Service`]]**, **[[c-broadcast-receiver|Broadcast Receiver]]**, and **[[c-content-provider|Content Provider]]**. Components are typically declared in `AndroidManifest.xml`, and some (such as `BroadcastReceiver`) can also be registered dynamically in code. They communicate via **Intents**.

### 1. `Activity`

Represents a single screen with UI. Manages the lifecycle (`onCreate`, `onStart`, `onResume`, `onPause`, `onStop`, `onDestroy`) and handles user input.

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

Performs long-running background operations without a UI. Three main types:
- **Started**: launched via `startService()` / `startForegroundService()` (Android 8+ when started from background), runs independently of the caller
- **Bound**: bound to a component via `bindService()`, lives while clients are bound
- **Foreground**: shows a persistent notification, has higher priority and is less likely to be killed

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Background music playback
        return START_STICKY  // ✅ System attempts to restart after kill; intent may be null
    }

    override fun onBind(intent: Intent?): IBinder? = null  // ❌ No bound interface (started-only service)
}
```

### 3. Broadcast Receiver

Responds to system-wide or custom events. Registration:
- **Static** (manifest): can receive certain broadcasts even when the app is not running (subject to Android 8+ restrictions on implicit broadcasts)
- **Dynamic** (in code): active only while the registering component is running; recommended for many cases, especially restricted implicit broadcasts

```kotlin
class BatteryReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
            Intent.ACTION_BATTERY_LOW -> {
                // ✅ React to battery low
            }
        }
    }
}
```

### 4. Content Provider

Manages shared application data and provides secure access for other apps through a standardized URI interface. Controls read/write permissions.

```kotlin
class ContactsProvider : ContentProvider() {
    override fun query(
        uri: Uri,
        projection: Array<String>?,
        selection: String?,
        selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? {
        // ✅ Return data via Cursor (pseudo-code; actual implementation depends on storage)
        return database.query(/* ... */)
    }
}
```

### Component Communication

- **`Intent`**: explicit (specific class) or implicit (action/category)
- **`Intent` Filter**: declares component capabilities for implicit intents
- **Manifest**: component and permission declarations; behavior (especially for BroadcastReceivers) is subject to Android version-specific restrictions

---

## Дополнительные Вопросы (RU)

- В чем различия жизненного цикла между started-, bound- и foreground-сервисами?
- Когда стоит использовать статическую, а когда динамическую регистрацию `BroadcastReceiver`?
- Как Android определяет, какой компонент получит неявный `Intent`?
- Что происходит, когда процесс с `Service` завершается системой?
- Как `Content Provider` обрабатывает конкурентный доступ к данным?

## Follow-ups

- What are the lifecycle differences between started, bound, and foreground services?
- When should you use static vs dynamic `BroadcastReceiver` registration?
- How does Android determine which component receives an implicit `Intent`?
- What happens when a process with a `Service` is killed by the system?
- How do Content Providers handle concurrent access to data?

## Ссылки (RU)

- [[c-service]] - шаблоны реализации `Service`
- [[c-broadcast-receiver]] - регистрация ресиверов и безопасность
- [[c-content-provider]] - обмен данными и URI
- https://developer.android.com/guide/components/fundamentals - официальное руководство по компонентам Android
- https://developer.android.com/guide/components/intents-filters - `Intent` и фильтры `Intent`

## References

- [[c-service]] - `Service` implementation patterns
- [[c-broadcast-receiver]] - Receiver registration and security
- [[c-content-provider]] - Data sharing and URIs
- https://developer.android.com/guide/components/fundamentals - Official Android Components Guide
- https://developer.android.com/guide/components/intents-filters - `Intent` and `Intent` Filters

## Связанные Вопросы (RU)

### Предпосылки
- [[q-what-is-intent--android--easy]] - основы `Intent` для взаимодействия компонентов

### Связанные
- [[q-activity-lifecycle-methods--android--medium]] - состояния и колбэки жизненного цикла `Activity`
- [[q-service-types-android--android--easy]] - типы `Service` и сценарии использования
- [[q-how-to-register-broadcastreceiver-to-receive-messages--android--medium]] - варианты регистрации `BroadcastReceiver`

### Продвинутое
- Жизненный цикл процессов и приоритеты компонентов в Android
- Механизмы межпроцессного взаимодействия (AIDL, Binder)
- Проектирование URI и управление разрешениями в `Content Provider`

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
