---\
id: android-170
title: "What To Do In Android Project To Start Drawing UI On Screen / Что делать в Android проекте чтобы начать рисовать UI на экране"
aliases: ["What To Do In Android Project To Start Drawing UI On Screen", "Что делать в Android проекте чтобы начать рисовать UI на экране"]
topic: android
subtopics: [activity, ui-compose, ui-views]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, q-how-to-pass-parameters-to-fragment--android--easy]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android, android/activity, android/ui-compose, android/ui-views, difficulty/easy]

---\
# Вопрос (RU)
> Что нужно сделать в Android-проекте, чтобы начать рисовать UI на экране?

# Question (EN)
> What needs to be done in an Android project to start drawing UI on the screen?

---

## Ответ (RU)

Чтобы отобразить UI на экране в Android, необходимо: **(1)** создать `Activity` как точку входа (или экран), **(2)** установить для неё содержимое (content view) с помощью XML layout, [[c-jetpack-compose|Compose]] или программно, **(3)** объявить хотя бы одну `Activity` в AndroidManifest.xml c `MAIN` + `LAUNCHER` (для стартового экрана приложения). При запуске приложения система вызывает `onCreate()` у LAUNCHER-`Activity` и прикрепляет указанный UI к окну.

### Минимальные Шаги

1. **Создать `Activity`**
2. **Установить content view** (XML, Compose или программно)
3. **Зарегистрировать `Activity` в AndroidManifest.xml** (и добавить MAIN/LAUNCHER для стартовой `Activity`)

### Классический Подход (XML + Views)

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

### Jetpack Compose Подход

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

### Регистрация В AndroidManifest.xml

```xml
<application ...>
    <activity
        android:name=".MainActivity"
        android:exported="true">  <!-- ✅ Обязательно для Activity с intent-filter (API 31+), включая LAUNCHER -->
        <intent-filter>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent-filter>
    </activity>
</application>
```

**Ключевые моменты:**
- **LAUNCHER** intent filter делает `Activity` стартовой точкой приложения.
- `android:exported="true"` обязателен для компонентов с intent-filter начиная с Android 12 (API 31+).
- Обычно `setContentView()` или `setContent {}` вызываются один раз в `onCreate()` для установки базового UI; при необходимости UI можно обновлять или заменять позже (через те же методы или работу с view-иерархией / state в Compose).
- Любая зарегистрированная `Activity` с установленным контентом может отображать UI, если она запущена (не только LAUNCHER).

---

## Answer (EN)

To display UI on screen in Android, you need to: **(1)** create an `Activity` as an entry point (screen), **(2)** set its content (content view) using an XML layout, [[c-jetpack-compose|Compose]], or programmatically, **(3)** declare at least one `Activity` in AndroidManifest.xml with `MAIN` + `LAUNCHER` (as the app launch screen). When the app is started, the system calls `onCreate()` on the LAUNCHER `Activity` and attaches the specified UI to the window.

### Minimum Steps

1. **Create an `Activity`**
2. **`Set` content view** (XML, Compose, or programmatically)
3. **Register the `Activity` in AndroidManifest.xml** (and add MAIN/LAUNCHER for the launch `Activity`)

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
        android:exported="true">  <!-- ✅ Required for activities with intent-filters (API 31+), including LAUNCHER -->
        <intent-filter>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent-filter>
    </activity>
</application>
```

**Key Points:**
- The **LAUNCHER** intent filter makes an `Activity` the app entry (launch) point.
- `android:exported="true"` is mandatory for components with intent-filters starting from Android 12 (API 31+).
- Typically `setContentView()` or `setContent {}` is called once in `onCreate()` to set the base UI; you can update or replace the UI later (via these methods, view hierarchy changes, or Compose state).
- Any registered `Activity` with content set can display UI when started, not only the LAUNCHER `Activity`.

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
- [[q-how-to-pass-parameters-to-fragment--android--easy]] - `Fragment` initialization
- [[q-fragment-vs-activity-lifecycle--android--medium]] - `Fragment` vs `Activity` lifecycle

### Advanced
- [[q-activity-lifecycle-methods--android--medium]] - `Activity` lifecycle callbacks
- [[q-how-does-activity-lifecycle-work--android--medium]] - Detailed lifecycle mechanics
