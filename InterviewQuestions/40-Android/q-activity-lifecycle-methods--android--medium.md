---
id: android-181
title: Activity Lifecycle Methods / Методы жизненного цикла Activity
aliases: [Activity Lifecycle Methods, Методы жизненного цикла Activity]
topic: android
subtopics:
  - activity
  - lifecycle
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-lifecycle
  - q-android-app-components--android--easy
  - q-how-to-save-activity-state--android--medium
  - q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium
  - q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium
created: 2025-10-15
updated: 2025-11-10
tags: [android/activity, android/lifecycle, difficulty/medium, jetpack]
sources: []

date created: Saturday, November 1st 2025, 1:24:36 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---
# Вопрос (RU)
> Объясните методы жизненного цикла `Activity` и правила управления ресурсами в них.

---

# Question (EN)
> Explain `Activity` lifecycle methods and resource management rules within them.

---

## Ответ (RU)

Методы жизненного цикла `Activity` — это callback-функции, вызываемые системой при изменении состояния. Понимание жизненного цикла критично для правильного управления ресурсами и избежания утечек памяти.

### Основные Методы

```kotlin
onCreate() → onStart() → onResume() → RUNNING
                ↑           ↓
            onRestart() ← onPause() → onStop() → onDestroy()
```

Типичный поток:
- `onCreate()` → `onStart()` → `onResume()`
- При возврате к остановленной Activity: `onRestart()` → `onStart()` → `onResume()`
- При уходе с экрана: `onPause()` → `onStop()` → (возможен `onDestroy()`)

Ключевые методы:

- `onCreate()`: Инициализация `Activity` (создание UI, привязка данных) — вызывается при создании нового экземпляра (например, при первом запуске или при пересоздании после конфигурационных изменений/убийства процесса).
- `onStart()`: `Activity` становится видимой пользователю.
- `onResume()`: `Activity` на переднем плане, пользователь может взаимодействовать.
- `onPause()`: `Activity` теряет фокус (поверх может появиться другая `Activity`/диалог) — сохранить критичные данные UI/состояния, должен быть БЫСТРЫМ (< 1с); после `onPause()` возможен переход как обратно в `onResume()`, так и далее в `onStop()`.
- `onStop()`: `Activity` больше не видна — освободить тяжёлые и невидимые ресурсы (анимации, сенсоры, приостановить сложные операции, остановить слушателей и т.п.). После `onStop()` система может убить процесс без вызова `onDestroy()`.
- `onDestroy()`: `Activity` уничтожается системой (например, при завершении через `finish()` или при пересоздании после конфигурационных изменений) — финальная очистка для случая, когда коллбек всё же вызывается; НЕЛЬЗЯ полагаться, что `onDestroy()` будет вызван при убийстве процесса.

### Правила Управления Ресурсами

```kotlin
// ❌ ПЛОХО — Утечка ресурсов
class BadActivity : AppCompatActivity() {
    override fun onResume() {
        super.onResume()
        // ❌ Создаёт новый экземпляр каждый раз и не освобождает
        val player = MediaPlayer.create(this, R.raw.video)
        player.start()
    }
}

// ✅ ХОРОШО — Правильное управление (упрощённый пример)
class GoodActivity : AppCompatActivity() {
    private var mediaPlayer: MediaPlayer? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        mediaPlayer = MediaPlayer.create(this, R.raw.video)
    }

    override fun onResume() {
        super.onResume()
        mediaPlayer?.start()
    }

    override fun onPause() {
        super.onPause()
        mediaPlayer?.pause()
    }

    override fun onStop() {
        super.onStop()
        // Высвобождение тяжёлых ресурсов, когда Activity больше не видна
        mediaPlayer?.release()
        mediaPlayer = null
    }
}
```

Важно: тяжёлые ресурсы (камера, плейер, сенсоры, подписки на локацию и т.п.) предпочтительно освобождать не позднее `onStop()`, так как процесс может быть убит после `onStop()` без вызова `onDestroy()`.

### Современный Подход: Lifecycle Observer

```kotlin
// ✅ Используйте DefaultLifecycleObserver
class LocationObserver(
    private val locationManager: LocationManager
) : DefaultLifecycleObserver {

    override fun onStart(owner: LifecycleOwner) {
        // Начинаем обновления, когда владелец стал видимым
        locationManager.startUpdates()
    }

    override fun onStop(owner: LifecycleOwner) {
        // Останавливаем, когда владелец больше не виден
        locationManager.stopUpdates()
    }
}

// В Activity
lifecycle.addObserver(LocationObserver(locationManager))
```

Такой подход инкапсулирует работу с жизненным циклом и помогает избежать утечек.

### Важные Различия

**onPause() vs onStop()**:
- `onPause()`: `Activity` может быть частично видна (диалог поверх) — должен быть БЫСТРЫМ; избегать длительных/блокирующих операций и тяжёлого I/O.
- `onStop()`: `Activity` полностью скрыта — можно выполнять более тяжёлые операции и освобождать тяжёлые ресурсы.

**onStop() vs onDestroy()**:
- `onStop()`: После него экземпляр `Activity` может быть уничтожен системой без вызова `onDestroy()`.
- `onDestroy()`: Вызывается системой перед уничтожением конкретного экземпляра `Activity`, если у процесса есть возможность отработать; нельзя рассчитывать на его вызов при убийстве процесса.

### Обработка Конфигурационных Изменений

```kotlin
// ✅ Сохранение состояния при повороте экрана
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putInt("counter", counter)
}

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    // Восстановление только легковесного состояния UI/данных
    counter = savedInstanceState?.getInt("counter") ?: 0
}
```

