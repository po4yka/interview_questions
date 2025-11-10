---
id: android-306
title: FragmentManager vs FragmentTransaction / FragmentManager против FragmentTransaction
aliases:
- FragmentManager vs FragmentTransaction
- FragmentManager против FragmentTransaction
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
status: reviewed
moc: moc-android
related:
- c-fragments
- c-lifecycle
created: 2025-10-15
updated: 2025-10-28
tags:
- android/fragment
- android/lifecycle
- difficulty/medium
- fragmentmanager
- fragmenttransaction
sources:
- https://developer.android.com/guide/fragments/fragmentmanager
---

# Вопрос (RU)
> В чем разница между FragmentManager и FragmentTransaction?

# Question (EN)
> What is the difference between FragmentManager and FragmentTransaction?

---

## Ответ (RU)

**FragmentManager** — менеджер для управления фрагментами в Activity и внутри фрагментов (через `childFragmentManager`). Отвечает за:
- Жизненный цикл фрагментов
- Операции со стеком возврата фрагментов
- Поиск фрагментов

**FragmentTransaction** — объект для группировки и выполнения операций с фрагментами (add, replace, remove и др.) единым набором изменений, применяемых при `commit*()`. Получается через `fragmentManager.beginTransaction()`.

**Ключевое различие:** FragmentManager — это контроллер/точка доступа к управлению (что и где управлять), FragmentTransaction — это описанная команда изменений (какие именно операции применить).

```kotlin
// FragmentManager: поиск и управление back stack
val manager = supportFragmentManager
val fragment = manager.findFragmentByTag("TAG")
manager.popBackStack()

// FragmentTransaction: модификация фрагментов
manager.beginTransaction().apply {
    replace(R.id.container, MyFragment())
    addToBackStack(null)
    commit() // ✅ Асинхронно: выполнение запланировано в главном потоке
}

// ❌ Неправильно: создать транзакцию и не закоммитить
val tx = manager.beginTransaction()
tx.replace(R.id.container, MyFragment())
// Фрагмент НЕ будет добавлен, пока не будет вызван commit*()!
```

**Методы commit:**
- `commit()` — асинхронный (ставит транзакцию в очередь на главном потоке; нужно вызывать до сохранения состояния)
- `commitNow()` — синхронный (выполняется немедленно, нельзя использовать с `addToBackStack`)
- `commitAllowingStateLoss()` — допускает потерю состояния (используется, когда потенциальная потеря состояния приемлема и осознанна)

## Answer (EN)

**FragmentManager** — the manager that controls fragments in an Activity and inside other fragments (via `childFragmentManager`). Responsible for:
- Fragment lifecycle management
- Fragment back stack operations
- Fragment lookup

**FragmentTransaction** — an object used to group and perform fragment operations (add, replace, remove, etc.) as a set of changes that are applied when `commit*()` is called. Obtained via `fragmentManager.beginTransaction()`.

**Key difference:** FragmentManager is the controller/access point (what and where to manage); FragmentTransaction is the described set of changes/command (which operations to apply).

```kotlin
// FragmentManager: lookup and back stack management
val manager = supportFragmentManager
val fragment = manager.findFragmentByTag("TAG")
manager.popBackStack()

// FragmentTransaction: fragment modifications
manager.beginTransaction().apply {
    replace(R.id.container, MyFragment())
    addToBackStack(null)
    commit() // ✅ Asynchronous: enqueues execution on the main thread
}

// ❌ Wrong: create transaction and don't commit
val tx = manager.beginTransaction()
tx.replace(R.id.container, MyFragment())
// Fragment will NOT be added until commit*() is called!
```

**Commit methods:**
- `commit()` — asynchronous (schedules the transaction to run on the main thread; must be called before state is saved)
- `commitNow()` — synchronous (executes immediately; cannot be used with `addToBackStack`)
- `commitAllowingStateLoss()` — allows state loss (should be used only when potential state loss is acceptable and understood)

---

## Follow-ups

- What happens if you don't call `commit()` on a transaction?
- When would you use `commitNow()` vs `commit()`?
- What causes `IllegalStateException: Can not perform this action after onSaveInstanceState`?
- What's the difference between `add()` and `replace()`?
- How does `addToBackStack()` affect fragment lifecycle?

## References

- [Android Developers: FragmentManager](https://developer.android.com/guide/fragments/fragmentmanager)
- [Android Developers: Fragment Transactions](https://developer.android.com/guide/fragments/transactions)

## Related Questions

### Prerequisites / Concepts

- [[c-fragments]]
- [[c-lifecycle]]


### Prerequisites (Easier)
- Fragment basics and lifecycle concepts
- Activity lifecycle fundamentals

### Related (Same Level)
- Fragment lifecycle states and callbacks
- Fragment state loss scenarios and solutions
- Fragment back stack navigation patterns

### Advanced (Harder)
- Fragment result API and communication patterns
- Fragment architecture with Navigation Component
- Custom fragment transitions and animations
