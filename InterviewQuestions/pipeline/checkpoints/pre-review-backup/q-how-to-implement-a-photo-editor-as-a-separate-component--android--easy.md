---
id: 20251012-1227185
title: "How To Implement A Photo Editor As A Separate Component / Как реализовать фоторедактор как отдельный компонент"
topic: android
difficulty: easy
status: draft
moc: moc-android
related: [q-workmanager-vs-alternatives--background--medium, q-compose-custom-layout--jetpack-compose--hard, q-how-to-tell-adapter-to-redraw-list-if-element-was-deleted--android--medium]
created: 2025-10-15
tags: [android, android/fragments, android/views, bitmap, canvas, fragment, fragments, imageview, ui, views, difficulty/easy]
---
# Как реализовать редактор фотографий в качестве отдельного компонента?

**English**: How to implement a photo editor as a separate component?

## Answer (EN)
Implementing a photo editor in Android as a separate component requires several steps, including creating a user interface for editing, image processing, and the ability to integrate this component into other parts of your application.

### 1. Create User Interface

Design a layout with an ImageView for displaying the photo and buttons for editing operations.

```xml
<!-- fragment_photo_editor.xml -->
<androidx.constraintlayout.widget.ConstraintLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <!-- Image display -->
    <ImageView
        android:id="@+id/photoImageView"
        android:layout_width="0dp"
        android:layout_height="0dp"
        android:scaleType="centerInside"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintBottom_toTopOf="@id/editToolbar"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent" />

    <!-- Editing toolbar -->
    <HorizontalScrollView
        android:id="@+id/editToolbar"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:padding="8dp"
        android:background="@color/toolbar_background"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent">

        <LinearLayout
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:orientation="horizontal">

            <Button
                android:id="@+id/rotateButton"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Rotate"
                android:drawableTop="@drawable/ic_rotate" />

            <Button
                android:id="@+id/cropButton"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Crop"
                android:drawableTop="@drawable/ic_crop" />

            <Button
                android:id="@+id/filterButton"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Filter"
                android:drawableTop="@drawable/ic_filter" />

            <Button
                android:id="@+id/brightnessButton"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Brightness"
                android:drawableTop="@drawable/ic_brightness" />

            <Button
                android:id="@+id/saveButton"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Save"
                android:drawableTop="@drawable/ic_save" />

        </LinearLayout>
    </HorizontalScrollView>

</androidx.constraintlayout.widget.ConstraintLayout>
```

### 2. Image Processing

Use Bitmap and Canvas for basic operations, or third-party libraries for advanced features.

