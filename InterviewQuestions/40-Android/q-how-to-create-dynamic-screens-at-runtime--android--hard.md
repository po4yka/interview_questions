---
id: android-184
title: How To Create Dynamic Screens At Runtime / Как создавать динамические экраны во время выполнения
aliases:
- How To Create Dynamic Screens At Runtime
- Как создавать динамические экраны во время выполнения
topic: android
subtopics:
- ui-views
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android-components
- q-fragments-history-and-purpose--android--hard
- q-how-is-navigation-implemented--android--medium
- q-how-to-add-fragment-synchronously-asynchronously--android--medium
created: 2025-10-15
updated: 2025-11-10
tags:
- android/ui-views
- difficulty/hard

---

# Вопрос (RU)

> Как в runtime делать динамические экраны которые не были предусмотрены

## Ответ (RU)

Для создания действительно динамических экранов во время выполнения в Android обычно:
- Загружают конфигурацию с бэкенда (JSON/XML/Proto)
- Мапят её в локальную модель
- Используют фабрики (Fragments/Views/Composables) для построения UI из описания
- Используют контейнеры вроде RecyclerView с разными ViewType или Jetpack Compose

Ниже представлены основные подходы.

### 1. Server-Driven UI с JSON-конфигурацией

```kotlin
// Модели, совместимые с JSON
data class ScreenConfig(
    val type: String?,
    val title: String?,
    val components: List<Component>
)

data class Component(
    val type: String,
    val properties: Map<String, Any?>
)

// Билдер динамических экранов на базе View
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
                text = component.properties["text"] as? String ?: ""
                val size = (component.properties["size"] as? Number)?.toFloat()
                textSize = size ?: 14f
            }

            "button" -> Button(context).apply {
                text = component.properties["text"] as? String ?: "Button"
                setOnClickListener {
                    // Обработка динамического действия (navigate / analytics и т.п.)
                }
            }

            "image" -> ImageView(context).apply {
                val url = component.properties["url"] as? String
                // Загрузка изображения через Coil/Glide
            }

            else -> TextView(context).apply { text = "Unknown component: ${component.type}" }
        }
    }
}
```

Важные моменты:
- Использовать Moshi/Gson/kotlinx.serialization вместо ручных кастов.
- Валидировать конфигурацию перед рендерингом, чтобы избежать падений.

### 2. Jetpack Compose для динамического UI

```kotlin
@Composable
fun DynamicScreen(config: ScreenConfig) {
    Column(modifier = Modifier
        .fillMaxSize()
        .padding(16.dp)) {
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
            fontSize = ((component.properties["size"] as? Number)?.toInt() ?: 14).sp
        )

        "button" -> Button(onClick = {
            // Обработка динамического действия (например, по properties["action"])
        }) {
            Text(component.properties["text"] as? String ?: "Button")
        }

        "image" -> AsyncImage(
            model = component.properties["url"] as? String,
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

### 3. RecyclerView с несколькими ViewType

```kotlin
class DynamicAdapter(
    private val components: List<Component>
) : RecyclerView.Adapter<RecyclerView.ViewHolder>() {

    companion object {
        private const val TYPE_TEXT = 0
        private const val TYPE_BUTTON = 1
        private const val TYPE_IMAGE = 2
        private const val TYPE_INPUT = 3
    }

    override fun getItemViewType(position: Int): Int = when (components[position].type) {
        "text" -> TYPE_TEXT
        "button" -> TYPE_BUTTON
        "image" -> TYPE_IMAGE
        "input" -> TYPE_INPUT
        else -> TYPE_TEXT
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        val context = parent.context
        return when (viewType) {
            TYPE_TEXT -> TextViewHolder(
                TextView(context).apply {
                    layoutParams = ViewGroup.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                    )
                    setPadding(dpToPx(context, 16), dpToPx(context, 8), dpToPx(context, 16), dpToPx(context, 8))
                }
            )

            TYPE_BUTTON -> ButtonViewHolder(
                Button(context).apply {
                    layoutParams = ViewGroup.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                    )
                }
            )

            TYPE_IMAGE -> ImageViewHolder(
                ImageView(context).apply {
                    layoutParams = ViewGroup.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        dpToPx(context, 200)
                    )
                    scaleType = ImageView.ScaleType.CENTER_CROP
                }
            )

            TYPE_INPUT -> InputViewHolder(
                EditText(context).apply {
                    layoutParams = ViewGroup.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                    )
                }
            )

            else -> TextViewHolder(TextView(context))
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

    override fun getItemCount(): Int = components.size

    class TextViewHolder(private val textView: TextView) : RecyclerView.ViewHolder(textView) {
        fun bind(component: Component) {
            textView.text = component.properties["text"] as? String ?: ""
        }
    }

    class ButtonViewHolder(private val button: Button) : RecyclerView.ViewHolder(button) {
        fun bind(component: Component) {
            button.text = component.properties["text"] as? String ?: "Button"
            // Опционально: привязка динамических действий
        }
    }

    class ImageViewHolder(private val imageView: ImageView) : RecyclerView.ViewHolder(imageView) {
        fun bind(component: Component) {
            val url = component.properties["url"] as? String
            // Загрузка через Coil/Glide
        }
    }

    class InputViewHolder(private val editText: EditText) : RecyclerView.ViewHolder(editText) {
        fun bind(component: Component) {
            editText.hint = component.properties["hint"] as? String ?: ""
        }
    }
}

