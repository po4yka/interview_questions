---
id: android-068
title: Biometric Authentication / Биометрическая аутентификация
aliases: [Biometric Authentication, Биометрическая аутентификация]
topic: android
subtopics:
  - keystore-crypto
  - permissions
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-biometric-authentication
sources: []
created: 2025-10-12
updated: 2025-10-30
tags: [android/keystore-crypto, android/permissions, authentication, biometric, difficulty/medium]
date created: Thursday, October 30th 2025, 11:51:48 am
date modified: Sunday, November 2nd 2025, 1:03:02 pm
---

# Вопрос (RU)
> Как реализовать биометрическую аутентификацию в Android?

# Question (EN)
> How to implement biometric authentication in Android?

---

## Ответ (RU)

**Подход**: AndroidX Biometric предоставляет единый API для биометрии (отпечаток, лицо, радужка) с обратной совместимостью. Ключевые компоненты: `BiometricPrompt` (UI + callbacks), `BiometricManager` (проверка доступности), `CryptoObject` (привязка к Keystore).

### 1. Базовая Реализация

```kotlin
// ✅ BiometricPrompt с fallback на device credential
val executor = ContextCompat.getMainExecutor(context)
val prompt = BiometricPrompt(
    activity,
    executor,
    object : BiometricPrompt.AuthenticationCallback() {
        override fun onAuthenticationSucceeded(
            result: BiometricPrompt.AuthenticationResult
        ) {
            // Успех: cryptoObject?.cipher для шифрования
        }

        override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
            when (errorCode) {
                ERROR_LOCKOUT -> showRetryLater()
                ERROR_LOCKOUT_PERMANENT -> showDeviceCredential()
                ERROR_NO_BIOMETRICS -> navigateToEnrollment()
            }
        }
    }
)

val promptInfo = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Вход в приложение")
    .setSubtitle("Используйте биометрию")
    .setAllowedAuthenticators(BIOMETRIC_STRONG or DEVICE_CREDENTIAL)
    .build()

prompt.authenticate(promptInfo)
```

### 2. Типы Аутентификаторов

**Выбор по назначению**:
- `BIOMETRIC_STRONG` — Class 3 (отпечаток, лицо), поддерживает `CryptoObject`, для криптографии
- `BIOMETRIC_WEAK` — Class 2, НЕ поддерживает `CryptoObject`, для обычной аутентификации
- `DEVICE_CREDENTIAL` — PIN/pattern/password, fallback для биометрии

```kotlin
// ✅ Проверка доступности перед запросом
val manager = BiometricManager.from(context)
when (manager.canAuthenticate(BIOMETRIC_STRONG)) {
    BIOMETRIC_SUCCESS -> showBiometricPrompt()
    BIOMETRIC_ERROR_NONE_ENROLLED -> {
        // Предложить зарегистрировать биометрию
        val enrollIntent = Intent(Settings.ACTION_BIOMETRIC_ENROLL).apply {
            putExtra(EXTRA_BIOMETRIC_AUTHENTICATORS_ALLOWED, BIOMETRIC_STRONG)
        }
        startActivity(enrollIntent)
    }
    else -> showPasswordFallback()
}
```

### 3. Интеграция С Keystore

**Для критичных операций** (шифрование токенов, паролей):

```kotlin
// ✅ Генерация ключа с биометрической привязкой
private fun generateBiometricKey(): SecretKey {
    val keyGen = KeyGenerator.getInstance(KEY_ALGORITHM_AES, "AndroidKeyStore")
    keyGen.init(
        KeyGenParameterSpec.Builder(
            "biometric_key",
            PURPOSE_ENCRYPT or PURPOSE_DECRYPT
        )
            .setBlockModes(BLOCK_MODE_CBC)
            .setEncryptionPaddings(ENCRYPTION_PADDING_PKCS7)
            .setUserAuthenticationRequired(true)
            .setInvalidatedByBiometricEnrollment(true)  // ❗ Ключ инвалидируется при изменении биометрии
            .build()
    )
    return keyGen.generateKey()
}

// ✅ Использование CryptoObject
fun authenticateWithCrypto(dataToEncrypt: ByteArray) {
    val cipher = Cipher.getInstance("AES/CBC/PKCS7Padding")
    cipher.init(Cipher.ENCRYPT_MODE, generateBiometricKey())

    val promptInfo = BiometricPrompt.PromptInfo.Builder()
        .setTitle("Шифрование данных")
        .setNegativeButtonText("Отмена")
        .build()

    biometricPrompt.authenticate(promptInfo, BiometricPrompt.CryptoObject(cipher))
}
```

**Важно**: При `setInvalidatedByBiometricEnrollment(true)` ключ удаляется, если пользователь добавляет/удаляет отпечатки → нужен механизм перегенерации.

### 4. Best Practices

**Обработка ошибок**:
- `ERROR_LOCKOUT` (30 сек) → показать таймер
- `ERROR_LOCKOUT_PERMANENT` → только device credential
- `ERROR_NO_BIOMETRICS` → предложить регистрацию
- `ERROR_USER_CANCELED` → не спамить, запомнить выбор

**UX**:
- Не показывать биометрию каждый раз — timeout (напр., 5 мин после успешной аутентификации)
- Всегда предоставлять альтернативу (PIN/password)
- Для `BIOMETRIC_STRONG or DEVICE_CREDENTIAL` не нужна кнопка Cancel (система покажет fallback)

## Answer (EN)

