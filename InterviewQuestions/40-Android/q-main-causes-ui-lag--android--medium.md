---
topic: android
tags:
  - android
  - android/performance
  - android/ui
  - animations
  - images
  - layouts
  - main-thread
  - optimization
  - performance
  - threading
  - ui
difficulty: medium
status: draft
---

# Какие основные причины торможения UI?

**English**: What are the main causes of UI lag?

## Answer (EN)
The main causes of **UI lag** (janky user interface) in Android applications include:

### 1. Heavy Operations on Main Thread

**Problem:** Long-running operations block UI rendering.

**Examples:**
- Network requests
- Database queries
- File I/O
- Complex calculations
- Image processing

**Solution:** Execute heavy operations in background threads:

```kotlin
// - BAD - Blocks UI thread
fun loadData() {
    val data = database.getAllUsers()  // Blocks UI!
    updateUI(data)
}

// - GOOD - Using Coroutines
suspend fun loadData() {
    val data = withContext(Dispatchers.IO) {
        database.getAllUsers()  // Runs on background thread
    }
    updateUI(data)  // Back to main thread
}

// - GOOD - Using Flow
fun observeUsers() {
    viewModelScope.launch {
        database.getUsersFlow()
            .flowOn(Dispatchers.IO)
            .collect { users ->
                updateUI(users)  // UI updates on main thread
            }
    }
}
```

**Modern approaches:**
- **Kotlin Coroutines** (recommended)
- **WorkManager** (for deferrable background work)
- **RxJava** (reactive streams)
- ~~AsyncTask~~ (deprecated since API 30)
- ~~Thread/Handler~~ (low-level, error-prone)

---

### 2. Unoptimized Layouts

**Problem:** Complex view hierarchies cause slow rendering.

**Examples:**
- Deeply nested LinearLayouts
- Multiple RelativeLayouts
- Excessive ViewGroups
- Unnecessary layout passes

**Solution:** Use simpler, flatter layouts:

```xml
<!-- - BAD - Deeply nested (4 levels) -->
<LinearLayout>
    <RelativeLayout>
        <LinearLayout>
            <FrameLayout>
                <TextView />
                <ImageView />
            </FrameLayout>
        </LinearLayout>
    </RelativeLayout>
</LinearLayout>

<!-- - GOOD - Flat hierarchy (1 level) -->
<androidx.constraintlayout.widget.ConstraintLayout>
    <TextView
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

    <ImageView
        app:layout_constraintStart_toEndOf="@id/textView"
        app:layout_constraintTop_toTopOf="parent" />
</androidx.constraintlayout.widget.ConstraintLayout>
```

**Best practices:**
- Use **ConstraintLayout** to reduce nesting
- Avoid nested weights in LinearLayout
- Use **ViewStub** for conditionally displayed views
- Use **merge** tag to eliminate unnecessary ViewGroups
- Profile with **Layout Inspector** tool

---

### 3. Unoptimized Image Handling

**Problem:** Loading large images causes memory issues and lag.

**Examples:**
- Loading full-resolution images for thumbnails
- No caching
- Synchronous loading
- Memory leaks from bitmaps

**Solution:** Use image loading libraries:

```kotlin
// - BAD - Manual bitmap loading
val bitmap = BitmapFactory.decodeFile(imagePath)  // Full size!
imageView.setImageBitmap(bitmap)  // Blocks UI!

// - GOOD - Using Glide
Glide.with(context)
    .load(imageUrl)
    .placeholder(R.drawable.placeholder)
    .error(R.drawable.error)
    .into(imageView)

// - GOOD - Using Coil (Kotlin-first)
imageView.load(imageUrl) {
    crossfade(true)
    placeholder(R.drawable.placeholder)
    transformations(CircleCropTransformation())
}

// - GOOD - Using Picasso
Picasso.get()
    .load(imageUrl)
    .resize(200, 200)
    .centerCrop()
    .into(imageView)
```

**Features of image libraries:**
- Automatic resizing
- Memory/disk caching
- Async loading
- Lifecycle awareness
- Transformation support

---

### 4. Frequent UI Updates

**Problem:** Too many UI updates cause excessive rendering.

**Examples:**
- Updating every item in RecyclerView
- Rapid TextView changes
- Excessive notifyDataSetChanged()
- Animation frame updates

**Solution:** Minimize and batch UI updates:

```kotlin
// - BAD - Updates entire list
fun updateAllItems() {
    adapter.notifyDataSetChanged()  // Redraws everything!
}

// - GOOD - Update specific items
fun updateItem(position: Int) {
    adapter.notifyItemChanged(position)
}

// - GOOD - Batch updates
fun updateMultipleItems(positions: List<Int>) {
    positions.forEach { position ->
        adapter.notifyItemChanged(position)
    }
}

// - BEST - Use DiffUtil
fun updateList(newList: List<Item>) {
    val diffResult = DiffUtil.calculateDiff(
        MyDiffCallback(oldList, newList)
    )
    oldList = newList
    diffResult.dispatchUpdatesTo(adapter)
}
```

**Debouncing rapid updates:**

```kotlin
private val updateHandler = Handler(Looper.getMainLooper())
private var updateRunnable: Runnable? = null

fun scheduleUpdate(data: Data) {
    updateRunnable?.let { updateHandler.removeCallbacks(it) }
    updateRunnable = Runnable {
        updateUI(data)
    }.also {
        updateHandler.postDelayed(it, 300)  // Debounce 300ms
    }
}
```

---

### 5. Unoptimized Animations

**Problem:** Heavy animations drop frames (< 60fps).

