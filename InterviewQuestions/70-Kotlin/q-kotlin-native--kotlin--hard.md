---
anki_cards:
- slug: q-kotlin-native--kotlin--hard-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-kotlin-native--kotlin--hard-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
## Answer (EN)

**Kotlin/Native** is a technology for compiling Kotlin code to native binaries that run without a virtual machine (no JVM). It enables Kotlin to target platforms like iOS, macOS, Linux, Windows, and some embedded systems.

See also: [[c-kotlin]].

### Key Features

1. **Native Compilation**: Compiles to platform-specific machine code via LLVM.
2. **No JVM Required**: Produces standalone executables and libraries.
3. **C Interop**: Direct integration with C libraries via `cinterop`.
4. **Objective-C/Swift Interop**: Interoperability with iOS/macOS code and frameworks.
5. **Multiplatform**: Share business logic across platforms (via KMP).
6. **Memory Management**: Automatic memory management with the unified memory manager; manual allocation (nativeHeap/memScoped, etc.) is primarily used for interop and low-level use cases.

### Kotlin/Native Architecture

```text

       Kotlin Source Code

          Kotlin/Native
            Compiler

  LLVM                LLVM
  iOS                 macOS

 .framework           Binary

```

(Simplified: Kotlin/Native compiler lowers Kotlin to LLVM IR and produces platform-specific binaries/frameworks.)

### Basic Kotlin/Native Multiplatform Setup

```kotlin
// commonMain/Platform.kt
expect class Platform() {
    val name: String
}

fun getPlatformName(): String = Platform().name

// iosMain/Platform.kt
import platform.UIKit.UIDevice

actual class Platform {
    actual val name: String =
        UIDevice.currentDevice.systemName() + " " +
        UIDevice.currentDevice.systemVersion
}
```

### C Interop (cinterop)

Calling C libraries from Kotlin using a `.def` file:

```kotlin
// curl.def
headers = curl/curl.h
headerFilter = curl/*
compilerOpts.linux = -I/usr/include -I/usr/include/x86_64-linux-gnu
linkerOpts.osx = -L/opt/local/lib -L/usr/local/opt/curl/lib -lcurl
linkerOpts.linux = -L/usr/lib/x86_64-linux-gnu -lcurl
```

```kotlin
import kotlinx.cinterop.*
import curl.*

fun httpGet(url: String): String? {
    val curl = curl_easy_init()

    if (curl != null) {
        curl_easy_setopt(curl, CURLOPT_URL, url)
        curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L)

        val result = curl_easy_perform(curl)
        curl_easy_cleanup(curl)

        if (result == CURLE_OK) {
            // Real-world code should use CURLOPT_WRITEFUNCTION to capture response.
            return "Success"
        }
    }

    return null
}
```

Working with C structs:

```c
// mylib.h
typedef struct {
    int id;
    char name[100];
    double value;
} MyStruct;

void process_struct(MyStruct* s);
```

```kotlin
// Kotlin
import kotlinx.cinterop.*
import mylib.*

fun useStruct() {
    memScoped {
        val struct = alloc<MyStruct>()

        struct.id = 42
        struct.name[0] = 'T'.code.toByte()
        struct.name[1] = 'e'.code.toByte()
        struct.name[2] = 's'.code.toByte()
        struct.name[3] = 't'.code.toByte()
        struct.value = 3.14

        process_struct(struct.ptr)
        // Memory is released automatically when memScoped exits.
    }
}
```

### Objective-C/Swift Interop

Calling Objective-C from Kotlin:

```objective-c
// MyClass.h
@interface MyClass : NSObject
- (NSString *)greet:(NSString *)name;
- (NSInteger)addA:(NSInteger)a b:(NSInteger)b;
@property (nonatomic, strong) NSString *title;
@end

// MyClass.m
@implementation MyClass
- (NSString *)greet:(NSString *)name {
    return [NSString stringWithFormat:@"Hello, %@!", name];
}

- (NSInteger)addA:(NSInteger)a b:(NSInteger)b {
    return a + b;
}
@end
```

```kotlin
// Kotlin
import platform.Foundation.*
import cocoapods.MyFramework.*

fun useObjCClass() {
    val obj = MyClass()

    val greeting = obj.greet("World")
    println(greeting) // "Hello, World!"

    val sum = obj.addA(5, b = 3)
    println(sum) // 8

    obj.title = "My Title"
    println(obj.title)
}
```

Exposing Kotlin to Swift (schematic; requires a wrapper around suspend):

```kotlin
class UserRepository {
    suspend fun getUsers(): List<User> {
        // ...
        return listOf(User(1, "Alice"), User(2, "Bob"))
    }
}

data class User(val id: Int, val name: String)

@OptIn(ExperimentalForeignApi::class)
fun iosGetUsers(callback: (List<User>) -> Unit) {
    val repository = UserRepository()

    // In real code, use a shared scope with well-defined lifecycle.
    MainScope().launch {
        val users = repository.getUsers()
        callback(users)
    }
}
```

