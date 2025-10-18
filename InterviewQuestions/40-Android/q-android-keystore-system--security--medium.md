---
id: 20251012-122766
title: "Android Keystore System / Система Android Keystore"
topic: security
difficulty: medium
status: draft
moc: moc-android
related: [q-privacy-sandbox-topics-api--privacy--medium, q-why-use-diffutil--android--medium, q-integration-testing-strategies--testing--medium]
created: 2025-10-15
tags: [keystore, encryption, biometric, attestation, authentication, difficulty/medium]
---
# Android Keystore System / Система Android Keystore

**English**: Implement secure key storage using Android Keystore. Handle biometric authentication and key attestation for sensitive operations.

## Answer (EN)
The **Android Keystore System** is a hardware-backed security module that provides secure key generation, storage, and usage. Keys stored in the Keystore are protected from extraction, even on rooted devices, making it the most secure way to handle cryptographic keys on Android.

### Key Concepts

#### Keystore Features

1. **Hardware-Backed Security**: Keys stored in secure hardware (TEE/SE) when available
2. **Key Isolation**: Keys never leave secure environment
3. **User Authentication**: Tie key usage to biometric or lock screen
4. **Key Attestation**: Verify key properties and device integrity
5. **Key Validity**: Limit key usage by time or authentication

#### Security Levels

```kotlin
// Keys can be stored in:
// 1. StrongBox (Hardware Security Module) - Most secure
// 2. TEE (Trusted Execution Environment) - Secure
// 3. Software (Fallback) - Least secure
```

### Complete Keystore Implementation

#### 1. Basic Key Generation and Storage

```kotlin
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import java.security.KeyStore
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey

/**
 * Android Keystore wrapper for secure key management
 */
class KeystoreManager {

    companion object {
        private const val ANDROID_KEYSTORE = "AndroidKeyStore"
        private const val AES_KEY_SIZE = 256
    }

    private val keyStore: KeyStore = KeyStore.getInstance(ANDROID_KEYSTORE).apply {
        load(null)
    }

    /**
     * Generate a new AES key in the Keystore
     */
    fun generateKey(
        alias: String,
        requireAuthentication: Boolean = false,
        authenticationValiditySeconds: Int = 30
    ): SecretKey {
        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            ANDROID_KEYSTORE
        )

        val purposes = KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT

        val builder = KeyGenParameterSpec.Builder(alias, purposes)
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(AES_KEY_SIZE)
            .setRandomizedEncryptionRequired(true)

        if (requireAuthentication) {
            builder.setUserAuthenticationRequired(true)
            builder.setUserAuthenticationValidityDurationSeconds(authenticationValiditySeconds)
        }

        keyGenerator.init(builder.build())
        return keyGenerator.generateKey()
    }

    /**
     * Get existing key from Keystore
     */
    fun getKey(alias: String): SecretKey? {
        return keyStore.getKey(alias, null) as? SecretKey
    }

    /**
     * Check if key exists
     */
    fun containsKey(alias: String): Boolean {
        return keyStore.containsAlias(alias)
    }

    /**
     * Delete key from Keystore
     */
    fun deleteKey(alias: String) {
        keyStore.deleteEntry(alias)
    }

    /**
     * Get all key aliases
     */
    fun getAllKeyAliases(): List<String> {
        return keyStore.aliases().toList()
    }
}
```

#### 2. AES Encryption/Decryption

