---
id: 20251012-122766
title: "Android Keystore System / Система Android Keystore"
aliases: [Android Keystore System, Система Android Keystore]
topic: security
subtopics: [encryption, biometric-authentication]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: reviewed
moc: moc-security
created: 2025-10-15
updated: 2025-10-15
tags: [security/encryption, security/biometric-authentication, keystore, encryption, biometric, attestation, authentication, difficulty/medium]
related: [q-android-security-practices-checklist--android--medium, q-encrypted-file-storage--security--medium, q-database-encryption-android--android--medium]
---
# Question (EN)
> How to implement secure key storage using Android Keystore?

# Вопрос (RU)
> Как реализовать безопасное хранение ключей с помощью Android Keystore?

---

## Answer (EN)

**Android Keystore** is a hardware-backed security module that provides secure key generation, storage, and usage. Keys are protected from extraction even on rooted devices, making it the most secure way to handle cryptographic keys on Android.

**Security Architecture:**
- **Hardware Security Module (HSM)**: Keys stored in dedicated secure hardware (TEE/StrongBox)
- **Key Isolation**: Private keys never leave the secure environment
- **Attestation**: Cryptographic proof of key properties and device integrity
- **User Authentication**: Keys can be tied to biometric or lock screen authentication

**Security Levels (in order of security):**
1. **StrongBox**: Dedicated hardware security module (highest security)
2. **TEE**: Trusted Execution Environment (secure)
3. **Software**: Fallback when hardware unavailable (least secure)

**Key Features:**
- Hardware-backed security (TEE/StrongBox)
- Key isolation (never leave secure environment)
- User authentication (biometric/lock screen)
- Key attestation (verify device integrity)

**Basic Key Generation:**
```kotlin
class KeystoreManager {
    private val keyStore: KeyStore = KeyStore.getInstance("AndroidKeyStore").apply {
        load(null)
    }

    fun generateKey(alias: String, requireAuth: Boolean = false): SecretKey {
        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            "AndroidKeyStore"
        )

        val builder = KeyGenParameterSpec.Builder(alias, KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)

        if (requireAuth) {
            builder.setUserAuthenticationRequired(true)
        }

        keyGenerator.init(builder.build())
        return keyGenerator.generateKey()
    }
}
```

**AES-GCM Encryption Theory:**
AES-GCM provides both confidentiality and authenticity. The Galois/Counter Mode (GCM) is an authenticated encryption mode that produces a ciphertext and an authentication tag. The Initialization Vector (IV) must be unique for each encryption operation.

**AES Encryption Implementation:**
```kotlin
class AesEncryption(private val keystoreManager: KeystoreManager) {
    fun encrypt(alias: String, plaintext: String): String {
        val key = keystoreManager.getKey(alias) ?: throw IllegalStateException("Key not found")
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, key)

        val iv = cipher.iv
        val ciphertext = cipher.doFinal(plaintext.toByteArray())

        return Base64.encodeToString(iv + ciphertext, Base64.NO_WRAP)
    }

    fun decrypt(alias: String, encryptedData: String): String {
        val key = keystoreManager.getKey(alias) ?: throw IllegalStateException("Key not found")
        val combined = Base64.decode(encryptedData, Base64.NO_WRAP)

        val iv = combined.sliceArray(0..11)
        val ciphertext = combined.sliceArray(12 until combined.size)

        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        val spec = GCMParameterSpec(128, iv)
        cipher.init(Cipher.DECRYPT_MODE, key, spec)

        return String(cipher.doFinal(ciphertext))
    }
}
```

**Biometric Authentication Theory:**
Biometric authentication provides strong user verification without requiring password input. The Android Keystore can tie key usage to successful biometric authentication, ensuring only authenticated users can access encrypted data.

**Biometric Authentication Implementation:**
```kotlin
class BiometricAuthenticator(private val activity: FragmentActivity) {
    fun authenticateForEncryption(
        alias: String,
        onSuccess: (Cipher) -> Unit,
        onError: (String) -> Unit
    ) {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, key)

        val biometricPrompt = BiometricPrompt(
            activity,
            executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    result.cryptoObject?.cipher?.let { onSuccess(it) }
                }
                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    onError("Authentication error: $errString")
                }
            }
        )

        biometricPrompt.authenticate(promptInfo, BiometricPrompt.CryptoObject(cipher))
    }
}
```

