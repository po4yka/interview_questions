---
id: 20251012-122793
title: Canvas Drawing Optimization / Оптимизация отрисовки Canvas
aliases:
- Canvas Drawing Optimization
- Оптимизация отрисовки Canvas
topic: android
subtopics:
- ui-views
- performance-rendering
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-android-performance-measurement-tools--android--medium
- q-android-runtime-art--android--medium
- q-android-app-lag-analysis--android--medium
created: 2025-10-15
updated: 2025-10-20
tags:
- android/ui-views
- android/performance-rendering
- difficulty/hard
---

# Вопрос (RU)
> Оптимизация отрисовки Canvas?

# Question (EN)
> Canvas Drawing Optimization?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Core Theory
- **Target**: 60 FPS (16.67ms/frame); onDraw() < 5ms; zero allocations/frame.
- **Avoid**: object creation in onDraw() → GC thrashing → dropped frames. Use [[c-profiling]] to identify bottlenecks.
- **Optimize**: pre-allocate, cache, clip, hardware accelerate to prevent [[c-memory-leaks]].

### Zero Allocations
- Pre-allocate Paint/Path/Rect objects as fields; reuse with reset()/set().
- Never create objects inside onDraw(); move to init/onSizeChanged.

### Minimal snippet (no allocations)
```kotlin
class OptimizedView : View {
  private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
  private val rect = Rect()
  private val path = Path()

  override fun onDraw(canvas: Canvas) {
    rect.set(0, 0, width, height) // Reuse, no alloc
    path.reset(); path.moveTo(0f, 0f); path.lineTo(width.toFloat(), height.toFloat())
    canvas.drawPath(path, paint)
  }
}
```

### Hardware Acceleration
- Enable hardware layers for complex/animated views (LAYER_TYPE_HARDWARE).
- GPU caches drawing; 10x faster for static/complex content.

### Bitmap Caching
- Cache expensive drawings to Bitmap; redraw only when needed.
- Use for static content or slow-changing visuals.

### Clipping
- Get canvas.clipBounds; skip drawing off-screen items.
- For scrollable content, only draw visible region (20x speedup).

### Paint Optimization
- Reuse Paint objects; disable anti-aliasing for straight lines; use opaque colors.

### Profiling
- Use Trace.beginSection("section"); analyze with Android Profiler/Systrace and [[c-profiling]] tools.
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
- [[q-android-runtime-art--android--medium]]
- [[q-android-app-lag-analysis--android--medium]]

### Advanced (Harder)
- [[q-android-performance-measurement-tools--android--medium]]
