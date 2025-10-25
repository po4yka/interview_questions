---
id: 20251012-400003
title: Biometric Authentication / Биометрическая аутентификация
aliases: [Biometric Authentication, Биометрическая аутентификация]
topic: android
subtopics:
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
  - q-android-keystore-system--security--medium
  - q-android-security-best-practices--android--medium
  - q-app-security-best-practices--android--medium
created: 2025-10-12
updated: 2025-10-15
tags: [android/permissions, difficulty/medium]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:52:53 pm
---

# Вопрос (RU)
> Как реализовать биометрическую аутентификацию в Android?

# Question (EN)
> How to implement biometric authentication in Android?

---

## Ответ (RU)

### Обзор Биометрической Аутентификации

**Теория**: Биометрическая аутентификация обеспечивает безопасную и удобную аутентификацию пользователей с использованием отпечатка пальца, распознавания лица или радужной оболочки глаза. Библиотека AndroidX Biometric предоставляет единый API для всех версий Android.

**Ключевые компоненты**:
- BiometricPrompt: Единый API для всех типов биометрии
- BiometricManager: Проверка доступности биометрии
- CryptoObject: Интеграция с Android Keystore для шифрования

(См. подробный код и примеры в английской секции)

## Answer (EN)

### Biometric Authentication Overview

**Theory**: Biometric authentication provides secure, convenient user authentication using fingerprint, face, or iris recognition. AndroidX Biometric library offers unified API across Android versions. c-biometric-auth leverages hardware-backed security.

**Key Components**:
- BiometricPrompt: Unified API for all biometric types
- CryptoObject: Ties authentication to [[c-encryption]] operations
- Authenticator Types: BIOMETRIC_STRONG, BIOMETRIC_WEAK, DEVICE_CREDENTIAL

### Basic Implementation

**Minimal Snippet**:
```kotlin
val prompt = BiometricPrompt(this, ContextCompat.getMainExecutor(this), callback)
val info = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Sign in")
    .setAllowedAuthenticators(
        BiometricManager.Authenticators.BIOMETRIC_STRONG or
        BiometricManager.Authenticators.DEVICE_CREDENTIAL
    )
    .build()
prompt.authenticate(info)
```

### Authenticator Types

**BIOMETRIC_STRONG**:
```kotlin
// Theory: Strong biometric for sensitive operations, supports CryptoObject
private fun checkStrongBiometric() {
    val biometricManager = BiometricManager.from(this)
    val canAuthenticate = biometricManager.canAuthenticate(
        BiometricManager.Authenticators.BIOMETRIC_STRONG
    )

    when (canAuthenticate) {
        BiometricManager.BIOMETRIC_SUCCESS -> {
            // Strong biometric available
            showBiometricPrompt()
        }
        BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE -> {
            // No biometric hardware
            showPasswordFallback()
        }
        BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED -> {
            // No biometric enrolled
            showEnrollmentPrompt()
        }
    }
}
```

**BIOMETRIC_WEAK**:
```kotlin
// Theory: Weak biometric for convenience, no CryptoObject support
private fun checkWeakBiometric() {
    val biometricManager = BiometricManager.from(this)
    val canAuthenticate = biometricManager.canAuthenticate(
        BiometricManager.Authenticators.BIOMETRIC_WEAK
    )

    if (canAuthenticate == BiometricManager.BIOMETRIC_SUCCESS) {
        // Weak biometric available (face unlock, etc.)
        showBiometricPrompt()
    }
}
```

**DEVICE_CREDENTIAL**:
```kotlin
// Theory: Device credential (PIN, pattern, password) as fallback
private fun checkDeviceCredential() {
    val biometricManager = BiometricManager.from(this)
    val canAuthenticate = biometricManager.canAuthenticate(
        BiometricManager.Authenticators.DEVICE_CREDENTIAL
    )

    if (canAuthenticate == BiometricManager.BIOMETRIC_SUCCESS) {
        // Device credential available
        showDeviceCredentialPrompt()
    }
}
```

**Combined Authentication**:
```kotlin
// Theory: Best UX with automatic fallback between biometric and device credential
private fun checkCombinedAuthentication() {
    val biometricManager = BiometricManager.from(this)
    val canAuthenticate = biometricManager.canAuthenticate(
        BiometricManager.Authenticators.BIOMETRIC_STRONG or
        BiometricManager.Authenticators.DEVICE_CREDENTIAL
    )

    if (canAuthenticate == BiometricManager.BIOMETRIC_SUCCESS) {
        // Either biometric or device credential available
        showBiometricPrompt()
    }
}
```

