---
id: 202510031417016
title: "What events are Activity methods tied to"
question_ru: "К каким событиям привязаны методы Activity ?"
question_en: "К каким событиям привязаны методы Activity ?"
topic: android
moc: moc-android
status: draft
difficulty: medium
tags:
  - activity
  - lifecycle
  - android/activity
  - easy_kotlin
  - lang/ru
source: https://t.me/easy_kotlin/469
---

# What events are Activity methods tied to

## English Answer

Activity methods are tied to specific lifecycle events that occur as the Activity transitions through different states. Understanding these event bindings is crucial for proper resource management and application behavior.

### onCreate(Bundle savedInstanceState)

**Event**: Activity creation
**When**: First time Activity is instantiated
**Purpose**: Initial setup

```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.activity_main)

    // Triggered when:
    // - App is launched
    // - Activity is created after being destroyed
    // - Configuration change (screen rotation)

    Log.d("Lifecycle", "onCreate: Activity being created")
}
```

### onStart()

**Event**: Activity becoming visible
**When**: Activity is about to become visible to user
**Purpose**: Prepare UI for user

```kotlin
override fun onStart() {
    super.onStart()

    // Triggered when:
    // - After onCreate()
    // - After onRestart() (returning from stopped state)
    // - Activity transitioning to visible state

    Log.d("Lifecycle", "onStart: Activity becoming visible")
}
```

### onResume()

**Event**: Activity ready for interaction
**When**: Activity is about to start interacting with user
**Purpose**: Start foreground-only behaviors

```kotlin
override fun onResume() {
    super.onResume()

    // Triggered when:
    // - Activity is in foreground
    // - User can interact with Activity
    // - After onStart()
    // - Returning from onPause()

    // Start:
    // - Camera preview
    // - Animations
    // - Sensor listening
    // - Location updates

    Log.d("Lifecycle", "onResume: Activity interactive")
}
```

### onPause()

**Event**: Activity losing focus
**When**: System is about to resume another Activity
**Purpose**: Pause ongoing operations

```kotlin
override fun onPause() {
    super.onPause()

    // Triggered when:
    // - Another Activity comes to foreground (dialog, another app)
    // - Multi-window mode: user switches to other window
    // - Screen is locked
    // - User presses Home button

    // Pause:
    // - Animations
    // - Video playback
    // - Save draft data
    // - Commit unsaved changes

    Log.d("Lifecycle", "onPause: Activity losing focus")
}
```

### onStop()

**Event**: Activity no longer visible
**When**: Activity is completely hidden
**Purpose**: Release resources

```kotlin
override fun onStop() {
    super.onStop()

    // Triggered when:
    // - Another Activity fully covers this one
    // - User navigates away (Home button)
    // - Activity is finishing
    // - Configuration change

    // Stop:
    // - Network requests
    // - Database operations
    // - Release large objects
    // - Unregister broadcast receivers

    Log.d("Lifecycle", "onStop: Activity no longer visible")
}
```

### onRestart()

**Event**: Activity restarting after being stopped
**When**: Activity was stopped and is being started again
**Purpose**: Reinitialize resources

```kotlin
override fun onRestart() {
    super.onRestart()

    // Triggered when:
    // - User returns to app from Home screen
    // - User returns from another Activity
    // - After onStop(), before onStart()

    Log.d("Lifecycle", "onRestart: Activity being restarted")
}
```

### onDestroy()

**Event**: Activity destruction
**When**: Activity is being destroyed
**Purpose**: Final cleanup

```kotlin
override fun onDestroy() {
    super.onDestroy()

    // Triggered when:
    // - finish() is called
    // - System destroys Activity (memory pressure)
    // - Configuration change
    // - User presses Back button

    // Clean up:
    // - Unregister receivers
    // - Stop services
    // - Release all resources
    // - Cancel background tasks

    Log.d("Lifecycle", "onDestroy: Activity being destroyed")
}
```

### onSaveInstanceState(Bundle outState)

**Event**: Before Activity may be destroyed
**When**: System needs to save Activity state
**Purpose**: Save transient state

