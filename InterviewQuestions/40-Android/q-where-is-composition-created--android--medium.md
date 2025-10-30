---
id: 20251012-122711
title: "Where Is Composition Created / Где создается Composition"
aliases: [Composition Creation, Создание Composition, setContent, ComposeView]
topic: android
subtopics: [ui-compose, lifecycle, ui-views]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-is-layoutinflater-a-singleton-and-why--android--medium, q-network-error-handling-strategies--networking--medium, c-jetpack-compose]
created: 2025-10-15
updated: 2025-10-27
sources: []
tags: [android/ui-compose, android/lifecycle, android/ui-views, jetpack-compose, composition, difficulty/medium]
date created: Monday, October 27th 2025, 6:53:26 pm
date modified: Thursday, October 30th 2025, 3:18:07 pm
---

# Вопрос (RU)

Где создается композиция для вызова composable функций?

# Question (EN)

Where is composition created for calling composable functions?

---

## Ответ (RU)

**Композиция** создается при вызове **setContent** в Activity (или ComposeView во Fragment). Это точка входа для Compose UI.

### setContent в Activity

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ✅ Здесь создается Composition
        setContent {
            MyApp()
        }
    }
}

@Composable
fun MyApp() {
    MaterialTheme {
        Surface { MainScreen() }
    }
}
```

### ComposeView во Fragment

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // ✅ Composition создается в ComposeView
        return ComposeView(requireContext()).apply {
            setContent { MyComposable() }
        }
    }
}
```

### Несколько Compositions

```kotlin
// ✅ Каждый ComposeView = отдельная Composition
val layout = LinearLayout(this).apply {
    addView(ComposeView(this).apply {
        setContent { Text("First") } // Composition 1
    })
    addView(ComposeView(this).apply {
        setContent { Text("Second") } // Composition 2
    })
}
```

**Резюме**: Каждый вызов `setContent` или создание `ComposeView` запускает новую композицию с собственным lifecycle.

## Answer (EN)

**Composition** is created when **setContent** is called in Activity (or when ComposeView is created in Fragment). It's the entry point for Compose UI.

### setContent in Activity

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

@Composable
fun MyApp() {
    MaterialTheme {
        Surface { MainScreen() }
    }
}
```

### ComposeView in Fragment

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // ✅ Composition created in ComposeView
        return ComposeView(requireContext()).apply {
            setContent { MyComposable() }
        }
    }
}
```

### Multiple Compositions

```kotlin
// ✅ Each ComposeView = separate Composition
val layout = LinearLayout(this).apply {
    addView(ComposeView(this).apply {
        setContent { Text("First") } // Composition 1
    })
    addView(ComposeView(this).apply {
        setContent { Text("Second") } // Composition 2
    })
}
```

**Summary**: Every `setContent` call or `ComposeView` creation starts a new composition with its own lifecycle.

---

## Related Questions

- [[q-is-layoutinflater-a-singleton-and-why--android--medium]]
- [[q-network-error-handling-strategies--networking--medium]]
- [[c-jetpack-compose]]
