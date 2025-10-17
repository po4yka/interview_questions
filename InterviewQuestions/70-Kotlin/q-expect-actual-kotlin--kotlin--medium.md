---
id: 20251012-150059
title: "Kotlin Multiplatform expect/actual / Механизм expect/actual в Kotlin"
aliases: []

# Classification
topic: kotlin
subtopics: [multiplatform, expect-actual, platform-specific, kmp, common-code]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive guide on Kotlin Multiplatform expect/actual mechanism

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-native--kotlin--hard, q-kotlin-constructors--kotlin--easy, q-kotlin-collections--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [kotlin, multiplatform, kmp, expect-actual, platform-specific, cross-platform, difficulty/medium]
---

# Question (EN)
> What is the expect/actual mechanism in Kotlin Multiplatform? Explain how to declare platform-specific implementations and provide practical examples.

# Вопрос (RU)
> Что такое механизм expect/actual в Kotlin Multiplatform? Объясните как объявлять платформо-специфичные реализации и приведите практические примеры.

---

## Answer (EN)

The **expect/actual** mechanism in Kotlin Multiplatform (KMP) allows you to write common code that can have different implementations on different platforms (Android, iOS, JVM, JS, Native). It provides a type-safe way to access platform-specific APIs while maintaining code sharing.

### Key Concepts

1. **expect**: Declaration in common code that something will be provided by platform-specific code
2. **actual**: Platform-specific implementation of the expected declaration
3. **Platform modules**: commonMain, androidMain, iosMain, jvmMain, jsMain
4. **Type safety**: Compiler ensures actual implementations match expect declarations
5. **Flexibility**: Can be used for functions, classes, properties, and objects

### How expect/actual Works

```

         commonMain                   
      
    expect fun getPlatform()      
    expect class Storage          
      

               
      
                       
   
 androidMain     iosMain   
 actual impl    actual impl
   
```

### expect/actual Functions

Basic function declarations:

```kotlin
// commonMain/Platform.kt
expect fun getPlatformName(): String

expect fun currentTimeMillis(): Long

expect fun generateUUID(): String

// Common code using expect functions
class Logger {
    fun log(message: String) {
        val timestamp = currentTimeMillis()
        val platform = getPlatformName()
        println("[$platform][$timestamp] $message")
    }
}
```

Platform implementations:

```kotlin
// androidMain/Platform.kt
actual fun getPlatformName(): String = "Android ${android.os.Build.VERSION.SDK_INT}"

actual fun currentTimeMillis(): Long = System.currentTimeMillis()

actual fun generateUUID(): String = java.util.UUID.randomUUID().toString()

// iosMain/Platform.kt
import platform.UIKit.UIDevice
import platform.Foundation.NSUUID

actual fun getPlatformName(): String =
    "iOS ${UIDevice.currentDevice.systemVersion}"

actual fun currentTimeMillis(): Long =
    platform.Foundation.NSDate().timeIntervalSince1970.toLong() * 1000

actual fun generateUUID(): String =
    NSUUID().UUIDString()
```

### expect/actual Classes

Full class implementations:

```kotlin
// commonMain/Storage.kt
expect class KeyValueStorage {
    fun saveString(key: String, value: String)
    fun getString(key: String): String?
    fun remove(key: String)
    fun clear()
}

// Common usage
class UserPreferences(private val storage: KeyValueStorage) {
    var username: String?
        get() = storage.getString("username")
        set(value) {
            value?.let { storage.saveString("username", it) }
                ?: storage.remove("username")
        }

    var theme: String
        get() = storage.getString("theme") ?: "light"
        set(value) = storage.saveString("theme", value)

    fun clearAll() = storage.clear()
}
```

Android implementation:

