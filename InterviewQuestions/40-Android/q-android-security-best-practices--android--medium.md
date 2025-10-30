---
id: 20251012-122772
title: "Android Security Best Practices / Лучшие практики безопасности Android"
aliases: ["Android Security Best Practices", "Лучшие практики безопасности Android"]
topic: android
subtopics: [keystore-crypto, network-security-config, permissions]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-encryption, c-permissions, q-runtime-permissions--android--medium, q-android-manifest-file--android--easy]
created: 2025-10-15
updated: 2025-10-29
tags: [android/keystore-crypto, android/network-security-config, android/permissions, security, encryption, difficulty/medium]
sources: []
---
# Вопрос (RU)
> Какие основные практики безопасности нужно соблюдать при разработке Android приложений?

# Question (EN)
> What are the key security best practices for Android app development?

---

## Ответ (RU)

**Принцип глубокоэшелонированной защиты (Defense-in-Depth):**
Android использует многоуровневую безопасность: изоляция процессов, система разрешений, [[c-encryption|шифрование]] данных и защищенная сетевая коммуникация. Каждый уровень защищает от специфических векторов атак.

**1. Система разрешений:**
Runtime permissions контролируют доступ к чувствительным ресурсам (камера, местоположение, контакты). Используйте signature-based permissions для защиты внутренних API от сторонних приложений.

```xml
<!-- ✅ Защита внутреннего API signature-permission -->
<permission
    android:name="com.myapp.INTERNAL_API"
    android:protectionLevel="signature" />

<activity
    android:name=".AdminActivity"
    android:permission="com.myapp.INTERNAL_API"
    android:exported="false" />
```

**2. Безопасное хранение данных:**
Jetpack Security (EncryptedSharedPreferences, EncryptedFile) использует [[c-encryption|AES-256-GCM]] шифрование с ключами из Android Keystore, защищенными аппаратно.

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

// ❌ Небезопасное хранение токенов
// sharedPrefs.edit().putString("auth_token", token).apply()
```

**3. Сетевая безопасность:**
Network Security Config принудительно использует HTTPS и certificate pinning для защиты от MITM атак. Блокируйте cleartext traffic по умолчанию.

```xml
<!-- ✅ Network Security Config с pinning -->
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
Экспортированные компоненты доступны другим приложениям. Используйте `android:exported="false"` для внутренних Activity/Service/Provider.

```kotlin
// ✅ Валидация Intent от внешних источников
override fun onCreate(savedInstanceState: Bundle?) {
    if (intent.action == Intent.ACTION_VIEW) {
        val uri = intent.data ?: return finish()
        if (!isValidDeepLink(uri)) return finish()
        // Обработка только после валидации
    }
}

// ❌ Прямое использование данных из Intent без проверки
// val userId = intent.getStringExtra("user_id")
// deleteUser(userId)  // Опасно!
```

**5. WebView безопасность:**
Отключите JavaScript если не требуется, заблокируйте file:// доступ, валидируйте сообщения между JS и нативным кодом через postMessage.

```kotlin
// ✅ Минимально необходимые разрешения
webView.settings.apply {
    javaScriptEnabled = false
    allowFileAccess = false
    allowContentAccess = false
    mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
}

// Если JS необходим - безопасный JavascriptInterface
webView.addJavascriptInterface(object {
    @JavascriptInterface
    fun sendMessage(message: String) {
        if (isValidMessage(message)) processMessage(message)
    }
}, "NativeInterface")
```

**Дополнительные практики:**
- Обфускация кода (R8/ProGuard) для защиты от реверс-инжиниринга
- BiometricPrompt для криптографически стойкой аутентификации
- Android Lint/StrictMode для выявления security vulnerabilities
- Регулярные security audits и dependency scanning (OWASP Dependency-Check)

## Answer (EN)

**Defense-in-Depth Principle:**
Android employs multi-layered security: process isolation, permission system, data [[c-encryption|encryption]], and secure network communication. Each layer protects against specific attack vectors.

**1. Permission System:**
Runtime permissions control access to sensitive resources (camera, location, contacts). Use signature-based permissions to protect internal APIs from third-party apps.

```xml
<!-- ✅ Protect internal API with signature-permission -->
<permission
    android:name="com.myapp.INTERNAL_API"
    android:protectionLevel="signature" />

<activity
    android:name=".AdminActivity"
    android:permission="com.myapp.INTERNAL_API"
    android:exported="false" />
```

**2. Secure Data Storage:**
Jetpack Security (EncryptedSharedPreferences, EncryptedFile) uses [[c-encryption|AES-256-GCM]] encryption with keys from Android Keystore with hardware-backed protection.

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

// ❌ Insecure token storage
// sharedPrefs.edit().putString("auth_token", token).apply()
```

**3. Network Security:**
Network Security Config enforces HTTPS and certificate pinning to protect against MITM attacks. Block cleartext traffic by default.

```xml
<!-- ✅ Network Security Config with pinning -->
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
Exported components are accessible to other apps. Use `android:exported="false"` for internal Activity/Service/Provider.

```kotlin
// ✅ Validate Intent from external sources
override fun onCreate(savedInstanceState: Bundle?) {
    if (intent.action == Intent.ACTION_VIEW) {
        val uri = intent.data ?: return finish()
        if (!isValidDeepLink(uri)) return finish()
        // Process only after validation
    }
}

// ❌ Direct use of Intent data without validation
// val userId = intent.getStringExtra("user_id")
// deleteUser(userId)  // Dangerous!
```

**5. WebView Security:**
Disable JavaScript unless required, block file:// access, validate messages between JS and native code via postMessage.

```kotlin
// ✅ Minimal necessary permissions
webView.settings.apply {
    javaScriptEnabled = false
    allowFileAccess = false
    allowContentAccess = false
    mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
}

// If JS is needed - secure JavascriptInterface
webView.addJavascriptInterface(object {
    @JavascriptInterface
    fun sendMessage(message: String) {
        if (isValidMessage(message)) processMessage(message)
    }
}, "NativeInterface")
```

**Additional Practices:**
- Code obfuscation (R8/ProGuard) to prevent reverse engineering
- BiometricPrompt for cryptographically strong authentication
- Android Lint/StrictMode to detect security vulnerabilities
- Regular security audits and dependency scanning (OWASP Dependency-Check)

---

## Follow-ups

- How do you implement certificate pinning across different build variants (dev/staging/prod)?
- What are the security implications of using reflection and dynamic code loading?
- How do you securely store API keys and prevent extraction from APK?
- What's the difference between `BIOMETRIC_STRONG` and `BIOMETRIC_WEAK` authenticators?
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
- [[q-runtime-permissions--android--medium]] - Runtime permissions
- [[q-android-lint-tool--android--medium]] - Code analysis tools
- [[q-biometric-authentication--android--medium]] - Biometric authentication

### Advanced (Harder)
- [[q-android-root-detection--android--hard]] - Root detection techniques
- [[q-android-ssl-pinning-bypass--android--hard]] - SSL pinning bypass prevention
