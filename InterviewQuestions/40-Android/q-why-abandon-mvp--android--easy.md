---
id: android-379
title: "Why Abandon MVP / Почему отказаться от MVP"
aliases: [MVP problems, Why Abandon MVP, Почему отказаться от MVP, Проблемы MVP]
topic: android
subtopics: [architecture-mvvm]
question_kind: theory
difficulty: easy
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android, c-architecture-patterns, q-android-architectural-patterns--android--medium, q-mvp-pattern--android--medium, q-mvvm-vs-mvp-differences--android--medium, q-why-separate-ui-and-business-logic--android--easy]
created: 2024-10-15
updated: 2025-11-10
tags: [android/architecture-mvvm, architecture-patterns, difficulty/easy, mvi, mvp, mvvm]
sources: ["https://developer.android.com/jetpack/guide", "https://developer.android.com/topic/architecture"]

date created: Saturday, November 1st 2025, 12:47:11 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---
# Вопрос (RU)
> Почему многие отказываются от MVP?

# Question (EN)
> Why do many developers abandon MVP?

---

## Ответ (RU)

Android разработчики часто отказываются от MVP в новых проектах по нескольким ключевым причинам (см. также [[c-android]], [[c-architecture-patterns]]):

### 1. Слишком Много Шаблонного Кода

Классическая реализация MVP обычно требует создавать интерфейсы `View`/Presenter для каждого экрана и множества однотипных методов:

```kotlin
// ❌ Много повторяющегося кода
interface UserView {
    fun showLoading()
    fun hideLoading()
    fun showUsers(users: List<User>)
    fun showError(message: String)
}

interface UserPresenter {
    fun loadUsers()
    fun onUserClicked(user: User)
}
```

Это ведёт к бойлерплейту, сложнее поддерживать и развивать.

### 2. Ручное Управление Жизненным Циклом

Presenter сам по себе не "жизненно-цикл-осведомлён" (в отличие от `ViewModel`) и требует явного управления привязкой/отвязкой `View`:

```kotlin
// ❌ Нужно помнить про очистку
override fun onDestroy() {
    super.onDestroy()
    presenter.detachView()  // Легко забыть и получить утечки памяти или крэши
}
```

На практике это увеличивает риск утечек памяти, вызовов на уничтоженную `View` и дублирования логики при поворотах экрана.

### 3. Неудобная Работа С Реактивностью И Асинхронщиной

Исторически MVP массово применялся до появления современных инструментов (Lifecycle-aware компоненты, `ViewModel`, `LiveData`, `Flow`, Coroutines). Интегрировать их в MVP возможно, но:
- нужно вручную управлять подписками и их отменой,
- Presenter не имеет встроенной привязки к lifecycle,
- легко допустить ошибки при уничтожении/пересоздании `View`.

```kotlin
// ❌ Приходится вручную следить за подписками и жизненным циклом
class UserPresenter(private val view: UserView) {
    fun loadUsers() {
        // Нужно самим решать, где запускать корутины/подписки
        // и когда отменять их при уничтожении View
    }
}
```

### 4. Современные Альтернативы Удобнее На Android

**MVVM с `ViewModel`:**
- ✅ `ViewModel` переживает rotation и управляется LifecycleOwner-ами
- ✅ Встроенная поддержка `LiveData`/`Flow` и SavedStateHandle через Jetpack
- ✅ Меньше шаблонного кода за счёт отсутствия обязательных `View`-интерфейсов
- ✅ Рекомендуется официальными Android-гайдами

**MVI:**
- ✅ Однонаправленный поток данных
- ✅ Предсказуемое состояние
- ✅ Хорошо сочетается с декларативным UI (Jetpack Compose)

В итоге для Android экосистемы MVVM/MVI с архитектурными компонентами оказываются более естественными и безопасными.

### Сравнение

| Критерий | MVP (классический) | MVVM (с `ViewModel`) |
|----------|--------------------|--------------------|
| Шаблонный код | Часто много | Обычно меньше |
| Lifecycle | Ручной (detach/attach) | Встроенная поддержка lifecycle |
| Rotation | Требует явной обработки сохранения/восстановления | `ViewModel` переживает rotation |
| `Flow`/`LiveData` | Можно использовать, но без встроенной поддержки lifecycle | Нативная интеграция |

### Резюме

От MVP в новых Android-проектах чаще отказываются из-за:
- Избыточного шаблонного кода (особенно с интерфейсами для каждого экрана)
- Ручного и хрупкого управления жизненным циклом и подписками
- Неудобной интеграции с современными реактивными и lifecycle-aware инструментами
- Наличия более подходящих под Android альтернатив (MVVM с `ViewModel`, MVI)

MVP остаётся рабочим паттерном в существующих кодовых базах и может использоваться в специфических сценариях, но де-факто рекомендованный стандарт сегодня — архитектура на основе Jetpack (MVVM/`ViewModel` и/или однонаправленные потоки состояния).

## Answer (EN)

Android developers often move away from MVP in new projects for several key reasons:

### 1. Too Much Boilerplate Code

A classic MVP implementation usually requires separate `View`/Presenter interfaces for each screen and many repetitive methods:

