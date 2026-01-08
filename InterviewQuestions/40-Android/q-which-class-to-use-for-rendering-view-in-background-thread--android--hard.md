---\
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
updated: 2025-11-11
sources: []
moc: moc-android
related: [c-android-graphics-pipeline, c-android-surfaces, q-android-app-lag-analysis--android--medium]
tags: [android, android/performance-rendering, android/threads-sync, android/ui-graphics, difficulty/hard, graphics, multithreading]

---\
# Вопрос (RU)

> Какой класс следует использовать для отрисовки `View`-подобного контента в фоновом потоке, не нарушая ограничения главного потока?

# Question (EN)

> Which class should be used to render `View`-like content from a background thread without violating main thread constraints?

---

## Ответ (RU)

## Краткая Версия
Используйте `SurfaceView` (или низкоуровневый `Surface`, полученный через него) как основной специализированный класс для вынесения тяжелого рендеринга в фоновый поток. `TextureView` может быть альтернативой, если критичны трансформации и участие в обычной иерархии `View`.

## Подробная Версия
**SurfaceView** — основной специализированный класс для организации отрисовки в отдельной поверхности, которую можно обновлять из фонового потока. Он предоставляет отдельный буфер поверхности, который может обновляться вне главного потока через `Canvas` и `SurfaceHolder.lockCanvas()`.

Важно: стандартная иерархия `View` (measure/layout/draw) должна выполняться в главном потоке. `SurfaceView` (и низкоуровневое использование `Surface` / `TextureView`) предоставляет отдельную поверхность, на которую можно рисовать из других потоков, не нарушая этого правила — но любые операции с обычными `View` по-прежнему должны идти из UI-потока.

### Почему SurfaceView?

Обычные `View` обязаны отрисовываться в главном потоке. SurfaceView решает задачу вынесения тяжелого рендеринга за счет отдельной поверхности:
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
                try {
                    Thread.sleep(16) // ~60fps; подберите под задачу
                } catch (e: InterruptedException) {
                    // Если поток прерван — выходим из цикла
                    isRunning = false
                }
            }
        }.apply { start() }
    }

    override fun surfaceDestroyed(holder: SurfaceHolder) {
        isRunning = false
        // Важно: избегайте долгих join на UI-потоке; этот пример предполагает быстрый выход цикла.
        drawingThread?.join()
        drawingThread = null
    }

    override fun surfaceChanged(holder: SurfaceHolder, format: Int, w: Int, h: Int) {}
}
```

### TextureView Как Альтернатива

**TextureView** — альтернатива с поддержкой трансформаций и участием в обычной иерархии `View`. Для низкоуровневой отрисовки также можно использовать фоновые потоки, рисуя в `Surface`, полученный из его `SurfaceTexture`.

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
                    try {
                        Thread.sleep(16) // ~60fps
                    } catch (e: InterruptedException) {
                        isRunning = false
                    }
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
        return true // true -> система освободит SurfaceTexture
    }

    override fun onSurfaceTextureSizeChanged(s: SurfaceTexture, w: Int, h: Int) {}
    override fun onSurfaceTextureUpdated(surface: SurfaceTexture) {}
}
```

### Сравнение SurfaceView Vs TextureView

| Характеристика | SurfaceView | TextureView |
|----------------|-------------|-------------|
| **Производительность** | Как правило выше для полноэкранного/интенсивного рендеринга (отдельная поверхность, отдельная композиция) | Обычно хорошая; участвует в иерархии `View` и в GPU-компоновке, возможны накладные расходы |
| **Память** | Эффективна для полноэкранного рендеринга | Может потребоваться дополнительная память под текстуру и композицию; профиль зависит от сценария |
| **Трансформации** | Очень ограничены (не обычный `View`-контент) | Полная поддержка (scale, rotate, alpha и т.д.) |
| **Прозрачность** | Ограничена; классический SurfaceView рендерится в отдельном слое и перекрывает подлежащие `View` | Да, поддерживает полупрозрачность |
| **Анимации `View`** | Неприменимы напрямую к контенту поверхности | Полная поддержка стандартных `View`-анимаций |
| **Лучше для** | Игры, видео, высокопроизводительный full-screen рендеринг | UI с анимацией, встраиваемое видео, эффекты поверх UI |

