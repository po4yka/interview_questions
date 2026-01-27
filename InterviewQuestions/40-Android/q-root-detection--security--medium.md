---
id: sec-005
title: Root Detection Techniques / Metody obnaruzheniya root
aliases:
- Root Detection
- Rooted Device Detection
- Tamper Detection
topic: android
subtopics:
- security
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
- difficulty/medium
related:
- q-play-integrity-api--security--hard
- q-proguard-r8--security--medium
sources:
- https://developer.android.com/privacy-and-security/risks/device-rooting
- https://owasp.org/www-project-mobile-security-testing-guide/
anki_cards:
- slug: sec-005-0-en
  language: en
- slug: sec-005-0-ru
  language: ru
---
# Vopros (RU)
> Kakie metody obnaruzheniya root sushchestvuyut i kakovy ih ogranicheniya?

# Question (EN)
> What root detection techniques exist and what are their limitations?

---

## Otvet (RU)

**Teoriya:**
**Root detection** - eto nabor tehnik dlya opredeleniya, imeet li ustrojstvo povyshennye privilegii (root-dostup). Vazho ponimat', chto lyuboj metod obnaruzheniya mozhet byt' obojden opredelennymi zlonamerennikam, poetomu eto - chast' strategii "defence in depth".

### Zachem obnaruzhivat' root?
- **Zashchita dannyh**: root-dostup pozvolyaet chitat' dannye lyubogo prilozheniya
- **Zashchita ot tamperov**: modifikaciya prilozheniya
- **Compliance**: trebuetsya dlya finansovyh/medicinskih prilozenij
- **Anti-piracy**: zashchita ot piratskogo ispol'zovaniya

### Osnovnye metody obnaruzheniya

```kotlin
class RootDetector(private val context: Context) {

    // Metod 1: Proverka izvestnyh root-fajlov
    private fun checkRootFiles(): Boolean {
        val paths = listOf(
            "/system/app/Superuser.apk",
            "/system/xbin/su",
            "/system/bin/su",
            "/sbin/su",
            "/data/local/xbin/su",
            "/data/local/bin/su",
            "/system/sd/xbin/su",
            "/system/bin/failsafe/su",
            "/data/local/su",
            "/su/bin/su",
            // Magisk paths
            "/sbin/.magisk",
            "/data/adb/magisk",
            "/data/adb/modules"
        )

        return paths.any { path ->
            File(path).exists()
        }
    }

    // Metod 2: Proverka izvestnyh root-paketov
    private fun checkRootPackages(): Boolean {
        val packages = listOf(
            "com.noshufou.android.su",
            "com.noshufou.android.su.elite",
            "eu.chainfire.supersu",
            "com.koushikdutta.superuser",
            "com.thirdparty.superuser",
            "com.yellowes.su",
            "com.topjohnwu.magisk",      // Magisk Manager
            "com.kingroot.kinguser",
            "com.kingo.root"
        )

        val pm = context.packageManager
        return packages.any { pkg ->
            try {
                pm.getPackageInfo(pkg, 0)
                true
            } catch (e: PackageManager.NameNotFoundException) {
                false
            }
        }
    }

    // Metod 3: Proverka vozmozhnosti vypolneniya su
    private fun checkSuBinary(): Boolean {
        return try {
            val process = Runtime.getRuntime().exec(arrayOf("/system/xbin/which", "su"))
            val reader = BufferedReader(InputStreamReader(process.inputStream))
            reader.readLine() != null
        } catch (e: Exception) {
            false
        }
    }

    // Metod 4: Proverka sistemnyh svojstv
    private fun checkBuildTags(): Boolean {
        val tags = Build.TAGS
        return tags != null && tags.contains("test-keys")
    }

    // Metod 5: Proverka SELinux statusa
    private fun checkSelinuxEnforcing(): Boolean {
        return try {
            val file = File("/sys/fs/selinux/enforce")
            if (file.exists()) {
                val content = file.readText().trim()
                content != "1"  // Ne enforcing = podozritel'no
            } else {
                true  // Net SELinux = podozritel'no
            }
        } catch (e: Exception) {
            false
        }
    }

    // Metod 6: Proverka RW montirovaniya /system
    private fun checkSystemRW(): Boolean {
        return try {
            val mounts = File("/proc/mounts").readText()
            mounts.contains("/system") && mounts.contains("rw")
        } catch (e: Exception) {
            false
        }
    }

    // Sovokupnyj rezultat
    fun isDeviceRooted(): RootCheckResult {
        val checks = mapOf(
            "root_files" to checkRootFiles(),
            "root_packages" to checkRootPackages(),
            "su_binary" to checkSuBinary(),
            "test_keys" to checkBuildTags(),
            "selinux" to checkSelinuxEnforcing(),
            "system_rw" to checkSystemRW()
        )

        val detectedMethods = checks.filter { it.value }.keys

        return RootCheckResult(
            isRooted = detectedMethods.isNotEmpty(),
            detectedMethods = detectedMethods.toList(),
            confidence = when (detectedMethods.size) {
                0 -> Confidence.LIKELY_SAFE
                1 -> Confidence.SUSPICIOUS
                2 -> Confidence.PROBABLY_ROOTED
                else -> Confidence.DEFINITELY_ROOTED
            }
        )
    }
}

data class RootCheckResult(
    val isRooted: Boolean,
    val detectedMethods: List<String>,
    val confidence: Confidence
)

enum class Confidence {
    LIKELY_SAFE,
    SUSPICIOUS,
    PROBABLY_ROOTED,
    DEFINITELY_ROOTED
}
```

