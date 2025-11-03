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
status: reviewed
moc: moc-android
related:
  - q-data-encryption-at-rest--android--medium
created: 2025-10-20
updated: 2025-11-02
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
  - https://developer.android.com/topic/security/data
---

# Вопрос (RU)
> Как реализовать зашифрованное хранение файлов с использованием EncryptedFile API?

# Question (EN)
> How to implement encrypted file storage using EncryptedFile API?

---

## Ответ (RU)

`EncryptedFile` API из библиотеки Security Crypto обеспечивает прозрачное шифрование файлов с автоматическим управлением ключами через Android Keystore. Использует `AES-256-GCM` с `HKDF` для деривации ключей. Критично для защиты чувствительных данных от несанкционированного доступа.

### Базовая Реализация

`EncryptedFile` работает поверх обычных `File` операций. `MasterKey` хранится в Android Keystore (аппаратная защита через TEE/Secure Element). Каждый файл получает уникальный ключ через `HKDF`, обеспечивая изоляцию данных.

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

### Streaming для Больших Файлов

Для файлов >1MB используйте streaming во избежание `OutOfMemoryError`:

```kotlin
suspend fun copyEncrypted(source: InputStream, fileName: String) = withContext(Dispatchers.IO) {
    val encryptedFile = EncryptedFile.Builder(
        context, File(context.filesDir, fileName), masterKey,
        EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
    ).build()
    encryptedFile.openFileOutput().use { source.copyTo(it, bufferSize = 8192) }
}
```

### Ключевые Концепции

**AES-256-GCM**: Authenticated encryption (256-bit ключ, 96-bit IV). Одновременно шифрует и проверяет целостность данных. GCM mode предотвращает tampering.

**HKDF**: Создает уникальный ключ для каждого файла из `MasterKey`. Компрометация одного файла не раскрывает другие. `AES256_GCM_HKDF_4KB` для файлов <1MB, `AES256_GCM_HKDF_1MB` для больших (>10MB).

**Android Keystore**: Аппаратная защита ключей (TEE/Secure Element). Ключи не экспортируются в память приложения. Поддержка биометрической аутентификации.

```kotlin
// MasterKey с биометрией
val biometricKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .setUserAuthenticationRequired(true)
    .setUserAuthenticationValidityDurationSeconds(300)
    .build()
```

### Лучшие Практики

- Один `MasterKey` на приложение (кэшировать, не пересоздавать)
- Streaming для файлов >1MB, асинхронные операции на `Dispatchers.IO`
- Валидация путей файлов (защита от path traversal)
- Обработка `SecurityException` при шифровании/дешифровании
- Безопасное удаление: перезапись файлов случайными данными перед удалением

---

## Answer (EN)

`EncryptedFile` API from Security Crypto library provides transparent file encryption with automatic key management via Android Keystore. Uses `AES-256-GCM` with `HKDF` for key derivation. Critical for protecting sensitive data from unauthorized access.

### Basic Implementation

`EncryptedFile` works on top of regular `File` operations. `MasterKey` stored in Android Keystore (hardware-protected via TEE/Secure Element). Each file gets unique key through `HKDF`, ensuring data isolation.

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

For files >1MB use streaming to avoid `OutOfMemoryError`:

```kotlin
suspend fun copyEncrypted(source: InputStream, fileName: String) = withContext(Dispatchers.IO) {
    val encryptedFile = EncryptedFile.Builder(
        context, File(context.filesDir, fileName), masterKey,
        EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
    ).build()
    encryptedFile.openFileOutput().use { source.copyTo(it, bufferSize = 8192) }
}
```

### Key Concepts

**AES-256-GCM**: Authenticated encryption (256-bit key, 96-bit IV). Simultaneously encrypts and verifies data integrity. GCM mode prevents tampering.

**HKDF**: Creates unique key for each file from `MasterKey`. Compromising one file doesn't reveal others. `AES256_GCM_HKDF_4KB` for files <1MB, `AES256_GCM_HKDF_1MB` for large (>10MB).

**Android Keystore**: Hardware-backed key protection (TEE/Secure Element). Keys never exported to application memory. Biometric authentication support.

```kotlin
// MasterKey with biometrics
val biometricKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .setUserAuthenticationRequired(true)
    .setUserAuthenticationValidityDurationSeconds(300)
    .build()
```

### Best Practices

- Single `MasterKey` per application (cache, don't recreate)
- Streaming for files >1MB, async operations on `Dispatchers.IO`
- Validate file paths (protection against path traversal)
- Handle `SecurityException` during encryption/decryption
- Secure deletion: overwrite files with random data before deletion

---

## Follow-ups

- Как работает `AES-256-GCM` и в чем его преимущества перед другими режимами шифрования?
- Что такое `HKDF` и как происходит деривация ключей для каждого файла?
- Как реализовать биометрическую аутентификацию с `EncryptedFile`?
- Когда использовать `AES256_GCM_HKDF_4KB` vs `AES256_GCM_HKDF_1MB` схемы?
- Как обрабатывать key rotation для зашифрованных файлов?
- Что происходит с зашифрованными файлами после переустановки приложения?
- How does `AES-256-GCM` work and what are its advantages over other encryption modes?
- What is `HKDF` and how does key derivation work for each file?
- How to implement biometric authentication with `EncryptedFile`?
- When to use `AES256_GCM_HKDF_4KB` vs `AES256_GCM_HKDF_1MB` schemes?

## References

- [Android Security Crypto Library](https://developer.android.com/topic/security/data)
- [Android Keystore System](https://developer.android.com/training/articles/keystore)

## Related Questions

### Prerequisites (Easier)
- Basic file I/O in Android
- Android Keystore basics

### Related (Same Level)
- [[q-data-encryption-at-rest--android--medium]]

### Advanced (Harder)
- Key rotation strategies for encrypted data
- Biometric authentication integration with secure storage
