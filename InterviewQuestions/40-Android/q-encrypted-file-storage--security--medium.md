---
id: "20251015082237416"
title: "Encrypted File Storage / Зашифрованное хранение файлов"
topic: security
difficulty: medium
status: draft
created: 2025-10-15
tags: - security
  - encryption
  - file-storage
  - streaming
  - encrypted-file
  - difficulty/medium
---
# Encrypted File Storage / Шифрование файлов

**English**: Implement encrypted file storage using EncryptedFile API. Handle large files with streaming encryption/decryption.

## Answer (EN)
The **EncryptedFile API** from the Android Security Crypto library provides secure file encryption with automatic key management using Android Keystore. It uses AES-256-GCM encryption with streaming support for large files, ensuring both confidentiality and integrity.

### Key Concepts

#### EncryptedFile Features

1. **Automatic Key Management**: Keys stored in Android Keystore
2. **Streaming Encryption**: Efficient for large files
3. **AES-256-GCM**: Strong encryption with authentication
4. **File Integrity**: Detects tampering automatically
5. **Simple API**: Easy to implement and maintain

#### Security Guarantees

```kotlin
// EncryptedFile provides:
// - Confidentiality: Data encrypted with AES-256
// - Integrity: GCM authentication tag
// - Key security: Keys in Android Keystore
// - Forward secrecy: Unique encryption per file operation
```

### Complete EncryptedFile Implementation

#### 1. Basic Setup and Configuration

```kotlin
import androidx.security.crypto.EncryptedFile
import androidx.security.crypto.MasterKey
import android.content.Context
import java.io.File

/**
 * Manager for encrypted file operations
 */
class EncryptedFileManager(private val context: Context) {

    companion object {
        private const val ENCRYPTED_DIR = "encrypted_files"
    }

    // Create or get MasterKey for encryption
    private val masterKey: MasterKey by lazy {
        MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
    }

    /**
     * Get encrypted file directory
     */
    private fun getEncryptedDir(): File {
        val dir = File(context.filesDir, ENCRYPTED_DIR)
        if (!dir.exists()) {
            dir.mkdirs()
        }
        return dir
    }

    /**
     * Create EncryptedFile instance
     */
    fun getEncryptedFile(fileName: String): EncryptedFile {
        val file = File(getEncryptedDir(), fileName)

        return EncryptedFile.Builder(
            context,
            file,
            masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()
    }

    /**
     * Write text to encrypted file
     */
    fun writeText(fileName: String, content: String) {
        val encryptedFile = getEncryptedFile(fileName)

        encryptedFile.openFileOutput().use { outputStream ->
            outputStream.write(content.toByteArray(Charsets.UTF_8))
        }
    }

    /**
     * Read text from encrypted file
     */
    fun readText(fileName: String): String? {
        val encryptedFile = getEncryptedFile(fileName)
        val file = File(getEncryptedDir(), fileName)

        if (!file.exists()) {
            return null
        }

        return encryptedFile.openFileInput().use { inputStream ->
            inputStream.readBytes().toString(Charsets.UTF_8)
        }
    }

    /**
     * Write bytes to encrypted file
     */
    fun writeBytes(fileName: String, data: ByteArray) {
        val encryptedFile = getEncryptedFile(fileName)

        encryptedFile.openFileOutput().use { outputStream ->
            outputStream.write(data)
        }
    }

    /**
     * Read bytes from encrypted file
     */
    fun readBytes(fileName: String): ByteArray? {
        val encryptedFile = getEncryptedFile(fileName)
        val file = File(getEncryptedDir(), fileName)

        if (!file.exists()) {
            return null
        }

        return encryptedFile.openFileInput().use { inputStream ->
            inputStream.readBytes()
        }
    }

    /**
     * Delete encrypted file
     */
    fun deleteFile(fileName: String): Boolean {
        val file = File(getEncryptedDir(), fileName)
        return file.delete()
    }

    /**
     * Check if encrypted file exists
     */
    fun fileExists(fileName: String): Boolean {
        val file = File(getEncryptedDir(), fileName)
        return file.exists()
    }

    /**
     * Get file size
     */
    fun getFileSize(fileName: String): Long {
        val file = File(getEncryptedDir(), fileName)
        return if (file.exists()) file.length() else 0L
    }

    /**
     * List all encrypted files
     */
    fun listFiles(): List<String> {
        val dir = getEncryptedDir()
        return dir.listFiles()?.map { it.name } ?: emptyList()
    }
}
```

