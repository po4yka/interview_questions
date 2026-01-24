---
id: sec-007
title: Secure Data Storage on Android / Bezopasnoe hranenie dannyh v Android
aliases:
- Secure Data Storage
- Sensitive Data Storage
- Android Storage Security
topic: android
subtopics:
- security
- storage
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
- android/storage
- difficulty/medium
related:
- q-encrypted-shared-preferences--security--medium
- q-android-keystore--security--hard
- q-sharedpreferences-definition--android--easy
sources:
- https://developer.android.com/topic/security/data
- https://developer.android.com/privacy-and-security/security-tips
---
# Vopros (RU)
> Gde i kak bezopasno hranit' chuvstvitel'nye dannye v Android?

# Question (EN)
> Where and how should you securely store sensitive data on Android?

---

## Otvet (RU)

**Teoriya:**
Vybor sposoba hraneniya zavisit ot tipa dannyh, urovnya chuvstvitel'nosti i trebovanij dostupa. Android predlagaet neskol'ko mekhanizmov, kazhdyj so svoimi kompromissami.

### Ierarkhiya bezopasnosti hraneniya

| Uroven' | Mehanizm | Dlya chego |
|---------|----------|------------|
| Maksimal'nyj | Android Keystore | Kriptograficheskie klyuchi |
| Vysokij | EncryptedSharedPreferences | Tokeny, paroli |
| Srednij | Internal Storage + Encryption | Fajly s lichnymi dannymi |
| Bazovyj | Internal Storage | Nekritichnyye dannye |
| Izbegat' | External Storage | Ne dlya chuvstvitel'nyh dannyh |

### 1. Kriptograficheskie klyuchi - Android Keystore
```kotlin
// Klyuchi NIKOGDA ne dolzhny hranit'sya v kode ili failakh
// Tol'ko v Android Keystore

class KeyManager(context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .setUserAuthenticationRequired(true)
        .build()

    // Ispol'zuyte masterKey dlya EncryptedSharedPreferences/EncryptedFile
}
```

### 2. Tokeny i uchetnye dannye - EncryptedSharedPreferences
```kotlin
class SecureCredentialsManager(context: Context) {

    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val securePrefs = EncryptedSharedPreferences.create(
        context,
        "secure_credentials",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun saveAccessToken(token: String) {
        securePrefs.edit()
            .putString("access_token", token)
            .putLong("token_timestamp", System.currentTimeMillis())
            .apply()
    }

    fun getAccessToken(): String? {
        val token = securePrefs.getString("access_token", null)
        val timestamp = securePrefs.getLong("token_timestamp", 0)

        // Proverka svezhesti tokena
        val maxAge = TimeUnit.HOURS.toMillis(24)
        if (System.currentTimeMillis() - timestamp > maxAge) {
            clearCredentials()
            return null
        }

        return token
    }

    fun clearCredentials() {
        securePrefs.edit().clear().apply()
    }
}
```

### 3. Chuvstvitel'nye fajly - EncryptedFile
```kotlin
class SecureFileStorage(private val context: Context) {

    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    fun saveUserProfile(profile: UserProfile) {
        val file = File(context.filesDir, "user_profile.enc")

        if (file.exists()) file.delete()

        val encryptedFile = EncryptedFile.Builder(
            context,
            file,
            masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()

        encryptedFile.openFileOutput().use { output ->
            val json = Json.encodeToString(profile)
            output.write(json.toByteArray())
        }
    }

    fun loadUserProfile(): UserProfile? {
        val file = File(context.filesDir, "user_profile.enc")
        if (!file.exists()) return null

        val encryptedFile = EncryptedFile.Builder(
            context,
            file,
            masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()

        return encryptedFile.openFileInput().use { input ->
            val json = input.bufferedReader().readText()
            Json.decodeFromString(json)
        }
    }
}
```

### 4. Bazovoe vnutrennee hranilishche
```kotlin
// Dlya nekritichnyh dannyh - Internal Storage
// Dostupno tol'ko vasemu prilozheniyu

class InternalFileStorage(private val context: Context) {

    fun saveCache(key: String, data: String) {
        // filesDir - privatnaya direktoriya prilozheniya
        val file = File(context.filesDir, "$key.cache")
        file.writeText(data)
    }

    fun saveTempData(data: ByteArray) {
        // cacheDir - ochishaetsya sistemoj pri nehvatke mesta
        val file = File(context.cacheDir, "temp_${System.currentTimeMillis()}")
        file.writeBytes(data)
    }
}
```

