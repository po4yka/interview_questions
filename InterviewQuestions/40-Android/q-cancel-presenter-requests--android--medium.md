---
id: 20251012-122792
title: Cancel Presenter Requests / Отмена запросов презентера
aliases:
- Cancel Presenter Requests
- Отмена запросов презентера
topic: android
subtopics:
- architecture-mvp
- lifecycle
- coroutines
question_kind: android
difficulty: medium
status: reviewed
moc: moc-android
related:
- q-activity-lifecycle-methods--android--medium
- q-android-async-operations-android--android--medium
- q-android-testing-strategies--android--medium
created: 2025-10-15
updated: 2025-10-20
original_language: en
language_tags:
- en
- ru
tags:
- android/architecture-mvp
- android/lifecycle
- coroutines
- rxjava
- cancellation
- difficulty/medium
- android/coroutines
---# Вопрос (RU)
> Какие механизмы презентер может использовать для отмены выполняемой работы и предотвращения обновления уничтоженного View?

---

# Question (EN)
> What mechanisms can a Presenter use to cancel in-flight work and avoid updating a dead View?

## Ответ (RU)

### Цели
- Не обновлять UI после уничтожения/паузы View
- Избежать утечек и лишней работы
- Централизовать отмену по событиям жизненного цикла

### Базовые стратегии (сначала теория)
- **Владение**: Презентер владеет дескриптором отмены (Job/CompositeDisposable) и очищает его в `onStop/onDestroy`.
- **Осведомлён о жизненном цикле**: Реагирует на lifecycle; не держит жёсткую ссылку на View без проверок.
- **Единая точка учета**: Вся асинхронщина регистрируется в дескрипторе отмены.

### Минимальные реализации

- Coroutines (предпочтительно):
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
  fun onStop() { bag.clear() } // отмена текущих, сохраняем bag
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

### Рекомендации
- Проверяйте/ослабляйте ссылку на View перед рендером; лучше: интерфейс-«заглушка» после detach.
- Используйте main‑safe диспетчер (Main.immediate), чтобы не рендерить устаревшие post’ы.
- Разделяйте `onStop` (cancel children) и `onDestroy` (cancel scope) для переиспользования при resume.
- В тестах утверждайте отсутствие эмиссий после detach.

---

## Answer (EN)

### Goals
- Avoid UI updates after View is destroyed/paused
- Prevent leaks and wasted work
- Centralize cancellation on lifecycle events

### Core strategies (theory first)
- **Ownership**: Presenter owns a cancellation handle (Job/CompositeDisposable) and clears it on `onStop/onDestroy`.
- **Lifecycle-aware**: Observe lifecycle to start/stop work; never hold hard reference to View without checks.
- **One source of truth**: All async work must register with the cancellation handle.

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

