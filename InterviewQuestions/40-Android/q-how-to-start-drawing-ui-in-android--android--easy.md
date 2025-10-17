---
id: 20251012-1227198
title: "How To Start Drawing Ui In Android / Как начать рисовать UI в Android"
topic: android
difficulty: easy
status: draft
created: 2025-10-15
tags: [UI, XML, android, android/basics, android/ui, basics, ui, difficulty/easy]
---

# Что нужно сделать в Android-проекте чтобы начать рисовать UI на экране?

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

Чтобы начать рисовать пользовательский интерфейс (UI) на экране в Android-проекте, необходимо выполнить несколько шагов. Сначала создайте Android-проект в Android Studio с шаблоном «Empty Activity». Затем настройте макет, используя XML-файл в каталоге res/layout. Пример простого макета с TextView и Button. Подключите макет к активности через метод setContentView() в Activity классе. Если нужно нарисовать что-то вручную, создайте свой View и переопределите метод onDraw(). Для запуска приложения используйте Run в Android Studio.

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