```kotlin
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)

    // Triggered when:
    // - Configuration change (rotation)
    // - System puts app in background (low memory)
    // - Before onStop() (API 28+)

    // Save:
    // - User input data
    // - Scroll position
    // - Selected items
    // - Any transient UI state

    outState.putString("user_input", editText.text.toString())
    outState.putInt("scroll_position", recyclerView.scrollY)

    Log.d("Lifecycle", "onSaveInstanceState: Saving state")
}
```

### onRestoreInstanceState(Bundle savedInstanceState)

**Event**: After Activity recreation
**When**: Activity is being restored from saved state
**Purpose**: Restore previous state

```kotlin
override fun onRestoreInstanceState(savedInstanceState: Bundle) {
    super.onRestoreInstanceState(savedInstanceState)

    // Triggered when:
    // - After onCreate(), after onStart()
    // - Only when savedInstanceState is not null
    // - After configuration change
    // - After process recreation

    // Restore:
    val userInput = savedInstanceState.getString("user_input", "")
    val scrollPosition = savedInstanceState.getInt("scroll_position", 0)

    editText.setText(userInput)
    recyclerView.scrollTo(0, scrollPosition)

    Log.d("Lifecycle", "onRestoreInstanceState: Restoring state")
}
```

### Complete Event Flow Examples

#### Example 1: App Launch

```
User taps app icon
    ↓
Event: Activity creation
    → onCreate()
    ↓
Event: Activity becoming visible
    → onStart()
    ↓
Event: Activity ready for interaction
    → onResume()
    ↓
[Activity is running and interactive]
```

#### Example 2: User Presses Home

```
User presses Home button
    ↓
Event: Activity losing focus
    → onPause()
    ↓
Event: Activity no longer visible
    → onStop()
    ↓
Event: Save state (in case of process death)
    → onSaveInstanceState()
    ↓
[Activity is stopped, may be destroyed by system]
```

#### Example 3: User Returns to App

```
User returns from Home screen
    ↓
Event: Activity restarting
    → onRestart()
    ↓
Event: Activity becoming visible
    → onStart()
    ↓
Event: Activity ready for interaction
    → onResume()
    ↓
[Activity is running and interactive again]
```

#### Example 4: Screen Rotation

```
User rotates device
    ↓
Event: Configuration change detected
    → onPause()
    → onStop()
    → onSaveInstanceState()
    → onDestroy()
    ↓
[New Activity instance created]
    ↓
Event: Activity recreation
    → onCreate(savedInstanceState)  ← savedInstanceState is NOT null
    → onStart()
    → onRestoreInstanceState(savedInstanceState)
    → onResume()
```

#### Example 5: Back Button Pressed

```
User presses Back button
    ↓
Event: Activity finishing
    → onPause()
    → onStop()
    → onDestroy()
    ↓
[Activity is removed from back stack]
```

### Practical Implementation

