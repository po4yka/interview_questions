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

**Шифрование в покое** защищает данные на устройстве от несанкционированного доступа даже при физическом компрометировании. Android предлагает три типичных решения: `EncryptedSharedPreferences` (токены, настройки), `SQLCipher` (базы данных), `EncryptedFile` (файлы). `EncryptedSharedPreferences` и `EncryptedFile` используют `Android Keystore` для безопасного хранения ключей (через `MasterKey`/`EncryptedFile` API). Для `SQLCipher` ключ (пароль) вы предоставляете сами, и рекомендуется защищать его с помощью `Android Keystore`.

### Ключевые Принципы

**Архитектура:**
- Данные шифруются (например, `AES-256-GCM`) перед записью на диск (аутентифицированное шифрование)
- Ключи или ключи-обёртки хранятся в `Android Keystore` (при наличии — аппаратная защита через StrongBox на поддерживаемых устройствах)
- Автоматическое управление жизненным циклом ключей через `MasterKey` API для Jetpack Security компонентов
- Двухуровневая защита (envelope encryption): мастер-ключ в Keystore шифрует (оборачивает) рабочие ключи/пароли, которыми шифруются данные

| Подход | Использование | Производительность | Сложность |
|--------|--------------|-------------------|-----------|
| `EncryptedSharedPreferences` | Токены, настройки | Быстро (небольшой overhead, обычно единицы миллисекунд) | Простая |
| `SQLCipher` | Базы данных | Умеренно (заметный overhead, зависит от нагрузки/устройства) | Средняя |
| `EncryptedFile` | Медиа, документы | Медленнее (зависит от размера файлов) | Средняя |

(Оценки производительности приблизительные и зависят от устройства, размера данных и шаблонов доступа.)

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

**Важно:** `EncryptedSharedPreferences` шифрует и ключи (`AES256_SIV` — детерминированное шифрование), и значения (`AES256_GCM` — аутентифицированное шифрование). Для критичных данных при необходимости гарантировать немедленную запись используйте `commit()` вместо `apply()` (но с учётом возможного влияния на производительность).

### 2. SQLCipher Для Room

Рекомендуемый паттерн — не хранить пароль для SQLCipher в открытом виде, а сгенерировать случайный passphrase и зашифровать его с помощью ключа из `Android Keystore` (envelope encryption).

Упрощённый пример (иллюстративный, без обработки ошибок и миграций):

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
            val encryptedPrefs = context.getSharedPreferences("sqlcipher_keys", Context.MODE_PRIVATE)
            val existing = encryptedPrefs.getString("db_passphrase", null)
            if (existing != null) return existing

            // Сгенерировать криптостойкий случайный passphrase
            val passphraseBytes = ByteArray(32).also {
                SecureRandom().nextBytes(it)
            }
            val passphrase = Base64.encodeToString(passphraseBytes, Base64.NO_WRAP)

            // При желании: зашифровать passphrase с помощью ключа из Android Keystore
            // Здесь опущено для краткости; важно, что passphrase не хардкодится

            encryptedPrefs.edit().putString("db_passphrase", passphrase).commit()
            return passphrase
        }
    }
}
```

Ключевые моменты:
- Не используйте ключи, сгенерированные в `AndroidKeyStore`, напрямую как passphrase `SQLCipher` (такие ключи обычно неэкспортируемые, `secretKey.encoded == null`).
- Вместо этого: мастер-ключ в Keystore + сгенерированный случайный passphrase для SQLCipher, который хранится только в зашифрованном виде (envelope encryption).

### 3. Управление Ключами

**Критичные аспекты:**
- Используйте `StrongBox Keymaster` (API 28+) для аппаратной изоляции там, где он доступен: `setIsStrongBoxBacked(true)` при конфигурации ключа; необходимо обрабатывать случаи, когда устройство не поддерживает StrongBox.
- Привязка к биометрии / аутентификации пользователя: `setUserAuthenticationRequired(true)` и `setUserAuthenticationValidityDurationSeconds(...)` — ключ доступен только после успешной аутентификации пользователя.
- Ротация ключей: при компрометации или по политике безопасности создавайте новый мастер-ключ, расшифровывайте данные старым ключом и перешифровывайте новым.

```kotlin
// ❌ НЕПРАВИЛЬНО: жёстко заданный ключ в коде — легко извлечь из APK
val hardcodedKey = "my_secret_key_123"

// ✅ ПРАВИЛЬНО: ключ в Keystore, опционально с требованием аутентификации
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    // requires user authentication every 30 seconds for key use (если политика подходит)
    .setUserAuthenticationRequired(true, 30)
    .build()
