---
id: sec-004
title: Play Integrity API / Play Integrity API
aliases:
- Play Integrity API
- SafetyNet Replacement
- Device Attestation
topic: android
subtopics:
- security
- attestation
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
- difficulty/hard
related:
- q-root-detection--security--medium
- q-android-keystore--security--hard
sources:
- https://developer.android.com/google/play/integrity
- https://developer.android.com/google/play/integrity/verdicts
anki_cards:
- slug: sec-004-0-en
  language: en
- slug: sec-004-0-ru
  language: ru
---
# Vopros (RU)
> Chto takoe Play Integrity API i kak ego ispol'zovat' dlya proverki podlinnosti ustroystva i prilozheniya?

# Question (EN)
> What is Play Integrity API and how do you use it for device and app attestation?

---

## Otvet (RU)

**Teoriya:**
**Play Integrity API** (zamenil SafetyNet Attestation v 2024) - eto servis Google dlya proverki:
- **Podlinnosti prilozheniya**: APK ne modificirovan
- **Licenzirovaniya**: prilozhenie ustanovleno iz Google Play
- **Celostnosti ustroystva**: ustrojstvo ne rootirovano i ne modificirovano
- **Uchetnoj zapisi**: pol'zovatel' imeet licenziyu Google Play

### Komponenty otveta (Verdict)
```kotlin
// Primer rasshifrovannogo tokena
{
    "requestDetails": {
        "requestPackageName": "com.example.app",
        "timestampMillis": "1234567890123",
        "nonce": "aGVsbG8gd29ybGQ="
    },
    "appIntegrity": {
        "appRecognitionVerdict": "PLAY_RECOGNIZED",
        "packageName": "com.example.app",
        "certificateSha256Digest": ["..."],
        "versionCode": "42"
    },
    "deviceIntegrity": {
        "deviceRecognitionVerdict": ["MEETS_DEVICE_INTEGRITY", "MEETS_BASIC_INTEGRITY"]
    },
    "accountDetails": {
        "appLicensingVerdict": "LICENSED"
    }
}
```

### Nastrojka
```kotlin
// build.gradle.kts
dependencies {
    implementation("com.google.android.play:integrity:1.4.0")
}
```

### Bazovaya realizaciya
```kotlin
import com.google.android.play.core.integrity.IntegrityManagerFactory
import com.google.android.play.core.integrity.StandardIntegrityManager

class PlayIntegrityChecker(private val context: Context) {

    private val integrityManager = IntegrityManagerFactory.create(context)

    // Podgotovka providera (vyzyvat' zaranee dlya optimizacii)
    private var standardIntegrityTokenProvider: StandardIntegrityManager.StandardIntegrityTokenProvider? = null

    suspend fun prepareIntegrityToken() {
        val integrityManager = IntegrityManagerFactory.createStandard(context)

        val request = StandardIntegrityManager.PrepareIntegrityTokenRequest.builder()
            .setCloudProjectNumber(CLOUD_PROJECT_NUMBER) // Iz Google Cloud Console
            .build()

        integrityManager.prepareIntegrityToken(request)
            .addOnSuccessListener { provider ->
                standardIntegrityTokenProvider = provider
            }
            .addOnFailureListener { e ->
                Log.e("Integrity", "Failed to prepare: ${e.message}")
            }
    }

    // Zapros tokena dlya proverki
    suspend fun requestIntegrityToken(
        requestHash: String // Hash dannyh zaprosa
    ): String? = suspendCancellableCoroutine { cont ->

        val provider = standardIntegrityTokenProvider
        if (provider == null) {
            cont.resume(null) { }
            return@suspendCancellableCoroutine
        }

        val request = StandardIntegrityManager.StandardIntegrityTokenRequest.builder()
            .setRequestHash(requestHash)
            .build()

        provider.request(request)
            .addOnSuccessListener { response ->
                cont.resume(response.token()) { }
            }
            .addOnFailureListener { e ->
                Log.e("Integrity", "Token request failed: ${e.message}")
                cont.resume(null) { }
            }
    }

    companion object {
        private const val CLOUD_PROJECT_NUMBER = 123456789L // Vash nomer proekta
    }
}
```

