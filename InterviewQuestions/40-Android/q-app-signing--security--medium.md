---
id: sec-010
title: App Signing and Play App Signing / Podpis' prilozhenij i Play App Signing
aliases:
- App Signing
- Play App Signing
- APK Signing
- Key Rotation
topic: android
subtopics:
- security
- release
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
- q-proguard-r8--security--medium
sources:
- https://developer.android.com/studio/publish/app-signing
- https://developer.android.com/build/building-cmdline#sign_cmdline
---
# Vopros (RU)
> Kak rabotaet podpis' Android prilozhenij i chto takoe Play App Signing?

# Question (EN)
> How does Android app signing work and what is Play App Signing?

---

## Otvet (RU)

**Teoriya:**
**Podpis' prilozheniya** - eto kriptograficheskij mehanizm, garantiruyushchij:
- **Podlinnost'**: prilozhenie sozdano opredelennym razrabotchikom
- **Celostnost'**: APK ne byl modificirovan posle podpisi
- **Obnovleniya**: tol'ko vladelets klyucha mozhet vypuskat' obnovleniya

### Skhemy podpisi (v hronologicheskom poryadke)
| Skhema | API | Opisanie |
|--------|-----|----------|
| v1 (JAR) | Vse | Podpis' kazhdogo fayla v APK |
| v2 | 24+ | Podpis' vsego APK kak bloka |
| v3 | 28+ | Podderzhka rotacii klyuchej |
| v4 | 30+ | Inkremental'naya ustanovka (streaming) |

### Tipy klyuchej
```
Upload Key (Klyuch zagruzki)
    |
    v
[Google Play Console]
    |
    v
App Signing Key (Klyuch podpisi)
    |
    v
[Podpisannyj APK/AAB]
```

- **Upload Key**: ispol'zuete vy dlya zagruzki v Google Play
- **App Signing Key**: hranitsya v Google, ispol'zuetsya dlya final'noj podpisi

### Sozdanie klyucha (keystore)
```bash
# Sozdanie novogo keystore s klyuchom
keytool -genkeypair \
    -v \
    -keystore my-release-key.jks \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -alias my-key-alias \
    -storetype JKS

# Vvod informacii:
# - Parol' keystore
# - Parol' klyucha (mozhet sovpadat')
# - Imya, organizaciya, strana
```

### Nastrojka v Gradle
```kotlin
// build.gradle.kts (module)
android {
    signingConfigs {
        create("release") {
            // NE HARDCODE PAROLI V KODE!
            // Ispol'zujte local.properties ili env peremennye

            storeFile = file(System.getenv("KEYSTORE_PATH") ?: "release.keystore")
            storePassword = System.getenv("KEYSTORE_PASSWORD") ?: ""
            keyAlias = System.getenv("KEY_ALIAS") ?: ""
            keyPassword = System.getenv("KEY_PASSWORD") ?: ""
        }
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

### Bezopasnoye hranenie parolej
```properties
# local.properties (NE KOMMITIT'!)
KEYSTORE_PATH=/path/to/keystore.jks
KEYSTORE_PASSWORD=secure_password
KEY_ALIAS=my-alias
KEY_PASSWORD=key_password
```

```kotlin
// build.gradle.kts
import java.util.Properties

val localProperties = Properties().apply {
    val file = rootProject.file("local.properties")
    if (file.exists()) {
        load(file.inputStream())
    }
}

android {
    signingConfigs {
        create("release") {
            storeFile = file(localProperties.getProperty("KEYSTORE_PATH"))
            storePassword = localProperties.getProperty("KEYSTORE_PASSWORD")
            keyAlias = localProperties.getProperty("KEY_ALIAS")
            keyPassword = localProperties.getProperty("KEY_PASSWORD")
        }
    }
}
```

### Play App Signing
```kotlin
// Preimushchestva:
// 1. Google hranit app signing key - vy ne poteryaete ego
// 2. Esli upload key skompromitirovan - mozhno zamenit'
// 3. Google optimiziruet APK dlya kazhdogo ustrojstva
// 4. Podderzhka app bundles (AAB)

// Nastrojka:
// 1. V Google Play Console: Release > Setup > App signing
// 2. Vybrat' "Let Google manage and protect your app signing key"
// 3. Zagruzit' upload key ili sozdat' novyj

