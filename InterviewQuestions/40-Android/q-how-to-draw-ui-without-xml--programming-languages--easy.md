---
id: 20251012-1227182
title: "How To Draw Ui Without Xml / Как рисовать UI без XML"
topic: android
difficulty: easy
status: draft
created: 2025-10-15
tags: [languages, android, difficulty/easy]
---
# Как рисовать UI без xml?

## Answer (EN)
In Android, you can create UI without XML using **Jetpack Compose** (modern, declarative approach) or **programmatic View creation** (traditional approach).

### 1. Jetpack Compose (Recommended)

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            MaterialTheme {
                MainScreen()
            }
        }
    }
}

@Composable
fun MainScreen() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Hello, Compose!",
            style = MaterialTheme.typography.headlineMedium
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(onClick = { /* action */ }) {
            Text("Click Me")
        }
    }
}
```

### 2. Programmatic View Creation

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Create layout programmatically
        val linearLayout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.MATCH_PARENT
            )
            setPadding(16.dp, 16.dp, 16.dp, 16.dp)
            gravity = Gravity.CENTER
        }

        // Add TextView
        val textView = TextView(this).apply {
            text = "Hello, Android!"
            textSize = 24f
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
        }

        // Add Button
        val button = Button(this).apply {
            text = "Click Me"
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                topMargin = 16.dp
            }
            setOnClickListener {
                Toast.makeText(context, "Button clicked!", Toast.LENGTH_SHORT).show()
            }
        }

        // Add views to layout
        linearLayout.addView(textView)
        linearLayout.addView(button)

        // Set as content view
        setContentView(linearLayout)
    }

    private val Int.dp: Int
        get() = (this * resources.displayMetrics.density).toInt()
}
```

### 3. Complex Layout Example (Programmatic)

```kotlin
class ProgrammaticLayoutActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val rootLayout = createRootLayout()
        setContentView(rootLayout)
    }

    private fun createRootLayout(): View {
        return LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.MATCH_PARENT
            )

            // Add header
            addView(createHeader())

            // Add content
            addView(createContent())

            // Add footer
            addView(createFooter())
        }
    }

    private fun createHeader(): View {
        return TextView(this).apply {
            text = "Header"
            textSize = 20f
            gravity = Gravity.CENTER
            setBackgroundColor(Color.LTGRAY)
            setPadding(16.dp, 16.dp, 16.dp, 16.dp)
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
        }
    }

    private fun createContent(): View {
        return ScrollView(this).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                0,
                1f // weight
            )

            addView(LinearLayout(context).apply {
                orientation = LinearLayout.VERTICAL

                repeat(20) { index ->
                    addView(TextView(context).apply {
                        text = "Item $index"
                        setPadding(16.dp, 8.dp, 16.dp, 8.dp)
                    })
                }
            })
        }
    }

    private fun createFooter(): View {
        return Button(this).apply {
            text = "Action"
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                setMargins(16.dp, 8.dp, 16.dp, 16.dp)
            }
        }
    }

    private val Int.dp: Int
        get() = (this * resources.displayMetrics.density).toInt()
}
```

### 4. Compose vs Programmatic Views

| Aspect | Jetpack Compose | Programmatic Views |
|--------|-----------------|-------------------|
| Syntax | Declarative | Imperative |
| Code | Cleaner, less verbose | More boilerplate |
| State | Automatic updates | Manual updates |
| Preview | Built-in | Requires running app |
| Modern | Yes | Legacy approach |

### 5. Hybrid Approach - Compose in View

```kotlin
class HybridActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val rootLayout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
        }

        // Add traditional View
        rootLayout.addView(TextView(this).apply {
            text = "Traditional View"
        })

        // Add Compose View
        val composeView = ComposeView(this).apply {
            setContent {
                MaterialTheme {
                    Text("Compose View", modifier = Modifier.padding(16.dp))
                }
            }
        }
        rootLayout.addView(composeView)

        setContentView(rootLayout)
    }
}
```

---

# Как рисовать UI без xml

## Ответ (RU)
В Android можно создавать интерфейс без XML с помощью Jetpack Compose или программного кода (View в Kotlin/Java).

---

## Related Questions

### Related (Easy)
- [[q-why-separate-ui-and-business-logic--android--easy]] - Ui
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - Ui
- [[q-recyclerview-sethasfixedsize--android--easy]] - Ui

### Advanced (Harder)
- [[q-dagger-build-time-optimization--android--medium]] - Ui
- [[q-rxjava-pagination-recyclerview--android--medium]] - Ui
- [[q-build-optimization-gradle--gradle--medium]] - Ui