Swift usage (signature simplified for illustration; actual types and bridging use generated types from the produced framework):

```swift
import Shared

class ViewModel: ObservableObject {
    @Published var users: [User] = []

    func loadUsers() {
        SharedKt.iosGetUsers { users in
            self.users = users
        }
    }
}
```

### Memory Model

#### Old Memory Model (pre Unified Memory manager)

- Required `freeze()`, `Worker`, `DetachedObjectGraph` patterns.
- Sharing mutable objects across threads without freeze caused runtime errors.

```kotlin
// Conceptual example (legacy):
class DataHolder {
    var data = "Hello"
}

val holder = DataHolder()

// main thread
holder.data = "World"

// other thread (if holder was frozen explicitly):
// mutation would throw InvalidMutabilityException in old model.
```

#### New Memory Model (1.7.20+ default)

- Unified memory manager.
- Objects can be shared between threads.
- No automatic freezing; standard concurrency rules apply.
- Collections are not magically thread-safe.

```kotlin
class DataHolder {
    var data = "Hello"
}

val holder = DataHolder()

// Any thread can read/write; use locks/atomics if mutated concurrently.
holder.data = "Modified"
```

#### Interop-related Memory Management

```kotlin
import kotlinx.cinterop.*

// Manual memory management for C interop
fun manualMemory() {
    val buffer = nativeHeap.allocArray<ByteVar>(1024)
    try {
        buffer[0] = 'H'.code.toByte()
        buffer[1] = 'i'.code.toByte()
    } finally {
        nativeHeap.free(buffer)
    }
}

fun scopedMemory() {
    memScoped {
        val buffer = allocArray<ByteVar>(1024)
        // Automatically freed when memScoped exits
    }
}
```

### Coroutines in Kotlin/Native

Coroutines are supported; for iOS/Swift interop you typically expose callback- or `Flow`-based wrappers and must manage coroutine scope lifecycle explicitly.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.Flow

class FlowWrapper<T>(private val flow: Flow<T>, private val scope: CoroutineScope) {
    fun subscribe(
        onEach: (T) -> Unit,
        onComplete: () -> Unit,
        onThrow: (Throwable) -> Unit
    ): Cancellable {
        val job = scope.launch {
            try {
                flow.collect { value -> onEach(value) }
                onComplete()
            } catch (e: Throwable) {
                onThrow(e)
            }
        }

        return object : Cancellable {
            override fun cancel() {
                job.cancel()
            }
        }
    }
}

interface Cancellable {
    fun cancel()
}
```

(Swift side would receive a bridged API; signatures here are conceptual.)

### Platform-Specific APIs

```kotlin
// expect declaration in commonMain
expect class PlatformFile(path: String) {
    fun readText(): String
    fun writeText(text: String)
}
```

```kotlin
// actual implementation for iOS (simplified)
import platform.Foundation.*
import kotlinx.cinterop.*

actual class PlatformFile actual constructor(private val path: String) {
    actual fun readText(): String {
        memScoped {
            val errorPtr = alloc<ObjCObjectVar<NSError?>>()
            val url = NSURL.fileURLWithPath(path)
            val content = NSString.stringWithContentsOfURL(
                url,
                NSUTF8StringEncoding,
                errorPtr.ptr
            )
            val error = errorPtr.value
            if (error != null) throw Exception(error.localizedDescription)
            return content?.toString() ?: ""
        }
    }

    actual fun writeText(text: String) {
        memScoped {
            val errorPtr = alloc<ObjCObjectVar<NSError?>>()
            val url = NSURL.fileURLWithPath(path)
            val nsText: NSString = NSString.create(string = text)
            nsText.writeToURL(url, true, NSUTF8StringEncoding, errorPtr.ptr)
            val error = errorPtr.value
            if (error != null) throw Exception(error.localizedDescription)
        }
    }
}
```

### Build Configuration

```kotlin
// build.gradle.kts (KMP snippet; versions shown as example)
kotlin {
    iosArm64()
    iosX64()
    iosSimulatorArm64()

    sourceSets {
        val commonMain by getting {
            dependencies {
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
            }
        }

        val iosMain by creating {
            dependsOn(commonMain)
        }

        val iosArm64Main by getting { dependsOn(iosMain) }
        val iosX64Main by getting { dependsOn(iosMain) }
        val iosSimulatorArm64Main by getting { dependsOn(iosMain) }
    }
}
```

### Real-World Example: Shared Networking

```kotlin
// commonMain
import kotlinx.serialization.*
import kotlinx.serialization.json.Json

@Serializable
data class User(val id: Int, val name: String)

interface ApiService {
    suspend fun fetchUsers(): List<User>
    suspend fun createUser(user: User): User
}

