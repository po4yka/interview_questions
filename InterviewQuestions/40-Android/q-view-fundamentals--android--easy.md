---
id: "20251015082237386"
title: "View Fundamentals / Основы View"
topic: android
difficulty: easy
status: draft
created: 2025-10-15
tags: [view, ui, basics, widget, view-hierarchy, difficulty/easy]
---
# What is a View in Android? / Что такое View в Android?

**English**: What's View?

## Answer (EN)
`View` represents the **basic building block for user interface components** in Android. A View occupies a rectangular area on the screen and is responsible for drawing and event handling.

**View is the base class for widgets**, which are used to create interactive UI components such as:
- Buttons
- Text fields
- Checkboxes
- Images
- And many more

## View Hierarchy

All views in a window are arranged in a **single tree structure**. You can add views either:
- From code programmatically
- By specifying a tree of views in one or more XML layout files

There are many specialized subclasses of views that act as:
- **Controls**: Interactive UI elements (Button, EditText, etc.)
- **Display elements**: Show text, images, or other content (TextView, ImageView, etc.)

**View Hierarchy Example:**

```
ViewGroup (Root Layout - LinearLayout)
 TextView (Header)
 ViewGroup (Nested Layout - RelativeLayout)
    ImageView (Icon)
    TextView (Description)
 Button (Action Button)
```

## Using Views

Once you have created a tree of views, there are typically a few types of common operations:

### 1. Set Properties

Set properties like text, color, size, etc. The available properties and methods vary among different subclasses of views.

**XML Example:**
```xml
<TextView
    android:id="@+id/textView"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Hello World"
    android:textColor="#000000"
    android:textSize="18sp" />
```

**Programmatic Example:**
```kotlin
val textView = findViewById<TextView>(R.id.textView)
textView.text = "Hello World"
textView.setTextColor(Color.BLACK)
textView.textSize = 18f
```

**Note**: Properties known at build time should be set in XML layout files for better performance and maintainability.

### 2. Set Focus

The framework handles moving focus in response to user input. To force focus to a specific view:

```kotlin
val editText = findViewById<EditText>(R.id.editText)
editText.requestFocus()
```

### 3. Set Up Listeners

Views allow clients to set listeners that will be notified when something interesting happens to the view.

**Common Listeners:**

**Click Listener:**
```kotlin
val button = findViewById<Button>(R.id.button)
button.setOnClickListener {
    // Handle click
    Toast.makeText(this, "Button clicked", Toast.LENGTH_SHORT).show()
}
```

**Focus Change Listener:**
```kotlin
editText.setOnFocusChangeListener { view, hasFocus ->
    if (hasFocus) {
        // View gained focus
    } else {
        // View lost focus
    }
}
```

**Text Change Listener:**
```kotlin
editText.addTextChangedListener(object : TextWatcher {
    override fun afterTextChanged(s: Editable?) {
        // After text changed
    }

    override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {
        // Before text changed
    }

    override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
        // On text changed
    }
})
```

### 4. Set Visibility

You can hide or show views using `setVisibility(int)`:

```kotlin
val progressBar = findViewById<ProgressBar>(R.id.progressBar)

// Show view
progressBar.visibility = View.VISIBLE

// Hide view but preserve layout space
progressBar.visibility = View.INVISIBLE

// Hide view and remove from layout
progressBar.visibility = View.GONE
```

**Visibility States:**
- `VISIBLE` - View is visible
- `INVISIBLE` - View is hidden but still takes up space
- `GONE` - View is hidden and doesn't take up space

**Important Note**: The Android framework is responsible for measuring, laying out, and drawing views. You should **not** call methods that perform these actions on views yourself unless you are implementing a `ViewGroup`.

## View IDs

Views may have an integer ID associated with them. These IDs are typically assigned in the layout XML files and are used to find specific views within the view tree.

### Defining IDs in XML

**Common pattern:**

**1. Define a view with unique ID in layout file:**
```xml
<Button
    android:id="@+id/my_button"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="@string/my_button_text" />
```

**2. Find the view from Activity:**
```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val myButton = findViewById<Button>(R.id.my_button)
        myButton.setOnClickListener {
            // Handle click
        }
    }
}
```

**Using View Binding (Modern Approach):**
```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.myButton.setOnClickListener {
            // Handle click
        }
    }
}
```

**Note**: View IDs need **not be unique** throughout the tree, but it is **good practice** to ensure they are at least unique within the part of the tree you are searching.

## Event Handling and Threading

### The View Lifecycle

The basic cycle of a view is:

1. **Event comes in** and is dispatched to the appropriate view
2. **View handles event** and notifies any listeners
3. **If view's bounds need to change**, view calls `requestLayout()`
4. **If view's appearance needs to change**, view calls `invalidate()`
5. **Framework measures, lays out, and draws** the tree as appropriate

**Important Threading Rule:**

> The entire view tree is **single threaded**. You must always be on the **UI thread** when calling any method on any view.

**Updating UI from Background Thread:**

