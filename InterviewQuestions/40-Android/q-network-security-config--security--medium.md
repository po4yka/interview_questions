---
id: sec-009
title: Network Security Config / Konfiguracija setevoj bezopasnosti
aliases:
- Network Security Config
- network_security_config.xml
- Cleartext Traffic
topic: android
subtopics:
- security
- networking
question_kind: theory
difficulty: medium
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
- difficulty/medium
related:
- q-ssl-certificate-pinning--security--hard
sources:
- https://developer.android.com/privacy-and-security/security-config
---
# Vopros (RU)
> Kak nastroit' network_security_config.xml dlya upravleniya setevoj bezopasnost'yu?

# Question (EN)
> How do you configure network_security_config.xml for network security management?

---

## Otvet (RU)

**Teoriya:**
**Network Security Configuration** - eto deklarativniy sposob nastrojki setevoj bezopasnosti prilozheniya cherez XML fajl. Vveden v Android 7.0 (API 24) i pozvolyaet:
- Upravlyat' doveryaem k CA sertifikatam
- Nastrajivat' certificate pinning
- Blokirovat'/razreshat' cleartext (HTTP) trafik
- Nastrajivat' debug overrides

### Bazovaya struktura
```xml
<!-- res/xml/network_security_config.xml -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Nastrojki po umolchaniyu dlya vsego prilozheniya -->
    <base-config>
        ...
    </base-config>

    <!-- Nastrojki dlya konkretnyh domenov -->
    <domain-config>
        ...
    </domain-config>

    <!-- Nastrojki tol'ko dlya debug sborok -->
    <debug-overrides>
        ...
    </debug-overrides>
</network-security-config>
```

### Podklyuchenie v AndroidManifest.xml
```xml
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ...>
```

### Zapret cleartext (HTTP) trafika
```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Zapret HTTP dlya vsego prilozheniya -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>

    <!-- Isklyuchenie dlya lokalnoy razrabotki -->
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">10.0.2.2</domain>
        <domain includeSubdomains="true">localhost</domain>
    </domain-config>
</network-security-config>
```

### Certificate Pinning cherez XML
```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config>
        <domain includeSubdomains="true">api.example.com</domain>

        <!-- Certificate pinning -->
        <pin-set expiration="2026-12-31">
            <!-- SHA-256 hash publichnogo klyucha -->
            <pin digest="SHA-256">AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</pin>
            <!-- Backup pin -->
            <pin digest="SHA-256">BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=</pin>
        </pin-set>

        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </domain-config>
</network-security-config>
```

### Doveriye k pol'zovatel'skim CA (opasno!)
```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Tol'ko dlya debug! -->
    <debug-overrides>
        <trust-anchors>
            <!-- Razreshaem pol'zovatel'skie CA dlya Charles/Proxyman -->
            <certificates src="user" />
            <certificates src="system" />
        </trust-anchors>
    </debug-overrides>

    <!-- Production: tol'ko sistemnyye CA -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
</network-security-config>
```

### Sobstvennye CA sertifikaty
```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config>
        <domain includeSubdomains="true">internal.company.com</domain>
        <trust-anchors>
            <!-- Sobstvennyj CA sertifikat v res/raw/ -->
            <certificates src="@raw/company_ca" />
        </trust-anchors>
    </domain-config>

    <base-config>
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
</network-security-config>
```

### Polnyy primer dlya production
```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Bazovye nastrojki: HTTPS only -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>

    <!-- Glavnyj API s pinning -->
    <domain-config>
        <domain includeSubdomains="true">api.myapp.com</domain>
        <pin-set expiration="2027-01-01">
            <pin digest="SHA-256">base64-encoded-sha256-hash-1=</pin>
            <pin digest="SHA-256">base64-encoded-sha256-hash-2=</pin>
        </pin-set>
    </domain-config>

    <!-- CDN bez pinninga (sertifikaty chasto menyayutsya) -->
    <domain-config>
        <domain includeSubdomains="true">cdn.myapp.com</domain>
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </domain-config>

    <!-- Vnutrenniy servis s sobstvennym CA -->
    <domain-config>
        <domain includeSubdomains="true">internal.myapp.com</domain>
        <trust-anchors>
            <certificates src="@raw/internal_ca" />
        </trust-anchors>
    </domain-config>

    <!-- Debug: razreshaem proksi -->
    <debug-overrides>
        <trust-anchors>
            <certificates src="user" />
            <certificates src="system" />
        </trust-anchors>
    </debug-overrides>
</network-security-config>
```

### Poluchenie SHA-256 dlya pinninga
```bash
# Iz URL
openssl s_client -connect api.example.com:443 -servername api.example.com \
    < /dev/null 2>/dev/null \
    | openssl x509 -pubkey -noout \
    | openssl pkey -pubin -outform der \
    | openssl dgst -sha256 -binary \
    | openssl enc -base64

# Iz fayla sertifikata
openssl x509 -in certificate.crt -pubkey -noout \
    | openssl pkey -pubin -outform der \
    | openssl dgst -sha256 -binary \
    | openssl enc -base64
```

### Proverka konfiguracii v kode
```kotlin
// Proverka, razreshen li cleartext dlya domena
fun isCleartextPermitted(host: String): Boolean {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
        NetworkSecurityPolicy.getInstance().isCleartextTrafficPermitted(host)
    } else {
        true  // Do Android M cleartext razreshen po umolchaniyu
    }
}

// Proverka v OkHttp interceptore
class SecurityInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        val host = request.url.host

        if (request.url.scheme == "http" && !isCleartextPermitted(host)) {
            throw SecurityException("Cleartext HTTP not permitted for $host")
        }

        return chain.proceed(request)
    }
}
```

