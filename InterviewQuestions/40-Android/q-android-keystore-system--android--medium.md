---
id: sec-001
title: Android Keystore System / Система Android Keystore
aliases:
- Android Keystore System
- Система Android Keystore
topic: android
subtopics:
- keystore-crypto
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
created: 2025-10-15
updated: 2025-11-11
tags:
- android/keystore-crypto
- difficulty/medium
related:
- c-android-keystore
- q-android-security-best-practices--android--medium
- q-android-security-practices-checklist--android--medium
- q-database-encryption-android--android--medium
- q-encrypted-file-storage--android--medium
sources:
- https://developer.android.com/training/articles/keystore
anki_cards:
- slug: sec-001-0-en
  language: en
  anki_id: 1768363502147
  synced_at: '2026-01-14T09:17:53.306545'
- slug: sec-001-0-ru
  language: ru
  anki_id: 1768363502172
  synced_at: '2026-01-14T09:17:53.308958'
---
# Вопрос (RU)
> Как реализовать безопасное хранение ключей с помощью Android Keystore?

# Question (EN)
> How to implement secure key storage using Android Keystore?

## Ответ (RU)

**Android Keystore** (см. также [[c-android-keystore]]) — это модуль безопасности, обеспечивающий безопасную генерацию, хранение и использование ключей. На современных устройствах ключи могут храниться в аппаратно-защищённой среде (TEE/StrongBox), что существенно осложняет их извлечение даже при компрометации ОС (например, root/jailbreak), и является рекомендуемым способом работы с криптографическими ключами на Android.

**Архитектура безопасности:**
- **Аппаратный модуль/защищённая среда (TEE/StrongBox)**: при наличии железа ключи создаются и используются внутри доверенной среды
- **Изоляция ключей**: приватные ключи не покидают защищённую среду в открытом виде
- **Аттестация**: криптографическое доказательство свойств ключей и уровня защиты устройства (для поддерживаемых типов ключей)
- **Аутентификация пользователя**: использование ключей может быть привязано к биометрии или блокировке экрана

**Уровни безопасности (по возрастанию):**
1. **StrongBox**: выделенный модуль аппаратной безопасности (наивысшая безопасность при наличии)
2. **TEE**: доверенная среда выполнения (высокий уровень безопасности)
3. **Программное обеспечение**: резервный вариант при недоступности аппаратной поддержки (наименьшая безопасность)

**Основные функции:**
- Аппаратная защита (TEE/StrongBox при наличии)
- Изоляция ключей (ключи не покидают защищённую среду в открытом виде)
- Аутентификация пользователя (биометрия/блокировка экрана)
- Аттестация ключей (проверка свойств ключа и окружения для поддерживаемых конфигураций)

**Базовая генерация ключей (симметричный AES-ключ для шифрования данных):**
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

        val builder = KeyGenParameterSpec.Builder(
            alias,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)

        if (requireAuth) {
            // Привязать использование ключа к подтверждению пользователем (биометрия/экран блокировки)
            builder.setUserAuthenticationRequired(true)
        }

        keyGenerator.init(builder.build())
        return keyGenerator.generateKey()
    }

    fun getKey(alias: String): SecretKey? {
        val entry = keyStore.getEntry(alias, null) as? KeyStore.SecretKeyEntry
        return entry?.secretKey
    }
}
```

**Теория AES-GCM шифрования:**
AES-GCM обеспечивает конфиденциальность и целостность (аутентифицированное шифрование). Режим GCM создаёт зашифрованный текст и тег аутентификации. Вектор инициализации (IV/nonce) должен быть уникальным для каждой операции шифрования; типичный размер IV для GCM — 12 байт.

**Реализация AES шифрования:**
```kotlin
class AesEncryption(private val keystoreManager: KeystoreManager) {
    fun encrypt(alias: String, plaintext: String): String {
        val key = keystoreManager.getKey(alias) ?: throw IllegalStateException("Key not found")
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, key)

        val iv = cipher.iv // по умолчанию 12 байт для GCM на Android
        val ciphertext = cipher.doFinal(plaintext.toByteArray(Charsets.UTF_8))

