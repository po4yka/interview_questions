---
topic: android
tags:
  - android
  - android/data-passing
  - content-provider
  - data-passing
  - file-provider
  - intent
  - large-data
  - uri
difficulty: hard
status: draft
---

# Как правильно передать большой объем данных, например картинку, на Activity?

**English**: How to properly pass large data (e.g., an image) between Activities?

## Answer (EN)
**Don't** pass large data through `Intent.putExtra()` or `Bundle`. Instead:

1. **Save data** to file system, cache, or database
2. **Pass only a reference** (URI, file path, ID)
3. **Use mechanisms** like `Uri`, `ContentProvider`, or `FileProvider` for safe access

This prevents **TransactionTooLargeException** (Intent size limit ~1MB).

---

## Problem: Intent Size Limit

### Why You Can't Pass Large Data Directly

```kotlin
// - BAD: Pass bitmap directly
val bitmap = BitmapFactory.decodeResource(resources, R.drawable.large_image)
val intent = Intent(this, ViewImageActivity::class.java)
intent.putExtra("image", bitmap)  // TransactionTooLargeException!
startActivity(intent)
```

**Error:**
```
android.os.TransactionTooLargeException: data parcel size 2048000 bytes
```

**Why?** Intent uses Binder transactions, limited to **~1MB** total size.

---

## Solution 1: File + URI (Recommended)

### Using FileProvider

**Best for:** Passing images, videos, documents between Activities.

---

#### Step 1: Add FileProvider to Manifest

```xml
<!-- AndroidManifest.xml -->
<manifest>
    <application>
        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="${applicationId}.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/file_paths" />
        </provider>
    </application>
</manifest>
```

---

#### Step 2: Define File Paths

```xml
<!-- res/xml/file_paths.xml -->
<?xml version="1.0" encoding="utf-8"?>
<paths>
    <!-- Cache directory -->
    <cache-path name="cache" path="." />

    <!-- Internal storage -->
    <files-path name="files" path="." />

    <!-- External storage -->
    <external-path name="external" path="." />

    <!-- External cache -->
    <external-cache-path name="external_cache" path="." />
</paths>
```

---

#### Step 3: Save and Pass URI

```kotlin
class MainActivity : AppCompatActivity() {

    private fun passLargeImage() {
        // 1. Load bitmap
        val bitmap = BitmapFactory.decodeResource(resources, R.drawable.large_image)

        // 2. Save to cache directory
        val imageFile = File(cacheDir, "shared_image.jpg")
        FileOutputStream(imageFile).use { out ->
            bitmap.compress(Bitmap.CompressFormat.JPEG, 90, out)
        }

        // 3. Get URI via FileProvider
        val imageUri = FileProvider.getUriForFile(
            this,
            "${packageName}.fileprovider",
            imageFile
        )

        // 4. Pass URI via Intent
        val intent = Intent(this, ViewImageActivity::class.java).apply {
            putExtra("imageUri", imageUri.toString())
            // Grant read permission
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }

        startActivity(intent)
    }
}
```

---

#### Step 4: Receive and Display

```kotlin
class ViewImageActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_view_image)

        // 1. Get URI from intent
        val uriString = intent.getStringExtra("imageUri")
        val imageUri = Uri.parse(uriString)

        // 2. Load image from URI
        val imageView = findViewById<ImageView>(R.id.imageView)

        try {
            contentResolver.openInputStream(imageUri)?.use { inputStream ->
                val bitmap = BitmapFactory.decodeStream(inputStream)
                imageView.setImageBitmap(bitmap)
            }
        } catch (e: Exception) {
            Log.e("ViewImage", "Error loading image", e)
        }

        // Or use image loading library
        Glide.with(this)
            .load(imageUri)
            .into(imageView)
    }
}
```

---

## Solution 2: Shared ViewModel

### Using Jetpack ViewModel

**Best for:** Sharing data between Fragments in same Activity, or Activities in single task.

