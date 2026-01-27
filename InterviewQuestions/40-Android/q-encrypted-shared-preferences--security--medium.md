---
id: android-sec-002
title: EncryptedSharedPreferences and EncryptedFile / EncryptedSharedPreferences i
  EncryptedFile
aliases:
- EncryptedSharedPreferences
- EncryptedFile
- Jetpack Security
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
- q-android-keystore--security--hard
- q-secure-data-storage--security--medium
- q-sharedpreferences-definition--android--easy
sources:
- https://developer.android.com/topic/security/data
- https://developer.android.com/reference/androidx/security/crypto/EncryptedSharedPreferences
anki_cards:
- slug: android-sec-002-0-en
  language: en
- slug: android-sec-002-0-ru
  language: ru
---
# Vopros (RU)
> Kak ispol'zovat' EncryptedSharedPreferences i EncryptedFile dlya bezopasnogo hraneniya dannyh?

# Question (EN)
> How do you use EncryptedSharedPreferences and EncryptedFile for secure data storage?

---

## Otvet (RU)

**Teoriya:**
**EncryptedSharedPreferences** i **EncryptedFile** - chast' biblioteki Jetpack Security (androidx.security.crypto), kotoraya predostavlyaet prostoj API dlya shifrovannogo hraneniya dannyh s ispol'zovaniem Android Keystore.

### Preimushchestva
- **Prostota**: API sovmestim s obychnym SharedPreferences
- **Bezopasnost'**: AES-256-GCM dlya znachenij, AES-256-SIV dlya klyuchej
- **Apparatnaya zashchita**: Master-klyuch hranitsya v Android Keystore

### Nastroyka zavisimostej
```kotlin
// build.gradle.kts
dependencies {
    implementation("androidx.security:security-crypto:1.1.0-alpha06")
    // Dlya Kotlin Coroutines podderzhki
    implementation("androidx.security:security-crypto-ktx:1.1.0-alpha06")
}
```

### EncryptedSharedPreferences
```kotlin
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class SecurePreferencesManager(private val context: Context) {

    // Sozdanie master-klyucha (hranitsya v Android Keystore)
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        // Optsional'no: trebovat' razblokironku ustroystva
        .setUserAuthenticationRequired(
            true,
            MasterKey.getDefaultAuthenticationValidityDurationSeconds()
        )
        .build()

    // Sozdanie zashifrovannyh preferences
    private val encryptedPrefs: SharedPreferences = EncryptedSharedPreferences.create(
        context,
        "secure_prefs",           // Imya fayla
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,  // Dlya klyuchej
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM // Dlya znachenij
    )

    // Sohranenie tokena (API identichen obychnym SharedPreferences)
    fun saveAuthToken(token: String) {
        encryptedPrefs.edit()
            .putString("auth_token", token)
            .apply()
    }

    fun getAuthToken(): String? {
        return encryptedPrefs.getString("auth_token", null)
    }

    // Sohranenie chuvstvitel'nyh dannyh
    fun saveUserCredentials(userId: String, refreshToken: String) {
        encryptedPrefs.edit()
            .putString("user_id", userId)
            .putString("refresh_token", refreshToken)
            .putLong("token_saved_at", System.currentTimeMillis())
            .apply()
    }

    fun clearCredentials() {
        encryptedPrefs.edit()
            .remove("user_id")
            .remove("auth_token")
            .remove("refresh_token")
            .apply()
    }
}
```

