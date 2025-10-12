---
topic: android
tags:
  - android
difficulty: medium
status: draft
---

# What events are Activity methods tied to?

# Вопрос (RU)

К каким событиям привязаны методы Activity?

## Answer (EN)
Activity lifecycle methods are tied to specific system events that occur during an Activity's lifetime. These methods allow developers to respond to state changes and manage resources appropriately.

### Activity Lifecycle Events and Methods

```
┌─────────────────────────────────────────────┐
│         Activity Lifecycle Events            │
└─────────────────────────────────────────────┘

onCreate() ──────► Activity is created
    ↓
onStart() ───────► Activity becomes visible
    ↓
onResume() ──────► Activity gains focus, user can interact
    ↓
[Activity Running]
    ↓
onPause() ───────► Another activity comes to foreground
    ↓
onStop() ────────► Activity no longer visible
    ↓
onDestroy() ─────► Activity is destroyed
```

### Detailed Event Mapping

#### 1. onCreate() - Activity Creation Event

**Triggered when:**
- Activity is first created
- After process death and recreation
- Configuration change (rotation, language change)

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Initialize UI
        // Restore saved state
        // Set up ViewModels
        // Bind views

        if (savedInstanceState != null) {
            // Activity was recreated
            val counter = savedInstanceState.getInt("counter", 0)
            Log.d("Lifecycle", "Restored counter: $counter")
        } else {
            // First time creation
            Log.d("Lifecycle", "First creation")
        }
    }
}
```

**Use cases:**
- Set content view
- Initialize UI components
- Restore saved state
- Set up ViewModels
- Bind data

---

#### 2. onStart() - Visibility Event

**Triggered when:**
- Activity is about to become visible
- After onCreate() or onRestart()
- Returning from background

```kotlin
override fun onStart() {
    super.onStart()

    // Register broadcast receivers
    // Start animations
    // Begin updates that require visibility

    val intentFilter = IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)
    registerReceiver(networkReceiver, intentFilter)

    Log.d("Lifecycle", "Activity is becoming visible")
}
```

**Use cases:**
- Register broadcast receivers
- Start animations
- Update UI with fresh data
- Resume paused operations

---

#### 3. onResume() - Focus Gained Event

**Triggered when:**
- Activity is ready for user interaction
- After onStart()
- Returning from onPause()
- When dialog dismisses

```kotlin
override fun onResume() {
    super.onResume()

    // Resume camera preview
    // Start location updates
    // Resume game/video playback
    // Acquire exclusive resources

    cameraPreview.resume()
    locationManager.requestLocationUpdates()

    Log.d("Lifecycle", "Activity has focus - user can interact")
}
```

**Use cases:**
- Resume camera/sensors
- Start location updates
- Resume media playback
- Refresh data from server
- Acquire exclusive resources (camera, microphone)

---

#### 4. onPause() - Focus Lost Event

**Triggered when:**
- Another activity comes to foreground
- Dialog appears over activity
- Multi-window mode splits focus
- Phone call received
- About to navigate to another activity

```kotlin
override fun onPause() {
    super.onPause()

    // Pause camera preview
    // Stop location updates
    // Pause game/video
    // Save critical data (should be fast!)

    cameraPreview.pause()
    locationManager.removeUpdates(locationListener)

    // Save draft
    saveDraft()

    Log.d("Lifecycle", "Activity losing focus")
}
```

**Use cases:**
- Release exclusive resources
- Pause camera/sensors
- Stop animations
- Save uncommitted changes
- Pause media playback

**IMPORTANT:**
- Keep onPause() operations fast (< 1 second)
- Don't perform heavy operations
- Don't access database or network

---

#### 5. onStop() - Visibility Lost Event

**Triggered when:**
- Activity is no longer visible
- User navigated to another activity
- App moved to background
- Multi-tasking

```kotlin
override fun onStop() {
    super.onStop()

    // Unregister broadcast receivers
    // Release resources
    // Save persistent data
    // Stop background work

    unregisterReceiver(networkReceiver)

    // Save state to database
    viewModel.saveState()

    Log.d("Lifecycle", "Activity no longer visible")
}
```

**Use cases:**
- Unregister broadcast receivers
- Release heavy resources
- Save persistent data
- Stop background work
- Cancel network requests

---

#### 6. onDestroy() - Destruction Event

**Triggered when:**
- Activity is finishing (user pressed back)
- finish() is called
- Configuration change (rotation)
- System destroys activity to reclaim memory

```kotlin
override fun onDestroy() {
    super.onDestroy()

    // Clean up resources
    // Cancel coroutines
    // Close database connections
    // Release memory

    viewModelScope.cancel()
    database.close()

    if (isFinishing) {
        Log.d("Lifecycle", "Activity is finishing (user navigated away)")
    } else {
        Log.d("Lifecycle", "Activity destroyed for recreation (config change)")
    }
}
```

**Use cases:**
- Cancel coroutines
- Close database connections
- Release all resources
- Cleanup listeners

---

#### 7. onRestart() - Visibility Regained Event

**Triggered when:**
- Activity was stopped and is starting again
- User returns to activity from another activity
- User returns from home screen

```kotlin
override fun onRestart() {
    super.onRestart()

    // Refresh UI data
    // Reconnect to services

    viewModel.refreshData()

    Log.d("Lifecycle", "Activity restarting after being stopped")
}
```

**Use cases:**
- Refresh data
- Reconnect to services
- Update UI

---

### Complete Lifecycle Example

```kotlin
class DetailActivity : AppCompatActivity() {

