---
id: 20251012-122773
title: Android Service Types / Типы Service в Android
aliases: ["Android Service Types", "Типы Service в Android"]
topic: android
subtopics: [background-execution, service]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-app-components--android--easy, q-android-architectural-patterns--android--medium, q-android-async-primitives--android--easy]
created: 2025-10-15
updated: 2025-10-27
tags: [android/background-execution, android/service, difficulty/easy]
sources: []
---
# Вопрос (RU)
> Какие типы Service существуют в Android?

# Question (EN)
> What are the types of Service in Android?

---

## Ответ (RU)

Android предоставляет три типа Service для выполнения фоновых операций:

**1. Started Service (Запущенный сервис)**
Выполняется независимо в фоне. Запускается через `startService()` и работает пока не будет явно остановлен или уничтожен системой.

**2. Foreground Service (Приоритетный сервис)**
Выполняет заметные для пользователя операции с постоянной нотификацией. Имеет высокий приоритет и защищен от уничтожения системой. Требует permission и notification.

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification) // ✅ Required for foreground
        // Perform work
        return START_STICKY
    }
}
```

**3. Bound Service (Связанный сервис)**
Предоставляет клиент-серверный интерфейс для взаимодействия между компонентами. Живет только пока есть привязанные клиенты. Используется для IPC внутри приложения.

```kotlin
class LocalService : Service() {
    private val binder = LocalBinder()

    inner class LocalBinder : Binder() {
        fun getService(): LocalService = this@LocalService
    }

    override fun onBind(intent: Intent): IBinder = binder
}
```

**Сравнение типов:**

| Тип | Notification | Жизненный цикл | Когда использовать |
|-----|-------------|----------------|-------------------|
| Started | Нет | Независимый | Синхронизация данных, загрузка файлов |
| Foreground | Да (обязательно) | Независимый | Музыка, навигация, отслеживание |
| Bound | Нет | Зависит от клиентов | Локальное IPC, API для Activity |

**Важные ограничения (Android 8.0+):**
- Background execution limits требуют использования Foreground Service для long-running tasks
- WorkManager предпочтителен для deferrable background work
- Started Services могут быть killed системой при нехватке памяти

## Answer (EN)

Android provides three types of Services for background operations:

**1. Started Service**
Runs independently in the background. Launched via `startService()` and continues until explicitly stopped or killed by the system.

**2. Foreground Service**
Performs user-visible operations with a persistent notification. Has high priority and is protected from system termination. Requires permission and notification.

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification) // ✅ Required for foreground
        // Perform work
        return START_STICKY
    }
}
```

**3. Bound Service**
Provides client-server interface for component interaction. Lives only while clients are bound. Used for IPC within the app.

```kotlin
class LocalService : Service() {
    private val binder = LocalBinder()

    inner class LocalBinder : Binder() {
        fun getService(): LocalService = this@LocalService
    }

    override fun onBind(intent: Intent): IBinder = binder
}
```

**Type Comparison:**

| Type | Notification | Lifecycle | Use Case |
|------|-------------|-----------|----------|
| Started | No | Independent | Data sync, file upload |
| Foreground | Yes (required) | Independent | Music, navigation, tracking |
| Bound | No | Client-dependent | Local IPC, API for Activity |

**Important Constraints (Android 8.0+):**
- Background execution limits require Foreground Service for long-running tasks
- WorkManager is preferred for deferrable background work
- Started Services can be killed by system under memory pressure

---

## Follow-ups

- When should you use WorkManager instead of a Service?
- What are the Foreground Service types and required permissions?
- How do background execution limits affect Service behavior?

## References

- https://developer.android.com/guide/components/services
- https://developer.android.com/guide/components/foreground-services
- [[c-service]]
- [[c-lifecycle]]

## Related Questions

### Prerequisites
- [[q-android-app-components--android--easy]] - Android app components overview

### Related
- [[q-android-async-primitives--android--easy]] - Async execution primitives
- [[q-android-architectural-patterns--android--medium]] - Architecture patterns

### Advanced
- Background execution optimization strategies
- Service lifecycle management in multi-module apps