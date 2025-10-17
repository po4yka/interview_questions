---
id: "20251015082237590"
title: "Bundle Data Types / Типы данных Bundle"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [android/data-passing, bundle, data-passing, intent, parcelable, serializable, difficulty/medium]
---
# Что можно положить в Bundle?

# Question (EN)
> What can be put in a Bundle?

# Вопрос (RU)
> Что можно положить в Bundle?

---

## Answer (EN)

You can pass **primitive data types** and **serializable objects** in a Bundle:

1. **Primitives**: `int`, `float`, `boolean`, `double`, `long`, `byte`, `char`, `short`
2. **Strings** and **primitive arrays**
3. **Serializable** or **Parcelable** objects
4. For **large data** (e.g., files), use **references or paths** instead of direct data

---

## Bundle Overview

### What is a Bundle?

A **Bundle** is a key-value container for passing data between Android components (Activities, Fragments, Services).

```kotlin
val bundle = Bundle()
bundle.putString("key", "value")
bundle.putInt("count", 42)
```

---

## Data Types Supported by Bundle

### 1. Primitive Types

```kotlin
val bundle = Bundle()

// Integer types
bundle.putInt("age", 25)
bundle.putLong("id", 123456789L)
bundle.putShort("code", 42)
bundle.putByte("flag", 1)

// Floating-point types
bundle.putFloat("price", 19.99f)
bundle.putDouble("latitude", 37.7749)

// Boolean
bundle.putBoolean("isActive", true)

// Character
bundle.putChar("initial", 'A')
```

**Retrieving:**
```kotlin
val age = bundle.getInt("age")
val price = bundle.getFloat("price")
val isActive = bundle.getBoolean("isActive")
```

---

### 2. Strings

```kotlin
val bundle = Bundle()

bundle.putString("name", "John Doe")
bundle.putString("email", "john@example.com")

// CharSequence (for styled text)
bundle.putCharSequence("styledText", SpannableString("Bold text"))
```

**Retrieving:**
```kotlin
val name = bundle.getString("name")
val email = bundle.getString("email", "default@example.com")  // with default
```

---

### 3. Primitive Arrays

```kotlin
val bundle = Bundle()

bundle.putIntArray("scores", intArrayOf(10, 20, 30))
bundle.putFloatArray("values", floatArrayOf(1.5f, 2.5f, 3.5f))
bundle.putBooleanArray("flags", booleanArrayOf(true, false, true))
bundle.putLongArray("ids", longArrayOf(1L, 2L, 3L))
bundle.putDoubleArray("coords", doubleArrayOf(37.7, -122.4))
bundle.putByteArray("data", byteArrayOf(0x01, 0x02, 0x03))
bundle.putCharArray("chars", charArrayOf('A', 'B', 'C'))
bundle.putShortArray("codes", shortArrayOf(1, 2, 3))
```

**Retrieving:**
```kotlin
val scores = bundle.getIntArray("scores")
val values = bundle.getFloatArray("values")
```

---

### 4. String Arrays and Lists

```kotlin
val bundle = Bundle()

// String array
bundle.putStringArray("names", arrayOf("Alice", "Bob", "Charlie"))

// String ArrayList
bundle.putStringArrayList("tags", arrayListOf("kotlin", "android", "mobile"))

// CharSequence array
bundle.putCharSequenceArray("texts", arrayOf("Text 1", "Text 2"))

// CharSequence ArrayList
bundle.putCharSequenceArrayList("items", arrayListOf("Item 1", "Item 2"))
```

**Retrieving:**
```kotlin
val names = bundle.getStringArray("names")
val tags = bundle.getStringArrayList("tags")
```

---

### 5. Parcelable Objects

**Parcelable** is Android's optimized serialization mechanism (faster than Serializable).

```kotlin
@Parcelize
data class User(
    val id: String,
    val name: String,
    val age: Int
) : Parcelable

val bundle = Bundle()

// Single Parcelable
bundle.putParcelable("user", User("1", "Alice", 25))

// Parcelable array
bundle.putParcelableArray("users", arrayOf(
    User("1", "Alice", 25),
    User("2", "Bob", 30)
))

// Parcelable ArrayList
bundle.putParcelableArrayList("userList", arrayListOf(
    User("1", "Alice", 25),
    User("2", "Bob", 30)
))
```

