---
id: 202510031417
title: What needs to be done in an Android project to start drawing UI on screen / Что нужно сделать в Android-проекте чтобы начать рисовать UI на экране
aliases: []

# Classification
topic: android
subtopics: [android, ui, basics]
question_kind: practical
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/746
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-android
related:
  - c-android-activity
  - c-android-layouts

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [Activity, UI, XML, difficulty/easy, easy_kotlin, lang/ru, android/basics, android/ui]
---

# Question (EN)
> What needs to be done in an Android project to start drawing UI on screen

# Вопрос (RU)
> Что нужно сделать в Android-проекте чтобы начать рисовать UI на экране

---

## Answer (EN)

To start drawing UI in Android, you need to: (1) Create an Activity, (2) Define a layout XML file, (3) Connect layout to Activity using `setContentView()`.

### Basic Steps

```kotlin
// 1. Create Activity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // 2. Set layout
        setContentView(R.layout.activity_main)
    }
}
```

```xml
<!-- 3. Define layout (res/layout/activity_main.xml) -->
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello World" />

    <Button
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Click Me" />
</LinearLayout>
```

### Custom Drawing

```kotlin
class CustomView(context: Context) : View(context) {
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val paint = Paint().apply { color = Color.BLUE }
        canvas.drawCircle(100f, 100f, 50f, paint)
    }
}
```

## Ответ (RU)

Чтобы начать рисовать пользовательский интерфейс (UI) на экране в Android-проекте, необходимо выполнить несколько шагов. Сначала создайте Android-проект в Android Studio с шаблоном «Empty Activity». Затем настройте макет, используя XML-файл в каталоге res/layout. Пример простого макета с TextView и Button. Подключите макет к активности через метод setContentView() в Activity классе. Если нужно нарисовать что-то вручную, создайте свой View и переопределите метод onDraw(). Для запуска приложения используйте Run в Android Studio.

---

## Follow-ups
- What's the difference between setContentView() and inflate()?
- How do you create UI programmatically without XML?
- What happens during the layout inflation process?

## References
- [[c-android-activity]]
- [[c-android-layouts]]
- [[c-android-view]]
- [[moc-android]]

## Related Questions
- [[q-how-to-choose-layout-for-fragment--android--easy]]
- [[q-view-methods-and-their-purpose--android--medium]]
