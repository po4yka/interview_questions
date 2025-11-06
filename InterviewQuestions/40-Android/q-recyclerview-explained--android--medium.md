---
id: android-292
title: RecyclerView Explained / Объяснение RecyclerView
aliases:
- RecyclerView Explained
- Объяснение RecyclerView
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
- q-kmm-dependency-injection--multiplatform--medium
- q-what-does-itemdecoration-do--android--medium
- q-why-are-fragments-needed-if-there-is-activity--android--hard
created: 2025-10-15
updated: 2025-10-31
tags:
- android/ui-views
- difficulty/medium
date created: Saturday, November 1st 2025, 12:47:01 pm
date modified: Saturday, November 1st 2025, 5:43:32 pm
---

# Вопрос (RU)
> Объяснение RecyclerView

# Question (EN)
> RecyclerView Explained

---

## Answer (EN)
RecyclerView — это мощный компонент пользовательского интерфейса, предоставляемый библиотекой AndroidX, предназначенный для отображения динамических списков элементов. Он был представлен как улучшенная и более гибкая замена ListView.

### Key Features

#### 1. Efficient View Recycling

Uses ViewHolder pattern for efficient reuse of list items during scrolling.

```kotlin
class MyViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
    val textView: TextView = itemView.findViewById(R.id.textView)
    val imageView: ImageView = itemView.findViewById(R.id.imageView)
}
```

This improves performance for large lists since the number of created View objects is limited to only those visible to the user.

#### 2. Flexible Item Display

Supports various layouts through LayoutManager API:

```kotlin
// Vertical list
recyclerView.layoutManager = LinearLayoutManager(context)

// Horizontal list
recyclerView.layoutManager = LinearLayoutManager(
    context,
    LinearLayoutManager.HORIZONTAL,
    false
)

// Grid
recyclerView.layoutManager = GridLayoutManager(context, 2)

// Staggered Grid
recyclerView.layoutManager = StaggeredGridLayoutManager(
    2,
    StaggeredGridLayoutManager.VERTICAL
)
```

#### 3. Change Animations

Built-in animation support for add, remove, and move operations.

```kotlin
class MyAdapter : RecyclerView.Adapter<MyViewHolder>() {
    private val items = mutableListOf<String>()

    fun addItem(item: String, position: Int) {
        items.add(position, item)
        notifyItemInserted(position)  // Automatic animation
    }

    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)  // Automatic animation
    }
}
```

#### 4. Decorations and Dividers

ItemDecoration class makes it easy to add dividers between items.

```kotlin
class DividerItemDecoration : RecyclerView.ItemDecoration() {
    override fun onDraw(c: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        // Draw dividers
    }
}

recyclerView.addItemDecoration(DividerItemDecoration())
```

#### 5. Click Event Handling

Unlike ListView, RecyclerView doesn't have built-in method for handling item clicks, providing more flexibility.

```kotlin
class MyAdapter : RecyclerView.Adapter<MyViewHolder>() {
    var onItemClick: ((Int) -> Unit)? = null

    override fun onBindViewHolder(holder: MyViewHolder, position: Int) {
        holder.itemView.setOnClickListener {
            onItemClick?.invoke(position)
        }
    }
}

// Usage
adapter.onItemClick = { position ->
    Toast.makeText(context, "Clicked: $position", Toast.LENGTH_SHORT).show()
}
```

### Key Components

**Adapter** - responsible for binding data to ViewHolder and creating ViewHolder.

```kotlin
class MyAdapter(private val items: List<String>) :
    RecyclerView.Adapter<MyAdapter.MyViewHolder>() {

    class MyViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val textView: TextView = itemView.findViewById(R.id.textView)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MyViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return MyViewHolder(view)
    }

    override fun onBindViewHolder(holder: MyViewHolder, position: Int) {
        holder.textView.text = items[position]
    }

    override fun getItemCount() = items.size
}
```

**LayoutManager** - manages item positioning inside RecyclerView.

**ViewHolder** - holds references to all Views that need to be filled with data.

