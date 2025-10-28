---
id: 20251012-400003
title: Biometric Authentication / Биометрическая аутентификация
aliases: [Biometric Authentication, Биометрическая аутентификация]
topic: android
subtopics: [permissions, security]
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
updated: 2025-10-28
tags: [android/permissions, android/security, biometric, authentication, difficulty/medium]
---

# Вопрос (RU)
> Как реализовать биометрическую аутентификацию в Android?

# Question (EN)
> How to implement biometric authentication in Android?

---

## Ответ (RU)

### Обзор

Биометрическая аутентификация обеспечивает безопасную и удобную аутентификацию пользователей через отпечаток пальца, распознавание лица или радужной оболочки. AndroidX Biometric предоставляет единый API для всех версий Android.

**Ключевые компоненты**:
- `BiometricPrompt` — единый API для биометрии
- `BiometricManager` — проверка доступности
- `CryptoObject` — интеграция с Android Keystore

### Базовая Реализация

```kotlin
// ✅ Минимальный setup с fallback на device credential
val prompt = BiometricPrompt(
    this,
    ContextCompat.getMainExecutor(this),
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
    .setAllowedAuthenticators(
        BiometricManager.Authenticators.BIOMETRIC_STRONG or
        BiometricManager.Authenticators.DEVICE_CREDENTIAL
    )
    .build()

prompt.authenticate(promptInfo)
```

### Типы Аутентификаторов

**BIOMETRIC_STRONG** — для чувствительных операций, поддерживает CryptoObject:
```kotlin
// ✅ Проверка доступности сильной биометрии
val biometricManager = BiometricManager.from(this)
when (biometricManager.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG)) {
    BiometricManager.BIOMETRIC_SUCCESS -> showBiometricPrompt()
    BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED -> showEnrollmentPrompt()
    else -> showPasswordFallback()
}
```

**Комбинированная аутентификация** — лучший UX с автоматическим fallback:
```kotlin
// ✅ Биометрия или device credential
val authenticators = BiometricManager.Authenticators.BIOMETRIC_STRONG or
                     BiometricManager.Authenticators.DEVICE_CREDENTIAL
```

### Интеграция с Шифрованием

```kotlin
// ✅ Генерация ключа, привязанного к биометрии
private fun generateBiometricKey(): SecretKey {
    val keyGenerator = KeyGenerator.getInstance(
        KeyProperties.KEY_ALGORITHM_AES,
        "AndroidKeyStore"
    )

    keyGenerator.init(
        KeyGenParameterSpec.Builder(
            "biometric_key",
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_CBC)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_PKCS7)
            .setUserAuthenticationRequired(true)
            .setInvalidatedByBiometricEnrollment(true) // Инвалидация при изменении
            .build()
    )

    return keyGenerator.generateKey()
}

// ✅ Использование с CryptoObject
private fun authenticateWithCrypto() {
    val cipher = Cipher.getInstance("AES/CBC/PKCS7Padding")
    cipher.init(Cipher.ENCRYPT_MODE, generateBiometricKey())

    val cryptoObject = BiometricPrompt.CryptoObject(cipher)
    val promptInfo = BiometricPrompt.PromptInfo.Builder()
        .setTitle("Шифрование данных")
        .setNegativeButtonText("Отмена")
        .build()

    biometricPrompt.authenticate(promptInfo, cryptoObject)
}
```

### Обработка Ошибок

```kotlin
// ✅ Обработка основных сценариев
override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
    when (errorCode) {
        BiometricPrompt.ERROR_LOCKOUT ->
            showError("Слишком много попыток. Повторите позже.")
        BiometricPrompt.ERROR_LOCKOUT_PERMANENT ->
            showPasswordFallback()
        BiometricPrompt.ERROR_NO_BIOMETRICS ->
            showEnrollmentPrompt()
        BiometricPrompt.ERROR_USER_CANCELED ->
            { /* Пользователь отменил */ }
        else ->
            showError("Ошибка аутентификации: $errString")
    }
}
```

### Security Best Practices

```kotlin
// ✅ Re-authentication timeout для критичных операций
class SecurityManager {
    private var lastAuthTime = 0L
    private val AUTH_TIMEOUT = 5 * 60 * 1000L // 5 минут

    fun requiresReauth(): Boolean =
        System.currentTimeMillis() - lastAuthTime > AUTH_TIMEOUT
}
```

## Answer (EN)

### Overview

Biometric authentication provides secure, convenient user authentication using fingerprint, face, or iris recognition. AndroidX Biometric library offers a unified API across Android versions.

