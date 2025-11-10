---
id: android-370
title: What Does The Lifecycle Library Do / Что делает библиотека Lifecycle
aliases:
- What Does The Lifecycle Library Do
- Что делает библиотека Lifecycle
topic: android
subtopics:
- architecture-mvvm
- lifecycle
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
sources: []
status: draft
moc: moc-android
related:
- c-android
- q-service-lifecycle-binding--android--hard
- q-what-is-viewmodel--android--medium
- q-why-was-the-lifecycle-library-created--android--hard
created: 2025-10-15
updated: 2025-11-10
tags:
- android
- android/architecture-mvvm
- android/lifecycle
- difficulty/medium
- lifecycle-aware

---

# Вопрос (RU)

> Что делает библиотека Lifecycle?

---

## Ответ (RU)

**Библиотека Lifecycle** предоставляет классы и интерфейсы для создания **lifecycle-aware компонентов**, которые автоматически адаптируют свое поведение в зависимости от текущего состояния жизненного цикла компонентов, реализующих `LifecycleOwner` (в первую очередь `Activity` и `Fragment`). Это помогает уменьшить утечки памяти и количество крэшей и улучшает архитектуру кода, делая работу с жизненным циклом явной и декларативной.

### Основные Компоненты

**1. Lifecycle** — абстракция, представляющая состояние жизненного цикла и события переходов  
**2. LifecycleOwner** — интерфейс, реализуемый компонентами (`Activity`/`Fragment` и др.), предоставляющими `Lifecycle`  
**3. LifecycleObserver** / **DefaultLifecycleObserver** — наблюдатели за изменениями жизненного цикла

### Современный Подход: DefaultLifecycleObserver

```kotlin
class VideoPlayerObserver(
    private val player: VideoPlayer
) : DefaultLifecycleObserver {

    override fun onStart(owner: LifecycleOwner) {
        player.initialize()
    }

    override fun onStop(owner: LifecycleOwner) {
        player.release()
    }
}

// Использование
class VideoActivity : AppCompatActivity() {
    private val videoPlayer = VideoPlayer()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycle.addObserver(VideoPlayerObserver(videoPlayer))
    }
}
```

Здесь освобождение ресурсов привязано к событиям жизненного цикла через `DefaultLifecycleObserver`: если `Activity` корректно проходит через `onStop`, будет вызван `onStop` у наблюдателя.

### Состояния И События

**States (состояния):** INITIALIZED → CREATED → STARTED → RESUMED → DESTROYED

**Events (события):** ON_CREATE, ON_START, ON_RESUME, ON_PAUSE, ON_STOP, ON_DESTROY

```kotlin
// Проверка текущего состояния
if (lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)) {
    // Безопасно обращаться к UI (компонент в активном состоянии)
}
```

### Интеграция С `LiveData` И Корутинами

```kotlin
class MyViewModel : ViewModel() {
    val data = MutableLiveData<String>()
}

class MainActivity : AppCompatActivity() {
    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ✅ LiveData учитывает состояние LifecycleOwner
        viewModel.data.observe(this) { value ->
            // Коллбек вызывается, когда Lifecycle как минимум STARTED;
            // при возврате в активное состояние придут актуальные данные.
        }

        // ✅ lifecycleScope привязан к жизненному циклу Activity
        lifecycleScope.launch {
            fetchData()
            // Coroutine будет отменена при onDestroy владельца lifecycleScope.
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
                    // ✅ Все Activity в сумме перешли во фронт — приложение на переднем плане
                }

                override fun onStop(owner: LifecycleOwner) {
                    // ✅ Ни одной видимой Activity — приложение в фоне
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
        super.onStart()
        locationManager.requestLocationUpdates(/* ... */)
        // ❌ Забыли removeUpdates в onStop - потенциальная утечка / лишние коллбеки
    }
}

// ✅ Осознанное использование lifecycle-aware компонента
class LocationObserver : DefaultLifecycleObserver {
    override fun onStart(owner: LifecycleOwner) {
        // requestLocationUpdates(...)
    }

    override fun onStop(owner: LifecycleOwner) {
        // removeUpdates(...)
    }
}

class GoodActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycle.addObserver(LocationObserver())  // Логика подписки/отписки инкапсулирована в observer
    }
}
```

**2. Повторное использование** — один observer работает с любыми компонентами, реализующими `LifecycleOwner`  
**3. Тестируемость** — компоненты, зависящие от `Lifecycle`, можно тестировать, эмулируя события состояний  
**4. Уменьшение boilerplate** — меньше прямых переопределений методов жизненного цикла в UI-классах

### Дополнительные вопросы (RU)

- Как библиотека Lifecycle обрабатывает изменения конфигурации?
- В чем разница между `LifecycleObserver` и `DefaultLifecycleObserver`?
- Могут ли кастомные компоненты реализовывать `LifecycleOwner`?
- Чем отличается `ProcessLifecycleOwner` от жизненного цикла конкретного компонента?
- Что произойдет, если обратиться к UI в неактивном состоянии жизненного цикла?

### Ссылки (RU)

