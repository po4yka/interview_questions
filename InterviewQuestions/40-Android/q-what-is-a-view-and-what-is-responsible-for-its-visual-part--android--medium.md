---
id: android-145
title: What Is A View And What Is Responsible For Its Visual Part / Что такое View и что отвечает за её визуальную часть
aliases:
- What Is A View And What Is Responsible For Its Visual Part
- Что такое View и что отвечает за её визуальную часть
topic: android
subtopics:
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
- c-android-components
- q-what-is-known-about-methods-that-redraw-view--android--medium
- q-what-to-do-in-android-project-to-start-drawing-ui-on-screen--android--medium
sources: []
created: 2025-10-15
updated: 2025-11-10
tags:
- android/ui-views
- difficulty/medium

---

# Вопрос (RU)

> Что такое `View` и что отвечает за её визуальную часть?

# Question (EN)

> What is a `View` and what is responsible for its visual part?

## Ответ (RU)

**`View`** — базовый строительный блок пользовательских интерфейсов в Android. Это объект, который участвует в цикле measure → layout → draw, отображается на экране (если попадает в видимую область) и может взаимодействовать с пользователем.

### Основные Характеристики

**`View`** — базовый класс для виджетов (Button, TextView, ImageView). **`ViewGroup`** — подкласс `View`, контейнер для других `View`, формирующий иерархию и управляющий измерением и компоновкой дочерних элементов (например, LinearLayout, ConstraintLayout).

```kotlin
// ✅ Типичные подклассы View
class CustomButton(context: Context) : Button(context)
class CustomTextView(context: Context) : TextView(context)

// ✅ ViewGroup для размещения дочерних View
class CustomLayout(context: Context) : LinearLayout(context)
```

### Отрисовка, Измерения и Компоновка

Каждая `View` участвует в трёх основных этапах:

- `onMeasure()` — определяет желаемые размеры `View` на основе MeasureSpec от родителя.
- `onLayout()` — отвечает за позиционирование дочерних `View`. Обычно переопределяется только в `ViewGroup`.
- `onDraw(Canvas)` — отвечает за собственную отрисовку содержимого `View` (не дочерних). Переопределяется в случае кастомного рендера.

Большинству обычных `View` не нужно переопределять все эти методы: виджеты и `ViewGroup` уже реализуют их корректно, а мы переопределяем только при кастомном поведении.

```kotlin
class CustomView(context: Context) : View(context) {
    private val paint = Paint().apply {
        color = Color.BLUE
        style = Paint.Style.FILL
    }

    override fun onMeasure(widthSpec: Int, heightSpec: Int) {
        // ✅ Определяем размеры View с учётом требований родителя
        val desiredSize = 200
        val width = resolveSize(desiredSize, widthSpec)
        val height = resolveSize(desiredSize, heightSpec)
        setMeasuredDimension(width, height)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // ✅ Рисуем круг внутри вычисленных границ View
        val radius = min(width, height) / 2f
        canvas.drawCircle(width / 2f, height / 2f, radius, paint)
    }
}
```

### Что Управляет Визуальной Частью `View`

На визуальное представление `View` влияют несколько уровней:

1. Свойства самой `View`:
   - `background`, `foreground`
   - `padding`, `alpha`, `rotation`, `translationX/Y`, `scaleX/Y`, `elevation`
   - текст/картинка/контент конкретного виджета
   Эти свойства задаются в XML или программно и напрямую участвуют в отрисовке.

2. `LayoutParams` от родительского `ViewGroup`:
   - Определяют размеры и правила расположения `View` (например, `match_parent`, `wrap_content`, констрейнты и т.п.), что влияет на область, в которой она рисуется.

3. XML Layouts — декларативное описание `View` и их атрибутов:
   - размеры, отступы, цвета, шрифты, background и другие визуальные параметры.

4. Стили и темы — переиспользуемые наборы атрибутов, применяемые к `View`:

```xml
<style name="PrimaryButton">
    <item name="android:textSize">16sp</item>
    <item name="android:backgroundTint">@color/primary</item>
</style>
```

5. Программные изменения — динамическое управление внешним видом и состоянием:

```kotlin
textView.apply {
    text = "Dynamic Text"
    setTextColor(Color.BLUE)
    // ✅ Анимация, влияющая на визуальное представление
    animate().alpha(0.5f).setDuration(300).start()
}
```

6. Canvas API — используется внутри `onDraw()` для кастомной отрисовки (например, `drawCircle`, `drawPath`, `drawText`).

