---
id: "20251015082237358"
title: "App Security Best Practices / Лучшие практики безопасности приложения"
topic: security
difficulty: medium
status: draft
created: 2025-10-15
tags: [best-practices, audit, vulnerabilities, owasp, hardening, difficulty/medium]
---
# App Security Best Practices / Best Practices безопасности приложений

**English**: Implement comprehensive security best practices: secure network communication with certificate pinning, encrypted storage, code obfuscation, root detection, and secure coding patterns.

## Answer (EN)
Comprehensive **Android app security** requires a multi-layered approach covering network security, data protection, code security, and runtime protection. Following OWASP Mobile Top 10 guidelines and implementing defense-in-depth strategies ensures robust application security.

### Security Layers

1. **Network Security**: HTTPS, certificate pinning, cleartext prevention
2. **Data Security**: Encryption at rest, secure preferences, keystore
3. **Code Security**: ProGuard/R8, tamper detection, root detection
4. **Runtime Security**: Debugger detection, emulator detection
5. **Input Validation**: SQL injection prevention, XSS protection

### Complete Security Implementation

#### 1. Network Security Configuration

```kotlin
import okhttp3.CertificatePinner
import okhttp3.OkHttpClient
import java.util.concurrent.TimeUnit

/**
 * Secure network client with certificate pinning
 */
class SecureNetworkClient(private val context: Context) {

    companion object {
        private const val API_DOMAIN = "api.example.com"
        // SHA256 hash of certificate public key
        private const val CERTIFICATE_PIN_1 = "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
        private const val CERTIFICATE_PIN_2 = "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB="
    }

    /**
     * Create secure OkHttpClient with certificate pinning
     */
    fun createSecureClient(): OkHttpClient {
        val certificatePinner = CertificatePinner.Builder()
            .add(API_DOMAIN, CERTIFICATE_PIN_1)
            .add(API_DOMAIN, CERTIFICATE_PIN_2) // Backup pin for rotation
            .build()

        return OkHttpClient.Builder()
            .certificatePinner(certificatePinner)
            .addInterceptor(SecurityHeadersInterceptor())
            .addInterceptor(RequestSigningInterceptor())
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    /**
     * Add security headers to all requests
     */
    private class SecurityHeadersInterceptor : Interceptor {
        override fun intercept(chain: Interceptor.Chain): Response {
            val request = chain.request().newBuilder()
                .addHeader("X-App-Version", BuildConfig.VERSION_NAME)
                .addHeader("X-Platform", "Android")
                .addHeader("X-Device-Id", getDeviceId())
                .build()

            return chain.proceed(request)
        }

        private fun getDeviceId(): String {
            // Use Android ID (not IMEI which requires permission)
            return Settings.Secure.getString(
                context.contentResolver,
                Settings.Secure.ANDROID_ID
            ) ?: "unknown"
        }
    }

    /**
     * Sign requests with HMAC
     */
    private class RequestSigningInterceptor : Interceptor {
        override fun intercept(chain: Interceptor.Chain): Response {
            val request = chain.request()
            val timestamp = System.currentTimeMillis().toString()

            // Sign request with HMAC-SHA256
            val signature = signRequest(
                method = request.method,
                url = request.url.toString(),
                timestamp = timestamp,
                body = request.body?.toString() ?: ""
            )

            val signedRequest = request.newBuilder()
                .addHeader("X-Timestamp", timestamp)
                .addHeader("X-Signature", signature)
                .build()

            return chain.proceed(signedRequest)
        }

        private fun signRequest(
            method: String,
            url: String,
            timestamp: String,
            body: String
        ): String {
            val data = "$method:$url:$timestamp:$body"
            val secretKey = getApiSecret() // From secure storage

            val mac = Mac.getInstance("HmacSHA256")
            val keySpec = SecretKeySpec(secretKey.toByteArray(), "HmacSHA256")
            mac.init(keySpec)

            val signature = mac.doFinal(data.toByteArray())
            return Base64.encodeToString(signature, Base64.NO_WRAP)
        }

        private fun getApiSecret(): String {
            // Retrieve from encrypted storage or obfuscated code
            return "your-api-secret" // NEVER hardcode in production
        }
    }
}
```

#### 2. Network Security Config (XML)

