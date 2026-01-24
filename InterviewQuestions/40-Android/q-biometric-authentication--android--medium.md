---
id: android-068
title: Biometric Authentication / Биометрическая аутентификация
aliases:
- Biometric Authentication
- Биометрическая аутентификация
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
status: draft
moc: moc-android
related:
- c-android-keystore
- q-android-security-best-practices--android--medium
- q-android-security-practices-checklist--android--medium
- q-app-security-best-practices--android--medium
sources:
- https://developer.android.com/training/sign-in/biometric-auth
created: 2024-10-12
updated: 2025-11-11
tags:
- android/keystore-crypto
- android/permissions
- authentication
- biometric
- difficulty/medium
anki_cards:
- slug: android-068-0-en
  language: en
  anki_id: 1768364992150
  synced_at: '2026-01-23T16:45:06.301787'
- slug: android-068-0-ru
  language: ru
  anki_id: 1768364992173
  synced_at: '2026-01-23T16:45:06.302657'
---
# Вопрос (RU)
> Как реализовать биометрическую аутентификацию в Android?

# Question (EN)
> How to implement biometric authentication in Android?

---

## Ответ (RU)

**Подход**: AndroidX Biometric предоставляет единый API для биометрии (отпечаток, лицо, радужка) с обратной совместимостью. Ключевые компоненты: `BiometricPrompt` (UI + callbacks), `BiometricManager` (проверка доступности), `CryptoObject` (привязка к Keystore, см. [[c-android-keystore]]).

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
            // Успех: result.cryptoObject?.cipher для шифрования
        }

        override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
            when (errorCode) {
                BiometricPrompt.ERROR_LOCKOUT -> showRetryLater()
                BiometricPrompt.ERROR_LOCKOUT_PERMANENT -> showDeviceCredential()
                BiometricPrompt.ERROR_NO_BIOMETRICS -> navigateToEnrollment()
            }
        }
    }
)

val promptInfo = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Вход в приложение")
    .setSubtitle("Используйте биометрию")
    .setAllowedAuthenticators(
        BiometricManager.Authenticators.BIOMETRIC_STRONG or
            BiometricManager.Authenticators.DEVICE_CREDENTIAL
    )
    .build()

