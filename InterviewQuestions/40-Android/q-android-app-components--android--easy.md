---
id: 20251012-122759
title: Android App Components / Компоненты Android приложения
aliases:
- Android App Components
- Компоненты Android приложения
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
- q-activity-lifecycle-methods--android--medium
- q-service-types-android--android--easy
- q-how-to-register-broadcastreceiver-to-receive-messages--android--medium
created: 2025-10-15
updated: 2025-10-15
tags:
- android/activity
- android/architecture-clean
- difficulty/easy
---

## Answer (EN)
Android applications have four fundamental [[c-app-components|components]]: [[c-activity|Activity]], [[c-service|Service]], [[c-broadcast-receiver|Broadcast Receiver]], and [[c-content-provider|Content Provider]].

**1. Activity:**
- UI component representing a single screen
- Handles user interactions
- Manages lifecycle states

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

**2. Service:**
- Background component for long-running operations
- No UI, runs independently
- Types: Started, Bound, Foreground

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Background music playback
        return START_STICKY
    }
}
```

**3. Broadcast Receiver:**
- Responds to system-wide broadcast announcements
- Receives and reacts to events
- Can be registered statically or dynamically

```kotlin
class BatteryReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        // Handle battery low event
    }
}
```

**4. Content Provider:**
- Manages shared app data
- Provides data access interface
- Enables data sharing between apps

```kotlin
class MyContentProvider : ContentProvider() {
    override fun query(uri: Uri, projection: Array<String>?, selection: String?, selectionArgs: Array<String>?, sortOrder: String?): Cursor? {
        // Provide data to other apps
        return null
    }
}
```

**Component Communication:**
- **Intents**: Used to communicate between components
- **Intent Filters**: Declare component capabilities
- **Manifest**: Registers all components

## Follow-ups

- How do Intents enable communication between components?
- What are the differences between started and bound services?
- When should you use static vs dynamic Broadcast Receiver registration?
- How do Content Providers enable data sharing between apps?
- What role does the AndroidManifest.xml play in component registration?

## References

- [Android App Components](https://developer.android.com/guide/components/fundamentals)
- [Activities](https://developer.android.com/guide/components/activities/intro-activities)
- [Services](https://developer.android.com/guide/components/services)
- [Broadcast Receivers](https://developer.android.com/guide/components/broadcasts)
- [Content Providers](https://developer.android.com/guide/topics/providers/content-providers)

## Related Questions

### Prerequisites (Easier)
- [[q-gradle-basics--android--easy]] - Build system
- [[q-what-is-intent--android--easy]] - Intent system

### Related (Medium)
- [[q-activity-lifecycle-methods--android--medium]] - Activity lifecycle
- [[q-what-are-services-for--android--easy]] - Service purpose
- [[q-what-is-broadcastreceiver--android--easy]] - Broadcast receivers
- [[q-broadcastreceiver-contentprovider--android--easy]] - Content providers