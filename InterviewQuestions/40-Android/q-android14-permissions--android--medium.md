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
status: draft
moc: moc-android
related:
  - c-permissions
  - q-android-lint-tool--android--medium
  - q-android-manifest-file--android--easy
  - q-android-security-best-practices--android--medium
  - q-android-security-practices-checklist--android--medium
sources: []
created: 2024-10-15
updated: 2025-11-10
tags: [android/permissions, android/privacy-sdks, difficulty/medium]

date created: Saturday, November 1st 2025, 12:46:44 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---

# Вопрос (RU)

> Какие изменения в системе разрешений появились в Android 13-14, и как правильно их обрабатывать?

# Question (EN)

> What permission changes were introduced in Android 13-14, and how should they be handled correctly?

## Ответ (RU)

Android 13 (API 33) и Android 14 (API 34) усилили модель разрешений для медиа и уведомлений:
- добавлены гранулярные медиа-разрешения вместо одного широкого `READ_EXTERNAL_STORAGE` для устройств с API 33+;
- введено отдельное runtime-разрешение для уведомлений;
- добавлен частичный доступ к выбранным медиа в Android 14.

Важно: для API 32 и ниже `READ_EXTERNAL_STORAGE` остаётся актуальным; поведение зависит как от `Build.VERSION.SDK_INT`, так и от `targetSdkVersion`.

### 1. Photo Picker — Доступ Без Runtime-разрешений

Photo Picker позволяет выбирать медиа без запроса storage/media-разрешений (он даёт приложению прямой доступ только к выбранным пользователем элементам):

```kotlin
class PhotoPickerManager(private val activity: AppCompatActivity) {
    private val picker = activity.registerForActivityResult(
        ActivityResultContracts.PickVisualMedia()
    ) { uri -> uri?.let { handlePhoto(it) } }

    fun pickPhoto() {
        // ✅ Разрешения чтения хранилища/медиа не требуются
        picker.launch(PickVisualMediaRequest(
            ActivityResultContracts.PickVisualMedia.ImageOnly
        ))
    }
}
```

Используйте Photo Picker, когда достаточно выбора конкретных файлов пользователем, без доступа ко всей медиатеке.

### 2. Гранулярные Медиа-разрешения (API 33+)

На Android 13+ вместо `READ_EXTERNAL_STORAGE` используются раздельные разрешения для разных типов медиа:

```kotlin
fun getMediaPermissions(
    needsImages: Boolean,
    needsVideo: Boolean,
    needsAudio: Boolean
): Array<String> {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        buildList {
            if (needsImages) add(Manifest.permission.READ_MEDIA_IMAGES)
            if (needsVideo) add(Manifest.permission.READ_MEDIA_VIDEO)
            if (needsAudio) add(Manifest.permission.READ_MEDIA_AUDIO)
        }.toTypedArray()
    } else {
        // ✅ Backward-compatible: для API <= 32 требуется широкое разрешение
        arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE)
    }
}
```

### 3. Разрешение На Уведомления (API 33+)

Начиная с Android 13 для приложений с `targetSdkVersion >= 33` требуется явное runtime-разрешение `POST_NOTIFICATIONS`:

```kotlin
fun hasNotificationPermission(context: Context): Boolean {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
        context.applicationInfo.targetSdkVersion >= Build.VERSION_CODES.TIRAMISU
    ) {
        ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.POST_NOTIFICATIONS
        ) == PackageManager.PERMISSION_GRANTED
    } else {
        // Для старых версий/targetSdk разрешение не запрашивается как runtime
        true
    }
}
```

Правильно: запрашивать `POST_NOTIFICATIONS` только когда реально показываете уведомления, обычно после пояснения ценности.

### 4. Частичный Доступ К Медиа (API 34+)

В Android 14 пользователь может предоставить доступ только к выбранным фото/видео через `READ_MEDIA_VISUAL_USER_SELECTED`. Возможны сценарии:
- частичный доступ (`READ_MEDIA_VISUAL_USER_SELECTED`);
- полный доступ к изображениям (`READ_MEDIA_IMAGES`) и/или видео (`READ_MEDIA_VIDEO`);
- комбинация этих разрешений, в том числе downgrade/upgrade при повторном запросе.

Пример обработки (упрощённо):

