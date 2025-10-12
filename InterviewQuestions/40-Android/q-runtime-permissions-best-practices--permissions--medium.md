---
topic: permissions
tags:
  - permissions
  - runtime
  - privacy
  - ux
  - best-practices
  - activity-result
  - difficulty/medium
difficulty: medium
status: draft
---

# Runtime Permission Best Practices / Best Practices разрешений

**English**: Implement runtime permission handling with proper UX flow. Show rationale before requesting, handle permanent denial gracefully, and use ActivityResultContracts API.

## Answer (EN)
**Runtime permissions** were introduced in Android 6.0 (API 23) to give users more control over sensitive data and operations. Proper permission handling requires a well-designed UX flow that respects user decisions while explaining why permissions are needed.

### Key Concepts

#### Permission Flow States

1. **Not Requested**: Permission never asked
2. **Granted**: User approved permission
3. **Denied**: User rejected permission (can ask again)
4. **Permanently Denied**: User rejected and checked "Don't ask again"

#### Best Practices Overview

```kotlin
// Modern approach using ActivityResultContracts
val requestPermission = registerForActivityResult(
    ActivityResultContracts.RequestPermission()
) { isGranted ->
    if (isGranted) {
        // Permission granted
    } else {
        // Permission denied
    }
}
```

### Complete Permission Handling Implementation

#### 1. Permission Manager with ActivityResultContracts

