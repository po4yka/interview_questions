---
id: android-358
anki_cards:
- slug: android-358-0-en
  language: en
  anki_id: 1768414151417
  synced_at: '2026-01-23T16:45:06.219989'
- slug: android-358-0-ru
  language: ru
  anki_id: 1768414151441
  synced_at: '2026-01-23T16:45:06.220841'
title: Main Android Components / Основные компоненты Android
aliases:
- Main Android Components
- Основные компоненты Android
topic: android
subtopics:
- activity
- content-provider
- service
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-activity
- c-android-components
- c-content-provider
- q-android-components-besides-activity--android--easy
- q-how-does-activity-lifecycle-work--android--medium
- q-main-thread-android--android--medium
- q-what-unifies-android-components--android--easy
- q-what-unites-the-main-components-of-an-android-application--android--medium
sources: []
created: 2025-10-15
updated: 2025-11-10
tags:
- android
- android/activity
- android/content-provider
- android/service
- components
- difficulty/easy
---
# Вопрос (RU)

> Какие основные компоненты Android-приложения?

# Question (EN)

> What are the main Android application components?

## Ответ (RU)

**Четыре основных компонента Android:**

**1. `Activity`** - экран пользовательского интерфейса
- Представляет один экран с UI
- Точка взаимодействия пользователя с приложением
- Пример: экран входа, экран профиля

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

**2. `Service`** - фоновые операции
- Выполняет длительные операции без пользовательского интерфейса
- Работает в фоновом режиме
- Пример: воспроизведение музыки, синхронизация данных

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // START_STICKY сообщает системе попытаться перезапустить сервис после kill,
        // но момент и наличие исходного Intent не гарантируются
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**3. `BroadcastReceiver`** - обработчик системных событий
- Слушает системные или пользовательские broadcast-сообщения
- Реагирует на изменения состояния системы
- Пример: изменение сети, низкий заряд батареи

```kotlin
class NetworkReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val isConnected = checkNetworkStatus(context)
        // Обработка изменения состояния сети
    }
}
```

**4. `ContentProvider`** - управление и обмен данными
- Централизованное хранилище данных приложения
- Обеспечивает контролируемый доступ к данным из других приложений
- Пример: Contacts, MediaStore

```kotlin
class MyContentProvider : ContentProvider() {
    override fun query(
        uri: Uri, projection: Array<String>?,
        selection: String?, selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? {
        // Возвращает Cursor с данными на основе URI (реализация зависит от схемы данных)
        return database.query(/* ... */)
    }

    // onCreate, insert, update, delete...
}
```

**Ключевые особенности:**
- Основные компоненты (`Activity`, `Service`, `BroadcastReceiver`, `ContentProvider`) обычно объявляются в `AndroidManifest.xml`;
  некоторые `BroadcastReceiver` могут регистрироваться динамически в коде без манифеста
- Каждый компонент имеет свой lifecycle
- Компоненты запускаются/создаются системой в ответ на intents, URI-запросы или другие события и могут быть активированы независимо друг от друга

## Answer (EN)

**Four main Android components:**

**1. `Activity`** - user interface screen
- Represents a single screen with UI
- Entry point for user interaction
- Example: login screen, profile screen

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

**2. `Service`** - background operations
- Performs long-running operations without UI
- Runs in background
- Example: music playback, data synchronization

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // START_STICKY tells the system to try to recreate the service after it is killed,
        // but the timing and presence of the original Intent are not guaranteed
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**3. `BroadcastReceiver`** - system event handler
- Listens to system-wide or app broadcasts
- Responds to system state changes
- Example: network changes, low battery

```kotlin
class NetworkReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val isConnected = checkNetworkStatus(context)
        // Handle network state change
    }
}
```

**4. `ContentProvider`** - data management and sharing
- Centralized data storage for application
- `Provides` controlled access to data from other apps
- Example: Contacts, MediaStore

```kotlin
class MyContentProvider : ContentProvider() {
    override fun query(
        uri: Uri, projection: Array<String>?,
        selection: String?, selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? {
        // Returns a Cursor with data based on the URI (implementation depends on data schema)
        return database.query(/* ... */)
    }

    // onCreate, insert, update, delete...
}
```

**Key characteristics:**
- Core components (`Activity`, `Service`, `BroadcastReceiver`, `ContentProvider`) are typically declared in `AndroidManifest.xml`;
  some `BroadcastReceiver`s can be registered dynamically in code without manifest entries
- Each component has its own lifecycle
- Components are created/launched by the system in response to intents, URI requests, or other events and can be activated independently of one another

---

## Дополнительные Вопросы (RU)

- Как организовать взаимодействие между различными компонентами Android?
- В чем разница между foreground- и background-сервисами?
- Когда лучше использовать `BroadcastReceiver`, а когда event bus?
- Как `ContentProvider` обрабатывает конкурентный доступ к данным?
- Что произойдет, если забыть объявить компонент в `AndroidManifest.xml`?

## Follow-ups

- How do you communicate between different Android components?
- What is the difference between foreground and background services?
- When should you use a `BroadcastReceiver` vs an event bus?
- How does `ContentProvider` handle concurrent data access?
- What happens if you forget to declare a component in `AndroidManifest.xml`?

## Ссылки (RU)

- [[moc-android]] - Обзор разработки под Android
- [Android Developer Guide - `Application` Fundamentals](https://developer.android.com/guide/components/fundamentals)

## References

- [[moc-android]] - Android development overview
- [Android Developer Guide - `Application` Fundamentals](https://developer.android.com/guide/components/fundamentals)

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-android-components]]
- [[c-activity]]
- [[c-content-provider]]

### Предпосылки
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Основы main-потока
- [[q-what-unifies-android-components--android--easy]] - Общая основа компонент

### Связанные
- [[q-how-does-activity-lifecycle-work--android--medium]] - Детали lifecycle `Activity`
- [[q-android-components-besides-activity--android--easy]] - Другие типы компонентов

### Продвинутое
- [[q-what-unites-the-main-components-of-an-android-application--android--medium]] - Архитектура компонентов
- [[q-hilt-components-scope--android--medium]] - Dependency injection и компоненты

## Related Questions

### Prerequisites / Concepts

- [[c-android-components]]
- [[c-activity]]
- [[c-content-provider]]

### Prerequisites
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Main thread fundamentals
- [[q-what-unifies-android-components--android--easy]] - `Component` foundation

### Related
- [[q-how-does-activity-lifecycle-work--android--medium]] - `Activity` lifecycle details
- [[q-android-components-besides-activity--android--easy]] - Other component types

### Advanced
- [[q-what-unites-the-main-components-of-an-android-application--android--medium]] - `Component` architecture
- [[q-hilt-components-scope--android--medium]] - Dependency injection with components