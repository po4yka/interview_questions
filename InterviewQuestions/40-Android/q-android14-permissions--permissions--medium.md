---
id: 20251012-122776
title: "Android14 Permissions / Разрешения Android 14"
topic: permissions
difficulty: medium
status: draft
created: 2025-10-15
tags: [android14, android13, privacy, photos, notifications, compatibility, difficulty/medium]
---
# Android 14 Permission Changes / Изменения разрешений в Android 14

**English**: Implement Android 14 permission changes: photo picker for partial media access, notification permissions, and background location restrictions.

## Answer (EN)
**Android 14** (API 34) and **Android 13** (API 33) introduced significant privacy-focused permission changes. The most impactful are granular photo/video access, mandatory notification permissions, and stricter background location requirements. Proper implementation requires version checks and backward compatibility handling.

### Key Permission Changes by Android Version

#### Android 14 (API 34)
- **Partial Photo/Video Access**: Users can select specific photos
- **Health Connect Permissions**: New health data permissions
- **Background Location Further Restricted**: More explicit user consent
- **Foreground Service Types**: More granular service permissions

#### Android 13 (API 33)
- **Notification Permission**: POST_NOTIFICATIONS required
- **Granular Media Permissions**: Separate for images, videos, audio
- **Nearby Wi-Fi Devices**: New NEARBY_WIFI_DEVICES permission
- **Body Sensors Background**: Separate permission for background access

### Complete Implementation

#### 1. Photo Picker Implementation (Android 13+)

```kotlin
import android.net.Uri
import android.os.Build
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity

/**
 * Modern photo picker implementation
 */
class PhotoPickerManager(private val activity: AppCompatActivity) {

    // Single photo picker
    private val singlePhotoPickerLauncher = activity.registerForActivityResult(
        ActivityResultContracts.PickVisualMedia()
    ) { uri: Uri? ->
        uri?.let { selectedPhotoUri ->
            handleSelectedPhoto(selectedPhotoUri)
        }
    }

    // Multiple photos picker
    private val multiplePhotosPickerLauncher = activity.registerForActivityResult(
        ActivityResultContracts.PickMultipleVisualMedia(maxItems = 10)
    ) { uris: List<Uri> ->
        if (uris.isNotEmpty()) {
            handleSelectedPhotos(uris)
        }
    }

    // Legacy permission launcher for Android 12 and below
    private val legacyPhotoPermissionLauncher = activity.registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            openGalleryLegacy()
        }
    }

    /**
     * Pick single photo - uses Photo Picker on Android 13+
     */
    fun pickSinglePhoto() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            // Use Photo Picker (no permission needed)
            singlePhotoPickerLauncher.launch(
                PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly)
            )
        } else {
            // Request permission and use legacy gallery
            requestLegacyPhotoPermission()
        }
    }

    /**
     * Pick multiple photos
     */
    fun pickMultiplePhotos(maxItems: Int = 10) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            multiplePhotosPickerLauncher.launch(
                PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly)
            )
        } else {
            requestLegacyPhotoPermission()
        }
    }

    /**
     * Pick video
     */
    fun pickVideo() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            singlePhotoPickerLauncher.launch(
                PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.VideoOnly)
            )
        } else {
            requestLegacyPhotoPermission()
        }
    }

    /**
     * Pick any media (photos or videos)
     */
    fun pickMedia() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            singlePhotoPickerLauncher.launch(
                PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageAndVideo)
            )
        } else {
            requestLegacyPhotoPermission()
        }
    }

    private fun requestLegacyPhotoPermission() {
        val permission = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            Manifest.permission.READ_MEDIA_IMAGES
        } else {
            Manifest.permission.READ_EXTERNAL_STORAGE
        }

        legacyPhotoPermissionLauncher.launch(permission)
    }

    private fun openGalleryLegacy() {
        val intent = Intent(Intent.ACTION_PICK).apply {
            type = "image/*"
        }
        activity.startActivity(intent)
    }

    private fun handleSelectedPhoto(uri: Uri) {
        // Process selected photo
    }

    private fun handleSelectedPhotos(uris: List<Uri>) {
        // Process selected photos
    }
}
```

