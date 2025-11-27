---
id: android-306
title: FragmentManager vs FragmentTransaction / FragmentManager против FragmentTransaction
aliases: [FragmentManager vs FragmentTransaction, FragmentManager против FragmentTransaction]
topic: android
subtopics:
  - fragment
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
  - c-android-lifecycle
  - q-activity-lifecycle-methods--android--medium
  - q-dagger-build-time-optimization--android--medium
  - q-data-sync-unstable-network--android--hard
  - q-what-is-the-difference-between-fragmentmanager-and-fragmenttransaction--android--medium
created: 2025-10-15
updated: 2025-11-11
tags: [android/fragment, android/lifecycle, difficulty/medium, fragmentmanager, fragmenttransaction]
sources:
  - "https://developer.android.com/guide/fragments/fragmentmanager"

date created: Saturday, November 1st 2025, 12:46:50 pm
date modified: Tuesday, November 25th 2025, 8:54:00 pm
---
# Вопрос (RU)
> В чем разница между FragmentManager и FragmentTransaction?

# Question (EN)
> What is the difference between FragmentManager and FragmentTransaction?

---

## Ответ (RU)

**FragmentManager** — менеджер для управления фрагментами в `Activity` и внутри фрагментов (через `childFragmentManager`). Отвечает за:
- Жизненный цикл фрагментов и их состояния
- Операции со стеком возврата фрагментов
- Поиск фрагментов
- Регистрацию callback-ов (например, `OnBackStackChangedListener`) и взаимодействие с системой навигации/жизненного цикла

**FragmentTransaction** — объект для группировки и выполнения операций с фрагментами (add, replace, remove и др.) единым набором изменений, применяемых только при вызове одного из методов `commit*()`. Получается через `fragmentManager.beginTransaction()`.

**Ключевое различие:** FragmentManager — это контроллер/точка доступа к управлению (что и где управлять), FragmentTransaction — это описанная команда изменений (какие именно операции применить), которая не оказывает эффекта, пока не будет закоммичена.

```kotlin
// FragmentManager: поиск и управление back stack
val manager = supportFragmentManager
val fragment = manager.findFragmentByTag("TAG")
manager.popBackStack()

// FragmentTransaction: модификация фрагментов
manager.beginTransaction().apply {
    replace(R.id.container, MyFragment())
    addToBackStack(null)
    commit() // ✅ Асинхронно: транзакция ставится в очередь и будет выполнена на главном потоке,
             // когда цикл сообщений сможет её обработать. Вызывать до onSaveInstanceState().
}

// ❌ Неправильно: создать транзакцию и не закоммитить
val tx = manager.beginTransaction()
tx.replace(R.id.container, MyFragment())
// Фрагмент НЕ будет добавлен, пока не будет вызван commit*()!
```

**Методы commit:**
- `commit()` — асинхронный: ставит транзакцию в очередь для выполнения на главном потоке; должен быть вызван до сохранения состояния `Activity`/`Fragment` (`onSaveInstanceState()`), иначе возможен `IllegalStateException`.
- `commitNow()` — синхронный: выполняет транзакцию немедленно в текущем проходе цикла; нельзя использовать вместе с `addToBackStack()`.
- `commitAllowingStateLoss()` — допускает потерю состояния: может быть вызван после `onSaveInstanceState()`, если потенциальная потеря состояния приемлема и осознанна.

## Answer (EN)

**FragmentManager** is the manager that controls fragments in an `Activity` and inside other fragments (via `childFragmentManager`). Responsible for:
- Managing fragment lifecycle and state
- Managing the fragment back stack operations
- Looking up fragments
- Registering callbacks (e.g., `OnBackStackChangedListener`) and integrating with lifecycle/navigation behavior

**FragmentTransaction** is an object used to group and perform fragment operations (add, replace, remove, etc.) as a set of changes that only take effect when one of the `commit*()` methods is called. It is obtained via `fragmentManager.beginTransaction()`.

**Key difference:** FragmentManager is the controller/access point (what and where to manage); FragmentTransaction is the described command/set of changes (which operations to apply) that has no effect until it is committed.

```kotlin
// FragmentManager: lookup and back stack management
val manager = supportFragmentManager
val fragment = manager.findFragmentByTag("TAG")
manager.popBackStack()

// FragmentTransaction: fragment modifications
manager.beginTransaction().apply {
    replace(R.id.container, MyFragment())
    addToBackStack(null)
    commit() // ✅ Asynchronous: enqueues the transaction to run on the main thread
             // when the message loop can process it. Must be called before onSaveInstanceState().
}

// ❌ Wrong: create transaction and don't commit
val tx = manager.beginTransaction()
tx.replace(R.id.container, MyFragment())
// The fragment will NOT be added until a commit*() method is called!
```

**Commit methods:**
- `commit()` — asynchronous: enqueues the transaction to be executed on the main thread; must be called before the state is saved (`onSaveInstanceState()`), otherwise `IllegalStateException` can be thrown.
- `commitNow()` — synchronous: executes the transaction immediately in the current loop iteration; cannot be used with `addToBackStack()`.
- `commitAllowingStateLoss()` — allows state loss: can be used after `onSaveInstanceState()` when potential state loss is acceptable and understood.

---

## Дополнительные Вопросы (RU)

- Что произойдет, если не вызвать `commit()` у транзакции?
- Когда использовать `commitNow()` вместо `commit()`?
- Что вызывает `IllegalStateException: Can not perform this action after onSaveInstanceState`?
- В чем разница между `add()` и `replace()`?
- Как `addToBackStack()` влияет на жизненный цикл фрагментов?

## Follow-ups

- What happens if you don't call `commit()` on a transaction?
- When would you use `commitNow()` vs `commit()`?
- What causes `IllegalStateException: Can not perform this action after onSaveInstanceState`?
- What's the difference between `add()` and `replace()`?
- How does `addToBackStack()` affect fragment lifecycle?

## Ссылки (RU)

- [Android Developers: FragmentManager](https://developer.android.com/guide/fragments/fragmentmanager)
- [Android Developers: `Fragment` Transactions](https://developer.android.com/guide/fragments/transactions)

## References

- [Android Developers: FragmentManager](https://developer.android.com/guide/fragments/fragmentmanager)
- [Android Developers: `Fragment` Transactions](https://developer.android.com/guide/fragments/transactions)

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-android]]
- [[c-android-lifecycle]]

### Предпосылки (проще)
- Базовые понятия и жизненный цикл `Fragment`
- Основы жизненного цикла `Activity`

### Связанные (того Же уровня)
- Состояния и колбэки жизненного цикла `Fragment`
- Сценарии потери состояния `Fragment` и способы их избежать
- Паттерны навигации с использованием back stack фрагментов

### Продвинутые (сложнее)
- `Fragment` result API и паттерны коммуникации между фрагментами
- Архитектура с `Fragment` и Navigation Component
- Пользовательские переходы и анимации фрагментов

## Related Questions

### Prerequisites / Concepts

- [[c-android]]
- [[c-android-lifecycle]]

### Prerequisites (Easier)
- `Fragment` basics and lifecycle concepts
- `Activity` lifecycle fundamentals

### Related (Same Level)
- `Fragment` lifecycle states and callbacks
- `Fragment` state loss scenarios and solutions
- `Fragment` back stack navigation patterns

### Advanced (Harder)
- `Fragment` result API and communication patterns
- `Fragment` architecture with Navigation Component
- Custom fragment transitions and animations