```xml
<!-- res/xml/network_security_config.xml -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Production configuration -->
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>

        <!-- Certificate pinning -->
        <pin-set expiration="2025-12-31">
            <pin digest="SHA-256">AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</pin>
            <pin digest="SHA-256">BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=</pin>
        </pin-set>

        <!-- Trust only system certificates -->
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </domain-config>

    <!-- Debug configuration (only in debug builds) -->
    <debug-overrides>
        <trust-anchors>
            <certificates src="user" />
            <certificates src="system" />
        </trust-anchors>
    </debug-overrides>
</network-security-config>
```

```xml
<!-- AndroidManifest.xml -->
<application
    android:networkSecurityConfig="@xml/network_security_config"
    android:usesCleartextTraffic="false">
    <!-- ... -->
</application>
```

#### 3. Data Encryption and Secure Storage

```kotlin
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

/**
 * Comprehensive secure storage implementation
 */
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

    /**
     * Store sensitive data
     */
    fun storeAuthToken(token: String) {
        encryptedPrefs.edit()
            .putString("auth_token", token)
            .apply()
    }

    fun getAuthToken(): String? {
        return encryptedPrefs.getString("auth_token", null)
    }

    /**
     * Store API keys (better: use BuildConfig or server-side)
     */
    fun storeApiKey(key: String) {
        encryptedPrefs.edit()
            .putString("api_key", obfuscate(key))
            .apply()
    }

    fun getApiKey(): String {
        val obfuscated = encryptedPrefs.getString("api_key", null)
        return obfuscated?.let { deobfuscate(it) } ?: ""
    }

    /**
     * Simple obfuscation (not encryption, just basic protection)
     */
    private fun obfuscate(value: String): String {
        return Base64.encodeToString(
            value.reversed().toByteArray(),
            Base64.NO_WRAP
        )
    }

    private fun deobfuscate(value: String): String {
        return String(Base64.decode(value, Base64.NO_WRAP)).reversed()
    }

    /**
     * Clear all sensitive data
     */
    fun clearSecureData() {
        encryptedPrefs.edit().clear().apply()
    }

    /**
     * Check if secure storage is compromised
     */
    fun isSecureStorageIntact(): Boolean {
        return try {
            // Try to access encrypted prefs
            encryptedPrefs.all
            true
        } catch (e: Exception) {
            // Keys may have been invalidated (user changed lockscreen)
            false
        }
    }
}
```

#### 4. Root Detection

```kotlin
import java.io.File

/**
 * Detect rooted/jailbroken devices
 */
class RootDetector(private val context: Context) {

    /**
     * Comprehensive root detection
     */
    fun isDeviceRooted(): Boolean {
        return checkRootBuildTags() ||
                checkRootFiles() ||
                checkSuperuserApk() ||
                checkRootManagementApps() ||
                checkDangerousProps() ||
                checkRWPaths()
    }

    /**
     * Check build tags
     */
    private fun checkRootBuildTags(): Boolean {
        val buildTags = Build.TAGS
        return buildTags != null && buildTags.contains("test-keys")
    }

    /**
     * Check for common root files
     */
    private fun checkRootFiles(): Boolean {
        val paths = arrayOf(
            "/system/app/Superuser.apk",
            "/sbin/su",
            "/system/bin/su",
            "/system/xbin/su",
            "/data/local/xbin/su",
            "/data/local/bin/su",
            "/system/sd/xbin/su",
            "/system/bin/failsafe/su",
            "/data/local/su",
            "/su/bin/su"
        )

        return paths.any { File(it).exists() }
    }

    /**
     * Check for Superuser.apk
     */
    private fun checkSuperuserApk(): Boolean {
        val packageNames = arrayOf(
            "com.noshufou.android.su",
            "com.noshufou.android.su.elite",
            "eu.chainfire.supersu",
            "com.koushikdutta.superuser",
            "com.thirdparty.superuser",
            "com.yellowes.su",
            "com.topjohnwu.magisk"
        )

        return packageNames.any { isPackageInstalled(it) }
    }

    /**
     * Check for root management apps
     */
    private fun checkRootManagementApps(): Boolean {
        val packageNames = arrayOf(
            "com.koushikdutta.rommanager",
            "com.dimonvideo.luckypatcher",
            "com.chelpus.lackypatch",
            "com.ramdroid.appquarantine"
        )

        return packageNames.any { isPackageInstalled(it) }
    }

    private fun isPackageInstalled(packageName: String): Boolean {
        return try {
            context.packageManager.getPackageInfo(packageName, 0)
            true
        } catch (e: PackageManager.NameNotFoundException) {
            false
        }
    }

    /**
     * Check for dangerous system properties
     */
    private fun checkDangerousProps(): Boolean {
        val dangerousProps = mapOf(
            "ro.debuggable" to "1",
            "ro.secure" to "0"
        )

        return dangerousProps.any { (key, value) ->
            getSystemProperty(key) == value
        }
    }

    private fun getSystemProperty(key: String): String? {
        return try {
            val process = Runtime.getRuntime().exec("getprop $key")
            process.inputStream.bufferedReader().use { it.readText().trim() }
        } catch (e: Exception) {
            null
        }
    }

    /**
     * Check for writable system paths
     */
    private fun checkRWPaths(): Boolean {
        val paths = arrayOf(
            "/system",
            "/system/bin",
            "/system/sbin",
            "/system/xbin",
            "/vendor/bin",
            "/sbin",
            "/etc"
        )

        return paths.any { File(it).canWrite() }
    }

    /**
     * Get root detection score (0-100)
     */
    fun getRootScore(): Int {
        var score = 0

        if (checkRootBuildTags()) score += 20
        if (checkRootFiles()) score += 30
        if (checkSuperuserApk()) score += 30
        if (checkRootManagementApps()) score += 10
        if (checkDangerousProps()) score += 5
        if (checkRWPaths()) score += 5

        return score.coerceIn(0, 100)
    }
}
```

