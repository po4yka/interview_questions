---
tags:
  - android
  - components
  - service
  - broadcast-receiver
  - content-provider
  - fragment
  - view
  - viewmodel
  - easy_kotlin
  - android/android-components
  - android-components
difficulty: easy
---

# Какие компоненты используются помимо activity?

**English**: What components are used besides Activity?

## Answer

Besides Activity, Android uses several other **key components**, each playing a unique role in creating functional mobile applications.

**Main Components:**

**1. Service** - Background Operations

Performs long-running or background operations without UI.

```kotlin
class DownloadService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Download files in background
        return START_STICKY
    }
}
```

**2. BroadcastReceiver** - System Events

Receives and responds to broadcast messages from other apps or system.

```kotlin
class BatteryReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
        // Handle battery level change
    }
}
```

**3. ContentProvider** - Data Sharing

Provides a way for apps to **share data** with other apps.

```kotlin
class NotesProvider : ContentProvider() {
    override fun query(...): Cursor? {
        // Provide notes data to other apps
    }

    override fun insert(...): Uri? {
        // Allow other apps to insert data
    }
}
```

**4. Fragment** - UI Modules

Modular sections of UI that can be inserted into an Activity.

```kotlin
class ListFragment : Fragment() {
    override fun onCreateView(...): View? {
        return inflater.inflate(R.layout.fragment_list, container, false)
    }
}
```

**5. View** - UI Building Block

Basic building block for user interfaces.

```kotlin
class CustomChart : View(context) {
    override fun onDraw(canvas: Canvas) {
        // Custom drawing
    }
}
```

**6. ViewModel** - UI Data Management

Manages UI-related data.

```kotlin
class ProfileViewModel : ViewModel() {
    private val _userData = MutableLiveData<User>()
    val userData: LiveData<User> = _userData

    fun loadUser() {
        // Load user data
    }
}
```

**Comparison:**

| Component | Purpose | Lifecycle | Example Use |
|-----------|---------|-----------|-------------|
| Service | Background work | Independent | Music playback |
| BroadcastReceiver | Events | Short-lived | Network change |
| ContentProvider | Data access | Singleton | Contacts API |
| Fragment | UI portion | Tied to Activity | Tab content |
| View | UI element | Tied to parent | Custom button |
| ViewModel | Data management | Survives config changes | User profile |

**Summary:**

- **Service**: Long-running background tasks
- **BroadcastReceiver**: System event handling
- **ContentProvider**: Inter-app data sharing
- **Fragment**: Reusable UI portions
- **View**: Custom UI components
- **ViewModel**: UI data lifecycle management

## Ответ

Помимо Activity используется ряд других ключевых компонентов: Service (фоновые операции), Broadcast Receiver (широковещательные сообщения), Content Provider (обмен данными), Fragment (модульные секции UI), View (строительный блок UI), ViewModel (управление данными UI).

