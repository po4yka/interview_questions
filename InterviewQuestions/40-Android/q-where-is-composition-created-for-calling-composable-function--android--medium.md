---
id: "20251003141632"
title: "Where is composition created for calling composable function"
slug: "where-is-composition-created-for-calling-composable-function"
tags: ["Jetpack Compose", "setContent"]
topic: "android"
subtopics: ["android", "ui", "jetpack-compose"]
moc: "moc-android"
status: "draft"
difficulty: "medium"
question_kind: "theory"
source: "https://t.me/easy_kotlin/1492"
---

# Where is composition created for calling composable function

## Question (RU)

Где создается композиция для вызова composable функции

## Answer

Composition is created inside the **setContent** function, which sets the entry point for composable functions in Activity or Fragment. It initiates interface rendering and state management.

### setContent in Activity

```kotlin
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Composition is created here
        setContent {
            MyApp() // Entry point to Compose UI
        }
    }
}

@Composable
fun MyApp() {
    MaterialTheme {
        Surface {
            MainScreen()
        }
    }
}
```

### setContent in Fragment

```kotlin
class MyFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // Composition created in ComposeView
        return ComposeView(requireContext()).apply {
            setContent {
                MyComposable()
            }
        }
    }
}
```

### Multiple Compositions

```kotlin
class MultiCompositionActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
        }

        // First composition
        layout.addView(ComposeView(this).apply {
            setContent {
                Text("First Composition")
            }
        })

        // Second composition (separate)
        layout.addView(ComposeView(this).apply {
            setContent {
                Text("Second Composition")
            }
        })

        setContentView(layout)
    }
}
```

### Composition Lifecycle

```kotlin
@Composable
fun CompositionLifecycle() {
    // Enters composition when setContent is called
    DisposableEffect(Unit) {
        println("Entered composition")

        onDispose {
            println("Left composition")
        }
    }

    Text("Hello")
}
```

## Answer (RU)

Композиция создаётся внутри функции setContent, которая задает точку входа для composable функций в Activity или Fragment. Она инициирует рендеринг интерфейса и управление состоянием.
