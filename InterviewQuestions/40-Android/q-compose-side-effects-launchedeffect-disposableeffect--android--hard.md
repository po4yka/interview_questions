---
id: android-111
title: 'Compose Side Effects: LaunchedEffect vs DisposableEffect / Побочные эффекты
  Compose: LaunchedEffect vs DisposableEffect'
aliases:
- Compose LaunchedEffect vs DisposableEffect
- Compose Side Effects
- DisposableEffect
- LaunchedEffect
- Побочные эффекты Compose
topic: android
subtopics:
- ui-compose
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-compose-recomposition
- c-recomposition
- q-compose-compiler-plugin--android--hard
- q-compose-performance-optimization--android--hard
- q-compose-remember-derived-state--android--medium
- q-compose-side-effects-advanced--android--hard
- q-how-to-reduce-number-of-recompositions-besides-side-effects--android--hard
created: 2025-10-13
updated: 2025-11-10
tags:
- android/ui-compose
- difficulty/hard
- side-effects
sources:
- https://developer.android.com/jetpack/compose/lifecycle
- https://developer.android.com/jetpack/compose/side-effects
anki_cards:
- slug: android-111-0-en
  language: en
  anki_id: 1768366073777
  synced_at: '2026-01-23T16:45:06.417683'
- slug: android-111-0-ru
  language: ru
  anki_id: 1768366073800
  synced_at: '2026-01-23T16:45:06.418587'
---
# Вопрос (RU)
> В чем разница между побочными эффектами Compose: LaunchedEffect vs DisposableEffect?

# Question (EN)
> What is the difference between compose side effects: LaunchedEffect vs DisposableEffect?

---

## Ответ (RU)

### Основные Различия

**LaunchedEffect**
- Запускает корутину в scope композиции (Composition)
- Автоматически отменяется, когда эффект выходит из композиции: при изменении ключей или когда соответствующий Composable удаляется
- Подходит для suspend-функций, `Flow`, асинхронных операций, завязанных на жизненный цикл конкретного вхождения Composable

**DisposableEffect**
- Выполняет побочный эффект при входе в композицию синхронно
- Регистрирует внешние ресурсы (listeners, observers, callbacks)
- Требует явного cleanup через `onDispose`, который гарантированно вызывается при выходе эффекта из композиции (изменение ключей или удаление Composable)
- Подходит для lifecycle-aware и non-suspend ресурсов, которые должны быть очищены при удалении Composable

### Примеры Использования

**LaunchedEffect с автоперезапуском:**
```kotlin
LaunchedEffect(userId) { // ✅ Перезапуск при изменении userId, пока этот Composable в композиции
  repository.loadUser(userId)
    .onSuccess { state.value = it }
    .onFailure { showError(it) }
}
```

**LaunchedEffect + `Flow`:**
```kotlin
LaunchedEffect(Unit) { // ✅ Один запуск для данного вхождения Composable, пока оно остается в композиции
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
  onDispose { // ✅ Обязательная очистка при выходе из композиции или смене lifecycleOwner
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
  onDispose { sensorManager.unregisterListener(listener) } // ✅ Гарантированный cleanup при выходе Composable
}
```

### Выбор API

| API | Когда использовать |
|-----|-------------------|
| **LaunchedEffect** | Suspend-операции, `Flow`, API calls, таймеры, связанные с жизненным циклом конкретного Composable |
| **DisposableEffect** | Listeners, observers, нативные ресурсы, lifecycle callbacks, требующие детерминированного снятия регистрации при выходе Composable |
| **rememberCoroutineScope** | Event-driven корутины (клики, swipe), запускаемые из обработчиков, а не из композиции |
| **SideEffect** | Синхронизация внешнего не-suspend состояния после успешной recomposition, без корутин |

### Распространенные Ошибки

❌ **Неверные (нестабильные) ключи:**
```kotlin
LaunchedEffect(callback) { // ❌ Перезапуск при каждой recomposition, если callback не стабилен
  callback()
}
```

✅ **Стабильные ключи:**
```kotlin
val stableCallback = rememberUpdatedState(callback)
LaunchedEffect(Unit) { // ✅ Один запуск для данного вхождения Composable
  stableCallback.value()
}
```

