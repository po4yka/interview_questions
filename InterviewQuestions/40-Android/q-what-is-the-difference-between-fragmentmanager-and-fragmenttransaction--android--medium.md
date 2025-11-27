---
id: android-356
title: What Is The Difference Between FragmentManager And FragmentTransaction
aliases: [FragmentManager vs FragmentTransaction, Разница между FragmentManager и FragmentTransaction]
topic: android
subtopics:
  - fragment
  - lifecycle
  - ui-views
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-fragments
  - c-lifecycle
  - q-can-state-loss-be-related-to-a-fragment--android--medium
  - q-dagger-build-time-optimization--android--medium
  - q-fragmentmanager-vs-fragmenttransaction--android--medium
  - q-how-to-choose-layout-for-fragment--android--easy
  - q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium
  - q-pass-large-data-between-activities--android--hard
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [android/fragment, android/lifecycle, android/ui-views, difficulty/medium, fragmentmanager, fragments, fragmenttransaction]

date created: Saturday, November 1st 2025, 12:47:09 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---
# Вопрос (RU)

> В чём разница между FragmentManager и FragmentTransaction?

# Question (EN)

> What is the difference between FragmentManager and FragmentTransaction?

---

## Ответ (RU)

**FragmentManager** управляет жизненным циклом фрагментов, их добавлением/удалением и back stack. Обычно он ассоциирован с активити или хостом, который владеет фрагментами (например, `supportFragmentManager` у активности или `childFragmentManager` у фрагмента).

**FragmentTransaction** представляет набор операций над фрагментами (add, replace, remove), которые применяются как одна логическая транзакция. Транзакция создаётся через `FragmentManager.beginTransaction()` и применяется через один из методов `commit*()`.

Аналогия: FragmentManager — это база данных, FragmentTransaction — SQL-транзакция с операциями.

### Основные Возможности FragmentManager

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val fm = supportFragmentManager

        // ✅ Поиск фрагментов
        val fragment = fm.findFragmentByTag("MY_TAG")
        val fragmentById = fm.findFragmentById(R.id.container)

        // ✅ Управление back stack
        val count = fm.backStackEntryCount
        fm.popBackStack()  // pop last transaction

        // ✅ Слушатель изменений back stack
        fm.addOnBackStackChangedListener {
            Log.d("FM", "Stack changed: ${fm.backStackEntryCount}")
        }
    }
}
```

### FragmentTransaction Операции

```kotlin
class MainActivity : AppCompatActivity() {
    fun showFragment() {
        val fragment = MyFragment()

        supportFragmentManager.beginTransaction().apply {
            // ✅ Добавление фрагмента
            add(R.id.container, fragment, "TAG")

            // ✅ Замена фрагмента
            replace(R.id.container, AnotherFragment())

            // ✅ Удаление фрагмента
            supportFragmentManager.findFragmentByTag("TAG")?.let {
                remove(it)
            }

            // ✅ Show/Hide (не пересоздаёт view)
            show(fragment)
            hide(fragment)

            // ✅ Добавление в back stack
            addToBackStack("operation_name")

            commit()  // или commitNow(), см. ниже
        }
    }
}
```

### Варианты Commit

```kotlin
// ✅ Асинхронный commit: операции будут выполнены позже в главном потоке
transaction.commit()

// ✅ Синхронный commit: операции применяются немедленно на текущем потоке (обычно UI)
// Требует соблюдения ограничений API (нельзя вызывать в определённых состояниях/колбэках)
transaction.commitNow()

// ⚠️ Разрешает потерю состояния: не бросает IllegalStateException при state loss
// Использовать только при полном понимании последствий
transaction.commitAllowingStateLoss()

