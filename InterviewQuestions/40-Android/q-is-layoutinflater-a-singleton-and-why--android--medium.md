---
topic: android
tags:
  - LayoutInflater
  - Context
  - Singleton
  - android
  - ui
  - layoutinflater
difficulty: medium
status: draft
---

# Is LayoutInflater a singleton and why

# Вопрос (RU)

Является ли LayoutInflater синглтоном и почему

## Answer (EN)
No, **LayoutInflater is not a singleton**, but can be obtained as a scope-dependent object (`getSystemService`) in Context. However, it can be reused as it doesn't store state between calls.

### How LayoutInflater Works

```kotlin
class InflaterExample : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Each call returns the same instance per Context
        val inflater1 = getSystemService(Context.LAYOUT_INFLATER_SERVICE) as LayoutInflater
        val inflater2 = getSystemService(Context.LAYOUT_INFLATER_SERVICE) as LayoutInflater
        val inflater3 = LayoutInflater.from(this)

        // All reference the same instance for this Context
        println(inflater1 === inflater2) // true
        println(inflater2 === inflater3) // true
    }
}
```

### Not a Global Singleton

Different contexts have different LayoutInflater instances.

```kotlin
class ContextInflaters : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val activityInflater = LayoutInflater.from(this)
        val appInflater = LayoutInflater.from(applicationContext)

        // Different instances for different contexts
        println(activityInflater === appInflater) // false

        // Each has different theme/context
        println(activityInflater.context === this) // true
        println(appInflater.context === applicationContext) // true
    }
}
```

### Why It Can Be Reused

LayoutInflater is stateless between calls.

```kotlin
class StatelessInflater : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val inflater = LayoutInflater.from(this)
        val container = findViewById<ViewGroup>(R.id.container)

        // Can reuse for multiple inflations
        val view1 = inflater.inflate(R.layout.item1, container, false)
        val view2 = inflater.inflate(R.layout.item2, container, false)
        val view3 = inflater.inflate(R.layout.item3, container, false)

        container.addView(view1)
        container.addView(view2)
        container.addView(view3)
    }
}
```

### Internal Caching

```kotlin
// Inside Context implementation
private LayoutInflater mLayoutInflater

fun getSystemService(name: String): Any? {
    if (LAYOUT_INFLATER_SERVICE == name) {
        if (mLayoutInflater == null) {
            mLayoutInflater = LayoutInflater.from(this)
        }
        return mLayoutInflater
    }
    // Other services...
}
```

### Best Practices

```kotlin
// - GOOD: Reuse in adapter
class MyAdapter(
    private val inflater: LayoutInflater,
    private val items: List<Item>
) : RecyclerView.Adapter<ViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = inflater.inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }
}

// Usage
val adapter = MyAdapter(LayoutInflater.from(context), items)

// - BAD: Creating new inflater each time
class BadAdapter(private val items: List<Item>) : RecyclerView.Adapter<ViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val inflater = LayoutInflater.from(parent.context) // New call each time (but returns cached)
        val view = inflater.inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }
}
```

## Ответ (RU)

**Нет, LayoutInflater не является синглтоном**, но он кэшируется на уровне каждого Context. Это означает, что разные Context'ы имеют свои собственные экземпляры LayoutInflater, но в рамках одного Context возвращается один и тот же экземпляр.

### Как работает LayoutInflater

LayoutInflater получается через системный сервис и кэшируется Context'ом:

```kotlin
class InflaterExample : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Все три вызова возвращают один и тот же экземпляр для данного Context
        val inflater1 = getSystemService(Context.LAYOUT_INFLATER_SERVICE) as LayoutInflater
        val inflater2 = getSystemService(Context.LAYOUT_INFLATER_SERVICE) as LayoutInflater
        val inflater3 = LayoutInflater.from(this)

        // Все ссылаются на один экземпляр в рамках этого Context
        println(inflater1 === inflater2) // true
        println(inflater2 === inflater3) // true
    }
}
```

### Не глобальный синглтон

У разных Context есть свои экземпляры LayoutInflater:

```kotlin
class ContextInflaters : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val activityInflater = LayoutInflater.from(this)
        val appInflater = LayoutInflater.from(applicationContext)

        // Разные экземпляры для разных Context
        println(activityInflater === appInflater) // false

        // Каждый связан со своим Context и темой
        println(activityInflater.context === this) // true
        println(appInflater.context === applicationContext) // true
    }
}
```

