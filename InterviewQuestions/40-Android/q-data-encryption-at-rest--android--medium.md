---
id: 20251020-200000
title: Data Encryption At Rest / Шифрование данных в покое
aliases: ["Data Encryption At Rest", "Шифрование данных в покое"]
topic: android
subtopics: [files-media, keystore-crypto]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-encryption]
created: 2025-10-20
updated: 2025-10-27
tags: [android/files-media, android/keystore-crypto, encryption, difficulty/medium]
sources: ["https://developer.android.com/guide/topics/security/encryption"]
date created: Monday, October 27th 2025, 10:28:06 pm
date modified: Thursday, October 30th 2025, 12:47:32 pm
---

# Вопрос (RU)
> Как реализовать шифрование данных в покое с помощью EncryptedSharedPreferences и SQLCipher для Room? Сравните подходы, влияние на производительность и стратегии управления ключами.

# Question (EN)
> Implement data encryption at rest using EncryptedSharedPreferences and SQLCipher for Room. Compare approaches, performance impact, and key management strategies.

## Ответ (RU)

**Шифрование в покое** защищает данные на устройстве от несанкционированного доступа даже при физическом компрометировании. Android предлагает три основных решения: EncryptedSharedPreferences (токены, настройки), SQLCipher (базы данных), EncryptedFile (файлы).

### Ключевые Принципы

**Архитектура:**
- Данные шифруются AES-256-GCM перед записью на диск
- Ключи хранятся в Android Keystore (аппаратная защита на поддерживаемых устройствах)
- Автоматическое управление жизненным циклом ключей через MasterKey API
- Двухуровневая защита: шифрование ключей (envelope encryption) + шифрование данных

| Подход | Использование | Производительность | Сложность |
|--------|--------------|-------------------|-----------|
| EncryptedSharedPreferences | Токены, настройки | Быстро (~5% overhead) | Простая |
| SQLCipher | Базы данных | Умеренно (~15-20% overhead) | Средняя |
| EncryptedFile | Медиа, документы | Медленно (зависит от размера) | Средняя |

### 1. EncryptedSharedPreferences

```kotlin
class SecurePrefsManager(context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val prefs = EncryptedSharedPreferences.create(
        context,
        "secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,  // ✅ детерминированное шифрование ключей
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM // ✅ аутентифицированное шифрование значений
    )

    fun saveToken(token: String) {
        prefs.edit { putString("auth_token", token) }
    }
}
```

**Важно:** EncryptedSharedPreferences шифрует как ключи, так и значения. Для критичных данных используйте `commit()` вместо `apply()` для синхронной записи.

### 2. SQLCipher для Room

```kotlin
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    companion object {
        fun create(context: Context): AppDatabase {
            // ✅ Получаем passphrase из Keystore, не храним в коде
            val passphrase = getOrCreatePassphrase(context)
            val factory = SupportFactory(SQLiteDatabase.getBytes(passphrase.toCharArray()))

            return Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
                .openHelperFactory(factory)
                .build()
        }

        private fun getOrCreatePassphrase(context: Context): String {
            val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
            return if (keyStore.containsAlias("db_key")) {
                // Получаем существующий ключ
                val secretKey = keyStore.getKey("db_key", null) as SecretKey
                Base64.encodeToString(secretKey.encoded, Base64.NO_WRAP)
            } else {
                // Генерируем новый ключ в Keystore
                val keyGen = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
                val spec = KeyGenParameterSpec.Builder("db_key",
                    KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
                    .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                    .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                    .setRandomizedEncryptionRequired(false) // ✅ для детерминированного ключа
                    .build()
                keyGen.init(spec)
                val key = keyGen.generateKey()
                Base64.encodeToString(key.encoded, Base64.NO_WRAP)
            }
        }
    }
}
```

### 3. Управление Ключами

**Критичные аспекты:**
- Используйте StrongBox Keymaster (API 28+) для аппаратной изоляции: `setIsStrongBoxBacked(true)`
- Привязка к биометрии: `setUserAuthenticationRequired(true)` + `setUserAuthenticationValidityDurationSeconds(-1)`
- Ротация ключей: при компрометации создавайте новый MasterKey, перешифровывайте данные

```kotlin
// ❌ НЕПРАВИЛЬНО: ключ в коде
val hardcodedKey = "my_secret_key_123"

// ✅ ПРАВИЛЬНО: ключ в Keystore с биометрией
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .setUserAuthenticationRequired(true, 30) // требует аутентификацию каждые 30 сек
    .build()
```

### Производительность

