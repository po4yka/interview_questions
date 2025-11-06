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

Декларативный UI toolkit, который полностью заменяет XML:

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

Императивное создание view в коде:

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

**Сложный layout в Compose:**

```kotlin
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
                Image(
                    painter = rememberImagePainter(user.avatarUrl),
                    contentDescription = "Avatar",
                    modifier = Modifier.size(80.dp).clip(CircleShape)
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

**Сравнение подходов:**

| Аспект | Jetpack Compose | Программные `View` |
|--------|----------------|-------------------|
| Синтаксис | Декларативный, лаконичный | Императивный, многословный |
| State management | Встроенный, реактивный | Ручной |
| Preview | Поддержка @Preview | Нет preview |
| Читаемость | Высокая | Низкая для сложных UI |
| Рекомендация | ✅ Новые проекты | ❌ Только legacy |

**Рекомендации:**

- ✅ Jetpack Compose для нового кода (декларативный, поддерживаемый)
- ✅ Программные `View` для динамического UI в legacy-проектах
- ✅ Используйте @Preview в Compose для быстрой итерации
- ✅ Следуйте Material Design для консистентности

## Answer (EN)

There are two main approaches to create UI without XML in Android:

**1. Jetpack Compose (modern approach)**

Declarative UI toolkit that completely replaces XML:

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

Imperative view creation in code:

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

**Complex layout in Compose:**

```kotlin
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
                Image(
                    painter = rememberImagePainter(user.avatarUrl),
                    contentDescription = "Avatar",
                    modifier = Modifier.size(80.dp).clip(CircleShape)
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

**Comparison:**

| Aspect | Jetpack Compose | Programmatic Views |
|--------|----------------|-------------------|
| Syntax | Declarative, concise | Imperative, verbose |
| State management | Built-in, reactive | Manual |
| Preview | @Preview support | No preview |
| Readability | High | Low for complex UIs |
| Recommendation | ✅ New projects | ❌ Legacy only |

**Best practices:**

- ✅ Use Jetpack Compose for new code (declarative, maintainable)
- ✅ Use programmatic Views for dynamic UI in legacy projects
- ✅ Leverage @Preview in Compose for quick iteration
- ✅ Follow Material Design for consistency

---

## Follow-ups

- How to migrate existing XML layouts to Compose?
- How to mix Compose and `View`-based UI in the same project?
- What are the performance differences between Compose and Views?
- How to create custom layouts in Compose vs programmatic Views?
- When should you still use XML layouts?

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
