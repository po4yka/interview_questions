---
id: android-254
title: Compose Side Effects (Advanced) / Побочные эффекты Compose (продвинуто)
aliases: ["Compose Side Effects Advanced", "Побочные эффекты Compose"]
topic: android
subtopics: [ui-compose, ui-state, lifecycle]
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
  - q-compose-recomposition-lifecycle--android--medium
created: 2025-10-15
updated: 2025-10-30
tags: [android/ui-compose, android/ui-state, android/lifecycle, difficulty/hard]
sources: ["https://developer.android.com/jetpack/compose/side-effects"]
date created: Thursday, October 30th 2025, 11:23:25 am
date modified: Thursday, October 30th 2025, 12:43:50 pm
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

**Матрица выбора**:

| Сценарий | API | Причина |
|----------|-----|---------|
| Асинхронная загрузка данных | `LaunchedEffect` | Нужна корутина с отменой |
| Flow → State | `produceState` | Автоматическая конвертация |
| Регистрация слушателей | `DisposableEffect` | Нужна очистка ресурсов |
| Публикация в аналитику | `SideEffect` | Синхронизация без очистки |

**Ключи (keys)**: контролируют перезапуск эффекта. Изменение ключа отменяет текущий эффект и запускает новый.

**Примеры**:

```kotlin
// ✅ LaunchedEffect: асинхронная загрузка с отменой
LaunchedEffect(userId) {
  try {
    viewModel.loadUser(userId)
  } finally {
    // ✅ Гарантированно выполнится при отмене
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

// ✅ produceState: Flow → State
val imageState by produceState<ImageBitmap?>(null, url) {
  imageLoader.load(url).collect { value = it } // Автоматическая отмена
}

// ❌ WRONG: тяжёлая синхронная работа в SideEffect
SideEffect {
  processLargeDataset() // Блокирует рекомпозицию
}
```

**Типичные ошибки**:
- ❌ Отсутствие `onDispose` → утечки ресурсов
- ❌ Неправильные ключи → лишние перезапуски или их отсутствие
- ❌ Тяжёлая логика в `SideEffect` → блокировка рекомпозиции
- ✅ Для меняющихся callback без перезапуска эффекта: `rememberUpdatedState`

**Продвинутые паттерны**:

```kotlin
// ✅ rememberUpdatedState для callback без перезапуска
@Composable
fun Timer(onTimeout: () -> Unit) {
  val currentCallback by rememberUpdatedState(onTimeout)
  LaunchedEffect(Unit) { // ✅ Единожды
    delay(5000)
    currentCallback() // ✅ Всегда актуальный callback
  }
}

// ✅ Комбинация эффектов для lifecycle-aware работы
DisposableEffect(lifecycleOwner) {
  val observer = LifecycleEventObserver { _, event ->
    if (event == Lifecycle.Event.ON_RESUME) {
      // Запуск при resume
    }
  }
  lifecycleOwner.lifecycle.addObserver(observer)
  onDispose {
    lifecycleOwner.lifecycle.removeObserver(observer)
  }
}
```

## Answer (EN)

**Four APIs for different scenarios**:

1. **LaunchedEffect** — launches a coroutine tied to composition; cancels on key change or composition exit
2. **DisposableEffect** — registers external resources (listeners, subscriptions); requires `onDispose` for cleanup
3. **SideEffect** — synchronizes Compose state to external systems after every successful recomposition; no cleanup
4. **produceState** — converts async work (Flow, suspend functions) to `State<T>`; coroutine auto-cancels

**Selection matrix**:

| Scenario | API | Reason |
|----------|-----|--------|
| Async data loading | `LaunchedEffect` | Need coroutine with cancellation |
| Flow → State | `produceState` | Automatic conversion |
| Register listeners | `DisposableEffect` | Need resource cleanup |
| Analytics publishing | `SideEffect` | Sync without cleanup |

**Keys**: control effect restart semantics. Key change cancels current effect and starts new one.

**Examples**:

```kotlin
// ✅ LaunchedEffect: async loading with cancellation
LaunchedEffect(userId) {
  try {
    viewModel.loadUser(userId)
  } finally {
    // ✅ Guaranteed to run on cancellation
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

// ✅ produceState: Flow → State
val imageState by produceState<ImageBitmap?>(null, url) {
  imageLoader.load(url).collect { value = it } // Auto-cancelled
}

// ❌ WRONG: heavy sync work in SideEffect
SideEffect {
  processLargeDataset() // Blocks recomposition
}
```

**Common pitfalls**:
- ❌ Missing `onDispose` → resource leaks
- ❌ Wrong keys → unnecessary restarts or missing restarts
- ❌ Heavy logic in `SideEffect` → blocks recomposition thread
- ✅ For changing callbacks without restarting effect: `rememberUpdatedState`

**Advanced patterns**:

```kotlin
// ✅ rememberUpdatedState for callback without restart
@Composable
fun Timer(onTimeout: () -> Unit) {
  val currentCallback by rememberUpdatedState(onTimeout)
  LaunchedEffect(Unit) { // ✅ Once only
    delay(5000)
    currentCallback() // ✅ Always current callback
  }
}

// ✅ Combining effects for lifecycle-aware work
DisposableEffect(lifecycleOwner) {
  val observer = LifecycleEventObserver { _, event ->
    if (event == Lifecycle.Event.ON_RESUME) {
      // Start on resume
    }
  }
  lifecycleOwner.lifecycle.addObserver(observer)
  onDispose {
    lifecycleOwner.lifecycle.removeObserver(observer)
  }
}
```

## Follow-ups
- How to combine multiple side-effects safely in one composable?
- When to move effects into ViewModel vs keep in UI layer?
- How does `rememberUpdatedState` prevent unnecessary effect restarts?
- What's the difference between `LaunchedEffect` and `rememberCoroutineScope`?
- How to test composables with side effects?

## References
- [[c-coroutines]] — coroutine fundamentals
- [[c-compose-lifecycle]] — Compose lifecycle and recomposition
- [[c-structured-concurrency]] — cancellation and cleanup patterns
- https://developer.android.com/jetpack/compose/side-effects
- https://developer.android.com/jetpack/compose/lifecycle

## Related Questions

### Prerequisites
- [[q-compose-remember-derived-state--android--medium]] — understanding state management basics
- [[q-android-jetpack-overview--android--easy]] — Compose fundamentals
- [[q-coroutine-basics--kotlin--easy]] — coroutine concepts

### Related
- [[q-compose-performance-optimization--android--hard]] — avoiding unnecessary recompositions
- [[q-compose-compiler-plugin--android--hard]] — how Compose tracks effects
- [[q-compose-recomposition-lifecycle--android--medium]] — recomposition mechanics

### Advanced
- [[q-compose-slot-table-recomposition--android--hard]] — internal composition mechanics
- [[q-compose-stability-optimization--android--hard]] — stability inference and optimization
