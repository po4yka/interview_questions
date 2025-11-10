---
id: android-099
title: "Rendering Views in Background Thread / Отрисовка View в фоновом потоке"
aliases: ["Rendering Views in Background Thread", "SurfaceView", "TextureView", "Отрисовка View в фоновом потоке"]
topic: android
subtopics: [performance-rendering, threads-sync, ui-graphics]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-13
updated: 2025-11-10
sources: []
moc: moc-android
related: [c-android-surfaces]
tags: [android, android/performance-rendering, android/threads-sync, android/ui-graphics, difficulty/hard, graphics, multithreading]

---

# Вопрос (RU)

> Какой класс следует использовать для отрисовки `View`-подобного контента в фоновом потоке, не нарушая ограничения главного потока?

# Question (EN)

> Which class should be used to render `View`-like content from a background thread without violating main thread constraints?

---

## Ответ (RU)

**SurfaceView** — основной специализированный класс для организации отрисовки в отдельной поверхности, которую можно обновлять из фонового потока. Он предоставляет отдельный буфер поверхности, который может обновляться вне главного потока через `Canvas` и `SurfaceHolder.lockCanvas()`.

Важно: стандартная иерархия `View` должна измеряться, раскладываться и отрисовываться в главном потоке. `SurfaceView` (и аналогично низкоуровневое использование `Surface`/`TextureView`) предоставляет отдельную поверхность, не нарушая этого правила.

### Почему SurfaceView?

Обычные `View` обязаны отрисовываться в главном потоке. SurfaceView решает эту задачу за счет отдельной поверхности:
- Имеет отдельный буфер поверхности
- Позволяет отрисовку на этот буфер из фоновых потоков
- Обеспечивает высокую производительность для игр и видео
- Снижает нагрузку на UI-поток, так как основная работа происходит вне него (но события `SurfaceHolder.Callback` приходят в UI-поток, и неправильное использование все еще может его блокировать)

### Базовая Реализация SurfaceView

```kotlin
class GameView(context: Context) : SurfaceView(context), SurfaceHolder.Callback {
    private var drawingThread: Thread? = null
    @Volatile private var isRunning = false

    init {
        holder.addCallback(this)
    }

    override fun surfaceCreated(holder: SurfaceHolder) {
        isRunning = true
        drawingThread = Thread {
            while (isRunning) {
                var canvas: Canvas? = null
                try {
                    canvas = holder.lockCanvas() // ✅ Захват Canvas для рисования
                    synchronized(holder) {
                        canvas?.apply {
                            drawColor(Color.BLACK)
                            drawCircle(
                                width / 2f,
                                height / 2f,
                                100f,
                                Paint().apply { color = Color.RED }
                            )
                        }
                    }
                } finally {
                    canvas?.let { holder.unlockCanvasAndPost(it) } // ✅ Всегда освобождаем
                }
                // Рекомендуется ограничивать FPS, чтобы не загружать CPU на 100%
                Thread.sleep(16) // ~60fps; подберите под задачу
            }
        }.apply { start() }
    }

    override fun surfaceDestroyed(holder: SurfaceHolder) {
        isRunning = false
        drawingThread?.join() // ✅ Ждем завершения потока после выхода из цикла
    }

    override fun surfaceChanged(holder: SurfaceHolder, format: Int, w: Int, h: Int) {}
}
```

### TextureView Как Альтернатива

**TextureView** — современная альтернатива с поддержкой трансформаций и участия в обычной иерархии `View`. Для низкоуровневой отрисовки также можно использовать фоновые потоки, рисуя в `Surface`, полученный из его `SurfaceTexture`.

```kotlin
class CustomTextureView(context: Context) :
    TextureView(context), TextureView.SurfaceTextureListener {

    private var renderThread: Thread? = null
    @Volatile private var isRunning = false

    init {
        surfaceTextureListener = this
    }

    override fun onSurfaceTextureAvailable(surface: SurfaceTexture, w: Int, h: Int) {
        val surf = Surface(surface)
        isRunning = true
        renderThread = Thread {
            try {
                while (isRunning && isAvailable) {
                    var canvas: Canvas? = null
                    try {
                        canvas = surf.lockCanvas(null) // ✅ Захват Canvas
                        canvas.drawColor(Color.BLUE)
                    } finally {
                        canvas?.let { surf.unlockCanvasAndPost(it) }
                    }
                    Thread.sleep(16) // ~60fps
                }
            } finally {
                surf.release()
            }
        }.apply { start() }
    }

    override fun onSurfaceTextureDestroyed(surface: SurfaceTexture): Boolean {
        // Останавливаем цикл и ждем завершения потока перед уничтожением поверхности
        isRunning = false
        renderThread?.join()
        renderThread = null
        return true
    }

    override fun onSurfaceTextureSizeChanged(s: SurfaceTexture, w: Int, h: Int) {}
    override fun onSurfaceTextureUpdated(surface: SurfaceTexture) {}
}
```

