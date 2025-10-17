---
id: "20251015082237531"
title: "Certificate Pinning / Закрепление сертификатов"
topic: security
difficulty: medium
status: draft
created: 2025-10-15
tags: [certificate-pinning, networking, okhttp, ssl-tls, difficulty/medium]
---
# Certificate Pinning / Закрепление сертификатов

**English**: Implement certificate pinning with OkHttp. Handle certificate rotation, pin multiple certificates including backup pins, and test implementation.

## Answer (EN)
**Certificate Pinning** is a security technique that validates a server's identity by comparing its SSL/TLS certificate against a known, pre-defined set of certificates or public keys. This prevents man-in-the-middle (MITM) attacks even if a Certificate Authority is compromised.

### Understanding Certificate Pinning

#### Why Pin Certificates?

```kotlin
// Problem: Trust chain can be compromised
// 1. Rogue CA issues fake certificate
// 2. Corporate proxy with custom CA
// 3. Government-level interception
// 4. Compromised device with custom root CA

// Solution: Pin specific certificates
// Only accept certificates you explicitly trust
```

#### Pinning Strategies

1. **Certificate Pinning**: Pin the entire certificate
   - Pros: Most secure
   - Cons: Must update app when certificate expires

2. **Public Key Pinning**: Pin only the public key
   - Pros: Survives certificate renewal if key unchanged
   - Cons: Still needs updates when key rotates

3. **Intermediate CA Pinning**: Pin intermediate CA cert
   - Pros: More flexible
   - Cons: Less secure (broader trust)

### Complete Certificate Pinning Implementation

#### 1. OkHttp CertificatePinner

```kotlin
import okhttp3.CertificatePinner
import okhttp3.OkHttpClient
import java.util.concurrent.TimeUnit

/**
 * Certificate pinning with OkHttp
 */
class CertificatePinningClient {

    companion object {
        // SHA-256 hash of certificate's public key (Base64 encoded)
        // Format: sha256/<base64-encoded-hash>
        private const val API_HOST = "api.example.com"

        // Primary certificate pin
        private const val PRIMARY_PIN = "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="

        // Backup pins (for rotation)
        private const val BACKUP_PIN_1 = "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB="
        private const val BACKUP_PIN_2 = "sha256/CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC="
    }

    /**
     * Create OkHttpClient with certificate pinning
     */
    fun createPinnedClient(): OkHttpClient {
        val certificatePinner = CertificatePinner.Builder()
            // Add primary pin
            .add(API_HOST, PRIMARY_PIN)

            // Add backup pins for rotation
            .add(API_HOST, BACKUP_PIN_1)
            .add(API_HOST, BACKUP_PIN_2)

            // Can pin multiple hosts
            .add("cdn.example.com", "sha256/...")

            // Can use wildcards
            .add("*.example.com", "sha256/...")

            .build()

        return OkHttpClient.Builder()
            .certificatePinner(certificatePinner)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()
    }
}
```

#### 2. Generate Certificate Pins

```kotlin
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.tls.HandshakeCertificates
import java.security.MessageDigest
import java.security.cert.Certificate
import java.security.cert.X509Certificate
import okio.ByteString.Companion.toByteString
import android.util.Base64

/**
 * Utility to extract and generate certificate pins
 */
object CertificatePinGenerator {

    /**
     * Generate SHA-256 pin from certificate
     */
    fun generatePin(certificate: X509Certificate): String {
        val publicKey = certificate.publicKey.encoded
        val digest = MessageDigest.getInstance("SHA-256")
        val hash = digest.digest(publicKey)
        val base64Hash = Base64.encodeToString(hash, Base64.NO_WRAP)
        return "sha256/$base64Hash"
    }

    /**
     * Extract pins from a live server
     * Use this during development to get the correct pins
     */
    fun extractPinsFromServer(hostname: String, port: Int = 443): List<String> {
        val client = OkHttpClient.Builder().build()

        val request = Request.Builder()
            .url("https://$hostname:$port")
            .build()

        val pins = mutableListOf<String>()

        try {
            val response = client.newCall(request).execute()
            val handshake = response.handshake

            handshake?.peerCertificates?.forEach { certificate ->
                if (certificate is X509Certificate) {
                    val pin = generatePin(certificate)
                    pins.add(pin)
                    println("Certificate: ${certificate.subjectDN}")
                    println("Pin: $pin")
                    println("Valid until: ${certificate.notAfter}")
                    println("---")
                }
            }

            response.close()
        } catch (e: Exception) {
            println("Error extracting pins: ${e.message}")
        }

        return pins
    }

    /**
     * Extract pins from certificate file
     */
    fun extractPinsFromFile(certificateInputStream: InputStream): List<String> {
        val certificateFactory = CertificateFactory.getInstance("X.509")
        val certificates = certificateFactory.generateCertificates(certificateInputStream)

        return certificates.mapNotNull { cert ->
            if (cert is X509Certificate) {
                generatePin(cert)
            } else {
                null
            }
        }
    }
}

// Usage during development:
fun main() {
    // Extract pins from your server
    val pins = CertificatePinGenerator.extractPinsFromServer("api.example.com")

    println("Add these pins to your CertificatePinner:")
    pins.forEach { pin ->
        println(".add(\"api.example.com\", \"$pin\")")
    }
}
```