```kotlin
// Shared ViewModel
class SharedImageViewModel : ViewModel() {
    private val _imageBitmap = MutableLiveData<Bitmap?>()
    val imageBitmap: LiveData<Bitmap?> = _imageBitmap

    fun setImage(bitmap: Bitmap) {
        _imageBitmap.value = bitmap
    }

    fun clearImage() {
        _imageBitmap.value = null
    }

    override fun onCleared() {
        super.onCleared()
        // Clean up bitmap
        _imageBitmap.value?.recycle()
    }
}

// Sender Activity
class MainActivity : AppCompatActivity() {

    private val sharedViewModel: SharedImageViewModel by viewModels()

    private fun shareImage() {
        val bitmap = BitmapFactory.decodeResource(resources, R.drawable.large_image)

        // Store in ViewModel
        sharedViewModel.setImage(bitmap)

        // Navigate to viewer (no data in Intent!)
        val intent = Intent(this, ViewImageActivity::class.java)
        startActivity(intent)
    }
}

// Receiver Activity
class ViewImageActivity : AppCompatActivity() {

    private val sharedViewModel: SharedImageViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_view_image)

        val imageView = findViewById<ImageView>(R.id.imageView)

        // Observe image from ViewModel
        sharedViewModel.imageBitmap.observe(this) { bitmap ->
            bitmap?.let {
                imageView.setImageBitmap(it)
            }
        }
    }
}
```

**Limitation:** ViewModel is **cleared** when Activity is destroyed. Use for temporary sharing only.

---

## Solution 3: Database + ID

### Using Room Database

**Best for:** Persistent data, multiple access points.

```kotlin
// Entity
@Entity(tableName = "images")
data class ImageEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val filePath: String,
    val timestamp: Long
)

// DAO
@Dao
interface ImageDao {
    @Insert
    suspend fun insert(image: ImageEntity): Long

    @Query("SELECT * FROM images WHERE id = :id")
    suspend fun getById(id: Long): ImageEntity?

    @Delete
    suspend fun delete(image: ImageEntity)
}

// Sender Activity
class MainActivity : AppCompatActivity() {

    private lateinit var database: ImageDatabase

    private fun passImageViaDatabase() {
        val bitmap = BitmapFactory.decodeResource(resources, R.drawable.large_image)

        lifecycleScope.launch {
            // Save to file
            val imageFile = File(filesDir, "image_${System.currentTimeMillis()}.jpg")
            withContext(Dispatchers.IO) {
                FileOutputStream(imageFile).use { out ->
                    bitmap.compress(Bitmap.CompressFormat.JPEG, 90, out)
                }
            }

            // Save to database
            val imageEntity = ImageEntity(
                filePath = imageFile.absolutePath,
                timestamp = System.currentTimeMillis()
            )
            val imageId = database.imageDao().insert(imageEntity)

            // Pass only ID
            val intent = Intent(this@MainActivity, ViewImageActivity::class.java)
            intent.putExtra("imageId", imageId)
            startActivity(intent)
        }
    }
}

// Receiver Activity
class ViewImageActivity : AppCompatActivity() {

    private lateinit var database: ImageDatabase

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_view_image)

        val imageId = intent.getLongExtra("imageId", -1)

        lifecycleScope.launch {
            val imageEntity = database.imageDao().getById(imageId)

            imageEntity?.let {
                val bitmap = withContext(Dispatchers.IO) {
                    BitmapFactory.decodeFile(it.filePath)
                }

                findViewById<ImageView>(R.id.imageView).setImageBitmap(bitmap)
            }
        }
    }
}
```

---

## Solution 4: Singleton Data Holder

### Using Object or Application Class

**Best for:** Simple temporary sharing, small apps.

