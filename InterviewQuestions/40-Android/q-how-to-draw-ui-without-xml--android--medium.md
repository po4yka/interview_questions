---
id: android-240
title: How To Draw UI Without XML / Как рисовать UI без XML
aliases:
- Drawing UI without XML
- Jetpack Compose UI
- Programmatic UI
- Программный UI
- Рисование UI без XML
topic: android
subtopics:
- ui-compose
- ui-views
question_kind: theory
difficulty: medium
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-compose-state
- c-jetpack-compose
- q-how-to-create-list-like-recyclerview-in-compose--android--medium
- q-how-to-start-drawing-ui-in-android--android--easy
- q-testing-compose-ui--android--medium
sources: []
created: 2025-10-15
updated: 2025-10-28
tags:
- android
- android/ui-compose
- android/ui-views
- difficulty/medium
- jetpack-compose
- programmatic-views
- ui

---

# Вопрос (RU)

> Как рисовать UI без XML в Android?

# Question (EN)

> How to draw UI without XML in Android?

---

## Ответ (RU)

В Android есть два основных способа создания UI без XML:

**1. Jetpack Compose (современный подход)**

Современный декларативный UI toolkit, который позволяет описывать интерфейс без XML и заменяет его в большинстве новых проектов:

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(16.dp),
                    verticalArrangement = Arrangement.Center
                ) {
                    var count by remember { mutableStateOf(0) }

                    Text(
                        text = "Count: $count",
                        style = MaterialTheme.typography.headlineMedium
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Button(onClick = { count++ }) {
                        Text("Increment")
                    }
                }
            }
        }
    }
}
```

**2. Программное создание `View` (традиционный подход)**

Императивное создание `View`-иерархии в коде без использования XML:

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.MATCH_PARENT
            )
            // Используем dp-расширение для конвертации dp в пиксели
            setPadding(16.dp, 16.dp, 16.dp, 16.dp)
        }

        val textView = TextView(this).apply {
            text = "Hello Android!"
            textSize = 24f
        }

        val button = Button(this).apply {
            text = "Click Me"
            setOnClickListener {
                Toast.makeText(context, "Clicked!", Toast.LENGTH_SHORT).show()
            }
        }

        layout.addView(textView)
        layout.addView(button)
        setContentView(layout)
    }

    private val Int.dp: Int
        get() = (this * resources.displayMetrics.density).toInt()
}
```

**Пример более сложного layout в Compose:**

```kotlin
data class User(
    val name: String,
    val avatarUrl: String,
    val bio: String
)

@Composable
fun ProfileScreen(user: User) {
    Column(modifier = Modifier.fillMaxSize()) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(200.dp)
                .background(MaterialTheme.colorScheme.primary)
        ) {
            Column(
                modifier = Modifier.align(Alignment.Center),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // В реальном проекте используйте подходящую библиотеку для загрузки изображений.
                // Для современных сетапов часто применяют AsyncImage или актуальные API Coil.
                Image(
                    painter = rememberImagePainter(user.avatarUrl),
                    contentDescription = "Avatar",
                    modifier = Modifier
                        .size(80.dp)
                        .clip(CircleShape)
                )
                Text(user.name, color = Color.White)
            }
        }

        LazyColumn(contentPadding = PaddingValues(16.dp)) {
            item { Text("About", style = MaterialTheme.typography.titleLarge) }
            item { Text(user.bio) }
        }
    }
}
```

Примечание: `rememberImagePainter` относится к более старому API `coil-compose` и требует соответствующей зависимости. В новых проектах рекомендуется использовать `AsyncImage` или современные подходы загрузки изображений из актуальной версии Coil.

**Сравнение подходов:**

| Аспект | Jetpack Compose | Программные `View` |
|--------|----------------|-------------------|
| Синтаксис | Декларативный, лаконичный | Императивный, многословный |
| State management | Встроенный, реактивный | Ручное управление состоянием |
| Preview | Поддержка `@Preview` | Нет встроенного preview-инструмента |
| Читаемость | Обычно высокая для сложных UI | Может ухудшаться для сложных UI |
| Рекомендация | Предпочтителен для новых экранов и проектов | Актуален для существующих `View`-архитектур и специфических кейсов |

**Рекомендации:**

- Используйте Jetpack Compose как основной выбор для нового кода (декларативный, активно развиваемый)
- Применяйте программные `View` в legacy-проектах, при интеграции с существующей `View`-иерархией или при необходимости низкоуровневого контроля
- Используйте `@Preview` в Compose для быстрой итерации
- Следуйте Material Design для консистентности

## Answer (EN)

There are two main approaches to create UI without XML in Android:

**1. Jetpack Compose (modern approach)**