```kotlin
// androidMain/Storage.kt
import android.content.Context
import android.content.SharedPreferences

actual class KeyValueStorage(context: Context) {
    private val prefs: SharedPreferences =
        context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE)

    actual fun saveString(key: String, value: String) {
        prefs.edit().putString(key, value).apply()
    }

    actual fun getString(key: String): String? {
        return prefs.getString(key, null)
    }

    actual fun remove(key: String) {
        prefs.edit().remove(key).apply()
    }

    actual fun clear() {
        prefs.edit().clear().apply()
    }
}
```

iOS implementation:

```kotlin
// iosMain/Storage.kt
import platform.Foundation.NSUserDefaults

actual class KeyValueStorage {
    private val userDefaults = NSUserDefaults.standardUserDefaults

    actual fun saveString(key: String, value: String) {
        userDefaults.setObject(value, forKey = key)
        userDefaults.synchronize()
    }

    actual fun getString(key: String): String? {
        return userDefaults.stringForKey(key)
    }

    actual fun remove(key: String) {
        userDefaults.removeObjectForKey(key)
        userDefaults.synchronize()
    }

    actual fun clear() {
        val dictionary = userDefaults.dictionaryRepresentation()
        dictionary.keys.forEach { key ->
            userDefaults.removeObjectForKey(key as String)
        }
        userDefaults.synchronize()
    }
}
```

### expect/actual with Type Parameters

```kotlin
// commonMain/Serializer.kt
expect class JsonSerializer {
    fun <T> serialize(obj: T): String
    fun <T> deserialize(json: String, type: Class<T>): T
}

// androidMain/Serializer.kt
import com.google.gson.Gson

actual class JsonSerializer {
    private val gson = Gson()

    actual fun <T> serialize(obj: T): String {
        return gson.toJson(obj)
    }

    actual fun <T> deserialize(json: String, type: Class<T>): T {
        return gson.fromJson(json, type)
    }
}

// iosMain/Serializer.kt
import kotlinx.serialization.json.Json
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString

actual class JsonSerializer {
    actual fun <T> serialize(obj: T): String {
        return Json.encodeToString(obj)
    }

    actual fun <T> deserialize(json: String, type: Class<T>): T {
        return Json.decodeFromString(json)
    }
}
```

### expect/actual Properties

```kotlin
// commonMain/Platform.kt
expect val platformName: String
expect val platformVersion: String
expect val deviceModel: String

// Common usage
fun getSystemInfo(): String {
    return buildString {
        appendLine("Platform: $platformName")
        appendLine("Version: $platformVersion")
        appendLine("Device: $deviceModel")
    }
}

// androidMain/Platform.kt
import android.os.Build

actual val platformName: String = "Android"
actual val platformVersion: String = Build.VERSION.RELEASE
actual val deviceModel: String = "${Build.MANUFACTURER} ${Build.MODEL}"

// iosMain/Platform.kt
import platform.UIKit.UIDevice

actual val platformName: String = "iOS"
actual val platformVersion: String = UIDevice.currentDevice.systemVersion
actual val deviceModel: String = UIDevice.currentDevice.model
```

### expect/actual Objects (Singletons)

```kotlin
// commonMain/Logger.kt
expect object PlatformLogger {
    fun debug(message: String)
    fun info(message: String)
    fun warning(message: String)
    fun error(message: String)
}

// Common usage
class AppLogger {
    fun logAppStart() {
        PlatformLogger.info("Application started")
    }

    fun logError(exception: Exception) {
        PlatformLogger.error("Error: ${exception.message}")
    }
}

// androidMain/Logger.kt
import android.util.Log

actual object PlatformLogger {
    private const val TAG = "KMPApp"

    actual fun debug(message: String) {
        Log.d(TAG, message)
    }

    actual fun info(message: String) {
        Log.i(TAG, message)
    }

    actual fun warning(message: String) {
        Log.w(TAG, message)
    }

    actual fun error(message: String) {
        Log.e(TAG, message)
    }
}

// iosMain/Logger.kt
import platform.Foundation.NSLog

actual object PlatformLogger {
    actual fun debug(message: String) {
        NSLog("[DEBUG] $message")
    }

    actual fun info(message: String) {
        NSLog("[INFO] $message")
    }

    actual fun warning(message: String) {
        NSLog("[WARNING] $message")
    }

    actual fun error(message: String) {
        NSLog("[ERROR] $message")
    }
}
```

