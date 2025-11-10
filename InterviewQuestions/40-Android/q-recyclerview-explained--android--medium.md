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
- q-what-does-itemdecoration-do--android--medium
- q-why-are-fragments-needed-if-there-is-activity--android--hard
created: 2025-10-15
updated: 2025-11-10
tags:
- android/ui-views
- difficulty/medium

---

# Вопрос (RU)
> Объяснение RecyclerView

# Question (EN)
> RecyclerView Explained

---

## Ответ (RU)

RecyclerView — это мощный UI-компонент из библиотеки AndroidX (`androidx.recyclerview`), предназначенный для отображения динамических, потенциально больших списков элементов. Он был представлен как более гибкая и расширяемая замена ListView.

### Основные особенности

#### 1. Эффективное повторное использование `View`

Использует паттерн ViewHolder для эффективного повторного использования элементов при прокрутке.

```kotlin
class MyViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
    val textView: TextView = itemView.findViewById(R.id.textView)
    val imageView: ImageView = itemView.findViewById(R.id.imageView)
}
```

Это повышает производительность для больших списков, так как количество создаваемых объектов `View` ограничено (примерно) видимыми элементами плюс небольшой буфер, а не одним `View` на каждый элемент.

#### 2. Гибкое отображение элементов

Поддерживает различные компоновки через API LayoutManager:

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

// Staggered grid
recyclerView.layoutManager = StaggeredGridLayoutManager(
    2,
    StaggeredGridLayoutManager.VERTICAL
)
```

Также можно реализовать свой собственный LayoutManager для сложных сценариев.

#### 3. Анимация изменений

RecyclerView поддерживает анимации добавления, удаления, перемещения и изменения элементов через `RecyclerView.ItemAnimator` (по умолчанию `DefaultItemAnimator`).

```kotlin
class MyAdapter : RecyclerView.Adapter<MyViewHolder>() {
    private val items = mutableListOf<String>()

    fun addItem(item: String, position: Int) {
        items.add(position, item)
        notifyItemInserted(position)  // Запускает анимацию через ItemAnimator
    }

    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)  // Запускает анимацию через ItemAnimator
    }
}
```

#### 4. Декорации и разделители

`RecyclerView.ItemDecoration` упрощает добавление пользовательского рисования (разделители, отступы и т.п.) вокруг элементов.

```kotlin
class SimpleDividerItemDecoration : RecyclerView.ItemDecoration() {
    override fun onDraw(c: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        // Рисование разделителей
    }
}

recyclerView.addItemDecoration(SimpleDividerItemDecoration())
```

Также доступен встроенный `DividerItemDecoration` из `androidx.recyclerview.widget` для стандартных разделителей.

#### 5. Обработка нажатий на элементы

В отличие от ListView, RecyclerView не предоставляет встроенного `setOnItemClickListener`. Обработку кликов реализуют явно, что даёт больше гибкости и лучшую разделяемость ответственности.

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

### Ключевые компоненты

**Adapter** – отвечает за создание ViewHolder и привязку данных к ним.

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

**LayoutManager** – управляет расположением элементов и поведением прокрутки внутри RecyclerView.

**ViewHolder** – хранит ссылки на `View` для отображения данных элемента, уменьшая количество вызовов `findViewById`.

### Полный пример

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

        // Добавление разделителей с помощью встроенного DividerItemDecoration
        recyclerView.addItemDecoration(
            DividerItemDecoration(this, DividerItemDecoration.VERTICAL)
        )
    }
}
```

### Преимущества перед ListView

| Аспект | ListView | RecyclerView |
|--------|----------|--------------|
| **ViewHolder** | Необязателен (ручная оптимизация) | Требуется API (навязывает эффективное переиспользование) |
| **Layouts** | В основном вертикальный список | Плагинные LayoutManager'ы (вертикальный, горизонтальный, сетка, кастомный) |
| **Анимации** | Ограниченные/базовые (layout animations) | Отдельный ItemAnimator для анимаций на уровне элементов |
| **Декорации** | Ручная отрисовка в layout/adapter | ItemDecoration API, встроенный DividerItemDecoration |
| **Производительность/расширяемость** | Достаточна для простых списков | Лучше подходит для больших/сложных списков и кастомных поведений |

