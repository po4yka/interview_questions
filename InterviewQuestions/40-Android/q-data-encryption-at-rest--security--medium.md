---
topic: security
tags:
  - security
  - encryption
  - database
  - shared-preferences
  - sqlcipher
  - performance
  - key-management
  - difficulty/medium
difficulty: medium
status: draft
---

# Data Encryption at Rest / Шифрование данных в покое

**English**: Implement data encryption at rest using EncryptedSharedPreferences and SQLCipher for Room. Compare approaches, performance impact, and key management strategies.

## Answer (EN)
**Encryption at rest** protects sensitive data stored on the device from unauthorized access. Android provides multiple encryption options: EncryptedSharedPreferences for simple key-value storage and SQLCipher for database encryption. Proper implementation requires understanding performance trade-offs and secure key management.

### Encryption Options Comparison

| Feature | EncryptedSharedPreferences | SQLCipher | File Encryption |
|---------|---------------------------|-----------|-----------------|
| Use Case | Settings, tokens | Database | Large files |
| Performance | Fast | Moderate overhead | Depends on size |
| Complexity | Simple | Moderate | Complex |
| Key Management | Automatic (Keystore) | Manual | Manual |
| Library | Jetpack Security | SQLCipher for Android | EncryptedFile |
| Encryption | AES-256-GCM | AES-256 | AES-256-GCM |

### Complete Implementation

#### 1. EncryptedSharedPreferences Setup

```kotlin
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import android.content.Context
import android.content.SharedPreferences

/**
 * EncryptedSharedPreferences implementation
 */
class SecurePreferencesManager(private val context: Context) {

    companion object {
        private const val PREFS_FILE_NAME = "secure_preferences"
    }

    // Create MasterKey for encryption
    private val masterKey: MasterKey by lazy {
        MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .setUserAuthenticationRequired(false) // Set true for biometric-protected keys
            .setRequestStrongBoxBacked(true) // Use StrongBox if available
            .build()
    }

    // Create EncryptedSharedPreferences
    private val encryptedPrefs: SharedPreferences by lazy {
        EncryptedSharedPreferences.create(
            context,
            PREFS_FILE_NAME,
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }

    /**
     * Store encrypted string
     */
    fun putString(key: String, value: String) {
        encryptedPrefs.edit()
            .putString(key, value)
            .apply()
    }

    /**
     * Retrieve encrypted string
     */
    fun getString(key: String, defaultValue: String? = null): String? {
        return encryptedPrefs.getString(key, defaultValue)
    }

    /**
     * Store encrypted int
     */
    fun putInt(key: String, value: Int) {
        encryptedPrefs.edit()
            .putInt(key, value)
            .apply()
    }

    /**
     * Retrieve encrypted int
     */
    fun getInt(key: String, defaultValue: Int = 0): Int {
        return encryptedPrefs.getInt(key, defaultValue)
    }

    /**
     * Store encrypted boolean
     */
    fun putBoolean(key: String, value: Boolean) {
        encryptedPrefs.edit()
            .putBoolean(key, value)
            .apply()
    }

    /**
     * Retrieve encrypted boolean
     */
    fun getBoolean(key: String, defaultValue: Boolean = false): Boolean {
        return encryptedPrefs.getBoolean(key, defaultValue)
    }

    /**
     * Store encrypted long
     */
    fun putLong(key: String, value: Long) {
        encryptedPrefs.edit()
            .putLong(key, value)
            .apply()
    }

    /**
     * Retrieve encrypted long
     */
    fun getLong(key: String, defaultValue: Long = 0L): Long {
        return encryptedPrefs.getLong(key, defaultValue)
    }

    /**
     * Store encrypted float
     */
    fun putFloat(key: String, value: Float) {
        encryptedPrefs.edit()
            .putFloat(key, value)
            .apply()
    }

    /**
     * Retrieve encrypted float
     */
    fun getFloat(key: String, defaultValue: Float = 0f): Float {
        return encryptedPrefs.getFloat(key, defaultValue)
    }

    /**
     * Store encrypted string set
     */
    fun putStringSet(key: String, values: Set<String>) {
        encryptedPrefs.edit()
            .putStringSet(key, values)
            .apply()
    }

    /**
     * Retrieve encrypted string set
     */
    fun getStringSet(key: String, defaultValue: Set<String>? = null): Set<String>? {
        return encryptedPrefs.getStringSet(key, defaultValue)
    }

    /**
     * Remove key
     */
    fun remove(key: String) {
        encryptedPrefs.edit()
            .remove(key)
            .apply()
    }

    /**
     * Clear all data
     */
    fun clear() {
        encryptedPrefs.edit()
            .clear()
            .apply()
    }

    /**
     * Check if key exists
     */
    fun contains(key: String): Boolean {
        return encryptedPrefs.contains(key)
    }

    /**
     * Get all keys (decrypted)
     */
    fun getAllKeys(): Set<String> {
        return encryptedPrefs.all.keys
    }

    /**
     * Backup to JSON (for migration)
     */
    fun exportToJson(): String {
        val data = encryptedPrefs.all.mapValues { it.value.toString() }
        return Json.encodeToString(data)
    }

    /**
     * Restore from JSON
     */
    fun importFromJson(json: String) {
        val data = Json.decodeFromString<Map<String, String>>(json)
        val editor = encryptedPrefs.edit()

        data.forEach { (key, value) ->
            editor.putString(key, value)
        }

        editor.apply()
    }
}
```

