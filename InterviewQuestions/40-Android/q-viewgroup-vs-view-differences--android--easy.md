---
id: android-239
title: ViewGroup vs View Differences / Различия ViewGroup и View
aliases:
- ViewGroup vs View
- Различия ViewGroup и View
topic: android
subtopics:
- ui-views
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android
- c-android-views
- q-custom-view-attributes--android--medium
- q-viewmodel-pattern--android--easy
- q-what-does-viewgroup-inherit-from--android--easy
- q-what-is-a-view-and-what-is-responsible-for-its-visual-part--android--medium
- q-what-is-known-about-methods-that-redraw-view--android--medium
created: 2025-10-15
updated: 2025-11-11
tags:
- android/ui-views
- difficulty/easy
- view
- view-hierarchy
- viewgroup
anki_cards:
- slug: android-239-0-en
  language: en
  anki_id: 1769330074530
  synced_at: '2026-01-25T13:02:09.713127'
- slug: android-239-0-ru
  language: ru
  anki_id: 1769330074549
  synced_at: '2026-01-25T13:02:09.715750'
---
# Вопрос (RU)
> Различия `ViewGroup` и `View`

# Question (EN)
> `ViewGroup` vs `View` Differences

---

## Ответ (RU)

### Что Такое `ViewGroup`?

**`ViewGroup`** — это специальный `View`, который может **содержать другие `View`** (дочерние элементы). `ViewGroup` является базовым классом для layout-ов и контейнеров представлений. Этот класс также определяет `ViewGroup.LayoutParams`, который служит базовым классом для параметров размещения дочерних элементов.

`ViewGroup` — это контейнер, в который могут быть помещены другие `View`. Класс `ViewGroup` наследуется от `View` и добавляет API для управления дочерними элементами (добавление, удаление, измерение и размещение). Многие `ViewGroup` визуально минимальны, но могут выполнять отрисовку (фон, разделители, foreground, тени и т.п.).

### Иерархия `View`

```text
`View` (базовый класс)
  ↓
`ViewGroup` (контейнер)
  ↓
   LinearLayout
   RelativeLayout
   ConstraintLayout
   FrameLayout
   ... другие layouts
```