#### 2. Granular Media Permissions (Android 13+)

```kotlin
import android.Manifest
import android.os.Build
import androidx.activity.result.contract.ActivityResultContracts

/**
 * Handle granular media permissions
 */
class MediaPermissionsManager(private val activity: AppCompatActivity) {

    /**
     * Get required permissions based on Android version
     */
    fun getMediaPermissions(
        needsImages: Boolean = false,
        needsVideos: Boolean = false,
        needsAudio: Boolean = false
    ): Array<String> {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            // Android 13+: Granular permissions
            buildList {
                if (needsImages) add(Manifest.permission.READ_MEDIA_IMAGES)
                if (needsVideos) add(Manifest.permission.READ_MEDIA_VIDEO)
                if (needsAudio) add(Manifest.permission.READ_MEDIA_AUDIO)
            }.toTypedArray()
        } else {
            // Android 12 and below: Single permission
            arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE)
        }
    }

    /**
     * Request media permissions
     */
    fun requestMediaPermissions(
        needsImages: Boolean = false,
        needsVideos: Boolean = false,
        needsAudio: Boolean = false,
        onResult: (MediaPermissionResult) -> Unit
    ) {
        val permissions = getMediaPermissions(needsImages, needsVideos, needsAudio)

        if (permissions.isEmpty()) {
            onResult(MediaPermissionResult.NotNeeded)
            return
        }

        val launcher = activity.registerForActivityResult(
            ActivityResultContracts.RequestMultiplePermissions()
        ) { results ->
            val result = when {
                results.all { it.value } ->
                    MediaPermissionResult.AllGranted

                results.any { it.value } ->
                    MediaPermissionResult.PartiallyGranted(results)

                else ->
                    MediaPermissionResult.Denied
            }
            onResult(result)
        }

        launcher.launch(permissions)
    }

    sealed class MediaPermissionResult {
        object NotNeeded : MediaPermissionResult()
        object AllGranted : MediaPermissionResult()
        data class PartiallyGranted(val permissions: Map<String, Boolean>) : MediaPermissionResult()
        object Denied : MediaPermissionResult()
    }
}
```

#### 3. Notification Permission (Android 13+)

```kotlin
/**
 * Handle notification permission
 */
class NotificationPermissionManager(
    private val activity: AppCompatActivity,
    private val context: Context
) {

    private val notificationPermissionLauncher = activity.registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        handleNotificationPermissionResult(isGranted)
    }

    /**
     * Check if notification permission is granted
     */
    fun hasNotificationPermission(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.POST_NOTIFICATIONS
            ) == PackageManager.PERMISSION_GRANTED
        } else {
            // No permission needed on Android 12 and below
            areNotificationsEnabled()
        }
    }

    /**
     * Check if notifications are enabled (works on all versions)
     */
    private fun areNotificationsEnabled(): Boolean {
        val notificationManager = NotificationManagerCompat.from(context)
        return notificationManager.areNotificationsEnabled()
    }

    /**
     * Request notification permission with proper UX
     */
    fun requestNotificationPermission(
        showRationale: Boolean = true,
        onResult: (Boolean) -> Unit
    ) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) {
            // No permission needed on Android 12 and below
            onResult(areNotificationsEnabled())
            return
        }

        when {
            hasNotificationPermission() -> {
                onResult(true)
            }

            showRationale && activity.shouldShowRequestPermissionRationale(
                Manifest.permission.POST_NOTIFICATIONS
            ) -> {
                showNotificationRationale {
                    launchNotificationPermissionRequest(onResult)
                }
            }

            else -> {
                launchNotificationPermissionRequest(onResult)
            }
        }
    }

    private fun launchNotificationPermissionRequest(onResult: (Boolean) -> Unit) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            notificationPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
        }
    }

    private fun showNotificationRationale(onContinue: () -> Unit) {
        AlertDialog.Builder(activity)
            .setTitle("Enable Notifications")
            .setMessage("Notifications help you stay updated with important information.")
            .setPositiveButton("Continue") { dialog, _ ->
                dialog.dismiss()
                onContinue()
            }
            .setNegativeButton("Not Now") { dialog, _ ->
                dialog.dismiss()
            }
            .show()
    }

    private fun handleNotificationPermissionResult(isGranted: Boolean) {
        if (!isGranted) {
            // Show explanation or fallback
            showNotificationDeniedMessage()
        }
    }

    private fun showNotificationDeniedMessage() {
        Toast.makeText(
            context,
            "You won't receive notifications. You can enable them later in settings.",
            Toast.LENGTH_LONG
        ).show()
    }

    /**
     * Open notification settings
     */
    fun openNotificationSettings() {
        val intent = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS).apply {
                putExtra(Settings.EXTRA_APP_PACKAGE, context.packageName)
            }
        } else {
            Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
                data = Uri.fromParts("package", context.packageName, null)
            }
        }
        activity.startActivity(intent)
    }
}
```

