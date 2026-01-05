---
id: android-113
title: UI Setup in Android Project / Настройка UI в проекте Android
aliases: [UI Setup, Настройка UI]
topic: android
subtopics: [activity, ui-views]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-activity-lifecycle, c-android-view-system-basics, q-android-project-parts--android--easy, q-cicd-pipeline-setup--android--medium, q-what-is-activity-and-what-is-it-used-for--android--medium, q-what-layout-allows-overlapping-objects--android--easy, q-what-to-do-in-android-project-to-start-drawing-ui-on-screen--android--easy]
created: 2025-10-13
updated: 2025-11-10
tags: [android/activity, android/ui-views, difficulty/easy, layout, manifest, ui]

---
# Вопрос (RU)

> Что нужно сделать в Android-проекте, чтобы начать рисовать UI на экране?

# Question (EN)

> What needs to be done in an Android project to start drawing UI on the screen?

## Ответ (RU)

Минимальные шаги:
- создать `Activity` как точку входа для UI;
- в `onCreate()` установить UI через `setContentView()` (XML-разметка, программно созданный `View` или Jetpack Compose);
- объявить `Activity` в `AndroidManifest.xml` (для запуска из лаунчера указать `MAIN`/`LAUNCHER` `intent-filter`);
- запустить приложение, после чего система вызовет методы жизненного цикла `Activity`, и UI будет привязан к окну и показан на экране.

### 1. Создание `Activity`

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Устанавливаем UI здесь
        setContentView(R.layout.activity_main)
    }
}
```

### 2. XML-разметка

```xml
<!-- res/layout/activity_main.xml -->
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:gravity="center">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello, Android!"
        android:textSize="24sp" />

    <Button
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Click Me" />
</LinearLayout>
```

### 3. Регистрация В `AndroidManifest.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.myapp">

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/Theme.MyApp">

        <!-- Главная Activity — точка входа из лаунчера -->
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <!-- MAIN/LAUNCHER делает Activity точкой входа приложения с домашнего экрана -->
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

Примечание: любая `Activity` может отображать UI, если она запущена (например, через явный `Intent`); настройка `MAIN/LAUNCHER` нужна именно для запуска приложения с домашнего экрана.

### Альтернатива: Программный UI (без XML)

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Создаем UI программно
        val textView = TextView(this).apply {
            text = "Hello, Android!"
            textSize = 24f
            gravity = Gravity.CENTER
        }

        setContentView(textView)
    }
}
```

### Подход С Jetpack Compose

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            MaterialTheme {
                Column(
                    modifier = Modifier.fillMaxSize(),
                    verticalArrangement = Arrangement.Center,
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "Hello, Compose!",
                        fontSize = 24.sp
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    Button(onClick = { /* действие */ }) {
                        Text("Click Me")
                    }
                }
            }
        }
    }
}
```

### Пример Структуры Проекта

```text
app/
 src/
    main/
        java/com/example/myapp/
           MainActivity.kt
        res/
           layout/
              activity_main.xml
           values/
              strings.xml
              themes.xml
           mipmap/
               ic_launcher.png
        AndroidManifest.xml
 build.gradle
```

### Жизненный Цикл UI

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // 1. Activity создана
        setContentView(R.layout.activity_main)
        // 2. UI привязан к окну
    }

    override fun onStart() {
        super.onStart()
        // 3. Activity видна пользователю
    }

    override fun onResume() {
        super.onResume()
        // 4. Activity на переднем плане, возможна работа с UI
    }
}
```

### Ключевые Моменты

- `Activity` — типичная точка входа для UI.
- `setContentView()` (или `setContent {}` в Compose) привязывает UI к окну `Activity`.
- `onCreate()` — место, где обычно инициализируется UI.
- `AndroidManifest.xml` описывает структуру приложения и задает стартовую `Activity`.
- `MAIN/LAUNCHER` `intent-filter` помечает `Activity` как точку входа с домашнего экрана.

## Answer (EN)

To display UI on the screen in Android, you typically need to:
- Create an `Activity` as an entry point for the UI.
- In `onCreate()`, set the UI via `setContentView()` (XML layout, programmatic `View`, or Jetpack Compose).
- Declare the `Activity` in `AndroidManifest.xml` (with a `MAIN`/`LAUNCHER` intent filter if it should start from the launcher).
- Run the app so the system calls the `Activity` lifecycle methods and attaches the UI to the window.

### Minimum Steps

1. Create an `Activity`.
2. `Set` the content view (XML, programmatic `View`, or Compose).
3. Register the `Activity` in `AndroidManifest.xml` (`MAIN`/`LAUNCHER` for entry from launcher if needed).
4. Run the app.

### 1. Create `Activity`

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Set UI here
        setContentView(R.layout.activity_main)
    }
}
```

