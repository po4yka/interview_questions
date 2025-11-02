---
id: android-137
title: "How To Start Drawing UI In Android / Как начать рисовать UI в Android"
aliases: ["How To Start Drawing UI In Android", "Как начать рисовать UI в Android"]
topic: android
subtopics: [activity, ui-views]
question_kind: android
difficulty: easy
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-fragment-vs-activity-lifecycle--android--medium, q-retrofit-library--android--medium]
created: 2025-10-15
updated: 2025-01-27
tags: [android, android/activity, android/ui-views, difficulty/easy, ui]
sources: []
date created: Monday, October 27th 2025, 3:42:02 pm
date modified: Saturday, November 1st 2025, 5:43:35 pm
---

# Вопрос (RU)

> Что нужно сделать в Android-проекте, чтобы начать рисовать UI на экране?

# Question (EN)

> What needs to be done in an Android project to start drawing UI on screen?

## Ответ (RU)

Чтобы начать отображать UI в Android, необходимо: (1) создать [[c-activity|Activity]], (2) определить layout (разметку), (3) связать их через `setContentView()`.

### Основные Способы

**1. XML Layout (традиционный)**

```kotlin
// ✅ Стандартный подход для View-based UI
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)  // ✅ Связывание layout с Activity
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
// ✅ Декларативный UI без XML
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {  // ✅ Compose UI вместо setContentView
            Text("Hello World")
        }
    }
}
```

**3. Custom View (программная отрисовка)**

```kotlin
// ✅ Низкоуровневая отрисовка через Canvas
class CustomView(context: Context) : View(context) {
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val paint = Paint().apply { color = Color.BLUE }
        canvas.drawCircle(100f, 100f, 50f, paint)
    }
}
```

## Answer (EN)

To display UI in Android, you need to: (1) create an [[c-activity|Activity]], (2) define a layout, (3) connect them via `setContentView()`.

### Main Approaches

**1. XML Layout (traditional)**

```kotlin
// ✅ Standard approach for View-based UI
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)  // ✅ Bind layout to Activity
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
// ✅ Declarative UI without XML
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {  // ✅ Compose UI instead of setContentView
            Text("Hello World")
        }
    }
}
```

**3. Custom View (programmatic drawing)**

```kotlin
// ✅ Low-level drawing with Canvas
class CustomView(context: Context) : View(context) {
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val paint = Paint().apply { color = Color.BLUE }
        canvas.drawCircle(100f, 100f, 50f, paint)
    }
}
```

---

## Follow-ups

- What happens if `setContentView()` is called multiple times?
- How does Android handle Activity recreation during configuration changes (rotation)?
- What is the difference between `AppCompatActivity` and `ComponentActivity`?
- How does ViewBinding/DataBinding integrate with `setContentView()`?

## References

- [[c-activity]] - Activity lifecycle and fundamentals
- [[c-android-ui-composition]] - UI composition patterns
- https://developer.android.com/guide/components/activities/intro-activities

## Related Questions

### Prerequisites (Easier)

- [[c-activity]] - Understanding Activity basics

### Related (Same Level)

- [[q-fragment-vs-activity-lifecycle--android--medium]] - Fragment vs Activity lifecycle
- [[q-retrofit-library--android--medium]] - Network layer setup

### Advanced (Harder)

- Activity state restoration during process death
- Custom ViewGroup implementation
- Compose interop with XML Views