```kotlin
class PhotoEditorFragment : Fragment() {

    private lateinit var binding: FragmentPhotoEditorBinding
    private var originalBitmap: Bitmap? = null
    private var editedBitmap: Bitmap? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        binding = FragmentPhotoEditorBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Load image
        loadImage()

        // Setup button listeners
        binding.rotateButton.setOnClickListener { rotateImage() }
        binding.cropButton.setOnClickListener { cropImage() }
        binding.filterButton.setOnClickListener { applyFilter() }
        binding.brightnessButton.setOnClickListener { adjustBrightness() }
        binding.saveButton.setOnClickListener { saveImage() }
    }

    private fun loadImage() {
        // Load image from URI or resource
        val imageUri = arguments?.getParcelable<Uri>("image_uri")
        imageUri?.let { uri ->
            originalBitmap = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                val source = ImageDecoder.createSource(requireContext().contentResolver, uri)
                ImageDecoder.decodeBitmap(source)
            } else {
                @Suppress("DEPRECATION")
                MediaStore.Images.Media.getBitmap(requireContext().contentResolver, uri)
            }
            editedBitmap = originalBitmap?.copy(Bitmap.Config.ARGB_8888, true)
            binding.photoImageView.setImageBitmap(editedBitmap)
        }
    }

    private fun rotateImage() {
        editedBitmap?.let { bitmap ->
            val matrix = Matrix().apply {
                postRotate(90f)
            }
            editedBitmap = Bitmap.createBitmap(
                bitmap,
                0, 0,
                bitmap.width,
                bitmap.height,
                matrix,
                true
            )
            binding.photoImageView.setImageBitmap(editedBitmap)
        }
    }

    private fun cropImage() {
        // Use third-party library like uCrop
        editedBitmap?.let { bitmap ->
            val tempFile = File(requireContext().cacheDir, "temp_crop.jpg")
            FileOutputStream(tempFile).use { out ->
                bitmap.compress(Bitmap.CompressFormat.JPEG, 100, out)
            }

            UCrop.of(Uri.fromFile(tempFile), Uri.fromFile(tempFile))
                .withAspectRatio(1f, 1f)
                .withMaxResultSize(1080, 1080)
                .start(requireContext(), this)
        }
    }

    private fun applyFilter() {
        editedBitmap?.let { bitmap ->
            // Apply grayscale filter
            editedBitmap = applyGrayscaleFilter(bitmap)
            binding.photoImageView.setImageBitmap(editedBitmap)
        }
    }

    private fun applyGrayscaleFilter(source: Bitmap): Bitmap {
        val width = source.width
        val height = source.height
        val result = Bitmap.createBitmap(width, height, source.config)

        val canvas = Canvas(result)
        val paint = Paint()
        val colorMatrix = ColorMatrix().apply {
            setSaturation(0f) // Grayscale
        }
        val filter = ColorMatrixColorFilter(colorMatrix)
        paint.colorFilter = filter
        canvas.drawBitmap(source, 0f, 0f, paint)

        return result
    }

    private fun adjustBrightness() {
        // Show brightness adjustment dialog
        val dialog = BrightnessDialogFragment()
        dialog.setOnBrightnessChangedListener { value ->
            editedBitmap?.let { bitmap ->
                editedBitmap = adjustBitmapBrightness(bitmap, value)
                binding.photoImageView.setImageBitmap(editedBitmap)
            }
        }
        dialog.show(childFragmentManager, "brightness")
    }

    private fun adjustBitmapBrightness(bitmap: Bitmap, brightness: Float): Bitmap {
        val result = Bitmap.createBitmap(bitmap.width, bitmap.height, bitmap.config)
        val canvas = Canvas(result)
        val paint = Paint()
        val colorMatrix = ColorMatrix(
            floatArrayOf(
                1f, 0f, 0f, 0f, brightness,
                0f, 1f, 0f, 0f, brightness,
                0f, 0f, 1f, 0f, brightness,
                0f, 0f, 0f, 1f, 0f
            )
        )
        paint.colorFilter = ColorMatrixColorFilter(colorMatrix)
        canvas.drawBitmap(bitmap, 0f, 0f, paint)
        return result
    }

    private fun saveImage() {
        editedBitmap?.let { bitmap ->
            val filename = "edited_${System.currentTimeMillis()}.jpg"
            val contentValues = ContentValues().apply {
                put(MediaStore.Images.Media.DISPLAY_NAME, filename)
                put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES)
                }
            }

            val uri = requireContext().contentResolver.insert(
                MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                contentValues
            )

            uri?.let {
                requireContext().contentResolver.openOutputStream(it)?.use { out ->
                    bitmap.compress(Bitmap.CompressFormat.JPEG, 95, out)
                }
                Toast.makeText(requireContext(), "Image saved", Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        originalBitmap?.recycle()
        editedBitmap?.recycle()
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

### 3. Integration as Component

#### As Fragment

```kotlin
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

#### As Activity

```kotlin
class PhotoEditorActivity : AppCompatActivity() {
    private lateinit var binding: ActivityPhotoEditorBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPhotoEditorBinding.inflate(layoutInflater)
        setContentView(binding.root)

        val imageUri = intent.getParcelableExtra<Uri>("image_uri")
        imageUri?.let { uri ->
            supportFragmentManager.beginTransaction()
                .replace(R.id.container, PhotoEditorFragment.newInstance(uri))
                .commit()
        }
    }

    companion object {
        fun start(context: Context, imageUri: Uri) {
            val intent = Intent(context, PhotoEditorActivity::class.java).apply {
                putExtra("image_uri", imageUri)
            }
            context.startActivity(intent)
        }
    }
}
```