**Examples:**
- Animating layout changes
- ObjectAnimator on complex properties
- Too many simultaneous animations
- AnimationDrawable with large images

**Solution:** Use hardware-accelerated animations:

```kotlin
// - BAD - Layout animation (slow)
TranslateAnimation(0f, 100f, 0f, 0f).apply {
    duration = 300
    view.startAnimation(this)
}

// - GOOD - ViewPropertyAnimator (hardware-accelerated)
view.animate()
    .translationX(100f)
    .setDuration(300)
    .start()

// - GOOD - TransitionManager for layout changes
TransitionManager.beginDelayedTransition(container)
view.visibility = View.VISIBLE

// - GOOD - Jetpack Compose animations
AnimatedVisibility(visible = isVisible) {
    Text("Hello")
}
```

**Limiting simultaneous animations:**

```kotlin
private var activeAnimations = 0
private const val MAX_ANIMATIONS = 3

fun animateIfPossible(view: View) {
    if (activeAnimations >= MAX_ANIMATIONS) {
        view.translationX = targetX  // Jump to final position
        return
    }

    activeAnimations++
    view.animate()
        .translationX(targetX)
        .withEndAction { activeAnimations-- }
        .start()
}
```

---

## Additional Causes

### 6. Memory Issues

**Problem:** Low memory causes GC pauses.

**Solutions:**
- Fix memory leaks (use LeakCanary)
- Reduce object allocations
- Use object pools
- Optimize bitmap memory

### 7. Overdraw

**Problem:** Drawing pixels multiple times wastes GPU.

**Solutions:**
- Remove unnecessary backgrounds
- Use clipRect() in custom views
- Enable "Debug GPU overdraw" in Developer Options

### 8. Slow Custom Views

**Problem:** Inefficient onDraw() causes lag.

**Solutions:**
- Avoid allocations in onDraw()
- Cache Paint objects
- Use canvas.save/restore efficiently
- Minimize drawing operations

---

## Performance Measurement Tools

### 1. Systrace / Perfetto

**Captures system-level traces:**

```bash

# Capture trace
python systrace.py -a com.myapp -t 10 gfx view

# Analyze in chrome://tracing
```

### 2. Layout Inspector

**Analyzes view hierarchy:**

```
Tools → Layout Inspector → Select Device
```

### 3. Profile GPU Rendering

**Shows frame rendering time:**

```
Settings → Developer Options → Profile GPU Rendering → On screen as bars
```

Green line = 16ms (60fps threshold)

### 4. StrictMode

**Detects main thread violations:**

```kotlin
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectDiskReads()
            .detectDiskWrites()
            .detectNetwork()
            .penaltyLog()
            .build()
    )

    StrictMode.setVmPolicy(
        StrictMode.VmPolicy.Builder()
            .detectLeakedSqlLiteObjects()
            .detectLeakedClosableObjects()
            .penaltyLog()
            .build()
    )
}
```

---

## Summary Table

| Cause | Problem | Solution |
|-------|---------|----------|
| **Main thread blocking** | Network, DB, heavy operations | Coroutines, WorkManager |
| **Complex layouts** | Nested ViewGroups | ConstraintLayout, merge, ViewStub |
| **Unoptimized images** | Large bitmaps, no caching | Glide, Coil, Picasso |
| **Frequent UI updates** | Excessive redraws | DiffUtil, batch updates, debouncing |
| **Heavy animations** | Frame drops | ViewPropertyAnimator, TransitionManager |
| **Memory issues** | GC pauses | Fix leaks, reduce allocations |
| **Overdraw** | Drawing same pixels multiple times | Remove backgrounds, clipRect |
| **Slow custom views** | Inefficient onDraw() | Cache objects, minimize drawing |

---

## Best Practices

1. - **Keep frame time < 16ms** (60fps)
2. - **Never block main thread** (use coroutines)
3. - **Use ConstraintLayout** for complex UIs
4. - **Use image loading libraries** (Glide, Coil)
5. - **Batch UI updates** (DiffUtil)
6. - **Use hardware-accelerated animations**
7. - **Profile performance** (Systrace, GPU Profiling)
8. - **Enable StrictMode** in debug builds
9. - **Fix memory leaks** (LeakCanary)
10. - **Test on low-end devices**

---

## Ответ (RU)
Основные причины торможения пользовательского интерфейса (UI) в Android-приложениях:

1. **Тяжелые операции в главном потоке** - Решение: Выполнять тяжелые операции в фоновом потоке, используя Kotlin Coroutines или WorkManager (AsyncTask устарел).

2. **Неоптимизированные макеты (layouts)** - Решение: Использовать более простые и плоские макеты, рассматривать использование ConstraintLayout.

3. **Неоптимизированная работа с изображениями** - Решение: Использовать библиотеки для загрузки изображений такие как Glide, Coil или Picasso.

4. **Частое обновление UI** - Решение: Минимизировать количество обновлений UI, объединять изменения и обновлять UI только при необходимости.

5. **Неоптимизированные анимации** - Решение: Использовать ViewPropertyAnimator или TransitionManager для более плавных анимаций, ограничить количество одновременно выполняемых анимаций.


---

## Related Questions

### Related (Medium)
- [[q-dagger-build-time-optimization--android--medium]] - Performance, Ui
- [[q-build-optimization-gradle--gradle--medium]] - Performance, Ui
- [[q-android-build-optimization--android--medium]] - Performance, Ui
- [[q-compose-modifier-order-performance--jetpack-compose--medium]] - Performance
- [[q-macrobenchmark-startup--performance--medium]] - Performance

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Performance
