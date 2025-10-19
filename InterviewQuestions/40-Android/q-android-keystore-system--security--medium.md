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
status: draft
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

**Android Keystore** - Hardware-backed security module for secure key generation, storage, and usage. Keys are protected from extraction even on rooted devices.

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

**AES Encryption:**
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

**Biometric Authentication:**
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

**Secure Storage:**
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

**Key Attestation:**
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

**Android Keystore** - Аппаратно-защищённый модуль безопасности для безопасной генерации, хранения и использования ключей. Ключи защищены от извлечения даже на устройствах с root.

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

**AES шифрование:**
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

**Биометрическая аутентификация:**
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

**Безопасное хранилище:**
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

**Аттестация ключей:**
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

### Advanced (Harder)
- [[q-key-attestation-verification--security--hard]] - Key attestation
- [[q-hardware-security-module--security--hard]] - HSM integration