### 2. Create XML Layout

```xml
<!-- res/layout/activity_main.xml -->
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:gravity="center">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello, Android!"
        android:textSize="24sp" />

    <Button
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Click Me" />
</LinearLayout>
```

### 3. Register in `AndroidManifest.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.myapp">

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/Theme.MyApp">

        <!-- Main Activity - Entry Point from Launcher -->
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <!-- MAIN/LAUNCHER intent filter makes it the app entry point from the launcher -->
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

Note: Any `Activity` can show UI if it is started (e.g., via an explicit `Intent`); the `MAIN`/`LAUNCHER` configuration is specifically for launching the app from the home screen.

### Alternative: Programmatic UI (No XML)

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Create UI programmatically
        val textView = TextView(this).apply {
            text = "Hello, Android!"
            textSize = 24f
            gravity = Gravity.CENTER
        }

        setContentView(textView)
    }
}
```

### Jetpack Compose Approach

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            MaterialTheme {
                Column(
                    modifier = Modifier.fillMaxSize(),
                    verticalArrangement = Arrangement.Center,
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "Hello, Compose!",
                        fontSize = 24.sp
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    Button(onClick = { /* action */ }) {
                        Text("Click Me")
                    }
                }
            }
        }
    }
}
```

### Complete Example Project Structure

```text
app/
 src/
    main/
        java/com/example/myapp/
           MainActivity.kt
        res/
           layout/
              activity_main.xml
           values/
              strings.xml
              themes.xml
           mipmap/
               ic_launcher.png
        AndroidManifest.xml
 build.gradle
```

### UI Lifecycle

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // 1. Activity created
        setContentView(R.layout.activity_main)
        // 2. UI attached to window
    }

    override fun onStart() {
        super.onStart()
        // 3. Activity visible to user
    }

    override fun onResume() {
        super.onResume()
        // 4. Activity in foreground, user can interact
    }
}
```

### Key Points

- `Activity` is the typical entry point for UI.
- `setContentView()` (or `setContent {}` in Compose) attaches UI to the `Activity` window.
- `onCreate()` is where the UI is usually initialized.
- `AndroidManifest.xml` declares the app structure and the entry `Activity`.
- The `MAIN`/`LAUNCHER` intent filter marks the starting activity for launching the app from the home screen.

---

## Follow-ups (RU)

- [[c-activity-lifecycle]]
- [[c-android-view-system-basics]]
- [[q-what-is-activity-and-what-is-it-used-for--android--medium]]

## Follow-ups (EN)

- [[c-activity-lifecycle]]
- [[c-android-view-system-basics]]
- [[q-what-is-activity-and-what-is-it-used-for--android--medium]]

## References (RU)

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/)

## References (EN)

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/)

## Related Questions (RU)

### Prerequisites (Easier)
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - ui
- [[q-why-separate-ui-and-business-logic--android--easy]] - ui
- [[q-recyclerview-sethasfixedsize--android--easy]] - ui

### Related (Medium)
- [[q-dagger-build-time-optimization--android--medium]] - ui
- q-rxjava-pagination-recyclerview--android--medium - ui
- [[q-build-optimization-gradle--android--medium]] - ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - ui
- [[q-testing-compose-ui--android--medium]] - ui

### Advanced (Harder)
- [[q-why-fragment-needs-separate-callback-for-ui-creation--android--hard]] - ui

## Related Questions (EN)

### Prerequisites (Easier)
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - ui
- [[q-why-separate-ui-and-business-logic--android--easy]] - ui
- [[q-recyclerview-sethasfixedsize--android--easy]] - ui

### Related (Medium)
- [[q-dagger-build-time-optimization--android--medium]] - ui
- q-rxjava-pagination-recyclerview--android--medium - ui
- [[q-build-optimization-gradle--android--medium]] - ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - ui
- [[q-testing-compose-ui--android--medium]] - ui

### Advanced (Harder)
- [[q-why-fragment-needs-separate-callback-for-ui-creation--android--hard]] - ui