#### 2. Streaming Encryption for Large Files

```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOn
import java.io.InputStream
import java.io.OutputStream

/**
 * Streaming file encryption for large files
 */
class StreamingEncryptedFileManager(private val context: Context) {

    companion object {
        private const val BUFFER_SIZE = 8192 // 8KB buffer
    }

    private val encryptedFileManager = EncryptedFileManager(context)

    /**
     * Encrypt large file with progress tracking
     */
    suspend fun encryptFileWithProgress(
        sourceFile: File,
        encryptedFileName: String
    ): Flow<EncryptionProgress> = flow {
        val totalBytes = sourceFile.length()
        var bytesProcessed = 0L

        emit(EncryptionProgress.Started(totalBytes))

        withContext(Dispatchers.IO) {
            val encryptedFile = encryptedFileManager.getEncryptedFile(encryptedFileName)

            sourceFile.inputStream().use { input ->
                encryptedFile.openFileOutput().use { output ->
                    val buffer = ByteArray(BUFFER_SIZE)
                    var bytesRead: Int

                    while (input.read(buffer).also { bytesRead = it } != -1) {
                        output.write(buffer, 0, bytesRead)
                        bytesProcessed += bytesRead

                        val progress = (bytesProcessed * 100 / totalBytes).toInt()
                        emit(EncryptionProgress.InProgress(bytesProcessed, totalBytes, progress))
                    }
                }
            }
        }

        emit(EncryptionProgress.Completed(totalBytes))
    }.flowOn(Dispatchers.IO)

    /**
     * Decrypt large file with progress tracking
     */
    suspend fun decryptFileWithProgress(
        encryptedFileName: String,
        destinationFile: File
    ): Flow<DecryptionProgress> = flow {
        val encryptedFile = encryptedFileManager.getEncryptedFile(encryptedFileName)
        val encryptedFileObj = File(context.filesDir, "encrypted_files/$encryptedFileName")

        if (!encryptedFileObj.exists()) {
            emit(DecryptionProgress.Error("Encrypted file not found"))
            return@flow
        }

        val totalBytes = encryptedFileObj.length()
        var bytesProcessed = 0L

        emit(DecryptionProgress.Started(totalBytes))

        withContext(Dispatchers.IO) {
            encryptedFile.openFileInput().use { input ->
                destinationFile.outputStream().use { output ->
                    val buffer = ByteArray(BUFFER_SIZE)
                    var bytesRead: Int

                    while (input.read(buffer).also { bytesRead = it } != -1) {
                        output.write(buffer, 0, bytesRead)
                        bytesProcessed += bytesRead

                        val progress = (bytesProcessed * 100 / totalBytes).toInt()
                        emit(DecryptionProgress.InProgress(bytesProcessed, totalBytes, progress))
                    }
                }
            }
        }

        emit(DecryptionProgress.Completed(totalBytes))
    }.flowOn(Dispatchers.IO)

    /**
     * Copy and encrypt file from URI (e.g., from file picker)
     */
    suspend fun encryptFromUri(
        uri: android.net.Uri,
        encryptedFileName: String
    ): Flow<EncryptionProgress> = flow {
        withContext(Dispatchers.IO) {
            context.contentResolver.openInputStream(uri)?.use { inputStream ->
                val totalBytes = context.contentResolver.query(
                    uri,
                    arrayOf(android.provider.OpenableColumns.SIZE),
                    null,
                    null,
                    null
                )?.use { cursor ->
                    cursor.moveToFirst()
                    cursor.getLong(0)
                } ?: -1L

                if (totalBytes > 0) {
                    emit(EncryptionProgress.Started(totalBytes))
                }

                val encryptedFile = encryptedFileManager.getEncryptedFile(encryptedFileName)
                var bytesProcessed = 0L

                encryptedFile.openFileOutput().use { output ->
                    val buffer = ByteArray(BUFFER_SIZE)
                    var bytesRead: Int

                    while (inputStream.read(buffer).also { bytesRead = it } != -1) {
                        output.write(buffer, 0, bytesRead)
                        bytesProcessed += bytesRead

                        if (totalBytes > 0) {
                            val progress = (bytesProcessed * 100 / totalBytes).toInt()
                            emit(EncryptionProgress.InProgress(bytesProcessed, totalBytes, progress))
                        }
                    }
                }

                emit(EncryptionProgress.Completed(bytesProcessed))
            } ?: emit(EncryptionProgress.Error("Failed to open URI"))
        }
    }.flowOn(Dispatchers.IO)

    sealed class EncryptionProgress {
        data class Started(val totalBytes: Long) : EncryptionProgress()
        data class InProgress(
            val bytesProcessed: Long,
            val totalBytes: Long,
            val percentage: Int
        ) : EncryptionProgress()
        data class Completed(val totalBytes: Long) : EncryptionProgress()
        data class Error(val message: String) : EncryptionProgress()
    }

    sealed class DecryptionProgress {
        data class Started(val totalBytes: Long) : DecryptionProgress()
        data class InProgress(
            val bytesProcessed: Long,
            val totalBytes: Long,
            val percentage: Int
        ) : DecryptionProgress()
        data class Completed(val totalBytes: Long) : DecryptionProgress()
        data class Error(val message: String) : DecryptionProgress()
    }
}
```

