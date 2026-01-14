---
id: android-337
title: How To Add Fragment Synchronously/Asynchronously / Как добавить Fragment синхронно и асинхронно
aliases: [How To Add Fragment Synchronously Asynchronously, Как добавить Fragment синхронно и асинхронно]
topic: android
subtopics: [fragment]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-fragments, q-how-does-jetpackcompose-work--android--medium, q-how-to-choose-layout-for-fragment--android--easy, q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium, q-play-app-signing--android--medium, q-save-data-outside-fragment--android--medium, q-what-unites-the-main-components-of-an-android-application--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android/fragment, difficulty/medium]
anki_cards:
  - slug: android-337-0-en
    front: "What is the difference between commit() and commitNow() for Fragment transactions?"
    back: |
      **Asynchronous (default):**
      - `commit()` - enqueues transaction, executes before next frame
      - `commitAllowingStateLoss()` - same but allows after `onSaveInstanceState()`

      **Synchronous (immediate):**
      - `commitNow()` - executes immediately, blocks thread
      - `commitNowAllowingStateLoss()` - same but allows state loss

      **Key rules:**
      - `commitNow*` cannot use `addToBackStack()`
      - Regular `commit()` after `onSaveInstanceState()` throws `IllegalStateException`
    tags:
      - android_fragments
      - difficulty::medium
  - slug: android-337-0-ru
    front: "В чём разница между commit() и commitNow() для Fragment-транзакций?"
    back: |
      **Асинхронный (по умолчанию):**
      - `commit()` - ставит транзакцию в очередь, выполняет до следующего кадра
      - `commitAllowingStateLoss()` - то же, но разрешает после `onSaveInstanceState()`

      **Синхронный (немедленный):**
      - `commitNow()` - выполняет немедленно, блокирует поток
      - `commitNowAllowingStateLoss()` - то же, но разрешает потерю состояния

      **Ключевые правила:**
      - `commitNow*` нельзя использовать с `addToBackStack()`
      - Обычный `commit()` после `onSaveInstanceState()` выбрасывает `IllegalStateException`
    tags:
      - android_fragments
      - difficulty::medium

---
# Вопрос (RU)
> Как добавить `Fragment` синхронно и асинхронно

# Question (EN)
> How To Add `Fragment` Synchronously/Asynchronously

---

## Ответ (RU)

Фрагменты можно добавлять:
- асинхронно (стандартно, через `commit()` / `commitAllowingStateLoss()`),
- синхронно (немедленно, через `commitNow()` / `commitNowAllowingStateLoss()`).

Ключевые моменты:
- `commit()` и `commitAllowingStateLoss()` ставят транзакцию в очередь и выполняют её асинхронно на главном потоке перед следующим кадром UI.
- `commitNow()` и `commitNowAllowingStateLoss()` выполняют транзакцию немедленно и блокируют поток до завершения.
- Методы `commitNow*` нельзя использовать вместе с `addToBackStack()`.
- После `onSaveInstanceState()` обычный `commit()` может привести к `IllegalStateException`; для таких случаев либо откладывайте транзакцию, либо используйте варианты `*AllowingStateLoss()` (осознанно принимая риск потери состояния).

## Answer (EN)

Fragments can be added:
- asynchronously (standard: `commit()` / `commitAllowingStateLoss()`),
- synchronously (immediately: `commitNow()` / `commitNowAllowingStateLoss()`).

Key points:
- `commit()` and `commitAllowingStateLoss()` enqueue the transaction to be executed asynchronously on the main thread before the next UI frame.
- `commitNow()` and `commitNowAllowingStateLoss()` execute the transaction immediately and block the calling thread until it completes.
- `commitNow*` methods cannot be used with `addToBackStack()`.
- After `onSaveInstanceState()`, a normal `commit()` can throw `IllegalStateException`; in such cases either defer the transaction or use `*AllowingStateLoss()` variants (accepting possible state loss).

## EN (expanded)

### Asynchronous (Default and Recommended)

The standard way to add a fragment is asynchronous using `commit()`:

```kotlin
supportFragmentManager.beginTransaction()
    .add(R.id.fragment_container, MyFragment())
    .commit()
// Enqueued; executed asynchronously on the main thread
// Typically run before the next frame
```

Characteristics:
- Executes before the next frame draw
- Non-blocking
- Cannot be assumed safe after onSaveInstanceState(); may throw IllegalStateException if state is already saved
- Recommended for most in-lifecycle cases (e.g., in onCreate/onResume when state is not yet saved)
- Changes are not immediately visible right after commit() without executing pending transactions

### Synchronous (Immediate)

For immediate execution, use `commitNow()`:

