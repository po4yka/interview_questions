---
id: 20251012-122718
title: "How To Draw UI Without XML / Как рисовать UI без XML"
aliases: [Draw UI Without XML, Рисовать UI без XML, Jetpack Compose, Programmatic Views]
topic: android
subtopics: [ui-compose, ui-views]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, c-android-views, q-what-each-android-component-represents--android--easy]
created: 2025-10-15
updated: 2025-10-28
tags: [android/ui-compose, android/ui-views, compose, views, ui, difficulty/easy]
sources: []
date created: Tuesday, October 28th 2025, 9:49:16 am
date modified: Thursday, October 30th 2025, 12:48:36 pm
---

# Вопрос (RU)

> Как создать пользовательский интерфейс в Android без использования XML файлов разметки?

# Question (EN)

> How can you create user interfaces in Android without using XML layout files?

---

## Ответ (RU)

В Android существует два основных способа создания UI без XML:

**1. Jetpack Compose** (современный, декларативный подход):
- ✅ Декларативный синтаксис
- ✅ Автоматическое обновление состояния
- ✅ Меньше шаблонного кода
- ✅ Встроенный предпросмотр

**2. Программное создание View** (традиционный подход):
- ✅ Полный контроль над созданием
- ✅ Динамическое создание UI
- ❌ Императивный стиль
- ❌ Больше шаблонного кода

### Пример Jetpack Compose

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.Center
                ) {
                    Text("Hello, Compose!")
                    Button(onClick = { /* действие */ }) {
                        Text("Нажми")
                    }
                }
            }
        }
    }
}
```

### Пример программного создания View

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(16.dp, 16.dp, 16.dp, 16.dp)

            addView(TextView(context).apply {
                text = "Hello, Android!"
            })

            addView(Button(context).apply {
                text = "Нажми"
                setOnClickListener { /* действие */ }
            })
        }

        setContentView(layout)
    }

    private val Int.dp: Int
        get() = (this * resources.displayMetrics.density).toInt()
}
```

### Гибридный подход

```kotlin
// ComposeView в традиционной иерархии View
val composeView = ComposeView(context).apply {
    setContent {
        MaterialTheme {
            Text("Compose в View")
        }
    }
}
linearLayout.addView(composeView)
```

**Рекомендация**: Используйте [[c-jetpack-compose]] для новых проектов, программные View для поддержки legacy кода или специфичных случаев.

## Answer (EN)

Android provides two main approaches to create UI without XML:

**1. Jetpack Compose** (modern, declarative):
- ✅ Declarative syntax
- ✅ Automatic state updates
- ✅ Less boilerplate
- ✅ Built-in preview support

**2. Programmatic View creation** (traditional):
- ✅ Full control over creation
- ✅ Dynamic UI generation
- ❌ Imperative style
- ❌ More boilerplate

### Jetpack Compose Example

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.Center
                ) {
                    Text("Hello, Compose!")
                    Button(onClick = { /* action */ }) {
                        Text("Click Me")
                    }
                }
            }
        }
    }
}
```

### Programmatic View Creation Example

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(16.dp, 16.dp, 16.dp, 16.dp)

            addView(TextView(context).apply {
                text = "Hello, Android!"
            })

            addView(Button(context).apply {
                text = "Click Me"
                setOnClickListener { /* action */ }
            })
        }

        setContentView(layout)
    }

    private val Int.dp: Int
        get() = (this * resources.displayMetrics.density).toInt()
}
```

### Hybrid Approach

```kotlin
// ComposeView in traditional View hierarchy
val composeView = ComposeView(context).apply {
    setContent {
        MaterialTheme {
            Text("Compose in View")
        }
    }
}
linearLayout.addView(composeView)
```

**Recommendation**: Use [[c-jetpack-compose]] for new projects, programmatic Views for legacy support or specific use cases.

---

## Follow-ups

- What are the performance implications of Compose vs programmatic Views?
- How do you handle complex layouts programmatically?
- Can you mix Compose and traditional Views in the same screen?
- When would you choose programmatic Views over Compose?
- How do you test UI created without XML?

## References

- [[c-jetpack-compose]] - Modern declarative UI framework
- [[c-android-views]] - Traditional View system
- [[moc-android]] - Android development guide
- [Compose documentation](https://developer.android.com/jetpack/compose)
- [View system guide](https://developer.android.com/develop/ui/views)

## Related Questions

### Prerequisites (Easier)
- [[q-what-each-android-component-represents--android--easy]] - Android components overview

### Related (Same Level)
- [[q-why-separate-ui-and-business-logic--android--easy]] - UI architecture
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - UI basics

### Advanced (Harder)
- [[q-compose-state-management--android--medium]] - State in Compose
- [[q-compose-recomposition--android--medium]] - Recomposition optimization