#### 2. SQLCipher Integration with Room

```kotlin
import net.sqlcipher.database.SQLiteDatabase
import net.sqlcipher.database.SupportFactory
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

/**
 * SQLCipher-encrypted Room database
 */
@Database(entities = [User::class, Message::class], version = 1)
abstract class EncryptedDatabase : RoomDatabase() {

    abstract fun userDao(): UserDao
    abstract fun messageDao(): MessageDao

    companion object {
        @Volatile
        private var INSTANCE: EncryptedDatabase? = null

        fun getInstance(context: Context): EncryptedDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = buildDatabase(context)
                INSTANCE = instance
                instance
            }
        }

        private fun buildDatabase(context: Context): EncryptedDatabase {
            // Initialize SQLCipher
            SQLiteDatabase.loadLibs(context)

            // Get or create database passphrase
            val passphrase = getDatabasePassphrase(context)

            // Create SQLCipher support factory
            val factory = SupportFactory(passphrase)

            return Room.databaseBuilder(
                context.applicationContext,
                EncryptedDatabase::class.java,
                "encrypted_database.db"
            )
                .openHelperFactory(factory)
                .fallbackToDestructiveMigration()
                .build()
        }

        /**
         * Get database passphrase from Android Keystore
         */
        private fun getDatabasePassphrase(context: Context): ByteArray {
            val keyManager = DatabaseKeyManager(context)
            return keyManager.getDatabaseKey()
        }

        /**
         * Change database passphrase
         */
        fun changePassphrase(
            context: Context,
            database: EncryptedDatabase,
            newPassphrase: ByteArray
        ) {
            val dbFile = context.getDatabasePath("encrypted_database.db")

            database.close()

            SQLiteDatabase.openOrCreateDatabase(
                dbFile.absolutePath,
                getDatabasePassphrase(context),
                null
            ).use { db ->
                db.rawExecSQL("PRAGMA rekey = '${String(newPassphrase)}'")
            }
        }
    }
}

/**
 * Manage database encryption key
 */
class DatabaseKeyManager(private val context: Context) {

    companion object {
        private const val KEY_ALIAS = "database_key"
        private const val PREFS_NAME = "db_key_prefs"
        private const val KEY_ENCRYPTED_KEY = "encrypted_db_key"
    }

    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val encryptedPrefs = EncryptedSharedPreferences.create(
        context,
        PREFS_NAME,
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    /**
     * Get or create database key
     */
    fun getDatabaseKey(): ByteArray {
        val existingKey = encryptedPrefs.getString(KEY_ENCRYPTED_KEY, null)

        return if (existingKey != null) {
            Base64.decode(existingKey, Base64.NO_WRAP)
        } else {
            generateAndStoreKey()
        }
    }

    /**
     * Generate new database key
     */
    private fun generateAndStoreKey(): ByteArray {
        // Generate random 256-bit key
        val key = ByteArray(32)
        SecureRandom().nextBytes(key)

        // Store encrypted key
        val encodedKey = Base64.encodeToString(key, Base64.NO_WRAP)
        encryptedPrefs.edit()
            .putString(KEY_ENCRYPTED_KEY, encodedKey)
            .apply()

        return key
    }

    /**
     * Rotate database key
     */
    fun rotateKey(): ByteArray {
        encryptedPrefs.edit().remove(KEY_ENCRYPTED_KEY).apply()
        return generateAndStoreKey()
    }

    /**
     * Derive key from passphrase using PBKDF2
     */
    fun deriveKeyFromPassphrase(passphrase: String): ByteArray {
        val salt = getSalt()
        val iterations = 10000
        val keyLength = 256

        val factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
        val spec = PBEKeySpec(
            passphrase.toCharArray(),
            salt,
            iterations,
            keyLength
        )

        return factory.generateSecret(spec).encoded
    }

    private fun getSalt(): ByteArray {
        val existingSalt = encryptedPrefs.getString("salt", null)

        return if (existingSalt != null) {
            Base64.decode(existingSalt, Base64.NO_WRAP)
        } else {
            val salt = ByteArray(16)
            SecureRandom().nextBytes(salt)

            encryptedPrefs.edit()
                .putString("salt", Base64.encodeToString(salt, Base64.NO_WRAP))
                .apply()

            salt
        }
    }
}
```

