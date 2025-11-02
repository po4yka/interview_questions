---
id: android-306
title: "FragmentManager vs FragmentTransaction / FragmentManager против FragmentTransaction"
aliases: ["FragmentManager vs FragmentTransaction", "FragmentManager против FragmentTransaction"]
topic: android
subtopics: [fragment, lifecycle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: []
created: 2025-10-15
updated: 2025-10-28
tags: [android/fragment, android/lifecycle, difficulty/medium, fragmentmanager, fragmenttransaction]
sources: [https://developer.android.com/guide/fragments/fragmentmanager]
date created: Tuesday, October 28th 2025, 7:38:00 am
date modified: Saturday, November 1st 2025, 5:43:35 pm
---

# Вопрос (RU)
> В чем разница между FragmentManager и FragmentTransaction?

# Question (EN)
> What is the difference between FragmentManager and FragmentTransaction?

---

## Ответ (RU)

**FragmentManager** — менеджер для управления фрагментами Activity. Отвечает за:
- Жизненный цикл фрагментов
- Back stack (стек возврата)
- Поиск фрагментов

**FragmentTransaction** — объект для выполнения операций с фрагментами (add, replace, remove) как атомарная единица работы. Получается через `fragmentManager.beginTransaction()`.

**Ключевое различие:** FragmentManager — это контроллер (что делать), FragmentTransaction — это команда (как делать).

```kotlin
// FragmentManager: поиск и управление back stack
val manager = supportFragmentManager
val fragment = manager.findFragmentByTag("TAG")
manager.popBackStack()

// FragmentTransaction: модификация фрагментов
manager.beginTransaction().apply {
    replace(R.id.container, MyFragment())
    addToBackStack(null)
    commit() // ✅ Асинхронно, UI-safe
}

// ❌ Неправильно: создать транзакцию и не закоммитить
val tx = manager.beginTransaction()
tx.replace(R.id.container, MyFragment())
// Фрагмент НЕ будет добавлен!
```

**Методы commit:**
- `commit()` — асинхронный (планируется на главном потоке)
- `commitNow()` — синхронный (выполняется немедленно, нельзя с `addToBackStack`)
- `commitAllowingStateLoss()` — безопасный при возможной потере состояния

## Answer (EN)

**FragmentManager** — the manager that controls Activity's fragments. Responsible for:
- Fragment lifecycle management
- Back stack operations
- Fragment lookup

**FragmentTransaction** — an object for performing fragment operations (add, replace, remove) as an atomic unit of work. Obtained via `fragmentManager.beginTransaction()`.

**Key difference:** FragmentManager is the controller (what to manage), FragmentTransaction is the command (how to change).

```kotlin
// FragmentManager: lookup and back stack management
val manager = supportFragmentManager
val fragment = manager.findFragmentByTag("TAG")
manager.popBackStack()

// FragmentTransaction: fragment modifications
manager.beginTransaction().apply {
    replace(R.id.container, MyFragment())
    addToBackStack(null)
    commit() // ✅ Asynchronous, UI-safe
}

// ❌ Wrong: create transaction and don't commit
val tx = manager.beginTransaction()
tx.replace(R.id.container, MyFragment())
// Fragment will NOT be added!
```

**Commit methods:**
- `commit()` — asynchronous (scheduled on main thread)
- `commitNow()` — synchronous (executes immediately, can't use with `addToBackStack`)
- `commitAllowingStateLoss()` — safe when state loss is acceptable

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
