---
id: android-187
title: "Activity / Компонент Activity"
aliases: [Activity, Компонент Activity]
topic: android
subtopics: [activity, lifecycle]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-activity-lifecycle, c-android-components, q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium, q-what-each-android-component-represents--android--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [activity, android/activity, android/lifecycle, components, difficulty/medium, ui]
date created: Saturday, November 1st 2025, 12:47:08 pm
date modified: Saturday, November 1st 2025, 5:43:31 pm
---

# What is Activity and what is it Used For?

## Answer (EN)
Activity is a core component of an Android application that provides a user interface with which users can interact to perform various actions such as dialing a phone, viewing photos, sending emails, etc. Each Activity represents a single screen with a user interface.

### Activity as a Page in a Book

If you imagine an application as a book, then an Activity is one page of that book. Each page (Activity) has its own content and purpose, and users can navigate between pages.

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // This Activity displays the main screen
        setupMainScreen()
    }

    private fun setupMainScreen() {
        // Configure buttons, lists, and other UI elements
        findViewById<Button>(R.id.viewPhotosButton).setOnClickListener {
            // Navigate to photo viewing Activity
            startActivity(Intent(this, PhotoGalleryActivity::class.java))
        }

        findViewById<Button>(R.id.dialButton).setOnClickListener {
            // Navigate to dialer Activity
            val dialIntent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:1234567890"))
            startActivity(dialIntent)
        }
    }
}
```

### Main Purposes of Activity

#### 1. Providing User Interface

Activity is responsible for displaying the UI and making it interactive:

```kotlin
class PhotoGalleryActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_photo_gallery)

        // Display photos in a grid
        val recyclerView = findViewById<RecyclerView>(R.id.photoGrid)
        recyclerView.layoutManager = GridLayoutManager(this, 3)
        recyclerView.adapter = PhotoAdapter(getPhotos())
    }

    private fun getPhotos(): List<Photo> {
        // Load photos from storage or network
        return photoRepository.getAllPhotos()
    }
}
```

#### 2. User Interaction Handling

Activity processes user input and responds to it:

```kotlin
class EmailComposeActivity : AppCompatActivity() {

    private lateinit var toEditText: EditText
    private lateinit var subjectEditText: EditText
    private lateinit var messageEditText: EditText

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_email_compose)

        toEditText = findViewById(R.id.toEditText)
        subjectEditText = findViewById(R.id.subjectEditText)
        messageEditText = findViewById(R.id.messageEditText)

        // Handle send button click
        findViewById<Button>(R.id.sendButton).setOnClickListener {
            sendEmail()
        }

        // Handle attach file button click
        findViewById<Button>(R.id.attachButton).setOnClickListener {
            selectFile()
        }

        // Validate email address as user types
        toEditText.addTextChangedListener { text ->
            validateEmailAddress(text.toString())
        }
    }

    private fun sendEmail() {
        val to = toEditText.text.toString()
        val subject = subjectEditText.text.toString()
        val message = messageEditText.text.toString()

        // Send email via email app or API
        val emailIntent = Intent(Intent.ACTION_SEND).apply {
            type = "message/rfc822"
            putExtra(Intent.EXTRA_EMAIL, arrayOf(to))
            putExtra(Intent.EXTRA_SUBJECT, subject)
            putExtra(Intent.EXTRA_TEXT, message)
        }

        if (emailIntent.resolveActivity(packageManager) != null) {
            startActivity(Intent.createChooser(emailIntent, "Send email"))
        }
    }

    private fun selectFile() {
        // Open file picker
    }

    private fun validateEmailAddress(email: String) {
        // Validate email format
    }
}
```

#### 3. Lifecycle Management

Activity manages resources throughout its lifecycle:

```kotlin
class VideoPlayerActivity : AppCompatActivity() {

    private lateinit var player: VideoPlayer
    private lateinit var videoView: VideoView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_video_player)

        // Initialize player
        player = VideoPlayer(this)
        videoView = findViewById(R.id.videoView)

        val videoUrl = intent.getStringExtra("video_url")
        player.setDataSource(videoUrl)
    }

    override fun onStart() {
        super.onStart()
        // Prepare video when Activity becomes visible
        player.prepare()
    }

    override fun onResume() {
        super.onResume()
        // Start playback when Activity is in foreground
        player.play()
    }

    override fun onPause() {
        super.onPause()
        // Pause playback when Activity loses focus
        player.pause()
    }

    override fun onStop() {
        super.onStop()
        // Release resources when Activity is no longer visible
        player.stop()
    }

    override fun onDestroy() {
        super.onDestroy()
        // Clean up player
        player.release()
    }
}
```

#### 4. Screen Transitions

Activity enables navigation between different screens:

```kotlin
class ProductListActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_product_list)

        val recyclerView = findViewById<RecyclerView>(R.id.productRecyclerView)
        val adapter = ProductAdapter { product ->
            // Navigate to product details when item clicked
            navigateToProductDetails(product)
        }

        recyclerView.adapter = adapter
        adapter.submitList(getProducts())
    }

    private fun navigateToProductDetails(product: Product) {
        val intent = Intent(this, ProductDetailActivity::class.java).apply {
            putExtra("product_id", product.id)
            putExtra("product_name", product.name)
        }
        startActivity(intent)
    }

    private fun getProducts(): List<Product> {
        return productRepository.getProducts()
    }
}

class ProductDetailActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_product_detail)

        // Receive data from previous Activity
        val productId = intent.getIntExtra("product_id", -1)
        val productName = intent.getStringExtra("product_name")

        // Display product details
        loadProductDetails(productId)
    }

    private fun loadProductDetails(productId: Int) {
        val product = productRepository.getProductById(productId)
        // Display product information
    }
}
```

#### 5. Component Interaction

Activity interacts with other Android components:

```kotlin
class MainDashboardActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dashboard)

        // Start a Service for background download
        findViewById<Button>(R.id.downloadButton).setOnClickListener {
            val serviceIntent = Intent(this, DownloadService::class.java).apply {
                putExtra("file_url", "https://example.com/file.zip")
            }
            startService(serviceIntent)
        }

        // Register BroadcastReceiver for download completion
        registerDownloadReceiver()

        // Query ContentProvider for user data
        loadUserDataFromProvider()

        // Schedule work with WorkManager
        scheduleBackgroundSync()
    }

    private fun registerDownloadReceiver() {
        val receiver = object : BroadcastReceiver() {
            override fun onReceive(context: Context, intent: Intent) {
                Toast.makeText(context, "Download complete", Toast.LENGTH_SHORT).show()
            }
        }

        val filter = IntentFilter("com.example.DOWNLOAD_COMPLETE")
        registerReceiver(receiver, filter)
    }

    private fun loadUserDataFromProvider() {
        val uri = Uri.parse("content://com.example.provider/users")
        val cursor = contentResolver.query(uri, null, null, null, null)

        cursor?.use {
            // Process user data
        }
    }

    private fun scheduleBackgroundSync() {
        val workRequest = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS)
            .build()

        WorkManager.getInstance(this).enqueue(workRequest)
    }
}
```

### Real-World Examples

#### Dialing Phone
```kotlin
class DialerActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dialer)

        findViewById<Button>(R.id.dialButton).setOnClickListener {
            val phoneNumber = findViewById<EditText>(R.id.phoneNumberInput).text.toString()
            dialPhoneNumber(phoneNumber)
        }
    }

    private fun dialPhoneNumber(phoneNumber: String) {
        val intent = Intent(Intent.ACTION_DIAL).apply {
            data = Uri.parse("tel:$phoneNumber")
        }
        startActivity(intent)
    }
}
```

#### Viewing Photos
```kotlin
class PhotoViewerActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_photo_viewer)

        val photoUri = intent.getParcelableExtra<Uri>("photo_uri")

        findViewById<ImageView>(R.id.photoImageView).apply {
            setImageURI(photoUri)
        }

        // Implement zoom, share, delete functionality
        setupPhotoActions()
    }

    private fun setupPhotoActions() {
        findViewById<Button>(R.id.shareButton).setOnClickListener {
            sharePhoto()
        }

        findViewById<Button>(R.id.deleteButton).setOnClickListener {
            deletePhoto()
        }
    }

    private fun sharePhoto() {
        val shareIntent = Intent(Intent.ACTION_SEND).apply {
            type = "image/*"
            putExtra(Intent.EXTRA_STREAM, intent.getParcelableExtra<Uri>("photo_uri"))
        }
        startActivity(Intent.createChooser(shareIntent, "Share photo"))
    }

    private fun deletePhoto() {
        // Delete photo and finish Activity
    }
}
```

### Activity Properties

| Property | Description |
|----------|-------------|
| **Single Screen** | Each Activity typically represents one screen |
| **Independent** | Can be started by other apps (if exported) |
| **Managed by System** | Lifecycle controlled by Android |
| **Has Intent Filter** | Can respond to specific intents |
| **Resource Owner** | Manages its own UI resources |
| **Context Provider** | Provides application context |

### When to Use Activity

- **Use Activity for**:
- Distinct screens in your app
- Entry points from other apps
- Different task flows
- Full-screen experiences

- **Don't use Activity for**:
- Sub-sections of a screen (use Fragments)
- Temporary UI overlays (use DialogFragment)
- Background operations (use Service/WorkManager)

## Ответ (RU)
Это компонент приложения, который предоставляет пользовательский интерфейс (UI), с которым пользователи могут взаимодействовать для выполнения различных действий, таких как набор номера телефона, просмотр фотографий, отправка электронной почты и т. д. Каждая активность представляет собой один экран с пользовательским интерфейсом. Если представить приложение как книгу, то активность будет одной страницей этой книги. Основное назначение: предоставление интерфейса пользователя, взаимодействие с пользователем, управление жизненным циклом, переход между экранами и взаимодействие с другими компонентами приложения.

## Related Topics
- Activity lifecycle
- Intent system
- Fragment vs Activity
- Single Activity architecture
- Task and back stack

---


## Follow-ups

- [[c-activity-lifecycle]]
- [[c-android-components]]
- [[q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium]]


## References

- https://developer.android.com/docs
- https://developer.android.com/topic/libraries/architecture/lifecycle


## Related Questions

### Prerequisites (Easier)
- [[q-android-components-besides-activity--android--easy]] - Activity

### Related (Medium)
- [[q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]] - Activity
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Activity
- [[q-single-activity-pros-cons--android--medium]] - Activity
- [[q-if-activity-starts-after-a-service-can-you-connect-to-this-service--android--medium]] - Activity
- [[q-activity-lifecycle-methods--android--medium]] - Activity

### Advanced (Harder)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Activity