```kotlin
import android.util.Base64
import javax.crypto.Cipher
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import java.nio.ByteBuffer
import java.nio.charset.StandardCharsets

/**
 * AES-GCM encryption using Keystore keys
 */
class AesEncryption(private val keystoreManager: KeystoreManager) {

    companion object {
        private const val TRANSFORMATION = "AES/GCM/NoPadding"
        private const val GCM_TAG_LENGTH = 128
        private const val IV_LENGTH = 12
    }

    /**
     * Encrypt data with AES-GCM
     * Returns Base64-encoded: [IV][ciphertext][tag]
     */
    fun encrypt(alias: String, plaintext: String): EncryptionResult {
        val key = keystoreManager.getKey(alias)
            ?: throw IllegalStateException("Key not found: $alias")

        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.ENCRYPT_MODE, key)

        val iv = cipher.iv
        val ciphertext = cipher.doFinal(plaintext.toByteArray(StandardCharsets.UTF_8))

        // Combine IV + ciphertext for storage
        val combined = ByteBuffer.allocate(iv.size + ciphertext.size)
            .put(iv)
            .put(ciphertext)
            .array()

        return EncryptionResult(
            data = Base64.encodeToString(combined, Base64.NO_WRAP),
            iv = Base64.encodeToString(iv, Base64.NO_WRAP)
        )
    }

    /**
     * Decrypt data encrypted with AES-GCM
     */
    fun decrypt(alias: String, encryptedData: String): String {
        val key = keystoreManager.getKey(alias)
            ?: throw IllegalStateException("Key not found: $alias")

        val combined = Base64.decode(encryptedData, Base64.NO_WRAP)

        // Extract IV and ciphertext
        val buffer = ByteBuffer.wrap(combined)
        val iv = ByteArray(IV_LENGTH)
        buffer.get(iv)

        val ciphertext = ByteArray(buffer.remaining())
        buffer.get(ciphertext)

        // Decrypt
        val cipher = Cipher.getInstance(TRANSFORMATION)
        val spec = GCMParameterSpec(GCM_TAG_LENGTH, iv)
        cipher.init(Cipher.DECRYPT_MODE, key, spec)

        val plaintext = cipher.doFinal(ciphertext)
        return String(plaintext, StandardCharsets.UTF_8)
    }

    data class EncryptionResult(
        val data: String,
        val iv: String
    )
}
```

#### 3. RSA Key Pair Generation

```kotlin
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import java.security.KeyPairGenerator
import java.security.PrivateKey
import java.security.PublicKey
import java.security.spec.RSAKeyGenParameterSpec

/**
 * RSA encryption for key wrapping
 */
class RsaEncryption(private val keystoreManager: KeystoreManager) {

    companion object {
        private const val ANDROID_KEYSTORE = "AndroidKeyStore"
        private const val RSA_TRANSFORMATION = "RSA/ECB/OAEPWithSHA-256AndMGF1Padding"
        private const val RSA_KEY_SIZE = 2048
    }

    /**
     * Generate RSA key pair
     */
    fun generateKeyPair(alias: String, requireAuthentication: Boolean = false): KeyPair {
        val keyPairGenerator = KeyPairGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_RSA,
            ANDROID_KEYSTORE
        )

        val purposes = KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT

        val builder = KeyGenParameterSpec.Builder(alias, purposes)
            .setKeySize(RSA_KEY_SIZE)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_RSA_OAEP)
            .setDigests(
                KeyProperties.DIGEST_SHA256,
                KeyProperties.DIGEST_SHA512
            )

        if (requireAuthentication) {
            builder.setUserAuthenticationRequired(true)
        }

        keyPairGenerator.initialize(builder.build())
        return keyPairGenerator.generateKeyPair()
    }

    /**
     * Encrypt with RSA public key (for key wrapping)
     */
    fun encrypt(alias: String, plaintext: ByteArray): ByteArray {
        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE).apply { load(null) }
        val publicKey = keyStore.getCertificate(alias).publicKey

        val cipher = Cipher.getInstance(RSA_TRANSFORMATION)
        cipher.init(Cipher.ENCRYPT_MODE, publicKey)

        return cipher.doFinal(plaintext)
    }

    /**
     * Decrypt with RSA private key
     */
    fun decrypt(alias: String, ciphertext: ByteArray): ByteArray {
        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE).apply { load(null) }
        val privateKey = keyStore.getKey(alias, null) as PrivateKey

        val cipher = Cipher.getInstance(RSA_TRANSFORMATION)
        cipher.init(Cipher.DECRYPT_MODE, privateKey)

        return cipher.doFinal(ciphertext)
    }
}
```

