---
id: android-346
title: SurfaceView Rendering / Рендеринг SurfaceView
aliases:
- SurfaceView Rendering
- Рендеринг SurfaceView
topic: android
subtopics:
- performance-rendering
- ui-views
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-threading
- c-views
- q-viewgroup-vs-view-differences--android--easy
- q-what-methods-redraw-views--android--medium
created: 2025-10-15
updated: 2025-10-31
tags:
- android/performance-rendering
- android/ui-views
- difficulty/medium
- rendering
- surfaceview
---

# Вопрос (RU)
> Рендеринг SurfaceView

# Question (EN)
> SurfaceView Rendering

---

## Answer (EN)
`SurfaceView` is a special view that provides a dedicated drawing surface embedded inside of a view hierarchy. Unlike regular views, `SurfaceView` can be updated on a background thread, making it ideal for high-performance rendering scenarios.

**Key Characteristics:**

**1. Dedicated Surface Buffer:**
- `SurfaceView` has a dedicated surface buffer while all regular views share one surface buffer that is allocated by ViewRoot
- In other words, `SurfaceView` costs more resources but provides better performance for intensive rendering

**2. Background `Thread` Rendering:**
- Unlike regular views that must be drawn on the UI thread, `SurfaceView` can be updated on a background thread
- This prevents blocking the UI thread during intensive rendering operations
- Ideal for games, video playback, camera preview, and other high-frame-rate content

**3. Hardware Acceleration Limitations:**
- `SurfaceView` cannot be hardware accelerated (as of Android 4.2 JellyBean)
- In contrast, 95% of operations on normal views are hardware-accelerated using OpenGL ES
- However, this trade-off is acceptable for scenarios requiring background thread rendering

**4. Additional Development Complexity:**
- More work is required to create a customized `SurfaceView`
- You need to:
  - Listen to `surfaceCreated/surfaceDestroyed` events
  - Create and manage a render thread
  - Synchronize the render thread and main thread properly
  - Handle the surface lifecycle

**5. Different Update Timing:**
- **Regular Views**: Update mechanism is constrained and controlled by the framework
  - Call `view.invalidate()` in UI thread or `view.postInvalidate()` in other threads
  - `View` won't update immediately but waits until next VSYNC event
  - VSYNC can be understood as a timer that fires every 16ms for a 60fps screen
  - All normal view updates are synchronized with VSYNC for better smoothness

- **SurfaceView**: You have direct control over when and how to render
  - Can render at any time from the background thread
  - Not bound to VSYNC timing
  - Provides more flexibility for custom rendering loops

**Basic Implementation:**

```kotlin
class MySurfaceView(context: Context) : SurfaceView(context), SurfaceHolder.Callback {

    private var renderThread: RenderThread? = null

    init {
        holder.addCallback(this)
    }

    override fun surfaceCreated(holder: SurfaceHolder) {
        // Surface is ready, start rendering thread
        renderThread = RenderThread(holder).apply {
            start()
        }
    }

    override fun surfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) {
        // Surface dimensions changed
    }

    override fun surfaceDestroyed(holder: SurfaceHolder) {
        // Stop rendering thread
        renderThread?.requestStop()
        renderThread?.join()
        renderThread = null
    }

    inner class RenderThread(private val holder: SurfaceHolder) : Thread() {
        private var running = true

        fun requestStop() {
            running = false
        }

        override fun run() {
            while (running) {
                val canvas = holder.lockCanvas()
                try {
                    // Perform drawing operations
                    synchronized(holder) {
                        // Draw on canvas
                        canvas?.let { drawContent(it) }
                    }
                } finally {
                    if (canvas != null) {
                        holder.unlockCanvasAndPost(canvas)
                    }
                }
            }
        }

        private fun drawContent(canvas: Canvas) {
            // Your drawing code here
            canvas.drawColor(Color.BLACK)
            // Draw other content...
        }
    }
}
```

**Use Cases:**

1. **Game Development**: High frame rate games requiring continuous rendering
2. **Video Playback**: Smooth video rendering without blocking UI thread
3. **Camera Preview**: Real-time camera feed display
4. **Custom Animations**: Complex animations that need precise frame control
5. **Data Visualization**: Real-time charts and graphs with frequent updates
6. **AR/VR Applications**: High-performance 3D rendering

**SurfaceView vs Regular `View`:**

| Feature | SurfaceView | Regular `View` |
|---------|-------------|--------------|
| Threading | Background thread rendering | UI thread only |
| Surface Buffer | Dedicated buffer | Shared buffer |
| Hardware Acceleration | Not supported (JB 4.2) | Fully supported |
| Update Timing | Manual control | VSYNC synchronized |
| Resource Usage | Higher | Lower |
| Use Case | High-performance rendering | Standard UI elements |
| Complexity | More complex | Simpler |

**Modern Alternatives:**

- **TextureView**: Can be hardware-accelerated and supports transformations, but higher memory usage
- **SurfaceView with Vulkan/OpenGL**: For modern 3D rendering
- **Jetpack Compose**: For declarative UI with efficient rendering