#### 5. Debugger and Emulator Detection

```kotlin
/**
 * Detect debugging and emulator environments
 */
class RuntimeSecurityChecker(private val context: Context) {

    /**
     * Check if app is being debugged
     */
    fun isDebuggerAttached(): Boolean {
        return Debug.isDebuggerConnected() || Debug.waitingForDebugger()
    }

    /**
     * Check if running on emulator
     */
    fun isEmulator(): Boolean {
        return checkBuildParameters() ||
                checkTelephonyInfo() ||
                checkHardwareInfo() ||
                checkFilesystem()
    }

    private fun checkBuildParameters(): Boolean {
        return (Build.FINGERPRINT.startsWith("generic") ||
                Build.FINGERPRINT.startsWith("unknown") ||
                Build.MODEL.contains("google_sdk") ||
                Build.MODEL.contains("Emulator") ||
                Build.MODEL.contains("Android SDK built for x86") ||
                Build.MANUFACTURER.contains("Genymotion") ||
                Build.BRAND.startsWith("generic") && Build.DEVICE.startsWith("generic") ||
                "google_sdk" == Build.PRODUCT)
    }

    private fun checkTelephonyInfo(): Boolean {
        val telephony = context.getSystemService(Context.TELEPHONY_SERVICE) as TelephonyManager
        val networkOperator = telephony.networkOperatorName

        return networkOperator.lowercase() == "android" ||
                telephony.phoneType == TelephonyManager.PHONE_TYPE_NONE
    }

    private fun checkHardwareInfo(): Boolean {
        return Build.HARDWARE.contains("goldfish") ||
                Build.HARDWARE.contains("ranchu") ||
                Build.PRODUCT.contains("sdk") ||
                Build.BOARD.contains("QC_Reference_Phone")
    }

    private fun checkFilesystem(): Boolean {
        val emulatorFiles = arrayOf(
            "/dev/socket/qemud",
            "/dev/qemu_pipe",
            "/system/lib/libc_malloc_debug_qemu.so",
            "/sys/qemu_trace",
            "/system/bin/qemu-props"
        )

        return emulatorFiles.any { File(it).exists() }
    }

    /**
     * Check if APK signature is valid
     */
    fun isSignatureValid(): Boolean {
        return try {
            val packageInfo = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                context.packageManager.getPackageInfo(
                    context.packageName,
                    PackageManager.GET_SIGNING_CERTIFICATES
                )
            } else {
                @Suppress("DEPRECATION")
                context.packageManager.getPackageInfo(
                    context.packageName,
                    PackageManager.GET_SIGNATURES
                )
            }

            val expectedSignature = getExpectedSignature()
            val actualSignature = getActualSignature(packageInfo)

            actualSignature == expectedSignature
        } catch (e: Exception) {
            false
        }
    }

    private fun getExpectedSignature(): String {
        // Store expected signature hash (from your release keystore)
        return "YOUR_EXPECTED_SIGNATURE_HASH"
    }

    private fun getActualSignature(packageInfo: PackageInfo): String {
        val signatures = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            packageInfo.signingInfo.apkContentsSigners
        } else {
            @Suppress("DEPRECATION")
            packageInfo.signatures
        }

        if (signatures.isEmpty()) return ""

        val cert = signatures[0].toByteArray()
        val md = MessageDigest.getInstance("SHA-256")
        val hash = md.digest(cert)

        return Base64.encodeToString(hash, Base64.NO_WRAP)
    }
}
```

