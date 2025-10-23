---
id: 20251012-122776
title: Android 14 Permissions / Разрешения Android 14
aliases:
- Android 14 Permissions
- Разрешения Android 14
topic: android
subtopics:
- permissions
- privacy
- security
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-android-security-best-practices--android--medium
- q-android-security-practices-checklist--android--medium
- q-android-manifest-file--android--easy
created: 2025-10-15
updated: 2025-10-15
tags:
- android/permissions
- android/privacy
- android/security
- android14
- android13
- privacy
- photos
- notifications
- compatibility
- difficulty/medium
---# Вопрос (RU)
> Какие ключевые изменения разрешений в Android 14 и как их реализовать?

---

# Question (EN)
> What are the key permission changes in Android 14 and how do you implement them?

## Ответ (RU)

**Изменения разрешений Android 14** вводят обновления, ориентированные на приватность, требующие тщательной реализации и обратной совместимости.

**Теория изменений разрешений:**
Android 14 (API 34) и Android 13 (API 33) ввели детализированный доступ к медиа, обязательные разрешения на уведомления и более строгие требования к фоновой геолокации. Эти изменения приоритизируют приватность пользователя при сохранении функциональности приложения.

**1. Photo Picker (Android 13+):**
Современный подход для выбора медиа без требования разрешений на хранилище.

```kotlin
// Реализация Photo Picker
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
            requestLegacyPermission()
        }
    }
}
```

**2. Детализированные разрешения медиа (Android 13+):**
Отдельные разрешения для изображений, видео и аудио вместо единого разрешения на хранилище.

```kotlin
// Детализированные разрешения медиа
fun getMediaPermissions(needsImages: Boolean, needsVideos: Boolean): Array<String> {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        buildList {
            if (needsImages) add(Manifest.permission.READ_MEDIA_IMAGES)
            if (needsVideos) add(Manifest.permission.READ_MEDIA_VIDEO)
        }.toTypedArray()
    } else {
        arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE)
    }
}
```

**3. Разрешение на уведомления (Android 13+):**
Обязательное разрешение POST_NOTIFICATIONS для отправки уведомлений.

```kotlin
// Разрешение на уведомления
class NotificationPermissionManager {
    fun requestNotificationPermission(onResult: (Boolean) -> Unit) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            launcher.launch(Manifest.permission.POST_NOTIFICATIONS)
        } else {
            onResult(true) // Не требуется на старых версиях
        }
    }
}
```

**4. Фоновая геолокация (Android 11+):**
Двухэтапный процесс, требующий сначала разрешение на передний план, затем фоновое разрешение.

```kotlin
// Фоновая геолокация
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

**5. Конфигурация AndroidManifest.xml:**

```xml
<!-- Уведомления (Android 13+) -->
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

<!-- Детализированные медиа (Android 13+) -->
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
<uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />

<!-- Legacy медиа (Android 12 и ниже) -->
<uses-permission
    android:name="android.permission.READ_EXTERNAL_STORAGE"
    android:maxSdkVersion="32" />

<!-- Фоновая геолокация (Android 10+) -->
<uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" />
```

**Ключевые изменения по версиям:**
- **Android 14**: Частичный доступ к фото/видео, разрешения Health Connect
- **Android 13**: Разрешение на уведомления, детализированные разрешения медиа
- **Android 12**: Приблизительная геолокация, разрешения Bluetooth

**Лучшие практики:**
- Используйте Photo Picker вместо разрешений на хранилище
- Запрашивайте уведомления в подходящие моменты
- Реализуйте двухэтапный процесс фоновой геолокации
- Обрабатывайте различия версий корректно
- Тестируйте на нескольких версиях Android

---

## Answer (EN)

**Android 14 Permission Changes** introduce privacy-focused updates requiring careful implementation and backward compatibility handling.

**Permission Changes Theory:**
Android 14 (API 34) and Android 13 (API 33) introduced granular media access, mandatory notification permissions, and stricter background location requirements. These changes prioritize user privacy while maintaining app functionality.

**1. Photo Picker (Android 13+):**
Modern approach for media selection without requiring storage permissions.

```kotlin
// Photo Picker Implementation
class PhotoPickerManager(private val activity: AppCompatActivity) {
    private val photoPickerLauncher = activity.registerForActivityResult(
        ActivityResultContracts.PickVisualMedia()
    ) { uri: Uri? ->
        uri?.let { handlePhoto(it) }
    }

    fun pickPhoto() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            // No permission required
            photoPickerLauncher.launch(
                PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly)
            )
        } else {
            requestLegacyPermission()
        }
    }
}
```

**2. Granular Media Permissions (Android 13+):**
Separate permissions for images, videos, and audio instead of single storage permission.

```kotlin
// Granular Media Permissions
fun getMediaPermissions(needsImages: Boolean, needsVideos: Boolean): Array<String> {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        buildList {
            if (needsImages) add(Manifest.permission.READ_MEDIA_IMAGES)
            if (needsVideos) add(Manifest.permission.READ_MEDIA_VIDEO)
        }.toTypedArray()
    } else {
        arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE)
    }
}
```

**3. Notification Permission (Android 13+):**
Mandatory POST_NOTIFICATIONS permission for sending notifications.

```kotlin
// Notification Permission
class NotificationPermissionManager {
    fun requestNotificationPermission(onResult: (Boolean) -> Unit) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            launcher.launch(Manifest.permission.POST_NOTIFICATIONS)
        } else {
            onResult(true) // Not required on older versions
        }
    }
}
```

**4. Background Location (Android 11+):**
Two-step process requiring foreground location first, then background permission.

```kotlin
// Background Location
class BackgroundLocationManager {
    fun requestBackgroundLocation(onResult: (Boolean) -> Unit) {
        when {
            Build.VERSION.SDK_INT >= Build.VERSION_CODES.R -> {
                // Two-step process
                showEducationUI()
                requestSeparately()
            }
            Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q -> {
                // Can request together
                requestWithForeground()
            }
        }
    }
}
```

**5. AndroidManifest.xml Configuration:**

```xml
<!-- Notifications (Android 13+) -->
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

<!-- Granular Media (Android 13+) -->
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
<uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />

<!-- Legacy Media (Android 12 and below) -->
<uses-permission
    android:name="android.permission.READ_EXTERNAL_STORAGE"
    android:maxSdkVersion="32" />

<!-- Background Location (Android 10+) -->
<uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" />
```

**Key Changes by Version:**
- **Android 14**: Partial photo/video access, health connect permissions
- **Android 13**: Notification permission, granular media permissions
- **Android 12**: Approximate location, Bluetooth permissions

**Best Practices:**
- Use Photo Picker instead of storage permissions
- Request notifications at appropriate moments
- Implement two-step background location process
- Handle version differences gracefully
- Test on multiple Android versions

## Follow-ups

- How do you handle permission denials gracefully?
- What's the difference between approximate and precise location permissions?
- How do you migrate existing apps to new permission models?
- What are the best practices for requesting sensitive permissions?

## References

- [Android 14 Privacy Changes](https://developer.android.com/about/versions/14/privacy)
- [Permission Best Practices](https://developer.android.com/training/permissions/requesting)

## Related Questions

### Prerequisites (Easier)
- [[q-android-manifest-file--android--easy]]
- [[q-android-app-components--android--easy]]

### Related (Same Level)
- [[q-android-security-best-practices--android--medium]]
- [[q-android-security-practices-checklist--android--medium]]
- [[q-android-testing-strategies--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]