```kotlin
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
    when {
        ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.READ_MEDIA_VISUAL_USER_SELECTED
        ) == PackageManager.PERMISSION_GRANTED -> {
            // Доступ только к выбранным пользователем визуальным медиа
            loadSelectedMedia()
        }
        ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.READ_MEDIA_IMAGES
        ) == PackageManager.PERMISSION_GRANTED ||
        ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.READ_MEDIA_VIDEO
        ) == PackageManager.PERMISSION_GRANTED -> {
            // Доступ ко всей разрешённой медиатеке соответствующего типа
            loadAllMedia()
        }
        else -> {
            // Нет доступа — запросить нужные разрешения или использовать Photo Picker
            requestMediaPermissions()
        }
    }
}
```

(В реальном коде необходимо корректно обрабатывать результаты запросов и возможные изменения выбора пользователя.)

### 5. Конфигурация Манифеста

```xml
<!-- Уведомления (API 33+ runtime для targetSdk >= 33) -->
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

<!-- Гранулярные медиа (API 33+) -->
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
<uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />
<uses-permission android:name="android.permission.READ_MEDIA_AUDIO" />

<!-- Частичный доступ (API 34+) -->
<uses-permission android:name="android.permission.READ_MEDIA_VISUAL_USER_SELECTED" />

<!-- Backward compatibility (до API 33) -->
<uses-permission
    android:name="android.permission.READ_EXTERNAL_STORAGE"
    android:maxSdkVersion="32" />
```

### Стратегия Миграции

1. Предпочитать Photo Picker, когда нужен выбор конкретных файлов пользователем.
2. Использовать гранулярные медиа-разрешения (`READ_MEDIA_*`) только при необходимости прямого доступа (MediaStore/файлы) к более широкому набору медиа.
3. Обеспечить совместимость: `READ_EXTERNAL_STORAGE` для API <= 32 через `maxSdkVersion` в манифесте и ветвление логики по версии SDK.
4. Запрашивать разрешения в контексте использования (on-demand, с UI-объяснением причин).
5. Обрабатывать частичный доступ в Android 14+, учитывая комбинации `READ_MEDIA_VISUAL_USER_SELECTED` и `READ_MEDIA_*`.

## Answer (EN)

Android 13 (API 33) and Android 14 (API 34) strengthened the permission model for media and notifications by:
- introducing granular media permissions instead of a single broad `READ_EXTERNAL_STORAGE` on API 33+ devices;
- adding a dedicated runtime permission for notifications;
- adding partial access to selected media on Android 14.

Important: for API 32 and below, `READ_EXTERNAL_STORAGE` is still valid; behavior depends on both `Build.VERSION.SDK_INT` and your `targetSdkVersion`.

### 1. Photo Picker — Permission-Free Runtime Access

Photo Picker allows selecting media without requesting storage/media runtime permissions (it grants direct access only to items explicitly chosen by the user):

```kotlin
class PhotoPickerManager(private val activity: AppCompatActivity) {
    private val picker = activity.registerForActivityResult(
        ActivityResultContracts.PickVisualMedia()
    ) { uri -> uri?.let { handlePhoto(it) } }

    fun pickPhoto() {
        // ✅ No storage/media runtime permission required
        picker.launch(PickVisualMediaRequest(
            ActivityResultContracts.PickVisualMedia.ImageOnly
        ))
    }
}
```

Prefer Photo Picker when user-selected files are sufficient and you do not need broad library access.

### 2. Granular Media Permissions (API 33+)

On Android 13+, instead of `READ_EXTERNAL_STORAGE`, use separate permissions per media type:

```kotlin
fun getMediaPermissions(
    needsImages: Boolean,
    needsVideo: Boolean,
    needsAudio: Boolean
): Array<String> {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        buildList {
            if (needsImages) add(Manifest.permission.READ_MEDIA_IMAGES)
            if (needsVideo) add(Manifest.permission.READ_MEDIA_VIDEO)
            if (needsAudio) add(Manifest.permission.READ_MEDIA_AUDIO)
        }.toTypedArray()
    } else {
        // ✅ Backward-compatible: required for API <= 32
        arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE)
    }
}
```

### 3. Notification Permission (API 33+)

Starting with Android 13, apps with `targetSdkVersion >= 33` must request the `POST_NOTIFICATIONS` runtime permission:

```kotlin
fun hasNotificationPermission(context: Context): Boolean {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
        context.applicationInfo.targetSdkVersion >= Build.VERSION_CODES.TIRAMISU
    ) {
        ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.POST_NOTIFICATIONS
        ) == PackageManager.PERMISSION_GRANTED
    } else {
        // For older platform/targets, notifications are allowed without this runtime permission
        true
    }
}
```

Best practice: request `POST_NOTIFICATIONS` only when you actually plan to show notifications, ideally after explaining their value.

### 4. Partial Media Access (API 34+)

On Android 14, users can grant access only to selected photos/videos via `READ_MEDIA_VISUAL_USER_SELECTED`. Possible states:
- partial access (`READ_MEDIA_VISUAL_USER_SELECTED` only);
- full access via `READ_MEDIA_IMAGES` and/or `READ_MEDIA_VIDEO`;
- combinations and transitions between them when you re-request permissions.

Example handling (simplified):

```kotlin
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
    when {
        ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.READ_MEDIA_VISUAL_USER_SELECTED
        ) == PackageManager.PERMISSION_GRANTED -> {
            // Access only to user-selected visual media
            loadSelectedMedia()
        }
        ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.READ_MEDIA_IMAGES
        ) == PackageManager.PERMISSION_GRANTED ||
        ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.READ_MEDIA_VIDEO
        ) == PackageManager.PERMISSION_GRANTED -> {
            // Access to the full media library for the granted types
            loadAllMedia()
        }
        else -> {
            // No access: request appropriate permissions or fall back to Photo Picker
            requestMediaPermissions()
        }
    }
}
```

(Real implementations must handle permission request results and changes in the user selection over time.)

### 5. Manifest Configuration

```xml
<!-- Notifications (API 33+ runtime for targetSdk >= 33) -->
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

<!-- Granular media (API 33+) -->
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
<uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />
<uses-permission android:name="android.permission.READ_MEDIA_AUDIO" />

<!-- Partial access (API 34+) -->
<uses-permission android:name="android.permission.READ_MEDIA_VISUAL_USER_SELECTED" />

<!-- Legacy / backward compatibility (pre-API 33) -->
<uses-permission
    android:name="android.permission.READ_EXTERNAL_STORAGE"
    android:maxSdkVersion="32" />
```

### Migration Strategy

1. Prioritize Photo Picker when user-selected media is enough.
2. Use granular `READ_MEDIA_*` permissions only when you need broader direct access (e.g., MediaStore queries, file processing in background, etc.).
3. Maintain backward compatibility: declare `READ_EXTERNAL_STORAGE` with `maxSdkVersion="32"` and branch logic by SDK version.
4. Request permissions contextually, close to the feature that needs them, with clear rationale.
5. Handle Android 14 partial access by checking both `READ_MEDIA_VISUAL_USER_SELECTED` and `READ_MEDIA_*` and adapting behavior.

## Follow-ups

- How do you handle permission denial with rationale UI using `shouldShowRequestPermissionRationale`?
- What is the two-step background location request flow introduced in API 29?
- How do you migrate from `READ_EXTERNAL_STORAGE` to granular media permissions while maintaining backward compatibility?
- When should you use Photo Picker versus requesting `READ_MEDIA_IMAGES` (and related) permissions?
- What are the differences between partial access (`READ_MEDIA_VISUAL_USER_SELECTED`) and full access (`READ_MEDIA_IMAGES`/`READ_MEDIA_VIDEO`)?

## References

- [[c-permissions]] - Permission model fundamentals
- [Android Permissions Best Practices](https://developer.android.com/training/permissions/requesting)
- [Granular Media Permissions](https://developer.android.com/about/versions/13/behavior-changes-13#granular-media-permissions)
- [Photo Picker API](https://developer.android.com/training/data-storage/shared/photopicker)
- [Android 14 Behavior Changes](https://developer.android.com/about/versions/14/behavior-changes-14)

## Related Questions

### Prerequisites
- [[q-android-manifest-file--android--easy]] - AndroidManifest.xml structure and permission declaration
- Runtime permission model with `Activity` Result API

### Related
- [[q-android-security-best-practices--android--medium]] - Security implementation patterns and permission best practices
- Scoped storage and MediaStore API usage
- Permission request rationale UI patterns

### Advanced
- Background location two-step flow with foreground-first requirement
- Permission revocation handling and app lifecycle integration
- Scoped storage migration strategies for legacy apps