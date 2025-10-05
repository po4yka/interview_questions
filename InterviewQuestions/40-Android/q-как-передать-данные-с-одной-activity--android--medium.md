---
id: 20251003141808
title: "How to pass data from one Activity to another"
date: 2025-10-03
tags:
  - android
  - activity
  - intent
  - data-passing
difficulty: medium
topic: android
moc: moc-android
status: draft
source: https://t.me/easy_kotlin/686
---

# How to pass data from one Activity to another

## Question (RU)
Как передать данные с одной Activity на другую

## Question (EN)
How to pass data from one Activity to another

## Answer (EN)

Data can be passed between Activities in Android using several methods, with Intent extras being the most common approach.

### 1. Intent Extras (Primitive Types)

Pass simple data types using `putExtra()`:

```kotlin
// Sending Activity
class FirstActivity : AppCompatActivity() {
    fun navigateToSecond() {
        val intent = Intent(this, SecondActivity::class.java).apply {
            putExtra("user_name", "John Doe")
            putExtra("user_age", 25)
            putExtra("is_premium", true)
            putExtra("user_balance", 99.99)
        }
        startActivity(intent)
    }
}

// Receiving Activity
class SecondActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val userName = intent.getStringExtra("user_name")
        val userAge = intent.getIntExtra("user_age", 0)
        val isPremium = intent.getBooleanExtra("is_premium", false)
        val balance = intent.getDoubleExtra("user_balance", 0.0)
    }
}
```

### 2. Intent with Bundle

Group related data using Bundle:

```kotlin
// Sending Activity
class FirstActivity : AppCompatActivity() {
    fun sendDataWithBundle() {
        val bundle = Bundle().apply {
            putString("name", "Alice")
            putInt("age", 30)
            putStringArrayList("hobbies", arrayListOf("Reading", "Coding"))
        }

        val intent = Intent(this, SecondActivity::class.java)
        intent.putExtras(bundle)
        startActivity(intent)
    }
}

// Receiving Activity
class SecondActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        intent.extras?.let { bundle ->
            val name = bundle.getString("name")
            val age = bundle.getInt("age")
            val hobbies = bundle.getStringArrayList("hobbies")
        }
    }
}
```

### 3. Parcelable Objects (Recommended)

Pass complex objects efficiently:

```kotlin
// Data class implementing Parcelable
@Parcelize
data class User(
    val id: Int,
    val name: String,
    val email: String,
    val address: Address
) : Parcelable

@Parcelize
data class Address(
    val street: String,
    val city: String
) : Parcelable

// Sending Activity
class FirstActivity : AppCompatActivity() {
    fun sendUser() {
        val user = User(
            id = 1,
            name = "Bob",
            email = "bob@example.com",
            address = Address("123 Main St", "New York")
        )

        val intent = Intent(this, SecondActivity::class.java)
        intent.putExtra("user_object", user)
        startActivity(intent)
    }
}

// Receiving Activity
class SecondActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val user = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            intent.getParcelableExtra("user_object", User::class.java)
        } else {
            @Suppress("DEPRECATION")
            intent.getParcelableExtra("user_object")
        }

        user?.let {
            // Use user object
        }
    }
}
```

### 4. Serializable Objects (Less Efficient)

Alternative to Parcelable (slower):

```kotlin
data class Product(
    val id: Int,
    val name: String,
    val price: Double
) : Serializable

// Sending
val product = Product(1, "Laptop", 999.99)
intent.putExtra("product", product)

// Receiving
val product = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
    intent.getSerializableExtra("product", Product::class.java)
} else {
    @Suppress("DEPRECATION")
    intent.getSerializableExtra("product") as? Product
}
```

### 5. Shared ViewModel (Activity Scope)

Share data between Activities using shared ViewModel:

```kotlin
// Shared ViewModel
class SharedDataViewModel : ViewModel() {
    private val _userData = MutableLiveData<User>()
    val userData: LiveData<User> = _userData

    fun setUser(user: User) {
        _userData.value = user
    }
}

// First Activity
class FirstActivity : AppCompatActivity() {
    private val sharedViewModel: SharedDataViewModel by viewModels()

    fun saveAndNavigate() {
        sharedViewModel.setUser(User(1, "Charlie", "charlie@example.com"))
        startActivity(Intent(this, SecondActivity::class.java))
    }
}

// Second Activity
class SecondActivity : AppCompatActivity() {
    private val sharedViewModel: SharedDataViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        sharedViewModel.userData.observe(this) { user ->
            // Use shared data
        }
    }
}
```

### 6. startActivityForResult (Deprecated) / Activity Result API

Get data back from launched Activity:

```kotlin
// Modern approach - Activity Result API
class FirstActivity : AppCompatActivity() {

    private val launcher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            val returnedData = result.data?.getStringExtra("result_key")
        }
    }

    fun launchSecondActivity() {
        val intent = Intent(this, SecondActivity::class.java)
        intent.putExtra("request_data", "Send this to second activity")
        launcher.launch(intent)
    }
}

class SecondActivity : AppCompatActivity() {
    fun returnResult() {
        val resultIntent = Intent().apply {
            putExtra("result_key", "Data from second activity")
        }
        setResult(RESULT_OK, resultIntent)
        finish()
    }
}
```

### 7. Persistent Storage (Large Data)

For large datasets, use persistent storage:

```kotlin
// Use SharedPreferences, Room, or DataStore
class FirstActivity : AppCompatActivity() {
    fun saveLargeData() {
        // Save to database
        lifecycleScope.launch {
            database.userDao().insert(user)
        }

        // Pass only ID to next Activity
        val intent = Intent(this, SecondActivity::class.java)
        intent.putExtra("user_id", userId)
        startActivity(intent)
    }
}

class SecondActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val userId = intent.getIntExtra("user_id", -1)
        lifecycleScope.launch {
            val user = database.userDao().getUserById(userId)
            // Use loaded data
        }
    }
}
```

### Comparison Table

| Method | Performance | Data Size | Complexity | Survives Process Death |
|--------|-------------|-----------|------------|------------------------|
| Intent Extras | Fast | Small | Low | No |
| Parcelable | Fast | Medium | Medium | No |
| Serializable | Slow | Medium | Low | No |
| ViewModel | Fast | Any | Medium | No |
| Persistent Storage | Medium | Large | High | Yes |

### Best Practices

1. **Use Parcelable over Serializable**: Better performance
2. **Limit data size**: Intent extras limited to ~500KB
3. **Type safety**: Use constants for keys
4. **Handle null values**: Always provide defaults
5. **Large data**: Use persistent storage + ID passing

```kotlin
// Constants for type safety
object IntentKeys {
    const val USER_ID = "user_id"
    const val USER_NAME = "user_name"
}

// Usage
intent.putExtra(IntentKeys.USER_ID, userId)
val userId = intent.getIntExtra(IntentKeys.USER_ID, -1)
```

## Answer (RU)
В Android передача данных между Activity осуществляется через механизм Intent. Intent — это объект, который позволяет передавать данные и запускать компоненты, такие как Activity, Service и BroadcastReceiver. Передача данных с одной Activity на другую: 1. Создание Intent и добавление данных - В первой Activity создайте Intent и добавьте данные, которые хотите передать, используя методы putExtra. 2 Получение данных во второй Activity - Во второй Activity получите Intent, который запустил эту Activity, и извлеките данные из него. Передача объектов (Parcelable): Если вам нужно передать сложные объекты, вы можете использовать интерфейс Parcelable.

## Related Topics
- Intent mechanism
- Parcelable vs Serializable
- Activity Result API
- Bundle size limitations
- ViewModel sharing