// Generaciya upload key
// keytool -genkeypair -v -keystore upload-key.jks ...
```

### Rotaciya klyuchej (APK Signature Scheme v3)
```bash
# 1. Sozdayom novyj klyuch
keytool -genkeypair \
    -v \
    -keystore new-key.jks \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -alias new-alias

# 2. Sozdayom lineage (cepochku doveriya)
apksigner lineage \
    --old-signer-keystore old-key.jks \
    --old-signer-key-alias old-alias \
    --new-signer-keystore new-key.jks \
    --new-signer-key-alias new-alias \
    --out signing-lineage.bin

# 3. Podpisyvayom s lineage
apksigner sign \
    --ks new-key.jks \
    --ks-key-alias new-alias \
    --lineage signing-lineage.bin \
    --rotation-min-sdk-version 28 \
    app-release.apk
```

### Proverka podpisi
```bash
# Proverka podpisi APK
apksigner verify --verbose --print-certs app-release.apk

# Proverka keystore
keytool -list -v -keystore release.keystore

# Poluchenie SHA-256 otpechatka (dlya Google APIs, Firebase)
keytool -list -v -keystore release.keystore -alias my-alias | grep "SHA256"
```

### Oshibki i resheniya
```kotlin
// Oshibka: "APK signature verification failed"
// Prichina: APK modificirovan ili podpisan drugim klyuchom

// Oshibka: "INSTALL_PARSE_FAILED_NO_CERTIFICATES"
// Prichina: APK ne podpisan

// Oshibka: "INSTALL_FAILED_UPDATE_INCOMPATIBLE"
// Prichina: Obnovlenie podpisano drugim klyuchom
// Reshenie: Udalit' staruyu versiyu ili ispol'zovat' tot zhe klyuch
```

### CI/CD integraciya
```yaml
# GitHub Actions primer
name: Build Release

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Decode Keystore
        run: |
          echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > release.keystore

      - name: Build Release APK
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: ./gradlew assembleRelease

      - name: Upload to Play Store
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.SERVICE_ACCOUNT_JSON }}
          packageName: com.example.app
          releaseFiles: app/build/outputs/bundle/release/app-release.aab
          track: internal
```

### Luchshie praktiki
| Praktika | Opisanie |
|----------|----------|
| Play App Signing | VSEGDA ispol'zujte dlya novyh prilozhenij |
| Backup | Sohranyajte upload key v neskol'kih mestah |
| Slozhnyj parol' | Minimum 16 simvolov, sluchajnyj |
| Srok dejstviya | 25+ let dlya production klyuchej |
| Razdelenie | Raznye klyuchi dlya raznye prilozhenij |
| Versioning | Ne ispolzujte odin klyuch dlya debug i release |

---

## Answer (EN)

**Theory:**
**App signing** is a cryptographic mechanism that guarantees:
- **Authenticity**: app created by specific developer
- **Integrity**: APK wasn't modified after signing
- **Updates**: only key owner can release updates

### Signature schemes (chronological order)
| Scheme | API | Description |
|--------|-----|-------------|
| v1 (JAR) | All | Signs each file in APK |
| v2 | 24+ | Signs entire APK as block |
| v3 | 28+ | Key rotation support |
| v4 | 30+ | Incremental install (streaming) |

### Key types
```
Upload Key
    |
    v
[Google Play Console]
    |
    v
App Signing Key
    |
    v
[Signed APK/AAB]
```

- **Upload Key**: you use to upload to Google Play
- **App Signing Key**: stored by Google, used for final signing

### Creating keystore
```bash
# Create new keystore with key
keytool -genkeypair \
    -v \
    -keystore my-release-key.jks \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -alias my-key-alias \
    -storetype JKS

