---
id: android-364
title: "Android UI Drawing Setup / Подготовка UI к рисованию"
aliases: [Android UI Setup, Подготовка UI]
topic: android
subtopics: [activity, ui-views]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-activity-lifecycle, q-what-is-activity-and-what-is-it-used-for--android--medium, q-what-needs-to-be-done-in-android-project-to-start-drawing-ui-on-screen--android--easy]
created: 2025-10-15
updated: 2025-11-11
tags: [android/activity, android/ui-views, difficulty/medium]

date created: Saturday, November 1st 2025, 12:47:09 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---
# Вопрос (RU)
> Что нужно сделать в Android-проекте, чтобы начать рисовать UI на экране?

# Question (EN)
> What needs to be done in an Android project to start drawing UI on the screen?

---

## Ответ (RU)

Чтобы начать рисовать UI на экране в Android-проекте, нужно выполнить несколько базовых шагов.

### 1. Создать Android-проект

Создайте новый проект в Android Studio:
- File → New → New Project
- Выберите шаблон "Empty `Activity`" или "Empty Compose `Activity`"
- Укажите имя проекта, пакет и минимальный SDK

### 2. Метод A: Классический UI На XML

#### Шаг 1: Создать XML-разметку

Создайте или отредактируйте `res/layout/activity_main.xml`:

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

#### Шаг 2: Подключить Разметку К `Activity`

В `MainActivity.kt`:

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Подключаем XML-разметку к Activity
        setContentView(R.layout.activity_main)

        // Находим View и вешаем обработчики
        val textView = findViewById<TextView>(R.id.textView)
        val button = findViewById<Button>(R.id.button)

        button.setOnClickListener {
            textView.text = "Button clicked!"
        }
    }
}
```

#### Шаг 3: Запустить Приложение

- Подключить устройство или запустить эмулятор
- Нажать "Run" (зелёный треугольник) в Android Studio
- UI отобразится на экране

### 3. Метод B: `View` Binding (удобный Доступ К `View`)

#### Шаг 1: Включить `View` Binding

В `build.gradle.kts` (Module: app):

```kotlin
android {
    buildFeatures {
        viewBinding = true
    }
}
```

#### Шаг 2: Использовать `View` Binding В `Activity`

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Инициализируем binding и устанавливаем корневой layout
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Доступ к View напрямую через binding
        binding.textView.text = "Hello World!"
        binding.button.setOnClickListener {
            binding.textView.text = "Button clicked!"
        }
    }
}
```

### 4. Метод C: Jetpack Compose (современный подход)

#### Шаг 1: Включить Compose

В `build.gradle.kts` (Module: app):

```kotlin
android {
    buildFeatures {
        compose = true
    }

    composeOptions {
        // Укажите актуальную версию kotlinCompilerExtensionVersion
        kotlinCompilerExtensionVersion = "1.5.3" // пример значения
    }
}

dependencies {
    // Используйте актуальную версию BOM; значение ниже приведено как пример
    implementation(platform("androidx.compose:compose-bom:2024.01.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.activity:activity-compose:1.8.2")
}
```

#### Шаг 2: Создать UI На Compose

В `MainActivity.kt`:

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Вместо setContentView устанавливаем Compose-контент
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

### 5. Кастомное Рисование (Canvas)

Для собственного рисования создайте кастомный `View`:

```kotlin
class CustomView(context: Context, attrs: AttributeSet? = null) :
    View(context, attrs) {

    private val circlePaint = Paint().apply {
        color = Color.BLUE
        style = Paint.Style.FILL
        isAntiAlias = true
    }

    private val textPaint = Paint().apply {
        color = Color.BLACK
        textSize = 48f
        textAlign = Paint.Align.CENTER
        isAntiAlias = true
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        // Фон
        canvas.drawColor(Color.WHITE)

        // Круг
        canvas.drawCircle(
            width / 2f,
            height / 2f,
            200f,
            circlePaint
        )

        // Текст
        canvas.drawText(
            "Custom Drawing",
            width / 2f,
            height / 2f + 300f,
            textPaint
        )
    }
}
```

Использование в XML:

```xml
<com.example.app.CustomView
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

Либо программно:

```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    val customView = CustomView(this)
    setContentView(customView)
}
```

### 6. Пример: Программные `View` (без XML)

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Выбираем ОДИН основной подход для данного экрана.
        // Ниже пример полностью программного создания UI.

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

### 7. Настройка AndroidManifest.xml

Убедитесь, что `Activity` объявлена и имеет корректный MAIN action, если это экран запуска:

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
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

    </application>

</manifest>
```

### 8. Краткое Резюме Шагов

- Для XML UI:
  1. Создать XML-разметку.
  2. В `onCreate()` вызвать `setContentView(R.layout.activity_main)`.
  3. Запустить приложение.

- Для Compose UI:
  1. Включить Compose и добавить зависимости.
  2. В `ComponentActivity` вызвать `setContent { YourComposable() }` (без `setContentView`).
  3. Запустить приложение.

- Для кастомного рисования:
  1. Создать класс, наследующий `View`.
  2. Переопределить `onDraw(Canvas)`.
  3. Использовать этот `View` через `setContentView()` или в XML.

