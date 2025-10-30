---
id: 20251012-122756
title: Activity Lifecycle Methods / Методы жизненного цикла Activity
aliases: ["Activity Lifecycle Methods", "Методы жизненного цикла Activity"]
topic: android
subtopics: [activity, lifecycle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-fragment-vs-activity-lifecycle--android--medium, q-viewmodel-pattern--android--easy, c-lifecycle, q-configuration-changes--android--medium]
created: 2025-10-15
updated: 2025-10-29
tags: [android/activity, android/lifecycle, jetpack, difficulty/medium]
sources: []
date created: Wednesday, October 29th 2025, 4:18:27 pm
date modified: Thursday, October 30th 2025, 11:12:49 am
---

# Вопрос (RU)
> Объясните методы жизненного цикла Activity и правила управления ресурсами в них.

---

# Question (EN)
> Explain Activity lifecycle methods and resource management rules within them.

---

## Ответ (RU)

Методы жизненного цикла Activity - это callback-функции, вызываемые системой при изменении состояния. Понимание жизненного цикла критично для правильного управления ресурсами и избежания утечек памяти.

### Основные методы

```kotlin
onCreate() → onStart() → onResume() → RUNNING
                ↑           ↓
            onRestart() ← onPause() → onStop() → onDestroy()
```

- `onCreate()`: Инициализация Activity (создание UI, привязка данных) - вызывается ОДИН раз
- `onStart()`: Activity становится видимой пользователю
- `onResume()`: Activity на переднем плане, пользователь может взаимодействовать
- `onPause()`: Activity теряет фокус - сохранить критичные данные (должен быть БЫСТРЫМ < 1с)
- `onStop()`: Activity больше не видна - освободить тяжёлые ресурсы
- `onDestroy()`: Activity уничтожается - финальная очистка

### Правила управления ресурсами

```kotlin
// ❌ ПЛОХО - Утечка ресурсов
class BadActivity : AppCompatActivity() {
    override fun onResume() {
        super.onResume()
        // ❌ Создаёт новый экземпляр каждый раз
        val player = MediaPlayer.create(this, R.raw.video)
        player.start()
    }
}

// ✅ ХОРОШО - Правильное управление
class GoodActivity : AppCompatActivity() {
    private lateinit var mediaPlayer: MediaPlayer

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        mediaPlayer = MediaPlayer.create(this, R.raw.video)
    }

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
}
```

### Современный подход: Lifecycle Observer

```kotlin
// ✅ Используйте DefaultLifecycleObserver
class LocationObserver(
    private val locationManager: LocationManager
) : DefaultLifecycleObserver {

    override fun onResume(owner: LifecycleOwner) {
        locationManager.startUpdates()
    }

    override fun onPause(owner: LifecycleOwner) {
        locationManager.stopUpdates()
    }
}

// В Activity
lifecycle.addObserver(LocationObserver(locationManager))
```

### Важные различия

**onPause() vs onStop()**:
- `onPause()`: Activity частично видна (диалог поверх) - должен быть БЫСТРЫМ
- `onStop()`: Activity полностью скрыта - можно выполнять более тяжёлые операции

**onStop() vs onDestroy()**:
- `onStop()`: Activity может быть убита системой без вызова `onDestroy()`
- `onDestroy()`: Гарантированная очистка только если вызван явно

### Обработка конфигурационных изменений

```kotlin
// ✅ Сохранение состояния при повороте экрана
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putInt("counter", counter)
}

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    counter = savedInstanceState?.getInt("counter") ?: 0
}
```

---

## Answer (EN)

Activity lifecycle methods are callbacks invoked by the system during state changes. Understanding the lifecycle is critical for proper resource management and avoiding memory leaks.

### Core Methods

```kotlin
onCreate() → onStart() → onResume() → RUNNING
                ↑           ↓
            onRestart() ← onPause() → onStop() → onDestroy()
```

- `onCreate()`: Initialize Activity (create UI, bind data) - called ONCE
- `onStart()`: Activity becomes visible to user
- `onResume()`: Activity in foreground, user can interact
- `onPause()`: Activity losing focus - save critical data (must be FAST < 1s)
- `onStop()`: Activity no longer visible - release heavy resources
- `onDestroy()`: Activity being destroyed - final cleanup

### Resource Management Rules

```kotlin
// ❌ BAD - Resource leak
class BadActivity : AppCompatActivity() {
    override fun onResume() {
        super.onResume()
        // ❌ Creates new instance every time
        val player = MediaPlayer.create(this, R.raw.video)
        player.start()
    }
}

// ✅ GOOD - Proper lifecycle management
class GoodActivity : AppCompatActivity() {
    private lateinit var mediaPlayer: MediaPlayer

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        mediaPlayer = MediaPlayer.create(this, R.raw.video)
    }

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
}
```

### Modern Approach: Lifecycle Observer

```kotlin
// ✅ Use DefaultLifecycleObserver
class LocationObserver(
    private val locationManager: LocationManager
) : DefaultLifecycleObserver {

    override fun onResume(owner: LifecycleOwner) {
        locationManager.startUpdates()
    }

    override fun onPause(owner: LifecycleOwner) {
        locationManager.stopUpdates()
    }
}

// In Activity
lifecycle.addObserver(LocationObserver(locationManager))
```

### Important Distinctions

**onPause() vs onStop()**:
- `onPause()`: Activity partially visible (dialog on top) - must be FAST
- `onStop()`: Activity fully hidden - can perform heavier operations

**onStop() vs onDestroy()**:
- `onStop()`: Activity can be killed by system without calling `onDestroy()`
- `onDestroy()`: Guaranteed cleanup only if called explicitly

### Handling Configuration Changes

```kotlin
// ✅ Save state during screen rotation
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putInt("counter", counter)
}

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    counter = savedInstanceState?.getInt("counter") ?: 0
}
```

---

## Follow-ups

- What happens during configuration changes and how does ViewModel survive them?
- When would onDestroy() not be called and how to handle it?
- How does Fragment lifecycle relate to Activity lifecycle and what are the ordering guarantees?
- What operations should be avoided in onPause() due to performance constraints?
- How does process death differ from normal lifecycle transitions and what survives it?

## References

- [[c-lifecycle]]
- [[c-viewmodel]]
- [[moc-android]]
- https://developer.android.com/guide/components/activities/activity-lifecycle

## Related Questions

### Prerequisites (Easier)
- [[q-viewmodel-pattern--android--easy]]
- [[q-what-is-activity--android--easy]]

### Related (Medium)
- [[q-fragment-vs-activity-lifecycle--android--medium]]
- [[q-configuration-changes--android--medium]]
- [[q-savedinstancestate--android--medium]]

### Advanced (Harder)
- [[q-process-death-handling--android--hard]]
- [[q-lifecycle-aware-components--android--hard]]