#### 3. Entity and DAO Example

```kotlin
import androidx.room.*

@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val username: String,
    val email: String,
    val phoneNumber: String,
    val createdAt: Long = System.currentTimeMillis()
)

@Dao
interface UserDao {

    @Query("SELECT * FROM users")
    suspend fun getAllUsers(): List<User>

    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserById(userId: Long): User?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User): Long

    @Update
    suspend fun updateUser(user: User)

    @Delete
    suspend fun deleteUser(user: User)

    @Query("DELETE FROM users")
    suspend fun deleteAllUsers()
}

@Entity(tableName = "messages")
data class Message(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val userId: Long,
    val content: String,
    val timestamp: Long = System.currentTimeMillis()
)

@Dao
interface MessageDao {

    @Query("SELECT * FROM messages WHERE userId = :userId ORDER BY timestamp DESC")
    suspend fun getMessagesForUser(userId: Long): List<Message>

    @Insert
    suspend fun insertMessage(message: Message): Long

    @Query("DELETE FROM messages WHERE userId = :userId")
    suspend fun deleteMessagesForUser(userId: Long)
}
```

### Performance Comparison and Benchmarks

```kotlin
import kotlin.system.measureTimeMillis

/**
 * Benchmark encryption overhead
 */
class EncryptionBenchmark(
    private val context: Context,
    private val securePrefs: SecurePreferencesManager,
    private val encryptedDb: EncryptedDatabase
) {

    data class BenchmarkResult(
        val operation: String,
        val recordCount: Int,
        val encryptedTimeMs: Long,
        val unencryptedTimeMs: Long,
        val overheadPercent: Double
    ) {
        override fun toString(): String {
            return """
                $operation ($recordCount records):
                  Encrypted: ${encryptedTimeMs}ms
                  Unencrypted: ${unencryptedTimeMs}ms
                  Overhead: ${"%.2f".format(overheadPercent)}%
            """.trimIndent()
        }
    }

    /**
     * Benchmark SharedPreferences operations
     */
    suspend fun benchmarkSharedPreferences(): List<BenchmarkResult> = withContext(Dispatchers.IO) {
        val results = mutableListOf<BenchmarkResult>()
        val operations = listOf(10, 100, 1000)

        // Unencrypted SharedPreferences
        val normalPrefs = context.getSharedPreferences("benchmark", Context.MODE_PRIVATE)

        operations.forEach { count ->
            // Write benchmark
            val encryptedWriteTime = measureTimeMillis {
                repeat(count) { i ->
                    securePrefs.putString("key_$i", "value_$i")
                }
            }

            val unencryptedWriteTime = measureTimeMillis {
                val editor = normalPrefs.edit()
                repeat(count) { i ->
                    editor.putString("key_$i", "value_$i")
                }
                editor.apply()
            }

            results.add(
                BenchmarkResult(
                    operation = "SharedPreferences Write",
                    recordCount = count,
                    encryptedTimeMs = encryptedWriteTime,
                    unencryptedTimeMs = unencryptedWriteTime,
                    overheadPercent = calculateOverhead(encryptedWriteTime, unencryptedWriteTime)
                )
            )

            // Read benchmark
            val encryptedReadTime = measureTimeMillis {
                repeat(count) { i ->
                    securePrefs.getString("key_$i")
                }
            }

            val unencryptedReadTime = measureTimeMillis {
                repeat(count) { i ->
                    normalPrefs.getString("key_$i", null)
                }
            }

            results.add(
                BenchmarkResult(
                    operation = "SharedPreferences Read",
                    recordCount = count,
                    encryptedTimeMs = encryptedReadTime,
                    unencryptedTimeMs = unencryptedReadTime,
                    overheadPercent = calculateOverhead(encryptedReadTime, unencryptedReadTime)
                )
            )
        }

        results
    }

    /**
     * Benchmark database operations
     */
    suspend fun benchmarkDatabase(): List<BenchmarkResult> = withContext(Dispatchers.IO) {
        val results = mutableListOf<BenchmarkResult>()
        val operations = listOf(100, 1000, 5000)

        // Unencrypted Room database
        val unencryptedDb = Room.databaseBuilder(
            context,
            UnencryptedDatabase::class.java,
            "benchmark.db"
        ).build()

        operations.forEach { count ->
            // Insert benchmark
            val users = (1..count).map { i ->
                User(
                    username = "user_$i",
                    email = "user$i@example.com",
                    phoneNumber = "+123456789$i"
                )
            }

            val encryptedInsertTime = measureTimeMillis {
                users.forEach { encryptedDb.userDao().insertUser(it) }
            }

            val unencryptedInsertTime = measureTimeMillis {
                users.forEach { unencryptedDb.userDao().insertUser(it) }
            }

            results.add(
                BenchmarkResult(
                    operation = "Database Insert",
                    recordCount = count,
                    encryptedTimeMs = encryptedInsertTime,
                    unencryptedTimeMs = unencryptedInsertTime,
                    overheadPercent = calculateOverhead(encryptedInsertTime, unencryptedInsertTime)
                )
            )

            // Query benchmark
            val encryptedQueryTime = measureTimeMillis {
                encryptedDb.userDao().getAllUsers()
            }

            val unencryptedQueryTime = measureTimeMillis {
                unencryptedDb.userDao().getAllUsers()
            }

            results.add(
                BenchmarkResult(
                    operation = "Database Query",
                    recordCount = count,
                    encryptedTimeMs = encryptedQueryTime,
                    unencryptedTimeMs = unencryptedQueryTime,
                    overheadPercent = calculateOverhead(encryptedQueryTime, unencryptedQueryTime)
                )
            )

            // Clean up
            encryptedDb.userDao().deleteAllUsers()
            unencryptedDb.userDao().deleteAllUsers()
        }

        unencryptedDb.close()
        results
    }

    private fun calculateOverhead(encrypted: Long, unencrypted: Long): Double {
        if (unencrypted == 0L) return 0.0
        return ((encrypted - unencrypted).toDouble() / unencrypted) * 100
    }

    /**
     * Get performance summary
     */
    suspend fun getPerformanceSummary(): PerformanceSummary {
        val prefsResults = benchmarkSharedPreferences()
        val dbResults = benchmarkDatabase()

        return PerformanceSummary(
            avgPrefsOverhead = prefsResults.map { it.overheadPercent }.average(),
            avgDbOverhead = dbResults.map { it.overheadPercent }.average(),
            prefsResults = prefsResults,
            dbResults = dbResults
        )
    }

    data class PerformanceSummary(
        val avgPrefsOverhead: Double,
        val avgDbOverhead: Double,
        val prefsResults: List<BenchmarkResult>,
        val dbResults: List<BenchmarkResult>
    )
}
```

