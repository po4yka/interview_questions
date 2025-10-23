---
id: 20251012-122764
title: Android Components Besides Activity / Компоненты Android кроме Activity
aliases:
- Android Components Besides Activity
- Компоненты Android кроме Activity
topic: android
subtopics:
- activity
- architecture-clean
question_kind: android
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-android-app-components--android--easy
- q-service-types-android--android--easy
- q-fragment-vs-activity-lifecycle--android--medium
created: 2025-10-15
updated: 2025-10-15
tags:
- android/activity
- android/architecture-clean
- difficulty/easy
---

# Вопрос (RU)
> Что такое Компоненты Android кроме Activity?

---

# Вопрос (RU)
> Что такое Компоненты Android кроме Activity?

---

# Question (EN)
> What is Android Components Besides Activity?

# Question (EN)
> What is Android Components Besides Activity?

## Answer (EN)
**Service** - Background operations without UI
Long-running tasks that don't need user interaction. Runs independently of UI lifecycle. [[c-service|Services]] handle background work without a user interface.
```kotlin
class DownloadService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Background work
        return START_STICKY
    }
}
```

**BroadcastReceiver** - System event handling
Responds to system-wide announcements like battery low, network changes, SMS received. [[c-broadcast-receiver|BroadcastReceivers]] handle system events.
```kotlin
class BatteryReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
        // Handle system events
    }
}
```

**ContentProvider** - Data sharing between apps
Provides structured data access to other applications. Acts as data layer abstraction.
```kotlin
class NotesProvider : ContentProvider() {
    override fun query(...): Cursor? {
        // Share data with other apps
    }
}
```

**Fragment** - Reusable UI modules
Modular UI components that can be combined in Activities. Supports back stack and lifecycle. [[c-fragment|Fragments]] provide modular UI components.
```kotlin
class ListFragment : Fragment() {
    override fun onCreateView(...): View? {
        return inflater.inflate(R.layout.fragment_list, container, false)
    }
}
```

**ViewModel** - UI state management
Stores and manages UI-related data. Survives configuration changes like screen rotation.
```kotlin
class ProfileViewModel : ViewModel() {
    private val _userData = MutableLiveData<User>()
    val userData: LiveData<User> = _userData
}
```

**View** - Custom UI components
Basic building blocks for user interfaces. Can be customized for specific drawing needs.
```kotlin
class CustomChart : View(context) {
    override fun onDraw(canvas: Canvas) {
        // Custom drawing
    }
}
```

| Component | Purpose | Lifecycle |
|-----------|---------|-----------|
| Service | Background work | Independent |
| BroadcastReceiver | System events | Short-lived |
| ContentProvider | Data sharing | Singleton |
| Fragment | UI modules | Tied to Activity |
| ViewModel | State management | Survives config changes |
| View | UI elements | Tied to parent |

## Follow-ups

- What's the difference between Service and IntentService?
- When should you use Fragment vs Activity?
- How does ContentProvider differ from SharedPreferences?
- What's the purpose of Application class?

## References

- https://developer.android.com/guide/components/fundamentals
- https://developer.android.com/guide/components/services
- https://developer.android.com/guide/components/broadcasts

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components overview
- [[q-what-are-services-for--android--easy]] - Service purpose
- [[q-fragment-basics--android--easy]] - Fragment basics

### Related (Medium)
- [[q-android-service-types--android--easy]] - Service types
- [[q-what-is-broadcastreceiver--android--easy]] - Broadcast receiver basics
- [[q-broadcastreceiver-contentprovider--android--easy]] - Broadcast receiver and content provider
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Fragment lifecycle

### Advanced (Harder)
- [[q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard]] - Fragment callbacks
- [[q-fragments-and-activity-relationship--android--hard]] - Fragment-activity relationship