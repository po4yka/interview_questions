---
id: android-458
title: Encrypted File Storage / Зашифрованное хранение файлов
aliases: [Encrypted File Storage, Зашифрованное хранение файлов]
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
  - q-api-file-upload-server--android--medium
  - q-data-encryption-at-rest--android--medium
  - q-how-to-display-svg-string-as-a-vector-file--android--medium
  - q-large-file-upload--android--medium
created: 2025-10-20
updated: 2025-11-10
tags: [android/files-media, android/permissions, android/security, difficulty/medium, encryption, file-storage, keystore, security]
sources:
  - "https://developer.android.com/topic/security/data"
date created: Saturday, November 1st 2025, 12:46:49 pm
date modified: Tuesday, November 25th 2025, 8:54:01 pm
---
# Вопрос (RU)
> Как реализовать зашифрованное хранение файлов с использованием EncryptedFile API?

# Question (EN)
> How to implement encrypted file storage using EncryptedFile API?

---

## Ответ (RU)

`EncryptedFile` API из библиотеки `androidx.security:security-crypto` обеспечивает прозрачное шифрование файлов с автоматическим управлением ключами через Android Keystore. Использует `AES-256-GCM` с `HKDF` для построения схемы шифрования поверх файлов. Это критично для защиты чувствительных данных от несанкционированного доступа.

### Базовая Реализация

`EncryptedFile` работает поверх обычных операций с `File`. `MasterKey` хранится в Android Keystore (часто с аппаратной защитой через TEE/Secure Element, если доступно на устройстве). Для каждого зашифрованного файла библиотека применяет схему, основанную на `HKDF` и блочном шифровании, что обеспечивает изоляцию данных между файлами (компрометация одного файла не должна автоматически раскрывать другие).

```kotlin
class EncryptedFileManager(private val context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    fun writeSecure(fileName: String, content: String) {
        val encryptedFile = EncryptedFile.Builder(
            context,
            File(context.filesDir, fileName),
            masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()
        encryptedFile.openFileOutput().use {
            it.write(content.toByteArray(Charsets.UTF_8))
        }
    }

    fun readSecure(fileName: String): Result<String> = try {
        val encryptedFile = EncryptedFile.Builder(
            context,
            File(context.filesDir, fileName),
            masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()
        Result.success(
            encryptedFile.openFileInput().use {
                it.readBytes().toString(Charsets.UTF_8)
            }
        )
    } catch (e: Exception) { // Включает SecurityException, IOException и др.
        Result.failure(Exception("Decryption or read failed", e))
    }
}
```

> Примечание: `EncryptedFile` самостоятельно управляет IV/nonce и тегами аутентификации для `AES-GCM`; разработчику не нужно (и нельзя) переиспользовать их вручную.

### Streaming Для Больших Файлов

Для больших файлов используйте streaming во избежание `OutOfMemoryError`:

```kotlin
suspend fun copyEncrypted(source: InputStream, fileName: String) = withContext(Dispatchers.IO) {
    val encryptedFile = EncryptedFile.Builder(
        context,
        File(context.filesDir, fileName),
        masterKey,
        EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
    ).build()
    encryptedFile.openFileOutput().use { output ->
        source.copyTo(output, bufferSize = 8192)
    }
}
```

> Примечание: выбор между `AES256_GCM_HKDF_4KB` и `AES256_GCM_HKDF_1MB` влияет на накладные расходы и производительность (размер зашифрованных блоков), а не задает жесткие пороги размера файлов. Обычно 4KB подходит для большинства сценариев; 1MB может быть выгоден для очень больших последовательных файлов.

### Ключевые Концепции

**AES-256-GCM**: Режим аутентифицированного шифрования (256-битный ключ, типично 96-битный IV). Одновременно шифрует и обеспечивает контроль целостности данных. При корректном использовании GCM позволяет обнаруживать попытки модификации шифртекста.

**HKDF**: Криптографическая функция деривации ключей, используемая библиотекой для получения производных ключевых материалов. Схема на основе HKDF позволяет разделять криптографический контекст между файлами/блоками, чтобы компрометация одного не приводила к компрометации остальных.

**Android Keystore**: Предоставляет аппаратно- или программно-защищенное хранение ключей. Ключи, созданные как неэкспортируемые, не могут быть извлечены из Keystore в виде сырого ключевого материала; операции шифрования/расшифрования выполняются через Keystore API. Поддерживается привязка ключей к аутентификации пользователя (PIN/биометрия) на уровне параметров генерации ключей.

```kotlin
// Пример схемы: MasterKey, потенциально связанный с аутентификацией пользователя.
// Важно: конкретные флаги аутентификации настраиваются через KeyGenParameterSpec
// при кастомной генерации ключей, а не напрямую через MasterKey.Builder.
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()
```

> Важно: для сценариев, где доступ к данным должен зависеть от аутентификации пользователя (например, биометрия), применяйте пользовательские параметры Keystore (KeyGenParameterSpec) или Jetpack Biometric для gating-доступа, и учитывайте, что после истечения окна аутентификации операции расшифрования могут завершаться ошибкой — это нужно явно обрабатывать в UX/обработке ошибок.

### Лучшие Практики

