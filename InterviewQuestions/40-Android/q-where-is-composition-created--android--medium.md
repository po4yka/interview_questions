---
id: android-284
title: "Where Is Composition Created / Где создается Composition"
aliases: [ComposeView, Composition Creation, setContent, Создание Composition]
topic: android
subtopics: [lifecycle, ui-compose, ui-views]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, q-is-layoutinflater-a-singleton-and-why--android--medium, q-network-error-handling-strategies--networking--medium]
created: 2025-10-15
updated: 2025-10-27
sources: []
tags: [android/lifecycle, android/ui-compose, android/ui-views, composition, difficulty/medium, jetpack-compose]
---

# Вопрос (RU)

Где создается композиция для вызова composable функций?

# Question (EN)

Where is composition created for calling composable functions?

---

## Ответ (RU)

**Композиция** создается при вызове **setContent** в `Activity` (или ComposeView во `Fragment`). Это точка входа для Compose UI.

### setContent В `Activity`

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

### ComposeView Во `Fragment`

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

**Composition** is created when **setContent** is called in `Activity` (or when ComposeView is created in `Fragment`). It's the entry point for Compose UI.

### setContent in `Activity`

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

### ComposeView in `Fragment`

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


## Follow-ups

- [[c-jetpack-compose]]
- [[q-is-layoutinflater-a-singleton-and-why--android--medium]]
- [[q-network-error-handling-strategies--networking--medium]]


## References

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)
- [`Lifecycle`](https://developer.android.com/topic/libraries/architecture/lifecycle)
- [Jetpack Compose](https://developer.android.com/develop/ui/compose)


## Related Questions

- [[q-is-layoutinflater-a-singleton-and-why--android--medium]]
- [[q-network-error-handling-strategies--networking--medium]]
- [[c-jetpack-compose]]
