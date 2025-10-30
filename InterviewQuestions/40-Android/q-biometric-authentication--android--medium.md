---
id: 20251012-400003
title: Biometric Authentication / Биометрическая аутентификация
aliases: ["Biometric Authentication", "Биометрическая аутентификация"]
topic: android
subtopics: [permissions, keystore-crypto]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - q-android-keystore-system--security--medium
  - q-android-security-best-practices--android--medium
  - q-app-security-best-practices--android--medium
sources: []
created: 2025-10-12
updated: 2025-10-29
tags: [android/permissions, android/keystore-crypto, biometric, authentication, difficulty/medium]
---

# Вопрос (RU)
> Как реализовать биометрическую аутентификацию в Android?

# Question (EN)
> How to implement biometric authentication in Android?

---

## Ответ (RU)

### Обзор

AndroidX Biometric предоставляет единый API для биометрической аутентификации (отпечаток, лицо, радужка) с поддержкой всех версий Android.

**Компоненты**: `BiometricPrompt` (UI + callbacks), `BiometricManager` (проверка доступности), `CryptoObject` (привязка к Keystore).

### Базовая Реализация

```kotlin
// ✅ Setup с fallback на device credential
val prompt = BiometricPrompt(
    this, ContextCompat.getMainExecutor(this),
    object : BiometricPrompt.AuthenticationCallback() {
        override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
            // Успешная аутентификация
        }
        override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
            // Обработка ошибок
        }
    }
)

val promptInfo = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Вход в приложение")
    .setAllowedAuthenticators(BIOMETRIC_STRONG or DEVICE_CREDENTIAL)
    .build()

prompt.authenticate(promptInfo)
```

### Типы Аутентификаторов

```kotlin
// ✅ Проверка доступности BIOMETRIC_STRONG (для чувствительных операций)
val manager = BiometricManager.from(this)
when (manager.canAuthenticate(BIOMETRIC_STRONG)) {
    BIOMETRIC_SUCCESS -> showBiometricPrompt()
    BIOMETRIC_ERROR_NONE_ENROLLED -> showEnrollmentPrompt()
    else -> showPasswordFallback()
}

// ❌ BIOMETRIC_WEAK — не поддерживает CryptoObject
val authenticators = BIOMETRIC_WEAK or DEVICE_CREDENTIAL
```

### Интеграция с Keystore

```kotlin
// ✅ Генерация ключа, привязанного к биометрии
private fun generateBiometricKey(): SecretKey {
    val keyGen = KeyGenerator.getInstance(KEY_ALGORITHM_AES, "AndroidKeyStore")
    keyGen.init(
        KeyGenParameterSpec.Builder("biometric_key", PURPOSE_ENCRYPT or PURPOSE_DECRYPT)
            .setBlockModes(BLOCK_MODE_CBC)
            .setEncryptionPaddings(ENCRYPTION_PADDING_PKCS7)
            .setUserAuthenticationRequired(true)
            .setInvalidatedByBiometricEnrollment(true) // Инвалидация при изменении
            .build()
    )
    return keyGen.generateKey()
}

// ✅ Использование CryptoObject для шифрования
private fun authenticateWithCrypto() {
    val cipher = Cipher.getInstance("AES/CBC/PKCS7Padding")
    cipher.init(Cipher.ENCRYPT_MODE, generateBiometricKey())

    biometricPrompt.authenticate(
        BiometricPrompt.PromptInfo.Builder()
            .setTitle("Шифрование данных")
            .setNegativeButtonText("Отмена")
            .build(),
        BiometricPrompt.CryptoObject(cipher)
    )
}
```

### Обработка Ошибок

```kotlin
// ✅ Обработка основных сценариев
override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
    when (errorCode) {
        ERROR_LOCKOUT -> showError("Слишком много попыток")
        ERROR_LOCKOUT_PERMANENT -> showPasswordFallback()
        ERROR_NO_BIOMETRICS -> showEnrollmentPrompt()
        ERROR_USER_CANCELED -> { /* Пользователь отменил */ }
    }
}
```

## Answer (EN)

### Overview

AndroidX Biometric provides unified API for biometric authentication (fingerprint, face, iris) with backward compatibility across Android versions.

