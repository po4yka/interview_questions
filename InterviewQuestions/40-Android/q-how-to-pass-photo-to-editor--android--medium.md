---
topic: android
tags:
  - android
  - intent
  - fileprovider
  - bitmap
  - image-processing
difficulty: medium
status: reviewed
---

# How to pass a photo to an editor?

**Russian**: Как бы передавал фотографию в редактор

## Answer

Passing a photo to an editor depends on whether it's an external app or an internal editor within your app.

### 1. External Editor (Another App)

Use Intent with `ACTION_EDIT`:

```kotlin
fun openPhotoInExternalEditor(context: Context, photoUri: Uri) {
    val intent = Intent(Intent.ACTION_EDIT).apply {
        setDataAndType(photoUri, "image/*")
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
    }

    try {
        context.startActivity(Intent.createChooser(intent, "Choose editor"))
    } catch (e: ActivityNotFoundException) {
        Toast.makeText(context, "No image editor found", Toast.LENGTH_SHORT).show()
    }
}

// Usage
val photoUri = FileProvider.getUriForFile(
    context,
    "${context.packageName}.fileprovider",
    photoFile
)
openPhotoInExternalEditor(context, photoUri)
```

### 2. Internal Editor (Your App)

#### Method A: Pass URI via Intent

```kotlin
// Open editor activity
fun openInternalEditor(context: Context, photoFile: File) {
    val uri = FileProvider.getUriForFile(
        context,
        "${context.packageName}.fileprovider",
        photoFile
    )

    val intent = Intent(context, PhotoEditorActivity::class.java).apply {
        putExtra(EXTRA_PHOTO_URI, uri.toString())
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    }

    context.startActivity(intent)
}

// PhotoEditorActivity
class PhotoEditorActivity : AppCompatActivity() {

    companion object {
        const val EXTRA_PHOTO_URI = "photo_uri"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_photo_editor)

        val uriString = intent.getStringExtra(EXTRA_PHOTO_URI)
        val uri = uriString?.let { Uri.parse(it) }

        uri?.let {
            loadImage(it)
        }
    }

    private fun loadImage(uri: Uri) {
        // Load image from URI
        val bitmap = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            ImageDecoder.decodeBitmap(ImageDecoder.createSource(contentResolver, uri))
        } else {
            MediaStore.Images.Media.getBitmap(contentResolver, uri)
        }

        imageView.setImageBitmap(bitmap)
    }
}
```

#### Method B: Pass Bitmap via Intent (Small Images Only)

```kotlin
fun openEditorWithBitmap(context: Context, bitmap: Bitmap) {
    // Compress bitmap
    val stream = ByteArrayOutputStream()
    bitmap.compress(Bitmap.CompressFormat.PNG, 100, stream)
    val byteArray = stream.toByteArray()

    // WARNING: Bitmaps have size limit (~1MB for Intents)
    if (byteArray.size < 1_000_000) {
        val intent = Intent(context, PhotoEditorActivity::class.java).apply {
            putExtra("PHOTO_BYTES", byteArray)
        }
        context.startActivity(intent)
    } else {
        // Use file-based approach instead
        Toast.makeText(context, "Image too large for direct transfer", Toast.LENGTH_SHORT).show()
    }
}

// Receive in editor
class PhotoEditorActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val byteArray = intent.getByteArrayExtra("PHOTO_BYTES")
        byteArray?.let {
            val bitmap = BitmapFactory.decodeByteArray(it, 0, it.size)
            imageView.setImageBitmap(bitmap)
        }
    }
}
```

#### Method C: Save to Temp File and Pass Path

```kotlin
fun openEditorWithTempFile(context: Context, bitmap: Bitmap) {
    // Save to temp file
    val tempFile = File(context.cacheDir, "temp_edit_${System.currentTimeMillis()}.jpg")
    FileOutputStream(tempFile).use { out ->
        bitmap.compress(Bitmap.CompressFormat.JPEG, 90, out)
    }

    // Pass file URI
    val uri = FileProvider.getUriForFile(
        context,
        "${context.packageName}.fileprovider",
        tempFile
    )

    val intent = Intent(context, PhotoEditorActivity::class.java).apply {
        putExtra("PHOTO_URI", uri.toString())
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    }

    context.startActivity(intent)
}
```

### 3. Complete Example with FileProvider

#### AndroidManifest.xml

```xml
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

    <activity android:name=".PhotoEditorActivity" />
</application>
```

#### res/xml/file_paths.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<paths>
    <cache-path name="shared_images" path="images/" />
    <files-path name="app_images" path="images/" />
    <external-files-path name="external_images" path="images/" />
</paths>
```

#### PhotoManager.kt

```kotlin
class PhotoManager(private val context: Context) {

    fun openPhotoEditor(photoFile: File) {
        val uri = FileProvider.getUriForFile(
            context,
            "${context.packageName}.fileprovider",
            photoFile
        )

        val intent = Intent(context, PhotoEditorActivity::class.java).apply {
            putExtra(PhotoEditorActivity.EXTRA_PHOTO_URI, uri.toString())
            putExtra(PhotoEditorActivity.EXTRA_PHOTO_PATH, photoFile.absolutePath)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
        }

        context.startActivity(intent)
    }

    fun savePhotoToCache(bitmap: Bitmap): File {
        val imagesDir = File(context.cacheDir, "images")
        imagesDir.mkdirs()

        val imageFile = File(imagesDir, "photo_${System.currentTimeMillis()}.jpg")
        FileOutputStream(imageFile).use { out ->
            bitmap.compress(Bitmap.CompressFormat.JPEG, 90, out)
        }

        return imageFile
    }
}
```

#### PhotoEditorActivity.kt

```kotlin
class PhotoEditorActivity : AppCompatActivity() {

