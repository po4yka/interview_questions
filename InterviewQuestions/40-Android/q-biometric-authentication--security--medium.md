---
id: sec-008
title: Biometric Authentication / Biometricheskaya autentifikaciya
aliases:
- BiometricPrompt
- Fingerprint Authentication
- Face Authentication
topic: android
subtopics:
- security
- authentication
question_kind: theory
difficulty: medium
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
- difficulty/medium
related:
- q-android-keystore--security--hard
- q-encrypted-shared-preferences--security--medium
sources:
- https://developer.android.com/identity/sign-in/biometric-auth
- https://developer.android.com/reference/androidx/biometric/BiometricPrompt
---
# Vopros (RU)
> Kak realizovat' biometricheskuyu autentifikaciyu s BiometricPrompt i CryptoObject?

# Question (EN)
> How do you implement biometric authentication with BiometricPrompt and CryptoObject?

---

## Otvet (RU)

**Teoriya:**
**BiometricPrompt** - eto unificirovanniy API dlya biometricheskoy autentifikacii (otpechatok pal'ca, raspoznavanie lica), vvedenniy v Android 9 (API 28). On zamenayat ustarevshie FingerprintManager i factoobrazno rabotaet na vseh ustrojstvah.

### Urovni bezopasnosti biometrii
| Uroven' | Opisanie | Primery |
|---------|----------|---------|
| `BIOMETRIC_STRONG` | Class 3 biometriya | Otpechatok, 3D lico |
| `BIOMETRIC_WEAK` | Class 2 biometriya | 2D lico (menee bezopasno) |
| `DEVICE_CREDENTIAL` | PIN/Pattern/Parol' | Fallback variant |

### Nastroyka zavisimostej
```kotlin
// build.gradle.kts
dependencies {
    implementation("androidx.biometric:biometric:1.2.0-alpha05")
}
```

### Bazovaya realizaciya
```kotlin
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity

class BiometricAuthManager(private val activity: FragmentActivity) {

    private val executor = ContextCompat.getMainExecutor(activity)

    // Proverka dostupnosti biometrii
    fun checkBiometricAvailability(): BiometricStatus {
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

            BiometricManager.BIOMETRIC_ERROR_SECURITY_UPDATE_REQUIRED ->
                BiometricStatus.SecurityUpdateRequired

            else -> BiometricStatus.Unknown
        }
    }

    // Prostaya autentifikaciya (bez kripto)
    fun authenticateSimple(
        onSuccess: () -> Unit,
        onError: (Int, String) -> Unit,
        onFailed: () -> Unit
    ) {
        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Podtverdite lichnost'")
            .setSubtitle("Ispol'zujte biometriyu")
            .setDescription("Dlya dostupa k zaschischennoy funkcii")
            // Razreshaem fallback na PIN/Pattern
            .setAllowedAuthenticators(
                BiometricManager.Authenticators.BIOMETRIC_STRONG or
                BiometricManager.Authenticators.DEVICE_CREDENTIAL
            )
            .build()

        val biometricPrompt = BiometricPrompt(
            activity,
            executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(
                    result: BiometricPrompt.AuthenticationResult
                ) {
                    onSuccess()
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    onError(errorCode, errString.toString())
                }

                override fun onAuthenticationFailed() {
                    // Neudachnaya popytka (mozhno povtorit')
                    onFailed()
                }
            }
        )

        biometricPrompt.authenticate(promptInfo)
    }
}

sealed class BiometricStatus {
    object Available : BiometricStatus()
    object NoHardware : BiometricStatus()
    object HardwareUnavailable : BiometricStatus()
    object NoneEnrolled : BiometricStatus()
    object SecurityUpdateRequired : BiometricStatus()
    object Unknown : BiometricStatus()
}
```

### Autentifikaciya s CryptoObject (dlya maksimal'noj bezopasnosti)
```kotlin
class SecureBiometricAuth(private val activity: FragmentActivity) {

    companion object {
        private const val KEY_ALIAS = "biometric_key"
    }

    private val executor = ContextCompat.getMainExecutor(activity)

    // Sozdanie klyucha, privyazannogo k biometrii
    private fun generateBiometricKey(): SecretKey {
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
            // Trebuet biometriyu dlya kazhdogo ispol'zovaniya
            .setUserAuthenticationRequired(true)
            // Invalidate esli biometriya izmenena
            .setInvalidatedByBiometricEnrollment(true)
            .build()

        keyGenerator.init(spec)
        return keyGenerator.generateKey()
    }

    private fun getOrCreateKey(): SecretKey {
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }

        return if (keyStore.containsAlias(KEY_ALIAS)) {
            keyStore.getKey(KEY_ALIAS, null) as SecretKey
        } else {
            generateBiometricKey()
        }
    }

    // Autentifikaciya s shifrovaniem
    fun authenticateAndEncrypt(
        data: ByteArray,
        onSuccess: (EncryptedResult) -> Unit,
        onError: (BiometricError) -> Unit
    ) {
        val secretKey = try {
            getOrCreateKey()
        } catch (e: KeyPermanentlyInvalidatedException) {
            // Biometriya byla izmenena - nuzhno peregenerirovat' klyuch
            onError(BiometricError.KeyInvalidated)
            return
        }

        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, secretKey)

        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Zashchita dannyh")
            .setSubtitle("Podtverdite biometriju dlya shifrovapiya")
            .setNegativeButtonText("Otmena")
            .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
            .build()

        val biometricPrompt = BiometricPrompt(
            activity,
            executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(
                    result: BiometricPrompt.AuthenticationResult
                ) {
                    val authenticatedCipher = result.cryptoObject?.cipher
                        ?: run {
                            onError(BiometricError.CryptoObjectMissing)
                            return
                        }

                    val encrypted = authenticatedCipher.doFinal(data)
                    val iv = authenticatedCipher.iv

                    onSuccess(EncryptedResult(encrypted, iv))
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    val error = when (errorCode) {
                        BiometricPrompt.ERROR_CANCELED,
                        BiometricPrompt.ERROR_USER_CANCELED,
                        BiometricPrompt.ERROR_NEGATIVE_BUTTON ->
                            BiometricError.Canceled

                        BiometricPrompt.ERROR_LOCKOUT ->
                            BiometricError.Lockout(false)

                        BiometricPrompt.ERROR_LOCKOUT_PERMANENT ->
                            BiometricError.Lockout(true)

                        else ->
                            BiometricError.Other(errorCode, errString.toString())
                    }
                    onError(error)
                }

                override fun onAuthenticationFailed() {
                    // Popytka neudachna, no mozhno povtorit'
                }
            }
        )

        biometricPrompt.authenticate(promptInfo, BiometricPrompt.CryptoObject(cipher))
    }

    // Rasshifrovka s biometriej
    fun authenticateAndDecrypt(
        encryptedResult: EncryptedResult,
        onSuccess: (ByteArray) -> Unit,
        onError: (BiometricError) -> Unit
    ) {
        val secretKey = try {
            getOrCreateKey()
        } catch (e: KeyPermanentlyInvalidatedException) {
            onError(BiometricError.KeyInvalidated)
            return
        }

        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        val spec = GCMParameterSpec(128, encryptedResult.iv)
        cipher.init(Cipher.DECRYPT_MODE, secretKey, spec)

        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Dostup k dannym")
            .setSubtitle("Podtverdite biometriju")
            .setNegativeButtonText("Otmena")
            .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
            .build()

        val biometricPrompt = BiometricPrompt(
            activity,
            executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(
                    result: BiometricPrompt.AuthenticationResult
                ) {
                    val authenticatedCipher = result.cryptoObject?.cipher
                        ?: run {
                            onError(BiometricError.CryptoObjectMissing)
                            return
                        }

                    try {
                        val decrypted = authenticatedCipher.doFinal(encryptedResult.data)
                        onSuccess(decrypted)
                    } catch (e: Exception) {
                        onError(BiometricError.DecryptionFailed)
                    }
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    onError(BiometricError.Other(errorCode, errString.toString()))
                }
            }
        )

        biometricPrompt.authenticate(promptInfo, BiometricPrompt.CryptoObject(cipher))
    }
}

data class EncryptedResult(val data: ByteArray, val iv: ByteArray)

sealed class BiometricError {
    object KeyInvalidated : BiometricError()
    object CryptoObjectMissing : BiometricError()
    object DecryptionFailed : BiometricError()
    object Canceled : BiometricError()
    data class Lockout(val permanent: Boolean) : BiometricError()
    data class Other(val code: Int, val message: String) : BiometricError()
}
```

### Obrabotka oshibok
```kotlin
fun handleBiometricError(error: BiometricError) {
    when (error) {
        is BiometricError.KeyInvalidated -> {
            // Biometriya izmenena - predlozhit' povtornuyu nastrojku
            showReEnrollDialog()
        }
        is BiometricError.Lockout -> {
            if (error.permanent) {
                // Predlozhit' vosstanovlenie cherez parol' ustroystva
                showDeviceCredentialFallback()
            } else {
                // Pokazat' ozhidanie 30 sekund
                showTemporaryLockoutMessage()
            }
        }
        is BiometricError.Canceled -> {
            // Pol'zovatel' otmenil - nichego ne delaem
        }
        else -> {
            showGenericError()
        }
    }
}
```

---

## Answer (EN)

**Theory:**
**BiometricPrompt** is a unified API for biometric authentication (fingerprint, face recognition), introduced in Android 9 (API 28). It replaces the deprecated FingerprintManager and works consistently across all devices.

### Biometric security levels
| Level | Description | Examples |
|-------|-------------|----------|
| `BIOMETRIC_STRONG` | Class 3 biometrics | Fingerprint, 3D face |
| `BIOMETRIC_WEAK` | Class 2 biometrics | 2D face (less secure) |
| `DEVICE_CREDENTIAL` | PIN/Pattern/Password | Fallback option |

### Setup dependencies
```kotlin
// build.gradle.kts
dependencies {
    implementation("androidx.biometric:biometric:1.2.0-alpha05")
}
```

### Basic implementation
```kotlin
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity

class BiometricAuthManager(private val activity: FragmentActivity) {

    private val executor = ContextCompat.getMainExecutor(activity)

    // Check biometric availability
    fun checkBiometricAvailability(): BiometricStatus {
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

            BiometricManager.BIOMETRIC_ERROR_SECURITY_UPDATE_REQUIRED ->
                BiometricStatus.SecurityUpdateRequired

            else -> BiometricStatus.Unknown
        }
    }

    // Simple authentication (no crypto)
    fun authenticateSimple(
        onSuccess: () -> Unit,
        onError: (Int, String) -> Unit,
        onFailed: () -> Unit
    ) {
        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Confirm your identity")
            .setSubtitle("Use biometrics")
            .setDescription("To access protected feature")
            // Allow fallback to PIN/Pattern
            .setAllowedAuthenticators(
                BiometricManager.Authenticators.BIOMETRIC_STRONG or
                BiometricManager.Authenticators.DEVICE_CREDENTIAL
            )
            .build()

        val biometricPrompt = BiometricPrompt(
            activity,
            executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(
                    result: BiometricPrompt.AuthenticationResult
                ) {
                    onSuccess()
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    onError(errorCode, errString.toString())
                }

                override fun onAuthenticationFailed() {
                    // Failed attempt (can retry)
                    onFailed()
                }
            }
        )

        biometricPrompt.authenticate(promptInfo)
    }
}

sealed class BiometricStatus {
    object Available : BiometricStatus()
    object NoHardware : BiometricStatus()
    object HardwareUnavailable : BiometricStatus()
    object NoneEnrolled : BiometricStatus()
    object SecurityUpdateRequired : BiometricStatus()
    object Unknown : BiometricStatus()
}
```

### Authentication with CryptoObject (for maximum security)
```kotlin
class SecureBiometricAuth(private val activity: FragmentActivity) {

    companion object {
        private const val KEY_ALIAS = "biometric_key"
    }

    private val executor = ContextCompat.getMainExecutor(activity)

    // Create biometric-bound key
    private fun generateBiometricKey(): SecretKey {
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
            // Require biometrics for each use
            .setUserAuthenticationRequired(true)
            // Invalidate if biometrics changed
            .setInvalidatedByBiometricEnrollment(true)
            .build()

        keyGenerator.init(spec)
        return keyGenerator.generateKey()
    }

    private fun getOrCreateKey(): SecretKey {
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }

        return if (keyStore.containsAlias(KEY_ALIAS)) {
            keyStore.getKey(KEY_ALIAS, null) as SecretKey
        } else {
            generateBiometricKey()
        }
    }

    // Authenticate and encrypt
    fun authenticateAndEncrypt(
        data: ByteArray,
        onSuccess: (EncryptedResult) -> Unit,
        onError: (BiometricError) -> Unit
    ) {
        val secretKey = try {
            getOrCreateKey()
        } catch (e: KeyPermanentlyInvalidatedException) {
            // Biometrics changed - need to regenerate key
            onError(BiometricError.KeyInvalidated)
            return
        }

        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, secretKey)

        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Protect data")
            .setSubtitle("Confirm biometrics to encrypt")
            .setNegativeButtonText("Cancel")
            .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
            .build()

        val biometricPrompt = BiometricPrompt(
            activity,
            executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(
                    result: BiometricPrompt.AuthenticationResult
                ) {
                    val authenticatedCipher = result.cryptoObject?.cipher
                        ?: run {
                            onError(BiometricError.CryptoObjectMissing)
                            return
                        }

                    val encrypted = authenticatedCipher.doFinal(data)
                    val iv = authenticatedCipher.iv

                    onSuccess(EncryptedResult(encrypted, iv))
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    val error = when (errorCode) {
                        BiometricPrompt.ERROR_CANCELED,
                        BiometricPrompt.ERROR_USER_CANCELED,
                        BiometricPrompt.ERROR_NEGATIVE_BUTTON ->
                            BiometricError.Canceled

                        BiometricPrompt.ERROR_LOCKOUT ->
                            BiometricError.Lockout(false)

                        BiometricPrompt.ERROR_LOCKOUT_PERMANENT ->
                            BiometricError.Lockout(true)

                        else ->
                            BiometricError.Other(errorCode, errString.toString())
                    }
                    onError(error)
                }

                override fun onAuthenticationFailed() {
                    // Attempt failed but can retry
                }
            }
        )

        biometricPrompt.authenticate(promptInfo, BiometricPrompt.CryptoObject(cipher))
    }

    // Decrypt with biometrics
    fun authenticateAndDecrypt(
        encryptedResult: EncryptedResult,
        onSuccess: (ByteArray) -> Unit,
        onError: (BiometricError) -> Unit
    ) {
        val secretKey = try {
            getOrCreateKey()
        } catch (e: KeyPermanentlyInvalidatedException) {
            onError(BiometricError.KeyInvalidated)
            return
        }

        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        val spec = GCMParameterSpec(128, encryptedResult.iv)
        cipher.init(Cipher.DECRYPT_MODE, secretKey, spec)

        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Access data")
            .setSubtitle("Confirm biometrics")
            .setNegativeButtonText("Cancel")
            .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
            .build()

        val biometricPrompt = BiometricPrompt(
            activity,
            executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(
                    result: BiometricPrompt.AuthenticationResult
                ) {
                    val authenticatedCipher = result.cryptoObject?.cipher
                        ?: run {
                            onError(BiometricError.CryptoObjectMissing)
                            return
                        }

                    try {
                        val decrypted = authenticatedCipher.doFinal(encryptedResult.data)
                        onSuccess(decrypted)
                    } catch (e: Exception) {
                        onError(BiometricError.DecryptionFailed)
                    }
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    onError(BiometricError.Other(errorCode, errString.toString()))
                }
            }
        )

        biometricPrompt.authenticate(promptInfo, BiometricPrompt.CryptoObject(cipher))
    }
}

data class EncryptedResult(val data: ByteArray, val iv: ByteArray)

sealed class BiometricError {
    object KeyInvalidated : BiometricError()
    object CryptoObjectMissing : BiometricError()
    object DecryptionFailed : BiometricError()
    object Canceled : BiometricError()
    data class Lockout(val permanent: Boolean) : BiometricError()
    data class Other(val code: Int, val message: String) : BiometricError()
}
```

### Error handling
```kotlin
fun handleBiometricError(error: BiometricError) {
    when (error) {
        is BiometricError.KeyInvalidated -> {
            // Biometrics changed - prompt for re-enrollment
            showReEnrollDialog()
        }
        is BiometricError.Lockout -> {
            if (error.permanent) {
                // Offer recovery via device credentials
                showDeviceCredentialFallback()
            } else {
                // Show 30 second wait message
                showTemporaryLockoutMessage()
            }
        }
        is BiometricError.Canceled -> {
            // User canceled - do nothing
        }
        else -> {
            showGenericError()
        }
    }
}
```

---

## Follow-ups

- How do you handle devices with only weak biometrics?
- What is the difference between BIOMETRIC_STRONG and BIOMETRIC_WEAK?
- How do you implement re-enrollment flow when biometrics are invalidated?
- What is the relationship between BiometricPrompt and Credential Manager?

## References

- https://developer.android.com/identity/sign-in/biometric-auth
- https://developer.android.com/reference/androidx/biometric/BiometricPrompt
- https://developer.android.com/reference/androidx/biometric/BiometricManager

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - Android basics

### Related (Same Level)
- [[q-android-keystore--security--hard]] - Keystore for key storage
- [[q-encrypted-shared-preferences--security--medium]] - Encrypted storage