#### 3. Certificate Rotation Handling

```kotlin
import android.content.Context
import android.content.SharedPreferences
import okhttp3.CertificatePinner
import okhttp3.OkHttpClient
import java.util.concurrent.TimeUnit

/**
 * Certificate pinning with rotation support
 */
class RotatingCertificatePinner(
    private val context: Context
) {

    companion object {
        private const val PREFS_NAME = "certificate_pins"
        private const val KEY_PRIMARY_PIN = "primary_pin"
        private const val KEY_BACKUP_PINS = "backup_pins"
        private const val KEY_LAST_UPDATE = "last_update"

        // Default pins (shipped with app)
        private val DEFAULT_PRIMARY = "sha256/primary..."
        private val DEFAULT_BACKUPS = listOf(
            "sha256/backup1...",
            "sha256/backup2..."
        )

        private const val API_HOST = "api.example.com"
    }

    private val prefs: SharedPreferences = context.getSharedPreferences(
        PREFS_NAME,
        Context.MODE_PRIVATE
    )

    /**
     * Get current certificate pinner
     */
    fun getCertificatePinner(): CertificatePinner {
        val primaryPin = prefs.getString(KEY_PRIMARY_PIN, DEFAULT_PRIMARY)!!
        val backupPinsString = prefs.getString(KEY_BACKUP_PINS, null)
        val backupPins = backupPinsString?.split(",") ?: DEFAULT_BACKUPS

        val builder = CertificatePinner.Builder()
            .add(API_HOST, primaryPin)

        backupPins.forEach { pin ->
            builder.add(API_HOST, pin)
        }

        return builder.build()
    }

    /**
     * Update pins dynamically (from server)
     * Should be done over a secure, authenticated channel
     */
    fun updatePins(newPrimaryPin: String, newBackupPins: List<String>) {
        prefs.edit()
            .putString(KEY_PRIMARY_PIN, newPrimaryPin)
            .putString(KEY_BACKUP_PINS, newBackupPins.joinToString(","))
            .putLong(KEY_LAST_UPDATE, System.currentTimeMillis())
            .apply()
    }

    /**
     * Check if pins need updating
     */
    fun shouldUpdatePins(): Boolean {
        val lastUpdate = prefs.getLong(KEY_LAST_UPDATE, 0)
        val daysSinceUpdate = TimeUnit.MILLISECONDS.toDays(
            System.currentTimeMillis() - lastUpdate
        )

        // Update pins every 30 days
        return daysSinceUpdate > 30
    }

    /**
     * Reset to default pins
     */
    fun resetToDefaults() {
        prefs.edit()
            .putString(KEY_PRIMARY_PIN, DEFAULT_PRIMARY)
            .putString(KEY_BACKUP_PINS, DEFAULT_BACKUPS.joinToString(","))
            .putLong(KEY_LAST_UPDATE, System.currentTimeMillis())
            .apply()
    }
}
```

#### 4. NetworkSecurityConfig Alternative

