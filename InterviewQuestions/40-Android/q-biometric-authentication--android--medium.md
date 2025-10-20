---
id: 20251012-400003
title: Biometric Authentication / Биометрическая аутентификация
aliases: [Biometric Authentication, Биометрическая аутентификация]
topic: android
subtopics: [security, biometric, authentication]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-keystore-system--security--medium, q-android-security-best-practices--android--medium, q-app-security-best-practices--security--medium]
created: 2025-10-12
updated: 2025-10-15
tags: [android/security, android/biometric, android/authentication, security, biometric, authentication, difficulty/medium]
---
# Question (EN)
> How do you implement biometric authentication in Android? What are BiometricPrompt, CryptoObject, and different authenticator types? How do you handle fallback authentication?

# Вопрос (RU)
> Как реализовать биометрическую аутентификацию в Android? Что такое BiometricPrompt, CryptoObject и различные типы аутентификаторов? Как обрабатывать резервную аутентификацию?

---

## Answer (EN)

### Biometric Authentication Overview

**Theory**: Biometric authentication provides secure, convenient user authentication using fingerprint, face, or iris recognition. AndroidX Biometric library offers unified API across Android versions.

**Key Components**:
- BiometricPrompt: Unified API for all biometric types
- CryptoObject: Ties authentication to cryptographic operations
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

## Ответ (RU)

### Обзор биометрической аутентификации

**Теория**: Биометрическая аутентификация обеспечивает безопасную и удобную аутентификацию пользователя с использованием отпечатка пальца, лица или радужной оболочки. Библиотека AndroidX Biometric предоставляет унифицированный API для разных версий Android.

**Ключевые компоненты**:
- BiometricPrompt: Унифицированный API для всех типов биометрии
- CryptoObject: Привязывает аутентификацию к криптографическим операциям
- Типы аутентификаторов: BIOMETRIC_STRONG, BIOMETRIC_WEAK, DEVICE_CREDENTIAL

### Базовая реализация

**Минимальный сниппет**:
```kotlin
val prompt = BiometricPrompt(this, ContextCompat.getMainExecutor(this), callback)
val info = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Вход")
    .setAllowedAuthenticators(
        BiometricManager.Authenticators.BIOMETRIC_STRONG or
        BiometricManager.Authenticators.DEVICE_CREDENTIAL
    )
    .build()
prompt.authenticate(info)
```

### Типы аутентификаторов

**BIOMETRIC_STRONG**:
```kotlin
// Теория: Сильная биометрия для чувствительных операций, поддерживает CryptoObject
private fun checkStrongBiometric() {
    val biometricManager = BiometricManager.from(this)
    val canAuthenticate = biometricManager.canAuthenticate(
        BiometricManager.Authenticators.BIOMETRIC_STRONG
    )

    when (canAuthenticate) {
        BiometricManager.BIOMETRIC_SUCCESS -> {
            // Сильная биометрия доступна
            showBiometricPrompt()
        }
        BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE -> {
            // Нет биометрического оборудования
            showPasswordFallback()
        }
        BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED -> {
            // Биометрия не зарегистрирована
            showEnrollmentPrompt()
        }
    }
}
```

**BIOMETRIC_WEAK**:
```kotlin
// Теория: Слабая биометрия для удобства, без поддержки CryptoObject
private fun checkWeakBiometric() {
    val biometricManager = BiometricManager.from(this)
    val canAuthenticate = biometricManager.canAuthenticate(
        BiometricManager.Authenticators.BIOMETRIC_WEAK
    )

    if (canAuthenticate == BiometricManager.BIOMETRIC_SUCCESS) {
        // Слабая биометрия доступна (разблокировка по лицу и т.д.)
        showBiometricPrompt()
    }
}
```

**DEVICE_CREDENTIAL**:
```kotlin
// Теория: Учетные данные устройства (PIN, графический ключ, пароль) как резерв
private fun checkDeviceCredential() {
    val biometricManager = BiometricManager.from(this)
    val canAuthenticate = biometricManager.canAuthenticate(
        BiometricManager.Authenticators.DEVICE_CREDENTIAL
    )

    if (canAuthenticate == BiometricManager.BIOMETRIC_SUCCESS) {
        // Учетные данные устройства доступны
        showDeviceCredentialPrompt()
    }
}
```