#### 3. EncryptedSharedPreferences Integration

```kotlin
import androidx.security.crypto.EncryptedSharedPreferences

/**
 * Secure settings storage using EncryptedSharedPreferences
 */
class SecurePreferences(context: Context) {

    companion object {
        private const val PREFS_FILE_NAME = "secure_prefs"
    }

    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val sharedPreferences = EncryptedSharedPreferences.create(
        context,
        PREFS_FILE_NAME,
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun putString(key: String, value: String) {
        sharedPreferences.edit().putString(key, value).apply()
    }

    fun getString(key: String, defaultValue: String? = null): String? {
        return sharedPreferences.getString(key, defaultValue)
    }

    fun putInt(key: String, value: Int) {
        sharedPreferences.edit().putInt(key, value).apply()
    }

    fun getInt(key: String, defaultValue: Int = 0): Int {
        return sharedPreferences.getInt(key, defaultValue)
    }

    fun putBoolean(key: String, value: Boolean) {
        sharedPreferences.edit().putBoolean(key, value).apply()
    }

    fun getBoolean(key: String, defaultValue: Boolean = false): Boolean {
        return sharedPreferences.getBoolean(key, defaultValue)
    }

    fun remove(key: String) {
        sharedPreferences.edit().remove(key).apply()
    }

    fun clear() {
        sharedPreferences.edit().clear().apply()
    }

    fun contains(key: String): Boolean {
        return sharedPreferences.contains(key)
    }
}
```

#### 4. Migration from Unencrypted to Encrypted Storage