```xml
<!-- res/xml/network_security_config.xml -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Pin certificates for production API -->
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>

        <pin-set expiration="2025-12-31">
            <!-- Primary pin -->
            <pin digest="SHA-256">primary_pin_base64_here</pin>

            <!-- Backup pins -->
            <pin digest="SHA-256">backup_pin_1_base64_here</pin>
            <pin digest="SHA-256">backup_pin_2_base64_here</pin>
        </pin-set>

        <!-- Fallback to system trust for other certificates -->
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </domain-config>

    <!-- Debug configuration -->
    <debug-overrides>
        <trust-anchors>
            <!-- Trust custom CA for debugging -->
            <certificates src="@raw/debug_ca" />
            <!-- Also trust system CAs -->
            <certificates src="system" />
        </trust-anchors>
    </debug-overrides>
</network-security-config>
```

```xml
<!-- AndroidManifest.xml -->
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ...>
</application>
```

### Handling Pinning Failures

```kotlin
import okhttp3.Interceptor
import okhttp3.Response
import javax.net.ssl.SSLPeerUnverifiedException

/**
 * Interceptor to handle certificate pinning failures
 */
class CertificatePinningInterceptor(
    private val onPinningFailure: (String) -> Unit
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        return try {
            chain.proceed(chain.request())
        } catch (e: SSLPeerUnverifiedException) {
            // Certificate pinning failed
            val message = when {
                e.message?.contains("pin") == true ->
                    "Certificate pinning validation failed. This may indicate a security issue."

                else ->
                    "SSL verification failed: ${e.message}"
            }

            onPinningFailure(message)

            // Rethrow to prevent continuing with insecure connection
            throw e
        }
    }
}

// Usage
val client = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .addInterceptor(
        CertificatePinningInterceptor { errorMessage ->
            // Log to analytics
            logSecurityEvent("certificate_pinning_failure", errorMessage)

            // Show user warning
            showSecurityWarning(errorMessage)

            // Optionally disable app functionality
            disableNetworkFeatures()
        }
    )
    .build()
```

### Testing Certificate Pinning

#### 1. Unit Testing with MockWebServer

```kotlin
import okhttp3.mockwebserver.MockWebServer
import okhttp3.tls.HandshakeCertificates
import okhttp3.tls.HeldCertificate
import org.junit.After
import org.junit.Before
import org.junit.Test
import kotlin.test.assertFailsWith

class CertificatePinningTest {

    private lateinit var mockWebServer: MockWebServer
    private lateinit var serverCertificate: HeldCertificate

    @Before
    fun setup() {
        // Generate test certificate
        serverCertificate = HeldCertificate.Builder()
            .commonName("localhost")
            .addSubjectAlternativeName("localhost")
            .build()

        val serverCertificates = HandshakeCertificates.Builder()
            .heldCertificate(serverCertificate)
            .build()

        mockWebServer = MockWebServer()
        mockWebServer.useHttps(serverCertificates.sslSocketFactory(), false)
        mockWebServer.start()
    }

    @After
    fun teardown() {
        mockWebServer.shutdown()
    }

    @Test
    fun `test valid certificate pin succeeds`() {
        // Generate correct pin
        val correctPin = CertificatePinGenerator.generatePin(
            serverCertificate.certificate
        )

        // Create client with correct pin
        val certificatePinner = CertificatePinner.Builder()
            .add(mockWebServer.hostName, correctPin)
            .build()

        val clientCertificates = HandshakeCertificates.Builder()
            .addTrustedCertificate(serverCertificate.certificate)
            .build()

        val client = OkHttpClient.Builder()
            .certificatePinner(certificatePinner)
            .sslSocketFactory(
                clientCertificates.sslSocketFactory(),
                clientCertificates.trustManager
            )
            .build()

        // Should succeed
        val response = client.newCall(
            Request.Builder()
                .url(mockWebServer.url("/"))
                .build()
        ).execute()

        assert(response.isSuccessful)
    }

    @Test
    fun `test invalid certificate pin fails`() {
        // Use wrong pin
        val wrongPin = "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="

        val certificatePinner = CertificatePinner.Builder()
            .add(mockWebServer.hostName, wrongPin)
            .build()

        val clientCertificates = HandshakeCertificates.Builder()
            .addTrustedCertificate(serverCertificate.certificate)
            .build()

        val client = OkHttpClient.Builder()
            .certificatePinner(certificatePinner)
            .sslSocketFactory(
                clientCertificates.sslSocketFactory(),
                clientCertificates.trustManager
            )
            .build()

        // Should fail with SSLPeerUnverifiedException
        assertFailsWith<SSLPeerUnverifiedException> {
            client.newCall(
                Request.Builder()
                    .url(mockWebServer.url("/"))
                    .build()
            ).execute()
        }
    }
}
```

