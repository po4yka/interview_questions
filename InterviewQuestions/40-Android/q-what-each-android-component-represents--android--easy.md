---
topic: android
tags:
  - activity
  - android
  - android-components
  - android/android-components
  - broadcast-receiver
  - components
  - content-provider
  - fragment
  - intent
  - service
  - view
difficulty: easy
status: reviewed
---

# Что из себя представляет каждый компонент Android-приложения?

**English**: What does each Android application component represent?

## Answer

Android applications are built from several **main components**, each with specific tasks and features. These components **interact with each other** and the operating system to create a functional application.

**Main Components:**

**1. Activity** - User Interface

Provides user interface. Each Activity represents a **single screen**.

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

**2. Service** - Background Operations

Performs **long-running operations** in background without UI.

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Play music in background
        return START_STICKY
    }
}
```

**3. BroadcastReceiver** - System Events

Receives and responds to **broadcast messages** from other apps or system.

```kotlin
class NetworkReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Handle network change
    }
}
```

**4. ContentProvider** - Data Sharing

Enables apps to **share data** with other apps.

```kotlin
class MyContentProvider : ContentProvider() {
    override fun query(...): Cursor? {
        // Provide data to other apps
    }
}
```

**5. Fragment** - UI Portion

Represents a **portion of UI** or behavior in an Activity.

```kotlin
class ProfileFragment : Fragment() {
    override fun onCreateView(...): View? {
        return inflater.inflate(R.layout.fragment_profile, container, false)
    }
}
```

**6. View** - UI Building Block

Basic **building block** for UI components.

```kotlin
class CustomButton : View(context) {
    // Custom view implementation
}
```

**7. Intent** - Communication

Used for **communication between components**.

```kotlin
val intent = Intent(this, ProfileActivity::class.java)
startActivity(intent)
```

**Summary:**

| Component | Purpose | Has UI | Example |
|-----------|---------|--------|---------|
| Activity | Screen | - Yes | Login screen |
| Service | Background work | - No | Music player |
| BroadcastReceiver | Events | - No | Network change |
| ContentProvider | Data sharing | - No | Contacts |
| Fragment | UI portion | - Yes | Tab content |
| View | UI element | - Yes | Button, TextView |
| Intent | Messaging | - No | Start Activity |

## Ответ

В Android приложения строятся из нескольких основных компонентов, каждый из которых имеет свои специфические задачи и особенности. Эти компоненты взаимодействуют друг с другом и с операционной системой для создания функционального приложения.

**Основные компоненты:** Activity (пользовательский интерфейс), Service (фоновые операции), Broadcast Receiver (системные события), Content Provider (обмен данными), Fragment (часть UI), View (строительный блок UI), Intent (связь между компонентами).