```kotlin
import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.provider.Settings
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat

/**
 * Comprehensive permission manager using modern APIs
 */
class PermissionManager(private val activity: AppCompatActivity) {

    // Single permission launcher
    private var singlePermissionLauncher: ActivityResultLauncher<String>? = null
    private var singlePermissionCallback: ((Boolean) -> Unit)? = null

    // Multiple permissions launcher
    private var multiplePermissionsLauncher: ActivityResultLauncher<Array<String>>? = null
    private var multiplePermissionsCallback: ((Map<String, Boolean>) -> Unit)? = null

    init {
        // Register single permission launcher
        singlePermissionLauncher = activity.registerForActivityResult(
            ActivityResultContracts.RequestPermission()
        ) { isGranted ->
            singlePermissionCallback?.invoke(isGranted)
            singlePermissionCallback = null
        }

        // Register multiple permissions launcher
        multiplePermissionsLauncher = activity.registerForActivityResult(
            ActivityResultContracts.RequestMultiplePermissions()
        ) { permissions ->
            multiplePermissionsCallback?.invoke(permissions)
            multiplePermissionsCallback = null
        }
    }

    /**
     * Check if permission is granted
     */
    fun isPermissionGranted(permission: String): Boolean {
        return ContextCompat.checkSelfPermission(
            activity,
            permission
        ) == PackageManager.PERMISSION_GRANTED
    }

    /**
     * Check if should show rationale
     */
    fun shouldShowRationale(permission: String): Boolean {
        return activity.shouldShowRequestPermissionRationale(permission)
    }

    /**
     * Determine permission state
     */
    fun getPermissionState(permission: String): PermissionState {
        return when {
            isPermissionGranted(permission) -> PermissionState.Granted

            shouldShowRationale(permission) -> PermissionState.Denied

            // Never requested or permanently denied
            // Check shared preferences to distinguish
            wasPermissionRequested(permission) -> PermissionState.PermanentlyDenied

            else -> PermissionState.NotRequested
        }
    }

    /**
     * Request single permission with rationale
     */
    fun requestPermission(
        permission: String,
        rationale: String? = null,
        onResult: (Boolean) -> Unit
    ) {
        when (getPermissionState(permission)) {
            PermissionState.Granted -> {
                onResult(true)
            }

            PermissionState.NotRequested,
            PermissionState.Denied -> {
                // Show rationale if needed
                if (rationale != null && shouldShowRationale(permission)) {
                    showRationaleDialog(
                        message = rationale,
                        onPositive = {
                            launchPermissionRequest(permission, onResult)
                        },
                        onNegative = {
                            onResult(false)
                        }
                    )
                } else {
                    launchPermissionRequest(permission, onResult)
                }
            }

            PermissionState.PermanentlyDenied -> {
                showPermanentlyDeniedDialog(permission)
                onResult(false)
            }
        }
    }

    /**
     * Request multiple permissions
     */
    fun requestPermissions(
        permissions: Array<String>,
        rationale: String? = null,
        onResult: (Map<String, Boolean>) -> Unit
    ) {
        val deniedPermissions = permissions.filter { !isPermissionGranted(it) }

        if (deniedPermissions.isEmpty()) {
            onResult(permissions.associateWith { true })
            return
        }

        val shouldShowRationale = deniedPermissions.any { shouldShowRationale(it) }

        if (rationale != null && shouldShowRationale) {
            showRationaleDialog(
                message = rationale,
                onPositive = {
                    launchMultiplePermissionsRequest(permissions, onResult)
                },
                onNegative = {
                    onResult(permissions.associateWith { isPermissionGranted(it) })
                }
            )
        } else {
            launchMultiplePermissionsRequest(permissions, onResult)
        }
    }

    private fun launchPermissionRequest(permission: String, callback: (Boolean) -> Unit) {
        markPermissionAsRequested(permission)
        singlePermissionCallback = callback
        singlePermissionLauncher?.launch(permission)
    }

    private fun launchMultiplePermissionsRequest(
        permissions: Array<String>,
        callback: (Map<String, Boolean>) -> Unit
    ) {
        permissions.forEach { markPermissionAsRequested(it) }
        multiplePermissionsCallback = callback
        multiplePermissionsLauncher?.launch(permissions)
    }

    private fun showRationaleDialog(
        message: String,
        onPositive: () -> Unit,
        onNegative: () -> Unit
    ) {
        androidx.appcompat.app.AlertDialog.Builder(activity)
            .setTitle("Permission Required")
            .setMessage(message)
            .setPositiveButton("Continue") { dialog, _ ->
                dialog.dismiss()
                onPositive()
            }
            .setNegativeButton("Cancel") { dialog, _ ->
                dialog.dismiss()
                onNegative()
            }
            .setCancelable(false)
            .show()
    }

    private fun showPermanentlyDeniedDialog(permission: String) {
        val permissionName = getPermissionName(permission)

        androidx.appcompat.app.AlertDialog.Builder(activity)
            .setTitle("Permission Permanently Denied")
            .setMessage(
                "$permissionName permission was permanently denied. " +
                "Please enable it in app settings to use this feature."
            )
            .setPositiveButton("Open Settings") { dialog, _ ->
                dialog.dismiss()
                openAppSettings()
            }
            .setNegativeButton("Cancel") { dialog, _ ->
                dialog.dismiss()
            }
            .show()
    }

    /**
     * Open app settings
     */
    fun openAppSettings() {
        val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
            data = Uri.fromParts("package", activity.packageName, null)
        }
        activity.startActivity(intent)
    }

    private fun wasPermissionRequested(permission: String): Boolean {
        val prefs = activity.getSharedPreferences("permissions", Context.MODE_PRIVATE)
        return prefs.getBoolean("requested_$permission", false)
    }

    private fun markPermissionAsRequested(permission: String) {
        val prefs = activity.getSharedPreferences("permissions", Context.MODE_PRIVATE)
        prefs.edit().putBoolean("requested_$permission", true).apply()
    }

    private fun getPermissionName(permission: String): String {
        return when (permission) {
            Manifest.permission.CAMERA -> "Camera"
            Manifest.permission.ACCESS_FINE_LOCATION -> "Location"
            Manifest.permission.RECORD_AUDIO -> "Microphone"
            Manifest.permission.READ_CONTACTS -> "Contacts"
            Manifest.permission.READ_CALENDAR -> "Calendar"
            Manifest.permission.POST_NOTIFICATIONS -> "Notifications"
            else -> permission.substringAfterLast(".")
        }
    }

    sealed class PermissionState {
        object NotRequested : PermissionState()
        object Granted : PermissionState()
        object Denied : PermissionState()
        object PermanentlyDenied : PermissionState()
    }
}
```

#### 2. Permission Groups Handling

