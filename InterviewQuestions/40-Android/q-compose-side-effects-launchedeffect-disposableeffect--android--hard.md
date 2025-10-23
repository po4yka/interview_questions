---
id: 20251017-145045
title: 'Compose Side Effects: LaunchedEffect vs DisposableEffect / Побочные эффекты:
  LaunchedEffect vs DisposableEffect'
aliases:
- Compose LaunchedEffect vs DisposableEffect
topic: android
subtopics:
- ui-compose
- side-effects
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
source: https://developer.android.com/jetpack/compose/side-effects
source_note: Official Compose side‑effects docs
status: reviewed
moc: moc-android
related:
- q-compose-side-effects-advanced--jetpack-compose--hard
- q-compose-performance-optimization--android--hard
- q-compose-remember-derived-state--jetpack-compose--medium
created: 2025-10-13
updated: 2025-10-20
tags:
- android/ui-compose
- compose/side-effects
- coroutines
- lifecycle
- difficulty/hard
- android/side-effects
---# Вопрос (RU)
> В чём разница между `LaunchedEffect` и `DisposableEffect` в Compose? Когда использовать каждый? Приведите минимальные паттерны.

---

# Question (EN)
> What is the difference between `LaunchedEffect` and `DisposableEffect` in Compose? When should each be used? Show minimal patterns.

## Ответ (RU)

### Краткое сравнение
- LaunchedEffect: запуск корутин с привязкой к composition; авто‑отмена при смене ключей/удалении.
- DisposableEffect: регистрация внешних ресурсов (listener/observer); обязательная очистка в onDispose.

### Минимальные паттерны

LaunchedEffect (async по ключам)
```kotlin
LaunchedEffect(userId) { // отменит предыдущую при смене userId
  runCatching { vm.load(userId) }.onFailure { /* обработка */ }
}
```

LaunchedEffect + Flow
```kotlin
LaunchedEffect(orderId) {
  repo.observeOrder(orderId).collect { state -> vm.update(state) }
}
```

DisposableEffect (жизненный цикл listener)
```kotlin
DisposableEffect(sensorType) {
  val mgr = context.getSystemService<SensorManager>()
  val listener = object: SensorEventListener { override fun onSensorChanged(e: SensorEvent){ /* state */ } }
  mgr?.registerListener(listener, mgr?.getDefaultSensor(sensorType), SensorManager.SENSOR_DELAY_NORMAL)
  onDispose { mgr?.unregisterListener(listener) }
}
```

DisposableEffect (наблюдатель lifecycle)
```kotlin
DisposableEffect(lifecycleOwner) {
  val observer = LifecycleEventObserver { _, e -> if (e==ON_START) start(); if (e==ON_STOP) stop() }
  lifecycleOwner.lifecycle.addObserver(observer)
  onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
}
```

### Как выбирать
- LaunchedEffect для suspend/Flow, требующих рестарт по ключам и отмену при dispose.
- DisposableEffect для ресурсов, требующих явной очистки (сенсоры, приёмники, плееры, обратные вызовы).
- Для событий (onClick) — `rememberCoroutineScope`.
- Для синхронизации после рекомпозиции — `SideEffect` (не для тяжёлой работы).

### Типичные ошибки
- Неверные ключи → лишние перезапуски; нет onDispose → утечки; тяжёлая работа в SideEffect.
- Меняющиеся callbacks перезапускают эффекты: используйте `rememberUpdatedState`, чтобы иметь актуальный колбэк без рестарта эффекта.

---

## Answer (EN)

### Quick comparison
- LaunchedEffect: start coroutine work tied to composition; auto‑cancels on key change or dispose.
- DisposableEffect: register external resources (listeners, observers); must clean up in onDispose.

### Minimal patterns

LaunchedEffect (async by keys)
```kotlin
LaunchedEffect(userId) { // cancels previous when userId changes
  runCatching { vm.load(userId) }.onFailure { /* handle */ }
}
```

LaunchedEffect + Flow
```kotlin
LaunchedEffect(orderId) {
  repo.observeOrder(orderId).collect { state -> vm.update(state) }
}
```

DisposableEffect (listener lifecycle)
```kotlin
DisposableEffect(sensorType) {
  val mgr = context.getSystemService<SensorManager>()
  val listener = object: SensorEventListener { override fun onSensorChanged(e: SensorEvent){ /* state */ } }
  mgr?.registerListener(listener, mgr?.getDefaultSensor(sensorType), SensorManager.SENSOR_DELAY_NORMAL)
  onDispose { mgr?.unregisterListener(listener) }
}
```

DisposableEffect (lifecycle observer)
```kotlin
DisposableEffect(lifecycleOwner) {
  val observer = LifecycleEventObserver { _, e -> if (e==ON_START) start(); if (e==ON_STOP) stop() }
  lifecycleOwner.lifecycle.addObserver(observer)
  onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
}
```

### Choosing the right one
- Use LaunchedEffect for suspend/Flow work that should restart on key changes and cancel on dispose.
- Use DisposableEffect for resources needing explicit cleanup (sensors, receivers, players, callbacks).
- For event‑driven coroutines (clicks) use `rememberCoroutineScope` instead.
- For syncing state after recomposition, use `SideEffect` (not for heavy work).

### Common pitfalls
- Wrong keys → unnecessary restarts; missing onDispose → leaks; heavy work in SideEffect.
- Changing callbacks restarting effects: wrap with `rememberUpdatedState` to keep latest without restart.

## Follow-ups
- How to avoid restarting effects when only callbacks change? (`rememberUpdatedState`)
- When to lift side‑effects into ViewModel vs keep in UI?
- Testing side‑effects: ensuring cleanup and no leaks.

## References
- https://developer.android.com/jetpack/compose/side-effects
- https://developer.android.com/jetpack/compose/lifecycle

## Related Questions

### Prerequisites (Easier)
- [[q-android-jetpack-overview--android--easy]]

### Related (Same Level)
- [[q-compose-remember-derived-state--android--medium]]
- [[q-compose-performance-optimization--android--hard]]

### Advanced (Harder)
- [[q-compose-side-effects-advanced--android--hard]]