### Native proverki (bolee nadezhnye)
```cpp
// native-lib.cpp
#include <jni.h>
#include <unistd.h>
#include <sys/stat.h>

extern "C" JNIEXPORT jboolean JNICALL
Java_com_example_RootDetector_nativeCheckSu(JNIEnv *env, jobject) {
    const char* paths[] = {
        "/system/xbin/su",
        "/system/bin/su",
        "/sbin/su",
        "/data/local/xbin/su"
    };

    for (const char* path : paths) {
        if (access(path, F_OK) == 0) {
            return JNI_TRUE;
        }
    }

    return JNI_FALSE;
}
```

### Ogranicheniya i sposoby obhoda
| Metod | Obhod |
|-------|-------|
| Proverka fajlov | Magisk skryvaet puti |
| Proverka paketov | Magisk Hide, pereimenovanie paketov |
| su binary | Magisk MagiskHide |
| Build tags | Modificirovannyj ROM |
| Native proverki | Frida, Xposed hooks |

### Luchshie praktiki
```kotlin
class SecurityPolicy(
    private val rootDetector: RootDetector,
    private val integrityChecker: PlayIntegrityChecker
) {
    // Defence in depth: kombinirovat' metody
    suspend fun evaluateSecurityPosture(): SecurityPosture {
        val rootResult = rootDetector.isDeviceRooted()
        val integrityResult = integrityChecker.checkIntegrity()

        return SecurityPosture(
            allowFullAccess = !rootResult.isRooted && integrityResult.isValid,
            allowLimitedAccess = rootResult.confidence != Confidence.DEFINITELY_ROOTED,
            riskLevel = calculateRiskLevel(rootResult, integrityResult)
        )
    }

    // Reakciya na obnaruzhenie root
    fun handleRootedDevice(result: RootCheckResult) {
        when (result.confidence) {
            Confidence.LIKELY_SAFE -> { /* Normal'naya rabota */ }
            Confidence.SUSPICIOUS -> {
                // Logirovanie, monitoring
                Analytics.log("suspicious_device")
            }
            Confidence.PROBABLY_ROOTED -> {
                // Ogranichennaya funkcional'nost'
                disableSensitiveFeatures()
            }
            Confidence.DEFINITELY_ROOTED -> {
                // Polnaya blokirovka ili preduprezhdenie
                showSecurityWarning()
            }
        }
    }
}
```

