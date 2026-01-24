---
id: android-187
title: Activity / Компонент Activity
aliases:
- Activity
- Компонент Activity
topic: android
subtopics:
- activity
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-activity-lifecycle
- c-android-components
- q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium
- q-single-activity-pros-cons--android--medium
- q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium
- q-what-each-android-component-represents--android--easy
- q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium
created: 2025-10-15
updated: 2025-11-10
tags:
- android/activity
- difficulty/medium
anki_cards:
- slug: android-187-0-en
  language: en
  anki_id: 1768398630534
  synced_at: '2026-01-23T16:45:05.608682'
- slug: android-187-0-ru
  language: ru
  anki_id: 1768398630559
  synced_at: '2026-01-23T16:45:05.610219'
---
# Вопрос (RU)
> Компонент `Activity`

# Question (EN)
> `Activity`

---

## Ответ (RU)
Активность (`Activity`) — это базовый компонент Android-приложения, который обычно представляет один логически целостный экран или точку входа, с которой пользователь может взаимодействовать. `Activity`:
- отображает и управляет пользовательским интерфейсом,
- обрабатывает действия и ввод пользователя,
- участвует в жизненном цикле, управляемом системой,
- инициирует навигацию между экранами через `Intent` и взаимодействует с другими компонентами.

### `Activity` Как Страница Книги

Если представить приложение как книгу, то `Activity` — это одна "страница" этой книги. Каждая страница (`Activity`) имеет собственный контент и назначение, а пользователь может переходить между такими страницами. При этом в современных архитектурах (например, single-activity) несколько экранов могут жить внутри одной `Activity` (через `Fragment` или composable-экраны).

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Эта Activity отображает главный экран
        setupMainScreen()
    }

    private fun setupMainScreen() {
        // Настройка кнопок, списков и других элементов UI
        findViewById<Button>(R.id.viewPhotosButton).setOnClickListener {
            // Переход к Activity просмотра фотографий
            startActivity(Intent(this, PhotoGalleryActivity::class.java))
        }

        findViewById<Button>(R.id.dialButton).setOnClickListener {
            // Открыть звонилку через неявный Intent
            val dialIntent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:1234567890"))
            startActivity(dialIntent)
        }
    }
}
```

### Основные Назначения `Activity`

#### 1. Предоставление Пользовательского Интерфейса

`Activity` отвечает за отображение UI и обеспечение интерактивности:

```kotlin
class PhotoGalleryActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_photo_gallery)

        // Отображение фотографий в сетке
        val recyclerView = findViewById<RecyclerView>(R.id.photoGrid)
        recyclerView.layoutManager = GridLayoutManager(this, 3)
        recyclerView.adapter = PhotoAdapter(getPhotos())
    }

    private fun getPhotos(): List<Photo> {
        // Загрузка фотографий из хранилища или сети
        return photoRepository.getAllPhotos()
    }
}
```

#### 2. Обработка Пользовательских Действий

`Activity` обрабатывает ввод пользователя и реагирует на него:

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

        // Обработка нажатия на кнопку отправки
        findViewById<Button>(R.id.sendButton).setOnClickListener {
            sendEmail()
        }

        // Обработка выбора файла для вложения
        findViewById<Button>(R.id.attachButton).setOnClickListener {
            selectFile()
        }

        // Валидация email-адреса по мере ввода
        toEditText.addTextChangedListener { text ->
            validateEmailAddress(text.toString())
        }
    }

    private fun sendEmail() {
        val to = toEditText.text.toString()
        val subject = subjectEditText.text.toString()
        val message = messageEditText.text.toString()

        // Упрощенный пример отправки письма через почтовое приложение
        // На практике часто используют ACTION_SENDTO с mailto: URI
        val emailIntent = Intent(Intent.ACTION_SEND).apply {
            type = "message/*"
            putExtra(Intent.EXTRA_EMAIL, arrayOf(to))
            putExtra(Intent.EXTRA_SUBJECT, subject)
            putExtra(Intent.EXTRA_TEXT, message)
        }

        if (emailIntent.resolveActivity(packageManager) != null) {
            startActivity(Intent.createChooser(emailIntent, "Send email"))
        }
    }

    private fun selectFile() {
        // Открыть файловый менеджер для выбора файла
    }

    private fun validateEmailAddress(email: String) {
        // Проверить формат email-адреса
    }
}
```