#### 4. Background Location Permission (Android 10+)

```kotlin
/**
 * Handle background location permission with Android version considerations
 */
class BackgroundLocationManager(private val activity: AppCompatActivity) {

    /**
     * Request background location (must request foreground first)
     */
    fun requestBackgroundLocation(onResult: (BackgroundLocationResult) -> Unit) {
        when {
            Build.VERSION.SDK_INT < Build.VERSION_CODES.Q -> {
                // Background location included in foreground permission on Android 9 and below
                onResult(BackgroundLocationResult.NotNeeded)
            }

            Build.VERSION.SDK_INT >= Build.VERSION_CODES.R -> {
                // Android 11+: Must request separately with specific UI flow
                requestBackgroundLocationAndroid11Plus(onResult)
            }

            else -> {
                // Android 10: Can request with foreground
                requestBackgroundLocationAndroid10(onResult)
            }
        }
    }

    /**
     * Android 11+ flow (more restrictive)
     */
    private fun requestBackgroundLocationAndroid11Plus(
        onResult: (BackgroundLocationResult) -> Unit
    ) {
        // Step 1: Check foreground location
        val hasForegroundLocation = checkForegroundLocationPermission()

        if (!hasForegroundLocation) {
            onResult(BackgroundLocationResult.ForegroundNotGranted)
            return
        }

        // Step 2: Show educational UI (required by Google Play)
        showBackgroundLocationEducation {
            // Step 3: Request background permission
            val launcher = activity.registerForActivityResult(
                ActivityResultContracts.RequestPermission()
            ) { isGranted ->
                onResult(
                    if (isGranted) BackgroundLocationResult.Granted
                    else BackgroundLocationResult.Denied
                )
            }

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                launcher.launch(Manifest.permission.ACCESS_BACKGROUND_LOCATION)
            }
        }
    }

    /**
     * Android 10 flow
     */
    private fun requestBackgroundLocationAndroid10(
        onResult: (BackgroundLocationResult) -> Unit
    ) {
        val permissions = arrayOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_BACKGROUND_LOCATION
        )

        val launcher = activity.registerForActivityResult(
            ActivityResultContracts.RequestMultiplePermissions()
        ) { results ->
            val backgroundGranted = results[Manifest.permission.ACCESS_BACKGROUND_LOCATION] == true
            onResult(
                if (backgroundGranted) BackgroundLocationResult.Granted
                else BackgroundLocationResult.Denied
            )
        }

        launcher.launch(permissions)
    }

    private fun checkForegroundLocationPermission(): Boolean {
        return ContextCompat.checkSelfPermission(
            activity,
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED
    }

    private fun showBackgroundLocationEducation(onContinue: () -> Unit) {
        AlertDialog.Builder(activity)
            .setTitle("Background Location Access")
            .setMessage(
                "This app needs background location to track your activity even when " +
                "the app is closed or not in use.\n\n" +
                "On the next screen, please select 'Allow all the time' for full functionality."
            )
            .setPositiveButton("Continue") { dialog, _ ->
                dialog.dismiss()
                onContinue()
            }
            .setNegativeButton("Cancel") { dialog, _ ->
                dialog.dismiss()
            }
            .setCancelable(false)
            .show()
    }

    sealed class BackgroundLocationResult {
        object NotNeeded : BackgroundLocationResult()
        object Granted : BackgroundLocationResult()
        object Denied : BackgroundLocationResult()
        object ForegroundNotGranted : BackgroundLocationResult()
    }
}
```

