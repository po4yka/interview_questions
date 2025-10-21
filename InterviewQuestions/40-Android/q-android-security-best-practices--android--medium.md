---
id: 20251012-122772
title: Android Security Best Practices / Лучшие практики безопасности Android
aliases: [Android Security Best Practices, Лучшие практики безопасности Android]
topic: android
subtopics: [permissions, keystore-crypto, network-security-config]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: reviewed
moc: moc-android
created: 2025-10-15
updated: 2025-10-15
tags: [android/permissions, android/keystore-crypto, android/network-security-config, security, best-practices, encryption, ssl, webview, difficulty/medium]
source: https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20security%20best%20practices%20you%20know.md
related: [q-android-keystore-system--security--medium, q-android-manifest-file--android--easy, q-android-lint-tool--android--medium]
---
# Question (EN)
> What security best practices for Android do you know?

# Вопрос (RU)
> Какие лучшие практики безопасности для Android вы знаете?

---

## Answer (EN)

**Android Security Best Practices** involve implementing multiple layers of protection to safeguard user data, prevent unauthorized access, and ensure secure communication between app components and external services.

**Security Architecture Theory:**
Android security follows a defense-in-depth strategy with multiple security layers: application sandboxing, permission system, secure storage, encrypted communication, and runtime protection. Each layer provides specific protection against different attack vectors.

**Permission Security:**
```kotlin
// Show app chooser for sensitive intents
val intent = Intent(ACTION_SEND)
val possibleActivities = queryIntentActivities(intent, PackageManager.MATCH_ALL)

if (possibleActivities.size > 1) {
    val chooser = Intent.createChooser(intent, "Share with")
    startActivity(chooser)
} else if (intent.resolveActivity(packageManager) != null) {
    startActivity(intent)
}
```

**Permission Theory:**
App choosers prevent malicious apps from intercepting sensitive intents by allowing users to explicitly choose trusted applications. This prevents data leakage through intent hijacking.

**Signature-based Permissions:**
```xml
<!-- Custom signature-based permission -->
<permission android:name="my_custom_permission_name"
            android:protectionLevel="signature" />
```

**Signature Permission Theory:**
Signature-based permissions only allow apps signed with the same certificate to access protected resources. This provides seamless security without user interaction for trusted apps.

**Content Provider Security:**
```xml
<!-- Disable external access to ContentProvider -->
<provider
    android:name="android.support.v4.content.FileProvider"
    android:authorities="com.example.myapp.fileprovider"
    android:exported="false" />
```

**Content Provider Theory:**
Content providers with `android:exported="false"` prevent external apps from accessing internal data. This is critical for preventing data leakage through content provider attacks.

**Network Security:**
```kotlin
// HTTPS communication
val url = URL("https://api.example.com")
val connection = url.openConnection() as HttpsURLConnection
connection.connect()
```

**Network Security Configuration:**
```xml
<!-- Manifest declaration -->
<application
    android:networkSecurityConfig="@xml/network_security_config">
</application>
```

```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>
    </domain-config>
</network-security-config>
```

**Network Security Theory:**
Network security configuration enforces HTTPS-only communication and prevents cleartext traffic. This protects against man-in-the-middle attacks and data interception.

**WebView Security:**
```kotlin
val webView: WebView = findViewById(R.id.webview)

// Secure message channels (Android 6.0+)
val channel = webView.createWebMessageChannel()
channel[0].setWebMessageCallback(object : WebMessagePort.WebMessageCallback() {
    override fun onMessage(port: WebMessagePort, message: WebMessage) {
        // Handle secure message
    }
})
channel[1].postMessage(WebMessage("Secure data"))
```

**WebView Security Theory:**
WebView security involves restricting content to allowlisted sources and using secure communication channels. JavaScript interfaces should be avoided unless completely trusted.

