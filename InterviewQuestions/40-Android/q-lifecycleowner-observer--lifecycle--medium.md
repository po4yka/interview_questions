---
id: android-lc-004
title: LifecycleOwner and LifecycleObserver / LifecycleOwner и LifecycleObserver
aliases: []
topic: android
subtopics:
- lifecycle
- jetpack
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source_note: Android interview preparation
status: draft
moc: moc-android
related:
- c-lifecycle
- c-jetpack
created: 2025-01-23
updated: 2025-01-23
tags:
- android/lifecycle
- android/jetpack
- difficulty/medium
anki_cards:
- slug: android-lc-004-0-en
  language: en
  anki_id: 1769172258557
  synced_at: '2026-01-23T16:45:05.769506'
- slug: android-lc-004-0-ru
  language: ru
  anki_id: 1769172258581
  synced_at: '2026-01-23T16:45:05.772142'
---
# Question (EN)
> What are LifecycleOwner and LifecycleObserver and how do they work?

# Vopros (RU)
> Что такое LifecycleOwner и LifecycleObserver и как они работают?

---

## Answer (EN)

**LifecycleOwner** - Interface for classes that have a lifecycle (Activity, Fragment, custom components).

**LifecycleObserver** - Interface for classes that want to observe lifecycle events.

**Core components:**
- `Lifecycle` - Object holding lifecycle state and events
- `LifecycleOwner` - Provider of lifecycle (has `getLifecycle()`)
- `LifecycleObserver` - Consumer that reacts to events

**Lifecycle states and events:**
```
INITIALIZED -> CREATED -> STARTED -> RESUMED
     |           |          |          |
  ON_CREATE  ON_START  ON_RESUME  (active)
                |          |
            ON_STOP    ON_PAUSE
     |           |
  ON_DESTROY  DESTROYED
```

**Modern approach with DefaultLifecycleObserver:**
```kotlin
class MyObserver : DefaultLifecycleObserver {
    override fun onStart(owner: LifecycleOwner) {
        // Start listening to location updates
    }

    override fun onStop(owner: LifecycleOwner) {
        // Stop listening to save battery
    }
}

// In Activity/Fragment:
lifecycle.addObserver(MyObserver())
```

**LifecycleEventObserver (alternative):**
```kotlin
class MyObserver : LifecycleEventObserver {
    override fun onStateChanged(source: LifecycleOwner, event: Lifecycle.Event) {
        when (event) {
            Lifecycle.Event.ON_START -> startCamera()
            Lifecycle.Event.ON_STOP -> stopCamera()
            else -> {}
        }
    }
}
```

**Benefits:**
- Components manage their own lifecycle cleanup
- No memory leaks from forgotten unsubscribes
- Decoupled from Activity/Fragment code
- Testable in isolation

**Custom LifecycleOwner:**
```kotlin
class MyService : Service(), LifecycleOwner {
    private val lifecycleRegistry = LifecycleRegistry(this)

    override val lifecycle: Lifecycle = lifecycleRegistry

    override fun onCreate() {
        super.onCreate()
        lifecycleRegistry.currentState = Lifecycle.State.CREATED
    }
}
```

## Otvet (RU)

**LifecycleOwner** - Интерфейс для классов, имеющих жизненный цикл (Activity, Fragment, кастомные компоненты).

**LifecycleObserver** - Интерфейс для классов, которые хотят наблюдать за событиями жизненного цикла.

**Основные компоненты:**
- `Lifecycle` - Объект, хранящий состояние и события жизненного цикла
- `LifecycleOwner` - Поставщик lifecycle (имеет `getLifecycle()`)
- `LifecycleObserver` - Потребитель, реагирующий на события

**Состояния и события lifecycle:**
```
INITIALIZED -> CREATED -> STARTED -> RESUMED
     |           |          |          |
  ON_CREATE  ON_START  ON_RESUME  (active)
                |          |
            ON_STOP    ON_PAUSE
     |           |
  ON_DESTROY  DESTROYED
```

**Современный подход с DefaultLifecycleObserver:**
```kotlin
class MyObserver : DefaultLifecycleObserver {
    override fun onStart(owner: LifecycleOwner) {
        // Начать слушать обновления локации
    }

    override fun onStop(owner: LifecycleOwner) {
        // Остановить прослушивание для экономии батареи
    }
}

// В Activity/Fragment:
lifecycle.addObserver(MyObserver())
```

**LifecycleEventObserver (альтернатива):**
```kotlin
class MyObserver : LifecycleEventObserver {
    override fun onStateChanged(source: LifecycleOwner, event: Lifecycle.Event) {
        when (event) {
            Lifecycle.Event.ON_START -> startCamera()
            Lifecycle.Event.ON_STOP -> stopCamera()
            else -> {}
        }
    }
}
```

**Преимущества:**
- Компоненты сами управляют очисткой своего жизненного цикла
- Нет утечек памяти от забытых отписок
- Отвязаны от кода Activity/Fragment
- Тестируемы изолированно

**Кастомный LifecycleOwner:**
```kotlin
class MyService : Service(), LifecycleOwner {
    private val lifecycleRegistry = LifecycleRegistry(this)

    override val lifecycle: Lifecycle = lifecycleRegistry

    override fun onCreate() {
        super.onCreate()
        lifecycleRegistry.currentState = Lifecycle.State.CREATED
    }
}
```

---

## Follow-ups
- What is the difference between Lifecycle.State and Lifecycle.Event?
- How does LiveData use LifecycleOwner?
- What is lifecycleScope in coroutines?

## References
- [[c-lifecycle]]
- [[c-jetpack]]
- [[moc-android]]