### Version-Specific Permission Flow

```kotlin
/**
 * Unified permission manager with version-specific handling
 */
class VersionAwarePermissionManager(
    private val activity: AppCompatActivity,
    private val context: Context
) {

    private val photoPickerManager = PhotoPickerManager(activity)
    private val mediaPermissionsManager = MediaPermissionsManager(activity)
    private val notificationManager = NotificationPermissionManager(activity, context)
    private val locationManager = BackgroundLocationManager(activity)

    /**
     * Request photos access with version-appropriate method
     */
    fun requestPhotosAccess(
        usePhotoPicker: Boolean = true,
        onResult: (PhotoAccessResult) -> Unit
    ) {
        when {
            // Android 14+: Prefer photo picker
            Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE && usePhotoPicker -> {
                photoPickerManager.pickMultiplePhotos()
                onResult(PhotoAccessResult.PhotoPickerUsed)
            }

            // Android 13: Granular permission or photo picker
            Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU -> {
                if (usePhotoPicker) {
                    photoPickerManager.pickMultiplePhotos()
                    onResult(PhotoAccessResult.PhotoPickerUsed)
                } else {
                    mediaPermissionsManager.requestMediaPermissions(
                        needsImages = true
                    ) { result ->
                        onResult(
                            when (result) {
                                MediaPermissionsManager.MediaPermissionResult.AllGranted ->
                                    PhotoAccessResult.FullAccess
                                else ->
                                    PhotoAccessResult.Denied
                            }
                        )
                    }
                }
            }

            // Android 12 and below: Legacy permission
            else -> {
                val launcher = activity.registerForActivityResult(
                    ActivityResultContracts.RequestPermission()
                ) { isGranted ->
                    onResult(
                        if (isGranted) PhotoAccessResult.FullAccess
                        else PhotoAccessResult.Denied
                    )
                }
                launcher.launch(Manifest.permission.READ_EXTERNAL_STORAGE)
            }
        }
    }

    /**
     * Setup notifications with version checks
     */
    fun setupNotifications(onResult: (Boolean) -> Unit) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            notificationManager.requestNotificationPermission { granted ->
                onResult(granted)
            }
        } else {
            // No permission needed, but check if enabled
            onResult(notificationManager.hasNotificationPermission())
        }
    }

    /**
     * Get permission declaration for manifest
     */
    fun getRequiredManifestPermissions(): List<String> {
        return buildList {
            // Notification permission (Android 13+)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                add(Manifest.permission.POST_NOTIFICATIONS)
            }

            // Media permissions (Android 13+)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                add(Manifest.permission.READ_MEDIA_IMAGES)
                add(Manifest.permission.READ_MEDIA_VIDEO)
                add(Manifest.permission.READ_MEDIA_AUDIO)
            } else {
                add(Manifest.permission.READ_EXTERNAL_STORAGE)
            }

            // Location permissions
            add(Manifest.permission.ACCESS_FINE_LOCATION)
            add(Manifest.permission.ACCESS_COARSE_LOCATION)

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                add(Manifest.permission.ACCESS_BACKGROUND_LOCATION)
            }
        }
    }

    sealed class PhotoAccessResult {
        object PhotoPickerUsed : PhotoAccessResult()
        object FullAccess : PhotoAccessResult()
        object PartialAccess : PhotoAccessResult()
        object Denied : PhotoAccessResult()
    }
}
```

### Migration Guide

