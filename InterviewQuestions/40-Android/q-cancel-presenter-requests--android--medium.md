---
id: android-273
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
related: [c-lifecycle, c-coroutines, q-activity-lifecycle-methods--android--medium, q-async-operations-android--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-29
tags: [android/architecture-clean, android/coroutines, android/lifecycle, mvp, presenter-pattern, difficulty/medium]
date created: Thursday, October 30th 2025, 11:11:14 am
date modified: Thursday, October 30th 2025, 12:43:31 pm
---

# Вопрос (RU)
> Как корректно отменять асинхронные запросы в Presenter при изменении состояния жизненного цикла View?

# Question (EN)
> How to properly cancel async requests in a Presenter when View lifecycle changes?

---

## Ответ (RU)

### Ключевая проблема
Presenter не должен обновлять уничтоженную или detached View — это вызывает утечки памяти и крэши. Решение: привязать отмену запросов к lifecycle событиям View.

### Подход с Coroutines (рекомендуется)

```kotlin
class UserPresenter(private val repo: UserRepository) {
  private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
  private var view: UserView? = null

  fun attach(view: UserView) {
    this.view = view
  }

  fun loadUser(id: String) {
    scope.launch {
      // ✅ Cancellable, bound to presenter scope
      val user = repo.fetchUser(id)
      view?.displayUser(user) // ✅ Null-safe
    }
  }

  fun detach() {
    view = null
    scope.coroutineContext.cancelChildren() // ✅ Cancel pending work
  }

  fun destroy() {
    scope.cancel() // ✅ Clean up scope
  }
}
```

**Почему `Main.immediate`:** избегает race condition, когда событие уже неактуально к моменту диспатча.

### Подход с RxJava

```kotlin
class UserPresenter(private val repo: UserRepository) {
  private val disposables = CompositeDisposable()
  private var view: UserView? = null

  fun loadUser(id: String) {
    repo.getUser(id)
      .subscribeOn(Schedulers.io())
      .observeOn(AndroidSchedulers.mainThread())
      .subscribe(
        { user -> view?.displayUser(user) }, // ✅ Null-safe
        { error -> view?.showError(error) }
      )
      .also { disposables.add(it) } // ✅ Track for disposal
  }

  fun detach() {
    view = null
    disposables.clear() // ❌ Disposes subscriptions
  }
}
```

### Альтернатива: No-op Proxy Pattern

```kotlin
class NoOpUserView : UserView {
  override fun displayUser(user: User) { /* no-op */ }
  override fun showError(error: Throwable) { /* no-op */ }
}

fun detach() {
  view = NoOpUserView() // ✅ Avoids null-checks
  scope.coroutineContext.cancelChildren()
}
```

## Answer (EN)

### Core Problem
A Presenter must not update a destroyed or detached View — this causes memory leaks and crashes. Solution: bind request cancellation to View lifecycle events.

### Coroutines Approach (recommended)

```kotlin
class UserPresenter(private val repo: UserRepository) {
  private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
  private var view: UserView? = null

  fun attach(view: UserView) {
    this.view = view
  }

  fun loadUser(id: String) {
    scope.launch {
      // ✅ Cancellable, bound to presenter scope
      val user = repo.fetchUser(id)
      view?.displayUser(user) // ✅ Null-safe
    }
  }

  fun detach() {
    view = null
    scope.coroutineContext.cancelChildren() // ✅ Cancel pending work
  }

  fun destroy() {
    scope.cancel() // ✅ Clean up scope
  }
}
```

**Why `Main.immediate`:** avoids race conditions where the event is stale by dispatch time.

### RxJava Approach

```kotlin
class UserPresenter(private val repo: UserRepository) {
  private val disposables = CompositeDisposable()
  private var view: UserView? = null

  fun loadUser(id: String) {
    repo.getUser(id)
      .subscribeOn(Schedulers.io())
      .observeOn(AndroidSchedulers.mainThread())
      .subscribe(
        { user -> view?.displayUser(user) }, // ✅ Null-safe
        { error -> view?.showError(error) }
      )
      .also { disposables.add(it) } // ✅ Track for disposal
  }

  fun detach() {
    view = null
    disposables.clear() // ❌ Disposes subscriptions
  }
}
```

### Alternative: No-op Proxy Pattern

```kotlin
class NoOpUserView : UserView {
  override fun displayUser(user: User) { /* no-op */ }
  override fun showError(error: Throwable) { /* no-op */ }
}

fun detach() {
  view = NoOpUserView() // ✅ Avoids null-checks
  scope.coroutineContext.cancelChildren()
}
```

## Follow-ups

1. How do `cancelChildren()` and `cancel()` differ, and when should each be used?
2. What happens if a coroutine is cancelled while performing a suspend call?
3. How would you test that a Presenter correctly cancels requests on `detach()`?
4. Why prefer `Main.immediate` over `Main` dispatcher in Presenters?
5. How can DI frameworks (Hilt, Koin) automate Presenter lifecycle scoping?

## References

- [[c-coroutines]] - Kotlin coroutines fundamentals
- [[c-lifecycle]] - Android component lifecycle
- [[c-mvp-pattern]] - Model-View-Presenter architecture
- https://developer.android.com/kotlin/coroutines/coroutines-best-practices
- https://developer.android.com/topic/architecture/ui-layer

## Related Questions

### Prerequisites
- [[q-activity-lifecycle-methods--android--medium]] - Understanding Activity lifecycle callbacks
- Understanding of MVP pattern and separation of concerns
- Basic coroutine or RxJava knowledge

### Related
- [[q-async-operations-android--android--medium]] - General async handling strategies
- [[q-viewmodel-lifecycle-scope--android--medium]] - Alternative approach with ViewModel
- [[q-memory-leaks-android--android--medium]] - Detecting and preventing memory leaks

### Advanced
- [[q-lifecycle-aware-components--android--hard]] - Building lifecycle-aware observers
- [[q-structured-concurrency-android--android--hard]] - Advanced coroutine cancellation patterns
- Testing cancellation behavior in instrumented tests
