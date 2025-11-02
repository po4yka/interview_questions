---
id: android-225
title: "View Fundamentals / Основы View"
aliases: ["View Fundamentals", "Основы View"]
topic: android
subtopics: [ui-views, ui-widgets, lifecycle]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-what-is-the-main-application-execution-thread--android--easy, q-fragments-and-activity-relationship--android--hard, q-what-is-known-about-methods-that-redraw-view--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-28
tags: [android/ui-views, android/ui-widgets, android/lifecycle, view, view-hierarchy, difficulty/easy]
---

# Вопрос (RU)

> Что такое View в Android?

# Question (EN)

> What is a View in Android?

---

## Ответ (RU)

**View** — это базовый класс для всех компонентов пользовательского интерфейса в Android. View занимает прямоугольную область на экране и отвечает за отрисовку и обработку событий.

### Иерархия View

Все view организованы в **древовидную структуру**. Можно добавлять view:
- Программно из кода
- Декларативно через XML-макеты

**Пример иерархии:**
```
ViewGroup (LinearLayout)
├── TextView (Заголовок)
├── ViewGroup (RelativeLayout)
│   ├── ImageView (Иконка)
│   └── TextView (Описание)
└── Button (Кнопка действия)
```

### Основные операции

**1. Установка свойств**

```kotlin
val textView = findViewById<TextView>(R.id.textView)
textView.text = "Hello" // ✅ Простое изменение текста
textView.setTextColor(Color.BLACK)
textView.textSize = 18f
```

**XML (предпочтительно для статических свойств):**
```xml
<TextView
    android:id="@+id/textView"
    android:text="Hello World"
    android:textColor="#000000"
    android:textSize="18sp" />
```

**2. Установка слушателей**

```kotlin
button.setOnClickListener {
    // ✅ Обработка клика
    Toast.makeText(this, "Clicked", Toast.LENGTH_SHORT).show()
}

editText.setOnFocusChangeListener { view, hasFocus ->
    if (hasFocus) {
        // Получен фокус
    }
}
```

**3. Управление видимостью**

```kotlin
// VISIBLE - видим, занимает место
progressBar.visibility = View.VISIBLE

// INVISIBLE - невидим, но занимает место
progressBar.visibility = View.INVISIBLE

// GONE - невидим, не занимает места ✅ Для полного скрытия
progressBar.visibility = View.GONE
```

### View ID и поиск

**findViewById (старый способ):**
```kotlin
val button = findViewById<Button>(R.id.my_button) // ❌ Устаревший
```

**View Binding (современный подход):**
```kotlin
private lateinit var binding: ActivityMainBinding

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    binding = ActivityMainBinding.inflate(layoutInflater)
    setContentView(binding.root)

    binding.myButton.setOnClickListener { // ✅ Типобезопасный доступ
        // Handle click
    }
}
```

### Жизненный цикл View

```
Событие → Обработка → requestLayout()/invalidate() → Measure/Layout/Draw
```

**requestLayout()** — вызывать при изменении размера/позиции:
```kotlin
parentLayout.addView(newView)
parentLayout.requestLayout() // ✅ Принудительное измерение
```

**invalidate()** — вызывать при изменении внешнего вида:
```kotlin
textView.setTextColor(Color.RED)
// invalidate() вызывается автоматически
```

### Потоки и UI

**КРИТИЧЕСКОЕ ПРАВИЛО**: View можно изменять ТОЛЬКО из UI потока.

```kotlin
// ❌ НЕПРАВИЛЬНО - будет крэш
Thread {
    val result = performNetworkCall()
    textView.text = result // Не в UI потоке!
}.start()

// ✅ ПРАВИЛЬНО - корутины
lifecycleScope.launch {
    val result = withContext(Dispatchers.IO) {
        performNetworkCall()
    }
    textView.text = result // Автоматически в UI потоке
}
```

