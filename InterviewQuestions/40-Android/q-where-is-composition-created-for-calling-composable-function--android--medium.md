---
id: android-410
title: "Where Is Composition Created For Calling Composable Function / Где создается Composition для вызова Composable функции"
aliases: ["Where Is Composition Created", "Где создается Composition"]
topic: android
subtopics: [ui-compose, lifecycle]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, q-how-does-jetpackcompose-work--android--medium, q-compositionlocal-advanced--android--medium]
created: 2025-10-15
updated: 2025-10-29
sources: []
tags: [android/ui-compose, android/lifecycle, setContent, jetpack-compose, difficulty/medium]
date created: Wednesday, October 29th 2025, 12:15:40 pm
date modified: Thursday, October 30th 2025, 3:18:07 pm
---

# Вопрос (RU)

> Где создается Composition для вызова composable функции?

# Question (EN)

> Where is the Composition created when calling a composable function?

---

## Ответ (RU)

**Композиция создается в точке вызова `setContent`** — это корневая точка входа в Compose UI, которая инициирует построение UI-дерева и управление состоянием.

### Основные места создания

**1. В Activity через ComponentActivity.setContent():**

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ✅ Композиция создается здесь
        setContent {
            MyApp()
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
        // ✅ Композиция создается при setContent на ComposeView
        return ComposeView(requireContext()).apply {
            setContent { MyComposable() }
        }
    }
}
```

**3. В обычной View через ComposeView:**

```kotlin
class MyCustomView(context: Context) : LinearLayout(context) {
    init {
        // ✅ Каждый ComposeView создает отдельную композицию
        addView(ComposeView(context).apply {
            setContent { Text("Compose inside View") }
        })
    }
}
```

### Множественные композиции

Каждый вызов `setContent` создает **отдельную независимую композицию**:

```kotlin
val layout = LinearLayout(context)

// ❌ Две композиции не видят состояние друг друга
layout.addView(ComposeView(context).apply {
    setContent { Text("First composition") }  // Композиция #1
})

layout.addView(ComposeView(context).apply {
    setContent { Text("Second composition") } // Композиция #2
})
```

### Жизненный цикл композиции

```kotlin
@Composable
fun CompositionLifecycle() {
    // Входит в композицию при setContent
    DisposableEffect(Unit) {
        println("Entered composition")

        onDispose {
            // Выходит при уничтожении Activity/Fragment
            println("Left composition")
        }
    }
}
```

**Резюме**: Композиция = корневой узел Compose UI, создается в `setContent` или `ComposeView`, привязана к жизненному циклу Activity/Fragment.

## Answer (EN)

**Composition is created at the point of calling `setContent`** — this is the root entry point into Compose UI that initiates UI tree building and state management.

### Primary Creation Points

**1. In Activity via ComponentActivity.setContent():**

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ✅ Composition created here
        setContent {
            MyApp()
        }
    }
}
```

**2. In Fragment via ComposeView:**

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // ✅ Composition created when setContent is called on ComposeView
        return ComposeView(requireContext()).apply {
            setContent { MyComposable() }
        }
    }
}
```

**3. In custom View via ComposeView:**

```kotlin
class MyCustomView(context: Context) : LinearLayout(context) {
    init {
        // ✅ Each ComposeView creates a separate composition
        addView(ComposeView(context).apply {
            setContent { Text("Compose inside View") }
        })
    }
}
```

### Multiple Compositions

Each `setContent` call creates a **separate independent composition**:

```kotlin
val layout = LinearLayout(context)

// ❌ Two compositions don't share state
layout.addView(ComposeView(context).apply {
    setContent { Text("First composition") }  // Composition #1
})

layout.addView(ComposeView(context).apply {
    setContent { Text("Second composition") } // Composition #2
})
```

### Composition Lifecycle

```kotlin
@Composable
fun CompositionLifecycle() {
    // Enters composition when setContent is called
    DisposableEffect(Unit) {
        println("Entered composition")

        onDispose {
            // Leaves when Activity/Fragment is destroyed
            println("Left composition")
        }
    }
}
```

**Summary**: Composition = root Compose UI node, created in `setContent` or `ComposeView`, tied to Activity/Fragment lifecycle.

---

## Follow-ups

- What happens to composition when configuration changes occur?
- How do multiple compositions communicate with each other?
- Can you create a composition programmatically without setContent?
- What is the difference between Composition and CompositionLocal?
- How does composition disposal affect ongoing coroutines?

## References

- [[c-jetpack-compose]] - Core Jetpack Compose concepts
- [Compose Lifecycle](https://developer.android.com/jetpack/compose/lifecycle)
- [Understanding Composition](https://developer.android.com/jetpack/compose/mental-model)
- [Thinking in Compose](https://developer.android.com/jetpack/compose/mental-model)

## Related Questions

### Prerequisites (Easier)
- [[q-what-are-the-most-important-components-of-compose--android--medium]]

### Related (Same Level)
- [[q-how-does-jetpackcompose-work--android--medium]]
- [[q-compositionlocal-advanced--android--medium]]
- [[q-compose-modifier-order-performance--android--medium]]

### Advanced (Harder)
- [[q-compose-stability-skippability--android--hard]]
- [[q-compose-custom-layout--android--hard]]
- [[q-compose-performance-optimization--android--hard]]