```kotlin
// Singleton data holder
object ImageHolder {
    var currentBitmap: Bitmap? = null
    var currentImageUri: Uri? = null

    fun clear() {
        currentBitmap?.recycle()
        currentBitmap = null
        currentImageUri = null
    }
}

// Sender Activity
class MainActivity : AppCompatActivity() {

    private fun shareViaHolder() {
        val bitmap = BitmapFactory.decodeResource(resources, R.drawable.large_image)

        // Store in singleton
        ImageHolder.currentBitmap = bitmap

        // Pass nothing in Intent
        val intent = Intent(this, ViewImageActivity::class.java)
        startActivity(intent)
    }
}

// Receiver Activity
class ViewImageActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_view_image)

        // Get from singleton
        ImageHolder.currentBitmap?.let { bitmap ->
            findViewById<ImageView>(R.id.imageView).setImageBitmap(bitmap)
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        // Clean up when done
        ImageHolder.clear()
    }
}
```

**Warning:** Be careful with memory leaks. Always clean up when done.

---

## Solution 5: ContentProvider

### Custom ContentProvider

**Best for:** Sharing data with other apps, complex data access.

```kotlin
class ImageContentProvider : ContentProvider() {

    companion object {
        const val AUTHORITY = "com.example.app.imageprovider"
        val CONTENT_URI: Uri = Uri.parse("content://$AUTHORITY/images")
    }

    override fun query(
        uri: Uri,
        projection: Array<String>?,
        selection: String?,
        selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? {
        // Return cursor with image data
        return null
    }

    override fun openFile(uri: Uri, mode: String): ParcelFileDescriptor? {
        // Return file descriptor for image
        val imageId = uri.lastPathSegment?.toLongOrNull() ?: return null
        val imageFile = File(context?.filesDir, "image_$imageId.jpg")

        return ParcelFileDescriptor.open(
            imageFile,
            ParcelFileDescriptor.MODE_READ_ONLY
        )
    }

    // Other methods...
}

// Manifest
<provider
    android:name=".ImageContentProvider"
    android:authorities="com.example.app.imageprovider"
    android:exported="true"
    android:grantUriPermissions="true" />

// Usage
val imageUri = Uri.withAppendedPath(
    ImageContentProvider.CONTENT_URI,
    imageId.toString()
)

val intent = Intent(this, ViewImageActivity::class.java)
intent.putExtra("imageUri", imageUri.toString())
intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
startActivity(intent)
```

---

## Comparison

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **File + URI** | - Secure, standard, works across apps | Need FileProvider setup | Images, documents, any files |
| **ViewModel** | - Simple, lifecycle-aware | - Cleared on config change/destroy | Same Activity/task only |
| **Database + ID** | - Persistent, multiple access | Need database setup | Persistent data |
| **Singleton** | - Very simple | - Memory leaks risk | Temporary, small apps |
| **ContentProvider** | - Share with other apps | Complex setup | Cross-app sharing |

---

## Complete Example: Image Sharing Flow

