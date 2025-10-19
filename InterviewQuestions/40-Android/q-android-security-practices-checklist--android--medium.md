---
id: 20251005-215456
title: Android Security Practices Checklist / Чек-лист практик безопасности Android
aliases: [Android Security Practices Checklist, Чек-лист практик безопасности Android]
topic: android
subtopics: [security, best-practices, data-protection]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
created: 2025-10-05
updated: 2025-10-15
tags: [android/security, android/best-practices, android/data-protection, security, checklist, data-protection, difficulty/medium]
source: https://github.com/Kirchhoff-Android-Interview-Questions
related: [q-android-security-best-practices--android--medium, q-android-keystore-system--security--medium, q-android-manifest-file--android--easy]
---
# Question (EN)
> What security practices checklist do you follow for Android development?

# Вопрос (RU)
> Какой чек-лист практик безопасности вы используете для разработки Android?

---

## Answer (EN)

**Android Security Practices Checklist** provides a systematic approach to implementing security measures throughout the Android development lifecycle, ensuring comprehensive protection against common vulnerabilities and attack vectors.

**Security Checklist Theory:**
A security checklist serves as a systematic verification tool to ensure all critical security measures are implemented. It covers multiple security domains: data protection, network security, authentication, code protection, and runtime security.

**Intent Security:**
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

**Intent Security Theory:**
App choosers prevent malicious apps from intercepting sensitive intents by allowing users to explicitly choose trusted applications. This prevents data leakage through intent hijacking attacks.

**Permission Security:**
Signature-based permissions enable secure communication between apps signed with the same certificate, bypassing user permission dialogs for trusted internal components.

```xml
<!-- Signature-based permissions -->
    <permission android:name="my_custom_permission_name"
                android:protectionLevel="signature" />
```

**Content Provider Security:**
Content providers expose data to other apps. Disabling external access prevents unauthorized apps from accessing sensitive internal data through content provider attacks.

```xml
<!-- Disable external access -->
        <provider
            android:name="android.support.v4.content.FileProvider"
            android:authorities="com.example.myapp.fileprovider"
    android:exported="false" />
```

**Network Security:**
HTTPS encryption protects data in transit from interception and man-in-the-middle attacks, ensuring secure communication between the app and servers.

```kotlin
// HTTPS communication
val url = URL("https://api.example.com")
val connection = url.openConnection() as HttpsURLConnection
connection.connect()
```

**Network Security Configuration:**
Network Security Config enforces HTTPS-only communication and prevents cleartext traffic, providing centralized control over network security policies.

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

**WebView Security:**
WebView components can execute malicious JavaScript and access device resources. Secure message channels provide controlled communication between native code and web content.

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

**Data Storage Security:**
Different storage locations provide varying levels of security. Internal storage is sandboxed per app, while external storage is accessible to other apps and users.

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

**Modern Security Practices:**
Code obfuscation and minification make reverse engineering difficult while reducing app size, protecting intellectual property and sensitive logic.

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
Jetpack Security provides hardware-backed encryption using Android Keystore, ensuring sensitive data remains protected even if the device is compromised.

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
```

**Biometric Authentication:**
Biometric authentication provides secure user verification using device biometric sensors, offering stronger security than traditional passwords.

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
Certificate pinning ensures communication only with trusted servers by validating specific certificates, preventing man-in-the-middle attacks even with compromised certificate authorities.

```kotlin
val certificatePinner = CertificatePinner.Builder()
    .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build()
```

**Security Checklist Items:**
- **Intent Security**: Use app choosers for sensitive intents. Prevents malicious apps from intercepting sensitive data by allowing users to explicitly choose trusted applications.
- **Permission Security**: Apply signature-based permissions for trusted apps. Enables seamless data sharing between apps signed with the same certificate without user interaction.
- **Content Provider Security**: Disable external access with `android:exported="false"`. Prevents unauthorized apps from accessing internal data through content provider attacks.
- **Network Security**: Enforce HTTPS-only communication. Protects data in transit from interception and man-in-the-middle attacks.
- **WebView Security**: Restrict content to allowlisted sources. Prevents malicious websites from executing code or accessing device resources.
- **Data Storage**: Use internal storage for sensitive data. Ensures data is sandboxed per app and automatically deleted on uninstall.
- **Code Protection**: Enable R8 obfuscation and minification. Makes reverse engineering difficult and reduces app size.
- **Encryption**: Use Jetpack Security for sensitive data. Provides hardware-backed encryption using Android Keystore for maximum security.
- **Authentication**: Implement biometric authentication. Provides secure user verification using device biometric sensors.
- **Certificate Pinning**: Prevent MITM attacks. Ensures communication only with trusted servers by pinning specific certificates.
- **Dependency Management**: Keep dependencies updated. Prevents exploitation of known vulnerabilities in third-party libraries.
- **Static Analysis**: Use Android Lint and Detekt. Identifies security vulnerabilities and code quality issues during development.
- **Penetration Testing**: Regular security audits. Validates security measures through simulated attacks and vulnerability assessments.

## Ответ (RU)

**Чек-лист практик безопасности Android** предоставляет систематический подход к реализации мер безопасности на протяжении всего жизненного цикла разработки Android, обеспечивая комплексную защиту от распространенных уязвимостей и векторов атак.

**Теория чек-листа безопасности:**
Чек-лист безопасности служит систематическим инструментом проверки для обеспечения реализации всех критических мер безопасности. Он охватывает несколько доменов безопасности: защита данных, сетевая безопасность, аутентификация, защита кода и безопасность во время выполнения.

**Безопасность интентов:**
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

**Теория безопасности интентов:**
Селекторы приложений предотвращают перехват чувствительных интентов вредоносными приложениями, позволяя пользователям явно выбирать доверенные приложения. Это предотвращает утечку данных через атаки перехвата интентов.

**Безопасность разрешений:**
Разрешения на основе подписи обеспечивают безопасную связь между приложениями, подписанными одним сертификатом, обходя диалоги разрешений пользователя для доверенных внутренних компонентов.

```xml
<!-- Разрешения на основе подписи -->
    <permission android:name="my_custom_permission_name"
                android:protectionLevel="signature" />