**Data Storage Security:**
```kotlin
// Internal storage (secure)
val file = File(filesDir, "sensitive_data.txt")
file.writeText("Private data")

// External storage (public)
val externalFile = File(getExternalFilesDir(null), "public_data.txt")

// SharedPreferences (private mode)
val prefs = getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
prefs.edit().putString("key", "value").apply()
```

**Data Storage Theory:**
Internal storage is sandboxed per app and automatically deleted on uninstall. External storage is accessible to other apps and should only store non-sensitive data.

**Modern Security Practices:**
```kotlin
// Code obfuscation (build.gradle.kts)
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
        }
    }
}
```

**Encrypted Storage:**
```kotlin
// Jetpack Security
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

encryptedPrefs.edit()
    .putString("api_key", "secret_value")
    .apply()
```

**Encryption Theory:**
Jetpack Security provides hardware-backed encryption using Android Keystore. Master keys are protected by device security features and cannot be extracted.

**Biometric Authentication:**
```kotlin
val biometricPrompt = BiometricPrompt(
    this,
    executor,
    object : BiometricPrompt.AuthenticationCallback() {
        override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
            // User authenticated
        }
    }
)

val promptInfo = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Biometric Authentication")
    .setAllowedAuthenticators(BIOMETRIC_STRONG or DEVICE_CREDENTIAL)
    .build()

biometricPrompt.authenticate(promptInfo)
```

**Certificate Pinning:**
```kotlin
val certificatePinner = CertificatePinner.Builder()
    .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build()
```

**Security Monitoring:**
- Keep dependencies updated
- Target latest Android SDK
- Perform penetration testing
- Use static analysis tools
- Monitor security advisories

## Ответ (RU)

**Лучшие практики безопасности Android** включают реализацию множественных уровней защиты для обеспечения безопасности пользовательских данных, предотвращения несанкционированного доступа и обеспечения безопасной связи между компонентами приложения и внешними сервисами.

**Теория архитектуры безопасности:**
Безопасность Android следует стратегии защиты в глубину с несколькими уровнями безопасности: изоляция приложений, система разрешений, безопасное хранение, зашифрованная связь и защита во время выполнения. Каждый уровень обеспечивает специфическую защиту от различных векторов атак.

**Безопасность разрешений:**
```kotlin
// Показать выбор приложения для чувствительных интентов
val intent = Intent(ACTION_SEND)
val possibleActivities = queryIntentActivities(intent, PackageManager.MATCH_ALL)

if (possibleActivities.size > 1) {
    val chooser = Intent.createChooser(intent, "Поделиться с")
    startActivity(chooser)
} else if (intent.resolveActivity(packageManager) != null) {
    startActivity(intent)
}
```

**Теория разрешений:**
Селекторы приложений предотвращают перехват чувствительных интентов вредоносными приложениями, позволяя пользователям явно выбирать доверенные приложения. Это предотвращает утечку данных через перехват интентов.

**Разрешения на основе подписи:**
```xml
<!-- Пользовательское разрешение на основе подписи -->
<permission android:name="my_custom_permission_name"
            android:protectionLevel="signature" />
```

**Теория разрешений на основе подписи:**
Разрешения на основе подписи позволяют доступ к защищенным ресурсам только приложениям, подписанным тем же сертификатом. Это обеспечивает бесшовную безопасность без взаимодействия с пользователем для доверенных приложений.

**Безопасность Content Provider:**
```xml
<!-- Отключить внешний доступ к ContentProvider -->
<provider
    android:name="android.support.v4.content.FileProvider"
    android:authorities="com.example.myapp.fileprovider"
    android:exported="false" />
```

**Теория Content Provider:**
Content provider с `android:exported="false"` предотвращают доступ внешних приложений к внутренним данным. Это критично для предотвращения утечки данных через атаки на content provider.

**Сетевая безопасность:**
```kotlin
// HTTPS связь
val url = URL("https://api.example.com")
val connection = url.openConnection() as HttpsURLConnection
connection.connect()
```

