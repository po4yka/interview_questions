---
id: 20251020-200300
title: Encrypted File Storage / Зашифрованное хранение файлов
aliases:
- Encrypted File Storage
- Зашифрованное хранение файлов
topic: android
subtopics:
- files-media
- security
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
source: https://developer.android.com/topic/security/data
source_note: Android encrypted file storage documentation
status: reviewed
moc: moc-android
related:
- q-data-encryption-at-rest--security--medium
- q-android-keystore--security--medium
- q-android-security-best-practices--security--medium
created: 2025-10-20
updated: 2025-10-20
tags:
- android/files-media
- android/security
- encryption
- file-storage
- keystore
- difficulty/medium
---# Вопрос (RU)
> Как реализовать зашифрованное хранение файлов с использованием EncryptedFile API?

# Question (EN)
> How to implement encrypted file storage using EncryptedFile API?

---

## Ответ (RU)

EncryptedFile API из Android Security Crypto библиотеки обеспечивает безопасное шифрование файлов с автоматическим управлением ключами через Android Keystore. Использует AES-256-GCM с поддержкой streaming для больших файлов.

### Основные концепции

**EncryptedFile возможности:**
- Автоматическое управление ключами (Android Keystore)
- Streaming шифрование для больших файлов
- AES-256-GCM с аутентификацией
- Обнаружение изменений файлов
- Простой API

**Гарантии безопасности:**
- Конфиденциальность: AES-256 шифрование
- Целостность: GCM authentication tag
- Безопасность ключей: Android Keystore
- Forward secrecy: уникальное шифрование для каждой операции

### Реализация

**1. Базовая настройка**
```kotlin
class EncryptedFileManager(private val context: Context) {
    private val masterKey: MasterKey by lazy {
        MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
    }

    fun getEncryptedFile(fileName: String): EncryptedFile {
        val file = File(context.filesDir, fileName)
        return EncryptedFile.Builder(context, file, masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB)
            .build()
    }
}
```

**2. Запись и чтение**
```kotlin
// Запись текста
fun writeText(fileName: String, content: String) {
    val encryptedFile = getEncryptedFile(fileName)
    encryptedFile.openFileOutput().use { outputStream ->
        outputStream.write(content.toByteArray(Charsets.UTF_8))
    }
}

// Чтение текста
fun readText(fileName: String): String {
    val encryptedFile = getEncryptedFile(fileName)
    return encryptedFile.openFileInput().use { inputStream ->
        inputStream.readBytes().toString(Charsets.UTF_8)
    }
}
```

**3. Streaming для больших файлов**
```kotlin
// Запись больших файлов
fun writeLargeFile(fileName: String, inputStream: InputStream) {
    val encryptedFile = getEncryptedFile(fileName)
    encryptedFile.openFileOutput().use { output ->
        inputStream.copyTo(output, bufferSize = 8192)
    }
}

// Чтение больших файлов
fun readLargeFile(fileName: String, outputStream: OutputStream) {
    val encryptedFile = getEncryptedFile(fileName)
    encryptedFile.openFileInput().use { input ->
        input.copyTo(outputStream, bufferSize = 8192)
    }
}
```

**4. Обработка ошибок**
```kotlin
fun safeWriteText(fileName: String, content: String): Result<String> {
    return try {
        writeText(fileName, content)
        Result.success("File written successfully")
    } catch (e: Exception) {
        Result.failure(e)
    }
}
```

### Теория шифрования

**AES-256-GCM:**
- Advanced Encryption Standard с 256-битным ключом
- Galois/Counter Mode для аутентификации
- Обеспечивает конфиденциальность и целостность
- Поддерживает streaming операции

**HKDF (HMAC-based Key Derivation Function):**
- Производство ключей из master key
- Уникальные ключи для каждого файла
- Forward secrecy при компрометации master key

**Android Keystore:**
- Аппаратная защита ключей (TEE/SE)
- Ключи не покидают устройство
- Защита от root и side-channel атак
- Биометрическая аутентификация для доступа

**File Encryption Scheme:**
- `AES256_GCM_HKDF_4KB`: 4KB блоки для streaming
- `AES256_GCM_HKDF_1MB`: 1MB блоки для больших файлов
- Автоматическое управление IV (Initialization Vector)

### Best Practices

**1. Управление ключами**
- Использовать один MasterKey для приложения
- Не хранить ключи в SharedPreferences
- Использовать биометрическую аутентификацию для чувствительных данных

**2. Производительность**
- Использовать streaming для файлов >1MB
- Буферизация для оптимизации I/O
- Асинхронные операции для UI

