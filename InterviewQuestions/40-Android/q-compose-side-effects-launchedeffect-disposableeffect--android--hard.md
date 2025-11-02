---
id: android-111
title: "Compose Side Effects: LaunchedEffect vs DisposableEffect / Побочные эффекты Compose: LaunchedEffect vs DisposableEffect"
aliases: ["Compose LaunchedEffect vs DisposableEffect", "Compose Side Effects", "DisposableEffect", "LaunchedEffect", "Побочные эффекты Compose"]
topic: android
subtopics: [lifecycle, ui-compose]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-compose-performance-optimization--android--hard, q-compose-remember-derived-state--android--medium]
created: 2025-10-13
updated: 2025-10-30
tags: [android/lifecycle, android/ui-compose, compose, difficulty/hard, side-effects]
sources: [https://developer.android.com/jetpack/compose/lifecycle, https://developer.android.com/jetpack/compose/side-effects]
date created: Thursday, October 30th 2025, 11:51:33 am
date modified: Saturday, November 1st 2025, 5:43:36 pm
---

# Вопрос (RU)
> В чем разница между побочными эффектами Compose: LaunchedEffect vs DisposableEffect?

# Question (EN)
> What is the difference between compose side effects: LaunchedEffect vs DisposableEffect?

---

## Ответ (RU)

### Основные Различия

**LaunchedEffect**
- Запускает корутину в composition scope
- Автоматически отменяется при изменении ключей или recomposition выходе
- Для suspend-функций, Flow, асинхронных операций

**DisposableEffect**
- Регистрирует внешние ресурсы (listeners, observers, callbacks)
- Требует явного cleanup через `onDispose`
- Для lifecycle-aware и non-suspend ресурсов

### Примеры Использования

**LaunchedEffect с автоперезапуском:**
```kotlin
LaunchedEffect(userId) { // ✅ Перезапуск при изменении userId
  repository.loadUser(userId)
    .onSuccess { state.value = it }
    .onFailure { showError(it) }
}
```

**LaunchedEffect + Flow:**
```kotlin
LaunchedEffect(Unit) { // ✅ Единожды за lifecycle
  viewModel.events.collect { event ->
    when (event) {
      is NavigateEvent -> navigator.navigate(event.route)
    }
  }
}
```

**DisposableEffect для внешних callbacks:**
```kotlin
DisposableEffect(lifecycleOwner) {
  val observer = LifecycleEventObserver { _, event ->
    if (event == Lifecycle.Event.ON_RESUME) {
      // ✅ Реакция на lifecycle
    }
  }
  lifecycleOwner.lifecycle.addObserver(observer)
  onDispose { // ✅ Обязательная очистка
    lifecycleOwner.lifecycle.removeObserver(observer)
  }
}
```

**DisposableEffect для сенсоров:**
```kotlin
DisposableEffect(sensorType) {
  val listener = object : SensorEventListener {
    override fun onSensorChanged(e: SensorEvent) { /* update */ }
    override fun onAccuracyChanged(s: Sensor, a: Int) {}
  }
  sensorManager.registerListener(listener, sensor, SENSOR_DELAY_NORMAL)
  onDispose { sensorManager.unregisterListener(listener) } // ✅ Cleanup
}
```

### Выбор API

| API | Когда использовать |
|-----|-------------------|
| **LaunchedEffect** | Suspend-операции, Flow, API calls, таймеры |
| **DisposableEffect** | Listeners, observers, native ресурсы, lifecycle callbacks |
| **rememberCoroutineScope** | Event-driven корутины (клики, swipe) |
| **SideEffect** | Синхронизация state после recomposition (без suspend) |

### Распространенные Ошибки

❌ **Неверные ключи:**
```kotlin
LaunchedEffect(callback) { // ❌ Перезапуск при каждой recomposition
  callback()
}
```

✅ **Стабильные ключи:**
```kotlin
val stableCallback = rememberUpdatedState(callback)
LaunchedEffect(Unit) { // ✅ Единожды
  stableCallback.value()
}
```

❌ **Отсутствие cleanup:**
```kotlin
DisposableEffect(Unit) {
  player.start() // ❌ Утечка ресурса
  // Нет onDispose!
}
```

## Answer (EN)

### Core Differences

**LaunchedEffect**
- Launches coroutine in composition scope
- Auto-cancels on key change or recomposition exit
- For suspend functions, Flow, async operations

**DisposableEffect**
- Registers external resources (listeners, observers, callbacks)
- Requires explicit cleanup via `onDispose`
- For lifecycle-aware and non-suspend resources

### Usage Examples

**LaunchedEffect with auto-restart:**
```kotlin
LaunchedEffect(userId) { // ✅ Restarts when userId changes
  repository.loadUser(userId)
    .onSuccess { state.value = it }
    .onFailure { showError(it) }
}
```

**LaunchedEffect + Flow:**
```kotlin
LaunchedEffect(Unit) { // ✅ Once per lifecycle
  viewModel.events.collect { event ->
    when (event) {
      is NavigateEvent -> navigator.navigate(event.route)
    }
  }
}
```

**DisposableEffect for external callbacks:**
```kotlin
DisposableEffect(lifecycleOwner) {
  val observer = LifecycleEventObserver { _, event ->
    if (event == Lifecycle.Event.ON_RESUME) {
      // ✅ React to lifecycle
    }
  }
  lifecycleOwner.lifecycle.addObserver(observer)
  onDispose { // ✅ Mandatory cleanup
    lifecycleOwner.lifecycle.removeObserver(observer)
  }
}
```

**DisposableEffect for sensors:**
```kotlin
DisposableEffect(sensorType) {
  val listener = object : SensorEventListener {
    override fun onSensorChanged(e: SensorEvent) { /* update */ }
    override fun onAccuracyChanged(s: Sensor, a: Int) {}
  }
  sensorManager.registerListener(listener, sensor, SENSOR_DELAY_NORMAL)
  onDispose { sensorManager.unregisterListener(listener) } // ✅ Cleanup
}
```

### API Selection

| API | When to use |
|-----|-------------|
| **LaunchedEffect** | Suspend operations, Flow, API calls, timers |
| **DisposableEffect** | Listeners, observers, native resources, lifecycle callbacks |
| **rememberCoroutineScope** | Event-driven coroutines (clicks, swipes) |
| **SideEffect** | Sync state after recomposition (no suspend) |

### Common Pitfalls

❌ **Unstable keys:**
```kotlin
LaunchedEffect(callback) { // ❌ Restarts every recomposition
  callback()
}
```

✅ **Stable keys:**
```kotlin
val stableCallback = rememberUpdatedState(callback)
LaunchedEffect(Unit) { // ✅ Once
  stableCallback.value()
}
```

❌ **Missing cleanup:**
```kotlin
DisposableEffect(Unit) {
  player.start() // ❌ Resource leak
  // No onDispose!
}
```

---

## Follow-ups

- How does `rememberUpdatedState` prevent unnecessary effect restarts?
- When should effects live in ViewModel versus Composable?
- How to test side effects for proper cleanup and leak prevention?
- What is the difference between `SideEffect` and `LaunchedEffect`?
- How do effect keys interact with recomposition and smart recomposition?

## References

- [[c-coroutines]]
- [[c-compose-lifecycle]]
- [[c-structured-concurrency]]
- https://developer.android.com/jetpack/compose/side-effects
- https://developer.android.com/jetpack/compose/lifecycle
- https://developer.android.com/jetpack/compose/mental-model

## Related Questions

### Prerequisites (Easier)
- [[q-android-jetpack-overview--android--easy]]
- [[q-compose-remember-derived-state--android--medium]]

### Related (Same Level)
- [[q-compose-performance-optimization--android--hard]]

### Advanced (Harder)
