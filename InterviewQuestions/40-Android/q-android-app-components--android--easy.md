---
id: 20251012-122759
title: "Android App Components / Компоненты Android приложения"
aliases: [Android App Components, Компоненты Android приложения]
topic: android
subtopics: [app-components, architecture]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-activity-lifecycle-methods--android--medium, q-service-types--android--medium, q-broadcast-receivers--android--medium]
created: 2025-10-15
updated: 2025-10-15
tags: [android/app-components, android/architecture, app-components, architecture, difficulty/easy]
---

# Question (EN)
> What are the main components of an Android application?

# Вопрос (RU)
> Какие основные компоненты Android-приложения?

---

## Answer (EN)

Android applications have four fundamental components:

**1. Activity:**
- UI component representing a single screen
- Handles user interactions
- Manages lifecycle states

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

**2. Service:**
- Background component for long-running operations
- No UI, runs independently
- Types: Started, Bound, Foreground

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Background music playback
        return START_STICKY
    }
}
```

**3. Broadcast Receiver:**
- Responds to system-wide broadcast announcements
- Receives and reacts to events
- Can be registered statically or dynamically

```kotlin
class BatteryReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        // Handle battery low event
    }
}
```

**4. Content Provider:**
- Manages shared app data
- Provides data access interface
- Enables data sharing between apps

```kotlin
class MyContentProvider : ContentProvider() {
    override fun query(uri: Uri, projection: Array<String>?, selection: String?, selectionArgs: Array<String>?, sortOrder: String?): Cursor? {
        // Provide data to other apps
        return null
    }
}
```

**Component Communication:**
- **Intents**: Used to communicate between components
- **Intent Filters**: Declare component capabilities
- **Manifest**: Registers all components

## Ответ (RU)

Android-приложения имеют четыре основных компонента:

**1. Activity:**
- UI компонент, представляющий один экран
- Обрабатывает взаимодействие с пользователем
- Управляет состояниями жизненного цикла

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

**2. Service:**
- Фоновый компонент для длительных операций
- Без UI, работает независимо
- Типы: Started, Bound, Foreground

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Фоновое воспроизведение музыки
        return START_STICKY
    }
}
```

**3. Broadcast Receiver:**
- Реагирует на системные широковещательные сообщения
- Получает и обрабатывает события
- Может быть зарегистрирован статически или динамически

```kotlin
class BatteryReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        // Обработка события низкого заряда батареи
    }
}
```

**4. Content Provider:**
- Управляет общими данными приложения
- Предоставляет интерфейс доступа к данным
- Обеспечивает обмен данными между приложениями

```kotlin
class MyContentProvider : ContentProvider() {
    override fun query(uri: Uri, projection: Array<String>?, selection: String?, selectionArgs: Array<String>?, sortOrder: String?): Cursor? {
        // Предоставление данных другим приложениям
        return null
    }
}
```

**Связь между компонентами:**
- **Intents**: Используются для связи между компонентами
- **Intent Filters**: Объявляют возможности компонентов
- **Manifest**: Регистрирует все компоненты

---

## Follow-ups

- How do Intents enable communication between components?
- What are the differences between started and bound services?
- When should you use static vs dynamic Broadcast Receiver registration?
- How do Content Providers enable data sharing between apps?
- What role does the AndroidManifest.xml play in component registration?

## References

- [Android App Components](https://developer.android.com/guide/components/fundamentals)
- [Activities](https://developer.android.com/guide/components/activities/intro-activities)
- [Services](https://developer.android.com/guide/components/services)
- [Broadcast Receivers](https://developer.android.com/guide/components/broadcasts)
- [Content Providers](https://developer.android.com/guide/topics/providers/content-providers)

## Related Questions

### Prerequisites (Easier)
- [[q-android-basics--android--easy]] - Android fundamentals
- [[q-manifest-file--android--easy]] - Manifest configuration

### Related (Medium)
- [[q-activity-lifecycle-methods--android--medium]] - Activity lifecycle
- [[q-service-types--android--medium]] - Service types
- [[q-broadcast-receivers--android--medium]] - Broadcast receivers
- [[q-content-providers--android--medium]] - Content providers

### Advanced (Harder)
- [[q-component-communication--android--hard]] - Advanced communication
- [[q-custom-content-providers--android--hard]] - Custom providers
