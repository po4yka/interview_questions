---
id: android-418
title: "In What Cases Might You Need To Call Commitallowingstateloss / В каких случаях может понадобиться commitAllowingStateLoss"
aliases: [commitAllowingStateLoss, commitAllowingStateLoss vs commit, commitAllowingStateLoss в Android, Fragment state loss]
topic: android
subtopics: [fragment, lifecycle]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-fragments-and-activity-relationship--android--hard, q-how-can-data-be-saved-beyond-the-fragment-scope--android--medium, q-why-diffutil-needed--android--medium]
created: 2025-10-15
updated: 2025-10-31
sources: []
tags: [android/fragment, android/lifecycle, difficulty/hard, fragments, lifecycle]
---

# Вопрос (RU)

> В каких случаях может понадобиться вызывать commitAllowingStateLoss?

# Question (EN)

> In what cases might you need to call commitAllowingStateLoss?

---

## Ответ (RU)

**Метод**: `commitAllowingStateLoss()` выполняет транзакции фрагментов даже после сохранения состояния активности.

**Когда использовать**:

### 1. Критические Операции
Операции, которые должны выполниться немедленно:

```kotlin
class NotificationHandler {
    fun handleNotification(activity: FragmentActivity) {
        // ✅ Уведомление требует немедленного отображения
        activity.supportFragmentManager.beginTransaction()
            .replace(R.id.container, NotificationFragment())
            .commitAllowingStateLoss()
    }
}
```

### 2. Закрытие Диалогов
Dismiss диалогов при паузе активности:

```kotlin
override fun onPause() {
    super.onPause()
    // ✅ Диалог будет пересоздан при restore если нужен
    dialogFragment?.dismissAllowingStateLoss()
}
```

### 3. Фоновые Процессы
Background задачи, которые обновляют UI:

```kotlin
class DataSyncManager(private val activity: FragmentActivity) {
    fun onSyncCompleted() {
        activity.runOnUiThread {
            // ✅ Активность может быть в любом состоянии
            activity.supportFragmentManager.beginTransaction()
                .replace(R.id.container, SyncResultFragment())
                .commitAllowingStateLoss()
        }
    }
}
```

**Проблема**: `commit()` вызывает `IllegalStateException` после `onSaveInstanceState()`:

```kotlin
// ❌ Исключение если состояние сохранено
supportFragmentManager.beginTransaction()
    .replace(R.id.container, MyFragment())
    .commit()

// ✅ Выполнится, но транзакция может потеряться
supportFragmentManager.beginTransaction()
    .replace(R.id.container, MyFragment())
    .commitAllowingStateLoss()
```

**Что теряется**:
- Транзакция не будет в `savedInstanceState`
- Back stack запись исчезнет
- При recreate activity восстановится предыдущее состояние

**Лучшие альтернативы**:

```kotlin
// 1. Lifecycle-aware navigation
viewModel.navigationEvent.observe(this) { fragment ->
    // ✅ Работает только когда lifecycle STARTED
    supportFragmentManager.beginTransaction()
        .replace(R.id.container, fragment)
        .commit()
}

// 2. Navigation Component
findNavController().navigate(R.id.action_to_detail)

// 3. Post до onPostResume
override fun onPostResume() {
    super.onPostResume()
    // ✅ Активность полностью resumed
    supportFragmentManager.beginTransaction()
        .replace(R.id.container, MyFragment())
        .commit()
}
```

**Когда НЕ использовать**:
- ❌ Пользовательские данные (формы, input)
- ❌ Критическая навигация
- ❌ Транзакции с side effects (DB, API)

**Best practice**:

```kotlin
class MainActivity : AppCompatActivity() {
    private var isStateSaved = false

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        isStateSaved = true
    }

    override fun onResumeFragments() {
        super.onResumeFragments()
        isStateSaved = false
    }

    fun commitSafely(fragment: Fragment) {
        val transaction = supportFragmentManager.beginTransaction()
            .replace(R.id.container, fragment)

        if (isStateSaved) {
            transaction.commitAllowingStateLoss()
        } else {
            transaction.commit()
        }
    }
}
```