В конечном итоге визуальная часть `View` формируется комбинацией:
- параметров компоновки от родителя (где и какого размера `View`),
- собственных атрибутов и состояния `View`,
- логики в `onDraw()` и отрисовки background/foreground,
- применённых стилей, тем и программных изменений.

## Answer (EN)

A **`View`** is the fundamental building block for user interfaces in Android. It is an object that participates in the measure → layout → draw pipeline, can be displayed on screen (if within the visible area), and can interact with the user.

### Core Characteristics

**`View`** is the base class for widgets (Button, TextView, ImageView). **`ViewGroup`** is a subclass of `View` that acts as a container for other Views, forming a hierarchy and controlling how its children are measured and laid out (e.g., LinearLayout, ConstraintLayout).

```kotlin
// ✅ Typical View subclasses
class CustomButton(context: Context) : Button(context)
class CustomTextView(context: Context) : TextView(context)

// ✅ ViewGroup used to host and lay out child Views
class CustomLayout(context: Context) : LinearLayout(context)
```

### Rendering, Measurement, and Layout

Each `View` participates in three main stages:

- `onMeasure()` — determines the `View`'s desired size based on the MeasureSpecs from its parent.
- `onLayout()` — positions child Views. Typically overridden only in `ViewGroup` implementations.
- `onDraw(Canvas)` — draws the `View`'s own content (not its children). Overridden when custom rendering is needed.

Most standard Views do not need to override all of these methods: existing widgets and ViewGroups already provide correct implementations; you override only when you need custom behavior.

```kotlin
class CustomView(context: Context) : View(context) {
    private val paint = Paint().apply {
        color = Color.BLUE
        style = Paint.Style.FILL
    }

    override fun onMeasure(widthSpec: Int, heightSpec: Int) {
        // ✅ Determine dimensions respecting parent constraints
        val desiredSize = 200
        val width = resolveSize(desiredSize, widthSpec)
        val height = resolveSize(desiredSize, heightSpec)
        setMeasuredDimension(width, height)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // ✅ Draw a circle within the measured bounds
        val radius = min(width, height) / 2f
        canvas.drawCircle(width / 2f, height / 2f, radius, paint)
    }
}
```

### What Controls the Visual Part of a `View`

Several layers affect a `View`'s visual appearance:

1. `View`'s own properties:
   - `background`, `foreground`
   - `padding`, `alpha`, `rotation`, `translationX/Y`, `scaleX/Y`, `elevation`
   - the widget-specific content (text, image, etc.)
   These are set in XML or programmatically and directly influence drawing.

2. `LayoutParams` provided by the parent `ViewGroup`:
   - Define how big the `View` is and how it is positioned (e.g., `match_parent`, `wrap_content`, constraints), which determines the area it can draw into.

3. XML Layouts — declarative UI definition specifying Views and their attributes:
   - dimensions, margins, colors, fonts, backgrounds, and other visual attributes.

4. Styles and Themes — reusable sets of attributes applied to Views:

```xml
<style name="PrimaryButton">
    <item name="android:textSize">16sp</item>
    <item name="android:backgroundTint">@color/primary</item>
</style>
```

5. Programmatic Changes — dynamic control via code:

```kotlin
textView.apply {
    text = "Dynamic Text"
    setTextColor(Color.BLUE)
    // ✅ Animation affecting visual appearance
    animate().alpha(0.5f).setDuration(300).start()
}
```

6. Canvas API — used inside `onDraw()` for custom drawing (e.g., `drawCircle`, `drawPath`, `drawText`).

Ultimately, the `View`'s visual part is defined by the combination of:
- layout parameters from its parent (where it is placed and how big it is),
- the `View`'s own attributes and state,
- the implementation of `onDraw()` plus background/foreground drawing,
- applied styles, themes, and runtime changes.

---

## Follow-ups

- How do `onMeasure`, `onLayout`, and `onDraw` interact during the rendering pipeline?
- When should you override `dispatchDraw` vs `onDraw`?
- How does hardware acceleration affect custom `View` performance and what drawing operations are unsupported?

## References

- https://developer.android.com/reference/android/view/View — `View` API
- https://developer.android.com/guide/topics/ui/custom-components — Custom components
- https://developer.android.com/guide/topics/ui/how-android-draws — How Android draws views

## Related Questions

### Prerequisites / Concepts

- [[c-android-components]]

### Prerequisites (Easier)

- [[q-what-to-do-in-android-project-to-start-drawing-ui-on-screen--android--medium]] - Android rendering basics

### Related (Medium)

- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - `View` invalidation

### Advanced (Harder)

- [[q-compose-custom-layout--android--hard]] - Modern UI with Compose
