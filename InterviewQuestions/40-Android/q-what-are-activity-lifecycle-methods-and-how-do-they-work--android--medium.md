---
id: "20251015082237529"
title: "What Are Activity Lifecycle Methods And How Do They Work / What Are Activity Lifecycle Methods и How Do They Work"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - android
---
# What are Activity lifecycle methods and how do they work?

## Answer (EN)
Activity lifecycle methods are callback functions that the Android system calls at different stages of an Activity's life. Understanding these methods is crucial for proper resource management, state preservation, and creating a smooth user experience.

### The Activity Lifecycle

```

   Activity Launched 

           ↓
     
     onCreate() ← Activity is being created
     
          ↓
     
     onStart()  ← Activity is becoming visible
     
          ↓
     
     onResume()  ← Activity is in foreground and interactive
     
          ↓
   
    Running State
   
          ↓
     
     onPause()  ← Activity is losing focus
     
          ↓
     
     onStop()   ← Activity is no longer visible
     
          ↓
     
     onDestroy()  ← Activity is being destroyed
     
```

### Complete Lifecycle Methods

```kotlin
class MainActivity : AppCompatActivity() {

    // 1. onCreate() - Activity is being created
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("Lifecycle", "onCreate called")

        // Set content view
        setContentView(R.layout.activity_main)

        // Initialize UI components
        setupViews()

        // Restore saved state if exists
        savedInstanceState?.let {
            restoreState(it)
        }

        // One-time initialization
        initializeData()
    }

    // 2. onStart() - Activity is becoming visible
    override fun onStart() {
        super.onStart()
        Log.d("Lifecycle", "onStart called")

        // Start animations, register listeners
        startAnimations()
        registerReceivers()
    }

    // 3. onResume() - Activity is in foreground and interactive
    override fun onResume() {
        super.onResume()
        Log.d("Lifecycle", "onResume called")

        // Resume camera, sensors, location updates
        startCamera()
        startLocationUpdates()

        // Refresh data if needed
        refreshData()
    }

    // 4. onPause() - Activity is losing focus
    override fun onPause() {
        super.onPause()
        Log.d("Lifecycle", "onPause called")

        // Pause camera, sensors, video playback
        pauseCamera()
        pauseVideo()

        // Save critical user data
        saveDraft()

        // Stop expensive operations
        stopLocationUpdates()
    }

    // 5. onStop() - Activity is no longer visible
    override fun onStop() {
        super.onStop()
        Log.d("Lifecycle", "onStop called")

        // Stop animations
        stopAnimations()

        // Unregister listeners
        unregisterReceivers()

        // Save state
        saveState()
    }

    // 6. onDestroy() - Activity is being destroyed
    override fun onDestroy() {
        super.onDestroy()
        Log.d("Lifecycle", "onDestroy called")

        // Clean up resources
        cleanupResources()

        // Cancel coroutines
        cancelBackgroundTasks()

        // Release memory
        releaseMemory()
    }

    // 7. onRestart() - Activity is restarting after being stopped
    override fun onRestart() {
        super.onRestart()
        Log.d("Lifecycle", "onRestart called")

        // Called before onStart() when returning from stopped state
        reloadData()
    }

    // Helper methods
    private fun setupViews() { /* ... */ }
    private fun initializeData() { /* ... */ }
    private fun restoreState(savedInstanceState: Bundle) { /* ... */ }
    private fun startAnimations() { /* ... */ }
    private fun registerReceivers() { /* ... */ }
    private fun startCamera() { /* ... */ }
    private fun startLocationUpdates() { /* ... */ }
    private fun refreshData() { /* ... */ }
    private fun pauseCamera() { /* ... */ }
    private fun pauseVideo() { /* ... */ }
    private fun saveDraft() { /* ... */ }
    private fun stopLocationUpdates() { /* ... */ }
    private fun stopAnimations() { /* ... */ }
    private fun unregisterReceivers() { /* ... */ }
    private fun saveState() { /* ... */ }
    private fun cleanupResources() { /* ... */ }
    private fun cancelBackgroundTasks() { /* ... */ }
    private fun releaseMemory() { /* ... */ }
    private fun reloadData() { /* ... */ }
}
```

### Common Lifecycle Scenarios

#### Scenario 1: App Launch

```
onCreate() → onStart() → onResume() → [Running]
```

#### Scenario 2: User Presses Home Button