#### 3. Управление Жизненным Циклом

`Activity` управляет ресурсами в рамках своего жизненного цикла. Пример демонстрирует привязку использования ресурсов к колбэкам жизненного цикла (класс `VideoPlayer` условный):

```kotlin
class VideoPlayerActivity : AppCompatActivity() {

    private lateinit var player: VideoPlayer

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_video_player)

        player = VideoPlayer(this)
        val videoUrl = intent.getStringExtra("video_url")
        if (videoUrl != null) {
            player.setDataSource(videoUrl)
        }
    }

    override fun onStart() {
        super.onStart()
        // Подготовить видео, когда Activity становится видимой
        player.prepare()
    }

    override fun onResume() {
        super.onResume()
        // Начать воспроизведение, когда Activity на переднем плане
        player.play()
    }

    override fun onPause() {
        // Приостановить воспроизведение, когда Activity частично скрыта
        player.pause()
        super.onPause()
    }

    override fun onStop() {
        // Остановить воспроизведение, когда Activity больше не видна
        player.stop()
        super.onStop()
    }

    override fun onDestroy() {
        // Освободить ресурсы плеера
        player.release()
        super.onDestroy()
    }
}
```

#### 4. Переходы Между Экранами

`Activity` инициирует навигацию между экранами с помощью `Intent`:

```kotlin
class ProductListActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_product_list)

        val recyclerView = findViewById<RecyclerView>(R.id.productRecyclerView)
        val adapter = ProductAdapter { product ->
            // Переход к экрану деталей товара при клике
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

        // Получение данных из предыдущей Activity
        val productId = intent.getIntExtra("product_id", -1)
        val productName = intent.getStringExtra("product_name")

        // Отобразить детали товара
        loadProductDetails(productId)
    }

    private fun loadProductDetails(productId: Int) {
        val product = productRepository.getProductById(productId)
        // Показать информацию о товаре
    }
}
```

#### 5. Взаимодействие С Другими Компонентами

`Activity` взаимодействует с другими компонентами Android: `Service`, `BroadcastReceiver`, `ContentProvider`, `WorkManager`:

```kotlin
class MainDashboardActivity : AppCompatActivity() {

    private var downloadReceiver: BroadcastReceiver? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dashboard)

        // Запуск Service для фоновой загрузки (упрощенный пример — для длительных задач предпочтительнее WorkManager или foreground service)
        findViewById<Button>(R.id.downloadButton).setOnClickListener {
            val serviceIntent = Intent(this, DownloadService::class.java).apply {
                putExtra("file_url", "https://example.com/file.zip")
            }
            startService(serviceIntent)
        }

        // Регистрация BroadcastReceiver для получения события об окончании загрузки
        registerDownloadReceiver()

        // Загрузка данных пользователя из ContentProvider
        loadUserDataFromProvider()

        // Планирование фоновой синхронизации через WorkManager
        scheduleBackgroundSync()
    }

    private fun registerDownloadReceiver() {
        downloadReceiver = object : BroadcastReceiver() {
            override fun onReceive(context: Context, intent: Intent) {
                Toast.makeText(context, "Download complete", Toast.LENGTH_SHORT).show()
            }
        }

        val filter = IntentFilter("com.example.DOWNLOAD_COMPLETE")
        registerReceiver(downloadReceiver, filter)
    }

    override fun onDestroy() {
        downloadReceiver?.let { unregisterReceiver(it) }
        super.onDestroy()
    }

    private fun loadUserDataFromProvider() {
        val uri = Uri.parse("content://com.example.provider/users")
        val cursor = contentResolver.query(uri, null, null, null, null)

        cursor?.use {
            // Обработка данных пользователя
        }
    }

    private fun scheduleBackgroundSync() {
        val workRequest = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS).build()
        WorkManager.getInstance(this).enqueue(workRequest)
    }
}
```

