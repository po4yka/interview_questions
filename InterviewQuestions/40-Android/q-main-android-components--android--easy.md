---
id: android-358
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
- c-service
- c-activity
- c-content-provider
- q-how-does-activity-lifecycle-work--android--medium
- q-jit-vs-aot-compilation--android--medium
sources: []
created: 2025-10-15
updated: 2025-10-28
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

**1. Activity** - экран пользовательского интерфейса
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

**2. Service** - фоновые операции
- Выполняет длительные операции без пользовательского интерфейса
- Работает в фоновом режиме
- Пример: воспроизведение музыки, синхронизация данных

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ START_STICKY перезапускает сервис после kill
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**3. BroadcastReceiver** - обработчик системных событий
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

**4. ContentProvider** - управление и обмен данными
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
        // ✅ Возвращает данные по URI
        return database.query(...)
    }

    // onCreate, insert, update, delete...
}
```

**Ключевые особенности:**
- Все компоненты объявляются в **AndroidManifest.xml**
- Каждый компонент имеет свой lifecycle
- Компоненты могут быть запущены системой независимо друг от друга

## Answer (EN)

**Four main Android components:**

**1. Activity** - user interface screen
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

**2. Service** - background operations
- Performs long-running operations without UI
- Runs in background
- Example: music playback, data synchronization

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ START_STICKY restarts service after kill
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**3. BroadcastReceiver** - system event handler
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

**4. ContentProvider** - data management and sharing
- Centralized data storage for application
- Provides controlled access to data from other apps
- Example: Contacts, MediaStore

```kotlin
class MyContentProvider : ContentProvider() {
    override fun query(
        uri: Uri, projection: Array<String>?,
        selection: String?, selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? {
        // ✅ Returns data based on URI
        return database.query(...)
    }

    // onCreate, insert, update, delete...
}
```

**Key characteristics:**
- All components must be declared in **AndroidManifest.xml**
- Each component has its own lifecycle
- Components can be started by the system independently

---

## Follow-ups

- How do you communicate between different Android components?
- What is the difference between foreground and background services?
- When should you use a BroadcastReceiver vs an event bus?
- How does ContentProvider handle concurrent data access?
- What happens if you forget to declare a component in AndroidManifest.xml?

## References

- [[moc-android]] - Android development overview
- [Android Developer Guide - Application Fundamentals](https://developer.android.com/guide/components/fundamentals)

## Related Questions

### Prerequisites / Concepts

- [[c-service]]
- [[c-activity]]
- [[c-content-provider]]


### Prerequisites
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Main thread fundamentals
- [[q-what-unifies-android-components--android--easy]] - Component foundation

### Related
- [[q-how-does-activity-lifecycle-work--android--medium]] - Activity lifecycle details
- [[q-android-components-besides-activity--android--easy]] - Other component types

### Advanced
- [[q-what-unites-the-main-components-of-an-android-application--android--medium]] - Component architecture
- [[q-hilt-components-scope--android--medium]] - Dependency injection with components
