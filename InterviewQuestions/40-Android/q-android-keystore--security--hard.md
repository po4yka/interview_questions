---
id: sec-010
title: Android Keystore Advanced Security / Продвинутая безопасность Android Keystore
aliases:
- Android Keystore Advanced Security
- Продвинутая безопасность Android Keystore
topic: android
subtopics:
- security
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
created: 2026-01-23
updated: 2026-01-23
tags:
- android/security
- android/keystore-crypto
- difficulty/hard
related:
- q-android-keystore-system--android--medium
- q-biometric-authentication--android--medium
- q-encrypted-shared-preferences--security--medium
sources:
- https://developer.android.com/training/articles/keystore
- https://developer.android.com/reference/android/security/keystore/KeyGenParameterSpec
anki_cards:
- slug: sec-010-0-en
  language: en
- slug: sec-010-0-ru
  language: ru
---
# Vopros (RU)
> Kak nastroit' KeyGenParameterSpec dlya maksimal'noj bezopasnosti s privyazkoj k biometrii i apparatnoj zashchitoj?

# Question (EN)
> How to configure KeyGenParameterSpec for maximum security with biometric binding and hardware-backed protection?

---

## Otvet (RU)

**KeyGenParameterSpec** - eto konfigurator dlya generacii klyuchej v Android Keystore, pozvolyayushchij nastroit' uroven' bezopasnosti, privyazku k autentifikacii pol'zovatelya i apparatnuyu zashchitu.

### Polnaya konfiguraciya bezopasnosti

```kotlin
class SecureKeyManager(private val context: Context) {

    companion object {
        private const val KEY_ALIAS = "secure_biometric_key"
        private const val AUTH_VALIDITY_SECONDS = 30
    }

    /**
     * Sozdaet klyuch s maksimal'noj zashchitoj:
     * - Apparatnaya podderzhka (TEE/StrongBox)
     * - Privyazka k biometrii
     * - Ogranichennoe vremya dejstviya autentifikacii
     */
    fun generateSecureKey(): SecretKey {
        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            "AndroidKeyStore"
        )

        val spec = KeyGenParameterSpec.Builder(
            KEY_ALIAS,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            // Algoritm i rezhim shifrovaniia
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)

            // Apparatnaya zashchita
            .setIsStrongBoxBacked(true)  // API 28+: ispol'zuet StrongBox esli dostupno

            // Privyazka k autentifikacii pol'zovatelya
            .setUserAuthenticationRequired(true)
            .setUserAuthenticationParameters(
                AUTH_VALIDITY_SECONDS,  // Vremya dejstviya autentifikacii
                KeyProperties.AUTH_BIOMETRIC_STRONG  // Tol'ko sil'naya biometriya
            )  // API 30+

            // Invalidaciya klyucha pri izmenenii biometrii
            .setInvalidatedByBiometricEnrollment(true)

            // Klyuch nel'zya eksportirovat'
            .setRandomizedEncryptionRequired(true)

            .build()

        return try {
            keyGenerator.init(spec)
            keyGenerator.generateKey()
        } catch (e: StrongBoxUnavailableException) {
            // Fallback na TEE esli StrongBox nedostupno
            generateKeyWithTEE()
        }
    }

    private fun generateKeyWithTEE(): SecretKey {
        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            "AndroidKeyStore"
        )

        val spec = KeyGenParameterSpec.Builder(
            KEY_ALIAS,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)
            .setUserAuthenticationRequired(true)
            .setUserAuthenticationParameters(
                AUTH_VALIDITY_SECONDS,
                KeyProperties.AUTH_BIOMETRIC_STRONG or
                    KeyProperties.AUTH_DEVICE_CREDENTIAL
            )
            .setInvalidatedByBiometricEnrollment(true)
            .build()

        keyGenerator.init(spec)
        return keyGenerator.generateKey()
    }
}
```

### Proverka urovnya apparatnoj zashchity