### Proverka na servere (OBYAZATEL'NO!)
```kotlin
// Server-side (Kotlin/Ktor primer)
import com.google.api.services.playintegrity.v1.PlayIntegrity
import com.google.api.services.playintegrity.v1.model.DecodeIntegrityTokenRequest

class IntegrityVerifier(private val playIntegrity: PlayIntegrity) {

    fun verifyToken(integrityToken: String, expectedPackageName: String): VerificationResult {
        val request = DecodeIntegrityTokenRequest().apply {
            this.integrityToken = integrityToken
        }

        val response = playIntegrity.v1()
            .decodeIntegrityToken("com.example.app", request)
            .execute()

        val payload = response.tokenPayloadExternal

        // Proverka podlinnosti prilozheniya
        val appIntegrity = payload.appIntegrity
        if (appIntegrity.appRecognitionVerdict != "PLAY_RECOGNIZED") {
            return VerificationResult.AppModified
        }
        if (appIntegrity.packageName != expectedPackageName) {
            return VerificationResult.WrongPackage
        }

        // Proverka celostnosti ustroystva
        val deviceVerdicts = payload.deviceIntegrity.deviceRecognitionVerdict
        if ("MEETS_DEVICE_INTEGRITY" !in deviceVerdicts) {
            return VerificationResult.DeviceCompromised
        }

        // Proverka licenzii
        if (payload.accountDetails.appLicensingVerdict != "LICENSED") {
            return VerificationResult.Unlicensed
        }

        return VerificationResult.Valid
    }
}

sealed class VerificationResult {
    object Valid : VerificationResult()
    object AppModified : VerificationResult()
    object WrongPackage : VerificationResult()
    object DeviceCompromised : VerificationResult()
    object Unlicensed : VerificationResult()
}
```

### Integraciya s API-zaprosami
```kotlin
class SecureApiClient(
    private val integrityChecker: PlayIntegrityChecker,
    private val api: ApiService
) {
    suspend fun performSecureOperation(data: OperationData): Result<Response> {
        // Sozdayom hash dannyh zaprosa
        val requestHash = data.toJson().sha256()

        // Poluchayom integrity token
        val integrityToken = integrityChecker.requestIntegrityToken(requestHash)
            ?: return Result.failure(SecurityException("Integrity check unavailable"))

        // Otpravlyayom zapros s tokenom
        return try {
            val response = api.secureOperation(
                data = data,
                integrityToken = integrityToken
            )
            Result.success(response)
        } catch (e: HttpException) {
            if (e.code() == 403) {
                // Server otklil iz-za proverki celostnosti
                Result.failure(SecurityException("Integrity verification failed"))
            } else {
                Result.failure(e)
            }
        }
    }
}
```

### Urovni celostnosti ustroystva
| Verdict | Opisanie | Uroven' doveriya |
|---------|----------|-----------------|
| `MEETS_STRONG_INTEGRITY` | Podlinnoe ustrojstvo, zagruzchik zablokirovan | Vysshij |
| `MEETS_DEVICE_INTEGRITY` | Podlinnoe ustrojstvo s Google Play | Vysokij |
| `MEETS_BASIC_INTEGRITY` | Ustrojstvo proshlo bazovye proverki | Srednij |
| `MEETS_VIRTUAL_INTEGRITY` | Emulyator s Google Play | Nizky |
| (pusto) | Ustrojstvo ne proshlo proverki | Net doveriya |

### Luchshie praktiki
```kotlin
// 1. Vsegda proveryat' na servere (ne v kliente!)

// 2. Ispol'zovat' request hash dlya svyazyvaniya s dannymy
val requestHash = sensitiveData.hashCode().toString()

// 3. Predvaritel'no podgotovit' provider
// (vyzyvat' prepareIntegrityToken() pri zapuske prilozheniya)

// 4. Keshirovat' rezul'taty (no ne token!)
// Token deystvitelen tol'ko dlya odnogo zaprosa

// 5. Graceful degradation dlya ustroystv bez Google Play
if (!isGooglePlayServicesAvailable()) {
    // Al'ternativnaya logika (s ogranichennoy funkcional'nost'yu)
}
```