### Real-World Example: HTTP Client

```kotlin
// commonMain/HttpClient.kt
expect class HttpClient {
    suspend fun get(url: String): String
    suspend fun post(url: String, body: String): String
    fun close()
}

// Common repository using HTTP client
class ApiRepository(private val client: HttpClient) {
    suspend fun fetchUsers(): List<User> {
        val response = client.get("https://api.example.com/users")
        return Json.decodeFromString(response)
    }

    suspend fun createUser(user: User): User {
        val body = Json.encodeToString(user)
        val response = client.post("https://api.example.com/users", body)
        return Json.decodeFromString(response)
    }

    fun cleanup() {
        client.close()
    }
}

// androidMain/HttpClient.kt
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.MediaType.Companion.toMediaType
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

actual class HttpClient {
    private val okHttpClient = OkHttpClient()

    actual suspend fun get(url: String): String = suspendCancellableCoroutine { continuation ->
        val request = Request.Builder()
            .url(url)
            .build()

        okHttpClient.newCall(request).execute().use { response ->
            if (response.isSuccessful) {
                continuation.resume(response.body?.string() ?: "")
            } else {
                continuation.resumeWithException(
                    Exception("HTTP ${response.code}")
                )
            }
        }
    }

    actual suspend fun post(url: String, body: String): String =
        suspendCancellableCoroutine { continuation ->
            val mediaType = "application/json".toMediaType()
            val requestBody = body.toRequestBody(mediaType)
            val request = Request.Builder()
                .url(url)
                .post(requestBody)
                .build()

            okHttpClient.newCall(request).execute().use { response ->
                if (response.isSuccessful) {
                    continuation.resume(response.body?.string() ?: "")
                } else {
                    continuation.resumeWithException(
                        Exception("HTTP ${response.code}")
                    )
                }
            }
        }

    actual fun close() {
        okHttpClient.dispatcher.executorService.shutdown()
    }
}

// iosMain/HttpClient.kt
import platform.Foundation.*
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

actual class HttpClient {
    private val session = NSURLSession.sharedSession

    actual suspend fun get(url: String): String = suspendCancellableCoroutine { continuation ->
        val nsUrl = NSURL(string = url)
        val request = NSMutableURLRequest(uRL = nsUrl)
        request.HTTPMethod = "GET"

        val task = session.dataTaskWithRequest(request) { data, response, error ->
            when {
                error != null -> continuation.resumeWithException(
                    Exception(error.localizedDescription)
                )
                data != null -> {
                    val string = NSString.create(data = data, encoding = NSUTF8StringEncoding)
                    continuation.resume(string?.toString() ?: "")
                }
                else -> continuation.resumeWithException(Exception("Unknown error"))
            }
        }
        task.resume()

        continuation.invokeOnCancellation {
            task.cancel()
        }
    }

    actual suspend fun post(url: String, body: String): String =
        suspendCancellableCoroutine { continuation ->
            val nsUrl = NSURL(string = url)
            val request = NSMutableURLRequest(uRL = nsUrl)
            request.HTTPMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField = "Content-Type")
            request.HTTPBody = body.encodeToByteArray().toNSData()

            val task = session.dataTaskWithRequest(request) { data, response, error ->
                when {
                    error != null -> continuation.resumeWithException(
                        Exception(error.localizedDescription)
                    )
                    data != null -> {
                        val string = NSString.create(data = data, encoding = NSUTF8StringEncoding)
                        continuation.resume(string?.toString() ?: "")
                    }
                    else -> continuation.resumeWithException(Exception("Unknown error"))
                }
            }
            task.resume()

            continuation.invokeOnCancellation {
                task.cancel()
            }
        }

    actual fun close() {
        // iOS URLSession cleanup if needed
    }
}
```

