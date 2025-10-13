---
topic: android
tags:
  - android
difficulty: medium
status: draft
---

# What does the Lifecycle library do?

## Answer (EN)
The **Lifecycle library** provides classes and interfaces to build **lifecycle-aware components** that automatically adjust their behavior based on the current lifecycle state of Activities and Fragments. It helps prevent memory leaks, crashes, and improves code organization.

### Core Components

**1. Lifecycle** - Represents the lifecycle state
**2. LifecycleOwner** - Interface implemented by Activity/Fragment
**3. LifecycleObserver** - Observes lifecycle changes

### Basic Usage

```kotlin
// Lifecycle-aware component
class MyLocationListener(
    private val context: Context,
    private val callback: (Location) -> Unit
) : LifecycleObserver {

    private lateinit var locationManager: LocationManager

    @OnLifecycleEvent(Lifecycle.Event.ON_START)
    fun startListening() {
        locationManager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
        // Start location updates
    }

    @OnLifecycleEvent(Lifecycle.Event.ON_STOP)
    fun stopListening() {
        // Stop location updates
        locationManager.removeUpdates(locationListener)
    }
}

// Activity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val locationListener = MyLocationListener(this) { location ->
            updateUI(location)
        }

        // Register observer
        lifecycle.addObserver(locationListener)
    }
}
```

### Modern Approach with DefaultLifecycleObserver

```kotlin
class MyLifecycleObserver(
    private val onStart: () -> Unit,
    private val onStop: () -> Unit
) : DefaultLifecycleObserver {

    override fun onStart(owner: LifecycleOwner) {
        onStart()
    }

    override fun onStop(owner: LifecycleOwner) {
        onStop()
    }
}

// Usage
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycle.addObserver(MyLifecycleObserver(
            onStart = { startSomething() },
            onStop = { stopSomething() }
        ))
    }
}
```

### Lifecycle States and Events

**States:**
- INITIALIZED
- CREATED
- STARTED
- RESUMED
- DESTROYED

**Events:**
- ON_CREATE
- ON_START
- ON_RESUME
- ON_PAUSE
- ON_STOP
- ON_DESTROY

```kotlin
class LifecycleLogger : DefaultLifecycleObserver {
    override fun onCreate(owner: LifecycleOwner) {
        Log.d("Lifecycle", "onCreate")
    }

    override fun onStart(owner: LifecycleOwner) {
        Log.d("Lifecycle", "onStart")
    }

    override fun onResume(owner: LifecycleOwner) {
        Log.d("Lifecycle", "onResume")
    }

    override fun onPause(owner: LifecycleOwner) {
        Log.d("Lifecycle", "onPause")
    }

    override fun onStop(owner: LifecycleOwner) {
        Log.d("Lifecycle", "onStop")
    }

    override fun onDestroy(owner: LifecycleOwner) {
        Log.d("Lifecycle", "onDestroy")
    }
}
```

### Practical Examples

#### 1. Video Player

```kotlin
class VideoPlayerObserver(
    private val videoPlayer: VideoPlayer
) : DefaultLifecycleObserver {

    override fun onStart(owner: LifecycleOwner) {
        videoPlayer.initialize()
    }

    override fun onResume(owner: LifecycleOwner) {
        videoPlayer.play()
    }

    override fun onPause(owner: LifecycleOwner) {
        videoPlayer.pause()
    }

    override fun onStop(owner: LifecycleOwner) {
        videoPlayer.stop()
    }

    override fun onDestroy(owner: LifecycleOwner) {
        videoPlayer.release()
    }
}

// Activity
class VideoActivity : AppCompatActivity() {
    private val videoPlayer = VideoPlayer()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycle.addObserver(VideoPlayerObserver(videoPlayer))
    }
}
```

#### 2. Network Listener

```kotlin
class NetworkObserver(
    private val context: Context,
    private val onNetworkAvailable: (Boolean) -> Unit
) : DefaultLifecycleObserver {

    private val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
    private lateinit var networkCallback: ConnectivityManager.NetworkCallback

    override fun onStart(owner: LifecycleOwner) {
        networkCallback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) {
                onNetworkAvailable(true)
            }

            override fun onLost(network: Network) {
                onNetworkAvailable(false)
            }
        }

        connectivityManager.registerDefaultNetworkCallback(networkCallback)
    }

    override fun onStop(owner: LifecycleOwner) {
        connectivityManager.unregisterNetworkCallback(networkCallback)
    }
}
```

#### 3. Analytics Tracker

```kotlin
class AnalyticsObserver(
    private val screenName: String
) : DefaultLifecycleObserver {

    override fun onResume(owner: LifecycleOwner) {
        Analytics.logScreenView(screenName)
    }

    override fun onPause(owner: LifecycleOwner) {
        Analytics.logScreenExit(screenName)
    }
}

// Usage
class ProductActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycle.addObserver(AnalyticsObserver("ProductScreen"))
    }
}
```