### Complete Example

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val recyclerView = findViewById<RecyclerView>(R.id.recyclerView)

        // Setup LayoutManager
        recyclerView.layoutManager = LinearLayoutManager(this)

        // Create and set adapter
        val items = listOf("Item 1", "Item 2", "Item 3")
        val adapter = MyAdapter(items)
        recyclerView.adapter = adapter

        // Add dividers
        recyclerView.addItemDecoration(
            DividerItemDecoration(this, DividerItemDecoration.VERTICAL)
        )
    }
}
```

### Advantages over ListView

| Aspect | ListView | RecyclerView |
|--------|----------|--------------|
| **ViewHolder** | Optional | Mandatory (better performance) |
| **Layouts** | Vertical only | Vertical, horizontal, grid |
| **Animations** | No built-in | Built-in animations |
| **Decorations** | Difficult | ItemDecoration API |
| **Performance** | Good | Excellent |


# Question (EN)
> RecyclerView Explained

---


---


## Answer (EN)
RecyclerView — это мощный компонент пользовательского интерфейса, предоставляемый библиотекой AndroidX, предназначенный для отображения динамических списков элементов. Он был представлен как улучшенная и более гибкая замена ListView.

### Key Features

#### 1. Efficient View Recycling

Uses ViewHolder pattern for efficient reuse of list items during scrolling.

```kotlin
class MyViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
    val textView: TextView = itemView.findViewById(R.id.textView)
    val imageView: ImageView = itemView.findViewById(R.id.imageView)
}
```

This improves performance for large lists since the number of created View objects is limited to only those visible to the user.

#### 2. Flexible Item Display

Supports various layouts through LayoutManager API:

```kotlin
// Vertical list
recyclerView.layoutManager = LinearLayoutManager(context)

// Horizontal list
recyclerView.layoutManager = LinearLayoutManager(
    context,
    LinearLayoutManager.HORIZONTAL,
    false
)

// Grid
recyclerView.layoutManager = GridLayoutManager(context, 2)

// Staggered Grid
recyclerView.layoutManager = StaggeredGridLayoutManager(
    2,
    StaggeredGridLayoutManager.VERTICAL
)
```

#### 3. Change Animations

Built-in animation support for add, remove, and move operations.

```kotlin
class MyAdapter : RecyclerView.Adapter<MyViewHolder>() {
    private val items = mutableListOf<String>()

    fun addItem(item: String, position: Int) {
        items.add(position, item)
        notifyItemInserted(position)  // Automatic animation
    }

    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)  // Automatic animation
    }
}
```

#### 4. Decorations and Dividers

ItemDecoration class makes it easy to add dividers between items.

```kotlin
class DividerItemDecoration : RecyclerView.ItemDecoration() {
    override fun onDraw(c: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        // Draw dividers
    }
}

recyclerView.addItemDecoration(DividerItemDecoration())
```

#### 5. Click Event Handling

Unlike ListView, RecyclerView doesn't have built-in method for handling item clicks, providing more flexibility.

```kotlin
class MyAdapter : RecyclerView.Adapter<MyViewHolder>() {
    var onItemClick: ((Int) -> Unit)? = null

    override fun onBindViewHolder(holder: MyViewHolder, position: Int) {
        holder.itemView.setOnClickListener {
            onItemClick?.invoke(position)
        }
    }
}

// Usage
adapter.onItemClick = { position ->
    Toast.makeText(context, "Clicked: $position", Toast.LENGTH_SHORT).show()
}
```

### Key Components

**Adapter** - responsible for binding data to ViewHolder and creating ViewHolder.

```kotlin
class MyAdapter(private val items: List<String>) :
    RecyclerView.Adapter<MyAdapter.MyViewHolder>() {

    class MyViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val textView: TextView = itemView.findViewById(R.id.textView)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MyViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return MyViewHolder(view)
    }

    override fun onBindViewHolder(holder: MyViewHolder, position: Int) {
        holder.textView.text = items[position]
    }

    override fun getItemCount() = items.size
}
```

**LayoutManager** - manages item positioning inside RecyclerView.

**ViewHolder** - holds references to all Views that need to be filled with data.

### Complete Example

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val recyclerView = findViewById<RecyclerView>(R.id.recyclerView)

        // Setup LayoutManager
        recyclerView.layoutManager = LinearLayoutManager(this)

        // Create and set adapter
        val items = listOf("Item 1", "Item 2", "Item 3")
        val adapter = MyAdapter(items)
        recyclerView.adapter = adapter

        // Add dividers
        recyclerView.addItemDecoration(
            DividerItemDecoration(this, DividerItemDecoration.VERTICAL)
        )
    }
}
```

### Advantages over ListView

| Aspect | ListView | RecyclerView |
|--------|----------|--------------|
| **ViewHolder** | Optional | Mandatory (better performance) |
| **Layouts** | Vertical only | Vertical, horizontal, grid |
| **Animations** | No built-in | Built-in animations |
| **Decorations** | Difficult | ItemDecoration API |
| **Performance** | Good | Excellent |

## Ответ (RU)

RecyclerView - это мощный компонент пользовательского интерфейса, предоставляемый библиотекой AndroidX, предназначенный для отображения динамических списков элементов. Он был представлен как улучшенная и более гибкая замена ListView.

### Основные Особенности

#### 1. Эффективное Повторное Использование View

Использует концепцию ViewHolder для эффективного повторного использования элементов списка при прокрутке.

```kotlin
class MyViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
    val textView: TextView = itemView.findViewById(R.id.textView)
    val imageView: ImageView = itemView.findViewById(R.id.imageView)
}
```

