---
id: android-470
title: Database Encryption Android / Шифрование базы данных Android
aliases: [Database Encryption Android, Шифрование базы данных Android]
topic: android
subtopics:
  - keystore-crypto
  - room
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
tags: [android/keystore-crypto, android/room, database, difficulty/medium, encryption, keystore, room, security, sqlcipher]
sources:
  - https://developer.android.com/topic/security/data
---

# Вопрос (RU)
> Как реализовать шифрование базы данных в Android? Какие лучшие практики и доступные библиотеки?

# Question (EN)
> How do you implement database encryption in Android? What are the best practices and available libraries?

## Ответ (RU)

Шифрование базы данных в Android защищает данные в покое (at rest). Основное решение — `SQLCipher` с `Room`, в сочетании с `Android Keystore` для управления ключами. Это обеспечивает прозрачное шифрование без изменения логики работы с базой данных.

### Архитектура Шифрования

**Компоненты:**
- **`SQLCipher`** — прозрачное `AES-256` шифрование для SQLite (совместимо с `Room`)
- **`Android Keystore`** — аппаратное хранение ключей шифрования (hardware-backed TEE)
- **`Room + SupportFactory`** — интеграция зашифрованной БД с `Room` (прозрачная для разработчика)

**Принцип работы:**
Данные шифруются перед записью на диск (`AES-256` в режиме `CBC` или `GCM`), ключи хранятся в `Keystore` (не извлекаемы даже при root-доступе на устройствах с TEE), расшифровка происходит автоматически при чтении через `SupportFactory`.

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
- Накладные расходы ~10-15% на операции чтения/записи (шифрование/дешифрование)
- Инициализация БД медленнее на ~50-100ms (генерация ключа, проверка целостности)
- Решение: кэширование расшифрованных данных, асинхронные операции через `Coroutines`, оптимизация индексов

**Безопасность:**
- `Keystore` защищен hardware-backed TEE на современных устройствах (API 23+) — ключи хранятся в отдельном защищенном пространстве
- Ключи не извлекаются даже при root-доступе (на устройствах с TEE/StrongBox) — физическая изоляция
- Уязвимость: если устройство скомпрометировано во время работы приложения — расшифрованные данные доступны в памяти
- Ограничение: legacy устройства без TEE используют software-backed хранилище (менее безопасно)

### Лучшие Практики

- **Используйте `Android Keystore`** — никогда не храните ключи в `SharedPreferences`, файлах или коде
- **Биометрическая аутентификация** — для особо критичных данных используйте `setUserAuthenticationRequired(true)` с `setUserAuthenticationValidityDurationSeconds(-1)` (требуется биометрия при каждом доступе)
- **Тестируйте миграции** — `SQLCipher` требует re-encryption при обновлениях ключей (создайте новый ключ, перешифруйте данные старым, сохраните новым)
- **StrongBox Keystore** — используйте на устройствах с API 28+ где доступен (`setIsStrongBoxBacked(true)`) — максимальная защита
- **Ротация ключей** — периодически обновляйте ключи шифрования для долгосрочной безопасности

## Answer (EN)

Database encryption in Android protects data at rest. The primary solution is `SQLCipher` with `Room`, combined with `Android Keystore` for key management. This provides transparent encryption without changing database logic.

### Encryption Architecture

**Components:**
- **`SQLCipher`** — transparent `AES-256` encryption for SQLite (compatible with `Room`)
- **`Android Keystore`** — hardware-backed key storage (hardware-backed TEE)
- **`Room + SupportFactory`** — integration of encrypted DB with `Room` (transparent to developer)

**How it works:**
Data encrypted before writing to disk (`AES-256` in `CBC` or `GCM` mode), keys stored in `Keystore` (non-extractable even with root access on TEE devices), decryption happens automatically on read via `SupportFactory`.

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
- ~10-15% overhead on read/write operations (encryption/decryption)
- Database initialization slower by ~50-100ms (key generation, integrity check)
- Solution: caching decrypted data, async operations via `Coroutines`, index optimization

**Security:**
- `Keystore` protected by hardware-backed TEE on modern devices (API 23+) — keys stored in separate secure enclave
- Keys not extractable even with root access (on TEE/StrongBox devices) — physical isolation
- Vulnerability: if device compromised while app is running — decrypted data accessible in memory
- Limitation: legacy devices without TEE use software-backed storage (less secure)

### Best Practices

- **Use `Android Keystore`** — never store keys in `SharedPreferences`, files, or code
- **Biometric authentication** — for highly sensitive data use `setUserAuthenticationRequired(true)` with `setUserAuthenticationValidityDurationSeconds(-1)` (requires biometrics on each access)
- **Test migrations** — `SQLCipher` requires re-encryption when updating keys (create new key, re-encrypt data with old, save with new)
- **StrongBox Keystore** — use on devices with API 28+ where available (`setIsStrongBoxBacked(true)`) — maximum protection
- **Key rotation** — periodically update encryption keys for long-term security


## Follow-ups

- How do you migrate from unencrypted to encrypted `Room` database without data loss?
- What happens to encrypted database when user changes device lock credentials?
- How do you implement biometric authentication for database access?
- What are the differences between `StrongBox` and regular `Keystore`?
- How do you handle database decryption on app startup?
- How to implement key rotation for `SQLCipher` database?

## References

- [[c-encryption]]
- [Android Data Security Guide](https://developer.android.com/topic/security/data)
- [Android Keystore Guide](https://developer.android.com/privacy-and-security/keystore)

## Related Questions

### Prerequisites (Easier)
- Understanding of `Android Keystore` API and symmetric encryption (`AES`)
- Basic knowledge of `Room` database architecture

### Related (Same Level)
- Biometric authentication with `Keystore`
- Data encryption at rest strategies
- `SQLCipher` implementation patterns

### Advanced (Harder)
- Key rotation strategies for encrypted databases
- Multi-key encryption for different data sensitivity levels
- Performance optimization for encrypted databases
