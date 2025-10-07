---
topic: android
tags:
  - android
difficulty: medium
status: draft
---

# What are Intents for?

## Answer

Intents are the fundamental messaging objects in Android used for communication between app components. They serve as the primary mechanism for starting activities, services, broadcasting messages, and passing data.

### Core Purposes of Intents

#### 1. Starting Activities

```kotlin
// Start another Activity in the same app
val intent = Intent(this, DetailActivity::class.java)
startActivity(intent)

// Start Activity with data
val intent = Intent(this, ProductActivity::class.java).apply {
    putExtra("product_id", 123)
    putExtra("product_name", "Laptop")
}
startActivity(intent)

// Start Activity for result
val launcher = registerForActivityResult(
    ActivityResultContracts.StartActivityForResult()
) { result ->
    if (result.resultCode == RESULT_OK) {
        val data = result.data?.getStringExtra("result")
    }
}

launcher.launch(Intent(this, PickerActivity::class.java))
```

#### 2. Starting Services

```kotlin
// Start a Service
val serviceIntent = Intent(this, DownloadService::class.java).apply {
    putExtra("file_url", "https://example.com/file.zip")
}
startService(serviceIntent)

// Bind to a Service
val connection = object : ServiceConnection {
    override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
        val binder = service as MyService.MyBinder
        val myService = binder.getService()
    }

    override fun onServiceDisconnected(name: ComponentName?) {
        // Service disconnected
    }
}

val bindIntent = Intent(this, MyService::class.java)
bindService(bindIntent, connection, Context.BIND_AUTO_CREATE)
```

#### 3. Broadcasting Messages

```kotlin
// Send broadcast
val broadcastIntent = Intent("com.example.CUSTOM_ACTION").apply {
    putExtra("data", "Hello World")
}
sendBroadcast(broadcastIntent)

// Send ordered broadcast
sendOrderedBroadcast(
    Intent("com.example.ORDER_ACTION"),
    null // permission
)

// Send broadcast with permission
sendBroadcast(
    Intent("com.example.PROTECTED_ACTION"),
    "com.example.permission.CUSTOM"
)
```

#### 4. Passing Data Between Components

```kotlin
// Simple data types
val intent = Intent(this, NextActivity::class.java).apply {
    putExtra("string_key", "Hello")
    putExtra("int_key", 42)
    putExtra("boolean_key", true)
    putExtra("double_key", 3.14)
}

// Arrays and lists
intent.putExtra("int_array", intArrayOf(1, 2, 3))
intent.putStringArrayListExtra("string_list", arrayListOf("a", "b", "c"))

// Bundle for grouping
val bundle = Bundle().apply {
    putString("name", "John")
    putInt("age", 30)
}
intent.putExtras(bundle)

// Parcelable objects
@Parcelize
data class User(val id: Int, val name: String) : Parcelable

intent.putExtra("user", User(1, "Alice"))

// Receiving data
class NextActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val stringData = intent.getStringExtra("string_key")
        val intData = intent.getIntExtra("int_key", 0)
        val user = intent.getParcelableExtra<User>("user")
    }
}
```

### Types of Intents

#### Explicit Intents

Target specific component by name:

```kotlin
// Explicit Intent - knows exact component
val explicitIntent = Intent(this, SpecificActivity::class.java)
startActivity(explicitIntent)

// Start specific service
val serviceIntent = Intent(this, MyService::class.java)
startService(serviceIntent)

// Component name
val componentIntent = Intent().apply {
    component = ComponentName(
        "com.example.app",
        "com.example.app.MainActivity"
    )
}
startActivity(componentIntent)
```

#### Implicit Intents

System finds appropriate component based on action and data:

```kotlin
// Open web browser
val webIntent = Intent(Intent.ACTION_VIEW, Uri.parse("https://google.com"))
startActivity(webIntent)

// Share text
val shareIntent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_TEXT, "Check this out!")
}
startActivity(Intent.createChooser(shareIntent, "Share via"))

// Make phone call
val callIntent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:1234567890"))
startActivity(callIntent)

// Open email app
val emailIntent = Intent(Intent.ACTION_SENDTO).apply {
    data = Uri.parse("mailto:")
    putExtra(Intent.EXTRA_EMAIL, arrayOf("user@example.com"))
    putExtra(Intent.EXTRA_SUBJECT, "Hello")
}
startActivity(emailIntent)

// Take photo
val photoIntent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
cameraLauncher.launch(photoIntent)

// Pick image from gallery
val galleryIntent = Intent(Intent.ACTION_PICK).apply {
    type = "image/*"
}
galleryLauncher.launch(galleryIntent)

// Open map location
val mapIntent = Intent(Intent.ACTION_VIEW, Uri.parse("geo:37.7749,-122.4194"))
startActivity(mapIntent)
```

### Intent Components

```kotlin
val intent = Intent().apply {
    // 1. Action - what to do
    action = Intent.ACTION_VIEW

    // 2. Data - data to operate on
    data = Uri.parse("https://example.com")

    // 3. Category - additional info about action
    addCategory(Intent.CATEGORY_BROWSABLE)

    // 4. Type - MIME type of data
    type = "text/plain"

    // 5. Component - specific component to use
    component = ComponentName(packageName, "com.example.TargetActivity")

    // 6. Extras - additional data
    putExtra("key", "value")

    // 7. Flags - control behavior
    flags = Intent.FLAG_ACTIVITY_NEW_TASK
}
```

### Intent Flags

Control Activity behavior:

```kotlin
// Start Activity in new task
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK

// Clear all activities above target
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP

// Don't create new instance if already on top
intent.flags = Intent.FLAG_ACTIVITY_SINGLE_TOP

// Clear task and start new
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TASK or Intent.FLAG_ACTIVITY_NEW_TASK

// Bring existing Activity to front
intent.flags = Intent.FLAG_ACTIVITY_REORDER_TO_FRONT

// Don't add to back stack
intent.flags = Intent.FLAG_ACTIVITY_NO_HISTORY

// Multiple flags
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or
               Intent.FLAG_ACTIVITY_CLEAR_TOP or
               Intent.FLAG_ACTIVITY_SINGLE_TOP
```

### Common Intent Actions

```kotlin
// View actions
Intent.ACTION_VIEW          // Display data
Intent.ACTION_EDIT          // Edit data
Intent.ACTION_PICK          // Pick item from data

// Communication
Intent.ACTION_SEND          // Send data
Intent.ACTION_SENDTO        // Send to someone
Intent.ACTION_DIAL          // Dial phone number
Intent.ACTION_CALL          // Call phone number (requires permission)

// Media
Intent.ACTION_IMAGE_CAPTURE     // Take photo
Intent.ACTION_VIDEO_CAPTURE     // Record video
MediaStore.ACTION_IMAGE_CAPTURE // Take photo (alternative)

// System
Intent.ACTION_MAIN          // Main entry point
Intent.ACTION_SEARCH        // Perform search
Intent.ACTION_WEB_SEARCH    // Web search
Intent.ACTION_SETTINGS      // System settings
```

### Intent Filters

Declare what Intents a component can handle:

```xml
<!-- In AndroidManifest.xml -->
<activity android:name=".ViewerActivity">
    <intent-filter>
        <!-- Can view web pages -->
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="https" />
    </intent-filter>

    <intent-filter>
        <!-- Can handle custom scheme -->
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <data android:scheme="myapp" android:host="product" />
    </intent-filter>
</activity>
```

### Checking Intent Availability

```kotlin
fun safeStartActivity(intent: Intent) {
    if (intent.resolveActivity(packageManager) != null) {
        startActivity(intent)
    } else {
        Toast.makeText(this, "No app can handle this action", Toast.LENGTH_SHORT).show()
    }
}

// Query all apps that can handle intent
val resolveInfoList = packageManager.queryIntentActivities(
    intent,
    PackageManager.MATCH_DEFAULT_ONLY
)

if (resolveInfoList.isNotEmpty()) {
    startActivity(intent)
}
```

### PendingIntent

Intent that can be executed by another app:

```kotlin
// For notification
val notificationIntent = Intent(this, MainActivity::class.java)
val pendingIntent = PendingIntent.getActivity(
    this,
    0,
    notificationIntent,
    PendingIntent.FLAG_IMMUTABLE
)

val notification = NotificationCompat.Builder(this, CHANNEL_ID)
    .setContentTitle("Title")
    .setContentText("Text")
    .setContentIntent(pendingIntent)
    .build()

// For alarm
val alarmIntent = Intent(this, AlarmReceiver::class.java)
val alarmPendingIntent = PendingIntent.getBroadcast(
    this,
    0,
    alarmIntent,
    PendingIntent.FLAG_IMMUTABLE
)

val alarmManager = getSystemService(AlarmManager::class.java)
alarmManager.setExact(
    AlarmManager.RTC_WAKEUP,
    triggerTime,
    alarmPendingIntent
)
```

### Intent vs Bundle

| Aspect | Intent | Bundle |
|--------|--------|--------|
| Purpose | Start components + carry data | Carry data only |
| Can start components | Yes | No |
| Contains extras | Yes (as Bundle) | N/A |
| Has action/data | Yes | No |
| Typical use | Component communication | Data passing, state saving |

### Practical Examples

```kotlin
// Example 1: Social media share
fun shareContent(text: String, imageUri: Uri?) {
    val shareIntent = Intent(Intent.ACTION_SEND).apply {
        type = if (imageUri != null) "image/*" else "text/plain"
        putExtra(Intent.EXTRA_TEXT, text)
        imageUri?.let { putExtra(Intent.EXTRA_STREAM, it) }
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    }
    startActivity(Intent.createChooser(shareIntent, "Share via"))
}

// Example 2: Open external app
fun openInBrowser(url: String) {
    val browserIntent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
    if (browserIntent.resolveActivity(packageManager) != null) {
        startActivity(browserIntent)
    }
}

// Example 3: Custom deep link
fun handleDeepLink(uri: Uri) {
    val intent = Intent(Intent.ACTION_VIEW, uri).apply {
        setPackage(packageName) // Force this app
    }
    startActivity(intent)
}

// Example 4: Result from Activity
val pickContactLauncher = registerForActivityResult(
    ActivityResultContracts.PickContact()
) { contactUri: Uri? ->
    contactUri?.let {
        // Handle selected contact
        val cursor = contentResolver.query(it, null, null, null, null)
        cursor?.use {
            if (it.moveToFirst()) {
                val name = it.getString(it.getColumnIndex(ContactsContract.Contacts.DISPLAY_NAME))
            }
        }
    }
}

fun pickContact() {
    pickContactLauncher.launch(null)
}
```

### Summary

Intents are used for:
1. **Starting Activities** - Navigate between screens
2. **Starting Services** - Launch background operations
3. **Broadcasting** - Send messages to multiple receivers
4. **Passing data** - Transfer information between components
5. **External app integration** - Share content, open URLs, etc.

**Two types**:
- **Explicit**: Targets specific component by name
- **Implicit**: System finds suitable component based on action/data

## Answer (RU)
Intents нужны для взаимодействия компонентов приложения: запуска Activity, Service, передачи данных или отправки Broadcast. Они являются основным способом коммуникации между модулями и приложениями в Android

## Related Topics
- Intent filters
- Explicit vs Implicit Intents
- PendingIntent
- Activity launch modes
- Deep linking
