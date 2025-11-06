---
id: android-466
title: Data Encryption At Rest / Шифрование данных в покое
aliases: [Data Encryption At Rest, Шифрование данных в покое]
topic: android
subtopics:
  - files-media
  - keystore-crypto
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-encryption
created: 2025-10-20
updated: 2025-11-02
tags: [android/files-media, android/keystore-crypto, difficulty/medium, encryption]
sources:
  - https://developer.android.com/guide/topics/security/encryption
---

# Вопрос (RU)
> Как реализовать шифрование данных в покое с помощью EncryptedSharedPreferences и SQLCipher для Room? Сравните подходы, влияние на производительность и стратегии управления ключами.

# Question (EN)
> Implement data encryption at rest using EncryptedSharedPreferences and SQLCipher for Room. Compare approaches, performance impact, and key management strategies.

## Ответ (RU)

**Шифрование в покое** защищает данные на устройстве от несанкционированного доступа даже при физическом компрометировании. Android предлагает три основных решения: `EncryptedSharedPreferences` (токены, настройки), `SQLCipher` (базы данных), `EncryptedFile` (файлы). Все они используют `Android Keystore` для безопасного хранения ключей шифрования.

### Ключевые Принципы

**Архитектура:**
- Данные шифруются `AES-256-GCM` перед записью на диск (аутентифицированное шифрование)
- Ключи хранятся в `Android Keystore` (аппаратная защита на поддерживаемых устройствах через StrongBox)
- Автоматическое управление жизненным циклом ключей через `MasterKey` API
- Двухуровневая защита: шифрование ключей (envelope encryption) + шифрование данных

| Подход | Использование | Производительность | Сложность |
|--------|--------------|-------------------|-----------|
| `EncryptedSharedPreferences` | Токены, настройки | Быстро (~5% overhead) | Простая |
| `SQLCipher` | Базы данных | Умеренно (~15-20% overhead) | Средняя |
| `EncryptedFile` | Медиа, документы | Медленно (зависит от размера) | Средняя |

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
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun saveToken(token: String) {
        prefs.edit { putString("auth_token", token) }
    }
}
```

**Важно:** `EncryptedSharedPreferences` шифрует как ключи (`AES256_SIV` — детерминированное), так и значения (`AES256_GCM` — аутентифицированное). Для критичных данных используйте `commit()` вместо `apply()` для синхронной записи и гарантии сохранения.

### 2. SQLCipher Для Room

```kotlin
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    companion object {
        fun create(context: Context): AppDatabase {
            val passphrase = getOrCreatePassphrase(context)
            val factory = SupportFactory(SQLiteDatabase.getBytes(passphrase.toCharArray()))
            return Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
                .openHelperFactory(factory)
                .build()
        }

        private fun getOrCreatePassphrase(context: Context): String {
            val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
            return if (keyStore.containsAlias("db_key")) {
                val secretKey = keyStore.getKey("db_key", null) as SecretKey
                Base64.encodeToString(secretKey.encoded, Base64.NO_WRAP)
            } else {
                val keyGen = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
                val spec = KeyGenParameterSpec.Builder("db_key",
                    KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
                    .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                    .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                    .setRandomizedEncryptionRequired(false)
                    .build()
                keyGen.init(spec)
                Base64.encodeToString(keyGen.generateKey().encoded, Base64.NO_WRAP)
            }
        }
    }
}
```

### 3. Управление Ключами

**Критичные аспекты:**
- Используйте `StrongBox Keymaster` (API 28+) для аппаратной изоляции: `setIsStrongBoxBacked(true)` — ключи хранятся в отдельном чипе, недоступном даже root-доступу
- Привязка к биометрии: `setUserAuthenticationRequired(true)` + `setUserAuthenticationValidityDurationSeconds(-1)` — ключ доступен только после аутентификации пользователя
- Ротация ключей: при компрометации создавайте новый `MasterKey`, перешифровывайте данные старым ключом и сохраняйте новым

```kotlin
// ❌ НЕПРАВИЛЬНО: ключ в коде — легко извлечь из APK
val hardcodedKey = "my_secret_key_123"

// ✅ ПРАВИЛЬНО: ключ в Keystore с биометрией
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .setUserAuthenticationRequired(true, 30) // требует аутентификацию каждые 30 сек
    .build()
