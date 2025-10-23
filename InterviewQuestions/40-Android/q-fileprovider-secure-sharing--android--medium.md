---
id: 20251020-200800
title: FileProvider for Secure File Sharing / FileProvider для безопасного обмена файлами
aliases:
  - FileProvider for Secure File Sharing
  - FileProvider для безопасного обмена файлами
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
source: https://developer.android.com/reference/androidx/core/content/FileProvider
source_note: Android FileProvider documentation
status: reviewed
moc: moc-android
related:
  - q-android-permissions--android--medium
  - q-content-providers--android--medium
  - q-file-storage-android--android--medium
created: 2025-10-20
updated: 2025-10-20
tags:
  - android/files-media
  - android/permissions
  - fileprovider
  - content-provider
  - file-sharing
  - security
  - difficulty/medium
---
# Вопрос (RU)
> Что вы знаете о FileProvider?

# Question (EN)
> What do you know about FileProvider?

---

## Ответ (RU)

FileProvider - специальный подкласс ContentProvider для безопасного обмена файлами через content:// URI вместо file:// URI. Обеспечивает временные разрешения доступа и безопасность.

### Основные концепции

**1. Проблема file:// URI**
- Проблема: file:// URI требует изменения системных разрешений файлов
- Результат: небезопасный доступ для всех приложений
- Решение: content:// URI с временными разрешениями

**2. Content URI безопасность**
- Проблема: необходимость контролируемого доступа к файлам
- Результат: временные разрешения только для получающего приложения
- Решение: FileProvider генерирует безопасные content:// URI

### Реализация

**1. Определение FileProvider в манифесте**
```xml
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="com.example.fileprovider"
    android:exported="false"
    android:grantUriPermissions="true">
    <meta-data
        android:name="android.support.FILE_PROVIDER_PATHS"
        android:resource="@xml/file_paths" />
</provider>
```

**2. Определение доступных файлов**
```xml
<!-- res/xml/file_paths.xml -->
<paths xmlns:android="http://schemas.android.com/apk/res/android">
    <files-path name="images" path="images/" />
    <cache-path name="cache" path="." />
    <external-path name="external" path="." />
    <external-files-path name="external_files" path="." />
</paths>
```

**3. Генерация content URI**
```kotlin
fun getContentUri(context: Context, file: File): Uri {
    return FileProvider.getUriForFile(
        context,
        "com.example.fileprovider",
        file
    )
}

// Использование
val imageFile = File(context.filesDir, "images/photo.jpg")
val contentUri = getContentUri(context, imageFile)
```

**4. Обмен файлами через Intent**
```kotlin
fun shareImage(context: Context, imageFile: File) {
    val contentUri = FileProvider.getUriForFile(
        context,
        "com.example.fileprovider",
        imageFile
    )

    val shareIntent = Intent(Intent.ACTION_SEND).apply {
        type = "image/*"
        putExtra(Intent.EXTRA_STREAM, contentUri)
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    }

    context.startActivity(Intent.createChooser(shareIntent, "Share image"))
}
```

**5. Обработка полученных файлов**
```kotlin
fun handleReceivedUri(context: Context, uri: Uri) {
    try {
        val inputStream = context.contentResolver.openInputStream(uri)
        // Обработка файла
        inputStream?.use { stream ->
            // Чтение данных
        }
    } catch (e: SecurityException) {
        // Нет разрешения на доступ к файлу
    }
}
```

### Теория FileProvider

**ContentProvider архитектура:**
- FileProvider наследуется от ContentProvider
- Предоставляет доступ к файлам через content:// URI
- Управляет разрешениями доступа
- Интегрируется с системой безопасности Android

**URI типы:**
- **file://**: прямой доступ к файловой системе (небезопасно)
- **content://**: контролируемый доступ через ContentProvider (безопасно)
- **http://**: сетевые ресурсы
- **https://**: защищенные сетевые ресурсы

**Разрешения доступа:**
- **FLAG_GRANT_READ_URI_PERMISSION**: временное разрешение на чтение
- **FLAG_GRANT_WRITE_URI_PERMISSION**: временное разрешение на запись
- **FLAG_GRANT_PERSISTABLE_URI_PERMISSION**: постоянное разрешение
- **FLAG_GRANT_PREFIX_URI_PERMISSION**: разрешение для префикса URI

