---
id: "20251003141516"
title: "How to add fragment synchronously/asynchronously?"
slug: "kak-dobavit-fragment-sinhronno-asinhronno"
topic: "android"
moc: "moc-android"
difficulty: "hard"
status: "draft"
tags:
  - android
  - ui
  - fragments
  - asynchronous
  - threading
date: "2025-10-03"
source: "https://t.me/easy_kotlin/972"
---

# How to add fragment synchronously/asynchronously?

## EN (expanded)

### Asynchronous (Default and Recommended)

The standard way to add a fragment is **asynchronous** using `commit()`:

```kotlin
supportFragmentManager.beginTransaction()
    .add(R.id.fragment_container, MyFragment())
    .commit()
// Executes asynchronously on main thread
// Scheduled to run before next frame
```

**Characteristics:**
- Executes before next frame draw
- Non-blocking
- Can be called from any point in activity lifecycle
- Recommended for most cases
- Changes may not be immediate

### Synchronous (Immediate)

For immediate execution, use `commitNow()`:

```kotlin
supportFragmentManager.beginTransaction()
    .add(R.id.fragment_container, MyFragment())
    .commitNow()
// Executes immediately, synchronously
// Blocks until transaction completes
```

**Characteristics:**
- Executes immediately
- Blocks calling thread
- Cannot be used with `addToBackStack()`
- Used rarely (setup methods, testing)
- Changes are immediate

### Comparison

```kotlin
class FragmentTransactionExample : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // ASYNCHRONOUS (default)
        supportFragmentManager.beginTransaction()
            .add(R.id.container, Fragment1())
            .commit()

        // Fragment not yet added here!
        val fragment = supportFragmentManager.findFragmentById(R.id.container)
        println("Fragment: $fragment") // null

        // Execute pending transactions
        supportFragmentManager.executePendingTransactions()
        val fragmentAfter = supportFragmentManager.findFragmentById(R.id.container)
        println("Fragment after: $fragmentAfter") // Fragment1

        // SYNCHRONOUS
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, Fragment2())
            .commitNow()

        // Fragment immediately available
        val fragment2 = supportFragmentManager.findFragmentById(R.id.container)
        println("Fragment2: $fragment2") // Fragment2
    }
}
```

### Asynchronous Methods

#### 1. commit() - Standard Async

```kotlin
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment())
    .addToBackStack("my_fragment")
    .commit()

// Can be called anytime
// Executes before next frame
```

#### 2. commitAllowingStateLoss() - Async, Allows State Loss

```kotlin
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment())
    .commitAllowingStateLoss()

// Like commit() but won't throw exception
// if activity state is already saved
// Use when state loss is acceptable
```

#### 3. commitNowAllowingStateLoss() - Sync, Allows State Loss

```kotlin
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment())
    .commitNowAllowingStateLoss()

// Immediate execution
// Allows state loss
// Cannot use with back stack
```

### Complete Examples

#### Asynchronous Fragment Addition

```kotlin
class AsyncFragmentActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_container)

        if (savedInstanceState == null) {
            // Add fragment asynchronously
            supportFragmentManager.beginTransaction()
                .add(R.id.fragment_container, HomeFragment(), "home")
                .commit()
        }
    }

    fun navigateToDetails(itemId: String) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.fragment_container, DetailsFragment.newInstance(itemId))
            .addToBackStack("details")
            .commit()
        // Transaction scheduled, not executed yet
    }

    fun getCurrentFragment(): Fragment? {
        // Force execution of pending transactions
        supportFragmentManager.executePendingTransactions()
        return supportFragmentManager.findFragmentById(R.id.fragment_container)
    }
}
```

#### Synchronous Fragment Addition

```kotlin
class SyncFragmentActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_container)

        // Synchronous setup
        setupFragments()

        // Fragments are guaranteed to be added here
        val homeFragment = supportFragmentManager
            .findFragmentByTag("home") as? HomeFragment
        homeFragment?.initialize(data)
    }

    private fun setupFragments() {
        if (supportFragmentManager.findFragmentByTag("home") == null) {
            supportFragmentManager.beginTransaction()
                .add(R.id.fragment_container, HomeFragment(), "home")
                .commitNow()
            // Fragment added immediately
        }
    }

    fun replaceFragmentImmediately() {
        supportFragmentManager.beginTransaction()
            .replace(R.id.fragment_container, DetailsFragment())
            .commitNow()
        // Cannot add to back stack with commitNow()

        // Fragment available immediately
        val detailsFragment = supportFragmentManager
            .findFragmentById(R.id.fragment_container) as DetailsFragment
        detailsFragment.loadData()
    }
}
```

