---
id: 20251012-122711175
title: "What To Do In Android Project To Start Drawing Ui On Screen / Что делать в Android проекте чтобы начать рисовать UI на экране"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-in-what-cases-might-you-need-to-call-commitallowingstateloss--android--hard, q-mvp-pattern--android--medium, q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard]
created: 2025-10-15
tags:
  - android
---
# What needs to be done in Android project to start drawing UI on screen?

# Question (EN)
> What needs to be done in an Android project to start drawing UI on the screen?

# Вопрос (RU)
> Что нужно сделать в Android-проекте, чтобы начать рисовать UI на экране?

---

## Answer (EN)

To start drawing UI on screen in an Android project, you need to follow several fundamental steps:

### 1. Create an Android Project

Use Android Studio to create a new project:
- File → New → New Project
- Select "Empty Activity" or "Empty Compose Activity" template
- Configure project name, package, and minimum SDK

### 2. Method A: Traditional XML-Based UI

#### Step 1: Create XML Layout

Create or edit `res/layout/activity_main.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp">

    <TextView
        android:id="@+id/textView"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello World!"
        android:textSize="24sp" />

    <Button
        android:id="@+id/button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="16dp"
        android:text="Click Me" />

</LinearLayout>
```

#### Step 2: Connect Layout to Activity

In `MainActivity.kt`:

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Connect XML layout to activity
        setContentView(R.layout.activity_main)

        // Access views and set listeners
        val textView = findViewById<TextView>(R.id.textView)
        val button = findViewById<Button>(R.id.button)

        button.setOnClickListener {
            textView.text = "Button clicked!"
        }
    }
}
```

#### Step 3: Run the Application

- Connect device or start emulator
- Click "Run" (green triangle) in Android Studio
- UI will be displayed on screen

### 2. Method B: View Binding (Recommended for XML)

#### Step 1: Enable View Binding

In `build.gradle.kts` (Module: app):

```kotlin
android {
    buildFeatures {
        viewBinding = true
    }
}
```

#### Step 2: Use View Binding in Activity

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Inflate layout using view binding
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Access views directly
        binding.textView.text = "Hello World!"
        binding.button.setOnClickListener {
            binding.textView.text = "Button clicked!"
        }
    }
}
```

### 3. Method C: Jetpack Compose (Modern Approach)

#### Step 1: Enable Compose

In `build.gradle.kts` (Module: app):

```kotlin
android {
    buildFeatures {
        compose = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.3"
    }
}

dependencies {
    implementation(platform("androidx.compose:compose-bom:2024.01.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.activity:activity-compose:1.8.2")
}
```

#### Step 2: Create Composable UI

In `MainActivity.kt`:

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Set composable content
        setContent {
            MaterialTheme {
                MyApp()
            }
        }
    }
}

@Composable
fun MyApp() {
    var text by remember { mutableStateOf("Hello World!") }

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = MaterialTheme.colorScheme.background
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = text,
                style = MaterialTheme.typography.headlineMedium
            )

            Spacer(modifier = Modifier.height(16.dp))

            Button(onClick = {
                text = "Button clicked!"
            }) {
                Text("Click Me")
            }
        }
    }
}

@Preview(showBackground = true)
@Composable
fun PreviewMyApp() {
    MaterialTheme {
        MyApp()
    }
}
```

### 4. Custom Drawing (Canvas)

For custom graphics, create a custom view:

```kotlin
class CustomView(context: Context, attrs: AttributeSet? = null) :
    View(context, attrs) {

    private val paint = Paint().apply {
        color = Color.BLUE
        style = Paint.Style.FILL
        isAntiAlias = true
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        // Draw background
        canvas.drawColor(Color.WHITE)

        // Draw circle
        canvas.drawCircle(
            width / 2f,
            height / 2f,
            200f,
            paint
        )

        // Draw text
        paint.apply {
            color = Color.BLACK
            textSize = 48f
            textAlign = Paint.Align.CENTER
        }
        canvas.drawText(
            "Custom Drawing",
            width / 2f,
            height / 2f + 300f,
            paint
        )
    }
}
```

Use in XML:

```xml
<com.example.app.CustomView
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