# Enter information:
# - Keystore password
# - Key password (can match)
# - Name, organization, country
```

### Gradle configuration
```kotlin
// build.gradle.kts (module)
android {
    signingConfigs {
        create("release") {
            // DON'T HARDCODE PASSWORDS!
            // Use local.properties or env variables

            storeFile = file(System.getenv("KEYSTORE_PATH") ?: "release.keystore")
            storePassword = System.getenv("KEYSTORE_PASSWORD") ?: ""
            keyAlias = System.getenv("KEY_ALIAS") ?: ""
            keyPassword = System.getenv("KEY_PASSWORD") ?: ""
        }
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

### Secure password storage
```properties
# local.properties (DON'T COMMIT!)
KEYSTORE_PATH=/path/to/keystore.jks
KEYSTORE_PASSWORD=secure_password
KEY_ALIAS=my-alias
KEY_PASSWORD=key_password
```

```kotlin
// build.gradle.kts
import java.util.Properties

val localProperties = Properties().apply {
    val file = rootProject.file("local.properties")
    if (file.exists()) {
        load(file.inputStream())
    }
}

android {
    signingConfigs {
        create("release") {
            storeFile = file(localProperties.getProperty("KEYSTORE_PATH"))
            storePassword = localProperties.getProperty("KEYSTORE_PASSWORD")
            keyAlias = localProperties.getProperty("KEY_ALIAS")
            keyPassword = localProperties.getProperty("KEY_PASSWORD")
        }
    }
}
```

### Play App Signing
```kotlin
// Benefits:
// 1. Google stores app signing key - you can't lose it
// 2. If upload key compromised - can be replaced
// 3. Google optimizes APK for each device
// 4. App bundles (AAB) support

// Setup:
// 1. In Google Play Console: Release > Setup > App signing
// 2. Select "Let Google manage and protect your app signing key"
// 3. Upload existing key or create new

// Generate upload key
// keytool -genkeypair -v -keystore upload-key.jks ...
```

### Key rotation (APK Signature Scheme v3)
```bash
# 1. Create new key
keytool -genkeypair \
    -v \
    -keystore new-key.jks \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -alias new-alias

# 2. Create lineage (trust chain)
apksigner lineage \
    --old-signer-keystore old-key.jks \
    --old-signer-key-alias old-alias \
    --new-signer-keystore new-key.jks \
    --new-signer-key-alias new-alias \
    --out signing-lineage.bin

# 3. Sign with lineage
apksigner sign \
    --ks new-key.jks \
    --ks-key-alias new-alias \
    --lineage signing-lineage.bin \
    --rotation-min-sdk-version 28 \
    app-release.apk
```

### Signature verification
```bash
# Verify APK signature
apksigner verify --verbose --print-certs app-release.apk

# Verify keystore
keytool -list -v -keystore release.keystore

# Get SHA-256 fingerprint (for Google APIs, Firebase)
keytool -list -v -keystore release.keystore -alias my-alias | grep "SHA256"
```

### Errors and solutions
```kotlin
// Error: "APK signature verification failed"
// Cause: APK modified or signed with different key

// Error: "INSTALL_PARSE_FAILED_NO_CERTIFICATES"
// Cause: APK not signed

// Error: "INSTALL_FAILED_UPDATE_INCOMPATIBLE"
// Cause: Update signed with different key
// Solution: Uninstall old version or use same key
```

### CI/CD integration
```yaml
# GitHub Actions example
name: Build Release

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Decode Keystore
        run: |
          echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > release.keystore

      - name: Build Release APK
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: ./gradlew assembleRelease

      - name: Upload to Play Store
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.SERVICE_ACCOUNT_JSON }}
          packageName: com.example.app
          releaseFiles: app/build/outputs/bundle/release/app-release.aab
          track: internal
```

### Best practices
| Practice | Description |
|----------|-------------|
| Play App Signing | ALWAYS use for new apps |
| Backup | Store upload key in multiple locations |
| Strong password | Minimum 16 characters, random |
| Validity period | 25+ years for production keys |
| Separation | Different keys for different apps |
| Versioning | Don't use same key for debug and release |

---

## Follow-ups

- What happens if you lose your signing key?
- How do you migrate an existing app to Play App Signing?
- What is the difference between signing an APK and an AAB?
- How do you handle multiple keystores for different flavors?

## References

- https://developer.android.com/studio/publish/app-signing
- https://developer.android.com/build/building-cmdline#sign_cmdline
- https://support.google.com/googleplay/android-developer/answer/9842756

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - Android basics

### Related (Same Level)
- [[q-proguard-r8--security--medium]] - Code obfuscation