### Создание Custom View

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
        // ✅ Кастомная отрисовка
        canvas.drawCircle(width / 2f, height / 2f, 100f, paint)
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        // Логика измерения
        super.onMeasure(widthMeasureSpec, heightMeasureSpec)
    }
}
```

### Ключевые практики

1. **XML для статических макетов** — проще визуализировать и поддерживать
2. **View Binding** вместо findViewById — типобезопасность
3. **UI обновления в main thread** — используйте корутины/handlers
4. **ConstraintLayout** — минимизирует вложенность
5. **Очистка listeners** — предотвращает утечки памяти

### Резюме

- View — фундаментальный блок UI, занимает прямоугольную область
- Организованы в древовидную иерархию
- Система однопоточная — изменения только из UI потока
- `requestLayout()` для размера/позиции, `invalidate()` для внешнего вида
- ViewGroup — специальный View, содержащий дочерние view

---

## Answer (EN)

**View** is the base class for all user interface components in Android. A View occupies a rectangular area on the screen and is responsible for drawing and event handling.

### View Hierarchy

All views are arranged in a **tree structure**. You can add views:
- Programmatically from code
- Declaratively via XML layouts

**Hierarchy Example:**
```
ViewGroup (LinearLayout)
├── TextView (Header)
├── ViewGroup (RelativeLayout)
│   ├── ImageView (Icon)
│   └── TextView (Description)
└── Button (Action Button)
```

### Core Operations

**1. Setting Properties**

```kotlin
val textView = findViewById<TextView>(R.id.textView)
textView.text = "Hello" // ✅ Simple text update
textView.setTextColor(Color.BLACK)
textView.textSize = 18f
```

**XML (preferred for static properties):**
```xml
<TextView
    android:id="@+id/textView"
    android:text="Hello World"
    android:textColor="#000000"
    android:textSize="18sp" />
```

**2. Setting Listeners**

```kotlin
button.setOnClickListener {
    // ✅ Handle click
    Toast.makeText(this, "Clicked", Toast.LENGTH_SHORT).show()
}

editText.setOnFocusChangeListener { view, hasFocus ->
    if (hasFocus) {
        // Gained focus
    }
}
```

**3. Managing Visibility**

```kotlin
// VISIBLE - shown, occupies space
progressBar.visibility = View.VISIBLE

// INVISIBLE - hidden, occupies space
progressBar.visibility = View.INVISIBLE

// GONE - hidden, doesn't occupy space ✅ For complete hiding
progressBar.visibility = View.GONE
```

### View IDs and Lookup

**findViewById (legacy approach):**
```kotlin
val button = findViewById<Button>(R.id.my_button) // ❌ Deprecated
```

**View Binding (modern approach):**
```kotlin
private lateinit var binding: ActivityMainBinding

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    binding = ActivityMainBinding.inflate(layoutInflater)
    setContentView(binding.root)

    binding.myButton.setOnClickListener { // ✅ Type-safe access
        // Handle click
    }
}
```

### View Lifecycle

```
Event → Handle → requestLayout()/invalidate() → Measure/Layout/Draw
```

**requestLayout()** — call when size/position changes:
```kotlin
parentLayout.addView(newView)
parentLayout.requestLayout() // ✅ Force remeasurement
```

**invalidate()** — call when appearance changes:
```kotlin
textView.setTextColor(Color.RED)
// invalidate() is called automatically
```

### Threading and UI

**CRITICAL RULE**: Views can ONLY be modified from the UI thread.

```kotlin
// ❌ WRONG - will crash
Thread {
    val result = performNetworkCall()
    textView.text = result // Not on UI thread!
}.start()

// ✅ CORRECT - coroutines
lifecycleScope.launch {
    val result = withContext(Dispatchers.IO) {
        performNetworkCall()
    }
    textView.text = result // Automatically on UI thread
}
```

### Creating Custom Views

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
        // ✅ Custom drawing
        canvas.drawCircle(width / 2f, height / 2f, 100f, paint)
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        // Custom measurement logic
        super.onMeasure(widthMeasureSpec, heightMeasureSpec)
    }
}
```

### Key Practices

1. **Use XML for static layouts** — easier to visualize and maintain
2. **View Binding** over findViewById — type safety
3. **Update UI on main thread** — use coroutines/handlers
4. **ConstraintLayout** — minimizes nesting
5. **Clean up listeners** — prevents memory leaks

### Summary

- View is the fundamental UI building block occupying a rectangular area
- Organized in a tree hierarchy
- Single-threaded system — changes only from UI thread
- `requestLayout()` for size/position, `invalidate()` for appearance
- ViewGroup is a special View that contains child views

---

## Follow-ups

1. What's the difference between `invalidate()` and `requestLayout()`?
2. How does the View drawing process work (measure, layout, draw phases)?
3. What are ViewStubs and when should you use them?
4. How do you prevent memory leaks with View listeners?
5. What's the performance impact of deep view hierarchies?

## References

- [[c-android-view-system]]
- [[c-view-lifecycle]]
- [View API Reference](https://developer.android.com/reference/android/view/View)
- [Custom Views Guide](https://developer.android.com/develop/ui/views/layout/custom-views/custom-components)

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-the-main-application-execution-thread--android--easy]] - UI thread basics

### Related (Same Level)
- [[q-recyclerview-sethasfixedsize--android--easy]] - RecyclerView optimization
- [[q-viewmodel-pattern--android--easy]] - ViewModel pattern

### Advanced (Harder)
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - View redrawing deep dive
- [[q-fragments-and-activity-relationship--android--hard]] - Fragment lifecycle
