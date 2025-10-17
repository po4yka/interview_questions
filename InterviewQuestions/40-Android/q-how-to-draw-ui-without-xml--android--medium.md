---
id: "20251015082237404"
title: "How To Draw Ui Without Xml / Как рисовать UI без XML"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - android
---
# How to draw UI without XML?

## EN (expanded)

In Android, you can create UI without XML using two main approaches:

1. **Jetpack Compose** (Modern, Declarative)
2. **Programmatic Views** (Traditional, Imperative)

### 1. Jetpack Compose (Recommended)

Compose is the modern, declarative UI toolkit that replaces XML entirely:

#### Basic Example

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MyApp()
        }
    }
}

@Composable
fun MyApp() {
    MaterialTheme {
        Surface(
            modifier = Modifier.fillMaxSize(),
            color = MaterialTheme.colorScheme.background
        ) {
            Greeting("Android")
        }
    }
}

@Composable
fun Greeting(name: String) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Hello $name!",
            style = MaterialTheme.typography.headlineMedium
        )
        Spacer(modifier = Modifier.height(16.dp))
        Button(onClick = { /* action */ }) {
            Text("Click Me")
        }
    }
}
```

#### Complex Layout Example

```kotlin
@Composable
fun ProfileScreen(user: User) {
    Column(modifier = Modifier.fillMaxSize()) {
        // Header
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(200.dp)
                .background(MaterialTheme.colorScheme.primary)
        ) {
            Column(
                modifier = Modifier
                    .align(Alignment.Center)
                    .padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Image(
                    painter = rememberImagePainter(user.avatarUrl),
                    contentDescription = "Avatar",
                    modifier = Modifier
                        .size(80.dp)
                        .clip(CircleShape)
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = user.name,
                    style = MaterialTheme.typography.headlineSmall,
                    color = Color.White
                )
            }
        }

        // Content
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(16.dp)
        ) {
            item {
                Text(
                    text = "About",
                    style = MaterialTheme.typography.titleLarge
                )
            }
            item {
                Text(
                    text = user.bio,
                    style = MaterialTheme.typography.bodyMedium
                )
            }
            // More items...
        }
    }
}
```

#### Form Example

```kotlin
@Composable
fun LoginScreen() {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var isPasswordVisible by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Login",
            style = MaterialTheme.typography.headlineLarge
        )

        Spacer(modifier = Modifier.height(32.dp))

        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email") },
            modifier = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(
                keyboardType = KeyboardType.Email
            )
        )

        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password") },
            modifier = Modifier.fillMaxWidth(),
            visualTransformation = if (isPasswordVisible) {
                VisualTransformation.None
            } else {
                PasswordVisualTransformation()
            },
            trailingIcon = {
                IconButton(onClick = { isPasswordVisible = !isPasswordVisible }) {
                    Icon(
                        imageVector = if (isPasswordVisible) {
                            Icons.Default.Visibility
                        } else {
                            Icons.Default.VisibilityOff
                        },
                        contentDescription = "Toggle password visibility"
                    )
                }
            }
        )

        Spacer(modifier = Modifier.height(24.dp))

        Button(
            onClick = { /* login */ },
            modifier = Modifier.fillMaxWidth(),
            enabled = email.isNotEmpty() && password.isNotEmpty()
        ) {
            Text("Login")
        }
    }
}
```

### 2. Programmatic Views (Traditional)

You can also create views programmatically in Kotlin/Java:

#### Basic Example

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.MATCH_PARENT
            )
            setPadding(16.dp, 16.dp, 16.dp, 16.dp)
        }

        val textView = TextView(this).apply {
            text = "Hello Android!"
            textSize = 24f
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
        }

        val button = Button(this).apply {
            text = "Click Me"
            setOnClickListener {
                Toast.makeText(context, "Clicked!", Toast.LENGTH_SHORT).show()
            }
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                topMargin = 16.dp
            }
        }

        layout.addView(textView)
        layout.addView(button)

        setContentView(layout)
    }

    private val Int.dp: Int
        get() = (this * resources.displayMetrics.density).toInt()
}
```

