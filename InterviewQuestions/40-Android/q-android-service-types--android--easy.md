---
id: 20251012-122773
title: "Android Service Types / Типы Service в Android"
topic: android
difficulty: easy
status: draft
moc: moc-android
related: [q-why-multithreading-tools--android--easy, q-workmanager-return-result--android--medium, q-multi-module-best-practices--android--hard]
created: 2025-10-15
tags: [android/background-execution, android/service, background-execution, bound-service, foreground-service, service, started-service, difficulty/easy]
---
# Какие виды сервисов есть в Android?

# Question (EN)
> What types of services are there in Android?

# Вопрос (RU)
> Какие виды сервисов есть в Android?

---

## Answer (EN)

**Three main types of services:**

**1. Started Service (Background Service)**

Performs operation and doesn't return result.

```kotlin
class DataSyncService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Do work
        return START_STICKY
    }
}

// Start service
startService(Intent(this, DataSyncService::class.java))
```

**2. Foreground Service**

Shows notification, higher priority, harder to kill.

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification)
        return START_STICKY
    }
}
```

**3. Bound Service**

Allows components to bind and interact.

```kotlin
class MusicService : Service() {
    private val binder = MusicBinder()

    inner class MusicBinder : Binder() {
        fun getService(): MusicService = this@MusicService
    }

    override fun onBind(intent: Intent): IBinder = binder
}

// Bind to service
bindService(Intent(this, MusicService::class.java), connection, BIND_AUTO_CREATE)
```

**Comparison:**

| Type | Notification | User Interaction | Use Case |
|------|--------------|------------------|----------|
| Started | No | No | Data sync |
| Foreground | Yes | Visible | Music player |
| Bound | No | Client-server | API calls |

**Summary:**

- **Started**: Background tasks without UI
- **Foreground**: Ongoing notifications (music, location)
- **Bound**: Client-server interaction within app

---

## Ответ (RU)

В Android есть три основных типа сервисов:

**1. Started Service (Background Service)**

Выполняет операцию и не возвращает результат. Запускается через `startService()` и продолжает работать в фоне даже после завершения компонента, который его запустил.

```kotlin
class DataSyncService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Выполнить работу
        return START_STICKY // Перезапустить если убит системой
    }
}

// Запуск сервиса
startService(Intent(this, DataSyncService::class.java))
```

**2. Foreground Service**

Отображает уведомление, имеет высокий приоритет и сложнее убивается системой. Используется для операций, о которых пользователь должен знать (музыка, навигация, загрузка файлов).

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification)
        return START_STICKY
    }
}
```

**3. Bound Service**

Позволяет компонентам привязываться и взаимодействовать через интерфейс. Живет только пока к нему привязан хотя бы один клиент.

```kotlin
class MusicService : Service() {
    private val binder = MusicBinder()

    inner class MusicBinder : Binder() {
        fun getService(): MusicService = this@MusicService
    }

    override fun onBind(intent: Intent): IBinder = binder
}

// Привязка к сервису
bindService(Intent(this, MusicService::class.java), connection, BIND_AUTO_CREATE)
```

**Сравнение:**

| Тип | Уведомление | Взаимодействие | Пример использования |
|------|--------------|------------------|----------|
| Started | Нет | Нет | Синхронизация данных |
| Foreground | Да | Видимое | Музыкальный плеер |
| Bound | Нет | Клиент-сервер | API вызовы |

**Резюме:**

- **Started**: Фоновые задачи без UI
- **Foreground**: Постоянные уведомления (музыка, геолокация)
- **Bound**: Взаимодействие клиент-сервер внутри приложения


---

## Related Questions

### Advanced (Harder)
- [[q-service-component--android--medium]] - Service
- [[q-foreground-service-types--background--medium]] - Service
- [[q-when-can-the-system-restart-a-service--android--medium]] - Service