```kotlin
/**
 * Migration helper from old to new permission APIs
 */
object PermissionMigrationGuide {

    /**
     * Before: READ_EXTERNAL_STORAGE for all media
     * After: Granular permissions or photo picker
     */
    fun migrateMediaAccess() {
        // OLD (Android 12 and below)
        // <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />

        // NEW (Android 13+)
        // <uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
        // <uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />
        // <uses-permission android:name="android.permission.READ_MEDIA_AUDIO" />

        // Or use Photo Picker (no permission needed)
    }

    /**
     * Before: Notifications worked without permission
     * After: POST_NOTIFICATIONS required (Android 13+)
     */
    fun migrateNotifications() {
        // OLD (Android 12 and below)
        // No permission needed

        // NEW (Android 13+)
        // <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

        // Request at appropriate time:
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            // requestPermission(POST_NOTIFICATIONS)
        }
    }

    /**
     * Before: Background location with foreground
     * After: Separate requests (Android 11+)
     */
    fun migrateBackgroundLocation() {
        // OLD (Android 9 and below)
        // Background included with ACCESS_FINE_LOCATION

        // ANDROID 10
        // Can request together, but shown separately

        // ANDROID 11+
        // MUST request separately with education UI
    }
}
```

### AndroidManifest.xml Configuration

```xml
<!-- Complete manifest with version-specific permissions -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- Camera (all versions) -->
    <uses-permission android:name="android.permission.CAMERA" />

    <!-- Location (all versions) -->
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />

    <!-- Background location (Android 10+) -->
    <uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" />

    <!-- Notifications (Android 13+) -->
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <!-- Media - Granular (Android 13+) -->
    <uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
    <uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />
    <uses-permission android:name="android.permission.READ_MEDIA_AUDIO" />

    <!-- Media - Legacy (Android 12 and below) -->
    <uses-permission
        android:name="android.permission.READ_EXTERNAL_STORAGE"
        android:maxSdkVersion="32" />

    <!-- Optional: Photo picker on older versions -->
    <uses-feature
        android:name="android.software.picture_in_picture"
        android:required="false" />

</manifest>
```

### Best Practices

1. **Use Photo Picker When Possible**
   ```kotlin
   // No permission needed on Android 13+
   pickVisualMediaLauncher.launch(PickVisualMediaRequest())
   ```

2. **Request Notification Permission at Right Time**
   ```kotlin
   // After user performs action that benefits from notifications
   fun onUserSubscribesToUpdates() {
       requestNotificationPermission()
   }
   ```

3. **Request Background Location Incrementally**
   ```kotlin
   // First foreground, then background after user sees value
   requestForeground { granted ->
       if (granted && needsBackground) {
           showBackgroundEducation()
           requestBackground()
       }
   }
   ```

4. **Handle Version Differences**
   ```kotlin
   val permissions = if (Build.VERSION.SDK_INT >= 33) {
       arrayOf(READ_MEDIA_IMAGES)
   } else {
       arrayOf(READ_EXTERNAL_STORAGE)
   }
   ```

5. **Test on Multiple Android Versions**
   ```kotlin
   // Test on Android 11, 12, 13, 14
   // Behavior differs significantly
   ```

### Common Pitfalls

1. **Not Using Photo Picker**
   ```kotlin
   // BAD: Request READ_MEDIA_IMAGES on Android 13+
   // GOOD: Use photo picker (no permission)
   ```

2. **Requesting Background Location Too Early**
   ```kotlin
   // BAD: Request on app launch
   // GOOD: After user enables a tracking feature
   ```

3. **Forgetting maxSdkVersion**
   ```xml
   <!-- Prevent legacy permission on new Android -->
   <uses-permission
       android:name="android.permission.READ_EXTERNAL_STORAGE"
       android:maxSdkVersion="32" />
   ```

4. **Not Handling Partial Access**
   ```kotlin
   // User may grant only some media permissions
   if (hasImagesPermission || hasVideosPermission) {
       // Handle partial access
   }
   ```

### Summary

Android 13/14 permission changes:

- **Photo Picker**: Preferred over READ_MEDIA_IMAGES permission
- **Granular Media**: Separate permissions for images, videos, audio
- **Notification Permission**: Required on Android 13+
- **Background Location**: More restrictive on Android 11+
- **Version Checks**: Essential for compatibility