### expect/actual with Interfaces

```kotlin
// commonMain/Database.kt
interface DatabaseDriver {
    fun insert(table: String, values: Map<String, Any>)
    fun query(table: String, where: String): List<Map<String, Any>>
    fun delete(table: String, where: String)
}

expect fun createDatabaseDriver(databaseName: String): DatabaseDriver

// Common usage
class UserDatabase {
    private val driver = createDatabaseDriver("users.db")

    fun saveUser(user: User) {
        driver.insert("users", mapOf(
            "id" to user.id,
            "name" to user.name,
            "email" to user.email
        ))
    }

    fun getUser(id: Int): User? {
        val results = driver.query("users", "id = $id")
        return results.firstOrNull()?.let {
            User(
                id = it["id"] as Int,
                name = it["name"] as String,
                email = it["email"] as String
            )
        }
    }
}

// androidMain/Database.kt
import android.content.ContentValues
import android.database.sqlite.SQLiteDatabase

class AndroidDatabaseDriver(private val db: SQLiteDatabase) : DatabaseDriver {
    override fun insert(table: String, values: Map<String, Any>) {
        val contentValues = ContentValues().apply {
            values.forEach { (key, value) ->
                when (value) {
                    is String -> put(key, value)
                    is Int -> put(key, value)
                    is Long -> put(key, value)
                    is Boolean -> put(key, value)
                }
            }
        }
        db.insert(table, null, contentValues)
    }

    override fun query(table: String, where: String): List<Map<String, Any>> {
        val results = mutableListOf<Map<String, Any>>()
        val cursor = db.query(table, null, where, null, null, null, null)

        cursor.use {
            while (it.moveToNext()) {
                val row = mutableMapOf<String, Any>()
                for (i in 0 until it.columnCount) {
                    val columnName = it.getColumnName(i)
                    val value = it.getString(i)
                    row[columnName] = value
                }
                results.add(row)
            }
        }
        return results
    }

    override fun delete(table: String, where: String) {
        db.delete(table, where, null)
    }
}

actual fun createDatabaseDriver(databaseName: String): DatabaseDriver {
    // Implementation would get SQLiteDatabase instance
    return AndroidDatabaseDriver(/* SQLiteDatabase instance */)
}

// iosMain/Database.kt
import platform.Foundation.*

class IosDatabaseDriver(private val databasePath: String) : DatabaseDriver {
    override fun insert(table: String, values: Map<String, Any>) {
        // iOS SQLite implementation
    }

    override fun query(table: String, where: String): List<Map<String, Any>> {
        // iOS SQLite implementation
        return emptyList()
    }

    override fun delete(table: String, where: String) {
        // iOS SQLite implementation
    }
}

actual fun createDatabaseDriver(databaseName: String): DatabaseDriver {
    val paths = NSSearchPathForDirectoriesInDomains(
        NSDocumentDirectory,
        NSUserDomainMask,
        true
    )
    val documentsDirectory = paths.first() as String
    val databasePath = "$documentsDirectory/$databaseName"
    return IosDatabaseDriver(databasePath)
}
```

### Common Pitfalls

```kotlin
// BAD: Using platform-specific types in expect
expect class MyClass {
    fun doSomething(context: android.content.Context)  // Error: Android type in common!
}

// GOOD: Use common types or abstraction
expect class MyClass {
    fun doSomething(platformContext: Any)
}

// BAD: Different signatures between expect and actual
expect fun format(value: Double): String

actual fun format(value: Double, precision: Int = 2): String  // Error: different signature!

// GOOD: Match signatures exactly
expect fun format(value: Double, precision: Int = 2): String

actual fun format(value: Double, precision: Int): String =
    String.format("%.${precision}f", value)

// BAD: Forgetting to provide actual implementation
expect fun platformSpecific(): String

// iosMain: Missing actual implementation
// This will cause compilation error!

// GOOD: Always provide actual for all platforms
// androidMain
actual fun platformSpecific(): String = "Android"

// iosMain
actual fun platformSpecific(): String = "iOS"
```

