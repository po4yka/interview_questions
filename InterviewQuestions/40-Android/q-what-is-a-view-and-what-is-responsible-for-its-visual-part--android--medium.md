---
id: android-145
title: What Is A View And What Is Responsible For Its Visual Part / Что такое View
  и что отвечает за её визуальную часть
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
updated: 2025-01-27
tags:
- android/ui-views
- difficulty/medium
date created: Saturday, November 1st 2025, 12:47:08 pm
date modified: Saturday, November 1st 2025, 5:43:31 pm
---

# Вопрос (RU)

> Что такое View и что отвечает за её визуальную часть?

# Question (EN)

> What is a View and what is responsible for its visual part?

## Ответ (RU)

**View** — базовый строительный блок пользовательских интерфейсов в Android. Это объект, который отрисовывается на экране и может взаимодействовать с пользователем.

### Основные Характеристики

**View** — базовый класс для виджетов (Button, TextView, ImageView). **ViewGroup** — контейнер для других View, образующий иерархию (LinearLayout, ConstraintLayout).

```kotlin
// ✅ Типичные подклассы View
class CustomButton : Button(context)
class CustomTextView : TextView(context)

// ✅ ViewGroup для компоновки
class CustomLayout : LinearLayout(context)
```

### Отрисовка И Измерения

Каждая View отвечает за свою отрисовку через `onDraw(Canvas)`, измерения через `onMeasure()`, и позиционирование через `onLayout()`.

```kotlin
class CustomView(context: Context) : View(context) {
    private val paint = Paint().apply {
        color = Color.BLUE
        style = Paint.Style.FILL
    }

    override fun onMeasure(widthSpec: Int, heightSpec: Int) {
        // ✅ Определяем размеры View
        val size = 200
        setMeasuredDimension(
            resolveSize(size, widthSpec),
            resolveSize(size, heightSpec)
        )
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // ✅ Рисуем круг
        canvas.drawCircle(
            width / 2f,
            height / 2f,
            100f,
            paint
        )
    }
}
```

### Что Управляет Визуальной Частью

**1. XML Layouts** — декларативное определение UI с атрибутами (размеры, цвета, шрифты)

**2. Стили и темы** — переиспользуемые наборы атрибутов для единообразия

```xml
<style name="PrimaryButton">
    <item name="android:textSize">16sp</item>
    <item name="backgroundTint">@color/primary</item>
</style>
```

**3. Программное изменение** — динамическое управление через методы

```kotlin
textView.apply {
    text = "Dynamic Text"
    setTextColor(Color.BLUE)
    // ✅ Анимация
    animate().alpha(0.5f).setDuration(300).start()
}
```

**4. Canvas API** — кастомная отрисовка (drawCircle, drawPath, drawText)

## Answer (EN)

**View** is the fundamental building block for user interfaces in Android. It's an object that is drawn on screen and can interact with the user.

### Core Characteristics

**View** is the base class for widgets (Button, TextView, ImageView). **ViewGroup** is a container for other Views, forming a hierarchy (LinearLayout, ConstraintLayout).

```kotlin
// ✅ Typical View subclasses
class CustomButton : Button(context)
class CustomTextView : TextView(context)

// ✅ ViewGroup for layouts
class CustomLayout : LinearLayout(context)
```

### Rendering and Measurement

Each View is responsible for its own drawing via `onDraw(Canvas)`, measurement via `onMeasure()`, and positioning via `onLayout()`.

```kotlin
class CustomView(context: Context) : View(context) {
    private val paint = Paint().apply {
        color = Color.BLUE
        style = Paint.Style.FILL
    }

    override fun onMeasure(widthSpec: Int, heightSpec: Int) {
        // ✅ Determine View dimensions
        val size = 200
        setMeasuredDimension(
            resolveSize(size, widthSpec),
            resolveSize(size, heightSpec)
        )
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // ✅ Draw a circle
        canvas.drawCircle(
            width / 2f,
            height / 2f,
            100f,
            paint
        )
    }
}
```

### What Controls the Visual Part

**1. XML Layouts** — declarative UI definition with attributes (dimensions, colors, fonts)

**2. Styles and Themes** — reusable attribute sets for consistency

```xml
<style name="PrimaryButton">
    <item name="android:textSize">16sp</item>
    <item name="backgroundTint">@color/primary</item>
</style>
```

**3. Programmatic Changes** — dynamic control via methods

```kotlin
textView.apply {
    text = "Dynamic Text"
    setTextColor(Color.BLUE)
    // ✅ Animation
    animate().alpha(0.5f).setDuration(300).start()
}
```

**4. Canvas API** — custom drawing (drawCircle, drawPath, drawText)

---

## Follow-ups

- How do `onMeasure`, `onLayout`, and `onDraw` interact during the rendering pipeline?
- When should you override `dispatchDraw` vs `onDraw`?
- How does hardware acceleration affect custom View performance and what drawing operations are unsupported?

## References

- https://developer.android.com/reference/android/view/View — View API
- https://developer.android.com/guide/topics/ui/custom-components — Custom components
- https://developer.android.com/guide/topics/ui/how-android-draws — How Android draws views

## Related Questions

### Prerequisites / Concepts

- [[c-android-components]]


### Prerequisites (Easier)

- [[q-what-to-do-in-android-project-to-start-drawing-ui-on-screen--android--medium]] - Android rendering basics

### Related (Medium)

- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - View invalidation

### Advanced (Harder)

- [[q-compose-custom-layout--android--hard]] - Modern UI with Compose
