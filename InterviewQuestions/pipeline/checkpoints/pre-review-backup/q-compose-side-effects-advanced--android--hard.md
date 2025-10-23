---
id: 20251017-104815
title: Compose Side Effects (Advanced) / Побочные эффекты Compose (продвинуто)
aliases:
- Compose Side Effects Advanced
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
status: reviewed
moc: moc-android
related:
- q-compose-performance-optimization--android--hard
- q-compose-compiler-plugin--android--hard
- q-compose-remember-derived-state--android--medium
created: 2025-10-15
updated: 2025-10-20
tags:
- android/ui-compose
- android/ui-state
- difficulty/hard
source: https://developer.android.com/jetpack/compose/side-effects
source_note: Official Compose side‑effects docs
---

# Вопрос (RU)
> Побочные эффекты Compose (продвинуто)?

# Question (EN)
> Compose Side Effects (Advanced)?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### What each API does
- LaunchedEffect: run coroutine side‑effects tied to composition; cancels on key change/dispose.
- DisposableEffect: register external resources; must clean up in onDispose on key change/dispose.
- SideEffect: sync Compose state to non‑Compose after every successful recomposition; no cleanup.
- produceState: convert async work/Flow into `State<T>`; coroutine auto‑cancelled on dispose.
- Relies on [[c-coroutines]] for async operations and lifecycle management.

### Minimal patterns

LaunchedEffect (async work with keys)
```kotlin
LaunchedEffect(userId) { /* cancels previous on userId change */
  try { vm.load(userId) } finally { /* update UI flags */ }
}
```

DisposableEffect (listener lifecycle)
```kotlin
DisposableEffect(sensorType) {
  val mgr = context.getSystemService<SensorManager>()
  val listener = object: SensorEventListener { /* update state */ }
  mgr?.registerListener(listener, mgr.getDefaultSensor(sensorType), SensorManager.SENSOR_DELAY_NORMAL)
  onDispose { mgr?.unregisterListener(listener) }
}
```

SideEffect (publish state out)
```kotlin
SideEffect { analytics.logScreen(screenName) } // runs after every recomposition
```

produceState (async→State)
```kotlin
val image by produceState<ImageBitmap?>(initialValue = null, key1 = url) {
  value = loader.load(url) // cancelled on dispose/key change
}
```

### Choosing the right API
- Need coroutine? use LaunchedEffect; converting to State? use produceState.
- No coroutine: need cleanup? DisposableEffect; just sync state? SideEffect.
- Use correct keys to control restart semantics; avoid heavy work in SideEffect.

### Common pitfalls
- Missing onDispose → leaks listeners; wrong keys → unnecessary restarts; heavy logic in SideEffect.
- For callbacks that change but shouldn’t restart effect, wrap with `rememberUpdatedState`.

## Follow-ups
- How to combine multiple side‑effects safely in one composable?
- When to move effects into ViewModel vs keep in UI?
- Patterns for lifecycle‑aware Flow collection without leaks?

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
- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-slot-table-recomposition--android--hard]]
