---
id: android-284
title: "Where Is Composition Created"
aliases: [ComposeView, Composition Creation, setContent]
topic: android
subtopics: [ui-compose, ui-views]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-is-layoutinflater-a-singleton-and-why--android--medium, q-network-error-handling-strategies--networking--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android/ui-compose, android/ui-views, difficulty/medium]

---

# Вопрос (RU)

> Где создается композиция для вызова composable функций?

# Question (EN)

> Where is composition created for calling composable functions?

---

## Ответ (RU)

**Композиция** создается и управляется средой Compose, когда вы задаете содержимое через **`setContent`** у `ComponentActivity` / `ComponentDialog` или через `setContent` у `ComposeView` (например, во `Fragment` или обычном `View`). Эти вызовы создают корень композиции и подключают его к жизненному циклу соответствующего владельца.

### setContent в `Activity`

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Здесь создается корневая Composition для этого окна
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

### ComposeView во `Fragment`

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // Composition создается, когда для ComposeView вызывается setContent
        return ComposeView(requireContext()).apply {
            setContent { MyComposable() }
        }
    }
}
```

### Несколько Compositions

```kotlin
// Каждый вызов setContent на отдельном ComposeView создает отдельную Composition
val layout = LinearLayout(this).apply {
    addView(ComposeView(this).apply {
        setContent { Text("First") } // Composition 1
    })
    addView(ComposeView(this).apply {
        setContent { Text("Second") } // Composition 2
    })
}
```

**Резюме**: Каждый отдельный корень, заданный через `setContent` в `ComponentActivity`/`ComposeView`, формирует собственную Composition. Ее жизненный цикл привязан к соответствующему владельцу (`Activity`, `Fragment` или `View`), а сам Compose управляет первоначальной композицией и последующими рекомпозициями.

## Answer (EN)

A **Composition** is created and managed by the Compose runtime when you provide UI content via **`setContent`** on a `ComponentActivity` / `ComponentDialog` or via `setContent` on a `ComposeView` (e.g., inside a `Fragment` or a regular `View`). These calls create a composition root and attach it to the lifecycle of the corresponding host.

### setContent in `Activity`

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // The root Composition for this window is created here
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
        // Composition is created when setContent is called on this ComposeView
        return ComposeView(requireContext()).apply {
            setContent { MyComposable() }
        }
    }
}
```

### Multiple Compositions

```kotlin
// Each setContent call on a distinct ComposeView creates a separate Composition
val layout = LinearLayout(this).apply {
    addView(ComposeView(this).apply {
        setContent { Text("First") } // Composition 1
    })
    addView(ComposeView(this).apply {
        setContent { Text("Second") } // Composition 2
    })
}
```

**Summary**: Every separate root defined via `setContent` on a `ComponentActivity` or `ComposeView` forms its own Composition. Its lifecycle is tied to the corresponding host (`Activity`, `Fragment`, or `View`), while the Compose runtime handles the initial composition and any subsequent recompositions.

---

## Дополнительные вопросы (RU)

- [[q-is-layoutinflater-a-singleton-and-why--android--medium]]
- [[q-network-error-handling-strategies--networking--medium]]
- Как отличается жизненный цикл Composition между `ComponentActivity` и `ComposeView` во `Fragment`?
- Что происходит с Composition при пересоздании `Activity` из-за смены конфигурации?
- Как отлаживать проблемы, связанные с несколькими вызовами `setContent` и неожиданными рекомпозициями?

## Follow-ups

- [[q-is-layoutinflater-a-singleton-and-why--android--medium]]
- [[q-network-error-handling-strategies--networking--medium]]
- How does the lifecycle of a Composition differ between `ComponentActivity` and `ComposeView` in a `Fragment`?
- What happens to the Composition when an `Activity` is recreated due to a configuration change?
- How can you debug issues related to multiple `setContent` calls and unexpected recompositions?

## Ссылки (RU)

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)
- [Lifecycle](https://developer.android.com/topic/libraries/architecture/lifecycle)
- [Jetpack Compose](https://developer.android.com/develop/ui/compose)

## References

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)
- [Lifecycle](https://developer.android.com/topic/libraries/architecture/lifecycle)
- [Jetpack Compose](https://developer.android.com/develop/ui/compose)

## Связанные вопросы (RU)

- [[q-is-layoutinflater-a-singleton-and-why--android--medium]]
- [[q-network-error-handling-strategies--networking--medium]]

## Related Questions

- [[q-is-layoutinflater-a-singleton-and-why--android--medium]]
- [[q-network-error-handling-strategies--networking--medium]]
