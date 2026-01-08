---\
id: "20251023-120100"
title: "Android Lifecycle / Жизненный цикл Android"
aliases: ["Android Lifecycle", "Lifecycle Components", "Lifecycle", "Жизненный цикл"]
summary: "Framework for managing Android component states and lifecycle-aware behavior"
topic: "android"
subtopics: ["architecture-components", "lifecycle"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: ["c-activity-lifecycle", "c-fragment-lifecycle", "c-viewmodel", "c-process-lifecycle", "c-coroutines"]
created: "2025-10-23"
updated: "2025-10-23"
tags: ["android", "architecture-components", "concept", "difficulty/medium", "lifecycle"]
---\

# Android Lifecycle / Жизненный Цикл Android

## Summary (EN)

Android `Lifecycle` refers to the series of states that Android components (`Activity`, `Fragment`, `Service`) go through from creation to destruction. The `Lifecycle` Architecture `Component` provides classes and interfaces that help build lifecycle-aware components, which automatically adjust their behavior based on the current lifecycle state, preventing memory leaks and crashes.

## Краткое Описание (RU)

Жизненный цикл Android — это серия состояний, через которые проходят компоненты Android (`Activity`, `Fragment`, `Service`) от создания до уничтожения. Архитектурный компонент `Lifecycle` предоставляет классы и интерфейсы для создания компонентов, учитывающих жизненный цикл, которые автоматически адаптируют свое поведение в зависимости от текущего состояния, предотвращая утечки памяти и сбои.

## Key Points (EN)

- **`Lifecycle` States**: CREATED, STARTED, RESUMED, DESTROYED
- **`Lifecycle` Events**: ON_CREATE, ON_START, ON_RESUME, ON_PAUSE, ON_STOP, ON_DESTROY
- **`LifecycleOwner`**: Interface implemented by `Activity` and `Fragment`
- **LifecycleObserver**: Interface for components that observe lifecycle changes
- **`Lifecycle`-aware components**: Automatically respond to lifecycle changes

## Ключевые Моменты (RU)

- **Состояния жизненного цикла**: CREATED, STARTED, RESUMED, DESTROYED
- **События жизненного цикла**: ON_CREATE, ON_START, ON_RESUME, ON_PAUSE, ON_STOP, ON_DESTROY
- **`LifecycleOwner`**: Интерфейс, реализуемый `Activity` и `Fragment`
- **LifecycleObserver**: Интерфейс для компонентов, наблюдающих за изменениями жизненного цикла
- **Компоненты, учитывающие жизненный цикл**: Автоматически реагируют на изменения жизненного цикла

## Activity Lifecycle States

```
CREATED → STARTED → RESUMED → STARTED → CREATED → DESTROYED
   ↓         ↓         ↓         ↑         ↑
onCreate  onStart  onResume  onPause   onStop   onDestroy
```

### State Transitions

```kotlin
// Activity lifecycle callbacks
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Initialize UI, set content view
        // State: CREATED
    }

    override fun onStart() {
        super.onStart()
        // Component becomes visible
        // State: STARTED
    }

    override fun onResume() {
        super.onResume()
        // Component in foreground, interactive
        // State: RESUMED
    }

    override fun onPause() {
        super.onPause()
        // Component losing focus
        // State: STARTED
    }

    override fun onStop() {
        super.onStop()
        // Component no longer visible
        // State: CREATED
    }

    override fun onDestroy() {
        super.onDestroy()
        // Component being destroyed
        // Clean up resources
    }
}
```

## Lifecycle-Aware Components

### Using LifecycleObserver

```kotlin
class MyObserver : DefaultLifecycleObserver {

    override fun onCreate(owner: LifecycleOwner) {
        // React to ON_CREATE
    }

    override fun onStart(owner: LifecycleOwner) {
        // React to ON_START
    }

    override fun onResume(owner: LifecycleOwner) {
        // Start listening for updates
    }

    override fun onPause(owner: LifecycleOwner) {
        // Stop listening for updates
    }

    override fun onDestroy(owner: LifecycleOwner) {
        // Clean up resources
    }
}

// In Activity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycle.addObserver(MyObserver())
    }
}
```

### Custom LifecycleOwner

```kotlin
class MyLocationManager(context: Context, lifecycle: Lifecycle) {

    init {
        lifecycle.addObserver(object : DefaultLifecycleObserver {
            override fun onResume(owner: LifecycleOwner) {
                startLocationUpdates()
            }

            override fun onPause(owner: LifecycleOwner) {
                stopLocationUpdates()
            }
        })
    }

    private fun startLocationUpdates() {
        // Start receiving location updates
    }

    private fun stopLocationUpdates() {
        // Stop receiving location updates
    }
}
```

## Use Cases

### When to Use

- Managing resources that should be active only when component is visible
- Starting/stopping animations based on lifecycle
- Network requests that should be cancelled when component is destroyed
- Location updates that should respect lifecycle
- Observing `LiveData` or `Flow` in ViewModels
- Camera, sensors, or other system resources

### When to Avoid

- One-time initialization that doesn't need cleanup
- Pure business logic without system resources
- Static utility functions
- Data classes or simple models

## Trade-offs

**Pros**:
- **Automatic cleanup**: Prevents memory leaks and crashes
- **Decoupled code**: `Lifecycle` logic separated from component code
- **Reusable**: `Lifecycle` observers can be shared across components
- **Predictable**: Clear state transitions and events
- **Integration**: Works seamlessly with Architecture Components

**Cons**:
- **Complexity**: Adds abstraction layer to understand
- **Learning curve**: Requires understanding lifecycle states and events
- **Boilerplate**: May require additional classes for observers
- **Debugging**: `Lifecycle` issues can be harder to trace

## Common Lifecycle Issues

### Memory Leaks

```kotlin
// BAD: Listener not removed
class MainActivity : AppCompatActivity() {
    override fun onResume() {
        super.onResume()
        locationManager.addListener(this) // Leak if not removed
    }
}

// GOOD: Lifecycle-aware
class MainActivity : AppCompatActivity() {
    init {
        lifecycle.addObserver(object : DefaultLifecycleObserver {
            override fun onResume(owner: LifecycleOwner) {
                locationManager.addListener(this@MainActivity)
            }

            override fun onPause(owner: LifecycleOwner) {
                locationManager.removeListener(this@MainActivity)
            }
        })
    }
}
```

### Configuration Changes

```kotlin
// Handle configuration changes (rotation, etc.)
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // savedInstanceState is null on first creation
        // non-null after configuration change
        if (savedInstanceState != null) {
            // Restore state
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Save state before destruction
    }
}
```

## Related Questions

- [[q-activity-lifecycle-states--android--easy]]
- [[q-fragment-lifecycle-difference--android--medium]]
- [[q-lifecycle-aware-components--android--medium]]
- [[q-configuration-change-handling--android--hard]]
- [[q-viewmodel-lifecycle--android--medium]]

## Related Concepts

- [[c-viewmodel]] - Survives configuration changes
- [[c-livedata]] - `Lifecycle`-aware observable data holder
- [[c-fragment]] - Has its own lifecycle tied to `Activity`
- [[c-coroutines]] - Can be scoped to lifecycle

## References

- [Android `Activity` Lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle)
- [Lifecycle-Aware Components](https://developer.android.com/topic/libraries/architecture/lifecycle)
- [Handling Lifecycles](https://developer.android.com/topic/libraries/architecture/lifecycle)
- [Fragment Lifecycle](https://developer.android.com/guide/fragments/lifecycle)
