---
id: "20251110-130945"
title: "Scoped Storage / Scoped Storage"
aliases: ["Scoped Storage"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: [c-android-storage-options, c-permissions, c-content-provider, c-datastore, c-security]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
date created: Monday, November 10th 2025, 8:37:44 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

Scoped Storage is a data access model that restricts how apps read and write files on a device by confining them to app-specific directories and controlled, permissioned entry points. It is most commonly associated with Android (Android 10+), where it was introduced to improve user privacy, security, and predictable storage behavior. Instead of broad file system access, apps must use well-defined APIs (e.g., MediaStore, SAF, app-specific directories) to interact with shared media and documents.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Scoped Storage — это модель доступа к данным, ограничивающая чтение и запись файлов приложением его собственными директориями и контролируемыми точками доступа. Наиболее известна по Android (начиная с Android 10), где она введена для усиления приватности, безопасности и предсказуемого поведения хранилища. Вместо широкого доступа к файловой системе приложения используют специализированные API (например, MediaStore, SAF и app-specific директории) для работы с общими медиа и документами.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Restricted file access: Apps lose unrestricted access to external storage; by default they can fully access only their own app-specific directories.
- Privacy and security: Limits the risk of leaking or tampering with other apps’ files and user data by enforcing scoped, permission-based access.
- Standardized APIs: Access to shared media (images, video, audio) and documents goes through system APIs like MediaStore or the Storage Access Framework instead of raw file paths.
- Backward compatibility and migration: Requires handling legacy storage behavior on older Android versions and migrating existing file access code paths when targeting newer SDKs.
- User control: Users gain finer-grained control over what each app can see or modify, often at the media/category level rather than granting blanket storage permissions.

## Ключевые Моменты (RU)

- Ограниченный доступ к файлам: Приложения теряют неограниченный доступ к внешнему хранилищу и по умолчанию полноценно работают только со своими app-specific директориями.
- Приватность и безопасность: Уменьшает риск утечек и подмены данных других приложений, так как доступ к хранилищу становится scoped и основан на разрешениях.
- Стандартизированные API: Доступ к общим медиа (изображения, видео, аудио) и документам осуществляется через системные API, такие как MediaStore и Storage Access Framework, вместо прямой работы с путями файлов.
- Обратная совместимость и миграция: Требует учитывать старое поведение хранилища на более ранних версиях Android и мигрировать существующий код работы с файлами при выборе новых уровней SDK.
- Контроль пользователя: Пользователь получает более точечный контроль над тем, какие данные и категории медиа может просматривать или изменять конкретное приложение, вместо общего доступа ко всему хранилищу.

## References

- Android Developers: https://developer.android.com/training/data-storage/shared/media
- Android Developers (Scoped Storage overview): https://developer.android.com/about/versions/10/privacy/changes#scoped-storage