**Secure Storage Theory:**
Secure storage combines Android Keystore with SharedPreferences to create an encrypted storage solution. Data is encrypted using Keystore keys before being stored in SharedPreferences, providing protection against common attack vectors.

**Secure Storage Implementation:**
```kotlin
class SecureStorage(
    context: Context,
    private val keystoreManager: KeystoreManager,
    private val aesEncryption: AesEncryption
) {
    private val prefs = context.getSharedPreferences("secure_storage", Context.MODE_PRIVATE)

    fun putString(key: String, value: String) {
        val encrypted = aesEncryption.encrypt("storage_key", value)
        prefs.edit().putString(key, encrypted).apply()
    }

    fun getString(key: String): String? {
        val encrypted = prefs.getString(key, null) ?: return null
        return try {
            aesEncryption.decrypt("storage_key", encrypted)
        } catch (e: Exception) {
            null
        }
    }
}
```

**Key Attestation Theory:**
Key attestation provides cryptographic proof that a key was generated in a secure environment with specific properties. This is crucial for applications that need to verify the security level of the device and key before trusting sensitive operations.

**Key Attestation Implementation:**
```kotlin
fun generateKeyWithAttestation(alias: String, challenge: ByteArray): Array<X509Certificate> {
    val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")

    val spec = KeyGenParameterSpec.Builder(alias, KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
        .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
        .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
        .setKeySize(256)
        .setAttestationChallenge(challenge)
        .build()

    keyGenerator.init(spec)
    keyGenerator.generateKey()

    val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
    return keyStore.getCertificateChain(alias).map { it as X509Certificate }.toTypedArray()
}
```

**Best Practices:**
- Use hardware-backed keys when available
- Enable user authentication for sensitive data
- Handle key invalidation (user changes lockscreen)
- Use strong biometric authentication (BIOMETRIC_STRONG)
- Implement key attestation for critical apps

## Ответ (RU)

**Android Keystore** - это аппаратно-защищённый модуль безопасности для безопасной генерации, хранения и использования ключей. Ключи защищены от извлечения даже на устройствах с root, что делает его самым безопасным способом обработки криптографических ключей на Android.

**Архитектура безопасности:**
- **Модуль аппаратной безопасности (HSM)**: Ключи хранятся в выделенном защищённом оборудовании (TEE/StrongBox)
- **Изоляция ключей**: Приватные ключи никогда не покидают защищённую среду
- **Аттестация**: Криптографическое доказательство свойств ключей и целостности устройства
- **Аутентификация пользователя**: Ключи могут быть привязаны к биометрической аутентификации или блокировке экрана

**Уровни безопасности (по возрастанию):**
1. **StrongBox**: Выделенный модуль аппаратной безопасности (наивысшая безопасность)
2. **TEE**: Доверенная среда выполнения (безопасно)
3. **Программное обеспечение**: Резервный вариант при недоступности оборудования (наименьшая безопасность)

**Основные функции:**
- Аппаратная безопасность (TEE/StrongBox)
- Изоляция ключей (никогда не покидают защищённую среду)
- Аутентификация пользователя (биометрия/блокировка экрана)
- Аттестация ключей (проверка целостности устройства)

**Базовая генерация ключей:**
```kotlin
class KeystoreManager {
    private val keyStore: KeyStore = KeyStore.getInstance("AndroidKeyStore").apply {
        load(null)
    }

    fun generateKey(alias: String, requireAuth: Boolean = false): SecretKey {
        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            "AndroidKeyStore"
        )

        val builder = KeyGenParameterSpec.Builder(alias, KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)

        if (requireAuth) {
            builder.setUserAuthenticationRequired(true)
        }

        keyGenerator.init(builder.build())
        return keyGenerator.generateKey()
    }
}
```

**Теория AES-GCM шифрования:**
AES-GCM обеспечивает как конфиденциальность, так и аутентичность. Режим Galois/Counter Mode (GCM) - это аутентифицированное шифрование, которое создаёт зашифрованный текст и тег аутентификации. Вектор инициализации (IV) должен быть уникальным для каждой операции шифрования.