### EncryptedFile dlya bol'shih dannyh
```kotlin
import androidx.security.crypto.EncryptedFile

class SecureFileManager(private val context: Context) {

    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    // Zapis' zashifrovannogo fayla
    fun writeSecureFile(filename: String, content: ByteArray) {
        val file = File(context.filesDir, filename)

        // Udalyaem sushchestvuyushchiy fayl (EncryptedFile ne perepisyvaet)
        if (file.exists()) {
            file.delete()
        }

        val encryptedFile = EncryptedFile.Builder(
            context,
            file,
            masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()

        encryptedFile.openFileOutput().use { outputStream ->
            outputStream.write(content)
        }
    }

    // Chtenie zashifrovannogo fayla
    fun readSecureFile(filename: String): ByteArray? {
        val file = File(context.filesDir, filename)
        if (!file.exists()) return null

        val encryptedFile = EncryptedFile.Builder(
            context,
            file,
            masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()

        return encryptedFile.openFileInput().use { inputStream ->
            inputStream.readBytes()
        }
    }

    // Sohranenie JSON ob"ekta
    fun saveSecureJson(filename: String, data: Any) {
        val json = Json.encodeToString(data)
        writeSecureFile(filename, json.toByteArray(Charsets.UTF_8))
    }

    inline fun <reified T> readSecureJson(filename: String): T? {
        val bytes = readSecureFile(filename) ?: return null
        return Json.decodeFromString(String(bytes, Charsets.UTF_8))
    }
}
```

### Migraciya s obychnyh SharedPreferences
```kotlin
fun migrateToEncrypted(context: Context) {
    val oldPrefs = context.getSharedPreferences("old_prefs", Context.MODE_PRIVATE)
    val secureManager = SecurePreferencesManager(context)

    // Kopiruem dannye
    oldPrefs.getString("auth_token", null)?.let { token ->
        secureManager.saveAuthToken(token)
    }

    // Udalyaem starye dannye
    oldPrefs.edit().clear().apply()

    // Udalyaem fajl
    File(context.filesDir.parent, "shared_prefs/old_prefs.xml").delete()
}
```

### Obrabotka oshibok
```kotlin
fun getEncryptedPrefsOrNull(context: Context): SharedPreferences? {
    return try {
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()

        EncryptedSharedPreferences.create(
            context,
            "secure_prefs",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    } catch (e: GeneralSecurityException) {
        // Klyuch povrezhden ili nedostupen
        Log.e("Security", "Failed to create encrypted prefs", e)
        // Vosstanovlenie: udalit' starye i sozdat' novye
        context.deleteSharedPreferences("secure_prefs")
        null
    } catch (e: IOException) {
        Log.e("Security", "IO error with encrypted prefs", e)
        null
    }
}
```

### Vazhno
| Aspekt | Opisanie |
|--------|----------|
| Proizvoditel'nost' | Pervaya inicializaciya mozhet zanyat' ~50-100ms |
| Razmer | Ne rekomenduetsya dlya bol'shih ob"emov (>1MB) |
| Backup | Fajly mozhno vklyuchit' v Android Backup (klyuch ostanetsya v Keystore) |
| Wipe | Pri sbrose k zavodskim nastrojkam dannye teryayutsya |

---

## Answer (EN)

**Theory:**
**EncryptedSharedPreferences** and **EncryptedFile** are part of the Jetpack Security library (androidx.security.crypto), providing a simple API for encrypted data storage using Android Keystore.

### Benefits
- **Simplicity**: API compatible with regular SharedPreferences
- **Security**: AES-256-GCM for values, AES-256-SIV for keys
- **Hardware-backed**: Master key stored in Android Keystore

### Setup dependencies
```kotlin
// build.gradle.kts
dependencies {
    implementation("androidx.security:security-crypto:1.1.0-alpha06")
    // For Kotlin Coroutines support
    implementation("androidx.security:security-crypto-ktx:1.1.0-alpha06")
}
```

### EncryptedSharedPreferences
```kotlin
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class SecurePreferencesManager(private val context: Context) {

    // Create master key (stored in Android Keystore)
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        // Optional: require device unlock
        .setUserAuthenticationRequired(
            true,
            MasterKey.getDefaultAuthenticationValidityDurationSeconds()
        )
        .build()

    // Create encrypted preferences
    private val encryptedPrefs: SharedPreferences = EncryptedSharedPreferences.create(
        context,
        "secure_prefs",           // File name
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,  // For keys
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM // For values
    )

    // Save token (API identical to regular SharedPreferences)
    fun saveAuthToken(token: String) {
        encryptedPrefs.edit()
            .putString("auth_token", token)
            .apply()
    }

    fun getAuthToken(): String? {
        return encryptedPrefs.getString("auth_token", null)
    }

    // Save sensitive data
    fun saveUserCredentials(userId: String, refreshToken: String) {
        encryptedPrefs.edit()
            .putString("user_id", userId)
            .putString("refresh_token", refreshToken)
            .putLong("token_saved_at", System.currentTimeMillis())
            .apply()
    }

    fun clearCredentials() {
        encryptedPrefs.edit()
            .remove("user_id")
            .remove("auth_token")
            .remove("refresh_token")
            .apply()
    }
}
```

