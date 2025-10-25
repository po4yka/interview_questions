---
id: 20251012-122781
title: App Security Best Practices / Лучшие практики безопасности приложения
aliases:
- App Security Best Practices
- Лучшие практики безопасности приложения
topic: android
subtopics:
- permissions
- architecture-clean
- keystore-crypto
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-android-security-best-practices--android--medium
- q-android-keystore-system--security--medium
- q-android-security-practices-checklist--android--medium
created: 2025-10-15
updated: 2025-10-15
tags:
- android/permissions
- android/architecture-clean
- android/keystore-crypto
- difficulty/medium
---

# Вопрос (RU)
> Что такое Лучшие практики безопасности приложения?

---

# Question (EN)
> What are App Security Best Practices?

## Answer (EN)
**Android App Security** requires a multi-layered defense-in-depth approach covering network security, data protection, code security, and runtime protection. Following OWASP Mobile Top 10 guidelines ensures comprehensive application security.

**Security Architecture Theory:**
Defense-in-depth implements multiple security layers where each layer provides protection even if others fail. This includes network [[c-encryption]], data encryption at rest, code obfuscation, runtime protection, and input validation to create overlapping security controls.

**1. Network Security with Certificate Pinning:**

**Certificate Pinning Implementation:**
Prevents man-in-the-middle attacks by pinning specific certificates. Uses OkHttp CertificatePinner to validate server certificates against known public key hashes, ensuring communication only with trusted servers.

```kotlin
class SecureNetworkClient(private val context: Context) {

    companion object {
        private const val API_DOMAIN = "api.example.com"
        // SHA256 hash of certificate public key
        private const val CERTIFICATE_PIN = "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    }

    fun createSecureClient(): OkHttpClient {
        val certificatePinner = CertificatePinner.Builder()
            .add(API_DOMAIN, CERTIFICATE_PIN)
            .build()

        return OkHttpClient.Builder()
            .certificatePinner(certificatePinner)
            .addInterceptor(SecurityHeadersInterceptor())
            .connectTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    // Add security headers to all requests
    private class SecurityHeadersInterceptor : Interceptor {
        override fun intercept(chain: Interceptor.Chain): Response {
            val request = chain.request().newBuilder()
                .addHeader("X-App-Version", BuildConfig.VERSION_NAME)
                .addHeader("X-Platform", "Android")
                .build()

            return chain.proceed(request)
        }
    }
}
```

**2. Encrypted Data Storage:**

**Secure Storage Implementation:**
Uses Android Keystore for key management and EncryptedSharedPreferences for data encryption. Keys are hardware-backed when available, providing strong protection against extraction.

```kotlin
class SecureStorageManager(private val context: Context) {

    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val encryptedPrefs = EncryptedSharedPreferences.create(
        context,
        "secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun storeToken(token: String) {
        encryptedPrefs.edit().putString("token", token).apply()
    }

    fun getToken(): String? {
        return encryptedPrefs.getString("token", null)
    }

    fun clearSensitiveData() {
        encryptedPrefs.edit().clear().apply()
    }
}
```

**3. Root Detection and Runtime Security:**

**Device Security Validation:**
Detects rooted devices and debugger attachment to prevent reverse engineering and tampering. Uses multiple detection methods for comprehensive coverage.

```kotlin
class SecurityChecker {

    fun isDeviceRooted(): Boolean {
        return checkRootFiles() || checkSuperuserApk() || checkRootManagementApps()
    }

    private fun checkRootFiles(): Boolean {
        val rootFiles = arrayOf(
            "/system/app/Superuser.apk",
            "/sbin/su",
            "/system/bin/su",
            "/system/xbin/su"
        )
        return rootFiles.any { File(it).exists() }
    }

    private fun checkSuperuserApk(): Boolean {
        val packageManager = context.packageManager
        return try {
            packageManager.getPackageInfo("com.noshufou.android.su", 0)
            true
        } catch (e: PackageManager.NameNotFoundException) {
            false
        }
    }

    fun isDebuggerAttached(): Boolean {
        return Debug.isDebuggerConnected()
    }

    fun isEmulator(): Boolean {
        return Build.FINGERPRINT.startsWith("generic") ||
                Build.MODEL.contains("google_sdk") ||
                Build.MANUFACTURER.contains("Genymotion")
    }
}
```

