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
updated: 2025-10-29
sources: []
moc: moc-android
related: []
tags: [android, android/performance-rendering, android/threads-sync, android/ui-graphics, difficulty/hard, graphics, multithreading]
---

# Вопрос (RU)

Какой класс следует использовать для отрисовки `View` в фоновом потоке?

# Question (EN)

Which class should be used to render `View` in a background thread?

---

## Ответ (RU)

**SurfaceView** — основной класс для отрисовки в фоновом потоке. Он предоставляет отдельный буфер поверхности, который можно обновлять вне главного потока через `Canvas` и `SurfaceHolder.lockCanvas()`.

### Почему SurfaceView?

Обычные `View` обязаны отрисовываться в главном потоке. SurfaceView решает эту проблему:
- Имеет отдельный буфер поверхности
- Позволяет отрисовку из фоновых потоков
- Обеспечивает высокую производительность для игр и видео
- Не блокирует UI поток

### Базовая Реализация SurfaceView

```kotlin
class GameView(context: Context) : SurfaceView(context), SurfaceHolder.Callback {
 private var drawingThread: Thread? = null
 private var isRunning = false

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
 drawCircle(width / 2f, height / 2f, 100f,
 Paint().apply { color = Color.RED })
 }
 }
 } finally {
 canvas?.let { holder.unlockCanvasAndPost(it) } // ✅ Всегда освобождаем
 }
 }
 }.apply { start() }
 }

 override fun surfaceDestroyed(holder: SurfaceHolder) {
 isRunning = false
 drawingThread?.join() // ✅ Ждем завершения потока
 }

 override fun surfaceChanged(holder: SurfaceHolder, format: Int, w: Int, h: Int) {}
}
```

### TextureView Как Альтернатива

**TextureView** — современная альтернатива с поддержкой трансформаций:

```kotlin
class CustomTextureView(context: Context) :
 TextureView(context), TextureView.SurfaceTextureListener {

 private var renderThread: Thread? = null

 init {
 surfaceTextureListener = this
 }

 override fun onSurfaceTextureAvailable(surface: SurfaceTexture, w: Int, h: Int) {
 renderThread = Thread {
 val surf = Surface(surface)
 while (isAvailable) {
 val canvas = surf.lockCanvas(null) // ✅ Захват Canvas
 canvas.drawColor(Color.BLUE)
 surf.unlockCanvasAndPost(canvas)
 Thread.sleep(16) // ~60fps
 }
 }.apply { start() }
 }

 override fun onSurfaceTextureDestroyed(surface: SurfaceTexture): Boolean {
 renderThread?.join()
 return true
 }

 override fun onSurfaceTextureSizeChanged(s: SurfaceTexture, w: Int, h: Int) {}
 override fun onSurfaceTextureUpdated(surface: SurfaceTexture) {}
}
```

### Сравнение SurfaceView Vs TextureView

| Характеристика | SurfaceView | TextureView |
|----------------|-------------|-------------|
| **Производительность** | Выше | Хорошая |
| **Память** | Меньше | Больше |
| **Трансформации** | Ограничены | Полная поддержка |
| **Прозрачность** | Нет | Да |
| **Анимации `View`** | Нет | Да |
| **Лучше для** | Игры, видео | UI с анимацией |

### Использование С Корутинами

```kotlin
class ModernSurfaceView(context: Context) :
 SurfaceView(context), SurfaceHolder.Callback {

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
 renderJob?.cancel()
 scope.cancel()
 }

 override fun surfaceChanged(holder: SurfaceHolder, f: Int, w: Int, h: Int) {}

 private fun draw(canvas: Canvas) {
 canvas.drawColor(Color.BLACK)
 }
}
```

### Best Practices

1. **Всегда освобождать `Canvas`**: используйте `try-finally` с `unlockCanvasAndPost()`
2. **Контроль FPS**: избегайте чрезмерной нагрузки на CPU
3. **Правильная остановка**: используйте флаги и `join()` для завершения потоков
4. **Синхронизация**: защищайте доступ к общим данным через `synchronized`

### Типичные Ошибки

```kotlin
// ❌ ПЛОХО: Не освобожден Canvas
canvas = holder.lockCanvas()
draw(canvas)
// Забыли вызвать unlock!

// ✅ ХОРОШО: Всегда используем finally
var canvas: Canvas? = null
try {
 canvas = holder.lockCanvas()
 draw(canvas)
} finally {
 canvas?.let { holder.unlockCanvasAndPost(it) }
}

// ❌ ПЛОХО: Неправильная остановка потока
override fun surfaceDestroyed(holder: SurfaceHolder) {
 thread?.interrupt() // Может не сработать
}

// ✅ ХОРОШО: Используем флаг и join
override fun surfaceDestroyed(holder: SurfaceHolder) {
 isRunning = false
 thread?.join()
}
```

## Answer (EN)

