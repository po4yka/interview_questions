---
id: android-257
title: How To Pass Photo To Editor / Как передать фото в редактор
aliases:
- How To Pass Photo To Editor
- Как передать фото в редактор
topic: android
subtopics:
- files-media
- intents-deeplinks
- ui-graphics
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-intent
- c-scoped-storage-security
- q-android-storage-types--android--medium
- q-fileprovider-secure-sharing--android--medium
- q-what-are-intents-for--android--medium
created: 2025-10-15
updated: 2025-10-30
sources: []
tags:
- android/files-media
- android/intents-deeplinks
- android/ui-graphics
- difficulty/medium
- image-processing
---

# Вопрос (RU)

Как передать фотографию в редактор — внутри приложения и во внешнее приложение?

# Question (EN)

How to pass a photo to an editor — both within your app and to an external app?

## Ответ (RU)

Передача фотографии зависит от того, внешний это редактор (другое приложение) или внутренний (ваше приложение).

### 1. Внешний Редактор

Используйте `Intent` с `ACTION_EDIT`:

```kotlin
fun openExternalEditor(context: Context, photoUri: Uri) {
    val intent = Intent(Intent.ACTION_EDIT).apply {
        setDataAndType(photoUri, "image/*")
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
    }

    // ✅ Проверка наличия редактора
    try {
        context.startActivity(Intent.createChooser(intent, "Выберите редактор"))
    } catch (e: ActivityNotFoundException) {
        // ❌ Редактор не найден
    }
}
```

### 2. Внутренний Редактор

**Вариант A: Передача URI через `Intent`** (РЕКОМЕНДУЕТСЯ)

```kotlin
fun openInternalEditor(context: Context, photoFile: File) {
    val uri = FileProvider.getUriForFile(
        context,
        "${context.packageName}.fileprovider",
        photoFile
    )

    val intent = Intent(context, PhotoEditorActivity::class.java).apply {
        putExtra("PHOTO_URI", uri.toString())
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    }
    context.startActivity(intent)
}
```

**Вариант B: ByteArray** (только для маленьких изображений < 1MB)

```kotlin
// ❌ ПЛОХО: Большой bitmap через Intent
val bitmap = BitmapFactory.decodeFile(largeFile)
intent.putExtra("bitmap", bitmap) // TransactionTooLargeException!

// ✅ ХОРОШО: Проверка размера
val stream = ByteArrayOutputStream()
bitmap.compress(Bitmap.CompressFormat.PNG, 100, stream)
val bytes = stream.toByteArray()

if (bytes.size < 1_000_000) {
    intent.putExtra("PHOTO_BYTES", bytes)
} else {
    // Используйте вариант A
}
```

### 3. FileProvider Setup

**AndroidManifest.xml:**
```xml
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="${applicationId}.fileprovider"
    android:exported="false"
    android:grantUriPermissions="true">
    <meta-data
        android:name="android.support.FILE_PROVIDER_PATHS"
        android:resource="@xml/file_paths" />
</provider>
```

**res/xml/file_paths.xml:**
```xml
<paths>
    <cache-path name="shared_images" path="images/" />
    <files-path name="app_images" path="images/" />
</paths>
```

### 4. PhotoEditorActivity

```kotlin
class PhotoEditorActivity : AppCompatActivity() {

    private var bitmap: Bitmap? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val uriString = intent.getStringExtra("PHOTO_URI")
        val uri = uriString?.let { Uri.parse(it) }

        uri?.let { loadImage(it) }
    }

    private fun loadImage(uri: Uri) {
        bitmap = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            ImageDecoder.decodeBitmap(ImageDecoder.createSource(contentResolver, uri))
        } else {
            @Suppress("DEPRECATION")
            MediaStore.Images.Media.getBitmap(contentResolver, uri)
        }
        imageView.setImageBitmap(bitmap)
    }

    override fun onDestroy() {
        super.onDestroy()
        // ✅ Освобождение памяти
        bitmap?.recycle()
    }
}
```

### 5. Jetpack Compose

```kotlin
@Composable
fun PhotoEditorScreen(photoUri: Uri) {
    val context = LocalContext.current
    var bitmap by remember { mutableStateOf<Bitmap?>(null) }

    LaunchedEffect(photoUri) {
        withContext(Dispatchers.IO) {
            bitmap = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                ImageDecoder.decodeBitmap(
                    ImageDecoder.createSource(context.contentResolver, photoUri)
                )
            } else {
                @Suppress("DEPRECATION")
                MediaStore.Images.Media.getBitmap(context.contentResolver, photoUri)
            }
        }
    }

    bitmap?.let {
        Image(
            bitmap = it.asImageBitmap(),
            contentDescription = "Редактируемое фото"
        )
    }
}
```

### Лучшие Практики

1. **Используйте FileProvider** для Android 7.0+ (обязательно)
2. **Предоставляйте разрешения URI** для внешних приложений
3. **Не передавайте большие bitmap** через `Intent` extras (лимит ~1MB)
4. **Освобождайте память** — `bitmap.recycle()` в `onDestroy()`
5. **Сохраняйте временные файлы** в `cacheDir`
6. **Обрабатывайте ошибки** — проверяйте наличие редактора

## Answer (EN)

Passing a photo depends on whether it's an external editor (another app) or internal (your app).

### 1. External Editor

