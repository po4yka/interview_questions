---
id: 20251012-122756
title: Activity Lifecycle Methods / Методы жизненного цикла Activity
aliases:
- Activity Lifecycle Methods
- Методы жизненного цикла Activity
topic: android
subtopics:
- lifecycle
- activity
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-viewmodel-pattern--android--easy
- q-fragment-vs-activity-lifecycle--android--medium
created: 2025-10-15
updated: 2025-10-15
tags:
- android/lifecycle
- android/activity
- difficulty/medium
---

# Вопрос (RU)
> Что такое Методы жизненного цикла Activity?

---

# Question (EN)
> What are Activity Lifecycle Methods?

## Answer (EN)
Activity lifecycle methods are callbacks invoked by Android system during state changes. The LifecycleOwner interface provides lifecycle-aware components. Understanding the lifecycle is critical for proper resource management and avoiding [[c-memory-leaks|memory leaks]].

**Main lifecycle methods:**

- `onCreate()`: Initialize Activity (create UI, bind data) - called ONCE
- `onStart()`: Activity becomes visible - called MULTIPLE times
- `onResume()`: Activity in foreground, user can interact
- `onPause()`: Activity losing focus, user leaving - save data quickly
- `onStop()`: Activity no longer visible - release resources
- `onRestart()`: Activity restarting from stopped state
- `onDestroy()`: Activity being destroyed - final cleanup

**Lifecycle flow:**

```
onCreate() → onStart() → onResume() → RUNNING
                ↑           ↓
            onRestart() ← onPause() → onStop() → onDestroy()
```

**Common scenarios:**

**First launch:**
```
onCreate() → onStart() → onResume()
```

**Press Home button:**
```
onPause() → onStop()
```

**Return to app:**
```
onRestart() → onStart() → onResume()
```

**Screen rotation:**
```
onPause() → onStop() → onDestroy() → onCreate() → onStart() → onResume()
```

**Key rules:**

- `onCreate()`: Initialize UI, create objects, bind data
- `onPause()`: Save critical data, stop animations - must be FAST
- `onStop()`: Release resources, unregister listeners
- `onDestroy()`: Final cleanup - may not be called (system kill)

**Modern approach:**

```kotlin
// Use DefaultLifecycleObserver (not deprecated @OnLifecycleEvent)
class MyLifecycleObserver : DefaultLifecycleObserver {
    override fun onResume(owner: LifecycleOwner) {
        // Start updates
    }

    override fun onPause(owner: LifecycleOwner) {
        // Stop updates
    }
}

// Register observer
lifecycle.addObserver(MyLifecycleObserver())
```

**Resource management:**

```kotlin
// BAD - Resource leak
override fun onResume() {
    super.onResume()
    mediaPlayer = MediaPlayer.create(this, R.raw.video)
    mediaPlayer.start()
}

// GOOD - Proper lifecycle management
override fun onResume() {
    super.onResume()
    mediaPlayer.start()
}

override fun onPause() {
    super.onPause()
    mediaPlayer.pause()
}

override fun onDestroy() {
    super.onDestroy()
    mediaPlayer.release()
}
```

**State saving:**

```kotlin
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putString("user_input", editText.text.toString())
}

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    if (savedInstanceState != null) {
        val savedText = savedInstanceState.getString("user_input")
        editText.setText(savedText)
    }
}
```

## Follow-ups

- How does Fragment lifecycle relate to Activity lifecycle?
- What happens during configuration changes?
- How do you handle memory pressure in lifecycle methods?
- What's the difference between onPause() and onStop()?
- How do you test lifecycle methods?

## References

- [Android Activity Lifecycle Guide](https://developer.android.com/guide/components/activities/activity-lifecycle)
- [Lifecycle-Aware Components](https://developer.android.com/topic/libraries/architecture/lifecycle)
- [Saving and Restoring Activity State](https://developer.android.com/guide/components/activities/activity-lifecycle#saras)

## Related Questions

### Prerequisites (Easier)
- [[q-viewmodel-pattern--android--easy]] - Lifecycle management
- [[q-android-app-components--android--easy]] - Activity basics

### Related (Medium)
- [[q-fragment-basics--android--easy]] - Fragment lifecycle
- [[q-what-are-services-for--android--easy]] - Service lifecycle