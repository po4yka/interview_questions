---
id: android-273
title: Cancel Presenter Requests / Отмена запросов презентера
aliases:
- Cancel Presenter Requests
- Отмена запросов презентера
topic: android
subtopics:
- architecture-clean
- coroutines
- lifecycle
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android
- c-coroutines
- q-activity-lifecycle-methods--android--medium
- q-inject-router-to-presenter--android--medium
- q-mvvm-pattern--android--medium
- q-presenter-notify-view--android--medium
sources: []
created: 2023-10-15
updated: 2025-11-10
tags:
- android/architecture-clean
- android/coroutines
- android/lifecycle
- difficulty/medium
- mvp
- presenter-pattern
anki_cards:
- slug: android-273-0-en
  language: en
  anki_id: 1768365308475
  synced_at: '2026-01-14T09:17:53.399377'
- slug: android-273-0-ru
  language: ru
  anki_id: 1768365308497
  synced_at: '2026-01-14T09:17:53.401251'
---
# Вопрос (RU)
> Как корректно отменять асинхронные запросы в Presenter при изменении состояния жизненного цикла `View`?

# Question (EN)
> How to properly cancel async requests in a Presenter when `View` lifecycle changes?

---

## Ответ (RU)

### Ключевая Проблема
`Presenter` не должен обновлять уничтоженную или detached `View` — это вызывает утечки памяти и крэши. Решение: привязать отмену запросов к событиям жизненного цикла `View` и корректно управлять областью (scope) асинхронной работы.

### Подход С Coroutines (рекомендуется)

```kotlin
class UserPresenter(private val repo: UserRepository) {
  private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
  private var view: UserView? = null

  fun attach(view: UserView) {
    this.view = view
  }

  fun loadUser(id: String) {
    scope.launch {
      // ✅ Cancellable, bound to presenter scope (при условии, что repo.fetchUser поддерживает отмену)
      val user = repo.fetchUser(id)
      view?.displayUser(user) // ✅ Null-safe
    }
  }

  fun detach() {
    view = null
    scope.coroutineContext.cancelChildren() // ✅ Cancel pending work tied to current view
  }

  fun destroy() {
    scope.cancel() // ✅ Полная очистка scope презентера, используется при уничтожении презентера
  }
}
```

**Почему `Main.immediate`:** если уже на главном потоке, блок запускается немедленно без дополнительной диспатчеризации, что уменьшает задержки и вероятность обработать устаревшее состояние; если не на `Main`, всё равно будет диспатчеризация на главный поток.

Важно: `repo.fetchUser` как suspend-функция должен быть кооперативно отменяемым (например, использовать функции, проверяющие `isActive`, или основанные на cancellable API), чтобы вызов действительно прерывался при `cancelChildren()` / `cancel()`.

### Подход С RxJava

```kotlin
class UserPresenter(private val repo: UserRepository) {
  private val disposables = CompositeDisposable()
  private var view: UserView? = null

  fun attach(view: UserView) {
    this.view = view
  }

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
    disposables.clear() // ✅ Отменяет/освобождает активные подписки, связанные с текущей View
  }

  fun destroy() {
    disposables.dispose() // ✅ Полная очистка при уничтожении презентера
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
  scope.coroutineContext.cancelChildren() // ✅ Всё ещё отменяем незавершённые операции
}
```

Шаблон no-op не заменяет отмену асинхронной работы: он лишь предотвращает попытки обновить уничтоженную `View`, поэтому отмена coroutine / подписок всё равно нужна.

## Answer (EN)