### 5. Chto NE delat'
```kotlin
// OSHIBKI - Ne delayte tak!

// Hardcoded klyuchi (legko izvlech' iz APK)
const val API_KEY = "sk_live_123456789"

// Klyuchi v BuildConfig (vidny v dekompilirovannom APK)
val key = BuildConfig.SECRET_KEY

// Nezashifrovannye SharedPreferences dlya tokenov
val prefs = context.getSharedPreferences("prefs", MODE_PRIVATE)
prefs.edit().putString("token", authToken).apply()

// External Storage dlya chuvstvitel'nyh dannyh
val file = File(Environment.getExternalStorageDirectory(), "user_data.json")

// Logirovanie chuvstvitel'nyh dannyh
Log.d("Auth", "Token: $token")
```

### 6. Room Database s shifrovaniyem
```kotlin
// Dlya strukturirovannyh dannyh - SQLCipher s Room

// build.gradle.kts
// implementation("net.zetetic:android-database-sqlcipher:4.5.4")
// implementation("androidx.sqlite:sqlite-ktx:2.4.0")

class EncryptedDatabaseFactory(private val context: Context) {

    fun createEncryptedDatabase(): AppDatabase {
        // Poluchaem klyuch iz Keystore
        val passphrase = getOrCreateDatabaseKey()

        val factory = SupportFactory(passphrase)

        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app_database.db"
        )
            .openHelperFactory(factory)
            .build()
    }

    private fun getOrCreateDatabaseKey(): ByteArray {
        val prefs = EncryptedSharedPreferences.create(
            context,
            "db_key_prefs",
            getMasterKey(),
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )

        val existingKey = prefs.getString("db_key", null)
        if (existingKey != null) {
            return Base64.decode(existingKey, Base64.DEFAULT)
        }

        // Generiruem novyj klyuch
        val newKey = ByteArray(32).apply {
            SecureRandom().nextBytes(this)
        }
        prefs.edit()
            .putString("db_key", Base64.encodeToString(newKey, Base64.DEFAULT))
            .apply()

        return newKey
    }
}
```

### Tablitsa reshenij
| Tip dannyh | Reshenie | Pochemu |
|------------|----------|---------|
| API klyuchi | Sever ili Keystore | Klyuchi ne dolzhny byt' v APK |
| Auth tokeny | EncryptedSharedPreferences | Shifrovanie + prostoj API |
| Paroli pol'zovatelej | NE HRANITE | Ispol'zuyte OAuth/biometriku |
| Lichnye dokumenty | EncryptedFile | Zashchita fajlov |
| Kesh | Internal Storage | Avtomaticheskaya izolyaciya |
| Bazy dannyh | Room + SQLCipher | Shifrovanie na urovne BD |

---

## Answer (EN)

**Theory:**
Storage choice depends on data type, sensitivity level, and access requirements. Android offers several mechanisms, each with its own tradeoffs.

### Storage security hierarchy

| Level | Mechanism | Use For |
|-------|-----------|---------|
| Maximum | Android Keystore | Cryptographic keys |
| High | EncryptedSharedPreferences | Tokens, passwords |
| Medium | Internal Storage + Encryption | Files with personal data |
| Basic | Internal Storage | Non-critical data |
| Avoid | External Storage | Not for sensitive data |

### 1. Cryptographic keys - Android Keystore
```kotlin
// Keys should NEVER be stored in code or files
// Only in Android Keystore

class KeyManager(context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .setUserAuthenticationRequired(true)
        .build()

    // Use masterKey for EncryptedSharedPreferences/EncryptedFile
}
```

### 2. Tokens and credentials - EncryptedSharedPreferences
```kotlin
class SecureCredentialsManager(context: Context) {

    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val securePrefs = EncryptedSharedPreferences.create(
        context,
        "secure_credentials",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun saveAccessToken(token: String) {
        securePrefs.edit()
            .putString("access_token", token)
            .putLong("token_timestamp", System.currentTimeMillis())
            .apply()
    }

    fun getAccessToken(): String? {
        val token = securePrefs.getString("access_token", null)
        val timestamp = securePrefs.getLong("token_timestamp", 0)

        // Check token freshness
        val maxAge = TimeUnit.HOURS.toMillis(24)
        if (System.currentTimeMillis() - timestamp > maxAge) {
            clearCredentials()
            return null
        }

        return token
    }

    fun clearCredentials() {
        securePrefs.edit().clear().apply()
    }
}
```

