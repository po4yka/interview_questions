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
related: [c-encryption, c-permissions, q-certificate-pinning--security--medium]
created: 2025-10-15
updated: 2025-01-25
tags: [android/keystore-crypto, android/network-security-config, android/permissions, difficulty/medium]
sources: [https://developer.android.com/topic/security/best-practices]
---
# Вопрос (RU)
> Какие лучшие практики безопасности Android вы знаете?

# Question (EN)
> What Android security best practices do you know?

---

## Ответ (RU)

**Архитектура безопасности:**
Android применяет defense-in-depth подход: изоляция процессов (sandboxing), система разрешений, [[c-encryption|шифрование]] данных и защищенная сетевая коммуникация. Каждый слой защищает от специфических векторов атак.

**1. Система разрешений:**
Runtime permissions контролируют доступ к чувствительным ресурсам. Signature-based permissions ограничивают доступ приложениями с одинаковым сертификатом подписи.

```xml
<!-- ✅ Signature permission для внутреннего API -->
<permission
    android:name="com.app.INTERNAL_API"
    android:protectionLevel="signature" />
```

**2. Безопасное хранение данных:**
Jetpack Security (EncryptedSharedPreferences, EncryptedFile) использует [[c-encryption|AES-256-GCM]] шифрование с ключами из Android Keystore, защищенными аппаратно.

```kotlin
// ✅ Шифрование SharedPreferences
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val encryptedPrefs = EncryptedSharedPreferences.create(
    context, "secure_prefs", masterKey,
    PrefKeyEncryptionScheme.AES256_SIV,
    PrefValueEncryptionScheme.AES256_GCM
)
```

**3. Сетевая безопасность:**
Network Security Config принудительно обеспечивает HTTPS и certificate pinning для защиты от MITM атак.

```xml
<!-- ✅ Блокировка cleartext + pinning -->
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set>
            <pin digest="SHA-256">base64hash==</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

**4. Защита компонентов:**
Экспортированные компоненты доступны другим приложениям. Используйте `android:exported="false"` для внутренних компонентов.

```xml
<!-- ✅ Неэкспортированный Provider -->
<provider
    android:name=".InternalProvider"
    android:exported="false" />

<!-- ❌ Небезопасный Intent без проверки -->
<!-- Используйте Intent.createChooser() для критичных операций -->
```

**5. WebView безопасность:**
Отключите ненужные функции, включите HTTPS-only режим, валидируйте сообщения между JS и нативным кодом.

```kotlin
// ✅ Безопасная конфигурация WebView
webView.settings.apply {
    javaScriptEnabled = false  // Включать только если необходимо
    allowFileAccess = false
    allowContentAccess = false
}
```

**Дополнительные практики:**
- Обфускация кода (R8/ProGuard)
- Биометрическая аутентификация через BiometricPrompt
- Регулярные security audits и penetration testing
- Использование Android Lint для статического анализа

## Answer (EN)

**Security Architecture:**
Android employs defense-in-depth approach: process isolation (sandboxing), permission system, data [[c-encryption|encryption]], and secure network communication. Each layer protects against specific attack vectors.

**1. Permission System:**
Runtime permissions control access to sensitive resources. Signature-based permissions restrict access to apps signed with the same certificate.

```xml
<!-- ✅ Signature permission for internal API -->
<permission
    android:name="com.app.INTERNAL_API"
    android:protectionLevel="signature" />
```

**2. Secure Data Storage:**
Jetpack Security (EncryptedSharedPreferences, EncryptedFile) uses [[c-encryption|AES-256-GCM]] encryption with keys from Android Keystore, hardware-backed protection.

```kotlin
// ✅ Encrypt SharedPreferences
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val encryptedPrefs = EncryptedSharedPreferences.create(
    context, "secure_prefs", masterKey,
    PrefKeyEncryptionScheme.AES256_SIV,
    PrefValueEncryptionScheme.AES256_GCM
)
```

**3. Network Security:**
Network Security Config enforces HTTPS and certificate pinning to protect against MITM attacks.

```xml
<!-- ✅ Block cleartext + pinning -->
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set>
            <pin digest="SHA-256">base64hash==</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

**4. Component Protection:**
Exported components are accessible to other apps. Use `android:exported="false"` for internal components.

```xml
<!-- ✅ Non-exported Provider -->
<provider
    android:name=".InternalProvider"
    android:exported="false" />

<!-- ❌ Unsafe Intent without validation -->
<!-- Use Intent.createChooser() for sensitive operations -->
```

**5. WebView Security:**
Disable unnecessary features, enforce HTTPS-only mode, validate messages between JS and native code.

```kotlin
// ✅ Secure WebView configuration
webView.settings.apply {
    javaScriptEnabled = false  // Enable only if necessary
    allowFileAccess = false
    allowContentAccess = false
}
```

**Additional Practices:**
- Code obfuscation (R8/ProGuard)
- Biometric authentication via BiometricPrompt
- Regular security audits and penetration testing
- Android Lint for static analysis

---

## Follow-ups

- How do you implement certificate pinning for different build variants (dev/staging/prod)?
- What are the security implications of using WebView with JavaScript enabled?
- How do you handle sensitive data in memory to prevent memory dumps?
- What's the difference between `BIOMETRIC_STRONG` and `BIOMETRIC_WEAK` authenticators?
- How do you securely store API keys in an Android app?

## References

- [[c-encryption]] - Encryption fundamentals
- [[c-permissions]] - Android permissions system
- https://developer.android.com/topic/security/best-practices

## Related Questions

### Prerequisites (Easier)
- [[q-android-manifest-file--android--easy]] - Manifest configuration
- [[q-android-app-components--android--easy]] - App components

### Related (Same Level)
- [[q-certificate-pinning--security--medium]] - Certificate pinning
- [[q-android-lint-tool--android--medium]] - Code analysis
- [[q-biometric-authentication--android--medium]] - Biometric auth

### Advanced (Harder)
- [[q-android-architectural-patterns--android--medium]] - Security patterns
- [[q-android-runtime-internals--android--hard]] - Runtime security
