---
id: android-002
title: Android Security Practices Checklist / Чек-лист практик безопасности Android
aliases:
- Android Security Practices Checklist
- Чек-лист практик безопасности Android
topic: android
subtopics:
- keystore-crypto
- network-security-config
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
- c-encryption
- c-enterprise-mdm
- c-play-integrity
- c-scoped-storage-security
- c-security
- c-security-hardening
- q-android-security-best-practices--android--medium
- q-app-security-best-practices--android--medium
- q-database-encryption-android--android--medium
created: 2025-10-05
updated: 2025-11-10
tags:
- android/keystore-crypto
- android/network-security-config
- android/permissions
- difficulty/medium
- security
sources: []
anki_cards:
- slug: android-002-0-en
  language: en
  anki_id: 1768363949681
  synced_at: '2026-01-14T09:17:53.123157'
- slug: android-002-0-ru
  language: ru
  anki_id: 1768363949725
  synced_at: '2026-01-14T09:17:53.125286'
---
# Вопрос (RU)
> Какой минимальный чек-лист безопасности Android приложения для production?

# Question (EN)
> What is the essential Android security practices checklist for production apps?

---

## Ответ (RU)

**Систематический подход** к защите через [[c-encryption|шифрование]] данных, Android Keystore, Network Security Config, обфускацию кода и биометрическую аутентификацию.

### 1. Защита Данных В Хранилище

**[[c-encryption|EncryptedSharedPreferences]]** для токенов и ключей:

```kotlin
// ✅ Шифрование AES256-GCM
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val prefs = EncryptedSharedPreferences.create(
    context, "secure_prefs", masterKey,
    PrefKeyEncryptionScheme.AES256_SIV,
    PrefValueEncryptionScheme.AES256_GCM
)

// ❌ Открытое хранение
val plainPrefs = getSharedPreferences("prefs", MODE_PRIVATE)
```

**Правила**:
- Internal storage для чувствительных данных
- Избегать external storage для токенов/паролей
- [[c-android-keystore|Android Keystore]] для криптографических ключей

### 2. Сетевая Безопасность

**Network Security Config** запрещает cleartext HTTP и может использоваться для пиннинга сертификатов:

```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
    <!-- ✅ Запрет cleartext по умолчанию -->
    <base-config cleartextTrafficPermitted="false" />

    <!-- HTTPS и явное разрешение для домена API -->
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>
    </domain-config>

    <!-- Certificate pinning для критичного домена -->
    <domain-config>
        <domain>secure.example.com</domain>
        <pin-set>
            <pin digest="SHA-256">base64hash==</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

**AndroidManifest.xml**:
```xml
<application
    android:networkSecurityConfig="@xml/network_security_config">
```

### 3. Защита Компонентов

**Ограничение экспорта** для внутренних компонентов (Activities, Services, Providers, Receivers):

```xml
<!-- ✅ Внутренний провайдер, не доступен другим приложениям -->
<provider
    android:name="com.example.internal.DataProvider"
    android:authorities="com.example.internal.provider"
    android:exported="false" />

<!-- ✅ FileProvider для шаринга файлов: доступен, но с granular-разрешениями -->
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="com.example.fileprovider"
    android:exported="true"
    android:grantUriPermissions="true" />
```

**Правила**:
- Явно указывать `android:exported` для компонентов, особенно с intent-filters (Android 12+).
- Использовать `exported="false"` по умолчанию для внутренних компонент; включать `exported="true"` только для заведомо публичных API.
- Для FileProvider полагаться на `grantUriPermissions`/`FLAG_GRANT_*` и корректный `authorities`, а не на глобальный доступ.

### 4. Обфускация Кода

**R8** усложняет обратную инженерию:

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

### 5. Биометрическая Аутентификация

**BiometricPrompt** для критичных операций (платежи, изменение настроек безопасности):

```kotlin
val biometricPrompt = BiometricPrompt(
    this, executor,
    object : BiometricPrompt.AuthenticationCallback() {
        override fun onAuthenticationSucceeded(
            result: BiometricPrompt.AuthenticationResult
        ) {
            // ✅ Выполнить операцию
        }
    }
)

val promptInfo = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Подтверждение платежа")
    .setSubtitle("Используйте биометрию или экран блокировки устройства")
    .setAllowedAuthenticators(
        BiometricManager.Authenticators.BIOMETRIC_STRONG or
            BiometricManager.Authenticators.DEVICE_CREDENTIAL
    )
    .build()