**Migration Strategy**:
1. Use photo picker when possible (no permission)
2. Add granular media permissions with maxSdkVersion on legacy
3. Request POST_NOTIFICATIONS conditionally on Android 13+
4. Implement two-step background location flow on Android 11+
5. Test thoroughly on Android 11, 12, 13, 14

---

## Ответ (RU)
**Android 14** (API 34) и **Android 13** (API 33) представили значительные изменения разрешений, ориентированные на конфиденциальность. Основные: детализированный доступ к фото/видео, обязательное разрешение на уведомления и более строгие требования к фоновой геолокации.

### Ключевые изменения

**Android 14 (API 34):**
- Частичный доступ к фото/видео
- Разрешения Health Connect
- Дополнительные ограничения фоновой геолокации

**Android 13 (API 33):**
- Разрешение на уведомления (POST_NOTIFICATIONS)
- Детализированные медиа-разрешения
- Новое разрешение NEARBY_WIFI_DEVICES

### Реализация

```kotlin
// Photo Picker (Android 13+)
class PhotoPickerManager(private val activity: AppCompatActivity) {

    private val photoPickerLauncher = activity.registerForActivityResult(
        ActivityResultContracts.PickVisualMedia()
    ) { uri: Uri? ->
        uri?.let { handlePhoto(it) }
    }

    fun pickPhoto() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            // Разрешение не требуется
            photoPickerLauncher.launch(
                PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly)
            )
        } else {
            // Запросить разрешение
            requestLegacyPermission()
        }
    }
}

// Уведомления (Android 13+)
class NotificationPermissionManager {

    fun requestNotificationPermission(onResult: (Boolean) -> Unit) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            launcher.launch(Manifest.permission.POST_NOTIFICATIONS)
        } else {
            onResult(true) // Не требуется на старых версиях
        }
    }
}

// Фоновая геолокация (Android 11+)
class BackgroundLocationManager {

    fun requestBackgroundLocation(onResult: (Boolean) -> Unit) {
        when {
            Build.VERSION.SDK_INT >= Build.VERSION_CODES.R -> {
                // Двухэтапный процесс
                showEducationUI()
                requestSeparately()
            }
            Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q -> {
                // Можно запросить вместе
                requestWithForeground()
            }
        }
    }
}
```

### AndroidManifest.xml

```xml
<!-- Уведомления (Android 13+) -->
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

<!-- Медиа - детализированные (Android 13+) -->
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
<uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />

<!-- Медиа - legacy (Android 12 и ниже) -->
<uses-permission
    android:name="android.permission.READ_EXTERNAL_STORAGE"
    android:maxSdkVersion="32" />

<!-- Фоновая геолокация (Android 10+) -->
<uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" />
```

### Best Practices

1. **Используйте Photo Picker (без разрешения)**
2. **Запрашивайте уведомления в нужный момент**
3. **Постепенный запрос фоновой геолокации**
4. **Обрабатывайте различия версий**
5. **Тестируйте на нескольких версиях Android**

### Стратегия миграции

1. Использовать photo picker (без разрешения)
2. Добавить детализированные медиа-разрешения
3. Условный запрос POST_NOTIFICATIONS
4. Двухэтапный процесс для фоновой геолокации
5. Тщательное тестирование

### Резюме

Изменения Android 13/14:

- **Photo Picker**: Предпочтительнее разрешения
- **Детализированные медиа**: Отдельные разрешения
- **Уведомления**: Обязательны на Android 13+
- **Фоновая геолокация**: Более строгие требования
- **Проверки версий**: Критичны для совместимости

---

## Related Questions

### Related (Medium)
- [[q-android-security-practices-checklist--android--medium]] - Security
- [[q-encrypted-file-storage--security--medium]] - Security
- [[q-database-encryption-android--android--medium]] - Security
- [[q-runtime-permissions-best-practices--permissions--medium]] - Security
- [[q-app-security-best-practices--security--medium]] - Security
