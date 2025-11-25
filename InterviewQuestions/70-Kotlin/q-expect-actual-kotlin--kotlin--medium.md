---
id: kotlin-134
title: "Kotlin Multiplatform expect/actual / Механизм expect/actual в Kotlin"
aliases: ["Kotlin Multiplatform expect/actual", "Механизм expect/actual в Kotlin"]

# Classification
topic: kotlin
subtopics: [c-kotlin-multiplatform, expect-actual, kmp]
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
related: [c-kotlin, q-kotlin-collections--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-11-10

tags: [cross-platform, difficulty/medium, expect-actual, kmp, kotlin, multiplatform, platform-specific]
date created: Sunday, October 12th 2025, 3:00:59 pm
date modified: Tuesday, November 25th 2025, 8:53:52 pm
---

# Вопрос (RU)
> Что такое механизм expect/actual в Kotlin Multiplatform? Объясните как объявлять платформо-специфичные реализации и приведите практические примеры.

# Question (EN)
> What is the expect/actual mechanism in Kotlin Multiplatform? Explain how to declare platform-specific implementations and provide practical examples.

## Ответ (RU)

Механизм **expect/actual** в Kotlin Multiplatform (KMP) позволяет писать общий код, который может иметь разные реализации на разных платформах (Android, iOS, JVM, JS, Native). Он обеспечивает типобезопасный способ доступа к платформо-специфичным API при сохранении возможности разделения кода. Подробнее см. [[c-kotlin]].

### Ключевые Концепции

1. **expect**: Объявление в общем коде, что что-то будет предоставлено платформо-специфичным кодом.
2. **actual**: Платформо-специфичная реализация ожидаемого объявления.
3. **Платформенные модули**: commonMain, androidMain, iosMain, jvmMain, jsMain (и более детальные source sets для конкретных целей).
4. **Типобезопасность**: Компилятор гарантирует, что actual-реализации соответствуют expect-объявлениям (имя, сигнатура, модификаторы и nullability).
5. **Гибкость**: Может использоваться для функций, классов, свойств и объектов.

### Как Работает expect/actual

```

         commonMain

    expect fun getPlatform()
    expect class Storage




 androidMain     iosMain
 actual impl    actual impl

```

### expect/actual Функции

Базовые объявления функций:

```kotlin
// commonMain/Platform.kt
expect fun getPlatformName(): String

expect fun currentTimeMillis(): Long

expect fun generateUUID(): String

// Общий код, использующий expect-функции
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

actual fun currentTimeMillis(): Long = java.lang.System.currentTimeMillis()

actual fun generateUUID(): String = java.util.UUID.randomUUID().toString()

// iosMain/Platform.kt
import platform.UIKit.UIDevice
import platform.Foundation.NSUUID
import platform.Foundation.NSDate

actual fun getPlatformName(): String =
    "iOS ${UIDevice.currentDevice.systemVersion}"

actual fun currentTimeMillis(): Long =
    (NSDate().timeIntervalSince1970 * 1000).toLong()

actual fun generateUUID(): String =
    NSUUID().UUIDString()
```

### expect/actual Классы

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

Android-реализация:

```kotlin
// androidMain/Storage.kt
import android.content.Context
import android.content.SharedPreferences

actual class KeyValueStorage(private val context: Context) {
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

iOS-реализация (упрощённый пример):

```kotlin
// iosMain/Storage.kt
import platform.Foundation.NSUserDefaults

actual class KeyValueStorage {
    private val userDefaults = NSUserDefaults.standardUserDefaults

    actual fun saveString(key: String, value: String) {
        userDefaults.setObject(value, forKey = key)
    }

    actual fun getString(key: String): String? {
        return userDefaults.stringForKey(key)
    }

    actual fun remove(key: String) {
        userDefaults.removeObjectForKey(key)
    }

    actual fun clear() {
        val dictionary = userDefaults.dictionaryRepresentation()
        dictionary.keys.forEach { key ->
            userDefaults.removeObjectForKey(key as String)
        }
    }
}
```

(В реальном коде реализации могут учитывать миграции, типизированный доступ и избегать устаревших API.)

### expect/actual С Параметрами Типов (Концептуально)

Важно, чтобы `expect`/`actual`-объявления совпадали полностью, включая дженерики и ограничения типов. Для JSON в KMP обычно используют kotlinx.serialization и механизмы `serializer()` вместо `Class<T>`.

```kotlin
// commonMain/Serializer.kt (концептуально)
expect class JsonSerializer {
    fun <T> serialize(obj: T): String
}
```

Каждая `actual`-реализация обязана иметь совместимые сигнатуры и использовать доступные на платформе механизмы.

### expect/actual Свойства

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

### expect/actual Объекты (Одиночки)

```kotlin
// commonMain/Logger.kt
expect object PlatformLogger {
    fun debug(message: String)
    fun info(message: String)
    fun warning(message: String)
    fun error(message: String)
}

// Общее использование
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

### Реальный Пример: HTTP Клиент (Концептуально)

```kotlin
// commonMain/HttpClient.kt
expect class HttpClient {
    suspend fun get(url: String): String
    suspend fun post(url: String, body: String): String
    fun close()
}

// Общий репозиторий, использующий HTTP-клиент
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

Платформенные `actual`-реализации должны:
- Не блокировать внутри `suspend`-функций.
- Корректно бриджить колбэки в `suspend` или использовать мультиплатформенные HTTP-библиотеки.

### expect/actual С Интерфейсами

```kotlin
// commonMain/Database.kt
interface DatabaseDriver {
    fun insert(table: String, values: Map<String, Any>)
    fun query(table: String, where: String): List<Map<String, Any>>
    fun delete(table: String, where: String)
}

expect fun createDatabaseDriver(databaseName: String): DatabaseDriver

// Общее использование
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
```

Платформенные `actual`-реализации должны предоставлять конкретный `DatabaseDriver` в соответствии со своими API для хранения данных (например, SQLite на Android), обычно через инъекцию зависимостей из платформенного кода.

### Распространённые Ошибки

```kotlin
// ПЛОХО: Использование платформо-специфичных типов в expect
expect class MyClass {
    fun doSomething(context: android.content.Context)  // Ошибка: Android-тип в общем коде!
}

// ХОРОШО: Использовать общие типы или абстракцию
expect class MyClass {
    fun doSomething(platformContext: Any)
}

// ПЛОХО: Разные сигнатуры между expect и actual
expect fun format(value: Double): String

actual fun format(value: Double, precision: Int): String  // Ошибка: другая сигнатура!

// ХОРОШО: Сигнатуры должны точно совпадать (включая параметры по умолчанию)
expect fun format(value: Double, precision: Int = 2): String

actual fun format(value: Double, precision: Int): String =
    String.format("%.${precision}f", value)

// ПЛОХО: Отсутствует actual-реализация
expect fun platformSpecific(): String

// iosMain: нет actual-реализации
// Это приведет к ошибке компиляции!

// ХОРОШО: Всегда предоставляйте actual для всех целевых платформ
// androidMain
actual fun platformSpecific(): String = "Android"

// iosMain
actual fun platformSpecific(): String = "iOS"
```

Также помните: `expect`-объявления не могут иметь тела; общая логика и реализации по умолчанию должны быть вынесены в обычные функции или inline-хелперы, а не в `expect`.

Недопустимы и несогласованные nullability:

```kotlin
// ПЛОХО: nullability не совпадает
expect fun getValue(): String

actual fun getValue(): String? = null  // Ошибка: несоответствие nullability!
```

### Лучшие Практики

#### ДЕЛАТЬ:

```kotlin
// Использовать expect/actual для платформо-специфичной функциональности
expect fun openUrl(url: String)

// Держать expect-объявления минимальными и сфокусированными
expect class ImageLoader {
    fun load(url: String): ByteArray
}

// Использовать описательные имена, указывающие на специфичность платформы
expect fun getPlatformHttpClient(): HttpClient

// Использовать общие абстракции (sealed-классы и т.п.) для разделяемой логики
sealed class PlatformResult {
    data class Success(val data: String) : PlatformResult()
    data class Error(val message: String) : PlatformResult()
}
```

#### НЕ ДЕЛАТЬ:

```kotlin
// Не допускайте утечку платформенных типов в общий код
expect class BadClass {
    fun method(view: android.view.View)  // Плохо!
}

// Не делайте всё expect/actual
// Используйте общий код, когда возможно
class CommonHelper {  // Не нужен expect/actual
    fun formatNumber(num: Int): String = num.toString()
}

// Не создавайте чрезмерно сложные expect/actual-иерархии
expect abstract class ComplexBase {
    abstract class Inner {
        abstract class DeeperInner  // Слишком сложно!
    }
}
```

### Тестирование expect/actual-Кода (Концептуально)

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
}
```

Для каждой платформы можно добавить специфичные тесты, проверяющие корректность `actual`-реализаций.

### Структура Проекта

```
myproject/
 commonMain/
    kotlin/
        Platform.kt        (expect-объявления)
        Storage.kt         (expect class)
        Logger.kt          (expect object)
 androidMain/
    kotlin/
        Platform.kt        (actual-реализации)
        Storage.kt         (actual class)
        Logger.kt          (actual object)
 iosMain/
    kotlin/
        Platform.kt        (actual-реализации)
        Storage.kt         (actual class)
        Logger.kt          (actual object)
 commonTest/
     kotlin/
         PlatformTest.kt   (общие тесты)
```

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого механизма от подхода в Java (без expect/actual)?
- В каких практических сценариях вы бы использовали expect/actual в реальных проектах?
- Какие типичные ошибки и подводные камни при использовании expect/actual следует избегать?

## Ссылки (RU)

- https://kotlinlang.org/docs/multiplatform-connect-to-apis.html
- https://kotlinlang.org/docs/multiplatform-expect-actual.html
- https://kotlinlang.org/docs/multiplatform-mobile-getting-started.html
- https://www.jetbrains.com/help/kotlin-multiplatform-dev/multiplatform-expect-actual.html

## Связанные Вопросы (RU)

- [[q-kotlin-native--kotlin--hard]]
- [[q-kotlin-constructors--kotlin--easy]]
- [[q-kotlin-collections--kotlin--medium]]

## MOC-ссылки (RU)

- [[moc-kotlin]]

## Answer (EN)

The **expect/actual** mechanism in Kotlin Multiplatform (KMP) allows you to write common code that can have different implementations on different platforms (Android, iOS, JVM, JS, Native). It provides a type-safe way to access platform-specific APIs while maintaining code sharing. See also [[c-kotlin]].

### Key Concepts

1. **expect**: Declaration in common code that something will be provided by platform-specific code.
2. **actual**: Platform-specific implementation of the expected declaration.
3. **Platform modules**: commonMain, androidMain, iosMain, jvmMain, jsMain (plus more granular targets/source sets).
4. **Type safety**: The compiler ensures actual implementations match expect declarations (name, signature, modifiers, nullability).
5. **Flexibility**: Can be used for functions, classes, properties, and objects.

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

actual fun currentTimeMillis(): Long = java.lang.System.currentTimeMillis()

actual fun generateUUID(): String = java.util.UUID.randomUUID().toString()

// iosMain/Platform.kt
import platform.UIKit.UIDevice
import platform.Foundation.NSUUID
import platform.Foundation.NSDate

actual fun getPlatformName(): String =
    "iOS ${UIDevice.currentDevice.systemVersion}"

actual fun currentTimeMillis(): Long =
    (NSDate().timeIntervalSince1970 * 1000).toLong()

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

actual class KeyValueStorage(private val context: Context) {
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

iOS implementation (simplified example):

```kotlin
// iosMain/Storage.kt
import platform.Foundation.NSUserDefaults

actual class KeyValueStorage {
    private val userDefaults = NSUserDefaults.standardUserDefaults

    actual fun saveString(key: String, value: String) {
        userDefaults.setObject(value, forKey = key)
    }

    actual fun getString(key: String): String? {
        return userDefaults.stringForKey(key)
    }

    actual fun remove(key: String) {
        userDefaults.removeObjectForKey(key)
    }

    actual fun clear() {
        val dictionary = userDefaults.dictionaryRepresentation()
        dictionary.keys.forEach { key ->
            userDefaults.removeObjectForKey(key as String)
        }
    }
}
```

(Real-world implementations may manage migration, typed accessors, and avoid deprecated APIs.)

### expect/actual With Type Parameters (Conceptual)

Be careful that expect/actual declarations match exactly, including generic constraints and parameters. For JSON in KMP, kotlinx.serialization with `serializer()` is typically used instead of `Class<T>`.

```kotlin
// commonMain/Serializer.kt (conceptual)
expect class JsonSerializer {
    fun <T> serialize(obj: T): String
}
```

Each actual implementation must use compatible signatures and mechanisms available on that platform.

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

### Real-World Example: HTTP Client (Conceptual)

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
```

Platform-specific actual implementations should:
- Avoid blocking inside suspending functions.
- Use proper callback-to-suspend bridging or a multiplatform HTTP library.

### expect/actual With Interfaces

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
```

Platform actual implementations must provide a concrete DatabaseDriver consistent with their storage APIs. The exact acquisition of, for example, SQLiteDatabase on Android is environment-specific and typically injected from Android code.

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

actual fun format(value: Double, precision: Int): String  // Error: different signature!

// GOOD: Match signatures exactly (including default params)
expect fun format(value: Double, precision: Int = 2): String

actual fun format(value: Double, precision: Int): String =
    String.format("%.${precision}f", value)

// BAD: Forgetting to provide actual implementation
expect fun platformSpecific(): String

// iosMain: Missing actual implementation
// This will cause compilation error!

// GOOD: Always provide actual for all relevant targets
// androidMain
actual fun platformSpecific(): String = "Android"

// iosMain
actual fun platformSpecific(): String = "iOS"

// BAD: Mismatched nullability between expect and actual
expect fun getValue(): String

actual fun getValue(): String? = null  // Error: nullability mismatch!
```

Also remember: expect declarations cannot have bodies; default implementations, if needed, must be expressed via common functions or inline helpers, not in expect itself.

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

// Use sealed classes or other common abstractions for shared logic
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
```

### Testing expect/actual Code (Conceptual)

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
}
```

Each platform can have specific tests too, ensuring actual implementations behave as expected.

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
         PlatformTest.kt   (common tests)
```

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- https://kotlinlang.org/docs/multiplatform-connect-to-apis.html
- https://kotlinlang.org/docs/multiplatform-expect-actual.html
- https://kotlinlang.org/docs/multiplatform-mobile-getting-started.html
- https://www.jetbrains.com/help/kotlin-multiplatform-dev/multiplatform-expect-actual.html

## Related Questions

- [[q-kotlin-native--kotlin--hard]]
- [[q-kotlin-constructors--kotlin--easy]]
- [[q-kotlin-collections--kotlin--medium]]

## MOC Links

- [[moc-kotlin]]