```

**Чек-лист проверки**:
- EncryptedSharedPreferences для токенов
- Network Security Config с глобальным запретом cleartext и HTTPS
- Компоненты с явным `android:exported`, внутренние — `false`
- R8 minification включен в release
- BiometricPrompt с сильной аутентификацией для финансовых/критичных операций

## Answer (EN)

**Systematic approach** to security through [[c-encryption|encryption]], Android Keystore, Network Security Config, code obfuscation, and biometric authentication.

### 1. Storage Protection

**[[c-encryption|EncryptedSharedPreferences]]** for tokens and keys:

```kotlin
// ✅ AES256-GCM encryption
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val prefs = EncryptedSharedPreferences.create(
    context, "secure_prefs", masterKey,
    PrefKeyEncryptionScheme.AES256_SIV,
    PrefValueEncryptionScheme.AES256_GCM
)

// ❌ Plain storage
val plainPrefs = getSharedPreferences("prefs", MODE_PRIVATE)
```

**Rules**:
- Internal storage for sensitive data
- Avoid external storage for tokens/passwords
- [[c-android-keystore|Android Keystore]] for cryptographic keys

### 2. Network Security

**Network Security Config** should disable cleartext HTTP and can be used for certificate pinning:

```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
    <!-- ✅ Disable cleartext by default -->
    <base-config cleartextTrafficPermitted="false" />

    <!-- HTTPS and explicit allow for API domain -->
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>
    </domain-config>

    <!-- Certificate pinning for critical domain -->
    <domain-config>
        <domain>secure.example.com</domain>
        <pin-set>
            <pin digest="SHA-256">base64hash==</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

**AndroidManifest.xml**:
```xml
<application
    android:networkSecurityConfig="@xml/network_security_config">
```

### 3. Component Protection

**Restrict export** for internal components (Activities, Services, Providers, Receivers):

```xml
<!-- ✅ Internal provider, not accessible to other apps -->
<provider
    android:name="com.example.internal.DataProvider"
    android:authorities="com.example.internal.provider"
    android:exported="false" />

<!-- ✅ FileProvider for file sharing: exported with scoped grants -->
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="com.example.fileprovider"
    android:exported="true"
    android:grantUriPermissions="true" />
```

**Rules**:
- Explicitly set `android:exported` for components, especially those with intent-filters (Android 12+).
- Use `exported="false"` by default for internal components; set `exported="true"` only for intentional public APIs.
- For FileProvider, rely on `grantUriPermissions`/`FLAG_GRANT_*` flags and proper `authorities` instead of broad access.

### 4. Code Obfuscation

**R8** complicates reverse engineering:

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

**BiometricPrompt** for critical operations (payments, security settings changes):

```kotlin
val biometricPrompt = BiometricPrompt(
    this, executor,
    object : BiometricPrompt.AuthenticationCallback() {
        override fun onAuthenticationSucceeded(
            result: BiometricPrompt.AuthenticationResult
        ) {
            // ✅ Execute operation
        }
    }
)

val promptInfo = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Confirm Payment")
    .setSubtitle("Use biometrics or device screen lock")
    .setAllowedAuthenticators(
        BiometricManager.Authenticators.BIOMETRIC_STRONG or
            BiometricManager.Authenticators.DEVICE_CREDENTIAL
    )
    .build()
```

**Verification checklist**:
- EncryptedSharedPreferences for tokens
- Network Security Config with global cleartext disabled and HTTPS
- Components with explicit `android:exported`, internal ones set to `false`
- R8 minification enabled in release
- BiometricPrompt with strong authenticators for financial/critical operations

---

## Follow-ups

- How would you implement certificate pinning with dynamic domain rotation for multi-tenant APIs?
- What security risks arise when using WebView with JavaScript enabled for OAuth flows?
- How do you prevent security token extraction through memory dumps on rooted devices?
- What strategies mitigate man-in-the-middle attacks when certificate pinning fails or expires?
- How would you design secure key rotation for encrypted database migrations without data loss?

## References

- [[c-encryption]] - Encryption fundamentals and Android implementation patterns
- [[c-android-keystore]] - Android Keystore system architecture and key management
- https://developer.android.com/topic/security/best-practices
- https://developer.android.com/privacy-and-security/security-tips

## Related Questions

### Prerequisites (Easier)
- [[q-android-manifest-file--android--easy]] - Manifest configuration and permissions fundamentals

### Related (Medium)
 - Android Keystore patterns and cryptographic key lifecycle
 - Advanced network security configurations and certificate pinning strategies
 - R8/ProGuard rules for third-party library obfuscation
