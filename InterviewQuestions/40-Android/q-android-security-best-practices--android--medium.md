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
status: draft
moc: moc-android
related:
- c-encryption
- c-permissions
created: 2025-10-15
updated: 2025-11-11
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
Android использует изоляцию процессов, систему разрешений, [[c-encryption|шифрование]] данных и защищенную сетевую коммуникацию. Каждый уровень должен рассматриваться как отдельный барьер против конкретных векторов атак.

**1. Система разрешений:**
Runtime permissions контролируют доступ к чувствительным ресурсам. Signature-permissions защищают внутренние API от сторонних приложений (доступ предоставляется только приложениям с той же подписью).

```xml
<!-- ✅ Защита внутреннего API: доступ только приложениям с той же подписью -->
<permission
    android:name="com.myapp.INTERNAL_API"
    android:protectionLevel="signature" />

<!-- Если компонент должен быть доступен только своим приложениям с той же подписью,
     android:exported="true" и android:permission с signature-permission -->
<activity
    android:name=".AdminActivity"
    android:permission="com.myapp.INTERNAL_API"
    android:exported="true" />
```

**2. Безопасное хранение данных:**
Jetpack Security (EncryptedSharedPreferences, EncryptedFile) при использовании MasterKey с схемой AES256_GCM применяет [[c-encryption|AES-256-GCM]] и ключи из Android Keystore, предпочтительно с аппаратной защитой, если устройство поддерживает.

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
Network Security Config помогает:
- запретить незашифрованный HTTP-трафик (`cleartextTrafficPermitted="false"`),
- ограничить доверенные CA через trust anchors.

Сам по себе Network Security Config не реализует certificate pinning; для пиннинга нужно использовать дополнительные механизмы (например, кастомный TrustManager или поддержку пиннинга в HTTP-клиенте).

```xml
<!-- ✅ Network Security Config: запрет cleartext и настройка trust anchors -->
<network-security-config>
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>

    <domain-config>
        <domain includeSubdomains="true">api.myapp.com</domain>
    </domain-config>
</network-security-config>
```

**4. Защита компонентов:**
Используйте `android:exported="false"` для внутренних `Activity`/`Service`/Provider, которые не должны вызываться извне. Для экспортируемых компонентов валидируйте `Intent` от внешних источников.

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
Отключите JavaScript, если не требуется, заблокируйте file:// доступ, избегайте загрузки недоверенного контента при наличии `addJavascriptInterface`, валидируйте JS-нативное взаимодействие.

```kotlin
// ✅ Минимальные разрешения
webView.settings.apply {
    javaScriptEnabled = false  // Включать только при необходимости
    allowFileAccess = false
    allowContentAccess = false
    mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
}

// Использовать JavascriptInterface только с доверенным контентом
webView.addJavascriptInterface(object {
    @JavascriptInterface
    fun sendMessage(msg: String) {
        if (isValidMessage(msg)) processMessage(msg)
    }
}, "NativeInterface")
```

**Дополнительные меры:**
- Используйте R8/ProGuard для обфускации кода (понимая, что это не защита, а усложнение анализа)
- Используйте BiometricPrompt для криптографически стойкой аутентификации пользователей
- Используйте Android Lint/StrictMode для выявления потенциальных уязвимостей и неправильного использования API
- Выполняйте анализ зависимостей (например, OWASP Dependency-Check) для поиска известных уязвимостей

## Ответы / Дополнительные вопросы (RU)

- Как реализовать certificate pinning для разных build variant (dev/staging/prod)?
- Каковы риски использования рефлексии и динамической загрузки кода с точки зрения безопасности?
- Как безопасно хранить API-ключи и предотвращать их извлечение из APK?
- В чем разница между аутентификаторами BIOMETRIC_STRONG и BIOMETRIC_WEAK?
- Как обрабатывать чувствительные данные в памяти, чтобы снизить риск дампов памяти и атак холодной перезагрузки?

## Ссылки (RU)

- [[c-encryption]] - Основы шифрования
- [[c-permissions]] - Система разрешений Android
- https://developer.android.com/topic/security/best-practices
- https://owasp.org/www-project-mobile-app-security/

## Связанные вопросы (RU)

### Предпосылки (Проще)
- [[q-android-manifest-file--android--easy]] - Конфигурация Manifest
- [[q-android-app-components--android--easy]] - Базовые компоненты приложения

### Связанные (Того же уровня)
- Runtime permissions
- [[q-android-lint-tool--android--medium]] - Инструменты анализа кода
- [[q-biometric-authentication--android--medium]] - Биометрическая аутентификация

### Продвинутые (Сложнее)
- Методы обнаружения рута (root detection techniques)
- Предотвращение обхода SSL pinning

## Answer (EN)

**Defense-in-Depth Principle:**
Android employs process isolation, a permission system, data [[c-encryption|encryption]], and secure network communication. Each layer should be treated as a separate barrier against specific attack vectors.

**1. Permission System:**
Runtime permissions control access to sensitive resources. Signature-permissions protect internal APIs from third-party apps (only apps signed with the same certificate can access them).

```xml
<!-- ✅ Protect internal API: only apps signed with the same key can access it -->
<permission
    android:name="com.myapp.INTERNAL_API"
    android:protectionLevel="signature" />

<!-- If the component is meant to be accessible only to same-signature apps,
     use android:exported="true" with a signature-level permission -->
<activity
    android:name=".AdminActivity"
    android:permission="com.myapp.INTERNAL_API"
    android:exported="true" />
```

**2. Secure Data Storage:**
Jetpack Security (EncryptedSharedPreferences, EncryptedFile), when using a MasterKey with AES256_GCM scheme, relies on [[c-encryption|AES-256-GCM]] and keys stored in Android Keystore, preferably hardware-backed when available.

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
Network Security Config helps to:
- disable cleartext HTTP traffic (`cleartextTrafficPermitted="false"`),
- restrict trusted CAs via trust anchors.

By itself, Network Security Config does not implement certificate pinning; pinning must be handled separately (e.g., via a custom TrustManager or HTTP client pinning support).

```xml
<!-- ✅ Network Security Config: disable cleartext and configure trust anchors -->
<network-security-config>
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>

    <domain-config>
        <domain includeSubdomains="true">api.myapp.com</domain>
    </domain-config>
</network-security-config>
```

**4. Component Protection:**
Use `android:exported="false"` for internal `Activity`/`Service`/Provider components that must not be invoked externally. For exported components, always validate `Intents` from external sources.

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
Disable JavaScript unless required, block file:// access, avoid loading untrusted content when `addJavascriptInterface` is used, and validate JS-native interactions.

```kotlin
// ✅ Minimal permissions
webView.settings.apply {
    javaScriptEnabled = false  // Enable only when necessary
    allowFileAccess = false
    allowContentAccess = false
    mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
}

// Use JavascriptInterface only with trusted content
webView.addJavascriptInterface(object {
    @JavascriptInterface
    fun sendMessage(msg: String) {
        if (isValidMessage(msg)) processMessage(msg)
    }
}, "NativeInterface")
```

**Additional Measures:**
- Use R8/ProGuard for code obfuscation (understanding it is not a strong security control, but raises the bar for reverse engineering)
- Use BiometricPrompt for cryptographically strong user authentication
- Use Android Lint/StrictMode to detect potential vulnerabilities and API misuses
- Perform dependency scanning (e.g., OWASP Dependency-Check) to catch known vulnerabilities

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