```kotlin
/**
 * Handle related permissions as groups
 */
class PermissionGroupManager(private val permissionManager: PermissionManager) {

    companion object {
        // Location permissions
        val LOCATION_PERMISSIONS = arrayOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )

        // Camera and storage for photos
        val CAMERA_PERMISSIONS = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            arrayOf(
                Manifest.permission.CAMERA,
                Manifest.permission.READ_MEDIA_IMAGES
            )
        } else {
            arrayOf(
                Manifest.permission.CAMERA,
                Manifest.permission.READ_EXTERNAL_STORAGE
            )
        }

        // Contacts
        val CONTACTS_PERMISSIONS = arrayOf(
            Manifest.permission.READ_CONTACTS,
            Manifest.permission.WRITE_CONTACTS
        )
    }

    /**
     * Request location permissions with fine/coarse fallback
     */
    fun requestLocationPermission(
        requireFineLocation: Boolean = true,
        onResult: (LocationPermissionResult) -> Unit
    ) {
        val permissions = if (requireFineLocation) {
            LOCATION_PERMISSIONS
        } else {
            arrayOf(Manifest.permission.ACCESS_COARSE_LOCATION)
        }

        permissionManager.requestPermissions(
            permissions = permissions,
            rationale = "Location access is needed to show nearby places and provide accurate navigation."
        ) { results ->
            val result = when {
                results[Manifest.permission.ACCESS_FINE_LOCATION] == true ->
                    LocationPermissionResult.FineLocation

                results[Manifest.permission.ACCESS_COARSE_LOCATION] == true ->
                    LocationPermissionResult.CoarseLocation

                else ->
                    LocationPermissionResult.Denied
            }
            onResult(result)
        }
    }

    /**
     * Request background location (Android 10+)
     */
    fun requestBackgroundLocation(
        onResult: (Boolean) -> Unit
    ) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q) {
            onResult(true) // Not needed on older versions
            return
        }

        // Must request foreground location first
        requestLocationPermission { foregroundResult ->
            if (foregroundResult != LocationPermissionResult.Denied) {
                // Show explanation for background location
                permissionManager.requestPermission(
                    permission = Manifest.permission.ACCESS_BACKGROUND_LOCATION,
                    rationale = "Background location is needed to track your activity even when the app is closed."
                ) { isGranted ->
                    onResult(isGranted)
                }
            } else {
                onResult(false)
            }
        }
    }

    sealed class LocationPermissionResult {
        object FineLocation : LocationPermissionResult()
        object CoarseLocation : LocationPermissionResult()
        object Denied : LocationPermissionResult()
    }
}
```

#### 3. ViewModel-Based Permission State Management

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * ViewModel for managing permission state
 */
class PermissionViewModel : ViewModel() {

    private val _cameraPermissionState = MutableStateFlow<PermissionUiState>(
        PermissionUiState.NotRequested
    )
    val cameraPermissionState: StateFlow<PermissionUiState> = _cameraPermissionState.asStateFlow()

    private val _locationPermissionState = MutableStateFlow<PermissionUiState>(
        PermissionUiState.NotRequested
    )
    val locationPermissionState: StateFlow<PermissionUiState> = _locationPermissionState.asStateFlow()

    /**
     * Update camera permission state
     */
    fun onCameraPermissionResult(isGranted: Boolean) {
        viewModelScope.launch {
            _cameraPermissionState.value = if (isGranted) {
                PermissionUiState.Granted
            } else {
                PermissionUiState.Denied
            }
        }
    }

    /**
     * Update location permission state
     */
    fun onLocationPermissionResult(result: PermissionGroupManager.LocationPermissionResult) {
        viewModelScope.launch {
            _locationPermissionState.value = when (result) {
                PermissionGroupManager.LocationPermissionResult.FineLocation ->
                    PermissionUiState.Granted

                PermissionGroupManager.LocationPermissionResult.CoarseLocation ->
                    PermissionUiState.GrantedWithLimitations("Only approximate location")

                PermissionGroupManager.LocationPermissionResult.Denied ->
                    PermissionUiState.Denied
            }
        }
    }

    /**
     * Reset permission states
     */
    fun resetPermissions() {
        _cameraPermissionState.value = PermissionUiState.NotRequested
        _locationPermissionState.value = PermissionUiState.NotRequested
    }