```kotlin
fun checkKeySecurityLevel(alias: String): SecurityLevel {
    val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
    val secretKey = (keyStore.getEntry(alias, null) as? KeyStore.SecretKeyEntry)?.secretKey
        ?: return SecurityLevel.NOT_FOUND

    val factory = SecretKeyFactory.getInstance(secretKey.algorithm, "AndroidKeyStore")
    val keyInfo = factory.getKeySpec(secretKey, KeyInfo::class.java) as KeyInfo

    return when {
        keyInfo.securityLevel == KeyProperties.SECURITY_LEVEL_STRONGBOX ->
            SecurityLevel.STRONGBOX
        keyInfo.securityLevel == KeyProperties.SECURITY_LEVEL_TRUSTED_ENVIRONMENT ->
            SecurityLevel.TEE
        keyInfo.isInsideSecureHardware ->
            SecurityLevel.HARDWARE_BACKED  // API < 31
        else ->
            SecurityLevel.SOFTWARE
    }
}

enum class SecurityLevel {
    STRONGBOX,           // Vysshij uroven': otdel'nyj chip
    TEE,                 // Vysokij uroven': Trusted Execution Environment
    HARDWARE_BACKED,     // Apparatnaya podderzhka (starye API)
    SOFTWARE,            // Programmnyj uroven' (minimal'naya zashchita)
    NOT_FOUND
}
```

### Ispol'zovanie s BiometricPrompt

```kotlin
class BiometricCryptoManager(
    private val activity: FragmentActivity,
    private val keyManager: SecureKeyManager
) {
    fun encryptWithBiometric(
        data: ByteArray,
        onSuccess: (EncryptedData) -> Unit,
        onError: (BiometricError) -> Unit
    ) {
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        val secretKey = (keyStore.getEntry("secure_biometric_key", null)
            as? KeyStore.SecretKeyEntry)?.secretKey
            ?: run {
                onError(BiometricError.KeyNotFound)
                return
            }

        val cipher = try {
            Cipher.getInstance("AES/GCM/NoPadding").apply {
                init(Cipher.ENCRYPT_MODE, secretKey)
            }
        } catch (e: UserNotAuthenticatedException) {
            // Klyuch trebuet autentifikacii - zapustim BiometricPrompt
            authenticateAndEncrypt(secretKey, data, onSuccess, onError)
            return
        }

        // Autentifikaciya eshche dejstvitel'na
        val encrypted = EncryptedData(
            ciphertext = cipher.doFinal(data),
            iv = cipher.iv
        )
        onSuccess(encrypted)
    }

    private fun authenticateAndEncrypt(
        secretKey: SecretKey,
        data: ByteArray,
        onSuccess: (EncryptedData) -> Unit,
        onError: (BiometricError) -> Unit
    ) {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, secretKey)

        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Podtverdite lichnost'")
            .setSubtitle("Ispol'zujte biometriyu dlya dostupa k dannym")
            .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
            .setNegativeButtonText("Otmena")
            .build()

        val biometricPrompt = BiometricPrompt(
            activity,
            ContextCompat.getMainExecutor(activity),
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(
                    result: BiometricPrompt.AuthenticationResult
                ) {
                    val authenticatedCipher = result.cryptoObject?.cipher ?: return
                    val encrypted = EncryptedData(
                        ciphertext = authenticatedCipher.doFinal(data),
                        iv = authenticatedCipher.iv
                    )
                    onSuccess(encrypted)
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    onError(BiometricError.AuthenticationFailed(errorCode, errString.toString()))
                }
            }
        )

        biometricPrompt.authenticate(promptInfo, BiometricPrompt.CryptoObject(cipher))
    }
}

data class EncryptedData(val ciphertext: ByteArray, val iv: ByteArray)

sealed class BiometricError {
    object KeyNotFound : BiometricError()
    data class AuthenticationFailed(val code: Int, val message: String) : BiometricError()
}
```

### Attestaciya klyuchej

```kotlin
/**
 * Attestaciya pozvolyaet serveru proverit', chto klyuch:
 * - Sgenerirovan vnutri zashhishchennoj sredy
 * - Imeet opredelennye svojstva bezopasnosti
 */
fun generateKeyWithAttestation(
    alias: String,
    challenge: ByteArray  // Odnorazovyj challenge ot servera
): Certificate? {
    val keyPairGenerator = KeyPairGenerator.getInstance(
        KeyProperties.KEY_ALGORITHM_EC,
        "AndroidKeyStore"
    )

    val spec = KeyGenParameterSpec.Builder(
        alias,
        KeyProperties.PURPOSE_SIGN or KeyProperties.PURPOSE_VERIFY
    )
        .setDigests(KeyProperties.DIGEST_SHA256)
        .setAttestationChallenge(challenge)  // Privyazka k servera challenge
        .setIsStrongBoxBacked(true)
        .build()

    keyPairGenerator.initialize(spec)
    keyPairGenerator.generateKeyPair()

    val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
    return keyStore.getCertificate(alias)
}
```