    companion object {
        const val EXTRA_PHOTO_URI = "photo_uri"
        const val EXTRA_PHOTO_PATH = "photo_path"
    }

    private lateinit var originalBitmap: Bitmap
    private var currentBitmap: Bitmap? = null
    private var photoPath: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_photo_editor)

        photoPath = intent.getStringExtra(EXTRA_PHOTO_PATH)
        val uriString = intent.getStringExtra(EXTRA_PHOTO_URI)
        val uri = uriString?.let { Uri.parse(it) }

        uri?.let {
            loadImage(it)
        }

        setupEditorControls()
    }

    private fun loadImage(uri: Uri) {
        try {
            originalBitmap = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                ImageDecoder.decodeBitmap(ImageDecoder.createSource(contentResolver, uri))
            } else {
                @Suppress("DEPRECATION")
                MediaStore.Images.Media.getBitmap(contentResolver, uri)
            }

            currentBitmap = originalBitmap.copy(originalBitmap.config, true)
            imageView.setImageBitmap(currentBitmap)

        } catch (e: Exception) {
            Toast.makeText(this, "Error loading image", Toast.LENGTH_SHORT).show()
            finish()
        }
    }

    private fun setupEditorControls() {
        btnRotate.setOnClickListener {
            currentBitmap = rotateBitmap(currentBitmap!!, 90f)
            imageView.setImageBitmap(currentBitmap)
        }

        btnCrop.setOnClickListener {
            // Implement crop functionality
        }

        btnFilter.setOnClickListener {
            // Implement filter functionality
        }

        btnSave.setOnClickListener {
            saveEditedImage()
        }

        btnCancel.setOnClickListener {
            finish()
        }
    }

    private fun rotateBitmap(bitmap: Bitmap, degrees: Float): Bitmap {
        val matrix = Matrix().apply { postRotate(degrees) }
        return Bitmap.createBitmap(
            bitmap,
            0,
            0,
            bitmap.width,
            bitmap.height,
            matrix,
            true
        )
    }

    private fun saveEditedImage() {
        currentBitmap?.let { bitmap ->
            photoPath?.let { path ->
                try {
                    FileOutputStream(path).use { out ->
                        bitmap.compress(Bitmap.CompressFormat.JPEG, 90, out)
                    }

                    setResult(RESULT_OK, Intent().apply {
                        putExtra("edited_path", path)
                    })
                    finish()

                } catch (e: Exception) {
                    Toast.makeText(this, "Error saving image", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        currentBitmap?.recycle()
        if (currentBitmap != originalBitmap) {
            originalBitmap.recycle()
        }
    }
}
```

### 4. From Network (Byte Array)

```kotlin
// Downloading image from server
suspend fun downloadAndEdit(imageUrl: String) {
    withContext(Dispatchers.IO) {
        val response = apiService.downloadImage(imageUrl)
        val byteArray = response.bytes()

        withContext(Dispatchers.Main) {
            // Save to temp file
            val tempFile = File(context.cacheDir, "downloaded_image.jpg")
            tempFile.writeBytes(byteArray)

            // Open editor
            val uri = FileProvider.getUriForFile(
                context,
                "${context.packageName}.fileprovider",
                tempFile
            )

            openEditor(uri)
        }
    }
}
```

### 5. Jetpack Compose Approach

```kotlin
@Composable
fun PhotoEditScreen(photoUri: Uri) {
    val context = LocalContext.current
    var bitmap by remember { mutableStateOf<Bitmap?>(null) }

    LaunchedEffect(photoUri) {
        withContext(Dispatchers.IO) {
            try {
                val loadedBitmap = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                    ImageDecoder.decodeBitmap(
                        ImageDecoder.createSource(context.contentResolver, photoUri)
                    )
                } else {
                    @Suppress("DEPRECATION")
                    MediaStore.Images.Media.getBitmap(context.contentResolver, photoUri)
                }
                bitmap = loadedBitmap
            } catch (e: Exception) {
                // Handle error
            }
        }
    }

    bitmap?.let {
        PhotoEditor(
            bitmap = it,
            onSave = { editedBitmap ->
                // Save edited bitmap
            },
            onCancel = {
                // Handle cancel
            }
        )
    }
}

@Composable
fun PhotoEditor(
    bitmap: Bitmap,
    onSave: (Bitmap) -> Unit,
    onCancel: () -> Unit
) {
    Column {
        Image(
            bitmap = bitmap.asImageBitmap(),
            contentDescription = "Photo to edit"
        )

        Row {
            Button(onClick = { onSave(bitmap) }) {
                Text("Save")
            }
            Button(onClick = onCancel) {
                Text("Cancel")
            }
        }
    }
}
```

### Best Practices

1. **Use FileProvider** for Android 7.0+ (API 24+)
2. **Grant URI permissions** when sharing with external apps
3. **Handle large images carefully** - don't pass via Intent extras
4. **Use proper image formats** - JPEG for photos, PNG for graphics
5. **Manage memory** - recycle bitmaps when done
6. **Handle errors gracefully** - check if editor app exists
7. **Save to appropriate location** - cache for temp, files for permanent

### Common Pitfalls

```kotlin
// ❌ BAD: Large bitmap via Intent
val bitmap = BitmapFactory.decodeFile(largefile)
intent.putExtra("bitmap", bitmap) // TransactionTooLargeException!

// ✅ GOOD: Use URI
val uri = FileProvider.getUriForFile(context, authority, file)
intent.putExtra("uri", uri.toString())
```

---

## RU (original)

Как бы передавал фотографию в редактор

Передача фото в редактор зависит от типа редактора: 1. Внешний редактор (например, Google Photos, Snapseed). 2. Встроенный редактор внутри приложения. [Contains extensive code examples for both approaches]
