---
id: "20251015082238599"
title: "Android App Components / Компоненты Android приложения"
topic: android
difficulty: easy
status: draft
created: 2025-10-15
tags: - android
  - app-architecture
  - components
---

# Какие основные компоненты Android-приложения?

# Question (EN)

> What are the main components of an Android application?

# Вопрос (RU)

> Какие основные компоненты Android-приложения?

---

## Answer (EN)

The four fundamental building blocks of Android applications:

1. **Activity** - UI component representing a single screen
2. **Service** - Background component for long-running operations
3. **Broadcast Receiver** - Responds to system-wide broadcast announcements
4. **Content Provider** - Manages shared app data and provides data access interface

---

## Ответ (RU)

Основные компоненты Android-приложения включают:

### 1. Activity

Представляет собой один экран с пользовательским интерфейсом. Каждая активность предназначена для выполнения одной конкретной задачи (например, выбора фотографии из галереи или отправки сообщения).

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

### 2. Services

Компоненты, которые выполняют длительные или фоновые операции без предоставления пользовательского интерфейса. Например, сервис может воспроизводить музыку в фоне, когда пользователь находится в другом приложении, или синхронизировать данные в фоновом режиме.

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Воспроизведение музыки
        return START_STICKY
    }
}
```

### 3. Broadcast Receivers

Предназначены для прослушивания и реагирования на широковещательные сообщения от других приложений или системы. Например, приложение может запускать определенные действия или уведомления в ответ на сообщения о низком заряде батареи или загрузке новой фотографии.

```kotlin
class BatteryReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        // Обработка события
    }
}
```

### 4. Content Providers

Позволяют приложениям хранить и делиться данными. Через них можно осуществлять доступ к данным внутри одного приложения из других приложений, а также управлять доступом к этим данным. Примером может служить доступ к контактам или медиафайлам на устройстве.

```kotlin
class MyContentProvider : ContentProvider() {
    override fun query(...): Cursor? {
        // Предоставление данных
    }
}
```

**English**: The main Android app components are: **Activity** (UI screen), **Services** (background operations), **Broadcast Receivers** (system event listeners), and **Content Providers** (data sharing between apps).

---

## Follow-ups

-   What is the role of Intent Filters with these components?
-   How do foreground services differ from background services post Android 8.0?
-   When to expose data via ContentProvider vs in-app repository?

## References

-   `https://developer.android.com/guide/components/fundamentals` — App components
-   `https://developer.android.com/guide/components/activities/intro-activities` — Activities
-   `https://developer.android.com/guide/components/services` — Services
-   `https://developer.android.com/guide/components/broadcasts` — Broadcasts
-   `https://developer.android.com/guide/topics/providers/content-providers` — Content providers

## Related Questions

### Related (Easy)

-   [[q-architecture-components-libraries--android--easy]] - Fundamentals
-   [[q-what-unifies-android-components--android--easy]] - Fundamentals
-   [[q-android-components-besides-activity--android--easy]] - Fundamentals
-   [[q-main-android-components--android--easy]] - Fundamentals
-   [[q-material3-components--material-design--easy]] - Fundamentals

### Advanced (Harder)

-   [[q-what-are-the-most-important-components-of-compose--android--medium]] - Fundamentals
-   [[q-what-unites-the-main-components-of-an-android-application--android--medium]] - Fundamentals
-   [[q-hilt-components-scope--android--medium]] - Fundamentals
