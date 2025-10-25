---
id: 20251012-1227198
title: "How To Start Drawing Ui In Android / Как начать рисовать UI в Android"
topic: android
difficulty: easy
status: draft
moc: moc-android
related: [q-fragment-vs-activity-lifecycle--android--medium, q-mlkit-face-detection--ml--medium, q-retrofit-library--android--medium]
created: 2025-10-15
tags: [android, android/basics, android/ui, basics, difficulty/easy, ui, UI, XML]
date created: Saturday, October 25th 2025, 1:26:29 pm
date modified: Saturday, October 25th 2025, 4:11:15 pm
---

# Что Нужно Сделать В Android-проекте Чтобы Начать Рисовать UI На Экране?

**English**: What needs to be done in an Android project to start drawing UI on screen?

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

Чтобы начать рисовать UI в Android, необходимо: (1) Создать Activity, (2) Определить XML-файл разметки, (3) Подключить разметку к Activity с помощью `setContentView()`.

### Основные Шаги

```kotlin
// 1. Создать Activity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // 2. Установить разметку
        setContentView(R.layout.activity_main)
    }
}
```

```xml
<!-- 3. Определить разметку (res/layout/activity_main.xml) -->
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

### Пользовательская Отрисовка

```kotlin
class CustomView(context: Context) : View(context) {
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val paint = Paint().apply { color = Color.BLUE }
        canvas.drawCircle(100f, 100f, 50f, paint)
    }
}
```

---

---

## Follow-ups

-   What's the difference between onCreate() and onStart() for UI initialization?
-   How do you handle different screen sizes and orientations when creating UI layouts?
-   What are the alternatives to XML layouts for creating Android UI?

## References

-   `https://developer.android.com/guide/components/activities` — Activity lifecycle
-   `https://developer.android.com/guide/topics/ui/declaring-layout` — Layout guide
-   `https://developer.android.com/training/basics/firstapp` — First app tutorial

## Related Questions

### Related (Easy)

-   [[q-what-needs-to-be-done-in-android-project-to-start-drawing-ui-on-screen--android--easy]] - UI basics
