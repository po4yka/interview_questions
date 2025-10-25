---
id: 20251012-122711182
title: "Where Is Composition Created / Где создается Composition"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-is-layoutinflater-a-singleton-and-why--android--medium, q-canvas-drawing-optimization--custom-views--hard, q-network-error-handling-strategies--networking--medium]
created: 2025-10-15
tags: [jetpack-compose, compose, composition, difficulty/medium]
---

# Where is composition created for calling composable functions?

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

---

# Где создается композиция для вызова composable функции

## Ответ (RU)

Композиция создается внутри функции **setContent**, которая задает точку входа для composable функций в Activity или Fragment. Она инициирует рендеринг интерфейса и управление состоянием.

### setContent в Activity

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

@Composable
fun MyApp() {
    MaterialTheme {
        Surface {
            MainScreen()
        }
    }
}
```

### setContent во Fragment

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

### Несколько композиций

```kotlin
class MultiCompositionActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
        }

        // Первая композиция
        layout.addView(ComposeView(this).apply {
            setContent {
                Text("First Composition")
            }
        })

        // Вторая композиция (отдельная)
        layout.addView(ComposeView(this).apply {
            setContent {
                Text("Second Composition")
            }
        })

        setContentView(layout)
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

### Резюме

Композиция создается при вызове `setContent` в Activity или при создании `ComposeView` во Fragment. Это точка входа, которая запускает механизм Compose для отрисовки UI и отслеживания состояния. Каждый `setContent` или `ComposeView` создает отдельную композицию с собственным жизненным циклом

## Related Questions

- [[q-is-layoutinflater-a-singleton-and-why--android--medium]]
- [[q-canvas-drawing-optimization--android--hard]]
- [[q-network-error-handling-strategies--networking--medium]]
