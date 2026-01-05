---
id: android-247
title: How To Implement A Photo Editor As A Separate Component / Как реализовать фоторедактор как отдельный компонент
aliases: [Photo Editor Component, Separate Photo Editor, Отдельный компонент редактора, Фоторедактор как компонент]
topic: android
subtopics: [fragment, ui-graphics, ui-views]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-activity, q-how-to-pass-photo-to-editor--android--medium, q-how-to-tell-adapter-to-redraw-list-if-element-was-deleted--android--medium, q-implement-voice-video-call--android--hard, q-why-separate-ui-and-business-logic--android--easy, q-workmanager-vs-alternatives--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android, android/fragment, android/ui-graphics, android/ui-views, bitmap, canvas, difficulty/easy, fragments, imageview, views]

---
# Вопрос (RU)

> Как реализовать фоторедактор как отдельный компонент?

# Question (EN)

> How to implement a photo editor as a separate component?

---

## Ответ (RU)

Фоторедактор можно реализовать как переиспользуемый `Fragment` с `ImageView` для отображения и методами обработки `Bitmap` внутри фрагмента. Для трансформаций используйте `Matrix`, для базовых цветовых эффектов — `ColorMatrix`. Важно чётко определить API фрагмента (например, `newInstance` для передачи URI и callback/интерфейс или `FragmentResult` для возврата результата), чтобы компонент был изолирован от конкретной `Activity`.

### Основной Компонент

```kotlin
// Fragment-based photo editor (упрощённый пример)
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
            // На API 28+ можно использовать ImageDecoder; на более старых версиях используйте BitmapFactory
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                val source = ImageDecoder.createSource(requireContext().contentResolver, uri)
                originalBitmap = ImageDecoder.decodeBitmap(source) { decoder, _, _ ->
                    decoder.isMutableRequired = true
                }
            } else {
                originalBitmap = requireContext().contentResolver.openInputStream(uri)?.use { input ->
                    BitmapFactory.decodeStream(input)
                }
            }

            editedBitmap = originalBitmap?.copy(Bitmap.Config.ARGB_8888, true)
            binding.photoImageView.setImageBitmap(editedBitmap)
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // Освобождаем ссылки на большие Bitmap, чтобы помочь GC и избежать утечек
        originalBitmap = null
        editedBitmap = null
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

    // Пример API возврата результата во внешнюю Activity/Fragment через Fragment Result API
    private fun returnResult(uri: Uri) {
        parentFragmentManager.setFragmentResult(
            "photo_editor_result",
            bundleOf("edited_image_uri" to uri)
        )
    }
}
```

### Базовые Операции

```kotlin
// Поворот изображения (пример трансформации)
private fun rotateImage() {
    editedBitmap?.let { bitmap ->
        val matrix = Matrix().apply { postRotate(90f) }
        val rotated = Bitmap.createBitmap(
            bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true
        )
        // При необходимости освобождаем ссылку на старый bitmap, чтобы GC мог его собрать
        editedBitmap = rotated
        binding.photoImageView.setImageBitmap(rotated)
    }
}

// Применение градаций серого (пример ColorMatrix)
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

// Аналогично можно настроить ColorMatrix для яркости/контраста,
// изменяя элементы матрицы вместо использования готовых параметров.
```

### Интеграция

```kotlin
// Использование как отдельного фрагмента
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

        // Пример получения результата от фрагмента через Fragment Result API
        supportFragmentManager.setFragmentResultListener(
            "photo_editor_result",
            this
        ) { _, bundle ->
            val editedUri = bundle.getParcelable<Uri>("edited_image_uri")
            // Обработка результата (например, показ или загрузка отредактированного изображения)
        }
    }
}
```

### Сохранение Изменений

```kotlin
// Сохранение в MediaStore (подход Android 10+; на старых API некоторые поля, как RELATIVE_PATH, игнорируются)
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
            // При использовании как отдельного компонента можно вернуть URI через callback / FragmentResult
            // returnResult(it)
        }
    }
}
```

**Управление памятью**:

- Используйте подходящую конфигурацию декодирования (например, масштабирование под размер контейнера), чтобы избежать `OutOfMemoryError` на больших изображениях.
- Не вызывайте `bitmap.recycle()` вручную без строгого контроля владения; в типичном фрагмент-компоненте достаточно освободить ссылки в `onDestroyView` и полагаться на GC.

**Ключевые моменты**:
- `Fragment` как переиспользуемый компонент с чётким API (входные данные и возврат результата через callback/интерфейс или `Fragment` Result API)
- `Matrix` для трансформаций (rotate, scale, translate)
- `ColorMatrix` для цветовых эффектов (grayscale и корректировки через матрицу)
- `MediaStore` для сохранения результата (с учётом различий поведения на разных API)
- Корректная работа с `View` Binding и освобождение ссылок для предотвращения утечек

---

## Answer (EN)