```

**Безопасность Content Provider:**
Content Provider предоставляют данные другим приложениям. Отключение внешнего доступа предотвращает доступ неавторизованных приложений к чувствительным внутренним данным через атаки на content provider.

```xml
<!-- Отключить внешний доступ -->
        <provider
            android:name="android.support.v4.content.FileProvider"
            android:authorities="com.example.myapp.fileprovider"
    android:exported="false" />
```

**Сетевая безопасность:**
HTTPS шифрование защищает данные в пути от перехвата и атак "человек посередине", обеспечивая безопасную связь между приложением и серверами.

```kotlin
// HTTPS связь
val url = URL("https://api.example.com")
val connection = url.openConnection() as HttpsURLConnection
connection.connect()
```

**Конфигурация сетевой безопасности:**
Network Security Config принудительно использует только HTTPS связь и предотвращает передачу открытого текста, обеспечивая централизованный контроль над политиками сетевой безопасности.

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

**Безопасность WebView:**
Компоненты WebView могут выполнять вредоносный JavaScript и получать доступ к ресурсам устройства. Безопасные каналы сообщений обеспечивают контролируемую связь между нативным кодом и веб-контентом.

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

**Безопасность хранения данных:**
Разные места хранения обеспечивают различные уровни безопасности. Внутреннее хранилище изолировано для каждого приложения, а внешнее хранилище доступно другим приложениям и пользователям.

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

**Современные практики безопасности:**
Обфускация и минификация кода усложняют обратную инженерию и уменьшают размер приложения, защищая интеллектуальную собственность и чувствительную логику.

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
Jetpack Security обеспечивает аппаратное шифрование с использованием Android Keystore, гарантируя защиту чувствительных данных даже при компрометации устройства.

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
```

**Биометрическая аутентификация:**
Биометрическая аутентификация обеспечивает безопасную верификацию пользователя с использованием биометрических датчиков устройства, предлагая более сильную безопасность по сравнению с традиционными паролями.

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
Закрепление сертификатов обеспечивает связь только с доверенными серверами путем проверки конкретных сертификатов, предотвращая атаки "человек посередине" даже при компрометации центров сертификации.

```kotlin
val certificatePinner = CertificatePinner.Builder()
    .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build()
```

**Пункты чек-листа безопасности:**
- **Безопасность интентов**: Использовать селекторы приложений для чувствительных интентов. Предотвращает перехват чувствительных данных вредоносными приложениями, позволяя пользователям явно выбирать доверенные приложения.
- **Безопасность разрешений**: Применять разрешения на основе подписи для доверенных приложений. Обеспечивает бесшовный обмен данными между приложениями, подписанными одним сертификатом, без взаимодействия с пользователем.
- **Безопасность Content Provider**: Отключать внешний доступ с `android:exported="false"`. Предотвращает доступ неавторизованных приложений к внутренним данным через атаки на content provider.
- **Сетевая безопасность**: Принудительно использовать только HTTPS связь. Защищает данные в пути от перехвата и атак "человек посередине".
- **Безопасность WebView**: Ограничивать контент только разрешенными источниками. Предотвращает выполнение кода или доступ к ресурсам устройства вредоносными веб-сайтами.
- **Хранение данных**: Использовать внутреннее хранилище для чувствительных данных. Обеспечивает изоляцию данных для каждого приложения и автоматическое удаление при деинсталляции.
- **Защита кода**: Включать обфускацию и минификацию R8. Усложняет обратную инженерию и уменьшает размер приложения.
- **Шифрование**: Использовать Jetpack Security для чувствительных данных. Обеспечивает аппаратное шифрование с использованием Android Keystore для максимальной безопасности.
- **Аутентификация**: Реализовать биометрическую аутентификацию. Обеспечивает безопасную верификацию пользователя с использованием биометрических датчиков устройства.
- **Закрепление сертификатов**: Предотвращать атаки MITM. Обеспечивает связь только с доверенными серверами путем закрепления конкретных сертификатов.
- **Управление зависимостями**: Поддерживать зависимости в актуальном состоянии. Предотвращает эксплуатацию известных уязвимостей в сторонних библиотеках.
- **Статический анализ**: Использовать Android Lint и Detekt. Выявляет уязвимости безопасности и проблемы качества кода во время разработки.
- **Тестирование на проникновение**: Регулярные аудиты безопасности. Проверяет меры безопасности через имитацию атак и оценку уязвимостей.

---

## Follow-ups

- How do you prioritize security checklist items for different app types?
- What tools do you use to automate security checklist verification?
- How do you handle security checklist compliance in CI/CD pipelines?

## References

- https://developer.android.com/topic/security/best-practices
- https://developer.android.com/training/articles/security-tips

## Related Questions

### Prerequisites (Easier)
- [[q-android-manifest-file--android--easy]] - Manifest configuration
- [[q-android-app-components--android--easy]] - App components

### Related (Medium)
- [[q-android-security-best-practices--android--medium]] - Security best practices
- [[q-android-keystore-system--security--medium]] - Keystore system
- [[q-android-lint-tool--android--medium]] - Code analysis

### Advanced (Harder)
- [[q-android-architectural-patterns--android--medium]] - Security patterns
- [[q-android-runtime-internals--android--hard]] - Runtime security
