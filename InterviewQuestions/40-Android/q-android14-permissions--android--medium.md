---
id: android-293
title: Android 14 Permissions / Разрешения Android 14
aliases: [Android 14 Permissions, Разрешения Android 14]
topic: android
subtopics:
  - permissions
  - privacy-sdks
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-permissions
  - q-android-manifest-file--android--easy
  - q-android-security-best-practices--android--medium
sources: []
created: 2025-10-15
updated: 2025-10-30
tags: [android/permissions, android/privacy-sdks, difficulty/medium]
date created: Thursday, October 30th 2025, 11:36:03 am
date modified: Sunday, November 2nd 2025, 12:50:18 pm
---

# Вопрос (RU)

> Какие изменения в системе разрешений появились в Android 13-14, и как правильно их обрабатывать?

# Question (EN)

> What permission changes were introduced in Android 13-14, and how should they be handled correctly?

## Ответ (RU)

Android 13+ (API 33+) кардинально изменил систему разрешений, заменив широкие разрешения на хранилище гранулярными медиа-разрешениями и добавив обязательное разрешение на уведомления.

### 1. Photo Picker — Доступ Без Разрешений

Photo Picker позволяет выбирать медиа без запроса разрешений:

```kotlin
class PhotoPickerManager(private val activity: AppCompatActivity) {
    private val picker = activity.registerForActivityResult(
        ActivityResultContracts.PickVisualMedia()
    ) { uri -> uri?.let { handlePhoto(it) } }

    fun pickPhoto() {
        // ✅ Разрешения не требуются
        picker.launch(PickVisualMediaRequest(
            ActivityResultContracts.PickVisualMedia.ImageOnly
        ))
    }
}
```

### 2. Гранулярные Медиа-разрешения (API 33+)

Вместо `READ_EXTERNAL_STORAGE` используются раздельные разрешения:

```kotlin
fun getMediaPermissions(needsImages: Boolean, needsVideo: Boolean): Array<String> {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        buildList {
            if (needsImages) add(Manifest.permission.READ_MEDIA_IMAGES)
            if (needsVideo) add(Manifest.permission.READ_MEDIA_VIDEO)
        }.toTypedArray()
    } else {
        arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE) // ❌ Устаревший подход
    }
}
```

### 3. Разрешение На Уведомления (API 33+)

С Android 13 требуется явное разрешение `POST_NOTIFICATIONS`:

```kotlin
fun checkNotificationPermission(context: Context): Boolean {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        ContextCompat.checkSelfPermission(
            context, Manifest.permission.POST_NOTIFICATIONS
        ) == PackageManager.PERMISSION_GRANTED
    } else {
        true  // На старых версиях не требуется
    }
}
```

### 4. Частичный Доступ К Медиа (API 34+)

Пользователь может предоставить доступ только к выбранным фото/видео:

```kotlin
// ✅ Обработка частичного доступа
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
    when {
        checkSelfPermission(READ_MEDIA_VISUAL_USER_SELECTED) == GRANTED ->
            loadSelectedMedia()
        checkSelfPermission(READ_MEDIA_IMAGES) == GRANTED ->
            loadAllMedia()
    }
}
```

### 5. Конфигурация Манифеста

```xml
<!-- Уведомления (API 33+) -->
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

<!-- Гранулярные медиа (API 33+) -->
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
<uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />

<!-- Частичный доступ (API 34+) -->
<uses-permission android:name="android.permission.READ_MEDIA_VISUAL_USER_SELECTED" />

<!-- Устаревший API (до API 33) -->
<uses-permission
    android:name="android.permission.READ_EXTERNAL_STORAGE"
    android:maxSdkVersion="32" />
```

### Стратегия Миграции

1. **Приоритет Photo Picker** для выбора медиа
2. **Запрос разрешений в контексте** использования
3. **Graceful degradation** для старых версий
4. **Объяснение необходимости** разрешений пользователю

## Answer (EN)

Android 13+ (API 33+) fundamentally changed the permission system, replacing broad storage permissions with granular media permissions and adding mandatory notification permissions.