#### 6. Input Validation and SQL Injection Prevention

```kotlin
/**
 * Secure input validation
 */
class InputValidator {

    /**
     * Sanitize user input
     */
    fun sanitizeInput(input: String): String {
        return input
            .trim()
            .replace(Regex("[<>\"']"), "") // Remove HTML/SQL characters
            .take(1000) // Limit length
    }

    /**
     * Validate email
     */
    fun isValidEmail(email: String): Boolean {
        val pattern = "[a-zA-Z0-9._-]+@[a-z]+\\.+[a-z]+"
        return email.matches(pattern.toRegex())
    }

    /**
     * Validate phone number
     */
    fun isValidPhone(phone: String): Boolean {
        val pattern = "^[+]?[0-9]{10,13}$"
        return phone.matches(pattern.toRegex())
    }

    /**
     * SQL injection prevention (use Room instead)
     */
    fun sanitizeSqlInput(input: String): String {
        return input.replace("'", "''") // Escape single quotes
    }

    /**
     * Prevent XSS in WebView
     */
    fun sanitizeForWebView(input: String): String {
        return input
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\"", "&quot;")
            .replace("'", "&#39;")
    }
}

/**
 * Use Room to prevent SQL injection
 */
@Dao
interface SecureUserDao {

    // SAFE: Room uses parameterized queries
    @Query("SELECT * FROM users WHERE email = :email")
    suspend fun getUserByEmail(email: String): User?

    // UNSAFE: Don't use raw queries with user input
    // @RawQuery
    // suspend fun unsafeQuery(query: SupportSQLiteQuery): List<User>
}
```

### Security Audit Checklist

