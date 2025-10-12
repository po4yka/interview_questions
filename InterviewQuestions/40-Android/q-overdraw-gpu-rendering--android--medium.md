---
topic: android
tags:
  - android
  - performance
  - gpu
  - rendering
  - overdraw
  - optimization
  - difficulty/medium
difficulty: medium
status: draft
---

# What is Overdraw? / Что такое Overdraw?

**English**: What is Overdraw?

## Answer (EN)
An app may draw the same pixel more than once within a single frame, an event called **overdraw**. Overdraw is usually unnecessary and best eliminated. It manifests itself as a performance problem by wasting GPU time to render pixels that don't contribute to what the user sees on the screen.

**Understanding Overdraw:**

Overdraw occurs when your app draws the same pixel multiple times in a single frame. This happens when:
- Multiple UI elements are layered on top of each other
- Background colors are set on views that are completely covered by other views
- Complex view hierarchies cause unnecessary rendering passes

**Performance Impact:**

Overdraw can significantly impact app performance by:
- **Wasting GPU resources**: The GPU spends time rendering pixels that will be completely hidden
- **Reducing frame rate**: Excessive overdraw can cause frame drops and janky animations
- **Increasing battery consumption**: Unnecessary rendering work consumes more power
- **Slowing down rendering**: The more pixels that need to be drawn multiple times, the slower the rendering process

**Detecting Overdraw:**

Android provides a **Debug GPU Overdraw** tool in Developer Options that visualizes overdraw:
- **True color (no overdraw)**: Pixel drawn once
- **Blue**: Overdrawn once (1x)
- **Green**: Overdrawn twice (2x)
- **Pink**: Overdrawn three times (3x)
- **Red**: Overdrawn four or more times (4x+)

**Common Causes:**

1. **Unnecessary backgrounds**: Setting backgrounds on views that are completely covered
2. **Complex view hierarchies**: Deep nesting of layouts with overlapping views
3. **Default window backgrounds**: Using the default window background when it's not needed
4. **Custom drawing**: Inefficient `onDraw()` implementations that redraw entire areas

**Optimization Strategies:**

1. **Remove unnecessary backgrounds**: Don't set backgrounds on views that will be completely covered
2. **Flatten view hierarchies**: Use ConstraintLayout to reduce nesting
3. **Use clipRect()**: Clip drawing to visible areas only
4. **Optimize custom views**: Only draw what's necessary in `onDraw()`
5. **Use ViewStub**: For views that are rarely shown
6. **Remove default window background**: If your layout provides a full background

**Example - Removing Unnecessary Background:**

```xml
<!-- BAD: Layout has background that's completely covered -->
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

<!-- GOOD: Remove unnecessary background -->
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <ImageView
        android:src="@drawable/full_screen_image"
        android:scaleType="centerCrop"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
</LinearLayout>
```

**Example - Removing Window Background:**

```kotlin
// In Activity or Fragment
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    // Remove window background if your layout provides full background
    window.setBackgroundDrawable(null)

    setContentView(R.layout.activity_main)
}
```

**Best Practices:**

- Aim for no more than 2x overdraw (green) in most of your app
- Pay special attention to areas with 4x+ overdraw (red)
- Test your app with the GPU Overdraw tool regularly
- Profile rendering performance using GPU Profiling tools
- Consider the trade-off between view hierarchy complexity and overdraw

**Source**: [Reduce overdraw](https://developer.android.com/topic/performance/rendering/overdraw)

## Ответ (RU)
Приложение может рисовать один и тот же пиксель более одного раза в пределах одного кадра — это событие называется **overdraw** (избыточная отрисовка). Overdraw обычно не нужен и его лучше устранить. Он проявляется как проблема производительности, тратя время GPU на рендеринг пикселей, которые не вносят вклад в то, что пользователь видит на экране.

**Понимание Overdraw:**

Overdraw возникает, когда приложение рисует один и тот же пиксель несколько раз в одном кадре. Это происходит когда:
- Несколько UI элементов наложены друг на друга
- Цвета фона установлены на вью, которые полностью закрыты другими вью
- Сложные иерархии вью вызывают ненужные проходы рендеринга

**Влияние на производительность:**

Overdraw может значительно влиять на производительность приложения:
- **Тратит ресурсы GPU**: GPU тратит время на рендеринг пикселей, которые будут полностью скрыты
- **Снижает частоту кадров**: Чрезмерный overdraw может вызывать пропуски кадров и рывки анимаций
- **Увеличивает расход батареи**: Ненужная работа рендеринга потребляет больше энергии
- **Замедляет рендеринг**: Чем больше пикселей нужно рисовать многократно, тем медленнее процесс рендеринга

**Обнаружение Overdraw:**

Android предоставляет инструмент **Debug GPU Overdraw** в настройках разработчика, который визуализирует overdraw:
- **Истинный цвет (нет overdraw)**: Пиксель нарисован один раз
- **Синий**: Перерисован один раз (1x)
- **Зелёный**: Перерисован дважды (2x)
- **Розовый**: Перерисован три раза (3x)
- **Красный**: Перерисован четыре или более раз (4x+)

**Распространённые причины:**

1. **Ненужные фоны**: Установка фонов на вью, которые полностью закрыты
2. **Сложные иерархии вью**: Глубокая вложенность лэйаутов с перекрывающимися вью
3. **Фон окна по умолчанию**: Использование фона окна по умолчанию, когда он не нужен
4. **Пользовательская отрисовка**: Неэффективные реализации `onDraw()`, которые перерисовывают целые области

**Стратегии оптимизации:**

1. Удаляйте ненужные фоны
2. Упрощайте иерархии вью, используя ConstraintLayout
3. Используйте `clipRect()` для обрезки отрисовки только до видимых областей
4. Оптимизируйте пользовательские вью
5. Используйте ViewStub для редко показываемых вью
6. Удаляйте фон окна по умолчанию, если ваш лэйаут предоставляет полный фон

**Лучшие практики:**

- Стремитесь к не более чем 2x overdraw (зелёный) в большей части приложения
- Обращайте особое внимание на области с 4x+ overdraw (красный)
- Регулярно тестируйте приложение с инструментом GPU Overdraw
- Профилируйте производительность рендеринга, используя инструменты GPU Profiling
- Учитывайте компромисс между сложностью иерархии вью и overdraw