### 1. Photo Picker — Permission-Free Access

Photo Picker allows media selection without requesting permissions:

```kotlin
class PhotoPickerManager(private val activity: AppCompatActivity) {
    private val picker = activity.registerForActivityResult(
        ActivityResultContracts.PickVisualMedia()
    ) { uri -> uri?.let { handlePhoto(it) } }

    fun pickPhoto() {
        // ✅ No permission required
        picker.launch(PickVisualMediaRequest(
            ActivityResultContracts.PickVisualMedia.ImageOnly
        ))
    }
}
```

### 2. Granular Media Permissions (API 33+)

Instead of `READ_EXTERNAL_STORAGE`, use separate permissions:

```kotlin
fun getMediaPermissions(needsImages: Boolean, needsVideo: Boolean): Array<String> {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        buildList {
            if (needsImages) add(Manifest.permission.READ_MEDIA_IMAGES)
            if (needsVideo) add(Manifest.permission.READ_MEDIA_VIDEO)
        }.toTypedArray()
    } else {
        arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE) // ❌ Legacy approach
    }
}
```

### 3. Notification Permission (API 33+)

Android 13 requires explicit `POST_NOTIFICATIONS` permission:

```kotlin
fun checkNotificationPermission(context: Context): Boolean {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        ContextCompat.checkSelfPermission(
            context, Manifest.permission.POST_NOTIFICATIONS
        ) == PackageManager.PERMISSION_GRANTED
    } else {
        true  // Not required on older versions
    }
}
```

### 4. Partial Media Access (API 34+)

Users can grant access to selected photos/videos only:

```kotlin
// ✅ Handle partial access
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
    when {
        checkSelfPermission(READ_MEDIA_VISUAL_USER_SELECTED) == GRANTED ->
            loadSelectedMedia()
        checkSelfPermission(READ_MEDIA_IMAGES) == GRANTED ->
            loadAllMedia()
    }
}
```

### 5. Manifest Configuration

```xml
<!-- Notifications (API 33+) -->
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

<!-- Granular media (API 33+) -->
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
<uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />

<!-- Partial access (API 34+) -->
<uses-permission android:name="android.permission.READ_MEDIA_VISUAL_USER_SELECTED" />

<!-- Legacy API (pre-API 33) -->
<uses-permission
    android:name="android.permission.READ_EXTERNAL_STORAGE"
    android:maxSdkVersion="32" />
```

### Migration Strategy

1. **Prioritize Photo Picker** for media selection
2. **Request permissions contextually** when needed
3. **Graceful degradation** for older versions
4. **Explain permission necessity** to users

## Follow-ups

- How do you handle permission denial with rationale UI using `shouldShowRequestPermissionRationale`?
- What is the two-step background location request flow introduced in API 29?
- How do you migrate from `READ_EXTERNAL_STORAGE` to granular media permissions while maintaining backward compatibility?
- When should you use Photo Picker versus requesting `READ_MEDIA_IMAGES` permission?
- What are the differences between partial access (`READ_MEDIA_VISUAL_USER_SELECTED`) and full access (`READ_MEDIA_IMAGES`)?

## References

- [[c-permissions]] - Permission model fundamentals
- [Android Permissions Best Practices](https://developer.android.com/training/permissions/requesting)
- [Granular Media Permissions](https://developer.android.com/about/versions/13/behavior-changes-13#granular-media-permissions)
- [Photo Picker API](https://developer.android.com/training/data-storage/shared/photopicker)
- [Android Behavior Changes](https://developer.android.com/about/versions/14/behavior-changes-14)

## Related Questions

### Prerequisites
- [[q-android-manifest-file--android--easy]] - AndroidManifest.xml structure and permission declaration
- Runtime permission model with Activity Result API

### Related
- [[q-android-security-best-practices--android--medium]] - Security implementation patterns and permission best practices
- Scoped storage and MediaStore API usage
- Permission request rationale UI patterns

### Advanced
- Background location two-step flow with foreground-first requirement
- Permission revocation handling and app lifecycle integration
- Scoped storage migration strategies for legacy apps
