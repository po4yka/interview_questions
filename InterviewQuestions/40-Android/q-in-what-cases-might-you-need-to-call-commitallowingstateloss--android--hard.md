---
id: "20251015082238633"
title: "In What Cases Might You Need To Call Commitallowingstateloss / В каких случаях может понадобиться commitAllowingStateLoss"
topic: android
difficulty: hard
status: draft
created: 2025-10-15
tags: [android/fragments, fragments, lifecycle, ui, difficulty/hard]
---
# В каких случаях может понадобиться вызывать commitAllowingStateLoss

**English**: In what cases might you need to call commitAllowingStateLoss

## Answer (EN)
The **`commitAllowingStateLoss()`** method in Android is used to execute fragment transactions even when the activity state has already been saved. It can be useful but should be used with caution as it may lead to state loss.

### Understanding the Problem

When you try to commit a fragment transaction after `onSaveInstanceState()` has been called, you'll get an `IllegalStateException`:

```
java.lang.IllegalStateException: Can not perform this action after onSaveInstanceState
```

This happens because:
1. Activity calls `onSaveInstanceState()` before being paused or stopped
2. The system saves the current fragment state
3. Any fragment transactions after this point won't be saved
4. This could lead to state inconsistency on activity recreation

### commit() vs commitAllowingStateLoss()

```kotlin
// Regular commit - throws exception if state is saved
supportFragmentManager.beginTransaction()
    .replace(R.id.container, MyFragment())
    .commit()

// Allows committing after state saved - may lose transaction state
supportFragmentManager.beginTransaction()
    .replace(R.id.container, MyFragment())
    .commitAllowingStateLoss()
```

### Use Cases

#### 1. User Navigation with Low Probability of Rollback

When the user performs an action that should complete regardless of activity state:

```kotlin
class MainActivity : AppCompatActivity() {

    fun onUserClickedButton() {
        // User explicitly requested this action
        // Even if activity is in the process of being destroyed,
        // we want to show this fragment
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, ResultFragment())
            .commitAllowingStateLoss()
    }
}
```

#### 2. Operations That Must Execute Immediately

For critical operations that cannot be delayed:

```kotlin
class NotificationHandler {

    fun handleNotification(activity: FragmentActivity, data: NotificationData) {
        // Notification requires immediate display
        // We accept potential state loss for immediacy
        activity.supportFragmentManager.beginTransaction()
            .replace(R.id.container, NotificationFragment.newInstance(data))
            .commitAllowingStateLoss()
    }
}
```

#### 3. Removing DialogFragment

Dismissing dialogs that might need to close urgently:

```kotlin
class MyDialogFragment : DialogFragment() {

    fun dismissSafely() {
        // Dismiss even if activity state is saved
        // Dialog will be recreated on restore if needed
        dismissAllowingStateLoss()
    }
}

// Usage
override fun onPause() {
    super.onPause()
    // Close dialog when activity is pausing
    dialogFragment?.dismissAllowingStateLoss()
}
```

#### 4. Automatic Processes or System Changes

Background tasks or system events that trigger fragment changes:

```kotlin
class DataSyncManager(private val activity: FragmentActivity) {

    fun onDataSyncCompleted() {
        // Background sync completed, show result
        // Activity might be in any state
        activity.runOnUiThread {
            activity.supportFragmentManager.beginTransaction()
                .replace(R.id.container, SyncResultFragment())
                .commitAllowingStateLoss()
        }
    }
}
```

#### 5. Fixing Configuration Change Bugs

Handling fragment transactions during configuration changes:

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Safe to use during onCreate after setContentView
        if (savedInstanceState == null) {
            supportFragmentManager.beginTransaction()
                .add(R.id.container, HomeFragment())
                .commitAllowingStateLoss()
        }
    }
}
```

### Better Alternatives

Before using `commitAllowingStateLoss()`, consider these alternatives:

#### 1. Use commitNow() or executePendingTransactions()

```kotlin
// For synchronous execution before state save
try {
    supportFragmentManager.beginTransaction()
        .replace(R.id.container, MyFragment())
        .commitNow()
} catch (e: IllegalStateException) {
    // Handle gracefully
}
```

#### 2. Use Lifecycle-Aware Components

```kotlin
class MyViewModel : ViewModel() {
    private val _navigationEvent = MutableLiveData<Event<Fragment>>()
    val navigationEvent: LiveData<Event<Fragment>> = _navigationEvent

    fun navigateToFragment(fragment: Fragment) {
        _navigationEvent.value = Event(fragment)
    }
}

class MainActivity : AppCompatActivity() {
    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.navigationEvent.observe(this) { event ->
            event.getContentIfNotHandled()?.let { fragment ->
                // Safe because observe() only works when lifecycle is STARTED
                supportFragmentManager.beginTransaction()
                    .replace(R.id.container, fragment)
                    .commit()
            }
        }
    }
}

