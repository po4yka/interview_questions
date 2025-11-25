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
status: draft
moc: moc-android
related:
  - c-android-keystore
  - q-android-security-best-practices--android--medium
  - q-android-security-practices-checklist--android--medium
  - q-data-encryption-at-rest--android--medium
created: 2025-10-20
updated: 2025-11-11
tags: [android/keystore-crypto, android/room, database, difficulty/medium, encryption, keystore, room, security, sqlcipher]
sources:
  - "https://developer.android.com/topic/security/data"
date created: Saturday, November 1st 2025, 1:27:53 pm
date modified: Tuesday, November 25th 2025, 8:54:01 pm
---

# Вопрос (RU)
> Как реализовать шифрование базы данных в Android? Какие лучшие практики и доступные библиотеки?

# Question (EN)
> How do you implement database encryption in Android? What are the best practices and available libraries?

## Ответ (RU)

Шифрование базы данных в Android защищает данные в покое (at rest). Типичное практическое решение — `SQLCipher` с `Room`, в сочетании с `Android Keystore` для безопасного управления ключами/паролем. Это обеспечивает прозрачное шифрование без изменения логики работы с базой данных.

### Архитектура Шифрования

**Компоненты:**
- **`SQLCipher`** — прозрачное шифрование (обычно `AES-256`) для SQLite (совместимо с `Room`)
- **`Android Keystore`** — защищенное (по возможности hardware-backed) хранение ключей
- **`Room + SupportFactory`** — интеграция зашифрованной БД с `Room` (прозрачная для разработчика)

**Принцип работы:**
Данные шифруются перед записью на диск (например, с использованием `AES-256` согласно реализации `SQLCipher`), ключ или passphrase защищен через `Android Keystore`, расшифровка происходит автоматически при чтении через `SupportFactory`.

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

**2. Управление ключами через Keystore (паттерн):**

Важно: ключи, сгенерированные в `Android Keystore` как `SecretKey`, часто неэкспортируемы (`encoded == null`) при hardware-backed хранении и не могут напрямую использоваться как passphrase для `SQLCipher`. Рекомендуемый подход — использовать ключ из Keystore для шифрования/дешифрования отдельно сгенерированного случайного passphrase, который хранится на диске в зашифрованном виде.

```kotlin
object KeystoreManager {
    private const val KEY_ALIAS = "db_key_wrapper"

    fun getOrCreateWrappingKey(): SecretKey {
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
                    .setUserAuthenticationRequired(false) // или true для привязки к биометрии/lock screen
                    .build()
            )
            keyGen.generateKey()
        }

        val key = keyStore.getKey(KEY_ALIAS, null) as SecretKey
        return key
    }
}

// Пример: генерация и хранение passphrase (упрощённо, без обработки ошибок и деталей формата)

fun getOrCreateSqlCipherPassphrase(context: Context): ByteArray {
    val file = File(context.filesDir, "db_passphrase.enc")
    val wrappingKey = KeystoreManager.getOrCreateWrappingKey()

    return if (file.exists()) {
        // расшифровать passphrase из файла с помощью wrappingKey
        decryptPassphrase(file.readBytes(), wrappingKey)
    } else {
        val passphrase = ByteArray(32).also { SecureRandom().nextBytes(it) }
        val encrypted = encryptPassphrase(passphrase, wrappingKey)
        file.writeBytes(encrypted)
        passphrase
    }
}
```

(Реализация `encryptPassphrase`/`decryptPassphrase` предполагает использование `AES-GCM` с IV и тегом аутентичности; детали могут обсуждаться на интервью.)

**3. Интеграция:**

```kotlin
// ✅ Правильно: инициализация с passphrase, защищённым через Keystore
class DatabaseProvider @Inject constructor(private val context: Context) {
    val database: AppDatabase by lazy {
        val passphrase = getOrCreateSqlCipherPassphrase(context)
        AppDatabase.build(context, passphrase)
    }
}

// ❌ Неправильно: передача пользовательского пароля напрямую как единственный секрет
// Проблема: пользователи выбирают слабые пароли; используйте его максимум как вход для KDF + доп. секрет.
```

### Компромиссы

**Производительность:**
- Накладные расходы ~10–15% на операции чтения/записи (шифрование/дешифрование) — оценка, зависящая от устройства и нагрузки
- Инициализация БД может быть медленнее на ~десятки миллисекунд (генерация/получение ключа, проверка целостности)
- Решения: кэширование данных, асинхронные операции через `Coroutines`, оптимизация запросов и индексов

**Безопасность:**
- При hardware-backed `Keystore` (TEE/StrongBox) ключи хранятся в изолированном окружении и неэкспортируемы даже при root-доступе
- На устройствах без TEE ключи могут быть только software-backed и потенциально уязвимее
- Уязвимость: если устройство скомпрометировано во время работы приложения, расшифрованные данные доступны в памяти и через активный процесс

### Лучшие Практики

