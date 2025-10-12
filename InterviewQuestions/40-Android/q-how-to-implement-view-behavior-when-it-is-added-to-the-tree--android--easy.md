---
topic: android
tags:
  - android
  - android/views
  - custom view
  - ui
  - view lifecycle
  - views
difficulty: easy
status: draft
---

# Как можно реализовать поведение view при ее добавлении в дерево?

**English**: How to implement view behavior when it is added to the tree?

## Answer (EN)
To implement View behavior when it is added to the view tree in Android, you can use the **`View.onAttachedToWindow()`** method, which is called when a View is added to a window. This method allows you to perform actions when the View becomes visible to the user.

### Understanding View Attachment Lifecycle

When a View is added to the view hierarchy, several methods are called in sequence:

1. **Constructor** - View is created
2. **onFinishInflate()** - Called after view and its children are inflated from XML
3. **onAttachedToWindow()** - View is now attached to a window
4. **onMeasure()** - View size is measured
5. **onLayout()** - View is positioned
6. **onDraw()** - View is drawn

When a View is removed:
1. **onDetachedFromWindow()** - View is detached from window

### Basic Implementation

```kotlin
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        // View is now attached to window
        // Perform initialization that requires window access
        Log.d("CustomView", "View attached to window")

        // Example: Start animations
        startAnimation()

        // Example: Register listeners
        registerListeners()
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        // View is being removed from window
        // Clean up resources
        Log.d("CustomView", "View detached from window")

        // Example: Stop animations
        stopAnimation()

        // Example: Unregister listeners
        unregisterListeners()
    }

    private fun startAnimation() {
        animate()
            .alpha(1f)
            .setDuration(300)
            .start()
    }

    private fun stopAnimation() {
        clearAnimation()
    }

    private fun registerListeners() {
        // Register broadcast receivers, etc.
    }

    private fun unregisterListeners() {
        // Unregister to prevent memory leaks
    }
}
```

### Practical Use Cases

#### 1. Auto-Start Video Playback

```kotlin
class VideoPlayerView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : FrameLayout(context, attrs) {

    private var player: ExoPlayer? = null
    private val playerView: PlayerView

    init {
        inflate(context, R.layout.view_video_player, this)
        playerView = findViewById(R.id.playerView)
    }

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        // Initialize and start player when view becomes visible
        initializePlayer()
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        // Release player to free resources
        releasePlayer()
    }

    private fun initializePlayer() {
        player = ExoPlayer.Builder(context).build().apply {
            playerView.player = this
            // Set media item and prepare
            setMediaItem(MediaItem.fromUri(videoUri))
            prepare()
            playWhenReady = true
        }
    }

    private fun releasePlayer() {
        player?.release()
        player = null
    }
}
```

#### 2. Visibility Tracking

```kotlin
class TrackableView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var onVisibilityChangeListener: ((Boolean) -> Unit)? = null

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        // View became visible
        onVisibilityChangeListener?.invoke(true)
        trackImpression()
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        // View became invisible
        onVisibilityChangeListener?.invoke(false)
    }

    fun setOnVisibilityChangeListener(listener: (Boolean) -> Unit) {
        onVisibilityChangeListener = listener
    }

    private fun trackImpression() {
        // Send analytics event
        Log.d("TrackableView", "View impression tracked")
    }
}

// Usage
trackableView.setOnVisibilityChangeListener { isVisible ->
    if (isVisible) {
        // Start something
    } else {
        // Stop something
    }
}
```

#### 3. Auto-Refresh Content

```kotlin
class AutoRefreshView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : LinearLayout(context, attrs) {

    private val handler = Handler(Looper.getMainLooper())
    private val refreshInterval = 5000L // 5 seconds

    private val refreshRunnable = object : Runnable {
        override fun run() {
            refreshContent()
            handler.postDelayed(this, refreshInterval)
        }
    }

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        // Start auto-refresh when view is visible
        handler.post(refreshRunnable)
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        // Stop auto-refresh to save resources
        handler.removeCallbacks(refreshRunnable)
    }

    private fun refreshContent() {
        // Refresh view content
        Log.d("AutoRefreshView", "Content refreshed")
    }
}
```