```

### Производительность

**Бенчмарки (средние значения):**
- `EncryptedSharedPreferences`: 1-2ms на операцию чтения/записи (незначительный overhead)
- `SQLCipher`: +15-20% времени выполнения запросов по сравнению с обычным SQLite (приемлемо для большинства случаев)
- `EncryptedFile`: зависит от размера (1MB файл ~50-100ms)

**Оптимизации:**
- Минимизируйте количество операций шифрования/дешифрования — кешируйте часто используемые данные
- Используйте батчинг для `SQLCipher` (транзакции) — группировка операций снижает overhead
- Кешируйте расшифрованные данные в памяти с осторожностью (риск утечки через дампы памяти) — очищайте кеш при выходе из приложения

## Answer (EN)

**Encryption at rest** protects data on the device from unauthorized access even when physically compromised. Android offers three primary solutions: `EncryptedSharedPreferences` (tokens, settings), `SQLCipher` (databases), `EncryptedFile` (files). All use `Android Keystore` for secure key storage.

### Core Principles

**Architecture:**
- Data encrypted with `AES-256-GCM` before disk write (authenticated encryption)
- Keys stored in `Android Keystore` (hardware-backed on supported devices via StrongBox)
- Automatic key lifecycle management via `MasterKey` API
- Two-tier protection: key encryption (envelope encryption) + data encryption

| Approach | Use Case | Performance | Complexity |
|----------|----------|-------------|------------|
| `EncryptedSharedPreferences` | Tokens, settings | Fast (~5% overhead) | Simple |
| `SQLCipher` | Databases | Moderate (~15-20% overhead) | Medium |
| `EncryptedFile` | Media, documents | Slow (size-dependent) | Medium |

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
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun saveToken(token: String) {
        prefs.edit { putString("auth_token", token) }
    }
}
```

**Important:** `EncryptedSharedPreferences` encrypts both keys (`AES256_SIV` — deterministic) and values (`AES256_GCM` — authenticated). For critical data use `commit()` instead of `apply()` for synchronous writes and guaranteed persistence.

### 2. SQLCipher for Room

```kotlin
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    companion object {
        fun create(context: Context): AppDatabase {
            val passphrase = getOrCreatePassphrase(context)
            val factory = SupportFactory(SQLiteDatabase.getBytes(passphrase.toCharArray()))
            return Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
                .openHelperFactory(factory)
                .build()
        }

        private fun getOrCreatePassphrase(context: Context): String {
            val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
            return if (keyStore.containsAlias("db_key")) {
                val secretKey = keyStore.getKey("db_key", null) as SecretKey
                Base64.encodeToString(secretKey.encoded, Base64.NO_WRAP)
            } else {
                val keyGen = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
                val spec = KeyGenParameterSpec.Builder("db_key",
                    KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
                    .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                    .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                    .setRandomizedEncryptionRequired(false)
                    .build()
                keyGen.init(spec)
                Base64.encodeToString(keyGen.generateKey().encoded, Base64.NO_WRAP)
            }
        }
    }
}
```

### 3. Key Management

**Critical aspects:**
- Use `StrongBox Keymaster` (API 28+) for hardware isolation: `setIsStrongBoxBacked(true)` — keys stored in separate chip, inaccessible even to root
- Biometric binding: `setUserAuthenticationRequired(true)` + `setUserAuthenticationValidityDurationSeconds(-1)` — key accessible only after user authentication
- Key rotation: on compromise create new `MasterKey`, re-encrypt data with old key and save with new one

```kotlin
// ❌ WRONG: hardcoded key — easily extractable from APK
val hardcodedKey = "my_secret_key_123"

// ✅ CORRECT: Keystore key with biometric
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .setUserAuthenticationRequired(true, 30) // requires auth every 30 sec
    .build()
```

### Performance

**Benchmarks (average values):**
- `EncryptedSharedPreferences`: 1-2ms per read/write operation (negligible overhead)
- `SQLCipher`: +15-20% query execution time vs plain SQLite (acceptable for most cases)
- `EncryptedFile`: size-dependent (1MB file ~50-100ms)

**Optimizations:**
- Minimize encryption/decryption operations — cache frequently used data
- Use batching for `SQLCipher` (transactions) — grouping operations reduces overhead
- Cache decrypted data in memory cautiously (memory dump leak risk) — clear cache on app exit

## Follow-ups

- How to migrate from plain to encrypted database without data loss?
- What happens to encrypted data when user changes device PIN/pattern?
- How to implement key rotation for `SQLCipher` database?
- What's the impact of `StrongBox` vs software-backed keys on performance?
- How to handle key loss or device reset scenarios?

## References

- [[c-encryption]]

## Related Questions

### Prerequisites (Easier)
- Understanding of symmetric encryption (`AES`)
- Android Storage fundamentals (`SharedPreferences`, `Room`)
- Basic knowledge of `Android Keystore`

### Related (Same Level)
- Android biometric authentication
- Secure credential storage patterns
- Data migration strategies

### Advanced (Harder)
- Hardware security module integration
- Zero-knowledge encryption patterns
- Key attestation and device integrity
