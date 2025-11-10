---
id: android-458
title: Encrypted File Storage / Зашифрованное хранение файлов
aliases:
- Encrypted File Storage
- Зашифрованное хранение файлов
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
status: draft
moc: moc-android
related:
- c-permissions
- c-scoped-storage-security
- q-data-encryption-at-rest--android--medium
created: 2025-10-20
updated: 2025-11-10
tags:
- android/files-media
- android/permissions
- android/security
- difficulty/medium
- encryption
- file-storage
- keystore
- security
sources:
- "https://developer.android.com/topic/security/data"
---

# Вопрос (RU)
> Как реализовать зашифрованное хранение файлов с использованием EncryptedFile API?

# Question (EN)
> How to implement encrypted file storage using EncryptedFile API?

---

## Ответ (RU)

`EncryptedFile` API из библиотеки `androidx.security:security-crypto` обеспечивает прозрачное шифрование файлов с автоматическим управлением ключами через Android Keystore. Использует `AES-256-GCM` с `HKDF` для деривации ключей. Критично для защиты чувствительных данных от несанкционированного доступа.

### Базовая Реализация

`EncryptedFile` работает поверх обычных `File` операций. `MasterKey` хранится в Android Keystore (часто с аппаратной защитой через TEE/Secure Element, если доступно на устройстве). Для каждого файла из `MasterKey` выводится отдельный ключ через `HKDF`, обеспечивая изоляцию данных.

```kotlin
class EncryptedFileManager(private val context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    fun writeSecure(fileName: String, content: String) {
        val encryptedFile = EncryptedFile.Builder(
            context, File(context.filesDir, fileName), masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()
        encryptedFile.openFileOutput().use {
            it.write(content.toByteArray(Charsets.UTF_8))
        }
    }

    fun readSecure(fileName: String): Result<String> = try {
        val encryptedFile = EncryptedFile.Builder(
            context, File(context.filesDir, fileName), masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()
        Result.success(encryptedFile.openFileInput().use {
            it.readBytes().toString(Charsets.UTF_8)
        })
    } catch (e: SecurityException) {
        Result.failure(Exception("Decryption failed", e))
    }
}
```

### Streaming Для Больших Файлов

Для больших файлов используйте streaming во избежание `OutOfMemoryError`:

```kotlin
suspend fun copyEncrypted(source: InputStream, fileName: String) = withContext(Dispatchers.IO) {
    val encryptedFile = EncryptedFile.Builder(
        context, File(context.filesDir, fileName), masterKey,
        EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
    ).build()
    encryptedFile.openFileOutput().use { source.copyTo(it, bufferSize = 8192) }
}
```

> Примечание: выбор между `AES256_GCM_HKDF_4KB` и `AES256_GCM_HKDF_1MB` влияет на накладные расходы и производительность (размер зашифрованных блоков), а не задает жесткие пороги размера файлов. Обычно 4KB подходит для большинства сценариев; 1MB может быть выгоден для очень больших последовательных файлов.

### Ключевые Концепции

**AES-256-GCM**: Режим аутентифицированного шифрования (256-битный ключ, 96-битный IV). Одновременно шифрует и обеспечивает контроль целостности данных. При корректном использовании GCM позволяет обнаруживать попытки модификации шифртекста.

**HKDF**: Создает уникальный ключ для каждого файла из `MasterKey`. Компрометация одного файла не раскрывает другие.

**Android Keystore**: Предоставляет аппаратно- или программно-защищенное хранение ключей. Ключи, созданные как неэкспортируемые, не могут быть извлечены из Keystore в виде сырого ключевого материала; операции шифрования/расшифрования выполняются через Keystore API. Поддерживается привязка ключей к аутентификации пользователя (PIN/биометрия) на уровне политики.

```kotlin
// MasterKey с требованием аутентификации пользователя (пример: доступ к данным только после разблокировки)
val biometricKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .setUserAuthenticationRequired(true)
    .setUserAuthenticationValidityDurationSeconds(300)
    .build()
```

> Важно: использование `setUserAuthenticationRequired(true)` для ключа, применяемого с `EncryptedFile`, означает, что при истечении окна аутентификации операции расшифрования могут завершаться ошибкой, что нужно явно обрабатывать в UX/обработке ошибок.

### Лучшие Практики

- Один `MasterKey` на приложение (кэшировать, не пересоздавать при каждом вызове)
- Использовать streaming и `Dispatchers.IO` для работы с большими файлами
- Валидировать имена и пути файлов (защита от path traversal)
- Обрабатывать `SecurityException` и связанные ошибки при шифровании/дешифровании
- Понимать, что гарантированно "безопасное удаление" на flash/FS уровне не обеспечивается; при необходимости минимизировать экспозицию (использовать внутреннее хранилище, шифрование по умолчанию, не создавать незашифрованных копий)

