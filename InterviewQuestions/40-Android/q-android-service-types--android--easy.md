---
id: 20251012-122773
title: Android Service Types / Типы Service в Android
aliases: ["Android Service Types", "Типы Service в Android"]
topic: android
subtopics: [service, background-execution]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-app-components--android--easy, q-android-async-primitives--android--easy, q-android-architectural-patterns--android--medium]
created: 2025-10-15
updated: 2025-10-30
tags: [android/service, android/background-execution, difficulty/easy]
sources: []
---
# Вопрос (RU)
> Какие типы Service существуют в Android?

# Question (EN)
> What are the types of Service in Android?

---

## Ответ (RU)

Android предоставляет три типа Service:

**1. Started Service**
Запускается через `startService()` и работает независимо до явной остановки или уничтожения системой при нехватке памяти.

**2. Foreground Service**
Выполняет видимую пользователю работу с обязательной нотификацией. Защищен от уничтожения системой. Требует permission и указание типа foreground service.

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIFICATION_ID, createNotification()) // ✅ Обязательно
        return START_STICKY // ✅ Перезапуск при убийстве
    }
}
```

**3. Bound Service**
Предоставляет клиент-серверный интерфейс. Живет только пока есть привязанные клиенты.

```kotlin
class LocalService : Service() {
    inner class LocalBinder : Binder() {
        fun getService() = this@LocalService // ✅ Прямой доступ
    }

    override fun onBind(intent: Intent): IBinder = LocalBinder()
}
```

**Ключевые отличия:**

| Тип | Notification | Жизненный цикл | Когда использовать |
|-----|-------------|----------------|-------------------|
| Started | — | Независимый | Одноразовая фоновая работа |
| Foreground | Обязательна | Независимый | Музыка, навигация, загрузка |
| Bound | — | Зависит от клиентов | IPC между компонентами |

**Ограничения:**
- Android 8.0+ требует Foreground Service для длительных задач
- WorkManager предпочтителен для отложенной работы
- Started Service может быть убит системой

## Answer (EN)

Android provides three Service types:

**1. Started Service**
Launched via `startService()` and runs independently until explicitly stopped or killed by system under memory pressure.

**2. Foreground Service**
Performs user-visible work with mandatory notification. Protected from system termination. Requires permission and foreground service type declaration.

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIFICATION_ID, createNotification()) // ✅ Required
        return START_STICKY // ✅ Restart after killed
    }
}
```

**3. Bound Service**
Provides client-server interface. Lives only while clients are bound.

```kotlin
class LocalService : Service() {
    inner class LocalBinder : Binder() {
        fun getService() = this@LocalService // ✅ Direct access
    }

    override fun onBind(intent: Intent): IBinder = LocalBinder()
}
```

**Key Differences:**

| Type | Notification | Lifecycle | Use Case |
|------|-------------|-----------|----------|
| Started | — | Independent | One-shot background work |
| Foreground | Required | Independent | Music, navigation, download |
| Bound | — | Client-dependent | IPC between components |

**Constraints:**
- Android 8.0+ requires Foreground Service for long-running tasks
- WorkManager is preferred for deferrable work
- Started Service can be killed by system

---

## Follow-ups

- What are the Foreground Service types and when are they required?
- How does `START_STICKY` differ from `START_NOT_STICKY` and `START_REDELIVER_INTENT`?
- When should you use WorkManager instead of a Service?
- How do you implement a hybrid Service (both started and bound)?
- What happens to a Bound Service when the last client unbinds?

## References

- [[c-service]] - Service lifecycle and implementation
- [[c-lifecycle]] - Android component lifecycle
- https://developer.android.com/guide/components/services
- https://developer.android.com/guide/components/foreground-services

## Related Questions

### Prerequisites
- [[q-android-app-components--android--easy]] - Core Android components

### Related
- [[q-android-async-primitives--android--easy]] - Async execution options
- Foreground Service types and permissions

### Advanced
- [[q-android-architectural-patterns--android--medium]] - MVVM and service integration
- Service lifecycle in multi-process architectures
