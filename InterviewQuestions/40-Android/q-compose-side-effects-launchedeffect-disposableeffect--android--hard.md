---
id: 20251017-145045
title: Compose Side Effects: LaunchedEffect vs DisposableEffect / Побочные эффекты Compose: LaunchedEffect vs DisposableEffect
aliases:
  - Compose LaunchedEffect vs DisposableEffect
  - Compose Side Effects
  - Побочные эффекты Compose
topic: android
subtopics:
  - ui-compose
  - ui-state
question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-compose-side-effects-advanced--android--hard
  - q-compose-performance-optimization--android--hard
  - q-compose-remember-derived-state--android--medium
created: 2025-10-13
updated: 2025-10-20
tags:
  - android/ui-compose
  - android/ui-state
  - compose
  - side-effects
  - launched-effect
  - disposable-effect
  - difficulty/hard
source: https://developer.android.com/jetpack/compose/side-effects
source_note: Official Compose side-effects docs
---
# Вопрос (RU)
> В чем разница между побочными эффектами Compose: LaunchedEffect vs DisposableEffect?

# Question (EN)
> What is the difference between compose side effects: launchedeffect vs disposableeffect?

---

## Ответ (RU)

LaunchedEffect и DisposableEffect - основные API для побочных эффектов в Compose. LaunchedEffect запускает корутины, DisposableEffect управляет ресурсами с cleanup.

### Различия

**LaunchedEffect:**
- Запускает корутину при composition
- Автоматически отменяется при изменении ключей
- Используется для suspend-функций и Flow

**DisposableEffect:**
- Регистрирует внешние ресурсы (слушатели, обсерверы)
- Требует cleanup в onDispose
- Используется для lifecycle-aware ресурсов

### Когда использовать

- **LaunchedEffect**: для асинхронных операций, которые должны перезапускаться при изменении ключей
- **DisposableEffect**: для ресурсов, требующих явной очистки (сенсоры, ресиверы, плейеры)

## Answer (EN)

### Quick comparison
- LaunchedEffect: start coroutine work tied to composition; auto‑cancels on key change or dispose.
- DisposableEffect: register external resources (listeners, observers); must clean up in onDispose.
- Both leverage [[c-coroutines]] for managing asynchronous operations and lifecycle.

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

---

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

