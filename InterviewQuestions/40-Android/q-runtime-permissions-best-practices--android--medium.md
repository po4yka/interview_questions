---
id: android-213
title: Runtime Permissions Best Practices / Лучшие практики runtime разрешений
aliases:
- Runtime Permissions Best Practices
- Лучшие практики runtime разрешений
topic: android
subtopics:
- permissions
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-permissions
- q-android-security-practices-checklist--android--medium
- q-database-encryption-android--android--medium
sources: []
created: 2025-10-15
updated: 2025-11-10
tags:
- android
- android/permissions
- difficulty/medium
- permissions
- security
- ux
---

# Вопрос (RU)

> Реализуйте обработку runtime-разрешений с правильным UX: показывайте обоснование запроса, корректно обрабатывайте постоянный отказ и используйте API ActivityResultContracts.

# Question (EN)

> Implement runtime permission handling with proper UX flow. Show rationale before requesting, handle permanent denial gracefully, and use ActivityResultContracts API.

---

## Ответ (RU)

**Runtime-разрешения** были введены в Android 6.0 (API 23) для предоставления пользователям контроля над конфиденциальными данными. Правильная обработка требует продуманного UX-потока с использованием современного API ActivityResultContracts.

### Состояния Разрешений

1. **Не запрошено**: разрешение никогда не запрашивалось
2. **Предоставлено**: пользователь одобрил
3. **Отклонено**: пользователь отказал (можно запросить снова)
4. **Навсегда отклонено**: пользователь отметил "Больше не спрашивать" (или система больше не показывает диалог)

### Реализация с ActivityResultContracts

```kotlin
class PermissionManager(private val activity: AppCompatActivity) {

    // ✅ Современный подход с ActivityResultContracts
    private val permissionLauncher: ActivityResultLauncher<String> =
        activity.registerForActivityResult(
            ActivityResultContracts.RequestPermission()
        ) { isGranted ->
            // Обработайте результат: включите фичу или покажите сообщение/диалог
            handlePermissionResult(isGranted)
        }

    fun requestPermission(permission: String, rationale: String?) {
        when (getPermissionState(permission)) {
            PermissionState.Granted -> {
                proceedWithFeature()
            }

            PermissionState.Denied -> {
                // ✅ Показать обоснование перед повторным запросом
                if (rationale != null) {
                    showRationaleDialog(rationale) {
                        permissionLauncher.launch(permission)
                    }
                } else {
                    permissionLauncher.launch(permission)
                }
            }

            PermissionState.PermanentlyDenied -> {
                // ✅ Направить в настройки (без повторного системного диалога)
                showSettingsDialog()
            }

            PermissionState.NotRequested -> {
                permissionLauncher.launch(permission)
            }
        }
    }

    private fun getPermissionState(permission: String): PermissionState {
        return when {
            ContextCompat.checkSelfPermission(activity, permission) ==
                PackageManager.PERMISSION_GRANTED -> PermissionState.Granted

            activity.shouldShowRequestPermissionRationale(permission) ->
                // Был отказ без "Больше не спрашивать", можно показать rationale
                PermissionState.Denied

            // Для определения "навсегда отклонено" требуется помнить, что мы уже запрашивали
            wasPermissionRequested(permission) &&
                !activity.shouldShowRequestPermissionRationale(permission) ->
                PermissionState.PermanentlyDenied

            else -> PermissionState.NotRequested
        }
    }

    // Реализации handlePermissionResult / proceedWithFeature / showRationaleDialog /
    // showSettingsDialog / wasPermissionRequested опущены для краткости.
}
```

### Множественные Разрешения

```kotlin
// ✅ Запрос группы связанных разрешений
val locationLauncher = registerForActivityResult(
    ActivityResultContracts.RequestMultiplePermissions()
) { permissions ->
    when {
        permissions[Manifest.permission.ACCESS_FINE_LOCATION] == true ->
            LocationResult.FineLocation

        permissions[Manifest.permission.ACCESS_COARSE_LOCATION] == true ->
            LocationResult.CoarseLocation

        else -> LocationResult.Denied
    }
}

// ❌ НЕПРАВИЛЬНО: запрос всех разрешений при запуске приложения
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    requestAllPermissions() // анти-паттерн
}

// ✅ ПРАВИЛЬНО: запрос в момент использования функции
fun startLocationTracking() {
    locationLauncher.launch(
        arrayOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )
    )
}
```

### Jetpack Compose Интеграция

(пример использует библиотеку accompanist-permissions, `rememberPermissionState` и `ExperimentalPermissionsApi` не входят в core Compose)

