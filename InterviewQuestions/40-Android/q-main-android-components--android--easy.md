---
id: "20251015082237548"
title: "Main Android Components / Основные компоненты Android"
topic: android
difficulty: easy
status: draft
created: 2025-10-15
tags: [android, android/activity, android/broadcast-receiver, android/content-provider, android/service, broadcast-receiver, components, content-provider, service, difficulty/easy]
---
# Какие основные компоненты Android-приложения?

**English**: What are the main Android application components?

## Answer (EN)
The **four main Android components** are:

**1. Activity** - UI Screen
- Represents one screen with user interface
- User interacts with app through Activities
- Example: HomeActivity, ProfileActivity

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

**2. Service** - Background Operations
- Performs long-running operations without UI
- Runs in background
- Example: Music playback, data sync

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Play music in background
        return START_STICKY
    }
}
```

**3. BroadcastReceiver** - System Events
- Listens to system or app broadcasts
- Responds to events
- Example: Battery low, network change

```kotlin
class NetworkReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Handle network change
    }
}
```

**4. ContentProvider** - Data Sharing
- Manages and shares app data
- Allows data access from other apps
- Example: Contacts, MediaStore

```kotlin
class MyContentProvider : ContentProvider() {
    override fun query(...): Cursor? {
        // Provide data to other apps
    }
}
```

**Summary:**

| Component | Purpose | Has UI | Example Use Case |
|-----------|---------|--------|------------------|
| Activity | UI screen | - Yes | Login screen |
| Service | Background work | - No | Music player |
| BroadcastReceiver | Event listener | - No | Battery alerts |
| ContentProvider | Data sharing | - No | Contact list |

All components declared in **AndroidManifest.xml**.

## Ответ (RU)

**Четыре основных компонента Android:**

**1. Activity** - Экран UI
- Представляет один экран с пользовательским интерфейсом
- Пользователь взаимодействует с приложением через Activity
- Пример: HomeActivity, ProfileActivity

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

**2. Service** - Фоновые операции
- Выполняет длительные операции без UI
- Работает в фоне
- Пример: Воспроизведение музыки, синхронизация данных

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Воспроизведение музыки в фоне
        return START_STICKY
    }
}
```

**3. BroadcastReceiver** - Системные события
- Прослушивает системные или приложением рассылаемые события
- Реагирует на события
- Пример: Низкий заряд батареи, изменение сети

```kotlin
class NetworkReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Обработать изменение сети
    }
}
```

**4. ContentProvider** - Обмен данными
- Управляет и делится данными приложения
- Позволяет доступ к данным из других приложений
- Пример: Контакты, MediaStore

```kotlin
class MyContentProvider : ContentProvider() {
    override fun query(...): Cursor? {
        // Предоставить данные другим приложениям
    }
}
```

**Резюме:**

| Компонент | Назначение | Есть UI | Пример применения |
|-----------|------------|---------|-------------------|
| Activity | Экран UI | Да | Экран входа |
| Service | Фоновая работа | Нет | Музыкальный плеер |
| BroadcastReceiver | Слушатель событий | Нет | Оповещения о батарее |
| ContentProvider | Обмен данными | Нет | Список контактов |

Все компоненты объявляются в **AndroidManifest.xml**.


---

## Related Questions

### Related (Easy)
- [[q-architecture-components-libraries--android--easy]] - Fundamentals
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Fundamentals
- [[q-what-unifies-android-components--android--easy]] - Fundamentals
- [[q-android-components-besides-activity--android--easy]] - Fundamentals
- [[q-material3-components--material-design--easy]] - Fundamentals

### Advanced (Harder)
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Fundamentals
- [[q-what-unites-the-main-components-of-an-android-application--android--medium]] - Fundamentals
- [[q-hilt-components-scope--android--medium]] - Fundamentals