(Это типичные сценарии, а не жесткие правила; выбор зависит от конкретного кейса.)

### Использование С Корутинами

```kotlin
class ModernSurfaceView(context: Context) :
    SurfaceView(context), SurfaceHolder.Callback {

    // Важно: используем не-main Dispatcher, чтобы рендер действительно шел вне UI-потока.
    // Scope предполагается посвященным этому View и отменяется при уничтожении поверхности.
    private val renderScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    private var renderJob: Job? = null

    init {
        holder.addCallback(this)
    }

    override fun surfaceCreated(holder: SurfaceHolder) {
        // Не запускаем новый рендер, если предыдущий ещё не остановлен
        if (renderJob?.isActive == true) return

        renderJob = renderScope.launch {
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
        // Так как scope посвящен этому SurfaceView, безопасно отменить его здесь
        renderScope.cancel()
    }

    override fun surfaceChanged(holder: SurfaceHolder, f: Int, w: Int, h: Int) {}

    private fun draw(canvas: Canvas) {
        canvas.drawColor(Color.BLACK)
    }
}
```

### Рекомендации (Best Practices)

1. Всегда освобождайте `Canvas`: используйте `try-finally` с `unlockCanvasAndPost()`.
2. Контролируйте FPS: ограничивайте частоту кадров (`sleep`/`delay` или временная логика), чтобы не загружать CPU на 100%.
3. Корректно останавливайте потоки/корутины: перед `join()` меняйте флаг или отменяйте `Job`, чтобы цикл корректно завершился; избегайте долгих блокирующих `join()` в UI-потоке.
4. Обеспечьте синхронизацию доступа к общим данным (`synchronized` и другие средства), если они используются из нескольких потоков.
5. Учитывайте жизненный цикл: корректно обрабатывайте `surfaceCreated` / `surfaceDestroyed` / `onSurfaceTextureAvailable` / `onSurfaceTextureDestroyed` и lifecycle владельца (`Activity`/`Fragment`).
6. Соблюдайте правило главного потока: вся обычная `View`-иерархия (layout, invalidate, свойства `View`) должна обновляться только из UI-потока.

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

### Требования

- Функциональные:
  - Обеспечить отрисовку `View`-подобного контента из фонового потока.
  - Не нарушать правило обновления обычной `View`-иерархии только из главного потока.
  - Поддержать стабильный FPS и корректную работу с жизненным циклом `SurfaceView`/`TextureView`.
- Нефункциональные:
  - Высокая производительность и минимизация jank.
  - Предсказуемое потребление ресурсов (CPU/GPU/память).
  - Безопасность многопоточности при доступе к общим данным.

### Архитектура

- Используется специализированная поверхность рендеринга (`SurfaceView` или `TextureView`), отделённая от стандартной `View`-иерархии.
- Фоновый поток (или корутина на `Dispatchers.Default`) выполняет цикл рендеринга и пишет в `Surface` через `lockCanvas`/`unlockCanvasAndPost`.
- Главный поток обрабатывает жизненный цикл и стандартные `View`-операции, не блокируясь тяжелым рисованием.
- Синхронизация данных между UI-потоком и рендер-потоком выполняется через безопасные примитивы (флаги, `synchronized`, корутинные механизмы).

## Answer (EN)

## Short Version
Use `SurfaceView` (or a `Surface` obtained from it) as the primary class for off-main-thread rendering of `View`-like content. `TextureView` is a viable alternative when you need transformations and integration into the normal `View` hierarchy.

## Detailed Version
**SurfaceView** is the primary specialized class for rendering into a separate surface that can be updated from a background thread. It exposes a dedicated drawing buffer that can be updated off the main thread using a `Canvas` obtained via `SurfaceHolder.lockCanvas()`.

