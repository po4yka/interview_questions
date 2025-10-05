---
id: 202510031417006
title: "What is Activity and what is it used for"
question_ru: "Что такое Activity и для чего это используется"
question_en: "Что такое Activity и для чего это используется"
topic: android
moc: moc-android
status: draft
difficulty: easy
tags:
  - activity
  - android lifecycle
  - android/activity
  - lifecycle
  - easy_kotlin
  - lang/ru
source: https://t.me/easy_kotlin/63
---

# What is Activity and what is it used for

## English Answer

**Activity** is an application component that provides a user interface (UI) with which users can interact to perform various actions, such as dialing a phone number, viewing photos, sending email, etc. Each Activity represents a single screen with a user interface. If you think of an application as a book, then an Activity would be one page of that book.

### Key Purposes

#### 1. Providing User Interface
Activity is the foundation for presenting UI to users:

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Set the user interface layout
        setContentView(R.layout.activity_main)
    }
}
```

#### 2. User Interaction
Handles user input and interactions:

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Handle button clicks
        findViewById<Button>(R.id.button).setOnClickListener {
            // Respond to user interaction
            handleButtonClick()
        }

        // Handle text input
        findViewById<EditText>(R.id.editText).addTextChangedListener { text ->
            // Respond to text changes
        }
    }
}
```

#### 3. Lifecycle Management
Activity has a well-defined lifecycle that helps manage resources:

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        // Initialize components
    }

    override fun onStart() {
        super.onStart()
        // Activity becoming visible
    }

    override fun onResume() {
        super.onResume()
        // Activity interactive
    }

    override fun onPause() {
        super.onPause()
        // Activity losing focus
    }

    override fun onStop() {
        super.onStop()
        // Activity no longer visible
    }

    override fun onDestroy() {
        super.onDestroy()
        // Clean up resources
    }
}
```

#### 4. Navigation Between Screens
Activities enable navigation between different screens:

```kotlin
// Navigate to another Activity
class MainActivity : AppCompatActivity() {
    private fun navigateToDetails() {
        val intent = Intent(this, DetailsActivity::class.java)
        intent.putExtra("item_id", 123)
        startActivity(intent)
    }
}

// Receive data in destination Activity
class DetailsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_details)

        val itemId = intent.getIntExtra("item_id", -1)
        loadDetails(itemId)
    }
}
```

#### 5. Interaction with Other Components
Activities can interact with other app components:

```kotlin
class MainActivity : AppCompatActivity() {

    // Start a Service
    private fun startBackgroundWork() {
        val intent = Intent(this, MyService::class.java)
        startService(intent)
    }

    // Send a Broadcast
    private fun notifyDataUpdated() {
        val intent = Intent("com.example.DATA_UPDATED")
        sendBroadcast(intent)
    }

    // Query ContentProvider
    private fun loadContacts() {
        contentResolver.query(
            ContactsContract.Contacts.CONTENT_URI,
            null, null, null, null
        )?.use { cursor ->
            // Process contacts
        }
    }
}
```

### Activity Characteristics

| Aspect | Description |
|--------|-------------|
| **Single Screen** | Represents one screen in the app |
| **Has Lifecycle** | onCreate, onStart, onResume, onPause, onStop, onDestroy |
| **Can Have UI** | Usually has a layout (can be without UI too) |
| **Entry Point** | Can be launched by system or other apps |
| **Independent** | Each Activity is relatively independent |

### Types of Activities

#### 1. Main/Launcher Activity
The entry point of the application:

```xml
<activity
    android:name=".MainActivity"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.MAIN"/>
        <category android:name="android.intent.category.LAUNCHER"/>
    </intent-filter>
</activity>
```

#### 2. Detail Activity
Shows detailed information:

```kotlin
class ProductDetailActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_product_detail)

        val productId = intent.getStringExtra("product_id")
        displayProductDetails(productId)
    }
}
```

#### 3. Dialog Activity
Activity styled as a dialog:

```xml
<activity
    android:name=".DialogActivity"
    android:theme="@style/Theme.AppCompat.Dialog"/>