```kotlin
/**
 * Comprehensive security audit
 */
class SecurityAudit(private val context: Context) {

    data class AuditResult(
        val score: Int,
        val issues: List<SecurityIssue>,
        val recommendations: List<String>
    )

    data class SecurityIssue(
        val severity: Severity,
        val category: Category,
        val description: String
    )

    enum class Severity { CRITICAL, HIGH, MEDIUM, LOW }
    enum class Category {
        NETWORK, DATA, CODE, RUNTIME, INPUT
    }

    /**
     * Run comprehensive security audit
     */
    fun runSecurityAudit(): AuditResult {
        val issues = mutableListOf<SecurityIssue>()
        var score = 100

        // Network security checks
        if (!isHttpsOnlyEnforced()) {
            issues.add(SecurityIssue(
                Severity.CRITICAL,
                Category.NETWORK,
                "HTTPS not enforced - cleartext traffic allowed"
            ))
            score -= 20
        }

        if (!isCertificatePinningEnabled()) {
            issues.add(SecurityIssue(
                Severity.HIGH,
                Category.NETWORK,
                "Certificate pinning not implemented"
            ))
            score -= 15
        }

        // Data security checks
        if (!isDataEncrypted()) {
            issues.add(SecurityIssue(
                Severity.CRITICAL,
                Category.DATA,
                "Sensitive data not encrypted"
            ))
            score -= 20
        }

        // Code security checks
        if (!isCodeObfuscated()) {
            issues.add(SecurityIssue(
                Severity.HIGH,
                Category.CODE,
                "Code not obfuscated with ProGuard/R8"
            ))
            score -= 10
        }

        // Runtime security checks
        val rootDetector = RootDetector(context)
        if (rootDetector.isDeviceRooted()) {
            issues.add(SecurityIssue(
                Severity.HIGH,
                Category.RUNTIME,
                "App running on rooted device"
            ))
            score -= 15
        }

        val runtimeChecker = RuntimeSecurityChecker(context)
        if (runtimeChecker.isDebuggerAttached()) {
            issues.add(SecurityIssue(
                Severity.CRITICAL,
                Category.RUNTIME,
                "Debugger attached to app"
            ))
            score -= 25
        }

        // Generate recommendations
        val recommendations = generateRecommendations(issues)

        return AuditResult(
            score = score.coerceIn(0, 100),
            issues = issues,
            recommendations = recommendations
        )
    }

    private fun isHttpsOnlyEnforced(): Boolean {
        // Check network security config
        return true // Implement actual check
    }

    private fun isCertificatePinningEnabled(): Boolean {
        // Check if certificate pinning is configured
        return true // Implement actual check
    }

    private fun isDataEncrypted(): Boolean {
        // Check if EncryptedSharedPreferences is used
        return true // Implement actual check
    }

    private fun isCodeObfuscated(): Boolean {
        // In debug build, check if classes are obfuscated
        return !BuildConfig.DEBUG
    }

    private fun generateRecommendations(issues: List<SecurityIssue>): List<String> {
        return issues.map { issue ->
            when (issue.category) {
                Category.NETWORK -> "Implement HTTPS-only and certificate pinning"
                Category.DATA -> "Use EncryptedSharedPreferences and Android Keystore"
                Category.CODE -> "Enable ProGuard/R8 in release builds"
                Category.RUNTIME -> "Implement root detection and app hardening"
                Category.INPUT -> "Validate and sanitize all user inputs"
            }
        }.distinct()
    }

    /**
     * Get security score with breakdown
     */
    fun getDetailedSecurityScore(): Map<String, Int> {
        return mapOf(
            "Network Security" to assessNetworkSecurity(),
            "Data Security" to assessDataSecurity(),
            "Code Security" to assessCodeSecurity(),
            "Runtime Security" to assessRuntimeSecurity(),
            "Input Validation" to assessInputValidation()
        )
    }

    private fun assessNetworkSecurity(): Int {
        var score = 100
        if (!isHttpsOnlyEnforced()) score -= 30
        if (!isCertificatePinningEnabled()) score -= 20
        return score.coerceIn(0, 100)
    }

    private fun assessDataSecurity(): Int {
        var score = 100
        if (!isDataEncrypted()) score -= 40
        return score.coerceIn(0, 100)
    }

    private fun assessCodeSecurity(): Int {
        var score = 100
        if (!isCodeObfuscated()) score -= 25
        return score.coerceIn(0, 100)
    }

    private fun assessRuntimeSecurity(): Int {
        var score = 100
        val rootDetector = RootDetector(context)
        if (rootDetector.isDeviceRooted()) score -= 30

        val runtimeChecker = RuntimeSecurityChecker(context)
        if (runtimeChecker.isDebuggerAttached()) score -= 40
        if (runtimeChecker.isEmulator()) score -= 20

        return score.coerceIn(0, 100)
    }

    private fun assessInputValidation(): Int {
        // Check if proper input validation is implemented
        return 100 // Implement actual assessment
    }
}
```

### Best Practices (20+ Items)

1. **Always use HTTPS**: Never send sensitive data over HTTP
2. **Implement certificate pinning**: Prevent MITM attacks
3. **Encrypt data at rest**: Use EncryptedSharedPreferences
4. **Use Android Keystore**: For cryptographic keys
5. **Enable ProGuard/R8**: Obfuscate code in release builds
6. **Validate all inputs**: Prevent injection attacks
7. **Implement root detection**: Warn users on rooted devices
8. **Detect debugger**: Prevent reverse engineering
9. **Sign requests**: Use HMAC for request integrity
10. **Never hardcode secrets**: Use BuildConfig or server
11. **Use SafetyNet**: Verify device integrity
12. **Implement app attestation**: Verify app authenticity
13. **Clear sensitive data**: From memory after use
14. **Disable screenshots**: For sensitive screens
15. **Use secure random**: For tokens and IDs
16. **Implement timeout**: For sensitive operations
17. **Log securely**: Never log sensitive data
18. **Update dependencies**: Patch security vulnerabilities
19. **Use least privilege**: Request minimal permissions
20. **Test security**: Regular penetration testing

### Common Pitfalls

1. **Hardcoded API Keys**
   ```kotlin
   // BAD
   const val API_KEY = "sk_live_1234567890"

   // GOOD
   val apiKey = BuildConfig.API_KEY // From build config
   ```

2. **Cleartext Traffic**
   ```xml
   <!-- BAD -->
   <application android:usesCleartextTraffic="true">

   <!-- GOOD -->
   <application android:usesCleartextTraffic="false">
   ```

3. **Unencrypted Storage**
   ```kotlin
   // BAD
   sharedPrefs.edit().putString("token", token).apply()

   // GOOD
   encryptedPrefs.edit().putString("token", token).apply()
   ```

4. **No Input Validation**
   ```kotlin
   // BAD
   db.query("SELECT * FROM users WHERE name = '$userInput'")

   // GOOD
   db.query("SELECT * FROM users WHERE name = ?", arrayOf(userInput))
   ```