Important: the standard `View` hierarchy (measure/layout/draw) must run on the main thread. `SurfaceView` (and low-level use of `Surface` / `TextureView`) gives you a separate surface you can render to from other threads without violating that rule — but all interactions with normal `View` APIs must still happen on the UI thread.

### Why SurfaceView?

Regular `Views` must be drawn on the main thread. `SurfaceView` addresses this by using a separate surface:
- Has its own surface buffer
- Allows drawing to that buffer from background threads
- `Provides` high performance for games and video
- Reduces load on the UI thread because heavy rendering runs off the main thread (though `SurfaceHolder.Callback` events still arrive on the UI thread, and misusing them can block it)

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
                try {
                    Thread.sleep(16) // ~60fps; tune for your use case
                } catch (e: InterruptedException) {
                    // If interrupted, exit loop
                    isRunning = false
                }
            }
        }.apply { start() }
    }

    override fun surfaceDestroyed(holder: SurfaceHolder) {
        isRunning = false
        // Note: avoid long blocking joins on the UI thread; here we assume quick loop exit.
        drawingThread?.join()
        drawingThread = null
    }

    override fun surfaceChanged(holder: SurfaceHolder, format: Int, w: Int, h: Int) {}
}
```

### TextureView Alternative

**TextureView** is an alternative that supports transformations and participates in the normal `View` hierarchy. For low-level rendering, you can also use a background thread to draw into a `Surface` backed by its `SurfaceTexture`.

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
                    try {
                        Thread.sleep(16) // ~60fps
                    } catch (e: InterruptedException) {
                        isRunning = false
                    }
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
        return true // true -> framework will release the SurfaceTexture
    }

    override fun onSurfaceTextureSizeChanged(s: SurfaceTexture, w: Int, h: Int) {}
    override fun onSurfaceTextureUpdated(surface: SurfaceTexture) {}
}
```

### SurfaceView Vs TextureView Comparison

| Feature | SurfaceView | TextureView |
|---------|-------------|-------------|
| **Performance** | Typically higher for fullscreen / heavy rendering (separate surface, separate composition) | Generally good; participates in `View` hierarchy and GPU composition, may incur extra overhead |
| **Memory** | Efficient for fullscreen rendering | May use additional memory for the texture and composition; actual profile is scenario-dependent |
| **Transformations** | Very limited (not standard `View` content) | Full support (scale, rotate, alpha, etc.) |
| **Transparency** | Limited; classic SurfaceView is in a separate layer and obscures underlying `Views` | Yes, supports transparency |
| **`View` animations** | Not directly applicable to surface content | Fully supports standard `View` animations |
| **Best for** | Games, video, high-performance fullscreen rendering | Animated / transformable UI, embedded video, visual effects within UI |

(These are typical guidelines, not absolute rules; choose based on your use case.)

### Using with Coroutines

```kotlin
class ModernSurfaceView(context: Context) :
    SurfaceView(context), SurfaceHolder.Callback {

    // Important: use a non-main Dispatcher so rendering is off the UI thread.
    // Scope is dedicated to this view and cancelled when the surface is destroyed.
    private val renderScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    private var renderJob: Job? = null

    init {
        holder.addCallback(this)
    }

    override fun surfaceCreated(holder: SurfaceHolder) {
        if (renderJob?.isActive == true) return

        renderJob = renderScope.launch {
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
        // Stop the specific rendering job
        renderJob?.cancel()
        renderJob = null
        // Since this scope is dedicated to this SurfaceView, it's safe to cancel here
        renderScope.cancel()
    }

    override fun surfaceChanged(holder: SurfaceHolder, f: Int, w: Int, h: Int) {}

    private fun draw(canvas: Canvas) {
        canvas.drawColor(Color.BLACK)
    }
}
```

### Best Practices

