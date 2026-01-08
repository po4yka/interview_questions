---\
id: android-257
title: How To Pass Photo To Editor / Как передать фото в редактор
aliases: [How To Pass Photo To Editor, Как передать фото в редактор]
topic: android
subtopics: [files-media, intents-deeplinks, ui-graphics]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-intent, c-scoped-storage-security, q-android-storage-types--android--medium, q-fileprovider-secure-sharing--android--medium, q-how-to-implement-a-photo-editor-as-a-separate-component--android--easy, q-how-to-pass-data-from-one-fragment-to-another--android--medium, q-how-to-pass-parameters-to-a-fragment--android--easy, q-what-are-intents-for--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/files-media, android/intents-deeplinks, android/ui-graphics, difficulty/medium, image-processing]

---\
# Вопрос (RU)

> Как передать фотографию в редактор — внутри приложения и во внешнее приложение?

# Question (EN)

> How to pass a photo to an editor — both within your app and to an external app?

## Ответ (RU)

Передача фотографии зависит от того, внешний это редактор (другое приложение) или внутренний (ваше приложение).

### 1. Внешний Редактор

Используйте `Intent` с `ACTION_EDIT`:

```kotlin
fun openExternalEditor(context: Context, photoUri: Uri) {
    val intent = Intent(Intent.ACTION_EDIT).apply {
        setDataAndType(photoUri, "image/*")
        // Обычно достаточно READ; WRITE даём, только если ожидаем, что редактор изменит этот Uri
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
    }

    // ✅ Проверка наличия редактора
    try {
        context.startActivity(Intent.createChooser(intent, "Выберите редактор"))
    } catch (e: ActivityNotFoundException) {
        // ❌ Редактор не найден (обработайте ошибку в UI)
    }
}
```

Важно:
- `photoUri` должен быть `content://`-URI (например, от `FileProvider` или `MediaStore`), а не `file://`.
- Если ожидается, что внешний редактор сохранит изменения по этому же URI, убедитесь, что URI ссылается на доступное для записи местоположение и вы выдали `FLAG_GRANT_WRITE_URI_PERMISSION`.

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
        // Лучше передавать Uri как Parcelable, без toString/parsing
        putExtra("PHOTO_URI", uri)
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    }
    context.startActivity(intent)
}
```

**Вариант B: ByteArray** (только для маленьких изображений, безопасный размер заметно меньше предела Binder ~1MB)

```kotlin
// ❌ ПЛОХО: Большой bitmap через Intent
val bitmap = BitmapFactory.decodeFile(largeFile.path)
intent.putExtra("bitmap", bitmap) // Risk: TransactionTooLargeException!

// ✅ ХОРОШО: Проверка размера (примерно, зависит от системы)
val stream = ByteArrayOutputStream()
bitmap.compress(Bitmap.CompressFormat.PNG, 100, stream)
val bytes = stream.toByteArray()

if (bytes.size < 500_000) { // используем консервативный порог
    intent.putExtra("PHOTO_BYTES", bytes)
} else {
    // Используйте вариант A (URI через FileProvider)
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
    <!-- Используйте реальные директории, где вы фактически сохраняете изображения -->
    <cache-path name="shared_images" path="images/" />
    <files-path name="app_images" path="images/" />
</paths>
```

Убедитесь, что:
- `authorities` точно совпадает со значением, используемым в `FileProvider.getUriForFile`.
- Путь файла (`photoFile`) попадает в один из объявленных в `file_paths.xml` путей.

### 4. PhotoEditorActivity

```kotlin
class PhotoEditorActivity : AppCompatActivity() {

    private var bitmap: Bitmap? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val uri: Uri? = intent.getParcelableExtra("PHOTO_URI")
        uri?.let { loadImage(it) }
    }

    private fun loadImage(uri: Uri) {
        // Для реальных приложений стоит использовать downsampling (BitmapFactory.Options)
        // или библиотеку (Glide/Coil/Picasso), чтобы избежать OOM
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
        // ✅ Битмап будет собран GC; явный recycle() нужен только для старых/особых кейсов
        bitmap = null
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
        // Декодируем в фоновом потоке, а результат записываем в state на главном потоке
        val decoded = withContext(Dispatchers.IO) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                ImageDecoder.decodeBitmap(
                    ImageDecoder.createSource(context.contentResolver, photoUri)
                )
            } else {
                @Suppress("DEPRECATION")
                MediaStore.Images.Media.getBitmap(context.contentResolver, photoUri)
            }
        }
        bitmap = decoded
    }

    bitmap?.let {
        Image(
            bitmap = it.asImageBitmap(),
            contentDescription = "Редактируемое фото"
        )
    }
}
```

(Требуется зависимость coroutines и `kotlinx-coroutines-android` для использования `Dispatchers.IO` в Compose.)

### Лучшие Практики

1. Используйте FileProvider для Android 7.0+ (обязательно для передачи файлов между приложениями).
2. Предоставляйте URI-разрешения для внешних приложений через `FLAG_GRANT_READ_URI_PERMISSION` / `FLAG_GRANT_WRITE_URI_PERMISSION` только при необходимости записи.
3. Не передавайте большие bitmap через `Intent` extras — Binder-транзакции ограничены (~1MB), используйте безопасный запас и отдавайте предпочтение URI.
4. Управляйте памятью аккуратно — масштабируйте большие изображения, при необходимости очищайте ссылки; явный `recycle()` нужен редко.
5. Используйте временные файлы в `cacheDir` или аналогичных путях для файлов, которые не должны долго храниться.
6. Обрабатывайте ошибки — проверяйте наличие подходящего редактора и корректность URI/authority.

## Answer (EN)

Passing a photo depends on whether it's an external editor (another app) or internal (your app).

### 1. External Editor

Use `Intent` with `ACTION_EDIT`:

```kotlin
fun openExternalEditor(context: Context, photoUri: Uri) {
    val intent = Intent(Intent.ACTION_EDIT).apply {
        setDataAndType(photoUri, "image/*")
        // Usually READ is enough; grant WRITE only if you expect the editor to modify that Uri
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
    }

    // ✅ Check editor exists
    try {
        context.startActivity(Intent.createChooser(intent, "Choose editor"))
    } catch (e: ActivityNotFoundException) {
        // ❌ No editor found (handle gracefully in UI)
    }
}
```

Important:
- `photoUri` should be a `content://` URI (e.g., from `FileProvider` or `MediaStore`), not `file://`.
- If you expect the external editor to save changes back to the same URI, ensure the URI points to a writable location and that you grant `FLAG_GRANT_WRITE_URI_PERMISSION`.

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
        // Prefer passing Uri as Parcelable rather than String
        putExtra("PHOTO_URI", uri)
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    }
    context.startActivity(intent)
}
```

**Option B: ByteArray** (only for small images; safe size is well below Binder's ~1MB limit)

```kotlin
// ❌ BAD: Large bitmap via Intent
val bitmap = BitmapFactory.decodeFile(largeFile.path)
intent.putExtra("bitmap", bitmap) // Risk: TransactionTooLargeException!