```kotlin
@OptIn(ExperimentalPermissionsApi::class)
@Composable
fun CameraPermissionScreen() {
    val cameraState = rememberPermissionState(Manifest.permission.CAMERA)

    when {
        cameraState.status.isGranted -> {
            // ✅ Разрешение предоставлено
            CameraPreview()
        }

        cameraState.status.shouldShowRationale -> {
            // ✅ Показать обоснование
            RationaleDialog(
                message = "Камера нужна для сканирования QR-кодов",
                onRequest = { cameraState.launchPermissionRequest() }
            )
        }

        else -> {
            // ✅ Первый запрос или постоянный отказ
            Button(onClick = { cameraState.launchPermissionRequest() }) {
                Text("Разрешить доступ к камере")
            }
        }
    }
}
```

### Best Practices

1. **Запрашивайте в момент использования** — не при запуске приложения.
2. **Объясняйте перед запросом** — покажите, зачем нужно разрешение.
3. **Обрабатывайте постоянный отказ** — направляйте в Settings, не зацикливайте запросы.
4. **Запрашивайте минимум** — только необходимые разрешения и только связанные группы.
5. **Тестируйте все состояния** — granted, denied, permanently denied (включая конфигурации "Don't ask again").

### Типичные Ошибки

**❌ Запрос при старте приложения:**
```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    requestPermissions(arrayOf(CAMERA, LOCATION, CONTACTS))
}
```

**✅ Запрос при использовании:**
```kotlin
fun openCamera() {
    permissionManager.requestPermission(CAMERA, "Для сканирования штрих-кодов")
}
```

**❌ Игнорирование постоянного отказа:**
```kotlin
// Продолжаем вызывать системный диалог, хотя пользователь отключил "спрашивать" (Don't ask again)
```

**✅ Направление в настройки:**
```kotlin
if (isPermanentlyDenied) {
    showSettingsDialog()
}
```

---

## Answer (EN)

**Runtime permissions** were introduced in Android 6.0 (API 23) to give users control over sensitive data. Proper handling requires a well-designed UX flow using the modern ActivityResultContracts API.

### Permission States

1. **Not Requested**: permission never asked.
2. **Granted**: user approved.
3. **Denied**: user rejected (can ask again).
4. **Permanently Denied**: user checked "Don't ask again" (or the system no longer shows the dialog).

### Implementation with ActivityResultContracts

```kotlin
class PermissionManager(private val activity: AppCompatActivity) {

    // ✅ Modern approach with ActivityResultContracts
    private val permissionLauncher: ActivityResultLauncher<String> =
        activity.registerForActivityResult(
            ActivityResultContracts.RequestPermission()
        ) { isGranted ->
            // Handle result: enable feature or show message/dialog
            handlePermissionResult(isGranted)
        }

    fun requestPermission(permission: String, rationale: String?) {
        when (getPermissionState(permission)) {
            PermissionState.Granted -> {
                proceedWithFeature()
            }

            PermissionState.Denied -> {
                // ✅ Show rationale before re-requesting
                if (rationale != null) {
                    showRationaleDialog(rationale) {
                        permissionLauncher.launch(permission)
                    }
                } else {
                    permissionLauncher.launch(permission)
                }
            }

            PermissionState.PermanentlyDenied -> {
                // ✅ Direct to settings (no further system dialog)
                showSettingsDialog()
            }

            PermissionState.NotRequested -> {
                permissionLauncher.launch(permission)
            }
        }
    }

    private fun getPermissionState(permission: String): PermissionState {
        return when {
            ContextCompat.checkSelfPermission(activity, permission) ==
                PackageManager.PERMISSION_GRANTED -> PermissionState.Granted

            activity.shouldShowRequestPermissionRationale(permission) ->
                // Previously denied without "Don't ask again".
                PermissionState.Denied

            // To detect "permanently denied" you must remember that it was requested before.
            wasPermissionRequested(permission) &&
                !activity.shouldShowRequestPermissionRationale(permission) ->
                PermissionState.PermanentlyDenied

            else -> PermissionState.NotRequested
        }
    }

    // Implementations of handlePermissionResult / proceedWithFeature /
    // showRationaleDialog / showSettingsDialog / wasPermissionRequested are omitted for brevity.
}
```

### Multiple Permissions

```kotlin
// ✅ Request group of related permissions
val locationLauncher = registerForActivityResult(
    ActivityResultContracts.RequestMultiplePermissions()
) { permissions ->
    when {
        permissions[Manifest.permission.ACCESS_FINE_LOCATION] == true ->
            LocationResult.FineLocation

        permissions[Manifest.permission.ACCESS_COARSE_LOCATION] == true ->
            LocationResult.CoarseLocation

        else -> LocationResult.Denied
    }
}

// ❌ WRONG: request all permissions on app launch
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    requestAllPermissions() // anti-pattern
}

// ✅ CORRECT: request at point of use
fun startLocationTracking() {
    locationLauncher.launch(
        arrayOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )
    )
}
```