**Пути файлов:**
- **files-path**: внутреннее хранилище приложения
- **cache-path**: кэш приложения
- **external-path**: внешнее хранилище
- **external-files-path**: внешние файлы приложения
- **external-cache-path**: внешний кэш приложения

**Безопасность:**
- Временные разрешения действуют только пока активен получатель
- Невозможность доступа к файлам вне указанных путей
- Контроль доступа на уровне URI
- Защита от path traversal атак

**Best Practices:**
- Использовать уникальные authorities для каждого приложения
- Ограничивать доступ только необходимыми директориями
- Проверять разрешения перед доступом к файлам
- Использовать временные разрешения вместо постоянных
- Валидировать полученные URI

## Answer (EN)

FileProvider is a special ContentProvider subclass for secure file sharing via content:// URI instead of file:// URI. Provides temporary access permissions and security.

### Key Concepts

**1. file:// URI problem**
- Problem: file:// URI requires changing file system permissions
- Result: insecure access for all applications
- Solution: content:// URI with temporary permissions

**2. Content URI security**
- Problem: need for controlled file access
- Result: temporary permissions only for receiving application
- Solution: FileProvider generates secure content:// URI

### Implementation

**1. Define FileProvider in manifest**
```xml
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="com.example.fileprovider"
    android:exported="false"
    android:grantUriPermissions="true">
    <meta-data
        android:name="android.support.FILE_PROVIDER_PATHS"
        android:resource="@xml/file_paths" />
</provider>
```

**2. Define available files**
```xml
<!-- res/xml/file_paths.xml -->
<paths xmlns:android="http://schemas.android.com/apk/res/android">
    <files-path name="images" path="images/" />
    <cache-path name="cache" path="." />
    <external-path name="external" path="." />
    <external-files-path name="external_files" path="." />
</paths>
```

**3. Generate content URI**
```kotlin
fun getContentUri(context: Context, file: File): Uri {
    return FileProvider.getUriForFile(
        context,
        "com.example.fileprovider",
        file
    )
}

// Usage
val imageFile = File(context.filesDir, "images/photo.jpg")
val contentUri = getContentUri(context, imageFile)
```

**4. Share files via Intent**
```kotlin
fun shareImage(context: Context, imageFile: File) {
    val contentUri = FileProvider.getUriForFile(
        context,
        "com.example.fileprovider",
        imageFile
    )

    val shareIntent = Intent(Intent.ACTION_SEND).apply {
        type = "image/*"
        putExtra(Intent.EXTRA_STREAM, contentUri)
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    }

    context.startActivity(Intent.createChooser(shareIntent, "Share image"))
}
```

**5. Handle received files**
```kotlin
fun handleReceivedUri(context: Context, uri: Uri) {
    try {
        val inputStream = context.contentResolver.openInputStream(uri)
        // Process file
        inputStream?.use { stream ->
            // Read data
        }
    } catch (e: SecurityException) {
        // No permission to access file
    }
}
```

### FileProvider Theory

**ContentProvider architecture:**
- FileProvider extends ContentProvider
- Provides file access via content:// URI
- Manages access permissions
- Integrates with Android security system

**URI types:**
- **file://**: direct file system access (insecure)
- **content://**: controlled access via ContentProvider (secure)
- **http://**: network resources
- **https://**: secure network resources

**Access permissions:**
- **FLAG_GRANT_READ_URI_PERMISSION**: temporary read permission
- **FLAG_GRANT_WRITE_URI_PERMISSION**: temporary write permission
- **FLAG_GRANT_PERSISTABLE_URI_PERMISSION**: permanent permission
- **FLAG_GRANT_PREFIX_URI_PERMISSION**: permission for URI prefix

**File paths:**
- **files-path**: app internal storage
- **cache-path**: app cache
- **external-path**: external storage
- **external-files-path**: app external files
- **external-cache-path**: app external cache

**Security:**
- Temporary permissions last only while receiver is active
- No access to files outside specified paths
- Access control at URI level
- Protection against path traversal attacks

**Best Practices:**
- Use unique authorities for each application
- Restrict access to only necessary directories
- Check permissions before file access
- Use temporary permissions instead of permanent
- Validate received URIs

## Follow-ups
- How to handle FileProvider with different Android versions?
- What's the difference between FileProvider and MediaStore?
- How to implement custom ContentProvider for file sharing?