```kotlin
supportFragmentManager.beginTransaction()
    .add(R.id.fragment_container, MyFragment())
    .commitNow()
// Executes immediately, synchronously
// Blocks until transaction completes
```

Characteristics:
- Executes immediately on the calling thread
- Blocks until the transaction is complete
- Cannot be used with `addToBackStack()`
- Used rarely (initial setup, certain tests, or when you must have the fragment immediately)
- Changes are immediately visible after the call

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
        println("Fragment: $fragment") // null (before pending transactions executed)

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

// Enqueued; executes asynchronously before the next frame
// May throw IllegalStateException if called after state is saved
```

#### 2. commitAllowingStateLoss() - Async, Allows State Loss

```kotlin
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment())
    .commitAllowingStateLoss()

// Like commit() but won't throw if state is already saved
// Use only when state loss is acceptable
```

#### 3. commitNowAllowingStateLoss() - Sync, Allows State Loss

```kotlin
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment())
    .commitNowAllowingStateLoss()

// Immediate execution, synchronous
// Allows state loss
// Cannot use with back stack
```

### Complete Examples

#### Asynchronous `Fragment` Addition

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
        // Force execution of pending transactions (use sparingly)
        supportFragmentManager.executePendingTransactions()
        return supportFragmentManager.findFragmentById(R.id.fragment_container)
    }
}
```

#### Synchronous `Fragment` Addition

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
            // Activity state already saved: committing normally may crash
            // Either postpone the transaction or, if acceptable, allow state loss
            supportFragmentManager.beginTransaction()
                .add(R.id.container, MyFragment())
                .commitAllowingStateLoss()
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
// RECOMMENDED: Async commit while state is not yet saved
fun addFragment() {
    supportFragmentManager.beginTransaction()
        .add(R.id.container, MyFragment())
        .addToBackStack(null)
        .commit()
}
```

#### Use commitNow() for Setup

```kotlin
// Synchronous for initial setup, without back stack
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
    // Safe to commit normally (state not yet saved)
    supportFragmentManager.beginTransaction()
        .add(R.id.container, MyFragment())
        .commit()
}

fun onAsyncCallback() {
    // Activity might be in background or state might be saved
    if (lifecycle.currentState.isAtLeast(Lifecycle.State.RESUMED) &&
        !supportFragmentManager.isStateSaved
    ) {
        supportFragmentManager.beginTransaction()
            .add(R.id.container, MyFragment())
            .commit()
    } else {
        // Either postpone, or if UI-only and loss is acceptable, allow state loss
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
    // No back stack when using commitNow()
}
```

### Common Pitfalls

```kotlin
// BAD: Can't use back stack with commitNow()
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment())
    .addToBackStack(null)
    .commitNow() // IllegalStateException!

// GOOD: Use commit() with back stack
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment())
    .addToBackStack(null)
    .commit()

// BAD: Assuming fragment available immediately
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment())
    .commit()
val fragment = supportFragmentManager
    .findFragmentById(R.id.container) // May be null!

// GOOD: Execute pending or use commitNow()
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment())
    .commit()
supportFragmentManager.executePendingTransactions()
val fragment2 = supportFragmentManager
    .findFragmentById(R.id.container) // Now available
```

### Decision Tree

```text
Need to add fragment?

 Need immediate availability?
   Yes → Use commitNow() (no back stack)
   No → Continue

 Need back stack?
   Yes → Use commit() (async)
   No → Continue

 Activity state might be saved / you're after onSaveInstanceState()?
   Yes → Use commitAllowingStateLoss() or commitNowAllowingStateLoss() (if truly acceptable)
   No → Use commit()
```

---

## RU (расширенный)

### Асинхронно (по Умолчанию И Чаще Всего правильно)

Стандартный способ добавить фрагмент — асинхронный через `commit()`:

```kotlin
supportFragmentManager.beginTransaction()
    .add(R.id.fragment_container, MyFragment())
    .commit()
// Транзакция ставится в очередь, выполняется асинхронно на главном потоке
// Обычно выполняется до следующего кадра
```

Характеристики:
- Выполняется до следующего кадра отрисовки
- Не блокирует поток
- Не гарантированно безопасен после `onSaveInstanceState()`; при уже сохранённом состоянии может бросить `IllegalStateException`
- Рекомендуется для большинства случаев внутри нормального жизненного цикла (`onCreate`, `onResume`, когда состояние ещё не сохранено)
- Изменения не гарантированно видны сразу после `commit()` без `executePendingTransactions()`

### Синхронно (немедленно)

Для немедленного выполнения используйте `commitNow()`:

```kotlin
supportFragmentManager.beginTransaction()
    .add(R.id.fragment_container, MyFragment())
    .commitNow()
