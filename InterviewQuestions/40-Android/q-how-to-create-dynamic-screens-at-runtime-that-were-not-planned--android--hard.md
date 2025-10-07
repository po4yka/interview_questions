---
topic: android
tags:
  - Jetpack Compose
  - Fragment
  - RecyclerView
  - dynamic UI
  - android
  - ui
  - dynamic-ui
  - jetpack-compose
difficulty: medium
status: draft
---

# How to create dynamic screens at runtime that were not planned?

## Question (RU)

Как в runtime делать динамические экраны которые не были предусмотрены

## Answer

To create dynamic screens at runtime in Android: Load configuration from server (JSON/XML), use Fragment/View factories, generate UI from description, or use Jetpack Compose/RecyclerView with different ViewTypes.

### 1. Server-Driven UI with JSON

```kotlin
// JSON structure from server
data class ScreenConfig(
    val type: String,
    val title: String,
    val components: List<Component>
)

data class Component(
    val type: String,
    val properties: Map<String, Any>
)

// Dynamic screen builder
class DynamicScreenBuilder {

    fun buildScreen(config: ScreenConfig, container: ViewGroup) {
        container.removeAllViews()

        config.components.forEach { component ->
            val view = createViewForComponent(component, container.context)
            container.addView(view)
        }
    }

    private fun createViewForComponent(component: Component, context: Context): View {
        return when (component.type) {
            "text" -> TextView(context).apply {
                text = component.properties["text"] as? String
                textSize = (component.properties["size"] as? Double)?.toFloat() ?: 14f
            }

            "button" -> Button(context).apply {
                text = component.properties["text"] as? String
                setOnClickListener {
                    // Handle dynamic action
                }
            }

            "image" -> ImageView(context).apply {
                val url = component.properties["url"] as? String
                // Load image with Coil/Glide
            }

            else -> TextView(context).apply { text = "Unknown component" }
        }
    }
}
```

### 2. Jetpack Compose Dynamic UI

```kotlin
@Composable
fun DynamicScreen(config: ScreenConfig) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        config.components.forEach { component ->
            DynamicComponent(component)
        }
    }
}

@Composable
fun DynamicComponent(component: Component) {
    when (component.type) {
        "text" -> Text(
            text = component.properties["text"] as? String ?: "",
            fontSize = (component.properties["size"] as? Int ?: 14).sp
        )

        "button" -> Button(
            onClick = { /* dynamic action */ }
        ) {
            Text(component.properties["text"] as? String ?: "Button")
        }

        "image" -> AsyncImage(
            model = component.properties["url"],
            contentDescription = null,
            modifier = Modifier.size(200.dp)
        )

        "input" -> {
            var text by remember { mutableStateOf("") }
            TextField(
                value = text,
                onValueChange = { text = it },
                label = { Text(component.properties["label"] as? String ?: "") }
            )
        }

        else -> Text("Unknown component: ${component.type}")
    }

    Spacer(modifier = Modifier.height(8.dp))
}
```

### 3. RecyclerView with Multiple ViewTypes

```kotlin
class DynamicAdapter(
    private val components: List<Component>
) : RecyclerView.Adapter<RecyclerView.ViewHolder>() {

    companion object {
        const val TYPE_TEXT = 0
        const val TYPE_BUTTON = 1
        const val TYPE_IMAGE = 2
        const val TYPE_INPUT = 3
    }

    override fun getItemViewType(position: Int): Int {
        return when (components[position].type) {
            "text" -> TYPE_TEXT
            "button" -> TYPE_BUTTON
            "image" -> TYPE_IMAGE
            "input" -> TYPE_INPUT
            else -> TYPE_TEXT
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return when (viewType) {
            TYPE_TEXT -> TextViewHolder(
                TextView(parent.context).apply {
                    layoutParams = ViewGroup.LayoutParams(MATCH_PARENT, WRAP_CONTENT)
                    setPadding(16.dp, 8.dp, 16.dp, 8.dp)
                }
            )
            TYPE_BUTTON -> ButtonViewHolder(
                Button(parent.context).apply {
                    layoutParams = ViewGroup.LayoutParams(MATCH_PARENT, WRAP_CONTENT)
                }
            )
            TYPE_IMAGE -> ImageViewHolder(
                ImageView(parent.context).apply {
                    layoutParams = ViewGroup.LayoutParams(MATCH_PARENT, 200.dp)
                    scaleType = ImageView.ScaleType.CENTER_CROP
                }
            )
            TYPE_INPUT -> InputViewHolder(
                EditText(parent.context).apply {
                    layoutParams = ViewGroup.LayoutParams(MATCH_PARENT, WRAP_CONTENT)
                }
            )
            else -> TextViewHolder(TextView(parent.context))
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        val component = components[position]

        when (holder) {
            is TextViewHolder -> holder.bind(component)
            is ButtonViewHolder -> holder.bind(component)
            is ImageViewHolder -> holder.bind(component)
            is InputViewHolder -> holder.bind(component)
        }
    }

    override fun getItemCount() = components.size

    class TextViewHolder(private val textView: TextView) : RecyclerView.ViewHolder(textView) {
        fun bind(component: Component) {
            textView.text = component.properties["text"] as? String
        }
    }

    class ButtonViewHolder(private val button: Button) : RecyclerView.ViewHolder(button) {
        fun bind(component: Component) {
            button.text = component.properties["text"] as? String
        }
    }

    class ImageViewHolder(private val imageView: ImageView) : RecyclerView.ViewHolder(imageView) {
        fun bind(component: Component) {
            val url = component.properties["url"] as? String
            // Load with Coil/Glide
        }
    }

    class InputViewHolder(private val editText: EditText) : RecyclerView.ViewHolder(editText) {
        fun bind(component: Component) {
            editText.hint = component.properties["hint"] as? String
        }
    }

    private val Int.dp: Int
        get() = (this * itemView.context.resources.displayMetrics.density).toInt()
}
```

