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
updated: 2025-10-30
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

Что такое Overdraw и как его оптимизировать?

# Question (EN)

What is Overdraw and how to optimize it?

## Ответ (RU)

**Overdraw** — это многократная отрисовка одного пикселя в пределах одного кадра. Происходит при наложении UI элементов, избыточных фонах или глубокой вложенности layouts. Снижает производительность, тратя GPU время на рендеринг скрытых пикселей.

**Обнаружение:**

Инструмент **Debug GPU Overdraw** (Developer Options) визуализирует проблемные зоны:
- **Синий** — 1x overdraw (приемлемо)
- **Зелёный** — 2x overdraw (целевой уровень для большинства UI)
- **Розовый** — 3x overdraw (требует внимания)
- **Красный** — 4x+ overdraw (критично, нужна оптимизация)

**Основные причины:**

1. **Избыточные фоны** — background на view, полностью закрытой дочерними элементами
2. **Глубокая иерархия layouts** — вложенные LinearLayout/RelativeLayout с пересекающимися bounds
3. **Window background** — дефолтный фон окна, дублирующий корневой layout
4. **Неоптимальный onDraw()** — перерисовка всей области вместо изменённых участков

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
        window.setBackgroundDrawable(null) // если корневой layout покрывает весь экран
        setContentView(R.layout.activity_main)
    }
}
```

```kotlin
// ✅ clipRect() в кастомных View
override fun onDraw(canvas: Canvas) {
    canvas.clipRect(visibleBounds) // отрисовка только видимой области
    // рендеринг контента
}
```

**Практические советы:**

- **ConstraintLayout** вместо вложенных Linear/Relative — уменьшает глубину иерархии
- **ViewStub** для редко показываемых элементов — ленивая инициализация
- **Профилирование** — Systrace/Perfetto для анализа GPU load
- **Целевой уровень** — максимум 2x overdraw (зелёный) для основных экранов

## Answer (EN)

**Overdraw** is multiple rendering of the same pixel within a single frame. Occurs with layered UI elements, redundant backgrounds, or deeply nested layouts. Degrades performance by wasting GPU time on rendering hidden pixels.

**Detection:**

**Debug GPU Overdraw** tool (Developer Options) visualizes problem areas:
- **Blue** — 1x overdraw (acceptable)
- **Green** — 2x overdraw (target level for most UI)
- **Pink** — 3x overdraw (needs attention)
- **Red** — 4x+ overdraw (critical, optimization required)

**Root Causes:**

1. **Redundant backgrounds** — background on view completely covered by children
2. **Deep layout hierarchy** — nested LinearLayout/RelativeLayout with overlapping bounds
3. **Window background** — default window background duplicating root layout
4. **Inefficient onDraw()** — redrawing entire area instead of changed regions

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
        window.setBackgroundDrawable(null) // if root layout covers entire screen
        setContentView(R.layout.activity_main)
    }
}
```

```kotlin
// ✅ clipRect() in custom Views
override fun onDraw(canvas: Canvas) {
    canvas.clipRect(visibleBounds) // draw only visible area
    // render content
}
```

**Practical Guidelines:**

- **ConstraintLayout** instead of nested Linear/Relative — reduces hierarchy depth
- **ViewStub** for rarely shown elements — lazy initialization
- **Profiling** — Systrace/Perfetto for GPU load analysis
- **Target level** — max 2x overdraw (green) for primary screens

## Follow-ups

- How does Compose handle overdraw compared to View system?
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