## Answer (EN)

**Method**: `commitAllowingStateLoss()` executes fragment transactions even after activity state has been saved.

**When to use**:

### 1. Critical Operations
Operations that must execute immediately:

```kotlin
class NotificationHandler {
    fun handleNotification(activity: FragmentActivity) {
        // ✅ Notification requires immediate display
        activity.supportFragmentManager.beginTransaction()
            .replace(R.id.container, NotificationFragment())
            .commitAllowingStateLoss()
    }
}
```

### 2. Dismissing Dialogs
Close dialogs when activity is pausing:

```kotlin
override fun onPause() {
    super.onPause()
    // ✅ Dialog will be recreated on restore if needed
    dialogFragment?.dismissAllowingStateLoss()
}
```

### 3. Background Processes
Background tasks updating UI:

```kotlin
class DataSyncManager(private val activity: FragmentActivity) {
    fun onSyncCompleted() {
        activity.runOnUiThread {
            // ✅ Activity might be in any state
            activity.supportFragmentManager.beginTransaction()
                .replace(R.id.container, SyncResultFragment())
                .commitAllowingStateLoss()
        }
    }
}
```

**Problem**: `commit()` throws `IllegalStateException` after `onSaveInstanceState()`:

```kotlin
// ❌ Exception if state is saved
supportFragmentManager.beginTransaction()
    .replace(R.id.container, MyFragment())
    .commit()

// ✅ Will execute, but transaction may be lost
supportFragmentManager.beginTransaction()
    .replace(R.id.container, MyFragment())
    .commitAllowingStateLoss()
```

**What gets lost**:
- Transaction won't be in `savedInstanceState`
- Back stack entry will disappear
- On activity recreate, previous state is restored

**Better alternatives**:

```kotlin
// 1. Lifecycle-aware navigation
viewModel.navigationEvent.observe(this) { fragment ->
    // ✅ Only works when lifecycle is STARTED
    supportFragmentManager.beginTransaction()
        .replace(R.id.container, fragment)
        .commit()
}

// 2. Navigation Component
findNavController().navigate(R.id.action_to_detail)

// 3. Post until onPostResume
override fun onPostResume() {
    super.onPostResume()
    // ✅ Activity is fully resumed
    supportFragmentManager.beginTransaction()
        .replace(R.id.container, MyFragment())
        .commit()
}
```

**When NOT to use**:
- ❌ User data (forms, input)
- ❌ Critical navigation
- ❌ Transactions with side effects (DB, API)

**Best practice**:

```kotlin
class MainActivity : AppCompatActivity() {
    private var isStateSaved = false

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        isStateSaved = true
    }

    override fun onResumeFragments() {
        super.onResumeFragments()
        isStateSaved = false
    }

    fun commitSafely(fragment: Fragment) {
        val transaction = supportFragmentManager.beginTransaction()
            .replace(R.id.container, fragment)

        if (isStateSaved) {
            transaction.commitAllowingStateLoss()
        } else {
            transaction.commit()
        }
    }
}
```

---

## Follow-ups

- What happens if you call `commit()` after `onSaveInstanceState()`?
- How does Navigation Component handle state saving?
- Can you queue transactions for later execution?
- What's the difference between `commitNow()` and `commitAllowingStateLoss()`?
- How to check if activity state has been saved?

## References

- [[c-fragments]]
- [[c-activity-lifecycle]]
- Android `Fragment` documentation
- `Fragment` transactions best practices

## Related Questions

### Prerequisites (Easier)
- [[q-fragments-and-activity-relationship--android--hard]]
- [[q-how-can-data-be-saved-beyond-the-fragment-scope--android--medium]]

### Related (Same Level)
- [[q-why-diffutil-needed--android--medium]]

### Advanced (Harder)
- `Fragment` lifecycle with configuration changes
- State restoration strategies
