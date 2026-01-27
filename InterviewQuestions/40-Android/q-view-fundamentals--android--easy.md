---
id: android-225
title: View Fundamentals / Основы View
aliases:
- View Fundamentals
- Основы View
topic: android
subtopics:
- ui-views
- ui-widgets
question_kind: android
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android-views
- q-fragments-and-activity-relationship--android--hard
- q-what-is-known-about-methods-that-redraw-view--android--medium
- q-what-is-the-main-application-execution-thread--android--easy
sources:
- https://developer.android.com/develop/ui/views/layout/custom-views/custom-components
- https://developer.android.com/reference/android/view/View
created: 2024-10-15
updated: 2025-11-10
tags:
- android/ui-views
- android/ui-widgets
- difficulty/easy
- view
- view-hierarchy
anki_cards:
- slug: android-225-0-ru
  language: ru
  anki_id: 1768420767664
  synced_at: '2026-01-14 23:59:27.669344'
- slug: android-225-0-en
  language: en
  anki_id: 1768420767641
  synced_at: '2026-01-14 23:59:27.645212'
---
# Вопрос (RU)

> Что такое `View` в Android?

# Question (EN)

> What is a `View` in Android?

---

## Ответ (RU)

**`View`** — это базовый класс для всех компонентов пользовательского интерфейса в Android. `View` занимает прямоугольную область на экране и отвечает за отрисовку и обработку событий.

См. также: [[c-android-views]]

### Иерархия `View`

Все view организованы в **древовидную структуру**. Можно добавлять view:
- Программно из кода
- Декларативно через XML-макеты

**Пример иерархии:**
```text
ViewGroup (LinearLayout)
├── TextView (Заголовок)
├── ViewGroup (RelativeLayout)
│   ├── ImageView (Иконка)
│   └── TextView (Описание)
└── Button (Кнопка действия)
```

### Основные Операции

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

### `View` ID И Поиск

**findViewById (базовый, менее удобный подход):**
```kotlin
val button = findViewById<Button>(R.id.my_button) // ⚠️ Работает, но менее безопасно и более многословно
```

**`View` Binding (современный, рекомендуемый подход):**
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

### Жизненный Цикл `View`

```text
Событие → Обработка → requestLayout()/invalidate() → Measure/Layout/Draw
```

**requestLayout()** — вызывать при изменении, влияющем на размер/позицию `View`.
```kotlin
parentLayout.addView(newView)
parentLayout.requestLayout() // ✅ Можно запросить переизмерение/переразметку при необходимости
```
(Добавление view обычно само инициирует проход layout; явный вызов нужен в особых случаях.)

**invalidate()** — вызывать при изменении внешнего вида (но не размеров):
```kotlin
textView.setTextColor(Color.RED)
// Во многих стандартных методах invalidate() вызывается автоматически
```

### Потоки И UI

**КРИТИЧЕСКОЕ ПРАВИЛО**: Доступ к `View` и обновление UI допускается ТОЛЬКО из главного (UI) потока.

```kotlin
// ❌ НЕПРАВИЛЬНО - может привести к исключению
Thread {
    val result = performNetworkCall()
    textView.text = result // Не в UI потоке!
}.start()

// ✅ ПРАВИЛЬНО - корутины
lifecycleScope.launch {
    val result = withContext(Dispatchers.IO) {
        performNetworkCall()
    }
    textView.text = result // Выполняется в главном потоке
}
```

### Создание Custom `View`

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
        // Для собственного измерения переопределите логику здесь;
        // если вас устраивает стандартное поведение, вызывайте super.onMeasure(...)
        super.onMeasure(widthMeasureSpec, heightMeasureSpec)
    }
}
```

### Ключевые Практики

1. **XML для статических макетов** — проще визуализировать и поддерживать
2. **`View` Binding** вместо прямого `findViewById` — типобезопасность и меньше шаблонного кода
3. **UI обновления в main thread** — используйте корутины/Handlers/RunOnUiThread
4. **`ConstraintLayout`** — помогает минимизировать глубину вложенности
5. **Очистка listeners** — предотвращает утечки памяти (особенно при привязке к жизненному циклу `Activity`/`Fragment`)

### Резюме

- `View` — фундаментальный блок UI, занимает прямоугольную область
- Организованы в древовидную иерархию
- UI-инструментарий не потокобезопасен — изменения `View` только из главного/UI-потока
- `requestLayout()` для изменений, влияющих на размер/позицию; `invalidate()` для изменений внешнего вида
- `ViewGroup` — специальный `View`, содержащий дочерние view

---

## Answer (EN)

**`View`** is the base class for all user interface components in Android. A `View` occupies a rectangular area on the screen and is responsible for drawing and event handling.

See also: [[c-android-views]]

### `View` Hierarchy

All views are arranged in a **tree structure**. You can add views:
- Programmatically from code
- Declaratively via XML layouts

**Hierarchy Example:**
```text
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

