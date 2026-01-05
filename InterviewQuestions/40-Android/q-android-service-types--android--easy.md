---
id: android-285
title: Android Service Types / Типы Service в Android
aliases: [Android Service Types, Типы Service в Android]
topic: android
subtopics: [background-execution, service]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-components, q-android-app-components--android--easy, q-android-architectural-patterns--android--medium, q-android-async-primitives--android--easy, q-android-services-purpose--android--easy, q-foreground-service-types--android--medium, q-service-types-android--android--easy]
created: 2024-10-15
updated: 2025-11-10
tags: [android/background-execution, android/service, difficulty/easy]

---
# Вопрос (RU)
> Какие типы `Service` существуют в Android?

# Question (EN)
> What are the types of `Service` in Android?

---

## Ответ (RU)

С точки зрения компонентной модели Android есть два основных типа `Service`:

- Started `Service` (запущенный)
- Bound `Service` (привязанный)

Сервис также может быть одновременно и started, и bound. Foreground `Service` — это особый режим работы started-сервиса, а не отдельный компонентный тип, но в интервью его часто выделяют отдельно.

**1. Started `Service`**
Запускается через `startService()` (ограничен на Android 8.0+ для фонового старта) или `startForegroundService()` (для будущего foreground режима) и работает независимо, пока не будет остановлен `stopSelf()`/`stopService()` или уничтожен системой при нехватке ресурсов.

**2. Foreground `Service` (режим started-сервиса)**
Выполняет видимую пользователю работу с обязательной нотификацией. Имеет более высокий приоритет, реже убивается системой, но не имеет абсолютной защиты от завершения. На Android 9+ требует явного разрешения (`FOREGROUND_SERVICE` и специализированные permissions для некоторых типов) и указания типа foreground service.

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // На Android 8.0+ для долгой фоновой работы сервис обычно
        // запускают через startForegroundService(), затем вызывают startForeground().
        startForeground(NOTIFICATION_ID, createNotification()) // ✅ Обязательно для foreground
        return START_STICKY // ✅ Попытка перезапуска после убийства системой
    }
}
```

**3. Bound `Service`**
Предоставляет клиент-серверный интерфейс. Живет только пока есть привязанные клиенты (если не комбинирован со started-состоянием).

```kotlin
class LocalService : Service() {
    inner class LocalBinder : Binder() {
        fun getService() = this@LocalService // ✅ Прямой доступ к сервису
    }

    override fun onBind(intent: Intent): IBinder = LocalBinder()
}
```

**Ключевые отличия:**

| Тип            | Notification      | Жизненный цикл                       | Когда использовать                           |
|----------------|-------------------|--------------------------------------|----------------------------------------------|
| Started        | Необязательна     | Независим (может быть убит системой) | Одноразовая/ограниченная по времени работа   |
| Foreground     | Обязательна       | Независим, повышенный приоритет      | Музыка, навигация, активные загрузки и т.п.  |
| Bound          | Необязательна     | Зависит от привязанных клиентов      | IPC/общий сервис для компонентов             |

**Ограничения:**
- Android 8.0+ резко ограничивает длительную фоновую работу; для долгих операций обычно используют Foreground `Service`, WorkManager или другие планировщики в зависимости от сценария.
- WorkManager предпочтителен для отложенной, гарантируемой, но не немедленной работы.
- Started `Service` может быть убит системой; поведение при перезапуске определяется значением, возвращаемым `onStartCommand()`.

См. также: [[c-android-components]]

## Answer (EN)

From the Android component model perspective, there are two primary `Service` types:

- Started `Service`
- Bound `Service`

A service can be both started and bound at the same time. A Foreground `Service` is a special execution mode of a started service, not a separate component type, though it is often discussed separately in interviews.

**1. Started `Service`**
Launched via `startService()` (background starts are restricted on Android 8.0+) or `startForegroundService()` (for future foreground mode). It runs independently until `stopSelf()`/`stopService()` is called or the system kills it under resource pressure.

**2. Foreground `Service` (mode of a started service)**
Performs user-visible work with a mandatory notification. It has higher priority and is less likely to be killed, but it is not completely immune to termination. On Android 9+ it requires the `FOREGROUND_SERVICE` permission (and specialized permissions for some types) and a declared foreground service type.

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // On Android 8.0+, long-running work typically uses startForegroundService()
        // to start, then calls startForeground() promptly.
        startForeground(NOTIFICATION_ID, createNotification()) // ✅ Required for foreground
        return START_STICKY // ✅ Attempts restart after system kill
    }
}
```

**3. Bound `Service`**
Provides a client-server interface. Lives only while clients are bound (unless also started).

```kotlin
class LocalService : Service() {
    inner class LocalBinder : Binder() {
        fun getService() = this@LocalService // ✅ Direct access to service
    }

    override fun onBind(intent: Intent): IBinder = LocalBinder()
}
```

**Key Differences:**

| Type       | Notification  | Lifecycle                          | Use Case                                      |
|------------|---------------|------------------------------------|-----------------------------------------------|
| Started    | Optional      | Independent (may be killed)        | One-shot / time-limited background work       |
| Foreground | Required      | Independent, higher priority       | Music, navigation, active downloads, etc.     |
| Bound      | Optional      | Client-dependent                   | IPC/shared service for components             |

**Constraints:**
- Android 8.0+ heavily restricts long-running background work; for long tasks you typically use a Foreground `Service`, WorkManager, or scheduling APIs depending on the use case.
- WorkManager is preferred for deferrable, guaranteed, but not strictly immediate work.
- A Started `Service` can be killed by the system; restart behavior depends on the `onStartCommand()` return value.

See also: [[c-android-components]]

---

## Дополнительные Вопросы (RU)

- Какие существуют типы Foreground `Service` и когда каждый из них обязателен?
- Чем отличается `START_STICKY` от `START_NOT_STICKY` и `START_REDELIVER_INTENT`?
- В каких случаях следует использовать WorkManager вместо `Service`?
- Как реализовать гибридный `Service`, который одновременно started и bound?
- Что происходит с Bound `Service`, когда последний клиент отвязывается?

## Follow-ups

- What are the Foreground `Service` types and when are they required?
- How does `START_STICKY` differ from `START_NOT_STICKY` and `START_REDELIVER_INTENT`?
- When should you use WorkManager instead of a `Service`?
- How do you implement a hybrid `Service` (both started and bound)?
- What happens to a Bound `Service` when the last client unbinds?

## Ссылки (RU)

- https://developer.android.com/guide/components/services
- https://developer.android.com/guide/components/foreground-services

## References

- https://developer.android.com/guide/components/services
- https://developer.android.com/guide/components/foreground-services

## Связанные Вопросы (RU)

### Базовые Знания
- [[q-android-app-components--android--easy]] - Основные Android-компоненты

### Связанные
- [[q-android-async-primitives--android--easy]] - Варианты асинхронного выполнения
- Типы и разрешения Foreground `Service`

### Продвинутые
- [[q-android-architectural-patterns--android--medium]] - MVVM и интеграция с сервисами
- Жизненный цикл `Service` в мультипроцессной архитектуре

## Related Questions

### Prerequisites
- [[q-android-app-components--android--easy]] - Core Android components

### Related
- [[q-android-async-primitives--android--easy]] - Async execution options
- Foreground `Service` types and permissions

### Advanced
- [[q-android-architectural-patterns--android--medium]] - MVVM and service integration
- `Service` lifecycle in multi-process architectures