prompt.authenticate(promptInfo)
```

### 2. Типы Аутентификаторов

**Выбор по назначению**:
- `BIOMETRIC_STRONG` — Class 3 (отпечаток, лицо), подходит для использования с `CryptoObject` и привязки ключей, когда требуются сильные гарантии.
- `BIOMETRIC_WEAK` — Class 2, предназначен для менее критичных сценариев; ключи, защищающие высокоценные секреты, должны опираться на `BIOMETRIC_STRONG` и/или `DEVICE_CREDENTIAL`, а не только на слабую биометрию.
- `DEVICE_CREDENTIAL` — PIN/pattern/password, системный credential, может использоваться как fallback или единственный метод.

```kotlin
// ✅ Проверка доступности перед запросом
val manager = BiometricManager.from(context)
when (manager.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG)) {
    BiometricManager.BIOMETRIC_SUCCESS -> showBiometricPrompt()
    BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED -> {
        // Предложить зарегистрировать биометрию
        val enrollIntent = Intent(Settings.ACTION_BIOMETRIC_ENROLL).apply {
            putExtra(
                Settings.EXTRA_BIOMETRIC_AUTHENTICATORS_ALLOWED,
                BiometricManager.Authenticators.BIOMETRIC_STRONG
            )
        }
        startActivity(enrollIntent)
    }
    else -> showPasswordFallback()
}
```

### 3. Интеграция С Keystore

**Для критичных операций** (шифрование токенов, паролей):

```kotlin
// ✅ Генерация ключа с биометрической / credential-привязкой
// (обычно вызывается один раз; далее ключ загружается по alias для повторного использования)
private fun generateBiometricKey(): SecretKey {
    val keyGen = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
    keyGen.init(
        KeyGenParameterSpec.Builder(
            "biometric_key",
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            // Для новых реализаций предпочтительно использовать AES/GCM:
            // .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            // .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setBlockModes(KeyProperties.BLOCK_MODE_CBC)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_PKCS7)
            .setUserAuthenticationRequired(true)
            // Привязка к аутентификации пользователя (биометрия/credential) согласно конфигурации
            .setInvalidatedByBiometricEnrollment(true)  // ❗ Ключ инвалидируется при изменении биометрии (на поддерживаемых версиях)
            .build()
    )
    return keyGen.generateKey()
}

// ✅ Использование CryptoObject
fun authenticateWithCrypto(dataToEncrypt: ByteArray) {
    // В реальных реализациях нужно загружать существующий ключ из Android Keystore по alias,
    // а не генерировать новый при каждом вызове.
    val secretKey = generateBiometricKey()
    val cipher = Cipher.getInstance("AES/CBC/PKCS7Padding")
    cipher.init(Cipher.ENCRYPT_MODE, secretKey)

    val promptInfo = BiometricPrompt.PromptInfo.Builder()
        .setTitle("Шифрование данных")
        // При использовании только биометрии требуется negative button.
        // При включении DEVICE_CREDENTIAL в allowedAuthenticators
        // negative button НЕ задается.
        .setNegativeButtonText("Отмена")
        .build()

    val biometricPrompt = BiometricPrompt(
        activity,
        ContextCompat.getMainExecutor(context),
        object : BiometricPrompt.AuthenticationCallback() {}
    )

    biometricPrompt.authenticate(promptInfo, BiometricPrompt.CryptoObject(cipher))
}
```

**Важно**:
- При `setInvalidatedByBiometricEnrollment(true)` ключ удаляется, если пользователь изменяет набор биометрических шаблонов → нужен механизм перегенерации ключа и повторного шифрования данных.
- Ключи, защищающие чувствительные данные, следует конфигурировать так, чтобы требовать `BIOMETRIC_STRONG` и/или `DEVICE_CREDENTIAL` (через `setAllowedAuthenticators`) и не полагаться только на `BIOMETRIC_WEAK`.

### 4. Рекомендации (Best Practices)

**Обработка ошибок**:
- `ERROR_LOCKOUT` (временная блокировка, продолжительность задается системой) → показать сообщение/подсказку и не делать жестких предположений о точном времени.
- `ERROR_LOCKOUT_PERMANENT` → предложить использовать device credential.
- `ERROR_NO_BIOMETRICS` → предложить регистрацию.
- `ERROR_USER_CANCELED` → не спамить диалогом, учитывать выбор пользователя.

**UX**:
- Не показывать запрос биометрии на каждом экране — использовать таймаут (например, несколько минут после успешной аутентификации, в зависимости от рисков).
- Всегда предоставлять альтернативу (PIN/password или device credential), если это допускается бизнес-требованиями.
- Для конфигурации `BIOMETRIC_STRONG or DEVICE_CREDENTIAL` в `setAllowedAuthenticators` не вызывать `setNegativeButtonText()`: системный UI сам обрабатывает отмену и fallback.

## Answer (EN)

**Approach**: AndroidX Biometric provides a unified API for biometrics (fingerprint, face, iris) with backward compatibility. Key components: `BiometricPrompt` (UI + callbacks), `BiometricManager` (availability check), `CryptoObject` (Keystore binding, see [[c-android-keystore]]).

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
                BiometricPrompt.ERROR_LOCKOUT -> showRetryLater()
                BiometricPrompt.ERROR_LOCKOUT_PERMANENT -> showDeviceCredential()
                BiometricPrompt.ERROR_NO_BIOMETRICS -> navigateToEnrollment()
            }
        }
    }
)

val promptInfo = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Sign in to app")
    .setSubtitle("Use biometric credentials")
    .setAllowedAuthenticators(
        BiometricManager.Authenticators.BIOMETRIC_STRONG or
            BiometricManager.Authenticators.DEVICE_CREDENTIAL
    )
    .build()

prompt.authenticate(promptInfo)
```

### 2. Authenticator Types

**Choose by use case**:
- `BIOMETRIC_STRONG` — Class 3 (fingerprint, face), suitable for use with `CryptoObject` and key binding when strong guarantees are required.
- `BIOMETRIC_WEAK` — Class 2, for less sensitive scenarios; keys that require strong user verification should rely on `BIOMETRIC_STRONG` (or device credential), not only on weak biometrics.
- `DEVICE_CREDENTIAL` — PIN/pattern/password, system credential that can serve as fallback or primary method.

```kotlin
// ✅ Check availability before prompting
val manager = BiometricManager.from(context)
when (manager.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG)) {
    BiometricManager.BIOMETRIC_SUCCESS -> showBiometricPrompt()
    BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED -> {
        // Prompt user to enroll biometrics
        val enrollIntent = Intent(Settings.ACTION_BIOMETRIC_ENROLL).apply {
            putExtra(
                Settings.EXTRA_BIOMETRIC_AUTHENTICATORS_ALLOWED,
                BiometricManager.Authenticators.BIOMETRIC_STRONG
            )
        }
        startActivity(enrollIntent)
    }
    else -> showPasswordFallback()
}
```

### 3. Keystore Integration

**For sensitive operations** (encrypting tokens, passwords):

```kotlin
// ✅ Generate a key bound to biometric / device credential authentication
// (typically called once; key is then loaded by alias for later use)
private fun generateBiometricKey(): SecretKey {
    val keyGen = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
    keyGen.init(
        KeyGenParameterSpec.Builder(
            "biometric_key",
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            // Prefer AES/GCM for new designs:
            // .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            // .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setBlockModes(KeyProperties.BLOCK_MODE_CBC)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_PKCS7)
            .setUserAuthenticationRequired(true)
            // Tied to user authentication (biometrics/credential) per configuration
            .setInvalidatedByBiometricEnrollment(true)  // ❗ Key invalidated on biometric enrollment changes (on supported versions)
            .build()
    )
    return keyGen.generateKey()
}

// ✅ Use CryptoObject
fun authenticateWithCrypto(dataToEncrypt: ByteArray) {
    // In real implementations, load the existing key from Android Keystore by alias
    // instead of generating a new one on every call.
    val secretKey = generateBiometricKey()
    val cipher = Cipher.getInstance("AES/CBC/PKCS7Padding")
    cipher.init(Cipher.ENCRYPT_MODE, secretKey)

    val promptInfo = BiometricPrompt.PromptInfo.Builder()
        .setTitle("Encrypt Data")
        // When ONLY biometric authenticators are allowed,
        // negative button text is required.
        // When DEVICE_CREDENTIAL is included in allowedAuthenticators,
        // negative button must NOT be set.
        .setNegativeButtonText("Cancel")
        .build()

    val biometricPrompt = BiometricPrompt(
        activity,
        ContextCompat.getMainExecutor(context),
        object : BiometricPrompt.AuthenticationCallback() {}
    )

    biometricPrompt.authenticate(promptInfo, BiometricPrompt.CryptoObject(cipher))
}
```

**Important**:
- With `setInvalidatedByBiometricEnrollment(true)`, the key is deleted if the user changes enrolled biometrics on supported versions → you must handle key regeneration and data re-encryption.
- Keys protecting sensitive data should be configured so that only `BIOMETRIC_STRONG` and/or `DEVICE_CREDENTIAL` (set via `setAllowedAuthenticators`) satisfy the authentication requirement; do not rely solely on `BIOMETRIC_WEAK` for high-value secrets.

### 4. Best Practices

**Error handling**:
- `ERROR_LOCKOUT` (temporary lock enforced by the system) → show an appropriate message / wait before retrying; do not hard-code assumptions about exact duration.
- `ERROR_LOCKOUT_PERMANENT` → suggest using device credential.
- `ERROR_NO_BIOMETRICS` → offer enrollment.
- `ERROR_USER_CANCELED` → avoid spamming dialogs; respect user's choice.

**UX**:
- Don't prompt on every screen — use a timeout (e.g., a few minutes after successful auth) depending on risk.
- Always provide an alternative (PIN/password or device credential), if allowed by business requirements.
- For `BIOMETRIC_STRONG or DEVICE_CREDENTIAL` in `setAllowedAuthenticators`, do NOT call `setNegativeButtonText()`: system UI provides appropriate controls and handles fallback.

---

## Дополнительные Вопросы (RU)

- Что происходит с зашифрованными данными при изменении набора биометрии, если используется `setInvalidatedByBiometricEnrollment(true)`?
- Как различия между `BIOMETRIC_STRONG` и `BIOMETRIC_WEAK` влияют на гарантии безопасности и использование `CryptoObject`/ключей?
- Когда использовать `setUserAuthenticationRequired(true)` против `setUserAuthenticationValidityDurationSeconds()`?
- Как реализовать биометрическую аутентификацию на устройствах с несколькими пользователями?
- Какая стратегия ограничения количества попыток (rate limiting) рекомендуется дополнительно к системной блокировке?

## Follow-ups

- What happens to encrypted data when biometric enrollment changes with `setInvalidatedByBiometricEnrollment(true)`?
- How does `BIOMETRIC_STRONG` vs `BIOMETRIC_WEAK` affect security guarantees and CryptoObject/key usage?
- When should you use `setUserAuthenticationRequired(true)` vs `setUserAuthenticationValidityDurationSeconds()`?
- How to implement biometric authentication for multi-user devices?
- What's the recommended strategy for rate limiting authentication attempts beyond system lockout?

## Ссылки (RU)

- https://developer.android.com/training/sign-in/biometric-auth
- https://developer.android.com/reference/androidx/biometric/BiometricPrompt

## References

- https://developer.android.com/training/sign-in/biometric-auth
- https://developer.android.com/reference/androidx/biometric/BiometricPrompt

## Связанные Вопросы (RU)

### Предварительные (проще)
- [[q-android-security-best-practices--android--medium]] — Базовые принципы безопасности

### Связанные (тот Же уровень)
- [[q-android-keystore-system--android--medium]] — Keystore API и генерация ключей
- [[q-app-security-best-practices--android--medium]] — Подходы к безопасности приложения

### Продвинутые (сложнее)
- [[q-android-runtime-internals--android--hard]] — Архитектура безопасности платформы

## Related Questions

### Prerequisites (Easier)
- [[q-android-security-best-practices--android--medium]] — Security fundamentals

### Related (Same Level)
- [[q-android-keystore-system--android--medium]] — Keystore API and key generation
- [[q-app-security-best-practices--android--medium]] — App-level security patterns

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] — Platform security architecture
