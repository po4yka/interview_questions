---
id: android-424
title: Android Security Best Practices / Лучшие практики безопасности Android
aliases: [Android Security Best Practices, Лучшие практики безопасности Android]
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
status: reviewed
moc: moc-android
related:
  - c-encryption
  - c-permissions
created: 2025-10-15
updated: 2025-10-30
tags: [android/keystore-crypto, android/network-security-config, android/permissions, difficulty/medium, encryption, security]
sources: []
---

# Вопрос (RU)
> Какие основные практики безопасности нужно соблюдать при разработке Android приложений?

# Question (EN)
> What are the key security best practices for Android app development?

---

## Ответ (RU)

**Принцип многоуровневой защиты (Defense-in-Depth):**
Android использует изоляцию процессов, систему разрешений, [[c-encryption|шифрование]] данных и защищенную сетевую коммуникацию. Каждый уровень защищает от конкретных векторов атак.

**1. Система разрешений:**
Runtime permissions контролируют доступ к чувствительным ресурсам. Signature-permissions защищают внутренние API от сторонних приложений.

```xml
<!-- ✅ Защита внутреннего API -->
<permission
    android:name="com.myapp.INTERNAL_API"
    android:protectionLevel="signature" />

<activity
    android:name=".AdminActivity"
    android:permission="com.myapp.INTERNAL_API"
    android:exported="false" />
```

**2. Безопасное хранение данных:**
Jetpack Security (EncryptedSharedPreferences, EncryptedFile) использует [[c-encryption|AES-256-GCM]] с ключами из Android Keystore, защищенными аппаратно.

```kotlin
// ✅ Шифрование чувствительных данных
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val encryptedPrefs = EncryptedSharedPreferences.create(
    context,
    "secure_prefs",
    masterKey,
    PrefKeyEncryptionScheme.AES256_SIV,
    PrefValueEncryptionScheme.AES256_GCM
)

// ❌ Небезопасное хранение
// sharedPrefs.edit().putString("auth_token", token).apply()
```

**3. Сетевая безопасность:**
Network Security Config принудительно использует HTTPS и certificate pinning для защиты от MITM атак.

```xml
<!-- ✅ Network Security Config -->
<network-security-config>
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>

    <domain-config>
        <domain includeSubdomains="true">api.myapp.com</domain>
        <pin-set expiration="2026-01-01">
            <pin digest="SHA-256">base64hash==</pin>
            <pin digest="SHA-256">backup_hash==</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

**4. Защита компонентов:**
Используйте `android:exported="false"` для внутренних Activity/Service/Provider. Валидируйте Intent от внешних источников.

```kotlin
// ✅ Валидация Intent
override fun onCreate(savedInstanceState: Bundle?) {
    if (intent.action == Intent.ACTION_VIEW) {
        val uri = intent.data ?: return finish()
        if (!isValidDeepLink(uri)) return finish()
        processDeepLink(uri)
    }
}

// ❌ Прямое использование без проверки
// val userId = intent.getStringExtra("user_id")
// deleteUser(userId)  // Опасно!
```

**5. WebView безопасность:**
Отключите JavaScript если не требуется, заблокируйте file:// доступ, валидируйте JS-нативное взаимодействие.

```kotlin
// ✅ Минимальные разрешения
webView.settings.apply {
    javaScriptEnabled = false  // Включать только при необходимости
    allowFileAccess = false
    allowContentAccess = false
    mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
}

// Безопасный JavascriptInterface
webView.addJavascriptInterface(object {
    @JavascriptInterface
    fun sendMessage(msg: String) {
        if (isValidMessage(msg)) processMessage(msg)
    }
}, "NativeInterface")
```

**Дополнительные меры:**
- R8/ProGuard для обфускации кода
- BiometricPrompt для криптографически стойкой аутентификации
- Android Lint/StrictMode для выявления уязвимостей
- Dependency scanning (OWASP Dependency-Check)

## Answer (EN)

**Defense-in-Depth Principle:**
Android employs process isolation, permission system, data [[c-encryption|encryption]], and secure network communication. Each layer protects against specific attack vectors.

**1. Permission System:**
Runtime permissions control access to sensitive resources. Signature-permissions protect internal APIs from third-party apps.

```xml
<!-- ✅ Protect internal API -->
<permission
    android:name="com.myapp.INTERNAL_API"
    android:protectionLevel="signature" />