### 4. Using Third-Party Libraries

#### GPUImage for Filters

```kotlin
// build.gradle
dependencies {
    implementation 'jp.co.cyberagent.android:gpuimage:2.1.0'
}

// Usage
class PhotoEditorFragment : Fragment() {
    private lateinit var gpuImage: GPUImage

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        gpuImage = GPUImage(requireContext())
        gpuImage.setGLSurfaceView(binding.gpuImageView)

        // Apply filter
        binding.filterButton.setOnClickListener {
            gpuImage.setFilter(GPUImageGrayscaleFilter())
        }

        // Load image
        originalBitmap?.let { bitmap ->
            gpuImage.setImage(bitmap)
        }
    }
}
```

#### uCrop for Cropping

```kotlin
// build.gradle
dependencies {
    implementation 'com.github.yalantis:ucrop:2.2.8'
}

// Usage
private fun startCrop(sourceUri: Uri) {
    val destinationUri = Uri.fromFile(File(requireContext().cacheDir, "cropped.jpg"))

    UCrop.of(sourceUri, destinationUri)
        .withAspectRatio(16f, 9f)
        .withMaxResultSize(1080, 1920)
        .start(requireContext(), this)
}

override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
    super.onActivityResult(requestCode, resultCode, data)
    if (resultCode == Activity.RESULT_OK && requestCode == UCrop.REQUEST_CROP) {
        val resultUri = UCrop.getOutput(data!!)
        binding.photoImageView.setImageURI(resultUri)
    }
}
```

### 5. Custom View Approach

```kotlin
class PhotoEditorView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : FrameLayout(context, attrs, defStyleAttr) {

    private val imageView: ImageView
    private var bitmap: Bitmap? = null

    init {
        inflate(context, R.layout.view_photo_editor, this)
        imageView = findViewById(R.id.imageView)
    }

    fun setImage(bitmap: Bitmap) {
        this.bitmap = bitmap
        imageView.setImageBitmap(bitmap)
    }

    fun rotate() {
        bitmap?.let { bmp ->
            val matrix = Matrix().apply { postRotate(90f) }
            bitmap = Bitmap.createBitmap(bmp, 0, 0, bmp.width, bmp.height, matrix, true)
            imageView.setImageBitmap(bitmap)
        }
    }

    fun applyFilter(filter: ColorFilter) {
        imageView.colorFilter = filter
    }
}
```

### Summary

To implement a photo editor as a separate component:

1. **Create UI** with ImageView and editing buttons
2. **Implement image processing** using Bitmap and Canvas or libraries
3. **Integrate as Fragment or Activity** for reusability
4. **Use third-party libraries** like GPUImage (filters), uCrop (cropping)
5. **Handle memory** properly by recycling bitmaps
6. **Save edited images** to MediaStore or cache

## Ответ (RU)
Реализация редактора фотографий в Android как отдельного компонента требует нескольких шагов, включающих создание пользовательского интерфейса для редактирования, обработку изображений, а также возможность интеграции этого компонента в другие части вашего приложения. 1. Создание пользовательского интерфейса: Пример XML-разметки с ImageView и кнопками для редактирования. 2. Обработка изображений: Использование Bitmap и Canvas или сторонних библиотек для операций с изображениями. Пример кода на Kotlin показывает функции поворота и применения фильтров к изображению. 3. Интеграция компонента: Создание Activity или Fragment для использования редактора. 4. Обработка разных функций редактирования: Интеграция библиотек, таких как GPUImage для фильтров и Ucrop для обрезки.

## Related Questions

- [[q-workmanager-vs-alternatives--background--medium]]
- [[q-compose-custom-layout--android--hard]]
- [[q-how-to-tell-adapter-to-redraw-list-if-element-was-deleted--android--medium]]
