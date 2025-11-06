---
id: android-247
title: How To Implement A Photo Editor As A Separate Component / Как реализовать фоторедактор
  как отдельный компонент
aliases:
- Photo Editor Component
- Separate Photo Editor
- Отдельный компонент редактора
- Фоторедактор как компонент
topic: android
subtopics:
- fragment
- ui-graphics
- ui-views
question_kind: android
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-fragments
- q-how-to-tell-adapter-to-redraw-list-if-element-was-deleted--android--medium
- q-workmanager-vs-alternatives--android--medium
created: 2025-10-15
updated: 2025-10-31
sources: []
tags:
- android
- android/fragment
- android/ui-graphics
- android/ui-views
- bitmap
- canvas
- difficulty/easy
- fragments
- imageview
- views
---

# Вопрос (RU)

> Как реализовать фоторедактор как отдельный компонент?

# Question (EN)

> How to implement a photo editor as a separate component?

---

## Ответ (RU)

Фоторедактор реализуется как Fragment с ImageView для отображения и методами обработки Bitmap. Используйте Matrix для трансформаций и ColorMatrix для фильтров.

### Основной Компонент

```kotlin
// ✅ Fragment-based photo editor
class PhotoEditorFragment : Fragment() {
    private lateinit var binding: FragmentPhotoEditorBinding
    private var originalBitmap: Bitmap? = null
    private var editedBitmap: Bitmap? = null

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        loadImage()
        setupListeners()
    }

    private fun loadImage() {
        val imageUri = arguments?.getParcelable<Uri>("image_uri")
        imageUri?.let { uri ->
            originalBitmap = ImageDecoder.decodeBitmap(
                ImageDecoder.createSource(requireContext().contentResolver, uri)
            )
            editedBitmap = originalBitmap?.copy(Bitmap.Config.ARGB_8888, true)
            binding.photoImageView.setImageBitmap(editedBitmap)
        }
    }
}
```

### Базовые Операции

```kotlin
// ✅ Rotate image
private fun rotateImage() {
    editedBitmap?.let { bitmap ->
        val matrix = Matrix().apply { postRotate(90f) }
        editedBitmap = Bitmap.createBitmap(
            bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true
        )
        binding.photoImageView.setImageBitmap(editedBitmap)
    }
}

// ✅ Apply grayscale filter
private fun applyGrayscaleFilter(source: Bitmap): Bitmap {
    val result = Bitmap.createBitmap(source.width, source.height, source.config)
    val paint = Paint().apply {
        colorFilter = ColorMatrixColorFilter(
            ColorMatrix().apply { setSaturation(0f) }
        )
    }
    Canvas(result).drawBitmap(source, 0f, 0f, paint)
    return result
}
```

### Интеграция

```kotlin
// ✅ Use as fragment
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val imageUri = intent.getParcelableExtra<Uri>("image_uri")
        imageUri?.let { uri ->
            supportFragmentManager.beginTransaction()
                .replace(R.id.container, PhotoEditorFragment.newInstance(uri))
                .commit()
        }
    }
}
```

### Сохранение Изменений

```kotlin
// ✅ Save to MediaStore
private fun saveImage() {
    editedBitmap?.let { bitmap ->
        val contentValues = ContentValues().apply {
            put(MediaStore.Images.Media.DISPLAY_NAME, "edited_${System.currentTimeMillis()}.jpg")
            put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
            put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES)
        }

        val uri = requireContext().contentResolver.insert(
            MediaStore.Images.Media.EXTERNAL_CONTENT_URI, contentValues
        )

        uri?.let {
            requireContext().contentResolver.openOutputStream(it)?.use { out ->
                bitmap.compress(Bitmap.CompressFormat.JPEG, 95, out)
            }
        }
    }
}
```

**Управление памятью**:
```kotlin
// ✅ Recycle bitmaps
override fun onDestroyView() {
    super.onDestroyView()
    originalBitmap?.recycle()
    editedBitmap?.recycle()
}
```

**Ключевые моменты**:
- Fragment для переиспользования
- Matrix для трансформаций (rotate, scale, translate)
- ColorMatrix для фильтров (brightness, contrast, saturation)
- MediaStore для сохранения результата
- Recycling bitmaps для освобождения памяти