```kotlin
/**
 * Migrate files from unencrypted to encrypted storage
 */
class EncryptionMigration(
    private val context: Context,
    private val encryptedFileManager: EncryptedFileManager
) {

    /**
     * Migrate all files from a directory to encrypted storage
     */
    suspend fun migrateDirectory(
        sourceDir: File,
        deleteOriginals: Boolean = true
    ): MigrationResult = withContext(Dispatchers.IO) {
        val results = mutableListOf<FileMigrationResult>()
        var successCount = 0
        var failureCount = 0

        sourceDir.listFiles()?.forEach { file ->
            if (file.isFile) {
                val result = migrateFile(file, deleteOriginals)
                results.add(result)

                when (result) {
                    is FileMigrationResult.Success -> successCount++
                    is FileMigrationResult.Failure -> failureCount++
                }
            }
        }

        MigrationResult(
            totalFiles = results.size,
            successCount = successCount,
            failureCount = failureCount,
            fileResults = results
        )
    }

    /**
     * Migrate single file to encrypted storage
     */
    private suspend fun migrateFile(
        sourceFile: File,
        deleteOriginal: Boolean
    ): FileMigrationResult = withContext(Dispatchers.IO) {
        try {
            val encryptedFileName = "${sourceFile.name}.encrypted"

            // Read original file
            val data = sourceFile.readBytes()

            // Write to encrypted storage
            encryptedFileManager.writeBytes(encryptedFileName, data)

            // Verify encrypted file
            val decrypted = encryptedFileManager.readBytes(encryptedFileName)
            if (!data.contentEquals(decrypted)) {
                throw Exception("Verification failed: decrypted data doesn't match")
            }

            // Delete original if requested
            if (deleteOriginal) {
                sourceFile.delete()
            }

            FileMigrationResult.Success(
                originalName = sourceFile.name,
                encryptedName = encryptedFileName,
                sizeBytes = data.size.toLong()
            )
        } catch (e: Exception) {
            FileMigrationResult.Failure(
                fileName = sourceFile.name,
                error = e.message ?: "Unknown error"
            )
        }
    }

    /**
     * Migrate SharedPreferences to EncryptedSharedPreferences
     */
    suspend fun migrateSharedPreferences(
        oldPrefsName: String,
        deleteOld: Boolean = true
    ): SharedPrefsMigrationResult = withContext(Dispatchers.IO) {
        try {
            val oldPrefs = context.getSharedPreferences(oldPrefsName, Context.MODE_PRIVATE)
            val securePrefs = SecurePreferences(context)

            val allEntries = oldPrefs.all
            var migratedCount = 0

            allEntries.forEach { (key, value) ->
                when (value) {
                    is String -> securePrefs.putString(key, value)
                    is Int -> securePrefs.putInt(key, value)
                    is Boolean -> securePrefs.putBoolean(key, value)
                    // Add other types as needed
                }
                migratedCount++
            }

            if (deleteOld) {
                oldPrefs.edit().clear().apply()
            }

            SharedPrefsMigrationResult.Success(
                prefsName = oldPrefsName,
                entriesMigrated = migratedCount
            )
        } catch (e: Exception) {
            SharedPrefsMigrationResult.Failure(
                prefsName = oldPrefsName,
                error = e.message ?: "Unknown error"
            )
        }
    }

    data class MigrationResult(
        val totalFiles: Int,
        val successCount: Int,
        val failureCount: Int,
        val fileResults: List<FileMigrationResult>
    )

    sealed class FileMigrationResult {
        data class Success(
            val originalName: String,
            val encryptedName: String,
            val sizeBytes: Long
        ) : FileMigrationResult()

        data class Failure(
            val fileName: String,
            val error: String
        ) : FileMigrationResult()
    }

    sealed class SharedPrefsMigrationResult {
        data class Success(
            val prefsName: String,
            val entriesMigrated: Int
        ) : SharedPrefsMigrationResult()

        data class Failure(
            val prefsName: String,
            val error: String
        ) : SharedPrefsMigrationResult()
    }
}
```

### Performance Comparison