// ⚠️ Синхронный commit c разрешённой потерей состояния
transaction.commitNowAllowingStateLoss()
```

### Сравнение

| FragmentManager | FragmentTransaction |
|----------------|---------------------|
| Управляет жизненным циклом и состоянием фрагментов | Описывает и выполняет операции над фрагментами |
| Находит существующие фрагменты | Добавляет/удаляет/заменяет фрагменты |
| Управляет back stack транзакций | Добавляет операции в back stack |
| Имеется у активити (`supportFragmentManager`) и у фрагментов (`childFragmentManager`) | Создаётся через `beginTransaction()` для набора операций |
| Преимущественно операции чтения/управления состоянием | Мутация состояния через commit-методы |

## Answer (EN)

**FragmentManager** manages fragment lifecycle, addition/removal, and the back stack. It is associated with the host that owns fragments (e.g., an activity via `supportFragmentManager` or a fragment via `childFragmentManager`).

**FragmentTransaction** represents a set of fragment operations (add, replace, remove) that are applied as one logical transaction. Transactions are created via `FragmentManager.beginTransaction()` and finalized via one of the `commit*()` methods.

Analogy: FragmentManager is the database, FragmentTransaction is the SQL transaction containing operations.

### Core FragmentManager Capabilities

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val fm = supportFragmentManager

        // ✅ Find fragments
        val fragment = fm.findFragmentByTag("MY_TAG")
        val fragmentById = fm.findFragmentById(R.id.container)

        // ✅ Back stack management
        val count = fm.backStackEntryCount
        fm.popBackStack()  // pop last transaction

        // ✅ Back stack change listener
        fm.addOnBackStackChangedListener {
            Log.d("FM", "Stack changed: ${fm.backStackEntryCount}")
        }
    }
}
```

### FragmentTransaction Operations

```kotlin
class MainActivity : AppCompatActivity() {
    fun showFragment() {
        val fragment = MyFragment()

        supportFragmentManager.beginTransaction().apply {
            // ✅ Add fragment
            add(R.id.container, fragment, "TAG")

            // ✅ Replace fragment
            replace(R.id.container, AnotherFragment())

            // ✅ Remove fragment
            supportFragmentManager.findFragmentByTag("TAG")?.let {
                remove(it)
            }

            // ✅ Show/Hide (doesn't recreate view)
            show(fragment)
            hide(fragment)

            // ✅ Add to back stack
            addToBackStack("operation_name")

            commit()  // or commitNow(), see below
        }
    }
}
```

### Commit Variants

```kotlin
// ✅ Asynchronous commit: operations are scheduled and run later on the main thread
transaction.commit()

// ✅ Synchronous commit: operations are executed immediately on the current thread (typically main)
// Subject to API restrictions (cannot be used in certain states/callbacks)
transaction.commitNow()

// ⚠️ Allows state loss: does not throw IllegalStateException if state has already been saved
// Use only when you fully understand and accept potential state loss
transaction.commitAllowingStateLoss()

// ⚠️ Synchronous commit with state loss allowed
transaction.commitNowAllowingStateLoss()
```

### Comparison

| FragmentManager | FragmentTransaction |
|----------------|---------------------|
| Manages fragment lifecycle and state | Describes and performs fragment operations |
| Finds existing fragments | Adds/removes/replaces fragments |
| Manages the back stack of fragment transactions | Adds operations to the back stack |
| Available on activities (`supportFragmentManager`) and fragments (`childFragmentManager`) | Created via `beginTransaction()` for a set of operations |
| Primarily query/control operations | Mutating operations via commit methods |

---

## Follow-ups

1. What happens if you don't call `commit()` on a FragmentTransaction?
2. When should you use `commitNow()` instead of `commit()`?
3. What causes "IllegalStateException: Can not perform this action after onSaveInstanceState"?
4. How does `addToBackStack()` affect fragment lifecycle?
5. What's the difference between `replace()` and `remove()` + `add()`?

## References

- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - `Fragment` lifecycle
- [[q-can-state-loss-be-related-to-a-fragment--android--medium]] - State loss issues
- [[q-fragments-history-and-purpose--android--hard]] - `Fragment` architecture
- Official: [Fragments Guide](https://developer.android.com/guide/fragments)
- Official: [FragmentManager API](https://developer.android.com/reference/androidx/fragment/app/FragmentManager)

## Related Questions

### Prerequisites / Concepts

- [[c-fragments]]
- [[c-lifecycle]]

### Prerequisites (Easier)
- [[q-how-to-choose-layout-for-fragment--android--easy]] - `Fragment` basics
- [[q-how-to-display-two-identical-fragments-on-the-screen-at-the-same-time--android--easy]] - Multiple fragments

### Related (Medium)
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - `Fragment` lifecycle
- [[q-can-state-loss-be-related-to-a-fragment--android--medium]] - State loss
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Lifecycle comparison

### Advanced (Harder)
- [[q-fragments-history-and-purpose--android--hard]] - `Fragment` design rationale
- [[q-why-fragment-needs-separate-callback-for-ui-creation--android--hard]] - `Fragment` architecture
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - `Fragment` necessity
