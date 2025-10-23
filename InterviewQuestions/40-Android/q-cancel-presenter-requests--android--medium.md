---
id: 20251012-122792
title: Cancel Presenter Requests / Отмена запросов презентера
aliases:
- Cancel Presenter Requests
- Отмена запросов презентера
topic: android
subtopics:
- architecture-clean
- lifecycle
- coroutines
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-activity-lifecycle-methods--android--medium
- q-async-operations-android--android--medium
- q-android-testing-strategies--android--medium
created: 2025-10-15
updated: 2025-10-20
tags:
- android/architecture-clean
- android/lifecycle
- android/coroutines
- difficulty/medium
---

# Вопрос (RU)
> Отмена запросов презентера?

# Question (EN)
> Cancel Presenter Requests?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Goals
- Avoid UI updates after View is destroyed/paused
- Prevent leaks and wasted work
- Centralize cancellation on lifecycle events

### Core strategies (theory first)
- **Ownership**: Presenter owns a cancellation handle (Job/CompositeDisposable) and clears it on `onStop/onDestroy`.
- **Lifecycle-aware**: Observe [[c-lifecycle]] to start/stop work; never hold hard reference to View without checks.
- **One source of truth**: All async work must register with the cancellation handle using [[c-coroutines]].

### Minimal implementations

- Coroutines (preferred):
```kotlin
class Presenter {
  private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)

  fun load() = scope.launch { view?.show(dataRepo.fetch()) }
  fun onStop() { scope.coroutineContext.cancelChildren() }
  fun onDestroy() { scope.cancel() }
}
```

- RxJava:
```kotlin
class Presenter {
  private val bag = CompositeDisposable()
  fun load() { bag += repo.get().subscribe(view::show, view::error) }
  fun onStop() { bag.clear() } // cancel in-flight, keep bag
  fun onDestroy() { bag.dispose() }
}
```

- Callback/Executor:
```kotlin
class Presenter {
  private var future: Future<*>? = null
  fun load() { future = executor.submit { /* work */ } }
  fun onStop() { future?.cancel(true) }
}
```

### Best practices
- Null-check/weak reference View before rendering; better: pass render via interface that is swapped to a no-op when detached.
- Prefer main-safe dispatch (Main.immediate) to avoid stale posts.
- Split `onStop` (cancel children) vs `onDestroy` (cancel scope) to allow reuse on resume.
- In tests, assert no emissions after detach.

## Follow-ups
- How to model Presenter scope as DI-provided tied to screen lifecycle?
- Coroutines vs Rx cancellation trade-offs in mixed codebases?
- How to verify cancellation in unit/instrumented tests?

## References
- https://developer.android.com/kotlin/coroutines
- https://reactivex.io/documentation/disposable.html

## Related Questions

### Prerequisites (Easier)
- [[q-activity-lifecycle-methods--android--medium]]

### Related (Same Level)
- [[q-android-async-operations-android--android--medium]]
- [[q-android-testing-strategies--android--medium]]

### Advanced (Harder)
- [[q-android-performance-measurement-tools--android--medium]]
