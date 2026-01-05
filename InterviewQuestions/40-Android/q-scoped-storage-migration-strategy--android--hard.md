---
id: android-632
title: Scoped Storage Migration Strategy / Стратегия миграции на Scoped Storage
aliases: [Scoped Storage Migration Strategy, Стратегия миграции на Scoped Storage]
topic: android
subtopics: [files-media, permissions]
question_kind: android
difficulty: hard
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-storage-options, q-android-storage-types--android--medium, q-global-localization-strategy--android--hard, q-media3-migration-strategy--android--hard]
created: 2025-11-02
updated: 2025-11-10
tags: [android/files-media, android/permissions, difficulty/hard]
sources:
  - "https://developer.android.com/about/versions/11/privacy/storage"
  - "https://developer.android.com/training/data-storage"

---
# Вопрос (RU)
> Как мигрировать legacy-приложение на scoped storage, сохранив данные пользователей, обеспечив приватность и совместимость с бэкапом/экспортом?

# Question (EN)
> How do you migrate a legacy app to scoped storage while preserving user data, maintaining privacy, and supporting backup/export workflows?

---

## Ответ (RU)

## Краткая Версия
- Провести аудит всех мест записи/чтения файлов.
- Перенести данные в приватные и app-specific директории или в `MediaStore`/SAF в зависимости от типа данных.
- Отказаться от глобальных прав на внешнее хранилище в пользу scoped storage, `MediaStore`, SAF и точечных разрешений.
- Обеспечить корректные сценарии backup/export без утечек приватных данных.

## Подробная Версия
### Требования

- Функциональные:
  - Сохранить все пользовательские данные при обновлении.
  - Поддержать экспорт/импорт (backup/restore) пользовательских данных.
  - Обеспечить корректную работу с медиа и документами на Android 10+.
- Нефункциональные:
  - Минимизировать риск потери данных при миграции.
  - Обеспечить приватность и соответствие политикам Google Play.
  - Сохранить приемлемую производительность при миграции больших объёмов.

### Архитектура

- Чётко разделить уровни хранения:
  - Приватные данные приложения во внутреннем и app-specific external хранилищах.
  - Пользовательские медиа через `MediaStore` (коллекции с `RELATIVE_PATH`).
  - Документы и произвольные директории через SAF (`ACTION_OPEN_DOCUMENT*`).
- Использовать URI и `ContentResolver` / `DocumentFile` вместо прямых путей.
- Добавить модуль миграции, который запускается один раз после обновления и логирует прогресс.

См. также: [[c-android-storage-options]].

### 1. Аудит Данных

- Категоризируйте файлы: app-private (internal storage, `context.getFilesDir()` / `getCacheDir()`), app-specific external (`context.getExternalFilesDir()`), shared media (фото/видео/аудио через `MediaStore`), документы пользователя (через SAF).
- Определите, какие данные обязательны для экспортов/backup.
- Откажитесь от `WRITE_EXTERNAL_STORAGE`, используйте per-collection permissions (`READ_MEDIA_IMAGES` / `READ_MEDIA_VIDEO` / `READ_MEDIA_AUDIO` и т.п. на Android 13+).

### 2. Миграция (Android 10+)

- На первый запуск после обновления:
  - Если ранее писали в произвольные директории на внешнем хранилище, перенесите критичные файлы в:
    - app-private (`filesDir` / `noBackupFilesDir`) или
    - app-specific external (`getExternalFilesDir`) или
    - соответствующие коллекции `MediaStore`.
  - Для данных, которые по смыслу принадлежат пользователю (документы, произвольные папки), предложите выбрать директорию через `ACTION_OPEN_DOCUMENT_TREE` и сохраните доступ.

- Типичный паттерн миграции файлов в `MediaStore`:

```kotlin
val values = ContentValues().apply {
    put(MediaStore.MediaColumns.DISPLAY_NAME, legacyFile.name)
    put(MediaStore.MediaColumns.MIME_TYPE, "image/jpeg") // подобрать корректный MIME
    put(MediaStore.MediaColumns.RELATIVE_PATH, "Pictures/LegacyApp")
    put(MediaStore.MediaColumns.IS_PENDING, 1)
}

val collection = MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)
val uri = context.contentResolver.insert(collection, values)

uri?.let { destUri ->
    context.contentResolver.openOutputStream(destUri)?.use { output ->
        legacyFile.inputStream().use { input ->
            input.copyTo(output)
        }
    }

    val finalize = ContentValues().apply {
        put(MediaStore.MediaColumns.IS_PENDING, 0)
    }
    context.contentResolver.update(destUri, finalize, null, null)
}
```