1. Always unlock the canvas: use `try-finally` with `unlockCanvasAndPost()`.
2. Control FPS: limit frame rate (`sleep`/`delay` or time-based logic) to avoid pegging the CPU.
3. Proper shutdown: before calling `join()`, flip the running flag / cancel jobs so loops exit; avoid long blocking `join()` on the main thread.
4. Synchronization: protect shared data (`synchronized` or other primitives) when accessed from multiple threads.
5. Respect lifecycle: handle `surfaceCreated` / `surfaceDestroyed` / `onSurfaceTextureAvailable` / `onSurfaceTextureDestroyed` and the owning `Activity`/`Fragment` lifecycle correctly.
6. Respect main thread rule: all normal `View` hierarchy operations (layout, invalidation, property changes) must stay on the UI thread.

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
    thread?.interrupt() // May not safely stop the loop/thread
}

// ✅ GOOD: Use flag and join
@Volatile private var isRunning = true

override fun surfaceDestroyed(holder: SurfaceHolder) {
    isRunning = false // Loop exits
    thread?.join()
}
```

### Requirements

- Functional:
  - Allow rendering of `View`-like content from a background thread.
  - Preserve the rule that normal `View` hierarchy updates happen only on the main thread.
  - Maintain stable FPS and correct lifecycle handling for `SurfaceView`/`TextureView`.
- Non-functional:
  - High performance and minimal jank.
  - Predictable resource usage (CPU/GPU/memory).
  - `Thread`-safety for shared data access.

### Architecture

- A dedicated rendering surface (`SurfaceView` or `TextureView`) is used, separated from the standard `View` hierarchy.
- A background thread (or coroutine on `Dispatchers.Default`) runs the rendering loop, writing into the `Surface` via `lockCanvas`/`unlockCanvasAndPost`.
- The main thread manages lifecycle and regular `View` operations without being blocked by heavy drawing.
- Data shared between UI and rendering threads is synchronized using safe primitives (flags, `synchronized`, coroutine mechanisms).

## Дополнительные Вопросы (RU)

1. Каковы ключевые trade-off'ы между использованием `SurfaceView` и `TextureView` для высокочастотного рендеринга?
2. Как синхронизировать потоки игровой логики и рендеринга при использовании `SurfaceView`?
3. Как изменения жизненного цикла (`pause`/`resume`, смена конфигурации) влияют на рендерер, основанный на `SurfaceView`?
4. Как профилировать и отлаживать jank или пропущенные кадры при рисовании через `SurfaceView`?
5. В каких сценариях рендеринг все еще предпочтительно оставлять на главном потоке, несмотря на наличие `SurfaceView`?

## Additional Questions (EN)

1. What are the trade-offs between using `SurfaceView` and `TextureView` for high-frequency rendering?
2. How would you synchronize game logic and rendering threads when using `SurfaceView`?
3. How do lifecycle changes (pause/resume, configuration changes) affect a `SurfaceView`-based renderer?
4. How can you profile and debug jank or dropped frames when drawing via `SurfaceView`?
5. In which scenarios is it still preferable to keep rendering on the main thread despite `SurfaceView` availability?

## Follow-ups (RU/EN)

- См. секции "Дополнительные вопросы (RU)" и "Additional Questions (EN)" для продолжения обсуждения.

## Ссылки (RU)

- [[c-android-surfaces]]
- [[c-android-graphics-pipeline]]
- [[q-android-app-lag-analysis--android--medium]]
- https://developer.android.com/reference/android/view/SurfaceView
- https://developer.android.com/reference/android/view/TextureView

## References (EN)

- [[c-android-surfaces]]
- [[c-android-graphics-pipeline]]
- [[q-android-app-lag-analysis--android--medium]]
- https://developer.android.com/reference/android/view/SurfaceView
- https://developer.android.com/reference/android/view/TextureView

## Связанные Вопросы (RU)

### Предварительные (проще)
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Базовые знания о главном потоке

### Связанные (тот Же уровень)
- [[q-android-app-lag-analysis--android--medium]]

### Продвинутые (сложнее)
- (отсутствует: продвинутые вопросы по Vulkan / оптимизациям)

## Related Questions (EN)

### Prerequisites (Easier)
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Main thread basics

### Related (Same Level)
- [[q-android-app-lag-analysis--android--medium]]

### Advanced (Harder)
- (missing: advanced Vulkan / optimization questions)