```kotlin
import kotlin.system.measureTimeMillis

/**
 * Benchmark encrypted vs unencrypted file operations
 */
class EncryptionBenchmark(
    private val context: Context,
    private val encryptedFileManager: EncryptedFileManager
) {

    data class BenchmarkResult(
        val operation: String,
        val fileSize: Long,
        val encryptedTimeMs: Long,
        val unencryptedTimeMs: Long,
        val overhead: Double
    ) {
        override fun toString(): String {
            return """
                Operation: $operation
                File Size: ${fileSize / 1024} KB
                Encrypted: ${encryptedTimeMs}ms
                Unencrypted: ${unencryptedTimeMs}ms
                Overhead: ${"%.2f".format(overhead)}%
            """.trimIndent()
        }
    }

    suspend fun benchmarkWrite(sizeKB: Int): BenchmarkResult = withContext(Dispatchers.IO) {
        val data = ByteArray(sizeKB * 1024) { it.toByte() }

        val encryptedTime = measureTimeMillis {
            encryptedFileManager.writeBytes("benchmark_encrypted.dat", data)
        }

        val unencryptedFile = File(context.cacheDir, "benchmark_unencrypted.dat")
        val unencryptedTime = measureTimeMillis {
            unencryptedFile.writeBytes(data)
        }

        val overhead = ((encryptedTime - unencryptedTime).toDouble() / unencryptedTime) * 100

        BenchmarkResult(
            operation = "Write",
            fileSize = data.size.toLong(),
            encryptedTimeMs = encryptedTime,
            unencryptedTimeMs = unencryptedTime,
            overhead = overhead
        )
    }

    suspend fun benchmarkRead(sizeKB: Int): BenchmarkResult = withContext(Dispatchers.IO) {
        val data = ByteArray(sizeKB * 1024) { it.toByte() }

        // Setup
        encryptedFileManager.writeBytes("benchmark_encrypted.dat", data)
        val unencryptedFile = File(context.cacheDir, "benchmark_unencrypted.dat")
        unencryptedFile.writeBytes(data)

        val encryptedTime = measureTimeMillis {
            encryptedFileManager.readBytes("benchmark_encrypted.dat")
        }

        val unencryptedTime = measureTimeMillis {
            unencryptedFile.readBytes()
        }

        val overhead = ((encryptedTime - unencryptedTime).toDouble() / unencryptedTime) * 100

        BenchmarkResult(
            operation = "Read",
            fileSize = data.size.toLong(),
            encryptedTimeMs = encryptedTime,
            unencryptedTimeMs = unencryptedTime,
            overhead = overhead
        )
    }

    suspend fun runFullBenchmark(): List<BenchmarkResult> = withContext(Dispatchers.IO) {
        listOf(
            benchmarkWrite(100),   // 100KB
            benchmarkWrite(1024),  // 1MB
            benchmarkWrite(10240), // 10MB
            benchmarkRead(100),
            benchmarkRead(1024),
            benchmarkRead(10240)
        )
    }
}
```

### Error Handling and Recovery

```kotlin
/**
 * Robust error handling for encrypted file operations
 */
class RobustEncryptedFileManager(
    context: Context
) {
    private val encryptedFileManager = EncryptedFileManager(context)

    /**
     * Write with automatic retry and backup
     */
    suspend fun safeWrite(
        fileName: String,
        data: ByteArray,
        maxRetries: Int = 3
    ): WriteResult = withContext(Dispatchers.IO) {
        var lastException: Exception? = null

        repeat(maxRetries) { attempt ->
            try {
                // Create backup if file exists
                if (encryptedFileManager.fileExists(fileName)) {
                    val backupName = "$fileName.backup"
                    val existing = encryptedFileManager.readBytes(fileName)
                    existing?.let {
                        encryptedFileManager.writeBytes(backupName, it)
                    }
                }

                // Write new data
                encryptedFileManager.writeBytes(fileName, data)

                // Verify write
                val written = encryptedFileManager.readBytes(fileName)
                if (!data.contentEquals(written)) {
                    throw Exception("Write verification failed")
                }

                return@withContext WriteResult.Success(fileName)
            } catch (e: Exception) {
                lastException = e
                if (attempt < maxRetries - 1) {
                    delay(100 * (attempt + 1)) // Exponential backoff
                }
            }
        }

        WriteResult.Failure(fileName, lastException?.message ?: "Unknown error")
    }

    /**
     * Read with fallback to backup
     */
    suspend fun safeRead(fileName: String): ReadResult = withContext(Dispatchers.IO) {
        try {
            val data = encryptedFileManager.readBytes(fileName)
            if (data != null) {
                return@withContext ReadResult.Success(data)
            }

            // Try backup
            val backupName = "$fileName.backup"
            val backupData = encryptedFileManager.readBytes(backupName)
            if (backupData != null) {
                return@withContext ReadResult.SuccessFromBackup(backupData)
            }

            ReadResult.Failure("File not found")
        } catch (e: Exception) {
            // Try backup on error
            try {
                val backupName = "$fileName.backup"
                val backupData = encryptedFileManager.readBytes(backupName)
                if (backupData != null) {
                    return@withContext ReadResult.SuccessFromBackup(backupData)
                }
            } catch (backupException: Exception) {
                // Ignore backup exception
            }

            ReadResult.Failure(e.message ?: "Unknown error")
        }
    }

    sealed class WriteResult {
        data class Success(val fileName: String) : WriteResult()
        data class Failure(val fileName: String, val error: String) : WriteResult()
    }

    sealed class ReadResult {
        data class Success(val data: ByteArray) : ReadResult()
        data class SuccessFromBackup(val data: ByteArray) : ReadResult()
        data class Failure(val error: String) : ReadResult()
    }
}
```