### Ogranichepniya
| Aspekt | Opisanie |
|--------|----------|
| Kvota | 10,000 zaprosov/den' besplatno |
| Latency | ~200-500ms na zapros |
| Dostupnost' | Tol'ko ustrojstva s Google Play |
| Obkhod | Opytnyj zlonamerenik mozhet obojti (defence in depth) |

---

## Answer (EN)

**Theory:**
**Play Integrity API** (replaced SafetyNet Attestation in 2024) is a Google service for verifying:
- **App authenticity**: APK not modified
- **Licensing**: app installed from Google Play
- **Device integrity**: device not rooted or modified
- **Account**: user has Google Play license

### Response components (Verdict)
```kotlin
// Example decoded token
{
    "requestDetails": {
        "requestPackageName": "com.example.app",
        "timestampMillis": "1234567890123",
        "nonce": "aGVsbG8gd29ybGQ="
    },
    "appIntegrity": {
        "appRecognitionVerdict": "PLAY_RECOGNIZED",
        "packageName": "com.example.app",
        "certificateSha256Digest": ["..."],
        "versionCode": "42"
    },
    "deviceIntegrity": {
        "deviceRecognitionVerdict": ["MEETS_DEVICE_INTEGRITY", "MEETS_BASIC_INTEGRITY"]
    },
    "accountDetails": {
        "appLicensingVerdict": "LICENSED"
    }
}
```

### Setup
```kotlin
// build.gradle.kts
dependencies {
    implementation("com.google.android.play:integrity:1.4.0")
}
```

### Basic implementation
```kotlin
import com.google.android.play.core.integrity.IntegrityManagerFactory
import com.google.android.play.core.integrity.StandardIntegrityManager

class PlayIntegrityChecker(private val context: Context) {

    private val integrityManager = IntegrityManagerFactory.create(context)

    // Prepare provider (call ahead for optimization)
    private var standardIntegrityTokenProvider: StandardIntegrityManager.StandardIntegrityTokenProvider? = null

    suspend fun prepareIntegrityToken() {
        val integrityManager = IntegrityManagerFactory.createStandard(context)

        val request = StandardIntegrityManager.PrepareIntegrityTokenRequest.builder()
            .setCloudProjectNumber(CLOUD_PROJECT_NUMBER) // From Google Cloud Console
            .build()

        integrityManager.prepareIntegrityToken(request)
            .addOnSuccessListener { provider ->
                standardIntegrityTokenProvider = provider
            }
            .addOnFailureListener { e ->
                Log.e("Integrity", "Failed to prepare: ${e.message}")
            }
    }

    // Request token for verification
    suspend fun requestIntegrityToken(
        requestHash: String // Hash of request data
    ): String? = suspendCancellableCoroutine { cont ->

        val provider = standardIntegrityTokenProvider
        if (provider == null) {
            cont.resume(null) { }
            return@suspendCancellableCoroutine
        }

        val request = StandardIntegrityManager.StandardIntegrityTokenRequest.builder()
            .setRequestHash(requestHash)
            .build()

        provider.request(request)
            .addOnSuccessListener { response ->
                cont.resume(response.token()) { }
            }
            .addOnFailureListener { e ->
                Log.e("Integrity", "Token request failed: ${e.message}")
                cont.resume(null) { }
            }
    }

    companion object {
        private const val CLOUD_PROJECT_NUMBER = 123456789L // Your project number
    }
}
```