    sealed class PermissionUiState {
        object NotRequested : PermissionUiState()
        object Granted : PermissionUiState()
        data class GrantedWithLimitations(val message: String) : PermissionUiState()
        object Denied : PermissionUiState()
        object PermanentlyDenied : PermissionUiState()
    }
}
```

#### 4. Jetpack Compose Integration

```kotlin
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.google.accompanist.permissions.*

/**
 * Compose UI for permission handling
 */
@OptIn(ExperimentalPermissionsApi::class)
@Composable
fun CameraPermissionScreen() {
    val cameraPermissionState = rememberPermissionState(
        permission = Manifest.permission.CAMERA
    )

    PermissionUI(
        permissionState = cameraPermissionState,
        permissionName = "Camera",
        rationaleMessage = "Camera access is needed to take photos for your profile.",
        onPermissionGranted = {
            // Navigate to camera screen
        }
    )
}

@OptIn(ExperimentalPermissionsApi::class)
@Composable
fun PermissionUI(
    permissionState: PermissionState,
    permissionName: String,
    rationaleMessage: String,
    onPermissionGranted: () -> Unit
) {
    when {
        permissionState.status.isGranted -> {
            PermissionGrantedContent(
                permissionName = permissionName,
                onAction = onPermissionGranted
            )
        }

        permissionState.status.shouldShowRationale -> {
            PermissionRationaleContent(
                permissionName = permissionName,
                message = rationaleMessage,
                onRequestPermission = { permissionState.launchPermissionRequest() }
            )
        }

        else -> {
            PermissionRequestContent(
                permissionName = permissionName,
                onRequestPermission = { permissionState.launchPermissionRequest() }
            )
        }
    }
}

@Composable
fun PermissionGrantedContent(
    permissionName: String,
    onAction: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "$permissionName permission granted",
            style = MaterialTheme.typography.titleLarge
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(onClick = onAction) {
            Text("Continue")
        }
    }
}

@Composable
fun PermissionRationaleContent(
    permissionName: String,
    message: String,
    onRequestPermission: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Permission Required",
            style = MaterialTheme.typography.titleLarge
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = message,
            style = MaterialTheme.typography.bodyMedium
        )

        Spacer(modifier = Modifier.height(24.dp))

        Button(onClick = onRequestPermission) {
            Text("Grant $permissionName Permission")
        }
    }
}

@Composable
fun PermissionRequestContent(
    permissionName: String,
    onRequestPermission: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "$permissionName access needed",
            style = MaterialTheme.typography.titleLarge
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(onClick = onRequestPermission) {
            Text("Request Permission")
        }
    }
}

/**
 * Multiple permissions in Compose
 */
@OptIn(ExperimentalPermissionsApi::class)
@Composable
fun LocationPermissionScreen() {
    val locationPermissionsState = rememberMultiplePermissionsState(
        permissions = listOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )
    )

    MultiplePermissionsUI(
        permissionsState = locationPermissionsState,
        permissionsName = "Location",
        onAllPermissionsGranted = {
            // Navigate to map screen
        }
    )
}

@OptIn(ExperimentalPermissionsApi::class)
@Composable
fun MultiplePermissionsUI(
    permissionsState: MultiplePermissionsState,
    permissionsName: String,
    onAllPermissionsGranted: () -> Unit
) {
    when {
        permissionsState.allPermissionsGranted -> {
            PermissionGrantedContent(
                permissionName = permissionsName,
                onAction = onAllPermissionsGranted
            )
        }

        permissionsState.shouldShowRationale -> {
            PermissionRationaleContent(
                permissionName = permissionsName,
                message = "$permissionsName permissions are needed for this feature.",
                onRequestPermission = { permissionsState.launchMultiplePermissionRequest() }
            )
        }

        else -> {
            PermissionRequestContent(
                permissionName = permissionsName,
                onRequestPermission = { permissionsState.launchMultiplePermissionRequest() }
            )
        }
    }
}
```

### Testing Permission Flows

```kotlin
import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.rule.GrantPermissionRule
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Test permission handling flows
 */