Modern declarative UI toolkit that lets you define UI without XML and is the recommended choice for most new projects:

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(16.dp),
                    verticalArrangement = Arrangement.Center
                ) {
                    var count by remember { mutableStateOf(0) }

                    Text(
                        text = "Count: $count",
                        style = MaterialTheme.typography.headlineMedium
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Button(onClick = { count++ }) {
                        Text("Increment")
                    }
                }
            }
        }
    }
}
```

**2. Programmatic Views (traditional approach)**

Imperative creation of the `View` hierarchy in code, without XML:

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.MATCH_PARENT
            )
            // Use dp extension to convert dp to pixels
            setPadding(16.dp, 16.dp, 16.dp, 16.dp)
        }

        val textView = TextView(this).apply {
            text = "Hello Android!"
            textSize = 24f
        }

        val button = Button(this).apply {
            text = "Click Me"
            setOnClickListener {
                Toast.makeText(context, "Clicked!", Toast.LENGTH_SHORT).show()
            }
        }

        layout.addView(textView)
        layout.addView(button)
        setContentView(layout)
    }

    private val Int.dp: Int
        get() = (this * resources.displayMetrics.density).toInt()
}
```

**Example of a more complex layout in Compose:**

```kotlin
data class User(
    val name: String,
    val avatarUrl: String,
    val bio: String
)

@Composable
fun ProfileScreen(user: User) {
    Column(modifier = Modifier.fillMaxSize()) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(200.dp)
                .background(MaterialTheme.colorScheme.primary)
        ) {
            Column(
                modifier = Modifier.align(Alignment.Center),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // In a real project use an appropriate image-loading library.
                // For modern setups, a common choice is AsyncImage or other up-to-date Coil APIs.
                Image(
                    painter = rememberImagePainter(user.avatarUrl),
                    contentDescription = "Avatar",
                    modifier = Modifier
                        .size(80.dp)
                        .clip(CircleShape)
                )
                Text(user.name, color = Color.White)
            }
        }

        LazyColumn(contentPadding = PaddingValues(16.dp)) {
            item { Text("About", style = MaterialTheme.typography.titleLarge) }
            item { Text(user.bio) }
        }
    }
}
```

Note: `rememberImagePainter` is part of an older `coil-compose` API and requires the proper Coil dependency. For new projects, it is recommended to use `AsyncImage` or other up-to-date image loading approaches from the latest Coil library.

**Comparison:**

| Aspect | Jetpack Compose | Programmatic Views |
|--------|----------------|-------------------|
| Syntax | Declarative, concise | Imperative, more verbose |
| State management | Built-in, reactive | Manual state handling |
| Preview | `@Preview` support | No built-in preview tooling |
| Readability | Typically high for complex UIs | Can degrade for complex UIs |
| Recommendation | Preferred for new screens and projects | Valid for existing `View`-based stacks and specific use cases |

**Best practices:**

- Use Jetpack Compose as the primary choice for new code (declarative, actively supported)
- Use programmatic Views in legacy projects, when integrating with existing `View` hierarchies, or when low-level control is needed
- Leverage `@Preview` in Compose for quick iteration
- Follow Material Design for consistency

---

## Дополнительные вопросы (RU)

- Как мигрировать существующие XML-разметки на Compose?
- Как совместить Compose и `View`-базированный UI в одном проекте?
- Каковы различия в производительности между Compose и Views?
- Как создавать кастомные layouts в Compose и программных `View`?
- Когда все еще имеет смысл использовать XML-верстку?

## Follow-ups

- How to migrate existing XML layouts to Compose?
- How to mix Compose and `View`-based UI in the same project?
- What are the performance differences between Compose and Views?
- How to create custom layouts in Compose vs programmatic Views?
- When should you still use XML layouts?

## Ссылки (RU)

- [Документация Jetpack Compose](https://developer.android.com/jetpack/compose)
- [Программные Views и кастомные компоненты](https://developer.android.com/guide/topics/ui/custom-components)
- [Сравнение Compose и Views](https://developer.android.com/jetpack/compose/mental-model)

## References

- [Jetpack Compose documentation](https://developer.android.com/jetpack/compose)
- [Programmatic Views guide](https://developer.android.com/guide/topics/ui/custom-components)
- [Compose vs Views comparison](https://developer.android.com/jetpack/compose/mental-model)

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]
- [[c-jetpack-compose]]

### Prerequisites (Easier)
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - UI basics in Android
- [[q-why-separate-ui-and-business-logic--android--easy]] - UI separation principles

### Related (Same Level)
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Lists in Compose
- [[q-testing-compose-ui--android--medium]] - Testing Compose UI
- [[q-which-event-is-triggered-when-user-presses-screen--android--medium]] - UI event handling
