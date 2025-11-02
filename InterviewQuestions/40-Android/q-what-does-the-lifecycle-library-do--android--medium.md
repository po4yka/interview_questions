---
id: android-370
title: "What Does The Lifecycle Library Do / Что делает библиотека Lifecycle"
aliases: ["What Does The Lifecycle Library Do", "Что делает библиотека Lifecycle"]

# Classification
topic: android
subtopics: [lifecycle, architecture-mvvm]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
sources: []

# Workflow & relations
status: draft
moc: moc-android
related: [q-why-was-the-lifecycle-library-created--android--hard, q-what-is-viewmodel--android--medium, q-service-lifecycle-binding--android--hard]

# Timestamps
created: 2025-10-15
updated: 2025-10-29

# Tags (EN only; no leading #)
tags: [android, android/lifecycle, android/architecture-mvvm, lifecycle-aware, difficulty/medium]
---

# Вопрос (RU)

> Что делает библиотека Lifecycle?

# Question (EN)

> What does the Lifecycle library do?

---

## Ответ (RU)

**Библиотека Lifecycle** предоставляет классы и интерфейсы для создания **lifecycle-aware компонентов**, которые автоматически адаптируют свое поведение в зависимости от текущего состояния жизненного цикла Activity и Fragment. Это предотвращает утечки памяти, крэши и улучшает архитектуру кода.

### Основные компоненты

**1. Lifecycle** — представляет состояние жизненного цикла
**2. LifecycleOwner** — интерфейс, реализуемый Activity/Fragment
**3. LifecycleObserver** — наблюдатель за изменениями жизненного цикла

### Современный подход: DefaultLifecycleObserver

```kotlin
class VideoPlayerObserver(
    private val player: VideoPlayer
) : DefaultLifecycleObserver {

    // ✅ Автоматическая очистка ресурсов
    override fun onStart(owner: LifecycleOwner) {
        player.initialize()
    }

    override fun onStop(owner: LifecycleOwner) {
        player.release()  // ✅ Гарантированно вызовется
    }
}

// Использование
class VideoActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycle.addObserver(VideoPlayerObserver(videoPlayer))
    }
}
```

### Состояния и события

**States (состояния):** INITIALIZED → CREATED → STARTED → RESUMED → DESTROYED

**Events (события):** ON_CREATE, ON_START, ON_RESUME, ON_PAUSE, ON_STOP, ON_DESTROY

```kotlin
// Проверка текущего состояния
if (lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)) {
    // Безопасно обращаться к UI
}
```

### Интеграция с LiveData и корутинами

```kotlin
class MyViewModel : ViewModel() {
    val data = MutableLiveData<String>()
}

class MainActivity : AppCompatActivity() {
    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ✅ LiveData автоматически lifecycle-aware
        viewModel.data.observe(this) { value ->
            // Обновления только в STARTED/RESUMED
        }

        // ✅ lifecycleScope отменяется автоматически
        lifecycleScope.launch {
            fetchData()
        }
    }
}
```

### ProcessLifecycleOwner (жизненный цикл приложения)

```kotlin
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()

        ProcessLifecycleOwner.get().lifecycle.addObserver(
            object : DefaultLifecycleObserver {
                override fun onStart(owner: LifecycleOwner) {
                    // ✅ Приложение на переднем плане
                }

                override fun onStop(owner: LifecycleOwner) {
                    // ✅ Приложение в фоне
                }
            }
        )
    }
}
```

### Преимущества

**1. Предотвращение утечек памяти**
```kotlin
// ❌ Ручное управление - легко забыть очистить
class BadActivity : AppCompatActivity() {
    override fun onStart() {
        locationManager.requestUpdates(...)
        // ❌ Забыли removeUpdates в onStop - утечка!
    }
}

// ✅ Автоматическая очистка
class GoodActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        lifecycle.addObserver(LocationObserver())  // ✅ Cleanup автоматический
    }
}
```

**2. Повторное использование** — один observer работает с любыми Activity/Fragment