@RunWith(AndroidJUnit4::class)
class PermissionFlowTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @get:Rule
    val cameraPermissionRule = GrantPermissionRule.grant(Manifest.permission.CAMERA)

    @Test
    fun whenCameraPermissionGranted_shouldShowCamera() {
        // Given permission is granted (by rule)

        // When opening camera screen
        onView(withId(R.id.openCameraButton)).perform(click())

        // Then camera preview should be visible
        onView(withId(R.id.cameraPreview))
            .check(matches(isDisplayed()))
    }

    @Test
    fun whenLocationPermissionDenied_shouldShowRationale() {
        // Given permission is denied

        // When requesting location
        onView(withId(R.id.requestLocationButton)).perform(click())

        // Then rationale should be shown
        onView(withText("Location access is needed"))
            .check(matches(isDisplayed()))
    }

    @Test
    fun whenPermissionPermanentlyDenied_shouldShowSettingsDialog() {
        // Simulate permanent denial by denying multiple times
        // Then verify settings dialog is shown
        onView(withText("Open Settings"))
            .check(matches(isDisplayed()))
    }
}
```

### Best Practices

1. **Request Permissions at Point of Use**
   ```kotlin
   // BAD: Request all permissions on app launch
   // GOOD: Request when user tries to use feature
   button.setOnClickListener {
       permissionManager.requestPermission(CAMERA) { granted ->
           if (granted) openCamera()
       }
   }
   ```

2. **Always Show Rationale**
   ```kotlin
   permissionManager.requestPermission(
       permission = CAMERA,
       rationale = "Camera access is needed to scan QR codes"
   ) { granted -> }
   ```

3. **Handle Permanent Denial Gracefully**
   ```kotlin
   when (state) {
       PermanentlyDenied -> showSettingsDialog()
       Denied -> showRationale()
       Granted -> proceed()
   }
   ```

4. **Use Minimal Permissions**
   ```kotlin
   // Request COARSE_LOCATION if fine is not needed
   if (needsApproximateLocation) {
       requestPermission(ACCESS_COARSE_LOCATION)
   }
   ```

5. **Request Incrementally**
   ```kotlin
   // Request foreground first, then background
   requestForegroundLocation { granted ->
       if (granted && needsBackground) {
           requestBackgroundLocation()
       }
   }
   ```

6. **Explain Before Requesting**
   ```kotlin
   // Show UI explaining why, then request
   showExplanationUI {
       onContinue = { requestPermission() }
   }
   ```

7. **Don't Block App Usage**
   ```kotlin
   // Allow app usage with degraded functionality
   if (!hasLocationPermission) {
       showManualLocationInput()
   }
   ```

8. **Test All Permission States**
   ```kotlin
   // Test: not requested, granted, denied, permanently denied
   ```

9. **Use System UI When Possible**
   ```kotlin
   // Photo picker instead of READ_MEDIA_IMAGES on Android 13+
   ```

10. **Track Permission Analytics**
    ```kotlin
    analytics.logEvent("permission_requested", permission)
    analytics.logEvent("permission_granted", permission)
    ```

### Common Pitfalls

1. **Requesting Too Early**
   ```kotlin
   // BAD: On app launch
   override fun onCreate() {
       requestAllPermissions()
   }

   // GOOD: When feature is used
   fun openCamera() {
       requestCameraPermission()
   }
   ```

2. **Not Handling Permanent Denial**
   ```kotlin
   // BAD: Keep asking
   // GOOD: Direct to settings
   if (isPermanentlyDenied) {
       openAppSettings()
   }
   ```

3. **Poor Rationale Messaging**
   ```kotlin
   // BAD: "App needs camera"
   // GOOD: "Camera is needed to scan barcodes for product lookup"
   ```

4. **Forgetting Android Version Checks**
   ```kotlin
   if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
       requestRuntimePermission()
   }
   ```

### Summary

Runtime permission best practices:

- **Request at point of use**: Not on app launch
- **Show clear rationale**: Explain why permission is needed
- **Handle denial gracefully**: Provide alternative flows
- **Permanent denial**: Direct users to settings
- **Use ActivityResultContracts**: Modern, lifecycle-aware API
- **Test all states**: Not requested, granted, denied, permanent
- **Respect user choice**: Don't nag users
- **Request minimal permissions**: Only what's truly needed

**UX Guidelines**:
- Explain before requesting
- Make denial non-blocking when possible
- One permission at a time for clarity
- Use system UI when available (photo picker)
- Analytics to understand permission conversion rates

---

## Ответ (RU)
**Runtime разрешения** были введены в Android 6.0 (API 23) для предоставления пользователям большего контроля над конфиденциальными данными. Правильная обработка разрешений требует продуманного UX-потока.

### Основные концепции

**Состояния разрешений:**
- Не запрошено
- Предоставлено
- Отклонено (можно запросить снова)
- Навсегда отклонено (пользователь отметил "Больше не спрашивать")

### Полная реализация

```kotlin
class PermissionManager(private val activity: AppCompatActivity) {