### Complete File Manager Example

```kotlin
/**
 * Complete encrypted file manager with all features
 */
class ComprehensiveFileManager(private val context: Context) {

    private val encryptedFileManager = EncryptedFileManager(context)
    private val streamingManager = StreamingEncryptedFileManager(context)
    private val robustManager = RobustEncryptedFileManager(context)

    /**
     * Save document with encryption
     */
    suspend fun saveDocument(
        name: String,
        content: String,
        metadata: DocumentMetadata
    ): SaveResult = withContext(Dispatchers.IO) {
        try {
            // Save metadata
            val metadataJson = Json.encodeToString(metadata)
            encryptedFileManager.writeText("$name.meta", metadataJson)

            // Save content
            encryptedFileManager.writeText(name, content)

            SaveResult.Success(name)
        } catch (e: Exception) {
            SaveResult.Failure(e.message ?: "Unknown error")
        }
    }

    /**
     * Load document with decryption
     */
    suspend fun loadDocument(name: String): LoadResult = withContext(Dispatchers.IO) {
        try {
            val content = encryptedFileManager.readText(name)
                ?: return@withContext LoadResult.NotFound

            val metadataJson = encryptedFileManager.readText("$name.meta")
            val metadata = metadataJson?.let {
                Json.decodeFromString<DocumentMetadata>(it)
            }

            LoadResult.Success(
                Document(
                    name = name,
                    content = content,
                    metadata = metadata
                )
            )
        } catch (e: Exception) {
            LoadResult.Failure(e.message ?: "Unknown error")
        }
    }

    /**
     * Save large file with progress
     */
    fun saveLargeFile(
        sourceFile: File,
        encryptedName: String
    ): Flow<StreamingEncryptedFileManager.EncryptionProgress> {
        return streamingManager.encryptFileWithProgress(sourceFile, encryptedName)
    }

    /**
     * Export encrypted file to external storage
     */
    suspend fun exportFile(
        encryptedName: String,
        destinationUri: android.net.Uri
    ): ExportResult = withContext(Dispatchers.IO) {
        try {
            val data = encryptedFileManager.readBytes(encryptedName)
                ?: return@withContext ExportResult.NotFound

            context.contentResolver.openOutputStream(destinationUri)?.use { output ->
                output.write(data)
            } ?: return@withContext ExportResult.Failure("Failed to open output stream")

            ExportResult.Success(data.size.toLong())
        } catch (e: Exception) {
            ExportResult.Failure(e.message ?: "Unknown error")
        }
    }

    @Serializable
    data class DocumentMetadata(
        val createdAt: Long = System.currentTimeMillis(),
        val modifiedAt: Long = System.currentTimeMillis(),
        val author: String? = null,
        val tags: List<String> = emptyList()
    )

    data class Document(
        val name: String,
        val content: String,
        val metadata: DocumentMetadata?
    )

    sealed class SaveResult {
        data class Success(val name: String) : SaveResult()
        data class Failure(val error: String) : SaveResult()
    }

    sealed class LoadResult {
        data class Success(val document: Document) : LoadResult()
        object NotFound : LoadResult()
        data class Failure(val error: String) : LoadResult()
    }

    sealed class ExportResult {
        data class Success(val bytesWritten: Long) : ExportResult()
        object NotFound : ExportResult()
        data class Failure(val error: String) : ExportResult()
    }
}
```

