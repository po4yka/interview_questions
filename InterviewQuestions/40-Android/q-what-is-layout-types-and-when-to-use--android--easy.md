---
id: android-134
title: "What Is Layout Types And When To Use / What Is Layout Types и When To Use"
aliases: ["What Is Layout Types And When To Use", "What Is Layout Types и When To Use"]
topic: android
subtopics: [ui-views]
question_kind: theory
difficulty: easy
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-views, q-annotation-processing--android--medium, q-play-feature-delivery--android--medium]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android, android/ui-views, difficulty/easy, layouts, ui, xml]
---

# Вопрос (RU)

> Что такое layout, какие их виды бывают и когда их использовать?

# Question (EN)

> What is layout, what types exist and when to use them?

---

## Ответ (RU)

**Layout** — это способ определения пользовательского интерфейса приложения. Описывает как элементы интерфейса (виджеты) располагаются и позиционируются на экране. Макеты задаются через XML файлы или программно в коде.

### Основные Типы Layout

#### 1. LinearLayout

Располагает дочерние элементы в одну строку или столбец (вертикально или горизонтально).

```xml
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="First Item" />

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Second Item" />
</LinearLayout>
```

**Когда использовать:**
- Простые интерфейсы с последовательным расположением элементов
- Формы с вертикальным или горизонтальным размещением
- Когда нужно равномерное распределение веса между дочерними элементами (`layout_weight`)

#### 2. RelativeLayout

Позиционирует дочерние элементы относительно друг друга или относительно родительского контейнера.

```xml
<RelativeLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <TextView
        android:id="@+id/title"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_centerHorizontal="true"
        android:text="Title" />

    <Button
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_below="@id/title"  <!-- ✅ Relative positioning -->
        android:layout_centerHorizontal="true"
        android:text="Click Me" />
</RelativeLayout>
```

**Когда использовать:**
- Элементы должны быть позиционированы относительно друг друга
- Нужно избежать глубокой вложенности view-иерархии
- Создание перекрывающихся view

NOTE: Для новых проектов рекомендуется ConstraintLayout.

#### 3. ConstraintLayout

Обеспечивает гибкую систему constraints для позиционирования элементов относительно друг друга и границ контейнера.

```xml
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <TextView
        android:id="@+id/title"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Title"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent" /> <!-- ✅ Centered horizontally -->

    <Button
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Button"
        app:layout_constraintTop_toBottomOf="@id/title"
        app:layout_constraintStart_toStartOf="parent" />
</androidx.constraintlayout.widget.ConstraintLayout>
```

**Когда использовать:**
- Сложные интерфейсы требующие точного позиционирования
- Плоская view-иерархия для улучшения производительности
- Адаптивные дизайны для разных размеров экранов
- Современная Android разработка (рекомендуется по умолчанию)

#### 4. FrameLayout

Создан для размещения одного дочернего view, но может содержать несколько view, наложенных друг на друга.

```xml
<FrameLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <ImageView
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:src="@drawable/background" />

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="center"
        android:text="Overlay Text" /> <!-- ✅ Overlay on image -->
</FrameLayout>
```

**Когда использовать:**
- Контейнеры для фрагментов
- Простые overlay
- Контейнеры для одного view

#### 5. GridLayout

Располагает дочерние элементы в виде сетки.

```xml
<GridLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:columnCount="2"
    android:rowCount="2">

    <Button android:text="1" />
    <Button android:text="2" />
    <Button android:text="3" />
    <Button android:text="4" />
</GridLayout>
```

**Когда использовать:**
- Макеты калькуляторов
- Галереи изображений
- Сетки кнопок

### Рекомендации По Выбору

| Layout Type      | Производительность | Гибкость | Сложность | Лучше для        |
| ---------------- | ------------------ | -------- | --------- | ---------------- |
| LinearLayout     | Хорошая            | Низкая   | Низкая    | Простые списки   |
| RelativeLayout   | Средняя            | Средняя  | Средняя   | Legacy приложения|
| ConstraintLayout | Лучшая             | Высокая  | Средняя   | Современные app  |
| FrameLayout      | Лучшая             | Низкая   | Низкая    | Overlay          |
| GridLayout       | Хорошая            | Средняя  | Средняя   | Сетки            |

### Best Practices

