---
id: 20251012-122756
title: Activity Lifecycle Methods / Методы жизненного цикла Activity
aliases: [Activity Lifecycle Methods, Методы жизненного цикла Activity]
topic: android
subtopics: [activity, lifecycle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-fragment-vs-activity-lifecycle--android--medium, q-viewmodel-pattern--android--easy, c-lifecycle]
created: 2025-10-15
updated: 2025-10-27
tags: [android/activity, android/lifecycle, difficulty/medium]
sources: []
---
# Вопрос (RU)
> Что такое Методы жизненного цикла Activity?

---

# Question (EN)
> What are Activity Lifecycle Methods?

---

## Ответ (RU)
Методы жизненного цикла Activity - это callback-функции, вызываемые системой Android при изменении состояния. Понимание жизненного цикла критично для правильного управления ресурсами и избежания утечек памяти.

**Основные методы:**

- `onCreate()`: Инициализация Activity (создание UI, привязка данных) - вызывается ОДИН раз
- `onStart()`: Activity становится видимой
- `onResume()`: Activity на переднем плане, пользователь может взаимодействовать
- `onPause()`: Activity теряет фокус - быстро сохранить данные (должен быть БЫСТРЫМ)
- `onStop()`: Activity больше не видна - освободить ресурсы
- `onDestroy()`: Activity уничтожается - финальная очистка

**Поток жизненного цикла:**

```kotlin
onCreate() → onStart() → onResume() → RUNNING
                ↑           ↓
            onRestart() ← onPause() → onStop() → onDestroy()
```

**Современный подход с DefaultLifecycleObserver:**

```kotlin
// ✅ Используйте DefaultLifecycleObserver (не устаревший @OnLifecycleEvent)
class MyLifecycleObserver : DefaultLifecycleObserver {
    override fun onResume(owner: LifecycleOwner) {
        // ✅ Начать обновления
    }

    override fun onPause(owner: LifecycleOwner) {
        // ✅ Остановить обновления
    }
}

lifecycle.addObserver(MyLifecycleObserver())
```

**Пример управления ресурсами:**

```kotlin
// ❌ ПЛОХО - Утечка ресурсов
override fun onResume() {
    super.onResume()
    mediaPlayer = MediaPlayer.create(this, R.raw.video) // ❌ Создаёт новый экземпляр каждый раз
    mediaPlayer.start()
}

// ✅ ХОРОШО - Правильное управление жизненным циклом
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    mediaPlayer = MediaPlayer.create(this, R.raw.video) // ✅ Создать один раз
}

override fun onResume() {
    super.onResume()
    mediaPlayer.start() // ✅ Только запуск/пауза
}

override fun onPause() {
    super.onPause()
    mediaPlayer.pause()
}

override fun onDestroy() {
    super.onDestroy()
    mediaPlayer.release() // ✅ Освободить ресурсы
}
```

## Answer (EN)
Activity lifecycle methods are callbacks invoked by Android system during state changes. Understanding the lifecycle is critical for proper resource management and avoiding memory leaks.

**Main lifecycle methods:**

- `onCreate()`: Initialize Activity (create UI, bind data) - called ONCE
- `onStart()`: Activity becomes visible
- `onResume()`: Activity in foreground, user can interact
- `onPause()`: Activity losing focus - save data quickly (must be FAST)
- `onStop()`: Activity no longer visible - release resources
- `onDestroy()`: Activity being destroyed - final cleanup

**Lifecycle flow:**

```kotlin
onCreate() → onStart() → onResume() → RUNNING
                ↑           ↓
            onRestart() ← onPause() → onStop() → onDestroy()
```

**Modern approach with DefaultLifecycleObserver:**

```kotlin
// ✅ Use DefaultLifecycleObserver (not deprecated @OnLifecycleEvent)
class MyLifecycleObserver : DefaultLifecycleObserver {
    override fun onResume(owner: LifecycleOwner) {
        // ✅ Start updates
    }

    override fun onPause(owner: LifecycleOwner) {
        // ✅ Stop updates
    }
}

lifecycle.addObserver(MyLifecycleObserver())
```

**Resource management example:**

```kotlin
// ❌ BAD - Resource leak
override fun onResume() {
    super.onResume()
    mediaPlayer = MediaPlayer.create(this, R.raw.video) // ❌ Creates new instance every time
    mediaPlayer.start()
}

// ✅ GOOD - Proper lifecycle management
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    mediaPlayer = MediaPlayer.create(this, R.raw.video) // ✅ Create once
}

override fun onResume() {
    super.onResume()
    mediaPlayer.start() // ✅ Just start/pause
}

override fun onPause() {
    super.onPause()
    mediaPlayer.pause()
}

override fun onDestroy() {
    super.onDestroy()
    mediaPlayer.release() // ✅ Release resources
}
```

---

## Follow-ups

- How does Fragment lifecycle relate to Activity lifecycle?
- What happens during configuration changes (screen rotation)?
- What's the difference between onPause() and onStop()?

## References

- [[c-lifecycle]]
- [[moc-android]]
- [Android Activity Lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle)

## Related Questions

### Prerequisites (Easier)
- [[q-viewmodel-pattern--android--easy]]

### Related (Medium)
- [[q-fragment-vs-activity-lifecycle--android--medium]]