```kotlin
// ❌ Lots of repetitive code
interface UserView {
    fun showLoading()
    fun hideLoading()
    fun showUsers(users: List<User>)
    fun showError(message: String)
}

interface UserPresenter {
    fun loadUsers()
    fun onUserClicked(user: User)
}
```

This leads to boilerplate and makes the codebase harder to maintain and evolve.

### 2. Manual Lifecycle Management

A Presenter is not lifecycle-aware by default (unlike a `ViewModel`) and needs explicit attach/detach handling:

```kotlin
// ❌ Need to remember cleanup
override fun onDestroy() {
    super.onDestroy()
    presenter.detachView()  // Easy to forget and cause leaks or crashes
}
```

In practice this increases the risk of memory leaks, calls on a destroyed `View`, and duplicated logic across configuration changes.

### 3. Awkward Reactive and Async Handling

MVP became popular before the modern Android stack (Lifecycle-aware components, `ViewModel`, `LiveData`, `Flow`, Coroutines). You can integrate these tools into MVP, but:
- you must manage subscriptions and cancellations manually,
- the presenter has no built-in lifecycle awareness,
- it’s easy to get things wrong when the `View` is destroyed/recreated.

```kotlin
// ❌ You must manually manage subscriptions and lifecycle
class UserPresenter(private val view: UserView) {
    fun loadUsers() {
        // You have to decide where to launch coroutines/subscriptions
        // and when to cancel them when the View is destroyed
    }
}
```

### 4. Modern Android-Friendly Alternatives

**MVVM with `ViewModel`:**
- ✅ `ViewModel` survives configuration changes and works with LifecycleOwner
- ✅ Built-in support for `LiveData`/`Flow` and SavedStateHandle via Jetpack
- ✅ Less boilerplate (no mandatory `View` interfaces)
- ✅ Recommended by official Android architecture guidelines

**MVI:**
- ✅ Unidirectional data flow
- ✅ Predictable state management
- ✅ Pairs well with declarative UI (Jetpack Compose)

As a result, MVVM/MVI with Architecture Components are a more natural and safer fit for modern Android apps.

### Comparison

| Criteria | MVP (classic) | MVVM (with `ViewModel`) |
|----------|---------------|------------------------|
| Boilerplate | Often high | Generally lower |
| Lifecycle | Manual (attach/detach) | Lifecycle-aware support built-in |
| Rotation | Requires explicit state handling | `ViewModel` survives rotation |
| `Flow`/`LiveData` Support | Possible, but no built-in lifecycle support | First-class integration |

### Summary

MVP is less favored for new Android projects because of:
- Excessive boilerplate (especially with per-screen interfaces)
- Manual, fragile lifecycle and subscription management
- Inconvenient integration with modern reactive and lifecycle-aware tools
- More suitable alternatives available (MVVM with `ViewModel`, MVI)

MVP remains a valid pattern in existing codebases and specific scenarios, but the de facto recommended approach today is Jetpack-based architectures (MVVM/`ViewModel` and/or unidirectional state flow).

---

## Дополнительные Вопросы (RU)

- Как `ViewModel` переживает изменения конфигурации?
- В чем основное отличие между MVVM и MVI?
- Когда всё еще имеет смысл использовать MVP?
- Как Jetpack Compose влияет на выбор архитектурных паттернов?
- Что такое паттерн Repository и как он сочетается с MVVM?

## Follow-ups

- How does `ViewModel` survive configuration changes?
- What is the main difference between MVVM and MVI?
- When would you still use MVP?
- How does Jetpack Compose change architecture patterns?
- What is the Repository pattern and how does it work with MVVM?

## Ссылки (RU)

- [Руководство по архитектуре Android](https://developer.android.com/topic/architecture)
- [Руководство по архитектуре приложений](https://developer.android.com/jetpack/guide)

## References

- [Android Architecture Guide](https://developer.android.com/topic/architecture)
- [Guide to app architecture](https://developer.android.com/jetpack/guide)

## Связанные Вопросы (RU)

### Предварительные (проще)
- [[q-why-separate-ui-and-business-logic--android--easy]]
- [[q-viewmodel-pattern--android--easy]]
- [[q-architecture-components-libraries--android--easy]]

### Связанные (тот Же уровень)
- [[q-android-jetpack-overview--android--easy]]
- [[q-what-is-data-binding--android--easy]]

### Продвинутые (сложнее)
- [[q-mvp-pattern--android--medium]]
- [[q-mvvm-pattern--android--medium]]
- [[q-mvvm-vs-mvp-differences--android--medium]]
- [[q-android-architectural-patterns--android--medium]]
- [[q-mvi-architecture--android--hard]]
- [[q-clean-architecture-android--android--hard]]

## Related Questions

### Prerequisites (Easier)
- [[q-why-separate-ui-and-business-logic--android--easy]]
- [[q-viewmodel-pattern--android--easy]]
- [[q-architecture-components-libraries--android--easy]]

### Related (Same Level)
- [[q-android-jetpack-overview--android--easy]]
- [[q-what-is-data-binding--android--easy]]

### Advanced (Harder)
- [[q-mvp-pattern--android--medium]]
- [[q-mvvm-pattern--android--medium]]
- [[q-mvvm-vs-mvp-differences--android--medium]]
- [[q-android-architectural-patterns--android--medium]]
- [[q-mvi-architecture--android--hard]]
- [[q-clean-architecture-android--android--hard]]