### Сравнение SurfaceView Vs TextureView

| Характеристика | SurfaceView | TextureView |
|----------------|-------------|-------------|
| **Производительность** | Как правило выше для полноэкранного/интенсивного рендеринга (отдельная поверхность, композитится отдельно) | Обычно хорошая, но с накладными расходами, участвует в иерархии `View` |
| **Память** | Обычно меньше | Может быть выше из-за текстур и участия в компоновке |
| **Трансформации** | Очень ограничены (не обычный `View`-контент) | Полная поддержка (scale, rotate, alpha и т.д.) |
| **Прозрачность** | Ограничена; классический SurfaceView перекрывает подлежащие `View` | Да, поддерживает полупрозрачность |
| **Анимации `View`** | Неприменимы напрямую к контенту поверхности | Полная поддержка стандартных `View`-анимаций |
| **Лучше для** | Игры, видео, высокопроизводительный full-screen рендеринг | UI с анимацией, встраиваемое видео, эффекты поверх UI |

(Это типичные сценарии, а не жесткие правила; выбор зависит от конкретного кейса.)

### Использование с корутинами

```kotlin
class ModernSurfaceView(context: Context) :
    SurfaceView(context), SurfaceHolder.Callback {

    // Важно: используем не-main Dispatcher, чтобы рендер действительно шел вне UI-потока
    private val scope = CoroutineScope(Dispatchers.Default)
    private var renderJob: Job? = null

    init {
        holder.addCallback(this)
    }

    override fun surfaceCreated(holder: SurfaceHolder) {
        renderJob = scope.launch {
            while (isActive) {
                var canvas: Canvas? = null
                try {
                    canvas = holder.lockCanvas()
                    canvas?.let { draw(it) }
                } finally {
                    canvas?.let { holder.unlockCanvasAndPost(it) }
                }
                delay(16) // ~60fps
            }
        }
    }

    override fun surfaceDestroyed(holder: SurfaceHolder) {
        // Останавливаем конкретную задачу рендеринга
        renderJob?.cancel()
        renderJob = null
        // При использовании общего scope для нескольких задач, отмену всего scope делайте осознанно.
        // Здесь предполагается, что scope посвящен только этому SurfaceView:
        scope.cancel()
    }

    override fun surfaceChanged(holder: SurfaceHolder, f: Int, w: Int, h: Int) {}

    private fun draw(canvas: Canvas) {
        canvas.drawColor(Color.BLACK)
    }
}
```

### Best Practices

1. **Всегда освобождать Canvas**: используйте `try-finally` с `unlockCanvasAndPost()`.
2. **Контроль FPS**: ограничивайте частоту кадров (`sleep`/`delay` или временная логика), чтобы не загружать CPU на 100%.
3. **Правильная остановка**: перед `join()` сначала меняйте флаг/отменяйте Job, чтобы цикл вышел и поток/корутина завершились.
4. **Синхронизация**: защищайте доступ к общим данным (`synchronized`, другие средства синхронизации), если к ним обращаются несколько потоков.
5. **Учитывайте lifecycle**: корректно реагируйте на `surfaceCreated`/`surfaceDestroyed`/`onSurfaceTextureAvailable`/`onSurfaceTextureDestroyed`.

### Типичные Ошибки

