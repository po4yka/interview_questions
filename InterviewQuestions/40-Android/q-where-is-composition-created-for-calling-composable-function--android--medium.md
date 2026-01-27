---
anki_cards:
- slug: android-742-0-en
  language: en
- slug: android-742-0-ru
  language: ru
- slug: q-where-is-composition-created-for-calling-composable-function--android--medium-0-en
  language: en
- slug: q-where-is-composition-created-for-calling-composable-function--android--medium-0-ru
  language: ru
---

id: android-410
id: android-742
title: "Где создается Composition для вызова composable функции / Where Is Composition Created For Calling Composable Function"
aliases: ["Where Is Composition Created", "Где создается Composition"]
topic: android
subtopics: [ui-compose]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-ui-composition, c-compose-recomposition, c-recomposition, q-compositionlocal-advanced--android--medium, q-how-does-jetpackcompose-work--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/ui-compose, difficulty/medium, setContent]

---
# Вопрос (RU)

> Где создается Composition для вызова composable функции?

# Question (EN)

> Where is the Composition created when calling a composable function?

---

## Ответ (RU)

**Композиция создается не при каждом вызове composable-функции, а в точке, где хост (например, `setContent` или `ComposeView`) создает корневую композицию.** Эта точка входа инициирует построение дерева composable-функций и управление их состоянием.

### Основные Места Создания Корневой Композиции

**1. В `Activity` через ComponentActivity.setContent():**

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ✅ Корневая композиция создается здесь
        setContent {
            MyApp()
        }
    }
}
```

**2. Во `Fragment` через ComposeView:**

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // ✅ Корневая композиция создается при setContent на ComposeView
        return ComposeView(requireContext()).apply {
            setContent { MyComposable() }
        }
    }
}
```

**3. В обычной `View` через ComposeView:**

```kotlin
class MyCustomView(context: Context) : LinearLayout(context) {
    init {
        // ✅ Каждый ComposeView создает отдельную корневую композицию
        addView(ComposeView(context).apply {
            setContent { Text("Compose inside View") }
        })
    }
}
```

### Множественные Композиции

Каждый вызов `setContent` или `ComposeView.setContent` создает **отдельную независимую корневую композицию**:

```kotlin
val layout = LinearLayout(context)

// ⚠️ Эти две композиции не разделяют одно и то же compose-состояние по умолчанию
layout.addView(ComposeView(context).apply {
    setContent { Text("First composition") }  // Композиция #1
})

layout.addView(ComposeView(context).apply {
    setContent { Text("Second composition") } // Композиция #2
})
```

Если нужно разделять состояние между разными композициями, это делается через общие владельцы состояния (например, `ViewModel`, DI, синглтоны), а не через общий Composition tree.

### Жизненный Цикл Композиции

```kotlin
@Composable
fun CompositionLifecycle() {
    // Входит в композицию, когда этот composable становится частью дерева в рамках корневой композиции
    DisposableEffect(Unit) {
        println("Entered composition")

        onDispose {
            // Выходит при удалении этого composable из дерева
            // (например, при уничтожении хоста или изменении навигации/условий)
            println("Left composition")
        }
    }
}
```

Композиция живет, пока жив ее хост: `setContent` на `Activity`/Window, `ComposeView` во вью-иерархии и т.п. При уничтожении или отсоединении хоста соответствующая композиция удаляется.

**Резюме**: Composition — это структура данных, описывающая дерево composable-функций и их состояние. Корневая композиция создается хостом (например, `setContent` или `ComposeView`) и привязана к жизненному циклу этого хоста.

## Answer (EN)

**A Composition is not created for each arbitrary composable call; it is created by a host (such as `setContent` or `ComposeView`) that creates a root composition.** This entry point initializes the tree of composable functions and their state management.

### Primary Root Composition Creation Points

**1. In `Activity` via ComponentActivity.setContent():**

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ✅ Root composition is created here
        setContent {
            MyApp()
        }
    }
}
```

**2. In `Fragment` via ComposeView:**

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // ✅ Root composition is created when setContent is called on ComposeView
        return ComposeView(requireContext()).apply {
            setContent { MyComposable() }
        }
    }
}
```

**3. In a custom `View` via ComposeView:**

```kotlin
class MyCustomView(context: Context) : LinearLayout(context) {
    init {
        // ✅ Each ComposeView creates its own root composition
        addView(ComposeView(context).apply {
            setContent { Text("Compose inside View") }
        })
    }
}
```

### Multiple Compositions

Each call to `setContent` or `ComposeView.setContent` creates a **separate independent root composition**:

```kotlin
val layout = LinearLayout(context)

// ⚠️ These two compositions do not share the same compose state by default
layout.addView(ComposeView(context).apply {
    setContent { Text("First composition") }  // Composition #1
})

layout.addView(ComposeView(context).apply {
    setContent { Text("Second composition") } // Composition #2
})
```

If you need to share state across multiple compositions, you do it via shared state owners (e.g., ViewModels, DI, singletons), not through a single shared Composition tree.

### Composition Lifecycle

```kotlin
@Composable
fun CompositionLifecycle() {
    // Enters the composition when this composable becomes part of the tree in a root composition
    DisposableEffect(Unit) {
        println("Entered composition")

        onDispose {
            // Called when this composable leaves the composition
            // (e.g., host is destroyed or navigation/conditions change)
            println("Left composition")
        }
    }
}
```

A composition lives as long as its host lives: the `setContent` host on an `Activity`/Window, a `ComposeView` attached to the view hierarchy, etc. When the host is destroyed or detached, the corresponding composition is disposed.

**Summary**: A Composition is the data structure representing the tree of composable functions and their state. A root composition is created by a host (e.g., `setContent` or `ComposeView`) and is tied to that host's lifecycle.

---

## Дополнительные Вопросы (RU)

- Что происходит с композицией при изменении конфигурации?
- Как несколько композиций могут взаимодействовать друг с другом?
- Можно ли создать композицию программно без `setContent`?
- В чем разница между `Composition` и `CompositionLocal`?
- Как уничтожение композиции влияет на выполняющиеся корутины?

## Follow-ups

- What happens to composition when configuration changes occur?
- How do multiple compositions communicate with each other?
- Can you create a composition programmatically without `setContent`?
- What is the difference between `Composition` and `CompositionLocal`?
- How does composition disposal affect ongoing coroutines?

## Ссылки (RU)

- [Compose Lifecycle](https://developer.android.com/jetpack/compose/lifecycle)
- [Understanding Composition](https://developer.android.com/jetpack/compose/mental-model)
- [Thinking in Compose](https://developer.android.com/jetpack/compose/mental-model)

## References

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