### EncryptedFile for larger data
```kotlin
import androidx.security.crypto.EncryptedFile

class SecureFileManager(private val context: Context) {

    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    // Write encrypted file
    fun writeSecureFile(filename: String, content: ByteArray) {
        val file = File(context.filesDir, filename)

        // Delete existing file (EncryptedFile doesn't overwrite)
        if (file.exists()) {
            file.delete()
        }

        val encryptedFile = EncryptedFile.Builder(
            context,
            file,
            masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()

        encryptedFile.openFileOutput().use { outputStream ->
            outputStream.write(content)
        }
    }

    // Read encrypted file
    fun readSecureFile(filename: String): ByteArray? {
        val file = File(context.filesDir, filename)
        if (!file.exists()) return null

        val encryptedFile = EncryptedFile.Builder(
            context,
            file,
            masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()

        return encryptedFile.openFileInput().use { inputStream ->
            inputStream.readBytes()
        }
    }

    // Save JSON object
    fun saveSecureJson(filename: String, data: Any) {
        val json = Json.encodeToString(data)
        writeSecureFile(filename, json.toByteArray(Charsets.UTF_8))
    }

    inline fun <reified T> readSecureJson(filename: String): T? {
        val bytes = readSecureFile(filename) ?: return null
        return Json.decodeFromString(String(bytes, Charsets.UTF_8))
    }
}
```

### Migration from regular SharedPreferences
```kotlin
fun migrateToEncrypted(context: Context) {
    val oldPrefs = context.getSharedPreferences("old_prefs", Context.MODE_PRIVATE)
    val secureManager = SecurePreferencesManager(context)

    // Copy data
    oldPrefs.getString("auth_token", null)?.let { token ->
        secureManager.saveAuthToken(token)
    }

    // Clear old data
    oldPrefs.edit().clear().apply()

    // Delete file
    File(context.filesDir.parent, "shared_prefs/old_prefs.xml").delete()
}
```

### Error handling
```kotlin
fun getEncryptedPrefsOrNull(context: Context): SharedPreferences? {
    return try {
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()

        EncryptedSharedPreferences.create(
            context,
            "secure_prefs",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    } catch (e: GeneralSecurityException) {
        // Key corrupted or unavailable
        Log.e("Security", "Failed to create encrypted prefs", e)
        // Recovery: delete old and create new
        context.deleteSharedPreferences("secure_prefs")
        null
    } catch (e: IOException) {
        Log.e("Security", "IO error with encrypted prefs", e)
        null
    }
}
```

### Important notes
| Aspect | Description |
|--------|-------------|
| Performance | First initialization may take ~50-100ms |
| Size | Not recommended for large data (>1MB) |
| Backup | Files can be included in Android Backup (key stays in Keystore) |
| Wipe | Data lost on factory reset |

---

## Follow-ups

- How do you handle key corruption or loss scenarios?
- What is the difference between EncryptedSharedPreferences and DataStore with encryption?
- How do you test code that uses EncryptedSharedPreferences?
- What are the thread-safety guarantees of EncryptedSharedPreferences?

## References

- https://developer.android.com/topic/security/data
- https://developer.android.com/reference/androidx/security/crypto/EncryptedSharedPreferences
- https://developer.android.com/reference/androidx/security/crypto/EncryptedFile

## Related Questions

### Prerequisites (Easier)
- [[q-sharedpreferences-definition--android--easy]] - Basic SharedPreferences

### Related (Same Level)
- [[q-secure-data-storage--security--medium]] - Where to store sensitive data
- [[q-android-keystore--security--hard]] - Android Keystore system