### Vazhnye zamechaniya
- **Ne polochajtes' tol'ko na root detection**: kombinirujte s Play Integrity API
- **Izbegajte lozhnykh srabatyvany**: nekotorye pol'zovateli imeyut legitimnye prichiny dlya root
- **Reakciya proporcional'na risku**: ne blokirujte polnost'yu dlya nizkogo riska
- **Obnolyajte proverki**: Magisk i drugie instrumenty postoyanno razvivayutsya

---

## Answer (EN)

**Theory:**
**Root detection** is a set of techniques for determining if a device has elevated privileges (root access). It's important to understand that any detection method can be bypassed by determined attackers, so this is part of a "defence in depth" strategy.

### Why detect root?
- **Data protection**: root access allows reading any app's data
- **Tamper protection**: app modification
- **Compliance**: required for financial/medical apps
- **Anti-piracy**: protection against pirated usage

### Main detection methods

```kotlin
class RootDetector(private val context: Context) {

    // Method 1: Check known root files
    private fun checkRootFiles(): Boolean {
        val paths = listOf(
            "/system/app/Superuser.apk",
            "/system/xbin/su",
            "/system/bin/su",
            "/sbin/su",
            "/data/local/xbin/su",
            "/data/local/bin/su",
            "/system/sd/xbin/su",
            "/system/bin/failsafe/su",
            "/data/local/su",
            "/su/bin/su",
            // Magisk paths
            "/sbin/.magisk",
            "/data/adb/magisk",
            "/data/adb/modules"
        )

        return paths.any { path ->
            File(path).exists()
        }
    }

    // Method 2: Check known root packages
    private fun checkRootPackages(): Boolean {
        val packages = listOf(
            "com.noshufou.android.su",
            "com.noshufou.android.su.elite",
            "eu.chainfire.supersu",
            "com.koushikdutta.superuser",
            "com.thirdparty.superuser",
            "com.yellowes.su",
            "com.topjohnwu.magisk",      // Magisk Manager
            "com.kingroot.kinguser",
            "com.kingo.root"
        )

        val pm = context.packageManager
        return packages.any { pkg ->
            try {
                pm.getPackageInfo(pkg, 0)
                true
            } catch (e: PackageManager.NameNotFoundException) {
                false
            }
        }
    }

    // Method 3: Check if su can be executed
    private fun checkSuBinary(): Boolean {
        return try {
            val process = Runtime.getRuntime().exec(arrayOf("/system/xbin/which", "su"))
            val reader = BufferedReader(InputStreamReader(process.inputStream))
            reader.readLine() != null
        } catch (e: Exception) {
            false
        }
    }

    // Method 4: Check system properties
    private fun checkBuildTags(): Boolean {
        val tags = Build.TAGS
        return tags != null && tags.contains("test-keys")
    }

    // Method 5: Check SELinux status
    private fun checkSelinuxEnforcing(): Boolean {
        return try {
            val file = File("/sys/fs/selinux/enforce")
            if (file.exists()) {
                val content = file.readText().trim()
                content != "1"  // Not enforcing = suspicious
            } else {
                true  // No SELinux = suspicious
            }
        } catch (e: Exception) {
            false
        }
    }

    // Method 6: Check /system RW mount
    private fun checkSystemRW(): Boolean {
        return try {
            val mounts = File("/proc/mounts").readText()
            mounts.contains("/system") && mounts.contains("rw")
        } catch (e: Exception) {
            false
        }
    }

    // Combined result
    fun isDeviceRooted(): RootCheckResult {
        val checks = mapOf(
            "root_files" to checkRootFiles(),
            "root_packages" to checkRootPackages(),
            "su_binary" to checkSuBinary(),
            "test_keys" to checkBuildTags(),
            "selinux" to checkSelinuxEnforcing(),
            "system_rw" to checkSystemRW()
        )

        val detectedMethods = checks.filter { it.value }.keys

        return RootCheckResult(
            isRooted = detectedMethods.isNotEmpty(),
            detectedMethods = detectedMethods.toList(),
            confidence = when (detectedMethods.size) {
                0 -> Confidence.LIKELY_SAFE
                1 -> Confidence.SUSPICIOUS
                2 -> Confidence.PROBABLY_ROOTED
                else -> Confidence.DEFINITELY_ROOTED
            }
        )
    }
}

data class RootCheckResult(
    val isRooted: Boolean,
    val detectedMethods: List<String>,
    val confidence: Confidence
)

enum class Confidence {
    LIKELY_SAFE,
    SUSPICIOUS,
    PROBABLY_ROOTED,
    DEFINITELY_ROOTED
}
```