### Migration from Unencrypted to Encrypted Storage

```kotlin
/**
 * Migrate from unencrypted to encrypted storage
 */
class EncryptionMigration(
    private val context: Context,
    private val securePrefs: SecurePreferencesManager
) {

    /**
     * Migrate SharedPreferences
     */
    suspend fun migrateSharedPreferences(
        oldPrefsName: String
    ): MigrationResult = withContext(Dispatchers.IO) {
        try {
            val oldPrefs = context.getSharedPreferences(oldPrefsName, Context.MODE_PRIVATE)
            val allEntries = oldPrefs.all

            var migratedCount = 0

            allEntries.forEach { (key, value) ->
                when (value) {
                    is String -> securePrefs.putString(key, value)
                    is Int -> securePrefs.putInt(key, value)
                    is Boolean -> securePrefs.putBoolean(key, value)
                    is Long -> securePrefs.putLong(key, value)
                    is Float -> securePrefs.putFloat(key, value)
                    is Set<*> -> {
                        @Suppress("UNCHECKED_CAST")
                        securePrefs.putStringSet(key, value as Set<String>)
                    }
                }
                migratedCount++
            }

            // Delete old preferences
            oldPrefs.edit().clear().apply()

            MigrationResult.Success(migratedCount)
        } catch (e: Exception) {
            MigrationResult.Failure(e.message ?: "Unknown error")
        }
    }

    /**
     * Migrate Room database
     */
    suspend fun migrateDatabase(
        oldDbName: String,
        newDbName: String
    ): MigrationResult = withContext(Dispatchers.IO) {
        try {
            // Open old database
            val oldDb = Room.databaseBuilder(
                context,
                UnencryptedDatabase::class.java,
                oldDbName
            ).build()

            // Open new encrypted database
            val newDb = EncryptedDatabase.getInstance(context)

            // Migrate users
            val users = oldDb.userDao().getAllUsers()
            users.forEach { newDb.userDao().insertUser(it) }

            // Migrate messages
            users.forEach { user ->
                val messages = oldDb.messageDao().getMessagesForUser(user.id)
                messages.forEach { newDb.messageDao().insertMessage(it) }
            }

            // Close and delete old database
            oldDb.close()
            context.deleteDatabase(oldDbName)

            MigrationResult.Success(users.size)
        } catch (e: Exception) {
            MigrationResult.Failure(e.message ?: "Unknown error")
        }
    }

    sealed class MigrationResult {
        data class Success(val recordsMigrated: Int) : MigrationResult()
        data class Failure(val error: String) : MigrationResult()
    }
}
```

