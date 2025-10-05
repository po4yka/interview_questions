---
id: 20251003141817
title: "What is Activity and what is it used for"
date: 2025-10-03
tags:
  - android
  - activity
  - lifecycle
  - basics
difficulty: easy
topic: android
moc: moc-android
status: draft
source: https://t.me/easy_kotlin/947
---

# What is Activity and what is it used for

## Question (RU)
Что такое Activity и для чего это используется

## Question (EN)
What is Activity and what is it used for

## Answer (EN)

Activity is a fundamental Android component that represents a single screen with a user interface. It serves as an entry point for user interaction and is the main building block for creating interactive Android applications.

### What is Activity

An Activity is a class that:
- Provides a window for UI elements
- Manages user interactions
- Has a defined lifecycle
- Can contain Fragments
- Is registered in AndroidManifest.xml

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Set up UI components
        val button = findViewById<Button>(R.id.button)
        button.setOnClickListener {
            // Handle user interaction
            navigateToNextScreen()
        }
    }

    private fun navigateToNextScreen() {
        val intent = Intent(this, DetailActivity::class.java)
        startActivity(intent)
    }
}
```

### Core Purposes of Activity

#### 1. User Interface Presentation

```kotlin
class ProductListActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_product_list)

        // Display list of products
        val recyclerView = findViewById<RecyclerView>(R.id.recyclerView)
        recyclerView.adapter = ProductAdapter(getProducts())
    }
}
```

#### 2. User Interaction Handling

```kotlin
class FormActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_form)

        // Handle button clicks
        findViewById<Button>(R.id.submitButton).setOnClickListener {
            submitForm()
        }

        // Handle text input
        findViewById<EditText>(R.id.emailInput).addTextChangedListener { text ->
            validateEmail(text.toString())
        }
    }
}
```

#### 3. Lifecycle Management

```kotlin
class MediaActivity : AppCompatActivity() {

    private lateinit var mediaPlayer: MediaPlayer

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_media)
        mediaPlayer = MediaPlayer()
    }

    override fun onStart() {
        super.onStart()
        // Activity becoming visible
        mediaPlayer.prepare()
    }

    override fun onResume() {
        super.onResume()
        // Activity in foreground
        mediaPlayer.start()
    }

    override fun onPause() {
        super.onPause()
        // Activity losing focus
        mediaPlayer.pause()
    }

    override fun onDestroy() {
        super.onDestroy()
        // Activity being destroyed
        mediaPlayer.release()
    }
}
```

#### 4. Screen Navigation

```kotlin
class NavigationActivity : AppCompatActivity() {

    fun navigateToProfile() {
        val intent = Intent(this, ProfileActivity::class.java)
        startActivity(intent)
    }

    fun navigateWithData() {
        val intent = Intent(this, DetailActivity::class.java).apply {
            putExtra("user_id", 123)
            putExtra("user_name", "John")
        }
        startActivity(intent)
    }

    fun navigateForResult() {
        val intent = Intent(this, SettingsActivity::class.java)
        settingsLauncher.launch(intent)
    }

    private val settingsLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            // Handle result
        }
    }
}
```

#### 5. Component Interaction

```kotlin
class IntegrationActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_integration)

        // Start Service
        startService(Intent(this, DownloadService::class.java))

        // Send Broadcast
        sendBroadcast(Intent("com.example.CUSTOM_ACTION"))

        // Query ContentProvider
        val uri = Uri.parse("content://com.example.provider/users")
        contentResolver.query(uri, null, null, null, null)
    }
}
```

### Activity Lifecycle

```
[Not Created]
     ↓
onCreate() ← Activity created
     ↓
onStart() ← Becoming visible
     ↓
onResume() ← Interactive (foreground)
     ↓
[Running]
     ↓
onPause() ← Losing focus
     ↓
onStop() ← No longer visible
     ↓
onDestroy() ← Being destroyed
     ↓
[Destroyed]
```

### Activity Declaration in Manifest

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

    <application>
        <!-- Main/Launcher Activity -->
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- Regular Activity -->
        <activity
            android:name=".DetailActivity"
            android:parentActivityName=".MainActivity" />

        <!-- Activity with configuration -->
        <activity
            android:name=".FullscreenActivity"
            android:theme="@style/Theme.Fullscreen"
            android:screenOrientation="landscape" />
    </application>
</manifest>
```

### Types of Activities by Purpose

#### 1. Main/Launcher Activity
Entry point of the app:
```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        // App starts here
    }
}
```

#### 2. Detail/Secondary Activity
Shows detailed information:
```kotlin
class DetailActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val itemId = intent.getIntExtra("item_id", -1)
        displayItemDetails(itemId)
    }
}
```

#### 3. Settings Activity
Configuration screen:
```kotlin
class SettingsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        supportFragmentManager
            .beginTransaction()
            .replace(R.id.settings, SettingsFragment())
            .commit()
    }
}
```

#### 4. Form/Input Activity
Data entry:
```kotlin
class CreateAccountActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_create_account)
        setupFormValidation()
    }
}
```

### Activity vs Fragment

| Aspect | Activity | Fragment |
|--------|----------|----------|
| UI Container | Full screen | Part of screen |
| Manifest | Required | Not required |
| Lifecycle | Independent | Tied to host Activity |
| Navigation | Intent | FragmentManager |
| Reusability | Limited | High |
| Creation cost | High | Lower |

### Common Activity Patterns

#### Single Activity Architecture
```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // All navigation via Fragments
        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        val navController = navHostFragment.navController
    }
}
```

#### Multiple Activities
```kotlin
// Traditional approach
class MainActivity : AppCompatActivity() { }
class DetailActivity : AppCompatActivity() { }
class SettingsActivity : AppCompatActivity() { }
```

### Activity Communication

```kotlin
// Activity A → Activity B
class ActivityA : AppCompatActivity() {
    fun sendData() {
        val intent = Intent(this, ActivityB::class.java)
        intent.putExtra("message", "Hello from A")
        startActivity(intent)
    }
}

// Activity B receives data
class ActivityB : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val message = intent.getStringExtra("message")
    }
}
```

### Best Practices

1. **Keep onCreate() lightweight**: Avoid heavy operations
2. **Use Fragments**: For complex UI and reusability
3. **Handle configuration changes**: Save/restore state properly
4. **Follow single responsibility**: One purpose per Activity
5. **Declare in Manifest**: All Activities must be registered
6. **Memory management**: Clean up resources in onDestroy()

## Answer (RU)
`Activity` в Android — это компонент приложения, который представляет один экран пользовательского интерфейса и отвечает за взаимодействие с пользователем. Каждое приложение может содержать несколько Activity, и они управляются системой Android в рамках жизненного цикла. Activity управляет пользовательским вводом, отображением данных и переходами между экранами. Это основной блок для создания интерактивных приложений на Android.

## Related Topics
- Activity lifecycle
- Fragment vs Activity
- Intent and navigation
- AndroidManifest.xml
- AppCompatActivity