    private lateinit var viewModel: DetailViewModel
    private lateinit var networkReceiver: BroadcastReceiver
    private lateinit var player: MediaPlayer

    // 1. Activity Created
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_detail)

        Log.d("Lifecycle", "onCreate - Activity created")

        viewModel = ViewModelProvider(this)[DetailViewModel::class.java]

        // Initialize UI
        setupViews()

        // Restore state
        savedInstanceState?.let { bundle ->
            val position = bundle.getInt("player_position", 0)
            Log.d("Lifecycle", "Restored player position: $position")
        }
    }

    // 2. Activity Becoming Visible
    override fun onStart() {
        super.onStart()
        Log.d("Lifecycle", "onStart - Activity becoming visible")

        // Register receiver
        networkReceiver = NetworkChangeReceiver()
        val filter = IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)
        registerReceiver(networkReceiver, filter)
    }

    // 3. Activity Has Focus
    override fun onResume() {
        super.onResume()
        Log.d("Lifecycle", "onResume - Activity has focus")

        // Resume playback
        player.start()

        // Refresh data
        viewModel.loadData()
    }

    // 4. Activity Losing Focus
    override fun onPause() {
        super.onPause()
        Log.d("Lifecycle", "onPause - Activity losing focus")

        // Pause playback
        if (player.isPlaying) {
            player.pause()
        }

        // Save draft (fast operation!)
        viewModel.saveDraft()
    }

    // 5. Activity No Longer Visible
    override fun onStop() {
        super.onStop()
        Log.d("Lifecycle", "onStop - Activity no longer visible")

        // Unregister receiver
        unregisterReceiver(networkReceiver)

        // Save state to database
        viewModel.saveToDatabase()
    }

    // 6. Activity Destroyed
    override fun onDestroy() {
        super.onDestroy()
        Log.d("Lifecycle", "onDestroy - Activity destroyed")

        // Release resources
        player.release()

        if (isFinishing) {
            Log.d("Lifecycle", "User navigated away - cleanup completely")
        } else {
            Log.d("Lifecycle", "Configuration change - will be recreated")
        }
    }

    // 7. Activity Restarting
    override fun onRestart() {
        super.onRestart()
        Log.d("Lifecycle", "onRestart - Returning to activity")

        // Refresh data since user returned
        viewModel.refreshData()
    }

    // Save state for recreation
    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        outState.putInt("player_position", player.currentPosition)

        Log.d("Lifecycle", "onSaveInstanceState - Saving state")
    }

    // Restore state after recreation
    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)

        val position = savedInstanceState.getInt("player_position", 0)
        player.seekTo(position)

        Log.d("Lifecycle", "onRestoreInstanceState - Restored state")
    }
}
```

### Configuration Change Events

**Triggered when:**
- Screen rotation
- Language change
- Dark mode toggle
- Font size change

```kotlin
// onSaveInstanceState - Save state before destruction
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)

    outState.putInt("counter", counter)
    outState.putString("text", editText.text.toString())

    Log.d("Lifecycle", "Saving state before config change")
}