### Native checks (more reliable)
```cpp
// native-lib.cpp
#include <jni.h>
#include <unistd.h>
#include <sys/stat.h>

extern "C" JNIEXPORT jboolean JNICALL
Java_com_example_RootDetector_nativeCheckSu(JNIEnv *env, jobject) {
    const char* paths[] = {
        "/system/xbin/su",
        "/system/bin/su",
        "/sbin/su",
        "/data/local/xbin/su"
    };

    for (const char* path : paths) {
        if (access(path, F_OK) == 0) {
            return JNI_TRUE;
        }
    }

    return JNI_FALSE;
}
```

### Limitations and bypass methods
| Method | Bypass |
|--------|--------|
| File checks | Magisk hides paths |
| Package checks | Magisk Hide, package renaming |
| su binary | Magisk MagiskHide |
| Build tags | Modified ROM |
| Native checks | Frida, Xposed hooks |

### Best practices
```kotlin
class SecurityPolicy(
    private val rootDetector: RootDetector,
    private val integrityChecker: PlayIntegrityChecker
) {
    // Defence in depth: combine methods
    suspend fun evaluateSecurityPosture(): SecurityPosture {
        val rootResult = rootDetector.isDeviceRooted()
        val integrityResult = integrityChecker.checkIntegrity()

        return SecurityPosture(
            allowFullAccess = !rootResult.isRooted && integrityResult.isValid,
            allowLimitedAccess = rootResult.confidence != Confidence.DEFINITELY_ROOTED,
            riskLevel = calculateRiskLevel(rootResult, integrityResult)
        )
    }

    // React to root detection
    fun handleRootedDevice(result: RootCheckResult) {
        when (result.confidence) {
            Confidence.LIKELY_SAFE -> { /* Normal operation */ }
            Confidence.SUSPICIOUS -> {
                // Logging, monitoring
                Analytics.log("suspicious_device")
            }
            Confidence.PROBABLY_ROOTED -> {
                // Limited functionality
                disableSensitiveFeatures()
            }
            Confidence.DEFINITELY_ROOTED -> {
                // Full block or warning
                showSecurityWarning()
            }
        }
    }
}
```

### Important notes
- **Don't rely only on root detection**: combine with Play Integrity API
- **Avoid false positives**: some users have legitimate reasons for root
- **Response proportional to risk**: don't fully block for low risk
- **Update checks**: Magisk and other tools constantly evolve

---

## Follow-ups

- How do you handle false positives in root detection?
- What is the difference between Magisk and SuperSU?
- How do you implement root detection without affecting legitimate users?
- What alternatives exist for devices without Play Services?

## References

- https://developer.android.com/privacy-and-security/risks/device-rooting
- https://owasp.org/www-project-mobile-security-testing-guide/
- https://github.com/nickyblok/root-detection-tools

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - Android basics

### Related (Same Level)
- [[q-proguard-r8--security--medium]] - Code obfuscation
- [[q-play-integrity-api--security--hard]] - Play Integrity API
