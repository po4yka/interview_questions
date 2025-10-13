---
topic: android
tags:
  - android
difficulty: medium
status: draft
---

# Which class should be used to render View in background thread?

## EN (expanded)

## Answer (EN)

**SurfaceView** provides a dedicated drawing surface that can be rendered from a background thread. It's designed for high-performance graphics operations that would be too heavy for the main UI thread.

### Why SurfaceView?

Regular Views must be drawn on the main thread, but SurfaceView:
- Has a separate surface buffer
- Allows drawing from background threads
- Provides better performance for animations and games
- Doesn't block the UI thread

### Basic SurfaceView Implementation

```kotlin
class GameView(context: Context) : SurfaceView(context), SurfaceHolder.Callback {

    private var drawingThread: DrawingThread? = null
    private val paint = Paint()

    init {
        holder.addCallback(this)
    }

    override fun surfaceCreated(holder: SurfaceHolder) {
        // Start drawing thread
        drawingThread = DrawingThread(holder)
        drawingThread?.isRunning = true
        drawingThread?.start()
    }

    override fun surfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) {
        // Handle surface changes
    }

    override fun surfaceDestroyed(holder: SurfaceHolder) {
        // Stop drawing thread
        var retry = true
        drawingThread?.isRunning = false
        while (retry) {
            try {
                drawingThread?.join()
                retry = false
            } catch (e: InterruptedException) {
                e.printStackTrace()
            }
        }
    }

    private inner class DrawingThread(private val surfaceHolder: SurfaceHolder) : Thread() {
        var isRunning = false

        override fun run() {
            while (isRunning) {
                var canvas: Canvas? = null
                try {
                    // Lock canvas for drawing
                    canvas = surfaceHolder.lockCanvas()

                    synchronized(surfaceHolder) {
                        // Draw on canvas
                        draw(canvas)
                    }
                } finally {
                    // Always unlock and post canvas
                    canvas?.let {
                        surfaceHolder.unlockCanvasAndPost(it)
                    }
                }
            }
        }

        private fun draw(canvas: Canvas?) {
            canvas?.apply {
                // Clear canvas
                drawColor(Color.BLACK)

                // Draw content
                drawCircle(
                    width / 2f,
                    height / 2f,
                    100f,
                    paint.apply { color = Color.RED }
                )
            }
        }
    }
}
```

### Complete Game Example

```kotlin
class GameSurfaceView(context: Context, attrs: AttributeSet? = null) :
    SurfaceView(context, attrs), SurfaceHolder.Callback {

    private var gameThread: GameThread? = null
    private var ball: Ball = Ball(100f, 100f, 50f)

    init {
        holder.addCallback(this)
        isFocusable = true
    }

    override fun surfaceCreated(holder: SurfaceHolder) {
        gameThread = GameThread(holder)
        gameThread?.start()
    }

    override fun surfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) {
        // Handle size changes
    }

    override fun surfaceDestroyed(holder: SurfaceHolder) {
        var retry = true
        gameThread?.running = false
        while (retry) {
            try {
                gameThread?.join()
                retry = false
            } catch (e: InterruptedException) {
                e.printStackTrace()
            }
        }
    }

    private inner class GameThread(private val surfaceHolder: SurfaceHolder) : Thread() {
        var running = false
        private val targetFPS = 60
        private val targetTime = 1000 / targetFPS

        override fun run() {
            running = true

            while (running) {
                val startTime = System.currentTimeMillis()

                // Update game state
                update()

                // Draw
                draw()

                // Control frame rate
                val timeMillis = System.currentTimeMillis() - startTime
                val waitTime = targetTime - timeMillis

                if (waitTime > 0) {
                    try {
                        sleep(waitTime)
                    } catch (e: InterruptedException) {
                        e.printStackTrace()
                    }
                }
            }
        }

        private fun update() {
            // Update game logic
            ball.update()
        }

        private fun draw() {
            var canvas: Canvas? = null
            try {
                canvas = surfaceHolder.lockCanvas()
                canvas?.let {
                    synchronized(surfaceHolder) {
                        // Clear
                        it.drawColor(Color.BLACK)

                        // Draw game objects
                        ball.draw(it)
                    }
                }
            } catch (e: Exception) {
                e.printStackTrace()
            } finally {
                canvas?.let {
                    try {
                        surfaceHolder.unlockCanvasAndPost(it)
                    } catch (e: Exception) {
                        e.printStackTrace()
                    }
                }
            }
        }
    }

    class Ball(var x: Float, var y: Float, private val radius: Float) {
        private var dx = 5f
        private var dy = 5f
        private val paint = Paint().apply {
            color = Color.RED
            isAntiAlias = true
        }

        fun update() {
            x += dx
            y += dy

            // Bounce off edges (assuming screen bounds)
            if (x - radius < 0 || x + radius > 1080) {
                dx = -dx
            }
            if (y - radius < 0 || y + radius > 1920) {
                dy = -dy
            }
        }

        fun draw(canvas: Canvas) {
            canvas.drawCircle(x, y, radius, paint)
        }
    }
}
```

### TextureView Alternative

**TextureView** is another option for background rendering:

