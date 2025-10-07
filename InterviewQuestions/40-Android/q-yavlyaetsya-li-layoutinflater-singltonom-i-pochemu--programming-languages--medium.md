---
tags:
  - programming-languages
  - android
difficulty: medium
status: draft
---

# Является ли LayoutInflater синглтоном и почему?

## Answer

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
// ✅ GOOD: Reuse in adapter
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

// ❌ BAD: Creating new inflater each time
class BadAdapter(private val items: List<Item>) : RecyclerView.Adapter<ViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val inflater = LayoutInflater.from(parent.context) // New call each time (but returns cached)
        val view = inflater.inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }
}
```

---

# Является ли LayoutInflater синглтоном и почему

## Ответ

Нет, LayoutInflater — не синглтон, но может быть получен как скоуп-зависимый объект (getSystemService) в Context. Однако его можно переиспользовать, так как он не хранит состояния между вызовами