expect class NetworkClient() {
    suspend fun get(url: String): String
    suspend fun post(url: String, body: String): String
}

class ApiServiceImpl(private val client: NetworkClient) : ApiService {
    override suspend fun fetchUsers(): List<User> {
        val json = client.get("https://api.example.com/users")
        return Json.decodeFromString(json)
    }

    override suspend fun createUser(user: User): User {
        val body = Json.encodeToString(user)
        val json = client.post("https://api.example.com/users", body)
        return Json.decodeFromString(json)
    }
}
```

```kotlin
// iosMain (simplified)
import kotlinx.cinterop.*
import platform.Foundation.*
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import kotlin.coroutines.suspendCoroutine

actual class NetworkClient {
    actual suspend fun get(url: String): String = suspendCoroutine { continuation ->
        val nsUrl = NSURL(string = url)
        val request = NSURLRequest.requestWithURL(nsUrl)

        NSURLSession.sharedSession.dataTaskWithRequest(request) { data, _, error ->
            when {
                error != null -> continuation.resumeWithException(
                    Exception(error.localizedDescription)
                )
                data != null -> {
                    val string = NSString.create(data = data, encoding = NSUTF8StringEncoding)
                    continuation.resume(string.toString())
                }
                else -> continuation.resumeWithException(Exception("Unknown error"))
            }
        }.resume()
    }

    actual suspend fun post(url: String, body: String): String = suspendCoroutine { continuation ->
        // Implementation analogous to get(): configure HTTP method and body.
        continuation.resume("") // Placeholder for brevity.
    }
}
```

### Use Cases

1. **iOS App Development**
   - Share business/domain logic between Android and iOS.
   - Keep UI platform-specific (SwiftUI/UIKit on iOS, Jetpack Compose/Views on Android).

2. **Cross-Platform Libraries**
   - Networking, persistence, crypto, analytics, etc.

3. **Embedded / Native Utilities and certain desktop/embedded targets**
   - CLI tools and applications where Kotlin/Native targets are supported.

4. **Game Development**
   - Shared core game logic with native renderers.

### Best Practices

#### DO:

```kotlin
// Share business logic in commonMain
class UserRepository {
    suspend fun getUsers(): List<User> { /* ... */ return emptyList() }
}

// Keep UI platform-specific

// Use expect/actual for platform APIs
expect fun getCurrentTimestamp(): Long

// Use memScoped/nativeHeap primarily for interop buffers and low-level tasks
memScoped {
    val buffer = allocArray<ByteVar>(1024)
    // Auto-freed on scope exit
}

// Wrap coroutines/Flow for idiomatic and safe iOS consumption
class FlowWrapper<T>(private val flow: Flow<T>, private val scope: CoroutineScope)
```

#### DON'T:

```kotlin
// Don't forget manual free for nativeHeap allocations
val buffer = nativeHeap.allocArray<ByteVar>(1024)
// nativeHeap.free(buffer) is required

// Don't expose suspend directly to Swift without a wrapper
suspend fun getData(): List<User>

// Don't try to share full UI across iOS/Android purely via Kotlin/Native

// Don't rely on deprecated freezing patterns with the new memory manager
```

---

## Дополнительные Вопросы (RU)

- В чём ключевые отличия между Kotlin/Native и запуском Kotlin на JVM?
- В каких практических сценариях вы бы выбрали Kotlin/Native или KMP для iOS?
- Какие типичные подводные камни при interop с C/ObjC и работе с моделью памяти?

## Follow-ups

- What are the key differences between Kotlin/Native and running Kotlin on the JVM?
- When would you use Kotlin/Native or KMP with iOS in practice?
- What are common pitfalls to avoid with C/ObjC interop and the memory model?

## Ссылки (RU)

- https://kotlinlang.org/docs/native-overview.html
- https://kotlinlang.org/docs/native-c-interop.html
- https://kotlinlang.org/docs/native-objc-interop.html
- https://kotlinlang.org/docs/native-memory-manager.html

## References (EN)

- https://kotlinlang.org/docs/native-overview.html
- https://kotlinlang.org/docs/native-c-interop.html
- https://kotlinlang.org/docs/native-objc-interop.html
- https://kotlinlang.org/docs/native-memory-manager.html

## Связанные Вопросы (RU)

- [[q-expect-actual-kotlin--kotlin--medium]]
- [[q-structured-concurrency--kotlin--hard]]
- [[q-kotlin-collections--kotlin--medium]]
- [[q-flow-basics--kotlin--easy]]

## Related Questions (EN)

- [[q-expect-actual-kotlin--kotlin--medium]]
- [[q-structured-concurrency--kotlin--hard]]
- [[q-kotlin-collections--kotlin--medium]]
- [[q-flow-basics--kotlin--easy]]

## MOC-ссылки (RU)

- [[moc-kotlin]]

## MOC Links (EN)

- [[moc-kotlin]]
