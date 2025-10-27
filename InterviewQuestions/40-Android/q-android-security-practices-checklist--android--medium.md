---
id: 20251005-215456
title: Android Security Practices Checklist / Чек-лист практик безопасности Android
aliases: ["Android Security Practices Checklist", "Чек-лист практик безопасности Android"]
topic: android
subtopics: [keystore-crypto, permissions, architecture-clean]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-manifest-file--android--easy, c-encryption]
created: 2025-10-05
updated: 2025-01-27
tags: [android/keystore-crypto, android/permissions, android/architecture-clean, difficulty/medium]
sources: ["https://developer.android.com/topic/security/best-practices"]
---
# Вопрос (RU)
> Какой минимальный чек-лист безопасности Android приложения для production?

---

# Question (EN)
> What is the essential Android security practices checklist for production apps?

## Ответ (RU)

**Чек-лист практик безопасности Android** — систематический подход к защите приложения от типичных уязвимостей через использование [[c-encryption|шифрования]], Android Keystore, Network Security Config и обфускации кода.

**Ключевые области безопасности:**

**1. Защита данных:**
- Используйте internal storage для конфиденциальных данных
- Применяйте [[c-encryption|EncryptedSharedPreferences]] для токенов и ключей
- Избегайте хранения чувствительных данных в external storage

```kotlin
// ✅ Правильно: зашифрованное хранилище
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val encryptedPrefs = EncryptedSharedPreferences.create(
    context,
    "secure_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

// ❌ Неправильно: открытое хранилище для токенов
val prefs = getSharedPreferences("prefs", Context.MODE_PRIVATE)
prefs.edit().putString("api_token", token).apply()
```

**2. Сетевая безопасность:**

Network Security Config принудительно использует HTTPS и предотвращает cleartext-трафик.

```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
    <!-- ✅ Правильно: только HTTPS -->
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>
    </domain-config>
</network-security-config>
```

**3. Защита компонентов:**

Отключайте экспорт компонентов по умолчанию.

```xml
<!-- ✅ Правильно: отключен экспорт -->
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="${applicationId}.fileprovider"
    android:exported="false" />

<!-- ❌ Неправильно: доступен всем приложениям -->
<provider
    android:name="com.example.DataProvider"
    android:exported="true" />
```

**4. Обфускация кода:**

R8 защищает от обратной инженерии.

```kotlin
// build.gradle.kts
android {
    buildTypes {
        release {
            isMinifyEnabled = true  // ✅ Обфускация включена
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
        }
    }
}
```

**5. Аутентификация:**

Используйте биометрию для критичных операций.

```kotlin
// ✅ Правильно: биометрия для платежей
val biometricPrompt = BiometricPrompt(
    this,
    executor,
    object : BiometricPrompt.AuthenticationCallback() {
        override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
            executePayment()
        }
    }
)
```

## Answer (EN)

**Android Security Practices Checklist** is a systematic approach to protecting apps from common vulnerabilities through [[c-encryption|encryption]], Android Keystore, Network Security Config, and code obfuscation.

**Key security domains:**

**1. Data Protection:**
- Use internal storage for sensitive data
- Apply [[c-encryption|EncryptedSharedPreferences]] for tokens and keys
- Avoid storing sensitive data in external storage

```kotlin
// ✅ Correct: encrypted storage
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val encryptedPrefs = EncryptedSharedPreferences.create(
    context,
    "secure_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

// ❌ Wrong: plaintext storage for tokens
val prefs = getSharedPreferences("prefs", Context.MODE_PRIVATE)
prefs.edit().putString("api_token", token).apply()
```

**2. Network Security:**

Network Security Config enforces HTTPS-only communication.

```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
    <!-- ✅ Correct: HTTPS only -->
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>
    </domain-config>
</network-security-config>
```

**3. Component Protection:**

Disable component export by default.

```xml
<!-- ✅ Correct: export disabled -->
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="${applicationId}.fileprovider"
    android:exported="false" />

<!-- ❌ Wrong: accessible to all apps -->
<provider
    android:name="com.example.DataProvider"
    android:exported="true" />
```

**4. Code Obfuscation:**

R8 protects against reverse engineering.

```kotlin
// build.gradle.kts
android {
    buildTypes {
        release {
            isMinifyEnabled = true  // ✅ Obfuscation enabled
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
        }
    }
}
```

**5. Authentication:**

Use biometrics for critical operations.

```kotlin
// ✅ Correct: biometric for payments
val biometricPrompt = BiometricPrompt(
    this,
    executor,
    object : BiometricPrompt.AuthenticationCallback() {
        override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
            executePayment()
        }
    }
)
```

## Follow-ups

- How would you implement certificate pinning for a banking app with multiple backend domains?
- What are the security implications of using WebView with JavaScript enabled for OAuth flows?
- How do you balance security hardening with app performance in resource-constrained devices?

## References

- [[c-encryption]] - Encryption fundamentals
- https://developer.android.com/topic/security/best-practices

## Related Questions

### Prerequisites (Easier)
- [[q-android-manifest-file--android--easy]] - Manifest configuration basics

### Related (Medium)
- Android Keystore implementation patterns
- Network security configuration for hybrid apps
- ProGuard rules for third-party SDKs

### Advanced (Harder)
- Runtime security monitoring and threat detection
- Secure multi-process architecture design
- Hardware-backed key attestation implementation