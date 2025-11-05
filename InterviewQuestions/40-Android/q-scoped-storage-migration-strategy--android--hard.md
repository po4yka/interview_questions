---
id: android-632
title: Scoped Storage Migration Strategy / Стратегия миграции на Scoped Storage
aliases:
  - Scoped Storage Migration Strategy
  - Стратегия миграции на Scoped Storage
topic: android
subtopics:
  - storage
  - security
  - privacy
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-scoped-storage-security
  - q-android-coverage-gaps--android--hard
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/storage
  - android/security
  - privacy
  - difficulty/hard
sources:
  - url: https://developer.android.com/training/data-storage
    note: Android storage guide
  - url: https://developer.android.com/about/versions/11/privacy/storage
    note: Scoped storage best practices
---

# Вопрос (RU)
> Как мигрировать legacy-приложение на scoped storage, сохранив данные пользователей, обеспечив приватность и совместимость с бэкапом/экспортом?

# Question (EN)
> How do you migrate a legacy app to scoped storage while preserving user data, maintaining privacy, and supporting backup/export workflows?

---

## Ответ (RU)

### 1. Аудит данных

- Категоризируйте файлы: app-private, shared media, документы пользователя.
- Определите, какие данные обязательны для экспортов/backup.
- Откажитесь от `WRITE_EXTERNAL_STORAGE`, используйте per-collection permissions.

### 2. Миграция

- На первый запуск после обновления:
  - Используйте `Storage Access Framework` (`ACTION_OPEN_DOCUMENT_TREE`) для пользовательских директорий.
  - Перенесите файлы в `context.getExternalFilesDir()` или `MediaStore`.

```kotlin
val projection = arrayOf(MediaStore.MediaColumns._ID, MediaStore.MediaColumns.RELATIVE_PATH)
val selection = "${MediaStore.MediaColumns.RELATIVE_PATH} LIKE ?"
val args = arrayOf("LegacyApp/%")

context.contentResolver.query(MediaStore.Files.getContentUri("external"), projection, selection, args, null)?.use { cursor ->
    while (cursor.moveToNext()) {
        // reinsert into scoped location
    }
}
```

- Помечайте старые файлы для удаления (после подтверждения пользователя).

### 3. Доступ к медиа

- Используйте `MediaStore` insert с `RELATIVE_PATH` и `IS_PENDING`.
- После записи выставляйте `IS_PENDING = 0`, чтобы файл стал доступен.
- Для чтения других файлов запросите `READ_MEDIA_*` (Android 13+).

### 4. Storage Access Framework

- Для пользовательских директорий создайте UI с `ACTION_OPEN_DOCUMENT` / `CREATE_DOCUMENT`.
- Сохраняйте `takePersistableUriPermission`.
- Используйте `DocumentFile` для операций (без прямых путей).

### 5. Backup/Export

- Exclude чувствительные файлы через `fullBackupContent` / `deviceProtected`.
- Для экспортов создавайте временные копии в `cacheDir`, шифруйте при необходимости.
- Проверяйте MIME и размер перед шарингом (`Intent.createChooser` with `ClipData`).

### 6. Permissions & Compliance

- Не используйте `MANAGE_EXTERNAL_STORAGE`, если нет строгих причин (policy risk).
- Обновите privacy policy, объясните пользователям переход.
- Логируйте поток миграции; fallback при ошибках (например, сохраните в private storage).

---

## Answer (EN)

- Audit legacy file usage, classify data, and drop `WRITE_EXTERNAL_STORAGE`.
- Migrate media into scoped directories and MediaStore collections, using `IS_PENDING` workflow.
- Prompt users for document tree access when necessary, persisting URI permissions and working via `DocumentFile`.
- Handle backups/exports with encrypted temporary copies and explicit MIME checks.
- Avoid broad storage permissions, update privacy policies, and ensure rollback paths if migration fails.

---

## Follow-ups
- Как поддерживать совместимость с desktop backup (ADB backup deprecated)?
- Как реализовать end-to-end шифрование пользовательских экспортов?
- Какие практики для синхронизации фото/видео с облаком при scoped storage?

## References

- [[c-scoped-storage-security]]
- [[q-android-coverage-gaps--android--hard]]
- [Data Storage](https://developer.android.com/training/data-storage)


## Related Questions

- [[c-scoped-storage-security]]
- [[q-android-coverage-gaps--android--hard]]
