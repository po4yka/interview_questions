---
id: 20251020-200000
title: Database Encryption Android / Шифрование базы данных Android
aliases: [Database Encryption Android, Шифрование базы данных Android]
topic: android
subtopics:
  - permissions
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
  - q-android-keystore--security--hard
  - q-android-security-basics--android--medium
  - q-data-encryption-at-rest--android--medium
created: 2025-10-20
updated: 2025-10-20
tags: [android/permissions, android/room, database, difficulty/medium, encryption, keystore, room, security, sqlcipher]
source: https://developer.android.com/topic/security/data
source_note: Android Data Security documentation
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:52:11 pm
---

# Вопрос (RU)
> Как реализовать шифрование базы данных в Android? Какие лучшие практики и доступные библиотеки?

# Question (EN)
> How do you implement database encryption in Android? What are the best practices and available libraries?

## Ответ (RU)

Шифрование базы данных критически важно для защиты конфиденциальных пользовательских данных в покое. Android предоставляет несколько вариантов для шифрования баз данных с различными компромиссами.

### Теория: Принципы Шифрования Базы Данных

**Основные концепции:**
- **Шифрование на уровне базы данных** - защита данных на диске
- **Прозрачное шифрование** - автоматическое шифрование/расшифровка
- **Управление ключами** - безопасное хранение ключей шифрования
- **Производительность** - влияние шифрования на скорость операций
- **Совместимость** - интеграция с существующими решениями

**Принципы работы:**
- Данные шифруются перед записью на диск
- Ключи шифрования хранятся в Android Keystore
- Расшифровка происходит при чтении данных
- Автоматическое управление жизненным циклом ключей

### 1. SQLCipher Для Room

**Теоретические основы:**
SQLCipher предоставляет прозрачное 256-битное AES шифрование для SQLite баз данных. Он полностью совместим с Room и обеспечивает высокий уровень безопасности.

**Преимущества:**
- Прозрачное шифрование без изменения кода
- Высокий уровень безопасности (AES-256)
- Полная совместимость с Room
- Активная поддержка и обновления

**Компактная реализация:**
```kotlin
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        fun create(context: Context, passphrase: String): AppDatabase {
            val factory = SupportFactory(SQLiteDatabase.getBytes(passphrase.toCharArray()))
            return Room.databaseBuilder(context, AppDatabase::class.java, "encrypted.db")
                .openHelperFactory(factory)
                .build()
        }
    }
}
```

### 2. Управление Ключами

**Теоретические основы:**
Безопасное хранение ключей шифрования критически важно. Android Keystore предоставляет аппаратную защиту ключей и предотвращает их извлечение из устройства.

**Принципы безопасности:**
- Ключи никогда не покидают устройство
- Аппаратная защита на поддерживаемых устройствах
- Автоматическая очистка при компрометации устройства
- Защита от root-доступа

**Компактная реализация:**
```kotlin
class KeystoreManager {
    companion object {
        private const val KEY_ALIAS = "db_encryption_key"

        fun getDatabasePassphrase(context: Context): String {
            val keyStore = KeyStore.getInstance("AndroidKeyStore")
            keyStore.load(null)

            if (!keyStore.containsAlias(KEY_ALIAS)) {
                generateKey()
            }

            val key = keyStore.getKey(KEY_ALIAS, null) as SecretKey
            return Base64.encodeToString(key.encoded, Base64.DEFAULT)
        }

        private fun generateKey() {
            val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
            val keyGenParameterSpec = KeyGenParameterSpec.Builder(KEY_ALIAS,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .build()

            keyGenerator.init(keyGenParameterSpec)
            keyGenerator.generateKey()
        }
    }
}
```

### 3. Интеграция С Room

**Теоретические основы:**
Room предоставляет абстракцию над SQLite, а SQLCipher добавляет слой шифрования. Интеграция требует минимальных изменений в существующем коде.

**Принципы интеграции:**
- Использование SupportFactory для создания зашифрованной базы
- Автоматическое шифрование всех операций
- Прозрачная работа с DAO и Entity
- Совместимость с миграциями

**Компактная реализация:**
```kotlin
class DatabaseManager @Inject constructor(private val context: Context) {
    private val database: AppDatabase by lazy {
        val passphrase = KeystoreManager.getDatabasePassphrase(context)
        AppDatabase.create(context, passphrase)
    }

    fun saveUser(user: User) {
        database.userDao().insertUser(user)
    }

    fun getUser(id: Long): User? {
        return database.userDao().getUserById(id)
    }
}
```

### 4. Производительность И Оптимизация

**Теоретические основы:**
Шифрование добавляет накладные расходы на производительность. Понимание этих затрат критически важно для оптимизации приложения.

**Факторы производительности:**
- Накладные расходы на шифрование/расшифровку
- Размер базы данных влияет на время инициализации
- Частота операций записи/чтения
- Использование индексов и запросов

**Оптимизация:**
- Используйте асинхронные операции для больших данных
- Кэшируйте часто используемые данные
- Оптимизируйте запросы и индексы
- Рассмотрите частичное шифрование критических данных

