---
id: sec-003
title: SSL Certificate Pinning / Pinning SSL-sertifikatov
aliases:
- Certificate Pinning
- SSL Pinning
- OkHttp CertificatePinner
topic: android
subtopics:
- security
- networking
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
created: 2026-01-23
updated: 2026-01-23
tags:
- android/security
- android/networking
- difficulty/hard
related:
- q-network-security-config--security--medium
- q-android-keystore--security--hard
sources:
- https://developer.android.com/privacy-and-security/security-config
- https://square.github.io/okhttp/features/https/
---
# Vopros (RU)
> Chto takoe certificate pinning i kak ego realizovat' v Android s OkHttp?

# Question (EN)
> What is certificate pinning and how do you implement it in Android with OkHttp?

---

## Otvet (RU)

**Teoriya:**
**Certificate Pinning** - eto tekhnika zashchity ot MITM-atak (Man-in-the-Middle), pri kotoroj prilozhenie prinimaet tol'ko zaranee izvestnye sertifikaty servera, ignorируя doverie k sistemnym CA (Certificate Authorities).

### Zachem nuzhen pinning?
- **Zashchita ot MITM**: zlonamerennye proksi ne smogut perekhvatit' trafik
- **Zashchita ot skompromentirovannogo CA**: dazhe esli CA vydam poddel'nyj sertifikat
- **Compliance**: trebuetsya dlya finansovyh i medicinskih prilozenij

### Vidy pinninga
| Vid | Opisanie | Gibkost' |
|-----|----------|----------|
| Certificate Pin | Pin vsego sertifikata | Nizkaya (nuzhno obnovlyat' pri rotacii) |
| Public Key Pin | Pin tol'ko publichnogo klyucha | Srednyaya |
| SPKI Pin | Pin Subject Public Key Info hash | Vysokaya (rekomenduetsya) |

### Realizaciya s OkHttp
```kotlin
import okhttp3.CertificatePinner
import okhttp3.OkHttpClient

class SecureApiClient {

    // Poluchenie SHA-256 pin iz sertifikata:
    // openssl s_client -connect api.example.com:443 | openssl x509 -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | openssl enc -base64

    private val certificatePinner = CertificatePinner.Builder()
        // Osnovnoj pin (tekushchij sertifikat)
        .add(
            "api.example.com",
            "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
        )
        // Backup pin (sleduyushchij sertifikat ili promezhutochnyj CA)
        .add(
            "api.example.com",
            "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB="
        )
        // Poddomeny
        .add(
            "*.example.com",
            "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
        )
        .build()

    val client = OkHttpClient.Builder()
        .certificatePinner(certificatePinner)
        .build()
}
```

### Poluchenie pin iz sertifikata programmno
```kotlin
// Dlya testirovaniya: poluchit' pin pri pervom podklyuchenii
fun getPinsFromServer(hostname: String): List<String> {
    val client = OkHttpClient.Builder()
        .certificatePinner(
            CertificatePinner.Builder()
                .add(hostname, "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
                .build()
        )
        .build()

    return try {
        client.newCall(Request.Builder().url("https://$hostname").build()).execute()
        emptyList()
    } catch (e: SSLPeerUnverifiedException) {
        // Izvlekam real'nye piny iz soobsheniya ob oshibke
        val regex = "sha256/[A-Za-z0-9+/=]+".toRegex()
        regex.findAll(e.message ?: "").map { it.value }.toList()
    }
}
```

### Pinning cherez Network Security Config (XML)
```xml
<!-- res/xml/network_security_config.xml -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config>
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set expiration="2026-12-31">
            <!-- Osnovnoj pin -->
            <pin digest="SHA-256">AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</pin>
            <!-- Backup pin -->
            <pin digest="SHA-256">BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

```xml
<!-- AndroidManifest.xml -->
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ...>
```

### Obrabotka oshibok pinninga
```kotlin
class PinningInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        return try {
            chain.proceed(chain.request())
        } catch (e: SSLPeerUnverifiedException) {
            // Log dlya monitoringa
            Log.e("Security", "Certificate pinning failed: ${e.message}")
            Analytics.logSecurityEvent("PIN_FAILURE", mapOf(
                "host" to chain.request().url.host,
                "error" to e.message
            ))
            throw SecurityException("Network security violation", e)
        }
    }
}
```

### Strategiya rotacii sertifikatov
```kotlin
class CertificatePinManager(private val context: Context) {

    // Dinamicheskoe obnovlenie pinov (cherez Remote Config)
    suspend fun getUpdatedPins(): CertificatePinner {
        val pins = try {
            // Poluchayem piny s servera (cherez otdel'nyj bezopasnyj kanal)
            fetchRemotePins()
        } catch (e: Exception) {
            // Fallback na lokalno sohranennye
            getLocalPins()
        }

        return CertificatePinner.Builder().apply {
            pins.forEach { (host, pinList) ->
                pinList.forEach { pin ->
                    add(host, pin)
                }
            }
        }.build()
    }

