---
id: 20251012-1227127
title: "Database Encryption Android / Шифрование базы данных Android"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [database, encryption, security, sqlcipher, room, keystore, difficulty/medium]
---
# Database Encryption in Android

**Difficulty**: Medium
**Source**: Amit Shekhar Android Interview Questions

# Question (EN)
> 

# Вопрос (RU)
> 

---

## Answer (EN)
# Question (EN)
How do you implement database encryption in Android? What are the best practices and available libraries?

## Answer (EN)
Database encryption is essential for protecting sensitive user data at rest. Android provides several options for encrypting databases, each with different trade-offs.

#### 1. **SQLCipher for Room**

SQLCipher is the most popular solution for Room database encryption. It provides transparent 256-bit AES encryption.

**Implementation:**

```kotlin
import net.sqlcipher.database.SupportFactory

@Database(entities = [User::class, Message::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun messageDao(): MessageDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getInstance(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: buildDatabase(context).also { INSTANCE = it }
            }
        }

        private fun buildDatabase(context: Context): AppDatabase {
            // Generate or retrieve encryption key
            val passphrase = getEncryptionKey(context)
            val factory = SupportFactory(passphrase)

            return Room.databaseBuilder(
                context.applicationContext,
                AppDatabase::class.java,
                "encrypted-database"
            )
                .openHelperFactory(factory)
                .build()
        }

        private fun getEncryptionKey(context: Context): ByteArray {
            // Use Android Keystore for secure key storage
            return KeystoreManager.getOrCreateDatabaseKey(context)
        }
    }
}
```

#### 2. **Secure Key Management with Android Keystore**

```kotlin
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import java.security.KeyStore
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey

object KeystoreManager {
    private const val ANDROID_KEYSTORE = "AndroidKeyStore"
    private const val DATABASE_KEY_ALIAS = "database_encryption_key"

    fun getOrCreateDatabaseKey(context: Context): ByteArray {
        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE).apply { load(null) }

        // Check if key already exists
        if (keyStore.containsAlias(DATABASE_KEY_ALIAS)) {
            return getExistingKey(keyStore)
        }

        // Generate new key
        return generateNewKey(keyStore)
    }

    private fun generateNewKey(keyStore: KeyStore): ByteArray {
        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            ANDROID_KEYSTORE
        )

        val keyGenParameterSpec = KeyGenParameterSpec.Builder(
            DATABASE_KEY_ALIAS,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)
            .setUserAuthenticationRequired(false)
            .build()

        keyGenerator.init(keyGenParameterSpec)
        val secretKey = keyGenerator.generateKey()

        return secretKey.encoded
    }

    private fun getExistingKey(keyStore: KeyStore): ByteArray {
        val secretKeyEntry = keyStore.getEntry(
            DATABASE_KEY_ALIAS,
            null
        ) as KeyStore.SecretKeyEntry

        return secretKeyEntry.secretKey.encoded
    }

    fun deleteKey() {
        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE).apply { load(null) }
        keyStore.deleteEntry(DATABASE_KEY_ALIAS)
    }
}
```

#### 3. **Alternative: Encrypted Shared Preferences for Key Storage**

```kotlin
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKeys

object SecureKeyStorage {
    private const val PREFS_NAME = "encrypted_prefs"
    private const val KEY_DATABASE_PASSPHRASE = "database_passphrase"

    fun getOrCreatePassphrase(context: Context): ByteArray {
        val masterKeyAlias = MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC)

        val sharedPreferences = EncryptedSharedPreferences.create(
            PREFS_NAME,
            masterKeyAlias,
            context,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )

        // Check if passphrase exists
        val existingPassphrase = sharedPreferences.getString(KEY_DATABASE_PASSPHRASE, null)
        if (existingPassphrase != null) {
            return existingPassphrase.toByteArray(Charsets.UTF_8)
        }

        // Generate new passphrase
        val newPassphrase = generateSecurePassphrase()
        sharedPreferences.edit()
            .putString(KEY_DATABASE_PASSPHRASE, newPassphrase.toString(Charsets.UTF_8))
            .apply()

        return newPassphrase
    }

    private fun generateSecurePassphrase(): ByteArray {
        val random = SecureRandom()
        return ByteArray(32).apply { random.nextBytes(this) }
    }
}
```

#### 4. **Migration from Unencrypted to Encrypted Database**