`onSaveInstanceState()` используется для сохранения кратковременного UI-состояния. Для долгоживущих данных и работы, переживающей конфигурационные изменения, следует использовать такие механизмы, как `ViewModel`.

---

## Answer (EN)

`Activity` lifecycle methods are callbacks invoked by the system during state changes. Understanding the lifecycle is critical for proper resource management and avoiding memory leaks.

### Core Methods

```kotlin
onCreate() → onStart() → onResume() → RUNNING
                ↑           ↓
            onRestart() ← onPause() → onStop() → onDestroy()
```

Typical flows:
- `onCreate()` → `onStart()` → `onResume()` for a fresh start.
- Returning to a stopped Activity: `onRestart()` → `onStart()` → `onResume()`.
- Leaving the screen: `onPause()` → `onStop()` → (optionally `onDestroy()`).

Key methods:

- `onCreate()`: Initialize the `Activity` (create UI, bind data) — called when a new instance is created (e.g., first launch or recreation after configuration change/process death).
- `onStart()`: `Activity` becomes visible to the user.
- `onResume()`: `Activity` is in the foreground; user can interact with it.
- `onPause()`: `Activity` is losing focus (another `Activity`/dialog on top) — persist critical UI-related state; must be FAST (< 1s). After `onPause()` the system may return to `onResume()` or proceed to `onStop()`.
- `onStop()`: `Activity` is no longer visible — release heavy and non-visible resources (animations, sensors, listeners, expensive work, etc.). After `onStop()`, the system may kill the process without calling `onDestroy()`.
- `onDestroy()`: `Activity` is being destroyed (e.g., `finish()` or recreation for configuration changes) — final cleanup when this callback is actually invoked; you MUST NOT rely on it when the process is killed.

### Resource Management Rules

```kotlin
// ❌ BAD — Resource leak
class BadActivity : AppCompatActivity() {
    override fun onResume() {
        super.onResume()
        // ❌ Creates new instance every time and never releases it
        val player = MediaPlayer.create(this, R.raw.video)
        player.start()
    }
}

// ✅ GOOD — Proper lifecycle management (simplified)
class GoodActivity : AppCompatActivity() {
    private var mediaPlayer: MediaPlayer? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        mediaPlayer = MediaPlayer.create(this, R.raw.video)
    }

    override fun onResume() {
        super.onResume()
        mediaPlayer?.start()
    }

    override fun onPause() {
        super.onPause()
        mediaPlayer?.pause()
    }

    override fun onStop() {
        super.onStop()
        // Release heavy resources once Activity is no longer visible
        mediaPlayer?.release()
        mediaPlayer = null
    }
}
```

Important: heavy resources (camera, player, sensors, location updates, etc.) should generally be released no later than `onStop()`, since the process may be killed after `onStop()` without `onDestroy()` being called.

### Modern Approach: Lifecycle Observer

```kotlin
// ✅ Use DefaultLifecycleObserver
class LocationObserver(
    private val locationManager: LocationManager
) : DefaultLifecycleObserver {

    override fun onStart(owner: LifecycleOwner) {
        // Start updates when the owner becomes visible
        locationManager.startUpdates()
    }

    override fun onStop(owner: LifecycleOwner) {
        // Stop updates when the owner is no longer visible
        locationManager.stopUpdates()
    }
}

// In Activity
lifecycle.addObserver(LocationObserver(locationManager))
```

This encapsulates lifecycle-aware work and helps prevent leaks.

### Important Distinctions

**onPause() vs onStop()**:
- `onPause()`: `Activity` may still be partially visible (e.g., dialog on top) — must be FAST; avoid long-running/blocking operations and heavy I/O.
- `onStop()`: `Activity` is fully hidden — safe place for heavier work and releasing heavy resources.

**onStop() vs onDestroy()**:
- `onStop()`: After this, the `Activity` instance may be destroyed without `onDestroy()` being called.
- `onDestroy()`: Called before destroying this `Activity` instance when the process can run it; you cannot rely on it when the process is killed.

### Handling Configuration Changes

```kotlin
// ✅ Save state during screen rotation
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putInt("counter", counter)
}

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    // Restore only lightweight UI/state data
    counter = savedInstanceState?.getInt("counter") ?: 0
}
```

`onSaveInstanceState()` is for saving transient, lightweight UI state. For longer-lived data and work that should survive configuration changes, use mechanisms like `ViewModel`.

---

## Дополнительные Вопросы (RU)

- Что происходит при конфигурационных изменениях и как `ViewModel` переживает их?
- В каких случаях `onDestroy()` может не быть вызван и как это обработать?
- Как `Fragment`-жизненный цикл соотносится с жизненным циклом `Activity` и каковы гарантии порядка вызовов?
- Какие операции следует избегать в `onPause()` из-за ограничений по производительности?
- Чем отличается завершение процесса от обычных переходов жизненного цикла и что переживает его?

## Follow-ups

- What happens during configuration changes and how does `ViewModel` survive them?
- When would onDestroy() not be called and how to handle it?
- How does `Fragment` lifecycle relate to `Activity` lifecycle and what are the ordering guarantees?
- What operations should be avoided in onPause() due to performance constraints?
- How does process death differ from normal lifecycle transitions and what survives it?

## Ссылки (RU)

- [[c-lifecycle]]
- [[moc-android]]
- "https://developer.android.com/guide/components/activities/activity-lifecycle"

## References

- [[c-lifecycle]]
- [[moc-android]]
- https://developer.android.com/guide/components/activities/activity-lifecycle

## Связанные Вопросы (RU)

### Связанные (Medium)
- [[q-fragment-vs-activity-lifecycle--android--medium]]

## Related Questions

### Related (Medium)
- [[q-fragment-vs-activity-lifecycle--android--medium]]