**Комбинированная аутентификация**:
```kotlin
// Теория: Лучший UX с автоматическим переключением между биометрией и учетными данными устройства
private fun checkCombinedAuthentication() {
    val biometricManager = BiometricManager.from(this)
    val canAuthenticate = biometricManager.canAuthenticate(
        BiometricManager.Authenticators.BIOMETRIC_STRONG or
        BiometricManager.Authenticators.DEVICE_CREDENTIAL
    )

    if (canAuthenticate == BiometricManager.BIOMETRIC_SUCCESS) {
        // Доступна либо биометрия, либо учетные данные устройства
        showBiometricPrompt()
    }
}
```

### Интеграция с CryptoObject

**Генерация ключа**:
```kotlin
// Теория: Генерировать ключ, требующий биометрической аутентификации
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

**Использование CryptoObject**:
```kotlin
// Теория: Использовать CryptoObject для привязки аутентификации к криптографическим операциям
private fun authenticateWithCrypto() {
    val secretKey = generateBiometricKey()
    val cipher = Cipher.getInstance("AES/CBC/PKCS7Padding")
    cipher.init(Cipher.ENCRYPT_MODE, secretKey)

    val cryptoObject = BiometricPrompt.CryptoObject(cipher)

    val promptInfo = BiometricPrompt.PromptInfo.Builder()
        .setTitle("Шифрование данных")
        .setSubtitle("Аутентифицируйтесь для шифрования чувствительных данных")
        .setNegativeButtonText("Отмена")
        .build()

    biometricPrompt.authenticate(promptInfo, cryptoObject)
}
```

### Обработка ошибок

**Комплексная обработка ошибок**:
```kotlin
// Теория: Корректно обрабатывать все ошибки биометрической аутентификации
override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
    super.onAuthenticationError(errorCode, errString)

    when (errorCode) {
        BiometricPrompt.ERROR_HW_UNAVAILABLE -> {
            // Оборудование недоступно
            showPasswordFallback()
        }
        BiometricPrompt.ERROR_LOCKOUT -> {
            // Слишком много попыток, временная блокировка
            showError("Слишком много попыток. Попробуйте позже.")
        }
        BiometricPrompt.ERROR_LOCKOUT_PERMANENT -> {
            // Постоянная блокировка, требуется пароль
            showPasswordFallback()
        }
        BiometricPrompt.ERROR_NO_BIOMETRICS -> {
            // Биометрия не зарегистрирована
            showEnrollmentPrompt()
        }
        BiometricPrompt.ERROR_USER_CANCELED -> {
            // Пользователь отменил
            // Обработать корректно, не показывать ошибку
        }
        else -> {
            showError("Ошибка аутентификации: $errString")
        }
    }
}
```

### Лучшие практики безопасности

**Повторная аутентификация**:
```kotlin
// Теория: Требовать повторную аутентификацию для чувствительных операций
class SecurityManager {
    private var lastAuthenticationTime = 0L
    private val AUTHENTICATION_TIMEOUT = 5 * 60 * 1000L // 5 минут

    fun requiresReauthentication(): Boolean {
        return System.currentTimeMillis() - lastAuthenticationTime > AUTHENTICATION_TIMEOUT
    }

    fun onAuthenticationSuccess() {
        lastAuthenticationTime = System.currentTimeMillis()
    }
}
```

**Инвалидация ключей**:
```kotlin
// Теория: Инвалидировать ключи при изменении биометрической регистрации
private fun generateSecureKey(): SecretKey {
    val keyGenParameterSpec = KeyGenParameterSpec.Builder(
        "secure_key",
        KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
    )
        .setUserAuthenticationRequired(true)
        .setInvalidatedByBiometricEnrollment(true) // Ключ инвалидируется при изменении регистрации
        .build()

    // Генерировать ключ...
}
```

---

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
- [[q-app-security-best-practices--security--medium]]

### Related (Same Level)
- [[q-android-security-practices-checklist--android--medium]]
- [[q-android14-permissions--permissions--medium]]
- [[q-android-runtime-art--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]
- [[q-offline-first-architecture--android--hard]]
- [[q-android-modularization--android--medium]]
