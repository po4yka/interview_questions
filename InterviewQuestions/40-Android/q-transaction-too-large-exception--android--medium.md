---
id: "20251015082237318"
title: "Transaction Too Large Exception"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - android
  - android/memory-management
  - binder
  - exceptions
  - intent
  - ipc
  - savedinstancestate
---
# Что такое TransactionTooLargeException?

**English**: What is TransactionTooLargeException?

## Answer (EN)
**TransactionTooLargeException** is an exception that occurs if transmitted data **exceeds the 1MB limit** in Binder.

Most often the error appears when passing large objects through **Intent**, **Bundle**, or **onSaveInstanceState**.

**Binder Transaction Limit:**

```
Binder Transaction Buffer: 1 MB total
Per-process limit shared across all transactions
```

**Common Causes:**

**1. Large Intent Data:**

```kotlin
// - BAD - May cause TransactionTooLargeException
val intent = Intent(this, DetailActivity::class.java)

// Passing large bitmap
val largeBitmap = getBitmapFromCamera()  // e.g., 5 MB
intent.putExtra("image", largeBitmap)  // - CRASH!

startActivity(intent)
```

**Error:**
```
android.os.TransactionTooLargeException: data parcel size 5242880 bytes
```

**2. Large Bundle in Fragment:**

```kotlin
// - BAD
val fragment = MyFragment()
val bundle = Bundle()

// Adding large data
bundle.putSerializable("userList", largeUserList)  // 2 MB
fragment.arguments = bundle  // - CRASH!
```

**3. onSaveInstanceState with Large Data:**

```kotlin
// - BAD
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)

    // Saving large bitmap
    outState.putParcelable("screenshot", largeScreenshot)  // - CRASH!
}
```

**Solutions:**

**1. Pass ID Instead of Object**

```kotlin
// - GOOD - Pass ID, not entire object
val intent = Intent(this, DetailActivity::class.java)
intent.putExtra("user_id", userId)  // Just an Int
startActivity(intent)

// In DetailActivity
val userId = intent.getIntExtra("user_id", -1)
val user = database.getUserById(userId)  // Load from DB
```

**2. Use Persistent Storage**

```kotlin
// - GOOD - Save to file/database
val imageFile = File(cacheDir, "temp_image.jpg")
bitmap.compress(Bitmap.CompressFormat.JPEG, 90, FileOutputStream(imageFile))

val intent = Intent(this, DetailActivity::class.java)
intent.putExtra("image_path", imageFile.absolutePath)
startActivity(intent)

// In DetailActivity
val imagePath = intent.getStringExtra("image_path")
val bitmap = BitmapFactory.decodeFile(imagePath)
```

**3. Use ViewModel for Fragments**

```kotlin
// - GOOD - Share data via ViewModel
class SharedViewModel : ViewModel() {
    val userData = MutableLiveData<List<User>>()
}

// In Activity
class MainActivity : AppCompatActivity() {
    private val sharedViewModel: SharedViewModel by viewModels()

    fun loadFragment() {
        sharedViewModel.userData.value = largeUserList

        val fragment = MyFragment()
        // No bundle needed!
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, fragment)
            .commit()
    }
}

// In Fragment
class MyFragment : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        sharedViewModel.userData.observe(viewLifecycleOwner) { users ->
            // Use data
        }
    }
}
```

**4. Singleton/Application Scope**

```kotlin
// - GOOD - Temporary storage
object DataHolder {
    var tempBitmap: Bitmap? = null
}

// Source Activity
DataHolder.tempBitmap = largeBitmap
startActivity(Intent(this, DetailActivity::class.java))

// Detail Activity
val bitmap = DataHolder.tempBitmap
DataHolder.tempBitmap = null  // Clean up
```

**5. onSaveInstanceState - Save Only Essential Data**

```kotlin
// - GOOD - Save minimal state
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)

    // Only save scroll position, not entire list
    outState.putInt("scroll_position", recyclerView.scrollY)

    // Save ID, not entire object
    outState.putInt("selected_user_id", selectedUser?.id ?: -1)
}

override fun onRestoreInstanceState(savedInstanceState: Bundle) {
    super.onRestoreInstanceState(savedInstanceState)

    val scrollPosition = savedInstanceState.getInt("scroll_position")
    recyclerView.scrollTo(0, scrollPosition)

    val userId = savedInstanceState.getInt("selected_user_id")
    if (userId != -1) {
        selectedUser = database.getUserById(userId)
    }
}
```

**Size Calculation:**

```kotlin
// Check bundle size
fun Bundle.getSize(): Int {
    val parcel = Parcel.obtain()
    parcel.writeBundle(this)
    val size = parcel.dataSize()
    parcel.recycle()
    return size
}

val bundle = Bundle()
bundle.putSerializable("data", myData)

val sizeInBytes = bundle.getSize()
val sizeInKB = sizeInBytes / 1024
val sizeInMB = sizeInKB / 1024

if (sizeInMB > 0.5) {
    Log.w("Bundle", "Bundle size too large: $sizeInMB MB")
}
```

**Best Practices:**

| - Don't | - Do |
|----------|-------|
| Pass large Bitmaps | Pass file path or ID |
| Pass entire lists | Pass query params to reload |
| Save screenshots in Bundle | Save to temp file |
| Serialize large objects | Use database/file storage |
| Pass full objects | Pass IDs and reload |

**Alternative: Content URIs**

```kotlin
// - GOOD - Use ContentUri for images
val imageUri = FileProvider.getUriForFile(
    context,
    "$packageName.fileprovider",
    imageFile
)

val intent = Intent(this, DetailActivity::class.java)
intent.data = imageUri
intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
startActivity(intent)

// In DetailActivity
val imageUri = intent.data
val bitmap = contentResolver.openInputStream(imageUri)?.use {
    BitmapFactory.decodeStream(it)
}
```

**Summary:**

- **Limit**: 1 MB Binder transaction buffer
- **Causes**: Large Intent/Bundle/savedInstanceState data
- **Solutions**:
  - Pass IDs, not objects
  - Use persistent storage (files/database)
  - Use ViewModel for fragments
  - Use singleton for temporary data
  - Save only essential state

## Ответ (RU)
**TransactionTooLargeException** — это исключение, которое возникает если передаваемые данные превышают лимит **1MB в Binder**.

Чаще всего ошибка появляется при передаче больших объектов через **Intent**, **Bundle**, **onSaveInstanceState**.

