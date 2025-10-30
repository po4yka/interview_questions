---
id: 20251020-200300
title: Encrypted File Storage / Зашифрованное хранение файлов
aliases: [Encrypted File Storage, Зашифрованное хранение файлов]
topic: android
subtopics: [files-media, permissions]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-keystore-system--security--medium, q-android-security-best-practices--android--medium, q-data-encryption-at-rest--android--medium]
created: 2025-10-20
updated: 2025-10-28
sources: [https://developer.android.com/topic/security/data]
tags: [android/files-media, android/permissions, android/security, difficulty/medium, encryption, file-storage, keystore]
date created: Tuesday, October 28th 2025, 9:23:47 am
date modified: Thursday, October 30th 2025, 12:47:43 pm
---

# Вопрос (RU)
> Как реализовать зашифрованное хранение файлов с использованием EncryptedFile API?

# Question (EN)
> How to implement encrypted file storage using EncryptedFile API?

---

## Ответ (RU)

EncryptedFile API из библиотеки Security Crypto обеспечивает прозрачное шифрование файлов с автоматическим управлением ключами через Android Keystore. Использует AES-256-GCM с HKDF для деривации ключей.

### Базовая реализация

```kotlin
class EncryptedFileManager(private val context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    // ✅ Правильно: используем use для автоматического закрытия потоков
    fun writeSecure(fileName: String, content: String) {
        val file = File(context.filesDir, fileName)
        val encryptedFile = EncryptedFile.Builder(
            context, file, masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()

        encryptedFile.openFileOutput().use {
            it.write(content.toByteArray(Charsets.UTF_8))
        }
    }

    fun readSecure(fileName: String): String {
        val file = File(context.filesDir, fileName)
        val encryptedFile = EncryptedFile.Builder(
            context, file, masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()

        return encryptedFile.openFileInput().use {
            it.readBytes().toString(Charsets.UTF_8)
        }
    }
}
```

### Streaming для больших файлов

```kotlin
// ✅ Правильно: 8KB буфер оптимален для большинства случаев
fun copyEncrypted(source: InputStream, fileName: String) {
    val file = File(context.filesDir, fileName)
    val encryptedFile = buildEncryptedFile(file)

    encryptedFile.openFileOutput().use { output ->
        source.copyTo(output, bufferSize = 8192)
    }
}

// ❌ Неправильно: загрузка всего файла в память
fun copyWrong(source: InputStream, fileName: String) {
    val allBytes = source.readBytes() // OOM для больших файлов
    writeSecure(fileName, String(allBytes))
}
```

### Ключевые концепции

**AES-256-GCM:**
- Authenticated encryption: одновременно шифрует и проверяет целостность
- 256-битный ключ, 96-битный IV
- GCM mode предотвращает tampering

**HKDF деривация:**
- Каждый файл получает уникальный ключ из master key
- Компрометация одного файла не раскрывает другие
- 4KB блоки позволяют streaming без загрузки всего файла

**Android Keystore:**
- Аппаратная защита ключей (TEE/Secure Element)
- Ключи никогда не экспортируются в память приложения
- Поддержка биометрической аутентификации

### Best practices

**Управление ключами:**
- Один MasterKey на приложение
- Избегать хранения ключей в SharedPreferences
- Биометрия для доступа к особо чувствительным файлам

**Производительность:**
- Streaming для файлов >1MB
- Асинхронные операции (Dispatchers.IO)
- 8KB буфер оптимален для большинства сценариев

**Безопасность:**
- Валидация путей файлов (path traversal)
- Обработка SecurityException
- Никогда не логировать plaintext содержимое

---

## Answer (EN)

EncryptedFile API from Security Crypto library provides transparent file encryption with automatic key management via Android Keystore. Uses AES-256-GCM with HKDF for key derivation.

### Basic implementation

```kotlin
class EncryptedFileManager(private val context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    // ✅ Correct: use for automatic stream closure
    fun writeSecure(fileName: String, content: String) {
        val file = File(context.filesDir, fileName)
        val encryptedFile = EncryptedFile.Builder(
            context, file, masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()

        encryptedFile.openFileOutput().use {
            it.write(content.toByteArray(Charsets.UTF_8))
        }
    }

    fun readSecure(fileName: String): String {
        val file = File(context.filesDir, fileName)
        val encryptedFile = EncryptedFile.Builder(
            context, file, masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()

        return encryptedFile.openFileInput().use {
            it.readBytes().toString(Charsets.UTF_8)
        }
    }
}
```

### Streaming for large files

```kotlin
// ✅ Correct: 8KB buffer optimal for most cases
fun copyEncrypted(source: InputStream, fileName: String) {
    val file = File(context.filesDir, fileName)
    val encryptedFile = buildEncryptedFile(file)

    encryptedFile.openFileOutput().use { output ->
        source.copyTo(output, bufferSize = 8192)
    }
}

// ❌ Wrong: loading entire file into memory
fun copyWrong(source: InputStream, fileName: String) {
    val allBytes = source.readBytes() // OOM for large files
    writeSecure(fileName, String(allBytes))
}
```

### Key concepts

**AES-256-GCM:**
- Authenticated encryption: encrypts and verifies integrity simultaneously
- 256-bit key, 96-bit IV
- GCM mode prevents tampering

**HKDF derivation:**
- Each file gets unique key derived from master key
- Compromising one file doesn't reveal others
- 4KB blocks enable streaming without loading entire file

**Android Keystore:**
- Hardware-backed key protection (TEE/Secure Element)
- Keys never exported to app memory
- Biometric authentication support

### Best practices

**Key management:**
- Single MasterKey per application
- Avoid storing keys in SharedPreferences
- Biometrics for access to highly sensitive files

**Performance:**
- Streaming for files >1MB
- Async operations (Dispatchers.IO)
- 8KB buffer optimal for most scenarios

**Security:**
- Validate file paths (path traversal)
- Handle SecurityException
- Never log plaintext content

---

## Follow-ups

- How to implement biometric authentication with EncryptedFile?
- When to use AES256_GCM_HKDF_4KB vs AES256_GCM_HKDF_1MB schemes?
- How to handle key rotation for encrypted files?
- What happens to encrypted files after app reinstall?
- How to securely delete encrypted files?

## References

- Android Security Crypto library documentation
- Android Keystore system architecture
- AES-GCM authenticated encryption mode

## Related Questions

### Prerequisites
- Basic file I/O in Android (internal/external storage)
- Android permissions model

### Related
- [[q-android-keystore-system--security--medium]] - Key storage fundamentals
- [[q-android-security-best-practices--android--medium]] - Security patterns
- [[q-data-encryption-at-rest--android--medium]] - Encryption strategies

### Advanced
- Key rotation strategies for encrypted data
- Biometric authentication integration with secure storage
