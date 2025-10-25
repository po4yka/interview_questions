---
id: 20251012-122760
title: Android App Lag Analysis / Анализ тормозов приложения Android
aliases:
- Android App Lag Analysis
- Анализ тормозов приложения Android
topic: android
subtopics:
- performance-memory
- performance-rendering
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-android-performance-measurement-tools--android--medium
- q-compose-performance-optimization--android--hard
- q-strictmode-debugging--android--medium
created: 2025-10-13
updated: 2025-10-15
tags:
- android/performance-memory
- android/performance-rendering
- difficulty/medium
---

# Вопрос (RU)
> Что такое Анализ тормозов приложения Android?

---

# Question (EN)
> What are Android App Lag Analysis?

## Answer (EN)
App lag occurs when UI thread is blocked or frame rendering exceeds 16ms (60 FPS target). Understanding root causes and using proper diagnostic tools like Android Profiler is essential for smooth user experience.

**Common Causes:**

**1. Main Thread Blocking:**
- Synchronous DB/network calls
- Heavy computations
- Solution: Use coroutines, Dispatchers.IO/Default

```kotlin
// BAD: Blocking main thread
fun loadData() {
    val data = database.getAllUsers() // Synchronous DB call
    val result = heavyComputation(data)
    updateUI(result)
}

// GOOD: Async operations
fun loadData() {
    viewModelScope.launch {
        val data = withContext(Dispatchers.IO) {
            repository.getAllUsers()
        }
        val result = withContext(Dispatchers.Default) {
            heavyComputation(data)
        }
        _uiState.value = UiState.Success(result)
    }
}
```

**2. Memory Issues:**
- Memory leaks
- Excessive allocations
- Solution: LeakCanary, proper lifecycle management

```kotlin
// BAD: Memory leak
companion object {
    private var listener: OnDataListener? = null
}

// GOOD: Proper lifecycle
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.data.collect { data ->
            updateUI(data)
        }
    }
}
```

**3. Overdraw and Complex Layouts:**
- Deep view hierarchy
- Multiple pixel redraws
- Solution: ConstraintLayout, Compose, minimize nesting

```kotlin
// BAD: Deep hierarchy
<LinearLayout>
    <RelativeLayout>
        <FrameLayout>
            <ConstraintLayout>
                <TextView />
            </ConstraintLayout>
        </FrameLayout>
    </RelativeLayout>
</LinearLayout>

// GOOD: Flat hierarchy
<ConstraintLayout>
    <TextView
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent" />
</ConstraintLayout>
```

**4. Unoptimized Lists:**
- No recycling
- No DiffUtil
- Solution: RecyclerView with optimization

```kotlin
// RecyclerView optimization
recyclerView.apply {
    setHasFixedSize(true)
    setItemViewCacheSize(20)
    layoutManager = LinearLayoutManager(context).apply {
        isItemPrefetchEnabled = true
        initialPrefetchItemCount = 4
    }
}

// Use DiffUtil for efficient updates
val diffResult = DiffUtil.calculateDiff(ItemDiffCallback(oldItems, newItems))
diffResult.dispatchUpdatesTo(adapter)
```

**5. Poor Image Loading:**
- Loading large images
- Synchronous loading
- Solution: Glide/Coil, sampling, caching

```kotlin
// BAD: Loading large images
imageView.setImageBitmap(BitmapFactory.decodeFile(largeImagePath))

// GOOD: Proper image loading
Glide.with(imageView.context)
    .load(imagePath)
    .override(targetWidth, targetHeight)
    .diskCacheStrategy(DiskCacheStrategy.ALL)
    .into(imageView)
```

**Diagnostic Tools:**

**1. GPU Overdraw Detection:**
- Enable: Settings → Developer Options → Debug GPU overdraw
- Colors indicate overdraw levels (blue=2x, green=3x, red=4x+)

**2. Profile GPU Rendering:**
- Enable: Settings → Developer Options → Profile GPU Rendering
- Green line = 16ms target, bars above = dropped frames

**3. StrictMode:**
```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectDiskReads()
        .detectNetwork()
        .penaltyLog()
        .build()
)
```

**4. Android Profiler:**
- CPU Profiler: Identify hot methods
- Memory Profiler: Find memory leaks
- Network Profiler: Analyze requests
- Energy Profiler: Check battery consumption

**5. LeakCanary:**
- Automatically detects memory leaks in debug builds

## Follow-ups

- How do you measure frame rendering performance in production?
- What are the differences between GPU and CPU profiling?
- How do you optimize RecyclerView for large datasets?
- What are the best practices for image loading and caching?
- How do you prevent memory leaks in long-running services?

## References

- [Android Performance Best Practices](https://developer.android.com/topic/performance)
- [GPU Profiling](https://developer.android.com/topic/performance/rendering/profile-gpu)
- [Memory Profiler](https://developer.android.com/studio/profile/memory-profiler)
- [LeakCanary Documentation](https://square.github.io/leakcanary/)

## Related Questions

### Prerequisites (Easier)
- [[q-android-performance-measurement-tools--android--medium]] - Performance tools
- [[q-strictmode-debugging--android--medium]] - StrictMode debugging

### Related (Medium)
- [[q-compose-performance-optimization--android--hard]] - Compose performance
- [[q-performance-monitoring-jank-compose--android--medium]] - Jank monitoring
- [[q-performance-optimization-android--android--medium]] - Performance optimization

### Advanced (Harder)
- [[q-what-is-layout-performance-measured-in--android--medium]] - Layout performance
- [[q-performance-optimization-android--android--medium]] - Advanced optimization