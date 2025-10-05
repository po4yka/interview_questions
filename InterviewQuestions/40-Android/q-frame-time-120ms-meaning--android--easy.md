---
tags:
  - android
  - performance
  - rendering
  - frame-rate
  - fps
  - ui-performance
  - easy_kotlin
  - android/performance
difficulty: easy
---

# Если профайлер показывает тебе что какой-нибудь фрейм занял 120 миллисекунд, что это значит?

**English**: If profiler shows that a frame took 120 milliseconds, what does it mean?

## Answer

If the profiler shows that rendering a frame took **120 milliseconds**, this means the frame **executed too long**, which leads to **freezes and lags** in the user interface.

**Frame Budget:**

- **60 fps target**: 16.67ms per frame
- **120ms frame**: 7x over budget!
- **Result**: Dropped ~7 frames

**Calculation:**

```
60 fps = 1000ms / 60 = 16.67ms per frame
120ms frame = 120 / 16.67 = ~7 frames dropped

User sees: freeze/stutter for 120ms
```

**Visual Impact:**

```
Normal (16ms):    ████████████████ Smooth
Your frame (120ms): ████████████████████████████████████████████████████████████████████████ JANKY!

Timeline:
0ms    16ms   32ms   48ms   64ms   80ms   96ms   112ms  120ms
|------|------|------|------|------|------|------|------|
 1      2      3      4      5      6      7      8      Your frame completes

User sees 7 dropped frames = visible stutter
```

**Profile GPU Rendering Visualization:**

```
Green line = 16ms (60 fps budget)

     |
120ms|                                    ████ ← Your frame (BAD!)
     |                                    ████
     |                                    ████
     |                                    ████
     |                                    ████
     |                                    ████
 16ms|────────────────────────────────────────────
     |  ████ ████   ████ ████   ████ ████
     |  ████ ████   ████ ████   ████ ████
     |__________________________|___|___|___|____
        Normal frames            ^
                                 Spike!
```

**Common Causes:**

**1. Heavy UI work on main thread:**

```kotlin
// ❌ BAD - Blocks UI for 120ms
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    // Complex calculation on main thread
    val processedData = heavyProcessing(data[position])  // 120ms!
    holder.bind(processedData)
}
```

**2. Synchronous network/database:**

```kotlin
// ❌ BAD
button.setOnClickListener {
    val data = database.query()  // Blocks UI!
    updateUI(data)
}
```

**3. Large list without recycling:**

```kotlin
// ❌ BAD
for (item in largeList) {
    val view = inflate(R.layout.item)  // Many inflations!
    container.addView(view)
}
```

**Solutions:**

```kotlin
// ✅ GOOD - Move work off main thread
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    viewModelScope.launch(Dispatchers.Default) {
        val processed = heavyProcessing(data[position])
        withContext(Dispatchers.Main) {
            holder.bind(processed)
        }
    }
}

// ✅ GOOD - Async operations
button.setOnClickListener {
    viewModelScope.launch {
        val data = withContext(Dispatchers.IO) {
            database.query()
        }
        updateUI(data)
    }
}

// ✅ GOOD - Use RecyclerView
recyclerView.adapter = MyAdapter(largeList)  // Efficient recycling
```

**Measuring Frame Time:**

```kotlin
// Choreographer - frame callback
Choreographer.getInstance().postFrameCallback(object : Choreographer.FrameCallback {
    var lastFrameTime = 0L

    override fun doFrame(frameTimeNanos: Long) {
        if (lastFrameTime != 0L) {
            val frameDuration = (frameTimeNanos - lastFrameTime) / 1_000_000
            if (frameDuration > 16) {
                Log.w("Performance", "Slow frame: ${frameDuration}ms")
            }
        }
        lastFrameTime = frameTimeNanos
        Choreographer.getInstance().postFrameCallback(this)
    }
})
```

**Frame Time Guidelines:**

| Frame Time | FPS | User Experience |
|------------|-----|-----------------|
| 16ms | 60 | ✅ Smooth |
| 33ms | 30 | ⚠️ Noticeable |
| 120ms | 8 | ❌ Janky, freezes |
| 1000ms | 1 | 💥 ANR risk |

**Summary:**

- **120ms frame** = **7 dropped frames** at 60 fps
- **Causes**: Heavy main thread work, sync I/O, inefficient rendering
- **Effect**: Visible stuttering and lag
- **Solution**: Move work off main thread, optimize rendering, use async operations
- **Target**: Keep frames under 16ms for smooth 60 fps

## Ответ

Если профайлер показывает что рендеринг какого-либо фрейма занял 120 миллисекунд это означает что этот фрейм выполнялся слишком долго что приводит к фризам и лагам в пользовательском интерфейсе.

Цель: 60 fps = 16.67ms на фрейм
120ms = пропущено ~7 кадров = заметные лаги