### Best Practices

#### DO:

```kotlin
// Use expect/actual for platform-specific functionality
expect fun openUrl(url: String)

// Keep expect declarations minimal and focused
expect class ImageLoader {
    fun load(url: String): ByteArray
}

// Use descriptive names that indicate platform specificity
expect fun getPlatformHttpClient(): HttpClient

// Provide default implementations when possible
expect fun getDeviceId(): String {
    return "unknown"  // Default implementation
}

// Use sealed classes for platform-specific results
sealed class PlatformResult {
    data class Success(val data: String) : PlatformResult()
    data class Error(val message: String) : PlatformResult()
}
```

#### DON'T:

```kotlin
// Don't leak platform types into common code
expect class BadClass {
    fun method(view: android.view.View)  // Bad!
}

// Don't make everything expect/actual
// Use common code when possible
class CommonHelper {  // No need for expect/actual
    fun formatNumber(num: Int): String = num.toString()
}

// Don't create overly complex expect/actual hierarchies
expect abstract class ComplexBase {
    abstract class Inner {
        abstract class DeeperInner  // Too complex!
    }
}

// Don't forget null safety in actual implementations
expect fun getValue(): String

actual fun getValue(): String? = null  // Error: nullability mismatch!
```

### Testing expect/actual Code

```kotlin
// commonTest/PlatformTest.kt
import kotlin.test.Test
import kotlin.test.assertTrue
import kotlin.test.assertNotNull

class PlatformTest {
    @Test
    fun testPlatformName() {
        val name = getPlatformName()
        assertNotNull(name)
        assertTrue(name.isNotBlank())
    }

    @Test
    fun testStorage() {
        val storage = createStorage()
        storage.saveString("test", "value")
        assertEquals("value", storage.getString("test"))
        storage.clear()
        assertNull(storage.getString("test"))
    }
}

// Each platform can have specific tests too
// androidTest/AndroidPlatformTest.kt
class AndroidPlatformTest {
    @Test
    fun testAndroidSpecificFeature() {
        val name = getPlatformName()
        assertTrue(name.startsWith("Android"))
    }
}
```

### Project Structure

```
myproject/
 commonMain/
    kotlin/
        Platform.kt        (expect declarations)
        Storage.kt         (expect class)
        Logger.kt          (expect object)
 androidMain/
    kotlin/
        Platform.kt        (actual implementations)
        Storage.kt         (actual class)
        Logger.kt          (actual object)
 iosMain/
    kotlin/
        Platform.kt        (actual implementations)
        Storage.kt         (actual class)
        Logger.kt          (actual object)
 commonTest/
     kotlin/
         PlatformTest.kt    (common tests)
```

---

## Ответ (RU)

Механизм **expect/actual** в Kotlin Multiplatform (KMP) позволяет писать общий код, который может иметь разные реализации на разных платформах (Android, iOS, JVM, JS, Native). Он обеспечивает типобезопасный способ доступа к платформо-специфичным API при сохранении возможности разделения кода.

### Ключевые концепции

1. **expect**: Объявление в общем коде, что что-то будет предоставлено платформо-специфичным кодом
2. **actual**: Платформо-специфичная реализация ожидаемого объявления
3. **Платформенные модули**: commonMain, androidMain, iosMain, jvmMain, jsMain
4. **Типобезопасность**: Компилятор гарантирует, что actual реализации соответствуют expect объявлениям
5. **Гибкость**: Может использоваться для функций, классов, свойств и объектов

### expect/actual функции

Базовые объявления функций:

```kotlin
// commonMain/Platform.kt
expect fun getPlatformName(): String

expect fun currentTimeMillis(): Long

expect fun generateUUID(): String

// Общий код, использующий expect функции
class Logger {
    fun log(message: String) {
        val timestamp = currentTimeMillis()
        val platform = getPlatformName()
        println("[$platform][$timestamp] $message")
    }
}
```

Платформенные реализации:

```kotlin
// androidMain/Platform.kt
actual fun getPlatformName(): String = "Android ${android.os.Build.VERSION.SDK_INT}"

actual fun currentTimeMillis(): Long = System.currentTimeMillis()

actual fun generateUUID(): String = java.util.UUID.randomUUID().toString()

// iosMain/Platform.kt
import platform.UIKit.UIDevice
import platform.Foundation.NSUUID

actual fun getPlatformName(): String =
    "iOS ${UIDevice.currentDevice.systemVersion}"

actual fun currentTimeMillis(): Long =
    platform.Foundation.NSDate().timeIntervalSince1970.toLong() * 1000

actual fun generateUUID(): String =
    NSUUID().UUIDString()
```

### expect/actual классы

Полные реализации классов:

```kotlin
// commonMain/Storage.kt
expect class KeyValueStorage {
    fun saveString(key: String, value: String)
    fun getString(key: String): String?
    fun remove(key: String)
    fun clear()
}

// Общее использование
class UserPreferences(private val storage: KeyValueStorage) {
    var username: String?
        get() = storage.getString("username")
        set(value) {
            value?.let { storage.saveString("username", it) }
                ?: storage.remove("username")
        }

    var theme: String
        get() = storage.getString("theme") ?: "light"
        set(value) = storage.saveString("theme", value)

    fun clearAll() = storage.clear()
}
```

Android реализация:

```kotlin
// androidMain/Storage.kt
import android.content.Context
import android.content.SharedPreferences

actual class KeyValueStorage(context: Context) {
    private val prefs: SharedPreferences =
        context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE)

    actual fun saveString(key: String, value: String) {
        prefs.edit().putString(key, value).apply()
    }

    actual fun getString(key: String): String? {
        return prefs.getString(key, null)
    }

    actual fun remove(key: String) {
        prefs.edit().remove(key).apply()
    }

    actual fun clear() {
        prefs.edit().clear().apply()
    }
}
```

iOS реализация:

```kotlin
// iosMain/Storage.kt
import platform.Foundation.NSUserDefaults

actual class KeyValueStorage {
    private val userDefaults = NSUserDefaults.standardUserDefaults

    actual fun saveString(key: String, value: String) {
        userDefaults.setObject(value, forKey = key)
        userDefaults.synchronize()
    }

    actual fun getString(key: String): String? {
        return userDefaults.stringForKey(key)
    }

    actual fun remove(key: String) {
        userDefaults.removeObjectForKey(key)
        userDefaults.synchronize()
    }

    actual fun clear() {
        val dictionary = userDefaults.dictionaryRepresentation()
        dictionary.keys.forEach { key ->
            userDefaults.removeObjectForKey(key as String)
        }
        userDefaults.synchronize()
    }
}
```

### expect/actual свойства

```kotlin
// commonMain/Platform.kt
expect val platformName: String
expect val platformVersion: String
expect val deviceModel: String

// Общее использование
fun getSystemInfo(): String {
    return buildString {
        appendLine("Платформа: $platformName")
        appendLine("Версия: $platformVersion")
        appendLine("Устройство: $deviceModel")
    }
}

// androidMain/Platform.kt
import android.os.Build

actual val platformName: String = "Android"
actual val platformVersion: String = Build.VERSION.RELEASE
actual val deviceModel: String = "${Build.MANUFACTURER} ${Build.MODEL}"

// iosMain/Platform.kt
import platform.UIKit.UIDevice

actual val platformName: String = "iOS"
actual val platformVersion: String = UIDevice.currentDevice.systemVersion
actual val deviceModel: String = UIDevice.currentDevice.model
```

### Реальный пример: HTTP клиент