#### 2. Manual Testing with Proxy

```kotlin
/**
 * Testing certificate pinning with Charles Proxy or similar
 */
class CertificatePinningManualTest {

    /**
     * Steps to test:
     *
     * 1. Install Charles Proxy or mitmproxy
     * 2. Configure device to use proxy
     * 3. Install proxy's root CA on device
     * 4. Try to intercept HTTPS traffic
     * 5. App should fail with SSLPeerUnverifiedException
     *
     * If app continues to work, pinning is NOT working!
     */

    fun testWithProxy() {
        // Enable logging to see pinning failures
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.HEADERS
        }

        val client = OkHttpClient.Builder()
            .certificatePinner(getCertificatePinner())
            .addInterceptor(loggingInterceptor)
            .addInterceptor(CertificatePinningInterceptor { error ->
                // This should be called when proxy intercepts
                println("PINNING FAILURE DETECTED: $error")
            })
            .build()

        // Try to make request through proxy
        // Should fail with certificate pinning error
    }
}
```

### Certificate Expiration Monitoring

```kotlin
import java.security.cert.X509Certificate
import java.util.Date
import java.util.concurrent.TimeUnit

/**
 * Monitor certificate expiration dates
 */
class CertificateExpirationMonitor {

    /**
     * Check if certificate is expiring soon
     */
    fun isExpiringSoon(
        certificate: X509Certificate,
        daysThreshold: Int = 30
    ): Boolean {
        val expirationDate = certificate.notAfter
        val now = Date()
        val daysUntilExpiration = TimeUnit.MILLISECONDS.toDays(
            expirationDate.time - now.time
        )

        return daysUntilExpiration <= daysThreshold
    }

    /**
     * Get days until certificate expires
     */
    fun getDaysUntilExpiration(certificate: X509Certificate): Long {
        val expirationDate = certificate.notAfter
        val now = Date()
        return TimeUnit.MILLISECONDS.toDays(
            expirationDate.time - now.time
        )
    }

    /**
     * Monitor certificate expiration from live server
     */
    suspend fun monitorServerCertificate(hostname: String): CertificateStatus {
        return withContext(Dispatchers.IO) {
            try {
                val client = OkHttpClient.Builder().build()
                val request = Request.Builder()
                    .url("https://$hostname")
                    .build()

                val response = client.newCall(request).execute()
                val handshake = response.handshake

                handshake?.peerCertificates?.firstOrNull()?.let { cert ->
                    if (cert is X509Certificate) {
                        val daysUntilExpiration = getDaysUntilExpiration(cert)

                        CertificateStatus.Valid(
                            subject = cert.subjectDN.name,
                            issuer = cert.issuerDN.name,
                            expirationDate = cert.notAfter,
                            daysUntilExpiration = daysUntilExpiration,
                            isExpiringSoon = isExpiringSoon(cert)
                        )
                    } else {
                        CertificateStatus.Error("Not an X509 certificate")
                    }
                } ?: CertificateStatus.Error("No certificate found")
            } catch (e: Exception) {
                CertificateStatus.Error("Failed to check certificate: ${e.message}")
            }
        }
    }

    sealed class CertificateStatus {
        data class Valid(
            val subject: String,
            val issuer: String,
            val expirationDate: Date,
            val daysUntilExpiration: Long,
            val isExpiringSoon: Boolean
        ) : CertificateStatus()

        data class Error(val message: String) : CertificateStatus()
    }
}
```

### Best Practices

1. **Always Use Backup Pins**
   ```kotlin
   // GOOD: Primary + 2 backup pins
   val pinner = CertificatePinner.Builder()
       .add(host, primaryPin)
       .add(host, backupPin1)
       .add(host, backupPin2)
       .build()

   // BAD: Single pin (can lock users out)
   val pinner = CertificatePinner.Builder()
       .add(host, singlePin)
       .build()
   ```

2. **Pin Leaf and Intermediate Certificates**
   ```kotlin
   // Pin both for redundancy
   .add(host, leafCertPin)
   .add(host, intermediateCertPin)
   ```