### CryptoObject Integration

**Key Generation**:
```kotlin
// Theory: Generate key that requires biometric authentication
private fun generateBiometricKey(): SecretKey {
    val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
    val keyGenParameterSpec = KeyGenParameterSpec.Builder(
        "biometric_key",
        KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
    )
        .setBlockModes(KeyProperties.BLOCK_MODE_CBC)
        .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_PKCS7)
        .setUserAuthenticationRequired(true)
        .setInvalidatedByBiometricEnrollment(true)
        .build()

    keyGenerator.init(keyGenParameterSpec)
    return keyGenerator.generateKey()
}
```

**CryptoObject Usage**:
```kotlin
// Theory: Use CryptoObject to tie authentication to cryptographic operations
private fun authenticateWithCrypto() {
    val secretKey = generateBiometricKey()
    val cipher = Cipher.getInstance("AES/CBC/PKCS7Padding")
    cipher.init(Cipher.ENCRYPT_MODE, secretKey)

    val cryptoObject = BiometricPrompt.CryptoObject(cipher)

    val promptInfo = BiometricPrompt.PromptInfo.Builder()
        .setTitle("Encrypt Data")
        .setSubtitle("Authenticate to encrypt sensitive data")
        .setNegativeButtonText("Cancel")
        .build()

    biometricPrompt.authenticate(promptInfo, cryptoObject)
}
```

### Error Handling

**Comprehensive Error Handling**:
```kotlin
// Theory: Handle all biometric authentication errors gracefully
override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
    super.onAuthenticationError(errorCode, errString)

    when (errorCode) {
        BiometricPrompt.ERROR_HW_UNAVAILABLE -> {
            // Hardware unavailable
            showPasswordFallback()
        }
        BiometricPrompt.ERROR_LOCKOUT -> {
            // Too many attempts, temporary lockout
            showError("Too many attempts. Try again later.")
        }
        BiometricPrompt.ERROR_LOCKOUT_PERMANENT -> {
            // Permanent lockout, require password
            showPasswordFallback()
        }
        BiometricPrompt.ERROR_NO_BIOMETRICS -> {
            // No biometric enrolled
            showEnrollmentPrompt()
        }
        BiometricPrompt.ERROR_USER_CANCELED -> {
            // User canceled
            // Handle gracefully, don't show error
        }
        else -> {
            showError("Authentication error: $errString")
        }
    }
}
```

### Security Best Practices

**Re-authentication**:
```kotlin
// Theory: Require re-authentication for sensitive operations
class SecurityManager {
    private var lastAuthenticationTime = 0L
    private val AUTHENTICATION_TIMEOUT = 5 * 60 * 1000L // 5 minutes

    fun requiresReauthentication(): Boolean {
        return System.currentTimeMillis() - lastAuthenticationTime > AUTHENTICATION_TIMEOUT
    }

    fun onAuthenticationSuccess() {
        lastAuthenticationTime = System.currentTimeMillis()
    }
}
```

**Key Invalidation**:
```kotlin
// Theory: Invalidate keys when biometric enrollment changes
private fun generateSecureKey(): SecretKey {
    val keyGenParameterSpec = KeyGenParameterSpec.Builder(
        "secure_key",
        KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
    )
        .setUserAuthenticationRequired(true)
        .setInvalidatedByBiometricEnrollment(true) // Key invalidated on enrollment change
        .build()

    // Generate key...
}
```

## Follow-ups

- How do you handle biometric enrollment changes?
- What are the differences between BIOMETRIC_STRONG and BIOMETRIC_WEAK?
- How do you implement biometric authentication with encryption?

## References

- https://developer.android.com/training/sign-in/biometric-auth

## Related Questions

### Prerequisites (Easier)
- [[q-android-security-best-practices--android--medium]]
- [[q-android-keystore-system--security--medium]]
- [[q-app-security-best-practices--android--medium]]

### Related (Same Level)
- [[q-android-security-practices-checklist--android--medium]]
- [[q-android14-permissions--android--medium]]
- [[q-android-runtime-art--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]
- [[q-offline-first-architecture--android--hard]]
- [[q-android-modularization--android--medium]]

