---
id: 20251020-200000
title: Database Encryption Android / Шифрование базы данных Android
aliases: ["Database Encryption Android", "Шифрование базы данных Android"]
topic: android
subtopics: [keystore-crypto, room]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-encryption, c-android-keystore, q-room-database-basics--android--medium]
created: 2025-10-20
updated: 2025-10-27
tags: [android/keystore-crypto, android/room, database, difficulty/medium, encryption, keystore, room, security, sqlcipher]
sources: [https://developer.android.com/topic/security/data]
date created: Monday, October 27th 2025, 10:27:23 pm
date modified: Thursday, October 30th 2025, 12:47:35 pm
---

# Вопрос (RU)
> Как реализовать шифрование базы данных в Android? Какие лучшие практики и доступные библиотеки?

# Question (EN)
> How do you implement database encryption in Android? What are the best practices and available libraries?

## Ответ (RU)

Шифрование базы данных в Android защищает данные в покое (at rest). Основное решение — SQLCipher с Room, в сочетании с Android Keystore для управления ключами.

### Архитектура Шифрования

**Компоненты:**
- **SQLCipher** — прозрачное AES-256 шифрование для SQLite
- **Android Keystore** — аппаратное хранение ключей шифрования
- **Room + SupportFactory** — интеграция зашифрованной БД с Room

**Принцип работы:**
Данные шифруются перед записью на диск, ключи хранятся в Keystore (не извлекаемы), расшифровка происходит автоматически при чтении.

### Реализация

**1. Настройка SQLCipher с Room:**

```kotlin
// ✅ Правильно: использование SupportFactory для шифрования
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        fun build(context: Context, passphrase: ByteArray): AppDatabase {
            val factory = SupportFactory(passphrase)
            return Room.databaseBuilder(context, AppDatabase::class.java, "encrypted.db")
                .openHelperFactory(factory)
                .build()
        }
    }
}

// ❌ Неправильно: хранение passphrase в коде
val db = AppDatabase.build(context, "hardcoded_password".toByteArray())
```

**2. Управление ключами через Keystore:**

```kotlin
// ✅ Правильно: генерация и извлечение ключа из Keystore
object KeystoreManager {
    private const val KEY_ALIAS = "db_encryption_key"

    fun getOrCreateKey(): ByteArray {
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }

        if (!keyStore.containsAlias(KEY_ALIAS)) {
            val keyGen = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
            keyGen.init(
                KeyGenParameterSpec.Builder(
                    KEY_ALIAS,
                    KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
                )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setUserAuthenticationRequired(false) // или true для биометрии
                .build()
            )
            keyGen.generateKey()
        }

        return (keyStore.getKey(KEY_ALIAS, null) as SecretKey).encoded
    }
}
```

**3. Интеграция:**

```kotlin
// ✅ Правильно: инициализация с безопасным ключом
class DatabaseProvider @Inject constructor(private val context: Context) {
    val database: AppDatabase by lazy {
        AppDatabase.build(context, KeystoreManager.getOrCreateKey())
    }
}

// ❌ Неправильно: передача user-provided пароля напрямую
// Проблема: пользователи выбирают слабые пароли
```

### Компромиссы

**Производительность:**
- Накладные расходы ~10-15% на операции чтения/записи
- Инициализация БД медленнее на ~50-100ms
- Решение: кэширование, асинхронные операции, индексы

**Безопасность:**
- Keystore защищен hardware-backed TEE на современных устройствах
- Ключи не извлекаются даже при root-доступе (на устройствах с TEE)
- Уязвимость: если устройство скомпрометировано во время работы приложения

### Лучшие Практики

- Используйте Android Keystore, никогда не храните ключи в SharedPreferences или коде
- Для особо критичных данных добавьте `setUserAuthenticationRequired(true)` — требуется биометрия
- Тестируйте миграции: SQLCipher требует re-encryption при обновлениях ключей
- Учитывайте legacy устройства без TEE — используйте StrongBox Keystore (API 28+) где доступен

## Answer (EN)

Database encryption in Android protects data at rest. The primary solution is SQLCipher with Room, combined with Android Keystore for key management.

### Encryption Architecture

**Components:**
- **SQLCipher** — transparent AES-256 encryption for SQLite
- **Android Keystore** — hardware-backed key storage
- **Room + SupportFactory** — integration of encrypted DB with Room

**How it works:**
Data is encrypted before writing to disk, keys are stored in Keystore (non-extractable), decryption happens automatically on read.

### Implementation

**1. SQLCipher with Room Setup:**

```kotlin
// ✅ Correct: using SupportFactory for encryption
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        fun build(context: Context, passphrase: ByteArray): AppDatabase {
            val factory = SupportFactory(passphrase)
            return Room.databaseBuilder(context, AppDatabase::class.java, "encrypted.db")
                .openHelperFactory(factory)
                .build()
        }
    }
}

// ❌ Wrong: hardcoding passphrase in code
val db = AppDatabase.build(context, "hardcoded_password".toByteArray())
```

**2. Key Management via Keystore:**

```kotlin
// ✅ Correct: generating and retrieving key from Keystore
object KeystoreManager {
    private const val KEY_ALIAS = "db_encryption_key"

    fun getOrCreateKey(): ByteArray {
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }

        if (!keyStore.containsAlias(KEY_ALIAS)) {
            val keyGen = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
            keyGen.init(
                KeyGenParameterSpec.Builder(
                    KEY_ALIAS,
                    KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
                )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setUserAuthenticationRequired(false) // or true for biometrics
                .build()
            )
            keyGen.generateKey()
        }

        return (keyStore.getKey(KEY_ALIAS, null) as SecretKey).encoded
    }
}
```

**3. Integration:**

```kotlin
// ✅ Correct: initialization with secure key
class DatabaseProvider @Inject constructor(private val context: Context) {
    val database: AppDatabase by lazy {
        AppDatabase.build(context, KeystoreManager.getOrCreateKey())
    }
}

// ❌ Wrong: passing user-provided password directly
// Problem: users choose weak passwords
```

### Trade-offs

**Performance:**
- ~10-15% overhead on read/write operations
- Database initialization slower by ~50-100ms
- Solution: caching, async operations, indexes

**Security:**
- Keystore protected by hardware-backed TEE on modern devices
- Keys not extractable even with root access (on TEE devices)
- Vulnerability: if device is compromised while app is running

### Best Practices

- Use Android Keystore, never store keys in SharedPreferences or code
- For highly sensitive data, add `setUserAuthenticationRequired(true)` — requires biometrics
- Test migrations: SQLCipher requires re-encryption when updating keys
- Consider legacy devices without TEE — use StrongBox Keystore (API 28+) where available


## Follow-ups

- How do you migrate from unencrypted to encrypted Room database without data loss?
- What happens to encrypted database when user changes device lock credentials?
- How do you implement biometric authentication for database access?
- What are the differences between StrongBox and regular Keystore?
- How do you handle database decryption on app startup?

## References

- [[c-encryption]]
- [[c-android-keystore]]
- https://developer.android.com/topic/security/data
- https://developer.android.com/privacy-and-security/keystore

## Related Questions

### Prerequisites
- [[q-room-database-basics--android--medium]] — Room fundamentals required for understanding encryption integration
- Understanding of Android Keystore API and symmetric encryption

### Related (Same Level)
- [[q-android-data-security--android--medium]] — Other data protection techniques
- [[q-biometric-authentication--android--medium]] — Combining biometrics with encryption

### Advanced
- [[q-android-security-hardening--android--hard]] — Advanced security patterns
- [[q-key-rotation-strategies--android--hard]] — Implementing key rotation in production