❌ **Отсутствие cleanup:**
```kotlin
DisposableEffect(Unit) {
  player.start() // ❌ Возможная утечка ресурса: player не будет остановлен
  // Нет onDispose!
}
```

---

## Дополнительные Вопросы (RU)

- Как `rememberUpdatedState` предотвращает ненужные перезапуски эффектов?
- Когда эффекты должны жить во `ViewModel`, а когда в Composable?
- Как тестировать побочные эффекты на корректный cleanup и предотвращение утечек?
- В чем разница между `SideEffect` и `LaunchedEffect`?
- Как ключи эффектов взаимодействуют с рекомпозицией и умной рекомпозицией?

## Ссылки (RU)

- [[c-coroutines]]
- "https://developer.android.com/jetpack/compose/side-effects"
- "https://developer.android.com/jetpack/compose/lifecycle"
- "https://developer.android.com/jetpack/compose/mental-model"

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-android-jetpack-overview--android--easy]]
- [[q-compose-remember-derived-state--android--medium]]

### Связанные (тот Же уровень)
- [[q-compose-performance-optimization--android--hard]]

---

## Answer (EN)

### Core Differences

**LaunchedEffect**
- Launches a coroutine in the composition scope
- Automatically cancels when the effect leaves the composition: on key change or when the corresponding Composable is removed
- Use for suspend functions, Flows, async operations tied to the lifecycle of a specific Composable instance

**DisposableEffect**
- Runs its effect block synchronously when entering the composition
- Registers external resources (listeners, observers, callbacks)
- Requires explicit cleanup via `onDispose`, which is guaranteed to be called when the effect leaves the composition (key change or Composable removal)
- Use for lifecycle-aware and non-suspend resources that must be cleaned up when the Composable is disposed

### Usage Examples

**LaunchedEffect with auto-restart:**
```kotlin
LaunchedEffect(userId) { // ✅ Restarts when userId changes, while this Composable stays in composition
  repository.loadUser(userId)
    .onSuccess { state.value = it }
    .onFailure { showError(it) }
}
```

**LaunchedEffect + `Flow`:**
```kotlin
LaunchedEffect(Unit) { // ✅ Runs once for this Composable instance while it remains in the composition
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
  onDispose { // ✅ Mandatory cleanup when leaving composition or when lifecycleOwner changes
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
  onDispose { sensorManager.unregisterListener(listener) } // ✅ Guaranteed cleanup when Composable is disposed
}
```

### API Selection

| API | When to use |
|-----|-------------|
| **LaunchedEffect** | Suspend operations, Flows, API calls, timers tied to the lifecycle of a specific Composable instance |
| **DisposableEffect** | Listeners, observers, native resources, lifecycle callbacks that require deterministic deregistration on Composable disposal |
| **rememberCoroutineScope** | Event-driven coroutines (clicks, swipes) started from callbacks rather than from composition itself |
| **SideEffect** | Sync external non-suspend state after a successful recomposition, without launching coroutines |

### Common Pitfalls

❌ **Unstable keys:**
```kotlin
LaunchedEffect(callback) { // ❌ Restarts on every recomposition if callback is unstable
  callback()
}
```

✅ **Stable keys:**
```kotlin
val stableCallback = rememberUpdatedState(callback)
LaunchedEffect(Unit) { // ✅ Once for this Composable instance
  stableCallback.value()
}
```

❌ **Missing cleanup:**
```kotlin
DisposableEffect(Unit) {
  player.start() // ❌ Potential resource leak: player won't be stopped
  // No onDispose!
}
```

---

## Follow-ups

- How does `rememberUpdatedState` prevent unnecessary effect restarts?
- When should effects live in `ViewModel` versus Composable?
- How to test side effects for proper cleanup and leak prevention?
- What is the difference between `SideEffect` and `LaunchedEffect`?
- How do effect keys interact with recomposition and smart recomposition?

## References

- [[c-coroutines]]
- "https://developer.android.com/jetpack/compose/side-effects"
- "https://developer.android.com/jetpack/compose/lifecycle"
- "https://developer.android.com/jetpack/compose/mental-model"

## Related Questions

### Prerequisites (Easier)
- [[q-android-jetpack-overview--android--easy]]
- [[q-compose-remember-derived-state--android--medium]]

### Related (Same Level)
- [[q-compose-performance-optimization--android--hard]]