```kotlin
object DatabaseMigrationHelper {
    suspend fun migrateToEncrypted(
        context: Context,
        unencryptedDbName: String,
        encryptedDbName: String,
        passphrase: ByteArray
    ) = withContext(Dispatchers.IO) {
        try {
            val unencryptedDb = context.getDatabasePath(unencryptedDbName)
            val encryptedDb = context.getDatabasePath(encryptedDbName)

            if (!unencryptedDb.exists()) {
                throw IllegalStateException("Unencrypted database does not exist")
            }

            // Create encrypted database from unencrypted
            val database = SQLiteDatabase.openDatabase(
                unencryptedDb.absolutePath,
                "",
                null,
                SQLiteDatabase.OPEN_READWRITE
            )

            val passphraseString = String(passphrase, Charsets.UTF_8)
            database.rawExecSQL("ATTACH DATABASE '${encryptedDb.absolutePath}' AS encrypted KEY '$passphraseString'")
            database.rawExecSQL("SELECT sqlcipher_export('encrypted')")
            database.rawExecSQL("DETACH DATABASE encrypted")
            database.close()

            // Verify encrypted database
            val verifiedDb = SQLiteDatabase.openDatabase(
                encryptedDb.absolutePath,
                passphraseString,
                null,
                SQLiteDatabase.OPEN_READONLY
            )
            verifiedDb.close()

            // Delete unencrypted database
            unencryptedDb.delete()
        } catch (e: Exception) {
            Log.e("Migration", "Failed to migrate database", e)
            throw e
        }
    }
}
```

#### 5. **Performance Considerations**

```kotlin
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {

    companion object {
        fun create(context: Context): AppDatabase {
            val passphrase = KeystoreManager.getOrCreateDatabaseKey(context)
            val factory = SupportFactory(passphrase)

            return Room.databaseBuilder(
                context.applicationContext,
                AppDatabase::class.java,
                "app-database"
            )
                .openHelperFactory(factory)
                // Enable WAL mode for better concurrent access
                .setJournalMode(JournalMode.WRITE_AHEAD_LOGGING)
                // Set query executor for background operations
                .setQueryExecutor(Executors.newFixedThreadPool(4))
                .build()
        }
    }
}

// Benchmark encryption overhead
class DatabaseBenchmark {
    suspend fun benchmarkOperations(
        encryptedDb: AppDatabase,
        unencryptedDb: AppDatabase
    ) {
        val testData = generateTestUsers(10000)

        // Measure encrypted database
        val encryptedTime = measureTimeMillis {
            encryptedDb.userDao().insertAll(testData)
        }

        // Measure unencrypted database
        val unencryptedTime = measureTimeMillis {
            unencryptedDb.userDao().insertAll(testData)
        }

        Log.d("Benchmark", "Encrypted: ${encryptedTime}ms, Unencrypted: ${unencryptedTime}ms")
        Log.d("Benchmark", "Overhead: ${((encryptedTime - unencryptedTime).toFloat() / unencryptedTime * 100)}%")
    }
}
```

#### 6. **Handling Key Rotation**

```kotlin
object DatabaseKeyRotation {
    suspend fun rotateEncryptionKey(
        context: Context,
        database: AppDatabase,
        newPassphrase: ByteArray
    ) = withContext(Dispatchers.IO) {
        try {
            database.close()

            val dbPath = context.getDatabasePath("app-database")
            val db = SQLiteDatabase.openDatabase(
                dbPath.absolutePath,
                KeystoreManager.getOrCreateDatabaseKey(context),
                null,
                SQLiteDatabase.OPEN_READWRITE
            )

            // Change encryption key
            val newPassphraseString = String(newPassphrase, Charsets.UTF_8)
            db.rawExecSQL("PRAGMA rekey = '$newPassphraseString'")
            db.close()

            // Update stored key
            KeystoreManager.updateDatabaseKey(context, newPassphrase)
        } catch (e: Exception) {
            Log.e("KeyRotation", "Failed to rotate key", e)
            throw e
        }
    }
}
```

#### 7. **Backup and Restore Encrypted Database**

```kotlin
class EncryptedDatabaseBackup(
    private val context: Context,
    private val database: AppDatabase
) {
    suspend fun createBackup(backupFile: File) = withContext(Dispatchers.IO) {
        try {
            // Close database before backup
            database.close()

            val dbFile = context.getDatabasePath("app-database")
            dbFile.copyTo(backupFile, overwrite = true)

            // Reopen database
            AppDatabase.getInstance(context)
        } catch (e: Exception) {
            Log.e("Backup", "Failed to create backup", e)
            throw e
        }
    }

    suspend fun restoreBackup(backupFile: File) = withContext(Dispatchers.IO) {
        try {
            // Close database
            database.close()

            val dbFile = context.getDatabasePath("app-database")
            backupFile.copyTo(dbFile, overwrite = true)

            // Verify restored database can be opened
            val passphrase = KeystoreManager.getOrCreateDatabaseKey(context)
            val verifyDb = SQLiteDatabase.openDatabase(
                dbFile.absolutePath,
                String(passphrase, Charsets.UTF_8),
                null,
                SQLiteDatabase.OPEN_READONLY
            )
            verifyDb.close()

            // Reopen database
            AppDatabase.getInstance(context)
        } catch (e: Exception) {
            Log.e("Restore", "Failed to restore backup", e)
            throw e
        }
    }
}
```

#### 8. **Testing Encrypted Database**