3. **Set Expiration Dates in NetworkSecurityConfig**
   ```xml
   <pin-set expiration="2025-12-31">
       <!-- Pins automatically ignored after expiration -->
   </pin-set>
   ```

4. **Monitor Certificate Expiration**
   ```kotlin
   // Alert when certificate expires in 30 days
   if (monitor.isExpiringSoon(cert, daysThreshold = 30)) {
       alertDevelopers()
   }
   ```

5. **Test Pinning Regularly**
   ```kotlin
   // Automated tests
   @Test
   fun testCertificatePinning() { /* ... */ }

   // Manual testing with proxy
   ```

6. **Plan for Rotation**
   ```kotlin
   // Include next certificate's pin before rotation
   // Remove old pin after rotation complete
   ```

7. **Handle Failures Gracefully**
   ```kotlin
   // Don't silently fall back to insecure connection
   // Show user-friendly error
   // Log to analytics for monitoring
   ```

### Common Pitfalls

1. **Single Pin (No Backup)**
   ```kotlin
   // BAD: Certificate rotation locks out users
   .add(host, singlePin)

   // GOOD: Multiple pins for rotation
   .add(host, pin1)
   .add(host, pin2)
   ```

2. **Not Testing Pinning**
   ```kotlin
   // Always test with proxy to verify pinning works
   ```

3. **Hardcoded Pins Without Update Mechanism**
   ```kotlin
   // GOOD: Allow pin updates via secure channel
   fun updatePins(newPins: List<String>)
   ```

4. **Ignoring Pin Failures**
   ```kotlin
   // BAD: Catch and ignore
   try { request() } catch (e: SSLException) { /* ignore */ }

   // GOOD: Log and alert
   catch (e: SSLPeerUnverifiedException) { logSecurityEvent() }
   ```

5. **Pinning in Debug Builds**
   ```kotlin
   // Disable pinning for debug to allow proxying
   if (BuildConfig.DEBUG) {
       // Don't add certificate pinner
   } else {
       .certificatePinner(pinner)
   }
   ```

### Summary

Certificate pinning provides:

- **MITM Protection**: Prevents interception even with compromised CA
- **Defense in Depth**: Additional security layer beyond standard TLS
- **Trust Control**: Explicitly define which certificates to trust
- **Attack Detection**: Identify attempted man-in-the-middle attacks

**Implementation Checklist:**
-  Pin leaf and intermediate certificates
-  Include backup pins for rotation
-  Set expiration dates
-  Monitor certificate expiration
-  Test with proxy tools
-  Handle failures gracefully
-  Log pinning failures
-  Plan rotation strategy

Use certificate pinning for apps handling sensitive data: banking, healthcare, messaging, payments.

---

## Ответ (RU)
**Закрепление сертификатов (Certificate Pinning)** - это техника безопасности, которая проверяет подлинность сервера путём сравнения его SSL/TLS сертификата с известным, заранее определённым набором сертификатов или публичных ключей. Это предотвращает атаки типа man-in-the-middle даже если центр сертификации скомпрометирован.

### Понимание закрепления сертификатов

**Зачем закреплять сертификаты?**

```kotlin
// Проблема: Цепочка доверия может быть скомпрометирована
// 1. Недобросовестный CA выдаёт поддельный сертификат
// 2. Корпоративный прокси с пользовательским CA
// 3. Перехват на государственном уровне
// 4. Скомпрометированное устройство с пользовательским root CA

// Решение: Закрепить конкретные сертификаты
// Принимать только явно доверенные сертификаты
```

### Полная реализация закрепления сертификатов

#### OkHttp CertificatePinner

```kotlin
class CertificatePinningClient {

    companion object {
        private const val API_HOST = "api.example.com"

        // SHA-256 хеш публичного ключа сертификата
        private const val PRIMARY_PIN = "sha256/AAAA..."
        private const val BACKUP_PIN_1 = "sha256/BBBB..."
        private const val BACKUP_PIN_2 = "sha256/CCCC..."
    }

    fun createPinnedClient(): OkHttpClient {
        val certificatePinner = CertificatePinner.Builder()
            // Добавить основной pin
            .add(API_HOST, PRIMARY_PIN)

            // Добавить резервные pins для ротации
            .add(API_HOST, BACKUP_PIN_1)
            .add(API_HOST, BACKUP_PIN_2)

            .build()

        return OkHttpClient.Builder()
            .certificatePinner(certificatePinner)
            .build()
    }
}
```