```kotlin
// WRONG - Will crash
Thread {
    // Background work
    val result = performNetworkCall()

    // DON'T DO THIS - Not on UI thread
    textView.text = result
}.start()

// CORRECT - Using Handler
Thread {
    val result = performNetworkCall()

    // Post to UI thread
    runOnUiThread {
        textView.text = result
    }
}.start()

// CORRECT - Using Coroutines (Modern approach)
lifecycleScope.launch {
    val result = withContext(Dispatchers.IO) {
        performNetworkCall()
    }
    // Automatically back on UI thread
    textView.text = result
}
```

### View Update Methods

**requestLayout():**
- Call when the view's size or position needs to change
- Triggers measure and layout pass
- Example: Adding/removing child views

```kotlin
// When adding a child dynamically
parentLayout.addView(newView)
parentLayout.requestLayout()
```

**invalidate():**
- Call when the view's appearance needs to change
- Triggers only the draw pass (faster than requestLayout)
- Example: Changing color, text, or visual properties

```kotlin
// When changing visual appearance
textView.setTextColor(Color.RED)
textView.invalidate()  // Framework usually calls this automatically
```

## Common View Subclasses

**Basic Widgets:**
- `TextView` - Display text
- `EditText` - Text input
- `Button` - Clickable button
- `ImageView` - Display images
- `ImageButton` - Image-based button

**Layouts (ViewGroup subclasses):**
- `LinearLayout` - Linear arrangement (horizontal/vertical)
- `RelativeLayout` - Position relative to parent or siblings
- `ConstraintLayout` - Constraint-based positioning
- `FrameLayout` - Single child or stacked children
- `RecyclerView` - Efficient scrolling lists

**Advanced Views:**
- `WebView` - Display web content
- `VideoView` - Video playback
- `SurfaceView` - High-performance rendering
- `TextureView` - Hardware-accelerated rendering

## Creating Custom Views

You can create custom views by extending `View` or any of its subclasses:

```kotlin
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private val paint = Paint().apply {
        color = Color.BLUE
        strokeWidth = 5f
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // Custom drawing
        canvas.drawCircle(
            width / 2f,
            height / 2f,
            100f,
            paint
        )
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        // Custom measurement logic
        super.onMeasure(widthMeasureSpec, heightMeasureSpec)
    }
}
```

**Use in XML:**
```xml
<com.example.app.CustomView
    android:layout_width="200dp"
    android:layout_height="200dp" />
```

## Best Practices

1. **Use XML for layouts** when possible - easier to maintain and visualize
2. **Set proper IDs** for views you need to reference
3. **Use View Binding or ViewBinding** instead of `findViewById`
4. **Always update UI on main thread** - use handlers, `runOnUiThread`, or coroutines
5. **Reuse views** in lists using RecyclerView with ViewHolder pattern
6. **Minimize view hierarchy depth** for better performance
7. **Use ConstraintLayout** for complex layouts to reduce nesting
8. **Handle configuration changes** properly (screen rotation)
9. **Clean up listeners** to prevent memory leaks

## Summary

- **View** is the fundamental building block for UI in Android
- All views are arranged in a **tree hierarchy**
- Views can be defined in **XML** or created **programmatically**
- Each view has an **ID** for identification and retrieval
- The view system is **single-threaded** - always update UI on main thread
- **requestLayout()** for size/position changes, **invalidate()** for visual changes
- Use **listeners** to respond to user interactions
- **ViewGroup** is a special view that can contain other views