```kotlin
// ❌ ПЛОХО: Не освобожден Canvas
canvas = holder.lockCanvas()
// ... рисование ...
// Забыли вызвать unlockCanvasAndPost!

// ✅ ХОРОШО: Всегда используем finally
var canvas: Canvas? = null
try {
    canvas = holder.lockCanvas()
    // ... рисование ...
} finally {
    canvas?.let { holder.unlockCanvasAndPost(it) }
}

// ❌ ПЛОХО: Неправильная остановка потока
override fun surfaceDestroyed(holder: SurfaceHolder) {
    thread?.interrupt() // Может не сработать и оставить поток живым
}

// ✅ ХОРОШО: Используем флаг и join
@Volatile private var isRunning = true

override fun surfaceDestroyed(holder: SurfaceHolder) {
    isRunning = false // Цикл в потоке завершится
    thread?.join()
}
```

## Answer (EN)

**SurfaceView** is the primary specialized class for rendering into a separate surface that can be updated from a background thread. It exposes a dedicated drawing buffer that can be updated off the main thread using a `Canvas` obtained via `SurfaceHolder.lockCanvas()`.

Important: the standard `View` hierarchy must be measured, laid out, and drawn on the main thread. `SurfaceView` (and similarly low-level use of `Surface`/`TextureView`) provides a separate surface so you can render off the UI thread without violating this rule.

### Why SurfaceView?

Regular Views must be drawn on the main thread. SurfaceView addresses this by using a separate surface:
- Has its own surface buffer
- Allows drawing to that buffer from background threads
- Provides high performance for games and video
- Reduces load on the UI thread because heavy rendering runs off the main thread (though `SurfaceHolder.Callback` events still come on the UI thread, and misusing them can block it)

### Basic SurfaceView Implementation

```kotlin
class GameView(context: Context) : SurfaceView(context), SurfaceHolder.Callback {
    private var drawingThread: Thread? = null
    @Volatile private var isRunning = false

    init {
        holder.addCallback(this)
    }

    override fun surfaceCreated(holder: SurfaceHolder) {
        isRunning = true
        drawingThread = Thread {
            while (isRunning) {
                var canvas: Canvas? = null
                try {
                    canvas = holder.lockCanvas() // ✅ Lock canvas for drawing
                    synchronized(holder) {
                        canvas?.apply {
                            drawColor(Color.BLACK)
                            drawCircle(
                                width / 2f,
                                height / 2f,
                                100f,
                                Paint().apply { color = Color.RED }
                            )
                        }
                    }
                } finally {
                    canvas?.let { holder.unlockCanvasAndPost(it) } // ✅ Always unlock
                }
                // Recommend frame limiting to avoid 100% CPU usage
                Thread.sleep(16) // ~60fps; tune for your use case
            }
        }.apply { start() }
    }

    override fun surfaceDestroyed(holder: SurfaceHolder) {
        isRunning = false
        drawingThread?.join() // ✅ Wait for thread completion after loop exits
    }

    override fun surfaceChanged(holder: SurfaceHolder, format: Int, w: Int, h: Int) {}
}
```

### TextureView Alternative

**TextureView** is a modern alternative that supports transformations and participates in the normal `View` hierarchy. For low-level rendering, you can also use a background thread to draw into a `Surface` backed by its `SurfaceTexture`.

```kotlin
class CustomTextureView(context: Context) :
    TextureView(context), TextureView.SurfaceTextureListener {

    private var renderThread: Thread? = null
    @Volatile private var isRunning = false

    init {
        surfaceTextureListener = this
    }

    override fun onSurfaceTextureAvailable(surface: SurfaceTexture, w: Int, h: Int) {
        val surf = Surface(surface)
        isRunning = true
        renderThread = Thread {
            try {
                while (isRunning && isAvailable) {
                    var canvas: Canvas? = null
                    try {
                        canvas = surf.lockCanvas(null) // ✅ Lock canvas
                        canvas.drawColor(Color.BLUE)
                    } finally {
                        canvas?.let { surf.unlockCanvasAndPost(it) }
                    }
                    Thread.sleep(16) // ~60fps
                }
            } finally {
                surf.release()
            }
        }.apply { start() }
    }

    override fun onSurfaceTextureDestroyed(surface: SurfaceTexture): Boolean {
        // Stop loop and wait for render thread before releasing surface
        isRunning = false
        renderThread?.join()
        renderThread = null
        return true
    }

    override fun onSurfaceTextureSizeChanged(s: SurfaceTexture, w: Int, h: Int) {}
    override fun onSurfaceTextureUpdated(surface: SurfaceTexture) {}
}
```

### SurfaceView Vs TextureView Comparison

