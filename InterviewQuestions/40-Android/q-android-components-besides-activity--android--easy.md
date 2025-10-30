---
id: 20251015-132630
title: Android Components Besides Activity / Компоненты Android кроме Activity
aliases: ["Android Components Besides Activity", "Компоненты Android кроме Activity"]
topic: android
subtopics: [service, broadcast-receiver, content-provider]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-app-components--android--easy, q-fragment-vs-activity-lifecycle--android--medium, q-service-types-android--android--easy, c-service, c-lifecycle]
created: 2025-10-15
updated: 2025-10-30
tags: [android/service, android/broadcast-receiver, android/content-provider, difficulty/easy]
sources: []
date created: Thursday, October 30th 2025, 11:26:39 am
date modified: Thursday, October 30th 2025, 12:42:46 pm
---

# Вопрос (RU)

Какие компоненты Android существуют помимо Activity?

---

# Question (EN)

What Android components exist besides Activity?

---

## Ответ (RU)

Android определяет четыре основных компонента приложения, из которых три работают без UI:

### 1. Service (Сервис)
Выполняет длительные операции в фоне без пользовательского интерфейса.

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Работа в фоне независимо от UI
        playMusic(intent?.getStringExtra("trackId"))
        return START_STICKY // ✅ Перезапуск после завершения системой
    }
}
```

**Применение**: Воспроизведение музыки, загрузка файлов, синхронизация данных.

### 2. BroadcastReceiver (Приёмник событий)
Реагирует на системные и кастомные broadcast-сообщения.

```kotlin
class NetworkReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // ✅ Обработка системных событий
        val isOnline = isNetworkAvailable(context)
    }
}
```

**Сценарии**: Изменение подключения, уровень батареи, загрузка завершена, кастомные события.

### 3. ContentProvider (Поставщик контента)
Управляет доступом к структурированным данным между приложениями.

```kotlin
class ContactsProvider : ContentProvider() {
    override fun query(uri: Uri, projection: Array<String>?, ...): Cursor? {
        // ✅ Безопасный доступ к данным через URI
        return database.query(parseTable(uri), projection, ...)
    }
}
```

**Назначение**: Межприложенский доступ к контактам, медиафайлам, календарю.

### 4. Fragment (Фрагмент)
Модульная часть UI с собственным жизненным циклом, привязанная к Activity.

```kotlin
class DetailsFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // ✅ Переиспользуемый UI-компонент
        return inflater.inflate(R.layout.fragment_details, container, false)
    }
}
```

**Преимущества**: Переиспользуемость, master-detail layouts, поддержка back stack.

| Компонент | Назначение | UI | Жизненный цикл |
|-----------|------------|----|----------------|
| Service | Фоновые операции | ❌ | Независимый от Activity |
| BroadcastReceiver | Обработка событий | ❌ | Кратковременный (10 сек) |
| ContentProvider | Обмен данными | ❌ | Singleton, по требованию |
| Fragment | UI-модули | ✅ | Привязан к Activity |

---

## Answer (EN)

Android defines four main application components, three of which operate without UI:

### 1. Service
Executes long-running operations in the background without a user interface.

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Background work independent of UI
        playMusic(intent?.getStringExtra("trackId"))
        return START_STICKY // ✅ Restart if killed by system
    }
}
```

**Use cases**: Music playback, file downloads, data synchronization.

### 2. BroadcastReceiver
Responds to system-wide and custom broadcast announcements.

```kotlin
class NetworkReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // ✅ Handle system events
        val isOnline = isNetworkAvailable(context)
    }
}
```

**Use cases**: Network connectivity changes, battery level, download completed, custom events.

### 3. ContentProvider
Manages access to structured data shared between applications.

```kotlin
class ContactsProvider : ContentProvider() {
    override fun query(uri: Uri, projection: Array<String>?, ...): Cursor? {
        // ✅ Secure data access via URI
        return database.query(parseTable(uri), projection, ...)
    }
}
```

**Purpose**: Inter-app access to contacts, media files, calendar.

### 4. Fragment
Modular UI portion with its own lifecycle, attached to an Activity.

```kotlin
class DetailsFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // ✅ Reusable UI component
        return inflater.inflate(R.layout.fragment_details, container, false)
    }
}
```

**Benefits**: Reusability, master-detail layouts, back stack support.

| Component | Purpose | UI | Lifecycle |
|-----------|---------|-----|-----------|
| Service | Background operations | ❌ | Independent from Activity |
| BroadcastReceiver | Event handling | ❌ | Short-lived (10 sec) |
| ContentProvider | Data sharing | ❌ | Singleton, on-demand |
| Fragment | UI modules | ✅ | Tied to Activity |

---

## Follow-ups

- What's the difference between started Service and bound Service?
- When should you use WorkManager instead of Service?
- How does BroadcastReceiver's 10-second limit affect implementation?
- What security mechanisms does ContentProvider offer?
- Why are Fragments controversial in modern Android development?

## References

- [[c-service]] - Service component details
- [[c-lifecycle]] - Android lifecycle fundamentals
- https://developer.android.com/guide/components/fundamentals

## Related Questions

### Prerequisites
- [[q-android-app-components--android--easy]] - Overview of all app components

### Related
- [[q-service-types-android--android--easy]] - Started vs Bound Service
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Fragment lifecycle comparison

### Advanced
- [[q-workmanager-vs-service--android--medium]] - Modern background work patterns
