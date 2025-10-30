---
id: 20251005-215456
title: Android Security Practices Checklist / Чек-лист практик безопасности Android
aliases: ["Android Security Practices Checklist", "Чек-лист практик безопасности Android"]
topic: android
subtopics: [keystore-crypto, permissions, network-security-config]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-encryption, q-android-manifest-file--android--easy]
created: 2025-10-05
updated: 2025-10-29
tags: [android/keystore-crypto, android/permissions, android/network-security-config, security, difficulty/medium]
sources: []
---

# Вопрос (RU)
> Какой минимальный чек-лист безопасности Android приложения для production?

---

# Question (EN)
> What is the essential Android security practices checklist for production apps?

---

## Ответ (RU)

**Систематический подход** к защите Android приложения через [[c-encryption|шифрование]], Android Keystore, Network Security Config и обфускацию кода.

### 1. Защита данных

**EncryptedSharedPreferences** для конфиденциальных данных:

```kotlin
// ✅ Безопасное хранилище
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val encryptedPrefs = EncryptedSharedPreferences.create(
    context, "secure_prefs", masterKey,
    PrefKeyEncryptionScheme.AES256_SIV,
    PrefValueEncryptionScheme.AES256_GCM
)

// ❌ Незащищённое хранилище
val prefs = getSharedPreferences("prefs", Context.MODE_PRIVATE)
prefs.edit().putString("api_token", token).apply()
```

**Правила хранения**:
- Internal storage для чувствительных данных
- [[c-encryption|EncryptedSharedPreferences]] для токенов/ключей
- Избегать external storage для конфиденциальной информации

### 2. Сетевая безопасность

**Network Security Config** принудительно использует HTTPS:

```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
    <!-- ✅ Только HTTPS -->
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>
    </domain-config>

    <!-- Certificate pinning для критичных доменов -->
    <domain-config>
        <domain includeSubdomains="true">secure.example.com</domain>
        <pin-set>
            <pin digest="SHA-256">base64hash==</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

### 3. Защита компонентов

**Отключение экспорта** по умолчанию:

```xml
<!-- ✅ Безопасно: только внутреннее использование -->
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="${applicationId}.fileprovider"
    android:exported="false"
    android:grantUriPermissions="true" />

<!-- ❌ Небезопасно: доступен всем -->
<provider
    android:name="com.example.DataProvider"
    android:exported="true" />
```

**Правило**: Компоненты exported="false" по умолчанию, except explicit API.

### 4. Обфускация кода

**R8** защищает от обратной инженерии:

```kotlin
// build.gradle.kts
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

### 5. Биометрическая аутентификация

**BiometricPrompt** для критичных операций:

```kotlin
// ✅ Биометрия для платежей
val biometricPrompt = BiometricPrompt(
    this, executor,
    object : BiometricPrompt.AuthenticationCallback() {
        override fun onAuthenticationSucceeded(
            result: BiometricPrompt.AuthenticationResult
        ) {
            executePayment()
        }

        override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
            showError(errString)
        }
    }
)

val promptInfo = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Подтверждение платежа")
    .setNegativeButtonText("Отмена")
    .build()

biometricPrompt.authenticate(promptInfo)
```

## Answer (EN)

**Systematic approach** to Android app security through [[c-encryption|encryption]], Android Keystore, Network Security Config, and code obfuscation.

### 1. Data Protection

**EncryptedSharedPreferences** for sensitive data:

```kotlin
// ✅ Secure storage
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val encryptedPrefs = EncryptedSharedPreferences.create(
    context, "secure_prefs", masterKey,
    PrefKeyEncryptionScheme.AES256_SIV,
    PrefValueEncryptionScheme.AES256_GCM
)

// ❌ Insecure storage
val prefs = getSharedPreferences("prefs", Context.MODE_PRIVATE)
prefs.edit().putString("api_token", token).apply()
```

**Storage rules**:
- Internal storage for sensitive data
- [[c-encryption|EncryptedSharedPreferences]] for tokens/keys
- Avoid external storage for confidential information

### 2. Network Security

**Network Security Config** enforces HTTPS:

```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
    <!-- ✅ HTTPS only -->
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>
    </domain-config>

    <!-- Certificate pinning for critical domains -->
    <domain-config>
        <domain includeSubdomains="true">secure.example.com</domain>
        <pin-set>
            <pin digest="SHA-256">base64hash==</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

### 3. Component Protection

**Disable export** by default:

```xml
<!-- ✅ Secure: internal use only -->
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="${applicationId}.fileprovider"
    android:exported="false"
    android:grantUriPermissions="true" />

<!-- ❌ Insecure: accessible to all -->
<provider
    android:name="com.example.DataProvider"
    android:exported="true" />
```

**Rule**: Components exported="false" by default, except explicit API.

### 4. Code Obfuscation

**R8** protects against reverse engineering:

```kotlin
// build.gradle.kts
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

### 5. Biometric Authentication

**BiometricPrompt** for critical operations:

```kotlin
// ✅ Biometric for payments
val biometricPrompt = BiometricPrompt(
    this, executor,
    object : BiometricPrompt.AuthenticationCallback() {
        override fun onAuthenticationSucceeded(
            result: BiometricPrompt.AuthenticationResult
        ) {
            executePayment()
        }

        override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
            showError(errString)
        }
    }
)

val promptInfo = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Confirm Payment")
    .setNegativeButtonText("Cancel")
    .build()

biometricPrompt.authenticate(promptInfo)
```

---

## Follow-ups

- How would you implement certificate pinning for a multi-tenant API with dynamic domain rotation?
- What security implications arise when using WebView with JavaScript enabled for OAuth authentication flows?
- How do you prevent security token extraction through memory dumps on rooted devices?
- What strategies mitigate man-in-the-middle attacks when certificate pinning fails or expires?
- How would you design secure key rotation for encrypted database migrations without data loss?

## References

- [[c-encryption]] - Encryption fundamentals and Android implementation
- [[c-android-keystore]] - Android Keystore system architecture
- https://developer.android.com/topic/security/best-practices
- https://developer.android.com/privacy-and-security/security-tips

## Related Questions

### Prerequisites (Easier)
- [[q-android-manifest-file--android--easy]] - Manifest configuration basics and permissions

### Related (Medium)
- [[q-android-keystore-implementation--android--medium]] - Android Keystore patterns and key management
- [[q-network-security-config--android--medium]] - Advanced network security configurations
- [[q-proguard-rules-optimization--android--medium]] - R8/ProGuard rules for third-party libraries

### Advanced (Harder)
- [[q-runtime-security-monitoring--android--hard]] - Runtime threat detection and response strategies
- [[q-secure-multiprocess-architecture--android--hard]] - Inter-process security in modular apps
- [[q-hardware-key-attestation--android--hard]] - Hardware-backed key attestation implementation
