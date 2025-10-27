---
id: 20251012-122759
title: Android App Components / Компоненты Android приложения
aliases: [Android App Components, Компоненты Android приложения]
topic: android
subtopics:
  - activity
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
  - q-activity-lifecycle-methods--android--medium
  - q-how-to-register-broadcastreceiver-to-receive-messages--android--medium
  - q-service-types-android--android--easy
  - c-service
  - c-broadcast-receiver
  - c-content-provider
created: 2025-10-15
updated: 2025-10-27
sources: []
tags: [android/activity, android/service, difficulty/easy]
---
# Вопрос (RU)
> Назовите основные компоненты Android приложения и их назначение.

---

# Question (EN)
> What are the four fundamental components of an Android application?

---

## Ответ (RU)

В Android существует четыре основных типа компонентов приложения: Activity, [[c-service|Service]], [[c-broadcast-receiver|Broadcast Receiver]] и [[c-content-provider|Content Provider]].

**1. Activity (Активность):**
- Представляет один экран UI
- Обрабатывает взаимодействия пользователя
- Управляет состояниями жизненного цикла

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)  // ✅ Устанавливает UI
    }
}
```

**2. Service (Служба):**
- Выполняет длительные операции в фоне
- Работает без UI
- Типы: Started, Bound, Foreground

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Воспроизведение музыки в фоне
        return START_STICKY  // ✅ Автоматический перезапуск
    }
}
```

**3. Broadcast Receiver (Получатель широковещательных сообщений):**
- Реагирует на системные события
- Регистрируется статически (manifest) или динамически (код)

```kotlin
class BatteryReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        // ✅ Обработка события низкого заряда батареи
    }
}
```

**4. Content Provider (Поставщик содержимого):**
- Управляет общими данными приложения
- Обеспечивает межпроцессный доступ к данным

```kotlin
class MyContentProvider : ContentProvider() {
    override fun query(uri: Uri, ...): Cursor? {
        // ✅ Предоставление данных другим приложениям
        return cursor
    }
}
```

**Связь между компонентами:**
- **Intent** — передача сообщений между компонентами
- **Intent Filter** — объявление возможностей компонента
- **AndroidManifest.xml** — регистрация всех компонентов

---

## Answer (EN)

Android has four fundamental application components: Activity, [[c-service|Service]], [[c-broadcast-receiver|Broadcast Receiver]], and [[c-content-provider|Content Provider]].

**1. Activity:**
- Represents a single UI screen
- Handles user interactions
- Manages lifecycle states

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)  // ✅ Sets the UI
    }
}
```

**2. Service:**
- Performs long-running background operations
- Runs without UI
- Types: Started, Bound, Foreground

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Background music playback
        return START_STICKY  // ✅ Auto-restart after termination
    }
}
```

**3. Broadcast Receiver:**
- Responds to system-wide events
- Registered statically (manifest) or dynamically (code)

```kotlin
class BatteryReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        // ✅ Handle battery low event
    }
}
```

**4. Content Provider:**
- Manages shared application data
- Enables inter-process data access

```kotlin
class MyContentProvider : ContentProvider() {
    override fun query(uri: Uri, ...): Cursor? {
        // ✅ Provide data to other apps
        return cursor
    }
}
```

**Component Communication:**
- **Intent** — messaging between components
- **Intent Filter** — declares component capabilities
- **AndroidManifest.xml** — registers all components

---

## Follow-ups

- What are the differences between started, bound, and foreground services?
- When should you use static vs dynamic Broadcast Receiver registration?
- How does the AndroidManifest.xml register components?
- What is the lifecycle of each component type?

## References

- [[c-service]] - Service component details
- [[c-broadcast-receiver]] - Broadcast receiver patterns
- [[c-content-provider]] - Content provider implementation
- [Android Components Guide](https://developer.android.com/guide/components/fundamentals)

## Related Questions

### Prerequisites
- [[q-what-is-intent--android--easy]] - Intent system basics
- [[q-gradle-basics--android--easy]] - Build system

### Related
- [[q-activity-lifecycle-methods--android--medium]] - Activity lifecycle
- [[q-service-types-android--android--easy]] - Service types
- [[q-how-to-register-broadcastreceiver-to-receive-messages--android--medium]] - BroadcastReceiver registration

### Advanced
- Component lifecycle patterns and best practices
- Inter-process communication mechanisms