### Server-side verification (MANDATORY!)
```kotlin
// Server-side (Kotlin/Ktor example)
import com.google.api.services.playintegrity.v1.PlayIntegrity
import com.google.api.services.playintegrity.v1.model.DecodeIntegrityTokenRequest

class IntegrityVerifier(private val playIntegrity: PlayIntegrity) {

    fun verifyToken(integrityToken: String, expectedPackageName: String): VerificationResult {
        val request = DecodeIntegrityTokenRequest().apply {
            this.integrityToken = integrityToken
        }

        val response = playIntegrity.v1()
            .decodeIntegrityToken("com.example.app", request)
            .execute()

        val payload = response.tokenPayloadExternal

        // Verify app authenticity
        val appIntegrity = payload.appIntegrity
        if (appIntegrity.appRecognitionVerdict != "PLAY_RECOGNIZED") {
            return VerificationResult.AppModified
        }
        if (appIntegrity.packageName != expectedPackageName) {
            return VerificationResult.WrongPackage
        }

        // Verify device integrity
        val deviceVerdicts = payload.deviceIntegrity.deviceRecognitionVerdict
        if ("MEETS_DEVICE_INTEGRITY" !in deviceVerdicts) {
            return VerificationResult.DeviceCompromised
        }

        // Verify license
        if (payload.accountDetails.appLicensingVerdict != "LICENSED") {
            return VerificationResult.Unlicensed
        }

        return VerificationResult.Valid
    }
}

sealed class VerificationResult {
    object Valid : VerificationResult()
    object AppModified : VerificationResult()
    object WrongPackage : VerificationResult()
    object DeviceCompromised : VerificationResult()
    object Unlicensed : VerificationResult()
}
```

### API integration
```kotlin
class SecureApiClient(
    private val integrityChecker: PlayIntegrityChecker,
    private val api: ApiService
) {
    suspend fun performSecureOperation(data: OperationData): Result<Response> {
        // Create hash of request data
        val requestHash = data.toJson().sha256()

        // Get integrity token
        val integrityToken = integrityChecker.requestIntegrityToken(requestHash)
            ?: return Result.failure(SecurityException("Integrity check unavailable"))

        // Send request with token
        return try {
            val response = api.secureOperation(
                data = data,
                integrityToken = integrityToken
            )
            Result.success(response)
        } catch (e: HttpException) {
            if (e.code() == 403) {
                // Server rejected due to integrity check
                Result.failure(SecurityException("Integrity verification failed"))
            } else {
                Result.failure(e)
            }
        }
    }
}
```

### Device integrity levels
| Verdict | Description | Trust Level |
|---------|-------------|-------------|
| `MEETS_STRONG_INTEGRITY` | Genuine device, bootloader locked | Highest |
| `MEETS_DEVICE_INTEGRITY` | Genuine device with Google Play | High |
| `MEETS_BASIC_INTEGRITY` | Device passes basic checks | Medium |
| `MEETS_VIRTUAL_INTEGRITY` | Emulator with Google Play | Low |
| (empty) | Device failed checks | No trust |

### Best practices
```kotlin
// 1. Always verify on server (not client!)

// 2. Use request hash to bind to data
val requestHash = sensitiveData.hashCode().toString()

// 3. Pre-prepare provider
// (call prepareIntegrityToken() at app startup)

// 4. Cache results (but not tokens!)
// Token is valid for single request only

// 5. Graceful degradation for devices without Google Play
if (!isGooglePlayServicesAvailable()) {
    // Alternative logic (with limited functionality)
}
```

### Limitations
| Aspect | Description |
|--------|-------------|
| Quota | 10,000 requests/day free |
| Latency | ~200-500ms per request |
| Availability | Only devices with Google Play |
| Bypass | Skilled attacker can bypass (defence in depth) |

---

## Follow-ups

- How do you handle devices without Google Play Services?
- What is the migration path from SafetyNet to Play Integrity?
- How do you implement defence in depth with Play Integrity?
- What are the privacy implications of device attestation?

## References

- https://developer.android.com/google/play/integrity
- https://developer.android.com/google/play/integrity/verdicts
- https://developer.android.com/google/play/integrity/setup

## Related Questions

### Prerequisites (Easier)
- [[q-root-detection--security--medium]] - Root detection basics

### Related (Same Level)
- [[q-android-keystore--security--hard]] - Key attestation
- [[q-ssl-certificate-pinning--security--hard]] - Certificate pinning
