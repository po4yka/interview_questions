---
id: "20251015082237521"
title: "Factory Pattern Android / Factory Паттерн Android"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [android-framework, android/architecture-clean, architecture-clean, design-patterns, factory-pattern, platform/android, difficulty/medium]
---
# Можешь привести пример когда android фреймворк использует паттерн Factory

**English**: Can you give an example of when the Android framework uses the Factory pattern

## Answer (EN)
Yes, the Android Framework extensively uses the Factory pattern throughout its APIs. Here are the most prominent examples:

### 1. LayoutInflater (Factory Method Pattern)

The most famous example - LayoutInflater creates View instances from XML layouts.

```kotlin
// Factory method that creates View objects
val inflater = LayoutInflater.from(context)
val view = inflater.inflate(R.layout.custom_layout, parent, false)

// Behind the scenes, LayoutInflater uses reflection and factory methods
// to instantiate appropriate View subclasses based on XML tags:
// <TextView> → new TextView(context)
// <Button> → new Button(context)
// <RecyclerView> → new RecyclerView(context)
```

**How it works:**
```kotlin
// Simplified LayoutInflater implementation
class LayoutInflater {
    fun inflate(resource: Int, parent: ViewGroup?, attachToRoot: Boolean): View {
        val parser = resources.getLayout(resource)

        // Factory method creates views based on XML tags
        return createViewFromTag(parser.name, context, attrs)
    }

    private fun createViewFromTag(name: String, context: Context, attrs: AttributeSet): View {
        // Factory pattern: creates different View types
        return when (name) {
            "TextView" -> TextView(context, attrs)
            "Button" -> Button(context, attrs)
            "ImageView" -> ImageView(context, attrs)
            "LinearLayout" -> LinearLayout(context, attrs)
            else -> Class.forName(name).getConstructor(Context::class.java, AttributeSet::class.java)
                .newInstance(context, attrs) as View
        }
    }
}
```

**Usage in Activity:**
```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Factory method - inflates XML to create View hierarchy
        setContentView(R.layout.activity_main)

        // Or explicit factory usage
        val inflater = LayoutInflater.from(this)
        val customView = inflater.inflate(R.layout.custom_view, null)
    }
}
```

**In RecyclerView.Adapter:**
```kotlin
class MyAdapter : RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        // Factory method using LayoutInflater
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView)
}
```

### 2. Fragment.instantiate() (Factory Pattern)

Creates Fragment instances without directly calling constructors.

```kotlin
// Factory method for creating fragments
val fragment = Fragment.instantiate(context, MyFragment::class.java.name)

// With arguments
val args = Bundle().apply {
    putString("key", "value")
}
val fragment = Fragment.instantiate(context, MyFragment::class.java.name, args)

// Modern approach using FragmentFactory
class MyFragmentFactory : FragmentFactory() {
    override fun instantiate(classLoader: ClassLoader, className: String): Fragment {
        return when (className) {
            ProfileFragment::class.java.name -> ProfileFragment(viewModel)
            SettingsFragment::class.java.name -> SettingsFragment(repository)
            else -> super.instantiate(classLoader, className)
        }
    }
}

// Set custom factory
supportFragmentManager.fragmentFactory = MyFragmentFactory()
```

### 3. ViewModelProvider.Factory

Creates ViewModel instances with dependency injection.

```kotlin
class MyViewModelFactory(
    private val repository: UserRepository
) : ViewModelProvider.Factory {

    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        // Factory pattern: creates ViewModel based on class type
        return when {
            modelClass.isAssignableFrom(UserViewModel::class.java) -> {
                UserViewModel(repository) as T
            }
            modelClass.isAssignableFrom(ProfileViewModel::class.java) -> {
                ProfileViewModel(repository) as T
            }
            else -> throw IllegalArgumentException("Unknown ViewModel class")
        }
    }
}

// Usage
class MyActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels {
        MyViewModelFactory(userRepository)
    }
}
```

### 4. MediaPlayer.create() (Static Factory Method)

Factory method that creates and configures MediaPlayer.

```kotlin
// Static factory method - creates and prepares MediaPlayer in one step
val mediaPlayer = MediaPlayer.create(context, R.raw.audio_file)
mediaPlayer.start()

// Equivalent manual creation (more complex)
val mediaPlayer = MediaPlayer().apply {
    setDataSource(context, Uri.parse("android.resource://$packageName/${R.raw.audio_file}"))
    prepare() // Could throw exception
}
mediaPlayer.start()
```

**Advantages of factory method:**
- Handles resource loading
- Automatic preparation
- Exception handling
- Returns ready-to-use object

```kotlin
// Usage in Service
class MusicService : Service() {
    private var mediaPlayer: MediaPlayer? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Factory method simplifies creation
        mediaPlayer = MediaPlayer.create(this, R.raw.background_music)
        mediaPlayer?.start()

        return START_STICKY
    }
}
```

