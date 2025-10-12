---
topic: android
tags:
  - activity
  - android
  - android/activity
  - android/broadcast-receiver
  - android/content-provider
  - android/service
  - broadcast-receiver
  - components
  - content-provider
  - service
difficulty: easy
status: draft
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
Основные компоненты: Activity (экран UI), Services (фоновые операции), Broadcast Receivers (события), Content Providers (обмен данными).