### Практические Примеры

#### Набор Номера Телефона

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

#### Просмотр Фотографий

```kotlin
class PhotoViewerActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_photo_viewer)

        val photoUri = intent.getParcelableExtra<Uri>("photo_uri")

        findViewById<ImageView>(R.id.photoImageView).apply {
            setImageURI(photoUri)
        }

        // Реализация масштабирования, шаринга и удаления
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
        val uriToShare = intent.getParcelableExtra<Uri>("photo_uri")
        val shareIntent = Intent(Intent.ACTION_SEND).apply {
            type = "image/*"
            putExtra(Intent.EXTRA_STREAM, uriToShare)
        }
        startActivity(Intent.createChooser(shareIntent, "Share photo"))
    }

    private fun deletePhoto() {
        // Удалить фото при наличии прав и закрыть Activity
        // contentResolver.delete(photoUri, null, null)
        finish()
    }
}
```

### Свойства `Activity`

- Один сфокусированный экран или точка входа.
- Может быть запущена другими приложениями (если экспортирована и объявлены нужные `intent-filter`).
- Жизненным циклом управляет фреймворк Android.
- Может обрабатывать конкретные `Intent` при наличии соответствующих фильтров.
- Управляет собственным UI и связанными ресурсами.
- Является `Context`: используется для работы с UI и привязанных к нему ресурсов; для долгоживущих объектов и контекста приложения используют `applicationContext`.

### Когда Использовать `Activity`

Используйте новую `Activity`, когда:
- нужен отдельный, логически самостоятельный экран или поток взаимодействия;
- это точка входа извне (deep links, implicit intents, launcher-иконки);
- требуется полноэкранный или крупный пользовательский сценарий.

Предпочитайте другие компоненты вместо новой `Activity`, когда:
- нужно разбить экран на части — используйте `Fragment` или навигацию на уровне composable;
- нужна временная накладка/диалог — используйте `Dialog`, `DialogFragment` или элементы внутри текущего экрана;
- требуется длительная или фоновая работа — используйте `Service`, `WorkManager`, корутины и т.п., а не держите `Activity` живой.

---

## Answer (EN)
`Activity` is a core component of an Android application that typically represents a single logical screen or entry point with which users can interact. It:
- provides a visual user interface,
- handles user input,
- participates in a well-defined lifecycle managed by the system,
- initiates navigation to other screens via `Intent` and coordinates interaction with other components.

Activities are commonly used as entry points into an app or into distinct user flows (e.g., dialing a phone number, viewing photos, composing an email), but modern architectures may use a single `Activity` hosting multiple screens (Fragments or composable destinations).

### `Activity` As a Page in a Book

If you imagine an application as a book, then an `Activity` is one "page" of that book. Each page (`Activity`) has its own content and purpose, and users can navigate between pages. In modern single-activity setups, multiple UI "pages" can exist within one `Activity` (e.g., via `Fragment` or composable screens).

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
            // Open dialer app via implicit intent
            val dialIntent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:1234567890"))
            startActivity(dialIntent)
        }
    }
}
```

### Main Purposes of `Activity`

#### 1. Providing User Interface

`Activity` is responsible for displaying the UI and making it interactive:

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

`Activity` processes user input and responds to it:

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

        // Simplified example of sending email via an email app
        // In real apps, ACTION_SENDTO with mailto: URI is commonly preferred
        val emailIntent = Intent(Intent.ACTION_SEND).apply {
            type = "message/*"
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

`Activity` manages resources throughout its lifecycle. This example illustrates binding resource usage to lifecycle callbacks (the VideoPlayer class is hypothetical):

```kotlin
class VideoPlayerActivity : AppCompatActivity() {