RecyclerView — это гибкий, расширяемый и производительный компонент для реализации списков и сеток с контролируемым переиспользованием `View`, настраиваемыми LayoutManager'ами, анимациями и декорациями.

---

## Answer (EN)
RecyclerView is a powerful UI component from the AndroidX `androidx.recyclerview` library designed for displaying dynamic, potentially large lists of items. It was introduced as a more flexible and extensible replacement for ListView.

### Key Features

#### 1. Efficient `View` Recycling

Uses the ViewHolder pattern for efficient reuse of item views during scrolling.

```kotlin
class MyViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
    val textView: TextView = itemView.findViewById(R.id.textView)
    val imageView: ImageView = itemView.findViewById(R.id.imageView)
}
```

This improves performance for large lists since the number of created `View` objects is limited to (roughly) those visible on screen plus a small buffer, instead of one per item.

#### 2. Flexible Item Display

Supports various layouts through the LayoutManager API:

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

// Staggered grid
recyclerView.layoutManager = StaggeredGridLayoutManager(
    2,
    StaggeredGridLayoutManager.VERTICAL
)
```

You can also implement custom LayoutManagers for advanced behaviors.

#### 3. Change Animations

RecyclerView supports item change animations (add, remove, move, change) via `RecyclerView.ItemAnimator` (by default `DefaultItemAnimator`).

```kotlin
class MyAdapter : RecyclerView.Adapter<MyViewHolder>() {
    private val items = mutableListOf<String>()

    fun addItem(item: String, position: Int) {
        items.add(position, item)
        notifyItemInserted(position)  // Triggers ItemAnimator animation
    }

    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)  // Triggers ItemAnimator animation
    }
}
```

#### 4. Decorations and Dividers

`RecyclerView.ItemDecoration` makes it easy to add custom drawing (e.g., dividers, padding) around items.

```kotlin
class SimpleDividerItemDecoration : RecyclerView.ItemDecoration() {
    override fun onDraw(c: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        // Draw dividers
    }
}

recyclerView.addItemDecoration(SimpleDividerItemDecoration())
```

You can also use the built-in `DividerItemDecoration` from `androidx.recyclerview.widget` for standard dividers.

#### 5. Click Event Handling

Unlike ListView, RecyclerView does not provide a built-in `setOnItemClickListener`. Item click handling is implemented explicitly, which gives more flexibility and better separation of concerns.

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

**Adapter** – responsible for creating ViewHolders and binding data to them.

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

**LayoutManager** – manages item positioning and scrolling behavior inside RecyclerView.

**ViewHolder** – holds references to Views that display item data, minimizing expensive `findViewById` calls.

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

        // Add dividers using built-in DividerItemDecoration
        recyclerView.addItemDecoration(
            DividerItemDecoration(this, DividerItemDecoration.VERTICAL)
        )
    }
}
```

### Advantages over ListView

| Aspect | ListView | RecyclerView |
|--------|----------|--------------|
| **ViewHolder** | Optional (manual optimization) | Required by API (enforces efficient reuse) |
| **Layouts** | Primarily vertical list | Pluggable LayoutManagers (vertical, horizontal, grid, custom) |
| **Animations** | Limited/basic (e.g., layout animations) | Dedicated ItemAnimator API for item-level animations |
| **Decorations** | Manual handling in adapter/view | ItemDecoration API, built-in DividerItemDecoration |
| **Performance/Extensibility** | Adequate for simple lists | Better suited for large/complex lists and custom behaviors |

RecyclerView is a flexible, extensible, and high-performance component for list and grid UIs, with explicit control over view recycling, layout, animations, and decorations.

---

## Follow-ups

- [[q-what-does-itemdecoration-do--android--medium]]
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]]
- [[q-recyclerview-sethasfixedsize--android--easy]]
- [[q-how-animations-work-in-recyclerview--android--medium]]
- [[q-recyclerview-async-list-differ--android--medium]]


## References

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)


## Related Questions

### Prerequisites / Concepts


### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - `View`, Ui
- [[q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy]] - `View`, Ui

### Related (Medium)
- q-rxjava-pagination-recyclerview--android--medium - `View`, Ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - `View`, Ui
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - `View`, Ui
- [[q-how-animations-work-in-recyclerview--android--medium]] - `View`, Ui
- [[q-recyclerview-async-list-differ--android--medium]] - `View`, Ui
