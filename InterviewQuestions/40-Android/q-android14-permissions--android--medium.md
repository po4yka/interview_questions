---
id: 20251012-122776
title: Android 14 Permissions / Разрешения Android 14
aliases: ["Android 14 Permissions", "Разрешения Android 14"]
topic: android
subtopics: [permissions, privacy-sdks]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-manifest-file--android--easy, q-android-security-best-practices--android--medium, q-android-security-practices-checklist--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-28
tags: [android/permissions, android/privacy-sdks, difficulty/medium]
---
# Вопрос (RU)
> Какие изменения в системе разрешений появились в Android 14, и как правильно их обрабатывать?

# Question (EN)
> What permission changes were introduced in Android 14, and how should they be handled correctly?

## Ответ (RU)

**Основные изменения в разрешениях Android 14:**

Android 14 (API 34) и Android 13 (API 33) внесли значительные изменения в систему разрешений, фокусируясь на конфиденциальности пользователя через гранулярный доступ к медиа, обязательные разрешения для уведомлений и более строгие требования для фоновой геолокации.

**1. Photo Picker (Android 13+):**
Современный подход к выбору медиа без запроса разрешений на хранилище.

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
            // ✅ Разрешения не требуются
            photoPickerLauncher.launch(
                PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly)
            )
        } else {
            // ❌ Устаревший подход с разрешениями
            requestLegacyPermission()
        }
    }
}
```

**2. Гранулярные медиа-разрешения (Android 13+):**
Раздельные разрешения для изображений, видео и аудио вместо единого разрешения на хранилище.

```kotlin
// Запрос разрешений в зависимости от типа медиа
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
Обязательное разрешение `POST_NOTIFICATIONS` для отправки уведомлений.

```kotlin
// Запрос разрешения на уведомления
fun requestNotificationPermission(context: Context): Boolean {
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        // ✅ Проверяем и запрашиваем разрешение
        return ContextCompat.checkSelfPermission(
            context, Manifest.permission.POST_NOTIFICATIONS
        ) == PackageManager.PERMISSION_GRANTED
    }
    // ❌ На старых версиях разрешение не требуется
    return true
}
```

**4. Манифест (AndroidManifest.xml):**

```xml
<!-- Уведомления (Android 13+) -->
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

<!-- Гранулярный доступ к медиа (Android 13+) -->
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
<uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />

<!-- Устаревший доступ к хранилищу (Android 12 и ниже) -->
<uses-permission
    android:name="android.permission.READ_EXTERNAL_STORAGE"
    android:maxSdkVersion="32" />
```

**Ключевые изменения по версиям:**
- **Android 14 (API 34)**: Частичный доступ к фото/видео, разрешения Health Connect
- **Android 13 (API 33)**: Разрешение на уведомления, гранулярные медиа-разрешения
- **Android 12 (API 31)**: Приблизительная геолокация, разрешения Bluetooth

**Лучшие практики:**
- Использовать Photo Picker вместо разрешений на хранилище
- Запрашивать разрешения в контексте функциональности
- Корректно обрабатывать различия между версиями API
- Объяснять пользователю, зачем нужно разрешение
- Тестировать на нескольких версиях Android

## Answer (EN)

**Core Permission Changes in Android 14:**

Android 14 (API 34) and Android 13 (API 33) introduced significant permission system changes, focusing on user privacy through granular media access, mandatory notification permissions, and stricter background location requirements.

**1. Photo Picker (Android 13+):**
Modern approach for media selection without requesting storage permissions.

```kotlin
// Photo Picker implementation
class PhotoPickerManager(private val activity: AppCompatActivity) {
    private val photoPickerLauncher = activity.registerForActivityResult(
        ActivityResultContracts.PickVisualMedia()
    ) { uri: Uri? ->
        uri?.let { handlePhoto(it) }
    }

    fun pickPhoto() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            // ✅ No permission required
            photoPickerLauncher.launch(
                PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly)
            )
        } else {
            // ❌ Legacy approach with permissions
            requestLegacyPermission()
        }
    }
}
```

**2. Granular Media Permissions (Android 13+):**
Separate permissions for images, videos, and audio instead of single storage permission.

```kotlin
// Request permissions based on media type
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
Mandatory `POST_NOTIFICATIONS` permission for sending notifications.

```kotlin
// Request notification permission
fun requestNotificationPermission(context: Context): Boolean {
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        // ✅ Check and request permission
        return ContextCompat.checkSelfPermission(
            context, Manifest.permission.POST_NOTIFICATIONS
        ) == PackageManager.PERMISSION_GRANTED
    }
    // ❌ Not required on older versions
    return true
}
```

**4. Manifest Configuration (AndroidManifest.xml):**

```xml
<!-- Notifications (Android 13+) -->
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

<!-- Granular media access (Android 13+) -->
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
<uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />

<!-- Legacy storage access (Android 12 and below) -->
<uses-permission
    android:name="android.permission.READ_EXTERNAL_STORAGE"
    android:maxSdkVersion="32" />
```

**Key Changes by Version:**
- **Android 14 (API 34)**: Partial photo/video access, Health Connect permissions
- **Android 13 (API 33)**: Notification permission, granular media permissions
- **Android 12 (API 31)**: Approximate location, Bluetooth permissions

**Best Practices:**
- Use Photo Picker instead of storage permissions
- Request permissions contextually when functionality is needed
- Handle API version differences gracefully
- Explain to users why permission is needed
- Test across multiple Android versions

## Follow-ups

- How should you handle permission denial with rationale UI?
- What's the two-step background location request flow in Android 11+?
- How do you migrate from READ_EXTERNAL_STORAGE to granular media permissions?
- When should you use Photo Picker vs. requesting media permissions?
- What are Health Connect permissions in Android 14?

## References

- [[c-permissions]] - Permission model concepts
- [Android 14 Privacy Changes](https://developer.android.com/about/versions/14/privacy)
- [Permissions Best Practices](https://developer.android.com/training/permissions/requesting)
- [Photo Picker Guide](https://developer.android.com/training/data-storage/shared/photopicker)

## Related Questions

### Prerequisites
- [[q-android-manifest-file--android--easy]] - AndroidManifest.xml structure
- Runtime permission basics

### Related
- [[q-android-security-best-practices--android--medium]] - Security implementation patterns
- Permission handling strategies
- Activity result contracts usage

### Advanced
- Background location two-step flow
- Permission revocation handling
- Scoped storage migration strategies