---

## Answer (EN)

`EncryptedFile` API from `androidx.security:security-crypto` provides transparent file encryption with automatic key management via Android Keystore. It uses `AES-256-GCM` with `HKDF` for key derivation and is critical for protecting sensitive data from unauthorized access.

### Basic Implementation

`EncryptedFile` works on top of regular `File` operations. `MasterKey` is stored in Android Keystore (often hardware-backed via TEE/Secure Element when available). For each file, a distinct key is derived from the `MasterKey` using `HKDF`, ensuring data isolation.

```kotlin
class EncryptedFileManager(private val context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    fun writeSecure(fileName: String, content: String) {
        val encryptedFile = EncryptedFile.Builder(
            context, File(context.filesDir, fileName), masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()
        encryptedFile.openFileOutput().use {
            it.write(content.toByteArray(Charsets.UTF_8))
        }
    }

    fun readSecure(fileName: String): Result<String> = try {
        val encryptedFile = EncryptedFile.Builder(
            context, File(context.filesDir, fileName), masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()
        Result.success(encryptedFile.openFileInput().use {
            it.readBytes().toString(Charsets.UTF_8)
        })
    } catch (e: SecurityException) {
        Result.failure(Exception("Decryption failed", e))
    }
}
```

### Streaming for Large Files

For large files use streaming to avoid `OutOfMemoryError`:

```kotlin
suspend fun copyEncrypted(source: InputStream, fileName: String) = withContext(Dispatchers.IO) {
    val encryptedFile = EncryptedFile.Builder(
        context, File(context.filesDir, fileName), masterKey,
        EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
    ).build()
    encryptedFile.openFileOutput().use { source.copyTo(it, bufferSize = 8192) }
}
```

> Note: choosing between `AES256_GCM_HKDF_4KB` and `AES256_GCM_HKDF_1MB` affects overhead and performance characteristics (encrypted chunk size), not strict file size thresholds. Typically 4KB is fine for most cases; 1MB may be beneficial for very large sequential files.

### Key Concepts

**AES-256-GCM**: Authenticated encryption mode (256-bit key, 96-bit IV). Encrypts and verifies integrity simultaneously. When used correctly, GCM allows detection of ciphertext tampering.

**HKDF**: Derives a unique key for each file from the `MasterKey`. Compromising one file does not reveal others.

**Android Keystore**: Provides hardware- or software-backed key protection. Keys created as non-exportable cannot be retrieved as raw key material; cryptographic operations are performed via Keystore APIs. It supports binding keys to user authentication policies (PIN/biometrics).

```kotlin
// MasterKey with user authentication requirement (e.g., restrict access to data until user authenticates)
val biometricKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .setUserAuthenticationRequired(true)
    .setUserAuthenticationValidityDurationSeconds(300)
    .build()
```

> Important: using `setUserAuthenticationRequired(true)` for a key employed with `EncryptedFile` means that once the auth window expires, decryption may fail until the user re-authenticates; this must be handled explicitly in UX/error handling.

### Best Practices

- Use a single `MasterKey` per application (cache it, avoid recreating unnecessarily)
- Use streaming and `Dispatchers.IO` for large-file operations
- Validate file names and paths (protect against path traversal)
- Handle `SecurityException` and related errors during encryption/decryption
- Understand that truly secure deletion on flash/FS is not guaranteed; minimize exposure (use internal storage, encryption by default, avoid unencrypted temp copies)

---

## Дополнительные вопросы (RU)

- Как работает `AES-256-GCM` и в чем его преимущества перед другими режимами шифрования?
- Что такое `HKDF` и как происходит деривация ключей для каждого файла?
- Как реализовать биометрическую аутентификацию с `EncryptedFile`?
- Когда использовать схемы `AES256_GCM_HKDF_4KB` vs `AES256_GCM_HKDF_1MB`?
- Как обрабатывать key rotation для зашифрованных файлов?

## Follow-ups (EN)

- How does `AES-256-GCM` work and what are its advantages over other encryption modes?
- What is `HKDF` and how does key derivation work for each file?
- How to implement biometric authentication with `EncryptedFile`?
- When to use `AES256_GCM_HKDF_4KB` vs `AES256_GCM_HKDF_1MB` schemes?
- How to handle key rotation for encrypted files?

## References

- [Android Security Crypto Library](https://developer.android.com/topic/security/data)
- [Android Keystore System](https://developer.android.com/training/articles/keystore)

## Related Questions

### Prerequisites / Concepts

- [[c-permissions]]
- [[c-scoped-storage-security]]

### Prerequisites (Easier)
- Basic file I/O in Android
- Android Keystore basics

### Related (Same Level)
- [[q-data-encryption-at-rest--android--medium]]

### Advanced (Harder)
- Key rotation strategies for encrypted data
- Biometric authentication integration with secure storage