// Event wrapper to prevent duplicate handling
class Event<out T>(private val content: T) {
    private var hasBeenHandled = false

    fun getContentIfNotHandled(): T? {
        return if (hasBeenHandled) {
            null
        } else {
            hasBeenHandled = true
            content
        }
    }
}
```

#### 3. Use Navigation Component

```kotlin
// build.gradle
dependencies {
    implementation "androidx.navigation:navigation-fragment-ktx:2.7.0"
}

// Safe navigation with Navigation Component
class MyFragment : Fragment() {
    fun navigateToDetail() {
        // Navigation Component handles state saving automatically
        findNavController().navigate(R.id.action_to_detail)
    }
}
```

#### 4. Post Transaction After State Restore

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onPostResume() {
        super.onPostResume()
        // Safe to commit here - activity is fully resumed
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, MyFragment())
            .commit()
    }
}
```

### Understanding State Loss

What gets lost with `commitAllowingStateLoss()`:

```kotlin
// This transaction won't be in savedInstanceState
supportFragmentManager.beginTransaction()
    .replace(R.id.container, MyFragment())
    .addToBackStack("my_transaction")
    .commitAllowingStateLoss()

// If activity is recreated immediately after:
// 1. MyFragment won't be restored
// 2. Back stack entry won't exist
// 3. Previous fragment state is restored instead
```

### Best Practices

#### 1. Document Why You're Using It

```kotlin
/**
 * Dismisses dialog allowing state loss.
 * State loss is acceptable here because:
 * - Dialog will be recreated on activity restore if still needed
 * - This prevents IllegalStateException on activity pause
 */
fun dismissDialogSafely() {
    dialogFragment?.dismissAllowingStateLoss()
}
```

#### 2. Check If State Is Saved

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

    fun commitFragmentSafely(fragment: Fragment) {
        if (isStateSaved) {
            // Queue transaction for later or use commitAllowingStateLoss
            supportFragmentManager.beginTransaction()
                .replace(R.id.container, fragment)
                .commitAllowingStateLoss()
        } else {
            // Normal commit
            supportFragmentManager.beginTransaction()
                .replace(R.id.container, fragment)
                .commit()
        }
    }
}
```

#### 3. Prefer Navigation Component

```xml
<!-- nav_graph.xml -->
<navigation>
    <fragment
        android:id="@+id/homeFragment"
        android:name="com.example.HomeFragment">
        <action
            android:id="@+id/action_to_detail"
            app:destination="@id/detailFragment" />
    </fragment>
</navigation>
```

```kotlin
// Safe navigation - no state loss concerns
findNavController().navigate(R.id.action_to_detail)
```

### When NOT to Use

**Avoid using `commitAllowingStateLoss()` when:**

1. **User data is involved** - Users expect their actions to be preserved
2. **Form state** - Losing form input is frustrating
3. **Critical navigation** - Important app flows should be preserved
4. **Transaction has side effects** - Database changes, API calls tied to transaction

```kotlin
// BAD - Don't lose user's form data
fun saveUserForm() {
    supportFragmentManager.beginTransaction()
        .replace(R.id.container, FormFragment())
        .commitAllowingStateLoss()  // User data might be lost!
}

// GOOD - Use proper lifecycle handling
fun saveUserForm() {
    lifecycleScope.launch {
        whenResumed {
            supportFragmentManager.beginTransaction()
                .replace(R.id.container, FormFragment())
                .commit()
        }
    }
}
```

### Summary

Use `commitAllowingStateLoss()` when:
1. User navigation is unlikely to be rolled back
2. Operations must execute immediately regardless of state
3. Dismissing dialogs on pause/stop
4. Automatic background processes update UI
5. Configuration change handling where state loss is acceptable

**Better alternatives:**
1. `commitNow()` for synchronous execution
2. Lifecycle-aware components (LiveData, ViewModel)
3. Navigation Component for safe navigation
4. Post transactions to `onPostResume()`

**Key principle:** Only use when you understand and accept the consequences of potential state loss.

## Ответ (RU)
Метод commitAllowingStateLoss() в Android используется для выполнения транзакций фрагментов даже когда состояние активности уже сохранено. Он может быть полезен но следует использовать с осторожностью так как может привести к потере состояния. Рассмотрены ситуации: пользовательская навигация с малой вероятностью возврата операции которые должны быть выполнены немедленно автоматические процессы или системные изменения устранение багов при смене конфигурации. Примеры использования включают переход между фрагментами удаление диалогового фрагмента. Метод позволяет избежать ошибки IllegalStateException при пересоздании активности но с риском потери состояния.