Use `Intent` with `ACTION_EDIT`:

```kotlin
fun openExternalEditor(context: Context, photoUri: Uri) {
    val intent = Intent(Intent.ACTION_EDIT).apply {
        setDataAndType(photoUri, "image/*")
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
    }

    // ✅ Check editor exists
    try {
        context.startActivity(Intent.createChooser(intent, "Choose editor"))
    } catch (e: ActivityNotFoundException) {
        // ❌ No editor found
    }
}
```

### 2. Internal Editor

**Option A: Pass URI via `Intent`** (RECOMMENDED)

```kotlin
fun openInternalEditor(context: Context, photoFile: File) {
    val uri = FileProvider.getUriForFile(
        context,
        "${context.packageName}.fileprovider",
        photoFile
    )

    val intent = Intent(context, PhotoEditorActivity::class.java).apply {
        putExtra("PHOTO_URI", uri.toString())
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    }
    context.startActivity(intent)
}
```

**Option B: ByteArray** (only for small images < 1MB)

```kotlin
// ❌ BAD: Large bitmap via Intent
val bitmap = BitmapFactory.decodeFile(largeFile)
intent.putExtra("bitmap", bitmap) // TransactionTooLargeException!

// ✅ GOOD: Check size
val stream = ByteArrayOutputStream()
bitmap.compress(Bitmap.CompressFormat.PNG, 100, stream)
val bytes = stream.toByteArray()

if (bytes.size < 1_000_000) {
    intent.putExtra("PHOTO_BYTES", bytes)
} else {
    // Use Option A instead
}
```

### 3. FileProvider Setup

**AndroidManifest.xml:**
```xml
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="${applicationId}.fileprovider"
    android:exported="false"
    android:grantUriPermissions="true">
    <meta-data
        android:name="android.support.FILE_PROVIDER_PATHS"
        android:resource="@xml/file_paths" />
</provider>
```

**res/xml/file_paths.xml:**
```xml
<paths>
    <cache-path name="shared_images" path="images/" />
    <files-path name="app_images" path="images/" />
</paths>
```

### 4. PhotoEditorActivity

```kotlin
class PhotoEditorActivity : AppCompatActivity() {

    private var bitmap: Bitmap? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val uriString = intent.getStringExtra("PHOTO_URI")
        val uri = uriString?.let { Uri.parse(it) }

        uri?.let { loadImage(it) }
    }

    private fun loadImage(uri: Uri) {
        bitmap = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            ImageDecoder.decodeBitmap(ImageDecoder.createSource(contentResolver, uri))
        } else {
            @Suppress("DEPRECATION")
            MediaStore.Images.Media.getBitmap(contentResolver, uri)
        }
        imageView.setImageBitmap(bitmap)
    }

    override fun onDestroy() {
        super.onDestroy()
        // ✅ Free memory
        bitmap?.recycle()
    }
}
```

### 5. Jetpack Compose

```kotlin
@Composable
fun PhotoEditorScreen(photoUri: Uri) {
    val context = LocalContext.current
    var bitmap by remember { mutableStateOf<Bitmap?>(null) }

    LaunchedEffect(photoUri) {
        withContext(Dispatchers.IO) {
            bitmap = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                ImageDecoder.decodeBitmap(
                    ImageDecoder.createSource(context.contentResolver, photoUri)
                )
            } else {
                @Suppress("DEPRECATION")
                MediaStore.Images.Media.getBitmap(context.contentResolver, photoUri)
            }
        }
    }

    bitmap?.let {
        Image(
            bitmap = it.asImageBitmap(),
            contentDescription = "Photo to edit"
        )
    }
}
```

### Best Practices

1. **Use FileProvider** for Android 7.0+ (mandatory)
2. **Grant URI permissions** for external apps
3. **Don't pass large bitmaps** via `Intent` extras (limit ~1MB)
4. **Free memory** — call `bitmap.recycle()` in `onDestroy()`
5. **Save temp files** to `cacheDir`
6. **Handle errors** — check if editor exists

## Follow-ups

1. What happens if FileProvider authority doesn't match the manifest?
2. How to handle photo rotation metadata (EXIF orientation)?
3. What's the memory overhead of loading large images directly vs using BitmapFactory.Options?
4. How to implement undo/redo for image editing operations?
5. When should you use MediaStore vs FileProvider for sharing images?

## References

- Android FileProvider Guide: https://developer.android.com/reference/androidx/core/content/FileProvider
- Sharing Files Documentation: https://developer.android.com/training/secure-file-sharing
- `Intent` Documentation: https://developer.android.com/reference/android/content/`Intent`

## Related Questions

### Prerequisites / Concepts

- [[c-intent]]
- [[c-scoped-storage-security]]


### Prerequisites
- [[q-what-are-intents-for--android--medium]] — Understanding `Intent` basics
- [[q-android-storage-types--android--medium]] — Storage options in Android

### Related
- [[q-fileprovider-secure-sharing--android--medium]] — FileProvider secure file sharing
- [[q-how-to-implement-a-photo-editor-as-a-separate-component--android--easy]] — Photo editor architecture
- [[q-encrypted-file-storage--android--medium]] — Secure image storage

### Advanced
- Image optimization and memory management for large photos
- Custom `ContentProvider` for complex file sharing scenarios
- Implementing image filters and transformations efficiently