### 4. Fragment Factory Pattern

```kotlin
class DynamicFragmentFactory(
    private val config: Map<String, Any>
) : FragmentFactory() {

    override fun instantiate(classLoader: ClassLoader, className: String): Fragment {
        return when (config["type"]) {
            "list" -> ListFragment.newInstance(config)
            "detail" -> DetailFragment.newInstance(config)
            "form" -> FormFragment.newInstance(config)
            else -> super.instantiate(classLoader, className)
        }
    }
}

// Usage
supportFragmentManager.fragmentFactory = DynamicFragmentFactory(serverConfig)
```

### 5. DSL for UI Building

```kotlin
class UiBuilder(private val context: Context) {

    fun build(block: UiScope.() -> Unit): View {
        val scope = UiScope(context)
        scope.block()
        return scope.root
    }
}

class UiScope(private val context: Context) {
    val root = LinearLayout(context).apply {
        orientation = LinearLayout.VERTICAL
        layoutParams = LinearLayout.LayoutParams(MATCH_PARENT, MATCH_PARENT)
    }

    fun text(text: String, size: Float = 14f) {
        root.addView(TextView(context).apply {
            this.text = text
            textSize = size
        })
    }

    fun button(text: String, onClick: () -> Unit) {
        root.addView(Button(context).apply {
            this.text = text
            setOnClickListener { onClick() }
        })
    }

    fun image(url: String) {
        root.addView(ImageView(context).apply {
            // Load image
        })
    }
}

// Usage
val view = UiBuilder(context).build {
    text("Dynamic Title", 20f)
    button("Click Me") {
        // Handle click
    }
    image("https://example.com/image.jpg")
}
```

### 6. Server Response Example

```json
{
  "screen_id": "home_v2",
  "type": "scroll",
  "title": "Home",
  "components": [
    {
      "type": "text",
      "properties": {
        "text": "Welcome",
        "size": 24,
        "color": "#000000"
      }
    },
    {
      "type": "image",
      "properties": {
        "url": "https://example.com/banner.jpg",
        "aspect_ratio": "16:9"
      }
    },
    {
      "type": "button",
      "properties": {
        "text": "Get Started",
        "action": "navigate",
        "destination": "signup"
      }
    }
  ]
}
```

### 7. Complete Example with Networking

```kotlin
class DynamicScreenActivity : AppCompatActivity() {

    private lateinit var container: LinearLayout

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        container = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = LinearLayout.LayoutParams(MATCH_PARENT, MATCH_PARENT)
        }

        setContentView(container)

        loadDynamicScreen()
    }

    private fun loadDynamicScreen() {
        lifecycleScope.launch {
            try {
                val config = fetchScreenConfig()
                buildDynamicUI(config)
            } catch (e: Exception) {
                showError(e)
            }
        }
    }

    private suspend fun fetchScreenConfig(): ScreenConfig {
        // Fetch from server
        return withContext(Dispatchers.IO) {
            // API call
            ScreenConfig(/* ... */)
        }
    }

    private fun buildDynamicUI(config: ScreenConfig) {
        DynamicScreenBuilder().buildScreen(config, container)
    }
}
```

## Answer (RU)

Загружать конфигурацию с сервера JSON XML Использовать Fragment View фабрики Генерировать UI из описания Использовать Jetpack Compose или RecyclerView с различными ViewType
