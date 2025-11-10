---
id: android-272
title: Android Components Besides Activity / Компоненты Android кроме Activity
aliases: [Android Components Besides Activity, Компоненты Android кроме Activity]
topic: android
subtopics:
- broadcast-receiver
- content-provider
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
- c-android-components
- q-android-app-components--android--easy
created: 2025-10-15
updated: 2025-11-10
tags: [android/broadcast-receiver, android/content-provider, android/service, difficulty/easy]
sources: []

---

# Вопрос (RU)

> Какие компоненты Android существуют помимо `Activity`?

---

# Question (EN)

> What Android components exist besides `Activity`?

---

## Ответ (RU)

Android определяет четыре основных компонента приложения: `Activity`, `Service`, `BroadcastReceiver` и `ContentProvider`. Помимо `Activity` ключевыми компонентами являются:

### 1. `Service` (Сервис)
Выполняет длительные операции в фоне без пользовательского интерфейса.

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Работа в фоне независимо от UI
        playMusic(intent?.getStringExtra("trackId"))
        return START_STICKY // ✅ Перезапуск после завершения системой (когда это возможно)
    }
}
```

**Применение**: Воспроизведение музыки, загрузка файлов, синхронизация данных.

### 2. `BroadcastReceiver` (Приёмник событий)
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

### 3. `ContentProvider` (Поставщик контента)
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

### 4. `Fragment` (Фрагмент)
НЕ является одним из четырёх основных компонентов, но является важной модульной частью UI с собственным жизненным циклом, привязанной к `Activity`.

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
| `Service` | Фоновые операции | ❌ | Независим от `Activity` |
| `BroadcastReceiver` | Обработка событий | ❌ | Кратковременный, должен завершить работу быстро |
| `ContentProvider` | Обмен данными | ❌ | Создаётся по требованию процессом приложения |
| `Fragment` | UI-модули (не основной компонент) | ✅ | Привязан к `Activity` |

---

## Answer (EN)

Android defines four main application components: `Activity`, `Service`, `BroadcastReceiver`, and `ContentProvider`. Besides `Activity`, the key components are:

### 1. `Service`
Executes long-running operations in the background without a user interface.

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Background work independent of UI
        playMusic(intent?.getStringExtra("trackId"))
        return START_STICKY // ✅ Request restart if killed by the system when possible
    }
}
```

**Use cases**: Music playback, file downloads, data synchronization.

### 2. `BroadcastReceiver`
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

### 3. `ContentProvider`
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

### 4. `Fragment`
NOT one of the four main app components, but an important modular UI unit with its own lifecycle, attached to an `Activity`.

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
|-----------|---------|----|-----------|
| `Service` | Background operations | ❌ | Independent from `Activity` |
| `BroadcastReceiver` | Event handling | ❌ | `Short`-lived, must finish quickly |
| `ContentProvider` | Data sharing | ❌ | Created on demand within the app process |
| `Fragment` | UI modules (not a core app component) | ✅ | Tied to `Activity` |

---

## Дополнительные вопросы (RU)

- В чем разница между запущенным (`started`) `Service` и привязанным (`bound`) `Service`?
- Когда следует использовать WorkManager вместо `Service`?
- Как ограничения по времени выполнения и условия для `BroadcastReceiver` влияют на реализацию?
- Какие механизмы безопасности предоставляет `ContentProvider`?
- Почему фрагменты считаются спорным решением в современной Android-разработке?

## Follow-ups

- What's the difference between started `Service` and bound `Service`?
- When should you use WorkManager instead of `Service`?
- How does `BroadcastReceiver`'s time limit and execution constraints affect implementation?
- What security mechanisms does `ContentProvider` offer?
- Why are Fragments controversial in modern Android development?

## Ссылки (RU)

- https://developer.android.com/guide/components/fundamentals

## References

- https://developer.android.com/guide/components/fundamentals

## Связанные вопросы (RU)

### Предусловия
- [[q-android-app-components--android--easy]] - Обзор всех компонентов приложения

### Связанные
- [[q-android-service-types--android--easy]] - Запущенный vs привязанный `Service`
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Сравнение жизненного цикла `Fragment`

### Продвинутые
- Современные паттерны фоновой работы

## Related Questions

### Prerequisites
- [[q-android-app-components--android--easy]] - Overview of all app components

### Related
- [[q-android-service-types--android--easy]] - Started vs Bound `Service`
- [[q-fragment-vs-activity-lifecycle--android--medium]] - `Fragment` lifecycle comparison

### Advanced
- Modern background work patterns