```

#### 4. Settings Activity
For app settings (often uses PreferenceActivity):

```kotlin
class SettingsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        supportFragmentManager
            .beginTransaction()
            .replace(android.R.id.content, SettingsFragment())
            .commit()
    }
}
```

### Complete Activity Example

```kotlin
class ProfileActivity : AppCompatActivity() {

    private lateinit var binding: ActivityProfileBinding
    private val viewModel: ProfileViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityProfileBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Setup toolbar
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

        // Get user ID from intent
        val userId = intent.getStringExtra("user_id") ?: return

        // Observe ViewModel data
        viewModel.loadUser(userId)
        viewModel.user.observe(this) { user ->
            displayUser(user)
        }

        // Setup click listeners
        binding.editButton.setOnClickListener {
            navigateToEditProfile()
        }
    }

    private fun displayUser(user: User) {
        binding.nameTextView.text = user.name
        binding.emailTextView.text = user.email
        Glide.with(this)
            .load(user.avatarUrl)
            .into(binding.avatarImageView)
    }

    private fun navigateToEditProfile() {
        val intent = Intent(this, EditProfileActivity::class.java)
        intent.putExtra("user_id", viewModel.user.value?.id)
        startActivity(intent)
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            android.R.id.home -> {
                onBackPressed()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }
}
```

### Activity Declaration in Manifest

Every Activity must be declared in AndroidManifest.xml:

```xml
<manifest>
    <application>
        <!-- Main launcher Activity -->
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>

        <!-- Other Activities -->
        <activity
            android:name=".ProfileActivity"
            android:label="@string/profile_title"
            android:parentActivityName=".MainActivity"/>

        <activity
            android:name=".SettingsActivity"
            android:label="@string/settings_title"/>
    </application>
</manifest>
```

### Common Activity Patterns

#### 1. Single Activity Architecture
Modern approach using Fragments:

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var navController: NavController

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        navController = navHostFragment.navController

        // All screens are Fragments, one Activity hosts them all
    }
}
```

#### 2. Multiple Activities
Traditional approach:

```kotlin
// Each screen is a separate Activity
class ListActivity : AppCompatActivity()
class DetailActivity : AppCompatActivity()
class EditActivity : AppCompatActivity()
```

### Best Practices

1. **Keep Activities lightweight** - Use ViewModels for business logic
2. **Handle configuration changes** - Use ViewModel to survive rotations
3. **Save and restore state** - Use onSaveInstanceState/onRestoreInstanceState
4. **Don't hold static references** - Avoid memory leaks
5. **Use appropriate launch modes** - singleTop, singleTask, etc.

## Russian Answer

**Activity** — это компонент приложения, который предоставляет пользовательский интерфейс (UI), с которым пользователи могут взаимодействовать для выполнения различных действий, таких как набор номера телефона, просмотр фотографий, отправка электронной почты и т.д. Каждая активность представляет собой один экран с пользовательским интерфейсом. Если представить приложение как книгу, то активность будет одной страницей этой книги.

### Основное назначение

1. **Предоставление интерфейса пользователя**: Activity отвечает за отображение UI элементов на экране

2. **Взаимодействие с пользователем**: Обработка нажатий, ввода текста, жестов и других действий пользователя

3. **Управление жизненным циклом**: Activity имеет четко определенный жизненный цикл (onCreate, onStart, onResume, onPause, onStop, onDestroy), который позволяет правильно управлять ресурсами

4. **Переход между экранами**: Activity служит точкой перехода между различными экранами приложения

5. **Взаимодействие с другими компонентами приложения**: Activity может запускать сервисы, отправлять широковещательные сообщения, работать с провайдерами контента

Каждая Activity должна быть объявлена в файле AndroidManifest.xml, чтобы система знала о её существовании и могла её запустить.