### Luchshie praktiki

| Aspekt | Rekomendaciya |
|--------|---------------|
| Apparatnaya zashchita | StrongBox > TEE > Software |
| Autentifikaciya | `BIOMETRIC_STRONG` dlya chuvstvitel'nyh operacij |
| Vremya dejstviya | 30-60 sekund dlya finansovyh operacij |
| Invalidaciya | `setInvalidatedByBiometricEnrollment(true)` |
| Attestaciya | Ispol'zovat' dlya kritichnyh klyuchej (bankovskie prilozheniya) |

---

## Answer (EN)

**KeyGenParameterSpec** is the configurator for key generation in Android Keystore, allowing you to set security level, user authentication binding, and hardware-backed protection.

### Complete security configuration

```kotlin
class SecureKeyManager(private val context: Context) {

    companion object {
        private const val KEY_ALIAS = "secure_biometric_key"
        private const val AUTH_VALIDITY_SECONDS = 30
    }

    /**
     * Creates a key with maximum protection:
     * - Hardware-backed (TEE/StrongBox)
     * - Biometric binding
     * - Limited authentication validity
     */
    fun generateSecureKey(): SecretKey {
        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            "AndroidKeyStore"
        )

        val spec = KeyGenParameterSpec.Builder(
            KEY_ALIAS,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            // Algorithm and encryption mode
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)

            // Hardware protection
            .setIsStrongBoxBacked(true)  // API 28+: uses StrongBox if available

            // User authentication binding
            .setUserAuthenticationRequired(true)
            .setUserAuthenticationParameters(
                AUTH_VALIDITY_SECONDS,  // Authentication validity window
                KeyProperties.AUTH_BIOMETRIC_STRONG  // Strong biometric only
            )  // API 30+

            // Key invalidation on biometric enrollment change
            .setInvalidatedByBiometricEnrollment(true)

            // Key cannot be exported
            .setRandomizedEncryptionRequired(true)

            .build()

        return try {
            keyGenerator.init(spec)
            keyGenerator.generateKey()
        } catch (e: StrongBoxUnavailableException) {
            // Fallback to TEE if StrongBox unavailable
            generateKeyWithTEE()
        }
    }

    private fun generateKeyWithTEE(): SecretKey {
        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            "AndroidKeyStore"
        )

        val spec = KeyGenParameterSpec.Builder(
            KEY_ALIAS,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)
            .setUserAuthenticationRequired(true)
            .setUserAuthenticationParameters(
                AUTH_VALIDITY_SECONDS,
                KeyProperties.AUTH_BIOMETRIC_STRONG or
                    KeyProperties.AUTH_DEVICE_CREDENTIAL
            )
            .setInvalidatedByBiometricEnrollment(true)
            .build()

        keyGenerator.init(spec)
        return keyGenerator.generateKey()
    }
}
```

### Checking key security level

```kotlin
fun checkKeySecurityLevel(alias: String): SecurityLevel {
    val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
    val secretKey = (keyStore.getEntry(alias, null) as? KeyStore.SecretKeyEntry)?.secretKey
        ?: return SecurityLevel.NOT_FOUND

    val factory = SecretKeyFactory.getInstance(secretKey.algorithm, "AndroidKeyStore")
    val keyInfo = factory.getKeySpec(secretKey, KeyInfo::class.java) as KeyInfo

    return when {
        keyInfo.securityLevel == KeyProperties.SECURITY_LEVEL_STRONGBOX ->
            SecurityLevel.STRONGBOX
        keyInfo.securityLevel == KeyProperties.SECURITY_LEVEL_TRUSTED_ENVIRONMENT ->
            SecurityLevel.TEE
        keyInfo.isInsideSecureHardware ->
            SecurityLevel.HARDWARE_BACKED  // API < 31
        else ->
            SecurityLevel.SOFTWARE
    }
}

enum class SecurityLevel {
    STRONGBOX,           // Highest level: dedicated chip
    TEE,                 // High level: Trusted Execution Environment
    HARDWARE_BACKED,     // Hardware-backed (older APIs)
    SOFTWARE,            // Software level (minimum protection)
    NOT_FOUND
}
```

### Usage with BiometricPrompt

