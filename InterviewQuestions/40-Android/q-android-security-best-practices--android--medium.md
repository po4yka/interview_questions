---
id: 20251012-122772
title: "Android Security Best Practices / Лучшие практики безопасности Android"
aliases: [Android Security Best Practices, Лучшие практики безопасности Android]
topic: android
subtopics: [permissions, keystore-crypto, network-security-config]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-encryption, c-permissions, q-certificate-pinning--security--medium]
created: 2025-10-15
updated: 2025-01-25
tags: [android/permissions, android/keystore-crypto, android/network-security-config, difficulty/medium]
sources: [https://developer.android.com/topic/security/best-practices]
---

# Вопрос (RU)
> Какие лучшие практики безопасности Android вы знаете?

# Question (EN)
> What Android security best practices do you know?

---

## Ответ (RU)

**Теория безопасности Android:**
Android использует многоуровневую архитектуру безопасности (defense-in-depth) с изоляцией приложений, системой разрешений, безопасным хранилищем и зашифрованной связью. Каждый уровень защищает от специфических векторов атак.

**Безопасность разрешений:**
App choosers предотвращают перехват чувствительных интентов вредоносными приложениями, позволяя пользователям явно выбирать доверенные приложения.

```kotlin
// Показать выбор приложения для чувствительных интентов
val intent = Intent(ACTION_SEND)
val possibleActivities = queryIntentActivities(intent, PackageManager.MATCH_ALL)

if (possibleActivities.size > 1) {
    val chooser = Intent.createChooser(intent, "Share with")
    startActivity(chooser)
}
```

**Signature-разрешения:**
Разрешения на основе подписи позволяют только приложениям, подписанным тем же сертификатом, получать доступ к защищенным ресурсам.

```xml
<permission android:name="my_custom_permission_name"
            android:protectionLevel="signature" />
```

**Безопасность Content Provider:**
Content providers с `android:exported="false"` предотвращают доступ внешних приложений к внутренним данным.

```xml
<provider
    android:name="android.support.v4.content.FileProvider"
    android:authorities="com.example.myapp.fileprovider"
    android:exported="false" />
```

**Сетевая безопасность:**
Конфигурация сетевой безопасности обеспечивает коммуникацию только через HTTPS и предотвращает незашифрованный трафик.

```xml
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>
    </domain-config>
</network-security-config>
```

**Безопасность WebView:**
Ограничение контента до списка разрешенных источников и использование безопасных каналов связи.

```kotlin
val channel = webView.createWebMessageChannel()
channel[0].setWebMessageCallback(object : WebMessagePort.WebMessageCallback() {
    override fun onMessage(port: WebMessagePort, message: WebMessage) {
        // Обработка безопасного сообщения
    }
})
```

**Безопасность хранения:**
Внутреннее хранилище изолировано для каждого приложения и автоматически удаляется при деинсталляции.

```kotlin
val file = File(filesDir, "sensitive_data.txt")
file.writeText("Private data")
```

**Зашифрованное хранилище:**
Jetpack Security обеспечивает шифрование с аппаратной поддержкой с использованием Android Keystore.

```kotlin
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val encryptedPrefs = EncryptedSharedPreferences.create(
    context, "secure_prefs", masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)
```

**Биометрическая аутентификация:**
Использование BiometricPrompt для безопасной аутентификации пользователей.

```kotlin
val biometricPrompt = BiometricPrompt(this, executor, callback)
val promptInfo = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Biometric Authentication")
    .setAllowedAuthenticators(BIOMETRIC_STRONG or DEVICE_CREDENTIAL)
    .build()
biometricPrompt.authenticate(promptInfo)
```

**Certificate Pinning:**
Привязка сертификатов предотвращает атаки man-in-the-middle.

```kotlin
val certificatePinner = CertificatePinner.Builder()
    .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    .build()
```

**Мониторинг безопасности:**
- Поддерживать зависимости обновленными
- Нацеливаться на последнюю Android SDK
- Проводить тестирование на проникновение
- Использовать инструменты статического анализа

## Answer (EN)

**Android Security Theory:**
Android uses a defense-in-depth security architecture with application sandboxing, permission system, secure storage, and encrypted communication. Each layer protects against specific attack vectors.

**Permission Security:**
App choosers prevent malicious apps from intercepting sensitive intents by allowing users to explicitly choose trusted applications.

```kotlin
// Show app chooser for sensitive intents
val intent = Intent(ACTION_SEND)
val possibleActivities = queryIntentActivities(intent, PackageManager.MATCH_ALL)

if (possibleActivities.size > 1) {
    val chooser = Intent.createChooser(intent, "Share with")
    startActivity(chooser)
}
```

**Signature-based Permissions:**
Signature-based permissions only allow apps signed with the same certificate to access protected resources.

```xml
<permission android:name="my_custom_permission_name"
            android:protectionLevel="signature" />
```

**Content Provider Security:**
Content providers with `android:exported="false"` prevent external apps from accessing internal data.

```xml
<provider
    android:name="android.support.v4.content.FileProvider"
    android:authorities="com.example.myapp.fileprovider"
    android:exported="false" />
```

**Network Security:**
Network security configuration enforces HTTPS-only communication and prevents cleartext traffic.

```xml
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>
    </domain-config>
</network-security-config>
```

**WebView Security:**
Restrict content to allowlisted sources and use secure communication channels.

```kotlin
val channel = webView.createWebMessageChannel()
channel[0].setWebMessageCallback(object : WebMessagePort.WebMessageCallback() {
    override fun onMessage(port: WebMessagePort, message: WebMessage) {
        // Handle secure message
    }
})
```

**Data Storage Security:**
Internal storage is sandboxed per app and automatically deleted on uninstall.

```kotlin
val file = File(filesDir, "sensitive_data.txt")
file.writeText("Private data")
```

**Encrypted Storage:**
Jetpack Security provides hardware-backed encryption using Android Keystore.

```kotlin
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val encryptedPrefs = EncryptedSharedPreferences.create(
    context, "secure_prefs", masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)
```

**Biometric Authentication:**
Use BiometricPrompt for secure user authentication.

```kotlin
val biometricPrompt = BiometricPrompt(this, executor, callback)
val promptInfo = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Biometric Authentication")
    .setAllowedAuthenticators(BIOMETRIC_STRONG or DEVICE_CREDENTIAL)
    .build()
biometricPrompt.authenticate(promptInfo)
```

**Certificate Pinning:**
Certificate pinning prevents man-in-the-middle attacks.

```kotlin
val certificatePinner = CertificatePinner.Builder()
    .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    .build()
```

**Security Monitoring:**
- Keep dependencies updated
- Target latest Android SDK
- Perform penetration testing
- Use static analysis tools

---

## Follow-ups

- How do you implement certificate pinning for different environments?
- What are the security implications of using WebView in Android apps?
- How do you handle sensitive data in memory to prevent memory dumps?

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