// ✅ GOOD: Check size (approximate, implementation-dependent)
val stream = ByteArrayOutputStream()
bitmap.compress(Bitmap.CompressFormat.PNG, 100, stream)
val bytes = stream.toByteArray()

if (bytes.size < 500_000) { // conservative threshold
    intent.putExtra("PHOTO_BYTES", bytes)
} else {
    // Use Option A (URI via FileProvider)
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
    <!-- Ensure these paths match actual directories where you store images -->
    <cache-path name="shared_images" path="images/" />
    <files-path name="app_images" path="images/" />
</paths>
```

Make sure that:
- The `authorities` value exactly matches what you use in `FileProvider.getUriForFile`.
- The file path (`photoFile`) is inside one of the paths declared in `file_paths.xml`.

### 4. PhotoEditorActivity

```kotlin
class PhotoEditorActivity : AppCompatActivity() {

    private var bitmap: Bitmap? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val uri: Uri? = intent.getParcelableExtra("PHOTO_URI")
        uri?.let { loadImage(it) }
    }

    private fun loadImage(uri: Uri) {
        // In real apps, downsample/scale large images (BitmapFactory.Options)
        // or use an image library (Glide/Coil/Picasso) to avoid OOM
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
        // ✅ Let GC collect the bitmap; explicit recycle() is rarely needed now
        bitmap = null
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
        // Decode off the main thread; assign to state on the main thread
        val decoded = withContext(Dispatchers.IO) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                ImageDecoder.decodeBitmap(
                    ImageDecoder.createSource(context.contentResolver, photoUri)
                )
            } else {
                @Suppress("DEPRECATION")
                MediaStore.Images.Media.getBitmap(context.contentResolver, photoUri)
            }
        }
        bitmap = decoded
    }

    bitmap?.let {
        Image(
            bitmap = it.asImageBitmap(),
            contentDescription = "Photo to edit"
        )
    }
}
```

(Requires coroutines and `kotlinx-coroutines-android` for `Dispatchers.IO` in Compose.)

### Best Practices

1. Use FileProvider for Android 7.0+ when sharing files between apps.
2. Grant URI permissions to external apps via `FLAG_GRANT_READ_URI_PERMISSION` / `FLAG_GRANT_WRITE_URI_PERMISSION` (WRITE only when needed).
3. Avoid passing large bitmaps via `Intent` extras — Binder transactions are limited (~1MB); use a conservative payload size and prefer URIs.
4. Manage memory carefully — scale/downsample large images; explicit `recycle()` is generally unnecessary with managed Bitmaps.
5. Store temporary files under `cacheDir` or similar for non-persistent images.
6. Handle errors — ensure a suitable editor exists and that your FileProvider authority/paths and URIs are valid.

## Follow-ups

1. What happens if FileProvider authority does not match the authority declared in the manifest?
2. How can you handle EXIF orientation so photos are displayed with correct rotation in the editor?
3. What strategies can you use to avoid OOM when loading very large images for editing?
4. When should you use `MediaStore` versus `FileProvider` for sharing or editing images?
5. How do you securely share edited images with other apps while respecting scoped storage?

## References

- Android FileProvider Guide: https://developer.android.com/reference/androidx/core/content/FileProvider
- Sharing Files Documentation: https://developer.android.com/training/secure-file-sharing
- `Intent` Documentation: https://developer.android.com/reference/android/content/Intent

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