**Retrieving:**
```kotlin
val user = bundle.getParcelable<User>("user")
val users = bundle.getParcelableArray("users")
val userList = bundle.getParcelableArrayList<User>("userList")

// Android 13+ (Tiramisu) - type-safe
val user = bundle.getParcelable("user", User::class.java)
val userList = bundle.getParcelableArrayList("userList", User::class.java)
```

---

### 6. Serializable Objects

**Serializable** is Java's standard serialization (slower than Parcelable, but simpler).

```kotlin
data class Product(
    val id: String,
    val name: String,
    val price: Double
) : Serializable

val bundle = Bundle()

bundle.putSerializable("product", Product("p1", "Laptop", 999.99))
```

**Retrieving:**
```kotlin
val product = bundle.getSerializable("product") as? Product

// Android 13+ (Tiramisu) - type-safe
val product = bundle.getSerializable("product", Product::class.java)
```

---

### 7. Nested Bundles

```kotlin
val userBundle = Bundle().apply {
    putString("name", "Alice")
    putInt("age", 25)
}

val mainBundle = Bundle()
mainBundle.putBundle("userData", userBundle)
```

**Retrieving:**
```kotlin
val userData = mainBundle.getBundle("userData")
val name = userData?.getString("name")
```

---

### 8. Other Types

```kotlin
val bundle = Bundle()

// Size (Android dimensions)
bundle.putSize("screenSize", Size(1080, 1920))

// SizeF (floating-point size)
bundle.putSizeF("aspectRatio", SizeF(16f, 9f))

// Binder (IPC communication)
bundle.putBinder("service", myBinder)
```

---

## Complete Example: Passing Data Between Activities

### Sender Activity

```kotlin
class MainActivity : AppCompatActivity() {

    private fun navigateToDetails() {
        val user = User("1", "Alice", 25)
        val tags = arrayListOf("kotlin", "android", "developer")

        val intent = Intent(this, DetailsActivity::class.java).apply {
            // Using Bundle explicitly
            val bundle = Bundle()
            bundle.putString("userId", user.id)
            bundle.putParcelable("user", user)
            bundle.putStringArrayList("tags", tags)
            bundle.putBoolean("isVerified", true)
            putExtras(bundle)

            // Or use Intent's put methods (they use Bundle internally)
            // putExtra("userId", user.id)
            // putExtra("user", user)
            // putStringArrayListExtra("tags", tags)
        }

        startActivity(intent)
    }
}
```

---

### Receiver Activity

```kotlin
class DetailsActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_details)

        // Get Bundle from Intent
        val bundle = intent.extras

        bundle?.let {
            val userId = it.getString("userId")
            val user = it.getParcelable<User>("user")
            val tags = it.getStringArrayList("tags")
            val isVerified = it.getBoolean("isVerified")

            Log.d("Details", "User: ${user?.name}, Tags: $tags, Verified: $isVerified")
        }
    }
}
```

---

## Fragment Arguments

```kotlin
class UserFragment : Fragment() {

    companion object {
        fun newInstance(user: User, tags: ArrayList<String>): UserFragment {
            return UserFragment().apply {
                arguments = Bundle().apply {
                    putParcelable("user", user)
                    putStringArrayList("tags", tags)
                    putBoolean("isEditable", true)
                }
            }
        }
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        arguments?.let { bundle ->
            val user = bundle.getParcelable<User>("user")
            val tags = bundle.getStringArrayList("tags")
            val isEditable = bundle.getBoolean("isEditable")

            // Use data
            displayUser(user, tags, isEditable)
        }
    }
}

// Usage
val fragment = UserFragment.newInstance(
    User("1", "Alice", 25),
    arrayListOf("kotlin", "android")
)
```

---

## Limitations and Best Practices

### 1. Size Limit

**Problem:** Bundle has a size limit (~1MB total for Intent).

