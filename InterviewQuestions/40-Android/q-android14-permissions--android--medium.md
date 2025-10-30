---
id: 20251012-122776
title: Android 14 Permissions / Разрешения Android 14
aliases: ["Android 14 Permissions", "Разрешения Android 14"]
topic: android
subtopics: [permissions, privacy-sdks]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-manifest-file--android--easy, q-android-security-best-practices--android--medium, q-android-security-practices-checklist--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-29
tags: [android/permissions, android/privacy-sdks, difficulty/medium]
---
# Вопрос (RU)
> Какие изменения в системе разрешений появились в Android 14, и как правильно их обрабатывать?

# Question (EN)
> What permission changes were introduced in Android 14, and how should they be handled correctly?

## Ответ (RU)

Android 13+ (API 33+) кардинально изменил систему разрешений, заменив широкие разрешения на хранилище гранулярными медиа-разрешениями и добавив обязательное разрешение на уведомления.

**1. Photo Picker — доступ без разрешений**

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

**2. Гранулярные медиа-разрешения**

Вместо `READ_EXTERNAL_STORAGE` используются раздельные разрешения:

```kotlin
fun getMediaPermissions(needsImages: Boolean, needsVideo: Boolean): Array<String> {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        buildList {
            if (needsImages) add(Manifest.permission.READ_MEDIA_IMAGES)
            if (needsVideo) add(Manifest.permission.READ_MEDIA_VIDEO)
        }.toTypedArray()
    } else {
        // ❌ Устаревший подход
        arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE)
    }
}
```

**3. Разрешение на уведомления**

С Android 13 требуется явное разрешение `POST_NOTIFICATIONS`:

```kotlin
fun checkNotificationPermission(context: Context): Boolean {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        // ✅ Проверяем разрешение
        ContextCompat.checkSelfPermission(
            context, Manifest.permission.POST_NOTIFICATIONS
        ) == PackageManager.PERMISSION_GRANTED
    } else {
        true  // На старых версиях не требуется
    }
}
```

**4. Частичный доступ к медиа (Android 14)**

Пользователь может предоставить доступ только к выбранным фото/видео:

```kotlin
// Обработка частичного доступа
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
    when {
        checkSelfPermission(READ_MEDIA_VISUAL_USER_SELECTED) == GRANTED -> {
            // ✅ Частичный доступ предоставлен
            loadSelectedMedia()
        }
        checkSelfPermission(READ_MEDIA_IMAGES) == GRANTED -> {
            // ✅ Полный доступ
            loadAllMedia()
        }
    }
}
```

**5. Конфигурация манифеста**

```xml
<!-- Уведомления (Android 13+) -->
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

<!-- Гранулярные медиа (Android 13+) -->
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
<uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />

<!-- Частичный доступ (Android 14+) -->
<uses-permission android:name="android.permission.READ_MEDIA_VISUAL_USER_SELECTED" />

<!-- Устаревший API (до Android 13) -->
<uses-permission
    android:name="android.permission.READ_EXTERNAL_STORAGE"
    android:maxSdkVersion="32" />
```

**Ключевые версии:**
- API 34 (Android 14): частичный доступ к медиа, Health Connect
- API 33 (Android 13): гранулярные медиа-разрешения, POST_NOTIFICATIONS
- API 31 (Android 12): приблизительная геолокация, Bluetooth-разрешения

**Стратегия миграции:**
1. Приоритет Photo Picker для выбора медиа
2. Запрос разрешений в контексте использования
3. Graceful degradation для старых версий
4. Объяснение необходимости разрешений пользователю

## Answer (EN)

Android 13+ (API 33+) fundamentally changed the permission system, replacing broad storage permissions with granular media permissions and adding mandatory notification permissions.

**1. Photo Picker — Permission-Free Access**

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

**2. Granular Media Permissions**

Instead of `READ_EXTERNAL_STORAGE`, use separate permissions:

```kotlin
fun getMediaPermissions(needsImages: Boolean, needsVideo: Boolean): Array<String> {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        buildList {
            if (needsImages) add(Manifest.permission.READ_MEDIA_IMAGES)
            if (needsVideo) add(Manifest.permission.READ_MEDIA_VIDEO)
        }.toTypedArray()
    } else {
        // ❌ Legacy approach
        arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE)
    }
}
```

**3. Notification Permission**

Android 13 requires explicit `POST_NOTIFICATIONS` permission:

```kotlin
fun checkNotificationPermission(context: Context): Boolean {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        // ✅ Check permission
        ContextCompat.checkSelfPermission(
            context, Manifest.permission.POST_NOTIFICATIONS
        ) == PackageManager.PERMISSION_GRANTED
    } else {
        true  // Not required on older versions
    }
}
```

**4. Partial Media Access (Android 14)**

Users can grant access to selected photos/videos only:

```kotlin
// Handle partial access
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
    when {
        checkSelfPermission(READ_MEDIA_VISUAL_USER_SELECTED) == GRANTED -> {
            // ✅ Partial access granted
            loadSelectedMedia()
        }
        checkSelfPermission(READ_MEDIA_IMAGES) == GRANTED -> {
            // ✅ Full access
            loadAllMedia()
        }
    }
}
```

**5. Manifest Configuration**

```xml
<!-- Notifications (Android 13+) -->
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

<!-- Granular media (Android 13+) -->
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
<uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />

<!-- Partial access (Android 14+) -->
<uses-permission android:name="android.permission.READ_MEDIA_VISUAL_USER_SELECTED" />

<!-- Legacy API (pre-Android 13) -->
<uses-permission
    android:name="android.permission.READ_EXTERNAL_STORAGE"
    android:maxSdkVersion="32" />
```

**Key Versions:**
- API 34 (Android 14): partial media access, Health Connect
- API 33 (Android 13): granular media permissions, POST_NOTIFICATIONS
- API 31 (Android 12): approximate location, Bluetooth permissions

**Migration Strategy:**
1. Prioritize Photo Picker for media selection
2. Request permissions contextually when needed
3. Graceful degradation for older versions
4. Explain permission necessity to users

## Follow-ups

- How do you handle permission denial with rationale UI using `shouldShowRequestPermissionRationale`?
- What is the two-step background location request flow introduced in Android 11?
- How do you migrate from `READ_EXTERNAL_STORAGE` to granular media permissions while maintaining backward compatibility?
- When should you use Photo Picker versus requesting `READ_MEDIA_IMAGES` permission?
- What are Health Connect permissions in Android 14 and how do they differ from standard permissions?

## References

- [[c-permissions]] - Permission model fundamentals
- [Android 14 Behavior Changes](https://developer.android.com/about/versions/14/behavior-changes-14)
- [Granular Media Permissions](https://developer.android.com/about/versions/13/behavior-changes-13#granular-media-permissions)
- [Photo Picker API](https://developer.android.com/training/data-storage/shared/photopicker)

## Related Questions

### Prerequisites
- [[q-android-manifest-file--android--easy]] - AndroidManifest.xml structure and permission declaration
- Runtime permission model (Activity Result API)

### Related
- [[q-android-security-best-practices--android--medium]] - Security implementation patterns and permission best practices
- [[q-android-security-practices-checklist--android--medium]] - Comprehensive security checklist
- Scoped storage and MediaStore API usage

### Advanced
- Background location two-step flow with foreground-first requirement
- Permission revocation handling and app lifecycle integration
- Scoped storage migration strategies for legacy apps