### 5. Лучшие Практики

**Безопасность:**
- Всегда используйте Android Keystore для хранения ключей
- Регулярно ротируйте ключи шифрования
- Не храните ключи в коде приложения
- Используйте сильные пароли и алгоритмы

**Производительность:**
- Тестируйте производительность на реальных устройствах
- Оптимизируйте размер базы данных
- Используйте асинхронные операции
- Мониторьте использование памяти

**Совместимость:**
- Тестируйте на разных версиях Android
- Обеспечивайте миграцию данных при обновлениях
- Документируйте используемые алгоритмы шифрования
- Планируйте обратную совместимость

## Answer (EN)

Database encryption is critical for protecting sensitive user data at rest. Android provides several options for encrypting databases with different trade-offs.

### Theory: Database Encryption Principles

**Core Concepts:**
- **Database-level encryption** - protecting data on disk
- **Transparent encryption** - automatic encryption/decryption
- **Key management** - secure storage of encryption keys
- **Performance** - impact of encryption on operation speed
- **Compatibility** - integration with existing solutions

**Working Principles:**
- Data is encrypted before writing to disk
- Encryption keys are stored in Android Keystore
- Decryption occurs when reading data
- Automatic key lifecycle management

### 1. SQLCipher for Room

**Theoretical Foundations:**
SQLCipher provides transparent 256-bit AES encryption for SQLite databases. It's fully compatible with Room and provides high security level.

**Benefits:**
- Transparent encryption without code changes
- High security level (AES-256)
- Full compatibility with Room
- Active support and updates

**Compact Implementation:**
```kotlin
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        fun create(context: Context, passphrase: String): AppDatabase {
            val factory = SupportFactory(SQLiteDatabase.getBytes(passphrase.toCharArray()))
            return Room.databaseBuilder(context, AppDatabase::class.java, "encrypted.db")
                .openHelperFactory(factory)
                .build()
        }
    }
}
```

### 2. Key Management

**Theoretical Foundations:**
Secure storage of encryption keys is critical. Android Keystore provides hardware protection for keys and prevents their extraction from the device.

**Security Principles:**
- Keys never leave the device
- Hardware protection on supported devices
- Automatic cleanup on device compromise
- Protection against root access

**Compact Implementation:**
```kotlin
class KeystoreManager {
    companion object {
        private const val KEY_ALIAS = "db_encryption_key"

        fun getDatabasePassphrase(context: Context): String {
            val keyStore = KeyStore.getInstance("AndroidKeyStore")
            keyStore.load(null)

            if (!keyStore.containsAlias(KEY_ALIAS)) {
                generateKey()
            }

            val key = keyStore.getKey(KEY_ALIAS, null) as SecretKey
            return Base64.encodeToString(key.encoded, Base64.DEFAULT)
        }

        private fun generateKey() {
            val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
            val keyGenParameterSpec = KeyGenParameterSpec.Builder(KEY_ALIAS,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .build()

            keyGenerator.init(keyGenParameterSpec)
            keyGenerator.generateKey()
        }
    }
}
```

### 3. Room Integration

**Theoretical Foundations:**
Room provides abstraction over SQLite, while SQLCipher adds encryption layer. Integration requires minimal changes to existing code.

**Integration Principles:**
- Using SupportFactory to create encrypted database
- Automatic encryption of all operations
- Transparent work with DAO and Entity
- Compatibility with migrations

**Compact Implementation:**
```kotlin
class DatabaseManager @Inject constructor(private val context: Context) {
    private val database: AppDatabase by lazy {
        val passphrase = KeystoreManager.getDatabasePassphrase(context)
        AppDatabase.create(context, passphrase)
    }

    fun saveUser(user: User) {
        database.userDao().insertUser(user)
    }

    fun getUser(id: Long): User? {
        return database.userDao().getUserById(id)
    }
}
```

### 4. Performance and Optimization

**Theoretical Foundations:**
Encryption adds performance overhead. Understanding these costs is critical for application optimization.

**Performance Factors:**
- Encryption/decryption overhead
- Database size affects initialization time
- Frequency of write/read operations
- Use of indexes and queries

**Optimization:**
- Use asynchronous operations for large data
- Cache frequently used data
- Optimize queries and indexes
- Consider partial encryption of critical data

### 5. Best Practices

**Security:**
- Always use Android Keystore for key storage
- Regularly rotate encryption keys
- Never store keys in application code
- Use strong passwords and algorithms

**Performance:**
- Test performance on real devices
- Optimize database size
- Use asynchronous operations
- Monitor memory usage

**Compatibility:**
- Test on different Android versions
- Ensure data migration on updates
- Document used encryption algorithms
- Plan backward compatibility

**See also:** [[c-encryption]], c-sqlite


## Follow-ups

- How do you handle database migration with encryption?
- What are the performance implications of different encryption algorithms?
- How do you implement key rotation for encrypted databases?

## Related Questions

### Related (Same Level)
- [[q-data-encryption-at-rest--android--medium]]