#### 4. Sensor-Based View

```kotlin
class SensorView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs), SensorEventListener {

    private val sensorManager: SensorManager =
        context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private val accelerometer: Sensor? =
        sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        // Register sensor listener when view is attached
        accelerometer?.let {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL)
        }
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        // Unregister to save battery
        sensorManager.unregisterListener(this)
    }

    override fun onSensorChanged(event: SensorEvent?) {
        event?.let {
            // Handle sensor data
            invalidate() // Redraw view based on sensor data
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {
        // Handle accuracy changes
    }
}
```

#### 5. Lifecycle-Aware View

```kotlin
class LifecycleAwareView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs), LifecycleEventObserver {

    private var lifecycleOwner: LifecycleOwner? = null

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()

        // Find lifecycle owner (Fragment or Activity)
        lifecycleOwner = findViewTreeLifecycleOwner()
        lifecycleOwner?.lifecycle?.addObserver(this)
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()

        lifecycleOwner?.lifecycle?.removeObserver(this)
        lifecycleOwner = null
    }

    override fun onStateChanged(source: LifecycleOwner, event: Lifecycle.Event) {
        when (event) {
            Lifecycle.Event.ON_RESUME -> {
                // View's lifecycle owner resumed
                startAnimations()
            }
            Lifecycle.Event.ON_PAUSE -> {
                // View's lifecycle owner paused
                pauseAnimations()
            }
            else -> {}
        }
    }

    private fun startAnimations() {
        // Start animations
    }

    private fun pauseAnimations() {
        // Pause animations
    }
}
```

### Using View.addOnAttachStateChangeListener

Alternative approach using a listener:

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val myView = findViewById<View>(R.id.myView)

        myView.addOnAttachStateChangeListener(object : View.OnAttachStateChangeListener {
            override fun onViewAttachedToWindow(v: View) {
                // View attached to window
                Log.d("MainActivity", "View attached")
            }

            override fun onViewDetachedFromWindow(v: View) {
                // View detached from window
                Log.d("MainActivity", "View detached")
            }
        })
    }
}
```

### Best Practices

1. **Always call super methods** - `super.onAttachedToWindow()` and `super.onDetachedFromWindow()`

2. **Clean up resources** - Unregister listeners, stop animations, release heavy objects in `onDetachedFromWindow()`

3. **Check window attachment** - Use `isAttachedToWindow` to check current state

```kotlin
fun doSomethingIfAttached() {
    if (isAttachedToWindow) {
        // Safe to access window-dependent resources
    }
}
```

4. **Avoid memory leaks** - Always clean up in `onDetachedFromWindow()`

5. **Use ViewTreeLifecycleOwner** - For lifecycle-aware operations

```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()

    findViewTreeLifecycleOwner()?.lifecycleScope?.launch {
        // Coroutine automatically cancelled when lifecycle is destroyed
    }
}
```

### Common Scenarios

| Use Case | Implementation |
|----------|----------------|
| Start animation | `onAttachedToWindow()` → start, `onDetachedFromWindow()` → stop |
| Register listeners | `onAttachedToWindow()` → register, `onDetachedFromWindow()` → unregister |
| Initialize resources | `onAttachedToWindow()` → init, `onDetachedFromWindow()` → release |
| Track visibility | `onAttachedToWindow()` → visible, `onDetachedFromWindow()` → invisible |
| Auto-refresh | `onAttachedToWindow()` → start timer, `onDetachedFromWindow()` → stop timer |

## Ответ (RU)
Для реализации поведения View при её добавлении в дерево View в Android можно воспользоваться несколькими подходами. Один из наиболее удобных способов — использование метода View.onAttachedToWindow(), который вызывается, когда View добавляется в окно. Этот метод позволяет выполнять какие-либо действия, когда View становится видимой для пользователя. Пример использования: создайте пользовательский класс View и переопределите метод onAttachedToWindow() для выполнения необходимых действий при добавлении View в дерево.