### Best Practices

1. **Use MasterKey with Android Keystore**
   ```kotlin
   val masterKey = MasterKey.Builder(context)
       .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
       .build()
   ```

2. **Stream Large Files**
   ```kotlin
   // Don't load entire file into memory
   encryptedFile.openFileInput().use { input ->
       input.copyTo(output, bufferSize = 8192)
   }
   ```

3. **Always Use Try-Catch**
   ```kotlin
   try {
       encryptedFileManager.writeText(name, content)
   } catch (e: Exception) {
       // Handle encryption failures
   }
   ```

4. **Verify Data After Write**
   ```kotlin
   encryptedFileManager.writeBytes(name, data)
   val verified = encryptedFileManager.readBytes(name)
   require(data.contentEquals(verified))
   ```

5. **Keep Backups During Migration**
   ```kotlin
   // Create backup before deleting originals
   migrateDirectory(sourceDir, deleteOriginals = false)
   ```

6. **Use EncryptedSharedPreferences for Settings**
   ```kotlin
   // Not EncryptedFile for simple key-value pairs
   val securePrefs = SecurePreferences(context)
   ```

7. **Handle Key Invalidation**
   ```kotlin
   try {
       decrypt(file)
   } catch (e: KeyPermanentlyInvalidatedException) {
       // User changed lockscreen - keys invalidated
       recreateKeys()
   }
   ```

8. **Monitor File Sizes**
   ```kotlin
   // Encrypted files are larger due to metadata
   val overhead = encryptedSize - originalSize
   ```

9. **Use Appropriate Buffer Sizes**
   ```kotlin
   // 8KB is optimal for most cases
   private const val BUFFER_SIZE = 8192
   ```

10. **Implement Progress Tracking**
    ```kotlin
    encryptFileWithProgress(file, name).collect { progress ->
        when (progress) {
            is InProgress -> updateUI(progress.percentage)
            // ...
        }
    }
    ```

### Common Pitfalls

1. **Loading Large Files into Memory**
   ```kotlin
   // BAD
   val allData = file.readBytes()

   // GOOD
   file.inputStream().use { input ->
       input.copyTo(output, bufferSize = 8192)
   }
   ```

2. **Not Handling Key Invalidation**
   ```kotlin
   // Keys invalidated when user changes lockscreen
   // Always catch KeyPermanentlyInvalidatedException
   ```

3. **Forgetting File Extensions**
   ```kotlin
   // Track which files are encrypted
   val encryptedName = "$originalName.encrypted"
   ```

4. **Synchronous Operations on Main Thread**
   ```kotlin
   // Always use coroutines or background threads
   withContext(Dispatchers.IO) { /* encrypt */ }
   ```

### Summary

EncryptedFile API provides:

- **Secure Storage**: AES-256-GCM encryption
- **Easy Integration**: Simple API with automatic key management
- **Streaming Support**: Efficient for large files
- **Android Keystore**: Hardware-backed key security
- **Integrity Protection**: Automatic tampering detection

Use for: sensitive documents, user data, downloaded files, cached credentials, private photos/videos, and any confidential information.

**Typical overhead**: 5-15% for encryption/decryption, negligible for most use cases.

---

## Ответ (RU)
**EncryptedFile API** из библиотеки Android Security Crypto обеспечивает безопасное шифрование файлов с автоматическим управлением ключами через Android Keystore. Использует шифрование AES-256-GCM с поддержкой потоковой обработки для больших файлов.

### Основные концепции

**Возможности EncryptedFile:**
- Автоматическое управление ключами в Android Keystore
- Потоковое шифрование для больших файлов
- Сильное шифрование AES-256-GCM
- Автоматическая проверка целостности файлов
- Простой API для внедрения

### Полная реализация

