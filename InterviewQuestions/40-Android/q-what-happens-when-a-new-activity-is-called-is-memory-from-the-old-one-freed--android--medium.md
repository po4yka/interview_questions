---
topic: android
tags:
  - android
difficulty: medium
status: draft
---

# What happens when a new Activity is called? Is memory from the old one freed?

## Answer

When a new Activity is called, the old Activity does **not** immediately have its memory freed. Instead, it goes through lifecycle transitions and stays in the back stack. The system may free its memory later under memory pressure.

### What Happens When New Activity Starts

```kotlin
// Activity A (currently visible)
class ActivityA : AppCompatActivity() {

    fun startActivityB() {
        val intent = Intent(this, ActivityB::class.java)
        startActivity(intent)

        // What happens now:
        // 1. ActivityA.onPause() is called
        // 2. ActivityB is created and started
        // 3. ActivityA.onStop() is called
        // 4. ActivityA remains in memory (back stack)
    }

    override fun onPause() {
        super.onPause()
        Log.d("ActivityA", "onPause - losing focus")
        // Activity A is still partially visible
        // Still in memory
    }

    override fun onStop() {
        super.onStop()
        Log.d("ActivityA", "onStop - no longer visible")
        // Activity A is no longer visible
        // Still in memory (in back stack)
        // Memory MAY be freed by system if needed
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("ActivityA", "onDestroy - being destroyed")
        // Only called if:
        // - finish() was called
        // - System needs memory
        // - User pressed back on last activity
    }
}
```

### Lifecycle Sequence

```
Before: Activity A is running (RESUMED state)
      ↓
User starts Activity B
      ↓
Activity A: onPause()     ← A loses focus, still visible
      ↓
Activity B: onCreate()
Activity B: onStart()
Activity B: onResume()    ← B now has focus
      ↓
Activity A: onStop()      ← A no longer visible
      ↓
Current state:
- Activity B: RESUMED (foreground, interactive)
- Activity A: STOPPED (background, in back stack, in memory)
```

### Memory State

```kotlin
class ActivityA : AppCompatActivity() {

    // These objects remain in memory when Activity is stopped
    private val largeData = ByteArray(1024 * 1024) // 1MB
    private lateinit var viewModel: MyViewModel
    private var userScore: Int = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // All these are created and stored in memory
    }

    override fun onStop() {
        super.onStop()
        // ✅ Activity instance still in memory
        // ✅ All member variables still exist
        // ✅ largeData still allocated
        // ✅ viewModel still exists
        // ✅ userScore value preserved
    }

    // ❌ onDestroy() NOT called yet
    // Memory NOT freed automatically
}
```

### Back Stack Behavior

```kotlin
// Scenario: A → B → C

// 1. User starts app
class ActivityA : AppCompatActivity() {
    fun goToB() {
        startActivity(Intent(this, ActivityB::class.java))
        // A moves to STOPPED state
        // A stays in back stack
    }
}

// 2. From B, start C
class ActivityB : AppCompatActivity() {
    fun goToC() {
        startActivity(Intent(this, ActivityC::class.java))
        // B moves to STOPPED state
        // B stays in back stack
    }
}

// Current back stack:
// [ActivityA - STOPPED] ← bottom
// [ActivityB - STOPPED]
// [ActivityC - RESUMED] ← top
//
// All three Activities are in memory!
```

### When Memory IS Freed

#### Scenario 1: User Presses Back

```kotlin
class ActivityC : AppCompatActivity() {
    // User presses back button

    // Lifecycle:
    // onPause()
    // onStop()
    // onDestroy()  ← Activity C destroyed, memory freed

    override fun onDestroy() {
        super.onDestroy()
        // Memory is being freed
        // All member variables will be garbage collected
    }
}

// After back press:
// [ActivityA - STOPPED]
// [ActivityB - RESUMED] ← comes back to foreground
// ActivityC - DESTROYED ← memory freed
```

#### Scenario 2: finish() Is Called

```kotlin
class ActivityB : AppCompatActivity() {

    fun completeTask() {
        // Finish this Activity programmatically
        finish()

        // Lifecycle immediately:
        // onPause()
        // onStop()
        // onDestroy() ← Memory freed
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("ActivityB", "Memory being freed")
    }
}
```

#### Scenario 3: System Needs Memory

```kotlin
class ActivityA : AppCompatActivity() {

    override fun onStop() {
        super.onStop()
        // Activity in background

        // If system needs memory:
        // - May call onDestroy() and kill this Activity
        // - State saved via onSaveInstanceState()
        // - Memory freed
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        // Save critical state
        outState.putInt("user_score", userScore)

        // System may kill Activity after this
    }

    override fun onDestroy() {
        super.onDestroy()

        if (isFinishing) {
            Log.d("ActivityA", "Finishing normally")
        } else {
            Log.d("ActivityA", "Killed by system for memory")
        }
    }
}
```

