---
id: 20251029-120000
title: "What Is The Difference Between Fragmentmanager And Fragmenttransaction / В чём разница между FragmentManager и FragmentTransaction"
aliases: ["FragmentManager vs FragmentTransaction", "Разница между FragmentManager и FragmentTransaction"]
topic: android
subtopics: [fragment, lifecycle, ui-views]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-how-to-choose-layout-for-fragment--android--easy, q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium, q-can-state-loss-be-related-to-a-fragment--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-29
tags: [android/fragment, android/lifecycle, android/ui-views, fragments, fragmentmanager, fragmenttransaction, difficulty/medium]
---
# Вопрос (RU)

В чём разница между FragmentManager и FragmentTransaction?

# Question (EN)

What is the difference between FragmentManager and FragmentTransaction?

---

## Ответ (RU)

**FragmentManager** управляет жизненным циклом фрагментов и back stack. Это менеджер состояния фрагментов в активити.

**FragmentTransaction** представляет набор операций над фрагментами (add, replace, remove), которые выполняются атомарно. Транзакция создаётся через `FragmentManager.beginTransaction()` и применяется через `commit()`.

Аналогия: FragmentManager — это база данных, FragmentTransaction — SQL-транзакция с операциями.

### Основные возможности FragmentManager

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

### FragmentTransaction операции

```kotlin
class MainActivity : AppCompatActivity() {
    fun showFragment() {
        supportFragmentManager.beginTransaction().apply {
            // ✅ Добавление фрагмента
            add(R.id.container, MyFragment(), "TAG")

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

            commit()  // или commitNow()
        }
    }
}
```

### Варианты commit

```kotlin
// ✅ Асинхронный commit (рекомендуется)
transaction.commit()

// ✅ Синхронный commit (блокирует UI thread)
transaction.commitNow()

// ❌ Не бросает IllegalStateException при state loss
transaction.commitAllowingStateLoss()  // use only if necessary

// ❌ Синхронный + state loss allowed
transaction.commitNowAllowingStateLoss()
```

### Сравнение

| FragmentManager | FragmentTransaction |
|----------------|---------------------|
| Управляет жизненным циклом | Выполняет операции |
| Находит фрагменты | Добавляет/удаляет фрагменты |
| Управляет back stack | Добавляет в back stack |
| Singleton для активити | Создаётся для каждой операции |
| Query операции | Mutate операции |

## Answer (EN)

**FragmentManager** manages fragment lifecycle and back stack. It's the state manager for fragments in an activity.

**FragmentTransaction** represents a set of fragment operations (add, replace, remove) that execute atomically. Transactions are created via `FragmentManager.beginTransaction()` and applied via `commit()`.

Analogy: FragmentManager is a database, FragmentTransaction is a SQL transaction with operations.

### Core FragmentManager capabilities

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

### FragmentTransaction operations

```kotlin
class MainActivity : AppCompatActivity() {
    fun showFragment() {
        supportFragmentManager.beginTransaction().apply {
            // ✅ Add fragment
            add(R.id.container, MyFragment(), "TAG")

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

            commit()  // or commitNow()
        }
    }
}
```

### Commit variants

```kotlin
// ✅ Asynchronous commit (recommended)
transaction.commit()

// ✅ Synchronous commit (blocks UI thread)
transaction.commitNow()

// ❌ Doesn't throw IllegalStateException on state loss
transaction.commitAllowingStateLoss()  // use only if necessary

// ❌ Synchronous + state loss allowed
transaction.commitNowAllowingStateLoss()
```

### Comparison

| FragmentManager | FragmentTransaction |
|----------------|---------------------|
| Manages lifecycle | Performs operations |
| Finds fragments | Adds/removes fragments |
| Manages back stack | Adds to back stack |
| Singleton per activity | Created per operation |
| Query operations | Mutate operations |

---

## Follow-ups

1. What happens if you don't call `commit()` on a FragmentTransaction?
2. When should you use `commitNow()` instead of `commit()`?
3. What causes "IllegalStateException: Can not perform this action after onSaveInstanceState"?
4. How does `addToBackStack()` affect fragment lifecycle?
5. What's the difference between `replace()` and `remove()` + `add()`?

## References

- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Fragment lifecycle
- [[q-can-state-loss-be-related-to-a-fragment--android--medium]] - State loss issues
- [[q-fragments-history-and-purpose--android--hard]] - Fragment architecture
- Official: [Fragments Guide](https://developer.android.com/guide/fragments)
- Official: [FragmentManager API](https://developer.android.com/reference/androidx/fragment/app/FragmentManager)

## Related Questions

### Prerequisites (Easier)
- [[q-how-to-choose-layout-for-fragment--android--easy]] - Fragment basics
- [[q-how-to-display-two-identical-fragments-on-the-screen-at-the-same-time--android--easy]] - Multiple fragments

### Related (Medium)
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Fragment lifecycle
- [[q-can-state-loss-be-related-to-a-fragment--android--medium]] - State loss
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Lifecycle comparison

### Advanced (Harder)
- [[q-fragments-history-and-purpose--android--hard]] - Fragment design rationale
- [[q-why-fragment-needs-separate-callback-for-ui-creation--android--hard]] - Fragment architecture
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Fragment necessity
