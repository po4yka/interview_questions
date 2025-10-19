---
id: 20251012-122756
title: "Activity Lifecycle Methods / Методы жизненного цикла Activity"
aliases: [Activity Lifecycle Methods, Методы жизненного цикла Activity]
topic: android
subtopics: [lifecycle, activity]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-viewmodel-pattern--android--easy, q-fragment-lifecycle--android--medium, q-lifecycle-aware-components--android--medium]
created: 2025-10-15
updated: 2025-10-15
tags: [android/lifecycle, android/activity, lifecycle, activity, difficulty/medium]
---
# Question (EN)
> What Activity lifecycle methods exist and how do they work?

# Вопрос (RU)
> Какие есть методы жизненного цикла Activity и как они отрабатывают?

---

## Answer (EN)

Activity lifecycle methods are callbacks invoked by Android system during state changes.

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

## Ответ (RU)

Методы жизненного цикла Activity представляют собой коллбэки, вызываемые системой Android при изменении состояния.

**Основные методы жизненного цикла:**

- `onCreate()`: Инициализация Activity (создание UI, привязка данных) - вызывается ОДИН раз
- `onStart()`: Activity становится видимой - может вызываться МНОГО раз
- `onResume()`: Activity на переднем плане, пользователь может взаимодействовать
- `onPause()`: Activity теряет фокус, пользователь уходит - сохранить данные быстро
- `onStop()`: Activity больше не видна - освободить ресурсы
- `onRestart()`: Activity возобновляется после остановки
- `onDestroy()`: Activity уничтожается - финальная очистка

**Поток жизненного цикла:**

```
onCreate() → onStart() → onResume() → RUNNING
                ↑           ↓
            onRestart() ← onPause() → onStop() → onDestroy()
```

**Распространённые сценарии:**

**Первый запуск:**
```
onCreate() → onStart() → onResume()
```

**Нажатие кнопки Home:**
```
onPause() → onStop()
```

**Возврат в приложение:**
```
onRestart() → onStart() → onResume()
```

**Поворот экрана:**
```
onPause() → onStop() → onDestroy() → onCreate() → onStart() → onResume()
```

**Ключевые правила:**

- `onCreate()`: Инициализировать UI, создать объекты, привязать данные
- `onPause()`: Сохранить критичные данные, остановить анимации - должно быть БЫСТРО
- `onStop()`: Освободить ресурсы, отменить регистрацию слушателей
- `onDestroy()`: Финальная очистка - может не вызваться (убийство системой)

**Современный подход:**

```kotlin
// Использовать DefaultLifecycleObserver (не устаревший @OnLifecycleEvent)
class MyLifecycleObserver : DefaultLifecycleObserver {
    override fun onResume(owner: LifecycleOwner) {
        // Начать обновления
    }

    override fun onPause(owner: LifecycleOwner) {
        // Остановить обновления
    }
}

// Зарегистрировать наблюдатель
lifecycle.addObserver(MyLifecycleObserver())
```

**Управление ресурсами:**

```kotlin
// ПЛОХО - Утечка ресурсов
override fun onResume() {
    super.onResume()
    mediaPlayer = MediaPlayer.create(this, R.raw.video)
    mediaPlayer.start()
}

// ХОРОШО - Правильное управление жизненным циклом
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

**Сохранение состояния:**

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

---

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
- [[q-fragment-lifecycle--android--medium]] - Fragment lifecycle
- [[q-lifecycle-aware-components--android--medium]] - Modern lifecycle approach
- [[q-configuration-changes--android--medium]] - Handling configuration changes
- [[q-memory-management-android--android--medium]] - Resource management

### Advanced (Harder)
- [[q-activity-task-stack--android--hard]] - Task management
- [[q-process-lifecycle--android--hard]] - Process lifecycle