### `View` IDs and Lookup

**findViewById (basic, less convenient approach):**
```kotlin
val button = findViewById<Button>(R.id.my_button) // ⚠️ Works, but more verbose and less type-safe
```

**`View` Binding (modern, recommended approach):**
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

### `View` Lifecycle

```text
Event → Handle → requestLayout()/invalidate() → Measure/Layout/Draw
```

**requestLayout()** — call when a change affects view size/position.
```kotlin
parentLayout.addView(newView)
parentLayout.requestLayout() // ✅ Can be used to request re-measure/re-layout if needed
```
(Adding a view typically triggers a layout pass automatically; explicit calls are for special cases.)

**invalidate()** — call when appearance changes (but not size):
```kotlin
textView.setTextColor(Color.RED)
// Many standard setters call invalidate() internally
```

### Threading and UI

**CRITICAL RULE**: Accessing `Views` and updating UI must be done ONLY from the main (UI) thread.

```kotlin
// ❌ WRONG - may cause an exception
Thread {
    val result = performNetworkCall()
    textView.text = result // Not on UI thread!
}.start()

// ✅ CORRECT - coroutines
lifecycleScope.launch {
    val result = withContext(Dispatchers.IO) {
        performNetworkCall()
    }
    textView.text = result // Executed on the main thread
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
        // Put custom measuring logic here if needed;
        // if default behavior is fine, delegate to super.
        super.onMeasure(widthMeasureSpec, heightMeasureSpec)
    }
}
```

### Key Practices

1. **Use XML for static layouts** — easier to visualize and maintain
2. **Prefer `View` Binding over raw findViewById** — type safety and less boilerplate
3. **Update UI on main thread** — use coroutines/Handlers/runOnUiThread
4. **Use `ConstraintLayout`** — helps reduce hierarchy depth
5. **Clean up listeners** — prevents memory leaks (especially with `Activity`/`Fragment` references)

### Summary

- `View` is the fundamental UI building block occupying a rectangular area
- `Views` are organized in a tree hierarchy
- UI toolkit is not thread-safe — update `Views` only from the main/UI thread
- `requestLayout()` for changes affecting size/position; `invalidate()` for appearance changes
- `ViewGroup` is a special `View` that contains child views

---

## Дополнительные Вопросы (RU)

1. В чем разница между `invalidate()` и `requestLayout()`?
2. Как работает процесс отрисовки `View` (фазы measure, layout, draw)?
3. Что такое `ViewStub` и `ViewStubCompat`, и когда их стоит использовать?
4. Как предотвращать утечки памяти при работе со слушателями `View`?
5. Какова проблема глубоких иерархий `View` и как оптимизировать их для производительности?

## Follow-ups

1. What's the difference between `invalidate()` and `requestLayout()`?
2. How does the `View` drawing process work (measure, layout, draw phases)?
3. What are `ViewStub`, `ViewStubCompat` and when should you use them?
4. How do you prevent memory leaks with `View` listeners?
5. What's the performance impact of deep view hierarchies and how can you optimize them?

## Ссылки (RU)

- [Документация по `View`](https://developer.android.com/reference/android/view/View)
- [Руководство по кастомным `View`](https://developer.android.com/develop/ui/views/layout/custom-views/custom-components)

## References

- [`View` API Reference](https://developer.android.com/reference/android/view/View)
- [Custom `Views` Guide](https://developer.android.com/develop/ui/views/layout/custom-views/custom-components)

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-what-is-the-main-application-execution-thread--android--easy]] — основы UI-потока

### Связанные (тот Же уровень)
- [[q-recyclerview-sethasfixedsize--android--easy]] — оптимизация `RecyclerView`
- [[q-viewmodel-pattern--android--easy]] — паттерн `ViewModel`

### Продвинутое (сложнее)
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] — детали перерисовки `View`
- [[q-fragments-and-activity-relationship--android--hard]] — жизненный цикл `Fragment`

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-the-main-application-execution-thread--android--easy]] - UI thread basics

### Related (Same Level)
- [[q-recyclerview-sethasfixedsize--android--easy]] - `RecyclerView` optimization
- [[q-viewmodel-pattern--android--easy]] - `ViewModel` pattern

### Advanced (Harder)
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - `View` redrawing deep dive
- [[q-fragments-and-activity-relationship--android--hard]] - `Fragment` lifecycle
