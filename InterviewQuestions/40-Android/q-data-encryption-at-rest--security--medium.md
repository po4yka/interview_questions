---
id: 20251020-200000
title: Data Encryption At Rest / Шифрование данных в покое
aliases:
  - Data Encryption At Rest
  - Шифрование данных в покое
topic: android
subtopics:
  - security
  - files-media
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - q-android-security-basics--android--medium
  - q-android-keystore--security--hard
  - q-android-biometric-authentication--security--medium
created: 2025-10-20
updated: 2025-10-20
tags:
  - android/security
  - android/files-media
  - encryption
  - security
  - database
  - shared-preferences
  - sqlcipher
  - difficulty/medium
source: https://developer.android.com/guide/topics/security/encryption
source_note: Android Encryption documentation
---
# Вопрос (RU)
> Как реализовать шифрование данных в покое с помощью EncryptedSharedPreferences и SQLCipher для Room? Сравните подходы, влияние на производительность и стратегии управления ключами.

# Question (EN)
> Implement data encryption at rest using EncryptedSharedPreferences and SQLCipher for Room. Compare approaches, performance impact, and key management strategies.

## Ответ (RU)

**Шифрование в покое** защищает конфиденциальные данные, хранящиеся на устройстве, от несанкционированного доступа. Android предоставляет несколько вариантов шифрования: EncryptedSharedPreferences для простого хранения ключ-значение и SQLCipher для шифрования базы данных.

### Теория: Принципы шифрования в покое

**Основные концепции:**
- **Защита данных** - предотвращение несанкционированного доступа к хранимым данным
- **Шифрование на уровне приложения** - дополнительная защита поверх системного шифрования
- **Управление ключами** - безопасное хранение и использование ключей шифрования
- **Производительность** - баланс между безопасностью и производительностью
- **Совместимость** - поддержка различных типов данных и API

**Принципы работы:**
- Данные шифруются перед записью на диск
- Ключи шифрования хранятся в Android Keystore
- Расшифровка происходит при чтении данных
- Автоматическое управление жизненным циклом ключей

### Сравнение подходов к шифрованию

| Функция | EncryptedSharedPreferences | SQLCipher | Шифрование файлов |
|---------|---------------------------|-----------|-------------------|
| Использование | Настройки, токены | База данных | Большие файлы |
| Производительность | Быстро | Умеренная нагрузка | Зависит от размера |
| Сложность | Простая | Умеренная | Сложная |
| Управление ключами | Автоматическое (Keystore) | Ручное | Ручное |
| Библиотека | Jetpack Security | SQLCipher for Android | EncryptedFile |
| Шифрование | AES-256-GCM | AES-256 | AES-256-GCM |

### 1. EncryptedSharedPreferences

**Настройка EncryptedSharedPreferences:**
```kotlin
class SecurePreferencesManager(private val context: Context) {
    private val masterKey: MasterKey by lazy {
        MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
    }

    private val sharedPreferences: SharedPreferences by lazy {
        EncryptedSharedPreferences.create(
            context,
            "secure_prefs",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }

    fun saveSecureData(key: String, value: String) {
        sharedPreferences.edit()
            .putString(key, value)
            .apply()
    }

    fun getSecureData(key: String): String? {
        return sharedPreferences.getString(key, null)
    }
}
```

**Использование:**
```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var securePrefs: SecurePreferencesManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        securePrefs = SecurePreferencesManager(this)

        // Сохранение зашифрованных данных
        securePrefs.saveSecureData("auth_token", "secret_token_123")

        // Получение зашифрованных данных
        val token = securePrefs.getSecureData("auth_token")
    }
}
```

### 2. SQLCipher для Room

