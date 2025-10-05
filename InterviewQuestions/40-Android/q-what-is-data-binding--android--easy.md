---
id: 202510031409
title: Have you used Data Binding / Использовал Data Binding
aliases: []

# Classification
topic: android
subtopics: [android, ui, data-binding]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/504
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-android
related:
  - c-android-data-binding
  - c-android-view-binding

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [data binding, difficulty/easy, easy_kotlin, lang/ru, android/data-binding, android/ui]
---

# Question (EN)
> Have you used Data Binding

# Вопрос (RU)
> Использовал Data Binding

---

## Answer (EN)

**Data Binding** is a library in Android that allows you to bind user interface (UI) components directly to data sources in your app, reducing the amount of boilerplate code needed to synchronize UI with data.

### Key Features

1. **Eliminates findViewById()**: Direct view references
2. **Two-way binding**: Automatic UI updates when data changes
3. **Expression language**: Logic in XML layouts
4. **Observable data**: Automatic UI updates
5. **Null safety**: Built-in null checks

### Setup

```gradle
// build.gradle (Module)
android {
    buildFeatures {
        dataBinding true
    }
}
```

### Basic Usage

```xml
<!-- activity_main.xml -->
<layout xmlns:android="http://schemas.android.com/apk/res/android">
    <data>
        <variable
            name="user"
            type="com.example.User" />
    </data>

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:orientation="vertical">

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="@{user.name}" />

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="@{String.valueOf(user.age)}" />
    </LinearLayout>
</layout>
```

```kotlin
// Data class
data class User(val name: String, val age: Int)

// Activity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val binding: ActivityMainBinding = DataBindingUtil.setContentView(
            this, R.layout.activity_main
        )

        val user = User("John Doe", 30)
        binding.user = user
    }
}
```

### Observable Data

```kotlin
class User : BaseObservable() {
    @get:Bindable
    var name: String = ""
        set(value) {
            field = value
            notifyPropertyChanged(BR.name)
        }

    @get:Bindable
    var age: Int = 0
        set(value) {
            field = value
            notifyPropertyChanged(BR.age)
        }
}

// UI automatically updates when properties change
user.name = "Jane Doe"  // TextView updates automatically
```

### Two-Way Data Binding

```xml
<EditText
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:text="@={viewModel.searchQuery}" />
```

```kotlin
class SearchViewModel : ViewModel() {
    val searchQuery = MutableLiveData<String>()

    init {
        searchQuery.value = ""
    }
}
```

### Binding Expressions

```xml
<!-- String concatenation -->
<TextView
    android:text="@{`Hello, ` + user.name}" />

<!-- Null coalescing -->
<TextView
    android:text="@{user.name ?? `Unknown`}" />

<!-- Conditionals -->
<TextView
    android:visibility="@{user.isActive ? View.VISIBLE : View.GONE}" />

<!-- Method calls -->
<Button
    android:onClick="@{() -> viewModel.onButtonClick()}" />
```

### With ViewModel

```kotlin
class UserViewModel : ViewModel() {
    val userName = MutableLiveData<String>()
    val userAge = MutableLiveData<Int>()

    fun loadUser() {
        userName.value = "John Doe"
        userAge.value = 30
    }
}
```

```xml
<layout>
    <data>
        <variable
            name="viewModel"
            type="com.example.UserViewModel" />
    </data>

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="match_parent">

        <TextView
            android:text="@{viewModel.userName}" />

        <TextView
            android:text="@{String.valueOf(viewModel.userAge)}" />
    </LinearLayout>
</layout>
```

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding
    private lateinit var viewModel: UserViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = DataBindingUtil.setContentView(this, R.layout.activity_main)
        viewModel = ViewModelProvider(this)[UserViewModel::class.java]

        binding.lifecycleOwner = this
        binding.viewModel = viewModel

        viewModel.loadUser()
    }
}
```

### Data Binding vs View Binding

| Feature | Data Binding | View Binding |
|---------|-------------|--------------|
| Null safety | ✅ | ✅ |
| Type safety | ✅ | ✅ |
| Boilerplate | Less | Minimal |
| Two-way binding | ✅ | ❌ |
| Expression language | ✅ | ❌ |
| Build time | Slower | Faster |
| Complexity | Higher | Lower |

### Advantages

1. **Less boilerplate code**
2. **Type-safe view access**
3. **Automatic UI updates**
4. **Better separation of concerns**
5. **Improved readability**

### Disadvantages

1. **Increased build time**
2. **Harder to debug**
3. **Logic in XML** (can be anti-pattern)
4. **Learning curve**
5. **Not recommended by Google** (prefer View Binding)

### Modern Alternative: View Binding

```kotlin
// Simpler and recommended
class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Direct, type-safe view access
        binding.textView.text = "Hello"
        binding.button.setOnClickListener {
            // Handle click
        }
    }
}
```

## Ответ (RU)

Это библиотека в Android, которая позволяет связывать компоненты пользовательского интерфейса (UI) напрямую с источниками данных, снижая количество шаблонного кода

---

## Follow-ups
- What are the performance implications of Data Binding?
- When should you use Data Binding vs View Binding?
- How do you handle complex logic with Data Binding expressions?

## References
- [[c-android-data-binding]]
- [[c-android-view-binding]]
- [[c-android-viewmodel]]
- [[c-android-livedata]]
- [[moc-android]]

## Related Questions
- [[q-viewmodel-pattern--android--easy]]
- [[q-how-to-choose-layout-for-fragment--android--easy]]