### Jetpack Compose Integration

(This example uses the accompanist-permissions library; `rememberPermissionState` and `ExperimentalPermissionsApi` are not part of core Compose.)

```kotlin
@OptIn(ExperimentalPermissionsApi::class)
@Composable
fun CameraPermissionScreen() {
    val cameraState = rememberPermissionState(Manifest.permission.CAMERA)

    when {
        cameraState.status.isGranted -> {
            // ✅ Permission granted
            CameraPreview()
        }

        cameraState.status.shouldShowRationale -> {
            // ✅ Show rationale
            RationaleDialog(
                message = "Camera is needed to scan QR codes",
                onRequest = { cameraState.launchPermissionRequest() }
            )
        }

        else -> {
            // ✅ First request or permanently denied
            Button(onClick = { cameraState.launchPermissionRequest() }) {
                Text("Allow Camera Access")
            }
        }
    }
}
```

### Best Practices

1. **Request at point of use** — not on app launch.
2. **Explain before requesting** — make it clear why the permission is needed.
3. **Handle permanent denial** — direct users to Settings instead of looping requests.
4. **Request minimum** — only necessary and logically related permissions.
5. **Test all states** — granted, denied, permanently denied (including "Don't ask again").

### Common Mistakes

**❌ Requesting on app start:**
```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    requestPermissions(arrayOf(CAMERA, LOCATION, CONTACTS))
}
```

**✅ Requesting when needed:**
```kotlin
fun openCamera() {
    permissionManager.requestPermission(CAMERA, "To scan barcodes")
}
```

**❌ Ignoring permanent denial:**
```kotlin
// Keep trying to show system dialog even when user selected "Don't ask again"
```

**✅ Directing to settings:**
```kotlin
if (isPermanentlyDenied) {
    showSettingsDialog()
}
```

---

## Дополнительные вопросы (RU)

- Как по-разному обрабатывать фоновые разрешения на локацию по сравнению с foreground?
- Как строить стратегию запроса разрешения на уведомления в Android 13+?
- Как изящно деградировать функциональность при отказе в разрешениях?
- Какие метрики и события аналитики отслеживать для конверсии по разрешениям?
- Как тестировать permission-флоу в инструментальных тестах?

## Follow-ups

- How to handle background location permissions separately from foreground?
- What's the strategy for requesting notification permissions on Android 13+?
- How to gracefully degrade functionality when permissions are denied?
- What analytics should be tracked for permission conversion rates?
- How to test permission flows in instrumented tests?

## Ссылки (RU)

- https://developer.android.com/training/permissions/requesting
- https://developer.android.com/guide/topics/permissions/overview
- https://developer.android.com/reference/androidx/activity/result/contract/ActivityResultContracts

## References

- https://developer.android.com/training/permissions/requesting
- https://developer.android.com/guide/topics/permissions/overview
- https://developer.android.com/reference/androidx/activity/result/contract/ActivityResultContracts

## Связанные вопросы (RU)

### Предпосылки / Концепции

- [[c-permissions]]

### Предпосылки (проще)

- Понимание модели разрешений Android и объявлений в манифесте
- Базовые знания системы runtime-разрешений Android

### Связанные (тот же уровень)

- [[q-database-encryption-android--android--medium]] - Практики безопасности
- [[q-android-security-practices-checklist--android--medium]] - Чек-лист по безопасности
- Паттерны использования ActivityResult API
- Лучшие практики согласия пользователя и приватности

### Продвинутое (сложнее)

- [[q-clean-architecture-android--android--hard]] - Архитектурные паттерны
- Реализация оберток над разрешениями в мультимодульной архитектуре
- Продвинутые паттерны безопасности при доступе к чувствительным данным

## Related Questions

### Prerequisites / Concepts

- [[c-permissions]]

### Prerequisites (Easier)

- Understanding Android permission model and manifest declarations
- Basics of Android runtime permission system

### Related (Same Level)

- [[q-database-encryption-android--android--medium]] - Security practices
- [[q-android-security-practices-checklist--android--medium]] - Security checklist
- ActivityResult API usage patterns
- User consent and privacy best practices

### Advanced (Harder)

- [[q-clean-architecture-android--android--hard]] - Architecture patterns
- Implementing permission wrappers in multi-module architecture
- Advanced security patterns for sensitive data access