- **Используйте `Android Keystore`** — никогда не храните ключи/пароли в открытом виде в `SharedPreferences`, файлах или коде
- **Храните passphrase непрямо** — генерируйте случайный passphrase для `SQLCipher`, шифруйте его ключом из Keystore и храните только зашифрованную версию
- **Биометрическая аутентификация** — для особо критичных данных используйте `setUserAuthenticationRequired(true)` (и при необходимости `setUserAuthenticationValidityDurationSeconds(...)`) для связывания доступа с биометрией/экраном блокировки
- **Тестируйте миграции** — при смене ключей/passphrase требуется корректное пере-шифрование БД (создать новый passphrase, расшифровать старым, зашифровать новым)
- **StrongBox Keystore** — при наличии на устройствах (API 28+) можно использовать `setIsStrongBoxBacked(true)` для максимальной защиты ключей
- **Ротация ключей** — периодически обновляйте ключи и passphrase, продумывая безопасный процесс ротации и отката

## Answer (EN)

Database encryption in Android protects data at rest. A common practical solution is `SQLCipher` with `Room`, combined with `Android Keystore` for secure key/passphrase management. This provides transparent encryption without changing the database access API.

### Encryption Architecture

**Components:**
- **`SQLCipher`** — transparent encryption (typically `AES-256`) for SQLite (compatible with `Room`)
- **`Android Keystore`** — secure (preferably hardware-backed) key storage
- **`Room + SupportFactory`** — integration of encrypted DB with `Room` (transparent to developer)

**How it works:**
Data is encrypted before being written to disk (for example with `AES-256` as implemented by SQLCipher). The key or passphrase is protected via `Android Keystore`. Decryption happens automatically on reads via `SupportFactory` when you provide the correct passphrase.

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

**2. Key Management via Keystore (pattern):**

Important: `SecretKey`s generated inside `AndroidKeyStore` are often non-exportable (`encoded == null`) when hardware-backed, so they cannot be used directly as the `SQLCipher` passphrase. Recommended pattern is to use the Keystore key to encrypt/decrypt a randomly generated passphrase that is stored on disk in encrypted form.

```kotlin
object KeystoreManager {
    private const val KEY_ALIAS = "db_key_wrapper"

    fun getOrCreateWrappingKey(): SecretKey {
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
                    .setUserAuthenticationRequired(false) // or true to bind to biometrics/lock screen
                    .build()
            )
            keyGen.generateKey()
        }

        val key = keyStore.getKey(KEY_ALIAS, null) as SecretKey
        return key
    }
}

// Example: creating and storing SQLCipher passphrase (simplified, without error handling and full format details)

fun getOrCreateSqlCipherPassphrase(context: Context): ByteArray {
    val file = File(context.filesDir, "db_passphrase.enc")
    val wrappingKey = KeystoreManager.getOrCreateWrappingKey()

    return if (file.exists()) {
        // decrypt passphrase from file using wrappingKey
        decryptPassphrase(file.readBytes(), wrappingKey)
    } else {
        val passphrase = ByteArray(32).also { SecureRandom().nextBytes(it) }
        val encrypted = encryptPassphrase(passphrase, wrappingKey)
        file.writeBytes(encrypted)
        passphrase
    }
}
```

(`encryptPassphrase`/`decryptPassphrase` would typically use AES-GCM with IV + auth tag; details can be explored in the interview.)

**3. Integration:**

```kotlin
// ✅ Correct: initialization with a passphrase protected via Keystore
class DatabaseProvider @Inject constructor(private val context: Context) {
    val database: AppDatabase by lazy {
        val passphrase = getOrCreateSqlCipherPassphrase(context)
        AppDatabase.build(context, passphrase)
    }
}

// ❌ Wrong: using user-provided password directly as the only secret
// Problem: user passwords are weak; at most derive a key via KDF and combine with device-held secret.
```

### Trade-offs

**Performance:**
- Roughly 10–15% overhead on read/write operations (encryption/decryption), depending on device and workload
- Database initialization may be slower by tens of milliseconds (key retrieval/generation, integrity checks)
- Mitigations: caching data, asynchronous work via Coroutines, query/index optimization

**Security:**
- With hardware-backed `Keystore` (TEE/StrongBox), keys are stored in an isolated environment and are non-extractable even with root access
- On devices without TEE keys may be software-backed only and more susceptible to extraction
- Vulnerability: if the device is compromised while the app is running, decrypted data can be accessed from memory or active process

### Best Practices

- **Use `Android Keystore`** — never store keys/passphrases in plaintext in `SharedPreferences`, files, or source code
- **Store passphrase indirectly** — generate a random passphrase for `SQLCipher`, encrypt it with a Keystore key, and store only the encrypted blob
- **Biometric authentication** — for highly sensitive data, use `setUserAuthenticationRequired(true)` (and optionally `setUserAuthenticationValidityDurationSeconds(...)`) to bind decryption to biometrics/lock screen
- **Test migrations** — when changing keys/passphrases you must correctly re-encrypt the DB (new passphrase, decrypt with old, encrypt with new)
- **StrongBox Keystore** — where available on API 28+ devices, use `setIsStrongBoxBacked(true)` for maximum key protection
- **Key rotation** — periodically rotate keys and passphrases with a well-defined, tested process


## Follow-ups

- How do you migrate from unencrypted to encrypted `Room` database without data loss?
- What happens to encrypted database when user changes device lock credentials?
- How do you implement biometric authentication for database access?
- What are the differences between `StrongBox` and regular `Keystore`?
- How do you handle database decryption on app startup?
- How to implement key rotation for `SQLCipher` database?

## References

- [[c-android-keystore]]
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