**Approach**: AndroidX Biometric provides unified API for biometrics (fingerprint, face, iris) with backward compatibility. Key components: `BiometricPrompt` (UI + callbacks), `BiometricManager` (availability check), `CryptoObject` (Keystore binding).

### 1. Basic Implementation

```kotlin
// ✅ BiometricPrompt with device credential fallback
val executor = ContextCompat.getMainExecutor(context)
val prompt = BiometricPrompt(
    activity,
    executor,
    object : BiometricPrompt.AuthenticationCallback() {
        override fun onAuthenticationSucceeded(
            result: BiometricPrompt.AuthenticationResult
        ) {
            // Success: result.cryptoObject?.cipher for encryption
        }

        override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
            when (errorCode) {
                ERROR_LOCKOUT -> showRetryLater()
                ERROR_LOCKOUT_PERMANENT -> showDeviceCredential()
                ERROR_NO_BIOMETRICS -> navigateToEnrollment()
            }
        }
    }
)

val promptInfo = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Sign in to app")
    .setSubtitle("Use biometric credentials")
    .setAllowedAuthenticators(BIOMETRIC_STRONG or DEVICE_CREDENTIAL)
    .build()

prompt.authenticate(promptInfo)
```

### 2. Authenticator Types

**Choose by use case**:
- `BIOMETRIC_STRONG` — Class 3 (fingerprint, face), supports `CryptoObject`, for cryptography
- `BIOMETRIC_WEAK` — Class 2, does NOT support `CryptoObject`, for simple authentication
- `DEVICE_CREDENTIAL` — PIN/pattern/password, fallback for biometrics

```kotlin
// ✅ Check availability before prompting
val manager = BiometricManager.from(context)
when (manager.canAuthenticate(BIOMETRIC_STRONG)) {
    BIOMETRIC_SUCCESS -> showBiometricPrompt()
    BIOMETRIC_ERROR_NONE_ENROLLED -> {
        // Prompt user to enroll biometrics
        val enrollIntent = Intent(Settings.ACTION_BIOMETRIC_ENROLL).apply {
            putExtra(EXTRA_BIOMETRIC_AUTHENTICATORS_ALLOWED, BIOMETRIC_STRONG)
        }
        startActivity(enrollIntent)
    }
    else -> showPasswordFallback()
}
```

### 3. Keystore Integration

**For sensitive operations** (encrypting tokens, passwords):

```kotlin
// ✅ Generate biometric-bound key
private fun generateBiometricKey(): SecretKey {
    val keyGen = KeyGenerator.getInstance(KEY_ALGORITHM_AES, "AndroidKeyStore")
    keyGen.init(
        KeyGenParameterSpec.Builder(
            "biometric_key",
            PURPOSE_ENCRYPT or PURPOSE_DECRYPT
        )
            .setBlockModes(BLOCK_MODE_CBC)
            .setEncryptionPaddings(ENCRYPTION_PADDING_PKCS7)
            .setUserAuthenticationRequired(true)
            .setInvalidatedByBiometricEnrollment(true)  // ❗ Key invalidated on enrollment change
            .build()
    )
    return keyGen.generateKey()
}

// ✅ Use CryptoObject
fun authenticateWithCrypto(dataToEncrypt: ByteArray) {
    val cipher = Cipher.getInstance("AES/CBC/PKCS7Padding")
    cipher.init(Cipher.ENCRYPT_MODE, generateBiometricKey())

    val promptInfo = BiometricPrompt.PromptInfo.Builder()
        .setTitle("Encrypt Data")
        .setNegativeButtonText("Cancel")
        .build()

    biometricPrompt.authenticate(promptInfo, BiometricPrompt.CryptoObject(cipher))
}
```

**Important**: With `setInvalidatedByBiometricEnrollment(true)`, key is deleted if user adds/removes fingerprints → need re-encryption mechanism.

### 4. Best Practices

**Error handling**:
- `ERROR_LOCKOUT` (30 sec) → show timer
- `ERROR_LOCKOUT_PERMANENT` → device credential only
- `ERROR_NO_BIOMETRICS` → offer enrollment
- `ERROR_USER_CANCELED` → don't spam, remember choice

**UX**:
- Don't prompt every time — use timeout (e.g., 5 min after successful auth)
- Always provide alternative (PIN/password)
- For `BIOMETRIC_STRONG or DEVICE_CREDENTIAL`, no Cancel button needed (system shows fallback)

---

## Follow-ups

- What happens to encrypted data when biometric enrollment changes with `setInvalidatedByBiometricEnrollment(true)`?
- How does `BIOMETRIC_STRONG` vs `BIOMETRIC_WEAK` affect security guarantees and CryptoObject support?
- When should you use `setUserAuthenticationRequired(true)` vs `setUserAuthenticationValidityDurationSeconds()`?
- How to implement biometric authentication for multi-user devices?
- What's the recommended strategy for rate limiting authentication attempts beyond system lockout?

## References

- [[c-android-keystore]] — Cryptographic key storage fundamentals
- https://developer.android.com/training/sign-in/biometric-auth
- https://developer.android.com/reference/androidx/biometric/BiometricPrompt

## Related Questions

### Prerequisites (Easier)
- [[q-android-security-best-practices--android--medium]] — Security fundamentals
 — Runtime permissions system

### Related (Same Level)
- [[q-android-keystore-system--security--medium]] — Keystore API and key generation
- [[q-app-security-best-practices--android--medium]] — App-level security patterns

### Advanced (Harder)
 — Advanced encryption patterns
- [[q-android-runtime-internals--android--hard]] — Platform security architecture