// onRestoreInstanceState - Restore state after recreation
override fun onRestoreInstanceState(savedInstanceState: Bundle) {
    super.onRestoreInstanceState(savedInstanceState)

    counter = savedInstanceState.getInt("counter", 0)
    val text = savedInstanceState.getString("text", "")
    editText.setText(text)

    Log.d("Lifecycle", "Restored state after config change")
}
```

**Lifecycle during configuration change:**
```
onPause()
onStop()
onSaveInstanceState()
onDestroy()
onCreate()
onStart()
onRestoreInstanceState()
onResume()
```

### Multi-Window Events (Android 7.0+)

```kotlin
override fun onMultiWindowModeChanged(isInMultiWindowMode: Boolean) {
    super.onMultiWindowModeChanged(isInMultiWindowMode)

    if (isInMultiWindowMode) {
        Log.d("Lifecycle", "Entered multi-window mode")
        // Adjust UI for split screen
        adjustLayoutForSplitScreen()
    } else {
        Log.d("Lifecycle", "Exited multi-window mode")
        // Restore full-screen UI
        restoreFullScreenLayout()
    }
}
```

### Picture-in-Picture Events (Android 8.0+)

```kotlin
override fun onPictureInPictureModeChanged(
    isInPictureInPictureMode: Boolean,
    newConfig: Configuration
) {
    super.onPictureInPictureModeChanged(isInPictureInPictureMode, newConfig)

    if (isInPictureInPictureMode) {
        Log.d("Lifecycle", "Entered PiP mode")
        // Hide controls
        hideControls()
    } else {
        Log.d("Lifecycle", "Exited PiP mode")
        // Show controls
        showControls()
    }
}
```

### Common Event Scenarios

#### Scenario 1: User Opens App

```
onCreate()
onStart()
onResume()
[User interacts with app]
```

#### Scenario 2: User Presses Home Button

```
onPause()
onStop()
[App in background]
```

#### Scenario 3: User Returns to App

```
onRestart()
onStart()
onResume()
[User interacts with app]
```

#### Scenario 4: User Rotates Screen

```
onPause()
onStop()
onSaveInstanceState()
onDestroy()
onCreate()
onStart()
onRestoreInstanceState()
onResume()
```

#### Scenario 5: User Presses Back Button

```
onPause()
onStop()
onDestroy()
[Activity finished]
```

#### Scenario 6: Phone Call Received

```
onPause()
[Phone app comes to foreground]
[Call ends]
onResume()
```

### Best Practices

**1. Keep onPause() Fast**
```kotlin
// - BAD - Heavy operation in onPause
override fun onPause() {
    super.onPause()
    database.saveAllData() // TOO SLOW!
    uploadToServer()       // TOO SLOW!
}

// - GOOD - Fast operation in onPause
override fun onPause() {
    super.onPause()
    player.pause()
    saveDraftLocally() // Fast local save only
}
```

**2. Use ViewModel for Data**
```kotlin
// - BAD - Lose data on config change
class MainActivity : AppCompatActivity() {
    private var userData: List<User> = emptyList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        loadUserData() // Reloads on every rotation!
    }
}

// - GOOD - ViewModel survives config changes
class MainActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel.users.observe(this) { users ->
            updateUI(users)
        }
        // ViewModel survives rotation, data not reloaded
    }
}
```

**3. Release Resources in onStop()**
```kotlin
override fun onStop() {
    super.onStop()

    // Release heavy resources
    unregisterReceiver(receiver)
    stopLocationUpdates()
    releaseCamera()
}
```

### Summary Table

| Method | Event | When Called | Use For |
|--------|-------|-------------|---------|
| **onCreate()** | Activity created | First launch, config change | Initialize UI, ViewModels |
| **onStart()** | Becoming visible | Before visible to user | Register receivers, start animations |
| **onResume()** | Has focus | Ready for interaction | Resume camera, sensors, playback |
| **onPause()** | Losing focus | Another activity foreground | Pause camera, save draft |
| **onStop()** | Not visible | No longer visible | Unregister receivers, save data |
| **onDestroy()** | Destroyed | Finishing or config change | Release all resources |
| **onRestart()** | Restarting | Returning from stopped | Refresh data |

## Ответ (RU)
Методы жизненного цикла Activity привязаны к конкретным системным событиям, которые происходят в течение жизни Activity. Эти методы позволяют разработчикам реагировать на изменения состояния и правильно управлять ресурсами.

### Основные события и методы

**onCreate()** - Создание активности
- Вызывается при первом запуске
- После пересоздания из-за поворота экрана
- Используется для инициализации UI

**onStart()** - Активность становится видимой
- Вызывается перед отображением пользователю
- Регистрация broadcast receivers
- Запуск анимаций

**onResume()** - Активность получает фокус
- Пользователь может взаимодействовать
- Возобновление камеры, сенсоров
- Начало воспроизведения медиа

**onPause()** - Активность теряет фокус
- Другая активность на переднем плане
- Пауза камеры, сенсоров
- Быстрое сохранение черновика

**onStop()** - Активность больше не видна
- Пользователь перешел в другую активность
- Отмена регистрации receivers
- Сохранение данных в базу

**onDestroy()** - Уничтожение активности
- Пользователь нажал кнопку "Назад"
- Поворот экрана
- Освобождение всех ресурсов

**onRestart()** - Возврат к активности
- Возврат из остановленного состояния
- Обновление данных

### Типичные сценарии

**Открытие приложения:**
onCreate() → onStart() → onResume()

**Нажатие кнопки Home:**
onPause() → onStop()

**Возврат в приложение:**
onRestart() → onStart() → onResume()

**Поворот экрана:**
onPause() → onStop() → onSaveInstanceState() → onDestroy() → onCreate() → onStart() → onRestoreInstanceState() → onResume()

**Нажатие кнопки Назад:**
onPause() → onStop() → onDestroy()

