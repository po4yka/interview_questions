---
id: android-247
title: How To Implement A Photo Editor As A Separate Component / Как реализовать фоторедактор как отдельный компонент
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
updated: 2025-11-10
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

Фоторедактор можно реализовать как переиспользуемый `Fragment` с ImageView для отображения и методами обработки Bitmap внутри фрагмента. Для трансформаций используйте Matrix, для базовых цветовых эффектов — ColorMatrix. Важно чётко определить API фрагмента (например, newInstance для передачи URI и callback для результата), чтобы компонент был изолирован от конкретной `Activity`.

### Основной Компонент

```kotlin
// ✅ Fragment-based photo editor (упрощённый пример)
class PhotoEditorFragment : Fragment() {
    private var _binding: FragmentPhotoEditorBinding? = null
    private val binding get() = _binding!!

    private var originalBitmap: Bitmap? = null
    private var editedBitmap: Bitmap? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentPhotoEditorBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        loadImage()
        setupListeners() // предполагается, что тут кнопки вызывают rotate/applyFilter/save
    }

    private fun loadImage() {
        val imageUri = arguments?.getParcelable<Uri>("image_uri")
        imageUri?.let { uri ->
            val source = ImageDecoder.createSource(requireContext().contentResolver, uri)
            originalBitmap = ImageDecoder.decodeBitmap(source) { decoder, _, _ ->
                // Базовый пример: подстройка размера при необходимости
                decoder.isMutableRequired = true
            }
            editedBitmap = originalBitmap?.copy(Bitmap.Config.ARGB_8888, true)
            binding.photoImageView.setImageBitmap(editedBitmap)
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // Не вызываем recycle() вручную, чтобы избежать использования уже рецикленных Bitmap.
        _binding = null
    }

    companion object {
        fun newInstance(imageUri: Uri): PhotoEditorFragment {
            return PhotoEditorFragment().apply {
                arguments = Bundle().apply {
                    putParcelable("image_uri", imageUri)
                }
            }
        }
    }
}
```

### Базовые Операции

```kotlin
// ✅ Rotate image (пример трансформации)
private fun rotateImage() {
    editedBitmap?.let { bitmap ->
        val matrix = Matrix().apply { postRotate(90f) }
        val rotated = Bitmap.createBitmap(
            bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true
        )
        editedBitmap = rotated
        binding.photoImageView.setImageBitmap(rotated)
    }
}

// ✅ Apply grayscale filter (пример ColorMatrix)
private fun applyGrayscaleFilter(source: Bitmap): Bitmap {
    val result = Bitmap.createBitmap(source.width, source.height, Bitmap.Config.ARGB_8888)
    val paint = Paint().apply {
        colorFilter = ColorMatrixColorFilter(
            ColorMatrix().apply { setSaturation(0f) }
        )
    }
    Canvas(result).drawBitmap(source, 0f, 0f, paint)
    return result
}

// Аналогично можно задать ColorMatrix для яркости/контраста,
// изменяя элементы матрицы, а не через "готовые" параметры.
```

### Интеграция

```kotlin
// ✅ Использование как отдельного фрагмента
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

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
// ✅ Save to MediaStore (Android 10+ подход)
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

- Используйте конфигурацию декодирования (например, масштабирование под размер контейнера), чтобы избежать OutOfMemoryError на больших изображениях.
- Не вызывайте `bitmap.recycle()` вручную без строгого контроля владения объектом; в типичном фрагмент-компоненте достаточно полагаться на GC и освобождение ссылок при уничтожении view.

**Ключевые моменты**:
- `Fragment` как переиспользуемый компонент с чётким API (передача входных данных и возврат результата)
- Matrix для трансформаций (rotate, scale, translate)
- ColorMatrix для цветовых эффектов (grayscale, корректировки через матрицу)
- MediaStore для сохранения результата
- Корректная работа с `View` Binding и освобождение ссылок для предотвращения утечек

## Answer (EN)

You can implement the photo editor as a reusable `Fragment` with an ImageView for display and Bitmap processing methods inside the fragment. Use Matrix for transformations and ColorMatrix for basic color effects. Define a clear fragment API (e.g., newInstance for input URI and a callback/interface for the result) to keep it independent from a specific `Activity`.

### Core Component

```kotlin
// ✅ Fragment-based photo editor (simplified example)
class PhotoEditorFragment : Fragment() {
    private var _binding: FragmentPhotoEditorBinding? = null
    private val binding get() = _binding!!

    private var originalBitmap: Bitmap? = null
    private var editedBitmap: Bitmap? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentPhotoEditorBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        loadImage()
        setupListeners() // assume buttons call rotate/applyFilter/save
    }

    private fun loadImage() {
        val imageUri = arguments?.getParcelable<Uri>("image_uri")
        imageUri?.let { uri ->
            val source = ImageDecoder.createSource(requireContext().contentResolver, uri)
            originalBitmap = ImageDecoder.decodeBitmap(source) { decoder, _, _ ->
                // Basic example: adjust if you need downscaling
                decoder.isMutableRequired = true
            }
            editedBitmap = originalBitmap?.copy(Bitmap.Config.ARGB_8888, true)
            binding.photoImageView.setImageBitmap(editedBitmap)
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // Do not manually call recycle() here: avoid using recycled bitmaps.
        _binding = null
    }

    companion object {
        fun newInstance(imageUri: Uri): PhotoEditorFragment {
            return PhotoEditorFragment().apply {
                arguments = Bundle().apply {
                    putParcelable("image_uri", imageUri)
                }
            }
        }
    }
}
```

### Basic Operations

```kotlin
// ✅ Rotate image (transformation example)
private fun rotateImage() {
    editedBitmap?.let { bitmap ->
        val matrix = Matrix().apply { postRotate(90f) }
        val rotated = Bitmap.createBitmap(
            bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true
        )
        editedBitmap = rotated
        binding.photoImageView.setImageBitmap(rotated)
    }
}

// ✅ Apply grayscale filter (ColorMatrix example)
private fun applyGrayscaleFilter(source: Bitmap): Bitmap {
    val result = Bitmap.createBitmap(source.width, source.height, Bitmap.Config.ARGB_8888)
    val paint = Paint().apply {
        colorFilter = ColorMatrixColorFilter(
            ColorMatrix().apply { setSaturation(0f) }
        )
    }
    Canvas(result).drawBitmap(source, 0f, 0f, paint)
    return result
}

// Similarly, you can configure ColorMatrix values for brightness/contrast
// instead of expecting built-in parameters.
```

### Integration

```kotlin
// ✅ Use as a separate fragment
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

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
// ✅ Save to MediaStore (Android 10+ style)
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

- Use proper decode configuration (e.g., downscaling to view/container size) to avoid OutOfMemoryError with large images.
- Avoid calling `bitmap.recycle()` manually unless you have strict ownership control; in a typical fragment component, releasing references on view destruction and letting GC handle it is safer.

**Key Points**:
- `Fragment` as a reusable component with a clear API (input and output contracts)
- Matrix for transformations (rotate, scale, translate)
- ColorMatrix for color effects (grayscale and other adjustments via matrix values)
- MediaStore for saving result images
- Correct `View` Binding usage and releasing references to prevent leaks

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
