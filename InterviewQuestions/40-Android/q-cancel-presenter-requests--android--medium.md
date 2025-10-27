---
id: 20251012-122792
title: Cancel Presenter Requests / Отмена запросов презентера
aliases: ["Cancel Presenter Requests", "Отмена запросов презентера"]
topic: android
subtopics: [architecture-clean, coroutines, lifecycle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-activity-lifecycle-methods--android--medium, q-android-testing-strategies--android--medium, q-async-operations-android--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-27
tags: [android/architecture-clean, android/coroutines, android/lifecycle, difficulty/medium]
---

# Вопрос (RU)
> Как корректно отменять асинхронные запросы в Presenter при изменении состояния жизненного цикла View?

# Question (EN)
> How to properly cancel async requests in a Presenter when View lifecycle changes?

---

## Ответ (RU)

### Цели
- Предотвратить обновление UI после уничтожения или паузы View
- Избежать утечек памяти и напрасной работы
- Централизованно управлять отменой при событиях жизненного цикла

### Стратегии отмены

**Владение:** Presenter владеет механизмом отмены (Job/CompositeDisposable), очищает его в `onStop`/`onDestroy`.

**Осведомлённость о жизненном цикле:** Наблюдать за lifecycle для старта/остановки работы, избегать жёстких ссылок на View.

**Единая точка управления:** Все асинхронные операции регистрируются через механизм отмены.

### Реализации

**Coroutines (предпочтительно):**
```kotlin
class UserPresenter {
  private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)

  fun loadUser() {
    scope.launch { // ✅ Bound to presenter scope
      val user = userRepo.fetch()
      view?.displayUser(user)
    }
  }

  fun onStop() {
    scope.coroutineContext.cancelChildren() // ✅ Cancel pending work
  }

  fun onDestroy() {
    scope.cancel() // ✅ Clean up scope completely
  }
}
```

**RxJava:**
```kotlin
class UserPresenter {
  private val disposables = CompositeDisposable()

  fun loadUser() {
    userRepo.getUser()
      .subscribe({ view?.displayUser(it) }, { view?.showError(it) })
      .also { disposables.add(it) } // ✅ Track subscription
  }

  fun onStop() { disposables.clear() } // ✅ Cancel in-flight
  fun onDestroy() { disposables.dispose() }
}
```

### Лучшие практики
- Null-проверка View перед обновлением или использование no-op proxy при detach
- Использовать `Main.immediate` для избежания устаревших событий
- Разделять `onStop` (отмена задач) и `onDestroy` (полная очистка)
- В тестах проверять отсутствие событий после detach

## Answer (EN)

### Goals
- Prevent UI updates after View is destroyed or paused
- Avoid memory leaks and wasted work
- Centralize cancellation on lifecycle events

### Cancellation Strategies

**Ownership:** Presenter owns a cancellation handle (Job/CompositeDisposable), clears it on `onStop`/`onDestroy`.

**Lifecycle-awareness:** Observe lifecycle to start/stop work, avoid hard references to View.

**Single source of truth:** All async operations register with the cancellation handle.

### Implementations

**Coroutines (preferred):**
```kotlin
class UserPresenter {
  private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)

  fun loadUser() {
    scope.launch { // ✅ Bound to presenter scope
      val user = userRepo.fetch()
      view?.displayUser(user)
    }
  }

  fun onStop() {
    scope.coroutineContext.cancelChildren() // ✅ Cancel pending work
  }

  fun onDestroy() {
    scope.cancel() // ✅ Clean up scope completely
  }
}
```

**RxJava:**
```kotlin
class UserPresenter {
  private val disposables = CompositeDisposable()

  fun loadUser() {
    userRepo.getUser()
      .subscribe({ view?.displayUser(it) }, { view?.showError(it) })
      .also { disposables.add(it) } // ✅ Track subscription
  }

  fun onStop() { disposables.clear() } // ✅ Cancel in-flight
  fun onDestroy() { disposables.dispose() }
}
```

### Best Practices
- Null-check View before updates or use no-op proxy when detached
- Use `Main.immediate` to avoid stale events
- Separate `onStop` (cancel tasks) from `onDestroy` (full cleanup)
- In tests, assert no emissions after detach

## Follow-ups
- How to scope Presenter lifecycle using DI frameworks (Hilt/Koin)?
- What are trade-offs between coroutines and RxJava for cancellation?
- How to test that requests are properly cancelled in unit tests?
- When to use `cancelChildren()` vs `cancel()` on scope?

## References
- [[c-coroutines]]
- [[c-lifecycle]]
- https://developer.android.com/kotlin/coroutines
- https://reactivex.io/documentation/disposable.html

## Related Questions

### Prerequisites
- [[q-activity-lifecycle-methods--android--medium]] - Understanding lifecycle events
- Basic knowledge of MVP pattern and async operations

### Related
- [[q-async-operations-android--android--medium]] - General async patterns in Android
- [[q-android-testing-strategies--android--medium]] - Testing async behavior

### Advanced
- Implementing lifecycle-aware components with Architecture Components
- Memory leak detection and prevention in long-running operations
