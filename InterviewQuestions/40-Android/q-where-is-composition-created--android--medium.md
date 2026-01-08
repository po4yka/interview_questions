---id: android-284
title: "Где создается композиция / Where Is Composition Created"
aliases: [ComposeView, Composition Creation, setContent]
topic: android
subtopics: [ui-compose, ui-views]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-ui-composition, c-compose-recomposition, c-recomposition, q-is-layoutinflater-a-singleton-and-why--android--medium, q-network-error-handling-strategies--networking--medium]
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

**Композиция (Composition)** создается и управляется **runtime-средой Jetpack Compose**, когда вы задаете содержимое через **`setContent`** у `ComponentActivity` / `ComponentDialog` или через `setContent` у `ComposeView` (например, во `Fragment` или обычном `View`). Каждый вызов `setContent` создает корневую Composition для данного хоста и привязывает ее к соответствующим жизненному циклу и владельцам состояния.

См. также: [[c-android-ui-composition]]

### setContent В `Activity`

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Здесь создается корневая Composition, связанная с этим Activity и окном
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
        // Composition создается, когда для данного ComposeView вызывается setContent
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

**Резюме**: Каждый отдельный корень, заданный через `setContent` в `ComponentActivity`, `ComponentDialog` или `ComposeView`, формирует собственную Composition. Композиция привязана к жизненному циклу конкретного хоста (окна/`Activity` и соответствующих владельцев жизненного цикла для `ComposeView`), а runtime Jetpack Compose управляет первоначальной композицией, сохранением состояния и последующими рекомпозициями.

## Answer (EN)

A **Composition** is created and managed by the **Jetpack Compose runtime** when you provide UI content via **`setContent`** on a `ComponentActivity` / `ComponentDialog` or via `setContent` on a `ComposeView` (e.g., inside a `Fragment` or a regular `View`). Each `setContent` call creates a composition root for that host and attaches it to the appropriate lifecycle and state owners.

See also: [[c-android-ui-composition]]

### setContent in `Activity`

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // The root Composition associated with this Activity and window is created here
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
        // A Composition is created when setContent is called on this ComposeView
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

**Summary**: Every separate root defined via `setContent` on a `ComponentActivity`, `ComponentDialog`, or `ComposeView` forms its own Composition. The Composition is tied to the lifecycle of its specific host (the window/`Activity` and the relevant lifecycle owners for the `ComposeView`), while the Jetpack Compose runtime is responsible for the initial composition, state handling, and subsequent recompositions.

---

## Дополнительные Вопросы (RU)

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

## Связанные Вопросы (RU)

- [[q-is-layoutinflater-a-singleton-and-why--android--medium]]
- [[q-network-error-handling-strategies--networking--medium]]

## Related Questions

- [[q-is-layoutinflater-a-singleton-and-why--android--medium]]
- [[q-network-error-handling-strategies--networking--medium]]