### 3. Sensitive files - EncryptedFile
```kotlin
class SecureFileStorage(private val context: Context) {

    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    fun saveUserProfile(profile: UserProfile) {
        val file = File(context.filesDir, "user_profile.enc")

        if (file.exists()) file.delete()

        val encryptedFile = EncryptedFile.Builder(
            context,
            file,
            masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()

        encryptedFile.openFileOutput().use { output ->
            val json = Json.encodeToString(profile)
            output.write(json.toByteArray())
        }
    }

    fun loadUserProfile(): UserProfile? {
        val file = File(context.filesDir, "user_profile.enc")
        if (!file.exists()) return null

        val encryptedFile = EncryptedFile.Builder(
            context,
            file,
            masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()

        return encryptedFile.openFileInput().use { input ->
            val json = input.bufferedReader().readText()
            Json.decodeFromString(json)
        }
    }
}
```

### 4. Basic internal storage
```kotlin
// For non-critical data - Internal Storage
// Accessible only by your app

class InternalFileStorage(private val context: Context) {

    fun saveCache(key: String, data: String) {
        // filesDir - app's private directory
        val file = File(context.filesDir, "$key.cache")
        file.writeText(data)
    }

    fun saveTempData(data: ByteArray) {
        // cacheDir - cleared by system when low on space
        val file = File(context.cacheDir, "temp_${System.currentTimeMillis()}")
        file.writeBytes(data)
    }
}
```

### 5. What NOT to do
```kotlin
// MISTAKES - Don't do this!

// Hardcoded keys (easily extracted from APK)
const val API_KEY = "sk_live_123456789"

// Keys in BuildConfig (visible in decompiled APK)
val key = BuildConfig.SECRET_KEY

// Unencrypted SharedPreferences for tokens
val prefs = context.getSharedPreferences("prefs", MODE_PRIVATE)
prefs.edit().putString("token", authToken).apply()

// External Storage for sensitive data
val file = File(Environment.getExternalStorageDirectory(), "user_data.json")

// Logging sensitive data
Log.d("Auth", "Token: $token")
```

### 6. Room Database with encryption
```kotlin
// For structured data - SQLCipher with Room

// build.gradle.kts
// implementation("net.zetetic:android-database-sqlcipher:4.5.4")
// implementation("androidx.sqlite:sqlite-ktx:2.4.0")

class EncryptedDatabaseFactory(private val context: Context) {

    fun createEncryptedDatabase(): AppDatabase {
        // Get key from Keystore
        val passphrase = getOrCreateDatabaseKey()

        val factory = SupportFactory(passphrase)

        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app_database.db"
        )
            .openHelperFactory(factory)
            .build()
    }

    private fun getOrCreateDatabaseKey(): ByteArray {
        val prefs = EncryptedSharedPreferences.create(
            context,
            "db_key_prefs",
            getMasterKey(),
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )

        val existingKey = prefs.getString("db_key", null)
        if (existingKey != null) {
            return Base64.decode(existingKey, Base64.DEFAULT)
        }

        // Generate new key
        val newKey = ByteArray(32).apply {
            SecureRandom().nextBytes(this)
        }
        prefs.edit()
            .putString("db_key", Base64.encodeToString(newKey, Base64.DEFAULT))
            .apply()

        return newKey
    }
}
```

### Decision table
| Data Type | Solution | Why |
|-----------|----------|-----|
| API keys | Server or Keystore | Keys shouldn't be in APK |
| Auth tokens | EncryptedSharedPreferences | Encryption + simple API |
| User passwords | DON'T STORE | Use OAuth/biometrics |
| Personal documents | EncryptedFile | File protection |
| Cache | Internal Storage | Automatic isolation |
| Databases | Room + SQLCipher | DB-level encryption |

---

## Follow-ups

- How do you handle data backup with encrypted storage?
- What happens to encrypted data on factory reset?
- How do you migrate from unencrypted to encrypted storage?
- What are the performance implications of encryption?

## References

- https://developer.android.com/topic/security/data
- https://developer.android.com/privacy-and-security/security-tips
- https://owasp.org/www-project-mobile-security-testing-guide/

## Related Questions

### Prerequisites (Easier)
- [[q-sharedpreferences-definition--android--easy]] - SharedPreferences basics

### Related (Same Level)
- [[q-encrypted-shared-preferences--security--medium]] - EncryptedSharedPreferences
- [[q-android-keystore--security--hard]] - Android Keystore
