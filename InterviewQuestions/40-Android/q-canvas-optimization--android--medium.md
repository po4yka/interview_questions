---
id: 20251012-122794
title: Canvas Optimization / Оптимизация Canvas
aliases:
- Canvas Optimization
- Оптимизация Canvas
topic: android
subtopics:
- ui-views
- ui-graphics
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-android-performance-measurement-tools--android--medium
- q-canvas-drawing-optimization--android--hard
- q-android-app-lag-analysis--android--medium
created: 2025-10-13
updated: 2025-10-20
tags:
- android/ui-views
- android/ui-graphics
- difficulty/medium
---

# Вопрос (RU)
> Оптимизация Canvas?

# Question (EN)
> Canvas Optimization?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Core Principles
- **Target**: 60 FPS (16.67ms/frame); onDraw() < 5ms; zero allocations/frame.
- **Pre-allocate**: Paint/Path/Rect/Matrix as fields; reuse with reset()/set().
- **Cache**: bitmap cache for static content; clip to visible regions.
- **Hardware**: enable for complex/animated views; disable for compatibility.

### Zero Allocations Pattern
```kotlin
class OptimizedView : View {
  private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val rect = RectF()
    private val path = Path()

    override fun onDraw(canvas: Canvas) {
    rect.set(0f, 0f, width.toFloat(), height.toFloat())
    path.reset(); path.addCircle(width/2f, height/2f, radius, Path.Direction.CW)
        canvas.drawPath(path, paint)
    }
}
```

### Hardware Acceleration
- Enable for complex views: `setLayerType(LAYER_TYPE_HARDWARE, null)`.
- GPU caches drawing; 10x faster for static/complex content.

### Bitmap Caching
- Cache expensive drawings to Bitmap; redraw only when needed.
- Use for static content or slow-changing visuals.

### Clipping Optimization
- Get `canvas.clipBounds`; skip off-screen items.
- For scrollable content, only draw visible region (20x speedup).

### Paint Optimization
- Reuse Paint objects; disable anti-aliasing for straight lines; use opaque colors.

### Profiling
- Use `Trace.beginSection("section")`; analyze with Android Profiler/Systrace.
- Look for allocations, long draw times, GC events.

## Follow-ups
- How to measure and optimize specific drawing bottlenecks (path complexity, bitmap size, overdraw)?
- When to use software vs hardware rendering for custom views?
- How to implement incremental drawing for large datasets (pagination/virtualization)?

## References
- https://developer.android.com/topic/performance/rendering
- https://developer.android.com/topic/performance/inspect-gpu-rendering

## Related Questions

### Prerequisites (Easier)
- [[q-android-performance-measurement-tools--android--medium]]

### Related (Same Level)
- [[q-canvas-drawing-optimization--android--hard]]
- [[q-android-app-lag-analysis--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-art--android--medium]]
