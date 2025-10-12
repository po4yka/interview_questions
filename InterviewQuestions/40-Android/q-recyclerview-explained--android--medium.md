---
topic: android
tags:
  - android
  - recyclerview
  - ui-components
difficulty: medium
status: draft
---

# Что известно про RecyclerView?

**English**: What do you know about RecyclerView?

## Answer (EN)
RecyclerView — это мощный компонент пользовательского интерфейса, предоставляемый библиотекой AndroidX, предназначенный для отображения динамических списков элементов. Он был представлен как улучшенная и более гибкая замена ListView.

### Основные особенности

#### 1. Эффективное повторное использование View

Использует концепцию ViewHolder для эффективного повторного использования элементов списка при прокрутке.

```kotlin
class MyViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
    val textView: TextView = itemView.findViewById(R.id.textView)
    val imageView: ImageView = itemView.findViewById(R.id.imageView)
}
```

Это повышает производительность для больших списков, поскольку количество создаваемых объектов View ограничивается только теми, которые видны пользователю.

#### 2. Гибкое отображение элементов

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

#### 3. Анимация изменений

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

#### 4. Декорации и разделители

С помощью класса ItemDecoration можно легко добавлять разделители между элементами.

```kotlin
class DividerItemDecoration : RecyclerView.ItemDecoration() {
    override fun onDraw(c: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        // Рисование разделителей
    }
}

recyclerView.addItemDecoration(DividerItemDecoration())
```

#### 5. Обработка событий нажатий

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

### Ключевые компоненты

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

        // Добавление разделителей
        recyclerView.addItemDecoration(
            DividerItemDecoration(this, DividerItemDecoration.VERTICAL)
        )
    }
}
```

### Преимущества перед ListView

| Аспект | ListView | RecyclerView |
|--------|----------|--------------|
| **ViewHolder** | Опционально | Обязательно (лучше производительность) |
| **Layouts** | Только вертикальный | Вертикальный, горизонтальный, сетка |
| **Анимации** | Нет встроенных | Встроенные анимации |
| **Декорации** | Сложно | ItemDecoration API |
| **Производительность** | Хорошая | Отличная |

**English**: RecyclerView is a powerful, flexible UI component for displaying dynamic lists with efficient view recycling via ViewHolder pattern. Supports multiple layouts (linear, grid, staggered), built-in animations, custom decorations, and better performance than ListView through mandatory ViewHolder usage.
