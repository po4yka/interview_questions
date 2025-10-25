---
id: 20251012-122711124
title: "FragmentManager vs FragmentTransaction / FragmentManager против FragmentTransaction"
aliases: ["FragmentManager vs FragmentTransaction", "FragmentManager против FragmentTransaction"]
topic: android
subtopics: [fragments, lifecycle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-fragmentmanager, q-fragment-lifecycle--android--medium, q-fragment-state-loss--android--medium]
created: 2025-10-15
updated: 2025-01-25
tags: [android/fragments, android/lifecycle, difficulty/medium, fragmentmanager, fragments, fragmenttransaction, lifecycle]
sources: [https://developer.android.com/guide/fragments/fragmentmanager]
date created: Saturday, October 25th 2025, 3:04:24 pm
date modified: Saturday, October 25th 2025, 4:47:10 pm
---

# Вопрос (RU)
> В чем разница между FragmentManager и FragmentTransaction?

# Question (EN)
> What is the difference between FragmentManager and FragmentTransaction?

---

## Ответ (RU)

**Теория FragmentManager и FragmentTransaction:**
FragmentManager управляет жизненным циклом фрагментов и стеком возврата, а FragmentTransaction выполняет операции с фрагментами как атомарные транзакции.

**FragmentManager:**
Управляет фрагментами, их поиском и стеком возврата.

```kotlin
// Получение FragmentManager и поиск фрагментов
val fragmentManager = supportFragmentManager
val fragment = fragmentManager.findFragmentByTag("MY_FRAGMENT")
val fragmentById = fragmentManager.findFragmentById(R.id.fragment_container)

// Управление стеком возврата
fragmentManager.popBackStack()
val backStackCount = fragmentManager.backStackEntryCount
```

**FragmentTransaction:**
Выполняет операции с фрагментами как транзакции.

```kotlin
// Создание и выполнение транзакции
val transaction = fragmentManager.beginTransaction()
transaction.add(R.id.fragment_container, MyFragment(), "MY_FRAGMENT")
transaction.addToBackStack("fragment_added")
transaction.commit()
```

**Основные операции транзакции:**
```kotlin
fragmentManager.beginTransaction().apply {
    add(R.id.container, Fragment1(), "FRAGMENT_1") // Добавить
    replace(R.id.container, Fragment2(), "FRAGMENT_2") // Заменить
    remove(fragment) // Удалить
    show(fragment) // Показать
    hide(fragment) // Скрыть
    addToBackStack("operation_name") // Добавить в стек
    commit() // Применить
}
```

**Методы commit:**
- `commit()` - асинхронный, планируется на главном потоке
- `commitNow()` - немедленное выполнение на главном потоке
- `commitAllowingStateLoss()` - безопасный commit, не выбрасывает исключение

## Answer (EN)

**FragmentManager and FragmentTransaction Theory:**
FragmentManager manages fragment lifecycle and back stack, while FragmentTransaction performs fragment operations as atomic transactions.

**FragmentManager:**
Manages fragments, their finding, and back stack.

```kotlin
// Getting FragmentManager and finding fragments
val fragmentManager = supportFragmentManager
val fragment = fragmentManager.findFragmentByTag("MY_FRAGMENT")
val fragmentById = fragmentManager.findFragmentById(R.id.fragment_container)

// Managing back stack
fragmentManager.popBackStack()
val backStackCount = fragmentManager.backStackEntryCount
```

**FragmentTransaction:**
Performs fragment operations as transactions.

```kotlin
// Creating and executing transaction
val transaction = fragmentManager.beginTransaction()
transaction.add(R.id.fragment_container, MyFragment(), "MY_FRAGMENT")
transaction.addToBackStack("fragment_added")
transaction.commit()
```

**Main transaction operations:**
```kotlin
fragmentManager.beginTransaction().apply {
    add(R.id.container, Fragment1(), "FRAGMENT_1") // Add
    replace(R.id.container, Fragment2(), "FRAGMENT_2") // Replace
    remove(fragment) // Remove
    show(fragment) // Show
    hide(fragment) // Hide
    addToBackStack("operation_name") // Add to back stack
    commit() // Apply
}
```

**Commit methods:**
- `commit()` - asynchronous, scheduled on main thread
- `commitNow()` - immediate execution on main thread
- `commitAllowingStateLoss()` - safe commit, doesn't throw exception

---

## Follow-ups

- What happens if you don't call commit() on a transaction?
- How do you handle fragment state loss?
- What's the difference between attach/detach and show/hide?

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components
- [[q-fragment-basics--android--easy]] - Fragment basics

### Related (Same Level)
- [[q-fragment-lifecycle--android--medium]] - Fragment lifecycle
- [[q-fragment-state-loss--android--medium]] - Fragment state loss
- [[q-fragment-navigation--android--medium]] - Fragment navigation

### Advanced (Harder)
- [[q-fragment-architecture--android--hard]] - Fragment architecture
- [[q-android-runtime-internals--android--hard]] - Runtime internals