```kotlin
class CustomTextureView(context: Context, attrs: AttributeSet? = null) :
    TextureView(context, attrs), TextureView.SurfaceTextureListener {

    private var renderThread: RenderThread? = null

    init {
        surfaceTextureListener = this
    }

    override fun onSurfaceTextureAvailable(surface: SurfaceTexture, width: Int, height: Int) {
        renderThread = RenderThread(Surface(surface), width, height)
        renderThread?.start()
    }

    override fun onSurfaceTextureSizeChanged(surface: SurfaceTexture, width: Int, height: Int) {
        // Handle size changes
    }

    override fun onSurfaceTextureDestroyed(surface: SurfaceTexture): Boolean {
        renderThread?.running = false
        renderThread?.join()
        return true
    }

    override fun onSurfaceTextureUpdated(surface: SurfaceTexture) {
        // Called after drawing
    }

    private class RenderThread(
        private val surface: Surface,
        private val width: Int,
        private val height: Int
    ) : Thread() {
        var running = false

        override fun run() {
            running = true

            while (running) {
                try {
                    val canvas = surface.lockCanvas(null)

                    // Draw
                    canvas.drawColor(Color.BLUE)
                    canvas.drawCircle(
                        width / 2f,
                        height / 2f,
                        100f,
                        Paint().apply { color = Color.WHITE }
                    )

                    surface.unlockCanvasAndPost(canvas)

                    sleep(16) // ~60fps
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }
        }
    }
}
```

### SurfaceView vs TextureView

| Feature | SurfaceView | TextureView |
|---------|-------------|-------------|
| **Performance** | Better | Good |
| **Memory** | Lower | Higher |
| **Transformations** | Limited | Full support |
| **Animations** | No | Yes |
| **Transparency** | No | Yes |
| **Best for** | Games, video | Smooth animations |

### Advanced: Using Coroutines

```kotlin
class ModernSurfaceView(context: Context, attrs: AttributeSet? = null) :
    SurfaceView(context, attrs), SurfaceHolder.Callback {

    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    private var renderJob: Job? = null

    init {
        holder.addCallback(this)
    }

    override fun surfaceCreated(holder: SurfaceHolder) {
        renderJob = scope.launch {
            render(holder)
        }
    }

    override fun surfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) {
        // Handle changes
    }

    override fun surfaceDestroyed(holder: SurfaceHolder) {
        renderJob?.cancel()
    }

    private suspend fun render(holder: SurfaceHolder) {
        while (isActive) {
            var canvas: Canvas? = null
            try {
                canvas = holder.lockCanvas()
                canvas?.let { draw(it) }
            } finally {
                canvas?.let {
                    holder.unlockCanvasAndPost(it)
                }
            }

            delay(16) // ~60fps
        }
    }

    private fun draw(canvas: Canvas) {
        canvas.drawColor(Color.BLACK)
        // Draw content
    }

    fun cleanup() {
        scope.cancel()
    }
}
```

### Video Playback Example

```kotlin
class VideoSurfaceView(context: Context) : SurfaceView(context), SurfaceHolder.Callback {

    private var mediaPlayer: MediaPlayer? = null

    init {
        holder.addCallback(this)
    }

    override fun surfaceCreated(holder: SurfaceHolder) {
        mediaPlayer = MediaPlayer().apply {
            setDisplay(holder)
            setDataSource("path/to/video.mp4")
            prepare()
            start()
        }
    }

    override fun surfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) {
        // Handle changes
    }

    override fun surfaceDestroyed(holder: SurfaceHolder) {
        mediaPlayer?.release()
        mediaPlayer = null
    }
}
```

### Camera Preview Example

```kotlin
class CameraSurfaceView(context: Context) : SurfaceView(context), SurfaceHolder.Callback {

    private var camera: Camera? = null

    init {
        holder.addCallback(this)
    }

    override fun surfaceCreated(holder: SurfaceHolder) {
        try {
            camera = Camera.open()
            camera?.setPreviewDisplay(holder)
            camera?.startPreview()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    override fun surfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) {
        camera?.apply {
            stopPreview()
            parameters = parameters.apply {
                setPreviewSize(width, height)
            }
            startPreview()
        }
    }

    override fun surfaceDestroyed(holder: SurfaceHolder) {
        camera?.apply {
            stopPreview()
            release()
        }
        camera = null
    }
}
```

### Best Practices

1. **Always lock/unlock canvas** in try-finally blocks
2. **Control frame rate** to avoid excessive CPU usage
3. **Properly cleanup threads** when surface is destroyed
4. **Use synchronized blocks** when accessing shared data
5. **Handle exceptions** gracefully
6. **Check holder validity** before drawing

### Common Mistakes

```kotlin
//  BAD: Not unlocking canvas
canvas = holder.lockCanvas()
draw(canvas)
// Forgot to unlock!

//  GOOD: Always unlock in finally
var canvas: Canvas? = null
try {
    canvas = holder.lockCanvas()
    draw(canvas)
} finally {
    canvas?.let { holder.unlockCanvasAndPost(it) }
}

//  BAD: Not stopping thread properly
override fun surfaceDestroyed(holder: SurfaceHolder) {
    thread?.interrupt() // May not work
}

//  GOOD: Use flag and join
override fun surfaceDestroyed(holder: SurfaceHolder) {
    thread?.running = false
    thread?.join()
}
```

---

## RU (original)

Какой класс нужно использовать чтобы отрисовывать View в background thread

Нужно использовать SurfaceView который предоставляет отдельный буфер для обновления вне основного потока а также использовать Canvas через SurfaceHolder.lockCanvas