```kotlin
// MainActivity.kt
class MainActivity : AppCompatActivity() {

    private fun shareImage(bitmap: Bitmap) {
        lifecycleScope.launch {
            try {
                // 1. Save to cache
                val imageFile = withContext(Dispatchers.IO) {
                    File(cacheDir, "shared_${System.currentTimeMillis()}.jpg").apply {
                        FileOutputStream(this).use { out ->
                            bitmap.compress(Bitmap.CompressFormat.JPEG, 90, out)
                        }
                    }
                }

                // 2. Get URI
                val imageUri = FileProvider.getUriForFile(
                    this@MainActivity,
                    "${packageName}.fileprovider",
                    imageFile
                )

                // 3. Navigate with URI
                val intent = Intent(this@MainActivity, ViewImageActivity::class.java).apply {
                    putExtra(ViewImageActivity.EXTRA_IMAGE_URI, imageUri.toString())
                    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                }

                startActivity(intent)

            } catch (e: Exception) {
                Log.e("MainActivity", "Error sharing image", e)
                Toast.makeText(this@MainActivity, "Failed to share image", Toast.LENGTH_SHORT).show()
            }
        }
    }
}

// ViewImageActivity.kt
class ViewImageActivity : AppCompatActivity() {

    companion object {
        const val EXTRA_IMAGE_URI = "imageUri"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_view_image)

        val imageView = findViewById<ImageView>(R.id.imageView)
        val uriString = intent.getStringExtra(EXTRA_IMAGE_URI)

        uriString?.let {
            val imageUri = Uri.parse(it)
            loadImage(imageUri, imageView)
        }
    }

    private fun loadImage(uri: Uri, imageView: ImageView) {
        lifecycleScope.launch {
            try {
                val bitmap = withContext(Dispatchers.IO) {
                    contentResolver.openInputStream(uri)?.use { inputStream ->
                        BitmapFactory.decodeStream(inputStream)
                    }
                }

                bitmap?.let {
                    imageView.setImageBitmap(it)
                }

            } catch (e: Exception) {
                Log.e("ViewImage", "Error loading image", e)
                Toast.makeText(this@ViewImageActivity, "Failed to load image", Toast.LENGTH_SHORT).show()
            }
        }
    }
}
```

---

## Best Practices

### 1. Choose the Right Method

```kotlin
// - File + URI: For images, videos, documents
fun shareFile(file: File) {
    val uri = FileProvider.getUriForFile(context, authority, file)
    intent.putExtra("fileUri", uri.toString())
}

// - Database + ID: For persistent structured data
fun shareData(data: MyData) {
    val id = database.insert(data)
    intent.putExtra("dataId", id)
}

// - ViewModel: For temporary sharing in same task
viewModel.setData(largeData)
startActivity(intent)  // No data in Intent
```

---

### 2. Clean Up After Use

```kotlin
// Clean up cached files
override fun onDestroy() {
    super.onDestroy()

    // Delete temporary file
    val imageFile = File(cacheDir, "shared_image.jpg")
    if (imageFile.exists()) {
        imageFile.delete()
    }

    // Clear ViewModel
    sharedViewModel.clearImage()
}
```

---

### 3. Handle Permissions

```kotlin
// Grant URI permission
intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

// For write access
intent.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION)

// Revoke when done
revokeUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION)
```

---

## Summary

**How to pass large data between Activities:**

1. **File + URI (Recommended)**
   - Save data to file
   - Use FileProvider to get URI
   - Pass URI via Intent
   - Grant read permission

2. **ViewModel**
   - Store in shared ViewModel
   - Pass nothing in Intent
   - Access from ViewModel in target Activity

3. **Database + ID**
   - Save data to database
   - Pass only ID via Intent
   - Load from database in target

4. **Singleton**
   - Store in singleton object
   - Pass nothing in Intent
   - Retrieve from singleton

5. **ContentProvider**
   - Create ContentProvider
   - Pass content:// URI
   - Access via ContentResolver

**Key principle:** **Never pass large data directly in Intent/Bundle**. Always pass a **reference** (URI, ID, path).

**Size limit:** Intent/Bundle limited to ~1MB (TransactionTooLargeException if exceeded)

---

## Ответ (RU)
**Не передавайте** большие данные через `Intent.putExtra()` или `Bundle`. Вместо этого:

1. **Сохраните данные** в файловую систему, кэш или базу данных
2. **Передайте только ссылку** (URI, путь к файлу, ID)
3. **Используйте механизмы** вроде `Uri`, `ContentProvider` или `FileProvider` для безопасного доступа

**Рекомендуемый подход - File + URI:**
1. Сохраните изображение в файл
2. Получите URI через FileProvider
3. Передайте URI через Intent с флагом `FLAG_GRANT_READ_URI_PERMISSION`
4. Загрузите изображение из URI в целевой Activity

Это предотвращает ошибку **TransactionTooLargeException** (лимит Intent ~1MB).