**Реализация AES шифрования:**
```kotlin
class AesEncryption(private val keystoreManager: KeystoreManager) {
    fun encrypt(alias: String, plaintext: String): String {
        val key = keystoreManager.getKey(alias) ?: throw IllegalStateException("Key not found")
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, key)

        val iv = cipher.iv
        val ciphertext = cipher.doFinal(plaintext.toByteArray())

        return Base64.encodeToString(iv + ciphertext, Base64.NO_WRAP)
    }

    fun decrypt(alias: String, encryptedData: String): String {
        val key = keystoreManager.getKey(alias) ?: throw IllegalStateException("Key not found")
        val combined = Base64.decode(encryptedData, Base64.NO_WRAP)

        val iv = combined.sliceArray(0..11)
        val ciphertext = combined.sliceArray(12 until combined.size)

        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        val spec = GCMParameterSpec(128, iv)
        cipher.init(Cipher.DECRYPT_MODE, key, spec)

        return String(cipher.doFinal(ciphertext))
    }
}
```

**Теория биометрической аутентификации:**
Биометрическая аутентификация обеспечивает сильную верификацию пользователя без ввода пароля. Android Keystore может привязать использование ключей к успешной биометрической аутентификации, гарантируя доступ к зашифрованным данным только аутентифицированным пользователям.

**Реализация биометрической аутентификации:**
```kotlin
class BiometricAuthenticator(private val activity: FragmentActivity) {
    fun authenticateForEncryption(
        alias: String,
        onSuccess: (Cipher) -> Unit,
        onError: (String) -> Unit
    ) {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, key)

        val biometricPrompt = BiometricPrompt(
            activity,
            executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    result.cryptoObject?.cipher?.let { onSuccess(it) }
                }
                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    onError("Authentication error: $errString")
                }
            }
        )

        biometricPrompt.authenticate(promptInfo, BiometricPrompt.CryptoObject(cipher))
    }
}
```

**Теория безопасного хранилища:**
Безопасное хранилище объединяет Android Keystore с SharedPreferences для создания зашифрованного решения хранения. Данные шифруются с помощью ключей Keystore перед сохранением в SharedPreferences, обеспечивая защиту от распространённых векторов атак.

**Реализация безопасного хранилища:**
```kotlin
class SecureStorage(
    context: Context,
    private val keystoreManager: KeystoreManager,
    private val aesEncryption: AesEncryption
) {
    private val prefs = context.getSharedPreferences("secure_storage", Context.MODE_PRIVATE)

    fun putString(key: String, value: String) {
        val encrypted = aesEncryption.encrypt("storage_key", value)
        prefs.edit().putString(key, encrypted).apply()
    }

    fun getString(key: String): String? {
        val encrypted = prefs.getString(key, null) ?: return null
        return try {
            aesEncryption.decrypt("storage_key", encrypted)
        } catch (e: Exception) {
            null
        }
    }
}
```

**Теория аттестации ключей:**
Аттестация ключей предоставляет криптографическое доказательство того, что ключ был сгенерирован в защищённой среде с определёнными свойствами. Это критично для приложений, которым необходимо проверить уровень безопасности устройства и ключа перед доверием к чувствительным операциям.

**Реализация аттестации ключей:**
```kotlin
fun generateKeyWithAttestation(alias: String, challenge: ByteArray): Array<X509Certificate> {
    val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")

    val spec = KeyGenParameterSpec.Builder(alias, KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
        .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
        .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
        .setKeySize(256)
        .setAttestationChallenge(challenge)
        .build()

    keyGenerator.init(spec)
    keyGenerator.generateKey()

    val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
    return keyStore.getCertificateChain(alias).map { it as X509Certificate }.toTypedArray()
}
```

**Лучшие практики:**
- Используйте аппаратные ключи когда доступно
- Включайте аутентификацию для чувствительных данных
- Обрабатывайте инвалидацию ключей (пользователь изменил блокировку)
- Используйте сильную биометрическую аутентификацию (BIOMETRIC_STRONG)
- Реализуйте аттестацию ключей для критичных приложений

---

## Follow-ups

- When to use hardware-backed vs software keys?
- How to handle key rotation and migration?
- Biometric authentication fallback strategies?

## References

- https://developer.android.com/training/articles/keystore
- https://developer.android.com/guide/topics/security/cryptography
- https://developer.android.com/topic/security/best-practices

## Related Questions

### Prerequisites (Easier)
- [[q-android-security-practices-checklist--android--medium]] - Security basics
- [[q-encrypted-file-storage--security--medium]] - File encryption

### Related (Medium)
- [[q-database-encryption-android--android--medium]] - Database encryption
- [[q-app-security-best-practices--security--medium]] - App security
- [[q-data-encryption-at-rest--security--medium]] - Data encryption