### 5. Notification.Builder (Builder Pattern - Factory Variant)

Creates complex Notification objects.

```kotlin
// Builder pattern (factory variant) for creating notifications
val notification = NotificationCompat.Builder(context, CHANNEL_ID)
    .setContentTitle("New Message")
    .setContentText("You have a new message")
    .setSmallIcon(R.drawable.ic_notification)
    .setPriority(NotificationCompat.PRIORITY_HIGH)
    .setAutoCancel(true)
    .setContentIntent(pendingIntent)
    .build() // Factory method returns final Notification

val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
notificationManager.notify(NOTIFICATION_ID, notification)
```

### 6. Intent (Factory Methods)

Multiple factory methods for creating different Intent types.

```kotlin
// Factory methods for common intents
val dialIntent = Intent.makeMainActivity(componentName)
val restartIntent = Intent.makeRestartActivityTask(componentName)

// Implicit intent factories
val callIntent = Intent(Intent.ACTION_DIAL).apply {
    data = Uri.parse("tel:1234567890")
}

val emailIntent = Intent(Intent.ACTION_SENDTO).apply {
    data = Uri.parse("mailto:")
    putExtra(Intent.EXTRA_EMAIL, arrayOf("test@example.com"))
}

// Share intent factory
val shareIntent = Intent.createChooser(
    Intent(Intent.ACTION_SEND).apply {
        type = "text/plain"
        putExtra(Intent.EXTRA_TEXT, "Share this text")
    },
    "Share via"
)
```

### 7. Bitmap.createBitmap() (Static Factory)

Factory methods for creating Bitmap objects.

```kotlin
// Factory methods for different Bitmap creation scenarios
val bitmap1 = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)

val bitmap2 = Bitmap.createBitmap(sourceBitmap, x, y, width, height)

val bitmap3 = Bitmap.createScaledBitmap(sourceBitmap, newWidth, newHeight, filter = true)

// Factory with transformation matrix
val matrix = Matrix().apply {
    postRotate(90f)
}
val rotatedBitmap = Bitmap.createBitmap(
    sourceBitmap,
    0, 0,
    sourceBitmap.width,
    sourceBitmap.height,
    matrix,
    true
)
```

### 8. Executors (Factory for ThreadPools)

Factory methods for creating different executor types.

```kotlin
// Factory methods for creating thread pools
val singleThreadExecutor = Executors.newSingleThreadExecutor()
val fixedThreadPool = Executors.newFixedThreadPool(4)
val cachedThreadPool = Executors.newCachedThreadPool()
val scheduledExecutor = Executors.newScheduledThreadPool(2)

// Usage
singleThreadExecutor.execute {
    // Background task
    performNetworkRequest()
}
```

### 9. Context.getSystemService() (Service Locator/Factory)

Factory method that returns different system services.

```kotlin
// Factory pattern: returns different service types based on constant
val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
val locationManager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager

// Type-safe variant (API 23+)
val notificationManager = context.getSystemService(NotificationManager::class.java)
val locationManager = context.getSystemService(LocationManager::class.java)

// Behind the scenes (simplified)
fun getSystemService(name: String): Any? {
    return when (name) {
        NOTIFICATION_SERVICE -> NotificationManager(...)
        LOCATION_SERVICE -> LocationManager(...)
        CONNECTIVITY_SERVICE -> ConnectivityManager(...)
        // ... many more services
        else -> null
    }
}
```

### 10. Camera.open() (Factory with Resource Management)

```kotlin
// Factory method that opens camera with resource management
val camera = Camera.open(cameraId)

// Camera2 API uses factory pattern too
val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
cameraManager.openCamera(cameraId, stateCallback, handler)
```

### 11. Drawable.createFromStream() (Factory)

```kotlin
// Factory methods for creating Drawable from various sources
val drawable1 = Drawable.createFromStream(inputStream, "source_name")
val drawable2 = Drawable.createFromPath("/path/to/image.png")
val drawable3 = Drawable.createFromResourceStream(resources, typedValue, inputStream, "source")

// Modern approach
val drawable = ResourcesCompat.getDrawable(resources, R.drawable.icon, theme)
```

### 12. AsyncTask.execute() (Factory + Command Pattern)

```kotlin
// Factory pattern combined with Command pattern
class DownloadTask : AsyncTask<String, Int, String>() {
    override fun doInBackground(vararg params: String): String {
        // Background work
        return downloadFile(params[0])
    }

    override fun onPostExecute(result: String) {
        // UI update
        updateUI(result)
    }
}

// Factory method for execution
DownloadTask().execute("https://example.com/file.zip")

// With custom executor (factory)
DownloadTask().executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR, "url")
```

