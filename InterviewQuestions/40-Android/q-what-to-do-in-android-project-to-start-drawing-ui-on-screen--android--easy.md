---
id: 20251012-122711
title: "What To Do In Android Project To Start Drawing UI On Screen / Что делать в Android проекте чтобы начать рисовать UI на экране"
aliases: ["What To Do In Android Project To Start Drawing UI On Screen", "Что делать в Android проекте чтобы начать рисовать UI на экране"]
topic: android
subtopics: [activity, ui-views, ui-compose]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, q-how-to-pass-parameters-to-fragment--android--easy]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android, android/activity, android/ui-views, android/ui-compose, difficulty/easy]
---
# Вопрос (RU)
> Что нужно сделать в Android-проекте, чтобы начать рисовать UI на экране?

# Question (EN)
> What needs to be done in an Android project to start drawing UI on the screen?

---

## Ответ (RU)

Чтобы отобразить UI на экране в Android, необходимо: **(1)** создать Activity как точку входа, **(2)** установить content view с помощью XML layout или [[c-jetpack-compose|Compose]], **(3)** объявить Activity в AndroidManifest.xml как `LAUNCHER`. При запуске система вызывает `onCreate()` и UI прикрепляется к экрану.

### Минимальные шаги

1. **Создать Activity**
2. **Установить content view** (XML, Compose или программно)
3. **Зарегистрировать в AndroidManifest.xml**

### Классический подход (XML + Views)

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // ✅ Установка UI через XML layout
        setContentView(R.layout.activity_main)
    }
}
```

XML layout:
```xml
<!-- res/layout/activity_main.xml -->
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:gravity="center">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello, Android!" />
</LinearLayout>
```

### Jetpack Compose подход

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // ✅ Установка UI через Compose
        setContent {
            MaterialTheme {
                Text("Hello, Compose!")
            }
        }
    }
}
```

### Регистрация в AndroidManifest.xml

```xml
<application ...>
    <activity
        android:name=".MainActivity"
        android:exported="true">  <!-- ✅ Обязательно для LAUNCHER -->
        <intent-filter>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent-filter>
    </activity>
</application>
```

**Ключевые моменты:**
- **LAUNCHER** intent filter делает Activity стартовой точкой приложения
- `android:exported="true"` обязателен для компонентов с intent-filter
- `setContentView()` или `setContent {}` вызываются **один раз** в `onCreate()`

---

## Answer (EN)

To display UI on screen in Android, you need: **(1)** create an Activity as entry point, **(2)** set content view with XML layout or [[c-jetpack-compose|Compose]], **(3)** declare the Activity in AndroidManifest.xml as `LAUNCHER`. When launched, the system calls `onCreate()` and UI is attached to the screen.

### Minimum Steps

1. **Create Activity**
2. **Set content view** (XML, Compose, or programmatically)
3. **Register in AndroidManifest.xml**

### Classic Approach (XML + Views)

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // ✅ Set UI via XML layout
        setContentView(R.layout.activity_main)
    }
}
```

XML layout:
```xml
<!-- res/layout/activity_main.xml -->
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:gravity="center">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello, Android!" />
</LinearLayout>
```

### Jetpack Compose Approach

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // ✅ Set UI via Compose
        setContent {
            MaterialTheme {
                Text("Hello, Compose!")
            }
        }
    }
}
```

### Registration in AndroidManifest.xml

```xml
<application ...>
    <activity
        android:name=".MainActivity"
        android:exported="true">  <!-- ✅ Required for LAUNCHER -->
        <intent-filter>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent-filter>
    </activity>
</application>
```

**Key Points:**
- **LAUNCHER** intent filter makes Activity the app entry point
- `android:exported="true"` is mandatory for components with intent-filter
- `setContentView()` or `setContent {}` called **once** in `onCreate()`

---

## Follow-ups

- What happens if multiple Activities have LAUNCHER intent filter?
- When should you use `setContentView()` vs `setContent {}`?
- Can you change UI after `onCreate()` completes?
- What are the implications of `android:exported` for security?

## References

- [[c-jetpack-compose]] - Declarative UI with Compose
- Official Android Developer Docs on Activities

## Related Questions

### Prerequisites
- Basic understanding of Android project structure
- Familiarity with Kotlin or Java

### Related
- [[q-how-to-pass-parameters-to-fragment--android--easy]] - Fragment initialization
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Fragment vs Activity lifecycle

### Advanced
- [[q-activity-lifecycle-methods--android--medium]] - Activity lifecycle callbacks
- [[q-how-does-activity-lifecycle-work--android--medium]] - Detailed lifecycle mechanics