### Biometric Authentication Integration

#### 1. BiometricPrompt Setup

```kotlin
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity

/**
 * Biometric authentication with Keystore integration
 */
class BiometricAuthenticator(
    private val activity: FragmentActivity,
    private val keystoreManager: KeystoreManager
) {

    /**
     * Check if biometric authentication is available
     */
    fun canAuthenticate(): BiometricStatus {
        val biometricManager = BiometricManager.from(activity)

        return when (biometricManager.canAuthenticate(
            BiometricManager.Authenticators.BIOMETRIC_STRONG
        )) {
            BiometricManager.BIOMETRIC_SUCCESS ->
                BiometricStatus.Available

            BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE ->
                BiometricStatus.NoHardware

            BiometricManager.BIOMETRIC_ERROR_HW_UNAVAILABLE ->
                BiometricStatus.HardwareUnavailable

            BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED ->
                BiometricStatus.NoneEnrolled

            else -> BiometricStatus.Unknown
        }
    }

    /**
     * Authenticate with biometrics for encryption
     */
    fun authenticateForEncryption(
        alias: String,
        title: String,
        subtitle: String,
        onSuccess: (Cipher) -> Unit,
        onError: (String) -> Unit
    ) {
        try {
            // Get or create key that requires authentication
            val key = keystoreManager.getKey(alias)
                ?: keystoreManager.generateKey(
                    alias = alias,
                    requireAuthentication = true
                )

            // Create cipher
            val cipher = Cipher.getInstance("AES/GCM/NoPadding")
            cipher.init(Cipher.ENCRYPT_MODE, key)

            // Show biometric prompt
            showBiometricPrompt(
                title = title,
                subtitle = subtitle,
                cipher = cipher,
                onSuccess = onSuccess,
                onError = onError
            )
        } catch (e: Exception) {
            onError("Failed to initialize encryption: ${e.message}")
        }
    }

    /**
     * Authenticate with biometrics for decryption
     */
    fun authenticateForDecryption(
        alias: String,
        iv: ByteArray,
        title: String,
        subtitle: String,
        onSuccess: (Cipher) -> Unit,
        onError: (String) -> Unit
    ) {
        try {
            val key = keystoreManager.getKey(alias)
                ?: throw IllegalStateException("Key not found: $alias")

            // Create cipher with IV for decryption
            val cipher = Cipher.getInstance("AES/GCM/NoPadding")
            val spec = GCMParameterSpec(128, iv)
            cipher.init(Cipher.DECRYPT_MODE, key, spec)

            showBiometricPrompt(
                title = title,
                subtitle = subtitle,
                cipher = cipher,
                onSuccess = onSuccess,
                onError = onError
            )
        } catch (e: Exception) {
            onError("Failed to initialize decryption: ${e.message}")
        }
    }

    private fun showBiometricPrompt(
        title: String,
        subtitle: String,
        cipher: Cipher,
        onSuccess: (Cipher) -> Unit,
        onError: (String) -> Unit
    ) {
        val executor = ContextCompat.getMainExecutor(activity)

        val biometricPrompt = BiometricPrompt(
            activity,
            executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(
                    result: BiometricPrompt.AuthenticationResult
                ) {
                    result.cryptoObject?.cipher?.let { authenticatedCipher ->
                        onSuccess(authenticatedCipher)
                    } ?: onError("No cipher from authentication")
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    onError("Authentication error: $errString")
                }

                override fun onAuthenticationFailed() {
                    onError("Authentication failed")
                }
            }
        )

        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle(title)
            .setSubtitle(subtitle)
            .setNegativeButtonText("Cancel")
            .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
            .build()

        biometricPrompt.authenticate(
            promptInfo,
            BiometricPrompt.CryptoObject(cipher)
        )
    }

    sealed class BiometricStatus {
        object Available : BiometricStatus()
        object NoHardware : BiometricStatus()
        object HardwareUnavailable : BiometricStatus()
        object NoneEnrolled : BiometricStatus()
        object Unknown : BiometricStatus()
    }
}
```