### Почему можно переиспользовать

LayoutInflater не хранит состояние между вызовами inflate() - он stateless:

```kotlin
class StatelessInflater : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val inflater = LayoutInflater.from(this)
        val container = findViewById<ViewGroup>(R.id.container)

        // Можно переиспользовать для множества inflate операций
        val view1 = inflater.inflate(R.layout.item1, container, false)
        val view2 = inflater.inflate(R.layout.item2, container, false)
        val view3 = inflater.inflate(R.layout.item3, container, false)

        container.addView(view1)
        container.addView(view2)
        container.addView(view3)
    }
}
```

### Внутреннее кэширование

Концептуально Context кэширует LayoutInflater так:

```kotlin
// Внутри реализации Context (упрощено)
private var mLayoutInflater: LayoutInflater? = null

fun getSystemService(name: String): Any? {
    if (LAYOUT_INFLATER_SERVICE == name) {
        if (mLayoutInflater == null) {
            mLayoutInflater = PolicyManager.makeNewLayoutInflater(this)
        }
        return mLayoutInflater
    }
    // Другие сервисы...
}
```

### Почему важен Context

LayoutInflater зависит от Context, потому что Context содержит:
- **Тему приложения/Activity** - влияет на стили View
- **Ресурсы** - доступ к layout файлам
- **ClassLoader** - для создания экземпляров View классов

```kotlin
class ThemeExample : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Activity inflater использует тему Activity
        val activityInflater = LayoutInflater.from(this)

        // Application inflater использует тему Application
        val appInflater = LayoutInflater.from(applicationContext)

        // Результаты могут визуально отличаться из-за разных тем!
        val view1 = activityInflater.inflate(R.layout.themed_view, null, false)
        val view2 = appInflater.inflate(R.layout.themed_view, null, false)
    }
}
```

### Лучшие практики использования

**Правильно: Переиспользуйте в адаптере**

```kotlin
class MyAdapter(
    private val inflater: LayoutInflater,
    private val items: List<Item>
) : RecyclerView.Adapter<ViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = inflater.inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun getItemCount() = items.size
}

// Использование
val adapter = MyAdapter(LayoutInflater.from(context), items)
```

**Неоптимально (но работает): Получение inflater каждый раз**

```kotlin
class BadAdapter(private val items: List<Item>) : RecyclerView.Adapter<ViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        // Вызывается каждый раз, но возвращает закэшированный экземпляр
        val inflater = LayoutInflater.from(parent.context)
        val view = inflater.inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }
}
```

**Важно: Правильный parent при inflate**

```kotlin
// Правильно - передаем parent и false
val view = inflater.inflate(R.layout.item, parent, false)

// Неправильно - null parent игнорирует layout_* параметры
val view = inflater.inflate(R.layout.item, null, false)

// Неправильно - true добавляет view автоматически (не нужно для RecyclerView)
val view = inflater.inflate(R.layout.item, parent, true)
```

### Производительность

Хотя LayoutInflater кэшируется, сам процесс inflate дорогой:

```kotlin
class PerformanceExample {

    // Правильно: Переиспользуйте View вместо повторного inflate
    fun updateView(view: View, data: Data) {
        view.findViewById<TextView>(R.id.title).text = data.title
        view.findViewById<TextView>(R.id.subtitle).text = data.subtitle
    }

    // Неправильно: Избегайте inflate в циклах
    fun badApproach(container: ViewGroup, items: List<Item>) {
        val inflater = LayoutInflater.from(container.context)
        items.forEach { item ->
            val view = inflater.inflate(R.layout.item, container, true) // Медленно!
            // setup view
        }
    }

    // Правильно: Используйте RecyclerView для списков
    fun goodApproach(recyclerView: RecyclerView, items: List<Item>) {
        recyclerView.adapter = MyAdapter(items) // View переиспользуются автоматически
    }
}
```

### Резюме

**LayoutInflater не является глобальным синглтоном**, но:
- Кэшируется на уровне каждого Context
- Один экземпляр на один Context
- Разные Context имеют разные экземпляры
- Stateless - можно безопасно переиспользовать
- Зависит от Context для темы и ресурсов

**Практические выводы:**
- Получайте через `LayoutInflater.from(context)` или `getSystemService()`
- Передавайте в конструктор адаптера для переиспользования
- Помните, что разные Context могут дать разные визуальные результаты из-за тем