**Sources**:
- [View](https://developer.android.com/reference/android/view/View)
- [The life cycle of a view in Android](https://proandroiddev.com/the-life-cycle-of-a-view-in-android-6a2c4665b95e)

## Ответ (RU)
`View` представляет собой **основной строительный блок для компонентов пользовательского интерфейса** в Android. View занимает прямоугольную область на экране и отвечает за отрисовку и обработку событий.

**View является базовым классом для виджетов**, которые используются для создания интерактивных UI компонентов, таких как:
- Кнопки
- Текстовые поля
- Чекбоксы
- Изображения
- И многие другие

## Иерархия View

Все view в окне организованы в **единую древовидную структуру**. Вы можете добавлять view либо:
- Программно из кода
- Указывая дерево view в одном или нескольких XML файлах макета

Существует множество специализированных подклассов view, которые действуют как:
- **Элементы управления**: Интерактивные UI элементы (Button, EditText и т.д.)
- **Элементы отображения**: Показывают текст, изображения или другой контент (TextView, ImageView и т.д.)

## Использование Views

После создания дерева view обычно выполняются несколько типов общих операций:

### 1. Установка свойств

Установка свойств, таких как текст, цвет, размер и т.д. Доступные свойства и методы различаются для разных подклассов view.

**Примечание**: Свойства, известные во время сборки, должны быть установлены в XML файлах макета для лучшей производительности и поддерживаемости.

### 2. Установка фокуса

Фреймворк обрабатывает перемещение фокуса в ответ на ввод пользователя. Чтобы принудительно установить фокус на конкретный view, вызовите `requestFocus()`.

### 3. Установка слушателей (Listeners)

View позволяют клиентам устанавливать слушателей, которые будут уведомлены, когда что-то интересное происходит с view.

### 4. Установка видимости

Вы можете скрывать или показывать view, используя `setVisibility(int)`.

**Состояния видимости:**
- `VISIBLE` - View видим
- `INVISIBLE` - View скрыт, но всё ещё занимает место
- `GONE` - View скрыт и не занимает места

**Важное примечание**: Фреймворк Android отвечает за измерение, размещение и отрисовку view. Вы **не должны** вызывать методы, выполняющие эти действия на view самостоятельно, если только вы не реализуете `ViewGroup`.

## View ID

View могут иметь связанный с ними целочисленный ID. Эти ID обычно назначаются в XML файлах макета и используются для поиска конкретных view в дереве view.

**Общий паттерн:**

1. Определить view с уникальным ID в файле макета
2. Найти view из Activity с помощью `findViewById`

**Примечание**: View ID **не обязательно должны быть уникальными** во всём дереве, но это **хорошая практика** — обеспечить их уникальность хотя бы в той части дерева, в которой вы ищете.

## Обработка событий и потоки

### Жизненный цикл View

Базовый цикл view:

1. **Событие поступает** и отправляется соответствующему view
2. **View обрабатывает событие** и уведомляет слушателей
3. **Если границы view должны измениться**, view вызывает `requestLayout()`
4. **Если внешний вид view должен измениться**, view вызывает `invalidate()`
5. **Фреймворк измеряет, размещает и отрисовывает** дерево по мере необходимости

**Важное правило потоков:**

> Всё дерево view **однопоточное**. Вы всегда должны находиться в **UI потоке** при вызове любого метода на любом view.

**Обновление UI из фонового потока:**

Если вы выполняете работу в других потоках и хотите обновить состояние view из этого потока, используйте `Handler`, `runOnUiThread` или корутины.

### Методы обновления View

**requestLayout():**
- Вызывайте, когда размер или позиция view должны измениться
- Запускает проход измерения и размещения
- Пример: Добавление/удаление дочерних view

**invalidate():**
- Вызывайте, когда внешний вид view должен измениться
- Запускает только проход отрисовки (быстрее, чем requestLayout)
- Пример: Изменение цвета, текста или визуальных свойств

## Общие подклассы View

**Базовые виджеты:**
- `TextView` - Отображение текста
- `EditText` - Ввод текста
- `Button` - Кликабельная кнопка
- `ImageView` - Отображение изображений
- `ImageButton` - Кнопка на основе изображения

**Макеты (подклассы ViewGroup):**
- `LinearLayout` - Линейное расположение (горизонтальное/вертикальное)
- `RelativeLayout` - Позиционирование относительно родителя или соседей
- `ConstraintLayout` - Позиционирование на основе ограничений
- `FrameLayout` - Один дочерний элемент или наложенные дочерние элементы
- `RecyclerView` - Эффективные прокручиваемые списки

**Продвинутые Views:**
- `WebView` - Отображение веб-контента
- `VideoView` - Воспроизведение видео
- `SurfaceView` - Высокопроизводительная отрисовка
- `TextureView` - Аппаратно-ускоренная отрисовка

## Лучшие практики

1. **Используйте XML для макетов**, когда возможно - легче поддерживать и визуализировать
2. **Устанавливайте правильные ID** для view, на которые нужно ссылаться
3. **Используйте View Binding или ViewBinding** вместо `findViewById`
4. **Всегда обновляйте UI в главном потоке** - используйте handlers, `runOnUiThread` или корутины
5. **Повторно используйте view** в списках, используя RecyclerView с паттерном ViewHolder
6. **Минимизируйте глубину иерархии view** для лучшей производительности
7. **Используйте ConstraintLayout** для сложных макетов для уменьшения вложенности
8. **Правильно обрабатывайте изменения конфигурации** (поворот экрана)
9. **Очищайте слушателей** для предотвращения утечек памяти

## Резюме

- **View** - это фундаментальный строительный блок для UI в Android
- Все view организованы в **древовидную иерархию**
- View могут быть определены в **XML** или созданы **программно**
- Каждый view имеет **ID** для идентификации и получения
- Система view **однопоточная** - всегда обновляйте UI в главном потоке
- **requestLayout()** для изменений размера/позиции, **invalidate()** для визуальных изменений
- Используйте **слушателей** для ответа на взаимодействия пользователя
- **ViewGroup** - это специальный view, который может содержать другие view

---

## Related Questions

### Related (Easy)
- [[q-recyclerview-sethasfixedsize--android--easy]] - View
- [[q-viewmodel-pattern--android--easy]] - View

### Advanced (Harder)
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - View
- [[q-testing-viewmodels-turbine--testing--medium]] - View
- [[q-rxjava-pagination-recyclerview--android--medium]] - View