- Старые файлы во внешнем хранилище помечайте для удаления после успешной миграции и (по возможности) явного подтверждения пользователя.

### 3. Доступ К Медиа

- Для записи в коллекции используйте `MediaStore` с `RELATIVE_PATH` и флагом `IS_PENDING` до завершения записи.
- Для чтения собственных файлов в app-specific директориях права не нужны; для доступа к общим медиа:
  - На Android 13+ используйте `READ_MEDIA_IMAGES` / `READ_MEDIA_VIDEO` / `READ_MEDIA_AUDIO`.
  - На Android 10–12 используйте `READ_EXTERNAL_STORAGE` (с учетом ограничений scoped storage).
- Не полагайтесь на прямые пути к файлам в общих медиа-директориях; работайте через URI.

### 4. Storage Access Framework

- Используйте `ACTION_OPEN_DOCUMENT` / `CREATE_DOCUMENT` / `ACTION_OPEN_DOCUMENT_TREE` только когда действительно требуется доступ к пользовательским документам или произвольным директориям вне app-specific/MediaStore.
- Сохраняйте персистентные разрешения через `takePersistableUriPermission`.
- Для операций (создание, чтение, удаление) используйте `DocumentFile` поверх полученных URI; не опирайтесь на абсолютные пути.

### 5. Backup/Export

- Управляйте включением/исключением файлов из Auto Backup через `android:fullBackupContent`; для данных, которые не должны бэкапиться, используйте `noBackupFilesDir`.
- Не путайте область `device-protected storage` с механизмами исключения из backup: она для доступа до разблокировки, а не для фильтрации бэкапа.
- Для пользовательских экспортов:
  - Создавайте временные копии в `cacheDir` или app-specific директории.
  - При необходимости шифруйте экспортируемые данные.
  - Проверяйте MIME-тип и размер перед шарингом; используйте явные `Intent` с корректно настроенным `ClipData` и `FLAG_GRANT_READ_URI_PERMISSION`.
- Учитывайте, что ADB backup устарел; опирайтесь на Auto Backup / Key-Value backup и пользовательские экспортные механизмы (через SAF/шаринг).

### 6. Permissions & Compliance

- Не запрашивайте `MANAGE_EXTERNAL_STORAGE`, если нет строго обоснованной необходимости и вы не соответствуете политикам Google Play.
- Обновите privacy policy и в явном виде объясните пользователю причины и последствия миграции.
- Логируйте процесс миграции (без чувствительных данных), реализуйте fallback: при ошибках сохранения в публичные директории сохраняйте данные в приватном хранилище и показывайте пользователю понятное уведомление.
- При поддержке Android 10 учитывайте флаг `requestLegacyExternalStorage=true` как временную меру для совместимости и заранее планируйте отказ от него на Android 11+.

---

## Answer (EN)

## Short Version
- Audit all legacy file reads/writes.
- Move data into private/app-specific directories or `MediaStore`/SAF depending on data type.
- Replace broad external storage access with scoped storage, `MediaStore`, SAF, and granular permissions.
- Preserve robust backup/export flows without leaking private data.

## Detailed Version
### Requirements

- Functional:
  - Preserve all user data during upgrade.
  - Support export/import (backup/restore) of user data.
  - Work correctly with media and documents on Android 10+.
- Non-functional:
  - Minimize risk of data loss during migration.
  - Ensure privacy and Google Play policy compliance.
  - Keep acceptable performance for large migrations.

### Architecture

- Clearly separate storage layers:
  - Private app data in internal and app-specific external storage.
  - User media via `MediaStore` (collections with `RELATIVE_PATH`).
  - Documents/custom directories via SAF (`ACTION_OPEN_DOCUMENT*`).
- Use URIs and `ContentResolver` / `DocumentFile` instead of direct file paths.
- Add a migration module that runs once after update and logs progress.

See also: [[c-android-storage-options]].

### 1. Audit Data

- Classify app-private (internal storage, `context.getFilesDir()` / `getCacheDir()`), app-specific external (`context.getExternalFilesDir()`), shared media (photos/videos/audio via `MediaStore`), and user documents (via SAF).
- Identify what must be preserved for exports/backup.
- Drop `WRITE_EXTERNAL_STORAGE`; use per-collection permissions (`READ_MEDIA_IMAGES` / `READ_MEDIA_VIDEO` / `READ_MEDIA_AUDIO`, etc. on Android 13+).