    private var singlePermissionLauncher: ActivityResultLauncher<String>? = null

    init {
        singlePermissionLauncher = activity.registerForActivityResult(
            ActivityResultContracts.RequestPermission()
        ) { isGranted ->
            // Обработка результата
        }
    }

    fun requestPermission(
        permission: String,
        rationale: String? = null,
        onResult: (Boolean) -> Unit
    ) {
        when (getPermissionState(permission)) {
            PermissionState.Granted -> onResult(true)

            PermissionState.Denied -> {
                if (rationale != null) {
                    showRationaleDialog(rationale) {
                        launchPermissionRequest(permission, onResult)
                    }
                } else {
                    launchPermissionRequest(permission, onResult)
                }
            }

            PermissionState.PermanentlyDenied -> {
                showPermanentlyDeniedDialog(permission)
            }
        }
    }
}
```

### Группы разрешений

```kotlin
class PermissionGroupManager {

    fun requestLocationPermission(
        requireFineLocation: Boolean = true,
        onResult: (LocationPermissionResult) -> Unit
    ) {
        val permissions = if (requireFineLocation) {
            arrayOf(ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION)
        } else {
            arrayOf(ACCESS_COARSE_LOCATION)
        }

        permissionManager.requestPermissions(permissions) { results ->
            // Обработка результатов
        }
    }
}
```

### Compose интеграция

```kotlin
@OptIn(ExperimentalPermissionsApi::class)
@Composable
fun CameraPermissionScreen() {
    val cameraPermissionState = rememberPermissionState(
        permission = Manifest.permission.CAMERA
    )

    when {
        cameraPermissionState.status.isGranted -> {
            // Разрешение предоставлено
        }

        cameraPermissionState.status.shouldShowRationale -> {
            // Показать обоснование
            PermissionRationaleContent(
                onRequestPermission = {
                    cameraPermissionState.launchPermissionRequest()
                }
            )
        }

        else -> {
            // Запросить разрешение
            PermissionRequestContent(
                onRequestPermission = {
                    cameraPermissionState.launchPermissionRequest()
                }
            )
        }
    }
}
```

### Best Practices

1. **Запрашивайте в момент использования**
2. **Всегда показывайте обоснование**
3. **Обрабатывайте постоянный отказ**
4. **Используйте минимальные разрешения**
5. **Запрашивайте постепенно**
6. **Объясняйте перед запросом**
7. **Не блокируйте приложение**
8. **Тестируйте все состояния**
9. **Используйте системный UI**
10. **Отслеживайте аналитику**

### Типичные ошибки

1. Запрос слишком рано (при запуске приложения)
2. Отсутствие обработки постоянного отказа
3. Плохие сообщения обоснования
4. Забывание проверки версии Android

### Резюме

Runtime разрешения требуют:

- **Запрос в момент использования**: Не при запуске приложения
- **Четкое обоснование**: Объяснение необходимости
- **Graceful обработка отказа**: Альтернативные потоки
- **ActivityResultContracts**: Современный API
- **Тестирование всех состояний**
- **Уважение выбора пользователя**

**UX рекомендации**:
- Объяснение перед запросом
- Не блокирование при отказе
- Одно разрешение за раз
- Использование системного UI
- Аналитика конверсии разрешений