5. **Ignoring Root Detection**
   ```kotlin
   // BAD: Ignore rooted devices

   // GOOD: Detect and respond appropriately
   if (rootDetector.isDeviceRooted()) {
       showRootWarning()
   }
   ```

### Summary

Comprehensive Android security requires:

- **Network Security**: HTTPS, certificate pinning, request signing
- **Data Security**: Encryption at rest, secure keystore usage
- **Code Security**: ProGuard/R8, tamper detection
- **Runtime Security**: Root detection, debugger detection
- **Input Validation**: Sanitization, parameterized queries
- **Regular Audits**: Security scanning and penetration testing

**OWASP Mobile Top 10 Coverage**:
1. Improper Platform Usage 
2. Insecure Data Storage 
3. Insecure Communication 
4. Insecure Authentication 
5. Insufficient Cryptography 
6. Insecure Authorization 
7. Client Code Quality 
8. Code Tampering 
9. Reverse Engineering 
10. Extraneous Functionality 

**Security Maturity Levels**:
- **Level 1**: Basic HTTPS and encryption
- **Level 2**: Certificate pinning, root detection
- **Level 3**: Code obfuscation, tamper detection
- **Level 4**: Advanced hardening, penetration testing
- **Level 5**: Continuous security monitoring

---

## Ответ (RU)
Комплексная **безопасность Android приложений** требует многоуровневого подхода, охватывающего безопасность сети, защиту данных, безопасность кода и защиту во время выполнения.

### Слои безопасности

1. **Безопасность сети**: HTTPS, certificate pinning
2. **Безопасность данных**: Шифрование, Keystore
3. **Безопасность кода**: ProGuard/R8, обнаружение вмешательства
4. **Безопасность выполнения**: Обнаружение root, отладчика
5. **Валидация ввода**: Предотвращение SQL-инъекций

### Реализация

```kotlin
// Безопасный сетевой клиент
class SecureNetworkClient {

    fun createSecureClient(): OkHttpClient {
        val certificatePinner = CertificatePinner.Builder()
            .add("api.example.com", "sha256/AAAA...")
            .build()

        return OkHttpClient.Builder()
            .certificatePinner(certificatePinner)
            .build()
    }
}

// Безопасное хранилище
class SecureStorageManager(context: Context) {

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
}

// Обнаружение root
class RootDetector {

    fun isDeviceRooted(): Boolean {
        return checkRootFiles() ||
                checkSuperuserApk() ||
                checkRootManagementApps()
    }
}

// Обнаружение отладчика
class RuntimeSecurityChecker {

    fun isDebuggerAttached(): Boolean {
        return Debug.isDebuggerConnected()
    }

    fun isEmulator(): Boolean {
        return checkBuildParameters() ||
                checkHardwareInfo()
    }
}
```

### Чеклист безопасности (20+ пунктов)

1. Всегда использовать HTTPS
2. Реализовать certificate pinning
3. Шифровать данные в покое
4. Использовать Android Keystore
5. Включить ProGuard/R8
6. Валидировать все вводы
7. Обнаруживать root
8. Обнаруживать отладчик
9. Подписывать запросы
10. Не хардкодить секреты
11. Использовать SafetyNet
12. Очищать чувствительные данные
13. Отключать скриншоты
14. Использовать безопасный random
15. Реализовать timeout
16. Безопасное логирование
17. Обновлять зависимости
18. Минимальные разрешения
19. Тестировать безопасность
20. Регулярные аудиты

### Резюме

Комплексная безопасность Android включает:

- **Сетевая безопасность**: HTTPS, pinning
- **Безопасность данных**: Шифрование, Keystore
- **Безопасность кода**: ProGuard, обнаружение
- **Защита выполнения**: Root, отладчик
- **Валидация**: Санитизация, параметризация
- **Регулярные аудиты**: Сканирование, тестирование

**Покрытие OWASP Mobile Top 10**: Все 10 категорий уязвимостей покрыты защитными мерами.

---

## Related Questions

### Related (Medium)
- [[q-android-security-practices-checklist--android--medium]] - Security
- [[q-encrypted-file-storage--security--medium]] - Security
- [[q-database-encryption-android--android--medium]] - Security
- [[q-runtime-permissions-best-practices--permissions--medium]] - Security
- [[q-data-encryption-at-rest--security--medium]] - Security