**Бенчмарки (средние значения):**
- EncryptedSharedPreferences: 1-2ms на операцию чтения/записи
- SQLCipher: +15-20% времени выполнения запросов по сравнению с обычным SQLite
- EncryptedFile: зависит от размера (1MB файл ~50-100ms)

**Оптимизации:**
- Минимизируйте количество операций шифрования/дешифрования
- Используйте батчинг для SQLCipher (транзакции)
- Кешируйте расшифрованные данные в памяти с осторожностью (риск утечки через дампы памяти)

## Answer (EN)

**Encryption at rest** protects data on the device from unauthorized access even when physically compromised. Android offers three primary solutions: EncryptedSharedPreferences (tokens, settings), SQLCipher (databases), EncryptedFile (files).

### Core Principles

**Architecture:**
- Data encrypted with AES-256-GCM before disk write
- Keys stored in Android Keystore (hardware-backed on supported devices)
- Automatic key lifecycle management via MasterKey API
- Two-tier protection: key encryption (envelope encryption) + data encryption

| Approach | Use Case | Performance | Complexity |
|----------|----------|-------------|------------|
| EncryptedSharedPreferences | Tokens, settings | Fast (~5% overhead) | Simple |
| SQLCipher | Databases | Moderate (~15-20% overhead) | Medium |
| EncryptedFile | Media, documents | Slow (size-dependent) | Medium |

### 1. EncryptedSharedPreferences

```kotlin
class SecurePrefsManager(context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val prefs = EncryptedSharedPreferences.create(
        context,
        "secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,  // ✅ deterministic key encryption
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM // ✅ authenticated value encryption
    )

    fun saveToken(token: String) {
        prefs.edit { putString("auth_token", token) }
    }
}
```

**Important:** EncryptedSharedPreferences encrypts both keys and values. For critical data use `commit()` instead of `apply()` for synchronous writes.

### 2. SQLCipher for Room

```kotlin
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    companion object {
        fun create(context: Context): AppDatabase {
            // ✅ Get passphrase from Keystore, never hardcode
            val passphrase = getOrCreatePassphrase(context)
            val factory = SupportFactory(SQLiteDatabase.getBytes(passphrase.toCharArray()))

            return Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
                .openHelperFactory(factory)
                .build()
        }

        private fun getOrCreatePassphrase(context: Context): String {
            val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
            return if (keyStore.containsAlias("db_key")) {
                // Retrieve existing key
                val secretKey = keyStore.getKey("db_key", null) as SecretKey
                Base64.encodeToString(secretKey.encoded, Base64.NO_WRAP)
            } else {
                // Generate new key in Keystore
                val keyGen = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
                val spec = KeyGenParameterSpec.Builder("db_key",
                    KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
                    .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                    .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                    .setRandomizedEncryptionRequired(false) // ✅ for deterministic key
                    .build()
                keyGen.init(spec)
                val key = keyGen.generateKey()
                Base64.encodeToString(key.encoded, Base64.NO_WRAP)
            }
        }
    }
}
```

### 3. Key Management

**Critical aspects:**
- Use StrongBox Keymaster (API 28+) for hardware isolation: `setIsStrongBoxBacked(true)`
- Biometric binding: `setUserAuthenticationRequired(true)` + `setUserAuthenticationValidityDurationSeconds(-1)`
- Key rotation: on compromise create new MasterKey and re-encrypt data

```kotlin
// ❌ WRONG: hardcoded key
val hardcodedKey = "my_secret_key_123"

// ✅ CORRECT: Keystore key with biometric
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .setUserAuthenticationRequired(true, 30) // requires auth every 30 sec
    .build()
```

### Performance

**Benchmarks (average values):**
- EncryptedSharedPreferences: 1-2ms per read/write operation
- SQLCipher: +15-20% query execution time vs plain SQLite
- EncryptedFile: size-dependent (1MB file ~50-100ms)

**Optimizations:**
- Minimize encryption/decryption operations
- Use batching for SQLCipher (transactions)
- Cache decrypted data in memory cautiously (memory dump leak risk)

## Follow-ups

- How to migrate from plain to encrypted database without data loss?
- What happens to encrypted data when user changes device PIN/pattern?
- How to implement key rotation for SQLCipher database?
- What's the impact of StrongBox vs software-backed keys on performance?

## References

- [[c-encryption]]

## Related Questions

### Prerequisites
- Understanding of symmetric encryption (AES)
- Android Storage fundamentals (SharedPreferences, Room)

### Related
- Android biometric authentication
- Secure credential storage patterns
- Data migration strategies

### Advanced
- Hardware security module integration
- Zero-knowledge encryption patterns
- Key attestation and device integrity