![Иерархия `View`](https://raw.githubusercontent.com/Kirchhoff-/Android-Interview-Questions/master/Android/res/view_hierarchy.png)

### Популярные `ViewGroup`

- **`LinearLayout`** — размещает дочерние элементы в один ряд или столбец
- **`RelativeLayout`** — позиционирует дочерние элементы относительно друг друга или родителя
- **`ConstraintLayout`** — гибкое позиционирование на основе ограничений
- **`FrameLayout`** — накладывает дочерние элементы друг на друга
- **MotionLayout** — layout для анимаций и переходов (расширяет `ConstraintLayout`)
- **GridLayout** — размещает дочерние элементы в таблице

### Что Такое `View`?

**`View`** — это базовый строительный блок компонентов пользовательского интерфейса. `View` занимает прямоугольную область на экране и отвечает за отрисовку содержимого и обработку событий (нажатия, жесты и т.д.).

### Популярные `View`

- **`TextView`** — отображает текст
- **`ImageView`** — отображает изображения
- **`EditText`** — редактируемое текстовое поле
- **`Button`** — кликабельная кнопка
- **SeekBar** — ползунок
- **CheckBox** — переключатель-флажок
- **RadioButton** — переключатель-вариант

### `View` Vs `ViewGroup`: Ключевые Отличия

#### `View`
- Определение: базовый элемент UI (`android.view.View`)
- Назначение: представляет прямоугольную область, может рисовать содержимое и обрабатывать пользовательские события
- Иерархия: базовый UI-класс
- Дочерние элементы: не может содержать другие `View`
- Примеры: `TextView`, `Button`, `ImageView`, `EditText`

#### `ViewGroup`
- Определение: `View`, выступающий контейнером и содержащий объекты `View` и `ViewGroup`
- Назначение: базовый класс для layout-ов; организует и позиционирует дочерние элементы
- Иерархия: наследуется от `android.view.View`
- Дочерние элементы: может содержать несколько дочерних `View` и `ViewGroup`
- Примеры: `LinearLayout`, `RelativeLayout`, `ConstraintLayout`, `FrameLayout`

### Пример Сравнения

```xml
<!-- View: не может содержать дочерние элементы -->
<TextView
    android:id="@+id/textView"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Hello World" />

<!-- ViewGroup: может содержать дочерние элементы -->
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical">

    <!-- Дочерний View 1 -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="First Item" />

    <!-- Дочерний View 2 -->
    <Button
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Click Me" />

    <!-- Вложенный ViewGroup -->
    <FrameLayout
        android:layout_width="match_parent"
        android:layout_height="100dp">

        <ImageView
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:src="@drawable/ic_image" />
    </FrameLayout>
</LinearLayout>
```

### Наследование (упрощенно)

```kotlin
// Упрощенный псевдокод (не точный код Android)
open class View {
    open fun onDraw(canvas: Canvas) {}
    open fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {}
    open fun onTouchEvent(event: MotionEvent): Boolean = false
}

// ViewGroup наследуется от View и добавляет управление дочерними элементами
abstract class ViewGroup : View() {
    // Методы для работы с дочерними элементами
    fun addView(child: View) {}
    fun removeView(child: View) {}
    fun getChildAt(index: Int): View = TODO()
    fun getChildCount(): Int = TODO()

    // Управление компоновкой
    abstract fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int)

    fun measureChildren(widthMeasureSpec: Int, heightMeasureSpec: Int) {}
}
```

### Пример Кастомного `ViewGroup` (упрощенно)

```kotlin
class CustomContainer @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : ViewGroup(context, attrs, defStyleAttr) {

    // Должен измерить себя и дочерние элементы
    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        var maxWidth = 0
        var maxHeight = 0

        // Упрощенно измеряем все дочерние элементы с теми же spec'ами
        measureChildren(widthMeasureSpec, heightMeasureSpec)

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility != GONE) {
                maxWidth = maxOf(maxWidth, child.measuredWidth)
                maxHeight = maxOf(maxHeight, child.measuredHeight)
            }
        }

        setMeasuredDimension(
            resolveSize(maxWidth, widthMeasureSpec),
            resolveSize(maxHeight, heightMeasureSpec)
        )
    }

    // Должен разместить дочерние элементы
    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility != GONE) {
                child.layout(0, 0, child.measuredWidth, child.measuredHeight)
            }
        }
    }
}
```

### Сводка (таблица)

| Аспект | `View` | `ViewGroup` |
|--------|--------|-------------|
| Назначение | Отображает содержимое и обрабатывает ввод пользователя | Контейнер для организации других `View` |
| Может иметь дочерние элементы? | Нет | Да |
| Наследование | Базовый UI-класс (`android.view.View`) | Наследуется от `View` |
| Визуальное поведение | Обычно рисует свое содержимое | Часто служит структурным контейнером; может рисовать фон/foreground и т.п. |
| Примеры | `TextView`, `Button`, `ImageView`, `EditText` | `LinearLayout`, `RelativeLayout`, `FrameLayout`, `ConstraintLayout` |
| Основная ответственность | Отрисовка и обработка событий | Измерение, размещение и управление дочерними `View` |
| Кастомные реализации | Часто переопределяют `onDraw()`, `onMeasure()` | Обязателен `onLayout()`, часто переопределяют `onMeasure()` |

### Ключевые Моменты

1. **`ViewGroup` является `View`** — наследует все возможности `View` и добавляет управление дочерними элементами.
2. **Вложенные контейнеры** — `ViewGroup` может содержать другие `ViewGroup`, образуя сложную иерархию.
3. **Отрисовка** — многие `ViewGroup` рисуют минимум, но могут отображать фон, разделители, тени и т.п.
4. **Ответственность за layout** — `ViewGroup` отвечает за измерение и позиционирование дочерних элементов.
5. **Распределение событий** — `ViewGroup` участвует в диспетчеризации событий и может перехватывать или делегировать touch-события дочерним `View`.

---

## Answer (EN)

### What is `ViewGroup`?

A **`ViewGroup`** is a special `View` that can **contain other `View` instances** (called children). The `ViewGroup` class is the base class for layouts and view containers. This class also defines `ViewGroup.LayoutParams`, which serves as the base class for layout parameters of its children.

`ViewGroup` is a container in which other `View` elements can be placed. The class `ViewGroup` extends the class `View` and adds APIs for managing children (adding, removing, measuring, and laying them out). Many `ViewGroup` instances are visually minimal, but they can draw (e.g., background, foreground, dividers, elevation shadows).

### `View` Hierarchy

```text
`View` (base class)
  ↓
`ViewGroup` (container)
  ↓
   LinearLayout
   RelativeLayout
   ConstraintLayout
   FrameLayout
   ... other layouts
```

![`View` hierarchy](https://raw.githubusercontent.com/Kirchhoff-/Android-Interview-Questions/master/Android/res/view_hierarchy.png)

### Popular `ViewGroup` Implementations

Common layout containers that extend `ViewGroup`:

- **`LinearLayout`** - arranges children in a single row or column
- **`RelativeLayout`** - positions children relative to each other or parent
- **`ConstraintLayout`** - flexible constraint-based positioning
- **`FrameLayout`** - stacks children on top of each other
- **MotionLayout** - animation and transition layout (extends `ConstraintLayout`)
- **GridLayout** - arranges children in a grid

### What is `View`?

A **`View`** represents the basic building block for user interface components. A `View` occupies a rectangular area on the screen and is responsible for drawing and handling events (such as clicks and touches).

### Popular `View` Implementations

Common UI components that extend `View`:

- **`TextView`** - displays text
- **`ImageView`** - displays images
- **`EditText`** - editable text field
- **`Button`** - clickable button
- **SeekBar** - slider control
- **CheckBox** - checkbox control
- **RadioButton** - radio button control

### `View` Vs `ViewGroup`: Key Differences

#### `View`
- **Definition**: Basic building block of User Interface (UI) elements in Android (`android.view.View`)
- **Purpose**: Represents a rectangular area that can draw content and respond to user actions
- **Hierarchy**: Base UI class
- **Children**: Cannot contain other `View` instances
- **Examples**: `TextView`, `Button`, `ImageView`, `EditText`

#### `ViewGroup`
- **Definition**: A `View` that acts as a container and holds `View` and `ViewGroup` objects
- **Purpose**: Base class for layouts; organizes and positions child views
- **Hierarchy**: Extends `android.view.View`
- **Children**: Can contain multiple `View` and `ViewGroup` children
- **Examples**: `LinearLayout`, `RelativeLayout`, `ConstraintLayout`, `FrameLayout`

### Example Comparison

```xml
<!-- View: Cannot contain children -->
<TextView
    android:id="@+id/textView"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Hello World" />

<!-- ViewGroup: Can contain children -->
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical">

    <!-- Child View 1 -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="First Item" />

    <!-- Child View 2 -->
    <Button
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Click Me" />

    <!-- Child ViewGroup (nested) -->
    <FrameLayout
        android:layout_width="match_parent"
        android:layout_height="100dp">

        <ImageView
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:src="@drawable/ic_image" />
    </FrameLayout>
</LinearLayout>
```

### Inheritance Relationship (simplified)

```kotlin
// Simplified pseudo-code (not exact Android source)
open class View {
    open fun onDraw(canvas: Canvas) {}
    open fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {}
    open fun onTouchEvent(event: MotionEvent): Boolean = false
}

// ViewGroup extends View and adds child management
abstract class ViewGroup : View() {
    // Child management methods
    fun addView(child: View) {}
    fun removeView(child: View) {}
    fun getChildAt(index: Int): View = TODO()
    fun getChildCount(): Int = TODO()

    // Layout management
    abstract fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int)

    fun measureChildren(widthMeasureSpec: Int, heightMeasureSpec: Int) {}
}
```

### Custom `ViewGroup` Example (simplified)

```kotlin
class CustomContainer @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : ViewGroup(context, attrs, defStyleAttr) {

    // Must measure itself and its children
    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        var maxWidth = 0
        var maxHeight = 0

        // Measure all children with the same specs (simplified)
        measureChildren(widthMeasureSpec, heightMeasureSpec)

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility != GONE) {
                maxWidth = maxOf(maxWidth, child.measuredWidth)
                maxHeight = maxOf(maxHeight, child.measuredHeight)
            }
        }

        setMeasuredDimension(
            resolveSize(maxWidth, widthMeasureSpec),
            resolveSize(maxHeight, heightMeasureSpec)
        )
    }

    // Must position its children
    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility != GONE) {
                child.layout(0, 0, child.measuredWidth, child.measuredHeight)
            }
        }
    }
}
```

### Summary Table

| Aspect | `View` | `ViewGroup` |
|--------|------|-----------|
| **Purpose** | Display content and handle user input | Container for organizing other views |
| **Can have children?** | No | Yes |
| **Inheritance** | Base UI class (`android.view.View`) | Extends `View` |
| **Visibility** | Typically draws its own content | Often used as a structural container; may draw background/foreground, etc. |
| **Examples** | `TextView`, `Button`, `ImageView`, `EditText` | `LinearLayout`, `RelativeLayout`, `FrameLayout`, `ConstraintLayout` |
| **Main responsibility** | Drawing and event handling | Measuring, laying out, and managing child views |
| **Required methods for custom implementations** | Commonly override `onDraw()`, `onMeasure()` | Must implement `onLayout()`; often override `onMeasure()` |

### Key Points to Remember

1. **`ViewGroup` IS a `View`** - `ViewGroup` inherits from `View`, so it has all `View` capabilities plus child management.
2. **Nested containers** - `ViewGroup` can contain other `ViewGroup` instances, creating complex layouts.
3. **Drawing** - Many `ViewGroup` implementations do minimal drawing, but they can draw backgrounds, dividers, foregrounds, and elevation.
4. **Layout responsibility** - `ViewGroup` is responsible for measuring and positioning its children.
5. **Event distribution** - `ViewGroup` participates in event dispatch and can intercept or delegate touch events to children.

---

**Source**: [Kirchhoff Android Interview Questions](https://github.com/Kirchhoff-/Android-Interview-Questions)

## Links

- [`View` - Android Developers](https://developer.android.com/reference/android/view/View)
- [`ViewGroup` - Android Developers](https://developer.android.com/reference/android/view/ViewGroup)
- [Difference between `View` and `ViewGroup` in Android - `Stack` Overflow](https://stackoverflow.com/questions/27352476/difference-between-view-and-viewgroup-in-android)
- [The life cycle of a view in Android - ProAndroidDev](https://proandroiddev.com/the-life-cycle-of-a-view-in-android-6a2c4665b95e)

---

## Follow-ups

- [[c-android]] — связь иерархии `View`/`ViewGroup` с композицией UI
- [[c-android-views]] — обзор стандартных `View` и их ролей в UI
- [[q-viewmodel-pattern--android--easy]] — разделение UI и логики состояния поверх иерархии `View`/`ViewGroup`

## References

- [`Views`](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)

## Related Questions

### Related (Easy)
- [[q-recyclerview-sethasfixedsize--android--easy]] - `View`
- [[q-viewmodel-pattern--android--easy]] - `View`

### Advanced (Harder)
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - `View`
- [[q-testing-viewmodels-turbine--android--medium]] - `View`