| Feature | SurfaceView | TextureView |
|---------|-------------|-------------|
| **Performance** | Typically higher for fullscreen / heavy rendering (separate surface, separate composition) | Generally good; participates in `View` hierarchy with some overhead |
| **Memory** | Typically lower | May be higher due to textures and `View` hierarchy participation |
| **Transformations** | Very limited (not standard `View` content) | Full support (scale, rotate, alpha, etc.) |
| **Transparency** | Limited; classic SurfaceView sits in a separate layer and obscures below | Yes, supports transparency |
| **`View` animations** | Not directly applicable to surface content | Fully supports standard `View` animations |
| **Best for** | Games, video, high-performance fullscreen rendering | Animated/transformable UI, embedded video, effects within UI |

(These are typical guidelines, not absolute rules; choose based on your use case.)

### Using with Coroutines

```kotlin
class ModernSurfaceView(context: Context) :
    SurfaceView(context), SurfaceHolder.Callback {

    // Important: use a non-main Dispatcher so rendering is off the UI thread
    private val scope = CoroutineScope(Dispatchers.Default)
    private var renderJob: Job? = null

    init {
        holder.addCallback(this)
    }

    override fun surfaceCreated(holder: SurfaceHolder) {
        renderJob = scope.launch {
            while (isActive) {
                var canvas: Canvas? = null
                try {
                    canvas = holder.lockCanvas()
                    canvas?.let { draw(it) }
                } finally {
                    canvas?.let { holder.unlockCanvasAndPost(it) }
                }
                delay(16) // ~60fps
            }
        }
    }

    override fun surfaceDestroyed(holder: SurfaceHolder) {
        // Stop just the rendering job first
        renderJob?.cancel()
        renderJob = null
        // If this scope is dedicated solely to this view, it's safe to cancel it here.
        scope.cancel()
    }

    override fun surfaceChanged(holder: SurfaceHolder, f: Int, w: Int, h: Int) {}

    private fun draw(canvas: Canvas) {
        canvas.drawColor(Color.BLACK)
    }
}
```

### Best Practices

1. **Always unlock the canvas**: use `try-finally` with `unlockCanvasAndPost()`.
2. **Control FPS**: limit frame rate (`sleep`/`delay` or time-based logic) to avoid pegging the CPU.
3. **Proper shutdown**: before calling `join()`, flip the running flag / cancel jobs so loops exit cleanly.
4. **Synchronization**: protect shared data access (`synchronized` or other primitives) when multiple threads are involved.
5. **Respect lifecycle**: handle `surfaceCreated`/`surfaceDestroyed`/`onSurfaceTextureAvailable`/`onSurfaceTextureDestroyed` correctly.

### Common Mistakes

```kotlin
// ❌ BAD: Canvas not unlocked
canvas = holder.lockCanvas()
// ... drawing ...
// Forgot to call unlockCanvasAndPost!

// ✅ GOOD: Always use finally
var canvas: Canvas? = null
try {
    canvas = holder.lockCanvas()
    // ... drawing ...
} finally {
    canvas?.let { holder.unlockCanvasAndPost(it) }
}

// ❌ BAD: Improper thread stopping
override fun surfaceDestroyed(holder: SurfaceHolder) {
    thread?.interrupt() // May not stop the loop / thread safely
}

// ✅ GOOD: Use flag and join
@Volatile private var isRunning = true

override fun surfaceDestroyed(holder: SurfaceHolder) {
    isRunning = false // Loop exits
    thread?.join()
}
```

---

## Follow-ups

1. What are the trade-offs between using `SurfaceView` and `TextureView` for high-frequency rendering?
2. How would you synchronize game logic and rendering threads when using `SurfaceView`?
3. How do lifecycle changes (pause/resume, configuration changes) affect a `SurfaceView`-based renderer?
4. How can you profile and debug jank or dropped frames when drawing via `SurfaceView`?
5. In which scenarios is it still preferable to keep rendering on the main thread despite `SurfaceView` availability?

## References

- [[c-android-surfaces]]
- [[q-what-is-the-main-application-execution-thread--android--easy]]
- https://developer.android.com/reference/android/view/SurfaceView
- https://developer.android.com/reference/android/view/TextureView

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Main thread basics

### Related (Same Level)
- (missing: related custom view / OpenGL / video playback questions)

### Advanced (Harder)
- (missing: advanced Vulkan / optimization questions)