**Настройка SQLCipher с Room:**
```kotlin
@Database(
    entities = [User::class],
    version = 1
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        fun create(context: Context, passphrase: String): AppDatabase {
            val factory = SupportFactory(
                SQLiteDatabase.getBytes(passphrase.toCharArray())
            )

            return Room.databaseBuilder(
                context,
                AppDatabase::class.java,
                "encrypted_database.db"
            )
            .openHelperFactory(factory)
            .build()
        }
    }
}
```

**Использование зашифрованной базы данных:**
```kotlin
class DatabaseManager(private val context: Context) {
    private val database: AppDatabase by lazy {
        val passphrase = getDatabasePassphrase()
        AppDatabase.create(context, passphrase)
    }

    private fun getDatabasePassphrase(): String {
        // Получение пароля из Android Keystore
        return KeystoreManager.getDatabasePassphrase(context)
    }

    fun saveUser(user: User) {
        database.userDao().insertUser(user)
    }

    fun getUser(id: Long): User? {
        return database.userDao().getUserById(id)
    }
}
```

### 3. Управление ключами

**Android Keystore для безопасного хранения ключей:**
```kotlin
class KeystoreManager {
    companion object {
        private const val KEY_ALIAS = "app_encryption_key"
        private const val ANDROID_KEYSTORE = "AndroidKeyStore"

        fun generateKey(context: Context): SecretKey {
            val keyGenerator = KeyGenerator.getInstance(
                KeyProperties.KEY_ALGORITHM_AES,
                ANDROID_KEYSTORE
            )

            val keyGenParameterSpec = KeyGenParameterSpec.Builder(
                KEY_ALIAS,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
            )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .build()

            keyGenerator.init(keyGenParameterSpec)
            return keyGenerator.generateKey()
        }

        fun getKey(): SecretKey? {
            val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE)
            keyStore.load(null)
            return keyStore.getKey(KEY_ALIAS, null) as? SecretKey
        }
    }
}
```

### 4. Производительность и оптимизация

**Влияние на производительность:**
- **EncryptedSharedPreferences**: Минимальная нагрузка, подходит для небольших данных
- **SQLCipher**: Умеренная нагрузка, подходит для средних объемов данных
- **File Encryption**: Высокая нагрузка для больших файлов

**Оптимизация:**
- Используйте асинхронные операции для больших данных
- Кэшируйте расшифрованные данные в памяти
- Избегайте частого шифрования/расшифровки

### 5. Лучшие практики

**Безопасность:**
- Всегда используйте Android Keystore для хранения ключей
- Регулярно ротируйте ключи шифрования
- Не храните ключи в коде приложения

**Производительность:**
- Выбирайте подходящий метод шифрования для типа данных
- Используйте асинхронные операции
- Оптимизируйте частоту операций шифрования

**Совместимость:**
- Тестируйте на разных версиях Android
- Обеспечивайте миграцию данных при обновлениях
- Документируйте используемые алгоритмы шифрования

## Answer (EN)

**Encryption at rest** protects sensitive data stored on the device from unauthorized access. Android provides multiple encryption options: EncryptedSharedPreferences for simple key-value storage and SQLCipher for database encryption.

### Theory: Encryption at Rest Principles

**Core Concepts:**
- **Data Protection** - preventing unauthorized access to stored data
- **Application-level Encryption** - additional protection on top of system encryption
- **Key Management** - secure storage and use of encryption keys
- **Performance** - balance between security and performance
- **Compatibility** - support for different data types and APIs

**Working Principles:**
- Data is encrypted before writing to disk
- Encryption keys are stored in Android Keystore
- Decryption occurs when reading data
- Automatic key lifecycle management

### Encryption Approaches Comparison

| Feature | EncryptedSharedPreferences | SQLCipher | File Encryption |
|---------|---------------------------|-----------|-----------------|
| Use Case | Settings, tokens | Database | Large files |
| Performance | Fast | Moderate overhead | Depends on size |
| Complexity | Simple | Moderate | Complex |
| Key Management | Automatic (Keystore) | Manual | Manual |
| Library | Jetpack Security | SQLCipher for Android | EncryptedFile |
| Encryption | AES-256-GCM | AES-256 | AES-256-GCM |