1. **Предпочитайте ConstraintLayout** для сложных макетов
2. **Избегайте глубокой вложенности** layout-ов (влияет на производительность)
3. **Используйте merge tag** для устранения избыточных ViewGroup
4. **Используйте include tag** для переиспользуемых layout-ов
5. **Учитывайте производительность** при выборе типа layout

## Answer (EN)

A **layout** defines how user interface elements (widgets) are arranged and positioned on the screen. Layouts are typically defined using XML files or programmatically in code.

### Main Layout Types

#### 1. LinearLayout

Arranges child elements in a single row or column (vertically or horizontally).

```xml
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="First Item" />

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Second Item" />
</LinearLayout>
```

**When to use:**
- Simple interfaces with sequential arrangement
- Forms with vertical or horizontal placement
- When equal weight distribution is needed among children (`layout_weight`)

#### 2. RelativeLayout

Positions child elements relative to each other or to the parent container.

```xml
<RelativeLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <TextView
        android:id="@+id/title"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_centerHorizontal="true"
        android:text="Title" />

    <Button
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_below="@id/title"  <!-- ✅ Relative positioning -->
        android:layout_centerHorizontal="true"
        android:text="Click Me" />
</RelativeLayout>
```

**When to use:**
- Elements need relative positioning to each other
- Avoiding deep view hierarchies
- Creating overlapping views

NOTE: For new projects, ConstraintLayout is recommended.

#### 3. ConstraintLayout

Provides a flexible constraint system for positioning elements relative to each other and container boundaries.

```xml
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <TextView
        android:id="@+id/title"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Title"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent" /> <!-- ✅ Centered horizontally -->

    <Button
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Button"
        app:layout_constraintTop_toBottomOf="@id/title"
        app:layout_constraintStart_toStartOf="parent" />
</androidx.constraintlayout.widget.ConstraintLayout>
```

**When to use:**
- Complex interfaces requiring precise positioning
- Flat view hierarchies for better performance
- Responsive designs adapting to different screen sizes
- Modern Android development (recommended default)

#### 4. FrameLayout

Designed to hold a single child view, though it can contain multiple views stacked on top of each other.

```xml
<FrameLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <ImageView
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:src="@drawable/background" />

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="center"
        android:text="Overlay Text" /> <!-- ✅ Overlay on image -->
</FrameLayout>
```

**When to use:**
- Fragment containers
- Simple overlays
- Single view containers

#### 5. GridLayout

Arranges children in a grid structure.

```xml
<GridLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:columnCount="2"
    android:rowCount="2">

    <Button android:text="1" />
    <Button android:text="2" />
    <Button android:text="3" />
    <Button android:text="4" />
</GridLayout>
```

**When to use:**
- Calculator layouts
- Image galleries
- Button grids

### Selection Guidelines

| Layout Type      | Performance | Flexibility | Complexity | Best For          |
| ---------------- | ----------- | ----------- | ---------- | ----------------- |
| LinearLayout     | Good        | Low         | Low        | Simple lists      |
| RelativeLayout   | Moderate    | Moderate    | Moderate   | Legacy apps       |
| ConstraintLayout | Best        | High        | Moderate   | Modern apps       |
| FrameLayout      | Best        | Low         | Low        | Overlays          |
| GridLayout       | Good        | Moderate    | Moderate   | Grid structures   |

### Best Practices

1. **Prefer ConstraintLayout** for complex layouts
2. **Avoid deep nesting** of layouts (affects performance)
3. **Use merge tags** to eliminate redundant ViewGroups
4. **Use include tags** for reusable layouts
5. **Consider performance** when choosing layout types

---

## Follow-ups

- How does ConstraintLayout improve performance compared to nested LinearLayouts?
- What are the performance implications of deeply nested view hierarchies?
- How do you optimize layout inflation time for complex screens?
- When would you choose programmatic layout creation over XML?

## References

- [[c-views]] - Understanding Android view hierarchy
- Official Layout Guide: https://developer.android.com/guide/topics/ui/declaring-layout
- ConstraintLayout Guide: https://developer.android.com/training/constraint-layout

## Related Questions

### Prerequisites (Easier)
- [[c-views]] - Understanding view hierarchy fundamentals

### Related (Same Level)
- [[q-play-feature-delivery--android--medium]] - Dynamic feature delivery
- [[q-annotation-processing--android--medium]] - Annotation processing

### Advanced (Harder)
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - View redrawing mechanisms