```kotlin
// commonMain/HttpClient.kt
expect class HttpClient {
    suspend fun get(url: String): String
    suspend fun post(url: String, body: String): String
    fun close()
}

// Общий репозиторий, использующий HTTP клиент
class ApiRepository(private val client: HttpClient) {
    suspend fun fetchUsers(): List<User> {
        val response = client.get("https://api.example.com/users")
        return Json.decodeFromString(response)
    }

    suspend fun createUser(user: User): User {
        val body = Json.encodeToString(user)
        val response = client.post("https://api.example.com/users", body)
        return Json.decodeFromString(response)
    }

    fun cleanup() {
        client.close()
    }
}
```

### Распространённые ошибки

```kotlin
// ПЛОХО: Использование платформо-специфичных типов в expect
expect class MyClass {
    fun doSomething(context: android.content.Context)  // Ошибка: Android тип в общем коде!
}

// ХОРОШО: Использовать общие типы или абстракцию
expect class MyClass {
    fun doSomething(platformContext: Any)
}

// ПЛОХО: Разные сигнатуры между expect и actual
expect fun format(value: Double): String

actual fun format(value: Double, precision: Int = 2): String  // Ошибка: разные сигнатуры!

// ХОРОШО: Сигнатуры должны точно совпадать
expect fun format(value: Double, precision: Int = 2): String

actual fun format(value: Double, precision: Int): String =
    String.format("%.${precision}f", value)
```

### Лучшие практики

#### ДЕЛАТЬ:

```kotlin
// Использовать expect/actual для платформо-специфичной функциональности
expect fun openUrl(url: String)

// Держать expect объявления минимальными и сфокусированными
expect class ImageLoader {
    fun load(url: String): ByteArray
}

// Использовать описательные имена, указывающие на специфичность платформы
expect fun getPlatformHttpClient(): HttpClient

// Предоставлять реализации по умолчанию когда возможно
expect fun getDeviceId(): String {
    return "unknown"  // Реализация по умолчанию
}
```

#### НЕ ДЕЛАТЬ:

```kotlin
// Не допускайте утечку платформенных типов в общий код
expect class BadClass {
    fun method(view: android.view.View)  // Плохо!
}

// Не делайте всё expect/actual
// Используйте общий код когда возможно
class CommonHelper {  // Не нужен expect/actual
    fun formatNumber(num: Int): String = num.toString()
}

// Не создавайте излишне сложные expect/actual иерархии
expect abstract class ComplexBase {
    abstract class Inner {
        abstract class DeeperInner  // Слишком сложно!
    }
}
```

### Структура проекта

```
myproject/
 commonMain/
    kotlin/
        Platform.kt        (expect объявления)
        Storage.kt         (expect class)
        Logger.kt          (expect object)
 androidMain/
    kotlin/
        Platform.kt        (actual реализации)
        Storage.kt         (actual class)
        Logger.kt          (actual object)
 iosMain/
    kotlin/
        Platform.kt        (actual реализации)
        Storage.kt         (actual class)
        Logger.kt          (actual object)
 commonTest/
     kotlin/
         PlatformTest.kt    (общие тесты)
```

---

## References

- [Kotlin Multiplatform expect/actual](https://kotlinlang.org/docs/multiplatform-connect-to-apis.html)
- [KMP Platform-specific declarations](https://kotlinlang.org/docs/multiplatform-expect-actual.html)
- [Kotlin Multiplatform Mobile](https://kotlinlang.org/docs/multiplatform-mobile-getting-started.html)
- [expect/actual Tutorial](https://www.jetbrains.com/help/kotlin-multiplatform-dev/multiplatform-expect-actual.html)

## Related Questions

- [[q-kotlin-native--kotlin--hard]]
- [[q-kotlin-constructors--kotlin--easy]]
- [[q-kotlin-collections--kotlin--medium]]
- [[q-flow-basics--kotlin--easy]]

## MOC Links

- [[moc-kotlin]]