private fun dpToPx(context: Context, dp: Int): Int =
    (dp * context.resources.displayMetrics.density).toInt()
```

### 4. Паттерн FragmentFactory

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

// Важно: установить factory ДО создания/восстановления фрагментов
class HostActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        supportFragmentManager.fragmentFactory = DynamicFragmentFactory(serverConfig)
        super.onCreate(savedInstanceState)
        // setContentView(...)
    }
}
```

### 5. DSL для построения UI

```kotlin
class UiBuilder(private val context: Context) {

    fun build(block: UiScope.() -> Unit): View {
        val scope = UiScope(context)
        scope.block()
        return scope.root
    }
}

class UiScope(private val context: Context) {
    val root: LinearLayout = LinearLayout(context).apply {
        orientation = LinearLayout.VERTICAL
        layoutParams = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
        )
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
            // Загрузка изображения по url
        })
    }
}

// Использование
val view = UiBuilder(context).build {
    text("Динамический заголовок", 20f)
    button("Нажми меня") {
        // Обработка клика
    }
    image("https://example.com/image.jpg")
}
```

### 6. Пример JSON-ответа от сервера

```json
{
  "screen_id": "home_v2",
  "type": "scroll",
  "title": "Главная",
  "components": [
    {
      "type": "text",
      "properties": {
        "text": "Добро пожаловать",
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
        "text": "Начать",
        "action": "navigate",
        "destination": "signup"
      }
    }
  ]
}
```

### 7. Полный пример с загрузкой из сети

```kotlin
class DynamicScreenActivity : AppCompatActivity() {

    private lateinit var container: LinearLayout

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        container = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
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

    private suspend fun fetchScreenConfig(): ScreenConfig =
        withContext(Dispatchers.IO) {
            // Вызов API и парсинг JSON в ScreenConfig
            ScreenConfig(
                type = "scroll",
                title = "Dynamic",
                components = emptyList()
            )
        }

    private fun buildDynamicUI(config: ScreenConfig) {
        DynamicScreenBuilder().buildScreen(config, container)
    }

    private fun showError(e: Throwable) {
        // Показ fallback-экрана или сообщения об ошибке
    }
}
```

### Преимущества динамических экранов

1. Гибкость — изменение UI без обновления приложения
2. A/B-тесты — разные варианты экранов для разных сегментов
3. Быстрые эксперименты — выкладка новых сценариев без релиза
4. Персонализация — адаптация под пользователя или регион
5. Быстрое исправление проблемных экранов через конфигурацию

### Недостатки

1. Сложность — требуется инфраструктура и протоколы на сервере и клиенте
2. Производительность — парсинг и создание UI в runtime
3. Ограничения — не все фичи и компоненты удобно делать конфигурируемыми
4. Тестирование — больше состояний и конфигураций
5. Зависимость от сети — нужна стратегия кэширования и fallback