### Key Attestation

```kotlin
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Log
import com.google.android.attestation.AttestationApplicationId
import com.google.android.attestation.AuthorizationList
import com.google.android.attestation.ParsedAttestationRecord
import java.security.cert.X509Certificate

/**
 * Key attestation for verifying key properties and device integrity
 */
class KeyAttestationVerifier {

    /**
     * Generate key with attestation
     * Requires API 24+
     */
    fun generateKeyWithAttestation(
        alias: String,
        challenge: ByteArray
    ): Array<X509Certificate> {
        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            "AndroidKeyStore"
        )

        val purposes = KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT

        val spec = KeyGenParameterSpec.Builder(alias, purposes)
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)
            .setAttestationChallenge(challenge) // Include attestation
            .build()

        keyGenerator.init(spec)
        keyGenerator.generateKey()

        // Get attestation certificate chain
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        return keyStore.getCertificateChain(alias)
            .map { it as X509Certificate }
            .toTypedArray()
    }

    /**
     * Verify attestation certificate chain
     */
    fun verifyAttestation(
        certificateChain: Array<X509Certificate>,
        expectedChallenge: ByteArray
    ): AttestationResult {
        return try {
            // Parse attestation record
            val attestationRecord = ParsedAttestationRecord.createParsedAttestationRecord(
                certificateChain[0]
            )

            // Verify challenge
            if (!attestationRecord.attestationChallenge.contentEquals(expectedChallenge)) {
                return AttestationResult.Failure("Challenge mismatch")
            }

            // Check key properties
            val keymaster = attestationRecord.softwareEnforced
            val tee = attestationRecord.teeEnforced

            // Verify key is hardware-backed
            val isHardwareBacked = tee.purpose != null

            // Check attestation security level
            val securityLevel = attestationRecord.attestationSecurityLevel

            AttestationResult.Success(
                isHardwareBacked = isHardwareBacked,
                securityLevel = securityLevel.name,
                osVersion = tee.osVersion ?: -1,
                patchLevel = tee.osPatchLevel ?: -1
            )
        } catch (e: Exception) {
            AttestationResult.Failure("Attestation verification failed: ${e.message}")
        }
    }

    sealed class AttestationResult {
        data class Success(
            val isHardwareBacked: Boolean,
            val securityLevel: String,
            val osVersion: Int,
            val patchLevel: Int
        ) : AttestationResult()

        data class Failure(val reason: String) : AttestationResult()
    }
}
```

### Secure Storage Implementation

```kotlin
/**
 * Secure storage for sensitive data using Keystore
 */
class SecureStorage(
    context: Context,
    private val keystoreManager: KeystoreManager,
    private val aesEncryption: AesEncryption
) {

    companion object {
        private const val PREFS_NAME = "secure_storage"
        private const val KEY_ALIAS = "secure_storage_key"
    }

    private val sharedPreferences = context.getSharedPreferences(
        PREFS_NAME,
        Context.MODE_PRIVATE
    )

    init {
        // Ensure key exists
        if (!keystoreManager.containsKey(KEY_ALIAS)) {
            keystoreManager.generateKey(KEY_ALIAS)
        }
    }

    /**
     * Store encrypted value
     */
    fun putString(key: String, value: String) {
        val encrypted = aesEncryption.encrypt(KEY_ALIAS, value)
        sharedPreferences.edit()
            .putString(key, encrypted.data)
            .apply()
    }

    /**
     * Retrieve and decrypt value
     */
    fun getString(key: String, defaultValue: String? = null): String? {
        val encrypted = sharedPreferences.getString(key, null) ?: return defaultValue

        return try {
            aesEncryption.decrypt(KEY_ALIAS, encrypted)
        } catch (e: Exception) {
            Log.e("SecureStorage", "Decryption failed", e)
            defaultValue
        }
    }

    /**
     * Remove value
     */
    fun remove(key: String) {
        sharedPreferences.edit()
            .remove(key)
            .apply()
    }

    /**
     * Clear all stored values
     */
    fun clear() {
        sharedPreferences.edit()
            .clear()
            .apply()
    }

    /**
     * Check if key exists
     */
    fun contains(key: String): Boolean {
        return sharedPreferences.contains(key)
    }
}
```

