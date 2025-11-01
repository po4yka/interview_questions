---
id: 20251012-122711173
title: "UI Setup in Android Project / Настройка UI в проекте Android"
aliases: [UI Setup, Настройка UI]
topic: android
subtopics: [activity, ui-views]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-activity-lifecycle, c-layouts, q-what-is-activity-and-what-is-it-used-for--android--medium, q-what-layout-allows-overlapping-objects--android--easy]
created: 2025-10-13
updated: 2025-10-31
tags: [android/activity, android/ui-views, ui, activity, layout, manifest, difficulty/easy]
---

# What needs to be done in Android project to start drawing UI on screen?

# Вопрос (RU)

Что нужно сделать в Android-проекте чтобы начать рисовать UI на экране

## Answer (EN)
To display UI on screen in Android, you need: (1) Create an Activity as entry point, (2) Set content view with XML layout or programmatic View, (3) Declare the Activity in AndroidManifest.xml as LAUNCHER. When the device launches, the system calls `onCreate()` and UI is attached to screen.

### Minimum Steps

1. **Create an Activity**
2. **Set content view** (XML or programmatic)
3. **Register in AndroidManifest.xml**
4. **Run the app**

### 1. Create Activity

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

### 3. Register in AndroidManifest.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.myapp">

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/Theme.MyApp">

        <!-- Main Activity - Entry Point -->
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <!-- LAUNCHER intent filter makes it the app entry point -->
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

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

```
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

- **Activity** is the entry point for UI
- **setContentView()** attaches UI to screen
- **onCreate()** is where UI is initialized
- **AndroidManifest.xml** declares the app structure
- **LAUNCHER** intent filter marks the starting activity

## Ответ (RU)

Минимальные шаги: создать Activity как точку входа для UI установить content view в виде XML или программно созданного View убедиться что в манифесте указана MainActivity как LAUNCHER при запуске устройства система вызывает onCreate() и в этот момент UI привязывается к экрану

---

## Related Questions

### Prerequisites (Easier)
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - Ui
- [[q-why-separate-ui-and-business-logic--android--easy]] - Ui
- [[q-recyclerview-sethasfixedsize--android--easy]] - Ui

### Related (Medium)
- [[q-dagger-build-time-optimization--android--medium]] - Ui
- q-rxjava-pagination-recyclerview--android--medium - Ui
- [[q-build-optimization-gradle--android--medium]] - Ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Ui
- [[q-testing-compose-ui--android--medium]] - Ui

### Advanced (Harder)
- [[q-why-fragment-needs-separate-callback-for-ui-creation--android--hard]] - Ui
