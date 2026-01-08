---\
id: "20251025-110314"
title: "Android Permissions / Разрешения Android"
aliases: ["Android Permissions", "Permissions", "Runtime Permissions", "Разрешения Времени Выполнения", "Разрешения"]
summary: "System for controlling app access to sensitive user data and device features"
topic: "android"
subtopics: ["permissions", "privacy", "security"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: ["c-android-manifest", "c-security", "c-scoped-storage", "c-privacy-by-design", "c-biometric-authentication"]
created: "2025-10-25"
updated: "2025-10-25"
tags: ["android", "concept", "difficulty/medium", "permissions", "privacy", "security"]
---\

# Android Permissions / Разрешения Android

## Summary (EN)

Android permissions are a security mechanism that controls app access to sensitive user data and device features. Apps must declare required permissions in the manifest, and starting from Android 6.0 (API 23), dangerous permissions require explicit user approval at runtime. The permission system protects user privacy by ensuring users are informed and in control of what data and features apps can access.

## Краткое Описание (RU)

Разрешения Android - это механизм безопасности, контролирующий доступ приложений к конфиденциальным пользовательским данным и функциям устройства. Приложения должны объявлять требуемые разрешения в манифесте, и начиная с Android 6.0 (API 23), опасные разрешения требуют явного одобрения пользователя во время выполнения. Система разрешений защищает конфиденциальность пользователей, гарантируя, что пользователи информированы и контролируют, какие данные и функции могут использовать приложения.

## Key Points (EN)

- **Permission types**: Normal, dangerous, signature, special
- **Runtime permissions**: Required for dangerous permissions on API 23+
- **Permission groups**: Related permissions grouped together
- **Grant modes**: Install-time vs runtime
- **User control**: Users can revoke permissions at any time
- **Best practices**: `Request` only necessary permissions, explain why needed
- **Android 11+**: One-time permissions and auto-reset

## Ключевые Моменты (RU)

- **Типы разрешений**: Обычные, опасные, подписи, специальные
- **Разрешения времени выполнения**: Требуются для опасных разрешений на API 23+
- **Группы разрешений**: Связанные разрешения сгруппированы вместе
- **Режимы предоставления**: Во время установки vs во время выполнения
- **Контроль пользователя**: Пользователи могут отозвать разрешения в любое время
- **Лучшие практики**: Запрашивать только необходимые разрешения, объяснять зачем нужны
- **Android 11+**: Одноразовые разрешения и автосброс

## Permission Types

### Normal Permissions

Automatically granted at install time, don't pose privacy risk.

```xml
<!-- AndroidManifest.xml -->
<manifest>
    <!-- Normal permissions - granted automatically -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.VIBRATE" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
</manifest>
```

**Examples**: Internet access, network state, vibrate, wake lock

### Dangerous Permissions

Require runtime request on Android 6.0+ (API 23), affect user privacy.

```xml
<manifest>
    <!-- Dangerous permissions - require runtime request -->
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.READ_CONTACTS" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
</manifest>
```

**Permission Groups**:
- **Calendar**: READ_CALENDAR, WRITE_CALENDAR
- **Camera**: CAMERA
- **Contacts**: READ_CONTACTS, WRITE_CONTACTS, GET_ACCOUNTS
- **Location**: ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION
- **Microphone**: RECORD_AUDIO
- **Phone**: READ_PHONE_STATE, CALL_PHONE, READ_CALL_LOG, etc.
- **Sensors**: BODY_SENSORS
- **SMS**: SEND_SMS, RECEIVE_SMS, READ_SMS, etc.
- **Storage**: READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

### Signature Permissions

Only granted to apps signed with the same certificate as the declaring app.

```xml
<!-- Define custom signature permission -->
<permission
    android:name="com.example.permission.CUSTOM_PERMISSION"
    android:protectionLevel="signature" />

<!-- Use the permission -->
<uses-permission android:name="com.example.permission.CUSTOM_PERMISSION" />
```

### Special Permissions

Require special handling, user navigates to Settings.

```kotlin
// SYSTEM_ALERT_WINDOW - Draw over other apps
if (!Settings.canDrawOverlays(this)) {
    val intent = Intent(
        Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
        Uri.parse("package:$packageName")
    )
    startActivityForResult(intent, REQUEST_CODE_OVERLAY)
}

// WRITE_SETTINGS - Modify system settings
if (!Settings.System.canWrite(this)) {
    val intent = Intent(
        Settings.ACTION_MANAGE_WRITE_SETTINGS,
        Uri.parse("package:$packageName")
    )
    startActivityForResult(intent, REQUEST_CODE_WRITE_SETTINGS)
}

// REQUEST_IGNORE_BATTERY_OPTIMIZATIONS
val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
if (!powerManager.isIgnoringBatteryOptimizations(packageName)) {
    val intent = Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS).apply {
        data = Uri.parse("package:$packageName")
    }
    startActivity(intent)
}
```

## Requesting Runtime Permissions

### Basic Permission Request

```kotlin
class MainActivity : AppCompatActivity() {
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        if (isGranted) {
            // Permission granted - proceed with feature
            accessCamera()
        } else {
            // Permission denied - show explanation or disable feature
            showPermissionDeniedMessage()
        }
    }

    private fun requestCameraPermission() {
        when {
            // Check if permission is already granted
            ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.CAMERA
            ) == PackageManager.PERMISSION_GRANTED -> {
                // Permission already granted
                accessCamera()
            }

            // Show rationale if needed
            shouldShowRequestPermissionRationale(Manifest.permission.CAMERA) -> {
                // Show explanation why permission is needed
                showPermissionRationale {
                    // After explanation, request permission
                    requestPermissionLauncher.launch(Manifest.permission.CAMERA)
                }
            }

            else -> {
                // Directly request permission
                requestPermissionLauncher.launch(Manifest.permission.CAMERA)
            }
        }
    }

    private fun accessCamera() {
        // Use camera feature
    }

    private fun showPermissionRationale(onPositive: () -> Unit) {
        AlertDialog.Builder(this)
            .setTitle("Camera Permission Needed")
            .setMessage("This feature requires camera access to take photos.")
            .setPositiveButton("Grant") { _, _ -> onPositive() }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun showPermissionDeniedMessage() {
        Toast.makeText(this, "Camera permission is required", Toast.LENGTH_SHORT).show()
    }
}
```

### Multiple Permissions Request

```kotlin
class MainActivity : AppCompatActivity() {
    private val requestMultiplePermissions = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val allGranted = permissions.entries.all { it.value }

        if (allGranted) {
            // All permissions granted
            startFeature()
        } else {
            // Some permissions denied
            val deniedPermissions = permissions.filterValues { !it }.keys
            handleDeniedPermissions(deniedPermissions)
        }
    }

    private fun requestLocationAndCamera() {
        val permissions = arrayOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.CAMERA
        )

        requestMultiplePermissions.launch(permissions)
    }

    private fun handleDeniedPermissions(denied: Set<String>) {
        denied.forEach { permission ->
            when (permission) {
                Manifest.permission.ACCESS_FINE_LOCATION -> {
                    // Handle location denied
                }
                Manifest.permission.CAMERA -> {
                    // Handle camera denied
                }
            }
        }
    }
}
```

### Checking Permissions Before Use

```kotlin
fun takePicture() {
    if (ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.CAMERA
        ) == PackageManager.PERMISSION_GRANTED
    ) {
        // Permission is granted - safe to use camera
        openCamera()
    } else {
        // Permission not granted - request it
        requestCameraPermission()
    }
}

fun checkMultiplePermissions(): Boolean {
    val permissions = arrayOf(
        Manifest.permission.CAMERA,
        Manifest.permission.RECORD_AUDIO
    )

    return permissions.all { permission ->
        ContextCompat.checkSelfPermission(this, permission) == PackageManager.PERMISSION_GRANTED
    }
}
```

## Modern Permission Features

### Android 11+ One-Time Permissions

```kotlin
// User can grant permission "Only this time"
// Permission is automatically revoked when app goes to background

// Check if permission was revoked
override fun onResume() {
    super.onResume()

    if (ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.CAMERA
        ) != PackageManager.PERMISSION_GRANTED
    ) {
        // Permission was revoked (possibly one-time grant expired)
        // Request again if feature is needed
    }
}
```

### Android 11+ Auto-Reset Permissions

```kotlin
// Permissions for unused apps are automatically reset after few months
// No code change needed, but be prepared for permission being revoked

// Best practice: Always check permission before use
private fun useFeature() {
    if (hasPermission()) {
        // Proceed
    } else {
        // Request permission again
    }
}
```

### Android 12+ Approximate Location

```xml
<!-- Request both precise and approximate location -->
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
```

```kotlin
// User can choose to grant approximate location only
private fun requestLocation() {
    requestMultiplePermissions.launch(
        arrayOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )
    )
}

// Check which location permission was granted
private fun getLocationAccuracy(): LocationAccuracy {
    return when {
        ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED -> LocationAccuracy.PRECISE

        ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.ACCESS_COARSE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED -> LocationAccuracy.APPROXIMATE

        else -> LocationAccuracy.NONE
    }
}
```

### Android 13+ Notification Permission

```xml
<!-- Required for Android 13+ to show notifications -->
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
```

```kotlin
private fun requestNotificationPermission() {
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        if (ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.POST_NOTIFICATIONS
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            requestPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
        }
    }
}
```

## Scoped Storage (Android 10+)

```kotlin
// Android 10+ restricts direct file access
// Use MediaStore API instead

// Writing image to MediaStore
private fun saveImage(bitmap: Bitmap) {
    val contentValues = ContentValues().apply {
        put(MediaStore.Images.Media.DISPLAY_NAME, "image_${System.currentTimeMillis()}.jpg")
        put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES)
        }
    }

    val uri = contentResolver.insert(
        MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
        contentValues
    )

    uri?.let {
        contentResolver.openOutputStream(it)?.use { outputStream ->
            bitmap.compress(Bitmap.CompressFormat.JPEG, 100, outputStream)
        }
    }
}

// Reading images from MediaStore
private fun loadImages(): List<Uri> {
    val images = mutableListOf<Uri>()
    val projection = arrayOf(MediaStore.Images.Media._ID)

    contentResolver.query(
        MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
        projection,
        null,
        null,
        "${MediaStore.Images.Media.DATE_ADDED} DESC"
    )?.use { cursor ->
        val idColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.Media._ID)

        while (cursor.moveToNext()) {
            val id = cursor.getLong(idColumn)
            val uri = ContentUris.withAppendedId(
                MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                id
            )
            images.add(uri)
        }
    }

    return images
}

// For legacy app-specific files, use app-specific directory (no permission needed)
private fun saveToAppStorage(data: String) {
    val file = File(getExternalFilesDir(null), "data.txt")
    file.writeText(data)
    // No permission needed for app-specific directory
}
```

## Permission Helper Class

```kotlin
object PermissionHelper {
    fun hasPermission(context: Context, permission: String): Boolean {
        return ContextCompat.checkSelfPermission(
            context,
            permission
        ) == PackageManager.PERMISSION_GRANTED
    }

    fun hasPermissions(context: Context, permissions: Array<String>): Boolean {
        return permissions.all { hasPermission(context, it) }
    }

    fun shouldShowRationale(activity: Activity, permission: String): Boolean {
        return activity.shouldShowRequestPermissionRationale(permission)
    }

    fun openAppSettings(context: Context) {
        val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
            data = Uri.fromParts("package", context.packageName, null)
        }
        context.startActivity(intent)
    }

    // Permission groups for common features
    object Groups {
        val CAMERA = arrayOf(Manifest.permission.CAMERA)

        val LOCATION = arrayOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )

        val STORAGE = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            arrayOf(
                Manifest.permission.READ_MEDIA_IMAGES,
                Manifest.permission.READ_MEDIA_VIDEO,
                Manifest.permission.READ_MEDIA_AUDIO
            )
        } else {
            arrayOf(
                Manifest.permission.READ_EXTERNAL_STORAGE,
                Manifest.permission.WRITE_EXTERNAL_STORAGE
            )
        }

        val CONTACTS = arrayOf(
            Manifest.permission.READ_CONTACTS,
            Manifest.permission.WRITE_CONTACTS
        )
    }
}

// Usage
if (PermissionHelper.hasPermission(this, Manifest.permission.CAMERA)) {
    openCamera()
} else {
    requestCameraPermission()
}
```

## Use Cases

### When to Request Permissions

- **Camera access**: Taking photos or videos
- **Location access**: Maps, navigation, location-based features
- **Storage access**: Reading/writing files, photos
- **Contacts access**: Contact picker, messaging
- **Microphone access**: Voice recording, calls
- **Phone state**: Reading phone number, call status
- **Calendar access**: Event management
- **SMS access**: Reading or sending messages

### When to Avoid Requesting Permissions

- **Unnecessary features**: Don't request if feature isn't core
- **Alternative approaches**: Use intents instead (camera intent vs CAMERA permission)
- **Privacy concerns**: Minimize data collection
- **User trust**: Too many permission requests decrease trust

## Trade-offs

**Pros**:
- **User privacy**: Users control sensitive data access
- **Security**: Prevents malicious apps from accessing data
- **Transparency**: Users know what apps can access
- **Granular control**: Can revoke individual permissions
- **Trust**: Clear permission model builds user confidence

**Cons**:
- **User experience**: Multiple permission dialogs can be annoying
- **Complexity**: Developers must handle all permission states
- **Fragmentation**: Different behavior across Android versions
- **Permission fatigue**: Users may blindly accept or deny
- **Development effort**: More code to handle permissions properly

## Best Practices

1. **`Request` in context**: Ask for permission when user initiates related feature
2. **Explain why**: Show rationale before requesting
3. **`Request` minimum**: Only request necessary permissions
4. **Handle denials gracefully**: Provide alternative functionality
5. **Check before use**: Always verify permission before accessing resource
6. **Use intents when possible**: Camera/file picker intents don't need permissions
7. **Target latest API**: Stay current with permission model changes
8. **Test all scenarios**: Grant, deny, "Don't ask again", revoke
9. **Respect user choice**: Don't repeatedly ask if denied
10. **Link to settings**: Provide easy way to grant from Settings

## Handling "Don't Ask Again"

```kotlin
private fun handlePermissionDenied(permission: String) {
    when {
        shouldShowRequestPermissionRationale(permission) -> {
            // User denied, but can be asked again
            showPermissionRationale {
                requestPermissionLauncher.launch(permission)
            }
        }
        else -> {
            // User selected "Don't ask again" or first time asking
            // Direct to app settings
            AlertDialog.Builder(this)
                .setTitle("Permission Required")
                .setMessage("This permission is required for this feature. Please enable it in Settings.")
                .setPositiveButton("Open Settings") { _, _ ->
                    PermissionHelper.openAppSettings(this)
                }
                .setNegativeButton("Cancel", null)
                .show()
        }
    }
}
```

## Related Concepts

- [[c-broadcast-receiver]]
- [[c-lifecycle]]
- [[c-memory-management]]

## References

- [Request App Permissions](https://developer.android.com/training/permissions/requesting)
- [Permissions Overview](https://developer.android.com/guide/topics/permissions/overview)
- [Permission Best Practices](https://developer.android.com/training/permissions/usage-notes)
- [Scoped Storage](https://developer.android.com/training/data-storage#scoped-storage)
- [Android 11 Privacy](https://developer.android.com/about/versions/11/privacy)
- [Android 12 Privacy](https://developer.android.com/about/versions/12/behavior-changes-12#approximate-location)
- [Android 13 Privacy](https://developer.android.com/about/versions/13/changes/notification-permission)
