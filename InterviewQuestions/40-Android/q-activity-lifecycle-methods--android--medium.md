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
created: 2025-10-15
updated: 2025-11-10
tags: [android/activity, android/lifecycle, difficulty/medium, jetpack]
sources: []

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

- `onCreate()`: Инициализация `Activity` (создание UI, привязка данных) — вызывается при каждом создании экземпляра (например, при первом запуске или после конфигурационных изменений)
- `onStart()`: `Activity` становится видимой пользователю
- `onResume()`: `Activity` на переднем плане, пользователь может взаимодействовать
- `onPause()`: `Activity` теряет фокус (поверх может появиться другая `Activity`/диалог) — сохранить критичные данные, должен быть БЫСТРЫМ (< 1с); после `onPause()` возможен переход как в `onResume()`, так и в `onStop()`
- `onStop()`: `Activity` больше не видна — освободить тяжёлые ресурсы
- `onDestroy()`: `Activity` уничтожается системой (например, при завершении или повороте с пересозданием) — финальная очистка, НО система может убить процесс без вызова `onDestroy()`

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

// ✅ ХОРОШО — Правильное управление
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

    override fun onDestroy() {
        super.onDestroy()
        mediaPlayer?.release()
        mediaPlayer = null
    }
}
```

### Современный Подход: Lifecycle Observer

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

### Важные Различия

**onPause() vs onStop()**:
- `onPause()`: `Activity` частично видна (диалог поверх) — должен быть БЫСТРЫМ; не стоит выполнять длительные операции ввода-вывода
- `onStop()`: `Activity` полностью скрыта — можно выполнять более тяжёлые операции и освобождать тяжёлые ресурсы

**onStop() vs onDestroy()**:
- `onStop()`: После него `Activity` может быть убита системой без вызова `onDestroy()`
- `onDestroy()`: Вызывается системой перед уничтожением конкретного экземпляра `Activity`, если у процесса есть возможность отработать; нельзя рассчитывать на его вызов при убийстве процесса

### Обработка Конфигурационных Изменений

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

`Activity` lifecycle methods are callbacks invoked by the system during state changes. Understanding the lifecycle is critical for proper resource management and avoiding memory leaks.

### Core Methods

```kotlin
onCreate() → onStart() → onResume() → RUNNING
                ↑           ↓
            onRestart() ← onPause() → onStop() → onDestroy()
```

- `onCreate()`: Initialize `Activity` (create UI, bind data) — called each time a new instance is created (e.g., first launch or after configuration change / process recreation)
- `onStart()`: `Activity` becomes visible to the user
- `onResume()`: `Activity` in the foreground, user can interact
- `onPause()`: `Activity` losing focus (another `Activity`/dialog on top) — save critical data, must be FAST (< 1s); after `onPause()` the system may go either back to `onResume()` or forward to `onStop()`
- `onStop()`: `Activity` no longer visible — release heavy resources
- `onDestroy()`: `Activity` is being destroyed by the system (e.g., finish() or configuration change recreation) — final cleanup; however, the process may be killed without `onDestroy()` being called

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

// ✅ GOOD — Proper lifecycle management
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

    override fun onDestroy() {
        super.onDestroy()
        mediaPlayer?.release()
        mediaPlayer = null
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
- `onPause()`: `Activity` partially visible (dialog on top) — must be FAST; avoid long-running or blocking operations
- `onStop()`: `Activity` fully hidden — you can perform heavier work and release heavy resources

**onStop() vs onDestroy()**:
- `onStop()`: After this, the `Activity` instance may be killed by the system without `onDestroy()` being called
- `onDestroy()`: Called by the system before destroying this `Activity` instance when possible; you must not rely on it for scenarios where the process is killed

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

## Дополнительные вопросы (RU)

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

## Связанные вопросы (RU)

### Связанные (Medium)
- [[q-fragment-vs-activity-lifecycle--android--medium]]

## Related Questions

### Related (Medium)
- [[q-fragment-vs-activity-lifecycle--android--medium]]