**Конфигурация сетевой безопасности:**
```xml
<!-- Объявление в манифесте -->
<application
    android:networkSecurityConfig="@xml/network_security_config">
</application>
```

```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>
    </domain-config>
</network-security-config>
```

**Теория сетевой безопасности:**
Конфигурация сетевой безопасности принудительно использует только HTTPS связь и предотвращает передачу открытого текста. Это защищает от атак "человек посередине" и перехвата данных.

**Безопасность WebView:**
```kotlin
val webView: WebView = findViewById(R.id.webview)

// Безопасные каналы сообщений (Android 6.0+)
val channel = webView.createWebMessageChannel()
channel[0].setWebMessageCallback(object : WebMessagePort.WebMessageCallback() {
    override fun onMessage(port: WebMessagePort, message: WebMessage) {
        // Обработка безопасного сообщения
    }
})
channel[1].postMessage(WebMessage("Безопасные данные"))
```

**Теория безопасности WebView:**
Безопасность WebView включает ограничение контента только разрешенными источниками и использование безопасных каналов связи. JavaScript интерфейсы следует избегать, если они не полностью доверены.

**Безопасность хранения данных:**
```kotlin
// Внутреннее хранилище (безопасно)
val file = File(filesDir, "sensitive_data.txt")
file.writeText("Приватные данные")

// Внешнее хранилище (публично)
val externalFile = File(getExternalFilesDir(null), "public_data.txt")

// SharedPreferences (приватный режим)
val prefs = getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
prefs.edit().putString("key", "value").apply()
```

**Теория хранения данных:**
Внутреннее хранилище изолировано для каждого приложения и автоматически удаляется при деинсталляции. Внешнее хранилище доступно другим приложениям и должно хранить только нечувствительные данные.

**Современные практики безопасности:**
```kotlin
// Обфускация кода (build.gradle.kts)
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
        }
    }
}
```

**Зашифрованное хранение:**
```kotlin
// Jetpack Security
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

encryptedPrefs.edit()
    .putString("api_key", "secret_value")
    .apply()
```

**Теория шифрования:**
Jetpack Security обеспечивает аппаратное шифрование с использованием Android Keystore. Главные ключи защищены функциями безопасности устройства и не могут быть извлечены.

**Биометрическая аутентификация:**
```kotlin
val biometricPrompt = BiometricPrompt(
    this,
    executor,
    object : BiometricPrompt.AuthenticationCallback() {
        override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
            // Пользователь аутентифицирован
        }
    }
)

val promptInfo = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Биометрическая аутентификация")
    .setAllowedAuthenticators(BIOMETRIC_STRONG or DEVICE_CREDENTIAL)
    .build()

biometricPrompt.authenticate(promptInfo)
```

**Закрепление сертификатов:**
```kotlin
val certificatePinner = CertificatePinner.Builder()
    .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build()
```

**Мониторинг безопасности:**
- Поддерживать зависимости в актуальном состоянии
- Использовать последний Android SDK
- Проводить тестирование на проникновение
- Использовать инструменты статического анализа
- Отслеживать уведомления о безопасности

---

## Follow-ups

- How do you implement certificate pinning for different environments?
- What are the security implications of using WebView in Android apps?
- How do you handle sensitive data in memory to prevent memory dumps?

## References

- https://developer.android.com/topic/security/best-practices
- https://developer.android.com/training/articles/security-tips

## Related Questions

### Prerequisites (Easier)
- [[q-android-manifest-file--android--easy]] - Manifest configuration
- [[q-android-app-components--android--easy]] - App components

### Related (Medium)
- [[q-android-keystore-system--security--medium]] - Keystore system
- [[q-android-lint-tool--android--medium]] - Code analysis
- [[q-android-build-optimization--android--medium]] - Build security

### Advanced (Harder)
- [[q-android-architectural-patterns--android--medium]] - Security patterns
- [[q-android-runtime-internals--android--hard]] - Runtime security