// Выполняется немедленно и синхронно
// Блокирует поток до завершения транзакции
```

Характеристики:
- Выполняется сразу в вызывающем потоке
- Блокирует поток до завершения
- Нельзя использовать с `addToBackStack()`
- Используется редко (первоначальная инициализация, тесты, ситуации, когда фрагмент нужен прямо сейчас)
- Изменения доступны сразу после вызова

### Сравнение

```kotlin
class FragmentTransactionExample : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // АСИНХРОННО (по умолчанию)
        supportFragmentManager.beginTransaction()
            .add(R.id.container, Fragment1())
            .commit()

        // Фрагмент здесь ещё может не быть добавлен!
        val fragment = supportFragmentManager.findFragmentById(R.id.container)
        println("Fragment: $fragment") // null (до выполнения отложенных транзакций)

        // Выполнить все отложенные транзакции
        supportFragmentManager.executePendingTransactions()
        val fragmentAfter = supportFragmentManager.findFragmentById(R.id.container)
        println("Fragment after: $fragmentAfter") // Fragment1

        // СИНХРОННО
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, Fragment2())
            .commitNow()

        // Фрагмент доступен сразу
        val fragment2 = supportFragmentManager.findFragmentById(R.id.container)
        println("Fragment2: $fragment2") // Fragment2
    }
}
```

### Асинхронные Методы

#### 1. `commit()` — Стандартный Асинхронный

```kotlin
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment())
    .addToBackStack("my_fragment")
    .commit()

// Транзакция ставится в очередь и выполняется асинхронно до следующего кадра
// Может вызвать IllegalStateException, если состояние уже сохранено
```

#### 2. `commitAllowingStateLoss()` — Асинхронно, С Допущением Потери Состояния

```kotlin
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment())
    .commitAllowingStateLoss()

// Как commit(), но не бросает исключение, если состояние уже сохранено
// Использовать только если допустима потеря состояния
```

#### 3. `commitNowAllowingStateLoss()` — Синхронно, С Допущением Потери Состояния

```kotlin
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment())
    .commitNowAllowingStateLoss()

// Немедленное синхронное выполнение
// Допускает потерю состояния
// Нельзя использовать с back stack
```

### Полные Примеры

#### Асинхронное Добавление `Fragment`

```kotlin
class AsyncFragmentActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_container)

        if (savedInstanceState == null) {
            // Асинхронно добавляем фрагмент
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
        // Транзакция запланирована, но ещё не выполнена
    }

    fun getCurrentFragment(): Fragment? {
        // Принудительно выполняем отложенные транзакции (использовать аккуратно)
        supportFragmentManager.executePendingTransactions()
        return supportFragmentManager.findFragmentById(R.id.fragment_container)
    }
}
```

#### Синхронное Добавление `Fragment`

```kotlin
class SyncFragmentActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_container)

        // Синхронная инициализация
        setupFragments()

        // На этом этапе фрагменты уже добавлены
        val homeFragment = supportFragmentManager
            .findFragmentByTag("home") as? HomeFragment
        homeFragment?.initialize(data)
    }

    private fun setupFragments() {
        if (supportFragmentManager.findFragmentByTag("home") == null) {
            supportFragmentManager.beginTransaction()
                .add(R.id.fragment_container, HomeFragment(), "home")
                .commitNow()
            // Фрагмент добавлен немедленно
        }
    }

    fun replaceFragmentImmediately() {
        supportFragmentManager.beginTransaction()
            .replace(R.id.fragment_container, DetailsFragment())
            .commitNow()
        // Нельзя использовать back stack с commitNow()

        // Фрагмент доступен сразу
        val detailsFragment = supportFragmentManager
            .findFragmentById(R.id.fragment_container) as DetailsFragment
        detailsFragment.loadData()
    }
}
```

### Учет Потери Состояния

```kotlin
class StateAwareActivity : AppCompatActivity() {

    fun safeCommit() {
        if (!isStateSaved) {
            supportFragmentManager.beginTransaction()
                .add(R.id.container, MyFragment())
                .commit()
        } else {
            // Состояние Activity уже сохранено: обычный commit может привести к крэшу
            // Либо откладываем транзакцию, либо (если допустимо) разрешаем потерю состояния
            supportFragmentManager.beginTransaction()
                .add(R.id.container, MyFragment())
                .commitAllowingStateLoss()
        }
    }