### 2. Migration (Android 10+)

- On first launch after update:
  - If you previously wrote to arbitrary directories on external storage, move critical files into:
    - app-private (`filesDir` / `noBackupFilesDir`), or
    - app-specific external (`getExternalFilesDir`), or
    - appropriate `MediaStore` collections.
  - For data that truly belongs to the user (documents, custom folders), prompt with `ACTION_OPEN_DOCUMENT_TREE` and persist access.

- Typical pattern for migrating files into `MediaStore`:

```kotlin
val values = ContentValues().apply {
    put(MediaStore.MediaColumns.DISPLAY_NAME, legacyFile.name)
    put(MediaStore.MediaColumns.MIME_TYPE, "image/jpeg") // pick correct MIME
    put(MediaStore.MediaColumns.RELATIVE_PATH, "Pictures/LegacyApp")
    put(MediaStore.MediaColumns.IS_PENDING, 1)
}

val collection = MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)
val uri = context.contentResolver.insert(collection, values)

uri?.let { destUri ->
    context.contentResolver.openOutputStream(destUri)?.use { output ->
        legacyFile.inputStream().use { input ->
            input.copyTo(output)
        }
    }

    val finalize = ContentValues().apply {
        put(MediaStore.MediaColumns.IS_PENDING, 0)
    }
    context.contentResolver.update(destUri, finalize, null, null)
}
```

- Mark legacy external files for deletion after successful migration and, ideally, explicit user confirmation.

### 3. Media Access

- For writes, use `MediaStore` with `RELATIVE_PATH` and `IS_PENDING` until write completion.
- For reading app-owned files in app-specific dirs no permissions are required; for shared media:
  - On Android 13+ use `READ_MEDIA_IMAGES` / `READ_MEDIA_VIDEO` / `READ_MEDIA_AUDIO`.
  - On Android 10–12 use `READ_EXTERNAL_STORAGE` (respecting scoped storage constraints).
- Avoid relying on raw file paths in shared media dirs; always use URIs.

### 4. Storage Access Framework

- Use `ACTION_OPEN_DOCUMENT` / `CREATE_DOCUMENT` / `ACTION_OPEN_DOCUMENT_TREE` only when you truly need access to user documents or arbitrary directories beyond app-specific storage/`MediaStore`.
- Persist URI permissions via `takePersistableUriPermission`.
- For create/read/delete operations use `DocumentFile` over obtained URIs; avoid absolute paths.

### 5. Backup/Export

- Control inclusion/exclusion in Auto Backup via `android:fullBackupContent`; use `noBackupFilesDir` for data that must not be backed up.
- Do not confuse device-protected storage with backup exclusion; it is for pre-unlock access.
- For user exports:
  - Create temporary copies in `cacheDir` or app-specific directories.
  - Encrypt exported data if needed.
  - Validate MIME type and size before sharing; use explicit `Intent` with proper `ClipData` and `FLAG_GRANT_READ_URI_PERMISSION`.
- Acknowledge ADB backup is deprecated; rely on Auto Backup / Key-Value backup and explicit export flows (SAF/sharing).

### 6. Permissions & Compliance

- Do not request `MANAGE_EXTERNAL_STORAGE` unless strictly necessary and compliant with Play policies.
- Update privacy policy and clearly explain migration impacts to users.
- Log migration (without sensitive data), implement fallbacks: on write failures to public dirs, save to private storage and notify user.
- Treat `requestLegacyExternalStorage=true` as a temporary Android 10 compatibility flag and plan its removal on Android 11+.

---

## Follow-ups (RU)
- Как поддерживать совместимость с desktop backup (ADB backup deprecated)?
- Как реализовать end-to-end шифрование пользовательских экспортов?
- Какие практики для синхронизации фото/видео с облаком при scoped storage?

## Follow-ups (EN)
- How to keep compatibility with desktop backup flows now that ADB backup is deprecated?
- How to implement end-to-end encryption for user exports?
- What are best practices for syncing photos/videos to the cloud under scoped storage?

## References (RU)

- [Data Storage](https://developer.android.com/training/data-storage)

## References (EN)

- [Data Storage](https://developer.android.com/training/data-storage)

## Related Questions

- [[q-android-storage-types--android--medium]]