        // Сохраняем IV (nonce) вместе с шифротекстом; тег аутентификации входит в ciphertext
        return Base64.encodeToString(iv + ciphertext, Base64.NO_WRAP)
    }

    fun decrypt(alias: String, encryptedData: String): String {
        val key = keystoreManager.getKey(alias) ?: throw IllegalStateException("Key not found")
        val combined = Base64.decode(encryptedData, Base64.NO_WRAP)

        // Извлекаем первые 12 байт как IV, оставшееся — шифротекст + тег
        val ivSize = 12
        require(combined.size > ivSize) { "Invalid input" }
        val iv = combined.sliceArray(0 until ivSize)
        val ciphertext = combined.sliceArray(ivSize until combined.size)

        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        val spec = GCMParameterSpec(128, iv)
        cipher.init(Cipher.DECRYPT_MODE, key, spec)

        return cipher.doFinal(ciphertext).toString(Charsets.UTF_8)
    }
}
```

**Теория биометрической аутентификации:**
Биометрическая аутентификация обеспечивает сильную проверку пользователя без ввода пароля. Android Keystore позволяет привязать использование ключей к успешной аутентификации (через `setUserAuthenticationRequired` и связанные параметры), чтобы доступ к зашифрованным данным был только у аутентифицированных пользователей.

**Пример интеграции с BiometricPrompt (упрощённый, ключ должен быть создан с требованием аутентификации):**
```kotlin
class BiometricAuthenticator(
    private val activity: FragmentActivity,
    private val executor: Executor,
    private val promptInfo: BiometricPrompt.PromptInfo
) {
    fun authenticateForEncryption(
        alias: String,
        onSuccess: (Cipher) -> Unit,
        onError: (String) -> Unit
    ) {
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        val secretKey = (keyStore.getEntry(alias, null) as? KeyStore.SecretKeyEntry)?.secretKey
            ?: run {
                onError("Key not found")
                return
            }

        val cipher = try {
            Cipher.getInstance("AES/GCM/NoPadding").apply {
                init(Cipher.ENCRYPT_MODE, secretKey)
            }
        } catch (e: Exception) {
            onError("Cipher init failed: ${e.message}")
            return
        }

        val biometricPrompt = BiometricPrompt(
            activity,
            executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    result.cryptoObject?.cipher?.let { onSuccess(it) }
                        ?: onError("No Cipher in result")
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
Безопасное хранилище сочетает Android Keystore (для хранения ключа) с устойчивым хранилищем (например, `SharedPreferences` или файл) для хранения зашифрованных данных. Данные шифруются с помощью ключей Keystore перед сохранением, что защищает их даже при компрометации обычного хранилища.

**Реализация безопасного хранилища:**
```kotlin
class SecureStorage(
    context: Context,
    private val aesEncryption: AesEncryption
) {
    private val prefs = context.getSharedPreferences("secure_storage", Context.MODE_PRIVATE)

    private val alias = "storage_key"

    fun putString(key: String, value: String) {
        val encrypted = aesEncryption.encrypt(alias, value)
        prefs.edit().putString(key, encrypted).apply()
    }

    fun getString(key: String): String? {
        val encrypted = prefs.getString(key, null) ?: return null
        return try {
            aesEncryption.decrypt(alias, encrypted)
        } catch (e: Exception) {
            null
        }
    }
}
```

**Теория аттестации ключей:**
Аттестация ключей предоставляет криптографическое доказательство того, что ключ был сгенерирован внутри доверенной среды с определёнными свойствами (аппаратная защита, версия ОС и т.п.). На Android аттестация доступна для ключей, поддерживающих attestation (как правило, асимметричные RSA/ECDSA ключи).

**Реализация аттестации ключей (пример с ECDSA-ключом):**
```kotlin
fun generateEcKeyWithAttestation(alias: String, challenge: ByteArray): Array<X509Certificate> {
    val kpg = KeyPairGenerator.getInstance(
        KeyProperties.KEY_ALGORITHM_EC,
        "AndroidKeyStore"
    )

    val spec = KeyGenParameterSpec.Builder(
        alias,
        KeyProperties.PURPOSE_SIGN or KeyProperties.PURPOSE_VERIFY
    )
        .setDigests(KeyProperties.DIGEST_SHA256, KeyProperties.DIGEST_SHA512)
        .setAttestationChallenge(challenge)
        .build()

    kpg.initialize(spec)
    kpg.generateKeyPair()

    val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
    return keyStore.getCertificateChain(alias)
        ?.map { it as X509Certificate }
        ?.toTypedArray()
        ?: emptyArray()
}
```

**Лучшие практики:**
- Используйте аппаратно-защищённые ключи при наличии поддержки (StrongBox/TEE)
- Включайте требование аутентификации пользователя для работы с ключами, защищающими чувствительные данные
- Обрабатывайте инвалидацию ключей (изменение/удаление блокировки экрана, удаление биометрии)
- Настраивайте использование сильной биометрии (`BIOMETRIC_STRONG`), когда это оправдано моделью угроз
- Используйте аттестацию ключей для критичных сценариев (финансовые приложения, защита целостности устройства)

## Follow-ups (RU)

- Когда использовать ключи с аппаратной защитой, а когда достаточно программных?
- Как обрабатывать ротацию и миграцию ключей?
- Стратегии резервных вариантов при сбое биометрической аутентификации?

## References (RU)

- https://developer.android.com/training/articles/keystore
- https://developer.android.com/guide/topics/security/cryptography
- https://developer.android.com/topic/security/best-practices

## Related Questions (RU)

### База (проще)
- [[q-android-security-practices-checklist--android--medium]] — основы безопасности
- [[q-encrypted-file-storage--android--medium]] — шифрование файлов

### Связанные (средний уровень)
- [[q-database-encryption-android--android--medium]] — шифрование базы данных

---

## Answer (EN)

**Android Keystore** (see also [[c-android-keystore]]) is a security module that provides secure key generation, storage, and usage. On modern devices, keys can be stored in hardware-backed environments (TEE/StrongBox), which significantly raises the bar for key extraction even if the OS is compromised (e.g., rooted), and is the recommended way to handle cryptographic keys on Android.

**Security Architecture:**
- **Hardware-backed environment (TEE/StrongBox)**: when available, keys are generated and used inside a trusted environment
- **Key Isolation**: private keys never leave the secure environment in plaintext
- **Attestation**: cryptographic proof of key properties and device protection level (for supported key types)
- **User Authentication**: key usage can be bound to biometric or lock screen authentication

**Security Levels (in order of security):**
1. **StrongBox**: dedicated hardware security module (highest security when available)
2. **TEE**: Trusted Execution Environment (strong security)
3. **Software**: fallback when hardware is unavailable (lowest security)

**Key Features:**
- Hardware-backed protection (TEE/StrongBox when available)
- Key isolation (keys do not leave the secure environment in plaintext)
- User authentication binding (biometric/lock screen)
- Key attestation (validate key and environment properties for supported configurations)

**Basic Key Generation (symmetric AES key for data encryption):**
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

        val builder = KeyGenParameterSpec.Builder(
            alias,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)

        if (requireAuth) {
            // Bind key usage to user authentication (biometrics/lock screen)
            builder.setUserAuthenticationRequired(true)
        }

        keyGenerator.init(builder.build())
        return keyGenerator.generateKey()
    }

    fun getKey(alias: String): SecretKey? {
        val entry = keyStore.getEntry(alias, null) as? KeyStore.SecretKeyEntry
        return entry?.secretKey
    }
}
```

**AES-GCM Encryption Theory:**
AES-GCM provides both confidentiality and integrity (authenticated encryption). Galois/Counter Mode (GCM) produces ciphertext plus an authentication tag. The Initialization Vector (IV/nonce) must be unique for each encryption operation; a typical IV size for GCM is 12 bytes.

**AES Encryption Implementation:**
```kotlin
class AesEncryption(private val keystoreManager: KeystoreManager) {
    fun encrypt(alias: String, plaintext: String): String {
        val key = keystoreManager.getKey(alias) ?: throw IllegalStateException("Key not found")
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, key)

        val iv = cipher.iv // defaults to 12 bytes for GCM on Android
        val ciphertext = cipher.doFinal(plaintext.toByteArray(Charsets.UTF_8))

        // Store IV together with ciphertext; auth tag is part of ciphertext
        return Base64.encodeToString(iv + ciphertext, Base64.NO_WRAP)
    }

    fun decrypt(alias: String, encryptedData: String): String {
        val key = keystoreManager.getKey(alias) ?: throw IllegalStateException("Key not found")
        val combined = Base64.decode(encryptedData, Base64.NO_WRAP)

        val ivSize = 12
        require(combined.size > ivSize) { "Invalid input" }
        val iv = combined.sliceArray(0 until ivSize)
        val ciphertext = combined.sliceArray(ivSize until combined.size)

        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        val spec = GCMParameterSpec(128, iv)
        cipher.init(Cipher.DECRYPT_MODE, key, spec)

        return cipher.doFinal(ciphertext).toString(Charsets.UTF_8)
    }
}
```

**Biometric Authentication Theory:**
Biometric authentication provides strong user verification without requiring a password. The Android Keystore allows binding key usage to successful authentication (via `setUserAuthenticationRequired` and related options), ensuring that only an authenticated user can use those keys to decrypt or sign.

**Biometric Authentication Implementation (simplified example with BiometricPrompt; key must be created requiring auth):**
```kotlin
class BiometricAuthenticator(
    private val activity: FragmentActivity,
    private val executor: Executor,
    private val promptInfo: BiometricPrompt.PromptInfo
) {
    fun authenticateForEncryption(
        alias: String,
        onSuccess: (Cipher) -> Unit,
        onError: (String) -> Unit
    ) {
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        val secretKey = (keyStore.getEntry(alias, null) as? KeyStore.SecretKeyEntry)?.secretKey
            ?: run {
                onError("Key not found")
                return
            }

        val cipher = try {
            Cipher.getInstance("AES/GCM/NoPadding").apply {
                init(Cipher.ENCRYPT_MODE, secretKey)
            }
        } catch (e: Exception) {
            onError("Cipher init failed: ${e.message}")
            return
        }

        val biometricPrompt = BiometricPrompt(
            activity,
            executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    result.cryptoObject?.cipher?.let { onSuccess(it) }
                        ?: onError("No Cipher in result")
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
Secure storage combines Android Keystore (for key protection) with persistent storage (e.g., `SharedPreferences` or files) to hold encrypted data. Data is encrypted with a Keystore-managed key before being persisted, mitigating risks if the plain storage is compromised.

**Secure Storage Implementation:**
```kotlin
class SecureStorage(
    context: Context,
    private val aesEncryption: AesEncryption
) {
    private val prefs = context.getSharedPreferences("secure_storage", Context.MODE_PRIVATE)

    private val alias = "storage_key"

    fun putString(key: String, value: String) {
        val encrypted = aesEncryption.encrypt(alias, value)
        prefs.edit().putString(key, encrypted).apply()
    }

    fun getString(key: String): String? {
        val encrypted = prefs.getString(key, null) ?: return null
        return try {
            aesEncryption.decrypt(alias, encrypted)
        } catch (e: Exception) {
            null
        }
    }
}
```

**Key Attestation Theory:**
Key attestation provides cryptographic proof that a key was generated inside a trusted environment with specific properties (e.g., hardware-backed, OS version, security patch level). On Android, attestation is available for keys that support it, typically asymmetric keys (RSA/ECDSA) generated in the Keystore.

**Key Attestation Implementation (example with EC key):**
```kotlin
fun generateEcKeyWithAttestation(alias: String, challenge: ByteArray): Array<X509Certificate> {
    val kpg = KeyPairGenerator.getInstance(
        KeyProperties.KEY_ALGORITHM_EC,
        "AndroidKeyStore"
    )

    val spec = KeyGenParameterSpec.Builder(
        alias,
        KeyProperties.PURPOSE_SIGN or KeyProperties.PURPOSE_VERIFY
    )
        .setDigests(KeyProperties.DIGEST_SHA256, KeyProperties.DIGEST_SHA512)
        .setAttestationChallenge(challenge)
        .build()

    kpg.initialize(spec)
    kpg.generateKeyPair()

    val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
    return keyStore.getCertificateChain(alias)
        ?.map { it as X509Certificate }
        ?.toTypedArray()
        ?: emptyArray()
}
```

**Best Practices:**
- Prefer hardware-backed keys when available (StrongBox/TEE)
- Require user authentication for keys protecting sensitive data
- Handle key invalidation (lock screen changes, biometrics reset, key removal)
- Configure strong biometrics (`BIOMETRIC_STRONG`) where appropriate for the threat model
- Use key attestation for high-security use cases (e.g., financial, anti-tampering)

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
- [[q-encrypted-file-storage--android--medium]] - File encryption

### Related (Medium)
- [[q-database-encryption-android--android--medium]] - `Database` encryption
