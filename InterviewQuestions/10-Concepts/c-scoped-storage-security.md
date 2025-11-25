---
id: ivc-20251102-019
title: Scoped Storage Security / Безопасность Scoped Storage
aliases: [Android Storage Isolation, Scoped Storage Security]
kind: concept
summary: Advanced scoped storage patterns covering SAF, MediaStore, app-private files, and data migrations with privacy constraints
links: []
created: 2025-11-02
updated: 2025-11-02
tags: [android, concept, privacy, security, storage]
date created: Thursday, November 6th 2025, 4:39:51 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

Scoped storage enforces per-app sandboxes, rich MediaStore APIs, and Storage Access Framework for user-granted access. Secure implementations must handle migration from legacy `WRITE_EXTERNAL_STORAGE`, manage backups, and protect sensitive exports.

# Сводка (RU)

Scoped storage обеспечивает песочницу для приложений, расширенный MediaStore API и Storage Access Framework для доступа, предоставленного пользователем. Безопасная реализация включает миграцию с `WRITE_EXTERNAL_STORAGE`, управление резервным копированием и защиту чувствительных экспортов.

## Key Topics

- `Context.getExternalFilesDir`, `MediaStore` scoped inserts, pending publish workflow
- Storage Access Framework (`ACTION_OPEN_DOCUMENT`) + persistable URI permissions
- App-specific directories vs shared collections
- Data migration and clean-up strategies
- Backup exclusions, encryption, redaction

## Considerations

- Ограничения `MANAGE_EXTERNAL_STORAGE` (только для определённых случаев).
- Проверка пользовательских URI (не доверять путям, validate MIME).
- Удаление/анонимизация данных при logout (privacy-by-design).