### Best Practices

1. Кэшировать последнюю валидную конфигурацию локально
2. Версионировать схемы и API конфигурации
3. Делать fallback-экраны и поведение по умолчанию
4. Валидировать конфиг перед применением, логировать ошибки
5. Повышать типобезопасность (sealed-классы/enum для типов компонентов)

### Использование в продакшене

Многие крупные приложения используют server-driven UI / динамический UI-подход:
- Airbnb — Epoxy для динамических списков
- Facebook — ComponentKit/Litho для компонентного UI
- Uber — RIBs для модульной динамической навигации
- Instagram — IGListKit для сложных списков
- Netflix — конфигурационные системы для витрин

# Question (EN)

> How To Create Dynamic Screens At Runtime

## Answer (EN)

To create truly dynamic screens at runtime in Android you typically:
- Load configuration from a backend (JSON/XML/Proto)
- `Map` this configuration to a local model
- Use factories (Fragments/Views/Composables) to render UI from that model
- Use containers such as RecyclerView (multiple view types) or Jetpack Compose

Below are core implementation patterns.

### 1. Server-Driven UI with JSON

```kotlin
// JSON-mapped models (keep them JSON-friendly)
data class ScreenConfig(
    val type: String?,
    val title: String?,
    val components: List<Component>
)

data class Component(
    val type: String,
    val properties: Map<String, Any?>
)

// Dynamic screen builder for classic Views
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
                text = component.properties["text"] as? String ?: ""
                // Be careful with numeric types from JSON (may arrive as Int/Double)
                val size = (component.properties["size"] as? Number)?.toFloat()
                textSize = size ?: 14f
            }

            "button" -> Button(context).apply {
                text = component.properties["text"] as? String ?: "Button"
                setOnClickListener {
                    // Handle dynamic action based on properties (e.g., navigate / analytics)
                }
            }

            "image" -> ImageView(context).apply {
                val url = component.properties["url"] as? String
                // Load image with Coil/Glide using 'url'
            }

            else -> TextView(context).apply { text = "Unknown component: ${component.type}" }
        }
    }
}
```

Key considerations:
- `Map` JSON via a real JSON library (Moshi/Gson/Kotlinx Serialization) to avoid unsafe casts.
- Validate config before rendering to avoid crashes.

### 2. Jetpack Compose Dynamic UI