```
[Running] → onPause() → onStop() → [Stopped]
```

#### Scenario 3: User Returns to App

```
[Stopped] → onRestart() → onStart() → onResume() → [Running]
```

#### Scenario 4: Screen Rotation

```
onPause() → onStop() → onDestroy() →
onCreate() → onStart() → onResume()
```

#### Scenario 5: Dialog Appears (Activity Still Visible)

```
[Running] → onPause() → [Paused but visible]
```

#### Scenario 6: Another Activity Covers It

```
onPause() → onStop() → [Stopped]
```

### State Saving and Restoration

```kotlin
class DataActivity : AppCompatActivity() {

    private var userInput: String = ""
    private var counter: Int = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_data)

        // Restore state after configuration change
        savedInstanceState?.let {
            userInput = it.getString("USER_INPUT", "")
            counter = it.getInt("COUNTER", 0)
            Log.d("Lifecycle", "Restored: input=$userInput, counter=$counter")
        }

        updateUI()
    }

    // Save state before Activity is destroyed
    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        outState.putString("USER_INPUT", userInput)
        outState.putInt("COUNTER", counter)

        Log.d("Lifecycle", "State saved: input=$userInput, counter=$counter")
    }

    // Restore state after onStart()
    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)

        // Alternative to onCreate restoration
        userInput = savedInstanceState.getString("USER_INPUT", "")
        counter = savedInstanceState.getInt("COUNTER", 0)

        Log.d("Lifecycle", "State restored in onRestoreInstanceState")
    }

    private fun updateUI() {
        findViewById<TextView>(R.id.inputText).text = userInput
        findViewById<TextView>(R.id.counterText).text = "Count: $counter"
    }
}
```

### Lifecycle-Aware Components

Modern Android development uses lifecycle-aware components:

```kotlin
class ModernActivity : AppCompatActivity() {

    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_modern)

        // Observe LiveData - automatically handles lifecycle
        viewModel.userData.observe(this) { user ->
            updateUI(user)
        }

        // Launch coroutine scoped to lifecycle
        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                handleState(state)
            }
        }

        // Observe lifecycle events
        lifecycle.addObserver(MyLifecycleObserver())
    }

    private fun updateUI(user: User) { /* ... */ }
    private fun handleState(state: UiState) { /* ... */ }
}

// Custom lifecycle observer
class MyLifecycleObserver : DefaultLifecycleObserver {

    override fun onCreate(owner: LifecycleOwner) {
        Log.d("Observer", "onCreate")
    }

    override fun onStart(owner: LifecycleOwner) {
        Log.d("Observer", "onStart")
    }

    override fun onResume(owner: LifecycleOwner) {
        Log.d("Observer", "onResume")
    }

    override fun onPause(owner: LifecycleOwner) {
        Log.d("Observer", "onPause")
    }

    override fun onStop(owner: LifecycleOwner) {
        Log.d("Observer", "onStop")
    }

    override fun onDestroy(owner: LifecycleOwner) {
        Log.d("Observer", "onDestroy")
    }
}
```

### Configuration Changes

```kotlin
class ConfigActivity : AppCompatActivity() {

    private var expensiveData: LargeData? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_config)

        // Check if data was retained (deprecated approach)
        @Suppress("DEPRECATION")
        val retained = lastCustomNonConfigurationInstance as? LargeData

        expensiveData = retained ?: loadExpensiveData()
    }

    // Deprecated but shows concept
    @Deprecated("Use ViewModel instead")
    override fun onRetainCustomNonConfigurationInstance(): Any? {
        return expensiveData
    }

    private fun loadExpensiveData(): LargeData {
        // Expensive operation
        return LargeData()
    }
}

// Modern approach: Use ViewModel
class ModernConfigActivity : AppCompatActivity() {

    private val viewModel: DataViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_config)

        // ViewModel survives configuration changes automatically
        val data = viewModel.expensiveData
    }
}

class DataViewModel : ViewModel() {
    // Survives configuration changes
    val expensiveData = loadExpensiveData()

    private fun loadExpensiveData(): LargeData {
        return LargeData()
    }
}

data class LargeData(val items: List<String> = emptyList())
```

### Handling Back Button