Это повышает производительность для больших списков, поскольку количество создаваемых объектов View ограничивается только теми, которые видны пользователю.

#### 2. Гибкое Отображение Элементов

Поддерживает различные компоновки через LayoutManager API:

```kotlin
// Вертикальный список
recyclerView.layoutManager = LinearLayoutManager(context)

// Горизонтальный список
recyclerView.layoutManager = LinearLayoutManager(
    context,
    LinearLayoutManager.HORIZONTAL,
    false
)

// Сетка
recyclerView.layoutManager = GridLayoutManager(context, 2)

// Staggered Grid
recyclerView.layoutManager = StaggeredGridLayoutManager(
    2,
    StaggeredGridLayoutManager.VERTICAL
)
```

#### 3. Анимация Изменений

Встроенная поддержка анимаций для операций добавления, удаления и перемещения элементов.

```kotlin
class MyAdapter : RecyclerView.Adapter<MyViewHolder>() {
    private val items = mutableListOf<String>()

    fun addItem(item: String, position: Int) {
        items.add(position, item)
        notifyItemInserted(position)  // Автоматическая анимация
    }

    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)  // Автоматическая анимация
    }
}
```

#### 4. Декорации И Разделители

С помощью класса ItemDecoration можно легко добавлять разделители между элементами.

```kotlin
class DividerItemDecoration : RecyclerView.ItemDecoration() {
    override fun onDraw(c: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        // Рисование разделителей
    }
}

recyclerView.addItemDecoration(DividerItemDecoration())
```

#### 5. Обработка Событий Нажатий

В отличие от ListView, RecyclerView не имеет встроенного метода для обработки нажатий на элементы, что предоставляет больше гибкости.

```kotlin
class MyAdapter : RecyclerView.Adapter<MyViewHolder>() {
    var onItemClick: ((Int) -> Unit)? = null

    override fun onBindViewHolder(holder: MyViewHolder, position: Int) {
        holder.itemView.setOnClickListener {
            onItemClick?.invoke(position)
        }
    }
}

// Использование
adapter.onItemClick = { position ->
    Toast.makeText(context, "Clicked: $position", Toast.LENGTH_SHORT).show()
}
```

### Ключевые Компоненты

**Adapter** - отвечает за связь данных с ViewHolder и создание ViewHolder.

```kotlin
class MyAdapter(private val items: List<String>) :
    RecyclerView.Adapter<MyAdapter.MyViewHolder>() {

    class MyViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val textView: TextView = itemView.findViewById(R.id.textView)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MyViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return MyViewHolder(view)
    }

    override fun onBindViewHolder(holder: MyViewHolder, position: Int) {
        holder.textView.text = items[position]
    }

    override fun getItemCount() = items.size
}
```

**LayoutManager** - управляет расположением элементов внутри RecyclerView.

**ViewHolder** - содержит ссылки на все View, которые необходимо заполнить данными.

### Полный Пример

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val recyclerView = findViewById<RecyclerView>(R.id.recyclerView)

        // Настройка LayoutManager
        recyclerView.layoutManager = LinearLayoutManager(this)

        // Создание и установка адаптера
        val items = listOf("Item 1", "Item 2", "Item 3")
        val adapter = MyAdapter(items)
        recyclerView.adapter = adapter

        // Добавление разделителей
        recyclerView.addItemDecoration(
            DividerItemDecoration(this, DividerItemDecoration.VERTICAL)
        )
    }
}
```

### Преимущества Перед ListView

| Аспект | ListView | RecyclerView |
|--------|----------|--------------|
| **ViewHolder** | Опционально | Обязательно (лучше производительность) |
| **Layouts** | Только вертикальный | Вертикальный, горизонтальный, сетка |
| **Анимации** | Нет встроенных | Встроенные анимации |
| **Декорации** | Сложно | ItemDecoration API |
| **Производительность** | Хорошая | Отличная |

RecyclerView - это мощный, гибкий UI компонент для отображения динамических списков с эффективным повторным использованием view через паттерн ViewHolder. Поддерживает множественные layouts (linear, grid, staggered), встроенные анимации, пользовательские декорации и лучшую производительность чем ListView благодаря обязательному использованию ViewHolder.

---


## Follow-ups

- [[q-kmm-dependency-injection--multiplatform--medium]]
- [[q-what-does-itemdecoration-do--android--medium]]
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]]


## References

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)


## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - View, Ui
- [[q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy]] - View, Ui

### Related (Medium)
- q-rxjava-pagination-recyclerview--android--medium - View, Ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - View, Ui
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - View, Ui
- [[q-how-animations-work-in-recyclerview--android--medium]] - View, Ui
- [[q-recyclerview-async-list-differ--android--medium]] - View, Ui
