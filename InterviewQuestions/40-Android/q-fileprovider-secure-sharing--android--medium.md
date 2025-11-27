---
id: android-446
title: FileProvider for Secure File Sharing / FileProvider для безопасного обмена файлами
aliases: [FileProvider, FileProvider for Secure File Sharing, FileProvider для безопасного обмена файлами, Безопасный обмен файлами]
topic: android
subtopics:
  - files-media
  - permissions
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
sources:
  - https://developer.android.com/reference/androidx/core/content/FileProvider
status: reviewed
moc: moc-android
related:
  - c-content-provider
  - q-android-security-practices-checklist--android--medium
  - q-android-storage-types--android--medium
  - q-api-file-upload-server--android--medium
  - q-how-to-display-svg-string-as-a-vector-file--android--medium
  - q-runtime-permissions-best-practices--android--medium
created: 2025-10-20
updated: 2025-10-28
tags: [android/files-media, android/permissions, content-provider, difficulty/medium, file-sharing, security]
date created: Saturday, November 1st 2025, 12:46:49 pm
date modified: Tuesday, November 25th 2025, 8:54:00 pm
---
# Вопрос (RU)
> Что вы знаете о FileProvider?

# Question (EN)
> What do you know about FileProvider?

---

## Ответ (RU)

[[c-content-provider|FileProvider]] — специализированный ContentProvider для безопасного межпроцессного обмена файлами через `content://` URI вместо прямых `file://` URI. Предоставляет временные и адресные разрешения на доступ к конкретным файлам без изменения их системных прав доступа.

### Проблема file:// URI

С Android 7.0 (API 24) передача `file://` URI через Intent вызывает `FileUriExposedException`. Причины:
- `file://` опирается на файловые разрешения процесса и часто требовал глобальных прав на чтение (например, MODE_WORLD_READABLE — deprecated), что приводило к избыточному доступу
- При прямой передаче пути через `file://` сложно обеспечить принцип минимально необходимых прав и неочевидно, какие файлы могут быть доступны при ошибочной настройке прав
- Невозможность централизованно управлять и отзываться разрешения на конкретные ресурсы после передачи

### Архитектура FileProvider

```kotlin
// AndroidManifest.xml
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="${applicationId}.fileprovider"  // ✅ Уникальный authority
    android:exported="false"                             // ✅ Запрет прямого таргетирования провайдера
    android:grantUriPermissions="true">                  // ✅ Разрешить временные grant'ы по URI
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

// Передача с временными разрешениями (чтение)
val intent = Intent(Intent.ACTION_SEND).apply {
    type = "image/*"
    putExtra(Intent.EXTRA_STREAM, contentUri)
    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)  // ✅ Временное право на чтение для целевого получателя
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
- Grant выдаётся для конкретного `content://` URI и указанного получателя
- Обычно действует, пока задача/активность получателя актуальна; может быть отозван системой (например, при перезагрузке устройства)
- Не требует от получателя собственных runtime permissions к файловой системе, если выдан соответствующий grant

**Контроль доступа:**
- Пути в `file_paths.xml` ограничивают набор файлов, доступных через FileProvider
- Разные authority изолируют FileProvider разных приложений
- `exported="false"` запрещает прямое таргетирование провайдера из других приложений; доступ возможен только к тем URI, на которые явно выданы разрешения через Intent-флаги

**Потенциальные уязвимости:**
- ❌ `external-path` с `path="."` открывает слишком широкий доступ к внешнему хранилищу
- ❌ Необработанные пользовательские пути (path traversal) при формировании File-объектов до передачи в FileProvider
- ✅ Используйте минимально необходимые директории и точечные пути

## Answer (EN)

[[c-content-provider|FileProvider]] is a specialized ContentProvider for secure inter-process file sharing using `content://` URIs instead of direct `file://` URIs. It provides temporary, URI-scoped permissions to specific files without changing their underlying filesystem permissions.

### The file:// URI Problem

Starting with Android 7.0 (API 24), passing `file://` URIs through Intents throws `FileUriExposedException`. Reasons:
- `file://` relies on the sender's filesystem permissions and historically used global/world-readable flags (e.g., MODE_WORLD_READABLE — deprecated), which can overexpose data
- Directly exposing raw filesystem paths via `file://` makes it hard to enforce least-privilege and to reason about what may be accessible if permissions are misconfigured
- There is no built-in, fine-grained mechanism to centrally manage and revoke access to specific resources once a `file://` path is shared

### FileProvider Architecture

```kotlin
// AndroidManifest.xml
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="${applicationId}.fileprovider"  // ✅ Unique authority
    android:exported="false"                             // ✅ Prevent direct targeting of the provider
    android:grantUriPermissions="true">                  // ✅ Allow temporary URI grants
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

// Share with temporary read permissions
val intent = Intent(Intent.ACTION_SEND).apply {
    type = "image/*"
    putExtra(Intent.EXTRA_STREAM, contentUri)
    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)  // ✅ Temporary read access for the resolved target(s)
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
- Grants are issued for specific `content://` URIs and the resolved recipient components
- Typically remain valid while the recipient's task/component is in use and may be cleared by the system (e.g., on device reboot)
- Do not require the receiving app to hold its own filesystem runtime permissions for that file, as long as the appropriate grant flag (read/write) is provided

**Access Control:**
- Paths in `file_paths.xml` constrain which files are exposed via FileProvider
- Distinct authorities isolate FileProviders between apps
- `exported="false"` prevents other apps from directly targeting the provider; access is only possible to URIs for which grants have been explicitly provided via Intent flags

**Potential Vulnerabilities:**
- ❌ `external-path` with `path="."` exposes an overly broad portion of external storage
- ❌ Unvalidated, user-controlled paths (path traversal) when constructing File instances before passing them to FileProvider
- ✅ Always expose only the minimal required directories and specific paths

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