```kotlin
class BackHandlingActivity : AppCompatActivity() {

    private val onBackPressedCallback = object : OnBackPressedCallback(true) {
        override fun handleOnBackPressed() {
            // Custom back handling
            if (hasUnsavedChanges()) {
                showSaveDialog()
            } else {
                // Let default back behavior happen
                isEnabled = false
                onBackPressedDispatcher.onBackPressed()
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_back)

        // Modern back handling
        onBackPressedDispatcher.addCallback(this, onBackPressedCallback)
    }

    private fun hasUnsavedChanges(): Boolean = false
    private fun showSaveDialog() { /* ... */ }
}
```

### Lifecycle Method Timing

```kotlin
class TimingActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("Timing", "onCreate: Activity not visible yet")
        // Window not visible
        // Cannot interact with UI
    }

    override fun onStart() {
        super.onStart()
        Log.d("Timing", "onStart: Activity becoming visible")
        // Window becoming visible
        // Still cannot interact
    }

    override fun onResume() {
        super.onResume()
        Log.d("Timing", "onResume: Activity is interactive")
        // Window visible and interactive
        // Can handle user input
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        Log.d("Timing", "onWindowFocusChanged: hasFocus=$hasFocus")
        // Called after onResume() when window gains focus
        // Good place to start animations
        if (hasFocus) {
            startAnimations()
        }
    }

    private fun startAnimations() { /* ... */ }
}
```

### Lifecycle Summary Table

| Method | When Called | Visibility | Interactive | What to Do |
|--------|-------------|------------|-------------|------------|
| onCreate() | Activity created | No | No | Initialize UI, restore state |
| onStart() | Becoming visible | Yes | No | Register receivers, start animations |
| onResume() | In foreground | Yes | Yes | Resume camera, sensors, refresh data |
| onPause() | Losing focus | Yes | No | Pause camera, save drafts |
| onStop() | No longer visible | No | No | Stop animations, save state |
| onDestroy() | Being destroyed | No | No | Clean up resources, cancel tasks |
| onRestart() | Restarting | No | No | Reload data before onStart() |

### Best Practices

1. **Always call super methods first** (except onSaveInstanceState)
2. **Use onCreate() for one-time initialization**
3. **Use onResume()/onPause() for resources tied to visibility**
4. **Save state in onSaveInstanceState()**
5. **Use ViewModel for configuration changes**
6. **Use lifecycle-aware components** (LiveData, lifecycleScope)
7. **Clean up in onDestroy()**
8. **Don't perform long operations** in lifecycle methods
9. **Handle configuration changes properly**
10. **Test all lifecycle scenarios**

### Common Mistakes

```kotlin
// - WRONG: Long operation in onCreate
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    Thread.sleep(5000) // Blocks UI!
}

// - CORRECT: Use background thread
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    lifecycleScope.launch {
        withContext(Dispatchers.IO) {
            loadData()
        }
    }
}

// - WRONG: Not saving state
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    counter = 0 // Lost on configuration change
}

// - CORRECT: Save and restore state
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putInt("counter", counter)
}
```

## Ответ (RU)

Методы жизненного цикла Activity — это колбэк-функции, которые Android система вызывает на разных этапах жизни Activity. Понимание этих методов критически важно для правильного управления ресурсами, сохранения состояния и создания плавного пользовательского опыта.

**Основные методы:**
- **onCreate()** - Activity создана, инициализация UI
- **onStart()** - Activity становится видимой
- **onResume()** - Activity в фокусе и интерактивна
- **onPause()** - Activity теряет фокус
- **onStop()** - Activity больше не видна
- **onDestroy()** - Activity уничтожается
- **onRestart()** - Activity перезапускается после остановки

**Важные моменты:**
- Всегда вызывайте super методы
- Используйте onCreate() для одноразовой инициализации
- Сохраняйте состояние в onSaveInstanceState()
- Используйте ViewModel для конфигурационных изменений
- Очищайте ресурсы в onDestroy()

## Related Topics
- Fragment lifecycle
- ViewModel
- SavedStateHandle
- Configuration changes
- Lifecycle-aware components
- Process death

---

## Related Questions

### Prerequisites (Easier)
- [[q-viewmodel-pattern--android--easy]] - Lifecycle

### Related (Medium)
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Lifecycle, Activity
- [[q-activity-lifecycle-methods--android--medium]] - Lifecycle, Activity
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Lifecycle, Activity
- [[q-how-does-fragment-lifecycle-differ-from-activity-v2--android--medium]] - Lifecycle, Activity
- [[q-how-does-activity-lifecycle-work--android--medium]] - Lifecycle, Activity