    private lateinit var player: VideoPlayer

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_video_player)

        player = VideoPlayer(this)
        val videoUrl = intent.getStringExtra("video_url")
        if (videoUrl != null) {
            player.setDataSource(videoUrl)
        }
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
        // Pause playback when Activity is partially obscured
        player.pause()
        super.onPause()
    }

    override fun onStop() {
        // Stop playback when Activity is no longer visible
        player.stop()
        super.onStop()
    }

    override fun onDestroy() {
        // Clean up player resources
        player.release()
        super.onDestroy()
    }
}
```

#### 4. Screen Transitions

`Activity` initiates navigation between different screens (Activities) using intents:

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

`Activity` interacts with other Android components such as Services, BroadcastReceivers, ContentProviders, and `WorkManager`:

```kotlin
class MainDashboardActivity : AppCompatActivity() {

    private var downloadReceiver: BroadcastReceiver? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dashboard)

        // Start a Service for background download (simplified example — for long-running work, prefer WorkManager or a properly declared foreground service)
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
        downloadReceiver = object : BroadcastReceiver() {
            override fun onReceive(context: Context, intent: Intent) {
                Toast.makeText(context, "Download complete", Toast.LENGTH_SHORT).show()
            }
        }

        val filter = IntentFilter("com.example.DOWNLOAD_COMPLETE")
        registerReceiver(downloadReceiver, filter)
    }

    override fun onDestroy() {
        downloadReceiver?.let { unregisterReceiver(it) }
        super.onDestroy()
    }

    private fun loadUserDataFromProvider() {
        val uri = Uri.parse("content://com.example.provider/users")
        val cursor = contentResolver.query(uri, null, null, null, null)

        cursor?.use {
            // Process user data
        }
    }

    private fun scheduleBackgroundSync() {
        val workRequest = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS).build()
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
        val uriToShare = intent.getParcelableExtra<Uri>("photo_uri")
        val shareIntent = Intent(Intent.ACTION_SEND).apply {
            type = "image/*"
            putExtra(Intent.EXTRA_STREAM, uriToShare)
        }
        startActivity(Intent.createChooser(shareIntent, "Share photo"))
    }

    private fun deletePhoto() {
        // Delete photo if permitted and finish Activity
        // contentResolver.delete(photoUri, null, null)
        finish()
    }
}
```

### `Activity` Properties

- Single screen or entry point: typically represents one focused screen or logical entry point.
- Can be started by other apps (if exported via manifest and with appropriate intent filters).
- `Lifecycle` managed by the Android framework.
- Can handle specific `Intent`s when matching intent filters are declared.
- Manages its own UI and related resources.
- Is a `Context`: used for UI-related operations; for application-wide or long-lived usage, prefer `applicationContext` instead of holding an `Activity` reference.

### When to Use `Activity`

- Use an `Activity` for:
  - Distinct screens or flows in your app.
  - Entry points from other apps (deep links, implicit intents, launcher icons).
  - Full-screen or major user experiences.

- Prefer other components instead of a new `Activity` for:
  - Sub-sections of a screen (use Fragments or composable destinations).
  - Temporary UI overlays (use DialogFragment, dialogs, or in-view UI).
  - Background operations (use `Service`, `WorkManager`, coroutines, etc., instead of keeping an `Activity` alive).

---

## Related Topics
- `Activity` lifecycle
- `Intent` system
- `Fragment` vs `Activity`
- Single `Activity` architecture
- Task and back stack

---

## Follow-ups

- [[c-activity-lifecycle]]
- [[c-android-components]]
- [[q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium]]

## References

- [Android Documentation](https://developer.android.com/docs)
- [Lifecycle](https://developer.android.com/topic/libraries/architecture/lifecycle)

## Related Questions

### Prerequisites (Easier)
- [[q-android-components-besides-activity--android--easy]] - `Activity`

### Related (Medium)
- [[q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]] - `Activity`
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - `Activity`
- [[q-single-activity-pros-cons--android--medium]] - `Activity`
- [[q-if-activity-starts-after-a-service-can-you-connect-to-this-service--android--medium]] - `Activity`
- [[q-activity-lifecycle-methods--android--medium]] - `Activity`

### Advanced (Harder)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - `Activity`