### LiveData Integration

LiveData is lifecycle-aware by default:

```kotlin
class MyViewModel : ViewModel() {
    private val _data = MutableLiveData<String>()
    val data: LiveData<String> = _data

    fun loadData() {
        _data.value = "Data loaded"
    }
}

class MainActivity : AppCompatActivity() {
    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Automatically handles lifecycle
        viewModel.data.observe(this) { data ->
            // Updates only when STARTED or RESUMED
            textView.text = data
        }
    }
}
```

### Coroutines Integration

```kotlin
class CoroutineObserver(
    private val scope: CoroutineScope
) : DefaultLifecycleObserver {

    private var job: Job? = null

    override fun onStart(owner: LifecycleOwner) {
        job = scope.launch {
            // Start coroutine work
            while (isActive) {
                fetchData()
                delay(5000)
            }
        }
    }

    override fun onStop(owner: LifecycleOwner) {
        job?.cancel()
    }
}

// Or use lifecycleScope
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Automatically cancelled when lifecycle is destroyed
            fetchData()
        }
    }
}
```

### Benefits

**1. Prevents Memory Leaks**
```kotlin
// BAD - Manual management
class BadActivity : AppCompatActivity() {
    override fun onStart() {
        super.onStart()
        locationManager.requestLocationUpdates(...)
    }

    override fun onStop() {
        super.onStop()
        // Easy to forget!
        // locationManager.removeUpdates(...)
    }
}

// GOOD - Automatic cleanup
class GoodActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycle.addObserver(LocationObserver()) // Handles cleanup automatically
    }
}
```

**2. Reduces Boilerplate**

No need to override lifecycle methods in every Activity/Fragment.

**3. Improves Testability**

Lifecycle-aware components can be tested independently.

**4. Reusability**

Same observer can be used across multiple Activities/Fragments.

### Checking Lifecycle State

```kotlin
class MyObserver : DefaultLifecycleObserver {
    override fun onStart(owner: LifecycleOwner) {
        if (owner.lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)) {
            // Safe to access UI
        }
    }
}

// In Activity
if (lifecycle.currentState.isAtLeast(Lifecycle.State.RESUMED)) {
    performAction()
}
```

### Custom LifecycleOwner

```kotlin
class MyCustomComponent : LifecycleOwner {
    private val lifecycleRegistry = LifecycleRegistry(this)

    override val lifecycle: Lifecycle
        get() = lifecycleRegistry

    fun start() {
        lifecycleRegistry.currentState = Lifecycle.State.STARTED
    }

    fun stop() {
        lifecycleRegistry.currentState = Lifecycle.State.DESTROYED
    }
}
```

### ProcessLifecycleOwner

Observe entire app lifecycle:

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        ProcessLifecycleOwner.get().lifecycle.addObserver(object : DefaultLifecycleObserver {
            override fun onStart(owner: LifecycleOwner) {
                // App moved to foreground
                Log.d("App", "App in foreground")
            }

            override fun onStop(owner: LifecycleOwner) {
                // App moved to background
                Log.d("App", "App in background")
            }
        })
    }
}
```

**English Summary**: Lifecycle library provides **lifecycle-aware components** that automatically respond to Activity/Fragment lifecycle changes. Core: Lifecycle (state), LifecycleOwner (Activity/Fragment), LifecycleObserver (observer). Use DefaultLifecycleObserver for modern approach. States: INITIALIZED, CREATED, STARTED, RESUMED, DESTROYED. Events: ON_CREATE, ON_START, ON_RESUME, ON_PAUSE, ON_STOP, ON_DESTROY. Benefits: prevents memory leaks, reduces boilerplate, improves testability, enables reusability. LiveData is lifecycle-aware by default. Use ProcessLifecycleOwner for app-level lifecycle. Works seamlessly with coroutines (lifecycleScope, viewModelScope).


---

## Related Questions

### Prerequisites (Easier)
- [[q-viewmodel-pattern--android--easy]] - Lifecycle

### Related (Medium)
- [[q-testing-viewmodels-turbine--testing--medium]] - Lifecycle
- [[q-what-is-viewmodel--android--medium]] - Lifecycle
- [[q-why-is-viewmodel-needed-and-what-happens-in-it--android--medium]] - Lifecycle
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] - Lifecycle
- [[q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium]] - Lifecycle

### Advanced (Harder)
- [[q-service-lifecycle-binding--background--hard]] - Lifecycle
- [[q-why-was-the-lifecycle-library-created--android--hard]] - Lifecycle