```kotlin
class LifecycleExampleActivity : AppCompatActivity() {

    private lateinit var sensor: Sensor
    private lateinit var sensorManager: SensorManager
    private var receiver: BroadcastReceiver? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_example)

        // Event: Activity created
        // Initialize views, setup data
        sensorManager = getSystemService(Context.SENSOR_SERVICE) as SensorManager
        sensor = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)!!

        Log.d("Lifecycle", "onCreate - Initializing")
    }

    override fun onStart() {
        super.onStart()

        // Event: Activity becoming visible
        // Register receivers, start animations
        receiver = object : BroadcastReceiver() {
            override fun onReceive(context: Context?, intent: Intent?) {
                // Handle broadcast
            }
        }
        registerReceiver(receiver, IntentFilter(Intent.ACTION_BATTERY_LOW))

        Log.d("Lifecycle", "onStart - Activity visible")
    }

    override fun onResume() {
        super.onResume()

        // Event: Activity interactive
        // Start foreground operations
        sensorManager.registerListener(
            sensorListener,
            sensor,
            SensorManager.SENSOR_DELAY_NORMAL
        )
        startCameraPreview()
        startAnimations()

        Log.d("Lifecycle", "onResume - Started foreground operations")
    }

    override fun onPause() {
        super.onPause()

        // Event: Losing focus
        // Pause operations, save drafts
        sensorManager.unregisterListener(sensorListener)
        stopCameraPreview()
        pauseAnimations()
        saveDraftData()

        Log.d("Lifecycle", "onPause - Paused operations")
    }

    override fun onStop() {
        super.onStop()

        // Event: No longer visible
        // Release resources
        receiver?.let { unregisterReceiver(it) }
        receiver = null
        stopNetworkRequests()

        Log.d("Lifecycle", "onStop - Released resources")
    }

    override fun onRestart() {
        super.onRestart()

        // Event: Restarting from stopped state
        // Reinitialize if needed
        Log.d("Lifecycle", "onRestart - Restarting")
    }

    override fun onDestroy() {
        super.onDestroy()

        // Event: Activity destroyed
        // Final cleanup
        releaseAllResources()

        Log.d("Lifecycle", "onDestroy - Final cleanup")
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        // Event: Before potential destruction
        // Save UI state
        outState.putString("draft_text", editText.text.toString())
        outState.putInt("selected_position", spinner.selectedItemPosition)

        Log.d("Lifecycle", "onSaveInstanceState - Saved state")
    }

    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)

        // Event: After recreation
        // Restore UI state
        val draftText = savedInstanceState.getString("draft_text", "")
        val selectedPosition = savedInstanceState.getInt("selected_position", 0)

        editText.setText(draftText)
        spinner.setSelection(selectedPosition)

        Log.d("Lifecycle", "onRestoreInstanceState - Restored state")
    }

    // Helper methods
    private val sensorListener = object : SensorEventListener {
        override fun onSensorChanged(event: SensorEvent?) { }
        override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) { }
    }

    private fun startCameraPreview() { }
    private fun stopCameraPreview() { }
    private fun startAnimations() { }
    private fun pauseAnimations() { }
    private fun saveDraftData() { }
    private fun stopNetworkRequests() { }
    private fun releaseAllResources() { }
}
```

### Summary Table

| Method | Event | When | Common Use |
|--------|-------|------|------------|
| onCreate() | Creation | Activity instantiated | Initialize views, setup |
| onStart() | Becoming visible | Before visible to user | Register receivers |
| onResume() | Interactive | Ready for input | Start camera, sensors |
| onPause() | Losing focus | Another Activity focused | Pause operations, save drafts |
| onStop() | Hidden | Not visible | Release resources |
| onRestart() | Restarting | After stopped | Reinitialize |
| onDestroy() | Destruction | About to be destroyed | Final cleanup |
| onSaveInstanceState() | Before destruction | May be killed | Save UI state |
| onRestoreInstanceState() | After recreation | Restored from death | Restore UI state |

## Russian Answer

Методы Activity привязаны к следующим событиям:

1. **onCreate(Bundle savedInstanceState)** - создание активности (первый запуск, пересоздание после уничтожения, изменение конфигурации)

2. **onStart()** - активность становится видимой для пользователя (после onCreate() или onRestart())

3. **onResume()** - активность становится доступной для взаимодействия с пользователем (получение фокуса, готовность к вводу)

4. **onPause()** - активность перестает быть доступной для взаимодействия (потеря фокуса, другая активность на переднем плане)

5. **onStop()** - активность становится невидимой для пользователя (полностью скрыта другой активностью)

6. **onDestroy()** - уничтожение активности (вызов finish(), нажатие Back, изменение конфигурации, нехватка памяти)

7. **onRestart()** - активность снова становится активной после остановки (возврат из фонового режима)

8. **onSaveInstanceState(Bundle outState)** - сохранение состояния активности перед возможным уничтожением (поворот экрана, нехватка памяти)

9. **onRestoreInstanceState(Bundle savedInstanceState)** - восстановление состояния активности после ее пересоздания (после onStart(), когда есть сохраненное состояние)

Эти методы позволяют правильно управлять ресурсами приложения на разных этапах жизненного цикла активности.