### Real-World Examples

```kotlin
/**
 * Example 1: Secure Token Storage
 */
class TokenManager(private val secureStorage: SecureStorage) {

    fun saveAccessToken(token: String) {
        secureStorage.putString("access_token", token)
    }

    fun getAccessToken(): String? {
        return secureStorage.getString("access_token")
    }

    fun clearTokens() {
        secureStorage.remove("access_token")
        secureStorage.remove("refresh_token")
    }
}

/**
 * Example 2: Credit Card Storage with Biometrics
 */
class CreditCardManager(
    private val activity: FragmentActivity,
    private val keystoreManager: KeystoreManager,
    private val biometricAuthenticator: BiometricAuthenticator
) {

    companion object {
        private const val CARD_KEY_ALIAS = "credit_card_key"
    }

    /**
     * Save credit card with biometric protection
     */
    fun saveCreditCard(
        cardNumber: String,
        onSuccess: () -> Unit,
        onError: (String) -> Unit
    ) {
        biometricAuthenticator.authenticateForEncryption(
            alias = CARD_KEY_ALIAS,
            title = "Save Credit Card",
            subtitle = "Authenticate to securely save your card",
            onSuccess = { cipher ->
                try {
                    val encrypted = cipher.doFinal(cardNumber.toByteArray())
                    val encoded = Base64.encodeToString(encrypted, Base64.NO_WRAP)

                    // Save to preferences
                    val prefs = activity.getSharedPreferences("cards", Context.MODE_PRIVATE)
                    prefs.edit()
                        .putString("card_data", encoded)
                        .putString("card_iv", Base64.encodeToString(cipher.iv, Base64.NO_WRAP))
                        .apply()

                    onSuccess()
                } catch (e: Exception) {
                    onError("Failed to encrypt: ${e.message}")
                }
            },
            onError = onError
        )
    }

    /**
     * Load credit card with biometric authentication
     */
    fun loadCreditCard(
        onSuccess: (String) -> Unit,
        onError: (String) -> Unit
    ) {
        val prefs = activity.getSharedPreferences("cards", Context.MODE_PRIVATE)
        val encrypted = prefs.getString("card_data", null)
        val ivString = prefs.getString("card_iv", null)

        if (encrypted == null || ivString == null) {
            onError("No card data found")
            return
        }

        val iv = Base64.decode(ivString, Base64.NO_WRAP)

        biometricAuthenticator.authenticateForDecryption(
            alias = CARD_KEY_ALIAS,
            iv = iv,
            title = "Access Credit Card",
            subtitle = "Authenticate to view your card",
            onSuccess = { cipher ->
                try {
                    val encryptedData = Base64.decode(encrypted, Base64.NO_WRAP)
                    val decrypted = cipher.doFinal(encryptedData)
                    val cardNumber = String(decrypted)
                    onSuccess(cardNumber)
                } catch (e: Exception) {
                    onError("Failed to decrypt: ${e.message}")
                }
            },
            onError = onError
        )
    }
}
```

### Best Practices

1. **Always Use Hardware-Backed Keys**
   ```kotlin
   // Keys automatically use hardware when available
   keystoreManager.generateKey(alias)
   ```

2. **Enable User Authentication for Sensitive Data**
   ```kotlin
   keystoreManager.generateKey(
       alias = "sensitive_key",
       requireAuthentication = true,
       authenticationValiditySeconds = 30
   )
   ```

3. **Handle Key Invalidation**
   ```kotlin
   try {
       decrypt(data)
   } catch (e: KeyPermanentlyInvalidatedException) {
       // Key invalidated (user changed lockscreen)
       regenerateKey()
   }
   ```