You can implement the photo editor as a reusable `Fragment` with an `ImageView` for display and `Bitmap` processing methods inside the fragment. Use `Matrix` for transformations and `ColorMatrix` for basic color effects. Define a clear fragment API (e.g., `newInstance` for the input URI and a callback/interface or `Fragment` Result API for returning the result) so the component stays independent of a specific `Activity`.

### Core Component

```kotlin
// Fragment-based photo editor (simplified example)
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
            // On API 28+ use ImageDecoder; on older APIs fall back to BitmapFactory
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                val source = ImageDecoder.createSource(requireContext().contentResolver, uri)
                originalBitmap = ImageDecoder.decodeBitmap(source) { decoder, _, _ ->
                    decoder.isMutableRequired = true
                }
            } else {
                originalBitmap = requireContext().contentResolver.openInputStream(uri)?.use { input ->
                    BitmapFactory.decodeStream(input)
                }
            }

            editedBitmap = originalBitmap?.copy(Bitmap.Config.ARGB_8888, true)
            binding.photoImageView.setImageBitmap(editedBitmap)
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // Clear references to large Bitmaps to help GC and avoid leaks
        originalBitmap = null
        editedBitmap = null
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

    // Example API to deliver result to host via Fragment Result API
    private fun returnResult(uri: Uri) {
        parentFragmentManager.setFragmentResult(
            "photo_editor_result",
            bundleOf("edited_image_uri" to uri)
        )
    }
}
```

### Basic Operations

```kotlin
// Rotate image (transformation example)
private fun rotateImage() {
    editedBitmap?.let { bitmap ->
        val matrix = Matrix().apply { postRotate(90f) }
        val rotated = Bitmap.createBitmap(
            bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true
        )
        // Optionally drop reference to the previous bitmap so GC can reclaim it
        editedBitmap = rotated
        binding.photoImageView.setImageBitmap(rotated)
    }
}

// Apply grayscale filter (ColorMatrix example)
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
// Use as a separate fragment
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

        // Example of receiving result from the editor via Fragment Result API
        supportFragmentManager.setFragmentResultListener(
            "photo_editor_result",
            this
        ) { _, bundle ->
            val editedUri = bundle.getParcelable<Uri>("edited_image_uri")
            // Handle the result (e.g., display or upload the edited image)
        }
    }
}
```

### Saving Changes

```kotlin
// Save to MediaStore (Android 10+ style; on earlier APIs some fields like RELATIVE_PATH are ignored)
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
            // When used as a separate component, you can return the URI via callback / FragmentResult
            // returnResult(it)
        }
    }
}
```

**Memory Management**:

- Use proper decode configuration (e.g., downscaling to the container/view size) to avoid `OutOfMemoryError` with large images.
- Avoid calling `bitmap.recycle()` manually unless you have strict ownership control; in a typical fragment-based component, clearing references in `onDestroyView` and relying on GC is safer.

**Key Points**:
- `Fragment` as a reusable component with a clear API (input data and returning result via callback/interface or `Fragment` Result API)
- `Matrix` for transformations (rotate, scale, translate)
- `ColorMatrix` for color effects (grayscale and adjustments via matrix values)
- `MediaStore` for saving result images (noting behavioral differences across API levels)
- Correct `View` Binding usage and clearing references to prevent leaks

---

## Дополнительные Вопросы (RU)

- Как реализовать функцию обрезки изображения (crop)?
- Как применять кастомные фильтры с использованием `ColorMatrix`?
- Как обрабатывать большие изображения без `OutOfMemoryError`?
- Как добавить функциональность undo/redo?
- Как использовать сторонние библиотеки, такие как GPUImage или uCrop?

## Follow-ups

- How to implement crop functionality?
- How to apply custom filters using `ColorMatrix`?
- How to handle large images without `OutOfMemoryError`?
- How to add undo/redo functionality?
- How to use third-party libraries like GPUImage or uCrop?

## Ссылки (RU)

- [Документация по Bitmap](https://developer.android.com/reference/android/graphics/Bitmap)
- [ColorMatrix Filters](https://developer.android.com/reference/android/graphics/ColorMatrix)
- [MediaStore API](https://developer.android.com/training/data-storage/shared/media)

## References

- [Android Canvas and Bitmap Documentation](https://developer.android.com/reference/android/graphics/Bitmap)
- [ColorMatrix Filters](https://developer.android.com/reference/android/graphics/ColorMatrix)
- [MediaStore API](https://developer.android.com/training/data-storage/shared/media)

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-activity]]

### Предпосылки (проще)

### Связанные (тот Же уровень)

- [[q-how-to-tell-adapter-to-redraw-list-if-element-was-deleted--android--medium]]

### Продвинутые (сложнее)

- [[q-workmanager-vs-alternatives--android--medium]]

## Related Questions

### Prerequisites / Concepts

- [[c-activity]]

### Prerequisites (Easier)

### Related (Same Level)

- [[q-how-to-tell-adapter-to-redraw-list-if-element-was-deleted--android--medium]]

### Advanced (Harder)

- [[q-workmanager-vs-alternatives--android--medium]]