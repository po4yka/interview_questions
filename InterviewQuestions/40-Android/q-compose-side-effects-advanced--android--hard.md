---
id: 20251017-104815
title: Compose Side Effects (Advanced) / Побочные эффекты Compose (продвинуто)
aliases: ["Compose Side Effects Advanced", "Побочные эффекты Compose"]
topic: android
subtopics: [ui-compose, ui-state]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - q-compose-compiler-plugin--android--hard
  - q-compose-performance-optimization--android--hard
  - q-compose-remember-derived-state--android--medium
created: 2025-10-15
updated: 2025-10-27
tags: [android/ui-compose, android/ui-state, difficulty/hard]
sources: ["https://developer.android.com/jetpack/compose/side-effects"]
---
# Вопрос (RU)
> Как выбирать и правильно использовать API побочных эффектов Compose (LaunchedEffect, DisposableEffect, SideEffect, produceState)?

# Question (EN)
> How to choose and correctly use Compose side-effect APIs (LaunchedEffect, DisposableEffect, SideEffect, produceState)?

---

## Ответ (RU)

**Четыре API для различных сценариев**:

1. **LaunchedEffect** — запускает корутину, привязанную к композиции; отменяется при изменении ключа или выходе из композиции
2. **DisposableEffect** — регистрирует внешние ресурсы (слушатели, подписки); требует `onDispose` для очистки
3. **SideEffect** — синхронизирует состояние Compose с внешними системами после каждой успешной рекомпозиции; без очистки
4. **produceState** — конвертирует асинхронную работу (Flow, suspend функции) в `State<T>`; корутина автоматически отменяется

**Выбор API**:
- Нужна корутина → `LaunchedEffect`; конвертация в State → `produceState`
- Без корутины: нужна очистка → `DisposableEffect`; только синхронизация → `SideEffect`

**Ключи (keys)**: контролируют перезапуск эффекта. Изменение ключа отменяет текущий эффект и запускает новый.

**Примеры**:

```kotlin
// ✅ LaunchedEffect: асинхронная загрузка с отменой
LaunchedEffect(userId) {
  try {
    viewModel.loadUser(userId)
  } finally {
    // Гарантированно выполнится при отмене
  }
}

// ✅ DisposableEffect: регистрация слушателя с очисткой
DisposableEffect(sensorType) {
  val manager = context.getSystemService<SensorManager>()
  val listener = object : SensorEventListener { /* ... */ }
  manager?.registerListener(listener, /* ... */)
  onDispose {
    manager?.unregisterListener(listener) // ✅ Обязательная очистка
  }
}

// ✅ SideEffect: публикация в аналитику (без ключей)
SideEffect {
  analytics.logScreen(currentScreen) // Вызывается после каждой рекомпозиции
}

// ✅ produceState: асинхронная загрузка → State
val imageState by produceState<ImageBitmap?>(null, url) {
  value = imageLoader.load(url) // Автоматическая отмена
}
```

**Типичные ошибки**:
- ❌ Отсутствие `onDispose` → утечки ресурсов
- ❌ Неправильные ключи → лишние перезапуски или их отсутствие
- ❌ Тяжёлая логика в `SideEffect` → проблемы с производительностью
- ✅ Для меняющихся callback без перезапуска эффекта: `rememberUpdatedState`

## Answer (EN)

**Four APIs for different scenarios**:

1. **LaunchedEffect** — launches a coroutine tied to composition; cancels on key change or composition exit
2. **DisposableEffect** — registers external resources (listeners, subscriptions); requires `onDispose` for cleanup
3. **SideEffect** — synchronizes Compose state to external systems after every successful recomposition; no cleanup
4. **produceState** — converts async work (Flow, suspend functions) to `State<T>`; coroutine auto-cancels

**Choosing the API**:
- Need coroutine → `LaunchedEffect`; converting to State → `produceState`
- No coroutine: need cleanup → `DisposableEffect`; just sync → `SideEffect`

**Keys**: control effect restart semantics. Key change cancels current effect and starts new one.

**Examples**:

```kotlin
// ✅ LaunchedEffect: async loading with cancellation
LaunchedEffect(userId) {
  try {
    viewModel.loadUser(userId)
  } finally {
    // Guaranteed to run on cancellation
  }
}

// ✅ DisposableEffect: listener registration with cleanup
DisposableEffect(sensorType) {
  val manager = context.getSystemService<SensorManager>()
  val listener = object : SensorEventListener { /* ... */ }
  manager?.registerListener(listener, /* ... */)
  onDispose {
    manager?.unregisterListener(listener) // ✅ Mandatory cleanup
  }
}

// ✅ SideEffect: analytics publishing (no keys)
SideEffect {
  analytics.logScreen(currentScreen) // Called after every recomposition
}

// ✅ produceState: async load → State
val imageState by produceState<ImageBitmap?>(null, url) {
  value = imageLoader.load(url) // Auto-cancelled
}
```

**Common pitfalls**:
- ❌ Missing `onDispose` → resource leaks
- ❌ Wrong keys → unnecessary restarts or missing restarts
- ❌ Heavy logic in `SideEffect` → performance issues
- ✅ For changing callbacks without restarting effect: `rememberUpdatedState`

## Follow-ups
- How to combine multiple side-effects safely in one composable?
- When to move effects into ViewModel vs keep in UI layer?
- How to collect Flow lifecycle-aware without leaks using `collectAsStateWithLifecycle`?
- What's the difference between `LaunchedEffect` and `rememberCoroutineScope`?
- How does `rememberUpdatedState` prevent unnecessary effect restarts?

## References
- [[c-coroutines]] — coroutine fundamentals
- https://developer.android.com/jetpack/compose/side-effects
- https://developer.android.com/jetpack/compose/lifecycle

## Related Questions

### Prerequisites
- [[q-compose-remember-derived-state--android--medium]] — understanding state management basics
- [[q-android-jetpack-overview--android--easy]] — Compose fundamentals

### Related
- [[q-compose-performance-optimization--android--hard]] — avoiding unnecessary recompositions
- [[q-compose-compiler-plugin--android--hard]] — how Compose tracks effects

### Advanced
- [[q-compose-slot-table-recomposition--android--hard]] — internal composition mechanics