### Complete Repository with Encryption

```kotlin
/**
 * Repository with encrypted storage
 */
class UserRepository(
    private val database: EncryptedDatabase,
    private val securePrefs: SecurePreferencesManager
) {

    private val userDao = database.userDao()

    /**
     * Save user with encrypted storage
     */
    suspend fun saveUser(user: User): Long {
        val userId = userDao.insertUser(user)

        // Store user preferences
        securePrefs.putString("current_user_email", user.email)
        securePrefs.putLong("current_user_id", userId)

        return userId
    }

    /**
     * Get user by ID
     */
    suspend fun getUser(userId: Long): User? {
        return userDao.getUserById(userId)
    }

    /**
     * Get all users
     */
    suspend fun getAllUsers(): List<User> {
        return userDao.getAllUsers()
    }

    /**
     * Update user
     */
    suspend fun updateUser(user: User) {
        userDao.updateUser(user)

        // Update preferences if current user
        val currentUserId = securePrefs.getLong("current_user_id", -1)
        if (currentUserId == user.id) {
            securePrefs.putString("current_user_email", user.email)
        }
    }

    /**
     * Delete user
     */
    suspend fun deleteUser(user: User) {
        userDao.deleteUser(user)

        // Clear preferences if current user
        val currentUserId = securePrefs.getLong("current_user_id", -1)
        if (currentUserId == user.id) {
            securePrefs.remove("current_user_email")
            securePrefs.remove("current_user_id")
        }
    }

    /**
     * Get current user
     */
    suspend fun getCurrentUser(): User? {
        val userId = securePrefs.getLong("current_user_id", -1)
        return if (userId != -1L) {
            userDao.getUserById(userId)
        } else {
            null
        }
    }

    /**
     * Clear all data
     */
    suspend fun clearAllData() {
        userDao.deleteAllUsers()
        securePrefs.clear()
    }
}
```