### Core Problem
A `Presenter` must not update a destroyed or detached `View` — this can cause memory leaks and crashes. The solution is to bind request cancellation to `View` lifecycle events and properly scope async work.

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
      // ✅ Cancellable, bound to presenter scope (assuming repo.fetchUser is cooperative-cancellable)
      val user = repo.fetchUser(id)
      view?.displayUser(user) // ✅ Null-safe
    }
  }

  fun detach() {
    view = null
    scope.coroutineContext.cancelChildren() // ✅ Cancel pending work tied to current view
  }

  fun destroy() {
    scope.cancel() // ✅ Full scope cleanup when presenter is destroyed
  }
}
```

**Why `Main.immediate`:** when already on the main thread, it runs immediately without extra dispatch, reducing latency and the chance of acting on stale state; when off main, it still dispatches to the main thread.

Important: `repo.fetchUser` as a suspend function must be cooperatively cancellable (e.g., using cancellable APIs or checking `isActive`) so that `cancelChildren()` / `cancel()` actually interrupt ongoing work.

### RxJava Approach

```kotlin
class UserPresenter(private val repo: UserRepository) {
  private val disposables = CompositeDisposable()
  private var view: UserView? = null

  fun attach(view: UserView) {
    this.view = view
  }

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
    disposables.clear() // ✅ Cancels/clears active subscriptions for the current View
  }

  fun destroy() {
    disposables.dispose() // ✅ Full cleanup when presenter is destroyed
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
  scope.coroutineContext.cancelChildren() // ✅ Still cancel ongoing async work
}
```

The no-op pattern does not replace cancellation of async work; it only prevents UI calls hitting a dead `View`, so you still need to cancel coroutines/subscriptions.

## Дополнительные Вопросы (RU)

1. В чем разница между `cancelChildren()` и `cancel()`, и когда использовать каждый из них в презентере?
2. Что происходит, если coroutine отменяется во время выполнения `suspend`-вызова, и какие вызовы корректно реагируют на отмену?
3. Как протестировать, что `Presenter` корректно отменяет запросы при вызове `detach()` и `destroy()`?
4. Почему в реализациях `Presenter` может быть предпочтителен диспетчер `Main.immediate` по сравнению с `Main`?
5. Как DI-фреймворки (`Hilt`, `Koin`) могут помочь в автоматизации связывания жизненного цикла и области `Presenter`?

## Follow-ups

1. How do `cancelChildren()` and `cancel()` differ, and when should each be used in a presenter?
2. What happens if a coroutine is cancelled while performing a suspend call, and which calls correctly react to cancellation?
3. How would you test that a `Presenter` correctly cancels requests on `detach()` and `destroy()`?
4. Why prefer `Main.immediate` over `Main` dispatcher in `Presenter` implementations?
5. How can DI frameworks (`Hilt`, `Koin`) automate `Presenter` lifecycle scoping?

## Ссылки (RU)

- [[c-coroutines]] — основы Kotlin coroutines
- [[c-android]] — обзор платформы Android и компонентов
- "Kotlin coroutines best practices" — официальная документация Android Developers
- "UI Layer Architecture" — раздел документации Android Developers о слоях UI

## References

- [[c-coroutines]] — Kotlin coroutines fundamentals
- [[c-android]] — Android platform and components overview
- https://developer.android.com/kotlin/coroutines/coroutines-best-practices
- https://developer.android.com/topic/architecture/ui-layer

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-activity-lifecycle-methods--android--medium]] — понимание колбэков жизненного цикла `Activity`
- Понимание паттерна MVP и разделения ответственности
- Базовые знания coroutines или `RxJava`

### Связанные (такой Же уровень)
- Общие стратегии обработки асинхронных операций в Android
- Использование `ViewModel` как альтернативы `Presenter`
- Выявление и предотвращение утечек памяти

### Продвинутые (сложнее)
- Построение lifecycle-aware наблюдателей
- Продвинутые паттерны отмены coroutines
- Тестирование поведения отмены в инструментальных тестах

## Related Questions

### Prerequisites (Easier)
- [[q-activity-lifecycle-methods--android--medium]] — Understanding `Activity` lifecycle callbacks
- Understanding of MVP pattern and separation of concerns
- Basic coroutine or `RxJava` knowledge

### Related (Same Level)
- General async handling strategies in Android
- Alternative approach with `ViewModel`
- Detecting and preventing memory leaks

### Advanced (Harder)
- Building lifecycle-aware observers
- Advanced coroutine cancellation patterns
- Testing cancellation behavior in instrumented tests
