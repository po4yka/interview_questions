---
id: "20251015082237547"
title: "What Is The Difference Between Fragmentmanager And Fragmenttransaction / What Is The Difference Between Fragmentmanager и Fragmenttransaction"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [fragmentmanager, fragmenttransaction, android, ui, fragments, difficulty/medium]
---
# What is the difference between FragmentManager and FragmentTransaction?

# Вопрос (RU)

В чём разница между FragmentManager и FragmentTransaction

## Answer (EN)
**FragmentManager** manages fragments: adding, finding, back stack. **FragmentTransaction** is used to perform operations with fragments (add, replace, remove). It's like a database transaction applied to UI. Transaction is created via `FragmentManager.beginTransaction()` and applied via `commit()`.

### FragmentManager

Manages the fragment lifecycle and back stack.

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Get FragmentManager
        val fragmentManager = supportFragmentManager

        // Find fragment by tag or ID
        val fragment = fragmentManager.findFragmentByTag("MY_FRAGMENT")
        val fragmentById = fragmentManager.findFragmentById(R.id.fragment_container)

        // Get back stack count
        val backStackCount = fragmentManager.backStackEntryCount

        // Pop back stack
        fragmentManager.popBackStack()

        // Listen to back stack changes
        fragmentManager.addOnBackStackChangedListener {
            Log.d("FragmentManager", "Back stack changed")
        }
    }
}
```

### FragmentTransaction

Performs fragment operations as a transaction.

```kotlin
class MainActivity : AppCompatActivity() {

    fun showFragment() {
        // 1. Get FragmentManager
        val fragmentManager = supportFragmentManager

        // 2. Begin transaction
        val transaction: FragmentTransaction = fragmentManager.beginTransaction()

        // 3. Perform operations
        val fragment = MyFragment()
        transaction.add(R.id.fragment_container, fragment, "MY_FRAGMENT")
        transaction.addToBackStack("fragment_added")

        // 4. Commit transaction
        transaction.commit()
    }
}
```

### FragmentTransaction Operations

```kotlin
class FragmentOperations : AppCompatActivity() {

    fun demonstrateOperations() {
        val fragmentManager = supportFragmentManager

        fragmentManager.beginTransaction().apply {
            // Add fragment
            add(R.id.container, Fragment1(), "FRAGMENT_1")

            // Replace fragment
            replace(R.id.container, Fragment2(), "FRAGMENT_2")

            // Remove fragment
            val fragment = fragmentManager.findFragmentByTag("FRAGMENT_1")
            fragment?.let { remove(it) }

            // Show/hide fragments
            show(fragmentManager.findFragmentByTag("FRAGMENT_2")!!)
            hide(fragmentManager.findFragmentByTag("FRAGMENT_3")!!)

            // Attach/detach
            detach(fragmentManager.findFragmentByTag("FRAGMENT_4")!!)
            attach(fragmentManager.findFragmentByTag("FRAGMENT_4")!!)

            // Add to back stack
            addToBackStack("operation_name")

            // Set animations
            setCustomAnimations(
                R.anim.slide_in_right,
                R.anim.slide_out_left,
                R.anim.slide_in_left,
                R.anim.slide_out_right
            )

            // Set transition
            setTransition(FragmentTransaction.TRANSIT_FRAGMENT_FADE)

            // Commit
            commit()
        }
    }
}
```

### Commit Methods

```kotlin
// Regular commit - asynchronous, scheduled on main thread
transaction.commit()

// Commit immediately on main thread
transaction.commitNow()

// Safe commit - won't throw exception if state is saved
transaction.commitAllowingStateLoss()

// Commit after onSaveInstanceState
transaction.commitNowAllowingStateLoss()
```

### Comparison

| FragmentManager | FragmentTransaction |
|----------------|---------------------|
| Manages fragments | Performs operations |
| Finds fragments | Adds/removes fragments |
| Handles back stack | Adds to back stack |
| Singleton per activity | Created per operation |
| Always available | Created via beginTransaction() |
| Query operations | Modify operations |

## Ответ (RU)

FragmentManager управляет фрагментами: добавление, поиск, стек возврата. FragmentTransaction используется для выполнения операций с фрагментами (добавление, замена, удаление). Это как транзакция базы данных применяемая к UI. Transaction создаётся через FragmentManager.beginTransaction() и применяется через commit()

---

## Related Questions

### Prerequisites (Easier)
- [[q-how-to-choose-layout-for-fragment--android--easy]] - Fragment
- [[q-how-to-display-two-identical-fragments-on-the-screen-at-the-same-time--android--easy]] - Fragment

### Related (Medium)
- [[q-save-data-outside-fragment--android--medium]] - Fragment
- [[q-v-chyom-raznitsa-mezhdu-fragmentmanager-i-fragmenttransaction--programming-languages--medium]] - Fragment
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Fragment
- [[q-can-state-loss-be-related-to-a-fragment--android--medium]] - Fragment
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Fragment

### Advanced (Harder)
- [[q-fragments-history-and-purpose--android--hard]] - Fragment
- [[q-why-fragment-needs-separate-callback-for-ui-creation--android--hard]] - Fragment
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Fragment