### Best Practices

1. **Use EncryptedSharedPreferences for Simple Data**
   ```kotlin
   val securePrefs = SecurePreferencesManager(context)
   securePrefs.putString("token", authToken)
   ```

2. **Use SQLCipher for Databases**
   ```kotlin
   val factory = SupportFactory(passphrase)
   Room.databaseBuilder(...).openHelperFactory(factory).build()
   ```

3. **Store Keys in Android Keystore**
   ```kotlin
   val masterKey = MasterKey.Builder(context)
       .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
       .build()
   ```

4. **Monitor Performance Impact**
   ```kotlin
   // Typical overhead: 5-15% for EncryptedSharedPreferences
   // Typical overhead: 10-25% for SQLCipher
   ```

5. **Handle Key Rotation**
   ```kotlin
   database.rawExecSQL("PRAGMA rekey = 'newPassphrase'")
   ```

6. **Plan Migration Strategy**
   ```kotlin
   // Migrate existing data to encrypted storage
   migrateSharedPreferences("old_prefs")
   ```

7. **Use Strong Passphrases**
   ```kotlin
   val key = deriveKeyFromPassphrase(userPassphrase)
   ```

8. **Backup Encrypted Data Carefully**
   ```kotlin
   // Encrypted backups remain encrypted
   // Key backup requires separate secure channel
   ```

### Common Pitfalls

1. **Not Using Keystore**
   ```kotlin
   // BAD: Hardcoded passphrase
   val passphrase = "myPassword123".toByteArray()

   // GOOD: Key from Keystore
   val passphrase = keyManager.getDatabaseKey()
   ```

2. **Ignoring Performance**
   ```kotlin
   // Measure and optimize for your use case
   // Consider caching frequently accessed data
   ```

3. **Forgetting Migration**
   ```kotlin
   // Always provide migration path from unencrypted data
   ```

4. **Not Handling Key Invalidation**
   ```kotlin
   try {
       readEncryptedData()
   } catch (e: KeyPermanentlyInvalidatedException) {
       // User changed lockscreen - re-encrypt with new key
   }
   ```

### Summary

Data encryption at rest on Android:

- **EncryptedSharedPreferences**: Simple, automatic key management, 5-15% overhead
- **SQLCipher**: Database encryption, 10-25% overhead, manual key management
- **EncryptedFile**: Large files, streaming support
- **Key Management**: Android Keystore for secure key storage
- **Migration**: Plan for migrating existing data

**Decision Matrix**:
- Use **EncryptedSharedPreferences** for: tokens, settings, small data
- Use **SQLCipher** for: user data, messages, sensitive databases
- Use **EncryptedFile** for: documents, images, large files

**Performance Impact**:
- EncryptedSharedPreferences: ~5-15% slower than standard
- SQLCipher: ~10-25% slower than unencrypted Room
- File encryption: ~5-20% overhead depending on size