## Answer (EN)

Photo editor is implemented as a Fragment with ImageView for display and Bitmap processing methods. Use Matrix for transformations and ColorMatrix for filters.

### Core Component

```kotlin
// ✅ Fragment-based photo editor
class PhotoEditorFragment : Fragment() {
    private lateinit var binding: FragmentPhotoEditorBinding
    private var originalBitmap: Bitmap? = null
    private var editedBitmap: Bitmap? = null

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        loadImage()
        setupListeners()
    }

    private fun loadImage() {
        val imageUri = arguments?.getParcelable<Uri>("image_uri")
        imageUri?.let { uri ->
            originalBitmap = ImageDecoder.decodeBitmap(
                ImageDecoder.createSource(requireContext().contentResolver, uri)
            )
            editedBitmap = originalBitmap?.copy(Bitmap.Config.ARGB_8888, true)
            binding.photoImageView.setImageBitmap(editedBitmap)
        }
    }
}
```

### Basic Operations

```kotlin
// ✅ Rotate image
private fun rotateImage() {
    editedBitmap?.let { bitmap ->
        val matrix = Matrix().apply { postRotate(90f) }
        editedBitmap = Bitmap.createBitmap(
            bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true
        )
        binding.photoImageView.setImageBitmap(editedBitmap)
    }
}

// ✅ Apply grayscale filter
private fun applyGrayscaleFilter(source: Bitmap): Bitmap {
    val result = Bitmap.createBitmap(source.width, source.height, source.config)
    val paint = Paint().apply {
        colorFilter = ColorMatrixColorFilter(
            ColorMatrix().apply { setSaturation(0f) }
        )
    }
    Canvas(result).drawBitmap(source, 0f, 0f, paint)
    return result
}
```

### Integration

```kotlin
// ✅ Use as fragment
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val imageUri = intent.getParcelableExtra<Uri>("image_uri")
        imageUri?.let { uri ->
            supportFragmentManager.beginTransaction()
                .replace(R.id.container, PhotoEditorFragment.newInstance(uri))
                .commit()
        }
    }
}
```

### Saving Changes

```kotlin
// ✅ Save to MediaStore
private fun saveImage() {
    editedBitmap?.let { bitmap ->
        val contentValues = ContentValues().apply {
            put(MediaStore.Images.Media.DISPLAY_NAME, "edited_${System.currentTimeMillis()}.jpg")
            put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
            put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES)
        }

        val uri = requireContext().contentResolver.insert(
            MediaStore.Images.Media.EXTERNAL_CONTENT_URI, contentValues
        )

        uri?.let {
            requireContext().contentResolver.openOutputStream(it)?.use { out ->
                bitmap.compress(Bitmap.CompressFormat.JPEG, 95, out)
            }
        }
    }
}
```

**Memory Management**:
```kotlin
// ✅ Recycle bitmaps
override fun onDestroyView() {
    super.onDestroyView()
    originalBitmap?.recycle()
    editedBitmap?.recycle()
}
```

**Key Points**:
- Fragment for reusability
- Matrix for transformations (rotate, scale, translate)
- ColorMatrix for filters (brightness, contrast, saturation)
- MediaStore for saving results
- Recycling bitmaps to free memory

---

## Follow-ups

- How to implement crop functionality?
- How to apply custom filters using ColorMatrix?
- How to handle large images without OutOfMemoryError?
- How to add undo/redo functionality?
- How to use third-party libraries like GPUImage or uCrop?

## References

- [Android Canvas and Bitmap Documentation](https://developer.android.com/reference/android/graphics/Bitmap)
- [ColorMatrix Filters](https://developer.android.com/reference/android/graphics/ColorMatrix)
- [MediaStore API](https://developer.android.com/training/data-storage/shared/media)

## Related Questions

### Prerequisites / Concepts

- [[c-fragments]]


### Prerequisites (Easier)

### Related (Same Level)
- [[q-how-to-tell-adapter-to-redraw-list-if-element-was-deleted--android--medium]]

### Advanced (Harder)
- [[q-workmanager-vs-alternatives--android--medium]]
- [[q-custom-view-optimization--android--hard]]