- [[q-why-was-the-lifecycle-library-created--android--hard]]
- [[q-what-is-viewmodel--android--medium]]
- [Lifecycle](https://developer.android.com/topic/libraries/architecture/lifecycle)

### Связанные вопросы (RU)

#### Предпосылки / Концепции

- [[c-android]]

#### Предпосылки (проще)

- [[q-what-is-the-difference-between-measurement-units-like-dp-and-sp--android--easy]] - Базовые Android-концепции

#### Связанные (средний уровень)

- [[q-what-is-viewmodel--android--medium]] - Использует библиотеку Lifecycle
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] - Сохранение состояния через жизненный цикл

#### Продвинутые (сложнее)

- [[q-why-was-the-lifecycle-library-created--android--hard]] - Мотивация дизайна
- [[q-service-lifecycle-binding--android--hard]] - Продвинутое управление жизненным циклом

---

# Question (EN)

> What does the Lifecycle library do?

---

## Answer (EN)

The **Lifecycle library** provides classes and interfaces to build **lifecycle-aware components** that automatically adjust their behavior based on the current lifecycle state of components that implement `LifecycleOwner` (most commonly Activities and Fragments). It helps reduce memory leaks and crashes and improves code architecture by making lifecycle handling explicit and declarative.

### Core Components

**1. Lifecycle** — abstraction that represents lifecycle state and transition events  
**2. LifecycleOwner** — interface implemented by components (`Activity`/`Fragment` and others) that expose a `Lifecycle`  
**3. LifecycleObserver** / **DefaultLifecycleObserver** — observers that react to lifecycle changes

### Modern Approach: DefaultLifecycleObserver

```kotlin
class VideoPlayerObserver(
    private val player: VideoPlayer
) : DefaultLifecycleObserver {

    override fun onStart(owner: LifecycleOwner) {
        player.initialize()
    }

    override fun onStop(owner: LifecycleOwner) {
        player.release()
    }
}

// Usage
class VideoActivity : AppCompatActivity() {
    private val videoPlayer = VideoPlayer()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycle.addObserver(VideoPlayerObserver(videoPlayer))
    }
}
```

Here resource cleanup is tied to lifecycle events via `DefaultLifecycleObserver`: when the `Activity` goes through `onStop`, the observer's `onStop` is invoked accordingly.

### States and Events

**States:** INITIALIZED → CREATED → STARTED → RESUMED → DESTROYED

**Events:** ON_CREATE, ON_START, ON_RESUME, ON_PAUSE, ON_STOP, ON_DESTROY

```kotlin
// Check current state
if (lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)) {
    // Safe to interact with UI (owner is in an active state)
}
```

### Integration with `LiveData` and Coroutines

```kotlin
class MyViewModel : ViewModel() {
    val data = MutableLiveData<String>()
}

class MainActivity : AppCompatActivity() {
    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ✅ LiveData respects the LifecycleOwner's state
        viewModel.data.observe(this) { value ->
            // Called while Lifecycle is at least STARTED;
            // when coming back to an active state, the latest value is delivered.
        }

        // ✅ lifecycleScope is tied to Activity's lifecycle
        lifecycleScope.launch {
            fetchData()
            // This coroutine will be cancelled when the LifecycleOwner reaches onDestroy.
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
                    // ✅ All activities collectively moved to foreground — app in foreground
                }

                override fun onStop(owner: LifecycleOwner) {
                    // ✅ No visible activities — app in background
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
        super.onStart()
        locationManager.requestLocationUpdates(/* ... */)
        // ❌ Forgot removeUpdates in onStop - potential leak / unnecessary callbacks
    }
}

// ✅ Lifecycle-aware encapsulation
class LocationObserver : DefaultLifecycleObserver {
    override fun onStart(owner: LifecycleOwner) {
        // requestLocationUpdates(...)
    }

    override fun onStop(owner: LifecycleOwner) {
        // removeUpdates(...)
    }
}

class GoodActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycle.addObserver(LocationObserver())  // Subscription/unsubscription is encapsulated in the observer
    }
}
```

**2. Reusability** — the same observer works with any `LifecycleOwner` components  
**3. Testability** — components depending on `Lifecycle` can be tested by simulating state events  
**4. Reduces Boilerplate** — fewer direct lifecycle overrides in UI classes

---

## Follow-ups

- How does Lifecycle library handle configuration changes?
- What's the difference between `LifecycleObserver` and `DefaultLifecycleObserver`?
- Can custom components implement `LifecycleOwner`?
- How does `ProcessLifecycleOwner` differ from component lifecycle?
- What happens if you try to access UI in an inactive lifecycle state?

## References

- [[q-why-was-the-lifecycle-library-created--android--hard]]
- [[q-what-is-viewmodel--android--medium]]
- [Lifecycle](https://developer.android.com/topic/libraries/architecture/lifecycle)

## Related Questions

### Prerequisites / Concepts

- [[c-android]]

### Prerequisites (Easier)
- [[q-what-is-the-difference-between-measurement-units-like-dp-and-sp--android--easy]] - Basic Android concepts

### Related (Medium)
- [[q-what-is-viewmodel--android--medium]] - Uses Lifecycle library
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] - State preservation across lifecycle

### Advanced (Harder)
- [[q-why-was-the-lifecycle-library-created--android--hard]] - Design rationale
- [[q-service-lifecycle-binding--android--hard]] - Advanced lifecycle management