```

### Производительность

**Приблизительно (будет отличаться в зависимости от устройства и сценария):**
- `EncryptedSharedPreferences`: обычно +1-2ms на операцию чтения/записи по сравнению с обычными `SharedPreferences`.
- `SQLCipher`: дополнительный overhead при чтении/записи/индексации; для многих приложений укладывается в +десятки процентов, но требует профилирования.
- `EncryptedFile`: стоимость зависит в основном от размера файла и I/O; для файлов ~1MB задержка может составлять десятки миллисекунд.

**Оптимизации:**
- Минимизируйте количество операций шифрования/дешифрования — кешируйте часто используемые данные (с осознанным управлением сроком жизни и очисткой).
- Используйте батчинг и транзакции с `SQLCipher` для снижения относительного overhead.
- Кешируйте расшифрованные данные в памяти осторожно (возможность утечек через дампы памяти, бэкапы, логирование); очищайте чувствительный кеш при выходе из приложения и при блокировке.

## Answer (EN)

**Encryption at rest** protects data on the device from unauthorized access even when it is physically compromised. Android offers three typical solutions: `EncryptedSharedPreferences` (tokens, settings), `SQLCipher` (databases), `EncryptedFile` (files). `EncryptedSharedPreferences` and `EncryptedFile` use the `Android Keystore` for key storage via the Jetpack Security APIs. For `SQLCipher`, you supply the key (passphrase) yourself and should protect it using the `Android Keystore`.

### Core Principles

**Architecture:**
- Data is encrypted (e.g., `AES-256-GCM`) before being written to disk (authenticated encryption)
- Keys or wrapping keys are stored in `Android Keystore` (hardware-backed with StrongBox on supported devices)
- Automatic key lifecycle management via `MasterKey` API for Jetpack Security components
- Two-tier protection (envelope encryption): a Keystore master key encrypts (wraps) working keys/passwords that encrypt the data

| Approach | Use Case | Performance | Complexity |
|----------|----------|-------------|------------|
| `EncryptedSharedPreferences` | Tokens, settings | Fast (small overhead, usually a few ms) | Simple |
| `SQLCipher` | Databases | Moderate (noticeable overhead, load/device-dependent) | Medium |
| `EncryptedFile` | Media, documents | Slower (file-size dependent) | Medium |

(Performance numbers are approximate and depend on device, data size, and access patterns.)

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

**Important:** `EncryptedSharedPreferences` encrypts both keys (`AES256_SIV` — deterministic) and values (`AES256_GCM` — authenticated). For critical data where you need immediate persistence guarantees, prefer `commit()` over `apply()`, while being aware of its potential performance impact.

### 2. SQLCipher for Room

Recommended pattern: do not store the SQLCipher passphrase in plaintext or hardcoded. Instead, generate a strong random passphrase and protect it via a key stored in the `Android Keystore` (envelope encryption).

Simplified example (illustrative; omits error handling and migrations):

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
            val prefs = context.getSharedPreferences("sqlcipher_keys", Context.MODE_PRIVATE)
            val existing = prefs.getString("db_passphrase", null)
            if (existing != null) return existing

            // Generate cryptographically strong random passphrase
            val passphraseBytes = ByteArray(32).also {
                SecureRandom().nextBytes(it)
            }
            val passphrase = Base64.encodeToString(passphraseBytes, Base64.NO_WRAP)

            // Optionally: encrypt this passphrase with an Android Keystore key before storing.
            // Kept simple here; key must not be hardcoded.

            prefs.edit().putString("db_passphrase", passphrase).commit()
            return passphrase
        }
    }
}
```

Key points:
- Do not use `AndroidKeyStore`-generated AES keys directly as the SQLCipher passphrase (they are typically non-exportable; `secretKey.encoded` is null).
- Instead, use a Keystore master key to encrypt (wrap) a randomly generated passphrase that SQLCipher uses.

### 3. Key Management

**Critical aspects:**
- Use `StrongBox Keymaster` (API 28+) for hardware isolation where supported: call `setIsStrongBoxBacked(true)` when configuring the key and gracefully handle devices that do not support StrongBox.
- Biometric / user-auth binding: `setUserAuthenticationRequired(true)` with `setUserAuthenticationValidityDurationSeconds(...)` — key usage requires successful user authentication according to your policy.
- Key rotation: upon suspected compromise or per policy, create a new master key, decrypt data with the old key, and re-encrypt with the new key.

```kotlin
// ❌ WRONG: hardcoded key — easily extractable from APK
val hardcodedKey = "my_secret_key_123"

// ✅ CORRECT: Keystore-backed key, optionally requiring authentication
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    // requires authentication every 30 seconds for key usage (if appropriate for your UX/policy)
    .setUserAuthenticationRequired(true, 30)
    .build()
```

### Performance

**Approximate (device- and workload-dependent):**
- `EncryptedSharedPreferences`: typically +1–2 ms per read/write vs plain `SharedPreferences`.
- `SQLCipher`: overhead on queries and writes; often within tens of percent vs plain SQLite but must be profiled for your access patterns.
- `EncryptedFile`: overhead scales with file size and I/O; a ~1MB file may add tens of ms.

**Optimizations:**
- Minimize encryption/decryption operations — cache frequently used values with careful lifecycle and invalidation.
- Use batching and transactions with `SQLCipher` to amortize overhead across multiple operations.
- Cache decrypted data in memory cautiously (risk of leaks via memory dumps, logs, etc.); clear sensitive caches on app exit/lock.

## Follow-ups

- How to migrate from plain to encrypted database without data loss?
- What happens to encrypted data when the user changes device PIN/pattern?
- How to implement key rotation for a `SQLCipher` database?
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