<activity
    android:name=".AdminActivity"
    android:permission="com.myapp.INTERNAL_API"
    android:exported="false" />
```

**2. Secure Data Storage:**
Jetpack Security (EncryptedSharedPreferences, EncryptedFile) uses [[c-encryption|AES-256-GCM]] with keys from Android Keystore with hardware-backed protection.

```kotlin
// ✅ Encrypt sensitive data
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val encryptedPrefs = EncryptedSharedPreferences.create(
    context,
    "secure_prefs",
    masterKey,
    PrefKeyEncryptionScheme.AES256_SIV,
    PrefValueEncryptionScheme.AES256_GCM
)

// ❌ Insecure storage
// sharedPrefs.edit().putString("auth_token", token).apply()
```

**3. Network Security:**
Network Security Config enforces HTTPS and certificate pinning to protect against MITM attacks.

```xml
<!-- ✅ Network Security Config -->
<network-security-config>
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>

    <domain-config>
        <domain includeSubdomains="true">api.myapp.com</domain>
        <pin-set expiration="2026-01-01">
            <pin digest="SHA-256">base64hash==</pin>
            <pin digest="SHA-256">backup_hash==</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

**4. Component Protection:**
Use `android:exported="false"` for internal Activity/Service/Provider. Validate Intent from external sources.

```kotlin
// ✅ Validate Intent
override fun onCreate(savedInstanceState: Bundle?) {
    if (intent.action == Intent.ACTION_VIEW) {
        val uri = intent.data ?: return finish()
        if (!isValidDeepLink(uri)) return finish()
        processDeepLink(uri)
    }
}

// ❌ Direct use without validation
// val userId = intent.getStringExtra("user_id")
// deleteUser(userId)  // Dangerous!
```

**5. WebView Security:**
Disable JavaScript unless required, block file:// access, validate JS-native interactions.

```kotlin
// ✅ Minimal permissions
webView.settings.apply {
    javaScriptEnabled = false  // Enable only when necessary
    allowFileAccess = false
    allowContentAccess = false
    mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
}

// Secure JavascriptInterface
webView.addJavascriptInterface(object {
    @JavascriptInterface
    fun sendMessage(msg: String) {
        if (isValidMessage(msg)) processMessage(msg)
    }
}, "NativeInterface")
```

**Additional Measures:**
- R8/ProGuard for code obfuscation
- BiometricPrompt for cryptographically strong authentication
- Android Lint/StrictMode to detect vulnerabilities
- Dependency scanning (OWASP Dependency-Check)

---

## Follow-ups

- How do you implement certificate pinning across different build variants (dev/staging/prod)?
- What are the security implications of using reflection and dynamic code loading?
- How do you securely store API keys and prevent extraction from APK?
- What's the difference between BIOMETRIC_STRONG and BIOMETRIC_WEAK authenticators?
- How do you handle sensitive data in memory to prevent memory dumps and cold boot attacks?

## References

- [[c-encryption]] - Encryption fundamentals
- [[c-permissions]] - Android permissions system
- [[c-android-keystore]] - Android Keystore system
- https://developer.android.com/topic/security/best-practices
- https://owasp.org/www-project-mobile-app-security/

## Related Questions

### Prerequisites (Easier)
- [[q-android-manifest-file--android--easy]] - Manifest configuration
- [[q-android-app-components--android--easy]] - App components basics

### Related (Same Level)
 - Runtime permissions
- [[q-android-lint-tool--android--medium]] - Code analysis tools
- [[q-biometric-authentication--android--medium]] - Biometric authentication

### Advanced (Harder)
 - Root detection techniques
 - SSL pinning bypass prevention
