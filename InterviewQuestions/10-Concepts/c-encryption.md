---
id: "20251023-120300"
title: "Encryption / Шифрование"
aliases: ["Cryptography", "Encryption", "Криптография", "Шифрование"]
summary: "Process of encoding data to prevent unauthorized access using cryptographic algorithms"
topic: "security"
subtopics: ["android", "cryptography", "encryption"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-security"
related: []
created: "2025-10-23"
updated: "2025-10-23"
tags: ["android", "concept", "cryptography", "difficulty/medium", "encryption", "security"]
date created: Thursday, October 23rd 2025, 1:45:31 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Encryption / Шифрование

## Summary (EN)

Encryption is the process of converting plaintext data into ciphertext using cryptographic algorithms to prevent unauthorized access. In Android development, encryption is essential for protecting sensitive data both at rest (stored on device) and in transit (transmitted over network). Android provides the Keystore System for secure key management and APIs for implementing symmetric (AES) and asymmetric (RSA) encryption.

## Краткое Описание (RU)

Шифрование — это процесс преобразования открытого текста в зашифрованный текст с использованием криптографических алгоритмов для предотвращения несанкционированного доступа. В разработке Android шифрование необходимо для защиты конфиденциальных данных как в хранилище (на устройстве), так и при передаче (по сети). Android предоставляет систему Keystore для безопасного управления ключами и API для реализации симметричного (AES) и асимметричного (RSA) шифрования.

## Key Points (EN)

- **Symmetric encryption**: Same key for encryption and decryption (AES, ChaCha20)
- **Asymmetric encryption**: Public key for encryption, private key for decryption (RSA, ECC)
- **Android Keystore**: Hardware-backed secure storage for cryptographic keys
- **Data at rest**: Encrypt stored data (SharedPreferences, files, databases)
- **Data in transit**: Encrypt network communications (TLS/SSL)
- **Key management**: Secure generation, storage, and rotation of encryption keys

## Ключевые Моменты (RU)

- **Симметричное шифрование**: Один ключ для шифрования и расшифровки (AES, ChaCha20)
- **Асимметричное шифрование**: Публичный ключ для шифрования, приватный для расшифровки (RSA, ECC)
- **Android Keystore**: Аппаратно защищенное хранилище криптографических ключей
- **Данные в хранилище**: Шифрование сохраненных данных (SharedPreferences, файлы, базы данных)
- **Данные в передаче**: Шифрование сетевых коммуникаций (TLS/SSL)
- **Управление ключами**: Безопасная генерация, хранение и ротация ключей шифрования

## Encryption Types

### Symmetric Encryption (AES)

```kotlin
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

// Generate AES key
fun generateAESKey(): SecretKey {
    val keyGenerator = KeyGenerator.getInstance("AES")
    keyGenerator.init(256) // 256-bit key
    return keyGenerator.generateKey()
}

// Encrypt with AES-GCM
fun encryptAES(plaintext: ByteArray, key: SecretKey): Pair<ByteArray, ByteArray> {
    val cipher = Cipher.getInstance("AES/GCM/NoPadding")
    cipher.init(Cipher.ENCRYPT_MODE, key)

    val iv = cipher.iv // Initialization vector
    val ciphertext = cipher.doFinal(plaintext)

    return Pair(ciphertext, iv)
}

// Decrypt with AES-GCM
fun decryptAES(ciphertext: ByteArray, key: SecretKey, iv: ByteArray): ByteArray {
    val cipher = Cipher.getInstance("AES/GCM/NoPadding")
    val spec = GCMParameterSpec(128, iv)
    cipher.init(Cipher.DECRYPT_MODE, key, spec)

    return cipher.doFinal(ciphertext)
}
```

### Asymmetric Encryption (RSA)

```kotlin
import java.security.KeyPairGenerator
import java.security.KeyPair
import javax.crypto.Cipher

// Generate RSA key pair
fun generateRSAKeyPair(): KeyPair {
    val keyPairGenerator = KeyPairGenerator.getInstance("RSA")
    keyPairGenerator.initialize(2048) // 2048-bit key
    return keyPairGenerator.generateKeyPair()
}

// Encrypt with RSA public key
fun encryptRSA(plaintext: ByteArray, keyPair: KeyPair): ByteArray {
    val cipher = Cipher.getInstance("RSA/ECB/OAEPWITHSHA-256ANDMGF1PADDING")
    cipher.init(Cipher.ENCRYPT_MODE, keyPair.public)
    return cipher.doFinal(plaintext)
}

// Decrypt with RSA private key
fun decryptRSA(ciphertext: ByteArray, keyPair: KeyPair): ByteArray {
    val cipher = Cipher.getInstance("RSA/ECB/OAEPWITHSHA-256ANDMGF1PADDING")
    cipher.init(Cipher.DECRYPT_MODE, keyPair.private)
    return cipher.doFinal(ciphertext)
}
```

## Android Keystore System

```kotlin
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import java.security.KeyStore

// Generate key in Android Keystore
fun generateKeystoreKey(alias: String) {
    val keyGenerator = KeyGenerator.getInstance(
        KeyProperties.KEY_ALGORITHM_AES,
        "AndroidKeyStore"
    )

    val spec = KeyGenParameterSpec.Builder(
        alias,
        KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
    )
        .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
        .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
        .setKeySize(256)
        .setUserAuthenticationRequired(false)
        .build()

    keyGenerator.init(spec)
    keyGenerator.generateKey()
}

// Retrieve key from Keystore
fun getKeystoreKey(alias: String): SecretKey {
    val keyStore = KeyStore.getInstance("AndroidKeyStore")
    keyStore.load(null)
    return keyStore.getKey(alias, null) as SecretKey
}
```

## EncryptedSharedPreferences

```kotlin
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

// Create encrypted SharedPreferences
fun createEncryptedPreferences(context: Context): SharedPreferences {
    val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    return EncryptedSharedPreferences.create(
        context,
        "secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )
}

// Usage
val prefs = createEncryptedPreferences(context)
prefs.edit()
    .putString("api_key", "secret_key_value")
    .apply()
```

## EncryptedFile

```kotlin
import androidx.security.crypto.EncryptedFile
import java.io.File

// Create encrypted file
fun createEncryptedFile(context: Context, fileName: String): EncryptedFile {
    val file = File(context.filesDir, fileName)

    val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    return EncryptedFile.Builder(
        context,
        file,
        masterKey,
        EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
    ).build()
}

// Write encrypted data
fun writeEncrypted(encryptedFile: EncryptedFile, data: String) {
    encryptedFile.openFileOutput().use { output ->
        output.write(data.toByteArray())
    }
}

// Read encrypted data
fun readEncrypted(encryptedFile: EncryptedFile): String {
    return encryptedFile.openFileInput().use { input ->
        input.readBytes().toString(Charsets.UTF_8)
    }
}
```

## Use Cases

### When to Use

- **Sensitive user data**: Passwords, tokens, personal information
- **Financial data**: Credit card numbers, bank account details
- **Health information**: Medical records, health metrics
- **Authentication**: API keys, OAuth tokens, session data
- **Compliance**: GDPR, HIPAA, PCI-DSS requirements
- **Network communication**: Protecting data in transit

### When to Avoid

- **Public data**: Information meant to be publicly accessible
- **Performance-critical operations**: Encryption adds computational overhead
- **Already encrypted**: Data encrypted at system level (full disk encryption)
- **Temporary cache**: Non-sensitive cached data

## Trade-offs

**Pros**:
- **Security**: Protects data from unauthorized access
- **Compliance**: Meets regulatory requirements
- **Trust**: Increases user confidence in app security
- **Data integrity**: Detects tampering (with authenticated encryption)
- **Hardware support**: Keystore can use hardware-backed security

**Cons**:
- **Performance overhead**: Encryption/decryption takes CPU time
- **Complexity**: Requires understanding of cryptography
- **Key management**: Securely managing keys is challenging
- **Backwards compatibility**: Older Android versions have limitations
- **Battery drain**: Cryptographic operations consume power
- **Storage overhead**: Encrypted data may be larger

## Common Algorithms

### Symmetric Algorithms

| Algorithm | Key Size | Use Case |
|-----------|----------|----------|
| **AES-GCM** | 128/256 bit | General purpose, authenticated |
| **AES-CBC** | 128/256 bit | Legacy support |
| **ChaCha20-Poly1305** | 256 bit | Mobile-optimized |

### Asymmetric Algorithms

| Algorithm | Key Size | Use Case |
|-----------|----------|----------|
| **RSA** | 2048/4096 bit | Key exchange, signatures |
| **ECC (Elliptic Curve)** | 256 bit | Modern, efficient |

### Hashing Algorithms

| Algorithm | Output Size | Use Case |
|-----------|-------------|----------|
| **SHA-256** | 256 bit | General hashing |
| **SHA-512** | 512 bit | High security |
| **PBKDF2** | Variable | Password derivation |

## Best Practices

### DO:
- Use Android Keystore for key storage
- Use AES-GCM for symmetric encryption
- Use proper key sizes (AES-256, RSA-2048+)
- Implement proper IV (Initialization Vector) handling
- Use authenticated encryption (GCM mode)
- Rotate keys periodically
- Use HTTPS for network communication

### DON'T:
- Hard-code encryption keys in code
- Use ECB mode (insecure)
- Reuse IVs with same key
- Store keys with encrypted data
- Use weak algorithms (DES, MD5)
- Implement custom cryptography
- Store plaintext passwords

## Related Questions

- [[q-encryption-types-android--android--medium]]
- [[q-android-keystore-system--android--hard]]
- [[q-encrypted-sharedpreferences--android--medium]]
- [[q-aes-vs-rsa-encryption--android--medium]]

## Related Concepts

- [[c-security]] - General security concepts
- [[c-authentication]] - User authentication
- [[c-networking]] - Network security with TLS
- [[c-data-storage]] - Secure data persistence

## References

- [Android Security Best Practices](https://developer.android.com/topic/security/best-practices)
- [Android Keystore System](https://developer.android.com/training/articles/keystore)
- [Jetpack Security Crypto](https://developer.android.com/topic/security/data)
- [EncryptedSharedPreferences](https://developer.android.com/reference/androidx/security/crypto/EncryptedSharedPreferences)
- [OWASP Mobile Security](https://owasp.org/www-project-mobile-security/)