**Best Practices:**

1. Always implement `SurfaceHolder.Callback` to handle lifecycle events
2. Properly synchronize access to the `Canvas` between threads
3. Stop rendering thread when surface is destroyed to prevent memory leaks
4. Use `lockCanvas()` and `unlockCanvasAndPost()` carefully in try-finally blocks
5. Consider using `TextureView` if you need hardware acceleration and transformations

**Source**: [SurfaceView](https://developer.android.com/reference/android/view/SurfaceView)


# Question (EN)
> SurfaceView Rendering

---


---


## Answer (EN)
`SurfaceView` is a special view that provides a dedicated drawing surface embedded inside of a view hierarchy. Unlike regular views, `SurfaceView` can be updated on a background thread, making it ideal for high-performance rendering scenarios.

**Key Characteristics:**

**1. Dedicated Surface Buffer:**
- `SurfaceView` has a dedicated surface buffer while all regular views share one surface buffer that is allocated by ViewRoot
- In other words, `SurfaceView` costs more resources but provides better performance for intensive rendering

**2. Background `Thread` Rendering:**
- Unlike regular views that must be drawn on the UI thread, `SurfaceView` can be updated on a background thread
- This prevents blocking the UI thread during intensive rendering operations
- Ideal for games, video playback, camera preview, and other high-frame-rate content

**3. Hardware Acceleration Limitations:**
- `SurfaceView` cannot be hardware accelerated (as of Android 4.2 JellyBean)
- In contrast, 95% of operations on normal views are hardware-accelerated using OpenGL ES
- However, this trade-off is acceptable for scenarios requiring background thread rendering

**4. Additional Development Complexity:**
- More work is required to create a customized `SurfaceView`
- You need to:
  - Listen to `surfaceCreated/surfaceDestroyed` events
  - Create and manage a render thread
  - Synchronize the render thread and main thread properly
  - Handle the surface lifecycle

**5. Different Update Timing:**
- **Regular Views**: Update mechanism is constrained and controlled by the framework
  - Call `view.invalidate()` in UI thread or `view.postInvalidate()` in other threads
  - `View` won't update immediately but waits until next VSYNC event
  - VSYNC can be understood as a timer that fires every 16ms for a 60fps screen
  - All normal view updates are synchronized with VSYNC for better smoothness

- **SurfaceView**: You have direct control over when and how to render
  - Can render at any time from the background thread
  - Not bound to VSYNC timing
  - Provides more flexibility for custom rendering loops

**Basic Implementation:**

```kotlin
class MySurfaceView(context: Context) : SurfaceView(context), SurfaceHolder.Callback {

    private var renderThread: RenderThread? = null

    init {
        holder.addCallback(this)
    }

    override fun surfaceCreated(holder: SurfaceHolder) {
        // Surface is ready, start rendering thread
        renderThread = RenderThread(holder).apply {
            start()
        }
    }

    override fun surfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) {
        // Surface dimensions changed
    }

    override fun surfaceDestroyed(holder: SurfaceHolder) {
        // Stop rendering thread
        renderThread?.requestStop()
        renderThread?.join()
        renderThread = null
    }

    inner class RenderThread(private val holder: SurfaceHolder) : Thread() {
        private var running = true

        fun requestStop() {
            running = false
        }

        override fun run() {
            while (running) {
                val canvas = holder.lockCanvas()
                try {
                    // Perform drawing operations
                    synchronized(holder) {
                        // Draw on canvas
                        canvas?.let { drawContent(it) }
                    }
                } finally {
                    if (canvas != null) {
                        holder.unlockCanvasAndPost(canvas)
                    }
                }
            }
        }

        private fun drawContent(canvas: Canvas) {
            // Your drawing code here
            canvas.drawColor(Color.BLACK)
            // Draw other content...
        }
    }
}
```

**Use Cases:**

1. **Game Development**: High frame rate games requiring continuous rendering
2. **Video Playback**: Smooth video rendering without blocking UI thread
3. **Camera Preview**: Real-time camera feed display
4. **Custom Animations**: Complex animations that need precise frame control
5. **Data Visualization**: Real-time charts and graphs with frequent updates
6. **AR/VR Applications**: High-performance 3D rendering

**SurfaceView vs Regular `View`:**

| Feature | SurfaceView | Regular `View` |
|---------|-------------|--------------|
| Threading | Background thread rendering | UI thread only |
| Surface Buffer | Dedicated buffer | Shared buffer |
| Hardware Acceleration | Not supported (JB 4.2) | Fully supported |
| Update Timing | Manual control | VSYNC synchronized |
| Resource Usage | Higher | Lower |
| Use Case | High-performance rendering | Standard UI elements |
| Complexity | More complex | Simpler |

**Modern Alternatives:**

- **TextureView**: Can be hardware-accelerated and supports transformations, but higher memory usage
- **SurfaceView with Vulkan/OpenGL**: For modern 3D rendering
- **Jetpack Compose**: For declarative UI with efficient rendering

**Best Practices:**

1. Always implement `SurfaceHolder.Callback` to handle lifecycle events
2. Properly synchronize access to the `Canvas` between threads
3. Stop rendering thread when surface is destroyed to prevent memory leaks
4. Use `lockCanvas()` and `unlockCanvasAndPost()` carefully in try-finally blocks
5. Consider using `TextureView` if you need hardware acceleration and transformations

**Source**: [SurfaceView](https://developer.android.com/reference/android/view/SurfaceView)

## Ответ (RU)
`SurfaceView` — это специальное представление, которое предоставляет выделенную поверхность для рисования, встроенную в иерархию представлений. В отличие от обычных представлений, `SurfaceView` может обновляться в фоновом потоке, что делает его идеальным для сценариев высокопроизводительного рендеринга.

**Ключевые характеристики:**

**1. Выделенный буфер поверхности:**
- `SurfaceView` имеет выделенный буфер поверхности, в то время как все обычные представления используют один общий буфер, выделяемый ViewRoot
- Другими словами, `SurfaceView` требует больше ресурсов, но обеспечивает лучшую производительность для интенсивного рендеринга

**2. Рендеринг в фоновом потоке:**
- В отличие от обычных представлений, которые должны рисоваться в UI потоке, `SurfaceView` может обновляться в фоновом потоке
- Это предотвращает блокировку UI потока во время интенсивных операций рендеринга
- Идеально подходит для игр, воспроизведения видео, предварительного просмотра камеры и другого контента с высокой частотой кадров

**3. Ограничения аппаратного ускорения:**
- `SurfaceView` не может быть аппаратно ускорен (начиная с Android 4.2 JellyBean)
- В отличие от этого, 95% операций на обычных представлениях аппаратно ускоряются с использованием OpenGL ES
- Однако этот компромисс приемлем для сценариев, требующих рендеринга в фоновом потоке

**4. Дополнительная сложность разработки:**
- Для создания пользовательского `SurfaceView` требуется больше работы
- Необходимо:
  - Слушать события `surfaceCreated/surfaceDestroyed`
  - Создавать и управлять потоком рендеринга
  - Правильно синхронизировать поток рендеринга и главный поток
  - Обрабатывать жизненный цикл поверхности

**5. Отличная синхронизация обновлений:**
- **Обычные `View`**: Механизм обновления ограничен и контролируется фреймворком
  - Вызов `view.invalidate()` в UI потоке или `view.postInvalidate()` в других потоках
  - Представление не обновляется немедленно, а ждёт следующего события VSYNC
  - VSYNC можно понимать как таймер, который срабатывает каждые 16мс для экрана 60fps
  - Все обновления обычных представлений синхронизируются с VSYNC для лучшей плавности

- **SurfaceView**: Вы имеете прямой контроль над тем, когда и как выполнять рендеринг
  - Можно рендерить в любое время из фонового потока
  - Не привязан к таймингу VSYNC
  - Обеспечивает большую гибкость для пользовательских циклов рендеринга

**Варианты использования:**

1. **Разработка игр**: Игры с высокой частотой кадров, требующие непрерывного рендеринга
2. **Воспроизведение видео**: Плавный рендеринг видео без блокировки UI потока
3. **Предварительный просмотр камеры**: Отображение потока камеры в реальном времени
4. **Пользовательские анимации**: Сложные анимации, требующие точного управления кадрами
5. **Визуализация данных**: Графики и диаграммы в реальном времени с частыми обновлениями
6. **AR/VR приложения**: Высокопроизводительный 3D рендеринг

**SurfaceView vs Обычное `View`:**

| Функция | SurfaceView | Обычное `View` |
|---------|-------------|--------------|
| Потоки | Рендеринг в фоновом потоке | Только UI поток |
| Буфер поверхности | Выделенный буфер | Общий буфер |
| Аппаратное ускорение | Не поддерживается | Полностью поддерживается |
| Время обновления | Ручной контроль | Синхронизация с VSYNC |
| Использование ресурсов | Выше | Ниже |
| Вариант использования | Высокопроизводительный рендеринг | Стандартные UI элементы |
| Сложность | Более сложный | Проще |

**Лучшие практики:**

1. Всегда реализуйте `SurfaceHolder.Callback` для обработки событий жизненного цикла
2. Правильно синхронизируйте доступ к `Canvas` между потоками
3. Останавливайте поток рендеринга при уничтожении поверхности для предотвращения утечек памяти
4. Используйте `lockCanvas()` и `unlockCanvasAndPost()` осторожно в блоках try-finally
5. Рассмотрите использование `TextureView`, если нужно аппаратное ускорение и трансформации

---


## Follow-ups

- [[c-threading]]
- [[c-views]]
- [[q-viewgroup-vs-view-differences--android--easy]]


## References

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)


## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - `View`
- [[q-viewmodel-pattern--android--easy]] - `View`

### Related (Medium)
- [[q-testing-viewmodels-turbine--android--medium]] - `View`
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - `View`
- q-rxjava-pagination-recyclerview--android--medium - `View`
- [[q-what-is-viewmodel--android--medium]] - `View`
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - `View`

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]] - `View`
