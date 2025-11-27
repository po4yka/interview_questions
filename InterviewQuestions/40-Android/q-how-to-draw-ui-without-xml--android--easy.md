---
id: android-342
title: "How To Draw UI Without XML / Как рисовать UI без XML"
aliases: [Draw UI Without XML, Jetpack Compose, Programmatic Views, Рисовать UI без XML]
topic: android
subtopics: [ui-compose, ui-views]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-ui-composition-basics, c-jetpack-compose, q-what-each-android-component-represents--android--easy]
created: 2025-10-15
updated: 2025-11-10
tags: [android/ui-compose, android/ui-views, compose, difficulty/easy, ui, views]
sources: []

date created: Saturday, November 1st 2025, 1:32:21 pm
date modified: Tuesday, November 25th 2025, 8:54:00 pm
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

**2. Программное создание `View`** (традиционный подход):
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
                        Text("Click Me")
                    }
                }
            }
        }
    }
}
```

### Пример Программного Создания `View`

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val density = resources.displayMetrics.density

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            // Конвертация dp в px при программной разметке
            val padding = (16 * density).toInt()
            setPadding(padding, padding, padding, padding)

            addView(TextView(context).apply {
                text = "Hello, Android!"
            })

            addView(Button(context).apply {
                text = "Click Me"
                setOnClickListener { /* действие */ }
            })
        }

        setContentView(layout)
    }
}
```

### Гибридный Подход

```kotlin
// ComposeView в традиционной иерархии View
val composeView = ComposeView(context).apply {
    setContent {
        MaterialTheme {
            Text("Compose in View")
        }
    }
}
linearLayout.addView(composeView)
```

**Рекомендация**: Используйте [[c-jetpack-compose]] для новых проектов, программные `View` для поддержки legacy кода или специфичных случаев.

## Answer (EN)

Android provides two main approaches to create UI without XML:

**1. Jetpack Compose** (modern, declarative):
- ✅ Declarative syntax
- ✅ Automatic state updates
- ✅ Less boilerplate
- ✅ Built-in preview support

**2. Programmatic `View` creation** (traditional):
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

### Programmatic `View` Creation Example

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val density = resources.displayMetrics.density

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            // Convert dp to px when building UI programmatically
            val padding = (16 * density).toInt()
            setPadding(padding, padding, padding, padding)

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

## Дополнительные Вопросы (RU)

- Каковы особенности производительности Compose по сравнению с программными `View`?
- Как обрабатывать сложные макеты при программном создании UI?
- Можно ли сочетать Compose и традиционные `View` на одном экране?
- В каких случаях лучше выбрать программные `View` вместо Compose?
- Как тестировать UI, созданный без XML?

## Follow-ups

- What are the performance implications of Compose vs programmatic Views?
- How do you handle complex layouts programmatically?
- Can you mix Compose and traditional Views in the same screen?
- When would you choose programmatic Views over Compose?
- How do you test UI created without XML?

## Ссылки (RU)

- [[c-jetpack-compose]] — современный декларативный UI-фреймворк
- [[c-android-ui-composition-basics]] — базовые принципы традиционной иерархии `View`
- [[moc-android]] — гид по Android-разработке
- [Документация Compose](https://developer.android.com/jetpack/compose)
- [Руководство по системе `View`](https://developer.android.com/develop/ui/views)

## References

- [[c-jetpack-compose]] - Modern declarative UI framework
- [[c-android-ui-composition-basics]] - Basics of traditional `View` hierarchy
- [[moc-android]] - Android development guide
- [Compose documentation](https://developer.android.com/jetpack/compose)
- [`View` system guide](https://developer.android.com/develop/ui/views)

## Связанные Вопросы (RU)

### Предварительные (проще)
- [[q-what-each-android-component-represents--android--easy]] - Обзор компонентов Android

### Похожие (такой Же уровень)
- [[q-why-separate-ui-and-business-logic--android--easy]] - Архитектура UI
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - Базовые сведения о UI

### Продвинутые (сложнее)
- [[q-compose-testing--android--medium]] - Оптимизация рекомпозиции

## Related Questions

### Prerequisites (Easier)
- [[q-what-each-android-component-represents--android--easy]] - Android components overview

### Related (Same Level)
- [[q-why-separate-ui-and-business-logic--android--easy]] - UI architecture
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - UI basics

### Advanced (Harder)
- [[q-compose-testing--android--medium]] - Recomposition optimization