**3. Тестируемость** — компоненты легко тестировать независимо

**4. Уменьшение boilerplate** — не нужно переопределять lifecycle методы

## Answer (EN)

The **Lifecycle library** provides classes and interfaces to build **lifecycle-aware components** that automatically adjust their behavior based on the current lifecycle state of Activities and Fragments. This prevents memory leaks, crashes, and improves code architecture.

### Core Components

**1. Lifecycle** — represents the lifecycle state
**2. LifecycleOwner** — interface implemented by Activity/Fragment
**3. LifecycleObserver** — observes lifecycle changes

### Modern Approach: DefaultLifecycleObserver

```kotlin
class VideoPlayerObserver(
    private val player: VideoPlayer
) : DefaultLifecycleObserver {

    // ✅ Automatic resource cleanup
    override fun onStart(owner: LifecycleOwner) {
        player.initialize()
    }

    override fun onStop(owner: LifecycleOwner) {
        player.release()  // ✅ Guaranteed to be called
    }
}

// Usage
class VideoActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycle.addObserver(VideoPlayerObserver(videoPlayer))
    }
}
```

### States and Events

**States:** INITIALIZED → CREATED → STARTED → RESUMED → DESTROYED

**Events:** ON_CREATE, ON_START, ON_RESUME, ON_PAUSE, ON_STOP, ON_DESTROY

```kotlin
// Check current state
if (lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)) {
    // Safe to access UI
}
```

### Integration with LiveData and Coroutines

```kotlin
class MyViewModel : ViewModel() {
    val data = MutableLiveData<String>()
}

class MainActivity : AppCompatActivity() {
    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ✅ LiveData is automatically lifecycle-aware
        viewModel.data.observe(this) { value ->
            // Updates only in STARTED/RESUMED
        }

        // ✅ lifecycleScope cancels automatically
        lifecycleScope.launch {
            fetchData()
        }
    }
}
```

### ProcessLifecycleOwner (App Lifecycle)

```kotlin
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()

        ProcessLifecycleOwner.get().lifecycle.addObserver(
            object : DefaultLifecycleObserver {
                override fun onStart(owner: LifecycleOwner) {
                    // ✅ App moved to foreground
                }

                override fun onStop(owner: LifecycleOwner) {
                    // ✅ App moved to background
                }
            }
        )
    }
}
```

### Benefits

**1. Prevents Memory Leaks**
```kotlin
// ❌ Manual management - easy to forget cleanup
class BadActivity : AppCompatActivity() {
    override fun onStart() {
        locationManager.requestUpdates(...)
        // ❌ Forgot removeUpdates in onStop - leak!
    }
}

// ✅ Automatic cleanup
class GoodActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        lifecycle.addObserver(LocationObserver())  // ✅ Cleanup automatic
    }
}
```

**2. Reusability** — same observer works with any Activity/Fragment

**3. Testability** — components are easily testable independently

**4. Reduces Boilerplate** — no need to override lifecycle methods

---

## Follow-ups

- How does Lifecycle library handle configuration changes?
- What's the difference between LifecycleObserver and DefaultLifecycleObserver?
- Can custom components implement LifecycleOwner?
- How does ProcessLifecycleOwner differ from component lifecycle?
- What happens if you try to access UI in an inactive lifecycle state?

## References

- [[q-why-was-the-lifecycle-library-created--android--hard]]
- [[q-what-is-viewmodel--android--medium]]
- https://developer.android.com/topic/libraries/architecture/lifecycle

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-the-difference-between-measurement-units-like-dp-and-sp--android--easy]] - Basic Android concepts

### Related (Medium)
- [[q-what-is-viewmodel--android--medium]] - Uses Lifecycle library
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] - State preservation across lifecycle

### Advanced (Harder)
- [[q-why-was-the-lifecycle-library-created--android--hard]] - Design rationale
- [[q-service-lifecycle-binding--android--hard]] - Advanced lifecycle management