- Один `MasterKey` на приложение (кэшировать, не пересоздавать при каждом вызове)
- Использовать streaming и `Dispatchers.IO` для работы с большими файлами
- Валидировать имена и пути файлов (защита от path traversal)
- Обрабатывать `SecurityException`, `IOException` и другие ошибки при шифровании/дешифровании
- Понимать, что гарантированно "безопасное удаление" на уровне flash/ФС не обеспечивается; при необходимости минимизировать экспозицию (использовать внутреннее хранилище, шифрование по умолчанию, не создавать незашифрованных копий)

---

## Answer (EN)

`EncryptedFile` API from `androidx.security:security-crypto` provides transparent file encryption with automatic key management via Android Keystore. It uses `AES-256-GCM` with `HKDF` as part of its encryption scheme over files and is critical for protecting sensitive data from unauthorized access.

### Basic Implementation

`EncryptedFile` operates on top of regular `File` APIs. `MasterKey` is stored in Android Keystore (often hardware-backed via TEE/Secure Element when available). For each encrypted file, the library applies an HKDF-based and chunk-based scheme that isolates data across files/segments (compromise of one file should not automatically expose others).

```kotlin
class EncryptedFileManager(private val context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    fun writeSecure(fileName: String, content: String) {
        val encryptedFile = EncryptedFile.Builder(
            context,
            File(context.filesDir, fileName),
            masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()
        encryptedFile.openFileOutput().use {
            it.write(content.toByteArray(Charsets.UTF_8))
        }
    }

    fun readSecure(fileName: String): Result<String> = try {
        val encryptedFile = EncryptedFile.Builder(
            context,
            File(context.filesDir, fileName),
            masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()
        Result.success(
            encryptedFile.openFileInput().use {
                it.readBytes().toString(Charsets.UTF_8)
            }
        )
    } catch (e: Exception) { // Includes SecurityException, IOException, etc.
        Result.failure(Exception("Decryption or read failed", e))
    }
}
```

> Note: `EncryptedFile` manages IV/nonces and authentication tags for `AES-GCM` internally; developers should not attempt to reuse or manage them manually.

### Streaming for Large Files

For large files, use streaming to avoid `OutOfMemoryError`:

```kotlin
suspend fun copyEncrypted(source: InputStream, fileName: String) = withContext(Dispatchers.IO) {
    val encryptedFile = EncryptedFile.Builder(
        context,
        File(context.filesDir, fileName),
        masterKey,
        EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
    ).build()
    encryptedFile.openFileOutput().use { output ->
        source.copyTo(output, bufferSize = 8192)
    }
}
```

> Note: choosing between `AES256_GCM_HKDF_4KB` and `AES256_GCM_HKDF_1MB` affects overhead and performance characteristics (encrypted chunk size), not strict file size thresholds. Typically 4KB is fine for most scenarios; 1MB may be beneficial for very large sequential files.

### Key Concepts

**AES-256-GCM**: Authenticated encryption mode (256-bit key, typically 96-bit IV). Provides both confidentiality and integrity. When used correctly, GCM allows detection of ciphertext tampering.

**HKDF**: A cryptographic key derivation function used by the library to derive related key material. An HKDF-based scheme helps separate cryptographic context between files/blocks so that compromise of one does not trivially compromise others.

**Android Keystore**: Provides hardware- or software-backed protection for keys. Non-exportable keys cannot be retrieved as raw key material; cryptographic operations are performed via Keystore APIs. Binding keys to user-auth policies (PIN/biometric) is configured at key generation time.

```kotlin
// Example: MasterKey that can be configured with secure defaults.
// Note: detailed user-auth binding is done via KeyGenParameterSpec when generating
// custom keys, not via non-existent setters on MasterKey.Builder.
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()
```

> Important: for scenarios where file access must depend on user authentication (e.g., biometrics), use appropriate Keystore key parameters (KeyGenParameterSpec) and/or Jetpack Biometric to gate access. Once the auth timeout is exceeded, decryption operations may fail until the user re-authenticates; UX and error handling must account for this.

### Best Practices

- Use a single `MasterKey` per application (cache it, avoid recreating on every call)
- Use streaming and `Dispatchers.IO` for large-file operations
- Validate file names and paths (protect against path traversal)
- Handle `SecurityException`, `IOException`, and other failures during encryption/decryption
- Understand that guaranteed secure deletion on flash/FS is not assured; minimize exposure (use internal storage, default encryption, avoid unencrypted temporary copies)

---

## Дополнительные Вопросы (RU)

- Как работает `AES-256-GCM` и в чем его преимущества перед другими режимами шифрования?
- Что такое `HKDF` и как схема EncryptedFile изолирует данные для разных файлов?
- Как реализовать биометрическую аутентификацию и/или привязку ключей в Keystore для работы с `EncryptedFile`?
- Когда использовать схемы `AES256_GCM_HKDF_4KB` vs `AES256_GCM_HKDF_1MB`?
- Как обрабатывать key rotation для зашифрованных файлов?

## Follow-ups (EN)

- How does `AES-256-GCM` work and what are its advantages over other encryption modes?
- What is `HKDF` and how does EncryptedFile's scheme isolate data across files?
- How to implement biometric authentication and/or Keystore-bound keys for use with `EncryptedFile`?
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