    private fun getLocalPins(): Map<String, List<String>> {
        // Minimal'nyj nabor pinov vshityh v prilozhenie
        return mapOf(
            "api.example.com" to listOf(
                "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
                "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB="
            )
        )
    }
}
```

### Debug-rezhim (otklyuchenie pinninga)
```kotlin
fun createOkHttpClient(isDebug: Boolean): OkHttpClient {
    return OkHttpClient.Builder().apply {
        if (!isDebug) {
            certificatePinner(productionPinner)
        }
        // V debug mozhno prosmatrivat' trafik cherez Charles/Proxyman
    }.build()
}
```

### Luchshie praktiki
| Praktika | Opisanie |
|----------|----------|
| Minimum 2 pina | Osnovnoj + backup (dlya rotacii) |
| Pin promezhutochnyj CA | Bol'she gibkosti pri rotacii leaf-sertifikata |
| Expiration date | Ustanavlivat' srok dejstviya v Network Security Config |
| Monitoring | Logirovanie oshibok pinninga dlya vyyavleniya atak |
| Graceful degradation | Plan na sluchaj neudachnogo pinninga |

---

## Answer (EN)

**Theory:**
**Certificate Pinning** is a technique to protect against MITM (Man-in-the-Middle) attacks where the application only accepts pre-known server certificates, ignoring trust in system CAs (Certificate Authorities).

### Why pinning?
- **MITM protection**: malicious proxies cannot intercept traffic
- **Compromised CA protection**: even if a CA issues a fake certificate
- **Compliance**: required for financial and medical applications

### Types of pinning
| Type | Description | Flexibility |
|------|-------------|-------------|
| Certificate Pin | Pin entire certificate | Low (need update on rotation) |
| Public Key Pin | Pin only public key | Medium |
| SPKI Pin | Pin Subject Public Key Info hash | High (recommended) |

### Implementation with OkHttp
```kotlin
import okhttp3.CertificatePinner
import okhttp3.OkHttpClient

class SecureApiClient {

    // Get SHA-256 pin from certificate:
    // openssl s_client -connect api.example.com:443 | openssl x509 -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | openssl enc -base64

    private val certificatePinner = CertificatePinner.Builder()
        // Primary pin (current certificate)
        .add(
            "api.example.com",
            "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
        )
        // Backup pin (next certificate or intermediate CA)
        .add(
            "api.example.com",
            "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB="
        )
        // Subdomains
        .add(
            "*.example.com",
            "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
        )
        .build()

    val client = OkHttpClient.Builder()
        .certificatePinner(certificatePinner)
        .build()
}
```

### Get pins from certificate programmatically
```kotlin
// For testing: get pins on first connection
fun getPinsFromServer(hostname: String): List<String> {
    val client = OkHttpClient.Builder()
        .certificatePinner(
            CertificatePinner.Builder()
                .add(hostname, "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
                .build()
        )
        .build()

    return try {
        client.newCall(Request.Builder().url("https://$hostname").build()).execute()
        emptyList()
    } catch (e: SSLPeerUnverifiedException) {
        // Extract real pins from error message
        val regex = "sha256/[A-Za-z0-9+/=]+".toRegex()
        regex.findAll(e.message ?: "").map { it.value }.toList()
    }
}
```

### Pinning via Network Security Config (XML)
```xml
<!-- res/xml/network_security_config.xml -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config>
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set expiration="2026-12-31">
            <!-- Primary pin -->
            <pin digest="SHA-256">AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</pin>
            <!-- Backup pin -->
            <pin digest="SHA-256">BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

```xml
<!-- AndroidManifest.xml -->
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ...>
```

### Pin failure handling
```kotlin
class PinningInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        return try {
            chain.proceed(chain.request())
        } catch (e: SSLPeerUnverifiedException) {
            // Log for monitoring
            Log.e("Security", "Certificate pinning failed: ${e.message}")
            Analytics.logSecurityEvent("PIN_FAILURE", mapOf(
                "host" to chain.request().url.host,
                "error" to e.message
            ))
            throw SecurityException("Network security violation", e)
        }
    }
}
```

### Certificate rotation strategy
```kotlin
class CertificatePinManager(private val context: Context) {

    // Dynamic pin updates (via Remote Config)
    suspend fun getUpdatedPins(): CertificatePinner {
        val pins = try {
            // Fetch pins from server (via separate secure channel)
            fetchRemotePins()
        } catch (e: Exception) {
            // Fallback to locally stored
            getLocalPins()
        }

        return CertificatePinner.Builder().apply {
            pins.forEach { (host, pinList) ->
                pinList.forEach { pin ->
                    add(host, pin)
                }
            }
        }.build()
    }

    private fun getLocalPins(): Map<String, List<String>> {
        // Minimal set of pins baked into the app
        return mapOf(
            "api.example.com" to listOf(
                "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
                "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB="
            )
        )
    }
}
```

### Debug mode (disable pinning)
```kotlin
fun createOkHttpClient(isDebug: Boolean): OkHttpClient {
    return OkHttpClient.Builder().apply {
        if (!isDebug) {
            certificatePinner(productionPinner)
        }
        // In debug can inspect traffic via Charles/Proxyman
    }.build()
}
```

### Best practices
| Practice | Description |
|----------|-------------|
| Minimum 2 pins | Primary + backup (for rotation) |
| Pin intermediate CA | More flexibility when rotating leaf certificate |
| Expiration date | Set expiration in Network Security Config |
| Monitoring | Log pinning failures to detect attacks |
| Graceful degradation | Plan for pinning failure scenarios |

---

## Follow-ups

- How do you handle certificate rotation without app update?
- What are the risks of certificate pinning?
- How do you test certificate pinning?
- What is the difference between pinning leaf certificate vs intermediate CA?

## References

- https://developer.android.com/privacy-and-security/security-config
- https://square.github.io/okhttp/features/https/
- https://owasp.org/www-community/controls/Certificate_and_Public_Key_Pinning

## Related Questions

### Prerequisites (Easier)
- [[q-network-security-config--security--medium]] - Network Security Config basics

### Related (Same Level)
- [[q-android-keystore--security--hard]] - Android Keystore
- [[q-play-integrity-api--security--hard]] - Play Integrity API