**Key Components**:
- `BiometricPrompt` — unified API for all biometric types
- `BiometricManager` — availability checking
- `CryptoObject` — integration with Android Keystore

### Basic Implementation

```kotlin
// ✅ Minimal setup with device credential fallback
val prompt = BiometricPrompt(
    this,
    ContextCompat.getMainExecutor(this),
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
    .setAllowedAuthenticators(
        BiometricManager.Authenticators.BIOMETRIC_STRONG or
        BiometricManager.Authenticators.DEVICE_CREDENTIAL
    )
    .build()

prompt.authenticate(promptInfo)
```

### Authenticator Types

**BIOMETRIC_STRONG** — for sensitive operations, supports CryptoObject:
```kotlin
// ✅ Check strong biometric availability
val biometricManager = BiometricManager.from(this)
when (biometricManager.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG)) {
    BiometricManager.BIOMETRIC_SUCCESS -> showBiometricPrompt()
    BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED -> showEnrollmentPrompt()
    else -> showPasswordFallback()
}
```

**Combined Authentication** — best UX with automatic fallback:
```kotlin
// ✅ Biometric or device credential
val authenticators = BiometricManager.Authenticators.BIOMETRIC_STRONG or
                     BiometricManager.Authenticators.DEVICE_CREDENTIAL
```

### Encryption Integration

```kotlin
// ✅ Generate biometric-bound key
private fun generateBiometricKey(): SecretKey {
    val keyGenerator = KeyGenerator.getInstance(
        KeyProperties.KEY_ALGORITHM_AES,
        "AndroidKeyStore"
    )

    keyGenerator.init(
        KeyGenParameterSpec.Builder(
            "biometric_key",
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_CBC)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_PKCS7)
            .setUserAuthenticationRequired(true)
            .setInvalidatedByBiometricEnrollment(true) // Invalidate on enrollment change
            .build()
    )

    return keyGenerator.generateKey()
}

// ✅ Use with CryptoObject
private fun authenticateWithCrypto() {
    val cipher = Cipher.getInstance("AES/CBC/PKCS7Padding")
    cipher.init(Cipher.ENCRYPT_MODE, generateBiometricKey())

    val cryptoObject = BiometricPrompt.CryptoObject(cipher)
    val promptInfo = BiometricPrompt.PromptInfo.Builder()
        .setTitle("Encrypt Data")
        .setNegativeButtonText("Cancel")
        .build()

    biometricPrompt.authenticate(promptInfo, cryptoObject)
}
```

### Error Handling

```kotlin
// ✅ Handle main scenarios
override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
    when (errorCode) {
        BiometricPrompt.ERROR_LOCKOUT ->
            showError("Too many attempts. Try again later.")
        BiometricPrompt.ERROR_LOCKOUT_PERMANENT ->
            showPasswordFallback()
        BiometricPrompt.ERROR_NO_BIOMETRICS ->
            showEnrollmentPrompt()
        BiometricPrompt.ERROR_USER_CANCELED ->
            { /* User canceled */ }
        else ->
            showError("Authentication error: $errString")
    }
}
```

### Security Best Practices

```kotlin
// ✅ Re-authentication timeout for critical operations
class SecurityManager {
    private var lastAuthTime = 0L
    private val AUTH_TIMEOUT = 5 * 60 * 1000L // 5 minutes

    fun requiresReauth(): Boolean =
        System.currentTimeMillis() - lastAuthTime > AUTH_TIMEOUT
}
```

---

## Follow-ups

- How does `setInvalidatedByBiometricEnrollment(true)` affect key lifecycle?
- What's the difference between `BIOMETRIC_STRONG` and `BIOMETRIC_WEAK` in terms of security guarantees?
- How do you handle biometric authentication in multi-user devices?
- What happens to encrypted data when biometric enrollment changes?
- How to implement rate limiting for authentication attempts?

## References

- AndroidX Biometric library official documentation
- Android Keystore System guide
- [[q-android-keystore-system--security--medium]]
- [[q-android-security-best-practices--android--medium]]

## Related Questions

### Prerequisites (Easier)
- [[q-android-security-best-practices--android--medium]] — Security fundamentals
- [[q-app-security-best-practices--android--medium]] — App-level security patterns

### Related (Same Level)
- [[q-android-keystore-system--security--medium]] — Cryptographic key storage
- [[q-android14-permissions--android--medium]] — Runtime permissions system

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] — Platform security architecture
- [[q-offline-first-architecture--android--hard]] — Secure offline data handling
