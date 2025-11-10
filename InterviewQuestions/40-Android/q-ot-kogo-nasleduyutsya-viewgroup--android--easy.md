---
id: android-278
title: Ot Kogo Nasleduyutsya Viewgroup / От кого наследуется ViewGroup
aliases:
- View Hierarchy
- ViewGroup Inheritance
- Иерархия View
- Наследование ViewGroup
topic: android
subtopics:
- ui-views
question_kind: theory
difficulty: easy
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android-components
- q-canvas-optimization--android--medium
- q-how-to-display-two-identical-fragments-on-the-screen-at-the-same-time--android--easy
- q-what-does-itemdecoration-do--android--medium
created: 2025-10-15
updated: 2025-11-10
sources: []
tags:
- android
- android/ui-views
- difficulty/easy

---

# Вопрос (RU)

> От кого наследуется класс `ViewGroup` в Android?

# Question (EN)

> What class does `ViewGroup` inherit from in Android?

---

## Ответ (RU)

**`ViewGroup` наследуется от класса `View`** — базового класса для всех UI элементов в Android.

### Иерархия Наследования

```
Object
  ↓
View (базовый класс для всех UI элементов)
  ↓
ViewGroup (контейнер для других View)
  ↓
Конкретные Layout классы (LinearLayout, RelativeLayout, и т.д.)
```

### Ключевые Методы `View`

**Правильно** — ниже упрощённый псевдокод, иллюстрирующий базовую функциональность `View` (не точные сигнатуры исходного API):

```kotlin
open class View {
    // Базовые свойства (в реальности доступны через геттеры/сеттеры)
    var visibility: Int
    var isEnabled: Boolean
    var isClickable: Boolean

    // Измерение и позиционирование
    protected open fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {}
    protected open fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {}

    // Рисование
    protected open fun onDraw(canvas: Canvas) {}

    // События
    open fun onTouchEvent(event: MotionEvent): Boolean = false
}
```

### Дополнительная Функциональность `ViewGroup`

`ViewGroup` расширяет `View` и добавляет управление дочерними элементами (также показано в виде упрощённого псевдокода):

```kotlin
abstract class ViewGroup(context: Context, attrs: AttributeSet? = null) : View(/* ... */) {
    // Управление дочерними элементами
    fun addView(child: View) {}
    fun removeView(child: View) {}
    fun getChildAt(index: Int): View = TODO()
    fun getChildCount(): Int = TODO()

    // Измерение дочерних элементов
    fun measureChildren(widthMeasureSpec: Int, heightMeasureSpec: Int) {}

    // Перехват и распределение событий касания
    open fun onInterceptTouchEvent(ev: MotionEvent): Boolean = false
}
```

### Пример Пользовательского `ViewGroup`

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

### Почему Это Важно

1. Полиморфизм — `ViewGroup` можно использовать везде, где ожидается `View`.
2. Единый API — все UI элементы имеют общие методы.
3. Гибкость — можно переопределять методы `View` в `ViewGroup`.

**Правильно** — `ViewGroup` как `View`:

```kotlin
fun setViewProperties(view: View) {
    view.visibility = View.VISIBLE
    view.alpha = 1.0f
}

val linearLayout = LinearLayout(context)
setViewProperties(linearLayout) // Работает, так как LinearLayout : ViewGroup : View
```

---

## Answer (EN)

**`ViewGroup` inherits from the `View` class** — the base class for all UI elements in Android.

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

### Key `View` Methods

**Correct** — below is simplified pseudo-code illustrating `View`'s base functionality (not the exact framework signatures):

```kotlin
open class View {
    // Basic properties (actually exposed via getters/setters)
    var visibility: Int
    var isEnabled: Boolean
    var isClickable: Boolean

    // Measurement and positioning
    protected open fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {}
    protected open fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {}

    // Drawing
    protected open fun onDraw(canvas: Canvas) {}

    // Events
    open fun onTouchEvent(event: MotionEvent): Boolean = false
}
```

### `ViewGroup` Additional Functionality

`ViewGroup` extends `View` and adds child management (also shown as simplified pseudo-code):

```kotlin
abstract class ViewGroup(context: Context, attrs: AttributeSet? = null) : View(/* ... */) {
    // Child management
    fun addView(child: View) {}
    fun removeView(child: View) {}
    fun getChildAt(index: Int): View = TODO()
    fun getChildCount(): Int = TODO()

    // Child measurement
    fun measureChildren(widthMeasureSpec: Int, heightMeasureSpec: Int) {}

    // Touch event interception and distribution
    open fun onInterceptTouchEvent(ev: MotionEvent): Boolean = false
}
```

### Custom `ViewGroup` Example

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

1. Polymorphism — `ViewGroup` can be used anywhere `View` is expected.
2. Unified API — all UI elements share common methods.
3. Flexibility — `ViewGroup` can override and extend `View` behavior.

**Correct** — `ViewGroup` as `View`:

```kotlin
fun setViewProperties(view: View) {
    view.visibility = View.VISIBLE
    view.alpha = 1.0f
}

val linearLayout = LinearLayout(context)
setViewProperties(linearLayout) // Works because LinearLayout : ViewGroup : View
```

---

## Дополнительные вопросы (RU)

- В чем ключевые отличия между `View` и `ViewGroup`?
- Почему метод `onLayout()` объявлен абстрактным в `ViewGroup` и что должны реализовать наследники?
- Чем отличается обработка касаний в `View` и `ViewGroup`?
- Какие распространенные наследники `ViewGroup` используются в Android?

## Follow-ups

- What are the key differences between `View` and `ViewGroup`?
- Why is onLayout() declared abstract in `ViewGroup`, and what must subclasses implement there?
- How does touch event handling differ between `View` and `ViewGroup`?
- What common `ViewGroup` subclasses are used in Android?

## Ссылки (RU)

- Документация Android: `View` (https://developer.android.com/reference/android/view/View)
- Документация Android: `ViewGroup` (https://developer.android.com/reference/android/view/ViewGroup)
- Android Developers: Пользовательские представления (Custom Views): https://developer.android.com/develop/ui/views/layout/custom-views/custom-components

## References

- Android Documentation: `View` (https://developer.android.com/reference/android/view/View)
- Android Documentation: `ViewGroup` (https://developer.android.com/reference/android/view/ViewGroup)
- Android Developers: Custom Views (https://developer.android.com/develop/ui/views/layout/custom-views/custom-components)

## Related Questions

### Prerequisites / Concepts

- [[c-android-components]]

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]]
- [[q-viewmodel-pattern--android--easy]]

### Related (Same Level)
- [[q-how-to-display-two-identical-fragments-on-the-screen-at-the-same-time--android--easy]]
- [[q-what-does-itemdecoration-do--android--medium]]

### Advanced (Harder)
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]]
- [[q-canvas-optimization--android--medium]]
- [[q-testing-viewmodels-turbine--android--medium]]