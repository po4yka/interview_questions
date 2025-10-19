---
id: 20251012-122773
title: Android Service Types / Типы Service в Android
aliases: [Android Service Types, Типы Service в Android]
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
updated: 2025-10-15
tags: [android/service, android/background-execution, service, background-execution, bound-service, foreground-service, started-service, difficulty/easy]
---
# Question (EN)
> What types of services are there in Android?

# Вопрос (RU)
> Какие виды сервисов есть в Android?

---

## Answer (EN)

**Android Service Types** provide background execution capabilities for long-running operations without user interface.

**Service Types Theory:**
Services run in the background and can continue executing even when the user switches to another app. They are essential for tasks that need to persist beyond the app's lifecycle.

**1. Started Service:**
Runs independently in the background without user interaction. Continues until explicitly stopped or system kills it.

```kotlin
class DataSyncService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Background work
        return START_STICKY
    }
}

startService(Intent(this, DataSyncService::class.java))
```

**2. Foreground Service:**
Shows persistent notification and has higher priority. System is less likely to kill it.

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification)
        return START_STICKY
    }
}
```

**3. Bound Service:**
Allows components to bind and communicate through interface. Lives only while bound to clients.

```kotlin
class MusicService : Service() {
    private val binder = MusicBinder()

    inner class MusicBinder : Binder() {
        fun getService(): MusicService = this@MusicService
    }

    override fun onBind(intent: Intent): IBinder = binder
}

bindService(Intent(this, MusicService::class.java), connection, BIND_AUTO_CREATE)
```

**Service Comparison:**

| Type | Notification | Lifecycle | Use Case |
|------|--------------|-----------|----------|
| Started | No | Independent | Data sync, file upload |
| Foreground | Yes | Independent | Music player, location tracking |
| Bound | No | Client-dependent | API calls, local communication |

**Service Characteristics:**
- **Started**: Background tasks without UI interaction
- **Foreground**: Visible operations requiring user awareness
- **Bound**: Client-server communication within app

---

## Ответ (RU)

**Типы Service в Android** обеспечивают фоновое выполнение длительных операций без пользовательского интерфейса.

**Теория типов сервисов:**
Сервисы работают в фоне и могут продолжать выполнение даже когда пользователь переключается на другое приложение. Они необходимы для задач, которые должны выполняться за пределами жизненного цикла приложения.

**1. Started Service:**
Работает независимо в фоне без взаимодействия с пользователем. Продолжает работу до явной остановки или завершения системой.

```kotlin
class DataSyncService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Фоновая работа
        return START_STICKY
    }
}

startService(Intent(this, DataSyncService::class.java))
```

**2. Foreground Service:**
Показывает постоянное уведомление и имеет высокий приоритет. Система реже завершает такие сервисы.

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification)
        return START_STICKY
    }
}
```

**3. Bound Service:**
Позволяет компонентам привязываться и взаимодействовать через интерфейс. Живет только пока к нему привязан хотя бы один клиент.

```kotlin
class MusicService : Service() {
    private val binder = MusicBinder()

    inner class MusicBinder : Binder() {
        fun getService(): MusicService = this@MusicService
    }

    override fun onBind(intent: Intent): IBinder = binder
}

bindService(Intent(this, MusicService::class.java), connection, BIND_AUTO_CREATE)
```

**Сравнение сервисов:**

| Тип | Уведомление | Жизненный цикл | Пример использования |
|------|--------------|----------------|---------------------|
| Started | Нет | Независимый | Синхронизация данных, загрузка файлов |
| Foreground | Да | Независимый | Музыкальный плеер, отслеживание местоположения |
| Bound | Нет | Зависит от клиента | API вызовы, локальная связь |

**Характеристики сервисов:**
- **Started**: Фоновые задачи без взаимодействия с UI
- **Foreground**: Видимые операции, требующие внимания пользователя
- **Bound**: Связь клиент-сервер внутри приложения

---

## Follow-ups

- How do you choose between Started and Foreground services?
- What are the limitations of background services on Android 8.0+?
- How do you handle service lifecycle in different Android versions?

## References

- https://developer.android.com/guide/components/services
- https://developer.android.com/guide/components/foreground-services

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components overview
- [[q-android-async-primitives--android--easy]] - Async primitives

### Related (Medium)
- [[q-android-architectural-patterns--android--medium]] - Architecture patterns
- [[q-android-performance-measurement-tools--android--medium]] - Performance tools