4. **Use Strong Biometric Authentication**
   ```kotlin
   BiometricManager.Authenticators.BIOMETRIC_STRONG // Not WEAK
   ```

5. **Implement Key Attestation for Critical Apps**
   ```kotlin
   val attestation = generateKeyWithAttestation(alias, challenge)
   verifyAttestation(attestation, challenge)
   ```

### Summary

Android Keystore provides:

- **Hardware Security**: TEE/StrongBox backed key storage
- **Biometric Integration**: Seamless fingerprint/face authentication
- **Key Attestation**: Device and key integrity verification
- **Secure by Default**: Keys never leave secure environment
- **User Authentication**: Tie operations to device unlock

Use Keystore for: tokens, passwords, credit cards, encryption keys, API credentials, and any sensitive data.

---

## Ответ (RU)
**Система Android Keystore** - это аппаратно-защищённый модуль безопасности, который обеспечивает безопасную генерацию, хранение и использование ключей. Ключи, хранящиеся в Keystore, защищены от извлечения даже на устройствах с root, что делает его самым безопасным способом обработки криптографических ключей на Android.

### Основные концепции

**Функции Keystore:**
- Аппаратная безопасность: Ключи в защищённом оборудовании
- Изоляция ключей: Ключи никогда не покидают защищённую среду
- Аутентификация пользователя: Привязка использования ключей к биометрии
- Аттестация ключей: Проверка свойств ключей и целостности устройства

### Полная реализация Keystore

```kotlin
class KeystoreManager {
    private val keyStore: KeyStore = KeyStore.getInstance("AndroidKeyStore").apply {
        load(null)
    }

    fun generateKey(
        alias: String,
        requireAuthentication: Boolean = false
    ): SecretKey {
        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            "AndroidKeyStore"
        )

        val purposes = KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT

        val builder = KeyGenParameterSpec.Builder(alias, purposes)
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)

        if (requireAuthentication) {
            builder.setUserAuthenticationRequired(true)
        }

        keyGenerator.init(builder.build())
        return keyGenerator.generateKey()
    }
}
```

### Интеграция биометрической аутентификации

```kotlin
class BiometricAuthenticator(
    private val activity: FragmentActivity
) {

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
                override fun onAuthenticationSucceeded(
                    result: BiometricPrompt.AuthenticationResult
                ) {
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

### Безопасное хранилище

```kotlin
class SecureStorage(
    context: Context,
    private val keystoreManager: KeystoreManager
) {

    fun putString(key: String, value: String) {
        val encrypted = encrypt(value)
        sharedPreferences.edit()
            .putString(key, encrypted)
            .apply()
    }

    fun getString(key: String): String? {
        val encrypted = sharedPreferences.getString(key, null) ?: return null
        return decrypt(encrypted)
    }
}
```

### Best Practices

1. **Всегда используйте аппаратные ключи**
2. **Включайте аутентификацию для чувствительных данных**
3. **Обрабатывайте инвалидацию ключей**
4. **Используйте сильную биометрическую аутентификацию**
5. **Реализуйте аттестацию ключей для критичных приложений**

### Резюме

Android Keystore обеспечивает:

- **Аппаратную безопасность**: TEE/StrongBox хранение
- **Биометрическую интеграцию**: Аутентификация по отпечатку/лицу
- **Аттестацию ключей**: Проверка целостности
- **Безопасность по умолчанию**: Ключи не покидают защищённую среду

Используйте Keystore для: токенов, паролей, кредитных карт, ключей шифрования и любых чувствительных данных.

---

## Related Questions

### Related (Medium)
- [[q-android-security-practices-checklist--android--medium]] - Security
- [[q-encrypted-file-storage--security--medium]] - Security
- [[q-database-encryption-android--android--medium]] - Security
- [[q-app-security-best-practices--security--medium]] - Security
- [[q-data-encryption-at-rest--security--medium]] - Security
