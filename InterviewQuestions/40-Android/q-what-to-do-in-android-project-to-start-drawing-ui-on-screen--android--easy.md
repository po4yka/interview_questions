---
id: 20251012-122711176
title: "What To Do In Android Project To Start Drawing Ui On Screen / Что делать в Android проекте чтобы начать рисовать UI на экране"
topic: android
difficulty: easy
status: draft
moc: moc-android
related: [q-sparsearray-optimization--android--medium, q-compose-performance-optimization--android--hard, q-how-to-pass-parameters-to-fragment--android--easy]
created: 2025-10-15
tags: [languages, difficulty/easy]
---

# Что нужно сделать в Android-проекте чтобы начать рисовать UI на экране?

# Question (EN)
> What needs to be done in an Android project to start drawing UI on the screen?

# Вопрос (RU)
> Что нужно сделать в Android-проекте, чтобы начать рисовать UI на экране?

---

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

---

## Ответ (RU)

Чтобы отобразить UI на экране в Android, необходимо: (1) Создать Activity как точку входа, (2) Установить content view с помощью XML layout или программно созданного View, (3) Объявить Activity в AndroidManifest.xml как LAUNCHER. При запуске приложения система вызывает `onCreate()` и UI прикрепляется к экрану.

### Минимальные шаги

1. **Создать Activity**
2. **Установить content view** (XML или программно)
3. **Зарегистрировать в AndroidManifest.xml**
4. **Запустить приложение**

### 1. Создание Activity

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Установить UI здесь
        setContentView(R.layout.activity_main)
    }
}
```

### 2. Создание XML Layout

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

### 3. Регистрация в AndroidManifest.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.myapp">

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/Theme.MyApp">

        <!-- Main Activity - Точка входа -->
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <!-- LAUNCHER intent filter делает её точкой входа приложения -->
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

### Альтернатива: Программный UI (Без XML)

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Создание UI программно
        val textView = TextView(this).apply {
            text = "Hello, Android!"
            textSize = 24f
            gravity = Gravity.CENTER
        }

        setContentView(textView)
    }
}
```

### Подход с Jetpack Compose

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

### Жизненный цикл UI

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // 1. Activity создана
        setContentView(R.layout.activity_main)
        // 2. UI прикреплён к окну
    }

    override fun onStart() {
        super.onStart()
        // 3. Activity видна пользователю
    }

    override fun onResume() {
        super.onResume()
        // 4. Activity на переднем плане, пользователь может взаимодействовать
    }
}
```

### Ключевые моменты

- **Activity** — это точка входа для UI
- **setContentView()** прикрепляет UI к экрану
- **onCreate()** — место, где инициализируется UI
- **AndroidManifest.xml** объявляет структуру приложения
- **LAUNCHER** intent filter отмечает стартовую activity

### Резюме

Для отображения UI в Android необходимо создать Activity, установить content view через `setContentView()` в методе `onCreate()`, и зарегистрировать Activity в AndroidManifest.xml с intent-filter LAUNCHER. При запуске приложения Android система автоматически создаёт Activity и отображает указанный UI на экране.

---

## Related Questions

### Related (Easy)
- [[q-why-separate-ui-and-business-logic--android--easy]] - Ui
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - Ui
- [[q-recyclerview-sethasfixedsize--android--easy]] - Ui

### Advanced (Harder)
- [[q-dagger-build-time-optimization--android--medium]] - Ui
- q-rxjava-pagination-recyclerview--android--medium - Ui
- [[q-build-optimization-gradle--android--medium]] - Ui
