---
id: android-301
title: Overdraw Gpu Rendering / Overdraw и GPU рендеринг
aliases:
- Overdraw GPU Rendering
- Overdraw и GPU рендеринг
topic: android
subtopics:
- performance-rendering
- profiling
- ui-graphics
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-perfetto
- c-performance
- q-android-performance-measurement-tools--android--medium
- q-performance-optimization-android--android--medium
- q-what-is-layout-performance-measured-in--android--medium
created: 2025-10-15
updated: 2025-11-10
tags:
- android/performance-rendering
- android/profiling
- android/ui-graphics
- difficulty/medium
- gpu
- overdraw
- performance
- rendering
sources: []

---

# Вопрос (RU)

> Что такое Overdraw и как его оптимизировать?

# Question (EN)

> What is Overdraw and how to optimize it?

## Ответ (RU)

**Overdraw** — это многократная отрисовка одного пикселя в пределах одного кадра. Происходит при наложении UI элементов, избыточных фонах или глубокой вложенности layouts. Снижает производительность, тратя GPU время на рендеринг скрытых пикселей.

**Обнаружение:**

Инструмент **Debug GPU Overdraw** (Developer Options) визуализирует, сколько раз каждый пиксель был перерисован:
- **Синий** — исходный цвет содержимого (0 дополнительных слоёв, без overdraw)
- **Зелёный** — 1x overdraw (1 дополнительный слой поверх базового, обычно приемлемо)
- **Светло-красный / розовый** — 2x overdraw (нужно контролировать)
- **Тёмно-красный** — 3x+ overdraw (критично, нужна оптимизация)

(Оттенки могут незначительно отличаться между версиями Android, важно относительная интенсивность цвета: чем "краснее", тем хуже.)

**Основные причины:**

1. **Избыточные фоны** — background на view, полностью закрытой дочерними элементами
2. **Глубокая иерархия layouts** — вложенные LinearLayout/RelativeLayout с пересекающимися bounds
3. **Window background** — дефолтный фон окна, дублирующий корневой layout
4. **Неоптимальный onDraw()** — перерисовка всей области вместо изменённых участков либо отрисовка вне реально видимых границ

**Стратегии оптимизации:**

```xml
<!-- ❌ Избыточный background -->
<LinearLayout
    android:background="@color/white"
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    <ImageView
        android:src="@drawable/full_screen_image"
        android:scaleType="centerCrop"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
</LinearLayout>

<!-- ✅ Background удалён -->
<FrameLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    <ImageView
        android:src="@drawable/full_screen_image"
        android:scaleType="centerCrop"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
</FrameLayout>
```

```kotlin
// ✅ Удаление window background
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Если корневой layout полностью покрывает окно, фон можно убрать,
        // чтобы избежать лишнего слоя отрисовки.
        window.setBackgroundDrawable(null)
        setContentView(R.layout.activity_main)
    }
}
```

```kotlin
// ✅ clipRect() в кастомных View (аккуратно)
override fun onDraw(canvas: Canvas) {
    // Ограничивать область рисования имеет смысл только если это существенно
    // уменьшает количество реально отрисовываемых пикселей;
    // сами операции clipping тоже имеют стоимость.
    canvas.clipRect(visibleBounds)
    // рендеринг контента
}
```

**Практические советы:**

- **ConstraintLayout** вместо вложенных Linear/Relative — уменьшает глубину иерархии
- **ViewStub** для редко показываемых элементов — ленивая инициализация
- **Профилирование** — Perfetto / Android Studio профайлеры для анализа GPU и рендеринга (Systrace устарел, заменён современными инструментами)
- **Целевой уровень** — стремиться к минимуму слоёв; 0–1 дополнительный слой (зелёный) для основных экранов считается хорошей практикой, интенсивный красный — сигнал к оптимизации

## Answer (EN)

**Overdraw** is multiple rendering of the same pixel within a single frame. It occurs with layered UI elements, redundant backgrounds, or deeply nested layouts. It degrades performance by wasting GPU time on drawing pixels that end up hidden.

**Detection:**

The **Debug GPU Overdraw** tool (Developer Options) visualizes how many times each pixel is redrawn:
- **Blue** — original content color (0 extra layers, no overdraw)
- **Green** — 1x overdraw (1 extra layer on top of base, usually acceptable)
- **Light red / pink** — 2x overdraw (should be monitored)
- **Dark red** — 3x+ overdraw (critical, optimization required)

(Exact shades may vary across Android versions; the key is that "more red" means worse.)

**Root Causes:**

1. **Redundant backgrounds** — background on a view that is fully covered by its children
2. **Deep layout hierarchy** — nested LinearLayout/RelativeLayout with overlapping bounds
3. **Window background** — default window background duplicating the root layout
4. **Inefficient onDraw()** — redrawing the entire area instead of changed regions, or drawing outside the actually visible bounds

**Optimization Strategies:**

```xml
<!-- ❌ Redundant background -->
<LinearLayout
    android:background="@color/white"
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    <ImageView
        android:src="@drawable/full_screen_image"
        android:scaleType="centerCrop"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
</LinearLayout>

<!-- ✅ Background removed -->
<FrameLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    <ImageView
        android:src="@drawable/full_screen_image"
        android:scaleType="centerCrop"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
</FrameLayout>
```

```kotlin
// ✅ Remove window background
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // If the root layout fully covers the window, removing the window background
        // avoids an extra overdraw layer.
        window.setBackgroundDrawable(null)
        setContentView(R.layout.activity_main)
    }
}
```

```kotlin
// ✅ clipRect() in custom Views (with care)
override fun onDraw(canvas: Canvas) {
    // Use clipping only when it meaningfully reduces the number of drawn pixels;
    // clip operations themselves have a cost.
    canvas.clipRect(visibleBounds)
    // render content
}
```

**Practical Guidelines:**

- **ConstraintLayout** instead of nested Linear/Relative — reduces hierarchy depth
- **ViewStub** for rarely shown elements — lazy initialization
- **Profiling** — use Perfetto / Android Studio profilers to analyze GPU and rendering (Systrace is deprecated and replaced by modern tools)
- **Target level** — aim to minimize layers; 0–1 extra layer (green) on primary screens is a good baseline, heavy dark red areas indicate issues that require optimization

## Follow-ups

- How does Compose handle overdraw compared to `View` system?
- What's the performance impact of translucent views on overdraw?
- How to optimize overdraw in RecyclerView with complex items?
- When is clipRect() applicable and when does it add overhead?
- How does hardware acceleration affect overdraw detection and optimization?

## References

- [Android Developer - Reduce Overdraw](https://developer.android.com/topic/performance/rendering/overdraw)
- [[q-android-performance-measurement-tools--android--medium]]
- [[q-performance-optimization-android--android--medium]]

## Related Questions

### Prerequisites / Concepts

- [[c-perfetto]]
- [[c-performance]]


### Prerequisites
- [[q-what-is-layout-performance-measured-in--android--medium]] — Understanding rendering metrics

### Related
- [[q-android-performance-measurement-tools--android--medium]] — Profiling and debugging tools
- [[q-performance-optimization-android--android--medium]] — General performance optimization strategies
- [[q-performance-monitoring-jank-compose--android--medium]] — Frame drops and jank detection

### Advanced
- [[q-compose-performance-optimization--android--hard]] — Compose-specific rendering optimizations
- [[q-surfaceview-rendering--android--medium]] — Advanced rendering techniques
- [[q-opengl-advanced-rendering--android--medium]] — Low-level GPU rendering
