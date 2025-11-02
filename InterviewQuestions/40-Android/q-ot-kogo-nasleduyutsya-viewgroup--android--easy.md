---
id: android-278
title: "Ot Kogo Nasleduyutsya Viewgroup / От кого наследуется ViewGroup"
aliases: [ViewGroup Inheritance, Наследование ViewGroup, View Hierarchy, Иерархия View]
topic: android
subtopics: [ui-views]
question_kind: theory
difficulty: easy
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-how-to-display-two-identical-fragments-on-the-screen-at-the-same-time--android--easy, q-canvas-optimization--graphics--medium, q-what-does-itemdecoration-do--android--medium]
created: 2025-10-15
updated: 2025-10-31
sources: []
tags: [android, android/ui-views, difficulty/easy]
date created: Tuesday, October 28th 2025, 9:50:23 pm
date modified: Thursday, October 30th 2025, 3:15:36 pm
---

# Вопрос (RU)

> От кого наследуется класс ViewGroup в Android?

# Question (EN)

> What class does ViewGroup inherit from in Android?

---

## Ответ (RU)

**ViewGroup наследуется от класса View** - базового класса для всех UI элементов в Android.

### Иерархия наследования

```
Object
  ↓
View (базовый класс для всех UI элементов)
  ↓
ViewGroup (контейнер для других View)
  ↓
Конкретные Layout классы (LinearLayout, RelativeLayout, и т.д.)
```

### Ключевые методы View

✅ **Правильно** - View предоставляет базовую функциональность:

```kotlin
abstract class View {
    // Базовые свойства
    var visibility: Int
    var isEnabled: Boolean
    var isClickable: Boolean

    // Измерение и позиционирование
    protected open fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int)
    protected open fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int)

    // Рисование
    protected open fun onDraw(canvas: Canvas)

    // События
    open fun onTouchEvent(event: MotionEvent): Boolean
}
```

### Дополнительная функциональность ViewGroup

ViewGroup расширяет View и добавляет управление дочерними элементами:

```kotlin
abstract class ViewGroup : View {
    // Управление дочерними элементами
    fun addView(child: View)
    fun removeView(child: View)
    fun getChildAt(index: Int): View
    fun getChildCount(): Int

    // Измерение дочерних элементов
    fun measureChildren(widthMeasureSpec: Int, heightMeasureSpec: Int)

    // Распределение событий касания
    override fun onInterceptTouchEvent(ev: MotionEvent): Boolean
}
```

### Пример пользовательского ViewGroup

```kotlin
class CustomLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : ViewGroup(context, attrs) {

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        var maxWidth = 0
        var maxHeight = 0

        measureChildren(widthMeasureSpec, heightMeasureSpec)

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            maxWidth = maxOf(maxWidth, child.measuredWidth)
            maxHeight = maxOf(maxHeight, child.measuredHeight)
        }

        setMeasuredDimension(
            resolveSize(maxWidth, widthMeasureSpec),
            resolveSize(maxHeight, heightMeasureSpec)
        )
    }

    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            child.layout(0, 0, child.measuredWidth, child.measuredHeight)
        }
    }
}
```

### Почему это важно

1. **Полиморфизм** - ViewGroup можно использовать везде, где ожидается View
2. **Единый API** - все UI элементы имеют общие методы
3. **Гибкость** - можно переопределять методы View в ViewGroup

✅ **Правильно** - ViewGroup как View:

```kotlin
fun setViewProperties(view: View) {
    view.visibility = View.VISIBLE
    view.alpha = 1.0f
}

val linearLayout = LinearLayout(context)
setViewProperties(linearLayout) // Работает, так как LinearLayout extends ViewGroup extends View
```

---

## Answer (EN)

**ViewGroup inherits from the View class** - the base class for all UI elements in Android.

### Inheritance Hierarchy

```
Object
  ↓
View (base class for all UI elements)
  ↓
ViewGroup (container for other Views)
  ↓
Specific Layout Classes (LinearLayout, RelativeLayout, etc.)
```

### Key View Methods

✅ **Correct** - View provides base functionality:

```kotlin
abstract class View {
    // Basic properties
    var visibility: Int
    var isEnabled: Boolean
    var isClickable: Boolean

    // Measurement and positioning
    protected open fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int)
    protected open fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int)

    // Drawing
    protected open fun onDraw(canvas: Canvas)

    // Events
    open fun onTouchEvent(event: MotionEvent): Boolean
}
```

### ViewGroup Additional Functionality

ViewGroup extends View and adds child management:

```kotlin
abstract class ViewGroup : View {
    // Child management
    fun addView(child: View)
    fun removeView(child: View)
    fun getChildAt(index: Int): View
    fun getChildCount(): Int

    // Child measurement
    fun measureChildren(widthMeasureSpec: Int, heightMeasureSpec: Int)

    // Touch event distribution
    override fun onInterceptTouchEvent(ev: MotionEvent): Boolean
}
```

### Custom ViewGroup Example

```kotlin
class CustomLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : ViewGroup(context, attrs) {

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        var maxWidth = 0
        var maxHeight = 0

        measureChildren(widthMeasureSpec, heightMeasureSpec)

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            maxWidth = maxOf(maxWidth, child.measuredWidth)
            maxHeight = maxOf(maxHeight, child.measuredHeight)
        }

        setMeasuredDimension(
            resolveSize(maxWidth, widthMeasureSpec),
            resolveSize(maxHeight, heightMeasureSpec)
        )
    }

    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            child.layout(0, 0, child.measuredWidth, child.measuredHeight)
        }
    }
}
```

### Why This Matters

1. **Polymorphism** - ViewGroup can be used anywhere View is expected
2. **Unified API** - all UI elements share common methods
3. **Flexibility** - can override View methods in ViewGroup

✅ **Correct** - ViewGroup as View:

```kotlin
fun setViewProperties(view: View) {
    view.visibility = View.VISIBLE
    view.alpha = 1.0f
}

val linearLayout = LinearLayout(context)
setViewProperties(linearLayout) // Works because LinearLayout extends ViewGroup extends View
```

---

## Follow-ups

- What are the key differences between View and ViewGroup?
- Why must ViewGroup override onLayout() as abstract?
- How does touch event handling differ between View and ViewGroup?
- What common ViewGroup subclasses are used in Android?

## References

- Android Documentation: [View](https://developer.android.com/reference/android/view/View)
- Android Documentation: [ViewGroup](https://developer.android.com/reference/android/view/ViewGroup)
- Android Developers: [Custom Views](https://developer.android.com/develop/ui/views/layout/custom-views/custom-components)

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]]
- [[q-viewmodel-pattern--android--easy]]

### Related (Same Level)
- [[q-how-to-display-two-identical-fragments-on-the-screen-at-the-same-time--android--easy]]
- [[q-what-does-itemdecoration-do--android--medium]]

### Advanced (Harder)
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]]
- [[q-canvas-optimization--graphics--medium]]
- [[q-testing-viewmodels-turbine--android--medium]]