```kotlin
class EncryptedFileManager(private val context: Context) {

    private val masterKey: MasterKey by lazy {
        MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
    }

    fun getEncryptedFile(fileName: String): EncryptedFile {
        val file = File(context.filesDir, "encrypted/$fileName")

        return EncryptedFile.Builder(
            context,
            file,
            masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()
    }

    fun writeText(fileName: String, content: String) {
        val encryptedFile = getEncryptedFile(fileName)
        encryptedFile.openFileOutput().use { output ->
            output.write(content.toByteArray(Charsets.UTF_8))
        }
    }

    fun readText(fileName: String): String? {
        val encryptedFile = getEncryptedFile(fileName)
        return encryptedFile.openFileInput().use { input ->
            input.readBytes().toString(Charsets.UTF_8)
        }
    }
}
```

### Потоковое шифрование

```kotlin
class StreamingEncryptedFileManager(private val context: Context) {

    suspend fun encryptFileWithProgress(
        sourceFile: File,
        encryptedFileName: String
    ): Flow<EncryptionProgress> = flow {
        val totalBytes = sourceFile.length()
        var bytesProcessed = 0L

        sourceFile.inputStream().use { input ->
            encryptedFile.openFileOutput().use { output ->
                val buffer = ByteArray(8192)
                var bytesRead: Int

                while (input.read(buffer).also { bytesRead = it } != -1) {
                    output.write(buffer, 0, bytesRead)
                    bytesProcessed += bytesRead

                    val progress = (bytesProcessed * 100 / totalBytes).toInt()
                    emit(EncryptionProgress.InProgress(bytesProcessed, totalBytes, progress))
                }
            }
        }

        emit(EncryptionProgress.Completed(totalBytes))
    }.flowOn(Dispatchers.IO)
}
```

### EncryptedSharedPreferences

```kotlin
class SecurePreferences(context: Context) {

    private val sharedPreferences = EncryptedSharedPreferences.create(
        context,
        "secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun putString(key: String, value: String) {
        sharedPreferences.edit().putString(key, value).apply()
    }

    fun getString(key: String, defaultValue: String? = null): String? {
        return sharedPreferences.getString(key, defaultValue)
    }
}
```

### Миграция данных

```kotlin
suspend fun migrateFile(
    sourceFile: File,
    deleteOriginal: Boolean
): FileMigrationResult = withContext(Dispatchers.IO) {
    try {
        val data = sourceFile.readBytes()
        encryptedFileManager.writeBytes("${sourceFile.name}.encrypted", data)

        // Проверка
        val decrypted = encryptedFileManager.readBytes("${sourceFile.name}.encrypted")
        require(data.contentEquals(decrypted))

        if (deleteOriginal) {
            sourceFile.delete()
        }

        FileMigrationResult.Success(sourceFile.name)
    } catch (e: Exception) {
        FileMigrationResult.Failure(sourceFile.name, e.message ?: "Unknown error")
    }
}
```

### Best Practices

1. **Используйте MasterKey с Android Keystore**
2. **Потоковая обработка для больших файлов**
3. **Всегда обрабатывайте исключения**
4. **Проверяйте данные после записи**
5. **Создавайте резервные копии при миграции**
6. **EncryptedSharedPreferences для настроек**
7. **Обрабатывайте инвалидацию ключей**
8. **Используйте оптимальные размеры буфера (8KB)**

### Резюме

EncryptedFile API обеспечивает:

- **Безопасное хранение**: Шифрование AES-256-GCM
- **Простую интеграцию**: Автоматическое управление ключами
- **Потоковую обработку**: Эффективно для больших файлов
- **Защиту целостности**: Автоматическое обнаружение подделки

Используйте для: конфиденциальных документов, пользовательских данных, загруженных файлов, кэшированных учетных данных, приватных фото/видео.

**Накладные расходы**: 5-15% на шифрование/дешифрование, незначительны для большинства случаев.

---

## Related Questions

### Prerequisites (Easier)
- [[q-sharedpreferences-commit-vs-apply--android--easy]] - Storage

### Related (Medium)
- [[q-database-encryption-android--android--medium]] - Storage, Security
- [[q-android-security-practices-checklist--android--medium]] - Security
- [[q-android-storage-types--android--medium]] - Storage
- [[q-app-security-best-practices--security--medium]] - Security
- [[q-data-encryption-at-rest--security--medium]] - Security
