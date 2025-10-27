---
id: 20251017-145045
title: "Compose Side Effects: LaunchedEffect vs DisposableEffect / Побочные эффекты Compose: LaunchedEffect vs DisposableEffect"
aliases: [Compose LaunchedEffect vs DisposableEffect, Compose Side Effects, Побочные эффекты Compose]
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
  - q-compose-performance-optimization--android--hard
  - q-compose-remember-derived-state--android--medium
  - q-compose-side-effects-advanced--android--hard
created: 2025-10-13
updated: 2025-10-27
tags: [android/ui-compose, android/ui-state, compose, difficulty/hard, disposable-effect, launched-effect, side-effects]
sources: [https://developer.android.com/jetpack/compose/side-effects, https://developer.android.com/jetpack/compose/lifecycle]
---
# Вопрос (RU)
> В чем разница между побочными эффектами Compose: LaunchedEffect vs DisposableEffect?

# Question (EN)
> What is the difference between compose side effects: launchedeffect vs disposableeffect?

---

## Ответ (RU)

### Основные Различия

**LaunchedEffect**
- Запускает корутину, привязанную к композиции
- Автоматически отменяется при изменении ключей или выходе из композиции
- Применяется для suspend-функций, Flow, асинхронных операций

**DisposableEffect**
- Регистрирует внешние ресурсы (слушатели, обсерверы)
- Требует явного cleanup через `onDispose`
- Применяется для lifecycle-aware ресурсов

### Примеры

LaunchedEffect с ключами:
```kotlin
LaunchedEffect(userId) { // ✅ Корутина перезапустится при изменении userId
  runCatching { viewModel.loadUser(userId) }
    .onFailure { showError(it) }
}
```

LaunchedEffect + Flow:
```kotlin
LaunchedEffect(orderId) { // ✅ Отменяется при dispose
  repository.observeOrder(orderId)
    .collect { state -> viewModel.update(state) }
}
```

DisposableEffect для сенсоров:
```kotlin
DisposableEffect(sensorType) {
  val manager = context.getSystemService<SensorManager>()
  val listener = object : SensorEventListener {
    override fun onSensorChanged(event: SensorEvent) { /* обновление */ }
    override fun onAccuracyChanged(sensor: Sensor, accuracy: Int) {}
  }
  manager?.registerListener(listener, manager.getDefaultSensor(sensorType), SENSOR_DELAY_NORMAL)
  onDispose { manager?.unregisterListener(listener) } // ✅ Обязательная очистка
}
```

### Выбор API

- **LaunchedEffect** — асинхронная работа, перезапускающаяся при изменении ключей
- **DisposableEffect** — ресурсы с явной очисткой (сенсоры, ресиверы, плееры)
- **rememberCoroutineScope** — event-driven корутины (клики, жесты)
- **SideEffect** — синхронизация после recomposition (без тяжелой работы)

### Распространенные Ошибки

- Неверные ключи → избыточные перезапуски
- Отсутствие `onDispose` → утечки ресурсов
- Изменение callback → ненужные рестарты: используйте `rememberUpdatedState`

## Answer (EN)

### Core Differences

**LaunchedEffect**
- Launches coroutine tied to composition lifecycle
- Auto-cancels on key change or composition exit
- For suspend functions, Flow, async operations

**DisposableEffect**
- Registers external resources (listeners, observers)
- Requires explicit cleanup via `onDispose`
- For lifecycle-aware resources

### Examples

LaunchedEffect with keys:
```kotlin
LaunchedEffect(userId) { // ✅ Restarts when userId changes
  runCatching { viewModel.loadUser(userId) }
    .onFailure { showError(it) }
}
```

LaunchedEffect + Flow:
```kotlin
LaunchedEffect(orderId) { // ✅ Cancels on dispose
  repository.observeOrder(orderId)
    .collect { state -> viewModel.update(state) }
}
```

DisposableEffect for sensors:
```kotlin
DisposableEffect(sensorType) {
  val manager = context.getSystemService<SensorManager>()
  val listener = object : SensorEventListener {
    override fun onSensorChanged(event: SensorEvent) { /* update */ }
    override fun onAccuracyChanged(sensor: Sensor, accuracy: Int) {}
  }
  manager?.registerListener(listener, manager.getDefaultSensor(sensorType), SENSOR_DELAY_NORMAL)
  onDispose { manager?.unregisterListener(listener) } // ✅ Mandatory cleanup
}
```

### API Selection

- **LaunchedEffect** — async work restarting on key changes
- **DisposableEffect** — resources requiring explicit cleanup (sensors, receivers, players)
- **rememberCoroutineScope** — event-driven coroutines (clicks, gestures)
- **SideEffect** — syncing state post-recomposition (no heavy work)

### Common Pitfalls

- Wrong keys → unnecessary restarts
- Missing `onDispose` → resource leaks
- Callback changes → unwanted restarts: use `rememberUpdatedState`

---

## Follow-ups

- How does `rememberUpdatedState` prevent unnecessary effect restarts?
- When should side effects live in ViewModel versus composable?
- How to test effects for proper cleanup and leak prevention?
- What's the difference between `SideEffect` and `LaunchedEffect`?

## References

- [[c-coroutines]]
- https://developer.android.com/jetpack/compose/side-effects
- https://developer.android.com/jetpack/compose/lifecycle

## Related Questions

### Prerequisites
- [[q-android-jetpack-overview--android--easy]]
- [[q-compose-remember-derived-state--android--medium]]

### Related
- [[q-compose-performance-optimization--android--hard]]

### Advanced
- [[q-compose-side-effects-advanced--android--hard]]