```kotlin
class BiometricCryptoManager(
    private val activity: FragmentActivity,
    private val keyManager: SecureKeyManager
) {
    fun encryptWithBiometric(
        data: ByteArray,
        onSuccess: (EncryptedData) -> Unit,
        onError: (BiometricError) -> Unit
    ) {
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        val secretKey = (keyStore.getEntry("secure_biometric_key", null)
            as? KeyStore.SecretKeyEntry)?.secretKey
            ?: run {
                onError(BiometricError.KeyNotFound)
                return
            }

        val cipher = try {
            Cipher.getInstance("AES/GCM/NoPadding").apply {
                init(Cipher.ENCRYPT_MODE, secretKey)
            }
        } catch (e: UserNotAuthenticatedException) {
            // Key requires authentication - launch BiometricPrompt
            authenticateAndEncrypt(secretKey, data, onSuccess, onError)
            return
        }

        // Authentication still valid
        val encrypted = EncryptedData(
            ciphertext = cipher.doFinal(data),
            iv = cipher.iv
        )
        onSuccess(encrypted)
    }

    private fun authenticateAndEncrypt(
        secretKey: SecretKey,
        data: ByteArray,
        onSuccess: (EncryptedData) -> Unit,
        onError: (BiometricError) -> Unit
    ) {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, secretKey)

        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Confirm your identity")
            .setSubtitle("Use biometrics to access data")
            .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
            .setNegativeButtonText("Cancel")
            .build()

        val biometricPrompt = BiometricPrompt(
            activity,
            ContextCompat.getMainExecutor(activity),
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(
                    result: BiometricPrompt.AuthenticationResult
                ) {
                    val authenticatedCipher = result.cryptoObject?.cipher ?: return
                    val encrypted = EncryptedData(
                        ciphertext = authenticatedCipher.doFinal(data),
                        iv = authenticatedCipher.iv
                    )
                    onSuccess(encrypted)
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    onError(BiometricError.AuthenticationFailed(errorCode, errString.toString()))
                }
            }
        )

        biometricPrompt.authenticate(promptInfo, BiometricPrompt.CryptoObject(cipher))
    }
}

data class EncryptedData(val ciphertext: ByteArray, val iv: ByteArray)

sealed class BiometricError {
    object KeyNotFound : BiometricError()
    data class AuthenticationFailed(val code: Int, val message: String) : BiometricError()
}
```

### Key attestation

```kotlin
/**
 * Attestation allows server to verify that the key:
 * - Was generated inside a secure environment
 * - Has specific security properties
 */
fun generateKeyWithAttestation(
    alias: String,
    challenge: ByteArray  // One-time challenge from server
): Certificate? {
    val keyPairGenerator = KeyPairGenerator.getInstance(
        KeyProperties.KEY_ALGORITHM_EC,
        "AndroidKeyStore"
    )

    val spec = KeyGenParameterSpec.Builder(
        alias,
        KeyProperties.PURPOSE_SIGN or KeyProperties.PURPOSE_VERIFY
    )
        .setDigests(KeyProperties.DIGEST_SHA256)
        .setAttestationChallenge(challenge)  // Bind to server challenge
        .setIsStrongBoxBacked(true)
        .build()

    keyPairGenerator.initialize(spec)
    keyPairGenerator.generateKeyPair()

    val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
    return keyStore.getCertificate(alias)
}
```

### Best practices

| Aspect | Recommendation |
|--------|----------------|
| Hardware protection | StrongBox > TEE > Software |
| Authentication | `BIOMETRIC_STRONG` for sensitive operations |
| Validity window | 30-60 seconds for financial operations |
| Invalidation | `setInvalidatedByBiometricEnrollment(true)` |
| Attestation | Use for critical keys (banking apps) |

---

## Follow-ups

- How to handle key migration when upgrading security levels?
- What happens when StrongBox key is accessed on device without StrongBox?
- How to implement secure key backup and recovery?

## References

- https://developer.android.com/training/articles/keystore
- https://developer.android.com/reference/android/security/keystore/KeyGenParameterSpec
- https://developer.android.com/training/articles/keystore#HardwareSecurityModule

## Related Questions

### Prerequisites (Easier)
- [[q-android-keystore-system--android--medium]] - Basic Keystore usage
- [[q-biometric-authentication--android--medium]] - BiometricPrompt basics

### Related (Same Level)
- [[q-encrypted-shared-preferences--security--medium]] - Encrypted storage
- [[q-play-integrity-api--security--hard]] - Device attestation