#### Complex Layout Example

```kotlin
class ProgrammaticActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val rootLayout = FrameLayout(this).apply {
            layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
            )
        }

        // Background image
        val backgroundImage = ImageView(this).apply {
            setImageResource(R.drawable.background)
            scaleType = ImageView.ScaleType.CENTER_CROP
            layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
            )
        }

        // Content container
        val contentLayout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(32.dp, 32.dp, 32.dp, 32.dp)
            layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
            )
        }

        val titleText = TextView(this).apply {
            text = "Welcome"
            textSize = 32f
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
        }

        val subtitleText = TextView(this).apply {
            text = "Get started with our app"
            textSize = 16f
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                topMargin = 8.dp
            }
        }

        val startButton = Button(this).apply {
            text = "Get Started"
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                topMargin = 32.dp
            }
            setOnClickListener {
                // Navigate to next screen
            }
        }

        contentLayout.addView(titleText)
        contentLayout.addView(subtitleText)
        contentLayout.addView(startButton)

        rootLayout.addView(backgroundImage)
        rootLayout.addView(contentLayout)

        setContentView(rootLayout)
    }

    private val Int.dp: Int
        get() = (this * resources.displayMetrics.density).toInt()
}
```

#### RecyclerView Programmatically

```kotlin
class ListActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val recyclerView = RecyclerView(this).apply {
            layoutManager = LinearLayoutManager(this@ListActivity)
            adapter = MyAdapter(getItems())
            layoutParams = RecyclerView.LayoutParams(
                RecyclerView.LayoutParams.MATCH_PARENT,
                RecyclerView.LayoutParams.MATCH_PARENT
            )
        }

        setContentView(recyclerView)
    }

    private fun getItems(): List<String> {
        return (1..50).map { "Item $it" }
    }
}

class MyAdapter(private val items: List<String>) :
    RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    class ViewHolder(val textView: TextView) : RecyclerView.ViewHolder(textView)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val textView = TextView(parent.context).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            )
            setPadding(16.dp, 16.dp, 16.dp, 16.dp)
            textSize = 16f
        }
        return ViewHolder(textView)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.textView.text = items[position]
    }

    override fun getItemCount() = items.size

    private val Int.dp: Int
        get() = (this * holder.itemView.context.resources.displayMetrics.density).toInt()
}
```

### Comparison

| Aspect | Jetpack Compose | Programmatic Views |
|--------|----------------|-------------------|
| **Syntax** | Declarative, concise | Imperative, verbose |
| **State Management** | Built-in, reactive | Manual |
| **Preview** | @Preview support | No preview |
| **Learning Curve** | Moderate | Steep for complex UIs |
| **Code Readability** | High | Low for complex UIs |
| **Recommended** | Yes (modern apps) | No (legacy only) |

### Best Practices

1. **Use Compose for new projects** - It's more maintainable and readable
2. **Keep UI code modular** - Break into small, reusable components
3. **Leverage previews** - Use `@Preview` in Compose for quick iteration
4. **Follow Material Design** - Use Material components for consistency

---

## RU (original)

Как рисовать UI без xml

В Android можно создавать интерфейс без XML с помощью Jetpack Compose или программного кода (View в Kotlin/Java).

---

## Related Questions

### Prerequisites (Easier)
- [[q-why-separate-ui-and-business-logic--android--easy]] - Ui
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - Ui
- [[q-recyclerview-sethasfixedsize--android--easy]] - Ui

### Related (Medium)
- [[q-dagger-build-time-optimization--android--medium]] - Ui
- [[q-rxjava-pagination-recyclerview--android--medium]] - Ui
- [[q-build-optimization-gradle--gradle--medium]] - Ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Ui
- [[q-testing-compose-ui--android--medium]] - Ui