```kotlin
@Composable
fun DynamicScreen(config: ScreenConfig) {
    Column(modifier = Modifier
        .fillMaxSize()
        .padding(16.dp)) {
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
            fontSize = ((component.properties["size"] as? Number)?.toInt() ?: 14).sp
        )

        "button" -> Button(onClick = {
            // Handle dynamic action (e.g., use properties["action"])
        }) {
            Text(component.properties["text"] as? String ?: "Button")
        }

        "image" -> AsyncImage(
            model = component.properties["url"] as? String,
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
        private const val TYPE_TEXT = 0
        private const val TYPE_BUTTON = 1
        private const val TYPE_IMAGE = 2
        private const val TYPE_INPUT = 3
    }

    override fun getItemViewType(position: Int): Int = when (components[position].type) {
        "text" -> TYPE_TEXT
        "button" -> TYPE_BUTTON
        "image" -> TYPE_IMAGE
        "input" -> TYPE_INPUT
        else -> TYPE_TEXT
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        val context = parent.context
        return when (viewType) {
            TYPE_TEXT -> TextViewHolder(
                TextView(context).apply {
                    layoutParams = ViewGroup.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                    )
                    setPadding(dpToPx(context, 16), dpToPx(context, 8), dpToPx(context, 16), dpToPx(context, 8))
                }
            )

            TYPE_BUTTON -> ButtonViewHolder(
                Button(context).apply {
                    layoutParams = ViewGroup.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                    )
                }
            )

            TYPE_IMAGE -> ImageViewHolder(
                ImageView(context).apply {
                    layoutParams = ViewGroup.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        dpToPx(context, 200)
                    )
                    scaleType = ImageView.ScaleType.CENTER_CROP
                }
            )

            TYPE_INPUT -> InputViewHolder(
                EditText(context).apply {
                    layoutParams = ViewGroup.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                    )
                }
            )

            else -> TextViewHolder(TextView(context))
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

    override fun getItemCount(): Int = components.size

    class TextViewHolder(private val textView: TextView) : RecyclerView.ViewHolder(textView) {
        fun bind(component: Component) {
            textView.text = component.properties["text"] as? String ?: ""
        }
    }

    class ButtonViewHolder(private val button: Button) : RecyclerView.ViewHolder(button) {
        fun bind(component: Component) {
            button.text = component.properties["text"] as? String ?: "Button"
            // Optionally wire dynamic actions here
        }
    }

    class ImageViewHolder(private val imageView: ImageView) : RecyclerView.ViewHolder(imageView) {
        fun bind(component: Component) {
            val url = component.properties["url"] as? String
            // Load with Coil/Glide using 'url'
        }
    }

    class InputViewHolder(private val editText: EditText) : RecyclerView.ViewHolder(editText) {
        fun bind(component: Component) {
            editText.hint = component.properties["hint"] as? String ?: ""
        }
    }
}

private fun dpToPx(context: Context, dp: Int): Int =
    (dp * context.resources.displayMetrics.density).toInt()
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

// Usage: set factory BEFORE any fragments are inflated/restored
class HostActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        supportFragmentManager.fragmentFactory = DynamicFragmentFactory(serverConfig)
        super.onCreate(savedInstanceState)
        // setContentView(...)
    }
}
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
    val root: LinearLayout = LinearLayout(context).apply {
        orientation = LinearLayout.VERTICAL
        layoutParams = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
        )
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
            // Load image from 'url' with an image loader
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
            layoutParams = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
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

    private suspend fun fetchScreenConfig(): ScreenConfig =
        withContext(Dispatchers.IO) {
            // TODO: real API call that parses JSON into ScreenConfig
            ScreenConfig(
                type = "scroll",
                title = "Dynamic",
                components = emptyList()
            )
        }

    private fun buildDynamicUI(config: ScreenConfig) {
        DynamicScreenBuilder().buildScreen(config, container)
    }

    private fun showError(e: Throwable) {
        // Show fallback UI or error state
    }
}
```

### Advantages of dynamic screens

1. Flexibility — change UI without updating the app
2. A/B testing — different variants for different user segments
3. Fast experiments — roll out new flows without releases
4. Personalization — adapt UI to user or region
5. Rapid fixes — adjust problematic screens via configuration

### Disadvantages of dynamic screens

1. Complexity — requires infrastructure and protocols on both server and client
2. Performance — parsing and building UI at runtime
3. Limitations — not all features/components are easy to make configurable
4. Testing — many more states and configurations to cover
5. Network dependency — must have caching and fallback strategies

### Best Practices

1. Cache the last valid configuration locally
2. Version configuration schemas and APIs
3. Provide fallback screens and default behavior
4. Validate configuration before applying, log errors
5. Increase type safety (sealed classes/enums for component types)

### Production usage

Many large apps use server-driven / dynamic UI approaches:
- Airbnb — Epoxy for dynamic lists
- Facebook — ComponentKit/Litho for component-based UI
- Uber — RIBs for modular dynamic navigation
- Instagram — IGListKit for complex lists
- Netflix — configuration-driven merchandising/landing layouts

## Follow-ups

- [[q-fragments-history-and-purpose--android--hard]]
- [[q-how-is-navigation-implemented--android--medium]]
- [[q-how-to-add-fragment-synchronously-asynchronously--android--medium]]

## References

- https://developer.android.com/develop/ui/views
- https://developer.android.com/docs

## Related Questions

### Prerequisites / Concepts

- [[c-android-components]]

- [[q-fragments-history-and-purpose--android--hard]]
- [[q-how-to-add-fragment-synchronously-asynchronously--android--medium]]
- [[q-how-is-navigation-implemented--android--medium]]