### Memory Pressure Scenario

```kotlin
// Low memory situation

Back Stack:
[Activity A - STOPPED] ← May be killed for memory
[Activity B - STOPPED] ← May be killed for memory
[Activity C - STOPPED] ← May be killed for memory
[Activity D - RESUMED] ← Safe, in foreground

// System kills from oldest (bottom) first
// Activity A likely killed first
// onDestroy() called
// Memory freed
// State saved in Bundle

// When user navigates back to A:
// - New instance created
// - onCreate(savedInstanceState) called with saved state
// - State restored
```

### Checking if Activity Is Finishing

```kotlin
class MyActivity : AppCompatActivity() {

    override fun onDestroy() {
        super.onDestroy()

        if (isFinishing) {
            // User pressed back or finish() was called
            // Activity permanently destroyed
            Log.d("Activity", "Finishing - permanent")
            cleanupResources()
        } else {
            // System killed for memory
            // May be recreated later
            Log.d("Activity", "Killed by system - may recreate")
            // Don't do permanent cleanup
        }
    }

    private fun cleanupResources() {
        // Close database connections
        // Cancel network requests
        // Unregister listeners
    }
}
```

### Memory Optimization

```kotlin
class MemoryEfficientActivity : AppCompatActivity() {

    private var heavyObject: LargeDataSet? = null

    override fun onStop() {
        super.onStop()

        // ✅ Release heavy resources when not visible
        heavyObject = null

        // Suggest garbage collection (not guaranteed)
        System.gc()
    }

    override fun onStart() {
        super.onStart()

        // ✅ Recreate heavy resources when visible again
        if (heavyObject == null) {
            heavyObject = loadLargeDataSet()
        }
    }

    override fun onDestroy() {
        super.onDestroy()

        // ✅ Final cleanup
        heavyObject = null
    }
}
```

### ViewModel Survival

```kotlin
class MyViewModel : ViewModel() {
    val data = MutableLiveData<String>()

    override fun onCleared() {
        super.onCleared()
        // Only called when Activity is FINISHED
        // Not called when Activity is just stopped
    }
}

class MyActivity : AppCompatActivity() {

    private val viewModel: MyViewModel by viewModels()

    // Sequence when new Activity starts:
    // 1. onPause()
    // 2. onStop()
    // ViewModel.onCleared() NOT called ← ViewModel survives!

    // ViewModel only cleared when:
    // - finish() is called
    // - User presses back (last activity)
    // NOT when system kills for memory
}
```

### Memory States Summary

| State | Activity Lifecycle | Memory Status | Can Be Killed |
|-------|-------------------|---------------|---------------|
| Created | onCreate() → onStart() | Allocated | No |
| Resumed | onResume() | In use, foreground | No |
| Paused | onPause() | In use, visible | No (rare) |
| Stopped | onStop() | In memory, background | Yes |
| Destroyed | onDestroy() | Freed/being freed | N/A |

### Best Practices

```kotlin
class BestPracticeActivity : AppCompatActivity() {

    private var bitmap: Bitmap? = null
    private lateinit var disposables: CompositeDisposable

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        disposables = CompositeDisposable()
    }

    override fun onStop() {
        super.onStop()

        // ✅ Release memory-heavy resources
        bitmap?.recycle()
        bitmap = null

        // ✅ Cancel background operations
        disposables.clear()
    }

    override fun onDestroy() {
        super.onDestroy()

        // ✅ Final cleanup
        disposables.dispose()
    }

    // ✅ Use ViewModel for data that should survive
    private val viewModel: DataViewModel by viewModels()

    // ✅ Save critical state
    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putString("critical_data", criticalData)
    }
}
```

### Summary

When a new Activity is called:
1. **Old Activity is paused** (onPause)
2. **New Activity starts** (onCreate → onStart → onResume)
3. **Old Activity is stopped** (onStop)
4. **Old Activity stays in memory** (in back stack)
5. **Memory is NOT immediately freed**

Memory is freed when:
- User presses **back** (onDestroy called)
- **finish()** is called
- **System needs memory** (may kill stopped Activities)

The old Activity **remains in memory in the back stack** until explicitly finished or killed by the system for memory.

## Answer (RU)
Нет, старая Activity:

## Related Topics
- Activity lifecycle
- Back stack
- onSaveInstanceState
- ViewModel lifecycle
- Memory management
- Process death