```kotlin
@RunWith(AndroidJUnit4::class)
class EncryptedDatabaseTest {
    private lateinit var database: AppDatabase
    private lateinit var userDao: UserDao

    @Before
    fun setup() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val passphrase = "test_passphrase_32_characters!!".toByteArray()
        val factory = SupportFactory(passphrase)

        database = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java)
            .openHelperFactory(factory)
            .allowMainThreadQueries()
            .build()

        userDao = database.userDao()
    }

    @After
    fun teardown() {
        database.close()
    }

    @Test
    fun testEncryptedInsertAndRetrieve() = runBlocking {
        val user = User(id = 1, name = "John Doe", email = "john@example.com")
        userDao.insert(user)

        val retrieved = userDao.getUserById(1)
        assertEquals(user, retrieved)
    }

    @Test
    fun testWrongPassphraseFails() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val wrongPassphrase = "wrong_passphrase".toByteArray()
        val factory = SupportFactory(wrongPassphrase)

        // This should fail to open
        assertThrows<SQLiteException> {
            Room.databaseBuilder(context, AppDatabase::class.java, "test-db")
                .openHelperFactory(factory)
                .build()
                .userDao()
                .getAllUsers()
        }
    }
}
```

### Best Practices

**Security:**
- [ ] Use Android Keystore for key management
- [ ] Never hardcode encryption keys
- [ ] Implement key rotation strategy
- [ ] Use strong passphrases (256-bit)
- [ ] Clear sensitive data from memory
- [ ] Implement certificate pinning for sync

**Performance:**
- [ ] Enable WAL mode
- [ ] Use connection pooling
- [ ] Monitor encryption overhead
- [ ] Optimize query patterns
- [ ] Consider partial encryption (encrypt only sensitive tables)

**Implementation:**
- [ ] Test migration thoroughly
- [ ] Implement proper error handling
- [ ] Provide backup/restore functionality
- [ ] Document key management process
- [ ] Plan for key loss scenarios

**Compliance:**
- [ ] Understand regulatory requirements (GDPR, HIPAA)
- [ ] Implement data retention policies
- [ ] Provide data export functionality
- [ ] Document encryption methods

---



## Ответ (RU)
# Вопрос (RU)
Как реализовать шифрование базы данных в Android? Каковы лучшие практики и доступные библиотеки?

## Ответ (RU)
Шифрование базы данных необходимо для защиты конфиденциальных пользовательских данных в состоянии покоя. Android предоставляет несколько вариантов шифрования баз данных с различными компромиссами.

#### 1. **SQLCipher для Room**

SQLCipher - самое популярное решение для шифрования Room. Обеспечивает прозрачное 256-битное AES шифрование.

#### 2. **Безопасное управление ключами с Android Keystore**

Android Keystore System - наиболее безопасный способ хранения ключей шифрования. Ключи хранятся в аппаратном защищенном хранилище (если доступно).

#### 3. **Альтернатива: Encrypted Shared Preferences**

Для простых случаев можно использовать EncryptedSharedPreferences для хранения парольной фразы базы данных.

#### 4. **Миграция с незашифрованной БД**

Процесс миграции включает создание зашифрованной копии, верификацию и удаление исходной базы.

#### 5. **Производительность**

Шифрование добавляет накладные расходы (обычно 5-15%). Используйте WAL режим и оптимизируйте запросы.

#### 6. **Ротация ключей**

Регулярная ротация ключей повышает безопасность. SQLCipher поддерживает команду PRAGMA rekey.

#### 7. **Резервное копирование**

Зашифрованные базы данных остаются зашифрованными в резервных копиях. Храните ключи отдельно.

#### 8. **Тестирование**

Тестируйте миграцию, ротацию ключей и сценарии восстановления.

### Лучшие практики

**Безопасность:**
- Используйте Android Keystore
- Никогда не хардкодьте ключи
- Реализуйте стратегию ротации ключей
- Используйте сильные парольные фразы
- Очищайте чувствительные данные из памяти

**Производительность:**
- Включайте режим WAL
- Используйте пул соединений
- Мониторьте накладные расходы
- Оптимизируйте паттерны запросов

**Реализация:**
- Тщательно тестируйте миграцию
- Реализуйте обработку ошибок
- Предоставьте функции backup/restore
- Документируйте процесс управления ключами

**Соответствие требованиям:**
- Изучите регуляторные требования
- Реализуйте политики хранения данных
- Предоставьте экспорт данных

---

## Related Questions

### Prerequisites (Easier)
- [[q-sharedpreferences-commit-vs-apply--android--easy]] - Storage
- [[q-sharedpreferences-definition--android--easy]] - Storage

### Related (Medium)
- [[q-encrypted-file-storage--security--medium]] - Storage, Security
- [[q-android-security-practices-checklist--android--medium]] - Security
- [[q-save-markdown-structure-database--android--medium]] - Storage
- [[q-database-optimization-android--android--medium]] - Storage
- [[q-room-database-migrations--room--medium]] - Storage