Примечание: Для сложных экранов можно комбинировать подходы (например, встраивать Compose в `View`-иерархию и наоборот), но в типичном случае для одного экрана выбирают один основной способ описания UI.

### 9. Жизненный Цикл `Activity` (основы)

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Для XML / программных View устанавливаем контент здесь
        setContentView(R.layout.activity_main)
    }

    override fun onStart() {
        super.onStart()
        // Activity становится видимой
    }

    override fun onResume() {
        super.onResume()
        // Activity на переднем плане, доступна для взаимодействия
    }
}
```

Ключевые моменты:
1. `Activity` (или хост-`Activity` для Compose) предоставляет окно, в котором рисуется UI.
2. Нужно задать содержимое окна: через `setContentView(...)` для `View`/XML, через `setContent { ... }` для Compose или добавить кастомные `View`.
3. Разметка может быть описана в XML, на Compose или создана программно.
4. Корректная запись в манифесте и запуск на устройстве/эмуляторе обязательны, чтобы UI появился.
5. Для одного экрана обычно выбирают один основной подход (XML + `View` Binding, программные `View` или Compose), при необходимости комбинируя их осознанно.

---

## Answer (EN)

To start drawing UI on screen in an Android project, you need to follow several fundamental steps:

### 1. Create an Android Project

Use Android Studio to create a new project:
- File → New → New Project
- Select "Empty `Activity`" or "Empty Compose `Activity`" template
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

#### Step 2: Connect Layout to `Activity`

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

#### Step 3: Run the `Application`

- Connect device or start emulator
- Click "Run" (green triangle) in Android Studio
- UI will be displayed on screen

### 3. Method B: `View` Binding (XML Convenience)

#### Step 1: Enable `View` Binding

In `build.gradle.kts` (Module: app):

```kotlin
android {
    buildFeatures {
        viewBinding = true
    }
}
```

#### Step 2: Use `View` Binding in `Activity`

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

### 4. Method C: Jetpack Compose (Modern Approach)

#### Step 1: Enable Compose

In `build.gradle.kts` (Module: app):

```kotlin
android {
    buildFeatures {
        compose = true
    }

    composeOptions {
        // Specify an up-to-date kotlinCompilerExtensionVersion
        kotlinCompilerExtensionVersion = "1.5.3" // example value
    }
}

dependencies {
    // Use the latest stable Compose BOM; the version below is an example
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

        // Set composable content instead of setContentView
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

### 5. Custom Drawing (Canvas)

For custom graphics, create a custom view:

```kotlin
class CustomView(context: Context, attrs: AttributeSet? = null) :
    View(context, attrs) {

    private val circlePaint = Paint().apply {
        color = Color.BLUE
        style = Paint.Style.FILL
        isAntiAlias = true
    }

    private val textPaint = Paint().apply {
        color = Color.BLACK
        textSize = 48f
        textAlign = Paint.Align.CENTER
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
            circlePaint
        )

        // Draw text
        canvas.drawText(
            "Custom Drawing",
            width / 2f,
            height / 2f + 300f,
            textPaint
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

### 6. Example: Programmatic Views (Without XML)

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Choose ONE primary approach for this screen.
        // Example below: fully programmatic views.

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

### 7. AndroidManifest.xml Configuration

Ensure your activity is declared and has the correct MAIN action to be launchable:

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
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

    </application>

</manifest>
```

### 8. Minimal Steps Summary

- For XML-based UI:
  1. Create XML layout file (`activity_main.xml`).
  2. In your activity's `onCreate()`, call `setContentView(R.layout.activity_main)`.
  3. Run the app on a device/emulator.

- For Compose UI:
  1. Enable Compose and add dependencies.
  2. In a `ComponentActivity`, call `setContent { YourComposable() }` instead of `setContentView()`.
  3. Run the app.

- For Custom Drawing:
  1. Create a class extending `View`.
  2. Override `onDraw(canvas: Canvas)`.
  3. Use this view via `setContentView()` or in an XML layout.

Note: For more advanced cases you can combine approaches (e.g., host Compose inside a `View`-based screen and vice versa), but typically you choose one primary UI approach per screen.

### 9. Essential `Activity` Lifecycle

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // For XML / programmatic Views: set the content view here
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

Key points:
1. An `Activity` (or other appropriate entry point, e.g. a Compose host activity) provides the window where UI is drawn.
2. You must set the UI content: via `setContentView(...)` for `Views`/XML, by calling `setContent { ... }` for Compose, or by attaching custom views.
3. Layout can be defined in XML, in Compose, or created programmatically.
4. A proper manifest declaration and launch configuration are required to show the UI on device/emulator.
5. Use one primary approach per screen (XML + `View` Binding, programmatic `Views`, or Compose), combining them consciously when needed.

---

## Дополнительные Вопросы (RU)

- [[c-activity-lifecycle]]
- [[q-what-is-activity-and-what-is-it-used-for--android--medium]]
- [[q-what-needs-to-be-done-in-android-project-to-start-drawing-ui-on-screen--android--easy]]

## Follow-ups

- [[c-activity-lifecycle]]
- [[q-what-is-activity-and-what-is-it-used-for--android--medium]]
- [[q-what-needs-to-be-done-in-android-project-to-start-drawing-ui-on-screen--android--easy]]

## Ссылки (RU)

- [`Views`](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)

## References

- [`Views`](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)