### 13. PendingIntent (Factory Methods)

```kotlin
// Different factory methods for different intent types
val activityPendingIntent = PendingIntent.getActivity(
    context,
    requestCode,
    intent,
    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
)

val servicePendingIntent = PendingIntent.getService(
    context,
    requestCode,
    intent,
    PendingIntent.FLAG_IMMUTABLE
)

val broadcastPendingIntent = PendingIntent.getBroadcast(
    context,
    requestCode,
    intent,
    PendingIntent.FLAG_IMMUTABLE
)
```

### 14. Cursor and ContentProvider (Factory Pattern)

```kotlin
// Factory method returns Cursor with data
val cursor = contentResolver.query(
    uri,
    projection,
    selection,
    selectionArgs,
    sortOrder
)

// Behind the scenes, different cursor implementations are created
// based on the content provider
```

### Summary Table

| Android API | Factory Type | Purpose |
|------------|--------------|---------|
| LayoutInflater | Factory Method | Create Views from XML |
| Fragment.instantiate() | Factory Method | Create Fragment instances |
| ViewModelProvider.Factory | Abstract Factory | Create ViewModels with DI |
| MediaPlayer.create() | Static Factory | Create configured MediaPlayer |
| Notification.Builder | Builder (Factory) | Create complex Notifications |
| Intent factory methods | Static Factory | Create common Intents |
| Bitmap.createBitmap() | Static Factory | Create Bitmap instances |
| Executors | Static Factory | Create thread pools |
| getSystemService() | Service Locator/Factory | Retrieve system services |
| PendingIntent | Static Factory | Create PendingIntent types |

### Why Factory Pattern is Used in Android

1. **Encapsulation** - Hides complex creation logic
2. **Flexibility** - Easy to change implementation without affecting client code
3. **Resource management** - Handles system resources properly
4. **Type safety** - Returns specific types based on parameters
5. **Centralized creation** - Single point for object creation
6. **Configuration** - Objects can be pre-configured (MediaPlayer.create())

### Custom Factory Pattern Example

```kotlin
// Custom factory for creating different types of dialogs
class DialogFactory(private val context: Context) {

    fun createAlertDialog(title: String, message: String): AlertDialog {
        return AlertDialog.Builder(context)
            .setTitle(title)
            .setMessage(message)
            .setPositiveButton("OK") { dialog, _ -> dialog.dismiss() }
            .create()
    }

    fun createConfirmDialog(
        title: String,
        message: String,
        onConfirm: () -> Unit
    ): AlertDialog {
        return AlertDialog.Builder(context)
            .setTitle(title)
            .setMessage(message)
            .setPositiveButton("Confirm") { _, _ -> onConfirm() }
            .setNegativeButton("Cancel") { dialog, _ -> dialog.dismiss() }
            .create()
    }

    fun createListDialog(
        title: String,
        items: Array<String>,
        onItemClick: (Int) -> Unit
    ): AlertDialog {
        return AlertDialog.Builder(context)
            .setTitle(title)
            .setItems(items) { _, which -> onItemClick(which) }
            .create()
    }
}

// Usage
val dialogFactory = DialogFactory(this)
val dialog = dialogFactory.createConfirmDialog(
    "Delete Item",
    "Are you sure?"
) {
    deleteItem()
}
dialog.show()
```

## Ответ (RU)
Да, Android Framework активно использует паттерн Factory в различных API. Самые известные примеры:

**LayoutInflater (Фабричный метод)** - создаёт View из XML. Вместо ручного создания объектов View, система предоставляет фабричный метод inflate(), который создаёт экземпляры View на основе XML-тегов.

```kotlin
val inflater = LayoutInflater.from(context)
val view = inflater.inflate(R.layout.custom_layout, parent, false)
```

**Другие примеры:**
- **MediaPlayer.create()** - создаёт и настраивает MediaPlayer автоматически
- **Fragment.instantiate()** - фабричный метод для создания Fragment без явного вызова конструктора
- **ViewModelProvider.Factory** - создаёт ViewModel с внедрением зависимостей
- **Bitmap.createBitmap()** - статические фабричные методы для создания Bitmap
- **getSystemService()** - возвращает различные системные сервисы
- **PendingIntent.getActivity/getService/getBroadcast()** - фабричные методы для разных типов PendingIntent
- **Notification.Builder** - паттерн Builder (вариант Factory) для создания уведомлений

**Преимущества:**
- Скрывает сложную логику создания объектов
- Позволяет легко менять реализацию
- Управляет системными ресурсами
- Предоставляет типобезопасность
- Может возвращать предварительно настроенные объекты

## Related Topics
- Design Patterns
- Dependency Injection
- Builder Pattern
- Abstract Factory Pattern
- Object Creation Patterns
