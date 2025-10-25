---
id: 20251012-122711183
title: "Where Is Composition Created For Calling Composable Function / Где создается Composition для вызова Composable функции"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-what-is-layout-types-and-when-to-use--android--easy, q-background-tasks-decision-guide--android--medium, q-okhttp-interceptors-advanced--networking--medium]
created: 2025-10-15
tags: [setContent, android, ui, jetpack-compose, difficulty/medium]
---

# Where is composition created for calling composable function?

# Вопрос (RU)

Где создается композиция для вызова composable функции

## Answer (EN)
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

## Ответ (RU)

Композиция создается внутри функции **setContent**, которая задает точку входа для composable функций в Activity или Fragment. Она инициирует рендеринг интерфейса и управление состоянием.

### Где создается композиция

**1. В Activity через setContent:**

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Композиция создается здесь
        setContent {
            MyApp() // Точка входа в Compose UI
        }
    }
}
```

**2. Во Fragment через ComposeView:**

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // Композиция создается в ComposeView
        return ComposeView(requireContext()).apply {
            setContent {
                MyComposable()
            }
        }
    }
}
```

**3. В обычной View через ComposeView:**

```kotlin
class MyCustomView(context: Context) : LinearLayout(context) {
    init {
        addView(ComposeView(context).apply {
            setContent {
                Text("Compose inside custom View")
            }
        })
    }
}
```

### Жизненный цикл композиции

```kotlin
@Composable
fun CompositionLifecycle() {
    // Входит в композицию при вызове setContent
    DisposableEffect(Unit) {
        println("Entered composition")

        onDispose {
            println("Left composition")
        }
    }

    Text("Hello")
}
```

### Множественные композиции

Каждый вызов `setContent` создает отдельную независимую композицию:

```kotlin
class MultiCompositionActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this)

        // Первая композиция
        layout.addView(ComposeView(this).apply {
            setContent { Text("First") }
        })

        // Вторая композиция (независимая)
        layout.addView(ComposeView(this).apply {
            setContent { Text("Second") }
        })

        setContentView(layout)
    }
}
```

### Резюме

Композиция создается в точке вызова `setContent` внутри Activity (`ComponentActivity.setContent()`) или при создании `ComposeView` во Fragment/View. Это корневая точка входа, которая запускает механизм Compose для построения UI дерева, отслеживания состояния и управления рекомпозициями. Каждый `setContent` создает отдельную изолированную композицию

---

## Related Questions

### Related (Medium)
- [[q-how-does-jetpackcompose-work--android--medium]] - Compose
- [[q-compose-modifier-order-performance--android--medium]] - Compose
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Compose
- [[q-compositionlocal-advanced--android--medium]] - Compose
- [[q-accessibility-compose--android--medium]] - Compose

### Advanced (Harder)
- [[q-compose-stability-skippability--android--hard]] - Compose
- [[q-compose-custom-layout--android--hard]] - Compose
- [[q-compose-performance-optimization--android--hard]] - Compose