**Components**: `BiometricPrompt` (UI + callbacks), `BiometricManager` (availability check), `CryptoObject` (Keystore binding).

### Basic Implementation

```kotlin
// ✅ Setup with device credential fallback
val prompt = BiometricPrompt(
    this, ContextCompat.getMainExecutor(this),
    object : BiometricPrompt.AuthenticationCallback() {
        override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
            // Successful authentication
        }
        override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
            // Handle errors
        }
    }
)

val promptInfo = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Sign in")
    .setAllowedAuthenticators(BIOMETRIC_STRONG or DEVICE_CREDENTIAL)
    .build()

prompt.authenticate(promptInfo)
```

### Authenticator Types

```kotlin
// ✅ Check BIOMETRIC_STRONG availability (for sensitive operations)
val manager = BiometricManager.from(this)
when (manager.canAuthenticate(BIOMETRIC_STRONG)) {
    BIOMETRIC_SUCCESS -> showBiometricPrompt()
    BIOMETRIC_ERROR_NONE_ENROLLED -> showEnrollmentPrompt()
    else -> showPasswordFallback()
}

// ❌ BIOMETRIC_WEAK — doesn't support CryptoObject
val authenticators = BIOMETRIC_WEAK or DEVICE_CREDENTIAL
```

### Keystore Integration

```kotlin
// ✅ Generate biometric-bound key
private fun generateBiometricKey(): SecretKey {
    val keyGen = KeyGenerator.getInstance(KEY_ALGORITHM_AES, "AndroidKeyStore")
    keyGen.init(
        KeyGenParameterSpec.Builder("biometric_key", PURPOSE_ENCRYPT or PURPOSE_DECRYPT)
            .setBlockModes(BLOCK_MODE_CBC)
            .setEncryptionPaddings(ENCRYPTION_PADDING_PKCS7)
            .setUserAuthenticationRequired(true)
            .setInvalidatedByBiometricEnrollment(true) // Invalidate on enrollment change
            .build()
    )
    return keyGen.generateKey()
}

// ✅ Use CryptoObject for encryption
private fun authenticateWithCrypto() {
    val cipher = Cipher.getInstance("AES/CBC/PKCS7Padding")
    cipher.init(Cipher.ENCRYPT_MODE, generateBiometricKey())

    biometricPrompt.authenticate(
        BiometricPrompt.PromptInfo.Builder()
            .setTitle("Encrypt Data")
            .setNegativeButtonText("Cancel")
            .build(),
        BiometricPrompt.CryptoObject(cipher)
    )
}
```

### Error Handling

```kotlin
// ✅ Handle main scenarios
override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
    when (errorCode) {
        ERROR_LOCKOUT -> showError("Too many attempts")
        ERROR_LOCKOUT_PERMANENT -> showPasswordFallback()
        ERROR_NO_BIOMETRICS -> showEnrollmentPrompt()
        ERROR_USER_CANCELED -> { /* User canceled */ }
    }
}
```

---

## Follow-ups

- What happens to encrypted data when biometric enrollment changes with `setInvalidatedByBiometricEnrollment(true)`?
- How does `BIOMETRIC_STRONG` vs `BIOMETRIC_WEAK` affect security model and CryptoObject support?
- When should you use `setUserAuthenticationRequired(true)` vs `setUserAuthenticationValidityDurationSeconds()`?
- How to handle biometric authentication on multi-user devices?
- What's the recommended strategy for rate limiting authentication attempts beyond system lockout?

## References

- Official AndroidX Biometric library documentation
- Android Keystore System guide
- [[q-android-keystore-system--security--medium]]
- [[q-android-security-best-practices--android--medium]]
- [[q-app-security-best-practices--android--medium]]

## Related Questions

### Prerequisites (Easier)
- [[q-android-security-best-practices--android--medium]] — Security fundamentals
- [[q-app-security-best-practices--android--medium]] — App security patterns
- [[q-android14-permissions--android--medium]] — Runtime permissions

### Related (Same Level)
- [[q-android-keystore-system--security--medium]] — Cryptographic key storage
- [[q-runtime-permissions-android--android--medium]] — Permissions system

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] — Platform security architecture
- [[q-secure-storage-encryption--android--hard]] — Advanced encryption patterns