**3. Безопасность**
- Валидация входных данных
- Обработка исключений
- Логирование без чувствительных данных

**4. Тестирование**
- Unit тесты для криптографических операций
- Интеграционные тесты с реальными файлами
- Тестирование на разных версиях Android

### Альтернативы

**SQLCipher:**
- Шифрование SQLite баз данных
- Прозрачное шифрование
- Хорошо для структурированных данных

**Custom encryption:**
- Больше контроля над процессом
- Сложнее в реализации
- Выше риск ошибок

**Cloud encryption:**
- Шифрование на стороне сервера
- Зависимость от провайдера
- Меньше контроля над ключами

## Answer (EN)

EncryptedFile API from Android Security Crypto library provides secure file encryption with automatic key management via Android Keystore. Uses AES-256-GCM with streaming support for large files.

### Key Concepts

**EncryptedFile features:**
- Automatic key management (Android Keystore)
- Streaming encryption for large files
- AES-256-GCM with authentication
- File tampering detection
- Simple API

**Security guarantees:**
- Confidentiality: AES-256 encryption
- Integrity: GCM authentication tag
- Key security: Android Keystore
- Forward secrecy: unique encryption per operation

### Implementation

**1. Basic setup**
```kotlin
class EncryptedFileManager(private val context: Context) {
    private val masterKey: MasterKey by lazy {
        MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
    }

    fun getEncryptedFile(fileName: String): EncryptedFile {
        val file = File(context.filesDir, fileName)
        return EncryptedFile.Builder(context, file, masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB)
            .build()
    }
}
```

**2. Read and write**
```kotlin
// Write text
fun writeText(fileName: String, content: String) {
    val encryptedFile = getEncryptedFile(fileName)
    encryptedFile.openFileOutput().use { outputStream ->
        outputStream.write(content.toByteArray(Charsets.UTF_8))
    }
}

// Read text
fun readText(fileName: String): String {
    val encryptedFile = getEncryptedFile(fileName)
    return encryptedFile.openFileInput().use { inputStream ->
        inputStream.readBytes().toString(Charsets.UTF_8)
    }
}
```

**3. Streaming for large files**
```kotlin
// Write large files
fun writeLargeFile(fileName: String, inputStream: InputStream) {
    val encryptedFile = getEncryptedFile(fileName)
    encryptedFile.openFileOutput().use { output ->
        inputStream.copyTo(output, bufferSize = 8192)
    }
}

// Read large files
fun readLargeFile(fileName: String, outputStream: OutputStream) {
    val encryptedFile = getEncryptedFile(fileName)
    encryptedFile.openFileInput().use { input ->
        input.copyTo(outputStream, bufferSize = 8192)
    }
}
```

**4. Error handling**
```kotlin
fun safeWriteText(fileName: String, content: String): Result<String> {
    return try {
        writeText(fileName, content)
        Result.success("File written successfully")
    } catch (e: Exception) {
        Result.failure(e)
    }
}
```

### Encryption Theory

**AES-256-GCM:**
- Advanced Encryption Standard with 256-bit key
- Galois/Counter Mode for authentication
- Provides confidentiality and integrity
- Supports streaming operations

**HKDF (HMAC-based Key Derivation Function):**
- Key derivation from master key
- Unique keys per file
- Forward secrecy on master key compromise

**Android Keystore:**
- Hardware-backed key protection (TEE/SE)
- Keys never leave device
- Protection against root and side-channel attacks
- Biometric authentication for access

**File Encryption Scheme:**
- `AES256_GCM_HKDF_4KB`: 4KB blocks for streaming
- `AES256_GCM_HKDF_1MB`: 1MB blocks for large files
- Automatic IV (Initialization Vector) management

### Best Practices

**1. Key management**
- Use single MasterKey per application
- Don't store keys in SharedPreferences
- Use biometric authentication for sensitive data

**2. Performance**
- Use streaming for files >1MB
- Buffering for I/O optimization
- Async operations for UI

**3. Security**
- Validate input data
- Handle exceptions properly
- Log without sensitive data

**4. Testing**
- Unit tests for cryptographic operations
- Integration tests with real files
- Testing on different Android versions

### Alternatives

**SQLCipher:**
- SQLite database encryption
- Transparent encryption
- Good for structured data

**Custom encryption:**
- More control over process
- Harder to implement
- Higher risk of errors

**Cloud encryption:**
- Server-side encryption
- Provider dependency
- Less control over keys

## Follow-ups
- How to implement biometric authentication for encrypted files?
- What's the difference between EncryptedFile and SQLCipher?
- How to handle key rotation in encrypted file storage?

## Related Questions
- [[q-data-encryption-at-rest--android--medium]]