```kotlin
// BAD: Large bitmap in Bundle
val bitmap = BitmapFactory.decodeResource(resources, R.drawable.large_image)
bundle.putParcelable("image", bitmap)  // May crash with TransactionTooLargeException!
```

**Solution:** Pass references instead:

```kotlin
// GOOD: Pass URI or path
val imageUri = saveImageToCache(bitmap)
bundle.putString("imageUri", imageUri.toString())

// Or use resource ID
bundle.putInt("imageResId", R.drawable.large_image)
```

---

### 2. Use Parcelable over Serializable

**Why Parcelable?**
- **Faster**: 10x faster than Serializable
- **Less memory**: More efficient
- **Android-optimized**: Designed for Android

```kotlin
// GOOD: Parcelable (fast)
@Parcelize
data class User(
    val id: String,
    val name: String
) : Parcelable

// ACCEPTABLE: Serializable (slower, but simpler)
data class User(
    val id: String,
    val name: String
) : Serializable
```

---

### 3. Don't Store Complex Objects

```kotlin
// BAD: Complex objects with heavy state
val bundle = Bundle()
bundle.putSerializable("database", database)  // Database connection
bundle.putParcelable("context", applicationContext)  // Context
bundle.putSerializable("viewModel", viewModel)  // ViewModel
```

**Why bad?**
- Contexts can cause memory leaks
- ViewModels should not be serialized
- Heavy objects exceed size limits

---

### 4. For Large Data, Use Alternative Mechanisms

```kotlin
// GOOD: Save to file and pass path
fun passLargeData(data: ByteArray) {
    val file = File(cacheDir, "large_data.bin")
    file.writeBytes(data)

    val bundle = Bundle()
    bundle.putString("dataPath", file.absolutePath)
}

// GOOD: Use ViewModel for shared data
class SharedViewModel : ViewModel() {
    val largeData = MutableLiveData<Bitmap>()
}

// In Fragment A
sharedViewModel.largeData.value = bitmap

// In Fragment B
sharedViewModel.largeData.observe(viewLifecycleOwner) { bitmap ->
    // Use bitmap
}

// GOOD: Use singleton or dependency injection
object DataHolder {
    var currentImage: Bitmap? = null
}

// Pass only ID
bundle.putInt("imageId", imageId)
```

---

## Summary

**What can be put in Bundle:**

1. **Primitive types**: `int`, `float`, `boolean`, `double`, `long`, `byte`, `char`, `short`
2. **Strings**: `String`, `CharSequence`
3. **Arrays**: Primitive arrays, String arrays
4. **Lists**: `ArrayList<String>`, `ArrayList<Parcelable>`
5. **Parcelable objects**: Custom objects implementing Parcelable (recommended)
6. **Serializable objects**: Custom objects implementing Serializable (slower)
7. **Other**: Nested Bundles, Size, Binder

**Size limit:** ~1MB total (TransactionTooLargeException if exceeded)

**Best practices:**
1. Use **Parcelable** over Serializable (10x faster)
2. For **large data** (images, files), pass **URI or path**
3. For **shared data** between Fragments, use **ViewModel**
4. Don't pass: Contexts, ViewModels, Database connections
5. Don't exceed: 1MB size limit

**Alternatives for large data:**
- File storage + pass path
- ViewModel (shared state)
- Database + pass ID
- ContentProvider + pass URI

---

## Ответ (RU)

В Bundle можно передавать **примитивные типы данных** и **сериализуемые объекты**:

1. **Примитивы**: `int`, `float`, `boolean`, `double`, `long`, `byte`, `char`, `short`
2. **Строки** и **массивы примитивов**
3. **Serializable** или **Parcelable** объекты
4. Для **больших данных** (например, файлов) лучше использовать **ссылки или путь к данным**

**Ограничение размера:** ~1MB (TransactionTooLargeException при превышении)

**Лучшие практики:**
- Используйте Parcelable вместо Serializable (в 10 раз быстрее)
- Для больших данных передавайте URI или путь к файлу
- Для обмена данными между Fragment используйте ViewModel
- Не передавайте Context, ViewModel, соединения с БД