**Key Takeaways**:
1. Encryption is essential for sensitive data
2. Performance overhead is acceptable for most use cases
3. Use Android Keystore for key management
4. Plan migration from unencrypted to encrypted
5. Test on actual devices with realistic data sizes

---

## Ответ (RU)
**Шифрование данных в покое** защищает конфиденциальные данные на устройстве от несанкционированного доступа. Android предоставляет EncryptedSharedPreferences для простого хранилища и SQLCipher для шифрования баз данных.

### Сравнение подходов

| Функция | EncryptedSharedPreferences | SQLCipher |
|---------|---------------------------|-----------|
| Назначение | Настройки, токены | База данных |
| Производительность | Быстро | Умеренные накладные расходы |
| Сложность | Просто | Умеренно |
| Управление ключами | Автоматическое | Ручное |
| Шифрование | AES-256-GCM | AES-256 |

### Реализация

```kotlin
// EncryptedSharedPreferences
class SecurePreferencesManager(context: Context) {

    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val encryptedPrefs = EncryptedSharedPreferences.create(
        context,
        "secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun putString(key: String, value: String) {
        encryptedPrefs.edit().putString(key, value).apply()
    }
}

// SQLCipher с Room
class EncryptedDatabase : RoomDatabase() {

    companion object {
        fun getInstance(context: Context): EncryptedDatabase {
            SQLiteDatabase.loadLibs(context)
            val passphrase = getDatabasePassphrase(context)
            val factory = SupportFactory(passphrase)

            return Room.databaseBuilder(
                context,
                EncryptedDatabase::class.java,
                "encrypted.db"
            )
                .openHelperFactory(factory)
                .build()
        }
    }
}
```

### Управление ключами

```kotlin
class DatabaseKeyManager(context: Context) {

    fun getDatabaseKey(): ByteArray {
        // Генерация или получение ключа из Keystore
        val key = ByteArray(32)
        SecureRandom().nextBytes(key)
        return key
    }

    fun deriveKeyFromPassphrase(passphrase: String): ByteArray {
        val factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
        val spec = PBEKeySpec(passphrase.toCharArray(), salt, 10000, 256)
        return factory.generateSecret(spec).encoded
    }
}
```

### Производительность

**Типичные накладные расходы:**
- EncryptedSharedPreferences: 5-15%
- SQLCipher: 10-25%
- Шифрование файлов: 5-20%

### Миграция данных

```kotlin
suspend fun migrateSharedPreferences(oldPrefsName: String) {
    val oldPrefs = context.getSharedPreferences(oldPrefsName, MODE_PRIVATE)
    oldPrefs.all.forEach { (key, value) ->
        when (value) {
            is String -> securePrefs.putString(key, value)
            is Int -> securePrefs.putInt(key, value)
            // ...
        }
    }
    oldPrefs.edit().clear().apply()
}
```

### Best Practices

1. **EncryptedSharedPreferences для простых данных**
2. **SQLCipher для баз данных**
3. **Хранение ключей в Android Keystore**
4. **Мониторинг влияния на производительность**
5. **Обработка ротации ключей**
6. **Планирование миграции**
7. **Использование сильных паролей**

### Резюме

Шифрование данных в покое:

- **EncryptedSharedPreferences**: Простое, автоматическое управление ключами
- **SQLCipher**: Шифрование БД, ручное управление
- **Keystore**: Безопасное хранение ключей
- **Производительность**: 5-25% накладных расходов
- **Миграция**: Планируйте переход от незашифрованных данных

**Выбор решения**:
- EncryptedSharedPreferences: токены, настройки
- SQLCipher: пользовательские данные, сообщения
- EncryptedFile: документы, изображения

---

## Related Questions

### Related (Medium)
- [[q-android-security-practices-checklist--android--medium]] - Security
- [[q-encrypted-file-storage--security--medium]] - Security
- [[q-database-encryption-android--android--medium]] - Security
- [[q-app-security-best-practices--security--medium]] - Security
- [[q-android-keystore-system--security--medium]] - Security
