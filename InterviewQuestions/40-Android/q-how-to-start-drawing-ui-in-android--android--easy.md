---
id: android-704
anki_cards:
- slug: android-137-0-en
  language: en
  anki_id: 1769330954291
  synced_at: '2026-01-25T12:50:08.577578'
- slug: android-137-0-ru
  language: ru
  anki_id: 1769330954310
  synced_at: '2026-01-25T12:50:08.579405'
- slug: android-704-0-en
  language: en
- slug: android-704-0-ru
  language: ru
- slug: q-how-to-start-drawing-ui-in-android--android--easy-0-en
  language: en
- slug: q-how-to-start-drawing-ui-in-android--android--easy-0-ru
  language: ru
title: How To Start Drawing UI In Android / Как начать рисовать UI в Android
aliases:
- How To Start Drawing UI In Android
- Как начать рисовать UI в Android
topic: android
subtopics:
- activity
- ui-views
question_kind: android
difficulty: easy
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-activity
- c-compose-recomposition
- c-recomposition
- c-wear-compose
- q-fragment-vs-activity-lifecycle--android--medium
- q-retrofit-library--android--medium
created: 2025-10-15
updated: 2025-11-10
tags:
- android
- android/activity
- android/ui-views
- difficulty/easy
- ui
sources: []
---
# Вопрос (RU)

> Что нужно сделать в Android-проекте, чтобы начать рисовать UI на экране?

# Question (EN)

> What needs to be done in an Android project to start drawing UI on screen?

## Ответ (RU)

Чтобы начать отображать UI в Android, нужно:
- создать точку входа, обычно [[c-activity|`Activity`]] (или экран на её основе),
- задать для неё содержимое: `View`-иерархию через `setContentView()` (`View`-based UI) или дерево composable-функций через `setContent {}` (Jetpack Compose).

### Основные Способы

**1. XML Layout (традиционный, `View`-based UI)**

```kotlin
// Стандартный подход для View-based UI
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)  // Связывание layout с Activity
    }
}
```

```xml
<!-- res/layout/activity_main.xml -->
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello World" />
</LinearLayout>
```

**2. Jetpack Compose (современный)**

```kotlin
// Декларативный UI без XML
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {  // Compose UI вместо setContentView для Activity
            Text("Hello World")
        }
    }
}
```

**3. Custom `View` (программная отрисовка)**

```kotlin
// Низкоуровневая отрисовка через Canvas
class CustomView(context: Context) : View(context) {
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val paint = Paint().apply { color = Color.BLUE }
        canvas.drawCircle(100f, 100f, 50f, paint)
    }
}

// Подключение CustomView, один из вариантов:
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(CustomView(this))  // Устанавливаем CustomView как корневой View
    }
}
```

## Answer (EN)

To display UI in Android, you need to:
- create an entry point, usually an [[c-activity|`Activity`]] (or a screen based on it),
- set its content: a `View` hierarchy via `setContentView()` (`View`-based UI) or a tree of composable functions via `setContent {}` (Jetpack Compose).

### Main Approaches

**1. XML Layout (traditional, `View`-based UI)**

```kotlin
// Standard approach for View-based UI
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)  // Bind layout to Activity
    }
}
```

```xml
<!-- res/layout/activity_main.xml -->
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello World" />
</LinearLayout>
```

**2. Jetpack Compose (modern)**

```kotlin
// Declarative UI without XML
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {  // Compose UI instead of setContentView for the Activity
            Text("Hello World")
        }
    }
}
```

**3. Custom `View` (programmatic drawing)**

```kotlin
// Low-level drawing with Canvas
class CustomView(context: Context) : View(context) {
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val paint = Paint().apply { color = Color.BLUE }
        canvas.drawCircle(100f, 100f, 50f, paint)
    }
}

// Attaching the CustomView, one option:
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(CustomView(this))  // Set CustomView as the root View
    }
}
```

---

## Дополнительные Вопросы (RU)

- Что произойдет, если вызвать `setContentView()` несколько раз?
- Как Android обрабатывает пересоздание `Activity` при изменении конфигурации (например, поворот экрана)?
- В чем разница между `AppCompatActivity` и `ComponentActivity`?
- Как ViewBinding/DataBinding интегрируются с `setContentView()`?

## Follow-ups

- What happens if `setContentView()` is called multiple times?
- How does Android handle `Activity` recreation during configuration changes (rotation)?
- What is the difference between `AppCompatActivity` and `ComponentActivity`?
- How does ViewBinding/DataBinding integrate with `setContentView()`?

## Ссылки (RU)

- [[c-activity]] - Жизненный цикл и основы `Activity`
- https://developer.android.com/guide/components/activities/intro-activities

## References

- [[c-activity]] - `Activity` lifecycle and fundamentals
- https://developer.android.com/guide/components/activities/intro-activities

## Связанные Вопросы (RU)

### Предпосылки (проще)

- [[c-activity]] - Базовые понятия об `Activity`

### Похожие (тот Же уровень)

- [[q-fragment-vs-activity-lifecycle--android--medium]] - Жизненный цикл `Fragment` vs `Activity`
- [[q-retrofit-library--android--medium]] - Настройка сетевого слоя

### Продвинутые (сложнее)

- Восстановление состояния `Activity` после убийства процесса
- Реализация пользовательского `ViewGroup`
- Интеграция Compose с XML-представлениями

## Related Questions

### Prerequisites (Easier)

- [[c-activity]] - Understanding `Activity` basics

### Related (Same Level)

- [[q-fragment-vs-activity-lifecycle--android--medium]] - `Fragment` vs `Activity` lifecycle
- [[q-retrofit-library--android--medium]] - Network layer setup

### Advanced (Harder)

- `Activity` state restoration during process death
- Custom `ViewGroup` implementation
- Compose interop with XML Views