### State Loss Considerations

```kotlin
class StateAwareActivity : AppCompatActivity() {

    fun safeCommit() {
        if (!isStateSaved) {
            supportFragmentManager.beginTransaction()
                .add(R.id.container, MyFragment())
                .commit()
        } else {
            // Activity state saved, can't commit normally
            supportFragmentManager.beginTransaction()
                .add(R.id.container, MyFragment())
                .commitAllowingStateLoss()
            // Or postpone until activity resumed
        }
    }

    private val isStateSaved: Boolean
        get() = supportFragmentManager.isStateSaved
}
```

### Executing Pending Transactions

```kotlin
fun forceExecution() {
    // Queue transaction
    supportFragmentManager.beginTransaction()
        .add(R.id.container, Fragment1())
        .commit()

    // Force immediate execution of all pending transactions
    supportFragmentManager.executePendingTransactions()

    // Now fragment is available
    val fragment = supportFragmentManager.findFragmentById(R.id.container)
}
```

### Best Practices

#### Use commit() for Most Cases

```kotlin
// RECOMMENDED: Async commit
fun addFragment() {
    supportFragmentManager.beginTransaction()
        .add(R.id.container, MyFragment())
        .addToBackStack(null)
        .commit()
}
```

#### Use commitNow() for Setup

```kotlin
// Synchronous for initial setup
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.activity_main)

    if (savedInstanceState == null) {
        supportFragmentManager.beginTransaction()
            .add(R.id.container, HomeFragment())
            .commitNow() // No back stack, immediate
    }
}
```

#### Handle State Loss Properly

```kotlin
override fun onResume() {
    super.onResume()
    // Safe to commit normally
    supportFragmentManager.beginTransaction()
        .add(R.id.container, MyFragment())
        .commit()
}

fun onAsyncCallback() {
    // Activity might be in background
    if (lifecycle.currentState.isAtLeast(Lifecycle.State.RESUMED)) {
        supportFragmentManager.beginTransaction()
            .add(R.id.container, MyFragment())
            .commit()
    } else {
        // Allow state loss or postpone
        supportFragmentManager.beginTransaction()
            .add(R.id.container, MyFragment())
            .commitAllowingStateLoss()
    }
}
```

### Kotlin Extensions

```kotlin
// Extension for safe fragment transactions
fun FragmentManager.commitTransaction(
    allowStateLoss: Boolean = false,
    now: Boolean = false,
    block: FragmentTransaction.() -> Unit
) {
    beginTransaction().apply {
        block()
        when {
            now && allowStateLoss -> commitNowAllowingStateLoss()
            now -> commitNow()
            allowStateLoss -> commitAllowingStateLoss()
            else -> commit()
        }
    }
}

// Usage
supportFragmentManager.commitTransaction {
    add(R.id.container, MyFragment())
    addToBackStack(null)
}

supportFragmentManager.commitTransaction(now = true) {
    replace(R.id.container, OtherFragment())
}
```

### Common Pitfalls

```kotlin
// ❌ BAD: Can't use back stack with commitNow()
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment())
    .addToBackStack(null)
    .commitNow() // IllegalStateException!

// ✅ GOOD: Use commit() with back stack
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment())
    .addToBackStack(null)
    .commit()

// ❌ BAD: Assuming fragment available immediately
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment())
    .commit()
val fragment = supportFragmentManager
    .findFragmentById(R.id.container) // null!

// ✅ GOOD: Execute pending or use commitNow()
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment())
    .commit()
supportFragmentManager.executePendingTransactions()
val fragment = supportFragmentManager
    .findFragmentById(R.id.container) // available
```

### Decision Tree

```
Need to add fragment?
│
├─ Need immediate availability?
│  ├─ Yes → Use commitNow()
│  └─ No → Continue
│
├─ Need back stack?
│  ├─ Yes → Must use commit() (async)
│  └─ No → Continue
│
├─ Activity state might be saved?
│  ├─ Yes → Use commitAllowingStateLoss()
│  └─ No → Use commit()
```

---

## RU (original)

Как добавить фрагмент синхронно / асинхронно

Синхронно: Асинхронно (с отложенным исполнением): commitNow() — выполняется немедленно в текущем потоке. Используется редко (например, в setup-методах).