#### Генерация pin'ов сертификатов

```kotlin
object CertificatePinGenerator {

    fun generatePin(certificate: X509Certificate): String {
        val publicKey = certificate.publicKey.encoded
        val digest = MessageDigest.getInstance("SHA-256")
        val hash = digest.digest(publicKey)
        val base64Hash = Base64.encodeToString(hash, Base64.NO_WRAP)
        return "sha256/$base64Hash"
    }

    fun extractPinsFromServer(hostname: String): List<String> {
        val client = OkHttpClient.Builder().build()
        val request = Request.Builder()
            .url("https://$hostname")
            .build()

        val pins = mutableListOf<String>()

        val response = client.newCall(request).execute()
        val handshake = response.handshake

        handshake?.peerCertificates?.forEach { certificate ->
            if (certificate is X509Certificate) {
                val pin = generatePin(certificate)
                pins.add(pin)
                println("Pin: $pin")
            }
        }

        return pins
    }
}
```

#### NetworkSecurityConfig альтернатива

```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>

        <pin-set expiration="2025-12-31">
            <pin digest="SHA-256">primary_pin_here</pin>
            <pin digest="SHA-256">backup_pin_here</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

### Обработка сбоев закрепления

```kotlin
class CertificatePinningInterceptor(
    private val onPinningFailure: (String) -> Unit
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        return try {
            chain.proceed(chain.request())
        } catch (e: SSLPeerUnverifiedException) {
            onPinningFailure("Certificate pinning failed")
            throw e
        }
    }
}
```

### Тестирование закрепления сертификатов

```kotlin
class CertificatePinningTest {

    @Test
    fun `test valid certificate pin succeeds`() {
        val correctPin = CertificatePinGenerator.generatePin(serverCertificate)

        val certificatePinner = CertificatePinner.Builder()
            .add(hostname, correctPin)
            .build()

        // Должно успешно выполниться
    }

    @Test
    fun `test invalid certificate pin fails`() {
        val wrongPin = "sha256/AAAA..."

        val certificatePinner = CertificatePinner.Builder()
            .add(hostname, wrongPin)
            .build()

        // Должно провалиться с SSLPeerUnverifiedException
        assertFailsWith<SSLPeerUnverifiedException> {
            // Выполнить запрос
        }
    }
}
```

### Best Practices

1. **Всегда используйте резервные pin'ы**
   ```kotlin
   .add(host, primaryPin)
   .add(host, backupPin1)
   .add(host, backupPin2)
   ```

2. **Закрепляйте leaf и intermediate сертификаты**

3. **Устанавливайте даты истечения**
   ```xml
   <pin-set expiration="2025-12-31">
   ```

4. **Мониторьте истечение сертификатов**

5. **Регулярно тестируйте закрепление**

6. **Планируйте ротацию**

7. **Gracefully обрабатывайте сбои**

### Распространённые ошибки

1. **Единственный pin (без резервного)**
2. **Не тестирование закрепления**
3. **Жёстко заданные pins без механизма обновления**
4. **Игнорирование сбоев pin'ов**
5. **Закрепление в debug сборках**

### Резюме

Закрепление сертификатов обеспечивает:

- **Защита от MITM**: Предотвращает перехват даже при скомпрометированном CA
- **Эшелонированная защита**: Дополнительный уровень безопасности
- **Контроль доверия**: Явное определение доверенных сертификатов
- **Обнаружение атак**: Идентификация попыток man-in-the-middle

**Контрольный список:**
-  Закрепить leaf и intermediate сертификаты
-  Включить резервные pins
-  Установить даты истечения
-  Мониторить истечение сертификатов
-  Тестировать с прокси
-  Gracefully обрабатывать сбои
-  Логировать сбои закрепления

Используйте закрепление сертификатов для приложений с чувствительными данными: банкинг, здравоохранение, мессенджеры, платежи.

---

## Related Questions

### Related (Medium)
- [[q-android-security-practices-checklist--android--medium]] - Security
- [[q-encrypted-file-storage--security--medium]] - Security
- [[q-database-encryption-android--android--medium]] - Security
- [[q-app-security-best-practices--security--medium]] - Security
- [[q-data-encryption-at-rest--security--medium]] - Security