### Vazhno
| Aspekt | Opisanie |
|--------|----------|
| API Level | Rabotaet s API 24+, na bolee staryh ignoriruyetsya |
| Debug overrides | Primenyayutsya tol'ko esli `debuggable="true"` |
| Pin expiration | Esli istok - pinning otklyuchaetsya, prilozhenie prodolzhaet rabotat' |
| Cleartext default | S Android 9 (API 28) cleartext zapreshchen po umolchaniyu |

---

## Answer (EN)

**Theory:**
**Network Security Configuration** is a declarative way to configure app network security through an XML file. Introduced in Android 7.0 (API 24), it allows:
- Managing trust in CA certificates
- Configuring certificate pinning
- Blocking/allowing cleartext (HTTP) traffic
- Configuring debug overrides

### Basic structure
```xml
<!-- res/xml/network_security_config.xml -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Default settings for entire app -->
    <base-config>
        ...
    </base-config>

    <!-- Settings for specific domains -->
    <domain-config>
        ...
    </domain-config>

    <!-- Settings only for debug builds -->
    <debug-overrides>
        ...
    </debug-overrides>
</network-security-config>
```

### Connecting in AndroidManifest.xml
```xml
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ...>
```

### Blocking cleartext (HTTP) traffic
```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Block HTTP for entire app -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>

    <!-- Exception for local development -->
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">10.0.2.2</domain>
        <domain includeSubdomains="true">localhost</domain>
    </domain-config>
</network-security-config>
```

### Certificate Pinning via XML
```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config>
        <domain includeSubdomains="true">api.example.com</domain>

        <!-- Certificate pinning -->
        <pin-set expiration="2026-12-31">
            <!-- SHA-256 hash of public key -->
            <pin digest="SHA-256">AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</pin>
            <!-- Backup pin -->
            <pin digest="SHA-256">BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=</pin>
        </pin-set>

        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </domain-config>
</network-security-config>
```

### Trust user-installed CAs (dangerous!)
```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Debug only! -->
    <debug-overrides>
        <trust-anchors>
            <!-- Allow user CAs for Charles/Proxyman -->
            <certificates src="user" />
            <certificates src="system" />
        </trust-anchors>
    </debug-overrides>

    <!-- Production: system CAs only -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
</network-security-config>
```

### Custom CA certificates
```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config>
        <domain includeSubdomains="true">internal.company.com</domain>
        <trust-anchors>
            <!-- Custom CA certificate in res/raw/ -->
            <certificates src="@raw/company_ca" />
        </trust-anchors>
    </domain-config>

    <base-config>
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
</network-security-config>
```

### Full production example
```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Base settings: HTTPS only -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>

    <!-- Main API with pinning -->
    <domain-config>
        <domain includeSubdomains="true">api.myapp.com</domain>
        <pin-set expiration="2027-01-01">
            <pin digest="SHA-256">base64-encoded-sha256-hash-1=</pin>
            <pin digest="SHA-256">base64-encoded-sha256-hash-2=</pin>
        </pin-set>
    </domain-config>

    <!-- CDN without pinning (certificates change often) -->
    <domain-config>
        <domain includeSubdomains="true">cdn.myapp.com</domain>
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </domain-config>

    <!-- Internal service with custom CA -->
    <domain-config>
        <domain includeSubdomains="true">internal.myapp.com</domain>
        <trust-anchors>
            <certificates src="@raw/internal_ca" />
        </trust-anchors>
    </domain-config>

    <!-- Debug: allow proxy -->
    <debug-overrides>
        <trust-anchors>
            <certificates src="user" />
            <certificates src="system" />
        </trust-anchors>
    </debug-overrides>
</network-security-config>
```

### Getting SHA-256 for pinning
```bash
# From URL
openssl s_client -connect api.example.com:443 -servername api.example.com \
    < /dev/null 2>/dev/null \
    | openssl x509 -pubkey -noout \
    | openssl pkey -pubin -outform der \
    | openssl dgst -sha256 -binary \
    | openssl enc -base64

# From certificate file
openssl x509 -in certificate.crt -pubkey -noout \
    | openssl pkey -pubin -outform der \
    | openssl dgst -sha256 -binary \
    | openssl enc -base64
```

### Checking configuration in code
```kotlin
// Check if cleartext permitted for domain
fun isCleartextPermitted(host: String): Boolean {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
        NetworkSecurityPolicy.getInstance().isCleartextTrafficPermitted(host)
    } else {
        true  // Before Android M cleartext permitted by default
    }
}

// Check in OkHttp interceptor
class SecurityInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        val host = request.url.host

        if (request.url.scheme == "http" && !isCleartextPermitted(host)) {
            throw SecurityException("Cleartext HTTP not permitted for $host")
        }

        return chain.proceed(request)
    }
}
```

### Important notes
| Aspect | Description |
|--------|-------------|
| API Level | Works on API 24+, ignored on older versions |
| Debug overrides | Applied only if `debuggable="true"` |
| Pin expiration | If expired - pinning disabled, app continues working |
| Cleartext default | From Android 9 (API 28) cleartext blocked by default |

---

## Follow-ups

- How do you debug network issues when cleartext is blocked?
- What happens when pin expiration date passes?
- How do you handle different configurations for different build types?
- What is the priority order when multiple domain-config blocks match?

## References

- https://developer.android.com/privacy-and-security/security-config
- https://developer.android.com/privacy-and-security/security-config#CertificatePinning

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - Android basics

### Related (Same Level)
- [[q-ssl-certificate-pinning--security--hard]] - OkHttp certificate pinning