**SurfaceView** is the primary class for background thread rendering. It provides a dedicated drawing surface buffer that can be updated off the main thread using `Canvas` via `SurfaceHolder.lockCanvas()`.

### Why SurfaceView?

Regular Views must be drawn on the main thread. SurfaceView solves this by:
- Having a separate surface buffer
- Allowing drawing from background threads
- Providing better performance for games and video
- Not blocking the UI thread

### Basic SurfaceView Implementation

```kotlin
class GameView(context: Context) : SurfaceView(context), SurfaceHolder.Callback {
 private var drawingThread: Thread? = null
 private var isRunning = false

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
 drawCircle(width / 2f, height / 2f, 100f,
 Paint().apply { color = Color.RED })
 }
 }
 } finally {
 canvas?.let { holder.unlockCanvasAndPost(it) } // ✅ Always unlock
 }
 }
 }.apply { start() }
 }

 override fun surfaceDestroyed(holder: SurfaceHolder) {
 isRunning = false
 drawingThread?.join() // ✅ Wait for thread completion
 }

 override fun surfaceChanged(holder: SurfaceHolder, format: Int, w: Int, h: Int) {}
}
```

### TextureView Alternative

**TextureView** is a modern alternative with transformation support:

```kotlin
class CustomTextureView(context: Context) :
 TextureView(context), TextureView.SurfaceTextureListener {

 private var renderThread: Thread? = null

 init {
 surfaceTextureListener = this
 }

 override fun onSurfaceTextureAvailable(surface: SurfaceTexture, w: Int, h: Int) {
 renderThread = Thread {
 val surf = Surface(surface)
 while (isAvailable) {
 val canvas = surf.lockCanvas(null) // ✅ Lock canvas
 canvas.drawColor(Color.BLUE)
 surf.unlockCanvasAndPost(canvas)
 Thread.sleep(16) // ~60fps
 }
 }.apply { start() }
 }

 override fun onSurfaceTextureDestroyed(surface: SurfaceTexture): Boolean {
 renderThread?.join()
 return true
 }

 override fun onSurfaceTextureSizeChanged(s: SurfaceTexture, w: Int, h: Int) {}
 override fun onSurfaceTextureUpdated(surface: SurfaceTexture) {}
}
```

### SurfaceView Vs TextureView Comparison

| Feature | SurfaceView | TextureView |
|---------|-------------|-------------|
| **Performance** | Higher | Good |
| **Memory** | Lower | Higher |
| **Transformations** | Limited | Full support |
| **Transparency** | No | Yes |
| **`View` animations** | No | Yes |
| **Best for** | Games, video | UI with animation |

### Using with Coroutines

```kotlin
class ModernSurfaceView(context: Context) :
 SurfaceView(context), SurfaceHolder.Callback {

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
 renderJob?.cancel()
 scope.cancel()
 }

 override fun surfaceChanged(holder: SurfaceHolder, f: Int, w: Int, h: Int) {}

 private fun draw(canvas: Canvas) {
 canvas.drawColor(Color.BLACK)
 }
}
```

### Best Practices

1. **Always unlock canvas**: use `try-finally` with `unlockCanvasAndPost()`
2. **Control FPS**: avoid excessive CPU usage
3. **Proper shutdown**: use flags and `join()` to stop threads
4. **Synchronization**: protect shared data access with `synchronized`

### Common Mistakes

```kotlin
// ❌ BAD: Canvas not unlocked
canvas = holder.lockCanvas()
draw(canvas)
// Forgot to unlock!

// ✅ GOOD: Always use finally
var canvas: Canvas? = null
try {
 canvas = holder.lockCanvas()
 draw(canvas)
} finally {
 canvas?.let { holder.unlockCanvasAndPost(it) }
}

// ❌ BAD: Improper thread stopping
override fun surfaceDestroyed(holder: SurfaceHolder) {
 thread?.interrupt() // May not work
}

// ✅ GOOD: Use flag and join
override fun surfaceDestroyed(holder: SurfaceHolder) {
 isRunning = false
 thread?.join()
}
```

---

## Follow-ups

1. What are the memory implications of using SurfaceView vs regular `View`?
2. How do you handle screen rotation with SurfaceView without losing state?
3. Can you use hardware acceleration with SurfaceView?
4. What's the difference between lockCanvas() and lockCanvas(Rect)?
5. How do you implement double buffering with SurfaceView?

## References

- - SurfaceView concept and architecture
- - TextureView implementation details
- - `Canvas` API and drawing operations
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Understanding main thread constraints
- https://developer.android.com/reference/android/view/SurfaceView
- https://developer.android.com/reference/android/view/TextureView

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Main thread basics
- - `Thread` communication

### Related (Same Level)
- - Custom view implementation
- - Using OpenGL with SurfaceView
- - Video rendering with SurfaceView

### Advanced (Harder)
- - Vulkan API for high-performance graphics
- - Advanced rendering optimization