    private val isStateSaved: Boolean
        get() = supportFragmentManager.isStateSaved
}
```

### Выполнение Отложенных Транзакций

```kotlin
fun forceExecution() {
    // Ставим транзакцию в очередь
    supportFragmentManager.beginTransaction()
        .add(R.id.container, Fragment1())
        .commit()

    // Принудительно выполняем все отложенные транзакции
    supportFragmentManager.executePendingTransactions()

    // Теперь фрагмент доступен
    val fragment = supportFragmentManager.findFragmentById(R.id.container)
}
```

### Рекомендации (Best Practices)

#### Используйте `commit()` В Большинстве Случаев

```kotlin
// РЕКОМЕНДУЕТСЯ: асинхронный commit, пока состояние еще не сохранено
fun addFragment() {
    supportFragmentManager.beginTransaction()
        .add(R.id.container, MyFragment())
        .addToBackStack(null)
        .commit()
}
```

#### Используйте `commitNow()` Для Начальной Настройки

```kotlin
// Синхронно для первичной инициализации без back stack
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.activity_main)

    if (savedInstanceState == null) {
        supportFragmentManager.beginTransaction()
            .add(R.id.container, HomeFragment())
            .commitNow() // Без back stack, немедленно
    }
}
```

#### Правильно Обрабатывайте Возможную Потерю Состояния

```kotlin
override fun onResume() {
    super.onResume()
    // Здесь обычно безопасно вызывать обычный commit
    supportFragmentManager.beginTransaction()
        .add(R.id.container, MyFragment())
        .commit()
}

fun onAsyncCallback() {
    // Колбэк может прийти, когда Activity уже в фоне или состояние сохранено
    if (lifecycle.currentState.isAtLeast(Lifecycle.State.RESUMED) &&
        !supportFragmentManager.isStateSaved
    ) {
        supportFragmentManager.beginTransaction()
            .add(R.id.container, MyFragment())
            .commit()
    } else {
        // Либо откладываем транзакцию, либо, если это только UI и потеря допустима, разрешаем state loss
        supportFragmentManager.beginTransaction()
            .add(R.id.container, MyFragment())
            .commitAllowingStateLoss()
    }
}
```

### Kotlin-расширения

```kotlin
// Универсальное расширение для безопасных транзакций с выбором типа commit
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

// Использование
supportFragmentManager.commitTransaction {
    add(R.id.container, MyFragment())
    addToBackStack(null)
}

supportFragmentManager.commitTransaction(now = true) {
    replace(R.id.container, OtherFragment())
    // Без back stack при commitNow()
}
```

### Частые Ошибки (Common Pitfalls)

```kotlin
// ПЛОХО: использование back stack с commitNow()
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment())
    .addToBackStack(null)
    .commitNow() // IllegalStateException!

// ПРАВИЛЬНО: для back stack использовать commit()
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment())
    .addToBackStack(null)
    .commit()

// ПЛОХО: считать, что фрагмент доступен сразу после commit()
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment())
    .commit()
val fragment = supportFragmentManager
    .findFragmentById(R.id.container) // Может быть null!

// ПРАВИЛЬНО: выполнить отложенные транзакции или использовать commitNow()
supportFragmentManager.beginTransaction()
    .add(R.id.container, MyFragment())
    .commit()
supportFragmentManager.executePendingTransactions()
val fragment2 = supportFragmentManager
    .findFragmentById(R.id.container) // Теперь доступен
```

### Дерево Решений (Decision Tree)

```text
Нужно добавить фрагмент?

 Нужна немедленная доступность?
   Да → Используем commitNow() (без back stack)
   Нет → Дальше

 Нужен back stack?
   Да → Используем commit() (асинхронно)
   Нет → Дальше

 Есть риск, что состояние уже сохранено / вызов после onSaveInstanceState()?
   Да → Используем commitAllowingStateLoss() или commitNowAllowingStateLoss() (только если действительно допустима потеря состояния)
   Нет → Используем commit()
```

---

## Follow-ups

- [[q-how-does-jetpackcompose-work--android--medium]]
- [[q-play-app-signing--android--medium]]
- [[q-what-unites-the-main-components-of-an-android-application--android--medium]]

## References

- [Android Documentation](https://developer.android.com/docs)

## Related Questions

### Prerequisites / Concepts

- [[c-fragments]]

### Prerequisites (Easier)
- [[q-how-to-choose-layout-for-fragment--android--easy]] - `Fragment`
- [[q-fragment-basics--android--easy]] - `Fragment`

### Related (Medium)
- [[q-save-data-outside-fragment--android--medium]] - `Fragment`
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - `Fragment`
- [[q-can-state-loss-be-related-to-a-fragment--android--medium]] - `Fragment`
- [[q-fragment-vs-activity-lifecycle--android--medium]] - `Fragment`
- [[q-how-to-pass-data-from-one-fragment-to-another--android--medium]] - `Fragment`

### Advanced (Harder)
- [[q-why-fragment-needs-separate-callback-for-ui-creation--android--hard]] - `Fragment`