Or programmatically:

```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    val customView = CustomView(this)
    setContentView(customView)
}
```

### 5. Complete Example: All Methods Combined

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Choose ONE method:

        // METHOD 1: XML Layout
        // setContentView(R.layout.activity_main)

        // METHOD 2: View Binding
        // val binding = ActivityMainBinding.inflate(layoutInflater)
        // setContentView(binding.root)

        // METHOD 3: Compose
        // setContent {
        //     MyApp()
        // }

        // METHOD 4: Programmatic Views
        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(16.dp, 16.dp, 16.dp, 16.dp)
        }

        val textView = TextView(this).apply {
            text = "Hello World!"
            textSize = 24f
        }

        val button = Button(this).apply {
            text = "Click Me"
            setOnClickListener {
                textView.text = "Button clicked!"
            }
        }

        layout.addView(textView)
        layout.addView(button)

        setContentView(layout)
    }

    private val Int.dp: Int
        get() = (this * resources.displayMetrics.density).toInt()
}
```

### 6. AndroidManifest.xml Configuration

Ensure your activity is declared:

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/Theme.MyApp">

        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

    </application>

</manifest>
```

### 7. Minimal Steps Summary

**For XML-based UI:**
1. Create XML layout file (`activity_main.xml`)
2. Call `setContentView(R.layout.activity_main)` in `onCreate()`
3. Run app

**For Compose UI:**
1. Add Compose dependencies
2. Call `setContent { YourComposable() }` in `onCreate()`
3. Run app

**For Custom Drawing:**
1. Create class extending `View`
2. Override `onDraw(canvas: Canvas)`
3. Set as content view or add to layout

### 8. Essential Activity Lifecycle

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Set content view here - required step
        setContentView(R.layout.activity_main)
        // UI is now ready to be displayed
    }

    override fun onStart() {
        super.onStart()
        // Activity becoming visible
    }

    override fun onResume() {
        super.onResume()
        // Activity in foreground, interactive
    }
}
```

### Key Points

1. **Activity** is the entry point for UI
2. **setContentView()** must be called in `onCreate()`
3. **Layout** can be defined in XML, Compose, or programmatically
4. **Run the app** on emulator or device to see UI
5. **Choose one approach**: XML + View Binding OR Compose (recommended for new projects)

### Common Mistakes

```kotlin
// BAD: Accessing views before setContentView
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    val textView = findViewById<TextView>(R.id.textView) // null!
    setContentView(R.layout.activity_main)
}

// GOOD: Set content view first
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.activity_main)
    val textView = findViewById<TextView>(R.id.textView) // works
}
```

---

## Ответ (RU)

Что нужно сделать в Android-проекте чтобы начать рисовать UI на экране?

Чтобы начать рисовать пользовательский интерфейс (UI) на экране в Android-проекте, необходимо выполнить несколько шагов. Сначала создайте Android-проект в Android Studio с шаблоном «Empty Activity». Затем настройте макет, используя XML-файл для определения структуры интерфейса. Подключите макет к активности с помощью метода setContentView() в Activity классе. Если требуется кастомное рисование, создайте собственный класс, унаследованный от View и переопределите метод onDraw(). Наконец, запустите приложение на эмуляторе или реальном устройстве.

---

## Related Questions

### Prerequisites (Easier)
- [[q-why-separate-ui-and-business-logic--android--easy]] - Ui
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - Ui
- [[q-recyclerview-sethasfixedsize--android--easy]] - Ui

### Related (Medium)
- [[q-dagger-build-time-optimization--android--medium]] - Ui
- q-rxjava-pagination-recyclerview--android--medium - Ui
- [[q-build-optimization-gradle--android--medium]] - Ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Ui
- [[q-testing-compose-ui--android--medium]] - Ui