**4. Code Obfuscation and ProGuard:**

**Code Protection Configuration:**
Enables R8/ProGuard obfuscation to make reverse engineering difficult. Removes debug information and renames classes/methods to meaningless names.

```gradle
// build.gradle (app)
android {
    buildTypes {
        release {
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
            signingConfig signingConfigs.release
        }
    }
}
```

**5. Input Validation and SQL Injection Prevention:**

**Secure Input Handling:**
Validates and sanitizes all user inputs to prevent injection attacks. Uses parameterized queries and input validation patterns.

```kotlin
class SecureInputValidator {

    fun validateEmail(email: String): Boolean {
        val emailPattern = "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$".toRegex()
        return emailPattern.matches(email)
    }

    fun sanitizeInput(input: String): String {
        return input.replace(Regex("[<>\"'&]"), "")
    }

    // Room database with parameterized queries
    @Query("SELECT * FROM users WHERE email = :email AND password = :password")
    suspend fun authenticateUser(email: String, password: String): User?
}
```

**6. Network Security Configuration:**

**HTTPS Enforcement:**
Disables cleartext traffic and enforces HTTPS for all network communication. Uses network security config for certificate pinning.

```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set expiration="2025-12-31">
            <pin digest="SHA-256">AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

**7. Biometric Authentication:**

**Secure Authentication:**
Implements biometric authentication using AndroidX Biometric library for secure user authentication without storing passwords.

```kotlin
class BiometricAuthManager(private val context: Context) {

    fun authenticate(callback: (Boolean) -> Unit) {
        val biometricPrompt = BiometricPrompt(
            context as FragmentActivity,
            ContextCompat.getMainExecutor(context),
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    callback(true)
                }

                override fun onAuthenticationFailed() {
                    callback(false)
                }
            }
        )

        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Biometric Authentication")
            .setSubtitle("Use your fingerprint or face")
            .setNegativeButtonText("Cancel")
            .build()

        biometricPrompt.authenticate(promptInfo)
    }
}
```

**8. Secure Random Number Generation:**

**Cryptographically Secure Random:**
Uses SecureRandom for generating cryptographic keys, tokens, and nonces to ensure unpredictability and security.

```kotlin
class SecureRandomGenerator {

    fun generateSecureToken(length: Int = 32): String {
        val random = SecureRandom()
        val bytes = ByteArray(length)
        random.nextBytes(bytes)
        return Base64.encodeToString(bytes, Base64.NO_WRAP)
    }

    fun generateSecureKey(): SecretKey {
        val keyGenerator = KeyGenerator.getInstance("AES")
        keyGenerator.init(256)
        return keyGenerator.generateKey()
    }
}
```

**Security Checklist:**
- Enable HTTPS with certificate pinning
- Encrypt sensitive data at rest using Android Keystore
- Implement code obfuscation with R8/ProGuard
- Validate and sanitize all user inputs
- Detect rooted devices and debugger attachment
- Use biometric authentication where appropriate
- Generate cryptographically secure random numbers
- Disable cleartext traffic
- Implement proper session management
- Regular security audits and dependency updates
- Use minimal required permissions
- Secure logging (no sensitive data)
- Implement timeout mechanisms
- Clear sensitive data from memory
- Use SafetyNet Attestation for additional validation

## Follow-ups

- How do you implement certificate pinning rotation?
- What's the difference between obfuscation and encryption?
- How do you handle security in offline scenarios?
- What are the trade-offs of different encryption algorithms?

## References

- [OWASP Mobile Top 10](https://owasp.org/www-project-mobile-top-10/)
- [Android Security Best Practices](https://developer.android.com/topic/security/best-practices)

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]]
- [[q-android-manifest-file--android--easy]]

### Related (Same Level)
- [[q-android-security-best-practices--android--medium]]
- [[q-android-keystore-system--security--medium]]
- [[q-android-security-practices-checklist--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]