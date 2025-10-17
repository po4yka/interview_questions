---
id: "20251015082237440"
title: "Android Components Besides Activity / Компоненты Android кроме Activity"
topic: android
difficulty: easy
status: draft
created: 2025-10-15
tags: [android-components, android/android-components, broadcast-receiver, components, content-provider, fragment, service, view, viewmodel, difficulty/easy]
---
# Какие компоненты используются помимо activity?

# Question (EN)
> What components are used in Android besides Activity?

# Вопрос (RU)
> Какие компоненты используются в Android помимо Activity?

---

## Answer (EN)

Besides Activity, Android uses: **Service** (background tasks), **Broadcast Receiver** (system events), **Content Provider** (data sharing), **Fragment** (UI modularization), **ViewModel** (UI state management), **View** (UI building blocks), and **Application** (app-wide state).

---

## Ответ (RU)

Помимо Activity, Android использует несколько других **ключевых компонентов**, каждый из которых играет уникальную роль в создании функциональных мобильных приложений.

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

## Ответ (RU)
Помимо Activity используется ряд других ключевых компонентов: Service (фоновые операции), Broadcast Receiver (широковещательные сообщения), Content Provider (обмен данными), Fragment (модульные секции UI), View (строительный блок UI), ViewModel (управление данными UI).


---

## Related Questions

### Related (Medium)
- [[q-architecture-components-libraries--android--easy]] - Fundamentals

### Advanced (Harder)
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Fundamentals
- [[q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]] - Activity
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Activity