### 1. EncryptedSharedPreferences

**EncryptedSharedPreferences Setup:**
```kotlin
class SecurePreferencesManager(private val context: Context) {
    private val masterKey: MasterKey by lazy {
        MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
    }

    private val sharedPreferences: SharedPreferences by lazy {
        EncryptedSharedPreferences.create(
            context,
            "secure_prefs",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }

    fun saveSecureData(key: String, value: String) {
        sharedPreferences.edit()
            .putString(key, value)
            .apply()
    }

    fun getSecureData(key: String): String? {
        return sharedPreferences.getString(key, null)
    }
}
```

**Usage:**
```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var securePrefs: SecurePreferencesManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        securePrefs = SecurePreferencesManager(this)

        // Save encrypted data
        securePrefs.saveSecureData("auth_token", "secret_token_123")

        // Get encrypted data
        val token = securePrefs.getSecureData("auth_token")
    }
}
```

### 2. SQLCipher for Room

**SQLCipher Setup with Room:**
```kotlin
@Database(
    entities = [User::class],
    version = 1
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        fun create(context: Context, passphrase: String): AppDatabase {
            val factory = SupportFactory(
                SQLiteDatabase.getBytes(passphrase.toCharArray())
            )

            return Room.databaseBuilder(
                context,
                AppDatabase::class.java,
                "encrypted_database.db"
            )
            .openHelperFactory(factory)
            .build()
        }
    }
}
```

**Using Encrypted Database:**
```kotlin
class DatabaseManager(private val context: Context) {
    private val database: AppDatabase by lazy {
        val passphrase = getDatabasePassphrase()
        AppDatabase.create(context, passphrase)
    }

    private fun getDatabasePassphrase(): String {
        // Get passphrase from Android Keystore
        return KeystoreManager.getDatabasePassphrase(context)
    }

    fun saveUser(user: User) {
        database.userDao().insertUser(user)
    }

    fun getUser(id: Long): User? {
        return database.userDao().getUserById(id)
    }
}
```

### 3. Key Management

**Android Keystore for Secure Key Storage:**
```kotlin
class KeystoreManager {
    companion object {
        private const val KEY_ALIAS = "app_encryption_key"
        private const val ANDROID_KEYSTORE = "AndroidKeyStore"

        fun generateKey(context: Context): SecretKey {
            val keyGenerator = KeyGenerator.getInstance(
                KeyProperties.KEY_ALGORITHM_AES,
                ANDROID_KEYSTORE
            )

            val keyGenParameterSpec = KeyGenParameterSpec.Builder(
                KEY_ALIAS,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
            )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .build()

            keyGenerator.init(keyGenParameterSpec)
            return keyGenerator.generateKey()
        }

        fun getKey(): SecretKey? {
            val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE)
            keyStore.load(null)
            return keyStore.getKey(KEY_ALIAS, null) as? SecretKey
        }
    }
}
```

### 4. Performance and Optimization

**Performance Impact:**
- **EncryptedSharedPreferences**: Minimal overhead, suitable for small data
- **SQLCipher**: Moderate overhead, suitable for medium data volumes
- **File Encryption**: High overhead for large files

**Optimization:**
- Use asynchronous operations for large data
- Cache decrypted data in memory
- Avoid frequent encryption/decryption

### 5. Best Practices

**Security:**
- Always use Android Keystore for key storage
- Regularly rotate encryption keys
- Never store keys in application code

**Performance:**
- Choose appropriate encryption method for data type
- Use asynchronous operations
- Optimize encryption frequency

**Compatibility:**
- Test on different Android versions
- Ensure data migration on updates
- Document used encryption algorithms

## Follow-ups

- How do you handle key rotation in encrypted databases?
- What are the performance implications of different encryption algorithms?
- How do you implement encryption for large files?
