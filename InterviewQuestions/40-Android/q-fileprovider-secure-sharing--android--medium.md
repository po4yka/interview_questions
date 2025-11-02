---
id: android-446
title: FileProvider for Secure File Sharing / FileProvider для безопасного обмена файлами
aliases: [FileProvider, FileProvider for Secure File Sharing, FileProvider для безопасного обмена файлами, Безопасный обмен файлами]
topic: android
subtopics: [files-media, permissions]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
sources: [https://developer.android.com/reference/androidx/core/content/FileProvider]
status: draft
moc: moc-android
related: [c-content-provider, q-android-storage-types--android--medium, q-runtime-permissions-best-practices--android--medium]
created: 2025-10-20
updated: 2025-10-28
tags: [android/files-media, android/permissions, content-provider, difficulty/medium, file-sharing, security]
date created: Tuesday, October 28th 2025, 7:39:08 am
date modified: Saturday, November 1st 2025, 5:43:35 pm
---

# Вопрос (RU)
> Что вы знаете о FileProvider?

# Question (EN)
> What do you know about FileProvider?

---

## Ответ (RU)

[[c-content-provider|FileProvider]] — специализированный ContentProvider для безопасного межпроцессного обмена файлами через `content://` URI вместо небезопасных `file://` URI. Предоставляет временные гранулярные разрешения без изменения системных прав доступа.

### Проблема file:// URI

С Android 7.0 (API 24) передача `file://` URI через Intent вызывает `FileUriExposedException`. Причины:
- `file://` требует глобальных разрешений на чтение (MODE_WORLD_READABLE — deprecated)
- Получатель имеет доступ ко всей файловой системе отправителя
- Невозможность отзыва разрешений после передачи

### Архитектура FileProvider

```kotlin
// AndroidManifest.xml
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="${applicationId}.fileprovider"  // ✅ Уникальный authority
    android:exported="false"                             // ✅ Запрет прямого доступа
    android:grantUriPermissions="true">                  // ✅ Временные разрешения
    <meta-data
        android:name="android.support.FILE_PROVIDER_PATHS"
        android:resource="@xml/file_paths" />
</provider>

// res/xml/file_paths.xml
<paths>
    <files-path name="images" path="images/" />          // ✅ Ограничение scope
    <cache-path name="temp" path="temp/" />
</paths>
```

### Использование

```kotlin
// Генерация content:// URI
val file = File(context.filesDir, "images/photo.jpg")
val contentUri = FileProvider.getUriForFile(
    context,
    "${context.packageName}.fileprovider",
    file
)
// content://com.example.fileprovider/images/photo.jpg

// Передача с временными разрешениями
val intent = Intent(Intent.ACTION_SEND).apply {
    type = "image/*"
    putExtra(Intent.EXTRA_STREAM, contentUri)
    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)  // ✅ Временное право на чтение
}
context.startActivity(Intent.createChooser(intent, null))
```

### Типы Путей

| Элемент | Системный путь | Назначение |
|---------|---------------|------------|
| `files-path` | `Context.getFilesDir()` | Приватные файлы |
| `cache-path` | `Context.getCacheDir()` | Временный кэш |
| `external-files-path` | `Context.getExternalFilesDir()` | Внешние файлы приложения |
| `external-cache-path` | `Context.getExternalCacheDir()` | Внешний кэш |
| `external-path` | `Environment.getExternalStorageDirectory()` | Публичное хранилище (deprecated API 29+) |

### Безопасность

**Временные разрешения:**
- Действуют только пока активен компонент-получатель (Activity/Service)
- Автоматически отзываются при уничтожении получателя
- Не требуют runtime permissions

**Контроль доступа:**
- Путь в `file_paths.xml` ограничивает доступные файлы
- Authority изолирует FileProvider разных приложений
- `exported="false"` блокирует прямой доступ через ContentResolver

**Потенциальные уязвимости:**
- ❌ `external-path` с `path="."` открывает всё внешнее хранилище
- ❌ Не валидированные пользовательские пути (path traversal)
- ✅ Используйте минимально необходимые директории

## Answer (EN)

[[c-content-provider|FileProvider]] is a specialized ContentProvider for secure inter-process file sharing using `content://` URIs instead of insecure `file://` URIs. It provides temporary granular permissions without modifying system file permissions.

### The file:// URI Problem

Starting with Android 7.0 (API 24), passing `file://` URIs through Intents throws `FileUriExposedException`. Reasons:
- `file://` requires global read permissions (MODE_WORLD_READABLE — deprecated)
- Receiver gains access to sender's entire file system
- No ability to revoke permissions after sharing

### FileProvider Architecture

```kotlin
// AndroidManifest.xml
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="${applicationId}.fileprovider"  // ✅ Unique authority
    android:exported="false"                             // ✅ Prevent direct access
    android:grantUriPermissions="true">                  // ✅ Enable temp permissions
    <meta-data
        android:name="android.support.FILE_PROVIDER_PATHS"
        android:resource="@xml/file_paths" />
</provider>

// res/xml/file_paths.xml
<paths>
    <files-path name="images" path="images/" />          // ✅ Restrict scope
    <cache-path name="temp" path="temp/" />
</paths>
```

### Usage

```kotlin
// Generate content:// URI
val file = File(context.filesDir, "images/photo.jpg")
val contentUri = FileProvider.getUriForFile(
    context,
    "${context.packageName}.fileprovider",
    file
)
// content://com.example.fileprovider/images/photo.jpg

// Share with temporary permissions
val intent = Intent(Intent.ACTION_SEND).apply {
    type = "image/*"
    putExtra(Intent.EXTRA_STREAM, contentUri)
    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)  // ✅ Temporary read access
}
context.startActivity(Intent.createChooser(intent, null))
```

### Path Types

| Element | System Path | Purpose |
|---------|-------------|---------|
| `files-path` | `Context.getFilesDir()` | Private app files |
| `cache-path` | `Context.getCacheDir()` | Temporary cache |
| `external-files-path` | `Context.getExternalFilesDir()` | External app files |
| `external-cache-path` | `Context.getExternalCacheDir()` | External cache |
| `external-path` | `Environment.getExternalStorageDirectory()` | Public storage (deprecated API 29+) |

### Security

**Temporary Permissions:**
- Active only while recipient component (Activity/Service) is alive
- Automatically revoked when recipient is destroyed
- No runtime permissions required

**Access Control:**
- Paths in `file_paths.xml` restrict accessible files
- Authority isolates FileProviders across apps
- `exported="false"` blocks direct ContentResolver access

**Potential Vulnerabilities:**
- ❌ `external-path` with `path="."` exposes entire external storage
- ❌ Unvalidated user-controlled paths (path traversal)
- ✅ Use minimally necessary directories

## Follow-ups
- How does FLAG_GRANT_PERSISTABLE_URI_PERMISSION differ from temporary grants?
- When should you use MediaStore API instead of FileProvider?
- How to handle FileProvider conflicts in multi-module apps with merged manifests?
- What happens if two apps use the same FileProvider authority?

## References
- [[c-content-provider|ContentProvider Architecture]]
- Official docs: https://developer.android.com/reference/androidx/core/content/FileProvider
- Security guide: https://developer.android.com/training/secure-file-sharing

## Related Questions

### Prerequisites
- [[q-android-storage-types--android--medium|Android Storage Types]]
- [[c-content-provider|ContentProvider Basics]]

### Related
- [[q-runtime-permissions-best-practices--android--medium|Runtime Permissions Best Practices]]
- [[q-intent-filters-android--android--medium|Intent Filters]]

### Advanced
- Custom ContentProvider implementation for advanced file sharing scenarios
- Scoped storage integration with FileProvider (Android 10+)
